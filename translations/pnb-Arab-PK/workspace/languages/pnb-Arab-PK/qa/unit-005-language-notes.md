# PNB-005 — tables translation and source notes

Date: 2026-08-30. Target: Western Punjabi in Shahmukhi (`pnb-Arab-PK`). This is a bounded checkpoint in the continuing A10/A20/A30/B10/B40 assignment, not completion of a module or book. Native-speaker and mathematics-educator review remain pending.

## Source boundary and witnesses

Read the actual English and Indonesian section `fs-id1165137804204`, “Representing Functions Using Tables,” from the acquired `m49301/index.cnxml` files. The canonical English source is `downloads/upstream/osbooks-college-algebra-bundle/modules/m49301/index.cnxml`, commit `789b54099106b071d1d32bfcee454fed72eb4768`. The comparison is `downloads/extracted/A30/repo/source/modules/m49301/index.cnxml`. The English remains authoritative; Indonesian `dan` in display mathematics is not substituted for the English `and`.

The selection is exactly one complete section, including its introduction, Tables `Table_01_01_03` through `Table_01_01_09`, how-to, `Example_01_01_05`, and the complete Try It `ti_01_01_03`, ending with answer paragraph `fs-id1165137844279`. Stop before section `fs-id1165137503241`, “Finding Input and Output Values of a Function.” The selected section is the last child of `fs-id1165133394710`; the next section is outside that parent, not its next direct sibling. Source lines 565–903 contain the selection, but line 903 also closes the parent and starts the next section. The excerpt was made from the verified complete XML element, not a raw line slice.

`prepare_text_unit.py` only accepts units 003/004 and assumes a following direct sibling. It was read but not run or edited. The small excerpt and manifest were created with `apply_patch`. XML serialization changes namespace placement/self-closing syntax but retains element/attribute structure, all internal text and whitespace, tables, IDs, mathematics, and order. No source content was silently normalized.

Byte witnesses recorded in `source-excerpts/manifest-005.json`:

- Canonical checkout SHA-256: `f35932b5b8107fd527d50547adf00d3981860be5d6e981c1238041369b207612`.
- Pinned LF witness `downloads/m49301.cnxml`: `81115d90dd1d9781e65844526bbbfbea638cc6fd515c623c4d535bf3bd0e37e3`.
- The checkout contains 4,801 CR bytes; removing only those gives the exact pinned LF witness. The differing byte hashes do not indicate differing prose or mathematics.
- Indonesian comparison SHA-256: `67678da7d3faa988d0c42a63ef15f140a2c0478610cd1fadc499fb749d55c77a`.
- Frozen `source-excerpts/unit-005.cnxml`: `d26ac1f0ea21679db4534cc8ff8513e3531cbebca095dbd1978e9752e4b38c1f`.

No figure, image, media node, footnote, or separately referenced component occurs in this selection. No new component-notice file or asset was created; existing book attribution remains applicable. This is not a new supply/license audit.

## Coverage and schema

The JSON has 41 ordered source-block strings, 34 retained source IDs, seven source tables, 13 ordered source-link placeholders, and 12 ordered MathML placeholders. Two standalone equations contribute two further MathML trees, for 14 total. Empty equation labels require no translated block. No child placeholder is needed.

Table keys use global row indexes, including `thead`. The first three tables have their header entries in column one; the last four have their headers in row one. Both pure-MathML headers in `Table_01_01_04` have explicit `/row/1/entry/1` and `/row/2/entry/1` keys with `{{math:0}}`; they must not fall through to plain flattened cell text.

| Source table | Actual rows × columns, including headers | Input/output data and source conclusion |
| --- | --- | --- |
| `Table_01_01_03` | 2 × 13 | Month numbers 1–12; 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31 days; function |
| `Table_01_01_04` | 2 × 6 | (1,8), (2,6), (3,7), (4,6), (5,8); function |
| `Table_01_01_05` | 2 × 8 | (5,40), (5,42), (6,44), (7,47), (8,50), (9,52), (10,54); not a function |
| `Table_01_01_06` | 4 × 2 | (2,1), (5,3), (8,6); function |
| `Table_01_01_07` | 4 × 2 | (–3,5), (0,1), (4,5); function |
| `Table_01_01_08` | 4 × 2 | (1,0), (5,2), (5,4); not a function |
| `Table_01_01_09` | 4 × 2 | (1,10), (2,100), (3,1000); source answer “yes” |

