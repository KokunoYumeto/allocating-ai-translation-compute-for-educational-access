#!/usr/bin/env python3
"""Build the uniform exact-target OER gap evidence matrix.

This is a pre-scorer evidence transform.  It never ranks targets and never
converts missing catalogue or item evidence into a scarcity number.  The only
local inputs used are the requested seed audit, exact target identities, and
the counterfactual exclusion policy.  Access claims must resolve to independent
external sources in the emitted registry.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import html
import json
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable, Mapping


ROOT = Path(__file__).resolve().parents[1]
STRUCTURED = ROOT / "structured"
QA = ROOT / "qa"
REPORTS = ROOT / "agent_reports"

SEED_EVIDENCE = STRUCTURED / "oer_scarcity_evidence.json"
IDENTITY_INPUT = STRUCTURED / "canonical_universe_proposal.json"
BASELINE_POLICY = STRUCTURED / "baseline_resource_policy.json"
EXCLUSION_REGISTRY = STRUCTURED / "program_output_exclusion_register.json"

SNAPSHOT_OUT = STRUCTURED / "oer_catalog_inventory_snapshot.json"
TARGETS_OUT = STRUCTURED / "oer_gap_target_roster.csv"
SOURCES_OUT = STRUCTURED / "oer_gap_source_registry.json"
QUERIES_OUT = STRUCTURED / "oer_gap_query_manifest.csv"
MATRIX_OUT = STRUCTURED / "oer_target_canon_evidence_matrix.csv"
DERIVATION_OUT = STRUCTURED / "oer_resource_gap_derivation_inputs.csv"
EXPANDED_OUT = STRUCTURED / "oer_scarcity_evidence_expanded.json"
MANIFEST_OUT = STRUCTURED / "oer_gap_canonical_manifest.json"
VALIDATION_OUT = QA / "OER_GAP_EXPANSION_VALIDATION.json"
REPORT_OUT = REPORTS / "OER_GAP_EXPANSION_AUDIT.md"

AUDIT_DATE = "2026-09-01"
AUDITED_AT_UTC = "2026-09-01T00:00:00Z"
USER_AGENT = "Interlanguage-OER-Evidence-Audit/2.0 (+bounded reproducibility query)"


STAGES = [
    ("E0", "ISCED 0 / pre-primary and school readiness"),
    ("E1", "first three years of ISCED 1"),
    ("E2", "remaining ISCED 1"),
    ("E3", "ISCED 2 / lower secondary"),
    ("E4", "ISCED 3 / upper secondary"),
    ("E5", "ISCED 4-8 gateway and discipline-specific learning"),
    ("E6", "adult basic and second-chance learning"),
]

SUBJECTS = [
    ("LANGUAGE_LITERACY", "language, literacy, literature, and academic communication"),
    ("MATHEMATICS_DATA", "mathematics, numeracy, statistics, and data reasoning"),
    ("SCIENCE_HEALTH", "natural science, climate, health, and safety"),
    ("SOCIAL_CIVIC", "social studies, history, geography, civics, and media literacy"),
    ("COMPUTING_DIGITAL", "computing, digital literacy, and introductory AI literacy"),
]

INTERNATIONAL_CATALOGS = (
    "GDL_API",
    "AFRICAN_STORYBOOK",
    "PRESSBOOKS_DIRECTORY",
    "STORYWEAVER",
)

F_GRADES = {"F0", "F1", "F2", "F3", "F4"}
O_GRADES = {"O0", "O1", "O2", "O3"}
FINDING_STATUSES = {"RESOURCE_FOUND", "NO_QUALIFYING_RESOURCE_FOUND", "SEARCH_UNRESOLVED"}
GATE_STATUSES = {
    "UNRESOLVED",
    "VERIFIED_PASS",
    "VERIFIED_FAIL",
    "PARTIAL",
    "PLATFORM_CAPABILITY_ITEM_PENDING",
    "NOT_APPLICABLE",
}
QUERY_STATUSES = {
    "CATALOGUE_LANGUAGE_PRESENCE_ONLY",
    "EXACT_CELL_ITEM_FOUND",
    "SEARCH_UNRESOLVED_NO_EXACT_MATCH",
    "SEARCH_UNRESOLVED_TECHNICAL",
    "SEARCH_UNRESOLVED_NATIVE_LOCATOR",
    "SEARCH_UNRESOLVED_CELL_FIT",
}


TARGET_FIELDS = (
    "target_id",
    "language_tag",
    "language_names_json",
    "script_orthography_json",
    "territories_json",
    "language_mode",
    "identity_exactness",
    "identity_only_not_access_evidence",
    "target_row_hash",
)

QUERY_FIELDS = (
    "query_id",
    "matrix_row_id",
    "target_id",
    "canon_atom_id",
    "catalog_id",
    "query_method",
    "query_url",
    "query_terms_json",
    "queried_at_utc",
    "http_status",
    "query_status",
    "catalogue_hit_count",
    "language_match_status",
    "script_match_status",
    "territory_match_status",
    "stage_match_status",
    "subject_match_status",
    "curriculum_coverage_credit_allowed",
    "source_ids_json",
    "caveat",
    "query_row_hash",
)

MATRIX_FIELDS = (
    "matrix_row_id",
    "target_id",
    "language_tag",
    "language_names_json",
    "script_orthography_json",
    "territories_json",
    "isced_stage",
    "stage_label",
    "subject_domain",
    "subject_label",
    "canon_id",
    "canon_version",
    "canon_atom_id",
    "baseline_access_endpoint_id",
    "resource_route_id",
    "finding_status",
    "functional_access_grade",
    "open_adaptation_grade",
    "exact_language_variety_script_status",
    "free_access_status",
    "open_license_status",
    "adaptation_permission_status",
    "redistribution_permission_status",
    "completeness_status",
    "exercises_status",
    "answers_status",
    "download_status",
    "offline_status",
    "accessibility_status",
    "self_study_usability_status",
    "alignment_status",
    "technical_integrity_status",
    "coverage_credit_status",
    "evidence_grade",
    "source_ids_json",
    "query_ids_json",
    "repository_count_used_as_coverage",
    "unresolved_source_flag",
    "independent_origin_status",
    "program_exclusion_status",
    "baseline_policy_version",
    "baseline_observation_date",
    "caveat",
    "input_row_hash",
)

DERIVATION_FIELDS = (
    "derivation_row_id",
    "matrix_row_id",
    "target_id",
    "canon_atom_id",
    "baseline_functional_route_id",
    "baseline_access_endpoint_id",
    "finding_status",
    "resource_gap_low",
    "resource_gap_base",
    "resource_gap_high",
    "derivation_status",
    "unresolved_source_flag",
    "source_ids_json",
    "evidence_matrix_row_hash",
    "baseline_policy_version",
    "baseline_observation_date",
    "program_exclusion_registry_hash",
    "program_exclusion_status",
    "derivation_row_hash",
)


GDL_URL = "https://content.digitallibrary.io/wp-json/content-api/v1/languages"
GDL_API_DOC = "https://content.digitallibrary.io/api/"
ASB_URL = "https://www.africanstorybook.org/"
PRESSBOOKS_GUIDE_URL = "https://pressbooks.pub/guide/chapter/find-books-on-the-pressbooks-directory/"
PRESSBOOKS_QUERY_ROOT = "https://pressbooks.directory/"
STORYWEAVER_OPEN_URL = "https://storyweaver.org.in/en/open-content"
STORYWEAVER_QUERY_ROOT = "https://storyweaver.org.in/en/stories"


TERRITORY_SOURCE_IDS: dict[str, tuple[str, ...]] = {
    "IN": ("INDIA_DIKSHA_2026",),
    "ID": ("INDONESIA_SIBI_2026",),
    "CN": ("CHINA_SMARTEDU_BASIC_2026",),
    "MX": ("MEXICO_CONALITEG_2025_2026",),
    "BR": ("BRAZIL_PNLD_DIGITAL_2026",),
}

# These are exact source-to-target equivalences already present in the requested
# seed audit.  Generic language entries are deliberately not projected onto a
# territory-specific target.
SEED_TARGET_ALIASES = {
    "lang:id-Latn-ID": "id-Latn-ID",
    "lang:hi-Deva-IN": "hi-Deva-IN",
    "lang:mr-Deva-IN": "mr-Deva-IN",
    "lang:pa-Guru-IN": "pa-Guru-IN",
    "lang:ta-Taml-IN": "ta-Taml-IN",
    "lang:te-Telu-IN": "te-Telu-IN",
    "lang:ur-Arab-IN": "ur-Arab-IN",
    "lang:jv-Latn-ID": "jv-Latn-ID",
    "lang:my-Mymr-MM": "my-Mymr-MM",
}

# GDL exposes a mix of ISO 639-1 and 639-3 slugs.  Only explicit equivalences
# are allowed; similarity or macrolanguage guesses are prohibited.
GDL_CODE_EQUIVALENTS: dict[str, tuple[str, ...]] = {
    "as": ("as", "asm"),
    "awa": ("awa", "aw"),
    "bn": ("bn", "ben"),
    "gu": ("gu", "guj"),
    "hi": ("hi", "hin"),
    "id": ("id", "ind"),
    "km": ("km", "khm"),
    "kn": ("kn", "kan"),
    "ml": ("ml", "mal"),
    "mr": ("mr", "mar"),
    "my": ("my", "mya"),
    "ne": ("ne", "nep"),
    "or": ("or", "ory"),
    "pa": ("pa", "pan"),
    "ps": ("ps", "pus"),
    "sd": ("sd", "snd"),
    "ta": ("ta", "tam"),
    "te": ("te", "tel"),
    "ur": ("ur", "urd"),
    "uz": ("uz", "uzb"),
    "yo": ("yo", "yor"),
}


def canonical_json_bytes(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, ensure_ascii=True, separators=(",", ":")).encode("utf-8")


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def row_hash(row: Mapping[str, Any], hash_field: str) -> str:
    return sha256_bytes(canonical_json_bytes({key: row[key] for key in row if key != hash_field}))


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(json.dumps(value, ensure_ascii=True, indent=2, sort_keys=True).encode("utf-8") + b"\n")


def write_csv(path: Path, fields: Iterable[str], rows: Iterable[Mapping[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(fields), extrasaction="raise", lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def compact_json(value: Any) -> str:
    return canonical_json_bytes(value).decode("ascii")


def fetch(url: str) -> tuple[int, bytes, str]:
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, "Accept": "*/*"})
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            return int(response.status), response.read(), ""
    except urllib.error.HTTPError as exc:
        body = exc.read()
        return int(exc.code), body, f"HTTPError:{exc.code}"
    except Exception as exc:  # bounded evidence capture; failure remains unresolved
        return 0, b"", f"{type(exc).__name__}:{exc}"


def parse_asb_languages(raw: bytes) -> list[dict[str, str]]:
    text = raw.decode("utf-8", errors="replace")
    match = re.search(r'var languages = "(?P<options>.*?)";', text, flags=re.DOTALL)
    if not match:
        raise ValueError("African Storybook language inventory was not found in the official homepage")
    options = []
    for value, name in re.findall(r"<option(?: selected)? value='([^']+)'(?: selected)?>(.*?)</option>", match.group("options")):
        clean = html.unescape(re.sub(r"<[^>]+>", "", name)).strip()
        if value != "0" and clean:
            options.append({"catalog_language_id": value, "name": clean})
    if len(options) < 100:
        raise ValueError(f"African Storybook inventory unexpectedly short: {len(options)}")
    return sorted(options, key=lambda row: (row["name"].casefold(), row["catalog_language_id"]))


def refresh_catalog_snapshot() -> dict[str, Any]:
    gdl_status, gdl_raw, gdl_error = fetch(GDL_URL)
    if gdl_status != 200:
        raise ValueError(f"GDL language API retrieval failed closed: {gdl_status} {gdl_error}")
    gdl_rows = json.loads(gdl_raw.decode("utf-8"))
    if not isinstance(gdl_rows, list) or len(gdl_rows) < 100:
        raise ValueError("GDL language API did not return the expected language list")
    gdl_languages = sorted(
        [
            {
                "name": str(row["name"]),
                "slug": str(row["slug"]),
                "catalogue_resource_count": int(row.get("count", 0)),
            }
            for row in gdl_rows
        ],
        key=lambda row: (row["slug"], row["name"].casefold()),
    )

    asb_status, asb_raw, asb_error = fetch(ASB_URL)
    if asb_status != 200:
        raise ValueError(f"African Storybook retrieval failed closed: {asb_status} {asb_error}")
    asb_languages = parse_asb_languages(asb_raw)

    press_status, press_raw, press_error = fetch(PRESSBOOKS_QUERY_ROOT + "?q=lang%3AEnglish")
    story_status, story_raw, story_error = fetch(STORYWEAVER_QUERY_ROOT + "?query=English")
    press_challenge = b"cf_chl" in press_raw or b"Enable JavaScript and cookies" in press_raw
    story_challenge = b"cf_chl" in story_raw or b"Enable JavaScript and cookies" in story_raw
    snapshot = {
        "schema": "interlanguage/oer-catalog-inventory-snapshot/1.0.0",
        "audit_date": AUDIT_DATE,
        "retrieval_protocol": {
            "user_agent": USER_AGENT,
            "timeout_seconds": 30,
            "retry_count": 0,
            "interpretation": "One official catalogue inventory/probe is normalized; per-cell lookups are deterministic queries over these bytes. A technical failure is unresolved, never a zero-result claim.",
        },
        "gdl": {
            "url": GDL_URL,
            "http_status": gdl_status,
            "response_sha256": sha256_bytes(gdl_raw),
            "language_count": len(gdl_languages),
            "languages": gdl_languages,
        },
        "african_storybook": {
            "url": ASB_URL,
            "http_status": asb_status,
            "response_sha256": sha256_bytes(asb_raw),
            "language_count": len(asb_languages),
            "languages": asb_languages,
        },
        "pressbooks_probe": {
            "url": PRESSBOOKS_QUERY_ROOT + "?q=lang%3AEnglish",
            "http_status": press_status,
            "response_sha256": sha256_bytes(press_raw) if press_raw else "",
            "error": press_error,
            "access_state": "TECHNICAL_CHALLENGE_OR_HTTP_BLOCK" if press_status != 200 or press_challenge else "ACCESSIBLE_RESPONSE_NOT_NORMALIZED",
            "interpretation": "The same public route is used for all generated cell queries. A blocked probe makes every result unresolved; it is not evidence of no books.",
        },
        "storyweaver_probe": {
            "url": STORYWEAVER_QUERY_ROOT + "?query=English",
            "http_status": story_status,
            "response_sha256": sha256_bytes(story_raw) if story_raw else "",
            "error": story_error,
            "access_state": "TECHNICAL_CHALLENGE_OR_HTTP_BLOCK" if story_status != 200 or story_challenge else "ACCESSIBLE_RESPONSE_NOT_NORMALIZED",
            "interpretation": "The same public route is used for all generated cell queries. A blocked probe makes every result unresolved; it is not evidence of no stories.",
        },
    }
    write_json(SNAPSHOT_OUT, snapshot)
    return snapshot


def target_region(language_tag: str) -> str:
    for part in language_tag.split("-")[1:]:
        if re.fullmatch(r"[A-Z]{2}", part):
            return part
    return ""


def target_base_code(language_tag: str) -> str:
    return language_tag.split("-", 1)[0].casefold()


def normalized_name(value: str) -> str:
    value = html.unescape(value).casefold()
    value = value.replace("’", "'").replace("ʻ", "'").replace("`", "'")
    value = re.sub(r"\([^)]*\)", " ", value)
    value = re.sub(r"[^\w]+", " ", value, flags=re.UNICODE)
    return " ".join(value.split())


def load_targets() -> list[dict[str, Any]]:
    document = load_json(IDENTITY_INPUT)
    selected = [
        row
        for row in document.get("language_targets", [])
        if row.get("rankable_population_basis") is True
        and row.get("exactness") == "exact"
        and row.get("language_tags")
        and row.get("scripts_orthographies")
        and row.get("territories_communities")
    ]
    if len(selected) != 148:
        raise ValueError(f"expected 148 exact identity rows in the fixed audit roster, found {len(selected)}")
    rows: list[dict[str, Any]] = []
    for raw in sorted(selected, key=lambda item: str(item["language_target_id"])):
        tags = sorted({str(value) for value in raw["language_tags"] if str(value)})
        if len(tags) != 1:
            raise ValueError(f"target {raw['language_target_id']} must have one exact language tag")
        row = {
            "target_id": str(raw["language_target_id"]),
            "language_tag": tags[0],
            "language_names_json": compact_json(sorted({str(v) for v in raw["language_variety_names"] if str(v)})),
            "script_orthography_json": compact_json(sorted({str(v) for v in raw["scripts_orthographies"] if str(v)})),
            "territories_json": compact_json(sorted({str(v) for v in raw["territories_communities"] if str(v)})),
            "language_mode": str(raw.get("language_mode", "")),
            "identity_exactness": "EXACT_TARGET_IDENTITY",
            "identity_only_not_access_evidence": "1",
        }
        row["target_row_hash"] = row_hash(row, "target_row_hash")
        rows.append(row)
    return rows


def source_fingerprint(source: Mapping[str, Any]) -> str:
    fields = ("id", "url", "checked_at", "grade", "claim", "caveat")
    payload = "|".join(str(source.get(field, "")) for field in fields).encode("utf-8")
    return sha256_bytes(payload)


def build_source_registry(seed: Mapping[str, Any], snapshot: Mapping[str, Any]) -> dict[str, Any]:
    records: list[dict[str, Any]] = []
    for source in seed.get("source_registry", []):
        recomputed = source_fingerprint(source)
        if recomputed != str(source.get("record_sha256", "")).casefold():
            raise ValueError(f"seed source fingerprint mismatch: {source.get('id')}")
        record = dict(source)
        record["source_origin_class"] = "VERIFIED_INDEPENDENT_EXTERNAL"
        record["program_exclusion_status"] = "PASS_INDEPENDENT_EXTERNAL"
        record["live_byte_verified"] = False
        record["seed_record_sha256"] = record.pop("record_sha256")
        record["source_record_sha256"] = row_hash(record, "source_record_sha256")
        records.append(record)

    additions = [
        {
            "id": "GDL_API_DOC_20260901",
            "provider": "Global Digital Library",
            "url": GDL_API_DOC,
            "page_date": "current at audit",
            "checked_at": AUDIT_DATE,
            "grade": "A",
            "claim": "The official content API documents language inventory, per-language book/game endpoints, topic metadata, downloadable H5P/EPUB routes, and item-level Creative Commons license metadata.",
            "caveat": "Catalog and repository counts are not curriculum coverage; exact item, stage, subject, script, completeness, exercise, answer, accessibility, and offline behavior still require separate verification.",
            "source_origin_class": "VERIFIED_INDEPENDENT_EXTERNAL",
            "program_exclusion_status": "PASS_INDEPENDENT_EXTERNAL",
            "live_byte_verified": False,
        },
        {
            "id": "GDL_LANGUAGES_SNAPSHOT_20260901",
            "provider": "Global Digital Library",
            "url": GDL_URL,
            "page_date": "dynamic",
            "checked_at": AUDIT_DATE,
            "grade": "C",
            "claim": f"The official API returned {snapshot['gdl']['language_count']} language entries in the captured response.",
            "caveat": "A language entry and its repository count establish catalogue presence only, not exact script/territory fit or curriculum coverage.",
            "source_origin_class": "VERIFIED_INDEPENDENT_EXTERNAL",
            "program_exclusion_status": "PASS_INDEPENDENT_EXTERNAL",
            "live_byte_verified": True,
            "retrieved_file_sha256": snapshot["gdl"]["response_sha256"],
        },
        {
            "id": "ASB_HOME_CATALOG_20260901",
            "provider": "African Storybook / Saide",
            "url": ASB_URL,
            "page_date": "dynamic",
            "checked_at": AUDIT_DATE,
            "grade": "C",
            "claim": f"The captured official homepage exposed {snapshot['african_storybook']['language_count']} language filter entries and described CC BY 4.0 storybooks with download, offline reading, translation, and adaptation routes.",
            "caveat": "A language filter entry is catalogue presence only. It does not prove exact script/territory, stage-subject completeness, exercises, answers, or accessibility for an item.",
            "source_origin_class": "VERIFIED_INDEPENDENT_EXTERNAL",
            "program_exclusion_status": "PASS_INDEPENDENT_EXTERNAL",
            "live_byte_verified": True,
            "retrieved_file_sha256": snapshot["african_storybook"]["response_sha256"],
        },
        {
            "id": "STORYWEAVER_OPEN_CONTENT_20260901",
            "provider": "Pratham Books StoryWeaver",
            "url": STORYWEAVER_OPEN_URL,
            "page_date": "current at audit",
            "checked_at": AUDIT_DATE,
            "grade": "B",
            "claim": "The official open-content page states that StoryWeaver books are CC BY 4.0; readalong and video media have different CC BY-NC-ND terms.",
            "caveat": (
                "The reproducible query route returned an automated-access challenge in this run, so no target or cell result is asserted from it."
                if snapshot["storyweaver_probe"]["access_state"] == "TECHNICAL_CHALLENGE_OR_HTTP_BLOCK"
                else "The reproducible query route responded, but no exact target/script/stage/subject result was normalized from the captured response, so no cell result is asserted from it."
            ),
            "source_origin_class": "VERIFIED_INDEPENDENT_EXTERNAL",
            "program_exclusion_status": "PASS_INDEPENDENT_EXTERNAL",
            "live_byte_verified": False,
        },
        {
            "id": "PRESSBOOKS_QUERY_PROTOCOL_20260901",
            "provider": "Pressbooks",
            "url": PRESSBOOKS_GUIDE_URL,
            "page_date": "current at audit",
            "checked_at": AUDIT_DATE,
            "grade": "B",
            "claim": "The official guide documents full-text and language, subject, license, H5P, and word-count filters and shareable query URLs.",
            "caveat": "The reproducible directory query route returned a technical access failure in this run; no target count or coverage claim is inferred.",
            "source_origin_class": "VERIFIED_INDEPENDENT_EXTERNAL",
            "program_exclusion_status": "PASS_INDEPENDENT_EXTERNAL",
            "live_byte_verified": False,
        },
    ]
    for record in additions:
        record["source_record_sha256"] = row_hash(record, "source_record_sha256")
        records.append(record)
    if len({record["id"] for record in records}) != len(records):
        raise ValueError("duplicate source ids in expanded registry")
    return {
        "schema": "interlanguage/oer-gap-source-registry/2.0.0",
        "audit_date": AUDIT_DATE,
        "admission_rule": "Only independent external public sources may support access gates. Target identity inputs, user outputs, local programme artifacts, repository totals, and search-result totals are never access evidence.",
        "records": sorted(records, key=lambda record: record["id"]),
    }


def inventory_match(target: Mapping[str, str], snapshot: Mapping[str, Any], catalog_id: str) -> dict[str, Any]:
    base = target_base_code(target["language_tag"])
    names = json.loads(target["language_names_json"])
    normalized_target_names = {normalized_name(name) for name in names if normalized_name(name)}
    if catalog_id == "GDL_API":
        allowed = set(GDL_CODE_EQUIVALENTS.get(base, (base,)))
        rows = [row for row in snapshot["gdl"]["languages"] if str(row["slug"]).casefold() in allowed]
        if not rows:
            rows = [
                row
                for row in snapshot["gdl"]["languages"]
                if normalized_name(str(row["name"])) in normalized_target_names
            ]
        if rows:
            return {
                "matched": True,
                "hit_count": sum(int(row["catalogue_resource_count"]) for row in rows),
                "language_match": "EXACT_BASE_LANGUAGE_CODE_OR_NAME",
                "source_ids": ["GDL_API_DOC_20260901", "GDL_LANGUAGES_SNAPSHOT_20260901"],
                "catalog_names": [row["name"] for row in rows],
            }
        return {"matched": False, "hit_count": "", "language_match": "NO_EXACT_LANGUAGE_ENTRY_MATCH", "source_ids": ["GDL_LANGUAGES_SNAPSHOT_20260901"], "catalog_names": []}
    if catalog_id == "AFRICAN_STORYBOOK":
        rows = [
            row
            for row in snapshot["african_storybook"]["languages"]
            if normalized_name(str(row["name"])) in normalized_target_names
        ]
        if rows:
            return {
                "matched": True,
                "hit_count": "",
                "language_match": "EXACT_LANGUAGE_NAME_CATALOGUE_ENTRY",
                "source_ids": ["ASB_HOME_CATALOG_20260901"],
                "catalog_names": [row["name"] for row in rows],
            }
        return {"matched": False, "hit_count": "", "language_match": "NO_EXACT_LANGUAGE_ENTRY_MATCH", "source_ids": ["ASB_HOME_CATALOG_20260901"], "catalog_names": []}
    raise ValueError(catalog_id)


def canonical_atom_id(stage: str, subject: str) -> str:
    return f"CANON-OER-CORE-v1:{stage}:{subject}"


def matrix_row_id(target_id: str, stage: str, subject: str) -> str:
    digest = sha256_bytes(f"{target_id}|{stage}|{subject}".encode("utf-8"))[:20]
    return f"oer-cell:{digest}"


def base_matrix_row(target: Mapping[str, str], stage: tuple[str, str], subject: tuple[str, str], policy: Mapping[str, Any]) -> dict[str, str]:
    stage_id, stage_label = stage
    subject_id, subject_label = subject
    atom = canonical_atom_id(stage_id, subject_id)
    endpoint = f"endpoint:public-current-access:{target['target_id']}:{stage_id}:{subject_id}:{AUDIT_DATE}"
    return {
        "matrix_row_id": matrix_row_id(target["target_id"], stage_id, subject_id),
        "target_id": target["target_id"],
        "language_tag": target["language_tag"],
        "language_names_json": target["language_names_json"],
        "script_orthography_json": target["script_orthography_json"],
        "territories_json": target["territories_json"],
        "isced_stage": stage_id,
        "stage_label": stage_label,
        "subject_domain": subject_id,
        "subject_label": subject_label,
        "canon_id": "CANON-OER-CORE",
        "canon_version": "1.0.0",
        "canon_atom_id": atom,
        "baseline_access_endpoint_id": endpoint,
        "resource_route_id": "",
        "finding_status": "SEARCH_UNRESOLVED",
        "functional_access_grade": "F0",
        "open_adaptation_grade": "O0",
        "exact_language_variety_script_status": "UNRESOLVED",
        "free_access_status": "UNRESOLVED",
        "open_license_status": "UNRESOLVED",
        "adaptation_permission_status": "UNRESOLVED",
        "redistribution_permission_status": "UNRESOLVED",
        "completeness_status": "UNRESOLVED",
        "exercises_status": "UNRESOLVED",
        "answers_status": "UNRESOLVED",
        "download_status": "UNRESOLVED",
        "offline_status": "UNRESOLVED",
        "accessibility_status": "UNRESOLVED",
        "self_study_usability_status": "UNRESOLVED",
        "alignment_status": "UNRESOLVED",
        "technical_integrity_status": "UNRESOLVED",
        "coverage_credit_status": "UNRESOLVED_NO_EXACT_CELL_ROUTE",
        "evidence_grade": "U",
        "source_ids_json": "[]",
        "query_ids_json": "[]",
        "repository_count_used_as_coverage": "0",
        "unresolved_source_flag": "1",
        "independent_origin_status": "NOT_APPLICABLE_NO_RESOURCE_ROUTE",
        "program_exclusion_status": "PASS_NO_PROGRAM_OUTPUT_ADMITTED",
        "baseline_policy_version": str(policy["baseline_policy_version"]),
        "baseline_observation_date": str(policy["public_evidence_observation_date"]),
        "caveat": "No exact item-level route satisfying every functional-access gate is verified for this target and canon cell; missing evidence is unresolved and is not a scarcity value.",
    }


def merge_sources(row: dict[str, str], source_ids: Iterable[str]) -> None:
    existing = set(json.loads(row["source_ids_json"]))
    existing.update(source_ids)
    row["source_ids_json"] = compact_json(sorted(existing))


def apply_catalogue_presence(row: dict[str, str], gdl: Mapping[str, Any], asb: Mapping[str, Any]) -> None:
    if row["isced_stage"] not in {"E0", "E1"} or row["subject_domain"] != "LANGUAGE_LITERACY":
        return
    matches = []
    if gdl["matched"]:
        matches.append("Global Digital Library")
        merge_sources(row, gdl["source_ids"])
        row["open_license_status"] = "PLATFORM_CAPABILITY_ITEM_PENDING"
    if asb["matched"]:
        matches.append("African Storybook")
        merge_sources(row, asb["source_ids"])
        row["open_adaptation_grade"] = "O3"
        row["open_license_status"] = "PLATFORM_CAPABILITY_ITEM_PENDING"
        row["adaptation_permission_status"] = "PLATFORM_CAPABILITY_ITEM_PENDING"
        row["redistribution_permission_status"] = "PLATFORM_CAPABILITY_ITEM_PENDING"
        row["download_status"] = "PLATFORM_CAPABILITY_ITEM_PENDING"
        row["offline_status"] = "PLATFORM_CAPABILITY_ITEM_PENDING"
    if matches:
        row["functional_access_grade"] = "F1"
        row["finding_status"] = "SEARCH_UNRESOLVED"
        row["evidence_grade"] = "C"
        row["coverage_credit_status"] = "CATALOGUE_PRESENCE_NO_CURRICULUM_CREDIT"
        row["caveat"] = (
            f"Catalogue-language presence was found in {', '.join(matches)}, but exact script/territory, item identity, cell alignment, completeness, exercises, answers, accessibility, and self-study behavior remain unresolved. Repository counts are not curriculum coverage."
        )


def apply_seed_native_evidence(row: dict[str, str], seed_targets: Mapping[str, Mapping[str, Any]]) -> None:
    seed_id = SEED_TARGET_ALIASES.get(row["target_id"])
    if not seed_id or seed_id not in seed_targets:
        return
    seed = seed_targets[seed_id]
    source_ids = [str(value) for value in seed.get("source_ids", [])]
    if source_ids:
        merge_sources(row, source_ids)

    # NCERT/ePathshala supplies an exact Hindi and Urdu classes I-XII route.
    if row["target_id"] in {"lang:hi-Deva-IN", "lang:ur-Arab-IN"} and row["isced_stage"] in {"E1", "E2", "E3", "E4"} and row["subject_domain"] in {"LANGUAGE_LITERACY", "MATHEMATICS_DATA", "SCIENCE_HEALTH", "SOCIAL_CIVIC"}:
        row.update(
            {
                "resource_route_id": f"route:epathshala:{row['target_id']}:{row['isced_stage']}:{row['subject_domain']}",
                "finding_status": "RESOURCE_FOUND",
                "functional_access_grade": "F4",
                "open_adaptation_grade": "O1",
                "exact_language_variety_script_status": "VERIFIED_PASS",
                "free_access_status": "VERIFIED_PASS",
                "open_license_status": "VERIFIED_FAIL",
                "adaptation_permission_status": "VERIFIED_FAIL",
                "redistribution_permission_status": "VERIFIED_FAIL",
                "completeness_status": "PLATFORM_CAPABILITY_ITEM_PENDING",
                "exercises_status": "UNRESOLVED",
                "answers_status": "UNRESOLVED",
                "download_status": "VERIFIED_PASS",
                "offline_status": "PARTIAL",
                "accessibility_status": "UNRESOLVED",
                "self_study_usability_status": "PARTIAL",
                "alignment_status": "PLATFORM_CAPABILITY_ITEM_PENDING",
                "technical_integrity_status": "PARTIAL",
                "coverage_credit_status": "FUNCTIONAL_ROUTE_FOUND_OPEN_CAPABILITY_FAILS",
                "evidence_grade": "B",
                "unresolved_source_flag": "0",
                "independent_origin_status": "VERIFIED_INDEPENDENT_EXTERNAL",
                "caveat": "The official classes I-XII route verifies free whole-book/chapter downloads in the exact target language and script. The source states that the books are copyrighted and prohibits republication/redistribution. Cell-level item sequence, exercises, answers, assistive-technology behavior, and tested offline usability remain unresolved, so no numeric coverage fraction is derived.",
            }
        )
        merge_sources(row, ["INDIA_NCERT_TEXTBOOKS"])
        return

    # All other exact seed targets retain only the seed platform tier.  Coarse
    # target evidence is never replicated into curriculum coverage.
    if source_ids and row["functional_access_grade"] == "F0":
        row["functional_access_grade"] = "F1"
        row["evidence_grade"] = "C"
        row["coverage_credit_status"] = "PLATFORM_OR_TARGET_TIER_NO_CELL_CREDIT"
        row["caveat"] = (
            "An independent official/native platform or provider tier is linked for the exact target, but the seed evidence does not identify an exact item for this stage-subject cell. All item gates remain unresolved and no curriculum coverage is credited."
        )


def query_row(
    target: Mapping[str, str],
    matrix: Mapping[str, str],
    catalog_id: str,
    snapshot: Mapping[str, Any],
    inventory: Mapping[str, Any] | None,
    native_source_ids: tuple[str, ...],
    seed_source_urls: Mapping[str, str],
) -> dict[str, str]:
    names = json.loads(target["language_names_json"])
    language_name = names[0] if names else target["language_tag"]
    terms = {
        "language_tag": target["language_tag"],
        "language_name": language_name,
        "stage": matrix["isced_stage"],
        "stage_label": matrix["stage_label"],
        "subject": matrix["subject_domain"],
        "subject_label": matrix["subject_label"],
    }
    source_ids: list[str] = []
    hit_count: str = ""
    http_status = ""
    language_match = "UNRESOLVED"
    script_match = "UNRESOLVED"
    territory_match = "UNRESOLVED"
    stage_match = "UNRESOLVED"
    subject_match = "UNRESOLVED"
    credit = "0"
    caveat = ""

    if catalog_id == "GDL_API":
        assert inventory is not None
        base = target_base_code(target["language_tag"])
        allowed = sorted(set(GDL_CODE_EQUIVALENTS.get(base, (base,))))
        url = GDL_URL
        method = "official_language_inventory_exact_code_or_name_lookup"
        http_status = str(snapshot["gdl"]["http_status"])
        source_ids = list(inventory["source_ids"])
        language_match = str(inventory["language_match"])
        hit_count = str(inventory["hit_count"])
        if inventory["matched"]:
            status = "CATALOGUE_LANGUAGE_PRESENCE_ONLY"
            caveat = "Language inventory match only. The displayed repository count is retained as catalogue metadata and is never treated as curriculum coverage."
        else:
            status = "SEARCH_UNRESOLVED_NO_EXACT_MATCH"
            caveat = "No exact code/name entry matched the captured inventory. This bounded lookup is unresolved, not an absence claim."
        terms["accepted_catalog_codes"] = allowed
        terms["matched_catalog_names"] = inventory["catalog_names"]
    elif catalog_id == "AFRICAN_STORYBOOK":
        assert inventory is not None
        url = ASB_URL
        method = "official_homepage_language_filter_exact_name_lookup"
        http_status = str(snapshot["african_storybook"]["http_status"])
        source_ids = list(inventory["source_ids"])
        language_match = str(inventory["language_match"])
        if inventory["matched"]:
            status = "CATALOGUE_LANGUAGE_PRESENCE_ONLY"
            caveat = "Language-filter presence only; no per-cell item, script/territory, completeness, exercise, answer, or accessibility claim is inferred."
        else:
            status = "SEARCH_UNRESOLVED_NO_EXACT_MATCH"
            caveat = "No exact normalized language-name entry matched the captured filter inventory. This is unresolved, not an absence claim."
        terms["matched_catalog_names"] = inventory["catalog_names"]
    elif catalog_id == "PRESSBOOKS_DIRECTORY":
        q = f'"{language_name}" "{matrix["stage_label"]}" "{matrix["subject_label"]}"'
        url = PRESSBOOKS_QUERY_ROOT + "?q=" + urllib.parse.quote(q)
        method = "official_directory_exact_phrase_stage_subject_query"
        http_status = f"{snapshot['pressbooks_probe']['http_status']}:{snapshot['pressbooks_probe']['access_state']}"
        source_ids = ["PRESSBOOKS_QUERY_PROTOCOL_20260901", "PRESSBOOKS_GUIDE"]
        if snapshot["pressbooks_probe"]["access_state"] == "TECHNICAL_CHALLENGE_OR_HTTP_BLOCK":
            status = "SEARCH_UNRESOLVED_TECHNICAL"
            caveat = "The reproducible public query route was technically blocked in the captured probe. No count, no-result, or coverage claim is made."
        else:
            status = "SEARCH_UNRESOLVED_CELL_FIT"
            caveat = "The query route responded, but no exact target/script/stage/subject result was normalized from the captured response. No count or coverage claim is made."
    elif catalog_id == "STORYWEAVER":
        q = f'{language_name} {matrix["stage_label"]} {matrix["subject_label"]}'
        url = STORYWEAVER_QUERY_ROOT + "?query=" + urllib.parse.quote(q)
        method = "official_catalog_exact_language_stage_subject_query"
        http_status = f"{snapshot['storyweaver_probe']['http_status']}:{snapshot['storyweaver_probe']['access_state']}"
        source_ids = ["STORYWEAVER_OPEN_CONTENT_20260901"]
        if snapshot["storyweaver_probe"]["access_state"] == "TECHNICAL_CHALLENGE_OR_HTTP_BLOCK":
            status = "SEARCH_UNRESOLVED_TECHNICAL"
            caveat = "The reproducible public query route returned an automated-access challenge in the captured probe. No count, no-result, or coverage claim is made."
        else:
            status = "SEARCH_UNRESOLVED_CELL_FIT"
            caveat = "The query route responded, but no exact target/script/stage/subject result was normalized from the captured response. No count or coverage claim is made."
    elif catalog_id == "OFFICIAL_NATIVE":
        method = "territory_official_or_native_platform_exact_target_cell_lookup"
        source_ids = list(native_source_ids)
        if native_source_ids:
            url = seed_source_urls.get(native_source_ids[0], "")
            status = "SEARCH_UNRESOLVED_CELL_FIT"
            caveat = "An official territory platform was identified, but no exact item was returned solely by this uniform cell lookup. Separate source-specific evidence may verify a route; platform presence alone receives no coverage credit."
        else:
            url = ""
            status = "SEARCH_UNRESOLVED_NATIVE_LOCATOR"
            caveat = "No reproducible official/native platform locator was registered in this bounded pass. This is missing evidence, not an absence claim."
    else:
        raise ValueError(catalog_id)

    qid_seed = f"{matrix['matrix_row_id']}|{catalog_id}"
    row = {
        "query_id": f"oer-query:{sha256_bytes(qid_seed.encode('utf-8'))[:20]}",
        "matrix_row_id": matrix["matrix_row_id"],
        "target_id": target["target_id"],
        "canon_atom_id": matrix["canon_atom_id"],
        "catalog_id": catalog_id,
        "query_method": method,
        "query_url": url,
        "query_terms_json": compact_json(terms),
        "queried_at_utc": AUDITED_AT_UTC,
        "http_status": http_status,
        "query_status": status,
        "catalogue_hit_count": hit_count,
        "language_match_status": language_match,
        "script_match_status": script_match,
        "territory_match_status": territory_match,
        "stage_match_status": stage_match,
        "subject_match_status": subject_match,
        "curriculum_coverage_credit_allowed": credit,
        "source_ids_json": compact_json(sorted(source_ids)),
        "caveat": caveat,
    }
    row["query_row_hash"] = row_hash(row, "query_row_hash")
    return row


def build_rows(
    targets: list[dict[str, str]],
    seed: Mapping[str, Any],
    snapshot: Mapping[str, Any],
    policy: Mapping[str, Any],
) -> tuple[list[dict[str, str]], list[dict[str, str]], list[dict[str, str]]]:
    seed_targets = {str(row["target_id"]): row for row in seed.get("targets", [])}
    seed_source_urls = {str(row["id"]): str(row.get("url", "")) for row in seed.get("source_registry", [])}
    matrices: list[dict[str, str]] = []
    queries: list[dict[str, str]] = []
    derivations: list[dict[str, str]] = []
    exclusion_hash = sha256_file(EXCLUSION_REGISTRY)
    for target in targets:
        gdl = inventory_match(target, snapshot, "GDL_API")
        asb = inventory_match(target, snapshot, "AFRICAN_STORYBOOK")
        region = target_region(target["language_tag"])
        native_sources = TERRITORY_SOURCE_IDS.get(region, ())
        for stage in STAGES:
            for subject in SUBJECTS:
                matrix = base_matrix_row(target, stage, subject, policy)
                apply_catalogue_presence(matrix, gdl, asb)
                apply_seed_native_evidence(matrix, seed_targets)
                query_records = [
                    query_row(target, matrix, "GDL_API", snapshot, gdl, native_sources, seed_source_urls),
                    query_row(target, matrix, "AFRICAN_STORYBOOK", snapshot, asb, native_sources, seed_source_urls),
                    query_row(target, matrix, "PRESSBOOKS_DIRECTORY", snapshot, None, native_sources, seed_source_urls),
                    query_row(target, matrix, "STORYWEAVER", snapshot, None, native_sources, seed_source_urls),
                    query_row(target, matrix, "OFFICIAL_NATIVE", snapshot, None, native_sources, seed_source_urls),
                ]
                matrix["query_ids_json"] = compact_json(sorted(record["query_id"] for record in query_records))
                matrix["input_row_hash"] = row_hash(matrix, "input_row_hash")
                matrices.append(matrix)
                queries.extend(query_records)

                derivation = {
                    "derivation_row_id": f"oer-derivation:{sha256_bytes(matrix['matrix_row_id'].encode('utf-8'))[:20]}",
                    "matrix_row_id": matrix["matrix_row_id"],
                    "target_id": matrix["target_id"],
                    "canon_atom_id": matrix["canon_atom_id"],
                    "baseline_functional_route_id": matrix["resource_route_id"],
                    "baseline_access_endpoint_id": matrix["baseline_access_endpoint_id"],
                    "finding_status": matrix["finding_status"],
                    "resource_gap_low": "",
                    "resource_gap_base": "",
                    "resource_gap_high": "",
                    "derivation_status": "NOT_DERIVABLE_NO_IDENTIFIED_DENOMINATOR_OR_FRACTIONAL_COVERAGE_MODEL",
                    "unresolved_source_flag": matrix["unresolved_source_flag"],
                    "source_ids_json": matrix["source_ids_json"],
                    "evidence_matrix_row_hash": matrix["input_row_hash"],
                    "baseline_policy_version": matrix["baseline_policy_version"],
                    "baseline_observation_date": matrix["baseline_observation_date"],
                    "program_exclusion_registry_hash": exclusion_hash,
                    "program_exclusion_status": matrix["program_exclusion_status"],
                }
                derivation["derivation_row_hash"] = row_hash(derivation, "derivation_row_hash")
                derivations.append(derivation)
    return matrices, queries, derivations


def validate_documents(
    targets: list[dict[str, str]],
    source_registry: Mapping[str, Any],
    matrices: list[dict[str, str]],
    queries: list[dict[str, str]],
    derivations: list[dict[str, str]],
) -> dict[str, Any]:
    failures: list[str] = []
    source_ids = {str(row["id"]) for row in source_registry["records"]}
    target_ids = {row["target_id"] for row in targets}
    expected_cells = len(STAGES) * len(SUBJECTS)
    expected_queries = expected_cells * (len(INTERNATIONAL_CATALOGS) + 1)

    def unique(label: str, values: Iterable[str]) -> None:
        values = list(values)
        if len(values) != len(set(values)):
            failures.append(f"duplicate {label}")

    if len(targets) < 100:
        failures.append("fewer than 100 exact targets")
    if any(row["identity_exactness"] != "EXACT_TARGET_IDENTITY" for row in targets):
        failures.append("non-exact target identity admitted")
    unique("target_id", (row["target_id"] for row in targets))
    unique("target_row_hash", (row["target_row_hash"] for row in targets))
    unique("matrix_row_id", (row["matrix_row_id"] for row in matrices))
    unique("query_id", (row["query_id"] for row in queries))
    unique("derivation_row_id", (row["derivation_row_id"] for row in derivations))

    per_target_cells = Counter(row["target_id"] for row in matrices)
    per_target_queries = Counter(row["target_id"] for row in queries)
    if set(per_target_cells) != target_ids or any(count != expected_cells for count in per_target_cells.values()):
        failures.append("target-by-canon matrix is not rectangular")
    if set(per_target_queries) != target_ids or any(count != expected_queries for count in per_target_queries.values()):
        failures.append("uniform query matrix is not rectangular")
    if len(derivations) != len(matrices):
        failures.append("derivation rows do not cover every matrix row")

    query_by_id = {row["query_id"]: row for row in queries}
    derivation_by_matrix = {row["matrix_row_id"]: row for row in derivations}
    for row in matrices:
        if row["functional_access_grade"] not in F_GRADES:
            failures.append(f"invalid F grade {row['matrix_row_id']}")
        if row["open_adaptation_grade"] not in O_GRADES:
            failures.append(f"invalid O grade {row['matrix_row_id']}")
        if row["finding_status"] not in FINDING_STATUSES:
            failures.append(f"invalid finding status {row['matrix_row_id']}")
        for field in (
            "exact_language_variety_script_status",
            "free_access_status",
            "open_license_status",
            "adaptation_permission_status",
            "redistribution_permission_status",
            "completeness_status",
            "exercises_status",
            "answers_status",
            "download_status",
            "offline_status",
            "accessibility_status",
            "self_study_usability_status",
            "alignment_status",
            "technical_integrity_status",
        ):
            if row[field] not in GATE_STATUSES:
                failures.append(f"invalid gate {field} in {row['matrix_row_id']}")
        linked_sources = set(json.loads(row["source_ids_json"]))
        if not linked_sources <= source_ids:
            failures.append(f"unknown matrix source id {row['matrix_row_id']}")
        linked_queries = json.loads(row["query_ids_json"])
        if len(linked_queries) != 5 or any(query_id not in query_by_id for query_id in linked_queries):
            failures.append(f"matrix query linkage failure {row['matrix_row_id']}")
        if row["repository_count_used_as_coverage"] != "0":
            failures.append(f"repository count credited as coverage {row['matrix_row_id']}")
        if row["functional_access_grade"] == "F0" and row["unresolved_source_flag"] != "1":
            failures.append(f"F0 row not explicitly unresolved {row['matrix_row_id']}")
        if row["finding_status"] == "SEARCH_UNRESOLVED" and row["coverage_credit_status"].startswith("FUNCTIONAL_ROUTE"):
            failures.append(f"unresolved row has functional coverage credit {row['matrix_row_id']}")
        if row_hash(row, "input_row_hash") != row["input_row_hash"]:
            failures.append(f"matrix row hash mismatch {row['matrix_row_id']}")
        derivation = derivation_by_matrix.get(row["matrix_row_id"])
        if derivation is None or derivation.get("evidence_matrix_row_hash") != row["input_row_hash"]:
            failures.append(f"derivation linkage mismatch {row['matrix_row_id']}")

    for row in queries:
        if row["query_status"] not in QUERY_STATUSES:
            failures.append(f"invalid query status {row['query_id']}")
        if row["curriculum_coverage_credit_allowed"] != "0":
            failures.append(f"query row grants coverage {row['query_id']}")
        linked_sources = set(json.loads(row["source_ids_json"]))
        if not linked_sources <= source_ids:
            failures.append(f"unknown query source id {row['query_id']}")
        if row_hash(row, "query_row_hash") != row["query_row_hash"]:
            failures.append(f"query row hash mismatch {row['query_id']}")

    for row in derivations:
        if any(row[field] for field in ("resource_gap_low", "resource_gap_base", "resource_gap_high")):
            failures.append(f"unidentified resource-gap scalar emitted {row['derivation_row_id']}")
        if row_hash(row, "derivation_row_hash") != row["derivation_row_hash"]:
            failures.append(f"derivation row hash mismatch {row['derivation_row_id']}")

    forbidden_tokens = ("user-produced", "programme-produced", "local translation", "local repository")
    for source in source_registry["records"]:
        if source.get("source_origin_class") != "VERIFIED_INDEPENDENT_EXTERNAL":
            failures.append(f"non-independent source admitted: {source['id']}")
        url = str(source.get("url", "")).casefold()
        if any(token in url for token in forbidden_tokens) or "c:\\users\\" in url:
            failures.append(f"local/program source url admitted: {source['id']}")
        if row_hash(source, "source_record_sha256") != source["source_record_sha256"]:
            failures.append(f"source row hash mismatch {source['id']}")

    return {
        "schema": "interlanguage/oer-gap-expansion-validation/2.0.0",
        "audit_date": AUDIT_DATE,
        "validation_passed": not failures,
        "failures": failures,
        "counts": {
            "exact_targets": len(targets),
            "stages": len(STAGES),
            "subjects": len(SUBJECTS),
            "canon_cells_per_target": expected_cells,
            "matrix_rows": len(matrices),
            "queries_per_cell": len(INTERNATIONAL_CATALOGS) + 1,
            "query_rows": len(queries),
            "source_records": len(source_registry["records"]),
            "derivation_rows": len(derivations),
            "resource_found_rows": sum(row["finding_status"] == "RESOURCE_FOUND" for row in matrices),
            "unresolved_rows": sum(row["finding_status"] == "SEARCH_UNRESOLVED" for row in matrices),
            "f0_rows": sum(row["functional_access_grade"] == "F0" for row in matrices),
            "f1_rows": sum(row["functional_access_grade"] == "F1" for row in matrices),
            "f2_rows": sum(row["functional_access_grade"] == "F2" for row in matrices),
            "f3_rows": sum(row["functional_access_grade"] == "F3" for row in matrices),
            "f4_rows": sum(row["functional_access_grade"] == "F4" for row in matrices),
            "repository_counts_credited_as_coverage": sum(row["repository_count_used_as_coverage"] != "0" for row in matrices),
            "numeric_resource_gap_rows": sum(any(row[field] for field in ("resource_gap_low", "resource_gap_base", "resource_gap_high")) for row in derivations),
        },
        "invariants": {
            "unresolved_is_missing_not_high_scarcity": True,
            "repository_counts_are_not_curriculum_coverage": True,
            "functional_access_is_independent_of_open_adaptation": True,
            "all_access_sources_are_independent_external": True,
            "user_and_programme_outputs_excluded": True,
            "no_rankings_produced": True,
            "no_resource_gap_scalar_imputed": True,
        },
    }


def artifact_entry(path: Path, rows: int | None, sort_key: str) -> dict[str, Any]:
    return {
        "path": path.relative_to(ROOT).as_posix(),
        "bytes": path.stat().st_size,
        "sha256": sha256_file(path),
        "row_count": rows,
        "canonicalization": {
            "encoding": "UTF-8",
            "line_ending": "LF",
            "csv_delimiter": "," if path.suffix == ".csv" else None,
            "row_order": sort_key,
            "row_hash": "SHA-256 of canonical JSON object excluding the row-hash field" if rows is not None else None,
        },
    }


def build_expanded_summary(seed: Mapping[str, Any], validation: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "schema": "interlanguage/oer-scarcity-evidence/2.0.0",
        "generated_at": AUDITED_AT_UTC,
        "audit_date": AUDIT_DATE,
        "seed": {
            "schema": seed.get("schema"),
            "sha256": sha256_file(SEED_EVIDENCE),
            "purpose": "F0-F4/O0-O3 definitions and independently sourced seed observations",
        },
        "scope": {
            "ranking": False,
            "publication": False,
            "scoring": False,
            "target_count": validation["counts"]["exact_targets"],
            "matrix_row_count": validation["counts"]["matrix_rows"],
            "interpretation": "A target-by-canon evidence layer. It preserves missingness and supplies canonical pre-scorer derivation rows without inventing resource-gap scalars.",
        },
        "protocol": {
            "functional_access_scale": seed["protocol"]["functional_access_scale"],
            "adaptation_scale": seed["protocol"]["adaptation_scale"],
            "evidence_grades": seed["protocol"]["evidence_grades"],
            "required_gates": seed["protocol"]["required_gates"],
            "additional_cell_dimensions": [
                "free access",
                "open license",
                "adaptation permission",
                "redistribution permission",
                "completeness",
                "exercises",
                "answers",
                "download",
                "offline use",
                "accessibility",
                "self-study usability",
            ],
            "missingness_rule": "SEARCH_UNRESOLVED/F0 means evidence is missing. It is never converted to high scarcity, zero coverage, or a numeric resource gap.",
            "repository_rule": "Catalogue and repository counts are retained only as query metadata and never converted into curriculum coverage.",
        },
        "canon": {
            "canon_id": "CANON-OER-CORE",
            "version": "1.0.0",
            "stages": [{"id": key, "label": label} for key, label in STAGES],
            "subjects": [{"id": key, "label": label} for key, label in SUBJECTS],
            "cells_per_target": len(STAGES) * len(SUBJECTS),
        },
        "artifacts": {
            "target_roster": TARGETS_OUT.name,
            "source_registry": SOURCES_OUT.name,
            "query_manifest": QUERIES_OUT.name,
            "evidence_matrix": MATRIX_OUT.name,
            "resource_gap_derivation_inputs": DERIVATION_OUT.name,
            "canonical_manifest": MANIFEST_OUT.name,
            "validation": VALIDATION_OUT.relative_to(ROOT).as_posix(),
        },
        "validation": validation,
    }


def write_report(validation: Mapping[str, Any], snapshot: Mapping[str, Any]) -> None:
    counts = validation["counts"]
    press_state = snapshot["pressbooks_probe"]["access_state"]
    story_state = snapshot["storyweaver_probe"]["access_state"]
    text = f"""# Uniform OER gap expansion audit

