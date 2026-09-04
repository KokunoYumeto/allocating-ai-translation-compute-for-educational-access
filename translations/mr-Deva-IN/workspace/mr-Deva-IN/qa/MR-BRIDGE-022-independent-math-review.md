# MR-BRIDGE-022 — independent source and mathematics review

Date: 2026-09-01. Reviewer: `second_unit_builder`, independent of the MR022 writer. Result: **PASS within source/mathematics scope.** I found no new defect requiring an XML/config change.

This is not Marathi-native or human-teacher approval, generated HTML/browser/PDF acceptance, accessibility acceptance, or production promotion. Only this report and `tools/test_unit22_math.py` were created/edited. The entire five-book assignment remains active.

## Evidence actually read

I read the complete frozen Marathi XML and config; the entire Practice Test sections in the pinned English and Indonesian m81374 module members; all 60 frozen selected fragments; and all 24 original EN/ID raster copies at original resolution. I also read the actual m81375 EN/ID introduction members to verify the stated next boundary. Writer notes were navigation clues, not substitutes for any of these reads.

| Frozen input | Bytes | SHA-256 |
| --- | ---: | --- |
| translations/MR-BRIDGE-022.xml | 44,623 | ec136afe3b909a855882c2b50dd1a34fb2ecd90aeaf15206326bbd2e9a176b66 |
| units/MR-BRIDGE-022.json | 6,669 | 17d561931c667a68ba00b9644fc9a5ef15e5ab5eb52ffbeca291c925cb7e39ea |
| provenance/MR-BRIDGE-022.lock.json | 100,801 | a3f0e9ade78d7e967bc4a47bc29b2a06158e15aa9d600bc2d7ea4ca08553275c |
| EN m81374/index.cnxml | 247,327 | 021c29fa9a6ab3d5b06d2ef143a82d2ac818ed25fe6fd44ebf5d7a6be07a123a |
| ID m81374/index.cnxml | 247,303 | d89a74aef766afca6a4ac7e1ae720f120d22cc771c11dd7e025c55bca1fabb8e |
| EN m81375/index.cnxml | 1,568 | 5577a5087c332c7c6eb5ee185dee43b98e8a754687985410be8b84e4173d53e9 |
| ID m81375/index.cnxml | 1,610 | e1204520eb35f8ade93655696d814c560deded28c18c5d7cfb525b38ffc2df23 |
| tools/test_unit22_math.py | 25,321 | a1693b0018e6dc5d87ef80ec9ba483e6dd5abb5be97eecb24738e89a07563a1e |

The module archives actually read were the existing bounded files `A20-canonical.zip` and `A20-v0.3.0-source.zip`; nothing was extracted wholesale or downloaded.

Structural findings:

- Exactly 30 ordered selectors: five instruction paragraphs and 25 exercises, beginning `fs-id1167833142400` and ending `fs-id1167832940626`.
- Exactly 124 source IDs, including the Practice Test wrapper, in original preorder and nearest preserved ancestry; article and credits yield 126 total IDs.
- Thirteen source-supplied solutions on odd-numbered questions and twelve explicit source-answer omissions on even-numbered questions. Every supplied problem/solution pair has one forward and one return anchor. All 31 local links resolve; the only two nonlocal links are HTTPS OpenStax and license URLs.
- Sixty frozen EN/ID fragments total 57,808 bytes and match the corresponding module elements structurally, by fragment hash and by every recorded MathML hash.
- All 81 local witnesses match byte count/SHA-256. Component notices remain in scope without beginning a new general license audit.
- Exactly 65 unique data checks: 53 source MathML displays, six literal source text/combined interval displays, and six visibly original clarifications. One source MathML occurrence is only the partial `−4,` embedded inside the q25 range; it is accounted for and consolidated into the complete R display rather than pretending to be a separate expression.
- Five source instruction paragraphs and all source subpart labels are preserved. Config counts 25 translated practice items, zero new practice items, definitions or worked examples, and an empty original-`question_ids` list.
- The actual m81375 members are titled Introduction/Pendahuluan, begin with `CNX_IntAlg_Figure_04_00_001`, then `fs-id1167836596342`. The credit's next-marker statement is accurate.

## Independent mathematical results

Exact arithmetic uses `fractions.Fraction`. Linear/polynomial expressions pass through a strict AST whitelist and coefficient comparison, never `eval`. The calculations below are reviewer checks; where the source omits an answer, they are deliberately not inserted into the translation.

