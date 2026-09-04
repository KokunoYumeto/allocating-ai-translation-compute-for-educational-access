# B10-001 — complete Chapter 0 input checkpoint

## Coverage and authority

This is the entire active canonical chapter **Introduction and Preliminaries**, not a sample: its opening title/introduction, full Sections 0.1 and 0.2, all seven active subsections, both investigations and all six exercises. Earlier book metadata and both full prefaces are covered by the separate frozen B10-frontmatter checkpoint; they are not silently skipped or duplicated here. The first outside source is `source/ch_logic.ptx`, `ch_logic`, **Logic and Proofs**. No later chapter is claimed complete.

The authoritative work is Oscar Levin's **Discrete Mathematics: An Open Introduction, Fourth Edition**, not OpenLogic. Actual instructions, durable goal, lock and source plan were read. Canonical Git commit is `82336dc87d77c3f18d2cdbc8ec1e74eb3ba38799`; the Indonesian comparison is `e94905932301e699b7c4d44e88ec54e972b886b6`. Both complete active English sections and their Indonesian counterparts were read. Both canonical SVG files were read as actual XML/path/label data. This is not a claim of rendered visual inspection.

The witness expands only the two active chapter XIncludes from pinned Git section text. It preserves comments, source attributes and all active children. Inactive older includes and the commented Statements subsection remain comments, not translated content. The raw composition is 37,881 bytes, SHA-256 `0e0f609c396780e9036d808a18c3f33dc4e1e7627304b5e26ffd4db1ce128185`. The reviewable witness adds exactly one final LF: 37,882 bytes, SHA-256 `22d106e2b8f6e456550c292ecbda0f40d528dec139462629a4d3c1de1c844721`. This difference is explicit, not described as byte identity.

The manifest records exact Git SHA-256/blob SHA-1 and separate checkout byte hashes for all six English/Indonesian PTX files. Selected checkout text is CRLF while Git blobs use LF; no source files were normalized on disk. Source macro/preamble/publication and next-chapter dependencies retain their own exact identities. The existing fourth-edition rights/attribution policy is retained from the frozen frontmatter manifest, including the already recorded upstream-root-license discrepancy. No new license/supply audit, image clearance, author endorsement or training-data use is claimed.

## Complete input inventory

- 157 ordered translation keys: 85 paragraphs, 10 titles, 2 footnotes, 2 image shortdescriptions, 6 feedback strings, 38 index headings, 2 index “see” strings and 12 table cells.
- 492 active source elements; 12 original XML IDs and 7 original label attributes with exact owner/ancestry/order.
- 105 exact TeX blobs: 102 inline `m`, 3 display `me`; **zero source MathML**.
- 65 source terms, 34 emphasis nodes (including nested emphasis), 11 quotation nodes and 2 alert nodes.
- 33 index entries: 29 inline placeholders and 4 standalone entries, preserving all nested heading/see content.
- Three ordered lists with 12 total items; three list-inside-paragraph child slots. Parent own prose does not duplicate descendants.
- One PreTeXt tabular, exactly 2 rows × 6 cells, six `col` nodes, first-column `right="minor"` and first-row `bottom="minor"`.
- Two footnotes, three cross-references, two source image nodes and two inert TikZ source blocks; no source figure/caption node.
- Six exercises: five empty ungraded response nodes; one exercise with three input slots and source numeric conditions **6, 10, 15**, each followed by its own `.*` fallback and feedback.
- 49 literal numeric occurrences in 31 prose/cell/description blocks, apart from exact TeX and setup metadata.

Source TeX, inline terms, references, index entries, footnotes, symbols and mixed children have local per-owner placeholders. A mathematical `n` inside the source `n-tuple` term remains inside that term's translation marker. No formula has been retyped into translated prose. The manifest includes every source node's own text, tail and ordered children, approved target-block hashes and exact source/target punctuation-position ledgers.

## Mathematical and source-fidelity decisions

