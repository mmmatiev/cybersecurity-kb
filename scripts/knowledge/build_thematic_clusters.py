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
from thematic_clusters import (
    BY_ID, CANVAS_EDGES, CANVAS_GROUPS, CANVAS_LEGEND_GEOMETRY,
    CANVAS_NODE_OFFSETS, CANVAS_PATH, CLUSTERS, primary_membership,
)

VAULT = Path(__file__).resolve().parents[2]
MANIFEST = Path("scripts/knowledge/thematic-clusters-manifest.json")
BASE_PATH = Path("00 Home/Карточки по темам.base")
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
                  ("Инфраструктура, сетевые приложения и анализ", (8, 9, 10)),
                  ("Дополнительные приложения", (13,)),
                  ("Квантовая и постквантовая область", (11, 12)))
        intro = "Выберите тему ниже. Внутри каждой темы карточки расположены в учебном порядке; начинать весь курс заново не требуется."
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
        intro = "Начните с модели угроз, затем переходите к конкретному механизму. Регулирование и сертификация находятся в отдельной подгруппе инфраструктурной темы; сведения курса требуют проверки актуальности."
    elif key == "stego":
        groups = (("Технические основы", (14, 15)),
                  ("Сокрытие и встраивание", (16, 17, 18)),
                  ("Проверка обнаружимости", (19,)))
        intro = "Маршрут: представление изображений → цели сокрытия → пространственные методы → преобразования и JPEG → стегоанализ. Если основы изображений уже знакомы, начните с целей сокрытия. Это самостоятельная последовательность, не продолжение курса шифрования."
    else:
        raise ValueError(f"Unknown navigation key: {key}")
    lines = ["## Темы", "", intro, "", map_link() + " — обзор двух учебных маршрутов на Canvas.", ""]
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
    lines += ["aliases:", f'  - "{c.legacy_basename}"']
    lines += ["---", "", "<!-- generated: thematic-clusters -->", f"# {c.title}", "",
              "## Обзор", "", f"**{c.number:02d} · {c.title}**", "", c.purpose, "",
              "## Что нужно знать заранее", ""]
    if c.prerequisites:
        lines += [f"- {cluster_link(n)}." for n in c.prerequisites]
    else:
        lines += ["Можно начинать здесь: специальные знания из других тем не обязательны."]
    lines += ["", "## Порядок изучения", "",
              " → ".join(s.title for s in c.sections) + ".", "",
              "## Карточки по подгруппам", ""]
    for s in c.sections:
        lines += [f"### {s.title}", ""]
        lines += [f"- {note_link(title)} — {description}." for title, description in s.entries]
        lines.append("")
    if c.secondary:
        lines += ["## Дополнительные связи", ""]
        lines += [f"- {note_link(title)} — {description}." for title, description in c.secondary]
        lines.append("")
    lines += ["## Связанные темы", ""]
    lines += [f"- {cluster_link(n)}." for n in c.related]
    lines += ["", f"← [[{c.parent}]] · {map_link()} · [[{BASE_PATH.as_posix()}|Карточки по темам]]", ""]
    return "\n".join(lines)


def render_canvas() -> dict:
    nodes = []
    for key, label, color, x, y, numbers in CANVAS_GROUPS:
        nodes.append(dict(id=f"group-{key}", type="group", label=label, color=color,
                          x=x, y=y, width=640, height=100 + len(numbers) * 380))
    legend_x, legend_y, legend_width, legend_height = CANVAS_LEGEND_GEOMETRY
    nodes.append(dict(id="legend", type="text", x=legend_x, y=legend_y,
        width=legend_width, height=legend_height,
        text="# Криптография и стеганография · карта тем\n\n"
             "**Слева — криптография. Справа — изображения и стеганография.** Это два самостоятельных маршрута. "
             "Каждый узел открывает страницу темы с подгруппами и карточками. Стрелки показывают отдельные учебные зависимости, а не все связи базы. "
             "Для деталей приблизьте нужную группу и откройте её страницу."))
    for _, _, color, x, y, numbers in CANVAS_GROUPS:
        for row, n in enumerate(numbers):
            offset_x, offset_y = CANVAS_NODE_OFFSETS.get(n, (0, 0))
            nodes.append(dict(id=f"cluster-{n:02d}", type="file", file=BY_ID[n].path.as_posix(),
                subpath="#Обзор", color=color, x=x + 30 + offset_x,
                y=y + 70 + row * 380 + offset_y,
                width=580, height=300))
    edges = [dict(id=f"edge-{a:02d}-{b:02d}", fromNode=f"cluster-{a:02d}",
                  toNode=f"cluster-{b:02d}", fromSide=side_a, toSide=side_b)
             for a, b, side_a, side_b in CANVAS_EDGES]
    return dict(nodes=nodes, edges=edges)


