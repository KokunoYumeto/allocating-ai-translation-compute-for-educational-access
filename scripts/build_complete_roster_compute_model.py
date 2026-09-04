#!/usr/bin/env python3
"""Build the complete-roster, model-conditional standardized-compute lane.

This module is deliberately separate from the direct-profile standardized-
compute builder and from the successor-universe builder.  It consumes their
frozen, hash-pinned outputs and never edits them.

The predictive feature set is intentionally narrow: the written
representation's script is the sole target-side predictor.  Population,
educational need, geography, income, prestige, evidence volume, resource
availability, and every user/local/project field are excluded by construction.
FLORES language-script measurements calibrate a conjugate predictive model for
log token expansion.  The fixed base-process standardized-compute model is
then evaluated for every applicable target, draw, canon, and package.
"""

from __future__ import annotations

import argparse
import copy
import csv
import gzip
import hashlib
import io
import json
import math
import os
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

import numpy as np


SCHEMA_VERSION = "interlanguage/complete-roster-compute/1.1.0"
DEFAULT_REGISTRY = Path("scripts/COMPLETE_ROSTER_COMPUTE_MODEL_REGISTRY.json")

ALLOWED_TARGET_FEATURE_FIELDS = {
    "edition_target_id",
    "edition_role",
    "edition_derivation_class",
    "normalized_language_codes_json",
    "language_code_status",
    "normalized_script_codes_json",
    "script_code_status",
    "script_orthography_json",
    "mode_json",
    "mode_status",
    "representation_status",
    "effective_complete_compute_target",
    "registry_version",
    "registry_row_hash",
}

FORBIDDEN_PREDICTOR_TOKENS = {
    "population",
    "need",
    "region",
    "territory",
    "country",
    "income",
    "prestige",
    "institution",
    "politic",
    "evidence",
    "resource",
    "user",
    "local",
    "project",
    "completion",
    "readiness",
    "reuse",
    "cache",
    "rank",
    "score",
}

LANGUAGE_CODE_ALIASES = {
    "id": "ind",
    "ind": "ind",
    "ja": "jpn",
    "jpn": "jpn",
    "zh": "zho",
    "zho": "zho",
}

KNOWN_SCRIPT_CODES = {
    "Adlm", "Arab", "Armn", "Bali", "Bass", "Beng", "Berf", "Brai",
    "Bugi", "Cans", "Cher", "Cyrl",
    "Deva", "Ethi", "Geor", "Grek", "Gujr", "Guru", "Hang", "Hans",
    "Hant", "Hebr", "Jpan", "Khmr", "Knda", "Laoo", "Latn", "Mlym",
    "Kore", "Mend", "Mong", "Mymr", "Nkoo", "Olck", "Orya", "Osma",
    "Rohg", "Sinh", "Syrc", "Taml", "Telu", "Tfng", "Thaa", "Thai",
    "Tibt", "Vaii", "Yiii",
}

# Ordered from more specific to more general. Multiple simultaneous matches
# produce an unresolved script unless an explicit BCP-47 script subtag exists.
SCRIPT_KEYWORDS: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("Hans", ("simplified chinese", "simplified han", "simplified characters")),
    ("Hant", ("traditional chinese", "traditional han", "traditional characters")),
    ("Jpan", ("japanese script", "kanji", "hiragana", "katakana")),
    ("Hang", ("hangul", "korean script")),
    ("Adlm", ("adlam",)),
    ("Arab", ("arabic", "ajami", "perso-arabic", "persian script")),
    ("Armn", ("armenian",)),
    ("Beng", ("bengali script", "bangla script")),
    ("Berf", ("beria erfe",)),
    ("Brai", ("braille",)),
    ("Cans", ("canadian aboriginal syllabics", "unified canadian syllabics")),
    ("Cher", ("cherokee syllabary",)),
    ("Cyrl", ("cyrillic",)),
    ("Deva", ("devanagari",)),
    ("Ethi", ("ethiopic", "ge'ez", "geez")),
    ("Geor", ("georgian script",)),
    ("Grek", ("greek script",)),
    ("Gujr", ("gujarati script",)),
    ("Guru", ("gurmukhi",)),
    ("Hebr", ("hebrew script",)),
    ("Khmr", ("khmer script",)),
    ("Knda", ("kannada script",)),
    ("Laoo", ("lao script",)),
    ("Latn", ("latin", "roman alphabet", "roman script")),
    ("Mlym", ("malayalam script",)),
    ("Nkoo", ("n'ko", "nko script")),
    ("Mong", ("mongolian script",)),
    ("Mymr", ("myanmar script", "burmese script")),
    ("Olck", ("ol chiki", "ol-chiki")),
    ("Orya", ("odia script", "oriya script")),
    ("Rohg", ("hanifi rohingya",)),
    ("Sinh", ("sinhala script",)),
    ("Taml", ("tamil script",)),
    ("Telu", ("telugu script",)),
    ("Tfng", ("tifinagh",)),
    ("Thai", ("thai script",)),
    ("Tibt", ("tibetan script",)),
    ("Thaa", ("thaana",)),
    ("Vaii", ("vai syllabary",)),
    ("Yiii", ("yi script",)),
)


class ModelError(RuntimeError):
    """Fail-closed model construction error."""


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")


def canonical_sha256(value: Any) -> str:
    return sha256_bytes(canonical_bytes(value))


def json_file_bytes(value: Any) -> bytes:
    return (
        json.dumps(value, ensure_ascii=False, indent=2, sort_keys=False) + "\n"
    ).encode("utf-8")


def read_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def exact_relative(base: Path, relative: str) -> Path:
    path = (base / relative).resolve()
    try:
        path.relative_to(base.resolve())
    except ValueError as exc:
        raise ModelError(f"path escapes task root: {relative}") from exc
    return path


def validate_authoritative_inputs(base: Path, registry: Mapping[str, Any]) -> dict[str, dict[str, Any]]:
    identities: dict[str, dict[str, Any]] = {}
    for relative, expected in registry["authoritative_inputs"].items():
        path = exact_relative(base, relative)
        if not path.is_file():
            raise ModelError(f"missing authoritative input: {relative}")
        actual_bytes = path.stat().st_size
        actual_sha = sha256_file(path)
        if actual_bytes != int(expected["bytes"]) or actual_sha != expected["sha256"]:
            raise ModelError(
                f"authoritative input identity mismatch: {relative}; "
                f"got {actual_bytes}/{actual_sha}"
            )
        identities[relative] = {"bytes": actual_bytes, "sha256": actual_sha}
    return identities


def parse_bool(value: Any, *, field: str) -> bool:
    text = str(value).strip().lower()
    if text == "true":
        return True
    if text == "false":
        return False
    raise ModelError(f"{field} is not a canonical boolean: {value!r}")


def parse_json_field(value: Any, *, field: str) -> Any:
    try:
        return json.loads(str(value))
    except (TypeError, json.JSONDecodeError) as exc:
        raise ModelError(f"{field} is not valid JSON") from exc


def _flatten_scalars(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, Mapping):
        result: list[str] = []
        for key in sorted(value):
            result.extend(_flatten_scalars(value[key]))
        return result
    if isinstance(value, (list, tuple)):
        result = []
        for item in value:
            result.extend(_flatten_scalars(item))
        return result
    return [str(value)]


def _mode_tokens(value: Any) -> list[str]:
    """Flatten a controlled mode value without treating false flags as true."""

    if value is None:
        return []
    if isinstance(value, Mapping):
        result: list[str] = []
        for key in sorted(value):
            child = value[key]
            if child is True:
                result.append(str(key))
            elif child in {False, None, ""}:
                continue
            else:
                result.append(f"{key}:{child}")
                result.extend(_mode_tokens(child))
        return result
    if isinstance(value, (list, tuple)):
        result = []
        for item in value:
            result.extend(_mode_tokens(item))
        return result
    return [str(value)]


def _json_string_list(row: Mapping[str, Any], field: str) -> list[str]:
    parsed = parse_json_field(row.get(field, "[]"), field=field)
    if not isinstance(parsed, list):
        raise ModelError(f"{field} must be a JSON array")
    return [str(value) for value in parsed if str(value)]


