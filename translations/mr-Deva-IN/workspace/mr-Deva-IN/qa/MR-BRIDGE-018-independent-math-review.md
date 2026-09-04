# MR-BRIDGE-018 independent source and mathematics review

Date: 2026-08-31. Reviewer: `/root/second_unit_builder`; MR018 was drafted by the separate `/root/freeze_regressions` agent. This is an independent source/mathematics review, not the writer's self-check.

**Result: PASS for this bounded scope. All 27 tests pass, with zero failures or skips. No new source or mathematical defect was found; no XML/config correction is requested.** The source-alt errors and vertical-line instruction exception were independently confirmed, not accepted merely because drafting notes mentioned them.

Owned files are only `tools/test_unit18_math.py` and this report. No translation, config, source lock, canonical image, shared ledger or rendering file was edited. This result is not HTML/PDF reader acceptance, human/native-speaker approval, a complete-module decision or completion of the five-book assignment.

## 1. Actual scope and immutable inputs

Read every Marathi line of the complete XML and the complete config. Read both actual EN and ID source topics, including every heading, instruction, question, supplied answer, MathML expression and source image description. Then read the writer's notes as a cross-check, not as source authority.

The reviewed topic is `A20:m81374#fs-id1167836526512`, “Find the Equation of a Line” / “Menentukan Persamaan Garis.” It is the third Chapter Review topic, inside `fs-id1167836524742`. Both pinned modules place it immediately after `fs-id1167829740806` and before `fs-id1167836570304`. Its 35 direct non-title selections run from `fs-id1167836613250` through `fs-id1167836686948`.

Actual counts:

- 11 heading/instruction paragraphs: five bold headings and six exercise instructions.
- 24 original questions; 12 supplied answers at even local numbers and 12 explicit omissions at odd numbers.
- 107 original IDs within selected blocks, plus the topic and Chapter Review wrappers: 109 original IDs. Target article and credits make 111 unique target IDs.
- 54 source MathML items in each locale: 42 in questions and 12 in supplied solutions.
- 64 target mathematics keys: those 54 source items, the source's plain-text zero in q3, and nine visibly original reminder/qualification formulas. These are not 64 source equations.
- Four canonical EN problem images, eight separately inspected EN/ID originals; no source tables, formal definition blocks, worked-example blocks or resource notes.
- 70 frozen fragments totaling 41,374 bytes; 83 unique witness files.

| Input below `mr-Deva-IN/` | Bytes | SHA-256 |
| --- | ---: | --- |
| `translations/MR-BRIDGE-018.xml` | 32,346 | `f7b37554ff6973e523952578d742fda63eaa75962cd7a32369f266d2de2ec60a` |
| `units/MR-BRIDGE-018.json` | 4,519 | `b374350df5b6fd3db857ee8726a65ccbcdb7888fe32aabaa111eaf510482cd4c` |
| `provenance/MR-BRIDGE-018.lock.json` | 97,307 | `d7d13b2352c6aa829db9c57e38059b730cff8faf0f9af21ae214ad8238fa6aad` |

All source locators are compared in order against the actual complete topic, the frozen lock and the target. The full original-ID preorder and nearest-original-ID ancestry are checked in both locales and the target. All 70 frozen fragments are read and hashed; their full parsed element shape, text, attributes, descendants and child tails are compared with the actual selected source elements. Fragment-root serialization tail whitespace is excluded.

### Pinned source members

Existing ignored archives were read in memory, with no download, extraction or corpus copying. EN uses `A20-canonical.zip`, prefix `osbooks-prealgebra-bundle-38cae454e644abf9f0a623e876994553881597c9`. ID uses `A20-v0.3.0-source.zip`, prefix `source`. Both archives reside under `downloads/mr-Deva-IN/releases/`.

Recorded archive hashes:

- EN: `effdf2dbb6dfd9cab771b568c6575d8074be4a1f9565f1fedbd54f621e138917`.
- ID: `a9c53c328be944e12b707d5cb16e289755eff0c603d1652bfca13dd572e780d7`.

Selected module members are `<prefix>/modules/<module>/index.cnxml`:

| Locale/module | Bytes | SHA-256 |
| --- | ---: | --- |
| EN m81374 | 247,327 | `021c29fa9a6ab3d5b06d2ef143a82d2ac818ed25fe6fd44ebf5d7a6be07a123a` |
| ID m81374 | 247,303 | `d89a74aef766afca6a4ac7e1ae720f120d22cc771c11dd7e025c55bca1fabb8e` |
| EN m81371 | 123,694 | `a8d9b3cdd70107f7ee603d104ac9cdd4168b57acc9b19e2e8116fea3dccc2ed2` |
| ID m81371 | 127,034 | `c306d979513478a707e5740b20eb0ac4de39bac8e3b18402a79904ae9f4f6d1a` |

The tests hash these member bytes and the eight named original image members; archive-hash metadata is checked against the known pins. They do not rehash entire large archives each time. ZIP-member reads also check CRC. Only m81371 title/metadata/learning-objective text was personally read for the title backreference; this does not claim review of that entire teaching section.

The first EN source-output attempt stopped at the console's legacy encoding when printing a minus sign. It was rerun from the beginning with explicit UTF-8, and the whole EN topic plus the whole ID topic was actually read. A failed or truncated output was not counted as a complete source read.

## 2. Every question and supplied equation checked

Local numbers below are explicitly local MR018 question numbers. For odd questions the equations in this report are **reviewer calculations only**; the XML preserves the source's missing-answer state and does not add them as reader answers.

| Local q | Actual constraint | Independently derived line | Source answer |
| ---: | --- | --- | --- |
| 1 | Slope 1/3; y-intercept (0,−6) | y = (1/3)x − 6 | Absent |
| 2 | Slope −5; y-intercept (0,−3) | y = −5x − 3 | Supplied, matches |
| 3 | Slope 0; y-intercept (0,4) | y = 4 | Absent |
| 4 | Slope −2; y-intercept (0,0) | y = −2x | Supplied, matches |
| 5 | Figure 226: intercept (0,1), highlighted (1,3) | y = 2x + 1 | Absent |
| 6 | Figure 227: intercept (0,5), highlighted (1,2) | y = −3x + 5 | Supplied, matches |
| 7 | Figure 228: intercept (0,−2), highlighted (4,1) | y = (3/4)x − 2 | Absent |
| 8 | Figure 229: horizontal, through (0,−4), highlighted (4,−4) | y = −4 | Supplied, matches |
| 9 | Slope −1/4, through (−8,3) | y = −(1/4)x + 1 | Absent |
| 10 | Slope 3/5, through (10,6) | y = (3/5)x | Supplied, matches |
| 11 | Horizontal, through (−2,7) | y = 7 | Absent |
| 12 | Slope −2, through (−1,−3) | y = −2x − 5 | Supplied, matches |
| 13 | Through (2,10) and (−2,−2) | y = 3x + 4 | Absent |
| 14 | Through (7,1) and (5,0) | y = (1/2)x − 5/2 | Supplied, matches |
| 15 | Through (3,8) and (3,−4) | x = 3, vertical | Absent |
| 16 | Through (5,2) and (−1,2) | y = 2, horizontal | Supplied, matches |
| 17 | Parallel to y = −3x + 6, through (1,−5) | y = −3x − 2 | Absent |
| 18 | Parallel to 2x + 5y = −10, through (10,4) | y = −(2/5)x + 8 | Supplied, matches |
| 19 | Parallel to x = 4, through (−2,−1) | x = −2, vertical | Absent |
| 20 | Parallel to y = −5, through (−4,3) | y = 3, horizontal | Supplied, matches |
| 21 | Perpendicular to y = −(4/5)x + 2, through (8,9) | y = (5/4)x − 1 | Absent |
| 22 | Perpendicular to 2x − 3y = 9, through (−4,0) | y = −(3/2)x − 6 | Supplied, matches |
| 23 | Perpendicular to y = 3, through (−1,−3) | x = −1, vertical | Absent |
| 24 | Perpendicular to x = −5, through (2,1) | y = 1, horizontal | Supplied, matches |

Every supplied answer is a single original MathML equation, present in both EN and ID. Each of the twelve is independently compared with the line constructed from its actual question constraints, not merely compared with the target config. All signed fractions, coordinates, horizontal/vertical constraints and supplied equations agree.

