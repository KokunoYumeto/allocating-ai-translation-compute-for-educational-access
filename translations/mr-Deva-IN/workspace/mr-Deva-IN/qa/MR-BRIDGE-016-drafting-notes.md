# MR-BRIDGE-016 — first Chapter Review topic: drafting record

2026-08-31. Stable writer handoff. This is the drafting author's actual source/image/canon reading and consistency check, not an independent review or reader acceptance. Only this note, `translations/MR-BRIDGE-016.xml` and `units/MR-BRIDGE-016.json` were authored. Root owns freezing, asset configuration, builds, independent QA and shared logs. No Browser action, HTML/PDF build, bulk acquisition, publication, commit or deletion occurred.

## Exact boundary and counts

I inspected the actual pinned EN and ID Chapter Review hierarchy. Container `fs-id1167836524742` has six topic-group children. This unit takes the **whole first child `fs-id1167824674139`**, “Graph Linear Equations in Two Variables”, including its linked title and all opening/intervening headings and instructions. It ends at exercise `fs-id1167836626758`, immediately before the next sibling **`fs-id1167829740806`, “Slope of a Line”**. This is a thematic boundary, not an arbitrary question-count cutoff. The topic's subsection title links to source document `m81369`.

| Item | Count |
| --- | ---: |
| Direct selected blocks | 40 |
| Heading/instruction paragraphs | 13: five bold topic headings and eight instructions |
| Original exercises | 27 |
| Supplied source solutions | 14: ten graphical and four textual |
| Questions without supplied solutions | 13, explicitly marked; no replacement solutions supplied |
| Newly invented questions | 0 |
| IDs within selected blocks | 132 |
| Source IDs including topic and Chapter Review wrappers | 134 |
| All XML IDs including article and credits | 136 |
| Original image uses / distinct names | 12 / 12 |
| Personally inspected EN/ID image files | 24 |
| Displayed-math keys | 49 |
| Local anchors / HTTPS references | 34 / 3 |

All 14 supplied solutions belong to the locally numbered odd questions; every even question has an explicit missing-source-answer notice. These are source omissions, not translation omissions disguised as complete answers. The three HTTPS links comprise the preserved source-title reference and two attribution links. The local links comprise six navigation links and both directions for all fourteen source-answer pairs. Source-local numbering is not asserted: the header labels 1–27 as this unit's numbering.

The next five topic groups and the later Practice Test `fs-id1167836628671` are excluded. The whole Chapter Review census is 146 exercises, 73 supplied solutions and 55 image uses, but those totals are **not this unit's translated coverage**. No module/book/program completion is implied.

## Pinned source actually read

| Locale | Exact existing ZIP member | Bytes | SHA-256 |
| --- | --- | ---: | --- |
| EN | `A20-canonical.zip` / `osbooks-prealgebra-bundle-38cae454e644abf9f0a623e876994553881597c9/modules/m81374/index.cnxml` | 247,327 | `021c29fa9a6ab3d5b06d2ef143a82d2ac818ed25fe6fd44ebf5d7a6be07a123a` |
| ID | `A20-v0.3.0-source.zip` / `source/modules/m81374/index.cnxml` | 247,303 | `d89a74aef766afca6a4ac7e1ae720f120d22cc771c11dd7e025c55bca1fabb8e` |

Both actual topic trees, every selected paragraph, MathML item, solution and media alt were read in bounded pieces. Fraction structure was read as MathML fractions, not concatenated digits: the first problem's fourth coordinate is `5/2`, question 4 uses `1/3`, and the slopes `1/2`, `−4/5`, `4/3`, `3/4` are preserved. Canonical EN governs; the actual pinned ID version corroborates, rather than an Indonesian repository HEAD. Both trees have the same IDs, order and ancestry here.

The title's original `document="m81369"` is retained as `data-source-document="m81369"`, with an HTTPS link to the [official OpenStax section 3.1](https://openstax.org/books/intermediate-algebra-2e/pages/3-1-graph-linear-equations-in-two-variables). I opened its primary reader and verified the section title, rather than guessing the route. This was reference resolution, not substitution of current web exercise data for the pinned corpus. The reader explicitly says that the full Marathi teaching section is not present and the link needs internet. There is no original target-ID attribute to invent for this document-level link.

## Actual pixels and source corrections

The existing freezer's narrow command copied only these twelve named rasters from each already pinned archive into ignored `downloads/mr-Deva-IN/source-image-qa/MR-BRIDGE-016/`. It verified full archive byte counts and SHA-256 before reading the named ZIP members. I personally viewed **all 24 files**, each EN image and its ID counterpart. Later read-only comparison confirmed every review copy equals its exact archive member, and all twelve EN/ID pairs are byte-identical. Each locale totals 850,595 bytes, together 1,701,190 bytes. No raster was edited, generated, resized on disk or replaced by a translated redraw. Display scaling is not a new source file.

