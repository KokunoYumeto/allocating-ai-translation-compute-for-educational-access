# MR-BRIDGE-006 independent mathematics/source review

Date: 2026-08-31. This is an independent agent review of the complete selected **Find the Value of a Function** group, not book/module/assignment completion or native-speaker/teacher approval. The reviewer owns only this note and `tools/test_unit6_math.py`; the parent owns provenance freezing, builds, browser review and shared records.

## Sources actually read

Read all 31 contiguous source blocks in both existing pinned A20 ZIP members, in memory without extraction. Selection begins `fs-id1167836714017`, ends `fs-id1167829749356`, and reaches the end of the parent Practice Makes Perfect section. It comprises five heading/instruction paragraphs and 26 exercises, with 13 supplied solutions and 13 omissions. Read the actual Marathi XML/config and drafting notes separately.

Source module SHA-256 pins checked:

- EN: `2b606026c2b34cdf69acfa29bfe4b90abdb6961a322a78c7ec20107e0948b05c`.
- ID: `e9e593b31587995170c520b9175f2e0c0cb335282c951bb1d769f775344311ee`.

The tests read the actual frozen fragments when available, validating their module pins, witness entries and byte hashes. Before freezing, the fallback reads only these two module members and checks the exact complete sibling run. Neither source locale contains an image in this group; no raster inspection or image asset is needed.

## Mathematics and source result

No mathematical or source-parity defect was found. Independently checked all 26 definitions, all **56 requested numeric/expression answer subparts**, the four application-variable identifications, and every displayed intermediate equality. The 107 XML mathematical check entries exactly match the config, but this string comparison is only an additional regression check: the answers and intermediate steps are independently recomputed from actual source MathML.

| Group | Coverage | Method |
|---|---:|---|
| Basic f evaluations | 24 subparts in 8 questions | Exact numerical substitution and polynomial coefficients for the symbolic input |
| Expression inputs to g | 18 subparts in 6 questions | Exact polynomial composition/addition for every displayed step |
| Single values | 8 questions | Signed-square arithmetic, numeric absolute values, and rational arithmetic |
| Applications | 6 numeric subparts plus 4 variable identifications | Exact decimal fractions; source units, roles and explanations |

The symbolic checks are coefficient identities, not finite-grid evidence for a universal claim. For each linear g, the difference between `g(x)+g(2)` and `g(x+2)` is its constant term; those terms are nonzero in all six source questions. The two requested expressions therefore remain distinct. Function-letter case and the original input parameters, including uppercase F/G and h's t/y variants, are preserved.

The eight single-value answers are, in order, 2, 27, 6, 24, 22, 12, 4 and 1/3. Negative inputs remain parenthesized before squaring. The absolute-value evaluations use magnitudes 9 and 5. Rational values retain exact fractions, with nonzero denominators at the requested inputs; the interpreter rejects the corresponding excluded inputs 1 and −2. The review does not add a new all-real-domain claim to either rational function.

Application values are 165 and 73 for the two count models, 1500/4750 for printing, and 2500/9750 for manufacturing. Decimal coefficients are interpreted exactly as 13/4 and 29/4, never binary floating-point approximations. Weekly and daily time units remain distinct; the printing model retains dollars, while no currency is invented for manufacturing, whose source does not specify one. The requested contextual inputs are nonnegative whole periods/items. No unrequested extrapolation to negative/fractional real-world counts is asserted.

## Source correction and preservation

The English printing-cost problem defines C, but its supplied answer incorrectly prints `N(0)` and `N(1000)`. The ID answer uses C. The draft keeps the original solution ID and the values, uses C in all answer/calculation fields, and explicitly records the English N-to-C correction in an original note. The tests inspect both original answer versions and permit only this declared symbol correction; the source error is not adopted as the mathematical answer.

All **119 original IDs** are present once and in source order, including original exercise/problem/solution paragraphs. All 26 question/answer pairs have nonempty forward/back anchors. The 13 supplied answers retain their original solution IDs and source-answer labels. The other 13 answers use separate original IDs and visibly state that the source did not supply an answer. Added work is distinguished from supplied answers. No new source question, omitted source image, or omitted outgoing source link was found.

## Actual canon use during independent QA

Read the existing C12 OCR prose for Balbharati printed p75 (physical p85), on an equation's solution and equal operations with nonzero divisors. This supports distinguishing finding a function value from finding an equation's उकल and checking equality chains. No unreliable OCR formula was used as the source mathematics; no new PDF acquisition, rendering or OCR is claimed here.

Direct reopening of C20 returned an error, but a fresh official-domain search returned the actual table row for absolute value. Read its `केवल मूल्य` and `चिन्ह निरपेक्ष मूल्य` wording, along with the nearby notation explanation. This supports the draft's absolute-value terminology and the preserved vertical bars; no advanced or missing image-only formula was imported. [Marathi Vishwakosh, गणितीय संकेतने, चिन्हे व संज्ञा](https://vishwakosh.marathi.gov.in/21279/).

The drafting notes separately document their C14–C17 readings. This review does not misstate those as its own fresh retrievals. The independent/dependent variable roles were additionally checked against the actual EN/ID application text.

## Run status and limits

Command: `python -B mr-Deva-IN/tools/test_unit6_math.py`.

Final frozen run: **all 18 tests passed** (14 actual-unit/source tests and four interpreter tests). All 62 frozen EN/ID fragments were read and checked against their byte hashes and witness entries; the final lock contains 71 witnesses. The mathematics, source preservation, all 107 check strings, and all navigation checks pass. The earlier pre-freeze run's sole missing-lock failure is resolved. This does not replace the separate reader/browser review.

Final reviewed snapshot, including the drafting worker's final prose revision:

- XML SHA-256: `ceb0b5d680fab0bf1b97c8668a77a13675a45d54ca25230f1f066eb3b2325fe9`.
- Config SHA-256: `d835ce92f4d9c68799a41e5a61a74d4484aed15092b817226dbe030870d980a4`.
- Provenance lock SHA-256: `985cf64f992885c0aadbba887a8dabf9a5f614f37bb16278853e1b855c408039`.

The stdlib interpreter uses a narrow AST whitelist and Fraction coefficient arithmetic; it never evaluates source code. Parser tests reject unsafe syntax, unsupported symbols, wrong function case, zero denominators and unsupported symbolic absolute-value calculations. It is a bounded regression interpreter, not a general computer algebra system. Browser rendering, accessibility, generic builder security and native-language review remain separate. No downloads, corpus copies, source/XML/config/shared-tool edits, deletions or commits were performed by this review.

## Primary integration addendum — 2026-08-31

The primary integrator inspected the existing phone applications screenshot and found that the final values 4750 and 9750 were split across lines inside their long calculation chains. Added exactly two `<br />` elements before the final simplifications; all text, source IDs and mathematics are unchanged. The primary reran this independent suite: all eighteen tests still pass. Current XML SHA-256 is `5538a28327ac72086ab4ab4d4054fe892ff78fb5a8864f1ada67871b93bc5fd0`; config and lock hashes above are unchanged. Rebuilt HTML SHA-256 is `523d085ccf293510648d983fee27517890f7efd41a0b7ec8794e5f634f358043`.

The old browser receipt remains untouched and belongs to HTML `14779ea08de90d1a42f38a3ed253015675e43699b37577a06ba99019aab76ad5`, not this revision. Following the explicit unit007 Browser URL-policy denial, no browser workaround or revised HTML visual check was attempted. Therefore this addendum records mathematical preservation only, not visual resolution. Separately authored PDF copies will carry separate format-specific QA.
