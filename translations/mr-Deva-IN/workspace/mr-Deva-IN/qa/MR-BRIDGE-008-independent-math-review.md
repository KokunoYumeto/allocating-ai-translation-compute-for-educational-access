# MR-BRIDGE-008 independent mathematics/source review

Date: 2026-08-31. This is a bounded independent agent review, not native-speaker/teacher approval or completion of the module, book or five-book assignment. This reviewer edits only `tools/test_unit8_math.py` and this report; source text, config, assets, shared tools and coordination records remain owned by the parent/drafting worker.

## Scope independently verified

Read the actual opening m81373 source in both pinned ZIP members, without extraction, and the Marathi XML/config. The 21 selected blocks comprise the abstract's introductory paragraph and three-objective list, three readiness notes, and the remaining first teaching-section children excluding example `fs-id1167836692527`, already translated in MR001. That earlier source selector was checked in the existing MR001 XML; it is not included or counted in MR008.

The selected blocks contain **101 original IDs**. The retained first-section context ID `fs-id1167829789538` makes **102 source-origin IDs in the target**, without making that enclosing section a 22nd selected block. The source contains two worked examples, nine practice exercises including readiness, two definition notes, six images, and eleven supplied solutions. The tests verify these counts from the actual structures rather than just trusting the config. All eleven original solution IDs and question/answer navigation pairs are preserved; no fully new answer or question is counted.

Checked module SHA-256 pins:

- EN: `2b606026c2b34cdf69acfa29bfe4b90abdb6961a322a78c7ec20107e0948b05c`.
- ID: `e9e593b31587995170c520b9175f2e0c0cb335282c951bb1d769f775344311ee`.

The loader prefers frozen fragments and verifies their witness entries and byte hashes. Before freezing, it reads only the two selected module members and verifies the opening/first-section selection, including the exclusion of the already translated example.

## Mathematical result

No mathematical or source-parity defect was found in the reviewed draft. All 35 config/data-check entries agree, but independent mathematical checks go beyond string equality:

- The three readiness results are −11, `2a² − a − 3`, and `3x + 4`. Exact substitution/coefficient arithmetic checks both source locales, the target answers, and the added numerical equality chain. The symbolic a is not replaced with an arbitrary sample. Source sentence punctuation occurs inside MathML, including final `<mn>5.</mn>`; the reader-side test normalizes only that terminal integer-point form without changing its exact value.
- The two explicit numeric relations and six diagram relations are compared with independent source/pixel readings. All **16 domain/range sets** are computed as coordinate projections, deduplicated, with every displayed relation pair retained.
- The graph readings include the point on the x-axis, repeated first coordinates, repeated second coordinates, and the lower-edge point `(−3, −6)`. Both graph axes span −6 to 6 in all three figures. Grid lines, intervening points, and all axis labels are not mistaken for the finite relation.
- Literal student-ID codes remain strings rather than numbers; birthday values retain their month/day identities across English, Indonesian and Marathi ordering. Names remain source example labels rather than replaced identities.

The three original readiness references retain source document `m81422`, their two distinct target IDs, and the corresponding OpenStax page fragments. The tests inspect those attributes and nonempty anchor text, not a live network page. The drafting worker separately reported checking the actual destination examples; that browser/network check is not attributed to this independent test.

## Direct pixel review and recorded discrepancies

Personally viewed **all twelve EN/ID rasters**, figures 001–006, and traced their arrows/coordinates. The six canonical EN reader images total 410644 bytes. The ID redraws are comparison witnesses, not replacement reader assets.

