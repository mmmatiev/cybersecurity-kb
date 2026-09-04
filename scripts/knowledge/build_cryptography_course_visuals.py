#!/usr/bin/env python3
"""Build a curated, reproducible set of course visuals for Obsidian notes."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import tempfile
import zipfile
from pathlib import Path


VAULT = Path(__file__).resolve().parents[2]
COURSE_NAME = "Криптографические методы защиты информации"
COURSE = VAULT / "07 Sources" / "Courses" / COURSE_NAME
OUTPUT = VAULT / "90 Attachments" / "Cryptography" / "Course Visuals"
MANIFEST = OUTPUT / "course-visuals-manifest.json"

# Crop away the slide chrome while retaining the title and all teaching content.
SLIDE_CROP = (0.035, 0.155, 0.965, 0.945)

PDF_VISUALS = [
    {
        "source": "2024_Лекция 08.pdf",
        "page": 5,
        "output": "ECC - Point Addition - Lecture 08 p05.png",
        "target_note": "01 Knowledge/Cryptography/Elliptic Curves.md",
        "source_note": "Source - 2024_Лекция 08",
    },
    {
        "source": "2024_Лекция 16.pdf",
        "page": 6,
        "output": "AES - Round Transformations - Lecture 16 p06.png",
        "target_note": "01 Knowledge/Cryptography/Advanced Encryption Standard.md",
        "source_note": "Source - 2024_Лекция 16",
    },
    {
        "source": "2024_Лекция 16.pdf",
        "page": 3,
        "output": "DES - Feistel Round - Lecture 16 p03.png",
        "target_note": "01 Knowledge/Cryptography/DES and Triple DES.md",
        "source_note": "Source - 2024_Лекция 16",
    },
    {
        "source": "2024_Лекция 17-18.pdf",
        "page": 7,
        "output": "Diffie-Hellman - Key Agreement - Lecture 17-18 p07.png",
        "target_note": "01 Knowledge/Cryptography/Diffie-Hellman Key Exchange.md",
        "source_note": "Source - 2024_Лекция 17-18",
    },
    {
        "source": "2024_Лекция 17-18.pdf",
        "page": 8,
        "output": "MITM - Diffie-Hellman - Lecture 17-18 p08.png",
        "target_note": "01 Knowledge/Cybersecurity/Network Security/Man-in-the-Middle Attack.md",
        "source_note": "Source - 2024_Лекция 17-18",
    },
    {
        "source": "2024_Лекция 20.pdf",
        "page": 4,
        "output": "MAC - Integrity and Authenticity - Lecture 20 p04.png",
        "target_note": "01 Knowledge/Cryptography/Message Authentication Codes.md",
        "source_note": "Source - 2024_Лекция 20",
    },
    {
        "source": "2024_Лекция 20.pdf",
        "page": 13,
        "output": "Digital Signatures - RSA Flow - Lecture 20 p13.png",
        "target_note": "01 Knowledge/Cryptography/Digital Signatures.md",
        "source_note": "Source - 2024_Лекция 20",
    },
    {
        "source": "2024_Лекция 22.pdf",
        "page": 6,
        "output": "PKI - Certification Authority - Lecture 22 p06.png",
        "target_note": "01 Knowledge/Cryptography/Public Key Infrastructure and X.509.md",
        "source_note": "Source - 2024_Лекция 22",
    },
    {
        "source": "2024_Лекция 22.pdf",
        "page": 8,
        "output": "PKI - Certificate Chain - Lecture 22 p08.png",
        "target_note": "01 Knowledge/Cryptography/Public Key Infrastructure and X.509.md",
        "source_note": "Source - 2024_Лекция 22",
    },
    {
        "source": "2024_Лекция 23.pdf",
        "page": 12,
        "output": "QKD - General Flow - Lecture 23 p12.png",
        "target_note": "01 Knowledge/Cryptography/Quantum Key Distribution.md",
        "source_note": "Source - 2024_Лекция 23",
    },
    {
        "source": "2024_Лекция 23.pdf",
        "page": 18,
        "output": "BB84 - Protocol Flow - Lecture 23 p18.png",
        "target_note": "01 Knowledge/Cryptography/BB84.md",
        "source_note": "Source - 2024_Лекция 23",
    },
]

DOCX_VISUALS = [
    {
        "source": "Тема №2 Блокчейн(1).docx",
        "media": "image2.png",
        "paragraphs": "68–69",
        "output": "Blockchain - Merkle Proof - Topic 2 p068-069.png",
        "target_note": "01 Knowledge/Computer Science/Blockchain Cryptography.md",
        "source_note": "Source - Тема №2 Блокчейн(1)",
    },
    {
        "source": "Тема №2 Блокчейн(1).docx",
        "media": "image3.png",
        "paragraphs": "131–132",
        "output": "Blockchain Attacks - Competing Chains - Topic 2 p131-132.png",
        "target_note": "01 Knowledge/Cybersecurity/Security Engineering/Blockchain Attacks.md",
        "source_note": "Source - Тема №2 Блокчейн(1)",
    },
    {
        "source": "Тема №3 Алгоритмы(1).docx",
        "media": "image4.png",
        "paragraphs": "97–98",
        "output": "Block Cipher Design - Feistel Network - Topic 3 p097-098.png",
        "target_note": "01 Knowledge/Cryptography/Block Cipher Design.md",
        "source_note": "Source - Тема №3 Алгоритмы(1)",
    },
    {
        "source": "Тема №3 Алгоритмы(1).docx",
        "media": "image5.png",
        "paragraphs": "97–99",
        "output": "Block Cipher Design - SP Network - Topic 3 p097-099.png",
        "target_note": "01 Knowledge/Cryptography/Block Cipher Design.md",
        "source_note": "Source - Тема №3 Алгоритмы(1)",
    },
    {
        "source": "Тема №3 Алгоритмы(1).docx",
        "media": "image6.png",
        "paragraphs": "158–159",
        "output": "GCM - Authenticated Encryption Layout - Topic 3 p158-159.png",
        "target_note": "01 Knowledge/Cryptography/Block Cipher Modes.md",
        "source_note": "Source - Тема №3 Алгоритмы(1)",
    },
    {
        "source": "Тема №3 Алгоритмы(1).docx",
        "media": "image10.png",
        "paragraphs": "193–194",
        "output": "Hash Functions - Merkle-Damgard Construction - Topic 3 p193-194.png",
        "target_note": "01 Knowledge/Cryptography/Cryptographic Hash Functions.md",
        "source_note": "Source - Тема №3 Алгоритмы(1)",
    },
    {
        "source": "Тема №4 ГСЧ(1).docx",
        "media": "image8.png",
        "paragraphs": "122–124",
        "output": "RNG - Quantum Entropy Pipeline - Topic 4 p122-124.png",
        "target_note": "01 Knowledge/Cryptography/Random Number Generation and Entropy.md",
        "source_note": "Source - Тема №4 ГСЧ(1)",
    },
    {
        "source": "Тема №7 Постквантовая криптография(1).docx",
        "media": "image1.png",
        "paragraphs": "126–127",
        "output": "Lattice Cryptography - Alternative Bases - Topic 7 p126-127.png",
        "target_note": "01 Knowledge/Cryptography/Lattice-Based Cryptography.md",
        "source_note": "Source - Тема №7 Постквантовая криптография(1)",
    },
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--overwrite", action="store_true", help="replace this script's outputs")
    return parser.parse_args()


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def image_dimensions(path: Path) -> tuple[int, int]:
    result = subprocess.run(
        ["magick", "identify", "-format", "%w %h", str(path)],
        check=True,
        capture_output=True,
        text=True,
    )
    width, height = result.stdout.split()
    return int(width), int(height)


def build_pdf_visual(item: dict[str, object], temporary: Path) -> tuple[Path, Path]:
    source = COURSE / "PDF" / str(item["source"])
    raw_prefix = temporary / "rendered-page"
    subprocess.run(
        [
            "pdftoppm", "-png", "-r", "200", "-f", str(item["page"]),
            "-l", str(item["page"]), "-singlefile", str(source), str(raw_prefix),
        ],
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    raw = raw_prefix.with_suffix(".png")
    width, height = image_dimensions(raw)
    left, top, right, bottom = SLIDE_CROP
    x = round(width * left)
    y = round(height * top)
    crop_width = round(width * (right - left))
    crop_height = round(height * (bottom - top))
    output = temporary / str(item["output"])
    subprocess.run(
        [
            "magick", str(raw), "-crop", f"{crop_width}x{crop_height}+{x}+{y}",
            "+repage", "-strip", str(output),
        ],
        check=True,
    )
    return source, output


def build_docx_visual(item: dict[str, object], temporary: Path) -> tuple[Path, Path]:
    source = COURSE / "Original" / str(item["source"])
    archive_path = f"word/media/{item['media']}"
    output = temporary / str(item["output"])
    with zipfile.ZipFile(source) as archive:
        output.write_bytes(archive.read(archive_path))
    return source, output


def main() -> int:
    args = parse_args()
    for command in ("pdftoppm", "magick"):
        if shutil.which(command) is None:
            raise RuntimeError(f"required command is unavailable: {command}")

    records = [
        {**item, "kind": "pdf-page"} for item in PDF_VISUALS
    ] + [
        {**item, "kind": "docx-media"} for item in DOCX_VISUALS
    ]
    expected = [OUTPUT / str(item["output"]) for item in records] + [MANIFEST]
    existing = [path for path in expected if path.exists()]
    if existing and not args.overwrite:
        names = ", ".join(path.name for path in existing[:3])
        raise RuntimeError(f"output already exists ({names}); use --overwrite")

    OUTPUT.mkdir(parents=True, exist_ok=True)
    manifest_records: list[dict[str, object]] = []
    with tempfile.TemporaryDirectory(prefix="crypto-course-visuals-") as directory:
        temporary_root = Path(directory)
        for number, item in enumerate(records):
            item_directory = temporary_root / f"item-{number:02d}"
            item_directory.mkdir()
            if item["kind"] == "pdf-page":
                source, temporary_output = build_pdf_visual(item, item_directory)
            else:
                source, temporary_output = build_docx_visual(item, item_directory)
            width, height = image_dimensions(temporary_output)
            record = {
                "output": str(item["output"]),
                "kind": str(item["kind"]),
                "source_path": str(source.relative_to(VAULT)),
                "source_sha256": sha256(source),
                "target_note": str(item["target_note"]),
                "source_note": str(item["source_note"]),
                "width": width,
                "height": height,
                "output_sha256": sha256(temporary_output),
            }
            if item["kind"] == "pdf-page":
                record["page"] = int(item["page"])
                record["crop_fraction"] = list(SLIDE_CROP)
            else:
                record["media"] = str(item["media"])
                record["paragraphs"] = str(item["paragraphs"])
            manifest_records.append(record)
            os.replace(temporary_output, OUTPUT / str(item["output"]))

        temporary_manifest = temporary_root / MANIFEST.name
        temporary_manifest.write_text(
            json.dumps({"visuals": manifest_records}, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        os.replace(temporary_manifest, MANIFEST)

    print(f"Built {len(manifest_records)} course visuals in {OUTPUT.relative_to(VAULT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
