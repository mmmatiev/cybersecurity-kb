#!/usr/bin/env python3
"""Build only thematic navigation. Default is a read-only freshness check."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from collections import Counter
from pathlib import Path

from enhance_cryptography_notes import ALIASES
from thematic_clusters import BY_ID, CANVAS_EDGES, CANVAS_GROUPS, CANVAS_PATH, CLUSTERS

VAULT = Path(__file__).resolve().parents[2]
MANIFEST = Path("scripts/knowledge/thematic-clusters-manifest.json")
END = "<!-- thematic-clusters:end -->"
START_RE = re.compile(r"<!-- thematic-clusters:start sha256=([a-f0-9]{64}) -->\n")

# Exact preimages authorize the one-time migration, not arbitrary future edits.
NAVIGATION = {
    "crypto": ("Cryptography/Cryptography", "## Основы\n", "Стеганография не",
        "fff9f1c797d5c134923235412d6af523469b0e2f4fd280a969006a7135e151ed"),
    "cs": ("Computer Science/Computer Science", "## Системы, связанные с криптографией\n", "Вернуться на",
        "71d34b39f23fa65522fb112ff491c027c1357a47386caa6d3910de547259fcee"),
    "networks": ("Networks/Networks", "## Protected communication\n", "Вернуться на",
        "45283be58c28fbaec7243fc4a37ec246ca1581c06d5f4c56620873085370a7d2"),
    "security": ("Cybersecurity/Cybersecurity", "## Атаки на криптографические системы\n", "## Практическая работа\n",
        "39367fb9cbf8b37d459c06423b81f750f1d75313e3c17471301355df40670f48"),
    "engineering": ("Cybersecurity/Security Engineering/Security Engineering", "## Криптография\n", "## Практическая работа\n",
        "4210e60e6bde30b0ad62538932e815cf8d7875d4c4734323e8770e2cf0aa3ecf"),
    "stego": ("Cybersecurity/Steganography/Стеганография", "## Как изучать\n", "## Формальная модель\n",
        "007ea51f4532d66114334fb845e0232920e4a7d3e3879d14a8600698b42c9f16"),
}


def digest(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def cluster_link(number: int) -> str:
    c = BY_ID[number]
    return f"[[{c.basename}|{c.title}]]"


def note_link(title: str) -> str:
    label = ALIASES.get(title, [title])[0]
    return f"[[{title}|{label}]]" if label != title else f"[[{title}]]"


def map_link() -> str:
    return f"[[{CANVAS_PATH.as_posix()}|Общая карта тем]]"


def navigation_body(key: str) -> str:
    if key == "crypto":
        groups = (("Основы и математика", (1, 2, 3, 4)),
                  ("Криптографические механизмы", (5, 6, 7)),
                  ("Инфраструктура, приложения и анализ", (8, 9, 10, 13)),
                  ("Квантовая и постквантовая область", (11, 12)))
        intro = "Выберите тему ниже. Внутри каждого кластера карточки расположены в учебном порядке; начинать весь курс заново не требуется."
    elif key == "cs":
        groups = (("Системы, связанные с криптографией", (13, 11, 12)),
                  ("Цифровые изображения", (14, 15)))
        intro = "Изображения изучаются как самостоятельная техническая основа, а затем используются в [[Стеганография|стеганографии]]."
    elif key == "networks":
        groups = (("Защищённая связь", (9,)),)
        intro = "Протоколы собраны в один маршрут. [[TLS]] сохраняет своё место в [[Cryptography]], сетевые карточки остаются в Networks."
    elif key == "security":
        groups = (("Анализ криптографических систем", (10, 13)),
                  ("Сокрытие и обнаружение", (16, 19)))
        intro = "Тематические карты соединяют технологические основы и атаки без копирования карточек между направлениями. Полный маршрут сокрытия данных — [[Стеганография]]."
    elif key == "engineering":
        groups = (("Криптография и безопасность систем", (10, 13, 8)),)
        intro = "Начните с модели угроз, затем переходите к конкретному механизму. Регулирование и сертификация находятся в отдельной подгруппе инфраструктурного кластера; сведения курса требуют проверки актуальности."
    elif key == "stego":
        groups = (("Технические основы", (14, 15)),
                  ("Сокрытие и встраивание", (16, 17, 18)),
                  ("Проверка обнаружимости", (19,)))
        intro = "Маршрут: представление изображений → цели сокрытия → пространственные методы → преобразования и JPEG → стегоанализ. Если основы изображений уже знакомы, начните с целей сокрытия. Это самостоятельная последовательность, не продолжение курса шифрования."
    else:
        raise ValueError(f"Unknown navigation key: {key}")
    lines = ["## Тематические кластеры", "", intro, "", map_link() + " — обзор двух учебных маршрутов на Canvas.", ""]
    for title, numbers in groups:
        lines += [f"### {title}", ""]
        lines += [f"- {cluster_link(n)} — {BY_ID[n].purpose[0].lower() + BY_ID[n].purpose[1:]}" for n in numbers]
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def replace_navigation(key: str, text: str) -> str:
    """Preserve bytes outside the authorized navigation span; reject manual edits."""
    matches = list(START_RE.finditer(text))
    if matches:
        if len(matches) != 1 or text.count(END) != 1 or text.count("<!-- thematic-clusters:start") != 1:
            raise RuntimeError(f"Malformed navigation markers: {key}")
        match = matches[0]
        end = text.index(END)
        old = text[match.end():end]
        if end < match.end() or digest(old) != match.group(1):
            raise RuntimeError(f"Manual changes in navigation block: {key}")
        start, stop = match.start(), end + len(END)
        trailing = ""
    else:
        if "thematic-clusters:" in text:
            raise RuntimeError(f"Malformed navigation markers: {key}")
        _, begin, finish, expected = NAVIGATION[key]
        if text.count(begin) != 1 or text.count(finish) != 1:
            raise RuntimeError(f"Cannot locate original navigation: {key}")
        start, stop = text.index(begin), text.index(finish)
        if stop <= start or digest(text[start:stop]) != expected:
            raise RuntimeError(f"Original navigation changed; review migration: {key}")
        trailing = "\n\n"
    body = navigation_body(key)
    replacement = f"<!-- thematic-clusters:start sha256={digest(body)} -->\n{body}{END}"
    return text[:start] + replacement + trailing + text[stop:]


def render_cluster(c) -> str:
    area = "Cryptography" if c.domain == "Cybersecurity/Security Engineering" else c.domain.split("/")[0]
    if c.domain.endswith("Steganography"):
        area = "Computer Science"
    lines = ["---", "type: moc", "area:", f"  - {area}"]
    if c.domain.startswith("Cybersecurity/"):
        lines += ["security:", f"  - {c.domain.split('/')[-1]}"]
    lines += ["---", "", "<!-- generated: thematic-clusters -->", f"# {c.basename}", "",
              "## Обзор", "", f"**{c.number:02d} · {c.title}**", "", c.purpose, "",
              f"Карточек в основном маршруте: {sum(len(s.entries) for s in c.sections)}.", "",
              "## Что нужно знать заранее", ""]
    if c.prerequisites:
        lines += [f"- {cluster_link(n)}." for n in c.prerequisites]
    else:
        lines += ["Можно начинать здесь: специальные знания из других кластеров не обязательны."]
    lines += ["", "## Порядок изучения", "",
              " → ".join(s.title for s in c.sections) + ".", "",
              "Читайте карточки в порядке списка. После каждой попробуйте объяснить механизм своими словами и ответить на её вопросы для самопроверки.", "",
              "## Карточки по подгруппам", ""]
    for s in c.sections:
        lines += [f"### {s.title}", ""]
        lines += [f"- {note_link(title)} — {description}." for title, description in s.entries]
        lines.append("")
    if c.secondary:
        lines += ["## Дополнительные связи", ""]
        lines += [f"- {note_link(title)} — {description}." for title, description in c.secondary]
        lines.append("")
    lines += ["## Связанные кластеры", ""]
    lines += [f"- {cluster_link(n)}." for n in c.related]
    lines += ["", "## Навигация", "", f"Родительский раздел: [[{c.parent}]]. {map_link()}.", "",
              "Это карта чтения, а не новая теоретическая карточка. Формулы, примеры, иллюстрации и источники остаются в связанных заметках. Для возвращения из карточки используйте обратные ссылки Obsidian.", ""]
    return "\n".join(lines)


def render_canvas() -> dict:
    nodes = []
    for key, label, color, x, y, numbers in CANVAS_GROUPS:
        nodes.append(dict(id=f"group-{key}", type="group", label=label, color=color,
                          x=x, y=y, width=640, height=100 + len(numbers) * 380))
    nodes.append(dict(id="legend", type="text", x=0, y=-270, width=3460, height=190,
        text="# Криптография и стеганография · карта тем\n\n"
             "**Слева — криптография. Справа — изображения и стеганография.** Это два самостоятельных маршрута. "
             "Каждый узел открывает страницу темы с подгруппами и карточками. Стрелки показывают отдельные учебные зависимости, а не все связи базы. "
             "Для деталей приблизьте нужную группу и откройте её страницу."))
    for _, _, color, x, y, numbers in CANVAS_GROUPS:
        for row, n in enumerate(numbers):
            nodes.append(dict(id=f"cluster-{n:02d}", type="file", file=BY_ID[n].path.as_posix(),
                subpath="#Обзор", color=color, x=x + 30, y=y + 70 + row * 380,
                width=580, height=300))
    edges = [dict(id=f"edge-{a:02d}-{b:02d}", fromNode=f"cluster-{a:02d}",
                  toNode=f"cluster-{b:02d}", fromSide=side_a, toSide=side_b,
                  fromEnd="none", toEnd="arrow") for a, b, side_a, side_b in CANVAS_EDGES]
    return dict(nodes=nodes, edges=edges)


def serialize(data) -> str:
    return json.dumps(data, ensure_ascii=False, indent=2) + "\n"


def corpus_paths(root: Path) -> dict[str, Path]:
    from build_crypto_steganography_knowledge import NOTES, canonical_title
    expected = set(ALIASES) | {canonical_title(n.title) for n in NOTES}
    entries = [title for c in CLUSTERS for s in c.sections for title, _ in s.entries]
    counts = Counter(entries)
    if len(CLUSTERS) != 19 or len(BY_ID) != 19 or set(counts) != expected or any(n != 1 for n in counts.values()):
        raise RuntimeError(f"Invalid primary membership: missing={sorted(expected-set(counts))}, extra={sorted(set(counts)-expected)}, duplicate={[k for k,v in counts.items() if v!=1]}")
    result = {}
    files = list((root / "01 Knowledge").rglob("*.md"))
    for title in expected:
        matches = [p for p in files if p.stem == title]
        if len(matches) != 1:
            raise RuntimeError(f"Missing or duplicate canonical note: {title}")
        result[title] = matches[0].relative_to(root)
    for c in CLUSTERS:
        if c.number in c.prerequisites + c.related or not set(c.prerequisites + c.related) <= set(BY_ID):
            raise RuntimeError(f"Invalid cluster relation: {c.number}")
        if not {title for title, _ in c.secondary} <= expected:
            raise RuntimeError(f"Unknown secondary note in cluster {c.number}")
    return result


def desired_outputs(root: Path) -> dict[Path, str]:
    corpus = corpus_paths(root)
    owned = {c.path: render_cluster(c) for c in CLUSTERS}
    owned[CANVAS_PATH] = serialize(render_canvas())
    old_manifest_path = root / MANIFEST
    old_manifest = json.loads(old_manifest_path.read_text()) if old_manifest_path.exists() else None
    if old_manifest is not None and (old_manifest.get("version") != 1 or set(old_manifest.get("outputs", {})) != {p.as_posix() for p in owned}):
        raise RuntimeError("Unexpected thematic manifest; review changes before generation")
    # Validate every target before returning any write operations.
    for path in owned:
        target = root / path
        if target.exists():
            if not old_manifest or digest(target.read_text()) != old_manifest["outputs"].get(path.as_posix()):
                raise RuntimeError(f"Manual changes or unowned existing file: {path}")
        elif old_manifest:
            raise RuntimeError(f"Previously generated file is missing: {path}")
    outputs = dict(owned)
    for key, (stem, _, _, _) in NAVIGATION.items():
        path = Path("01 Knowledge") / (stem + ".md")
        outputs[path] = replace_navigation(key, (root / path).read_text(encoding="utf-8"))
    outputs[MANIFEST] = serialize({
        "version": 1,
        "outputs": {p.as_posix(): digest(text) for p, text in owned.items()},
        "primary_membership": {title: {"note": corpus[title].as_posix(), "cluster": c.path.as_posix()}
                               for c in CLUSTERS for s in c.sections for title, _ in s.entries},
    })
    return outputs


def build(root: Path, write: bool = False) -> list[Path]:
    outputs = desired_outputs(root)
    changed = [p for p, content in outputs.items()
               if not (root / p).exists() or (root / p).read_text(encoding="utf-8") != content]
    if write:
        for p in changed:
            target = root / p
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(outputs[p], encoding="utf-8")
    return changed


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--vault-root", type=Path, default=VAULT)
    parser.add_argument("--write", action="store_true", help="Write validated navigation changes (default: check only)")
    args = parser.parse_args()
    try:
        changed = build(args.vault_root.resolve(), args.write)
    except (OSError, ValueError, RuntimeError) as exc:
        parser.exit(1, f"thematic_clusters=failed: {exc}\n")
    print(f"thematic_clusters={'written' if args.write else 'checked'}; changed={len(changed)}; clusters={len(CLUSTERS)}")
    if changed and not args.write:
        print("Run with --write after reviewing the generated navigation.")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
