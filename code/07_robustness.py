"""
07_robustness.py -- Table 4.

Five robustness checks on the primary TE coefficient (Table 3, Column
3): cattle-only denominator, low-buffalo-share subsample, and +/-30-50%
IPCC Tier 1 uncertainty bounds. All specifications use the primary
model (excl. post-conflict districts, year fixed effects,
district-clustered SE).

Requires: 04_emission_intensity.py to have been run first.

Produces: output/Table4_robustness.csv
"""
import numpy as np
import pandas as pd
from scipy.stats import t as tdist
import _paths as p

df = pd.read_csv(p.DATA_PROCESSED / "analytical_panel_with_emissions.csv")
df["log_yield"] = np.log(df["yield_combined"])
df["log_yield_cattle_only"] = np.log(df["yield_cattle_only"])
excl = df[~df["region"].isin(p.POST_CONFLICT_DISTRICTS)].reset_index(drop=True)


def primary_spec_te(data, ycol, xcol_yield):
    year_dum = pd.get_dummies(data["year"], prefix="yr", drop_first=True).astype(float)
    y = data[ycol].values
    X = np.column_stack([np.ones(len(data)), data["TE"].values, data[xcol_yield].values,
                          *[year_dum[c].values for c in year_dum.columns]])
    n, k = X.shape
    XtX_inv = np.linalg.inv(X.T @ X)
    beta = XtX_inv @ X.T @ y
    resid = y - X @ beta
    clusters = data["region"].values
    uniq = np.unique(clusters)
    G = len(uniq)
    meat = np.zeros((k, k))
    for c in uniq:
        idx = clusters == c
        score = X[idx].T @ resid[idx]
        meat += np.outer(score, score)
    corr = (G / (G - 1)) * ((n - 1) / (n - k))
    V = corr * XtX_inv @ meat @ XtX_inv
    se = np.sqrt(np.diag(V))
    t_te, se_te = beta[1] / se[1], se[1]
    p_te = 2 * (1 - tdist.cdf(np.abs(t_te), df=G - 1))
    return beta[1], se_te, p_te, n, G


rows = []

b, se, pv, n, g = primary_spec_te(excl, "CH4_intensity", "log_yield")
rows.append({"specification": "Primary (combined cattle+buffalo denom.)",
             "TE_coef": round(b, 4), "SE": round(se, 4), "p": round(pv, 3), "N": n, "districts": g})
print(f"Primary: TE={b:.4f} (SE {se:.4f}), p={pv:.3f}")

b, se, pv, n, g = primary_spec_te(excl, "CH4_intensity_cattle_only", "log_yield_cattle_only")
rows.append({"specification": "Cattle-only denominator (uncorrected)",
             "TE_coef": round(b, 4), "SE": round(se, 4), "p": round(pv, 3), "N": n, "districts": g})
print(f"Cattle-only denom.: TE={b:.4f} (SE {se:.4f}), p={pv:.3f}")

excl_lb = excl.copy()
excl_lb["buffalo_share"] = 1 - excl_lb["cows_heads"] / excl_lb["cows_dairy_buffaloes_stock_heads"]
low_buf = excl_lb[excl_lb["buffalo_share"] < 0.05].reset_index(drop=True)
b, se, pv, n, g = primary_spec_te(low_buf, "CH4_intensity", "log_yield")
rows.append({"specification": "Low-buffalo-share (<5%) subsample",
             "TE_coef": round(b, 4), "SE": round(se, 4), "p": round(pv, 3), "N": n, "districts": g})
print(f"Low-buffalo-share subsample: TE={b:.4f} (SE {se:.4f}), p={pv:.3f}, N={n}")

for label, mult in [("IPCC Tier 1 lower bound (-30% EF)", p.IPCC_TIER1_UNCERTAINTY_LOW),
                     ("IPCC Tier 1 upper bound (+50% EF)", p.IPCC_TIER1_UNCERTAINTY_HIGH)]:
    excl_scaled = excl.copy()
    excl_scaled["CH4_intensity"] = excl_scaled["CH4_intensity"] * mult
    b, se, pv, n, g = primary_spec_te(excl_scaled, "CH4_intensity", "log_yield")
    rows.append({"specification": label, "TE_coef": round(b, 4), "SE": round(se, 4),
                 "p": round(pv, 3), "N": n, "districts": g})
    print(f"{label}: TE={b:.4f} (SE {se:.4f}), p={pv:.3f}")

out = pd.DataFrame(rows)
print("\n" + out.to_string(index=False))

assert round(out.loc[0, "TE_coef"], 3) == -0.029
assert round(out.loc[1, "TE_coef"], 4) == -0.0334
assert round(out.loc[2, "TE_coef"], 4) == -0.0423
assert out.loc[2, "N"] == 411 and out.loc[2, "districts"] == 36
assert out.loc[2, "p"] > 0.05
assert round(out.loc[3, "TE_coef"], 4) == -0.0202
assert round(out.loc[4, "TE_coef"], 4) == -0.0433
print("\nVERIFIED: matches manuscript Table 4 (all five specifications).")

out.to_csv(p.OUTPUT / "Table4_robustness.csv", index=False)
print(f"\nSaved: {p.OUTPUT / 'Table4_robustness.csv'}")
