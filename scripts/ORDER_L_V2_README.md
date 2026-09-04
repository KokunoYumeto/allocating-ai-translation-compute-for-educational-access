# Executable Order-L V2 identification/model pair

`needs_access_order_l_v2.py` is a separately versioned language-level lane. It
does not call, replace, or relax `needs_access_ranking.py`. The original strict
conditional-chain order is labelled `L-C`; the additive outputs are:

- `L-ID`: finite population/need bounds, best and worst identified ranks, rank sets, and definite/possible/outside Top-10 and Top-100 states.
- `L-M`: the reference common-prior model-conditional order with posterior mean, median, P05/P95 need, rank P05/P50/P95, Top-10/100 probabilities, boundary ties, and pairwise boundary probabilities.

## Input contract

The executable accepts one language-keyed table for each contract:

- `structured/schema/order_l_v2_cells.csv`: exact targets, one canonical universe version and semantic hash, mutually exclusive person profiles, finite population bounds, fixed-direct or latent-symmetric assignment, stable assignment atoms, within-atom target splits, and L-ID bounds. In production, `universe_semantic_hash` is exactly the `snapshot_payload_sha256` of `structured/SUCCESSOR_TARGET_ROSTER_v2.json`: `b392bba62805f6f80a5e31206de59f32d8a4c261a2590aa3ba90382729e51309`. It is not the JSON file-byte hash or a hash of the broader successor artifact.
- `structured/schema/order_l_v2_assignment_evidence.csv`: optional complete compatible multinomial counts over all atoms in one latent profile. An empty header-only file means prior-only latent shares.
- `structured/schema/order_l_v2_observations.csv`: direct full-endpoint or component-proxy counts and shared-source identities.
- `structured/schema/order_l_v2_measurement_models.csv`: mandatory calibration for component proxies.
- `structured/schema/order_l_v2_transport_models.csv`: mandatory directional transport for ecological, broader-cohort, cross-stage, or cross-endpoint observations.
- `scripts/ORDER_L_V2_PRIOR_REGISTRY.json`: frozen reference/diffuse/optimistic/pessimistic need priors and sparse/concentrated symmetric assignment-prior sensitivities.

For every person profile, `fixed_direct` assignment weights sum exactly to one.
For `latent_symmetric`, stable atom shares are drawn from one symmetric
Dirichlet distribution and sum exactly to one in every draw; the fixed target
weights within each atom also sum to one. Adding target rows therefore cannot
duplicate people, and splitting or merging a target representation conserves
the atom's total mass. Compatible language-share evidence updates this
Dirichlet; region, income, exact target label, prestige, evidence tier,
source-count, local-work, and project fields are never predictors.

Every profile requires a finite public population ceiling. A missing endpoint
remains a latent prior draw rather than zero or `0.5`. Direct endpoint counts
bypass component multiplication; component proxies and transported evidence
must pass their explicit registered models. The ranker rejects an incomplete or
duplicate target-by-draw grid.

## Synthetic replay

These are invented values, not a production ranking. From the
`from_scratch_20260901` directory:

```powershell
python scripts/needs_access_order_l_v2.py `
  --cells tests/fixtures/order_l_v2_cells_synthetic.csv `
  --assignment-evidence tests/fixtures/order_l_v2_assignment_evidence_synthetic.csv `
  --observations tests/fixtures/order_l_v2_observations_synthetic.csv `
  --measurement-models tests/fixtures/order_l_v2_measurement_models_synthetic.csv `
  --transport-models tests/fixtures/order_l_v2_transport_models_synthetic.csv `
  --prior-registry scripts/ORDER_L_V2_PRIOR_REGISTRY.json `
  --l-id-output tests/fixtures/order_l_v2_expected/order_l_id_v2.csv `
  --l-m-output tests/fixtures/order_l_v2_expected/order_l_m_v2.csv `
  --joint-draw-output tests/fixtures/order_l_v2_expected/order_l_v2_joint_draws.csv `
  --cell-draw-output tests/fixtures/order_l_v2_expected/order_l_v2_cell_draws.csv `
  --shared-effect-output tests/fixtures/order_l_v2_expected/order_l_v2_shared_effect_draws.csv `
  --sensitivity-output tests/fixtures/order_l_v2_expected/order_l_v2_sensitivity.csv `
  --pairwise-output tests/fixtures/order_l_v2_expected/order_l_v2_boundary_pairwise.csv `
  --voi-output tests/fixtures/order_l_v2_expected/order_l_v2_value_of_information.csv `
  --validation-output tests/fixtures/order_l_v2_expected/order_l_v2_validation_receipt.json `
  --draw-count 64 `
  --public-seed synthetic-order-l-v2-public-seed `
  --allow-synthetic
```

Run the additive verification suite:

```powershell
python -m unittest -v tests.test_needs_access_order_l_v2
```

The validation receipt binds every input and output by SHA-256 and marks
`global_top100_release_authorized=false`. Production remains blocked until the
successor universe supplies its canonical exact-target table and semantic hash,
and every admitted target has complete finite-population, assignment, and
endpoint-model inputs under the same common-benefit contract.
