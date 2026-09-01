"""Explicit, pre-ranking ownership of bounded educational work components.

This is a content-identity layer, not a language ranking. It narrows a mixed
architecture before opportunity calibration, so duplicate components cannot
retain another audience or consume a second commissioning position.
"""

from __future__ import annotations

import copy
import json
from pathlib import Path


CONTRACT_PATH = Path(__file__).resolve().parents[1] / "staging" / "component_work_ownership_v1_1.json"


def load_contract(path: Path = CONTRACT_PATH) -> dict[str, dict]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    result = {}
    for entry in payload["entries"]:
        entry_id = entry["entry_id"]
        if entry_id in result or not entry["active_components"]:
            raise ValueError("Missing active work or duplicate component owner: " + entry_id)
        expected_owner = entry.get("canonical_alias_of", entry_id)
        if any(c["owner_entry_id"] != expected_owner for c in entry["active_components"]):
            raise ValueError("Residualize scope before ranking: " + entry_id)
        result[entry_id] = entry
    return result


def component_need_edges(entry_id: str, contract: dict, original: list[dict]) -> list[dict]:
    """Retain only active stage/output edges; source registers stay unchanged."""
    spec = contract.get(entry_id)
    if not spec:
        return original
    edges = []
    for component in spec["active_components"]:
        for need in component.get("evidence_ids", []):
            if not need.startswith("HRN-"):
                continue
            edges.append({
                "needs_profile_id": need, "candidate_id": entry_id,
                "portfolio_entry_id": entry_id,
                "named_output_profile_id": component["locale"],
                "edge_role": "exact_active_work_component_need", "edge_status": "resolved",
                "package_id": component["package_id"], "stage_id": component["stage_id"],
                "modality": component["modality"],
            })
    return edges


def attach_components(row: dict, contract: dict) -> dict:
    spec = contract.get(row["entry_id"])
    if not spec:
        return row
    row = copy.deepcopy(row)
    row["_work_components"] = copy.deepcopy(spec["active_components"])
    row["_reuse_components"] = copy.deepcopy(spec["reuse_components"])
    row["named_output_profile_ids"] = ";".join(dict.fromkeys(c["locale"] for c in spec["active_components"]))
    row["component_scope_basis"] = "component_work_ownership_v1_1.json: exact active work, before opportunity calibration and ranking"
    row["active_work_components"] = json.dumps(spec["active_components"], ensure_ascii=False, separators=(",", ":"))
    row["reused_work_components"] = json.dumps(spec["reuse_components"], ensure_ascii=False, separators=(",", ":"))
    return row
