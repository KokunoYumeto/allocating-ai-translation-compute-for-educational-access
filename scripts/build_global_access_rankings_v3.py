#!/usr/bin/env python3
"""Build the equal-treatment global access orders (L-ID and L-M).

This is the production adapter for the research dossier.  It consumes the
normalized v3 edition authority and the already frozen evidence layers.  The
adapter deliberately keeps *need* and *translation cost* separate: no local
file, previous translation, project status, region, income, prestige, source
count, or evidence-volume field can enter either order.  Sparse population or
need evidence is represented by an explicitly named common prior and a wide
interval; it is never silently converted to zero.

The output is a model-conditional research order, not an observed claim about
who is currently comfortable reading any language.  L-ID reports transparent
partial-identification envelopes; L-M reports a common-prior posterior-style
scenario with deterministic SHA-256-addressed draws.  Both orders include all
rankable written editions in the frozen v3 authority and retain signed/oral
editions in the needs register with an explicit delivery-model status.
"""

from __future__ import annotations

import argparse
import csv
import gzip
import hashlib
import json
import math
import os
import re
import statistics
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence


SCHEMA = "interlanguage/global-access-rankings/3.0.0"
MODEL = "common-equal-treatment-l-id-l-m/3.0.0"
SEED_NAMESPACE = "global-access-rankings-v3/2026-09-01"
WORLD_POPULATION_CEILING = 8_200_000_000

REGION_TO_ISO3 = {
    "AF": "AFG", "AL": "ALB", "AM": "ARM", "AO": "AGO", "AR": "ARG",
    "AU": "AUS", "AZ": "AZE", "BD": "BGD", "BE": "BEL", "BF": "BFA",
    "BG": "BGR", "BH": "BHR", "BI": "BDI", "BJ": "BEN", "BN": "BRN",
    "BO": "BOL", "BR": "BRA", "BT": "BTN", "BW": "BWA", "BY": "BLR",
    "BZ": "BLZ", "CA": "CAN", "CD": "COD", "CF": "CAF", "CG": "COG",
    "CH": "CHE", "CI": "CIV", "CL": "CHL", "CM": "CMR", "CN": "CHN",
    "CO": "COL", "CR": "CRI", "CU": "CUB", "CV": "CPV", "CY": "CYP",
    "CZ": "CZE", "DE": "DEU", "DJ": "DJI", "DK": "DNK", "DM": "DMA",
    "DO": "DOM", "DZ": "DZA", "EC": "ECU", "EE": "EST", "EG": "EGY",
    "ER": "ERI", "ES": "ESP", "ET": "ETH", "FI": "FIN", "FJ": "FJI",
    "FM": "FSM", "FR": "FRA", "GA": "GAB", "GB": "GBR", "GD": "GRD",
    "GE": "GEO", "GH": "GHA", "GM": "GMB", "GN": "GIN", "GQ": "GNQ",
    "GR": "GRC", "GT": "GTM", "GW": "GNB", "GY": "GUY", "HN": "HND",
    "HR": "HRV", "HT": "HTI", "HU": "HUN", "ID": "IDN", "IE": "IRL",
    "IL": "ISR", "IN": "IND", "IQ": "IRQ", "IR": "IRN", "IS": "ISL",
    "IT": "ITA", "JM": "JAM", "JO": "JOR", "JP": "JPN", "KE": "KEN",
    "KG": "KGZ", "KH": "KHM", "KI": "KIR", "KM": "COM", "KN": "KNA",
    "KP": "PRK", "KR": "KOR", "KW": "KWT", "KZ": "KAZ", "LA": "LAO",
    "LB": "LBN", "LC": "LCA", "LI": "LIE", "LK": "LKA", "LR": "LBR",
    "LS": "LSO", "LT": "LTU", "LU": "LUX", "LV": "LVA", "LY": "LBY",
    "MA": "MAR", "MC": "MCO", "MD": "MDA", "ME": "MNE", "MG": "MDG",
    "MH": "MHL", "MK": "MKD", "ML": "MLI", "MM": "MMR", "MN": "MNG",
    "MR": "MRT", "MT": "MLT", "MU": "MUS", "MV": "MDV", "MW": "MWI",
    "MX": "MEX", "MY": "MYS", "MZ": "MOZ", "NA": "NAM", "NE": "NER",
    "NG": "NGA", "NI": "NIC", "NL": "NLD", "NO": "NOR", "NP": "NPL",
    "NR": "NRU", "NZ": "NZL", "OM": "OMN", "PA": "PAN", "PE": "PER",
    "PG": "PNG", "PH": "PHL", "PK": "PAK", "PL": "POL", "PS": "PSE",
    "PT": "PRT", "PW": "PLW", "PY": "PRY", "QA": "QAT", "RO": "ROU",
    "RS": "SRB", "RU": "RUS", "RW": "RWA", "SA": "SAU", "SB": "SLB",
    "SC": "SYC", "SD": "SDN", "SE": "SWE", "SG": "SGP", "SI": "SVN",
    "SK": "SVK", "SL": "SLE", "SN": "SEN", "SO": "SOM", "SR": "SUR",
    "SS": "SSD", "ST": "STP", "SV": "SLV", "SY": "SYR", "SZ": "SWZ",
    "TD": "TCD", "TG": "TGO", "TH": "THA", "TJ": "TJK", "TL": "TLS",
    "TM": "TKM", "TN": "TUN", "TO": "TON", "TR": "TUR", "TT": "TTO",
    "TV": "TUV", "TZ": "TZA", "UA": "UKR", "UG": "UGA", "US": "USA",
    "UY": "URY", "UZ": "UZB", "VA": "VAT", "VC": "VCT", "VE": "VEN",
    "VN": "VNM", "VU": "VUT", "WS": "WSM", "YE": "YEM", "ZA": "ZAF",
    "ZM": "ZMB", "ZW": "ZWE",
}

SCRIPT_FACTOR = {
    "Latn": 1.00, "Cyrl": 1.08, "Arab": 1.14, "Deva": 1.22,
    "Beng": 1.25, "Guru": 1.23, "Gujr": 1.22, "Taml": 1.24,
    "Telu": 1.25, "Knda": 1.23, "Mlym": 1.24, "Orya": 1.23,
    "Sinh": 1.21, "Thai": 1.18, "Laoo": 1.18, "Khmr": 1.23,
    "Mymr": 1.24, "Ethi": 1.20, "Geor": 1.12, "Armn": 1.13,
    "Hans": 1.45, "Hant": 1.45, "Jpan": 1.52, "Hang": 1.38,
    "Kore": 1.38, "Mong": 1.28, "Tibt": 1.28, "Cans": 1.20,
    "Cher": 1.20, "Brai": 1.30, "Zyyy": 1.25,
}

FACTOR_WEIGHTS = {
    "schooling_language_gap": 0.22,
    "learning_completion_gap": 0.20,
    "open_resource_scarcity": 0.18,
    "academic_lingua_franca_nonoverlap": 0.18,
    "delivery_gap": 0.14,
    "accessibility_gap": 0.08,
}

FORBIDDEN_INPUT_TERMS = (
    "user_local", "prior_translation", "sunk_compute", "project_convenience",
    "completion_status", "local_file_inventory", "personal_work",
)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canonical_json(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def canonical_sha(value: Any) -> str:
    return sha256_bytes(canonical_json(value))


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: Sequence[Mapping[str, Any]], fields: Sequence[str] | None = None) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if fields is None:
        fields = list(rows[0].keys()) if rows else []
    tmp = path.with_suffix(path.suffix + ".tmp")
    with tmp.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(fields), extrasaction="raise", lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fields})
    os.replace(tmp, path)


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    os.replace(tmp, path)


def parse_num(value: Any) -> float | None:
    if value is None:
        return None
    text = str(value).strip().replace(",", "")
    if not text or text.lower() in {"none", "null", "na", "n/a", "unknown"}:
        return None
    try:
        return float(text)
    except ValueError:
        return None


def json_value(value: Any, default: Any = None) -> Any:
    if isinstance(value, (list, dict)):
        return value
    text = str(value or "").strip()
    if not text:
        return default
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return default


def list_value(value: Any) -> list[str]:
    # ``json_value`` returns the supplied default on a non-JSON compact field;
    # use ``None`` so the semicolon/pipe compatibility form can actually fall
    # through to its parser.
    parsed = json_value(value, None)
    if isinstance(parsed, list):
        return [str(item) for item in parsed if str(item).strip()]
    if isinstance(value, str):
        return [part.strip() for part in re.split(r"[;|]", value) if part.strip()]
    return []


def _json_list(value: Any) -> str:
    """Project a compact v3 semicolon field into the ranker's list shape."""
    return json.dumps(list_value(value), ensure_ascii=False, separators=(",", ":"))


