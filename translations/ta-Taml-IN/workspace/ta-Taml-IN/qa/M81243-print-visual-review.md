# m81243 print PDF — independent visual review

Latest completed review: see “Completed full-overview review of candidate 881380” below. It covers all 223 pages at overview resolution and 95 individual-page views; changes are required before final approval.

## Status and boundary

2026-08-31. **Initial representative review: changes required. Full-page review is pending a revised export.** The export owner explicitly requested that the reviewer stop further sample rendering after reporting the defects below, because this PDF will be superseded. This is not approval of the 173 pages, the screen PDF, or the complete Tamil wording.

Read-only scope: the integrated print PDF, its actual temporary HTML/CSS, and source SVG evidence for the observed defects. Read the PDF skill completely. Used bundled Poppler for rasterization and bundled Python/pypdf for page inventory/text lookup. Did not invoke the PDF marker, author/re-export a PDF, edit source content, edit builders/CSS, download software, or delete files. Only this report and scratch PNGs under `tmp/pdfs/ta-m81243-independent-print/` belong to this review.

## Exact initial export

Paths are relative to the workspace unless prefixed `ta-Taml-IN/` below.

| Item | SHA-256 |
| --- | --- |
| `ta-Taml-IN/output/pdf/ta-Taml-IN-A00-m81243-print.pdf` | `679422d965593ea3a682730af934423a005c8576627fafcb4659fd1138a66134` |
| `tmp/pdfs/ta-m81243/m81243-print.html` | `07d1dc295720df1d905afdda460952768f4d9c4d54422ca59c127f2f00fd3398` |
| `ta-Taml-IN/assets/m81243-pdf.css` | `57d9cc253f6c4be75e3f13cad9e2c46fffe3ea664fc743073038248b4a92f66f` |
| Upstream integrated learning HTML (export receipt) | `cfe15686bb3e3cd2a2f428c7b1e2529553ad85326eeb9ee992db16a8184db7c2` |
| Export builder (export receipt) | `125224ecfe5d49ffe1540a595ca8d4f9de40e46d78b3b76991bd0e6b125a3cbf` |

Independently read page boxes: **173 pages; 151 A4 portrait and 22 A3 landscape** (rounded point dimensions 595×842 and 1191×842). The source PDF hash was checked before and during rendering and remained the hash above. Printed folios matched sampled physical PDF page numbers.

## Actual representative coverage

Rendered and inspected these **30 complete pages** at a maximum dimension of 1400 pixels: **1, 3, 6, 44, 77, 79, 80, 88, 108–116, 122–128, 139, 140, 165, 168, 169, 173**. PNG names are `initial-pNNN.png`. No contact sheet was used as a substitute for these complete-page views. Page text was inventoried more broadly to locate material; extraction alone does not establish visual correctness.

Coverage includes cover/contents, module route and checkpoint table, companion international-scale table, wide fifteen-place chart and semantic alternative, five-period number-name diagram, rounding procedure tables including carrying, all four U008 assessment block models, source confidence checklist and semantic alternative, S20/S21 and S26–S29 answer material, and the last credits page. It excludes an all-page raster review; page 2, the number-line pages, much of the earlier companions, and many source/answer pages have not been visually inspected here.

## Actionable findings in the initial PDF

### R1 — P1: a single assessment model is fragmented across pages

**Pages 123–124; U008 exercise `fs-id1224988`, media `fs-id1393361`, SVG `CNX_BMath_Figure_01_01_201_img.svg`.** Page 123 displays five hundreds squares and six tens rods. The single ones square appears by itself at the top of page 124, followed by the description and supplied answer 561. The preceding question identifier is on page 122. The apparently complete model on page 123 therefore visually represents 560 unless the learner realizes that a lone shape on the next page belongs to it.

This is **fragmentation, not deletion**: the first quick report suspected clipping, but the next-page render explicitly located the missing unit. The actual SVG has viewBox `0 0 344 540` and its ones square at `(251,510)`, size 14×14; the mathematical geometry itself is correct. Preserve the entire model as an indivisible printed graphic and limit its print height/width to the available page box. Keep its identifying context with it where practical. A text-content presence check alone cannot catch this defect.

### R2 — P1: the rounding replacement instruction is visibly clipped

