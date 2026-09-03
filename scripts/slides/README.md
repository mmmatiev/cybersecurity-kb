# Local slide inspection

Минимальный локальный pipeline для технической подготовки PDF и PPTX. Он не использует LLM, внешние API, SaaS OCR, embeddings или vector database и не создаёт knowledge-notes.

## Workflow

1. Drop PDF/PPTX into 07 Sources/Slides/Incoming.
2. Keep the original file unchanged.
3. Convert PPTX to PDF if useful for page links and embeds.
4. Run inspect_slides.py.
5. Ask Codex to integrate the presentation.
6. Codex reads the source and/or locally extracted text.
7. Create or update exactly one source-note.
8. Identify semantic topics rather than one topic per slide.
9. Search existing Knowledge.
10. Update existing notes or propose a new note only when justified.
11. Add page or slide provenance.
12. Move the source out of Incoming only after successful processing.

For a PPTX, move the unchanged original to Original after successful integration and keep an optional PDF export in PDF. If the source is already a PDF, move that file to PDF and do not create a duplicate in Original.

## Setup

The script requires Python 3.10 or newer. Create a local virtual environment if the optional Python parsers are needed:

    python3 -m venv .venv
    source .venv/bin/activate
    python -m pip install -r scripts/slides/requirements.txt

PyMuPDF is the preferred PDF parser. If it is unavailable, the script can use local pdfinfo and pdftotext executables. Direct PPTX inspection requires python-pptx.

## Inspect a source

From the Vault root:

    python3 scripts/slides/inspect_slides.py "07 Sources/Slides/Incoming/file.pdf"

The default result is:

    07 Sources/Slides/Processed/file/
    ├── manifest.json
    └── extracted-text.md

The command does not move or rename the source. It refuses to overwrite an existing technical result unless --overwrite is explicitly provided:

    python3 scripts/slides/inspect_slides.py \
      "07 Sources/Slides/Incoming/file.pdf" \
      --overwrite

Extracted text is written only to the local output files. It is not printed to standard output.

## PPTX to PDF

PDF is preferred for stable page references in Obsidian. Check for a local converter:

    command -v soffice
    command -v libreoffice

If LibreOffice or its soffice command is available:

    soffice --headless --convert-to pdf \
      --outdir "07 Sources/Slides/PDF" \
      "07 Sources/Slides/Incoming/file.pptx"

Conversion is optional and the pipeline is not tied to LibreOffice. A PDF can instead be exported manually from PowerPoint, Keynote, or another trusted local office application. Do not use external conversion services for confidential material.

## Integrate with Codex

After inspection, use scripts/slides/PROCESSING_PROMPT.md or ask:

    Интегрируй презентацию
    07 Sources/Slides/Incoming/file.pdf
    в базу знаний.

The technical files in Processed are extraction artifacts. They must be public-safe and are intentionally tracked by Git, but they should not be linked from Home, Sources, or knowledge MOC pages.

## Security and storage

- Keep all parsing and conversion local.
- Do not print presentation contents to public logs.
- Only public-safe presentation material may enter this Vault; keep confidential, internal, restricted, and private PoC material outside it.
- Original presentation binaries, PDF exports, and Processed outputs are intentionally tracked in the public repository.
- Run `scripts/public_preflight.sh` before committing. Do not add a file of 50 MiB or more to regular Git without a separate Git LFS or external-storage decision.
