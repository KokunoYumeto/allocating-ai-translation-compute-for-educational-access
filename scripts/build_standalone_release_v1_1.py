#!/usr/bin/env python3
"""Build the preservation-safe standalone v1.1 release and upload projections.

The script is deliberately fail-closed.  Its default mode is a read-only
preflight.  Local files are created only with ``--execute``.  It never removes
or rewrites the frozen v1.0 release, archive, staging projections, or receipts.

The build is split into two phases:

* ``build`` assembles the versioned repository tree, manifest, deterministic
  reproducibility ZIP, and GitHub release-asset projection.
* ``stage-zenodo`` first reuses ``verify_release_package.py`` and verifies a
  clean-room smoke receipt for that exact ZIP, then creates the exact Zenodo
  top-level upload projection.
"""

from __future__ import annotations

import argparse
import csv
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
from typing import Any
import zipfile

import build_standalone_release as v1


ROOT = Path(__file__).resolve().parents[1]
VERSION = "1.1.0"
VERSION_TOKEN = "v1_1_0"
DEFAULT_DATE = "2026-08-31"
TITLE_STEM = "Allocating_AI_Translation_Compute_for_Marginal_Educational_Access"

FROZEN_V1_PATHS = {
    (ROOT / "standalone_release_20260830").resolve(),
    (ROOT / "Allocating_AI_Translation_Compute_for_Marginal_Educational_Access_20260830_reproducibility.zip").resolve(),
    (ROOT / "staging" / "github_release_assets_20260830").resolve(),
    (ROOT / "staging" / "zenodo_upload_20260830").resolve(),
    (ROOT / "staging" / "release_metadata_draft_20260830").resolve(),
}

DEFAULT_EXTRA_FILES = {
    "JAPANESE_STAGE_SPECIFIC_ACCESS_ASSESSMENT_20260830.md":
        "JAPANESE_STAGE_SPECIFIC_ACCESS_ASSESSMENT_20260830.md",
    "ZH_HANS_CN_EQUAL_BASIS_AND_RESIDUAL_ASSESSMENT_20260830.md":
        "ZH_HANS_CN_EQUAL_BASIS_AND_RESIDUAL_ASSESSMENT_20260830.md",
    "RESEARCH_FRONTIER_TRANSLATION_AS_EDUCATIONAL_INFRASTRUCTURE_20260830.md":
        "RESEARCH_FRONTIER_TRANSLATION_AS_EDUCATIONAL_INFRASTRUCTURE_20260830.md",
    "scripts/update_top100_needs_v1_1.py":
        "scripts/update_top100_needs_v1_1.py",
    "scripts/update_top100_interlanguage_crosswalk_v1_1.py":
        "scripts/update_top100_interlanguage_crosswalk_v1_1.py",
    "scripts/build_standalone_release_v1_1.py":
        "scripts/build_standalone_release_v1_1.py",
    "scripts/publish_github_standalone_v1_1.py":
        "scripts/publish_github_standalone_v1_1.py",
    "scripts/publish_zenodo_standalone_v1_1.py":
        "scripts/publish_zenodo_standalone_v1_1.py",
    "staging/publication_tooling_20260830/verify_public_release.py":
        "scripts/publication/verify_public_release.py",
    "staging/publication_tooling_20260830/verify_github_release_assets.py":
        "scripts/publication/verify_github_release_assets.py",
}

