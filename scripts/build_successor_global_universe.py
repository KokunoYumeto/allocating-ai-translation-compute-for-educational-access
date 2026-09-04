#!/usr/bin/env python3
"""Build the append-only successor global language universe.

The builder preserves the legacy 945 target objects and their provenance as an
unchanged prefix, then evaluates legacy and imported evidence through one
closed ontology.  Population evidence, package context, proxy/context rows,
accessibility overlays, and supply/policy evidence remain separate lanes.

Only manifest-pinned files are imported.  There is deliberately no directory
glob, update, delete, score imputation, or implicit zero.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
from collections import Counter, defaultdict
from copy import deepcopy
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence


SCHEMA_VERSION = "interlanguage/global-educational-access-canonical-universe/2.0.0"
UNIVERSE_VERSION = "global-educational-access-universe/2.0.0"
ONTOLOGY_VERSION = "equal-admissibility-scoring-ontology/2.0.0"
IMPORT_ADAPTER_VERSION = "closed-regional-csv/2.0.0"
AUDIT_DATE = "2026-09-01"

DEFAULT_BASE = Path(__file__).resolve().parents[1]
DEFAULT_MANIFEST = Path("structured/SUCCESSOR_UNIVERSE_IMPORT_MANIFEST_v2.json")
DEFAULT_OUTPUT = Path("structured/canonical_universe_successor_v2.json")
DEFAULT_REPORT = Path("agent_reports/SUCCESSOR_GLOBAL_UNIVERSE_BUILDER_v2.md")
DEFAULT_RECEIPT = Path("qa/SUCCESSOR_UNIVERSE_BUILD_RECEIPT_20260901_v2.json")
DEFAULT_ROSTER = Path("structured/SUCCESSOR_TARGET_ROSTER_v2.json")
DEFAULT_ROSTER_RECEIPT = Path("qa/SUCCESSOR_TARGET_ROSTER_RECEIPT_20260901_v2.json")

MANIFEST_GENESIS = {
    "manifest_sha256": "ceb4c79b7ffea22f0d1a46132bf56cca5cfcae542a4cf2cacd01421bb1328697",
    "contract_path": "structured/schema/SUCCESSOR_UNIVERSE_IMPORT_CONTRACT_v2.json",
    "contract_bytes": 7186,
    "contract_sha256": "0e99d86613c7a9cfd2245b0f99e53be1b0a5e47ea4013e57f8d4418be8483edf",
    "regional_prefix_count": 1,
    "regional_prefix_sha256": "d21ca66d09b0f86288d7e8c4ab4f9820a16ad22669e0f5459c9f210c6eecfe55",
    "specialized_count": 6,
    "specialized_sha256": "b2d71d488df7c2bbc97dc520081c553db80700c00e10e0518e529f96c8676680",
}

CORE_INPUTS = {
    "structured/canonical_universe_proposal.json": "185344e61d3227a7d367211bcff39d78efe0b336e68e6a45abb2e57d717f11be",
    "structured/large_language_population_strata_proposal.json": "f18854be60843a1e78708065a59ac3985eefb1c78cc6e3e3f8728686896464bd",
    "agent_reports/GLOBAL_LARGE_LANGUAGE_CONTROLS.md": "44ef486ea3dc58e5db21d6fd14c728fb7323b76738aecbc108d59359e921f3ae",
    "agent_reports/LARGE_COHORT_EQUAL_INCLUSION_AUDIT.md": "c182bf7a53afda13d405832377110ddfb0baf03bcbdef9eb0e5cefe64bc19a4e",
    "structured/empirical_event_gap_ledger_v2.json": "6a29239b2d5f297b67d87719852991f616e98566f53aef0f778a905a1253d582",
    "scripts/needs_access_ranking.py": "53ff7113102bedba57f8b87d0c23abe3c0e64b833ce591bf09fbb1f57500cb86",
    "structured/schema/SCHEMA_CONTRACT.json": "c022ac483b781d5f19d88926d2eae299f7f91d42b163b632c8490eb82107b933",
    "qa/FULL_EXECUTABLE_TEST_RECEIPT_20260901_v2.json": "0bd60937282dac62aabb68cc37eafad2fef66ee0b0c87fa652630aaee7ce453e",
}

CANONICAL_PUTONGHUA_MEASURE_ID = "pop:6698b2f0da2a35b453dc1faf"
LLPS_QUARANTINE = {
    "LLPS-CMN-CN-ABILITY-2020": (
        "INCOMPATIBLE_DERIVED_DENOMINATOR",
        "The 80.72% survey rate has no compatible published person denominator or design uncertainty in the locator.",
        ["regional:cmn-cn-putonghua-rate-2020"],
    ),
    "LLPS-JA-JP-EXPOSURE-2024": (
        "INCOMPATIBLE_CONSTRUCTS_AS_INTERVAL",
        "Japanese nationals and total residents are distinct exposure definitions, not interval bounds.",
        ["regional:ja-jp-nationality-exposure-2024", "regional:ja-jp-resident-exposure-2024"],
    ),
    "LLPS-JA-JP-ADULT-LOW-SKILL-2023": (
        "PSEUDO_PRECISION_UNPROPAGATED_UNCERTAINTY",
        "The proposed 5,229,000 is a rounded 7% derivation without survey or rounding uncertainty.",
        [],
    ),
    "LLPS-TR-TR-EXPOSURE-2024": (
        "INCOMPATIBLE_CONSTRUCTS_AS_INTERVAL",
        "A rounded speaker lower bound and a resident ceiling are different constructs, not one interval.",
        ["regional:tr-tr-speaker-lower-bound", "regional:tr-tr-resident-ceiling-2024"],
    ),
}

MACRO_TARGET_IDS = {
    "lang:arb-Arab-001",
    "lang:de-Latn-001",
    "lang:en-Latn-001",
    "lang:es-Latn-001",
    "lang:fr-Latn-001",
    "lang:ko-Kore-001",
    "lang:pt-Latn-001",
    "lang:ru-Cyrl-001",
    "lang:sw-Latn-001",
}

SUPERSEDED_TARGETS = {
    "lang:cmn-Hans-CN:spoken": {
        "effective_status": "SUPERSEDED_IDENTITY_QUARANTINE",
        "superseded_by": "lang:cmn-CN:spoken",
        "reason": "A spoken-only target cannot inherit a Hans script identity.",
    }
}

SIGNED_TARGET_MAP = {
    "SL-ASL-US-GAP": "lang:ase-US",
    "SL-ASL-CA-2021-KNOW": "lang:ase-CA",
    "SL-BSL-ENG-2021-MAIN": "lang:bfi-GB",
    "SL-BSL-WLS-2021-MAIN": "lang:bfi-GB",
    "SL-BSL-SCT-2022-CANUSE": "lang:bfi-GB",
    "SL-BSL-NIR-2021-MAIN": "lang:bfi-GB",
    "SL-LIBRAS-BR-2019-KNOW": "lang:bzs-BR",
    "SL-LSF-FR-1998-99-USE": "lang:fsl-FR",
    "SL-DGS-DE-2007-INTERP-PROXY": "lang:gsg-DE",
    "SL-JSL-JP-2006-SIGNMEDIATED": "lang:jsl-JP",
    "SL-CSL-CN-2025-HEARING-PROXY": "lang:csl-CN",
    "SL-ISLINDIA-IN-2011-HEARING-PROXY": "lang:ins-IN",
    "SL-AUSLAN-AU-2021-HOME": "lang:asf-AU",
    "SL-NZSL-NZ-2023-CANUSE": "lang:nzs-NZ",
    "SL-LSQ-CA-2021-KNOW": "lang:fcs-CA",
    "SL-IRSL-IE-2011-HOME": "lang:isg-IE",
    "SL-SPAIN-SIGN-2020-USE": None,
}

RANKABILITY_STATUSES = {
    "POINT_DISTRIBUTION",
    "INTERVAL_ONLY",
    "INSUFFICIENT_PUBLIC_EVIDENCE",
    "STRUCTURAL_ZERO",
}


class BuildError(ValueError):
    """Raised when an input violates the pinned successor contract."""


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def canonical_json_bytes(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def canonical_sha256(value: Any) -> str:
    return sha256_bytes(canonical_json_bytes(value))


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def read_csv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None:
            raise BuildError(f"CSV has no header: {path}")
        rows = [dict(row) for row in reader]
        return list(reader.fieldnames), rows


def exact_relative(base: Path, value: str) -> Path:
    candidate = (base / Path(value)).resolve()
    try:
        candidate.relative_to(base.resolve())
    except ValueError as exc:
        raise BuildError(f"manifest path escapes base directory: {value}") from exc
    return candidate


def _number(text: Any, *, label: str) -> int | float | None:
    if text is None or text == "":
        return None
    try:
        value = Decimal(str(text))
    except InvalidOperation as exc:
        raise BuildError(f"{label} is not a decimal: {text!r}") from exc
    if not value.is_finite() or value < 0:
        raise BuildError(f"{label} must be finite and nonnegative")
    if value == value.to_integral_value():
        return int(value)
    result = float(value)
    if not math.isfinite(result):
        raise BuildError(f"{label} is not a finite JSON number")
    return result


def _multiply(value: int | float | None, multiplier: int | float | None) -> int | float | None:
    if value is None:
        return None
    if multiplier is None:
        raise BuildError("numeric person normalization requires a multiplier")
    result = Decimal(str(value)) * Decimal(str(multiplier))
    return int(result) if result == result.to_integral_value() else float(result)


def _bound_values(
    low: int | float | None,
    base: int | float | None,
    high: int | float | None,
    semantics: str,
    multiplier: int | float | None,
) -> dict[str, int | float | None]:
    if semantics == "NONE":
        if any(value is not None for value in (low, base, high)):
            raise BuildError("NONE bound semantics cannot carry numeric values")
        return {"low": None, "base": None, "high": None}
    scaled = {
        "low": _multiply(low, multiplier),
        "base": _multiply(base, multiplier),
        "high": _multiply(high, multiplier),
    }
    if semantics == "POINT":
        if scaled["base"] is None:
            raise BuildError("POINT bound semantics requires source_base")
    elif semantics == "INTERVAL":
        if scaled["low"] is None or scaled["high"] is None:
            raise BuildError("INTERVAL bound semantics requires source_low and source_high")
    elif semantics == "LOWER_BOUND":
        value = scaled["low"] if scaled["low"] is not None else scaled["base"]
        if value is None:
            raise BuildError("LOWER_BOUND requires source_low or source_base")
        scaled = {"low": value, "base": None, "high": None}
    elif semantics == "UPPER_BOUND":
        value = scaled["high"] if scaled["high"] is not None else scaled["base"]
        if value is None:
            raise BuildError("UPPER_BOUND requires source_high or source_base")
        scaled = {"low": None, "base": None, "high": value}
    else:
        raise BuildError(f"unsupported bound semantics: {semantics!r}")
    if scaled["low"] is not None and scaled["high"] is not None and scaled["low"] > scaled["high"]:
        raise BuildError("normalized low exceeds high")
    if scaled["base"] is not None:
        if scaled["low"] is not None and scaled["base"] < scaled["low"]:
            raise BuildError("normalized base is below low")
        if scaled["high"] is not None and scaled["base"] > scaled["high"]:
            raise BuildError("normalized base exceeds high")
    return scaled


def _rankability(values: Mapping[str, Any], direct: bool) -> str:
    if not direct:
        return "INSUFFICIENT_PUBLIC_EVIDENCE"
    if values.get("base") is not None:
        return "POINT_DISTRIBUTION"
    if values.get("low") is not None and values.get("high") is not None:
        return "INTERVAL_ONLY"
    return "INSUFFICIENT_PUBLIC_EVIDENCE"


def _row_sha(row: Mapping[str, str], *, omit: str | None = None) -> str:
    body = {key: value for key, value in row.items() if key != omit}
    return canonical_sha256(body)


def _split_semicolon(value: str) -> list[str]:
    return [item for item in value.split(";") if item]


def _is_macro_target(target: Mapping[str, Any]) -> bool:
    target_id = target["language_target_id"]
    tags = target.get("language_tags", [])
    reasons = " ".join(target.get("unranked_reasons", [])).casefold()
    return (
        target_id in MACRO_TARGET_IDS
        or target_id.startswith("macro:")
        or target_id.split(":", 1)[-1].split(":", 1)[0].endswith("-001")
        or any(str(tag).endswith("-001") for tag in tags)
        or "macro" in reasons
    )


def _source_record(
    source_id: str,
    *,
    origin_file: str,
    title: str,
    organization: str = "Audited input authority",
    year: str = "2026",
    url: str = "",
    claim_scope: str = "Successor-universe import evidence",
    row_number: int = 1,
    row_sha256: str,
) -> dict[str, Any]:
    return {
        "source_id": source_id,
        "canonical_source_id": source_id,
        "same_url_alias_ids": [source_id],
        "title": title,
        "organization": organization,
        "year": year,
        "url": url,
        "access_date": AUDIT_DATE,
        "claim_scope": claim_scope,
        "origin_file": origin_file,
        "source_row_number": row_number,
        "source_row_sha256": row_sha256,
        "undated": year in {"", "n.d."},
    }


def _provenance_record(
    *,
    input_id: str,
    origin_file: str,
    row_number: int,
    row_sha: str,
    output_type: str,
    output_id: str,
    target_ids: Sequence[str] = (),
    measure_ids: Sequence[str] = (),
    source_id: str = "",
) -> dict[str, Any]:
    return {
        "provenance_id": f"prov:successor:{sha256_bytes(f'{origin_file}|{input_id}'.encode())[:24]}",
        "input_candidate_id": input_id,
        "origin_file": origin_file,
        "source_row_number": row_number,
        "original_row_sha256": row_sha,
        "effective_row_sha256": row_sha,
        "applied_update": False,
        "input_disposition": "successor_append_only_import",
        "primary_output_type": output_type,
        "primary_output_id": output_id,
        "language_target_ids": list(target_ids),
        "population_measure_ids": list(measure_ids),
        "population_measure_disposition": "typed_nonadditive_successor_evidence",
        "population_source_id": source_id or None,
        "preferred_population_row_decision": "ontology_evaluated_not_automatically_scored",
        "mapped_exactly_once": True,
    }


def _assignment_from_provenance(row: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "input_candidate_id": row["input_candidate_id"],
        "origin_file": row["origin_file"],
        "primary_output_type": row["primary_output_type"],
        "primary_output_id": row["primary_output_id"],
        "language_target_ids": list(row["language_target_ids"]),
        "population_measure_ids": list(row["population_measure_ids"]),
    }


def validate_pinned_inputs(
    base: Path,
    manifest_path: Path,
    *,
    allow_scorer_transition: bool = False,
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    identities: dict[str, Any] = {}
    for relative, expected in CORE_INPUTS.items():
        path = exact_relative(base, relative)
        actual = sha256_file(path)
        transitioning = relative in {
            "scripts/needs_access_ranking.py",
            "structured/schema/SCHEMA_CONTRACT.json",
            "qa/FULL_EXECUTABLE_TEST_RECEIPT_20260901_v2.json",
        }
        if actual != expected and not (allow_scorer_transition and transitioning):
            raise BuildError(f"pinned core input hash mismatch for {relative}: {actual} != {expected}")
        if allow_scorer_transition and transitioning:
            identities[relative] = {
                "bytes": None,
                "sha256": None,
                "binding_status": "PENDING_NOT_IMPORTED_FOR_UNIVERSE_DATA",
            }
        else:
            identities[relative] = {"bytes": path.stat().st_size, "sha256": actual}

    receipt = read_json(base / "qa/FULL_EXECUTABLE_TEST_RECEIPT_20260901_v2.json")
    receipt_hashes = {
        item["path"]: item["sha256"].lower() for item in receipt.get("critical_artifacts", [])
    }
    for relative in (
        "scripts/needs_access_ranking.py",
        "structured/schema/SCHEMA_CONTRACT.json",
        "structured/empirical_event_gap_ledger_v2.json",
    ):
        transitioning = relative in {
            "scripts/needs_access_ranking.py",
            "structured/schema/SCHEMA_CONTRACT.json",
        }
        if receipt_hashes.get(relative) != identities[relative].get("sha256") and not (
            allow_scorer_transition and transitioning
        ):
            raise BuildError(f"executable receipt does not bind current {relative}")

    manifest = read_json(manifest_path)
    if manifest.get("schema") != "interlanguage/successor-universe-import-manifest/2.0.0":
        raise BuildError("unsupported successor import manifest schema")
    if manifest.get("universe_version") != UNIVERSE_VERSION:
        raise BuildError("successor import manifest has the wrong universe version")
    if manifest.get("merge_mode") != "append_only_non_destructive":
        raise BuildError("successor import manifest is not append-only")
    if manifest.get("implicit_directory_scan") is not False:
        raise BuildError("implicit directory scanning must remain disabled")

    contract_spec = manifest["contract"]
    if contract_spec != {
        "path": MANIFEST_GENESIS["contract_path"],
        "bytes": MANIFEST_GENESIS["contract_bytes"],
        "sha256": MANIFEST_GENESIS["contract_sha256"],
    }:
        raise BuildError("successor import contract identity differs from the externally pinned genesis")
    regional_imports = manifest.get("regional_csv_imports")
    specialized_imports = manifest.get("specialized_imports")
    if not isinstance(regional_imports, list) or len(regional_imports) < MANIFEST_GENESIS["regional_prefix_count"]:
        raise BuildError("successor manifest removed its frozen regional prefix")
    if canonical_sha256(regional_imports[: MANIFEST_GENESIS["regional_prefix_count"]]) != MANIFEST_GENESIS["regional_prefix_sha256"]:
        raise BuildError("successor manifest mutated or reordered its frozen regional prefix")
    if (
        not isinstance(specialized_imports, list)
        or len(specialized_imports) != MANIFEST_GENESIS["specialized_count"]
        or canonical_sha256(specialized_imports) != MANIFEST_GENESIS["specialized_sha256"]
    ):
        raise BuildError("successor manifest mutated its frozen specialized-import set")
    allowed_regional_keys = {"path", "adapter", "bytes", "sha256"}
    regional_paths: list[str] = []
    for index, spec in enumerate(regional_imports):
        if set(spec) != allowed_regional_keys or spec["adapter"] != "closed_regional_csv_v2":
            raise BuildError(f"regional manifest batch {index} violates the closed append schema")
        regional_paths.append(spec["path"])
    if len(regional_paths) != len(set(regional_paths)):
        raise BuildError("successor manifest reuses a regional batch path")
    specialized_authority_paths: set[str] = set()
    for spec in specialized_imports:
        for key, value in spec.items():
            if key == "path" or key.endswith("_path"):
                if value in specialized_authority_paths:
                    raise BuildError(f"successor manifest reuses a specialized authority path: {value}")
                specialized_authority_paths.add(value)
    if set(regional_paths) & specialized_authority_paths:
        raise BuildError("successor manifest reuses an authority path across adapter families")
    contract_path = exact_relative(base, contract_spec["path"])
    if contract_path.stat().st_size != contract_spec["bytes"] or sha256_file(contract_path) != contract_spec["sha256"]:
        raise BuildError("regional import contract identity mismatch")
    identities[contract_spec["path"]] = {
        "bytes": contract_path.stat().st_size,
        "sha256": sha256_file(contract_path),
    }
    identities[str(manifest_path.relative_to(base)).replace("\\", "/")] = {
        "bytes": manifest_path.stat().st_size,
        "sha256": sha256_file(manifest_path),
    }
    authority_binding = {
        "status": (
            "DATA_UNIVERSE_FROZEN_SCORER_BINDING_PENDING"
            if allow_scorer_transition
            else "FROZEN_EXECUTABLE_RECEIPT_BOUND"
        ),
        "final_artifact_allowed": True,
        "universe_data_final": True,
        "ranking_or_selection_allowed": not allow_scorer_transition,
        "scorer_binding_status": (
            "PENDING_NO_NORMATIVE_SCORER_HASH_BOUND"
            if allow_scorer_transition
            else "FROZEN_EXECUTABLE_RECEIPT_BOUND"
        ),
        "schema_binding_status": (
            "PENDING_ADDITIVE_SCHEMA_RECEIPT_NOT_IMPORTED"
            if allow_scorer_transition
            else "FROZEN_EXECUTABLE_RECEIPT_BOUND"
        ),
        "normative_scorer_sha256": None if allow_scorer_transition else identities["scripts/needs_access_ranking.py"]["sha256"],
        "pending_authorities": (
            [
                "scripts/needs_access_ranking.py",
                "structured/schema/SCHEMA_CONTRACT.json",
                "qa/FULL_EXECUTABLE_TEST_RECEIPT_20260901_v2.json",
            ]
            if allow_scorer_transition
            else []
        ),
        "note": (
            "The successor universe data and roster are frozen independently. Scorer, additive schema, and full-suite "
            "receipt bytes are intentionally unbound and non-normative; no ranking or selection may be produced until "
            "a later versioned executable binding is frozen."
            if allow_scorer_transition
            else "Current scorer and schema/event inputs are bound by the frozen executable receipt."
        ),
    }
    return manifest, identities, authority_binding


def normalize_event_ledger(
    ledger: Mapping[str, Any], canonical_target_ids: set[str]
) -> tuple[
    list[dict[str, Any]],
    dict[str, list[dict[str, Any]]],
    dict[str, list[dict[str, Any]]],
]:
    if ledger.get("schema") != "interlanguage/population-stage-endpoint-event-proposal/2.0.0":
        raise BuildError("unsupported empirical event ledger schema")
    bindings: list[dict[str, Any]] = []
    by_target: dict[str, list[dict[str, Any]]] = defaultdict(list)
    by_measure: dict[str, list[dict[str, Any]]] = defaultdict(list)
    event_ids: set[str] = set()
    for event in ledger["events"]:
        event_id = event["event_id"]
        if event_id in event_ids:
            raise BuildError(f"duplicate event_id in ledger: {event_id}")
        event_ids.add(event_id)
        target_id = event["language_target_id"]
        if target_id not in canonical_target_ids:
            raise BuildError(f"event references a noncanonical legacy target: {target_id}")
        binding = {
            "event_id": event_id,
            "language_target_id": target_id,
            "package_intervention_id": event["package_intervention_id"],
            "endpoint_id": event["endpoint_id"],
            "endpoint_operational_status": event["endpoint_operational_status"],
            "stage_ids": list(event["stage_ids"]),
            "stage_identity_status": event["stage_identity_status"],
            "population_measure_id": event["population_measure_id"],
            "population_denominator_id": event["population_denominator_id"],
            "population_event_role": event["population_event_role"],
            "source_population_unit": event["source_population_unit"],
            "normalization_multiplier": event["normalization_multiplier"],
            "normalization_status": event["normalization_status"],
            "person_basis_status": event["person_basis_status"],
            "population_values_persons": {
                key: _number(value, label=f"{event_id}.population_values_persons.{key}")
                for key, value in event["population_values_persons"].items()
            },
            "rankable_now": bool(event["rankable_now"]),
        }
        bindings.append(binding)
        by_target[target_id].append(binding)
        if binding["population_measure_id"]:
            by_measure[binding["population_measure_id"]].append(binding)
    if len(bindings) != ledger["counts"]["event_proposal_rows"]:
        raise BuildError("event binding count differs from the ledger receipt")
    if {row["language_target_id"] for row in bindings} != canonical_target_ids:
        raise BuildError("event ledger does not preserve all legacy language targets")
    return bindings, by_target, by_measure


def _one_normalized_person_bundle(
    measure_id: str, event_rows: Sequence[Mapping[str, Any]]
) -> tuple[dict[str, Any], str, list[str], list[str], list[str], list[str]]:
    bundles = {
        canonical_sha256(row["population_values_persons"]): row["population_values_persons"]
        for row in event_rows
        if any(value is not None for value in row["population_values_persons"].values())
    }
    if len(bundles) > 1:
        values = {"low": None, "base": None, "high": None}
        status = "INCONSISTENT_EVENT_NORMALIZATION"
    elif bundles:
        values = deepcopy(next(iter(bundles.values())))
        status = "PRESERVED_FROM_EMPIRICAL_EVENT_LEDGER_V2"
    else:
        values = {"low": None, "base": None, "high": None}
        status = "NO_PERSON_NORMALIZATION_IN_EVENT_LEDGER"
    return (
        values,
        status,
        sorted({row["event_id"] for row in event_rows}),
        sorted({row["endpoint_id"] for row in event_rows}),
        sorted({stage for row in event_rows for stage in row["stage_ids"]}),
        sorted({row["stage_identity_status"] for row in event_rows}),
    )


def adapt_canonical_population(
    canonical: Mapping[str, Any],
    events_by_measure: Mapping[str, Sequence[Mapping[str, Any]]],
    target_by_id: Mapping[str, Mapping[str, Any]],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    evidence: list[dict[str, Any]] = []
    quarantine: list[dict[str, Any]] = []
    seen: set[str] = set()
    for original in canonical["population_measures"]:
        measure_id = original["population_measure_id"]
        if measure_id in seen:
            raise BuildError(f"duplicate legacy population measure: {measure_id}")
        seen.add(measure_id)
        event_rows = list(events_by_measure.get(measure_id, []))
        values, normalization_status, event_ids, endpoint_ids, stage_ids, stage_statuses = (
            _one_normalized_person_bundle(measure_id, event_rows)
        )
        target_ids = list(original["language_target_ids"])
        exact_single_target = (
            len(target_ids) == 1
            and not _is_macro_target(target_by_id[target_ids[0]])
            and target_by_id[target_ids[0]]["exactness"] == "exact"
        )
        direct = (
            original["rank_eligibility"].startswith("eligible_direct_typed_measure")
            and exact_single_target
            and normalization_status == "PRESERVED_FROM_EMPIRICAL_EVENT_LEDGER_V2"
        )
        record = {
            "population_evidence_id": f"canonical:{measure_id}",
            "origin_lane": "legacy_canonical_population",
            "origin_record_id": measure_id,
            "language_target_ids": target_ids,
            "measure_class": original["measure_class"],
            "measure_role": (
                "stage_need"
                if any(row["population_event_role"] == "DIRECT_NEED_NUMERATOR_COHORT" for row in event_rows)
                else (
                    "stage_opportunity"
                    if any(row["population_event_role"] == "DIRECT_LEARNER_OR_APPLIED_COHORT" for row in event_rows)
                    else "language_population_or_context"
                )
            ),
            "source_values": {
                "low": original["population_low"],
                "base": original["population_base"],
                "high": original["population_high"],
                "unit": original["population_unit"],
            },
            "person_normalization": {
                "status": normalization_status,
                "values_persons": values,
                "normalization_statuses": sorted({row["normalization_status"] for row in event_rows}),
                "person_basis_statuses": sorted({row["person_basis_status"] for row in event_rows}),
            },
            "population_definition": original["population_definition"],
            "reference_year": original["population_reference_year"],
            "source_ids": [original["population_source_id"]],
            "source_url": original["population_source_url"],
            "endpoint_type": "legacy_event_bound_population",
            "endpoint_ids": endpoint_ids,
            "stage_ids": stage_ids,
            "stage_identity_statuses": stage_statuses,
            "event_ids": event_ids,
            "additivity_class": original["aggregation_policy"],
            "overlap_group": original["shared_denominator_group"],
            "target_binding": "DIRECT_TARGET_ONLY" if direct else "CONTEXT_NO_INHERITANCE",
            "population_rankability_status": _rankability(values, direct),
            "rank_eligibility_source_label": original["rank_eligibility"],
            "score_eligible": False,
            "score": None,
        }
        if measure_id == CANONICAL_PUTONGHUA_MEASURE_ID:
            record["target_binding"] = "QUARANTINED_NO_INHERITANCE"
            record["population_rankability_status"] = "INSUFFICIENT_PUBLIC_EVIDENCE"
            quarantine.append(
                {
                    "quarantine_id": f"quarantine:canonical:{measure_id}",
                    "origin_lane": "legacy_canonical_population",
                    "origin_record_id": measure_id,
                    "reason_codes": ["INCOMPATIBLE_DERIVED_DENOMINATOR", "UNPROPAGATED_DESIGN_UNCERTAINTY"],
                    "reason": "The Putonghua rate was multiplied by an incompatible all-ages territorial denominator.",
                    "replacement_ids": ["regional:cmn-cn-putonghua-rate-2020"],
                    "record": record,
                    "original_payload": deepcopy(original),
                }
            )
        else:
            evidence.append(record)
    return evidence, quarantine


def _llps_source_id(source_id: str) -> str:
    return f"source:llps:{source_id.lower()}"


def _llps_source_to_registry(source: Mapping[str, Any], row_number: int) -> dict[str, Any]:
    row_sha = canonical_sha256(source)
    return {
        "source_id": _llps_source_id(source["source_id"]),
        "canonical_source_id": _llps_source_id(source["source_id"]),
        "same_url_alias_ids": [_llps_source_id(source["source_id"]), source["source_id"]],
        "upstream_source_id": source["source_id"],
        "title": source["title"],
        "organization": source["institution_or_author"],
        "year": source["reference_year"],
        "url": source["url_or_doi"],
        "access_date": AUDIT_DATE,
        "claim_scope": source["locator"],
        "origin_file": "structured/large_language_population_strata_proposal.json",
        "source_row_number": row_number,
        "source_row_sha256": row_sha,
        "undated": source["reference_year"] in {"", "n.d."},
    }


def _llps_stage_identity(row: Mapping[str, Any]) -> tuple[list[str], str]:
    endpoint = row["endpoint"]
    if endpoint == "school_academic_language_support":
        return ["E1", "E2", "E3"], "COMPOUND_WITH_OTHER_UNMAPPED"
    if endpoint == "higher_education_opportunity":
        return ["E5", "E6"], "EXPLICIT_COMPOUND_STAGE"
    if endpoint == "adult_integrated_literacy_numeracy_digital_need":
        return ["E6"], "SOURCE_NAMED_ADULT_STAGE"
    if endpoint == "formal_education_opportunity":
        return [], "COMPOUND_UNSPLIT_FORMAL_EDUCATION"
    return [], "NOT_STAGE_SPECIFIC"


def _package_id_for_llps(source_id: str) -> str:
    if source_id == "PKG-WEST-AFRICAN-PIDGIN-SIX":
        return "package:west-african-pidgin-six-v2"
    return f"package:llps:{source_id.lower()}"


def initialize_llps_packages(
    proposal: Mapping[str, Any],
    package_profiles: dict[str, dict[str, Any]],
) -> tuple[dict[str, str], dict[str, dict[str, Any]], list[dict[str, Any]]]:
    stratum_by_id = {row["stratum_id"]: row for row in proposal["population_strata"]}
    component_to_package: dict[str, str] = {}
    aggregate_context: list[dict[str, Any]] = []
    package_source_by_id: dict[str, dict[str, Any]] = {}
    for profile in proposal["parallel_or_common_core_package_profiles"]:
        effective_id = _package_id_for_llps(profile["package_profile_id"])
        component_targets = sorted(
            {
                target_id
                for stratum_id in profile["component_stratum_ids"]
                for target_id in stratum_by_id[stratum_id]["language_target_ids"]
            }
        )
        if effective_id == "package:west-african-pidgin-six-v2" and effective_id in package_profiles:
            component_targets = list(package_profiles[effective_id]["component_target_ids"])
            package_profiles[effective_id]["source_package_profile_ids"].append(profile["package_profile_id"])
        elif effective_id not in package_profiles:
            package_profiles[effective_id] = {
                "package_id": effective_id,
                "label": profile["label"],
                "component_target_ids": component_targets,
                "context_measure_ids": [],
                "measure_inheritance_policy": "NONE",
                "population_measure_ids": [],
                "rankability_status": "INSUFFICIENT_PUBLIC_EVIDENCE",
                "score": None,
                "source_package_profile_ids": [profile["package_profile_id"]],
            }
        for stratum_id in profile["component_stratum_ids"]:
            component_to_package[stratum_id] = effective_id
        package_source_by_id[effective_id] = profile

        if len(profile["component_stratum_ids"]) > 1:
            context_id = f"llps-package:{profile['package_profile_id']}"
            aggregate_context.append(
                {
                    "package_context_measure_id": context_id,
                    "origin_lane": "large_language_package_profile",
                    "origin_record_id": profile["package_profile_id"],
                    "package_id": effective_id,
                    "component_target_ids": component_targets,
                    "population_values_persons": {
                        "low": profile["population_low"],
                        "base": profile["population_base"],
                        "high": profile["population_high"],
                    },
                    "source_unit": profile["population_unit"],
                    "aggregation": profile["aggregation"],
                    "target_binding": "PACKAGE_CONTEXT_NO_INHERITANCE",
                    "population_rankability_status": "INSUFFICIENT_PUBLIC_EVIDENCE",
                    "score": None,
                }
            )
            package_profiles[effective_id]["context_measure_ids"].append(context_id)
    return component_to_package, package_source_by_id, aggregate_context


def adapt_llps(
    proposal: Mapping[str, Any],
    target_by_id: Mapping[str, Mapping[str, Any]],
    package_profiles: dict[str, dict[str, Any]],
) -> tuple[
    list[dict[str, Any]],
    list[dict[str, Any]],
    list[dict[str, Any]],
    list[dict[str, Any]],
    list[dict[str, Any]],
]:
    evidence: list[dict[str, Any]] = []
    quarantine: list[dict[str, Any]] = []
    provenance: list[dict[str, Any]] = []
    sources = [_llps_source_to_registry(row, index) for index, row in enumerate(proposal["sources"], 1)]
    component_to_package, _, package_context = initialize_llps_packages(proposal, package_profiles)
    package_context_by_id = {row["package_context_measure_id"]: row for row in package_context}

    for row_number, original in enumerate(proposal["population_strata"], 1):
        stratum_id = original["stratum_id"]
        row_sha = canonical_sha256(original)
        target_ids = list(original["language_target_ids"])
        if any(target_id not in target_by_id for target_id in target_ids):
            raise BuildError(f"LLPS stratum references unknown target: {stratum_id}")
        if stratum_id in LLPS_QUARANTINE:
            code, reason, replacements = LLPS_QUARANTINE[stratum_id]
            quarantine_id = f"quarantine:llps:{stratum_id}"
            quarantine.append(
                {
                    "quarantine_id": quarantine_id,
                    "origin_lane": "large_language_population_strata",
                    "origin_record_id": stratum_id,
                    "reason_codes": [code],
                    "reason": reason,
                    "replacement_ids": replacements,
                    "original_payload": deepcopy(original),
                }
            )
            provenance.append(
                _provenance_record(
                    input_id=stratum_id,
                    origin_file="structured/large_language_population_strata_proposal.json",
                    row_number=row_number,
                    row_sha=row_sha,
                    output_type="quarantine",
                    output_id=quarantine_id,
                    target_ids=target_ids,
                    source_id=_llps_source_id(original["source_ids"][0]),
                )
            )
            continue

        stage_ids, stage_status = _llps_stage_identity(original)
        values = {
            "low": original["population_low"],
            "base": original["population_base"],
            "high": original["population_high"],
        }
        audit_adjustments: list[str] = []
        if stratum_id == "LLPS-BN-BD-L1PROXY-2022":
            values = {"low": None, "base": original["population_base"], "high": None}
            audit_adjustments.append("discarded rounding band as non-confidence interval; retained mixed-year proxy as context")

        package_id = component_to_package.get(stratum_id)
        multi_target = len(target_ids) != 1
        if multi_target:
            if package_id is None:
                package_id = f"package:llps-shared:{stratum_id.lower()}"
                package_profiles.setdefault(
                    package_id,
                    {
                        "package_id": package_id,
                        "label": original["exact_variety_or_register"],
                        "component_target_ids": sorted(target_ids),
                        "context_measure_ids": [],
                        "measure_inheritance_policy": "NONE",
                        "population_measure_ids": [],
                        "rankability_status": "INSUFFICIENT_PUBLIC_EVIDENCE",
                        "score": None,
                        "source_package_profile_ids": [],
                    },
                )
            context_id = f"llps:{stratum_id}"
            context_record = {
                "package_context_measure_id": context_id,
                "origin_lane": "large_language_population_strata",
                "origin_record_id": stratum_id,
                "package_id": package_id,
                "component_target_ids": list(package_profiles[package_id]["component_target_ids"]),
                "original_language_target_ids": target_ids,
                "measure_class": original["measure_class"],
                "population_values_persons": values,
                "source_unit": original["population_unit"],
                "population_definition": original["population_definition"],
                "reference_year": original["population_reference_year"],
                "source_ids": [_llps_source_id(source_id) for source_id in original["source_ids"]],
                "aggregation": original["additivity"],
                "target_binding": "PACKAGE_CONTEXT_NO_INHERITANCE",
                "population_rankability_status": "INSUFFICIENT_PUBLIC_EVIDENCE",
                "score": None,
                "limitations": list(original["limitations"]),
            }
            package_context_by_id[context_id] = context_record
            if context_id not in package_profiles[package_id]["context_measure_ids"]:
                package_profiles[package_id]["context_measure_ids"].append(context_id)
            output_type = "package_context_measure"
            output_id = context_id
            measure_ids: list[str] = []
        else:
            target_id = target_ids[0]
            exact_target = (
                not _is_macro_target(target_by_id[target_id])
                and target_by_id[target_id]["exactness"] == "exact"
            )
            direct_label = original["rankability"].startswith("eligible_direct_typed_measure")
            direct_label = direct_label or original["rankability"].startswith("eligible_derived_typed_measure")
            direct = (
                direct_label
                and exact_target
                and original["endpoint"] == "language_population_basis"
                and "language_not_script" not in original["rankability"]
                and "partial_global_coverage" not in original["rankability"]
                and stratum_id != "LLPS-BN-BD-L1PROXY-2022"
            )
            target_binding = (
                "DIRECT_TARGET_ONLY"
                if direct
                else (
                    "STAGE_ONLY_NO_WHOLE_LANGUAGE_INHERITANCE"
                    if original["endpoint"] != "language_population_basis"
                    else "CONTEXT_NO_INHERITANCE"
                )
            )
            evidence_id = f"llps:{stratum_id}"
            evidence.append(
                {
                    "population_evidence_id": evidence_id,
                    "origin_lane": "large_language_population_strata",
                    "origin_record_id": stratum_id,
                    "language_target_ids": target_ids,
                    "measure_class": original["measure_class"],
                    "measure_role": original["endpoint"],
                    "source_values": {**values, "unit": original["population_unit"]},
                    "person_normalization": {
                        "status": "NORMALIZED_IDENTITY_MULTIPLIER",
                        "values_persons": values,
                        "normalization_multiplier": 1,
                    },
                    "population_definition": original["population_definition"],
                    "reference_year": original["population_reference_year"],
                    "source_ids": [_llps_source_id(source_id) for source_id in original["source_ids"]],
                    "source_url": "",
                    "endpoint_type": original["endpoint"],
                    "endpoint_ids": [],
                    "stage_ids": stage_ids,
                    "stage_identity_statuses": [stage_status],
                    "event_ids": [],
                    "additivity_class": original["additivity"],
                    "overlap_group": original["overlap_group"],
                    "target_binding": target_binding,
                    "population_rankability_status": _rankability(values, direct),
                    "rank_eligibility_source_label": original["rankability"],
                    "score_eligible": False,
                    "score": None,
                    "limitations": list(original["limitations"]),
                    "audit_adjustments": audit_adjustments,
                }
            )
            output_type = "population_evidence"
            output_id = evidence_id
            measure_ids = [evidence_id]
        provenance.append(
            _provenance_record(
                input_id=stratum_id,
                origin_file="structured/large_language_population_strata_proposal.json",
                row_number=row_number,
                row_sha=row_sha,
                output_type=output_type,
                output_id=output_id,
                target_ids=target_ids,
                measure_ids=measure_ids,
                source_id=_llps_source_id(original["source_ids"][0]),
            )
        )

    # A one-component proposal package reuses its sole stratum context record.
    stratum_by_id = {row["stratum_id"]: row for row in proposal["population_strata"]}
    for profile in proposal["parallel_or_common_core_package_profiles"]:
        effective_id = _package_id_for_llps(profile["package_profile_id"])
        if len(profile["component_stratum_ids"]) == 1:
            context_id = f"llps:{profile['component_stratum_ids'][0]}"
            if context_id in package_context_by_id and context_id not in package_profiles[effective_id]["context_measure_ids"]:
                package_profiles[effective_id]["context_measure_ids"].append(context_id)
    return evidence, list(package_context_by_id.values()), quarantine, provenance, sources


def _assert_exact_header(actual: Sequence[str], expected: Sequence[str], label: str) -> None:
    if list(actual) != list(expected):
        raise BuildError(f"{label} header differs from its closed schema")


def _assert_clean_csv_row(row: Mapping[str, str], *, label: str) -> None:
    forbidden_nulls = {"na", "n/a", "nan", "null", "none", "infinity", "+infinity", "-infinity"}
    for field, value in row.items():
        if value is None:
            raise BuildError(f"{label}.{field} is an absent CSV field rather than the empty-string null")
        if value != value.strip():
            raise BuildError(f"{label}.{field} contains leading or trailing whitespace")
        if value.casefold() in forbidden_nulls and not (field == "bound_semantics" and value == "NONE"):
            raise BuildError(f"{label}.{field} uses a forbidden pseudo-null token: {value!r}")


def _assert_target_identity(target: Mapping[str, Any], row: Mapping[str, str]) -> None:
    target_id = row["target_id"]
    scalar = {
        "language_mode": "language_mode",
        "exactness": "exactness",
    }
    arrays = {
        "target_name": "language_variety_names",
        "language_tag": "language_tags",
        "script_orthography": "scripts_orthographies",
        "territory": "territories_communities",
    }
    for input_field, target_field in scalar.items():
        supplied = row[input_field]
        if supplied and supplied != target[target_field]:
            raise BuildError(
                f"regional row asserts incompatible {input_field} for existing target {target_id}: "
                f"{supplied!r} != {target[target_field]!r}"
            )
    for input_field, target_field in arrays.items():
        supplied = row[input_field]
        if supplied and supplied not in target[target_field]:
            raise BuildError(
                f"regional row asserts unknown {input_field} for existing target {target_id}: {supplied!r}"
            )


def _new_target_from_regional(row: Mapping[str, str], origin_file: str) -> dict[str, Any]:
    required = (
        "target_id",
        "target_name",
        "language_tag",
        "script_orthography",
        "territory",
        "language_mode",
        "exactness",
    )
    missing = [field for field in required if not row[field]]
    if missing:
        raise BuildError(f"new target {row['target_id']} lacks identity fields: {missing}")
    return {
        "language_target_id": row["target_id"],
        "universe_membership": True,
        "language_tags": [row["language_tag"]],
        "language_variety_names": [row["target_name"]],
        "scripts_orthographies": [row["script_orthography"]],
        "territories_communities": [row["territory"]],
        "language_mode": row["language_mode"],
        "exactness": row["exactness"],
        "source_candidate_ids": [row["import_row_id"]],
        "source_origin_files": [origin_file],
        "population_measure_ids": [],
        "rankable_population_basis": False,
        "unranked_reasons": ["no_complete_need_access_score_inputs"],
    }


def _regional_evidence_record(
    row: Mapping[str, str],
    *,
    target: Mapping[str, Any],
    origin_file: str,
    row_number: int,
    row_sha: str,
) -> dict[str, Any]:
    raw = {
        "low": _number(row["source_low"], label=f"{row['import_row_id']}.source_low"),
        "base": _number(row["source_base"], label=f"{row['import_row_id']}.source_base"),
        "high": _number(row["source_high"], label=f"{row['import_row_id']}.source_high"),
    }
    source_values = _bound_values(raw["low"], raw["base"], raw["high"], row["bound_semantics"], 1)
    multiplier = _number(
        row["normalization_multiplier"], label=f"{row['import_row_id']}.normalization_multiplier"
    )
    if row["source_unit"] == "persons":
        normalized_values = _bound_values(
            raw["low"], raw["base"], raw["high"], row["bound_semantics"], multiplier
        )
        normalization_status = "NORMALIZED_TO_PERSONS"
    else:
        normalized_values = {"low": None, "base": None, "high": None}
        normalization_status = "NONPERSON_CONTEXT_NOT_NORMALIZED"
        if multiplier is not None:
            raise BuildError(f"{row['import_row_id']} supplies a multiplier for a non-person unit")

    direct = row["disposition"] == "ADMIT_DIRECT"
    if direct:
        if row["source_unit"] != "persons" or multiplier != 1:
            raise BuildError(f"{row['import_row_id']} direct evidence is not identity-normalized persons")
        if row["bound_semantics"] not in {"POINT", "INTERVAL"}:
            raise BuildError(f"{row['import_row_id']} direct evidence lacks point/interval semantics")
        if (
            target.get("exactness") != "exact"
            or _is_macro_target(target)
            or target["language_target_id"] in SUPERSEDED_TARGETS
        ):
            raise BuildError(
                f"{row['import_row_id']} attempts direct evidence for a macro, unresolved, or superseded target"
            )
    stage_ids = _split_semicolon(row["stage_ids"])
    if any(stage not in {f"E{index}" for index in range(7)} for stage in stage_ids):
        raise BuildError(f"{row['import_row_id']} uses an unregistered stage")
    evidence_id = row["measure_id"]
    return {
        "population_evidence_id": evidence_id,
        "origin_lane": "regional_schema_driven_import",
        "origin_record_id": row["import_row_id"],
        "origin_file": origin_file,
        "origin_row_number": row_number,
        "origin_row_sha256": row_sha,
        "language_target_ids": [row["target_id"]],
        "measure_class": row["measure_class"],
        "measure_role": row["endpoint_type"],
        "source_values": {**source_values, "unit": row["source_unit"]},
        "person_normalization": {
            "status": normalization_status,
            "values_persons": normalized_values,
            "normalization_multiplier": multiplier,
        },
        "population_definition": row["population_definition"],
        "reference_year": row["reference_year"],
        "source_ids": [row["evidence_source_id"]],
        "source_url": row["evidence_url"],
        "endpoint_type": row["endpoint_type"],
        "endpoint_ids": [],
        "stage_ids": stage_ids,
        "stage_identity_statuses": [row["stage_identity_status"]],
        "event_ids": [],
        "additivity_class": row["additivity_class"],
        "overlap_group": row["overlap_group"],
        "target_binding": "DIRECT_TARGET_ONLY" if direct else "CONTEXT_NO_INHERITANCE",
        "population_rankability_status": _rankability(normalized_values, direct),
        "rank_eligibility_source_label": row["disposition"],
        "score_eligible": False,
        "score": None,
        "evidence_class": row["evidence_class"],
        "authority_path": row["authority_path"],
        "authority_locator": row["authority_locator"],
        "notes": row["notes"],
    }


def adapt_regional_csvs(
    base: Path,
    manifest: Mapping[str, Any],
    contract: Mapping[str, Any],
    language_targets: list[dict[str, Any]],
    package_profiles: dict[str, dict[str, Any]],
    occupied_measure_ids: set[str],
    occupied_import_ids: set[str],
) -> tuple[
    list[dict[str, Any]],
    list[dict[str, Any]],
    list[dict[str, Any]],
    list[dict[str, Any]],
    list[dict[str, Any]],
    list[dict[str, Any]],
]:
    expected_header = contract["csv"]["header"]
    enums = contract["enums"]
    target_by_id = {row["language_target_id"]: row for row in language_targets}
    evidence: list[dict[str, Any]] = []
    quarantine: list[dict[str, Any]] = []
    provenance: list[dict[str, Any]] = []
    sources_by_id: dict[str, dict[str, Any]] = {}
    batch_identities: list[dict[str, Any]] = []
    new_targets: list[dict[str, Any]] = []
    seen_rows: set[str] = set()

    for spec in manifest["regional_csv_imports"]:
        if spec.get("adapter") != "closed_regional_csv_v2":
            raise BuildError(f"unsupported regional adapter: {spec.get('adapter')!r}")
        path = exact_relative(base, spec["path"])
        actual_identity = {"path": spec["path"], "bytes": path.stat().st_size, "sha256": sha256_file(path)}
        if actual_identity["bytes"] != spec["bytes"] or actual_identity["sha256"] != spec["sha256"]:
            raise BuildError(f"regional batch identity mismatch: {spec['path']}")
        batch_identities.append(actual_identity)
        header, rows = read_csv(path)
        _assert_exact_header(header, expected_header, spec["path"])
        for row_number, row in enumerate(rows, 2):
            row_id = row["import_row_id"]
            if not row_id:
                raise BuildError(f"{spec['path']} row {row_number} has no import_row_id")
            if row_id in seen_rows or row_id in occupied_import_ids:
                raise BuildError(f"duplicate regional import_row_id: {row_id}")
            seen_rows.add(row_id)
            occupied_import_ids.add(row_id)
            _assert_clean_csv_row(row, label=row_id)
            for field in ("record_kind", "bound_semantics", "disposition"):
                if row[field] not in enums[field]:
                    raise BuildError(f"{row_id}.{field} is outside the import ontology")
            if row["language_mode"] and row["language_mode"] not in enums["language_mode"]:
                raise BuildError(f"{row_id}.language_mode is outside the import ontology")
            if row["exactness"] and row["exactness"] not in enums["exactness"]:
                raise BuildError(f"{row_id}.exactness is outside the import ontology")
            row_sha = _row_sha(row)

            source_id = row["evidence_source_id"]
            if not source_id:
                raise BuildError(f"{row_id} has no evidence_source_id")
            if source_id not in sources_by_id:
                source_record = _source_record(
                    source_id,
                    origin_file=spec["path"],
                    title=f"Audited successor input: {row['authority_locator']}",
                    url=row["evidence_url"],
                    claim_scope=row["evidence_class"],
                    row_number=row_number,
                    row_sha256=row_sha,
                )
                source_record["authority_paths"] = [row["authority_path"]]
                source_record["authority_locators"] = [row["authority_locator"]]
                source_record["assertion_row_ids"] = [row_id]
                source_record["assertion_row_sha256"] = [row_sha]
                sources_by_id[source_id] = source_record
            else:
                source_record = sources_by_id[source_id]
                for field, value in (
                    ("authority_paths", row["authority_path"]),
                    ("authority_locators", row["authority_locator"]),
                    ("assertion_row_ids", row_id),
                    ("assertion_row_sha256", row_sha),
                ):
                    if value not in source_record[field]:
                        source_record[field].append(value)

            if row["record_kind"] == "PACKAGE_PROFILE":
                forbidden = (
                    "target_id", "measure_id", "source_low", "source_base", "source_high",
                    "normalization_multiplier",
                )
                if any(row[field] for field in forbidden):
                    raise BuildError(f"{row_id} package profile carries target or measure values")
                package_id = row["package_id"]
                components = _split_semicolon(row["component_target_ids"])
                if not package_id or not components or len(components) != len(set(components)):
                    raise BuildError(f"{row_id} package profile has an invalid component list")
                unknown = [target_id for target_id in components if target_id not in target_by_id]
                if unknown:
                    raise BuildError(f"{row_id} package references unknown targets: {unknown}")
                profile = {
                    "package_id": package_id,
                    "label": row["notes"] or package_id,
                    "component_target_ids": components,
                    "context_measure_ids": [],
                    "measure_inheritance_policy": "NONE",
                    "population_measure_ids": [],
                    "rankability_status": "INSUFFICIENT_PUBLIC_EVIDENCE",
                    "score": None,
                    "source_package_profile_ids": [row_id],
                    "source_ids": [source_id],
                    "authority_path": row["authority_path"],
                }
                if package_id in package_profiles:
                    if package_profiles[package_id]["component_target_ids"] != components:
                        raise BuildError(f"package identity collision: {package_id}")
                else:
                    package_profiles[package_id] = profile
                output_type, output_id, target_ids, measure_ids = (
                    "package_profile", package_id, components, []
                )
            else:
                target_id = row["target_id"]
                if not target_id:
                    raise BuildError(f"{row_id} language evidence has no target_id")
                if target_id in target_by_id:
                    _assert_target_identity(target_by_id[target_id], row)
                    target = target_by_id[target_id]
                else:
                    target = _new_target_from_regional(row, spec["path"])
                    language_targets.append(target)
                    new_targets.append(target)
                    target_by_id[target_id] = target
                if row_id not in target["source_candidate_ids"] and target in new_targets:
                    target["source_candidate_ids"].append(row_id)
                if spec["path"] not in target["source_origin_files"] and target in new_targets:
                    target["source_origin_files"].append(spec["path"])

                disposition = row["disposition"]
                if disposition == "INCLUSION_ONLY":
                    if row["measure_id"] or any(row[field] for field in ("source_low", "source_base", "source_high")):
                        raise BuildError(f"{row_id} inclusion-only row carries measure data")
                    output_type, output_id, target_ids, measure_ids = (
                        "language_target_assertion", target_id, [target_id], []
                    )
                elif disposition == "QUARANTINE":
                    if not row["quarantine_reason"]:
                        raise BuildError(f"{row_id} quarantine row lacks a reason")
                    quarantine_id = f"quarantine:regional:{row_id.lower()}"
                    quarantine.append(
                        {
                            "quarantine_id": quarantine_id,
                            "origin_lane": "regional_schema_driven_import",
                            "origin_record_id": row_id,
                            "reason_codes": ["REGIONAL_IMPORT_QUARANTINE"],
                            "reason": row["quarantine_reason"],
                            "replacement_ids": [],
                            "original_payload": deepcopy(row),
                        }
                    )
                    output_type, output_id, target_ids, measure_ids = (
                        "quarantine", quarantine_id, [target_id], []
                    )
                else:
                    measure_id = row["measure_id"]
                    if not measure_id or measure_id in occupied_measure_ids:
                        raise BuildError(f"{row_id} has a missing or duplicate measure_id: {measure_id!r}")
                    occupied_measure_ids.add(measure_id)
                    record = _regional_evidence_record(
                        row,
                        target=target,
                        origin_file=spec["path"],
                        row_number=row_number,
                        row_sha=row_sha,
                    )
                    evidence.append(record)
                    if record["target_binding"] == "DIRECT_TARGET_ONLY" and target in new_targets:
                        target["population_measure_ids"].append(measure_id)
                        target["rankable_population_basis"] = True
                    output_type, output_id, target_ids, measure_ids = (
                        "population_evidence", measure_id, [target_id], [measure_id]
                    )
            provenance.append(
                _provenance_record(
                    input_id=row_id,
                    origin_file=spec["path"],
                    row_number=row_number,
                    row_sha=row_sha,
                    output_type=output_type,
                    output_id=output_id,
                    target_ids=target_ids,
                    measure_ids=measure_ids,
                    source_id=source_id,
                )
            )
    return evidence, quarantine, provenance, list(sources_by_id.values()), batch_identities, new_targets


SIGNED_HEADER = [
    "record_id", "domain", "intervention_or_language", "jurisdiction", "reference_year",
    "evidence_role", "measure_label", "value", "value_qualifier", "unit", "numerator",
    "denominator", "denominator_unit", "reported_rate_percent", "rate_basis",
    "population_universe", "age_scope", "measure_definition", "directness",
    "language_specificity", "valid_sign_language_user_count", "source_tier",
    "source_publisher", "source_title", "publication_date", "source_url", "source_locator",
    "additivity_class", "overlap_group", "population_evidence_key", "double_count_rule",
    "applicable_interventions", "recommended_use", "status", "limitations",
]


def _signed_common_record(row: Mapping[str, str], row_number: int, row_sha: str) -> dict[str, Any]:
    value = _number(row["value"], label=f"{row['record_id']}.value")
    numerator = _number(row["numerator"], label=f"{row['record_id']}.numerator")
    denominator = _number(row["denominator"], label=f"{row['record_id']}.denominator")
    rate = _number(row["reported_rate_percent"], label=f"{row['record_id']}.reported_rate_percent")
    unit = row["unit"]
    if unit == "persons":
        person_values = {"low": None, "base": value, "high": None}
        normalization_status = "PERSON_MEASURE_PRESERVED"
    elif unit == "students":
        person_values = {"low": None, "base": value, "high": None}
        normalization_status = "LEARNER_STOCK_PERSONS_PRESERVED_AS_OVERLAY_ONLY"
    else:
        person_values = {"low": None, "base": None, "high": None}
        normalization_status = "NONPERSON_UNIT_NOT_NORMALIZED"
    return {
        "record_id": row["record_id"],
        "origin_file": "structured/SIGNED_ACCESSIBILITY_EMPIRICAL_INPUTS.csv",
        "origin_row_number": row_number,
        "origin_row_sha256": row_sha,
        "domain": row["domain"],
        "evidence_role": row["evidence_role"],
        "intervention_or_language": row["intervention_or_language"],
        "jurisdiction": row["jurisdiction"],
        "reference_year": row["reference_year"],
        "measure_label": row["measure_label"],
        "source_values": {
            "value": value,
            "qualifier": row["value_qualifier"],
            "unit": unit,
            "numerator": numerator,
            "denominator": denominator,
            "denominator_unit": row["denominator_unit"],
            "reported_rate_percent": rate,
            "rate_basis": row["rate_basis"],
        },
        "person_normalization": {
            "status": normalization_status,
            "values_persons": person_values,
            "normalization_multiplier": 1 if unit in {"persons", "students"} and value is not None else None,
        },
        "population_universe": row["population_universe"],
        "age_scope": row["age_scope"],
        "measure_definition": row["measure_definition"],
        "directness": row["directness"],
        "language_specificity": row["language_specificity"],
        "source_tier": row["source_tier"],
        "source_id": f"source:signed:{row['record_id'].lower()}",
        "source_url": row["source_url"],
        "additivity_class": row["additivity_class"],
        "overlap_group": row["overlap_group"],
        "double_count_rule": row["double_count_rule"],
        "applicable_interventions": _split_semicolon(row["applicable_interventions"]),
        "recommended_use": row["recommended_use"],
        "status": row["status"],
        "limitations": row["limitations"],
        "score_eligible": False,
        "score": None,
    }


def adapt_signed_accessibility(
    base: Path,
    spec: Mapping[str, Any],
    target_by_id: Mapping[str, Mapping[str, Any]],
    new_target_ids: set[str],
    occupied_measure_ids: set[str],
    occupied_import_ids: set[str],
) -> tuple[dict[str, list[dict[str, Any]]], list[dict[str, Any]], list[dict[str, Any]], dict[str, Any]]:
    if spec.get("adapter") != "signed_accessibility_register_v1":
        raise BuildError("signed/accessibility register has the wrong adapter")
    path = exact_relative(base, spec["path"])
    if path.stat().st_size != spec["bytes"] or sha256_file(path) != spec["sha256"]:
        raise BuildError("signed/accessibility register identity mismatch")
    validation_path = exact_relative(base, spec["validation_path"])
    if sha256_file(validation_path) != "ef0403cb6a19ed679e3d0f4df489e0d848dadcdd2b8f513923f896ce2a6ff54a":
        raise BuildError("signed/accessibility validation identity mismatch")
    validation = read_json(validation_path)
    if validation.get("passed") is not True or validation.get("row_count") != 35:
        raise BuildError("signed/accessibility validation did not pass")
    if validation["content_hashes"]["SIGNED_ACCESSIBILITY_EMPIRICAL_INPUTS.csv"] != spec["sha256"]:
        raise BuildError("signed validation does not bind the imported CSV")
    header, rows = read_csv(path)
    _assert_exact_header(header, SIGNED_HEADER, spec["path"])
    if len(rows) != validation["row_count"]:
        raise BuildError("signed/accessibility row count differs from validation")

    lanes: dict[str, list[dict[str, Any]]] = {
        "signed_language_person_measures": [],
        "signed_language_proxy_and_gap_rows": [],
        "accessibility_overlays": [],
        "accessibility_supply_policy_and_utilization": [],
    }
    provenance: list[dict[str, Any]] = []
    sources: list[dict[str, Any]] = []
    seen: set[str] = set()
    for row_number, row in enumerate(rows, 2):
        record_id = row["record_id"]
        if not record_id or record_id in seen or record_id in occupied_import_ids:
            raise BuildError(f"duplicate signed/accessibility record_id: {record_id!r}")
        seen.add(record_id)
        occupied_import_ids.add(record_id)
        _assert_clean_csv_row(row, label=record_id)
        row_sha = _row_sha(row)
        record = _signed_common_record(row, row_number, row_sha)
        target_id = SIGNED_TARGET_MAP.get(record_id)
        record["language_target_id"] = target_id
        if target_id is not None and target_id not in target_by_id:
            raise BuildError(f"signed/accessibility mapping references unknown target: {record_id} -> {target_id}")

        if row["domain"] == "signed_language" and row["evidence_role"] == "language_user_measure":
            lane = "signed_language_person_measures"
            if row["unit"] != "persons" or record["source_values"]["value"] is None:
                raise BuildError(f"{record_id} language-user measure is not a numeric person measure")
            direct = row["valid_sign_language_user_count"] == "yes" and target_id is not None
            measure_id = f"signed:{record_id.lower()}"
            if measure_id in occupied_measure_ids:
                raise BuildError(f"duplicate signed person measure: {measure_id}")
            occupied_measure_ids.add(measure_id)
            record["population_evidence_id"] = measure_id
            record["target_binding"] = "DIRECT_TARGET_ONLY" if direct else "QUALIFIED_CONTEXT_NO_INHERITANCE"
            record["population_rankability_status"] = (
                "POINT_DISTRIBUTION" if direct else "INSUFFICIENT_PUBLIC_EVIDENCE"
            )
            record["valid_sign_language_user_count"] = row["valid_sign_language_user_count"]
            measure_ids = [measure_id]
            if direct and target_id in new_target_ids:
                target = target_by_id[target_id]
                target["population_measure_ids"].append(measure_id)
                target["rankable_population_basis"] = True
            output_type, output_id = "signed_language_person_measure", measure_id
        elif row["domain"] == "signed_language":
            lane = "signed_language_proxy_and_gap_rows"
            record["target_binding"] = "PROXY_OR_GAP_NO_INHERITANCE"
            record["population_rankability_status"] = "INSUFFICIENT_PUBLIC_EVIDENCE"
            measure_ids = []
            output_type, output_id = "signed_language_proxy_or_gap", record_id
        elif row["domain"] == "accessibility_overlay":
            lane = "accessibility_overlays"
            record["target_binding"] = "ACCESSIBILITY_OVERLAY_NONADDITIVE"
            record["population_rankability_status"] = "INSUFFICIENT_PUBLIC_EVIDENCE"
            measure_ids = []
            output_type, output_id = "accessibility_overlay_evidence", record_id
        else:
            lane = "accessibility_supply_policy_and_utilization"
            record["target_binding"] = "SUPPLY_POLICY_UTILIZATION_NONADDITIVE"
            record["population_rankability_status"] = "INSUFFICIENT_PUBLIC_EVIDENCE"
            measure_ids = []
            output_type, output_id = "accessibility_supply_policy_or_utilization", record_id
        lanes[lane].append(record)
        sources.append(
            _source_record(
                record["source_id"],
                origin_file=spec["path"],
                title=row["source_title"],
                organization=row["source_publisher"],
                year=row["publication_date"][:4] if row["publication_date"] else "n.d.",
                url=row["source_url"],
                claim_scope=row["source_locator"],
                row_number=row_number,
                row_sha256=row_sha,
            )
        )
        provenance.append(
            _provenance_record(
                input_id=record_id,
                origin_file=spec["path"],
                row_number=row_number,
                row_sha=row_sha,
                output_type=output_type,
                output_id=output_id,
                target_ids=[target_id] if target_id else [],
                measure_ids=measure_ids,
                source_id=record["source_id"],
            )
        )

    partition = {key: len(value) for key, value in lanes.items()}
    expected_partition = {
        "signed_language_person_measures": 12,
        "signed_language_proxy_and_gap_rows": 5,
        "accessibility_overlays": 10,
        "accessibility_supply_policy_and_utilization": 8,
    }
    if partition != expected_partition:
        raise BuildError(f"signed/accessibility lane partition changed: {partition}")
    valid_direct = sum(
        row["valid_sign_language_user_count"] == "yes"
        for row in lanes["signed_language_person_measures"]
    )
    qualified = sum(
        row["valid_sign_language_user_count"] == "qualified"
        for row in lanes["signed_language_person_measures"]
    )
    if (valid_direct, qualified) != (10, 2):
        raise BuildError("signed person-measure validity partition changed")
    identity = {
        "path": spec["path"],
        "bytes": path.stat().st_size,
        "sha256": sha256_file(path),
        "validation_path": spec["validation_path"],
        "validation_bytes": validation_path.stat().st_size,
        "validation_sha256": sha256_file(validation_path),
        "validation_passed": True,
        "lane_counts": partition,
        "valid_direct_person_measures": valid_direct,
        "qualified_person_measures": qualified,
        "nonadditive": True,
    }
    return lanes, provenance, sources, identity


def _manifest_artifact(manifest: Mapping[str, Any], relative: str) -> Mapping[str, Any]:
    matches = [row for row in manifest["artifacts"] if row["path"] == relative]
    if len(matches) != 1:
        raise BuildError(f"OER manifest does not identify exactly one {relative}")
    return matches[0]


def adapt_oer_gap_lane(
    base: Path,
    spec: Mapping[str, Any],
    canonical_target_ids: set[str],
) -> dict[str, Any]:
    if spec.get("adapter") != "oer_route_status_manifest_v2":
        raise BuildError("OER gap input has the wrong adapter")
    manifest_path = exact_relative(base, spec["path"])
    if manifest_path.stat().st_size != spec["bytes"] or sha256_file(manifest_path) != spec["sha256"]:
        raise BuildError("OER canonical manifest identity mismatch")
    validation_path = exact_relative(base, spec["validation_path"])
    if sha256_file(validation_path) != "5aa0e91e60a218dbf03b0b2fc5859209620d08845792d74bf3e5f6c601452669":
        raise BuildError("OER validation identity mismatch")
    manifest = read_json(manifest_path)
    validation = read_json(validation_path)
    if manifest.get("schema") != "interlanguage/oer-gap-canonical-manifest/2.0.0":
        raise BuildError("unsupported OER canonical manifest")
    validation_artifact = _manifest_artifact(manifest, spec["validation_path"])
    if (
        validation_artifact["bytes"] != validation_path.stat().st_size
        or validation_artifact["sha256"] != sha256_file(validation_path)
    ):
        raise BuildError("OER manifest does not bind the imported validation receipt")
    if validation.get("schema") != "interlanguage/oer-gap-expansion-validation/2.0.0":
        raise BuildError("unsupported OER validation schema")
    if validation.get("validation_passed") is not True or validation.get("failures"):
        raise BuildError("OER validation did not pass")
    required_invariants = {
        "all_access_sources_are_independent_external",
        "functional_access_is_independent_of_open_adaptation",
        "no_rankings_produced",
        "no_resource_gap_scalar_imputed",
        "repository_counts_are_not_curriculum_coverage",
        "unresolved_is_missing_not_high_scarcity",
        "user_and_programme_outputs_excluded",
    }
    if set(validation.get("invariants", {})) != required_invariants or not all(
        validation["invariants"].values()
    ):
        raise BuildError("OER validation invariants are incomplete or failed")

    requested = {
        "matrix": "structured/oer_target_canon_evidence_matrix.csv",
        "queries": "structured/oer_gap_query_manifest.csv",
        "derivation": "structured/oer_resource_gap_derivation_inputs.csv",
    }
    expected_headers = {
        "matrix": [
            "matrix_row_id", "target_id", "language_tag", "language_names_json",
            "script_orthography_json", "territories_json", "isced_stage", "stage_label",
            "subject_domain", "subject_label", "canon_id", "canon_version", "canon_atom_id",
            "baseline_access_endpoint_id", "resource_route_id", "finding_status",
            "functional_access_grade", "open_adaptation_grade",
            "exact_language_variety_script_status", "free_access_status", "open_license_status",
            "adaptation_permission_status", "redistribution_permission_status", "completeness_status",
            "exercises_status", "answers_status", "download_status", "offline_status",
            "accessibility_status", "self_study_usability_status", "alignment_status",
            "technical_integrity_status", "coverage_credit_status", "evidence_grade",
            "source_ids_json", "query_ids_json", "repository_count_used_as_coverage",
            "unresolved_source_flag", "independent_origin_status", "program_exclusion_status",
            "baseline_policy_version", "baseline_observation_date", "caveat", "input_row_hash",
        ],
        "queries": [
            "query_id", "matrix_row_id", "target_id", "canon_atom_id", "catalog_id",
            "query_method", "query_url", "query_terms_json", "queried_at_utc", "http_status",
            "query_status", "catalogue_hit_count", "language_match_status", "script_match_status",
            "territory_match_status", "stage_match_status", "subject_match_status",
            "curriculum_coverage_credit_allowed", "source_ids_json", "caveat", "query_row_hash",
        ],
        "derivation": [
            "derivation_row_id", "matrix_row_id", "target_id", "canon_atom_id",
            "baseline_functional_route_id", "baseline_access_endpoint_id", "finding_status",
            "resource_gap_low", "resource_gap_base", "resource_gap_high", "derivation_status",
            "unresolved_source_flag", "source_ids_json", "evidence_matrix_row_hash",
            "baseline_policy_version", "baseline_observation_date", "program_exclusion_registry_hash",
            "program_exclusion_status", "derivation_row_hash",
        ],
    }
    identities: dict[str, Any] = {}
    loaded: dict[str, list[dict[str, str]]] = {}
    for label, relative in requested.items():
        artifact = _manifest_artifact(manifest, relative)
        path = exact_relative(base, relative)
        actual = {"path": relative, "bytes": path.stat().st_size, "sha256": sha256_file(path)}
        if actual["bytes"] != artifact["bytes"] or actual["sha256"] != artifact["sha256"]:
            raise BuildError(f"OER artifact identity mismatch: {relative}")
        header, rows = read_csv(path)
        if header != expected_headers[label]:
            raise BuildError(f"OER artifact header mismatch: {relative}")
        if len(rows) != artifact["row_count"]:
            raise BuildError(f"OER row count mismatch: {relative}")
        loaded[label] = rows
        identities[relative] = {**actual, "row_count": len(rows)}

    matrix_rows = loaded["matrix"]
    query_rows = loaded["queries"]
    derivation_rows = loaded["derivation"]
    for row in matrix_rows:
        if _row_sha(row, omit="input_row_hash") != row["input_row_hash"]:
            raise BuildError(f"OER matrix row hash mismatch: {row['matrix_row_id']}")
    for row in query_rows:
        if _row_sha(row, omit="query_row_hash") != row["query_row_hash"]:
            raise BuildError(f"OER query row hash mismatch: {row['query_id']}")
    for row in derivation_rows:
        if _row_sha(row, omit="derivation_row_hash") != row["derivation_row_hash"]:
            raise BuildError(f"OER derivation row hash mismatch: {row['derivation_row_id']}")

    matrix_by_id = {row["matrix_row_id"]: row for row in matrix_rows}
    if len(matrix_by_id) != len(matrix_rows):
        raise BuildError("duplicate OER matrix_row_id")
    natural = {(row["target_id"], row["canon_atom_id"]) for row in matrix_rows}
    if len(natural) != len(matrix_rows):
        raise BuildError("duplicate OER target/canon cell")
    target_ids = {row["target_id"] for row in matrix_rows}
    if not target_ids <= canonical_target_ids:
        raise BuildError("OER lane contains a target outside the preserved legacy universe")
    stage_ids = {row["isced_stage"] for row in matrix_rows}
    subject_ids = {row["subject_domain"] for row in matrix_rows}
    expected_stage_ids = {f"E{index}" for index in range(7)}
    expected_subject_ids = {
        "COMPUTING_DIGITAL",
        "LANGUAGE_LITERACY",
        "MATHEMATICS_DATA",
        "SCIENCE_HEALTH",
        "SOCIAL_CIVIC",
    }
    canon_cells = {(row["isced_stage"], row["subject_domain"]) for row in matrix_rows}
    if stage_ids != expected_stage_ids or subject_ids != expected_subject_ids or len(canon_cells) != 35:
        raise BuildError("OER matrix is not the declared 7-stage by 5-subject canon")
    cells_by_target: dict[str, set[tuple[str, str]]] = defaultdict(set)
    for row in matrix_rows:
        cells_by_target[row["target_id"]].add((row["isced_stage"], row["subject_domain"]))
        if row["canon_id"] != "CANON-OER-CORE" or row["canon_version"] != "1.0.0":
            raise BuildError(f"OER row has an unexpected canon identity: {row['matrix_row_id']}")
        expected_atom_id = f"CANON-OER-CORE-v1:{row['isced_stage']}:{row['subject_domain']}"
        expected_endpoint_id = (
            f"endpoint:public-current-access:{row['target_id']}:{row['isced_stage']}:"
            f"{row['subject_domain']}:{row['baseline_observation_date']}"
        )
        if row["canon_atom_id"] != expected_atom_id or row["baseline_access_endpoint_id"] != expected_endpoint_id:
            raise BuildError(f"OER row has a noncanonical atom or endpoint identity: {row['matrix_row_id']}")
        if row["baseline_policy_version"] != "counterfactual-independent-public-resources-v1":
            raise BuildError(f"OER row has an unexpected baseline policy: {row['matrix_row_id']}")
        if row["program_exclusion_status"] != "PASS_NO_PROGRAM_OUTPUT_ADMITTED":
            raise BuildError(f"OER row admits programme/user output: {row['matrix_row_id']}")
        source_ids = json.loads(row["source_ids_json"])
        if not isinstance(source_ids, list) or len(source_ids) != len(set(source_ids)):
            raise BuildError(f"OER matrix source list is malformed: {row['matrix_row_id']}")
    if set(cells_by_target) != target_ids or any(
        cells != canon_cells for cells in cells_by_target.values()
    ):
        raise BuildError("OER targets do not each have all 35 canon cells")
    query_ids: set[str] = set()
    queries_by_matrix: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in query_rows:
        if row["query_id"] in query_ids:
            raise BuildError(f"duplicate OER query_id: {row['query_id']}")
        query_ids.add(row["query_id"])
        if row["matrix_row_id"] not in matrix_by_id:
            raise BuildError(f"orphan OER query row: {row['query_id']}")
        matrix = matrix_by_id[row["matrix_row_id"]]
        if row["target_id"] != matrix["target_id"] or row["canon_atom_id"] != matrix["canon_atom_id"]:
            raise BuildError(f"OER query does not bind its target/canon cell: {row['query_id']}")
        if row["curriculum_coverage_credit_allowed"] != "0":
            raise BuildError("OER query attempted to credit catalogue/repository hits as curriculum coverage")
        query_sources = json.loads(row["source_ids_json"])
        if not isinstance(query_sources, list) or len(query_sources) != len(set(query_sources)):
            raise BuildError(f"OER query source list is malformed: {row['query_id']}")
        queries_by_matrix[row["matrix_row_id"]].append(row)
    derivation_by_matrix: dict[str, dict[str, str]] = {}
    derivation_ids: set[str] = set()
    for row in derivation_rows:
        matrix_id = row["matrix_row_id"]
        if row["derivation_row_id"] in derivation_ids:
            raise BuildError(f"duplicate OER derivation_row_id: {row['derivation_row_id']}")
        derivation_ids.add(row["derivation_row_id"])
        if matrix_id not in matrix_by_id or matrix_id in derivation_by_matrix:
            raise BuildError(f"orphan or duplicate OER derivation: {row['derivation_row_id']}")
        if any(row[field] for field in ("resource_gap_low", "resource_gap_base", "resource_gap_high")):
            raise BuildError("OER derivation contains a numeric resource-gap scalar")
        if row["evidence_matrix_row_hash"] != matrix_by_id[matrix_id]["input_row_hash"]:
            raise BuildError(f"OER derivation does not bind matrix hash: {row['derivation_row_id']}")
        matrix = matrix_by_id[matrix_id]
        join_fields = (
            "target_id",
            "canon_atom_id",
            "baseline_access_endpoint_id",
            "finding_status",
            "unresolved_source_flag",
            "source_ids_json",
            "baseline_policy_version",
            "baseline_observation_date",
            "program_exclusion_status",
        )
        if any(row[field] != matrix[field] for field in join_fields):
            raise BuildError(f"OER derivation/matrix semantic mismatch: {row['derivation_row_id']}")
        if row["baseline_functional_route_id"] != matrix["resource_route_id"]:
            raise BuildError(f"OER derivation/matrix route mismatch: {row['derivation_row_id']}")
        if row["derivation_status"] != "NOT_DERIVABLE_NO_IDENTIFIED_DENOMINATOR_OR_FRACTIONAL_COVERAGE_MODEL":
            raise BuildError(f"OER derivation claims an unsupported scalar route: {row['derivation_row_id']}")
        derivation_by_matrix[matrix_id] = row
    if set(derivation_by_matrix) != set(matrix_by_id):
        raise BuildError("OER derivation coverage is incomplete")

    route_statuses: list[dict[str, Any]] = []
    for row in matrix_rows:
        matrix_id = row["matrix_row_id"]
        queries = queries_by_matrix[matrix_id]
        declared_query_ids = json.loads(row["query_ids_json"])
        if (
            not isinstance(declared_query_ids, list)
            or len(declared_query_ids) != 5
            or len(set(declared_query_ids)) != 5
            or len(queries) != 5
            or set(declared_query_ids) != {query["query_id"] for query in queries}
            or {query["catalog_id"] for query in queries}
            != {"AFRICAN_STORYBOOK", "GDL_API", "OFFICIAL_NATIVE", "PRESSBOOKS_DIRECTORY", "STORYWEAVER"}
            or declared_query_ids != sorted(declared_query_ids)
        ):
            raise BuildError(f"OER cell does not bind exactly five declared queries: {matrix_id}")
        if row["repository_count_used_as_coverage"] != "0":
            raise BuildError(f"OER matrix row credits a repository count: {matrix_id}")
        derivation = derivation_by_matrix[matrix_id]
        if derivation["target_id"] != row["target_id"] or derivation["canon_atom_id"] != row["canon_atom_id"]:
            raise BuildError(f"OER derivation join mismatch: {matrix_id}")
        if row["finding_status"] == "RESOURCE_FOUND":
            if (
                not row["resource_route_id"]
                or row["unresolved_source_flag"] != "0"
                or row["functional_access_grade"] != "F4"
                or row["independent_origin_status"] != "VERIFIED_INDEPENDENT_EXTERNAL"
                or row["open_adaptation_grade"] != "O1"
                or row["coverage_credit_status"] != "FUNCTIONAL_ROUTE_FOUND_OPEN_CAPABILITY_FAILS"
            ):
                raise BuildError(f"OER resource-found row lacks an exact functional route: {matrix_id}")
        elif row["finding_status"] == "SEARCH_UNRESOLVED":
            if row["resource_route_id"] or row["unresolved_source_flag"] != "1":
                raise BuildError(f"OER unresolved row improperly carries a route: {matrix_id}")
            unresolved_state = (
                row["functional_access_grade"],
                row["open_adaptation_grade"],
                row["coverage_credit_status"],
            )
            if unresolved_state not in {
                ("F0", "O0", "UNRESOLVED_NO_EXACT_CELL_ROUTE"),
                ("F1", "O0", "PLATFORM_OR_TARGET_TIER_NO_CELL_CREDIT"),
                ("F1", "O0", "CATALOGUE_PRESENCE_NO_CURRICULUM_CREDIT"),
                ("F1", "O3", "CATALOGUE_PRESENCE_NO_CURRICULUM_CREDIT"),
            }:
                raise BuildError(f"OER unresolved row has an unsupported finite state: {matrix_id}")
        else:
            raise BuildError(f"unsupported OER finding status: {matrix_id}")
        route_statuses.append(
            {
                "route_status_id": matrix_id,
                "target_id": row["target_id"],
                "isced_stage": row["isced_stage"],
                "subject_domain": row["subject_domain"],
                "canon_atom_id": row["canon_atom_id"],
                "baseline_access_endpoint_id": row["baseline_access_endpoint_id"],
                "baseline_functional_route_id": derivation["baseline_functional_route_id"] or None,
                "finding_status": row["finding_status"],
                "functional_access_grade": row["functional_access_grade"],
                "open_adaptation_grade": row["open_adaptation_grade"],
                "coverage_credit_status": row["coverage_credit_status"],
                "derivation_status": derivation["derivation_status"],
                "resource_gap_values": {"low": None, "base": None, "high": None},
                "query_count": len(queries),
                "repository_count_credit": 0,
                "score_effect": None,
            }
        )

    counts = validation["counts"]
    expected_validation_counts = {
        "canon_cells_per_target": 35,
        "derivation_rows": 5180,
        "exact_targets": 148,
        "f0_rows": 4852,
        "f1_rows": 296,
        "f2_rows": 0,
        "f3_rows": 0,
        "f4_rows": 32,
        "matrix_rows": 5180,
        "numeric_resource_gap_rows": 0,
        "queries_per_cell": 5,
        "query_rows": 25900,
        "repository_counts_credited_as_coverage": 0,
        "resource_found_rows": 32,
        "source_records": 35,
        "stages": 7,
        "subjects": 5,
        "unresolved_rows": 5148,
    }
    if counts != expected_validation_counts:
        raise BuildError("OER validation receipt does not have the frozen complete count profile")
    actual_counts = {
        "exact_targets": len(target_ids),
        "matrix_rows": len(matrix_rows),
        "query_rows": len(query_rows),
        "derivation_rows": len(derivation_rows),
        "resource_found_rows": sum(row["finding_status"] == "RESOURCE_FOUND" for row in matrix_rows),
        "unresolved_rows": sum(row["finding_status"] == "SEARCH_UNRESOLVED" for row in matrix_rows),
        "numeric_resource_gap_rows": sum(
            any(row[field] for field in ("resource_gap_low", "resource_gap_base", "resource_gap_high"))
            for row in derivation_rows
        ),
        "repository_counts_credited_as_coverage": sum(
            row["repository_count_used_as_coverage"] != "0" for row in matrix_rows
        ),
        "f0_rows": sum(row["functional_access_grade"] == "F0" for row in matrix_rows),
        "f1_rows": sum(row["functional_access_grade"] == "F1" for row in matrix_rows),
        "f2_rows": sum(row["functional_access_grade"] == "F2" for row in matrix_rows),
        "f3_rows": sum(row["functional_access_grade"] == "F3" for row in matrix_rows),
        "f4_rows": sum(row["functional_access_grade"] == "F4" for row in matrix_rows),
        "canon_cells_per_target": len(canon_cells),
        "queries_per_cell": 5,
        "stages": len(stage_ids),
        "subjects": len(subject_ids),
    }
    for key, value in actual_counts.items():
        if value != counts[key]:
            raise BuildError(f"OER validation count mismatch for {key}: {value} != {counts[key]}")
    if actual_counts != {
        "exact_targets": 148,
        "matrix_rows": 5180,
        "query_rows": 25900,
        "derivation_rows": 5180,
        "resource_found_rows": 32,
        "unresolved_rows": 5148,
        "numeric_resource_gap_rows": 0,
        "repository_counts_credited_as_coverage": 0,
        "f0_rows": 4852,
        "f1_rows": 296,
        "f2_rows": 0,
        "f3_rows": 0,
        "f4_rows": 32,
        "canon_cells_per_target": 35,
        "queries_per_cell": 5,
        "stages": 7,
        "subjects": 5,
    }:
        raise BuildError(f"unexpected OER lane profile: {actual_counts}")
    found_routes = [row["resource_route_id"] for row in matrix_rows if row["finding_status"] == "RESOURCE_FOUND"]
    if len(found_routes) != 32 or len(set(found_routes)) != 32:
        raise BuildError("OER lane does not preserve 32 distinct exact functional-school routes")
    return {
        "adapter": "oer_route_status_manifest_v2",
        "manifest_identity": {
            "path": spec["path"],
            "bytes": manifest_path.stat().st_size,
            "sha256": sha256_file(manifest_path),
        },
        "validation_identity": {
            "path": spec["validation_path"],
            "bytes": validation_path.stat().st_size,
            "sha256": sha256_file(validation_path),
            "validation_passed": True,
        },
        "artifact_identities": identities,
        "counts": actual_counts,
        "route_statuses": route_statuses,
        "import_scope": "manifest identities and route-level status only",
        "query_rows_embedded": False,
        "unresolved_semantics": "MISSING_NOT_ZERO_NOT_HIGH_SCARCITY",
        "repository_count_credit_policy": "FORBIDDEN",
        "resource_gap_score_effect": None,
        "source_registry_fk_status": "NOT_IMPORTED_OUTSIDE_TASK_AUTHORITY_SCOPE",
    }


EMPIRICAL_CONTEXT_TOKENS = (
    "ceiling",
    "proxy",
    "context",
    "not_script_readership",
    "not_language",
    "variety_unresolved",
    "no_compatible",
    "unrankable",
    "no_exact",
    "unavailable",
    "no_person",
    "no_source_stated_count",
    "without_source_stated",
    "share_no",
    "shares_no",
    "shares_without",
    "ethnic",
    "ethnicity",
    "nationality",
    "registered_population",
    "territorial_population",
    "territorial_presence",
    "territorial_written",
    "territorial_education",
    "territorial_official",
    "territorial_national",
    "territorial_variety",
    "model_based",
    "sample_based_territorial",
    "official_census_scope",
    "household_counts_no_person",
    "person_response_ceiling",
)

EMPIRICAL_QUARANTINE_TOKENS = (
    "macro",
    "umbrella",
    "shared",
    "not_script_readership",
    "not_language",
    "variety_unresolved",
    "ethnic",
    "ethnicity",
    "nationality",
    "proxy",
)


def _validate_file_spec(
    base: Path,
    spec: Mapping[str, Any],
    path_key: str,
    bytes_key: str,
    sha_key: str,
) -> tuple[Path, dict[str, Any]]:
    path = exact_relative(base, spec[path_key])
    identity = {
        "path": spec[path_key],
        "bytes": path.stat().st_size,
        "sha256": sha256_file(path),
    }
    if identity["bytes"] != spec[bytes_key] or identity["sha256"] != str(spec[sha_key]).lower():
        raise BuildError(f"pinned empirical bundle identity mismatch: {spec[path_key]}")
    return path, identity


def _validate_detached_hash_manifest(
    base: Path,
    spec: Mapping[str, Any],
    identities: Sequence[Mapping[str, Any]],
) -> dict[str, Any] | None:
    if "hash_manifest_path" not in spec:
        return None
    path, identity = _validate_file_spec(
        base, spec, "hash_manifest_path", "hash_manifest_bytes", "hash_manifest_sha256"
    )
    declared: dict[str, str] = {}
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        if not raw_line.strip():
            continue
        parts = raw_line.strip().split(maxsplit=1)
        if len(parts) != 2 or len(parts[0]) != 64:
            raise BuildError(f"malformed detached hash-manifest line in {spec['hash_manifest_path']}")
        declared[parts[1].replace("\\", "/")] = parts[0].lower()
    for item in identities:
        matches = [value for name, value in declared.items() if name == item["path"] or Path(name).name == Path(item["path"]).name]
        if len(matches) != 1 or matches[0] != item["sha256"]:
            raise BuildError(f"detached hash manifest does not bind {item['path']}")
    return identity


def _validate_empirical_profile(
    profile: str,
    validation: Mapping[str, Any],
    *,
    row_count: int,
    source_count: int,
    numeric_count: int,
) -> tuple[int, set[str], set[str]]:
    upstream_unrankable: set[str] = set()
    upstream_proxy_or_ceiling: set[str] = set()
    if profile == "africa_v1":
        if any(check["status"] != "passed" for check in validation["checks"]):
            raise BuildError("Africa empirical validation contains a failed check")
        expected_rows = validation["coverage"]["total_exact_rows"]
        expected_sources = validation["source_integrity"]["referenced_source_count"]
        expected_numeric = validation["population_integrity"]["rows_with_compatible_numeric_construct"]
    elif profile == "asia_v1":
        if not all(validation["checks"].values()):
            raise BuildError("Asia empirical validation contains a failed check")
        expected_rows = validation["coverage"]["final_rows"]
        expected_sources = validation["source_integrity"]["registry_rows"]
        patterns = validation["population_integrity"]["patterns"]
        expected_numeric = expected_rows - patterns["no_numeric"]
    elif profile == "americas_europe_v1":
        if validation.get("status") != "pass" or validation.get("errors"):
            raise BuildError("Americas/Europe empirical validation did not pass")
        if any(check["passed"] is not True for check in validation["checks"]):
            raise BuildError("Americas/Europe empirical validation contains a failed check")
        expected_rows = validation["row_count"]
        expected_sources = validation["source_count"]
        expected_numeric = validation["direct_base_person_rows"] + validation["range_or_ceiling_rows"]
    elif profile == "oceania_central_asia_v1":
        if validation.get("status") != "PASS" or validation.get("errors"):
            raise BuildError("Oceania/Central Asia empirical validation did not pass")
        if not all(validation["deterministic_checks"].values()):
            raise BuildError("Oceania/Central Asia empirical validation contains a failed check")
        expected_rows = validation["row_count"]
        expected_sources = validation["source_count"]
        expected_numeric = expected_rows - sum(
            count
            for measure_class, count in validation["population_measure_class_counts"].items()
            if measure_class.startswith("unrankable")
        )
        # The source receipt explicitly identifies numeric rows that remain unrankable.
        upstream_unrankable = set(validation["unrankable_numeric_rows"])
        upstream_proxy_or_ceiling = set(validation["proxy_or_ceiling_rows"])
    else:
        raise BuildError(f"unsupported empirical validation profile: {profile}")
    if (row_count, source_count, numeric_count) != (expected_rows, expected_sources, expected_numeric):
        raise BuildError(
            f"empirical validation count mismatch for {profile}: "
            f"{(row_count, source_count, numeric_count)} != {(expected_rows, expected_sources, expected_numeric)}"
        )
    return expected_rows - expected_numeric, upstream_unrankable, upstream_proxy_or_ceiling


def _normalized_empirical_source(
    row: Mapping[str, str],
    *,
    bundle_id: str,
    source_schema: str,
    origin_file: str,
    row_number: int,
) -> dict[str, Any]:
    source_id = f"source:empirical:{bundle_id}:{row['source_id'].lower()}"
    if source_schema == "standard_11":
        organization = row["organization"]
        year = row["year"]
        access_date = row["access_date"]
        claim_scope = row["claim_scope"]
        notes = row["notes"]
    elif source_schema == "americas_europe_10":
        organization = row["publisher"]
        year = row["reference_year"]
        access_date = row["accessed_date"]
        claim_scope = row["construct_and_limits"]
        notes = ""
    elif source_schema == "oceania_central_asia_11":
        organization = row["issuer_or_authors"]
        year = row["year"]
        access_date = row["accessed_utc"]
        claim_scope = row["evidence_scope"]
        notes = row["limitations"]
    else:
        raise BuildError(f"unsupported empirical source schema: {source_schema}")
    return {
        "source_id": source_id,
        "canonical_source_id": source_id,
        "same_url_alias_ids": [source_id, row["source_id"]],
        "upstream_source_id": row["source_id"],
        "title": row["title"],
        "organization": organization,
        "year": year,
        "url": row["url"],
        "access_date": access_date,
        "claim_scope": claim_scope,
        "origin_file": origin_file,
        "source_row_number": row_number,
        "source_row_sha256": _row_sha(row),
        "undated": year in {"", "n.d."},
        "source_type": row["source_type"],
        "locator": row["locator"],
        "territory_or_scope": row.get("territory_or_scope") or row.get("region", ""),
        "notes": notes,
    }


def _empirical_construct_disposition(
    row: Mapping[str, str],
    values: Mapping[str, Any],
    *,
    upstream_unrankable: set[str],
    upstream_proxy_or_ceiling: set[str],
) -> tuple[str, str, str]:
    if not any(value is not None for value in values.values()):
        return (
            "MISSING_COMPATIBLE_PERSON_EVIDENCE",
            "INSUFFICIENT_PUBLIC_EVIDENCE",
            "NO_NUMERIC_PERSON_CONSTRUCT",
        )
    measure_class = row["population_measure_class"]
    folded = measure_class.casefold()
    context_tokens = sorted(token for token in EMPIRICAL_CONTEXT_TOKENS if token in folded)
    if row["stratum_id"] in upstream_unrankable:
        context_tokens.append("upstream_explicit_unrankable_numeric")
    if row["stratum_id"] in upstream_proxy_or_ceiling:
        context_tokens.append("upstream_proxy_or_ceiling")
    if context_tokens:
        quarantine = any(token in folded for token in EMPIRICAL_QUARANTINE_TOKENS)
        status = (
            "QUARANTINED_INCOMPATIBLE_CONSTRUCT_NO_INHERITANCE"
            if quarantine
            else "ADMIT_CONTEXT_NO_INHERITANCE"
        )
        return status, "INSUFFICIENT_PUBLIC_EVIDENCE", ";".join(sorted(set(context_tokens)))
    low, base, high = values["low"], values["base"], values["high"]
    if low is not None and high is not None and low != high:
        rankability = "INTERVAL_ONLY"
    elif base is not None or (low is not None and high is not None and low == high):
        rankability = "POINT_DISTRIBUTION"
    else:
        rankability = "INSUFFICIENT_PUBLIC_EVIDENCE"
    return "ADMIT_DIRECT_EXACT_STRATUM_ONLY", rankability, "closed_compatible_construct"


def _validate_empirical_validation_binding(
    profile: str,
    validation: Mapping[str, Any],
    identities: Sequence[Mapping[str, Any]],
) -> None:
    by_name = {Path(row["path"]).name: row for row in identities}
    if profile == "africa_v1":
        for key in ("inputs_csv", "sources_csv"):
            declared = validation["files"][key]
            actual = by_name[Path(declared["path"]).name]
            if declared["bytes"] != actual["bytes"] or declared["sha256"].lower() != actual["sha256"]:
                raise BuildError(f"Africa validation does not bind {actual['path']}")
    elif profile == "asia_v1":
        declared_by_name = {Path(row["relative_path"]).name: row for row in validation["files"]}
        for actual in identities:
            declared = declared_by_name.get(Path(actual["path"]).name)
            if declared is None:
                continue
            if declared["bytes"] != actual["bytes"] or declared["sha256"].lower() != actual["sha256"]:
                raise BuildError(f"Asia validation does not bind {actual['path']}")


def adapt_empirical_need_bundles(
    base: Path,
    specs: Sequence[Mapping[str, Any]],
    contract: Mapping[str, Any],
    occupied_import_ids: set[str],
) -> tuple[dict[str, Any], list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    expected_input_header = contract["regional_empirical_need_bundle"]["input_header"]
    source_headers = contract["regional_empirical_need_bundle"]["source_headers"]
    bundle_ids = [row["bundle_id"] for row in specs]
    if len(bundle_ids) != len(set(bundle_ids)):
        raise BuildError("duplicate regional empirical bundle_id")
    evidence_records: list[dict[str, Any]] = []
    provenance: list[dict[str, Any]] = []
    sources: list[dict[str, Any]] = []
    quarantines: list[dict[str, Any]] = []
    bundle_receipts: list[dict[str, Any]] = []
    group_by_stratum: dict[str, list[dict[str, Any]]] = defaultdict(list)

    for spec in specs:
        inputs_path, inputs_identity = _validate_file_spec(
            base, spec, "inputs_path", "inputs_bytes", "inputs_sha256"
        )
        sources_path, sources_identity = _validate_file_spec(
            base, spec, "sources_path", "sources_bytes", "sources_sha256"
        )
        validation_path, validation_identity = _validate_file_spec(
            base, spec, "validation_path", "validation_bytes", "validation_sha256"
        )
        detached_identity = _validate_detached_hash_manifest(
            base, spec, [inputs_identity, sources_identity, validation_identity]
        )
        validation = read_json(validation_path)
        input_header, input_rows = read_csv(inputs_path)
        source_header, source_rows = read_csv(sources_path)
        _assert_exact_header(input_header, expected_input_header, spec["inputs_path"])
        schema_name = spec["source_schema"]
        if schema_name not in source_headers:
            raise BuildError(f"unknown empirical source schema: {schema_name}")
        _assert_exact_header(source_header, source_headers[schema_name], spec["sources_path"])
        if len({row["stratum_id"] for row in input_rows}) != len(input_rows):
            raise BuildError(f"duplicate stratum_id within {spec['bundle_id']}")
        if len({row["source_id"] for row in source_rows}) != len(source_rows):
            raise BuildError(f"duplicate source_id within {spec['bundle_id']}")
        source_by_upstream_id = {row["source_id"]: row for row in source_rows}
        numeric_count = 0
        parsed_values: dict[str, dict[str, int | float | None]] = {}
        for row in input_rows:
            values = {
                "low": _number(row["population_low_persons"], label=f"{spec['bundle_id']}:{row['stratum_id']}.low"),
                "base": _number(row["population_base_persons"], label=f"{spec['bundle_id']}:{row['stratum_id']}.base"),
                "high": _number(row["population_high_persons"], label=f"{spec['bundle_id']}:{row['stratum_id']}.high"),
            }
            if values["low"] is not None and values["high"] is not None and values["low"] > values["high"]:
                raise BuildError(f"empirical low exceeds high: {spec['bundle_id']}:{row['stratum_id']}")
            if values["base"] is not None:
                if values["low"] is not None and values["base"] < values["low"]:
                    raise BuildError(f"empirical base below low: {spec['bundle_id']}:{row['stratum_id']}")
                if values["high"] is not None and values["base"] > values["high"]:
                    raise BuildError(f"empirical base above high: {spec['bundle_id']}:{row['stratum_id']}")
            if any(value is not None for value in values.values()):
                numeric_count += 1
            parsed_values[row["stratum_id"]] = values
        explicit_blank_count, upstream_unrankable, upstream_proxy_or_ceiling = _validate_empirical_profile(
            spec["validation_profile"],
            validation,
            row_count=len(input_rows),
            source_count=len(source_rows),
            numeric_count=numeric_count,
        )
        _validate_empirical_validation_binding(
            spec["validation_profile"], validation, [inputs_identity, sources_identity]
        )

        for row_number, row in enumerate(source_rows, 2):
            if not row["source_id"] or not row["url"].startswith("https://"):
                raise BuildError(f"invalid empirical source row in {spec['sources_path']}:{row_number}")
            sources.append(
                _normalized_empirical_source(
                    row,
                    bundle_id=spec["bundle_id"],
                    source_schema=schema_name,
                    origin_file=spec["sources_path"],
                    row_number=row_number,
                )
            )

        for row_number, row in enumerate(input_rows, 2):
            stratum_id = row["stratum_id"]
            import_id = f"{spec['bundle_id']}:{stratum_id}"
            if import_id in occupied_import_ids:
                raise BuildError(f"duplicate empirical import identity: {import_id}")
            occupied_import_ids.add(import_id)
            if not all(row[field] for field in (
                "stratum_id", "label", "territory", "script_or_mode", "population_measure_class",
                "population_definition", "education_language_exposure_mismatch_by_stage",
                "learning_completion_evidence", "functional_resource_access", "open_adaptable_scarcity",
                "academic_lingua_franca_nonoverlap", "device_connectivity_electricity",
                "accessible_offline_delivery_evidence", "source_ids", "source_urls",
                "uncertainty_incompatibilities", "evidence_confidence",
            )):
                raise BuildError(f"empirical row lacks required evidence fields: {import_id}")
            upstream_source_ids = _split_semicolon(row["source_ids"])
            source_urls = _split_semicolon(row["source_urls"])
            if len(upstream_source_ids) != len(source_urls):
                raise BuildError(f"empirical source ID/URL alignment failure: {import_id}")
            missing_sources = [source_id for source_id in upstream_source_ids if source_id not in source_by_upstream_id]
            if missing_sources:
                raise BuildError(f"empirical source foreign-key failure {import_id}: {missing_sources}")
            for source_id, url in zip(upstream_source_ids, source_urls):
                if source_by_upstream_id[source_id]["url"] != url:
                    raise BuildError(f"empirical source URL binding failure: {import_id}:{source_id}")
            values = parsed_values[stratum_id]
            disposition, rankability, disposition_reason = _empirical_construct_disposition(
                row,
                values,
                upstream_unrankable=upstream_unrankable,
                upstream_proxy_or_ceiling=upstream_proxy_or_ceiling,
            )
            if values["low"] is not None and values["high"] is not None and values["low"] != values["high"]:
                bound_semantics = "INTERVAL"
            elif values["base"] is not None or (
                values["low"] is not None and values["high"] is not None and values["low"] == values["high"]
            ):
                bound_semantics = "POINT"
            elif values["low"] is not None:
                bound_semantics = "LOWER_BOUND"
            elif values["high"] is not None:
                bound_semantics = "UPPER_BOUND"
            else:
                bound_semantics = "NONE"
            evidence_id = f"empirical-evidence:{spec['bundle_id']}:{stratum_id}"
            measure_id = f"empirical-measure:{spec['bundle_id']}:{stratum_id}" if numeric_count and any(
                value is not None for value in values.values()
            ) else None
            row_sha = _row_sha(row)
            evidence = {
                "empirical_evidence_id": evidence_id,
                "population_evidence_id": measure_id,
                "bundle_id": spec["bundle_id"],
                "region": spec["region"],
                "stratum_id": stratum_id,
                "origin_file": spec["inputs_path"],
                "origin_row_number": row_number,
                "origin_row_sha256": row_sha,
                "identity_assertion": {
                    "label": row["label"],
                    "aliases": _split_semicolon(row["aliases"]),
                    "territory": row["territory"],
                    "script_or_mode": row["script_or_mode"],
                },
                "language_target_ids": [],
                "population_measure_class": row["population_measure_class"],
                "source_values": {
                    **values,
                    "unit": row["population_unit"],
                    "bound_semantics": bound_semantics,
                },
                "person_normalization": {
                    "status": (
                        "VALIDATED_PERSON_STOCK_FIELDS_IDENTITY_MULTIPLIER"
                        if any(value is not None for value in values.values())
                        else "NO_COMPATIBLE_PERSON_VALUE"
                    ),
                    "values_persons": deepcopy(values),
                    "normalization_multiplier": 1 if any(value is not None for value in values.values()) else None,
                },
                "population_definition": row["population_definition"],
                "reference_year": row["population_reference_year"],
                "population_secondary_context": row["population_secondary_context"],
                "source_ids": [
                    f"source:empirical:{spec['bundle_id']}:{source_id.lower()}"
                    for source_id in upstream_source_ids
                ],
                "construct_admissibility_status": disposition,
                "construct_admissibility_reason": disposition_reason,
                "target_binding": (
                    "EMPIRICAL_STRATUM_ONLY_NO_CANONICAL_INHERITANCE"
                    if disposition == "ADMIT_DIRECT_EXACT_STRATUM_ONLY"
                    else (
                        "QUARANTINED_NO_INHERITANCE"
                        if disposition.startswith("QUARANTINED")
                        else "CONTEXT_OR_MISSING_NO_INHERITANCE"
                    )
                ),
                "population_rankability_status": rankability,
                "qualitative_evidence": {
                    "stage_exposure_mismatch": row["education_language_exposure_mismatch_by_stage"],
                    "learning_completion": row["learning_completion_evidence"],
                    "functional_resource_access": row["functional_resource_access"],
                    "open_adaptable_scarcity": row["open_adaptable_scarcity"],
                    "academic_lingua_franca_nonoverlap": row["academic_lingua_franca_nonoverlap"],
                    "device_connectivity_electricity": row["device_connectivity_electricity"],
                    "accessible_offline_delivery": row["accessible_offline_delivery_evidence"],
                    "uncertainty_incompatibilities": row["uncertainty_incompatibilities"],
                    "evidence_confidence": row["evidence_confidence"],
                },
                "stage_identity_status": "QUALITATIVE_UNSPLIT_NOT_EVENT_TYPED",
                "endpoint_identity_status": "QUALITATIVE_UNSPLIT_NOT_EVENT_TYPED",
                "local_or_user_production_inputs_used": False,
                "score_eligible": False,
                "score": None,
                "collision_disposition": "NO_COLLISION",
                "identity_effective_for_intervention_target": True,
            }
            evidence_records.append(evidence)
            group_by_stratum[stratum_id].append(evidence)
            if disposition.startswith("QUARANTINED"):
                quarantine_id = f"quarantine:empirical:{spec['bundle_id']}:{stratum_id}"
                quarantines.append(
                    {
                        "quarantine_id": quarantine_id,
                        "origin_lane": "regional_empirical_need_bundle",
                        "origin_record_id": import_id,
                        "reason_codes": ["INCOMPATIBLE_EXACT_STRATUM_DENOMINATOR"],
                        "reason": disposition_reason,
                        "replacement_ids": [],
                        "record": evidence,
                    }
                )
            provenance.append(
                _provenance_record(
                    input_id=import_id,
                    origin_file=spec["inputs_path"],
                    row_number=row_number,
                    row_sha=row_sha,
                    output_type="regional_empirical_stratum_evidence",
                    output_id=f"empirical-stratum:{stratum_id}",
                    target_ids=[],
                    measure_ids=[measure_id] if measure_id else [],
                    source_id=evidence["source_ids"][0],
                )
            )
        bundle_receipts.append(
            {
                "bundle_id": spec["bundle_id"],
                "region": spec["region"],
                "adapter": spec["adapter"],
                "identities": {
                    "inputs": inputs_identity,
                    "sources": sources_identity,
                    "validation": validation_identity,
                    "hash_manifest": detached_identity,
                },
                "row_count": len(input_rows),
                "source_count": len(source_rows),
                "numeric_person_rows": numeric_count,
                "explicit_blank_rows": explicit_blank_count,
                "validation_passed": True,
            }
        )

    expected_collision_ids = {"apd-Arab-SD", "arz-Arab-EG", "mey-Arab-MR", "shu-Arab-TD", "mg-Latn-MG"}
    actual_collision_ids = {key for key, rows in group_by_stratum.items() if len(rows) > 1}
    if actual_collision_ids != expected_collision_ids:
        raise BuildError(
            f"regional empirical collision set changed: {sorted(actual_collision_ids)} != {sorted(expected_collision_ids)}"
        )
    collision_dispositions: list[dict[str, Any]] = []
    for stratum_id in sorted(actual_collision_ids):
        rows = group_by_stratum[stratum_id]
        if len(rows) != 2:
            raise BuildError(f"unexpected empirical collision multiplicity: {stratum_id}")
        bundle_set = {row["bundle_id"] for row in rows}
        if stratum_id in {"apd-Arab-SD", "arz-Arab-EG", "mey-Arab-MR", "shu-Arab-TD"}:
            asia = next(row for row in rows if row["bundle_id"] == "asia_20260901_v1")
            africa = next(row for row in rows if row["bundle_id"] == "africa_20260901_v1")
            asia["collision_disposition"] = "QUARANTINED_SPOKEN_OR_BROADER_SCOPE_ASSERTION_FROM_ARAB_SCRIPT_TARGET_IDENTITY"
            asia["identity_effective_for_intervention_target"] = False
            quarantine_id = f"quarantine:empirical-collision:{stratum_id}:asia-identity-scope"
            quarantines.append(
                {
                    "quarantine_id": quarantine_id,
                    "origin_lane": "regional_empirical_need_collision",
                    "origin_record_id": f"asia_20260901_v1:{stratum_id}",
                    "reason_codes": ["PRODUCTION_IDENTITY_MODE_OR_SCOPE_CONFLICT"],
                    "reason": (
                        "The Asia assertion describes a spoken variety (and, for Hassaniya, broader territory context), "
                        "while the exact stratum ID contains an Arab script arm. Its evidence is preserved as "
                        "nonadditive context, but its identity assertion cannot redefine the script-specific intervention target."
                    ),
                    "replacement_ids": [],
                    "record": asia,
                }
            )
            disposition = "MERGED_EVIDENCE_WITH_ASIA_PRODUCTION_IDENTITY_ASSERTION_QUARANTINED"
            compatibility = "SCRIPT_OR_MODE_SCOPE_CONFLICT"
            identity_basis = [africa["empirical_evidence_id"]]
        elif stratum_id == "mg-Latn-MG":
            disposition = "MERGED_DISTINCT_NONADDITIVE_ABILITY_AND_WRITTEN_EXPOSURE_CONSTRUCTS"
            compatibility = "COMPATIBLE_IDENTITY_DISTINCT_CONSTRUCTS"
            identity_basis = sorted(row["empirical_evidence_id"] for row in rows)
        for row in rows:
            if row["collision_disposition"] == "NO_COLLISION":
                row["collision_disposition"] = disposition
        collision_dispositions.append(
            {
                "stratum_id": stratum_id,
                "bundle_ids": sorted(bundle_set),
                "evidence_ids": sorted(row["empirical_evidence_id"] for row in rows),
                "compatibility_status": compatibility,
                "disposition": disposition,
                "intervention_target_identity_evidence_ids": identity_basis,
                "additivity": "NONADDITIVE",
                "chosen_by_bundle_order": False,
            }
        )

    strata: list[dict[str, Any]] = []
    intervention_targets: list[dict[str, Any]] = []
    for stratum_id in sorted(group_by_stratum):
        rows = group_by_stratum[stratum_id]
        effective_identity_rows = [row for row in rows if row["identity_effective_for_intervention_target"]]
        quarantined_identity_rows = [row for row in rows if not row["identity_effective_for_intervention_target"]]
        if not effective_identity_rows:
            raise BuildError(f"empirical stratum has no effective intervention identity: {stratum_id}")
        intervention_target_id = f"intervention-target:regional-stratum:{stratum_id}"
        stratum_record = {
            "stratum_id": stratum_id,
            "intervention_target_id": intervention_target_id,
            "bundle_ids": sorted({row["bundle_id"] for row in rows}),
            "identity_assertions": [deepcopy(row["identity_assertion"]) for row in effective_identity_rows],
            "quarantined_identity_assertions": [
                {
                    "empirical_evidence_id": row["empirical_evidence_id"],
                    **deepcopy(row["identity_assertion"]),
                    "collision_disposition": row["collision_disposition"],
                }
                for row in quarantined_identity_rows
            ],
            "empirical_evidence_ids": [row["empirical_evidence_id"] for row in rows],
            "direct_population_measure_ids": [
                row["population_evidence_id"]
                for row in rows
                if row["population_evidence_id"]
                and row["construct_admissibility_status"] == "ADMIT_DIRECT_EXACT_STRATUM_ONLY"
                and row["identity_effective_for_intervention_target"]
            ],
            "context_population_measure_ids": [
                row["population_evidence_id"]
                for row in rows
                if row["population_evidence_id"]
                and (
                    row["construct_admissibility_status"] != "ADMIT_DIRECT_EXACT_STRATUM_ONLY"
                    or not row["identity_effective_for_intervention_target"]
                )
            ],
            "canonical_language_target_inheritance": "NONE",
            "collision_status": (
                next(
                    item["disposition"]
                    for item in collision_dispositions
                    if item["stratum_id"] == stratum_id
                )
                if len(rows) > 1
                else "NO_COLLISION"
            ),
        }
        strata.append(stratum_record)
        intervention_targets.append(
            {
                "intervention_target_id": intervention_target_id,
                "stratum_id": stratum_id,
                "canonical_language_target_id": None,
                "mapping_cardinality": "ONE_STRATUM_TO_ONE_INTERVENTION_TARGET",
                "identity_assertions": deepcopy(stratum_record["identity_assertions"]),
                "production_intervention_design": "STANDALONE_EXACT_VARIETY_REGISTER_SCRIPT_MODE_TERRITORY_STRATUM",
                "package_or_overlay_inheritance": "NONE",
                "evidence_ids": list(stratum_record["empirical_evidence_ids"]),
            }
        )
    if len({row["intervention_target_id"] for row in intervention_targets}) != len(intervention_targets):
        raise BuildError("two empirical strata map to one intervention target")
    if {row["stratum_id"] for row in intervention_targets} != set(group_by_stratum):
        raise BuildError("lossless empirical stratum-to-target mapping is incomplete")
    if len(evidence_records) != 302 or len(strata) != 297 or len(collision_dispositions) != 5:
        raise BuildError("joined empirical bundle counts do not match the frozen four-bundle boundary")
    lane = {
        "adapter": "regional_empirical_need_bundle_v1",
        "bundle_receipts": bundle_receipts,
        "counts": {
            "bundle_count": len(bundle_receipts),
            "input_rows": len(evidence_records),
            "unique_strata": len(strata),
            "collision_strata": len(collision_dispositions),
            "numeric_person_rows": sum(row["numeric_person_rows"] for row in bundle_receipts),
            "explicit_blank_rows": sum(row["explicit_blank_rows"] for row in bundle_receipts),
            "source_rows": len(sources),
            "direct_exact_stratum_person_rows": sum(
                row["construct_admissibility_status"] == "ADMIT_DIRECT_EXACT_STRATUM_ONLY"
                for row in evidence_records
            ),
            "context_or_quarantined_numeric_rows": sum(
                row["population_evidence_id"] is not None
                and row["construct_admissibility_status"] != "ADMIT_DIRECT_EXACT_STRATUM_ONLY"
                for row in evidence_records
            ),
        },
        "strata": strata,
        "intervention_targets": intervention_targets,
        "stratum_to_target_mapping": [
            {
                "stratum_id": row["stratum_id"],
                "intervention_target_id": row["intervention_target_id"],
                "mapping_cardinality": row["mapping_cardinality"],
            }
            for row in intervention_targets
        ],
        "evidence_records": evidence_records,
        "collision_dispositions": collision_dispositions,
        "canonical_language_target_inheritance": "NONE",
        "qualitative_fields_have_numeric_score_effect": False,
        "local_or_user_production_inputs_used": False,
    }
    return lane, provenance, sources, quarantines


def _append_sources_preserving_prefix(
    original: Sequence[Mapping[str, Any]], additions: Iterable[Mapping[str, Any]]
) -> list[dict[str, Any]]:
    result = deepcopy(list(original))
    existing = {row["source_id"]: row for row in result}
    for addition in additions:
        source_id = addition["source_id"]
        if source_id in existing:
            if canonical_sha256(existing[source_id]) != canonical_sha256(addition):
                raise BuildError(f"unequal source_id collision: {source_id}")
            continue
        copied = deepcopy(dict(addition))
        result.append(copied)
        existing[source_id] = copied
    return result


def _candidate_shell(
    *,
    candidate_id: str,
    candidate_kind: str,
    language_target_id: str | None,
    intervention_target_id: str | None,
    empirical_stratum_id: str | None,
    regional_bundle_ids: Sequence[str],
    package_id: str | None,
    component_target_ids: Sequence[str],
    admissibility_status: str,
    effective_universe_membership: bool,
    target_identity_status: str,
    event_identity_status: str,
    supersession: Mapping[str, Any] | None,
    direct_population_measure_ids: Sequence[str],
    context_measure_ids: Sequence[str],
    quarantine_ids: Sequence[str],
    event_ids: Sequence[str],
    endpoint_ids: Sequence[str],
    stage_ids: Sequence[str],
    population_measure_role: str,
    oer_route_status_counts: Mapping[str, int],
    population_rankability_status: str,
    missing_core_fields: Sequence[str],
) -> dict[str, Any]:
    return {
        "candidate_id": candidate_id,
        "candidate_kind": candidate_kind,
        "language_target_id": language_target_id,
        "intervention_target_id": intervention_target_id,
        "empirical_stratum_id": empirical_stratum_id,
        "regional_bundle_ids": list(regional_bundle_ids),
        "package_id": package_id,
        "component_target_ids": list(component_target_ids),
        "admissibility_status": admissibility_status,
        "effective_universe_membership": effective_universe_membership,
        "target_identity_status": target_identity_status,
        "event_identity_status": event_identity_status,
        "supersession": deepcopy(supersession),
        "direct_population_measure_ids": list(direct_population_measure_ids),
        "context_measure_ids": list(context_measure_ids),
        "quarantine_ids": sorted(set(quarantine_ids)),
        "event_ids": list(event_ids),
        "endpoint_ids": list(endpoint_ids),
        "stage_ids": list(stage_ids),
        "population_measure_role": population_measure_role,
        "oer_route_status_counts": dict(oer_route_status_counts),
        "qualitative_evidence_score_effect": None,
        "population_rankability_status": population_rankability_status,
        "score_rankability_status": "INSUFFICIENT_PUBLIC_EVIDENCE",
        "selection_status": "UNRANKED_INSUFFICIENT",
        "score": None,
        "competition_rank": None,
        "selection_step": None,
        "missing_core_fields": sorted(set(missing_core_fields)),
    }


def evaluate_candidates(
    language_targets: Sequence[Mapping[str, Any]],
    legacy_package_interventions: Sequence[Mapping[str, Any]],
    package_profiles: Mapping[str, Mapping[str, Any]],
    population_evidence: Sequence[Mapping[str, Any]],
    signed_person_measures: Sequence[Mapping[str, Any]],
    quarantined_evidence: Sequence[Mapping[str, Any]],
    event_bindings: Sequence[Mapping[str, Any]],
    events_by_target: Mapping[str, Sequence[Mapping[str, Any]]],
    oer_lane: Mapping[str, Any],
    empirical_lane: Mapping[str, Any],
) -> list[dict[str, Any]]:
    evidence_by_target: dict[str, list[Mapping[str, Any]]] = defaultdict(list)
    for row in population_evidence:
        for target_id in row["language_target_ids"]:
            evidence_by_target[target_id].append(row)
    for row in signed_person_measures:
        if row.get("language_target_id"):
            evidence_by_target[row["language_target_id"]].append(row)
    quarantine_by_target: dict[str, list[str]] = defaultdict(list)
    for row in quarantined_evidence:
        target_ids: list[str] = []
        if "record" in row:
            target_ids.extend(row["record"].get("language_target_ids", []))
        original = row.get("original_payload", {})
        target_ids.extend(original.get("language_target_ids", []))
        if original.get("target_id"):
            target_ids.append(original["target_id"])
        for target_id in set(target_ids):
            quarantine_by_target[target_id].append(row["quarantine_id"])
    oer_counts_by_target: dict[str, Counter[str]] = defaultdict(Counter)
    oer_numeric_by_target: Counter[str] = Counter()
    for row in oer_lane["route_statuses"]:
        oer_counts_by_target[row["target_id"]][row["finding_status"]] += 1
        if any(value is not None for value in row["resource_gap_values"].values()):
            oer_numeric_by_target[row["target_id"]] += 1

    evidence_by_origin_id: dict[str, Mapping[str, Any]] = {}
    for row in population_evidence:
        origin_id = row.get("origin_record_id")
        if origin_id:
            evidence_by_origin_id[origin_id] = row
    target_by_id = {row["language_target_id"]: row for row in language_targets}

    evaluations: list[dict[str, Any]] = []
    for target in language_targets:
        target_id = target["language_target_id"]
        rows = evidence_by_target.get(target_id, [])
        direct = [
            row for row in rows
            if row.get("target_binding") == "DIRECT_TARGET_ONLY"
            and row.get("population_rankability_status") in {"POINT_DISTRIBUTION", "INTERVAL_ONLY"}
        ]
        contexts = [
            row for row in rows
            if row.get("population_evidence_id") not in {
                item.get("population_evidence_id") for item in direct
            }
        ]
        direct_ids = [row["population_evidence_id"] for row in direct]
        context_ids = [
            row.get("population_evidence_id") or row.get("record_id") or row.get("origin_record_id")
            for row in contexts
        ]
        event_rows = list(events_by_target.get(target_id, []))
        rankable_events = [row for row in event_rows if row["rankable_now"]]
        if any(row.get("population_rankability_status") == "POINT_DISTRIBUTION" for row in direct):
            population_status = "POINT_DISTRIBUTION"
        elif direct:
            population_status = "INTERVAL_ONLY"
        else:
            population_status = "INSUFFICIENT_PUBLIC_EVIDENCE"
        missing = []
        if not direct:
            missing.append("population_factor")
        if not rankable_events:
            missing.append("normative_conditional_need_event")
        missing.extend(["access_gain_factor", "common_complete_joint_draws"])
        route_counts = dict(sorted(oer_counts_by_target.get(target_id, {}).items()))
        if not route_counts or oer_numeric_by_target[target_id] < sum(route_counts.values()):
            missing.append("numeric_resource_gap_factor")
        superseded = SUPERSEDED_TARGETS.get(target_id)
        macro = (
            _is_macro_target(target)
            or target.get("exactness") != "exact"
        )
        if superseded:
            admissibility = "PRESERVED_LEGACY_SUPERSEDED_IDENTITY"
            identity_status = superseded["effective_status"]
            effective_membership = False
        elif macro:
            admissibility = "ADMISSIBLE_CONTEXT_ONLY_MACRO"
            identity_status = "MACRO_OR_UNRESOLVED_CONTEXT"
            effective_membership = bool(target["universe_membership"])
        else:
            admissibility = "ADMISSIBLE_EXACT_TARGET"
            identity_status = "EXACT_TARGET"
            effective_membership = bool(target["universe_membership"])
        evaluations.append(
            _candidate_shell(
                candidate_id=f"candidate:language:{target_id}",
                candidate_kind="language_target_summary",
                language_target_id=target_id,
                intervention_target_id=None,
                empirical_stratum_id=None,
                regional_bundle_ids=[],
                package_id=None,
                component_target_ids=[],
                admissibility_status=admissibility,
                effective_universe_membership=effective_membership,
                target_identity_status=identity_status,
                event_identity_status="LANGUAGE_SUMMARY_NOT_EVENT",
                supersession=superseded,
                direct_population_measure_ids=direct_ids,
                context_measure_ids=context_ids,
                quarantine_ids=quarantine_by_target.get(target_id, []),
                event_ids=sorted(row["event_id"] for row in event_rows),
                endpoint_ids=sorted({row["endpoint_id"] for row in event_rows}),
                stage_ids=sorted({stage for row in event_rows for stage in row["stage_ids"]}),
                population_measure_role="language_target_evidence_summary",
                oer_route_status_counts=route_counts,
                population_rankability_status=population_status,
                missing_core_fields=missing,
            )
        )

    legacy_package_ids: set[str] = set()
    for package in legacy_package_interventions:
        package_id = package["package_intervention_id"]
        if package_id in legacy_package_ids:
            raise BuildError(f"duplicate legacy package intervention: {package_id}")
        legacy_package_ids.add(package_id)
        evaluations.append(
            _candidate_shell(
                candidate_id=f"candidate:legacy-package:{package_id}",
                candidate_kind="legacy_package_intervention_summary",
                language_target_id=None,
                intervention_target_id=None,
                empirical_stratum_id=None,
                regional_bundle_ids=[],
                package_id=package_id,
                component_target_ids=package["language_target_ids"],
                admissibility_status="ADMISSIBLE_LEGACY_PACKAGE_CONTEXT_ONLY",
                effective_universe_membership=True,
                target_identity_status="PACKAGE_NOT_LANGUAGE_TARGET",
                event_identity_status="PACKAGE_SUMMARY_NOT_EVENT",
                supersession=None,
                direct_population_measure_ids=[],
                context_measure_ids=package["population_measure_ids"],
                quarantine_ids=[],
                event_ids=[],
                endpoint_ids=[],
                stage_ids=[],
                population_measure_role="package_context_never_inherited",
                oer_route_status_counts={},
                population_rankability_status="INSUFFICIENT_PUBLIC_EVIDENCE",
                missing_core_fields=[
                    "access_gain_factor",
                    "common_complete_joint_draws",
                    "normative_conditional_need_event",
                    "numeric_resource_gap_factor",
                    "population_factor",
                ],
            )
        )

    event_ids_seen: set[str] = set()
    for event in event_bindings:
        event_id = event["event_id"]
        if event_id in event_ids_seen:
            raise BuildError(f"duplicate event candidate: {event_id}")
        event_ids_seen.add(event_id)
        target_id = event["language_target_id"]
        package_id = event["package_intervention_id"]
        if package_id is not None and package_id not in legacy_package_ids:
            raise BuildError(f"event references unknown preserved package: {event_id} -> {package_id}")
        population_row = evidence_by_origin_id.get(event["population_measure_id"])
        direct_ids: list[str] = []
        context_ids: list[str] = []
        population_status = "INSUFFICIENT_PUBLIC_EVIDENCE"
        if population_row is not None:
            population_id = population_row["population_evidence_id"]
            if (
                population_row.get("target_binding") == "DIRECT_TARGET_ONLY"
                and population_row.get("population_rankability_status") in {"POINT_DISTRIBUTION", "INTERVAL_ONLY"}
            ):
                direct_ids = [population_id]
                population_status = population_row["population_rankability_status"]
            else:
                context_ids = [population_id]
        missing = ["access_gain_factor", "common_complete_joint_draws"]
        if not direct_ids:
            missing.append("population_factor")
        if not event["rankable_now"]:
            missing.append("normative_conditional_need_event")
        route_counts = dict(sorted(oer_counts_by_target.get(target_id, {}).items()))
        if not route_counts or oer_numeric_by_target[target_id] < sum(route_counts.values()):
            missing.append("numeric_resource_gap_factor")
        target = target_by_id[target_id]
        superseded = SUPERSEDED_TARGETS.get(target_id)
        context_identity = superseded is not None or _is_macro_target(target) or target.get("exactness") != "exact"
        evaluations.append(
            _candidate_shell(
                candidate_id=f"candidate:event:{event_id}",
                candidate_kind="typed_endpoint_stage_package_event",
                language_target_id=target_id,
                intervention_target_id=None,
                empirical_stratum_id=None,
                regional_bundle_ids=[],
                package_id=package_id,
                component_target_ids=[target_id],
                admissibility_status=(
                    "PRESERVED_EVENT_CONTEXT_ONLY_IDENTITY"
                    if context_identity
                    else "ADMISSIBLE_TYPED_EVENT_CANDIDATE"
                ),
                effective_universe_membership=not bool(superseded),
                target_identity_status=(
                    superseded["effective_status"]
                    if superseded
                    else ("MACRO_OR_UNRESOLVED_CONTEXT" if context_identity else "EXACT_TARGET")
                ),
                event_identity_status=f"{event['endpoint_operational_status']}|{event['stage_identity_status']}",
                supersession=superseded,
                direct_population_measure_ids=direct_ids,
                context_measure_ids=context_ids,
                quarantine_ids=quarantine_by_target.get(target_id, []),
                event_ids=[event_id],
                endpoint_ids=[event["endpoint_id"]],
                stage_ids=event["stage_ids"],
                population_measure_role=event["population_event_role"],
                oer_route_status_counts=route_counts,
                population_rankability_status=population_status,
                missing_core_fields=missing,
            )
        )

    for package_id in sorted(package_profiles):
        profile = package_profiles[package_id]
        if profile.get("population_measure_ids"):
            raise BuildError(f"package inherited population measures: {package_id}")
        evaluations.append(
            _candidate_shell(
                candidate_id=f"candidate:package:{package_id}",
                candidate_kind="successor_package_profile_summary",
                language_target_id=None,
                intervention_target_id=None,
                empirical_stratum_id=None,
                regional_bundle_ids=[],
                package_id=package_id,
                component_target_ids=profile["component_target_ids"],
                admissibility_status="ADMISSIBLE_PACKAGE_CONTEXT_ONLY",
                effective_universe_membership=True,
                target_identity_status="PACKAGE_NOT_LANGUAGE_TARGET",
                event_identity_status="PACKAGE_SUMMARY_NOT_EVENT",
                supersession=None,
                direct_population_measure_ids=[],
                context_measure_ids=list(profile.get("context_measure_ids", [])),
                quarantine_ids=[],
                event_ids=[],
                endpoint_ids=[],
                stage_ids=[],
                population_measure_role="package_context_never_inherited",
                oer_route_status_counts={},
                population_rankability_status="INSUFFICIENT_PUBLIC_EVIDENCE",
                missing_core_fields=[
                    "access_gain_factor",
                    "common_complete_joint_draws",
                    "normative_conditional_need_event",
                    "numeric_resource_gap_factor",
                    "population_factor",
                ],
            )
        )

    empirical_evidence_by_id = {
        row["empirical_evidence_id"]: row for row in empirical_lane["evidence_records"]
    }
    quarantine_by_stratum: dict[str, list[str]] = defaultdict(list)
    for row in quarantined_evidence:
        record = row.get("record", {})
        stratum_id = record.get("stratum_id")
        if stratum_id:
            quarantine_by_stratum[stratum_id].append(row["quarantine_id"])
    for stratum in empirical_lane["strata"]:
        stratum_id = stratum["stratum_id"]
        rows = [empirical_evidence_by_id[row_id] for row_id in stratum["empirical_evidence_ids"]]
        direct_rows = [
            row for row in rows
            if row["construct_admissibility_status"] == "ADMIT_DIRECT_EXACT_STRATUM_ONLY"
            and row["population_evidence_id"]
        ]
        if any(row["population_rankability_status"] == "POINT_DISTRIBUTION" for row in direct_rows):
            population_status = "POINT_DISTRIBUTION"
        elif any(row["population_rankability_status"] == "INTERVAL_ONLY" for row in direct_rows):
            population_status = "INTERVAL_ONLY"
        else:
            population_status = "INSUFFICIENT_PUBLIC_EVIDENCE"
        missing = [
            "access_gain_factor",
            "common_complete_joint_draws",
            "normative_conditional_need_event",
            "numeric_resource_gap_factor",
            "typed_stage_endpoint_event",
        ]
        if not direct_rows:
            missing.append("population_factor")
        evaluations.append(
            _candidate_shell(
                candidate_id=f"candidate:empirical-stratum:{stratum_id}",
                candidate_kind="regional_empirical_stratum",
                language_target_id=None,
                intervention_target_id=stratum["intervention_target_id"],
                empirical_stratum_id=stratum_id,
                regional_bundle_ids=stratum["bundle_ids"],
                package_id=None,
                component_target_ids=[],
                admissibility_status="ADMISSIBLE_EXACT_REGIONAL_INTERVENTION_TARGET",
                effective_universe_membership=True,
                target_identity_status=stratum["collision_status"],
                event_identity_status="QUALITATIVE_UNSPLIT_NOT_EVENT_TYPED",
                supersession=None,
                direct_population_measure_ids=stratum["direct_population_measure_ids"],
                context_measure_ids=stratum["context_population_measure_ids"],
                quarantine_ids=quarantine_by_stratum.get(stratum_id, []),
                event_ids=stratum["empirical_evidence_ids"],
                endpoint_ids=[],
                stage_ids=[],
                population_measure_role="regional_exact_stratum_population_or_context",
                oer_route_status_counts={},
                population_rankability_status=population_status,
                missing_core_fields=missing,
            )
        )
    return evaluations


def _validate_successor(
    artifact: Mapping[str, Any], canonical: Mapping[str, Any], regional_new_target_count: int
) -> dict[str, Any]:
    targets = artifact["language_targets"]
    legacy_count = len(canonical["language_targets"])
    if targets[:legacy_count] != canonical["language_targets"]:
        raise BuildError("legacy language targets are not an unchanged prefix")
    if artifact["legacy_population_measures"] != canonical["population_measures"]:
        raise BuildError("legacy population measures were altered")
    if artifact["legacy_package_interventions"] != canonical["package_interventions"]:
        raise BuildError("legacy package interventions were altered")
    if artifact["legacy_access_overlays"] != canonical["access_overlays"]:
        raise BuildError("legacy access overlays were altered")
    if artifact["source_registry"][: len(canonical["source_registry"])] != canonical["source_registry"]:
        raise BuildError("legacy source registry is not an unchanged prefix")
    if artifact["source_row_provenance"][: len(canonical["source_row_provenance"])] != canonical["source_row_provenance"]:
        raise BuildError("legacy provenance is not an unchanged prefix")
    if artifact["input_assignment"][: len(canonical["input_assignment"])] != canonical["input_assignment"]:
        raise BuildError("legacy assignments are not an unchanged prefix")
    target_ids = [row["language_target_id"] for row in targets]
    if len(target_ids) != len(set(target_ids)):
        raise BuildError("successor target IDs are not unique")
    if legacy_count != 945 or len(targets) != 945 + regional_new_target_count:
        raise BuildError("successor target count does not equal preserved legacy plus audited additions")
    for profile in artifact["package_profiles"]:
        if profile["measure_inheritance_policy"] != "NONE" or profile["population_measure_ids"]:
            raise BuildError(f"package measure inheritance detected: {profile['package_id']}")
    for row in artifact["candidate_evaluations"]:
        if row["score"] is not None or row["competition_rank"] is not None:
            raise BuildError(f"incomplete candidate received a score or rank: {row['candidate_id']}")
        if row["score_rankability_status"] != "INSUFFICIENT_PUBLIC_EVIDENCE":
            raise BuildError(f"candidate escaped fail-closed score status: {row['candidate_id']}")
    candidate_ids = [row["candidate_id"] for row in artifact["candidate_evaluations"]]
    if len(candidate_ids) != len(set(candidate_ids)):
        raise BuildError("candidate evaluation IDs are not unique")
    candidate_keys = {tuple(sorted(row)) for row in artifact["candidate_evaluations"]}
    if len(candidate_keys) != 1:
        raise BuildError("candidate kinds do not share one evaluation schema")
    candidate_kind_counts = Counter(row["candidate_kind"] for row in artifact["candidate_evaluations"])
    expected_candidate_kind_counts = {
        "language_target_summary": 969,
        "legacy_package_intervention_summary": 1011,
        "typed_endpoint_stage_package_event": 1035,
        "successor_package_profile_summary": len(artifact["package_profiles"]),
        "regional_empirical_stratum": 297,
    }
    if dict(candidate_kind_counts) != expected_candidate_kind_counts:
        raise BuildError(
            f"candidate coverage differs from the equal-treatment boundary: "
            f"{dict(candidate_kind_counts)} != {expected_candidate_kind_counts}"
        )
    if len(artifact["candidate_evaluations"]) != 3325:
        raise BuildError("expected exactly 3,325 equal-treatment candidate evaluations")
    event_candidate_ids = {
        row["event_ids"][0]
        for row in artifact["candidate_evaluations"]
        if row["candidate_kind"] == "typed_endpoint_stage_package_event"
    }
    if event_candidate_ids != {row["event_id"] for row in artifact["event_bindings"]}:
        raise BuildError("typed event candidates do not cover the event ledger exactly")
    legacy_package_candidate_ids = {
        row["package_id"]
        for row in artifact["candidate_evaluations"]
        if row["candidate_kind"] == "legacy_package_intervention_summary"
    }
    if legacy_package_candidate_ids != {
        row["package_intervention_id"] for row in canonical["package_interventions"]
    }:
        raise BuildError("legacy package candidates do not cover the preserved packages exactly")
    if any(row["resource_gap_values"] != {"low": None, "base": None, "high": None}
           for row in artifact["oer_gap_lane"]["route_statuses"]):
        raise BuildError("OER missingness was not preserved")
    prov_ids = [row["provenance_id"] for row in artifact["source_row_provenance"]]
    if len(prov_ids) != len(set(prov_ids)):
        raise BuildError("source provenance IDs are not unique")
    assignments = [
        (row["origin_file"], row["input_candidate_id"])
        for row in artifact["input_assignment"]
    ]
    if len(assignments) != len(set(assignments)):
        raise BuildError("input assignments are not unique by origin and candidate")
    source_ids = [row["source_id"] for row in artifact["source_registry"]]
    if len(source_ids) != len(set(source_ids)):
        raise BuildError("successor source IDs are not unique")
    empirical = artifact["regional_empirical_need_lane"]
    expected_empirical_counts = {
        "bundle_count": 4,
        "input_rows": 302,
        "unique_strata": 297,
        "collision_strata": 5,
        "numeric_person_rows": 204,
        "explicit_blank_rows": 98,
        "source_rows": 475,
    }
    for key, expected in expected_empirical_counts.items():
        if empirical["counts"][key] != expected:
            raise BuildError(f"empirical count mismatch for {key}: {empirical['counts'][key]} != {expected}")
    mappings = empirical["stratum_to_target_mapping"]
    if len(mappings) != 297:
        raise BuildError("empirical stratum-to-target mapping is incomplete")
    if len({row["stratum_id"] for row in mappings}) != 297 or len(
        {row["intervention_target_id"] for row in mappings}
    ) != 297:
        raise BuildError("empirical stratum-to-target mapping is not one-to-one")
    if any(
        row["canonical_language_target_inheritance"] != "NONE"
        for row in empirical["strata"]
    ):
        raise BuildError("an empirical stratum inherited into a canonical language target")
    upper_bound_rows = [
        row for row in artifact["population_evidence"]
        if row.get("source_values", {}).get("base") is None
        and row.get("source_values", {}).get("high") is not None
        and row.get("target_binding") == "CONTEXT_NO_INHERITANCE"
    ]
    if any(row["source_values"]["low"] == 0 for row in upper_bound_rows):
        raise BuildError("an upper-bound context fabricated a zero lower bound")
    status_counts = Counter(row["score_rankability_status"] for row in artifact["candidate_evaluations"])
    selection_counts = Counter(row["selection_status"] for row in artifact["candidate_evaluations"])
    return {
        "validation_passed": True,
        "legacy_language_targets_preserved": legacy_count,
        "regional_exact_targets_added": regional_new_target_count,
        "successor_language_targets": len(targets),
        "legacy_population_measures_preserved": len(canonical["population_measures"]),
        "legacy_package_interventions_preserved": len(canonical["package_interventions"]),
        "legacy_access_overlays_preserved": len(canonical["access_overlays"]),
        "legacy_source_records_preserved": len(canonical["source_registry"]),
        "legacy_provenance_rows_preserved": len(canonical["source_row_provenance"]),
        "legacy_assignment_rows_preserved": len(canonical["input_assignment"]),
        "successor_source_records": len(artifact["source_registry"]),
        "successor_provenance_rows": len(artifact["source_row_provenance"]),
        "successor_assignment_rows": len(artifact["input_assignment"]),
        "population_evidence_rows": len(artifact["population_evidence"]),
        "package_context_measure_rows": len(artifact["package_context_measures"]),
        "quarantined_evidence_rows": len(artifact["quarantined_evidence"]),
        "event_bindings": len(artifact["event_bindings"]),
        "package_profiles": len(artifact["package_profiles"]),
        "candidate_evaluations": len(artifact["candidate_evaluations"]),
        "candidate_kind_counts": dict(candidate_kind_counts),
        "score_rankability_status_counts": dict(sorted(status_counts.items())),
        "selection_status_counts": dict(sorted(selection_counts.items())),
        "non_null_scores": sum(row["score"] is not None for row in artifact["candidate_evaluations"]),
        "zero_imputed_scores": sum(row["score"] == 0 for row in artifact["candidate_evaluations"] if row["score"] is not None),
        "package_population_inheritance_rows": sum(bool(row["population_measure_ids"]) for row in artifact["package_profiles"]),
        "oer_route_status_rows": len(artifact["oer_gap_lane"]["route_statuses"]),
        "oer_numeric_resource_gap_rows": artifact["oer_gap_lane"]["counts"]["numeric_resource_gap_rows"],
        "regional_empirical_bundle_rows": empirical["counts"]["input_rows"],
        "regional_empirical_unique_strata": empirical["counts"]["unique_strata"],
        "regional_empirical_collision_strata": empirical["counts"]["collision_strata"],
        "regional_empirical_numeric_person_rows": empirical["counts"]["numeric_person_rows"],
        "regional_empirical_explicit_blank_rows": empirical["counts"]["explicit_blank_rows"],
        "regional_empirical_direct_person_rows": empirical["counts"]["direct_exact_stratum_person_rows"],
        "regional_empirical_context_or_quarantined_numeric_rows": empirical["counts"]["context_or_quarantined_numeric_rows"],
        "regional_empirical_intervention_target_mappings": len(mappings),
    }


def build_successor(
    base: Path,
    manifest_path: Path,
    *,
    allow_scorer_transition: bool = False,
) -> dict[str, Any]:
    base = base.resolve()
    manifest_path = manifest_path if manifest_path.is_absolute() else (base / manifest_path)
    manifest, identities, authority_binding = validate_pinned_inputs(
        base, manifest_path, allow_scorer_transition=allow_scorer_transition
    )
    canonical = read_json(base / "structured/canonical_universe_proposal.json")
    llps = read_json(base / "structured/large_language_population_strata_proposal.json")
    ledger = read_json(base / "structured/empirical_event_gap_ledger_v2.json")
    contract = read_json(base / manifest["contract"]["path"])
    if contract.get("$id") != "interlanguage/successor-universe-import-contract/2.0.0":
        raise BuildError("unsupported regional import contract")

    language_targets = deepcopy(canonical["language_targets"])
    canonical_target_ids = {row["language_target_id"] for row in canonical["language_targets"]}
    target_by_id = {row["language_target_id"]: row for row in language_targets}
    event_bindings, events_by_target, events_by_measure = normalize_event_ledger(ledger, canonical_target_ids)
    canonical_evidence, canonical_quarantine = adapt_canonical_population(
        canonical, events_by_measure, target_by_id
    )
    package_profiles: dict[str, dict[str, Any]] = {}
    occupied_measure_ids = {row["population_measure_id"] for row in canonical["population_measures"]}
    occupied_import_ids = {
        row["input_candidate_id"] for row in canonical["source_row_provenance"]
    }

    regional = adapt_regional_csvs(
        base,
        manifest,
        contract,
        language_targets,
        package_profiles,
        occupied_measure_ids,
        occupied_import_ids,
    )
    regional_evidence, regional_quarantine, regional_prov, regional_sources, batch_ids, new_targets = regional
    target_by_id = {row["language_target_id"]: row for row in language_targets}

    llps_evidence, package_context, llps_quarantine, llps_prov, llps_sources = adapt_llps(
        llps, target_by_id, package_profiles
    )
    for row in llps_evidence:
        if row["population_evidence_id"] in occupied_measure_ids:
            raise BuildError(f"LLPS measure collision: {row['population_evidence_id']}")
        occupied_measure_ids.add(row["population_evidence_id"])
    for row in llps_prov:
        key = row["input_candidate_id"]
        if key in occupied_import_ids:
            raise BuildError(f"LLPS import ID collision: {key}")
        occupied_import_ids.add(key)

    specialized_by_adapter: dict[str, list[Mapping[str, Any]]] = defaultdict(list)
    for spec in manifest["specialized_imports"]:
        specialized_by_adapter[spec["adapter"]].append(spec)
    allowed_specialized = {
        "signed_accessibility_register_v1",
        "oer_route_status_manifest_v2",
        "regional_empirical_need_bundle_v1",
    }
    unknown_specialized = set(specialized_by_adapter) - allowed_specialized
    if unknown_specialized:
        raise BuildError(f"unconsumed specialized import adapters: {sorted(unknown_specialized)}")
    if len(specialized_by_adapter["signed_accessibility_register_v1"]) != 1:
        raise BuildError("manifest must declare exactly one signed/accessibility register")
    if len(specialized_by_adapter["oer_route_status_manifest_v2"]) != 1:
        raise BuildError("manifest must declare exactly one OER route-status manifest")
    if len(specialized_by_adapter["regional_empirical_need_bundle_v1"]) != 4:
        raise BuildError("manifest must declare the four frozen regional empirical bundles")
    signed_lanes, signed_prov, signed_sources, signed_identity = adapt_signed_accessibility(
        base,
        specialized_by_adapter["signed_accessibility_register_v1"][0],
        target_by_id,
        {row["language_target_id"] for row in new_targets},
        occupied_measure_ids,
        occupied_import_ids,
    )
    oer_lane = adapt_oer_gap_lane(
        base, specialized_by_adapter["oer_route_status_manifest_v2"][0], canonical_target_ids
    )
    empirical_lane, empirical_prov, empirical_sources, empirical_quarantine = adapt_empirical_need_bundles(
        base,
        specialized_by_adapter["regional_empirical_need_bundle_v1"],
        contract,
        occupied_import_ids,
    )

    all_new_provenance = regional_prov + llps_prov + signed_prov + empirical_prov
    source_row_provenance = deepcopy(canonical["source_row_provenance"]) + all_new_provenance
    input_assignment = deepcopy(canonical["input_assignment"]) + [
        _assignment_from_provenance(row) for row in all_new_provenance
    ]
    source_registry = _append_sources_preserving_prefix(
        canonical["source_registry"],
        regional_sources + llps_sources + signed_sources + empirical_sources,
    )
    population_evidence = canonical_evidence + regional_evidence + llps_evidence
    quarantined = canonical_quarantine + regional_quarantine + llps_quarantine + empirical_quarantine
    candidate_evaluations = evaluate_candidates(
        language_targets,
        canonical["package_interventions"],
        package_profiles,
        population_evidence,
        signed_lanes["signed_language_person_measures"],
        quarantined,
        event_bindings,
        events_by_target,
        oer_lane,
        empirical_lane,
    )
    input_identities = {
        **identities,
        **{row["path"]: {"bytes": row["bytes"], "sha256": row["sha256"]} for row in batch_ids},
        signed_identity["path"]: {"bytes": signed_identity["bytes"], "sha256": signed_identity["sha256"]},
        signed_identity["validation_path"]: {
            "bytes": signed_identity["validation_bytes"],
            "sha256": signed_identity["validation_sha256"],
        },
        oer_lane["manifest_identity"]["path"]: {
            "bytes": oer_lane["manifest_identity"]["bytes"],
            "sha256": oer_lane["manifest_identity"]["sha256"],
        },
        oer_lane["validation_identity"]["path"]: {
            "bytes": oer_lane["validation_identity"]["bytes"],
            "sha256": oer_lane["validation_identity"]["sha256"],
        },
        **{
            path: {"bytes": row["bytes"], "sha256": row["sha256"]}
            for path, row in oer_lane["artifact_identities"].items()
        },
        **{
            identity["path"]: {"bytes": identity["bytes"], "sha256": identity["sha256"]}
            for receipt in empirical_lane["bundle_receipts"]
            for identity in receipt["identities"].values()
            if identity is not None
        },
    }
    artifact: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "artifact_status": "validated_successor_universe_not_a_ranking",
        "audit_date": AUDIT_DATE,
        "universe_version": UNIVERSE_VERSION,
        "ontology_version": ONTOLOGY_VERSION,
        "import_adapter_version": IMPORT_ADAPTER_VERSION,
        "authority_binding": authority_binding,
        "input_manifest": {
            "path": str(manifest_path.relative_to(base)).replace("\\", "/"),
            "bytes": manifest_path.stat().st_size,
            "sha256": sha256_file(manifest_path),
            "pinned_inputs": dict(sorted(input_identities.items())),
        },
        "merge_contract": {
            "mode": "APPEND_ONLY_ASSERT_EXISTING",
            "legacy_prefix_immutable": True,
            "manifest_genesis_sha256": MANIFEST_GENESIS["manifest_sha256"],
            "manifest_regional_prefix_sha256": MANIFEST_GENESIS["regional_prefix_sha256"],
            "manifest_specialized_set_sha256": MANIFEST_GENESIS["specialized_sha256"],
            "future_suffix_only": True,
            "implicit_directory_scan": False,
            "future_regional_inputs": "manifest-pinned closed-schema CSV batches only",
            "missing_numeric_policy": "PRESERVE_NULL_NEVER_ZERO",
            "macro_and_package_measure_inheritance": "FORBIDDEN",
            "lane_additivity": "population, proxy, overlay, and supply/policy/utilization lanes are nonadditive",
        },
        "language_targets": language_targets,
        "legacy_population_measures": deepcopy(canonical["population_measures"]),
        "legacy_package_interventions": deepcopy(canonical["package_interventions"]),
        "legacy_access_overlays": deepcopy(canonical["access_overlays"]),
        "source_registry": source_registry,
        "source_row_provenance": source_row_provenance,
        "input_assignment": input_assignment,
        "population_evidence": population_evidence,
        "package_profiles": [package_profiles[key] for key in sorted(package_profiles)],
        "package_context_measures": package_context,
        "quarantined_evidence": quarantined,
        "signed_accessibility_lane": {
            "identity": signed_identity,
            **signed_lanes,
            "additivity_policy": "SEPARATE_NONADDITIVE_LANES",
        },
        "event_bindings": event_bindings,
        "oer_gap_lane": oer_lane,
        "regional_empirical_need_lane": empirical_lane,
        "candidate_evaluations": candidate_evaluations,
        "known_corrections": {
            "putonghua": "invalid denominator-derived count quarantined; spoken target no longer carries Hans identity",
            "japan": "nationality and resident ceilings are separate context constructs; rounded adult low-skill pseudo-exact count quarantined",
            "turkish": "rounded speaker lower bound and resident ceiling are separate context constructs",
            "zh_hant": "Taiwan, Hong Kong, and Macao written-standard territorial ceilings are separate and not reader counts",
            "arabic": "territory/variety targets admitted without inherited national or package populations",
            "russian_federation": "reported ability and daily-use person rows are exact alternative overlapping endpoints; respondent denominator is context",
            "west_african_pidgin": "three missing exact targets admitted; six-variety package range remains package-only",
        },
    }
    artifact["validation"] = _validate_successor(artifact, canonical, len(new_targets))
    projected_roster = build_target_roster(artifact)
    projected_roster_bytes = _json_file_bytes(projected_roster)
    artifact["target_roster_binding"] = {
        "path": "structured/SUCCESSOR_TARGET_ROSTER_v2.json",
        "schema": projected_roster["schema"],
        "bytes": len(projected_roster_bytes),
        "sha256": hashlib.sha256(projected_roster_bytes).hexdigest(),
        "snapshot_id": projected_roster["snapshot_id"],
        "snapshot_payload_sha256": projected_roster["snapshot_payload_sha256"],
        "all_binding_row_count": projected_roster["target_selector"]["all_binding_row_count"],
        "effective_production_target_count": projected_roster["target_selector"][
            "effective_production_target_count"
        ],
    }
    artifact["payload_sha256"] = canonical_sha256(artifact)
    return artifact


def _json_file_bytes(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=False) + "\n").encode("utf-8")


def build_target_roster(artifact: Mapping[str, Any]) -> dict[str, Any]:
    """Project the scorer-independent, one-row-per-production-identity roster."""
    if artifact["validation"].get("validation_passed") is not True:
        raise BuildError("cannot freeze a roster from an invalid successor universe")
    language_evaluations = {
        row["language_target_id"]: row
        for row in artifact["candidate_evaluations"]
        if row["candidate_kind"] == "language_target_summary"
    }
    empirical_evaluations = {
        row["empirical_stratum_id"]: row
        for row in artifact["candidate_evaluations"]
        if row["candidate_kind"] == "regional_empirical_stratum"
    }
    rows: list[dict[str, Any]] = []
    for target in artifact["language_targets"]:
        target_id = target["language_target_id"]
        evaluation = language_evaluations[target_id]
        production_applicable = bool(
            evaluation["effective_universe_membership"]
            and evaluation["target_identity_status"] == "EXACT_TARGET"
            and target["exactness"] == "exact"
        )
        row = {
            "roster_target_id": target_id,
            "target_kind": "canonical_language_target",
            "language_target_id": target_id,
            "intervention_target_id": None,
            "empirical_stratum_id": None,
            "language_tags": list(target["language_tags"]),
            "language_variety_names": list(target["language_variety_names"]),
            "scripts_orthographies": list(target["scripts_orthographies"]),
            "territories_communities": list(target["territories_communities"]),
            "language_mode": target["language_mode"],
            "identity_assertions": [],
            "exactness": target["exactness"],
            "target_identity_status": evaluation["target_identity_status"],
            "effective_universe_membership": evaluation["effective_universe_membership"],
            "production_applicable": production_applicable,
            "package_or_overlay_inheritance": "NONE",
            "profile_binding_requirement": (
                "DIRECT_EXACT_PROFILE_OR_EXPLICIT_MISSING_UNRANKED"
                if production_applicable
                else "EXPLICIT_CONTEXT_OR_MISSING_UNRANKED_ONLY"
            ),
            "profile_binding_status": "UNBOUND_PENDING_COMPUTE_PROFILE_REGISTRY",
        }
        row["roster_row_sha256"] = canonical_sha256(row)
        rows.append(row)

    empirical_lane = artifact["regional_empirical_need_lane"]
    for target in empirical_lane["intervention_targets"]:
        stratum_id = target["stratum_id"]
        evaluation = empirical_evaluations[stratum_id]
        row = {
            "roster_target_id": target["intervention_target_id"],
            "target_kind": "regional_empirical_intervention_target",
            "language_target_id": None,
            "intervention_target_id": target["intervention_target_id"],
            "empirical_stratum_id": stratum_id,
            "language_tags": [],
            "language_variety_names": [],
            "scripts_orthographies": [],
            "territories_communities": [],
            "language_mode": None,
            "identity_assertions": deepcopy(target["identity_assertions"]),
            "exactness": "exact_regional_production_stratum",
            "target_identity_status": evaluation["target_identity_status"],
            "effective_universe_membership": evaluation["effective_universe_membership"],
            "production_applicable": True,
            "package_or_overlay_inheritance": target["package_or_overlay_inheritance"],
            "profile_binding_requirement": "DIRECT_EXACT_PROFILE_OR_EXPLICIT_MISSING_UNRANKED",
            "profile_binding_status": "UNBOUND_PENDING_COMPUTE_PROFILE_REGISTRY",
        }
        row["roster_row_sha256"] = canonical_sha256(row)
        rows.append(row)

    roster_ids = [row["roster_target_id"] for row in rows]
    if len(rows) != 1266 or len(roster_ids) != len(set(roster_ids)):
        raise BuildError("target roster is not the required 1,266 unique identities")
    if sum(row["target_kind"] == "canonical_language_target" for row in rows) != 969:
        raise BuildError("target roster does not preserve all 969 language identities")
    if sum(row["target_kind"] == "regional_empirical_intervention_target" for row in rows) != 297:
        raise BuildError("target roster does not preserve all 297 empirical intervention identities")
    production_applicable = [row for row in rows if row["production_applicable"]]
    if len(production_applicable) != 1157:
        raise BuildError("unexpected production-applicable target count")

    pinned = artifact["input_manifest"]["pinned_inputs"]
    roster_authority_paths = {
        "structured/canonical_universe_proposal.json",
        "structured/large_language_population_strata_proposal.json",
        "agent_reports/GLOBAL_LARGE_LANGUAGE_CONTROLS.md",
        "agent_reports/LARGE_COHORT_EQUAL_INCLUSION_AUDIT.md",
        "structured/SUCCESSOR_GLOBAL_UNIVERSE_REGIONAL_INPUTS_v2.csv",
        "structured/schema/SUCCESSOR_UNIVERSE_IMPORT_CONTRACT_v2.json",
    }
    for bundle in empirical_lane["bundle_receipts"]:
        for identity in bundle["identities"].values():
            if identity is not None:
                roster_authority_paths.add(identity["path"])
    roster_authorities = {
        path: pinned[path]
        for path in sorted(roster_authority_paths)
    }
    body: dict[str, Any] = {
        "schema": "interlanguage/successor-target-roster/2.0.0",
        "universe_version": artifact["universe_version"],
        "ontology_version": artifact["ontology_version"],
        "audit_date": AUDIT_DATE,
        "status": "DATA_ROSTER_FROZEN_EXECUTABLE_BINDING_PENDING",
        "scorer_identity_included": False,
        "schema_contract_identity_included": False,
        "unmanifested_inputs_imported": False,
        "target_selector": {
            "all_binding_rows": "every roster_targets row",
            "all_binding_row_count": len(rows),
            "effective_production_selector": "production_applicable == true",
            "effective_production_target_count": len(production_applicable),
            "effective_language_target_count": sum(
                row["production_applicable"] and row["target_kind"] == "canonical_language_target"
                for row in rows
            ),
            "effective_empirical_intervention_target_count": sum(
                row["production_applicable"]
                and row["target_kind"] == "regional_empirical_intervention_target"
                for row in rows
            ),
            "binding_outcome_contract": "one row per roster target: direct exact profile or explicit missing/unranked",
        },
        "counts": {
            "roster_targets": len(rows),
            "preserved_legacy_language_targets": 945,
            "audited_appended_language_targets": 24,
            "language_targets": 969,
            "production_applicable_language_targets": 860,
            "context_or_superseded_language_targets": 109,
            "regional_empirical_input_rows": empirical_lane["counts"]["input_rows"],
            "regional_empirical_unique_strata": empirical_lane["counts"]["unique_strata"],
            "regional_empirical_intervention_targets": 297,
            "regional_empirical_collision_strata": 5,
            "production_applicable_targets": len(production_applicable),
            "expected_successor_evaluation_rows": artifact["validation"]["candidate_evaluations"],
        },
        "expected_evaluation_kind_counts": deepcopy(artifact["validation"]["candidate_kind_counts"]),
        "roster_authority_identities": roster_authorities,
        "collision_dispositions": deepcopy(empirical_lane["collision_dispositions"]),
        "stratum_to_target_mapping": deepcopy(empirical_lane["stratum_to_target_mapping"]),
        "roster_targets": rows,
    }
    snapshot_payload_sha256 = canonical_sha256(body)
    body["snapshot_id"] = f"successor-target-roster:sha256:{snapshot_payload_sha256}"
    body["snapshot_payload_sha256"] = snapshot_payload_sha256
    return body


def write_target_roster_snapshot(
    artifact: Mapping[str, Any],
    *,
    base: Path,
    roster_path: Path,
    receipt_path: Path,
) -> dict[str, Any]:
    roster = build_target_roster(artifact)
    roster_path = roster_path if roster_path.is_absolute() else base / roster_path
    receipt_path = receipt_path if receipt_path.is_absolute() else base / receipt_path
    roster_path.parent.mkdir(parents=True, exist_ok=True)
    receipt_path.parent.mkdir(parents=True, exist_ok=True)
    roster_path.write_bytes(_json_file_bytes(roster))
    roster_identity = {
        "path": "structured/SUCCESSOR_TARGET_ROSTER_v2.json",
        "bytes": roster_path.stat().st_size,
        "sha256": sha256_file(roster_path),
    }
    receipt = {
        "schema": "interlanguage/successor-target-roster-receipt/2.0.0",
        "audit_date": AUDIT_DATE,
        "validation_passed": True,
        "status": "DATA_ROSTER_FROZEN_EXECUTABLE_BINDING_PENDING",
        "snapshot_id": roster["snapshot_id"],
        "snapshot_payload_sha256": roster["snapshot_payload_sha256"],
        "roster_artifact": roster_identity,
        "builder_identity_at_freeze": {
            "path": "scripts/build_successor_global_universe.py",
            "bytes": (base / "scripts/build_successor_global_universe.py").stat().st_size,
            "sha256": sha256_file(base / "scripts/build_successor_global_universe.py"),
        },
        "counts": roster["counts"],
        "target_selector": roster["target_selector"],
        "scorer_binding_pending": True,
        "combined_successor_receipt_issued": False,
        "paper_or_logbook_modified": False,
    }
    receipt_path.write_bytes(_json_file_bytes(receipt))
    return receipt


def render_report(
    artifact: Mapping[str, Any],
    output_sha256: str,
    roster_identity: Mapping[str, Any],
) -> str:
    validation = artifact["validation"]
    signed = artifact["signed_accessibility_lane"]["identity"]
    oer = artifact["oer_gap_lane"]["counts"]
    empirical = artifact["regional_empirical_need_lane"]["counts"]
    candidate_kinds = validation["candidate_kind_counts"]
    inputs = artifact["input_manifest"]["pinned_inputs"]
    input_lines = "\n".join(
        (
            f"- `{path}` — binding `{row['binding_status']}`; bytes and SHA-256 intentionally null"
            if row.get("binding_status")
            else f"- `{path}` — {row['bytes']:,} bytes; SHA-256 `{row['sha256']}`"
        )
        for path, row in inputs.items()
    )
    return f"""# Successor global-universe builder v2

