# MR-BRIDGE-012 — independent source and mathematics review

2026-08-31. Result: **19/19 tests pass**. The reviewing agent did not draft MR012. This pass found no additional source/math defect requiring a translation change. It independently confirms the draft's disclosed source-alt and backlink corrections.

This is source, mathematics and source-pixel review, not visual acceptance of an HTML/PDF reader, human/native-speaker approval, publication approval or a whole-module completion claim. No browser, HTML reader or PDF was opened. The full five-book assignment and all uncompleted workflow obligations remain active.

## Reviewed snapshot and reproduction

| File | Bytes | SHA-256 |
| --- | ---: | --- |
| translations/MR-BRIDGE-012.xml | 33878 | `1883fddbb24d1d3518e6d34ebdec38c608ebcee78872af069dc7030f6920402b` |
| units/MR-BRIDGE-012.json | 3486 | `cb9c08d87b32ca61cfc2a59b3638700197666c3375a91a343e51c32516263454` |
| provenance/MR-BRIDGE-012.lock.json | 56317 | `c85ef3350201e4364853f25718a6d18f7029c248047b92ddd03252f7386029b6` |
| tools/test_unit12_math.py | — | `0e280f3c7e23b059d0d94c982c40ce3aa87423a530f76041573a8ab1ec5a8a39` |

Run from the worktree root:

```powershell
python -B mr-Deva-IN/tools/test_unit12_math.py
```

Latest run:19 tests,19 passes. The suite uses only the standard library, including the existing narrow Fraction/AST arithmetic interpreter in `test_unit6_math.py`; it does not execute source expressions with `eval`. Sharing that interpreter is an implementation limitation, not a claim of a second independent arithmetic engine. The square-root helper uses integer square-root verification and the nonnegative-root convention, without floating-point approximation.

## Actual source reading and scope

Read the complete current translation and config. Read all36 frozen EN/ID fragments, including all prose, MathML, objectives, readiness instructions, source solutions, definition text, media attributes and reference targets. Any initially truncated combined output was reread in bounded form before relying on it. The tests compare every fragment with the actual complete selected element from each pinned module, including attributes and text; only indentation whitespace is ignored in this structural comparison. Their individual hashes are freshly checked, and a separately fixed inventory digest binds the36 source pins:

`0dcf0a4c8aafa871a4af37ce29b77f9f3a206951928f4b165a09783eb75154da` = SHA-256 of sorted UTF-8 `target_id|locale|fragment_sha256` lines, including final LF.

Actually read the m81374 metadata, first-section title/children and succeeding section boundary from the original archive members:

- EN `A20-canonical.zip`, `osbooks-prealgebra-bundle-38cae454e644abf9f0a623e876994553881597c9/modules/m81374/index.cnxml`,247327bytes, SHA-256 `021c29fa9a6ab3d5b06d2ef143a82d2ac818ed25fe6fd44ebf5d7a6be07a123a`.
- ID `A20-v0.3.0-source.zip`, `source/modules/m81374/index.cnxml`,247303bytes, SHA-256 `d89a74aef766afca6a4ac7e1ae720f120d22cc771c11dd7e025c55bca1fabb8e`.
- Both metadata records identify m81374 with UUID `4b2bbf1b-2df7-4b9a-9933-dd70d1fd8ada`.

The18 ordered selectors comprise the objective paragraph/list, all three readiness notes and all13 non-title children of first teaching section `fs-id1167836579284`. The complete original section heading survives in its uncounted wrapper. There are57 IDs within the selected blocks, plus that wrapper =58 retained original IDs; there are61 target IDs altogether. Every original ID retains its relative order and source-identity ancestry. The section wrapper is not separately counted as another selected block.

Classification is one worked example, one definition and five source practice items (three readiness and two Try Its), with no new practice question. Six original problem/solution containers hold12 subparts: six readiness evaluations and six graph judgments. All supplied answers and their forward/return links survive; source answers are distinguished from newly added reasoning. The remaining selected material is metadata, eight teaching paragraphs and the standalone source figure.

All three module objectives remain translated, but the scope note explicitly limits this unit to the first objective. The18 selectors do not overlap those in units001–011. Last selected block `fs-id1167836537878` completes this first teaching section. The next safe production marker is **A20:m81374#fs-id1167836522816**, “Identify Graphs of Basic Functions.” Later m81374 sections are not covered, and this result does not resolve m81373 assembly/readiness obligations.

