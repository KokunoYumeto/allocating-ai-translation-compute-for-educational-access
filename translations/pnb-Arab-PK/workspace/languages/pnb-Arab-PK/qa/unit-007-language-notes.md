# PNB-007 — formulas, tables and graphs

Date: 2026-08-31 local time; canon receipt timestamps below are UTC on 2026-08-30. Target: Western Punjabi in Shahmukhi, pnb-Arab-PK. This is a larger translation checkpoint within the full A10/A20/A30/B10/B40 assignment. It completes the remaining three skills under the already-started input/output section, not the complete m49301 module or any assigned book. Native-speaker, mathematics-educator and assistive-technology approval remain pending.

## Exact source boundary

Read the actual canonical English and Indonesian m49301 sources before choosing scope or drafting. English checkout is downloads/upstream/osbooks-college-algebra-bundle/modules/m49301/index.cnxml at commit 789b54099106b071d1d32bfcee454fed72eb4768. Indonesian comparison is downloads/extracted/A30/repo/source/modules/m49301/index.cnxml.

This unit contains all three remaining consecutive direct children, positions 5–7, of fs-id1165137503241, “Finding Input and Output Values of a Function”:

1. fs-id1165137591827, “Evaluating Functions Expressed in Formulas”: complete section, source lines 1603–1982.
2. fs-id1165137648450, “Evaluating a Function Given in Tabular Form”: complete section, source lines 1983–2219.
3. fs-id1165135696152, “Finding Function Values from a Graph”: complete section, source lines 2220–2364.

The final selected descendant is fs-id1165137598287, the last Try It answer. The next source cursor is fs-id1165135422920, “Determining Whether a Function is One-to-One,” opening on line 2365. The outer title and two introductory paragraphs already translated in PNB-006 are not duplicated.

The excerpt was constructed from the actual three complete XML elements with apply_patch. Source text, tails, attributes, IDs, MathML and internal child order are retained. Namespace placement and empty-element serialization can differ. The shared prepare_text_unit.py was read but not run or edited: its unit choices and image-copying workflow did not match this owned-files-only drafting scope.

## Witnesses and inventory

Verified SHA-256 values:

- Canonical CRLF checkout: f35932b5b8107fd527d50547adf00d3981860be5d6e981c1238041369b207612.
- Pinned LF downloads/m49301.cnxml: 81115d90dd1d9781e65844526bbbfbea638cc6fd515c623c4d535bf3bd0e37e3. Removing only the checkout's 4,801 CR bytes produces this witness exactly.
- Indonesian comparison: 67678da7d3faa988d0c42a63ef15f140a2c0478610cd1fadc499fb749d55c77a.
- Frozen source-excerpts/unit-007.cnxml, hashing after only CRLF-to-LF normalization: c1827e4cd0938a646b0a0b62c035b691292e0a649f93a7191507e56cf236b407.
- source-excerpts/manifest-007.json: 177bab81ed6e266f68c1f18837b96c2558469dd1830147a61139a26dc4dc34ae.
- translations/unit-007.json at drafting handoff: db56a49067d731c94d6c58e9eead9513cbf01c15598b20e24830213f041cad3d.

The source-derived inventory is 72 ordered translation-block keys, 84 identified source nodes, 83 MathML trees, four display equations, three CALS tables, three images, six source links, one footnote, three inline terms, and three immediate structural-child placeholders. The MathML split is 79 own placeholders plus four equations. The 79 own placeholders include four MathML row-header cells in Tables 11 and 12.

Per-skill counts are 23/35/14 translation blocks, 37/26/21 source IDs, and 37/23/23 MathML trees. All four examples, Example_01_01_09 through Example_01_01_12, and all three Try Its are complete. There are seven exercise/problem/solution pairings. Example 09 has an Analysis commentary after its solution; its exercise is not a two-child-only container. The formulas section also includes the full Q&A.

Child placeholders are exactly the footnote in fs-id1165135186427 and Figures 008/009 inside the two solution items of fs-id1165137871522. The figures must remain in their original list items. The graph's second solution item owns fourteen MathML placeholders; its nested figure owns none.

## Actual canon consultation