# Explicit file closure; no repository or workspace enumeration is used to
# discover inputs. Receipt keys containing only a basename resolve here.
PIPELINE_STEPS = (
    "normalize_interlanguage_staging.py", "augment_equal_basis_east_asia_v1_1.py",
    "build_candidate_master_and_join_suggestions.py", "build_edge_curation_queue.py",
    "build_natural_language_scores_v3.py", "build_final_portfolio.py",
    "build_global_expected_universe_v1_1.py", "build_supplemental_typed_population_estimates_v1_1.py",
    "join_expected_universe_to_population_v1_1.py", "build_high_reach_education_needs_v1_1.py",
    "build_denominator_stratified_rankings_v1_1.py", "test_allocation_policy_v1_1.py",
    "test_opportunity_planning_v1_1.py", "test_portfolio_unit_identity_v1_1.py",
    "test_component_scope_v1_1.py", "build_authoritative_exposure_portfolio_v1_1.py",
    "build_top100_companions_v1_1.py",
)
CURRENT_ROOT_FILES = (
    "candidate_population_join_suggestions.csv", "candidate_population_edge_curation_queue.csv",
    "table_a_ex_ante_gross_opportunity.csv", "table_b_target_readable_access_sensitivity.csv",
    "table_c_forward_residual_commissioning.csv", "denominator_stratified_rankings_v1_1_validation.json",
    "top100_commissioning_portfolio_v1_1_validation.json", "allocation_policy_v1_1_validation.json",
    "allocation_policy_sensitivity_v1_1.csv", "opportunity_planning_sensitivity_v1_1.csv",
    "top100_companions_v1_1_validation.json", "V1_1_DATA_PIPELINE_REBUILD_20260831.json",
    "PAPER_V1_1_CONTENT_VALIDATION_20260831.json", "HTML_READER_V1_1_VALIDATION.json",
    "FINAL_DOCUMENT_QA_PUBLIC_20260831.json", "population_observations_normalized.csv",
    "interlanguage_candidates.csv",
)
CURRENT_STAGING_FILES = (
    "global_expected_universe/expected_language_profiles_v1_1.csv",
    "global_expected_universe/bridge_shared_core_hypotheses_v1_1.csv",
    "global_expected_universe/expected_universe_validation_v1_1.json",
    "global_expected_universe/profile_population_estimates_supplement_v1_1.csv",
    "global_expected_universe/profile_population_estimates_supplement_validation_v1_1.json",
    "global_expected_universe/expected_profile_population_joins_v1_1.csv",
    "global_expected_universe/expected_profile_population_joins_validation_v1_1.json",
    "high_reach_education_needs/high_reach_education_needs_v1_1.csv",
    "high_reach_education_needs/high_reach_needs_portfolio_edges_v1_1.csv",
    "authoritative_exposure_portfolio_v1_1/full_computed_allocation_queue.csv",
    "authoritative_exposure_portfolio_v1_1/candidate_dispositions.json",
    "authoritative_exposure_portfolio_v1_1/recovered_lane_and_prior_band_crosswalk.json",
    "authoritative_exposure_portfolio_v1_1/scope_calibrated_planning_crosswalk.json",
    "opportunity_planning_v1_1/asia_core.json", "opportunity_planning_v1_1/large_profiles.json",
    "component_work_ownership_v1_1.json", "reader_surface_v1_1/index.html",
    "interlanguage_matrix/candidate_interventions_agent.csv",
    "interlanguage_matrix/interlanguage_overlap_agent.csv",
    "interlanguage_matrix/candidate_interventions_normalized.csv",
    "target_profile_completion/target_profiles_agent.csv",
    "resolve_unresolved_profiles/profiles.csv",
    "equal_basis_east_asia_v1_1/source_register.csv",
)
CURRENT_SCRIPTS = (*PIPELINE_STEPS,
    "allocation_policy_v1_1.py", "opportunity_planning_v1_1.py", "component_scope_v1_1.py",
    "rebuild_v1_1_data_pipeline.py", "build_paper_v1_1_20260831.py",
    "validate_paper_v1_1_20260831.py", "build_html_reader_v1_1.py",
    "build_standalone_release.py",
)
RECEIPT_INPUT_PATHS = {
    **{name: name for name in (*CURRENT_ROOT_FILES, *v1.DATA_FILES)},
    **{Path(name).name: "staging/" + name for name in CURRENT_STAGING_FILES},
    **{name: "scripts/" + name for name in CURRENT_SCRIPTS},
    "candidate_expansion.csv": "staging/expand_rankable_candidates/candidate_expansion.csv",
    "GLOBAL_GAP_REGISTER.csv": "model_inputs/GLOBAL_GAP_REGISTER.csv",
}
CURRENT_QA_NAMES = (
    "PAPER_V1_1_CONTENT_VALIDATION_20260831.json", "V1_1_DATA_PIPELINE_REBUILD_20260831.json",
    "allocation_policy_v1_1_validation.json", "top100_companions_v1_1_validation.json",
    "HTML_READER_V1_1_VALIDATION.json", "FINAL_DOCUMENT_QA_PUBLIC_20260831.json",
)

GITHUB_ASSET_NAMES = (
    "MANIFEST.sha256",
    "PACKAGE_VALIDATION.json",
    "PAPER.docx",
    "PAPER.md",
    "PAPER.pdf",
)

ZENODO_METADATA_NAMES = (
    "CITATION.cff",
    "CODE_LICENSE",
    "LICENSE",
    "PROVENANCE.md",
    "README.md",
    "THIRD_PARTY_NOTICES.md",
)

FORBIDDEN_TEXT = {
    "absolute_windows_profile": re.compile(r"[A-Za-z]:\\" + r"Users\\[^\\\s]+", re.I),
    "absolute_unix_profile": re.compile("/" + r"Users/[^/\s]+", re.I),
    "github_token": re.compile(r"(?:github_pat_|ghp_)[A-Za-z0-9_]+", re.I),
    "authorization_bearer": re.compile(r"Authorization\s*:\s*Bearer\s+\S+", re.I),
    "zenodo_access_token": re.compile(r"access_token\s*[=:]\s*[^\s\"']+", re.I),
    "email_address": re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.I),
}
PUBLIC_TEXT_REDACTIONS = {
    "EVIDENCE_REGISTER.jsonl",
    "ZH_HANS_CN_EQUAL_BASIS_AND_RESIDUAL_ASSESSMENT_20260830.md",
}


class GateError(RuntimeError):
    """A deterministic release gate failed."""


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest().upper()


def identity(path: Path) -> dict[str, Any]:
    return {"bytes": path.stat().st_size, "sha256": sha256_file(path)}


def atomic_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as handle:
            json.dump(value, handle, indent=2, ensure_ascii=False, sort_keys=True)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    except BaseException:
        try:
            os.unlink(temporary)
        except OSError:
            pass
        raise


def within_root(path: Path) -> Path:
    resolved = path.resolve()
    try:
        resolved.relative_to(ROOT.resolve())
    except ValueError as exc:
        raise GateError(f"path escapes the task root: {path}") from exc
    return resolved


