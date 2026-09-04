# B003/B004 place-value and number-naming witnesses

Prepared 2026-08-30 for continuing the full Telugu assignment. This is a bounded
reference investigation, not translation completion or a native-speaker review.
Only this record and six ignored OCR/render pairs were written by this subtask.
The main translator must read the cited OCR and inspect the relevant page images
before applying these recommendations; this record does not stand in for that use.

## Verified source order and scope

Read the complete two adjacent subsections in the local canonical module:

- B003: `m81243#fs-id1883656`, **Identify the Place Value of a Digit**.
- B004: `m81243#fs-id1321580`, **Use Place Value to Name Whole Numbers**.
- Naming therefore follows the place-value subsection; it does not immediately
  follow B002's concrete models.

Canonical repository: `downloads/upstream-prealgebra`, commit
`38cae454e644abf9f0a623e876994553881597c9` (fresh `git rev-parse HEAD`).
Module `modules/m81243/index.cnxml` SHA-256:
`396b0029798e054e5db6d7acde738cec9f9d8b86bc81da8cc3690d01ec07cf2b`.
Source periods are groups of three: ones, thousands, millions, billions, trillions.
Its examples and comma positions remain authoritative for faithful translation.

## Readable canon and procedure

No new PDF download, archive copy, full-PDF OCR, or extraction was needed. Disk
space was checked before rendering: C: had `6649024512` bytes free; a later check
returned `6662070272`. No cleanup was performed.

