# TE-B008 assets: author production and validation receipt

2026-08-31. Bounded asset work only, not a completed unit/book or the full
translation assignment. This receipt is by the asset author, **not** an
independent visual reviewer or a native-speaker approval. The main task owns
the final integrated reader review. No translations, source freeze, source
archives, build scripts, locks or general logs were edited by this subtask.

## Actual inputs and selected extraction

Read the actual frozen media nodes, their enclosing problems, and the complete
self-check section, including its three follow-up confidence routes. This
asset receipt does not claim a full prose or all-exercise review of B008.

- Frozen B008 subsection: `sources/TE-B008.en.cnxml`,
  `fs-id2279009`, SHA-256
  `7f7ce451bd8f7757bd0bd515db42de196d26f68f41bec22959876e797e259a14`.
- Pinned OpenStax prealgebra commit:
  `38cae454e644abf9f0a623e876994553881597c9`.
- Existing complete ZIP: 537455794 bytes, SHA-256
  `effdf2dbb6dfd9cab771b568c6575d8074be4a1f9565f1fedbd54f621e138917`.
- Exactly the five named image members were read; CRC and selected Git blob
  SHA-1 checks passed. Existing originals are never overwritten on mismatch.
  Total preserved original bytes: **1259541**. No download or bulk extraction.
- The manifest records every source path, original/localized path, exact hash,
  ZIP member/CRC, Git blob, media ID and available figure ID. The first four
  images occur directly inside problems, not separate source figures.

Viewed every original fully using its preserved file, after extraction. A
first oversized multi-image tool response was truncated; that response was
not treated as inspection. Each image was then successfully displayed in
small subsequent calls and checked directly.

| Original suffix | Actual dimensions | Direct pixel observation | Preserved SHA-256 |
| --- | --- | --- | --- |
| `201_img.jpg` | 243×404 | Five 10×10 flats; six 1×10 rods; one unit. | `5dca1f3e0d7aad2e2fd1c5caf9345e4ddf3d6b4c3eeceaa592d12a5eaa8d3e5d` |
| `202_img.jpg` | 243×285 | Three flats; eight rods; four units. | `2dc89eb539e106cf1adfc463345f006446c10d4e178e2be600698c612fa92ffb` |
| `203_img.jpg` | 243×266 | Four flats; no rods; seven units, originally six on the left and one on the right. | `9e7c9dac10e181bad91e58062aff485a1f832714afa14538a12be2a15fb94327` |
| `204_img.jpg` | 243×392 | Six flats; two rods; no units. | `e0dc7bd082bd818e0f1efa7f6da87778cbc63afd5020d00cbb862cb07986266d` |
| `AppB_001.jpg` | 649×219 | Four columns, seven rows including header; six objectives and three rating options; all 18 response cells blank. | `d26ade53426ac1d159f56857f8ee337914b1c8719c6dc70edff70356b502eacd` |

The supplied base-ten alts agree with these pixels. No source pixel/count
discrepancy was found in this asset set. The generic checklist alt does not
enumerate its six rows; they were transcribed from the original pixels.

## Canon consulted at this stage

Read existing Telugu+English OCR before inspecting the complete corresponding
page image. No new PDF, rendering or OCR was required. OCR mistakes were
resolved against the visible page; OCR strings are not treated as final text.

- TS Class 2 PDF42 / printed30, `downloads/canon/ocr/TS-p042`:
  the 746 and 805 place/place-value/face-value tables visibly use
  **వందలు, పదులు, ఒకట్లు**. The 805 example and final zero statement distinguish
  an empty place count from the remaining place columns. Applied in the 407
  and 620 diagrams: keep the labeled empty tens/ones column, not a false block.
  TXT SHA `8b81712a2e430118c4a23f4bbc9dd3bbc6f53b607525da9f1bfc81bc92491a18`;
  PNG SHA `fb1eab02c2afa6b1bd2e1accd597ecd94d4e476fc09109a0171c7dccdd14fe13`.
- TS Class 6 PDF26 / printed16, `downloads/canon/ap/TS6-sets-026`:
  the page explicitly names సహజ సంఖ్యలు and displays N starting at 1;
  adding 0 yields పూర్ణాంకాలు and W starting at 0. Applied to the checklist's
  first row and all whole-number objectives, avoiding the previously rejected
  integer label. The `ap` folder name does not make this Andhra Pradesh evidence.
  TXT SHA `d51c819b172a78fdb1f7e48adece0f6a74cde4e8bf8463de32894245f4150d14`;
  PNG SHA `e22496bf6269a98db819536ee6101ca8f7cf404e81b556d34f2f6a1dde0c1867`.
