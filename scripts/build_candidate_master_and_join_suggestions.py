from __future__ import annotations

import csv
import re
import unicodedata
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CANDIDATE_INPUT = ROOT / "staging" / "interlanguage_matrix" / "candidate_interventions_normalized.csv"
POPULATION_INPUT = ROOT / "population_observations_master.csv"
ISO_INPUT = ROOT / "sources" / "LOC_ISO_639_2_utf8_20260825.txt"

# LOC publishes ISO 639-2 identifiers; a few modern ISO 639-3 identifiers used
# by the population register differ. Keep the crosswalk explicit rather than
# treating 639-2 and 639-3 as universally identical.
ALPHA2_TO_ISO3_OVERRIDES = {"or": "ory"}


REGION_NAMES = {
    "AF": "Afghanistan", "AM": "Armenia", "AU": "Australia", "AZ": "Azerbaijan", "BD": "Bangladesh",
    "BO": "Bolivia", "BR": "Brazil", "CA": "Canada", "CL": "Chile", "CN": "China",
    "CO": "Colombia", "DE": "Germany", "DZ": "Algeria", "ES": "Spain", "ET": "Ethiopia",
    "FO": "Faroe Islands", "FR": "France", "GB": "United Kingdom", "GE": "Georgia",
    "GL": "Greenland", "GT": "Guatemala", "HT": "Haiti", "ID": "Indonesia",
    "IN": "India", "IQ": "Iraq", "IR": "Iran", "KE": "Kenya", "KG": "Kyrgyzstan",
    "KH": "Cambodia", "KZ": "Kazakhstan", "LA": "Laos", "LK": "Sri Lanka",
    "MA": "Morocco", "MG": "Madagascar", "ML": "Mali", "MM": "Myanmar",
    "MN": "Mongolia", "MW": "Malawi", "MX": "Mexico", "MY": "Malaysia",
    "NG": "Nigeria", "NP": "Nepal", "NZ": "New Zealand", "PE": "Peru",
    "PH": "Philippines", "PK": "Pakistan", "PL": "Poland", "PY": "Paraguay", "RU": "Russian Federation",
    "RW": "Rwanda", "SN": "Senegal", "SO": "Somalia", "TH": "Thailand",
    "TJ": "Tajikistan", "TL": "Timor-Leste", "TM": "Turkmenistan", "TR": "Turkey",
    "TZ": "Tanzania", "UA": "Ukraine", "US": "United States", "UZ": "Uzbekistan", "VN": "Vietnam",
    "ZA": "South Africa", "ZW": "Zimbabwe",
}

NAME_ALIASES = {
    "bangla": "bengali",
    "indian bengali": "bengali",
    "indian tamil": "tamil",
    "bangladesh bangla": "bengali",
    "eastern punjabi": "punjabi",
    "western punjabi": "punjabi",
    "pakistani urdu": "urdu",
    "indian urdu": "urdu",
    "pakistani pashto": "pashto",
    "afghan pashto": "pashto",
    "isizulu": "zulu",
    "isixhosa": "xhosa",
    "south african ndebele": "isindebele",
    "maori": "maori",
    "northern ndebele": "zimbabwean ndebele",
    "indonesian open logic completion": "indonesian",
    "bajjika nepal profile": "bajjika",
    "maithili nepal profile": "maithili",
    "bhojpuri nepal profile": "bhojpuri",
    "avadhi nepal profile": "avadhi",
    "chichewa malawi profile": "chewa",
    "s gaw karen": "karen",
    "ayacucho quechua": "quechua",
    "cusco quechua": "quechua",
    "south bolivian quechua": "quechua",
    "central aymara": "aymara",
    "eastern huasteca nahuatl": "nahuatl",
    "tetum prasa": "tetun prasa",
    "thai usable home language union": "thai",
}


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def normalized_name(text: str) -> str:
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii").lower()
    text = re.sub(r"\([^)]*\)", " ", text)
    text = re.sub(r"[^a-z0-9]+", " ", text).strip()
    return NAME_ALIASES.get(text, text)