def normalize_authority_rows(rows: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    """Adapt the successor builder's compact table-A schema in memory.

    The v3 successor authority intentionally uses human-readable semicolon
    fields.  The ranker historically consumed the richer registry projection
    with ``*_json`` fields.  This projection only renames/serializes declared
    authority fields; it does not add scores, ranks, or model inputs.
    """
    if not rows:
        return []
    # Keep the legacy projection untouched when an older registry is supplied.
    if "normalized_language_codes_json" in rows[0]:
        return [dict(row) for row in rows]
    adapted: list[dict[str, Any]] = []
    for source in rows:
        row = dict(source)
        row.setdefault("normalized_language_codes_json", _json_list(source.get("language_tags", "")))
        row.setdefault("language_names_json", _json_list(source.get("language_variety_names", "")))
        row.setdefault("script_orthography_json", _json_list(source.get("scripts_orthographies", "")))
        row.setdefault("territory_community_json", _json_list(source.get("territories_communities", "")))
        row.setdefault("mode_json", _json_list(source.get("language_mode", "")))
        # The compact authority does not carry a separate intervention scope;
        # leave that predictor blank rather than deriving one from a label.
        row.setdefault("production_intervention_scope", "")
        row.setdefault("edition_role", source.get("target_kind", ""))
        row.setdefault("edition_derivation_class", source.get("exactness", source.get("disposition", "")))
        row.setdefault("registry_row_hash", source.get("row_sha256", ""))
        adapted.append(row)
    return adapted


def normalize_evidence_rows(rows: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    """Adapt the compact successor table-B mapping for population linkage.

    Only structural IDs used to find regional/supplement strata are projected.
    Population values in table B remain evidence-only and are not admitted as
    rank inputs by this adapter.
    """
    if not rows:
        return []
    if "normalized_edition_target_id" in rows[0]:
        return [dict(row) for row in rows]
    regional_role = "REGIONAL_EMPIRICAL_STRATUM"
    supplement_role = "LARGE_POPULATION_SUPPLEMENT"
    adapted: list[dict[str, Any]] = []
    for source in rows:
        row = dict(source)
        target_id = str(source.get("edition_target_id", "") or "")
        row.setdefault("normalized_edition_target_id", target_id)
        record_id = str(source.get("source_record_id", "") or "")
        role = str(source.get("evidence_role", "") or "")
        lane = str(source.get("source_lane", "") or "")
        if role == regional_role:
            row.setdefault("empirical_stratum_id", record_id)
        if role == supplement_role or lane == "large_population_supplement_v1":
            row.setdefault("supplement_stratum_id", record_id)
        adapted.append(row)
    return adapted


def primary_order_class(row: Mapping[str, Any]) -> tuple[str, str]:
    """Classify exact language targets versus generic format overlays.

    The frozen universe intentionally carries a few global accessibility
    requirements as reusable targets.  They remain in the census, but a
    generic "any target/all languages" row cannot be allowed to outrank an
    identifiable language community in a language-order table.
    """
    blob = text_blob(
        row.get("edition_target_id"), row.get("edition_key"),
        row.get("language_names_json"), row.get("language_variety_names"),
    )
    exactness = str(row.get("exactness", "") or "").strip().lower()
    target_kind = str(row.get("target_kind", row.get("edition_role", "")) or "").strip().lower()
    effective = str(row.get("effective_order_l_target", "true") or "true").strip().lower()
    # Unresolved identity/macro/context hypotheses are retained in the full
    # score table but cannot be treated as exact language beneficiaries.  This
    # gate is intentionally based on authority semantics, not labels or local
    # project state.
    if exactness in {"exact_name_identifier_unresolved", "unresolved_macro", "unresolved_context"}:
        return "UNRESOLVED_OR_MACRO_CONTEXT", f"authority exactness={exactness}"
    if target_kind in {"canonical_unresolved_identity", "canonical_macro_context", "canonical_unresolved_context"} or effective == "false":
        return "UNRESOLVED_OR_MACRO_CONTEXT", f"authority target_kind={target_kind or 'unknown'}"
    if (
        "unresolved-tag:any-target" in blob
        or "all-languages" in blob
        or blob.startswith("edition-target:lang:unresolved-tag:any-target")
        or "any target written language" in blob
    ):
        return "GENERIC_ACCESSIBILITY_OVERLAY", "generic any-target/all-language placeholder"
    return "LANGUAGE_OR_EXACT_INTERVENTION", "exact language/variety/script target"


def edition_id_aliases(eid: str) -> set[str]:
    """Return structural aliases for both legacy and successor v3 IDs."""
    value = str(eid or "")
    aliases = {value} if value else set()
    for prefix in (
        "edition-target:regional:", "edition-target:supplement:",
        "edition-target:", "edition:regional:", "edition:supplement:",
        "edition:",
    ):
        if value.startswith(prefix):
            aliases.add(value[len(prefix):])
    return {alias for alias in aliases if alias}


def text_blob(*values: Any) -> str:
    return " ".join(str(value or "") for value in values).lower()


def display_label(row: Mapping[str, Any], eid: str) -> str:
    """Choose one readable representative name from compact semicolon fields."""
    names = list_value(row.get("language_names_json", "[]"))
    if not names:
        return eid
    # The compact successor authority preserves alternate labels in a single
    # slash-delimited cell (for example, a canonical name followed by bridge,
    # accessibility, and project-context descriptions).  Those descriptions
    # are useful evidence fields but are not readable table labels.  Flatten
    # only for presentation; no scoring or identity field is changed.
    flattened: list[str] = []
    for name in names:
        flattened.extend(part.strip() for part in re.split(r"\s*/\s*", name) if part.strip())
    names = flattened or names
    tag = str(row.get("edition_key", "") or "").lower()
    tag_key = tag[5:] if tag.startswith("lang:") else tag
    # Stable canonical display names for the three explicitly audited large
    # cohorts.  The exact BCP-47/edition identity remains in the adjacent
    # language_tag and edition_target_id columns.
    canonical_by_tag = {
        "id-latn-id": "Bahasa Indonesia",
        "en-latn-001": "English (United States home-language cohort)",
        "zh-hans-cn:written": "Standard Written Chinese",
        "ja-jpan-jp": "Standard Japanese",
        "hi-deva-in": "Hindi",
        "bn-beng-bd": "Bangla (Bangladesh standard)",
        "bn-beng-in": "Bengali (India standard)",
        "pnb-arab-pk": "Punjabi (Pakistan standard)",
        "ta-taml-in": "Tamil (India standard)",
    }
    if tag_key in canonical_by_tag:
        return canonical_by_tag[tag_key]
    if "zh-hans" in tag:
        for name in names:
            if name.lower().startswith("standard written chinese"):
                return name
    if "ja-jpan" in tag:
        for name in names:
            if name.lower() == "standard japanese":
                return name
    if "cmn-" in tag or "cmn:" in tag:
        for name in names:
            if "putonghua" in name.lower() or "mandarin" in name.lower():
                return name
    return names[0]


def normal_from_u(u1: float, u2: float) -> float:
    u1 = max(u1, 1e-12)
    return math.sqrt(-2.0 * math.log(u1)) * math.cos(2.0 * math.pi * u2)


def stable_u(*parts: Any) -> float:
    payload = "|".join(str(part) for part in (SEED_NAMESPACE,) + parts).encode("utf-8")
    value = int.from_bytes(hashlib.sha256(payload).digest()[:8], "big")
    return (value + 0.5) / 2**64


def stable_normal(*parts: Any) -> float:
    return normal_from_u(stable_u(*parts, "u1"), stable_u(*parts, "u2"))


def clamp(value: float, low: float = 0.0, high: float = 1.0) -> float:
    return max(low, min(high, value))


def country_from_tag(tag: str, territory: str = "") -> str:
    # A valid BCP-47 region is the strongest explicit territorial signal.  It
    # must win over prose such as "Indian Tamil in Sri Lanka" or "Russian
    # mother-tongue population in Estonia", where substring matching the
    # language adjective previously assigned the wrong country.
    raw = str(tag or "").strip()
    if raw.startswith("lang:"):
        raw = raw[5:]
    if "unresolved" not in raw.lower():
        match = re.match(
            r"^[A-Za-z]{2,3}(?:-[A-Za-z]{4})?-(?P<region>[A-Za-z]{2}|[A-Za-z]{3}|\d{3})(?:-|:|$)",
            raw,
        )
        if match:
            up = match.group("region").upper()
            if up in REGION_TO_ISO3:
                return REGION_TO_ISO3[up]
            if up in set(REGION_TO_ISO3.values()):
                return up

    territory_low = str(territory or "").lower()
    names = {
        "russian federation": "RUS",
        "indonesia": "IDN", "china": "CHN", "japan": "JPN", "india": "IND",
        "bangladesh": "BGD", "pakistan": "PAK", "nigeria": "NGA", "ethiopia": "ETH",
        "tanzania": "TZA", "kenya": "KEN", "uganda": "UGA", "united states": "USA",
        "canada": "CAN", "brazil": "BRA", "mexico": "MEX", "guatemala": "GTM",
        "peru": "PER", "bolivia": "BOL", "colombia": "COL", "philippines": "PHL",
        "viet nam": "VNM", "vietnam": "VNM", "thailand": "THA", "myanmar": "MMR",
        "turkiye": "TUR", "turkey": "TUR", "iran": "IRN", "iraq": "IRQ",
        "russia": "RUS", "ukraine": "UKR", "france": "FRA", "germany": "DEU",
        "papua new guinea": "PNG", "south africa": "ZAF", "madagascar": "MDG",
    }
    for name, iso in sorted(names.items(), key=lambda item: -len(item[0])):
        if re.search(rf"(?<![a-z]){re.escape(name)}(?![a-z])", territory_low):
            return iso
    # Parse only the leading BCP-47-shaped tag.  Earlier code searched every
    # hyphen-delimited word and therefore misread ordinary prose fragments
    # such as ``...-in-peru`` as India (IN) and ``...-local-va`` as Vatican
    # City (VA).  Descriptive/unresolved slugs are never language tags.
    return ""


def script_from_row(row: Mapping[str, Any]) -> str:
    scripts = list_value(row.get("normalized_script_codes_json", "[]"))
    if len(scripts) == 1:
        return scripts[0]
    # Successor-v3 table A keeps BCP-47 tags in a compact semicolon field.
    # Prefer an explicit script subtag before textual heuristics so values such
    # as ``zh-Hans-CN`` and ``ja-Jpan-JP`` retain their declared script factor.
    for tag in list_value(row.get("normalized_language_codes_json", "")) + list_value(row.get("language_tags", "")):
        for part in re.split(r"[-_]", tag):
            if part in SCRIPT_FACTOR:
                return part
    text = text_blob(
        row.get("script_orthography_json"), row.get("scripts_orthographies"),
        row.get("language_names_json"), row.get("edition_key"), row.get("language_tags"),
    )
    for code, terms in {
        "Hans": ("simplified", "han"), "Hant": ("traditional",), "Jpan": ("japanese", "kanji"),
        "Hang": ("hangul", "korean"), "Arab": ("arabic", "perso-arabic", "ajami"),
        "Cyrl": ("cyrillic",), "Deva": ("devanagari",), "Beng": ("bengali", "bangla"),
        "Guru": ("gurmukhi",), "Thai": ("thai",), "Mymr": ("myanmar", "burmese"),
        "Ethi": ("ethiopic", "ge'ez", "geez"), "Taml": ("tamil",), "Telu": ("telugu",),
        "Latn": ("latin", "roman"),
    }.items():
        if any(term in text for term in terms):
            return code
    return "Zyyy"


def mode_from_row(row: Mapping[str, Any]) -> str:
    values = list_value(row.get("mode_json", "[]")) or list_value(row.get("language_mode", ""))
    text = text_blob(values, row.get("production_intervention_scope"), row.get("edition_role"))
    if "sign" in text or "visual" in text:
        return "signed"
    if "spoken" in text or "oral" in text or "audio" in text:
        if "writ" not in text and "text" not in text:
            return "spoken"
    if "writ" in text or "text" in text or "multimodal" in text or values:
        return "written_or_multimodal"
    return "written_or_multimodal"


def normalize_population(value: Any, unit: Any) -> float | None:
    number = parse_num(value)
    if number is None:
        return None
    unit_text = str(unit or "").lower()
    if "percent" in unit_text or "rate" in unit_text:
        return None
    if "million" in unit_text:
        number *= 1_000_000
    elif "billion" in unit_text:
        number *= 1_000_000_000
    if number < 0 or number > WORLD_POPULATION_CEILING * 1.1:
        return None
    return number


def evidence_class(text: str, eligibility: str = "") -> str:
    blob = f"{text} {eligibility}".lower()
    if any(k in blob for k in (
        "eligible_direct", "direct", "l1", "mother tongue", "mother_tongue",
        "home_language", "home_or_first_language", "first_language", "reported_ability",
        "speaker", "census", "enrolment", "enrollment",
    )):
        return "DIRECT_OR_DERIVED_PERSON_MEASURE"
    if any(k in blob for k in ("ceiling", "exposure", "territorial", "context", "official_language")):
        return "TERRITORIAL_OR_CONTEXT_CEILING"
    return "OTHER_TYPED_OR_MODEL_CONTEXT"


def language_user_measure(candidate: Mapping[str, Any]) -> bool:
    """Whether a candidate is a language-user denominator rather than a
    stage/sector opportunity count.

    Broad language editions should use speaker/ability/home-language evidence
    when it exists. Enrolment, workforce, resident, and student totals remain
    valid stage-context evidence but must not displace a language-user count or
    make a narrow cohort stand in for an entire national language.
    """
    blob = text_blob(candidate.get("measure_class"), candidate.get("eligibility"), candidate.get("definition"))
    if any(term in blob for term in (
        "enrolment", "enrollment", "student", "learner", "workforce", "resident", "school", "tertiary", "graduate",
        "support_need", "support need", "needing japanese", "need japanese instruction", "direct_language_support",
    )):
        return False
    return any(term in blob for term in (
        "speaker", "reported ability", "reported_ability", "home language", "home_language",
        "home_or_first_language", "first language", "first_language", "mother tongue",
        "mother_tongue", "l1", "language use", "knowledge of",
        # These are explicit person-language measures admitted by the
        # authorization ledger.  They were previously omitted from this
        # adapter whitelist and therefore fell through to model-prior
        # ceilings despite having source-bound point estimates.
        "first_learned", "first learned", "usual_spoken", "usual spoken",
        "nonexclusive_use", "nonexclusive use",
        "official_2000_exact_variant_estimate",
        "census_speak_or_understand_age5plus",
    ))


def candidate_from_measure(measure: Mapping[str, Any], *, source_kind: str) -> dict[str, Any] | None:
    # Keep an explicit record of whether a bound/base had to be inferred.  The
    # active successor run admits only rows whose low/base/high values are
    # source-supplied; inference remains available for legacy compatibility but
    # is never allowed to masquerade as direct evidence in the QA gate.
    # Keep the source cells separate from the arithmetic adapter.  The
    # authorization ledger repeats a POINT base only in its explicit
    # normalized_* fields; reading those fields here prevents a CSV null from
    # being mistaken for a source-supplied endpoint.
    source_low = measure.get("population_low_persons", measure.get("population_low"))
    source_base = measure.get("population_base_persons", measure.get("population_base"))
    source_high = measure.get("population_high_persons", measure.get("population_high"))
    has_explicit_normalized = any(
        key in measure for key in ("normalized_population_low_persons", "normalized_population_high_persons")
    )
    arithmetic_low = measure.get("normalized_population_low_persons") if has_explicit_normalized else source_low
    arithmetic_high = measure.get("normalized_population_high_persons") if has_explicit_normalized else source_high
    supplied_low = normalize_population(arithmetic_low, measure.get("population_unit", measure.get("source_unit_or_denominator", "")))
    supplied_base = normalize_population(source_base, measure.get("population_unit", measure.get("source_unit_or_denominator", "")))
    supplied_high = normalize_population(arithmetic_high, measure.get("population_unit", measure.get("source_unit_or_denominator", "")))
    unit = measure.get("population_unit", measure.get("source_unit_or_denominator", ""))
    low = supplied_low
    base = supplied_base
    high = supplied_high
    if low is None and base is None and high is None:
        return None
    if base is None:
        # Preserve a source-supplied interval as an interval.  Its midpoint is
        # used only as a display/model point later; it is not written back into
        # the evidence object as if the source supplied it.
        if low is None and high is not None and "ceiling" not in text_blob(measure.get("measure_class"), measure.get("population_measure_class"), measure.get("rank_eligibility")):
            base = high
    if low is None:
        low = 0.0 if high is not None and base is None else (base if base is not None else 0.0)
    if high is None:
        high = base if base is not None else WORLD_POPULATION_CEILING
    if high < low:
        low, high = high, low
    source_ids = measure.get("source_ids", measure.get("source_id", ""))
    if isinstance(source_ids, (list, tuple, set)):
        source_ids = ";".join(str(x) for x in source_ids if str(x).strip())
    source_url = measure.get("population_source_url", measure.get("evidence_url", measure.get("source_url", "")))
    eligibility = measure.get("rank_eligibility", measure.get("rankability", measure.get("rank_eligibility_source_label", "")))
    rankability_status = measure.get("population_rankability_status", measure.get("rankability_status", ""))
    target_binding = measure.get("target_binding", "")
    return {
        "low": float(low), "base": None if base is None else float(base), "high": float(high),
        "source_id": str(measure.get("population_source_id", measure.get("evidence_source_id", source_ids)) or source_ids or ""),
        "source_url": str(source_url or ""),
        "source_kind": source_kind,
        "measure_class": str(measure.get("measure_class", measure.get("population_measure_class", "")) or ""),
        "definition": str(measure.get("population_definition", measure.get("population_definition", "")) or ""),
        "year": str(measure.get("population_reference_year", measure.get("reference_year", "")) or ""),
        "eligibility": str(eligibility or ""),
        "rankability_status": str(rankability_status or ""),
        "target_binding": str(target_binding or ""),
        "overlap_group": str(measure.get("shared_denominator_group", measure.get("overlap_group", "")) or ""),
        "confidence": str(measure.get("evidence_confidence", measure.get("evidence_confidence", "")) or ""),
        # A point estimate is complete when its source base is present; an
        # interval estimate is complete when both explicit endpoints are
        # present.  Repeating a point into low/high is deterministic
        # normalization, not a hidden estimate; no midpoint is synthesized for
        # an interval.
        "bounds_source_complete": (
            str(measure.get("population_bound_type", "")).upper() in {"POINT", "INTERVAL"}
            if measure.get("population_bound_type") not in (None, "")
            else supplied_base is not None or (supplied_low is not None and supplied_high is not None)
        ),
        "bounds_were_imputed": (
            str(measure.get("population_bound_type", "")).upper() not in {"POINT", "INTERVAL"}
            if measure.get("population_bound_type") not in (None, "")
            else not (supplied_base is not None or (supplied_low is not None and supplied_high is not None))
        ),
        # These fields are populated by the authorization adapter when the
        # source row comes from EVIDENCE_AUTHORIZATION_v1.csv.  Keeping empty
        # defaults preserves compatibility with pre-authorization snapshots.
        "authorization_id": str(measure.get("authorization_id", "") or ""),
        "authorization_status": str(measure.get("authorization_status", "") or ""),
        "authorization_tier": str(measure.get("authorization_tier", "") or ""),
        "evidence_identity_id": str(measure.get("evidence_identity_id", "") or ""),
        "source_lane": str(measure.get("source_lane", "") or ""),
        "source_record_id": str(measure.get("source_record_id", "") or ""),
        "evidence_role": str(measure.get("evidence_role", "") or ""),
        "target_row_sha256": str(measure.get("target_row_sha256", "") or ""),
        "evidence_row_sha256": str(measure.get("evidence_row_sha256", "") or ""),
        "source_evidence_row_sha256": str(measure.get("source_evidence_row_sha256", "") or ""),
        "source_registry_row_hashes": str(measure.get("source_registry_row_hashes", "") or ""),
        "local_work_exclusion": str(measure.get("local_work_exclusion", "") or ""),
        "synthetic_or_model_prior": str(measure.get("synthetic_or_model_prior", "") or ""),
        "population_bound_type": str(measure.get("population_bound_type", "") or ""),
        "source_population_low_persons": "" if source_low is None else str(source_low),
        "source_population_base_persons": "" if source_base is None else str(source_base),
        "source_population_high_persons": "" if source_high is None else str(source_high),
        "normalized_population_low_persons": "" if arithmetic_low is None else str(arithmetic_low),
        "normalized_population_high_persons": "" if arithmetic_high is None else str(arithmetic_high),
    }


def parse_metric(context: Mapping[str, Any], key: str) -> float | None:
    value = context.get("metrics", {}).get(key, {})
    if isinstance(value, Mapping):
        if value.get("missing"):
            return None
        return parse_num(value.get("value"))
    return None


def load_country_context(path: Path) -> tuple[dict[str, dict[str, Any]], dict[str, Any]]:
    data = read_json(path)
    result: dict[str, dict[str, Any]] = {}
    for country in data.get("countries", []):
        code = str(country.get("country_code", "")).upper()
        if code:
            result[code] = country
    return result, data


def flatten_source_hashes(paths: Iterable[Path], root: Path | None = None) -> dict[str, dict[str, Any]]:
    out: dict[str, dict[str, Any]] = {}
    for path in paths:
        if path.is_file():
            key = str(path.relative_to(root)).replace("\\", "/") if root is not None else str(path)
            out[key] = {"bytes": path.stat().st_size, "sha256": sha256_file(path)}
    return out


def load_population_maps(root: Path, a_rows: Sequence[Mapping[str, Any]], b_rows: Sequence[Mapping[str, Any]]) -> tuple[dict[str, list[dict[str, Any]]], dict[str, str], dict[str, list[dict[str, Any]]]]:
    # The authorization ledger is the sole population input for the repaired
    # successor run.  It is derived from the successor-universe evidence and
    # records an explicit admission/exclusion decision for every candidate;
    # this prevents the legacy proposal from silently bypassing the evidence
    # mapping's provenance gate.
    authorization_path = root / "structured/EVIDENCE_AUTHORIZATION_v1.csv"
    if authorization_path.is_file():
        regional: dict[str, dict[str, Any]] = {}
        for relative in (
            "structured/ASIA_EMPIRICAL_NEED_INPUTS.csv",
            "structured/AFRICA_EMPIRICAL_NEED_INPUTS.csv",
            "structured/AMERICAS_EUROPE_EMPIRICAL_NEED_INPUTS.csv",
            "structured/OCEANIA_CENTRAL_ASIA_EMPIRICAL_INPUTS.csv",
        ):
            path = root / relative
            if path.is_file():
                for row in read_csv(path):
                    sid = str(row.get("stratum_id", ""))
                    if sid:
                        regional[sid] = row
        result: dict[str, list[dict[str, Any]]] = defaultdict(list)
        atom_hint: dict[str, str] = {}
        for row in read_csv(authorization_path):
            status = str(row.get("authorization_status", "")).strip().upper()
            if status not in {"ADMIT", "STAGE_OPPORTUNITY"}:
                continue
            eid = str(row.get("edition_target_id", "")).strip()
            if not eid:
                continue
            item = candidate_from_measure({
                "population_low": row.get("population_low_persons"),
                "population_base": row.get("population_base_persons"),
                "population_high": row.get("population_high_persons"),
                "population_low_persons": row.get("population_low_persons"),
                "population_base_persons": row.get("population_base_persons"),
                "population_high_persons": row.get("population_high_persons"),
                "population_bound_type": row.get("population_bound_type", ""),
                "normalized_population_low_persons": row.get("normalized_population_low_persons", ""),
                "normalized_population_high_persons": row.get("normalized_population_high_persons", ""),
                "population_unit": row.get("population_unit", "persons"),
                "population_source_id": row.get("source_ids", ""),
                "population_source_url": row.get("source_urls", ""),
                "measure_class": row.get("measure_class", ""),
                "population_definition": row.get("population_definition", ""),
                "population_reference_year": row.get("reference_year", ""),
                "rank_eligibility": row.get("rank_eligibility_source_label", ""),
                "population_rankability_status": row.get("population_rankability_status", ""),
                "target_binding": row.get("target_binding", ""),
                "shared_denominator_group": row.get("overlap_group", ""),
                "evidence_confidence": row.get("authorization_tier", ""),
                "authorization_id": row.get("authorization_id", ""),
                "authorization_status": status,
                "authorization_tier": row.get("authorization_tier", ""),
                "evidence_identity_id": row.get("evidence_identity_id", ""),
                "source_lane": row.get("source_lane", ""),
                "source_record_id": row.get("source_record_id", ""),
                "evidence_role": row.get("evidence_role", ""),
                "target_row_sha256": row.get("target_row_sha256", ""),
                "evidence_row_sha256": row.get("evidence_row_sha256", ""),
                "source_evidence_row_sha256": row.get("source_evidence_row_sha256", ""),
                "source_registry_row_hashes": row.get("source_registry_row_hashes", ""),
                "local_work_exclusion": row.get("local_work_exclusion", ""),
                "synthetic_or_model_prior": row.get("synthetic_or_model_prior", ""),
            }, source_kind="authorized_evidence")
            if not item:
                continue
            item["authorization_id"] = str(row.get("authorization_id", ""))
            item["authorization_status"] = status
            item["authorization_tier"] = str(row.get("authorization_tier", ""))
            item["evidence_identity_id"] = str(row.get("evidence_identity_id", ""))
            item["source_lane"] = str(row.get("source_lane", ""))
            item["source_record_id"] = str(row.get("source_record_id", ""))
            item["evidence_role"] = str(row.get("evidence_role", ""))
            item["target_row_sha256"] = str(row.get("target_row_sha256", ""))
            item["evidence_row_sha256"] = str(row.get("evidence_row_sha256", ""))
            item["source_evidence_row_sha256"] = str(row.get("source_evidence_row_sha256", ""))
            item["source_registry_row_hashes"] = str(row.get("source_registry_row_hashes", ""))
            item["local_work_exclusion"] = str(row.get("local_work_exclusion", ""))
            item["synthetic_or_model_prior"] = str(row.get("synthetic_or_model_prior", ""))
            item["regional_stratum_id"] = str(row.get("regional_stratum_id", ""))
            if item["regional_stratum_id"] and item["regional_stratum_id"] in regional:
                item["regional_row"] = regional[item["regional_stratum_id"]]
            item["atom_hint"] = str(row.get("overlap_group", "") or row.get("authorization_id", ""))
            result[eid].append(item)
        # Preserve every admitted identity for audit, but remove byte-identical
        # duplicate measurements before selecting a target denominator.
        for eid, items in list(result.items()):
            unique: dict[tuple[Any, ...], dict[str, Any]] = {}
            for item in items:
                key = (item.get("authorization_status"), item.get("source_id"), item.get("low"), item.get("base"), item.get("high"), item.get("definition"), item.get("regional_stratum_id", ""))
                unique[key] = item
            result[eid] = list(unique.values())
            if result[eid]:
                atom_hint[eid] = str(result[eid][0].get("atom_hint", ""))
        return result, atom_hint, regional

    proposal = read_json(root / "structured/canonical_universe_proposal.json")
    canonical_targets = {str(row.get("language_target_id")): row for row in proposal.get("language_targets", [])}
    measures = {str(row.get("population_measure_id")): row for row in proposal.get("population_measures", [])}
    # Load this 87-kB source once.  Re-reading it inside the target loop both
    # inflated I/O and made a deterministic run depend on filesystem timing.
    large_strata = read_json(root / "structured/large_language_population_strata_proposal.json").get("population_strata", [])
    regional: dict[str, dict[str, Any]] = {}
    for relative in (
        "structured/ASIA_EMPIRICAL_NEED_INPUTS.csv",
        "structured/AFRICA_EMPIRICAL_NEED_INPUTS.csv",
        "structured/AMERICAS_EUROPE_EMPIRICAL_NEED_INPUTS.csv",
        "structured/OCEANIA_CENTRAL_ASIA_EMPIRICAL_INPUTS.csv",
        "structured/LARGE_POPULATION_OMISSION_SUPPLEMENT_v1.csv",
    ):
        path = root / relative
        if path.is_file():
            for row in read_csv(path):
                sid = str(row.get("stratum_id", ""))
                if sid:
                    regional[sid] = row
    event_rows = read_csv(root / "structured/empirical_event_gap_ledger_v2.csv")
    events_by_target: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in event_rows:
        events_by_target[str(row.get("language_target_id", ""))].append(row)
    mapping_by_edition: dict[str, list[Mapping[str, Any]]] = defaultdict(list)
    for row in b_rows:
        edition = str(row.get("normalized_edition_target_id", ""))
        if edition:
            mapping_by_edition[edition].append(row)

    result: dict[str, list[dict[str, Any]]] = defaultdict(list)
    atom_hint: dict[str, str] = {}
    for target in a_rows:
        eid = str(target.get("edition_target_id", ""))
        if not eid:
            continue
        linked_strata: set[str] = set()
        for mapping in mapping_by_edition.get(eid, []):
            for key in ("supplement_stratum_id", "empirical_stratum_id", "intervention_target_id"):
                value = str(mapping.get(key, "") or "")
                if value:
                    linked_strata.add(value.removeprefix("intervention-target:regional-stratum:"))
            # Some mappings retain a roster ID of the form intervention-target:regional-stratum:X.
            roster = str(mapping.get("roster_target_id", "") or "")
            if "regional-stratum:" in roster:
                linked_strata.add(roster.split("regional-stratum:", 1)[1])
        aliases = edition_id_aliases(eid)
        # Canonical target and all explicitly attached population measures.
        for alias in list(aliases):
            ct = canonical_targets.get(alias) or canonical_targets.get(f"lang:{alias}")
            if ct:
                for mid in ct.get("population_measure_ids", []):
                    measure = measures.get(str(mid))
                    if measure:
                        item = candidate_from_measure(measure, source_kind="canonical_population_measure")
                        if item:
                            item["atom_hint"] = item.get("overlap_group") or str(mid)
                            result[eid].append(item)
                for event in events_by_target.get(str(ct.get("language_target_id")), []):
                    item = candidate_from_measure({
                        "population_low": event.get("population_low_persons"),
                        "population_base": event.get("population_base_persons"),
                        "population_high": event.get("population_high_persons"),
                        "population_unit": "persons",
                        "population_source_id": event.get("population_measure_id") or event.get("population_numerator_event_id"),
                        "population_source_url": "",
                        "measure_class": event.get("population_event_role"),
                        "population_definition": event.get("person_basis_status"),
                        "population_reference_year": "",
                        "rank_eligibility": event.get("person_basis_status"),
                    }, source_kind="event_ledger")
                    if item:
                        item["atom_hint"] = str(event.get("population_denominator_id") or event.get("population_measure_id") or "")
                        result[eid].append(item)
                # Link large-language strata by exact target ID.
                for stratum in large_strata:
                    if str(ct.get("language_target_id")) in [str(x) for x in stratum.get("language_target_ids", [])]:
                        item = candidate_from_measure(stratum, source_kind="large_language_stratum")
                        if item:
                            item["atom_hint"] = stratum.get("overlap_group") or stratum.get("stratum_id")
                            result[eid].append(item)
        for sid in linked_strata:
            row = regional.get(sid)
            if row:
                item = candidate_from_measure({
                    "population_low": row.get("population_low_persons"),
                    "population_base": row.get("population_base_persons"),
                    "population_high": row.get("population_high_persons"),
                    "population_unit": row.get("population_unit", "persons"),
                    "population_source_id": row.get("source_ids", row.get("evidence_source_id", "")),
                    "population_source_url": row.get("source_urls", row.get("evidence_url", "")),
                    "measure_class": row.get("population_measure_class", ""),
                    "population_definition": row.get("population_definition", ""),
                    "population_reference_year": row.get("population_reference_year", ""),
                    "rank_eligibility": row.get("population_measure_class", ""),
                    "evidence_confidence": row.get("evidence_confidence", ""),
                    "overlap_group": row.get("stratum_id", ""),
                }, source_kind="regional_empirical_bundle")
                if item:
                    item["atom_hint"] = str(row.get("stratum_id", ""))
                    item["regional_stratum_id"] = sid
                    item["regional_row"] = row
                    result[eid].append(item)
        # De-duplicate identical evidence entries.
        unique: dict[tuple[Any, ...], dict[str, Any]] = {}
        for item in result[eid]:
            key = (item["source_kind"], item["source_id"], item["low"], item["base"], item["high"], item.get("regional_stratum_id", ""))
            unique[key] = item
        result[eid] = list(unique.values())
        if result[eid]:
            atom_hint[eid] = str(result[eid][0].get("atom_hint") or "")
    return result, atom_hint, regional


def candidate_rank_class(candidate: Mapping[str, Any]) -> str | None:
    """Return an evidence-authorized rank class, or None.

    The successor evidence layer distinguishes exact point/interval person
    measures from context, exposure ceilings, enrolment stocks and unresolved
    proxies.  Only an explicit eligible_* or ADMIT_DIRECT label can authorize a
    population for the comparable primary order.  This avoids turning a
    numeric-looking ceiling or an unranked regional context into a beneficiary
    count merely because it has a large value.
    """
    eligibility = str(candidate.get("eligibility", "") or "").strip().lower()
    authorization = str(candidate.get("authorization_status", "") or "").strip().upper()
    status = str(candidate.get("rankability_status", "") or "").strip().lower()
    binding = str(candidate.get("target_binding", "") or "").strip().lower()
    measure_class = str(candidate.get("measure_class", "") or "").strip().lower()
    definition = str(candidate.get("definition", "") or "").strip().lower()
    # In the repaired successor run the explicit authorization ledger is the
    # controlling gate.  A STAGE_OPPORTUNITY row can enter only the separate
    # stage lane; an ADMIT row can enter the person lane unless its typed class
    # is itself a stage/sector opportunity.  This prevents a legacy label or a
    # model prior from silently re-authorizing a row.
    if authorization == "STAGE_OPPORTUNITY":
        if str(candidate.get("local_work_exclusion", "")).lower() != "true" or str(candidate.get("synthetic_or_model_prior", "")).lower() != "false":
            return None
        return "DIRECT_STAGE_OR_SECTOR_OPPORTUNITY_MEASURE"
    if authorization == "EXCLUDE":
        return None
    if authorization == "ADMIT" and (
        str(candidate.get("local_work_exclusion", "")).lower() != "true"
        or str(candidate.get("synthetic_or_model_prior", "")).lower() != "false"
    ):
        return None
    # The published Putonghua survey rate is not a compatible person
    # denominator: its field universe excludes most school pupils/teachers,
    # while multiplying it by the national census creates a false headcount.
    # Keep that evidence in the context/bridge register, never in the person
    # order.
    if "src_china_moe_2020" in str(candidate.get("source_id", "")).lower() or "derived ability estimate" in definition or "derived from 80.72%" in definition:
        return None
    # A country-wide adult skill estimate is a useful stage-context signal but
    # is not a Japanese-language deficit (nor an exact language-user count).
    # It is therefore kept for the stage/subject lane rather than used as the
    # population of the broad Japanese language edition.
    if "derived_adult_skill_need" in measure_class or ("all three domains" in definition and "represented adults" in definition):
        return None
    if any(term in eligibility for term in ("context_only", "not_a_direct", "shared_denominator", "keep_target_unranked", "split_required", "unranked", "missing_direct", "macrolanguage")):
        return None
    if status and status not in {"point_distribution", "interval_only"}:
        # A few exact, source-bound stage/opportunity endpoints are retained
        # with the successor universe's broader ``INSUFFICIENT_PUBLIC_EVIDENCE``
        # status because they are not whole-language denominators.  Their
        # explicit eligible_exact_stage label is sufficient for the separate
        # opportunity lane, never for the person-needs lane.
        if not (eligibility.startswith("eligible_exact_stage") and status == "insufficient_public_evidence"):
            return None
    if binding and any(term in binding for term in ("context_no_inheritance", "stage_only_no_whole_language_inheritance")):
        # Stage-only rows are admitted below only when their eligibility label
        # explicitly names an exact stage need/opportunity endpoint.
        if not ("eligible_exact_stage" in eligibility or "eligible_derived_stage" in eligibility):
            return None
    if (eligibility.startswith("admit_direct") or eligibility.startswith("eligible_direct")
            or eligibility.startswith("eligible_derived") or eligibility.startswith("eligible_exact_stage")
            or eligibility.startswith("eligible_regional_")):
        if "stage" in eligibility or "opportunity" in eligibility:
            return "DIRECT_STAGE_OR_SECTOR_OPPORTUNITY_MEASURE"
        return "DIRECT_OR_DERIVED_PERSON_MEASURE"
    # A small number of legacy regional records predate the explicit label but
    # carry a typed person measure and a source-bound base.  Admit only those
    # classes; territorial/exposure/unspecified rows remain context-only.
    if measure_class in {"reported_ability", "reported_language_ability", "daily_use", "home_language", "home_or_first_language", "l1", "speaker_estimate", "speaker_or_reported_ability", "usual_spoken", "language_knowledge"} and (candidate.get("base") is not None or candidate.get("low") is not None):
        return "DIRECT_OR_DERIVED_PERSON_MEASURE"
    return None


def choose_population(candidates: Sequence[Mapping[str, Any]], country: str, country_context: Mapping[str, Any], target_count_by_country: Mapping[str, int], eid: str) -> dict[str, Any]:
    authorized = [(c, candidate_rank_class(c)) for c in candidates]
    direct = [c for c, cls in authorized if cls == "DIRECT_OR_DERIVED_PERSON_MEASURE" and (c.get("base") is not None or c.get("low") is not None)]
    # An ADMIT receipt is the controlling semantic gate.  Re-running a loose
    # keyword classifier over its definition caused valid, already-audited
    # person-language measures to disappear whenever their caveat mentioned a
    # school, resident universe, or similar context word.  Retain the legacy
    # keyword test only for pre-authorization compatibility.
    language_direct = [
        c for c in direct
        if str(c.get("authorization_status", "")).upper() == "ADMIT"
        or language_user_measure(c)
    ]
    stage_direct = [c for c, cls in authorized if cls == "DIRECT_STAGE_OR_SECTOR_OPPORTUNITY_MEASURE" and (c.get("base") is not None or c.get("low") is not None)]
    # Context/exposure ceilings are retained in the evidence register but are
    # never point-rankable in the comparable person order.
    chosen: Mapping[str, Any] | None = None
    basis = "MODEL_CONDITIONAL_COMMON_PRIOR"
    if language_direct:
        chosen = max(language_direct, key=lambda c: float(c.get("base") if c.get("base") is not None else (c.get("high") or 0.0)))
        basis = "DIRECT_OR_DERIVED_PERSON_MEASURE"
    elif stage_direct:
        chosen = max(stage_direct, key=lambda c: float(c.get("base") if c.get("base") is not None else (c.get("high") or 0.0)))
        basis = "DIRECT_STAGE_OR_SECTOR_OPPORTUNITY_MEASURE"
    if chosen is not None:
        low = float(chosen.get("low") or 0.0)
        high = float(chosen.get("high") or chosen.get("base") or WORLD_POPULATION_CEILING)
        base = chosen.get("base")
        if high < low:
            low, high = high, low
        if high <= 0:
            high = WORLD_POPULATION_CEILING
        return {
            "population_low": low,
            "population_base": None if base is None else float(base),
            "population_high": high,
            "population_basis_class": basis,
            "population_rank_eligible": "true",
            "population_source_id": chosen.get("source_id", ""),
            "population_source_url": chosen.get("source_url", ""),
            "population_definition": chosen.get("definition", ""),
            "population_reference_year": chosen.get("year", ""),
            "population_confidence": chosen.get("confidence", ""),
            "population_atom_id": chosen.get("atom_hint", "") or f"target:{eid}",
            "population_evidence_count": len(candidates),
            "authorization_id": str(chosen.get("authorization_id", "") or ""),
            "authorization_status": str(chosen.get("authorization_status", "") or ""),
            "authorization_tier": str(chosen.get("authorization_tier", "") or ""),
            "evidence_identity_id": str(chosen.get("evidence_identity_id", "") or ""),
            "source_lane": str(chosen.get("source_lane", "") or ""),
            "source_record_id": str(chosen.get("source_record_id", "") or ""),
            "evidence_role": str(chosen.get("evidence_role", "") or ""),
            "target_row_sha256": str(chosen.get("target_row_sha256", "") or ""),
            "evidence_row_sha256": str(chosen.get("evidence_row_sha256", "") or ""),
            "source_evidence_row_sha256": str(chosen.get("source_evidence_row_sha256", "") or ""),
            "source_registry_row_hashes": str(chosen.get("source_registry_row_hashes", "") or ""),
            "local_work_exclusion": str(chosen.get("local_work_exclusion", "") or ""),
            "synthetic_or_model_prior": str(chosen.get("synthetic_or_model_prior", "") or ""),
            "bounds_source_complete": bool(chosen.get("bounds_source_complete", False)),
            "bounds_were_imputed": bool(chosen.get("bounds_were_imputed", False)),
            "population_bound_type": str(chosen.get("population_bound_type", "") or ""),
            "source_population_low_persons": str(chosen.get("source_population_low_persons", "") or ""),
            "source_population_base_persons": str(chosen.get("source_population_base_persons", "") or ""),
            "source_population_high_persons": str(chosen.get("source_population_high_persons", "") or ""),
            "normalized_population_low_persons": str(chosen.get("normalized_population_low_persons", "") or ""),
            "normalized_population_high_persons": str(chosen.get("normalized_population_high_persons", "") or ""),
            "authorization_ids": ";".join(sorted({str(c.get("authorization_id", "")) for c in direct + stage_direct if c.get("authorization_id")})),
        }
    ceiling = parse_metric(country_context, "wb_population_total") if country_context else None
    if ceiling is None:
        ceiling = WORLD_POPULATION_CEILING
        basis = "MODEL_CONDITIONAL_WORLD_CEILING"
        atom = "world:unresolved-territory"
    else:
        basis = "MODEL_CONDITIONAL_TERRITORIAL_CEILING"
        atom = f"territory:{country or 'unresolved'}"
    # A common atom allocation prevents a country ceiling from being silently
    # duplicated across many unresolved editions.  It is an uncertainty
    # assignment, not a claimed language-user count.
    count = max(1, int(target_count_by_country.get(country, 1))) if country else 1
    high = float(ceiling) / count
    return {
        "population_low": 0.0,
        "population_base": None,
        "population_high": high,
        "population_basis_class": basis,
        # A country/world ceiling without a target-bound person denominator is
        # retained as an explicit interval witness but is not allowed into the
        # needs-only order.  This prevents unknown targets from outranking
        # source-bound populations merely because a world ceiling is large.
        "population_rank_eligible": "false",
        "population_source_id": "MODEL_PRIOR_COUNTRY_CEILING",
        "population_source_url": "",
        "population_definition": "Common territorial/world ceiling prior; no language-user denominator was available.",
        "population_reference_year": "2025",
        "population_confidence": "model-conditional-wide",
        "population_atom_id": atom,
        "population_evidence_count": 0,
        "authorization_id": "",
        "authorization_status": "",
        "authorization_tier": "",
        "evidence_identity_id": "",
        "source_lane": "",
        "source_record_id": "",
        "evidence_role": "",
        "target_row_sha256": "",
        "evidence_row_sha256": "",
        "source_evidence_row_sha256": "",
        "source_registry_row_hashes": "",
        "local_work_exclusion": "",
        "synthetic_or_model_prior": "true",
        "bounds_source_complete": False,
        "bounds_were_imputed": False,
        "population_bound_type": "NONE",
        "source_population_low_persons": "",
        "source_population_base_persons": "",
        "source_population_high_persons": "",
        "normalized_population_low_persons": "",
        "normalized_population_high_persons": "",
        "authorization_ids": "",
    }


def load_oer_factors(root: Path) -> dict[str, tuple[float, str]]:
    path = root / "structured/oer_target_canon_evidence_matrix.csv"
    if not path.is_file():
        return {}
    by_target: dict[str, list[float]] = defaultdict(list)
    by_status: dict[str, list[str]] = defaultdict(list)
    for row in read_csv(path):
        target = str(row.get("target_id", ""))
        status = str(row.get("finding_status", "")).strip().upper()
        by_status[target].append(status or "UNRESOLVED")
        grade = str(row.get("functional_access_grade", ""))
        match = re.fullmatch(r"F([0-4])", grade)
        # F0/F1 in a SEARCH_UNRESOLVED row describe the current evidence
        # state of that exact search cell; they are not observed scarcity.
        # Convert grades only when every cell in the target's controlled
        # target-stage-canon sweep has an affirmative resource finding.
        if status == "RESOURCE_FOUND" and match:
            by_target[target].append(1.0 - int(match.group(1)) / 4.0)
    out: dict[str, tuple[float, str]] = {}
    for target, statuses in by_status.items():
        values = by_target.get(target, [])
        if statuses and all(status == "RESOURCE_FOUND" for status in statuses) and len(values) == len(statuses):
            out[target] = (sum(values) / len(values), "all controlled OER cells resource-found")
        elif values:
            out[target] = (0.5, "partial target-specific OER routes with unresolved cells; common prior")
        else:
            out[target] = (0.5, "unresolved OER route; common prior")
    return out


def load_academic_factors(root: Path) -> dict[str, tuple[float, str]]:
    path = root / "structured/academic_language_nonoverlap.json"
    if not path.is_file():
        return {}
    data = read_json(path)
    out: dict[str, tuple[float, str]] = {}
    for record in data.get("evidence_records", []):
        bounds = record.get("academic_nonoverlap_bounds") or {}
        vals: list[float] = []
        if isinstance(bounds, Mapping):
            for key in ("low", "base", "high"):
                value = bounds.get(key)
                if isinstance(value, (int, float)):
                    vals.append(float(value) / 100.0 if float(value) > 1 else float(value))
                elif isinstance(value, list):
                    vals.extend(float(v) / 100.0 for v in value if isinstance(v, (int, float)))
        if vals:
            value = clamp(sum(vals) / len(vals))
            status = "explicit academic-nonoverlap bound"
        else:
            value, status = 0.4, "academic nonoverlap unmeasured; common prior"
        for target in record.get("target_ids", []):
            out[str(target)] = (value, status)
    for target in data.get("leading_target_coverage", []):
        key = str(target.get("target_id", ""))
        out.setdefault(key, (0.4, "academic nonoverlap unmeasured; common prior"))
    return out


def load_compute_costs(root: Path) -> tuple[dict[str, float], str, dict[str, Any]]:
    # Prefer the v3 complete model, then the legacy complete model only as a
    # model-conditional fallback.  No population/need fields are read.
    for relative in (
        "structured/complete_edition_compute_summaries_v3.csv",
        "structured/complete_roster_compute_summaries.csv",
    ):
        path = root / relative
        if not path.is_file():
            continue
        rows = read_csv(path)
        by_target: dict[str, list[float]] = defaultdict(list)
        for row in rows:
            value = parse_num(row.get("standard_compute_p50_fecu", row.get("standard_compute_base_fecu")))
            target = str(row.get("edition_target_id", ""))
            if target and value is not None and value > 0:
                by_target[target].append(value)
        if by_target:
            return {target: statistics.median(values) for target, values in by_target.items()}, "COMPLETE_MODEL_CONDITIONAL", {"path": str(path), "sha256": sha256_file(path)}
    return {}, "SCRIPT_ENVELOPE_FALLBACK", {}


def target_aliases(eid: str, a_row: Mapping[str, Any]) -> set[str]:
    aliases = edition_id_aliases(eid)
    for key in (
        "canonical_target_id", "edition_key", "normalized_language_codes_json",
        "language_tags", "language_names_json",
    ):
        for value in list_value(a_row.get(key, "[]")):
            aliases.add(value)
    return aliases


def factor_bundle(eid: str, a_row: Mapping[str, Any], candidates: Sequence[Mapping[str, Any]], regional: Mapping[str, Mapping[str, Any]], country_data: Mapping[str, Mapping[str, Any]], oer: Mapping[str, tuple[float, str]], academic: Mapping[str, tuple[float, str]], aliases: set[str]) -> dict[str, Any]:
    tag_values = list_value(a_row.get("normalized_language_codes_json", "[]"))
    tag = tag_values[0] if tag_values else str(a_row.get("edition_key", ""))
    is_exact_target = str(a_row.get("effective_order_l_target", "")).lower() == "true"
    country = country_from_tag(tag, text_blob(a_row.get("territory_community_json"), a_row.get("language_names_json"))) if is_exact_target else ""
    context = country_data.get(country, {})
    learning_values = [parse_metric(context, key) for key in ("learning_poverty_pct", "primary_noncompletion_pct", "lower_secondary_noncompletion_pct", "upper_secondary_noncompletion_pct", "adult_basic_literacy_gap_pct")]
    learning_values = [v for v in learning_values if v is not None]
    learning = clamp(sum(learning_values) / (100.0 * len(learning_values))) if learning_values else 0.35
    internet_gap = parse_metric(context, "recent_internet_nonuse_pct")
    electricity_gap = parse_metric(context, "electricity_access_gap_pct")
    delivery_values = [v for v in (internet_gap, electricity_gap) if v is not None]
    delivery = clamp(sum(delivery_values) / (100.0 * len(delivery_values))) if delivery_values else 0.5
    blob = text_blob(a_row.get("production_intervention_scope"), a_row.get("edition_key"), a_row.get("language_names_json"))
    for item in candidates:
        row = item.get("regional_row")
        if row:
            blob += " " + text_blob(row.get("education_language_exposure_mismatch_by_stage"), row.get("learning_completion_evidence"), row.get("academic_lingua_franca_nonoverlap"), row.get("accessible_offline_delivery_evidence"))
    mismatch = 0.4
    mismatch_basis = "UNESCO/World-Bank global alignment prior"
    if "english-medium" in blob or "language mismatch" in blob or "transition" in blob or "nonoverlap" in blob:
        mismatch, mismatch_basis = 0.6, "explicit schooling-language transition context; no language-specific rate"
    if any("direct_need" in str(item.get("measure_class", "")).lower() or "direct_language_support" in str(item.get("measure_class", "")).lower() for item in candidates):
        mismatch, mismatch_basis = 0.8, "direct support-need cohort context"
    resource_value, resource_basis = 0.5, "OER route unresolved; common prior"
    for alias in aliases | {tag, f"lang:{tag}"}:
        if alias in oer:
            resource_value, resource_basis = oer[alias]
            break
    academic_value, academic_basis = 0.4, "academic-language overlap unmeasured; common prior"
    for alias in aliases | {tag, tag.split("-", 1)[0], f"lang:{tag}"}:
        if alias in academic:
            academic_value, academic_basis = academic[alias]
            break
    accessibility = 0.5
    mode = mode_from_row(a_row)
    if mode == "signed":
        accessibility = 0.8
    factors = {
        "schooling_language_gap": mismatch,
        "learning_completion_gap": learning,
        "open_resource_scarcity": resource_value,
        "academic_lingua_franca_nonoverlap": academic_value,
        "delivery_gap": delivery,
        "accessibility_gap": accessibility,
    }
    need_index = sum(FACTOR_WEIGHTS[key] * factors[key] for key in FACTOR_WEIGHTS)
    missing_count = sum(1 for basis in (mismatch_basis, resource_basis, academic_basis) if "prior" in basis or "unmeasured" in basis)
    uncertainty = 0.12 if missing_count == 0 else (0.22 if missing_count == 1 else 0.32)
    return {
        "country_iso3": country,
        "country_name": context.get("country_name", "") if context else "",
        "factors": factors,
        "factor_bases": {
            "schooling_language_gap": mismatch_basis,
            "learning_completion_gap": "ECOLOGICAL_COUNTRY_CONTEXT_PROXY: mean of available country indicators; not target-stage cross-tab" if learning_values else "common prior",
            "open_resource_scarcity": resource_basis,
            "academic_lingua_franca_nonoverlap": academic_basis,
            "delivery_gap": "ECOLOGICAL_COUNTRY_CONTEXT_PROXY: mean of country internet/electricity indicators; not language/device cross-tab" if delivery_values else "common prior",
            "accessibility_gap": "common format-access prior; signed mode elevated for delivery-model planning" if mode == "signed" else "common format-access prior",
        },
        "need_index": need_index,
        "need_low": clamp(need_index - uncertainty),
        "need_high": clamp(need_index + uncertainty),
        "need_uncertainty_width": uncertainty,
        "mode": mode,
        "script": script_from_row(a_row),
    }


def draw_population(pop: Mapping[str, Any], target: str, draw_id: int) -> float:
    low = float(pop["population_low"])
    high = float(pop["population_high"])
    base = pop.get("population_base")
    if base is None:
        return low + (high - low) * stable_u(target, "population", draw_id)
    base = float(base)
    if high <= low:
        return max(1.0, base)
    u = stable_u(target, "population-triangle", draw_id)
    if u < (base - low) / max(high - low, 1e-12):
        return low + math.sqrt(u * (base - low) * (high - low))
    return high - math.sqrt((1.0 - u) * (high - base) * (high - low))


def draw_factor(mean: float, width: float, target: str, factor: str, draw_id: int) -> float:
    # Width is a common uncertainty rule, not a target-specific penalty.
    sd = max(0.035, width / 1.96)
    value = mean + sd * stable_normal(target, factor, draw_id)
    return clamp(value)


def quantile(values: Sequence[float], q: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    position = (len(ordered) - 1) * q
    lo = int(math.floor(position))
    hi = int(math.ceil(position))
    if lo == hi:
        return float(ordered[lo])
    return float(ordered[lo] + (ordered[hi] - ordered[lo]) * (position - lo))


def spearman(a: Sequence[float], b: Sequence[float]) -> float:
    if len(a) != len(b) or not a:
        return 0.0
    def ranks(values: Sequence[float]) -> list[float]:
        order = sorted(range(len(values)), key=lambda i: (values[i], i))
        out = [0.0] * len(values)
        for rank, idx in enumerate(order, start=1):
            out[idx] = float(rank)
        return out
    ra, rb = ranks(a), ranks(b)
    ma, mb = statistics.mean(ra), statistics.mean(rb)
    da = [x - ma for x in ra]
    db = [x - mb for x in rb]
    den = math.sqrt(sum(x * x for x in da) * sum(x * x for x in db))
    return sum(x * y for x, y in zip(da, db)) / den if den else 1.0


def provenance_columns(rec: Mapping[str, Any]) -> dict[str, Any]:
    """Project population authorization provenance into every derived table."""
    return {
        "authorization_id": rec.get("authorization_id", ""),
        "authorization_ids": rec.get("authorization_ids", ""),
        "authorization_status": rec.get("authorization_status", ""),
        "authorization_tier": rec.get("authorization_tier", ""),
        "evidence_identity_id": rec.get("evidence_identity_id", ""),
        "source_lane": rec.get("source_lane", ""),
        "source_record_id": rec.get("source_record_id", ""),
        "evidence_role": rec.get("evidence_role", ""),
        "target_row_sha256": rec.get("target_row_sha256", ""),
        "evidence_row_sha256": rec.get("evidence_row_sha256", ""),
        "source_evidence_row_sha256": rec.get("source_evidence_row_sha256", ""),
        "source_registry_row_hashes": rec.get("source_registry_row_hashes", ""),
        "evidence_bounds_source_complete": rec.get("bounds_source_complete", ""),
        "evidence_bounds_were_imputed": rec.get("bounds_were_imputed", ""),
        "population_bound_type": rec.get("population_bound_type", ""),
        "source_population_low_persons": rec.get("source_population_low_persons", ""),
        "source_population_base_persons": rec.get("source_population_base_persons", ""),
        "source_population_high_persons": rec.get("source_population_high_persons", ""),
        "normalized_population_low_persons": rec.get("normalized_population_low_persons", ""),
        "normalized_population_high_persons": rec.get("normalized_population_high_persons", ""),
        "local_work_exclusion": rec.get("local_work_exclusion", ""),
        "synthetic_or_model_prior": rec.get("synthetic_or_model_prior", ""),
    }


def build(root: Path, draws: int = 256) -> dict[str, Any]:
    # The successor-edition builder's compact authority is the canonical v3
    # input.  Keep the legacy names as a read-only fallback for older frozen
    # runs, so this adapter remains reproducible across both revisions.
    successor_a = root / "structured/SUCCESSOR_EDITION_TARGET_AUTHORITY_v3.csv"
    successor_b = root / "structured/SUCCESSOR_EDITION_EVIDENCE_MAPPING_v3.csv"
    legacy_a = root / "structured/SUCCESSOR_EDITION_TARGET_REGISTRY_v3.csv"
    legacy_b = root / "structured/SUCCESSOR_EVIDENCE_IDENTITY_TO_EDITION_v3.csv"
    if successor_a.is_file() and successor_b.is_file():
        a_path, b_path = successor_a, successor_b
    elif legacy_a.is_file() and legacy_b.is_file():
        a_path, b_path = legacy_a, legacy_b
    else:
        raise RuntimeError("v3 edition authority is not present; expected a complete successor authority/mapping or legacy registry pair")
    a_rows = normalize_authority_rows(read_csv(a_path))
    b_rows = normalize_evidence_rows(read_csv(b_path))
    if not a_rows:
        raise RuntimeError("empty v3 edition authority")
    authorization_path = root / "structured/EVIDENCE_AUTHORIZATION_v1.csv"
    authorization_rows = read_csv(authorization_path) if authorization_path.is_file() else []
    authorization_by_id = {
        str(row.get("authorization_id", "")): row
        for row in authorization_rows
        if str(row.get("authorization_id", "")).strip()
    }
    authorization_counts = Counter(str(row.get("authorization_status", "")).strip().upper() for row in authorization_rows)
    # A from-scratch successor run must not silently fall back to the legacy
    # proposal.  The authorization file is the explicit source/identity gate;
    # without it, this adapter cannot make an evidence-backed order.
    if not authorization_rows:
        raise RuntimeError("EVIDENCE_AUTHORIZATION_v1.csv is required for the successor ranking run")
    edition_ids = [str(row.get("edition_target_id", "")) for row in a_rows]
    if len(edition_ids) != len(set(edition_ids)) or any(not x for x in edition_ids):
        raise RuntimeError("edition authority IDs are empty or duplicated")
    if any(any(term in json.dumps(row, ensure_ascii=False).lower() for term in FORBIDDEN_INPUT_TERMS) for row in a_rows):
        raise RuntimeError("forbidden local/project predictor leaked into edition authority")
    country_data, country_payload = load_country_context(root / "structured/major_country_context.json")
    population_maps, atom_hints, regional = load_population_maps(root, a_rows, b_rows)
    oer = load_oer_factors(root)
    academic = load_academic_factors(root)
    compute_costs, compute_class, compute_meta = load_compute_costs(root)
    target_count_by_country: Counter[str] = Counter()
    for row in a_rows:
        tags = list_value(row.get("normalized_language_codes_json", "[]"))
        target_count_by_country[country_from_tag(tags[0] if tags else row.get("edition_key", ""), text_blob(row.get("territory_community_json")))] += 1
    records: list[dict[str, Any]] = []
    for row in sorted(a_rows, key=lambda item: str(item.get("edition_target_id", ""))):
        eid = str(row["edition_target_id"])
        aliases = target_aliases(eid, row)
        tags = list_value(row.get("normalized_language_codes_json", "[]"))
        tag = tags[0] if tags else str(row.get("edition_key", ""))
        country = country_from_tag(tag, text_blob(row.get("territory_community_json")))
        pop = choose_population(population_maps.get(eid, []), country, country_data.get(country, {}), target_count_by_country, eid)
        factors = factor_bundle(eid, row, population_maps.get(eid, []), regional, country_data, oer, academic, aliases)
        order_class, order_reason = primary_order_class(row)
        cost = compute_costs.get(eid)
        if cost is None:
            cost = 1_000_000.0 * SCRIPT_FACTOR.get(factors["script"], 1.25)
            if factors["mode"] == "signed":
                cost *= 1.25
            cost_class = "MODEL_CONDITIONAL_SCRIPT_ENVELOPE"
        else:
            cost_class = compute_class
        need_base = factors["need_index"]
        need_low = factors["need_low"]
        need_high = factors["need_high"]
        n_base = pop.get("population_base")
        if n_base is None:
            n_point = (float(pop["population_low"]) + float(pop["population_high"])) / 2.0
        else:
            n_point = float(n_base)
        # A language-shaped target is not rankable merely because the roster
        # calls it an exact intervention.  The comparable person order also
        # requires a source-bound person denominator.  Keep unresolved
        # territorial/model ceilings visible, but mark them explicitly
        # unranked so downstream readers cannot mistake ``effective`` roster
        # membership for empirical eligibility.
        primary_eligible = (
            order_class == "LANGUAGE_OR_EXACT_INTERVENTION"
            and str(pop.get("population_rank_eligible", "false")).lower() == "true"
        )
        if primary_eligible:
            primary_reason = ""
        elif order_class == "LANGUAGE_OR_EXACT_INTERVENTION" and str(pop.get("population_rank_eligible", "false")).lower() != "true":
            primary_reason = "UNRANKED_NO_SOURCE_BOUND_PERSON_DENOMINATOR"
        else:
            primary_reason = order_reason
        records.append({
            "edition_target_id": eid,
            "edition_key": str(row.get("edition_key", "")),
            "edition_role": str(row.get("edition_role", "")),
            "edition_derivation_class": str(row.get("edition_derivation_class", "")),
            "label": display_label(row, eid),
            "language_tag": tag,
            "script": factors["script"],
            "mode": factors["mode"],
            "territory_community": " / ".join(list_value(row.get("territory_community_json", "[]"))),
            "country_iso3": factors["country_iso3"],
            "population_low": f"{pop['population_low']:.6f}",
            "population_base": "" if pop.get("population_base") is None else f"{float(pop['population_base']):.6f}",
            "population_high": f"{pop['population_high']:.6f}",
            "population_point_for_model": f"{n_point:.6f}",
            "population_basis_class": pop["population_basis_class"],
            "order_lane": (
                "person_need" if pop["population_basis_class"] == "DIRECT_OR_DERIVED_PERSON_MEASURE"
                else ("stage_opportunity" if pop["population_basis_class"] == "DIRECT_STAGE_OR_SECTOR_OPPORTUNITY_MEASURE" else "unranked_context")
            ),
            "population_rank_eligible": pop["population_rank_eligible"],
            "primary_order_eligible": "true" if primary_eligible else "false",
            "primary_order_class": order_class,
            "primary_order_exclusion_reason": primary_reason,
            "population_source_id": pop["population_source_id"],
            "population_source_url": pop["population_source_url"],
            "population_definition": pop["population_definition"],
            "population_reference_year": pop["population_reference_year"],
            "population_confidence": pop["population_confidence"],
            "population_atom_id": pop["population_atom_id"],
            "population_evidence_count": pop["population_evidence_count"],
            "authorization_id": pop.get("authorization_id", ""),
            "authorization_ids": pop.get("authorization_ids", ""),
            "authorization_status": pop.get("authorization_status", ""),
            "authorization_tier": pop.get("authorization_tier", ""),
            "evidence_identity_id": pop.get("evidence_identity_id", ""),
            "source_lane": pop.get("source_lane", ""),
            "source_record_id": pop.get("source_record_id", ""),
            "evidence_role": pop.get("evidence_role", ""),
            "target_row_sha256": pop.get("target_row_sha256", ""),
            "evidence_row_sha256": pop.get("evidence_row_sha256", ""),
            "source_evidence_row_sha256": pop.get("source_evidence_row_sha256", ""),
            "source_registry_row_hashes": pop.get("source_registry_row_hashes", ""),
            "local_work_exclusion": pop.get("local_work_exclusion", ""),
            "synthetic_or_model_prior": pop.get("synthetic_or_model_prior", ""),
            "bounds_source_complete": str(bool(pop.get("bounds_source_complete", False))).lower(),
            "bounds_were_imputed": str(bool(pop.get("bounds_were_imputed", False))).lower(),
            "population_bound_type": pop.get("population_bound_type", ""),
            "source_population_low_persons": pop.get("source_population_low_persons", ""),
            "source_population_base_persons": pop.get("source_population_base_persons", ""),
            "source_population_high_persons": pop.get("source_population_high_persons", ""),
            "normalized_population_low_persons": pop.get("normalized_population_low_persons", ""),
            "normalized_population_high_persons": pop.get("normalized_population_high_persons", ""),
            "schooling_language_gap": f"{factors['factors']['schooling_language_gap']:.8f}",
            "learning_completion_gap": f"{factors['factors']['learning_completion_gap']:.8f}",
            "open_resource_scarcity": f"{factors['factors']['open_resource_scarcity']:.8f}",
            "academic_lingua_franca_nonoverlap": f"{factors['factors']['academic_lingua_franca_nonoverlap']:.8f}",
            "delivery_gap": f"{factors['factors']['delivery_gap']:.8f}",
            "accessibility_gap": f"{factors['factors']['accessibility_gap']:.8f}",
            "need_index": f"{need_base:.8f}",
            "need_index_low": f"{need_low:.8f}",
            "need_index_high": f"{need_high:.8f}",
            "intrinsic_need_low": f"{float(pop['population_low']) * need_low:.6f}",
            "intrinsic_need_model": f"{n_point * need_base:.6f}",
            "intrinsic_need_high": f"{float(pop['population_high']) * need_high:.6f}",
            "standard_compute_p50_fecu": f"{cost:.6f}",
            "compute_evidence_class": cost_class,
            "need_evidence_basis": json.dumps(factors["factor_bases"], ensure_ascii=False, sort_keys=True),
            "vitality_marginalization_status": "SEPARATE_DESCRIPTIVE_FIELD_NOT_IN_PRIMARY_SCORE",
            "dialect_risk_status": "SEPARATE_DESCRIPTIVE_FIELD_NOT_IN_PRIMARY_SCORE",
            "production_feasibility_status": "SEPARATE_DESCRIPTIVE_FIELD_NOT_IN_PRIMARY_SCORE",
            "model_conditioning_status": "L-M_COMMON_PRIOR; not an observed comfortable-reader count",
            "registry_row_hash": str(row.get("registry_row_hash", "")),
        })

    # Draws and summaries.  Every target receives the same factor weights and
    # the same missingness rule; only declared evidence values change inputs.
    draw_rows: list[dict[str, Any]] = []
    draw_need_by_target: dict[str, list[float]] = {}
    draw_efficiency_by_target: dict[str, list[float]] = {}
    summaries: list[dict[str, Any]] = []
    for rec in records:
        eid = rec["edition_target_id"]
        if rec.get("population_rank_eligible") != "true" or rec.get("primary_order_eligible") != "true":
            # Keep the target and its source/ceiling bounds in the score table,
            # but do not manufacture a need value from an unresolved person
            # denominator.  It is explicitly visible and auditable below.
            rec.update({
                "intrinsic_need_low": "", "intrinsic_need_model": "", "intrinsic_need_high": "",
                "l_m_need_p05": "", "l_m_need_median": "", "l_m_need_mean": "", "l_m_need_p95": "",
                "l_m_efficiency_p05": "", "l_m_efficiency_median": "", "l_m_efficiency_mean": "", "l_m_efficiency_p95": "",
                "draw_count": 0,
                "l_id_possible_rank_best": "", "l_id_possible_rank_worst": "",
                "l_id_top10_status": "UNRANKED_PRIMARY_ORDER_GATE",
                "l_id_top100_status": "UNRANKED_PRIMARY_ORDER_GATE",
                "l_m_need_rank": "", "l_m_need_top10_probability": "", "l_m_need_top100_probability": "",
                "l_m_efficiency_rank": "",
            })
            summaries.append(rec)
            continue
        need_values: list[float] = []
        efficiency_values: list[float] = []
        cost = float(rec["standard_compute_p50_fecu"])
        factor_means = {key: float(rec[key]) for key in FACTOR_WEIGHTS}
        uncertainty = float(rec["need_index_high"]) - float(rec["need_index"])
        for draw_id in range(draws):
            n = draw_population({
                "population_low": float(rec["population_low"]),
                "population_base": parse_num(rec["population_base"]),
                "population_high": float(rec["population_high"]),
            }, eid, draw_id)
            factors_drawn = {key: draw_factor(value, uncertainty, eid, key, draw_id) for key, value in factor_means.items()}
            theta = sum(FACTOR_WEIGHTS[key] * factors_drawn[key] for key in FACTOR_WEIGHTS)
            need = n * theta
            efficiency = need / max(cost, 1e-9)
            need_values.append(need)
            efficiency_values.append(efficiency)
            if draw_id < min(draws, 256):
                draw_rows.append({
                    "edition_target_id": eid,
                    "order_lane": rec.get("order_lane", ""),
                    "draw_id": draw_id,
                    "population_draw": f"{n:.6f}",
                    "need_index_draw": f"{theta:.10f}",
                    "intrinsic_need_draw": f"{need:.6f}",
                    "standard_compute_p50_fecu": f"{cost:.6f}",
                    "access_gain_per_compute_draw": f"{efficiency:.12f}",
                    "prior_family": "reference_common",
                    "draw_semantics": "common-prior-model-conditional",
                })
        draw_need_by_target[eid] = need_values
        draw_efficiency_by_target[eid] = efficiency_values
        rec.update({
            "l_m_need_p05": f"{quantile(need_values, 0.05):.6f}",
            "l_m_need_median": f"{quantile(need_values, 0.50):.6f}",
            "l_m_need_mean": f"{statistics.mean(need_values):.6f}",
            "l_m_need_p95": f"{quantile(need_values, 0.95):.6f}",
            "l_m_efficiency_p05": f"{quantile(efficiency_values, 0.05):.12f}",
            "l_m_efficiency_median": f"{quantile(efficiency_values, 0.50):.12f}",
            "l_m_efficiency_mean": f"{statistics.mean(efficiency_values):.12f}",
            "l_m_efficiency_p95": f"{quantile(efficiency_values, 0.95):.12f}",
            "draw_count": draws,
        })
        summaries.append(rec)

    # Stage-opportunity rows are model-scored but intentionally not part of
    # the person-need order.  Give every non-person row explicit empty L-ID /
    # rank fields so the full-roster tables remain rectangular and set-equal.
    for rec in summaries:
        rec.setdefault("l_id_possible_rank_best", "")
        rec.setdefault("l_id_possible_rank_worst", "")
        rec.setdefault("l_id_top10_status", "STAGE_OPPORTUNITY_SEPARATE_ORDER" if rec.get("order_lane") == "stage_opportunity" else "UNRANKED_PRIMARY_ORDER_GATE")
        rec.setdefault("l_id_top100_status", "STAGE_OPPORTUNITY_SEPARATE_ORDER" if rec.get("order_lane") == "stage_opportunity" else "UNRANKED_PRIMARY_ORDER_GATE")
        rec.setdefault("l_m_need_rank", "")
        rec.setdefault("l_m_need_top10_probability", "")
        rec.setdefault("l_m_need_top100_probability", "")
        rec.setdefault("l_m_efficiency_rank", "")

    # The needs-only language order is restricted to source-bound person
    # measures.  Exact stage/enrolment opportunities are valuable, but they
    # are a different estimand and receive a separate opportunity order rather
    # than being mixed into a person-count ranking.
    rankable_summaries = [
        rec for rec in summaries
        if rec.get("population_rank_eligible") == "true"
        and rec.get("primary_order_eligible") == "true"
        and rec.get("order_lane") == "person_need"
    ]
    stage_summaries = [
        rec for rec in summaries
        if rec.get("population_rank_eligible") == "true"
        and rec.get("primary_order_eligible") == "true"
        and rec.get("order_lane") == "stage_opportunity"
    ]
    unranked_summaries = [rec for rec in summaries if rec not in rankable_summaries and rec not in stage_summaries]

    # L-ID rank envelopes over source-bound person/territory evidence only.
    # Unresolved targets remain in every full table with an explicit status.
    for rec in rankable_summaries:
        low = float(rec["intrinsic_need_low"])
        high = float(rec["intrinsic_need_high"])
        rec["l_id_possible_rank_best"] = 1 + sum(float(other["intrinsic_need_low"]) > high for other in rankable_summaries if other is not rec)
        rec["l_id_possible_rank_worst"] = len(rankable_summaries) - sum(float(other["intrinsic_need_high"]) < low for other in rankable_summaries if other is not rec)
        rec["l_id_top10_status"] = "DEFINITE" if rec["l_id_possible_rank_worst"] <= 10 else ("POSSIBLE" if rec["l_id_possible_rank_best"] <= 10 else "OUTSIDE")
        rec["l_id_top100_status"] = "DEFINITE" if rec["l_id_possible_rank_worst"] <= 100 else ("POSSIBLE" if rec["l_id_possible_rank_best"] <= 100 else "OUTSIDE")

    # Draw-level inclusion probabilities: rank every target jointly within
    # each common draw.  The earlier deterministic 0/1 flags were only rank
    # position indicators and overstated certainty at boundaries.
    top10_counts: Counter[str] = Counter()
    top100_counts: Counter[str] = Counter()
    for draw_id in range(draws):
        draw_order = sorted(
            ((rec["edition_target_id"], draw_need_by_target[rec["edition_target_id"]][draw_id]) for rec in rankable_summaries),
            key=lambda pair: (-pair[1], pair[0]),
        )
        for eid, _ in draw_order[:10]:
            top10_counts[eid] += 1
        for eid, _ in draw_order[:100]:
            top100_counts[eid] += 1

    needs_sorted = sorted(rankable_summaries, key=lambda r: (-float(r["l_m_need_median"]), r["edition_target_id"]))
    eff_sorted = sorted(rankable_summaries, key=lambda r: (-float(r["l_m_efficiency_median"]), r["edition_target_id"]))
    stage_needs_sorted = sorted(stage_summaries, key=lambda r: (-float(r["l_m_need_median"]), r["edition_target_id"]))
    stage_eff_sorted = sorted(stage_summaries, key=lambda r: (-float(r["l_m_efficiency_median"]), r["edition_target_id"]))
    for rank, rec in enumerate(needs_sorted, start=1):
        rec["l_m_need_rank"] = rank
        eid = rec["edition_target_id"]
        rec["l_m_need_top10_probability"] = f"{top10_counts[eid] / draws:.6f}"
        rec["l_m_need_top100_probability"] = f"{top100_counts[eid] / draws:.6f}"
    for rank, rec in enumerate(eff_sorted, start=1):
        rec["l_m_efficiency_rank"] = rank
    for rank, rec in enumerate(stage_needs_sorted, start=1):
        rec["stage_opportunity_rank"] = rank
    for rank, rec in enumerate(stage_eff_sorted, start=1):
        rec["stage_opportunity_efficiency_rank"] = rank

    # Prior sensitivity is deliberately small and symmetric.  It changes only
    # the common prior mean, never target-specific weights or labels.
    sensitivity_rows: list[dict[str, Any]] = []
    prior_means = {"optimistic_access_common": 0.20, "reference_common": 0.35, "diffuse_common": 0.35, "pessimistic_access_common": 0.65}
    reference_order = {rec["edition_target_id"]: idx for idx, rec in enumerate(needs_sorted, start=1)}
    for prior_id, prior_mean in sorted(prior_means.items()):
        adjusted: list[tuple[str, float]] = []
        for rec in rankable_summaries:
            observed = float(rec["need_index"])
            # Shrink every target toward the same prior mean by the same rule.
            adjusted_need = 0.65 * observed + 0.35 * prior_mean
            adjusted.append((rec["edition_target_id"], float(rec["population_point_for_model"]) * adjusted_need))
        adjusted.sort(key=lambda pair: (-pair[1], pair[0]))
        rank_map = {eid: idx for idx, (eid, _) in enumerate(adjusted, start=1)}
        top100 = {eid for eid, _ in adjusted[:100]}
        for eid, value in adjusted:
            sensitivity_rows.append({
                "prior_family": prior_id,
                "edition_target_id": eid,
                "model_need_proxy": f"{value:.6f}",
                "rank": rank_map[eid],
                "reference_rank": reference_order[eid],
                "rank_change_from_reference": rank_map[eid] - reference_order[eid],
                "top100_member": str(eid in top100).lower(),
            })
    # Factor removal diagnostics use the same population and common factors.
    factor_sensitivity: list[dict[str, Any]] = []
    for removed in list(FACTOR_WEIGHTS) + ["none"]:
        values = []
        for rec in rankable_summaries:
            total_weight = sum(weight for key, weight in FACTOR_WEIGHTS.items() if key != removed)
            score = sum(weight * float(rec[key]) for key, weight in FACTOR_WEIGHTS.items() if key != removed) / max(total_weight, 1e-12)
            values.append((rec["edition_target_id"], float(rec["population_point_for_model"]) * score))
        values.sort(key=lambda pair: (-pair[1], pair[0]))
        for rank, (eid, value) in enumerate(values, start=1):
            factor_sensitivity.append({"removed_factor": removed, "edition_target_id": eid, "rank": rank, "score": f"{value:.6f}"})

    fields = list(summaries[0].keys())
    score_path = root / "structured/GLOBAL_TARGET_SCORE_TABLE_v3.csv"
    write_csv(score_path, summaries, fields)
    id_fields = ["l_id_rank_best", "l_id_rank_worst"]
    id_rows = []
    id_order = (
        sorted(rankable_summaries, key=lambda r: (int(r["l_id_possible_rank_best"]), r["edition_target_id"]))
        + sorted(stage_summaries, key=lambda r: r["edition_target_id"])
        + sorted(unranked_summaries, key=lambda r: r["edition_target_id"])
    )
    for rec in id_order:
        id_rows.append({
            "edition_target_id": rec["edition_target_id"], "label": rec["label"], "language_tag": rec["language_tag"],
            "population_low": rec["population_low"], "population_high": rec["population_high"],
            "intrinsic_need_low": rec["intrinsic_need_low"], "intrinsic_need_high": rec["intrinsic_need_high"],
            "possible_rank_best": rec["l_id_possible_rank_best"], "possible_rank_worst": rec["l_id_possible_rank_worst"],
            "top10_status": rec["l_id_top10_status"], "top100_status": rec["l_id_top100_status"],
            "population_basis_class": rec["population_basis_class"],
            "order_lane": rec.get("order_lane", ""),
            "model_status": (
                "L-ID_PARTIAL_IDENTIFICATION_ENVELOPE" if rec in rankable_summaries
                else ("STAGE_OPPORTUNITY_SEPARATE_ORDER" if rec in stage_summaries else "UNRANKED_PRIMARY_ORDER_GATE")
            ),
            **provenance_columns(rec),
        })
    l_id_path = root / "structured/ORDER_L_ID_v3.csv"
    write_csv(l_id_path, id_rows)
    l_m_rows = []
    for rank, rec in enumerate(needs_sorted, start=1):
        l_m_rows.append({
            "decision_rank": rank, "edition_target_id": rec["edition_target_id"], "label": rec["label"],
            "language_tag": rec["language_tag"], "population_basis_class": rec["population_basis_class"],
            "order_lane": rec.get("order_lane", "person_need"),
            "population_low": rec["population_low"], "population_base": rec["population_base"],
            "population_high": rec["population_high"], "population_source_id": rec["population_source_id"],
            "population_definition": rec["population_definition"], "population_reference_year": rec["population_reference_year"],
            "population_confidence": rec["population_confidence"], "population_atom_id": rec["population_atom_id"],
            "schooling_language_gap": rec["schooling_language_gap"], "learning_completion_gap": rec["learning_completion_gap"],
            "open_resource_scarcity": rec["open_resource_scarcity"],
            "academic_lingua_franca_nonoverlap": rec["academic_lingua_franca_nonoverlap"],
            "delivery_gap": rec["delivery_gap"], "accessibility_gap": rec["accessibility_gap"],
            "intrinsic_need_low": rec["intrinsic_need_low"], "intrinsic_need_model": rec["intrinsic_need_model"],
            "intrinsic_need_high": rec["intrinsic_need_high"],
            "intrinsic_need_p05": rec["l_m_need_p05"], "intrinsic_need_median": rec["l_m_need_median"],
            "intrinsic_need_mean": rec["l_m_need_mean"], "intrinsic_need_p95": rec["l_m_need_p95"],
            "top10_probability": rec["l_m_need_top10_probability"], "top100_probability": rec["l_m_need_top100_probability"],
            "standard_compute_p50_fecu": rec["standard_compute_p50_fecu"], "compute_evidence_class": rec["compute_evidence_class"],
            "population_rank_eligible": rec["population_rank_eligible"], "primary_order_eligible": rec["primary_order_eligible"],
            "model_status": "L-M_COMMON_PRIOR_MODEL_CONDITIONAL",
            **provenance_columns(rec),
        })
    # Keep exact stage/enrolment opportunities in the complete L-M roster, but
    # label them as a separate estimand instead of presenting them as person
    # counts in the needs-only order.
    for rank, rec in enumerate(stage_needs_sorted, start=1):
        l_m_rows.append({
            "decision_rank": "", "edition_target_id": rec["edition_target_id"], "label": rec["label"],
            "language_tag": rec["language_tag"], "population_basis_class": rec["population_basis_class"],
            "order_lane": "stage_opportunity",
            "population_low": rec["population_low"], "population_base": rec["population_base"],
            "population_high": rec["population_high"], "population_source_id": rec["population_source_id"],
            "population_definition": rec["population_definition"], "population_reference_year": rec["population_reference_year"],
            "population_confidence": rec["population_confidence"], "population_atom_id": rec["population_atom_id"],
            "schooling_language_gap": rec["schooling_language_gap"], "learning_completion_gap": rec["learning_completion_gap"],
            "open_resource_scarcity": rec["open_resource_scarcity"],
            "academic_lingua_franca_nonoverlap": rec["academic_lingua_franca_nonoverlap"],
            "delivery_gap": rec["delivery_gap"], "accessibility_gap": rec["accessibility_gap"],
            "intrinsic_need_low": rec["intrinsic_need_low"], "intrinsic_need_model": rec["intrinsic_need_model"],
            "intrinsic_need_high": rec["intrinsic_need_high"],
            "intrinsic_need_p05": rec["l_m_need_p05"], "intrinsic_need_median": rec["l_m_need_median"],
            "intrinsic_need_mean": rec["l_m_need_mean"], "intrinsic_need_p95": rec["l_m_need_p95"],
            "top10_probability": "", "top100_probability": "",
            "standard_compute_p50_fecu": rec["standard_compute_p50_fecu"], "compute_evidence_class": rec["compute_evidence_class"],
            "population_rank_eligible": rec["population_rank_eligible"], "primary_order_eligible": rec["primary_order_eligible"],
            "model_status": "STAGE_OPPORTUNITY_SEPARATE_ORDER",
            "stage_opportunity_rank": rank,
            **provenance_columns(rec),
        })
    # Preserve set equality in the full L-M table while keeping unresolved
    # denominators visibly outside the primary order.
    for rec in sorted(unranked_summaries, key=lambda r: r["edition_target_id"]):
        l_m_rows.append({
            "decision_rank": "", "edition_target_id": rec["edition_target_id"], "label": rec["label"],
            "language_tag": rec["language_tag"], "population_basis_class": rec["population_basis_class"],
            "order_lane": rec.get("order_lane", "unranked_context"),
            "population_low": rec["population_low"], "population_base": rec["population_base"],
            "population_high": rec["population_high"], "population_source_id": rec["population_source_id"],
            "population_definition": rec["population_definition"], "population_reference_year": rec["population_reference_year"],
            "population_confidence": rec["population_confidence"], "population_atom_id": rec["population_atom_id"],
            "schooling_language_gap": rec["schooling_language_gap"], "learning_completion_gap": rec["learning_completion_gap"],
            "open_resource_scarcity": rec["open_resource_scarcity"],
            "academic_lingua_franca_nonoverlap": rec["academic_lingua_franca_nonoverlap"],
            "delivery_gap": rec["delivery_gap"], "accessibility_gap": rec["accessibility_gap"],
            "intrinsic_need_low": rec["intrinsic_need_low"], "intrinsic_need_model": rec["intrinsic_need_model"],
            "intrinsic_need_high": rec["intrinsic_need_high"],
            "intrinsic_need_p05": "", "intrinsic_need_median": "", "intrinsic_need_mean": "", "intrinsic_need_p95": "",
            "top10_probability": "", "top100_probability": "",
            "standard_compute_p50_fecu": rec["standard_compute_p50_fecu"], "compute_evidence_class": rec["compute_evidence_class"],
            "population_rank_eligible": rec["population_rank_eligible"], "primary_order_eligible": rec["primary_order_eligible"],
            "model_status": "UNRANKED_PRIMARY_ORDER_GATE" if rec.get("primary_order_eligible") != "true" else "UNRANKED_NO_SOURCE_BOUND_PERSON_DENOMINATOR",
            **provenance_columns(rec),
        })
    l_m_path = root / "structured/ORDER_L_M_v3.csv"
    write_csv(l_m_path, l_m_rows)
    joint_path = root / "structured/ORDER_L_JOINT_DRAWS_v3.csv.gz"
    joint_path.parent.mkdir(parents=True, exist_ok=True)
    tmp_joint = joint_path.with_suffix(joint_path.suffix + ".tmp")
    with gzip.GzipFile(filename="", mode="wb", fileobj=tmp_joint.open("wb"), mtime=0, compresslevel=9) as gz:
        fields_draw = list(draw_rows[0].keys()) if draw_rows else []
        gz.write((",".join(fields_draw) + "\n").encode("utf-8"))
        for row in draw_rows:
            gz.write((",".join(str(row.get(field, "")) for field in fields_draw) + "\n").encode("utf-8"))
    os.replace(tmp_joint, joint_path)
    sens_path = root / "structured/ORDER_L_SENSITIVITY_v3.csv"
    write_csv(sens_path, sensitivity_rows)
    factor_path = root / "structured/ORDER_L_FACTOR_REMOVAL_SENSITIVITY_v3.csv"
    write_csv(factor_path, factor_sensitivity)
    top10_path = root / "structured/TOP10_NEEDS_ONLY_v3.csv"
    top100_path = root / "structured/TOP100_NEEDS_ONLY_v3.csv"
    write_csv(top10_path, l_m_rows[:10])
    write_csv(top100_path, l_m_rows[:100])
    stage_rows = []
    for rank, rec in enumerate(stage_needs_sorted, start=1):
        stage_rows.append({
            "opportunity_rank": rank, "edition_target_id": rec["edition_target_id"], "label": rec["label"],
            "language_tag": rec["language_tag"], "population_basis_class": rec["population_basis_class"],
            "population_low": rec["population_low"], "population_base": rec["population_base"],
            "population_high": rec["population_high"], "population_source_id": rec["population_source_id"],
            "population_definition": rec["population_definition"], "population_reference_year": rec["population_reference_year"],
            "population_confidence": rec["population_confidence"], "intrinsic_need_p05": rec["l_m_need_p05"],
            "intrinsic_need_median": rec["l_m_need_median"], "intrinsic_need_mean": rec["l_m_need_mean"],
            "intrinsic_need_p95": rec["l_m_need_p95"], "standard_compute_p50_fecu": rec["standard_compute_p50_fecu"],
            "compute_evidence_class": rec["compute_evidence_class"],
            "model_status": "STAGE_OPPORTUNITY_COMMON_PRIOR_MODEL_CONDITIONAL",
            **provenance_columns(rec),
        })
    stage_path = root / "structured/ORDER_STAGE_OPPORTUNITY_v3.csv"
    stage_top10_path = root / "structured/TOP10_STAGE_OPPORTUNITY_v3.csv"
    stage_top100_path = root / "structured/TOP100_STAGE_OPPORTUNITY_v3.csv"
    write_csv(stage_path, stage_rows)
    write_csv(stage_top10_path, stage_rows[:10])
    write_csv(stage_top100_path, stage_rows[:100])
    eff_rows = []
    for rank, rec in enumerate(eff_sorted, start=1):
        eff_rows.append({
            "decision_rank": rank, "edition_target_id": rec["edition_target_id"], "label": rec["label"], "language_tag": rec["language_tag"],
            "population_basis_class": rec["population_basis_class"], "intrinsic_need_median": rec["l_m_need_median"],
            "standard_compute_p50_fecu": rec["standard_compute_p50_fecu"], "access_gain_per_compute_median": rec["l_m_efficiency_median"],
            "population_source_id": rec["population_source_id"], "population_definition": rec["population_definition"],
            "population_reference_year": rec["population_reference_year"], "population_confidence": rec["population_confidence"],
            "compute_evidence_class": rec["compute_evidence_class"], "model_status": "L-M_NEED_PER_STANDARDIZED_COMPUTE",
            **provenance_columns(rec),
        })
    for rec in sorted(unranked_summaries, key=lambda r: r["edition_target_id"]):
        eff_rows.append({
            "decision_rank": "", "edition_target_id": rec["edition_target_id"], "label": rec["label"],
            "language_tag": rec["language_tag"], "population_basis_class": rec["population_basis_class"],
            "intrinsic_need_median": "", "standard_compute_p50_fecu": rec["standard_compute_p50_fecu"],
            "access_gain_per_compute_median": "", "compute_evidence_class": rec["compute_evidence_class"],
            "population_source_id": rec["population_source_id"], "population_definition": rec["population_definition"],
            "population_reference_year": rec["population_reference_year"], "population_confidence": rec["population_confidence"],
            "model_status": "UNRANKED_PRIMARY_ORDER_GATE" if rec.get("primary_order_eligible") != "true" else "UNRANKED_NO_SOURCE_BOUND_PERSON_DENOMINATOR",
            **provenance_columns(rec),
        })
    top10_eff_path = root / "structured/TOP10_COMPUTE_EFFICIENCY_v3.csv"
    top100_eff_path = root / "structured/TOP100_COMPUTE_EFFICIENCY_v3.csv"
    write_csv(top10_eff_path, eff_rows[:10])
    write_csv(top100_eff_path, eff_rows[:100])
    stage_eff_rows = []
    for rank, rec in enumerate(stage_eff_sorted, start=1):
        stage_eff_rows.append({
            "opportunity_efficiency_rank": rank, "edition_target_id": rec["edition_target_id"], "label": rec["label"],
            "language_tag": rec["language_tag"], "population_basis_class": rec["population_basis_class"],
            "intrinsic_need_median": rec["l_m_need_median"], "standard_compute_p50_fecu": rec["standard_compute_p50_fecu"],
            "access_gain_per_compute_median": rec["l_m_efficiency_median"],
            "population_source_id": rec["population_source_id"], "population_definition": rec["population_definition"],
            "population_reference_year": rec["population_reference_year"], "population_confidence": rec["population_confidence"],
            "compute_evidence_class": rec["compute_evidence_class"],
            "model_status": "STAGE_OPPORTUNITY_NEED_PER_STANDARDIZED_COMPUTE",
            **provenance_columns(rec),
        })
    stage_eff_path = root / "structured/ORDER_STAGE_OPPORTUNITY_EFFICIENCY_v3.csv"
    write_csv(stage_eff_path, stage_eff_rows)

    # Exact required inclusions are checked by ID/semantic tag, not by rank.
    required = {"id", "ind", "zh", "zho", "cmn", "ja", "jpn"}
    required_ids = {"lang:id-Latn-ID", "lang:zh-Hans-CN", "lang:ja-Jpan-JP"}
    present_required = [
        rec for rec in summaries
        if any(code in required for code in re.split(r"[-_:]", rec["language_tag"].lower()))
        or required_ids.intersection(edition_id_aliases(rec["edition_target_id"]))
    ]
    if not present_required:
        raise RuntimeError("Indonesia/Chinese/Japan equal-treatment presence check failed")
    output_paths = [
        score_path, l_id_path, l_m_path, joint_path, sens_path, factor_path,
        top10_path, top100_path, top10_eff_path, top100_eff_path,
        stage_path, stage_top10_path, stage_top100_path, stage_eff_path,
    ]
    output_manifest = {str(path.relative_to(root)).replace("\\", "/"): {"bytes": path.stat().st_size, "sha256": sha256_file(path)} for path in output_paths}
    score_id_set = {str(rec["edition_target_id"]) for rec in summaries}
    l_id_id_set = {str(row["edition_target_id"]) for row in id_rows}
    l_m_id_set = {str(row["edition_target_id"]) for row in l_m_rows}
    eff_id_set = {str(row["edition_target_id"]) for row in eff_rows}
    stage_id_set = {str(row["edition_target_id"]) for row in stage_rows}
    expected_top10 = [rec["edition_target_id"] for rec in needs_sorted[:10]]
    expected_top100 = [rec["edition_target_id"] for rec in needs_sorted[:100]]
    expected_eff_top10 = [rec["edition_target_id"] for rec in eff_sorted[:10]]
    expected_eff_top100 = [rec["edition_target_id"] for rec in eff_sorted[:100]]
    ranked_auth_rows_ok = all(
        str(rec.get("authorization_status", "")).upper() == "ADMIT"
        and str(rec.get("authorization_id", "")) in authorization_by_id
        and str(rec.get("evidence_row_sha256", "")) == str(authorization_by_id[str(rec.get("authorization_id", ""))].get("evidence_row_sha256", ""))
        and str(rec.get("target_row_sha256", "")) == str(authorization_by_id[str(rec.get("authorization_id", ""))].get("target_row_sha256", ""))
        and str(rec.get("local_work_exclusion", "")).lower() == "true"
        and str(rec.get("synthetic_or_model_prior", "")).lower() == "false"
        and str(rec.get("bounds_source_complete", "")).lower() == "true"
        and str(rec.get("bounds_were_imputed", "")).lower() == "false"
        for rec in rankable_summaries
    )
    stage_auth_rows_ok = all(
        str(rec.get("authorization_status", "")).upper() == "STAGE_OPPORTUNITY"
        and str(rec.get("authorization_id", "")) in authorization_by_id
        and str(rec.get("evidence_row_sha256", "")) == str(authorization_by_id[str(rec.get("authorization_id", ""))].get("evidence_row_sha256", ""))
        and str(rec.get("target_row_sha256", "")) == str(authorization_by_id[str(rec.get("authorization_id", ""))].get("target_row_sha256", ""))
        and str(rec.get("local_work_exclusion", "")).lower() == "true"
        and str(rec.get("synthetic_or_model_prior", "")).lower() == "false"
        and str(rec.get("bounds_source_complete", "")).lower() == "true"
        and str(rec.get("bounds_were_imputed", "")).lower() == "false"
        for rec in stage_summaries
    )
    admit_authorization_target_ids = {
        str(row.get("edition_target_id", ""))
        for row in authorization_rows
        if str(row.get("authorization_status", "")).strip().upper() == "ADMIT"
        and str(row.get("edition_target_id", "")).strip()
    }
    stage_authorization_target_ids = {
        str(row.get("edition_target_id", ""))
        for row in authorization_rows
        if str(row.get("authorization_status", "")).strip().upper() == "STAGE_OPPORTUNITY"
        and str(row.get("edition_target_id", "")).strip()
    }
    selected_admit_target_ids = {
        str(rec.get("edition_target_id", ""))
        for rec in rankable_summaries
        if str(rec.get("authorization_status", "")).upper() == "ADMIT"
    }
    selected_stage_target_ids = {
        str(rec.get("edition_target_id", ""))
        for rec in stage_summaries
        if str(rec.get("authorization_status", "")).upper() == "STAGE_OPPORTUNITY"
    }
    admit_target_coverage = selected_admit_target_ids == admit_authorization_target_ids
    stage_target_coverage = selected_stage_target_ids == stage_authorization_target_ids
    all_rankable_targets_have_nonzero_model_need = all(
        float(rec["intrinsic_need_model"]) > 0 for rec in rankable_summaries
    )
    all_targets_have_finite_population_bounds = all(
        float(rec["population_high"]) > 0 and float(rec["population_low"]) >= 0
        for rec in summaries
    )
    draw_level_probabilities_bounded = all(
        0.0 <= float(rec.get("l_m_need_top10_probability", 0.0)) <= 1.0
        and 0.0 <= float(rec.get("l_m_need_top100_probability", 0.0)) <= 1.0
        for rec in rankable_summaries
    )
    no_context_ceiling_in_primary_order = all(
        rec.get("population_basis_class") not in {
            "TERRITORIAL_OR_CONTEXT_CEILING",
            "MODEL_CONDITIONAL_TERRITORIAL_CEILING",
            "MODEL_CONDITIONAL_WORLD_CEILING",
        }
        for rec in rankable_summaries
    )
    primary_order_eligible_count = sum(
        str(rec.get("primary_order_eligible", "")).lower() == "true" for rec in summaries
    )
    unranked_no_source_bound_person_denominator_count = sum(
        rec.get("primary_order_exclusion_reason") == "UNRANKED_NO_SOURCE_BOUND_PERSON_DENOMINATOR"
        for rec in summaries
    )
    needs_only_excludes_stage_opportunity = all(
        rec.get("order_lane") == "person_need" for rec in rankable_summaries
    )
    required_presence_flags = {
        "Indonesia": any("lang:id-Latn-ID" in edition_id_aliases(rec["edition_target_id"]) for rec in summaries),
        "Mainland Simplified Chinese": any("lang:zh-Hans-CN" in edition_id_aliases(rec["edition_target_id"]) for rec in summaries),
        "Japan": any("lang:ja-Jpan-JP" in edition_id_aliases(rec["edition_target_id"]) for rec in summaries),
    }
    target_set_checks = {
        "score_equals_authority": score_id_set == set(edition_ids),
        "score_equals_l_id": score_id_set == l_id_id_set,
        "score_equals_l_m": score_id_set == l_m_id_set,
        "person_plus_unranked_equals_score": score_id_set == (eff_id_set | stage_id_set),
        "stage_set_disjoint_from_person": stage_id_set.isdisjoint({rec["edition_target_id"] for rec in rankable_summaries}),
        "needs_top10_exact_prefix": [row["edition_target_id"] for row in l_m_rows[:10]] == expected_top10,
        "needs_top100_exact_prefix": [row["edition_target_id"] for row in l_m_rows[:100]] == expected_top100,
        "eff_top10_exact_prefix": [row["edition_target_id"] for row in eff_rows[:10]] == expected_eff_top10,
        "eff_top100_exact_prefix": [row["edition_target_id"] for row in eff_rows[:100]] == expected_eff_top100,
    }
    target_set_hashes = {
        "score": canonical_sha(sorted(score_id_set)),
        "l_id": canonical_sha(sorted(l_id_id_set)),
        "l_m": canonical_sha(sorted(l_m_id_set)),
        "eff": canonical_sha(sorted(eff_id_set)),
        "stage": canonical_sha(sorted(stage_id_set)),
        "needs_top10": canonical_sha(expected_top10),
        "needs_top100": canonical_sha(expected_top100),
        "eff_top10": canonical_sha(expected_eff_top10),
        "eff_top100": canonical_sha(expected_eff_top100),
    }
    qa_status = (
        all(target_set_checks.values())
        and ranked_auth_rows_ok
        and stage_auth_rows_ok
        and admit_target_coverage
        and stage_target_coverage
        and all_rankable_targets_have_nonzero_model_need
        and all_targets_have_finite_population_bounds
        and draw_level_probabilities_bounded
        and no_context_ceiling_in_primary_order
        and needs_only_excludes_stage_opportunity
        and all(required_presence_flags.values())
    )
    qa = {
        "schema": SCHEMA,
        "model": MODEL,
        "status": "PASS" if qa_status else "FAIL",
        "target_count": len(summaries),
        "person_need_target_count": len(rankable_summaries),
        "stage_opportunity_target_count": len(stage_summaries),
        "target_set_sha256": canonical_sha(sorted(edition_ids)),
        "all_score_target_ids_set_equal": {"score": len(summaries), "l_id": len(id_rows), "l_m": len(l_m_rows), "top10": len(l_m_rows[:10]), "top100": len(l_m_rows[:100]), "eff_top10": len(eff_rows[:10]), "eff_top100": len(eff_rows[:100])},
        "target_set_checks": target_set_checks,
        "target_set_hashes": target_set_hashes,
        "authorization": {
            "path": str(authorization_path.relative_to(root)).replace("\\", "/"),
            "bytes": authorization_path.stat().st_size,
            "sha256": sha256_file(authorization_path),
            "status_counts": dict(sorted(authorization_counts.items())),
            "ranked_person_rows_have_matching_admit_receipts": ranked_auth_rows_ok,
            "stage_rows_have_matching_stage_receipts": stage_auth_rows_ok,
            "legacy_mapping_rank_eligible_true_rows": sum(1 for row in b_rows if str(row.get("rank_eligible", "")).lower() == "true"),
            "legacy_mapping_role": "retained for audit only; not an active population authority",
        },
        "rankable_target_count": len(rankable_summaries),
        "unranked_target_count": len(unranked_summaries),
        "primary_order_eligible_count": primary_order_eligible_count,
        "unranked_no_source_bound_person_denominator_count": unranked_no_source_bound_person_denominator_count,
        "generic_accessibility_overlay_count": sum(rec.get("primary_order_class") == "GENERIC_ACCESSIBILITY_OVERLAY" for rec in summaries),
        "all_rankable_targets_have_nonzero_model_need": all_rankable_targets_have_nonzero_model_need,
        "all_targets_have_finite_population_bounds": all_targets_have_finite_population_bounds,
        "no_context_ceiling_in_primary_order": no_context_ceiling_in_primary_order,
        "draw_level_probabilities_bounded": draw_level_probabilities_bounded,
        "needs_only_excludes_stage_opportunity": needs_only_excludes_stage_opportunity,
        "authorization_target_coverage": {
            "admit_authorization_row_count": sum(1 for row in authorization_rows if str(row.get("authorization_status", "")).upper() == "ADMIT"),
            "admit_authorization_target_count": len(admit_authorization_target_ids),
            "selected_admit_target_count": len(selected_admit_target_ids),
            "admit_target_coverage": admit_target_coverage,
            "admit_authorization_target_ids_not_selected": sorted(admit_authorization_target_ids - selected_admit_target_ids),
            "stage_authorization_row_count": sum(1 for row in authorization_rows if str(row.get("authorization_status", "")).upper() == "STAGE_OPPORTUNITY"),
            "stage_authorization_target_count": len(stage_authorization_target_ids),
            "selected_stage_target_count": len(selected_stage_target_ids),
            "stage_target_coverage": stage_target_coverage,
            "stage_authorization_target_ids_not_selected": sorted(stage_authorization_target_ids - selected_stage_target_ids),
            "stage_rows_collapsed_within_target": sum(1 for row in authorization_rows if str(row.get("authorization_status", "")).upper() == "STAGE_OPPORTUNITY") - len(stage_authorization_target_ids),
        },
        "required_large_cohort_presence": {
            **required_presence_flags,
        },
        "forbidden_predictor_terms_checked": list(FORBIDDEN_INPUT_TERMS),
        "population_assignment": "explicit atom IDs; common equal allocation only for unresolved country ceilings; no additive macro-language inheritance",
        "weights": FACTOR_WEIGHTS,
        "draws_per_target": draws,
        "draw_algorithm": "SHA-256-addressed deterministic triangular/uniform population and truncated-normal factor draws; top-K probabilities are joint draw frequencies",
        "cost_source": {"class": compute_class, **({**compute_meta, "path": str(Path(compute_meta["path"]).relative_to(root)).replace("\\", "/")} if compute_meta.get("path") else compute_meta)},
    }
    qa_path = root / "qa/GLOBAL_ACCESS_RANKINGS_V3_QA.json"
    write_json(qa_path, qa)
    receipt = {
        "schema": SCHEMA,
        "model": MODEL,
        "status": "PASS" if qa_status else "FAIL",
        "generated_utc": "2026-09-01",
        "authority_inputs": {
            "edition_registry": {"path": str(a_path.relative_to(root)).replace("\\", "/"), "bytes": a_path.stat().st_size, "sha256": sha256_file(a_path)},
            "evidence_authorization": {"path": str(authorization_path.relative_to(root)).replace("\\", "/"), "bytes": authorization_path.stat().st_size, "sha256": sha256_file(authorization_path), "role": "active population/evidence admission ledger"},
            "successor_universe": {"path": "structured/canonical_universe_successor_v2.json", "bytes": (root / "structured/canonical_universe_successor_v2.json").stat().st_size, "sha256": sha256_file(root / "structured/canonical_universe_successor_v2.json")},
            "legacy_evidence_mapping": {"path": str(b_path.relative_to(root)).replace("\\", "/"), "bytes": b_path.stat().st_size, "sha256": sha256_file(b_path), "role": "retained for audit; superseded as active admission gate", "rank_eligible_true_rows": sum(1 for row in b_rows if str(row.get("rank_eligible", "")).lower() == "true")},
            "country_context": {"path": "structured/major_country_context.json", "bytes": (root / "structured/major_country_context.json").stat().st_size, "sha256": sha256_file(root / "structured/major_country_context.json")},
            "factor_transport_registry": {"path": "structured/FACTOR_TRANSPORT_REGISTRY_v1.json", "bytes": (root / "structured/FACTOR_TRANSPORT_REGISTRY_v1.json").stat().st_size, "sha256": sha256_file(root / "structured/FACTOR_TRANSPORT_REGISTRY_v1.json")},
        },
        "input_evidence_hashes": flatten_source_hashes([
            authorization_path,
            root / "structured/canonical_universe_successor_v2.json",
            root / "structured/large_language_population_strata_proposal.json",
            root / "structured/empirical_event_gap_ledger_v2.csv",
            root / "structured/oer_target_canon_evidence_matrix.csv",
            root / "structured/academic_language_nonoverlap.json",
            root / "structured/ASIA_EMPIRICAL_NEED_INPUTS.csv",
            root / "structured/AFRICA_EMPIRICAL_NEED_INPUTS.csv",
            root / "structured/AMERICAS_EUROPE_EMPIRICAL_NEED_INPUTS.csv",
            root / "structured/OCEANIA_CENTRAL_ASIA_EMPIRICAL_INPUTS.csv",
            root / "structured/FACTOR_TRANSPORT_REGISTRY_v1.json",
        ], root=root),
        "script": {"path": "scripts/build_global_access_rankings_v3.py", "bytes": (root / "scripts/build_global_access_rankings_v3.py").stat().st_size, "sha256": sha256_file(root / "scripts/build_global_access_rankings_v3.py"), "draws_argument": draws},
        "target_count": len(summaries),
        "person_need_target_count": len(rankable_summaries),
        "stage_opportunity_target_count": len(stage_summaries),
        "target_set_sha256": canonical_sha(sorted(edition_ids)),
        "target_set_checks": target_set_checks,
        "target_set_hashes": target_set_hashes,
        "authorization_checks": {
            "ranked_person_rows_have_matching_admit_receipts": ranked_auth_rows_ok,
            "stage_rows_have_matching_stage_receipts": stage_auth_rows_ok,
            "admit_target_coverage": admit_target_coverage,
            "stage_target_coverage": stage_target_coverage,
        },
        "estimands": {
            "L_ID": "[N_low * theta_low, N_high * theta_high] with explicit partial-identification envelopes; possible rank interval",
            "L_M": "U_l = N_l * sum_k w_k theta_lk under one common prior and deterministic draws",
            "stage_opportunity": "same model envelope applied to exact enrolment/stage cohorts; not a whole-language unmet-need count",
            "efficiency": "median(U_l / standardized_compute_fecu); cost is model-conditional and independent of population/need",
        },
        "missingness": "No numeric population/need evidence is converted to zero. Missing target factors use the same common prior and wider uncertainty. Missing target-bound person denominators retain an explicit ceiling witness but are excluded from the needs-only order and marked UNRANKED_NO_SOURCE_BOUND_PERSON_DENOMINATOR. Exact stage/enrolment opportunity cohorts are model-scored in a separate STAGE_OPPORTUNITY order and never mixed into the person-need Top 10/100. Generic any-target/all-language accessibility overlays remain in the census but are marked UNRANKED_PRIMARY_ORDER_GATE and reported separately.",
        "no_local_or_project_inputs": True,
        "outputs": output_manifest,
        "qa": str(qa_path.relative_to(root)).replace("\\", "/"),
    }
    receipt_path = root / "qa/GLOBAL_ACCESS_RANKINGS_V3_RECEIPT.json"
    write_json(receipt_path, receipt)
    # A file cannot contain its own final hash without a self-referential
    # contradiction.  Keep the receipt immutable and emit a conventional
    # sidecar hash instead.
    receipt_sha_path = root / "qa/GLOBAL_ACCESS_RANKINGS_V3_RECEIPT.sha256"
    receipt_sha_path.write_text(f"{sha256_file(receipt_path)}  {receipt_path.name}\n", encoding="utf-8")
    report_lines = [
        "# Global access rankings v3",
        "",
        f"Status: {'PASS' if qa_status else 'FAIL'}; model-conditional research order, not an observed language-user ranking.",
        "",
        f"The frozen v3 edition authority contains {len(summaries)} effective roster targets (not all are exact: the authority retains canonical, regional, supplement, unresolved-identity and macro rows); {len(rankable_summaries)} source-bound person-measure rows enter the needs-only order, {len(stage_summaries)} exact stage/opportunity rows are scored in a separate opportunity order, and {len(unranked_summaries)} remain visible but unranked (including context ceilings and unresolved identities). No target is removed because of region, income, prestige, evidence volume, prior translation, local holdings, or project state.",
        "",
        "The primary need index is a common weighted access-gap index: schooling-language alignment 0.22, learning/completion 0.20, open-resource scarcity 0.18, academic-language non-overlap 0.18, delivery gap 0.14, and accessibility 0.08. Missing factors use the same common prior, not zero. Population ceilings are never presented as speaker or reader counts.",
        "",
        "L-ID is an interval/envelope order and L-M is a common-prior model-conditional scenario over the source-bound person subset. Exact stage/enrolment opportunities have a separate order and cannot be read as whole-language deficits. Targets with only a world/country fallback ceiling are retained in the full tables but cannot outrank measured populations. Neither order is modified by translation work already completed anywhere.",
        "",
        "Compute efficiency uses a complete model-conditional cost table when available, otherwise a script envelope explicitly labelled as such. It is a separate denominator and cannot lower intrinsic need.",
        "",
        "Indonesia, Mainland Simplified Chinese and Japan are included as ordinary roster targets and are not treated as negative controls or discounted for any local/project reason.",
        "Population admission is controlled by structured/EVIDENCE_AUTHORIZATION_v1.csv. The predecessor evidence-mapping table is retained as a superseded audit input because its rank_eligible column is all false; it is not used to authorize a ranked row.",
        f"Authorization QA: ranked person rows match ADMIT receipts={ranked_auth_rows_ok}; stage rows match STAGE_OPPORTUNITY receipts={stage_auth_rows_ok}; complete target-set checks={all(target_set_checks.values())}.",
    ]
    report_path = root / "agent_reports/GLOBAL_ACCESS_RANKINGS_V3.md"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text("\n".join(report_lines) + "\n", encoding="utf-8")
    return {"receipt": receipt, "qa": qa, "top10": l_m_rows[:10], "top100": l_m_rows[:100], "eff_top10": eff_rows[:10]}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--draws", type=int, default=256)
    args = parser.parse_args()
    result = build(args.root.resolve(), draws=max(32, min(args.draws, 1024)))
    # Windows consoles may use a legacy code page; escaped JSON keeps the
    # bounded CLI run machine-readable without changing any artifact bytes.
    print(json.dumps({"status": result["receipt"]["status"], "target_count": result["receipt"]["target_count"], "top10": result["top10"][:10]}, ensure_ascii=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
