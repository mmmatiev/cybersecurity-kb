#!/usr/bin/env python3
"""Validate thematic coverage, metadata, navigation and JSON Canvas geometry."""

from __future__ import annotations

import json
import re
from itertools import combinations
from pathlib import Path

from audit_cryptography_kb import ALLOWED_AREAS, ALLOWED_SECURITY, check_vault_integrity, frontmatter
from build_thematic_clusters import MANIFEST, NAVIGATION, VAULT, build, corpus_paths
from thematic_clusters import BY_ID, CANVAS_PATH, CLUSTERS


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def linked_targets(text: str) -> set[str]:
    return {raw.split('|', 1)[0].split('#', 1)[0]
            for raw in re.findall(r'\[\[([^]\n]+)\]\]', text)}


def reachable_via_clusters(moc_text: str, canonical: dict[str, Path]) -> set[str]:
    """Allow one thematic hop, not arbitrary reachability through unrelated MOCs."""
    targets = linked_targets(moc_text)
    for title in tuple(targets):
        if title.startswith('Кластер - '):
            path = canonical.get(title)
            require(path is not None, f"Missing linked cluster: {title}")
            metadata, body = frontmatter(path.read_text())
            require(metadata.get('type') == 'moc', f"Linked cluster is not a MOC: {title}")
            targets.update(linked_targets(body))
    return targets


def intersects(a: dict, b: dict) -> bool:
    return (max(a['x'], b['x']) < min(a['x'] + a['width'], b['x'] + b['width'])
            and max(a['y'], b['y']) < min(a['y'] + a['height'], b['y'] + b['height']))


def contains(group: dict, node: dict) -> bool:
    return (group['x'] < node['x'] and group['y'] < node['y']
            and node['x'] + node['width'] < group['x'] + group['width']
            and node['y'] + node['height'] < group['y'] + group['height'])


def check_canvas(root: Path, canvas: dict) -> dict:
    nodes, edges = canvas['nodes'], canvas['edges']
    ids = [n['id'] for n in nodes] + [e['id'] for e in edges]
    require(len(ids) == len(set(ids)), "Duplicate Canvas ID")
    file_nodes = [n for n in nodes if n['type'] == 'file']
    groups = [n for n in nodes if n['type'] == 'group']
    foreground = [n for n in nodes if n['type'] != 'group']
    require(len(file_nodes) == 19 and len(groups) == 5, "Unexpected Canvas node count")
    require({n['file'] for n in file_nodes} == {c.path.as_posix() for c in CLUSTERS}, "Canvas file membership mismatch")
    for n in nodes:
        require(n['type'] in {'group', 'file', 'text'}, "Unknown Canvas node type")
        require(all(type(n[k]) is int for k in ('x', 'y', 'width', 'height')), "Non-integer Canvas geometry")
        require(n['width'] > 0 and n['height'] > 0, "Non-positive Canvas size")
    for a, b in list(combinations(foreground, 2)) + list(combinations(groups, 2)):
        require(not intersects(a, b), f"Canvas overlap: {a['id']} / {b['id']}")
    for n in file_nodes:
        path = root / n['file']
        require(path.is_file(), f"Missing Canvas target: {n['file']}")
        require(n.get('subpath') == '#Обзор' and '\n## Обзор\n' in path.read_text(), "Missing Canvas section")
        require(sum(contains(g, n) for g in groups) == 1, f"Wrong Canvas group: {n['id']}")
    node_ids = {n['id'] for n in file_nodes}
    require(len(edges) <= 12, "Too many Canvas connections")
    for e in edges:
        require(e['fromNode'] in node_ids and e['toNode'] in node_ids and e['fromNode'] != e['toNode'], "Bad Canvas edge")
        require(e['fromSide'] in {'left', 'right', 'top', 'bottom'} and e['toSide'] in {'left', 'right', 'top', 'bottom'}, "Bad Canvas side")
        require(e['fromEnd'] == 'none' and e['toEnd'] == 'arrow', "Bad Canvas arrow")
    return {'canvas_file_nodes': len(file_nodes), 'canvas_groups': len(groups), 'canvas_edges': len(edges)}


def check_clusters(root: Path = VAULT) -> dict:
    require(not build(root), "Thematic navigation is stale")
    corpus = corpus_paths(root)
    manifest = json.loads((root / MANIFEST).read_text())
    require(set(manifest['primary_membership']) == set(corpus), "Manifest coverage mismatch")
    for c in CLUSTERS:
        text = (root / c.path).read_text(encoding='utf-8')
        data, body = frontmatter(text)
        require(data['type'] == 'moc' and isinstance(data['area'], list) and 1 <= len(data['area']) <= 2
                and set(data['area']) <= ALLOWED_AREAS, f"Invalid cluster metadata: {c.title}")
        if c.domain.startswith('Cybersecurity/'):
            require(isinstance(data.get('security'), list) and len(data['security']) == 1
                    and set(data['security']) <= ALLOWED_SECURITY, f"Invalid security metadata: {c.title}")
        require(all(value not in ('', []) for value in data.values()), f"Empty metadata: {c.title}")
        require(f'# {c.basename}\n' in body, f"Wrong H1: {c.title}")
        for heading in ('Обзор', 'Что нужно знать заранее', 'Порядок изучения', 'Карточки по подгруппам', 'Связанные кластеры', 'Навигация'):
            require(f'\n## {heading}\n' in body, f"Missing cluster section: {c.title} / {heading}")
        parent_text = next((root / '01 Knowledge').rglob(c.parent + '.md')).read_text()
        require(f'[[{c.basename}|' in parent_text, f"Missing parent link: {c.title}")
    results = {'clusters': len(CLUSTERS), 'primary_cards': len(corpus), 'parent_mocs': len(NAVIGATION)}
    results.update(check_canvas(root, json.loads((root / CANVAS_PATH).read_text())))
    return results


if __name__ == '__main__':
    result = check_clusters()
    result.update(check_vault_integrity())
    print(json.dumps({'thematic_audit': 'ok', **result}, ensure_ascii=False))
