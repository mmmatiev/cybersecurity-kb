#!/usr/bin/env python3
"""Audit the Foundations of Cryptography and Steganography integration."""

from __future__ import annotations

import hashlib
import json
import re
import struct
import sys
from collections import Counter, defaultdict
from pathlib import Path

import pymupdf

from build_crypto_steganography_knowledge import SELF_CHECKS, TITLE_MAP, localize_prose
from crypto_steganography_enrichment import DETAILS, EXTERNAL_SOURCES


VAULT = Path(__file__).resolve().parents[2]
COURSE_NAME = "Основы криптографии и стеганографии"
COURSE = VAULT / "07 Sources" / "Courses" / COURSE_NAME
DESKTOP = Path("/Users/mmmatiev/Desktop/основы_крипты")
VISUALS = VAULT / "90 Attachments" / "Courses" / COURSE_NAME
KNOWLEDGE = VAULT / "01 Knowledge"
GENERATED_MARKER = "<!-- generated: crypto-stego-course -->"
UPDATE_START = "<!-- crypto-stego-course:start -->"
SOURCE_PREFIX = "Source - Основы криптографии и стеганографии - Лекция"
EXTERNAL_NOTE = "Source - Дополнительные материалы по криптографии и стеганографии"

CLASSICAL_KEYS = {
    "Classical Cryptography", "Substitution Ciphers", "Polybius Square", "Affine Cipher",
    "Transposition Ciphers", "Cardan Grille Cipher", "Playfair Cipher", "Hill Cipher",
    "Vigenere Cipher", "Frequency Analysis", "Perfect Secrecy and Cryptographic Strength",
}
IMAGE_FOUNDATION_KEYS = {
    "Digital Image Fundamentals", "Image Color Models", "Digital Image File Formats",
    "Lossless Image Compression", "JPEG Compression", "Image Frequency-Domain Transforms",
    "Discrete Fourier and Cosine Transforms for Images", "Walsh-Hadamard Transform",
    "Discrete Wavelet Transform",
}
STEGANOGRAPHY_KEYS = {
    "Steganography", "Information Hiding", "Digital Steganography", "Digital Watermarking",
    "Steganography Quality Metrics", "Digital Watermark Attacks",
    "Spatial-Domain Image Steganography", "LSB Steganography",
    "Plus-Minus One Steganography", "Quantization Index Modulation",
    "Pixel Value Differencing", "Neighbor Mean Interpolation",
    "Frequency-Domain Image Steganography", "Koch-Zhao Method", "JPEG Steganography",
    "JSteg", "F3 and F4 JPEG Steganography", "F5 JPEG Steganography", "Steganalysis",
    "Visual Steganalysis and Bit-Plane Analysis", "Statistical Steganalysis",
    "Machine Learning for Steganalysis", "Neural Network Steganalysis",
}
CLASSICAL = {TITLE_MAP[title] for title in CLASSICAL_KEYS}
IMAGE_FOUNDATIONS = {TITLE_MAP[title] for title in IMAGE_FOUNDATION_KEYS}
STEGANOGRAPHY = {TITLE_MAP[title] for title in STEGANOGRAPHY_KEYS}
EXPECTED_NOTES = CLASSICAL | IMAGE_FOUNDATIONS | STEGANOGRAPHY
COMMON_HEADINGS = {
    "Что нужно знать заранее", "Пояснение и границы применения", "Мини-практика",
    "Что запомнить", "Связи", "Самопроверка", "Источники",
}
TYPE_HEADINGS = {
    "concept": {
        "Кратко", "Зачем это нужно", "Основные понятия", "Как это устроено",
        "Формальная модель", "Разобранный пример", "Ограничения и типичные ошибки",
    },
    "technique": {
        "Кратко", "Где применяется", "Входные данные и результат",
        "Пошаговый алгоритм", "Формулы и обозначения", "Разбор примера",
        "Как проверить результат", "Ограничения и ошибки",
    },
    "attack": {
        "Цель атаки", "Предпосылки", "Основные понятия", "Как проходит атака",
        "Последствия и признаки", "Разбор сценария", "Противодействие",
        "Ограничения анализа и ошибки",
    },
}
WORD_BOUNDS = {"compact": (400, 600), "standard": (600, 850), "deep": (850, 1100)}
ALLOWED_TYPES = {"concept", "attack", "technique", "moc"}
ALLOWED_AREAS = {"Computer Science", "Cryptography", "Cybersecurity", "AI & ML"}
ALLOWED_SECURITY = {"Steganography", "DFIR", "Security Engineering"}
EMAIL_RE = re.compile(r"[\w.+-]+@[\w.-]+\.[A-Za-zА-Яа-я]{2,}")
PHONE_RE = re.compile(
    r"(?<!\d)(?:\+?7|8)[\s()\-]{0,3}\d{3}[\s()\-]{0,3}"
    r"\d{3}[\s\-]{0,2}\d{2}[\s\-]{0,2}\d{2}(?!\d)"
)
BANNED_PROSE_RE = re.compile(
    r"\b(?:embedding|payload|pipeline|padding|shrinkage|foundations?|workstream|targeted|baseline|accuracy|preprocessing|saliency)\b"
    r"|feature engineering|false positive|confusion matrix|cover/stego|pairs-of-values|робаст\w*|ресэмпл\w*"
    r"|разруш\(req\)|помRect",
    re.I,
)


