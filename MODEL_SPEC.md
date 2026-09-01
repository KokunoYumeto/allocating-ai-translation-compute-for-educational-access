# Marginal educational access per compute: model specification

## Current implementation notice — v1.1

The current selector is specified in the opening section of `RANKING_METHOD.md`
and implemented in `scripts/allocation_policy_v1_1.py`. It replaces the earlier
hard-coded exposure list with full-register selection, evidence-aware tied
fronts and an explicit operational allocation policy. Exact source populations,
estimated additional access and the decision to commission are separate outputs.

No scalar welfare optimum is claimed from heterogeneous gross-population
denominators or unmeasured academic-language overlap. R is the magnitude of
newly comfortable readership, not a raw population band; missing R/S/A/N evidence
remains unknown. Twenty-one current packages now have explicit source-informed
low/base/high planning judgments, with exact cohorts, scopes and threshold
reasoning in `staging/opportunity_planning_v1_1/asia_core.json` and
`large_profiles.json`. They are not measured effects or confidence intervals.
The recovered register's qualitative bands are preserved as
prior judgments, not silently promoted into measured access estimates. Exact-tag
matches may supply the independent high-reach, regional-depth or endangered/
prestige lane, but never an inherited numerical rank.

Scope-compatible R/S/A/N priors may inform the same FR-2 formal-reasoning domain;
they may not be copied onto ECE, TVET or small completion residuals. The baseline
uses only explicitly supplied central judgments, never an automatic midpoint.
Cautious/favorable, full-envelope and measured-only views remain separate. The
measured-only view is a diagnostic, not a prerequisite for recommendation.

Dispatch uses dynamic topological eligibility: once all remaining dominators
clear, an action competes immediately. Static evidence-front layers are diagnostic
only; an unknown/incomparable front cannot lock all better-studied later layers
behind it. Population observations without independently scoped learner/output
packages remain evidence, not manufactured commissions.

Exact work ownership is resolved before calibration/ranking using
`staging/component_work_ownership_v1_1.json`: locale, package, stage and modality
are all required. NAT-001 owns Bangladesh primary recovery; SHC-BN retains
preschool and Indian TVET. NAT-124 owns Hindi; IL-HU retains two Urdu outputs.
Active component keys must match their recalibrated opportunity scope. NAT-040
owns the Malaysian Malay FR-2 component; IL-IDMS is its architecture alias.
Reusable cores have no additional audience, and distinct stages remain distinct.

The current computation writes the full selected queue, the Top 100 and Top 10,
input/alias dispositions, package ownership and a hash-bound validation receipt.
The declared 6:3:1 lane schedule is a normative default; its sensitivity is
distinct from evidence uncertainty. Generic accessibility mechanisms are a
cross-cutting axis. National signed-language outputs retain their own language
identity and are not replaced by a universal signed or textual edition.

### Crosswalk to the recovered formalism

| Requested consideration | Current representation | Boundary |
| --- | --- | --- |
| Population sizes | Dated, typed source observations | Not automatically newly comfortable readers |
| Additional usable readership | R and exact learner/output identities | Unknown where no supported residual estimate exists |
| Scarcity of usable open material | S and stage-specific supply evidence | Bibliographic index counts are not textbook availability |
| Practical access | A plus explicit modality/delivery route | Audio/signed formats are not assigned low social value |
| Non-overlap | N, source nonadditivity and exact package ownership | No blanket family/bridge reach; do not discount the same overlap twice |
| Vitality and prestige | V/P and independent allocation lane | Not erased by raw population size |
| AI production and audit feasibility | F, source packages and actual tooling evidence | Model support is not population/comprehension evidence |
| Dialect/standard risk | D and a bounded profile-resolution action | No invented standard and no human-dependent hold |
| Compute efficiency | Category-resolved actual counters or separately labelled scenarios | Gross cached tokens are not fresh tokens, money or weekly allowance |

If R already measures a residual cohort after bilingual overlap, N is retained
as its provenance/diagnostic rather than multiplied again as a second numerical
discount. The present ordinal comparison does not multiply ordinal band labels.

## Historical fixed-comparator specification

The remainder records the earlier FR-2/D3 scenario model and its implementation
limits. References below to the "current selector", 134 rows, zero admitted
shared-core packages, and the base/optimistic/scarcity cycle refer to that
historical comparator, not the current commissioning queue. The source-token
and compute-category definitions remain applicable within their stated scope;
they are not cost estimates for every new ECE, TVET, audio or research package.

