# U06 independent model review

Status: **CLOSED — PASS for the stated independent model-review scope** on the exact bytes below. All five prior findings are resolved, all twelve prompt/key pairs and all seven worked examples are mathematically correct, and no further learner-facing, mathematical, visual, trace, or source/editorial-boundary defect was found. This is not independent human validation.

## Exact scope and byte binding

- Translation: `translations/U06-companion.md` — SHA-256 `4e6c18468d98f67b04d34b719d5426d5065e0317787e31a0d79400f5d5669db3`
- Consultation record: `canon/U06-consultations.json` — SHA-256 `2db8c2b2c857e40b95e4e38f4fa9b7a43ed7ebfddd40c8c48ea2568414cdb0db`
- Reader: `reader/U06-companion.html` — SHA-256 `90e64e0b46b24a940a921cad0759e7c030e1dcf3812c5105bcf184423a7d556d`
- Automated QA receipt: `qa/U06-companion.json` — SHA-256 `1fbd67fecbdd90a58d0c0a412816bfdbf66f7d81ece38e7b8b355299e43fba61`
- Browser receipt: `qa/browser/U06-companion.json` — SHA-256 `a5c7879b78c1e3ddfa5fbc65206892eafa891c09b9cbc43900da5ac3abc67d57`; its `input_sha256` matches the reader above and it records isolated Chrome at `C:/Program Files/Google/Chrome/Application/chrome.exe`.
- Visual-review receipt: `qa/U06-visual-review.md` — SHA-256 `8c2e8891d742b745fea85a4fd1ff511213a3517440d8373d51054984ea55dd71`
- Frozen source `m81291.source.cnxml` — SHA-256 `729ab266737111c7cdd795ca6ddd887c41a9efcb2e802ab6ae46adfe3c13a195`
- Frozen source `m81293.source.cnxml` — SHA-256 `334b23102b7f15d4c4bac459a2f3798b66d408e14ad59daa2f3d9cfe274f52d4`

I read the complete Markdown, consultation record, reader HTML, automated and browser receipts, relevant frozen-source passages, all six overlapping desktop captures, and both narrow endpoint captures. I also read the existing OCR and actual page images for TR pp.57–58 and WB pp.226–227. The page-image hashes were TR57 `7e9e25e29ee2ab73f7306f2c114fb26f601085512a6cd4893b350dcf79e87e2d`, TR58 `246558790d2b90acaf4f266cc5da4a77fc85a82b5671903303337747adb53596`, WB226 `8cf202d0dd0cd90db4c75cd0679597d8bcded11d275470a6e9df60a5e5de7a66`, and WB227 `ce52122e599ab1e77d530449dd436ea3d07d3a769f3ea7a53df61783e4faf009`.

The final screenshot hashes matched `qa/U06-visual-review.md`: desktop tiles 1–6 were `3c347c1a48ada2fda0dc3765aaf546f85d97018d9f7ed584727134761f8a61d5`, `1ae4ae7801b2ff8b62592c3aaa9dc93c682c17367c49fa1ba81377fed5d95d23`, `e3fd36b3b67b3036c196b141a73eb923d89bc7d804b697eb43cae0b8aab38ffd`, `86291c06a1d8a4bb7e887f9fba6d9078503614f2fb4bd6fb1786fc888e425719`, `756be221181ff67cda4ea36d3954893c45d5adb5b8858cec796afc238630ff0d`, and `b9a6f165af1bc5e521cc073d9e1f534833a5a2239d813e46e9ae8ee1af5c7ca9`; narrow top/bottom were `7b8d5fc22a9e850225644145af0c374537b998da8aad946e8596aa855ca7a1a7` and `29d3a5a1a8918b2fe94aafaa56782776c36422db60627cb66c550d5c1bbb51a4`. I had already read the four final captures whose bytes did not change and re-read the four changed captures (desktop 2, 3, 6 and narrow bottom), so every capture in the final set has independent model coverage. The six desktop tiles provide a complete top-to-bottom read; the two narrow images support only endpoint/wrapping coverage, not a complete narrow sweep. The in-app browser runtime remained unavailable to this reviewer because its kernel assets could not be created, so I independently inspected the hash-bound captures and receipt but do not claim an independently executed second browser run.

## Resolution of prior findings

