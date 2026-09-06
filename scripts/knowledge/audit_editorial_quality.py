#!/usr/bin/env python3
"""Structural editorial gate, explicitly not a proof of mathematical correctness."""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import re

from enhance_cryptography_notes import ALIASES, FORMULAS as FIRST_FORMULAS
from reviewed_first_course import EXAMPLES as FIRST_EXAMPLES
from reviewed_first_notation import NOTATION
from build_crypto_steganography_knowledge import NOTES, SELF_CHECKS, canonical_title, localize_prose
from reviewed_course_examples import EXAMPLES as SECOND_EXAMPLES
from reviewed_course_math import FORMULAS
from crypto_steganography_enrichment import DETAILS

ROOT = Path(__file__).resolve().parents[2]


def inspect(root: Path = ROOT) -> list[dict]:
    assert set(FIRST_EXAMPLES) == set(ALIASES)
    assert set(NOTATION) == set(FIRST_FORMULAS)
    assert set(SECOND_EXAMPLES) == set(FORMULAS) == set(SELF_CHECKS)
    paths = {}
    for path in (root / '01 Knowledge').rglob('*.md'):
        assert path.stem not in paths, f'Duplicate basename: {path.stem}'
        paths[path.stem] = path
    titles = {n.title: canonical_title(n.title) for n in NOTES}
    records, paragraphs = [], []
    for course, examples in [(1, FIRST_EXAMPLES), (2, SECOND_EXAMPLES)]:
        for title, example in examples.items():
            name = title if course == 1 else titles[title]
            path = paths[name]
            text = path.read_text()
            expected_example = example.markdown() if course == 1 else localize_prose(example.markdown())
            assert expected_example in text, f'Example diverged: {name}'
            assert len(example.steps) >= 2 and all(example.steps), name
            assert all((example.inputs, example.result, example.check, example.boundary, example.origin)), name
            assert '## Рабочий разбор' not in text and '## Мини-практика' not in text, name
            assert re.search(r'\[\[Source - .*?\]\].*?(?:стр\.|абз\.)', text), name
            formulas = FORMULAS[title] if course == 2 else ()
            for formula in formulas:
                assert formula.expression in text and formula.notation in text and formula.conditions in text, name
            if course == 1 and title in NOTATION:
                assert NOTATION[title] in text, name
            if course == 2:
                detail = DETAILS[title]
                assert len(set(detail.answers)) == len(set(SELF_CHECKS[title])) == 3, name
                assert all(localize_prose(answer) in text for answer in detail.answers), name
                assert '> [!answer]- Ответы' in text, name
            paragraphs.extend((name,p.strip()) for p in example.markdown().split('\n\n') if len(p.split()) >= 35)
            records.append({
                'course':course, 'title':name, 'path':path.relative_to(root).as_posix(),
                'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
                'formula_editorial_scope': 'paired expressions, notation and conditions' if course == 2 else ('canonical formula block with local notation' if title in NOTATION else 'no standalone canonical formula block; example terms explained locally'),
                'example_complete_structure':True, 'result':example.result, 'verification':example.check,
                'origin':example.origin, 'remaining_scope_limit':example.boundary,
                'semantic_validation':'editorial review plus independent calculations where applicable; structural checks alone are not evidence of mathematical truth',
            })
    duplicates = [p for p,n in Counter(p for _,p in paragraphs).items() if n>1]
    assert not duplicates, 'Duplicate long worked-example paragraphs'
    assert len(records) == 110
    return records


def markdown(records: list[dict]) -> str:
    lines = ['# Матрица содержательной редакции 110 карточек', '',
        'Матрица фиксирует объём редакции, проверяемый итог и границу каждого примера. Она не является сертификатом математической правильности: независимые расчёты находятся в `test_reviewed_examples.py` и `test_first_course_examples.py`, а фактические визуальные проверки и незавершённые пункты — в `EDITORIAL_REVIEW.md`.', '',
        'Во всех строках проверены наличие входов, шагов, результата, способа проверки и происхождения. Для второго курса формула хранится единым объектом с обозначениями и условиями; в первом курсе пояснены 34 канонических формульных блока. «Сценарий» не означает, что система была развёрнута или что результаты эксперимента измерены.', '',
        '| Карточка | Формулы и обозначения: объём редакции | Завершённый итог | Как проверять результат | Происхождение | Ограничение |',
        '|---|---|---|---|---|---|']
    def safe(v):return str(v).replace('|','&#124;').replace('\n',' ')
    for row in records:
        formula = 'Связанные формула, обозначения, условия' if row['course']==2 else ('Обозначения и условия формульного блока' if row['formula_editorial_scope'].startswith('canonical') else 'Термины локального примера; отдельного блока формулы нет')
        lines.append('| ' + ' | '.join(map(safe,[row['title'],formula,row['result'],row['verification'],row['origin'],row['remaining_scope_limit']])) + ' |')
    return '\n'.join(lines)+'\n'


if __name__ == '__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--write-matrix',action='store_true')
    args=parser.parse_args()
    rows=inspect()
    if args.write_matrix:
        (ROOT/'scripts/knowledge/editorial-review-matrix.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n')
        (ROOT/'scripts/knowledge/EDITORIAL_MATRIX.md').write_text(markdown(rows))
    print(json.dumps({'content_notes':len(rows),'first_course':68,'second_course':42,'result':'ok','scope':'structural, not mathematical proof'}))
