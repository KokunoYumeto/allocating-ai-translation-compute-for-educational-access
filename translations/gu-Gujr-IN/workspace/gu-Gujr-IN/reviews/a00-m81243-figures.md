# A00 m81243 part03 — completed figure redraw batch

Date: 2026-08-30. Implementation: `scripts/localized_place_value.py`. Public API: `render_figure(filename, alt, unique_id) -> str | None`. All **32** media occurrences in the five part03 sections return localized code-native HTML/SVG. Unknown filenames return `None`. No raster edits, new image downloads, or source-file mutations are required.

## Source inspection and canon use

Read the source figure descriptions while translating; subsequently inspected all 32 actual original media occurrences. Reviewed the large place/group charts and three source-description errors individually, then reviewed the full original-image contact sets under ignored `build/gujarati-part03-figures/original-1.jpg` through `original-4.jpg`. These are local review sheets, not substitute source illustrations or deliverable raster edits.

The previously read Std 5 p13 and Std 6 pp14–15 OCR/images supplied **એકમ**, **દશક**, **સો**, **હજાર**, **સ્થાનકિંમત**, and the number/word distinction before this redraw work. During revision, read the indexed Khan Gujarati rounding excerpts documented in `a00-m81243-part03.md`, then aligned result language to **સૌથી નજીકના દશકમાં ફેરવતાં**. Reviewed the final labels against those observed terms. International **મિલિયન**, **બિલિયન**, **ટ્રિલિયન** and source comma grouping remain unchanged; these are not falsely attributed to the school worksheet canon.

Original-image inspection found two details absent from the original alt descriptions: images `022` and `032_img` underline 6 and 2 respectively, and `031_img` contains an additional written 76 → 80 rounding-result sentence. Both underline details and the complete Gujarati result sentence are present in the redraws.

## Rendering choices

- The 15-place charts keep every place, all five groups in source order, and all leading empty cells. A blank cell remains blank and is named `ખાલી` for assistive technology; a source zero remains `0`. Semantic tables use captions and column-header scopes. The groups wrap on narrow screens without changing their order.
- Number/word cards retain each source group, word phrase, digit string and direction of conversion. Three digit slots remain visible where the source shows slots; leading blanks remain blank. In particular, `073` and `098` retain their zeros. A combined number identifies the relationship between the groups.
- Number lines retain all 11 equal-spaced ticks 70–80, both arrow ends and the exact marked value 76, 72 or 75. HTML tick labels stay at a readable font size as the SVG line narrows. The highlight is orange to match the already-localized description; mathematical position and endpoint emphasis are unchanged.
- Place labels identify the same digit as the original arrow. Underlines are preserved. Rounding-action diagrams connect the original target digit and trailing digits to their instructions, carry steps and result. Color is paired with explicit labels, arrows, underline or crossing; it is not the only source of meaning.
- All redraws use `font-family: Gujarati,'Nirmala UI',sans-serif`. All outer IDs and SVG marker IDs include a sanitized `unique_id` plus its hash, so identical numbers in different source figures cannot collide. No external resources, scripts or event handlers are emitted.

## Per-file coverage

Every filename below begins with `CNX_BMath_Figure_`. Every listed entry returns a redraw, including numeric-only images.

