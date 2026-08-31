# Coordinator decisions

Dated 2026-08-31. This is the portable decision record; detailed private dispatch and verification receipts stay on the originating PC.

| ID | Decision | Basis / consequence |
|---|---|---|
| C-D01 | Create a durable approximately 3,000-character coordination goal without a token budget. | The user requested consolidation and a later cross-PC handoff. Its completion is separate from completion of the nine translations. |
| C-D02 | Reuse the existing allocation-report repository and create a separate additive handoff branch. | It is the relevant existing project; no new repository or change to main is needed. The research paper and root release manifest stay untouched. |
| C-D03 | Build in an isolated checkout based on real remote history. | Avoid disturbing dirty translation worktrees and avoid merging unrelated local history into the report. |
| C-D04 | Publish coordinator facts and locators only. | Worker translations, raw user messages, private host/account records and source corpora are outside this publication scope. Worker SHAs remain local-only. |
| C-D05 | Use a bounded 02:30 CEST Git snapshot with separately dated working notes. | Translation continues while handoff preparation proceeds. Do not chase every new draft or silently relabel working work as committed. |
| C-D06 | Verify all nine checkpoint objects and evidence locators locally. | Presence is verified; linguistic correctness and full rebuildability do not follow from Git presence. Retain lane-reported replay qualifications. |
| C-D07 | Separate offline reading, rebuilding and full source QA. | Several lanes need ignored pinned sources or platform-specific tools. One offline HTML page does not prove a clean-machine full build. |
| C-D08 | Consolidate only the three independently corroborated A20 figure discrepancies. | Exact pins, image hashes and supplied-versus-original answer distinctions are portable. Other local source findings are not silently elevated to independently verified shared corrections. |
| C-D09 | Preserve full assignment scope and ongoing canon consultation. | Original user instructions override withdrawn coordinator paraphrases. Historical pilot names do not narrow whole-assignment goals. |
| C-D10 | Attribute remaining work rather than making all tasks wait. | Stale goal controls, one HTML access limitation and format-specific review limits are explicit. Pending human review does not prohibit continued translation. |
| C-D11 | Validate and hash the packet separately from the frozen report. | Reviewed allowlisted files only; stable LF text via local attributes. Validation does not imply all worker content has been transported or checked. |

Current next action for the receiving coordinator is in [INTEGRATION.md](INTEGRATION.md). The containing Git commit establishes this package version; the originating private publication receipt records the actual verified remote SHA. Publication is not asserted merely because a planned branch name appears in the manifest.
