# MR-BRIDGE-010 independent mathematics/source review

2026-08-31; independent reviewer freeze_regressions. Owned only `tools/test_unit10_math.py` and this report. This is bounded agent review, not native-speaker/teacher approval, layout acceptance, publication or completion of a module, book or the five-book assignment. The writer retained the XML; root inserted canonical assets and froze provenance. No XML/config/shared-tool edits, browser actions, downloads, extraction, image edits, build, rendering or commits were performed by this reviewer.

## Evidence actually inspected

Read the complete stable Marathi XML/config and drafting note. Independently read the selected EN and ID CNXML blocks and the enclosing section structure from the pinned ZIP members in memory. Truncated output portions were explicitly reread, including the final EN symbolic-input Try Its with powers preserved, and the corresponding Marathi practice paragraphs. The suite rereads the actual selected module/image members rather than treating the drafting report as the source.

Module members:

- EN: `A20-canonical.zip`, `osbooks-prealgebra-bundle-38cae454e644abf9f0a623e876994553881597c9/modules/m81373/index.cnxml`; SHA-256 `2b606026c2b34cdf69acfa29bfe4b90abdb6961a322a78c7ec20107e0948b05c`.
- ID: `A20-v0.3.0-source.zip`, `source/modules/m81373/index.cnxml`; SHA-256 `e9e593b31587995170c520b9175f2e0c0cb335282c951bb1d769f775344311ee`.

The tests check the actual module hashes and selected ZIP-member CRCs. The frozen records are compared with the known archive/module pins; root's freezer separately verifies complete archive SHA-256. This test does not reread and hash the entire archives.

Personally viewed all 12 existing EN/ID source rasters with the permitted filesystem image viewer: `CNX_IntAlg_Figure_03_05_013a_img.jpg` through `013c`, and `014a` through `014c`, both locales, in `downloads/mr-Deva-IN/source-image-qa/MR-BRIDGE-010`. The suite's twelve exact hash pins bind those actual pixels to the checked alt text and calculation steps; hashing is not described as image reading or OCR. Canonical EN totals 98,154 bytes, ID comparison copies 516,763 bytes, combined 614,917 bytes. ID images are comparison witnesses, not reader-asset replacements.

