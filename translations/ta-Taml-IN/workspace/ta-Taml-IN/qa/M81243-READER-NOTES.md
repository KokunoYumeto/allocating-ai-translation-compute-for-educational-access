# m81243 whole-module source-review reader

Date: 2026-08-31. Bounded scope: new `scripts/build_m81243_review.py`, `assets/m81243-review.css`, `reader-m81243-review/`, and this note. The assembled translation and all source SVGs remain unmodified. This is an HTML-only source-review draft, not a completed learner workflow. No recovery or missing-answer companion is included. No PDF, EPUB, browser service, download, commit, or shared builder/style/log change was made here.

## Source and implementation decisions

The builder reads the actual assembled `translation/m81243.cnxml`, not a concatenation invented by the renderer. Its 2,122 nodes and 628 source IDs match the pinned English witness in source order. It retains all eight top-level U001–U008 boundaries, four nested U008 sections, metadata (content ID, title, six objectives, UUID), and seven glossary definitions. The source's U008 outer section has no title: the added navigation/reading heading is explicitly labelled as editorial, not passed off as a translated source title.

The stable helpers in `build.py`, `build_u002.py` and `build_large_number_review.py` are imported read-only. Inherited whole-module figure numbering comes from the English witness, not image filenames. Source math remains semantic MathML; its complete ordered signatures are compared before/after rendering, including fractions, spaces, bold style, punctuation and currency text. All 49 source lists are retained: plain/default and explicitly bulleted lists use bullets; stepwise Arabic lists use ordered numerals; existing circled tokens remain visible in circled lists even where the source's `number-style` says Arabic or is absent. No extra competing list marker is shown. Default source emphasis renders strongly, while explicit italics and bold remain distinguished.

CNXML paragraphs containing a media block or list become a same-ID paragraph group with valid HTML block children; this avoids parser reparenting and dropped source boundaries. Every nonempty CNXML text/tail fragment is checked within its nearest source-ID boundary. The separate metadata values are also checked in the rendered metadata section. No source text is replaced by a diagram description or an editorial warning.

The reviewer banner explicitly distinguishes a whole-module source review from a complete course or independently usable recovery workflow. All 59 source solutions are visible; the 29 exercises lacking a source solution have explicit separate missing-answer notes. New companion answers are not silently substituted. The source's confidence advice and teacher-dependent advice remain visible as source material, but the confidence checklist receives a clear adjacent warning that it is not evidence of mastery.

## Canon consultation at this stage

The actual already OCRed canon pages 11, 12, 20 and 175 were read and their complete page images inspected during the immediately preceding companion work in this same drafting/revision chain. The current reader retains those decisions: separate period/place/contribution roles, the international group names and values rather than conversion to the canon's Indian groups, `முழு எண்கள்` distinct from `முழுக்கள்`, and the source-specific gloss of `திட்ட வடிவம்`. No new claim that the provisional international group terms are canon-attested is introduced.

For the now-integrated rounding tables, reread actual OCR page 31 and then inspected its full PNG. Visually confirmed examples 1.11–1.12: 8,436 → 8,400 and 78,794 → 79,000, target place versus the digit to its right, and the zeroing step. OCR corrupts digits and comparison operators. These are register/procedure checks only; the builder neither replaces the source's different rounding examples nor invents source diagrams. Original U006 raster/mark discrepancies remain documented in the existing U006 translation/figure notes, not silently reinterpreted here.

## Tables and diagrams

All 47 media occurrences are rendered, using 46 actual local SVG assets. Every occurrence receives a rendering-copy ID namespace `mr-svg-<source-media-id>--<original-svg-id>`. Internal `href`, `url(#...)`, and ARIA references are rewritten using the same map. Source SVG files and packaged raw SVG asset copies are unchanged. The manifest records every per-occurrence mapping. This prevents the U003 011 chart, reused in U007, from producing duplicate DOM IDs.

The two U003 charts and U007's reused chart each receive a complete vertical 15-row table of place, digit/blank and digit contribution. These rows are derived from the actual identified SVG text cells and verified positions, not merely from an alt or a total. Blank positions remain distinct from an explicit 0. Each dense SVG retains its intrinsic 1,082-pixel width and a keyboard-focusable horizontal scrolling region; other diagrams retain their actual intrinsic widths (344–1,840 pixels) instead of being shrunk into illegibility.

