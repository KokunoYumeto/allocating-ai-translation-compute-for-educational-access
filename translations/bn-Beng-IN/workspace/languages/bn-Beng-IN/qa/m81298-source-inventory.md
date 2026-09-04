# m81298 source inventory — Decimals and Fractions

Status: source-only production handoff for `bn-Beng-IN`; no translation overlay or canon consultation record is claimed here. Counts and order below were recomputed from the frozen CNXML, not copied from `NEXT.md` or `progress.json`.

## Canonical identity, pin and collection position

- Course/collection: A00, *Prealgebra 2e*, collection UUID `f0fa90be-fca8-43c9-9aad-715c0a2cee2b`.
- Collection witness: `provenance/A00/prealgebra-2e.collection.xml`, 5,043 bytes, SHA-256 `309fa072672372d1e46d52031167c21d9a120d1cdfdf3001548e1ca2975077a2`, Git blob `e81edc284a7ad911a21e381ae99d9aa8c62b4dcf` at pin `38cae454e644abf9f0a623e876994553881597c9`.
- Position: module 31 of 75 in the collection, and module 4 of 8 in the `Decimals` subcollection. The exact local sequence is `m81292 -> m81293 -> m81295 -> m81298 -> m81300 -> m81302 -> m81303 -> m81304`; there is no `m81294` in this collection.
- Module title/content ID/UUID: `Decimals and Fractions`; `m81298`; `69f66012-2d0d-4978-87c5-e6a4b16a8ec5`.
- Canonical input: `downloads/canonical-prealgebra/modules/m81298/index.cnxml`, exactly one matching `sources.lock.json` entry, 96,399 bytes, SHA-256 `a8105d6d162b071c7365bd74a48737cf4175ce1c7b14afbee4f3bcf472631d81`.
- Pinned Git identity: `38cae454e644abf9f0a623e876994553881597c9:modules/m81298/index.cnxml` is blob `3ea570bade6503f34824e6b720a221659dde547c`, size 96,399. `git hash-object` of the canonical input is the same blob.
- Frozen witness: `provenance/modules/m81298.source.cnxml`, byte-identical to that canonical input and independently rehashed to the same SHA-256. It was copied through the existing `build_sections.freeze_module()` pin/size/hash gate.
- Do not draft from similarly named mutable copies. `downloads/osbooks-prealgebra-bundle/modules/m81298/index.cnxml` is 97,883 bytes/SHA-256 `2c474fda9c60cb0145736d4efeb7d15692f51f9d6c887f418436806539fc64b6`; it is the same payload only after replacing its 1,484 CRLF line endings with LF, but it is not the pinned raw-byte witness. `downloads/openstax-prealgebra-2e-id-ID/modules/m81298/index.cnxml` is a different Indonesian work product, 100,283 bytes/SHA-256 `c4ec370cefad7d4112f399047007fcc96e46045cf01aa76a5bc57d5876e5c354`, and is not translation authority for this Bengali source overlay.
- Immediate source dependencies: all three empty-label readiness links resolve at the pin: `m81295#fs-id2262154`, `m81293#fs-id1778716`, and `m81293#fs-id2863926`. The module also has two valid local targets, four other cross-module links, and five `https://www.openstax.org/l/...` enrichment links that remain internet-dependent.

## Whole-source counts

The document has 3,521 XML elements including the `document` root (3,520 descendants), 687 IDs and 687 unique IDs, with no duplicates. It contains 328 top-level `<m:math>` expressions comprising 2,358 MathML-namespace elements, 10 image occurrences/10 unique files, 123 exercises/questions, 81 exercises with one supplied solution each, and 42 source-absent solutions. There are also 12 examples, 17 tables, 32 notes, 10 media alternatives, 2 ARIA labels and 15 table summaries.

The required block rows below contain 3,515 elements. The six remaining document elements are structural/provenance wrappers outside the learner-block overlay set: the `document`, `metadata`, metadata `content-id`, duplicate metadata title, metadata UUID and `content` wrapper. They add no ID, mathematics, image or exercise.

## Required learner-facing blocks

`Nodes` includes the block root. `Math` counts `<m:math>` expressions. `Supplied` means the exercise contains a source `<solution>`; `Absent` means it does not. File existence must not be used as a translated-status signal.

