# MR-BRIDGE-016 — independent mathematics and source review

2026-08-31. **PASS for the bounded source/math review: 26 tests, no skips.** No new mathematical or source-fidelity defect was found in the frozen draft. The two disclosed source-alt errors are genuine and correctly distinguished from the unchanged original images. The final q27 method clarification is mathematically correct and visibly original.

Role: this reviewer did **not** draft MR016. I read the actual Marathi XML/config, the complete selected English and Indonesian source trees, and all 24 original image files. Writer notes were clues, not authority. I authored only `tools/test_unit16_math.py` and this report. Root supplied the final freeze/release notification before final input pins were adopted. No XML/config/shared-ledger edit, browser action, HTML/PDF access, new extraction, download, deletion, commit or publication was performed by this reviewer.

This is not reader-format acceptance, human/native-Marathi approval, module completion or five-book completion. The assignment remains active.

## Reviewed scope and immutable inputs

The actual pinned `m81374` Chapter Review container is `fs-id1167836524742`. Its first topic child is `fs-id1167824674139`, “Graph Linear Equations in Two Variables.” MR016 preserves both wrappers and every non-title direct child of that topic. The final selected exercise is `fs-id1167836626758`; the next actual sibling is **`fs-id1167829740806`, “Slope of a Line.”** Neither that group nor the four later topic groups nor the subsequent Practice Test is covered by this review.

| Census independently checked | Result |
| --- | ---: |
| Ordered source selections | 40 |
| Heading/instruction paragraphs | 13: five bold headings, eight instructions |
| Original exercises | 27 |
| Supplied answers | 14: ten graph images, four textual answers |
| Explicit source-answer omissions | 13; all even-numbered local questions |
| IDs inside selected blocks | 132 |
| IDs including the two original context wrappers | 134 |
| Total target IDs | 136: original IDs plus article/credits |
| Original problem MathML items per source locale | 39: 25 equations and 14 coordinate tuples |
| Original solution MathML items per locale | 3, plus q3's textual choice tokens |
| Target `data-check` strings | 49, not the earlier coordination estimate of 46 |
| New questions / supplied replacements for missing answers | 0 / 0 |
| Local links / HTTPS references | 34 / 3 |
| Original images / personally viewed files | 12 / 24 (12 EN plus 12 ID) |
| Frozen fragments | 80, totaling 48,636 bytes |
| Witness pins | 101 |
| Committed canonical assets | 12, totaling 850,595 bytes |

All 14 supplied answers are the odd-numbered local questions. All 13 even-numbered questions have exactly one explicit, original `source-answer-missing` notice and no manufactured source-solution container. The q16 and q17 images are problem images, not additional supplied graphical solutions. The local numbers 1–27 are target-unit numbering, not asserted original book numbering.

| Frozen file | Bytes | SHA-256 |
| --- | ---: | --- |
| `translations/MR-BRIDGE-016.xml` | 36,416 | `cb4f1a89aa7d0762f003898aaef5315bccad05d5b61dc94e0011a4232f229025` |
| `units/MR-BRIDGE-016.json` | 4,941 | `85cdd3e51d3378fe82b99cf130f2f7925c948c68b52c1ba4cd65bd37de1e7b5c` |
| `provenance/MR-BRIDGE-016.lock.json` | 121,267 | `689ddf28c14356985a14975dae9047669694643e7dcf8a95ff49927d93e4c99a` |
| `tools/test_unit16_math.py` | 38,986 | `0e77d24a4cb0f95e672d71a5fec4e70184b1b285cbbd9a06c48b68420f91f44b` |

The suite requires these real files and existing ignored source inputs; missing files fail, never skip. It reads only selected ZIP members into memory and does not duplicate corpora or extract archives. The root freezer records full-archive hashes. This suite independently verifies selected module/image bytes and ZIP-member CRCs; it does not claim to rehash every byte of the large archives on each run.

## Actual source reading and preservation

English archive: `downloads/mr-Deva-IN/releases/A20-canonical.zip`; member prefix `osbooks-prealgebra-bundle-38cae454e644abf9f0a623e876994553881597c9`. Indonesian archive: `downloads/mr-Deva-IN/releases/A20-v0.3.0-source.zip`; prefix `source`. Both use `modules/m81374/index.cnxml`.

| Source member | Bytes | SHA-256 |
| --- | ---: | --- |
| EN m81374 | 247,327 | `021c29fa9a6ab3d5b06d2ef143a82d2ac818ed25fe6fd44ebf5d7a6be07a123a` |
| ID m81374 | 247,303 | `d89a74aef766afca6a4ac7e1ae720f120d22cc771c11dd7e025c55bca1fabb8e` |
| EN m81369, title-backreference witness | 182,816 | `0ca3b9284188e75f0fda3b59093ece79f5e174152095a057e69d2889be79abd2` |
| ID m81369, title-backreference witness | 171,955 | `bdeb65b4170314ab51629262742d77943ce6e9221a5863bca4ce294dfec6cbb2` |

