# A10-007 language and source notes

## Status and exact boundary

This is an input freeze for one complete source section in canonical OpenStax module `m82453`, not completion of the module, book or five-work assignment.

- Canonical source: `downloads/complete-upstream/osbooks-prealgebra-bundle/modules/m82453/index.cnxml`, 184,248 bytes, SHA-256 `a8fdd235aa254c5a0a1248fa858e9b3579d9b40982bbc514cbe6a18c3e6fcbed`, pinned commit `38cae454e644abf9f0a623e876994553881597c9`, tree `7907e4c81d43de1c3b6da173f0eb273c01dc5b55`, blob `b754c49c00681fac8192f4254d947d54661d1132`.
- Indonesian comparison: `downloads/extracted/A10/translated/modules/m82453/index.cnxml`, 186,219 bytes, SHA-256 `2c0b688d569044b128d589579e9ba7d871a0fb9ac7a670ac6f22d0ef2b66e635`, locked A10 release v1.0.2. It is comparison evidence, not authority over the pinned English.
- Included source: complete section `fs-id1170654953465`, “Simplify Expressions Using the Order of Operations”, all 31 direct children from its title through note `fs-id1170654936028`; last descendant is answer paragraph `fs-id1170654940244`.
- Exact raw canonical range: bytes `[42893,72059)`, 29,166 bytes, SHA-256 `3dc49717e5bbe76d0c8c1003e1bad065bdc079a9f274d4b55a33eb333cc55770`.
- Generated document-root excerpt: 29,437 bytes, SHA-256 `ba24af2abd61450c3b269543066608080acbb34ab1e29bf41d6c7431829bfaf2`. The generated wrapper ID is `a10-unit-007-excerpt`; the selected section tree is otherwise unchanged.
- Stop before complete next section `fs-id1170654889475`, “Evaluate an Expression”. No intervening node is skipped.
- Previous A10 reader is A10-006. Following sections, Section Exercises, glossary, remaining modules and the rest of A10/A20/A30/B10/B40 remain required.

The selection contains exactly 143 translated source blocks, 111 source IDs, 21 MathML trees, 31 paragraphs, six titles, three terms, nine exercises with nine supplied solutions, three explicit source “Solution” titles, 12 circled part tokens, three explicit newlines, four source tables, 35 rows, 70 cells, 16 genuinely empty cells, 23 media/image nodes and 18 bold source emphases. The 143-block calculation is:

- 31 paragraphs;
- six titles;
- eight list items;
- one direct-text note (`fs-id1166425080552`);
- four table summaries;
- 70 table cells, including all 16 empty cells;
- 23 image-alt blocks.

The earlier provisional count of 142 omitted the direct-text note. It was corrected before input freeze rather than being forced into a fabricated paragraph.

## Actual canon consultation

The readable target-language canon is the selected-passages catalog in `languages/pnb-Arab-PK/canon/examples.json` plus the underlying files `downloads/canon/pnb-Arab-PK/R1.txt`, `R2.txt` and `R3.txt`. These are three Shahmukhi Punjabi prose essays by Jamil Ahmad Pal. They guide prose register and grammar only; they are not mathematical authorities and do not certify the provisional terminology.

Actual stage receipts:

| Stage | Receipt | SHA-256 | Passages actually read |
|---|---|---|---|
| Source study | `canon/receipts/A10-007-next-unit-20260901T113658158000Z.json` | `b6fd5c63ff892c2cae0b04523e1bf8ac0ca36181916e0f4d1f5445c5c0cbb59b` | C01–C12 |
| Draft | `canon/receipts/A10-007-draft-20260901T131653162304Z.json` | `130cc5498a2fb3f7b3bada3a09bcefa2fe0d18472218e30149013ee9aa812d29` | C01–C12 |
| Revision | `canon/receipts/A10-007-revision-20260901T133224609108Z.json` | `767f1285e27c3793f12b8b07c3c1ee01a40137931bcdd26e15e265da3ae79446` | C01–C07, C09–C12 |
| Pre-render QA | `canon/receipts/A10-007-qa-20260901T143427234503Z.json` | `9fdfcdc97cd4d31c4ca391322c9ecf10ee4ac54d43b22a652e5923062c8b81a2` | C01–C05, C07, C09–C12 |

Specific influence:

- C01 supports Punjabi capability/agreement in “قدراں دے سکدیاں نیں”; Urdu `سکتی ہیں` was not substituted.
- C02 supports direct reader-facing infinitive/imperative clauses: “سادہ کرو”، “ضرب کرو”، “گھٹاؤ”، “ونڈو”.
- C03 directly supports `ترتیب وار`. Revision changed the equal-priority directions from the more generic “ترتیب نال” to “کھبے توں سجّے ول ترتیب وار”.
- C04 guided plural agreement with `نیں`, including expressions, values, operations, rows and images.
- C05 keeps purpose wording separate from implication; the equality-sign clarification uses `تاں جے` as a teaching aim, not an iff claim.
- C06 informed explicit alternatives such as multiplication versus division and multiplication-dot versus adjacency; it was not reread at QA because the relevant alternatives had already been reconciled.
- C07 informed ordinal/location language: `پہلاں`, `اندرلیاں`, `تھلے`, and left-to-right directions.
- C09 caused the revision from Urdu-leaning repeated `یاد` language to `چیتے رکھن / چیتا کراندا` around the mnemonic.
- C10 guided the separately labeled limits on the vague historical statement, source alt errors, and textbook equality-sign advice.
- C11 supports `کیوں جے` in the worked directions and explanation of equal priority.
- C12 supports the Punjabi transition/cursor wording for the still-pending next section.
- C08 was read during source study and draft but currency is not part of this section; it did not manufacture an influence on the operations prose.

No native Punjabi speaker, mathematics educator or assistive-technology user certified this work. All specialist choices remain provisional.

## Translation and terminology decisions

- `order of operations` → “حسابی عملاں دی ترتیب”.
- `simplify an expression` → “جبری عبارت نوں سادہ کرنا”.
- `grouping symbols` → “اکٹھا رکھن والیاں علامتاں”.
- `parentheses / brackets` → “گول قوساں / چورس قوساں”.
- `equal priority` → “اکو ترجیح”.
- Existing A10 terms remain: جمع، تفریق، ضرب، تقسیم، طاقت، برابری دی نشانی، جبری عبارت، مساوات.
- Urdu bridge terms are separately labeled in original scaffolding. Urdu is not used as a substitute target language, and no Gurmukhi or mechanically transliterated Eastern Punjabi was introduced.

The canonical English mnemonic is deliberately retained:

`Please Excuse My Dear Aunt Sally.` / `PEMDAS`

The source English keywords and all 18 bold source-emphasis nodes remain traceable, including M/D and A/S and the p/e/m/d letters in the first two worked tables. Punjabi prose explains their meanings. A separately labeled original four-level summary states grouping symbols, exponents, multiplication/division left-to-right at equal priority, then addition/subtraction left-to-right at equal priority. It cannot be read as “always multiply before divide” or “always add before subtract.” The Indonesian file removes the mnemonic and substitutes four neutral priority levels; that comparison informed only the separately labeled original summary and did not replace canonical content.

## Source/comparison discrepancies and qualifications

1. **Image 006a malformed source alt.** Source key `fs-id1167836700561/alt` literally ends with `(4 + 3) ', 7`. Its faithful Punjabi source block preserves that malformed witness. Original-detail pixels and the Indonesian description show `(4+3)·7`. A separately declared original accessible override uses the pixel-correct expression, retains the faithful value in `data-source-alt`, and points to visible note `a10-007-006a-correction`.

2. **Image 006c implicit multiplication.** Pixels show red `(7)` followed by black `7`, with no visible multiplication dot. Canonical alt agrees. Indonesian inserts a dot. The target does not silently import that dot; original note `a10-007-006c-adjacency` explains adjacency as implicit multiplication.

3. **Expression versus equation.** Canonical alts `fs-id1167836282522/alt`, `fs-id1167833397265/alt` and `fs-id1167836622811/alt` call `4+3·7`, `4+21` and `3+12` equations even though the source cells/pixels have no equality relation. Faithful source blocks preserve “مساوات”. Separately declared original accessible alts use “جبری عبارت” and point to `a10-007-image-terms`.

4. **“Game of 24” direct-text note.** Note `fs-id1166425080552` is direct text with class `manipulative-math`, not a paragraph and not a live link. Canonical English has the agreement error “activity … give”. Punjabi naturally uses singular agreement while the exact source witness stays frozen. No activity rules, URL, executable runtime or availability claim is invented.