def require_versioned_output(path: Path, label: str) -> Path:
    resolved = within_root(path)
    if resolved in FROZEN_V1_PATHS:
        raise GateError(f"{label} resolves to a frozen v1.0 path")
    if VERSION_TOKEN not in resolved.name.lower():
        raise GateError(f"{label} must contain {VERSION_TOKEN!r} in its name")
    return resolved


def safe_relative(value: str) -> str:
    normalized = value.replace("\\", "/")
    candidate = Path(normalized)
    if candidate.is_absolute() or not normalized or any(part in {"", ".", ".."} for part in candidate.parts):
        raise GateError(f"unsafe release-relative path: {value!r}")
    return candidate.as_posix()


def parse_extra(values: list[str]) -> dict[str, str]:
    result: dict[str, str] = {}
    for value in values:
        source, separator, destination = value.partition("=")
        if not separator:
            raise GateError("--extra-file must be SOURCE_REL=DESTINATION_REL")
        source = safe_relative(source)
        destination = safe_relative(destination)
        if destination in result.values():
            raise GateError(f"duplicate extra destination: {destination}")
        result[source] = destination
    return result


def copy_map(metadata_dir: Path, extras: dict[str, str]) -> dict[Path, str]:
    mappings: list[tuple[Path, str]] = []
    mappings.extend((ROOT / source, destination) for source, destination in v1.CORE_FILES.items())
    mappings.extend((ROOT / name, name) for name in v1.METHOD_FILES)
    mappings.extend((ROOT / name, name) for name in v1.DATA_FILES)
    mappings.extend((ROOT / source, destination) for source, destination in v1.MODEL_INPUT_FILES.items())
    mappings.extend((ROOT / name, name) for name in v1.EVIDENCE_FILES)
    # Historical QA remains in the immutable v1.0 publication. It must not be
    # repackaged as validation of the revised paper.
    mappings.extend((ROOT / source, destination) for source, destination in v1.SCRIPT_FILES.items())
    mappings.append((ROOT / "requirements.txt", "requirements.txt"))
    mappings.extend((metadata_dir / name, name) for name in v1.METADATA_FILES)
    mappings.extend((ROOT / name, name) for name in CURRENT_ROOT_FILES)
    mappings.extend((ROOT / "staging" / name, "staging/" + name) for name in CURRENT_STAGING_FILES)
    mappings.extend((ROOT / "scripts" / name, "scripts/" + name) for name in CURRENT_SCRIPTS)
    mappings.extend((ROOT / name, name) for name in (
        "model_inputs/GLOBAL_GAP_REGISTER.csv", "model_inputs/155_COMPUTE_TOKEN_AUDIT_33_ROOTS_20260830.json",
        "sources/LOC_ISO_639_2_utf8_20260825.txt",
        "population_source_register_master.csv",
    ))
    document_qa = ROOT / "FINAL_DOCUMENT_QA_PUBLIC_20260831.json"
    if document_qa.is_file():
        document = load_json(document_qa, "current document QA")
        for section_name in ("source_checks", "mechanical", "visual", "html_visual"):
            section = document.get(section_name) or {}
            candidates = list(section.get("receipts") or [])
            candidates.extend(value for value in section.values() if isinstance(value, dict) and value.get("path"))
            for receipt in candidates:
                relative = safe_relative(str(receipt.get("path", "")))
                mappings.append((ROOT / relative, relative))
    combined_extras = dict(DEFAULT_EXTRA_FILES)
    combined_extras.update(extras)
    mappings.extend((ROOT / source, destination) for source, destination in combined_extras.items())

    result: dict[Path, str] = {}
    destinations: dict[str, Path] = {}
    for source, destination_raw in mappings:
        source = within_root(source)
        destination = safe_relative(destination_raw)
        prior = destinations.get(destination)
        if prior is not None and prior != source:
            raise GateError(f"release destination collision: {destination}")
        destinations[destination] = source
        result[source] = destination
    return result


def load_json(path: Path, label: str) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise GateError(f"cannot read {label}: {path.name}") from exc
    if not isinstance(value, dict):
        raise GateError(f"{label} must be a JSON object")
    return value


def assert_identity(path: Path, expected: dict[str, Any], label: str) -> None:
    observed = identity(path)
    wanted = {
        "bytes": int(expected.get("bytes", -1)),
        "sha256": str(expected.get("sha256", "")).upper(),
    }
    if observed != wanted:
        raise GateError(f"{label} identity does not match its controlling receipt")


def validate_results_manifest(path: Path) -> dict[str, Any]:
    manifest = load_json(path, "results manifest")
    for section_name in ("input_identity", "outputs"):
        section = manifest.get(section_name)
        if not isinstance(section, dict) or not section:
            raise GateError(f"results manifest lacks {section_name}")
        for relative, expected in section.items():
            if not isinstance(expected, dict):
                raise GateError(f"invalid identity for {relative} in results manifest")
            candidate = within_root(ROOT / safe_relative(relative))
            if not candidate.is_file():
                raise GateError(f"results manifest file is missing: {relative}")
            assert_identity(candidate, expected, f"results manifest file {relative}")
    return manifest


def bound_file(base: Path, relative: str) -> Path:
    candidate = (base / safe_relative(relative)).resolve()
    try:
        candidate.relative_to(base.resolve())
    except ValueError as exc:
        raise GateError("receipt path escapes its artifact root") from exc
    if not candidate.is_file() or candidate.is_symlink():
        raise GateError(f"required regular artifact missing: {relative}")
    return candidate


