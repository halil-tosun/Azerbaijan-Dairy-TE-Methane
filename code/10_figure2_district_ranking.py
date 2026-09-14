"""
10_figure2_district_ranking.py -- Figure 2.

Ten districts with the highest and ten with the lowest sample-period
mean technical efficiency, with each district's mean CH4 intensity
shown on a secondary axis.

Requires: 04_emission_intensity.py to have been run first.

Produces: figures/Figure2_District_ranking.png
"""
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from matplotlib.lines import Line2D
import _paths as p

plt.rcParams.update({"font.size": 10, "font.family": "DejaVu Sans"})

df = pd.read_csv(p.DATA_PROCESSED / "analytical_panel_with_emissions.csv")
df["pc"] = df["region"].isin(p.POST_CONFLICT_DISTRICTS)

dist_means = df.groupby("region").agg(TE=("TE", "mean"), CH4=("CH4_intensity", "mean"),
                                        pc=("pc", "max")).reset_index()
top10 = dist_means.nlargest(10, "TE").sort_values("TE")
bot10 = dist_means.nsmallest(10, "TE").sort_values("TE")
combo = pd.concat([bot10, top10])

fig, ax1 = plt.subplots(figsize=(7.5, 6))
y_pos = np.arange(len(combo))
colors = ["#c0392b" if pc else "#1b4965" for pc in combo["pc"]]
ax1.barh(y_pos, combo["TE"], color=colors, height=0.6, alpha=0.85)
ax1.set_yticks(y_pos)
ax1.set_yticklabels([r.replace(" district", "") for r in combo["region"]], fontsize=8)
ax1.set_xlabel("Mean technical efficiency (TE)")
ax1.axhline(9.5, color="black", linewidth=0.8, linestyle="--")
ax1.set_xlim(0, 1)

ax2 = ax1.twiny()
ax2.plot(combo["CH4"].values, y_pos, "o", color="black", markersize=5)
ax2.set_xlabel("Mean CH4 intensity (kg CH4/kg milk)")

legend_elems = [Patch(facecolor="#1b4965", label="TE (non-post-conflict)"),
                Patch(facecolor="#c0392b", label="TE (post-conflict)"),
                Line2D([0], [0], marker="o", color="black", linestyle="", label="Mean CH4 intensity")]
ax1.legend(handles=legend_elems, loc="lower right", frameon=False, fontsize=8)
ax1.text(0.5, 9.7, "Bottom 10", fontsize=8, style="italic")
ax1.text(0.5, 19.3, "Top 10", fontsize=8, style="italic")

plt.tight_layout()
plt.savefig(p.FIGURES / "Figure2_District_ranking.png", dpi=300)
plt.close()
print(f"Saved: {p.FIGURES / 'Figure2_District_ranking.png'}")
print(f"Top TE district: {top10.iloc[-1]['region']} ({top10.iloc[-1]['TE']:.3f})")
print(f"Bottom TE district: {bot10.iloc[0]['region']} ({bot10.iloc[0]['TE']:.3f})")

assert bot10.iloc[0]["region"] == "Aghdara district"
print("VERIFIED: matches manuscript Figure 2 (lowest-TE district = Aghdara).")
