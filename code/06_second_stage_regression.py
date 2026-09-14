"""
06_second_stage_regression.py -- Table 3.

Second-stage regression of CH4 intensity on technical efficiency (Eq.
7), three specifications: (1) full sample with a post-conflict
intercept dummy, (2) excl. post-conflict without year fixed effects,
(3) excl. post-conflict with year fixed effects (primary
specification). District-clustered standard errors (Cameron & Miller,
2015 small-sample correction) throughout; the primary specification is
additionally checked by wild-cluster (Rademacher) bootstrap.

Requires: 04_emission_intensity.py to have been run first.

Produces: output/Table3_second_stage_regression.csv
"""
import numpy as np
import pandas as pd
from scipy.stats import t as tdist
import _paths as p

df = pd.read_csv(p.DATA_PROCESSED / "analytical_panel_with_emissions.csv")
df["log_yield"] = np.log(df["yield_combined"])
df["post_conflict"] = df["region"].isin(p.POST_CONFLICT_DISTRICTS).astype(float)


def cluster_ols(data, xcols, ycol="CH4_intensity", cluster_col="region"):
    y = data[ycol].values
    X = np.column_stack([np.ones(len(data))] + [data[c].values for c in xcols])
    n, k = X.shape
    XtX_inv = np.linalg.inv(X.T @ X)
    beta = XtX_inv @ X.T @ y
    resid = y - X @ beta
    clusters = data[cluster_col].values
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
    tstat = beta / se
    pval = 2 * (1 - tdist.cdf(np.abs(tstat), df=G - 1))
    r2 = 1 - np.sum(resid ** 2) / np.sum((y - y.mean()) ** 2)
    return beta, se, tstat, pval, n, G, r2, X, resid


rows = []

# ---- Column 1: full sample + post-conflict dummy + year FE ----
year_dum = pd.get_dummies(df["year"], prefix="yr", drop_first=True).astype(float)
d1 = pd.concat([df[["region", "CH4_intensity", "TE", "log_yield", "post_conflict"]], year_dum], axis=1)
xcols1 = ["TE", "log_yield", "post_conflict"] + list(year_dum.columns)
beta1, se1, t1, pv1, n1, g1, r2_1, _, _ = cluster_ols(d1, xcols1)
print(f"Column 1 (full + dummy + year FE): TE = {beta1[1]:.4f} (SE {se1[1]:.4f}), "
      f"p = {pv1[1]:.4f}, N={n1}, G={g1}, R2={r2_1:.3f}")

# ---- Column 2/3: exclude post-conflict districts ----
excl = df[~df["region"].isin(p.POST_CONFLICT_DISTRICTS)].reset_index(drop=True)

beta2, se2, t2, pv2, n2, g2, r2_2, _, _ = cluster_ols(excl, ["TE", "log_yield"])
print(f"Column 2 (excl. PC, no year FE): TE = {beta2[1]:.4f} (SE {se2[1]:.4f}), "
      f"p = {pv2[1]:.4f}, N={n2}, G={g2}, R2={r2_2:.3f}")

year_dum2 = pd.get_dummies(excl["year"], prefix="yr", drop_first=True).astype(float)
d3 = pd.concat([excl[["region", "CH4_intensity", "TE", "log_yield"]], year_dum2], axis=1)
xcols3 = ["TE", "log_yield"] + list(year_dum2.columns)
beta3, se3, t3, pv3, n3, g3, r2_3, X3, resid3 = cluster_ols(d3, xcols3)
print(f"Column 3 (excl. PC + year FE, PRIMARY): TE = {beta3[1]:.4f} (SE {se3[1]:.4f}), "
      f"p = {pv3[1]:.4f}, N={n3}, G={g3}, R2={r2_3:.3f}")

assert round(beta1[1], 4) == -0.0234 or round(beta1[1], 3) == -0.023
assert round(beta2[1], 4) == -0.0353
assert round(beta3[1], 3) == -0.029
print("\nVERIFIED: matches manuscript Table 3 (all three columns).")

# ---- Wild-cluster (Rademacher) bootstrap for the primary specification ----
clusters3 = d3["region"].values
uniq3 = np.unique(clusters3)
G3 = len(uniq3)

X_null = np.column_stack([np.ones(n3)] + [d3["log_yield"].values] +
                          [d3[c].values for c in list(year_dum2.columns)])
beta_null = np.linalg.lstsq(X_null, d3["CH4_intensity"].values, rcond=None)[0]
fitted_null = X_null @ beta_null
resid_null = d3["CH4_intensity"].values - fitted_null

rng = np.random.default_rng(p.WILD_BOOTSTRAP_SEED)
t_obs = t3[1]
t_boot = np.zeros(p.WILD_BOOTSTRAP_REPLICATIONS)
for b in range(p.WILD_BOOTSTRAP_REPLICATIONS):
    w = rng.choice([-1.0, 1.0], size=G3)
    w_map = dict(zip(uniq3, w))
    w_vec = np.array([w_map[c] for c in clusters3])
    y_star = fitted_null + resid_null * w_vec
    d3_star = d3.copy()
    d3_star["CH4_intensity"] = y_star
    beta_b, se_b, t_b, _, _, _, _, _, _ = cluster_ols(d3_star, xcols3)
    t_boot[b] = t_b[1]

p_wild = np.mean(np.abs(t_boot) >= np.abs(t_obs))
print(f"\nWild-cluster bootstrap (B={p.WILD_BOOTSTRAP_REPLICATIONS}): p = {p_wild:.4f}")
assert round(p_wild, 3) == 0.024
print("VERIFIED: matches manuscript (wild-cluster-bootstrap p = 0.024).")

out = pd.DataFrame([
    {"specification": "(1) Full sample + PC dummy", "TE_coef": round(beta1[1], 4), "SE": round(se1[1], 4),
     "p": round(pv1[1], 4), "N": n1, "districts": g1, "R2": round(r2_1, 3), "year_FE": "Yes"},
    {"specification": "(2) Excl. PC, no year FE", "TE_coef": round(beta2[1], 4), "SE": round(se2[1], 4),
     "p": round(pv2[1], 4), "N": n2, "districts": g2, "R2": round(r2_2, 3), "year_FE": "No"},
    {"specification": "(3) Excl. PC + year FE (primary)", "TE_coef": round(beta3[1], 4), "SE": round(se3[1], 4),
     "p": round(pv3[1], 4), "N": n3, "districts": g3, "R2": round(r2_3, 3), "year_FE": "Yes",
     "wild_bootstrap_p": round(p_wild, 4)},
])
out.to_csv(p.OUTPUT / "Table3_second_stage_regression.csv", index=False)
print(f"\nSaved: {p.OUTPUT / 'Table3_second_stage_regression.csv'}")
