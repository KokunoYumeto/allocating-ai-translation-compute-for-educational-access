# MR-BRIDGE-021 — independent source and mathematics review

Date: 2026-08-31. Reviewer: `second_unit_builder`, a separate agent from the MR021 writer. This is an independent source/mathematics review, not a Marathi-native or human-teacher endorsement, automated visual proof, HTML/browser/PDF acceptance, or production-readiness promotion.

Result: PASS within this scope. No new translation defect requiring an XML/config change was found. All 29 stdlib regression tests pass with zero skips; the final recorded run took 0.339 seconds. Only this report and `tools/test_unit21_math.py` were created/edited by this reviewer. Parent/root owns the unchanged translation, config, provenance and format decisions. The full five-book assignment continues.

## Actual inputs and scope

I read the whole frozen Marathi XML/config, both complete original EN/ID source topics from their existing ZIP members, their metadata/title and immediate topic boundaries, and the 62 frozen selected fragments (52,245 bytes) compared structurally to those original members. I personally viewed all 36 original source-image copies at original resolution; they were not replaced by writer notes, source alt text, a contact-sheet inference, or a prior unit's review. Each of the 18 EN/ID image pairs proves byte-identical here. Their identity is a result, not an assumption used to skip the second view.

The source is A20:m81374, Chapter Review `fs-id1167836524742`, its sixth and final topic `fs-id1167836699953` (“Graphs of Functions” / “Grafik Fungsi”). Its title points back to m81374. I read the actual metadata UUID `4b2bbf1b-2df7-4b9a-9933-dd70d1fd8ada`, its title and the three learning-objective items. Topic predecessor is Relations and Functions `fs-id1167826172554`; after the enclosing Chapter Review the actual next content section is Practice Test / Tes Latihan `fs-id1167836628671`. This review does not translate or claim that next section complete.

Exact frozen input pins, independently measured after root released them:

| Input | Bytes | SHA-256 |
| --- | ---: | --- |
| translations/MR-BRIDGE-021.xml | 49,033 | d179b984c1f22e796831e9f7d001e3b40634df8cc269c6c6b2e76e0fe0fcc5c9 |
| units/MR-BRIDGE-021.json | 7,709 | 6f210e5cb2266acf23214379684efa336f32c39bb0c3e1aa4621f275826ac4a6 |
| provenance/MR-BRIDGE-021.lock.json | 110,903 | 0128fa9f9e7fab0b5e9e68cfbd70d58e84495a13eb79260b2b9d1e41af8fcbc8 |
| Original EN m81374/index.cnxml | 247,327 | 021c29fa9a6ab3d5b06d2ef143a82d2ac818ed25fe6fd44ebf5d7a6be07a123a |
| Original ID m81374/index.cnxml | 247,303 | d89a74aef766afca6a4ac7e1ae720f120d22cc771c11dd7e025c55bca1fabb8e |
| tools/test_unit21_math.py | 46,422 | 87a64e2d51de6bcd902700e538cb8861c975da7c35d803166145b260ff883b53 |

Archives actually read, without extracting their contents:

- `downloads/mr-Deva-IN/releases/A20-canonical.zip`, member prefix `osbooks-prealgebra-bundle-38cae454e644abf9f0a623e876994553881597c9/`.
- `downloads/mr-Deva-IN/releases/A20-v0.3.0-source.zip`, member prefix `source/`.

The unit lock's recorded whole-archive digests remain, respectively, `effdf2dbb6dfd9cab771b568c6575d8074be4a1f9565f1fedbd54f621e138917` and `a9c53c328be944e12b707d5cb16e289755eff0c603d1652bfca13dd572e780d7`. This bounded suite checks the recorded archive references plus actual selected module/image bytes; it does not reread whole large archives merely to recompute their overall digests. All 89 local witnesses, including the parent corpus lock, component notices, source fragments and 18 assets, are read and matched to their own recorded byte counts/SHA-256. Component notices are retained without starting a new general license audit.

Structural results:

- Exactly 31 ordered direct selectors: seven source heading/instruction paragraphs and 24 exercises. First `fs-id1167836597214`, last `fs-id1167832994434`.
- Exactly 111 source IDs in the selected descendants, plus topic and Chapter Review wrappers = 113 original IDs, each present once in original preorder with nearest preserved source ancestry unchanged. Article and credits yield 115 total IDs.
- Twelve source-supplied solutions, on local odd-numbered questions 1–23; twelve explicit original “source answer not supplied” notices on even-numbered questions 2–24. The suite does not insert its independent answer calculations into those omissions.
- All twelve original problem/solution pairs have exactly one forward and one return link. Total 28 local anchors and three HTTPS links; no missing local target.
- The title's original m81374 backreference is preserved as the external OpenStax 3-6 URL and explicitly described as requiring Internet. The other two URLs are the OpenStax chapter introduction and CC BY-NC-SA 4.0 notice. No external image, script or media dependency was introduced.
- Exactly 54 distinct config/display math keys: 35 source MathML-derived occurrences, 14 displayed D/R components (including the corrected constant R), and five clearly original reminder/correction/conditional keys. There are 36 MathML nodes per source language: the extra partial `−2,` in the q17 D interval is consolidated into its complete D display, not dropped. Both languages' 72 MathML hashes and all source-derived key locations are accounted for.
- Config remains 24 translated practice items, zero worked examples, definitions, resource notes and original practice items. Empty `question_ids` counts no original question/answer pairs; it does not mean the twelve source pairs are absent.
- NFC, no replacement character, all required Marathi terms, retained component-credit caveat, and explicit unfinished full-assignment statement pass.

## Mathematics: independent checks and reasoning

The suite compares each actual source and target formula with a separately read expected expression through a strict AST whitelist and exact rational coefficient arithmetic. It never calls `eval`. Fraction division, sign, exponent, radical scope and absolute-value bars remain explicit. Model classification is restricted to the actual simple families in this topic; it is not a general symbolic theorem prover.

### Vertical-line questions 1–7

The supplied answers are q1 yes, q3 no, q5 yes, q7 no, unchanged in meaning. I examined the complete depicted curves, not just the listed points. Q1 is an upright upward parabola and q5 is a single-valued increasing cubic-shaped curve. Q2's sideways-spread increasing S curve is also single-valued as drawn, but its missing source answer remains missing. Positive judgments are graph-reading judgments of the intended full curves, not a claimed universal proof from three finite sample coordinates.

For nonfunctions a single valid same-x/different-y pair suffices:

| Question / figure | Counterexample read from source/pixels |
| --- | --- |
| 3 / 240 | x=0 has y=−5 and y=5 on the circle |
| 4 / 241 | x=−1 has y=−1 and y=1 on the right-opening parabola |
| 6 / 243 | x=4 has y=−2 and y=2 on the two-sided curved diagram |
| 7 / 244 | x=1 has y=−2 and y=0 on the sideways V |

The original q7 description's “sideways absolute value function” is potentially misleading as a function of x. Target alt describes the two right-opening straight branches, its caption discloses the source wording, and the supplied “no” is intact. The authored vertical-line reminder correctly restricts exactly-one-output to inputs in the domain; a vertical line with no intersection denotes an x outside the domain, not automatically a failure of functionality.

### Formula questions 8–19

The table gives independent reviewer results. Rows whose source has no answer are checks of the posed mathematical task, not newly translated or inserted solutions.

| Q | Actual formula | Domain | Range |
| --- | --- | --- | --- |
| 8 | f(x)=5x+1 | (−∞,∞) | (−∞,∞) |
| 9 | f(x)=−4x−2 | (−∞,∞) | (−∞,∞) |
| 10 | f(x)=(2/3)x−1 | (−∞,∞) | (−∞,∞) |
| 11 | f(x)=−6 | (−∞,∞) | {−6}, equivalently [−6,−6] |
| 12 | f(x)=2x | (−∞,∞) | (−∞,∞) |
| 13 | f(x)=3x² | (−∞,∞) | [0,∞) |
| 14 | f(x)=−(1/2)x² | (−∞,∞) | (−∞,0] |
| 15 | f(x)=x²+2 | (−∞,∞) | [2,∞) |
| 16 | f(x)=x³−2 | (−∞,∞) | (−∞,∞) |
| 17 | f(x)=√(x+2) | [−2,∞) | [0,∞) |
| 18 | f(x)=−\|x\| | (−∞,∞) | (−∞,0] |
| 19 | f(x)=\|x\|+1 | (−∞,∞) | [1,∞) |