All names use prefix `CNX_IntAlg_Figure_03_06_` and suffix `_img_new.jpg`:

| Number | Role / local question | EN SHA-256 (also identical ID SHA-256) |
| --- | --- | --- |
| 349 | Answer, q1: four separate points | `620da1000c5b91d660e591a7976f06ebd441fe669e1f1f699a21c1157ea0f576` |
| 351 | Answer, q5 | `10c1ece5d9a51b8810b589a12662b65ba23ef54858441e2148890dd0b6452178` |
| 353 | Answer, q7 | `945978fb6a91ed76208644f06375d39a280b83c60f0c02b289e8e727c975f3fa` |
| 355 | Answer, q9 | `3460bfb9cf8ab25bf95e10c1ed367b1ec9b64a45175c80034d14ef284ef23c0a` |
| 357 | Answer, q11 | `16a1d2c4e7005b046f886497aff6022c4bac7fa8cbe39cd3c09f07f7117132b3` |
| 359 | Answer, q13: vertical line | `3faf2645daffc6cf1e3ca1d51bb2009d1cd2b6bd6aa97b091dbd0e7ada9c84ff` |
| 361 | Answer, q15: two lines | `13326c6df7d1e3eda526d12f33a349004a367d6fc9c7792cb546b0b8f1326ad8` |
| 220 | Question image, q16 | `d59317fcdf00670419e0ded9bed3c289700c29eef5aff0494ab0e75b5b9e7ae3` |
| 221 | Question image, q17 | `3cc11b03b1c088fabcd2900afdd6ba6b7108fc690be874cac605f74b7eebb227` |
| 362 | Answer, q23 | `dfd154e26be8cb14db6703dc3d325316590b321f15854dc8ca7b5c362f1502cc` |
| 364 | Answer, q25 | `0da4da5aafe6fa434b97723c7ebda5a8b1c73c182178280100c44bc479ee7163` |
| 366 | Answer, q27 | `602f610ce4b3f830c3a2406e819f76e502244f07f9b71e1e6ef0ebac9f12ecc4` |

Two genuine alt-text defects were reported to root and corrected visibly, without changing equations, original answers or pixels:

1. q5 / media `fs-id1167829850431` / figure351: EN and ID descriptions list `(1, −1)` and `(2, 3)` although the question is `y = 4x − 3`. The original graph agrees with that equation. Correct pairs are `(1, 1)` and `(2, 5)`; the other stated points `(−1, −7)` and `(0, −3)` already agree. Both the wrong quoted pairs and correct replacement pairs are clearly distinguished in an original note.
2. q27 / media `fs-id1167829755848` / figure366: EN and ID descriptions reverse the signs at the two nonzero points, giving `(−1, 4)` and `(1, −4)`, which describe the opposite slope. Both actual images rise as `y = 4x`. Correct pairs are `(−1, −4)` and `(1, 4)`, with the origin unchanged. Again the source-error note is explicit.

The remaining described points, axis extents and directions agree with the inspected figures and exact equations. Fractional locations are justified by the equation and source data, not a claim to measure exact fractions from low-resolution pixels. Figure349 preserves finite unjoined points; all line figures preserve arrow continuation. The question images remain question images, not misclassified supplied solutions.

q27 adds one clearly original method clarification: both axis intercepts are the same origin, which alone cannot determine a line; another solution `(1, 4)`, checked by `4 = 4 · 1`, gives a second distinct point. The source gives only the graph. This note does not claim the source supplied the working and does not fill any of the thirteen missing answers.

## Actual Marathi canon consultation and revision effects

