# MR-BRIDGE-011 — independent source and mathematics review

2026-08-31. Result: no source-content, mathematical, or source-identity defect found in the reviewed snapshot. This reviewer did not draft MR011 and made no XML/config changes. This is an agent review, not native-speaker or human mathematics-teacher approval. Browser/HTML layout and PDF review are outside this record.

## Reviewed snapshot and scope

Actually read the complete Marathi XML/config, all eight frozen EN/ID fragments, all selected paragraph/instruction/answer/table/accessibility-description content, and the full relation glossary meaning. Compared the frozen selections with their corresponding children in the actual complete pinned module bytes, read in memory from the existing archives. This was not a fresh whole-module semantic audit or a download/extraction.

| A20:m81373 selector | Content | Original IDs |
| --- | --- | ---: |
| fs-id1167836692527 | Five-pair relation, two question parts and supplied solution | 10 |
| fs-id1167836521479 | f at 3, −2 and a; complete supplied working | 26 |
| fs-id1167829859398 | g at h² and x+2, then g(x)+g(2); complete supplied working | 27 |
| fs-id1167833175472 | Relation definition and complete identified meaning | 2 |

All 65 original IDs occur once, in source order with their identified ancestry preserved. The target contains 67 IDs in total. Compared with the historical MR001 XML, 61 nested source identities are restored. There are three worked examples, one definition, three supplied solutions, no new practice questions and no newly authored source answers. New explanatory notes, captions/headers, navigation and table-layout changes are explicitly distinguished from source content.

All four selectors already occur in MR001: **zero new unique selections**. Historical MR001 remains SHA-256 `367314e8948ae28ba17de187ebca4e09d294e2c472a20c433538adb8dd06aac9`. Future assembly must select MR011's fuller representation for these four blocks, not concatenate both versions or add four to unique coverage. Its six other MR001 selections are not replaced by MR011.

Exact SHA-256 snapshot:

- XML, 24,755 bytes: `1a5a8cca15aa154ca15f24ec2708502cd1837f4a3714d9e781483d956e1573f1`.
- Config, 2,827 bytes: `8755902abf15d4729374d5a853f7d64a105a3040de2ebe3065899e1e3e94591c`.
- Frozen lock, 50,775 bytes: `844a94adf5fcb698ddda9b08745d52b5a208d9d4a65cabaf0e8ae639a3161c22`.
- EN `A20-canonical.zip` module `osbooks-prealgebra-bundle-38cae454e644abf9f0a623e876994553881597c9/modules/m81373/index.cnxml`: `2b606026c2b34cdf69acfa29bfe4b90abdb6961a322a78c7ec20107e0948b05c`.
- ID `A20-v0.3.0-source.zip` module `source/modules/m81373/index.cnxml`: `e9e593b31587995170c520b9175f2e0c0cb335282c951bb1d769f775344311ee`.

## Actual pixel and row inspection

Personally opened every one of the 56 existing original EN/ID image witnesses using filesystem image inspection: 015a–e, 016a–f, 017a–c, 018a–c, 019a–d and 020a–g in each language. The final recheck used seven bounded batches of eight images. Every formula/instruction was legible; ID redraws were displayed at reduced size. Neither alt text, an earlier receipt nor the writer's report substituted for reading the pixels.

The 28 canonical media consist of 26 equation images and two prose-instruction images. All 28 IDs now identify text transcriptions; the unit embeds no image assets. Checked each existing review-copy byte sequence against its exact ZIP member and frozen hash/size record. EN totals 752,063 bytes; ID totals 2,899,820 bytes. The lock and drafting notes retain the individual 56-file inventory; this report does not duplicate it. All 17 frozen witnesses were checked against their recorded bytes/hashes.

| Source table | Task | Preserved body rows |
| --- | --- | ---: |
| fs-id1167836507536 | f(3) | 5 |
| fs-id1167829740069 | f(−2) | 5 |
| fs-id1167836600305 | f(a) | 3 |
| fs-id1171790386499 | g(h²) | 3 |
| fs-id1171792580965 | g(x+2) | 4 |
| fs-id1167836606104 | g(x)+g(2) | 6 |

All 26 rows, row-associated media order, nonempty explanatory cells and intentionally blank explanatory cells survive. Collapsing the source's empty spacer columns to two meaningful columns loses no content and is disclosed as adaptation. Added table captions and headings are marked original.