| Required ID | Role and source content | Nodes | IDs | Math | Images | Questions | Supplied | Absent |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| `__module_title__` | Learner title, “Decimals and Fractions” | 1 | 0 | 0 | 0 | 0 | 0 | 0 |
| `__abstract__` | Metadata abstract carrying all four learning objectives | 7 | 2 | 0 | 0 | 0 | 0 | 0 |
| `fs-id2173739` | Readiness: `0.24 / 8`; answer `0.03`; review link into m81295 | 20 | 7 | 2 | 0 | 1 | 1 | 0 |
| `fs-id2133739` | Readiness: compare `0.64` and `0.6`; answer `>`; review link into m81293 | 21 | 6 | 4 | 0 | 1 | 1 | 0 |
| `fs-id2173729` | Readiness: compare `-0.2` and `-0.1`; answer `<`; review link into m81293 | 21 | 6 | 4 | 0 | 1 | 1 | 0 |
| `fs-id2692103` | Lesson: convert fractions to decimals; nested repeating-decimal lesson | 479 | 95 | 57 | 6 | 12 | 12 | 0 |
| `fs-id1372950` | Lesson: order decimals and fractions, including signed values and ordered lists | 390 | 61 | 43 | 0 | 9 | 9 | 0 |
| `fs-id1739313` | Lesson: simplify decimal/fraction expressions using order of operations | 444 | 44 | 31 | 0 | 6 | 6 | 0 |
| `fs-id2218684` | Lesson: radius, diameter, circumference, area, exact/approximate pi and `22/7` | 793 | 90 | 83 | 2 | 9 | 9 | 0 |
| `fs-id1389226` | Key concepts: fraction-to-decimal rule and circle formulas/diagram | 40 | 3 | 6 | 1 | 0 | 0 | 0 |
| `fs-id2263562` | Section exercises, everyday math, writing and raster self-check | 1,285 | 364 | 98 | 1 | 84 | 42 | 42 |
| `__glossary_0__` | Four definitions: circumference, diameter, radius, repeating decimal | 14 | 9 | 0 | 0 | 0 | 0 | 0 |
| **Required-block total** | **12 blocks** | **3,515** | **687** | **328** | **10** | **123** | **81** | **42** |

### Objectives and terminal material

The abstract has four objectives: convert fractions to decimals; order decimals and fractions; simplify expressions using the order of operations; and find circle circumference and area. It is the only objective block; there is no separate prose abstract.

`fs-id1389226` is the source summary/key-concepts block. `fs-id2263562` contains four nested terminal groups:

| Nested group | Nodes | IDs | Math | Images | Questions | Supplied | Absent |
|---|---:|---:|---:|---:|---:|---:|---:|
| `fs-id2758024` / Practice Makes Perfect | 1,242 | 340 | 95 | 0 | 80 | 40 | 40 |
| `fs-id1960884` / Everyday Math | 22 | 9 | 3 | 0 | 2 | 1 | 1 |
| `fs-id2484061` / Writing Exercises | 10 | 9 | 0 | 0 | 2 | 1 | 1 |
| `eip-454` / Self Check | 10 | 5 | 0 | 1 | 0 | 0 | 0 |

The self-check still has two learner prompts around its English raster chart even though it has no `<exercise>` node. All 42 absent solutions occur in the terminal exercise block; none is to be invented silently. The structural supplied/absent classification is complete, but an independent answer-key review is still required before admission.

## Parallel production partition

The following boundaries are disjoint and suitable for concurrent overlays/canon receipts:

1. **Framing lane:** `__module_title__`, `__abstract__`, the three readiness notes, `fs-id1389226`, and `__glossary_0__` — 124 block elements, 16 math expressions, 1 image and 3/3 answered questions. This lane must not treat the key concepts as a substitute for any lesson.
2. **Fraction-to-decimal lane:** `fs-id2692103` — 479 nodes, 57 math expressions, 6 long-division/repetition images and 12/12 answered questions. It owns the repeating-decimal definition/table and the fraction-plus-decimal example.
3. **Ordering/operations lane:** `fs-id1372950` plus `fs-id1739313` — 834 nodes, 74 math expressions and 15/15 answered questions. Preserve the source’s signed-comparison direction and explain the operation order rather than inventing a Bengali mnemonic.
4. **Circle lane:** `fs-id2218684` — 793 nodes, 83 math expressions, 2 diagrams and 9/9 answered questions. It owns exact versus approximate pi, decimal `3.14`, fractional `22/7`, units and squared units.
5. **Exercise lane:** `fs-id2263562` — 1,285 nodes, 98 math expressions, the English self-check raster, 84 questions, 42 supplied solutions and 42 explicit absences.