Audit date: {AUDIT_DATE}

## Outcome

The audit now covers **{counts['exact_targets']} exact language/variety/script targets** under one rectangular protocol: seven E0-E6 stages by five subject domains, or **{counts['matrix_rows']} target-by-canon cells**. Every cell records functional access (F0-F4), open adaptation (O0-O3), free access, open license, adaptation and redistribution permissions, completeness, exercises, answers, download, offline use, accessibility, self-study usability, alignment, integrity, sources, and five uniform query records.

This is an evidence audit, not a ranking or score. `SEARCH_UNRESOLVED` and F0 mean missing evidence. They are never treated as high scarcity, zero coverage, or a numeric `resource_gap`.

## Uniform query protocol

Each of the {counts['matrix_rows']} cells has the same four international lookups plus one territory official/native-platform lookup ({counts['query_rows']} query records total):

1. Global Digital Library official API language-inventory lookup.
2. African Storybook official language-filter lookup.
3. Pressbooks Directory exact language + stage + subject query.
4. StoryWeaver exact language + stage + subject query.
5. An exact-target/cell lookup on a registered official or native platform for the territory, when one was identified; otherwise an explicit unresolved locator row.

The captured Global Digital Library inventory contained {snapshot['gdl']['language_count']} language entries, and African Storybook contained {snapshot['african_storybook']['language_count']} language-filter entries. Their counts are catalogue metadata only. The Pressbooks probe state was `{press_state}` and the StoryWeaver probe state was `{story_state}`. Neither route yielded a normalized exact target/script/stage/subject result, so all affected cells remain unresolved, with no no-result or absence claim.

