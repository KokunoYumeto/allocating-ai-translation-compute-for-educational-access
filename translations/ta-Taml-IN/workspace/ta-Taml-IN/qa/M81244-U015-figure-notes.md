# M81244 U015 figure redraw notes

Status: all 21 source figures for `m81244#fs-id2150139` have been redrawn as Tamil SVGs. This is an asset checkpoint only. It does not claim admission to a reader, complete alternative-format rendering, native-language approval, or completion of m81244 or the language assignment.

## Evidence and scope

- Final Tamil source read: `translation/m81244-fs-id2150139.cnxml`, 49,158 bytes, SHA-256 `4b6e7ee11d47eca9f7318b5c7b82add16b306012cbaaf7ffa678479d5ab93f0a`.
- Translation notes read: `qa/M81244-U015-translation-notes.md`, 26,655 bytes, SHA-256 `915064ce4078ec5379b855a339fadaee4bf841e336590b880fcb3982b340170b`.
- Both actual source witnesses were read at this boundary: `provenance/m81244.en.cnxml` and `provenance/m81244.id-ID.cnxml`. Their media order, IDs, source paths and alternatives were compared with the final Tamil source.
- All 21 canonical English JPEGs in the pinned OSBooks bundle were opened and visually inspected. No raster was downloaded, copied or embedded. The ordered JPEG evidence-manifest SHA-256 is `c2dfd3a9b84ce71c5a3ebe0a78043485ea1b4ca53c6d121545e768dc79f4f3e6`, defined as UTF-8 `basename<TAB>lowercase-file-SHA256<LF>`, English basenames sorted ordinally with a final LF.
- Continual Tamil canon consultation used the existing OCR and full page images for PDF pages 36, 46 and 175. Page 36 confirms the addition register; page 46 distinguishes boundary length from area and retains source measurement units; page 175 confirms relevant notation/whole-number terms. OCR was not used as geometry or arithmetic evidence.
- Exact canonical basenames and Tamil paths were preserved. The SVGs have no external references, scripts, links, raster payloads or foreign objects.

## Pixel-grounded redraw decisions

The four block figures remain schematic models, not decorative illustrations. Each unit square is a semantic `data-kind="one"` element; each ten-cell rod is a `data-kind="ten"` group with ten visible divisions. They reproduce 2 and 4 units; one ten and 2 units; 8 tens and 9 units; and 4 tens and 1 unit. These are provided source solutions, so their existing addition expressions remain in the accessible title and description.

The nine chart figures reproduce every source header, printed value and blank at its exact row/column. Every cell has a unique ID plus zero-based `data-row`, `data-column` and `data-role` (`header`, `value` or `blank`). Empty question cells contain no hidden number or text. No arbitrary totals were inserted.

| Figure | Geometry | Interior blanks | Supplied interior values |
|---|---:|---:|---:|
| 216 | 11 rows × 11 columns | 39 | 61 |
| 217 | 11 rows × 11 columns | 0 | 100 |
| 218 | 11 rows × 11 columns | 39 | 61 |
| 220 | 5 rows × 8 columns | 28 | 0 |
| 221 | 5 rows × 8 columns | 0 | 28 |
| 222 | **8 rows × 5 columns** | 28 | 0 |
| 224 | 6 rows × 6 columns | 25 | 0 |
| 225 | 6 rows × 6 columns | 0 | 25 |
| 226 | 5 rows × 5 columns | 16 | 0 |

Figure 222 follows the actual portrait JPEG: top headers `+ 6 7 8 9`, left headers `+ 3 4 5 6 7 8 9`. Both source-language alternatives say 8 columns by 5 rows; that statement conflicts with the pixels and the listed headers. The final Tamil alternative correctly says 5 columns by 8 rows, and the SVG preserves that correction.

The eight perimeter figures retain the actual shape, every printed side value, and its source unit. Visible abbreviations were localized to the full Tamil measurement names already used by the final Tamil alternative; no lengths were converted. Figures 208–213 retain their triangle, rectangle or trapezoid geometry. Figure 214 retains all six printed lengths. Figure 215 contains only `25 அங்குலம்`, `10 அங்குலம்`, `14 அங்குலம்`, `7 அங்குலம்` and `11 அங்குலம்`: the final left vertical side remains visibly unlabelled, and neither its inferred length nor the perimeter appears in the title or description.

Every root is `role="img"`, `lang/xml:lang="ta-Taml-IN"`, and references a unique Tamil `title` and exact final-source Tamil `desc`. Visible text uses `font-family="TamilBook, 'Nirmala UI', sans-serif"`. All 736 IDs are unique across the 21 assets.

## Verification

Fresh standard-library XML checks passed:

- 21 expected SVG paths exist and parse; 21 descriptions exactly equal the final CNXML media alternatives.
- Unique local and global IDs; valid root title/description references; required Tamil font stack present.
- Exact chart dimensions and blank/value counts above; all row/column coordinates present exactly once.
- Every visible or supplied interior chart value equals its row header plus its column header. Blank cells have no text.
- Exact block-model rod/unit counts.
- Exact perimeter-label multisets, including five labels—not six—in figure 215.
- No active or external SVG content.

