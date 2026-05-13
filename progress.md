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

---## 2026-05-09 — D5 Safety Labs and Vitals imported via data dictionary

### What was built
D5 imported successfully using a REDCap data dictionary CSV — 32 fields covering
visit context, vital signs, full blood count, liver function tests, renal function
and electrolytes, glucose monitoring with auto-warning above 11 mmol/L, and
investigator review.

### Incident — D1 to D4 lost during import
The data dictionary upload replaced the entire project instrument list rather than
appending D5 alongside existing instruments. D1 through D4 were removed. This is a
known REDCap behaviour when uploading a data dictionary without first exporting the
current project state.

### Lesson learned
Always export the current data dictionary before uploading a new one. The export
creates a CSV backup of the entire project that can be re-imported if something goes
wrong. This is standard defensive practice in clinical data management.

### Recovery plan
Regenerate D1 through D4 as individual data dictionaries and re-import each one
using append mode. All field definitions are preserved in project documentation.

---
## 2026-05-11 — Phase 1 CRF complete: all 7 instruments imported via master data dictionary

### What was built
The complete Phase 1 case report form for the dexamethasone PK trial — all seven instruments built and imported into REDCap in a single master data dictionary upload. The CRF is now ready to receive simulated volunteer data.

### Final structure of the Phase 1 CRF
- **D1 Healthy Volunteer Eligibility** — 27 fields covering site identification demographics inclusion criteria exclusion criteria and eligibility conclusion with screen failure branching
- **D2 Demographics and Medical History** — 25 fields with gateway pattern for medical history surgery allergies and current medications
- **D3 Dose Escalation** — 22 fields capturing cohort assignment sentinel dosing rules Safety Review Committee gates escalation decisions and protocol deviations
- **D4 PK Sampling Schedule** — 18 fields designed as a repeating instrument for the 8 timepoints from pre-dose through 48 hours
- **D5 Safety Labs and Vitals** — 32 fields covering vital signs full blood count liver function renal function electrolytes glucose monitoring and investigator review
- **D6 Adverse Events and SAEs** — 16 fields with CTCAE grading causality assessment and regulatory reporting timestamps
- **D7 Volunteer Symptom Diary** — 14 fields capturing daily symptom severity ratings across 7 days post-dose

### Total CRF metrics
- 7 instruments
- Approximately 145 individual fields
- 25 branching logic rules across all instruments
- 2 calculated fields — BMI in D1 and dose per kg in D3
- 14 date fields using ISO 8601 format
- One repeating instrument design (D4 across 8 PK timepoints)

### Standards locked in across every instrument
- All dates use ISO 8601 format YYYY-MM-DD per international regulatory standard
- Units captured in field notes never in field labels following CDISC SDTM convention
- Field labels kept short and clean for readable database column names
- No redundant fields — broader clinical criteria trusted over duplicative narrow checks
- All branching logic uses parser safe syntax that survives data dictionary import

### Hard lessons from this session
- REDCap data dictionary upload defaults to replace mode wiping any instruments not in the uploaded CSV. Lost D1 D2 D3 D4 when uploading D5 alone. Recovered by rebuilding all seven instruments into a single master CSV.
- REDCap calc parser cannot handle fractional negative exponents or the today function during data dictionary validation. Switched eGFR from calculated to plain number field. Switched age from calc to integer entry. Both reflect real clinical workflow — labs report eGFR and nurses calculate age once at screening.
- CSV column alignment is critical. Three rows with one missing empty column caused branching logic syntax errors. Every row must have exactly 18 columns matching the header.
- The defensive workflow is now standard practice — always export current data dictionary before uploading a new one. Treat the export as a backup.

### Next milestone
Set up REDCap events to define the visit schedule — screening dosing day with eight PK timepoints and day 7 follow-up. Then assign instruments to events. After that simulate dummy volunteer data and export to SQL for the analysis pipeline.

---
## 2026-05-11 — REDCap events defined and D5 redesigned with conditional branching

### What was built this session
Two interconnected milestones — first the visit schedule was defined as REDCap events, then a design flaw uncovered during event mapping was fixed by adding conditional branching logic to D5.

