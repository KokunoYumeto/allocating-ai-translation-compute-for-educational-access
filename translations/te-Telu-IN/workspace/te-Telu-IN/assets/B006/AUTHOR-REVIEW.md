# B006 diagram author review

2026-08-31. Bounded asset work only:23 original raster images and23 new
code-native bilingual SVGs. This is the diagram author's mathematical and
layout review, **not independent review, native-speaker approval, or completion
of TE-B006/the full translation assignment**. Main's reader and independent
review remain separate.

## Primary material actually read

- Read the complete frozen B006 subsection, metadata and all23 media descriptions.
- Read `canon/B006-rounding-witness.md`, then existing Telugu+English OCR for
  TS6 PDF14/printed4, PDF15/printed5 and PDF17/printed7 before inspecting their
  complete page images. No new OCR, PDF rendering or canon acquisition.
- Read exactly the23 selected media members in the verified complete prealgebra
  ZIP. Inspected every full original raster before drawing. Original bytes remain
  unchanged, totaling276046 bytes. Verified archive SHA256, selected ZIP CRCs and
  selected pinned Git blob SHA1s. No bulk extraction or repository expansion.

Concrete canon effects: witnessed nearby-tens/hundreds/thousands wording is
paired with English; target place differs from its single right-hand neighbor;
147,032's controlling hundreds0 is retained;75 uses the stated upward tie
convention. TS6 carry examples support regrouping arithmetic, not a claimed
official Telugu rounding algorithm. The known erroneous21504 factor row on
PDF15 was not used. No AP terminology or native approval is inferred.

## Reconciliation of source pixels and descriptions

| Asset | Actual source-image evidence | Localized treatment |
| --- | --- | --- |
| 019,020,021 | Teal/turquoise dots and selected labels at76,72,75, although source alt calls dots orange;70/80 red; unit ticks70..80. | Dark teal point/selected label, red endpoints; exact positions. No answers inserted in line images. |
| 022,032 | Tens-place arrow to7; right digit6/2 underlined and compared with5.032 pixels say `ten's place`. | Underlines and arrows retained; standard `tens place` plus Telugu. |
| 031,033 | Ones digit crossed out; add1/do not add1; replace with0;80/70 below. Only031 visibly includes the nearest-ten result caption. | Same crossing, actions and results.031 caption translated and preserved bilingually; none invented for033. |
| 034_img-02,03,04 | 843 with3 underlined in both02/03;840 with0 underlined in04. Files are PNG despite frozen JPEG MIME attributes. | Distinct media mappings remain; required0 retained; originals untouched and localized files are SVG. |
| 035_img-02 | Add1 at hundreds6; replace lower digits58 with0s;23,700. | Bracket covers58 only; exact target/result. |
| 036_img-02 | Visible text says add1 (9+1=10), write0 **in hundreds**, add1 **to thousands**;3,978→4,000. Table/problem request nearest hundred, control tens7. Frozen alt incorrectly says nearest thousand. | Correct hundreds target and carry, not the wrong-target alt. Exact source image and frozen source remain preserved. |
| 037_img-02,03 | Hundreds0 underlined in147,032; final147,000 has no label/underline. | Do not skip0 or erase trailing zeros. No new final label/underline. |
| 038_img-03 | Visible text says add1 (9+1=10), write0 **in thousands**, add1 **to ten-thousands**;29,504→30,000. Problem/table request nearest thousand, control hundreds5. Frozen alt incorrectly says nearest ten-thousand. | Correct thousands target and carry; replace only lower digits504 with0s. |

All source neighbor marks are underlines, not circles. New operation panels
include a contextual bilingual target heading. Layout, palette and brackets are
editorial code-native adaptations, not edits to the source rasters. The source
international comma grouping and all displayed digits/answers remain exact.

## Checks and actual rendered inspection

- `python -B te-Telu-IN/scripts/make_b006_assets.py --self-test`:
  **PASS23 diagrams and159 rejected actual-SVG corruption fixtures.** Checks
  visible digits/commas, exact target/neighbor geometry, control digit0, labels,
  underlines, point positions, arrows, carry explanations and required zeros.
  Intermediate images reject inserted answers. Same-answer/wrong-target
  regressions are explicit; answer-only validation is insufficient for036/038.
- `python -B te-Telu-IN/scripts/make_b006_assets.py --verify`:
  **PASS** source/metadata/archive identity;23 original CRC/Git blobs;
  deterministic23 SVGs and manifest; actual-SVG mathematical checks.
- Followed browser skill. Existing runtime selection returned `No browser is
  available`; troubleshooting discovery returned an empty list. Used isolated
  headless Edge via the existing local Playwright dependency, no signed-in
  profile or network upload. `render-author.cjs` generated23 complete PNGs and
  actual SVG-text bounding-box data under `author-render/`.
- **Viewed all23 generated PNGs**, not only browser metrics. Text fits the
  canvas; label/arrow relationships and carry blocks remain readable; no
  clipping was observed. All23 actual text-bounds checks pass. Checked the
  three number-line points, comparison labels, all single-digit underlines,
  target arrows, replacement suffixes, final zeros and both carry panels.
- This standalone render does not test the integrated reader's table layout,
  keyboard scrolling or mobile presentation. The manifest's pending separate
  visual-review field refers to that main/integrated review.

## Identity receipt

| File | Bytes | SHA256 |
| --- | ---: | --- |
| `sources/TE-B006.en.cnxml` |25116| `b0644c64501fbf41c50c2119a5e1b68c7d0c4294eeaa82dca3f495c4853df2af` |
| `canon/B006-rounding-witness.md` |17277| `bc9b867310c95bc7abae4afc09c4c76565d6976213b22d0051a8dc5993b36da7` |
| `scripts/make_b006_assets.py` |38982| `8f45bc00c9f86c20e9d1fd791295cdd83e46d6587c2908cafa3f91a106650b1e` |
| `assets/B006/manifest.json` |43471| `3c66eb0cda2cc16323f14207416796d98ac8b991b83634ea8319f0b1ec3ef392` |
| `assets/B006/preview.html` |11902| `8b390bf23dbb3e0ce9de315612616512793df7997cd31b85db2712aca6a8acd0` |
| `assets/B006/author-render/bounds.json` |38773| `4ec4c9cc4e8f376106b269e0e3632fcc854baf58bdc706fe0d2f5dc40cfa30b0` |

The manifest records each original and localized hash, original source URI,
relative path, media/figure ID, selected ZIP member/CRC and pinned Git blob ID.
All23 new SVGs total58442 bytes. This receipt records the exact inspected
generation; subsequent changes require fresh checks.
