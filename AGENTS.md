# AGENTS.md

## Purpose

- This repository is an Obsidian knowledge base for technology and cybersecurity.
- Keep the vault simple, useful, concise, and scalable.
- Prefer standard Obsidian functionality and avoid unnecessary plugin dependencies.

## Safety

- Search before creating. Never create duplicate notes.
- Never delete, rename, move, or overwrite user notes without explicit instruction.
- Never modify, expose, or store credentials, API keys, tokens, private keys, or passwords in notes.
- Do not edit MCP/API credentials or Local REST API authentication data.
- Treat .obsidian carefully and do not install plugins automatically.
- Preserve existing frontmatter and user content when editing notes.
- Do not use destructive Git commands or discard unrelated changes.

## Public repository and storage

- Treat every file placed in this Vault as intended for permanent public Git history.
- Never place confidential, internal, restricted, or otherwise non-public source material in the Vault, even temporarily.
- Never place credentials, private keys, passwords, tokens, or private PoCs in Inbox, Incoming, Processed, Attachments, or any other Vault directory.
- If publication safety is uncertain, keep the material outside the Vault and ask before importing it.
- Source binaries and the Incoming, Original, PDF, Processed, and Attachments directories are intentionally tracked by Git.
- Deleting sensitive material after a push does not remove it from published Git history.
- Before every commit, verify that ignored credential files are not tracked, scan tracked files for credential-shaped assignments and private-key markers without printing matched values, and check the size of newly added files.
- The repository uses the tracked `.githooks/pre-commit` hook for these checks. After cloning, enable it with `git config core.hooksPath .githooks`.
- Do not add a file of 50 MiB or more to regular Git without a separate decision about Git LFS or external storage. GitHub blocks regular Git objects larger than 100 MiB, and Git LFS is not currently installed. See [GitHub repository limits](https://docs.github.com/en/repositories/creating-and-managing-repositories/repository-limits).
- The public GitHub repository is the versioned backup. iCloud provides file synchronization for the Vault; it is not a substitute for version history. Time Machine is not currently configured.

## Architecture

- 00 Home: main entry point.
- 00 Inbox: unprocessed ideas, links, questions, and temporary notes.
- 01 Knowledge: durable domain knowledge and the cross-cutting Cybersecurity layer.
- 02 Tools: tools and their practical usage.
- 03 Practice: completed labs, CTF tasks, and hands-on exercises.
- 04 Cases: CVEs, incidents, bug bounty reports, campaigns, and writeups.
- 05 Research: original questions, experiments, ideas, and projects.
- 06 Cheat Sheets: short operational references.
- 07 Sources: source material and source-notes.
- 90 Attachments: images, diagrams, and selected slide excerpts.
- 98 Templates: note templates prefixed with Template -.
- 99 Archive: inactive material retained for history.
- scripts: small local-only helpers for repeatable technical processing.

Do not create new directories, notes, or MOC pages before real content requires them.

## Classification

Properties answer independent questions. The folder expresses lifecycle or physical location, `area` identifies the technology substrate, and `security` identifies the security workstream:

- type: What kind of note is this?
- area: What domain or technology is this about?
- security: Which cybersecurity area is relevant?

Allowed area values:

- Computer Science
- Networks
- Operating Systems
- Web
- Software Engineering
- Databases
- Cloud
- AI & ML
- Cryptography
- Cybersecurity

For content notes, `area` is required and is always a YAML list. Use one value by default and no more than two. Use `area: Cybersecurity` only for MOCs and genuinely domain-neutral security concepts. Navigation-only MOCs, templates, and Inbox placeholders are not content notes and may retain an empty required placeholder.

Allowed security values:

- AppSec
- Network Security
- Infrastructure Security
- Cloud Security
- AI Security
- Threat Intelligence
- DFIR
- Malware
- OSINT
- Security Engineering

The `security` property is required for every note under `01 Knowledge/Cybersecurity`. It is optional elsewhere. When present, it is a YAML list with one value by default and no more than two.

Allowed type values:

- concept
- attack
- vulnerability
- technique
- tool
- lab
- case
- research
- cheatsheet
- standard
- source
- moc

For content notes, `type` is required. Select one primary angle:

- concept: a neutral entity or mechanism.
- vulnerability: a pre-existing weakness.
- attack: a self-contained adversarial flow.
- technique: a repeatable action or method.

An alternative angle on the same object does not justify a second note. Extend the canonical note unless a separate note meets the independent-value rule below.

For Knowledge, optional status values are:

- learning
- review
- stable

Slide sources use processing_status instead of status:

- unprocessed
- processing
- processed
- review

Do not require level, created, updated, aliases, tags, or status when they are not actively useful. Outside `01 Knowledge/Cybersecurity`, do not require `security` when it is not useful. Do not repeat area or security classification in tags. Do not leave empty optional properties in saved notes; empty placeholders are allowed in templates only for fields required by that template.

## Domain-first organization

Knowledge is primarily organized by the domain or technology being studied:

- TCP belongs to Networks.
- HTTP and OAuth belong to Web.
- Linux belongs to Operating Systems.
- PostgreSQL belongs to Databases.
- Kubernetes belongs to Cloud.
- RAG belongs to AI & ML.

Security is a cross-cutting concern built on domain knowledge:

- TCP → SYN Flood
- HTTP → Request Smuggling
- SQL → SQL Injection
- OAuth → OAuth attacks
- RAG → RAG Poisoning
- LLM Agents → Prompt Injection

When creating a security-note, search for existing foundational concepts and link them when useful. Never create an empty foundation note only to satisfy this relationship.

## One canonical concept

- Maintain one canonical note for a technology or concept.
- Never create separate copies such as Networks/TCP and Network Security/TCP.
- Put concise security implications in the canonical domain note when that is sufficient.
- Create a separate attack, vulnerability, or security concept only when it has substantial independent value: its own attack flow, detection or mitigation content, related practice or cases, or a distinct retrieval purpose.
- A separate security note links to its domain foundation and does not restate the foundation's mechanics.
- Do not create X Security notes for every technology merely for symmetry.
- Use wikilinks and MOC pages instead of duplicating content.

## Physical placement

Apply this precedence in order:

1. Lifecycle placement overrides domain placement: tools go to `02 Tools`; labs and CTF work to `03 Practice`; real CVEs, incidents, bug bounty reports, campaigns, and writeups to `04 Cases`; original investigations to `05 Research`; operational references to `06 Cheat Sheets`; source material and source-notes to `07 Sources`.
2. Within `01 Knowledge`, place a neutral technology, mechanism, or standard in its most specific domain folder.
3. Place an attack, vulnerability, or security-specific process in `01 Knowledge/Cybersecurity/<primary workstream>`. Its `area` identifies the underlying technology substrate.
4. A cross-cutting security concept with no single technology substrate may live directly in `01 Knowledge/Cybersecurity`. Do not use `Security Engineering` as an automatic catch-all.
5. For a multi-area note, select one physical home and express secondary relationships through at most two `area` values, at most two `security` values, wikilinks, and MOCs.

Placement examples:

- TCP: `01 Knowledge/Networks`; `type: concept`; `area: [Networks]`.
- TLS: `01 Knowledge/Cryptography`; `type: concept`; `area: [Cryptography]` and optionally `Web` when the note substantially covers web use.
- OAuth: `01 Knowledge/Web`; `type: concept`; `area: [Web]`.
- Docker: `01 Knowledge/Cloud`; `type: concept`; `area: [Cloud]`.
- SSRF: `01 Knowledge/Cybersecurity/AppSec`; `type: attack`; `area: [Web]`, optionally adding `Cloud` for substantial cloud-specific coverage; `security: [AppSec]`.
- SQL Injection: `01 Knowledge/Cybersecurity/AppSec`; choose `type: vulnerability` for the injectable weakness or `type: attack` for the end-to-end exploitation flow; `area: [Web, Databases]`; `security: [AppSec]`.
- Prompt Injection: `01 Knowledge/Cybersecurity/AI Security`; choose one primary `type`; `area: [AI & ML]`; `security: [AI Security]`.
- Kerberoasting: `01 Knowledge/Cybersecurity/Infrastructure Security`; `type: attack`; `area: [Operating Systems]`, optionally adding `Networks`; `security: [Infrastructure Security]`.
- Threat Hunting: `01 Knowledge/Cybersecurity/Security Engineering`; `type: concept`; `area: [Cybersecurity]`; `security: [Security Engineering]`, optionally adding `DFIR` or `Threat Intelligence` only when the note substantially covers that workstream.
- AWS IMDS: `01 Knowledge/Cloud`; `type: concept`; `area: [Cloud]`. Put concise security implications here; place a substantial IMDS attack flow under the appropriate Cybersecurity workstream.
- Wireshark: `02 Tools`; `type: tool`; `area: [Networks]`; `security` is optional.
- A PortSwigger lab: `03 Practice`; `type: lab`; `area: [Web]`; `security: [AppSec]` when useful.
- A CVE: `04 Cases`; `type: case`; use the relevant `area` and `security` values.

## Minimal metadata

A basic knowledge-note starts with:

    ---
    type: concept
    area:
      - Networks
    ---

A note under `01 Knowledge/Cybersecurity` also includes:

    security:
      - Network Security

Add status, aliases, or tags only when they improve retrieval or workflow. A template is a starting structure, not a questionnaire.

## Naming and links

- Prefer canonical cybersecurity and technology terminology with human-readable filenames.
- Keep common English names for technologies, protocols, attacks, standards, products, and tools.
- Explanatory text may be written in Russian.
- Use Obsidian wikilinks such as <code>[[Target Note]]</code> for meaningful relationships.
- Search canonical names and aliases before creating a note.
- Preserve useful backlinks and update links when files move.
- Link only to useful existing notes; do not create large sets of artificial dead links.

Naming conventions:

- CVE: CVE-YYYY-NNNNN - Short Description.md.
- Lab: Platform - Topic - Lab Name.md.
- Research: Research - Short descriptive name.md.
- Templates: Template - Type.md.

## MOC philosophy

- MOC pages are curated learning and navigation maps, not exhaustive file indexes.
- A MOC should explain how an area is structured and where to begin.
- Security MOC pages should link to relevant domain foundations.
- Update a MOC only when navigation genuinely improves.
- Do not create MOC pages for empty speculative taxonomies.

## Knowledge lifecycle

- Source material belongs in Sources; synthesized knowledge belongs in Knowledge.
- Practice, Cases, and Research remain separate from canonical Knowledge.
- Knowledge explains how a technology works.
- Security notes explain how it is attacked, tested, detected, or protected.
- Tools, Practice, Cases, and Research connect to both foundation and security notes.
- Knowledge notes synthesize information in original wording and preserve provenance.

## Slide and Presentation Processing

- Presentations are sources, not canonical knowledge.
- Keep one mandatory source-note per processed presentation. Never create one note per slide.
- Original presentation files must not be modified.
- Process PDF and PPTX locally. Do not upload source files or extracted content to external conversion, OCR, parsing, or AI services.
- Segment presentations by semantic topic rather than page boundaries.
- Distinguish a term that is merely mentioned from a topic that is substantially explained.
- Search existing domain and security Knowledge before creating notes; prefer useful additions to existing canonical notes.
- Create a new note only when the source contains enough material for a durable concept, mechanism, vulnerability, attack, technique, or technology note.
- When uncertain whether a new note is justified, retain the information in the source-note and report the suggestion.
- Do not invent details or copy source text wholesale.
- Preserve provenance with the source-note and relevant page or slide range.
- Prefer PDF page links or embeds for useful visual material.
- Do not embed every slide or export every slide as an image.
- Extract a standalone diagram only when it materially improves reuse or comprehension.
- Use processing_status for slide source lifecycle.
- Move an input out of Slides/Incoming only after inspection and integration complete successfully.