Every lane needs its own before/during/pre-QA canon record, exact slot/XPath inventory, source-error dispositions and inverse structural/MathML gate. A later integrator must include all 12 required IDs exactly once.

## Frozen media and pixel inspection

The existing `build_sections.freeze_media()` gate copied and locked all 10 referenced files against the same pinned Git tree. Together they are 518,306 bytes. Each local byte count, SHA-256 and Git blob is recorded in `provenance/media.lock.json`; its commit remains `38cae454e644abf9f0a623e876994553881597c9`. All 10 entries were re-read after freezing and matched their lock fields and recomputed Git blob IDs.

| File | Owning media ID / block | Pixels and encoding | Direct pixel observation |
|---|---|---|---|
| `CNX_BMath_Figure_05_03_001_img.jpg` | `fs-id2702130` / convert | 51x26, CMYK JPEG | Initial `3 / 4` long-division layout (`4)3`) |
| `CNX_BMath_Figure_05_03_002_img.jpg` | `fs-id2140174` / convert | 51x122, CMYK JPEG | `3 / 4 = 0.75` long division |
| `CNX_BMath_Figure_05_03_003_img.jpg` | `fs-id2670259` / convert | 40x125, CMYK JPEG | `7 / 2 = 3.5` long division |
| `CNX_BMath_Figure_05_03_004_img.jpg` | `fs-id2820211` / convert | 70x198, CMYK JPEG | `4 / 3 = 1.333...`, ending with remainder 1 |
| `CNX_BMath_Figure_05_03_005_img.jpg` | `fs-id1790568` / convert | 485x269, CMYK JPEG | `43 / 22 = 1.95454...`; English/cyan/red annotations mark repeating 120/100 and quotient pattern |
| `CNX_BMath_Figure_05_03_011_img-01.png` | `eip-id1168468389277` / convert | 94x161, RGB PNG | `7 / 8 = 0.875` long division |
| `CNX_BMath_Figure_05_03_008.jpg` | `fs-id2762265` / circles | 212x212, CMYK JPEG | Circle with embedded English `Radius`, `Diameter`, `Circumference` |
| `CNX_BMath_Figure_05_03_010_img.jpg` | `fs-id2291411` / circles | 213x213, CMYK JPEG | Circle with `r, r, d`; center dot/diameter guide are teal/cyan, not red |
| `CNX_BMath_Figure_05_03_012_img.jpg` | `eip-id1170325412692` / key | 211x211, CMYK JPEG | Circle with `r, r, d`, blue guide and orange center dot |
| `CNX_BMath_Figure_AppB_030.jpg` | `fs-id1164271087726` / exercises | 666x172, CMYK JPEG | Entire self-check chart and confidence headings are embedded English text |

The first four long-division images are only 40–70 pixels wide. Preserve their bytes and inspect native-size plus narrow/high-zoom rendering; do not upscale/re-encode them as a hidden “fix.” The two `.jpg` files at media IDs `eip-id1170325412692` and `fs-id1164271087726` use source MIME `image/jpg` rather than standard `image/jpeg`, although their bytes are valid JPEG. All media have a source `media@alt`; the child `<image>` elements do not carry a second alt, which is the expected CNXML pattern here.

## Source errata and production risks

These are source observations, not permission to mutate frozen CNXML or pixels. Bengali overlays should preserve source mathematics/IDs/order and use explicit visible or accessibility warnings where meaning would otherwise be wrong.