**Page 110; table `eip-493`, media `eip-id1168287065587`, SVG `CNX_BMath_Figure_01_01_035_img-02.svg`.** The last row's right-hand red instruction shows only `0-களால்`, with the rest cut off at the printable right edge; the complete source instruction is `0-களால் மாற்றுங்கள்`. The SVG also extends beyond the right table border. Its viewBox is `0 0 780 285`; the source text and geometry are present. The screen minimum SVG width appears to survive into the narrower print table cell.

Reset print SVG minimum width, constrain the rendered viewport to the cell, and recheck the full instruction, both arrows/bracket, and 23,658 → 23,700 at readable size. Inspect all other A4 table diagrams for the same inherited constraint; the full labels in the sampled wide carrying diagrams on pages 112/116 do not prove the A4 cases safe.

### R3 — P2: paper navigation lacks destination page references

**Cover/contents pages 1 and 3, route table page 6, and sampled remedial/answer links.** The contents list numbers are entry ordinals, not printed destination pages. Link labels such as the repeated explanation/answer headings have no page reference. The paper reader cannot click them, and repeated D/P/M/T headings make manual lookup ambiguous.

Add print-only destination-page labels to the contents and internal learning/source/answer routes, with a converged destination map verified against the final pagination. Preserve clickable PDF links as well; page labels must supplement rather than rename the source targets. This is a paper-navigation issue, not a claim that the existing HTML/PDF hyperlinks are broken.

### R4 — P2: semantic tables and captions are poorly separated

**Pages 79–80; table `mr-fs-id1339846-table`, media `fs-id1339846`, figure `CNX_BMath_Figure_01_01_011`.** The semantic fifteen-place alternative starts with four blank-place rows below the large diagram on page 79, then continues on page 80. Its total 5,278,194 is repeated at the foot of both fragments because the table footer repeats. The first fragment thus places the whole-number total directly after only empty-place rows. Keep the fifteen data rows together where possible, and make the total a nonrepeating final row. Text lookup places caption “படம் 1.5” on portrait page 81 rather than on either of the diagram/alternative pages; the page-79 render has no caption. Page 81 was not separately rendered in this sample. Promote the wide layout wrapper to include the containing source figure/caption where applicable.

**Pages 139–140; `mr-confidence-table`, source media `eip-id1165721974707`.** The intact source checklist graphic is readable, with six skills and eighteen visibly blank response cells. Its semantic alternative then splits one skill on page 139 and five on an otherwise almost empty page 140. Keep this small six-row alternative together; do not remove either source skills or response cells. The visible warning that confidence is not mastery is present on page 139.

### R5 — P3: isolated navigation/credits produce nearly empty pages

**Page 77** contains only the return-to-contents link and a rule. **Page 173** contains only the final contributor, “Becky Wheelock, San Diego City College.” Avoid orphaning these trailing blocks in the print stylesheet. Preserve every credit and relevant navigation route. This is a layout economy/polish finding, not missing content.

## Positive observations, restricted to inspected pages

- Cover warnings and scope are visible; the page-6 route/checkpoint table and page-44 international group-value table have readable, nonoverlapping content.
- The page-79 fifteen-place diagram preserves its labels, leading blank positions, and digits 5,278,194. The page-88 five-period diagram visibly preserves both occurrences of 098 and its Tamil group/name labels.
- The carrying diagrams on pages 112 and 116 visibly retain 9 + 1 = 10, the relevant place labels, arrows, replacement zeros, and final 4,000 / 30,000.
- U008 models 202/203 on pages 125/126 visibly retain 3H8T4O / 4H0T7O. Model 204 has 6H2T0O on page 127; its description is on page 128. Model 201's split is R1 above.
- Sampled S20/S21 and S26–S29 text, mathematical expressions, headings, and continuation material are legible. This is not a new audit of every answer or a native-language review. The original independent content/answer reviews remain separate evidence.

Tamil characters look formed rather than missing-box glyphs in the sampled raster views. pypdf text extraction inserts NULs into some Tamil syllables; that extraction defect is not evidence of a visible missing glyph. The export owner is separately developing a full text/geometry oracle and reported an HTML namespace problem in that oracle's input handling. This report neither claims nor substitutes for its eventual result, PDF/UA conformance, assistive-technology testing, or actual printer testing.

## Handoff / next review

