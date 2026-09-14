"""
01_data_preparation.py -- Harmonized analytical panel (Section 2.1).

Merges the two raw SSC RA source tables in data/raw/ into a single
district-year analytical panel, applies the listwise-deletion sample
restriction described in the manuscript (Section 2.1), and writes the
result to data/processed/.

Raw inputs (see docs/DATA_DESCRIPTION.md for full source-table
provenance):
    data/raw/ssc_ra_district_panel_long.csv   -- milk production, cattle
                                                  and combined cattle+
                                                  buffalo stock, fodder-
                                                  crop sown area (long
                                                  format, all Azerbaijan
                                                  regions/districts)
    data/raw/ssc_ra_land_use_002_2en.csv      -- total land in ownership/
                                                  use, by district-year
                                                  (SSC RA Table 002_2en)

Produces: data/processed/analytical_panel.csv
"""
import pandas as pd
import numpy as np
import _paths as p

# ---- Land-use table: wide-format government table -> long format ----
raw = pd.read_csv(p.DATA_RAW / "ssc_ra_land_use_002_2en.csv",
                   encoding="utf-8", header=None)
years_row = raw.iloc[3].tolist()
years = [str(y).strip() for y in years_row if pd.notna(y) and str(y).strip()]

land_records = []
for _, row in raw.iloc[4:].iterrows():
    name = str(row.iloc[1]).strip() if len(row) > 1 else ""
    if not name or name == "nan":
        continue
    for yi, y in enumerate(years):
        col_idx = 2 + yi
        if col_idx >= len(row):
            continue
        val = str(row.iloc[col_idx]).strip().replace(",", ".").replace(" ", "")
        if val in ("-", "", "...", "nan", "\u2026"):
            continue
        try:
            val = float(val)
        except ValueError:
            continue
        land_records.append({"region": name, "year": int(y), "land_total_ha": val})
land_df = pd.DataFrame(land_records)

# ---- District panel: long format (region, region_type, year, variable, value) ----
panel = pd.read_csv(p.DATA_RAW / "ssc_ra_district_panel_long.csv")
wide = panel.pivot_table(index=["region", "region_type", "year"],
                          columns="variable", values="value", aggfunc="first").reset_index()
districts = wide[wide["region_type"] == "district"].copy()

# ---- Merge and apply sample restriction (Section 2.1) ----
merged = districts.merge(land_df, on=["region", "year"], how="inner")

keep_cols = ["region", "year", p.FRONTIER_OUTPUT] + p.FRONTIER_INPUTS + \
            ["cows_dairy_buffaloes_stock_heads"]
analytical = merged[keep_cols].dropna().reset_index(drop=True)

numeric_cols = [p.FRONTIER_OUTPUT] + p.FRONTIER_INPUTS + ["cows_dairy_buffaloes_stock_heads"]
analytical[numeric_cols] = analytical[numeric_cols].apply(pd.to_numeric, errors="coerce")
analytical = analytical[(analytical[numeric_cols] > 0).all(axis=1)].reset_index(drop=True)

n_obs = len(analytical)
n_districts = analytical["region"].nunique()

print(f"Analytical panel: N = {n_obs} district-years, {n_districts} districts, "
      f"{analytical['year'].min()}-{analytical['year'].max()}")

assert n_obs == p.SAMPLE_N_DISTRICT_YEARS, \
    f"Expected N={p.SAMPLE_N_DISTRICT_YEARS}, got {n_obs}"
assert n_districts == p.SAMPLE_N_DISTRICTS, \
    f"Expected {p.SAMPLE_N_DISTRICTS} districts, got {n_districts}"
print("VERIFIED: matches manuscript Section 2.1 (N = 920 district-years, 59 districts).")

analytical.to_csv(p.DATA_PROCESSED / "analytical_panel.csv", index=False)
print(f"\nSaved: {p.DATA_PROCESSED / 'analytical_panel.csv'}")
