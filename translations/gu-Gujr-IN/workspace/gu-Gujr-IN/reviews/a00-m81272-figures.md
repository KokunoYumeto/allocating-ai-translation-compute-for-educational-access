# A00 m81272 figure localization

Active durable goal, 2026-09-01: complete the full figure-localization workflow for A00 order12 m81272, **Find Multiples and Factors**, without changing the root-owned frozen translation, media/errata JSON, shared dispatcher, library renderer, status, canon, terminology, commits or publication branch. The bounded module work is to inspect all9 actual canonical originals independently, retain the four 1–50 number grids only after verifying that they contain mathematical numerals/highlights rather than English, and replace every one of the five language-bearing figures with source-faithful Gujarati native HTML/MathML/SVG. The helper must expose `render_figure(filename, alt, unique_id)` and namespace every SVG ID from `unique_id`. The redraw set is 008 factor/product brackets, 009 factor72 table, 014 prime/composite two-panel table, 203 Frank completed bank table, and AppB011 four-skill/twelve-blank self-check. Preserve exact source numbers, factor pairs, quotient decimals/dashes, prime-only highlights, table dimensions, the blank final right row in014, Frank's completed expressions/results, and every unselected self-check response cell. Do not silently repair source XML or invent responses; use the already-keyed root corrections only as visible/accessible redraw truth.

Workflow required before freeze: reread actual `AGENTS.md` and `USER_INSTRUCTIONS_VERBATIM.md`; bind the authority source SHA, frozen Gujarati SHA, all source media IDs/paths and all nine binary hashes; reread `terminology.csv`, admitted canon examples and the module's actually-read Khan Gujarati factor transcript record before drawing, again while revising, and at output review. Open the originals themselves at useful resolution before implementation and reopen all five language-bearing originals during revision. Produce only small unique artifacts: `scripts/localized_a00_factors.py`, a source-bound QA script, this review plus JSON receipts, and local preview HTML. Verify exact arithmetic independently:8·9=72; all factor72 rows; all factor lists2–20; prime set2,3,5,7,11,13,17,19; Frank's100+15w totals; four skills and12 blank response cells. Test semantic table headers/captions, Gujarati accessibility text, absence of embedded English, unique SVG IDs/references, local overflow behavior, Gujarati shaping, and actual phone/desktop rendering. Record all corrections and uncertainties. The existing translation review's initial claim that every number cell in014 was highlighted was already corrected after pixel review: only prime number cells are gray-teal, composite number cells are white. Compaction may contain stale or compressed claims; reconstruct state from actual files and pinned hashes, not from memory alone.

This module freeze is not completion of the full assignment. After a precise helper/QA/browser handoff to root, continue the queued m81273 four-figure workflow unless root redirects. Coordinator owns the hourly heartbeat and GitHub review branch. No push, merge, release, production claim, large acquisition, cleanup or deletion belongs to this lane.

## Source and canon reads

Actually reread `AGENTS.md`, `USER_INSTRUCTIONS_VERBATIM.md`, the complete frozen translator review, the media/errata mappings, the five relevant source figure contexts, `terminology.csv`, `targeted-examples.md`, `examples.csv` and Std6 Week1 p15 OCR before drawing. During revision and output review I returned to terminology rows T25–T32 and the module review's retained Khan Gujarati factor-transcript evidence. The terminology remains `અવયવ` for factor, `અવયવી` for multiple, `અવિભાજ્ય સંખ્યા` for prime, and `સંયુક્ત સંખ્યા` with the documented divisible-class bridge. The indexed factor transcript recorded by the translator actually uses factor pairs and divisibility with no remainder; the indexed LCM page supports `અવયવી` only at heading/exercise level. I do not claim a fresh direct-body read where the later direct open returned no lines. Std6 p15 supports concise educational command style but does not attest factor terminology. No withdrawn objective-rank claim or Indonesian candidate content is used.

Authority source SHA is `e547be567190fc22617dda6defdfa2d04349dd86584d890221d2d702aff6f214`; frozen Gujarati SHA is `85d41ab551d29636d5505cbfe53724c0e90149d2180646a3fdabeca90d493148`; frozen media/errata JSON SHA is `8d96c5ac6101a9bd39e6df0344a9d9e79d5d80627196cbb7f943e6d0ceb6fcdb`. All remain root-owned and unchanged.

## Actual-image review and redraw decisions

All nine canonical originals were opened individually at original resolution before implementation. The four 001–004 arrays visibly contain only numerals1–50, table lines and highlight fills, so `render_figure` returns `None` only for those exact filenames. The five language-bearing originals were reopened again after browser revision. The recheck confirms:

- 008 contains black `8 · 9 = 72`, two pale-cyan braces, and separate factor/product labels. The Gujarati SVG preserves the two bracket spans and all mathematical tokens.
- 009 has four headers and eight divisor rows1–8. Rows5 and7 have nonintegral quotients14.4 and `~10.29` with dashes in the factor column; there is no divisor9 row.
- 014 is one two-panel table with three columns on each side, a thin center spacer and ten body rows. Only the number cells2,3,5,7,11,13,17,19 are gray-teal; composites are white. The right final row is blank. The factor list for15 is `1, 3, 5, 15`, with no2.
- 203 is Frank's fully completed solution: weeks0,1,2,3,4,5,6,20,x; all expressions and results through `100 + 15x` are filled. It is not the copied Gina alt.
- AppB011 is a four-row skill grid with three unselected response cells in every row. The redraw preserves all12 blank cells and does not select a rating.

The helper `scripts/localized_a00_factors.py` exposes `render_figure(filename, alt, unique_id)`. The three wide tables use semantic headers, captions and source-sized relationships inside labelled horizontal regions. The 014 redraw uses a single seven-column semantic table so the center spacer and paired row alignment do not drift. The only SVG needs no reusable definitions or internal IDs; the outer accessible wrapper still derives its identifier from `unique_id`. All human-language labels use Gujarati/Nirmala-family fonts.

## Source-bound and arithmetic QA

`python gu-Gujr-IN/scripts/qa_a00_factor_figures.py` passes. It binds every source media ID/path to all nine original binary hashes and then verifies exactly5 redraws plus4 mathematical-only originals. It checks8·9=72; all eight factor72 rows; the independently enumerated prime set2–20; prime-only fill count8; the complete factor list for15; all nine Frank rows and `100+15w` totals; four self-check skills and12 blanks. It also rejects multi-letter Latin text in localized figure bodies, requires unique generated IDs and emits three reproducible preview pages.

Final integrated helper SHA is `7968a7163e3cad0b866a5ac4ae9f55a128c8a0e7bf057aa78db74cad0f87e2ea`. QA counts:9 media,5 redraws,4 verified math-only originals,5 unique wrapper IDs,0 unresolved references,8 factor72 data rows,8 prime highlights,9 Frank data rows,12 self-check blanks and7 independent mathematical/model checks.

During root integration, the shared library accessibility gate found that the intentionally blank center spacer in the two-panel prime/composite table lacked a header scope. Root added `scope="col"` to that existing hidden spacer, without changing visible content or geometry, rebound the helper hash above, and reran both source-bound figure QA and the deterministic full-library QA successfully.

## Actual browser review

All five redraws were actually scrolled and inspected at390x600 and1000x600. On phone the document stayed375/375 pixels on all three pages; the table regions were317/560,317/940 and317/650, and both horizontal ends were inspected. At1000 the page remained985/985 throughout. Final geometry at1280 was1265/1265,1280/1280,1265/1265, the middle difference reflecting the absence of a vertical scrollbar. Gujarati and Nirmala font checks passed, localized bodies had zero multi-letter Latin hits, and all generated IDs were unique. The browser receipt is `reviews/a00-m81272-figures-browser.json`.

No arithmetic, labeling or layout uncertainty remains in these five redraws. Gujarati composite-class terminology still carries the shared educator-review qualification already documented by the translation team; this technical figure pass does not elevate it to independently certified terminology.

## Nine-occurrence inventory

| Source media ID | Filename | Mode | Actual check |
|---|---|---|---|
| `fs-id1949566` | `CNX_BMath_Figure_02_04_001.jpg` | math-only | Opened; 1–50 numerals/grid/highlights only. |
| `fs-id1379128` | `CNX_BMath_Figure_02_04_002.jpg` | math-only | Opened; 1–50 numerals/grid/highlights only. |
| `fs-id2320043` | `CNX_BMath_Figure_02_04_003.jpg` | math-only | Opened; 1–50 numerals/grid/highlights only. |
| `fs-id1242400` | `CNX_BMath_Figure_02_04_004.jpg` | math-only | Opened; 1–50 numerals/grid/highlights only. |
| `fs-id2751166` | `CNX_BMath_Figure_02_04_008_img.jpg` | redraw | English factors/product; bracket relationships preserved. |
| `fs-id3369689` | `CNX_BMath_Figure_02_04_009.jpg` | redraw | Four English headers; all8 rows preserved. |
| `fs-id1480189` | `CNX_BMath_Figure_02_04_014_Errata.jpg` | redraw | Six English headers; prime-only highlights and blank row preserved. |
| `fs-id19495660` | `CNX_BMath_Figure_02_05_203_img.jpg` | redraw | Three English headers; all completed Frank rows preserved. |
| `eip-id1164271108221` | `CNX_BMath_Figure_AppB_011.jpg` | redraw | English skill/choice grid;4skills/12blank responses preserved. |
