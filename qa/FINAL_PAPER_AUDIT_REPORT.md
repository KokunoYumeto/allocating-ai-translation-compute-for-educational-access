# Independent final manuscript audit

## Audited snapshot

- `PAPER.md`: 186,340 bytes; SHA-256 `FFBF91F3B19E3DF1966E71608DCF96356FF467E7F6C4D545ED3F16F41CF59749`.
- `MODEL_SPEC.md`: 8,522 bytes; SHA-256 `0D7254C61152DCB1207AA2AA0EEC1DDF2599EFB23631C9C2B6276005BB4C96ED`.
- `RANKING_METHOD.md`: 3,375 bytes; SHA-256 `AB7FB1ECBC1728CB649C024AE3A49542166726CF73628117B2735EA8F01381BC`.
- `FACTOR_POLICY.md`: 9,754 bytes; SHA-256 `36724C1D3071A2578FEA5C0015233627952210085CC05C39EC6E236732BC60A9`.

The audit was read-only with respect to all central manuscript and data files. The only written artifacts are this report, the audit script, and its machine-readable results in `staging/final_paper_audit`.

## Verdict

**Pass. No release blocker or open audit finding remains in the audited snapshot.** The ranking, arithmetic, method boundary, source joins, citations, reference order, and manuscript tables reconcile.

Two substantive inconsistencies found during the audit were corrected before the snapshot above was frozen:

1. `PAPER.md` line 338 now correctly calls the 104-row object the **intervention matrix** and states its 80-interlanguage/24-accessibility decomposition. This agrees with lines 343–345 and `appendix_f_matrix_scope_counts.csv`.
2. `MODEL_SPEC.md` lines 81–86 now distinguish absent observed cache-write values from the explicit blank `cache_write_tokens` and status fields in the 12-row grant table. Missing cache-write data is not treated as zero.

Two additional nonblocking traceability/style findings were also corrected before the final snapshot: the excluded-package file is now named `table6_package_exclusions_noncardinal.csv`, avoiding collision with printed Table 6B, and the final reference blocks now pass the mechanical APA alphabetization check. The conclusion identifies IL-HU's modeled outputs as dual-territory Urdu rather than implying a newly emitted Hindi output.

## Machine-check results

The deterministic script ran 64 checks: **64 passed and 0 failed**.

Passed invariants include:

- all expected exact inputs were present and hashed;
- Table 1 source-file counts: 474 population observations, 80 population authorities, 209 candidate hypotheses, 105 prior scored rows, 37 expansion rows, 104 mixed matrix rows, 113 population links, 11 accessibility safeguards, 29 curriculum units, 13 curriculum portfolios, 94 OpenStax workload rows, and 60 portfolio-compute rows;
- 133 eligible cardinal interventions, positions 1–133 without gaps, and 136 output equivalents because three non-Top-100 interventions emit two localized outputs;
- exact Top 10 order: Indian Bengali, Bangladesh Bangla, Telugu, Marathi, Vietnamese, Javanese, Indian Tamil, Western Punjabi, Gujarati, Kannada;
- `TOP_10.csv` is a full-row-identical prefix of `TOP_100.csv`;
- 100 unique Top-100 intervention IDs, all `natural_language_edition`, each with one output;
- admission counts 40/40/20 in the Top 100 and 57/56/20 in the full 133-row exposure order;
- every conservative score is zero and every conservative rank interval is `[1,133]`;
- Top-100 gross-token sums of 91,273,700 low, 407,304,900 base, and 1,866,457,100 high;
- all 12 grant scenarios, including cardinal counts, output-equivalent counts, gross tokens, and displayed aggregate API-equivalent costs;
- all grant cache-write values blank with `not_observed_not_assumed_not_zero` status;
- zero cardinal packages, zero package IDs in the Top 100, and all four complete shared-core architectures noncardinal because both upstream union gates are false;
- every Top-100 first product is FR-2/D3; next allocations are exactly 36 MV-1/D2, 44 MV-1/D3, and 20 SB-1/D3;
- the Top-100 curriculum mapping agrees row-by-row with the Top-100 IDs, first-product tokens, next products, and depths;
- regional record counts of Asia 57, Africa 24, Americas 35, Oceania 12, Europe 5; Top-100 counts of 57, 24, 12, 2, and 5 respectively;
- all 11 accessibility safeguards remain unselected and noncardinal;
- all 15 interlanguage summary IDs remain nonrankable under current evidence;
- exact 209-row existing-work states: 189 missing, 18 partial, 2 researched, and zero in the other candidate-register states;
- all 54 source IDs used by Table 2 or the Top 100 resolve uniquely; 51 witnesses hash-pass and the three absent witnesses are explicitly identified as `NO_WITNESS_REGISTERED` rather than passed;
- all 21 corpus/method crosswalk rows pass current byte and SHA-256 checks;
- printed Tables 2, 3, 4, 5, 6A, 6B, 7, 8, and 9 equal their machine rows after presentation formatting;
- all 31 artifacts printed in Appendix A match current bytes and SHA-256 values;
- Appendix I contains every exact APA draft and source note from all 54 source-crosswalk rows;
- every main reference family has an in-text citation;
- no unsupported positive claim of dynamic residual recomputation, Monte Carlo analysis, fresh-output-equivalent efficiency, or numeric equity/prestige optimization;
- no malformed Markdown tables, heading-level jumps, patch/conflict markers, unbalanced code fences, local account/person identifier, or accidental current-publication/approval assertion.

