# Gujarati A00/A10 translation and numeracy workflow

Locale **gu-Gujr-IN**, rank **10**. Start with [the full-assignment library](output/library/index.html), [the first student companion](output/index.html), or [its worked answers and feedback](output/solutions.html). All reader files and the Gujarati font are local; no account, network runtime, analytics or pupil-data collection is used.

The active assignment is **all 75 A00 and 82 A10 modules plus AX-1/AX-3**, not only the completed first pilot. Twenty-three full source drafts are integrated: fourteen A00 modules through the integer chapter introduction, and nine A10 modules through decimals, including both books' front matter. They retain2,443exercises and1,573supplied solutions; eight separate companions add437omitted answers. The newest40integer answers have source/math/rendered checks and completed independent peer review. Source structures and mathematical tokens are checked; complete workflows are not finished. [COVERAGE.json](COVERAGE.json) records every assigned module and the latest counts. The distinct remediation sequence serves Grades 2–6 by skill, without dropping advanced assigned source content. Gujarati educator review, child testing and assistive-technology review remain pending.

## Current library and completed first checkpoint

- [A00 m81243](output/library/a00-m81243.html): all 88 exercises and 59 source-supplied solutions, with [29 separately added worked answers](output/library/a00-m81243-answers.html). Complete source XML trees are checked by [LIBRARY_QA.json](LIBRARY_QA.json).
- [A00 m81244 addition](output/library/a00-m81244.html): all129exercises and89supplied solutions, with [all40omitted answers](output/library/a00-m81244-answers.html), countable block models and completed answer grids. Language-bearing figures and accessibility attributes are localized.
- [A00 m81245 subtraction](output/library/a00-m81245.html): all125exercises and83supplied solutions, with [all42omitted answers](output/library/a00-m81245-answers.html), place-exchange models and inverse-addition checks. Source errors remain explicit correction notes.
- [A00 m81255 multiplication](output/library/a00-m81255.html): all171exercises and112supplied solutions. Six labelled diagrams,12source charts and the self-check are localized or semantic; original question blanks stay blank. All [59omitted answers](output/library/a00-m81255-answers.html) are in a separate checked companion.
- [A10 m82452](output/library/a10-m82452.html): all 115 exercises and 74 source-supplied solutions, with [41 separately added worked answers](output/library/a10-m82452-answers.html). Source errors have visible, ID-keyed correction notes; original mathematical data remain traceable. Completing omitted answers does not mean every original short solution has received expanded teaching scaffolding.
- [A10 m82453 algebra language](output/library/a10-m82453.html): all156exercises and105supplied solutions, all610language slots,14localized figures and36mathematical originals. Its [51omitted answers](output/library/a10-m82453-answers.html) now have a separate source-checked and peer-reviewed worked companion.
- [A00 m81256 division](output/library/a00-m81256.html): all313exercises and178supplied solutions, including chapter review/test. Six labelled diagrams, sixcharts and the self-check are localized/semantic; [all135omitted answers](output/library/a00-m81256-answers.html) now have a separate worked companion. Addition/multiplication chart operators, source blanks, long division, zero divisors and remainder checks are independently verified. The [algebra introduction](output/library/a00-m81266.html) retains all18word-cloud fragments.
- [A10 m82454 signed addition/subtraction](output/library/a10-m82454.html) and [m82455 signed multiplication/division](output/library/a10-m82455.html) are full source drafts with explicit errata; all20language-bearing m82454figures are localized; its45mathematical originals have reviewed Gujarati alternatives. All14language-bearing m82455figures are also localized, with15reviewed mathematical originals retained.
- [All40omitted integer answers](output/library/a10-m82454-answers.html) distinguish opposites, absolute value and subtraction, with worked reasoning and historical contexts preserved. Independent peer review is complete. Newly integrated source drafts include [factors/multiples](output/library/a00-m81272.html), [prime factorization/LCM and chapter review](output/library/a00-m81273.html), [the integer chapter introduction](output/library/a00-m81274.html), and [decimals](output/library/a10-m82458.html). All15language figures in [fraction addition/subtraction](output/library/a10-m82457.html) are now localized.
- Figures are being localized and reviewed separately from prose. Coverage records distinguish localized diagrams from original assets with Gujarati alternatives. No complete-book or full-workflow completion is claimed.

The earlier pilot checkpoint contains:

- A complete source-faithful translation of A00 `m81243`, section `fs-id1830385`, with its original example, two Try It exercises, solutions, figure ID and numeric/MathML structure. The number line is explicitly redrawn with Gujarati labels and an accessible description.
- One selected A10 `m82452` exercise, `fs-id1170655190140`, with its original numbers and solution IDs, as an optional five-digit place-value bridge.
- A separate AX-3 companion: **6 placement items, 3 remediation paths, 8 practice items and 3 exit items**. Every item has a full worked solution. All 18 placement options have specific feedback. Four additional explanations expand the source exercises' reasoning without altering their source-faithful answers.
- Offline semantic HTML and two print PDFs: [student, 10 pages](output/pdf/unit01-student-print.pdf) and [teacher, 8 pages](output/pdf/unit01-teacher-print.pdf). PDF Gujarati shaping and logical text extraction are checked. These PDFs are **not tagged PDF/UA**; semantic HTML remains the screen-reader format. A separate certified/tagged screen PDF is not claimed.
- A growing [terminology ledger](terminology.csv) and the original 13 OCR-read Gujarati canon examples, with targeted additions for later topics. See [canon workflow](canon/README.md), [targeted evidence](canon/targeted-examples.md) and [consultation log](canon/consultation-log.md).

## Acquired inputs

Four pinned repositories: Indonesian program, Indonesian A00, Indonesian A10 and the canonical OpenStax bundle. Both complete Indonesian editable source release ZIPs are acquired, plus manifests/checksums. A00 has 75/75 collection modules; A10 has 82/82. All **157 English module Git-blob hashes** match the edition authority copies. Windows checkout newline conversion is not mistaken for source-byte identity.

The Git canonical checkout is sparse. A **separate complete 537,455,794-byte pinned canonical archive and full extraction** provide media as well as text; do not infer full acquisition from a sparse checkout. Large files reside under ignored `downloads/gu-Gujr-IN/`. See [sources.lock.json](sources.lock.json) and [canonical archive receipt](provenance/canonical-archive.json). A00 and the full canonical ZIP were copied read-only from sibling tasks' verified acquisitions and rehashed locally; the A10 release was downloaded here. Published reader PDFs and duplicate backend ZIPs were unnecessary translation inputs and are not claimed acquired.

AX-1 and AX-3 are cross-project specifications in the program repository, not independent repos. Their exact selected records and source hashes are retained in [AX-specifications.json](provenance/AX-specifications.json).

## Source-to-product sequence

[source-module-map.csv](source-module-map.csv) maps every assigned A00/A10 module to its title, order, hashes, local paths and current status. Translation begins with the introductory modules and proceeds through both entire collections. Advanced source modules remain in the complete source edition, while the child-facing remediation sequence selects appropriate prerequisites and explanations separately. A10 modules are not excluded merely because they lie beyond Chapter 1.

Source-faithful text and plain-language adaptation remain separate. Source numbers, letters and identifiers are preserved. Gujarati/Western digit equivalence is taught explicitly; either answer script is accepted. No silent currency conversion, source correction or grade-equivalence claim is made.

## Rebuild and verify

Python 3.12 was used. The committed reader output can be opened without a build. The pilot HTML build needs only Python's standard library and committed files:

```powershell
python gu-Gujr-IN/scripts/build.py
```

The full library build and source-bound QA also need the ignored acquired inputs at the relative paths in `sources.lock.json` and `source-module-map.csv`: four pinned repositories, release authority XML and the complete canonical media extraction. A clean clone alone is insufficient. Rehydrate the exact recorded URLs/commits/hashes; no absolute sibling/donor path is needed. `fetch_releases.py` acquires the two pinned releases, but there is not yet one bootstrap command for all repositories and the canonical archive. With those inputs present:

```powershell
python gu-Gujr-IN/scripts/build_library.py
python gu-Gujr-IN/scripts/prepare_translation.py
python gu-Gujr-IN/scripts/lock_sources.py
python gu-Gujr-IN/scripts/qa.py
python gu-Gujr-IN/scripts/qa_library.py
python gu-Gujr-IN/scripts/qa_a00_added_solutions.py
python gu-Gujr-IN/scripts/qa_a00_addition_answers.py
python gu-Gujr-IN/scripts/qa_a00_subtraction_answers.py
python gu-Gujr-IN/scripts/qa_a00_multiplication_answers.py
python gu-Gujr-IN/scripts/qa_multiplication_figures.py
python gu-Gujr-IN/scripts/qa_division_figures.py
python gu-Gujr-IN/scripts/qa_a10_integers_figures.py
python gu-Gujr-IN/scripts/qa_a10_algebra_answers.py
python gu-Gujr-IN/scripts/qa_a10_front_matter.py
python gu-Gujr-IN/translations/qa_a10_m82452.py
python gu-Gujr-IN/translations/qa_a10_m82453.py
python gu-Gujr-IN/translations/qa_a10_m82453_math.py
python gu-Gujr-IN/scripts/package_offline.py
python gu-Gujr-IN/scripts/refresh_status.py
```

