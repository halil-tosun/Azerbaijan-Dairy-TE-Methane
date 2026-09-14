"""
_paths.py -- Shared path configuration and constants for this repository.

Technical Efficiency and Enteric Methane Emission Intensity in a
Transition-Economy Dairy Sector: A Stochastic Frontier Analysis from
Azerbaijan
(Tosun).

This is an INDEPENDENT repository. Ten districts examined in this
study correspond to territories reintegrated following the 2020
ceasefire; a separate, independent analysis of the causal effect of
post-conflict recovery on productivity in this same setting exists as
a distinct study with a distinct research question (see manuscript
Section 2, "Diagnostic Screening and Input Selection"). This
repository does not import from, or depend on, that or any other
companion package. All district-level official statistics used here
are independently re-harmonized in 01_data_preparation.py from their
original SSC RA source tables (see docs/DATA_DESCRIPTION.md).

Not run directly. Imported by every numbered script in code/.
"""
from pathlib import Path

# ---- Repository-relative paths ----
ROOT = Path(__file__).resolve().parents[1]
DATA_RAW = ROOT / "data" / "raw"
DATA_PROCESSED = ROOT / "data" / "processed"
OUTPUT = ROOT / "output"
FIGURES = ROOT / "figures"

for p in (DATA_RAW, DATA_PROCESSED, OUTPUT, FIGURES):
    p.mkdir(parents=True, exist_ok=True)

# ============================================================
# Study area and sample
# ============================================================
# State Statistical Committee of the Republic of Azerbaijan (SSC RA).
# 2025. Agriculture, Forestry and Fishery -- Statistical Yearbook Data.
# Baku: SSC RA. See docs/DATA_DESCRIPTION.md for the specific source
# table (and URL) underlying every raw column used in this repository.
N_DISTRICTS_TOTAL = 67
SAMPLE_YEARS = (2005, 2024)          # inclusive; 2006-2007 reporting gap
SAMPLE_N_DISTRICT_YEARS = 920        # after listwise deletion (Section 2.1)
SAMPLE_N_DISTRICTS = 59              # districts with at least one complete year

# Ten districts corresponding to territories reintegrated following
# the 2020 ceasefire (Trilateral Statement, 2020). Retained in frontier
# estimation (Section 2.2) but excluded from the second-stage
# regression on diagnostic grounds (Section 2.3; see also
# 03_diagnostics.py and docs/CODEBOOK.md).
POST_CONFLICT_DISTRICTS = [
    "Aghdam district", "Aghdara district", "Fuzuli district",
    "Gubadli district", "Jabrayil district", "Kalbajar district",
    "Khojavand district", "Lachin district", "Shusha district",
    "Zangilan district",
]

# ============================================================
# IPCC (2006) Tier 1 enteric-fermentation emission factors
# ============================================================
# IPCC. 2006. 2006 IPCC Guidelines for National Greenhouse Gas
# Inventories, Volume 4: Agriculture, Forestry and Other Land Use,
# Chapter 10: Emissions from Livestock and Manure Management, Table
# 10.11 (dairy cattle, by region) and Table 10.10 (buffalo, fixed
# factor). Eight regional (yield, EF) reference pairs, sorted by
# yield, used for linear interpolation (manuscript Eq. 6):
#   yield (kg head^-1 yr^-1) : EF (kg CH4 head^-1 yr^-1)
IPCC_DAIRY_YIELD_EF_PAIRS = [
    (475, 46), (800, 72), (900, 58), (1650, 68),
    (2200, 100), (2550, 99), (6000, 117), (8400, 128),
]
IPCC_DAIRY_YIELD_MIN = 475     # % of DM equivalent lower domain boundary
IPCC_DAIRY_YIELD_MAX = 8400
IPCC_BUFFALO_EF_FIXED = 55.0   # kg CH4 head^-1 yr^-1 (Table 10.10; not used
                                 # directly -- see manuscript Section 2.1 and
                                 # 2.4 for why a combined-stock, cattle-curve
                                 # approximation is used instead, and Table 4
                                 # / output/Table4_robustness.csv for the
                                 # cattle-only-denominator sensitivity check)
IPCC_TIER1_UNCERTAINTY_LOW = 0.70   # -30%
IPCC_TIER1_UNCERTAINTY_HIGH = 1.50  # +50%

# ============================================================
# Stochastic frontier specification (Eq. 1-4)
# ============================================================
# Aigner, D., C. A. K. Lovell, and P. Schmidt. 1977. Formulation and
# estimation of stochastic frontier production function models. J.
# Econometrics 6:21-37.
# Jondrow, J., C. A. K. Lovell, I. S. Materov, and P. Schmidt. 1982. On
# the estimation of technical inefficiency in the stochastic frontier
# production function model. J. Econometrics 19:233-238.
# Battese, G. E., and T. J. Coelli. 1988. Prediction of firm-level
# technical efficiencies with a generalized frontier production
# function and panel data. J. Econometrics 38:387-399.
FRONTIER_INPUTS = ["cows_heads", "fodder_sown_area_ha", "land_total_ha"]
FRONTIER_OUTPUT = "milk_production_tons"

# ============================================================
# Second-stage regression (Eq. 7) and inference
# ============================================================
# Cameron, A. C., J. B. Gelbach, and D. L. Miller. 2008. Bootstrap-
# based improvements for inference with clustered errors. Rev. Econ.
# Stat. 90:414-427.
# Cameron, A. C., and D. L. Miller. 2015. A practitioner's guide to
# cluster-robust inference. J. Human Resources 50:317-372.
WILD_BOOTSTRAP_REPLICATIONS = 999
WILD_BOOTSTRAP_SEED = 42

# ============================================================
# Robustness / leave-one-out random-exclusion test (Table S5)
# ============================================================
RANDOM_EXCLUSION_DRAWS = 200
RANDOM_EXCLUSION_SEED = 12345
