# Independent review of the two U008 answer companions

Review date: 2026-08-31. Reviewer: `u002_figures`, separate from the companions' author. This is a bounded mathematical/source-mapping review plus focused Tamil-meaning review, not a complete native-language review of every sentence. The parent continues integration and the whole-assignment learning workflow.

## Outcome and authorized correction

All 58 exercise mappings and all 96 declared response parts pass the independent checks below. No incorrect numerical answer, broken fragment link, duplicate ID, invalid checked equality, wrong requested rounding place or double-rounded final answer was found. One low-severity feedback ambiguity was found in M21, with closely related wording in S21. The parent explicitly authorized the reviewer to qualify only those two sentences. The issue is resolved in the final hashes below; no other actionable finding remains within this review's scope.

### R1 — low severity, resolved: qualify scale-name substitution

- M21: `ta-m1-missing-21`, exercise `fs-id1572155`, problem `fs-id2261957`.
- S21: `ta-m1-reason-21`, exercise `fs-id1733890`, problem `fs-id3204832`, supplied solution `fs-id2700417`.
- Why: changing the scale together with its count can preserve a value: 3 trillion = 3,000 billion. The warning should concern replacing trillion with billion **without changing the count**, rather than implying every such conversion is invalid. The printed final answers were already correct.

Exact M21 sentence before:

> டிரில்லியனை பில்லியனாக மாற்றினாலும் மதிப்பு தவறிவிடும்.

Exact M21 sentence after:

> எண்ணிக்கையை மாற்றாமல் டிரில்லியனை பில்லியனாக மாற்றினால் மதிப்பு தவறிவிடும்.

Exact S21 sentence before:

> டிரில்லியனை பில்லியனாக எழுதினால் மூன்று இடங்கள் குறைந்துவிடும்.

Exact S21 sentence after:

> எண்ணிக்கையை மாற்றாமல் டிரில்லியனை பில்லியனாக எழுதினால் மூன்று இடங்கள் குறைந்துவிடும்.

The scope extension authorized only these two feedback sentences and the corresponding receipt updates. Reversing exactly one sentence in each final file reproduces its complete initial SHA256 byte-for-byte. Thus source references, IDs, question statements, answers, MathML, surrounding feedback and all other bytes are unchanged. The complete independent checks were rerun on the corrected files. This is a reviewer rerun, not a claim that the original author reran the author's separate witness decoders or other historical checks.

## Exact inputs and outputs

| File | Bytes | SHA256 |
|---|---:|---|
| `translation/recovery-m81243-missing-answers.xhtml`, initially reviewed | 79,917 | `df651587881d0708d313815176374aa344b5a6193aba5bd4b4a47e10ba8db8d2` |
| Same file, corrected final output | 79,973 | `bae2e03c4757dc2693e8727de667266eb2138ba3f31c2adbd1fe8662a8efc8aa` |
| `translation/recovery-m81243-supplied-reasoning.xhtml`, initially reviewed | 78,981 | `b3073a49dd1cd4f96f25a9ef75b085bbab1e97ffc84082ef607bb79b2df03ed5` |
| Same file, corrected final output | 79,043 | `8decc79dab1d138b315dd8505b899e7c4893678de2dc23689b72c17066460fb5` |
| `translation/m81243-fs-id2279009.cnxml`, unchanged U008 source | 40,016 | `d5f6b6de6bd0273f9b0a525af429ec296703502bdb4b4a5d04bc985429fb6f57` |
| `translation/m81243.cnxml`, unchanged assembled link-target source | 169,344 | `699a12c0c3db042fe83262b7f38b6bc1504bad7a660478f090106593f7ced959` |

## Independent structural and numerical checks

The reviewer derived the checks from the actual current U008 questions and supplied solutions, not by trusting the author's answer tables. The original receipt files were read only after the independent numerical run, for the authorized superseding receipt updates. Read-only Python XML parsing, exact rational arithmetic, restricted expression evaluation and an independently assembled Tamil atomic-number-word decoder were used; no audit script was added to shared builders.