Status: **PASS** — deterministic append-only build; universe artifact, not a published ranking.

## Outcome

The builder preserves all {validation['legacy_language_targets_preserved']} legacy language-target objects as an unchanged prefix and appends {validation['regional_exact_targets_added']} audited exact targets, yielding {validation['successor_language_targets']} language targets. It applies one closed admissibility/rankability vocabulary to every candidate: {candidate_kinds['language_target_summary']} language summaries, {candidate_kinds['legacy_package_intervention_summary']} preserved package summaries, {candidate_kinds['typed_endpoint_stage_package_event']} typed endpoint/stage/package events, {candidate_kinds['successor_package_profile_summary']} successor package profiles, and {candidate_kinds['regional_empirical_stratum']} exact regional intervention strata. All {validation['candidate_evaluations']} candidates remain explicitly `UNRANKED_INSUFFICIENT`; there are {validation['non_null_scores']} non-null scores and {validation['zero_imputed_scores']} imputed zero scores.

The legacy population ({validation['legacy_population_measures_preserved']} rows), package ({validation['legacy_package_interventions_preserved']} rows), accessibility-overlay ({validation['legacy_access_overlays_preserved']} rows), source ({validation['legacy_source_records_preserved']} rows), provenance ({validation['legacy_provenance_rows_preserved']} rows), and assignment ({validation['legacy_assignment_rows_preserved']} rows) payloads remain byte-semantically unchanged within their preserved output sections/prefixes.

