# A10-002 language and source notes

Status: self-reviewed Western Punjabi Shahmukhi draft. Native-speaker, local educator, independent rendered structural QA and mobile/desktop reading review are not certified by this note. The complete A10/A20/A30/B10/B40 assignment remains unfinished.

## Exact source boundary

The English authority is `downloads/complete-upstream/osbooks-prealgebra-bundle/modules/m82452/index.cnxml`, module “Introduction to Whole Numbers,” in the independently identified A10 collection `col31130`, *Elementary Algebra 2e*. The pinned OpenStax repository commit is `38cae454e644abf9f0a623e876994553881597c9`. The full module SHA-256 is `0eaf5db27fd4e16e70d34d4b936abe173b93699e267b519e449c7b56f7233310`.

This unit contains all 20 remaining direct children of section `fs-id1170655083568`, starting `fs-id1170655113270` and ending inclusively `fs-id1170655197222`. These are canonical child indices 13–32, counting the original title as index 0. The original section container ID is retained, but its title and first 13 children are not repeated. There are 107 new IDs, or 108 retained IDs including that repeated section container. No following section is included. The immediate next canonical node is the standalone paragraph `newelem_para01` about variables; it must not be skipped by jumping to a later section. A10-001 and A10-002 together cover this first section, not all of m82452. Earlier collection items m82630 (Preface) and m82451 (chapter Introduction) are not covered by this unit; their separate work is outside this checkpoint.

The Indonesian comparison was actually read from `downloads/extracted/A10/translated/modules/m82452/index.cnxml`, SHA-256 `940ad448d8b2788984f386405131866fe32abb95f0f9c2a901ca1f4e3619a6fb`. The selected English XML was read completely and the same Indonesian 20-child remainder was read, then re-read in two bounded ranges during revision. Indonesian is a comparison, not permission to silently repair canonical English.

## Source inventory and translation schema

There are exactly 92 `source_blocks` keys in source document order:

- 32 paragraphs, 8 titles, 14 media alt strings and 15 list items.
- 3 table summaries translated from `aria-label`, plus all 20 table-cell scaffold keys, including 3 intentionally empty cells.
- 14 exact source MathML trees: 11 numeric/operator trees and 3 spacing-only trees; no MathML tables.
- 3 source CNXML tables, with 4×2, 3×2 and 3×2 cell layouts; one source figure and 14 original images.
- 4 worked examples, 8 Try Its, 12 exercises/solutions, 3 how-to notes, 5 lists, one term ID, 7 source newlines and 18 circled part tokens.

Keys are element IDs, `parent-id/title`, `media-id/alt`, `list-id/item/N`, `table-id/summary` and `table-id/row/N/entry/N`. Summary and alt strings are plain text. Empty table cells are empty strings, not omitted cells. Two empty source table labels remain structural nodes, not invented text blocks.

The templates use 14 immediate `{{math:0}}` occurrences, 13 `{{child:0}}` structural-child placeholders and one `{{link:0}}`. Child placeholders refer to immediate media/table/list children, never descendant math. The two source math periods stay terminal in the target question templates; no punctuation relocation or MathML edits are needed. Leading-zero groups 098, 061, 004, 051 and 073 retain their source forms wherever written in digits. The source’s comma-based three-digit grouping is not converted to lakh/crore grouping.

## Actual canon consultations

The actual local `scripts/read_canon.py` was used, with unit-specific unique receipts. Existing local HTML witnesses were present; no fresh canon download was needed. Each call displayed the chosen passages for reading. Receipt generation alone does not prove language quality. The script’s old generic `application` strings are not treated as evidence of this unit’s decisions; actual effects are recorded below.

| Stage | Exact receipt | SHA-256 |
| --- | --- | --- |
| Source analysis | `canon/receipts/A10-002-next-unit-20260830T225827605659Z.json` | `564bbbc14d4ca16d3023f0654972cf5802c37a8536a7fc7d6e5aa38c62567b6d` |
| Draft | `canon/receipts/A10-002-draft-20260830T231202830463Z.json` | `03931eb22cdf957ca472dbfce41bf0b9e4af390e4311a293194f0f508b259ea7` |
| Revision | `canon/receipts/A10-002-revision-20260830T231950759426Z.json` | `df1a507d24b6de040f005b3e0a14b4042f7e19b6a23b4b7e107c7ecbed5d09e0` |
| QA | `canon/receipts/A10-002-qa-20260830T232727969760Z.json` | `3ba626c11f3fd01bd8393a56d2bd7c003c460d0ca557be45fde636331f166577` |

