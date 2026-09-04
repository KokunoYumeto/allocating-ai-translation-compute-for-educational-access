# A00 `m81243` post-repair coverage readjudication — independent audit

Audit date: 2026-09-02. This audit is confined to the repaired coverage-layer
incorporation of the already completed automated cross-component rereview. It
changes no coverage code or JSON, test, producer, source, translation, generated
artifact, receipt, prior QA report, Git index, or ref.

## Verdict

**PASS / CLOSED for this exact automated coverage-adjudication snapshot.** The
repaired adjudicator now binds both the exact rereview report and the exact
build receipt reviewed by that report. The coherent producer-plus-saved-receipt
mutation that the first adjudication demonstrated is now rejected. Report-only
and saved-receipt-only mutation probes also reject, both focused coverage tests
pass, and global coverage remains exactly `0 complete / 2 partial / 155
untranslated` with `whole_module_complete: false`.

This closes only the bounded automated coverage incorporation. It does not
reinterpret the separately preserved failed adjudication, extend the underlying
rereview to new producer bytes, or establish human, native, accessibility,
publication, module, or assignment completion.

## Exact snapshot

| File | Bytes | Lines | SHA-256 |
| --- | ---: | ---: | --- |
| `scripts/coverage.py` | 40,650 | 620 | `c94d8a1323ae8bf518751cccf9c3e5b24fb4c3ef6ba1a9ebb9dbd0b8f0d4134d` |
| `coverage.json` | 310,242 | 7,317 | `f585926ba3f41dfc4b18e3c30740fa39d85cede449ffc1eb06a887a30aae9922` |
| `scripts/test_complete_a00_workflow.py` | 9,122 | 172 | `c36bbfcc862a65825acea88eaec6a24874f50dbc1c1fbb65ebce8ce2c3dd7b92` |
| `qa/A00_M81243_COMPLETE_REREVIEW.md` | 19,286 | 322 | `adfe7d63fe3325906f6dc7c7d259c9b5f92a297b702b12c72467cae5f5977218` |
| `qa/a00-m81243-complete.build-receipt.json` | 24,975 | 216 | `94f1f1f13f255a060ebdd4e1153f509f058a7be85a656f898f8bc153a4ee1099` |
| `qa/A00_M81243_COVERAGE_ADJUDICATION.md` | 9,518 | 182 | `456de47a4bacdfe69110d33ff09f9ade8af13dbcc5afc04a58e0aec00b8c83f7` |

The last row proves the failed first adjudication remains byte-identical and
separate. It is historical failure evidence, not silently reclassified as a
pass. The current `coverage.json` is also unchanged from that audit because the
repair strengthens admission of those exact existing bytes without changing
their correct serialized coverage record.

## Independent binding review

The repaired `complete_module_candidate_coverage()` now declares two separate
constants:

- exact rereview SHA-256
  `adfe7d63fe3325906f6dc7c7d259c9b5f92a297b702b12c72467cae5f5977218`;
- exact independently reviewed build-receipt SHA-256
  `94f1f1f13f255a060ebdd4e1153f509f058a7be85a656f898f8bc153a4ee1099`.

At `coverage.py:405–409`, the actual rereview bytes must hash to the former and
must contain both the exact closing statement and the reviewed receipt hash.
At lines 410–411, the current generated build-receipt bytes must independently
hash to the latter. Only after those checks does line 446 expose the same hash
in the candidate record. Thus an unchanged report can no longer authorize a
coherently changed receipt.

I parsed the complete current coverage JSON and independently hashed its two
referenced evidence files. Both row values equal the actual bytes and the two
constants above. I also verified the current producer receipt remains a
pre-review receipt rather than being rewritten as approval:

- `status: structural_pass_independent_cross_component_review_pending`;
- `independent_cross_component_review: pending`;
- `human_language_review: false`;
- visual, integrated-browser, screen-reader, and listening review: all `false`;
- `synthesized_audio_files: 0`; and
- `whole_module_complete: false`.

## Independent rejection probes

All probes were in-memory patches; no artifact was written.

### Coherent producer plus saved build receipt

I reran the exact counterexample from the failed adjudication: generate the
current product map, add
`_coverage_adjudication_probe: coherent-unreviewed-build-receipt` only to the
build receipt, reserialize it with two-space indentation and a trailing newline,
then make both `build_complete_a00_module.products()` and `Path.read_bytes()`
return those same coherent simulated bytes. The mutation retained SHA-256
`239c10e2ee5379291f767555d0eb61ef35a273b54bb4622325641dcf41959b87`.

It now rejects exactly as required:

```text
REJECTED ValueError Complete-module build receipt differs from independently reviewed bytes 239c10e2ee5379291f767555d0eb61ef35a273b54bb4622325641dcf41959b87
```

This is the same mutation and same mutated digest that the prior implementation
admitted as one candidate. The repaired boundary therefore directly closes the
reported defect.

### Rereview report pin

Appending an in-memory line only to the rereview report rejects:

```text
REJECTED ValueError Complete-module independent rereview evidence changed
```

### Saved build-receipt pin

Appending an in-memory newline only to the saved build receipt, while leaving
the producer output unchanged, rejects before adjudication:

```text
REJECTED ValueError Stale complete-module candidate: qa/a00-m81243-complete.build-receipt.json
```

The three independent probes therefore give `3/3` expected rejections. The new
focused regression independently reproduces the coherent case by patching both
producer output and simulated saved receipt, and requires the reviewed-bytes
error.

## Required commands and state

```text
python languages/jv-Latn-ID/scripts/coverage.py --check
Coverage matches: A00 75 + A10 82; 0 complete, 2 partial, 155 untranslated; all AX-2 module completions pending.
exit 0

cd languages/jv-Latn-ID/scripts
python -m unittest -v test_complete_a00_workflow.CompleteA00Workflow.test_coverage_records_candidate_without_advancing_module_count test_complete_a00_workflow.CompleteA00Workflow.test_coverage_rejects_coherent_unreviewed_build_receipt_mutation
Ran 2 tests in 14.746s
OK
```

An independent whole-JSON assertion pass confirmed:

- top-level `status: incomplete`;
- `completed_modules: 0`, `partial_modules: 2`, and
  `untranslated_modules: 155`;
- one complete-source `m81243` candidate;
- `producer_pre_review_state: pending`;
- bounded `independent_cross_component_review.status: passed`;
- `human_language_review: pending`;
- `whole_module_complete: false`; and
- no effect on baseline counts pending human and integrated accessibility
  review.

## Scope and exclusions

The repaired automated coverage adjudication closes on only the exact hashes in
this report. Any changed rereview or build-receipt bytes require new independent
evidence and fail the current pins. No defect remains in the bounded boundary I
was assigned to readjudicate.

This audit does not provide native Javanese or Indonesian review,
educator/register approval, integrated-browser or visual inspection, keyboard
or screen-reader testing, pronunciation/prosody approval, listening or
voice/provider validation, audio synthesis, publication approval, whole-module
approval, A00/A10/AX-2 completion, or commissioned-assignment completion. It
does not authorize staging, committing, publishing, or changing shared coverage
state.
