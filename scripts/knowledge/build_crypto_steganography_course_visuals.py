#!/usr/bin/env python3
"""Build 24 curated course visuals from sanitized public PDFs."""

from __future__ import annotations

import argparse
import hashlib
import json
from dataclasses import dataclass
from pathlib import Path

import pymupdf


COURSE = "Основы криптографии и стеганографии"
PDF_ROOT = Path("07 Sources/Courses") / COURSE / "PDF"
OUTPUT_ROOT = Path("90 Attachments/Courses") / COURSE
COMMON_CROP = (0.035, 0.14, 0.965, 0.94)


@dataclass(frozen=True)
class Visual:
    filename: str
    category: str
    lecture: int
    page: int
    targets: tuple[str, ...]
    crop: tuple[float, float, float, float] = COMMON_CROP


VISUALS = (
    Visual("OCS - Polybius Square - L03 p03.png", "classical", 3, 3, ("Polybius Square",)),
    Visual("OCS - Affine Cipher - L03 p06.png", "classical", 3, 6, ("Affine Cipher",)),
    Visual("OCS - Cardan Grille - L04 p03.png", "classical", 4, 3, ("Cardan Grille Cipher",)),
    Visual("OCS - Playfair Cipher - L05 p02.png", "classical", 5, 2, ("Playfair Cipher",)),
    Visual("OCS - Hill Cipher - L05 p05.png", "classical", 5, 5, ("Hill Cipher",)),
    Visual("OCS - RGB Model - L09 p12.png", "images", 9, 12, ("Image Color Models",)),
    Visual("OCS - YCbCr Model - L09 p15.png", "images", 9, 15, ("Image Color Models",)),
    Visual("OCS - DCT Basis - L11 p28.png", "images", 11, 28, ("Discrete Fourier and Cosine Transforms for Images",)),
    Visual("OCS - JPEG Pipeline - L12 p09.png", "images", 12, 9, ("JPEG Compression",)),
    Visual("OCS - LSB Embedding - L10 p03.png", "embedding", 10, 3, ("LSB Steganography",)),
    Visual("OCS - PM1 Embedding - L10 p05.png", "embedding", 10, 5, ("Plus-Minus One Steganography",)),
    Visual("OCS - QIM Embedding - L10 p07.png", "embedding", 10, 7, ("Quantization Index Modulation",)),
    Visual("OCS - PVD Embedding - L10 p10.png", "embedding", 10, 10, ("Pixel Value Differencing",)),
    Visual("OCS - NMI Embedding - L10 p13.png", "embedding", 10, 13, ("Neighbor Mean Interpolation",)),
    Visual("OCS - Koch Zhao - L13 p06.png", "embedding", 13, 6, ("Koch-Zhao Method",)),
    Visual("OCS - JSteg - L13 p11.png", "embedding", 13, 11, ("JSteg",)),
    Visual("OCS - F3 F4 - L13 p14.png", "embedding", 13, 14, ("F3 and F4 JPEG Steganography",)),
    Visual("OCS - F5 - L13 p15.png", "embedding", 13, 15, ("F5 JPEG Steganography",)),
    Visual("OCS - Bit Planes - L14 p05.png", "steganalysis", 14, 5, ("Visual Steganalysis and Bit-Plane Analysis",)),
    Visual("OCS - DCT Histogram - L14 p08.png", "steganalysis", 14, 8, ("Visual Steganalysis and Bit-Plane Analysis",)),
    Visual("OCS - Pairs of Values - L14 p12.png", "steganalysis", 14, 12, ("Statistical Steganalysis",)),
    Visual("OCS - Classification Pipeline - L14 p14.png", "steganalysis", 14, 14, ("Machine Learning for Steganalysis",)),
    Visual("OCS - GNCNN - L14 p26.png", "steganalysis", 14, 26, ("Neural Network Steganalysis",)),
    Visual("OCS - PNet - L14 p28.png", "steganalysis", 14, 28, ("Neural Network Steganalysis",)),
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--overwrite", action="store_true")
    return parser.parse_args()


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def public_pdf(lecture: int) -> Path:
    return PDF_ROOT / f"{COURSE} - Лекция {lecture:02d}.pdf"


def main() -> int:
    args = parse_args()
    if len(VISUALS) != 24 or len({visual.filename for visual in VISUALS}) != 24:
        raise RuntimeError("The curated visual set must contain 24 unique files")
    category_counts = {
        category: sum(visual.category == category for visual in VISUALS)
        for category in {visual.category for visual in VISUALS}
    }
    if category_counts != {"classical": 5, "images": 4, "embedding": 9, "steganalysis": 6}:
        raise RuntimeError(f"Unexpected visual category counts: {category_counts}")
    existing = [OUTPUT_ROOT / visual.filename for visual in VISUALS]
    existing.append(OUTPUT_ROOT / "visual-manifest.json")
    if not args.overwrite and any(path.exists() for path in existing):
        raise RuntimeError("Visual output already exists; use --overwrite")

    OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)
    records: list[dict[str, object]] = []
    documents: dict[int, pymupdf.Document] = {}
    try:
        for visual in VISUALS:
            pdf = public_pdf(visual.lecture)
            document = documents.setdefault(visual.lecture, pymupdf.open(pdf))
            if not 1 <= visual.page <= document.page_count:
                raise RuntimeError(f"Page out of range: {pdf}, page {visual.page}")
            page = document[visual.page - 1]
            x0, y0, x1, y1 = visual.crop
            rect = pymupdf.Rect(
                page.rect.x0 + page.rect.width * x0,
                page.rect.y0 + page.rect.height * y0,
                page.rect.x0 + page.rect.width * x1,
                page.rect.y0 + page.rect.height * y1,
            )
            pixmap = page.get_pixmap(matrix=pymupdf.Matrix(2.2, 2.2), clip=rect, alpha=False)
            output = OUTPUT_ROOT / visual.filename
            pixmap.save(output)
            records.append(
                {
                    "filename": visual.filename,
                    "category": visual.category,
                    "source_pdf": pdf.as_posix(),
                    "source_pdf_sha256": sha256(pdf),
                    "source_note": f"Source - {COURSE} - Лекция {visual.lecture:02d}",
                    "page": visual.page,
                    "crop_normalized": list(visual.crop),
                    "crop_points": [round(value, 3) for value in (rect.x0, rect.y0, rect.x1, rect.y1)],
                    "target_notes": list(visual.targets),
                    "width": pixmap.width,
                    "height": pixmap.height,
                    "bytes": output.stat().st_size,
                    "sha256": sha256(output),
                }
            )
    finally:
        for document in documents.values():
            document.close()

    manifest = {
        "course": COURSE,
        "count": len(records),
        "category_counts": category_counts,
        "render_scale": 2.2,
        "visuals": records,
    }
    (OUTPUT_ROOT / "visual-manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps({"count": len(records), "categories": category_counts}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
