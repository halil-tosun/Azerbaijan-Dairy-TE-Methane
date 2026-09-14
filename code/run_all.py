"""
run_all.py -- Runs the complete analytical pipeline in order.

Technical Efficiency and Enteric Methane Emission Intensity in a
Transition-Economy Dairy Sector: A Stochastic Frontier Analysis from
Azerbaijan
(Tosun).

Reproduces every table and figure reported in the manuscript and its
Supporting Information:
    Table 1   -- 05_descriptive_stats.py
    Table 2   -- 02_sfa_frontier_estimation.py
    Table 3   -- 06_second_stage_regression.py
    Table 4   -- 07_robustness.py
    Table S1  -- 03_diagnostics.py
    Table S3  -- 03_diagnostics.py
    Table S4  -- 03_diagnostics.py
    Table S5  -- 08_leave_one_out_test.py
    Figure 1  -- 09_figure1_te_trend.py
    Figure 2  -- 10_figure2_district_ranking.py
    Figure 3  -- 11_figure3_yield_confound.py

Every script contains its own internal `assert` statements checking its
output against the manuscript's and Supporting Information's reported
values; this script stops immediately if any check fails, rather than
silently continuing with a mismatched output.

Expected runtime: under one minute on a standard laptop (the frontier
maximum-likelihood estimation in scripts 02 and 03 is the slowest step).
"""
import subprocess
import sys
from pathlib import Path

SCRIPTS = [
    "01_data_preparation.py",
    "02_sfa_frontier_estimation.py",
    "03_diagnostics.py",
    "04_emission_intensity.py",
    "05_descriptive_stats.py",
    "06_second_stage_regression.py",
    "07_robustness.py",
    "08_leave_one_out_test.py",
    "09_figure1_te_trend.py",
    "10_figure2_district_ranking.py",
    "11_figure3_yield_confound.py",
]

CODE_DIR = Path(__file__).resolve().parent

if __name__ == "__main__":
    for script in SCRIPTS:
        print("=" * 70)
        print(f"Running {script}")
        print("=" * 70)
        result = subprocess.run([sys.executable, str(CODE_DIR / script)])
        if result.returncode != 0:
            print(f"\nFAILED at {script} (exit code {result.returncode}). Stopping.")
            sys.exit(result.returncode)
        print()

    print("=" * 70)
    print("All scripts completed successfully.")
    print("Every internal verification assertion passed against the")
    print("manuscript's and Supporting Information's reported values.")
    print("=" * 70)
