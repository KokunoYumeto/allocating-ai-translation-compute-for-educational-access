# M81244 tail independent source review

Date: 2026-09-01. Scope: independent source-only review of the four completed Tamil tail fragments and their author note. This report does not edit or approve any source fragment, SVG, reader, companion, package, or PDF. It is not native-speaker, learner, educator, accessibility, or production approval.

## Result

**PASS for source structure, identifiers, ordered source data, MathML, supplied arithmetic, omission preservation, section ordering, self-check meaning, and glossary definition semantics.** No mathematical or source-fidelity defect was found in the four reviewed CNXML files.

One bounded linguistic consistency issue remains for later editorial review: this addition module deliberately uses **கூடுதல்** for the result “sum,” while an earlier m81243 place-value table uses the plausible alternative **கூட்டுத்தொகை**. The current terminology ledger selects கூடுதல் and the current module uses it consistently. This is not a demonstrated error in the tail, but the eventual multi-module learner edition should either harmonize the alternatives or explicitly accept both after native Tamil review.

## Exact reviewed bytes

Pinned witnesses:

- `provenance/m81244.en.cnxml`: SHA-256 `b32058ce714e5fd43b010ccc81b2ae00a11567b229e9f96dda7b85b3cd82ba6b`.
- `provenance/m81244.id-ID.cnxml`: SHA-256 `d23343f302c34436169e88ffdbc4eab37baabf0a3d1134755b2f5676c75e1cc6`.

Tamil review inputs:

| File | Bytes | SHA-256 | Elements | IDs | MathML | Exercises | Solutions |
|---|---:|---|---:|---:|---:|---:|---:|
| `translation/m81244-fs-id2280700.cnxml` | 5,919 | `7d8abec4d0cc0ad191e124b94d935bf9b8d42ea283604f23f1b368f50f7df7ea` | 97 | 23 | 14 | 4 | 3 |
| `translation/m81244-fs-id1405751.cnxml` | 1,324 | `e4527c03e1c98627a713afde6d6d199e97f04fe33b28afac7020fc60fc3225b2` | 10 | 9 | 0 | 2 | 1 |
| `translation/m81244-eip-985.cnxml` | 2,740 | `ba06b9c41e5913ba2e26dae36bd6cc6bc9fd862c18d7e4ad862150f3509836f4` | 10 | 5 | 0 | 0 | 0 |
| `translation/m81244-glossary.cnxml` | 477 | `8d01abdc05c079b6f2752066bb699d7d89df015e653eb6afde4440730761e258` | 4 | 2 | 0 | 0 | 0 |
| **Combined** | **10,460** | — | **121** | **39** | **14** | **6** | **4** |

All 39 IDs are unique across the four fragments. Every root has `xml:lang="ta-Taml-IN"`. The reviewed author note is `qa/M81244-tail-translation-notes.md`, 9,161 bytes, SHA-256 `f24614b78be91677b0086d1ef299b1fcb7153b7bfb423e6616faba739d42a410`.

## Continual Tamil canon consultation at QA

This independent review reopened the actual OCR files for all 18 current locators, not merely `canon/README.md` or the terminology ledger:

- C01: page 005, இயற்கணிதம்.
- C02: page 007, கற்றல் நோக்கங்கள்.
- C03–C04: page 008, தொடரி / முன்னி.
- C05–C06: page 020, இடமதிப்பு / தீர்வு.
- C07: page 028, முதலில் and worked-step sequencing.
- C08–C10: page 035, இயல் எண்கள் / முழு எண்கள் / முடிவற்றவை.
- C11: page 036, கூட்டல், கூடுதல், மொத்தம், சமன்பாடு, and order-preserving addition language.
- C12: page 175, the bilingual glossary including குறியீடு, கூட்டல் சமனி, முழு எண்கள், and முழுக்கள்.
- C13–C14: pages 011–012, பிரிவுகள், எண்ணின் பெயர், விரிவாக்க வடிவம், and படித்துக்காட்டுதல்.
- C15–C16: pages 030–031, சுமார் / தோராயம் / உத்தேச மதிப்பு and முழுமையாக்குதல்.
- C17: page 038, zero as கூட்டல் சமனி.
- C18: page 046, everyday applications and the boundary-length / area distinction.

