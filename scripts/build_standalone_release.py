#!/usr/bin/env python3
"""Assemble the bounded public standalone paper and reproducibility release."""

from __future__ import annotations

import hashlib
import json
import re
import shutil
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RELEASE = ROOT / "standalone_release_20260830"
ZIP_PATH = ROOT / "Allocating_AI_Translation_Compute_for_Marginal_Educational_Access_20260830_reproducibility.zip"
METADATA_DRAFT = ROOT / "staging" / "release_metadata_draft_20260830"


CORE_FILES = {
    "PAPER.md": "PAPER.md",
    "PAPER.docx": "PAPER.docx",
    "PAPER.pdf": "PAPER.pdf",
    "figure_1_rank_sensitivity.png": "figure_1_rank_sensitivity.png",
    "figure_1_rank_sensitivity.svg": "figure_1_rank_sensitivity.svg",
    "figure_1_rank_sensitivity_data.csv": "figure_1_rank_sensitivity_data.csv",
}

METHOD_FILES = [
    "MODEL_SPEC.md",
    "FACTOR_POLICY.md",
    "RANKING_METHOD.md",
    "NEEDS_LAYER_20260830.md",
    "TOP100_NEEDS_METHOD_20260830.md",
    "TOP100_INTERLANGUAGE_CROSSWALK_METHOD_20260830.md",
    "TOP100_INTERLANGUAGE_CROSSWALK_VALIDATION_RECEIPT_20260830.md",
    "POPULATION_OBSERVATION_USE_RULES.md",
    "SEARCH_PROTOCOL.md",
    "TABLE_SOURCE_REFERENCES.md",
    "REFERENCE_VERIFICATION_20260830.md",
    "EVIDENCE_REGISTER.jsonl",
]

DATA_FILES = [
    "population_source_register_public.csv",
    "population_observations_master.csv",
    "candidate_interventions_master.csv",
    "candidate_expansion_scores.csv",
    "source_id_reference_crosswalk.csv",
    "corpus_method_reference_crosswalk.csv",
    "natural_language_scores_v3.csv",
    "portfolio_linguistic_candidates.csv",
    "portfolio_scale_planning.csv",
    "TOP_10.csv",
    "TOP_100.csv",
    "population_mathematics_needs_register.csv",
    "top100_needs_assignment_v2.csv",
    "top100_interlanguage_overlap_crosswalk.csv",
    "negative_controls_and_profile_exclusions.csv",
    "interlanguage_package_scores.csv",
    "package_replacement_decisions.csv",
    "curriculum_units.csv",
    "curriculum_portfolios.csv",
    "openstax_workload_measurements.csv",
    "accessibility_priority_backlog.csv",
    "adaptation_depths.csv",
    "indonesian_equal_basis_and_forward_allocation.csv",
    "compute_assumptions.csv",
    "compute_scenarios.csv",
    "compute_observations.csv",
    "portfolio_compute_scenarios.csv",
    "GRANT_COMPUTE_SCENARIOS_LOW_BASE_HIGH.csv",
    "SHARED_CORE_ARCHITECTURE_LOW_BASE_HIGH.csv",
    "IMPLEMENTED_VS_UNIMPLEMENTED_SENSITIVITY_MATRIX.csv",
    "country_access_indicators.csv",
    "country_home_language_instruction.csv",
    "education_access_observations.csv",
    "ai_language_support.csv",
    "openalex_math_language_counts.csv",
    "wikimedia_language_stats.csv",
    "india_c17_overlap.csv",
    "walter_benson_not_used_size_bands.csv",
    "accessibility_derivatives.csv",
    "candidate_context_features.csv",
    "appendix_a_existing_work_reconciliation.csv",
    "appendix_a_state_definitions.csv",
    "appendix_b_global_gap_map.csv",
    "appendix_b_regional_gap_summary.csv",
    "appendix_b_source_measure_confidence.csv",
    "appendix_c_accessibility_safeguards.csv",
    "appendix_d_adaptation_depths.csv",
    "appendix_d_curriculum_portfolios.csv",
    "appendix_d_top100_curriculum_mapping.csv",
    "appendix_e_unresolved_profiles_and_d0.csv",
    "appendix_f_interlanguage_matrix_summary.csv",
    "appendix_f_matrix_scope_counts.csv",
    "table2_exact_gross_ceilings.csv",
    "table3_marginal_access_sensitivity_ranges.csv",
    "table4_top10.csv",
    "table5_top100_grouped_lanes.csv",
    "table5_top100_members.csv",
    "table6_package_exclusions_noncardinal.csv",
    "table6a_architecture_sensitivity_noncardinal.csv",
    "table7_curriculum_allocation_summary.csv",
    "table8_negative_controls_and_exclusions.csv",
]

