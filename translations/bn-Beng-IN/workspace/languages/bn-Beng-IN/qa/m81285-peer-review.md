# m81285 Bengali integration peer review

Review date: 2026-08-30–31. Reviewer: model peer agent `pilot_review`.

Status: model integration review complete; all seven reported findings addressed and affected final render areas verified. This is not independent Bengali teacher, learner, or assistive-technology certification. The reviewer authored the number-line, model-equivalent-fractions, and section-exercise overlays; checks of those three blocks are explicitly self-review.

## Actual review coverage

- Read the pinned source `provenance/pilot/m81285.source.cnxml` and all fourteen completed overlay blocks through `build.translated` in read-only mode. All fourteen passed exact structure/ID/order/attribute checks and inverse linguistic-MathML checks. The source SHA-256 is `7a39fccee8a29712929f04a6ac02f4e2646e46a6920f6e8b06f56de40b7ffad4`.
- The module contains its title, objectives, two readiness notes, seven instructional sections, Key Concepts, complete section exercises, and glossary. The module receipt records 4,576 nodes, 938 IDs, 510 MathML expressions, and 100 images. HTML inspection independently found 938 unique IDs, no duplicate IDs, and no missing internal fragment targets.
- Opened and visually inspected every original desktop capture `tmp/bn-Beng-IN-visual/modules_m81285-1200-1.png` through `-69.png`, in consecutive batches without skipped tiles. These cover the entire original 61,628-pixel page with overlapping captures. Also inspected both original narrow captures `modules_m81285-390-1.png` and `-2.png`: page top and bottom only, not a complete narrow-page visual sweep.
- The original capture set was bound by the browser receipt to reader SHA-256 `04358d862ab5850a99bfdc97556970d30ff30f3239df6d74b79846c40f27c260`. Later source/renderer revisions must not inherit this visual-review hash without rechecking the changed output.
- Inspected the refreshed conversion captures `sections_m81285-fs-id2390912-1200-1.png` and `-3.png` after the long-division correction. Both enclosures are now visible.
- Readiness results 11 and −2 > −5, fraction/tile counts, mixed-number conversions, equality multipliers, negative-number ordering, visible supplied practice answers, and their picture descriptions were reviewed in the complete desktop sequence. This is visual/mathematical peer review, not a claim that every equation was independently machine-evaluated.
- The section-exercise source has 76 exercises, 38 supplied solutions, and 38 exercises without supplied solutions. The translation preserves that distinction; no missing source solutions should be filled into the source-faithful output.
- Independently compared the assembled CNXML with the source after integration edits: every tag and ID remains in source order; all 510 MathML trees retain structure, attributes, mathematical tokens, and internal tails. Exactly 20 changed linguistic `mtext` values match declared source/target exceptions. Also independently compared all 76 practice exercise IDs and their supplied-solution ID lists: exact match, including all 38 absent solution lists. This check used assembled CNXML SHA-256 `d7b8b474a19c17024d53f3f92975a38f4a4afc983c7855bdbe27ed2f83ad6664`; reader at that moment was `1af9ca724997120e77706b1234217320f1ff958359cfd3415f37aa6e5c4dc44d`.

## Canon consultation during this review

Read `canon/README.md`, the 16-entry `canon/examples.tsv`, and `canon/consultations.json`. Before the terminology/definition comparison, opened actual Tripura p.050/p.051 and West Bengal p.181 images. During the number-line review, reopened actual Tripura p.052 image and OCR. Before recording QA findings, reread the existing p.050, p.051, and p.181 OCR against the already inspected page images.

Concrete decisions:

- TR01 actually witnesses **মিশ্র ভগ্নাংশ**, **প্রকৃত ভগ্নাংশ**, **লব**, and **হর**. Its mixed-fraction definition explicitly says proper fraction. This informed findings R1 and R7 below.
- TR02 and WB02 support equivalent-fraction language and multiplying numerator and denominator by the same nonzero number. The project’s **সমতুল ভগ্নাংশ** remains consistent with its recorded **তুল্য ভগ্নাংশ** synonym; this review does not introduce another term.
- TR06 supports **সংখ্যারেখায় … অবস্থান দেখাও**. It is not a negative-fraction worked-example witness. Signed-number explanations and the figure-061 discrepancy were checked against the assigned source and actual pixels, not attributed to the canon.
- The incorrect intermediate denominator in Tripura p.051 and the improper “proper fraction” prompt in p.052 question 5 are excluded. OCR mathematical strings are not accepted as equation evidence.
- The bank supplies no exact music-measure, fudge, fraction-tile classroom-register, or negative-fraction worked-example witness. Those editorial choices still need independent language review; no canonical coverage is fabricated.

## Actionable findings and correction status

### R1 — Mixed-number terminology and suffixes

The definition at `fs-id2780329/fs-id2775051`, objectives, Key Concepts, and glossary used **মিশ্র ভগ্নাংশ**, while number-line `fs-id2784608` and practice `fs-id2299150` used **মিশ্র সংখ্যা** without a synonym bridge. Main chose to normalize to ledger T025 **মিশ্র ভগ্নাংশ**.

