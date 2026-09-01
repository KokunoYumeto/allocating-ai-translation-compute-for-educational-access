#!/usr/bin/env python3
"""Read-only unit-of-analysis checks; never invoke the portfolio builder main."""

from __future__ import annotations

import copy
import json
import unittest
from collections import Counter

import build_authoritative_exposure_portfolio_v1_1 as portfolio
import build_high_reach_education_needs_v1_1 as needs_builder


def current_identity_snapshot() -> tuple[dict, dict, dict, list, dict, dict, dict]:
    candidates = {row["intervention_id"]: row for row in portfolio.read_csv(portfolio.CANDIDATES)}
    observations = {row["observation_id"]: row for row in portfolio.read_csv(portfolio.OBSERVATIONS)}
    expected = {row["universe_profile_id"]: row for row in portfolio.read_csv(portfolio.EXPECTED)}
    edges = portfolio.read_csv(portfolio.NEEDS_EDGES)
    needs = {row["needs_profile_id"]: row for row in portfolio.read_csv(portfolio.NEEDS)}
    expansions = {row["candidate_id"]: row for row in portfolio.read_csv(portfolio.EXPANSION)}
    dispositions = portfolio.observation_candidate_dispositions(candidates, observations, expected, edges, needs)
    return candidates, observations, expected, edges, needs, expansions, dispositions


def prepolicy_identity_counts(snapshot: tuple) -> dict:
    candidates, _, expected, _, _, expansions, dispositions = snapshot
    active_master = {
        cid for cid, row in candidates.items() if cid not in dispositions
        and row.get("target_type") not in {"accessibility", "natural_language_baseline"}
    }
    aliases = {
        xid for xid, row in expansions.items()
        if row.get("existing_intervention_id") in candidates
        and candidates[row["existing_intervention_id"]].get("variety_or_register") == row.get("target_profile")
    }
    active = active_master | (set(expansions) - aliases)
    for pid, profile in expected.items():
        owners = {
            cid for cid in set(profile["candidate_ids"].split(";")) & active
            if cid not in portfolio.PROFILE_GROUPS or pid in portfolio.PROFILE_GROUPS[cid]
        }
        if not owners:
            active.add(pid)
    active.update(portfolio.PACKAGE_OVERRIDES)
    active.update(portfolio.BRIDGE_PACKAGE)
    return {
        "master_rows": len(candidates),
        "observation_derived_master_rows": sum(cid.startswith("OBS-") for cid in candidates),
        "observation_only_dispositions": len(dispositions),
        "explicit_scoped_observation_actions": sum(cid.startswith("OBS-") for cid in active_master),
        "active_nonobservation_master_identities": len(active_master),
        "expansion_aliases": len(aliases),
        "prepolicy_action_identities": len(active),
        "disposition_counts": dict(sorted(Counter(row["disposition"] for row in dispositions.values()).items())),
    }


class UnitIdentityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.snapshot = current_identity_snapshot()

    def test_all_observation_only_rows_are_disposed_without_padding(self) -> None:
        candidates, observations, expected, edges, needs, _, dispositions = self.snapshot
        before = copy.deepcopy((candidates, observations, expected, edges, needs))
        again = portfolio.observation_candidate_dispositions(candidates, observations, expected, edges, needs)
        self.assertEqual(dispositions, again)
        self.assertEqual(before, (candidates, observations, expected, edges, needs))
        self.assertTrue(all(cid.startswith("OBS-") for cid in dispositions))
        self.assertGreaterEqual(prepolicy_identity_counts(self.snapshot)["prepolicy_action_identities"], 100)

    def test_source_observations_and_territories_are_preserved(self) -> None:
        observations = self.snapshot[1]
        for cid, disposition in self.snapshot[-1].items():
            observation_id = cid.removeprefix("OBS-")
            self.assertIn(observation_id, observations)
            self.assertEqual(disposition["observation_id"], observation_id)
            self.assertEqual(disposition["source_territory"], observations[observation_id]["territory"])
            self.assertEqual(disposition["source_learner_stratum"], observations[observation_id]["learner_stratum"])

    def test_mam_diaspora_is_context_not_a_guatemala_population_or_new_action(self) -> None:
        disposition = self.snapshot[-1]["OBS-GRG-US-031"]
        self.assertEqual(disposition["source_territory"], "United States")
        self.assertEqual(disposition["target_profile_context"], "mam-Latn-GT")
        self.assertIn("NAT-096", disposition["owner"].split(";"))
        self.assertEqual(disposition["disposition"], "observation_evidence_for_existing_profile_not_a_new_commission")

    def test_explicit_negative_and_comparison_control_treatments_survive(self) -> None:
        dispositions = self.snapshot[-1]
        for cid in ("OBS-GRG-PL-001", "OBS-GRG-PL-003", "OBS-GRG-PL-005", "OBS-GRG-PL-006"):
            self.assertEqual(dispositions[cid]["disposition"], "observation_only_supply_rich_control")
            self.assertIn("deprioritize_generic_translation", dispositions[cid]["profile_ranking_treatment"])
        self.assertEqual(dispositions["OBS-GRG-PL-010"]["disposition"], "observation_only_scarcity_overlap_control")
        self.assertIn("GLB-030", dispositions["OBS-GRG-PL-001"]["owner"].split(";"))

    def test_a_valid_kriol_surface_does_not_itself_define_a_course(self) -> None:
        self.assertEqual(
            self.snapshot[-1]["OBS-GRG-AU-001"]["disposition"],
            "observation_only_pending_independent_action_definition",
        )

    def test_kiswahili_first_action_excludes_follow_on_population_views(self) -> None:
        rows = [row for row in portfolio.read_csv(portfolio.JOINS)
                if row["universe_profile_id"] == "GLB-036"]
        before = copy.deepcopy(rows)
        scoped = portfolio.first_package_population_rows("SHC-SWAHILI", rows)
        self.assertEqual(rows, before)
        self.assertEqual({row["observation_id"] for row in scoped}, {"SUP-024"})
        self.assertEqual(scoped[0]["source_profile_tag"], "swh-Latn-UG")
        self.assertEqual(scoped[0]["learner_stratum"], "Uganda residents")
        self.assertEqual(scoped[0]["denominator_class"], "territory_all_residents_ceiling")
        self.assertEqual(scoped[0]["population_base"], "45905417")
        self.assertTrue({"SUP-022", "SUP-023", "SUP-025"} <= {row["observation_id"] for row in rows})
        self.assertEqual(portfolio.first_package_population_rows("NAT-063", rows), rows)

    def test_kiswahili_exact_output_keys_match_first_package_not_wider_architecture(self) -> None:
        edges = [edge for edge in self.snapshot[3] if edge["portfolio_entry_id"] == "SHC-SWAHILI"]
        before = copy.deepcopy(edges)
        scoped = portfolio.first_package_needs_edges("SHC-SWAHILI", edges)
        self.assertEqual(edges, before)
        self.assertTrue(scoped)
        allowed = {"swc-Latn-CD", "swh-Latn-UG"}
        self.assertEqual({tag for edge in scoped for tag in edge["named_output_profile_id"].split(";")}, allowed)
        package = portfolio.PACKAGE_OVERRIDES["SHC-SWAHILI"]
        self.assertEqual({tag.strip() for tag in package["target_profiles"].split(";")}, allowed)
        self.assertIn("DRC grades 1–3", package["education_stages"])
        self.assertIn("Uganda P4", package["education_stages"])
        self.assertNotIn("Tanzania", package["territory_or_scope"])
        self.assertNotIn("Kenya", package["territory_or_scope"])
        self.assertIn("Follow-on context only", package["follow_on_package"])
        self.assertIn("swh-Latn-TZ", package["follow_on_package"])
        self.assertIn("swh-Latn-KE", package["follow_on_package"])

    def test_kiswahili_scope_can_admit_exact_drc_but_not_broad_umbrella(self) -> None:
        rows = [{"observation_id": "DRC-fixture", "source_profile_tag": "swc-Latn-CD"},
                {"observation_id": "umbrella-fixture", "source_profile_tag": "swh/swc; locale outputs required"}]
        self.assertEqual(portfolio.first_package_population_rows("SHC-SWAHILI", rows), rows[:1])

    def test_indonesian_prerequisite_credits_available_work_not_whole_program_completion(self) -> None:
        route = needs_builder.PREREQUISITE_ROUTES["HRN-010"]
        self.assertIn("completed Indonesian Open Logic", route)
        self.assertIn("relevant available exact-course prerequisites", route)
        self.assertIn("completion of the whole 40-course program is not required", route)
        self.assertNotIn("Completed Indonesian mathematics/logic program", route)

    def fixture_diaspora_need(self) -> tuple[dict, dict, list, dict]:
        candidate = {"intervention_id": "OBS-TEST-US", "variety_or_register": "mh-Latn-MH"}
        observation = {"territory": "United States", "learner_stratum": "age5plus_home_language"}
        edge = {"portfolio_entry_id": "OBS-TEST-US", "edge_status": "resolved", "edge_role": "direct_profile_need",
                "needs_profile_id": "NEED-US", "named_output_profile_id": "mh-Latn-MH"}
        need = {"target_profiles": "mh-Latn-MH", "territory_or_scope": "United States",
                "first_priority_stage": "US adult practical numeracy", "first_package": "US settlement numeracy with Marshallese worked audio",
                "need_evidence": "Explicit fixture for the source-defined US adult cohort", "source_urls": "fixture:source",
                "delivery_spec": "Offline audio and aligned text"}
        return candidate, observation, [edge], {"NEED-US": need}

    def test_an_independently_scoped_diaspora_action_can_be_preserved(self) -> None:
        self.assertTrue(portfolio.observation_action_has_exact_scope(*self.fixture_diaspora_need()))

    def test_origin_country_scope_cannot_reuse_a_us_population(self) -> None:
        candidate, observation, edges, needs = self.fixture_diaspora_need()
        needs["NEED-US"]["territory_or_scope"] = "Marshall Islands"
        self.assertFalse(portfolio.observation_action_has_exact_scope(candidate, observation, edges, needs))

    def test_profile_only_and_compute_only_evidence_are_not_action_bindings(self) -> None:
        candidate, observation, edges, needs = self.fixture_diaspora_need()
        edges[0]["edge_role"] = "cross_locale_compute_reuse_only"
        self.assertFalse(portfolio.observation_action_has_exact_scope(candidate, observation, edges, needs))
        edges[0]["edge_role"] = "direct_profile_need"
        needs["NEED-US"]["first_package"] = ""
        self.assertFalse(portfolio.observation_action_has_exact_scope(candidate, observation, edges, needs))


if __name__ == "__main__":
    print(json.dumps(prepolicy_identity_counts(current_identity_snapshot()), indent=2))
    unittest.main(verbosity=2)
