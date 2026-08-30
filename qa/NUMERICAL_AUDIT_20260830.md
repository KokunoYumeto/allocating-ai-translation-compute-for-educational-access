# Independent numerical audit — 2026-08-30

## Scope and snapshot

This audit recomputes the current cardinal counts, ordering, needs-assignment
counts, and compute scenarios from the bounded task directory. It does not edit
the paper or any analytical dataset.

The line locators below refer to the `PAPER.md` snapshot read at
`2026-08-30T01:07:01+02:00`: 200,820 bytes, SHA-256
`13A63114FFE23829AE6024CCFC292126B6C467E4164BCE1F03741892198683D2`.
Because the manuscript is being revised concurrently, the quoted anchor text is
controlling if later edits move the line numbers.

Principal recomputation inputs:

| Artifact | Rows | SHA-256 |
|---|---:|---|
| `natural_language_scores_v3.csv` | 106 | `096976FD45EB9B5EFC0D4D2C71730F861D51F6B18131AA56CD94876886A48BFD` |
| `candidate_expansion_scores.csv` | 37 | `B97383E20E9FAD2791BD4883082CF3985C66F08158670A466B9D82597BD43291` |
| `staging/resolve_unresolved_profiles/profiles.csv` | 16 | `BF9C0D68C07E74D35F8F2B96BDD81862CD381DCAFA3A99226C8990177E72B72F` |
| `negative_controls_and_profile_exclusions.csv` | 9 | `688248353B89534CDDE7E6957D261A7A40F3597ECFB9F3A0F3F05CFC2458517B` |
| `portfolio_linguistic_candidates.csv` | 134 | `0B99C00FC987F57C893BA8B0B1B91843D2CAEC0852F383249983904BC1945A9B` |
| `TOP_10.csv` | 10 | `E7287B63C063E21200F0D0C12E3C9E12828222ABF365563B4A6CF1BD1582FC48` |
| `TOP_100.csv` | 100 | `BB5894B135A77FA7EC6FBD854477025D0BF3ABA1FE476EA0F5430D6A9DF3CDE3` |
| `top100_needs_assignment.csv` | 100 | `7793FB8AF60E729B4B5178A3382F12CAA450E471629538756579D1809D306B19` |
| `portfolio_scale_planning.csv` | 45 | `75411459F126EFFD8EE3626759CCD596702B06081C0BAF2D34A6C204F4ED5107` |
| `table7_curriculum_allocation_summary.csv` | 4 | `34C83D6F7A93E30C8AACA980EBFC7246719956D791EB1AFA548148DF95F7D376` |

## 1. Eligibility and output counts

The current scoring universe has `106 + 37 = 143` rows. Before profile
resolution, its recommendation statuses are:

- 135 `provisional_eligible`;
- 4 `exclude_duplicate_or_explicit_control`;
- 2 `ineligible_D0_profile_population_mismatch`;
- 2 `target_profile_evidence_pending`.

Fourteen provisional rows initially have a `requires_*` profile state. The
profile-recovery table supplies 13 cardinal recoveries: ten one-output editions
and three two-output bundles. One provisional profile remains unresolved. Thus:

`135 provisional - 1 unresolved provisional = 134 eligible interventions`.

Equivalently, the final exclusion/control file contains nine rows: four richly
served controls, two D0 mismatches, and three unresolved localized-output
profiles; `143 - 9 = 134`.

The 134 interventions do **not** equal 134 outputs. The current portfolio has
131 one-output rows and three two-output rows:

| Position | Intervention | Outputs |
|---:|---|---:|
| 106 | `OBS-GRG-US-021` — CHamoru/Chamorro Guam + CNMI bundle | 2 |
| 120 | `OBS-GRG-US-006` — Choctaw Oklahoma + Mississippi bundle | 2 |
| 130 | `OBS-GRG-US-028` — Aruba Papiamento + Curaçao/Bonaire Papiamentu bundle | 2 |

Therefore the exact current modeled-output count is
`131 × 1 + 3 × 2 = 137`.

## 2. Current Top 10

The exact `TOP_10.csv` order matches positions 1–10 of `TOP_100.csv`:

1. `NAT-121` — Bahasa Indonesia (`id-Latn-ID`)
2. `NAT-001` — Bangladesh Bangla (`bn-Beng-BD`)
3. `NAT-003` — Telugu (`te-Telu-IN`)
4. `NAT-002` — Indian Bengali (`bn-Beng-IN`)
5. `NAT-028` — Vietnamese (`vi-Latn-VN`)
6. `NAT-006` — Marathi (`mr-Deva-IN`)
7. `NAT-004` — Indian Tamil (`ta-Taml-IN`)
8. `NAT-015` — Western Punjabi (`pnb-Arab-PK`)
9. `NAT-038` — Javanese (`jv-Latn-ID`)
10. `NAT-007` — Gujarati (`gu-Gujr-IN`)

The abstract and generated main-results tables state this order correctly.

## 3. Top-100 needs assignments

`top100_needs_assignment.csv` has 100 unique ordered rows:

- 10 `audited_primary_or_official_proxy` assignments, exactly positions 1–10;
- 90 `territory_proxy_only_not_a_content_commission` assignments, exactly
  positions 11–100.

Thus “10 audited / 90 needs-audit proxy” is the current exact split.

## 4. Fixed-source OpenStax comparator

The current `TOP_100.csv` groups are:

| Next fixed-source comparator | Interventions/outputs | Low gross tokens | Base gross tokens | High gross tokens |
|---|---:|---:|---:|---:|
| MV-1 / D2 | 36 | 39,137,220 | 156,816,432 | 670,681,044 |
| MV-1 / D3 | 43 | 69,334,447 | 235,382,774 | 906,173,443 |
| SB-1 / D3 | 21 | 62,944,707 | 238,856,625 | 989,359,497 |
| **Next-comparator subtotal** | **100** | **171,416,374** | **631,055,831** | **2,566,213,984** |

The common FR-2 / D3 Top-100 comparator contributes 91,273,700;
407,304,900; and 1,866,457,100 gross tokens. Adding it to the next-comparator
subtotal gives 262,690,074; 1,038,360,731; and 4,432,671,084 gross tokens.

## 5. One internally consistent Table 9 cost convention

Use the frozen **per-output planning cost** convention throughout Table 9:

`cost(scope, scenario) = sum over bundle groups g of [output_count(g) × portfolio_scale_planning.api_equivalent_usd_total(g, scenario, one output)]`.

That is, multiply the already two-decimal per-output planning costs in
`portfolio_scale_planning.csv`, then sum them. Do not describe these values as
repricing the aggregate token components. The per-output gross-token/cost rows
used are:

| Bundle | Low tokens / USD | Base tokens / USD | High tokens / USD |
|---|---:|---:|---:|
| FR-2 / D3 | 912,737 / $5.19 | 4,073,049 / $16.77 | 18,664,571 / $65.43 |
| MV-1 / D2 | 1,087,145 / $8.70 | 4,356,012 / $27.97 | 18,630,029 / $108.56 |
| MV-1 / D3 | 1,612,429 / $13.79 | 5,474,018 / $37.50 | 21,073,801 / $128.72 |
| SB-1 / D3 | 2,997,367 / $25.64 | 11,374,125 / $80.10 | 47,112,357 / $305.32 |

Under that single convention, every Table 9 row should be:

| Scope | Workflow | Interventions | Outputs | Bundle | Gross tokens | API-equivalent USD |
|---|---|---:|---:|---|---:|---:|
| Top-10 pilot | Low | 10 | 10 | 10 × FR-2/D3 | 9,127,370 | $51.90 |
| Top-10 pilot | Base | 10 | 10 | 10 × FR-2/D3 | 40,730,490 | $167.70 |
| Top-10 pilot | High | 10 | 10 | 10 × FR-2/D3 | 186,645,710 | $654.30 |
| Headline Top 100 | Low | 100 | 100 | 100 × FR-2/D3 | 91,273,700 | $519.00 |
| Headline Top 100 | Base | 100 | 100 | 100 × FR-2/D3 | 407,304,900 | $1,677.00 |
| Headline Top 100 | High | 100 | 100 | 100 × FR-2/D3 | 1,866,457,100 | $6,543.00 |
| Top 100 + fixed OpenStax | Low | 100 | 200 | 100 × FR-2/D3 + 36 × MV-1/D2 + 43 × MV-1/D3 + 21 × SB-1/D3 | 262,690,074 | $1,963.61 |
| Top 100 + fixed OpenStax | Base | 100 | 200 | same counts | 1,038,360,731 | $5,978.52 |
| Top 100 + fixed OpenStax | High | 100 | 200 | same counts | 4,432,671,084 | $22,397.84 |
| All eligible natural-language interventions | Low | 134 | 137 | 137 × FR-2/D3 | 125,044,969 | $711.03 |
| All eligible natural-language interventions | Base | 134 | 137 | 137 × FR-2/D3 | 558,007,713 | $2,297.49 |
| All eligible natural-language interventions | High | 134 | 137 | 137 × FR-2/D3 | 2,557,046,227 | $8,963.91 |

