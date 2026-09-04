#!/usr/bin/env python3
"""Run deterministic integrity checks for the integrated cryptography course."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import re
import runpy
import struct
import sys
from collections import Counter, defaultdict
from pathlib import Path


VAULT = Path(__file__).resolve().parents[2]
COURSE_NAME = "Криптографические методы защиты информации"
COURSE = VAULT / "07 Sources" / "Courses" / COURSE_NAME
DESKTOP = Path("/Users/mmmatiev/Desktop/крипта")
KNOWLEDGE = VAULT / "01 Knowledge"
VISUALS = VAULT / "90 Attachments" / "Cryptography" / "Course Visuals"

ALLOWED_TYPES = {
    "concept", "attack", "vulnerability", "technique", "tool", "lab", "case",
    "research", "cheatsheet", "standard", "source", "moc",
}
ALLOWED_AREAS = {
    "Computer Science", "Networks", "Operating Systems", "Web", "Software Engineering",
    "Databases", "Cloud", "AI & ML", "Cryptography", "Cybersecurity",
}
ALLOWED_SECURITY = {
    "AppSec", "Network Security", "Infrastructure Security", "Cloud Security", "AI Security",
    "Threat Intelligence", "DFIR", "Malware", "OSINT", "Security Engineering", "Steganography",
}
REQUIRED_SECTIONS = {
    "Суть", "Как устроено", "Практический разбор", "Ограничения и безопасность",
    "Связи", "Самопроверка", "Источники курса",
}


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
        line = lines[index]
        scalar = re.fullmatch(r"([A-Za-z_]+):(?: (.*))?", line)
        if not scalar:
            fail(f"unsupported frontmatter line: {line!r}")
        key, value = scalar.groups()
        if value is not None and value != "":
            cleaned = value.strip()
            if cleaned == "[]":
                data[key] = []
            elif cleaned.startswith("[") and cleaned.endswith("]"):
                data[key] = [
                    item.strip().strip('"').strip("'")
                    for item in cleaned[1:-1].split(",")
                    if item.strip()
                ]
            else:
                data[key] = cleaned.strip('"')
            index += 1
            continue
        values: list[str] = []
        index += 1
        while index < len(lines):
            item = re.fullmatch(r"  - (.*)", lines[index])
            if not item:
                break
            values.append(item.group(1).strip('"'))
            index += 1
        data[key] = values
    return data, text[match.end():]


def load_expected_titles() -> set[str]:
    helper = VAULT / "scripts" / "knowledge" / "enhance_cryptography_notes.py"
    spec = importlib.util.spec_from_file_location("enhance_crypto", helper)
    if spec is None or spec.loader is None:
        fail("cannot load corpus definition")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return set(module.ALIASES)


def png_dimensions(path: Path) -> tuple[int, int]:
    with path.open("rb") as stream:
        header = stream.read(24)
    if len(header) != 24 or header[:8] != b"\x89PNG\r\n\x1a\n":
        fail(f"not a valid PNG: {path.relative_to(VAULT)}")
    return struct.unpack(">II", header[16:24])


def check_course_visuals() -> dict[str, int]:
    manifest_path = VISUALS / "course-visuals-manifest.json"
    if not manifest_path.is_file():
        fail("missing course visuals manifest")
    records = json.loads(manifest_path.read_text(encoding="utf-8")).get("visuals", [])
    if len(records) != 19:
        fail(f"expected 19 course visuals, got {len(records)}")
    names = [record["output"] for record in records]
    if len(set(names)) != len(names):
        fail("duplicate course visual output name")
    actual = sorted(path.name for path in VISUALS.glob("*.png"))
    if sorted(names) != actual:
        fail("course visual file set does not match manifest")

    target_notes: set[str] = set()
    kinds = Counter()
    for record in records:
        output = VISUALS / record["output"]
        source = VAULT / record["source_path"]
        target = VAULT / record["target_note"]
        if not source.is_file() or sha256(source) != record["source_sha256"]:
            fail(f"course visual source mismatch: {record['output']}")
        if not output.is_file() or sha256(output) != record["output_sha256"]:
            fail(f"course visual output mismatch: {record['output']}")
        width, height = png_dimensions(output)
        if [width, height] != [record["width"], record["height"]]:
            fail(f"course visual dimensions mismatch: {record['output']}")
        if width < 400 or height < 280:
            fail(f"course visual is too small: {record['output']} ({width}x{height})")
        if not target.is_file():
            fail(f"missing course visual target note: {record['target_note']}")
        target_text = target.read_text(encoding="utf-8")
        embed = f"![[90 Attachments/Cryptography/Course Visuals/{record['output']}]]"
        source_link = f"[[{record['source_note']}]]"
        if embed not in target_text or source_link not in target_text:
            fail(f"course visual is not fully attributed in {record['target_note']}")
        target_notes.add(record["target_note"])
        kinds[record["kind"]] += 1
    if kinds != {"pdf-page": 11, "docx-media": 8}:
        fail(f"unexpected course visual kinds: {dict(kinds)}")
    return {"course_visuals": len(records), "notes_with_course_visuals": len(target_notes)}


def check_sources() -> dict[str, int]:
    index = json.loads((COURSE / "source-index.json").read_text(encoding="utf-8"))
    records = index["files"]
    if len(records) != 42:
        fail(f"expected 42 source records, got {len(records)}")
    kinds = Counter(record["kind"] for record in records)
    expected_kinds = {"lecture": 21, "seminar": 11, "standard": 3, "docx": 7}
    if dict(kinds) != expected_kinds:
        fail(f"unexpected source kinds: {dict(kinds)}")
    for record in records:
        name = record["source"]
        original = DESKTOP / name
        public = VAULT / record["public_path"]
        processed = VAULT / record["processed_path"]
        if not original.is_file() or sha256(original) != record["original_sha256"]:
            fail(f"original hash mismatch: {name}")
        if not public.is_file() or sha256(public) != record["public_sha256"]:
            fail(f"public hash mismatch: {name}")
        manifest_path = processed / "manifest.json"
        extract_path = processed / "extracted-text.md"
        if not manifest_path.is_file() or not extract_path.is_file():
            fail(f"missing processed output: {name}")
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        if manifest["public_sha256"] != record["public_sha256"]:
            fail(f"manifest hash mismatch: {name}")
        if record["kind"] == "lecture":
            sanitation = record["sanitization"]
            if sanitation["original_pages"] - sanitation["public_pages"] != 1:
                fail(f"lecture sanitation mismatch: {name}")
        elif record["original_sha256"] != record["public_sha256"]:
            fail(f"unexpected transformation of non-lecture: {name}")
    source_notes = list((COURSE / "Source Notes").glob("Source - *.md"))
    manifests = list((COURSE / "Processed").glob("*/manifest.json"))
    public_files = list((COURSE / "PDF").glob("*")) + list((COURSE / "Original").glob("*"))
    if (len(source_notes), len(manifests), len(public_files)) != (42, 42, 42):
        fail("source count mismatch")
    return dict(kinds)


def note_index() -> tuple[dict[str, Path], dict[str, list[Path]], dict[Path, dict[str, object]]]:
    by_name: dict[str, list[Path]] = defaultdict(list)
    metadata: dict[Path, dict[str, object]] = {}
    canonical: dict[str, Path] = {}
    for path in VAULT.rglob("*.md"):
        if ".git" in path.parts or ".trash" in path.parts:
            continue
        text = path.read_text(encoding="utf-8")
        data, _ = frontmatter(text) if text.startswith("---\n") else ({}, "")
        if not data:
            continue
        by_name[path.stem].append(path)
        metadata[path] = data
        canonical[path.stem] = path
        aliases = data.get("aliases", [])
        if isinstance(aliases, str):
            aliases = [aliases]
        for alias in aliases:
            canonical[str(alias)] = path
    duplicates = {name: paths for name, paths in by_name.items() if len(paths) > 1}
    if duplicates:
        fail(f"duplicate markdown basenames: {sorted(duplicates)}")
    return canonical, by_name, metadata


def check_vault_integrity() -> dict[str, int]:
    """Validate saved notes across the Vault, not only the course corpus."""
    canonical, _, metadata = note_index()
    optional_properties = {"aliases", "created", "security", "status", "tags", "updated"}
    all_files = [
        path for path in VAULT.rglob("*")
        if path.is_file() and ".git" not in path.parts and ".trash" not in path.parts
    ]
    by_filename = {path.name for path in all_files}
    checked_links = 0

    for path, data in metadata.items():
        relative = path.relative_to(VAULT)
        is_template = relative.parts[0] == "98 Templates"
        note_type = data.get("type")
        if note_type is not None and note_type not in ALLOWED_TYPES:
            fail(f"invalid type in {relative}: {note_type}")
        if not is_template:
            for key in optional_properties:
                if key in data and data[key] in ("", []):
                    fail(f"empty optional property in {relative}: {key}")
            if note_type not in {None, "moc"}:
                areas = data.get("area")
                if not isinstance(areas, list) or not 1 <= len(areas) <= 2:
                    fail(f"missing or invalid area in {relative}")
                if not set(areas) <= ALLOWED_AREAS:
                    fail(f"invalid area value in {relative}: {areas}")
            security = data.get("security")
            if security is not None and (
                not isinstance(security, list)
                or not 1 <= len(security) <= 2
                or not set(security) <= ALLOWED_SECURITY
            ):
                fail(f"invalid security in {relative}: {security}")

        body = path.read_text(encoding="utf-8")
        for raw_target in re.findall(r"\[\[([^]\n]+)\]\]", body):
            target = raw_target.split("|", 1)[0].split("#", 1)[0].strip()
            if not target:
                continue
            checked_links += 1
            if "/" in target:
                candidate = VAULT / target
                candidates = [candidate]
                if not candidate.suffix:
                    candidates.append(candidate.with_suffix(".md"))
                if not any(item.exists() for item in candidates):
                    fail(f"unresolved path link in {relative}: {raw_target}")
            elif target not in canonical and target not in by_filename:
                fail(f"unresolved wikilink in {relative}: {raw_target}")

    return {"vault_notes": len(metadata), "vault_links_checked": checked_links}


def check_notes() -> dict[str, int]:
    expected = load_expected_titles()
    canonical, _, metadata = note_index()
    paths = [path for path in KNOWLEDGE.rglob("*.md") if path.stem in expected]
    if {path.stem for path in paths} != expected or len(paths) != len(expected):
        fail("required cryptography-course note set is incomplete or duplicated")
    moc_texts = [
        path.read_text(encoding="utf-8")
        for path, data in metadata.items()
        if data.get("type") == "moc"
    ]
    math_count = 0
    diagram_count = 0
    seminar_refs: set[str] = set()
    for path in paths:
        text = path.read_text(encoding="utf-8")
        data, body = frontmatter(text)
        note_type = data.get("type")
        if note_type not in ALLOWED_TYPES:
            fail(f"invalid type in {path}")
        areas = data.get("area")
        if not isinstance(areas, list) or not 1 <= len(areas) <= 2 or not set(areas) <= ALLOWED_AREAS:
            fail(f"invalid area in {path}")
        security = data.get("security")
        if security is not None and (
            not isinstance(security, list) or not 1 <= len(security) <= 2 or not set(security) <= ALLOWED_SECURITY
        ):
            fail(f"invalid security in {path}")
        aliases = data.get("aliases")
        if not isinstance(aliases, list) or not aliases:
            fail(f"missing aliases in {path}")
        if data.get("status") not in {"learning", "review", "stable"}:
            fail(f"missing learning status in {path}")
        headings = set(re.findall(r"(?m)^## (.+)$", body))
        if not REQUIRED_SECTIONS <= headings:
            fail(f"missing study section in {path}: {sorted(REQUIRED_SECTIONS-headings)}")
        if "[[Source - " not in body:
            fail(f"missing course source in {path}")
        if not any(f"[[{path.stem}" in moc for moc in moc_texts):
            fail(f"note is not linked from a MOC: {path}")
        math_count += int("$$" in body)
        diagram_count += int("```mermaid" in body)
        seminar_refs.update(re.findall(r"\[\[Source - (Семинар \d{2})\]\]", body))
        for raw_target in re.findall(r"\[\[([^]]+)\]\]", body):
            target = raw_target.split("|", 1)[0].split("#", 1)[0]
            if "/" in target:
                candidate = VAULT / target
                candidates = [candidate]
                if not candidate.suffix:
                    candidates.append(candidate.with_suffix(".md"))
                if not any(item.exists() for item in candidates):
                    fail(f"unresolved path link in {path}: {raw_target}")
            elif target not in canonical:
                fail(f"unresolved wikilink in {path}: {raw_target}")
    if math_count < 30 or diagram_count < 8:
        fail(f"study-aid regression: math={math_count}, diagrams={diagram_count}")
    if seminar_refs != {f"Семинар {number:02d}" for number in range(1, 12)}:
        fail(f"seminar coverage mismatch: {sorted(seminar_refs)}")
    return {
        "required_cryptography_notes": len(paths),
        "notes_with_math": math_count,
        "notes_with_diagrams": diagram_count,
        "seminars_linked": len(seminar_refs),
    }


def check_localized_course_names() -> dict[str, int]:
    builder = VAULT / "scripts" / "knowledge" / "build_crypto_steganography_knowledge.py"
    title_map = runpy.run_path(builder)["TITLE_MAP"]
    canonical, by_name, metadata = note_index()
    for english, russian in title_map.items():
        path = canonical.get(russian)
        if path is None or path.stem != russian:
            fail(f"missing localized course note: {russian}")
        if english != russian:
            aliases = metadata[path].get("aliases", [])
            if not isinstance(aliases, list) or english not in aliases:
                fail(f"missing English alias in localized course note: {russian}")
            if english in by_name:
                fail(f"obsolete English basename remains: {english}")
    return {"localized_course_notes": len(title_map)}


def main() -> int:
    source_stats = check_sources()
    visual_stats = check_course_visuals()
    vault_stats = check_vault_integrity()
    note_stats = check_notes()
    localized_stats = check_localized_course_names()
    summary = {
        **source_stats, **visual_stats, **vault_stats, **note_stats,
        **localized_stats, "result": "ok",
    }
    print(json.dumps(summary, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except RuntimeError as error:
        print(f"audit=failed: {error}", file=sys.stderr)
        raise SystemExit(1)
