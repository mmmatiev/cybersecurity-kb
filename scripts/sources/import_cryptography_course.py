#!/usr/bin/env python3
"""Import the approved cryptography course corpus into its public Vault area."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

from pypdf import PdfReader, PdfWriter


COURSE_NAME = "Криптографические методы защиты информации"
LECTURE_PATTERN = re.compile(r"^2024_Лекция .+\.pdf$")
EXPECTED_COUNTS = {"lecture": 21, "seminar": 11, "standard": 3, "docx": 7}


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


def classify(path: Path) -> str:
    if LECTURE_PATTERN.match(path.name):
        return "lecture"
    if path.name.startswith("Семинар ") and path.suffix.lower() == ".pdf":
        return "seminar"
    if path.name.startswith("ГОСТ Р ") and path.suffix.lower() == ".pdf":
        return "standard"
    if path.name.startswith("Тема №") and path.suffix.lower() == ".docx":
        return "docx"
    raise RuntimeError(f"Unexpected course file: {path.name}")


def public_pdf(source: Path, target: Path, remove_last_page: bool) -> tuple[int, int]:
    reader = PdfReader(str(source))
    original_pages = len(reader.pages)
    target.parent.mkdir(parents=True, exist_ok=True)
    if not remove_last_page:
        shutil.copy2(source, target)
        return original_pages, original_pages
    if remove_last_page and original_pages < 2:
        raise RuntimeError(f"Cannot remove the only page from {source.name}")
    selected = reader.pages[:-1]
    writer = PdfWriter()
    for page in selected:
        writer.add_page(page)
    if reader.metadata:
        safe_metadata = {
            str(key): str(value)
            for key, value in reader.metadata.items()
            if value not in (None, "")
            and "@" not in str(value)
            and not re.search(r"(?:\+?7|8)[\s()\-]*\d{3}", str(value))
        }
        writer.add_metadata(safe_metadata)
    with target.open("wb") as stream:
        writer.write(stream)
    return original_pages, len(selected)


def run_inspector(script: Path, source: Path, output_root: Path, overwrite: bool) -> None:
    command = [sys.executable, str(script), str(source), "--output-root", str(output_root)]
    if overwrite:
        command.append("--overwrite")
    subprocess.run(command, check=True)


def update_manifest(
    manifest_path: Path,
    *,
    original: Path,
    public: Path,
    kind: str,
    original_pages: int | None,
    public_pages: int | None,
) -> dict[str, object]:
    data = json.loads(manifest_path.read_text(encoding="utf-8"))
    data.update(
        {
            "course": COURSE_NAME,
            "kind": kind,
            "original_filename": original.name,
            "public_filename": public.name,
            "original_sha256": sha256(original),
            "public_sha256": sha256(public),
            "original_bytes": original.stat().st_size,
            "public_bytes": public.stat().st_size,
            "sanitization": (
                {
                    "action": "removed final contact page",
                    "removed_page": original_pages,
                    "original_pages": original_pages,
                    "public_pages": public_pages,
                }
                if kind == "lecture"
                else {"action": "none; byte-for-byte public copy"}
            ),
        }
    )
    manifest_path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return data


def main() -> int:
    args = parse_args()
    source_root = args.source_root.expanduser().resolve(strict=True)
    target_root = args.target_root.expanduser()
    pdf_root = target_root / "PDF"
    original_root = target_root / "Original"
    processed_root = target_root / "Processed"
    scripts_root = Path(__file__).resolve().parents[1]
    pdf_inspector = scripts_root / "slides" / "inspect_slides.py"
    docx_inspector = Path(__file__).resolve().with_name("inspect_docx.py")

    sources = sorted(path for path in source_root.iterdir() if path.is_file())
    counts = {key: 0 for key in EXPECTED_COUNTS}
    records: list[dict[str, object]] = []
    for source in sources:
        kind = classify(source)
        counts[kind] += 1
        public = (original_root if kind == "docx" else pdf_root) / source.name
        if public.exists() and not args.overwrite:
            raise RuntimeError(f"Target already exists: {public}; use --overwrite")

        original_pages: int | None = None
        public_pages: int | None = None
        if source.suffix.lower() == ".pdf":
            original_pages, public_pages = public_pdf(
                source, public, remove_last_page=kind == "lecture"
            )
            run_inspector(pdf_inspector, public, processed_root, args.overwrite)
        else:
            public.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, public)
            run_inspector(docx_inspector, public, processed_root, args.overwrite)

        result_directory = processed_root / source.stem
        manifest = update_manifest(
            result_directory / "manifest.json",
            original=source,
            public=public,
            kind=kind,
            original_pages=original_pages,
            public_pages=public_pages,
        )
        records.append(
            {
                "source": source.name,
                "kind": kind,
                "public_path": str(public),
                "processed_path": str(result_directory),
                "original_sha256": manifest["original_sha256"],
                "public_sha256": manifest["public_sha256"],
                "sanitization": manifest["sanitization"],
            }
        )

    if counts != EXPECTED_COUNTS:
        raise RuntimeError(f"Unexpected corpus counts: {counts}; expected {EXPECTED_COUNTS}")

    index = {
        "course": COURSE_NAME,
        "source_root": str(source_root),
        "counts": counts,
        "files": records,
    }
    target_root.mkdir(parents=True, exist_ok=True)
    (target_root / "source-index.json").write_text(
        json.dumps(index, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"Imported {len(records)} course files into {target_root}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