Universal arguments, separate from illustrative exact Fraction substitutions:

- A nonzero affine coefficient has real inverse x=(y−b)/a. A constant has only its constant output. The test compares coefficients and distinguishes these cases.
- For ax²+b here, x² is nonnegative; all nonnegative square values are attained over the reals. The sign of a selects the lower- or upper-bounded range, and x=0 attains the finite endpoint.
- Every real output for x³−2 has a real cube-root input. Its domain/range result is not inferred from a finite grid.
- For q17, the actual MathML `msqrt` encloses all of x+2. Its real domain requires x+2≥0, and the principal root is nonnegative. For every y≥0, x=y²−2 attains y; negative outputs are excluded. The tests include exact fractional inverse witnesses and reject x<−2. Those witnesses supplement, not replace, the argument.
- For q18/q19, |x| is nonnegative and every nonnegative value is attained, including zero. The external minus and +1 shift are preserved.
- Infinite interval ends are open because infinity is not a real endpoint. A closed degenerate interval [−6,−6] contains exactly −6; it is neither (−6,−6) nor {6}.

Every point in the six supplied formula-answer graphs (386,388,390,392,394,396) was checked against its formula. Q9's (−2,6) satisfies −4x−2, but y=6 lies outside the actual −4..4 image window; the target correctly says that it is outside the visible frame instead of pretending it appears there.

### Questions 20–24

Q20/245 is an intended square-root curve beginning at (1,0), through (2,1),(5,2), with rightward continuation. Reading the source's stated curve family gives D=[1,∞), R=[0,∞); no source answer is supplied or manufactured. The three points do not uniquely determine an arbitrary function, so no exact formula is asserted from them alone.

Q21/246 is an upward V with vertex (0,2), both ends continuing upward. The supplied D=(−∞,∞), R=[2,∞) is correct and retained. Q22/247 is the intended cubic-shaped graph, with left local hump and right local dip, continuing downward-left/upward-right. The expected source-graph reading has real D/R; no unique polynomial is fitted to its three reported points and no answer is added.

Q23/248: I read the nine reported wave coordinates in both sources and both pixels. The requested values are f(0)=0, f(π/2)=1, f(−3π/2)=1. The five displayed-window zero inputs are −2π,−π,0,π,2π, with corresponding five x-intercepts (−2π,0),(−π,0),(0,0),(π,0),(2π,0); the y-intercept is (0,0). All five source entries remain intact. Supplied D is corrected to (−∞,∞), and supplied R=[−1,1] is retained, including attained extrema. All eight question and answer subpart labels are preserved.

The source describes infinite continuation of the pattern but supplies neither an exact sine formula nor a formal periodicity condition. The target's separate original paragraph is therefore appropriately conditional: only if the zeros continue every π both ways with no additional zeros does x=kπ, k any integer, describe all zero inputs and (kπ,0) all x-intercepts. It expressly says arrows alone do not prove the infinite zero set. The tests guard that hypothesis, its authored role and its distinction from the preserved five source entries. Neither tests nor review infer a global sine law or global periodic theorem from finite samples. The retained global D/R is the source's intended full-graph answer, not independent identification of an arbitrary function beyond a finite raster.

Q24/249 is the upper semicircle from (−2,0) through (0,2) to (2,0), with neither continuing arrows nor open endpoint circles. Its six independent readings are f(0)=2; zero inputs −2,2; x-intercepts (−2,0),(2,0); y-intercept (0,2); D=[−2,2]; R=[0,2]. On the intended semicircle x²+y²=4 with y≥0, those endpoints and extrema follow directly. The target still explicitly says no source answer was supplied. All six prompts and all four embedded MathML terms remain.

