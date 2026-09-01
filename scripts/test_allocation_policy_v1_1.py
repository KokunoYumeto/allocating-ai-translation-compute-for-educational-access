"""Deterministic tests; run with PYTHONDONTWRITEBYTECODE=1 python this_file.py."""

import copy
import itertools
import json
import random
import unittest

from allocation_policy_v1_1 import ENDANGERED, HIGH, REGIONAL, rank_portfolio, work_component_key


def observation(value, denominator="mother_tongue_or_first_language", source="SRC-1", **changes):
    row = {
        "observation_id": "OBS-" + source, "source_id": source,
        "population_base": str(value), "denominator_class": denominator,
        "count_unit": "persons", "learner_stratum": "all_residents",
        "reference_date_or_year": "2020",
    }
    row.update(changes)
    return row


def candidate(entry_id, population=None, lane=None, tier="stage", **changes):
    row = {
        "entry_id": entry_id, "entry_type": "natural_language_locale_output",
        "target_profiles": "xx-Latn-AA", "first_bounded_package": "One specified teacher-independent package",
        "delivery_formats": "HTML;PDF;offline", "teacher_independent_requirements": "Complete worked feedback",
        "accessibility_requirements": "Semantic mathematics", "non_overlap_rule": "Only the exact specified residual",
        "needs_profile_ids": "NEED-" + entry_id,
        "package_evidence_status": "literature_backed_high_reach_need" if tier == "stage" else "registered_curriculum_package_provisional_local_need_fit",
    }
    if population is not None:
        row["_population_observations"] = [observation(population, source="SRC-" + entry_id)]
    if lane:
        row["_lane_mapping"] = {"lane": lane, "basis": "exact-profile test source; not inherited rank"}
    row.update(changes)
    return row


def interval(low, high=None, **extra):
    return {"low": low, "high": low if high is None else high, "basis": "Sourced test ordinal interval", "evidence_ids": ["TEST-SOURCE"], **extra}


def edge(need="HRN-A", output="xx-Latn-AA", **changes):
    result = {"needs_profile_id": need, "named_output_profile_id": output, "edge_status": "resolved", "edge_role": "direct_profile_need"}
    result.update(changes)
    return result


def component(locale="xx-Latn-AA", package="quantitative-core", stage="grades2-5", modality="text_audio_offline", owner=None):
    result = {"locale": locale, "package_id": package, "stage_id": stage, "modality": modality}
    if owner is not None:
        result["owner_entry_id"] = owner
    return result