Accepted fidelity details, checked against actual pixels and both source texts:

- EN017b retains `f(a)=2(a)²+3·a−1`; ID017b is already simplified. MR011 preserves the canonical intermediate and separate017c, and visibly records the locale difference.
- 016c preserves the whole parenthesized negative input under the square, and `3(−2)` without inventing a source multiplication dot.
- Both018b and018c contain `g(h²)=3h²−5`; only highlighting changes. The EN table description mentions simplification although its last explanatory cell is blank. MR011 preserves both rows and the blank cell, with an explicit note.
- 016a is the substitution instruction, and020a says to find the sum. Both are translated under their original media IDs.
- 020e's underbraces identify `3x−5` as `g(x)` and `1` as `g(2)`. Their meaning remains under the original ID; the separate unannotated020f row is also preserved.

## Mathematics and Marathi meaning

Independently recomputed the finite coordinate projections: the exact five source pairs give domain `{1,2,3,4,5}` and range `{1,4,9,16,25}`. No sixth pair or all-real domain is inferred from the square-number pattern. The complete glossary says any set of ordered pairs, not only a function.

For `f(x)=2x²+3x−1`, the three results are26,1 and `2a²+3a−1`. For `g(x)=3x−5`, they are `3h²−5`, `3x+1` and `3x−4`. All 30 displayed equalities passed an independent read-only exact-Fraction polynomial check, using the earlier unit10 interpreter rather than the unit11 suite's unit6 interpreter. The final difference `g(x+2)−(g(x)+g(2))` is the constant5, not a conclusion based on sampled inputs. The authored qualification correctly limits the inequality to this supplied g, not every function. All54 XML math keys match the config. Three original problem/solution pairs have working reciprocal anchors; all11 local targets exist.

Actually consulted relevant Marathi canon during this review and refreshed the applicable passages at final checking:

- C12/C13: existing OCR `downloads/mr-Deva-IN/canon/ocr/balbharati8-85.txt` opening explanation and `balbharati8-86.txt` successive-operation prose. The distinction between finding an equation's उकल and evaluating a known input supports the explicit note in the f example. Stepwise operation language supports retaining every instructional row. OCR-corrupted formulas were not mathematical evidence; no fresh PDF-page inspection is claimed.
- [C14 function uniqueness prose](https://marathivishwakosh.org/21979/): readable conditions and the two-output contrast guided the check that the relation glossary is not incorrectly narrowed to a function. Image-only formulas were not counted as read.
- [C19 opening definition/image-set paragraph](https://vishwakosh.marathi.gov.in/27548/): actual प्रांत, सहप्रांत and कक्षा prose guided the distinction between the values present and a possible codomain. Unrelated advanced statements were not adopted. मूल्यसंच remains openly provisional; this review does not promote प्रतिस्थापन, आदान or every working phrase to independently attested terminology.

No new shared terminology or source decision was needed. Root owns consolidation into the shared consultation/decision logs.

## Regression evidence and limits

The separate `tools/test_unit11_math.py` was written by MR011's drafting agent. I read its implementation and reran it: **19/19 pass**. It is credited as a drafting-author regression suite, not my independently authored test. Its exact SHA-256 is `3909f262ffcbe1dca789a91013e48b8e790dc4133d6a109f596292b657dd0196`; its accompanying drafting-author report is `qa/MR-BRIDGE-011-math-regression.md`. Run with `python -B mr-Deva-IN/tools/test_unit11_math.py` from the worktree root. It requires the existing ignored archives and56 review copies; it neither builds nor opens HTML.

My separate read-only checks also passed all eight fragment-to-module structural comparisons, 65 IDs/61 restored identities, row counts/media ordering, 56 exact image-copy comparisons, 17 witness pins, 54 config keys, 30 exact equalities, finite projections, constant difference5 and unchanged legacy scope/hash. A temporary inspection command initially encountered Windows stdout encoding, and an earlier reviewer query used an incorrect image-record field; corrected inspection commands passed without changing any product file.

Only this independent report was authored in this subtask. No browser operation or workaround, build, source edit, shared-tool edit, corpus download, commit or publication was performed. Reader-layout QA, assembly selection and native-speaker review remain separate obligations. No full-module, full-book or five-book completion is asserted.
