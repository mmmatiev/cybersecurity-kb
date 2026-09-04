#!/usr/bin/env python3
"""Import the public-safe Foundations of Cryptography and Steganography course."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

import pymupdf


COURSE_NAME = "Основы криптографии и стеганографии"
SOURCE_PATTERN = re.compile(r"^2024_Лекция (\d{2})\.pdf$")
EXPECTED_LECTURES = tuple(range(1, 15))
EMAIL_RE = re.compile(r"[\w.+-]+@[\w.-]+\.[A-Za-zА-Яа-я]{2,}")
PHONE_RE = re.compile(
    r"(?<!\d)(?:\+?7|8)[\s()\-]{0,3}\d{3}[\s()\-]{0,3}"
    r"\d{3}[\s\-]{0,2}\d{2}[\s\-]{0,2}\d{2}(?!\d)"
)
CONTACT_SCHEMES = ("mailto:", "tel:")
SAFE_METADATA_KEYS = {
    "title",
    "author",
    "subject",
    "keywords",
    "creator",
    "producer",
    "creationDate",
    "modDate",
    "trapped",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source_root", type=Path)
    parser.add_argument(
        "--target-root",
        type=Path,
        default=Path("07 Sources/Courses") / COURSE_NAME,
    )
    parser.add_argument("--overwrite", action="store_true")
    return parser.parse_args()


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def has_contact(value: str) -> bool:
    return bool(EMAIL_RE.search(value) or PHONE_RE.search(value))


def discover_sources(source_root: Path) -> list[tuple[int, Path]]:
    discovered: dict[int, Path] = {}
    unexpected: list[str] = []
    for path in sorted(source_root.iterdir()):
        if not path.is_file() or path.name == ".DS_Store":
            continue
        match = SOURCE_PATTERN.fullmatch(path.name)
        if not match:
            unexpected.append(path.name)
            continue
        number = int(match.group(1))
        discovered[number] = path
    if unexpected:
        raise RuntimeError(f"Unexpected course files: {unexpected}")
    if tuple(sorted(discovered)) != EXPECTED_LECTURES:
        raise RuntimeError(
            f"Expected lectures 01-14, found: {sorted(discovered)}"
        )
    return sorted(discovered.items())


def public_name(number: int) -> str:
    return f"{COURSE_NAME} - Лекция {number:02d}.pdf"


def redact_contact_lines(page: pymupdf.Page) -> int:
    redactions = 0
    text = page.get_text("dict")
    for block in text.get("blocks", []):
        for line in block.get("lines", []):
            line_text = "".join(span.get("text", "") for span in line.get("spans", []))
            if not has_contact(line_text):
                continue
            rect = pymupdf.Rect(line["bbox"])
            rect.x0 = max(page.rect.x0, rect.x0 - 2)
            rect.y0 = max(page.rect.y0, rect.y0 - 1)
            rect.x1 = min(page.rect.x1, rect.x1 + 2)
            rect.y1 = min(page.rect.y1, rect.y1 + 1)
            page.add_redact_annot(rect, fill=(1, 1, 1))
            redactions += 1
    if redactions:
        page.apply_redactions(images=pymupdf.PDF_REDACT_IMAGE_NONE)
    return redactions


def remove_contact_links(page: pymupdf.Page) -> int:
    removed = 0
    for link in list(page.get_links()):
        uri = str(link.get("uri", ""))
        if uri.lower().startswith(CONTACT_SCHEMES) or has_contact(uri):
            page.delete_link(link)
            removed += 1
    return removed


def safe_metadata(metadata: dict[str, str]) -> dict[str, str]:
    result: dict[str, str] = {}
    for key in SAFE_METADATA_KEYS:
        value = str(metadata.get(key, "") or "").strip()
        if value and not has_contact(value):
            result[key] = value
    return result


def sanitize_pdf(source: Path, target: Path, number: int) -> dict[str, object]:
    document = pymupdf.open(source)
    try:
        original_pages = document.page_count
        expected_last = {
            1: 20,
            2: 13,
            3: 11,
            4: 7,
            5: 9,
            6: 12,
            7: 8,
            8: 19,
            9: 22,
            10: 16,
            11: 55,
            12: 19,
            13: 16,
            14: 29,
        }[number]
        if original_pages != expected_last:
            raise RuntimeError(
                f"Unexpected page count for {source.name}: {original_pages}; "
                f"expected {expected_last}"
            )

        redacted_pages: list[int] = []
        redaction_count = 0
        removed_links = 0
        if number == 1:
            for page_number in (3, 4):
                page = document[page_number - 1]
                count = redact_contact_lines(page)
                if count == 0:
                    raise RuntimeError(
                        f"No contact text found for required redaction on page {page_number}"
                    )
                redaction_count += count
                removed_links += remove_contact_links(page)
                redacted_pages.append(page_number)

        document.delete_page(document.page_count - 1)
        for page in document:
            removed_links += remove_contact_links(page)
            if has_contact(page.get_text("text")):
                raise RuntimeError(
                    f"Contact-shaped text remains in {source.name}, page {page.number + 1}"
                )

        document.set_metadata(safe_metadata(document.metadata or {}))
        target.parent.mkdir(parents=True, exist_ok=True)
        temporary = target.with_suffix(".pdf.tmp")
        if temporary.exists():
            temporary.unlink()
        document.save(
            temporary,
            garbage=4,
            deflate=True,
            clean=True,
            encryption=pymupdf.PDF_ENCRYPT_KEEP,
        )
        temporary.replace(target)
    finally:
        document.close()

    return {
        "original_pages": original_pages,
        "public_pages": original_pages - 1,
        "redacted_pages": redacted_pages,
        "removed_pages": [original_pages],
        "redaction_count": redaction_count,
        "removed_contact_links": removed_links,
        "page_mapping": [
            {"public_page": page, "original_page": page}
            for page in range(1, original_pages)
        ],
    }


def run_inspector(source: Path, output_root: Path, overwrite: bool) -> Path:
    inspector = Path(__file__).resolve().parents[1] / "slides" / "inspect_slides.py"
    command = [sys.executable, str(inspector), str(source), "--output-root", str(output_root)]
    if overwrite:
        command.append("--overwrite")
    subprocess.run(command, check=True)
    return output_root / source.stem / "manifest.json"


def update_manifest(
    manifest_path: Path,
    *,
    source: Path,
    public: Path,
    number: int,
    sanitization: dict[str, object],
) -> dict[str, object]:
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest.update(
        {
            "course": COURSE_NAME,
            "kind": "lecture",
            "lecture": number,
            "original_filename": source.name,
            "public_filename": public.name,
            "original_sha256": sha256(source),
            "public_sha256": sha256(public),
            "original_bytes": source.stat().st_size,
            "public_bytes": public.stat().st_size,
            "sanitization": sanitization,
        }
    )
    manifest_path.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return manifest


def main() -> int:
    args = parse_args()
    source_root = args.source_root.expanduser().resolve(strict=True)
    target_root = args.target_root.expanduser()
    pdf_root = target_root / "PDF"
    processed_root = target_root / "Processed"
    sources = discover_sources(source_root)

    records: list[dict[str, object]] = []
    for number, source in sources:
        public = pdf_root / public_name(number)
        result_root = processed_root / public.stem
        if (public.exists() or result_root.exists()) and not args.overwrite:
            raise RuntimeError(
                f"Target exists for lecture {number:02d}; use --overwrite"
            )
        sanitization = sanitize_pdf(source, public, number)
        manifest_path = run_inspector(public, processed_root, args.overwrite)
        manifest = update_manifest(
            manifest_path,
            source=source,
            public=public,
            number=number,
            sanitization=sanitization,
        )
        records.append(
            {
                "lecture": number,
                "original_filename": source.name,
                "public_filename": public.name,
                "public_path": str(public),
                "processed_path": str(result_root),
                "original_sha256": manifest["original_sha256"],
                "public_sha256": manifest["public_sha256"],
                "sanitization": sanitization,
            }
        )

    index = {
        "course": COURSE_NAME,
        "source_directory_name": source_root.name,
        "counts": {"lecture": len(records)},
        "original_pages": sum(
            int(record["sanitization"]["original_pages"]) for record in records
        ),
        "public_pages": sum(
            int(record["sanitization"]["public_pages"]) for record in records
        ),
        "files": records,
    }
    target_root.mkdir(parents=True, exist_ok=True)
    (target_root / "source-index.json").write_text(
        json.dumps(index, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(
        json.dumps(
            {
                "course": COURSE_NAME,
                "files": len(records),
                "original_pages": index["original_pages"],
                "public_pages": index["public_pages"],
            },
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