1. **Discrete, not discreet.** The English dictionary pronunciation is retained LTR with its source midpoint placeholder. “ڈسکریٹ” is explained as separate/distinct mathematical objects; the unrelated English word `discreet` appears only in original guidance.
2. **Source questions remain questions.** The handshake, hot-dog, chest-message and five-town road investigations have no translator-invented answer key. The chest's conditional applies to either chest separately. The 26th contestant and both requested counts remain distinct.
3. **Integer/whole-number tension retained.** Canonical `integers (whole numbers)` stays “صحیح عدد (پورے عدد)”. The Indonesian omission is not copied. A separately labeled note distinguishes integers including negatives from the usual elementary nonnegative whole-number convention. Actual counts in that example are nonnegative.
4. **Natural-number convention is local.** This source explicitly includes 0. The Fibonacci example starts with first term 1, not term 0; generic sequence notation starting at 0 is not conflated with it.
5. **Set examples are not collapsed.** The early descriptions `A={3,5,7}` and natural numbers below 10 are alternative examples of description methods, not asserted equal. The later four displayed descriptions really do denote the same set; duplicate expressions do not create extra elements.
6. **Codomain is not range.** Allowable outputs, actual outputs and the image of an individual input remain distinct. The point-set example retains the source claim of a unique function, with an original qualification that the previously specified domain/codomain matter if codomain is part of function identity. The initial square-range example is read in its real-input context.
7. **Recursive “only way” is not universalized.** Source wording is retained for the stepwise recurrence. The original note explains its local computational context without inserting the missing result; the later source discussion itself introduces finding a closed formula.
8. **Sequences preserve order.** Ordered pairs, triples and tuples are not translated as unordered sets. Source Fibonacci and triangular-number formulas, all subscripts and starting indices are unchanged.
9. **Table data is exact.** Rows are `[n,1,2,3,4,...]` and `[a_n,1,3,6,10,...]`. The following closed formula is present in the source itself, not inferred from a finite table.
10. **Relation properties are separate.** Irreflexive, antisymmetric and transitive explanations retain the source quantifiers and implications. Antisymmetric is not called a synonym of asymmetric. The equivalence-relation list retains reflexive, symmetric and transitive.
11. **Graph convention is bounded.** The source's symmetric/irreflexive relation definition is retained. A labeled original note scopes it to simple undirected graphs; it does not prohibit loops/directions in all graph theory.
12. **Source spellings remain traceable.** English `metroids`/`POSets` and target “میٹروئڈ”/“پی او سیٹ” are retained; Indonesian `matroid`/`poset` is recorded separately. The likely `matroids` correction is explicitly an inference, not confirmed author intent.
13. **Fiction is not localized silently.** The chest inscriptions remain “strangely in English,” although their content is translated for reading. Indonesian changes the story's language; this was not imported. The old-lady-in-a-shoe footnote remains a complete source joke, with any explanation outside source prose.
14. **No imported comparison formula/paragraph.** The one Indonesian TeX change, `\text{ and }` → `\text{ dan }`, is not copied. The second graph's extra Indonesian detailed description is not a new canonical paragraph.

## Punjabi register and provisional terms

The draft uses Punjabi relative clauses, auxiliaries and instructions: جیہڑا/جیہناں، اسیں/تسی، آں/او/اے/نیں، لبھو، ویکھو، مُڑ سوچو، کیوں جے، دی بجائے. It is not mechanical Urdu substitution or Gurmukhi transliteration. Revision corrected reader-address/plural typos and unified domino tiles as **گِٹیاں**, with ڈبل چھے/نوّں/صفر/اک/دو labels. Identical final reflection prompts now have the same target wording.

Existing shared terminology was consulted read-only. No shared glossary was edited. New choices are provisional, not terminology authority:

| English | Target choice / distinction |
|---|---|
| set; element; function | سیٹ؛ رکن؛ فنکشن |
| sequence; ordered pair/triple | ترتیب وار سلسلہ؛ ترتیب وار جوڑی/تِکڑی |
| domain; codomain; range | ڈومین؛ کوڈومین؛ رینج — allowable and actual outputs distinct |
| image | تصویر — a function's output, not necessarily a drawing |
| cardinality | رکناں دی گِنتی |
| union; intersection; subset | ملاپ؛ سانجھا حصہ؛ ذیلی سیٹ |
| set comprehension / builder notation | شرط نال سیٹ بیان کرن دا طریقہ / سیٹ بناؤن والی علامتی لکھت |
| finite; infinite | متناہی؛ بے انت |
| closed formula; recursive definition | بند فارمولا؛ بازگشتی تعریف, separately explained in plain Punjabi |
| binary relation | دو رکنی رشتہ |
| irreflexive; antisymmetric; transitive | غیر انعکاسی؛ ضدِ تشاکلی؛ تعدّی |
| reflexive; symmetric; equivalence relation | انعکاسی؛ متشاکل؛ مساواتی رشتہ |
| vertex; edge; graph | راس؛ کنارہ؛ گراف |
| multiset | کثیر سیٹ |

### Actual canon consultation

Three separate receipts record actual full local passage reads at draft, revision and QA stages; these are not receipts merely for file existence.

- R1: C01 line 28 supports passive ability; C02 line 39 reader-facing modality; C03 line 45 ترتیب وار; C04 line 35 plural/counting agreement.
- R2: C05/C06 line 27 purpose versus contrast, تاں جے and دی بجائے; C07 line 33 ordinal/location phrasing.
- R3: C09 line 52 reminders; C10 line 25 explicit qualifications; C11 line 38 کیوں جے reasoning.

Ten examples informed draft/revision; eight were reread at final QA. These essays support Punjabi register, not specialist mathematical terminology or their historical/political claims. Passage/local-source hashes and stage-specific application are in the receipts. Native-speaker/educator review remains outstanding.

## Renderer handoff — no build in this task

All 105 math strings use only `\N, \cdot, \frac, \ge, \in, \infty, \ldots, \lt, \ne, \st, \text, \to`, plus ordinary braces/superscripts/subscripts. Custom definitions are `\N=\mathbb N` and `\st=:`; the complete bookinfo macro text is retained **inert**. A canonical generated-assets filename search returned no math/knowl/mml-named precomputed formula artifacts. Formula delivery therefore still needs a separate renderer decision. Do not execute source TeX/TikZ or silently change raw `\text{ and }`.

Use a valid paragraph-equivalent container around mixed ordered lists; keep source `me` display math in the correct text position. Do not treat this as CNXML or flatten mixed children, index entries or footnotes. Index/response UI and inherited rename labels are separately marked renderer metadata, not invented source paragraphs.

Cross-reference labels bind to local Section **0.2**, future Chapter **4** and future Chapter **2**. The latter two are explicitly “not yet included in Punjabi”; they must not produce dead local links or imply a completed chapter.

The canonical graph SVGs are both **76×73**, source width **20%**, with no external references:

- `graphs-7sum.svg`: SHA-256 `27ac010ecf130314dd92dd7ffa74fff6b38002b83ee90025a316b80d24af98ab`; edges {1,6}, {2,5}, {3,4}.
- `graphs-evensum.svg`: SHA-256 `d59d64e902a9233ea4826db6bebf1e2ccd8a0162aeb29ed449e2f0e1117aa0c1`; edges {1,5}, {2,6}, {1,3}, {4,6}, {2,4}, {3,5}.

The Indonesian rs SVGs are byte-identical; its web variants are 77×75 and different bytes. Copy only pinned canonical Git bytes if/when a build is authorized. Do not mirror/redraw them. The first original ID is on `image`; the second `graphs-evensum` label belongs to `latex-image`. First-image shortdescription and description/p contain the same source text and both are retained. The second source has only shortdescription. Any additional detailed accessible text is the separately labeled original description, with raw source descriptions still available. Crossings do not create extra vertices.

