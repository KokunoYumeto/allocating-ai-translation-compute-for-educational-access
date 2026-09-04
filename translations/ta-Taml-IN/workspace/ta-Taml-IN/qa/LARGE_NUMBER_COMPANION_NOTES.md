# U003–U005 original recovery companion — drafting and QA notes

Date: 2026-08-31. Scope: `translation/recovery-large-numbers.xhtml` only, with this note. This is new Tamil instructional material, not a translation of additional OpenStax text. It is a component awaiting root integration and rendered review, not a standalone finished edition, grade-placement instrument, full-module completion claim, or evidence of learner effectiveness. No source fragments, shared builders/styles, existing readers, shared logs, downloads, PDF/EPUB files, or commits were changed in this task.

## Actual references consulted

Read the current U003 `m81243-fs-id1883656.cnxml`, U004 `m81243-fs-id1321580.cnxml`, and U005 `m81243-fs-id1339359.cnxml`, including their worked answers, named places, media descriptions, zero-filled groups, and English-language qualifications. Rechecked the actual U003 SVG's 15 place-label elements against the new semantic lookup table. `recovery-u002.xhtml` supplied the semantic section/item/answer and paper-route pattern; new identifiers use `ta-large-`, not the earlier prefix.

During drafting and again during revision, read the already OCRed Tamil reference pages, then inspected complete page PNGs. These are PDF-page numbers in the 2018 Tamil Nadu Class 6 Term 1 reference identified in `canon/README.md`:

- Page 11 / printed 5, section 1.4: actual place chart, the explanation that chart positions prevent missing digits, the `பிரிவுகள்` row, and the number-name model for 359468421. It supports the distinction between a period/group and an individual place and separated tens/unit words. Its grouping is Indian; no international grouping authority is claimed from it.
- Page 12 / printed 6, examples 1.1–1.2: visually verified `10 × 10 = 100`, the 50,000 name `ஐம்பதாயிரம்`, and the 676097 expansion with a zero hundreds term. Used the sequence numeral → expanded contribution → name, not the OCR's corrupted multiplication/addition signs. The companion's 406 and 42 checks are newly authored applications, not copied canon exercises.
- Page 20 / printed 14, example 1.4: visually checked the named ones position and comparison of 59283746 with 59283748. OCR misreads some digits/operators. Used the actual distinction between an individual digit's position and its contribution; did not import this comparison exercise into the companion.
- Page 175 / printed 169: visually checked `இடமதிப்பு அட்டவணை`, `திட்ட வடிவம்` / standard form, and `முழு எண்கள்` versus `முழுக்கள்`. The glossary's standalone `தொகுதி` denotes numerator, not the source's period: it is not evidence that the new period compound is attested there.

Current `terminology.tsv` was consulted alongside, not instead of, these pages. `இடமதிப்புத் தொகுதி`, `மில்லியன்`, `பில்லியன்`, `டிரில்லியன்`, and the international high-place compounds remain the current documented provisional register. The companion defines the scale values explicitly: 1,000,000; 1,000,000,000; 1,000,000,000,000. It does not silently replace them with lakh/crore values or Indian comma groups. `திட்ட வடிவம்` is explicitly glossed as writing this whole number in digits; English `s`/`and` rules remain English-only.

## Pedagogical and zero-notation decisions

Four independent paper explanations cover R1 grouping, R2 digit/place/contribution, R3 blanks and zeros, and R4 names ↔ digits. Each provides a fully specified paper action and its check. No teacher, missing worksheet, specialist equipment, purchase, network, timed response, or spoken performance is required. An alternative of pointing/mental checking is stated for difficulty writing. The fragment makes no claim to meet every disability access need.

The notation scope is whole numbers written without a decimal point or fraction notation; commas separate international groups. A leading chart blank is not a digit. R3's 15-slot table contains exactly eight leading blank positions followed by 5,0,7,3,0,0,8. Whole-number leading zeros may be removed without changing value, but deleting the first zero in the interior `073` shifts the nonzero digit to its left. A whole number equal to zero is written `0`, not a blank, and R4 names it `பூச்சியம்`.

A second reader (`u002_translation`) reviewed the R3/R4 distinctions, the three new output number names, and question/answer pairing. That review correctly requested a qualification: a `000` group must be retained in digit notation when it is to the right of the first nonzero group; unused leading groups can be omitted. Applied at `ta-large-R4`. Changed the T4 heading from “blank” to “unmentioned” period so spoken omission is not confused with a chart blank. That reader's scope was not a full independent 16-question arithmetic audit and is not native-speaker approval.

R4 provides number-name checks for within-group 406, 42, 20, 30, 40, 60 and 12 so the remedial route does not only repeat the instruction “read the group.” Correct equivalent Tamil joining/spacing is accepted when the count and scale remain clear; `நாற்பது ஆயிரம்` and `நாற்பதாயிரம்` are an explicit example. Comma grouping is still assessed when requested. No rounding or all-9 carry exercise is introduced; those belong to U006.

## All 16 question/answer checks

This is 16 multi-part questions, not merely 16 scalar answers. Recomputed from the actual question nodes using independent integer formatting, positional powers, normalization/deletion, and a Tamil coefficient/scale parser; then compared those results with the actual answer nodes. Manual read-through checked all asked explanations and remedies as well.