## Source-pixel and coordinate checks

Opened all12 original source-image paths with filesystem image inspection, in three batches containing paired EN/ID images001–006. The two versions of each image are byte-identical; thus there are six distinct pixel images, not12 distinct drawings. Their content was actually read, not inferred from alt descriptions. The suite freshly compares all12 original ZIP members, existing review-copy bytes, frozen records and six committed canonical assets. Source archives were not downloaded or fully extracted.

| Suffix in CNX_IntAlg_Figure_03_06_SUFFIX_img_new.jpg | Bytes per locale | SHA-256, EN and ID |
| --- | ---: | --- |
| 001 | 120547 | `de8ad8b7a7c2fed56a79b196866575e70a0e54b2ca70520342ce9081d92e3467` |
| 002 | 91065 | `50b51fdbccf8bbcc32fd4ce26bc0b255ae76e365026d772980f115506bf3486b` |
| 003 | 84283 | `109cdaa78c4bd812e17c70f304673faf5f36590ad133afc956c859f3f586eda8` |
| 004 | 66942 | `e0ec3c2945b43a91e675c6631f14c076dc7cac0c4927c14e1372414e5cd09b99` |
| 005 | 91655 | `9ccbba7c423566ea6c7a5ded367b840b81f3f799ba4634610d5d7a1910b1794e` |
| 006 | 72667 | `af4e418454ff1d2ce11c63566bba63c562db3e81fe6145b1af2d52af83d2660e` |

Six canonical embedded assets total527159bytes. All51 frozen witnesses pass their current byte checks. No image was changed.

Figure001 shows `y=2x−3` with table rows `(−2,−7),(−1,−5),(0,−3),(3,3),(4,5)`. All five rows independently satisfy the equation. The new three-column table preserves its title, headers and five rows; the surrounding explanation correctly distinguishes that sample table from the whole line and from the plot viewport. The additional alt points `(0,−3),(1,−1),(2,1)` also lie on the line.

The source plots independently confirm these corrections already visible in MR012:

- 002(a) and003 have axis marks−6 through6, not the EN/ID alts'−10 through10.
- 004's rightmost dashed vertical is atx=2. The EN alt contradicts itself by ending withx=3; the ID alt and both original rasters show2. The other dashed lines atx=−2 andx=−1 have zero and one intersection respectively. MR012 correctly avoids inventing exact y-coordinates for thex=2 intersections.
- 006(b) also has axis marks−6 through6, not the EN/ID alts'−12 through12.

Every numerical pair in all six Marathi alts matches the independently read source coordinates. Hashes and regression constants bind these observations to exact bytes; they do not perform automated image recognition.

## Independent mathematical reasoning

Readiness answers are `(8,9)`, `(7,3)`, `(2,4)`. The tests verify the actual source questions and supplied answers as well as the target, all eight added working/square-check strings, and all38 target/config math strings. In particular√4 and√16 denote the nonnegative roots2 and4, not the two-valued solutions of equations such asx²=4. Absolute values are correctly nonnegative distances from0.

| Source graph pair | Judgments | Reason |
| --- | --- | --- |
| Worked example002(a,b) | yes, no | Nonvertical line; right-opening parabola has `(0,1)` and `(0,−1)` |
| Try It005(a,b) | yes, no | Upward vertical-axis parabola; circle has `(0,2)` and `(0,−2)` |
| Try It006(a,b) | no, yes | Ellipse has `(0,3)` and `(0,−3)`; nonvertical line |

For each negative case, two actually present points sharex=0 and have distinct y-values. One such pair is sufficient; no universal claim is inferred from a finite grid.

For positive cases, the source explicitly identifies straight lines and an upward-opening parabola, and the source pixels confirm their orientation. A nonvertical straight line has formy=mx+b and therefore exactly one y for every realx. The observed descending and ascending line coordinates give slopes−2/3 and1, confirming they are not vertical. This conclusion uses their source-declared straight-line geometry, not an assumption that any curve through three points must be a line. An upward parabola with vertical axis has formy=a(x−h)²+k, a>0, and thus a unique y for eachx by its form. Checking the five observed points againstx²−1 is recorded only as coordinate consistency, not a proof that finite samples determine the full graph or permission to add that equation to the translation.