class AllocationPolicyTests(unittest.TestCase):
    def test_permutations_and_input_immutability(self):
        rows = [candidate("A", 12_000_000), candidate("B", 70_000_000), candidate("C", lane=REGIONAL), candidate("D", lane=ENDANGERED)]
        before = copy.deepcopy(rows)
        expected = rank_portfolio(rows)
        for permutation in itertools.permutations(rows):
            self.assertEqual(rank_portfolio(permutation), expected)
        self.assertEqual(rows, before)
        self.assertEqual(expected[0][0]["entry_id"], "B")
        self.assertTrue(all(not any(k.startswith("_") for k in row) for row in expected[0]))

    def test_many_random_permutations(self):
        rows = [candidate(f"C{i:03}", (i + 1) * 2_000_000, lane=(HIGH, REGIONAL, ENDANGERED)[i % 3]) for i in range(45)]
        expected = rank_portfolio(rows)
        rng = random.Random(817)
        for _ in range(30):
            rng.shuffle(rows)
            self.assertEqual(rank_portfolio(rows), expected)

    def test_old_positions_lanes_ranks_are_not_consumed(self):
        rows = [candidate("Z", 90_000_000), candidate("A", 12_000_000)]
        baseline, diag = rank_portfolio(rows)
        for i, row in enumerate(rows):
            row.update(exposure_position=str(2-i), allocation_lane=ENDANGERED, wave="old", ordering_basis="ORDER", neutral_efficiency_rank=i+1)
        result, changed = rank_portfolio(rows)
        self.assertEqual([r["entry_id"] for r in baseline], [r["entry_id"] for r in result])
        self.assertEqual(diag, changed)
        self.assertTrue(all(r["allocation_lane"] == HIGH and "wave" not in r for r in result))

    def test_stage_evidence_precedes_gross_scope_policy(self):
        rows = [candidate("BIG", 500_000_000, tier="provisional"), candidate("EXACT", 11_000_000)]
        ranked, diag = rank_portfolio(rows)
        self.assertEqual([r["entry_id"] for r in ranked], ["EXACT", "BIG"])
        self.assertEqual(diag["entries"]["BIG"]["dimensions"]["R"]["status"], "unknown")

    def test_source_informed_provisional_need_has_provisional_not_unresolved_tier(self):
        rows = [
            candidate("PROVISIONAL", 100_000_000, package_evidence_status="source_informed_provisional_custom_stage_need", needs_profile_ids=""),
            candidate("DIRECT", 12_000_000),
            candidate("UNRESOLVED", 500_000_000, package_evidence_status="unrecognized_package_status", needs_profile_ids=""),
        ]
        ranked, diag = rank_portfolio(rows)
        self.assertEqual([row["entry_id"] for row in ranked], ["DIRECT", "PROVISIONAL", "UNRESOLVED"])
        provisional = diag["entries"]["PROVISIONAL"]["operational_evidence"]
        self.assertEqual(provisional["tier"], "registered_provisional")
        self.assertEqual(provisional["need_evidence_priority"], 2)
        self.assertLess(provisional["need_evidence_priority"], diag["entries"]["DIRECT"]["operational_evidence"]["need_evidence_priority"])
        self.assertIn("not a measured cohort", provisional["basis"])
        self.assertEqual(diag["entries"]["PROVISIONAL"]["dimensions"]["R"]["status"], "unknown")

    def test_incompatible_denominators_never_count_compared(self):
        territory = candidate("TERR", _population_observations=[observation(5_000_000, "territory_all_residents_ceiling")], lane=HIGH)
        l1 = candidate("L1", 12_000_000)
        first, diag = rank_portfolio([territory, l1])
        territory["_population_observations"][0]["population_base"] = "9000000000"
        second, diag2 = rank_portfolio([territory, l1])
        self.assertEqual([r["entry_id"] for r in first], ["L1", "TERR"])
        self.assertEqual([r["entry_id"] for r in first], [r["entry_id"] for r in second])
        self.assertEqual(diag["dominance_edges"], [])
        self.assertEqual(diag2["dominance_edges"], [])
        self.assertNotEqual(diag["entries"]["L1"]["primary_typed_view"], diag["entries"]["TERR"]["primary_typed_view"])

    def test_incompatible_learner_strata_have_separate_views(self):
        rows = [candidate("A", _population_observations=[observation(20_000_000, learner_stratum="age5plus")]), candidate("B", 80_000_000)]
        _, diag = rank_portfolio(rows)
        self.assertNotEqual(diag["entries"]["A"]["primary_typed_view"], diag["entries"]["B"]["primary_typed_view"])

    def test_unknown_not_zero_and_never_excluded(self):
        rows = [candidate("UNKNOWN", lane=HIGH), candidate("KNOWN_GROSS", 40_000_000)]
        ranked, diag = rank_portfolio(rows)
        self.assertEqual({r["entry_id"] for r in ranked}, {"UNKNOWN", "KNOWN_GROSS"})
        unknown = diag["entries"]["UNKNOWN"]
        self.assertIsNone(unknown["gross_scope_band_index"])
        self.assertEqual(unknown["dimensions"]["R"]["band"], "RU")
        self.assertIn("neither endpoint", unknown["dimensions"]["R"]["interval_interpretation"])
        self.assertEqual(diag["dominance_edges"], [])

    def test_reported_point_does_not_gain_zero_bound(self):
        _, diag = rank_portfolio([candidate("POINT", 20_000_000)])
        pop = diag["entries"]["POINT"]["population_observations"][0]
        self.assertIsNone(pop["source_low"])
        self.assertIsNone(pop["source_high"])
        self.assertEqual(pop["source_base"], "20000000")

    def test_source_lower_bound_keeps_upper_unknown(self):
        row = candidate("LOWER", _population_observations=[observation("", population_low="89000000")])
        _, diag = rank_portfolio([row])
        pop = diag["entries"]["LOWER"]["population_observations"][0]
        self.assertEqual(pop["scheduling_value_field"], "population_low")
        self.assertIsNone(pop["source_high"])

    def test_households_and_unsourced_counts_not_used_as_person_scope(self):
        rows = [candidate("HOUSEHOLDS", _population_observations=[observation(100_000_000, count_unit="households")]), candidate("UNSOURCED", _population_observations=[observation(100_000_000, source="")])]
        _, diag = rank_portfolio(rows)
        for row in rows:
            self.assertIsNone(diag["entries"][row["entry_id"]]["gross_scope_band_index"])

    def test_population_observations_not_summed(self):
        row = candidate("MULTI", _population_observations=[observation(8_000_000, source="ONE"), observation(8_000_000, source="TWO")])
        _, diag = rank_portfolio([row])
        self.assertEqual(diag["entries"]["MULTI"]["gross_scope_band_index"], 1)
        self.assertEqual(diag["entries"]["MULTI"]["representative_gross_observation"]["scheduling_value"], "8000000")

    def test_robust_dominance_with_sourced_intervals(self):
        rows = [candidate("LOW", 90_000_000), candidate("HIGH", 12_000_000)]
        evidence = {}
        for entry_id, value in (("HIGH", 4), ("LOW", 2)):
            evidence[entry_id] = {"delivery_mode": "semantic_text_offline", "dimensions": {d: interval(value, measure_kind="newly_comfortable_reader_opportunity") for d in ("R", "S", "A", "N")}}
        ranked, diag = rank_portfolio(rows, {"evidence": evidence})
        self.assertEqual([r["entry_id"] for r in ranked], ["HIGH", "LOW"])
        self.assertEqual(diag["entries"]["HIGH"]["evidence_front"], 1)
        self.assertEqual(diag["entries"]["LOW"]["evidence_front"], 2)

    def test_dynamic_eligibility_does_not_force_unknown_static_front_before_successor(self):
        rows = [
            candidate("A", 90_000_000),
            candidate("B", 20_000_000),
            candidate("C_UNKNOWN", 100_000_000, tier="provisional"),
        ]
        evidence = {name: {"delivery_mode": "text", "dimensions": {d: interval(
            value, assumption_status="prior_qualitative_judgment", measure_kind="newly_comfortable_reader_opportunity",
        ) for d in ("R", "S", "A", "N")}} for name, value in (("A", 4), ("B", 2))}
        expected = rank_portfolio(rows, {"evidence": evidence})
        ranked, diag = expected
        self.assertEqual([row["entry_id"] for row in ranked], ["A", "B", "C_UNKNOWN"])
        self.assertEqual(diag["entries"]["B"]["evidence_front"], 2)
        self.assertEqual(diag["entries"]["C_UNKNOWN"]["evidence_front"], 1)
        self.assertEqual(diag["entries"]["C_UNKNOWN"]["dimensions"]["R"]["status"], "unknown")
        self.assertEqual(diag["dispatch_trace"][0]["eligible_entry_ids_in_lane_before_policy"], ["A", "C_UNKNOWN"])
        successor_turn = diag["dispatch_trace"][1]
        self.assertEqual(successor_turn["eligible_entry_ids_in_lane_before_policy"], ["B", "C_UNKNOWN"])
        self.assertEqual(successor_turn["remaining_dominance_predecessors"], [])
        self.assertEqual(successor_turn["cleared_dominance_predecessors"]["A"]["status"], "dispatched")
        self.assertTrue(diag["static_front_is_not_dispatch_priority"])
        for permutation in itertools.permutations(rows):
            self.assertEqual(rank_portfolio(permutation, {"evidence": evidence}), expected)

    def test_all_remaining_predecessors_must_clear_before_dynamic_eligibility(self):
        rows = [candidate("A", 90_000_000), candidate("B", 20_000_000), candidate("D", 100_000_000)]
        evidence = {name: {"delivery_mode": "text", "dimensions": {d: interval(
            value, measure_kind="newly_comfortable_reader_opportunity",
        ) for d in ("R", "S", "A", "N")}} for name, value in (("A", 4), ("B", 3), ("D", 2))}
        ranked, diag = rank_portfolio(rows, {"evidence": evidence})
        self.assertEqual([row["entry_id"] for row in ranked], ["A", "B", "D"])
        self.assertEqual(diag["dispatch_trace"][1]["eligible_entry_ids_in_lane_before_policy"], ["B"])
        self.assertEqual(set(diag["dispatch_trace"][2]["cleared_dominance_predecessors"]), {"A", "B"})
        positions = {row["entry_id"]: i for i, row in enumerate(ranked)}
        self.assertTrue(all(positions[edge["before"]] < positions[edge["after"]] for edge in diag["dominance_edges"]))

    def test_fully_covered_predecessor_clears_dynamic_eligibility(self):
        package_edge = edge()
        rows = [candidate("A_COMPLETED", 90_000_000, _needs_edges=[package_edge]), candidate("B", 20_000_000), candidate("C_UNKNOWN", 100_000_000, tier="provisional")]
        evidence = {name: {"delivery_mode": "text", "dimensions": {d: interval(
            value, measure_kind="newly_comfortable_reader_opportunity",
        ) for d in ("R", "S", "A", "N")}} for name, value in (("A_COMPLETED", 4), ("B", 2))}
        key = json.dumps(("HRN-A", "xx-Latn-AA", "", "", ""), separators=(",", ":"))
        ranked, diag = rank_portfolio(rows, {"evidence": evidence, "completed_package_keys": [key]})
        self.assertEqual([row["entry_id"] for row in ranked], ["B", "C_UNKNOWN"])
        self.assertEqual(diag["dispatch_trace"][0]["eligible_entry_ids_in_lane_before_policy"], ["B", "C_UNKNOWN"])
        self.assertEqual(diag["dispatch_trace"][0]["cleared_dominance_predecessors"]["A_COMPLETED"]["reason"], "all_exact_actionable_package_keys_already_owned")

    def test_unknown_R_prevents_false_dominance(self):
        rows = [candidate("A", 90_000_000), candidate("B", 12_000_000)]
        evidence = {name: {"delivery_mode": "text", "dimensions": {d: interval(value) for d in ("S", "A", "N")}} for name, value in (("A", 4), ("B", 2))}
        _, diag = rank_portfolio(rows, {"evidence": evidence})
        self.assertEqual(diag["dominance_edges"], [])

    def test_planning_accepts_sourced_prior_as_inference_measured_only_retains_unknown(self):
        rows = [candidate("A", 12_000_000), candidate("B", 90_000_000)]
        evidence = {name: {"delivery_mode": "text", "dimensions": {d: interval(
            value, assumption_status="prior_qualitative_judgment",
            measure_kind="newly_comfortable_reader_opportunity",
            source_register_path="research/GLOBAL_GAP_REGISTER.csv", source_register_sha256="a" * 64,
            planning_scope="Common FR-2 planning judgment; not observed current ECE or other residual-package reach",
        ) for d in ("R", "S", "A", "N")}} for name, value in (("A", 4), ("B", 2))}
        original = copy.deepcopy(evidence)
        planning_rows, planning = rank_portfolio(rows, {"evidence": evidence})
        measured_rows, measured = rank_portfolio(rows, {"evidence": evidence, "opportunity_view": "measured_only"})
        self.assertEqual([row["entry_id"] for row in planning_rows], ["A", "B"])
        self.assertEqual([row["entry_id"] for row in measured_rows], ["B", "A"])
        self.assertEqual(planning["opportunity_view"], "planning")
        self.assertEqual(measured["opportunity_view"], "measured_only")
        self.assertEqual(measured["dominance_edges"], [])
        self.assertEqual(len(planning["dominance_edges"]), 1)
        self.assertEqual(planning["entries"]["B"]["evidence_front"], 2)
        prior = planning["entries"]["A"]["dimensions"]["R"]
        conservative = measured["entries"]["A"]["dimensions"]["R"]
        self.assertEqual(prior["status"], "provisional_planning_inference")
        self.assertEqual(conservative["status"], "unknown")
        self.assertEqual(conservative["band"], "RU")
        self.assertEqual(prior["prior_interval"], conservative["prior_interval"])
        self.assertEqual(prior["prior_interval"]["low"], 4)
        self.assertEqual(prior["prior_interval"]["assumption_status"], "prior_qualitative_judgment")
        self.assertEqual(prior["provenance"]["source_register_sha256"], "a" * 64)
        self.assertIn("Common FR-2", prior["provenance"]["planning_scope"])
        self.assertIn("not measured readership", prior["interval_interpretation"])
        self.assertEqual(planning["opportunity_status_counts"]["measurement_supported_ordinal_interval"], 0)
        self.assertEqual(measured["opportunity_status_counts"]["provisional_planning_inference"], 0)
        self.assertEqual(planning["policy_sha256"], measured["policy_sha256"])
        self.assertNotEqual(planning["run_configuration_sha256"], measured["run_configuration_sha256"])
        self.assertEqual(evidence, original)

    def test_explicit_measurement_supported_intervals_active_in_both_views(self):
        rows = [candidate("A", 12_000_000), candidate("B", 90_000_000)]
        evidence = {name: {"delivery_mode": "text", "dimensions": {d: interval(
            value, assumption_status="measured_evidence", measure_kind="newly_comfortable_reader_opportunity",
        ) for d in ("R", "S", "A", "N")}} for name, value in (("A", 4), ("B", 2))}
        for view in ("planning", "measured_only"):
            ranked, diag = rank_portfolio(rows, {"evidence": evidence, "opportunity_view": view})
            self.assertEqual([row["entry_id"] for row in ranked], ["A", "B"])
            self.assertEqual(diag["entries"]["A"]["dimensions"]["R"]["status"], "measurement_supported_ordinal_interval")
            self.assertEqual(diag["opportunity_status_counts"]["measurement_supported_ordinal_interval"], 8)
            self.assertEqual(diag["opportunity_status_counts"]["provisional_planning_inference"], 0)

    def test_no_unsourced_prior_or_missing_interval_is_admitted_in_either_view(self):
        for view in ("planning", "measured_only"):
            for invalid in (
                interval(4, assumption_status="prior_qualitative_judgment", evidence_ids=[]),
                interval(4, assumption_status="prior_qualitative_judgment", basis=""),
                {"basis": "prior register", "evidence_ids": ["SOURCE"], "assumption_status": "prior_qualitative_judgment"},
            ):
                _, diag = rank_portfolio([candidate("A")], {"evidence": {"A": {"dimensions": {"S": invalid}}}, "opportunity_view": view})
                self.assertEqual(diag["entries"]["A"]["dimensions"]["S"]["status"], "unknown")

    def test_policy_and_unverified_scenarios_are_not_planning_evidence(self):
        for status in ("policy_assumption", "normative_assumption", "sensitivity", "unverified_prior"):
            _, diag = rank_portfolio([candidate("A")], {"evidence": {"A": {"dimensions": {"S": interval(4, assumption_status=status)}}}})
            dimension = diag["entries"]["A"]["dimensions"]["S"]
            self.assertEqual(dimension["status"], "unknown")
            self.assertEqual(dimension["prior_interval"]["assumption_status"], status)

    def test_prior_dimensions_are_permutation_invariant_in_both_views(self):
        rows = [candidate("A", 12_000_000), candidate("B", 90_000_000), candidate("C", lane=REGIONAL)]
        evidence = {name: {"delivery_mode": "text", "dimensions": {d: interval(
            value, assumption_status="prior_research_judgment", measure_kind="newly_comfortable_reader_opportunity",
        ) for d in ("R", "S", "A", "N")}} for name, value in (("A", 4), ("B", 2))}
        for view in ("planning", "measured_only"):
            context = {"evidence": evidence, "opportunity_view": view}
            expected = rank_portfolio(rows, context)
            for permutation in itertools.permutations(rows):
                self.assertEqual(rank_portfolio(permutation, context), expected)

    def test_scenario_labels_do_not_generate_or_modify_evidence(self):
        rows = [candidate("A", 12_000_000), candidate("B", 90_000_000)]
        evidence = {"A": {"dimensions": {"S": interval(2, 4, assumption_status="literature_backed_planning_range")}}}
        results = [rank_portfolio(rows, {"evidence": evidence, "scenario_label": label}) for label in ("cautious", "base", "favorable")]
        self.assertEqual(len({tuple(row["entry_id"] for row in ranked) for ranked, _ in results}), 1)
        self.assertEqual(len({diag["run_configuration_sha256"] for _, diag in results}), 3)
        for _, diag in results:
            supplied = diag["entries"]["A"]["dimensions"]["S"]
            self.assertEqual((supplied["low"], supplied["high"]), (2, 4))
            self.assertEqual(diag["entries"]["A"]["dimensions"]["R"]["status"], "unknown")
            self.assertIn("never selects endpoints", diag["scenario_generation_rule"])

    def test_gross_R_input_is_rejected_as_reader_opportunity(self):
        for view in ("planning", "measured_only"):
            for status in ("prior_qualitative_judgment", "measured_evidence"):
                _, diag = rank_portfolio([candidate("A", 90_000_000)], {"opportunity_view": view, "evidence": {"A": {"dimensions": {"R": interval(5, measure_kind="gross_population", assumption_status=status)}}}})
                self.assertEqual(diag["entries"]["A"]["dimensions"]["R"]["band"], "RU")

    def test_accessibility_modes_not_ordinally_compared(self):
        rows = [candidate("TEXT", lane=REGIONAL), candidate("SIGNED", lane=REGIONAL)]
        evidence = {name: {"delivery_mode": mode, "dimensions": {d: interval(value) for d in ("S", "A", "N")}} for name, mode, value in (("TEXT", "text", 4), ("SIGNED", "signed_video", 1))}
        _, diag = rank_portfolio(rows, {"evidence": evidence})
        self.assertEqual(diag["dominance_edges"], [])

    def test_exact_package_ownership_suppresses_duplicate_not_distinct_residual(self):
        rows = [candidate("OWNER", 90_000_000, _needs_edges=[edge()]), candidate("DUPLICATE", 11_000_000, _needs_edges=[edge()]), candidate("NEW_STAGE", 10_000_000, _needs_edges=[edge(stage_id="research")])]
        ranked, diag = rank_portfolio(rows)
        self.assertEqual({r["entry_id"] for r in ranked}, {"OWNER", "NEW_STAGE"})
        self.assertEqual(diag["suppressed_entries"][0]["entry_id"], "DUPLICATE")
        self.assertEqual(set(diag["suppressed_entries"][0]["package_owners"].values()), {"OWNER"})

    def test_partial_bundle_and_compute_only_edges(self):
        rows = [candidate("FIRST", 90_000_000, _needs_edges=[edge()]), candidate("BUNDLE", 20_000_000, _needs_edges=[edge(), edge(output="yy-Latn-BB")]), candidate("REUSE", 11_000_000, _needs_edges=[edge(edge_role="cross_locale_compute_reuse_only")])]
        ranked, diag = rank_portfolio(rows)
        bundle = next(row for row in ranked if row["entry_id"] == "BUNDLE")
        self.assertEqual(bundle["package_ownership_status"], "partially_covered_schedule_only_unowned_actions")
        self.assertEqual(len(json.loads(bundle["owned_package_keys"])), 1)
        self.assertEqual(diag["entries"]["REUSE"]["package_keys"], [])

    def test_unkeyed_urdu_output_not_erased_by_owned_hindi_package(self):
        rows = [
            candidate("HINDI", 90_000_000, target_profiles="hi-Deva-IN", _needs_edges=[edge(output="hi-Deva-IN")]),
            candidate("HINDI_URDU", 20_000_000, target_profiles="hi-Deva-IN;ur-Aran-IN;ur-Aran-PK", _needs_edges=[edge(output="hi-Deva-IN")]),
        ]
        ranked, diag = rank_portfolio(rows)
        self.assertEqual({row["entry_id"] for row in ranked}, {"HINDI", "HINDI_URDU"})
        self.assertFalse(diag["entries"]["HINDI_URDU"]["package_key_coverage"]["complete"])
        self.assertEqual(diag["entries"]["HINDI_URDU"]["package_key_coverage"]["unkeyed_output_profile_ids"], ["ur-Aran-IN", "ur-Aran-PK"])
        bundle = next(row for row in ranked if row["entry_id"] == "HINDI_URDU")
        self.assertEqual(bundle["package_ownership_status"], "registered_actions_covered_unkeyed_actions_retained")

    def test_prose_profile_cannot_assert_exhaustive_package_keys(self):
        rows = [candidate("FIRST", 90_000_000, _needs_edges=[edge()]), candidate("PROSE", 20_000_000, target_profiles="xx-Latn-AA plus separately named local outputs", _needs_edges=[edge()])]
        ranked, diag = rank_portfolio(rows)
        self.assertEqual(len(ranked), 2)
        self.assertIsNone(diag["entries"]["PROSE"]["package_key_coverage"]["complete"])

    def test_canonical_work_alias_suppressed_before_ranking_permutation_invariant(self):
        work = component(owner="OWNER")
        rows = [candidate("OWNER", 12_000_000, _work_components=[work]), candidate("ALIAS", 900_000_000, _work_components=[work]), candidate("OTHER", 30_000_000)]
        expected = rank_portfolio(rows)
        ranked, diag = expected
        self.assertEqual({row["entry_id"] for row in ranked}, {"OWNER", "OTHER"})
        self.assertEqual(diag["suppressed_entries"][0]["reason"], "all_exact_work_components_canonically_owned_elsewhere")
        self.assertEqual(diag["canonical_component_owners"][work_component_key(work)], "OWNER")
        self.assertIsNone(diag["entries"]["ALIAS"]["evidence_front"])
        self.assertFalse(any(edge["before"] == "ALIAS" or edge["after"] == "ALIAS" for edge in diag["dominance_edges"]))
        for permutation in itertools.permutations(rows):
            self.assertEqual(rank_portfolio(permutation), expected)

    def test_distinct_stage_and_modality_bypass_coarse_HRN_deduplication(self):
        rows = [
            candidate("RECOVERY", _work_components=[component(stage="grades2-5")], _needs_edges=[edge()]),
            candidate("ECE", _work_components=[component(stage="caregiver-ECE")], _needs_edges=[edge()]),
            candidate("TVET", _work_components=[component(stage="secondary-TVET")], _needs_edges=[edge()]),
            candidate("SIGNED", _work_components=[component(stage="grades2-5", modality="signed_video")], _needs_edges=[edge()]),
        ]
        ranked, diag = rank_portfolio(rows)
        self.assertEqual(len(ranked), 4)
        self.assertEqual(len(diag["canonical_component_owners"]), 4)
        self.assertEqual(diag["suppressed_entries"], [])
        self.assertTrue(all("coarse HRN ownership bypassed" in diag["entries"][row["entry_id"]]["package_key_rule"] for row in rows))

    def test_duplicate_work_requires_explicit_owner(self):
        rows = [candidate("A", _work_components=[component()]), candidate("B", _work_components=[component()])]
        with self.assertRaisesRegex(ValueError, "explicit canonical owner"):
            rank_portfolio(rows)
        ranked, _ = rank_portfolio(rows, {"component_owners": {work_component_key(component()): "B"}})
        self.assertEqual([row["entry_id"] for row in ranked], ["B"])

    def test_component_fields_required_no_HRN_stage_inference(self):
        for field in ("locale", "package_id", "stage_id", "modality"):
            invalid = component()
            invalid[field] = ""
            with self.assertRaisesRegex(ValueError, "nonempty string field"):
                rank_portfolio([candidate("A", _work_components=[invalid], _needs_edges=[edge()])])

    def test_unknown_component_owner_and_nonclaiming_owner_fail(self):
        with self.assertRaisesRegex(ValueError, "Unknown canonical component owner"):
            rank_portfolio([candidate("A", _work_components=[component(owner="MISSING")])])
        with self.assertRaisesRegex(ValueError, "does not actively claim the exact component"):
            rank_portfolio([candidate("A", _work_components=[component(owner="B")]), candidate("B", _work_components=[component(stage="different")])])
        with self.assertRaisesRegex(ValueError, "Conflicting canonical component owners"):
            rank_portfolio([candidate("A", _work_components=[component(owner="A")]), candidate("B", _work_components=[component(owner="B")])])

    def test_mixed_component_alias_requires_pre_rank_residualization(self):
        already_owned = component(owner="OWNER")
        new_work = component(locale="yy-Latn-BB", owner="MIXED")
        rows = [candidate("OWNER", _work_components=[already_owned]), candidate("MIXED", _work_components=[already_owned, new_work])]
        with self.assertRaisesRegex(ValueError, "residualize visible scope and opportunity before ranking"):
            rank_portfolio(rows)
        rows[1]["_work_components"] = [new_work]
        rows[1]["_reuse_components"] = [already_owned]
        ranked, diag = rank_portfolio(rows)
        self.assertEqual(len(ranked), 2)
        mixed = diag["entries"]["MIXED"]
        self.assertEqual(mixed["package_keys"], [work_component_key(new_work)])
        self.assertEqual(mixed["work_component_contract"]["reuse_component_keys"], [work_component_key(already_owned)])

    def test_reuse_must_name_known_exact_active_owner_and_cannot_be_active(self):
        owned = component(owner="OWNER")
        new = component(locale="yy-Latn-BB")
        with self.assertRaisesRegex(ValueError, "cannot also be active"):
            rank_portfolio([candidate("OWNER", _work_components=[owned], _reuse_components=[owned])])
        with self.assertRaisesRegex(ValueError, "must explicitly name its canonical owner"):
            rank_portfolio([candidate("OWNER", _work_components=[component()]), candidate("RESIDUAL", _work_components=[new], _reuse_components=[component()])])
        with self.assertRaisesRegex(ValueError, "does not actively claim the exact component"):
            rank_portfolio([candidate("OWNER", _work_components=[owned]), candidate("RESIDUAL", _work_components=[new], _reuse_components=[component(stage="not-owned", owner="OWNER")])])

    def test_reuse_cannot_inherit_population_or_whole_bundle_R(self):
        owned = component(owner="OWNER")
        active = component(locale="yy-Latn-BB", owner="RESIDUAL")
        rows = [candidate("OWNER", 500_000_000, _work_components=[owned]), candidate("RESIDUAL", 3_000_000, _work_components=[active], _reuse_components=[owned])]
        _, diag = rank_portfolio(rows)
        residual = diag["entries"]["RESIDUAL"]
        self.assertEqual(residual["dimensions"]["R"]["status"], "unknown")
        self.assertEqual(residual["representative_gross_observation"]["scheduling_value"], "3000000")
        evidence = {"RESIDUAL": {"dimensions": {"R": interval(2, measure_kind="newly_comfortable_reader_opportunity", assumption_status="prior_qualitative_judgment")}}}
        with self.assertRaisesRegex(ValueError, "Active opportunity scope not declared"):
            rank_portfolio(rows, {"evidence": evidence})
        evidence["RESIDUAL"]["opportunity_component_keys"] = [work_component_key(active)]
        _, scoped = rank_portfolio(rows, {"evidence": evidence})
        self.assertEqual(scoped["entries"]["RESIDUAL"]["dimensions"]["R"]["band"], "R2")
        evidence["RESIDUAL"]["opportunity_component_keys"].append(work_component_key(owned))
        with self.assertRaisesRegex(ValueError, "Active opportunity scope not declared"):
            rank_portfolio(rows, {"evidence": evidence})

    def test_component_contract_supported_in_evidence_context(self):
        work = component(owner="A")
        _, diag = rank_portfolio([candidate("A")], {"evidence": {"A": {"work_components": [work]}}})
        self.assertEqual(diag["entries"]["A"]["package_keys"], [work_component_key(work)])

    def test_policy_change_changes_queue_not_evidence(self):
        rows = [candidate("H", lane=HIGH), candidate("R", lane=REGIONAL), candidate("E", lane=ENDANGERED)]
        first, d1 = rank_portfolio(rows)
        second, d2 = rank_portfolio(rows, {"policy": {"lane_cycle": [ENDANGERED, REGIONAL, HIGH]}})
        self.assertNotEqual([r["entry_id"] for r in first], [r["entry_id"] for r in second])
        self.assertNotEqual(d1["policy_sha256"], d2["policy_sha256"])
        self.assertEqual(d1["dominance_edges"], d2["dominance_edges"])
        for entry_id in ("H", "R", "E"):
            self.assertEqual(d1["entries"][entry_id]["dimensions"], d2["entries"][entry_id]["dimensions"])
            self.assertEqual(d1["entries"][entry_id]["evidence_front"], d2["entries"][entry_id]["evidence_front"])

    def test_default_first_ten_lane_allocation(self):
        rows = [candidate(f"{lane}-{i}", lane=lane) for lane in (HIGH, REGIONAL, ENDANGERED) for i in range(12)]
        ranked, _ = rank_portfolio(rows)
        lanes = [row["allocation_lane"] for row in ranked[:10]]
        self.assertEqual((lanes.count(HIGH), lanes.count(REGIONAL), lanes.count(ENDANGERED)), (6, 3, 1))

    def test_lane_mapping_requires_provenance(self):
        with self.assertRaises(ValueError):
            rank_portfolio([candidate("A")], {"evidence": {"A": {"lane": ENDANGERED}}})

    def test_invalid_policy_and_duplicate_id_fail_closed(self):
        with self.assertRaises(ValueError):
            rank_portfolio([candidate("A"), candidate("A")])
        with self.assertRaises(ValueError):
            rank_portfolio([], {"policy": {"lane_cycle": [HIGH]}})
        with self.assertRaises(ValueError):
            rank_portfolio([], {"opportunity_view": "optimistic_point_estimate"})
        with self.assertRaises(ValueError):
            rank_portfolio([], {"scenario_label": ""})


if __name__ == "__main__":
    unittest.main(verbosity=2)
