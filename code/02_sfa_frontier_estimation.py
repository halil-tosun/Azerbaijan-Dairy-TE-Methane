"""
02_sfa_frontier_estimation.py -- Table 2.

Estimates the Cobb-Douglas and translog stochastic frontier production
functions (manuscript Eq. 1-4) by maximum likelihood (Nelder-Mead
simplex search, refined by BFGS), recovers district-year technical
efficiency scores via the Jondrow et al. (1982) conditional-mean
estimator in its Battese and Coelli (1988) multiplicative form, and
tests the Cobb-Douglas restriction by likelihood-ratio test.

Requires: 01_data_preparation.py to have been run first.

Produces:
    output/Table2_sfa_estimation_results.csv
    data/processed/analytical_panel_with_TE.csv  (adds a TE column,
        used by every downstream script)
"""
import numpy as np
import pandas as pd
from scipy.optimize import minimize
from scipy.stats import norm, chi2
import _paths as p

df = pd.read_csv(p.DATA_PROCESSED / "analytical_panel.csv")
N = len(df)

y = np.log(df[p.FRONTIER_OUTPUT].values)
lx = {c: np.log(df[c].values) for c in p.FRONTIER_INPUTS}
lxc = {c: lx[c] - lx[c].mean() for c in p.FRONTIER_INPUTS}  # mean-centered


def build_design(kind):
    ones = np.ones(N)
    c1, c2, c3 = (lxc[c] for c in p.FRONTIER_INPUTS)
    if kind == "cd":
        X = np.column_stack([ones, c1, c2, c3])
        names = ["Constant", "ln(Cows)", "ln(Fodder)", "ln(Land)"]
    else:
        X = np.column_stack([
            ones, c1, c2, c3,
            0.5 * c1**2, 0.5 * c2**2, 0.5 * c3**2,
            c1 * c2, c1 * c3, c2 * c3,
        ])
        names = ["Constant", "ln(Cows)", "ln(Fodder)", "ln(Land)",
                  "0.5 ln(Cows)^2", "0.5 ln(Fodder)^2", "0.5 ln(Land)^2",
                  "ln(Cows)*ln(Fodder)", "ln(Cows)*ln(Land)", "ln(Fodder)*ln(Land)"]
    return X, names


def negloglik(theta, X):
    k = X.shape[1]
    beta, log_sigma2, lam = theta[:k], theta[k], theta[k + 1]
    sigma2 = np.exp(log_sigma2)
    sigma = np.sqrt(sigma2)
    eps = y - X @ beta
    z = -eps * lam / sigma
    ll = (-0.5 * np.log(2 * np.pi) - 0.5 * log_sigma2
          + np.log(2) + norm.logcdf(z) - 0.5 * (eps ** 2) / sigma2)
    return -np.sum(ll)


def numerical_hessian(f, x0, h=1e-4):
    n = len(x0)
    H = np.zeros((n, n))
    for i in range(n):
        for j in range(i, n):
            xpp, xpm, xmp, xmm = (x0.copy() for _ in range(4))
            xpp[i] += h; xpp[j] += h
            xpm[i] += h; xpm[j] -= h
            xmp[i] -= h; xmp[j] += h
            xmm[i] -= h; xmm[j] -= h
            H[i, j] = (f(xpp) - f(xpm) - f(xmp) + f(xmm)) / (4 * h * h)
            H[j, i] = H[i, j]
    return H


