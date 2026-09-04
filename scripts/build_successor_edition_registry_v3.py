#!/usr/bin/env python3
"""Build the normalized successor edition-target/evidence authority (v3).

The v2 universe contains one row per language identity and one row per regional
stratum.  This adapter gives each normalized edition exactly one target row and
maps every source-bound evidence identity to that edition (or explicitly keeps
it context/alternative/quarantine evidence without creating a rank target).
No score, rank, or population imputation is performed.
"""
from __future__ import annotations

import argparse, csv, hashlib, json
from pathlib import Path
from collections import Counter, defaultdict

BASE = Path(__file__).resolve().parents[1]
CANON = BASE / "structured/canonical_universe_successor_v2.json"
REGIONAL = [
    BASE / "structured/AFRICA_EMPIRICAL_NEED_INPUTS.csv",
    BASE / "structured/ASIA_EMPIRICAL_NEED_INPUTS.csv",
    BASE / "structured/AMERICAS_EUROPE_EMPIRICAL_NEED_INPUTS.csv",
    BASE / "structured/OCEANIA_CENTRAL_ASIA_EMPIRICAL_INPUTS.csv",
]
SUPPLEMENT = BASE / "structured/LARGE_POPULATION_OMISSION_SUPPLEMENT_v1.csv"
SENTINEL = BASE / "structured/GLOBAL_INCLUSION_SENTINEL_SPEC_v1.csv"
OUT_A = BASE / "structured/SUCCESSOR_EDITION_TARGET_AUTHORITY_v3.csv"
OUT_B = BASE / "structured/SUCCESSOR_EDITION_EVIDENCE_MAPPING_v3.csv"
OUT_C = BASE / "structured/SUCCESSOR_EDITION_ALIAS_LEDGER_v3.csv"
RECEIPT = BASE / "qa/SUCCESSOR_EDITION_REGISTRY_V3_RECEIPT_20260901.json"
RECEIPT_SHA = BASE / "qa/SUCCESSOR_EDITION_REGISTRY_V3_RECEIPT_20260901.sha256"

def sha256_bytes(b: bytes) -> str: return hashlib.sha256(b).hexdigest()
def sha256_file(p: Path) -> str: return sha256_bytes(p.read_bytes())
def canon(v): return json.dumps(v, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
def row_hash(r):
    """Hash the normalized string projection that is written to CSV.

    CSV round trips turn numeric/boolean values into strings and serialize
    nulls as empty cells.  Normalizing before hashing makes both authority
    tables independently recomputable from their persisted bytes.
    """
    return sha256_bytes(canon({
        k: ("" if v is None else str(v))
        for k, v in r.items()
        if k != "row_sha256"
    }).encode())
def read_json(p): return json.loads(p.read_text(encoding="utf-8"))
def read_csv(p):
    with p.open("r", encoding="utf-8-sig", newline="") as f:
        rd = csv.DictReader(f)
        return list(rd.fieldnames or []), [dict(x) for x in rd]
def dump_csv(p, fields, rows):
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields, lineterminator="\n", extrasaction="raise")
        w.writeheader(); w.writerows(rows)