Source analysis read C01/C02/C03/C04/C07/C09/C10/C11. Draft added C12. Revision and QA read C01/C02/C04/C07/C09/C10/C11/C12. These passages come from the existing R1/R2/R3 Jamil Ahmad Pal essays; they provide prose/register evidence, not mathematical terminology certification.

Actual influence:

- C01’s ability construction informed Punjabi inflection in the historical estimate paragraph’s “آکھ سکدے ساں”; this is adaptation, not a claim that that complete phrase appears verbatim in the canon.
- C02’s instruction/obligation register supported reader-directed لکھو، لبھو، کھچو and the obligation construction in the three-place rule. Revision changed the drafted agreement to “تِن جگہاں ہونیاں چاہیدیاں نیں.”
- C04 guided plural agreement for ہندسے، پیریڈاں، ہدایتاں and نیں rather than replacing Punjabi grammar with Urdu ہے/ہیں.
- C07’s ordinal/location constructions informed دوجے خانے and تریجے کالم in the image descriptions.
- C09 supported the adapted reminder “چیتے رکھو” in the ones-period instruction and original bridge.
- C10 directly influenced the separately labeled carry qualification “ایہہ گل وضاحت منگدی اے,” rather than modifying the source’s overbroad instruction.
- C11 informed “کیوں جے” in the rounding explanations.
- C12 informed “ہُن اسیں” for the explicit reversal from word names to digits.
- C03 was consulted during study/draft but supplies no mathematical standard for “period” or rounding. No new fixed mathematical term was inferred from it.

## Number names and provisional vocabulary

The existing A10 choices are continued: پورے عدد، ہندسہ، جگہ دی قدر، پیریڈ، اکائیاں، دہائیاں، سینکڑے، ملین/بلین/ٹریلین. The new “گول کرنا” is a provisional explanatory choice for rounding, with a labeled Punjabi/Urdu/English key. It is not claimed as an approved local curriculum term. The bridge distinguishes it from drawing a circle.