## Corrections and separation rules

- The invalid Putonghua count derived from 80.72% and an incompatible all-ages denominator is quarantined. A clean spoken Putonghua identity is admitted without assigning Hans to speech.
- Japan's nationality ceiling and resident ceiling, and Turkey's rounded speaker lower bound and resident ceiling, are stored as separate context constructs rather than false intervals. Japan's rounded adult low-skill pseudo-exact derivation is quarantined.
- Taiwan, Hong Kong, and Macao `zh-Hant` written-standard ceilings are distinct territorial context rows, never reader counts.
- Russian Federation reported ability (134,319,233) and daily use (132,317,159) are exact alternative, overlapping person endpoints; the 135,125,671 response denominator remains context-only.
- Arabic variety/territory targets and the three added West African Pidgin targets receive no national, macro, bridge, or package-total inheritance.
- Every package has `measure_inheritance_policy=NONE`; package population-inheritance violations: {validation['package_population_inheritance_rows']}.
- Person normalization and event endpoint/stage typing are preserved in {validation['event_bindings']} event bindings.

## Signed/accessibility register

All 35 validated rows are imported into nonadditive lanes: {signed['lane_counts']['signed_language_person_measures']} signed-language person measures ({signed['valid_direct_person_measures']} valid direct and {signed['qualified_person_measures']} qualified/context-only), {signed['lane_counts']['signed_language_proxy_and_gap_rows']} proxy/data-gap rows, {signed['lane_counts']['accessibility_overlays']} accessibility overlays, and {signed['lane_counts']['accessibility_supply_policy_and_utilization']} supply/policy/utilization rows. Person-valued overlays remain overlays; proxy rows never become signer counts; non-person supply and rate units are never normalized to persons.