def fail(message: str) -> None:
    raise RuntimeError(message)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def frontmatter(text: str) -> tuple[dict[str, object], str]:
    match = re.match(r"\A---\n(.*?)\n---\n", text, re.S)
    if not match:
        fail("missing YAML frontmatter")
    data: dict[str, object] = {}
    lines = match.group(1).splitlines()
    index = 0
    while index < len(lines):
        scalar = re.fullmatch(r"([A-Za-z_]+):(?: (.*))?", lines[index])
        if not scalar:
            fail(f"unsupported frontmatter line: {lines[index]!r}")
        key, value = scalar.groups()
        if value:
            data[key] = value.strip().strip('"')
            index += 1
            continue
        values: list[str] = []
        index += 1
        while index < len(lines):
            item = re.fullmatch(r"  - (.*)", lines[index])
            if not item:
                break
            values.append(item.group(1).strip().strip('"'))
            index += 1
        data[key] = values
    return data, text[match.end():]


def study_word_count(body: str) -> int:
    """Count explanatory prose before navigation, excluding embeds and link syntax."""
    body = body.split("\n## Связи\n", 1)[0]
    body = re.sub(r"```.*?```", " ", body, flags=re.S)
    body = re.sub(r"!\[\[[^\n]+", " ", body)
    body = re.sub(r"\[([^\]]+)\]\([^\)]+\)", r"\1", body)
    body = re.sub(r"\[\[([^\]|]+)(?:\|[^\]]+)?\]\]", r"\1", body)
    body = re.sub(r"(?m)^#+\s+.*$", " ", body)
    return len(re.findall(r"[A-Za-zА-Яа-яЁё0-9]+(?:[-—][A-Za-zА-Яа-яЁё0-9]+)*", body))


def long_paragraphs(body: str) -> list[str]:
    paragraphs: list[str] = []
    for paragraph in re.split(r"\n\s*\n", body):
        cleaned = re.sub(r"!?(?:\[\[[^]]+\]\]|\[[^]]+\]\([^)]*\))", " ", paragraph)
        cleaned = re.sub(r"[`*_>#|$]", " ", cleaned)
        cleaned = re.sub(r"\s+", " ", cleaned).strip().casefold()
        if len(cleaned) >= 220 and not cleaned.startswith("обозначения и смысл"):
            paragraphs.append(cleaned)
    return paragraphs


def png_dimensions(path: Path) -> tuple[int, int]:
    with path.open("rb") as stream:
        header = stream.read(24)
    if len(header) != 24 or header[:8] != b"\x89PNG\r\n\x1a\n":
        fail(f"invalid PNG: {path.relative_to(VAULT)}")
    return struct.unpack(">II", header[16:24])


def index_notes() -> tuple[dict[str, Path], dict[str, list[Path]]]:
    names: dict[str, list[Path]] = defaultdict(list)
    canonical: dict[str, Path] = {}
    for path in VAULT.rglob("*.md"):
        if ".git" in path.parts or ".trash" in path.parts:
            continue
        text = path.read_text(encoding="utf-8")
        if not text.startswith("---\n"):
            continue
        metadata, _ = frontmatter(text)
        names[path.stem].append(path)
        canonical[path.stem] = path
        aliases = metadata.get("aliases", [])
        if isinstance(aliases, list):
            for alias in aliases:
                canonical[str(alias)] = path
    duplicates = {name: paths for name, paths in names.items() if len(paths) > 1}
    if duplicates:
        fail(f"duplicate markdown basenames: {sorted(duplicates)}")
    return canonical, names