Post-replacement self-review caught malformed inflections in the two normalized overlays: **মিশ্র ভগ্নাংশর** must be **মিশ্র ভগ্নাংশের**; **মিশ্র ভগ্নাংশয়** must be **মিশ্র ভগ্নাংশে**. Affected locations include the number-line title, conversion prose, negative-number alts, and practice self-check alt `eip-id1164269592721`. These were reported immediately. Final revision verification pending.

### R2 — Positive scope of proper/improper classification

Original module desktop tile 16 showed `fs-id2780329/fs-id4315540` and `fs-id2388743` stating the numerator/denominator inequalities without the positive-number scope already present in Key Concepts and glossary. The earlier fraction definition permits integer numerator/denominator; the unqualified rule is false for arbitrary signed denominators.

Suggested Bengali qualification: **এখানে আলোচিত ধনাত্মক লব ও হরের ক্ষেত্রে, …**. Main reports applying it to both paragraphs without altering source MathML. Final rendered verification pending.

### R3 — Invisible long-division enclosure

Original desktop tiles 23 and 25 displayed source `menclose notation="longdiv"` as the misleading concatenations **611** and **833**. Exact source parents: `fs-id2687652` and table entry `eip-id1168469862094` in `fs-id2390912`.

Main added renderer-only CSS for top/left enclosure borders, keeping source CNXML/MathML intact. Reopened refreshed conversion desktop tiles 1 and 3: both long-division enclosures are visibly present, and the divisors/dividends agree with the original division pictures. **Visually resolved in refreshed section output**; final module hash still needs binding.

### R4 — Source number-line dot color

Number-line `fs-id2784608` alts described **লাল বিন্দু**, but actual preserved figures show teal/dark markers. The source English color description was not reliable. Main removed **লাল** from all twenty number-line alts and recorded a source-alt correction. Suggested Bengali is simply **বিন্দু**; positions and pixels remain unchanged. Final output recheck pending.

### R5 — Actual figure-061 mismatch and correction to the reviewer’s earlier claim

Original desktop tile 45 prompted reopening `downloads/canonical-prealgebra/media/CNX_BMath_Figure_04_01_061.jpg`. Media ID: `fs-id1269539` in the number-line section. The requested **−5/2 and +5/2** points are correct. The extra mixed-number points actually show **−1 2/3 and +1 2/3**, whereas the preceding source problem/figure 060 used **−1 1/3 and +1 1/3**.

The earlier reviewer-authored alt and consultation incorrectly claimed that figure 061 retained the preceding ±1⅓ points. This review supersedes that claim based on direct pixel inspection. It must not survive unqualified in `editorial_note` or consultation history.

Main has added an accurate Bengali description and labelled warning: **সম্পাদকীয় সতর্কতা: মূল চিত্রে অতিরিক্ত বিন্দুদুটি 1 পূর্ণ দুই-তৃতীয়াংশের ধনাত্মক ও ঋণাত্মক মানে দেখানো, কিন্তু আগের ধাপে আলোচিত সংখ্যাদুটি ছিল 1 পূর্ণ এক-তৃতীয়াংশের ধনাত্মক ও ঋণাত্মক মান। −5/2 ও 5/2-এর অবস্থান সঠিক।** Source pixels and mathematical questions remain unchanged. `source_errata` distinguishes this `source_image_mismatch` from mere English-alt corrections. Final rendered warning verification pending.

This finding must not be confused with practice figure 235 (`fs-id1891270`/`fs-id1788637`): that actual answer image correctly shows −1⅗ and +1¾. Only its original English alt was wrong. Likewise figure 218(b) has two squares; its circle wording was an alt error, not a wrong mathematical answer.

### R6 — Practice question/answer boundaries

Original desktop tiles 52–65 show adjacent exercises without visible exercise labels or distinct outer boundaries. Example: exercise `fs-id1787409` gives 1/3 with no supplied solution, followed immediately by exercise `fs-id1232648` giving 3/4 and a grey answer region. Similar adjacent pairs occur throughout the block. Although the DOM preserves each exercise and the top disclaimer explains absent source answers, the visual question-to-answer association is unnecessarily difficult.

Suggested renderer-only correction: visibly separate exercise containers and label existing solution regions **উৎসে প্রদত্ত উত্তর**. If adding exercise labels, use a clearly editorial self-link/ID or renderer numbering; do not invent source exercise numbers or absent answers. Reported to main as a bounded usability finding; disposition pending.

### R7 — Source mixed-fraction definition is underspecified

Source-following Bengali at `fs-id2775051`, `fs-id2369709`, Key Concepts `eip-123` item 1, and glossary `fs-id3330885` says a whole-number part plus merely **একটি ভগ্নাংশ**. TR01’s actual definition specifies a proper fractional part. The current literal wording would also fit a noncanonical form such as 1 + 5/3.