## OER route-status lane

The import binds {oer['exact_targets']} preserved exact targets across {oer['matrix_rows']} canon cells ({oer['stages']} stages × {oer['subjects']} subjects; {oer['canon_cells_per_target']} per target) and verifies {oer['query_rows']} query-manifest rows. It retains {oer['resource_found_rows']} distinct functional-route statuses and {oer['unresolved_rows']} unresolved statuses, but imports no query detail, awards no repository-count curriculum credit, and carries {oer['numeric_resource_gap_rows']} numeric resource-gap scalars. The exact grade profile is F0={oer['f0_rows']}, F1={oer['f1_rows']}, F2={oer['f2_rows']}, F3={oer['f3_rows']}, F4={oer['f4_rows']}. Every resource-gap low/base/high remains null, so this lane has no score effect.

## Four-bundle empirical join and target roster

The frozen Africa, Asia, Americas/Europe, and Oceania/Central Asia bundles contribute {empirical['input_rows']} evidence rows over {empirical['unique_strata']} unique production strata. The join preserves {empirical['numeric_person_rows']} numeric-person rows and {empirical['explicit_blank_rows']} explicit missing rows; {empirical['direct_exact_stratum_person_rows']} numeric rows qualify as exact direct stratum evidence and {empirical['context_or_quarantined_numeric_rows']} remain context or quarantine. It emits one distinct intervention target per stratum and never inherits a coarser language or package total.

