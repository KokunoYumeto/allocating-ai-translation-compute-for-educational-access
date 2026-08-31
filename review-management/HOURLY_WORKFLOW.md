# Coordinator hourly workflow

This is the procedure for the coordinator's hourly heartbeat, not a replacement for any language owner's instructions. It maintains **one** continuing branch, `codex/additional-translations-review`, in the allocation-report repository. It does not create nine branches/clones or a production release. The local heartbeat can run only while its host and application are available; this document alone does not schedule execution.

## 1. Recover real instructions and the previous boundary

Read the actual user direction, `USER_INSTRUCTIONS_VERBATIM.md`, `TRANSLATION_MANAGEMENT_GOAL.md`, the private task/ref registry, previous publication receipt, decision log and restart cursor. Treat summaries and old status prose as navigation aids, not authority. Keep raw chats, task identifiers, account/machine paths and operational instructions out of the public export.

Check disk space before substantial writes. Inspect the nine existing tasks' actual files, committed checkpoints, uncommitted work, source/canon consultation and review boundaries. Refresh the export inventory; do not count generated artifacts, source downloads, front matter or parallel register tracks as equivalent completed instructional modules. Pending human review does not end the translation assignments.

## 2. Check upstreams without silently replacing source pins

Compare the [18-repository registry](UPSTREAMS.json) with live exact default-branch refs and published release identities. Include prereleases and asset digest/size changes; distinguish default `main`/`master`, release tag, sealed release commit and later live-source fixes. Exclude unpublished draft metadata from public records.

For the allocation research repository, inspect new commits and relevant branches, issues and pull requests for changed findings or priorities. For the Indonesian catalog and assigned source repositories, inspect relevant source/backend/refinement changes and bounded public route evidence. A course URL is not proof of adapter runtime use; an unknown evidence state is not absence. Record checked URLs, timestamps, failures, pagination/rate-limit bounds and unverified claims.

Send materially relevant source findings to their language owners with exact refs/asset identities and a scoped adoption question. Preserve existing pins until an explicit decision; do not automatically download large releases, rebase workers or restart source/license audits. Avoid repeatedly sending unchanged findings. Record message acceptance separately from worker acknowledgment or adoption.

## 3. Export a consistent boundary in the coordinator checkout

Keep all worker worktrees untouched. Prefer immutable committed objects. The initial exporter selects one saved HEAD per lane and records it in the output manifest; the manifest may therefore be newer than an earlier inventory. Changing/untracked work is excluded by this committed-only exporter. If a later implementation supports owner-agreed working snapshots, it must establish a coherent source/reader/provenance boundary and label unreviewed work explicitly; otherwise retain the saved checkpoint and record the omission.

Use the existing isolated destination checkout on the continuing review branch. Inspect its status and fetch the remote before overwriting coordinator output. Do not overwrite receiving-PC edits or unexpected local changes. If the remote advanced, reconcile its reviewed content first; if histories diverged, stop publication and record a concrete coordination blocker rather than resetting or force-pushing.

From the originating coordinator workspace, after refreshing the inventory and verifying the destination:

```sh
python management-staging/export_translations.py --inventory logs/TRANSLATION_EXPORT_INVENTORY_2026-08-31.json --destination tmp/coordination-github-handoff-20260831
```

The dated inventory path is the initial run's path: later runs must refresh that inventory or pass the actual newer inventory, not silently reuse stale state. The destination is the coordinator's isolated Git checkout, never a worker workspace. Published copies of the tools live under `review-management/tools/`; the receiving PC does not need the originating private inventory merely to review exported files.

Preserve `translations/<locale>/workspace/<original-prefix>/...`, applicable byte-preservation attributes, necessary small witnesses/assets, notices, canon consultation, useful QA and recovery records. Exclude raw operational instructions, credentials, unrelated files and unnecessary duplicate corpora. Parameterize executable runtime/donor paths deliberately; do not drop required builders or replace paths with unusable placeholders.

## 4. Validate what will actually be published

Check `translations/EXPORT_MANIFEST.json` against every exported byte. Retain original commit/blob/SHA-256 identities, delivered hashes, transformations, exclusions and deferred-work counts. Changed builders or locks invalidate their old byte-hash attestations; do not silently rewrite historical QA to imply fresh validation. Javanese's sanitized lock is one known case needing reviewed derivative rebinding before full lock-bound replay.

Run the exporter's declared syntax/resource checks and any justified bounded checks of transformed code. Review the exported tree and notices. Keep missing inputs, incomplete replay, visual/accessibility issues and native/educator-review limits visible. Successful hashing or a build does not make a translation production-ready. [REVIEW_GUIDE.md](REVIEW_GUIDE.md) records receiving-PC boundaries.

During continuing translation/review, owners must actually reconsult readable target-language canon and pinned mathematical witnesses at drafting, revision and QA stages. Preserve meaningful consultation and linguistic decisions; do not reduce canon work to an old acquisition count or an endless acquisition loop.

## 5. Publish only real reviewed changes

Review the destination diff and stage only the intended `translations/` and `review-management/` paths. If there is no substantive changed export/management content, do not create an empty or timestamp-only publication commit. Record the unchanged check locally instead.

For a reviewed nonempty change, commit normally on `codex/additional-translations-review`, then use a normal push, never `--force`:

```sh
git -C tmp/coordination-github-handoff-20260831 diff --check
git -C tmp/coordination-github-handoff-20260831 push origin HEAD:refs/heads/codex/additional-translations-review
```

These commands do not replace the preceding staged-diff review and commit step. If the push is rejected because the remote moved, fetch and inspect the divergence; preserve both sides and do not perform a blind merge/rebase. Do not merge to `main`, release production artifacts, or delete originating source/work as part of the hourly run.

Read back the remote branch commit and verify the expected manifest/paths at that commit. Record exact local/remote commits, exported per-locale boundaries, checks performed, omitted work, upstream decisions, outstanding owner actions and a restart cursor in external receipts. Report success only after remote verification; message acceptance and a local commit are not proof of publication. Keep private execution receipts local and publish only portable project facts.