Primary protocol sources: [Global Digital Library API]({GDL_API_DOC}), [African Storybook]({ASB_URL}), [Pressbooks Directory guide]({PRESSBOOKS_GUIDE_URL}), and [StoryWeaver open-content terms]({STORYWEAVER_OPEN_URL}).

## Cell evidence and scorer handoff

The matrix contains {counts['resource_found_rows']} independently sourced functional-route rows and {counts['unresolved_rows']} unresolved rows. A route can pass functional access while failing open adaptation; Hindi and Urdu NCERT/ePathshala cells make that separation explicit. All other coarse platform or catalogue hits remain F1 or F0 and receive no curriculum-coverage fraction.

`structured/oer_resource_gap_derivation_inputs.csv` binds every cell to an exact endpoint, the matrix row hash, the baseline policy, and the programme-exclusion registry hash. All resource-gap numeric fields are blank ({counts['numeric_resource_gap_rows']} numeric rows), because no common denominator/fractional coverage model has been established. This is deliberately compatible with the repaired scorer's canonical-byte checks while remaining fail-closed.

## Validation

- Exact targets: {counts['exact_targets']}
- Canon cells per target: {counts['canon_cells_per_target']}
- Matrix rows: {counts['matrix_rows']}
- Query rows: {counts['query_rows']}
- Independent external source records: {counts['source_records']}
- Repository counts credited as coverage: {counts['repository_counts_credited_as_coverage']}
- Numeric resource-gap rows emitted: {counts['numeric_resource_gap_rows']}
- Validation passed: **{str(validation['validation_passed']).lower()}**

