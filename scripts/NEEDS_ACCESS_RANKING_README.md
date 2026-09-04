# Executable need/access ranking

`needs_access_ranking.py` implements three deliberately separate rankings:

1. Order L: exact-language-target unmet need, with disjoint territory cells summed once and package rows deduplicated;
2. Order A: intrinsic package-level public educational need and expected access gain;
3. Order B: expected package-level access gain per standardized fresh-equivalent compute, joined only after Orders L and A are complete.

The intrinsic function has no compute argument. The second function accepts frozen intrinsic rows and a separate compute table whose `compute_scope` must be exactly `standardized_from_scratch`. Neither function reads local holdings, prior translations, current work, completion, production, reuse, readiness, project, or user-priority variables.

## Intrinsic equation

Each candidate has exactly one nonnegative population factor and one or more ordered conditional rate factors:

```text
intrinsic_gain = population
                 * conditional_need_1
                 * ...
                 * conditional_need_n
                 * conditional_access_gain_1
                 * ...
```

The input must establish that the rates form a conditional probability chain. `conditional_order` records that chain; it is not a weight. Every production factor also identifies its unique event, numerator, denominator stratum, and immediate parent event. The scorer rejects duplicate IDs, self-loops, broken parentage, and unrelated marginal indicators.

Low/base/high propagation is monotone:

```text
gain_low  = product(all factor lows)
gain_base = product(all factor bases)
gain_high = product(all factor highs)
```

If any required endpoint is blank, that result is blank. In particular, blank is never converted to zero or `0.5`.

When joint draws are supplied, each candidate's point score is the mean of its complete joint score draws, not a product of marginal means. P05/P50/P95 and rank distributions are computed from the same draws. Shared `draw_set_id` and `draw_id` values preserve cross-candidate dependence.

## Standardized from-scratch efficiency equation

After intrinsic ranking:

```text
efficiency_low  = intrinsic_low / compute_high
efficiency_base = intrinsic_point_score / compute_base
efficiency_high = intrinsic_high / compute_low
```

With joint `compute_new` draws, gain and compute are divided within the same draw before posterior summaries are calculated. A standardized compute-base constant is used only when gain draws exist but compute draws do not; the output labels this basis.

Changing the compute table can change only the efficiency output. It cannot alter intrinsic eligibility, scores, ties, overlap units, or ranks.

## Input contracts

### Candidate identities

Required executable headers include:

```text
candidate_id,target_label,language_target_id,language_target_label,
territory_cell_id,country_code,measure_class,language_need_measure_class,
endpoint_id,horizon_months,learner_stage,subject_domain,package_id,
delivery_format,stratum_compatibility_key,eligibility_status,
rankability_status,universe_version,overlap_group_id,overlap_rule,
overlap_evidence_source_id,overlap_evidence_source_url,
overlap_evidence_source_class,overlap_evidence_is_public
```

`measure_class` and `language_need_measure_class` must belong to closed, versioned comparability registries; an arbitrary string cannot create a private rank pool. `intervention_key` is derived from exact language target, territory cell, package, stage, domain, and delivery format. One language target can therefore have many package interventions without multiplying Order-L need.

Production Order L also requires a frozen population partition, exact cell and denominator definitions, and a normative joint-need component identity. Renamed or alternate-valued copies of one source/denominator basis are rejected, as are unlike need-event chains summed under one language target. Order-L status gates match Order A: structural-zero, interval-only, and insufficient-evidence rows receive no positive point rank.

`overlap_rule` is `none` or `max_union`. `max_union` is accepted only when every member has the same country, stratum compatibility key, endpoint, horizon, measure class, and exact public overlap-evidence identity. A shared group string alone has no semantics.

### Long-form public factor sources

Required headers:

```text
candidate_id,factor_name,factor_role,conditional_order,
factor_measure_class,low,base,high,unit,value_scale,
source_id,source_url,source_class,is_public,country_context_field,
event_id,numerator_definition,denominator_stratum_id,condition_on_event_id
```

- `factor_role`: `population`, `need`, or `access_gain`.
- `conditional_order`: population is exactly `0`; conditional rates use unique positive integers.
- `value_scale`: explicit normalization, such as `0.01` for percentages or `1000` for thousands of people.
- After scaling, population units must be `persons` or `learner_years`; conditional-rate units must be `proportion`.
- `source_class`: `public_empirical` or `public_model` for real runs. `is_public` must be true.
- `country_context_field`: optionally obtains the base value from the row selected by `country_code` in `COUNTRY_CONTEXT.csv`. Direct `base` and a context field may not both be supplied.
- `low`, `base`, and `high` may be blank independently. The scorer preserves those blanks.

Every empirical factor requires a public HTTP(S) source ID and URL. Factor names are accepted only from `INTRINSIC_FACTOR_REGISTRY.json`; a free-text term such as `observed_cost` is rejected even if labeled as need. Context joins are also factor-, orientation-, and stage-specific: for example, late-primary learning poverty can enter registered primary educational need, while adult literacy and internet use cannot be relabeled as that need.

`resource_gap` additionally requires a versioned counterfactual baseline, observation date, exact functional route and endpoint, resource-audit group hash, finding status, and programme-exclusion registry hash. Both hashes are recomputed from canonical bytes, and the scalar must equal the exact route/endpoint derivation row in those bytes. Current functional learner access is distinct from open-license/adaptation/redistribution capability; open-only eligibility applies to intervention source selection, not to whether an existing closed resource currently serves a learner.

### COUNTRY_CONTEXT

The table must contain a unique `country_code`. Other columns are read only when an allowlisted factor row names one through `country_context_field`; unused context columns cannot influence results. Fields whose names indicate local work, project, reuse, asset, status, or user-priority information are rejected when requested.