## Source errors and image arbitration

Three mathematical source defects are independently confirmed in the actual frozen EN and ID text, and visibly corrected rather than silently rewritten:

1. Q11: the formula and horizontal raster388 have value −6. EN's range text is `R: (6)`; ID's is `R: {6}`. Both omit the minus. EN additionally uses unsuitable singleton parentheses. Target gives {−6}, explains both source forms and offers [−6,−6] for the interval-notation instruction.
2. Q23(a): both source answers print f(x)=0, although the question asks f(0). Target gives f(0)=0 and names the correction.
3. Q23(g): both original MathML trees have closed infinity delimiters. Target gives open infinities and explains why. No numeric endpoint or finite source intercept is discarded.

All 18 independently read finite grid windows follow. Bounds refer to the last grid lines, not just numbered tick labels; the grid increment is not always the label interval.

| Figure | x grid | y grid | Grid increment | Shape/end observations |
| --- | --- | --- | --- | --- |
| 238 | −4..4 | −2..6 | 1 each | Upward parabola, vertex (0,1), two upper arrows |
| 239 | −4..4 | −4..4 | 1 each | Increasing horizontal-spread S, opposite-end arrows |
| 240 | −8..8 | −8..8 | 2 each | Origin-centred circle with radius 5 |
| 241 | −8..8 | −8..8 | 2 each | Right-opening parabola, left vertex (−2,0), two right arrows |
| 242 | −8..8 | −8..8 | 2 each | Upright increasing cubic-shaped curve |
| 243 | −8..8 | −8..8 | 2 each | Two outward curved branches, vertices (−3,0),(3,0), four arrows |
| 244 | −8..8 | −8..8 | 2 each | Two straight right-opening V branches, vertex (0,−1) |
| 245 | −2..10 | −2..8 | 2 each | Curved square-root graph starts (1,0), right arrow |
| 246 | −6..6 | −2..10 | 2 each | Upright V, vertex (0,2), two upper arrows |
| 247 | −8..8 | −8..8 | 2 each | Cubic-shaped curve with local hump/dip, opposite arrows |
| 248 | −2π..2π | −6..6 | π/2 horizontally, 1 vertically | Wave, visible extrema ±1, opposite arrows |
| 249 | −8..8 | −8..8 | 2 each | Upper radius-2 semicircle, closed endpoint reading, no arrows |
| 386 | −4..4 | −4..4 | 1 each | Decreasing line through (−1,2),(0,−2) |
| 388 | −4..4 | −7..2 | 1 each | Horizontal y=−6, both end arrows |
| 390 | −4..4 | −1..10 | 1 each | Upward 3x² parabola, vertex origin |
| 392 | −8..8 | −2..10 | 2 each | Upward x²+2 parabola, vertex (0,2) |
| 394 | −4..8 | −4..8 | 2 each | Curved √(x+2), starts (−2,0), right arrow |
| 396 | −8..8 | −2..10 | 2 each | Upright \|x\|+1 V, vertex (0,1), upper arrows |

Source alt axis bounds disagree with pixels for all listed figures except246/248; each target caption discloses its correction and target alt uses the actual window. In particular, 388 extends to a bottom grid y=−7, even though the last lower labelled tick is −6; 390's bottom grid is −1. The EN/ID files are unchanged.

For245/394, both source descriptions call the shape a half-line (`half-line` / `setengah garis`). Both pixels are visibly curved. Additionally, the exact successive point slopes are 1 then 1/3 in each case, already sufficient to disprove a single straight ray through those points. Target corrects the wording and preserves the original raster/media ID.

### Exact hashes of all personally viewed original pixels