Read the displayed surrounding passages from the existing readable R1/R2/R3 HTML witnesses with read_canon.py. No new reference was downloaded. Receipts:

- canon/receipts/PNB-007-next-unit-20260830T230304108428Z.json: C01/C02/C03/C04/C06/C07/C09/C10/C11/C12, during source analysis.
- canon/receipts/PNB-007-draft-20260830T231045082880Z.json: the same ten loci, before drafting.
- canon/receipts/PNB-007-revision-20260830T232155944137Z.json: C01/C02/C04/C06/C07/C09/C10/C11/C12, during the full saved-draft review.
- canon/receipts/PNB-007-qa-20260830T232605954577Z.json: C01/C02/C03/C04/C06/C07/C09/C10/C11, before final numerical and source-binding checks.

Actual influence:

- C01's سکدی اے construction supports Punjabi ability/passive statements such as لکھیا جا سکدا and یاد رکھ سکدی اے. This is a grammatical-register use, not evidence for the animal-memory claim.
- C02's reader-directed register supports لبھو، لکھو، کڈھو and the distinction between an instruction and the conditional “want to.” The Q&A draft was revised from ambiguous چاہیئے to چاہندے ہوئیے.
- C03 supports the compositional ordered-sequence wording in summaries. It does not certify ترتیب وار جوڑی as a standardized mathematical term.
- C04 supports plural agreement in قدراں، جدولاں and کالماں. Revision corrected the summary's singular کالم نوں to کالماں نوں.
- C06 helps distinguish alternative representations and replacement from logical implication. The prose uses ایتھے / دوجے پاسے / دی شکل وچ rather than treating a representation change as an iff claim.
- C07's ordinal/location construction informs first/second row and axis-reading language.
- C09 informs the reminders about source scope, domain/range and locally reused function names.
- C10's explicit qualification informs the separate original notes on nonzero division, the circle counterexample, dated animal data, the incorrect summary and the incorrect alt. These qualifications are not silently inserted into source-labeled translation.
- C11's reason-giving and دوہاں support the result explanations. Revision replaced a bridge occurrence of Urdu دونوں with دوہاں.
- C12's transition register informs ہُن اسیں in the move from subtracting to solving for y; it was not mechanically inserted in every paragraph.

The first formula paragraph's agreement was also revised to a complete “a formula involving the input quantity” construction. The script's older application labels sometimes name PNB-001; those are index metadata, not claims that this unit repeated that pilot's work. The canon remains three prose essays by one author, not specialist mathematics authority. No native fluency or scientific-source certification follows from these readings.

## Mathematical fidelity and original precision notes

- The first relationship is 2n+6p=12, giving p=f(n)=2−n/3. All five rows of its MathML derivation, including empty layout tables, NBSP strings and English instructions, remain in the witness. The original bridge translates “expression involving n,” “Subtract 2n from both sides,” and “Divide both sides by 6 and simplify.”
- The how-to permits multiplying or dividing by “the same quantity” without a nonzero condition. The faithful source wording remains. An explicitly original note states that equivalent multiplication/division steps require a nonzero quantity; division by zero is undefined and multiplication by zero can erase the equation's information.
- For x²+y²=1, x=0 gives two distinct outputs y=±1 and therefore disproves the whole relation being y=f(x). The original note does not claim two distinct outputs at every x: the endpoints x=±1 give only y=0, and no real y exists outside −1≤x≤1. Choosing one square-root branch would restrict the relation, not represent the entire source circle.
- The Try It equation x−8y³=0 has answer y=f(x)=∛x/2. The source mroot degree 3 and fraction denominator 2 remain exact. The original example x=−8, y=−1 explains real cube roots; no complex principal-root convention or accidental square root is introduced.
- The Q&A is about x=y+2^y, not x=y+2y. Over the reals, y+2^y is continuous, strictly increasing and has range all real numbers, so its inverse is single-valued. The source's closing “cannot be written explicitly” is qualified in the original note by its preceding “no simple algebraic formula,” not expanded into a prohibition on all special notation. No new named special function is introduced.
- Each example reuses f locally: the linear formula, cube-root answer and graphed function are not one definition. The tabular g is also not the square-root g from PNB-006. Source letters are not renamed.
- The draft uses descriptive Punjabi فنکشن دی قدر کڈھنا and فنکشن دی مساوات حل کرنا, with English/Urdu bridges. ضمنی، صریح، منحنی، راس، محدد، افقی محور، عمودی محور and مکعب جذر remain provisional educational choices requiring a Punjabi mathematics educator. The limited literary canon is not cited as authority for them.