- **U06-MR1 resolved:** W3 now scopes the terminating-decimal criterion to a fraction after reduction and names prime factors `2` and/or `5`; the `3/6` counterexample is no longer misclassified.
- **U06-MR2 resolved:** W3 now accurately says that `3.0` has only zero to the right of the decimal point.
- **U06-MR3 resolved:** all three MathML displays retain their correct token structure and now have readable Bengali accessible labels. The fraction label separates numerator and denominator values, the equation label expands `x` as `এক্স`, and the money label has an explicit pause before equality. Real screen-reader validation remains pending.
- **U06-MR4 resolved:** L1 now says `“চার এবং নিরানব্বই সহস্রাংশ” বলেও পড়া যায়`, while retaining the explicit alternate/editorial qualification.
- **U06-MR5 resolved:** the footer now links both `modules/m81293.html` and `../canon/U06-consultations.json`. All nine local links resolve; the attribution target and repository license remain correct.

No open learner-facing finding remains. The consultation JSON's compact English audit tokens are unchanged; they are semantically unambiguous, machine-facing record typography and do not affect this closure.

## Mathematical and answer-key verification

| Item | Independently checked result | Status |
| --- | --- | --- |
| P1 | `4.099`; ones/tenths/hundredths/thousandths = `4,0,9,9` | pass |
| P2 | `375/1000 = 3/8` | pass |
| P3 | `0.460 > 0.406` | pass |
| P4 | `3.748 → 3.75` to the nearest hundredth | pass |
| P5 | `x = 1 − 3/5 = 2/5 = 0.4` | pass |
| P6 | `20.00 − 13.46 = 6.54` | pass |
| E1 | `10.023`; tenths digit `0` | pass |
| E2 | `625/1000 = 5/8` | pass |
| E3 | `−0.63 < −0.6` | pass |
| E4 | `6.995 → 7.00` under the explicitly stated source half-up rule | pass |
| E5 | `y = 3/4 = 0.75`; `0.75 − 0.25 = 0.50` | pass |
| E6 | `12.30 − 8.75 = 3.55`; inverse `8.75 + 3.55 = 12.30` | pass |

All seven worked examples also pass: W1 preserves internal zero place value; W2 gives `0.375 = 375/1000 = 3/8` and correctly distinguishes a trailing zero; W3's displayed conversions `1/4 = 25/100 = 0.25` and `3/8 = 375/1000 = 0.375` are correct, and its general criterion is now properly scoped to reduced form; W4 handles positive and negative ordering correctly; W5 gives `3.75` and carry to `7.00` under the stated convention; W6 checks the equation in fraction and decimal forms; W7's borrowing, subtraction, and inverse addition are correct. Money questions explicitly disclaim prices, exchange rates, tax, and fees, so no real-world claim is implied.

## Canon, source/editorial boundary, routing, and claims

- TR57 visibly supports decimal-fraction/place-value terms and the correct `0.456`, `123.478`, and `4567.021` rows. Its visibly displaced `12.74` row is correctly excluded and disclosed.
- TR58 visibly supports digit-by-digit decimal readings with internal zero and the `0.3` number-line example. The companion correctly does not extend that page's nonnegative comparison prose into an unqualified signed-number rule.
- WB226 visibly supports defining a solution by substitution (`x=4` makes both sides `24`); WB227 supports applying the same operation to both sides. The companion's equation language matches those witnesses without claiming that its exact examples occur there.
- The companion repeatedly and correctly labels itself a separate AX-3 adaptation, not a direct source translation. New negative comparison, `6.995` carry, and money examples are expressly editorial. Source-absent answers are not represented as source answers.
- Routing is qualitative and teacher-mediated; it claims neither validated score thresholds nor certification. `qa/U06-companion.json` reports only automated `pass` and separately keeps human and routing validation pending. `qa/U06-visual-review.md` confines `COMPLETE` to its stated model/browser scope and repeats the pending human/learner/AT limits. I found no certification or coverage overstatement.
- Case-insensitive searches of the translation, consultation record, reader, and QA receipt found no withdrawn `Top 10`, ranking, ranked, or Bengali ranking-language claim.

## Validation still pending

Independent West Bengal teacher/pedagogy review, independent Bengali language review, learner testing, keyboard and real screen-reader testing, broader assistive-technology review, and validation of routing decisions all remain pending. This report must not be presented as any of those validations.
