#!/usr/bin/env python3
"""Extract DOCX text and structure locally without modifying the source."""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import re
import sys
import uuid
import zipfile
from pathlib import Path
from typing import Any
from xml.etree import ElementTree as ET

from docx import Document


DEFAULT_OUTPUT_ROOT = Path("07 Sources/Courses/Processed")
WORD_NAMESPACE = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
MATH_NAMESPACE = "http://schemas.openxmlformats.org/officeDocument/2006/math"
TEXT_TAGS = {
    f"{{{WORD_NAMESPACE}}}t",
    f"{{{MATH_NAMESPACE}}}t",
    f"{{{WORD_NAMESPACE}}}instrText",
    f"{{{WORD_NAMESPACE}}}delText",
}
PARAGRAPH_TAG = f"{{{WORD_NAMESPACE}}}p"
TABLE_TAG = f"{{{WORD_NAMESPACE}}}tbl"
ROW_TAG = f"{{{WORD_NAMESPACE}}}tr"
CELL_TAG = f"{{{WORD_NAMESPACE}}}tc"


class InspectionError(RuntimeError):
    """A user-facing inspection failure."""


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Extract DOCX paragraphs, tables, equations, headers, footers, "
            "notes, comments, images, and metadata locally."
        )
    )
    parser.add_argument("source", type=Path, help="Path to a DOCX source")
    parser.add_argument(
        "--output-root",
        type=Path,
        default=DEFAULT_OUTPUT_ROOT,
        help=f"Root for technical results (default: {DEFAULT_OUTPUT_ROOT})",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Replace only manifest.json and extracted-text.md",
    )
    return parser.parse_args(argv)


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def safe_result_name(stem: str) -> str:
    name = re.sub(r"[\x00-\x1f\x7f]", "", stem)
    name = re.sub(r"[/\\:]+", " - ", name)
    name = re.sub(r"\s+", " ", name).strip(" .")
    return (name or "document")[:180]


def json_value(value: Any) -> Any:
    if isinstance(value, (dt.date, dt.datetime)):
        return value.isoformat()
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    return str(value)


def clean_metadata(values: dict[str, Any]) -> dict[str, Any]:
    return {
        key: json_value(value)
        for key, value in values.items()
        if value not in (None, "")
    }


def element_text(element: ET.Element) -> str:
    parts: list[str] = []
    for node in element.iter():
        if node.tag in TEXT_TAGS and node.text:
            parts.append(node.text)
        elif node.tag == f"{{{WORD_NAMESPACE}}}tab":
            parts.append("\t")
        elif node.tag in {
            f"{{{WORD_NAMESPACE}}}br",
            f"{{{WORD_NAMESPACE}}}cr",
        }:
            parts.append("\n")
    text = "".join(parts)
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def paragraphs_from_xml(payload: bytes) -> list[str]:
    root = ET.fromstring(payload)
    paragraphs: list[str] = []
    for element in root.iter(PARAGRAPH_TAG):
        text = element_text(element)
        if text:
            paragraphs.append(text)
    return paragraphs


def tables_from_xml(payload: bytes) -> list[list[list[str]]]:
    root = ET.fromstring(payload)
    tables: list[list[list[str]]] = []
    for table in root.iter(TABLE_TAG):
        rows: list[list[str]] = []
        for row in table.findall(f"./{{{WORD_NAMESPACE}}}tr"):
            cells = [element_text(cell) for cell in row.findall(f"./{{{WORD_NAMESPACE}}}tc")]
            if any(cells):
                rows.append(cells)
        if rows:
            tables.append(rows)
    return tables


def equation_count(payload: bytes) -> int:
    root = ET.fromstring(payload)
    math_tags = {
        f"{{{MATH_NAMESPACE}}}oMath",
        f"{{{MATH_NAMESPACE}}}oMathPara",
    }
    return sum(1 for element in root.iter() if element.tag in math_tags)


