# Ranking method and comparability rule

## Current v1.1 method: evidence first, explicit allocation policy second

The current commissioning lists are built by
`scripts/build_authoritative_exposure_portfolio_v1_1.py` and the pure selector
`scripts/allocation_policy_v1_1.py`. The former hard-coded 100-entry order has
been removed. Candidate membership comes from the complete registered candidate
table, exact-profile expansion, expected-universe gaps, and explicitly defined
shared-source architectures. Generic accessibility mechanisms and the completed
Indonesian baseline retain separate dispositions; they are not fictitious new
language populations. Exact-profile aliases are collapsed only when their tags
match, not merely because two observations name the same language.

Three different results must not be conflated:

1. **Typed gross opportunity:** the source's count, denominator, territory,
   cohort and date. L1, home-language, oral ability, territory and literacy
   measures are not interchangeable or automatically additive.
2. **Marginal-intelligibility evidence:** the controlling R/S/A/N dimensions,
   with V/P/F/D separately visible. Unknown newly comfortable readership is
   unknown, not zero and not a renamed census population. A strict dominance
   relation may leave broad tied fronts when the evidence cannot distinguish
   benefit. Twenty-one current packages have explicit, source-informed qualitative
   calibrations with central judgments and uncertainty endpoints. Historical
   R/S/A/N priors transfer only to an exact-profile compatible FR-2 domain;
   profile-level modifiers remain distinct when the package scope changes.
3. **Operational commissioning sequence:** a reproducible allocation policy
   that makes a useful decision despite incomplete evidence. Its unique
   positions are not estimates of relative welfare or a demonstrated optimum.

The policy gives six high-reach, three regional-depth and one endangered/prestige
turn per ten while all lanes remain populated. This is a disclosed prioritization
choice, not an empirical estimate of the correct budget share. Within the
currently undominated actions it first considers stage-specific need evidence,
rotates compatible source-denominator subqueues, then uses typed gross-scope
bands, target precision and a supported delivery route. Canonical ID is only
the final deterministic tie-break. Changing the policy must not alter source
counts or turn unknown evidence into observed values.

The dominance graph is updated as work is selected or covered. Static front
numbers are diagnostic only: they cannot force every unknown/incomparable row
ahead of a studied candidate whose dominators have already cleared. Separate
base, cautious, favorable and full-envelope runs use supplied ordinal judgments;
no midpoint is invented. Measured-only retains provisional judgments as priors,
not active measurements, but is not the gate for a recommendation. Policy-cycle
sensitivity leaves the opportunity inputs unchanged.

Observation-only candidates are not extra commissions. All 57 current OBS-derived
rows remain source evidence/dispositions unless a separate exact output, beneficiary
territory/cohort, stage and supported package exists. Country-of-origin tags do not
turn a diaspora census count into an origin-country population. Supply-rich controls
require their stated residual action, not a generic FR-2 fallback.

The selection receipt records the exact policy, per-row reason, comparisons,
unknown dimensions, package ownership, suppressed duplicates and input hashes.
Top 10 and Top 100 are exact prefixes of the full computed queue. The full queue
and non-admission/alias dispositions remain available, so omission from Top 100
does not erase a community or imply that its needs are zero.

Named output plus need/package/stage/modality identifies ownership. A shared
semantic core is a production architecture, not an additional audience. The
same Hindi package cannot be commissioned again merely because it appears in
both a Hindi row and a Hindi–Urdu bundle. A different explicitly scoped residual
remains a different action. Spoken Putonghua is not added to written Chinese;
Indonesian source reuse is not Malaysian readership.

The canonical component register is applied before any ranking: Bangladesh
grades 2–5 recovery belongs to NAT-001, caregiver/pre-primary and Indian TVET to
SHC-BN, Hindi first-year/methods to NAT-124, and the two Urdu locale outputs to
IL-HU. Every reused key must resolve to an actual active owner; residual
opportunity keys must match active-only components. The Malaysian FR-2 work is
represented by NAT-040, with IL-IDMS retained as an alias in diagnostics and the
architecture register. Its completed Indonesian source is not a new readership.

