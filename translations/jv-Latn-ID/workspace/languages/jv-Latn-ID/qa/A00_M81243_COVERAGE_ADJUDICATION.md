# A00 `m81243` post-rereview coverage adjudication — independent audit

Audit date: 2026-09-02. This audit is confined to the coverage-layer
incorporation of the repaired candidate's already completed automated
cross-component rereview. It changes no coverage code or JSON, producer,
translation, generated artifact, receipt, prior QA report, Git index, or ref.

## Verdict

**FAIL / OPEN.** The current saved snapshot is internally consistent and keeps
the assignment ledger at `0 complete / 2 partial / 155 untranslated`, with
`whole_module_complete: false`, producer pre-review state `pending`, and human
review `pending`. The exact rereview report is correctly hash-bound. However,
the coverage adjudicator does **not** bind the build receipt being admitted to
the reviewed build-receipt SHA-256. A coherent, otherwise valid producer plus
saved-receipt mutation was accepted while the exact old rereview report remained
unchanged. Therefore this coverage adjudication cannot close on the current
implementation.

This finding does not reverse or reinterpret the rereview's automated pass for
the exact build receipt whose SHA-256 is
`94f1f1f13f255a060ebdd4e1153f509f058a7be85a656f898f8bc153a4ee1099`.
It prevents coverage from treating that report as approval for a later,
coherently regenerated receipt with different bytes.

## Instructions and state reread

I reread the required current files before adjudicating. Exact witnesses at the
audit snapshot were:

| File | Bytes | Lines | SHA-256 |
| --- | ---: | ---: | --- |
| `AGENTS.md` | 306 | 4 | `287aaeb6a9d8b6aea4bc166019a9b8ddce3c37fe41d6b2b997b99a03cbb5c300` |
| `USER_INSTRUCTIONS_VERBATIM.md` | 4,238 | 36 | `e25d82e41a204d601c494a41663e15e002068b8baea5ebcf5acad3b1db3845fa` |
| `languages/jv-Latn-ID/GOAL.md` | 3,562 | 24 | `22939b2c33231917d239e8369e6ba3e5e0d200e94d7c3b0a19d130af3a0111f8` |
| `languages/jv-Latn-ID/DECISIONS.md` | 59,069 | 254 | `6a7106fc77deb3f2f7e51eaff674d5b04f75ecc7865ab17079e17591f8546a52` |
| `languages/jv-Latn-ID/NEXT_UNIT.md` | 6,843 | 105 | `ddc1cbec35e3465abb351abbb25b77d6d92c9dce9dfa3d43ecf0246220f6479f` |
| `languages/jv-Latn-ID/qa/STATUS.md` | 25,464 | 408 | `f4ac11133f42a24f0462c74e5df2527ab329fbbfad47b36d8c3d83910b84947f` |
| `languages/jv-Latn-ID/scripts/coverage.py` | 40,420 | 617 | `ad5eb3e43656b7344d783bd2c60bf21d5aaa52dd84734b7fed8787d34132d69e` |
| `languages/jv-Latn-ID/coverage.json` | 310,242 | 7,317 | `f585926ba3f41dfc4b18e3c30740fa39d85cede449ffc1eb06a887a30aae9922` |
| `languages/jv-Latn-ID/scripts/test_complete_a00_workflow.py` | 8,080 | 152 | `7bbed7e95ee3a38f4c55262ec7ee0f9998007a0ae9cfc86e8f6754ae9bfc2e64` |
| `languages/jv-Latn-ID/qa/A00_M81243_COMPLETE_REREVIEW.md` | 19,286 | 322 | `adfe7d63fe3325906f6dc7c7d259c9b5f92a297b702b12c72467cae5f5977218` |
| `languages/jv-Latn-ID/qa/a00-m81243-complete.build-receipt.json` | 24,975 | 216 | `94f1f1f13f255a060ebdd4e1153f509f058a7be85a656f898f8bc153a4ee1099` |

The persistent objective remains the entire A00, A10, and AX-2 assignment.
The current GOAL, DECISIONS, NEXT, and STATUS records consistently describe the
rereview as a bounded automated pass and leave every human and integrated gate
open. The first failed complete-candidate review remains separate evidence.

## Current coverage state: correct but insufficient to close

I parsed all of `coverage.json`, recomputed both evidence-file hashes from their
actual bytes, and checked the relevant producer receipt fields. The current
serialized ledger says:

- top-level `status: incomplete`;
- `completed_modules: 0`, `partial_modules: 2`, and
  `untranslated_modules: 155`;
- one `a00-m81243-complete` candidate with
  `complete_source_scope: true`;
- candidate state
  `complete_source_scope_assembled_built_and_automated_cross_component_review_passed_human_review_pending`;
- `producer_pre_review_state: pending`;
- `independent_cross_component_review.status: passed`, explicitly scoped to
  automated source/tree/asset/reader/notice/narration/dependency/mutation work;
- `human_language_review: pending`;
- `whole_module_complete: false`; and
- `effect_on_baseline_module_counts:
  none_pending_human_and_integrated_accessibility_review`.

