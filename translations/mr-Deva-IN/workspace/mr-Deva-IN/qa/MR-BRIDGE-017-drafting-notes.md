# MR-BRIDGE-017 — complete slope-review topic: drafting record

2026-08-31. Stable drafting-author handoff, not an independent review or accepted reader. Only this note, the unit XML and its JSON config were authored. Root owns freeze/build, asset configuration, independent review and shared logs. No Browser action, HTML/PDF creation, broad audit, bulk download/extraction, deletion, commit or publication occurred.

## Exact source boundary

Both actual pinned m81374 modules contain Chapter Review wrapper `fs-id1167836524742`. This unit takes its complete second child, **`fs-id1167829740806`, Slope of a Line**, from its linked title and first paragraph `fs-id1167833047231` through final exercise `fs-id1167836792421`. The next actual sibling is **`fs-id1167836526512`, Find the Equation of a Line**. No preceding or later topic is imported; the later Practice Test `fs-id1167836628671` remains outside this unit.

| Item | Count |
| --- | ---: |
| Ordered selectors | 50 |
| Heading/instruction paragraphs | 14 |
| Original exercises | 36 |
| Supplied solutions | 18 |
| Explicit missing-source-answer notices | 18 |
| New questions / answers to source omissions | 0 / 0 |
| Original IDs in selected blocks | 165 |
| Original IDs including topic and Chapter Review wrappers | 167 |
| Total XML IDs including article/credits | 169 |
| Original image uses / distinct files | 9 / 9 |
| Personally inspected EN/ID images | 18 |
| Math-check spans | 50 |
| Local links / HTTPS references | 43 / 3 |

All locally numbered even questions have source solutions; all odd questions have no supplied answer and are explicitly marked. The 18 supplied answers comprise four graph-only answers, one mixed prose/graph answer, and thirteen text-only answers. The two application questions retain all eight subparts. Local numbering 1–36 is labeled as local, not reconstructed book numbering. The three HTTPS references are the original document-level title reference plus two attribution links. All eighteen source-answer pairs have reciprocal local links.

## Actual pinned sources and reading

| Locale | Existing archive and exact module member | Bytes | SHA-256 |
| --- | --- | ---: | --- |
| EN | `A20-canonical.zip` / `osbooks-prealgebra-bundle-38cae454e644abf9f0a623e876994553881597c9/modules/m81374/index.cnxml` | 247,327 | `021c29fa9a6ab3d5b06d2ef143a82d2ac818ed25fe6fd44ebf5d7a6be07a123a` |
| ID | `A20-v0.3.0-source.zip` / `source/modules/m81374/index.cnxml` | 247,303 | `d89a74aef766afca6a4ac7e1ae720f120d22cc771c11dd7e025c55bca1fabb8e` |

I read the complete selected EN and ID paragraphs, MathML, answers, subpart instructions and media descriptions in bounded pieces from these exact members. Both original ID sequences and nesting agree. Canonical EN governs and the pinned ID corpus corroborates; neither current repository HEAD nor current web exercises replaced the archive data.

The topic title's original link is `document="m81370"`, with no target ID. It is preserved as `data-source-document="m81370"` and a link to the [official OpenStax section 3.2](https://openstax.org/books/intermediate-algebra-2e/pages/3-2-slope-of-a-line). I opened its primary reader to verify the route/title. The draft explicitly says this is internet-dependent and does not claim the complete Marathi teaching module is locally present.

All original math identifiers remain unchanged. In particular, m denotes slope in earlier exercises but denotes meal count in Katherine's application; the draft gives an original warning against conflating these roles. Marjorie's s counts **student lessons**, not distinct students. Both applications retain weekly quantities and US-dollar amounts, rather than substituting a local currency or annual quantity.

## Original pixels, corrections and preserved unusual source text

The only source copies made were the nine named images from each archive, using `python -B mr-Deva-IN/tools/freeze_unit.py --review-images MR-BRIDGE-017 A20 IMAGE...`. The existing helper verifies complete archive byte counts/SHA-256 before reading the named members. No whole archive was extracted. I personally viewed every EN image and every ID counterpart. A final byte comparison confirmed each review file equals its exact ZIP member; all nine EN/ID pairs are identical.

Names below have prefix `CNX_IntAlg_Figure_03_06_` and suffix `_img_new.jpg`. Each locale totals **707,085 bytes**; all eighteen files total **1,414,170 bytes**. Review copies are ignored under `downloads/mr-Deva-IN/source-image-qa/MR-BRIDGE-017/`. The config intentionally has no asset entries until root freezes.

