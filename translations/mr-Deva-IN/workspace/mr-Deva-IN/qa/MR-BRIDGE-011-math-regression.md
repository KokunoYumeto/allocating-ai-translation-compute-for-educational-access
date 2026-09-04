# MR-BRIDGE-011 — drafting-author mathematics and preservation regressions

2026-08-31. Result: **19/19 tests pass** against the current frozen source/XML/config and exact original image bytes. No new arithmetic or source-transcription defect was found in this pass.

Reviewer role: the agent that drafted MR011 also wrote these tests and performed this review. This is a **drafting-author regression review, not writer-independent approval**. The separately assigned independent source review is a different record. No browser, HTML reader, PDF, native-speaker or human mathematics-teacher approval is claimed here. The entire five-book assignment and its supporting workflow remain in progress.

## Scope and exact reviewed files

MR011 supplies fuller replacement representations of four previously selected MR001 blocks. Its own config reports four selections, but its contribution to unique source coverage is **zero**. It does not complete the module. Prospective assembly must choose this representation for those four blocks rather than concatenate both versions. Legacy001 and its six other selections remain unchanged.

| Canonical-order selector in A20:m81373 | Complete content | Original IDs |
| --- | --- | ---: |
| fs-id1167836692527 | Five-pair relation; domain and range question and supplied solution | 10 |
| fs-id1167836521479 | f(x)=2x²+3x−1 at 3, −2 and a; all worked rows | 26 |
| fs-id1167829859398 | g(x)=3x−5 at h² and x+2; g(x)+g(2); all worked rows and comparison | 27 |
| fs-id1167833175472 | Relation glossary and complete identified meaning | 2 |

Snapshot SHA-256 values:

- `translations/MR-BRIDGE-011.xml` — 24755 bytes, `1a5a8cca15aa154ca15f24ec2708502cd1837f4a3714d9e781483d956e1573f1`.
- `units/MR-BRIDGE-011.json` — 2827 bytes, `8755902abf15d4729374d5a853f7d64a105a3040de2ebe3065899e1e3e94591c`.
- `provenance/MR-BRIDGE-011.lock.json` — 50775 bytes, `844a94adf5fcb698ddda9b08745d52b5a208d9d4a65cabaf0e8ae639a3161c22`.
- `tools/test_unit11_math.py` — `3909f262ffcbe1dca789a91013e48b8e790dc4133d6a109f596292b657dd0196`.
- Historical `translations/MR-BRIDGE-001.xml` remains `367314e8948ae28ba17de187ebca4e09d294e2c472a20c433538adb8dd06aac9`. This review did not read its HTML or rebuild either reader.

## Source and pixel evidence actually read

Read all eight frozen EN/ID fragments, including every semantic paragraph, question subpart, supplied solution, table-row entry, table accessibility description, MathML formula, media identity, final comparison and glossary meaning. The tests compare the complete fragment element/attribute/text/child structure with the actual selected module children; only indentation whitespace is normalized in that structural comparison. Fragment byte hashes are independently fixed in the test, not accepted merely because the mutable lock names them.

Both exact source modules were read in memory from the already-acquired archives; no whole-archive extraction or new download occurred:

- EN `A20-canonical.zip`, member `osbooks-prealgebra-bundle-38cae454e644abf9f0a623e876994553881597c9/modules/m81373/index.cnxml`, module SHA-256 `2b606026c2b34cdf69acfa29bfe4b90abdb6961a322a78c7ec20107e0948b05c`.
- ID `A20-v0.3.0-source.zip`, member `source/modules/m81373/index.cnxml`, module SHA-256 `e9e593b31587995170c520b9175f2e0c0cb335282c951bb1d769f775344311ee`.

Personally re-opened all 56 original review images using filesystem image inspection during this regression pass: paired EN/ID 015a–e, 016a–f, 017a–c, 018a–c, 019a–d and 020a–g. Final successful inspections were seven bounded batches of eight images; an earlier oversized batch was truncated and was not counted as complete inspection. The canonical English equation images were legible; larger Indonesian redraws were displayed at reduced size but every formula and instruction was readable. No source alt text or historical review claim substituted for reading these pixels.

The test checks every original ZIP member, its frozen source-image record and its existing review-copy bytes. There are 28 EN images totaling 752063 bytes and 28 ID images totaling 2899820 bytes. The sorted UTF-8 inventory `locale|basename|sha256|bytes`, one line each plus final LF, has fixed SHA-256 `70bbc45bfeaf09eb6f39d2b51c54009b073a0fca09c2a88a22efaa08751b9fb4`. Thus all 56 individual pins are bound, even though the test avoids duplicating the long pin table already present in `qa/MR-BRIDGE-011-drafting-notes.md` and `provenance/MR-BRIDGE-011.lock.json`. No source image is embedded by this unit; all 28 media IDs identify accessible text transcriptions.

## Mathematical and preservation findings

The six requested function values are exactly:

| Request | Result |
| --- | --- |
| f(3) | 26 |
| f(−2) | 1 |
| f(a) | 2a²+3a−1 |
| g(h²) | 3h²−5 |
| g(x+2) | 3x+1 |
| g(x)+g(2) | 3x−4 |