The coverage row's rereview SHA equals the actual report SHA exactly:
`adfe7d63fe3325906f6dc7c7d259c9b5f92a297b702b12c72467cae5f5977218`.
Its build-receipt SHA likewise equals the current actual receipt SHA exactly:
`94f1f1f13f255a060ebdd4e1153f509f058a7be85a656f898f8bc153a4ee1099`.
Thus the saved JSON correctly describes today's bytes; the defect is in the
admission rule for a coherently changed future byte set.

The producer receipt itself remains deliberately pre-review:

- `status: structural_pass_independent_cross_component_review_pending`;
- `independent_cross_component_review: pending`;
- `human_language_review`, `visual_review`, `integrated_browser_review`,
  `screen_reader_review`, and `listening_review`: all `false`;
- `synthesized_audio_files: 0`; and
- `whole_module_complete: false`.

The global AX-2 obligation remains pending, and the global linguistic/visual/
screen-reader/pronunciation review obligation remains pending. I found no new
human, native, educator, browser, visual, screen-reader, pronunciation,
listening, synthesis, publication, module-completion, or assignment-completion
claim in the candidate row or its surrounding coverage state.

## Exact rereview-report binding: passes

`complete_module_candidate_coverage()` hard-codes the exact report SHA at
`coverage.py:392`, checks the actual report bytes against it at lines 404–405,
and also requires the exact pass sentence and reviewed build-hash text at lines
406–407.

I appended an in-memory report mutation through `Path.read_bytes` without
writing the file. The call rejected it with the exact result:

```text
ValueError: Complete-module independent rereview evidence changed
```

The report's current exact bytes therefore are fail-closed at this boundary.

## Exact build-receipt binding: fails

The code verifies that saved complete products equal the producer's current
in-memory products at lines 398–401. It then requires only that the unchanged,
hash-bound report contains the literal old build SHA at lines 405–407. It never
compares `sha(built[build_name])` with that reviewed SHA. Line 443 instead writes
whatever current generated build-receipt hash it received into the coverage
row.

I independently demonstrated the gap entirely in memory:

1. Generate the current producer product map.
2. Parse only `qa/a00-m81243-complete.build-receipt.json`.
3. Add the semantically irrelevant field
   `_coverage_adjudication_probe: coherent-unreviewed-build-receipt`.
4. Serialize with the producer's two-space JSON style and trailing newline.
5. Patch `build_complete_a00_module.products()` to return that coherent product
   map and patch `Path.read_bytes` for exactly the receipt path to return the
   same simulated saved bytes.
6. Leave the rereview report and all other evidence unchanged, then call
   `complete_module_candidate_coverage()`.

Observed result:

```text
COHERENT_UNREVIEWED_RECEIPT_ACCEPTED 1 239c10e2ee5379291f767555d0eb61ef35a273b54bb4622325641dcf41959b87
MUTATED_BUILD_SHA256 239c10e2ee5379291f767555d0eb61ef35a273b54bb4622325641dcf41959b87
REVIEWED_BUILD_SHA256 94f1f1f13f255a060ebdd4e1153f509f058a7be85a656f898f8bc153a4ee1099
```

The function returned one admitted candidate and exposed the mutated hash as
its `build_receipt.sha256`. This is a direct counterexample to exact reviewed
build-receipt binding. A passing rereview of one receipt cannot authorize this
different receipt, even when its required semantic fields remain valid.

The focused test does not cover this boundary. It checks candidate cardinality,
complete-source scope, false whole-module completion, notice counts, producer
pending state, review `passed`, and no baseline-count effect, but asserts neither
the exact build SHA nor rejection of a coherent producer/receipt mutation.

## Required commands

Both requested current-state commands pass:

```text
python languages/jv-Latn-ID/scripts/coverage.py --check
Coverage matches: A00 75 + A10 82; 0 complete, 2 partial, 155 untranslated; all AX-2 module completions pending.
exit 0

cd languages/jv-Latn-ID/scripts
python -m unittest -v test_complete_a00_workflow.CompleteA00Workflow.test_coverage_records_candidate_without_advancing_module_count
Ran 1 test in 17.691s
OK
```

These passes establish deterministic agreement for the current byte set and the
currently asserted status fields. They do not close the coherent-mutation gap
demonstrated above.

## Required repair and exclusions

The adjudication remains open until coverage directly requires the current
generated build-receipt SHA to equal the exact reviewed SHA and a regression
rejects a coherent producer-plus-saved-receipt mutation while the old report is
unchanged. A repaired implementation and regenerated coverage form a new
coverage snapshot and require a separate readjudication; this failed report
must remain unchanged as historical evidence.

This audit is automated coverage-layer evidence only. It performs no linguistic
or native-language review, educator/register approval, integrated-browser or
visual inspection, keyboard or screen-reader exercise, pronunciation/prosody
approval, listening or voice/provider validation, audio synthesis, publication
approval, whole-module approval, or whole-assignment approval. It does not
authorize staging, committing, publishing, or changing coverage state.
