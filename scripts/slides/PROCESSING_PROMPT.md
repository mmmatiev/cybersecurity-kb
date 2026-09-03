# Presentation integration prompt

Use this prompt from the root of Cybersecurity-KB. Replace PRESENTATION_PATH with the actual PDF or PPTX path.

## Request

Обработай и интегрируй презентацию:

    PRESENTATION_PATH

Следуй существующему AGENTS.md и выполни алгоритм ниже. Все операции с исходником, конвертацией и извлечением выполняй только локально. Не отправляй файл или его содержимое во внешние API и сервисы.

## Algorithm

1. Inspect the source path, extension, size, and current location. Do not modify the original.
2. Determine available metadata such as title, author, organization, event or course, year, page or slide count, and source URL only when present in the source or supplied by the user. Do not invent missing metadata.
3. Read the original PDF/PPTX and, when useful, run:

       python3 scripts/slides/inspect_slides.py "PRESENTATION_PATH"

4. Review extracted text together with visually important source pages. Treat extraction as an aid, not as authoritative replacement for the original.
5. Segment the presentation into semantic sections. Never create one section or note per slide.
6. Search 07 Sources/Slides for an existing source-note representing the same presentation.
7. Create or conservatively update exactly one source-note using 98 Templates/Template - Slides Source.md. Record page or slide ranges for each semantic topic.
8. Search all of 01 Knowledge for canonical names, aliases, related terminology, and possible existing notes.
9. Match semantic sections to existing notes. Distinguish topics that are explained from terms that are merely mentioned.
10. Identify genuinely new knowledge not already present in each matching note.
11. Update an existing knowledge-note only with useful new synthesis. Preserve its frontmatter, structure, style, existing sources, and user-authored content. Do not create duplicate sections.
12. Create a new knowledge-note only when the topic is independently useful and the source contains enough explanation, mechanism, security implications, attack flow, or practical detail. Otherwise retain it only in the source-note and report the possible future note.
13. Write knowledge in original, structured wording. Do not copy the presentation wholesale and do not invent information absent from the source.
14. Link Source ↔ Knowledge. Add provenance such as the source-note plus pages 15–22 or slides 15–22 near the relevant section or in Sources.
15. Prefer PDF page links or embeds for useful visual slides. Do not export every slide to an image. Save a standalone diagram only when it materially improves reuse.
16. Update a relevant MOC only if a durable note was created or the navigation genuinely benefits.
17. Validate frontmatter, links, filenames, source ranges, and that no secrets or confidential content were exposed in logs.
18. Only after successful integration, move the input out of Incoming:
    - unchanged PPTX or other original → 07 Sources/Slides/Original;
    - PDF representation → 07 Sources/Slides/PDF;
    - an originally supplied PDF goes to PDF without a duplicate in Original.
19. Set the source-note processing_status to processed, or review when manual verification is still required.
20. Summarize created and updated files, mapped semantic topics, provenance added, unresolved questions, suggested notes not created, and the final source location.

Do not add embeddings, vector databases, Dataview, Templater, external APIs, a watcher, daemon, or web UI.