I read both complete selected topics in bounded source-text chunks, including the title link, every intervening heading/instruction, every problem, supplied solution, fraction structure and original media alt. The 80 frozen fragments were then parsed and compared to their exact original selected elements: tags, attributes, text, internal tails, order and descendants all match. Only serialization prefix spelling and a fragment root's following whitespace are irrelevant to that comparison. Every original ID occurs once, in original preorder with the same nearest preserved original ancestor, in EN, ID and the target. The wrappers are not miscounted as two extra selectors.

The original title link has only `document="m81369"`, not a target-element ID. The target retains that document identity and the corresponding official section URL. I inspected the pinned EN/ID m81369 titles and shared UUID `9d3bc1f0-6330-4e24-b67a-6f07f074d79c`; I did not audit its entire teaching content or claim current network availability. The target says that the teaching section is not fully translated here and the link needs internet. All 34 local anchors resolve, including both directions of all 14 original problem/solution pairs. The three external references are the title backreference and two attribution links. The existing CC BY-NC-SA 4.0/component-credit wording remains present; this was not a new license audit.

## Exact mathematical checks

The standard-library parser accepts only rational numbers, x/y, signs, arithmetic/grouping and affine expressions. It rejects unknown tokens, nonlinear products, nonconstant/zero divisors and incomplete expressions. It never uses `eval`. Source MathML fractions are interpreted structurally rather than concatenating their numerator and denominator. All 25 source equations are compared using exact `Fraction` coefficients of `Ax + By = C`; coordinate tuples are compared exactly. The three original textual coordinate answers are checked against both source locales and the equations/images. The 49-string map check is explicitly a regression, **not** an independent mathematical proof.

| Local question | Actual mathematical content checked | Source-answer status/result |
| --- | --- | --- |
| 1 | (−1,−5), (−3,4), (2,−3), (1,5/2); correct coordinate order and quadrants III, II, IV, I | Graph349 shows the four separate labeled points |
| 2 | (−2,0), (0,−4), (0,5), (3,0); all on the intended axes, not the origin | Source answer absent; remains explicitly absent |
| 3 | 5x+y=10 tested at (5,1), (2,0), (4,−10) | Supplied ⓑ/ⓒ correct; ⓐ gives 26≠10 |
| 4 | y=6x−2 tested at (1,4), (1/3,0), (6,−2) | Reviewer computes true/true/false; no source answer added |
| 5 | y=4x−3; intercepts (3/4,0), (0,−3) | Graph351 correct; wrong source-alt pairs visibly corrected |
| 6 | y=−3x; shared origin intercept | Source answer absent |
| 7 | y=(1/2)x+3; intercepts (−6,0), (0,3) | Graph353 correct |
| 8 | y=−(4/5)x−1; intercepts (−5/4,0), (0,−1) | Source answer absent |
| 9 | x−y=6; intercepts (6,0), (0,−6) | Graph355 correct |
| 10 | 2x+y=7; intercepts (7/2,0), (0,7) | Source answer absent |
| 11 | 3x−2y=6; intercepts (2,0), (0,−3) | Graph357 correct |
| 12 | y=−2 is horizontal; no x-intercept, y-intercept (0,−2) | Source answer absent |
| 13 | x=3 is vertical; x-intercept (3,0), no y-intercept | Graph359 correct; not mislabeled a function y(x) |
| 14 | y=−2x and y=−2 are different lines on common axes | Source answer absent |
| 15 | y=(4/3)x and y=4/3; unique intersection (1,4/3) | Both branches of graph361 correct |
| 16 | Graph220 rises through (−4,0), (0,4), consistent with y=x+4 | Source answer absent; reviewer intercepts are not supplied answers |
| 17 | Graph221 falls through (0,3), (3,0), consistent with x+y=3 | Supplied (0,3),(3,0), including original order, correct |
| 18 | x−y=−1; intercepts (−1,0), (0,1) | Source answer absent |
| 19 | x+2y=6 | Supplied (6,0),(0,3) correct |
| 20 | 2x+3y=12; intercepts (6,0), (0,4) | Source answer absent |
| 21 | y=(3/4)x−12 | Supplied (16,0),(0,−12) correct |
| 22 | y=3x; both intercepts are the origin | Source answer absent |
| 23 | −x+3y=3; intercepts (−3,0), (0,1) | Graph362 correct |
| 24 | x−y=4; intercepts (4,0), (0,−4) | Source answer absent |
| 25 | 2x−y=5; intercepts (5/2,0), (0,−5) | Graph364 correct |
| 26 | 2x−4y=8; intercepts (4,0), (0,−2) | Source answer absent |
| 27 | y=4x; origin and second point (1,4) | Graph366 correct; source-alt correction and original method note correct |

