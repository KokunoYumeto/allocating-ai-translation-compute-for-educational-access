from __future__ import annotations

import csv
import json
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
SOURCES = ROOT / "sources"
UIS = SOURCES / "uis_202602"
WB_API = SOURCES / "world_bank_api"
OUT_LONG = ROOT / "COUNTRY_EVIDENCE_LONG.csv"
OUT_WIDE = ROOT / "COUNTRY_CONTEXT.csv"


UIS_INDICATORS = {
    "CR.1": "primary_completion_pct",
    "CR.2": "lower_secondary_completion_pct",
    "CR.3": "upper_secondary_completion_pct",
    "ROFST.MOD.1": "primary_out_of_school_pct",
    "ROFST.MOD.2": "lower_secondary_out_of_school_pct",
    "ROFST.MOD.3": "upper_secondary_out_of_school_pct",
    "READ.PRIMARY": "end_primary_reading_minimum_pct",
    "READ.LOWERSEC": "end_lower_secondary_reading_minimum_pct",
    "MATH.PRIMARY": "end_primary_math_minimum_pct",
    "MATH.LOWERSEC": "end_lower_secondary_math_minimum_pct",
    "GER.5T8": "tertiary_gross_enrolment_pct",
    "LR.AG15T24": "youth_literacy_pct",
    "LR.AG15T99": "adult_literacy_pct",
}

DEM_INDICATORS = {
    "200101": "population_total_thousands",
    "200144": "population_15_24_thousands",
    "200151": "population_65_plus_thousands",
    "200343": "population_0_14_thousands",
    "200345": "population_25_64_thousands",
}

WB_INDICATORS = {
    "SP.POP.TOTL": "wb_population_total",
    "IT.NET.USER.ZS": "internet_users_pct",
    "EG.ELC.ACCS.ZS": "electricity_access_pct",
    "IT.CEL.SETS.P2": "mobile_subscriptions_per_100",
    "SE.ADT.LITR.ZS": "wb_adult_literacy_pct",
    "SE.SEC.ENRR": "wb_secondary_gross_enrolment_pct",
    "SE.TER.ENRR": "wb_tertiary_gross_enrolment_pct",
    "SP.URB.TOTL.IN.ZS": "urban_population_pct",
}

LP_INDICATORS = {
    "SE.LPV.PRIM": "learning_poverty_pct",
    "SE.LPV.PRIM.LD": "learning_deprivation_pct",
    "SE.LPV.PRIM.SD": "learning_poverty_schooling_deprivation_pct",
    "SE.LPV.POP.10": "population_age_10",
    "SE.LPV.POP.PRIM": "population_primary_age",
}


def latest_per_key(frame: pd.DataFrame, key_cols: list[str], year_col: str) -> pd.DataFrame:
    frame = frame.copy()
    frame[year_col] = pd.to_numeric(frame[year_col], errors="coerce")
    frame = frame.dropna(subset=[year_col, "value"])
    frame = frame.sort_values(key_cols + [year_col], kind="stable")
    return frame.groupby(key_cols, as_index=False, sort=True).tail(1)


def read_uis() -> pd.DataFrame:
    country = pd.read_csv(UIS / "SDG_COUNTRY.csv", dtype=str)
    country_cols = list(country.columns)
    if len(country_cols) < 2:
        raise ValueError("UIS country table has fewer than two columns")
    country = country.rename(columns={country_cols[0]: "country_code", country_cols[1]: "country_name"})
    country = country[["country_code", "country_name"]].drop_duplicates()

    chunks: list[pd.DataFrame] = []
    use = set(UIS_INDICATORS)
    for chunk in pd.read_csv(
        UIS / "SDG_DATA_NATIONAL.csv",
        dtype={"INDICATOR_ID": str, "COUNTRY_ID": str, "MAGNITUDE": str, "QUALIFIER": str},
        chunksize=400_000,
        low_memory=False,
    ):
        part = chunk[chunk["INDICATOR_ID"].isin(use)].copy()
        if not part.empty:
            chunks.append(part)
    data = pd.concat(chunks, ignore_index=True)
    data = data.rename(columns={"INDICATOR_ID": "indicator_id", "COUNTRY_ID": "country_code", "YEAR": "year", "VALUE": "value", "QUALIFIER": "qualifier"})
    data["value"] = pd.to_numeric(data["value"], errors="coerce")
    data = latest_per_key(data, ["country_code", "indicator_id"], "year")
    data = data.merge(country, on="country_code", how="left", validate="many_to_one")
    data["field"] = data["indicator_id"].map(UIS_INDICATORS)
    data["source_id"] = "UIS-SDG-2026-02"
    data["source_url"] = "https://download.uis.unesco.org/bdds/202602/SDG.zip"
    data["source_note"] = data["qualifier"].fillna("").astype(str)
    return data[["country_code", "country_name", "field", "value", "year", "source_id", "source_url", "source_note"]]


