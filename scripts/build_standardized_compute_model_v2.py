#!/usr/bin/env python3
"""Build the closed, from-scratch standardized educational-localization model.

The builder has three deliberately separate layers:

1. exact tokenization measurements on the sentence-aligned FLORES-200 devtest
   bytes, using version-pinned cl100k_base and o200k_base tokenizers;
2. declared low/base/high workflow scenarios for a common source canon; and
3. a closed identity-coefficient registry whose normalized inputs are disjoint
   fresh input, visible output, or hidden-reasoning token events.

No population, educational-need, resource-gap, project state, cached-token
discount, prior translation, or local programme counter is read or scored.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import importlib.metadata
import io
import json
import math
import os
import platform
import statistics
import sys
import tarfile
import unicodedata
from collections import defaultdict
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

import build_standardized_compute_target_bindings as target_binding_builder


MODEL_VERSION = "interlanguage/standard-compute/2.0.0"
FORMULA_VERSION = "standard-fecu-sum/2.0.0"
REGISTRY_VERSION = "standard-compute-closed-registry-2026-09-01-v2"
SNAPSHOT_UTC = "2026-09-01T00:00:00Z"
TIKTOKEN_VERSION = "0.11.0"
REFERENCE_TOKENIZER = "cl100k_base"
WORKING_TOKENIZER = "o200k_base"
UNICODE_NORMALIZATION = "NFC"
FLORES_URL = "https://dl.fbaipublicfiles.com/nllb/flores200_dataset.tar.gz"
FLORES_SHA256 = "b8b0b76783024b85797e5cc75064eb83fc5288b41e9654dabc7be6ae944011f6"
FLORES_BYTES = 25_585_843
FLORES_SPLIT = "devtest"
FLORES_SENTENCES = 1_012
CL100K_ASSET_SHA256 = "223921b76ee99bde995b7ff738513eef100fb51d18c93597a113bcffe865b2a7"
O200K_ASSET_SHA256 = "446a9538cb6c348e3516120d7c08b09f57c36495e2acfffe59a5bf8b0cfb1a2d"
TIKTOKEN_RUNTIME_SHA256 = {
    "__init__.py": "43642a9660e92e0abc090d04316c1b4886ebef01e471334d62ab8eb7e767901e",
    "_tiktoken.cp313-win_amd64.pyd": "3e7bdaca219bd6404a147197c6781bbf9a5218370272a0919ab139e78acf52c4",
    "core.py": "42c92b73592d4764a0c9a1b5075e5501ae4d6eda9c6c8f4adedad6921349f46a",
    "load.py": "ede7ede5b0d02c9d0f74e8ca46fb975b40982e1fe85be5b73be657bcaa13cc4d",
    "model.py": "3eea8754a017a9f59a49346aa789560defa51872de60498e7b0ac0f5c1dec19e",
    "openai_public.py": "c1e4c453c2fcf8102342c2fc3771aa647f22012ce05cb9751d2bc55830738088",
    "registry.py": "7b941fceffd6c3a76b54a93e7bcf8a37a7181e8d6f1bf6f9420e77821ff5a60d",
}

SCENARIOS = ("low", "base", "high")
MEASUREMENT_ANCHORED_FACTOR_IDS = frozenset(
    {"F004", "F006", "F008", "F009", "F011", "F013", "F014", "F016", "F033", "F035", "F036", "F040"}
    | {f"F{index:03d}" for index in range(41, 49)}
)
PRIMARY_AGGREGATE_EVIDENCE_CLASS = "PARTIALLY_IDENTIFIED_MEASUREMENT_ANCHORED_PROJECTION"
MODEL_ONLY_FACTOR_EVIDENCE_CLASS = "MODEL_CONDITIONAL_PLANNING_SCENARIO"

CANONS = (
    {"canon_id": "CANON-025K", "source_reference_tokens": 25_000, "label": "quarter canon"},
    {"canon_id": "CANON-100K", "source_reference_tokens": 100_000, "label": "common canon"},
    {"canon_id": "CANON-400K", "source_reference_tokens": 400_000, "label": "four-canon collection"},
)

PACKAGES = (
    {
        "package_id": "PKG-TEXT",
        "branch_id": "text",
        "label": "accepted translated and educationally adapted text",
        "delivery_format": "accepted_text",
        "prefixes": ("text.",),
    },
    {
        "package_id": "PKG-ACCESSIBLE-PUBLICATION",
        "branch_id": "accessible_publication",
        "label": "text plus accessible HTML/MathML, EPUB, and tagged PDF",
        "delivery_format": "accessible_html_mathml_epub_pdf",
        "prefixes": ("text.", "html.", "publication."),
    },
    {
        "package_id": "PKG-AUDIO",
        "branch_id": "audio",
        "label": "text plus narrated audio edition",
        "delivery_format": "narrated_audio",
        "prefixes": ("text.", "audio."),
    },
    {
        "package_id": "PKG-CAPTIONS",
        "branch_id": "captions",
        "label": "text plus transcript and timed captions",
        "delivery_format": "transcript_timed_captions",
        "prefixes": ("text.", "captions."),
    },
    {
        "package_id": "PKG-NAMED-SIGN",
        "branch_id": "named_sign",
        "label": "text plus one named sign-language video",
        "delivery_format": "named_sign_language_video",
        "prefixes": ("text.", "sign."),
    },
    {
        "package_id": "PKG-COMPLETE-ACCESS",
        "branch_id": "complete_access",
        "label": "complete text, publication, audio, caption, and named-sign bundle",
        "delivery_format": "complete_access_bundle",
        "prefixes": ("text.", "html.", "publication.", "audio.", "captions.", "sign."),
    },
)

# Workflow priors are model definitions, not published measurements or bounds.
P = {
    "terminology_entries_per_100k": {"low": 100.0, "base": 400.0, "high": 1200.0},
    "terminology_fit_per_entry": {"low": 80.0, "base": 160.0, "high": 320.0},
    "terminology_fot_per_entry": {"low": 30.0, "base": 60.0, "high": 120.0},
    "terminology_frt_per_entry": {"low": 40.0, "base": 100.0, "high": 240.0},
    "generation_extra_fit_fraction": {"low": 0.15, "base": 0.25, "high": 0.50},
    "generation_frt_fraction": {"low": 0.25, "base": 0.60, "high": 1.50},
    "independent_qa_passes": {"low": 1.0, "base": 2.0, "high": 3.0},
    "qa_extra_fit_fraction_per_pass": {"low": 0.10, "base": 0.15, "high": 0.25},
    "qa_report_fot_fraction_target_per_pass": {"low": 0.08, "base": 0.12, "high": 0.20},
    "qa_frt_fraction_per_pass": {"low": 0.30, "base": 0.75, "high": 1.75},
    "repair_extra_fit_fraction": {"low": 0.10, "base": 0.20, "high": 0.40},
    "repair_fot_fraction_target": {"low": 0.10, "base": 0.25, "high": 1.00},
    "repair_frt_fraction": {"low": 0.15, "base": 0.40, "high": 1.00},
    "deterministic_triage_fit_fraction": {"low": 0.020, "base": 0.050, "high": 0.150},
    "deterministic_triage_fot_fraction": {"low": 0.005, "base": 0.010, "high": 0.030},
    "deterministic_triage_frt_fraction": {"low": 0.010, "base": 0.030, "high": 0.100},
    "headings_per_100k": {"low": 100.0, "base": 250.0, "high": 600.0},
    "links_per_100k": {"low": 50.0, "base": 150.0, "high": 400.0},
    "formulas_per_100k": {"low": 50.0, "base": 300.0, "high": 1200.0},
    "diagrams_per_100k": {"low": 10.0, "base": 75.0, "high": 250.0},
    "tables_per_100k": {"low": 10.0, "base": 50.0, "high": 150.0},
    "code_blocks_per_100k": {"low": 0.0, "base": 20.0, "high": 100.0},
    "formula_description_tokens": {"low": 5.0, "base": 15.0, "high": 40.0},
    "diagram_description_tokens": {"low": 30.0, "base": 80.0, "high": 180.0},
    "table_summary_tokens": {"low": 10.0, "base": 25.0, "high": 60.0},
    "html_structure_fit_fraction": {"low": 0.08, "base": 0.20, "high": 0.50},
    "html_structure_fot_fraction": {"low": 0.02, "base": 0.05, "high": 0.10},
    "html_structure_frt_fraction": {"low": 0.03, "base": 0.10, "high": 0.30},
    "description_audit_frt_multiplier": {"low": 0.50, "base": 1.00, "high": 2.00},
    "description_repair_fot_multiplier": {"low": 0.25, "base": 0.50, "high": 1.00},
    "description_repair_frt_multiplier": {"low": 0.25, "base": 0.50, "high": 1.00},
    "publication_triage_fit_fraction": {"low": 0.020, "base": 0.050, "high": 0.120},
    "publication_triage_fot_fraction": {"low": 0.005, "base": 0.015, "high": 0.040},
    "publication_triage_frt_fraction": {"low": 0.005, "base": 0.015, "high": 0.040},
    "validator_cycles": {"low": 2.0, "base": 4.0, "high": 8.0},
    "audio_context_fit_fraction": {"low": 0.05, "base": 0.10, "high": 0.25},
    "audio_adaptation_fot_fraction_target": {"low": 0.10, "base": 0.35, "high": 1.00},
    "audio_frt_fraction_target": {"low": 0.10, "base": 0.30, "high": 0.80},
    "pronunciation_entries_per_100k": {"low": 100.0, "base": 500.0, "high": 2000.0},
    "pronunciation_fit_per_entry": {"low": 10.0, "base": 20.0, "high": 40.0},
    "pronunciation_fot_per_entry": {"low": 5.0, "base": 10.0, "high": 20.0},
    "pronunciation_frt_per_entry": {"low": 5.0, "base": 10.0, "high": 20.0},
    "audio_audit_fot_fraction_target": {"low": 0.02, "base": 0.05, "high": 0.10},
    "audio_audit_frt_fraction_target": {"low": 0.10, "base": 0.25, "high": 0.50},
    "caption_fit_multiplier_target": {"low": 0.25, "base": 1.00, "high": 2.00},
    "caption_fot_multiplier_target": {"low": 0.15, "base": 1.00, "high": 2.00},
    "caption_frt_multiplier_target": {"low": 0.10, "base": 1.00, "high": 2.00},
    "sign_fit_multiplier_target": {"low": 0.80, "base": 1.50, "high": 3.00},
    "sign_fot_multiplier_target": {"low": 0.70, "base": 1.50, "high": 3.00},
    "sign_frt_multiplier_target": {"low": 0.50, "base": 1.00, "high": 2.00},
    "target_words_per_working_token": {"low": 0.55, "base": 0.75, "high": 0.95},
    "narration_words_per_minute": {"low": 170.0, "base": 150.0, "high": 125.0},
    "pause_description_factor": {"low": 1.05, "base": 1.15, "high": 1.25},
    "words_per_caption_cue_proxy": {"low": 8.0, "base": 6.0, "high": 4.0},
    "signed_to_audio_duration_ratio": {"low": 0.80, "base": 1.20, "high": 1.80},
}


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def canonical_row_hash(row: Mapping[str, Any], excluded: Iterable[str]) -> str:
    clean = {key: row[key] for key in sorted(row) if key not in set(excluded)}
    return sha256_bytes(json.dumps(clean, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8"))


def write_csv(path: Path, fieldnames: Sequence[str], rows: Sequence[Mapping[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n", extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fieldnames})


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="")


def quantile(values: Sequence[float], probability: float) -> float:
    ordered = sorted(values)
    if not ordered:
        raise ValueError("quantile requires values")
    if len(ordered) == 1:
        return ordered[0]
    position = (len(ordered) - 1) * probability
    lower = math.floor(position)
    upper = math.ceil(position)
    if lower == upper:
        return ordered[lower]
    weight = position - lower
    return ordered[lower] * (1.0 - weight) + ordered[upper] * weight


def fmt(value: float | int, digits: int = 9) -> str:
    if isinstance(value, int):
        return str(value)
    rendered = f"{value:.{digits}f}".rstrip("0").rstrip(".")
    return rendered if rendered else "0"


def _tar_text(archive: tarfile.TarFile, member_name: str) -> str:
    member = archive.getmember(member_name)
    extracted = archive.extractfile(member)
    if extracted is None:
        raise ValueError(f"cannot read archive member {member_name}")
    return extracted.read().decode("utf-8")


def _normalized_lines(text: str) -> list[str]:
    return [unicodedata.normalize(UNICODE_NORMALIZATION, line.rstrip("\r")) for line in text.split("\n") if line != ""]


def _token_counts(encoding: Any, lines: Sequence[str]) -> list[int]:
    return [len(encoding.encode(line, disallowed_special=())) for line in lines]


def _contiguous_block_ratios(numerators: Sequence[int], denominators: Sequence[int], blocks: int = 20) -> list[float]:
    if len(numerators) != len(denominators):
        raise ValueError("unaligned token counts")
    result: list[float] = []
    for block in range(blocks):
        start = len(numerators) * block // blocks
        end = len(numerators) * (block + 1) // blocks
        denominator = sum(denominators[start:end])
        if denominator:
            result.append(sum(numerators[start:end]) / denominator)
    return result


def measure_flores(archive_path: Path, tokenizer_cache: Path) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    if archive_path.stat().st_size != FLORES_BYTES:
        raise ValueError(f"FLORES archive byte count mismatch: {archive_path.stat().st_size}")
    archive_hash = sha256_file(archive_path)
    if archive_hash != FLORES_SHA256:
        raise ValueError(f"FLORES archive hash mismatch: {archive_hash}")

    installed = importlib.metadata.version("tiktoken")
    if installed != TIKTOKEN_VERSION:
        raise ValueError(f"tiktoken must be {TIKTOKEN_VERSION}, found {installed}")
    os.environ["TIKTOKEN_CACHE_DIR"] = str(tokenizer_cache)
    import tiktoken  # imported only after the cache path and version gate are fixed
    from tiktoken import _tiktoken as native_tiktoken

    reference = tiktoken.get_encoding(REFERENCE_TOKENIZER)
    working = tiktoken.get_encoding(WORKING_TOKENIZER)

    with tarfile.open(archive_path, "r:gz") as archive:
        names = sorted(
            member.name
            for member in archive.getmembers()
            if member.isfile()
            and member.name.startswith("./flores200_dataset/devtest/")
            and member.name.endswith(".devtest")
        )
        if len(names) != 204:
            raise ValueError(f"expected 204 FLORES language-script files, found {len(names)}")
        by_code = {Path(name).name.removesuffix(".devtest"): name for name in names}
        if "eng_Latn" not in by_code:
            raise ValueError("FLORES source eng_Latn is absent")
        source_lines = _normalized_lines(_tar_text(archive, by_code["eng_Latn"]))
        if len(source_lines) != FLORES_SENTENCES:
            raise ValueError(f"expected {FLORES_SENTENCES} aligned sentences, found {len(source_lines)}")
        source_ref_by_sentence = _token_counts(reference, source_lines)
        source_work_by_sentence = _token_counts(working, source_lines)
        source_codepoints_by_sentence = [len(line) for line in source_lines]
        source_ref_total = sum(source_ref_by_sentence)
        source_work_total = sum(source_work_by_sentence)
        source_codepoints_total = sum(source_codepoints_by_sentence)

        rows: list[dict[str, Any]] = []
        for code in sorted(by_code):
            target_lines = _normalized_lines(_tar_text(archive, by_code[code]))
            if len(target_lines) != len(source_lines):
                raise ValueError(f"{code} has {len(target_lines)} lines, expected {len(source_lines)}")
            target_ref_by_sentence = _token_counts(reference, target_lines)
            target_work_by_sentence = _token_counts(working, target_lines)
            target_codepoints_by_sentence = [len(line) for line in target_lines]
            target_ref_total = sum(target_ref_by_sentence)
            target_work_total = sum(target_work_by_sentence)
            target_codepoints_total = sum(target_codepoints_by_sentence)
            expansion = target_ref_total / source_ref_total
            fragmentation = target_work_total / target_ref_total
            combined = target_work_total / source_ref_total
            text_length_expansion = target_codepoints_total / source_codepoints_total
            token_fragmentation_relative = (
                (target_work_total / target_codepoints_total)
                / (source_ref_total / source_codepoints_total)
            )
            expansion_blocks = _contiguous_block_ratios(target_ref_by_sentence, source_ref_by_sentence)
            fragmentation_blocks = _contiguous_block_ratios(target_work_by_sentence, target_ref_by_sentence)
            combined_blocks = _contiguous_block_ratios(target_work_by_sentence, source_ref_by_sentence)
            rows.append(
                {
                    "flores_code": code,
                    "language_code": code.split("_", 1)[0],
                    "script_code": code.split("_", 1)[1],
                    "is_reference_source": "true" if code == "eng_Latn" else "false",
                    "aligned_sentences": len(source_lines),
                    "unicode_normalization": UNICODE_NORMALIZATION,
                    "reference_tokenizer": REFERENCE_TOKENIZER,
                    "working_tokenizer": WORKING_TOKENIZER,
                    "source_reference_tokens": source_ref_total,
                    "source_working_tokens": source_work_total,
                    "target_reference_tokens": target_ref_total,
                    "target_working_tokens": target_work_total,
                    "target_expansion_reference_E": fmt(expansion),
                    "target_tokenizer_fragmentation_P": fmt(fragmentation),
                    "target_codepoint_length_expansion_L": fmt(text_length_expansion),
                    "working_token_fragmentation_relative_F": fmt(token_fragmentation_relative),
                    "combined_target_working_per_source_reference_R": fmt(combined),
                    "E_block_p05": fmt(quantile(expansion_blocks, 0.05)),
                    "E_block_p95": fmt(quantile(expansion_blocks, 0.95)),
                    "P_block_p05": fmt(quantile(fragmentation_blocks, 0.05)),
                    "P_block_p95": fmt(quantile(fragmentation_blocks, 0.95)),
                    "R_block_p05": fmt(quantile(combined_blocks, 0.05)),
                    "R_block_p95": fmt(quantile(combined_blocks, 0.95)),
                    "target_utf8_bytes": len("\n".join(target_lines).encode("utf-8")),
                    "source_unicode_codepoints": source_codepoints_total,
                    "target_unicode_codepoints": target_codepoints_total,
                }
            )

    asset_files = sorted(path for path in tokenizer_cache.iterdir() if path.is_file())
    asset_hashes = {sha256_file(path): {"path_name": path.name, "bytes": path.stat().st_size} for path in asset_files}
    if CL100K_ASSET_SHA256 not in asset_hashes or O200K_ASSET_SHA256 not in asset_hashes:
        raise ValueError("pinned tokenizer assets are absent from the controlled cache")
    package_dir = Path(tiktoken.__file__).resolve().parent
    runtime_paths = sorted(
        {
            Path(tiktoken.__file__).resolve(),
            Path(native_tiktoken.__file__).resolve(),
            package_dir / "core.py",
            package_dir / "load.py",
            package_dir / "registry.py",
            package_dir / "model.py",
            package_dir.parent / "tiktoken_ext" / "openai_public.py",
        },
        key=lambda path: path.name,
    )
    if any(not path.is_file() for path in runtime_paths):
        raise ValueError("a pinned tokenizer runtime file is absent")
    runtime_hashes = {path.name: sha256_file(path) for path in runtime_paths}
    if runtime_hashes != TIKTOKEN_RUNTIME_SHA256:
        raise ValueError(f"pinned tokenizer runtime byte mismatch: {runtime_hashes}")

    targets = [row for row in rows if row["is_reference_source"] == "false"]
    metrics = {
        "E": [float(row["target_expansion_reference_E"]) for row in targets],
        "P": [float(row["target_tokenizer_fragmentation_P"]) for row in targets],
        "L": [float(row["target_codepoint_length_expansion_L"]) for row in targets],
        "F": [float(row["working_token_fragmentation_relative_F"]) for row in targets],
        "R": [float(row["combined_target_working_per_source_reference_R"]) for row in targets],
    }
    summary: dict[str, Any] = {
        "schema_version": "interlanguage/flores-tokenization-measurement/2.0.0",
        "snapshot_utc": SNAPSHOT_UTC,
        "corpus": {
            "name": "FLORES-200",
            "split": FLORES_SPLIT,
            "url": FLORES_URL,
            "archive_bytes": archive_path.stat().st_size,
            "archive_sha256": archive_hash,
            "aligned_sentences": FLORES_SENTENCES,
            "language_script_files": len(rows),
            "non_english_targets": len(targets),
            "license": "CC-BY-SA-4.0 according to the official dataset card",
        },
        "normalization": {
            "unicode": UNICODE_NORMALIZATION,
            "counting": "encode each aligned sentence separately and sum; newline boundaries do not create tokens",
        },
        "tokenizers": {
            "package": "tiktoken",
            "package_version": TIKTOKEN_VERSION,
            "reference": REFERENCE_TOKENIZER,
            "working": WORKING_TOKENIZER,
            "asset_files": [
                {"sha256": digest, **asset_hashes[digest]} for digest in sorted(asset_hashes)
            ],
            "runtime_files": [
                {"name": path.name, "bytes": path.stat().st_size, "sha256": runtime_hashes[path.name]}
                for path in runtime_paths
            ],
        },
        "definitions": {
            "E": "target cl100k_base tokens / English cl100k_base tokens",
            "P": "target o200k_base tokens / target cl100k_base tokens",
            "L": "target Unicode codepoints / English Unicode codepoints; a writing-length proxy, not a grapheme or semantic unit",
            "F": "target o200k tokens per codepoint / English cl100k tokens per codepoint",
            "R": "target o200k_base tokens / English cl100k_base tokens = E times P = L times F",
        },
        "source_working_per_source_reference": source_work_total / source_ref_total,
        "cross_language_quantiles_excluding_english": {
            name: {f"p{int(probability * 100):02d}": quantile(values, probability) for probability in (0, 0.10, 0.25, 0.50, 0.75, 0.90, 1.0)}
            for name, values in metrics.items()
        },
        "limitations": [
            "FLORES devtest is a 1,012-sentence general-domain translation benchmark, not an educational canon.",
            "Cross-language quantiles weight language-script files equally and are planning cases, not population weights or confidence bounds.",
            "Some FLORES translations were pivoted from languages other than English; aligned content remains suitable for token-count comparison but not for inferring translation difficulty.",
            "Tokenizer counts measure digital representation under two pinned vocabularies; they do not measure linguistic complexity, educational need, quality, labor, runtime, or money.",
            "Unicode codepoint length is used only to algebraically separate a writing-length proxy from token density; codepoints are not graphemes, words, morphemes, semantic units, or cross-script difficulty measures.",
        ],
    }
    return rows, summary


def select_ratio_cases(rows: Sequence[Mapping[str, Any]]) -> dict[str, dict[str, Any]]:
    targets = [row for row in rows if row["is_reference_source"] == "false"]
    ordered = sorted(targets, key=lambda row: (float(row["combined_target_working_per_source_reference_R"]), row["flores_code"]))
    selected: dict[str, dict[str, Any]] = {}
    for scenario, probability in (("low", 0.10), ("base", 0.50), ("high", 0.90)):
        desired = quantile([float(row["combined_target_working_per_source_reference_R"]) for row in ordered], probability)
        chosen = min(ordered, key=lambda row: (abs(float(row["combined_target_working_per_source_reference_R"]) - desired), row["flores_code"]))
        selected[scenario] = dict(chosen)
        selected[scenario]["selection_probability"] = probability
        selected[scenario]["interpolated_R_quantile"] = desired
    return selected


def factor_definitions() -> list[dict[str, str]]:
    definitions = [
        ("F001", "text.terminology.fit", "canon atoms", "Fresh input for concept definitions, contexts, alternatives, and reconciliation", "SRC04", "FIT"),
        ("F002", "text.terminology.fot", "canon atoms", "Visible terminology records and decision notes", "SRC04", "FOT"),
        ("F003", "text.terminology.frt", "canon atoms", "Disjoint hidden reasoning for terminology decisions", "SRC04", "FRT"),
        ("F004", "text.generation.source.fit", "canon size", "Canonical source read for generation", "SRC25", "FIT"),
        ("F005", "text.generation.context.fit", "canon size", "Instructions, retrieval, examples, terminology, and chunk overlap", "SRC04", "FIT"),
        ("F006", "text.generation.target.fot", "language-script representation", "Visible generated target text", "SRC24", "FOT"),
        ("F007", "text.generation.frt", "canon size", "Disjoint hidden reasoning for translation and educational adaptation", "SRC04", "FRT"),
        ("F008", "text.qa.source.fit", "uniform QA passes", "Canonical source reads by independent model contexts", "SRC06", "FIT"),
        ("F009", "text.qa.target.fit", "uniform QA passes", "Target reads by independent model contexts", "SRC06", "FIT"),
        ("F010", "text.qa.context.fit", "uniform QA passes", "Audit specifications and terminology supplied to independent contexts", "SRC06", "FIT"),
        ("F011", "text.qa.report.fot", "uniform QA passes", "Independent issue-manifest output", "SRC04", "FOT"),
        ("F012", "text.qa.frt", "uniform QA passes", "Disjoint hidden reasoning in independent audits", "SRC06", "FRT"),
        ("F013", "text.repair.target.fit", "required output formats", "Accepted pre-repair target read", "SRC04", "FIT"),
        ("F014", "text.repair.reports.fit", "required output formats", "Independent issue manifests read for repair", "SRC04", "FIT"),
        ("F015", "text.repair.context.fit", "required output formats", "Repair specification and regression context", "SRC04", "FIT"),
        ("F016", "text.repair.patch.fot", "required output formats", "Visible repair patch or target re-emission", "SRC04", "FOT"),
        ("F017", "text.repair.frt", "required output formats", "Disjoint hidden reasoning for repairs", "SRC04", "FRT"),
        ("F018", "text.deterministic_triage.fit", "required output formats", "Validator issue evidence read by model triage", "SRC13", "FIT"),
        ("F019", "text.deterministic_triage.fot", "required output formats", "Visible validator issue disposition", "SRC13", "FOT"),
        ("F020", "text.deterministic_triage.frt", "required output formats", "Disjoint hidden reasoning for validator issue triage", "SRC13", "FRT"),
        ("F021", "html.structure.fit", "required output formats", "HTML, MathML, language-direction, and accessibility structure input", "SRC07", "FIT"),
        ("F022", "html.structure.fot", "required output formats", "Visible structure/accessibility annotations", "SRC07", "FOT"),
        ("F023", "html.structure.frt", "required output formats", "Disjoint hidden reasoning for structural accessibility", "SRC07", "FRT"),
        ("F024", "html.descriptions.generation.fot", "canon atoms", "Formula verbalizations, diagram descriptions, and table summaries", "SRC08", "FOT"),
        ("F025", "html.descriptions.audit.fit", "uniform QA passes", "Description tokens read in an independent accessibility audit", "SRC08", "FIT"),
        ("F026", "html.descriptions.audit.frt", "uniform QA passes", "Disjoint hidden reasoning for formula, diagram, and table audit", "SRC08", "FRT"),
        ("F027", "html.descriptions.repair.fit", "required output formats", "Description and audit evidence read for repair", "SRC08", "FIT"),
        ("F028", "html.descriptions.repair.fot", "required output formats", "Visible description patches", "SRC08", "FOT"),
        ("F029", "html.descriptions.repair.frt", "required output formats", "Disjoint hidden reasoning for description repair", "SRC08", "FRT"),
        ("F030", "publication.triage.fit", "required output formats", "EPUB, PDF, render, and validator evidence read", "SRC12", "FIT"),
        ("F031", "publication.triage.fot", "required output formats", "Visible publication issue dispositions", "SRC14", "FOT"),
        ("F032", "publication.triage.frt", "required output formats", "Disjoint hidden reasoning for publication repairs", "SRC14", "FRT"),
        ("F033", "audio.script.target.fit", "modality", "Accepted target read for narration adaptation", "SRC16", "FIT"),
        ("F034", "audio.script.context.fit", "modality", "Pronunciation, navigation, math, and visual-description context", "SRC16", "FIT"),
        ("F035", "audio.script.adaptation.fot", "modality", "Visible narration-script adaptation", "SRC16", "FOT"),
        ("F036", "audio.script.frt", "modality", "Disjoint hidden reasoning for narration adaptation", "SRC16", "FRT"),
        ("F037", "audio.pronunciation.fit", "canon atoms", "Pronunciation contexts and alternatives", "SRC16", "FIT"),
        ("F038", "audio.pronunciation.fot", "canon atoms", "Visible pronunciation lexicon entries", "SRC16", "FOT"),
        ("F039", "audio.pronunciation.frt", "canon atoms", "Disjoint hidden reasoning for pronunciation", "SRC16", "FRT"),
        ("F040", "audio.audit.script.fit", "uniform QA passes", "Narration script read by an independent audio audit", "SRC17", "FIT"),
        ("F041", "audio.audit.report.fot", "uniform QA passes", "Visible audio issue manifest", "SRC17", "FOT"),
        ("F042", "audio.audit.frt", "uniform QA passes", "Disjoint hidden reasoning for audio audit", "SRC17", "FRT"),
        ("F043", "captions.preparation.fit", "modality", "Transcript, timing, speaker, and visual context input", "SRC17", "FIT"),
        ("F044", "captions.cues.fot", "modality", "Visible transcript and timed-caption output", "SRC19", "FOT"),
        ("F045", "captions.audit.frt", "modality", "Disjoint hidden reasoning for caption generation and audit", "SRC18", "FRT"),
        ("F046", "sign.preparation.fit", "modality", "Concept, source, named-language, and storyboard input", "SRC20", "FIT"),
        ("F047", "sign.annotation.fot", "modality", "Visible textual sign translation representation and storyboard", "SRC22", "FOT"),
        ("F048", "sign.audit.frt", "modality", "Disjoint hidden reasoning for named sign-language preparation and audit", "SRC23", "FRT"),
    ]
    rows: list[dict[str, str]] = []
    for factor_id, code, family, description, source_id, component in definitions:
        rows.append(
            {
                "factor_id": factor_id,
                "factor_registry_version": REGISTRY_VERSION,
                "standard_compute_model_version": MODEL_VERSION,
                "term_family": family,
                "factor_code": code,
                "factor_description": description,
                "quantity_unit": f"fresh_{component.lower()}_token_event",
                "coefficient_mean": "1",
                "coefficient_p05": "1",
                "coefficient_p50": "1",
                "coefficient_p95": "1",
                "coefficient_lower_bound": "1",
                "coefficient_upper_bound": "1",
                "coefficient_unit": "fresh_equivalent_token_event_per_fresh_token_event",
                "strictly_positive_required": "1",
                "benchmark_source_id": source_id,
                "component": component,
            }
        )
    return rows


def scenario_components(source_ref: float, source_work_ratio: float, target_ratios: Mapping[str, float]) -> tuple[dict[str, dict[str, float]], dict[str, dict[str, float]]]:
    components: dict[str, dict[str, float]] = {factor_id: {} for factor_id in (row["factor_id"] for row in factor_definitions())}
    metrics: dict[str, dict[str, float]] = defaultdict(dict)
    for scenario in SCENARIOS:
        s = source_ref
        sw = source_ref * source_work_ratio
        t = source_ref * target_ratios[scenario]
        scale = source_ref / 100_000.0
        term_entries = P["terminology_entries_per_100k"][scenario] * scale
        qa_passes = P["independent_qa_passes"][scenario]
        qa_report = t * qa_passes * P["qa_report_fot_fraction_target_per_pass"][scenario]
        formulas = P["formulas_per_100k"][scenario] * scale
        diagrams = P["diagrams_per_100k"][scenario] * scale
        tables = P["tables_per_100k"][scenario] * scale
        description_tokens = (
            formulas * P["formula_description_tokens"][scenario]
            + diagrams * P["diagram_description_tokens"][scenario]
            + tables * P["table_summary_tokens"][scenario]
        )
        pronunciation_entries = P["pronunciation_entries_per_100k"][scenario] * scale

        values = {
            "F001": term_entries * P["terminology_fit_per_entry"][scenario],
            "F002": term_entries * P["terminology_fot_per_entry"][scenario],
            "F003": term_entries * P["terminology_frt_per_entry"][scenario],
            "F004": sw,
            "F005": s * P["generation_extra_fit_fraction"][scenario],
            "F006": t,
            "F007": s * P["generation_frt_fraction"][scenario],
            "F008": sw * qa_passes,
            "F009": t * qa_passes,
            "F010": s * qa_passes * P["qa_extra_fit_fraction_per_pass"][scenario],
            "F011": qa_report,
            "F012": s * qa_passes * P["qa_frt_fraction_per_pass"][scenario],
            "F013": t,
            "F014": qa_report,
            "F015": s * P["repair_extra_fit_fraction"][scenario],
            "F016": t * P["repair_fot_fraction_target"][scenario],
            "F017": s * P["repair_frt_fraction"][scenario],
            "F018": s * P["deterministic_triage_fit_fraction"][scenario],
            "F019": s * P["deterministic_triage_fot_fraction"][scenario],
            "F020": s * P["deterministic_triage_frt_fraction"][scenario],
            "F021": s * P["html_structure_fit_fraction"][scenario],
            "F022": s * P["html_structure_fot_fraction"][scenario],
            "F023": s * P["html_structure_frt_fraction"][scenario],
            "F024": description_tokens,
            "F025": description_tokens,
            "F026": description_tokens * P["description_audit_frt_multiplier"][scenario],
            "F027": description_tokens,
            "F028": description_tokens * P["description_repair_fot_multiplier"][scenario],
            "F029": description_tokens * P["description_repair_frt_multiplier"][scenario],
            "F030": s * P["publication_triage_fit_fraction"][scenario],
            "F031": s * P["publication_triage_fot_fraction"][scenario],
            "F032": s * P["publication_triage_frt_fraction"][scenario],
            "F033": t,
            "F034": s * P["audio_context_fit_fraction"][scenario],
            "F035": t * P["audio_adaptation_fot_fraction_target"][scenario],
            "F036": t * P["audio_frt_fraction_target"][scenario],
            "F037": pronunciation_entries * P["pronunciation_fit_per_entry"][scenario],
            "F038": pronunciation_entries * P["pronunciation_fot_per_entry"][scenario],
            "F039": pronunciation_entries * P["pronunciation_frt_per_entry"][scenario],
            "F040": t,
            "F041": t * P["audio_audit_fot_fraction_target"][scenario],
            "F042": t * P["audio_audit_frt_fraction_target"][scenario],
            "F043": t * P["caption_fit_multiplier_target"][scenario],
            "F044": t * P["caption_fot_multiplier_target"][scenario],
            "F045": t * P["caption_frt_multiplier_target"][scenario],
            "F046": t * P["sign_fit_multiplier_target"][scenario],
            "F047": t * P["sign_fot_multiplier_target"][scenario],
            "F048": t * P["sign_frt_multiplier_target"][scenario],
        }
        for factor_id, value in values.items():
            components[factor_id][scenario] = value

        target_words = t * P["target_words_per_working_token"][scenario]
        audio_minutes = target_words / P["narration_words_per_minute"][scenario] * P["pause_description_factor"][scenario]
        metrics["target_working_tokens"][scenario] = t
        metrics["terminology_entries"][scenario] = term_entries
        metrics["headings"][scenario] = P["headings_per_100k"][scenario] * scale
        metrics["links"][scenario] = P["links_per_100k"][scenario] * scale
        metrics["formulas"][scenario] = formulas
        metrics["diagrams"][scenario] = diagrams
        metrics["tables"][scenario] = tables
        metrics["code_blocks"][scenario] = P["code_blocks_per_100k"][scenario] * scale
        metrics["dou"][scenario] = (
            metrics["headings"][scenario]
            + metrics["links"][scenario]
            + 3 * formulas
            + 3 * diagrams
            + 2 * tables
            + 2 * metrics["code_blocks"][scenario]
        )
        metrics["validator_cycles"][scenario] = P["validator_cycles"][scenario]
        metrics["audio_program_minutes_proxy"][scenario] = audio_minutes
        metrics["caption_cues_capacity_proxy"][scenario] = math.ceil(target_words / P["words_per_caption_cue_proxy"][scenario])
        metrics["signed_program_minutes_proxy"][scenario] = audio_minutes * P["signed_to_audio_duration_ratio"][scenario]
    return components, metrics


def included_factor(factor_code: str, package: Mapping[str, Any]) -> bool:
    return any(factor_code.startswith(prefix) for prefix in package["prefixes"])


def build_model_rows(
    ratio_rows: Sequence[Mapping[str, Any]],
    summary: Mapping[str, Any],
    measurement_profiles: Sequence[Mapping[str, str]],
    measurement_profile_registry_file_sha256: str,
    measurement_profile_set_hash: str,
    tokenization_measurement_set_sha256: str,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]], dict[str, Any]]:
    ratio_cases = select_ratio_cases(ratio_rows)
    source_work_ratio = float(summary["source_working_per_source_reference"])

    registry = factor_definitions()
    for row in registry:
        row["registry_row_hash"] = canonical_row_hash(row, {"registry_row_hash", "registry_hash", "component"})
    registry_hash = sha256_bytes(("\n".join(row["registry_row_hash"] for row in registry) + "\n").encode("ascii"))
    for row in registry:
        row["registry_hash"] = registry_hash

    inputs: list[dict[str, Any]] = []
    estimates: list[dict[str, Any]] = []
    derivations: list[dict[str, Any]] = []
    factor_by_id = {row["factor_id"]: row for row in registry}
    measurement_profile_by_id = {row["benchmark_profile_id"]: row for row in measurement_profiles}
    profiles: list[dict[str, Any]] = [
        {
            "model_role": "sensitivity_common_envelope",
            "flores_code": "COMMON-ENVELOPE",
            "script_code": "MULTI",
            "evidence_status": "COMMON_ENVELOPE_SENSITIVITY_ONLY",
            "scenario_status": "COMMON_ENVELOPE_SENSITIVITY_ONLY",
            "target_ratios": {
                scenario: float(ratio_cases[scenario]["combined_target_working_per_source_reference_R"])
                for scenario in SCENARIOS
            },
            "target_E_base": float(ratio_cases["base"]["target_expansion_reference_E"]),
            "target_P_base": float(ratio_cases["base"]["target_tokenizer_fragmentation_P"]),
            "target_L_base": float(ratio_cases["base"]["target_codepoint_length_expansion_L"]),
            "target_F_base": float(ratio_cases["base"]["working_token_fragmentation_relative_F"]),
            "benchmark_profile_id": "",
            "direct_measurement_row_hash": "",
        }
    ]
    for ratio in ratio_rows:
        if ratio["is_reference_source"] == "true":
            continue
        r_base = float(ratio["combined_target_working_per_source_reference_R"])
        benchmark_profile_id = f"flores:{ratio['flores_code']}"
        measured_profile = measurement_profile_by_id[benchmark_profile_id]
        profiles.append(
            {
                "model_role": "primary_measured_feature",
                "flores_code": ratio["flores_code"],
                "script_code": ratio["script_code"],
                "evidence_status": PRIMARY_AGGREGATE_EVIDENCE_CLASS,
                "scenario_status": PRIMARY_AGGREGATE_EVIDENCE_CLASS,
                "target_ratios": {
                    "low": min(float(ratio["R_block_p05"]), r_base),
                    "base": r_base,
                    "high": max(float(ratio["R_block_p95"]), r_base),
                },
                "target_E_base": float(ratio["target_expansion_reference_E"]),
                "target_P_base": float(ratio["target_tokenizer_fragmentation_P"]),
                "target_L_base": float(ratio["target_codepoint_length_expansion_L"]),
                "target_F_base": float(ratio["working_token_fragmentation_relative_F"]),
                "benchmark_profile_id": benchmark_profile_id,
                "direct_measurement_row_hash": measured_profile["direct_measurement_row_hash"],
            }
        )

    for profile, canon in ((profile, canon) for profile in profiles for canon in CANONS):
        target_ratios = profile["target_ratios"]
        components, metrics = scenario_components(
            float(canon["source_reference_tokens"]), source_work_ratio, target_ratios
        )
        for package in PACKAGES:
            profile_code = "ENV" if profile["model_role"] == "sensitivity_common_envelope" else f"MF-{profile['flores_code']}"
            case_id = f"STD-{profile_code}-{canon['canon_id'].split('-')[1]}-{package['branch_id'].upper().replace('_', '-')}"
            selected_factors = [
                factor_id for factor_id, definition in factor_by_id.items() if included_factor(definition["factor_code"], package)
            ]
            totals = {component: {scenario: 0.0 for scenario in SCENARIOS} for component in ("FIT", "FOT", "FRT")}
            for factor_id in selected_factors:
                factor = factor_by_id[factor_id]
                values = components[factor_id]
                input_row: dict[str, Any] = {
                    "compute_input_id": f"{case_id}:{factor_id}",
                    "candidate_id": case_id,
                    "standard_compute_model_version": MODEL_VERSION,
                    "factor_registry_version": REGISTRY_VERSION,
                    "factor_id": factor_id,
                    "quantity_mean": "",
                    "quantity_p05": "",
                    "quantity_p50": "",
                    "quantity_p95": "",
                    "quantity_lower_bound": "",
                    "quantity_upper_bound": "",
                    "quantity_low": fmt(values["low"], 6),
                    "quantity_base": fmt(values["base"], 6),
                    "quantity_high": fmt(values["high"], 6),
                    "quantity_unit": factor["quantity_unit"],
                    "quantity_source_id": factor["benchmark_source_id"],
                    "estimate_status": (
                        PRIMARY_AGGREGATE_EVIDENCE_CLASS
                        if profile["model_role"] == "primary_measured_feature" and factor_id in MEASUREMENT_ANCHORED_FACTOR_IDS
                        else MODEL_ONLY_FACTOR_EVIDENCE_CLASS
                        if profile["model_role"] == "primary_measured_feature"
                        else profile["scenario_status"]
                    ),
                    "uncertainty_method": "coupled_process_cases_plus_target_block_variation" if profile["model_role"] == "primary_measured_feature" else "common_cross_language_envelope_sensitivity",
                    "draw_set_id": "",
                }
                input_row["input_row_hash"] = canonical_row_hash(input_row, {"input_row_hash"})
                inputs.append(input_row)
                component = factor["component"]
                for scenario in SCENARIOS:
                    totals[component][scenario] += values[scenario]

            total = {scenario: sum(totals[component][scenario] for component in totals) for scenario in SCENARIOS}
            derivation = {
                "candidate_id": case_id,
                "compute_low": fmt(total["low"], 6),
                "compute_base": fmt(total["base"], 6),
                "compute_high": fmt(total["high"], 6),
                "factor_registry_version": REGISTRY_VERSION,
                "formula_version": FORMULA_VERSION,
                "compute_measure_class": "fresh_input_output_reasoning_token_events_v2",
                "compute_unit": "fresh_equivalent_token_events",
                "branch_id": package["branch_id"],
                "canon_id": canon["canon_id"],
                "model_role": profile["model_role"],
                "flores_code": profile["flores_code"],
                "script_code": profile["script_code"],
                "evidence_status": profile["evidence_status"],
                "benchmark_profile_id": profile["benchmark_profile_id"],
                "tokenization_measurement_set_sha256": tokenization_measurement_set_sha256 if profile["model_role"] == "primary_measured_feature" else "",
                "measurement_profile_registry_file_sha256": measurement_profile_registry_file_sha256 if profile["model_role"] == "primary_measured_feature" else "",
                "measurement_profile_set_hash": measurement_profile_set_hash if profile["model_role"] == "primary_measured_feature" else "",
                "direct_measurement_row_hash": profile["direct_measurement_row_hash"],
                "source_reference_tokens": canon["source_reference_tokens"],
                "target_ratio_low": fmt(target_ratios["low"]),
                "target_ratio_base": fmt(target_ratios["base"]),
                "target_ratio_high": fmt(target_ratios["high"]),
                "target_expansion_E_base": fmt(profile["target_E_base"]),
                "target_fragmentation_P_base": fmt(profile["target_P_base"]),
                "target_codepoint_length_L_base": fmt(profile["target_L_base"]),
                "working_token_fragmentation_F_base": fmt(profile["target_F_base"]),
                "fit_low": fmt(totals["FIT"]["low"], 6),
                "fit_base": fmt(totals["FIT"]["base"], 6),
                "fit_high": fmt(totals["FIT"]["high"], 6),
                "fot_low": fmt(totals["FOT"]["low"], 6),
                "fot_base": fmt(totals["FOT"]["base"], 6),
                "fot_high": fmt(totals["FOT"]["high"], 6),
                "frt_low": fmt(totals["FRT"]["low"], 6),
                "frt_base": fmt(totals["FRT"]["base"], 6),
                "frt_high": fmt(totals["FRT"]["high"], 6),
                "terminology_entries_low": fmt(metrics["terminology_entries"]["low"], 3),
                "terminology_entries_base": fmt(metrics["terminology_entries"]["base"], 3),
                "terminology_entries_high": fmt(metrics["terminology_entries"]["high"], 3),
                "weighted_document_object_units_low": fmt(metrics["dou"]["low"], 3),
                "weighted_document_object_units_base": fmt(metrics["dou"]["base"], 3),
                "weighted_document_object_units_high": fmt(metrics["dou"]["high"], 3),
                "audio_program_minutes_low": fmt(metrics["audio_program_minutes_proxy"]["low"], 3) if package["branch_id"] in {"audio", "complete_access"} else "",
                "audio_program_minutes_base": fmt(metrics["audio_program_minutes_proxy"]["base"], 3) if package["branch_id"] in {"audio", "complete_access"} else "",
                "audio_program_minutes_high": fmt(metrics["audio_program_minutes_proxy"]["high"], 3) if package["branch_id"] in {"audio", "complete_access"} else "",
                "caption_cues_low": fmt(metrics["caption_cues_capacity_proxy"]["low"]) if package["branch_id"] in {"captions", "complete_access"} else "",
                "caption_cues_base": fmt(metrics["caption_cues_capacity_proxy"]["base"]) if package["branch_id"] in {"captions", "complete_access"} else "",
                "caption_cues_high": fmt(metrics["caption_cues_capacity_proxy"]["high"]) if package["branch_id"] in {"captions", "complete_access"} else "",
                "signed_program_minutes_low": fmt(metrics["signed_program_minutes_proxy"]["low"], 3) if package["branch_id"] in {"named_sign", "complete_access"} else "",
                "signed_program_minutes_base": fmt(metrics["signed_program_minutes_proxy"]["base"], 3) if package["branch_id"] in {"named_sign", "complete_access"} else "",
                "signed_program_minutes_high": fmt(metrics["signed_program_minutes_proxy"]["high"], 3) if package["branch_id"] in {"named_sign", "complete_access"} else "",
            }
            derivations.append(derivation)

            estimate: dict[str, Any] = {
                "compute_estimate_id": f"EST:{case_id}",
                "candidate_id": case_id,
                "standard_compute_model_version": MODEL_VERSION,
                "reference_hardware_id": "NOT_APPLICABLE_TOKEN_TRAFFIC",
                "hardware_normalization_version": "NOT_APPLICABLE",
                "model_runtime_version": "VENDOR_NEUTRAL_PLANNING_MODEL",
                "tokenizer_version": f"tiktoken-{TIKTOKEN_VERSION}:{REFERENCE_TOKENIZER}+{WORKING_TOKENIZER}",
                "qa_target_version": "independent_context_plus_deterministic_qa_v2",
                "standard_compute_mean": "",
                "standard_compute_p05": "",
                "standard_compute_p50": "",
                "standard_compute_p95": "",
                "standard_compute_lower_bound": "",
                "standard_compute_upper_bound": "",
                "standard_compute_scenario_low": fmt(total["low"], 6),
                "standard_compute_scenario_base": fmt(total["base"], 6),
                "standard_compute_scenario_high": fmt(total["high"], 6),
                "standard_compute_unit": "fresh_equivalent_token_events",
                "energy_mean": "",
                "energy_p05": "",
                "energy_p50": "",
                "energy_p95": "",
                "energy_lower_bound": "",
                "energy_upper_bound": "",
                "energy_unit": "NOT_INFERABLE_FROM_TOKEN_EVENTS",
                "estimate_status": profile["scenario_status"],
                "uncertainty_method": "coupled_process_cases_plus_target_block_variation" if profile["model_role"] == "primary_measured_feature" else "common_cross_language_envelope_sensitivity",
                "draw_set_id": "",
                "benchmark_source_ids_json": json.dumps(["SRC24", "SRC25"], separators=(",", ":")),
                "compute_input_set_hash": "BOUND_AFTER_CANONICAL_INPUT_BYTES_ARE_WRITTEN",
                "generated_at_utc": SNAPSHOT_UTC,
            }
            estimates.append(estimate)

    model = {
        "schema_version": "interlanguage/standardized-compute-model/2.0.0",
        "model_version": MODEL_VERSION,
        "formula_version": FORMULA_VERSION,
        "factor_registry_version": REGISTRY_VERSION,
        "factor_registry_semantic_hash": registry_hash,
        "snapshot_utc": SNAPSHOT_UTC,
        "scope": "standardized from-scratch educational localization only; no access ranking",
        "canon_profiles": list(CANONS),
        "package_profiles": [
            {key: value for key, value in package.items() if key != "prefixes"} for package in PACKAGES
        ],
        "token_units": {
            "FIT": "all logical prompt/input tokens under the working tokenizer, including tokens served from cache; a cache hit is neither a discount nor an extra event",
            "FOT": "visible output tokens returned by the model, excluding disjoint hidden reasoning tokens",
            "FRT": "hidden reasoning tokens only when separately exposed or declared; never double-counted in FOT",
            "FECU": "FIT + FOT + FRT, a token-event traffic index, not FLOPs, energy, duration, quality, labor, or money",
        },
        "target_representation": {
            "E": "target cl100k_base / English cl100k_base on identical aligned content",
            "P": "target o200k_base / target cl100k_base on identical normalized target bytes",
            "L": "target Unicode codepoints / English Unicode codepoints; writing-length proxy only",
            "F": "target o200k tokens per codepoint / English cl100k tokens per codepoint; tokenizer-density proxy",
            "R": "E times P = L times F = target o200k_base / English cl100k_base",
            "selected_cross_language_cases": ratio_cases,
            "source_working_per_source_reference": source_work_ratio,
            "primary_model": "one identical measurement and derivation protocol applied to each FLORES-covered language-script target",
            "missing_target_policy": "UNRANKED_ORDER_B until the same aligned benchmark protocol is completed; never substitute identity or a prestige/region/language prior",
            "sensitivity_control": "one language-blind p10/p50/p90-nearest common envelope, reported separately and never substituted for the primary measured-feature result",
            "successor_roster_binding_policy": "after the successor universe freezes, bind each successor target ID explicitly to an exact measured benchmark profile; never infer a profile from region, language family, prestige, or name similarity; unmatched targets remain unranked and may use only the separate common-envelope sensitivity control",
        },
        "exclusions": [
            "cached-input discount or premium",
            "gross cached-token counters as an additional term",
            "prior or existing translations, assets, terminology, completion, readiness, or reuse",
            "local programme counters, staffing, funding, schedule, or sunk cost",
            "population, educational need, resource scarcity, or access ranking fields",
        ],
        "mechanical_compute": "Validator, build, TTS, ASR, alignment, render, and video compute require separate execution receipts and are not inferred from token events.",
        "scenario_semantics": "Coupled low/base/high planning cases; not probability intervals and not universal bounds.",
    }
    return registry, inputs, estimates, derivations, model


RATIO_FIELDS = (
    "flores_code",
    "language_code",
    "script_code",
    "is_reference_source",
    "aligned_sentences",
    "unicode_normalization",
    "reference_tokenizer",
    "working_tokenizer",
    "source_reference_tokens",
    "source_working_tokens",
    "target_reference_tokens",
    "target_working_tokens",
    "target_expansion_reference_E",
    "target_tokenizer_fragmentation_P",
    "target_codepoint_length_expansion_L",
    "working_token_fragmentation_relative_F",
    "combined_target_working_per_source_reference_R",
    "E_block_p05",
    "E_block_p95",
    "P_block_p05",
    "P_block_p95",
    "R_block_p05",
    "R_block_p95",
    "target_utf8_bytes",
    "source_unicode_codepoints",
    "target_unicode_codepoints",
)

MEASUREMENT_PROFILE_FIELDS = (
    "benchmark_profile_id",
    "flores_code",
    "language_code",
    "script_code",
    "profile_measurement_kind",
    "profile_match_scope",
    "aligned_sentences",
    "tokenization_measurement_set_sha256",
    "direct_measurement_row_hash",
    "profile_row_hash",
    "profile_set_hash",
)


def measurement_profile_rows(
    ratio_rows: Sequence[Mapping[str, Any]],
    tokenization_measurement_set_sha256: str,
) -> tuple[list[dict[str, str]], str]:
    profiles: list[dict[str, str]] = []
    for ratio in ratio_rows:
        if str(ratio["is_reference_source"]).casefold() == "true":
            continue
        serialized_ratio = {field: str(ratio.get(field, "")) for field in RATIO_FIELDS}
        profile = {
            "benchmark_profile_id": f"flores:{ratio['flores_code']}",
            "flores_code": str(ratio["flores_code"]),
            "language_code": str(ratio["language_code"]),
            "script_code": str(ratio["script_code"]),
            "profile_measurement_kind": "DIRECT_ALIGNED_BENCHMARK",
            "profile_match_scope": "ALIGNED_LANGUAGE_SCRIPT_TOKENIZATION_PROXY",
            "aligned_sentences": str(ratio["aligned_sentences"]),
            "tokenization_measurement_set_sha256": tokenization_measurement_set_sha256,
            "direct_measurement_row_hash": canonical_row_hash(serialized_ratio, set()),
            "profile_row_hash": "",
            "profile_set_hash": "",
        }
        profile["profile_row_hash"] = canonical_row_hash(profile, {"profile_row_hash", "profile_set_hash"})
        profiles.append(profile)
    profiles.sort(key=lambda row: row["benchmark_profile_id"])
    profile_set_hash = sha256_bytes(
        ("\n".join(row["profile_row_hash"] for row in profiles) + "\n").encode("ascii")
    )
    for profile in profiles:
        profile["profile_set_hash"] = profile_set_hash
    return profiles, profile_set_hash

REGISTRY_FIELDS = (
    "factor_id",
    "factor_registry_version",
    "standard_compute_model_version",
    "term_family",
    "factor_code",
    "factor_description",
    "quantity_unit",
    "coefficient_mean",
    "coefficient_p05",
    "coefficient_p50",
    "coefficient_p95",
    "coefficient_lower_bound",
    "coefficient_upper_bound",
    "coefficient_unit",
    "strictly_positive_required",
    "benchmark_source_id",
    "registry_row_hash",
    "registry_hash",
)

INPUT_FIELDS = (
    "compute_input_id",
    "candidate_id",
    "standard_compute_model_version",
    "factor_registry_version",
    "factor_id",
    "quantity_mean",
    "quantity_p05",
    "quantity_p50",
    "quantity_p95",
    "quantity_lower_bound",
    "quantity_upper_bound",
    "quantity_low",
    "quantity_base",
    "quantity_high",
    "quantity_unit",
    "quantity_source_id",
    "estimate_status",
    "uncertainty_method",
    "draw_set_id",
    "input_row_hash",
)

ESTIMATE_FIELDS = (
    "compute_estimate_id",
    "candidate_id",
    "standard_compute_model_version",
    "reference_hardware_id",
    "hardware_normalization_version",
    "model_runtime_version",
    "tokenizer_version",
    "qa_target_version",
    "standard_compute_mean",
    "standard_compute_p05",
    "standard_compute_p50",
    "standard_compute_p95",
    "standard_compute_lower_bound",
    "standard_compute_upper_bound",
    "standard_compute_scenario_low",
    "standard_compute_scenario_base",
    "standard_compute_scenario_high",
    "standard_compute_unit",
    "energy_mean",
    "energy_p05",
    "energy_p50",
    "energy_p95",
    "energy_lower_bound",
    "energy_upper_bound",
    "energy_unit",
    "estimate_status",
    "uncertainty_method",
    "draw_set_id",
    "benchmark_source_ids_json",
    "compute_input_set_hash",
    "estimate_row_hash",
    "generated_at_utc",
)

DERIVATION_FIELDS = (
    "candidate_id",
    "compute_low",
    "compute_base",
    "compute_high",
    "factor_registry_version",
    "formula_version",
    "compute_measure_class",
    "compute_unit",
    "branch_id",
    "canon_id",
    "model_role",
    "flores_code",
    "script_code",
    "evidence_status",
    "benchmark_profile_id",
    "tokenization_measurement_set_sha256",
    "measurement_profile_registry_file_sha256",
    "measurement_profile_set_hash",
    "direct_measurement_row_hash",
    "source_reference_tokens",
    "target_ratio_low",
    "target_ratio_base",
    "target_ratio_high",
    "target_expansion_E_base",
    "target_fragmentation_P_base",
    "target_codepoint_length_L_base",
    "working_token_fragmentation_F_base",
    "fit_low",
    "fit_base",
    "fit_high",
    "fot_low",
    "fot_base",
    "fot_high",
    "frt_low",
    "frt_base",
    "frt_high",
    "terminology_entries_low",
    "terminology_entries_base",
    "terminology_entries_high",
    "weighted_document_object_units_low",
    "weighted_document_object_units_base",
    "weighted_document_object_units_high",
    "audio_program_minutes_low",
    "audio_program_minutes_base",
    "audio_program_minutes_high",
    "caption_cues_low",
    "caption_cues_base",
    "caption_cues_high",
    "signed_program_minutes_low",
    "signed_program_minutes_base",
    "signed_program_minutes_high",
)

SCORER_FIELDS = (
    "candidate_id",
    "language_target_id",
    "package_id",
    "learner_stage",
    "subject_domain",
    "delivery_format",
    "compute_scope",
    "compute_measure_class",
    "compute_low",
    "compute_base",
    "compute_high",
    "compute_unit",
    "source_id",
    "source_url",
    "source_class",
    "is_public",
    "formula_version",
    "factor_registry_version",
    "compute_input_set_hash",
    "compute_derivation_set_hash",
    "factor_registry_file_hash",
    "compute_model_role",
    "compute_evidence_status",
    "benchmark_profile_id",
    "tokenization_measurement_set_sha256",
    "measurement_profile_registry_file_sha256",
    "measurement_profile_set_hash",
    "direct_measurement_row_hash",
    "compute_binding_mode",
    "successor_roster_file_sha256",
    "target_binding_row_hash",
    "target_binding_set_hash",
    "order_b_eligible",
)


def assumptions_rows(summary: Mapping[str, Any], ratio_rows: Sequence[Mapping[str, Any]]) -> list[dict[str, str]]:
    selected = select_ratio_cases(ratio_rows)
    rows: list[dict[str, str]] = []

    def add(category: str, parameter: str, unit: str, low: Any, base: Any, high: Any, status: str, formula: str, override: str, notes: str, sources: str) -> None:
        rows.append(
            {
                "assumption_id": f"M2-A{len(rows) + 1:03d}",
                "category": category,
                "parameter": parameter,
                "unit": unit,
                "low": str(low),
                "base": str(base),
                "high": str(high),
                "evidence_status": status,
                "formula_or_definition": formula,
                "override_rule": override,
                "notes": notes,
                "source_ids": sources,
            }
        )

    add("canon", "source_reference_tokens_common_canon", "cl100k_base tokens", 100000, 100000, 100000, "DEFINED_STANDARD", "S=100000 after NFC; sentence boundaries retained", "Tokenize exact source and scale all atom counts to its measured S", "25k and 400k profiles are exact linear scale cases", "SRC25")
    add("tokenization", "source_working_per_source_reference", "ratio", *(fmt(float(summary["source_working_per_source_reference"])),) * 3, "PUBLIC_CORPUS_MEASUREMENT", "English o200k_base / English cl100k_base on FLORES devtest", "Replace with exact canonical source measurement", "Proxy source is general-domain English", "SRC24;SRC25")
    add("tokenization", "target_expansion_E_selected_case", "ratio", *(fmt(float(selected[s]["target_expansion_reference_E"])) for s in SCENARIOS), "PUBLIC_CORPUS_MEASUREMENT_CASE", "target cl100k_base / English cl100k_base", "Use exact aligned target/source measurement when available", "; ".join(f"{s}={selected[s]['flores_code']}" for s in SCENARIOS), "SRC24;SRC25")
    add("tokenization", "target_fragmentation_P_selected_case", "ratio", *(fmt(float(selected[s]["target_tokenizer_fragmentation_P"])) for s in SCENARIOS), "PUBLIC_CORPUS_MEASUREMENT_CASE", "target o200k_base / target cl100k_base", "Retokenize identical normalized target bytes with both pinned tokenizers", "Kept distinct from translation expansion", "SRC24;SRC25")
    add("tokenization", "target_codepoint_length_L_selected_case", "ratio", *(fmt(float(selected[s]["target_codepoint_length_expansion_L"])) for s in SCENARIOS), "PUBLIC_CORPUS_MEASUREMENT_CASE", "target Unicode codepoints / English Unicode codepoints", "Replace with the aligned educational target/source measurement", "Writing-length proxy only; codepoints are not graphemes, words, or semantic units", "SRC24")
    add("tokenization", "working_token_fragmentation_F_selected_case", "ratio", *(fmt(float(selected[s]["working_token_fragmentation_relative_F"])) for s in SCENARIOS), "DERIVED_PUBLIC_CORPUS_CASE", "(target o200k tokens/target codepoints)/(English cl100k tokens/English codepoints)", "Recompute on identical normalized aligned bytes", "Tokenizer-density proxy kept algebraically distinct from the codepoint-length proxy", "SRC24;SRC25")
    add("tokenization", "target_working_ratio_R_selected_case", "ratio", *(fmt(float(selected[s]["combined_target_working_per_source_reference_R"])) for s in SCENARIOS), "DERIVED_PUBLIC_CORPUS_CASE", "R=E*P", "Use exact target working tokens / source reference tokens", "Cross-language p10/p50/p90-nearest cases; not bounds or population weights", "SRC24;SRC25")
    for name, values in P.items():
        category = "media" if name.startswith(("audio", "caption", "sign", "pronunciation", "target_words", "narration", "pause", "words_per", "signed")) else "accessibility" if name.startswith(("html", "description", "publication", "validator", "formula", "diagram", "table", "heading", "links", "code")) else "text_pipeline"
        add(category, name, "declared model driver", fmt(values["low"]), fmt(values["base"]), fmt(values["high"]), "PLANNING_MODEL_DEFINITION", "See factor derivation in build_standardized_compute_model_v2.py", "Replace only through a versioned model or exact run ledger", "Coupled scenario driver; not an empirical confidence interval", "SRC04;SRC06;SRC07;SRC17;SRC20")
    add("accounting", "fresh_equivalent_compute_units", "fresh token events", "FIT+FOT+FRT", "FIT+FOT+FRT", "FIT+FOT+FRT", "DEFINED_STANDARD", "FECU=sum of disjoint fresh input, visible output, and hidden reasoning token events", "Retain components even when scalar is displayed", "Not FLOPs, energy, quality, labor, duration, price, or throughput", "SRC25")
    add("exclusion", "cached_gross_tokens", "excluded diagnostic", 0, 0, 0, "FORBIDDEN_TARGET_FACTOR", "Cache hits remain within FIT once and never create a discount, credit, or extra gross term", "None; exclusion is invariant", "May be recorded only in a non-scoring execution receipt", "")
    add("exclusion", "local_or_project_state", "excluded diagnostic", 0, 0, 0, "FORBIDDEN_TARGET_FACTOR", "No prior assets, completion, readiness, reuse, counters, staffing, funding, or schedule term", "None; exclusion is invariant", "A separately labeled programme observation cannot calibrate this model", "")
    return rows


def source_rows() -> list[dict[str, str]]:
    return [
        {"source_id": "SRC01", "organization_or_authors": "OpenAI", "title": "What are tokens and how to count them?", "source_type": "Official provider documentation", "url": "https://help.openai.com/en/articles/4936856-what-are-tokens-and-how-to-count-them", "publication_or_update": "accessed 2026-09-01", "claim_used": "Token counts depend on language and context; the English words-per-token heuristic is not multilingual", "evidence_class": "PUBLISHED_VENDOR_HEURISTIC", "limitations": "Provider- and tokenizer-specific", "retrieved_utc": "2026-09-01"},
        {"source_id": "SRC02", "organization_or_authors": "Ahia et al.", "title": "Do All Languages Cost the Same? Tokenization in the Era of Commercial Language Models", "source_type": "Peer-reviewed primary empirical study", "url": "https://aclanthology.org/2023.emnlp-main.614/", "publication_or_update": "2023", "claim_used": "Commercial tokenization differs materially across languages", "evidence_class": "PUBLISHED_MEASUREMENT", "limitations": "Models, corpora, and prices are time-specific", "retrieved_utc": "2026-09-01"},
        {"source_id": "SRC03", "organization_or_authors": "Petrov et al.", "title": "Language Model Tokenizers Introduce Unfairness Between Languages", "source_type": "Peer-reviewed primary empirical study", "url": "https://papers.neurips.cc/paper_files/paper/2023/file/74bb24dca8334adce292883b4b651eda-Paper-Conference.pdf", "publication_or_update": "2023", "claim_used": "Some parallel content and tokenizer comparisons showed very large disparities", "evidence_class": "PUBLISHED_MEASUREMENT", "limitations": "Extreme observations are stress cases, not universal priors", "retrieved_utc": "2026-09-01"},
        {"source_id": "SRC04", "organization_or_authors": "MQM Council", "title": "MQM Error Typology", "source_type": "Open translation-quality framework", "url": "https://www.themqm.org/mqm-pillars/typology/", "publication_or_update": "accessed 2026-09-01", "claim_used": "Audit dimensions cover accuracy, terminology, linguistic conventions, locale, audience, and design", "evidence_class": "STANDARDIZED_EVALUATION_FRAMEWORK", "limitations": "Does not supply token multipliers", "retrieved_utc": "2026-09-01"},
        {"source_id": "SRC06", "organization_or_authors": "European Commission Directorate-General for Translation", "title": "Translation quality evaluation: information pack for external contractors", "source_type": "Official operational methodology", "url": "https://commission.europa.eu/system/files/2024-02/DGT_Translation_quality_evaluation_Info%20pack_for_FL_contractors_27.02.2024.pdf", "publication_or_update": "2024-02-27", "claim_used": "Independent issue-based checking covers accuracy, terminology, norms, references, and style", "evidence_class": "PRIMARY_OPERATIONAL_GUIDANCE", "limitations": "Does not prescribe universal model effort", "retrieved_utc": "2026-09-01"},
        {"source_id": "SRC07", "organization_or_authors": "W3C", "title": "Web Content Accessibility Guidelines 2.2", "source_type": "W3C Recommendation", "url": "https://www.w3.org/TR/WCAG22/", "publication_or_update": "2024-12-12", "claim_used": "Accessible equivalents, captions, and named sign-language access are distinct requirements", "evidence_class": "NORMATIVE_STANDARD", "limitations": "Outcome requirements do not quantify effort", "retrieved_utc": "2026-09-01"},
        {"source_id": "SRC08", "organization_or_authors": "W3C Web Accessibility Initiative", "title": "Complex Images Tutorial", "source_type": "Official implementation guidance", "url": "https://www.w3.org/WAI/tutorials/images/complex/", "publication_or_update": "accessed 2026-09-01", "claim_used": "Complex diagrams generally need short identification and a meaningful long description", "evidence_class": "AUTHORITATIVE_GUIDANCE", "limitations": "No universal description length", "retrieved_utc": "2026-09-01"},
        {"source_id": "SRC09", "organization_or_authors": "W3C Math Working Group", "title": "MathML Core", "source_type": "Technical specification", "url": "https://www.w3.org/TR/mathml-core/", "publication_or_update": "accessed 2026-09-01", "claim_used": "MathML preserves structured mathematical notation", "evidence_class": "NORMATIVE_TECHNICAL_SPECIFICATION", "limitations": "Validity does not prove semantic transcription", "retrieved_utc": "2026-09-01"},
        {"source_id": "SRC10", "organization_or_authors": "W3C Math Working Group", "title": "Mathematical Markup Language Version 4.0", "source_type": "Technical specification", "url": "https://www.w3.org/TR/mathml4/", "publication_or_update": "accessed 2026-09-01", "claim_used": "Presentation and content markup distinguish notation from semantic structure", "evidence_class": "NORMATIVE_TECHNICAL_SPECIFICATION", "limitations": "No effort multiplier", "retrieved_utc": "2026-09-01"},
        {"source_id": "SRC11", "organization_or_authors": "W3C Publishing Working Group", "title": "EPUB 3.3", "source_type": "W3C Recommendation", "url": "https://www.w3.org/TR/epub-33/", "publication_or_update": "accessed 2026-09-01", "claim_used": "EPUB packages structured web content and media", "evidence_class": "NORMATIVE_TECHNICAL_SPECIFICATION", "limitations": "Conformance is not accessibility or semantic correctness", "retrieved_utc": "2026-09-01"},
        {"source_id": "SRC12", "organization_or_authors": "W3C Publishing Maintenance Working Group", "title": "EPUB Accessibility 1.1", "source_type": "W3C Recommendation", "url": "https://www.w3.org/TR/epub-a11y-11/", "publication_or_update": "2024-10-17", "claim_used": "Accessible EPUB conformance and discoverability requirements", "evidence_class": "NORMATIVE_STANDARD", "limitations": "Does not quantify remediation effort", "retrieved_utc": "2026-09-01"},
        {"source_id": "SRC13", "organization_or_authors": "W3C and DAISY Consortium", "title": "EPUBCheck", "source_type": "Official validator", "url": "https://github.com/w3c/epubcheck", "publication_or_update": "accessed 2026-09-01", "claim_used": "EPUB conformance validator", "evidence_class": "OFFICIAL_VALIDATION_TOOL", "limitations": "Tool scope is not semantic correctness", "retrieved_utc": "2026-09-01"},
        {"source_id": "SRC14", "organization_or_authors": "DAISY Consortium", "title": "Ace by DAISY validation guidance", "source_type": "Official accessibility validation guidance", "url": "https://kb.daisy.org/publishing/docs/epub/validation/ace.html", "publication_or_update": "accessed 2026-09-01", "claim_used": "Ace results require complementary validation and do not alone prove WCAG conformance", "evidence_class": "OFFICIAL_VALIDATION_GUIDANCE", "limitations": "Automated rule coverage is incomplete", "retrieved_utc": "2026-09-01"},
        {"source_id": "SRC16", "organization_or_authors": "W3C Voice Browser Working Group", "title": "Speech Synthesis Markup Language 1.1", "source_type": "W3C Recommendation", "url": "https://www.w3.org/TR/speech-synthesis/", "publication_or_update": "2010-09-07", "claim_used": "Pronunciation, language, rate, and other speech controls need explicit handling", "evidence_class": "NORMATIVE_TECHNICAL_SPECIFICATION", "limitations": "Synthesis behavior varies and no speed prior is supplied", "retrieved_utc": "2026-09-01"},
        {"source_id": "SRC17", "organization_or_authors": "W3C Web Accessibility Initiative", "title": "Making Audio and Video Media Accessible", "source_type": "Official accessibility guidance", "url": "https://www.w3.org/WAI/media/av/", "publication_or_update": "accessed 2026-09-01", "claim_used": "Captions, descriptive transcripts, visual description, and sign language are separate media branches", "evidence_class": "AUTHORITATIVE_GUIDANCE", "limitations": "No universal workload rate", "retrieved_utc": "2026-09-01"},
        {"source_id": "SRC18", "organization_or_authors": "United States Federal Communications Commission", "title": "Closed Captioning Quality Order FCC 14-12", "source_type": "Primary regulatory source", "url": "https://docs.fcc.gov/public/attachments/FCC-14-12A1_Rcd.pdf", "publication_or_update": "2014-02-24", "claim_used": "Accuracy, synchronicity, completeness, and placement form a useful caption QA checklist", "evidence_class": "PRIMARY_REGULATORY_SOURCE", "limitations": "US television context, not a global workload standard", "retrieved_utc": "2026-09-01"},
        {"source_id": "SRC19", "organization_or_authors": "W3C", "title": "WebVTT", "source_type": "Technical specification", "url": "https://www.w3.org/TR/webvtt1/", "publication_or_update": "accessed 2026-09-01", "claim_used": "Timed-text cue and timestamp structure", "evidence_class": "NORMATIVE_TECHNICAL_SPECIFICATION", "limitations": "Validity does not prove caption quality", "retrieved_utc": "2026-09-01"},
        {"source_id": "SRC20", "organization_or_authors": "World Federation of the Deaf", "title": "WFD Charter", "source_type": "Representative-organization charter", "url": "https://wfdeaf.org/wfd-charter-2/", "publication_or_update": "accessed 2026-09-01", "claim_used": "Sign languages are complete natural languages", "evidence_class": "AUTHORITATIVE_RIGHTS_AND_LANGUAGE_SOURCE", "limitations": "No production effort rate", "retrieved_utc": "2026-09-01"},
        {"source_id": "SRC21", "organization_or_authors": "World Federation of the Deaf and WASLI", "title": "Sign Language Interpreter Guidelines for the United Nations", "source_type": "Official practice guidance", "url": "https://wfdeaf.org/wp-content/uploads/2017/02/Interpreter-Guidelines-for-UN-Updated-August-2017-1.pdf", "publication_or_update": "2017", "claim_used": "Sign language is not universal", "evidence_class": "AUTHORITATIVE_GUIDANCE", "limitations": "Event guidance does not quantify localization duration", "retrieved_utc": "2026-09-01"},
        {"source_id": "SRC22", "organization_or_authors": "World Federation of the Deaf", "title": "Primacy of Deaf People in National Sign Language Development and Teaching", "source_type": "Official position paper", "url": "https://wfdeaf.org/resources/position-paper-on-the-primacy-of-deaf-people-in-the-development-and-teaching-of-national-sign-languages/", "publication_or_update": "accessed 2026-09-01", "claim_used": "Named sign-language work requires Deaf-community leadership and language-specific scope", "evidence_class": "AUTHORITATIVE_RIGHTS_AND_LANGUAGE_SOURCE", "limitations": "Not a compute benchmark", "retrieved_utc": "2026-09-01"},
        {"source_id": "SRC23", "organization_or_authors": "W3C Web Accessibility Initiative", "title": "Understanding Success Criterion 1.2.6: Sign Language (Prerecorded)", "source_type": "Official WCAG explanatory guidance", "url": "https://www.w3.org/WAI/WCAG22/Understanding/sign-language-prerecorded.html", "publication_or_update": "accessed 2026-09-01", "claim_used": "Named sign-language access is distinct from captions", "evidence_class": "AUTHORITATIVE_GUIDANCE", "limitations": "No workload multiplier", "retrieved_utc": "2026-09-01"},
        {"source_id": "SRC24", "organization_or_authors": "NLLB Team / Meta AI", "title": "FLORES-200 devtest parallel corpus", "source_type": "Public sentence-aligned multilingual evaluation corpus", "url": FLORES_URL, "publication_or_update": "2022 archive snapshot", "claim_used": "Exact aligned token counts for 204 language-script files and 203 non-English target variants", "evidence_class": "PUBLIC_CORPUS_MEASUREMENT", "limitations": "General-domain 1,012-sentence proxy, not educational text or a population-weighted language sample", "retrieved_utc": "2026-09-01"},
        {"source_id": "SRC25", "organization_or_authors": "OpenAI", "title": "tiktoken 0.11.0 with cl100k_base and o200k_base encoding assets", "source_type": "Pinned open-source tokenizer implementation and vocabularies", "url": "https://pypi.org/project/tiktoken/0.11.0/", "publication_or_update": "2025-08-08", "claim_used": "Reproducible reference and working token counts with exact vocabulary-asset hashes", "evidence_class": "PINNED_SOFTWARE_MEASUREMENT", "limitations": "Tokenizer representation is not linguistic difficulty or architecture-independent compute", "retrieved_utc": "2026-09-01"},
    ]


def make_report(summary: Mapping[str, Any], ratio_rows: Sequence[Mapping[str, Any]], derivations: Sequence[Mapping[str, Any]], manifest_names: Sequence[str]) -> str:
    selected = select_ratio_cases(ratio_rows)
    common = [row for row in derivations if row["canon_id"] == "CANON-100K" and row["model_role"] == "sensitivity_common_envelope"]
    primary_count = sum(row["model_role"] == "primary_measured_feature" for row in derivations)
    q = summary["cross_language_quantiles_excluding_english"]
    lines = [
        "# Standardized from-scratch AI-compute model for educational access",
        "",
        f"**Version:** `{MODEL_VERSION}`  ",
        f"**Snapshot:** {SNAPSHOT_UTC}  ",
        "**Scope:** workload normalization only. This artifact performs no empirical access ranking.",
        "",
        "## Result",
        "",
        "The model standardizes a fresh educational source into three canons—25,000, 100,000, and 400,000 `cl100k_base` reference tokens—and six output packages. It reports three disjoint token-event components: fresh input (FIT), visible output (FOT), and hidden reasoning (FRT). Their displayed scalar sum is a fresh-equivalent compute unit (FECU). Cache hits never reduce it, gross cached counters never add to it, and prior/local work never changes it.",
        "",
        f"The primary measured-feature layer contains {primary_count:,} target/canon/package derivations: the same formula and the same public benchmark protocol applied to every one of 203 FLORES-covered language-script targets. A language-blind common envelope is retained only as a sensitivity control. An unmeasured target is unavailable for Order B until the same benchmark is run; it is never assigned identity or a region/language/prestige prior.",
        "",
        "For the common 100,000-token canon:",
        "",
        "| Package | Low FECU | Base FECU | High FECU | Base FIT / FOT / FRT |",
        "|---|---:|---:|---:|---:|",
    ]
    for row in common:
        lines.append(
            f"| {row['branch_id']} | {float(row['compute_low']):,.0f} | {float(row['compute_base']):,.0f} | {float(row['compute_high']):,.0f} | {float(row['fit_base']):,.0f} / {float(row['fot_base']):,.0f} / {float(row['frt_base']):,.0f} |"
        )
    lines.extend(
        [
            "",
            "Low/base/high are coupled planning cases, not confidence intervals, prices, quality scores, means, quantiles, or bounds. They occupy the explicit `quantity_low/base/high` and `standard_compute_scenario_low/base/high` fields; probabilistic and bound fields remain blank. The high case is deliberately demanding but remains finite and is not a worst case.",
            "",
            "## 1. Accounting boundary and vocabulary",
            "",
            "- **Source reference token (SRT):** a token in the NFC-normalized source under pinned `cl100k_base` from `tiktoken==0.11.0`. The common canon is exactly `S=100,000` SRT.",
            "- **Fresh input token event (FIT):** every logical input token supplied to a model call under the working tokenizer. Cached and uncached portions are both counted once. A cache hit is neither a credit nor an extra term.",
            "- **Fresh output token event (FOT):** a visible returned token. It excludes disjoint hidden reasoning tokens.",
            "- **Fresh reasoning token event (FRT):** a hidden reasoning token only when the runtime exposes it or the planning scenario explicitly declares it. It is never also counted as FOT.",
            "- **FECU:** `FIT + FOT + FRT`. This is a standardized traffic index. It is not FLOPs, joules, wall time, money, labor, throughput, or quality.",
            "- **APM/SPM/DOU:** audio program minutes, signed program minutes, and weighted document-object units are separate workload ledgers, never token conversions.",
            "",
            "Machine validators, TTS, ASR/forced alignment, image processing, page rendering, video capture/animation, and transcoding require execution receipts with hardware/software versions, wall time, accelerator/CPU time, peak memory, bytes, and energy if measured. They are not inferred from FECU.",
            "",
            "## 2. Measured language/script representation",
            "",
            f"The builder measured the complete public FLORES-200 `devtest` split: {summary['corpus']['aligned_sentences']:,} aligned sentences in {summary['corpus']['language_script_files']} language-script files ({summary['corpus']['non_english_targets']} non-English targets). The archive is fixed at {summary['corpus']['archive_bytes']:,} bytes and SHA-256 `{summary['corpus']['archive_sha256']}`. Every sentence was normalized to NFC, tokenized separately, and then summed so that file concatenation did not create boundary tokens.",
            "",
            "Writing-length expansion and tokenizer fragmentation remain algebraically separate, with tokenizer-to-tokenizer sensitivity reported as another diagnostic:",
            "",
            "```text",
            "L = target_codepoints / english_codepoints",
            "F = (target_o200k/target_codepoints) / (english_cl100k/english_codepoints)",
            "P = target_o200k / target_cl100k        # tokenizer-to-tokenizer change on identical target bytes",
            "E = target_cl100k / english_cl100k      # reference-token ratio (still tokenizer-dependent)",
            "R = target_o200k / english_cl100k = L*F = E*P",
            "```",
            "",
            "This prevents a longer written realization from being mislabeled as tokenizer density and prevents a tokenizer change on identical target text from being mislabeled as target expansion. L is deliberately called a codepoint-length proxy: codepoints are not graphemes, words, morphemes, semantic units, or a cross-script difficulty scale.",
            "",
            "| Cross-language distribution (203 targets, equal file weights) | p10 | p50 | p90 | min | max |",
            "|---|---:|---:|---:|---:|---:|",
            f"| E | {q['E']['p10']:.3f} | {q['E']['p50']:.3f} | {q['E']['p90']:.3f} | {q['E']['p00']:.3f} | {q['E']['p100']:.3f} |",
            f"| P | {q['P']['p10']:.3f} | {q['P']['p50']:.3f} | {q['P']['p90']:.3f} | {q['P']['p00']:.3f} | {q['P']['p100']:.3f} |",
            f"| L | {q['L']['p10']:.3f} | {q['L']['p50']:.3f} | {q['L']['p90']:.3f} | {q['L']['p00']:.3f} | {q['L']['p100']:.3f} |",
            f"| F | {q['F']['p10']:.3f} | {q['F']['p50']:.3f} | {q['F']['p90']:.3f} | {q['F']['p00']:.3f} | {q['F']['p100']:.3f} |",
            f"| R | {q['R']['p10']:.3f} | {q['R']['p50']:.3f} | {q['R']['p90']:.3f} | {q['R']['p00']:.3f} | {q['R']['p100']:.3f} |",
            "",
            "The three generic planning cases are the actual language-script rows nearest the R p10/p50/p90 values, preserving each row's paired L/F and E/P rather than multiplying unrelated marginal quantiles:",
            "",
            "| Case | FLORES code | L | F | E | P | R=L×F=E×P |",
            "|---|---|---:|---:|---:|---:|---:|",
        ]
    )
    for scenario in SCENARIOS:
        row = selected[scenario]
        lines.append(f"| {scenario} | `{row['flores_code']}` | {float(row['target_codepoint_length_expansion_L']):.3f} | {float(row['working_token_fragmentation_relative_F']):.3f} | {float(row['target_expansion_reference_E']):.3f} | {float(row['target_tokenizer_fragmentation_P']):.3f} | {float(row['combined_target_working_per_source_reference_R']):.3f} |")
    lines.extend(
        [
            "",
            "These values are representation proxies, not language rankings. The primary model uses each target row's exact R as base and its twenty-block R p05/p95 as a narrow measurement-variation component inside the coupled process scenarios. It does not use the target's name, region, population, prestige, or presumed resource level. FLORES is a short general-domain benchmark; it is not a school curriculum, formula-heavy textbook, assessment bank, or sign-language corpus. The cross-language distribution is not population-weighted. Some FLORES targets used pivot translations. Block p05/p95 columns in the detailed CSV are not confidence bounds or domain-shift coverage. Replace the proxy by tokenizing an aligned educational pilot with the same pinned normalization and tokenizers when available. `standardized_compute_measurement_profiles.csv` binds each of the 203 direct profiles to the exact tokenization-file hash and its canonical measurement-row hash; a declared profile label alone is never evidence.",
            "",
            "## 3. Closed model equation",
            "",
            "Each registry row is an allowed nonnegative term with identity coefficient one. All workload assumptions are expanded into normalized, disjoint token-event quantities before summation:",
            "",
            "```text",
            "FIT(package, canon, scenario) = Σ normalized FIT factor quantities",
            "FOT(package, canon, scenario) = Σ normalized FOT factor quantities",
            "FRT(package, canon, scenario) = Σ normalized FRT factor quantities",
            "FECU(package, canon, scenario) = FIT + FOT + FRT",
            "```",
            "",
            "The registry is closed: a factor ID not in the versioned registry cannot contribute. All coefficients are positive identity conversions, so there is no subtractive credit. The normalized-input bytes, factor registry, estimates, canonical derivations, and scorer rows have row hashes and/or exact-byte SHA-256 bindings. Each package uses exactly the registered prefixes shown in the derivation companion; an absent, duplicate, unknown, wrong-unit, wrong-version, or tampered factor row fails scorer recomputation.",
            "",
            "```text",
            "source canon",
            "   │",
            "   ├── terminology ──► generation ──► independent model QA ──► repair ──► deterministic QA triage",
            "   │                                             │",
            "   │                                             └── issue manifests, never opaque self-rewrites",
            "   │",
            "   ├── accessible HTML/MathML ──► EPUB + tagged PDF validation",
            "   ├── narration script + pronunciation ──► audio execution receipt",
            "   ├── transcript + timed captions ──► timing/coverage checks",
            "   └── one named sign language ──► storyboard/annotation + separate video ledger",
            "```",
            "",
            "The media branches reuse the accepted text semantically but still count every new model read, visible output, and reasoning event. Complete-package totals add incremental branches to the text pipeline once; they do not add branch totals that each already contain text.",
            "",
            "## 4. Text, terminology, and independent QA",
            "",
            "The text branch includes concept-level terminology research, generation/adaptation, one/two/three independent model contexts, repair, and deterministic issue triage. An independent model audit receives the source, candidate target, terminology/specification, and its own instructions without the generator conversation or hidden state. The base case splits fidelity/terminology/formulas from target-language pedagogy/accessibility. The high case adds another independent context. A different prompt in the generator conversation is not independent evidence.",
            "",
            "Terminology entries retain concept, domain, source definition, target candidates, prohibited or ambiguous forms, morphology, context, pronunciation where relevant, decision status, and citations. Formula identity, numerals, units, dates, currencies, citations, cross-references, code literals, segment IDs, script/language tags, and Unicode normalization receive deterministic checks after repair.",
            "",
            "Hidden reasoning is modeled separately because runtimes may expose it separately from visible output. If a runtime does not report it, retain the declared scenario rather than silently treating it as zero. Actual ledgers must never count the same token as both FOT and FRT.",
            "",
            "## 5. Formulas, tables, diagrams, and accessible publication",
            "",
            "The source-object inventory keeps raw headings, links/cross-references, formula objects, informative diagrams/figures, semantic tables, and code blocks. The planning DOU is:",
            "",
            "```text",
            "DOU = headings + links + 3×formulas + 3×diagrams + 2×tables + 2×code_blocks",
            "```",
            "",
            "DOU is only a queueing aid. Raw counts and complexity flags remain authoritative. Image-only formulas need reconstruction and symbol-by-symbol comparison. MathML validity does not prove mathematical meaning. Diagrams need purpose, entities, relationships, direction/sequence, units/scales, salient values, and the meaning of visual encodings. Tables need real headers, scopes, captions, summaries where useful, and a reading order that survives reflow and right-to-left layouts.",
            "",
            "The accessible-publication branch creates semantic HTML/MathML, EPUB, and tagged PDF from one accepted structured master. It includes independent formula/diagram/table-description audit and repair, then validator/render issue triage. Validator execution itself stays outside FECU. Required evidence includes HTML/MathML checks, link checks, EPUBCheck, Ace with its limitations, PDF structure and extraction checks, page rendering, font/glyph coverage, keyboard/reading order, and exact output hashes.",
            "",
            "## 6. Audio, captions, and named sign-language branches",
            "",
            "**Audio.** The model counts target-script reads, navigation and pronunciation context, narration adaptation, a pronunciation lexicon, and an independent audio issue manifest. TTS inference, raw takes, regeneration, encoding, and listening time use APM and execution receipts. The APM formula is a provisional capacity proxy only:",
            "",
            "```text",
            "APM = target_working_tokens × words_per_token ÷ words_per_minute × pause_description_factor",
            "```",
            "",
            "For scripts without defensible word segmentation, replace the entire words formula with a timed subject-stratified pilot in minutes per 1,000 working tokens.",
            "",
            "**Captions/transcripts.** FIT, FOT, and FRT cover transcript enrichment, cue emission, independent content/timing audit, and repair. ASR/forced alignment is a non-token execution receipt. Mechanical checks include encoding, monotonic timestamps, overlaps/gaps, media-duration match, speaker and sound labels, placement, and transcript coverage. Cue counts are capacity proxies, not standards.",
            "",
            "**Named sign language.** Each deliverable names the sign language and regional/community variety. The branch counts only textual concept research, sign translation representation, storyboard/annotation, and model audit traffic. Signer/interpreter performance, Deaf-community language expertise, facial grammar, gaze, role shift, spatial reference, classifier/depicting constructions, filming, animation, reshoots, rendering, and review are not tokenized away. SPM is a separate provisional duration ledger. Each additional named sign language is a separate branch.",
            "",
            "## 7. Deterministic QA and calibration",
            "",
            "The executable tests enforce: archive, vocabulary-asset, and imported tokenizer-runtime hashes; 204 aligned files and 1,012 sentences each; exact `R=E×P=L×F`; 203 row-bound direct measurement profiles; a closed, byte-pinned F001–F048 registry whose every coefficient is exactly one; disjoint FIT/FOT/FRT factors; estimate recomputation from explicit scenario inputs; blank probabilistic/bound fields; package-specific APM/cue/SPM ledgers; monotone scenario totals; primary-only scorer export; exact normalized-input, canonical-derivation, measurement-profile, tokenization, and registry binding; per-row factor-ledger recomputation; rejection of coordinated profile relabel+rehash, nonidentity registries, unmeasured targets, and missing factors; absence of forbidden project/cache/reuse factors; manifest hashes; and detached execution receipts.",
            "",
            "Before operational use, run a subject-stratified educational pilot containing ordinary prose, exercises, formulas, tables, diagrams, citations, code, safety statements, and culturally adaptable passages. Replace exact source/target token ratios and raw object counts. Record per-call FIT/FOT/FRT, model/tokenizer versions, prompt/specification hashes, issue counts, patch fractions, validator cycles, APM/SPM, and machine execution receipts. Scenario values remain unchanged unless a new model version is issued.",
            "",
            "A local programme counter may be documented only as a separately labeled case-study observation. It cannot select a scenario, fit a coefficient, reduce a canon, create a cache/reuse credit, or otherwise calibrate this standard target.",
            "",
            "## 8. Scorer contract and artifacts",
            "",
            "`standardized_compute_canonical_derivations.csv` is the canonical aggregate table. `standardized_compute_scorer_rows.csv` exports only primary measured-feature profile-contract cases, never common-envelope sensitivity rows. Each row binds normalized inputs, canonical derivations, the byte-pinned identity registry, the pinned tokenization measurements, the complete direct-profile registry, and its exact measurement row. These profile-contract examples are test vectors, not successor-roster candidates: the production CLI rejects `PROFILE_CONTRACT_EXAMPLE`. `standardized_compute_successor_target_bindings.csv` exhaustively binds all 1,266 rows in the frozen successor target roster: exact language-subtag plus explicit-script matches receive a direct profile, and every unmatched or non-language target is explicit missing/unranked. Production accepts only `FROZEN_SUCCESSOR_BINDING` rows whose binding is direct, byte-bound, production-applicable, and `order_b_eligible=true`. Neither region, family, prestige, name similarity, nor the common envelope can manufacture a direct profile. The scorer pins and revalidates the roster and binding bytes, every measurement, registry, factor, and derivation hash, and recomputes low/base/high before admitting compute.",
            "",
            "The long-form factor registry follows the normative registry header. The normalized inputs and estimates preserve the normative probabilistic/bound fields but deliberately leave them blank, extending the schema with explicit scenario columns so planning cases cannot be mistaken for measurements or intervals. `standardized_compute_factor_registry.csv` is mirrored to `structured/schema/standard_compute_factor_registry.csv` because the scorer reads that closed registry by default. The build receipt is authenticated for replay by `qa/STANDARDIZED_COMPUTE_MODEL_V2_RECEIPT.sha256`, while the manifest binds the deterministic artifact set.",
            "",
            "Reproduction (from the scoped project directory; the requirements file pins accepted package bytes and the receipt additionally binds every imported tokenizer-runtime file):",
            "",
            "```powershell",
            "python -m pip install --require-hashes --no-deps --target .\\qa\\_standard_compute_tmp\\pylib313 -r .\\scripts\\standardized_compute_requirements.txt",
            "$env:PYTHONPATH = '.\\qa\\_standard_compute_tmp\\pylib313'",
            "$env:TIKTOKEN_CACHE_DIR = '.\\qa\\_standard_compute_tmp\\tiktoken_cache'",
            "python .\\scripts\\build_standardized_compute_model_v2.py",
            "python -m unittest tests.test_standardized_compute_model_v2",
            "python .\\scripts\\build_standardized_compute_model_v2.py --verify-only",
            "python .\\scripts\\build_standardized_compute_target_bindings.py --successor-roster .\\structured\\SUCCESSOR_TARGET_ROSTER_v2.json",
            "```",
            "",
            "Deterministic artifacts in the exact-byte manifest:",
            "",
        ]
    )
    lines.extend(f"- `{name}`" for name in manifest_names)
    lines.extend(
        [
            "",
            "## 9. Non-conversions",
            "",
            "No universal conversion from FECU to price, weekly throughput, quality, energy, or calendar duration is defined. Provider billing separates input, cached input, output, reasoning, audio, image, and video in changing ways; runtime depends on architecture, context, batching, routing, precision, hardware, and software. Apply a dated price card or a measured execution receipt only as a separate overlay after the standardized workload is fixed.",
            "",
        ]
    )
    return "\n".join(lines)


def make_derivation_report(
    registry: Sequence[Mapping[str, Any]],
    derivations: Sequence[Mapping[str, Any]],
) -> str:
    formulas = {
        "F001": "terminology_entries × terminology_FIT_per_entry",
        "F002": "terminology_entries × terminology_FOT_per_entry",
        "F003": "terminology_entries × terminology_FRT_per_entry",
        "F004": "source_reference_tokens × source_working/reference_ratio",
        "F005": "source_reference_tokens × generation_extra_FIT_fraction",
        "F006": "source_reference_tokens × target_working/source_reference_ratio",
        "F007": "source_reference_tokens × generation_FRT_fraction",
        "F008": "source_working_tokens × independent_QA_passes",
        "F009": "target_working_tokens × independent_QA_passes",
        "F010": "source_reference_tokens × QA_passes × QA_context_fraction",
        "F011": "target_working_tokens × QA_passes × QA_report_fraction",
        "F012": "source_reference_tokens × QA_passes × QA_FRT_fraction",
        "F013": "target_working_tokens",
        "F014": "F011 issue-manifest tokens",
        "F015": "source_reference_tokens × repair_context_fraction",
        "F016": "target_working_tokens × repair_output_fraction",
        "F017": "source_reference_tokens × repair_FRT_fraction",
        "F018": "source_reference_tokens × deterministic_triage_FIT_fraction",
        "F019": "source_reference_tokens × deterministic_triage_FOT_fraction",
        "F020": "source_reference_tokens × deterministic_triage_FRT_fraction",
        "F021": "source_reference_tokens × HTML_structure_FIT_fraction",
        "F022": "source_reference_tokens × HTML_structure_FOT_fraction",
        "F023": "source_reference_tokens × HTML_structure_FRT_fraction",
        "F024": "formulas×formula_description + diagrams×diagram_description + tables×table_summary",
        "F025": "F024 description tokens read by independent audit",
        "F026": "F024 × description_audit_FRT_multiplier",
        "F027": "F024 description tokens read for repair",
        "F028": "F024 × description_repair_FOT_multiplier",
        "F029": "F024 × description_repair_FRT_multiplier",
        "F030": "source_reference_tokens × publication_triage_FIT_fraction",
        "F031": "source_reference_tokens × publication_triage_FOT_fraction",
        "F032": "source_reference_tokens × publication_triage_FRT_fraction",
        "F033": "target_working_tokens read for narration",
        "F034": "source_reference_tokens × audio_context_FIT_fraction",
        "F035": "target_working_tokens × audio_adaptation_FOT_fraction",
        "F036": "target_working_tokens × audio_FRT_fraction",
        "F037": "pronunciation_entries × pronunciation_FIT_per_entry",
        "F038": "pronunciation_entries × pronunciation_FOT_per_entry",
        "F039": "pronunciation_entries × pronunciation_FRT_per_entry",
        "F040": "target_working_tokens read by independent audio audit",
        "F041": "target_working_tokens × audio_audit_FOT_fraction",
        "F042": "target_working_tokens × audio_audit_FRT_fraction",
        "F043": "target_working_tokens × caption_FIT_multiplier",
        "F044": "target_working_tokens × caption_FOT_multiplier",
        "F045": "target_working_tokens × caption_FRT_multiplier",
        "F046": "target_working_tokens × named_sign_FIT_multiplier",
        "F047": "target_working_tokens × named_sign_FOT_multiplier",
        "F048": "target_working_tokens × named_sign_FRT_multiplier",
    }
    factor_component = {
        row["factor_id"]: row["quantity_unit"].removeprefix("fresh_").split("_", 1)[0].upper()
        for row in registry
    }
    lines = [
        "# Human-readable derivation: standardized compute v2",
        "",
        f"**Model:** `{MODEL_VERSION}`  ",
        f"**Registry:** `{REGISTRY_VERSION}`  ",
        "**Role:** transparent derivation companion; normative numbers remain in the CSV/JSON artifacts.",
        "",
        "## Derivation boundary",
        "",
        "For a fixed target, canon, package, and coupled scenario, the builder first measures or declares primitive drivers, expands them into disjoint fresh token-event quantities, and then applies the closed registry's positive identity coefficient:",
        "",
        "```text",
        "q_i = declared or measured fresh token events for registered factor i",
        "contribution_i = q_i × 1",
        "FIT = Σ contribution_i where component_i = FIT",
        "FOT = Σ contribution_i where component_i = FOT",
        "FRT = Σ contribution_i where component_i = FRT",
        "FECU = FIT + FOT + FRT",
        "```",
        "",
        "No negative term exists. Cached input stays in FIT once; cached-gross diagnostics, existing material, readiness, completion, reuse, region, prestige, population, need, and access evidence are outside the derivation.",
        "",
        "## Target representation",
        "",
        "```text",
        "L = target codepoints / English codepoints",
        "F = (target o200k tokens / target codepoints) / (English cl100k tokens / English codepoints)",
        "E = target cl100k tokens / English cl100k tokens",
        "P = target o200k tokens / target cl100k tokens",
        "R = target o200k tokens / English cl100k tokens = L×F = E×P",
        "target_working_tokens = source_reference_tokens × R",
        "```",
        "",
        "The primary base R is measured separately for each FLORES target with identical normalized bytes, aligned sentences, tokenizers, and code. Low/high combine the same target's twenty-block R p05/p95 with the declared low/high process case. L is only a codepoint-length proxy; it is not a linguistic-difficulty unit. The common envelope is sensitivity-only. These profiles are roster-agnostic; after the successor universe freezes, each successor target must be explicitly bound to an exact measured profile. Region, family, prestige, and name similarity cannot create that binding. An unmatched target remains unavailable for Order B until measured under the same protocol.",
        "",
        "## Registered factor equations",
        "",
        "| ID | Component | Code | Normalized quantity formula |",
        "|---|---|---|---|",
    ]
    for row in registry:
        lines.append(
            f"| {row['factor_id']} | {factor_component[row['factor_id']]} | `{row['factor_code']}` | {formulas[row['factor_id']]} |"
        )
    lines.extend(
        [
            "",
            "## Package inclusion",
            "",
            "| Package | Included registered prefixes |",
            "|---|---|",
        ]
    )
    for package in PACKAGES:
        lines.append(f"| `{package['package_id']}` | {', '.join(f'`{prefix}`' for prefix in package['prefixes'])} |")
    lines.extend(
        [
            "",
            "A branch package includes the text prefix once plus its incremental prefixes. The complete package includes all prefixes once. This is why complete-package compute is not the sum of already-totaled branch package rows.",
            "",
            "## Worked common-envelope base case (100k canon)",
            "",
            "| Package | FIT | FOT | FRT | FECU | Check |",
            "|---|---:|---:|---:|---:|---|",
        ]
    )
    rows = [row for row in derivations if row["model_role"] == "sensitivity_common_envelope" and row["canon_id"] == "CANON-100K"]
    for row in rows:
        computed = float(row["fit_base"]) + float(row["fot_base"]) + float(row["frt_base"])
        lines.append(
            f"| `{row['branch_id']}` | {float(row['fit_base']):,.3f} | {float(row['fot_base']):,.3f} | {float(row['frt_base']):,.3f} | {float(row['compute_base']):,.3f} | {'PASS' if abs(computed-float(row['compute_base'])) < 0.001 else 'FAIL'} |"
        )
    lines.extend(
        [
            "",
            "The exact per-factor scenario quantities are in `structured/standardized_compute_normalized_inputs.csv`; the wide canonical sums are in `structured/standardized_compute_canonical_derivations.csv`. Scorer rows bind the exact bytes of that complete factor ledger, the canonical derivations, and the closed 48-factor registry. The scorer revalidates row hashes, units, versions, admissible primary-profile identity, and low/base/high arithmetic before accepting a row; common-envelope rows are never exported to it.",
            "",
            "## Non-token ledgers",
            "",
            "`DOU = headings + links + 3×formulas + 3×diagrams + 2×tables + 2×code_blocks`. APM appears only for audio/complete packages, cue count only for captions/complete, and SPM only for named-sign/complete; these capacity proxies remain separate from FECU. Validator/build/TTS/ASR/render/video execution needs hardware and software receipts and never enters FECU by conversion.",
            "",
        ]
    )
    return "\n".join(lines)


def deterministic_checks(
    ratio_rows: Sequence[Mapping[str, Any]],
    registry: Sequence[Mapping[str, Any]],
    inputs: Sequence[Mapping[str, Any]],
    estimates: Sequence[Mapping[str, Any]],
    derivations: Sequence[Mapping[str, Any]],
    input_bytes_hash: str,
    derivation_hash: str,
    registry_file_hash: str,
    tokenization_measurement_set_sha256: str,
    measurement_profile_registry_file_sha256: str,
    measurement_profile_set_hash: str,
    scorer_rows: Sequence[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    factor_ids = {row["factor_id"] for row in registry}
    factor_by_id = {row["factor_id"]: row for row in registry}
    derivation_by_id = {row["candidate_id"]: row for row in derivations}
    inputs_by_candidate: dict[str, list[Mapping[str, Any]]] = {}
    for row in inputs:
        inputs_by_candidate.setdefault(row["candidate_id"], []).append(row)
    checks: list[tuple[str, bool, Any]] = []
    checks.append(("flores_language_script_count", len(ratio_rows) == 204, len(ratio_rows)))
    checks.append(("flores_alignment_count", all(int(row["aligned_sentences"]) == FLORES_SENTENCES for row in ratio_rows), FLORES_SENTENCES))
    max_identity_error = max(abs(float(row["target_expansion_reference_E"]) * float(row["target_tokenizer_fragmentation_P"]) - float(row["combined_target_working_per_source_reference_R"])) for row in ratio_rows)
    checks.append(("token_ratio_identity_E_times_P_equals_R", max_identity_error < 1e-8, max_identity_error))
    max_length_fragmentation_error = max(abs(float(row["target_codepoint_length_expansion_L"]) * float(row["working_token_fragmentation_relative_F"]) - float(row["combined_target_working_per_source_reference_R"])) for row in ratio_rows)
    checks.append(("token_ratio_identity_L_times_F_equals_R", max_length_fragmentation_error < 1e-8, max_length_fragmentation_error))
    checks.append(("registry_is_closed_for_all_inputs", all(row["factor_id"] in factor_ids for row in inputs), len(factor_ids)))
    checks.append(("registry_coefficients_are_positive_identity", all(float(row["coefficient_lower_bound"]) > 0 and all(float(row[field]) == 1 for field in ("coefficient_mean", "coefficient_p05", "coefficient_p50", "coefficient_p95", "coefficient_lower_bound", "coefficient_upper_bound")) for row in registry), len(registry)))
    registry_row_hashes_valid = all(
        row["registry_row_hash"] == canonical_row_hash(row, {"registry_row_hash", "registry_hash", "component"})
        for row in registry
    )
    checks.append(("registry_row_hashes_validate", registry_row_hashes_valid, len(registry)))
    input_row_hashes_valid = all(
        row["input_row_hash"] == canonical_row_hash(row, {"input_row_hash"})
        for row in inputs
    )
    checks.append(("normalized_input_row_hashes_validate", input_row_hashes_valid, len(inputs)))
    forbidden = ("cache", "local", "project", "reuse", "readiness", "completion", "asset", "staff", "funding", "sunk")
    checks.append(("registry_has_no_forbidden_credit_or_state_factor", not any(token in (row["factor_code"] + " " + row["factor_description"]).casefold() for row in registry for token in forbidden), forbidden))
    checks.append(("scenario_totals_are_monotone", all(float(row["compute_low"]) <= float(row["compute_base"]) <= float(row["compute_high"]) for row in derivations), len(derivations)))
    checks.append(("one_estimate_per_derivation", {row["candidate_id"] for row in estimates} == {row["candidate_id"] for row in derivations}, len(estimates)))
    input_probability_fields = ("quantity_mean", "quantity_p05", "quantity_p50", "quantity_p95", "quantity_lower_bound", "quantity_upper_bound")
    estimate_probability_fields = ("standard_compute_mean", "standard_compute_p05", "standard_compute_p50", "standard_compute_p95", "standard_compute_lower_bound", "standard_compute_upper_bound")
    checks.append(("planning_inputs_do_not_claim_probability_or_bounds", all(not row[field] for row in inputs for field in input_probability_fields), len(inputs)))
    checks.append(("planning_estimates_do_not_claim_probability_or_bounds", all(not row[field] for row in estimates for field in estimate_probability_fields), len(estimates)))
    package_factor_sets_valid = True
    arithmetic_valid = True
    for candidate_id, derivation in derivation_by_id.items():
        package = next(item for item in PACKAGES if item["branch_id"] == derivation["branch_id"])
        expected = {
            factor_id
            for factor_id, factor in factor_by_id.items()
            if included_factor(factor["factor_code"], package)
        }
        candidate_inputs = inputs_by_candidate.get(candidate_id, [])
        observed = [row["factor_id"] for row in candidate_inputs]
        if len(observed) != len(set(observed)) or set(observed) != expected:
            package_factor_sets_valid = False
        for scenario in SCENARIOS:
            recomputed = sum(
                float(row[f"quantity_{scenario}"])
                * float(factor_by_id[row["factor_id"]]["coefficient_mean"])
                for row in candidate_inputs
            )
            if abs(recomputed - float(derivation[f"compute_{scenario}"])) > 0.0001:
                arithmetic_valid = False
    checks.append(("package_factor_sets_match_closed_registry", package_factor_sets_valid, len(derivations)))
    checks.append(("all_derivations_recompute_from_factor_ledger", arithmetic_valid, len(derivations)))
    def ledger_fields_are_package_specific(row: Mapping[str, Any]) -> bool:
        branch = row["branch_id"]
        groups = (
            (("audio_program_minutes_low", "audio_program_minutes_base", "audio_program_minutes_high"), branch in {"audio", "complete_access"}),
            (("caption_cues_low", "caption_cues_base", "caption_cues_high"), branch in {"captions", "complete_access"}),
            (("signed_program_minutes_low", "signed_program_minutes_base", "signed_program_minutes_high"), branch in {"named_sign", "complete_access"}),
        )
        return all(all(bool(row[field]) == expected for field in fields) for fields, expected in groups)
    checks.append(("non_token_ledgers_are_package_specific", all(ledger_fields_are_package_specific(row) for row in derivations), len(derivations)))
    checks.append(("scorer_rows_bind_exact_derivation_bytes", all(row["compute_derivation_set_hash"] == derivation_hash for row in scorer_rows), derivation_hash))
    checks.append(("scorer_rows_bind_exact_normalized_input_bytes", all(row["compute_input_set_hash"] == input_bytes_hash for row in scorer_rows), input_bytes_hash))
    checks.append(("scorer_rows_bind_exact_registry_bytes", all(row["factor_registry_file_hash"] == registry_file_hash for row in scorer_rows), registry_file_hash))
    checks.append(("scorer_rows_bind_pinned_tokenization_measurements", all(row["tokenization_measurement_set_sha256"] == tokenization_measurement_set_sha256 for row in scorer_rows), tokenization_measurement_set_sha256))
    checks.append(("scorer_rows_bind_measurement_profile_registry", all(row["measurement_profile_registry_file_sha256"] == measurement_profile_registry_file_sha256 and row["measurement_profile_set_hash"] == measurement_profile_set_hash for row in scorer_rows), measurement_profile_registry_file_sha256))
    primary_profiles = {row["flores_code"] for row in derivations if row["model_role"] == "primary_measured_feature"}
    checks.append(("primary_common_protocol_target_count", len(primary_profiles) == 203, len(primary_profiles)))
    checks.append(("common_envelope_is_separate_sensitivity", all(row["evidence_status"] == "COMMON_ENVELOPE_SENSITIVITY_ONLY" for row in derivations if row["model_role"] == "sensitivity_common_envelope"), sum(row["model_role"] == "sensitivity_common_envelope" for row in derivations)))
    primary_derivation_ids = {row["candidate_id"] for row in derivations if row["model_role"] == "primary_measured_feature"}
    checks.append(("scorer_exports_primary_rows_only", all(row["compute_model_role"] == "primary_measured_feature" and row["compute_evidence_status"] == PRIMARY_AGGREGATE_EVIDENCE_CLASS and row["benchmark_profile_id"] == row["language_target_id"] and row["compute_binding_mode"] == "PROFILE_CONTRACT_EXAMPLE" for row in scorer_rows) and {row["candidate_id"] for row in scorer_rows} == primary_derivation_ids and len(scorer_rows) == 203 * len(CANONS) * len(PACKAGES), len(scorer_rows)))
    checks.append(("primary_derivations_bind_direct_measurement_rows", all(row["benchmark_profile_id"] == f"flores:{row['flores_code']}" and row["tokenization_measurement_set_sha256"] == tokenization_measurement_set_sha256 and row["measurement_profile_registry_file_sha256"] == measurement_profile_registry_file_sha256 and row["measurement_profile_set_hash"] == measurement_profile_set_hash and bool(row["direct_measurement_row_hash"]) for row in derivations if row["model_role"] == "primary_measured_feature"), len(primary_derivation_ids)))
    checks.append(("common_envelope_has_no_direct_profile_binding", all(not row[field] for row in derivations if row["model_role"] == "sensitivity_common_envelope" for field in ("benchmark_profile_id", "tokenization_measurement_set_sha256", "measurement_profile_registry_file_sha256", "measurement_profile_set_hash", "direct_measurement_row_hash")), 18))
    checks.append(("no_empirical_access_ranking_output", True, "builder has no population, need, gain, efficiency, or ranking input"))
    return [
        {"check_id": check_id, "status": "PASS" if passed else "FAIL", "observed": observed}
        for check_id, passed, observed in checks
    ]


def build(root: Path, archive_path: Path, tokenizer_cache: Path) -> None:
    structured = root / "structured"
    scripts = root / "scripts"
    tests = root / "tests"
    qa = root / "qa"
    reports = root / "agent_reports"
    for directory in (structured, scripts, tests, qa, reports, structured / "schema"):
        directory.mkdir(parents=True, exist_ok=True)

    ratio_path = structured / "standardized_compute_tokenization_flores200.csv"
    summary_path = structured / "standardized_compute_tokenization_summary.json"
    measurement_profiles_path = structured / "standardized_compute_measurement_profiles.csv"
    registry_path = structured / "standardized_compute_factor_registry.csv"
    registry_schema_path = structured / "schema" / "standard_compute_factor_registry.csv"
    inputs_path = structured / "standardized_compute_normalized_inputs.csv"
    estimates_path = structured / "standardized_compute_estimates.csv"
    derivation_path = structured / "standardized_compute_canonical_derivations.csv"
    scorer_path = structured / "standardized_compute_scorer_rows.csv"
    model_path = structured / "standardized_compute_model.json"
    assumptions_path = structured / "standardized_compute_assumptions.csv"
    sources_path = structured / "standardized_compute_sources.csv"
    successor_roster_path = structured / "SUCCESSOR_TARGET_ROSTER_v2.json"
    target_bindings_path = structured / "standardized_compute_successor_target_bindings.csv"
    target_binding_receipt_path = qa / "STANDARDIZED_COMPUTE_TARGET_BINDING_RECEIPT.json"
    successor_roster_receipt_path = qa / "SUCCESSOR_TARGET_ROSTER_RECEIPT_20260901_v2.json"
    successor_universe_path = structured / "canonical_universe_successor_v2.json"
    successor_universe_receipt_path = qa / "SUCCESSOR_UNIVERSE_BUILD_RECEIPT_20260901_v2.json"
    alias_crosswalk_path = structured / "standardized_compute_language_alias_crosswalk.csv"
    iso6393_path = qa / "_standard_compute_tmp" / "iso-639-3.tab"
    iso6393_macrolanguage_path = qa / "_standard_compute_tmp" / "iso-639-3-macrolanguages.tab"
    iana_registry_path = qa / "_standard_compute_tmp" / "iana_language_subtag_registry.txt"

    ratio_rows, summary = measure_flores(archive_path, tokenizer_cache)
    write_csv(ratio_path, RATIO_FIELDS, ratio_rows)
    tokenization_measurement_set_sha256 = sha256_file(ratio_path)
    summary["measurement_csv_sha256"] = tokenization_measurement_set_sha256
    measurement_profiles, measurement_profile_set_hash = measurement_profile_rows(
        ratio_rows,
        tokenization_measurement_set_sha256,
    )
    write_csv(measurement_profiles_path, MEASUREMENT_PROFILE_FIELDS, measurement_profiles)
    measurement_profile_registry_file_sha256 = sha256_file(measurement_profiles_path)
    alias_rows, alias_set_hash = target_binding_builder.build_alias_crosswalk(
        iso6393_path,
        iso6393_macrolanguage_path,
        iana_registry_path,
    )
    target_binding_builder.write_alias_csv(alias_crosswalk_path, alias_rows)
    target_bindings, target_binding_receipt = target_binding_builder.build_bindings(
        successor_roster_path,
        measurement_profiles_path,
        successor_roster_receipt_path,
        successor_universe_path,
        successor_universe_receipt_path,
    )
    target_binding_builder.write_csv(target_bindings_path, target_bindings)
    target_binding_receipt["binding_registry_file_sha256"] = sha256_file(target_bindings_path)
    target_binding_receipt["binding_registry_path"] = str(target_bindings_path.resolve())
    write_json(target_binding_receipt_path, target_binding_receipt)
    summary["measurement_profile_registry"] = {
        "rows": len(measurement_profiles),
        "file_sha256": measurement_profile_registry_file_sha256,
        "semantic_set_hash": measurement_profile_set_hash,
    }
    write_json(summary_path, summary)
    registry, inputs, estimates, derivations, model = build_model_rows(
        ratio_rows,
        summary,
        measurement_profiles,
        measurement_profile_registry_file_sha256,
        measurement_profile_set_hash,
        tokenization_measurement_set_sha256,
    )
    write_csv(registry_path, REGISTRY_FIELDS, registry)
    write_csv(registry_schema_path, REGISTRY_FIELDS, registry)
    write_csv(inputs_path, INPUT_FIELDS, inputs)
    input_bytes_hash = sha256_file(inputs_path)
    for row in estimates:
        row["compute_input_set_hash"] = input_bytes_hash
        row["estimate_row_hash"] = canonical_row_hash(row, {"estimate_row_hash"})
    write_csv(estimates_path, ESTIMATE_FIELDS, estimates)
    write_csv(derivation_path, DERIVATION_FIELDS, derivations)
    derivation_hash = sha256_file(derivation_path)

    package_by_branch = {package["branch_id"]: package for package in PACKAGES}
    scorer_rows: list[dict[str, Any]] = []
    source_ids_by_candidate: dict[str, set[str]] = defaultdict(set)
    for input_row in inputs:
        source_ids_by_candidate[input_row["candidate_id"]].update(
            source_id for source_id in str(input_row["quantity_source_id"]).split("+") if source_id
        )
    for row in derivations:
        if row["model_role"] != "primary_measured_feature":
            continue
        package = package_by_branch[row["branch_id"]]
        scorer_rows.append(
            {
                "candidate_id": row["candidate_id"],
                "language_target_id": f"flores:{row['flores_code']}",
                "package_id": package["package_id"],
                "learner_stage": "COMMON",
                "subject_domain": "mixed_educational_proxy",
                "delivery_format": package["delivery_format"],
                "compute_scope": "standardized_from_scratch",
                "compute_measure_class": row["compute_measure_class"],
                "compute_low": row["compute_low"],
                "compute_base": row["compute_base"],
                "compute_high": row["compute_high"],
                "compute_unit": row["compute_unit"],
                "source_id": "+".join(sorted(source_ids_by_candidate[row["candidate_id"]])),
                "source_url": FLORES_URL,
                "source_class": "measurement_anchored_planning_model",
                "is_public": "true",
                "formula_version": FORMULA_VERSION,
                "factor_registry_version": REGISTRY_VERSION,
                "compute_input_set_hash": input_bytes_hash,
                "compute_derivation_set_hash": derivation_hash,
                "factor_registry_file_hash": sha256_file(registry_path),
                "compute_model_role": row["model_role"],
                "compute_evidence_status": row["evidence_status"],
                "benchmark_profile_id": row["benchmark_profile_id"],
                "tokenization_measurement_set_sha256": row["tokenization_measurement_set_sha256"],
                "measurement_profile_registry_file_sha256": row["measurement_profile_registry_file_sha256"],
                "measurement_profile_set_hash": row["measurement_profile_set_hash"],
                "direct_measurement_row_hash": row["direct_measurement_row_hash"],
                "compute_binding_mode": "PROFILE_CONTRACT_EXAMPLE",
                "successor_roster_file_sha256": "",
                "target_binding_row_hash": "",
                "target_binding_set_hash": "",
                "order_b_eligible": "",
            }
        )
    write_csv(scorer_path, SCORER_FIELDS, scorer_rows)
    model["exact_byte_bindings"] = {
        "normalized_inputs_sha256": input_bytes_hash,
        "canonical_derivations_sha256": derivation_hash,
        "factor_registry_file_sha256": sha256_file(registry_path),
        "tokenization_measurement_csv_sha256": sha256_file(ratio_path),
        "measurement_profile_registry_file_sha256": measurement_profile_registry_file_sha256,
        "measurement_profile_set_hash": measurement_profile_set_hash,
        "successor_target_roster_file_sha256": sha256_file(successor_roster_path),
        "target_binding_registry_file_sha256": sha256_file(target_bindings_path),
        "target_binding_set_hash": target_binding_receipt["binding_set_hash"],
        "language_alias_crosswalk_file_sha256": sha256_file(alias_crosswalk_path),
        "language_alias_crosswalk_set_hash": alias_set_hash,
    }
    write_json(model_path, model)

    assumption_fields = ("assumption_id", "category", "parameter", "unit", "low", "base", "high", "evidence_status", "formula_or_definition", "override_rule", "notes", "source_ids")
    source_fields = ("source_id", "organization_or_authors", "title", "source_type", "url", "publication_or_update", "claim_used", "evidence_class", "limitations", "retrieved_utc")
    write_csv(assumptions_path, assumption_fields, assumptions_rows(summary, ratio_rows))
    write_csv(sources_path, source_fields, source_rows())

    # Report names are fixed before the report itself is written, so its prose is deterministic.
    manifest_relatives = [
        "agent_reports/standardized_compute_model.md",
        "agent_reports/standardized_compute_derivation.md",
        "scripts/build_standardized_compute_model_v2.py",
        "scripts/build_standardized_compute_target_bindings.py",
        "scripts/needs_access_ranking.py",
        "scripts/NEEDS_ACCESS_RANKING_README.md",
        "scripts/standardized_compute_requirements.txt",
        "structured/standardized_compute_assumptions.csv",
        "structured/standardized_compute_sources.csv",
        "structured/standardized_compute_tokenization_flores200.csv",
        "structured/standardized_compute_tokenization_summary.json",
        "structured/standardized_compute_measurement_profiles.csv",
        "structured/standardized_compute_language_alias_crosswalk.csv",
        "structured/SUCCESSOR_TARGET_ROSTER_v2.json",
        "structured/standardized_compute_successor_target_bindings.csv",
        "structured/standardized_compute_factor_registry.csv",
        "structured/schema/standard_compute_factor_registry.csv",
        "structured/standardized_compute_normalized_inputs.csv",
        "structured/standardized_compute_estimates.csv",
        "structured/standardized_compute_canonical_derivations.csv",
        "structured/standardized_compute_scorer_rows.csv",
        "structured/standardized_compute_model.json",
        "tests/test_standardized_compute_model_v2.py",
        "qa/STANDARDIZED_COMPUTE_TARGET_BINDING_RECEIPT.json",
    ]
    report_path = reports / "standardized_compute_model.md"
    report_path.write_text(make_report(summary, ratio_rows, derivations, manifest_relatives), encoding="utf-8", newline="")
    derivation_report_path = reports / "standardized_compute_derivation.md"
    derivation_report_path.write_text(make_derivation_report(registry, derivations), encoding="utf-8", newline="")

    checks = deterministic_checks(
        ratio_rows,
        registry,
        inputs,
        estimates,
        derivations,
        input_bytes_hash,
        derivation_hash,
        sha256_file(registry_path),
        tokenization_measurement_set_sha256,
        measurement_profile_registry_file_sha256,
        measurement_profile_set_hash,
        scorer_rows,
    )
    if any(check["status"] != "PASS" for check in checks):
        raise ValueError(f"deterministic model checks failed: {checks}")
    qa_payload = {
        "schema_version": "interlanguage/standard-compute-deterministic-qa/2.0.0",
        "model_version": MODEL_VERSION,
        "snapshot_utc": SNAPSHOT_UTC,
        "checks": checks,
        "overall_status": "PASS",
    }
    write_json(qa / "STANDARDIZED_COMPUTE_MODEL_V2_DETERMINISTIC_QA.json", qa_payload)

    manifest_entries: list[tuple[str, str]] = []
    for relative in manifest_relatives + ["qa/STANDARDIZED_COMPUTE_MODEL_V2_DETERMINISTIC_QA.json"]:
        path = root / relative
        if not path.exists():
            raise FileNotFoundError(f"manifest artifact is absent: {relative}")
        manifest_entries.append((sha256_file(path), relative.replace("\\", "/")))
    manifest_path = structured / "standardized_compute_hashes.sha256"
    manifest_path.write_text("".join(f"{digest} *{relative}\n" for digest, relative in manifest_entries), encoding="ascii", newline="")

    receipt = {
        "schema_version": "interlanguage/standard-compute-build-receipt/2.0.0",
        "model_version": MODEL_VERSION,
        "snapshot_utc": SNAPSHOT_UTC,
        "status": "PASS",
        "python": platform.python_version(),
        "platform": platform.platform(),
        "inputs": {
            "flores_archive": {"bytes": archive_path.stat().st_size, "sha256": sha256_file(archive_path), "url": FLORES_URL},
            "tiktoken_version": TIKTOKEN_VERSION,
            "reference_tokenizer": REFERENCE_TOKENIZER,
            "working_tokenizer": WORKING_TOKENIZER,
            "cl100k_asset_sha256": CL100K_ASSET_SHA256,
            "o200k_asset_sha256": O200K_ASSET_SHA256,
            "runtime_files": summary["tokenizers"]["runtime_files"],
            "iso6393_table": {"bytes": iso6393_path.stat().st_size, "sha256": sha256_file(iso6393_path), "url": "https://iso639-3.sil.org/code_tables/download_tables"},
            "iso6393_macrolanguage_table": {"bytes": iso6393_macrolanguage_path.stat().st_size, "sha256": sha256_file(iso6393_macrolanguage_path), "url": "https://iso639-3.sil.org/code_tables/download_tables"},
            "iana_language_subtag_registry": {"bytes": iana_registry_path.stat().st_size, "sha256": sha256_file(iana_registry_path), "url": "https://www.iana.org/assignments/language-subtag-registry/language-subtag-registry"},
        },
        "counts": {
            "language_script_files": len(ratio_rows),
            "non_english_targets": sum(row["is_reference_source"] == "false" for row in ratio_rows),
            "direct_measurement_profiles": len(measurement_profiles),
            "successor_target_bindings": len(target_bindings),
            "successor_direct_profile_bindings": target_binding_receipt["counts"]["direct_profile_bound"],
            "successor_explicit_missing_bindings": target_binding_receipt["counts"]["no_direct_profile"],
            "successor_production_point_eligible_bindings": target_binding_receipt["counts"]["production_direct_profile_eligible"],
            "factor_registry_rows": len(registry),
            "normalized_input_rows": len(inputs),
            "estimate_rows": len(estimates),
            "canonical_derivation_rows": len(derivations),
            "scorer_contract_rows": len(scorer_rows),
        },
        "bindings": model["exact_byte_bindings"],
        "deterministic_qa_sha256": sha256_file(qa / "STANDARDIZED_COMPUTE_MODEL_V2_DETERMINISTIC_QA.json"),
        "artifact_manifest_sha256": sha256_file(manifest_path),
        "replay": "python scripts/build_standardized_compute_model_v2.py && python -m unittest tests.test_standardized_compute_model_v2 && python scripts/build_standardized_compute_model_v2.py --verify-only",
        "notes": [
            "No empirical access ranking was executed.",
            "Primary measured-feature rows use the same formula and benchmark protocol for every covered target; the language-blind common envelope is sensitivity-only.",
            "An unmeasured language-script target is unavailable for Order B until measured under the same protocol; no identity, region, language, or prestige shortcut is permitted.",
            "No population, need, resource, project-state, cache-discount, prior-work, or local programme counter was read by the builder.",
            "Low/base/high are coupled planning cases, not statistical intervals or bounds.",
        ],
    }
    receipt_path = qa / "STANDARDIZED_COMPUTE_MODEL_V2_RECEIPT.json"
    write_json(receipt_path, receipt)
    (qa / "STANDARDIZED_COMPUTE_MODEL_V2_RECEIPT.sha256").write_text(
        f"{sha256_file(receipt_path)} *STANDARDIZED_COMPUTE_MODEL_V2_RECEIPT.json\n",
        encoding="ascii",
        newline="",
    )


def verify(root: Path) -> None:
    manifest_path = root / "structured" / "standardized_compute_hashes.sha256"
    failures: list[str] = []
    for line in manifest_path.read_text(encoding="ascii").splitlines():
        digest, relative = line.split(" *", 1)
        path = root / relative
        if not path.exists():
            failures.append(f"missing:{relative}")
        elif sha256_file(path) != digest:
            failures.append(f"hash:{relative}")
    receipt_path = root / "qa" / "STANDARDIZED_COMPUTE_MODEL_V2_RECEIPT.json"
    receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    receipt_sidecar = root / "qa" / "STANDARDIZED_COMPUTE_MODEL_V2_RECEIPT.sha256"
    expected_receipt_line = f"{sha256_file(receipt_path)} *STANDARDIZED_COMPUTE_MODEL_V2_RECEIPT.json"
    if not receipt_sidecar.exists() or receipt_sidecar.read_text(encoding="ascii").strip() != expected_receipt_line:
        failures.append("receipt_sidecar_binding")
    derivation = root / "structured" / "standardized_compute_canonical_derivations.csv"
    scorer = root / "structured" / "standardized_compute_scorer_rows.csv"
    expected_derivation = sha256_file(derivation)
    expected_inputs = sha256_file(root / "structured" / "standardized_compute_normalized_inputs.csv")
    expected_registry = sha256_file(root / "structured" / "standardized_compute_factor_registry.csv")
    tokenization_path = root / "structured" / "standardized_compute_tokenization_flores200.csv"
    measurement_profiles_path = root / "structured" / "standardized_compute_measurement_profiles.csv"
    expected_tokenization = sha256_file(tokenization_path)
    expected_measurement_profiles = sha256_file(measurement_profiles_path)
    with tokenization_path.open("r", encoding="utf-8", newline="") as handle:
        token_rows = list(csv.DictReader(handle))
    with measurement_profiles_path.open("r", encoding="utf-8", newline="") as handle:
        measurement_profiles = list(csv.DictReader(handle))
    token_by_profile = {
        f"flores:{row['flores_code']}": row
        for row in token_rows
        if row["is_reference_source"] == "false"
    }
    profile_set_hashes = {row["profile_set_hash"] for row in measurement_profiles}
    observed_profile_row_hashes: list[str] = []
    profiles_valid = len(measurement_profiles) == 203 and set(token_by_profile) == {row["benchmark_profile_id"] for row in measurement_profiles}
    for profile in measurement_profiles:
        observed_profile_row_hash = canonical_row_hash(profile, {"profile_row_hash", "profile_set_hash"})
        observed_profile_row_hashes.append(observed_profile_row_hash)
        token_row = token_by_profile.get(profile["benchmark_profile_id"])
        profiles_valid = profiles_valid and bool(token_row) and profile["profile_row_hash"] == observed_profile_row_hash
        profiles_valid = profiles_valid and profile["tokenization_measurement_set_sha256"] == expected_tokenization
        profiles_valid = profiles_valid and profile["direct_measurement_row_hash"] == canonical_row_hash(token_row or {}, set())
    expected_profile_set_hash = sha256_bytes(("\n".join(observed_profile_row_hashes) + "\n").encode("ascii"))
    profiles_valid = profiles_valid and profile_set_hashes == {expected_profile_set_hash}
    if not profiles_valid:
        failures.append("measurement_profile_registry_binding")
    with scorer.open("r", encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    if not rows or any(
        row["compute_derivation_set_hash"] != expected_derivation
        or row["compute_input_set_hash"] != expected_inputs
        or row["factor_registry_file_hash"] != expected_registry
        or row["compute_model_role"] != "primary_measured_feature"
        or row["compute_evidence_status"] != PRIMARY_AGGREGATE_EVIDENCE_CLASS
        or row["tokenization_measurement_set_sha256"] != expected_tokenization
        or row["measurement_profile_registry_file_sha256"] != expected_measurement_profiles
        or row["measurement_profile_set_hash"] != expected_profile_set_hash
        or row["direct_measurement_row_hash"] != next((profile["direct_measurement_row_hash"] for profile in measurement_profiles if profile["benchmark_profile_id"] == row["benchmark_profile_id"]), "")
        or row["compute_binding_mode"] != "PROFILE_CONTRACT_EXAMPLE"
        for row in rows
    ):
        failures.append("scorer_derivation_binding")
    if receipt["artifact_manifest_sha256"] != sha256_file(manifest_path):
        failures.append("receipt_manifest_binding")
    if failures:
        raise SystemExit("verification failed: " + ",".join(failures))
    print(f"PASS model={MODEL_VERSION} manifest={sha256_file(manifest_path)} rows={len(rows)}")


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    default_root = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=default_root)
    parser.add_argument(
        "--flores-archive",
        type=Path,
        default=default_root / "qa" / "_standard_compute_tmp" / "flores200_dataset.tar.gz",
    )
    parser.add_argument(
        "--tokenizer-cache",
        type=Path,
        default=default_root / "qa" / "_standard_compute_tmp" / "tiktoken_cache",
    )
    parser.add_argument("--verify-only", action="store_true")
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    if args.verify_only:
        verify(args.root)
    else:
        build(args.root, args.flores_archive, args.tokenizer_cache)
        verify(args.root)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
