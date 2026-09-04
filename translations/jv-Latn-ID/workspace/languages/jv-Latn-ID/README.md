# Javanese–Indonesian mathematics

Target: **Javanese, `jv-Latn-ID`**, under the commissioned assignment formerly
labeled rank 9; that research ranking has been withdrawn and is not objective
support for reranking or stopping this work. This is a bilingual translation and
academic-register scaffold, not a model-training or fine-tuning dataset.
Downloaded corpora are translation inputs only. The completed project allocation,
supply, and license decisions are binding; this work starts at acquisition.

## Register contract

- `jv-conversation`: explicitly labeled conversational Javanese (ngoko), for
  low-pressure oral explanation. This is not krama and is not presented as a
  universally appropriate way to address elders or teachers.
- `jv-academic`: explicitly labeled academic Javanese scaffold. Mathematical
  loan terms are declared in the terminology ledger, not silently substituted.
- `id-academic`: Bahasa Indonesia bridge to the assigned Indonesian textbooks.

Academic Javanese here is a **provisional pedagogical register**, not a claim of
standardization. Native Javanese educator review, regional wording review, and
recorded pronunciation/listening review are still required before learner release.

## Contents

- `sources.lock.json`: exact repository commits, source identities, and hashes.
- `provenance/`: retained notices and source-authority witnesses.
- `translation/`: reviewable XML translation inputs, with stable source anchors.
- `terminology.csv`: register-specific choices and review flags.
- `audio/`: formula/diagram narration and voice-provider-neutral SSML policy.
- `scripts/`: offline deterministic build and structural QA.
- `review/`: committed reader and narration outputs for review, not publication.
- `qa/`: machine receipt and limitations; `NEXT_UNIT.md`: next contiguous work.

## Build

From the project root, using Python 3.12 or newer (standard library only):

```text
python languages/jv-Latn-ID/scripts/build.py
python languages/jv-Latn-ID/scripts/qa.py
python languages/jv-Latn-ID/scripts/test_qa.py
```

The build has no browser/CDN/network dependency, no telemetry, and no automatic
TTS service call. SSML is a narration handoff, **not synthesized or reviewed audio**.
This lane has not pushed independently. The coordinator's single review branch
has an incomplete initial upload; complete publication of all lane snapshots is
not claimed. This is a review workflow, not a production release.

The eleven ordinary post-pilot excerpts are rebuilt independently after their
source-bound drafts. A separate four-root build preserves the noncontiguous
module title, metadata, recap and outer glossary positions. A complete-source
candidate then assembles those exact reviewed components without changing their
source-marked narration bodies. The commands also have read-only `--check` modes:

```text
python languages/jv-Latn-ID/scripts/draft_units.py --unit a00-place-value
python languages/jv-Latn-ID/scripts/build_units.py --unit a00-place-value
python languages/jv-Latn-ID/scripts/draft_units.py --unit a10-operation-symbols
python languages/jv-Latn-ID/scripts/build_units.py --unit a10-operation-symbols
python languages/jv-Latn-ID/scripts/draft_units.py --unit a00-digit-place
python languages/jv-Latn-ID/scripts/build_units.py --unit a00-digit-place
python languages/jv-Latn-ID/scripts/draft_units.py --unit a10-equality-symbols
python languages/jv-Latn-ID/scripts/build_units.py --unit a10-equality-symbols
python languages/jv-Latn-ID/scripts/draft_units.py --unit a00-name-whole
python languages/jv-Latn-ID/scripts/build_units.py --unit a00-name-whole
python languages/jv-Latn-ID/scripts/draft_units.py --unit a10-grouping-symbols
python languages/jv-Latn-ID/scripts/build_units.py --unit a10-grouping-symbols
python languages/jv-Latn-ID/scripts/draft_units.py --unit a10-expressions-equations
python languages/jv-Latn-ID/scripts/build_units.py --unit a10-expressions-equations
python languages/jv-Latn-ID/scripts/draft_units.py --unit a00-write-whole
python languages/jv-Latn-ID/scripts/build_units.py --unit a00-write-whole
python languages/jv-Latn-ID/scripts/draft_units.py --unit a10-exponents
python languages/jv-Latn-ID/scripts/build_units.py --unit a10-exponents
python languages/jv-Latn-ID/scripts/prepare_rounding_assets.py
python languages/jv-Latn-ID/scripts/prepare_rounding_bindings.py
python languages/jv-Latn-ID/scripts/build_units.py --unit a00-rounding
python languages/jv-Latn-ID/scripts/test_unit_workflow.py
python languages/jv-Latn-ID/scripts/test_digit_place_workflow.py
python languages/jv-Latn-ID/scripts/test_equality_workflow.py
python languages/jv-Latn-ID/scripts/test_name_whole_workflow.py
python languages/jv-Latn-ID/scripts/test_grouping_workflow.py
python languages/jv-Latn-ID/scripts/test_expressions_workflow.py
python languages/jv-Latn-ID/scripts/test_reader_contract.py
python languages/jv-Latn-ID/scripts/test_write_whole_workflow.py
python languages/jv-Latn-ID/scripts/test_write_whole_assets.py
python languages/jv-Latn-ID/scripts/test_exponent_workflow.py
python languages/jv-Latn-ID/scripts/test_exponent_assets.py
python languages/jv-Latn-ID/scripts/test_rounding_assets.py
python languages/jv-Latn-ID/scripts/test_rounding_workflow.py
python languages/jv-Latn-ID/scripts/prepare_whole_summary_assets.py --check
python languages/jv-Latn-ID/scripts/draft_summary.py --check
python languages/jv-Latn-ID/scripts/build_summary.py --check
python languages/jv-Latn-ID/scripts/test_summary_components.py
python languages/jv-Latn-ID/scripts/test_summary_workflow.py
python languages/jv-Latn-ID/scripts/prepare_section_exercise_assets.py --check
python languages/jv-Latn-ID/scripts/draft_units.py --unit a00-section-exercises --check
python languages/jv-Latn-ID/scripts/build_units.py --unit a00-section-exercises --check
python languages/jv-Latn-ID/scripts/test_section_exercise_assets.py
python languages/jv-Latn-ID/scripts/test_section_exercise_workflow.py
python languages/jv-Latn-ID/scripts/draft_complete_a00_module.py --check
python languages/jv-Latn-ID/scripts/build_complete_a00_module.py --check
python languages/jv-Latn-ID/scripts/test_complete_a00_assembly.py
python languages/jv-Latn-ID/scripts/test_complete_a00_workflow.py
python languages/jv-Latn-ID/scripts/coverage.py --check
```

These are excerpt/component readers and TTS-ready drafts plus one complete-source
review candidate, not a human-approved completed module. The full ledger remains
at zero completed modules, two partial modules, and 155 wholly untranslated
modules.

To reacquire/replay input provenance, run
`python languages/jv-Latn-ID/scripts/prepare_sources.py --acquire`.
The complete pinned upstream archive is 537 MB; the current ignored local path
is a read-only NTFS hard link to the verified shared archive, avoiding duplicate
disk storage. The separate Git checkout is sparse and is **not** a complete
media checkout. The lock distinguishes these inputs.

`canon/` contains a 50-entry official KBJI reference shelf (18 initial entries,
thirty-two topic-driven extensions) and stage-by-stage
consultation log. Reference pages are native HTML converted to readable text;
they are consulted again as drafting/narration/QA require, not merely collected.
Original user workflow messages are retained in `USER_INSTRUCTIONS.md`.

## Attribution and status

This unofficial pilot adapts selected OpenStax *Prealgebra 2e* and *Elementary
Algebra 2e* material through the assigned Indonesian editions by KokunoYumeto.
See `ATTRIBUTION.md` for retained attribution, exact boundaries, and notices.
OpenStax and Rice University do not endorse this adaptation. Their names, logos,
and marks are not licensed. Component-specific restrictions remain in force.

The pilot is an AI-assisted draft produced in Codex. It has not been approved by
a human Javanese translator, mathematics educator, accessibility specialist, or
voice performer. Structural QA does not constitute linguistic validation.