Because number-name vocabulary was uncertain, the actual [Western Punjabi number-list data](https://en.wiktionary.org/w/index.php?oldid=91589273&title=Module:number_list/data/pnb), revision 91589273 (13 July 2026), was consulted during drafting. It is community lexicography, not a mathematical or native-review authority. It helped distinguish Punjabi forms such as اکاہٹھ، پینہٹھ، چھیاہٹھ، تہتر and the -ونجاہ and -یہہ series from mechanically substituted Urdu number names. It was not used to replace the source’s grouping convention. Orthographic/dialect choices such as یاراں، چوداں، ستاراں، اٹھاراں versus the page’s -ہ spellings are adaptations still needing native review. No Gurmukhi source was transliterated into the target, and no PDF/OCR claim is made.

A read-only numeric-association check parsed the selected Punjabi group names and confirmed these source-bound values:

| Source question/answer locus | Value |
| --- | --- |
| `fs-id1170655164902` | 8,165,432,098,710 |
| `fs-id1170654989620` | 9,258,137,904,061 |
| `fs-id1170654957397` | 17,864,325,619,004 |
| `fs-id1170655025082` | 9,246,073,189 |
| `fs-id1170655162842` | 2,466,714,051 |
| `fs-id1170655155164` | 11,921,830,106 |

The manual lexicon in that diagnostic only tests mathematical association; it is not independent attestation or proof of natural idiom.

## Source discrepancies: preserve first, explain separately

Correction explanations are in the explicitly original `bridge_after_html`, with stable IDs and `source_corrections` mappings. They are not folded into source-bound prose, alt or summaries. The later accessibility-delivery adaptation below adds separately original override mappings without changing `source_blocks`.

1. The source instruction that every digit left of the arrow remains unchanged needs a carry exception. The bridge uses the source’s own 103,978 example: 9+1=10 at hundreds, 0 written there and 1 carried to thousands, changing 3 to 4. Both source-bound occurrences retain the original claim.
2. Image 022’s alt describes two lines, underlined period words and brackets beneath phrases. Actual original-detail inspection shows four horizontal groups, bracket labels above phrases and arrows down to 9 / 246 / 073 / 189. Indonesian retains the inaccurate layout description.
3. Image 008c’s alt places the zero-replacement bracket there; it is actually in 008d. Image 008d shows intermediate 23,758 and the 23,700 conclusion in the right cell, not the first. Source and Indonesian alt positioning claims are retained, with a separate visual clarification.
4. The hundreds table summary twice calls 3 the hundreds digit/arrow target; it is 9. Indonesian corrects those references. The summary says the replacement bracket is under 7 alone; the original image shows it under 78. The source also locates final conclusions on the left although the actual CNXML final left cells are empty and conclusions occupy the right cells; all three source summaries retain this discrepancy.
5. Image 009c’s alt incorrectly describes nearest-thousand rounding. The question, source cell and actual image are nearest-hundred rounding, testing 7 and carrying after 9+1. Indonesian corrects the alt. Image 009b’s alt simply omits its underline under 7; the bridge supplements that omission without inventing it in source alt.
6. The thousands table’s row-2 instruction and summary incorrectly say to zero digits right of the hundreds place. They should refer to thousands, zeroing 978. Indonesian corrects both; target source-bound strings retain “سینکڑیاں.”
7. Image 010a’s alt wrongly describes underlined 3. The arrow points at 3, but 9 is underlined. Indonesian corrects it; the target source alt retains 3.
8. The ten-thousands table summary tests 0 against 5 instead of 3. The source cell and Indonesian summary correctly test 3 while leaving 0 unchanged. Target source summary retains the incorrect 0.
9. Four source image elements declare image/png for 010a/010b/011a/011b, although all four files are JPEG. Frozen source declarations remain unchanged; the asset contract records both declared MIME and actual format.

The opening “remove final s” instruction is not itself a typo: it concerns English plural period names. The faithful translation retains the LTR English s; the original bridge explicitly limits that instruction to English. Indonesian instead paraphrases it as singular form. The 2013 New York estimate remains a dated source example, not an assertion about current population.

## Original images, rights and renderer handoff

All 14 original images were actually viewed at original detail and checked with local image decoding. They total 3,635,803 bytes. All are JPEG, with exact original hashes and dimensions in the manifest. No source image was edited, mirrored, recropped or copied into reader assets during this translation-input phase. Subsequent authorized preparation may copy only those manifest-declared files.

The existing media authority CSV supplies hashes, sizes and Git blob identities, not per-image rights grants. The existing A10 notice/attribution policy remains binding; absence of an image-specific credit is not new clearance. Existing notice pins use the parent-integrated SHA-256 policy after CRLF-to-LF normalization only. No repeated supply or licensing audit was undertaken.

New renderer requirements are explicit in `manifest-a10-002.json`: valid mixed paragraph containers; source left/right column geometry retained; three empty cells; a nested bulleted list inside numbered step 3; four explicit Solution titles; seven newlines; one term ID; all 14 exact MathML trees; source figure versus unnumbered media distinction; and accessible original-correction destinations. The three label+newline+table solution paragraphs must not be wrapped in the short inline answer-group treatment. The four inline Try It paragraphs can retain that grouping. Large English images need local scrolling and fallback links without stretching or mirroring. Original additions and source structures must be counted separately.

## Checks actually performed at input handoff

A read-only recursive comparison found all 20 frozen child elements equal to canonical source in expanded tags, attributes, text, descendants and child tails. All 108 source IDs and their order match. All 92 keys and their order match a separately derived source traversal. Target fragments parse; all 14 math, 13 child and one link placeholder owners/index sequences match immediate source children. Seven newlines and 18 part labels match their source owners and order. All 54 source-prose bdi nodes are explicitly LTR. Unicode scans found no Gurmukhi or hidden directional controls in the translation JSON.

The individual image byte lengths, SHA-256 and Git blob SHA1 values match the pinned manifest; signatures confirm 14 JPEGs. The three table geometries and blank positions are preserved in the input contract. All bridge fragment links and all nine correction-group destinations resolve to declared source/bridge IDs. Existing notice logical hashes pass. Source-prose numeral multisets were checked by block; three literal “0s” labels were revised to retain numeric 0 in their faithful alt/summary translations rather than spelling that digit out. The source’s wrong 3/0 references remain intentional and traceable.

The six inline rounding answers were recomputed: 206,981 gives 207,000 / 207,000 / 210,000; 784,951 gives 785,000 / 785,000 / 780,000 for hundred/thousand/ten-thousand respectively. This is bounded mathematical self-checking, not independent QA. No rendered page, source-image accessibility delivery, phone layout or native-speaker approval is claimed here.

Initial input hashes before the later accessibility-delivery adaptation:

- Excerpt: `7ec9ded8624978ec796016e83a246232c4c22243aa4eeb27a142cb916ac87d50`.
- Manifest: `654f11d648edcf97973ab4946fcb919225f1f66e36cfbdc265d0c4ca165267e5`.
- Translation: `01ba66a200d9ef769cf94b85337fb2b4f3d8800d109caf4d010abd9c91b1e7d7`.

The next authorized phase is a scoped A10-002 prepare/build pipeline. Its generated reader and independent QA should be tracked separately rather than retroactively treating these draft checks as rendered verification.

## Later accessibility-delivery and scoped pipeline checkpoint

At the parent's explicit review request, six `image_alt_overrides` and three `table_summary_overrides` were added as clearly original descriptions. No `source_blocks` value changed. These original descriptions begin by labeling themselves as our clarification/correction. The reader preserves the exact faithful translations in `data-source-alt` / `data-source-summary`, announces the original corrected description in `alt` / `aria-label`, marks `data-description-origin="original-correction"`, and supplies visible advisory links plus `aria-describedby` to the stable original correction IDs. The known wrong source digits are therefore traceable without being the first description announced to assistive technology. The source-bound thousands-table instruction still faithfully retains its wrong hundreds wording, with its correction explained separately.

Actual additional canon consultations for these original descriptions were C07/C10/C11 in `canon/receipts/A10-002-revision-20260830T234715290961Z.json` (SHA-256 `b38168a09493abf8cc5f80b777398c6d7b7578f0f37040724bc53d735f8ecdfc`) and the same IDs at QA in `canon/receipts/A10-002-qa-20260830T235626610030Z.json` (SHA-256 `7d613add726cb0c45dbcb0ec75e2b600b7f55ba05bb29cfe43ed0441f98589d8`). C07 informed row/column locations, C10 the explicit carry qualification, and C11 the reasoning wording. These prose sources do not certify mathematical vocabulary or spoken-screen-reader quality.

The new `scripts/prepare_a10_002.py` and `scripts/build_a10_002.py` reuse existing A10 helpers read-only. Preparation copied only the fourteen declared original files, after validating source/target paths, pinned hashes, dimensions, JPEG signatures, media-authority rows and original Git blobs. Existing notice inputs are checked under logical CRLF-to-LF hashing. The generated `provenance/a10-unit-002-component-notices.json` retains the existing rights status, exact English source alts and declared-versus-actual MIME ledger; it does not assert new component clearance.

Two prepare/build runs were byte-identical: reader SHA-256 `50b10e13c1c1d35036f43d0f7ed3663728a020afd0f04e39075d4bd33d4dd7d2`, component record `9b7f4155377881f72bd7a79340956b3e4f9c537c99e25fca34cec5b506bf912b`. The updated manifest is `6d8bd544300fff3866bbe7f36ecfe9cf2710e8056d0e36cc586157a503973de3`; updated translation is `e0c4a710cfba7bf08f015546bee8626b39ceee6138c7d2a2a19761c0f0b7b337`. The frozen excerpt hash remains unchanged. Dedicated source-derived structural QA and the parent's visual/critical review are separate next gates; no native certification or complete-work claim is made.

The parent subsequently found narrow-screen clipping with the initial 700px table minimum. The unit-only builder CSS was reduced to 660px without editing source or shared CSS. The parent independently confirmed a 329.601px instruction cell fitting the 340px local wrapper, the full initial 103,978 visible, local scrolling to the original carry diagram, and unchanged 375px page width. The resulting reader SHA-256 is `6b9a1c45c521aa4d11502773c3327373fd1d4291ae4779a5a40e7579ce763a92`. This records the parent's actual bounded visual finding, not a native-language or universal assistive-technology certification. The separate `qa/structural-a10-002.json` records the current exact artifact hashes and source-derived test results.
