# Indonesian mathematics program: task-level token audit

**Audit cutoff:** 2026-08-30 (Europe/Berlin)  
**Status:** measured lower bound from completed-goal receipts and one live-goal checkpoint; not a program-wide total

## Result

The audited Indonesian production tasks already account for **at least 88,493,496 Codex pursuit-accounting tokens**. This is a strict lower bound over the exact counter-backed phases listed below. It is not a guess, a gross-input total, a billing total, a weekly-usage percentage, or a complete total for the 722-module Indonesian program.

Of that amount, **87,035,193 tokens** belong to edition-production/translation/QA pursuits (including their own end-to-end build and publication work where the goal did not expose a narrower split). The remaining **1,458,303 tokens** are separately identified maintenance, deployment, and durable-state correction goals. Several known Indonesian tasks had no surviving pursuit counter, so the unknown remainder is positive and potentially substantial.

## What the counter means

The current OpenAI Codex goal implementation computes a pursuit delta as:

`input_tokens - cached_input_tokens + output_tokens`

and routes descendant-agent usage into the root goal. See the OpenAI Codex source for the [goal-token formula](https://github.com/openai/codex/blob/main/codex-rs/ext/goal/src/accounting.rs#L422-L446) and [descendant accounting hook](https://github.com/openai/codex/blob/main/codex-rs/ext/goal/src/extension.rs#L388-L413).

Therefore, a pursuit value is **not gross model input**: cached input has already been subtracted. Reasoning is not added again because it is a component of output usage, not a second independent total. The pursuit receipts do not preserve the component totals needed to reconstruct input, cached input, uncached input, cache-write input, ordinary output, reasoning output, or request count.

For comparison, official OpenAI API usage schemas define request/organization fields for input, cached input, cache-write input, uncached input, output, reasoning output, and model-request counts; those fields would permit a component audit if the per-request records had been retained. They were not retained for these long Codex pursuits. See the official [Responses usage schema](https://developers.openai.com/api/reference/cli/resources/responses/methods/retrieve) and [organization usage schema](https://developers.openai.com/api/reference/resources/admin/subresources/organization/subresources/usage).

No money conversion is made here.

## Exact counter-backed phases

| Task and phase | Pursuit tokens | Pursuit elapsed | Exact scope / boundary | Counter provenance |
|---|---:|---:|---|---|
| `01a02164-3741-72b2-a48d-bab561ef5cd9` — D80 *Metode dalam Aljabar, Jilid 2* complete-edition goal | 31,014,565 | approximately 49 h 21 m (no exact seconds survive) | 146 units; 864-page edition; public `main` commit [`8dbaeb4443978aef6d89365149e28a6ba06e005a`](https://github.com/KokunoYumeto/metode-aljabar-jilid-2-id/commit/8dbaeb4443978aef6d89365149e28a6ba06e005a); tree `6f9c40a7dbe5ab4d28cbc87cacbbc9fd54459654`; 223-row [`MANIFEST.csv`](https://raw.githubusercontent.com/KokunoYumeto/metode-aljabar-jilid-2-id/8dbaeb4443978aef6d89365149e28a6ba06e005a/MANIFEST.csv), 24,150 B, SHA-256 `ce6d1534e83fbdf3703261b5e7a3f60d814a020e35782ebffaf6e523e90601b7` | Completed turn `01a04a62-970f-7c82-a1be-648dba70b22a`, final item `item-4096`; repository itself contains no token receipt |
| same task — later Pages-only deployment goal | 586,587 | 1,828 s (30 m 28 s) | 31 reader files; final Pages commit [`7aacf53215171cfc734e963bdc40ac8f3eddfe13`](https://github.com/KokunoYumeto/metode-aljabar-jilid-2-id/commit/7aacf53215171cfc734e963bdc40ac8f3eddfe13); no translation or corpus-byte change | Completed-goal final receipt; separate from the complete-edition pursuit |
| `01a01f41-26f0-7e63-952c-de86c2f9155e` — Elementary Algebra 2e owner goal, live checkpoint | 38,663,209 | 250,800 s (69 h 40 m) | 82/82 modules; current published reader 2,158 pages; translation, backend, reader/PDF, QA, and publication work in the owner lane; public boundary GitHub release `v1.0.1` / release ID `379103224`, Zenodo record `22165626` | Live `get_goal` checkpoint reported by the task on 2026-08-30; because the pursuit was still active, this is a lower bound even for that goal |
| `01a01f57-0ad8-7562-a71c-4af27dd4ba4c` — Elementary Algebra 17-module helper goal | 2,022,997 | approximately 3 h 13 m | 17 modules; `HANDOFF.json` SHA-256 `9ca4fa0d...2bd38`; 869/869 files independently read back | Preserved completed-goal final receipt. Current `get_goal` is null; null means the goal is no longer active, not zero usage |
| `01a02037-bb40-7882-a0e1-e563c3e685e8` — Applied Combinatorics production | 10,838,830 | 59,948 s | Indonesian Applied Combinatorics edition; public commit [`50cb1c9eae0273d7235494c747555be2b4e9f910`](https://github.com/KokunoYumeto/applied-combinatorics-id/commit/50cb1c9eae0273d7235494c747555be2b4e9f910); release `2026.08.22.2`; Zenodo `22062005` | Task's completed-pursuit audit, returned 2026-08-30 |
| same task — Applied Combinatorics maintenance/publication | 832,315 | 5,020 s | Terminology maintenance and publication checkpoint on the same public lineage | Separate completed pursuit; not included in the production row |
| same task — CLP4 Indonesian helper | 2,683,906 | 15,681 s | 316-page textbook + 486-page problem book; 4,477 files; `HANDOFF.json` SHA-256 `d5e09f6345e924f76dba2b962c8fd1f0ebf782567e68b99fb7c860ff18825303` | Separate completed pursuit |
| same task — Elementary Algebra 15-module replacement packet | 1,811,686 | 3,298 s | 15 modules; final `HANDOFF.json` SHA-256 `868172e433c974b23472084bb88f8e6e5e5b20e718940099f271dc253067e93a`; 843 retained files checksum-closed | Separate completed pursuit |
| same task — Elementary Algebra durable-goal correction | 39,401 | 246 s | No translation change; goal/cursor/handoff reseal and 847-file verification | Separate completed pursuit; classified as support rather than edition production |
| **Audited lower bound** | **88,493,496** | **not summed** | Parallel task elapsed times cannot be added into program wall-clock time | Sum of the nine non-overlapping counter rows above |

The five completed pursuits in task `01a02037-bb40-7882-a0e1-e563c3e685e8` total **16,206,138 tokens over 84,193 seconds (23:23:13)**. That task returned the phase split above directly; the audit uses the total only once and displays the components for scope transparency.

## No-double-counting map

1. Internal descendant-agent usage is already rolled into each root pursuit by the Codex goal-accounting hook. No internal subagent counter is added separately.
2. The helper rows above are distinct peer Codex tasks or distinct sequential pursuit goals with their own completion receipts. Their task/goal counters are not re-used elsewhere in this table.
3. The Elementary Algebra owner goal and the two helper goals cover related final-edition content, but their **compute events** are separate: the helper tasks produced packets; the owner task integrated and published them. Counting both measures actual program compute, not unique output pages.
4. The `01a02037...` subtotal is included once. Its component rows must never be added on top of the 16,206,138 subtotal again.
5. The D80 Pages deployment is separate from the 31,014,565-token edition goal and changed only deployment state. It is included in the broad program-compute lower bound but excluded from the 87,035,193-token edition-production subtotal.
6. A null current goal is never interpreted as zero historical usage. Historical completed-goal receipts are used only when they state an exact counter and scope.

## Known unmeasured remainder

The 88,493,496 figure excludes at least the following known work because no exact pursuit counter was returned or preserved:

- the central Indonesian curriculum selection/catalog/release work in `01a01ec1-e685-70d0-b022-211396334723`;
- the long-running coordination work in `01a024cd-b2e1-7d73-ad14-ce00f16bfdbc`;
- CLP2 helper work, Elementary Algebra post-release auditing, and the current v1.0.2 release-script/reader-repair work explicitly identified by task `01a02037...` as having no pursuit goal;
- DMOI4, CLP2 §3.1, later CLP3 maintenance, and v1.0.2 work in `01a01f57...` outside its preserved 2,022,997-token completed goal;
- every other Indonesian task not named in this bounded audit;
- any model activity that occurred outside an active pursuit goal or whose completed-goal receipt no longer survives.

There is no audited program-wide split for gross input, cached input, uncached input, cache-write tokens, ordinary output, reasoning output, request count, or weekly-usage percentage. Consequently, **88,493,496 is a measured lower bound in the Codex pursuit-accounting metric, not an estimate of gross tokens and not a basis for direct price conversion**.

## Research implication

The earlier small per-edition planning estimates are empirically inadequate for these actual end-to-end workflows. One 82-module Elementary Algebra owner lane alone had already reached 38.66 million pursuit-accounting tokens; one 146-unit/864-page advanced-algebra edition used 31.01 million. Any compute-allocation paper should therefore model at least two separate layers:

- source-text translation volume; and
- the observed workflow multiplier from mathematical checking, terminology work, deterministic replay, accessibility, reader/PDF/backend construction, repair, and publication.

The audit does not yet estimate that multiplier program-wide because the denominator (fresh source/output tokens by activity) was not retained. It establishes the measured numerator lower bound and the accounting boundary needed for a defensible later estimate.