All seven English table summaries accurately describe their table dimensions and ordered pairs. Translate them faithfully; no accessibility-summary override is needed. The plain-text summary attributes cannot carry HTML isolation. Visible numbers/variables in translated prose and the original bridge use `bdi dir="ltr"`; the parent renderer must preserve all numeric cells as LTR, retain source alignment, and keep tables horizontally scrollable from their first column.

## Actual canon consultation and influence

The canon index and actual surrounding prose windows were read using the existing `read_canon.py`, with already acquired R1/R2/R3 HTML witnesses. No new source was downloaded. Timestamped receipts, not overwritten pilot receipts, are:

- Source analysis: `canon/receipts/PNB-005-next-unit-20260830T203455628227Z.json`, C01/C03/C04/C07/C09/C10/C11.
- Draft: `canon/receipts/PNB-005-draft-20260830T213049748989Z.json`, C01/C03/C04/C07/C09/C10/C11, read before composing the translation.
- Revision: `canon/receipts/PNB-005-revision-20260830T213614328702Z.json`, C01/C04/C07/C09/C10/C11, read alongside the complete saved draft.
- QA: `canon/receipts/PNB-005-qa-20260830T214032550151Z.json`, C01/C03/C04/C07/C09/C10/C11, read against the revised wording before the source-bound checks below.

The script's receipt `application` strings are older index annotations, sometimes naming PNB-001. They establish which actual passages were displayed, not the specific new decisions; this note records the PNB-005 application:

- C01/R1's `بیان کیتی جا سکدی اے` informed Punjabi ability/passive constructions in the table/function discussion. Agreement is adapted to the current subject, not mechanically copied from the essay.
- C03/R1's `ترتیب وار` informed ordered-pair summary wording. The passage is ordinary sequencing prose, not proof of a settled mathematical term.
- C04/R1's plural/quantity prose supported `قدراں ... نیں`, `جدولاں`, and Punjabi agreement. Revision replaced Urdu-inflected `حالتوں` with `حالتاں` in the first paragraph.
- C07/R2's ordinal-location passage, including `چار کالماں وچ`, supported first/second row/column language and `کالماں`. It does not establish table-specific educational terminology.
- C09/R3's reminder wording supported `چیتے رکھو` in the month and notation paragraphs and original bridge.
- C10/R3's explicit qualification supported separating explanations of source limitations from the faithful source translation.
- C11/R3's `کیوں جے` supported reason-giving for failure of the function condition. Its `دوہاں حصیاں` also supported changing the original bridge's Urdu `دونوں` to Punjabi `دوہاں`.

These remain three prose essays by one author, not specialist mathematical authorities. Their historical claims do not supply any table data. `جدول`, `قطار`, `کالم`, `صحیح عدد`, `فنکشن دی علامتی لکھت`, and `ترتیب وار جوڑی` remain explicit provisional academic/compositional choices, alongside the existing input/output/function ledger. In particular, `صحیح عدد` is glossed with English `integer` in the original bridge; this scope only uses positive month numbers and does not attempt a complete definition of integers.

The revision also removed an accidental zero-width character from `مثالاں`, isolated the visible `n` and `Q` in a bridge link, and changed a vague Table 07 bridge label to “the second table of the worked example.” These are local linguistic/RTL edits, not source-data corrections.

## Mathematical and source-presentation decisions

