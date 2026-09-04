# U002 print PDF visual review

Reviewed: 2026-08-31. Scope: the 23-page print profile only; the screen profile is being reviewed separately.

Input: `ta-Taml-IN/output/pdf/ta-Taml-IN-A00-U002-print.pdf`, SHA-256 `ffa4d63da02df5ff5b179c5787c43bf099f03fa7024131b03586034124355a9b`, 875,838 bytes. PDF mtime: `2026-08-30T20:31:27.3206771Z`.

All 23 page PNGs (`tmp/pdfs/U002-print-pages/page-01.png` through `page-23.png`) and all six contact sheets existed and were newer than the PDF before inspection. Page PNG mtimes ran from `2026-08-30T22:02:30.3293962Z` to `2026-08-30T22:02:39.4770922Z`; contact sheets followed through `2026-08-30T22:02:40.5889408Z`. All six sheets were visually inspected, covering every page 1-23. Full-resolution page inspection additionally covered pages 8, 10, 11, 12, 13, 19, 21, 22, and 23, where diagram labels, table breaks, dense answer text, links, or credits warranted closer inspection.

## Findings

### P2: Keep the compact 215 place-value table together (pages 12-13)

The five-row source table `fs-id1785447` is divided across the page boundary. Page 12 has the header plus the hundreds and tens rows; page 13 repeats the header and shows only the ones row and the total 215. No row is visibly clipped and the repeated header is correct, but the learner cannot see `200 + 10 + 5 = 215` as one table. This is particularly disruptive in a recovery worked example.

Recommendation: keep this compact table intact in print, moving it to the next page if necessary. Retain semantic cells and header associations. Re-export and verify that the table remains readable and that the total stays with all three component rows.

### P3: Keep the worked-example prompt with its initial model (pages 11-12)

The source example `fs-id2222880` starts near the lower portion of page 11 with its heading and two-line prompt, but the referenced block model begins on page 12. Page 11 then leaves a large blank area beneath the prompt, and the example ultimately continues through page 13 because of the table break above. The heading is not literally isolated without text, but the task prompt is separated from the visual it asks the learner to use.

Recommendation: keep the example heading, prompt, and first model together where feasible; a print-only break before the example is preferable to a three-page worked-example sequence. Avoid scaling the model down so far that the individual base-ten cells become difficult to count.

### P3: Keep the short remediation link label together (page 21)

In `ta2-T4-answer`, the final `விளக்கம் 2` link wraps between the word and the numeral, leaving underlined `2.` on a line by itself. The reference remains readable, but the lone numeral is visually weak and can be confused with a list marker.

Recommendation: prevent wrapping inside short remediation labels such as `விளக்கம் 2`, while allowing the surrounding paragraph to wrap normally. This is a layout-only adjustment; do not change the authored answer or target.

## Otherwise observed

No clipped text, margin overflow, overlapping body content, broken SVG geometry, missing glyph boxes, or visibly unreadable Tamil was found in the inspected pages. The money labels on page 8 and base-ten labels on page 10 are legible at full resolution. The source/companion transition on pages 7-8 and 14-15 is clear. Question/answer sections, source figure labels 1.2-1.4, page numbers, and credits remain visible. The first place-value table on page 11 is intact and legible.

This is a visual-layout review, not native-speaker approval, pedagogical efficacy validation, assistive-technology-user testing, or PDF/UA conformance certification. Logical-text extraction evidence is recorded separately in `qa/PDF-font-investigation.md`. No source, CSS, HTML, EPUB, or PDF was edited during this review.

## Current-hash re-review after layout revision

Reviewed: 2026-08-31. This disposition supersedes the open findings above for the revised PDF only; the earlier record is retained as evidence of the issues and their resolution.

Current input: `ta-Taml-IN/output/pdf/ta-Taml-IN-A00-U002-print.pdf`, SHA-256 `ad7652a4ea6f75625a4a3ec002b8542f891a17e0abc37f4aa78aa6fc8d5ef4e0`, 875,507 bytes, **24 pages**. The actual receipt and page files establish 24 pages; the coordinator's initial shorthand of 23 pages was not used as the review count. PDF mtime: `2026-08-30T22:22:52.8181448Z`.

All current page PNGs 01-24 and all six current contact sheets were present and newer than this PDF. Page mtimes run from `2026-08-30T22:28:01.3763742Z` through `2026-08-30T22:28:09.2422720Z`; the final contact sheet mtime is `2026-08-30T22:28:10.1802316Z`. All six contact sheets were inspected, covering every page 1-24. Additional full-resolution inspection covered pages 11, 12, 13, 21, and 22.

| Prior finding | Current visual evidence | Disposition |
|---|---|---|
| Split 215 table on old pages 12-13 | Page 13 now contains the complete header, hundreds/tens/ones rows, and total 215 on one page. No cell or row is clipped. | Resolved. |
| Example prompt separated from initial model | Page 12 now begins with the example heading, prompt, block model, and its description together. The worked example spans pages 12-13, not three pages. | Resolved. |
| Lone numeral in T4 remediation link on old page 21 | The answer has moved to page 22; `விளக்கம் 2` remains together on one line. | Resolved. |

No new clipped text, margin overflow, overlapping content, broken table row, orphan heading, broken figure geometry, missing-glyph box, or visibly unreadable Tamil was observed in this current 24-page inspection. Blank space remains below the intact table on page 11 and below solution text on page 12 because larger content blocks are kept together; it does not hide or clip content and is accepted here as a pagination trade-off. The source/companion transition is now between pages 15-16, and the credits continue on pages 23-24.

Current visual disposition: all three reported layout findings resolved; no further visual-layout fix requested for this print hash. This is still not native-speaker, assistive-technology-user, pedagogical-efficacy, or PDF/UA certification. The screen profile is outside this re-review. Only this review note was edited during the re-review.