## Table data and source discrepancies

Table_01_01_10 is exactly six rows by two columns, including its header row. Actual row pairs are Puppy/0.008, Adult dog/0.083, Cat/16, Goldfish/2160, Beta fish/3600. The five ordinary animal-category labels are translated, not treated as proper names. Their exact translation keys are Table_01_01_10/row/2/entry/1 through row/6/entry/1.

The original English summary incorrectly gives goldfish 2100. The numeric cell and P(goldfish)=2160 formula both give 2160. The Indonesian summary already agrees with the actual cell. The draft preserves the faithful incorrect summary in source_blocks and supplies the corrected value through table_summary_overrides. The reader must retain the former in data-source-summary and use only the corrected summary as aria-label. The mismatch is explicitly disclosed in the original bridge; no original numeric table cell is changed.

Tables 11 and 12 are both two rows by six columns. Their complete rows are n,1,2,3,4,5 and g(n),8,6,7,6,8. The source MathML header cells use their exact row/entry keys and preserve emphasis. Table 12 is an unnumbered repetition with an empty label; no published or local number is invented for it. Its original class/label remain in the witness and manifest references include only Tables 10 and 11.

The renderer contract explicitly lists the five translated_table_data_cells: they remain td with RTL text, not th merely because they have translation keys. Other keyed table cells are actual column/row headers. Numeric cells remain unchanged LTR values, including 0.008 and 0.083 with decimal points. Source-centered cell alignment and original row/column order must remain.

The animal-memory paragraph is a dated source example, not newly verified zoology or advice about pet care. The original before-note warns readers before that story. The source footnote URL remains http://www.kgbanswers.com/how-long-is-a-dogs-memory-span/4221590 and the original access date remains 3/24/2014, not the comparison edition's reformatted date. The footnote has its own key; the renderer retains its original source ID in the inline superscript and links to a separate -text endnote with a backlink.

The original bridge explains that 0.008 hours is 28.8 seconds, not exactly 30; 0.083 hours is 4.98 minutes. Month-to-hour conversion needs a calendar assumption. No table value is “corrected” to a guessed biological value. The English source spelling beta fish is preserved as the English label in the key rather than silently respelled. The source's singular “range is a real number” remains faithfully translated; the original note distinguishes the five-value range set from the type of each output. “Paragraph or function form” is explained as a contrast with formula form, without implying that a table cannot itself specify a function.

## Images and accessible corrections

All three original images were opened at original detail. They are byte-identical to their Indonesian comparison assets; no generated/redrawn image was substituted.

| Source file | Dimensions | SHA-256 |
| --- | --- | --- |
| CNX_Precalc_Figure_01_01_007-985e.jpg | 487 × 445 | 02cde0483837d9e0327b2d969c153dc4e05bb19f2edcab5ceff627bdab00013d |
| CNX_Precalc_Figure_01_01_008.jpg | 361 × 339 | bbf8ad74f4c6abe5882a3bf246a4834a3aa1d72e638b4199a40d51941a95efa3 |
| CNX_Precalc_Figure_01_01_009-4a94.jpg | 487 × 445 | cf77d80db8d2616f63ef758adbccd016eac20df35a3e1699c2d4da131820736b |

Source figure IDs 007/008/009 and media IDs fs-id1165137705894, fs-id1165135675165 and fs-id1165137469773 are retained. Manifest local figure labels are 1.1.7–1.1.9. Parent integration owns copying the unchanged assets and carrying forward the exact existing component-notice rows; this drafting task did not repeat a supply/license audit or create a separate notice file.