- Table 03 concerns a fixed non-leap year. Its domain consists of the month numbers 1–12, not month names or years. February remains 28; the original bridge discloses the fixed-year scope without adding leap-year inputs.
- Function names are local to their examples. Month-table `f(2)=28` differs from Table 06's `f(2)=1`; Table 04's `g(4)=6` differs from Table 07's `g(4)=5`. The original bridge links each expression to its own actual table. No source variable is renamed and no global function map combines them.
- Table 05 records multiple children's ages and heights. The conflicting age-5 outputs are 40 and 42 inches. The source statement is not generalized into a claim about every possible age-height model or one particular child's growth. Inches remain inches; no unit conversion is introduced.
- Table 08 can still be written as an ordered-pair relation. The source's “cannot be expressed in a similar way” means it is not a single-output-per-input function. That clarification is clearly original support, not a silent rewrite of the translated source statement.
- Table 09's source answer remains only `ہاں۔`. The original bridge supplies the uniqueness reason separately. Finite values do not determine a unique algebraic rule or outputs beyond the displayed inputs; no exponential rule or extrapolation is asserted.
- Table 07's actual cell uses en dash `–3` (U+2013), its English summary uses hyphen-minus `-3` (U+002D), and its MathML uses minus `−` (U+2212). Preserve all three source spellings in their respective places and explain them separately. Indonesian's summary uses true minus; that is not silently substituted for English. Numeric comparison normalizes these signs only in memory, not in the source or translation witnesses.
- Both standalone source equations retain their internal English `and` plus NBSP, mathematical commas, function names, parentheses, and numbers. The original bridge explains `and` as `تے`. It also glosses the source prose abbreviation `in.` as inches.
- Inline slots 0 and 3 of `fs-id1165135191568` end in English periods, respectively an `mo` after `Q=g(n)` and an `mtext` after `Q`. Punjabi syntax puts the predicate after each symbol, so the renderer must relocate only these terminal prose periods with reversible source-text ledgers. The frozen CNXML stays unchanged. Reconstructing the exact MathML after rendering is a separate parent QA responsibility.
- The source question uses singular “which table” although the solution accepts Tables 06 and 07. Punjabi preserves the source question and its two-table answer without asserting that exactly one choice must be correct.

The original bridge has `data-origin="original-bridge"` and an explicit Punjabi heading/introduction separating it from the translation. Its orientation guidance and qualifications are not presented as missing source prose.

## Read-only draft QA and handoff

An in-memory, non-building Python/XML check passed **315 checks** after the revision. This is a draft inspection, not a permanent rendered-reader test suite. It checked:

- Exact canonical-subtree/excerpt equality for tags, attributes, all internal text/whitespace and ordered children; all 34 source IDs; selected-parent/final-descendant/following-section boundaries; recorded excerpt, English, LF-witness and Indonesian hashes.
- Exactly 41 derived source keys in source order, with no missing/extra keys; each MathML/link placeholder's count/order; no child placeholders; all 13 source targets local; 14 MathML trees and two equations; absence of images/footnotes.
- Every JSON/HTML fragment parsed, every source-block prose number outside mathematics retained in order, all visible Latin letters/digits in translated prose/bridge LTR-isolated, and zero Gurmukhi, replacement characters, forbidden bidi controls or accidental zero-width characters.
- Seven source table shapes and every ordered pair in both source and translated summaries, normalizing negative signs only for in-memory numeric comparison. Input uniqueness gave function results true/true/false/true/true/false/true in table order.
- Both standalone equations matched their own actual table pairs; their `and`/NBSP nodes were retained; all four displayed original-bridge equations matched their own linked table and source function symbol; all bridge links resolved to selected source IDs.

An independent read-only reviewer also compared all 41 blocks with the canonical section and frozen excerpt, verified the 12 math/13 link placeholder counts and order, parsed the fragments, and checked function classifications, local function-name reuse and negative-sign distinctions. It reported no material fidelity, mathematics, omission or draft-level RTL issue. It did not build the reader or certify the target language.

The checked translation SHA-256 is `a1a7e8435127b38386c0e42af257df310b562f2fb3e5fc25f90de10118d545bf`. No build, rendered-DOM mutation tests, visual layout, keyboard scrolling, screen-reader pronunciation or native-language approval is claimed by this drafting note. The parent owns shared renderer integration, final reproducible structural receipts, desktop/mobile checks and subsequent integration. A wide 13-column month table and both long equations need narrow-screen inspection.

Owned deliverables are this note, `translations/unit-005.json`, `source-excerpts/unit-005.cnxml`, and `source-excerpts/manifest-005.json`. Canon-reading receipts are the explicitly requested small workflow outputs. No shared renderer/CSS/terminology/provenance aggregate, other unit, download, bulk asset, deletion or commit was changed by this draft handoff.
