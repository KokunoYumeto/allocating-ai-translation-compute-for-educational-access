# M81244 U012 translation notes

## Scope and source identity

- Date: 2026-08-31. This is a bounded source translation, not an original recovery companion or a claim that the module/assignment is complete.
- Owned source: `translation/m81244-fs-id2691382.cnxml`.
- Complete source boundary read in both witnesses: `m81244#fs-id2691382`, **Translate Word Phrases to Math Notation**. Tamil title: **சொற்றொடர்களைக் கணிதக் குறியீட்டில் எழுதுதல்**; this agrees with the separately authored fourth module objective.
- English witness: `provenance/m81244.en.cnxml`, SHA-256 `b32058ce714e5fd43b010ccc81b2ae00a11567b229e9f96dda7b85b3cd82ba6b`.
- Indonesian witness: `provenance/m81244.id-ID.cnxml`, SHA-256 `d23343f302c34436169e88ffdbc4eab37baabf0a3d1134755b2f5676c75e1cc6`.
- These are the previously pinned module witnesses, not newly acquired material. No witness, shared terminology/log, builder, CSS, companion or asset was edited. No download, PDF build or commit was performed for this subtask.
- Disk space was checked before authoring: approximately 4.6 GB free; the later revision check still showed 4,571,000,832 bytes free. No disk-full error occurred.

## Actual canon consultation

Reference: the already acquired Tamil Nadu/SCERT Class 6 Term 1 Mathematics, first edition 2018, `downloads/tamil-canon/tn-scert-6-term1-maths-2018.pdf`. It is a language/register reference, not the translation source or a board-alignment/grade-placement claim. The actual OCR was read before page images; no new corpus or OCR was needed.

1. **Drafting:** reread `canon/README.md`, the current terminology ledger, actual OCR pages 036 and 175, then their complete page PNGs. Page 036/printed 30 directly supports **கூட்டல்**, **கூடுதல்**, and **மொத்தம்**. Its OCR misreads கூடுதல் as கூருதல்; the actual image, not the OCR spelling, was followed. Page 175/printed 169 visually confirms **குறியீடு / Notation**, **இயற்கணித கோவைகள் / Algebraic Expressions**, and **சொற்றொடர் கூற்று / Verbal statements**. The OCR's குறிமீடு is not adopted.
2. **Focused drafting extension within already OCRed material:** searching existing OCR for simplification located page 028. The actual page OCR and full image were read. Examples 1.9 and 1.10 use **சுருக்குக** and provide step-by-step evaluation under **தீர்வு**. This supports **சுருக்குங்கள் / சுருக்குதல்** here; the reference's unrelated expressions, operands and operations were not imported. No additional PDF or page acquisition was necessary.
3. **Revision:** reread the relevant actual page-028 worked-example passage, page-036 addition passage, and page-175 glossary entries while reviewing every Tamil title, paragraph and table cell. Retained the attested operation/result distinction. The grammatical cue in `fs-id2649934` was revised to **எண்களின்**, which actually occurs in the translated problem, rather than referring to a word absent from that question.
4. **QA:** focused rereading of the same actual simplification and notation/sum passages, together with the source problem/solution pairs, informed the final language/task check. This was a targeted consultation, not a repeat of the entire corpus. Actual image spellings resolved the OCR uncertainties above.

These stage details are externalized here because the parent task owns the shared consultation log. No native-speaker approval or independent linguistic certification is claimed.

## Inventory and exact continuation

Both witnesses and the Tamil fragment have:

| Item | Count |
|---|---:|
| Elements, including section root | 273 |
| Ordered, unique source IDs, including section root | 41 |
| MathML `math` expressions | 52 |
| MathML `mrow` / `mn` / `mo` | 32 / 63 / 17 |
| Examples / practice notes | 2 / 4 |
| Exercises / problems / supplied solutions | 6 / 6 / 6 |
| Tables / rows / entries | 3 / 10 / 24 |
| Explicit `newline` nodes | 15 |
| Emphasis nodes | 4 |
| Links | 1 |
| Media / images | 0 / 0 |