All R1–R5 findings were sent promptly to the export owner. The owner accepted the actionable layout findings and is revising print-only sizing, figure/table page breaks, footer repetition, and paper destination labels. **No fix is marked resolved until a revised PDF is rendered and inspected.** Initial raster work is paused at the owner's request; do not spend a full 173-page review on this superseded candidate. Resume with the new exact hash, recheck R1–R5 and affected neighbours first, then perform and record the complete-page layout review of that final candidate.

Scratch renders were retained; no cleanup was authorized. This bounded review does not close the whole language-allocation assignment.

## Revised candidate — targeted recheck (2026-08-31)

This addendum supersedes the defect status only for the candidate below. It preserves the initial candidate's observations and hashes as history. **No all-page approval is claimed.** The handoff described 220 pages, but independently reading the actual PDF gives **223 pages: 201 A4 portrait + 22 A3 landscape**. Page 220 starts the credits; page 223 ends them. The discrepancy was reported to the export owner.

| Item | Exact revised value |
| --- | --- |
| Print PDF SHA-256 | `88138014731b35f801b716ea214254c23b2b2fa7bc107b64d1a64e7eeac24a8b` |
| Print PDF bytes | 5,011,799 |
| Temporary print HTML SHA-256 | `01cbe88854ad18b042af6f143158e6b4e72284cc7d050bc960ac70a95ec88850` |
| Temporary print HTML bytes | 999,202 |
| Print CSS SHA-256 | `9afe8cb741d2cfa28c61d62d96fdd4a29209d27b57564cfaabc806d55306b399` |
| Export receipt SHA-256 | `e9fd54cf8d16f2f678d3951b62eeb5d5e5127e22ffa8e08d2e12dc928a16c3d3` |

Rendered and inspected **28 complete pages**, maximum dimension 1600 pixels: **1–4, 7–8, 99–102, 104–105, 137–138, 140, 147–148, 151–155, 170–174, 223**. New PNGs are separate, under `tmp/pdfs/ta-m81243-independent-print/candidate-881380/`; initial PNGs were not overwritten. The PDF hash was checked again after these renders and remained unchanged. No PDF authoring/marker operation occurred.

### Rechecked defect status

- **R1, resolved for the graphic:** page 152 contains the complete U008201 model together: five hundreds squares, six tens rods and one ones square, followed by its complete description and supplied solution. No shape is severed across pages. Also inspected the full models on pages 153–155: 3H8T4O, 4H0T7O and 6H2T0O. Their geometry and descriptions fit. A lower-priority context-separation issue remains: exercise `fs-id1224988` is at the bottom of page 151 and its model starts page 152; the next exercise identifier similarly appears below the preceding model page. Keeping each exercise identifier with its first graphic would improve paper clarity, but the former misleading split of a single mathematical model is fixed.
- **R2, resolved:** page 138 contains the entire 035-02 graphic inside the table cell, including `0-களால் மாற்றுங்கள்`, both red arrows, the bracket and 23,658 → 23,700. Page 137's place/underline stages are also intact. Carrying graphic 036-02 on page 140 retains the full labels and 9 + 1 = 10; no new clipping was observed in these targeted cases.
- **R3, resolved in the tested structure and visible samples:** all **626 non-skip internal anchors** in the actual print HTML have exactly one page-reference wrapper and one numeric label. Independently compared each number and `data-pdf-target` with the actual PDF named destination: **zero mismatches** across **283 referenced non-skip targets**. The PDF's full **284-destination map equals the receipt map exactly**. The receipt reports stabilization at pass 2; the reviewer checked the final map, not the earlier export passes. Complete contents pages 1–4 and route pages 7–8 show legible, unclipped labels. Visible examples include route start `(ப. 5)`, checkpoint route `(ப. 7)`, large-number R1 `(ப. 52)`, source U003 `(ப. 100)`, and figure 1.5 `(ப. 101)` on page 100. Fixed-width short page numbers leave extra internal space but remain understandable. This check does not claim every label was read from a raster.
- **R4, resolved in all three chart alternatives and the confidence alternative:** all fifteen rows and one final total appear together on pages 102, 105 and 148. Captions 1.5 and 1.9 now remain within the A3 figure sequences, on their semantic-alternative pages 102/148; they no longer land on an unrelated portrait text page. The source confidence graphic is complete on page 172. Page 173 has the entire six-row semantic table with eighteen blank response cells and a visible confidence-not-mastery warning/route. The source self-assessment prose on pages 170–171 and 174 remains legible.
- **R5, partly improved; low priority remains:** the former U002 return-link-only page is gone; page 99 has the return link with substantive U002 content. The final credit is no longer a one-line widow, but page 223 still has just four contributor lines. Optional print economy improvement: reduce spacing or use a print-only multi-column credit layout while preserving every credit. Also retain attention to short note tails and exercise headings at page boundaries (for example the final note line at the top of page 137 and the model identifier at the bottom of page 151). These are not missing content or unresolved mathematical clipping.

