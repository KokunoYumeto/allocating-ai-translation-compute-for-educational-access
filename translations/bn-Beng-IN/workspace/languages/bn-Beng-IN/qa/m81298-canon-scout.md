# m81298 canon scout — bn-Beng-IN

Date: 2026-09-01. Scope: read-only pre-translation audit. No translation, canon ledger, consultation log, source-lock, commit or publication change was made here.

## Authoritative source read

`sources.lock.json` pins `downloads/canonical-prealgebra/modules/m81298/index.cnxml`, title **Decimals and Fractions**, 96,399 bytes, SHA-256 `a8105d6d162b071c7365bd74a48737cf4175ce1c7b14afbee4f3bcf472631d81`. I read that complete file. The authority/logbook copy has the same byte count and hash. Do not draft from the different bundle copy (97,883 bytes, `2c474fda…`) or the mutable Indonesian module copy (100,283 bytes, `c4ec370c…`).

The source has 12 required progress blocks. Its mathematical progression is:

| Source block | Actual mathematical topics |
|---|---|
| `fs-id2173739`, `fs-id2133739`, `fs-id2173729` | Decimal division readiness; positive and negative decimal comparison. |
| `fs-id2692103` | Fraction bar as division; fraction-to-decimal conversion, including negative and improper fractions; adding a fraction and decimal after converting forms. Nested `fs-id1633681` introduces a repeating decimal, ellipsis, overbar, repeating digit/block, and examples whose nonrepeating prefix must stay outside the overbar. |
| `fs-id1372950` | Compare/order decimals and fractions by converting the fraction; signed comparisons; least-to-greatest lists; number-line direction. |
| `fs-id1739313` | Order of operations with decimals/fractions: parentheses, exponents, multiplication/division, addition/subtraction, and converting a decimal to a fraction inside a calculation. The English mnemonic is source-specific, not a Bengali canon witness. |
| `fs-id2218684` | Circle, centre, radius, diameter, circumference, area, `C=2πr=πd`, `A=πr²`, exact answers in terms of `π`, approximations with `π≈3.14`, linear versus square units. Nested `fs-id2741610` uses `22/7` as an approximation when the radius is fractional. |
| `fs-id1389226`, `fs-id2263562`, glossary | Key concepts; practice/mixed practice; circle applications; US-dollar and mosaic contexts; writing/self-check. Glossary terms are repeating decimal, radius, diameter and circumference. |

## Actual current bank/ledger snapshot

At audit time `canon/examples.tsv` has **22** rows (11 West Bengal + 11 explicitly supplementary Tripura), SHA-256 `0e7fe9c3c65386deb3e14f76be4e39989dd89650650c1cac822db6bef4a8f03a`. `terminology.tsv` has **57**, not merely 52, term rows (`T001`–`T057`), SHA-256 `a989ec8030754e3c8b48f1271fa8204c6435654aeb9b8358703f9262e8565ff1`.

I read the relevant OCR and opened the corresponding actual page images for Tripura pp.9, 51, 52, 57, 58 and West Bengal p.191. The following support is real:

| m81298 need | Current entries that suffice | Boundary that must remain explicit |
|---|---|---|
| Fraction/numerator/denominator, equivalent or simplest forms | `TR01`–`TR03`; `T001`–`T006`, `T023`–`T030` | No current exemplar directly shows fraction-to-decimal conversion. `T054` dividend and `T057` long division are already editorial, not locally witnessed. |
| Decimal naming, point, place-value digits and retained zeroes | `TR08`, `TR09`; `T045`–`T050`, `T052`, `T055`, `T056` | Exclude Tripura p.57's misaligned `12.74` row. These entries do not witness repeating decimals or overbar scope. |
| Positive ordering/register and number-line wording | `TR04`, `TR06`, `TR09`; `T032` | `TR09` is nonnegative. Signed fraction-versus-decimal comparison remains source-governed/editorial; do not cite it as a local worked witness. |
| Expression evaluation and grouping register | `WB07` (p.191) plus `WB04`–`WB06`/`TR05`; `T013`, `T016`, `T038`, `T039`, `T053` | `WB07` demonstrates powers/substitution/evaluation but does not name the order of operations. Existing output already uses `গাণিতিক প্রক্রিয়ার ক্রম`/`ক্রিয়ার ক্রম`; that is an internal editorial precedent, not a ledger witness. |
| Approximation vocabulary | `TR11`; `T051` | It witnesses `অনুমান`/`আসন্ন মান` only. It does not witness `π`, `≈`, exact-versus-approximate language, or a decimal tie rule. The actual p.9 says `4117→4100/4000`; OCR's `40900` is wrong. |
| General circle geometry | None. `T031` is specifically a **fraction circle** model and is not a substitute. | The bank and ledger currently lack circle/centre/radius/diameter/circumference/area/π/square-unit terminology. |

Exact unsupported terms/topics to resolve or mark editorial are: **repeating decimal**, repeating digit, repeating block, overbar/repetition line; the formal **order of operations** name and the English mnemonic; general circle, centre, radius, diameter, circumference, area, square unit; pi; exact value, approximate value and the `≈` relation. `translations/U06-companion.md` already contains the editorial wording `পুনরাবৃত্ত দশমিক`, and m81289/m81295 output already contains `গাণিতিক প্রক্রিয়ার ক্রম`/`ক্রিয়ার ক্রম`; reuse can preserve internal consistency, but neither wording may be represented as current government-exemplar evidence.

