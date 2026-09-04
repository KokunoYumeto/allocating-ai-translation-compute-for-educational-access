# Indian Tamil numeracy recovery

Locale: `ta-Taml-IN`. This is work toward a teacher-independent Grades 2-8 numeracy-recovery system, not a completed grade-spanning course or validated placement instrument.

## Current reading edition

The newest integrated review edition is `reader-m81243-learning/index.html` and `reader-m81243-learning/ta-Taml-IN-A00-m81243.epub`. Keep the HTML with its sibling files. It includes the complete first source module, four recovery segments, support for all58section exercises and an independent final/retry route:75new questions, all answered. Start at the linked learning route; the original confidence checklist is not a mastery test. This is one module, not the complete assigned course. Targeted browser/repeat/package checks and limitations are in `qa/M81243-LEARNING-INTEGRATION.md`; full human/AT review remains pending.

Corrected m81243 PDF repair candidates currently have224 print pages and262 larger-text screen pages, each with22A3-landscape pages for wide source charts and A4 elsewhere. Current hashes are `941fdf36…` and `faee1009…`; exact Tamil/numeric/operator/page-reference/logical-text/tag/geometry checks pass and fresh rasters exist for every page. Root targeted views confirm repaired answer openings, the complete five-choice source prompt, M18 and both number-line arrows. Two low-priority sentence-final periods still sit alone after block MathML and independent all-page final review is active. This PDF/CSS/receipt lane is deliberately excluded from the immediate takeover checkpoint; the PDFs are not released. See `qa/M81243-PDF-QA.md` and profile-specific review notes for historical and current boundaries.

Addition m81244 now has a complete checked **source-review** package: all14 canonical fragments,50SVGs,3,576elements,756IDs,401MathMLtrees,129exercises and89source solutions. The exact40source omissions remain unchanged. Separate recovery material includes the earlier16-item addition core and an independently admitted12-item U012–U013 phrase/application route; a companion for120omitted U015 response parts plus Fred's missing1,230 is active. No complete m81244 learner reader, EPUB, PDF or module-wide mastery route exists yet. Subtraction m81245 U019 is independently source-admitted and U020 is active. The wider assignment stays active.

The historical standalone readers are `reader/index.html` (U001) and `reader-u002/index.html` (U002), each with localfonts/assets and an EPUB. Their PDF profiles have20and24pages respectively. **Newly discovered U001 erratum:** the first number-line graphic lacks its upperright direction arrowhead; the historical HTML/EPUB/PDFs inherit this defect despite their earlier all-page visual review. Repair and full-module re-review are underway; do not treat the old U001renditions as production-ready. AllfourhistoricalPDFs still pass logical-Tamil-token regression (1,652U001;2,303U002); this does not test arrowheads. The earlier PDF-corruption diagnosis was retracted: pypdf misses contextual `/ActualText`, while Poppler recovers logicalTamil. See `qa/PDF-font-investigation.md` and the new module's review notes.

U001 translates the complete first instructional subsection of OpenStax Prealgebra 2e, `m81243#fs-id1830385`: counting/natural numbers, whole numbers and the number line. It preserves 204 XML elements, 44 source IDs, 17 MathML expressions and three source exercises with solutions. A separate recovery companion adds four diagnostic, three practice, four mastery and four retry questions, with all 15 answers, reasoning and feedback routes. Diagnostic routing is within this unit only.

The source translation and new explanations are explicitly separated. Source equations retain their numbers/operators. Counting/natural numbers begin at 1 in this source; whole numbers also include 0. This convention is stated, not presented as universal. The unit is an unofficial adaptation with full source credits and applicable notices.

## Coverage and source acquisition

| Assigned strand | Acquired input | Tamil coverage |
|---|---|---|
| A00 Prealgebra | Indonesian v0.2.7, 75/75 references; complete pinned English source/media | Complete m81243 source + connected HTML/EPUB learning-review route with final PDFs under repair; complete m81244 source-review package plus partial companions, learner integration pending; m81245 U019 admitted and U020 active; remainder pending |
| A10 Elementary Algebra | Indonesian v1.0.2, 82/82 modules; editable release and English source/media | Not yet translated |
| A20 Intermediate Algebra | Indonesian v0.3.0-wip release, 48/83 modules; all 83 English module sources | Not yet translated |
| AX-1 accessibility/offline | Cross-project specification in catalog/allocation | Pilot semantic HTML/MathML, local font, SVG and EPUB; full testing incomplete |
| AX-3 plain-language support | Cross-project specification, supplementary to source | Seven integrated m81243companions,75answered newitems and58source-answer supports; wider sequence incomplete |