Suggested contextual clarification: **এখানে ভগ্নাংশ অংশটি প্রকৃত ভগ্নাংশ।** Keep the source `b/c` and `c≠0` expressions unchanged and scope the explanation to the positive models under discussion; negative mixed numbers are handled later. Main may add labelled explanatory prose or retain this as an explicit source-definition limitation. Disposition pending.

## Routing, coverage claims, and remaining limits

All inspected internal fragment links resolve to unique module IDs. External prior-example links correctly name the pinned m81268/m81275 source documents, and the number-line link labels the integer lesson. The two original OpenStax supplemental-resource URLs remain unchanged. External online availability was not tested; a pinned source-file link is not a translated interactive remedial lesson.

The module’s top notice accurately limits completion to this module while saying the whole book remains in progress. It states that source questions, supplied solutions, IDs, and pictures are preserved; absent source answers are not invented; original English image labels are explained in Bengali; independent language/teacher, learner, and assistive-technology reviews remain pending. The footer says the translation is unofficial and does not claim original-publisher approval. No new certification/whole-assignment-completion overstatement was found in the inspected module.

The separate AX-3 companion is intentional. Source self-check encouragement is translated source prose, not a validated learner assessment. The original English self-check image is preserved with Bengali description; it is not a localized interactive form. No target-language exemplar or mathematical source is certified infallible.

No learner output, overlays, source media, shared builder, or external destination was edited by this reviewer during integration QA. Only this review record is owned by the reviewer.

## Final verification and dispositions

The statuses below supersede the intermediate “pending” wording in the chronological findings above.

Final reader SHA-256: `1af9ca724997120e77706b1234217320f1ff958359cfd3415f37aa6e5c4dc44d`.

Final assembled CNXML SHA-256: `d7b8b474a19c17024d53f3f92975a38f4a4afc983c7855bdbe27ed2f83ad6664`.

Verified that `qa/browser/modules_m81285.json` binds this exact reader hash. Its automated checks report 100 loaded images and 510 MathML expressions at both widths, no errors/overflow, page widths 1200/390 respectively, and positive top/left borders for both long-division enclosures. Final heights are 74,886 and 93,652 pixels. Independently reran all fourteen final overlay preservation gates: pass. The independent full-CNXML comparison above binds the same final CNXML hash.

Actual final visual spot checks: desktop tiles **17, 18, 26, 28, 43, 45, 51, 57, 58, 61, 74, 82, 83, 84**, plus both final narrow top/bottom captures. The new set has 84 desktop tiles; this is **not** a claim of a second complete 84-tile manual sweep. The earlier complete 69-tile review is recorded separately.

- **R1 resolved:** normalized **মিশ্র ভগ্নাংশ**, correct **ভগ্নাংশের/ভগ্নাংশে** suffixes, readable final number-line title and prose; repository search found no malformed suffixes in m81285 overlays.
- **R2 resolved:** both lesson classification statements visibly include the positive numerator/denominator scope in final tiles 17–18.
- **R3 resolved:** final module tiles 26 and 28 visibly show both long-division enclosures, agreeing with the refreshed section checks.
- **R4 resolved:** color-neutral number-line descriptions visible in final tiles 45/51; positions remain unchanged.
- **R5 resolved with preserved-source warning:** final tile 51 visibly reports the actual ±1⅔ extra points and clearly distinguishes the prior ±1⅓ step; ±5/2 positions remain correct. The stale editorial retention claim was removed and the correction history explicitly superseded it.
- **R6 resolved:** separate bordered exercise containers and **অনুশীলন · এই প্রশ্নের লিঙ্ক** labels now distinguish successive exercises; existing untitled answers carry **উৎসে প্রদত্ত উত্তর**. Final tiles 58, 61, and 74 show questions without source solutions remaining separate and unanswered. No source numbering was fabricated.
- **R7 resolved as explicit source-definition clarification:** **প্রকৃত ভগ্নাংশ** now appears in lesson definition, Key Concepts, and glossary, visually checked in final tiles 17, 57, 83/84 and narrow bottom. Source MathML remains unchanged.

A non-blocking receipt-hygiene note was sent to main: aggregated source-definition errata should include exact source IDs and correction statuses, and the twenty-dot-color entry should carry a consistent correction status. This does not alter the verified learner output.

No further blocking defect was found in the inspected scope. Independent Bengali teacher/language, learner, and assistive-technology validation remain pending. Continue translation of the remaining assignment; this review completes only the m81285 integration-review block.

## Main integration rebind — shared cancellation CSS

Main rebuilt m81285 after adding a renderer-only `updiagonalstrike` fallback for m81286. Current reader SHA-256 is `38bc532e87598e7e44dfcec725f2a7b4aea0d76d4a6e22ac52731156b24a75a9`. An exact byte comparison against commit35b8743 proves that removing only the new CSS rule restores the prior reader byte-for-byte; this module has no matching cancellation enclosures. CNXML and all learner text are unchanged. The refreshed browser receipt binds this new reader and again passes both widths with the same74,886/93,652heights and84desktop+2narrowcaptures. This is a main-agent receipt rebind, not an additional full model-peer or human visual sweep; the actual visual coverage above remains the review evidence.