def pass_checks(value: dict[str, Any], label: str) -> None:
    if value.get("status") != "PASS":
        raise GateError(f"{label} is not PASS")
    checks = value.get("checks")
    if checks is not None and (not isinstance(checks, dict) or not checks or any(v is not True for v in checks.values())):
        raise GateError(f"{label} has a missing or failed deterministic check")


def verify_bound_inputs(base: Path, entries: dict[str, Any], label: str) -> None:
    if not isinstance(entries, dict) or not entries:
        raise GateError(f"{label} has no bound identities")
    for name, expected in entries.items():
        relative = RECEIPT_INPUT_PATHS.get(name)
        if relative is None:
            raise GateError(f"{label} contains an unmapped input: {name}")
        assert_identity(bound_file(base, relative), expected, f"{label}/{name}")


def validate_qa(base: Path | None = None) -> dict[str, Any]:
    """Validate actual v1.1 bytes, including every-page inspection coverage.

    ``base`` can be the local task or the assembled release. No filesystem
    timestamp is used as a substitute for cryptographic input identity.
    """
    base = ROOT if base is None else base.resolve()
    receipts = {name: load_json(bound_file(base, name), name) for name in CURRENT_QA_NAMES}
    expected_schemas = {
        "PAPER_V1_1_CONTENT_VALIDATION_20260831.json": "interlanguage/paper-v1-1-content-validation/1.0.0",
        "V1_1_DATA_PIPELINE_REBUILD_20260831.json": "interlanguage/v1-1-data-pipeline-rebuild/1.1.0",
        "allocation_policy_v1_1_validation.json": "interlanguage/allocation-policy-validation/1.1.0",
        "top100_companions_v1_1_validation.json": "interlanguage/top100-companions-validation/1.1.0",
        "HTML_READER_V1_1_VALIDATION.json": "research-paper-html/1.1",
        "FINAL_DOCUMENT_QA_PUBLIC_20260831.json": "research-paper-final-document-qa/1.1",
    }
    for name, schema in expected_schemas.items():
        if receipts[name].get("schema") != schema:
            raise GateError(f"{name} has an unexpected schema")
    content = receipts[CURRENT_QA_NAMES[0]]
    pipeline = receipts[CURRENT_QA_NAMES[1]]
    policy = receipts[CURRENT_QA_NAMES[2]]
    companions = receipts[CURRENT_QA_NAMES[3]]
    html = receipts[CURRENT_QA_NAMES[4]]
    document = receipts[CURRENT_QA_NAMES[5]]
    for name, receipt in (("content", content), ("pipeline", pipeline), ("allocation policy", policy), ("Top-100 companions", companions)):
        pass_checks(receipt, name)
    steps = pipeline.get("steps") or []
    if [row.get("script") for row in steps] != list(PIPELINE_STEPS) or any(row.get("exit_code") != 0 for row in steps):
        raise GateError("the exact current data/test pipeline has not passed")
    verify_bound_inputs(base, pipeline.get("outputs"), "pipeline")
    verify_bound_inputs(base, policy.get("inputs"), "allocation policy")
    for field, name in (("paper", "PAPER.md"), ("top100", "TOP_100.csv"), ("top10", "TOP_10.csv"),
                        ("forward", "table_c_forward_residual_commissioning.csv"),
                        ("compute_receipt", "compute_token_audit_33_roots_20260830.json"),
                        ("allocation_policy_receipt", "allocation_policy_v1_1_validation.json")):
        assert_identity(bound_file(base, name), content.get(field) or {}, f"content/{name}")
    for field, name in (("top100", "TOP_100.csv"), ("needs", "top100_needs_assignment_v2.csv"),
                        ("crosswalk", "top100_interlanguage_overlap_crosswalk.csv"),
                        ("matrix", "staging/interlanguage_bundle_model/interlanguage_intervention_matrix.csv"),
                        ("forward_table", "table_c_forward_residual_commissioning.csv")):
        assert_identity(bound_file(base, name), companions.get(field) or {}, f"companions/{name}")
    pass_checks(document, "current final document QA")
    if document.get("release_version") != VERSION:
        raise GateError("final document QA does not identify release 1.1.0")
    for field, expected_path in (("paper_md", "PAPER.md"), ("docx", "PAPER.docx"), ("pdf", "PAPER.pdf")):
        artifact = document.get(field) or {}
        if artifact.get("path") != expected_path:
            raise GateError(f"document QA has the wrong {field} path")
        assert_identity(bound_file(base, expected_path), artifact, f"document QA/{field}")
    for field in ("source_checks", "mechanical", "visual", "html_visual"):
        if (document.get(field) or {}).get("status") != "PASS":
            raise GateError(f"current final QA lacks a passing {field}")
    for field, keys in (
        ("source_checks", ("content_validation", "pipeline_rebuild", "reference_verification")),
        ("mechanical", ("structural_qa", "accessibility_audit")),
    ):
        section = document[field]
        for key in keys:
            entry = section.get(key) or {}
            assert_identity(bound_file(base, str(entry.get("path", ""))), entry, f"document QA/{field}/{key}")
    pages = (document.get("pdf") or {}).get("pages")
    if not isinstance(pages, int) or isinstance(pages, bool) or pages < 1:
        raise GateError("final QA has no positive PDF page count")
    visual = document["visual"]
    if visual.get("pages_inspected") != list(range(1, pages + 1)):
        raise GateError("visual QA does not cover every current PDF page exactly once")
    visual_receipts = visual.get("receipts") or []
    if not isinstance(visual_receipts, list) or not visual_receipts:
        raise GateError("every-page visual QA has no hashed evidence receipts")
    for receipt in visual_receipts:
        assert_identity(bound_file(base, str(receipt.get("path", ""))), receipt, "visual QA receipt")
    final_visual = load_json(bound_file(base, str(visual_receipts[0].get("path", ""))), "final visual QA")
    if final_visual.get("schema") != "research-paper-visual-qa/1.1" or final_visual.get("status") != "PASS":
        raise GateError("final visual QA receipt has an unexpected schema or status")
    paper_hash = sha256_file(bound_file(base, "PAPER.md"))
    reader = bound_file(base, "staging/reader_surface_v1_1/index.html")
    reader_hash = sha256_file(reader)
    if str(html.get("source_sha256", "")).upper() != paper_hash or str(html.get("html_sha256", "")).upper() != reader_hash:
        raise GateError("HTML validation does not bind the current paper and reader")
    if html.get("status") not in {"PASS", "STRUCTURAL_PASS_VISUAL_REVIEW_PENDING", "STRUCTURAL_AND_VISUAL_PASS"}:
        raise GateError("HTML structure has not passed")
    if html.get("broken_internal_links") != [] or html.get("external_runtime_dependencies") != 0:
        raise GateError("HTML reader has broken internal links or external runtime dependencies")
    if not html.get("tables") or any(row.get("cell_roundtrip") is not True for row in html["tables"]):
        raise GateError("HTML table source roundtrip has not passed")
    hv = document["html_visual"]
    if str(hv.get("source_sha256", "")).upper() != paper_hash or str(hv.get("html_sha256", "")).upper() != reader_hash:
        raise GateError("HTML visual QA is stale")
    html_visual_receipts = hv.get("receipts") or []
    if not isinstance(html_visual_receipts, list) or not html_visual_receipts:
        raise GateError("HTML visual QA has no hashed evidence receipt")
    for receipt in html_visual_receipts:
        receipt_path = bound_file(base, str(receipt.get("path", "")))
        assert_identity(receipt_path, receipt, "HTML visual QA receipt")
        observed = load_json(receipt_path, "HTML visual QA receipt")
        if observed.get("schema") != "research-paper-html-visual-qa/1.1" or observed.get("status") != "PASS":
            raise GateError("HTML visual QA receipt has an unexpected schema or status")
    return {
        "receipts": {name: identity(base / name) for name in CURRENT_QA_NAMES},
        "paper": identity(base / "PAPER.md"), "docx": identity(base / "PAPER.docx"),
        "pdf": {**identity(base / "PAPER.pdf"), "pages": pages},
        "html": identity(reader), "visual_pages_verified": pages,
    }


