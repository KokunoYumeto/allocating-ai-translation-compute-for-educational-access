# MR-BRIDGE-017 independent source and mathematics review

Review date: 2026-08-31. Reviewer: `/root/second_unit_builder`, an independent agent who did not draft MR017. The writer was `/root/freeze_regressions`. This review owns only the test and this report; it made no changes to the translation, config, source lock, shared ledgers, canonical assets or renderer.

Result: **PASS for the bounded source/mathematics scope below; 28 tests pass, zero failures and zero skips.** No new mathematical or source-preservation defect was found. The already disclosed source-alt and axis-label discrepancies were independently confirmed from original pixels. This is not HTML/PDF visual acceptance, accessibility approval, native-Marathi approval, module completion or five-book completion.

## 1. Exact reviewed inputs and boundary

The complete second Chapter Review topic, “Slope of a Line,” is `A20:m81374#fs-id1167829740806`, under chapter wrapper `fs-id1167836524742`. Its 50 direct non-title children run from `fs-id1167833047231` through `fs-id1167836792421`. Both pinned EN and ID modules have the preceding topic `fs-id1167824674139` and following topic `fs-id1167836526512` in that order. The selected topic contains 14 heading/instruction paragraphs (six bold headings and eight instructions) and 36 exercises.

The 50 selected blocks contain 165 original IDs. Preserving their topic and Chapter Review wrappers brings the total to 167 original IDs; the target has 169 unique IDs after adding its article and credits IDs. The tests compare the full original-ID preorder and nearest-original-ID ancestry, not merely presence in a set. They also check every ordered source locator against the lock and the actual module.

| Input below `mr-Deva-IN/` | Bytes | SHA-256 |
| --- | ---: | --- |
| `translations/MR-BRIDGE-017.xml` | 43,757 | `f868cd613b00687a133ad6ede745749a3d78d0a7ac1e4fb4d700a9bf6b38cbf1` |
| `units/MR-BRIDGE-017.json` | 4,955 | `48f84cca5607f9faa224a85c877b4af6e713bc2c6e0452adb39db5521a37d860` |
| `provenance/MR-BRIDGE-017.lock.json` | 138,123 | `9b71760ec987da9622e6a55b3737b2a2da34d58e26a41e4ef0d98084f5c70c6b` |

The whole XML and config were actually read. All 50 EN and 50 ID frozen source fragments were checked against the corresponding real ZIP-member elements, including their text, attributes, descendants and child tails. Fragment-root serialization tail whitespace is outside that comparison. All 100 fragment files, totaling 55,482 bytes, are SHA-bound to their frozen records and witnesses. There are 118 unique witness paths; all 118 actual files are hashed by the suite.

The source question and answer prose was read in original order from both complete selected topic trees. An initially truncated source-output segment was reread for blocks 20–24 before finalizing; missing output was not treated as evidence. Drafting notes were used only as clues after original-source and pixel inspection.

### Selected-member authority

Existing ignored archives, with no download or bulk extraction:

| Archive | Recorded archive SHA-256 |
| --- | --- |
| `downloads/mr-Deva-IN/releases/A20-canonical.zip` | `effdf2dbb6dfd9cab771b568c6575d8074be4a1f9565f1fedbd54f621e138917` |
| `downloads/mr-Deva-IN/releases/A20-v0.3.0-source.zip` | `a9c53c328be944e12b707d5cb16e289755eff0c603d1652bfca13dd572e780d7` |

EN prefix: `osbooks-prealgebra-bundle-38cae454e644abf9f0a623e876994553881597c9`; ID prefix: `source`. The test reads only `<prefix>/modules/<module>/index.cnxml` and the nine named media members from each archive.

