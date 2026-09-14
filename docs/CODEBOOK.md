# CODEBOOK

Analytical workflow and model equations underlying this reproducibility
package. Read this before extending or modifying the pipeline.

## 1. Production Frontier (Eq. 1-4; `02_sfa_frontier_estimation.py`)

Translog stochastic frontier production function (Aigner, Lovell, &
Schmidt, 1977):

```
ln Y_it = beta0 + Sum_k beta_k ln X_kit
                + 0.5 Sum_k Sum_l beta_kl ln X_kit ln X_lit
                + v_it - u_it
```

- `Y_it`: milk production (tons), district *i*, year *t*
- `X_kit`, k=1..3: dairy cattle stock (head), fodder-crop sown area
  (ha), total agricultural land in use (ha) -- all log-transformed and
  mean-centered
- `v_it ~ N(0, sigma_v^2)`: symmetric noise
- `u_it >= 0, u_it ~ N+(0, sigma_u^2)`: half-normal technical
  inefficiency

Estimated by maximum likelihood: Nelder-Mead simplex search from OLS
starting values, refined by BFGS. Technical efficiency is recovered via
the Jondrow et al. (1982) conditional-mean estimator in its Battese &
Coelli (1988) multiplicative form: `TE_i = exp(-E[u_i | eps_i])`.

The Cobb-Douglas restriction (all second-order `beta_kl = 0`) is tested
by likelihood-ratio test against the translog alternative.

**A note on numerical Hessian standard errors:** `02_sfa_frontier_estimation.py`
computes standard errors from a numerical Hessian of the negative
log-likelihood. This is more brittle than an analytical Hessian but
avoids deriving one by hand for the translog specification; if you
modify the frontier specification (e.g., add an input), re-verify that
the Hessian remains well-conditioned (no near-zero or negative
diagonal elements) before trusting the reported standard errors.

## 2. Enteric Methane Emission Intensity (Eq. 5-6; `04_emission_intensity.py`)

```
CH4Int_it = (EF_it x N_it) / M_it                              (Eq. 5)
EF_it = interp(Yield_it; IPCC_DAIRY_YIELD_EF_PAIRS)             (Eq. 6)
```

- `N_it`: combined dairy-cattle-and-buffalo stock (head) -- the primary
  denominator throughout the manuscript, correcting a cattle-only/
  combined-stock species mismatch (see Section 5 below)
- `M_it`: milk production (kg)
- `EF_it`: district-year emission factor, linearly interpolated across
  IPCC (2006, Table 10.11)'s eight regional (yield, EF) reference
  pairs, boundary-clamped (not extrapolated) for yields outside
  [475, 8400] kg head^-1 yr^-1 (`numpy.interp` default behavior)

A cattle-only-denominator version (`yield_cattle_only`,
`CH4_intensity_cattle_only`) is also computed, used only for the Table
4 robustness comparison, not as a primary measure.

## 3. Second-Stage Regression (Eq. 7; `06_second_stage_regression.py`)

```
CH4Int_it = alpha + beta1 TE_it + beta2 ln(Yield_it) + Sum_t gamma_t Year_t + eps_it
```

Estimated by OLS with district-clustered standard errors (CR1
finite-sample correction, Cameron & Miller, 2015). Three columns:

1. Full sample (N=920) + simple post-conflict intercept dummy
2. Excl. post-conflict districts (N=832), no year fixed effects
3. Excl. post-conflict districts (N=832) + year fixed effects
   (**primary specification**)

Inference on the primary specification's `beta1` is additionally
checked via a wild-cluster (Rademacher) bootstrap of the
null-restricted model (`B=999`, fixed seed 42; Cameron, Gelbach, &
Miller, 2008).

## 4. Diagnostics (`03_diagnostics.py`)

Three distinct diagnostic checks, each using a **different form** of
the labor variable -- this is the single most important implementation
detail in this repository and is easy to get wrong:

- **VIF screening (Table S1)** uses labor in its raw, per-centner
  **ratio** form (`labour_hours_per_centner_milk_enterprises`). Using
  the district-year **total** form instead (ratio x milk production)
  induces a spurious mechanical correlation with the other,
  output-scale inputs and gives materially different (higher) VIF
  values that do **not** match the manuscript.
- **Frontier re-estimation (Table S3)** and the **labor-augmented
  frontier (Table S4)** both use labor as a district-year **total**
  (ratio x milk production x 10, converting hours-per-centner to
  hours-per-district-year), consistent with the scale of the other
  three inputs and with the manuscript's own variable description
  ("converted from a per-centner ratio to a district-year level").

**Convergence criterion (Table S3):** `scipy.optimize`'s raw BFGS
`.success` flag is not a reliable indicator of meaningful convergence
here -- it reports `False` even for the full-sample fit, which reaches
a stable, sensible `lambda` (~1.34) matching Table 2's translog
estimate, simply because BFGS's strict internal gradient tolerance is
not met at a flat optimum that Nelder-Mead has already found.
"Converged" is instead defined substantively: whether the MLE reaches a
non-degenerate `lambda` (`abs(lambda) > 0.05`) rather than drifting to
the `lambda = 0` boundary (a degenerate solution with no inefficiency
component, at which "mean technical efficiency" is not economically
meaningful). See `docs/REPRODUCIBILITY_CHECKLIST.md` for the specific
values this produces and how they relate to the manuscript's reported
"implied mean TE > 1" description of the same phenomenon.

## 5. Cattle/Buffalo Species Correction

Azerbaijan's official statistics report milk production as a single,
undifferentiated series (not disaggregated by cattle vs. buffalo), but
publish two separate herd-size series: dairy-cattle-only stock and
combined dairy-cattle-and-buffalo stock. Using the cattle-only stock as
the yield/emission-intensity denominator in districts where buffalo
are a non-trivial share of the herd (mean 7.7%, max 38.6% across the
sample) creates a numerator-denominator species mismatch. This
repository uses the **combined** stock as the denominator throughout
(Eq. 5-6) and reports the cattle-only version only as an explicit,
labeled robustness check (Table 4, row 2).

## 6. Leave-One-Out / Random-Exclusion Test (`08_leave_one_out_test.py`)

Directly tests whether the OLS residual-skewness reversal that
identifies the post-conflict exclusion decision (Table S3) is specific
to the ten post-conflict districts or a generic consequence of removing
any ten districts. Panel A retains one post-conflict district at a time
(excluding the other nine); Panel B excludes 200 independently drawn
random sets of ten non-post-conflict districts. See
`docs/REPRODUCIBILITY_CHECKLIST.md` for a note on run-to-run numerical
sensitivity in Panel B's exact summary statistics.