Source MathML is interpreted through a small whitelist: mathematical rows, tokens and numeric fractions. Trailing comma punctuation in the source's “line ..., point ...” and “m=..., point ...” layouts is handled explicitly; coordinate commas remain structural. The q3 plain-text 0 and the four separate inline y symbols are checked rather than ignored because they are not stand-alone equations.

### Exact reasoning, rather than a finite-grid claim

The helpers use Fraction coefficients and a whitelisted arithmetic AST; `eval` is never called. An affine line is represented as A·x + B·y = C and normalized only up to a nonzero common scalar.

- Given a finite slope m and point (x₀,y₀), the constructed normal is (−m,1) and C=y₀−mx₀. This verifies both the slope and passage through the point.
- Given two distinct points, the normal is (y₂−y₁,x₁−x₂). This covers equal-x and equal-y cases without illegal division, and reversing the point order leaves the normalized line unchanged.
- A parallel line retains the original normal and chooses C from the given point. All four requested lines here are distinct from their original lines, not coincident.
- A perpendicular line uses the rotated normal (−B,A), again choosing C from the given point. Exact dot products check perpendicularity. This handles horizontal/vertical cases directly rather than assigning an infinite slope.
- Finite slopes for q21 and q22 give products −1. Q23 and q24 correctly pair zero slope with undefined slope; they do not enter that finite arithmetic rule.
- Negative controls reject repeated identical points, zero normal vectors, zero denominators, variable denominators in the numeric affine parser, unsupported Python/math syntax and duplicate JSON keys. They also reject altered point signs, slopes or plotted values.

The 64 exact target/config strings and file hashes are regression alarms, not independent mathematical proofs. They sit alongside these constraint and coefficient checks.

## 3. Authored reminders and source-instruction limitation

Nine target mathematics spans lie within explicit `data-kind="original"` material: slope–intercept form, intercept point, generic given point, point–slope form, the b substitution, two-point nonzero condition, two-point slope formula, perpendicular product, and generic vertical-line form. The source's plain zero is the tenth key outside the 54 original MathML items; it is not an authored formula.

The generic reminder formulas were checked symbolically:

- Replacing b by y₁−mx₁ in y−mx−b yields exactly y−y₁−m(x−x₁), by comparing all polynomial coefficients.
- Setting x=x₁ and y=y₁ in the point–slope expression cancels identically.
- For the displayed two-point quotient, numerator and denominator are checked separately as y₂−y₁ and x₂−x₁. Under the separately displayed x₂≠x₁ condition, clearing that denominator agrees with point–slope form at the second point. The parser does not silently pretend division by a symbolic zero is safe.
- The intercept scalar b remains distinct from the point (0,b); the ordered generic point (x₁,y₁) is not interchanged.
- Marathi prose explicitly requires a nonzero divisor when applying equal operations to both sides and distinguishes undefined vertical slopes from zero horizontal slopes.

Both source locales repeatedly ask for slope–intercept form, including instructions governing vertical-result q15,19,23. The target preserves those instructions and adds a separately marked qualification after `fs-id1167833086732`: vertical lines instead have generic x=c form. It explicitly names these three questions, explains constant x, and says the note is not a source answer. Their actual values x=3,−2,−1 are not inserted as missing reader solutions. No correction to this treatment is needed.

The short Marathi point–slope and slope–intercept labels were encountered in the actual canon passage discussed below. That does not promote every complete classroom phrase or authored explanatory sentence into a globally attested term.

## 4. Original-pixel review: all eight files

Personally opened EN226, EN227, EN228, EN229 and then ID226, ID227, ID228, ID229 at original detail with the permitted filesystem image viewer. Both versions of every image were actually viewed, even though byte checks subsequently confirmed each pair is identical.

The existing files are `downloads/mr-Deva-IN/source-image-qa/MR-BRIDGE-018/<locale>-CNX_IntAlg_Figure_03_06_<number>_img_new.jpg`. Original members are `<prefix>/media/CNX_IntAlg_Figure_03_06_<number>_img_new.jpg`. Four canonical EN copies under `mr-Deva-IN/assets/MR-BRIDGE-018/` total 321,589 bytes; all eight review copies total 643,178 bytes. No source or review image was created, replaced or modified by this reviewer.