- There are **no source figures**, original image basenames, asset mappings or redraw requirements in U012.
- Last note: `fs-id1933763`.
- Its exercise: `fs-id2792137`; problem: `fs-id1899406`; problem paragraph: `fs-id1549718`.
- Last solution: `fs-id1410392`; final node: paragraph `fs-id2451444`.
- The next sibling is **`m81244#fs-id2197427`, Add Whole Numbers in Applications**. It is outside this file. Later module sections remain pending separately.

## Translation and register decisions

- **கூட்டல்** names addition and reads “plus”; **கூடுதல்** names its result/sum. **மொத்தம்** retains the separate “total of” wording. These continue U009-U011 and the actual page-036 model.
- **கணிதக் குறியீட்டில் எழுதுதல்** is used for translating a verbal phrase to mathematical notation. This is not inter-language translation. **சுருக்குதல்** then evaluates the expression, following the actual page-028 instruction register.
- Unlike U009's notation-to-words questions, **all six U012 questions require both an expression and its simplified value**. Neither half of any supplied answer is omitted or replaced by the other.
- **சொற்றொடர்** is supported by the longer page-175 term சொற்றொடர் கூற்று. The exact heading compound remains a compositional editorial choice. **கோவை** remains the documented provisional arithmetic extension of the attested இயற்கணித கோவைகள். **கூட்டப்படும் எண்கள்** remains the plain descriptive addend term; no new direct addend headword attestation is claimed.
- “Increased by” is rendered **சேர்த்து அதிகரித்தல்**, e.g. **5-ஐ 6 சேர்த்து அதிகரித்தல்**. The three questions explicitly ask for the **value after increasing** and then state the initial number and the amount added. This prevents the increase amount from being mistaken for the requested final answer. The worked final sentence explicitly adds 31 to 28 and gives 59. This exact introductory phrase is provisional, not claimed verbatim from the canon. The late-review correction that superseded the earlier amount-focused wording is documented below.
- The three sum questions are phrased **பின்வரும் எண்களின் கூடுதலைக் கணிதக் குறியீட்டில் எழுதி, சுருக்குங்கள்: ...**. This Tamil preposed instruction keeps the original two numeral nodes and the source terminal period in their original order. It does not introduce different operands or another task.
- English `fs-id2649934` separately italicizes “sum”, “of”, and “and”; Indonesian replaces “of” with a repeated “jumlah”. Tamil uses the genitive form **எண்களின்** that actually appears in its question and **மற்றும்** between the two original numeral nodes. All three emphasis nodes in this paragraph and their original positions relative to the numbers are preserved. This is a disclosed language-grammar adaptation, not an assertion that English “of” is an independently positioned Tamil word.
- All existing MathML punctuation is preserved exactly, including `mn` contents `42.`, `31.`, and the leading space in ` 59.`. Prose is arranged around these nodes; no punctuation was silently extracted from mathematics.
- `fs-id2451444` supplies its final answer in **plain source text**, `37 + 69` and `106`, rather than MathML. The Tamil source retains this structure and the exact numerical/operator text. Converting it to new MathML would be an additional structural edit and was not done.

### Six phrase mappings and source operand order

The phrase column's original numeral order is preserved even where the expression reverses it. Addition's commutativity is not used as an excuse to alter the source expression order.

| Source wording | Tamil phrase | Original expression retained |
|---|---|---|
| 1 plus 2 | 1 கூட்டல் 2 | `1+2` |
| the sum of 3 and 4 | 3 மற்றும் 4 ஆகியவற்றின் கூடுதல் | `3+4` |
| 5 increased by 6 | 5-ஐ 6 சேர்த்து அதிகரித்தல் | `5+6` |
| 8 more than 7 | 8 கூடுதலாக உள்ள எண், 7-உடன் ஒப்பிடும்போது | `7+8` |
| the total of 9 and 5 | 9 மற்றும் 5 ஆகியவற்றின் மொத்தம் | `9+5` |
| 6 added to 4 | 6 சேர்க்கப்பட்ட 4 | `4+6` |

For “more than”, the comparative clause is postposed in Tamil so the embedded source numerals remain **8 then 7** without implying `8-7`, `8>7`, or an altered addition expression. “Added to” uses a relative-participle phrase: 4 is the number receiving 6. Both exact constructions are provisional and merit later fluent-Tamil review. No extra examples or totals were inserted in this source table.

## Source discrepancies and retained structure

