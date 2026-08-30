# Factor-assignment and uncertainty policy

## Purpose

This policy operationalizes `MODEL_SPEC.md` without converting heterogeneous
census labels into fictitious counts of harmed students or likely users. It
keeps three quantities separate:

1. **source population observation**: the exact count and measure printed by a
   source;
2. **new-edition access ceiling**: the part of that observation for which the
   target edition is linguistically and technically usable; and
3. **marginal comfortable-access range**: the residual after subtracting
   evidenced access through an existing edition or academic lingua franca.

Only the third quantity is an `EMA` numerator. Neither the Walter–Benson 38.1%
global estimate nor the World Bank 37% LMIC-student estimate is multiplied into
named-language rows. Those sources establish scale and mechanisms, not a
language allocation key.

## Data layers

### Layer 1: observations

`population_observations_master.csv` preserves every dated, source-reported
measure. Counts with different units, years, nesting, modalities, or territorial
coverage are not summed. Each row remains a gross observation.

### Layer 2: intervention edges

An edge links one exact intervention to one compatible observation and records:

- whether the language/variety, territory, script, modality, and cohort match;
- which observation is preferred when aggregate and component alternatives
  coexist;
- low/base/high written or modality access;
- low/base/high comprehension of the proposed surface;
- existing same-language-edition coverage;
- academic-lingua-franca overlap;
- curriculum relevance and source scarcity;
- evidence IDs and whether each value is observed, derived, proxy, or scenario;
  and
- an overlap-group key that prevents additive use of the same people.

No machine join suggestion becomes a scoring edge without this curation.

### Layer 3: implemented portfolio results

The frozen cardinal set contains one canonical observation per natural-language row.
Packages may consume those rows only through the explicit fail-closed link/matrix
union gate; the current build authorizes none. Observation-ID uniqueness therefore
prevents current cardinal duplication. Semantic HTML, offline delivery, audio, plain
language, signed-language products, and other accessibility mechanisms remain a
separate safeguard backlog because their residual beneficiary counts are not yet
cardinally comparable.

The selector does not yet recompute a fractional residual after every admission.
Claims of sequential `U_selected_portfolio` optimization must be deferred until such
an edge-level residual algorithm and tests exist.

## Factor rules

### `N`: source population

- Preserve the exact source count, year, unit, and label.
- Prefer an exact same-name mother-tongue component to a broader census-language
  category for a standard named edition, while retaining both as nonadditive
  alternatives.
- Household counts, oral ability, ethnicity, refugee totals, school enrolment,
  and total speakers are never silently converted into one another.
- A population projection may be added only as a separate row with its own
  method and interval; it never overwrites the source-year count.

### `D`: missing-content deficit

The common comparator is the complete FR-2 Formal Reasoning Core at D3. Two
decision frames are mandatory and may not be mixed:

- In the **ex-ante equal-treatment ranking**, `D = 1` for every language at the
  common pre-production baseline. This asks whether the language belonged in the
  opportunity set; later successful production cannot retroactively disqualify it.
- In **forward allocation**, `D = 1` only when no exact target-profile edition of
  the selected product exists. This means the named content is absent in that
  profile; it does **not** mean every speaker is educationally harmed.
- `D = 0` for a duplicate of an already complete exact edition.
- For a partial exact edition, `D` is the fraction of measured source tokens not
  yet covered. Indonesian completion therefore uses the exact remaining-token
  share, not unfinished file share.
- Language-of-instruction mismatch is reported as a separate context or learner
  stratum unless the source measures the exact target cohort. Country-level
  primary-school mismatch is never multiplied into all speakers of one language.

### `C`: comprehension of the proposed linguistic surface

- For an exact named natural-language output, `C = 1` is a **target-definition
  identity conditional on literacy in that standard**, not a claim that every
  speaker understands advanced mathematics. Literacy/modality access belongs in
  `P`; curriculum preparedness and adoption are reported separately.
- For a localized output from a shared semantic core, the same rule applies only
  to that named localized output. Shared-source reuse changes compute, not reach.
- A constructed bridge receives numeric `C` only from an exact surface, script,
  cohort, and relevant task. A short-cloze score may appear only in a clearly
  labelled upper-bound sensitivity and cannot be called sustained mathematical
  comprehension.
- Unknown cross-language comprehension is zero in the conservative portfolio and
  remains missing—not 0.5—in the evidence-backed table.

### `P`: practical written or modality access

Preference order:

1. exact language- and modality-specific literacy/access count;
2. exact language-specific rate applied to its matching source denominator;
3. a territory-level literacy or infrastructure rate shown only as a proxy
   sensitivity; or
