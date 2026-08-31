# Language Allocation: coordination handoff

Dated 2026-08-31. Nine language assignments, ranks 2–10. **This is a coordination snapshot, not a translation release.**

The package records who owns which material, what each saved checkpoint actually contains, what remains unfinished, verified shared source corrections, and what the receiving PC needs. It does not transport worker Git objects, translations, ignored source archives, canon corpora or private operational logs. A SHA in the index is a locator, not a backup.

## Start here

1. [STATUS.md](STATUS.md): saved progress and readiness limits.
2. [ASSIGNMENTS.md](ASSIGNMENTS.md) and [CHECKPOINTS.json](CHECKPOINTS.json): ownership, full commit identities and relative recovery locators.
3. [ISSUES.md](ISSUES.md): coordinator, user/capability and language-owned next actions.
4. [SOURCES.md](SOURCES.md) and [SOURCE_CORRECTIONS.md](SOURCE_CORRECTIONS.md): pinned inputs and three verified A20 figure discrepancies.
5. [INTEGRATION.md](INTEGRATION.md): receiving-PC checkout, validation and later translation transfer.
6. [WORKFLOW.md](WORKFLOW.md) and [DECISIONS.md](DECISIONS.md): recovery/coordination boundaries.

From this directory, run `python validate.py` (Python 3.9+; standard library only). It is read-only and checks the packet's file allowlist, hashes, schema, internal document links and common private-data patterns. Passing does **not** certify linguistic quality, fetch evidence or prove a worker rebuild. Compare the containing commit with the originating coordinator's independently recorded remote SHA.

## Publication boundary

This folder is an additive working handoff in the allocation-report repository. It does not revise the frozen paper, its ranking, release number or root checksum manifest. The report history remains intact. The packet has its own [MANIFEST.sha256](MANIFEST.sha256) and [.gitattributes](.gitattributes) for stable text bytes.

First-party documentation follows the repository's existing CC BY 4.0 license; `validate.py` follows its MIT code license. Upstream notices and source exclusions continue to apply. The source index reuses completed acquisition/audit records; it is not a renewed general audit.

Original user instructions and subsequent directions remain authoritative for the private production workflow. This public index summarizes coordination facts; it does not replace those instructions or authorize new publication, deletion or access.