The complete page images for 007, 036, 038, 046, and 175 were opened after OCR. This resolved the relevant objective, addition/result, identity, application, and glossary wording. In particular, a high-resolution reread of page 036 visibly gives **அவற்றின் கூடுதலைப்** in the sentence that says changing addend order does not affect the result, while the operation is **கூட்டல்**. Therefore a proposed “correction” from கூடுதல் to கூட்டுத்தொகை would not be justified as a correction to the cited canon. The corpus search found no actual-canon occurrence of கூட்டுத்தொகை; it remains a plausible project-used alternative, not the wording attested by this passage.

The canon does not attest the tail's food names, personal-name transliterations, ராஞ்ச் சாஸ், ஷேக், சாண்ட்விச், அவுன்ஸ், பவுண்டு, or மின்தூக்கி. Those remain bounded provisional language choices. The canon is register evidence, not current-syllabus or native-approval evidence.

## Both-witness structural and token audit

For each Tamil fragment, an lxml preorder traversal was compared independently with the matching subtree in both pinned witnesses.

- Local element-name preorder is exact for all 121 elements.
- Ordered source IDs are exact; no ID was added, removed, changed, duplicated, or reordered.
- Stable attributes are exact except the expected Tamil root language, localized self-check `media@alt`, and repackaged self-check `image@src` / MIME type.
- Ordered visible ASCII digit sequences match both witnesses exactly.
- All 14 MathML roots have the same element/token preorder and attributes. Four unit `mtext` occurrences localize `16-ounce` / `12-oz` as `16-அவுன்ஸ்` / `12-அவுன்ஸ்`; two conjunction `mtext` nodes localize `and` as `மற்றும்`. Every `mn`, `mo`, comma, terminal period, and both `mspace width="0.2em"` nodes remain in source order.
- English self-check media is `image/jpg`; the Indonesian witness and Tamil derivative use `image/svg+xml`. This is the only MIME witness variant and does not change the source figure's meaning.

The separately owned Tamil SVG was not admitted or visually certified by this source-only review. The canonical English JPEG and Indonesian localized SVG were inspected directly to check the Tamil source alternative.

## Arithmetic and omissions

All source arithmetic was recomputed independently:

- `fs-id1606437`: `320 + 170 + 150 = 640`. The supplied Tamil answer 640 is correct.
- `fs-id1215287`: `420 + 230 + 580 = 1230`. Both witnesses omit a solution, and the Tamil source correctly preserves that omission; 1230 is a review key only and was not inserted.
- `fs-id1567863`: `82 + 91 + 75 + 88 + 70 = 406`; `406 >= 400`. The supplied “yes” answer is correct. Tamil **குறைந்தது 400** makes the threshold already implied by the source answer explicit without changing a datum.
- `fs-id1369108`: `210 + 145 + 183 + 230 + 159 + 164 = 1091`; `1091 < 1150` by 59. The supplied answer is correct.

The other preserved omission is writing exercise `fs-id1827602` / problem `fs-id1465007`, which has no solution in either witness. Writing exercise `fs-id1408863` asks two reflective response parts and retains the generic source solution **விடைகள் மாறுபடும்**; that is faithful but is not useful acceptance guidance.

Across the six exercises there are seven requested response parts: four everyday results/judgments and three writing reflections. The original source still lacks answers for the Fred total and the model-reflection exercise, and its generic writing answer supplies no reasoning. A later teacher-independent companion must label any completion as new material and provide the missing 1230 reasoning plus examples/acceptance guidance for all reflective parts.

## Outer wrapper and document end

Both witnesses have the same exact document structure:

- `content` ends with `section#fs-id2263283.section-exercises`.
- That outer section has **no direct title**.
- Its direct children, in order, are `fs-id2150139.practice-perfect`, `fs-id2280700.everyday`, `fs-id1405751.writing`, and `eip-985.self-check`.
- `eip-985` is the final child of the titleless outer section.
- A top-level glossary follows `content`; it is the final document child.
- The glossary has one definition, `fs-id1226736`, with term followed by meaning `fs-id1245763`; that meaning is the final named descendant.

Assembly must preserve this titleless wrapper and must not invent an outer heading.

## Self-check meaning and visual witness

The pinned English JPEG was opened at its actual 638 × 182 pixels. It is a four-column table: one “I can…” skill column and three confidence-choice columns. It has five skill rows and 15 blank response cells. The Indonesian SVG independently shows the same five rows and three choices.

The Tamil alternative names all four headings, all five skill sentences, and the three blank choices per row. It marks no choice and supplies no answer. The prose contains one pre-check paragraph and one post-check planning question, with source tokens ⓐ and ⓑ retained.

This instrument records five confidence selections plus one planning response. It is not five demonstrated-mastery questions, does not validate objective attainment, and cannot substitute for an executable diagnostic or mastery route. The Tamil wording **நீங்களே மதிப்பிட** appropriately frames it as self-estimation even though the source uses the term mastery / தேர்ச்சி.

## Glossary semantics and bounded terminology decision

The source definition says that a sum is the result of adding two or more numbers. Tamil preserves all three semantic components:

1. two or more numbers — **இரண்டு அல்லது அதற்கு மேற்பட்ட எண்கள்**;
2. the operation of adding — **கூட்டுவதால்**;
3. the resulting quantity — **கிடைக்கும் முடிவு கூடுதல்**.

Thus the definition does not confuse whole numbers with integers, reduce the scope to exactly two addends, or define the operation as its own result. The selected headword **கூடுதல்** is consistent with the current ledger and the visually resolved page-036 result usage. **கூட்டுத்தொகை** is also plausible and already appears in an earlier module, so final editorial harmonization and native review remain necessary; the present evidence does not justify silently changing this source fragment.

## Remaining limitations

- No native Tamil speaker has reviewed the loanwords, personal names, idiom, or the கூடுதல் / கூட்டுத்தொகை preference.
- The selected canon does not supply exact headwords for several food and measurement terms.
- The 16-ounce / 12-oz abbreviation distinction is normalized to the same Tamil unit word; quantity and source specificity are preserved, and the Indonesian witness's added “US fluid” detail is deliberately not imported.
- One numeric and one reflective source exercise remain unanswered; the generic reflective answer lacks criteria.
- The self-check is confidence-based rather than evidence-based mastery testing.
- This review does not certify the independently authored SVG, rendering, offline closure, keyboard/AT behavior, reader assembly, EPUB, PDF, or teacher-independent recovery routing.
- Completing these four source fragments does not complete m81244's learner workflow, A00, or the full A00–A20 / AX-1 / AX-3 assignment.

## Reproducible checks performed

- SHA-256 and byte-size checks with `Get-FileHash` / `Get-Item`.
- Full file reads of the four Tamil fragments, their author note, both exact witness tails, the current canon README/log, and all actual OCR pages named above.
- lxml parsing and preorder comparison of local names, IDs, stable attributes, ordered digit strings, MathML elements, `mn`, `mo`, `mtext`, and `mspace` attributes against each witness independently.
- Independent integer arithmetic for all four everyday problems and the capacity margin.
- Direct visual inspection of the English self-check JPEG, the Indonesian SVG source, five relevant canon page images, and a high-resolution page-036 crop used only as ignored review scratch.
- Direct document-parent/sibling inspection for the titleless outer section, child order, top-level glossary position, and final meaning node.

No reviewed source, asset, shared log, builder, or witness was changed.