Five cross-bundle collisions are explicit and order-independent: `apd-Arab-SD`, `arz-Arab-EG`, `mey-Arab-MR`, and `shu-Arab-TD` preserve both evidence records while quarantining the Asia production-identity assertion; `mg-Latn-MG` preserves compatible, distinct, nonadditive spoken-ability and written-exposure constructs. No collision is resolved by bundle order.

The scorer-independent roster is `{roster_identity['path']}` ({roster_identity['bytes']:,} bytes; SHA-256 `{roster_identity['sha256']}`), snapshot `{roster_identity['snapshot_id']}`. It contains 1,266 one-row-per-identity bindings: 969 language targets and 297 empirical intervention targets. The effective production selector `production_applicable == true` yields 1,157 targets (860 language and 297 empirical); every roster identity requires a direct exact compute profile or an explicit missing/unranked binding.

## Schema-driven future imports

Regional batches are accepted only when explicitly path/byte/hash-pinned in the versioned manifest and exactly match their declared closed schema: the 34-column successor CSV or the 25-column empirical-need bundle with its declared source/validation schema. Unknown columns, pseudo-null tokens, undeclared collisions, identity mutation, deletes, overwrites, implicit directory scans, and score fields fail closed. New batches append; prior batch identities and records are not rewritten.