| Figure / question | Bytes in each locale | SHA-256 of each individually viewed EN/ID original | Actual pixels |
| --- | ---: | --- | --- |
| 226 / q5 | 80,495 | `b65094690ad0890fac3f02bee25032a93ed199cedd500293eba1f84a8bec582f` | Ascending line; y-intercept (0,1); highlighted (1,3); both continuation arrows |
| 227 / q6 | 80,118 | `46b05b78acd8e919bd6b3b46cbd2e76beba0d6491e3cc34ccd35c01b33c3d5f4` | Descending line; y-intercept (0,5); highlighted (1,2); both continuation arrows |
| 228 / q7 | 82,690 | `bdac4223fddce4df86cbea4b02180908ef41be39cf8c3d5f3a64bd476c819ed0` | Ascending line; y-intercept (0,−2); highlighted (4,1); both continuation arrows |
| 229 / q8 | 78,286 | `3ba112acfc465daef1b41e2d37fad0b8909e472522f6582ef1cf64cf4a4a41b6` | Horizontal line y=−4; highlighted (4,−4); both continuation arrows |

All eight actual rasters label x horizontally and y vertically, and both displayed axes run from −6 to 6. Both source alts instead say −10 to 10. The Marathi alts use the visible −6 to 6 frame, and an explicit original note preserves the discrepancy. No raster redraw, crop or relabeling is made.

The source alts' numerical points all satisfy the appropriate line. In particular, figure 228's source-alt point (8,4) satisfies y=(3/4)x−2 but lies outside the x≤6 frame. The target describes the visible intercept and highlighted point, and the separate note expressly identifies the out-of-frame point. Figure 229's alt-source points (0,−4),(1,−4),(2,−4) are correct points on the line, while the target appropriately describes the actual highlighted point (4,−4).

The automated tests bind these manual observations to the original-image and asset hashes, verify all described points and correction wording, and preserve each original media ID under its original problem. They are not OCR or computer vision; passing a byte-bound regression does not itself recreate a fresh visual judgment.

## 5. Actual Marathi-canon reading and effects

Relevant canon was actually read during source/mathematical review and revisited while checking the completed assertions. These are this reviewer's reads, not the writer's reported consultations. No shared canon file or terminology entry was modified.

**C12, Balbharati Class 8, physical PDF p85 / printed p75:** Read the existing OCR's opening solution/equation prose and equal-operation rules, including division by the same nonzero number. Reread those actual lines while reviewing the symbolic assertions. Effect: check substitution by equality, preserve “शून्येतर,” and handle vertical exceptions without zero division. Garbled OCR formulas later on the page were not used as formula authority. No new PDF-page visual inspection is claimed. [Official Balbharati source](https://books.ebalbharati.in/pdfs/801020004.pdf). Read witness: `downloads/mr-Deva-IN/canon/ocr/balbharati8-85.txt`, 2,474 bytes, SHA-256 `f9bf9c42edb3e126573bc14f4671aa5c062920ee145c50590fdac6733af52a9b`.

**C18, आलेख:** A fresh official-domain search returned readable जात्याक्ष and equation-graph passages. Read the horizontal/vertical reference-axis and origin discussion, choosing suitable axis marks, and finding corresponding values from an equation on its stated interval. Effect: verify actual x/y orientation and distinguish the drawn frame from other points satisfying the same equation; do not equate an out-of-frame point with a wrong equation. The long result's unrelated later applications were not used as mathematical authority for MR018. [Marathi Vishwakosh, आलेख](https://vishwakosh.marathi.gov.in/24316/).