MODEL_INPUT_FILES = {
    "staging/accessibility_recovery/accessibility_population_strata.csv": "staging/accessibility_recovery/accessibility_population_strata.csv",
    "staging/expand_rankable_candidates/candidate_expansion.csv": "staging/expand_rankable_candidates/candidate_expansion.csv",
    "staging/interlanguage_bundle_model/interlanguage_intervention_matrix.csv": "staging/interlanguage_bundle_model/interlanguage_intervention_matrix.csv",
    "staging/interlanguage_bundle_model/interlanguage_population_links.csv": "staging/interlanguage_bundle_model/interlanguage_population_links.csv",
    "staging/interlanguage_matrix/interlanguage_overlap_normalized.csv": "staging/interlanguage_matrix/interlanguage_overlap_normalized.csv",
}

EVIDENCE_FILES = [
    "CURRENT_INDONESIAN_PROGRAM_STATUS_20260830.md",
    "INDONESIAN_EQUAL_BASIS_CORRECTION_20260830.md",
    "INDONESIAN_PUBLIC_PROGRAM_AUDIT_20260830.md",
    "INDONESIAN_TASK_TOKEN_AUDIT_20260830.md",
    "INDONESIAN_PROGRAM_COMPUTE_AND_PAGE_RECONCILIATION_PUBLIC_20260830.md",
    "compute_token_audit_33_roots_20260830.json",
]

QA_FILES = {
    "FINAL_CONTENT_VALIDATION_20260830.json": "qa/FINAL_CONTENT_VALIDATION_20260830.json",
    "FINAL_CONTENT_VALIDATION_20260830.md": "qa/FINAL_CONTENT_VALIDATION_20260830.md",
    "FINAL_DOCUMENT_QA_PUBLIC_20260830.json": "qa/FINAL_DOCUMENT_QA_PUBLIC_20260830.json",
    "staging/final_pdf_audit/FINAL_PDF_MECHANICAL_AUDIT_20260830.json": "qa/FINAL_PDF_MECHANICAL_AUDIT_20260830.json",
    "NUMERICAL_AUDIT_20260830.md": "qa/NUMERICAL_AUDIT_20260830.md",
    "RESULTS_TABLES_MANIFEST.json": "qa/RESULTS_TABLES_MANIFEST.json",
    "RESULTS_TABLES_VALIDATION.md": "qa/RESULTS_TABLES_VALIDATION.md",
    "INTERLANGUAGE_PACKAGE_SCORE_VALIDATION.md": "qa/INTERLANGUAGE_PACKAGE_SCORE_VALIDATION.md",
    "PORTFOLIO_BUILD_STATUS.json": "qa/PORTFOLIO_BUILD_STATUS.json",
    "staging/final_pdf_audit/FINAL_PDF_AUDIT.json": "qa/FINAL_PDF_AUDIT.json",
    "staging/final_pdf_audit/FINAL_PDF_AUDIT.md": "qa/FINAL_PDF_AUDIT.md",
    "staging/final_paper_audit/MACHINE_CHECK_RESULTS.json": "qa/MACHINE_CHECK_RESULTS.json",
    "staging/final_paper_audit/FINAL_PAPER_AUDIT_REPORT.md": "qa/FINAL_PAPER_AUDIT_REPORT.md",
}

SCRIPT_FILES = {
    "scripts/build_results_tables.py": "scripts/build_results_tables.py",
    "scripts/build_rank_sensitivity_figure.py": "scripts/build_rank_sensitivity_figure.py",
    "scripts/validate_final_publication_content.py": "scripts/validate_final_publication_content.py",
    "scripts/normalize_ascii_dashes.py": "scripts/normalize_ascii_dashes.py",
    "scripts/refresh_embedded_appendices_20260830.py": "scripts/refresh_embedded_appendices_20260830.py",
    "scripts/verify_release_package.py": "scripts/verify_release_package.py",
    "staging/document_builder/build_report_docx.py": "scripts/document/build_report_docx.py",
    "staging/document_builder/qa_docx.py": "scripts/document/qa_docx.py",
    "staging/document_builder/make_contact_sheets.py": "scripts/document/make_contact_sheets.py",
    "staging/final_pdf_audit/audit_final_pdf.py": "scripts/document/audit_final_pdf.py",
    "staging/research_appendices_completion/build_research_appendices.mjs": "scripts/data/build_research_appendices.mjs",
    "staging/top100_interlanguage_crosswalk/build_top100_interlanguage_crosswalk_20260830.mjs": "scripts/data/build_top100_interlanguage_crosswalk_20260830.mjs",
}

METADATA_FILES = [
    "README.md",
    "LICENSE",
    "CODE_LICENSE",
    "THIRD_PARTY_NOTICES.md",
    "CITATION.cff",
    "PROVENANCE.md",
    "zenodo_metadata.json",
]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest().upper()


def copy_one(source_rel: str, destination_rel: str) -> None:
    source = ROOT / source_rel
    destination = RELEASE / destination_rel
    if not source.is_file():
        raise FileNotFoundError(source_rel)
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, destination)


def copy_metadata(name: str) -> None:
    source = METADATA_DRAFT / name
    if not source.is_file():
        raise FileNotFoundError(f"missing release metadata draft: {name}")
    shutil.copy2(source, RELEASE / name)


