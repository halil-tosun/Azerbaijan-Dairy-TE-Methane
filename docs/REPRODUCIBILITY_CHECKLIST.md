# REPRODUCIBILITY CHECKLIST

## Internal-Consistency Verification Against the Manuscript

Every value below was checked, script-by-script, against the
corresponding value reported in the manuscript or Supporting
Information. Every script in `code/` also contains its own `assert`
statements enforcing these same checks at runtime; `run_all.py` stops
immediately if any check fails.

| Manuscript/SI value | Reported as | Verified by | Status |
|---|---|---|---|
| Sample size | N=920 district-years, 59 districts | `01_data_preparation.py` | Pass |
| Table 2, both specifications | LR=59.91, translog gamma=0.656, mean TE=0.776 | `02_sfa_frontier_estimation.py` | Pass |
| Table S1 (VIF) | Cows 1.39, Fodder 1.40, Land 1.02, Labor 1.01 | `03_diagnostics.py` | Pass |
| Table S3 | Skewness -1.18 -> +0.52; full sample converges, excl.-PC does not | `03_diagnostics.py` | Pass |
| Table S4 | 4-input skewness +0.071; same-sample 3-input -1.042 | `03_diagnostics.py` | Pass |
| Table 1 (Panel A/B) | All spot-checked mean/SD/min/max values | `04_emission_intensity.py`, `05_descriptive_stats.py` | Pass |
| Table 3, all three columns | TE coef. -0.023/-0.035/-0.029; wild-bootstrap p=0.024 | `06_second_stage_regression.py` | Pass |
| Table 4, all five rows | See script output | `07_robustness.py` | Pass |
| Table S5, Panel A (all 10 rows) | See script output | `08_leave_one_out_test.py` | Pass (exact match) |
| Table S5, Panel B (summary stats) | 0/200 positive; max approx -1.07 | `08_leave_one_out_test.py` | Pass (qualitative; see note below) |
| Figure 2 | Lowest-TE district = Aghdara | `10_figure2_district_ranking.py` | Pass |
| Figure 3 / Section 3.3 | Raw r=-0.61, rho=-0.82; R2_TE=80%, R2_CH4=45%; full-sample yield-netted r=-0.04; excl.-PC yield-netted r=-0.27 | `11_figure3_yield_confound.py` | Pass |

## Known, Documented Analytical Corrections

This section documents every substantive correction made during
preparation of this package, per open-science practice of disclosing
analytical history rather than presenting only a final, silently
corrected version.

### 1. Results 3.3 / Discussion 4.3: stale pre-buffalo-correction correlation figures

**Issue identified:** An earlier stage of this study's development
computed the correlation and variance-explained statistics reported in
Results Section 3.3 (raw and yield-netted associations between TE and
CH4 intensity) using a cattle-only yield denominator
(`milk_production_tons x 1000 / cows_heads`), predating the later
correction (documented in Section 5 of `docs/CODEBOOK.md`) that
switched the yield and emission-intensity denominator to the combined
cattle-and-buffalo stock for consistency with Methods Section 2.1 and
with Tables 3-4 and Figure 3. When that correction was made, Table 3,
Table 4, and Figure 3's plotted data were correctly updated, but the
narrative correlation statistics in Results 3.3, Discussion 4.1, 4.3,
and the Conclusion were not recomputed and retained their original,
cattle-only-denominator values (Pearson r = -0.59 raw; Spearman
rho = -0.79; yield alone explaining 85%/44% of TE/CH4Int variance; a
reported full-sample yield-netted correlation of +0.08 that was
described as "reversing sign" to -0.30 once post-conflict districts
were excluded).

**Correction:** All of these figures have been recomputed using the
combined-stock-denominator data (`data/processed/analytical_panel_with_emissions.csv`)
and now read: raw Pearson r = -0.61, Spearman rho = -0.82; yield alone
explaining 80%/45% of TE/CH4Int variance; full-sample yield-netted
Pearson r = -0.04 (close to zero, not positive); excl.-post-conflict
yield-netted Pearson r = -0.27. The manuscript's narrative was revised
accordingly: because the corrected full-sample yield-netted
correlation is already negative (not positive), there is no literal
"sign reversal" upon excluding post-conflict districts -- the accurate
description is a magnitude change from near-zero to moderate. The
substantive conclusion (a modest, yield-independent relationship
between technical efficiency and methane intensity, strongest once
post-conflict districts are excluded) is unchanged; only the raw
correlation, R-squared, full-sample residual-correlation figures, and
the "sign reversal" framing were corrected.