| Locale/module | Member bytes | Member SHA-256 |
| --- | ---: | --- |
| EN m81374 | 247,327 | `021c29fa9a6ab3d5b06d2ef143a82d2ac818ed25fe6fd44ebf5d7a6be07a123a` |
| ID m81374 | 247,303 | `d89a74aef766afca6a4ac7e1ae720f120d22cc771c11dd7e025c55bca1fabb8e` |
| EN m81370 | 192,242 | `12157ddd00dae98c6c2cbddec512297110ec945d2a1e0bed207e1801ffab8ad4` |
| ID m81370 | 191,468 | `86758280beefdbe4041ced71dd062697766d0609bc340b54eb07381a90d9edcd` |

The suite rehashes these exact member bytes and the selected media bytes. It validates archive-hash metadata against the known pins, but does **not** rehash entire large archives on every run. ZIP reads check member CRC as well. Reading a small complete module member in memory is not extraction of a corpus.

The m81370 read was confined to title/metadata/backreference verification, not a claim to review that entire teaching module. Its pinned titles are “Slope of a Line” / “Gradien Garis,” with UUID `f54f6801-0920-459c-af2e-72f85ddda846`.

## 2. Mathematical review of all 36 questions

Local numbers below are MR017 numbers, not invented source IDs. “Absent” means the source supplies no solution; the XML keeps an explicitly authored omission notice. Calculations in the “checked result” column for absent answers are **reviewer calculations only**, not translated source answers or additions to the reader.

| Local question | Actual question data / task | Independently checked result | Source answer status |
| ---: | --- | --- | --- |
| 1 | Graph 222 | Slope −3 from (0,0), (1,−3) | Absent |
| 2 | Graph 223 | Slope 1 from (−4,0), (0,4) | Supplied 1 |
| 3 | Graph 224 | Slope 1/3 from (−4,−4), (2,−2) | Absent |
| 4 | Graph 225 | Slope −1/2 from (1,4), (5,2) | Supplied −1/2 |
| 5 | y = 2 | Horizontal; slope 0 | Absent |
| 6 | x = 5 | Vertical; slope undefined, not infinity | Supplied undefined |
| 7 | x = −3 | Vertical; slope undefined | Absent |
| 8 | y = −1 | Horizontal; slope 0 | Supplied 0 |
| 9 | (−1,−1), (0,5) | (5+1)/(0+1) = 6 | Absent |
| 10 | (3,5), (4,−1) | (−1−5)/(4−3) = −6 | Supplied −6 |
| 11 | (−5,−2), (3,2) | 4/8 = 1/2 | Absent |
| 12 | (2,1), (4,6) | 5/2 | Supplied 5/2 |
| 13 | Through (2,−2), slope 5/2 | y = (5/2)x − 7 | Absent |
| 14 | Through (−3,4), slope −1/3 | y = −(1/3)x + 3; graph 368 agrees | Supplied graph |
| 15 | x-intercept value −4, slope 3 | Point (−4,0); y = 3x + 12 | Absent |
| 16 | y-intercept value 1, slope −3/4 | Point (0,1); y = −(3/4)x + 1; graph 370 agrees | Supplied graph |
| 17 | y = −4x + 9 | Slope −4; intercept point (0,9) | Absent |
| 18 | y = (5/3)x − 6 | Slope 5/3; intercept point (0,−6) | Supplied both |
| 19 | 5x + y = 10 | Slope −5; intercept point (0,10) | Absent |
| 20 | 4x − 5y = 8 | Slope 4/5; intercept point (0,−8/5) | Supplied both |
| 21 | y = 2x + 3 | Slope 2; intercept point (0,3) | Absent |
| 22 | y = −x − 1 | Slope −1; graph 372 through (0,−1), (1,−2) | Supplied graph |
| 23 | y = −(2/5)x + 3 | Slope −2/5; intercept point (0,3) | Absent |
| 24 | 4x − 3y = 12 | y = (4/3)x − 4; graph 374 through (0,−4), (3,0) | Supplied graph |
| 25 | x = 5; choose a convenient method | Vertical line x = 5 | Absent |
| 26 | y = −3; choose a convenient method | Horizontal line y = −3 | Supplied horizontal-line method |
| 27 | 2x + y = 5; choose a convenient method | y = −2x + 5; more than one valid method | Absent |
| 28 | x − y = 2; choose a convenient method | Intercepts (2,0), (0,−2) give y = x − 2 | Supplied intercept method |
| 29 | y = (2/2)x + 2; choose a convenient method | Exact slope 1, intercept (0,2); literal 2/2 preserved | Absent |
| 30 | y = (3/4)x − 1; choose a convenient method | Point plotting is valid, e.g. (0,−1), (4,2) | Supplied plotting-points method |
| 31 | C = 6.5m + 42; weekly meal cost; four parts | C(0)=42, C(14)=133; 6.5 dollars/additional meal; (0,42) baseline and line equation | Absent, all four prompts retained |
| 32 | P = 35s − 250; weekly piano profit; four parts | P(0)=−250, P(20)=450; 35 dollars/additional lesson; loss 250 at zero lessons; graph 376 | Supplied four-part mixed answer |
| 33 | 4x − 3y = −1; y = (4/3)x − 3 | Slopes 4/3, 4/3; intercept values 1/3, −3: distinct parallel lines | Absent |
| 34 | y = 5x − 1; 10x + 2y = 0 | Slopes 5, −5; product −25: neither parallel nor perpendicular | Supplied neither |
| 35 | 3x − 2y = 5; 2x + 3y = 6 | Slopes 3/2, −2/3; product −1: perpendicular | Absent |
| 36 | 2x − y = 8; x − 2y = 4 | Slopes 2, 1/2; product 1: neither | Supplied neither |

