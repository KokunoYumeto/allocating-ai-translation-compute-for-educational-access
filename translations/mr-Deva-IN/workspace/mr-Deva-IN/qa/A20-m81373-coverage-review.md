# A20:m81373 complete-source coverage reconciliation

2026-08-31. Scope: the full pinned English module **Relations and Functions**, reconciled with the current source XML of MR-BRIDGE-001–010. This is a structural/content-obligation audit, not a new translation, complete mathematical rereview, browser QA, or native-speaker approval. Only this report and `tools/test_m81373_coverage.py` were created. The existing MR009 independent report was separately finalized after all 19 frozen-file tests passed.

## Result: selection-complete, not module-complete

All **134 distinct m81373 source selectors** resolve. There are **no duplicate selectors, no overlapping selected subtrees and no duplicated m81373 original IDs across target units**. Every source exercise and every supplied solution lies inside exactly one selected subtree. No completely unselected exercise, definition, substantive prose paragraph, readiness item, learning objective, key-concept block, writing question, self-check block or glossary entry remains.

That does **not** establish a complete source-faithful module. The legacy MR001 material compresses three worked solutions and preserves only its four selected outer IDs, omitting 61 nested source IDs. Two higher practice wrappers and the general practice heading remain unrepresented. Units 006–010 are draft/integration coverage, not ready-reader evidence. The existing separate-unit readers lack direct offline cross-unit navigation. These obligations prevent a module-complete claim.

## Evidence and reproducibility

Read the actual 151578-byte EN module directly from the pinned ZIP, without extracting the archive:

- Archive: `downloads/mr-Deva-IN/releases/A20-canonical.zip`.
- Member: `osbooks-prealgebra-bundle-38cae454e644abf9f0a623e876994553881597c9/modules/m81373/index.cnxml`.
- Module SHA-256: `2b606026c2b34cdf69acfa29bfe4b90abdb6961a322a78c7ec20107e0948b05c`.
- Module identity: m81373; UUID `59fe6dc4-6e09-4a88-aa1c-b5f72bd79a20`.

Parsed all ten actual target XMLs, inspected their source selectors, nested IDs and links, read the legacy four selected passages and their corresponding source text/table structures, and read MR010's detailed exclusion/drafting note. This audit does not infer source content from that note alone. Source raster alt descriptions were not treated as independently verified pixels; a fresh line-by-line legacy-image audit remains part of the fidelity work described below.

Commands from the worktree root:

```powershell
python -B mr-Deva-IN/tools/test_m81373_coverage.py
python -B mr-Deva-IN/tools/test_m81373_coverage.py --report
```

All **9 tests pass**. PASS means this inventory and its explicitly recorded gaps match the files; it deliberately does not mean that the gaps have disappeared. The read-only JSON report lists every missing ID, current XML hashes, uncovered title/metadata text and per-unit counts. No corpora are copied, no files are written and no browser actions occur.

## Exact coverage by unit

Only m81373 selectors are counted here; MR001's other-module selections and all authored diagnostic/practice questions are excluded.

| Unit | m81373 selectors | IDs inside selected source blocks | Source exercises | Supplied solutions | Current workflow status |
|---|---:|---:|---:|---:|---|
| 001 | 4 | 65 | 3 | 3 | Ready review draft; legacy fidelity deficit below |
| 002 | 4 | 34 | 3 | 3 | Ready review draft |
| 003 | 1 | 4 | 0 | 0 | Ready review draft |
| 004 | 16 | 60 | 12 | 6 | Ready review draft |
| 005 | 16 | 56 | 12 | 6 | Ready review draft |
| 006 | 31 | 119 | 26 | 13 | Draft/integration coverage, not ready-reader promotion |
| 007 | 9 | 24 | 4 | 0 | Draft/integration coverage, not ready-reader promotion |
| 008 | 21 | 101 | 11 | 11 | Draft/integration coverage, not ready-reader promotion |
| 009 | 14 | 103 | 9 | 9 | Draft/integration coverage; independent 19-test frozen run passed |
| 010 | 18 | 53 | 4 | 4 | Draft/integration coverage, not ready-reader promotion |
| **Total** | **134** | **619** | **84** | **55** | **Module remains incomplete** |

The parent's explicit status for this audit is ready units **001–005 only**. That is 41 m81373 selections, 30 source exercises and 18 supplied solutions; the remaining 93 selections, 54 exercises and 37 supplied solutions are draft/integration coverage. `STATUS.json` still says 001–004 and carries an older 2026-08-30 snapshot. This report records the discrepancy but does not edit or silently update the shared status ledger.

The other **29 exercises have no source-supplied solution**, not missing translated source answers. Each has a visibly distinguishable authored-answer target in the current XML: six in 004, six in 005, thirteen in 006 and four in 007. Their existence does not substitute for those units' independent mathematics and reader review. Of the 55 supplied-solution IDs, 52 are retained; the remaining three belong to the condensed MR001 passages whose answer content is present but whose original solution anchors are absent.

## Non-exercise and wrapper coverage

