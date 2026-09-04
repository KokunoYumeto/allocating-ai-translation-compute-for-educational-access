# U003–U005 isolated source-review HTML

Status, 2026-08-31: bounded source-review draft, not a completed learner edition or full course. Recovery companion pending. The source exercises' solutions are intentionally visible; the Tamil cover states this. No PDF or EPUB was built. Existing U001/U002 builders, styles, readers and shared logs were not edited by this task.

## Inputs and canon consultation

The reader integrates the three actual translated sections in their English source order, without merging their boundaries:

| Unit | Source boundary | Translation |
|---|---|---|
| U003 | `m81243#fs-id1883656` | `translation/m81243-fs-id1883656.cnxml` |
| U004 | `m81243#fs-id1321580` | `translation/m81243-fs-id1321580.cnxml` |
| U005 | `m81243#fs-id1339359` | `translation/m81243-fs-id1339359.cnxml` |

The English witness is `provenance/m81243.en.cnxml`, pinned to OpenStax commit `38cae454e644abf9f0a623e876994553881597c9`. The existing Indonesian witness/attribution pin remains `3de9207f56f8b5c57c017abf973fb04e00d740f1`. Source-translation and figure-specific decisions are separately documented in the U003/U004/U005 notes; this integration does not replace those reviews.

For integration and QA I reread the actual already-OCRed canon pages 20 (printed 14), 11 (printed 5) and 12 (printed 6), along with `canon/README.md` and `terminology.tsv`. The actual page images had also been inspected during these source-figure tasks. Page 20 supports the இடமதிப்பு / இலக்கம் distinction and step/solution register. Pages 11–12 support the number-name presentation and separated tens/unit words used by the translator. Their Indian grouping is not authority to change the source's international grouping. OCR operators and digits are visibly unreliable and were not adopted as mathematical evidence. International scale compounds and இடமதிப்புத் தொகுதி remain the explicitly provisional choices recorded in the ledger, not newly claimed canon attestations.

## Rendering decisions

- `scripts/build_large_number_review.py` imports only stable helper functions and subclasses `build_u002.Renderer`; it does not call either shared builder's main workflow. The new stylesheet is isolated as `assets/large-number-review.css`.
- All 141 source IDs retain their exact order and section membership. All 55 translated MathML trees retain tokens, attributes, hierarchy and order. English/Tamil `mn`/`mo` values and dollar-bearing `mtext` are checked against the English witness; source units/currency are not converted.
- Source lists remain one bulleted list, two Arabic-numbered procedural lists and seven ordered circled-label lists. Literal ⓐ… labels are retained, with automatic duplicate list markers suppressed. Italics, the un-emphasized term, token spans, bold MathML and block media inside CNXML paragraphs are handled explicitly.
- Figure numbers come from numbered figures in the whole English module, excluding `unnumbered` figures. `CNX_BMath_Figure_01_01_011` is **1.5**, not 1.11. U004 `eip-id1168289680652` remains unnumbered. These three source sections contain no prose `caption` elements; no invented caption prose is added. The numbered source figure receives the faithful figure-number caption, and every medium exposes its exact translated source alt as a full visible description and SVG description.
- The U004 table `fs-id1171100715908` declares `tgroup cols="3"`, but each of its five actual rows has **two** `entry` elements. The source XML is unchanged. HTML renders those two actual data columns, not a fabricated empty third column. A visible Tamil editorial note explains the discrepancy, and the two added column headers are explicitly identified as reading aids.
- The eight SVGs are inlined so the bundled TamilBook font applies. Their original geometry and IDs remain; only rendering-copy description/accessibility attributes and fixed intrinsic width are set. Standalone SVG assets are also included in the offline folder. Widths in source order are 1082, 1082, 1000, 1280, 620, 1440, 1840 and 1440 px. Each image is inside its own keyboard-focusable horizontal scroll region. No dense chart is shrunk to fit the page width.
- Shared complete contributor credits and licenses are retained. Guarded, explicit replacements change U001-specific wording to these three source sections and state that this reader has no recovery companion yet. No new OpenStax endorsement or native-speaker approval is claimed.

## Full U003 semantic alternatives

Each dense source chart has a vertical HTML table with all **15** place rows, from power 14 through power 0, and columns for place, digit and digit contribution. Row/column headers have explicit associations. These are labeled as new text alternatives derived from the picture, not original source tables.