**C22, भूमिती, narrow registered slope locator:** Fresh official-domain retrieval supplied the actual “रेषेचा उतार व दोन रेषांमधील कोन” paragraph and neighboring line-equation prose. Read finite slopes, parallel/perpendicular criteria, constant-coordinate lines, point–slope and slope–intercept equations. The readable labels “बिंदु-उतार प्रकार” and “उतार- खंड प्रकार” were personally read and then reread from that retained fresh output during assertion revision. Effect: check the displayed forms, parameter/intercept distinctions, and finite-slope limits; treat vertical/horizontal lines separately. The globally registered T043 support remains narrowly उतार. Full target headings, en-dash styling, translations of explanations and other compound phrases were not globally promoted by this review. [Marathi Vishwakosh, भूमिती](https://vishwakosh.marathi.gov.in/28194/).

Access limits: the targeted C18/C22 searches succeeded in this MR018 review. No fresh direct-open success, new local HTML witness, PDF rendering or complete-article review is claimed. Earlier tasks' failed accesses are not recast as failures or successful reads in this task. Source rendering's initial console-encoding failure was handled by a complete UTF-8 reread, as recorded above.

## 6. Links, provenance and answer accounting

All twelve source solution IDs and their original paragraph IDs remain intact. Each supplied problem has exactly one answer anchor; each solution has exactly one return anchor to that original problem. The twelve missing-source-answer cases have no fabricated solution element and exactly one original omission notice each.

There are 30 local anchors: 24 directions for twelve source-answer pairs, plus six navigation links. All destinations resolve. The config's empty authored `question_ids` list does not mean there are no source question/answer pairs.

Three HTTPS links remain: the title backreference, OpenStax chapter-introduction credit and existing CC BY-NC-SA 4.0 notice. The original title's sole link is `document="m81371"`, with no target ID. The target retains `data-source-document="m81371"` and the matching English 3.3 section route. The pinned m81371 titles match the topic, and both metadata records use UUID `b7d62225-c09f-478e-8c1d-df46042de0b0`. This verifies the source-document/title mapping, not current live endpoint availability. The reviewer did not open that reader URL.

The target visibly explains that the reference requires internet and that the whole referenced teaching section is not translated here. The CC BY-NC-SA 4.0/component wording remains present; this is preservation, not a new general license audit. All four asset references use pinned local JPEGs and matching witnesses. No scripts, iframe, SVG, audio or video elements occur in this frozen XML. No claim about every possible renderer behavior follows from that check.

The suite verifies every one of the 83 actual witness files. Sorted UTF-8 rows joined by LF with a final LF give these inventory hashes:

| Row form | Rows | SHA-256 |
| --- | ---: | --- |
| `target_id\|locale\|fragment_sha256` | 70 | `3dbe61b168438ae88610e34467f2d81107c106a4c62553d5724a947e85f919c5` |
| `math_key\|text` | 64 | `c56c60188f5283e02f3280c6869db3c26c498babd681b6249258421f328edf10` |
| `locale\|filename\|sha256\|bytes` | 8 | `d078860954e9592ebbaaefd4b2481c6875af808c8be26c12295dcc32b363753d` |
| `witness_path\|sha256` | 83 | `9087661c9d6149524cd6f796f18de167df1aa4bd3c9d20d5b6cdd276cadb717c` |

## 7. Reproduction, release and limits

Run from the workspace:

```powershell
python -B mr-Deva-IN/tools/test_unit18_math.py
```

27/27 tests pass, with zero skips. The suite is self-contained Python standard library, reads real frozen inputs and bounded selected ZIP members, and makes no output files. Missing inputs fail; no synthetic fixtures replace absent real sources. Test categories cover pins, full scope, all fragments, identity preorder/ancestry, all headings/instructions, all target/source mathematics, every question constraint and supplied equation, authored coefficient identities, horizontal/vertical/parallel/perpendicular cases, actual-image pins and descriptions, source-answer links, title mapping, witnesses and parser negative controls.

[Test file](<[local-home]/.codex/worktrees/9286/LAN ALLOC/mr-Deva-IN/tools/test_unit18_math.py>): 45,091 bytes, SHA-256 `58ebc0acde896cee8e5c12253cfd9083d30be6e231c2ab18d11eb968c5022592`.

No new defect or requested source correction remains from this review. Root may independently rerun and integrate the result. Intentional future changes require renewed review and updated pins, not automatic replacement of expected hashes.

There was no browser or alternate-browser action, target HTML access, PDF generation, staging, commit, push, source cleanup or shared-file edit. The source-image inspection is not target-reader visual acceptance. No human/native Marathi, accessibility or complete-module approval is claimed.

The exact next source topic is `A20:m81374#fs-id1167836570304`, “Graph Linear Inequalities in Two Variables,” followed by two more Chapter Review topics and the Practice Test. MR018 covers its own complete topic only; the full five-book production and QA workflow remains active.