def iso_maps() -> tuple[dict[str, str], dict[str, str]]:
    alpha2_to_3: dict[str, str] = {}
    name_to_3: dict[str, str] = {}
    for line in ISO_INPUT.read_text(encoding="utf-8-sig").splitlines():
        fields = line.split("|")
        if len(fields) < 5:
            continue
        bibliographic, terminologic, alpha2, english, _ = fields[:5]
        iso3 = terminologic or bibliographic
        if alpha2:
            alpha2_to_3[alpha2.lower()] = iso3.lower()
        for name in english.split(";"):
            name_to_3[normalized_name(name)] = iso3.lower()
    alpha2_to_3.update(ALPHA2_TO_ISO3_OVERRIDES)
    return alpha2_to_3, name_to_3


def candidate_code(candidate: dict[str, str], alpha2_to_3: dict[str, str]) -> str:
    tag = candidate["variety_or_register"].split()[0]
    first = tag.split("-")[0].lower()
    if re.fullmatch(r"[a-z]{2}", first):
        return alpha2_to_3.get(first, "")
    if re.fullmatch(r"[a-z]{3}", first):
        return first
    return ""


def population_code(observation: dict[str, str], alpha2_to_3: dict[str, str]) -> str:
    # The canonical register may preserve an exact ISO-3 code followed by a
    # source-code note (for example, ``ben / source bn``). Admit only a leading
    # three-letter identifier; never scrape a later code from an aggregate or
    # prose label.
    identifier = observation["iso_639_3_or_other_id"].lower()
    first = re.split(r"[^a-z]", identifier, maxsplit=1)[0]
    if re.fullmatch(r"[a-z]{2}", first):
        return alpha2_to_3.get(first, "")
    if re.fullmatch(r"[a-z]{3}", first):
        return first
    return ""


def candidate_regions(candidate: dict[str, str]) -> set[str]:
    tag = candidate["variety_or_register"].split()[0]
    regions = set()
    for part in tag.split("-")[1:]:
        if re.fullmatch(r"[A-Z]{2}", part):
            regions.add(REGION_NAMES.get(part, part))
    scope = candidate["territory_scope"].lower()
    for name in REGION_NAMES.values():
        if name.lower() in scope:
            regions.add(name)
    return regions


def territory_matches(candidate: dict[str, str], observation: dict[str, str]) -> bool:
    territory = observation["territory"].lower()
    regions = candidate_regions(candidate)
    if any(region.lower() in territory or territory in region.lower() for region in regions):
        return True
    scope = candidate["territory_scope"].lower()
    return territory in scope or scope in territory