| Source component | Actual location or remaining obligation |
|---|---|
| Metadata objective introduction `para-00001`, list `list-00001`, all three objective items | MR008; whole-module objectives are correctly distinguished from that checkpoint's scope |
| Three readiness notes `fs-id1167836299681`, `fs-idm404421072`, `fs-idm387231616` | MR008, including original problems, answers and reference links |
| Domain/range teaching section `fs-id1167829789538` | Context ID and translated h2 retained in MR008; its selected children are split between 008 and legacy001 |
| Function teaching section `fs-id1167836610583` | Context ID and translated h2 retained in MR009; all direct content blocks selected there |
| Function-value teaching section `fs-id1167824731607` | Context ID and translated h2 retained in MR010; child selections split between 010, 002 and legacy001 |
| Key Concepts `fs-id1167829711772` | Entire section selected in MR003, including title and both child concept blocks |
| Exercise-group wrapper `fs-id1167826170977` | Missing target ID; infrastructure wrapper with `class=section-exercises`, no independent prose/title |
| Practice Makes Perfect wrapper `fs-id1167826189010` and unnumbered title | Target wrapper ID and this general heading missing; all actual practice questions/instructions underneath are already selected in 004–006 |
| Writing Exercises wrapper `fs-id1167829756260` | Uncounted context ID and translated h2 retained in MR007; all four questions selected individually |
| Self Check `fs-id1167829783756` | Entire source block selected in MR007, including the checklist's original media ID; unanswered learner self-assessment remains distinct from authored worked answers |
| Five glossary entries | Four in MR007; relation entry `fs-id1167833175472` in legacy001; its meaning text is translated but nested meaning ID is missing |
| CNXML document title / MDML title | English title is “Relations and Functions”; Marathi `संबंध आणि फलने` appears in MR007's contextual h1. There is no assembled module-level title/metadata artifact yet |
| MDML content-id, UUID, anonymous content/metadata/abstract/glossary containers | Infrastructure identity, not new teaching material to translate; retain/marshal these in the eventual module manifest, rather than inflating selection counts |

The source has **625 unique original IDs**. Selection subtrees account for 619; four more are properly retained as uncounted contextual IDs. Of all 625, **562 appear in the target files** and **63 do not**: 61 legacy nested IDs plus the two practice wrappers. The source's anonymous text outside selected subtrees consists only of module/metadata titles, content-id, UUID and the five section headings listed above. Four section headings are already translated under contextual wrappers; the practice heading needs explicit reconciliation.

Do not “fix” the two practice-wrapper gaps by simply counting or selecting their whole parent subtrees: that would overlap already translated exercise groups. They need an assembly/context mapping with preserved IDs and a translated heading, not duplicate exercise production.

## Legacy MR001: precise fidelity obligations

| Existing source selection | Present mathematics/content | Missing nested identity and full-source treatment |
|---|---|---|
| Relation glossary `fs-id1167833175472` | Relation/domain/range meaning translated | Meaning ID `fs-id1167833175475` absent; no missing mathematical definition is alleged |
| Example 6 `fs-id1167836692527` | Five ordered pairs, question and both projections present | 9 IDs absent: exercise, problem, solution and six paragraph IDs; source solution structure/repeated relation compressed |
| Example 7 `fs-id1167836521479` | Formula and all three requested values, 26, 1, `2a²+3a−1`, present | 25 IDs absent: exercise, problem, solution, five paragraphs, three tables and fourteen media; source's separate substitution/simplification rows are collapsed into shorter lines |
| Example 8 `fs-id1167829859398` | Formula, all three evaluations and the distinction `g(x+2)≠g(x)+g(2)` present | 26 IDs absent: exercise, problem, solution, six paragraphs, three tables and fourteen media; source's separated procedure/identification rows are condensed |

In aggregate: three exercise IDs, three problem IDs, three solution IDs, seventeen paragraph IDs, six table IDs, twenty-eight media IDs and one glossary-meaning ID. These are not 61 untranslated exercises or 61 independent concepts. The missing identities and condensed source procedures nevertheless prevent treating the selected outer blocks as fully preserved translations of every source text/step.

The earliest source-order fidelity reconciliation marker is **A20:m81373#fs-id1167836692527**. Reconcile that passage and the two later legacy examples with their actual EN/ID source text and canonical equation rasters; restore traceable problem/solution navigation, all original identities and the complete worked steps in an explicitly authorized full-module representation. Preserve the old MR001 output/hash unless the parent specifically authorizes changing it. A new faithful representation must record its relationship to the legacy adaptation and must not silently double-count the same selections.

## Links and unavailable destinations

All seven original source links are retained with their multiplicity. Current same-document `#` links resolve structurally in their own XMLs. No live-network availability or browser behavior is asserted here.

- Three MR008 readiness references go to **m81422**: `fs-id1167836530265` twice and `fs-id1167836652573` once. Those target example IDs are not present in units001–010. They remain disclosed HTTPS English-source references, not local Marathi/offline destinations. Their pinned source exists, but translating that earlier module remains part of the wider assignment.
- Three MR009 references point to two examples already translated in MR008: `fs-id1167829683746` twice and `fs-id1167833057329` once. The source IDs/document attributes survive, but the hyperlinks currently go to English HTTPS pages. The Marathi targets exist yet direct offline cross-unit navigation is unavailable.
- The external resource URL `https://openstax.org/l/37introfunction` remains in MR002. It is an optional internet resource, not silently dropped or falsely presented as embedded/offline material.