The extra computed values for unanswered questions in this review are reviewer calculations, not newly translated answers or additional source coverage. No missing source solution was invented in the target.

All 47 described point occurrences on the eleven line images satisfy the respective exact equations. The two three-point sets on figure361 are assigned to their correct, different lines. With straightness personally inspected, two distinct points determine the corresponding line; proportional affine coefficients verify line identity. This is not an assertion that finitely many grid samples prove an arbitrary function's behavior. Axis extents describe the displayed window; arrows continue the lines and do not define finite mathematical domains/ranges. Figure349 remains a finite set of unjoined points.

### Disclosed errors and q27's original clarification

- Figure351's actual EN and ID alts both contain (1,−1) and (2,3). Neither satisfies y=4x−3. The original pixels rise with y-intercept −3 and agree with the correct pairs (1,1), (2,5). The Marathi alt uses correct data and an explicit original note preserves and identifies the erroneous source pairs. Original JPEG bytes and the question equation are unchanged.
- Figure366's actual EN and ID alts contain (−1,4) and (1,−4), the opposite-slope line. The actual pixels rise through the origin as y=4x, agreeing with (−1,−4), (1,4). Again the bad source pairs are disclosed, not silently substituted or presented as correct answers.
- For q27, the two axis intercepts coincide at (0,0); that single point alone cannot determine a line. The added second solution (1,4) is distinct, gives 4=4·1, and determines the correct line together with the origin. The note explicitly says it is newly added and that the source supplied only the answer image. These are the three final extra keys that bring the frozen target to49. They do not convert any of the13 missing answers into translated solutions.

## Personally inspected original image evidence

I opened **each** file in `downloads/mr-Deva-IN/source-image-qa/MR-BRIDGE-016/` using the filesystem image viewer at original detail: all twelve `en-` copies and all twelve `id-` copies. Before relying on them, their bytes were compared with the exact corresponding source ZIP members; the suite repeats this binding. All twelve EN/ID pairs are byte-identical, but the second locale was still personally viewed. No raster was generated, edited or resized on disk.

Every basename below is `CNX_IntAlg_Figure_03_06_NUMBER_img_new.jpg`. The hash applies separately to the viewed EN and ID originals and to the canonical committed EN asset.

| Number | Personally read pixel content | Bytes each | EN/ID SHA-256 |
| --- | --- | ---: | --- |
| 349 | Axes−5…5; a(−1,−5), b(−3,4), c(2,−3), d(1,2.5); separate dots | 69,596 | `620da1000c5b91d660e591a7976f06ebd441fe669e1f1f699a21c1157ea0f576` |
| 351 | Axes−8…8; upward line, y-intercept−3 and x-intercept between0and1; compatible with y=4x−3 | 68,876 | `10c1ece5d9a51b8810b589a12662b65ba23ef54858441e2148890dd0b6452178` |
| 353 | Axes−8…8; upward line through (−6,0),(0,3) | 68,149 | `945978fb6a91ed76208644f06375d39a280b83c60f0c02b289e8e727c975f3fa` |
| 355 | Axes−8…8; upward line through (0,−6),(6,0) | 66,192 | `3460bfb9cf8ab25bf95e10c1ed367b1ec9b64a45175c80034d14ef284ef23c0a` |
| 357 | Axes−8…8; upward line through (0,−3),(2,0) | 67,492 | `16a1d2c4e7005b046f886497aff6022c4bac7fa8cbe39cd3c09f07f7117132b3` |
| 359 | Axes−8…8; vertical line at x=3, up/down continuation arrows | 63,029 | `3faf2645daffc6cf1e3ca1d51bb2009d1cd2b6bd6aa97b091dbd0e7ada9c84ff` |
| 361 | Axes−5…5; horizontal line above1 and upward line throughorigin; intersection atx=1, compatible with exact4/3 | 73,722 | `13326c6df7d1e3eda526d12f33a349004a367d6fc9c7792cb546b0b8f1326ad8` |
| 220 | Axes−8…8; upward line through (−4,0),(0,4) | 89,752 | `d59317fcdf00670419e0ded9bed3c289700c29eef5aff0494ab0e75b5b9e7ae3` |
| 221 | Axes−8…8; downward line through (0,3),(3,0) | 91,251 | `3cc11b03b1c088fabcd2900afdd6ba6b7108fc690be874cac605f74b7eebb227` |
| 362 | Axes−8…8; shallow upward line through (−3,0),(0,1) | 64,427 | `dfd154e26be8cb14db6703dc3d325316590b321f15854dc8ca7b5c362f1502cc` |
| 364 | Axes−8…8; upward line through (0,−5), crossingx-axis between2and3 | 63,966 | `0da4da5aafe6fa434b97723c7ebda5a8b1c73c182178280100c44bc479ee7163` |
| 366 | Axes−8…8; steep upward line throughorigin, compatible with (−1,−4),(1,4) | 64,143 | `602f610ce4b3f830c3a2406e819f76e502244f07f9b71e1e6ef0ebac9f12ecc4` |