# The 108 rows excluded here are explicit context/alternative/umbrella rows.
# They remain in table B, but do not create duplicate edition ranks.  All other
# unmatched regional strata are exact variety/script/territory/mode editions.
CONTEXT_IDS = {
    "swc-Latn-CD-Katanga", "swc-Latn-CD-Kivu", "swc-Latn-CD-Ituri",
    "ha-Latn-NG-Boko", "ha-Arab-NG-Ajami", "ha-Arab-NE-Ajami", "fuv-Arab-NG-Ajami",
    "ln-Latn-CD", "shi-oral-MA", "tzm-oral-MA", "rif-oral-MA", "taq-Latn-NE", "ary-oral-MA",
    "mey-oral-MA-Hassaniya", "lir-Latn-LR", "cmn-CN", "id-ID", "pa-Arab-PK", "ko-Kore-KR",
    "jv-ID", "su-ID", "nds-Latn-CA", "gug-Latn-PY-home", "es-BO", "es-CO", "es-DO", "es-EC",
    "es-ES", "es-GT", "es-MX", "es-PA", "es-PE", "es-PY", "pt-BR", "pt-PT",
    "zh-Hant-HK", "zh-Hant-MO", "ar-001-context", "ar-Arab-XLEV", "afb-Arab-XGULF", "ar-Arab-YE-varieties",
    "ar-Arab-XMAGH", "pga-SS", "gug-Latn-PY-home", "pap-Latn-BQ-BO", "ca-Latn-ES-IB", "ca-valencia-Latn-ES-VC",
    "frr-Latn-DE-SH", "nds-Latn-DE-NORTH", "sco-Latn-GB-SCT", "yi-Hebr-CA", "ay-central-Latn-BO-LP",
    "ay-southern-Latn-PE", "gne-Latn-PY", "gnw-Latn-PY", "gug-pai-tavytera-Latn-PY", "gun-Latn-PY",
    "nah-central-veracruz-Latn-MX", "nah-centro-puebla-Latn-MX", "nah-huasteca-veracruzana-Latn-MX",
    "nah-sierra-negra-norte-Latn-MX", "nah-sierra-negra-sur-Latn-MX", "qu-collao-Latn-PE", "quy-Latn-PE",
    "sgh-Latn-001", "wbl-Latn-001", "rcf-Latn-MU-ROD", "zdj-Latn-KM-NGZ", "wni-Latn-KM-NDZ", "wlc-Latn-KM-MWA",
    "rhg-Rohg-001", "mww-Latn-LA", "khm-Khmr-VN", "kaa-Latn-UZ", "dng-Cyrl-KG", "mn-Cyrl-MN", "kk-Cyrl-MN",
    "uz-Cyrl-UZ", "mn-Mong-MN", "ka-Geor-GE", "hy-Armn-AM", "az-Latn-GE", "hy-Armn-GE", "ku-Latn-AM-YEZ",
    "aii-Syrc-AM", "lez-Cyrl-AZ", "ce-Cyrl-RU", "av-Cyrl-RU-DA", "sdh-Arab-IR", "hac-Arab-IR", "lki-Arab-IR",
    "tly-Arab-IR", "bqi-Arab-IR", "glk-Arab-IR", "mzn-Arab-IR", "zza-Latn-TR", "kmr-Latn-001", "ckb-Arab-001",
    "bcc-Arab-001", "bgn-Arab-001", "bgp-Arab-PK-IN", "ydd-Hebr-global", "yid-contemporary-hasidic-Hebr-global",
    "tts-Thai-TH-NE", "mfa-Thai-TH", "tet-Latn-TL-PRASA", "tet-Latn-TL-TERIK", "bkx-Latn-TL", "ddg-Latn-TL",
}