| Filename suffix | Mode | Preserved content/check |
| --- | --- | --- |
| `01_01_011.jpg` | Semantic place tables | 15 places; 8 leading blanks; 5,278,194. |
| `01_01_012_img.jpg` | Semantic place tables | 15 places; 7 leading blanks; 63,407,218; internal zero preserved. |
| `01_01_013_img.jpg` | Number-to-words cards | 37 / 519 / 248 with million / thousand / ones correspondence; complete Gujarati words. |
| `01_01_014_img.jpg` | Number-to-words cards | 8 / 165 / 432 / 098 / 710 with all five periods and complete words. |
| `01_01_015_img.jpg` | Group-label cards | 327 / 577 / 529, correctly paired with periods. |
| `01_01_016_img.jpg` | Words-to-digits cards | 53 / 401 / 742; three slots per group with one leading blank in the first. |
| `01_01_017_img.jpg` | Words-to-digits cards | 9 / 246 / 073 / 189; first group has two leading blanks; confirmed `073`, not source-alt typo `742`. |
| `01_01_018_img.jpg` | Words-to-digits cards | 77 billion → 77 / 000 / 000 / 000; first group has one leading blank. |
| `01_01_019.jpg` | SVG line + HTML tick labels | 70–80; mark 76. |
| `01_01_020.jpg` | SVG line + HTML tick labels | 70–80; mark 72. |
| `01_01_021.jpg` | SVG line + HTML tick labels | 70–80; mark 75. |
| `01_01_022.jpg` | Digit + annotated place | 76; tens digit 7; underlined 6; 6 > 5 explained in Gujarati. |
| `01_01_031_img.jpg` | Rounding action | 76 → 80; add 1 to 7; cross out/replace 6; complete embedded result sentence translated. |
| `01_01_032_img.jpg` | Digit + annotated place | 72; tens digit 7; underlined 2; 2 < 5 explained in Gujarati. |
| `01_01_033_img.jpg` | Rounding action | 72 → 70; do not add 1 to 7; cross out/replace 2. |
| `01_01_034_img-01.png` | Digit + place label | 843; tens place identifies 4. |
| `01_01_034_img-02.png` | Number + underline | 843; underline 3. |
| `01_01_034_img-03.png` | Number + underline | 843; underline 3 retained in the second procedural image. |
| `01_01_034_img-04.png` | Number + underline | 840; underline 0. |
| `01_01_035_img-01.png` | Digit + place label | 23,658; hundreds place identifies 6. |
| `01_01_035_img-03.png` | Number + underline | 23,658; underline 5. |
| `01_01_035_img-02.png` | Rounding action | 23,658 → 23,700; add 1 to 6; replace 5 and 8. |
| `01_01_036_img-01.png` | Digit + place label | 3,978; hundreds place identifies 9. |
| `01_01_036_img-03.png` | Number + underline | 3,978; underline 7. |
| `01_01_036_img-02.png` | Rounding + carry action | 3,978 → 4,000; 9 + 1 = 10; write 0 hundreds, add 1 thousand, replace 7 and 8. |
| `01_01_037_img-01.png` | Digit + place label | 147,032; thousands place identifies 7. |
| `01_01_037_img-02.png` | Number + underline | 147,032; underline the hundreds 0. |
| `01_01_037_img-03.png` | Number | 147,000. |
| `01_01_038_img-01.png` | Digit + place label | 29,504; thousands place identifies 9. |
| `01_01_038_img-02.png` | Number + underline | 29,504; underline 5. |
| `01_01_038_img-03.png` | Rounding + carry action | 29,504 → 30,000; 9 + 1 = 10; write 0 thousands, add 1 ten thousand, replace 5, 0, 4. |
| `01_01_011.png` | Semantic place tables | Repeated 5,278,194 chart; same 15 places with a distinct namespaced ID. |

## Validation and actual visual review

Generated four local preview pages from all 32 source media records and the final helper. HTML parsing confirmed 32 redraws, 35 unique IDs, six SVG marker references all resolving inside their redraw, no Latin letters in visible figure text, no external URLs, and no event attributes. Unknown-name fallback returns `None`. Source numbers and relationships were checked against the actual images and the part03 mathematical review.

Reviewed the live browser DOM and screenshots of the table/group page, all three marked number lines, the underlined comparison digits, 76 → 80, the 843/840 underlines, and both carry-action figures. The 3,978 → 4,000 and 29,504 → 30,000 screenshots show complete readable carry instructions and results. Audited the underlined digits on the three later pages as 6/2, 3/3/0/5/7, and 0/5, matching the original figures. The initial long full-page capture had browser stitching artifacts; it was not used to diagnose layout. Normal viewport screenshots and live bounding boxes verified the actual layout instead.

At a 390×844 viewport, each page had document client/scroll width **375/375**, eight redraws and zero redraw containers with horizontal overflow. At the normal desktop viewport, page client/scroll width was **1265/1265**; the five place tables remained within the 1000-pixel review column. The temporary viewport override was reset. These are component checks, not a claim of PDF/UA or an assistive-technology certification.

Integration still needs to call this helper from the full reader renderer and review the result with surrounding source prose. Original XML image paths stay unchanged for dispatch. Root owns the full assignment, shared build, terminology ledger, status files and commit; this batch does not close the full Gujarati workflow.
