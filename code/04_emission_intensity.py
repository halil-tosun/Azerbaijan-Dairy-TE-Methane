"""
04_emission_intensity.py -- Enteric methane emission intensity (Eq. 5-6).

Constructs the yield-interpolated IPCC (2006) Tier 1 emission factor
and the resulting district-year enteric methane emission intensity
(CH4Int), using the combined dairy-cattle-and-buffalo stock as the
denominator (manuscript Section 2.1, 2.4). Also computes the
cattle-only-denominator version used in the Table 4 robustness check.

Requires: 02_sfa_frontier_estimation.py to have been run first.

Produces: data/processed/analytical_panel_with_emissions.csv
"""
import numpy as np
import pandas as pd
import _paths as p

df = pd.read_csv(p.DATA_PROCESSED / "analytical_panel_with_TE.csv")

yields_ref = np.array([pair[0] for pair in p.IPCC_DAIRY_YIELD_EF_PAIRS])
efs_ref = np.array([pair[1] for pair in p.IPCC_DAIRY_YIELD_EF_PAIRS])


def ef_interp(yield_kg):
    """Eq. 6. Linear interpolation across IPCC (2006, Table 10.11)
    regional (yield, EF) reference pairs; out-of-range values are
    boundary-clamped (numpy default), not extrapolated (manuscript
    Section 2.4)."""
    return np.interp(yield_kg, yields_ref, efs_ref)


# ---- Combined cattle+buffalo denominator (primary; Eq. 5-6) ----
df["yield_combined"] = df["milk_production_tons"] * 1000 / df["cows_dairy_buffaloes_stock_heads"]
df["EF_combined"] = ef_interp(df["yield_combined"].values)
df["CH4_intensity"] = df["EF_combined"] * df["cows_dairy_buffaloes_stock_heads"] / (df["milk_production_tons"] * 1000)

# ---- Cattle-only denominator (Table 4 robustness comparison) ----
df["yield_cattle_only"] = df["milk_production_tons"] * 1000 / df["cows_heads"]
df["EF_cattle_only"] = ef_interp(df["yield_cattle_only"].values)
df["CH4_intensity_cattle_only"] = df["EF_cattle_only"] * df["cows_heads"] / (df["milk_production_tons"] * 1000)

print(f"Mean CH4 intensity (combined-stock denominator): {df['CH4_intensity'].mean():.4f} "
      f"(range [{df['CH4_intensity'].min():.4f}, {df['CH4_intensity'].max():.4f}])")
print(f"Mean yield (combined-stock denominator): {df['yield_combined'].mean():.1f} kg head-1 yr-1")

assert round(df["CH4_intensity"].mean(), 3) == 0.050
assert round(df["yield_combined"].mean(), 1) == 1514.7
assert round(df["CH4_intensity"].max(), 3) == 0.745
print("VERIFIED: matches manuscript Table 1 (mean CH4 intensity = 0.050, mean yield = 1,514.7, max = 0.745).")

df.to_csv(p.DATA_PROCESSED / "analytical_panel_with_emissions.csv", index=False)
print(f"\nSaved: {p.DATA_PROCESSED / 'analytical_panel_with_emissions.csv'}")