MR010's references to prior units001–003 are authored explanatory references, not lost original source link elements; its selected source blocks contain none. Source links to external chapters/resources should remain honestly external until corresponding local translations and routes exist. An assembled module must provide usable ordering/navigation among its present sections and source problem/answer anchors.

## Remaining obligations and safe continuation

1. Close the legacy fidelity/identity obligations above without overwriting the frozen pilot by implication.
2. Add the two missing practice context IDs, general practice heading and module-level identity/title/assembly metadata, without overlapping the already selected child blocks.
3. Finish the actual mathematics, source-image, build and permitted visual/reader checks for 006–010; their existence and the passing coverage suite are not reader acceptance. Keep unresolved native-speaker/teacher review explicit.
4. Resolve current cross-unit navigation for present Marathi material; preserve clear external-link limitations for untranslated m81422 and the optional resource. Reconcile coverage/status ledgers with the completed evidence.
5. Only then assess full m81373 text/workflow completion. All later A20 and all other assigned books still remain substantial work.

There is **no further wholly unselected teaching/practice block inside m81373** to dispatch as a new slice. For fresh production in parallel with these obligations, the pinned Intermediate Algebra collection explicitly places **m81374, “Graphs of Functions,” next**; this is verified collection order, not an inference from module numbering. Its opening scope begins with **A20:m81374#para-00001** and `#list-00001` in metadata, then readiness note **A20:m81374#fs-id1167826157468**, followed by `fs-idm664502240`, `fs-idm263727344`, and the first teaching section `fs-id1167836579284` (“Use the Vertical Line Test”). Do not skip that metadata/readiness front matter. Starting this new module does not clear the m81373 completion obligations.

Read only the small collection and next module members to verify that forward marker. Collection SHA-256: `993990c353220be879928579c1393ced90c8b54764b4ba1182ba660b54e8ce32`; next module SHA-256: `021c29fa9a6ab3d5b06d2ef143a82d2ac818ed25fe6fd44ebf5d7a6be07a123a`. No m81374 translation, media inspection or full-module review is claimed.

## Exact target snapshot

These are actual file hashes, not authority to promote draft status. The script's `--report` prints updated values on later runs.

| Unit | XML SHA-256 |
|---|---|
| 001 | `367314e8948ae28ba17de187ebca4e09d294e2c472a20c433538adb8dd06aac9` |
| 002 | `0a46a929a80df9755bc4f4df95102049c524f2506daf03c37952a368f01a1172` |
| 003 | `374826ca75c4e3841afff71a7e4ad2d8cb0b58d4f3059430a4634c72ce751c98` |
| 004 | `0733c4a1630584e1c6451e3af34cf39d8d85a12173657720b541fbf3fe826430` |
| 005 | `b4480901a99322492c49481acd4b6c5edc3e587d2be0e9afe7c66ebc08e85ca3` |
| 006 | `5538a28327ac72086ab4ab4d4054fe892ff78fb5a8864f1ada67871b93bc5fd0` |
| 007 | `44593e8d688ad459ed2e72b1eac1293974cd3203661ff5df3b220d0815419e06` |
| 008 | `418afc11f3b4c9c54176e4ddb0bab257ecc245101cc593b7904560c5d7eb4f66` |
| 009 | `f3cb4ee775ed81f4a3381953c9e3c8a46bc339c9a4b7a3919355deea1f6f53ee` |
| 010 | `be72aae0b5e00768349c0b289ee229ec4d82d38a43de656cefc520fab32568f4` |

The script records known gaps rather than masking them as success. Its count/identity baseline should be revised together with this report when authorized corrections land. It cannot establish semantic completeness merely because a selected parent contains every source child, nor can it establish visual usability, current external-site availability or human linguistic approval. No source, translation, config, shared status file or browser state was changed by this coverage audit.

Later checkpoint note: ready PDF006–008 has now been accepted separately. This audit and its test's fixed READY set remain the historical001–005 baseline; they must not override current format-specific STATUS.json or infer readiness from selection coverage.011 replacement/full-module assembly is outside this001–010 inventory. The durable audit artifact is this Markdown report; `--report` emits fresh JSON to stdout and does not imply a saved coverage JSON file.

## Primary integration update — 2026-08-31

Commit `b66be4d` records the ready001–005 checkpoint and corrected shared status, so the earlier note that STATUS still lists001–004 is historical and resolved. This audit and its nine tests deliberately remain the001–010 baseline. Draft011 now restores the four condensed001 selections with their full working and61 additional nested IDs; it is a replacement, adds zero unique selectors, and still requires independent review and assembly. Draft012 advances into the next collection module m81374 without clearing these m81373 obligations. The two practice wrapper IDs, module identity/title/ordered assembly, usable cross-unit navigation and format-specific reading review remain required before any full-module claim.