| Figure | Role / local question | Bytes each | SHA-256, identical EN and ID |
| --- | --- | ---: | --- |
| 222 | Question q1 | 90,732 | `2df8fb519799cfdabec17cbbd4cd6da2cff9f30aa8d04772760d37e3a6b0780f` |
| 223 | Question q2 | 91,810 | `74a804ccfcf03720c6785db1af2d3cc6bf540a937839ec195c32878d8334081a` |
| 224 | Question q3 | 92,004 | `d8f927e1f4324f8281f0b68453d136e2ebccaa17eb4b6439f86c0d2be37fcce4` |
| 225 | Question q4 | 93,091 | `be8232235bb72764d434e62fdfdbbc26b918f78f7fdf2a8565125caa8afe36b6` |
| 368 | Source answer q14 | 61,222 | `c47373c3a1e7e840cef847920b3712e26839b95023d8596ace858f74b7779fd1` |
| 370 | Source answer q16 | 64,824 | `9777a5ef85b6ca1b23c207713aca7002161e239f9ecd8386a94cd090118cadba` |
| 372 | Source answer q22 | 76,137 | `c2bd6537d15b04a006a3fb54b964ecec1c1786249a9259890ffb4021da77a5fa` |
| 374 | Source answer q24 | 77,308 | `ba1128cfbdadf82ecb11f8c9117deae187ce484b4cf3fd1422df8d3ed3bc6062` |
| 376 | Mixed source answer q32 | 59,957 | `23cc633bcd3f8e86c6fb1d66c7ad7057bf56e6da40ce81c1aa6d5bfc74a1a985` |

Two description issues were reported to root and disclosed explicitly:

- Figures222–225: both EN and ID alternative descriptions say both axes run from −6 to 6. All eight actual images show −8 to 8. The Marathi descriptions use the actual limits and a shared visible original correction note identifies the discrepancy. Points, questions, answers and pixels are unchanged.
- Figure376, media `fs-id1167833050702`: both actual images label the horizontal axis **h**, while the question and formula use **s** for lessons; the vertical label is **P**. The source alt generically calls these x/y. The Marathi alt names the actual h/P labels and a visible note maps the horizontal quantity to s in this question. No source label was silently redrawn. The unequal horizontal/vertical scales, original line and arrow are retained.

The other point descriptions and slopes agree with the actual figures and equations. The graph data imply slopes −3, 1, 1/3, −1/2, −1/3, −3/4, −1, 4/3 and 35 for figures222 through376 in the table order. This is checked from numerical coordinates/equations, not from the apparent screen angle under unequal scaling.

Question29, paragraph `fs-id1167836575257`, really contains a MathML fraction with numerator2 and denominator2: `y = (2/2)x + 2` in **both** archives. It is retained unsimplified. A note warns against reading it as 22 or 2; I did not assert that it was a typo or invent a replacement.

Source method answers “horizontal line”, “intercepts” and “plotting points” are preserved. The original note explains that “most convenient” need not imply the only mathematically valid method. Source application answers remain −250 dollars, 450 dollars, 35 dollars per extra lesson and a 250-dollar loss at zero lessons. Original count-domain notes distinguish the continuous formula picture from nonnegative whole lesson/meal counts and distinguish a plot window from a domain. They do not create missing source answers.

## Actual Marathi canon at selection, drafting and revision