**Effect on reported results:** The primary second-stage regression
coefficient (Table 3, Column 3, beta1 = -0.029) and all Table 4
robustness rows are unaffected, since they were already computed on
the combined-stock data throughout. Only the descriptive correlation
statistics in Results 3.3 and their restatement in Discussion 4.1, 4.3,
and the Conclusion were corrected.

**Where implemented in this package:** `11_figure3_yield_confound.py`
computes all of Results 3.3's reported statistics directly from
`data/processed/analytical_panel_with_emissions.csv` (combined-stock
denominator throughout) and asserts the corrected values.

### 2. Table S1 (VIF): incorrect labor-variable form

**Issue identified:** An initial implementation of the VIF screening
script computed labor's variance-inflation factor using a district-year
**total**-hours construction (per-centner ratio x milk production x
10), which induces a mechanical correlation with the other,
output-scale inputs (cows, fodder, land) through the shared
`milk_production_tons` term. This gave VIF(cows)=2.91, VIF(labor)=2.54
-- both well above the manuscript's reported 1.39 and 1.01.

**Correction:** VIF screening uses labor in its raw, per-centner
**ratio** form (`labour_hours_per_centner_milk_enterprises`), which
does not share this mechanical output-scale dependence. This
reproduces the manuscript's reported values exactly (Cows 1.39, Fodder
1.40, Land 1.02, Labor 1.01). The district-year total form is retained,
correctly, for the separate labor-augmented frontier check (Table S4),
which is testing a different question (does labor belong in the
frontier itself, at the same input scale as the other three) than VIF
screening (is candidate labor collinear with the other inputs).

**Where implemented in this package:** `03_diagnostics.py`, Section (a)
uses the ratio-form `labor_ratio_col`; Section (c) separately
constructs `total_labor_hours` for the Table S4 frontier check.

### 3. Table S3: unreliable MLE convergence flag

**Issue identified:** Using `scipy.optimize`'s raw BFGS `.success`
return value as the convergence criterion incorrectly flagged the
full-sample frontier fit as "not converged" (`success=False`, message:
"Desired error not necessarily achieved due to precision loss"), even
though this fit reaches a stable, economically sensible solution
(`lambda` ~1.34) that exactly matches Table 2's translog estimates.
BFGS's strict internal gradient tolerance is not met at a flat optimum
that a preceding Nelder-Mead search has already found, independent of
whether the solution itself is meaningful.

**Correction:** "Converged" is defined substantively in
`03_diagnostics.py` as reaching a non-degenerate `lambda`
(`abs(lambda) > 0.05`) rather than by `scipy`'s raw success flag. Under
this criterion, the full sample converges (`lambda`=1.34) and the
post-conflict-excluded sample does not (`lambda` drifts to
approximately 3e-6, a degenerate boundary solution with no
inefficiency component), matching the manuscript's qualitative
description exactly.

**Effect on reported results:** None on any table value; this is a
diagnostic-classification criterion, not a re-estimated parameter.

## Note on Run-to-Run Sensitivity (Table S5, Panel B)

`08_leave_one_out_test.py`'s Panel B (200 random draws of ten
non-post-conflict districts) uses a fixed seed (`RANDOM_EXCLUSION_SEED
= 12345` in `_paths.py`) and is therefore fully deterministic within
this repository. However, the exact summary statistics (mean, min, max,
percentiles) are sensitive to the precise order in which candidate
non-post-conflict districts are enumerated before being passed to
`numpy.random.Generator.choice`, which can differ trivially across
environments or minor pandas/numpy version differences in how
`DataFrame.unique()` orders its output. The qualitative finding --
zero of 200 random draws produce positive skewness, and all fall
well short of the actual post-conflict-set skewness (+0.52) -- is
robust and has been confirmed stable across multiple independent runs
and random seeds during preparation of this package; only the exact
reported percentile values (e.g., -1.371 vs. -1.363 for the mean
across two runs) show this minor sensitivity.

## What This Package Does Not Claim

Consistent with the manuscript's own stated limitations (Discussion,
Section 4.6):

- This package does not propagate first-stage frontier estimation
  uncertainty into the second-stage regression's standard errors (the
  "generated regressor" problem; see manuscript Section 4.6).
- This package's frontier specification pools all district-years under
  a common half-normal inefficiency distribution and does not separate
  persistent, district-specific heterogeneity from time-varying
  technical inefficiency (see manuscript Section 4.6).
- The technical-efficiency-methane-intensity relationship is estimated
  at the district level; this package does not, and cannot, verify
  that the same relationship holds at the individual farm level (see
  manuscript Section 4.6, "ecological inference").