The actual images all show an upward-opening parabola with vertex (1,0). Figure 008 marks (2,1) and f(2)=1. Figure 009 marks (−1,4) and (3,4) on y=4. Its English alt incorrectly says vertex (0,1); the Indonesian alt correctly says (1,0). The faithful English-source alt translation remains in source_blocks; image_alt_overrides corrects the accessible description. The renderer must preserve the former in data-source-alt, use the corrected alt, and attach aria-describedby plus a visible advisory link to original paragraph representations-alt-vertex.

The earlier two source alts loosely say “positive” and “centered.” Their faithful translations are retained too; the accessible alternatives use upward-opening/vertex based on the images, with the original explanation at representations-alt-wording. This is a disclosed wording clarification, distinct from the numeric vertex reversal. image_alt_note_ids maps the three media IDs to those two stable original-note IDs.

The original bridge supplies a graph-reading key and all given values/solutions. It does not add an asserted source formula for the parabola. A parabola-model arithmetic check was used only as consistency evidence alongside actual pixel inspection.

## Reversible numeric-token punctuation handoff

The witness retains every token below exactly. Slot numbers are zero-based own MathML positions, excluding nested block children. Only terminal sentence punctuation may be relocated in a reversible old/new/path ledger. Numeric meaning, nodes and internal punctuation must remain.

| Owner | Slot | Token/tag |
| --- | --- | --- |
| fs-id1165137584852 | 2 | mn 2160. |
| fs-id1165137653327/item/2 | 0 | mn 6. |
| fs-id1165137725812/item/1 | 2 | mn 3. |
| fs-id1165137725812/item/1 | 4 | mn 7. |
| fs-id1165137725812/item/2 | 3 | mn 4. |
| fs-id1165137604039/item/2 | 0 | mn 4. |
| fs-id1165137871522/item/1 | 3 | mn 1. |
| fs-id1165137871522/item/2 | 0 | mn 4, |
| fs-id1165137871522/item/2 | 3 | mn 4: |
| fs-id1165137871522/item/2 | 6 | mn 4: |
| fs-id1165137871522/item/2 | 8 | mn 3. |
| fs-id1165137871522/item/2 | 12 | mtext 3, |
| fs-id1165137695208 | 0 | mn 1. |

This is twelve mn exceptions and one combined numeric mtext exception. Do not broadly strip numeric decimal points, commas or colons. Existing terminal standalone mo/mtext punctuation also needs the established edge-only ledger. Internal coordinate commas, closing parentheses, negative signs, English text including goldfish/and, NBSP layout strings and the mroot/fraction structure remain. The four MathML mtable structures include two nested empty tables, and English instructional cells are retained. Empty nodes are source layout, not permission to flatten the derivation.

## Read-only drafting QA and remaining workflow

The in-memory source/draft inspection passed 554 checks: exact three-subtree boundary, hashes/newline equivalence, 72 keys in order, 84 IDs, all 79/6/3 math/link/child slots, plain-prose numeric order, three inline term IDs, source emphasis, part labels, Unicode, LTR runs, table shapes/data-key roles, seven exercise pairings, three original image hashes/dimensions, correction fields, footnote URL/date and local links.

A further 55 in-memory arithmetic/bridge/correction-link checks passed. They derive the linear and cube-root expressions from the actual source MathML; test negative, zero and positive inputs; verify the circle counterexample and endpoints; derive both tabular g mappings and their supplied answers; compare goldfish data to its formula; check hour conversions; and bind all image note IDs. The scratch arithmetic parser needed parentheses around negative substitutions and removal of a terminal source sentence comma before numeric evaluation; no translation/source data was changed to satisfy those diagnostic fixes.

Finite arithmetic samples are not universal proofs. The real inverse's uniqueness follows from strict monotonicity/continuity and endpoint behavior, not the sampled grid. Graph arithmetic checks are consistency checks against independently inspected source pixels, not extraction of a source-provided formula.

No reader build or visual review was performed by this drafting task. The parent has independently implemented renderer support, copied unchanged assets and is reviewing source fidelity and rendering. Source-bound saved reader QA, detached-DOM mutations, deterministic builds and final visual verification remain separate steps. At this drafting handoff, owned edits are only the unit-007 excerpt, manifest, translation, this note and the requested canon receipts. No shared script, shared ledger, aggregate provenance, image, downloaded archive or existing earlier-unit translation was edited by this task.
