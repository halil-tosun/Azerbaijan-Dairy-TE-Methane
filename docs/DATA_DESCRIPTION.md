# DATA DESCRIPTION

## Primary Sources

All raw data used in this repository are publicly available official
statistics. No proprietary, licensed, or non-public data are used.

### 1. District panel (`data/raw/ssc_ra_district_panel_long.csv`)

Source: State Statistical Committee of the Republic of Azerbaijan (SSC
RA). 2025. *Agriculture, Forestry and Fishery -- Statistical Yearbook
Data.* Baku: SSC RA. https://www.stat.gov.az/source/agriculture/en/

Long-format panel (region, region_type, year, variable, value) covering
all 67 administrative districts and higher-level aggregates (economic
regions, national totals) of Azerbaijan. Variables used in this study:

| Variable | Description | Years available |
|---|---|---|
| `milk_production_tons` | Annual milk production | 2000-2024 |
| `cows_heads` | Dairy cattle stock (head) | 2000-2024 |
| `cows_dairy_buffaloes_stock_heads` | Combined dairy cattle + buffalo stock (head) | 2000-2024 |
| `fodder_sown_area_ha` | Fodder-crop sown area (ha) | 2005-2024 |
| `labour_hours_per_centner_milk_enterprises` | Labor input per centner (100 kg) of milk, enterprise subsector | 2005-2024 (partial) |

### 2. Land-use table (`data/raw/ssc_ra_land_use_002_2en.csv`)

Source: SSC RA, Table 002_2en, "Total land in ownership and use of
agricultural enterprises." Published as a wide-format government table
(districts as rows, years 2005-2024 as columns); parsed into long
format by `code/01_data_preparation.py`.

| Variable | Description | Years available |
|---|---|---|
| `land_total_ha` | Total agricultural land in ownership or use (ha) | 2005-2024 |

## Derived / Processed Data

`code/01_data_preparation.py` merges the two raw sources above on
(region, year), restricts to districts (excluding economic-region and
national aggregates), and applies listwise deletion for missing or
non-positive values on the four production-frontier variables,
producing `data/processed/analytical_panel.csv` (N = 920 district-years,
59 districts, 2005-2024).

Subsequent scripts add derived columns to this panel:

- `02_sfa_frontier_estimation.py` adds `TE` (technical efficiency,
  Eq. 3-4) -> `data/processed/analytical_panel_with_TE.csv`
- `04_emission_intensity.py` adds `yield_combined`, `EF_combined`,
  `CH4_intensity` (combined cattle+buffalo denominator; Eq. 5-6, primary
  measure throughout the manuscript) and `yield_cattle_only`,
  `EF_cattle_only`, `CH4_intensity_cattle_only` (cattle-only
  denominator; Table 4 robustness check only) ->
  `data/processed/analytical_panel_with_emissions.csv`

## IPCC (2006) Tier 1 Reference Values

The eight regional (milk yield, emission factor) reference pairs used
for the yield-interpolated emission factor (manuscript Eq. 6) are
transcribed from IPCC (2006), *2006 IPCC Guidelines for National
Greenhouse Gas Inventories*, Volume 4, Chapter 10, Table 10.11 (dairy
cattle). These are hard-coded as `IPCC_DAIRY_YIELD_EF_PAIRS` in
`code/_paths.py`, with the original table transcribed and cited in full
in `code/_paths.py`'s header comments.

## Post-Conflict District List

The ten districts treated as structurally distinct throughout this
study (`POST_CONFLICT_DISTRICTS` in `code/_paths.py`) correspond to
territories of the Republic of Azerbaijan reintegrated following the
ceasefire of November 9, 2020. This list is based on publicly available
administrative geography and is not itself derived from SSC RA data;
see manuscript Section 1 and 2.2 for the historical and administrative
context.

## Variable Naming Note

Raw source variable names (e.g., `cows_dairy_buffaloes_stock_heads`)
are retained as published by SSC RA and are longer/more literal than
the manuscript's prose descriptions (e.g., "combined dairy-cattle-and-
buffalo stock"); no renaming was performed in `data/raw/` to preserve
direct traceability to the original government tables.
