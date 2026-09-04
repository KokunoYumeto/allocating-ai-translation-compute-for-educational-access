# U003 place-value figures — 2026-08-30

Status: two source-faithful Tamil SVG drafts with structural, positional, arithmetic, and shaped-font metric checks. Integrated browser/PDF visual QA is still required. This bounded subtask changed only the two files in `assets/u003/` and this note; it did not edit the CNXML, builder, shared decision logs, or reader edition, and made no commit or download.

## Source and canon actually consulted

- Read the complete pinned English subsection `m81243#fs-id1883656` from `provenance/m81243.en.cnxml`, then viewed both original JPEGs in `downloads/osbooks-prealgebra-bundle-38cae454e644abf9f0a623e876994553881597c9/media/`.
- Canonical upstream: `openstax/osbooks-prealgebra-bundle@38cae454e644abf9f0a623e876994553881597c9`.
- Reread actual OCR `downloads/tamil-canon/ocr/page-020.txt`, then inspected its page image. SCERT 2018 PDF page 20 / printed page 14 supports the place-value chart register, digit-versus-place distinction, and aligned cells. The reference uses Indian number grouping; its lakh/crore places were not substituted into this international source chart. OCR operators/numbers were not used as mathematical authority.
- Coordinated all 15 place labels and five period headings with the source translator, then read the actual U003 CNXML media alternatives to verify alignment. Period remains the provisional compound **இடமதிப்புத் தொகுதி**. Millions, billions and trillions remain மில்லியன்கள், பில்லியன்கள், டிரில்லியன்கள்; these are not claimed as terms attested on canon page 20.

## Observed geometry and fidelity decisions

Figure 011 has four horizontal bands: visible “இடமதிப்பு” title, five period headings, 15 rotated place labels, and digit cells. Its first eight digit cells are empty; columns 9–15 contain 5, 2, 7, 8, 1, 9, 4. They show **5,278,194**.

Figure 012 has **three** bands: period headings, rotated place labels, and digit cells. The actual canonical JPEG has no visible “Place Values” title. Its English alternative incorrectly claims a title and two rows; the redraw follows the actual image, with no added visible title band. Its SVG `title` is accessibility metadata, not a drawn heading. The first seven digit cells are empty; columns 8–15 contain 6, 3, 4, 0, 7, 2, 1, 8. They show **63,407,218**. The interior 0 remains explicitly visible; leading blanks remain empty, not zero-filled.

Both diagrams retain 15 equally sized place columns, grouped three at a time. Period borders are heavier than individual column borders, so grouping does not rely only on colour. All source places are retained through hundred trillions. International comma grouping remains unchanged in accessible number labels. No source value was replaced with an unrelated example, a lakh/crore conversion, or merely a total without its digit-position mapping.

The row below records the full positional mapping; “blank” means an empty source cell, not a displayed zero.

| Power of ten | Tamil place label | 011 digit | 012 digit |
|---|---|---|---|
| 14 | நூறு டிரில்லியன்கள் | blank | blank |
| 13 | பத்து டிரில்லியன்கள் | blank | blank |
| 12 | டிரில்லியன்கள் | blank | blank |
| 11 | நூறு பில்லியன்கள் | blank | blank |
| 10 | பத்து பில்லியன்கள் | blank | blank |
| 9 | பில்லியன்கள் | blank | blank |
| 8 | நூறு மில்லியன்கள் | blank | blank |
| 7 | பத்து மில்லியன்கள் | blank | 6 |
| 6 | மில்லியன்கள் | 5 | 3 |
| 5 | நூறாயிரங்கள் | 2 | 4 |
| 4 | பத்தாயிரங்கள் | 7 | 0 |
| 3 | ஆயிரங்கள் | 8 | 7 |
| 2 | நூறுகள் | 1 | 2 |
| 1 | பத்துகள் | 9 | 1 |
| 0 | ஒன்றுகள் | 4 | 8 |

## Accessibility and integration requirements

- Unique `u003-f011-` / `u003-f012-` IDs identify every place and digit cell. Both SVG roots have Tamil language tags, `role="img"`, and resolvable `aria-labelledby`. Descriptions enumerate all 15 places, the period groups, the leading blanks, and every occupied digit position. Visible groups are hidden from duplicate accessibility traversal.
- Fonts declare `TamilBook, 'Nirmala UI', sans-serif`; the SVG does not embed or download a font. The integrating reader must continue supplying its local TamilBook font.
- The intrinsic width is 1082 units, with 21-unit rotated place labels, 23-unit period headings and 28-unit digits. This preserves the dense source chart without discarding columns. **Do not treat a phone-width fit as legible:** at 375px wide, labels would be only about 7.3px. Integrate a horizontally scrollable/zoomable chart and a semantic place/digit table (or equivalent fully readable text alternative); do not use SVG image semantics as a substitute for navigable table semantics. The existing complete SVG description supplies image alternative text, not proof of screen-reader usability.
- A typical 607-point PDF text width would render the place labels at about 11.8pt. Actual placement, page fit, rotated Tamil shaping, monochrome contrast, zoom and navigation still require browser/PDF inspection.

## Checks completed

Read-only assertions passed for XML parsing; IDs unique across both SVGs; accessible label resolution; all 15 expected Tamil place labels and five period headings; exact column coordinates and digit baselines; eight/seven leading blanks; the retained interior zero; and visible title count (one in 011, zero in 012). Summing each drawn digit times its indicated power of ten independently reconstructs 5,278,194 and 63,407,218.

Used Pillow with RAQM enabled and the actual bundled `assets/fonts/NotoSansTamil.ttf`, at width axis 100 and weight 400/600 as declared, to shape and measure each label. Every transformed place-label glyph box lies inside its own column and label band; every period heading and nonblank digit fits its cell; the 011 title fits its band. The longest shaped place label is 231px, within the 310px label-band height. These are font-metric checks, **not** a claim that a browser screenshot or PDF has been visually approved.

No native-speaker, educator, EPUB reader, screen-reader or PDF/UA approval is claimed. Final rendered QA and any semantic-table integration remain with the parent task.

## SHA-256 witnesses

| File | Bytes, when authored | SHA-256 |
|---|---:|---|
| Original `CNX_BMath_Figure_01_01_011.jpg` | — | `4372c506857a59bc35f64c8c663f12bb78ace2fa392207f4c7e94aa3a8953a25` |
| Original `CNX_BMath_Figure_01_01_012_img.jpg` | — | `358e0f2d7555e4930f995655ff9e406e467d19d5441402b59d464e4664a05717` |
| Tamil `CNX_BMath_Figure_01_01_011.svg` | 6,662 | `db6ca7a2becc7bb8de9b6dcc32b9b5b25a74eb2a8e0cd0ec31387fd8a584ca7e` |
| Tamil `CNX_BMath_Figure_01_01_012_img.svg` | 6,824 | `19102c5b68ba0b14ed623a4f78c4a380ea9de645b73a1bd33537166de847fbc9` |

Storage preflight reported 6,633,394,176 bytes free on C:; the final pre-note check reported 6,700,576,768. No large copies, extraction, cleanup or additional source acquisition occurred.
