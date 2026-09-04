# M81244 U012–U013 — original recovery companion notes

## Status, scope, and separation

- Date: 2026-09-01. Authored learner file: `translation/recovery-addition-phrases-applications.xhtml`. It is an original, teacher-independent recovery companion for U012–U013, not a translation/source fragment and not a replacement for either source section.
- The XHTML root declares `data-strand="original-companion"`; the opening Tamil text repeats the distinction. It collectively labels every D/P/M/T question and every R1–R3 model as newly authored. The only two source-derived phrase examples are separately introduced as such.
- This work did not edit U012/U013 CNXML, their notes, the existing addition-core companion, terminology, shared status/logs/builders/styles, or assets. The three existing U013 SVGs and their source JPEGs were inspected for source context; this companion does not embed or depend on them.
- Owned verifier: `scripts/qa_recovery_addition_phrases_applications.py`. It is read-only: it parses an input XHTML, evaluates/checks it in memory, runs negative mutations on deep copies, and prints a JSON result.

### Recorded prompt correction

The initial task shorthand paired U012–U013 with “subtraction by counting up.” Direct reading of the assigned U012 source showed that U012 is **addition phrase → notation and result**, while U013 is **application/perimeter problem solving**. The parent explicitly corrected the shorthand before final authoring: do not frame U012 as subtraction; any count-up material may appear only as an optional missing-addend/check strategy in newly authored companion material. The final companion follows that correction:

- R1 and every required D/P/M/T phrase item use addition only.
- The one count-up example is headed as an optional missing-addend check, says it is not U012 source, says it is not a D/P/M/T requirement, and limits its use here to final amount ≥ starting amount.
- Its subtraction equation is presented only as an equivalent check. The verifier requires that this be the only MathML subtraction in the entire companion.

## Exact bounded inputs

| Input | Bytes | SHA-256 |
|---|---:|---|
| `translation/m81244-fs-id2691382.cnxml` (U012) | 12,968 | `1bb36df94ec4db85db15a2b07985070532955e54f4e15edb94b15c8f39839c30` |
| `translation/m81244-fs-id2197427.cnxml` (U013) | 16,980 | `8e7aeb7d3d537466c4b98c902016f61ba4ff2f65b48f1c078c1d41029f8b5ceb` |
| `provenance/m81244.en.cnxml` | 119,141 | `b32058ce714e5fd43b010ccc81b2ae00a11567b229e9f96dda7b85b3cd82ba6b` |
| `provenance/m81244.id-ID.cnxml` | 123,306 | `d23343f302c34436169e88ffdbc4eab37baabf0a3d1134755b2f5676c75e1cc6` |
| `assets/u013/CNX_BMath_Figure_01_02_002.svg` | 3,245 | `9e7ba0e663a9fac7d3d801b8c14e9572a31482c872f521d7ca9ddde44671e249` |
| `assets/u013/CNX_BMath_Figure_01_02_003.svg` | 3,349 | `15c5db825e70164c99083bd70dbd184ada8d805fe9cc3f94ccae44d20022c67d` |
| `assets/u013/CNX_BMath_Figure_01_02_004.svg` | 3,454 | `fe97fdf9a9d0fc68890f683d4a0454829fa1165b375aed8d294d159b170fa911` |

The English/Indonesian files are whole-module witnesses. They and the already translated U012/U013 CNXML supplied source facts; they are not evidence for the new route's efficacy. The three U013 SVGs retain source perimeters 26 feet, 30 inches, and 36 inches but those source exercises were not copied into the companion. All companion D/P/M/T values are new.

## Actual Tamil canon consultation at all three stages

Reference throughout: the already acquired Tamil Nadu/SCERT Class 6 Term 1 Mathematics, first edition 2018, under ignored `downloads/tamil-canon/`. It is a register/convention reference, not the mathematical source and not current-board or grade-placement evidence. OCR was read first; complete page images controlled spelling and operators.

### Drafting — 17 actual examples across 10 complete pages