- TS Class 6 PDF14 / printed4, `downloads/canon/ap/TS6-naming-014`:
  nearby-place wording **సవరించి రాయడం** appears in actual explanation and
  specified tens/hundreds/thousands tasks. It supports the checklist's explicit
  specified-place rounding wording; the checklist adds no new rounding rule.
  Its 85→90 tie convention was visible, not inferred from the faulty OCR strip.
  TXT SHA `caf98a4bc0e0671ba27332b9fe4ff29e48d0ba7c164c2668ce2ec27c457680b0`;
  PNG SHA `0d276babd6be0f1137511e71585eb3a91fa527033dae10ce11c5d40d302351a3`.

The Class 6 reread was a final wording check after draft generation. It
confirmed the proposed strings; no retroactive pre-draft consultation claim
is made. AP comparison and native-language approval remain open.

## Adaptation choices

1. All five outputs are new static, code-native bilingual SVGs. No source
   raster is altered or embedded. Reuse of B002's unit-cell drawing primitive
   is explicit; counts and layout are new B008 specifications.
2. Equal 12px unit squares form every block: exactly 100 per flat, 10 per rod,
   and one per single unit. Flat arrangement supports up to six blocks without
   overlap. Color and arrangement change from the originals; mathematical
   amounts do not. Labels are Telugu first, English second.
3. No visible numeral answers, group-count numbers or equations appear in the
   four practice diagrams. Accessible descriptions retain the counted-object
   descriptions already provided by the source. Internal checks confirm
   561/384/407/620, but do not print them into the exercise artwork.
4. Checklist wording was coordinated with the B008 translator. Headers are
   `నేను చేయగలను…`, `నమ్మకంగా`, `కొంత సహాయంతో`, and
   `లేదు—ఇంకా అర్థం కాలేదు!`; the final `ఇంకా` is a learner-friendly “not yet”
   phrasing, not a preselected state. English header punctuation uses
   typographic ellipsis/dash; the meaning is unchanged.
5. All six English objective sentences remain visible, in original order.
   The Telugu naming/writing rows explicitly distinguish words from numerals.
   The third Telugu row says identifying the occupied place, consistent with
   the source exercise's supplied place-name answers; the exact English
   “identify the place value of a digit.” is preserved beneath it. This is an
   explicit contextual clarification, not a claim that place name and digit
   contribution are identical. The translator handles that distinction in
   the separate prose bridge.
6. All 18 rating cells are completely blank. There are no ticks, score,
   claimed mastery, automated assessment, or invented correct selections.
   This remains a static diagram; no interactive form was added.
7. The model SVGs are 900×560, recommended minimum width 900px; the checklist
   is 1480×780, recommended minimum width 1480px. The local preview has a
   focusable horizontally scrollable region. The integrated reader must
   independently retain usable scrolling/accessibility.

## Verification performed

- `python -B te-Telu-IN/scripts/make_b008_assets.py` — PASS, five originals,
  five SVGs totaling **308718** bytes, archive SHA/CRC/Git blobs checked.
- `python -B te-Telu-IN/scripts/make_b008_assets.py --verify` — PASS, checks
  existing original bytes, actual SVG structure/math, deterministic output
  bytes and the complete manifest without download/extraction or file writes.
- `python -B te-Telu-IN/scripts/make_b008_assets.py --self-test` — PASS:
  five valid cases and **58 rejected in-memory corruptions**, no files written.
  Fixtures cover missing/extra unit cells and groups, overlapped cells,
  wrong scale/index/color, false zero-count blocks, leaked answers,
  raster embedding/invisibility/clipping, changed table geometry/language,
  missing response cells, ticks and untexted marks, and wrong objective text.
- Reran both read-only modes with before/after SHA-256 snapshots of all
  **21** then-existing owned files; every hash remained unchanged. This receipt
  was subsequently extended with the check result and canon hash anchors.
- Browser skill runtime discovery returned `[]`; no attached browser was
  available. Used isolated headless Edge without a signed-in profile via
  `assets/B008/render-author.cjs`, not a silently substituted attached browser.
- Edge rendered all five SVGs with loaded fonts. `getBBox` tests found no text
  outside its canvas or, for the checklist, outside its own cell. All five
  resulting PNGs were viewed completely. Actual flats/rods/units and empty
  columns remain distinguishable; bilingual rows/headers are readable and
  all response cells are blank. No author-visible clipping/overlap finding.
- Author render bounds receipt: `author-render/bounds.json`, SHA-256
  `ecc09843d1552d5c3f83f4551f5b48742a44f02f983116adc3e831ab955c7a97`.
  It includes each rendered SVG's SHA-256. These author screenshots are not
  claimed to be independent review of the author's own assets.

Generator `scripts/make_b008_assets.py`: 24457 bytes, SHA-256
`442f6cae5e8fc920676ff7c6d09505bc1146235b3e4a71bcd375be035f429668`.
Manifest: 10071 bytes, SHA-256
`a542e38e1e812e8fe4776b62f2511cdcd612ca9cc3ab4256b0fe953b6ae0ea6c`.

No actionable asset finding remains at this handoff. The main task still
must inspect these assets within the generated reader and complete the
unit-level translation/content/accessibility review.