## Validation counts

- Population-evidence rows evaluated: {validation['population_evidence_rows']}
- Package-context measure rows: {validation['package_context_measure_rows']}
- Quarantined evidence rows: {validation['quarantined_evidence_rows']}
- Package profiles: {validation['package_profiles']}
- Successor provenance / assignment rows: {validation['successor_provenance_rows']} / {validation['successor_assignment_rows']}
- OER route-status rows: {validation['oer_route_status_rows']}
- Output SHA-256: `{output_sha256}`
- Payload SHA-256 (canonical JSON excluding only its own field at calculation time): `{artifact['payload_sha256']}`

## Caveats

This artifact is a universe and evidence-disposition build, not a prioritization result. The legacy event ledger marks no event rankable now; the OER lane has no numeric resource-gap scalars; and new inclusion-only targets lack complete need/access factors and common draws. Accordingly, missing evidence remains null and unranked rather than being treated as zero, high scarcity, or an unfavorable score. Territorial ceilings, language ability, daily use, home use, restricted-population knowledge, accessibility need, service use, supply rates, and policy statements remain incompatible/nonadditive constructs.

## Pinned input identities

{input_lines}
"""


def write_outputs(
    artifact: Mapping[str, Any],
    *,
    base: Path,
    output_path: Path,
    report_path: Path,
    receipt_path: Path,
) -> dict[str, Any]:
    if not artifact["authority_binding"]["final_artifact_allowed"]:
        raise BuildError("authority state does not permit a universe artifact")
    if (
        artifact["authority_binding"]["scorer_binding_status"]
        == "PENDING_NO_NORMATIVE_SCORER_HASH_BOUND"
        and any(row["score"] is not None for row in artifact["candidate_evaluations"])
    ):
        raise BuildError("a scorer-pending universe cannot contain scores")
    output_path = output_path if output_path.is_absolute() else base / output_path
    report_path = report_path if report_path.is_absolute() else base / report_path
    receipt_path = receipt_path if receipt_path.is_absolute() else base / receipt_path
    output_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    receipt_path.parent.mkdir(parents=True, exist_ok=True)
    roster_path = base / DEFAULT_ROSTER
    roster_receipt_path = base / DEFAULT_ROSTER_RECEIPT
    if not roster_path.is_file() or not roster_receipt_path.is_file():
        raise BuildError("frozen target roster or receipt is missing")
    frozen_roster = read_json(roster_path)
    expected_roster = build_target_roster(artifact)
    if frozen_roster != expected_roster:
        raise BuildError("frozen target roster no longer matches the successor target projection")
    frozen_roster_receipt = read_json(roster_receipt_path)
    roster_identity = {
        "path": "structured/SUCCESSOR_TARGET_ROSTER_v2.json",
        "bytes": roster_path.stat().st_size,
        "sha256": sha256_file(roster_path),
        "snapshot_id": frozen_roster["snapshot_id"],
    }
    if (
        frozen_roster_receipt.get("roster_artifact", {}).get("sha256") != roster_identity["sha256"]
        or frozen_roster_receipt.get("snapshot_id") != roster_identity["snapshot_id"]
    ):
        raise BuildError("target roster receipt does not bind the frozen roster")
    output_path.write_bytes(_json_file_bytes(artifact))
    output_sha = sha256_file(output_path)
    report_path.write_text(
        render_report(artifact, output_sha, roster_identity), encoding="utf-8", newline="\n"
    )
    receipt = {
        "schema": "interlanguage/successor-universe-build-receipt/2.0.0",
        "audit_date": AUDIT_DATE,
        "validation_passed": True,
        "builder": {
            "path": "scripts/build_successor_global_universe.py",
            "bytes": (base / "scripts/build_successor_global_universe.py").stat().st_size,
            "sha256": sha256_file(base / "scripts/build_successor_global_universe.py"),
        },
        "input_manifest": artifact["input_manifest"],
        "artifacts": [
            {
                "path": "structured/canonical_universe_successor_v2.json",
                "bytes": output_path.stat().st_size,
                "sha256": output_sha,
            },
            {
                "path": "agent_reports/SUCCESSOR_GLOBAL_UNIVERSE_BUILDER_v2.md",
                "bytes": report_path.stat().st_size,
                "sha256": sha256_file(report_path),
            },
        ],
        "counts": artifact["validation"],
        "target_roster_binding": {
            **roster_identity,
            "receipt_path": "qa/SUCCESSOR_TARGET_ROSTER_RECEIPT_20260901_v2.json",
            "receipt_bytes": roster_receipt_path.stat().st_size,
            "receipt_sha256": sha256_file(roster_receipt_path),
        },
        "payload_sha256": artifact["payload_sha256"],
        "authority_binding": artifact["authority_binding"],
        "rankings_produced": 0,
        "publication_performed": False,
        "paper_or_logbook_modified": False,
    }
    receipt_path.write_bytes(_json_file_bytes(receipt))
    return receipt


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base", type=Path, default=DEFAULT_BASE)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    parser.add_argument("--receipt", type=Path, default=DEFAULT_RECEIPT)
    parser.add_argument("--roster-output", type=Path, default=DEFAULT_ROSTER)
    parser.add_argument("--roster-receipt", type=Path, default=DEFAULT_ROSTER_RECEIPT)
    parser.add_argument("--check-only", action="store_true")
    parser.add_argument(
        "--write-roster",
        action="store_true",
        help="write the scorer-independent frozen target roster and its receipt",
    )
    parser.add_argument(
        "--allow-scorer-transition",
        action="store_true",
        help="freeze universe data with scorer/schema/full-receipt authority explicitly pending and non-normative",
    )
    args = parser.parse_args(argv)
    artifact = build_successor(
        args.base,
        args.manifest,
        allow_scorer_transition=args.allow_scorer_transition,
    )
    if args.check_only and args.write_roster:
        raise BuildError("--check-only and --write-roster are mutually exclusive")
    if args.check_only:
        print(json.dumps({"validation": artifact["validation"], "payload_sha256": artifact["payload_sha256"]}, indent=2))
        return 0
    if args.write_roster:
        roster_receipt = write_target_roster_snapshot(
            artifact,
            base=args.base.resolve(),
            roster_path=args.roster_output,
            receipt_path=args.roster_receipt,
        )
        print(json.dumps({"status": "PASS", **roster_receipt}, indent=2))
        return 0
    receipt = write_outputs(
        artifact,
        base=args.base.resolve(),
        output_path=args.output,
        report_path=args.report,
        receipt_path=args.receipt,
    )
    print(json.dumps({"status": "PASS", "counts": artifact["validation"], "artifacts": receipt["artifacts"]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