Read OCR and complete PNGs for PDF pages 007, 008, 011, 020, 028, 035, 036, 038, 046, and 175. The 17 relevant examples/locators were: learning objectives; successor; predecessor; grouped number-name reading; place value; numbered தீர்வு; சுருக்குக; முதலில்/இறுதியாக sequencing; இயல் எண்கள்; முழு எண்கள்; the unbounded next-number statement; கூட்டல்/commutativity; சமன்பாடு; மொத்தம்; கூட்டல் சமனி; everyday சுற்றளவு versus பரப்பளவு with miles; and glossary குறியீடு/கோவைகள்/கூற்று/தீர்வு distinctions.

### Revision — 16 actual examples across 9 complete pages

Reread the relevant OCR and complete images for pages 007, 008, 020, 028, 035, 036, 038, 046, and 175 while comparing the actual XHTML wording. This pass rechecked objective language; successor/predecessor; place value/solution; simplification and step order; natural/whole-number limits; addition, total, commutativity and equation; additive identity; application, distance, perimeter/area; and notation/expression/verbal-statement/solve glossary language.

### Final QA — 18 actual examples across 9 complete pages

Read the complete OCR again for pages 007, 008, 020, 028, 035, 036, 038, 046, and 175, then visually inspected all nine complete PNGs against the final wording. The 18 checks were: கற்றல் நோக்கங்கள்; +1 successor; −1 predecessor; இடமதிப்பு; தீர்வு; சுருக்குக; முதலில்/இரண்டாவதாக/இறுதியாக; இயல் எண்கள்; முழு எண்கள்; numbers are unbounded; கூட்டல்; பரிமாற்றுப் பண்பு; மொத்தம்; சமன்பாடு; கூட்டல் சமனி; அன்றாட வாழ்க்கை problem contexts; சுற்றளவு/பரப்பளவு and distance-unit separation; and glossary குறியீடு/இயற்கணித கோவைகள்/இயற்கணித கூற்று/தீர்வு காணல்/முழுக்கள் distinctions.

The actual images resolve OCR noise such as **கூருதல் → கூடுதல்** on page 036 and **குறிமீடு → குறியீடு** on page 175. No arithmetic/operator string was copied from OCR. The selected canon does not directly attest a headword for counting up or the exact missing-addend phrase; the companion therefore uses descriptive Tamil and marks the method optional. Arithmetic **கோவை** remains the already documented provisional extension of the attested algebraic-expression register. No native-speaker approval is inferred from consultation.

## Learner route and prerequisite check

The route is executable on paper without a teacher or script:

1. Attempt D1–D3 without opening answers. D1 checks phrase→addition notation/result; D2 checks the five application fields; D3 checks perimeter-side enumeration and a linear unit.
2. Mark an item correct only when every requested notation, calculation, reason, counted-object name/unit, and final sentence is present. D1 miss→R1, D2 miss→R2, D3 miss→R3; multiple misses start at the lowest R number.
3. Complete all P1–P3 even when all diagnostics pass. A practice miss routes to its matching R and the same P item again.
4. Attempt all M1–M3 with answers hidden. Any miss routes M1→R1→T1, M2→R2→T2, or M3→R3→T3.
5. After required T items pass, repeat all M1–M3 as one new answer-hidden attempt. Only one complete unassisted pass meets this companion's local condition; it is not full-course mastery.

R1 supplies six labelled new phrase models and the two separately labelled source-order examples. R2 supplies a fully worked five-field `135 + 86 = 221 குறிப்பேடுகள்` example with explicit carrying. R3 supplies a four-side `11 + 4 + 11 + 4 = 30 சென்டிமீட்டர்` example and separates perimeter from area. Every admitted D/P/M/T item has its own `.reason`, targeted `.feedback`, own answer mapping, and route link.

## Exact item/answer matrix