All 18 supplied solutions occur at even local question numbers, and all 18 missing solutions at odd numbers. Supplied answers comprise four graph-only answers (14,16,22,24), one mixed text/graph answer (32), and 13 text-only answers. No original exercise or answer to a source omission is added.

The suite separately parses all 41 MathML items in **each** locale: 35 problem items and six solution items. They are compared with target mathematics using exact rational polynomial, scalar and ordered-pair semantics. For example, source q10 encodes the first tuple unusually within a single `mn`, but its literal coordinate values remain (3,5). The explicit source q32 currency token `−$250` is compared to target −250 with the adjacent visible dollar label, not silently discarded.

All 50 unique target `data-check` strings equal the frozen config. This is an exact regression check, **not** the independent mathematical argument. The 41 source-derived MathML values plus nine separately checked spans account for every target key: two authored introductory formulas and seven spans for source plain-text values or answers. The count does not imply 50 source equations.

### Interpretation and algebra decisions

- **Slope and intercept:** An affine equation is interpreted as A·x + B·y = C with exact fractions. When B is nonzero, slope is −A/B and the y-intercept is (0,C/B). Vertical lines are kept undefined. The introductory y = mx + b and (0,b) are correctly distinct: b is the scalar intercept value, not the point itself. Q15 and q16 explicitly identify the scalar x-/y-intercept values.
- **Unsimplified source:** Both actual source trees retain numerator 2 and denominator 2 at q29. The target keeps `y = (2/2)x + 2` and warns against reading 22 or 2. Computing its slope as 1 in a review does not authorize altering that source display.
- **Convenient methods:** Q26,28,30 preserve their particular source method answers. The target visibly permits other correct methods; the test does not mistake a pedagogical preference for a unique mathematical theorem.
- **Two-point slopes:** Fraction arithmetic uses the same coordinate order in both numerator and denominator; reversing both endpoints leaves the answer unchanged. Repeated identical points are rejected by the helper rather than called a vertical line.
- **Parallel/perpendicular:** Coefficient determinants and dot products establish the four line-pair classifications exactly. Coincident lines have a separate category, and the negative controls include vertical/horizontal perpendicular lines. A finite-slope product criterion is not applied to an undefined vertical slope.
- **Meal cost:** In q31, m denotes meals, not slope. The target makes this change of symbol meaning explicit. 6.5 is parsed as 13/2, not binary floating-point approximation.
- **Piano profit:** s counts student lessons, not distinct students. All four source subparts remain visible. The increment identities C(m+1)−C(m)=13/2 and P(s+1)−P(s)=35 are checked by polynomial coefficient cancellation, not inferred as universal facts from a finite sample grid.
- **Physical count versus algebraic graph:** The authored notes distinguish nonnegative integer meal/lesson counts from the continuous formula line. Negative or fractional lesson counts are not treated as physically permitted; the visible plot window is not the full permitted count domain. Tests also exclude −1, 1/2 and 50/7 as counts and include larger counts outside the displayed window. The underlying condition is exact nonnegative integrality, not enumeration as a proof.