- The source contains exactly 58 exercise nodes. The two ordered `data-answer-for` lists are disjoint, contain 29 entries each, and together cover those 58 IDs exactly once. Each list matches source order within its missing/supplied partition.
- All 58 `data-source-problem` values equal the actual problem IDs. All 29 supplied `data-source-solution` values equal the actual solution IDs. The other 29 exercises actually have no source solution. No source solution was silently created or removed.
- Each declared part count matches the actual source list length, or the shared source classification instruction's two requested lists. Each companion has 48 parts. Multi-part labels appear once each in the requested order; scalar cards do not invent additional `data-part` answers. The source's confidence checklist is not counted among these 96 exercise responses.
- Across both fragments, all 76 HTML IDs are unique and disjoint from the assembled source IDs. All 134 `href` fragments resolve against the two companions plus assembled source. There are no additional `headers`, `aria-labelledby` or `aria-describedby` IDREF attributes to resolve. Parsing the fragments with an HTML parser also preserves the same ordered ID lists; this is not a browser accessibility test.
- Every card has a reason and misconception feedback, an actual source-exercise link and an internal companion-method link. M29's method link is in its acceptance paragraph, not its feedback paragraph; this is valid and was not misreported as a missing route. Source-only fragment links intentionally require the parent's combined reader.
- The eight classification-list responses were recomputed with exact rational values from source MathML. Neither the presence of digit 0 nor the mere presence of a fraction/decimal notation controls classification; the tested fractions and decimals are nonintegral. The source convention is natural/counting from 1 and whole from 0.
- The four block-model answers were recomputed from the actual U008 SVG `data-kind` pieces: 202 is 3H/8T/4O; 204 is 6H/2T/0O; 201 is 5H/6T/1O; 203 is 4H/0T/7O. Hundreds identify 10 rows by 10 columns and rods 10 columns. These agree with the original rasters read during the figure task; the current review did not claim a new rendered figure approval.
- All 20 requested digit positions were derived from the original numeral and matched to the stated Tamil place label. All 20 extra digit × place-unit contributions were evaluated, including the two zero contributions in S05/S06 without losing their different named places.
- All 20 complete answer-name spans were decoded compositionally using units, teens, tens, hundreds and explicit thousand/million/billion/trillion scale multipliers; all reconstruct the actual question values. The 12 restated word-question spans match the actual Tamil source question wording and independently decode to the printed numeral answers. The corresponding supplied source solutions also agree. This verifies numeric meaning, not every idiomatic or orthographic choice.
- All 30 rounded response values were recalculated from each original number and actual requested place with integer nearest-multiple arithmetic. All 30 target/right-digit pairs stated in the reasons match those original digits. All 60 printed endpoint-distance calculations were checked separately.
- Every one of the 38 MathML equality chains holds. A separate visible-text pass checked 64 numeric equality-chain occurrences, plus four Tamil-word-to-number scale definitions. Together these cover every one of the 77 visible equals signs, including equalities in tables and calendar reasoning. These counts overlap; they are not 102 distinct mathematical facts.

Part accounting:

| Requested response type | Missing | Supplied | Combined |
|---|---:|---:|---:|
| Classification lists | 4 | 4 | 8 |
| Model totals | 2 | 2 | 4 |
| Digit-place names | 10 | 10 | 20 |
| Names from numerals | 10 | 10 | 20 |
| Numerals from names | 6 | 6 | 12 |
| Rounding results | 15 | 15 | 30 |
| Qualitative responses | 1 | 1 | 2 |
| Total | 48 | 48 | 96 |

## Focused reading of actual cards and source questions/solutions

Read the complete actual M19/M20/M21/M26/M27/M28/M29 and S19/S20/S21/S24/S25/S26/S27/S28/S29 cards, not only their answer spans. Read their actual U008 questions and, where present, supplied solutions. Also read complete M11–M15 and S11–S15 for the unit/year assumptions, the shared method/zero-group guidance, every complete answer-name span and every restated word-question span. The remaining cards received source-mapping and mathematical checks without a claim of complete sentence-by-sentence native prose review.

