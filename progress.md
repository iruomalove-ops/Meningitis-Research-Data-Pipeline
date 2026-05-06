# Project Progress Log

A running diary of milestones, decisions, and lessons learned as the meningitis research data pipeline is built.

---

## 2026-05-04 — Phase 1 D1 Healthy Volunteer Eligibility instrument complete

### What was built
Completed the first REDCap instrument for the Phase 1 dexamethasone pharmacokinetic study in healthy volunteers. The instrument is fully functional in REDCap with all field types, validation rules, and branching logic in place.

### Final structure
- **30 fields** across five sections — site identification, demographics, inclusion criteria, exclusion criteria, eligibility conclusion
- **7 inclusion criteria** — age 18–55, BMI 18–35, good general health, normal hepatic function, normal renal function,willingness to comply with procedures, written informed consent
- **9 exclusion criteria** — including CYP3A4 drug interactions, recent medication use, diabetes, immunosuppression, pregnancy, corticosteroid allergy, smoking, excess alcohol, recent trial participation
- **3 branching logic rules** — pregnancy field shows only for female volunteers, screen failure reason and narrative show only when eligibility = screen failure
- **2 calculated fields** — age computed from date of birth, BMI computed from weight and height

### Key design decisions
- Kept the inclusion criterion "good general health" as a broad clinical judgement rather than adding redundant specific disease exclusions. A volunteer in good general health by definition does not have uncontrolled hypertension, peptic ulcer disease, or adrenal insufficiency. This avoids internal data contradictions that would generate monitor queries.
- Retained CYP3A4 drug interaction exclusion because dexamethasone is metabolised by this enzyme. Volunteers on CYP3A4 inducers or inhibitors would corrupt the pharmacokinetic curve.
- Used radio buttons coded 1=Yes, 0=No for all eligibility criteria to enable clean SQL queries and Power BI filters later.

### Tested
Form previewed and tested — branching logic fires correctly, calculated fields update live as inputs change, all required fields blocked saving when empty.

### Next milestone
Build D2 Demographics and Medical History instrument.
## 2026-05-04 — Phase 1 D2 Demographics & Medical History instrument complete

### What was built
Second REDCap instrument for the Phase 1 dexamethasone trial. Captures the safety baseline that contextualises every subsequent visit and adverse event.

### Final structure
- **25 fields** across six sections — identity & demographics, vital signs at screening, medical history, current medications, lifestyle factors, vaccination & family history
- **4 branching logic rules** — past medical history details, surgery details, allergy details, and medication list each appear only when the gateway Yes/No field is answered Yes
- **22 required fields** plus 3 conditional fields that become required when their gateway triggers

### Key design decisions
- Used a gateway pattern for medical history sections — one Yes/No question that conditionally reveals the free-text details field. Saves time when most healthy volunteers have nothing to declare while still capturing full detail when needed.
- Captured race and ethnicity separately following FDA convention. Race matters clinically because CYP3A4 polymorphisms vary between populations and affect dexamethasone metabolism — a covariate for the PK analysis later.
- Quantified alcohol and caffeine intake as numeric fields rather than categorical. This turns lifestyle data into analysable covariates for the PK model.
- Included recent vaccination status because immune activation from a recent vaccine could confound corticosteroid effects.

### New skills practised
Wrote branching logic formulas from scratch using the syntax `[variable_name] = 'value'`. Understood why branching is set on the field that should appear, not on the trigger field.

### Next milestone
Build D3 Dose Escalation instrument — captures cohort assignment, sentinel dosing rules, and the dose escalation decision log.

## 2026-05-04 — Phase 1 D3 Dose Escalation instrument complete

### What was built
Third REDCap instrument for the Phase 1 dexamethasone trial. Captures the operational backbone of the dose escalation study — cohort assignment, sentinel dosing, Safety Review Committee gates, and escalation decisions.

### Final structure
- **22 fields** across five sections — cohort assignment, dose information, SRC safety gates, escalation decision, protocol deviations
- **5 branching logic rules** — sentinel-specific safety review fields appear only for sentinel volunteers, DLT description appears only when DLT observed, deviation detail fields appear only when a deviation occurred
- **1 calculated field** — dose per kg automatically computed from planned dose divided by body weight pulled from D2
- **15 required fields** with the five-option SRC decision dropdown as the most consequential field in the entire trial

