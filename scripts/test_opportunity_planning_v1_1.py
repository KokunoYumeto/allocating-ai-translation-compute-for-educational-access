"""Small deterministic tests for scope and planning-evidence semantics."""

import unittest

from opportunity_planning_v1_1 import assemble_context, exact_prior_for_row, parse_band, scenario_context


class PlanningScopeTests(unittest.TestCase):
    def setUp(self):
        self.prior = {
            "profile_id": "EXACT-1", "tag": "xx-Latn-XX", "evidence_ids": "S1;S2",
            "likely_reader_cohort": "advanced readers with limited bridge-language comfort",
            "confidence": "medium", "decision_caveat": "Illustrative fixture only",
            "R": "R2-3", "S": "S3", "A": "A3", "N": "N3", "V": "V2", "P": "P3", "F": "F2", "D": "D1",
        }
        self.row = {"entry_id": "NAT-X", "target_profiles": "xx-Latn-XX",
                    "named_output_profile_ids": "xx-Latn-XX",
                    "education_stages": "upper-secondary through undergraduate formal reasoning",
                    "first_bounded_package": "Produce the registered FR-2 Formal-reasoning core."}
        self.identity = {"sha256": "fixture", "bytes": 1}

    def test_band_parser_never_converts_unknown_to_zero(self):
        self.assertIsNone(parse_band("RU", "R"))
        self.assertIsNone(parse_band("248501794", "R"))
        self.assertEqual(parse_band("R0", "R"), (0, 0))

    def test_exact_formal_reasoning_scope_retains_provisional_prior(self):
        evidence = exact_prior_for_row(self.row, [self.prior], self.identity)
        self.assertEqual(evidence["dimensions"]["R"]["low"], 2)
        self.assertEqual(evidence["dimensions"]["R"]["assumption_status"], "prior_research_judgment")
        self.assertEqual(evidence["dimensions"]["R"]["source_register_identity"], self.identity)

    def test_no_transfer_to_early_years_or_small_residual(self):
        for package in ("ECE foundational recovery", "Finish 25 calculus units"):
            row = {**self.row, "first_bounded_package": package}
            dims = exact_prior_for_row(row, [self.prior], self.identity)["dimensions"]
            self.assertNotIn("R", dims)
            self.assertNotIn("S", dims)
            self.assertNotIn("A", dims)
            self.assertNotIn("N", dims)
            self.assertIn("V", dims)

    def test_unresolved_profile_does_not_acquire_reader_band(self):
        row = {**self.row, "education_stages": "target/profile resolution before production"}
        self.assertNotIn("R", exact_prior_for_row(row, [self.prior], self.identity)["dimensions"])

    def test_no_cross_territory_tag_match(self):
        row = {**self.row, "target_profiles": "xx-Latn-YY", "named_output_profile_ids": "xx-Latn-YY"}
        self.assertEqual(exact_prior_for_row(row, [self.prior], self.identity), {})

    def test_package_calibration_overrides_prior_but_not_lane(self):
        calibration = {"NAT-X": {"dimensions": {"R": {"low": 1, "high": 2, "basis": "new exact-package judgment"}}}}
        context, crosswalk = assemble_context([self.row], [self.prior], self.identity,
                                             {"evidence": {"NAT-X": {"lane": "regional_depth"}}}, calibration)
        self.assertEqual(context["evidence"]["NAT-X"]["dimensions"]["R"]["low"], 1)
        self.assertEqual(context["evidence"]["NAT-X"]["lane"], "regional_depth")
        self.assertEqual(crosswalk[0]["calibration_origin"], "package_specific_research")

    def test_no_unmapped_calibration_is_silently_discarded(self):
        with self.assertRaises(ValueError):
            assemble_context([self.row], [], self.identity, {"evidence": {}}, {"OTHER": {"dimensions": {}}})

    def test_baseline_never_invents_midpoint(self):
        context = {"evidence": {"X": {"dimensions": {"R": {"low": 1, "high": 4}}}}}
        baseline = scenario_context(context, "base")
        self.assertEqual(baseline["evidence"]["X"]["dimensions"]["R"], {"low": 1, "high": 4})

    def test_explicit_baseline_and_endpoints_remain_scenarios(self):
        context = {"evidence": {"X": {"dimensions": {"R": {"low": 1, "high": 4, "base": 3, "base_basis": "fixture"}}}}}
        for label, value in (("base", 3), ("cautious", 1), ("favorable", 4)):
            result = scenario_context(context, label)["evidence"]["X"]["dimensions"]["R"]
            self.assertEqual((result["low"], result["high"]), (value, value))
            self.assertIn("not confidence", result["scenario_interpretation"])
        self.assertEqual(context["evidence"]["X"]["dimensions"]["R"]["low"], 1)

    def test_measured_only_preserves_supplied_envelope(self):
        context = {"evidence": {"X": {"dimensions": {"R": {"low": 1, "high": 4, "base": 3}}}}}
        result = scenario_context(context, "measured_only")
        self.assertEqual(result["opportunity_view"], "measured_only")
        self.assertEqual(result["evidence"]["X"]["dimensions"]["R"]["high"], 4)

    def test_dialect_risk_direction_is_not_positive_benefit(self):
        context = {"evidence": {"X": {"dimensions": {"D": {"low": 1, "high": 4}}}}}
        self.assertEqual(scenario_context(context, "favorable")["evidence"]["X"]["dimensions"]["D"]["low"], 1)
        self.assertEqual(scenario_context(context, "cautious")["evidence"]["X"]["dimensions"]["D"]["low"], 4)


if __name__ == "__main__":
    unittest.main(verbosity=2)
