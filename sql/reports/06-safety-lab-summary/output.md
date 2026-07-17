# Safety Lab Summary by Cohort — Output

Phase 1 Dexamethasone PK Study (ZA-CPT-P1)
Generated from `v_lab_classified`. 18 randomised volunteers, 17 analytes, 3 lab visits.
Full result sets: 153 rows (descriptives), 612 rows (change from baseline), 110 rows (shifts).
Representative extracts below; the complete tables regenerate from `query.sql`.

## 1. Descriptive statistics — dose-response at PK +48 h

| Cohort | Analyte | Unit | n | Mean | Min | Max | Out of range | Low | High |
|--------|---------|------|---|------|-----|-----|--------------|-----|------|
| 1 (2 mg) | GLUCOSE | mmol/L | 6 | 5.07 | 4.7 | 5.3 | 0 | 0 | 0 |
| 2 (4 mg) | GLUCOSE | mmol/L | 6 | 5.63 | 5.4 | 5.9 | 4 | 0 | 4 |
| 3 (8 mg) | GLUCOSE | mmol/L | 6 | 6.10 | 5.6 | 7.5 | 6 | 0 | 6 |
| 1 (2 mg) | NEUTROPHILS | 10^9/L | 6 | 5.68 | 4.9 | 6.5 | 0 | 0 | 0 |
| 2 (4 mg) | NEUTROPHILS | 10^9/L | 6 | 7.42 | 6.2 | 9.3 | 2 | 0 | 2 |
| 3 (8 mg) | NEUTROPHILS | 10^9/L | 6 | 8.87 | 7.0 | 10.2 | 5 | 0 | 5 |
| 1 (2 mg) | LYMPHOCYTES | 10^9/L | 6 | 2.45 | 1.9 | 3.0 | 0 | 0 | 0 |
| 2 (4 mg) | LYMPHOCYTES | 10^9/L | 6 | 2.05 | 1.7 | 2.5 | 0 | 0 | 0 |
| 3 (8 mg) | LYMPHOCYTES | 10^9/L | 6 | 1.52 | 1.2 | 2.0 | 0 | 0 | 0 |
| 1 (2 mg) | POTASSIUM | mmol/L | 6 | 4.22 | 3.7 | 4.5 | 0 | 0 | 0 |
| 2 (4 mg) | POTASSIUM | mmol/L | 6 | 3.85 | 3.3 | 4.1 | 1 | 1 | 0 |
| 3 (8 mg) | POTASSIUM | mmol/L | 6 | 3.73 | 3.6 | 3.9 | 0 | 0 | 0 |

Textbook single-dose corticosteroid effects, scaling with dose: glucose rise
(insulin antagonism), neutrophilia with mirror-image lymphopenia (demargination
and redistribution), and a modest potassium fall (mineralocorticoid activity).

**Note on potassium** — cohort 3 has the *lower* mean (3.73 vs 3.85) yet *zero*
flags, while cohort 2 has one Low. Cohort 2 contains a single volunteer at 3.3;
cohort 3's minimum is 3.6, so nobody crosses the 3.5 floor. Means and flag counts
answer different questions, which is why a CSR shows both.

## 2. Change from baseline — the high responder

| Subject | Cohort | Visit | Analyte | Baseline | Current | Change | Class |
|---------|--------|-------|---------|----------|---------|--------|-------|
| ZA-CPT-P1-080 | 3 | PK +48 h | GLUCOSE | 4.5 | 7.5 | **+3.0** | High |
| ZA-CPT-P1-080 | 3 | PK +48 h | NEUTROPHILS | 4.4 | 10.2 | **+5.8** | High |
| ZA-CPT-P1-080 | 3 | PK +48 h | ALT | 25 | 22 | −3 | Normal |
| ZA-CPT-P1-080 | 3 | Day 7 Follow-up | GLUCOSE | 4.5 | 4.9 | +0.4 | Normal |
| ZA-CPT-P1-080 | 3 | Day 7 Follow-up | NEUTROPHILS | 4.4 | 5.9 | +1.5 | Normal |
| ZA-CPT-P1-080 | 3 | Day 7 Follow-up | ALT | 25 | **86** | **+61** | High |

Volunteer 080 posted the study's largest glucose change (+3.0) and largest
neutrophil change (+5.8) at 48 h — both resolved by day 7 — and then a delayed
ALT elevation to 86 U/L (+61 from own baseline) at day 7. Three biggest-in-study
moves on one subject: the transaminase signal reads as biologically coherent with
a strong overall response, not as an isolated finding.

## 3. Shift table — baseline class → post-dose class

**Glucose, PK +48 h:**

| Cohort | Shift | n |
|--------|-------|---|
| 1 (2 mg) | Normal → Normal | 6 |
| 2 (4 mg) | Normal → High | 4 |
| 2 (4 mg) | Normal → Normal | 2 |
| 3 (8 mg) | Normal → High | **6** |

All six 8 mg volunteers moved from a normal baseline to high post-dose. No
pre-existing highs — the shift *is* the drug effect.

**Selected other shifts:**

| Cohort | Visit | Analyte | Shift | n |
|--------|-------|---------|-------|---|
| 3 | PK +48 h | NEUTROPHILS | Normal → High | 5 |
| 2 | PK +48 h | NEUTROPHILS | Normal → High | 2 |
| 2 | PK +48 h | POTASSIUM | Normal → Low | 1 |
| 3 | Day 7 Follow-up | ALT | Normal → High | 1 |
| 3 | Day 7 Follow-up | GLUCOSE | Normal → High | 1 |
| 2 | PK +48 h | PLATELETS | **Low → Normal** | 1 |
| 2 | Day 7 Follow-up | PLATELETS | **Low → Normal** | 1 |
| 1 | Day 7 Follow-up | ALBUMIN | Normal → Low | 1 |

**Resolution by day 7** — cohort 3's glucose falls from 6 High at 48 h to 1 at
day 7; neutrophils return entirely to Normal. The steroid effects are transient,
as expected of a single dose.

**Why the shift table earns its place** — cohort 2's platelets show `Low → Normal`
at both post-dose visits: volunteer 062's screening platelets were 144 (below the
150 floor) and normalised. An endpoint count would have read "0 abnormal at 48 h"
and hidden both the baseline abnormality and its resolution. A `Normal → High` is
a drug effect; a `Low → Normal` is a pre-existing finding resolving. Endpoint
counts cannot distinguish them.

*Classification decoded from `lab_reference` (units and normal ranges);
cohort shown as raw code (1 = 2 mg, 2 = 4 mg, 3 = 8 mg).*