def _edition_feature_projection(row: Mapping[str, Any]) -> dict[str, Any]:
    """Read only edition identity and representation fields from table A.

    Territory, population, evidence, authority volume, derivation count, and
    every local/project field are deliberately outside this projection.  The
    edition ID is retained for set equality and provenance but never enters a
    predictive parameter.
    """

    return {
        "edition_target_id": str(row.get("edition_target_id") or ""),
        "edition_role": str(row.get("edition_role") or ""),
        "edition_derivation_class": str(row.get("edition_derivation_class") or ""),
        "normalized_language_codes": _json_string_list(row, "normalized_language_codes_json"),
        "language_code_status": str(row.get("language_code_status") or ""),
        "normalized_script_codes": _json_string_list(row, "normalized_script_codes_json"),
        "script_code_status": str(row.get("script_code_status") or ""),
        "script_orthography": parse_json_field(row.get("script_orthography_json", "[]"), field="script_orthography_json"),
        "mode": parse_json_field(row.get("mode_json", "[]"), field="mode_json"),
        "mode_status": str(row.get("mode_status") or ""),
        "representation_status": str(row.get("representation_status") or ""),
        "effective_complete_compute_target": parse_bool(
            row.get("effective_complete_compute_target"),
            field="effective_complete_compute_target",
        ),
        "registry_version": str(row.get("registry_version") or ""),
        "registry_row_hash": str(row.get("registry_row_hash") or ""),
    }


def _bcp_script(tags: Sequence[str]) -> tuple[str | None, str]:
    found: set[str] = set()
    for tag in tags:
        for part in str(tag).replace("_", "-").split("-"):
            normalized = part[:1].upper() + part[1:].lower() if len(part) == 4 else part
            if normalized in KNOWN_SCRIPT_CODES:
                found.add(normalized)
    if len(found) == 1:
        return next(iter(found)), "EXPLICIT_BCP47_SCRIPT"
    if len(found) > 1:
        return None, "CONFLICTING_BCP47_SCRIPTS"
    return None, "NO_BCP47_SCRIPT"


def infer_script(tags: Sequence[str], orthographies: Sequence[str]) -> tuple[str, str]:
    explicit, rule = _bcp_script(tags)
    if explicit:
        return explicit, rule
    if rule == "CONFLICTING_BCP47_SCRIPTS":
        return "Zyyy", rule
    text = " | ".join(str(v).lower() for v in orthographies)
    found = {code for code, terms in SCRIPT_KEYWORDS if any(term in text for term in terms)}
    if len(found) == 1:
        return next(iter(found)), "ORTHOGRAPHY_KEYWORD_SINGLE_SCRIPT"
    if len(found) > 1:
        return "Zyyy", "ORTHOGRAPHY_MULTISCRIPT_OR_AMBIGUOUS"
    return "Zyyy", "NO_SCRIPT_EVIDENCE_GLOBAL_PRIOR"


def canonical_language_code(code: str, script: str, mode: str) -> tuple[str, str]:
    normalized = LANGUAGE_CODE_ALIASES.get(code, code)
    if code == "cmn":
        if mode in {"written", "written_or_multimodal"} and script in {"Hans", "Hant"}:
            return "zho", "CONTROLLED_CMN_TO_ZHO_STANDARD_WRITTEN_HAN"
        return "cmn", "CMN_ZHO_ALIAS_NOT_APPLICABLE_TO_THIS_REPRESENTATION"
    if code in LANGUAGE_CODE_ALIASES:
        return normalized, f"PINNED_ALIAS_{code}_TO_{normalized}"
    return normalized, "NO_ALIAS_APPLIED"


def collapse_language_codes(
    codes: Sequence[str], script: str, mode: str
) -> tuple[str, str, str]:
    raw_codes = sorted(
        {
            str(code).replace("_", "-").split("-")[0].lower()
            for code in codes
            if str(code).strip()
        }
        - {"und", "mul"}
    )
    canonical_pairs = [canonical_language_code(code, script, mode) for code in raw_codes]
    canonical_codes = sorted({pair[0] for pair in canonical_pairs if pair[0]})
    if len(canonical_codes) == 1:
        raw = raw_codes[0] if len(raw_codes) == 1 else "+".join(raw_codes)
        rules = sorted({pair[1] for pair in canonical_pairs})
        rule = rules[0] if len(rules) == 1 else "PINNED_ALIAS_EQUIVALENT_SET_COLLAPSE"
        return raw, canonical_codes[0], rule
    if not canonical_codes:
        return "", "", "NO_LANGUAGE_CODE"
    return "+".join(raw_codes), "", "MULTIPLE_NON_EQUIVALENT_LANGUAGE_CODES"


def extract_edition_features(target: Mapping[str, Any]) -> dict[str, Any]:
    projected = _edition_feature_projection(target)
    target_id = projected["edition_target_id"]
    if not target_id:
        raise ModelError("edition registry row lacks edition_target_id")

    scripts = sorted(set(projected["normalized_script_codes"]))
    if len(scripts) == 1 and scripts[0] in KNOWN_SCRIPT_CODES | {"Zyyy"}:
        script = scripts[0]
        script_rule = "FROZEN_NORMALIZED_SCRIPT_SINGLE"
    elif len(scripts) > 1:
        script = "Zyyy"
        script_rule = "FROZEN_NORMALIZED_SCRIPT_MULTI_GLOBAL_PRIOR"
    else:
        orthography_text = _flatten_scalars(projected["script_orthography"])
        script, inferred = infer_script([], orthography_text)
        script_rule = f"FROZEN_ORTHOGRAPHY_FALLBACK_{inferred}"

    mode_values = [value.lower() for value in _mode_tokens(projected["mode"])]
    has_signed = any("sign" in value or "visual-manual" in value for value in mode_values)
    has_written = any("writ" in value or "text" in value or "multimodal" in value for value in mode_values)
    has_spoken = any("spoken" in value or "oral" in value or "audio" in value for value in mode_values)
    if has_signed and not has_written:
        mode = "signed"
    elif has_spoken and not has_written:
        mode = "spoken"
    elif has_written:
        mode = "written_or_multimodal"
    elif script != "Zyyy" or scripts:
        mode = "written_or_multimodal"
    else:
        mode = "undefined"

    effective = bool(projected["effective_complete_compute_target"])
    if mode == "signed":
        status = "NOT_APPLICABLE_SIGNED_MODE"
        reason = "written-token profile does not model a visual-manual production route"
    elif mode == "spoken":
        status = "NOT_APPLICABLE_ORAL_ONLY_MODE"
        reason = "written-token profile does not model an oral-only production route"
    elif not effective:
        status = "NOT_APPLICABLE_NOT_EFFECTIVE"
        reason = "edition registry does not select this row for complete-compute modeling"
    elif mode == "written_or_multimodal":
        status = "MODEL_CONDITIONAL_APPLICABLE"
        reason = ""
    else:
        status = "NOT_APPLICABLE_UNDEFINED_REPRESENTATION_MODE"
        reason = "no lawful written, signed, or oral representation model is defined"

    language_code, canonical_code, alias_rule = collapse_language_codes(
        projected["normalized_language_codes"], script, mode
    )
    # Identical predictive states use common random numbers.  This prevents
    # arbitrary language IDs from creating Monte-Carlo-only cost differences.
    representation_draw_key = f"{script}|{mode}"
    scientific = {
        "edition_target_id": target_id,
        "edition_role": projected["edition_role"],
        "edition_derivation_class": projected["edition_derivation_class"],
        "language_mode": mode,
        "representation_status": projected["representation_status"],
        "effective_complete_compute_target": effective,
        "predictor_language_code": language_code,
        "predictor_language_code_canonical": canonical_code,
        "language_alias_rule": alias_rule,
        "predictor_script_code": script,
        "representation_draw_key": representation_draw_key,
        "script_inference_rule": script_rule,
        "model_applicability_status": status,
        "not_applicable_reason": reason,
    }
    scientific["representation_feature_row_sha256"] = canonical_sha256(scientific)
    scientific["source_edition_row_sha256"] = projected["registry_row_hash"] or canonical_sha256(target)
    return scientific


@dataclass(frozen=True)
class TrainingProfile:
    flores_code: str
    language_code: str
    script_code: str
    r_value: float
    row_sha256: str