Every name below is `CNX_IntAlg_Figure_03_06_N_img_new.jpg`. I viewed both `en-` and `id-` copies under `downloads/mr-Deva-IN/source-image-qa/MR-BRIDGE-021/`. For each row the EN and ID bytes and SHA-256 are equal; the single row records both, not an omitted ID inspection. The EN committed copy under `assets/MR-BRIDGE-021/` is also byte-identical. Total EN assets: 1,123,397 bytes. Both-locale review bytes: 2,246,794.

| N | Bytes in each EN/ID original | SHA-256 in each EN/ID original |
| --- | ---: | --- |
| 238 | 60,666 | c9d3bd5d527430a74cba19b4bb5a4215bd217ffe8117fd6a4f9e1bdca2b1ea5f |
| 239 | 59,326 | 6b5c8309a1536afad670ed6c35ffd21cfbe0a71956e6a4be1cfd466587696634 |
| 240 | 63,527 | f4f66b8ada6e28df48a35f601cbd9be1650bedecb00583cd1e959edfd25dd7fa |
| 241 | 61,255 | c294f4d9e193db4c8fd4319abb13d10b198ad0baf14949af08110d92c122958f |
| 242 | 70,256 | 7fe327900f8184b690c3ec0e4e81a3ddbe6f8745fc29cce3d284eb78170ecd89 |
| 243 | 75,317 | 514f0e759e5bb9ab421fe53b712ba82e618c03ee1ea88e8477b86e99dcd92267 |
| 244 | 73,577 | bc483225bc9abe5cd1f044028617b93735c3ffc1a990f25613b7a915ad588d22 |
| 245 | 54,043 | ce84d0bc1735dbcc8edf05245e03c422bdc673952ba5130e1c159586996e836b |
| 246 | 59,643 | 1f4bd3f0837aaefd66ba06326cdfec5e12eaf08afa7f38d5bc3faf2ccc4324c7 |
| 247 | 71,630 | 3c647479f45adb7e70c61550aa17cf3feaae3bc54d9fdb02e4cd2746141daeff |
| 248 | 58,088 | 975930511beac19bf91733646033c5796cb3bbe36f4ac05a32f1e8d84dde2eb9 |
| 249 | 67,175 | e445bfce3807e1df8c29ce6faf80a2afee50165bdc01d218253e1b3231180b24 |
| 386 | 60,424 | ab171ad4a8e50f32c7d1580c89accd56b4ab7328d54f80f2ec2097fff2d9d9f7 |
| 388 | 57,305 | 4f4461770b3bc5cad39b9525dd09183d05f6e823a771cdf2143c170d3049cb8f |
| 390 | 65,200 | fbfe0c7291dadbe7e21d97f847f765f6af9b1893dd87d3d95ae14c7d16ca65fc |
| 392 | 59,804 | 0d19ef498951647b0c2394271422e05a401fae74b7a9a87293dd5f69981f6463 |
| 394 | 42,900 | 013dd59a0893bb1e212da42376cb422078914cf7a06150e52db4688d18293b9d |
| 396 | 63,261 | 0b5f751f7296c357a95ad935ae8b2b3ee9d874dbd4f571ec11c440c3e8ad7752 |

The tests compare actual archived bytes, each local review copy, lock records, committed EN assets and config pins. Passing these comparisons binds the manual observations to exact files; it does not rerun semantic image recognition or certify generated output.

## Actual Marathi canon consultation and its effects

Consultation was active during source selection/review and revisited while validating interval/radical/correction language. This is not a claim based only on downloaded resources or a remembered prior-unit report.