| Table ID | Source `cols` | Actual source cells per row | Treatment |
|---|---:|---:|---|
| `fs-id1826990` | 5 | 4 in each of 2 rows | Preserve `cols="5"` and all 4 column specifications. Both source accessibility descriptions correctly say four columns; Tamil also says four. |
| `eip-id1168288294973` | 3 | 2 in each of 4 rows | Preserve `cols="3"` and every empty/nonempty cell. Translate its content summary. |
| `eip-id1168288520954` | 3 | 2 in each of 4 rows | Preserve `cols="3"` and every empty/nonempty cell. Translate its content summary. |

These are source declaration/content inconsistencies, not numerical errors. No extra blank columns or nodes were invented. A downstream renderer must handle the actual content without treating the declared excess column count as a new instructional field.

The English first table accessibility description spells one example operand as “five”; Indonesian writes “5”. Tamil **ஐந்து** in that description retains the English wording's value, while the visible example's original MathML remains `5`. One `aria-label` and two table `summary` attributes are translated. No other non-language source attribute changes are made except the locale declaration on the fragment root.

## Exact exercise/answer inventory

Each exercise has one source question requiring the expression and its result. All supplied solutions remain in source order.

| Exercise ID | Problem ID | Solution ID | Retained expression | Retained value |
|---|---|---|---|---:|
| `fs-id1392862` | `fs-id1833382` | `fs-id1363349` | `19+23` | 42 |
| `fs-id1932733` | `fs-id1375941` | `fs-id2211062` | `17+26` | 43 |
| `fs-id1311804` | `fs-id2216187` | `fs-id1731443` | `28+14` | 42 |
| `fs-id1330230` | `fs-id1568191` | `fs-id1726814` | `28+31` | 59 |
| `fs-id2130020` | `fs-id2370626` | `fs-id2164356` | `29+76` | 105 |
| `fs-id2792137` | `fs-id1899406` | `fs-id1410392` | `37 + 69` (plain text) | 106 |

All six values are correct. No missing source solution, supplied-answer repair, currency change or unit conversion was needed. The two source examples contain worked tables; the four try-item solutions are terser. Expanded recovery reasoning belongs in a separately labeled companion, not in this source fragment.

## Checks executed

Read-only Python/lxml checks were run against both actual pinned witnesses and the authored file; no helper scripts or output receipts were written outside the owned notes.

1. XML parses; recursive element hierarchy and ordered stable attributes match both witnesses, allowing only root `xml:lang` and the three translated language attributes.
2. All 41 IDs are unique and match the source sequence. The one link resolves to the retained local table `fs-id1826990`.
3. All 52 MathML trees match **exactly**, including element/child order, attributes, text, child tails, operators, punctuation, and the source ` 59.` leading space. No `mtext` translation exception is needed in this section.
4. Arabic numeral sequences match both sources in document text order, scanning individual text slots so separate rows/MathML nodes are not accidentally concatenated into new numbers. An initial checker joined all text before tokenization and therefore falsely merged adjacent row values across empty `newline` elements; that checker was corrected, not the source. Exact MathML equality had already passed.
5. Parsed each of the six problems, required its own ordered addends and mapped solution ID, and confirmed its corresponding expression and result. Independently recomputed each value by both direct integer addition and a decimal-column carry algorithm. All six pairs passed.
6. Separately asserted all six phrase-column numeral pairs and expression orders. In particular, `(8,7)` maps to `7+8`, and `(6,4)` maps to `4+6`, not merely to an equal total.
7. Enumerated all three actual table row widths and preserved the source inconsistencies reported above. Explicit line breaks, empty cells, four emphasis nodes and final plain-text answer are retained.
8. Scanned every prose text/tail slot for residual Latin prose: none. The translated accessibility label was manually compared with all six visible phrase/expression pairs, including five/ஐந்து/5 equivalence.
9. Media inventory is empty, so no image/download/asset closure operation was required.

Superseded pre-peer-review source SHA-256 after the grammar-cue revision: `4ce210463223cffb59b54c93ef3da85323b5e8f6cfbec4e53cf37f1674d3f8c3` (12,457 bytes). This is retained only as checkpoint history, not the current validated artifact identity.

