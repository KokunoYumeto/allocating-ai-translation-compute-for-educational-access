# m81295 `fs-id1358621` Bengali multiply peer review

Review date: 2026-09-02. Reviewer: independent model peer agent `m81295_multiply_final_review`.

Status: **CLOSED–PASS**. The reviewer owns only this report and did not edit the source, overlay, canon record, translated CNXML, reader, media, builders or receipts. This is model-peer review, not human West Bengal Bengali-language/teacher, representative learner, assistive-technology or publication certification.

## Final bound evidence

- Pinned source `provenance/modules/m81295.source.cnxml`: `c22d14bb2b833ed20ea5a7aa95d0e50b7810e8930834bd61993b8431dcfd02c3`.
- Final overlay `translations/m81295-fs-id1358621.bn-Beng-IN.json`: `c30f11bccda5033e5cca716e76b2e55a99ea7947ff005958b7451db658c2fdef`.
- Final canon record `canon/sections/m81295-fs-id1358621.json`: `1859b66b624337aaeaabe9f6ce1adf6774f2b1f38c711e9ae3651eb002165346`.
- Final translated CNXML `translations/m81295-fs-id1358621.bn-Beng-IN.cnxml`: `fc2fab34d1a7f44fd495c326f13d21711d99561c3a220c5f9234ef3fe070b105`.
- Final section reader `reader/sections/m81295-fs-id1358621.html`: `1040a822ac13a74eac56d177e6c8421476d5f043650d1970db732744e54dfd02`.
- Final section receipt `qa/sections/m81295-fs-id1358621.json`: `77479abb66eda029f23f828a1ddca3f798d0159e0c0da3828fc74d6b1b25805d`.
- Final section browser receipt `qa/browser/sections_m81295-fs-id1358621.json`: `2f5382e2f7ac00f41badc413bfcf6fa0efe7f519edc2cb3f4137480d6f0de03d`.
- Final builders: `scripts/build.py` `c4da8b071ff7e690ff8b530625ea3b33c53091631740cf1fa7e86977cb766451`; `scripts/build_sections.py` `9448f28a30578e8ad9333d9580afcc8d99ea0a9df7fddfb3503030874f3e349d`.
- Browser-QA script `scripts/visual_qa.cjs`: `44e4244f85e1b5ff0f7541e07f73b26d7748a264a322d05b00178a8887d496ab`.

The canon verification block independently agrees with all five output hashes above and records `html_fragment_characters: 34874`. A fresh source/target parse passed 775 nodes, 126 unique IDs, identical tag/ID/child order, exact nonlocalized attributes, and 72 exact MathML signatures. Counts also agree at 37 paragraphs, 8 tables, 4 examples, 12 exercises, 12 problems, 12 supplied solutions, zero source-absent solutions, 15 images and 2 links. There are zero three-letter English runs in learner text/translated accessibility fields outside MathML and zero hits for the punctuation gates (`.।`, `।.`, `।।`, doubled `?`/`!`, punctuation before danda, or whitespace before terminal punctuation).

## Recurring consultation of actual Tripura and West Bengal canon

This review did not rely on the ledger alone. Before paired review, I read the complete OCR and opened the actual page images for SCERT Tripura VI pp.57, 58 and 78 and West Bengal Class 7 Learning Bridge p.189. During the wording/answer audit I reopened the actual Tripura pp.58/78 and West Bengal p.189 images. Immediately before browser QA I reopened the actual Tripura p.57 and West Bengal p.189 images. The reviewed witnesses were:

- Tripura p.57 OCR/image: `6a094d3c1d9f4001ef4f8b6f046ac87dc64956df181cfdb17ad6d58b1c73b6a0` / `7e9e25e29ee2ab73f7306f2c114fb26f601085512a6cd4893b350dcf79e87e2d`.
- Tripura p.58 OCR/image: `ddd30a1e805d0f7b396a7adeb2bc0664e50764127c1c5d1c8171da948b120ac1` / `246558790d2b90acaf4f266cc5da4a77fc85a82b5671903303337747adb53596`.
- Tripura p.78 OCR/image: `fc04fa39ee4cb6fefe96844df67c4a847d9b86c210cd0de5cc512bb65ca5299d` / `1da4354782cd73208e4e360c4f5f30e8bc0d1e3376778617b5a9795caa123c48`.
- West Bengal p.189 OCR/image: `f2855cddf52aae63862e8de962c9f178f084d25319994c37f2182d2dbaac1e6c` / `c55d1f090e29adaf5053e21ad875b0c0e01c5d94f24afba0f9b6fad04da80c00`.

