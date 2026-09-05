"""Regression tests use temporary copies, never regenerate live content notes."""

import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from audit_thematic_clusters import check_canvas, check_clusters, reachable_via_clusters
from build_thematic_clusters import (
    END, MANIFEST, NAVIGATION, START_RE, VAULT, build, corpus_paths, replace_navigation,
)
from thematic_clusters import CANVAS_PATH, CLUSTERS


class ThematicTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='kb-clusters-test-')
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        shutil.copytree(VAULT / '01 Knowledge', self.root / '01 Knowledge')
        shutil.copytree(VAULT / 'scripts/knowledge', self.root / 'scripts/knowledge', ignore=shutil.ignore_patterns('__pycache__'))

    def hashes(self):
        import hashlib
        return {str(p.relative_to(self.root)): hashlib.sha256(p.read_bytes()).hexdigest()
                for p in self.root.rglob('*') if p.is_file()}

    def test_complete_unique_membership(self):
        self.assertEqual(len(corpus_paths(self.root)), 110)
        self.assertEqual(check_clusters(self.root)['clusters'], 19)

    def test_idempotent_and_read_only_check(self):
        before = self.hashes()
        self.assertEqual(build(self.root), [])
        self.assertEqual(build(self.root, write=True), [])
        self.assertEqual(before, self.hashes())

    def test_manual_cluster_edit_stops_before_any_write(self):
        path = self.root / CLUSTERS[0].path
        path.write_text(path.read_text() + '\nРучное дополнение.\n')
        before = self.hashes()
        with self.assertRaisesRegex(RuntimeError, 'Manual changes'):
            build(self.root, write=True)
        self.assertEqual(before, self.hashes())

    def test_manual_navigation_edit_stops_before_any_write(self):
        path = self.root / ('01 Knowledge/' + NAVIGATION['crypto'][0] + '.md')
        path.write_text(path.read_text().replace('Выберите тему ниже.', 'Моя правка.'))
        before = self.hashes()
        with self.assertRaisesRegex(RuntimeError, 'Manual changes'):
            build(self.root, write=True)
        self.assertEqual(before, self.hashes())

    def test_manual_canvas_edit_is_preserved(self):
        path = self.root / CANVAS_PATH
        canvas = json.loads(path.read_text())
        canvas['nodes'][-1]['x'] += 20
        path.write_text(json.dumps(canvas, ensure_ascii=False))
        before = self.hashes()
        with self.assertRaisesRegex(RuntimeError, 'Manual changes'):
            build(self.root, write=True)
        self.assertEqual(before, self.hashes())

    def test_content_and_outside_blocks_are_preserved(self):
        path = self.root / ('01 Knowledge/' + NAVIGATION['crypto'][0] + '.md')
        path.write_text(path.read_text() + '\nМоя заметка вне блока.\n')
        content = self.root / corpus_paths(self.root)['Атаки на цифровые водяные знаки']
        content.write_text(content.read_text() + '\nМой разбор.\n')
        before = self.hashes()
        self.assertEqual(build(self.root, write=True), [])
        self.assertEqual(before, self.hashes())

    def test_missing_canonical_note_stops(self):
        path = self.root / corpus_paths(self.root)['RSA']
        path.rename(path.with_suffix('.missing'))
        before = self.hashes()
        with self.assertRaisesRegex(RuntimeError, 'Missing or duplicate'):
            build(self.root, write=True)
        self.assertEqual(before, self.hashes())

    def test_unowned_collision_stops(self):
        (self.root / MANIFEST).unlink()
        with self.assertRaisesRegex(RuntimeError, 'unowned'):
            build(self.root, write=True)

    def test_bad_markers_and_preimage_stop(self):
        path = self.root / ('01 Knowledge/' + NAVIGATION['crypto'][0] + '.md')
        text = path.read_text()
        for bad in (text.replace(END, ''), text + END, text.replace('sha256=', 'digest='), '## Основы\nchanged\nСтеганография не'):
            with self.assertRaises(RuntimeError):
                replace_navigation('crypto', bad)

    def test_initial_migration_preserves_surrounding_text(self):
        # Validate all six original approved blocks, independent of current markers.
        for key, (stem, begin, finish, _) in NAVIGATION.items():
            original = subprocess.check_output(
                ['git', 'show', '720a531:' + '01 Knowledge/' + stem + '.md'], cwd=VAULT).decode()
            updated = replace_navigation(key, original)
            self.assertEqual(updated, replace_navigation(key, updated))
            match = START_RE.search(updated)
            self.assertEqual(original[:original.index(begin)], updated[:match.start()])
            self.assertEqual(original[original.index(finish):], updated[updated.index(END) + len(END) + 2:])

    def test_canvas_overlap_is_detected(self):
        data = json.loads((self.root / CANVAS_PATH).read_text())
        files = [n for n in data['nodes'] if n['type'] == 'file']
        files[1]['x'], files[1]['y'] = files[0]['x'], files[0]['y']
        with self.assertRaisesRegex(RuntimeError, 'overlap'):
            check_canvas(self.root, data)

    def test_navigation_requires_actual_cluster_link(self):
        canonical = {p.stem: p for p in (self.root / '01 Knowledge').rglob('*.md')}
        title = 'Кластер - Встраивание в частотной области и JPEG'
        self.assertIn('JSteg', reachable_via_clusters(f'[[{title}|JPEG]]', canonical))
        self.assertNotIn('JSteg', reachable_via_clusters('[[Cryptography]]', canonical))
        self.assertNotIn('JSteg', reachable_via_clusters('Нет ссылки.', canonical))

    def test_course_builder_preflights_manual_navigation_edit(self):
        path = self.root / ('01 Knowledge/' + NAVIGATION['stego'][0] + '.md')
        path.write_text(path.read_text().replace('Маршрут:', 'Мой маршрут:'))
        before = self.hashes()
        result = subprocess.run([sys.executable, '-B', str(self.root / 'scripts/knowledge/build_crypto_steganography_knowledge.py'), '--overwrite-generated'],
                                cwd=self.root, capture_output=True, text=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('Manual changes', result.stderr)
        self.assertEqual(before, self.hashes())

    def test_course_regeneration_keeps_navigation(self):
        # Copy-only: the live watermark-attack note intentionally contains a user edit.
        path = self.root / ('01 Knowledge/' + NAVIGATION['stego'][0] + '.md')
        path.write_text(path.read_text() + '\nЛичное дополнение к MOC.\n')
        before = path.read_bytes()
        for script, args in (
            ('enhance_cryptography_notes.py', []),
            ('build_crypto_steganography_knowledge.py', ['--overwrite-generated']),
        ):
            subprocess.run([sys.executable, '-B', str(self.root / 'scripts/knowledge' / script), *args],
                           cwd=self.root, check=True, capture_output=True, text=True)
        self.assertEqual(before, path.read_bytes())
        self.assertEqual(build(self.root), [])
        after = self.hashes()
        subprocess.run([sys.executable, '-B', str(self.root / 'scripts/knowledge/build_crypto_steganography_knowledge.py'), '--overwrite-generated'],
                       cwd=self.root, check=True, capture_output=True, text=True)
        self.assertEqual(after, self.hashes())


if __name__ == '__main__':
    unittest.main()
