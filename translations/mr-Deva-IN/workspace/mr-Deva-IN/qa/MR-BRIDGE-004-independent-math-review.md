# MR-BRIDGE-004 independent source/mathematics review

Command: `python -B mr-Deva-IN/tools/test_unit4_math.py`.

Result: 13 tests passed against the actual frozen unit: eleven real-unit/source tests and two strict-parser tests. These are not synthetic copies of the translation. The suite reads 32 pinned EN/ID fragments and the eight exact canonical English JPEG assets, without writing files or requiring a build.

Verified XML SHA-256: `0733c4a1630584e1c6451e3af34cf39d8d85a12173657720b541fbf3fe826430`.
Config SHA-256: `c631a5f89cf810776470cb0e7099d00bf33b26f42961682a68b96616440a7ecf`.
Unit provenance-lock SHA-256 after the LF metadata normalization: `ea27b6983090ee38be922112d22df9755b19d804e3efb3695d688e2b434638eb`.

2026-08-31 integration note: the initial review used lock hash 00948a46541ee46f257405aa1ec030187c5d8c2a4d6b2e7eed847cad65f3cd85. D046 corrects only the parent-lock line-ending witness. Selected source fragments, config, translation, image bytes and HTML remain unchanged; the primary agent reran the mathematical suite against the normalized lock.

## Independently checked

- All twelve finite relation datasets; all twelve domains and twelve ranges are computed by projection with exact `Fraction` values and deduplicated sets. Names and dates are compared through explicit English/Marathi month correspondences. Set ordering is not treated as mathematical content.
- First four pair sets against actual EN and ID MathML. Six source-supplied answers against the canonical English solution text. Six added answers remain visibly marked original and do not masquerade as source solutions.
- Sixteen ordered source-block locators and all sixty original IDs across those blocks, including nested IDs, in source order against both languages; preserved problem/solution nesting and all twelve bidirectional answer links.
- All eight English rasters, 201–208, were personally viewed during this independent pass. Mapping arrows were followed to their endpoints; graph coordinates were read from the actual grids. Their exact SHA-256 hashes are pinned in the test, so a substituted redraw cannot silently pass as the reviewed image.
- Image alt mappings, graph points and labeled axis bounds; forty displayed mathematical strings also agree with the unit config. There is no claim that text checks replace visual inspection of the rendered reader.

## Discrepancies resolved during this pass

The draft initially retained Amy → 14 February from inaccurate source alt text. English raster 202 actually shows Amy → 24 February. The parent corrected the Marathi alt, relation and range; tests now require 24.

English raster 205 confirms the point (-2,-1), not the erroneous (-3,-1) in its source alt. Raster 208 confirms (-1,-3) and (2,6), not the alternate endpoints in its source alt; (0.5,1.5) is retained exactly. Those coordinate corrections were already in the draft and independently confirmed here.

This pass additionally found two inaccurate alt descriptions of axis labels: raster 205 labels run from -5 to 5, not -6 to 6; raster 208 labels run from -7 to 7, not -10 to 10. The parent corrected both. Rasters 206 and 207 label -6 through 6.

The independent pass did not visually inspect the Indonesian redraws. Claims about their differences belong to the separate source reviewer/parent review, not this test suite. Both Indonesian and English text fragments were checked for source IDs and the first four MathML relations.

The source's E7 `+100` is retained and interpreted as the same number as 100. The source artifact `17. 2` is normalized to 17.2 when comparing numeric meaning. BMI values are treated solely as supplied mapping labels; no clinical recalculation or validation is claimed.

## Canon consultation and limits

Read the relevant search-readable Cartesian-coordinate paragraphs in the Marathi Vishwakosh [आलेख entry](https://vishwakosh.marathi.gov.in/24316/): horizontal/vertical axis order, sign orientation and explicit scale choice informed the grid check. Direct opening failed; the successful search retrieval supplied the prose. Its line-joining example was not applied to these finite dot relations.

Read the opening definition/image-set paragraphs in [फलन](https://vishwakosh.marathi.gov.in/27548/). The distinction between actual output images and the codomain informed deduplication of range values. The existing Marathi term मूल्यसंच was not changed to the reference's variant कक्षा. No image-only formulas or unviewed canon illustrations are claimed as read.

Remaining work belongs to separate reviews: browser layout/image decoding, suitability of all Marathi prose and alt descriptions, native-speaker/teacher review, and continued translation beyond this twelve-question group. This pass does not complete the module, A20, or the five-book assignment.