At selection/drafting I retrieved and read [C18, आलेख](https://vishwakosh.marathi.gov.in/24316/), specifically the जात्याक्ष passage: perpendicular horizontal/vertical axes, coordinate ordering and construction of a point. It informed the x/y orientation, सहनिर्देशक wording, and point-placement instructions. The graph-definition passage also keeps equation solutions distinct from arbitrary joined observations. I did not apply its context-specific interpolation example to the four isolated points. A later direct find failed with an internal error/no matching text; that failed action is not recorded as a fresh reading. The successful primary search-reader prose was actually read, not merely a search title.

At drafting and revision I read the existing C12 OCR, physical page85 / printed page75 (`downloads/mr-Deva-IN/canon/ocr/balbharati8-85.txt`), opening prose defining उकल by substitution giving equal sides, and its same-operations discussion. It supports saying that a coordinate pair satisfies an equation, the exact substitution check, and the concise q27 method note. Garbled OCR mathematics was not used; no new PDF acquisition, OCR or page-image review is claimed here.

A fresh successful C19 opening-prose retrieval also reminded me that a function requires one output per permitted input. This first review topic includes a vertical line, so the title and instructions consistently say रेषीय समीकरणांचे आलेख, not that all these lines are graphs of functions. [C19, फलन](https://vishwakosh.marathi.gov.in/27548/).

“काटकोनी सहनिर्देशक पद्धती” is an authored classroom rendering of rectangular coordinate system, informed by C18's perpendicular-axis construction; I do not claim that full compound is directly quoted there. The source x/y symbols remain Latin. “धड्याची उजळणी” is an authored heading choice. No new canon locator/term is silently promoted, and unrelated advanced claims or unread formulas in web entries were not adopted. Final revision corrected an authored continuation sentence to say the next Slope group **plus four further groups**, not an extra sixth remaining group.

## Writer checks actually run

Read-only Python standard-library checks were run against the actual XML/config and both pinned source members; all reported PASS:

- All 40 selected IDs equal the actual topic's direct-child sequence, without overlap. Every original ID's descendant order and nearest preserved ancestry match both sources. Both context wrappers are present; all IDs are unique.
- All 27 source problems remain, all 14 supplied-solution IDs are inside their original exercises, all fourteen question/answer link pairs resolve, and only the thirteen actual source omissions carry `source-answer-missing`. No later-group ID is imported.
- Exact symbolic linear-expression coefficients and `Fraction` coordinate tuples compare all **42 source MathML items per locale** against the translated spans. This is coefficient/tuple identity, not a finite-grid proof. Punctuation and redundant fraction parentheses are normalized explicitly.
- q3's supplied ⓑ/ⓒ choices and all three textual intercept pairs are verified exactly. All **47 described line-point occurrences** satisfy their respective equations; the four figure349 points match the question. Both three-point parts of figure361 are checked against the correct separate line. Both bad alt pairs fail their equations and both corrected pairs satisfy them.
- All twelve target image names/order equal the source media sequence, and all 24 review files match the exact ZIP bytes. All final **49 displayed-math strings** match the config, including the three final q27 clarification keys. No config assets were inserted by this writer.
- The final hierarchy and ZIP-copy checks were rerun after revision; all local links and required terms were checked. Scoped `git diff --check` and an authored trailing-whitespace scan were clean. These ad hoc writer checks are not described as an independent test suite.

The narrow image-copy command was `python -B mr-Deva-IN/tools/freeze_unit.py --review-images MR-BRIDGE-016 A20 IMAGE...`, with exactly the twelve filenames in the table. It did not run the unit freeze/build modes. C: was checked before writing: initially 4,759,158,784 bytes free; final recorded check 4,621,045,760 bytes. No cleanup or large source copy was attempted.

Final writer pins, before root's expected config asset insertion:

| File | Bytes | SHA-256 |
| --- | ---: | --- |
| `translations/MR-BRIDGE-016.xml` | 36,416 | `cb4f1a89aa7d0762f003898aaef5315bccad05d5b61dc94e0011a4232f229025` |
| `units/MR-BRIDGE-016.json` | 1,983 | `aecc52bfff99e206ac9690df663a1532b1ede0c4f39daf887f3bf2c51b87881e` |

## Ordered selection locators

Every ID below has prefix `A20:m81374#`; the two surrounding wrappers are deliberately not extra selected blocks.

```text
fs-id1167836689070
fs-id1167833059130
fs-id1167836560058
fs-id1167836729981
fs-id1167836408579
fs-id1167836728880
fs-id1167829644642
fs-id1167836667122
fs-id1167829785046
fs-id1167836423872
fs-id1167833326537
fs-id1167829859281
fs-id1167836624857
fs-id1167826169944
fs-id1167836705576
fs-id1167829688321
fs-id1167836296637
fs-id1167833019205
fs-id1167829861802
fs-id1167836698868
fs-id1167833207874
fs-id1167836611473
fs-id1167836407159
fs-id1167824578489
fs-id1167836340022
fs-id1167836692041
fs-id1167829751646
fs-id1167833369799
fs-id1167836627814
fs-id1167836514020
fs-id1167836697400
fs-id1167824737382
fs-id1167836537272
fs-id1167829595359
fs-id1167829906596
fs-id1167829877972
fs-id1167833057045
fs-id1167824648910
fs-id1167836509101
fs-id1167836626758
```

Handoff limits: source freeze, independent source/math review, reader builds, visual inspection and human/native-Marathi mathematics review remain pending. Do not count this draft as an accepted reader or as completion of the remaining Chapter Review groups, m81374, any assigned book or the five-book workflow.