def main() -> None:
    candidates = read_csv(CANDIDATE_INPUT)
    headers = list(candidates[0].keys())
    profile_fields = [
        "profile_tag_status", "profile_resolution_status",
        "profile_ranking_treatment", "profile_negative_control_status",
        "profile_source_ids", "resolved_edition_name",
    ]
    headers.extend(field for field in profile_fields if field not in headers)
    for candidate in candidates:
        for field in profile_fields:
            candidate.setdefault(field, "")
    if any(row["intervention_id"] == "CMP-ID-ID" for row in candidates):
        raise RuntimeError("CMP-ID-ID already exists")
    indonesian = {field: "" for field in headers}
    indonesian.update({
        "intervention_id": "CMP-ID-ID",
        "target_type": "natural_language_baseline",
        "target_name": "Indonesian Open Logic complete baseline",
        "variety_or_register": "id-Latn-ID",
        "script": "Latn",
        "territory_scope": "Indonesia",
        "curriculum_source": "Open Logic Project",
        "curriculum_work": "complete 722-unit reader",
        "curriculum_unit": "OLP-0001 through OLP-0722",
        "adaptation_depth": "D3",
        "formats": "AX-HTML;AX-PDF;AX-OFFLINE",
        "existing_local_status": "complete_722_of_722_current_program",
        "source_ids": "ACE-A011;CURRENT_INDONESIAN_PROGRAM_STATUS_20260830",
        "evidence_status": "public GitHub evidence: 722/722 editable content units and a 1,116-page reader; the broader established program is tracked separately",
        "overlap_rule": "D=0 for the exact Open Logic corpus; it adds no forward translation workload or new reach. Any future Indonesian item must name an exact uncovered component.",
        "notes": "Completed baseline, not a forward completion candidate and not a pilot. Retained to prevent double counting.",
        "rankability_status": "baseline_not_forward_completion_candidate",
    })
    candidates.append(indonesian)

    alpha2_to_3, _ = iso_maps()
    observations = read_csv(POPULATION_INPUT)

    # Exact official observations can reveal bounded target populations that
    # were absent from the discovery seed. Add a stable intervention shell for
    # those rows without inventing script or orthography evidence. These shells
    # are provisional until the separate target-profile evidence join is made,
    # but they permit transparent population/compute sensitivity accounting.
    admitted_provenance = {"ACE-A114", "ACE-A118"}
    admitted_mapping = {
        "source_named_language_observation",
        "exact_source_language_label_editorial_iso_mapping_pending_central_review",
        "exact_source_fula_variety_label_editorial_iso_mapping_pending_central_review",
        "exact_named_language_profile_editorial_iso_mapping_pending_central_review",
        "derived_exact_named_language_union_editorial_iso_mapping_pending_central_review",
    }
    territory_to_code = {name: code for code, name in REGION_NAMES.items()}
    for observation in observations:
        if observation["provenance_table"] not in admitted_provenance:
            continue
        if observation["count_unit"] not in {"persons", "estimated_persons"} or observation["negative_control"] == "true":
            continue
        if observation["target_mapping_status"] not in admitted_mapping:
            continue
        p_code = population_code(observation, alpha2_to_3)
        p_name = normalized_name(observation["language_label"])
        already_present = any(
            candidate["target_type"] in {"natural_language", "natural_language_completion", "signed_language_access"}
            and territory_matches(candidate, observation)
            and (
                (p_code and candidate_code(candidate, alpha2_to_3) == p_code)
                or normalized_name(candidate["target_name"]) == p_name
            )
            for candidate in candidates
        )
        if already_present:
            continue
        territory_code = territory_to_code.get(observation["territory"], "XX")
        language_code = p_code or "und"
        signed = "sign language" in observation["language_label"].casefold()
        addition = {field: "" for field in headers}
        addition.update({
            "intervention_id": f"OBS-{observation['observation_id']}",
            "target_type": "signed_language_access" if signed else "natural_language",
            "target_name": observation["language_label"],
            "variety_or_register": f"{language_code}-Zzzz-{territory_code} target profile; script unresolved by population source",
            "script": "Signed" if signed else "Zzzz (unresolved by population source)",
            "territory_scope": observation["territory"],
            "curriculum_source": "OpenStax plus Open Logic Project",
            "curriculum_work": "FR-2 common comparator",
            "curriculum_unit": "Open Logic FR-2 foundations; population-specific OpenStax priority pending final need join",
            "adaptation_depth": "D5" if signed else "D3",
            "formats": "AX-SIGNED-VIDEO;AX-HTML" if signed else "AX-HTML;AX-PDF;AX-OFFLINE",
            "existing_local_status": "not_found_in_bounded_local_census",
            "source_ids": f"{observation['source_id']};{observation['provenance_table']}",
            "evidence_status": "exact territory-specific source population observation; script and orthography require a separate target-profile source",
            "overlap_rule": "Use only the cited source universe; do not inflate it to a global speaker total or sum overlapping source categories.",
            "notes": f"Mechanically surfaced from {observation['observation_id']}; target-profile research remains explicit rather than inferred from the population source.",
            "rankability_status": "exact_population_join_target_profile_evidence_pending",
        })
        candidates.append(addition)

    # Apply the separately source-audited edition-profile return. A blank
    # profile is preserved for labels that genuinely require a community split;
    # it is never replaced by an invented aggregate standard.
    profile_path = ROOT / "staging" / "target_profile_completion" / "target_profiles_agent.csv"
    if profile_path.is_file():
        profile_rows = read_csv(profile_path)
        by_id = {row["intervention_id"]: row for row in profile_rows}
        candidate_by_id = {row["intervention_id"]: row for row in candidates}
        missing = set(by_id) - set(candidate_by_id)
        if missing:
            raise RuntimeError(f"Target profiles refer to missing candidates: {sorted(missing)}")
        for intervention_id, profile in by_id.items():
            candidate = candidate_by_id[intervention_id]
            if profile["bcp47_target_profile"]:
                candidate["variety_or_register"] = profile["bcp47_target_profile"]
                candidate["script"] = profile["script_subtag"]
            candidate["profile_tag_status"] = profile["profile_tag_status"]
            candidate["profile_resolution_status"] = profile["resolution_status"]
            candidate["profile_ranking_treatment"] = profile["ranking_treatment"]
            candidate["profile_negative_control_status"] = profile["negative_control_status"]
            candidate["profile_source_ids"] = profile["profile_source_ids"]
            candidate["resolved_edition_name"] = profile["resolved_edition_name"]

    # These three profiles were added after the source-audited profile-return
    # tranche. Their BCP 47 tags are explicit task authorities, so retain them
    # rather than silently downgrading them to unresolved during a full rebuild.
    equal_basis_profiles = {
        "NAT-121": ("single_valid_bcp47", "resolved_single_profile", "ex_ante_equal_basis_rank_forward_residual_separate", "ACE-E021;TP-S001-IANA;TP-S002-CLDR", "Bahasa Indonesia"),
        "NAT-122": ("single_valid_bcp47", "resolved_single_profile", "ex_ante_equal_basis_rank_forward_residual_separate", "ACE-E061;TP-S001-IANA;TP-S002-CLDR", "Standard Simplified Chinese (Mainland China)"),
        "NAT-123": ("single_valid_bcp47", "resolved_single_profile", "ex_ante_equal_basis_rank_forward_stage_specific", "ACE-E064;ACE-E065;TP-S001-IANA;TP-S002-CLDR", "Japanese (Japan)"),
        "NAT-124": ("single_valid_bcp47", "resolved_single_profile", "ex_ante_equal_basis_rank_forward_residual_separate", "ACE-E011;ACE-E019;TP-S001-IANA;TP-S002-CLDR", "Standard Hindi (India)"),
        "NAT-125": ("single_valid_bcp47", "resolved_single_profile", "rank_exact_india_profile_cross_border_reuse_separate", "ACE-E011;TP-S001-IANA", "Bhojpuri (India)"),
    }
    candidate_by_id = {row["intervention_id"]: row for row in candidates}
    for intervention_id, (tag_status, resolution, treatment, source_ids, edition_name) in equal_basis_profiles.items():
        if intervention_id not in candidate_by_id:
            raise RuntimeError(f"Missing equal-basis candidate {intervention_id}")
        candidate = candidate_by_id[intervention_id]
        candidate["profile_tag_status"] = tag_status
        candidate["profile_resolution_status"] = resolution
        candidate["profile_ranking_treatment"] = treatment
        candidate["profile_negative_control_status"] = ""
        candidate["profile_source_ids"] = source_ids
        candidate["resolved_edition_name"] = edition_name

    candidate_output = ROOT / "candidate_interventions_master.csv"
    with candidate_output.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=headers)
        writer.writeheader()
        writer.writerows(candidates)

    suggestions: list[dict[str, str]] = []
    # These equal-basis profiles deliberately use an official territory or
    # functional-language observation whose label is not identical to the
    # edition label.  The identity is registered explicitly rather than being
    # inferred from fuzzy name matching.  Without this crosswalk, the exact
    # Chinese and Japanese observations are downgraded to manual-review joins
    # solely because their source labels are "Mainland China population" and
    # "Japan population".
    explicit_equal_basis_observations = {
        "NAT-121": "POP-ID-018",
        "NAT-122": "POP-CN-001",
        "NAT-123": "POP-JP-001",
        "NAT-124": "POP-IN-COMP-006",
        "NAT-125": "POP-IN-023",
    }
    for candidate in candidates:
        if candidate["target_type"] not in {
            "natural_language", "natural_language_completion", "signed_language_access"
        }:
            continue
        c_code = candidate_code(candidate, alpha2_to_3)
        c_name = normalized_name(candidate["target_name"])
        for observation in observations:
            p_code = population_code(observation, alpha2_to_3)
            p_name = normalized_name(observation["language_label"])
            code_match = bool(c_code and p_code and c_code == p_code)
            # Substring matching is unsafe for language names (for example,
            # Odia/Cambodia, Thai/Thaikueng, Mon/Mongolian, Malay/Malayalam).
            # Only an explicit normalized alias or exact normalized name is a
            # name-level suggestion; code and territory remain separate tests.
            name_match = c_name == p_name
            if not (code_match or name_match):
                continue
            territory_match = territory_matches(candidate, observation)
            collective = any(token in observation["iso_639_3_or_other_id"].lower() for token in [":aggregate", ":orgi", ":inei", "collective", "und:"])
            if code_match and name_match and territory_match and not collective:
                status = "strong_join_suggestion"
            elif code_match and name_match and territory_match:
                status = "aggregate_or_collective_join_review"
            elif code_match and territory_match:
                status = "code_only_profile_join_review"
            elif code_match:
                status = "same_language_other_territory_review"
            else:
                status = "name_only_join_review"
            if explicit_equal_basis_observations.get(candidate["intervention_id"]) == observation["observation_id"]:
                if not (code_match and territory_match and not collective):
                    raise RuntimeError(
                        "Registered equal-basis observation no longer satisfies "
                        f"code/territory checks: {candidate['intervention_id']} -> "
                        f"{observation['observation_id']}"
                    )
                status = "strong_join_suggestion"
            suggestions.append({
                "join_suggestion_id": f"JOIN-{len(suggestions)+1:04d}",
                "intervention_id": candidate["intervention_id"],
                "target_name": candidate["target_name"],
                "observation_id": observation["observation_id"],
                "population_language_label": observation["language_label"],
                "candidate_iso3": c_code,
                "population_iso3": p_code,
                "code_match": str(code_match).lower(),
                "name_match": str(name_match).lower(),
                "territory_match": str(territory_match).lower(),
                "suggestion_status": status,
                "population_base": observation["population_base"],
                "count_unit": observation["count_unit"],
                "measure_type": observation["measure_type"],
                "target_mapping_status": observation["target_mapping_status"],
                "observation_use": observation["observation_use"],
                "negative_control": observation["negative_control"],
                "notes": "Machine suggestion only; semantic audit and explicit intervention-edge factors remain required.",
            })

    join_fields = list(suggestions[0].keys()) if suggestions else []
    join_output = ROOT / "candidate_population_join_suggestions.csv"
    with join_output.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=join_fields)
        writer.writeheader()
        writer.writerows(suggestions)

    print({
        "candidate_rows": len(candidates),
        "join_suggestions": len(suggestions),
        "strong": sum(row["suggestion_status"] == "strong_join_suggestion" for row in suggestions),
        "aggregate_review": sum(row["suggestion_status"] == "aggregate_or_collective_join_review" for row in suggestions),
        "code_only_profile_review": sum(row["suggestion_status"] == "code_only_profile_join_review" for row in suggestions),
        "same_language_other_territory": sum(row["suggestion_status"] == "same_language_other_territory_review" for row in suggestions),
        "name_only": sum(row["suggestion_status"] == "name_only_join_review" for row in suggestions),
    })


if __name__ == "__main__":
    main()