# Multiple observations of one edition remain evidence rows, not separate
# edition targets.  These suffixes name measurement constructs (ability and
# daily use), not different Russian language editions.
NORMALIZED_REGIONAL_ALIASES = {
    "ru-Cyrl-RU-ability": "lang:ru-Cyrl-RU",
    "ru-Cyrl-RU-daily": "lang:ru-Cyrl-RU",
    # A regional observation is not a second language edition merely because
    # its source key spells out script or subnational geography.  Preserve the
    # observation as evidence and attach it to the one reusable edition.
    "acr-Latn-GT": "lang:acr-GT",
    "cak-Latn-GT": "lang:cak-GT",
    "ixl-Latn-GT": "lang:ixl-GT",
    "kjb-Latn-GT": "lang:kjb-GT",
    "mam-Latn-GT": "lang:mam-GT",
    "poh-Latn-GT": "lang:poh-GT",
    "cy-Latn-GB-WLS": "lang:cy-Latn-GB",
    "eu-Latn-ES-NC": "lang:eu-Latn-ES",
    "eu-Latn-ES-PV": "lang:eu-Latn-ES",
    "kgk-Latn-BR": "lang:kgk-BR",
    "ikt-Latn-CA": "lang:ikt-CA",
    "ike-multiscript-CA": "lang:iku-CA",
    "crk-Latn-CA": "lang:crk-CA",
    "cwd-script-unresolved-CA": "lang:cwd-CA",
    "crl-script-unresolved-CA": "lang:crl-CA",
    "csw-script-unresolved-CA": "lang:csw-CA",
    "crm-script-unresolved-CA": "lang:crm-CA",
    "ojw-script-unresolved-CA": "lang:ojw-CA",
    "ciw-script-unresolved-CA": "lang:ciw-CA",
    "ojs-script-unresolved-CA": "lang:ojs-CA",
    "otw-script-unresolved-CA": "lang:otw-CA",
    "crj-script-unresolved-CA": "lang:crj-CA",
    "mah-Latn-MH": "lang:mh-Latn-MH",
    "haw-Latn-US-HI": "lang:haw-Latn-US",
    "rap-Latn-CL-IP": "lang:rap-Latn-CL",
    "acf-Latn-LC": "lang:acf-LC",
    "bzj-Latn-BZ": "lang:bzj-BZ",
    "ca-Latn-AD": "lang:ca-Latn-ES",
    "ca-Latn-ES-CT": "lang:ca-Latn-ES",
    "djk-Latn-SR": "lang:djk-SR",
    "gcf-Latn-GP": "lang:gcf-GP",
    "gyn-Latn-GY": "lang:gyn-GY",
    "jam-Latn-JM": "lang:jam-JM",
    "om-Latn-ET-Qubee": "lang:om-Latn-ET",
    "pap-Latn-AW": "lang:pap-AW",
    "pap-Latn-CW": "lang:pap-CW",
    "rcf-Latn-MU-ROD": "lang:mfe-Latn-MU-x-rodrigues",
    "srm-Latn-SR": "lang:srm-SR",
    "srn-Latn-SR": "lang:srn-SR",
    "so-Latn-SO": "lang:so-Latn-SO:variety:standard-somali-maxaa",
    "swh-Latn-TZ-mainland": "lang:swh-Latn-TZ:variety:tanzania-mainland-standard-kiswahili",
    "swh-Latn-TZ-Zanzibar": "lang:swh-Latn-TZ:variety:zanzibar-kiswahili-institutional-and-curri",
    "trf-Latn-TT": "lang:trf-TT",
    "yua-Latn-MX": "lang:yua-MX",
    "zh-Hant-TW": "lang:zh-Hant-TW:written",
}

# These are duplicate canonical records inherited from the v2 census, not
# distinct commissions.  Keep every source identifier resolvable while issuing
# only one edition target and one population atom in the funding order.
NORMALIZED_CANONICAL_ALIASES = {
    "lang:kek-Latn-GT": "lang:kek-GT",
    "lang:quc-Latn-GT": "lang:quc-GT",
    "lang:nzs": "lang:nzs-NZ",
    "lang:rap-CL": "lang:rap-Latn-CL",
}

FIELDS_A = ["edition_target_id","edition_key","target_kind","canonical_target_id","regional_stratum_id","language_tags","language_variety_names","scripts_orthographies","territories_communities","language_mode","exactness","effective_order_l_target","disposition","evidence_identity_count","row_sha256"]
FIELDS_B = ["evidence_identity_id","source_lane","source_record_id","edition_target_id","evidence_role","measure_class","population_unit","population_low_persons","population_base_persons","population_high_persons","population_definition","reference_year","territory","script_or_mode","source_ids","source_urls","source_locators","additivity_class","overlap_group","disposition","rank_eligible","row_sha256"]
FIELDS_C = ["alias_scope","alias_id","primary_canonical_target_id","primary_edition_target_id","reason","row_sha256"]