Each locale totals850,595bytes; the24viewed files total1,701,190bytes. Numerical fractions in alt descriptions are corroborated by exact equations; I do not claim to measure exact fractions solely from low-resolution raster coordinates. All line images visibly retain continuation arrows. The test binds the twelve original media IDs, order and problem/solution ancestry as well as the files.

## Fresh Marathi canon actually read during review

These were current review-stage readings, not assumptions carried from earlier units. No new canon ID or global terminology promotion was made.

1. **C12**: existing OCR `downloads/mr-Deva-IN/canon/ocr/balbharati8-85.txt`, physical page85 / printed page75 of the official [Balbharati Grade8 mathematics book](https://books.ebalbharati.in/pdfs/801020004.pdf). I read the opening definition of उकल through substitution making both sides equal, and the same-operations discussion including division by a nonzero number. It informed the q3/q4 membership checks and q27's explicit substitution. The source OCR's garbled worked formulas were not used. No fresh PDF/page-image examination is claimed. OCR bytes:2,474; SHA-256 `f9bf9c42edb3e126573bc14f4671aa5c062920ee145c50590fdac6733af52a9b`.
2. **C18**, [आलेख](https://vishwakosh.marathi.gov.in/24316/): a fresh official-domain search returned readable primary prose. I read the जात्याक्ष description of perpendicular horizontal/vertical axes, signed positions, origin and ordered coordinates; then the equation-graph passage defining solution points and distinguishing an equation graph from blindly joining sampled observations. This checked सहनिर्देशक/आदिबिंदू, x/y orientation, the unjoined q1 dots and the all-solutions line wording. The full classroom compound काटकोनी सहनिर्देशक पद्धती remains an authored phrasing, not an asserted quotation. No unread inline image formula was adopted.
3. **C19 access failure, then C14 fallback**: the fresh targeted C19 search did not return the intended फलन page, and direct opening `https://vishwakosh.marathi.gov.in/27548/` returned502. Neither is counted as a successful C19 reading. I then freshly retrieved and read [C14, फलन (Function)](https://marathivishwakosh.org/21979/), specifically its plain-language one-and-only-one output condition and the work-allocation example where multiple outputs for one input invalidate a function. This independently checked why x=3 must remain a linear-equation graph, not be described as a function y(x). Its inline QuickLaTeX images were not read or used. No new reference locator was needed.

## Test run, evidence limits and handoff

Command: `python -B mr-Deva-IN/tools/test_unit16_math.py`.

Result after root release/freeze: **26/26 PASS, zero skips.** Tests cover exact frozen input pins; both actual module/backreference members; complete source boundary;80exact fragments;134original IDs/preorder/ancestry;13headings/instructions;49unique target checks;39problem expressions;25symbolic equations;14coordinate tuples; all textual supplied answers;47line-point occurrences; vertical/horizontal distinctions; the fractional two-line graph; both source-alt corrections; q27's original note;14bidirectional answer pairs/13honest omissions;12canonical assets;24review-byte records; axes/arrows;34local/3external links;101witnesses; and parser negative controls.

Development note: the first run's sole failure was a test-author heading selector that counted any source emphasis, including italic x in an instruction, as a bold heading. I inspected the actual `effect` attributes and restricted that selector to `effect="bold"`; the true source census is five headings. No target change was required. Subsequent full run passed.

Inventory hashes in the suite use sorted UTF-8 rows joined by LF with a final LF: fragments are `target_id|locale|sha256`; source images `locale|filename|sha256|bytes`; target math `key|text`; witnesses `path|sha256`. They bind the manually reviewed observations to these inputs; they are not substitutes for reading or mathematics. Changed images, text or source pins require renewed review, not merely updating constants until tests pass.

The review is deliberately bounded. It does not verify live availability of outgoing URLs, automatically interpret image pixels, establish native-speaker quality, validate accessibility, or inspect/accept HTML or PDF. No alternative browser surface was used after the recorded policy denial. The13absent source answers remain reader-visible omissions. Future source production starts at `A20:m81374#fs-id1167829740806`; format review and broader five-book translation remain root-coordinated work.
