# PNB-004 — function-notation translation notes

Date: 2026-08-30. Language: Western Punjabi in Shahmukhi (`pnb-Arab-PK`). This is a draft; no native-speaker or educator certification is available.

## Boundary, witness, and schema

The root `FULL_ASSIGNMENT_USER_INSTRUCTION.md` was read before this work. The larger assignment remains ongoing; this file records only one bounded section, not completion of the assignment.

The complete English and Indonesian section `fs-id1165134474160`, “Using Function Notation,” was read from the actual local CNXML files at `downloads/upstream/osbooks-college-algebra-bundle/modules/m49301/index.cnxml` and `downloads/extracted/A30/repo/source/modules/m49301/index.cnxml`. The pinned English commit is `789b54099106b071d1d32bfcee454fed72eb4768`. Coverage stops before the next section, `fs-id1165137804204`.

The selected section has 11 direct children, including its title. Coverage includes its four introductory paragraphs, standalone equation, function-notation definition note, Examples `Example_01_01_03` and `Example_01_01_04`, the Analysis commentary, the Try It problem and answer, and the Q&A. The canonical diagram ID is `Image_01_01_005`, not a renamed Figure ID; its media ID is `fs-id1165135187902`. Inline term ID `term-00011` is preserved with an un-emphasized span.

JSON fields are `locale`, `unit`, `title`, `subtitle`, `source_blocks`, and `bridge_after_html`. The 23 source-block values are strings. They contain 45 ordered inline MathML placeholders. The standalone equation `fs-id1165135332760` contributes one further MathML tree, for 46 total; its empty label is not a translated text block. The actual section contains 35 source IDs, no CNXML links, no footnotes, and no immediate nested block children inside translated paragraphs. Therefore this translation needs neither link nor child placeholders. The display equation is a MathML `mtable`, not a CNXML table requiring translated table-header keys.

## Actual canon reading

`canon/examples.json` was reread before drafting. The following readable local source passages were then inspected with surrounding lines, not only their index quotes:

- R1 lines 27–29, C01: ability/passive constructions support Punjabi `سکدے آں`, `سکئیے`, and `کیتی جاندی اے` in the introduction, notation definition, and Q&A. These are grammatical adaptations, not claimed verbatim occurrences of every inflected form.
- R1 lines 38–40, C02: the infinitive/obligation register informed the instruction that operations must be performed in the stated order.
- R1 lines 44–46, C03: ordinary sequencing language informed `اِسے ترتیب نال`; no specialized notation terminology is certified by this literary passage.
- R2 lines 26–28, C05/C06: the purpose connective informed `تاں جے` in the opening paragraph, and the explicit-alternative construction informed `دی بجائے` in the Q&A. Purpose is not confused with mathematical implication.
- R3 lines 24–26, C10: the qualification register informed the separately marked original clarification of the leap-year/domain wording.
- R3 lines 30–32, C09: reminder phrasing informed `چیتے رکھو` and the reminder about `d = f(m)`.
- R3 lines 37–39, C11: reason-giving informed the March example's `کیوں جے`. Calendar values come from the algebra source, not the prose canon.

During revision of the composed draft, R1 lines 28, 39, and 45; R2 line 27; and R3 lines 25, 31, and 38 were reread. This pass checked ability/obligation, purpose versus implication, sequencing, alternatives, reminder wording, and explicit qualifications before the first file write. Canon sources remain one author's prose essays, not specialist mathematics references. No shared reading receipt was overwritten and `read_canon.py` was not run.

## Linguistic and mathematical decisions

- Provisional `فنکشن دی علامتی لکھت` translates function notation through an accessible Punjabi construction. It is not claimed as a settled Pakistani mathematical term. Existing ledger choices for function, input/output, variable, expression, domain, and set are retained. `قوساں`, `لیپ سال`, `ہندسی چیزاں دے لیبل`, and the applied-subject wording still need target-language educator review.
- The source term “height” is rendered `قد` in the age example. Source `h`, `a`, `f`, `g`, `x`, `y`, `z`, `A`, `B`, and `C` remain in their actual MathML order and case. English italic letters outside MathML (`a`, `b`, `f`, `y`, `x`) remain italic and explicitly LTR-isolated.
- The source's function/input/output distinctions are retained. Applying a function is not described as multiplication, and `f(a+b)` adds `a` and `b` before applying `f` to their sum. The Q&A distinguishes the rule from its output even when notation reuses a letter.
- The source reuses `h` first for height and later for the function `h(a)`. It also uses `y` for different roles in different examples. No variable was renamed to hide this; an original note directs the reader to context.
- The month example's source instruction says the domain excludes leap years although its inputs are month names. That wording remains in the faithful translation. A clearly labeled original note interprets the intended restriction as month names in a non-leap year and distinguishes months from years as domain members. No leap-day count or extra calendar rule is introduced from memory.
- January in the original image and March in the following prose are preserved as different examples. Source `31`, `2005`, and `300`, including repetitions outside MathML, remain unchanged and visible prose numerals are LTR-isolated. No date or count has been inferred from the canon's historical anecdotes.
- The police-officer scenario remains a town and year with the source numbers. The Try It remains the weight of a pig, in pounds, as a function of age in days. Neither the animal, pounds, days, nor answer `w = f(d)` is localized to a different example or unit.
- Source paragraphs are faithfully translated. The original `bridge_after_html` is marked both by `data-origin="original-bridge"` and Punjabi heading/introduction; it contains the English-expression/diagram key and the two disclosed clarifications. No new practice or following-section material is added.