The concrete new need was slope wording, absent from the existing terminology search. At selection I retrieved and read the primary [भूमिती entry](https://vishwakosh.marathi.gov.in/28194/), the paragraphs headed “रेषेचा उतार व दोन रेषांमधील कोन” and the later “रेषा” equation-form discussion. The readable text explicitly uses उतार and gives a slope/intercept form labeled उतार-खंड प्रकार. This informed “रेषेचा उतार” and the slope-versus-intercept distinction. It also supports समांतर and लंब terminology. Full classroom instructions remain authored translations, not quotations. The parallel/perpendicular slope statements have finite-slope context; they do not license assigning a numeric slope to a vertical line.

The duplicate primary entry at [28572](https://vishwakosh.marathi.gov.in/28572/) returned the same relevant slope passage, but no second canon locator was claimed. Root was sent the actual 28194 locator/passages and must personally read it before any global canon/term addition. I edited no shared ledger. A direct 28194 open succeeded, but subsequent targeted find calls returned internal-error/no-match responses; those failed lookups are not counted as successful new readings. A later targeted primary search again returned the relevant slope/coordinate prose, which I read during revision. Unrelated advanced claims, garbled quadrant signs and inaccessible image formulas were not imported.

During drafting/revision I also read C12's existing OCR at physical page85 / printed75, opening prose on उकल, equal operations and nonzero division. It guided the separation of undefined slope from zero and checking substitutions without treating division by zero as meaningful. This was an existing text witness, not fresh OCR/PDF visual review. The coordinate-order passage in the actually retrieved geometry entry supported the short original reminder that the first coordinate is x and the second y; source variables were not replaced by Marathi letters.

The final revision kept scalar intercept values separate from points: q15's x-intercept value −4 and q16's y-intercept value1 are not mislabeled whole ordered pairs; the original introduction explains b versus (0,b). “उतार-खंड रूपातील समीकरणांचे व्यावहारिक उपयोग” is a new classroom heading informed by, but not quoted from, the witnessed form label.

## Writer checks and corrections to the check harness

Read-only standard-library checks ran against actual disk files and both pinned modules. Final observed results were PASS:

- All50 selected IDs match the actual direct-child sequence; all167 contextual/source IDs, descendants and ancestry match both locales. All169 XML IDs are unique. No other-topic IDs were inserted.
- Each locale's **41 source MathML items** matches the corresponding target via exact Fraction values, tuple structure or symbolic affine coefficients. This is coefficient identity, not sampled-grid proof. Currency rendering is explicitly normalized from −$250 to −250 dollars. Source plain-text numerical answers1 and0 are separately checked and have math keys. Source plain-text intercept1 is separately checked too.
- All50 final displayed-math keys equal the config. The literal unsimplified2/2 is checked, as are all required terms, source image order,18 missing-answer markers and18 reciprocal source-answer link pairs.
- All18 review-copy files equal their exact ZIP members. The nine described point pairs yield the correct slopes. Supplied numerical slope/intercept answers, the three method answers, the application profit/rate and all four line-pair classifications were checked exactly. Classification checks for questions lacking source answers did not insert answers into the draft.
- Scalar/tuple source checks initially assumed every target numeric span corresponded to a MathML element; q16's source intercept1 is plain text. The harness was corrected to check that value separately. A later Fraction call initially failed to parse a Unicode minus in −250; it was changed to use the same explicit normalization as the other checked values. These were check-harness failures, not source or mathematical revisions, and only the successful final rerun is counted as PASS.
- Authored revision added the coordinate-order reminder to satisfy the chosen terminology check and removed trailing spaces from two checked math strings. No mathematical value or source ID changed.

The checks were ad hoc writer checks, not a separately authored independent test suite. XML/config creation used the already inspected source hierarchy as a mechanical ID/nesting scaffold, explicit Marathi prose/alt mappings, and source MathML transcription; unrecognized prose was not silently passed through. All authored files were written through the patch tool, with no persistent generator outside the three owned files.

Disk space was checked before writes: 4,585,996,288 bytes initially and 4,394,000,384 bytes at the final recorded check. Only the small named image copies and draft files were written; no cleanup was attempted.

Final writer pins before root's expected asset-configuration insertion:

| File | Bytes | SHA-256 |
| --- | ---: | --- |
| `translations/MR-BRIDGE-017.xml` | 43,757 | `f868cd613b00687a133ad6ede745749a3d78d0a7ac1e4fb4d700a9bf6b38cbf1` |
| `units/MR-BRIDGE-017.json` | 2,732 | `2fef04dff7b7ff0f92c244d5802b0338e1d53c20b2ad84e276cd34f218116277` |

## Ordered selections

Each ID has source prefix `A20:m81374#`; the two surrounding wrappers are not counted as extra selected blocks.

```text
fs-id1167833047231
fs-id1167836540143
fs-id1167836366545
fs-id1167829691193
fs-id1167836790118
fs-id1167836623132
fs-id1167836738035
fs-id1167833086454
fs-id1167836399770
fs-id1167836398874
fs-id1167829578786
fs-id1167829586801
fs-id1167829931428
fs-id1167824734049
fs-id1167836322980
fs-id1167836738195
fs-id1167836391480
fs-id1167836387581
fs-id1167829714127
fs-id1167836620933
fs-id1167829717719
fs-id1167829878927
fs-id1167836536584
fs-id1167829783830
fs-id1167836717185
fs-id1167836524200
fs-id1167836434016
fs-id1167836507861
fs-id1167829741996
fs-id1167836312931
fs-id1167836558639
fs-id1167836533072
fs-id1167833227116
fs-id1167836628505
fs-id1167836558141
fs-id1167836509786
fs-id1167829952812
fs-id1167833060079
fs-id1167833059952
fs-id1167833019834
fs-id1167836525357
fs-id1167836527756
fs-id1167826211804
fs-id1167829709310
fs-id1167833350392
fs-id1167836705885
fs-id1167836730415
fs-id1167836499090
fs-id1167836717592
fs-id1167836792421
```

Root may now freeze/build and commission independent source/math review. Those actions, reader visual QA and human/native-Marathi mathematics review remain pending. This checkpoint does not complete the remaining Chapter Review topics, m81374, any book or the full five-book task.