### Rotated-label investigation

The export owner reported three chart-label omissions from a text-extraction check. **Visually inspected all three actual chart pages: 101, 104, 147. All fifteen rotated Tamil place labels on each page are present, readable and unclipped.** Period headings and digits are intact: pages 101/147 have eight leading blank positions followed by 5,2,7,8,1,9,4; page 104 has seven leading blanks followed by 6,3,4,0,7,2,1,8. These are the correct original digit positions, with no Indian-grouping substitution. This establishes visible label presence, not the correctness of Poppler's reading order or assistive extraction. The extraction discrepancy still requires the owner's separate oracle investigation; do not describe it as a visible missing-label defect on this evidence.

### Revised handoff

No new high/medium-priority visual defect was found in these 28 targeted pages. The prior high-priority model fragmentation and instruction clipping are resolved in this exact candidate. Remaining sampled findings are low-priority context/spacing issues described above. **195 pages have not been visually reviewed for this candidate.** Earlier candidate views cannot be counted toward this candidate's complete coverage because pagination and typography changed. Full-page layout review, the independent text/geometry oracle, actual printer testing and native/AT/PDF-UA review remain separate unfinished evidence; the 223-page file is not approved wholesale here.

## Completed full-overview review of candidate 881380 (2026-08-31)

**Changes required; this candidate is not approved as defect-free.** This section supersedes the earlier “195 pages not visually reviewed” coverage limit, but not the historical findings. Every physical page **1–223** was actually viewed in central contact sheets **contact-01 through contact-56**. Each contact contains up to four complete page thumbnails. Questionable/detail pages were then opened individually; a contact overview is not a full-resolution sentence-by-sentence review.

In addition to the previously listed 28 individual pages, individually inspected these **67 complete pages** from the central maximum-1200-pixel rasters: **18, 19, 30, 32, 44, 45, 53, 65, 66, 78, 90, 91, 93–98, 109–112, 114, 115, 117, 119, 122, 125–133, 135, 136, 139, 141–144, 179–182, 185–190, 195, 196, 204, 205, 208, 209, 211, 212, 214–218, 220**. Thus this candidate has **223-page overview coverage and 95 distinct individual-page views**, not 223 individual full-size views. The 30 views of the older 679422 candidate are excluded from these counts.

The current review only edited this report. Central rasters were read-only; no new PDF export, marker operation, source/CSS/builder edit, download or cleanup was performed. The previously running read-only probe process (session 22855) completed; its collected result is recorded below. No process remains blocked and no additional probes were started after the finalization request.

### Final candidate identity and raster evidence

The final collected pre-rebuild PDF and temporary HTML hashes remained **88138014731b35f801b716ea214254c23b2b2fa7bc107b64d1a64e7eeac24a8b** and **01cbe88854ad18b042af6f143158e6b4e72284cc7d050bc960ac70a95ec88850**, respectively. The candidate's original CSS remains the earlier **9afe8cb741d2cfa28c61d62d96fdd4a29209d27b57564cfaabc806d55306b399** snapshot. The owner subsequently patched live CSS/assets/readers and began another export; those live files must not be treated as this candidate's inputs. The owner reports retaining the old PDF as `tmp/pdfs/ta-m81243/reviewed-print-881380.pdf`; that preservation copy was not independently rehashed by this reviewer.

All **279 central PNGs** (223 pages + 56 contacts), **39,533,777 bytes**, were SHA-256 fingerprinted before and after this review: **zero changed files**. Aggregate manifest SHA-256: **530fa7bceb698036a73dba254d2ffc0ccddcacbd87f4bfab7d1b9a9e130f0c43**. Reproduce the manifest by sorting the 279 basenames lexicographically and concatenating UTF-8 records `basename<TAB>lowercase-sha256<LF>`, with a final LF. This records exact raster-set identity without claiming that the raster generator's interrupted receipt completed.