def check_sources() -> dict[str, object]:
    index_path = COURSE / "source-index.json"
    if not index_path.is_file():
        fail("missing source index")
    index = json.loads(index_path.read_text(encoding="utf-8"))
    records = index.get("files", [])
    if len(records) != 14 or index.get("original_pages") != 256 or index.get("public_pages") != 242:
        fail("unexpected source or page counts")

    for record in records:
        number = int(record["lecture"])
        original = DESKTOP / str(record["original_filename"])
        public = VAULT / str(record["public_path"])
        processed = VAULT / str(record["processed_path"])
        if not original.is_file() or sha256(original) != record["original_sha256"]:
            fail(f"original hash mismatch: lecture {number:02d}")
        if not public.is_file() or sha256(public) != record["public_sha256"]:
            fail(f"public hash mismatch: lecture {number:02d}")
        manifest_path = processed / "manifest.json"
        extract_path = processed / "extracted-text.md"
        if not manifest_path.is_file() or not extract_path.is_file():
            fail(f"missing processed files: lecture {number:02d}")
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        sanitation = record["sanitization"]
        if int(sanitation["original_pages"]) - int(sanitation["public_pages"]) != 1:
            fail(f"page sanitation mismatch: lecture {number:02d}")
        expected_redactions = [3, 4] if number == 1 else []
        if sanitation["redacted_pages"] != expected_redactions:
            fail(f"redaction mapping mismatch: lecture {number:02d}")
        mapping = sanitation["page_mapping"]
        if len(mapping) != int(sanitation["public_pages"]) or any(
            row["public_page"] != row["original_page"] for row in mapping
        ):
            fail(f"page mapping mismatch: lecture {number:02d}")
        if manifest.get("public_sha256") != record["public_sha256"]:
            fail(f"manifest hash mismatch: lecture {number:02d}")

        document = pymupdf.open(public)
        try:
            text = "\n".join(page.get_text() for page in document)
            metadata = "\n".join(str(value) for value in (document.metadata or {}).values())
            links = "\n".join(str(link.get("uri", "")) for page in document for link in page.get_links())
            if EMAIL_RE.search(text + metadata + links) or PHONE_RE.search(text + metadata + links):
                fail(f"contact-shaped material remains: lecture {number:02d}")
            if "mailto:" in links.lower() or "tel:" in links.lower():
                fail(f"contact annotation remains: lecture {number:02d}")
        finally:
            document.close()

    pdfs = list((COURSE / "PDF").glob("*.pdf"))
    manifests = list((COURSE / "Processed").glob("*/manifest.json"))
    extracts = list((COURSE / "Processed").glob("*/extracted-text.md"))
    source_notes = list((COURSE / "Source Notes").glob("Source - *.md"))
    lecture_notes = list((COURSE / "Source Notes").glob(f"{SOURCE_PREFIX} *.md"))
    bibliography = COURSE / "Source Notes" / f"{EXTERNAL_NOTE}.md"
    course_note = COURSE / f"Course - {COURSE_NAME}.md"
    if tuple(map(len, (pdfs, manifests, extracts, lecture_notes, source_notes))) != (14, 14, 14, 14, 15):
        fail("course file count mismatch")
    if not course_note.is_file() or not bibliography.is_file():
        fail("missing course note or external bibliography")
    bibliography_text = bibliography.read_text(encoding="utf-8")
    for source in EXTERNAL_SOURCES.values():
        if source.url not in bibliography_text:
            fail(f"external source missing from bibliography: {source.key}")
    for old_title in DETAILS:
        if f"[[{TITLE_MAP[old_title]}]]" not in bibliography_text:
            fail(f"card missing from external bibliography: {old_title}")
    if f"[[{EXTERNAL_NOTE}]]" not in course_note.read_text(encoding="utf-8"):
        fail("course note does not link external bibliography")
    return {
        "course_pdfs": len(pdfs), "course_manifests": len(manifests),
        "course_source_notes": len(lecture_notes), "external_bibliographies": 1,
        "public_pages": index["public_pages"],
        "original_hashes_unchanged": True, "contact_scan": "clean",
    }