| Q | Independent check |
| ---: | --- |
| 1 | All five points match the statement and pixel397: (2,5), (−1,−3), (0,2), (−4,3/2), (5,0). |
| 2 | Substitution in 3x−y=6: (3,3) and (2,0) satisfy it; (4,−6) gives 18, not 6. |
| 3 | From (−5,2) to (0,−1), slope is −3/5. The second line has Δx=0, so slope is undefined, not zero. The supplied answer is correct. |
| 4 | Between (5,2) and (−1,−4), slope is 1. |
| 5 | Slope 1/2 through (−3,−4) gives y=(1/2)x−5/2; the three supplied graph points are collinear with that formula. |
| 6 | 4x+2y=−8 has intercepts (−2,0) and (0,−4). |
| 7 | Pixel400's points satisfy y=(5/3)x−1. |
| 8 | y=−x is retained; source supplies no graph answer. |
| 9 | Pixel402 is horizontal y=2; the supplied graph is correct. |
| 10 | Slope −3/4 and y-intercept (0,−2) give y=−(3/4)x−2. |
| 11 | Substituting (−3,−1) with m=2 yields b=5; source y=2x+5 is correct. |
| 12 | The two points give slope 1/2 and b=−4, hence y=(1/2)x−4. |
| 13 | Perpendicular slope is −4/5 because (5/4)(−4/5)=−1. Through (−10,3), b=−5; supplied y=−(4/5)x−5 is correct. |
| 14 | Solid boundary y=−x−3 and shaded test point (−5,0) yield y≤−x−3. Source omits the answer. |
| 15 | For y>(3/2)x+5, the boundary is dashed and excluded; (−5,5) satisfies it while (5,5) does not. Pixel403 agrees. |
| 16 | x−y≥−4 rearranges to y≤x+4: multiplying by −1 reverses the sign. Boundary points are included. Source omits the graph. |
| 17 | y≤−5x uses a solid included boundary. Pixel405's shaded test point (−5,0) satisfies it and (5,0) does not. |
| 18 | The model is 10x+15y≥450 with x≥0,y≥0 for hours. The source supplies no answer; the target does not insert this model or three pairs as an answer. |
| 19 | Every input in the seven listed pairs occurs once; y=|x|³ on that finite list. Domain is {−3,−2,−1,0,1,2,3}; range {0,1,8,27}. Supplied “yes” is correct. |
| 20 | For f(x)=4x²−2x−3: f(−1)=3, f(2)=9, f(c)=4c²−2c−3. No answer is inserted. |
| 21 | h(−4)=3|−5|−3=12. The supplied source answer is correct. |
| 22 | The complete pictured shifted cubic-shaped curve passes the vertical-line criterion. This is manual full-curve reading, not a universal conclusion from its three labelled points. |
| 23 | f(x)=x²+1 has D=(−∞,∞), R=[1,∞); all supplied graph points satisfy the formula. Algebraically x²≥0 and every nonnegative square value is attained, so this is not a finite-grid proof. |
| 24 | f(x)=√(x+1) has D=[−1,∞), R=[0,∞). The full radical grouping is preserved. For any y≥0, x=y²−1 attains y; negative outputs are excluded by the principal root. No answer is inserted. |
| 25 | The intended graph is y=x²−4. All five source coordinates, f(±1)=−3, D=(−∞,∞), R=[−4,∞), and source coordinate answers x=−2,2 / y=−4 are correct. The original explanatory paragraph adds the requested full intercept points (−2,0),(2,0),(0,−4) without deleting or relabelling the literal source answers. |

The q18 clarification is appropriately scoped: hours cannot be negative, but the source does not impose integrality or a maximum. The paragraph is marked original, appears after an explicit missing-source-answer notice, and explicitly says it does not fill the inequality/three-pair solution. The two checks are only `x ≥ 0`, `y ≥ 0`.

Universal function/domain/range statements are justified algebraically or by the complete intended curve. Finite points are used for substitution regressions and counterexamples, not promoted into proofs of a unique global formula.

## Pixel arbitration

I personally viewed both EN and ID copies of every image below. Each pair is byte-identical; each committed EN asset and local review copy also matches its lock/config pin. Total committed image bytes: 778,637.

| Figure | Bytes each | SHA-256 each | Observed window/style |
| ---: | ---: | --- | --- |
| 250 | 80,707 | eeb45bb253397500b3978705d0bb621c19dd4a1772882c1b4ea469aaf6cb7b55 | Both axes −6..6, step1; descending line |
| 251 | 78,479 | 811599759f9e98652fdb6c3c61036a87a328218e5772db69a885cf7e4b8ac711 | Both axes −6..6, step1; vertical x=2 |
| 252 | 78,764 | 32368a9318bf5aacf3074e4ea40d105b661f319a49691703fa82f7a673cf98d0 | Both axes −10..10, step2.5; solid red boundary, pink below-region |
| 253 | 71,014 | d4f05b3f293e8678ce64321e149401f691a370bb094a382d802a2132409b0ec9 | Both axes −8..8, step2; shifted cubic S |
| 254 | 62,811 | e379840f630eb048340780d98125fa72514b477b454d1e82cc1a65c9fe67d4a4 | Both axes −8..8, step2; vertex (0,−4) |
| 397 | 34,350 | d1bfc9c9ab84b7bfb0b942c24577d65d187866f3f9a50691a7806b186f34c9e0 | Both axes −8..8, step2; five unjoined points |
| 398 | 65,264 | 2d27a971a03586905c2eac78f0f4d5321ea073c07db3f3a3e2374fd8bdbad8e2 | Both axes −8..8, step2; slope1/2 |
| 400 | 65,867 | 3ceb3f205a3220eea77800094f641dcfa7239856b00125a43f38ad0029222ff4 | Both axes −10..10, step2.5; y=(5/3)x−1 |
| 402 | 63,208 | 79bd16a75d86c390ac5636c200133e06f7756dac2d177808236895fc08ea6bc5 | Both axes −10..10, step2.5; horizontal y=2 |
| 403 | 78,327 | 83060ebfe938c41c5b1fe47bc31ac7e3fe8548e4651c304cd3a7ab25430a79ac | Both axes −10..10, step2.5; dashed dark-blue boundary, pink upper-left |
| 405 | 38,662 | c8b425c4920baf9aa86308e99150b9cc4bac48b2056aed2a73f7842c8b0cf9ae | Both axes −8..8, step2; solid dark-blue boundary, pink solution region |
| 407 | 61,184 | 0002509ba8ca7387b8c3779857ec253f71562fa1ac1c593f834d95361cd94acf | x −8..8, y −4..10, step2; vertex (0,1) |