- [C14–C16, फलन (Function)](https://marathivishwakosh.org/21979/): I read the actual official result's opening dependence discussion, exactly-one-correspondence definition and प्रांत/सहप्रांत prose. Effect: check that the target's unique-output reminder is restricted to each domain input, and that actual range is not equated automatically with codomain. The page exposes some formula images as QuickLaTeX placeholders; I did not claim to have visually read those unavailable formula images.
- [C18, आलेख](https://vishwakosh.marathi.gov.in/24316/): direct open returned 502. Fresh official-domain search then exposed the actual coordinate/scaling paragraph, including how the two axis coordinates identify a plotted point and selecting scales to fit data. Effect: check x/y order, visible windows and grid increments separately from actual domain/range. Its instruction about joining sequential observational points is context-specific; I did not turn it into a rule that square-root graphs or arbitrary sampled functions are straight segments.
- [C19, फलन](https://vishwakosh.marathi.gov.in/27548/): direct open returned 502, followed by a successful fresh official-domain text result. I read the opening exactly-one association, domain/codomain and image-set-as-subset description, plus the actual periodic-function paragraph. Effect: retain the distinction between domain, actual outputs and codomain; require a stated periodic relation before treating an extension as a periodic formula. The article uses कक्षा for its image set; the unit's existing मूल्यसंच terminology is not newly attributed to that exact sentence. Unrelated problematic statements elsewhere in the long article are not adopted as mathematical authority.
- [C20, गणितातील चिन्हे व प्रतिके](https://vishwakosh.marathi.gov.in/21279/): fresh official-domain text results were read, and the exact relevant rows were reread during final test revision: केवल मूल्य / चिन्ह निरपेक्ष मूल्य, set braces, open/closed/half-open interval names, infinity and function notation. Effect: verify absolute-value usage and distinguish open infinity from a closed singleton interval. The selected compound अंतराल-संकेतलेखन and the mathematical endpoint explanation are authored context, not a falsely attested verbatim compound. The interval rows support the narrow existing अंतराल term; no new global term was promoted.
- [C21, गणितीय प्रतिरूपे](https://vishwakosh.marathi.gov.in/21277/): direct open returned 502; a fresh official-domain result provided the actual full शंकुच्छेद paragraph. I read its अन्वस्त (parabola) correspondence and its point that a model illustrates a principle rather than replacing proof. Effect: confirm the narrow अन्वस्त usage in the target graph descriptions and keep manual diagram interpretation distinct from algebraic proof. No new canon ledger entry or global term registration was made.

The temporary first function query was too broad and returned unrelated search hits; those were not used as Marathi mathematical evidence. Successful consultations above are to the actual official pages' readable text. No new PDF was acquired or rendered, and no unread/OCR-inaccessible PDF was cited as read. No Marathi-native/human approval is claimed. These checks found no further wording correction necessary in MR021; the independently verified corrections were already visibly authored in the frozen draft.

## Reproduction and test limitations

Run from the repository root:

```powershell
python -B mr-Deva-IN/tools/test_unit21_math.py
```

This is a read-only real-input suite with no optional test skips and no dependency on another unit's test/helper. Missing input/witness/archive member/image fails; it does not silently substitute a synthetic fixture. It checks 29 named test groups, including source pins and serialization, all source-ID ancestry, all MathML bookkeeping, exact formulas, D/R family reasoning, original answer/omission roles, twelve source link pairs, images/axis descriptions, all wave and semicircle subparts, conditional extension, and rejection of unsupported executable expressions, malformed intervals, bad root scope/sign and path escape.

The first run had 28/29 passing because my axis-language guard incorrectly required the combined phrase “both axes” for394, whose target explicitly and correctly lists x and y separately. Only the test guard was corrected. The second run passed29/29; I then added exact per-MathML hash comparisons and explicit x/y-token/source y-intercept comparisons. The final29/29 run above includes those additions. No source/translation/config pin changed.

Strict AST tests are bounded to the present arithmetic; exact Fraction witness checks are regressions, not independent proofs of all real-function behavior. The analytical arguments and manual full-curve observations above state the actual justification and limitations. Byte pins intentionally make any future source/translation/config change require renewed review. Pixel observations are manual, not an OCR or computer-vision oracle.

This review made no browser or alternate-browser action and did not open generated HTML/PDF. A root structural build, a PDF receipt or this mathematics PASS must not be promoted into HTML reader QA. Accessibility beyond source-alt content, layout, Devanagari shaping, page breaks and interactive rendering remain parent/root workflow obligations. No GitHub branch/push, staging or commit was performed; consolidated publication and upstream tracking stay with the coordinator. The entire five-book assignment remains unfinished and active.