def check_knowledge() -> dict[str, int]:
    canonical, _ = index_notes()
    questions = [question for group in SELF_CHECKS.values() for question in group]
    if len(questions) != 126 or len(set(questions)) != 126:
        fail("self-check questions must contain 126 unique prompts")
    actual = {
        path.stem
        for path in KNOWLEDGE.rglob("*.md")
        if GENERATED_MARKER in path.read_text(encoding="utf-8")
    }
    if actual != EXPECTED_NOTES:
        fail(f"new note set mismatch: missing={sorted(EXPECTED_NOTES-actual)}, extra={sorted(actual-EXPECTED_NOTES)}")
    moc = canonical.get("Стеганография")
    if moc is None:
        fail("missing Стеганография MOC")
    moc_text = moc.read_text(encoding="utf-8")

    visual_embeds = 0
    mermaid_diagrams = 0
    word_counts: list[int] = []
    paragraph_owners: dict[str, list[str]] = defaultdict(list)
    for title in sorted(EXPECTED_NOTES):
        path = canonical.get(title)
        if path is None:
            fail(f"missing required note: {title}")
        text = path.read_text(encoding="utf-8")
        data, body = frontmatter(text)
        h1 = re.search(r"(?m)^# (.+)$", body)
        if h1 is None or h1.group(1) != title or path.stem != title:
            fail(f"filename and H1 mismatch: {title}")
        if data.get("type") not in ALLOWED_TYPES:
            fail(f"invalid type: {title}")
        areas = data.get("area")
        if not isinstance(areas, list) or not 1 <= len(areas) <= 2 or not set(areas) <= ALLOWED_AREAS:
            fail(f"invalid area: {title}")
        security = data.get("security")
        if title in STEGANOGRAPHY:
            if not isinstance(security, list) or "Steganography" not in security or not set(security) <= ALLOWED_SECURITY:
                fail(f"invalid Steganography security metadata: {title}")
        elif security is not None and (
            not isinstance(security, list) or not set(security) <= ALLOWED_SECURITY
        ):
            fail(f"invalid security metadata: {title}")
        old_title = next(old for old, localized in TITLE_MAP.items() if localized == title)
        detail = DETAILS.get(old_title)
        aliases = data.get("aliases", [])
        if title != "JSteg" and (
            not isinstance(aliases, list) or old_title not in aliases
        ):
            fail(f"missing English alias: {title}")
        if title == "Стеганография":
            if data.get("type") != "moc":
                fail("Стеганография must be a MOC")
            continue
        if detail is None:
            fail(f"missing enrichment data: {title}")
        headings = set(re.findall(r"(?m)^## (.+)$", body))
        required_headings = COMMON_HEADINGS | TYPE_HEADINGS[str(data["type"])]
        if not required_headings <= headings:
            fail(f"missing study section in {title}: {sorted(required_headings-headings)}")
        opening = "Цель атаки" if data["type"] == "attack" else "Кратко"
        intro_match = re.search(rf"(?m)^## {re.escape(opening)}\n\n([^\n]+)", body)
        if intro_match is None:
            fail(f"missing introductory paragraph in {title}")
        has_short_identifier = re.search(r"(?:[A-ZА-ЯЁ]{2,}|[A-Z]\d)", title)
        if old_title != title and not has_short_identifier and old_title not in intro_match.group(1):
            fail(f"English term is not introduced in {title}")
        formula_blocks = body.count("$$") // 2
        if not formula_blocks or body.count("$$") % 2:
            fail(f"missing MathJax in {title}")
        if body.count("**Обозначения и смысл.**") != formula_blocks:
            fail(f"formula notation is not explained in {title}")
        if not re.search(
            rf"\[\[{re.escape(SOURCE_PREFIX)} \d{{2}}\]\], стр\. [\d,– ]+\.", body
        ):
            fail(f"missing exact course provenance in {title}")
        if f"[[{title}]]" not in moc_text and title not in CLASSICAL and title not in IMAGE_FOUNDATIONS:
            fail(f"Steganography note is not linked from its MOC: {title}")
        expected_questions = SELF_CHECKS[old_title]
        if any(f"{index}. {question}" not in body for index, question in enumerate(expected_questions, start=1)):
            fail(f"missing subject-specific self-check in {title}")
        if body.count("> [!answer]- Ответы") != 1 or any(
            f"> {index}. {localize_prose(answer)}" not in body
            for index, answer in enumerate(detail.answers, start=1)
        ):
            fail(f"missing three reference answers in {title}")
        if "Сформулируйте назначение" in body:
            fail(f"generic self-check remains in {title}")
        count = study_word_count(body)
        lower, upper = WORD_BOUNDS[detail.depth]
        if not lower <= count <= upper:
            fail(f"study prose outside {detail.depth} range in {title}: {count} not in {lower}..{upper}")
        word_counts.append(count)
        for source_key in detail.source_keys:
            source_record = EXTERNAL_SOURCES.get(source_key)
            if source_record is None or source_record.url not in body:
                fail(f"missing direct external source {source_key} in {title}")
        expected_mermaid = 1 if detail.diagram else 0
        actual_mermaid = body.count("```mermaid")
        if actual_mermaid != expected_mermaid:
            fail(f"Mermaid diagram mismatch in {title}: {actual_mermaid} != {expected_mermaid}")
        mermaid_diagrams += actual_mermaid
        for paragraph in long_paragraphs(body):
            paragraph_owners[paragraph].append(title)
        prose = re.sub(r"\$\$.*?\$\$", "", body, flags=re.S)
        prose = re.sub(r"!?\[\[[^]]+\]\]", "", prose)
        prose = re.sub(r"\[[^]]+\]\([^)]*\)", "", prose)
        prose = re.sub(r"`[^`]*`", "", prose)
        match = BANNED_PROSE_RE.search(prose)
        if match:
            fail(f"unnecessary English calque remains in {title}: {match.group(0)}")
        visual_embeds += len(re.findall(rf"!\[\[{re.escape('90 Attachments/Courses/'+COURSE_NAME)}/[^]]+\.png\]\]", body))

    repeated = {
        paragraph: owners for paragraph, owners in paragraph_owners.items()
        if len(set(owners)) > 1
    }
    if repeated:
        example = next(iter(repeated.values()))
        fail(f"repeated long explanatory paragraph in: {sorted(set(example))}")
    if mermaid_diagrams != 12:
        fail(f"expected 12 Mermaid diagrams, got {mermaid_diagrams}")

    updated = [
        path for path in KNOWLEDGE.rglob("*.md")
        if UPDATE_START in path.read_text(encoding="utf-8")
    ]
    if len(updated) != 10:
        fail(f"expected ten preserved-note updates, got {len(updated)}")
    return {
        "new_canonical_notes": len(actual), "expanded_content_notes": len(word_counts),
        "updated_existing_notes": len(updated), "visual_embeds": visual_embeds,
        "mermaid_diagrams": mermaid_diagrams, "min_words": min(word_counts),
        "max_words": max(word_counts),
    }