| ID | Checked result and required reasoning |
|---|---|
| D1 | 4,807,316; million/thousand/ones periods; split from the right. |
| D2 | In 26,540,318, 5 is hundred-thousands; 5 × 100,000 = 500,000. |
| D3 | 0073 = 73; 2,073,005 ≠ 273,005 after interior-zero deletion. The 2 contribution changes from 2,000,000 to 200,000. |
| D4 | 3,005,042,007 = 3 billion + 5 million + 42 thousand + 7; padding preserves each three-place group. |
| P1 | 6,002,040,051; billion/million/thousand/ones; 002/040/051 require three written places. |
| P2 | In 53,406,218, 4 is hundred-thousands/400,000 and 6 is thousands/6,000; same period does not mean same place. |
| P3 | `ஏழு மில்லியன், இருபது ஆயிரம், நானூற்று ஆறு` reconstructs 7,020,406; 020 is 20 thousand = 20,000, not 200. |
| P4 | 2,004,000,006,009; five groups 2/004/000/006/009; the unmentioned millions group requires 000. |
| M1 | 8,070,042,006; four periods from ones to billions; 1 billion = 1,000,000,000. |
| M2 | In 83,260,415, 2 is hundred-thousands/200,000; 0 is thousands/0. Zero contribution does not erase the position. |
| M3 | 008,040,006 normalizes to 8,040,006; `எட்டு மில்லியன், நாற்பது ஆயிரம், ஆறு` reconstructs it. Interior deletion gives 840,006; 8 contributes 8,000,000 versus 800,000. |
| M4 | 5,000,007,012,003; missing billions = 000; 5/000/007/012/003. 1 trillion = 1,000,000,000,000. |
| T1 | 9,070,305,008; billion/million/thousand/ones; the first group is the fourth period from the right. |
| T2 | In 62,480,731, 4 is hundred-thousands/400,000; 0 is thousands/0. |
| T3 | 005,060,004 normalizes to 5,060,004; `ஐந்து மில்லியன், அறுபது ஆயிரம், நான்கு` reconstructs it. Interior deletion gives 560,004; 5 contributes 5,000,000 versus 500,000. |
| T4 | 6,009,000,004,005; missing millions = 000; 6/009/000/004/005. |

Also checked worked examples 8026415 → 8,026,415; the 42,508,316 contributions 500,000/0/8,000; 5,073,008 versus 573,008; 4,006,030,008; and 1,000,002,005. Every lookup-table value is 10 to its declared place power (0 through 14); all 15 Tamil names match actual U003 SVG place labels. The five scale rows are powers 0,3,6,9,12. The one MathML equation is 5 × 100,000 = 500,000.

## Routing, answer separation and scoring

- D1/D2/D3/D4 lead to R1/R2/R3/R4 respectively; multi-error guidance starts at the lowest needed explanation and proceeds in order. Four correct diagnostic answers with reasons may go to source reading.
- Every answer has at least one explicit R1–R4 remedy plus a link back to its exact question. R1 → R2 → R3 → R4 → source-help → P1–P4 gives a complete route.
- Practice requires all requested parts plus reasons before M1–M4. Incorrect mastery answers route to a fully specified paper action and then the complete new T1–T4 set.
- A gate is 4 of 4 **complete questions with reasons in one attempt**, local to this segment. The text disallows mixing corrected old answers with a new attempt. Failed retry leads through the explanation/paper activity, practice and a full later M or T set; a full R1–R4 restart is available without a teacher. Rest and returning another day are allowed.
- Reused attempts require freshly grouping and explaining the places, not recalling an answer. This is still a local self-check, not independent mastery evidence or a validated assessment.
- Questions precede their separate answer sections. No question has an answer-bearing `title`, hidden answer attribute or image description. Deliberately proposed erroneous zero-deletion strings are part of questions requiring comparison, not leaked correct answers. The learner is told to cover answers on paper or avoid scrolling to them first. The component does not implement access control or claim that answers are inaccessible in the document.

## Structural checks and integration boundary

Final automated read-only checks passed:

- Well-formed XHTML; 14 top-level semantic sections; 80 unique `ta-large-` IDs.
- Exactly 4 diagnostic, 4 practice, 4 mastery and 4 retry `data-kind` items; 16 unique matching `data-answer-for` answers.
- 71 fragment links resolve in the union of this component and the current three source fragments. Exactly three external-to-component targets: `fs-id1883656`, `fs-id1321580`, `fs-id1339359`. No external web link or new asset dependency is introduced.
- Three semantic tables have captions, column/row headers and closed `headers` references. The 15-row place guide is vertical, not a dense image. No script or image is required for the new paper activities.
- A separate lxml HTML parse retained every ID and element order; one MathML expression remains semantic. This is static structure QA, not browser/assistive-technology or print-layout testing.

An initial QA assertion compared high-place labels only with CNXML text content, omitting its alt attributes; it therefore failed despite matching source data. The check was corrected to compare the actual SVG's uniquely identified place-label text, and all 15 passed. No label was changed to satisfy that incomplete check.

The component deliberately assumes the three source sections will be present in the integrated edition. It is not link-closed as a standalone file by itself. A natural insertion point for the original source sections is before `ta-large-source-help`, with explicit source/companion boundary labels; root owns the actual integration. Preserve all source IDs and the existing full semantic chart alternatives. Recheck integrated IDs, source order, fonts, answer navigation and layouts after insertion. No rendered visual QA is claimed here.

## Final input/output fingerprints

SHA-256 of `translation/recovery-large-numbers.xhtml`: `37f05038e4c238ca0e7a0951f2b136e84aa7c6391a6acac7da7678498361baf8` (71,345 bytes).

Source files read at this checkpoint:

- U003: `d0851335f8a28f4785bbe8fae21b3e83f3df72f0b5bfc9f84baa9d160f27c5f7`.
- U004: `7fe2102346c8fc56b989eafeb0df97c49128e3c334a58ac9edaa8975b74a5a02`.
- U005: `103c960aee58649ea1db02d9dc75b65722e15aedc543ec3f526356bec16e1eff`.

Approximately 10 GiB of free space was available during the final read-only checks. No large outputs or deletions were made.