| Kind | Exact source location | Evidence/risk | Required production disposition |
|---|---|---|---|
| Misleading mathematical prose | `fs-id1298092` | “the exact value of pi cannot be calculated since the decimal never ends or repeats” conflates an exact symbolic value with an unwritable complete decimal expansion. Nontermination/nonrepetition characterizes the decimal expansion; `pi` remains an exact value/symbol. | Translate the intended fact accurately and disclose the source wording issue; retain all source pi mathematics. Do not say merely that pi “cannot be calculated.” |
| Omitted domain condition | `fs-id2434715`; key list `eip-372` in `fs-id1389226` | The numerator/denominator division rule does not repeat that a denominator/divisor must be nonzero. | State the nonzero-denominator condition in Bengali without altering any expression. |
| MathML token-class fault | problem `fs-id1960093`, para `fs-id1960095` | In `2/5 ___ 0.25`, the number `0.25` is encoded as `<m:mo>` rather than `<m:mn>`. The visible comparison and supplied answer `>` are mathematically correct. | Preserve the pinned MathML structure under the source-faithful policy, record the semantic-token fault in the overlay, and test that rendering/accessibility still reads `0.25` as a number. |
| Stray punctuation in worked prose | solution `fs-id1509529`, table `eip-id1168467143703` | The circumference step literally says “and 10 for ,r.” | Omit the stray comma in natural Bengali and log the correction; preserve the adjacent `r` MathML and calculation. |
| Stray punctuation in supplied answer | solution `fs-id1302611`, para `fs-id1302613` | The radius-9-ft circumference answer is `56.52.ft.`. The numerical result `56.52 ft` is correct; the first period is spurious. | Render a correct Bengali/unit reading with a visible/source-error record; do not alter the question or value. |
| Noun mismatch and locale-sensitive money | problem `fs-id2202283`, para `fs-id2842885` | Kelly buys “boots,” but the final question asks for the price of the “shoes.” It also uses the historical/source amount `$84.99`. The supplied `$56.66` is exactly two thirds of the source price. | Use one consistent noun while logging the mismatch. Preserve the US-dollar example and amount; do not invent exchange rates or silently localize currency. |
| Repeating-decimal ARIA mismatch | table `fs-id2266631` | Body MathML has `4.1666...` and `0.271271271...`; the English ARIA says `4.166...` and omits the final ellipsis from the `0.271...` row. Its first sentence also reads “is ... is equal.” | Bengali ARIA must follow the actual table body, identify the repeating digit/block and overbar, and retain the ellipses. |
| Worked-table summary loses units | `eip-id1168467143703`, `eip-id1168466204784` | Summaries say radius 10/42.5 “units,” while the table body and problems use centimeters. | Translate summaries against the actual body and say centimeters. Do not rely on the English summaries as mathematical authority. |
| Alternative-text grammar/precision | media `fs-id1790568` | The English alt says “an ellipses” and gives a long positional description of the raster. Pixels and prose show recurring 120/100 remainders and repeating `54` in the quotient. | Write a concise Bengali mathematical description with `43 / 22`, `1.95454...`, recurring 120/100 and repeating `54`; preserve the English-labelled pixels. |
| Alternative/pixel color conflict | media `fs-id2291411` / `CNX_BMath_Figure_05_03_010_img.jpg` | Source alt says the center dot is red; direct pixel inspection shows a teal center dot with a cyan/teal diameter guide. | Avoid the false red claim. Describe position/relationships, or say a distinct color, while preserving pixels. |
| Under-described all-English self-check raster | figure `fs-id1164271087723`, media `fs-id1164271087726` | Source alt mentions skills/confidence generally, but the image contains every objective and the exact columns `Confidently`, `With some help`, `No-I don't get it!` in English pixels. | Supply a complete Bengali description/adjacent accessible checklist, including all objectives and response choices. Do not claim the original pixels were translated. |
| English raster labels | media `fs-id1790568`, `fs-id2762265`, `fs-id1164271087726` (and variable labels in `fs-id2291411`/`eip-id1170325412692`) | Essential labels/annotations remain inside source images. | Preserve pixels and carry their full meaning in Bengali alt/description. Verify the reader never depends on pixel text alone. |
| Unportable mnemonic | `fs-id1515935` | “Please excuse my dear Aunt Sally” is an English initial-letter mnemonic, not a Bengali canon witness. | Explain the actual operation order in Bengali. Do not transliterate it as if it worked, and do not invent a locally certified mnemonic. |
| Approximation boundary | `fs-id1459368` and circle examples | Both `3.14` and `22/7` are used as approximations to pi, while exact results elsewhere retain `pi`. Source uses `≈` correctly. | Preserve every exact/approximate distinction and unit/square-unit distinction. Do not turn `22/7` into an equality with pi. |
| Linguistic MathML workload | chiefly `fs-id2218684`, `fs-id1389226`, `fs-id2263562` | The source has 114 `<m:mtext>` nodes; 61 contain ASCII letters (30 unique values), including `radius`, `diameter`, explanatory sentences and English unit words. Variables/symbols such as `r`, `d`, `m` and pi must be distinguished from learner-language labels. | Inventory every linguistic `mtext` explicitly and use only the existing reversible `math_text` exception. Preserve numbers, operators, variable identity and MathML order exactly. |

No numerical value mismatch was found during this inventory’s source/pixel comparison of the displayed examples and supplied pairs beyond the punctuation/token/accessibility issues above. That observation is not a substitute for the independent 81-answer regression gate.