5. **Historical wording.** The source says mathematicians “early on established” the guidelines but supplies no date or person. The translation preserves its broad meaning. Original note `a10-007-history` explicitly avoids turning it into a dated or universal historical claim.

6. **Equality-sign advice.** The source advises not using an equal sign on each simplification line to avoid confusing expressions and equations. It is retained. Original note `a10-007-equals` limits this to the textbook’s display convention, not a universal ban on valid equality chains.

7. **Source spelling/descriptive looseness.** Worked summaries spell `parentheses` as `parantheses` and sometimes call the source table a figure. The exact English attributes remain in the frozen excerpt; translated summaries retain their intended description and the English mnemonic word/letter evidence. No new figure wrappers or numbers are invented.

8. **MathML comparison.** Canonical and Indonesian selections both have 21 MathML trees. Only source-order indexes 4, 5 and 6 differ: Indonesian localizes the explanatory English `mtext` in two worked `mtable` equations and replaces the English mnemonic `mtable` with a neutral priority table. All 21 canonical trees remain authoritative and exact.

## Mathematics, structure and renderer contract

- Preserve all 21 MathML trees exactly, in source order and LTR. There are 16 direct `{{math:n}}` placeholders and five standalone equation owners. No punctuation or text edit ledger is authorized.
- Preserve all 111 source IDs in original ancestor/order structure. Generated wrapper IDs must never replace or duplicate source IDs.
- Preserve all nine exercise/problem/solution associations and exactly three explicit source solution titles. Six Try It solutions may receive clearly generated UI headings but no invented source titles or answers.
- Preserve all 12 part labels in order. Ten short question/answer parts may receive source-derived inline grouping; the two one-token solution paragraphs `fs-id1167836283034` and `fs-id1167836522115` must keep their following table children outside any nowrap part wrapper.
- Preserve all three source newlines. The unusual cell `fs-id1167836375645/row/1/entry/2` owns two MathML trees, one `br`, then one media child; no child may escape its cell.
- Preserve all four LTR two-column source tables: 35 rows, 70 cells, 16 empty, zero `thead` cells. Do not invent headers/roles from visual placement or the source aria-label wording. Each table must scroll locally on narrow screens while keeping its initial Punjabi instruction column visible.
- Preserve question/answer arithmetic:
  - `4+3·7=25`; `(4+3)·7=49`.
  - `12−5·2=2`; `(12−5)·2=14`.
  - `8+3·9=35`; `(8+3)·9=99`.
  - `18÷6+4(5−2)=15`.
  - Try It answers `16`, `23`, `86`, `1`.
  - Worked nested expression `5+2³+3[6−3(4−2)]=13`.
- No answer, formula, grouping symbol, exponent, left-to-right priority rule or source numeral was invented or reordered.

## Images and rights/provenance limits

All 23 original-detail files were actually inspected. Their displayed sequences agree with the source worked steps; 006a and 006c are handled above. Exact declared bytes total 1,603,339. Dimensions range from 63×13 through 164×16, with the anomalously large but valid 602,520-byte `007b` retained exactly. Every source image element declares `image/png`, while every admitted source file is an actual JPEG. The renderer must preserve the source-declared MIME as trace metadata, serve `image/jpeg`, keep exact bytes/dimensions, leave geometry unmirrored, use natural width/local scroll and provide a fallback source-image link.

The existing authority manifest records byte/hash/blob identity; it does not add image-specific clearance. Existing audited A10 attribution and CC BY-NC-SA 4.0 policy remain binding subject to component-specific credits/restrictions. Absence of an image-specific credit is not described as a new clearance. No audit was repeated.

## Pre-render checks and remaining uncertainty

Before input freeze, the translation JSON parsed successfully and the source-bound fragments were checked for:

- exact 143-key order;
- exact math/child placeholder sequences;
- all three term IDs;
- all 18 source bold emphases;
- all three explicit line breaks;
- retention of every source prose numeral in its owner;
- exact English mnemonic phrase and source emphasis;
- faithful malformed/source-error values plus separately declared corrections;
- no Gurmukhi codepoints, replacement characters, prohibited bidi controls or other Unicode format controls;
- well-formed fragment HTML.

These are pre-render checks, not the independent final reader verifier. Isolated preparation, deterministic build, detached-mutation QA and browser review remain required. Native idiom, specialist terminology, teaching effectiveness, screen-reader behavior and the external historical/activity context remain uncertified.
