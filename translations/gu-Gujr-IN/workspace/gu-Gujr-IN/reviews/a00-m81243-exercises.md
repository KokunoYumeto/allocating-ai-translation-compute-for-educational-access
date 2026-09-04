# A00 m81243 exercise and metadata translation review

Date: 2026-08-30. Scope: the complete `fs-id2279009` exercise section, module title, metadata/learning objectives, glossary, and the complete text of the self-check image. This is a bounded contribution to the continuing Gujarati assignment, not completion of A00/A10 or AX1/AX3.

## Source and coverage

- Canonical witness: `downloads/gu-Gujr-IN/a00-id/provenance/logbook/authority/prealgebra2e/m81243.source.cnxml`; SHA-256 `396b0029798e054e5db6d7acde738cec9f9d8b86bc81da8cc3690d01ec07cf2b`.
- Read the corresponding Indonesian exercise prose in `downloads/gu-Gujr-IN/a00-id/modules/m81243/index.cnxml` as a secondary translation witness. Mathematical content follows the canonical witness.
- Exercise output: `translations/a00-m81243-exercises.gu.cnxml`: 659 source elements, 273 source IDs, 58 exercises, 29 source-supplied solutions, 57 MathML expressions. All 124 natural-language text/tail/alt slots are translated. No missing even-numbered solutions were invented.
- Metadata output: `translations/a00-m81243-metadata.gu.json`: translated module title, parseable metadata CNXML with all six learning objectives, parseable glossary CNXML with all seven definitions, and four headers/six rows for the self-check chart.
- Source links, figure paths, numerical tokens, choice markers, identifiers, and child order are unchanged. Only source-facing language and the permitted `base-10` MathML `mtext` changed.

## Actual canon consultations

Before drafting, read `terminology.csv`, the canon README, examples list and consultation log, followed by the already-OCRed Std 5 Week 1 PDF p13 and Std 6 Week 1 PDF pp14–16 text. Visually read Std 6 pp14–15. GU-C01–04 and GU-C08–10 support the distinction between અંક/સંખ્યા, સ્થાનકિંમત, એકમ/દશક/સો/હજાર and the short imperative register. GU-C11–13 support concise exercise instructions; their order terminology was not substituted for unrelated rounding terminology.

During drafting, read the already-OCRed Std 6 Week 1 p13 and its actual page image (printed p31, Q3 place/number-name table). This is an additional targeted consultation, not an unrecorded claim about the original 13 examples. The page shows દસ હજાર, સો, દશક, એકમ; its word rows include છત્રીસ and સડસઠ and examples composing hundreds/thousands. This supports those spellings and joined hundreds such as ત્રણસો. Its લાખ convention was deliberately not substituted for the source's international three-digit grouping.

The existing OCR pp31–33 was briefly inspected while looking for topic-specific material; those pages are language/word exercises and were not used as rounding evidence. No useful rounding canon is claimed from them.

During revision, reread Std 6 p13/p14 and Std 5 p13 OCR against the assembled Gujarati exercise paragraphs. Reopened Std 5 p13 image to confirm સો, દશક and એકમ. Adopted the root's shared heading `પૂર્ણ સંખ્યાઓને નમૂના દ્વારા દર્શાવો`, `આધાર-10`, and ખંડ/સળી wording. Rewrote the metadata objectives as grammatical `…શકશો` continuations rather than copying imperative headings beneath an ability statement.

Targeted dictionary checks resolved uncertain spellings without downloading new PDFs: GujaratiLexicon's [સિત્તોતેર](https://www.gujaratilexicon.com/dictionary/gujarati-to-english-translation/સિત્તોતેર/) and [અઠ્ઠોતેર](https://www.gujaratilexicon.com/dictionary/gujarati-to-english-translation/અઠ્ઠોતેર/) entries were opened and read; the [ત્રાણું](https://www.gujaratilexicon.com/dictionary/gujarati-to-english-translation/ત્રાણું/) result confirmed 93. A direct ચુમ્માલીસ entry did not resolve; retained the draft spelling and leave orthographic variant choice to educator review. Search-result PDFs were not admitted or used as canon.

## Decisions and checks

- Preserve મિલિયન/બિલિયન/ટ્રિલિયન and દસ હજાર/સો હજાર to retain the source's international place-value lesson. Explain the contrast with lakh/crore in a separately labeled companion; do not insert an unmarked conversion into this faithful translation.
- Use the shared provisional rounding wording `સૌથી નજીકના … સુધી ગોળ કરો`. The exercise list wording mentions the nearest ગુણિત to make the target increment unambiguous. Dedicated Gujarati rounding-register/educator review is still needed.
- Preserve historical years, projections, country names, dollar/gallon/foot units and all example values. These are source exercises, not assertions that the historical population projections are current facts.
- `prepare_m81243_exercises.py` verifies the pinned source SHA, maps exact source strings, and rejects any uncovered English slot. It validates element/child order, IDs, attributes except translated alt/title, numeric text tokens and non-mtext MathML tokens.
- `qa_m81243_exercises.py` passes. In addition to the structural checks, it independently decodes 22 Gujarati number-word quantities against source values, checks 15 source-supplied roundings arithmetically, scans all exercise text/tails/alts for residual English, and checks four self-check headers/six rows.
- Exercise output SHA-256 after this review: `54cb5fe5f95e2c8401404d9fd8389bcb5e7064936af630ac21fd422722c5e5e9`.

## Integration and remaining review

The four base-ten exercise media (`CNX_BMath_Figure_01_01_201_img.jpg` through `_204_img.jpg`) retain original paths with Gujarati alt descriptions. The complete `CNX_BMath_Figure_AppB_001.jpg` image was visually read: four columns and six objectives. Its Gujarati text is supplied in `self_check_table`; the original raster still has English and must be replaced in the reader by a Gujarati accessible table/equivalent. No responses are collected or filled in.

No integrated HTML/PDF rendering is claimed in this bounded review. Root owns the combined module build and its rendered/assistive-technology checks. Native educator review remains pending for international number-name conventions, rounding register, coordinate terminology, and age-appropriateness of the preserved college/campus self-check advice. All requested source text in this bounded section is translated; remaining integration review must not be represented as completed.

Initial free-space check before writes: 1,182,330,880 bytes. Only small new translation/mapping/review files were written; no source acquisitions, deletions or commits were performed.