def serialize(data) -> str:
    return json.dumps(data, ensure_ascii=False, indent=2) + "\n"


def legacy_path(cluster) -> Path:
    return Path("01 Knowledge") / cluster.domain / f"{cluster.legacy_basename}.md"


def apply_topic_metadata(text: str, cluster, order: int) -> str:
    """Set only the two generated study properties and preserve the note body."""
    match = re.match(r"\A---\n(.*?)\n---\n", text, re.S)
    if not match:
        raise RuntimeError(f"Missing frontmatter for topic {cluster.title}")
    lines = match.group(1).splitlines()
    if any(line.startswith("  - ") and index and lines[index - 1] in {"topic:", "study_order:"}
           for index, line in enumerate(lines)):
        raise RuntimeError("topic and study_order must be scalar properties")
    lines = [line for line in lines
             if not re.fullmatch(r"(?:topic|study_order):(?: .*)?", line)]
    lines += [f'topic: "[[{cluster.basename}]]"', f"study_order: {order}"]
    return "---\n" + "\n".join(lines) + "\n---\n" + text[match.end():]


def render_base() -> str:
    return '''filters:
  and:
    - 'file.ext == "md"'
    - 'file.inFolder("01 Knowledge")'
    - 'type != "moc"'
    - 'topic != null'
properties:
  file.name:
    displayName: Карточка
  study_order:
    displayName: Порядок
  type:
    displayName: Тип
  area:
    displayName: Область
  status:
    displayName: Статус
views:
  - type: table
    name: По темам
    groupBy:
      property: topic
      direction: ASC
    order:
      - file.name
      - study_order
      - type
      - area
      - status
    sort:
      - property: study_order
        direction: ASC
      - property: file.name
        direction: ASC
'''


def add_home_base_link(text: str) -> str:
    link = "- [[00 Home/Карточки по темам.base|Карточки по темам]]"
    if link in text:
        return text
    anchor = "- [[Cryptography]]\n"
    if text.count(anchor) != 1:
        raise RuntimeError("Cannot place the topic Base link in Home")
    return text.replace(anchor, anchor + link + "\n", 1)


def validate_v1_migration(root: Path, manifest: dict) -> None:
    expected = {legacy_path(c).as_posix() for c in CLUSTERS} | {CANVAS_PATH.as_posix()}
    if set(manifest.get("outputs", {})) != expected:
        raise RuntimeError("Unexpected version 1 thematic manifest")
    for cluster in CLUSTERS:
        path = legacy_path(cluster)
        target = root / path
        if not target.is_file() or digest(target.read_text()) != manifest["outputs"][path.as_posix()]:
            raise RuntimeError(f"Manual changes or missing legacy topic: {path}")
        if (root / cluster.path).exists():
            raise RuntimeError(f"Unowned topic destination already exists: {cluster.path}")
    canvas = json.loads((root / CANVAS_PATH).read_text())
    for node in canvas.get("nodes", []):
        if node.get("type") == "file" and node.get("id", "").startswith("cluster-"):
            number = int(node["id"].split("-")[1])
            if node.get("file") != legacy_path(BY_ID[number]).as_posix():
                raise RuntimeError(f"Unexpected legacy Canvas target: {node.get('id')}")
            node["file"] = BY_ID[number].path.as_posix()
    expected_canvas = render_canvas()
    same_nodes = {node["id"]: node for node in canvas.get("nodes", [])} == {
        node["id"]: node for node in expected_canvas["nodes"]
    }
    same_edges = {edge["id"]: edge for edge in canvas.get("edges", [])} == {
        edge["id"]: edge for edge in expected_canvas["edges"]
    }
    if set(canvas) != {"nodes", "edges"} or not same_nodes or not same_edges:
        raise RuntimeError("Manual Canvas changes exceed the accepted geometry")