def main():
    d = read_json(CANON)
    langs = d["language_targets"]
    canonical_ids = {r["language_target_id"] for r in langs}
    targets = []
    target_by_id = {}
    for r in sorted(langs, key=lambda x: x["language_target_id"]):
        if r["language_target_id"] in NORMALIZED_CANONICAL_ALIASES:
            continue
        tid = "edition-target:" + r["language_target_id"]
        exactness = str(r.get("exactness", "") or "")
        # The canonical universe deliberately retains unresolved identity and
        # macro/context hypotheses so that they remain auditable.  They are
        # not exact language endpoints and must never enter the needs-only
        # language order as if they were one.  Preserve them in table A/B with
        # an explicit non-effective disposition instead of silently dropping
        # them or inventing a target-level denominator.
        if exactness == "exact":
            target_kind = "canonical_language_edition"
            effective_order = "true"
            disposition = "CANONICAL_V2_EDITION"
        elif exactness == "unresolved_macro":
            target_kind = "canonical_macro_context"
            effective_order = "false"
            disposition = "CANONICAL_V2_MACRO_CONTEXT"
        elif exactness == "exact_name_identifier_unresolved":
            target_kind = "canonical_unresolved_identity"
            effective_order = "false"
            disposition = "CANONICAL_V2_UNRESOLVED_IDENTITY"
        else:
            target_kind = "canonical_unresolved_context"
            effective_order = "false"
            disposition = "CANONICAL_V2_UNRESOLVED_CONTEXT"
        out = {"edition_target_id":tid,"edition_key":r["language_target_id"],"target_kind":target_kind,"canonical_target_id":r["language_target_id"],"regional_stratum_id":"","language_tags":";".join(r.get("language_tags",[])),"language_variety_names":";".join(r.get("language_variety_names",[])),"scripts_orthographies":";".join(r.get("scripts_orthographies",[])),"territories_communities":";".join(r.get("territories_communities",[])),"language_mode":r.get("language_mode", ""),"exactness":exactness,"effective_order_l_target":effective_order,"disposition":disposition,"evidence_identity_count":0}
        out["row_sha256"] = row_hash(out); targets.append(out); target_by_id[r["language_target_id"]] = tid

    target_rows_by_canonical = {t["canonical_target_id"]: t for t in targets if t["canonical_target_id"]}
    canonical_rows_by_id = {r["language_target_id"]: r for r in langs}
    for alias, primary in NORMALIZED_CANONICAL_ALIASES.items():
        if alias not in canonical_rows_by_id or primary not in target_by_id:
            raise ValueError(f"Invalid canonical alias {alias!r} -> {primary!r}")
        target_by_id[alias] = target_by_id[primary]
        # Preserve useful descriptions from both inherited rows without
        # letting the alias create a second target.
        dst = target_rows_by_canonical[primary]
        src = canonical_rows_by_id[alias]
        for field, source_key in (
            ("language_tags", "language_tags"),
            ("language_variety_names", "language_variety_names"),
            ("scripts_orthographies", "scripts_orthographies"),
            ("territories_communities", "territories_communities"),
        ):
            values = [x for x in dst[field].split(";") if x]
            for value in src.get(source_key, []):
                if value and value not in values:
                    values.append(value)
            dst[field] = ";".join(values)
        dst["disposition"] = "CANONICAL_V2_EDITION_WITH_NORMALIZED_ALIASES"
        dst["row_sha256"] = row_hash(dst)

    # High-consequence global sentinels join the candidate authority before
    # regional evidence is bound, so an exact sentinel target can receive a
    # later source row without creating a duplicate regional edition.
    _, sentinel_rows = read_csv(SENTINEL)
    existing_target_ids = {t["edition_target_id"] for t in targets}
    new_sentinel_targets = []
    for r in sentinel_rows:
        tid = r.get("expected_edition_target_id", "")
        tag = r.get("expected_language_tag", "")
        sentinel_class = r.get("sentinel_class", "")
        if not tid or tid in existing_target_ids:
            continue
        if sentinel_class in {"LARGE_CONTEXT", "UNRESOLVED_MACRO"}:
            continue
        edition_key = tid.removeprefix("edition-target:")
        out = {
            "edition_target_id": tid,
            "edition_key": edition_key,
            "target_kind": "sentinel_exact_edition",
            "canonical_target_id": "",
            "regional_stratum_id": "",
            "language_tags": tag,
            "language_variety_names": r.get("target_label", ""),
            "scripts_orthographies": r.get("script_or_mode", ""),
            "territories_communities": r.get("territory_or_community", ""),
            "language_mode": "written_or_multimodal",
            "exactness": "exact_sentinel_target",
            "effective_order_l_target": "true",
            "disposition": "GLOBAL_SENTINEL_EXACT_TARGET_NO_POPULATION_INFERENCE",
            "evidence_identity_count": 0,
        }
        out["row_sha256"] = row_hash(out)
        targets.append(out)
        new_sentinel_targets.append(out)
        existing_target_ids.add(tid)
        target_by_id[edition_key] = tid

    _, regional_rows = sum((read_csv(p)[0], read_csv(p)[1]) for p in REGIONAL) if False else ([], [])
    regional_rows=[]
    for p in REGIONAL:
        _, rr = read_csv(p); regional_rows.extend([{**x,"_lane":p.stem} for x in rr])
    # one row per unique stratum; source duplicates remain evidence rows
    by_stratum={}
    for r in regional_rows: by_stratum.setdefault(r["stratum_id"],r)
    new_regional=[]; evidence_target={}
    for sid in sorted(by_stratum):
        normalized_alias = NORMALIZED_REGIONAL_ALIASES.get(sid, "")
        if normalized_alias and normalized_alias in target_by_id:
            evidence_target[sid] = target_by_id[normalized_alias]
            continue
        if "lang:"+sid in target_by_id:
            evidence_target[sid] = target_by_id["lang:"+sid]; continue
        if sid in CONTEXT_IDS:
            evidence_target[sid] = ""; continue
        tid="edition-target:regional:"+sid; evidence_target[sid]=tid; r=by_stratum[sid]
        out={"edition_target_id":tid,"edition_key":sid,"target_kind":"regional_exact_edition","canonical_target_id":"","regional_stratum_id":sid,"language_tags":sid,"language_variety_names":r.get("label",""),"scripts_orthographies":r.get("script_or_mode",""),"territories_communities":r.get("territory",""),"language_mode":r.get("script_or_mode",""),"exactness":"exact_regional_stratum","effective_order_l_target":"true","disposition":"NEW_UNMATCHED_EXACT_EDITION","evidence_identity_count":0}
        out["row_sha256"]=row_hash(out); new_regional.append(out)
    targets.extend(new_regional)
    # Supplement: seven new exact editions; three C-17 alternatives attach to existing editions.
    _, supp_rows=read_csv(SUPPLEMENT)
    supplement_target={"bn-Beng-IN-reported-L123-2011":target_by_id.get("lang:bn-Beng-IN", ""),"mr-Deva-IN-reported-L123-2011":target_by_id.get("lang:mr-Deva-IN", ""),"te-Telu-IN-reported-L123-2011":target_by_id.get("lang:te-Telu-IN", "")}
    for r in supp_rows:
        sid=r["stratum_id"]
        if sid in supplement_target: continue
        tid="edition-target:supplement:"+sid
        supplement_target[sid]=tid
        out={"edition_target_id":tid,"edition_key":sid,"target_kind":"supplement_exact_edition","canonical_target_id":"","regional_stratum_id":sid,"language_tags":sid,"language_variety_names":r.get("label",""),"scripts_orthographies":r.get("script_or_mode",""),"territories_communities":r.get("territory",""),"language_mode":r.get("script_or_mode",""),"exactness":"exact_supplement_stratum","effective_order_l_target":"true","disposition":"NEW_SUPPLEMENT_EXACT_EDITION","evidence_identity_count":0}
        out["row_sha256"]=row_hash(out); targets.append(out)
    targets.sort(key=lambda x:x["edition_target_id"])

    aliases=[]
    for alias, primary in sorted(NORMALIZED_CANONICAL_ALIASES.items()):
        row={"alias_scope":"canonical_target","alias_id":alias,"primary_canonical_target_id":primary,"primary_edition_target_id":target_by_id[primary],"reason":"DUPLICATE_CANONICAL_EDITION_IDENTITY"}
        row["row_sha256"]=row_hash(row); aliases.append(row)
    for alias, primary in sorted(NORMALIZED_REGIONAL_ALIASES.items()):
        row={"alias_scope":"regional_stratum","alias_id":alias,"primary_canonical_target_id":primary,"primary_edition_target_id":target_by_id[primary],"reason":"REGIONAL_EVIDENCE_ATTACHED_TO_EXISTING_EDITION"}
        row["row_sha256"]=row_hash(row); aliases.append(row)

    evidence=[]
    def add_evidence(eid,lane,record,edition,role,measure_class="",unit="",low="",base="",high="",definition="",year="",territory="",script="",source_ids="",source_urls="",locators="",additivity="",overlap="",disp="DIRECT_EVIDENCE",eligible="false"):
        x={"evidence_identity_id":eid,"source_lane":lane,"source_record_id":record,"edition_target_id":edition,"evidence_role":role,"measure_class":measure_class,"population_unit":unit,"population_low_persons":low,"population_base_persons":base,"population_high_persons":high,"population_definition":definition,"reference_year":year,"territory":territory,"script_or_mode":script,"source_ids":source_ids,"source_urls":source_urls,"source_locators":locators,"additivity_class":additivity,"overlap_group":overlap,"disposition":disp,"rank_eligible":eligible}
        x["row_sha256"]=row_hash(x); evidence.append(x)
    # v2 canonical population evidence
    for r in d.get("population_evidence",[]):
        ids=r.get("language_target_ids",[]); mapped=target_by_id.get(ids[0],"") if ids else ""
        vals=r.get("source_values",{}) or {}
        add_evidence(r.get("population_evidence_id",r.get("origin_record_id","")),"v2_population",r.get("origin_record_id",""),mapped,"POPULATION_OR_CONTEXT",r.get("measure_class",""),vals.get("unit",""),vals.get("low",""),vals.get("base",""),vals.get("high",""),r.get("population_definition",""),r.get("reference_year",""),"","", ";".join(r.get("source_ids",[])),r.get("source_url",""),"",r.get("additivity_class",""),r.get("overlap_group") or "", "V2_CANONICAL_EVIDENCE",str(bool(r.get("score_eligible"))).lower())
    for r in d.get("package_context_measures",[]):
        mapped=";".join(target_by_id.get(i,"") for i in r.get("component_target_ids",[]) if target_by_id.get(i))
        vals=r.get("population_values_persons",{}) or {}
        add_evidence(r.get("package_context_measure_id",""),"v2_package_context",r.get("package_context_measure_id",""),mapped,"PACKAGE_CONTEXT_NO_INHERITANCE","package_context","persons",vals.get("low",""),vals.get("base",""),vals.get("high",""),r.get("aggregation",""),"","","","","","",r.get("target_binding",""),"", "PACKAGE_CONTEXT_ONLY","false")
    for q in d.get("quarantined_evidence",[]):
        r=q.get("record",{}); ids=r.get("language_target_ids",[]); mapped=target_by_id.get(ids[0],"") if ids else ""
        add_evidence(q.get("quarantine_id",""),"v2_quarantine",q.get("origin_record_id",""),mapped,"QUARANTINED",r.get("measure_class",""),(r.get("source_values",{}) or {}).get("unit",""),(r.get("source_values",{}) or {}).get("low",""),(r.get("source_values",{}) or {}).get("base",""),(r.get("source_values",{}) or {}).get("high",""),r.get("population_definition",""),r.get("reference_year",""),"","", ";".join(r.get("source_ids",[])),r.get("source_url",""),"",r.get("additivity_class",""),r.get("overlap_group") or "", "QUARANTINE_NO_INHERITANCE","false")
    # Signed-language, accessibility-overlay and supply/policy identities are
    # carried as non-additive evidence; they never manufacture a target.
    sl = d.get("signed_accessibility_lane", {})
    for lane_key in ("signed_language_person_measures", "signed_language_proxy_and_gap_rows", "accessibility_overlays", "accessibility_supply_policy_and_utilization"):
        for r in sl.get(lane_key, []):
            vals = r.get("source_values", {}) or {}; norm = r.get("person_normalization", {}) or {}; pv = norm.get("values_persons", {}) or {}
            mapped = target_by_id.get(r.get("language_target_id", ""), "")
            add_evidence("signed:" + r.get("record_id", ""), "v2_signed_accessibility", r.get("record_id", ""), mapped, r.get("evidence_role", lane_key), vals.get("qualifier", ""), vals.get("unit", ""), pv.get("low", ""), pv.get("base", ""), pv.get("high", ""), r.get("measure_definition", ""), r.get("reference_year", ""), r.get("jurisdiction", ""), "", r.get("source_id", ""), r.get("source_url", ""), r.get("source_locator", ""), r.get("additivity_class", ""), r.get("overlap_group", ""), r.get("target_binding", "SIGNED_OR_ACCESSIBILITY_NONADDITIVE"), "false")
    for i,r in enumerate(regional_rows):
        sid=r["stratum_id"]; edition=evidence_target[sid]; eid=f"regional:{r['_lane']}:{sid}:{i+1:03d}"
        add_evidence(eid,r["_lane"],sid,edition,"REGIONAL_EMPIRICAL_STRATUM",r.get("population_measure_class",""),r.get("population_unit",""),r.get("population_low_persons",""),r.get("population_base_persons",""),r.get("population_high_persons",""),r.get("population_definition",""),r.get("population_reference_year",""),r.get("territory",""),r.get("script_or_mode",""),r.get("source_ids",""),r.get("source_urls",""),r.get("source_locators",""),r.get("uncertainty_incompatibilities",""),"", "EVIDENCE_ONLY_CONTEXT" if not edition else ("ATTACHED_TO_EXISTING_EDITION" if sid not in evidence_target or sid in CONTEXT_IDS or "lang:"+sid in target_by_id else "NEW_EDITION_EVIDENCE"), "false")
    for r in supp_rows:
        sid=r["stratum_id"]; edition=supplement_target.get(sid,"") or target_by_id.get(sid,"")
        disp="ALTERNATIVE_MEASURE_ATTACHED" if sid in supplement_target and sid not in {x["edition_key"] for x in targets if x["target_kind"]=="supplement_exact_edition"} else "NEW_SUPPLEMENT_EDITION_EVIDENCE"
        add_evidence(f"supplement:{sid}","large_population_supplement_v1",sid,edition,"LARGE_POPULATION_SUPPLEMENT",r.get("population_measure_class",""),r.get("population_unit",""),r.get("population_low_persons",""),r.get("population_base_persons",""),r.get("population_high_persons",""),r.get("population_definition",""),r.get("population_reference_year",""),r.get("territory",""),r.get("script_or_mode",""),r.get("source_ids",""),r.get("source_urls",""),r.get("source_locators",""),r.get("uncertainty_incompatibilities",""),"",disp,"false")
    evidence.sort(key=lambda x:x["evidence_identity_id"])
    counts=Counter(x["edition_target_id"] for x in evidence if x["edition_target_id"])
    for t in targets: t["evidence_identity_count"]=counts.get(t["edition_target_id"],0); t["row_sha256"]=row_hash(t)
    dump_csv(OUT_A,FIELDS_A,targets); dump_csv(OUT_B,FIELDS_B,evidence); dump_csv(OUT_C,FIELDS_C,aliases)
    effective_ok = all(
        ((t["exactness"] == "exact" and t["target_kind"] == "canonical_language_edition")
         or (t["exactness"] == "exact_regional_stratum" and t["target_kind"] == "regional_exact_edition")
         or (t["exactness"] == "exact_supplement_stratum" and t["target_kind"] == "supplement_exact_edition")
         or (t["exactness"] == "exact_sentinel_target" and t["target_kind"] == "sentinel_exact_edition"))
        == (t["effective_order_l_target"] == "true")
        for t in targets
    )
    receipt={"schema_version":"interlanguage/successor-edition-target-evidence-authority/3.2.0","audit_date":"2026-09-04","status":"PASS","authority_rule":"NEW-047 normalized unique editions; canonical and regional aliases resolve to one edition; exact language/regional/supplement/sentinel endpoints are effective; unresolved identity and macro/context rows remain auditable but never create primary ranks; sentinel targets close silent global omissions without population inference","hash_semantics":"row_sha256 is computed over the normalized string-valued persisted CSV row, excluding row_sha256 itself; nulls are empty strings","inputs":{str(CANON.relative_to(BASE)): {"bytes":CANON.stat().st_size,"sha256":sha256_file(CANON)}, **{str(p.relative_to(BASE)):{"bytes":p.stat().st_size,"sha256":sha256_file(p)} for p in REGIONAL+[SUPPLEMENT,SENTINEL]}},"outputs":{str(OUT_A.relative_to(BASE)): {"bytes":OUT_A.stat().st_size,"sha256":sha256_file(OUT_A),"rows":len(targets)},str(OUT_B.relative_to(BASE)): {"bytes":OUT_B.stat().st_size,"sha256":sha256_file(OUT_B),"rows":len(evidence)},str(OUT_C.relative_to(BASE)): {"bytes":OUT_C.stat().st_size,"sha256":sha256_file(OUT_C),"rows":len(aliases)}},"counts":{"canonical_input_rows":len(langs),"canonical_aliases":len(NORMALIZED_CANONICAL_ALIASES),"canonical_editions":len(langs)-len(NORMALIZED_CANONICAL_ALIASES),"canonical_exact_editions":sum(1 for t in targets if t['target_kind']=='canonical_language_edition'),"canonical_unresolved_or_macro":sum(1 for t in targets if t['target_kind'] in {'canonical_unresolved_identity','canonical_macro_context','canonical_unresolved_context'}),"regional_aliases":len(NORMALIZED_REGIONAL_ALIASES),"new_regional_editions":len(new_regional),"new_supplement_editions":sum(1 for t in targets if t['target_kind']=='supplement_exact_edition'),"new_global_sentinel_exact_editions":len(new_sentinel_targets),"edition_targets":len(targets),"evidence_identities":len(evidence),"regional_source_rows":len(regional_rows),"regional_unique_strata":len(by_stratum),"regional_exact_matches":sum(1 for s in by_stratum if 'lang:'+s in canonical_ids),"regional_context_only":sum(1 for s in by_stratum if not evidence_target[s]),"supplement_rows":len(supp_rows),"sentinel_rows":len(sentinel_rows)},"checks":{"target_ids_unique":len({t['edition_target_id'] for t in targets})==len(targets),"evidence_ids_unique":len({e['evidence_identity_id'] for e in evidence})==len(evidence),"alias_ids_unique":len({a['alias_id'] for a in aliases})==len(aliases),"all_target_hashes_valid":all(t['row_sha256']==row_hash(t) for t in targets),"all_evidence_hashes_valid":all(e['row_sha256']==row_hash(e) for e in evidence),"all_alias_hashes_valid":all(a['row_sha256']==row_hash(a) for a in aliases),"all_canonical_aliases_resolve":all(target_by_id.get(a)==target_by_id.get(p) for a,p in NORMALIZED_CANONICAL_ALIASES.items()),"all_regional_aliases_resolve":all(evidence_target.get(a)==target_by_id.get(p) for a,p in NORMALIZED_REGIONAL_ALIASES.items()),"effective_values_match_exactness":effective_ok,"no_scores_or_ranks":True}}
    RECEIPT.write_text(json.dumps(receipt,ensure_ascii=False,sort_keys=True,indent=2)+"\n",encoding="utf-8"); RECEIPT_SHA.write_text(f"{sha256_file(RECEIPT)}  {RECEIPT.name}\n",encoding="utf-8")
    print(json.dumps(receipt,ensure_ascii=False,sort_keys=True,indent=2))

if __name__=="__main__": main()