## 3. All 18 original rasters personally inspected

Each of the nine EN images **and** nine ID images was individually opened with the permitted filesystem image viewer at original detail before finalizing. There was no browser, rendering of target HTML, image generation, redrawing or image modification. Each reviewed copy was byte-compared to its named ZIP member, and every EN/ID pair proved byte-identical. This does not substitute an older agent's visual claim for this review.

Files have the form `CNX_IntAlg_Figure_03_06_<number>_img_new.jpg`. Review copies are `downloads/mr-Deva-IN/source-image-qa/MR-BRIDGE-017/<en-or-id>-<filename>`; canonical assets are under `mr-Deva-IN/assets/MR-BRIDGE-017/`. Nine canonical EN assets total 707,085 bytes; 18 original review copies total 1,414,170 bytes.

| Figure | Source role | Bytes in each locale | SHA-256 of each separately viewed EN and ID original |
| --- | --- | ---: | --- |
| 222 | q1 problem | 90,732 | `2df8fb519799cfdabec17cbbd4cd6da2cff9f30aa8d04772760d37e3a6b0780f` |
| 223 | q2 problem | 91,810 | `74a804ccfcf03720c6785db1af2d3cc6bf540a937839ec195c32878d8334081a` |
| 224 | q3 problem | 92,004 | `d8f927e1f4324f8281f0b68453d136e2ebccaa17eb4b6439f86c0d2be37fcce4` |
| 225 | q4 problem | 93,091 | `be8232235bb72764d434e62fdfdbbc26b918f78f7fdf2a8565125caa8afe36b6` |
| 368 | q14 solution | 61,222 | `c47373c3a1e7e840cef847920b3712e26839b95023d8596ace858f74b7779fd1` |
| 370 | q16 solution | 64,824 | `9777a5ef85b6ca1b23c207713aca7002161e239f9ecd8386a94cd090118cadba` |
| 372 | q22 solution | 76,137 | `c2bd6537d15b04a006a3fb54b964ecec1c1786249a9259890ffb4021da77a5fa` |
| 374 | q24 solution | 77,308 | `ba1128cfbdadf82ecb11f8c9117deae187ce484b4cf3fd1422df8d3ed3bc6062` |
| 376 | q32 solution | 59,957 | `23cc633bcd3f8e86c6fb1d66c7ad7057bf56e6da40ce81c1aa6d5bfc74a1a985` |

Concrete pixel observations:

- Figures 222–225 visibly have both axes extending through labeled values −8 to 8. Both EN and ID source alts incorrectly say −6 to 6 twice. The four target alts use −8 to 8, and a shared visible original note names the discrepancy. The plotted point pairs and directions in the mathematics table above agree with the pixels. All four lines have continuation arrows.
- Figures 368 and 370 use the −8 to 8 windows. Their downward lines respectively pass through (−3,4)/(0,3) and (0,1)/(4,−2).
- Figures 372 and 374 use −10 to 10 windows. Their lines respectively descend through (0,−1)/(1,−2) and ascend through (0,−4)/(3,0). Arrow descriptions remain present.
- Figure 376 actually labels the horizontal axis **h**, not s, and the vertical axis **P**. Its horizontal grid runs from −4 to 28, with displayed numeric labels including 4,12,20,28; vertical values run from −250 to 450 with 50-unit steps. The upward line starts at (0,−250), passes through (20,450), and has an upper continuation arrow. Horizontal and vertical scales are unequal: the slope is the numerical 700/20 = 35, not the apparent screen angle.
- Both original 376 source alts call the axes generic x/y. The target's original note preserves the raster and explains that its horizontal h is read as the question's lesson variable s. Its Marathi alt gives the actual h/P labels. This is an explicit notation reconciliation, not a silently edited source graph.

