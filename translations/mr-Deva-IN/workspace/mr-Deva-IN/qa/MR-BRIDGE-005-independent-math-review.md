# MR-BRIDGE-005 independent mathematics/source review

Scope: the complete 12-exercise **Determine if a Relation is a Function** group in A20:m81373, beginning `fs-id1167836513559` and ending with `fs-id1167833212947`, before `fs-id1167836714017`. This is a checkpoint within the active five-book assignment, not module/book/assignment completion.

The independent reviewer read the actual Marathi XML/config, all 16 selected blocks in both pinned ZIP members in memory, the drafting notes, and all eight EN/ID rasters 209–212. No corpus download/extraction, source modification, image editing, build, browser operation or commit was performed by this review. Only the independent test and this report are owned here.

## Mathematical result

No mathematical or mapping error was found in the reviewed draft. The four pair relations and four pixel-read mappings give these function judgments, in question order: **yes, no, yes, yes, yes, yes, no, yes**. All 16 requested finite domain/range sets agree with exact coordinate projections, without duplicates or invented inputs. Question 3's positive outputs at negative inputs are preserved; it is not silently changed into question 4's cube relation.

Question 2 has the valid same-input witness `9 → −3` and `9 → 3`. In question 7, Jenny has the distinct outputs `JKim@gmail.com` and `jenny@aol.com`; Raul also has two. The absolute-value and square mappings remain functions despite repeated outputs. Finite relation patterns are not extended to all real inputs.

For equations, the tested interpretation is real variables, with **y as a function of x**, matching the visible original scope note. The 12 judgments are:

| Question | (a) | (b) | (c) | Witness for the no-answer |
|---|---|---|---|---|
| 9 | yes | yes | no | x = −6, y = 1 and −1 |
| 10 | yes | yes | no | x = 0, y = 2 and −2 |
| 11 | yes | no | yes | x = 2, y = 1 and −1 |
| 12 | yes | yes | no | x = 4, y = 1 and −1 |

The eight yes-answers have the exact form `c·y + p(x) = 0`, with a nonzero constant c and a polynomial p. Thus `y = −p(x)/c` exists uniquely for every real x. Tests check this coefficient identity and every displayed rearrangement using `Fraction`; they do not infer a universal result from finite samples. In particular, 12(b) gives `y = x² + 4`, and 12(a)'s two displayed forms both give `x/2 − 2`.

Each no-answer substitutes the same input and two distinct real outputs into the source-equivalent equation. The displayed numerical equalities are checked for truth and for the actual substituted expression tree. An unrelated true equality would not satisfy that check. No negative output branch is discarded to force uniqueness.

## Source fidelity and pixels

The selected 16 blocks contain **56 original IDs** in each source locale. The tests compare their complete ordered list and original problem/solution containment against the actual target, including all four media IDs. All 12 question/answer pairs have nonempty forward/back anchors. Six odd-numbered answers preserve the supplied solution IDs; the six even-numbered answers are visibly authored additions, not new source questions.

Two supplied-answer corrections are transparent and mathematically justified:

- Question 3: EN has `0, 1, 8, 27}` without its opening brace; ID has the complete set. The target restores only that brace and labels the correction.
- Question 7: EN answer contains `R and y`, `RHern and ez@state.edu`, `DBroen@aol.com`, `jenny@aol.cvom`, and `R and y@gmail.com`. Canonical pixels and ID supply the corrected strings. The target's correction note retains all five erroneous readings explicitly; the corrected answer retains the source solution ID. Tests permit only these declared substitutions when comparing the original answer.

All arrows were personally traced in both raster editions. Figures 209/210 map −3 through 3 to absolute values/squares. Figure 211 has seven arrows, including Jenny's and Raul's double outputs; all are preserved in the Marathi alt. Figure 212 has seven one-output mappings. The canonical EN raster spells `rachel@state.edu` with lowercase r, unlike both source alts and the ID redraw. The target follows the EN pixels and records the case choice. The EN Matt label has a typographic space after @; the caption now explicitly records its normalization to `mattg@gmail.com`. The addresses remain literal example labels, not contact links.

The tests pin the four directly read EN raster hashes below and require matching config entries, on-disk bytes, MIME, preserved media figures, and provenance witnesses. ID hashes record the separately viewed comparison copies; ID images are not reader assets.