At that pre-review checkpoint, repeat checks passed against both witnesses: recursive hierarchy/stable attributes, ordered IDs, exact MathML, text-slot numeral order, every question's own expression/result, decimal-column and direct-addition results, all six table phrase mappings, local link closure, and no residual Latin prose. A separate assertion confirmed that the highlighted **எண்களின்** cue occurs in the actual Tamil problem. Boundary IDs remained `fs-id1899406`, `fs-id1549718`, `fs-id1410392`, `fs-id2451444`. Focused page-028 and page-175 OCR passages were reread at that QA stage, retaining the previously visually resolved spellings. That disk check showed 4,518,739,968 bytes free.

A bounded read-only sibling review of the table language and two explanatory paragraphs arrived after the original handoff. Its findings and resulting narrowly authorized edits follow. It is not a review of every source field or fluent-Tamil approval.

## Authorized late-review correction: result after an increase

On 2026-08-31, the figure/review worker identified a genuine task-meaning ambiguity in **28-ஐ அதிகரிக்க வேண்டிய அளவு 31**: it foregrounded the amount 31 rather than asking for the resulting value 28+31. The translator agreed, reported the concern to the parent without altering an out-of-scope file, and received explicit authorization to revise this U012 source and its notes while finishing U013. No mathematical answer was wrong or changed.

Actual page-028 simplification and page-036 addition passages were reread for this revision; their previously visually checked spellings were retained. The fix names both the action of adding to increase and the resulting value. Fixed source numeral nodes and terminal MathML periods remain untouched.

Exact changed language fields:

- `fs-id1826990/@aria-label`: the third keyword and third example now use **சேர்த்து அதிகரித்தல்** and **5-ஐ 6 சேர்த்து அதிகரித்தல்**.
- In the same table's body row, the second entry's third line uses the new keyword; the third entry's third example places the same two original numeral nodes inside the clearer action phrase. All other phrase lines and all six expressions are unchanged.
- Problem paragraphs `fs-id1968803`, `fs-id2269129`, and `fs-id1549718`: explicitly **அதிகரித்தபின் கிடைக்கும் மதிப்பைக் கணிதக் குறியீட்டில் எழுதி, சுருக்குங்கள்: தொடக்க எண் ...; அதனுடன் சேர்க்கப்படும் அளவு ...**. Original ordered pairs remain 28/31, 29/76 and 37/69.
- `fs-id1578716`'s existing emphasis node: **சேர்த்து அதிகரித்தல்**. Its addend explanation is otherwise unchanged.
- `eip-id1168288520954`, first row/second entry: explicitly states the value after increasing, initial number 28 and amount added 31. Fourth row/second entry: **எனவே, 28-ஐ 31 சேர்த்து அதிகரித்தபின் கிடைப்பது 59.** The translate row, add row and all mathematical nodes are unchanged.

The peer also found that the postposed comparison for “8 more than 7” is awkward but denotes 7+8, and confirmed that **எண்களின்** actually appears in the translated sum question. Those fields were not changed in this bounded fix; the provisional fluent-language review caveat remains.

**Current validated source SHA-256:** `1bb36df94ec4db85db15a2b07985070532955e54f4e15edb94b15c8f39839c30` (12,968 bytes). The old hash above is superseded.

Repeat QA on this exact new file passes both source witnesses: 273 elements, 41 ordered IDs, 52 exact MathML trees including internal text/tails/punctuation, stable attributes, and body numeral order. All six question/expression/result pairs were checked again and all six answers independently recomputed with direct and decimal-column addition. All six phrase-expression orders remain exact, including 8/7→7+8 and 6/4→4+6. Additional assertions require the three revised questions to ask for **அதிகரித்தபின் கிடைக்கும் மதிப்பு**, identify the **தொடக்க எண்** and **சேர்க்கப்படும் அளவு**, and contain no remaining **அதிகரிக்க வேண்டிய அளவு** wording. The table accessibility example matches its corrected visible wording. No new source nodes, examples, mathematical tokens or values were introduced. The parent was asked to rerun its source gate for the new hash rather than reusing the old receipt.

## Remaining boundaries

This checkpoint does not include rendered reader/PDF or assistive-technology QA, fluent-Tamil approval, validated placement, or a full teacher-independent route. No educational efficacy claim is made. The next source content is `m81244#fs-id2197427`; the parent task owns subsequent source assignment and module integration.