For relevant Marathi evidence, read the existing BB8 physical-page-34 OCR and then personally inspected its PNG (printed p24), including the C06/C09 mixed-sign and grouped-operation examples. The same ongoing production sequence had already personally read the C12/C13 physical-page-85/86 prose and images; those operation/solution distinctions informed the present check without another unrelated corpus read. Read the actual retrieved C14–C17 [Marathi Vishwakosh function prose](https://marathivishwakosh.org/21979/) in this review sequence: dependence, one resulting output per permitted input, domain/codomain naming, the person/task many-to-one example and the constant-function paragraph. No unavailable image-only QuickLaTeX formula is claimed read.

Concrete effects on review: checked the complete negative argument before squaring, distinguished evaluating a symbolic expression from solving an equation, checked that an allowed input is restricted by its domain, and ensured dependence is not described as requiring a changed output every time. The Marathi notation and independent/dependent-variable wording is consistent with the pilot choices. This is not certification that every classroom term is directly witnessed or native-speaker approved.

## Exact boundary and source completeness

Both pinned sources' section `fs-id1167824731607`, “Find the Value of a Function,” has 24 direct non-title blocks and 141 IDs including the section. The new unit selects exactly the 18 remaining direct blocks, in original order, after excluding six complete blocks already selected by MR001/MR002. The exact ordered IDs are independently encoded in the suite and checked against both source trees and the frozen selections.

The excluded block IDs are `fs-id1167836521479`, `fs-id1167829859398` (001), and `fs-id1167833158753`, `fs-id1167833369424`, `fs-id1167836481611`, `fs-id1167833128952` (002). Their original selectors are checked in those prior units; neither their wrapper nor descendant IDs occur in 010. No new selector overlaps another unit.

There are 53 selected original IDs nested under the correct translated wrapper, plus the uncounted original section wrapper: 54 preserved source IDs and 59 unique XML IDs in total. The classification is four Try Its, two definitions, two introductory calculation tables and ten prose blocks. There are zero newly selected formal worked examples, zero authored questions/answers and no selected resource note. Treating the two calculation tables as formal source examples would inflate the declared count; the draft does not do so.

All four original exercise/problem/solution structures and all 12 answer subparts are present. All four supplied solutions retain the original source solution IDs, “स्रोतातील उत्तर” labels and bidirectional question/answer links. Thirteen same-document anchors resolve. The selected source blocks have no source link elements; the only source link in the entire section is in the already-covered excluded MR002 note. The new XML's two HTTPS links are license/canon references. The existing lack of direct offline cross-unit reader navigation is disclosed in the credits; this review does not repair or waive that integration limitation.

## Independent calculation results

All twelve supplied answers agree with exact substitution into the actual source formulas:

| Try It | Source function and arguments | Verified results |
|---|---|---|
| 1 | `f(x)=3x²−2x+1`; `3`, `−1`, `t` | `22`; `6`; `3t²−2t+1` |
| 2 | `f(x)=2x²+4x−3`; `2`, `−3`, `h` | `13`; `3`; `2h²+4h−3` |
| 3 | `g(x)=4x−7`; `g(m²)`, `g(x−3)`, `g(x)−g(3)` | `4m²−7`; `4x−19`; `4x−12` |
| 4 | `h(x)=2x+1`; `h(k²)`, `h(x+1)`, `h(x)+h(1)` | `2k²+1`; `2x+3`; `2x+4` |

The suite serializes the source MathML without flattening superscripts, binds each question's own function, and composes exact coefficient polynomials using `Fraction`. It compares the resulting polynomial with each actual draft answer. This is an algebraic identity check, not finite-grid sampling, nor merely a comparison between a config string and its duplicate in XML. The additional syntax/config comparisons protect all 46 declared `data-check` expressions against source drift.

Dedicated regressions distinguish `g(x−3)` from `g(x)−g(3)`, `h(x+1)` from `h(x)+h(1)`, and `g(m²)` from `g(m)²`. The helper has negative controls for incorrect negative-input grouping and rejects unsupported execution, attribute/subscript access, division and negative powers. These are a narrowly scoped polynomial checker, not a general computer-algebra parser.

The six personally read equation strips show, in order, `y=4x−5`, `y=4·2−5`, `y=3`; and `f(x)=4x−5`, `f(2)=4·2−5`, `f(2)=3`. Both three-row tables preserve input 2 and every original media ID. Recomputing every right-hand step gives 3. Alt text correctly describes the evaluated outcome, not a new constant function.

## Source corrections independently confirmed

- EN Try It 2(a) answer `fs-id1167836732807` lacks `f`, displaying `(2)=13`; ID has `f(2)=13`. The question and independent calculation establish 13. The draft restores the missing letter with a visible original note and keeps the answer source-supplied rather than calling it newly authored.
- EN 013b alt contains garbled `4 ×7 2 ×1 5`; both actual rasters show `y=4·2−5`. The corrected Marathi alt and nearby disclosure match the pixels.
- Both EN/ID 013c alt descriptions invoke a horizontal line. The source table is evaluating at input 2, so the actual Marathi note explicitly says this does not mean the original function has value 3 for all x. That distinction is correct.
- EN 014b highlights only the substituted right-hand 2 in red, whereas ID highlights both occurrences of 2. The draft's canonical-EN alt says “उजव्या बाजूला” and does not import the ID color description. The mathematics agrees.
- The original bridge claiming the preceding example used a constant input is qualified because the previously selected MR001 example also has `f(a)`. The draft preserves the bridge and labels its qualification original; it neither duplicates the prior example nor silently rewrites its scope.

No additional mathematical/source discrepancy requiring an XML change was found. These confirmations were sent directly to the drafting worker. The source files themselves are unchanged.

## Frozen verification and result

After root inserted the six canonical asset records and froze the unit, reran `python -B mr-Deva-IN/tools/test_unit10_math.py`: **18 tests passed; zero skips or failures**. The freeze-dependent test is no longer pending. It validates all 18 selectors, semantic identity of the 36 frozen EN/ID fragments against actual ZIP source nodes, every one of 51 local witness hashes/byte counts, six exact canonical asset byte strings and all 12 source-image records. The six committed assets total 98,154 bytes; ID records have no `committed_asset` field.

Reviewed stable-file identities after freezing:

| File | Bytes | SHA-256 |
|---|---:|---|
| `translations/MR-BRIDGE-010.xml` | 26373 | `be72aae0b5e00768349c0b289ee229ec4d82d38a43de656cefc520fab32568f4` |
| `units/MR-BRIDGE-010.json` | 3624 | `5c62d54b33ab86264139ddbb069e4bfcc8b2741d16a534f3736bd081162531c9` |
| `provenance/MR-BRIDGE-010.lock.json` | 61580 | `03ddbadda5d951f683dfca3f44da84210948bcedccada8b2514b7e385368a2d5` |
| `tools/test_unit10_math.py` | 29097 | `d79a006ee68864be6d6e55541834f549936e54275e2565704caa00fe79f9ce6a` |

No mathematical/source-content issue remains from this bounded review. Build/reader layout and readability, the existing cross-unit navigation limitation, human Marathi review, publication and final acceptance remain outside this result. No browser was used or retried; the previously issued Browser URL security denial remains in force. Root owns the build and any permitted visual QA. This review hands back the complete bounded scope, not a claim that the overall assignment is complete.

## Primary regression-maintenance addendum — 2026-08-31

After the intentional full-source replacement draft011 was added, root's rerun passed 17 of 18 tests: the prior-unit exclusion test globbed future configs and overwrote legacy001 ownership with011. This was a test-scope defect, not changed mathematics or an unintended overlap in010. Root limited that historical baseline to units001–009 and retained a list of owners instead of silently overwriting duplicate selectors. The repaired suite passed all eighteen tests. XML/config/lock above remain unchanged. Current test-file SHA-256 is `275bdff0d181b4bc88993e81430cd816cb10e79e68cb04ebc0272287710d3b7f`; the earlier test-file hash is the independent review's historical snapshot, not silently replaced evidence.