The AppB self-check gets a separate semantic HTML table derived from the actual SVG's four headings, six skill texts and 18 identified blank rectangles. It has six skill rows and three blank response cells per row, proper column/row header associations, and screen-reader-only descriptions of blank cells. It is a static alternative, not a form or working checkbox interface. No responses are prefilled or submitted. Both the source self-check section and this alternative explicitly warn that confidence is not a mastery test.

All eight structural CNXML tables remain HTML tables:

| Source ID | Declared columns | Actual/rendered data columns | Source rows, including source header if present |
|---|---:|---:|---:|
| fs-id1714120 | 5 | 5 | 5 |
| fs-id1785447 | 5 | 5 | 5 |
| fs-id1171100715908 | 3 | 2 | 5 |
| eip-659 | 3 | 2 | 5 |
| eip-493 | 3 | 2 | 4 |
| eip-379 | 3 | 2 | 4 |
| eip-695 | 3 | 2 | 4 |
| eip-596 | 3 | 2 | 4 |

The six declared-three/actual-two cases have a visible discrepancy note. Their two data entries per source row are preserved, and the reader-added descriptive column headings are explicitly identified as additions. The two five-column U002 tables retain the source headers, cell alignment and row-header associations. Rounding media stays inside its proper table cell and in source order, including nonlexical 01/03/02 asset ordering.

Figure captions preserve source text and source numbering: 001 → 1.1; 002 → 1.2; 004 → 1.3; 005 → 1.4; 011 → 1.5; 019/020/021 → 1.6/1.7/1.8; the U007 figure `eip-id1170196618448` → 1.9. The U004 introductory figure and AppB self-check remain unnumbered.

## Offline scope and safe output

The 52-file output contains HTML, its dedicated stylesheet, the bundled TamilBook font and OFL notice, 46 original SVG assets, LICENSE.txt, and a deterministic manifest. The displayed SVG copies are inline. There is no script, form, remote font, remote image, CSS import, account dependency or analytics call.

The two source OpenStax links remain exact external links with adjacent text marking them as optional, unbundled internet resources. The U001 referenced “Number Line—Part 1” worksheet is explicitly not bundled and is not made a reading prerequisite. These external resources were not fetched or represented as tested. Contributor/license/source-pin links remain attribution links, not runtime dependencies. The source author/contributor credits are reused with guarded, visibly truthful scope wording.

Output is fixed to the isolated `reader-m81243-review` directory. Resolved output and dependency paths are checked, including symlink/path escape protection. Unexpected output files cause refusal rather than deletion or silent packaging. A write refuses to start if the available disk would fall below 100 MiB; current output is about 1.02 MiB. `--check` performs no writes. No cleanup/deletion was performed.

## Checks actually run

Commands from the workspace root:

```powershell
& '[local-home]/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe' ta-Taml-IN/scripts/build_m81243_review.py
& '[local-home]/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe' ta-Taml-IN/scripts/build_m81243_review.py --check
```

Both passed. Each run also compares two independent in-memory payload builds byte for byte. A further rebuild followed by `--check` passed; the HTML hash did not change. The manifest covers all actual input/output hashes; it excludes timestamps and machine-dependent paths.

Positive checks:

- 628 source IDs retained once, in original order; all source section boundaries retained.
- 1,653 unique document IDs; every local fragment, SVG use/marker reference, ARIA reference and table `headers` reference closes.
- 249 source MathML expressions retained with identical content and order; 88 exercises and 59 source solutions retained; 29 no-solution markers correspond to actual absent source solutions.
- 47 inline SVG occurrences, 46 unique packaged assets, three full 15-row alternatives, eight source tables, and 18 blank confidence cells.
- Independent lxml HTML parsing retained the same ordered 1,653 IDs, 47 SVGs and 249 MathML elements. It independently checked 573 scoped source text fragments and all 49 source list IDs.
- Independent inspection of every manifest occurrence map verified that all SVG ID references close within that occurrence, original viewBoxes are retained, and the two reused 011 namespaces are disjoint.
- Every generated output file matches its manifest hash; local font and license resources are present. No shared-builder/style diff was introduced.