For avoidance of doubt, direct summation of the three gross-token columns in
`portfolio_linguistic_candidates.csv` produces the same all-eligible token
totals as `137 × FR-2/D3`.

An aggregate-token repricing convention is also mathematically valid, but it
is a different convention. Its corresponding API values would be $51.95 /
$167.72 / $654.29 (Top 10), $519.50 / $1,677.21 / $6,542.92 (Top 100),
$1,964.24 / $5,978.51 / $22,397.51 (Top 100 + OpenStax), and $711.71 /
$2,297.77 / $8,963.80 (all eligible). These values must not be mixed with the
per-output-planning values in one table.

## 6. Stale or inconsistent claims in the audited paper snapshot

1. **Candidate inventory:** `PAPER.md:423`, anchor “Candidate intervention
   hypotheses | 209,” is stale. `candidate_interventions_master.csv` now has
   210 rows.

2. **Table 9 cost convention:** `PAPER.md:797-802` uses aggregate-repriced Top-10
   and Top-100 costs, while `PAPER.md:803-805` uses the sum of rounded per-output
   planning costs. Under the selected per-output convention, use the values in
   Section 5 above for all rows.

3. **All-eligible rows:** `PAPER.md:806-808`, anchors “134 | 134 | 134 x
   FR-2/D3,” are incorrect. The intervention count is 134 but the output count
   is 137; the corrected tokens and per-output-planning costs are shown above.

4. **Cost note:** `PAPER.md:815-817`, anchor “Dollar values reprice aggregate,”
   does not describe the selected per-output-planning convention and did not
   describe the mixed table consistently. Replace it with the exact convention
   formula above.

5. **Appendix A manifest:** `PAPER.md:1208-1236` contains 16 byte/hash and/or
   row-count mismatches against live files. Numerically important examples are
   population observations 474→475, population authorities 80→81, candidate
   interventions 209→210, natural-score rows 105→106, eligible portfolio rows
   133→134, reconciliation rows 209→210, and global-gap rows 133→134. The whole
   manifest table should be regenerated rather than patched selectively.

6. **Appendix B order:** in `PAPER.md:1240-1352`, 52 of the 100 displayed
   positions disagree with current `TOP_100.csv`. Position 1 still shows Indian
   Bengali instead of Bahasa Indonesia. Regenerate the entire appendix.

7. **Appendix D counts:** `PAPER.md:1375`, anchor “209-row candidate register,”
   must be 210. `PAPER.md:1406`, the `partial` row, must be 19 rather than 18.
   The displayed `missing = 189` remains correct. The live reconciliation file
   has 210 rows: 189 missing, 19 partial, and 2 researched.

8. **Appendix F mapping:** in `PAPER.md:1478-1600`, 52 of the 100 displayed
   IDs/positions disagree with current `TOP_100.csv`. The summary distribution
   36 MV-1/D2, 43 MV-1/D3, 21 SB-1/D3 is correct, but the row mapping needs full
   regeneration.

9. **Grant scenario CSV:** `GRANT_COMPUTE_SCENARIOS_LOW_BASE_HIGH.csv` lines
   8–10 still encode the superseded 36/44/20 OpenStax split; lines 11–13 still
   encode 133 interventions and 136 outputs. Regenerate those six records from
   the current 36/43/21 and 134-intervention/137-output state.

10. **Rank-sensitivity artifact:** `figure_1_rank_sensitivity_data.csv` still
    begins with Indian Bengali and omits Bahasa Indonesia. It is a pre-correction
    Top-20 artifact and should be regenerated or excluded from the release
    manifest.

## Audit conclusion

The current cardinal ranking and needs split are sound: 134 eligible
interventions; Bahasa Indonesia first; the stated corrected Top 10; and 10
audited versus 90 proxy-only Top-100 needs assignments. The fixed OpenStax group
counts are 36/43/21. The remaining critical correction is to respect the 137
localized outputs in the full eligible set and apply one cost convention to all
Table 9 rows.