Tests require input-permutation invariance, genuine tied evidence fronts,
no population-only assignment to R, no mixed-denominator numeric dominance,
exact package deduplication and a visible reason for every operational choice.
Passing these tests establishes reproducibility and internal consistency, not
that every proposed package has a measured educational effect.

## Historical fixed-comparator method — not the current selector

The remaining sections preserve the earlier FR-2/D3 sensitivity analysis. Its
modelled values remain useful scenarios, but its eligibility gates, rank order,
134-row counts and base/optimistic/scarcity admission cycle do not control the
current Top 10/Top 100. In particular, a zero lower sensitivity bound is not
evidence of zero value, and an OpenAlex percentile is not a direct inventory of
usable textbooks for a target cohort.

## Common educational denominator

The cardinal target-priority comparison fixes the complete **FR-2 Formal Reasoning
Core** at D3 depth for every eligible linguistic intervention. FR-2 contains 210
source units and 120,083 measured source alpha tokens. OpenStax is a separately
costed next-allocation layer; accessibility interventions remain a separate
noncardinal safeguard backlog.

This first ranking is an **ex-ante equal-treatment comparison**. It holds the
decision baseline fixed before target-specific production, so work already completed
cannot remove Bahasa Indonesia or any other language from the opportunity set. A
separate forward-allocation table subtracts exact current coverage and compares the
next marginal product and incremental workload.

## Eligibility and factor boundary

A row enters the cardinal candidate set only when it has an exact production profile,
a dated person observation, `recommendation_eligibility=provisional_eligible`, and no
unresolved `requires_*` profile status. Source-audited recoveries preserve their one
population interval and multiply compute by the number of separately emitted outputs.
Negative controls, D0 population/profile mismatches, and unresolved profiles remain
outside the rankable set.

The current low/base/high marginal-access values are factor-model sensitivities:
`N × deficit × exact-target identity × practical access × academic non-overlap`.
They are not observed counts of educational harm or use.

Language priority and content priority are separate. After the exact language/profile
screen, a needs-allocation register chooses among foundational, secondary,
bridge/remedial, undergraduate, advanced/reference, and accessibility/offline products
from direct learning, curriculum, and open-material evidence. The old tertiary-
enrolment threshold remains only a fallback proxy and may not be reported as if it
proved that every population needs the same Algebra and Trigonometry volume.

## Fail-closed package substitution and deduplication

Natural rows use globally unique population-observation IDs. A shared-core package
may consume its enumerated natural observations only when named-output coverage,
constituent score joins, access-interval reconciliation, positive reach, and base
token dominance all pass **and** both frozen upstream link/matrix controls authorize
the union. Any missing or false authorization excludes the package. The current
portfolio admits zero packages and consumes zero observations.

The implemented selector does not continuously recompute `U_selected_portfolio`.
That broader residual-set algorithm is future work if overlapping cardinal cells are
ever admitted.

## Implemented views

- `gross`: population ceiling / base gross tokens (reported, not an admission lane);
- `conservative`: low access / high gross tokens (reported; currently all zero);
- `base`: base sensitivity / base gross tokens;
- `optimistic`: high sensitivity / low gross tokens; and
- `scarcity`: scarcity-adjusted base sensitivity / base gross tokens.

Equity, vitality, prestige, feasibility, and dialect risk are not implemented numeric
ranking objectives. They remain descriptive or target-resolution evidence.

## Deterministic multicriteria admission

Tie intervals are computed over each emitted three-decimal score as
`[1 + number strictly greater, number greater than or equal]`. The admission cycle is
`base → optimistic → scarcity`. Each lane chooses its highest-scoring unadmitted row;
ties are resolved by the sum of available informative-rank midpoints and then
ascending intervention ID.

The cycle repeats until all eligible rows have been exposed. A depleted lane is
skipped while the other lanes continue in their fixed relative order. If no lane can
progress while rows remain, the build fails. In the corrected 134-row build, lane
counts are base 57, optimistic 57, scarcity 20; the Top 100 prefix contains 40/40/20. The
conservative all-zero tie is disclosed but never used to manufacture admission order.

The complete exposure order is the commissioning screen. `TOP_10.csv` and
`TOP_100.csv` are exact serialized prefixes, not claims of a uniquely identified
universal welfare ranking.