### Number names, zeros and source units

- M19 (`ta-m1-missing-19`): `11 | 471 | 036 | 106` correctly means 11,471,036,106. The name's 36-thousand group requires visible `036`, and 106 remains 106, not 160. The feedback correctly distinguishes losing a zero from merely speaking a group's count without saying its placeholder.
- S19 (`ta-m1-reason-19`): `3 | 226 | 512 | 017` correctly means 3,226,512,017. The final seventeen is `017`, not `170`; omitting its group-padding zero would shift more significant digits.
- M20: four billion plus 568 million produces 4,568,000,000 years, with both trailing thousand/ones groups `000`. This is the source's age estimate, not a new present-day factual verification.
- S20: seven billion plus 173 million produces 7,173,000,000 people. Both unnamed trailing groups remain `000` in digits; no new current population is substituted.
- M21: three trillion plus 500 billion produces 3,500,000,000,000 US dollars. Three trailing groups remain `000`. S21: 39 trillion produces 39,000,000,000,000 gallons, with four trailing groups / 12 zeros. Currency and gallon units remain unchanged. The narrow scale-count qualification is recorded above.
- Shared group guidance explicitly defines thousand 1,000, million 1,000,000, billion 1,000,000,000 and trillion 1,000,000,000,000. It uses international groups of three; it does not silently introduce lakh/crore grouping. The required `000` rule is qualified to groups right of the first used/nonzero group, avoiding a false requirement for unnecessary leading zero groups. The group-divider `|` is explained as a separator rather than division.
- M26's complete name “பதினெட்டு ஆயிரம், ஐந்நூற்று நாற்பத்து ஒன்பது” reconstructs the exact $18,549. S26's “இருபத்து நான்கு ஆயிரம், நானூற்று தொண்ணூற்று மூன்று” reconstructs the exact $24,493. Neither question asks for rounding; both companions preserve exact values and avoid claiming bank-specific check-writing instructions.
- M11/S11 retain feet. M12 states the 365-day assumption behind 365 × 24 × 60 = 525,600 minutes. S12 states the 365-day, no-leap-day assumption behind 70 × 365 × 24 = 613,200 hours, rather than applying it to every actual 70-year calendar span.
- M13/S13 preserve the source populations. M14 does not turn the source's relative “12 years ago” into a new date; S14 does not invent a base year for the five-year projection. M15 keeps the July 1, 2014 India estimate. S15's 2016 China projection, 1,377,583,156, stays separate from S28's 2014 original, 1,355,692,544. Source exercise data are not represented as newly verified contemporary statistics.

### Every rounding part, independently recomputed

Each arrow below starts from the source original, never the preceding result.

| Card | Original(s) and requested target(s) | Checked result(s) |
|---|---|---|
| M22 | 792 and 5,647; nearest 10 | 790; 5,650 |
| M23 | 28,166 and 481,628; nearest 100 | 28,200; 481,600 |
| M24 | 2,391 and 2,795; nearest 1,000 | 2,000; 3,000 |
| M25 | 163,584 and 163,246; nearest 1,000 | 164,000; 163,000 |
| M27 | $18,549; nearest 10 / 100 / 1,000 / 10,000 | $18,550 / $18,500 / $19,000 / $20,000 |
| M28 | 149,597,888 km; nearest 100,000,000 / 10,000,000 / 1,000,000 | 100,000,000 / 150,000,000 / 150,000,000 km |
| S22 | 386 and 2,931; nearest 10 | 390; 2,930 |
| S23 | 13,748 and 391,794; nearest 100 | 13,700; 391,800 |
| S24 | 1,492 and 1,497; nearest 10 | 1,490; 1,500 |
| S25 | 63,994 and 63,949; nearest 100 | 64,000; 63,900 |
| S27 | $24,493; nearest 10 / 100 / 1,000 / 10,000 | $24,490 / $24,500 / $24,000 / $20,000 |
| S28 | 1,355,692,544 people; nearest 1,000,000,000 / 100,000,000 / 1,000,000 | 1,000,000,000 / 1,400,000,000 / 1,356,000,000 people |