def validate_metadata(metadata_dir: Path, version: str, version_doi: str, release_date: str) -> dict[str, Any]:
    if version != VERSION:
        raise GateError(f"this lane only accepts version {VERSION}")
    if not re.fullmatch(r"10\.5281/zenodo\.[0-9]+", version_doi):
        raise GateError("--version-doi must be a concrete Zenodo version DOI")
    if version_doi in {"10.5281/zenodo.22172595", "10.5281/zenodo.22172596"}:
        raise GateError("v1.1 must use a new version DOI, not the concept or v1.0 DOI")
    try:
        dt.date.fromisoformat(release_date)
    except ValueError as exc:
        raise GateError("--release-date must be YYYY-MM-DD") from exc

    required = tuple(v1.METADATA_FILES)
    for name in required:
        if not (metadata_dir / name).is_file():
            raise GateError(f"metadata draft is missing {name}")
    zenodo = load_json(metadata_dir / "zenodo_metadata.json", "Zenodo metadata")
    metadata = zenodo.get("metadata") or {}
    if str(metadata.get("version")) != version:
        raise GateError("zenodo_metadata.json has the wrong version")
    if str(metadata.get("publication_date")) != release_date:
        raise GateError("zenodo_metadata.json has the wrong publication date")
    if str(metadata.get("access_right", "")).lower() != "open":
        raise GateError("Zenodo access_right must remain open")

    cff = (metadata_dir / "CITATION.cff").read_text(encoding="utf-8")
    readme = (metadata_dir / "README.md").read_text(encoding="utf-8")
    provenance = (metadata_dir / "PROVENANCE.md").read_text(encoding="utf-8")
    metadata_text = json.dumps(zenodo, ensure_ascii=False)
    for label, text in (("CITATION.cff", cff), ("README.md", readme), ("PROVENANCE.md", provenance), ("zenodo_metadata.json", metadata_text)):
        if version_doi not in text:
            raise GateError(f"{label} does not contain the v1.1 version DOI")
    if not re.search(r"(?m)^version:\s*[\"']?1\.1\.0[\"']?\s*$", cff):
        raise GateError("CITATION.cff does not declare version 1.1.0")
    if not re.search(r"(?m)^date-released:\s*[\"']?" + re.escape(release_date) + r"[\"']?\s*$", cff):
        raise GateError("CITATION.cff has the wrong release date")
    return {name: identity(metadata_dir / name) for name in required}