## Current Bengali canon relevance and targeted gaps

The actual current bank has 22 `examples.tsv` witnesses and 57 terminology entries. Its locked reference set contains 48 source-PDF/OCR/render artifacts plus the separately locked Bengali OCR model. The independent read-only findings are recorded in `qa/m81298-canon-scout.md`. Relevant current witnesses are:

- `TR01`–`TR04`: fraction, numerator/denominator, equivalence, simplest form and like-denominator comparison register.
- `TR06`: place `2/3` on a number line; useful for ordering instructions, not a signed-decimal rule.
- `TR08`: decimal number/fraction and place-value terminology; continue excluding its known bad `12.74` row.
- `TR09`: digit-by-digit decimal reading, retained zeros, `0.3` on a number line and a nonnegative decimal comparison context. It is not authority for arbitrary signed ordering.
- `TR05`, `WB04`–`WB07`: algebraic-expression/evaluation register; `WB07` directly evaluates an expression. None presently anchors a full order-of-operations rule.
- Ledger `T045`–`T050` cover decimal/place-value language; `T057` records long division as an editorial term without a direct local lexical witness. `T031` is only a fraction-circle model, not a geometry vocabulary witness.

Existing Bengali project output supplies consistency precedents but not new canon evidence: `translations/U06-companion.md` uses `পুনরাবৃত্ত দশমিক`, while m81289/m81295 output uses `গাণিতিক প্রক্রিয়ার ক্রম`/`ক্রিয়ার ক্রম`. Reuse may be editorially sensible, but consultation records must not present those internal choices as government-exemplar attestation.

The next topic exposes real gaps. Before drafting the owning lanes, use bounded targeted additions rather than pretending the current bank covers them:

1. **Fraction to decimal:** visually inspected SCERT Tripura VI PDF p.59 is a strong candidate, with direct headings for decimal-to-fraction and fraction-to-decimal and examples `17/10=1.7`, `1234/100=12.34`, `3002/1000=3.002`, `5/2=2.5`, `3/8=0.375`. It is not yet a current exemplar: render/OCR it, check the page image, add a narrow ledger entry and lock the new artifacts first.
2. **Circle vocabulary:** the same already acquired PDF p.73 witnesses `পরিমিতি`, `পরিসীমা`, the statement that a circle’s perimeter is called `পরিধি`, `ক্ষেত্রফল`, and `বর্গ একক`. Page 92 witnesses `বৃত্ত`, `কেন্দ্র`, `ব্যাসার্ধ`, `পরিধি`, `ব্যাস`, and the relation diameter = twice radius. Page 92’s preceding diameter-definition sentence is awkward/ambiguous, so use only its lexical register and explicitly clear relation; OpenStax remains the mathematical authority. These pages are also candidates, not locked current page artifacts.
3. **Operation order:** the already rendered/OCR-locked Tripura p.9 contains a visually inspected bracket passage that could become a zero-new-page-artifact targeted exemplar, but it is not currently an `examples.tsv` anchor. Verify the exact passage and scope before recording it. It witnesses doing the work inside parentheses first, not the full exponent/multiplication/division/addition/subtraction hierarchy.
4. **Repeating decimal and pi:** no current witness or inspected candidate directly supports repeating digit/block/overbar terminology or the pi cluster. Do a bounded search. If none is found, mark the Bengali terms editorial and request West Bengal review rather than inventing a consultation.

The candidate source PDF is already locked as `SCERT-Tripura-VI.pdf`, SHA-256 `7f5370c2377bb10837af920ce94370ee2c662d3f230401b0a6a95c7a58c3d9d2`; p.59/p.73/p.92 themselves have not yet been OCR/render-locked. Canon witnesses guide Bengali register only; they do not override OpenStax mathematics or authorize copying government prose.

## Admission boundary

This handoff freezes inputs and partitions work only. Production must still create one overlay and one honest recurring canon receipt for each of the 12 required IDs, translate all 10 media alternatives, 2 ARIA labels, 15 summaries, learner-facing links, 61 alphabetic `mtext` occurrences as applicable, and all supplied solution prose. It must retain the 42 explicit source absences, preserve all 687 IDs and 328 math expressions under the reversible linguistic-`mtext` rule, record the errata above, build the complete module, and run answer, asset, browser/narrow, inverse-structure and independent model-review gates. Human West Bengal language/teacher, learner and assistive-technology review remain pending.