- `TS6-2018`: SCERT Telangana Class 6 *గణితం*, 2018-19 impression, existing
  [official PDF](https://scert.telangana.gov.in/PDF/publication/ebooks/6TM_MAT.pdf).
  Local path: `downloads/canon/ap/TS-6TM-MAT.pdf`; SHA-256 freshly verified as
  `3faa1f0551382ea25853d62604c63aa27034c6c07f7d56ce016c83d36b6f90ee`.
  The directory name `ap` does not make this Andhra Pradesh evidence.
- `TS-MATH2-2018`: SCERT Telangana Class 2 mathematics, existing
  [official PDF](https://scert.telangana.gov.in/PDF/publication/ebooks/2TM_MAT.pdf).
  Local path: `downloads/canon/TS-2TM-MAT.pdf`; SHA-256 freshly verified as
  `88a78193298607ee83a232214736c77a33c4aebc8bfc7630896eca8a73317966`.
  Reread existing OCR pages42/44 (printed30/32), then inspected both complete
  page images for the place/value distinction and zero contributions.

First read the existing TS6 contents/intro OCR pages9-12 and the existing TS2
OCR. Rendered only TS6 PDF pages13-18 (printed3-8), then ran Telugu+English OCR
before reading their content. Read all six complete OCR outputs and inspected
all six complete PNGs. Tesseract version: `5.5.0.20241111`; models are the
existing `downloads/canon/tessdata/{tel,eng}.traineddata` from `canon/lock.json`.

```powershell
pdftoppm -f 13 -l 18 -r 140 -png downloads/canon/ap/TS-6TM-MAT.pdf downloads/canon/ap/TS6-naming
# For each generated PNG, using its same basename as the output prefix:
& 'C:/Program Files/Tesseract-OCR/tesseract.exe' downloads/canon/ap/TS6-naming-013.png downloads/canon/ap/TS6-naming-013 --tessdata-dir downloads/canon/tessdata -l tel+eng --psm 3
```

The command pattern was run once for each of the six pages. The raw OCR and
page renderings remain ignored reference files; this record is not a republication
or relicensing of the textbooks and is not training data.

## Four additional topic witnesses

These are new topic-specific anchors, not claims that every page is an exemplar.
The labels below avoid assigning the main canon's next C-numbers independently.

| Witness | Exact location | Verified observation | Concrete application | AP evidence |
| --- | --- | --- | --- | --- |
| TS6-PV-005 | PDF15 / printed5, section1.4, worked example3 | `5078 = (5×1000)+(0×100)+(7×10)+(8×1) = 5000+0+70+8`, then the zero term is omitted. Columns name `వేలు`, `వందలు`, `పదులు`, `ఒకట్లు`. Example4 also uses `పదివేలు`. | Distinguish named column, digit and contribution. An omitted addend does not erase the hundreds position. Use the existing smaller-place terms consistently. | Unverified |
| TS6-NAME-006 | PDF16 / printed6, section1.5, `3,15,645` example, table and final sentence | The lakh-position digit3 contributes `3×1,00,000`; the final name is `మూడులక్షల పదిహేను వేల ఆరువందల నలభై అయిదు`. The same page introduces one lakh after `99,999+1`. | Telugu number names combine each coefficient with a scale name. A separately labeled local-convention note may explain `లక్షలు`; do not replace OpenStax millions with lakhs in its charts. | Unverified |
| TS6-SCALE-007 | PDF17 / printed7, immediately below the table and the carry sequence | `9,99,999+1=10,00,000` is named `పదిలక్షలు`; `9999999+1=1,00,00,000` is named `ఒక కోటి`. | A local bridge comparison can equate quantities while preserving both notations: ten lakh is one million; one crore is ten million. The equivalences follow arithmetically, not from a claim that this page prints English scale names. | Unverified |
| TS6-COMMA-008 | PDF18 / printed8, section1.5.1, before/after comma examples and final chart | `130407` is shown as `1,30,407`, and `12200320` as `1,22,00,320`. Chart groups cover crores, lakhs, thousands and the three smaller places. The bottom identities include `1 కోటి = 100 లక్షలు` and `1 లక్ష = 100 వేలు`. | Explain that the same digits can be grouped differently without changing the number. Retain source `5,278,194` and source three-digit periods; if adding `52,78,194`, mark it as an original Indian-grouping comparison, not the translated source figure. | Unverified |

PDF13 / printed3, exercise1.1 items5-6 supplies the paired instruction forms
`అక్షరాలలో రాయండి` and `అంకెలలో రాయండి`. This supports an editorial translation
of naming as writing a number in words; it is not evidence for the English
million/billion/trillion loanwords. PDF14 / printed4 was read in full because it
fell inside the selected range; it treats rounding, so it is not used to justify
B003/B004 terminology. Its midpoint convention may be revisited when the actual
rounding subsection is translated, without another acquisition loop.

## Required semantic safeguards

1. **Source place-name wording differs from the canon's place-value distinction.**
   B003 source exercise `fs-id1256900` asks for "place value" in `63,407,218`,
   but its solutions give place names. For digit0 the source says ten thousands.
   TS2 PDF42/printed30 distinguishes `స్థానం` from `స్థాన విలువ`: zero has a
   named position but contributes0. Preserve the source answer and identify the
   question as asking which place the digit occupies, or add an explicit original
   terminology note alongside a faithful translation. Never state that this zero's
   numerical contribution is10,000. The same distinction applies to both Try Its.
2. **Preserve international grouping.** Three-digit periods and all original
   numeric strings, charts, exercise values and answers remain unchanged. Indian
   grouping/lakh/crore comparison belongs in labeled bridge commentary. The
   selected Telugu pages witness Indian grouping, not a Telugu instruction to
   rename OpenStax's periods.
3. **Keep unknown terminology unknown.** These six pages do not attest Telugu
   spellings for million, billion, trillion, or a technical equivalent of English
   "period" as a three-digit group. If using `మిలియన్`, `బిలియన్`, `ట్రిలియన్`
   and an explanatory `మూడంకెల సమూహం (period)`, record them as editorial
   bilingual choices, not as witnessed official TS terms. AP remains unverified.
4. **English naming grammar is not a universal Telugu rule.** B004's instruction
   to remove the final `s` from period names and omit the word *and* describes the
   source's English convention. Keep the English token and explain its scope;
   do not invent a Telugu suffix-removal rule or an unqualified rule against
   ordinary Telugu conjunctions. The canon provides usable Telugu naming syntax,
   but does not establish the source's US-English convention.
5. **Leading zeros within periods are positional.** In source `8,165,432,098,710`,
   keep the group `098` intact in the number/chart while naming its value as98
   thousand. This is compatible with the canon's explicit treatment of zero,
   but the exact source example is OpenStax evidence, not a TS quotation.
6. **Do not promote historical context to current statistics.** TS6 pages17-18
   mention older census figures; B004 gives a2014 mobile-phone example. These
   are source-context data, not verified current demographic claims.

## OCR and printed-source cautions

- At PDF18, OCR rendered `1,30,407` as `130,407`. The inspected image confirms
  the Indian separators; using raw OCR alone would reverse the evidence.
- At PDF15, OCR damaged multiplication and plus signs. The valid `5078`
  worked example was checked against the image, not inferred from OCR glyphs.
- The **printed** PDF15 bottom table row for21504 shows a factor `5×10`, while
  its expanded form correctly has `500`; the factor should be `5×100=500`.
  This corrects this record's first reading, which wrongly described the
  expanded contribution as50. Main's independent image rereading identified
  that descriptive error. The inconsistent factor row is not adopted
  as a mathematical exemplar. The well-formed examples1-4 above it independently
  support the same terminology. Do not copy the apparent printed error into a
  bridge explanation or silently claim the row was correct.
- At PDF16, OCR dropped the multiplication sign in `1×10,000`; the image
  confirms the correct expansion. PDF17's carry sequence has intentional blanks;
  they are exercises, not missing answers to be invented as printed content.

## Reproducible page receipts

All basenames below are under `downloads/canon/ap/`. Each `.txt` was nonempty
and read; each corresponding `.png` was inspected. PDF source hashes above were
checked in the same work session. Checksums prove identity, not reading.

| Basename | Printed page | TXT SHA-256 | PNG SHA-256 |
| --- | --- | --- | --- |
| TS6-naming-013 | 3 | `9481035018360d6ef49508da81dc480f89daafda9e30da83f7dca92cde744c60` | `1957028f7bf1097d7f790954dcc03353505e84a13b83fb4bb694add11400e104` |
| TS6-naming-014 | 4 | `caf98a4bc0e0671ba27332b9fe4ff29e48d0ba7c164c2668ce2ec27c457680b0` | `0d276babd6be0f1137511e71585eb3a91fa527033dae10ce11c5d40d302351a3` |
| TS6-naming-015 | 5 | `594afe62af4e28fd1a0bdc4801b4e798a383a8fd4ceccd2b3e9d9b568e68f9c3` | `79fd844a35ff3284c932b1b84c03787384028cd6db0153e8ae7ba795a38edbda` |
| TS6-naming-016 | 6 | `fa0940455952c00a09be0be31e8936ea07283a091680c595861b57d3ac603b4d` | `cfd288eb9e3822b68659c2f10ca3c0cf8002c494a3181acb1151f4208ef2883f` |
| TS6-naming-017 | 7 | `75997b6acb8cd098560a2a5f20359df7589701bb5764151f383d9afb43db560f` | `3551228fbaadb0ef43b9b7358219f4a7c8e00dcd84b0cffecf0c248f9ba74a28` |
| TS6-naming-018 | 8 | `e2a88d1fdb07c689a108383f9b2d3ad434899f9ed70a8f615e3a4037ddfb7b10` | `0a6805e6b1498a6b604f2a51ad7cb6911c641b66cd3e22f51b8871c5bb2023af` |

Next actual use: before drafting B003, reread TS2 PDF42 and TS6 PDF15/18 against
the complete source subsection; before B004, reread TS6 PDF13/16/17 and the
source's English-specific naming rules. Record the effect in the main
consultation log after using the evidence. A future focused international-term
lookup is justified if the chosen loanwords need stronger attestation; this
bounded six-page pass does not assert such evidence was found.
