# U004 source translation and review notes

Complete source scope: `m81243#fs-id1321580`, Use Place Value to Name Whole Numbers. Tamil AI draft dated 2026-08-30. Only the new source CNXML and this note file are authored in this subtask; the separately authorized figure worker owns diagrams. No native-speaker, teacher, curriculum-alignment or efficacy approval is claimed.

## Actual boundary and inventory

Read the full English and Indonesian subsection in the committed `m81243` witnesses. Read-only XML inventory agrees across both:

- 112 elements, 53 source IDs and 9 MathML expressions.
- Six exercises with solutions: worked `fs-id1545709`; practice `fs-id2601285`, `fs-id1773572`; worked `fs-id1314136`; practice `fs-id2472209`, `fs-id2060477`.
- Three original images: `CNX_BMath_Figure_01_01_013_img.jpg`, `_014_img.jpg`, `_015_img.jpg`. Visually read each canonical JPEG, including the 013 “periods” label and the repeated `098` in 014.
- The final source item is `fs-id1808812`, exercise `fs-id2060477`, solution `fs-id1360632`, answer `fs-id1269733`.
- The next sibling is exactly **`m81243#fs-id1339359` — Use Place Value to Write Whole Numbers**. It is not included in U004.

All example numbers, dates, written values and comma grouping remain international/source-bound. Do not convert million/billion/trillion periods to lakh/crore periods. `098`, `061`, `004` and `000` retain their source roles; zero-padded groups are spoken by value, not as strings of digit names. No new companion or additional assessment is added here.

## Focused canon expansion and working consultation

Initially reread actual existing OCR pages 8, 20 and 175. These attest large-number context, இடமதிப்பு, இலக்கம், தீர்வு and the familiar Indian names இலட்சம்/கோடி, but not a sufficient worked number-name sample for this section. Searched the already-OCRed pages for number-name examples, then read page 24; it uses digit/place-value prompts but does not resolve this new spelling/register need.

Used the PDF skill's read-only rendering/OCR workflow and the existing `scripts/ocr_canon.py` to OCR just PDF pages 9-12 of the already-downloaded SCERT Class 6 Term 1 (2018) reference. No book was newly downloaded and no PDF output was built. Generated page images/OCR remain ignored under `downloads/tamil-canon/ocr/`. Poppler reported missing Symbol/ArialUnicode/Tahoma display-font substitutions; the relevant Tamil pages were visually checked after OCR. No OCR mathematical string was imported into the translation.

- PDF 9 / printed 3, table 1.1: basic place names பத்து, நூறு, ஆயிரம், பத்தாயிரம், இலட்சம், பத்து இலட்சம், கோடி. Confirms this canon uses Indian large-number structure, not the OpenStax international periods.
- PDF 10 / printed 4: tenfold growth and written scale names. Supports repeated factor-ten reasoning, not a new claim about source data/history.
- PDF 11 / printed 5, section 1.4 and the 359468421 worked table: visually confirms **பிரிவுகள்** for the grouped positions, and separated number-word components such as முப்பத்து ஐந்து and நானூற்று இருபத்து ஒன்று. This is a newly found attested alternative to the provisional **இடமதிப்புத் தொகுதி**. Retain the already-coordinated term across U003/U004 for now; inform the parent so any cross-unit terminology change is deliberate, not a unilateral mixed-register edit.
- PDF 12 / printed 6, example 1.2: visually confirms a worked name for 6,76,097 using separated tens/unit words and the connective ஆயிரத்து. This guides spacing and number-name cadence, but its Indian period names and numeral grouping are not substituted into OpenStax.

The exact selected Tamil source remains SCERT first edition 2018; no claim is made about the current syllabus. Its whole-number spelling variants are register evidence, not a mandate to reproduce every form. The resulting international-period Tamil wording still needs specialist/native-speaker review.

## Number-name and grammar decisions