RTL prose requires LTR formulas, table/numeric runs, English and source dictionary pronunciation. Source ASCII range hyphen `2-3`, decimal `1.32419`, ellipses and raw TeX remain distinct. Prose punctuation is localized; the manifest records exact source and target punctuation offsets, including the source final graph-reference sentence's lack of terminal punctuation.

### Bounded converter source study, not implementation

There are **78 distinct raw TeX strings** across the 105 source owners. A small local, nonexecuting converter is feasible only with an explicit whitelist: simple identifiers/numerals, visible fences, operators, sub/superscripts, the observed two-argument fraction, the 12 named commands above and exact English text content. It must preserve raw TeX and inert macro evidence, consume every source character, fail on unknown syntax, and mark MathML as a derived rendering rather than canonical source MathML.

Important traps are the intentionally mixed interval fences `[0,\\infty)`, full-base grouping in `(a_n)_{n\\ge 0}`, the complete `n-1` subscript in `f_{n-1}`, source spaces inside `\\text{ and }`, and an explicit ASCII-TeX-minus to true-minus presentation ledger. Source prose punctuation stays outside the math owner.

Independent QA must not call the converter to create its expected results. Use reviewed expected tree descriptors for all 78 unique strings bound back to all 105 owners, or a genuinely independent checker with complete reviewed fixtures. Check full tree hierarchy, glyph/token order, fraction/script/fence binding, source reversibility and detached wrapper/owner/operator/whitespace mutations. This study is recorded in the scope plan; implementation awaits the parent's bounded assignment.

## QA and reproducibility

The first complete input run passed **2,925 checks** and rejected **35 detached mutations**. The frozen replay program is stored as text in `plans/B10-001-scope.json` under `input_qa.program`; its SHA-256 is `c709061c0f35854341aba8faa2a203ca224e9cc28b74ef698941b2038a6413c9`. It executes only locally authored verification code, never upstream code, and never writes files. Replay from the workspace root:

```powershell
python -B -c "import json,pathlib;exec(json.loads(pathlib.Path('languages/pnb-Arab-PK/plans/B10-001-scope.json').read_text(encoding='utf-8'))['input_qa']['program'])"
```

Checks independently rederive source slots and raw TeX from pinned Git blobs, compare the full witness/active tree/metadata/owner ledgers, verify exact table and source answer conditions, inspect all target inline event trees and literal numerals, enforce LTR isolation, preserve image/source-description identity, and check original/source separation and actual canon passages.

Detached mutations cover missing/extra/reordered keys, table/decimal digits, TeX order/whitespace/value, math moved out of a term, nested emphasis, removed bdi, term/index/list/footnote markers, original IDs/ancestry/structural own text, answer order/value and feedback, image hash/owner/alt/Indonesian-only content, unavailable-reference claims, punctuation ledgers, correction erasure, function-conclusion injection, duplicate prose, TikZ/macros, source boundary/LF and rights metadata.

Structural/numeral/inline mutations explicitly run with approved-text seals disabled. Arbitrary prose and original-bridge meaning changes are drift guards against the reviewed text, **not** an automatic proof that every translation is semantically correct. No rendered shaping, mobile layout, MathML conversion, exercise interaction, screen-reader behavior, native review or independent educator review is claimed here.

Final deterministic replay: two completed fresh-process runs of the frozen inputs returned identical results and hashes: **2,925 checks / 35 rejected detached mutations** in each. Witness SHA-256 is `22d106e2b8f6e456550c292ecbda0f40d528dec139462629a4d3c1de1c844721`; manifest `98848df0ae9bda7cea41e05cb42dfbadcda9181588beab3a4a5637c9be239443`; translation `6581cc29aa051220f91ec342c5642d08ff16203d5292b29948fa3df9595ea0cd`. Full B10 and the entire five-work assignment remain active.