### Standardized fresh-compute sources

Required headers:

```text
candidate_id,language_target_id,package_id,learner_stage,subject_domain,
delivery_format,compute_scope,
compute_measure_class,compute_low,compute_base,compute_high,compute_unit,
source_id,source_url,source_class,is_public,formula_version,
factor_registry_version,compute_input_set_hash,compute_derivation_set_hash,
factor_registry_file_hash,compute_model_role,compute_evidence_status,
benchmark_profile_id,tokenization_measurement_set_sha256,
measurement_profile_registry_file_sha256,measurement_profile_set_hash,
direct_measurement_row_hash,compute_binding_mode,successor_roster_file_sha256,
target_binding_row_hash,target_binding_set_hash,order_b_eligible
```

`compute_scope` must be `standardized_from_scratch`. The candidate/package/stage/domain/format fields must exactly reproduce the composite intervention endpoint. All nonblank compute values must be positive. Production estimates additionally require `--compute-derivations`, `--compute-inputs`, `--compute-tokenization-measurements`, `--compute-measurement-profiles`, `--compute-successor-roster`, `--compute-target-bindings`, and the closed registry selected by `--compute-factor-registry`. The scorer verifies exact bytes and semantic row/set hashes across the tokenization measurements, 203 direct profiles, exhaustive frozen-roster bindings, normalized factor inputs, canonical derivations, and the pinned identity-coefficient F001–F048 registry. Only `FROZEN_SUCCESSOR_BINDING` rows whose target binding is `DIRECT_PROFILE_BOUND` and `order_b_eligible=true` can enter production point order. Missing/unmatched targets have no compute row and remain explicitly unranked. `PROFILE_CONTRACT_EXAMPLE` rows are accepted only by the focused test API and are rejected by the production CLI. Common-envelope sensitivity rows, coordinated relabel+rehash proxies, nonidentity registries, and unmeasured targets are rejected.

### Joint draws

Required headers:

```text
draw_set_id,draw_id,candidate_id,factor_name,value
```

Intrinsic draws use the declared factor names. `compute_new` is reserved for standardized fresh-compute draws. Incomplete candidate/draw cells do not become zero and do not produce a score for that draw. An incomplete gain/compute grid remains a diagnostic and cannot receive a posterior point rank.
Draw values are already in canonical post-scaling units; factor-table `value_scale` is not applied a second time.

## Ranking and uncertainty

- Point ranks are descending competition ranks: `1,1,3`, never arbitrary unique ranks.
- A global pool has one common benefit unit. `persons` and `learner_years` remain uncombined unless an evidenced, versioned conversion is supplied.
- Exact equal scores share a deterministic `tie_group`; `candidate_id` sorts display rows only.
- Low/high intervals produce conservative partial-identification ranks within the declared common-benefit comparison pool:

```text
best  = 1 + count(other.low > candidate.high)
worst = n - count(other.high < candidate.low)
```

- `definite`, `possible`, and `outside` Top-K states follow those rank bounds.
- Joint draws additionally report median rank, P05/P95 rank, and Top-K inclusion probability. Every point-mass competitor is copied into every shared draw. Differential or incomplete candidate draw grids are not averaged over a favorable subset; they fall back to the identified deterministic base or remain unranked, with explicit status.
- No uncertainty width or evidence status becomes a score penalty.

## Overlap units

Compatibility- and evidence-valid `max_union` groups retain a draw-wise maximum only as a substitution diagnostic. Qualitative source identity does not identify unique union benefit or sequential marginal gain, so a multi-member group receives no portfolio point rank. Candidates with `overlap_rule=none` remain separate diagnostic units.

This is an explicit substitutability model, not an independence assumption. More complicated overlaps require a separate public joint-effect model rather than relabeling them `max_union`.

## Factor-removal sensitivity

`factor_removal_sensitivity` recomputes the intrinsic low/base/high model after removing each non-population factor for which the remaining model still has at least one need and one access-gain factor. These are labeled sensitivity rankings and never overwrite the primary ranking.

## Forbidden-field noninterference

Each input type is projected onto a fixed field allowlist before scoring. Extra fields—including project status, user priority, existing work, asset inventory, local completion, and reuse—are ignored and cannot enter output rows or tie-breaking. The tests add, delete, permute, and set extreme values for such fields and require the complete serialized ranking rows to remain identical.

## Synthetic replay

The fixtures under `tests/fixtures/needs_access_*_synthetic.csv` are invented unit-test values. They are not empirical evidence and the production default rejects them.

From the `from_scratch_20260901` directory:

```powershell
python scripts/needs_access_ranking.py `
  --candidates tests/fixtures/needs_access_candidates_synthetic.csv `
  --factor-sources tests/fixtures/needs_access_factor_sources_synthetic.csv `
  --country-context tests/fixtures/needs_access_country_context_synthetic.csv `
  --compute-sources tests/fixtures/needs_access_standardized_compute_synthetic.csv `
  --joint-draws tests/fixtures/needs_access_joint_draws_synthetic.csv `
  --language-output tests/tmp_needs_access/language_targets.csv `
  --intrinsic-output tests/tmp_needs_access/intrinsic.csv `
  --efficiency-output tests/tmp_needs_access/efficiency.csv `
  --portfolio-output tests/tmp_needs_access/portfolio.csv `
  --factor-removal-output tests/tmp_needs_access/factor_removal.csv `
  --validation-output tests/tmp_needs_access/validation.json `
  --top-k 2 `
  --allow-synthetic
```

Run the verification suite:

```powershell
python -m unittest -v tests/test_needs_access_ranking.py
```

The validation JSON records input/output hashes, measure classes, missing point estimates, ignored columns, removed factors, and the enforced split contracts. It contains no empirical values beyond those already present in the supplied input/output tables.