The builder reads each actual SVG's `*-place-pN` and `*-digit-pN` text nodes, validates their canonical column coordinates, aligns each with its power and computes contributions from the digits. It does not derive the rows from an answer total. The fixed source digit strings are only independent validation expectations; totals are computed from the extracted positions.

| Source media | Generated table | Checked source geometry |
|---|---|---|
| `fs-id1339846` | `lr-fs-id1339846-table` | 8 leading blank cells; digits `5 2 7 8 1 9 4`; sum 5,278,194 |
| `fs-id2297687` | `lr-fs-id2297687-table` | 7 leading blank cells; digits `6 3 4 0 7 2 1 8`; sum 63,407,218 |

Blank cells display `காலி` and a dash for an unassigned contribution, not an invented zero. The explicit zero at `u003-f012-digit-p4` has digit 0 and contribution 0. The visible explanation distinguishes these cases. Table row IDs are `lr-<source-media>-p14` through `-p0`; for example, `lr-fs-id2297687-p4` is the zero's row.

The U005 SVG/source alternatives preserve the actual source `073` thousands group in figure 017 (the English source alt typo is documented separately), the first period's leading blank slots, and the nine explicit zeros in figure 018. The whole section's source number values are not silently regrouped into lakh/crore notation.

## Verification performed

Commands:

```text
python ta-Taml-IN/scripts/build_large_number_review.py
python ta-Taml-IN/scripts/build_large_number_review.py --check
```

Both passed. Every run compares two independently constructed in-memory payloads byte for byte. Check mode compares the exact expected output file set and bytes without writing. Unknown existing output files cause a refusal instead of deletion. Build writes are confined to `reader-large-numbers/`, with a >100 MiB post-build free-space guard. Free C: space observed during this pass was about 10.35 GB.

Verified totals: 455 unique document IDs, 141 source IDs, 55 source MathML roots, 8 inline SVGs, 15 source exercises, 1 source table and 2 complete chart-alternative tables. Every fragment link, SVG marker reference, ARIA label/description reference and table header reference resolves. Local stylesheet/font references close inside the package; remote runtime resources, event handlers and active content are rejected. External attribution links are links only.

Nine deliberate in-memory mutations were correctly rejected: unsupported element, unsupported list style, an unreviewed change to the table's declared column count, changed interior zero, a shifted SVG digit column, unresolved document link, duplicate document ID, changed source MathML number and remote CSS import. An initial duplicate help-ID found by the validator was fixed before any successful output write.

An independent lxml HTML parse retained all 455 IDs in XML order and the same 8 SVG / 55 MathML / 3 table element counts. It also confirmed 15 body rows per chart alternative, correct totals, five two-cell source-table rows, one `படம் 1.5` caption, source list types and intrinsic SVG styles. This is a parser check, not browser rendering or HTML5 conformance certification.

The offline folder has 14 files and 538,320 bytes total at this revision, including the manifest. HTML is 113,342 bytes. No temporary preview server remains running from this task.

## Hashes and remaining review

| Artifact | SHA-256 |
|---|---|
| `scripts/build_large_number_review.py` | `4ae9d2addd041136d62eb41b9c33e6ba27b049b29d7d5ed67f41ea50071e464e` |
| `assets/large-number-review.css` | `a0e619950af7a18c1dc04d53abb65baa477e6992623001a09e748c8b896b0de7` |
| `reader-large-numbers/index.html` | `08c71549dae2bfe98e200fbd89cd56614a2ebcd368c7ea42cc98b213fd3ba9eb` |
| `reader-large-numbers/build-manifest.json` | `10bf5689b7faa20ae8b59905ce261bea152c1a6841607c61cf1bdb33c97b5ac1` |

The manifest records all input hashes and every output payload hash; source and figure notes retain image evidence.

Browser skill use did not yield a connection: initial URL selection reported “No browser is available”; the documented troubleshooting and a single availability listing returned an empty list. No alternate browser-control workaround was attempted. Thus this subtask makes **no desktop/mobile visual-fit, scroll-interaction or assistive-technology certification claim**. Parent task will inspect the reader using its available connection. Representative targets: `#fs-id1883656`, `#lr-fs-id1339846-table`, `#lr-fs-id2297687-p4`, `#fs-id1171100715908`, `#fs-id2903601` (U005 073), and `#fs-id1345376` (U005 zero-filled groups).

Native-speaker/editor review, final independent-learning routes and recovery companion remain outside this HTML-only source-review handoff. The full assignment remains ongoing.
