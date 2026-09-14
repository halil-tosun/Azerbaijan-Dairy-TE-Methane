# REPLICATION GUIDE

## Quick Start

```bash
conda env create -f environment.yml
conda activate azerbaijan-dairy-te-methane-repro
cd code
python run_all.py
```

or, without conda:

```bash
pip install -r requirements.txt
cd code
python run_all.py
```

Expected runtime: under one minute on a standard laptop. Every script
prints its results and its own internal verification checks; `run_all.py`
stops immediately if any check fails.

## Step-by-Step (running scripts individually)

All scripts read their inputs from `data/raw/` or `data/processed/`
directly (via `_paths.py`), not from another script's in-memory state,
so scripts can be run individually provided their stated prerequisite
has been run at least once. Prerequisites:

| Script | Requires (must be run first) |
|---|---|
| `01_data_preparation.py` | none |
| `02_sfa_frontier_estimation.py` | `01` |
| `03_diagnostics.py` | none (rebuilds its own merge from `data/raw/`) |
| `04_emission_intensity.py` | `02` |
| `05_descriptive_stats.py` | `04` |
| `06_second_stage_regression.py` | `04` |
| `07_robustness.py` | `04` |
| `08_leave_one_out_test.py` | none (rebuilds its own merge from `data/raw/`) |
| `09_figure1_te_trend.py` | `02` |
| `10_figure2_district_ranking.py` | `04` |
| `11_figure3_yield_confound.py` | `04` |

## Adapting This Package to a Different Setting

To apply this pipeline to a different district/region panel, a
different country's dairy statistics, or a different livestock
species:

1. **Replace the raw data files** in `data/raw/` with your own source
   tables, and rewrite `01_data_preparation.py`'s parsing logic to
   match your source format (the merge-and-restrict logic downstream
   of parsing is format-agnostic).
2. **Update `_paths.py`'s `IPCC_DAIRY_YIELD_EF_PAIRS`** if working with
   a different species (IPCC, 2006, Table 10.10 provides fixed,
   non-yield-varying factors for buffalo, sheep, goats, and other
   species; Table 10.11 is specific to cattle).
3. **Update `POST_CONFLICT_DISTRICTS`** (or remove this exclusion
   entirely) if your setting does not have an analogous structurally
   distinct subset of observations. If it does, first run
   `03_diagnostics.py`'s Table S3 logic (OLS residual skewness with and
   without the candidate exclusion set) to check whether an analogous
   identification issue exists before assuming the same exclusion
   strategy applies.
4. **Re-verify all `assert` statements.** Every script's assertions
   check against *this* study's specific reported values; when
   adapting the pipeline to new data, remove or update these
   assertions to reflect your own results before treating a "no
   AssertionError" run as a validation of correctness.
5. **Re-run `08_leave_one_out_test.py`'s logic** for any new exclusion
   decision, to confirm (as this package does for the ten post-conflict
   districts) that the exclusion reflects a genuine, data-specific
   property rather than an artifact of removing any similarly-sized
   subset of observations.

## Common Issues

- **`ModuleNotFoundError` for `_paths`:** scripts must be run from
  inside the `code/` directory (`cd code` first), since `_paths.py` is
  imported as a local module, not an installed package.
- **Numerical Hessian warnings in `02_sfa_frontier_estimation.py`:**
  if you modify the frontier specification, check that the printed
  standard errors are finite and positive; a singular or near-singular
  numerical Hessian will produce `NaN` or implausibly large standard
  errors, indicating the specification needs adjustment (e.g., more
  data, fewer parameters, or better-scaled inputs).