| Figure | EN SHA-256 | ID comparison SHA-256 |
|---|---|---|
| 209 | `2c4708d126a4b2973f8d66f6bbcee026342764f917a1a911d47f5498521ffa08` | `1aa4dc4069e1cb7aef0e52f07622ef9f175fedc21a70b25caf12d42d55c19dc6` |
| 210 | `2ca4bbd57f42b6014a93278db4f373b36f4c8d83daf79f21fa22f414a7e5ff69` | `9b189ee9307ff2c615fdb567d4a74609395a694ab8ca35f1936508b867eb70eb` |
| 211 | `580ca185896cb8c30325548d4cacb9fc058c14b36b45d9faf2703f1026d7b6e9` | `2b37ef257a0399d3c659f08c9bd0769c5771dd7cf2db58a89ef8dfd62fc28bfc` |
| 212 | `899112b8cfcff1d6049555fcccac5d6d4a1a293f431ae44caf7246b59e36e172` | `8381f42858196422ed75f9c6740ccadb95174f062a918a84f543f8eb3d3c33dc` |

The source module SHA-256 pins checked in both in-memory reads are EN `2b606026c2b34cdf69acfa29bfe4b90abdb6961a322a78c7ec20107e0948b05c` and ID `e9e593b31587995170c520b9175f2e0c0cb335282c951bb1d769f775344311ee`. The regression loader prefers final frozen fragments and validates their witness hashes; before freezing it reads only the two selected module members, checking the complete group boundary.

## Actual canon consultation during independent QA

Read the existing C12 OCR prose for Balbharati printed p75 (physical p85), specifically solution-as-equality and equal operations on both sides with nonzero divisors. That supports the operation-by-operation review of the new rearrangements. No unreliable OCR formula was used as the equation source, and no new PDF read/OCR is claimed.

Fresh search-reader retrieval supplied C19's actual opening paragraphs on exactly-one correspondence, domain/codomain, actual-image set, and the square-function example. This guided the distinction between repeated outputs and repeated inputs with different outputs, and between finite range and codomain. The established working term मूल्यसंच is retained; the witness also records कक्षा. [Marathi Vishwakosh, फलन](https://vishwakosh.marathi.gov.in/27548/).

The drafting agent's final terminology change to केवल मूल्य and its direct 21279 reading are documented in the drafting notes. This independent review's direct reopen of that page returned HTTP 502, so it does not claim a successful independent reading of that additional witness. It does not affect the already verified numeric mapping. No claim of reading missing image-only canon formulas is made.

## Regression run and limitations

Command: `python -B mr-Deva-IN/tools/test_unit5_math.py`.

Final post-freeze run: **all 16 tests passed** (13 real-unit/source tests and three parser/arithmetic tests). The run read and hash-checked all 32 frozen EN/ID fragments and all four EN assets, totaling 280431 image bytes. The final lock has 45 witnesses. All actual mathematics, source answers, 61 data-check entries, 56 source IDs, and navigation checks passed. An earlier pre-freeze run had 15 passes and one expected missing-lock/asset failure; that pending condition is now resolved. This result does not claim that browser rendering or the whole assignment has passed QA.

Final reviewed text/config/provenance snapshot:

- XML SHA-256: `b4480901a99322492c49481acd4b6c5edc3e587d2be0e9afe7c66ebc08e85ca3`.
- Config SHA-256: `0cfe1486492c410912cb2dd0f6980d37c0a04f042dfe3c08fba78228cd75b54b`.
- Provenance lock SHA-256 after the metadata-only normalization: `97455194a3e3256bb34bdf401faaf024fc48a92fa92052278ed497821006d2f1`.

2026-08-31 primary-agent addendum: the original independent review used lock `52ad3828ecfef44b2aec0eb1573d53d56cc65ada3bab3ad81bd9b36feab94a59`. D046's master-lock LF normalization required a metadata-only refreeze. The primary agent reran this complete 16-test suite successfully against the new lock. XML, config, all original fragments/assets and the HTML remain unchanged. This addendum does not turn the primary rerun into a new independent review or alter what the original reviewer actually read.

The tests use a narrow non-executing AST whitelist and exact arithmetic, with parser rejection checks. They are unit-specific regression and source-consistency checks, not a general symbolic theorem prover. Pixel interpretations are fixed human-readable reviewer observations bound to hashes; the script does not itself perform image OCR. Browser layout/interaction, generic builder security, source acquisition, Marathi-native/teacher review and final assignment integration remain separate responsibilities.
