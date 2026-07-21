# PK Summary Tables

## What this is
The pharmacokinetic analysis section of a Phase 1 Clinical Study Report:
descriptive PK parameters summarising each volunteer's exposure to the study
drug, aggregated by dose cohort. This is where the concentration-time data
becomes the numbers regulators read to judge how the drug behaves in the body.

## Why it matters in clinical work
A Phase 1 study's central question is: what does the body do to the drug? Three
parameters answer it:

- **Cmax** — the peak plasma concentration. How high does exposure get?
- **Tmax** — the time of that peak. How fast is the drug absorbed?
- **AUC** — area under the concentration-time curve. Total exposure over time.

Aggregated by cohort, these reveal **dose proportionality**: if doubling the dose
doubles Cmax and AUC, the drug has linear kinetics and dosing is predictable. If
it more-than-doubles, a clearance pathway may be saturating — a safety concern.
This study shows clean linearity across 2–8 mg.

## How the parameters are computed
All three live in the `v_pk_parameters` analytics view, computed once:

- **Cmax** — the maximum measured concentration per volunteer.
- **Tmax** — a ranking window function (ROW_NUMBER over concentration descending)
  picks each volunteer's peak sample; its timepoint is Tmax.
- **AUC(0–48h)** — the **linear trapezoidal rule**. Each adjacent pair of samples
  forms a trapezoid (½ × time-gap × sum-of-concentrations); the LEAD window
  function fetches the next sample so each row can compute the trapezoid to its
  right, and the areas are summed per volunteer. BLQ (below limit of
  quantification) values are set to 0, the standard convention (pre-dose has no
  drug).

## Two honest boundaries

**Half-life (t½) is not computed here.** Elimination half-life requires
log-linear regression on the terminal phase of the curve — a curve fit, not a
single arithmetic expression. That belongs in specialised PK software (Phoenix
WinNonlin, or a Python/`scipy` fit), which is where a real analysis would produce
it. SQL is the wrong tool, and forcing an approximation would misrepresent it.

**Tmax is bounded by the sampling schedule.** Every volunteer's observed Tmax is
0.5 h — the first post-dose sample. This is consistent with dexamethasone's rapid
absorption, but it means the *true* peak may have occurred before 0.5 h and gone
unobserved. Observed Tmax can only be as early as the first draw; a shorter true
Tmax would be invisible to this schedule. A real PK report notes this limitation
rather than presenting 0.5 h as certainly the true peak.

## What the report does
Reads `v_pk_parameters` twice: a per-volunteer listing, and a cohort-level
summary (mean/min/max of Cmax and AUC, plus CV% — the coefficient of variation,
SD/mean × 100, the standard PK measure of between-subject variability).

Pattern: **window functions plus aggregation** — ranking and LEAD windows to
derive per-subject parameters, then grouped descriptives for the cohort table.

## Source
- `v_pk_parameters` (analytics) — built on `pk_concentration`, `visit`,
  `enrollment`, `dosing`