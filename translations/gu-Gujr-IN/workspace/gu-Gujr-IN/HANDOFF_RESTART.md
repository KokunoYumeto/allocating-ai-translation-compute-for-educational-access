# Gujarati translation takeover cursor

This file is the transcript-independent entry point for continuing the Gujarati lane on another machine. Paths are relative to the bundle workspace. Read this file, `NEXT_UNIT.md`, `STATUS.json`, `WORK_QUEUE.json`, `COVERAGE.json`, `terminology.csv`, `canon/README.md`, `canon/consultation-log.md`, and the review for the unit being resumed. Do not infer completion from a commit, package, or source-draft count.

## Active goal and workflow

Complete the entire assigned Gujarati `gu-Gujr-IN` mathematics scope: all 75 A00 modules, all 82 A10 modules, AX-1 figure/accessibility work, and AX-3 diagnostic/remediation work. Preserve every source ID, hierarchy, mathematical token, exercise, supplied solution, and source omission. Put newly authored solutions in explicit companions instead of changing faithful CNXML. Keep source corrections and reading bridges visible and keyed; never silently rewrite authority mathematics. Continue after bounded commits until the full assignment and workflow are complete.

Use readable Gujarati mathematical canon throughout the work. The admitted initial set contains 13 examples; consult it before drafting, return to it while revising, and check it again during output review. Add narrow topic evidence only when the existing shelf is insufficient. OCR a PDF before treating its text as readable, inspect the original page where OCR damages numbers or operators, and never use noisy OCR as mathematical authority. Record what was actually read, when it was used, and what it did or did not support. Keep `terminology.csv` consistent: in particular, distinguish `પૂર્ણ સંખ્યા` (whole number) from `પૂર્ણાંક` (signed integer).

This is translation and educational production, not model training or fine-tuning. Do not start a new general acquisition, licensing, or supply audit. Use the pinned sources and existing notices. Do not delete, replace, hardlink, or reacquire authority inputs merely to simplify storage. Do not push this lane, merge main, or publish a release; the coordinator owns the single review branch. Native Gujarati educator review, pupil usability testing, keyboard/screen-reader testing with actual assistive technology, certified PDF/UA, and production approval remain outside machine QA and must stay marked pending.

The raw user conversation, private task records, credentials, account/host identifiers, and private update files are intentionally absent. The operational rules above are the durable public workflow derivative. Existing source and license notices remain authoritative for content rights.

## Checkpoint and completed boundary

The last translation-content checkpoint is commit `2c09d5b6be91aea2060aa2e04c4e48708164e281` on branch `codex/gujarati-numeracy-pilot`; parent `826aa1cef3eb169ec42668e79614c2f92388cf29`; tree `5326f9661a55db6f5202ae4b10651356059be47e`. A later handoff-only commit may carry this cursor and the bundle builder; its exact identity is recorded in the bundle manifest and does not widen the translation claim.

That content checkpoint contains 29 complete source drafts with 3,489 exercises, 2,213 source-supplied solutions, and 1,276 source omissions. Nine separate companions add 476 worked answers, leaving 800 current omissions without companions. Integrated AX-1 work includes A00 m81271, m81272, m81273, m81275; A10 m82454–m82458 as recorded in coverage and figure receipts. The latest m81275 increment covers all 13 language-bearing occurrences as 12 purpose-built Gujarati bodies plus the existing semantic self-check; 23 inspected mathematical originals remain. Its phone reader is 375/375, desktop is 1265/1265 with an 860-pixel main, and the semantic self-check retains 15 blank cells.

The portable checkpoint package is 17,327,642 bytes with SHA-256 `e34c38e4900e961e2190f2018cc0d27ff0a3f6efcee11a0f977f399cc8bead53`: 731 files, 43 HTML pages, no remote runtime dependency, and 48 optional external references. `OFFLINE_QA.json` records CRC, byte, link/fragment, CSS, and font-closure checks. This is a draft checkpoint, not a completed assignment or publication.

## Safe resume point and excluded work

Resume with frozen A00 m81277 (`Subtract Integers`) before taking any active successor file. Its complete translator package is deliberately outside the checkpoint: 4,226 elements, 919 IDs, 138 exercises, 96 supplied solutions, 42 omissions, 406 MathML expressions, 730 language slots, and 101 media. Frozen CNXML SHA-256 is `78f802aff98c1a622a91d83d47b6faaa0aeae21fcf7a5ff4179ac37202e2e5d7`; media/errata receipt SHA-256 is `7c56e667ecb3f86ef95da5eca3e117046ae9322a00dc9c0401ce5b676d0866fb`.