### Part 1 — Defined the 10 events of the Phase 1 trial
Set up the longitudinal visit schedule in REDCap Arm 1. The 10 events define the full volunteer journey from screening through 48 hour PK sampling to Day 7 safety follow-up.

The event schedule:
- Screening at Day -7
- Day 0 Dosing
- PK T+30min through PK T+48h covering all 8 pharmacokinetic timepoints
- Day 7 follow-up

Each event has its day offset configured for the visit calendar. Unique event names auto-generated in the format event_name_arm_1 for use in branching logic and SQL queries later.

### Part 2 — Discovered the D5 design flaw during event mapping
While planning which instruments fire at which event, realised D5 Safety Labs and Vitals could not simply fire only at the safety lab events. Vital signs need capturing at every PK timepoint because dexamethasone can cause acute haemodynamic effects within minutes of dosing. But full safety labs do not need to be drawn at every PK timepoint because most steroid-induced lab changes take hours to develop and continuous draws would mean unacceptable blood loss.

The flaw was that D5 as originally designed locked vital signs and labs together — fire D5 at every PK timepoint and waste the nurse time on hidden lab fields, or skip D5 at PK timepoints and miss critical vital sign data.

### Part 3 — Fixed D5 with conditional branching driven by the visit timepoint
Rather than create a separate vital signs instrument or add a redundant gateway field, expanded the existing d5_visit_timepoint dropdown to include all 10 events. Added branching logic to all 17 lab fields plus the investigator review section using the timepoint variable itself as the controller.

The branching condition applied to every lab field is:
[d5_visit_timepoint] = '1' or [d5_visit_timepoint] = '2' or [d5_visit_timepoint] = '7' or [d5_visit_timepoint] = '8' or [d5_visit_timepoint] = '9' or [d5_visit_timepoint] = '10'

This shows lab fields only at Screening, Pre-dose Day 0, PK T+8h, PK T+24h, PK T+48h, and Day 7. At PK timepoints 30min through 4h the form collapses to vital signs only.

### Skills learned and locked in
- The OR operator in branching logic joins multiple value comparisons of the same variable
- AND requires all conditions to be true at once
- Parentheses group conditions when mixing operators
- Don't repeat yourself principle applies to CRF design — if an existing field already carries information, do not add a duplicate gateway field
- One intelligent instrument that adapts via branching is cleaner than two instruments that share concepts
- Event design and instrument design influence each other — discovering structural issues during event mapping is normal and the fix often improves the underlying instrument

### Next milestone
Complete the instrument-to-event assignment grid. Then simulate dummy volunteer data across all 10 events and 18 volunteers. Export to SQL for the analysis pipeline.

---
## 2026-05-11 — Instrument to event assignment complete — Phase 1 CRF fully wired

### What was built
Completed the Designate Instruments for My Events grid in REDCap. Every instrument is now wired to fire at its correct event in the trial timeline. The Phase 1 CRF is structurally complete and ready to receive volunteer data.

### Final assignment grid — 30 ticks total
- D1 Healthy Volunteer Eligibility fires at Screening only — one-time eligibility check
- D2 Demographics and Medical History fires at Screening only — one-time baseline
- D3 Dose Escalation fires at Day 0 Dosing only — single dose per volunteer
- D4 PK Sampling Schedule fires at 8 events from Day 0 through PK T+48h — generates the time-series concentration dataset
- D5 Safety Labs and Vitals fires at every event from Screening through Day 7 — conditional branching controls which fields appear
- D6 Adverse Events and SAEs fires from Day 0 onwards at five events — AEs can emerge any time post-dose
- D7 Volunteer Symptom Diary fires at four events from Day 0 through Day 7 — captures daily symptom severity

### Dataset projection
With 18 volunteers across 3 cohorts and 10 events per volunteer, the trial generates approximately 180 event records. D4 PK Sampling alone produces 8 records per volunteer for 144 total rows of plasma concentration data. D5 produces 10 records per volunteer for 180 rows of vital signs with conditional lab data at the safety checkpoints. This is the dataset that will feed the SQL queries, the Python PK analysis, and the Power BI dashboard.