| Item | Required mapping/result | Required final meaning |
|---|---|---|
| D1 | `26+18=44`; `41+9=50` | identify the addition cue and base/addend relationship |
| P1 | `37+28=65`; `54+16=70` | identify starting and added amounts |
| M1 | `48+35=83`; `67+12=79` | retain phrase relationship and explain order |
| T1 | `29+46=75`; `62+18=80` | distinguish addends from the resulting whole value |
| D2 | `148+76=224` | 224 books, with sought quantity, phrase, notation, place-value work, and final sentence |
| P2 | `24+18+27=69` | 69 kilometres; include all three days, not “69 days” |
| M2 | `128+95+77=300` | 300 books; retain both carried 2s and both final zeroes |
| T2 | `186+139=325` | 325 notebooks; retain both carries and the counted-object name |
| D3 | `8+5+8+5=26` | 26 metres; all four rectangle sides, not area |
| P3 | `4+7+3+6+2+5=27` | 27 centimetres; six given sides exactly once |
| M3 | `15+9+15+9=48` | 48 centimetres; boundary length, not `15×9` area |
| T3 | `5+8+3+4+2+7=29` | 29 metres; six given sides exactly once |

The source-order edge cases are also fixed and checked: source phrase numerals 8 then 7 map to `7+8`, and source phrase numerals 6 then 4 map to `4+6`. Commutativity is explained but is not used to erase the semantic base/addend order.

## Machine validation and exact authored identities

Run from the repository root with the bundled runtime used in this workspace:

```powershell
& '[local-home]/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe' -X utf8 'ta-Taml-IN/scripts/qa_recovery_addition_phrases_applications.py' --check
```

Final PASS receipt for the exact companion below:

| Authored file | Bytes | SHA-256 |
|---|---:|---|
| `translation/recovery-addition-phrases-applications.xhtml` | 64,046 | `89831f415d7fc248d12ca3d1d2edcf13028c04d6e01a6fb9742454d406dd9736` |
| `scripts/qa_recovery_addition_phrases_applications.py` | 21,139 | `66d599ba9efc3d80b861b0364bdddcf84e16cf3b8d7d05b7313b0ee08ce7be40` |

Verifier result: 13 sections; 42 unique IDs; 60 closed local links; 12 items in exact 3 diagnostic/3 practice/3 mastery/3 retry distribution; 12 one-to-one answer containers; three rectangular semantic tables; six R1 phrase rows; 60 MathML roots comprising 43 true equations, 16 valid expressions, and one declared unknown; one optional count-up scope; and 10 deliberately corrupted in-memory fixtures rejected.

The verifier additionally checks:

- UTF-8 XML declaration, NFC text, passive XHTML/MathML element/attribute allow-list, Tamil `lang`/`xml:lang`, original-companion marker, no source/script/external resource node, unique ID prefixes, and every fragment target;
- each visible question link targets its own answer, each item's remediation attribute matches its R route, all answer/route/retry/gate links close, and every answer has useful-length reasoning and feedback;
- exact question operand lists, exact phrase-result equations, exact application expression/carry/final equation sequences, exact non-negated final sentences, exact perimeter side multisets/equations/linear-unit answers, and exact R1/R2/R3 worked mappings;
- all MathML numerals/operators, equality truth, the one unknown form `47+□=82`, the exact jump prose `3+30+2=35`, and that `82−47=35` is the only MathML subtraction and remains inside the optional R1 check;
- negative rejection of a numerically equal but semantically reversed phrase mapping, a missing application field, a true equation with the wrong perimeter side multiset, count-up relabelled as source, a wrong R route, a wrong visible answer link, an unrelated but true carry row, a false count-up prose endpoint, a negated final sentence, and subtraction inserted outside the optional check.

## Independent read-only review and limitations

An independent agent read the complete companion and checker without editing either file. Its first pass found the XHTML content clean and identified five checker blind spots; all five were then converted into the exact assertions/negative fixtures listed above. It then rehashed and reread the exact final identities in the table, reran the verifier, and independently confirmed that all five former blind-spot mutants are rejected. That final read-only audit was clean; it is agent review, not fluent-Tamil, human, teacher, or native-speaker approval.

No browser/EPUB/PDF render, screen-reader/assistive-technology test, full module integration, learning-efficacy study, teacher validation, fluent/native Tamil approval, current-board alignment, or grade placement is claimed. In particular, wide-table layout, MathML/`□`/`−` pronunciation, and final typography remain integration-stage checks. The companion's finishing condition applies only to its narrow new U012–U013 recovery route.