`sources.lock.json` records exact URLs, commits, release hashes, physical paths, source coverage and20preserved witnesses. All three English books share the pinned bundle commit `38cae454e644abf9f0a623e876994553881597c9`. The usable complete extraction is `downloads/osbooks-prealgebra-bundle-38cae454e644abf9f0a623e876994553881597c9`; the failed partial Git checkout without the commit suffix is not authoritative. Large corpora remain ignored and must not be modified through shared paths or hard links. No further large duplicate acquisitions are needed for these units.

The newer A20 release, not its stale repository README/root manifest, establishes the 48/83 Indonesian checkpoint. AX-1 and AX-3 are derivative specifications, not separate repositories. Existing allocation/license audits were accepted; no general audit was repeated. Materials are translation inputs and learning artifacts, not a model-training export.

## Rebuild and checks

Run from the repository root with Python 3.11+:

The newest module edition uses `python ta-Taml-IN/scripts/build_m81243_learning.py`; add `--check` for read-only byte verification. The separate source reviewer uses `build_m81243_review.py`. Addition source-draft checks use `qa_m81244.py`. The following older commands still build/check the first standalone unit:

```powershell
python ta-Taml-IN/scripts/build.py
python ta-Taml-IN/scripts/build.py --out build/ta-repeat
python ta-Taml-IN/scripts/qa.py
```

The first-unit HTML and EPUB build needs only the Python standard library and committed files, not the full download corpus. Repeated outputs must be byte-identical. QA checks source order/IDs, math, answers, links, local dependencies and pinned witness hashes. It is not linguistic or educational certification.

EPUB conformance check, using the already-acquired W3C EPUBCheck 5.3.0 and Java:

```powershell
java -jar downloads/qa-tools/epubcheck-5.3.0/epubcheck.jar ta-Taml-IN/reader/ta-Taml-IN-A00-U001.epub --json ta-Taml-IN/qa/epubcheck.json
```

The EPUB stylesheet excludes PDF-only page-margin boxes. This resolved the validator's print-CSS parsing errors without changing learning content. EPUB reader and assistive-technology testing are still needed.

PDF export uses an isolated Chromium document-print process (Edge's Windows path is the default; `--chromium` can override it):

```powershell
python ta-Taml-IN/scripts/render_pdf.py
```

For PDF QA, use a Python environment containing `Pillow`, `pypdf` and `pdfplumber`, and point `--pdftoppm` to Poppler. The Codex bundled workspace runtime provides these dependencies; discover its configured path rather than installing duplicates. Example command with those executables available:

```powershell
python ta-Taml-IN/scripts/pdf_qa.py --pdftoppm pdftoppm
```

This checks logical Unicode text with Poppler `pdftotext` (use `--pdftotext` if it is not on PATH), page bounds and tagging, then updates the task's existing page rasters/contact sheets under ignored `tmp/pdfs/`. Every final page must also be visually reviewed. Add `--unit U002` to export/check that unit. PDF byte hashes can change between exports because Chromium embeds creation timestamps; the deterministic-build claim is for HTML/EPUB, not PDF bytes. The source-only `reader-large-numbers/index.html` preview has no recovery companion, EPUB or PDF yet.

## Canon and review limitations

The initial canon contains 12 located Tamil exemplars from a 2018 Government of Tamil Nadu/SCERT mathematics book, extended to 18 focused shared locators through number-name, rounding, additive-identity and perimeter/area consultation. Individual unit reviewers additionally record larger page sets without inflating the shared locator count. See `canon/README.md` and `canon/CONSULTATION_LOG.md`. Selected PDF pages were OCRed before reading; mathematical OCR uncertainty is resolved against complete page images. The reference is consulted during drafting, revision and QA, not merely collected. It is a register reference, not a current syllabus-alignment claim, and its full PDF/OCR is not redistributed in the learner edition.

Native-speaker/Tamil educator review, learner validation, assistive-technology user testing and PDF/UA validation remain outstanding. Coordinate/origin terminology is provisional. Do not infer whole-course accessibility or efficacy from a tagged PDF, a passing EPUBCheck result, or the small pilot.

The newer `reader-large-recovery/index.html` and its U003-U005 EPUB combine the three large-number source sections with a separate16-item recovery companion. Run `scripts/build_large_numbers.py --check` and `scripts/qa_large_numbers.py` for repeat/content checks. EPUBCheck passes; targeted phone/desktop browser review is recorded in `qa/LARGE_NUMBER-INTEGRATION.md`. Full wide-figure and human accessibility review remain pending. The earlier `reader-large-numbers` remains a source-only reviewer preview; neither folder is a complete module workflow.

## Resume safely

Read `GOAL.md`, `DECISIONS.md`, `NEXT_UNIT.md`, the current root instructions and actual files after interruption. Verify hashes, Git status and HEAD; do not treat compaction summaries as authority. Check disk space before writes: a disk-full incident interrupted final QA, but U001 translation/companion/HTML/EPUB hashes were reverified unchanged after storage recovery. Do not delete source materials or shared logs without authorization. Meaningful local commits are checkpoints, not claims that the whole goal is finished.