### How the trial actually flows now
A volunteer enters at Screening where D1 D2 and D5 fire. If eligible they proceed to Day 0 Dosing where D3 D4 D5 D6 D7 all fire — the busiest event in the trial. They then have D4 and D5 firing at every PK timepoint with vitals captured continuously and the full safety panel at T+8h T+24h and T+48h. D7 diary entries are collected at 24h 48h and again at Day 7 follow-up. The trial closes out at Day 7 with final safety labs AE review and diary completion.

### What I learned this session
- Event design and instrument assignment together determine the longitudinal structure of the trial
- The same instrument can fire many times across events — D5 fires 10 times per volunteer because of the branching design
- The Designate Instruments grid is where the visit schedule and the form library become a real database
- Verifying the wiring by adding a test record reveals immediately whether the assignment is correct — each event row should show only the relevant instruments

### Next milestone
Simulate dummy volunteer data — add 18 test records walking through every event for each one. Then export the dataset to SQL and begin the analysis pipeline.

---
## 2026-05-11 — First 2 test volunteers entered + D5 age field cleanup

### What was completed
Entered the first two test volunteer records in REDCap as part of the hybrid data simulation approach. Manual entry validates the form works end-to-end and provides realistic seed data for the Python simulation script that will generate the remaining 16 records.

### The volunteers entered
- Volunteer 001 — Cohort A low dose sentinel position
- Volunteer 002 — Cohort C high dose non-sentinel position

This combination tests both ends of the dose escalation range and exercises the sentinel-specific branching in D3.

### Design improvement discovered during data entry
While completing D5 at the screening event the redundancy of capturing age in both D1 and D5 became obvious. The d5_age_at_visit field was a band-aid added during an earlier data dictionary recovery when the eGFR calc field needed an age reference within the instrument.

Once eGFR was changed from a calculated field to a plain number field reported by the bioanalytical lab the entire reason for d5_age_at_visit disappeared. The field had become orphaned clutter.

### The decision
Deleted d5_age_at_visit entirely. No replacement needed. Age is captured once in D1 at screening and available across all events via REDCap's cross-instrument variable references. No other D5 field needs age for any calculation reference range or branching logic.

### Skills demonstrated this session
- Identifying redundant fields by questioning whether each field earns its place in the instrument
- Recognising that the single source of truth principle applies to demographic data as much as to clinical data
- REDCap cross-instrument variable references make data duplication unnecessary in longitudinal projects
- Real CRF improvement work happens during data entry — the act of using a form reveals design issues that pure design review cannot catch

### Lessons locked in for future instruments
- Before adding a field always check whether the information already exists elsewhere in the project
- When changing one design decision (eGFR calc to plain text) check whether dependent fields are still justified
- Data entry testing is QA — it surfaces issues that need fixing before the trial goes live

### Next milestone
Generate the remaining 16 volunteers via Python data simulation script. Combine with the 2 manual REDCap records to produce the final 18-volunteer dataset ready for SQL export and analysis.

---
## 2026-05-11 — Python dictionary fundamentals completed

### What was learned this session
Worked through five hands-on lessons on Python dictionaries in learning_notes.ipynb. Each concept practised with code that actually ran in Jupyter not just theory. Variables and lists were covered in previous sessions.

### Concepts covered
- Creating dictionaries with key value pairs
- Accessing values by key using square bracket syntax
- Changing existing values and adding new keys
- Looping through dictionaries using keys values and items
- Nested dictionaries where a value is itself another dictionary
- Lists of dictionaries which is the pattern used to represent multiple clinical trial records

### Why this matters for the project
Every simulated volunteer in the upcoming data simulation script will be represented as a nested dictionary. A list of 18 volunteer dictionaries becomes the in-memory dataset before export to CSV. The looping pattern learned this session is the workhorse for processing each volunteer.

### Next milestone
Begin writing the simulate_volunteers.py script. The script will generate 16 realistic dummy volunteers matching the REDCap schema. Combined with the 2 manual records this completes the 18 volunteer Phase 1 dataset.

---