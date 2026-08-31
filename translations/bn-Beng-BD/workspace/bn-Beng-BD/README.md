# Bangladesh Bangla numeracy - U01/U02 and complete m81243

Open `output/U02/index.html` for the current compilation. Keep the extracted folder together so its local fonts and links work. Reading needs no server or connection; external reference links require a connection only when selected. U01 remains available at `output/u01-number-sense.html`.

This is the rank-2 Bangladesh Bangla assignment (`bn-Beng-BD`), not Indian Bengali. It is an AI-assisted draft, not an NCTB-approved or Bangladesh teacher-reviewed publication. The whole assignment remains active: 75 A00 modules, selected foundational A10, and AX-1/AX-3 products. Four complete source drafts exist: two instructional modules and two front-matter modules.

## Current coverage

The complete preface and first chapter introduction are at `output/m81241/index.html` and `output/m81242/index.html`. They preserve all source content, credits, 88 IDs and five original media files. Their deterministic structural/text/link checks pass; PDFs and visual/human/accessibility reviews remain pending. These later files are not part of the historical U02 offline ZIP. Rebuild with `python -B bn-Beng-BD/tools/build_frontmatter.py m81241 m81242`.

The complete addition source draft is `output/m81244/index.html`: all 3,576 elements, 756 IDs, 129 exercises, 89 supplied solutions, one glossary definition and 50 inspected images. Nine image charts also appear as real HTML tables. Forty unanswered source questions remain unanswered here; their worked companion answers are next. Rebuild with `python -B bn-Beng-BD/tools/build_module.py m81244`; run six non-writing guard tests with `python -B bn-Beng-BD/tools/test_module_guards.py`. This is a complete source draft, not finished U03/AX-1/AX-3 workflow. The authoritative CNXML is under `translations/complete_modules/m81244`; the older `draft_modules` copy is only a preserved historical prefix snapshot.

The complete OpenStax Prealgebra 2e module m81243 includes its title, metadata, learning objectives, eight content sections, all 88 exercises, 59 supplied solutions and seven glossary entries. Its faithful CNXML preserves 2,122 elements, 628 source IDs, mathematical values and 47 original media references. Original diagrams are retained under translations/media; the reading editions use translated text equivalents.

The separate companions cover number sense, place value, number naming/writing and rounding. U01 has 14 worked child tasks; U02A-D add 48. U02E supplies complete worked answers for all 58 final source practice exercises, including the 29 unanswered in the source. Newly authored answers are separate from the faithful source and are not attributed to OpenStax.

The new addition companion is `output/U03A/index.html`, with 14 fully explained diagnostic/practice/exit tasks. Its `answers.html` supplies separate worked answers for all 129 addition source exercises, including the 40 without original answers, 17 explicit block models, 18 phrase explanations and 297 chart cells. Quoted source questions retain their original digits; new answers use Bengali digits and explicitly retain international comma grouping for source comparison. Rebuild with `python -B bn-Beng-BD/tools/build_addition_companion.py`. Structural/math/reproducibility checks pass; new PDF/visual/human/accessibility reviews remain pending.

The compilation contains each faithful source section once, plus the U02 companions. It links to U01 instead of duplicating its companion. Larger international numbers, fractions and decimals in source/reference material are not Grade 2 prerequisites. Bangladesh grouping and child contexts are explicitly separate from the source's international grouping, historical examples, dollars, miles and pounds. No source quantities are silently converted or updated.

## Reading editions and limits

The U02 compilation has a 12-point, 57-page A4 print PDF and a 16-point, 83-page screen PDF under output/pdf. All 140 final-v3 page images were visually checked for readable shaping, tables, math symbols, checkboxes, margins and footers. Exact-hash review records are in u02-visual-qa.json and its per-page records.

These are untagged visual reading copies, not PDF/UA documents or interactive forms. Bengali copy/search text is unreliable: shaped-font extraction includes private-use glyph codes. Use the semantic HTML for text access. The coverage test compares HTML text with PDF layout input before font encoding; it does not certify exact Unicode extraction. Fractions are rendered as a/b, circled labels as (a)-(e), and Unicode dashes as ASCII hyphens.

Source-section headers retain their draft-time review notices. The exact-hash compilation QA receipt records the later completed PDF visual check. Native Bangladesh teacher/editorial review, browser rendering, screen-reader testing and a real printed-copy check remain pending. Browser runtime setup failed before page access; no browser visual approval is claimed.

U01's earlier 9-page print and 13-page screen PDFs and offline ZIP remain unchanged. The U01 ZIP is a historical checkpoint, not a package of current U02 work.

## Sources and canon

Complete assigned source corpora are already acquired and pinned in sources.lock.json: Indonesian A00/program checkouts, corrected A10 v1.0.2 source release (82 module hashes), and the complete canonical OpenStax bundle. The canonical archive has 13,738 files and matches publisher Git tree 7907e4c81d43de1c3b6da173f0eb273c01dc5b55. Large inputs stay ignored under downloads/bn-Beng-BD.

The working Bangladesh usage canon has 22 examples from 18 HTML witnesses, including addition/carrying, the commutative-property name and perimeter wording. Actual drafting/revision/QA consultations and acquisition hashes are in canon/. Government-hosted teacher and dictionary examples are usage evidence, not national curriculum certification. No un-OCRed PDF reference is counted. Some terms remain explicitly provisional in terminology.json.

## Rebuild and package

From the repository root, with the existing Python PDF dependencies and locked source/canon files:

```powershell
python -B bn-Beng-BD/tools/build_math_font.py
python -B bn-Beng-BD/tools/build_u02_edition.py
python -B bn-Beng-BD/tools/check_u02_reproducibility.py
python -B bn-Beng-BD/tools/package_u02.py
```

The edition builder reruns every translated section's structural/math QA before full assembly. Reproducibility checks two fresh small builds against the reviewed bytes, including an unchanged-U01 gate. If PDFs change, inspect the new page images and update exact-hash visual records before packaging; do not treat a successful build as visual inspection.

The offline ZIP is a reading/translation-review snapshot with local fonts, original diagrams, editable translation witnesses, notices and QA records. It excludes large reference corpora, raw consulted canon pages, temporary page images and runtime dependencies. Rebuilding requires the repository and locked local inputs. Every ZIP member, local HTML resource and internal link is checked, and ZIP rebuilding must be byte-identical.

No routine rebuild should acquire sources again. Acquisition scripts are recovery tools only. Never silently refresh retained dynamic reference pages or delete current source archives.

## Provenance

Based on OpenStax Prealgebra 2e by Lynn Marecek and MaryAnne Anthony-Smith; copyright Rice University. Indonesian edition: KokunoYumeto project. Bangladesh translation, text-equivalent figures, companions and expanded answers: Language Allocation, AI-assisted, 2026-08-30-31. Original credits, notices and source model provenance remain in provenance/notices.

Source and derivative: [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/), subject to component notices. Noto-derived fonts: SIL OFL 1.1, with font/merger provenance in assets/. OpenStax and Rice names, logos and marks are not licensed or endorsements. Supplied as-is. Canon references are consulted for usage, not relicensed or redistributed as a textbook. Inputs are never model-training/fine-tuning data.

Resume at NEXT_UNIT.json: U03A addition companion/full worked answers, m81245 subtraction and the remaining collection; new front-matter/addition editions remain queued. The eight-unit child map does not truncate faithful source coverage. Decisions, scope and current boundary are in GOAL.md, DECISIONS.md, STATUS.md and assignment-coverage.json. No publication or remote push has occurred.