## Smallest targeted candidates already acquired

All candidates below are in the already acquired official SCERT Tripura Class VI PDF, 2,242,448 bytes, SHA-256 `7f5370c2377bb10837af920ce94370ee2c662d3f230401b0a6a95c7a58c3d9d2`. They remain **visual-only candidates** in this audit: no new OCR, page artifact, hash-lock or `examples.tsv` row was created.

1. **Zero-new-artifact bracket witness:** the already locked OCR/render for PDF/printed p.9 contains a second, currently unregistered passage headed `বন্ধনীর ব্যবহার`. It says to calculate inside parentheses first and then follow the operations outside. If one-anchor-per-row is retained, add a separate next-ID exemplar after rereading rather than expanding `TR11`'s estimation claim. This supports parentheses-first behavior, not the whole exponent/multiply/divide/add/subtract hierarchy.
2. **Fraction→decimal, one page:** PDF/printed p.59. It directly headings fraction-to-decimal and decimal-to-fraction conversion and visibly gives `17/10=1.7`, `1234/100=12.34`, `3002/1000=3.002`, `5/2=2.5`, `3/8=0.375`. This is the smallest direct addition for `fs-id2692103`; it does not cover repeating decimals.
3. **Circle vocabulary, minimum two-page set:** PDF/printed p.73 plus p.92. Page 73 says a circle's perimeter is called `পরিধি` and uses `ক্ষেত্রফল` and `বর্গ একক`. Page 92 uses `বৃত্ত`, `কেন্দ্র`, `ব্যাসার্ধ`, `বৃত্তের পরিধি`, `ব্যাস`, and states diameter is twice radius. Page 92's preceding prose definition of diameter is awkward/ambiguous; use it only as a lexical witness and take the mathematics from the pinned OpenStax source. Optional p.93 has a clear 3 cm radius construction, but it is not needed for the minimum set.

No inspected/acquired page directly witnesses repeating-decimal or `π` terminology. After the candidates above, any further search should be narrowly limited to those two gaps. If no official Indian-Bengali witness is found, keep `পুনরাবৃত্ত দশমিক` and `পাই (π)` explicitly provisional/editorial and seek West Bengal review; do not enlarge the bank generically.

## Required consultation plan

### Before drafting

- Verify the pinned hash above; do not use the two divergent copies.
- Register/lock only the candidate pages actually adopted, with OCR plus page-image verification. Until then they must not appear in a consultation receipt as current exemplars.
- Read `TR01`–`TR03`, `TR08`–`TR09`, `TR11`, `WB07`, and the p.9 bracket passage. For the circle block, read adopted pp.73/92. Add provisional ledger entries for the missing terms, distinguishing witnessed wording from editorial wording.
- Do not invent a Bengali mnemonic for “Please excuse my dear Aunt Sally” inside the source-faithful edition. Explain the preserved operation order plainly; any new mnemonic belongs only in labelled adapted content.

### During translation

- Revisit by block, not indiscriminately: p.59 with `fs-id2692103`; `TR04`/`TR06`/`TR09` with `fs-id1372950`; p.9 + `WB07` with `fs-id1739313`; pp.73/92 with `fs-id2218684` and `fs-id2741610`.
- Keep `ভগ্নাংশের বৃত্ত` restricted to the fraction model. Use the general witnessed forms `বৃত্ত`, `কেন্দ্র`, `ব্যাসার্ধ`, `ব্যাস`, `বৃত্তের পরিধি`, `ক্ষেত্রফল`, `বর্গ একক` only after their candidate pages are admitted.
- Define the editorial repeating-decimal term immediately from the source. Describe which digit(s) repeat; do not let the overbar include the nonrepeating prefix in `43/22=1.9\overline{54}` or similar examples.
- Distinguish exact `π` expressions from approximations using `3.14` or `22/7`; never replace `≈` with `=`. Keep circumference units linear and area units square. Preserve source dollars rather than inventing rupees/exchange rates.

### Pre-QA

- Reopen every cited OCR **and** page image and record concrete effects/no-change decisions. For new pp.59/73/92, require receipt hashes before claiming consultation.
- Check all repeat bars and ellipses against source MathML/render; check every signed inequality; independently evaluate all `π`, circumference and area results, including fractional radii.
- Scan title, lesson, key-concept, practice and glossary slots for one consistent term per concept. Confirm `TR11` is not cited for a `π` rule, `T031` is not cited for general circle geometry, and candidates are not called West Bengal certification.
- Record teacher/language, learner and assistive-technology review as pending unless actually performed.

## Explicit exclusions

- No canon files, consultations, terminology, source pins, translations, shared logs or build outputs were edited by this scout; no download/OCR/commit/push/publication/deletion occurred.
- Government material is language evidence only; no prose is to be copied and no page is mathematical authority.
- Exclude p.57's bad `12.74` placement row, p.9 OCR `40900`, p.92's ambiguous diameter-definition sentence, Tripura p.51's faulty mixed-number intermediate denominator, and WB p.191 example 5's flattened exponent printing.
- Do not claim a direct local witness for repeating decimals, `π`, negative cross-form ordering, the full order-of-operations hierarchy, or the English mnemonic.