### Key design decisions
- Used a five-option dropdown for SRC decision rather than a simple yes or no — captures the full clinical reality of escalation choices (escalate, repeat, de-escalate, hold, or stop the trial entirely).
- Created branching logic that links cohort_position to is_sentinel automatically — only positions 1 and 2 are sentinels per protocol. This prevents data entry errors.
- Captured IMP batch number and expiry as required fields. In real trials this is non-negotiable for traceability — if a safety signal emerges weeks later, regulators trace it back through batch numbers.
- Added a separate protocol deviations section with branching to reporting confirmations. Forces nurses to confirm sponsor and ethics notification when deviations occur.

### What I learned this session
- How dose escalation actually works in a Phase 1 trial — sentinel dosing with a 48 hour observation gate before exposing the rest of the cohort
- Dose-Limiting Toxicity (DLT) is the criterion that pauses or stops escalation — typically CTCAE Grade 3+ AEs related to the study drug
- The SRC (Safety Review Committee) is the binding decision-making body for escalation, not the PI alone
- The dose per kg calculation matters because drug exposure is body-weight dependent

### Next milestone
Build D4 PK Sampling Schedule — the hero data domain for Phase 1. Captures every blood draw timepoint, the actual sample time vs scheduled time, sample handling, and centrifugation. This is the data that will populate the PK concentration-time curve in the Power BI dashboard.

---
## 2026-05-04 — Phase 1 D4 PK Sampling Schedule instrument complete

### What was built
The hero data domain of the Phase 1 trial. D4 captures every blood draw at every pharmacokinetic timepoint — the dataset that will eventually populate the concentration-time curve in Power BI and feed every PK calculation in Python.

### Final structure
- **18 fields** across four sections — timepoint identification, sample collection, sample handling and processing, bioanalytical assay result
- **8 branching logic rules** — most sample handling fields hide when sample_collected = No, replaced by a missed reason dropdown
- **1 calculated field** — time deviation in minutes, computed automatically from actual time minus scheduled time
- **Repeating instrument design** — when REDCap events are configured this single instrument will be assigned to 8 separate events (pre-dose, 30min, 1h, 2h, 4h, 8h, 24h, 48h) generating 144 rows of time-series data across 18 volunteers

### Key design decisions
- Captured both scheduled time and actual time as separate required fields. The pharmacokineticist needs actual times not scheduled times to fit the PK curve correctly. Honesty in data is more valuable than perfect adherence to schedule.
- Made the timepoint a dropdown not free text. Standardised values prevent data entry chaos when SQL queries try to filter by timepoint later. "T30min" "30 min" and "0.5h" would all be the same thing in different forms — the dropdown forces consistency.
- Used a gateway pattern around sample_collected. If the sample was missed, eight subsequent fields hide and a single missed_reason dropdown appears. Captures full detail when needed without cluttering the form when not.
- Documented the BLQ (Below Limit of Quantification) flag explicitly. At 24 and 48 hour timepoints concentrations may genuinely be too low to measure. BLQ is informative not missing data — flagging it correctly matters for PK analysis.
- Included sample handling fields (centrifuge time, storage temperature, tube type) that are not directly used in PK calculation but provide audit trail for sample integrity. Wrong tube type or delayed centrifugation invalidates the assay.

### What I learned this session
- The PK sampling schedule is the skeleton of a Phase 1 trial. Everything else (eligibility, demographics, dose escalation) supports getting clean PK data
- Actual time vs scheduled time matters more than I realised. A 32-minute draw recorded as 30 minutes corrupts the curve fitting
- BLQ samples are not the same as missing samples. They are valid data points that say "concentration is below the assay's detection threshold"
- Sample handling is part of the data integrity chain. The lab cannot fix a sample that was left at room temperature too long

### Dataset projection
With 8 timepoints multiplied by 18 volunteers across 3 cohorts the trial generates approximately 144 rows of time-series concentration data. This is the dataset that will:
- Feed the SQL window functions for cohort comparison queries
- Drive the Python AUC calculation using scipy.integrate.trapz
- Populate the hero PK concentration-time curve visual in the Power BI dashboard with individual volunteer lines and cohort mean overlay

### Next milestone
Build D5 Safety Labs and Vitals — captures all clinical chemistry and haematology results at scheduled timepoints plus vital sign monitoring. Detects steroid-induced hyperglycaemia, electrolyte disturbance, and any haematological signal during the trial.

---