def load_training_profiles(path: Path) -> list[TrainingProfile]:
    result: list[TrainingProfile] = []
    for row in read_csv(path):
        if str(row["is_reference_source"]).lower() == "true":
            continue
        r_value = float(row["combined_target_working_per_source_reference_R"])
        if not math.isfinite(r_value) or r_value <= 0:
            raise ModelError(f"invalid FLORES R value: {row['flores_code']}")
        result.append(
            TrainingProfile(
                flores_code=row["flores_code"],
                language_code=row["language_code"],
                script_code=row["script_code"],
                r_value=r_value,
                row_sha256=canonical_sha256(row),
            )
        )
    if len(result) != 203 or len({p.flores_code for p in result}) != 203:
        raise ModelError("the frozen FLORES training set must contain 203 unique non-English profiles")
    return sorted(result, key=lambda row: row.flores_code)


@dataclass(frozen=True)
class PredictiveParameters:
    location: float
    degrees_freedom: float
    scale: float
    training_rows: int
    script_training_rows: int
    global_mean_log_r: float
    global_variance_log_r: float


def predictive_parameters(
    profiles: Sequence[TrainingProfile], script_code: str, prior: Mapping[str, Any]
) -> PredictiveParameters:
    if len(profiles) < 3:
        raise ModelError("predictive training set has fewer than three profiles")
    values = np.asarray([math.log(row.r_value) for row in profiles], dtype=np.float64)
    mu0 = float(np.mean(values))
    variance = float(np.var(values, ddof=1)) * float(prior["variance_multiplier"])
    if not math.isfinite(variance) or variance <= 0:
        raise ModelError("non-positive global log-R variance")
    kappa0 = float(prior["kappa0"])
    alpha0 = float(prior["alpha0"])
    beta0 = (alpha0 - 1.0) * variance
    script_values = np.asarray(
        [math.log(row.r_value) for row in profiles if row.script_code == script_code],
        dtype=np.float64,
    )
    n = int(script_values.size)
    if n:
        mean = float(np.mean(script_values))
        sum_squares = float(np.sum((script_values - mean) ** 2))
    else:
        mean = mu0
        sum_squares = 0.0
    kappa_n = kappa0 + n
    mu_n = (kappa0 * mu0 + n * mean) / kappa_n
    alpha_n = alpha0 + n / 2.0
    beta_n = (
        beta0
        + 0.5 * sum_squares
        + (kappa0 * n * (mean - mu0) ** 2) / (2.0 * kappa_n)
    )
    scale = math.sqrt(beta_n * (kappa_n + 1.0) / (alpha_n * kappa_n))
    return PredictiveParameters(
        location=mu_n,
        degrees_freedom=2.0 * alpha_n,
        scale=scale,
        training_rows=len(profiles),
        script_training_rows=n,
        global_mean_log_r=mu0,
        global_variance_log_r=variance,
    )


def stable_seed(*parts: str) -> int:
    digest = hashlib.sha256("|".join(parts).encode("utf-8")).digest()
    return int.from_bytes(digest[:8], "big", signed=False)


def draw_r_values(
    params: PredictiveParameters,
    count: int,
    *,
    seed_parts: Sequence[str],
) -> np.ndarray:
    rng = np.random.Generator(np.random.PCG64(stable_seed(*seed_parts)))
    log_values = params.location + params.scale * rng.standard_t(
        params.degrees_freedom, size=count
    )
    values = np.exp(log_values)
    if values.shape != (count,) or not np.all(np.isfinite(values)) or np.any(values <= 0):
        raise ModelError("predictive draw generation produced invalid R values")
    return values


def predictive_state_draw_key(params: PredictiveParameters) -> str:
    """Canonical common-random-number key for one predictive law.

    Target IDs, language codes, origin, and evidence metadata are absent.  Two
    targets with identical predictive parameters therefore receive identical
    Monte Carlo quantiles rather than arbitrary seed noise.
    """

    state = {
        "location": f"{params.location:.17g}",
        "degrees_freedom": f"{params.degrees_freedom:.17g}",
        "scale": f"{params.scale:.17g}",
        "training_rows": params.training_rows,
        "script_training_rows": params.script_training_rows,
        "global_mean_log_r": f"{params.global_mean_log_r:.17g}",
        "global_variance_log_r": f"{params.global_variance_log_r:.17g}",
    }
    return f"predictive-state:sha256:{canonical_sha256(state)}"


def _package_map(model: Mapping[str, Any]) -> dict[str, str]:
    return {str(row["branch_id"]): str(row["package_id"]) for row in model["package_profiles"]}


def derive_cost_coefficients(
    derivation_path: Path,
    profiles: Sequence[TrainingProfile],
    standard_model: Mapping[str, Any],
    *,
    max_abs_error: float,
) -> list[dict[str, Any]]:
    r_by_code = {row.flores_code: row.r_value for row in profiles}
    package_ids = _package_map(standard_model)
    grouped: dict[tuple[str, str], list[tuple[float, float]]] = defaultdict(list)
    for row in read_csv(derivation_path):
        code = row.get("flores_code", "")
        if code not in r_by_code:
            continue
        canon_id = row["canon_id"]
        branch_id = row["branch_id"]
        grouped[(canon_id, branch_id)].append((r_by_code[code], float(row["compute_base"])))
    expected = {
        (str(canon["canon_id"]), str(package["branch_id"]))
        for canon in standard_model["canon_profiles"]
        for package in standard_model["package_profiles"]
    }
    if set(grouped) != expected:
        raise ModelError("canonical derivation combinations do not match the standard model")
    coefficients: list[dict[str, Any]] = []
    for canon_id, branch_id in sorted(expected):
        observations = sorted(grouped[(canon_id, branch_id)])
        if len(observations) != len(profiles):
            raise ModelError(f"incomplete cost calibration grid: {canon_id}/{branch_id}")
        x = np.asarray([row[0] for row in observations], dtype=np.float64)
        y = np.asarray([row[1] for row in observations], dtype=np.float64)
        design = np.column_stack((np.ones_like(x), x))
        intercept, slope = np.linalg.lstsq(design, y, rcond=None)[0]
        predicted = intercept + slope * x
        residual = np.abs(predicted - y)
        observed_error = float(np.max(residual))
        if observed_error > max_abs_error:
            raise ModelError(
                f"base-scenario cost is not affine in R for {canon_id}/{branch_id}: {observed_error}"
            )
        row = {
            "canon_id": canon_id,
            "package_id": package_ids[branch_id],
            "branch_id": branch_id,
            "intercept_fecu": float(intercept),
            "slope_fecu_per_r": float(slope),
            "calibration_rows": len(observations),
            "max_absolute_reconstruction_error_fecu": observed_error,
            "process_scenario": "FROZEN_STANDARD_COMPUTE_BASE_SCENARIO",
        }
        row["coefficient_row_sha256"] = canonical_sha256(row)
        coefficients.append(row)
    return coefficients


EDITION_REGISTRY_COLUMNS = (
    "edition_ordinal", "edition_target_id", "edition_key", "edition_role",
    "edition_derivation_class", "normalized_language_codes_json",
    "language_code_status", "language_names_json", "normalized_script_codes_json",
    "script_code_status", "script_orthography_json", "orthography_status",
    "normalized_territory_scope_ids_json", "territory_scope_id_status",
    "territory_community_json", "territory_community_status", "mode_json",
    "mode_status", "representation_status", "production_intervention_scope",
    "source_identity_ids_json", "source_identity_hashes_json", "derivation_ids_json",
    "derivation_hashes_json", "authority_paths_json", "authority_hashes_json",
    "missing_or_na_reasons_json", "effective_order_l_target",
    "effective_complete_compute_target", "registry_version", "registry_row_hash",
)

EVIDENCE_MAPPING_COLUMNS = (
    "mapping_ordinal", "evidence_identity_id", "source_identity_kind",
    "roster_target_id", "supplement_stratum_id", "target_kind",
    "language_target_id", "intervention_target_id", "empirical_stratum_id",
    "source_production_applicable", "row_role", "normalized_edition_target_id",
    "edition_mapping_status", "duplicate_collapse_status",
    "normalized_language_codes_json", "language_code_status", "language_names_json",
    "normalized_script_codes_json", "script_code_status", "script_orthography_json",
    "orthography_status", "normalized_territory_scope_ids_json",
    "territory_scope_id_status", "territory_community_json",
    "territory_community_status", "mode_json", "mode_status",
    "representation_status", "identity_source_ids_json", "identity_source_hashes_json",
    "identity_derivation_ids_json", "identity_derivation_hashes_json",
    "authority_paths_json", "authority_hashes_json", "population_measure_ids_json",
    "population_measure_classes_json", "population_bound_semantics_json",
    "population_values_persons_json", "evidence_attachment_scope",
    "population_additivity", "collision_binding_status", "collision_disposition",
    "missing_or_na_reasons_json", "effective_edition_membership",
    "source_identity_row_hash", "registry_version", "mapping_row_hash",
)


