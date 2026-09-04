# M81244 tail self-check figure notes

Status: the single source self-check chart for `m81244#eip-985` has been redrawn as a Tamil SVG. This is an asset checkpoint only; it is not a demonstrated-mastery assessment, pass/fail gate, reader admission, native-language approval, or module-completion claim.

## Evidence and consultation

- Final Tamil source: `translation/m81244-eip-985.cnxml`, 2,740 bytes, SHA-256 `ba06b9c41e5913ba2e26dae36bd6cc6bc9fd862c18d7e4ad862150f3509836f4`.
- Media ID: `eip-id1168469634014`; exact approved path: `../assets/m81244-tail/CNX_BMath_Figure_AppB_002_A.svg`.
- Canonical English JPEG: `CNX_BMath_Figure_AppB_002_A.jpg`, 90,432 bytes, SHA-256 `48f42617d19fa96c0be7c1fba6691f0f643cfb7126db986110c301cf1b6b7c04`. The actual raster was opened and read during drafting.
- Indonesian comparison SVG SHA-256: `d424d9c14c6059889fe4963d5323b9b55195efdfffc85c663cd9d2d4f5f633ea`. Its actual structure and visible text were read; it changes language but not the source chart's geometry.
- Existing Tamil canon OCR and complete images were reconsulted during drafting and QA: PDF page 7 for `கற்றல் நோக்கங்கள்`, page 36 for the addition register, and page 175 for whole-number/notation distinctions. The reference does not establish a mastery judgment, and none is inferred.

## Redraw decisions

The SVG preserves the actual source geometry: four columns, one header row, five ability rows, and three empty response cells per ability. The first column is deliberately wide enough for each complete Tamil sentence. The three confidence headings are:

1. `நம்பிக்கையுடன்`
2. `சிறிது உதவியுடன்`
3. `இல்லை—எனக்குப் புரியவில்லை!`

The five visible ability statements exactly match the final Tamil source:

1. `கூட்டல் குறியீட்டைப் பயன்படுத்த முடியும்.`
2. `முழு எண்களின் கூட்டலை மாதிரிகளால் காட்ட முடியும்.`
3. `மாதிரிகள் இல்லாமல் முழு எண்களைக் கூட்ட முடியும்.`
4. `சொற்றொடர்களைக் கணிதக் குறியீட்டில் எழுத முடியும்.`
5. `பயன்பாட்டுக் கணக்குகளில் முழு எண்களைக் கூட்ட முடியும்.`

No box is checked and no response, score, answer, routing decision or mastery result is embedded. Each visible cell has a unique ID and zero-based `data-row`/`data-column`; the 15 response cells have `data-role="blank-response"` and no text. The palette and first-column/choice-column distinction follow the source chart without depending on color for meaning.

The root is a Tamil `role="img"` with direct, uniquely identified `title` and `desc`; its `aria-labelledby` points to those two IDs in order. The description exactly equals the final CNXML media alternative. Visible text requests `font-family="TamilBook, 'Nirmala UI', sans-serif"`.

## Verification and limits

Fresh checks passed:

- regular non-symlink local file; well-formed XML; nonempty `viewBox`;
- exact source description and title/description references;
- 28 unique IDs, 24 exact cell coordinates, four headers, five ability cells and 15 empty response cells;
- no processing instruction, DOCTYPE, `xml:base`, stylesheet, script, animation, `foreignObject`, raster `image`, link, `href`, `src` or other active/external content;
- every complete Tamil row string fits the 724 px available line width under the bundled `NotoSansTamil.ttf` with RAQM at the SVG's 22 px size. Measured row widths are 471.5, 617, 605, 626.5, 680 px; maximum 680 px. Each confidence-heading line also fits its own cell by the same check.
- an actual SVG rasterization confirmed the 4 × 6 grid, line placement and 15 visibly empty cells. ImageMagick could not resolve the requested Tamil font family and therefore produced fallback boxes; that raster is geometry evidence only.
- the in-app/browser binding was unavailable when requested. Consequently no browser-render or final bundled-font visual approval is claimed; parent integration must repeat browser/PDF glyph and clipping QA.

Final SVG: `assets/m81244-tail/CNX_BMath_Figure_AppB_002_A.svg`, 8,163 bytes, SHA-256 `cd0294912322fca86eeb73681c7f769f6ff86620c250e2f8dbb47ffe09bc8ae3`.

Only this SVG and this distinct figure note were authored. No source fragment, builder, manifest, reader, output artifact or shared report was edited.