def validate_sources(mappings: dict[Path, str]) -> None:
    for source in mappings:
        if not source.is_file():
            raise GateError(f"required release input is missing: {source.relative_to(ROOT)}")
        if source.is_symlink():
            raise GateError(f"release input may not be a symlink: {source.relative_to(ROOT)}")


def scan_public_text(directory: Path) -> list[dict[str, str]]:
    binary_suffixes = {".docx", ".pdf", ".png"}
    findings: list[dict[str, str]] = []
    for path in sorted(item for item in directory.rglob("*") if item.is_file()):
        if path.suffix.lower() == ".zip":
            try:
                with zipfile.ZipFile(path) as archive:
                    names = [entry.filename for entry in archive.infolist()]
                    if len(names) != len(set(names)) or archive.testzip() is not None:
                        raise GateError("invalid ZIP inventory or CRC")
                    for name in names:
                        safe_relative(name.rstrip("/"))
            except (OSError, zipfile.BadZipFile, GateError):
                findings.append({"path": path.relative_to(directory).as_posix(), "rule": "invalid_zip"})
            continue
        if path.suffix.lower() in binary_suffixes:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            findings.append({"path": path.relative_to(directory).as_posix(), "rule": "non_utf8_text"})
            continue
        for rule, pattern in FORBIDDEN_TEXT.items():
            if pattern.search(text):
                findings.append({"path": path.relative_to(directory).as_posix(), "rule": rule})
    return findings


def write_manifest(release_dir: Path) -> None:
    paths = sorted(item for item in release_dir.rglob("*") if item.is_file() and item.name != "MANIFEST.sha256")
    lines = [f"{sha256_file(path)}  {path.relative_to(release_dir).as_posix()}" for path in paths]
    (release_dir / "MANIFEST.sha256").write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")


def write_deterministic_zip(release_dir: Path, zip_path: Path, release_date: str) -> None:
    date = dt.date.fromisoformat(release_date)
    zip_time = (date.year, date.month, date.day, 0, 0, 0)
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for path in sorted(item for item in release_dir.rglob("*") if item.is_file()):
            info = zipfile.ZipInfo(path.relative_to(release_dir).as_posix())
            info.date_time = zip_time
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            archive.writestr(info, path.read_bytes(), compress_type=zipfile.ZIP_DEFLATED, compresslevel=9)


def run_package_verifier(release_dir: Path, zip_path: Path) -> dict[str, Any]:
    verifier = ROOT / "scripts" / "verify_release_package.py"
    result = subprocess.run(
        [sys.executable, str(verifier), str(release_dir), str(zip_path)],
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise GateError("verify_release_package.py rejected the v1.1 package")
    try:
        payload = json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        raise GateError("verify_release_package.py returned invalid JSON") from exc
    if payload.get("status") != "PASS":
        raise GateError("verify_release_package.py did not return PASS")
    return payload


def copy_regular(source: Path, destination: Path) -> None:
    if source.is_symlink() or not source.is_file():
        raise GateError(f"cannot stage non-regular file: {source.name}")
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, destination)


def copy_public_population_register(source: Path, destination: Path) -> dict[str, Any]:
    """Redact only private locators; retain all analytical cell values."""
    with source.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        fields = reader.fieldnames
        rows = list(reader)
    if not fields or "local_witness_path" not in fields:
        raise GateError("population source register has no locator column")
    analytical_fields = [field for field in fields if field != "local_witness_path"]
    before = [[row[field] for field in analytical_fields] for row in rows]
    changed = 0
    for row in rows:
        locator = row.get("local_witness_path") or ""
        if re.search(r"(?:[A-Za-z]:[\\/]|^/)", locator):
            row["local_witness_path"] = "Private local locator omitted; use the retained public URL and source identity."
            changed += 1
    destination.parent.mkdir(parents=True, exist_ok=True)
    with destination.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    with destination.open("r", encoding="utf-8", newline="") as handle:
        copied = list(csv.DictReader(handle))
    if before != [[row[field] for field in analytical_fields] for row in copied]:
        raise GateError("population-register redaction changed analytical cells")
    return {
        "source": "population_source_register_master.csv", "source_identity": identity(source),
        "public_path": "population_source_register_master.csv", "public_identity": identity(destination),
        "rows": len(rows), "redacted_column": "local_witness_path", "redacted_cells": changed,
        "all_other_cell_values_preserved": True,
    }


def copy_public_text_redacted(source: Path, destination: Path) -> dict[str, Any]:
    """Remove only private profile prefixes from a known public evidence file."""
    try:
        text = source.read_text(encoding="utf-8")
    except UnicodeDecodeError as exc:
        raise GateError(f"cannot redact non-UTF-8 public text: {source.name}") from exc
    windows = re.compile(r"[A-Za-z]:\\" + r"Users\\[^\\\s]+", re.I)
    unix = re.compile("/" + r"Users/[^/\s]+", re.I)
    transformed, count_windows = windows.subn("<private-local-profile>", text)
    transformed, count_unix = unix.subn("<private-local-profile>", transformed)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(transformed, encoding="utf-8", newline="\n")
    return {
        "source": source.relative_to(ROOT).as_posix(),
        "source_identity": identity(source),
        "public_path": destination.name,
        "public_identity": identity(destination),
        "redacted_private_profile_prefixes": count_windows + count_unix,
        "other_text_preserved": True,
    }