Tripura pp.57–58 support `দশমিক`, explicit retained written zeros and the place labels `দশাংশ`, `শতাংশ`, `সহস্রাংশ`; the visibly bad 12.74 row on p.57 was excluded. Tripura p.78 and West Bengal p.189 directly witness ordinary multiplication/product register and `গুণফল`. They support distinguishing the result `গুণফল` from each factor `গুণনীয়ক`, but do not independently establish the complete signed-decimal placement algorithm. `দশমিক ঘর` and `স্থানধারক শূন্য` therefore remain transparent editorial language tied to the pinned OpenStax mathematics, pending the human reviews listed below.

## Mathematics, answers and errata

All twelve source-supplied answers were recomputed with exact decimal arithmetic and agree: `15.8925`, `27.4815`, `87.6148`, `−42.558`, `−13.427`, `−38.122`, `0.00135`, `0.00348`, `0.00603`; `5.63 × 10/100/1000 = 56.3/563/5630`; `2.58 × 10/100/1000 = 25.8/258/2580`; and `14.2 × 10/100/1000 = 142/1420/14200`. The three introductory products `0.3 × 0.7 = 0.21`, `0.2 × 0.46 = 0.092` and `0.01 × 0.004 = 0.00004` also agree.

All five source-errata records have a visible or accessibility-safe disposition while preserving source MathML/pixels:

1. `source_math_error_preserved` (`fs-id1388460`, `fs-id2151159`, `eip-id1168466081784`, `eip-id1168466166411`): the incorrect source row `56.3(10)` remains exact; the Bengali warning and accessibility text identify the required `5.63(10) = 56.3`.
2. `source_accessibility_partial_product_shift_omitted` (`eip-id1168465059325`, `eip-id1168466119810`): the source description omits that written row 12225 is shifted left and represents 122250. The Bengali image/table descriptions now state that place value; `36675 + 122250 = 158925` agrees with `4075 × 39`.
3. `source_aria_corrected` (`eip-id1168469608226`): the source ARIA both omits the shift and says 42588/42.588. The Bengali description states that written row 4152 represents 41520 and gives the body-MathML result `1038 + 41520 = 42558`, hence `−42.558` after sign/decimal restoration.
4. `source_prose_omission_preserved` (`fs-id2284313`): Bengali expresses the intended “same number of places” and visibly discloses the missing source word.
5. `source_alt_corrected` (`eip-id1168466166411`, `eip-id1168469895446`, `eip-id1168469782705`): the three generic English arrow descriptions are replaced by accurate Bengali descriptions of one-, two- and three-place decimal-point moves.

## Fifteen source rasters and Bengali alternatives

Every original raster was opened at full/original detail and paired with its source and final Bengali alternative. The section receipt independently confirms the same bytes, SHA-256 and Git blob for all 15 files. The checked sequence is:

1. `018_img.jpg` `03680402ebaf2481463a9b2526f4d4aeffa949043fb7b7af97872be3cfce648c`: fraction/decimal pattern and five total decimal places accurately described.
2. `019_img-01.png` `7d32c1a9140f3afbc72657d2d98f9a0b466b242af5d485daed23eff1ea95fcea`: initial vertical `4.075 × 3.9` layout accurately described.
3. `019_img-02.png` `1b4793a2008855ed16d53da0315daf728b547839034a42ccf7a0201522e3d6b3`: partial products and the shifted 12225 row accurately described by represented place value.
4. `019_img-03.png` `05b47dcf6a81ff66f358cc06f9f3535d0cb5cbef7f62a3f8ec482de2fee5e732`: four-place decimal placement and `15.8925` accurately described.
5. `020_img-01.png` `d8e852caa979d1ff0c9677b706ef1aa9118ff7190bed81c4022cd855cacbb6b7`: one plus two decimal places for `−8.2 × 5.19` accurately described.
6. `021_img-02.png` `4f7a4d7f26fb0a63f07e4ead021690a44bf3e5717fed8bb4c8764e76f4d16de6`: initial `0.045 × 0.03` vertical setup accurately described.
7. `021_img-03.png` `9d5c42b0ae796898ad67ce542bebded609bd3d741c9d6cbef8151d3f7ed35537`: whole-number partial result 135 accurately described.
8. `021_img-01.png` `d030d5845c701d537b7998662c414826012d73571e6e3bb137ef76e105336b42`: two plus three decimal places accurately described.
9. `021_img-04.png` `2ef1ac2139d5c180225f1014bc93baf7403f560ef28ed2f3f1d7d16f4fdd1535`: `0.00135`, arrows and required placeholder zeros accurately described.
10. `022_img.jpg` `9a0970cd1b1195a79ca84ff28766c9ee6f08ff495d908878daf5768d7a1b9e64`: `1.9436` multiplied by 10/100/1000 with retained trailing zeros accurately described.
11. `002_img.jpg` `1a2ff86f659d3670dc7aff900d95efed06d2356653d464d9bb0dbb8956be1f4e`: `45.86 × 100 = 4586` and two-place arrow accurately described.
12. `003_img.jpg` `5ced9625ffb1999bf9d77d0409db8e44b3d39e0624d0c10f654461ef1adb726f`: `2.4 × 100 = 240`, two-place arrow and added placeholder zero accurately described.
13. `023a_img-01.png` `a1c218a6500b6c3bfa66979d96251c65c7cdebfc6266dce28df667cf73cb00f3`: actual one-place move accurately described; source Math error separately warned.
14. `023b_img-01.png` `0042e041806021fe2b8f08d6fb560ee418c32ecab3b6ef6e940ad0339752e9ac`: actual two-place move accurately described.
15. `023c_img-01.png` `0765e904852f45f34b0ecfe59427bd6525b3bb3a95d3b1803670aa6f8f0cd202`: actual three-place move and new placeholder-zero position accurately described.