def corpus_paths(root: Path) -> dict[str, Path]:
    from build_crypto_steganography_knowledge import NOTES, canonical_title
    expected = set(ALIASES) | {canonical_title(n.title) for n in NOTES}
    memberships = primary_membership()
    counts = Counter(title for c in CLUSTERS for s in c.sections for title, _ in s.entries)
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
    memberships = primary_membership()
    owned = {c.path: render_cluster(c) for c in CLUSTERS}
    owned[CANVAS_PATH] = serialize(render_canvas())
    owned[BASE_PATH] = render_base()
    old_manifest_path = root / MANIFEST
    old_manifest = json.loads(old_manifest_path.read_text()) if old_manifest_path.exists() else None
    version = old_manifest.get("version") if old_manifest else None
    if version == 1:
        validate_v1_migration(root, old_manifest)
        if (root / BASE_PATH).exists():
            raise RuntimeError(f"Unowned Base destination already exists: {BASE_PATH}")
    elif version == 2:
        if set(old_manifest.get("outputs", {})) != {p.as_posix() for p in owned}:
            raise RuntimeError("Unexpected version 2 thematic manifest")
        for path in owned:
            target = root / path
            if not target.is_file() or digest(target.read_text()) != old_manifest["outputs"].get(path.as_posix()):
                raise RuntimeError(f"Manual changes or missing generated file: {path}")
    elif old_manifest is not None:
        raise RuntimeError("Unexpected thematic manifest version")
    else:
        for path in owned:
            if (root / path).exists():
                raise RuntimeError(f"Unowned existing file: {path}")

    outputs = dict(owned)
    for key, (stem, _, _, _) in NAVIGATION.items():
        path = Path("01 Knowledge") / (stem + ".md")
        outputs[path] = replace_navigation(key, (root / path).read_text(encoding="utf-8"))
    for title, (cluster, order) in memberships.items():
        path = corpus[title]
        outputs[path] = apply_topic_metadata((root / path).read_text(encoding="utf-8"), cluster, order)
    home_path = Path("00 Home/Home.md")
    outputs[home_path] = add_home_base_link((root / home_path).read_text(encoding="utf-8"))
    outputs[MANIFEST] = serialize({
        "version": 2,
        "outputs": {p.as_posix(): digest(text) for p, text in owned.items()},
        "primary_membership": {
            title: {
                "note": corpus[title].as_posix(),
                "topic": cluster.path.as_posix(),
                "study_order": order,
            }
            for title, (cluster, order) in memberships.items()
        },
    })
    return outputs


def build(root: Path, write: bool = False) -> list[Path]:
    manifest_path = root / MANIFEST
    old_manifest = json.loads(manifest_path.read_text()) if manifest_path.exists() else None
    stale = [legacy_path(c) for c in CLUSTERS] if old_manifest and old_manifest.get("version") == 1 else []
    outputs = desired_outputs(root)
    changed = [p for p, content in outputs.items()
               if not (root / p).exists() or (root / p).read_text(encoding="utf-8") != content]
    changed += stale
    if write:
        for p in outputs:
            target = root / p
            content = outputs[p]
            if not target.exists() or target.read_text(encoding="utf-8") != content:
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text(content, encoding="utf-8")
        for p in stale:
            (root / p).unlink()
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
    print(f"thematic_topics={'written' if args.write else 'checked'}; changed={len(changed)}; topics={len(CLUSTERS)}")
    if changed and not args.write:
        print("Run with --write after reviewing the generated navigation.")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