def read_dem() -> pd.DataFrame:
    country = pd.read_csv(UIS / "DEM_COUNTRY.csv", dtype=str)
    cols = list(country.columns)
    country = country.rename(columns={cols[0]: "country_code", cols[1]: "country_name"})[["country_code", "country_name"]].drop_duplicates()
    chunks: list[pd.DataFrame] = []
    for chunk in pd.read_csv(UIS / "DEM_DATA_NATIONAL.csv", dtype={"INDICATOR_ID": str, "COUNTRY_ID": str}, chunksize=250_000):
        part = chunk[chunk["INDICATOR_ID"].isin(DEM_INDICATORS)].copy()
        if not part.empty:
            chunks.append(part)
    data = pd.concat(chunks, ignore_index=True)
    data = data.rename(columns={"INDICATOR_ID": "indicator_id", "COUNTRY_ID": "country_code", "YEAR": "year", "VALUE": "value"})
    data["value"] = pd.to_numeric(data["value"], errors="coerce")
    data = latest_per_key(data, ["country_code", "indicator_id"], "year")
    data = data.merge(country, on="country_code", how="left", validate="many_to_one")
    data["field"] = data["indicator_id"].map(DEM_INDICATORS)
    data["source_id"] = "UIS-DEM-2026-02"
    data["source_url"] = "https://download.uis.unesco.org/bdds/202602/DEM.zip"
    data["source_note"] = "Values are thousands of persons."
    return data[["country_code", "country_name", "field", "value", "year", "source_id", "source_url", "source_note"]]


def read_wb_api() -> pd.DataFrame:
    rows: list[dict] = []
    for indicator, field in WB_INDICATORS.items():
        payload = json.loads((WB_API / f"{indicator}.json").read_text(encoding="utf-8-sig"))
        if not isinstance(payload, list) or len(payload) < 2:
            raise ValueError(f"Unexpected World Bank payload for {indicator}")
        for item in payload[1]:
            value = item.get("value")
            code = item.get("countryiso3code")
            if value is None or not code or len(code) != 3:
                continue
            rows.append(
                {
                    "country_code": code,
                    "country_name": item.get("country", {}).get("value", ""),
                    "field": field,
                    "value": value,
                    "year": item.get("date"),
                    "source_id": f"WB-{indicator}",
                    "source_url": f"https://api.worldbank.org/v2/country/all/indicator/{indicator}?format=json&per_page=20000",
                    "source_note": "Latest non-null country value selected; aggregates excluded after UIS-country join.",
                }
            )
    data = pd.DataFrame(rows)
    data["value"] = pd.to_numeric(data["value"], errors="coerce")
    return latest_per_key(data, ["country_code", "field"], "year")


def read_learning_poverty() -> pd.DataFrame:
    path = SOURCES / "WORLD_BANK_LEARNING_POVERTY_2024.xlsx"
    data = pd.read_excel(path, sheet_name="WDI_indicators", dtype={"countrycode": str, "indicator": str})
    data = data[(data["cty_or_agg"] == "cty") & data["indicator"].isin(LP_INDICATORS)].copy()
    data = data.rename(columns={"countrycode": "country_code", "countryname": "country_name", "indicator": "indicator_id"})
    data["field"] = data["indicator_id"].map(LP_INDICATORS)
    data["value"] = pd.to_numeric(data["value"], errors="coerce")
    data = latest_per_key(data, ["country_code", "field"], "year")
    data["source_id"] = "WORLD-BANK-LEARNING-POVERTY-2024"
    data["source_url"] = "https://datacatalog.worldbank.org/search/dataset/0038947/learning-poverty-global-database-historical-data-and-sub-components"
    data["source_note"] = data["value_metadata"].fillna("").astype(str)
    return data[["country_code", "country_name", "field", "value", "year", "source_id", "source_url", "source_note"]]


def main() -> None:
    uis = read_uis()
    dem = read_dem()
    wb = read_wb_api()
    lp = read_learning_poverty()

    valid_codes = set(pd.read_csv(UIS / "SDG_COUNTRY.csv", dtype=str).iloc[:, 0].astype(str))
    combined = pd.concat([uis, dem, wb, lp], ignore_index=True)
    combined = combined[combined["country_code"].isin(valid_codes)].copy()
    combined = combined.sort_values(["country_code", "field", "year"], kind="stable")
    combined.to_csv(OUT_LONG, index=False, quoting=csv.QUOTE_MINIMAL, lineterminator="\n")

    id_cols = combined[["country_code", "country_name"]].dropna().drop_duplicates("country_code")
    wide_values = combined.pivot_table(index="country_code", columns="field", values="value", aggfunc="last")
    wide_years = combined.pivot_table(index="country_code", columns="field", values="year", aggfunc="last").add_suffix("__year")
    wide = id_cols.set_index("country_code").join(wide_values, how="outer").join(wide_years, how="outer").reset_index()
    wide = wide.sort_values("country_code", kind="stable")
    wide.to_csv(OUT_WIDE, index=False, quoting=csv.QUOTE_MINIMAL, lineterminator="\n")

    print(json.dumps({
        "long_rows": int(len(combined)),
        "countries": int(combined["country_code"].nunique()),
        "fields": int(combined["field"].nunique()),
        "wide_rows": int(len(wide)),
        "out_long": str(OUT_LONG),
        "out_wide": str(OUT_WIDE),
    }, indent=2))


if __name__ == "__main__":
    main()
