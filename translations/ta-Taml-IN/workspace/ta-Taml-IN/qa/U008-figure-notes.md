# U008 model and self-assessment SVGs

Date: 2026-08-31. Bounded source-figure draft task only. Authored five files under `assets/u008/` plus this note; no CNXML, shared renderer, shared stylesheet/log, browser, PDF, EPUB or commit was changed or created here. U007 continues to reuse the existing U003 figure 011 unchanged.

## Actual evidence and canon consultation

Read the English and Indonesian alternatives for all five media in `provenance/m81243.en.cnxml` and `provenance/m81243.id-ID.cnxml`. Individually viewed all five actual canonical raster files, rather than deriving images from the assigned count summary. Read the current Tamil descriptions and the surrounding model-exercise and self-check source material in `translation/m81243-fs-id2279009.cnxml`.

The canonical raster pin is `38cae454e644abf9f0a623e876994553881597c9`. The Tamil source snapshot checked at drafting and final figure QA is SHA-256 `d5f6b6de6bd0273f9b0a525af429ec296703502bdb4b4a5d04bc985429fb6f57`.

Relevant actual canon was reread: page 20 / printed 14 (இடமதிப்பு, இலக்கம், ஒன்றுகள் in a worked comparison), page 175 / printed 169 (கிடைமட்டப் பட்டைகள், முழு எண்கள் versus முழுக்கள், முழுமையாக்கல்), and page 7 / printed 1 (கற்றல் நோக்கங்கள்). OCR was read first. Actual page images for pages 20 and 7 were then viewed during this task; the page-175 image had also been read in the immediately preceding figure task. The relevant OCR anchors were revisited at final QA. OCR corruption in page-20 numbers/operators is not used as mathematical evidence.

Canon supports the established place-value, whole-number, rounding and objective register, not an asserted validation of this self-assessment instrument. பத்துகள் பட்டை and other base-ten manipulative compounds retain the earlier documented provisional choices. The self-assessment response wording is the translator's contextual translation, not a newly claimed canon quotation or proof of mastery.

## Exact mapping

The target filename is each original basename with only the final extension replaced by `.svg`.

| Target file | Source media ID | Intrinsic width × height |
|---|---|---|
| `CNX_BMath_Figure_01_01_201_img.svg` | `fs-id1393361` | `344 540` |
| `CNX_BMath_Figure_01_01_202_img.svg` | `fs-id1284927` | `344 402` |
| `CNX_BMath_Figure_01_01_203_img.svg` | `fs-id2675330` | `344 358` |
| `CNX_BMath_Figure_01_01_204_img.svg` | `fs-id2716627` | `344 514` |
| `CNX_BMath_Figure_AppB_001.svg` | `eip-id1165721974707` | `1392 700` |

The four model images belong to the model-number exercises. AppB belongs to the original unnumbered self-check figure `eip-id1165721974706`, not a newly inserted assessment or result. The source chart's role and blank-response state remain intact.

## Model fidelity and answer concealment

Each unit cell is 14×14 SVG units. A hundred square is 140×140 with exactly nine internal vertical and nine internal horizontal lines, making a 10×10 grid. A horizontal tens rod is 140×14 with nine internal vertical lines, making ten unit cells. An isolated unit is a single 14×14 square. The grid, rods and isolated units therefore use the same geometric unit.

| Source suffix | Hundred squares | Tens rods | Isolated units | Source arrangement retained |
|---|---:|---:|---:|---|
| 201_img | 5 | 6 | 1 | Two columns of squares, fifth square lower left; six rods lower right; unit below the rods. |
| 202_img | 3 | 8 | 4 | Two upper squares and one lower-left square; eight rods on the lower right; four units beneath the left square. |
| 203_img | 4 | 0 | 7 | Two-by-two squares; six units below the left column and one below the right column. |
| 204_img | 6 | 2 | 0 | Two-by-three squares; one horizontal rod beneath each column. |

All four remain **unlabelled visible model diagrams**, as in the source. No total or worked place-value sum was added to visible text, SVG title, description or a `data-total` attribute. The descriptions provide the actual component counts and dimensions, allowing a nonvisual reader to solve the same task, but do not give the combined numeric answer. Automated checks tested both Arabic-digit totals and their Tamil number-name equivalents for absence in all model titles/descriptions. Source answer paragraphs elsewhere in the CNXML were not edited or moved.

The English and Indonesian alternatives agree on the quantities. The Indonesian alternatives explicitly state the absence of tens in 203 and ones in 204; the actual images support this and the Tamil descriptions retain it. No source-count disagreement was found.

## Self-assessment chart

The actual canonical chart has four columns: the left “I can…” skill column and three response columns. It has six skill rows and **18 empty response cells**. No tick, score, confidence state, extra row, new instruction or new result has been inserted.

Exact coordinated headers:

- **என்னால்…**
- **நம்பிக்கையுடன்**
- **சிறிது உதவியுடன்**
- **இல்லை—எனக்குப் புரியவில்லை!**