## English content retained in mathematics and image

The standalone equation contains ten English `mtext` nodes across three rows. Its original MathML is not rewritten into Punjabi. The original bridge explains each row in Punjabi, including the function name, the meaning of parentheses, and the reading “f of a.” Inline MathML's `days`, `month`, and `March` remain English, with Punjabi equivalents in the key.

The existing upstream JPG `downloads/complete-upstream/osbooks-college-algebra-bundle/media/CNX_Precalc_Figure_01_01_005.jpg` was opened with original detail before drafting. It shows `31 = f(January)` and the labels `output`, `rule`, and `input`, with arrows pointing to `31`, `f`, and `January` respectively. These English labels remain in the figure and have a bilingual key. The Punjabi alt text preserves the expression and provides `جنوری` as the meaning of January. The Indonesian source's localized SVG is a comparison witness, not a replacement asset. No image was edited, copied, downloaded, or extracted by this translation pass.

## Required display-punctuation treatment

All source MathML stays in the frozen witness. The parent renderer agreed to log presentation-only text changes by exact source-tree paths and old/new text in `data-source-text-edits`, without deleting nodes. Its structural QA must reconstruct the exact original tree from those logs. Important cases:

- `eip-id1165135256026`, inline slots 2/3: the source embeds an opening curly quote with `y` and a period plus closing curly quote after `x`. Punjabi uses the complete quotation `«{{math:2}}، {{math:3}} دا فنکشن اے»`; the embedded English quote/period must not appear midway through it.
- `eip-id1165135256026`, slot 5: the terminal comma is `mtext`, not `mo`. The translation supplies Punjabi prose punctuation.
- `fs-id1165137596424`, slot 0: `d` has a terminal `mtext` period; the Punjabi predicate follows the symbol, so that period belongs at the end of the translated sentence.
- `eip-id1165132005171`, slots 0/1: each final `mo` combines `),`. Only the terminal sentence/list comma is eligible for relocation; the closing parenthesis must remain.
- `fs-id1165137453971`, slots 2/4/6: internal commas separate `f,g`, `x,y`, and `A,B` and must remain. Only the terminal prose-list comma is handled as presentation punctuation.

Other terminal English commas/periods in the selected inline formulas likewise require the logged presentation treatment. The standalone English explanatory equation is preserved as a complete source display, with its language explained in the original key. No mathematical comma, parenthesis, variable, numeral, operation, or equality sign is intentionally changed.

## QA status

After the JSON was saved, the entire saved translation was reread, followed by R1 lines 28 and 45 (C01/C03), R2 line 27 (C05/C06), and R3 lines 25, 31, and 38 (C10/C09/C11). This final canon pass checked the actual wording for ability, operation order, purpose/alternatives, reminder constructions, reason-giving, and separated qualifications. The historical anecdotes were not used as mathematical or biographical data for the translation.

A read-only PowerShell comparison against the actual English section passed: 23 translated text/alt keys, zero missing/extra keys, 45 inline placeholders in exact per-block order, 46 total source MathML trees including the display equation, 35 source IDs, 11 direct section children, and the verified next section `fs-id1165137804204`. Every source block's numerals outside MathML were compared with its translated counterpart in order, including the alt text; no drift was found. JSON and all HTML-bearing fragments parsed, and the target contained zero Gurmukhi, replacement characters, or forbidden bidi controls. There are no unintended link/child placeholders.

Independent read-only source review confirmed the same inventory and the January/March distinction, retained pounds/days/pig scenario, inline term ID, Analysis commentary, and punctuation exceptions. No source witness, shared receipt, neighboring translation unit, renderer, or asset was changed by this drafting pass.

This drafting note does not claim successful reader builds, reversible MathML reconstruction, browser layout, screen-reader pronunciation, or native-language approval; those checks are separate. In particular, the quoted notation definition must be visually checked after the renderer's logged punctuation handling, and the wide English MathML display needs narrow-screen inspection.