| Figure | Independent finding | EN SHA-256 |
|---|---|---|
| 001 | Liz maps to August 2, not July 24. The EN alt is wrong; pixels, supplied answer and ID agree. | `b7187d1cd61e336d2ad7368cbe2710471f1d75f733aca9eef3b9674776c483c8` |
| 002 | EN pixels say Khan Nguyen; EN/ID text and ID redraw say Khanh Nguyen. All four student-ID arrows agree. | `ce00276b81f2e4ec1deea697515ddfb257580f23859d8017fb0ea0c3f4d2c3be` |
| 003 | Five birthday arrows agree; Armando is the continuous spelling in both rasters. | `da8bcab15681b37fde889ec049a04824e64ccdd6eda9934646d9aadf70c1e566` |
| 004 | Six points, including both x = −3 points and both y = −2 points, agree. | `c65297a087d98e313dc944b8ab60c55d9748dbfd4a786168e92075d467d3b1d0` |
| 005 | Six points agree, including `(−1, 0)` and `(0, −1)`. | `dddc2892ca12cfb8e3001d6c90c81dd3508ad43b04f373d9263212d3bc42f64c` |
| 006 | Six points agree, including all three x = −3 points and the bottom-edge point. | `b743ed6e890e2f2b683f5b7bf242a6fc968b930ab4832706cceeab2bb1d180fc` |

The target explicitly records Liz's erroneous EN alt, the Khan/Khanh edition disagreement, and the EN broken spellings `Jose Hern and ez` and `Arm and o`. It follows the displayed canonical EN pixels, with original solution IDs retained. Source comparisons permit only these declared name substitutions. The script binds the visual interpretation to exact EN bytes, config hashes, provenance witnesses and preserved media IDs; it does not itself perform image OCR or infer pixels from alt text.

## Actual Marathi canon use during independent QA

Read C12's existing Balbharati OCR prose for printed p75/physical p85 on equation solutions and equal operations. It informed the readiness distinction between a known numerical substitution, a symbolic substitution and collecting terms. No unreliable OCR formula was used as the source expression; no new PDF download, OCR or page rendering was performed here.

Fresh official-domain search-reader text supplied C19's opening definition and actual-image-set paragraphs. The range/codomain distinction informed the projection checks and retention of the established working term मूल्यसंच; the witnessed synonym कक्षा is acknowledged rather than silently substituted. [Marathi Vishwakosh, फलन](https://vishwakosh.marathi.gov.in/27548/).

Fresh targeted retrieval also supplied C18's जात्याक्ष आलेख prose on horizontal/vertical axes, sign conventions and ordered coordinate construction. That guided the graph-alt checks and retention of x/y coordinate order. The entry's line-joining example belongs to its own context; it was not applied to these explicitly finite point sets. The working word निर्देशांक remains unchanged while the witnessed सहनिर्देशक variant is acknowledged. [Marathi Vishwakosh, आलेख](https://vishwakosh.marathi.gov.in/24316/).

No missing image-only canon formula was treated as read. These consultation effects are not a claim of native-language approval.

## Run status and limitations

Command: `python -B mr-Deva-IN/tools/test_unit8_math.py`.

Final frozen run: **all 14 tests pass**. All readiness, relation, source-answer, ID, reference-link and alt-content checks pass, as do the final source/asset pins. The lock contains 21 selections, 42 EN/ID fragments totalling 53020 bytes and 57 witnesses. All six canonical EN assets, totalling 410644 bytes, match their independent image hashes and provenance witnesses.

Reviewed final frozen snapshot:

- XML SHA-256: `418afc11f3b4c9c54176e4ddb0bab257ecc245101cc593b7904560c5d7eb4f66`.
- Config SHA-256: `a734fe117cc9fa3743bee7b0f5d1ec1e9afd23fdf22f8d4fe8d211fe2c011286`.
- Lock SHA-256: `929b4d789dec589e8c9263d4814e527eb9c6283d42ddb947838708b6197c7211`.

The suite imports the previously tested, non-executing exact-expression helpers from `test_unit6_math.py`; that file is not edited. It also reads MR001 only to check the prior-example exclusion. Relation parsing and projection checks are unit-local. These are bounded regression/source checks, not a general theorem prover. Reader rendering, accessibility, live external-link operation, generic builder security and native-speaker/teacher review remain separate responsibilities. No source files, images, configs or shared tools were changed; no downloads, bulk copies, deletion or commits were performed.