4. `[0, unknown, 1]` when none exists.

A territory proxy is never relabelled as language-specific evidence. For the
neutral proxy sensitivity only, the national adult-literacy rate may be used as
the base written-access factor, with low `0` and high `1`; the full width is
deliberate. Internet and electricity rates select delivery modes, not language
comprehension. Signed-language and disability interventions require their own
population or access stratum and do not inherit the entire written-language
population.

An oral-language ability count remains a population ceiling, not a written-access
count. The BPS 2022 Bahasa Indonesia row therefore uses the official 248,501,794
age-5+ oral functional-language point estimate for `N`, while the 96% territory
adult-literacy proxy remains an independently labelled `P_base` sensitivity.

### `U`: non-overlap

The implemented `U` sensitivity is factored as:

`U = U_existing_exact_edition × U_academic_lingua_franca`

`U_selected_portfolio` is not dynamically recomputed in the current selector.
Canonical observation selection, unique observation IDs, and fail-closed package
substitution provide the present deduplication boundary.

- A complete exact edition sets the duplicate-edition factor to zero. Partial
  editions use the measured residual content fraction in `D`, not a guessed
  reader fraction.
- India C-17 English-or-Hindi unions supply a category-level sensitivity only:
  low treats all reported overlap as already served, base treats half as
  comfortably served, and high treats one fifth as served. These are explicit
  assumptions because census language knowledge is not academic reading comfort.
- Where academic-lingua-franca overlap is unmeasured, the evidence-backed low is
  zero and the high is one. A neutral `0.5` value may be shown only as a separate
  global sensitivity, never as an observed base estimate.
- Existing English, Arabic, Persian, Hindi, Turkish, Spanish, Portuguese, or
  other editions reduce reach only for cohorts evidenced or explicitly modelled
  as comfortably able to use them. Official status or shared script alone gives
  no coverage credit.

### `R`: curriculum relevance

For the fixed FR-2 target-priority comparison, `R = 1` means “potential access
to this specified curriculum,” not predicted enrolment or learning impact.
It does not mean FR-2 is the highest-need product for every community. The separate
content-needs layer uses learner-stratum, attainment, curriculum, local open-material,
and implementation evidence to choose among foundational/prealgebra, secondary,
bridge/remedial, undergraduate-core, advanced/reference, and accessibility/offline
products. OpenStax expansion portfolios use their own named scope and cannot be
compared to FR-2 as if more content were a penalty. Population size alone never
selects the next textbook.

## Scarcity, equity, prestige, feasibility, and risk

- OpenAlex and Wikimedia counts are bibliographic/digital-presence proxies, not
  inventories of usable mathematics. Scarcity is therefore an ordinal band with
  the exact proxy counts printed beside it.
- Scarcity currently has one numeric view. Vitality/marginalization and
  prestige-domain value remain descriptive evidence; no equity or prestige ranking
  objective is implemented, and they never inflate the number of people.
- AI benchmark inclusion, local corpus support, typography/tooling, and model
  auditing remain feasibility context. They are not numeric selector weights.
- Dialect or standardization risk moves an unresolved macro-target into a
  target-resolution lane. It is an eligibility control, not a scored portfolio lane,
  and it never assigns a macro population to an invented surface.

## Implemented ranking views and exclusions

The current machine outputs report:

1. exact gross demographic ceiling per common FR-2 base compute;
2. conservative low-access/high-compute efficiency (currently a complete zero tie);
3. bounded base and optimistic sensitivities;
4. scarcity-adjusted base efficiency; and
5. fail-closed shared-core architecture comparisons outside the cardinal ranking.

Base, optimistic, and scarcity are the three admission lanes. Equity, endangered/
prestige, feasibility, accessibility, and one-at-a-time sensitivity portfolios are
not implemented numeric lanes and must not be described as published rankings.

Every Top 10 and Top 100 entry requires a rankable exact target and dated person
observation. Unresolved macro-targets, D0 profile/population mismatches, negative
controls, nonauthorized package unions, and accessibility ceilings appear outside the
cardinal list. Missing evidence is never converted into an affirmative package gate
or numeric precision.

## Falsification and update rule

Every factor row carries its source and status. Replacing a proxy or sensitivity
with direct evidence changes only that field and triggers deterministic rebuilds
of the edge table, portfolios, rank ranges, paper tables, and hashes. Volatile
translation-completion cursors are timestamped and regenerated at final analysis;
stable corpus denominators remain pinned.
