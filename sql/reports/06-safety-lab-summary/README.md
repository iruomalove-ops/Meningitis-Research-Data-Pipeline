# Safety Lab Summary by Cohort

## What this is
The safety laboratory section of a Clinical Study Report — cohort-level lab
trends with clinically classified out-of-range values. Reviewed by the Safety
Review Committee during the trial and submitted as part of the CSR.

## Why it matters in clinical work
A lab value alone means nothing. "Potassium 3.3" is unreadable until you know
it's mmol/L and that normal is 3.5–5.0. This report is where raw numbers become
clinical statements, and it answers three different questions that a single view
of the data cannot:

**Did the drug do something?** — cohort means across dose levels. Glucose rising
5.07 → 5.63 → 6.10 across the 2/4/8 mg cohorts at 48h is a dose-response, visible
only in aggregate.

**Did it do something to *this* person?** — change from baseline. A value inside
the normal range can still represent a large individual move; a value outside it
may be where that subject always sat. Change from their own baseline separates
the two.

**Was it a drug effect or a pre-existing finding?** — the shift table. A subject
who was Normal at baseline and became High shows a drug effect. One who was
already High and stayed High shows a pre-existing condition. Endpoint counts
cannot tell them apart. In this study, cohort 2's platelets show `Low → Normal` —
a baseline abnormality resolving, which a raw "0 abnormal at 48h" count would
have hidden entirely.

## Components
1. **Descriptive statistics** — per cohort × visit × analyte: n, mean, min, max,
   and counts out of range (split Low/High). 153 rows.
2. **Change from baseline** — per subject × visit × analyte, using a FIRST_VALUE
   window function to fetch each subject's own screening value. 612 rows.
3. **Shift table** — baseline classification → post-dose classification, counted
   per cohort × visit × analyte. Long format; pivot for the printed CSR look.

Reference-range classification is not a separate component: it is the derivation
all three stand on, and lives in the `v_lab_classified` analytics view.

## The analytics view
`v_lab_classified` joins each lab result to its applicable reference range and
classifies it Low/Normal/High. Two resolution rules live there:

- **Sex-specific ranges** — HB and creatinine differ by sex; the other 14 analytes
  do not. Non-sex-specific tests carry `sex_code = 'ALL'`, and the join's
  `OR sex_code = 'ALL'` is what makes that a wildcard. Each range is stored once.
- **Glucose fasting** — the glucose range depends on fasting state, resolved from
  `lab_result.fasting_status` rather than a hardcoded assumption, so a rebuilt
  database classifies correctly from its own data.


## Source
- `v_lab_classified` (analytics) — built on `lab_result`, `subject`, `visit`,
  `enrollment`, `lab_reference`