Do not add the m81277 recipe unchanged. The current normalizer crashes on its three locator-keyed text errata; five malformed source `<mn>` unit strings need reader-only Gujarati replacements; table `eip-id1168469693755` needs the full leading-negative aria correction; and the second token under list `eip-id1168466333215` must render `ⓑ` with a visible source note. The faithful CNXML must remain byte-identical. Fourteen visible-English assets remain AX-1 work; AppB015 must become a semantic four-column/five-skill table with 15 empty cells. Partial local attempts to generalize the renderer/normalizer after `2c09d5b…` were not checkpointed and must be independently reconstructed and tested.

Also excluded: the frozen 12-figure AX-1 bundle for A00 m81276; active/unreviewed A10 m82463 files; any A00 m81278 successor work; dot-prefixed review scratch/contact sheets; and shared instruction/dispatch files. Their omission prevents torn ownership and private/transient material from entering the checkpoint. `WORK_QUEUE.json` records the intended ownership boundary.

## Rebuild inputs and commands

Use Python 3.12. The HTML/library/package path uses the standard library. Some source and PDF checks additionally use `lxml`, `pypdf`, ReportLab with shaping, `uharfbuzz` (0.56.0 was used), Poppler `pdftotext`, Playwright, and a local Chromium/Chrome. The semantic HTML is the preferred accessible output. PDF scripts accept environment-specific `PLAYWRIGHT_MODULE_PATH`, `PDF_CHROME_PATH`, and `PDFJS_MODULE_PATH`; do not copy another host's absolute paths.

The bundle mirrors curated ignored inputs under `downloads/gu-Gujr-IN/` so builds use repository-relative paths. `sources.lock.json`, `source-module-map.csv`, `provenance/`, and the bundle manifest bind versions and hashes. If a dependency is listed as absent, reacquire only its exact recorded URL/commit/hash; do not substitute a newer source automatically. The 537 MB canonical archive is too large for ordinary GitHub blob capture, so the bundle carries the exact authority CNXML and reviewed media needed by the checkpoint plus the archive locator/hash and deterministic reacquisition record.

From the bundle workspace root, the primary entry check is:

```powershell
python gu-Gujr-IN/scripts/qa_library.py
```

Then use, as relevant:

```powershell
python gu-Gujr-IN/scripts/build_library.py
python gu-Gujr-IN/scripts/qa.py
python gu-Gujr-IN/scripts/qa_a00_integer_intro_figures.py
python gu-Gujr-IN/scripts/package_offline.py
python gu-Gujr-IN/scripts/refresh_status.py
```

Run the module-specific QA named in each review before integration. After reader changes, inspect actual Gujarati rendering at phone and desktop widths, rerun deterministic library QA, rebuild the offline package, update durable records, and commit only the coherent unit. The bundle receipt states whether the entry check was actually rerun inside the copied directory.

## Canon and provenance in the bundle

The bundle includes the tracked canon shelf, terminology ledger, consultation logs, source locks/notices, exact authority CNXML for checkpointed modules, original media used by their readers/figure QA, and the complete small Gujarati-canon directory: original PDFs, selected page PNGs, OCR text, contact image, and OCR language data. Remote Gujarati Khan pages were consulted through indexed readable excerpts; webpage bytes were not preserved. Their exact locators, consultation dates, supported terminology, and stated limitations remain in `canon/targeted-examples.md`, `canon/consultation-log.md`, and module reviews, and the bundle absence record marks the bytes unavailable.

Verify `MANIFEST.json` and `sha256sums.txt` before use. Every included file has a relative path, size, SHA-256, role, and either a checkpoint Git blob identity or an external-input provenance source. Sanitized text derivatives identify their original blob and transformation. No raw chat, credential, private instruction, personal host/account/task identifier, private ZIP member, unrelated corpus, or known broken/transient output is part of the bundle.

## Human and production limits

Machine QA proves structural fidelity, selected mathematical relations, deterministic builds, local links/resources, and stated accessibility markup. It does not prove idiomatic native Gujarati across the full corpus, age suitability, classroom efficacy, actual screen-reader behavior, PDF/UA conformance, complete AX-1/AX-3 coverage, or production readiness. Continue to label all such work pending until the corresponding human or device-based acceptance is performed and recorded.
