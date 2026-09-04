"""Finite regression suite for complete A10 like-terms production."""
from __future__ import annotations

import copy
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent))

import build_like_terms as builder
import like_terms_checks as checks


class LikeTermsWorkflowTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.verified = checks.load_verified(require_route_reader=False)

    def test_complete_exact_scope_and_fixtures(self):
        rules = self.verified["rules"]
        self.assertEqual(len(list(self.verified["source"].iter())), 744)
        self.assertEqual(len([node for node in self.verified["source"].iter() if node.get("id")]), 108)
        self.assertEqual(len(self.verified["source"]), 35)
        self.assertEqual(
            [len(rules[name]) for name in (
                "math_fixtures", "prose_fixtures", "heading_fixtures",
                "math_layout_fixtures", "chart_fixtures", "reference_fixtures",
            )],
            [62, 45, 10, 2, 3, 1],
        )
        self.assertEqual(sum(not row["standalone_readout_authorized"] for row in rules["math_fixtures"]), 60)

    def test_all_tracks_have_exact_68_entry_recipe(self):
        hashes = {}
        for track in checks.TRACKS:
            blocks = checks.narration_blocks(self.verified, track)
            self.assertEqual(len(blocks), 68)
            self.assertEqual(len(dict(blocks)), 68)
            self.assertEqual(sum(mark.endswith("--answer-cue") for mark, _ in blocks), 8)
            hashes[track] = checks.sha(json.dumps(blocks, ensure_ascii=False, separators=(",", ":")).encode("utf-8"))
        self.assertEqual(len(hashes), 3)

    def test_live_node_copy_unknown_fixture_and_unknown_track_fail_closed(self):
        binding = checks.NarrationBinding(self.verified, "jv-academic")
        fixture = self.verified["rules"]["prose_fixtures"][0]
        node = checks.node_at(binding.target, fixture["source_path"])
        self.assertEqual(binding.read(fixture["id"], node), fixture["expected"]["jv-academic"])
        with self.assertRaisesRegex(ValueError, "unsupported_source_bound_narration"):
            binding.read(fixture["id"], copy.deepcopy(node))
        with self.assertRaisesRegex(ValueError, "unsupported_source_bound_narration"):
            binding.read("A10-COMB-P99", node)
        with self.assertRaisesRegex(ValueError, "unsupported_like_terms_track"):
            checks.NarrationBinding(self.verified, "jv-fallback")

    def test_source_target_track_and_rules_mutations_after_binding_fail_closed(self):
        fresh = checks.load_verified(require_route_reader=False)
        binding = checks.NarrationBinding(fresh, "jv-conversation")
        fixture = fresh["rules"]["prose_fixtures"][0]
        node = checks.node_at(binding.target, fixture["source_path"])
        original = node.text
        try:
            node.text = (node.text or "") + " owah"
            with self.assertRaisesRegex(ValueError, "changed_live_like_terms_context"):
                binding.read(fixture["id"], node)
        finally:
            node.text = original
        binding.track = "id-academic"
        with self.assertRaisesRegex(ValueError, "changed_like_terms_binding_context"):
            binding.read(fixture["id"], node)
        binding.track = binding.bound_track
        binding.rules["prose_fixtures"][0]["expected"]["jv-conversation"] += " jawaban palsu"
        with self.assertRaisesRegex(ValueError, "changed_like_terms_rules_after_binding"):
            binding.read(fixture["id"], node)

    def test_changed_rules_file_after_binding_fails_closed(self):
        binding = checks.NarrationBinding(self.verified, "id-academic")
        fixture = self.verified["rules"]["heading_fixtures"][0]
        node = checks.node_at(binding.target, fixture["source_path"])
        with tempfile.TemporaryDirectory(prefix="like-terms-rules-") as directory:
            changed = Path(directory) / "rules.json"
            changed.write_bytes(checks.RULES_PATH.read_bytes() + b" ")
            with patch.object(checks, "RULES_PATH", changed):
                with self.assertRaisesRegex(ValueError, "changed_like_terms_rules_after_binding"):
                    binding.read(fixture["id"], node)

    def test_real_cross_unit_destination_and_no_stub(self):
        route = checks.verify_route_reader(required=True)
        self.assertEqual(route["status"], "verified_existing_destination_reader")
        self.assertEqual(route["destination_fragment_count"], 1)
        reference = self.verified["rules"]["reference_fixtures"][0]
        self.assertEqual(reference["expected_route_proposal"], checks.ROUTE)
        self.assertFalse(reference["visible_text_mutation_authorized"])

    def test_reader_route_rejects_in_unit_or_missing_routes(self):
        valid = "".join(f'<a href="{checks.ROUTE}"></a>' for _ in range(3))
        checks.validate_reader_route(valid)
        with self.assertRaises(AssertionError):
            checks.validate_reader_route(valid.replace(checks.ROUTE, f"#{checks.EVALUATION_TARGET}", 1))
        with self.assertRaises(AssertionError):
            checks.validate_reader_route(valid + f'<span id="{checks.EVALUATION_TARGET}"></span>')

    def test_all_supplied_answers_and_nineteen_parts_recomputed_finitely(self):
        rules = copy.deepcopy(self.verified["rules"])
        checks.verify_finite_answers(rules)
        exercise_checks = rules["answer_policy"]["independent_checks"]["exercise_checks"]
        self.assertEqual(len(exercise_checks), 12)
        self.assertEqual(sum(row["part_count"] for row in exercise_checks), 19)
        practice = next(row for row in exercise_checks if row["exercise_id"] == "fs-id1170655163424")
        self.assertIsNone(practice["source_explicit_unmatched_statement"])
        self.assertEqual(practice["diagnostic_unmatched_not_new_answer"], [[9, "y", 1]])
        practice["source_explicit_unmatched_statement"] = "invented"
        with self.assertRaises(AssertionError):
            checks.verify_finite_answers(rules)

    def test_wrong_finite_coefficient_and_result_are_rejected(self):
        rules = copy.deepcopy(self.verified["rules"])
        independent = rules["answer_policy"]["independent_checks"]
        independent["exercise_checks"][0]["provided_answers"][1] = 225
        with self.assertRaises(AssertionError):
            checks.verify_finite_answers(rules)
        rules = copy.deepcopy(self.verified["rules"])
        combine = next(
            row for row in rules["answer_policy"]["independent_checks"]["exercise_checks"]
            if row["exercise_id"] == "fs-id1170655106283"
        )
        combine["provided_answer_coefficients"][0][0] = 13
        with self.assertRaises(AssertionError):
            checks.verify_finite_answers(rules)

    def test_generated_products_are_deterministic_and_current(self):
        generated = builder.products()
        for relative, raw in generated.items():
            self.assertEqual((checks.LANG / relative).read_bytes(), raw)
        self.assertEqual(len(generated), 12)
        page = generated[f"review/units/{checks.UNIT}.html"].decode("utf-8")
        checks.validate_reader_route(page)
        self.assertNotIn(f'id="{checks.EVALUATION_TARGET}"', page)
        self.assertEqual(page.count('data-route-fixture="A10-COMB-R01"'), 3)


if __name__ == "__main__":
    unittest.main()
