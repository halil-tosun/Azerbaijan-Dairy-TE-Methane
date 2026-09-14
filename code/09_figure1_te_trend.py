"""
09_figure1_te_trend.py -- Figure 1.

Mean technical efficiency by year, non-post-conflict vs. post-conflict
districts, with a sub-panel reporting the number of post-conflict
districts contributing data in each year.

Requires: 02_sfa_frontier_estimation.py to have been run first.

Produces: figures/Figure1_TE_trend.png
"""
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import _paths as p

plt.rcParams.update({"font.size": 10, "font.family": "DejaVu Sans"})

df = pd.read_csv(p.DATA_PROCESSED / "analytical_panel_with_TE.csv")
df["pc"] = df["region"].isin(p.POST_CONFLICT_DISTRICTS)

g = df.groupby(["year", "pc"])["TE"].mean().unstack()
n_pc = df[df["pc"]].groupby("year").size()

fig, (ax, ax2) = plt.subplots(2, 1, figsize=(6.5, 5.2), gridspec_kw={"height_ratios": [3, 1]}, sharex=True)

ax.plot(g.index, g[False], marker="o", markersize=4, linewidth=1.8, color="#1b4965", label="Non-post-conflict districts")
ax.plot(g.index, g[True], marker="s", markersize=4, linewidth=1.8, color="#c0392b", label="Post-conflict districts")
ax.set_ylabel("Mean technical efficiency (TE)")
ax.set_ylim(0, 1)
ax.legend(loc="lower right", frameon=False, fontsize=9)
ax.grid(alpha=0.3)

ax2.bar(n_pc.index, n_pc.values, color="#c0392b", alpha=0.75, width=0.6)
ax2.set_ylabel("N districts\n(post-conflict)", fontsize=8)
ax2.set_xlabel("Year")
ax2.set_ylim(0, 10)
ax2.set_yticks([0, 5, 10])
ax2.axhline(10, color="gray", linewidth=0.6, linestyle=":")
ax2.grid(alpha=0.3, axis="y")
for spine in ("top", "right"):
    ax2.spines[spine].set_visible(False)

plt.tight_layout()
plt.savefig(p.FIGURES / "Figure1_TE_trend.png", dpi=300)
plt.close()
print(f"Saved: {p.FIGURES / 'Figure1_TE_trend.png'}")
print(f"2024 non-PC mean TE = {g.loc[2024, False]:.3f}, 2024 PC mean TE = {g.loc[2024, True]:.3f} "
      f"(N={int(n_pc.loc[2024])} contributing districts)")