Exact skill statements:

1. இயல் எண்களையும் முழு எண்களையும் அடையாளம் காண முடியும்.
2. முழு எண்களை மாதிரிகளால் காட்ட முடியும்.
3. ஓர் இலக்கத்தின் இடமதிப்பைக் கண்டறிய முடியும்.
4. இடமதிப்பைப் பயன்படுத்தி முழு எண்களின் பெயர்களைக் கூற முடியும்.
5. இடமதிப்பைப் பயன்படுத்தி முழு எண்களை எழுத முடியும்.
6. முழு எண்களை முழுமையாக்க முடியும்.

The source's pale-teal header/skill-column shading and pale response-column shading remain visually recognizable. Wider Tamil text wraps inside the original cell roles instead of being compressed into the raster's English dimensions. There is no added visible title band. Header text is 24 px/weight 600; skill text is 22 px/weight 400.

Stable IDs identify `u008-appb001-header-0…3`, `u008-appb001-skill-0…5`, and every blank response rectangle `u008-appb001-response-r0-c1` through row 5 / column 3. `data-row`, `data-column` and `data-response-cell="blank"` record that structure for later semantic rendering. Each six-by-three row/column pair exists exactly once.

The expanded Tamil SVG description names every column and all six skills, unlike the terse source alts; this improves access to actual source content without inventing responses. The description is exactly the translator's current CNXML alt.

## Verification

Passed read-only checks:

- All five expected source media paths exist, and each SVG description exactly matches the current Tamil alt.
- **162 IDs**, unique across the entire asset set; all five title/description reference pairs resolve.
- Every square/rod grid path is checked against its actual rectangle and 14-unit spacing. Counts and absence cases match the table above. All shape rectangles are inside their viewBoxes.
- No visible text exists in the four model drawings; no Arabic/Tamil answer totals appear in their titles/descriptions; no `data-total` attribute exists.
- All four chart headers and all six skill sentences reconstruct exactly across wrapped tspans. All 18 response cells remain empty, without text or child nodes.
- **16 shaped Tamil text line boxes** were measured with the actual bundled Noto Sans Tamil variable font through Pillow RAQM, width axis 100 and each actual size/weight. Every box fits both its SVG canvas and its assigned table cell; no pair of text boxes overlaps.
- Total asset size: **31,509 bytes**. Free C: space was about 10.12 GB at task start; no disk-full error occurred.

All assets specify `font-family="TamilBook, 'Nirmala UI', sans-serif"`, Tamil language metadata, `role="img"`, full title/description references and per-image `u008-…` IDs. The visible drawing groups are `aria-hidden="true"` so decorative grid strokes are not repeatedly read after the complete image description.

This is static asset QA, not a browser/PDF or assistive-technology certification. The compact block-model widths are 344 px. The dense self-assessment chart is 1392×700: integration should keep it legible using horizontal scrolling and provide a real semantic HTML equivalent with the same six skills and three blank response columns. A static SVG must not be presented as an interactive checkbox form. Any teacher-independent learning/remediation route is separate from this preserved source chart and remains a parent integration task.

## Source and output hashes

The middle column hashes the canonical raster; the final column hashes its corresponding target SVG.

| Canonical raster filename | Source SHA-256 | SVG SHA-256 |
|---|---|---|
| `CNX_BMath_Figure_01_01_201_img.jpg` | `5dca1f3e0d7aad2e2fd1c5caf9345e4ddf3d6b4c3eeceaa592d12a5eaa8d3e5d` | `094442ba33d3a5a0b84d0eed96b9e039f5f0ba236858fc215b6417921bc1b59f` |
| `CNX_BMath_Figure_01_01_202_img.jpg` | `2dc89eb539e106cf1adfc463345f006446c10d4e178e2be600698c612fa92ffb` | `00fa7b5e6544372f263267b4a194e76ad0e4fa27fd8e3008749f5e86b1d80071` |
| `CNX_BMath_Figure_01_01_203_img.jpg` | `9e7c9dac10e181bad91e58062aff485a1f832714afa14538a12be2a15fb94327` | `1c1f254ab3fa13de0aec801bc415f71b44c67488675bdc89c44a76efef015bc5` |
| `CNX_BMath_Figure_01_01_204_img.jpg` | `e0dc7bd082bd818e0f1efa7f6da87778cbc63afd5020d00cbb862cb07986266d` | `d1f76c5d300da2f1a83f218ad4fa92f4f310deb53cdfe15bdb646cb954c5c481` |
| `CNX_BMath_Figure_AppB_001.jpg` | `d26ade53426ac1d159f56857f8ee337914b1c8719c6dc70edff70356b502eacd` | `53afb6faaa7ee071a7c92520bec03d846de18fbd327084ec8f431d07c4c787fb` |

No disagreements requiring additional source-alt changes were found. Native-speaker/editor review and rendered integration remain open. This completes only the bounded five-asset task, not the full assignment.