def preflight(args: argparse.Namespace) -> tuple[dict[Path, str], dict[str, Any]]:
    metadata_dir = within_root(args.metadata_dir)
    release_dir = require_versioned_output(args.release_dir, "release directory")
    zip_path = require_versioned_output(args.zip_path, "ZIP path")
    github_assets = require_versioned_output(args.github_assets_dir, "GitHub asset directory")
    zenodo_upload = require_versioned_output(args.zenodo_upload_dir, "Zenodo upload directory")
    extras = parse_extra(args.extra_file)
    mappings = copy_map(metadata_dir, extras)
    validate_sources(mappings)
    qa = validate_qa()
    metadata = validate_metadata(metadata_dir, args.version, args.version_doi, args.release_date)

    if args.mode == "build":
        for path, label in ((release_dir, "release directory"), (zip_path, "ZIP"), (github_assets, "GitHub asset directory")):
            if path.exists():
                raise GateError(f"{label} already exists: {path.name}")
    else:
        if not release_dir.is_dir() or not zip_path.is_file() or not github_assets.is_dir():
            raise GateError("stage-zenodo requires the completed release, ZIP, and GitHub projection")
        if zenodo_upload.exists():
            raise GateError(f"Zenodo upload directory already exists: {zenodo_upload.name}")
        if args.smoke_receipt is None:
            raise GateError("stage-zenodo requires --smoke-receipt")

    plan = {
        "schema": "standalone-v1.1-release-plan/1.0",
        "status": "PREFLIGHT_PASS",
        "mode": args.mode,
        "version": args.version,
        "version_doi": args.version_doi,
        "release_date": args.release_date,
        "release_dir": release_dir.relative_to(ROOT).as_posix(),
        "zip_path": zip_path.relative_to(ROOT).as_posix(),
        "github_assets_dir": github_assets.relative_to(ROOT).as_posix(),
        "zenodo_upload_dir": zenodo_upload.relative_to(ROOT).as_posix(),
        "release_input_files": len(mappings),
        "qa_gate": qa,
        "metadata_gate": metadata,
        "frozen_v1_paths_touched": [],
    }
    return mappings, plan


def build(args: argparse.Namespace, mappings: dict[Path, str], plan: dict[str, Any]) -> dict[str, Any]:
    release_dir = args.release_dir.resolve()
    zip_path = args.zip_path.resolve()
    github_assets = args.github_assets_dir.resolve()
    release_dir.mkdir(parents=True)
    try:
        privacy_transforms = []
        for source, destination in mappings.items():
            if destination == "population_source_register_master.csv":
                privacy_transforms.append(copy_public_population_register(source, release_dir / destination))
            elif destination in PUBLIC_TEXT_REDACTIONS:
                privacy_transforms.append(copy_public_text_redacted(source, release_dir / destination))
            else:
                copy_regular(source, release_dir / destination)
        copy_regular(release_dir / "staging" / "reader_surface_v1_1" / "index.html", release_dir / "index.html")
        (release_dir / ".nojekyll").write_bytes(b"")
        atomic_json(release_dir / "PUBLIC_INPUT_REDACTIONS.json", {
            "schema": "standalone-public-input-redactions/1.0", "transformations": privacy_transforms,
        })
        # The release copy is independently checked, rather than inheriting a
        # PASS merely because the source tree passed before it was copied.
        validate_qa(release_dir)
        findings = scan_public_text(release_dir)
        if findings:
            raise GateError("public-text privacy scan failed: " + json.dumps(findings, ensure_ascii=False))

        validation = {
            "schema": "standalone-ai-compute-access-release-validation/1.1.0",
            "generated_at_utc": dt.datetime.now(dt.timezone.utc).isoformat().replace("+00:00", "Z"),
            "release_version": args.version,
            "release_date": args.release_date,
            "version_doi": args.version_doi,
            "status": "PASS",
            "validated_input_files": len(mappings),
            "privacy_scan_findings": findings,
            "qa_gate": plan["qa_gate"],
            "metadata_gate": plan["metadata_gate"],
            "paper": {
                "markdown_sha256": sha256_file(release_dir / "PAPER.md"),
                "docx_sha256": sha256_file(release_dir / "PAPER.docx"),
                "pdf_sha256": sha256_file(release_dir / "PAPER.pdf"),
            },
            "notes": [
                "PASS is emitted only after identity, freshness, QA, metadata, and privacy gates pass.",
                "Third-party source bytes and private source-witness paths are excluded.",
                "MANIFEST.sha256 intentionally does not hash itself.",
                "Legacy FR-2 source tables are retained as model inputs, not as the current commissioning order.",
                "Current recommendations are PAPER, TOP_10, TOP_100 and their v1.1 companions and receipts.",
            ],
        }
        atomic_json(release_dir / "PACKAGE_VALIDATION.json", validation)
        write_manifest(release_dir)
        write_deterministic_zip(release_dir, zip_path, args.release_date)
        verification = run_package_verifier(release_dir, zip_path)

        github_assets.mkdir(parents=True)
        copy_regular(zip_path, github_assets / zip_path.name)
        for name in GITHUB_ASSET_NAMES:
            copy_regular(release_dir / name, github_assets / name)

        result = dict(plan)
        result.update({
            "status": "BUILT_AND_LOCALLY_VERIFIED",
            "release_files": sum(1 for path in release_dir.rglob("*") if path.is_file()),
            "release_bytes": sum(path.stat().st_size for path in release_dir.rglob("*") if path.is_file()),
            "zip": {"filename": zip_path.name, **identity(zip_path)},
            "manifest": identity(release_dir / "MANIFEST.sha256"),
            "github_assets": [
                {"filename": path.name, **identity(path)}
                for path in sorted(github_assets.iterdir()) if path.is_file()
            ],
            "package_verifier": verification,
        })
        return result
    except BaseException:
        # Outputs are new versioned siblings.  Leave partial bytes in place for
        # diagnosis; never delete or touch any frozen v1.0 path.
        raise


