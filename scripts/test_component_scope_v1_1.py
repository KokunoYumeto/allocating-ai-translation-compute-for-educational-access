"""Regression checks for exact component ownership and calibration binding."""

import unittest

from allocation_policy_v1_1 import work_component_key
from component_scope_v1_1 import CONTRACT_PATH, attach_components, component_need_edges, load_contract
from opportunity_planning_v1_1 import load_calibrations


class ComponentScopeTests(unittest.TestCase):
    def setUp(self):
        self.contract = load_contract()

    def test_active_components_have_single_owner(self):
        owners = {}
        for entry_id, spec in self.contract.items():
            if spec.get("canonical_alias_of"):
                continue
            for component in spec["active_components"]:
                key = work_component_key(component)
                self.assertNotIn(key, owners)
                self.assertEqual(component["owner_entry_id"], entry_id)
                owners[key] = entry_id
        self.assertEqual(len(owners), 7)

    def test_reused_work_is_exactly_owned_elsewhere(self):
        active = {work_component_key(c): c["owner_entry_id"] for entry_id, spec in self.contract.items()
                  for c in spec["active_components"]}
        for entry_id, spec in self.contract.items():
            for component in spec["reuse_components"]:
                self.assertEqual(active[work_component_key(component)], component["owner_entry_id"])
                self.assertNotEqual(entry_id, component["owner_entry_id"])

    def test_urdu_has_no_hindi_need_or_active_target(self):
        spec = self.contract["IL-HU"]
        self.assertEqual({c["locale"] for c in spec["active_components"]}, {"ur-Aran-IN", "ur-Aran-PK"})
        self.assertEqual(component_need_edges("IL-HU", self.contract, [{"needs_profile_id": "HRN-004"}]), [])
        self.assertNotIn("GLB-007", spec["component_profile_ids"])

    def test_primary_recovery_and_ece_are_distinct(self):
        primary = self.contract["NAT-001"]["active_components"][0]
        ece = self.contract["SHC-BN"]["active_components"][0]
        self.assertEqual(primary["locale"], ece["locale"])
        self.assertNotEqual(work_component_key(primary), work_component_key(ece))
        self.assertNotEqual(primary["stage_id"], ece["stage_id"])

    def test_prose_and_machine_active_outputs_agree(self):
        row = attach_components({"entry_id": "IL-HU"}, self.contract)
        self.assertEqual(row["named_output_profile_ids"], "ur-Aran-IN;ur-Aran-PK")
        self.assertEqual(len(row["_reuse_components"]), 1)
        self.assertNotIn("hi-Deva-IN", row["active_work_components"])

    def test_every_active_component_matches_current_calibration(self):
        root = CONTRACT_PATH.parent.parent
        calibrations, _ = load_calibrations([root / "staging/opportunity_planning_v1_1/asia_core.json"])
        for entry_id, spec in self.contract.items():
            if not spec.get("requires_calibration_binding", True):
                continue
            calibrated = calibrations[entry_id]["component_planning"]
            self.assertEqual({c["locale"] for c in spec["active_components"]}, set(calibrations[entry_id]["target_profiles"]))
            self.assertEqual({(c["locale"], c["package_id"]) for c in spec["active_components"]},
                             {(c["profile"], c["component_id"]) for c in calibrated})

    def test_malay_architecture_is_same_work_not_second_commission(self):
        alias = self.contract["IL-IDMS"]
        owner = self.contract["NAT-040"]
        self.assertEqual(alias["canonical_alias_of"], "NAT-040")
        self.assertEqual([work_component_key(c) for c in alias["active_components"]],
                         [work_component_key(c) for c in owner["active_components"]])


if __name__ == "__main__":
    unittest.main(verbosity=2)