Selected individually viewed evidence hashes:

| Central raster | SHA-256 |
| --- | --- |
| page-090.png | `f4f4a15044a6063e7564a8f6ec0d1ac0af23c59b0b7dc853046b4c189c786c61` |
| page-065.png | `8536693cf8bfc2135c133655f6b016d4c44f59df652877b0ca00829820b0da23` |
| page-066.png | `3efd146a932306e64f23ce80249bbc7dc0e1d46c2dfd7f8bc7d9cd1eff09b477` |
| page-188.png | `ac67d32c33adae14a67128814cea4ea8d0936f9b71c9bc7643eea4ea99539105` |
| page-189.png | `3abb4032639dc89fa148adc2de05ff0599d3d90c4d8ad99df47a1e75f9ebbbd1` |
| page-125.png | `08d13d5aa1502758423733aba47f1257a009db69996a9a6bf60d6a98ccf3bd91` |
| page-144.png | `186967adf0844e5672ff3c94b02bbdfdc82491e673c06f78efaaacd2092a913b` |
| page-211.png | `52a576a6869ace413ae8eabfa93e4cbac819e5f68331f4047a9e6c0046cdce96` |
| page-212.png | `023927490b393fa3633ca6fb9e319b2461b1821ddb5044dec680cb96af26865d` |
| page-218.png | `e1b3d4b7af545e82b8d68d15ba7bec94a2d01c3afaea0dd004891f1e9bb1c2bd` |

The collected automated receipt `73a3dad9aaa3d9702d5370db648700918224532894a9e1111feb8163eb89202a` matched this print PDF but contained **zero raster/contact entries**; do not claim it supplied the raster manifest. The reviewer fingerprint above is separate. The dual-profile export receipt at the collected snapshot was `3eb07c976194aa182fa207b41e46ce31c026d326dbadaa083c4afe51b2fb1922`; later exports supersede that receipt.

### New actionable findings

**R6 — P2, source diagram direction missing: page 90, Figure 1.1, media `fs-id2316516`, `assets/number-line.ta.svg`.** The upper line labelled “பெரிதாகும்” has no right arrowhead. The upper leftward arrow and both ends of the lower number line are intact. The actual pinned English `CNX_BMath_Figure_01_01_001.jpg` was opened and visibly has both upper directional arrowheads. The Tamil description also promises the rightward arrow. This is an SVG defect inherited by the PDF, not a clipped Tamil label or a print-only CSS defect. Existing SVG line 8 combines `M340 67 H560 M285 67 H65` into one path with `marker-end`; only the final subpath receives the endpoint marker. Split it into two paths, each with its own `marker-end`. All numerals 0–6 and the labels remain visible, but the missing instructional direction should be repaired before a final export is approved. The owner independently confirmed the source raster, accepted the finding, and reports fixing the upstream SVG; **no revised PDF is marked visually verified here**.

Cheap dependency inspection found the shared asset used directly by `scripts/build.py` for historical U001 readers/EPUB and by `scripts/build_m81243_review.py` for the whole-module source renderer, which the integrated learning edition uses. The assembled source and U001 fragment retain the media mapping; reader manifests include the asset. Text, ID and numeric-inventory checks cannot detect a missing path marker. During handoff the owner added a dedicated `check_number_line` guard and missing/compound-arrow negative fixtures to the source-review builder; this review does not substitute for the owner's rebuilt-output checks. Historical U001 approval requires an explicit erratum, not an assumption that the current fix retroactively repairs old exports.

**R7 — P3, a number-name heading splits internally: pages 188–189, `#ta-m1-missing-18 > h3`, inner `.question-number-name`; source exercise `fs-id2353124`, problem `fs-id1387432`.** The heading ends page 188 with “எழுநூற்று”; its remaining “எண்பத்து மூன்று” starts page 189 without the M18 label. All text and the answer 18,102,783 are present, so this is not a wrong answer. Keep the heading's lines together, then keep it with at least the following identifier/context. The owner reports adding heading keep rules; revised pagination remains untested here.

**R8 — P3, an inline equality crosses a page: pages 65–66, `#ta-large-M4-answer > p:first-of-type`.** Page 65 ends “1 டிரில்லியன் =”; page 66 starts “1,000,000,000,000 என்பதால்…” and correctly explains the leading 5's contribution. Meaning is recoverable across the adjacent pages and no digit is missing. Keep that short paragraph or the equality together. This is ordinary paragraph pagination, not evidence of an altered MathML tree. The owner reports a targeted paragraph keep rule.