def stage_zenodo(args: argparse.Namespace, plan: dict[str, Any]) -> dict[str, Any]:
    release_dir = args.release_dir.resolve()
    zip_path = args.zip_path.resolve()
    github_assets = args.github_assets_dir.resolve()
    zenodo_upload = args.zenodo_upload_dir.resolve()
    smoke_path = within_root(args.smoke_receipt)
    smoke = load_json(smoke_path, "clean-room smoke receipt")
    if str(smoke.get("status", "")).upper() != "PASS":
        raise GateError("clean-room smoke receipt status is not PASS")
    archive = smoke.get("input_archive") or {}
    assert_identity(zip_path, archive, "clean-room smoke-test archive")
    verification = run_package_verifier(release_dir, zip_path)

    expected_github = {zip_path.name, *GITHUB_ASSET_NAMES}
    observed_github = {path.name for path in github_assets.iterdir() if path.is_file()}
    if observed_github != expected_github:
        raise GateError("GitHub asset projection no longer has its exact six-file topology")

    zenodo_upload.mkdir(parents=True)
    try:
        for path in sorted(github_assets.iterdir()):
            if path.is_file():
                copy_regular(path, zenodo_upload / path.name)
        for name in ZENODO_METADATA_NAMES:
            copy_regular(release_dir / name, zenodo_upload / name)
        qa_name = "FINAL_DOCUMENT_QA_PUBLIC_20260831.json"
        copy_regular(release_dir / qa_name, zenodo_upload / qa_name)
        copy_regular(smoke_path, zenodo_upload / smoke_path.name)
        findings = scan_public_text(zenodo_upload)
        if findings:
            raise GateError("Zenodo projection privacy scan failed: " + json.dumps(findings, ensure_ascii=False))
        inventory = [
            {"filename": path.name, **identity(path)}
            for path in sorted(zenodo_upload.iterdir()) if path.is_file()
        ]
        if len(inventory) != 14:
            raise GateError(f"Zenodo projection must contain exactly 14 files, observed {len(inventory)}")
        result = dict(plan)
        result.update({
            "status": "ZENODO_PROJECTION_STAGED_AND_LOCALLY_VERIFIED",
            "package_verifier": verification,
            "smoke_receipt": {"filename": smoke_path.name, **identity(smoke_path)},
            "zenodo_inventory": inventory,
            "required_default_preview": "PAPER.pdf",
        })
        return result
    except BaseException:
        raise


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", choices=("build", "stage-zenodo"), default="build")
    parser.add_argument("--version", default=VERSION)
    parser.add_argument("--version-doi", required=True)
    parser.add_argument("--release-date", default=DEFAULT_DATE)
    parser.add_argument("--metadata-dir", type=Path, default=ROOT / "staging" / f"release_metadata_draft_{VERSION_TOKEN}_20260831")
    parser.add_argument("--release-dir", type=Path, default=ROOT / f"standalone_release_{VERSION_TOKEN}_20260831")
    parser.add_argument("--zip-path", type=Path, default=ROOT / f"{TITLE_STEM}_{VERSION_TOKEN}_20260831_reproducibility.zip")
    parser.add_argument("--github-assets-dir", type=Path, default=ROOT / "staging" / f"github_release_assets_{VERSION_TOKEN}_20260831")
    parser.add_argument("--zenodo-upload-dir", type=Path, default=ROOT / "staging" / f"zenodo_upload_{VERSION_TOKEN}_20260831")
    parser.add_argument("--smoke-receipt", type=Path)
    parser.add_argument("--extra-file", action="append", default=[], metavar="SOURCE_REL=DESTINATION_REL")
    parser.add_argument("--execute", action="store_true", help="create the new versioned local outputs; default is read-only preflight")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        mappings, plan = preflight(args)
        if not args.execute:
            print(json.dumps(plan, indent=2, ensure_ascii=False))
            return 0
        if args.mode == "build":
            result = build(args, mappings, plan)
        else:
            result = stage_zenodo(args, plan)
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return 0
    except GateError as exc:
        print(json.dumps({
            "schema": "standalone-v1.1-release-error/1.0",
            "status": "FAIL_CLOSED",
            "error": str(exc),
            "frozen_v1_paths_touched": [],
        }, indent=2), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