def inspect_docx(source: Path) -> tuple[dict[str, Any], str]:
    try:
        document = Document(str(source))
    except Exception as exc:
        raise InspectionError(f"python-docx could not open {source.name}: {exc}") from exc

    core = document.core_properties
    metadata = clean_metadata(
        {
            "title": core.title,
            "author": core.author,
            "subject": core.subject,
            "keywords": core.keywords,
            "category": core.category,
            "comments": core.comments,
            "created": core.created,
            "modified": core.modified,
            "last_modified_by": core.last_modified_by,
            "revision": core.revision,
            "language": core.language,
            "version": core.version,
        }
    )

    with zipfile.ZipFile(source) as archive:
        names = set(archive.namelist())
        main_payload = archive.read("word/document.xml")
        main_paragraphs = paragraphs_from_xml(main_payload)
        tables = tables_from_xml(main_payload)
        equations = equation_count(main_payload)

        related_parts: dict[str, list[str]] = {}
        for label, prefix in (
            ("Headers", "word/header"),
            ("Footers", "word/footer"),
            ("Footnotes", "word/footnotes.xml"),
            ("Endnotes", "word/endnotes.xml"),
            ("Comments", "word/comments.xml"),
        ):
            part_names = sorted(
                name
                for name in names
                if name.startswith(prefix) and name.endswith(".xml")
            )
            values: list[str] = []
            for part_name in part_names:
                values.extend(paragraphs_from_xml(archive.read(part_name)))
            if values:
                related_parts[label] = values

        media = sorted(
            name.removeprefix("word/media/")
            for name in names
            if name.startswith("word/media/") and not name.endswith("/")
        )

    lines = [f"# {source.stem}", "", "## Main document", ""]
    for number, paragraph in enumerate(main_paragraphs, start=1):
        lines.extend([f"<!-- paragraph:{number} -->", paragraph, ""])

    if tables:
        lines.extend(["## Tables", ""])
        for table_number, table in enumerate(tables, start=1):
            lines.extend([f"### Table {table_number}", ""])
            for row_number, row in enumerate(table, start=1):
                lines.append(f"- Row {row_number}: " + " | ".join(row))
            lines.append("")

    for label, values in related_parts.items():
        lines.extend([f"## {label}", ""])
        for number, value in enumerate(values, start=1):
            lines.append(f"- {number}: {value}")
        lines.append("")

    if media:
        lines.extend(["## Embedded media", ""])
        lines.extend(f"- {name}" for name in media)
        lines.append("")

    manifest = {
        "source": source.name,
        "format": "docx",
        "backend": "python-docx and OOXML",
        "paragraphs": len(main_paragraphs),
        "tables": len(tables),
        "equations": equations,
        "embedded_media": len(media),
        "related_parts": {key: len(value) for key, value in related_parts.items()},
        "metadata": metadata,
        "sha256": file_sha256(source),
        "generated_at": dt.datetime.now(dt.timezone.utc).isoformat(),
    }
    return manifest, "\n".join(lines).rstrip() + "\n"


def atomic_write(path: Path, content: str) -> None:
    temporary = path.with_name(f".{path.name}.{uuid.uuid4().hex}.tmp")
    try:
        temporary.write_text(content, encoding="utf-8")
        os.replace(temporary, path)
    finally:
        if temporary.exists():
            temporary.unlink()


def write_results(
    output_directory: Path,
    manifest: dict[str, Any],
    extracted_text: str,
    overwrite: bool,
) -> None:
    manifest_path = output_directory / "manifest.json"
    text_path = output_directory / "extracted-text.md"
    existing = [path.name for path in (manifest_path, text_path) if path.exists()]
    if existing and not overwrite:
        raise InspectionError(
            f"Result already exists in {output_directory}: {', '.join(existing)}. "
            "Use --overwrite to replace only generated files."
        )
    output_directory.mkdir(parents=True, exist_ok=True)
    atomic_write(manifest_path, json.dumps(manifest, ensure_ascii=False, indent=2) + "\n")
    atomic_write(text_path, extracted_text)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    source = args.source.expanduser()
    if not source.is_file() or source.suffix.lower() != ".docx":
        print(f"error: expected an existing DOCX file: {source}", file=sys.stderr)
        return 2
    try:
        source = source.resolve(strict=True)
        manifest, extracted_text = inspect_docx(source)
        output_directory = args.output_root.expanduser() / safe_result_name(source.stem)
        write_results(output_directory, manifest, extracted_text, args.overwrite)
    except (InspectionError, OSError, zipfile.BadZipFile, ET.ParseError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 3
    print(f"Inspected {source.name}. Result: {output_directory}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