def scan_public_text() -> list[dict[str, str]]:
    binary_suffixes = {".docx", ".pdf", ".png"}
    forbidden = {
        "absolute_windows_profile": re.compile(r"[A-Za-z]:\\Users\\[^\\\s]+", re.I),
        "absolute_unix_profile": re.compile(r"/" + r"Users/[^/\s]+", re.I),
        "github_token": re.compile(r"(?:github_pat_|ghp_)[A-Za-z0-9_]+", re.I),
        "authorization_bearer": re.compile(r"Authorization\s*:\s*Bearer\s+\S+", re.I),
        "zenodo_access_token": re.compile(r"access_token\s*[=:]\s*[^\s\"']+", re.I),
        "email_address": re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.I),
    }
    findings: list[dict[str, str]] = []
    for path in sorted(item for item in RELEASE.rglob("*") if item.is_file()):
        if path.suffix.lower() in binary_suffixes:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            findings.append({"path": path.relative_to(RELEASE).as_posix(), "rule": "non_utf8_text"})
            continue
        for rule, pattern in forbidden.items():
            if pattern.search(text):
                findings.append({"path": path.relative_to(RELEASE).as_posix(), "rule": rule})
    return findings


def write_validation() -> None:
    files = sorted(item for item in RELEASE.rglob("*") if item.is_file())
    validation = {
        "schema": "standalone-ai-compute-access-release-validation/1.0.0",
        "generated_date": "2026-08-30",
        "status": "PASS",
        "file_count_before_manifest": len(files),
        "total_bytes_before_manifest": sum(item.stat().st_size for item in files),
        "privacy_scan_findings": [],
        "paper": {
            "markdown_sha256": sha256(RELEASE / "PAPER.md"),
            "docx_sha256": sha256(RELEASE / "PAPER.docx"),
            "pdf_sha256": sha256(RELEASE / "PAPER.pdf"),
        },
        "notes": [
            "Third-party source bytes and private source-witness paths are excluded.",
            "The package begins from frozen public input tables and registered public locators.",
            "MANIFEST.sha256 intentionally does not hash itself.",
        ],
    }
    (RELEASE / "PACKAGE_VALIDATION.json").write_text(
        json.dumps(validation, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )


def write_manifest() -> None:
    paths = sorted(
        item for item in RELEASE.rglob("*")
        if item.is_file() and item.name != "MANIFEST.sha256"
    )
    lines = [f"{sha256(path)}  {path.relative_to(RELEASE).as_posix()}" for path in paths]
    (RELEASE / "MANIFEST.sha256").write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_deterministic_zip() -> None:
    with zipfile.ZipFile(ZIP_PATH, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for path in sorted(item for item in RELEASE.rglob("*") if item.is_file()):
            info = zipfile.ZipInfo(path.relative_to(RELEASE).as_posix())
            info.date_time = (2026, 8, 30, 0, 0, 0)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            archive.writestr(info, path.read_bytes(), compress_type=zipfile.ZIP_DEFLATED, compresslevel=9)
    with zipfile.ZipFile(ZIP_PATH) as archive:
        bad = archive.testzip()
        if bad is not None:
            raise RuntimeError(f"ZIP CRC failure: {bad}")
        expected = sorted(path.relative_to(RELEASE).as_posix() for path in RELEASE.rglob("*") if path.is_file())
        if sorted(archive.namelist()) != expected:
            raise RuntimeError("ZIP inventory differs from release directory")


def main() -> None:
    if RELEASE.exists():
        raise FileExistsError(RELEASE)
    if ZIP_PATH.exists():
        raise FileExistsError(ZIP_PATH)
    RELEASE.mkdir(parents=True)

    for source, destination in CORE_FILES.items():
        copy_one(source, destination)
    for name in METHOD_FILES:
        copy_one(name, name)
    for name in DATA_FILES:
        copy_one(name, name)
    for source, destination in MODEL_INPUT_FILES.items():
        copy_one(source, destination)
    for name in EVIDENCE_FILES:
        copy_one(name, name)
    for source, destination in QA_FILES.items():
        copy_one(source, destination)
    for source, destination in SCRIPT_FILES.items():
        copy_one(source, destination)
    copy_one("requirements.txt", "requirements.txt")
    for name in METADATA_FILES:
        copy_metadata(name)

    findings = scan_public_text()
    if findings:
        raise RuntimeError("Public-text privacy scan failed: " + json.dumps(findings, ensure_ascii=False))
    write_validation()
    write_manifest()
    write_deterministic_zip()

    files = sorted(item for item in RELEASE.rglob("*") if item.is_file())
    result = {
        "release_directory": RELEASE.relative_to(ROOT).as_posix(),
        "release_file_count": len(files),
        "release_total_bytes": sum(item.stat().st_size for item in files),
        "zip_path": ZIP_PATH.relative_to(ROOT).as_posix(),
        "zip_bytes": ZIP_PATH.stat().st_size,
        "zip_sha256": sha256(ZIP_PATH),
        "manifest_sha256": sha256(RELEASE / "MANIFEST.sha256"),
        "privacy_findings": findings,
    }
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
