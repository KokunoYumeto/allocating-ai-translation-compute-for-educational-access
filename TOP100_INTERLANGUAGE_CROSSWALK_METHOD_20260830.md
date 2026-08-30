# Top-100 interlanguage-overlap crosswalk method

Date: 2026-08-30

## Purpose and boundary

This crosswalk connects every natural-language row in `TOP_100.csv` to an existing interlanguage, shared-core, dual-script, or natural-intercomprehension architecture only when the current normalized matrices expose a specific language/profile relation. It is a compute-reuse and overlap-control layer. It is not a family-level demographic multiplier and it does not convert an architecture row into a comprehension claim.

## Authority order

1. `TOP_100.csv` fixes the 100 ordered natural-language interventions and exact target-profile tags.
2. `top100_needs_assignment_v2.csv` supplies the current needs/program assignment for the same position and intervention ID.
3. `staging/interlanguage_matrix/interlanguage_overlap_normalized.csv` supplies the exact edge, language/profile tag, script, territory, exclusions, double-count rule, source IDs, confidence, and current rankability.
4. `staging/interlanguage_bundle_model/interlanguage_intervention_matrix.csv` and `appendix_f_interlanguage_matrix_summary.csv` provide corroborating architecture and source-ID context.

## Matching rule

- **Exact profile match:** the Top-100 target tag equals the normalized edge tag.
- **Exact language/script and target-country cell:** the edge tag omits only the region suffix and its named territory explicitly contains the Top-100 target country. This adds four relations already represented by named matrix cells: South African Setswana, South African Sesotho, South African siSwati, and Pennsylvania German in exact United States communities.
- **Hypothesis only:** a language/script prefix aligns but the matrix territory is unresolved or incompatible. Official-standard Belarusian is retained in this category because the Interslavic edge says `exact territory pending`; it receives no integrability or reach credit.
- **No match:** no fuzzy family-name, typological, regional, or macro-language join is made. Explicit exclusions in the source matrices remain exclusions.

## Three separate quantities

1. **Integrability** records whether an exact component is already named in a reusable engineering architecture. It does not assert that another language's readers understand the output.
2. **Shared-core compute-reuse potential** records plausible reuse of aligned source structure, term graphs, register work, or script handling. No source supplies an empirical token-savings coefficient, so every positive reuse entry is explicitly unquantified.
3. **Current cross-language demographic reach credit** is numeric and equals **0 for all 100 rows**. No blanket family multiplier is applied. A current localized output may establish its own component baseline, but it creates no cross-language demographic credit without an exact named output and a defensible overlap rule.

## Indonesian overlap control

The Indonesian component has a complete named Open Logic output: 722 of 722 units. Its forward Open Logic deficit is therefore (D=0). The complete output can be a reusable source asset, but it is existing own-language coverage, not new work, and it provides no automatic Malaysian, Bruneian, Javanese, Sundanese, or other cross-language reach.

## Result counts

- Exact profile matches: 16
- Exact language/script plus named target-country matches: 4
- Hypothesis-only unresolved-territory relations: 1
- No exact current matrix relation: 79
- Total rows: 100

Mapped exact/country-compatible components by architecture:

- IL-GERM: 1
- IL-HU: 2
- IL-IDMS: 1
- IL-MANDING: 1
- IL-NGUNI: 4
- IL-PDT: 2
- IL-PUNJABI: 2
- IL-SOTHO: 3
- IL-TURKIC: 4

## Interpretation limit

The crosswalk is suitable for portfolio bookkeeping, avoiding duplicate translation, and identifying where shared engineering may save compute. It is not suitable for claiming family-wide comprehension, calculating a demographic reach bonus, or replacing exact language, script, territory, and product outputs.
