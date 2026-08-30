# Top-100 interlanguage crosswalk validation receipt

Date: 2026-08-30

## Source inventory

| Task-root-relative file | Bytes | SHA-256 |
|---|---:|---|
| `TOP_100.csv` | 117712 | `BB5894B135A77FA7EC6FBD854477025D0BF3ABA1FE476EA0F5430D6A9DF3CDE3` |
| `top100_needs_assignment_v2.csv` | 175234 | `A34A4C10F9CF84522A7CEB49A50EC59D727AD9C1086E025D0C09C4ECAF33CBB0` |
| `appendix_f_interlanguage_matrix_summary.csv` | 19555 | `BA41972EC17E027A6C3DB1E589B8070525845A1DD9D9492061A0A42FAF6A5F1C` |
| `staging/interlanguage_bundle_model/interlanguage_intervention_matrix.csv` | 84793 | `DD6BD32BCEC92FD2DE3111DBC584EBC7455E4C707241AF647B62F500318D8B33` |
| `staging/interlanguage_matrix/interlanguage_overlap_normalized.csv` | 48710 | `43C64A3D803ED91BAA4D975672E6B7E1995B5E08B185CCECA71263483CD271A7` |

## Deterministic validation

| Check | Result | Evidence |
|---|---|---|
| Top-100 source rows | PASS | 100 |
| Needs rows | PASS | 100 |
| Output rows | PASS | 100 |
| Unique portfolio positions | PASS | 100 |
| Unique intervention IDs | PASS | 100 |
| Exact positions 1-100 | PASS | pass |
| Exact expected mappings | PASS | 16/16 |
| All demographic reach credits zero | PASS | 100/100 |
| Indonesian completion overlap | PASS | 722 of 722 Open Logic units complete |
| Indonesian forward deficit | PASS | D=0 |
| RFC 4180 round-trip row count | PASS | 101 including header |
| RFC 4180 round-trip field widths | PASS | 35 fields in every row |
| RFC 4180 round-trip value identity | PASS | pass |

## Relation counts

| Relation status | Rows |
|---|---:|
| exact_profile_match | 16 |
| exact_language_script_and_target_country_cell | 4 |
| hypothesis_only_language_script_match_territory_unresolved | 1 |
| no_exact_relation_in_current_matrix | 79 |
| **Total** | **100** |

## Output identities

| Task-root-relative file | Bytes | SHA-256 |
|---|---:|---|
| `top100_interlanguage_overlap_crosswalk.csv` | 114561 | `ED88A556E1055655E3635AAA64C793A684E1C655713BA4F86AD50B851CC1A380` |
| `TOP100_INTERLANGUAGE_CROSSWALK_METHOD_20260830.md` | 3982 | `BF59C23B002F8ED7ECE9FDEC16CE624BED28D27ACA44044A5642404C48354AE8` |

The required bundled spreadsheet package was absent from the loader-provided runtime, so the requested CSV was generated with a deterministic RFC 4180 parser/serializer and fully reparsed for value identity. All linked interlanguage rows carry exact source IDs. Every current cross-language demographic reach credit is zero; no family-level multiplier was introduced.