## Controlling local formalism

This specification extends, and does not replace, the recovered formalized
heuristic in `marginal_intelligibility_reach_20260816/SCORING_MODEL.md` (SHA-256
`4F8377EED3F4E44C346A568230EAD8E972F6C98AED1BAC8378CBB6B1C956F1C7`).
Its `R × S × A × N` opportunity dimensions, separate `V/P/F/D` modifiers,
readiness fields, exact-profile unit, and negative-control logic remain the
controlling definitions. The equations below add three things required by the
current question: explicit population intervals, set-overlap accounting, and a
compute denominator.

Every result will therefore retain the original bands alongside any numeric
scenario. Numeric precision may refine a band but may not silently redefine
what the band means.

## 1. Population cells

Let `c` denote a non-overlapping population cell defined by exact language
variety, territory, script/orthography, learner stratum, and reference year.
`N_c = [N_low, N_base, N_high]` is the relevant population, not automatically
the total ethnolinguistic population.

## 2. Implemented intervention unit

The implemented cardinal unit is one exact linguistic intervention `i` evaluated
against the fixed complete FR-2 Formal Reasoning Core at D3 depth (`k = FR-2/D3`;
210 units; 120,083 measured source alpha tokens). A natural row carries one dated
population observation. A source-audited recovered multi-output bundle retains one
pooled population interval once and pays the full modeled cost of every output; it
receives no speculative shared-core saving.

The general `(i,k)` formulation remains a conceptual extension, not the current
ranking unit. The fixed-comparator ranking is explicitly **ex ante**: candidate-specific
production already completed does not remove a language from the equal-treatment
opportunity set. A distinct **forward-allocation** table then replaces `D=1` with the
exact current remaining-content share and uses incremental compute. Recommended
OpenStax/Open Logic products are a separately costed second layer.
Accessibility mechanisms are a separate noncardinal safeguard backlog until their
residual access gain is measured or bounded.

## 3. Implemented marginal-access sensitivities

For an eligible exact natural-language row `i`, the upstream score builder reports:

`MA_i^s = N_i × D_i × C_i × P_i^s × U_i^s`, for `s ∈ {low, base, high}`.

For the equal-treatment fixed first product, `D = 1` at the common decision baseline,
even when later production now exists; `C = 1`
is target-definition identity conditional on literacy in the named standard, and
curriculum relevance is held at `R = 1`. `P` and academic-lingua-franca non-overlap
carry disclosed low/base/high evidence or proxy statuses. The resulting values are
factor-model sensitivities, not observed harmed-population counts.

Forward allocation never reuses the ex-ante `D=1` mechanically. It subtracts exact
verified target × unit × format coverage and divides the resulting marginal-access
sensitivity by the incremental workload. `indonesian_equal_basis_and_forward_allocation.csv`
implements both estimands side by side so prior successful work cannot become either
an exclusion penalty or a double-counted future benefit.

The current selector does not recompute a continuous `U_selected_portfolio` after
each admission. Instead, upstream curation supplies one canonical observation per
natural row, portfolio construction requires globally unique observation IDs, and a
shared-core package may replace its enumerated natural rows only through the
fail-closed union gate in section 6. This is sufficient for the frozen portfolio but
is narrower than general residual-set optimization.

## 4. Implemented score views

The current build emits five score views over the fixed FR-2/D3 comparator:

- `gross`: source-bounded population ceiling divided by base gross tokens;
- `conservative`: low marginal access divided by high gross tokens;
- `base`: base marginal-access sensitivity divided by base gross tokens;
- `optimistic`: high marginal access divided by low gross tokens; and
- `scarcity`: scarcity-adjusted base access divided by base gross tokens.

Only `base`, `optimistic`, and `scarcity` allocate portfolio positions. `gross` is
reported as a ceiling. `conservative` is reported, but every current row has a zero
floor and therefore ties at `[1, 134]`. Equity, vitality, prestige, feasibility, and
dialect-risk fields remain separate evidence/descriptive dimensions; no numeric
equity-efficiency, prestige-efficiency, or endangered-language admission objective is
implemented in the frozen selector.

## 4.1 Population priority is not content priority

The headline score answers **where an exact language edition could create access**;
it does not answer **which mathematics that population most needs**. The second-stage
needs allocation therefore evaluates a product `k` separately by:

`NeedFit_ck = gap_level_ck × local_open_material_scarcity_ck × self_study_closure_k × practical_delivery_fit_ck`.

These terms are evidence labels or bounded sensitivities, not invented precision.
The product ladder distinguishes at least: foundational numeracy/prealgebra;
secondary algebra, trigonometry, precalculus, and statistics; bridge/remedial material;
undergraduate core; advanced/reference corpora; and accessibility/offline derivatives.
National or regional learning evidence, curriculum/OER inventories, and current exact
coverage select among those tiers. Population size alone never selects Algebra and
Trigonometry, and low national achievement never proves that translation is the sole
or primary remedy.

## 5. Implemented compute denominator and cache boundary

The scenario tables report:

`T_gross = T_uncached_input + T_cached_input + T_output`.

The observation schema reserves a `cache_write` field, but all eight recovered
observations leave it blank. Upstream scenario tables contain no populated cache-write
values; the grant-scenario table exposes an explicit blank `cache_write_tokens` column
and a status field on every row. The implementation therefore makes no cache-write
token claim and does not treat the missing quantity as zero. If a later
category-resolved usage record reports cache writes, that category must be added
explicitly and the gross/token-price formula versioned.

The low/base/high workflows model translation, critique, correction, build/QA, and
retry coefficients from measured source-token and unit denominators. They are
planning extrapolations, not recovered usage. API-equivalent prices apply the dated
uncached-input, cached-input, and output rates to those categories. Weekly-plan
allowance, fresh-token accounting, cache-write accounting, and non-API program costs
are not derived. The implemented efficiency denominator is gross tokens; no
fresh-output-equivalent efficiency is produced.

## 6. Implemented fail-closed multicriteria commissioning screen

### 6.1 Natural-row eligibility

A natural row is eligible only when `recommendation_eligibility` equals
`provisional_eligible` and `profile_resolution_status` does not begin `requires_`.
The 13 source-audited profile recoveries are applied without changing their
population numerators; three exact blockers, four negative controls, and two D0
profile/population mismatches remain outside the cardinal set.

### 6.2 Shared-core substitution gate

A shared-core package can replace its constituent natural rows only when all of the
following hold: at least two named outputs are planned; every named output has one
exact populated cell; the marginal-score join is complete; no territory-proxy output
is used; all exact constituent natural rows exist; low/base/high access sums reconcile
within the deterministic integer tolerance; base shared-core tokens are lower than
independent named-output tokens; observed reach is positive; the package does not
overlap a previously selected package; and both frozen upstream controls affirm the
union (`all_selected_links_usable_as_package_population_total=true`,
`all_planned_matrix_rows_rankable_under_current_evidence=true`, and the combined
package rankability field is true). Missing authorization fails closed. The current
model authorizes zero packages; the four complete compute-saving architectures remain
noncardinal engineering sensitivities.

### 6.3 Tie-aware ranks and admission

For each emitted three-decimal score, a tie group receives interval
`[1 + count(score > x), count(score >= x)]`. The current informative lane order is
`base → optimistic → scarcity`. Within each lane candidates are sorted by descending
lane score, then by the sum of available informative-rank midpoints, then by ascending
intervention ID. A lane admits its highest remaining candidate. If that candidate was
already admitted through another lane, the lane advances to its next unadmitted row.

After each three-lane pass the cycle repeats. When a lane is depleted, it is skipped;
the remaining lanes continue in their fixed relative order. In the corrected 134-row
portfolio, scarcity depletes after 20 admissions and base/optimistic continue to
57/57 total admissions. Failure of every lane to progress while rows remain is a
deterministic error. The first 10 and first 100 rows of this full exposure order are
the headline commissioning lists.

Accessibility interventions do not fill linguistic positions. No family population
is credited to a constructed bridge without exact target/task evidence.

## 7. Implemented uncertainty boundary and update rule

The current analysis propagates low/base/high access and compute scenarios, reports
tie-aware intervals across base/optimistic/scarcity views, preserves the degenerate
conservative tie, and exposes low/base/high shared-core reuse assumptions. It does not
run one-at-a-time factor perturbations, Monte Carlo uncertainty, equity/prestige
objective weights, learning-effect adjustment, or empirical reuse calibration.

Those analyses may be added only as deterministic, source-versioned outputs. Until
then the durable method and paper must call them unimplemented rather than implying
that they were run. Replacing a proxy with direct evidence triggers rebuilding the
score, package, portfolio, rank, paper-table, and hash outputs.