The focused Tamil reasons correctly unpack carries in S24(b), 149 tens + 1 ten = 150 tens; S25(a), 639 hundreds + 1 hundred = 640 hundreds; and M28(c), 149 millions + 1 million = 150 millions. S28's specific hundred-million calculation does not carry into its existing billion digit 1; that statement is not generalized to all rounding. The invalid double-rounding paths are explicitly identified as invalid: M27's 18,549→18,550→18,600; M28's 149,597,888→150,000,000→200,000,000 for the hundred-million target; S25's 63,949→63,950→64,000; and S27's 24,493→24,500→25,000 for the thousand target. All final answers use the originals.

### Qualitative acceptance and executable remediation

- M29 (`ta-m1-missing-29`, source exercise `fs-id1258379`): the newly authored 18-minute walk→about 20 minutes example correctly rounds to the nearest ten. Both distances, 2 and 8, are correct. It distinguishes the exact duration from an approximation, accepts a different sensible everyday example and asks for an original value, target place, rounded approximation and reason it helps. It does not impose the example's wording or claim 18 = 20.
- S29 (`ta-m1-reason-29`, source exercise `fs-id3202450`, supplied solution `fs-id1948767`): correctly explains whole numbers as counting/natural numbers plus zero under this source convention. Acceptance is based on that distinction, not verbatim copying. It does not introduce negative integers or misidentify the whole-number set as only zero.
- The method links point to actual classification, model, place, naming or rounding explanations. Card data, intermediate steps and misconception feedback support paper-based same-question correction without a teacher, purchased manipulative or missing worksheet. These are explanation/retry routes for already-present source questions, not fresh independent mastery tests or demonstrated learning efficacy.

## Actual canon consulted for this review

Read the current canon README and the actual already-OCRed p12 and p31 text, then inspected both complete page PNGs. Reread those examples during the two-sentence revision rather than relying only on a terminology ledger. No new PDF, OCR run or download was required.

- `downloads/tamil-canon/ocr/page-012.txt` and `.png`, PDF p12 / printed p6, examples 1.1–1.2: the actual chart/equation shows one lakh equals 100 thousands, demonstrating that a changed unit with a changed count can preserve value. This supports the M21/S21 qualification. The expanded-form example includes a zero hundreds contribution in 676,097; its visual operators and digit order, not garbled OCR, support checking named place versus contribution. The page's Indian grouping is not adopted for these international source questions.
- `downloads/tamil-canon/ocr/page-031.txt` and `.png`, PDF p31 / printed p25, examples 1.11–1.12: actual 8,436→8,400 and 78,794→79,000 confirm the chosen-place / immediate-right-digit / 5-threshold / increment-and-zero sequence. The image resolves OCR's corrupted inequality and digit readings. This supports the procedure, not an unverified assertion of current syllabus alignment.
- The previously established p11/p20/p35/p175 register remains context for grouped number names, இடமதிப்பு, natural/whole distinction and முழுமையாக்கல். This review does not invent new canon attestation for provisional international Tamil compounds or claim a fresh full reread of all those pages in this bounded pass.

## Limits and handoff

After correction, no actionable finding remains in the reviewed mathematics, mappings, link closure or focused passages. This is not a complete native-language review of every sentence, a human teacher review, a browser/screen-reader/print review, or proof that the whole module's independent learning route is complete. The source reviewer, module route hub, full diagnostics/mastery decisions and wider A00–A20 assignment remain the parent's ongoing work.

Only this new review note, the two explicitly authorized feedback sentences and appended reviewer supersession entries in the two original receipt files were authored with apply_patch. No source, SVG, builder, reader, shared log, PDF/EPUB or commit was changed. Free C: space before the correction was 13,743,058,944 bytes; no disk-full error occurred.