Similarly a right-opening parabola has formx=h+a(y−k)² witha>0: vertical intersections number zero, one or two whenx is below, equal to or aboveh. The pictured vertex has h=−1, supporting the three dashed-line intersection statements without estimating irrational coordinates.

The definition and explanation retain **every** vertical line and **at most one** intersection. The added domain clarification correctly allows zero intersections outside the graph's actual domain, while requiring an output at each member of a separately prescribed domain. It defines vertical as parallel to the y-axis, allows the same y-value at differentx-values, distinguishes the horizontal-line test, and warns against using a few sample vertical lines as a universal proof. These are important conceptual checks, not merely exact string equality.

## Four original references and other links

All four original reference occurrences retain exact targets: three readiness references and the same-document figure001 reference. The actual referenced module metadata and problem MathML were read in both pinned archives:

- `m81422#fs-id1167829586631`: operation-order example `5+2³+3[6−3(4−2)]`, value13. It is a relevant powers/operations review target.
- `m81423#fs-id1167835365552`: integer-addition questions `−1+(−4)`, `−1+5`, `1+(−5)`, not absolute-value questions. MR012 preserves the original reference and explicitly discloses this source mismatch while providing the needed absolute-value explanation locally.
- `m81425#fs-id1167833056590`: square roots√25,√121 and−√144, values5,11,−12. It is a relevant square-root review target.
- `CNX_IntAlg_Figure_03_06_001`: local target exists with its original media ID and figure/table content.

The suite pins all six referenced-module byte hashes and checks metadata UUIDs, exact target IDs and the chosen HTTPS route strings. It does not perform live navigation or claim the external pages work offline. All18 local anchors resolve; eight HTTPS source/credit/canon links remain explicit. The current footer uses the parent's corrected CC BY-NC-SA4.0 reference; the earlier incorrect footer is historical. This check did not reopen a general supply/license audit.

## Canon actually consulted during this independent review

- [C18, आलेख](https://vishwakosh.marathi.gov.in/24316/): direct open returned502; a fresh targeted official-domain search supplied the actual जात्याक्ष/axis-construction paragraphs. Read their horizontal/vertical directions, sign conventions, y-parallel construction and सहनिर्देशक wording. This supported checking the vertical-line orientation and coordinate interpretation; its separate interpolation/curve-fitting discussion was not treated as proof of these specific curves.
- [C14 and adjacent function/domain prose](https://marathivishwakosh.org/21979/): fresh search-reader text supplied the unique-output definition and प्रांत/सहप्रांत distinction. These guided the review of “at most one” versus a prescribed domain. QuickLaTeX image formulas were unavailable as text and are not claimed read.
- [C20, गणितीय संकेतने, चिन्हे व संज्ञा](https://vishwakosh.marathi.gov.in/21279/): actually reread the vertical-bar row giving केवल मूल्य and चिन्ह निरपेक्ष मूल्य. This confirms the target's chosen absolute-value name; unrelated notation was not imported.
- [Candidate21277, गणितीय प्रतिरूपे](https://vishwakosh.marathi.gov.in/21277/): actually read the शंकुच्छेद paragraph pairing अन्वस्त with पॅराबोला and विवृत्त with लंबवर्तुळ. The target's original shape-name aid is supported. This reference does not attest the entire phrase “उभ्या रेषेची कसोटी”; that phrase remains explicitly an authored classroom formulation. Global C21/terminology registration is root-owned, not performed here.

These were actual readable prose consultations, not assertions based on the drafting notes. No newly unread PDF formula was used, and no new canon download/OCR was necessary for this pass. No native-language reviewer is implied by these references.

## Limits and next obligations

The suite requires the actual unit/frozen witnesses, the existing ignored archives and the12 existing review-image copies; it reads only the named module/image members and small witnesses. It does not copy corpora, hash entire archives, extract, download, build, inspect HTML/PDF, edit shared ledgers or commit. Only this report and `test_unit12_math.py` were authored by this worker.

Exact byte/data-check equality is a regression safeguard, not independent proof of every Marathi wording choice. Pixel reading and geometric identification remain agent review bound to hashes; no automatic image-to-equation proof is asserted. Future source or XML changes require a conscious review/pin update. Root-owned reader QA, integration and remaining book production continue. Test success alone must not change HTML/PDF format-readiness status.
