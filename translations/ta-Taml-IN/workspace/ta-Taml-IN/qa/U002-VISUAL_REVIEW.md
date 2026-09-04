# U002 HTML visual review - 2026-08-30

Main-assistant inspection, not native-speaker, learner or assistive-technology certification.

Reviewed HTML SHA-256: `5231f5c9b793e0aabce9c69636d77d7ad83045cf2ffecc5e8496c989f602e9f5`. The 2026-08-31 print-only CSS revision leaves this HTML and screen styling unchanged but changes the packaged EPUB. Current package hashes must come from the refreshed structural receipt/build manifest, not the earlier EPUB hash. Source/companion/build hashes are in the structural receipt and builder notes.

## Observed browser evidence

- Individually inspected all nine actual inline SVGs: 3/7/4 denomination cards, $300+$70+$4→$374, the 1/10/100 unit model, 138 block model/decomposition, 215 model/decomposition, and unlabelled176/237 exercises. Counts, arrows, place labels and group values are correct. No visible Tamil tofu, cropped label or diagram overlap was found at desktop width.
- Visually inspected the138 semantic table: five columns, aligned rows, values100/30/8 and sum138. The215 table likewise has five columns; header associations are verified structurally. Source figure labels1.2/1.3/1.4 follow canonical numbering.
- The first phone fit made denomination labels about9.5CSSpx, too small. The final build added independent diagram overflow panels with544px minimum SVG width. A390×844viewport had375px document client and scroll widths: no page-level horizontal overflow. Panels were343/320/286px wide with544px content; tables independently overflowed too.
- Final phone screenshot showed readable card labels, a scrollbar and Tamil scrolling instructions. Exact text alternatives remain outside and reflow normally. All nine panels expose a Tamil label and tabindex0. Focus visibly receives an outline.
- Clicking the actual contents source link navigated to#fs-id2340048. Fonts were loaded; diagrams had the SVG namespace. Temporary viewport overrides were reset.

## Limits and PDF revision

Synthetic End/ArrowRight calls focused the region but did not change scrollLeft; the cause is not established. CSS inspection found no handler or screen rule suppressing scrolling. Do not claim keyboard panning or screen-reader usability verified.

2026-08-31 correction: Poppler recovers every authored Tamil token from both first PDFs, with no NUL or replacement character. Chromium preserves logical Tamil in `/ActualText`; the 708NULs came from pypdf's incompatible extraction, not absent logical PDF text. The broad corruption diagnosis is retracted, and no production font replacement is required. See `PDF-font-investigation.md` for the controlled evidence. The first print's 23 pages were visually reviewed, and its 215 worked example/table split was flagged. A print-only CSS pagination correction now requires fresh export and all-page visual checks for both profiles before PDF delivery.

Native/educator approval, learner validation, real assistive-technology testing, an EPUB reading-app check and PDF/UA validation remain open. The overall assignment is incomplete.

## Final PDF disposition - 2026-08-31

Both final profiles have24pages and pass Poppler logical-Tamil extraction:2,303authored tokens recovered exactly, no missing/extra Tamil tokens, noNUL/replacement characters, and no out-of-page glyph boxes. Both catalogs contain Tamil language/marked/structure information; that does not establish PDF/UA. The pypdf extractor limitation remains explicitly recorded.

| Profile | SHA-256 | Bytes | Review |
|---|---|---:|---|
| Print | `ad7652a4ea6f75625a4a3ec002b8542f891a17e0abc37f4aa78aa6fc8d5ef4e0` | 875507 | Independent model reviewer inspected all24pages; all three prior layout findings resolved. See `U002-PRINT-REVIEW.md`. |
| Screen | `8506af70826e548f430e51a3d1e9f647be24d581597256233ea3ca4f7d525f90` | 872343 | Main task inspected all six latest contact sheets, covering24pages; full-resolution checks also covered4,6,13,20. |

The screen revision retains13pt body text and all wording. Scoped line/paragraph/heading spacing reduced31pages to24by removing short spillovers in the contents, introduction, routing, explanation and mastery/retry feedback. Page4now contains its complete diagnostic route; page6contains the complete grouping explanation; page20contains all mastery answers and both next-step paragraphs. No clipped Tamil, overlapping lines, broken models, isolated continuation line or split compact table remained in this final review. Full-resolution checks confirm the denser1.5line-height sections remain legible. The source215model/solution spans12–13with its prompt/model together and complete table on13. Remaining whitespace beside intentionally kept blocks is accepted.

The final EPUB SHA-256 is `ba0015bcfe79f13a58f63b70ac1c1a18defb3ab1b6da1867ba2e5d337c591134`; fresh EPUBCheck5.3.0reports zero errors/warnings, and repeated nine-file builds match. The final stylesheet SHA-256 is `f67f3ab4a4c142573f20d52b6365b7f13e5246932dbe29dcef9a50efa889fdc3`. These are scoped technical/visual passes, not linguistic, learner or assistive-technology certification.