- Continue U003's period term தொகுதி / இடமதிப்புத் தொகுதி and scale names மில்லியன், பில்லியன், டிரில்லியன். Name a period with the singular scale word after its count, while diagram headings remain plural. These preserve the source short scale.
- Use separated tens/unit words consistently, for example முப்பத்து ஏழு, நாற்பத்து எட்டு and தொண்ணூற்று எட்டு. Teen words remain lexical units such as பத்தொன்பது and பதினேழு. Hundreds compounds include நூற்று, இருநூற்று, முந்நூற்று, நானூற்று, ஐந்நூற்று, அறுநூற்று, எழுநூற்று, எண்ணூற்று and தொள்ளாயிரத்து where needed.
- Keep each international period count visibly separate from the following scale word, including ஆயிரம், e.g. **தொள்ளாயிரத்து நான்கு ஆயிரம்** for the 904-thousands group. This is explicit period-by-period instructional naming, not a claim that the entire mixed-scale expression is the most idiomatic continuous Tamil number name. Do not misread 904 as 9,004 or drop the thousand multiplier. A companion may explain equivalent familiar forms separately.
- The English source says to remove final **‘s’** from the period name. The Indonesian witness omits that language-specific clause. Tamil retains it with the explicit qualifier **ஆங்கிலத்தில்**, rather than wrongly telling learners to remove a Tamil letter or silently deleting source content.
- The source's **and** rule is not a universal rule about all languages or all English varieties. The Tamil sentence explicitly identifies the source's English whole-number naming convention and glosses and as ‘மற்றும்’. The English word remains within the original emphasis node as a discussed language example, not untranslated instructional prose.
- Preserve the English source's commas between named periods in answers. Several Indonesian solutions omit some or all of these commas even though the surrounding instructions request them. Tamil follows the explicit English convention consistently without changing any represented value.

## Source discrepancies and bounded assumptions

- `fs-id1171100715908` declares `tgroup cols="3"` but contains five rows with two entries per row. Both witnesses have the same declaration. Preserve the source tree/attribute rather than inventing missing cells. The renderer should expose the actual two-cell row contents; any CALS repair must be declared separately. The Tamil alternative describes the worked sequence without a false column count.
- In `fs-id2627959`, the problem says “one month in 2014”; the solution `fs-id1394436` newly says April. Both witnesses retain that mismatch. Tamil retains the general month in the problem and April in the solution and records the discrepancy. The 327,577,529 mobile-user figure is an unverified historical source exercise datum, not a newly verified statistic, current estimate or claim about unique people versus subscriptions.
- `fs-id1250766` says one year has 31,536,000 seconds. This equals 365 × 24 × 60 × 60 and assumes a 365-day year; the source does not mention leap years. Preserve the exercise datum and flag the assumption, rather than silently changing the number or adding a qualifier to the source question. A companion should make the assumption explicit.
- English source typographical forms “bilions” in the 014 alternative and “Unites States” in the phone solution are translated by their clear intended meanings, not transliterated errors.

## Figure coordination

Sent the figure worker the three original basenames, exact Tamil period headings and number names, `098` preservation requirement, 013 period-label meaning and the English-only grammar-rule limitation. Tamil paths are `../assets/u004/CNX_BMath_Figure_01_01_013_img.svg`, `...014_img.svg`, `...015_img.svg`. Matching rendered assets and offline closure remain independent integration checks; this translation subtask does not claim those artifacts were created or tested here.

## Review status

After drafting, reread the actual extracted Tamil number names and the newly OCRed page-11/page-12 number-name passages during revision/QA. The visual page checks resolve OCR's loss of letters in ஏழு and noise in the reference numerals. Retained the separated tens/unit cadence while keeping source-specific international periods and documenting the still-provisional mixed-scale register.

Read-only verification passed:

- Exact recursive structure/stable-attribute comparison against both witnesses: 112 elements, 53 unique ordered IDs, 9 unchanged MathML expressions, 6 exercises with all source solutions. Root language and image source/MIME/translated alternatives are the declared attribute differences. All source mathematical text, numbers, formatting and punctuation remain intact.
- Reconstructed seven complete Tamil names from a separate atomic vocabulary of units/teens/tens/hundreds and explicit scale multipliers. Each ordered `(group count, period multiplier)` pair matches the actual source numeral, not merely the overall total. Checked 37,519,248; 8,165,432,098,710; 9,258,137,904,061; 17,864,325,619,004; 327,577,529; 316,128,839; 31,536,000.
- Independently checked all five worked-table group names and all three phone-example subgroup names. The 904-thousands group reconstructs as 904 × 1,000; `061` names 61, `004` names 4, and the final zero-valued `000` group in 31,536,000 is not spoken, matching the source answer.
- Confirmed five table rows still contain two entries each under the original three-column declaration; no cells were invented or dropped.
- Confirmed the discussed English `and` remains within its original emphasis node, and the final-‘s’ instruction explicitly says ஆங்கிலத்தில்.
- Calculated 365 × 24 × 60 × 60 = 31,536,000 as evidence for the recorded 365-day-year assumption; no historical-statistics verification was claimed.
- Current source translation SHA-256: `7fe2102346c8fc56b989eafeb0df97c49128e3c334a58ac9edaa8975b74a5a02`.

The atomic-vocabulary reconstruction checks mathematical representation, not independent native-speaker approval of Tamil compounds or idiom. Final diagram matching, rendered learner layout, accessibility, a self-contained recovery companion and broader product coverage remain separate work. No build, PDF export, commit or full-product completion is claimed.

Next contiguous source marker: **`m81243#fs-id1339359` — Use Place Value to Write Whole Numbers**.