The visible/source-description divergences are correctly disclosed:

- Both397 source alts claim axes −10..10, but pixels show −8..8.
- Source alts for250/251 claim −10..10, but pixels show −6..6. Source alts for398 claim −10..10, but pixels show −8..8.
- Both253/254 source alts claim −6..6; pixels show −8..8. Pixel407 differs from the source alt's x −6..6, y −2..10 and visibly has x −8..8, y −4..10.
- EN403 explicitly says dashed; ID403 omits that word, although both pixels are dashed. Target preserves the strict-boundary fact and names the ID omission.
- Both405 source alts call the boundary and shaded part red. The actual boundary is dark blue and solid; shading is pink. Target corrects color while preserving inclusion and solution direction.
- “Every square is one unit” would be wrong for several images. The target distinguishes step1, step2 and step2.5.

These are manual observations bound to exact bytes, not an automated semantic-image test or output-rendering claim.

## Marathi canon consultation

I performed fresh official-domain reads during review; these are not inherited claims from an earlier unit:

- [भूमिति २ ०](https://vishwakosh.marathi.gov.in/28572/): read the actual point–slope and slope–intercept paragraphs, including y−y₁=m(x−x₁) and y=mx+g. Effect: check the Marathi working description and all q10–13 line derivations. The target's full compound “उतार–y-अक्षछेद रूप” remains a context-specific authored phrase; only the narrow उतार term is treated as canon-supported.
- [वक्र](https://vishwakosh.marathi.gov.in/32227/): read the actual sentence defining a tangent-line slope through the tangent of its angle with the x direction. Effect: corroborate the narrow mathematical use of उतार, without importing calculus claims into these straight-line exercises.
- [भूमिती](https://vishwakosh.marathi.gov.in/28194/): read the actual Cartesian-coordinate passage explaining the ordered (x,y) coordinates and axis signs. Effect: verify x-first ordering, plotted quadrants and q25's distinction between coordinate values and complete points.
- [फलन](https://vishwakosh.marathi.gov.in/27548/): read the actual exactly-one correspondence, प्रांत/सहप्रांत and image-set-as-subset paragraph. Effect: check q19/q22 functionality and preserve the distinction between actual range and codomain.
- [आलेख](https://vishwakosh.marathi.gov.in/24316/): read the actual coordinate/scaling material exposed by fresh official search. Effect: treat visible grid scale separately from mathematical domain/range and avoid connecting q1's independent points.
- [गणितातील चिन्हे व प्रतिके](https://vishwakosh.marathi.gov.in/21279/): reread the actual केवल मूल्य, infinity and interval rows. Effect: check q21's bars and q23–25 interval endpoints.
- The official C18 search exposed “असमा” usage and inequality graphs, but did not attest the full authored compounds for solid/dashed boundaries or shaded half-planes. Those remain transparent working language, not falsely canon-attributed terms.

Direct page fetches are intermittently 502; fresh official-domain search returned the readable actual passages used above. No PDF, OCR loop, global canon-ledger change, or native/human endorsement is claimed.

## Test result and limitations

Run:

```powershell
python -B mr-Deva-IN/tools/test_unit22_math.py
```

Final result: **25 tests passed, zero skipped**, in 0.726 seconds. The first run surfaced only three test-harness mistakes and one object-identity setup error: a test compared equivalent fractional typography as raw text, expected ASCII minus from source MathML, and reparsed an XML tree before an identity-based parent lookup. Only the new test file was corrected; no source/translation/config content changed. The passing rerun includes all fixes.

The suite is read-only and self-contained. Missing files, witnesses, archive members or images fail rather than skip. It checks exact frozen pins, all fragments/MathML hashes, source-ID ancestry, answer/omission roles, links, assets, pixel descriptions, full expression keys, exact rational computations, inequality boundaries/test points, Hiro's role separation, all q25 literal and authored intercept forms, and unsafe-expression/path rejection.

The AST checker is intentionally bounded; it is not a general CAS. Image observations are manual and hash-bound, not computer vision. The suite does not inspect generated HTML/PDF, font shaping, layout, interaction or accessibility in the reader. A structural build/PDF receipt/mathematics PASS cannot be promoted into HTML QA. No browser, staging, commit or push was performed; coordinator/root retains those workflows.