PDF generation additionally requires ReportLab with shaping support and uharfbuzz (`0.56.0` used here):

```powershell
python gu-Gujr-IN/scripts/build_pdf.py
python gu-Gujr-IN/scripts/verify_print.py
```

The bundled Codex Python has ReportLab; this task installed uharfbuzz only into ignored `downloads/gu-Gujr-IN/python-deps`. `build_pdf.py` loads that local directory. The Noto Sans Gujarati font and its original OFL notice are committed. `scripts/fetch_releases.py` reproduces the exact pinned release downloads and checks their SHA-256 digests. `scripts/ocr_canon.py` OCRs only admitted reference pages; `scripts/record_canon.py` records their hashes.

The portable draft ZIP is generated at `dist/gujarati-current-draft-offline.zip` (ignored build product). It contains all reachable local reader assets, the pilot PDFs, a Gujarati opening guide, a hash manifest and current coverage. Extract the entire archive and open `index.html`. [OFFLINE_QA.json](OFFLINE_QA.json) verifies its bytes, internal links/fragments and absence of remote runtime dependencies. Optional external source links require the Internet; the lessons do not.

Print verification also requires `pypdf` and Poppler `pdftotext`. [PRINT_QA.json](PRINT_QA.json) records PDF hashes, page counts, font coverage and logical extraction. [REVIEW.md](REVIEW.md) records actual browser and rendered-page inspection. The print renderer substitutes supported `(a)`–`(e)` subpart labels for circled letters; editable sources and HTML retain the original labels.

Run [QA.json](QA.json)'s checks after any content change. Read [GOAL.md](GOAL.md), [DECISIONS.md](DECISIONS.md), [STATUS.json](STATUS.json), [NEXT_UNIT.md](NEXT_UNIT.md) and the relevant canon pages before resuming; do not treat compaction summaries as evidence. The ongoing coordinating task is `[local-task-id]`; read its latest **user messages** at resumption and integrate steering without duplicating the parent's administrative work.

## Attribution and license

OpenStax/Rice University; senior contributing authors Lynn Marecek, MaryAnne Anthony-Smith and Andrea Honeycutt Mathis. Indonesian editions: the pinned KokunoYumeto repositories, produced with OpenAI Codex gpt-5.6-sol, Ultra. Gujarati translation/adaptation: Language Allocation, OpenAI Codex, 2026-08-30. Original notices and full license texts are preserved in [notices/](notices/) and in the reader.

Content and adaptation: **CC BY-NC-SA 4.0**, subject to component-specific credits/restrictions. No endorsement, trademark license or warranty is implied. Gujarati canon references inform language; their full texts are not redistributed here. These materials are translation inputs and outputs, not a model-training or fine-tuning dataset.


## Full-module tagged PDF technical draft

[The41-page A00m81243 draft](output/tagged-screen-pdf/a00-m81243.pdf) contains real structure, bookmarks, Formula/Figure alternatives and embedded fonts. It is **not certified accessible or PDF/UA**: PDF.js loses some Gujarati shaped characters, although Poppler and structure-aware extraction pass. Prefer the HTML reader. [The detailed review](reviews/tagged-screen-pdf.md) preserves successful checks and the failed compatibility receipt. The offline ZIP includes this file with that limitation disclosed.

The PDF scripts use normal Node module resolution, or explicit `PLAYWRIGHT_MODULE_PATH`, `PDF_CHROME_PATH` and `PDFJS_MODULE_PATH` environment variables pointing to the second machine's own installations. They no longer require this PC's hardcoded runtime paths. Python needs lxml/pypdf and Poppler, and printing needs Playwright plus a local Chromium/Chrome installation. Root repeated the full41-page print/finalize/structure check with these configurable paths; the regenerated PDF has the same reviewed structure but different PDF bytes, so bit-identical PDF reproduction is not claimed. The delivered frozen PDF hash remains in its QA receipt.

Current continuation: sixteen source drafts retain1,585exercises/1,032suppliedsolutions, with262separate added answers. [Multiplication answers](output/library/a00-m81255-answers.html) cover all59omissions; [A00 algebra language](output/library/a00-m81268.html) and [A10 fraction visualization](output/library/a10-m82456.html) are new complete source drafts. Five A00 algebra figures and fourteen signed-product figures are localized; fraction figures remain in progress. Full module workflows and the whole assignment remain unfinished.

The coordinator maintains the single GitHub review branch `codex/additional-translations-review` in the allocation research repository. This supersedes the earlier coordination-only publication scope. Review snapshots remain drafts; no main merge, production release or external human approval is implied. Source pins remain unchanged; the scoped upstream decision is in [reviews/upstream-relevance-2026-08-31.md](reviews/upstream-relevance-2026-08-31.md).