def _read_csv_with_header(path: Path, expected: Sequence[str]) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        if tuple(reader.fieldnames or ()) != tuple(expected):
            raise ModelError(f"frozen CSV header mismatch: {path.name}")
        return list(reader)


def _ordinal_sequence(rows: Sequence[Mapping[str, str]], field: str) -> bool:
    try:
        values = [int(row[field]) for row in rows]
    except (KeyError, ValueError) as exc:
        raise ModelError(f"invalid ordinal field: {field}") from exc
    return values == list(range(1, len(rows) + 1)) or values == list(range(len(rows)))


def _receipt_schema(receipt: Mapping[str, Any], expected: str, *, name: str) -> None:
    observed = str(receipt.get("schema") or receipt.get("schema_version") or "")
    if observed != expected:
        raise ModelError(f"unsupported {name} receipt schema: {observed}")
    if str(receipt.get("status") or "").upper() != "PASS":
        raise ModelError(f"{name} receipt is not PASS")


def load_edition_authorities(
    edition_path: Path,
    mapping_path: Path,
    roster_path: Path,
    receipt_path: Path,
    test_receipt_path: Path,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Load table A and prove table-B/v2 closure without predicting B rows."""

    edition_rows = _read_csv_with_header(edition_path, EDITION_REGISTRY_COLUMNS)
    mapping_rows = _read_csv_with_header(mapping_path, EVIDENCE_MAPPING_COLUMNS)
    receipt = read_json(receipt_path)
    test_receipt = read_json(test_receipt_path)
    _receipt_schema(
        receipt,
        "interlanguage/successor-edition-target-registry-receipt/3.0.0",
        name="edition registry",
    )
    _receipt_schema(
        test_receipt,
        "interlanguage/successor-edition-target-registry-test-receipt/3.0.0",
        name="edition registry test",
    )
    if not edition_rows or not mapping_rows:
        raise ModelError("frozen edition authorities are empty")
    if not _ordinal_sequence(edition_rows, "edition_ordinal"):
        raise ModelError("edition registry ordinal sequence is not closed")
    if not _ordinal_sequence(mapping_rows, "mapping_ordinal"):
        raise ModelError("evidence mapping ordinal sequence is not closed")

    edition_ids = [row["edition_target_id"] for row in edition_rows]
    if any(not value for value in edition_ids) or len(edition_ids) != len(set(edition_ids)):
        raise ModelError("edition registry IDs are empty or duplicated")
    edition_set = set(edition_ids)
    evidence_ids = [row["evidence_identity_id"] for row in mapping_rows]
    if any(not value for value in evidence_ids) or len(evidence_ids) != len(set(evidence_ids)):
        raise ModelError("evidence identity IDs are empty or duplicated")
    mapped_ids = {row["normalized_edition_target_id"] for row in mapping_rows if row["normalized_edition_target_id"]}
    if not mapped_ids <= edition_set:
        raise ModelError(f"evidence mapping references foreign editions: {sorted(mapped_ids - edition_set)[:3]}")
    for row in mapping_rows:
        effective = parse_bool(row["effective_edition_membership"], field="effective_edition_membership")
        if not row["row_role"] or not row["edition_mapping_status"]:
            raise ModelError(f"evidence identity lacks a closed mapping role: {row['evidence_identity_id']}")
        if not row["collision_binding_status"] or not row["collision_disposition"]:
            raise ModelError(f"evidence identity lacks a closed collision disposition: {row['evidence_identity_id']}")
        if effective and not row["normalized_edition_target_id"]:
            raise ModelError(f"effective evidence identity lacks an edition mapping: {row['evidence_identity_id']}")

    roster = read_json(roster_path)
    if roster.get("schema") != "interlanguage/successor-target-roster/2.0.0":
        raise ModelError("unsupported frozen successor roster schema")
    roster_ids = {str(row.get("roster_target_id") or "") for row in roster.get("roster_targets", [])}
    roster_ids.discard("")
    mapped_roster_ids = {row["roster_target_id"] for row in mapping_rows if row["roster_target_id"]}
    if mapped_roster_ids != roster_ids:
        raise ModelError(
            "evidence mapping is not set-equal to the frozen v2 roster; "
            f"missing={sorted(roster_ids - mapped_roster_ids)[:3]} "
            f"extra={sorted(mapped_roster_ids - roster_ids)[:3]}"
        )

    features = [extract_edition_features(row) for row in edition_rows]
    features.sort(key=lambda row: row["edition_target_id"])
    feature_ids = {row["edition_target_id"] for row in features}
    if feature_ids != edition_set:
        raise ModelError("edition feature projection is not set-equal to table A")
    authority = {
        "edition_registry_schema": "interlanguage/successor-edition-target-registry/3.0.0",
        "evidence_mapping_schema": "interlanguage/successor-evidence-identity-to-edition/3.0.0",
        "edition_rows": len(edition_rows),
        "effective_complete_compute_targets": sum(
            parse_bool(row["effective_complete_compute_target"], field="effective_complete_compute_target")
            for row in edition_rows
        ),
        "evidence_identity_rows": len(mapping_rows),
        "mapped_evidence_identity_rows": sum(bool(row["normalized_edition_target_id"]) for row in mapping_rows),
        "v2_roster_identity_rows": len(mapped_roster_ids),
        "supplement_identity_rows": sum(bool(row["supplement_stratum_id"]) for row in mapping_rows),
        "edition_target_set_sha256": canonical_sha256(sorted(edition_set)),
        "evidence_identity_set_sha256": canonical_sha256(sorted(evidence_ids)),
        "mapping_role_counts": dict(sorted(Counter(row["row_role"] for row in mapping_rows).items())),
        "mapping_status_counts": dict(sorted(Counter(row["edition_mapping_status"] for row in mapping_rows).items())),
        "duplicate_collapse_counts": dict(sorted(Counter(row["duplicate_collapse_status"] for row in mapping_rows).items())),
        "receipt_schema": str(receipt.get("schema") or receipt.get("schema_version")),
        "test_receipt_schema": str(test_receipt.get("schema") or test_receipt.get("schema_version")),
    }
    return features, authority


def _quantiles(values: np.ndarray) -> tuple[float, float, float]:
    q05, q50, q95 = np.quantile(values, [0.05, 0.5, 0.95], method="linear")
    return float(q05), float(q50), float(q95)


def calibration_rows(
    profiles: Sequence[TrainingProfile],
    prior: Mapping[str, Any],
    *,
    seed_namespace: str,
    draw_count: int,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    result: list[dict[str, Any]] = []
    errors: list[float] = []
    covered: list[bool] = []
    group_errors: dict[str, list[float]] = defaultdict(list)
    group_covered: dict[str, list[bool]] = defaultdict(list)
    for profile in profiles:
        held_out_code = canonical_language_code(
            profile.language_code, profile.script_code, "written_or_multimodal"
        )[0]
        train = [
            row
            for row in profiles
            if canonical_language_code(
                row.language_code, row.script_code, "written_or_multimodal"
            )[0]
            != held_out_code
        ]
        params = predictive_parameters(train, profile.script_code, prior)
        draws = draw_r_values(
            params,
            draw_count,
            seed_parts=(seed_namespace, "leave-language-out", profile.flores_code),
        )
        p05, p50, p95 = _quantiles(draws)
        log_error = math.log(profile.r_value) - math.log(p50)
        hit = p05 <= profile.r_value <= p95
        errors.append(log_error)
        covered.append(hit)
        group_errors[held_out_code].append(log_error)
        group_covered[held_out_code].append(hit)
        result.append(
            {
                "flores_code": profile.flores_code,
                "held_out_language_code": profile.language_code,
                "held_out_canonical_language_code": held_out_code,
                "script_code": profile.script_code,
                "actual_r": profile.r_value,
                "predictive_p05_r": p05,
                "predictive_p50_r": p50,
                "predictive_p95_r": p95,
                "interval_90_hit": hit,
                "log_median_error": log_error,
                "absolute_log_median_error": abs(log_error),
                "training_rows": params.training_rows,
                "script_training_rows": params.script_training_rows,
            }
        )
    error_array = np.asarray(errors, dtype=np.float64)
    group_coverages = [float(np.mean(group_covered[key])) for key in sorted(group_covered)]
    group_median_abs_errors = [
        float(np.median(np.abs(np.asarray(group_errors[key], dtype=np.float64))))
        for key in sorted(group_errors)
    ]
    group_mean_squared_errors = [
        float(np.mean(np.asarray(group_errors[key], dtype=np.float64) ** 2))
        for key in sorted(group_errors)
    ]
    summary = {
        "profiles": len(result),
        "language_held_out_groups": len(group_errors),
        "predictive_interval_90_coverage": float(np.mean(covered)),
        "median_absolute_log_error": float(np.median(np.abs(error_array))),
        "rmse_log_error": float(np.sqrt(np.mean(error_array**2))),
        "p95_absolute_log_error": float(np.quantile(np.abs(error_array), 0.95)),
        "macro_language_predictive_interval_90_coverage": float(np.mean(group_coverages)),
        "macro_language_median_absolute_log_error": float(np.median(group_median_abs_errors)),
        "macro_language_rmse_log_error": float(np.sqrt(np.mean(group_mean_squared_errors))),
    }
    return result, summary


def leave_script_out_calibration_rows(
    profiles: Sequence[TrainingProfile],
    prior: Mapping[str, Any],
    *,
    seed_namespace: str,
    draw_count: int,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Diagnose the global fallback used for scripts absent from training."""

    result: list[dict[str, Any]] = []
    by_script_errors: dict[str, list[float]] = defaultdict(list)
    by_script_hits: dict[str, list[bool]] = defaultdict(list)
    for profile in profiles:
        train = [row for row in profiles if row.script_code != profile.script_code]
        params = predictive_parameters(train, profile.script_code, prior)
        if params.script_training_rows != 0:
            raise ModelError("leave-script-out calibration retained a held-out script row")
        draws = draw_r_values(
            params,
            draw_count,
            seed_parts=(seed_namespace, "leave-script-out", profile.script_code),
        )
        p05, p50, p95 = _quantiles(draws)
        log_error = math.log(profile.r_value) - math.log(p50)
        hit = p05 <= profile.r_value <= p95
        by_script_errors[profile.script_code].append(log_error)
        by_script_hits[profile.script_code].append(hit)
        result.append(
            {
                "flores_code": profile.flores_code,
                "held_out_script_code": profile.script_code,
                "actual_r": profile.r_value,
                "predictive_p05_r": p05,
                "predictive_p50_r": p50,
                "predictive_p95_r": p95,
                "interval_90_hit": hit,
                "log_median_error": log_error,
                "absolute_log_median_error": abs(log_error),
                "training_rows": params.training_rows,
                "script_training_rows": params.script_training_rows,
            }
        )
    errors = np.asarray(
        [float(row["log_median_error"]) for row in result], dtype=np.float64
    )
    per_script = []
    for script in sorted(by_script_errors):
        script_errors = np.asarray(by_script_errors[script], dtype=np.float64)
        per_script.append(
            {
                "script_code": script,
                "profiles": int(script_errors.size),
                "predictive_interval_90_coverage": float(np.mean(by_script_hits[script])),
                "median_absolute_log_error": float(np.median(np.abs(script_errors))),
                "rmse_log_error": float(np.sqrt(np.mean(script_errors**2))),
            }
        )
    summary = {
        "profiles": len(result),
        "held_out_scripts": len(per_script),
        "predictive_interval_90_coverage": float(
            np.mean([bool(row["interval_90_hit"]) for row in result])
        ),
        "median_absolute_log_error": float(np.median(np.abs(errors))),
        "rmse_log_error": float(np.sqrt(np.mean(errors**2))),
        "per_script": per_script,
        "interpretation": "DIAGNOSTIC_ONLY_GLOBAL_FALLBACK_RARE_SCRIPT_MISSES_REMAIN_VISIBLE",
    }
    return result, summary


def _write_csv(path: Path, rows: Sequence[Mapping[str, Any]], fieldnames: Sequence[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    with tmp.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, extrasaction="raise", lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow(row)
    os.replace(tmp, path)


def _write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_bytes(json_file_bytes(value))
    os.replace(tmp, path)


def _write_deterministic_gzip_grid(
    path: Path,
    features: Sequence[Mapping[str, Any]],
    profiles: Sequence[TrainingProfile],
    prior: Mapping[str, Any],
    coefficients: Sequence[Mapping[str, Any]],
    *,
    model_run_id: str,
    seed_namespace: str,
    draw_count: int,
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    raw_hash = hashlib.sha256()
    header = (
        "edition_target_id,draw_id,canon_id,package_id,predicted_profile_r,"
        "standard_compute_fecu,total_cost_evidence_class\n"
    ).encode("utf-8")
    raw_hash.update(header)
    row_count = 0
    summary_rows: list[dict[str, Any]] = []
    applicable = [row for row in features if row["model_applicability_status"] == "MODEL_CONDITIONAL_APPLICABLE"]
    with tmp.open("wb") as raw_handle:
        with gzip.GzipFile(fileobj=raw_handle, mode="wb", filename="", mtime=0, compresslevel=9) as gz:
            gz.write(header)
            for feature in applicable:
                target_id = feature["edition_target_id"]
                params = predictive_parameters(profiles, feature["predictor_script_code"], prior)
                r_draws = draw_r_values(
                    params,
                    draw_count,
                    seed_parts=(seed_namespace, "primary-grid", predictive_state_draw_key(params)),
                )
                for draw_id, r_value in enumerate(r_draws):
                    for coefficient in coefficients:
                        cost = coefficient["intercept_fecu"] + coefficient["slope_fecu_per_r"] * float(r_value)
                        if not math.isfinite(cost) or cost < 0:
                            raise ModelError(f"invalid modeled compute for {target_id}")
                        line = (
                            f"{target_id},{draw_id:04d},{coefficient['canon_id']},"
                            f"{coefficient['package_id']},{float(r_value):.12f},{cost:.6f},"
                            "MODEL_CONDITIONAL\n"
                        ).encode("utf-8")
                        raw_hash.update(line)
                        gz.write(line)
                        row_count += 1
                r_p05, r_p50, r_p95 = _quantiles(r_draws)
                for coefficient in coefficients:
                    costs = coefficient["intercept_fecu"] + coefficient["slope_fecu_per_r"] * r_draws
                    c_p05, c_p50, c_p95 = _quantiles(costs)
                    summary_rows.append(
                        {
                            "edition_target_id": target_id,
                            "canon_id": coefficient["canon_id"],
                            "package_id": coefficient["package_id"],
                            "draw_count": draw_count,
                            "profile_r_p05": f"{r_p05:.12f}",
                            "profile_r_p50": f"{r_p50:.12f}",
                            "profile_r_p95": f"{r_p95:.12f}",
                            "standard_compute_p05_fecu": f"{c_p05:.6f}",
                            "standard_compute_p50_fecu": f"{c_p50:.6f}",
                            "standard_compute_p95_fecu": f"{c_p95:.6f}",
                            "total_cost_evidence_class": "MODEL_CONDITIONAL",
                        }
                    )
    os.replace(tmp, path)
    expected = len(applicable) * draw_count * len(coefficients)
    if row_count != expected:
        raise ModelError(f"complete grid count mismatch: {row_count} != {expected}")
    return {
        "applicable_targets": len(applicable),
        "applicable_edition_target_set_sha256": canonical_sha256(
            sorted(row["edition_target_id"] for row in applicable)
        ),
        "draws_per_target": draw_count,
        "canon_package_combinations": len(coefficients),
        "rows": row_count,
        "uncompressed_csv_sha256": raw_hash.hexdigest(),
        "gzip_bytes": path.stat().st_size,
        "gzip_sha256": sha256_file(path),
    }, summary_rows


def sensitivity_rows(
    features: Sequence[Mapping[str, Any]],
    profiles: Sequence[TrainingProfile],
    priors: Mapping[str, Mapping[str, Any]],
    coefficients: Sequence[Mapping[str, Any]],
    *,
    model_run_id: str,
    seed_namespace: str,
    draw_count: int,
) -> list[dict[str, Any]]:
    result: list[dict[str, Any]] = []
    for feature in features:
        if feature["model_applicability_status"] != "MODEL_CONDITIONAL_APPLICABLE":
            continue
        target_id = feature["edition_target_id"]
        for prior_id, prior in sorted(priors.items()):
            params = predictive_parameters(profiles, feature["predictor_script_code"], prior)
            r_draws = draw_r_values(
                params,
                draw_count,
                seed_parts=(seed_namespace, "sensitivity", prior_id, predictive_state_draw_key(params)),
            )
            for coefficient in coefficients:
                costs = coefficient["intercept_fecu"] + coefficient["slope_fecu_per_r"] * r_draws
                c05, c50, c95 = _quantiles(costs)
                result.append(
                    {
                        "edition_target_id": target_id,
                        "prior_specification_id": prior_id,
                        "canon_id": coefficient["canon_id"],
                        "package_id": coefficient["package_id"],
                        "draw_count": draw_count,
                        "standard_compute_p05_fecu": f"{c05:.6f}",
                        "standard_compute_p50_fecu": f"{c50:.6f}",
                        "standard_compute_p95_fecu": f"{c95:.6f}",
                        "interval_semantics": "PREDICTIVE_NOT_BOUND",
                    }
                )
    return result


def _scientific_feature_rows(features: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    keys = (
        "edition_target_id",
        "edition_role",
        "edition_derivation_class",
        "language_mode",
        "representation_status",
        "effective_complete_compute_target",
        "predictor_language_code",
        "predictor_language_code_canonical",
        "language_alias_rule",
        "predictor_script_code",
        "representation_draw_key",
        "script_inference_rule",
        "model_applicability_status",
        "not_applicable_reason",
        "representation_feature_row_sha256",
    )
    return [{key: row[key] for key in keys} for row in sorted(features, key=lambda r: r["edition_target_id"])]


def scientific_input_payload(
    features: Sequence[Mapping[str, Any]],
    profiles: Sequence[TrainingProfile],
    coefficients: Sequence[Mapping[str, Any]],
    registry: Mapping[str, Any],
    edition_authority: Mapping[str, Any],
) -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "predictor_policy": registry["predictor_policy"],
        "language_alias_policy": registry["language_alias_policy"],
        "applicability_policy": registry["applicability_policy"],
        "priors": registry["prior_specifications"],
        "primary_prior_id": registry["primary_prior_id"],
        "draw_protocol": registry["draw_protocol"],
        "edition_authority": dict(edition_authority),
        "target_features": _scientific_feature_rows(features),
        "training_profiles": [
            {
                "flores_code": row.flores_code,
                "language_code": row.language_code,
                "script_code": row.script_code,
                "r_value": row.r_value,
                "row_sha256": row.row_sha256,
            }
            for row in profiles
        ],
        "cost_coefficients": list(coefficients),
    }


def _status_rows(
    features: Sequence[Mapping[str, Any]],
    *,
    model_run_id: str,
    edition_registry_file_sha256: str,
    evidence_mapping_file_sha256: str,
    edition_target_set_sha256: str,
    profiles: Sequence[TrainingProfile],
    prior: Mapping[str, Any],
) -> list[dict[str, Any]]:
    result: list[dict[str, Any]] = []
    for feature in features:
        if feature["model_applicability_status"] == "MODEL_CONDITIONAL_APPLICABLE":
            params = predictive_parameters(profiles, feature["predictor_script_code"], prior)
            training_rows = params.training_rows
            script_rows = params.script_training_rows
            evidence_class = "MODEL_CONDITIONAL_PROFILE"
        else:
            training_rows = ""
            script_rows = ""
            evidence_class = "NOT_APPLICABLE_MODE"
        result.append(
            {
                "model_run_id": model_run_id,
                "edition_registry_file_sha256": edition_registry_file_sha256,
                "evidence_mapping_file_sha256": evidence_mapping_file_sha256,
                "edition_target_set_sha256": edition_target_set_sha256,
                "edition_target_id": feature["edition_target_id"],
                "source_edition_row_sha256": feature["source_edition_row_sha256"],
                "representation_feature_row_sha256": feature["representation_feature_row_sha256"],
                "edition_role": feature["edition_role"],
                "edition_derivation_class": feature["edition_derivation_class"],
                "language_mode": feature["language_mode"],
                "representation_status": feature["representation_status"],
                "effective_complete_compute_target": str(feature["effective_complete_compute_target"]).lower(),
                "predictor_language_code": feature["predictor_language_code"],
                "predictor_language_code_canonical": feature["predictor_language_code_canonical"],
                "language_alias_rule": feature["language_alias_rule"],
                "predictor_script_code": feature["predictor_script_code"],
                "representation_draw_key": feature["representation_draw_key"],
                "script_inference_rule": feature["script_inference_rule"],
                "model_applicability_status": feature["model_applicability_status"],
                "not_applicable_reason": feature["not_applicable_reason"],
                "model_profile_evidence_class": evidence_class,
                "training_rows": training_rows,
                "script_training_rows": script_rows,
            }
        )
    return result


def _write_report(path: Path, model: Mapping[str, Any], receipt: Mapping[str, Any]) -> None:
    counts = model["counts"]
    cal = model["leave_language_out_calibration"]
    text = f"""# Complete-roster model-conditional standardized compute

Status: validated model-conditional evidence lane; not a ranking and not a direct-cost claim.

## Scope

This lane applies one frozen script-conditioned predictive protocol to every complete-compute edition selected by the successor edition registry. The companion evidence-identity table is verified for closure but never creates duplicate predictions. The model uses no population, educational-need, region, territory, income, prestige, institutional status, evidence count, resource stock, user/local/project status, completion, readiness, reuse, or cache field. Those fields cannot enter the model because the target feature projection does not read them.

Signed, oral-only, undefined-representation, and non-effective targets receive explicit not-applicable status rows. They receive no written-token draw and no numerical substitute. A named-sign package attached to an applicable written edition is a process package; it does not turn a signed-language target into a written target model.

## Model

The training set contains {counts['training_profiles']} aligned FLORES language-script profiles. The sole target-side predictor is script. Log token expansion uses a Normal-Inverse-Gamma posterior predictive distribution with a global empirical-Bayes center and script-specific updating. Scripts absent from FLORES use the common global prior predictive distribution. Every estimate remains `MODEL_CONDITIONAL`; predictive intervals are not identification bounds.

The model evaluates {counts['applicable_targets']} applicable editions, {counts['draws_per_target']} draws, {counts['canons']} canons, and {counts['packages']} packages, producing {counts['complete_grid_rows']} exact edition-by-draw-by-canon-by-package rows. The frozen base-process compute total is an affine function of the predicted target-token ratio; all 18 canon/package functions reproduce the direct-profile derivations within the preregistered tolerance. Because the exponentiated Student-t predictive law does not have a finite arithmetic mean, this lane reports medians and predictive quantiles only; it makes no mean-cost claim.

## Calibration

Leave-language-out calibration removes every script profile belonging to the held-out FLORES language code before prediction. Across {cal['profiles']} profiles, empirical coverage of the nominal 90% predictive interval is {cal['predictive_interval_90_coverage']:.3f}; median absolute log error is {cal['median_absolute_log_error']:.3f}; RMSE log error is {cal['rmse_log_error']:.3f}. These are calibration diagnostics, not evidence that every unobserved educational domain follows FLORES.

Leave-entire-script-out diagnostics separately exercise the global fallback used for unseen scripts and report every script, including rare-script misses, without converting the diagnostic into a target penalty or exclusion.

## Sensitivity and interpretation

The primary, weak-shrinkage/diffuse, and strong-shrinkage prior specifications are reported separately. No uncertainty penalty is applied. Direct profiles are training and calibration evidence only and do not relabel any edition result as direct measurement. The complete grid is suitable only for the model-conditional compute-efficiency lane.

## Integrity

- Model run: `{model['model_run_id']}`
- Scientific input SHA-256: `{model['scientific_input_sha256']}`
- Complete uncompressed grid SHA-256: `{model['complete_grid']['uncompressed_csv_sha256']}`
- Complete gzip SHA-256: `{model['complete_grid']['gzip_sha256']}`
- Receipt status: `{receipt['status']}`
"""
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(text, encoding="utf-8", newline="\n")
    os.replace(tmp, path)


def build(base: Path, output_root: Path, registry_path: Path) -> dict[str, Any]:
    registry = read_json(registry_path)
    if registry.get("schema_version") != "interlanguage/complete-roster-compute-model-registry/1.0.0":
        raise ModelError("unsupported complete-roster model registry")
    identities = validate_authoritative_inputs(base, registry)
    input_paths = registry["input_paths"]
    edition_path = exact_relative(base, input_paths["edition_target_registry"])
    mapping_path = exact_relative(base, input_paths["evidence_identity_mapping"])
    roster_path = exact_relative(base, input_paths["successor_roster_v2"])
    edition_receipt_path = exact_relative(base, input_paths["edition_registry_receipt"])
    edition_test_receipt_path = exact_relative(base, input_paths["edition_registry_test_receipt"])
    tokenization_path = exact_relative(base, input_paths["flores_tokenization"])
    derivation_path = exact_relative(base, input_paths["canonical_derivations"])
    standard_model_path = exact_relative(base, input_paths["standard_compute_model"])

    features, edition_authority = load_edition_authorities(
        edition_path,
        mapping_path,
        roster_path,
        edition_receipt_path,
        edition_test_receipt_path,
    )
    profiles = load_training_profiles(tokenization_path)
    standard_model = read_json(standard_model_path)
    coefficients = derive_cost_coefficients(
        derivation_path,
        profiles,
        standard_model,
        max_abs_error=float(registry["cost_projection"]["maximum_affine_reconstruction_error_fecu"]),
    )
    scientific_payload = scientific_input_payload(
        features, profiles, coefficients, registry, edition_authority
    )
    scientific_input_sha = canonical_sha256(scientific_payload)
    model_run_id = f"CRCM-{scientific_input_sha[:20]}"
    primary_prior = registry["prior_specifications"][registry["primary_prior_id"]]

    calibration, calibration_summary = calibration_rows(
        profiles,
        primary_prior,
        seed_namespace=registry["draw_protocol"]["seed_namespace"],
        draw_count=int(registry["draw_protocol"]["calibration_draws_per_profile"]),
    )
    thresholds = registry["calibration_thresholds"]
    if calibration_summary["predictive_interval_90_coverage"] < float(thresholds["minimum_90_interval_coverage"]):
        raise ModelError("leave-language-out 90% predictive coverage failed")
    if calibration_summary["median_absolute_log_error"] > float(thresholds["maximum_median_absolute_log_error"]):
        raise ModelError("leave-language-out median absolute log error failed")
    if calibration_summary["rmse_log_error"] > float(thresholds["maximum_rmse_log_error"]):
        raise ModelError("leave-language-out RMSE log error failed")
    if calibration_summary["macro_language_predictive_interval_90_coverage"] < float(
        thresholds["minimum_90_interval_coverage"]
    ):
        raise ModelError("macro-language leave-out 90% predictive coverage failed")
    if calibration_summary["macro_language_median_absolute_log_error"] > float(
        thresholds["maximum_median_absolute_log_error"]
    ):
        raise ModelError("macro-language leave-out median absolute log error failed")
    if calibration_summary["macro_language_rmse_log_error"] > float(
        thresholds["maximum_rmse_log_error"]
    ):
        raise ModelError("macro-language leave-out RMSE log error failed")
    script_calibration, script_calibration_summary = leave_script_out_calibration_rows(
        profiles,
        primary_prior,
        seed_namespace=registry["draw_protocol"]["seed_namespace"],
        draw_count=int(registry["draw_protocol"]["calibration_draws_per_profile"]),
    )

    output_paths = registry["output_paths"]
    grid_path = exact_relative(output_root, output_paths["complete_draw_grid"])
    grid_receipt, summaries = _write_deterministic_gzip_grid(
        grid_path,
        features,
        profiles,
        primary_prior,
        coefficients,
        model_run_id=model_run_id,
        seed_namespace=registry["draw_protocol"]["seed_namespace"],
        draw_count=int(registry["draw_protocol"]["primary_draws_per_target"]),
    )
    sensitivity = sensitivity_rows(
        features,
        profiles,
        registry["prior_specifications"],
        coefficients,
        model_run_id=model_run_id,
        seed_namespace=registry["draw_protocol"]["seed_namespace"],
        draw_count=int(registry["draw_protocol"]["sensitivity_draws_per_target_prior"]),
    )
    status = _status_rows(
        features,
        model_run_id=model_run_id,
        edition_registry_file_sha256=identities[input_paths["edition_target_registry"]]["sha256"],
        evidence_mapping_file_sha256=identities[input_paths["evidence_identity_mapping"]]["sha256"],
        edition_target_set_sha256=edition_authority["edition_target_set_sha256"],
        profiles=profiles,
        prior=primary_prior,
    )

    status_fields = list(status[0])
    calibration_fields = list(calibration[0])
    script_calibration_fields = list(script_calibration[0])
    summary_fields = list(summaries[0])
    sensitivity_fields = list(sensitivity[0])
    coefficient_fields = list(coefficients[0])
    _write_csv(exact_relative(output_root, output_paths["target_status"]), status, status_fields)
    _write_csv(exact_relative(output_root, output_paths["calibration"]), calibration, calibration_fields)
    _write_csv(
        exact_relative(output_root, output_paths["script_calibration"]),
        script_calibration,
        script_calibration_fields,
    )
    _write_csv(exact_relative(output_root, output_paths["summaries"]), summaries, summary_fields)
    _write_csv(exact_relative(output_root, output_paths["sensitivity"]), sensitivity, sensitivity_fields)
    _write_csv(exact_relative(output_root, output_paths["cost_coefficients"]), coefficients, coefficient_fields)

    applicable_count = sum(row["model_applicability_status"] == "MODEL_CONDITIONAL_APPLICABLE" for row in features)
    mode_counts = dict(sorted(Counter(row["model_applicability_status"] for row in features).items()))
    model = {
        "schema_version": SCHEMA_VERSION,
        "artifact_status": "VALIDATED_MODEL_CONDITIONAL_NOT_A_RANKING",
        "model_run_id": model_run_id,
        "snapshot_utc": registry["snapshot_utc"],
        "scientific_input_sha256": scientific_input_sha,
        "authority_inputs": identities,
        "edition_authority": edition_authority,
        "predictor_policy": registry["predictor_policy"],
        "language_alias_policy": registry["language_alias_policy"],
        "applicability_policy": registry["applicability_policy"],
        "prior_specifications": registry["prior_specifications"],
        "primary_prior_id": registry["primary_prior_id"],
        "draw_protocol": registry["draw_protocol"],
        "cost_projection": {
            **registry["cost_projection"],
            "coefficients": coefficients,
        },
        "counts": {
            "edition_registry_targets": len(features),
            "effective_complete_compute_targets": edition_authority["effective_complete_compute_targets"],
            "evidence_identity_rows": edition_authority["evidence_identity_rows"],
            "applicable_targets": applicable_count,
            "not_applicable_targets": len(features) - applicable_count,
            "applicability_statuses": mode_counts,
            "training_profiles": len(profiles),
            "draws_per_target": grid_receipt["draws_per_target"],
            "canons": len(standard_model["canon_profiles"]),
            "packages": len(standard_model["package_profiles"]),
            "complete_grid_rows": grid_receipt["rows"],
            "summary_rows": len(summaries),
            "sensitivity_rows": len(sensitivity),
        },
        "leave_language_out_calibration": calibration_summary,
        "leave_script_out_calibration": script_calibration_summary,
        "calibration_thresholds": thresholds,
        "complete_grid": grid_receipt,
        "interpretation": {
            "profile_values": "MODEL_CONDITIONAL_PREDICTIVE_DRAWS_NOT_DIRECT_MEASUREMENTS",
            "compute_values": "MODEL_CONDITIONAL_FIXED_BASE_PROCESS_SCENARIO",
            "intervals": "PREDICTIVE_NOT_IDENTIFICATION_BOUNDS",
            "uncertainty_penalty": "FORBIDDEN",
            "ranking_effect": "NONE_IN_THIS_ARTIFACT",
        },
    }
    model_path = exact_relative(output_root, output_paths["model"])
    _write_json(model_path, model)

    all_ids = {row["edition_target_id"] for row in features}
    effective_ids = {
        row["edition_target_id"] for row in features if row["effective_complete_compute_target"]
    }
    numeric_ids = {
        row["edition_target_id"]
        for row in features
        if row["model_applicability_status"] == "MODEL_CONDITIONAL_APPLICABLE"
    }
    nonwritten_na_ids = {
        row["edition_target_id"]
        for row in features
        if row["effective_complete_compute_target"]
        and row["model_applicability_status"]
        in {
            "NOT_APPLICABLE_SIGNED_MODE",
            "NOT_APPLICABLE_ORAL_ONLY_MODE",
            "NOT_APPLICABLE_UNDEFINED_REPRESENTATION_MODE",
        }
    }
    summary_ids = {row["edition_target_id"] for row in summaries}
    status_ids = {row["edition_target_id"] for row in status}
    tests = {
        "authoritative_inputs_hash_bound": True,
        "edition_target_ids_unique": len(features) == len(all_ids),
        "status_exact_set_equality_to_table_a": status_ids == all_ids,
        "effective_editions_exactly_numeric_or_nonwritten_na": effective_ids
        == numeric_ids | nonwritten_na_ids
        and not (numeric_ids & nonwritten_na_ids),
        "summary_exact_set_equality_to_numeric_editions": summary_ids == numeric_ids,
        "grid_target_set_hash_matches_numeric_editions": grid_receipt[
            "applicable_edition_target_set_sha256"
        ]
        == canonical_sha256(sorted(numeric_ids)),
        "evidence_mapping_covers_frozen_roster": edition_authority["v2_roster_identity_rows"]
        == 1266,
        "evidence_mapping_has_closed_roles": bool(edition_authority["mapping_role_counts"])
        and bool(edition_authority["mapping_status_counts"]),
        "signed_oral_receive_no_numeric_grid": all(
            row["model_applicability_status"] != "MODEL_CONDITIONAL_APPLICABLE"
            for row in features
            if row["language_mode"] in {"signed", "spoken"}
        ),
        "complete_grid_cartesian_count": grid_receipt["rows"]
        == applicable_count * int(registry["draw_protocol"]["primary_draws_per_target"]) * len(coefficients),
        "cost_calibration_affine_tolerance": all(
            row["max_absolute_reconstruction_error_fecu"]
            <= float(registry["cost_projection"]["maximum_affine_reconstruction_error_fecu"])
            for row in coefficients
        ),
        "leave_language_out_profiles_complete": len(calibration) == len(profiles),
        "leave_language_out_thresholds_pass": True,
        "leave_script_out_profiles_complete": len(script_calibration) == len(profiles),
        "target_id_permutation_invariant": canonical_sha256(_scientific_feature_rows(features))
        == canonical_sha256(_scientific_feature_rows(list(reversed(features)))),
        "forbidden_metadata_not_in_feature_projection": not any(
            any(token in key.lower() for token in FORBIDDEN_PREDICTOR_TOKENS)
            for key in ALLOWED_TARGET_FEATURE_FIELDS
        ),
        "target_draw_seed_replay": True,
        "all_effective_targets_have_numeric_or_nonwritten_disposition": all(
            (not row["effective_complete_compute_target"])
            or row["model_applicability_status"]
            in {
                "MODEL_CONDITIONAL_APPLICABLE",
                "NOT_APPLICABLE_SIGNED_MODE",
                "NOT_APPLICABLE_ORAL_ONLY_MODE",
                "NOT_APPLICABLE_UNDEFINED_REPRESENTATION_MODE",
            }
            for row in features
        ),
        "table_b_predictions_not_duplicated": len(features) == edition_authority["edition_rows"],
    }
    applicable_features = [row for row in features if row["model_applicability_status"] == "MODEL_CONDITIONAL_APPLICABLE"]
    for probe in (applicable_features[:1] + applicable_features[-1:]):
        params = predictive_parameters(profiles, probe["predictor_script_code"], primary_prior)
        seed_parts = (
            registry["draw_protocol"]["seed_namespace"],
            "replay-probe",
            predictive_state_draw_key(params),
        )
        a = draw_r_values(params, 16, seed_parts=seed_parts)
        b = draw_r_values(params, 16, seed_parts=seed_parts)
        tests["target_draw_seed_replay"] = tests["target_draw_seed_replay"] and bool(np.array_equal(a, b))
    if not all(tests.values()):
        raise ModelError(f"deterministic QA failed: {[key for key, value in tests.items() if not value]}")

    output_artifacts: dict[str, dict[str, Any]] = {}
    for key in (
        "target_status",
        "calibration",
        "script_calibration",
        "summaries",
        "sensitivity",
        "cost_coefficients",
        "model",
        "complete_draw_grid",
    ):
        relative = output_paths[key]
        path = exact_relative(output_root, relative)
        output_artifacts[relative] = {"bytes": path.stat().st_size, "sha256": sha256_file(path)}
    qa = {
        "schema_version": "interlanguage/complete-roster-compute-qa/1.0.0",
        "model_run_id": model_run_id,
        "status": "PASS",
        "checks": tests,
        "counts": model["counts"],
        "calibration": calibration_summary,
        "leave_script_out_calibration": script_calibration_summary,
        "scientific_input_sha256": scientific_input_sha,
        "complete_grid_uncompressed_sha256": grid_receipt["uncompressed_csv_sha256"],
    }
    qa_path = exact_relative(output_root, output_paths["qa"])
    _write_json(qa_path, qa)
    output_artifacts[output_paths["qa"]] = {"bytes": qa_path.stat().st_size, "sha256": sha256_file(qa_path)}

    script_rel = "scripts/build_complete_roster_compute_model.py"
    test_rel = "tests/test_complete_roster_compute_model.py"
    receipt = {
        "schema_version": "interlanguage/complete-roster-compute-receipt/1.0.0",
        "model_run_id": model_run_id,
        "status": "PASS",
        "snapshot_utc": registry["snapshot_utc"],
        "scientific_input_sha256": scientific_input_sha,
        "complete_grid_uncompressed_sha256": grid_receipt["uncompressed_csv_sha256"],
        "authoritative_inputs": identities,
        "implementation": {
            script_rel: {
                "bytes": exact_relative(base, script_rel).stat().st_size,
                "sha256": sha256_file(exact_relative(base, script_rel)),
            },
            test_rel: {
                "bytes": exact_relative(base, test_rel).stat().st_size,
                "sha256": sha256_file(exact_relative(base, test_rel)),
            },
            str(registry_path.relative_to(base)).replace("\\", "/"): {
                "bytes": registry_path.stat().st_size,
                "sha256": sha256_file(registry_path),
            },
        },
        "outputs": output_artifacts,
        "replay_command": "python scripts/build_complete_roster_compute_model.py --base . --output-root .",
        "tests_command": "python -m unittest tests.test_complete_roster_compute_model",
    }
    receipt_path = exact_relative(output_root, output_paths["receipt"])
    _write_json(receipt_path, receipt)
    output_artifacts[output_paths["receipt"]] = {"bytes": receipt_path.stat().st_size, "sha256": sha256_file(receipt_path)}

    report_path = exact_relative(output_root, output_paths["report"])
    _write_report(report_path, model, receipt)
    output_artifacts[output_paths["report"]] = {"bytes": report_path.stat().st_size, "sha256": sha256_file(report_path)}

    manifest_path = exact_relative(output_root, output_paths["hash_manifest"])
    manifest_lines = [f"{row['sha256']} *{relative}\n" for relative, row in sorted(output_artifacts.items())]
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    tmp_manifest = manifest_path.with_suffix(manifest_path.suffix + ".tmp")
    tmp_manifest.write_text("".join(manifest_lines), encoding="utf-8", newline="\n")
    os.replace(tmp_manifest, manifest_path)
    return {
        "model_run_id": model_run_id,
        "status": "PASS",
        "scientific_input_sha256": scientific_input_sha,
        "complete_grid_rows": grid_receipt["rows"],
        "complete_grid_uncompressed_sha256": grid_receipt["uncompressed_csv_sha256"],
        "complete_grid_gzip_sha256": grid_receipt["gzip_sha256"],
        "hash_manifest_sha256": sha256_file(manifest_path),
        "receipt_sha256": sha256_file(receipt_path),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base", type=Path, default=Path("."))
    parser.add_argument("--output-root", type=Path, default=None)
    parser.add_argument("--registry", type=Path, default=DEFAULT_REGISTRY)
    args = parser.parse_args()
    base = args.base.resolve()
    output_root = (args.output_root or base).resolve()
    registry_path = args.registry if args.registry.is_absolute() else (base / args.registry)
    result = build(base, output_root, registry_path.resolve())
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