Twenty in-memory negative cases are required to be rejected: unknown tag; unknown list style; unsupported source attribute; each of a five-column and two-column table declaration mutation; a missing actual table cell; changed chart internal 0; shifted chart digit position; a prefilled confidence cell; remote SVG use; media path escape; broken document link; duplicate document ID; missing objective ID; altered objective text; reused SVG ID collision; changed source MathML; missing local font; remote CSS import; removed confidence warning. These mutations do not write or modify source/output files.

During development, the removed-warning negative case initially raised a raw KeyError. Added an explicit required-semantic-ID check so missing chart/warning structures now fail with the same deliberate validation error as other unsupported mutations. This did not require changing source content.

## Review handoff and limits

This stage did not run a browser, screenshot test, screen reader, PDF, EPUB, native-language review or learner validation. lxml parsing and intrinsic-width checks are not substitutes for visible layout testing. Root owns browser/viewport and any later format work. The draft banner retains that limitation; do not describe this as a finished learner edition or a completed full-course goal.

Representative anchors for root review: `mr-metadata` and `para-00001` (metadata/objectives); `fs-id1714120` (five-column source table); `fs-id1171100715908` (U004 two-data-column discrepancy); `eip-659` and `eip-379` (rounding tables); `fs-id2296006` and `eip-id1170196618449` (reused U003 SVG); `mr-eip-id1170196618449-table` (its 15-row semantic alternative); `eip-823`, `mr-confidence-warning`, `mr-confidence-table` (self-check caveat and blank table); `mr-glossary` (seven source definitions).

## Final fingerprints

- Assembled source `translation/m81243.cnxml`: `699a12c0c3db042fe83262b7f38b6bc1504bad7a660478f090106593f7ced959`.
- Builder: `c8ae452d56c29e1c55696a3c8de61c979b757472e220552d3578b332fb9e410e`.
- Dedicated CSS: `3c11e231769cff9051c5e10e0c7ebfc856cf8abcb1dfbd060f1aeca8b3767bd5`.
- `reader-m81243-review/index.html`: `02205c4b475a555acc9d42237049360226d0e1f2281ed51f635be69ec4990729` (447,827 bytes).
- `reader-m81243-review/build-manifest.json`: `11f265dd996e856feee8e1e4b7032c72bd32954669ed1394daace3e14a03a5da` (103,181 bytes).

The manifest is the complete asset/input provenance ledger for this isolated build. Existing per-unit translation/figure notes remain the evidence for their earlier linguistic and raster decisions; this reader does not overwrite those records.

## Root verification and superseding fingerprints — 2026-08-31

The main task read the complete builder/CSS/notes and strengthened its source gate: the actual assembled-file bytes must equal the candidate independently assembled from both full witnesses, with all gate inputs hashed before/after rendering. Per-node child counts now supplement tag preorder. A same-preorder reparenting negative fixture brings this source reader to21negative cases. No source or rendered HTML prose changed.

Phone review initially measured718px document overflow at375px client width. The18absolute-positioned hidden blank-cell labels in the confidence alternative lacked a positioned scrolling ancestor. Added only `position: relative` to `.table-scroll`; reloaded and measured375/375. Inspected the static confidence table:6rows,18blank response cells, all45rows across the three place-chart alternatives. The full47SVG/249MathML inventory and loaded Tamil font were observed. This targeted check is not a full visual review of every wide figure or assistive-technology behavior.

Current builder SHA256 `801debf7ca48aba09362b40f787cf0bea6477b0db64c624eeafc067b5711e6bb`; CSS `cddf8be56be988228a1ed7dcaeb5e4da669e6fb231bb09c2fc9b6ab6edd90cf2`; manifest `9173f1347b9c77df3ca3d736ddbb79b02ca5ce2dee50cd9ab3dd23569c56c01e`. The447,827-byte HTML remains `02205c4b475a555acc9d42237049360226d0e1f2281ed51f635be69ec4990729`. The earlier fingerprints above document the author handoff, not current builder/CSS identity.

The source-only reader remains deliberately separate. The new companion integration is `reader-m81243-learning`, documented in `M81243-LEARNING-INTEGRATION.md`; this folder is not silently promoted or overwritten by that build.
