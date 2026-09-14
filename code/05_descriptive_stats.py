"""
05_descriptive_stats.py -- Table 1.

Descriptive statistics for the full analytical sample (Panel A) and
the sample excluding the ten post-conflict districts (Panel B).

Requires: 04_emission_intensity.py to have been run first.

Produces: output/Table1_descriptive_statistics.csv
"""
import pandas as pd
import _paths as p

df = pd.read_csv(p.DATA_PROCESSED / "analytical_panel_with_emissions.csv")

varlist = [
    ("milk_production_tons", "Milk production (tons)"),
    ("cows_heads", "Dairy cattle stock (head)"),
    ("cows_dairy_buffaloes_stock_heads", "Combined cattle+buffalo stock (head)"),
    ("fodder_sown_area_ha", "Fodder-crop sown area (ha)"),
    ("land_total_ha", "Total land in use (ha)"),
    ("yield_combined", "Milk yield (kg head-1 yr-1)"),
    ("TE", "Technical efficiency (TE)"),
    ("CH4_intensity", "CH4 intensity (kg CH4/kg milk)"),
]


def panel_stats(sub, label):
    rows = []
    for col, name in varlist:
        s = sub[col]
        rows.append({
            "panel": label, "variable": name,
            "mean": round(s.mean(), 3), "sd": round(s.std(), 3),
            "min": round(s.min(), 3), "max": round(s.max(), 3),
        })
    return rows


panel_a = panel_stats(df, f"Panel A: Full sample (N={len(df)}; {df['region'].nunique()} districts)")
excl = df[~df["region"].isin(p.POST_CONFLICT_DISTRICTS)]
panel_b = panel_stats(excl, f"Panel B: Excl. post-conflict (N={len(excl)}; {excl['region'].nunique()} districts)")

out = pd.DataFrame(panel_a + panel_b)
print(out.to_string(index=False))

# Spot-check key manuscript-reported values (Table 1)
te_row_a = [r for r in panel_a if r["variable"] == "Technical efficiency (TE)"][0]
ch4_row_a = [r for r in panel_a if r["variable"] == "CH4 intensity (kg CH4/kg milk)"][0]
te_row_b = [r for r in panel_b if r["variable"] == "Technical efficiency (TE)"][0]
ch4_row_b = [r for r in panel_b if r["variable"] == "CH4 intensity (kg CH4/kg milk)"][0]

assert len(df) == 920 and df["region"].nunique() == 59
assert len(excl) == 832 and excl["region"].nunique() == 49
assert te_row_a["mean"] == 0.776
assert ch4_row_a["max"] == 0.745
assert te_row_b["min"] == 0.537
assert ch4_row_b["max"] == 0.092
print("\nVERIFIED: matches manuscript Table 1 (Panel A/B all spot-checked values).")

out.to_csv(p.OUTPUT / "Table1_descriptive_statistics.csv", index=False)
print(f"\nSaved: {p.OUTPUT / 'Table1_descriptive_statistics.csv'}")