def check_visuals() -> dict[str, int]:
    manifest_path = VISUALS / "visual-manifest.json"
    if not manifest_path.is_file():
        fail("missing visual manifest")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    records = manifest.get("visuals", [])
    if len(records) != 24:
        fail(f"expected 24 visuals, got {len(records)}")
    if manifest.get("category_counts") != {"classical": 5, "images": 4, "embedding": 9, "steganalysis": 6}:
        fail("visual category count mismatch")
    files = sorted(path.name for path in VISUALS.glob("*.png"))
    names = sorted(str(record["filename"]) for record in records)
    if files != names or len(set(names)) != 24:
        fail("visual file set mismatch")

    canonical, _ = index_notes()
    for record in records:
        output = VISUALS / str(record["filename"])
        source_pdf = VAULT / str(record["source_pdf"])
        if sha256(output) != record["sha256"]:
            fail(f"visual hash mismatch: {record['filename']}")
        if sha256(source_pdf) != record["source_pdf_sha256"]:
            fail(f"visual source hash mismatch: {record['filename']}")
        if list(png_dimensions(output)) != [record["width"], record["height"]]:
            fail(f"visual dimension mismatch: {record['filename']}")
        if output.stat().st_size < 20_000 or record["width"] < 1000 or record["height"] < 700:
            fail(f"visual too small: {record['filename']}")
        for title in record["target_notes"]:
            target = canonical.get(str(title))
            if target is None:
                fail(f"missing visual target: {title}")
            body = target.read_text(encoding="utf-8")
            embed = f"![[90 Attachments/Courses/{COURSE_NAME}/{record['filename']}]]"
            attribution = f"[[{record['source_note']}]], стр. {record['page']}"
            if embed not in body or attribution not in body or "*Что смотреть:*" not in body:
                fail(f"visual attribution mismatch: {record['filename']}")
    return {"course_visuals": len(records), "visual_targets": len({t for r in records for t in r["target_notes"]})}


def main() -> int:
    if len(CLASSICAL) != 11 or len(IMAGE_FOUNDATIONS) != 9 or len(STEGANOGRAPHY) != 23:
        fail("required note group counts changed")
    source_stats = check_sources()
    knowledge_stats = check_knowledge()
    visual_stats = check_visuals()
    print(json.dumps({**source_stats, **knowledge_stats, **visual_stats, "result": "ok"}, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except RuntimeError as error:
        print(f"audit=failed: {error}", file=sys.stderr)
        raise SystemExit(1)