## Claim and method audit

### Population and education-language claims

The Walter–Benson discussion at `PAPER.md` lines 58–80 is bounded correctly to Table 14.2, p. 283: 97 large languages, 52 used in education, 45 not used; 3,741,110,588 versus 2,300,263,716 people; and 61.9% versus 38.1%. The manuscript explicitly says the chapter prints size bands rather than the 97 language names and does not distribute the aggregate percentage across modern targets. The independently derived 45-plus-662 subtotal is arithmetically correct: 1,120,220,125 + 968,356,346 = 2,088,576,471, or 90.797262% of 2,300,263,716.

The World Bank 37% student estimate is kept separate from the Walter–Benson population calculation. The South African phase-specific administrative counts at lines 214–222 are presented as principal-reported EMIS cells with verification caveats, not as a global or causal multiplier.

### Implemented selector

`PAPER.md` sections 6.2–6.5, `MODEL_SPEC.md`, `RANKING_METHOD.md`, and `FACTOR_POLICY.md` now describe the same implemented system: a fixed FR-2/D3 comparator; exact-profile eligibility; one canonical observation per natural row; five reported views; three allocating lanes in base → optimistic → scarcity order; and a fail-closed package substitution gate. They correctly state that the current selector does not dynamically recompute `U_selected_portfolio`.

Equity, vitality, prestige, feasibility, and dialect risk remain descriptive fields, not numeric objectives. Monte Carlo, one-at-a-time factor perturbation, empirical reuse calibration, learning-adjusted optimization, and fresh-output-equivalent efficiency are not claimed as implemented.

### Existing work and curriculum depth

The Indonesian deficit is correctly token-weighted: 185,429 / 367,220 = `0.5049501669`; the manuscript distinguishes that value from the larger 401 / 722 = 55.540% unfinished-unit share. Every cardinal first product is FR-2 at D3. Western Punjabi's `MV-1 (D2)` in Table 4 is its *next* allocation, not a D2 first product. The appendix mapping consistently labels all 100 first products D3.

### Interlanguage boundary

No interlanguage or package occupies a cardinal position. IL-HU's modeled outputs are now described precisely as dual-territory Urdu rather than implying that the existing Hindi baseline is a newly emitted output. The manuscript gives no blanket family multiplier to Interslavic, Germanic, Romance, Turkic, or any other bridge hypothesis. Shared-core savings are labeled unobserved engineering sensitivities, and diagnostic component subtotals are not presented as unique people.

### Source and citation closure

All main reference families appear in the body. OpenStax's eight exact repository snapshots are all cited; Open Logic, CLDR, SONAR, the recovered local formalism, the South African curriculum/orthography authorities, and the Wikimedia dataset authorship resolve through their source crosswalks. Appendix I reproduces the 54 source-authority references and notes exactly. The three population authorities without registered local witnesses remain prominently disclosed in Appendix B and the crosswalk.

## Reproduction

Run from the task root:

```powershell
python staging/final_paper_audit/audit_current_manuscript.py --write
```

The script writes `MACHINE_CHECK_RESULTS.json` beside itself and does not mutate central files.
