# U01 checkpoint audit — entire assignment not complete

Scope: the assigned input acquisition and first coherent Indian Bengali recovery unit. This is not full-book translation, validated Grades 3–8 coverage or a claim that the wider language gap is closed.

The user's later explicit instruction requires translation of the entire assignment and workflow. This audit proves only the U01 checkpoint and cannot authorize marking the overall goal complete. Full module/companion coverage remains pending.

| Requirement | Current evidence |
|---|---|
| Exact locale and worktree | `bn-Beng-IN` in translation metadata, terminology, HTML and QA; branch `codex/bn-beng-in-recovery` |
| All assigned Indonesian inputs | Catalog plus A00/A10/A20/A30 repository commits and trees in `sources.lock.json`; four exact-tag source ZIP digests and CRCs verified |
| Source freshness | Exact release manifests retained: A00 75/75, corrected A10 82/82, A20 48/83, A30 58/87; stale A20 README identified, not silently rewritten |
| Canonical upstream and selected scope | Both pinned trees, four collection UUIDs, 242 module references verified; A30 limited to m49301 and m49324 |
| Referenced media available | 11,046 unique referenced media checked against Git blob IDs; shared A00–A20 media used read-only; selected A30 74 locally verified |
| Source-faithful translation | Complete m81285/fs-id1726667 overlay, generated CNXML and offline HTML; 361 nodes, 59 IDs, 46 MathML expressions, 2 examples and 4 practice exercises |
| Distinct AX-3 companion | U01: placement 6, worked examples 7, exit/practice 6; all answers and provisional routing; original/adapted items labelled |
| Actual target-language canon | 15 indexed examples, readable OCR plus page-image verification, 5 actual consultation stages; Tripura explicitly supplementary |
| Terminology | 22-entry Indian Bengali ledger; regional synonym and editorial choices documented |
| Mathematical and structural QA | `status.json`: 20 rational checks, 12 answer-key regressions, preservation assertions, language tag, links, assets and reproducible output |
| Visual QA | `browser-check.json` and `VISUAL_REVIEW.md`: isolated local Edge, desktop/narrow layout, loaded images and MathML, no horizontal overflow |
| Attribution and restrictions | Original licenses/notices and full source preface preserved; unofficial derivative and modifications labelled; no training/fine-tuning dataset |
| Durable external state | README, WORK_GOAL, DECISIONS, source/release/reference locks, consultation records, QA and NEXT cursors |
| Post-disk-full integrity | JSON/XML/Python parse and pre/post-interruption HTML hashes matched; no Bengali source was truncated; missing lock/QA/cursor files subsequently generated |
| Independent reviews | Language/teacher, learner and screen-reader reviews explicitly pending, as required; no certification or human approval claimed |
| Local delivery | Commit includes only the language folder; inspect `git log -1` for the checkpoint. Coordinator-supplied root-file changes are preserved, not bundled. No push/publication. |

Resumption: source-faithful next `m81285/fs-id2784608`; companion U02 next `m81286/fs-id1408851`. Read the user's current coordinating-task instructions and the exemplar loop before further translation. Large duplication remains paused. The small reader build needs no downloaded corpus beyond committed witnesses.