results = {}
for kind in ("cd", "translog"):
    X, names = build_design(kind)
    k = X.shape[1]
    beta_ols = np.linalg.lstsq(X, y, rcond=None)[0]
    resid = y - X @ beta_ols
    x0 = np.concatenate([beta_ols, [np.log(np.var(resid)), 1.0]])

    res = minimize(negloglik, x0, args=(X,), method="Nelder-Mead",
                    options={"maxiter": 30000, "xatol": 1e-9, "fatol": 1e-9})
    res = minimize(negloglik, res.x, args=(X,), method="BFGS")
    theta = res.x
    logL = -res.fun

    H = numerical_hessian(lambda th: negloglik(th, X), theta)
    se = np.sqrt(np.diag(np.linalg.inv(H)))

    beta, log_sigma2, lam = theta[:k], theta[k], theta[k + 1]
    sigma2 = np.exp(log_sigma2)
    sigma = np.sqrt(sigma2)
    sigma_u = lam * sigma / np.sqrt(1 + lam ** 2)
    sigma_v = sigma / np.sqrt(1 + lam ** 2)
    gamma = sigma_u ** 2 / sigma2

    results[kind] = dict(X=X, names=names, beta=beta, se=se, theta=theta,
                          logL=logL, sigma_u=sigma_u, sigma_v=sigma_v, gamma=gamma)
    print(f"\n=== {kind.upper()} ===  logL={logL:.3f}  sigma_u={sigma_u:.4f}  "
          f"sigma_v={sigma_v:.4f}  gamma={gamma:.4f}")
    for nm, b, s in zip(names, beta, se):
        print(f"  {nm:22s} {b: .4f}  (SE {s:.4f})")

LR = 2 * (results["translog"]["logL"] - results["cd"]["logL"])
df_lr = len(results["translog"]["names"]) - len(results["cd"]["names"])
p_lr = 1 - chi2.cdf(LR, df_lr)
print(f"\nLR test (translog vs. Cobb-Douglas): LR = {LR:.2f}, df = {df_lr}, p = {p_lr:.6f}")

assert round(LR, 2) == 59.91, f"Expected LR=59.91, got {LR:.2f}"
assert round(results["translog"]["gamma"], 3) == 0.656
assert round(results["cd"]["gamma"], 3) == 0.642
print("VERIFIED: matches manuscript Table 2 (LR = 59.91, translog gamma = 0.656).")

# ---- Recover translog technical efficiency (Jondrow et al., 1982 / Battese & Coelli, 1988) ----
tl = results["translog"]
X, beta = tl["X"], tl["beta"]
theta = tl["theta"]
log_sigma2, lam = theta[len(beta)], theta[len(beta) + 1]
sigma2 = np.exp(log_sigma2)
sigma = np.sqrt(sigma2)
eps = y - X @ beta
mu_star = -eps * sigma2 * 0  # placeholder overwritten below for clarity
mu_star = -eps * (tl["sigma_u"] ** 2) / sigma2
sigma_star = tl["sigma_u"] * tl["sigma_v"] / sigma
E_u = mu_star + sigma_star * (norm.pdf(mu_star / sigma_star) / norm.cdf(mu_star / sigma_star))
TE = np.exp(-E_u)

df["TE"] = TE
print(f"\nMean TE = {TE.mean():.3f} (SD {TE.std():.3f}), range [{TE.min():.3f}, {TE.max():.3f}]")
assert round(TE.mean(), 3) == 0.776, f"Expected mean TE=0.776, got {TE.mean():.3f}"
print("VERIFIED: matches manuscript Table 1 (mean TE = 0.776).")

# ---- Save Table 2 ----
rows = []
for kind, label in (("cd", "Cobb-Douglas"), ("translog", "Translog")):
    r = results[kind]
    for nm, b, s in zip(r["names"], r["beta"], r["se"]):
        rows.append({"specification": label, "variable": nm, "coef": round(b, 4), "se": round(s, 4)})
    rows.append({"specification": label, "variable": "sigma_u", "coef": round(r["sigma_u"], 4), "se": ""})
    rows.append({"specification": label, "variable": "sigma_v", "coef": round(r["sigma_v"], 4), "se": ""})
    rows.append({"specification": label, "variable": "gamma", "coef": round(r["gamma"], 4), "se": ""})
    rows.append({"specification": label, "variable": "log-likelihood", "coef": round(r["logL"], 3), "se": ""})
    rows.append({"specification": label, "variable": "N", "coef": N, "se": ""})
pd.DataFrame(rows).to_csv(p.OUTPUT / "Table2_sfa_estimation_results.csv", index=False)
df.to_csv(p.DATA_PROCESSED / "analytical_panel_with_TE.csv", index=False)
print(f"\nSaved: {p.OUTPUT / 'Table2_sfa_estimation_results.csv'}")
print(f"Saved: {p.DATA_PROCESSED / 'analytical_panel_with_TE.csv'}")