A local ImageMagick rasterization visually confirmed the complete block, shape and chart geometry and that numbers remain inside their cells. That renderer did not resolve the requested Tamil font stack and displayed Tamil label glyphs with a fallback warning, so it is not evidence of final Tamil font rendering. The repository SVG structure and font request are correct, but parent integration still needs browser/PDF visual QA with the bundled Tamil font. Temporary raster checks were kept outside the workspace and are not deliverables.

The ordered SVG manifest SHA-256 is `2f27c0895f8cb82a6f7322b461fb578c4daea0475db1c598089218ce34a12425`, defined like the JPEG manifest above. Total SVG size is 176,011 bytes.

| Asset | SHA-256 | IDs |
|---|---|---:|
| `CNX_BMath_Figure_01_02_201_img.svg` | `cdd8d5d34ec4b56a11c9271132cbae3095bad2e722104a546ba13b43153b5319` | 10 |
| `CNX_BMath_Figure_01_02_203_img.svg` | `b660d63382605e5217494de5a30673a2905426a47ab0bf567d432797e1257175` | 7 |
| `CNX_BMath_Figure_01_02_205_img.svg` | `4b61c9807dd4106ea31d867140b6d819de903fd84fc45914876b48b8097668a1` | 21 |
| `CNX_BMath_Figure_01_02_207_img.svg` | `710910a69c6985fed04332caea7a94bb0086306504035daf98f42799579b626a` | 9 |
| `CNX_BMath_Figure_01_02_208_img.svg` | `4a0869de066919d06bc20d9d8ef1f0c52427d9a73ace3869e9c972b5571b1513` | 8 |
| `CNX_BMath_Figure_01_02_209_img.svg` | `e395382dda6fcf31b820ebe58879f0fd219322c56b2c5ffd3658c4788dff751a` | 8 |
| `CNX_BMath_Figure_01_02_210_img.svg` | `d73aed185760b5f517237141999ee4333d0c15cb4c0a15e1b03d86570da6c6a7` | 9 |
| `CNX_BMath_Figure_01_02_211_img.svg` | `d722571d7eb0568744cd00e4d045b3f3a8659efd4b8e6419d785145a2a1e8225` | 9 |
| `CNX_BMath_Figure_01_02_212_img.svg` | `93bb72459c5f83b3493d59314bd0e805f49828eb37782153e947cea857db299e` | 9 |
| `CNX_BMath_Figure_01_02_213_img.svg` | `0849e46e2f29f35179b1d600e4ce4053a3a53e96c5515a0b45b36729b5b5c4c6` | 9 |
| `CNX_BMath_Figure_01_02_214_img.svg` | `296387967e10097b37be218e8568b446baa5cba72f341b4105ef825bb2addd08` | 11 |
| `CNX_BMath_Figure_01_02_215_img.svg` | `a04dbddd4e8323c4b0468749afe3accaf0d9c4ceab20eb54b0270b644b5b8725` | 10 |
| `CNX_BMath_Figure_01_02_216.svg` | `7e9679afb862b0c2c783cf1a629fbb5c570d82fde071afac905d80c6d478f6eb` | 125 |
| `CNX_BMath_Figure_01_02_217.svg` | `a16943ed2d98aacbf34cccb556ec814f92ea1f5c160a407357e43c46c4e985b5` | 125 |
| `CNX_BMath_Figure_01_02_218.svg` | `2b621a1053c3bb28fd5418c420a8166fa0943f82a23c7b0967f0df7528a32194` | 125 |
| `CNX_BMath_Figure_01_02_220.svg` | `b8a97fa35dbb983bc7d98af5e72b4f21689cd57cdcd899d307ab529fc2dfda27` | 44 |
| `CNX_BMath_Figure_01_02_221.svg` | `19a34267cc9d7c63a1cafdd0ffd91bb32d12c391ad8972fd296bbabbb504bf3b` | 44 |
| `CNX_BMath_Figure_01_02_222.svg` | `883ca73fc1194efefb0c070f680153105c91cf6f7a3873c38353345f26d7f071` | 44 |
| `CNX_BMath_Figure_01_02_224.svg` | `d4f7ff1419c6fb02f1e46fd705b61489cdd37241b2d79b6ebe5e2fe60584fee1` | 40 |
| `CNX_BMath_Figure_01_02_225.svg` | `44ca1ed2baefddcf25e5346510cff80be17e0e19e1ef4ae7d8e8ffdbe23272d1` | 40 |
| `CNX_BMath_Figure_01_02_226.svg` | `1e06ac1d21780c7e089c0473533bd11f99002e526cf0d1bbb953ee5d28732806` | 29 |

No source fragment, witness, builder, reader, stylesheet, output artifact, shared log or earlier asset was edited. The separate m81244 tail confidence chart remains outside this U015 checkpoint.