The relation is precisely `{(1,1),(2,4),(3,9),(4,16),(5,25)}`. Projection of all five pairs gives domain `{1,2,3,4,5}` and range `{1,4,9,16,25}`. The authored note correctly prevents silently extending this finite relation because of its square-number pattern. The glossary retains “any set of ordered pairs,” all first-coordinate values as domain, and all second-coordinate values as range; it is not narrowed into the definition of a function.

Every one of the 30 displayed equalities holds using exact Fraction arithmetic and symbolic polynomial coefficient expansion through the existing narrow, non-evaluating AST interpreter in `test_unit6_math.py`. The comparison has the constant polynomial difference `g(x+2)−(g(x)+g(2))=5`, so its inequality holds for every real x under this supplied polynomial rule. This is an algebraic coefficient argument, not an inference from a finite grid. The target correctly avoids claiming the inequality for every possible function.

The six source tables retain 26 body rows, in counts `5,5,3,3,4,6`. All row-associated media IDs remain in their original row and order; all nonempty explanatory cells have translated counterparts. Only empty spacer columns are collapsed into the disclosed two-column adaptation. Original captions/headers added by the workflow are visibly marked as new writing.

Specific fidelity checks retained:

- English017b has the unsimplified `2(a)²+3·a−1`; the ID redraw is already `2a²+3a−1`. Both are equivalent, but MR011 correctly preserves the canonical intermediate and separately retains017c. The difference is disclosed.
- English016c uses `3(−2)` and the exponent applies to the whole parenthesized negative input. The transcription retains it; the result is1, not the value obtained by losing parentheses.
- Both018b and018c read `g(h²)=3h²−5`, with only the substitution highlight changing. The canonical aria description mentions simplification where the visible final prose cell is blank. Both equations and the blank cell remain, with a separate disclosure.
- Image016a is the instruction to substitute−2 forx, not decoration. Image020a instructs the reader to findg(x)+g(2). Both are translated under their original media IDs.
- Image020e's underbraces identify3x−5 asg(x) and1 asg(2). Both annotation meanings are preserved under the media ID. The following unannotated020f row is not merged away.

All65 original IDs occur exactly once in canonical relative order and preserve their source-identity ancestry, including61 identities absent from the pilot adaptations. The target has67 total IDs. All three supplied solutions remain supplied, with original exercise/problem/solution nesting and actual forward/return anchors. There are11 valid local links and3 external credit/canon links; the selected source blocks themselves contain no outgoing source links. No original practice item or new source answer has been added.

## Canon consultation at this review stage

Actually reread C12/C13's existing OCR (`balbharati8-85.txt`, SHA-256 `f9bf9c42edb3e126573bc14f4671aa5c062920ee145c50590fdac6733af52a9b`; `balbharati8-86.txt`, `497332d70fb096c86e468261e37186b888099b86830234a26d5c86253188ee57`). Used the reliable prose about an equation's उकल and explicit successive operations to check that the supplementary explanation distinguishes evaluating a known input from solving an equation, and that no intermediate instruction was condensed away. OCR-corrupted formulas were not used as mathematical authority or imported into this unit. The original page pixels were inspected during drafting, as recorded in the drafting notes; no new page-pixel inspection is claimed in this pass.

A fresh official-domain search-reader consultation of [C19, फलन](https://vishwakosh.marathi.gov.in/27548/) supplied readable prose distinguishing प्रांत, सहप्रांत and the set of actual images called कक्षा. Its concrete effect was to verify that the glossary/domain-range explanation names the actually present coordinate values, not an arbitrary codomain. The unit honestly retains provisional मूल्यसंच and notes कक्षा as a witnessed alternative. Image-only formulas and unrelated advanced statements in the entry were not used. No shared canon ledger was edited by this bounded reviewer; root owns consolidation.

## Reproduction and limits

Run from the worktree root:

```powershell
python -B mr-Deva-IN/tools/test_unit11_math.py
```

Latest run:19 tests,19 passes. An initial harness run failed on the source's colon included inside the first MathML block; the harness was corrected to strip terminal prose punctuation. No XML or mathematical content was changed to make the tests pass.

The suite requires the committed unit files, frozen witnesses, ignored pinned archives and the56 already-created review copies. It reads only the named module/image members and small witnesses. It does not hash entire archives, download, extract, build, open HTML, or write files. Archive digest metadata is checked against fixed known pins; selected member contents are freshly hashed. Source/config byte changes intentionally require an explicit review-pin update. Exact text/config agreement and literal pixel transcriptions are regression guards, not independent proof of translation quality. The interpreter is shared with prior suites, so these are not wholly independent mathematical implementations. Source-byte equality cannot automate a Marathi linguistic assessment.

Remaining workflow obligations include the separate independent source review, root-owned integration/coverage assembly and genuinely format-specific reader review. Test success must not promote MR011 to HTML/PDF-ready status. No publication or full-module/book completion is asserted.