The regression suite binds these manual observations to hashes and checks the described point pairs, directions, bounds, arrows, source media roles and correction text. It does not perform OCR/computer vision and cannot re-establish visual correctness merely by passing.

## 4. Actual Marathi-canon consultation and effect

Relevant readable canon was consulted during source/mathematical review and again while checking the final assertions/report, not merely downloaded or remembered. No shared canon entry or terminology ledger was edited by this reviewer.

1. **C12, Balbharati Class 8, physical PDF p85 / printed p75:** Read the existing OCR's opening equation paragraphs and four equal-operation rules. They define a solution by making the sides equal and state division by an equal **nonzero** number. This informed substitution, exact equation rearrangement, and the zero/undefined distinction. The available OCR formulas later on the page were not used as formula authority; no fresh PDF-page visual inspection is claimed. [Official Balbharati source](https://books.ebalbharati.in/pdfs/801020004.pdf). Read witness: `downloads/mr-Deva-IN/canon/ocr/balbharati8-85.txt`, 2,474 bytes, SHA-256 `f9bf9c42edb3e126573bc14f4671aa5c062920ee145c50590fdac6733af52a9b`.

2. **C18, आलेख:** Read the जात्याक्ष paragraph on perpendicular horizontal/vertical reference axes, origin, convenient axis marking and ordered सहनिर्देशक placement, plus the equation-graph paragraph defining points by satisfaction of the equation. The latter distinguishes equation curves from simply joining sampled observations and explicitly identifies the continuity assumption. Effects: correct coordinate order; numerical graph checks; distinguish the continuous formula from discrete lesson counts. Unequal scales in figure 376 were observed in the raster; this report does not invent a freshly read sentence saying both axes must or must not share a scale. [Marathi Vishwakosh, आलेख](https://vishwakosh.marathi.gov.in/24316/).

3. **Narrow slope reference, भूमिती, 28194:** Read “रेषेचा उतार व दोन रेषांमधील कोन” and the “रेषा” passages, including slope, equal slopes for parallel lines, the finite-slope perpendicular product, constant-coordinate lines, and the point-slope / slope-intercept forms. The short labels “बिंदु-उतार प्रकार” and “उतार- खंड प्रकार” were actually visible. Effects: support उतार, समांतर and लंब; check y−y₁=m(x−x₁), y=mx+b, scalar intercept versus point, and vertical exceptions. Full target classroom headings and the h-to-s explanation remain authored wording, not quotations attested as whole phrases. [Marathi Vishwakosh, भूमिती](https://vishwakosh.marathi.gov.in/28194/).

Access record: the first narrow slope search did not return the needed page and direct opening of 28194 returned 502. A subsequent official-domain search supplied readable 28194 paragraphs; an overlapping 28572 entry also appeared, but the 28194 passage was separately located before attribution. A later optional C18 unequal-scale query failed at the connection layer; it is not recorded as a successful read. After interruption, the C12 OCR was reread and the actual previously retrieved C18/28194 paragraphs were re-opened from the retained tool output while finalizing. No unsupported formula elsewhere in a long or garbled encyclopedia result was adopted. Root alone decides global canon promotion.

## 5. Identity, answer links, provenance and offline limits

The 18 original problem/solution pairs retain their original IDs. Each supplied problem has exactly one local answer link and its solution has exactly one return link to that problem. The 18 omitted answers have no fabricated solution elements and exactly one `source-answer-missing` original notice each. The generic builder's zero authored `question_ids` is not a count of these source pairs.

The target contains 43 local anchors: 36 source-answer directions plus seven navigation links. All local destinations exist. The three HTTPS links are the m81370 teaching-title link, the OpenStax chapter-introduction credit, and the existing CC BY-NC-SA 4.0 notice. The source title points to `document="m81370"` without a target ID. The target preserves that source-document attribute and maps it to the appropriate English teaching page, visibly noting internet access and that the full teaching section is not translated here. Pinned metadata supports this mapping; live endpoint availability was not tested. The review did not open external reader pages.

The existing CC BY-NC-SA 4.0 and component-notice wording remains present. This was a scoped preservation check, not a new general license audit. All nine target images are canonical local asset references with matching JPEG hashes, provenance witnesses and original media identities. There are no script, iframe, SVG, audio or video elements in this reviewed XML. Source/math review does not certify every possible renderer behavior or browser security property.

For repeatable inventory checks, sorted UTF-8 rows joined with LF and a final LF have these hashes:

| Inventory row form | Rows | SHA-256 |
| --- | ---: | --- |
| `target_id\|locale\|fragment_sha256` | 100 | `bc50b4c95fef0c69bc8f135d1827402c559d6bdde8356333c0511d9cf4d6aae6` |
| `locale\|filename\|sha256\|bytes` | 18 | `d8c819b6640d82a3bf1c360b8e6a55645f7453f556dea7b277697da19ff698a1` |
| `math_key\|text` | 50 | `2d811adf166d90fadd0bd0bdbcd30f6dea6ffca645825aca703a765208617c33` |
| `witness_path\|sha256` | 118 | `e39cd30ffa0ca1c8a7312de470d1fa6ceb811ce3f0778d58f996646ef674a380` |

## 6. Reproduction and handoff

Run from the workspace:

```powershell
python -B mr-Deva-IN/tools/test_unit17_math.py
```

The suite has 28 tests and uses only the Python standard library. It reads the real frozen files and bounded selected ZIP members; it makes no output files, downloads, corpus copies or extractions. All 28 tests passed again after the connection/compaction interruption against the unchanged frozen inputs, with zero skips. Missing inputs fail; no synthetic fallback makes an incomplete checkout appear reviewed.

Test categories: exact input/member pins; complete contiguous scope; all 100 fragments; 167 original IDs and ancestry; headings/instructions; all 50 strings and 41 source MathML items per locale; every question prompt; nine graphs/eighteen point observations; slopes/intercepts; three method answers; both four-part applications; exact affine rates; discrete count interpretation; four pair classifications; 18 answer/return pairs and omissions; nine assets and eighteen original-image pins; source-alt corrections; title backreference; all 118 witnesses; parser negative controls.

The arithmetic helper accepts only whitelisted AST arithmetic and exact Fraction coefficients; it never calls `eval`. Variable division, zero denominators, unsupported powers/functions, malformed equations and unsupported MathML are rejected. General algebraic proofs are not claimed: the coefficient arguments are appropriate to these exact affine problems. Exact file and string pins are change alarms; future intentional edits require renewed source/math review, not automatic pin replacement.

[Test file](<[local-home]/.codex/worktrees/9286/LAN ALLOC/mr-Deva-IN/tools/test_unit17_math.py>): 46,328 bytes, SHA-256 `70877405d49a9a55ca3ce223fdd2c1b34bf79e28b2037488f43dee71bd85e65d`.

No XML/config correction is requested. Root may integrate this independent result and independently rerun the suite. The immutable target's cautious footer is not rewritten by this review. HTML/PDF reader acceptance remains separate; no Browser, alternate browser, target HTML, PDF generation, staging or commit was performed. No human/native-speaker approval is claimed.

The exact following source topic is `A20:m81374#fs-id1167836526512`, “Find the Equation of a Line.” Remaining Chapter Review topics and Practice Test are outside MR017. This is one complete review-topic checkpoint within the continuing five-book assignment, not an endpoint for the overall work.