All 15 final alternatives are nonempty Bengali, preserve the visible numerals, and expose the meaningful arrow/colour/position information rather than repeating the source's generic wording.

## Findings and final visual closure

R1 — narrow long-numeric table overflow (resolved). The final scoped rule in `build_sections.py` affects only tables `eip-id1168469608226`, `eip-id1168469489639` and `eip-id1168469481183` below 480 px; the generic `build.py` is restored to its bound hash. At 390 px the two relevant multiplication tables fit a 284 px table rectangle; independently measured MathML right edges remain at or before 331 px in the 390 px viewport. There is no document horizontal overflow.

R2 — shifted-partial-product accessibility arithmetic (resolved). Initial target alternatives repeated the misleading source implication that the written rows themselves summed to the result. The final overlay explains the left shift/represented values for both `12225 → 122250` and `4152 → 41520`; the new/expanded errata above bind the correction.

R3 — stale post-fix canon verification (resolved). The final canon record now binds overlay `c30f11bc…`, CNXML `fc2fab34…`, reader `1040a822…`, section receipt `77479abb…`, browser receipt `2f5382e2…` and the independently reproduced 34,874-character rendered fragment.

The established repository harness ran on an isolated mirror of the exact reader with `C:/Program Files/Google/Chrome/Application/chrome.exe`, bundled Playwright and external requests blocked. At 1200 px: scroll width/client width `1200/1200`, height 11,927, 15/15 images loaded and labelled, 72 measurable MathML roots, Bengali font present, 14 captures, zero overflow and zero page errors. At 390 px: `390/390`, height 16,146, the same 15 images and 72 MathML roots, Bengali font present, two prescribed endpoint captures, zero overflow and zero errors. No long-division/cancellation assertion applies, and no scroll region is required by this final scoped solution.

I inspected every generated capture: all fourteen 1200 px tiles, both 390 px endpoints, and two additional 390 px captures centred on the formerly affected tables. Their sorted filename/SHA-256 manifest digest is `ec16640ba392b7717c859a1c2fcd647a8e2a6afcc9d901fad8032e7996668aa1` across 18 captures. The full desktop sequence covers every learner block, all 15 rasters, the visible 56.3(10) source warning, all four examples, all twelve exercise/solution pairs and the footer. The two narrow endpoints wrap cleanly; the targeted narrow captures show the affected table content legibly, while full-document geometry confirms the off-capture remainder. No clipping, overlap, broken image, obscured warning, duplicated content or unreadable math was found. The learner-subtree English gate excludes required reader attribution/footer text and source-pixel lettering, which remain visible and are exposed by Bengali descriptions.

Narrow visual review consists of the prescribed endpoints plus the two affected-table captures and full-document geometry; it is not a claim of a complete 16,146-pixel manual narrow sweep. Static inspection does not replace keyboard or screen-reader testing. External links were preserved but not navigated because the harness blocks external requests.

## Conclusion

No unresolved actionable source-pairing, mathematical, answer, Bengali wording/punctuation, image-alternative, accessibility-description or layout finding remains for m81295 `fs-id1358621` in the bound bytes. Human West Bengal Bengali-language/teacher review, representative learner review, assistive-technology testing and publication approval remain pending. **CLOSED–PASS.**
