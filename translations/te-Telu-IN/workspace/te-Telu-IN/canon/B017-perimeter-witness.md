# B017 perimeter witness — Telangana Class 6

2026-09-01. Bounded topic expansion for `TE-B017`, not a new general canon audit.

## Source and selection

- SCERT Telangana, Class 6 Mathematics, Telugu-medium, 2018-19 impression.
- [Official source PDF](https://www.scert.telangana.gov.in/PDF/publication/ebooks/6TM_MAT.pdf).
- Working PDF: `downloads/canon/ap/TS-6TM-MAT.pdf`, 45,716,499 bytes, SHA-256 `3faa1f0551382ea25853d62604c63aa27034c6c07f7d56ce016c83d36b6f90ee`.
- The actual table of contents is PDF page 9. It places chapter 10, చుట్టుకొలతలు మరియు వైశాల్యాలు, at printed pages 131–144. The earlier approximate PDF155–167 range is chapter 11, ratio and proportion, and is not used as perimeter evidence.
- Selected PDF141 / printed131 introduces §10.2 చుట్టుకొలత. Selected PDF142 / printed132 gives the edge-path definition and two worked examples. No other pages were OCRed for this topic.

The historical `downloads/canon/ap/` folder name does not make this Andhra Pradesh evidence. This is a Telangana government textbook witness. The AP terminology gap remains open; no AP/TS difference is invented.

## OCR-before-image workflow and fingerprints

Rendered the two selected pages only, then OCRed both before reading the complete PNGs:

```text
pdftoppm -f 141 -l 142 -scale-to 2200 -png downloads/canon/ap/TS-6TM-MAT.pdf downloads/canon/ap/TS6-perimeter
tesseract downloads/canon/ap/TS6-perimeter-141.png downloads/canon/ap/TS6-perimeter-141 --tessdata-dir downloads/canon/tessdata -l tel+eng --psm 3
tesseract downloads/canon/ap/TS6-perimeter-142.png downloads/canon/ap/TS6-perimeter-142 --tessdata-dir downloads/canon/tessdata -l tel+eng --psm 3
```

| Page | OCR bytes / SHA-256 | PNG bytes / SHA-256 |
| --- | --- | --- |
| PDF141, printed131 | 3,434 / `955eff95f9751e6cc92298a1864f4fbde30be1424250bba7a20c31bbeb099de3` | 731,315 / `c1ae6bdb11a0a7fd28c05b9a1239f053dfa4c9a27f71773585d12b6517851a2f` |
| PDF142, printed132 | 3,039 / `09d374d65caeeec3ef26b4f8a09fdf26574e178f14d31539905871e49923bc4c` | 491,128 / `f4925136c05cf895f3439a602cea067fc0c1cfdcac69cf1ec3766b61158624c1` |

## Actual wording and examples

The pages directly witness **చుట్టుకొలత**. Short anchors, read against the full page images:

- Printed131: “ఒక సంవృత పటములో దాని సరిహద్దు యొక్క మొత్తం పొడవు” is its perimeter. This establishes a closed figure and the total length of its boundary.
- Printed132: the bold definition says the measured total distance needed to go once around a closed figure, along its edge, is చుట్టుకొలత.
- Printed132 then states that the perimeter of a polygon is found from the sum of its side lengths.
- Example1 actual image and arithmetic: `130 మీ. + 90 మీ. + 130 మీ. + 90 మీ. = 440 మీ.` The OCR first mentions 180m, but the image clearly gives 130m and the displayed equation totals 440m. Use the image, not that OCR error.
- Example2 is a concave, notched 12-edge figure. It derives a missing outer edge `AL=7m`, then adds `4+1+3+2+2+1+2+2+3+1+4+7=32m`. The path follows every outer and notch edge once; it is not area and it does not skip inset edges.

## Effect on B017

1. Use directly witnessed చుట్టుకొలత for perimeter in this unit; it need not carry a “provisional formal term” warning. Do not extend that status to unattested formal terminology.
2. Define it in learner prose as the total distance once around a **closed boundary**, or equivalently the sum of all boundary-side lengths for a polygon.
3. In the three source problem diagrams, count every labeled boundary edge once, including inset/notch/stair edges. Do not add area, infer scale from drawing, or count an internal shortcut.
4. Preserve the source units: feet for source image002 and inches for003/004. The official Telugu witness uses meters, but that is terminology evidence, not authorization to convert source values or units.
5. The focused witness supplies terminology and reasoning support only. It does not validate the OpenStax exercises as Telangana grade-level tests or establish an AP regional preference.
