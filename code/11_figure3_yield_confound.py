"""
11_figure3_yield_confound.py -- Figure 3.

Two-panel figure: (a) raw, unconditional binned association between
technical efficiency and CH4 intensity, full sample; (b) the same
association after both variables are residualized on log(combined-herd
milk yield), post-conflict districts excluded.

Requires: 04_emission_intensity.py to have been run first.

Produces: figures/Figure3_yield_confound.png
"""
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import _paths as p

plt.rcParams.update({"font.size": 10, "font.family": "DejaVu Sans"})

df = pd.read_csv(p.DATA_PROCESSED / "analytical_panel_with_emissions.csv")
df["pc"] = df["region"].isin(p.POST_CONFLICT_DISTRICTS)


def bin_plot(ax, x, y, nbins=8, color="#1b4965"):
    d = pd.DataFrame({"x": x, "y": y}).dropna()
    d["bin"] = pd.qcut(d["x"], nbins, duplicates="drop")
    means = d.groupby("bin", observed=True).agg(
        xm=("x", "mean"), ym=("y", "mean"), yse=("y", lambda v: v.std() / np.sqrt(len(v))))
    ax.errorbar(means["xm"], means["ym"], yerr=1.96 * means["yse"], fmt="o-",
                color=color, capsize=3, markersize=5, linewidth=1.5)


fig, axes = plt.subplots(1, 2, figsize=(9.5, 4))

def residualize(y, x):
    X = np.column_stack([np.ones(len(x)), x])
    beta = np.linalg.lstsq(X, y, rcond=None)[0]
    return y - X @ beta


# Panel (a): raw, full sample
r_raw = np.corrcoef(df["TE"], df["CH4_intensity"])[0, 1]
rho_raw = pd.Series(df["TE"]).corr(pd.Series(df["CH4_intensity"]), method="spearman")
bin_plot(axes[0], df["TE"], df["CH4_intensity"], color="#1b4965")
axes[0].set_xlabel("Technical efficiency (TE), binned deciles")
axes[0].set_ylabel(r"Mean CH$_4$ intensity (kg CH$_4$/kg milk)")
axes[0].set_title(f"(a) Raw association, full sample\n(N={len(df)})", fontsize=10)
axes[0].grid(alpha=0.3)

# Full-sample yield-netted correlation and variance-explained checks (Results 3.3)
log_yield_full = np.log(df["yield_combined"].values)
TE_resid_full = residualize(df["TE"].values, log_yield_full)
CH4_resid_full = residualize(df["CH4_intensity"].values, log_yield_full)
r_full_netted = np.corrcoef(TE_resid_full, CH4_resid_full)[0, 1]

Xr = np.column_stack([np.ones(len(df)), log_yield_full])
beta_te = np.linalg.lstsq(Xr, df["TE"].values, rcond=None)[0]
r2_te = 1 - np.sum((df["TE"].values - Xr @ beta_te) ** 2) / np.sum((df["TE"].values - df["TE"].values.mean()) ** 2)
beta_ch4 = np.linalg.lstsq(Xr, df["CH4_intensity"].values, rcond=None)[0]
r2_ch4 = 1 - np.sum((df["CH4_intensity"].values - Xr @ beta_ch4) ** 2) / np.sum((df["CH4_intensity"].values - df["CH4_intensity"].values.mean()) ** 2)

# Panel (b): yield-netted, excl. post-conflict
excl = df[~df["pc"]].copy()


log_yield = np.log(excl["yield_combined"].values)
TE_resid = residualize(excl["TE"].values, log_yield)
CH4_resid = residualize(excl["CH4_intensity"].values, log_yield)
r_resid = np.corrcoef(TE_resid, CH4_resid)[0, 1]

bin_plot(axes[1], TE_resid, CH4_resid, color="#c0392b")
axes[1].set_xlabel("TE residual (net of log-yield)")
axes[1].set_ylabel(r"CH$_4$ intensity residual (net of log-yield)")
axes[1].set_title(f"(b) Yield-netted association,\nexcl. post-conflict (N={len(excl)})", fontsize=10)
axes[1].grid(alpha=0.3)
axes[1].axhline(0, color="gray", linewidth=0.7)
axes[1].axvline(0, color="gray", linewidth=0.7)

plt.tight_layout()
plt.savefig(p.FIGURES / "Figure3_yield_confound.png", dpi=300)
plt.close()

print(f"Panel (a) raw Pearson r = {r_raw:.3f}, Spearman rho = {rho_raw:.3f}")
print(f"Full-sample yield-netted Pearson r = {r_full_netted:.3f}")
print(f"R2 of TE ~ log(yield) = {r2_te:.3f}")
print(f"R2 of CH4Int ~ log(yield) = {r2_ch4:.3f}")
print(f"Panel (b) yield-netted (excl. post-conflict) Pearson r = {r_resid:.3f}")
print(f"Saved: {p.FIGURES / 'Figure3_yield_confound.png'}")

assert round(r_raw, 2) == -0.61
assert round(rho_raw, 2) == -0.82
assert round(r_full_netted, 2) == -0.04
assert round(r2_te, 2) == 0.80
assert round(r2_ch4, 2) == 0.45
assert round(r_resid, 2) == -0.27
print("VERIFIED: matches corrected manuscript Section 3.3 / Figure 3 in full "
      "(raw r=-0.61, rho=-0.82; R2_TE=80%, R2_CH4=45%; full-sample yield-netted r=-0.04; "
      "excl.-post-conflict yield-netted r=-0.27).")
