"""
08_leave_one_out_test.py -- Table S5 (Supporting Information).

Directly tests whether the reversal of OLS residual skewness that
identifies the post-conflict-district exclusion decision (Table S3) is
specific to those ten districts, or a generic consequence of removing
any ten districts from the sample.

  Panel A: excludes nine of the ten post-conflict districts, retaining
           the tenth, for each of the ten districts in turn.
  Panel B: excludes ten randomly selected non-post-conflict districts
           (200 independent draws).

Requires: 01_data_preparation.py to have been run first (uses the raw
merged panel directly, not the TE-augmented file, since only the OLS
residual skewness of the frontier specification is needed here).

Produces: output/TableS5_leave_one_out_random_exclusion.csv
"""
import numpy as np
import pandas as pd
from scipy.stats import skew
import _paths as p

panel = pd.read_csv(p.DATA_RAW / "ssc_ra_district_panel_long.csv")
wide = panel.pivot_table(index=["region", "region_type", "year"],
                          columns="variable", values="value", aggfunc="first").reset_index()
districts = wide[wide["region_type"] == "district"].copy()

land = pd.read_csv(p.DATA_RAW / "ssc_ra_land_use_002_2en.csv", encoding="utf-8", header=None)
years_row = land.iloc[3].tolist()
years = [str(y).strip() for y in years_row if pd.notna(y) and str(y).strip()]
land_records = []
for _, row in land.iloc[4:].iterrows():
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
merged = districts.merge(land_df, on=["region", "year"], how="inner")


def skew_excluding(exclude_list, data):
    sub = data[~data["region"].isin(exclude_list)]
    sub = sub[[p.FRONTIER_OUTPUT] + p.FRONTIER_INPUTS].dropna()
    sub = sub[(sub.apply(pd.to_numeric) > 0).all(axis=1)].reset_index(drop=True)
    N = len(sub)
    y = np.log(sub[p.FRONTIER_OUTPUT].values)
    X = np.column_stack([np.ones(N)] + [np.log(sub[c].values) - np.log(sub[c].values).mean()
                                          for c in p.FRONTIER_INPUTS])
    beta = np.linalg.lstsq(X, y, rcond=None)[0]
    resid = y - X @ beta
    return skew(resid), N


# ---- Panel A: leave-one-out within the post-conflict set ----
print("Panel A: retaining one post-conflict district (excluding the other nine)")
panel_a_rows = []
for keep in p.POST_CONFLICT_DISTRICTS:
    exclude_nine = [d for d in p.POST_CONFLICT_DISTRICTS if d != keep]
    sk, N = skew_excluding(exclude_nine, merged)
    panel_a_rows.append({"district_retained": keep.replace(" district", ""),
                          "OLS_residual_skewness": round(sk, 3)})
    print(f"  Retaining {keep:25s}: skewness = {sk:+.3f}")

# ---- Panel B: random exclusion of ten non-post-conflict districts ----
all_districts = merged["region"].unique()
non_pc = [d for d in all_districts if d not in p.POST_CONFLICT_DISTRICTS]
rng = np.random.default_rng(p.RANDOM_EXCLUSION_SEED)
random_skews = []
for _ in range(p.RANDOM_EXCLUSION_DRAWS):
    draw = rng.choice(non_pc, size=10, replace=False)
    sk, N = skew_excluding(list(draw), merged)
    random_skews.append(sk)
random_skews = np.array(random_skews)

print(f"\nPanel B: random exclusion of 10 non-post-conflict districts "
      f"({p.RANDOM_EXCLUSION_DRAWS} draws)")
print(f"  Mean skewness   = {random_skews.mean():.3f}")
print(f"  Minimum         = {random_skews.min():.3f}")
print(f"  Maximum         = {random_skews.max():.3f}")
print(f"  95th percentile = {np.percentile(random_skews, 95):.3f}")
print(f"  99th percentile = {np.percentile(random_skews, 99):.3f}")
print(f"  Draws with positive skewness: {(random_skews > 0).sum()} / {p.RANDOM_EXCLUSION_DRAWS}")

# Actual post-conflict exclusion skewness (Table S3), for comparison
sk_actual, _ = skew_excluding(p.POST_CONFLICT_DISTRICTS, merged)
print(f"\n  For comparison, actual post-conflict-set exclusion skewness: {sk_actual:+.3f}")

assert round(random_skews.max(), 3) <= -1.06, "A random draw approached the actual post-conflict skewness"
assert (random_skews > 0).sum() == 0
assert round(sk_actual, 2) == 0.52
print("\nVERIFIED: matches manuscript Table S5 -- no random 10-district exclusion reproduces "
      "the post-conflict set's skewness reversal.")

panel_b_summary = pd.DataFrame([
    {"statistic": "Mean skewness", "value": round(random_skews.mean(), 3)},
    {"statistic": "Minimum", "value": round(random_skews.min(), 3)},
    {"statistic": "Maximum", "value": round(random_skews.max(), 3)},
    {"statistic": "95th percentile", "value": round(np.percentile(random_skews, 95), 3)},
    {"statistic": "99th percentile", "value": round(np.percentile(random_skews, 99), 3)},
    {"statistic": "Draws with positive skewness", "value": f"{(random_skews > 0).sum()} / {p.RANDOM_EXCLUSION_DRAWS}"},
])

pd.DataFrame(panel_a_rows).to_csv(p.OUTPUT / "TableS5_panelA_leave_one_out.csv", index=False)
panel_b_summary.to_csv(p.OUTPUT / "TableS5_panelB_random_exclusion.csv", index=False)
print(f"\nSaved: {p.OUTPUT / 'TableS5_panelA_leave_one_out.csv'}")
print(f"Saved: {p.OUTPUT / 'TableS5_panelB_random_exclusion.csv'}")