**R9 — P3, sparse pages and small context orphans remain.** Individually confirmed one-line continuation pages 45 and 53; short continuation pages 19, 78, 180 and 187; one/two-line transition pages 126/128 between the A3 number-line figures; one final table row alone on page 111; and the answer plus backlink alone on page 115. At overview resolution, pages 197/201/203 are similarly short feedback tails and page 146 is a heading-only transition before the reused chart. Page 141 ends with table heading and its part marker, with substantive data starting page 142. These remain readable in source order; they are paper-economy/keep-with-next improvements, not further missing mathematics. Existing R5 credit/identifier findings remain applicable. Avoid broad typography changes solely to chase these low-priority gaps without rechecking pagination.

A related small polish issue is individually visible at page 18: `#ta-route-T5-answer .reason` places the terminal period on a line by itself after the intact 9,000,000 + 5,000 + 20 = 9,005,020 expression. The expression is complete. Its punctuation should remain attached if the print-only math layout is adjusted.

### Detail results and limits

All remaining full-size rounding stages inspected here preserve the visible place arrows, underlines, replacement instructions, brackets, 9 + 1 = 10 carry labels, final zeros and number-line points. Pages 125/127/129 show the 70–80 endpoints and teal points at 76/72/75. Page 131 retains the explicit 76 → 80 sentence. The 3,978 and 29,504 carrying tables show the intended hundred/thousand procedures; no new right-edge clipping was found.

The complete U002 money/block/decomposition diagrams on pages 93–98 remain countable and intact. Wide U004 diagrams preserve 37|519|248 and both 098 occurrences in 8|165|432|098|710; U005 diagrams preserve leading blanks, 073 and all nine explicit trailing zeros in the 77-billion construction. Previously verified U008 model, fifteen-place-chart and confidence-table corrections remain supported by their individual-page views. Newly opened answer tables and long equalities, including M19–M21/S19–S21 and the late rounding/qualitative cards, are contained and readable. This is layout evidence, **not a fresh full native-language or every-answer mathematical audit**.

### Independent oracle review and resolved probes

Read the then-current `qa_m81243_pdf.py` and `render_m81243_pdf.py` without running either authoring CLI. Initial in-memory probes demonstrated that the Tamil-token-only oracle accepted removal of every ASCII digit and a changed 23,658 digit, and that the PDF-link check accepted a malformed `/A /GoTo /D` action. These were genuine gaps in test coverage, not proof that those corruptions occurred in the actual PDF. Both gaps were sent to the owner.

The completed read-only probe against QA script SHA-256 **906f73a7bafd4ee6dc27a1601eff6b34b42ab60b4425e85231b1c4a0265432a3** confirms the implemented fixes: the actual candidate passes numeric/operator/currency/grouping inventory, with **626 printed page-reference ink fields, 223 physical footer numbers and 168 generated decimal list markers**. Removing all ASCII digits, changing 23,658 to 23,659, changing its comma to a decimal point, and installing a nonexistent GoTo destination are all rejected. Independent stale-page-field and missing-geometric-rotated-label probes are also rejected. The actual 284-destination map and 626 internal page-reference fields pass. The render builder reviewed at that point was SHA-256 **ff74c560fdf1c3796b68cbd1268dcf4fa5c472ba1c502289205bc682f2eaf1b1**.

These checks are deliberately bounded: numeric/operator multisets are not placement proofs; exact logical text and out-of-page glyph boxes do not prove visible arrows, nested-container clipping, reading order or every link's usability. R6 demonstrates why the visual pass remains necessary.

### Final handoff for this candidate

**The requested old-candidate review is complete.** The sole newly found medium-priority mathematical-graphic defect is R6; R7–R9 and the standalone period are lower-priority layout issues. Fixes reported by the owner are implementation status, not a new-PDF visual approval. The next export requires its own exact hash, updated destination labels, targeted verification of R6–R8 and changed neighbours, and a new all-page overview if pagination changes. Do not carry this report's raster approval onto a later file just because the output filename is reused. No all-sentence Tamil, actual-printer, assistive-technology, PDF/UA or learning-efficacy certification is claimed. The larger language-allocation workflow remains active.