The canonical manifest records UTF-8/LF serialization, byte counts, SHA-256 identities, row counts, and deterministic row ordering for every scorer-facing input.
"""
    REPORT_OUT.write_text(text, encoding="utf-8", newline="\n")


def build(refresh_catalogs: bool) -> dict[str, Any]:
    seed = load_json(SEED_EVIDENCE)
    policy = load_json(BASELINE_POLICY)
    exclusion = load_json(EXCLUSION_REGISTRY)
    if policy["baseline_policy_version"] != exclusion["baseline_policy_version"]:
        raise ValueError("baseline policy and programme-exclusion registry do not agree")
    if refresh_catalogs or not SNAPSHOT_OUT.exists():
        snapshot = refresh_catalog_snapshot()
    else:
        snapshot = load_json(SNAPSHOT_OUT)

    targets = load_targets()
    source_registry = build_source_registry(seed, snapshot)
    matrices, queries, derivations = build_rows(targets, seed, snapshot, policy)
    matrices.sort(key=lambda row: (row["target_id"], row["isced_stage"], row["subject_domain"]))
    queries.sort(key=lambda row: (row["target_id"], row["canon_atom_id"], row["catalog_id"]))
    derivations.sort(key=lambda row: (row["target_id"], row["canon_atom_id"]))

    validation = validate_documents(targets, source_registry, matrices, queries, derivations)
    if not validation["validation_passed"]:
        raise ValueError("OER gap expansion validation failed: " + "; ".join(validation["failures"][:20]))

    write_csv(TARGETS_OUT, TARGET_FIELDS, targets)
    write_json(SOURCES_OUT, source_registry)
    write_csv(QUERIES_OUT, QUERY_FIELDS, queries)
    write_csv(MATRIX_OUT, MATRIX_FIELDS, matrices)
    write_csv(DERIVATION_OUT, DERIVATION_FIELDS, derivations)
    write_json(VALIDATION_OUT, validation)
    expanded = build_expanded_summary(seed, validation)
    write_json(EXPANDED_OUT, expanded)
    write_report(validation, snapshot)

    artifacts = [
        artifact_entry(SNAPSHOT_OUT, None, "JSON keys sorted; catalogue records sorted by code/name"),
        artifact_entry(TARGETS_OUT, len(targets), "target_id"),
        artifact_entry(SOURCES_OUT, len(source_registry["records"]), "record id"),
        artifact_entry(QUERIES_OUT, len(queries), "target_id, canon_atom_id, catalog_id"),
        artifact_entry(MATRIX_OUT, len(matrices), "target_id, isced_stage, subject_domain"),
        artifact_entry(DERIVATION_OUT, len(derivations), "target_id, canon_atom_id"),
        artifact_entry(EXPANDED_OUT, None, "JSON keys sorted"),
        artifact_entry(VALIDATION_OUT, None, "JSON keys sorted"),
        artifact_entry(REPORT_OUT, None, "narrative"),
    ]
    manifest = {
        "schema": "interlanguage/oer-gap-canonical-manifest/2.0.0",
        "audit_date": AUDIT_DATE,
        "scorer_compatibility": {
            "hash_algorithm": "SHA-256",
            "resource_audit_binding": "oer_resource_gap_derivation_inputs.csv exposes baseline_functional_route_id, baseline_access_endpoint_id, resource_gap_low/base/high, finding_status, and canonical matrix-row binding",
            "fail_closed_rule": "Blank resource_gap fields are not scorer-ready and must never be coerced to zero or 0.5.",
        },
        "artifacts": artifacts,
    }
    write_json(MANIFEST_OUT, manifest)
    return validation


def check_outputs() -> dict[str, Any]:
    required = [TARGETS_OUT, SOURCES_OUT, QUERIES_OUT, MATRIX_OUT, DERIVATION_OUT, VALIDATION_OUT, EXPANDED_OUT, MANIFEST_OUT]
    missing = [str(path) for path in required if not path.exists()]
    if missing:
        raise ValueError("missing outputs: " + ", ".join(missing))
    targets = read_csv(TARGETS_OUT)
    source_registry = load_json(SOURCES_OUT)
    matrices = read_csv(MATRIX_OUT)
    queries = read_csv(QUERIES_OUT)
    derivations = read_csv(DERIVATION_OUT)
    validation = validate_documents(targets, source_registry, matrices, queries, derivations)
    if not validation["validation_passed"]:
        raise ValueError("output validation failed: " + "; ".join(validation["failures"][:20]))
    manifest = load_json(MANIFEST_OUT)
    manifest_paths = {ROOT / entry["path"]: entry for entry in manifest["artifacts"]}
    for path, entry in manifest_paths.items():
        if not path.exists() or path.stat().st_size != entry["bytes"] or sha256_file(path) != entry["sha256"]:
            raise ValueError(f"canonical manifest mismatch: {path}")
    return validation


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--refresh-catalogs", action="store_true", help="refresh bounded official catalogue snapshots")
    parser.add_argument("--check", action="store_true", help="validate emitted bytes without rewriting")
    args = parser.parse_args(argv)
    validation = check_outputs() if args.check else build(args.refresh_catalogs)
    print(json.dumps({"validation_passed": validation["validation_passed"], "counts": validation["counts"]}, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
