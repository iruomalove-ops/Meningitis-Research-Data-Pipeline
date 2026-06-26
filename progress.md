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
## 2026-05-12 — Python functions fundamentals + data pipeline design philosophy

### What was learned this session
Completed the core Python functions lessons in learning_notes.ipynb — function definition with the def keyword, parameters, return values, and default parameter values. Practised each concept with code that ran successfully in Jupyter.

### Concepts covered
- Defining functions with the def keyword
- Indentation as the structural marker for what belongs inside a function
- Parameters for passing inputs to a function
- Return values for handing results back to the caller
- Default parameter values for optional arguments
- Functions that return dictionaries — the pattern that will drive the simulation script

### Design philosophy locked in
While working through the lessons two important architectural principles emerged that will shape the rest of the project.

First — separation of concerns. The function should handle everything that varies between volunteers and the caller should just ask for a volunteer with minimal inputs. Twenty parameters per function call is no easier than writing the code manually. Hide complexity behind a simple interface.

Second — focus the simulation on analytically meaningful data not realistic-looking identifiers. This is a data analytics portfolio not a data entry system. Nobody will ever look at volunteer 7 individually so the initials and full demographic details do not matter. What matters is that the PK curves are realistic the AE distributions are plausible and the lab values reflect real safety patterns. The identifiers are just sequential labels that link records together.Of course, this approach applies specifically to this project; different projects will require tailored strategies that best suit their unique goals and requirements.
### Why this matters
This thinking applies to every subsequent step in the project. SQL queries focus on aggregate analyses not row-by-row manipulation. Python notebooks automate the calculations that drive insights. Power BI dashboards present aggregate metrics not record drill-downs. The simulation script being built reflects this philosophy from the start.

### Next milestone
Final basics concept — the random module for generating realistic variability. After that begin writing simulate_volunteers.py with the design philosophy applied throughout.

---
## 2026-05-12 — Python random module — final basics lesson complete

### What was learned
Worked through the random module in learning_notes.ipynb. The random module is the engine that drives the simulation script — it generates realistic variability so each call to make_volunteer produces a different result.

### Functions practised
- random.randint for whole number ranges like volunteer age
- random.uniform for decimal ranges like body weight in kilograms
- random.choice for picking one item from a list like cohort assignment or sex
- random.gauss for bell-curve distributions like systolic blood pressure clustered around a mean
- The import statement for loading external modules into a Python script

### Basics milestone complete
Variables types lists tuples dictionaries nested dictionaries lists of dictionaries for loops functions parameters return values default parameters and the random module are all covered. .

### Next milestone
Begin writing simulate_volunteers.py applying the separation of concerns and analytical focus principles established in earlier sessions. The function will generate analytically meaningful data with sequential identifiers and let random produce the variability.

---
## 2026-05-12 — Simulation script design locked — realistic enrolment funnel

### The simulation design philosophy
Decided to build the simulation script as a realistic clinical data engineering pipeline rather than a clean analytical dataset. The script will replicate every REDCap field from every form generating messy real-world style data. This data then flows through Power Query for cleaning before reaching SQL — mirroring exactly how clinical data moves in real pharma and CRO environments where nobody hands you a clean OMOP dataset.

### The enrolment funnel design
The simulation will generate a realistic volunteer journey from screening through trial completion.

- 100 volunteers screened at D1 to generate a meaningful screen failure dataset
- 80 screen failures distributed across multiple realistic reasons including BMI out of range abnormal screening labs prohibited medication volunteer withdrew consent and exclusion criterion present
- 20 eligible volunteers progress to randomisation and complete D2 and subsequent instruments
- 2 dropouts at random points during the trial to capture realistic missing data patterns
- 18 volunteers complete the full PK schedule with all 8 timepoints

### Output structure
One CSV file per instrument matching REDCap export naming conventions. After all instruments are generated the CSVs combine into a single Excel workbook with one sheet per instrument. This Excel file becomes the input to the Power Query cleaning stage.

### Build approach locked in
Start with D1 only. Build it. Test it. Confirm the CSV looks right. Only then add D2 D3 D4 D5 D6 D7 one at a time. Each instrument is its own focused piece of work.

### Why this approach matters for the portfolio
Demonstrates understanding of the real clinical data engineering pipeline not just analytical work. Shows familiarity with realistic data quality issues missing values and screen failure analysis. Sets up Power Query skills, Produces an audit trail of decisions that mirror how a clinical data manager actually works.

### Next milestone
Begin writing simulate_volunteers.py starting with the file header imports 

---
## 2026-05-12 — D1 simulation script complete — 100 volunteer records generated

### What was built
Wrote simulate_volunteers.py from scratch. The script generates 100 simulated healthy volunteer screening records matching the REDCap D1 instrument schema with realistic enrolment funnel dynamics. Output saved to d1_eligibility.csv ready for the Power Query cleaning stage.

### The functional pieces
- File header docstring and imports of random, csv and datetime modules
- D1 template dictionary defining 26 fields with REDCap coded value placeholders
- make_d1_record function that generates one volunteer with random demographics and derives eligibility from inclusion exclusion criteria
- Loop calling the function 100 times to build a list of 100 records
- CSV export using csv DictWriter with field order driven by the template

### Realistic features built in
- Sequential site IDs in ZA-CPT-P1-001 format
- Dates of birth generated as real random dates not just year variations
- Sex-dependent weight and height distributions using bell curves
- BMI calculated from generated weight and height
- Inclusion criteria I1 and I2 derived deterministically from age and BMI
- Inclusion criteria I3 I6 I7 generated with realistic probabilities
- Nine exclusion criteria with realistic probability rates per clinical context
- E5 pregnancy field empty for non-female volunteers matching REDCap branching behaviour
- Eligibility determination derived from all I and E values using all and any
- Screen failure reason coded based on which criterion actually failed
- All REDCap coded values used throughout matching real export format

### Skills demonstrated and learned
- Python language fundamentals applied to a real problem
- Function design with single source of truth principle
- Branching logic and comparison operators
- List comprehensions with all and any built ins
- File I O with the with statement and DictWriter
- Date arithmetic using timedelta
- Debugging real errors including variable name mismatches case sensitivity and hyphen versus underscore confusion
- The discipline of testing each line before moving on

### Output produced
d1_eligibility.csv with 100 rows and 26 columns matching the D1 instrument structure. Roughly 80 percent of records show as screen failures with reason codes derived from their actual criterion failures. Approximately 20 percent show as eligible ready for D2 enrolment.

### Next milestone
Build make_d2_record using the same pattern. D2 only generates for the 20 eligible volunteers from D1 establishing the enrolment funnel through to randomisation.

---
## 2026-05-15 — D2 step 1 complete — read D1 CSV and filter to eligible volunteers

### What was built
Started simulate_d2.py with the new Python concept of reading a CSV file into Python and filtering rows by a condition. The script reads d1_eligibility.csv produces a list of 100 D1 records then filters to the 20 volunteers whose eligibility determination is 1. Those 20 are exported to eligible_volunteers.csv as a reference dataset.

### New Python concepts applied
- csv DictReader for parsing CSV files into lists of dictionaries
- The string vs integer, when reading from CSV all values come back as strings
- Filtering a list using a for loop and conditional append
- Using existing record keys as fieldnames when there is no separate template

### The enrolment funnel narrowing visible
Started with 100 screened volunteers in D1. Filtered to 20 eligible by eligibility determination equals 1. The screen failure rate of 80 percent matches realistic clinical trial recruitment statistics. Those 20 eligible volunteers become the input to all subsequent instruments.

### Output produced
eligible_volunteers.csv with 20 rows and 26 columns containing the full D1 record for each eligible volunteer. This file is a checkpoint not a deliverable. The actual D2 demographics generation continues in the next step.

### Next milestone
Build the D2 schema template and generate demographics fields race ethnicity vital signs lifestyle and medical history gateways for each of the 20 eligible volunteers.

---
## 2026-05-15 — D2 simulation script complete — 20 demographics and medical history records

### What was built
Built simulate_d2.py from scratch using the same pattern locked in with simulate_d1.py. The script reads d1_eligibility.csv filters to the 20 eligible volunteers and generates a complete D2 record for each one. Output saved to d2_demographics_medical_history.csv ready for the next pipeline stage.

### The functional pieces
- File docstring and imports of random csv and string modules
- Country code lookup lists at the top of the file SA_CODE AFRICAN_CODES and REST_OF_WORLD_CODES
- D2 schema template with 25 fields including identifier vital signs medical history gateways lifestyle vaccination and PI assessment
- Read D1 CSV using csv DictReader and filter to eligible volunteers using a for loop with conditional append
- make_d2_record function generates a complete D2 record from one eligible D1 volunteer
- Loop calling make_d2_record for each of the 20 eligible volunteers
- CSV export using DictWriter with field order driven by d2_template

### New Python concepts learned this session
- csv DictReader for parsing CSV files into lists of dictionaries
- Filtering a list using a for loop and conditional append
- The string vs integer when reading CSV all values come back as strings
- The string module for ascii_uppercase letters used to build initials
- The max function for flooring negative random gauss values at zero
- Two stage random choice for country generation pick category then pick specific code
- Multi line if statement using parentheses for readability when conditions span multiple lines

### Realistic features built in
- Initials generated as random three uppercase letters per volunteer
- Race weighted to match Cape Town demographics 70 percent Black African 18 percent Coloured
- Ethnicity heavily weighted to Not Hispanic matching ZA population
- Country birth uses two stage logic 80 percent South Africa 15 percent specific African migrant countries 5 percent rest of world
- African migrant countries restricted to seven realistic Cape Town communities Nigeria Zimbabwe Malawi Lesotho Somalia DRC Mozambique
- Vital signs use bell curve distributions with realistic means and standard deviations
- SpO2 uses random integer between 97 and 100 to guarantee clinically realistic values
- Four medical history gateway pairs follow the if Yes populate details else empty pattern
- Lifestyle factors use bell curves floored at zero for alcohol and caffeine
- Exercise frequency weighted toward moderate to high activity matching healthy adult volunteers
- PI assessment derived from structured fields as either Excellent health or Good health

### Output produced
d2_demographics_medical_history.csv with 20 rows matching the eligible volunteers from D1. Each row has 25 fields populated with realistic clinically appropriate values.

### Cumulative enrolment funnel status
- D1 100 screened generated as d1_eligibility.csv
- D1 20 eligible exported as eligible_volunteers.csv reference checkpoint
- D2 20 records generated for the eligible volunteers
- D3 through D7 will continue applying the same architectural pattern

### Next milestone
Build simulate_d3.py for the dose escalation instrument. D3 fires once per eligible volunteer at Day 0 dosing. Will introduce cohort assignment based on enrolment order and sentinel positioning within cohorts.

---
## 2026-05-15 — Critical design flaw discovered — Identifier Block needed across all instruments

### What was discovered
While planning D3 dose escalation realised the trial design has a referential integrity problem. D1 has site_id as a unique key but D2 has no identifier connecting back to D1. D3 through D7 would inherit this problem. Without a shared identifier across instruments no SQL JOIN works and no Power BI cross-instrument analysis is possible.

### The clinical context
Real clinical trial datasets follow CDISC SDTM standards where every domain begins with an Identifier Block of common variables. These let you trace any record back to its volunteer their cohort their visit and the exact moment of collection. The first thing regulators check during submission is whether all datasets share the subject key.

### The Identifier Block design
Six identifiers will appear at the top of every record in every instrument from D1 onwards.

- site_id format P1-NNN universal screening identifier assigned at first contact every screened volunteer gets one
- subject_id format SUB-NNNN random four digit randomisation identifier assigned only to volunteers who proceed to dosing screen failures and not randomised volunteers get empty value
- visit_id descriptive labels SCR DOSING T30M T1H T2H T4H T8H T24H T48H D7 identifies which trial visit a record was collected at
- record_id format site_id-DN-visit unique row identifier within an instrument example P1-001-D4-T30M
- cohort_id format COHORT-X dose cohort assignment values COHORT-A COHORT-B COHORT-C empty before randomisation
- timestamp_collected format YYYY-MM-DD HH:MM:SS exact date time of collection important for D4 PK timing

### The design decision rationale
Random non-sequential subject_id matches real trial blinding practice. Sequential subject IDs would reveal dosing order. Descriptive visit_id reads naturally in dashboards and queries unlike numeric visit codes. Record_id with descriptive suffix lets you identify a record at a glance versus opaque UUID format. Dropping site code ZA-CPT from the prefix removes constant clutter while keeping P1 prevents collision when Phase 2 and Phase 3 work join the portfolio later.

### Implementation plan
Create identifiers.py shared module containing generator functions for all 6 identifiers. Retrofit simulate_d1.py and simulate_d2.py to use the new Identifier Block. Regenerate both CSVs with proper identifiers. Update the REDCap CRF to include matching Identifier Block fields so the actual form captures what the simulation generates. All subsequent instruments D3 through D7 will use the same architecture from the start.

### What this teaches
The single source of truth principle applied to identifiers. The DRY principle through a shared identifier module. CDISC SDTM standards which are the regulatory expectation for clinical datasets. Real data engineering happens iteratively as design flaws surface during implementation not before.

### Next milestone
Update REDCap forms with the Identifier Block then build identifiers.py shared module then retrofit D1 and D2 simulation scripts before continuing to D3.

---
## 2026-05-15 — Architectural pivot — leverage REDCap built-ins instead of custom Identifier Block

### What changed
Reversed the decision to build a custom Identifier Block across all instruments. After spotting the variable name uniqueness rule in REDCap realised the custom approach would force ugly naming patterns like d1_p1_subject_id and would not scale. More importantly realised REDCap already provides relational integrity natively through record_id and redcap_event_name and redcap_repeat_instance which appear automatically in every longitudinal project export.

### The new approach
Use REDCap built in identifiers for relational linkage. Update the Python simulation to add the same three columns to every output CSV so the simulated data matches real REDCap export format. This is more authentic professionally and easier to maintain.

### What REDCap provides natively
- record_id — primary key for each volunteer assigned automatically at first contact appears in every record
- redcap_event_name — identifies which event the row belongs to such as screening_arm_1 day_0_dosing_arm_1 pk_t30min_arm_1
- redcap_repeat_instance — sequence number for repeating instruments such as D4 PK timepoints

### Rollback actions
Delete the four custom Identifier Block fields previously added to D1 . Restore screening_date and screened_by to original positions. The Python simulation scripts need updating to add the three REDCap auto columns to all CSV outputs.

### Architectural lesson
Before building custom infrastructure check whether the platform you are using already solves the problem. REDCap is a relational database and its longitudinal data model provides the linkage we were trying to recreate. Real CRF teams leverage these built ins rather than recreating them.

### Next milestone
Roll back the REDCap Identifier Block fields. Update simulate_d1.py and simulate_d2.py to add record_id redcap_event_name and redcap_repeat_instance columns to their CSV outputs. Regenerate the CSVs. Continue with D3 onwards using this corrected architecture.

---
## 2026-05-15 — Referential integrity restored — record_id added across D1 and D2

### What was fixed
Closed the referential integrity gap discovered earlier where D1 had a unique identifier but D2 had no column linking back. Without a shared key column the two CSVs could not be joined in SQL or related in Power BI. The fix involved two architectural changes in simulate_d1.py and simulate_d2.py.

### Changes to simulate_d1.py
Renamed the existing site_id variable to record_id everywhere it appears in the script. The variable name now matches REDCaps native primary key column convention. The values stay as ZA-CPT-P1-NNN format because only one site means site_id was misleading anyway. The d1_eligibility.csv now uses record_id as its first column header.

### Changes to simulate_d2.py
Added record_id as the first field in d2_template. Updated the make_d2_record function return statement to pull record_id from the d1_record parameter using d1_record[record_id]. The make_d2_record function already received the d1_record as input so the data was available, we just had to use it. The d2_demographics_medical_history.csv now has record_id as its first column with values matching the eligible volunteers from D1.

### Verification
Opened the regenerated d2 CSV. First column header is record_id. First few records show values like ZA-CPT-P1-001 ZA-CPT-P1-004 ZA-CPT-P1-005. These match the eligible volunteers from D1. Twenty rows of data plus one header row. The CSVs can now be joined on record_id in SQL.

### Architectural pattern locked in for all future instruments
Every instrument template starts with record_id as the first field. Every make_dN_record function takes the parent record as input and pulls record_id forward. This guarantees every CSV joins cleanly to D1 through the shared record_id column.

### Lesson learned
Referential integrity must be designed in from the start of every instrument. Trying to add it retroactively is doable but messy. Going forward D3 through D7 will include record_id in their templates as the first field by default and the make_dN_record functions will pull it from the parent record. The pattern is now muscle memory.

### Next milestone
Build simulate_d3.py for the dose escalation instrument. D3 fires once per eligible volunteer at Day 0 dosing. Will introduce cohort assignment based on the stratified randomisation workflow.

---
## 2026-05-16 — D3 simulation Sections 1-6 complete — block randomisation working

### What was built in this session
Built simulate_d3.py through Section 6 of the planned 9-section architecture. Completed configuration setup data loading stratification block randomisation and reserve handling. Section 7 the make_d3_record function partially completed and parked for a design review.

### Architectural decisions locked in this session

**Random seed for reproducibility.** Added random.seed(42) to both simulate_d1.py and simulate_d2.py. Every run now produces identical data which makes debugging easier and matches real clinical trial standards where reproducible randomisation is a regulatory requirement.

**Stratified block randomisation algorithm fully implemented.** The script reads D2 stratifies volunteers into three piles based on pi_assessment and family_history then block randomises 1 Excellent plus 2 Standard plus 3 Family History into each of three cohorts. Six volunteers per cohort 18 dosed total. Sentinels are positions 1 and 2 in each cohort.

**Reserve handling shifted from upfront withdrawal to natural leftovers.** Original design pulled 2 reserves from Family History upfront. After locking the random seed D2 produced 28 eligible volunteers with 16 Standard 9 Family History and 3 Excellent. With Family History now exactly matching the 9 needed for randomisation reserves naturally emerge from the overrepresented Standard pile. Old Section 3 disabled and commented in place as design history.

**Cleanup of weight_kg in Section 5.** Removed the line that tried to access weight_kg from D2 records because D2 does not carry that field. Created a separate D1 weight lookup dictionary used by Section 7 for dose calculations.

### New Python concepts learned this session
- random sample for picking k unique items without replacement
- random shuffle for in place list reordering
- list pop with index zero for sequential removal from front of a list
- list extend for adding all items from one list to another
- enumerate with start argument for getting position and item simultaneously
- ternary expression for one line if else assignments
- nested for loops for cohort and position iteration
- sum with generator expression for counting matching items
- datetime strptime and strftime for date string conversion
- timedelta for date arithmetic
- dictionary based lookup for cross instrument data access

### Output produced through Section 6
- assignments list with 28 entries
- 18 marked Randomised with cohort assignment cohort_position and is_sentinel
- 10 marked Reserve with empty cohort fields
- All 28 reference back to D1 via record_id

### Design discovery to revisit
While building Section 7 surfaced a real clinical question about temporal reality. The D3 instrument as currently designed includes fields that get filled at different times in real trials. Cohort assignment and dose info on Day 0. Sentinel review on Day 2. DLT observations after Day 7. SRC decision after Day 14. Protocol deviations throughout. The simulation generates this as end state data which is realistic for analytical purposes but hides the staged data entry pattern. Parked for design review next session. Three options to consider Option A keep as is Option B split into temporal sub instruments Option C keep one instrument with documentation.

### Next milestone
Resume Section 7 once temporal design question is resolved. Complete make_d3_record function then Section 8 loop and Section 9 CSV export. Then move to D4 PK sampling which is the most important instrument for the entire trial because it produces the PK curves that drive the Power BI dashboard.

---
## 2026-05-16 — D3 split into D3a and D3b for temporal accuracy

### What was decided
Split the D3 dose escalation instrument into two separate instruments to respect the temporal reality of how clinical trial data actually gets captured. The original single D3 instrument tried to hold data points that get filled at completely different times across multiple weeks of trial activity which created confusion about when to fill each field. The split solves this by separating Day 0 dosing decisions from the Day 2 through Day 21 safety review and escalation decisions.

### D3a Dose Assignment and Administration
Eleven fields. Day 0 instrument. All 28 eligible volunteers receive a record including the 10 Reserves. Captures cohort assignment cohort position sentinel status cohort opening date planned dose dose per kilogram IMP batch IMP expiry and PI dosing sign off. Reserves receive a record with cohort fields empty.

### D3b Safety Review and SRC Escalation
Fourteen fields. Day 2 through Day 21 instrument. Only the 18 Randomised volunteers receive a record because Reserves are never dosed and have no safety follow up to record. Captures sentinel 48 hour review DLT observation SRC escalation decision protocol deviations and PI escalation sign off. Six fields use branching logic.

### Branching logic in D3b
The branching rules respect the conditional nature of clinical observations.
- sentinel_48h_pass and sentinel_review_date only appear if D3a is_sentinel equals 1
- dlt_description only appears if dlt_observed equals 1
- deviation_details deviation_reported and deviation_ethics only appear if deviation_any equals 1

### Field removed and deferred for later work
The cohort_pk_complete field was removed from D3b during the split because it represents a different concept than escalation decisions. PK completion is operational lab data about whether all 8 PK timepoints were successfully collected for each volunteer. This is naturally derivable from D4 PK sampling data by counting records per volunteer. Capturing it as a form field is redundant and risks data disagreement with the actual D4 records. Future implementation will be either a SQL view a Power BI calculated measure or a separate cohort summary instrument. Decision deferred to a later milestone after D4 is built and we have actual PK records to derive from.

### Architectural lesson
CRF design needs to respect the temporal flow of data capture. Fields that get filled at the same time and in the same context belong in the same instrument. Fields that get filled weeks apart belong in separate instruments even if they cover related concepts. The D3 split is a small example of a much bigger discipline that real clinical data managers practice constantly.

### Next milestone
Complete simulate_d3a.py with sections 7 8 and 9. Then build simulate_d3b.py from scratch following the same architectural pattern. After both are working continue to D4 the PK sampling instrument which is the most important data driver for the entire trial and will produce the dose response curves that anchor the Power BI dashboard.

---
## 2026-05-16 — simulate_d3a.py complete — 28 dose assignment records generated

### What was built
Completed simulate_d3a.py through all 9 sections. The script reads the D2 demographics CSV stratifies volunteers into 3 health based piles performs stratified block randomisation across 3 dose cohorts identifies leftover volunteers as reserves and exports a complete D3a CSV with dose assignment data for all 28 eligible volunteers.

### The complete pipeline now produces three CSVs from one starting seed
- d1_eligibility.csv with 100 screened volunteers and eligibility outcomes
- d2_demographics_medical_history.csv with 28 records for eligible volunteers
- d3a_dose_assignment.csv with 28 records of which 18 are Randomised and 10 are Reserve

### Architectural patterns locked in
- record_id flows through all instruments providing referential integrity
- Random seed 42 in simulate_d1 and simulate_d2 ensures reproducible data
- Stratified block randomisation distributes 1 Excellent plus 2 Standard plus 3 Family History per cohort exactly matching the 9 needed and using all available Excellent volunteers
- Reserves emerge naturally as the leftover Standard volunteers from the overrepresented stratum
- Sentinel selection is the 2 first volunteers of each cohort by enrolment order Position 1 is the Excellent volunteer Position 2 is one of the Standard volunteers

### Python concepts demonstrated
random sample random shuffle list pop with index zero list extend enumerate with start argument ternary expressions nested for loops sum with generator expressions datetime strptime and strftime timedelta dictionary based lookup using d1_weights to fetch weight data from D1 conditional return statements for Randomised versus Reserve handling

### Output data quality
- Each Randomised volunteer has cohort 1 2 or 3 with full dose information batch number expiry and PI signoff
- Each Reserve volunteer has empty cohort fields and enrolment_status equals Reserve
- 6 sentinels are flagged is_sentinel equals 1 across the 3 cohorts
- dose_per_kg auto calculated from planned_dose_mg and weight_kg pulled from D1
- imp_batch follows cohort specific format DEX-P1-2MG-L01 DEX-P1-4MG-L01 DEX-P1-8MG-L01

### Next milestone
Build simulate_d3b.py from scratch following the same architectural pattern. D3b will read d3a_dose_assignment.csv filter to Randomised volunteers only and generate the 14 field safety review and SRC escalation records for the 18 dosed volunteers. After D3b is complete move on to simulate_d4.py which generates PK sampling records and is the most important data driver for the entire trial because it produces the concentration time curves that anchor the Power BI dashboard.

---
## 2026-05-16 — simulate_d3b.py complete — 18 safety review records generated

### What was built
Completed simulate_d3b.py from scratch in six sections. The script reads d3a_dose_assignment.csv filters to the 18 Randomised volunteers and generates the safety follow up and SRC escalation data for each one. Reserves are correctly excluded because they were never dosed and have no safety follow up data to record.

### How D3b differs from D3a architecturally
D3a captures dosing decisions at Day 0 for all 28 eligible volunteers including Reserves. D3b captures post dose safety outcomes across Day 2 through Day 21 for the 18 dosed volunteers only. 

### Clinical logic implemented in D3b
- Sentinel 48 hour review fields populated only for the 6 sentinel volunteers based on is_sentinel value from D3a
- Sentinel review date calculated as cohort_open_date plus 2 days using datetime strptime and strftime
- DLT observed at a 5 percent rate with realistic CTCAE Grade 3 narrative descriptions when positive
- SRC meeting date calculated as cohort_open_date plus 21 days
- SRC decision driven by DLT outcome escalate to next dose if no DLT or repeat current dose if DLT observed
- Protocol deviations at a 10 percent rate with realistic narrative descriptions and reporting fields
- PI escalation sign off randomly selected from the three site investigators

### Cross instrument data flow demonstrated
D3b reads from D3a CSV and uses record_id to link back. Cohort_open_date from D3a drives sentinel_review_date and src_meeting_date in D3b through timedelta arithmetic. This is the first instrument that reads its parent record data and performs calculations across that linkage. Establishes the pattern for D4 D5 D6 D7 which will all read upstream data.

### Complete pipeline status now
Four instruments built out of eight total.
- simulate_d1.py 100 screened records eligibility outcomes
- simulate_d2.py 28 eligible records demographics and medical history
- simulate_d3a.py 28 dose assignment records 18 Randomised plus 10 Reserve
- simulate_d3b.py 18 safety review and SRC escalation records

### Next milestone
Build simulate_d4.py for the PK sampling instrument. D4 is the most important instrument for the entire trial because it produces the concentration time curves that anchor the entire PK analysis and the Power BI  dashboard. D4 introduces the repeating instrument pattern because each Randomised volunteer has 8 PK timepoint records SCR DOSING T30M T1H T2H T4H T8H T24H T48H D7. 

---
## 2026-05-16 — Event grid updated for D3a D3b split — SRC Review event added

### What was decided
After splitting D3 into D3a Dose Assignment and D3b Safety Review the event grid needed updating to reflect when each instrument actually fires. Added a new event called SRC Review at Day 21 offset to capture when the Safety Review Committee formally meets and signs off on dose escalation decisions. D3a fires at the Day 0 Dosing event. D3b fires only at the new SRC Review event with sentinel review fields filled retrospectively from Day 2 notes.

### The complete event grid now has 11 events
Screening Day -14, Day 0 Dosing, PK T+30min, PK T+1h, PK T+2h, PK T+4h, PK T+8h, PK T+24h, PK T+48h, Day 7 follow up, SRC Review Day 21.

### The instrument to event mapping
D1 and D2 fire at Screening only. D3a fires at Day 0 Dosing only. D3b fires at SRC Review only. D4 PK Sampling fires at all 8 PK timepoints plus Day 7 final sample. D5 Safety Labs fires at T+48h for sentinel review plus Day 7 follow up. D6 and D7 fire at Day 7.

### Design rationale for D3b at SRC Review only
Considered mapping D3b to multiple events which would produce multiple D3b records per volunteer. Rejected because one record per volunteer keeps the data clean and matches what the Python simulation already produces. Sentinel review data is retrospectively recorded at the SRC Review event which mirrors how real clinical data managers complete safety review forms at the formal decision point. The two sentinel specific fields use branching logic so they only display for actual sentinels.

### Next milestone
Build simulate_d4.py for the PK sampling instrument. D4 will be the first repeating instrument because each Randomised volunteer has 9 PK timepoint records across the events T+30min through D7. This introduces the redcap_repeat_instance column and the repeating measures pattern that drives the entire pharmacokinetic analysis.

---
## 2026-05-17 — D4 PK sampling fully planned — IV one-compartment model locked in

### What was decided in this session
Completed the full design plan for D4 the PK sampling instrument before writing any simulation code. Three planning buckets resolved: the pharmacokinetic science, the repeating-instrument structure, and the field mapping against the existing REDCap instrument.

### The pharmacokinetic science
Chose a real one-compartment PK model over a faked rise-and-fall shape because portfolio credibility depends on the science being authentic and the PK curve is where clinical domain knowledge becomes visible in the data.

Chose IV dosing rather than oral. Reasoning is that this is a safety study not an absorption study. IV gives 100 percent bioavailability and removes between-person absorption variability so any differences in exposure come from elimination and distribution not from gut absorption. This is correct first-in-human safety sequencing. Oral absorption can be studied later once safety is established.

IV dosing removes the absorption phase so the model simplifies from the two-exponential oral form to a single decay equation C of t equals D over V times e to the power minus ke times t. Concentration peaks instantly at dosing then decays.

### PK constants locked in with literature support
Half-life t-half equals 4 hours. Supported by StatPearls NIH reference giving mean terminal half-life of 4 hours and a pediatric PK review noting 4 to 9 hours for CYP3A4 metabolism. Elimination rate constant ke equals 0.693 divided by 4 equals 0.173 per hour.

Volume of distribution V equals 1.0 litres per kilogram of body weight. Supported by published weight-normalized values ranging 0.41 to 1.0 L per kg in healthy adults. V is computed per volunteer from their D1 weight so curves differ between volunteers naturally through real body weight differences. Lighter volunteers reach higher peaks heavier volunteers reach lower peaks. This is genuine physiology not artificial noise.in future if they are any discripancies it could be traced right back to this origin.

Output converted to nanograms per millilitre by multiplying mg per litre by 1000. Plus or minus 5 percent assay measurement noise added to each value so plotted points scatter realistically around the model curve like real lab data.

### Scientific coherence with eligibility design
Confirmed that dexamethasone is metabolized by CYP3A4 which is exactly why D1 exclusion criterion e1_cyp3a4 screens out CYP3A4 modulators. The eligibility logic and the PK model are scientifically consistent. Anyone on a CYP3A4 inhibitor or inducer would have a distorted elimination curve.

### The repeating-instrument structure
D4 is the first repeating instrument. Each volunteer has 8 PK timepoint records not one. The redcap_repeat_instance column distinguishes the 8 draws for the same record_id. Together record_id and redcap_repeat_instance uniquely identify each row. This creates a one-to-many relationship where one D1 or D3a record matches 8 D4 rows.

Eight timepoints confirmed matching the existing REDCap dropdown: Pre-dose T0, 30 minutes, 1 hour, 2 hours, 4 hours, 8 hours, 24 hours, 48 hours. T0 is the pre-dose baseline and reads BLQ since no drug is on board. Dropped the Day 7 PK draw because with a 4 hour half-life the drug is fully cleared by 48 hours so a Day 7 sample would add no information. Day 7 remains a safety follow-up visit for adverse events and labs not PK.

Dropped the artificial dropout idea entirely. That concept belonged to the earlier 20-volunteer scenario. With 18 clean randomised volunteers and 10 separate reserves there is no need to force missing data. All 18 volunteers get all 8 timepoints giving 144 PK records total.

### LLOQ decision
Lower limit of quantification set at 0.5 ng per mL rather than 1.0. Reasoning is that this safety-focused PK wants the most sensitive assay so late low concentrations can be measured and confirmed declining toward zero rather than hidden behind a BLQ flag. The goal is confirming safe clearance in all groups not characterising potency. At 0.5 the 24 hour timepoint stays quantifiable for essentially all cohorts and the 48 hour timepoint correctly goes BLQ everywhere confirming clearance. T0 always BLQ as pre-dose baseline.

### REDCap edit plan for D4 timing fields
The original D4 had three fragmented timing fields: sample_date holding only the date, scheduled_time holding only HH:MM, and actual_time holding only HH:MM. The problem with this split is that time was not a directly calculable variable. To work out elapsed time since dosing for the PK curve you would have to stitch the separate date and time fields back together first, which is awkward and error prone.

Collapsing into two complete datetime fields solves this. scheduled_datetime and actual_datetime each hold a full date and time to the minute in one field. Elapsed time since dosing then becomes a simple subtraction of two complete timestamps with no reassembly needed, which makes the PK time axis a genuinely calculable variable rather than something pieced together from fragments.

### Field mapping confirmed
Dose stays in D3a and weight stays in D1 joined to D4 via record_id rather than duplicated. PK parameters Cmax Tmax AUC clearance are derived in the analysis layer not stored in D4 following single source of truth. D4 captures the irreducible requirement which is concentration paired with time. sample_collected always Yes since no dropouts so the missed_reason branch stays empty. Logistics fields filled with realistic clinical defaults. plasma_concentration computed from the model. blq derived against the 0.5 threshold.

### Next milestone
Make the D4 timing field edits in REDCap. Regenerate the master data dictionary. Then map the D4 build into a section list and build simulate_d4.py section by section. D4 introduces the nested loop generating 8 timepoint rows per volunteer and the exponential decay calculation for plasma concentration.

---
## 2026-05-17 — D4 timing fields edited and verified — planning complete

### What was changed in REDCap
Collapsed the three fragmented D4 timing fields into complete datetime fields so that time becomes a directly calculable variable rather than something reassembled from separate date and time pieces. Removed sample_date scheduled_time and actual_time. Added scheduled_datetime and actual_datetime both as Text Box fields with datetime_ymd validation for to-the-minute precision. Also updated centrifuge_time to a datetime format for consistency with the other timing fields.

### Why datetime fields matter
With the old split design working out elapsed time since dosing meant stitching a separate date field back together with a separate time field before any arithmetic was possible. The complete datetime fields make elapsed time a simple subtraction of two timestamps which is what the PK time axis calculation actually needs. Keeping scheduled and actual as two separate datetime fields also preserves the sampling window deviation story since the difference between them shows how far each draw drifted from plan.

### Verification against the live instrument
Downloaded the D4 data dictionary from REDCap and confirmed the edit landed correctly. The three old fields are gone. The two new fields exist with the exact variable names scheduled_datetime and actual_datetime. Both carry datetime_ymd validation. Field count is now 16 down from 17 as planned. The variable names are confirmed so the simulation can reference them as dictionary keys with no risk of a column name mismatch when the CSV joins downstream.

### Final confirmed D4 field list in order
record_id and redcap_repeat_instance as identifiers then timepoint scheduled_datetime actual_datetime sample_collected missed_reason cannula_site sample_volume tube_type centrifuge_time plasma_aliquoted storage_temp shipped plasma_concentration blq assay_date sample_notes.

### Status
D4 planning is now fully complete. Science locked IV one-compartment model with confirmed constants. Structure locked repeating instrument 18 volunteers times 8 timepoints equals 144 records no dropouts. Field list locked and verified against the live REDCap form. Ready to build simulate_d4.py.

### Next milestone
Map simulate_d4.py into a section plan then build it section by section. The two genuinely new pieces are the nested loop generating 8 timepoint rows per volunteer and the exponential decay calculation for plasma concentration. Everything else reuses established patterns.

---

## 2026-05-31 — simulate_d4.py complete — 144 PK sampling records generated

### What was built
Completed simulate_d4.py in seven sections. The script reads d3a_dose_assignment.csv to find the 18 Randomised volunteers, pulls each volunteer's weight from d1_eligibility.csv, then generates 8 PK timepoint records per volunteer using an IV one-compartment pharmacokinetic model. Output is 144 records saved to d4_pk_sampling.csv with full referential integrity back to D1 and D3a via record_id.

### The pharmacokinetic model implemented
IV one-compartment model with the equation C(t) = (D/V) * exp(-ke*t). KE = 0.173 per hour derived from a 4-hour plasma half-life. V is computed per volunteer as 1.0 L/kg times their body weight from D1, so the volume of distribution varies between volunteers based on real measured weight. The dose D comes from D3a per cohort. Concentration output is in ng/mL after a multiplicative conversion from mg/L. Plus or minus 5 percent multiplicative assay noise applied to simulate LC-MS measurement variability. Pre-dose T0 forced to zero. Below-limit-of-quantification rule applied at LLOQ = 0.5 ng/mL.

### Why this matters scientifically
The curve shape is now genuine pharmacology. Concentrations rise instantly to peak at dosing, decay exponentially over the 48 hours, and fall to BLQ at the tail. Light volunteers reach higher peaks than heavy volunteers from the same dose because V scales with weight, and the 8mg cohort reaches roughly four times the peak of the 2mg cohort because dose scales linearly. The Power BI dashboard will eventually show three distinct curves separated by cohort dose, with realistic scatter from assay noise rather than implausibly smooth lines.

### First repeating instrument in the project
D4 is structurally different from D1, D2, D3a, D3b. Each volunteer has 8 records not 1, distinguished by redcap_repeat_instance counting 1 through 8 within each volunteer. The nested loop pattern generates these by looping volunteers on the outside and timepoints on the inside, with an independent repeat_instance counter that resets at the start of each volunteer.

### Defensive coupling decision
Initial draft of the nested loop used enumerate to produce a single position variable doing double duty as both the redcap_repeat_instance value and an implicit assumption that timepoint codes matched their list position. Caught this as a silent coupling risk before pasting and refactored to compute the two variables from independent sources. redcap_repeat_instance now comes from a manually incremented counter that resets per volunteer. timepoint code still comes from the TIMEPOINTS dictionary. The values are currently identical but are now structurally independent, so any future change to TIMEPOINTS order or content cannot silently mis-label rows. Comment in the section explains the discipline for future readers.

### New Python concepts learned this session
- math.exp for the exponential decay calculation
- random.uniform for flat-distribution random factors in the noise model
- multiplicative noise applied to true concentration to produce measured concentration
- datetime.strptime to parse a constructed date plus time string into a datetime object
- f-string formatting with the :02d width specifier for zero-padded integers
- timedelta arithmetic with hours, minutes, days
- the difference between additive and multiplicative noise models in measurement science
- the "true vs measured" distinction in PK simulation

### Verification on the output
All 18 volunteers have exactly 8 records each. T0 is 18/18 BLQ as expected pre-dose. 48 hours is 18/18 BLQ as expected post-elimination. Middle timepoints show plasma concentrations with realistic scatter from the assay noise. 24 hours shows partial BLQ depending on dose and weight which matches the LLOQ design.

### Complete pipeline status
Five simulation instruments built out of eight total.
- simulate_d1.py 100 screened records
- simulate_d2.py 28 eligible records
- simulate_d3a.py 28 dose assignment records (18 Randomised + 10 Reserve)
- simulate_d3b.py 18 safety review records
- simulate_d4.py 144 PK sampling records

### Next milestone
Build simulate_d5.py for the safety labs and vitals instrument. D5 is the second repeating instrument because each volunteer has labs and vitals captured at multiple events (T+48h sentinel review for sentinels, Day 7 follow-up for all). Will reuse the nested loop pattern from D4 but with conditional logic for which volunteers fire at which events.

---
## 2026-06-02 — D5 architectural cleanup — event-name branching and timepoint field removal

### What was done this session
Diagnosed and resolved a self-referencing branching bug in D5, replaced the broken custom-timepoint approach with event-name branching, removed the redundant d5_visit_timepoint field, and tested the form across all relevant events to confirm correct conditional rendering.

### The bug that surfaced first
The d5_visit_timepoint field had branching logic referencing its own value: [d5_visit_timepoint] = '1' or '2' or '7' or '8' or '9' or '10'. This is a logical paradox where the field needed a value to be visible but could not receive a value because it was hidden. REDCap parses this as syntactically valid but it can never satisfy itself. The field rendered in Designer but never in data entry across any event. Worse the branching referenced codes 7 8 9 10 which were not in the current dropdown which only contained 1 through 6. Stale branching pointing at codes that no longer existed.

### The design tension this exposed
D5 captures both vital signs and lab results. Vitals get taken at most events (screening dosing day every PK timepoint and follow up). Labs are only drawn 3 times in the trial. With both in one form mapped to all vitals events the user would see a long stretch of empty lab fields at vitals-only events which is a real data entry burden and clarity problem. Empty for a reason looks identical to empty by mistake. The original d5_visit_timepoint field was an attempt to solve this by conditionally hiding lab fields at vitals-only events but the implementation was wrong.

### Three paths considered
Path one was splitting D5 into D5 Vitals and D6 Labs with renumbering downstream. Clean for data entry but added another instrument split alongside D3a and D3b. Concern about too many split instruments in the project structure becoming a confusing pattern. Path two was keeping D5 together and using event-name branching to conditionally hide labs at non-labs events. Single instrument cleaner conceptually but event-name branching has known fragility risks. Path three was keeping everything together with no branching and accepting empty fields with documentation. Rejected as relying on training to compensate for form design which creates data quality problems.

### Path chosen and why
Path two. Event-name branching on the lab fields. The deliberate choice was to demonstrate problem-solving depth rather than defaulting to the same split-the-form pattern used for D3. A portfolio showing both splitting (D3a/D3b temporal split) and branching (D5 event-name conditional rendering) demonstrates judgement about when each tool is right. Splitting fits temporal separation where data is collected weeks apart. Branching fits conceptual unity where data shares a clinical encounter but only some pieces apply at any given visit. D5 fits the latter pattern because vitals and labs at the same visit are part of one nursing encounter and should not be artificially separated into two instruments.

### Implementation details
Captured exact unique event names from Define Events page before writing any branching to avoid typos. Three labs events screening_arm_1 pk_t48h_arm_1 day_7_followup_arm_1. Applied the expression [event-name] = "screening_arm_1" or [event-name] = "pk_t48h_arm_1" or [event-name] = "day_7_followup_arm_1" to every lab field across the four lab panels haematology liver function renal electrolytes glucose. Left vital signs fields unbranched so they remain visible at every event. Left investigator review section unbranched so the clinical signature applies to every visit whether vitals only or vitals plus labs. For lab fields that had pre-existing branching for clinical reasons composed the new event-name expression with the existing condition using AND so both must be true for the field to show preserving the original clinical logic.

### Field label discipline
Renamed the abnormalities field from "Any clinically significant lab abnormality" to a label that applies universally across both vitals-only and labs events. Since the form now serves both visit contexts every field label must read cleanly in both. The original lab-specific phrasing would have confused data entry at vitals-only events.

### Field removed
Deleted d5_visit_timepoint entirely once event-name branching took over its job. The field was duplicating what REDCap's redcap_event_name already tracks natively which is a single-source-of-truth violation. With event-name branching doing the visibility work the custom timepoint field served no remaining purpose.

### Testing confirmed
Walked the form through every event in the grid. At screening pk_t48h and day_7_followup all lab fields visible alongside vitals and investigator review. At day_0_dosing all PK observation timepoints and src_review only vitals and investigator review visible lab fields correctly hidden.

### Maintenance contract documented
D5 lab field branching depends on three unique event names exactly as spelled. If any of screening_arm_1 pk_t48h_arm_1 or day_7_followup_arm_1 are renamed in Define Events the branching breaks silently because the expression will never match a non-existent event name. Future maintenance of these events must include updating the D5 branching expressions in lockstep.

### Architectural lesson worth keeping
REDCap offers two ways to control field visibility across events. Instrument-to-event mapping turns whole forms on or off at the event level which is the right tool when the entire form does not apply at certain events. Field-level branching on event-name turns individual fields on or off within a form that does fire at all relevant events which is the right tool when only some fields are visit-specific within a form that otherwise applies broadly. D5 needs the second pattern because most of the form applies to every event but the lab subset does not.

### Pipeline status
Five simulation instruments built. D5 form architecture now clean and tested. simulate_d5.py not yet built. The form is ready for simulation against.

### Next milestone
Build simulate_d5.py. The repeating instrument pattern from D4 carries forward. Each volunteer gets multiple D5 records one per mapped event. Vitals fields populated at every record. Lab fields populated only at the three labs events screening pk_t48h day_7_followup matching the form's branching logic. The simulation must honour the conditional rendering by leaving lab fields empty at non-labs events not by inventing data the form would not collect.

---
## 2026-06-02 — D5 simulation design locked 

### What was decided
Locked the complete clinical narrative and structural design for simulate_d5.py before any code.narrative-driven simulation . The data tells a coherent Phase 1 dose escalation safety story rather than just generating plausible random values. This is the most ambitious simulation in the projec .

### The clinical narrative locked in
Eighteen randomised volunteers across three cohorts of six each. D5 fires at three events with labs populated and at the other vitals-event mappings with labs hidden via event-name branching.

At screening every volunteer has labs and vitals drawn for baseline. Two or three volunteers carry incidental abnormalities that did not fail eligibility. One has mildly elevated ALT around 1.2 times upper limit of normal consistent with occasional alcohol use. One young woman has marginal anaemia at the low end of normal range. Possibly one volunteer shows mild dehydration markers including slightly elevated creatinine and upper-normal sodium. These are stable individual baselines that persist across timepoints.

At T+48h drug-related effects appear that scale with cohort dose. The 2mg cohort shows minimal change with slight uptick in glucose slight neutrophil rise and slight potassium drop all within normal range. The 4mg cohort shows clearer effects with glucose nearer upper-normal neutrophil count roughly 50 percent above baseline corresponding lymphopenia and potassium at the lower end of normal. The 8mg cohort shows the most prominent effects with glucose elevations pushing one or two volunteers above upper-normal neutrophilia roughly doubling baseline potassium dropping to low-normal or just below. These are textbook corticosteroid effects. Volunteers with incidental screening findings continue to show those findings.

At Day 7 drug effects have largely resolved. Most values return to near-baseline. Incidental findings remain stable.

The engineered Story finding sits at Day 7 in the 8mg cohort. One specific volunteer selected deterministically using the random seed shows a Day 7 ALT elevation between 80 and 100 U per L falling clearly in CTCAE Grade 1 range above upper limit of normal up to three times ULN. The same volunteer also showed above-cohort-average glucose at T+48h above-cohort-average neutrophilia at T+48h and low-end-of-cohort potassium at T+48h. The narrative tells the story of a high responder volunteer whose Day 7 ALT elevation is biologically coherent with their stronger response to the drug rather than appearing as an isolated unexplained finding.

This is exactly the kind of signal that triggers SRC discussion in a real Phase 1 trial. The investigator review field for this volunteer at Day 7 is flagged Yes for clinically significant abnormality with appropriate narrative documentation.

### Why this narrative serves the portfolio
The high responder narrative produces a coherent dashboard story. A reviewer can see a pattern across multiple labs across multiple timepoints for the same volunteer and the pattern means something biologically. The alternative surprising-signal narrative would have looked like noise that happened to be designed in rather than a defensible clinical pattern. The chosen approach demonstrates understanding of how dose-related effects manifest progressively in individual responders and how Phase 1 safety monitoring is designed to catch exactly this kind of signal.

### Clinical pharmacology rationale documented
Dexamethasone is a synthetic corticosteroid. Even a single IV dose produces detectable physiological changes within 24 to 48 hours most of which are transient and resolve by Day 7. The effects depicted are all real and well-documented. Transient glucose rise from insulin antagonism and gluconeogenesis. Transient neutrophilia from demargination effects releasing marginated neutrophils into circulation paired with transient lymphopenia from lymphocyte redistribution. Transient hypokalaemia from mineralocorticoid activity. Subtle late ALT effects when corticosteroid hepatotoxicity occurs from a single dose tending to present as a delayed transaminase elevation rather than an immediate one. Day 7 timing for the engineered ALT finding is biologically plausible.

The hypokalaemia depicted will be modest. A drop from baseline near 4.3 mmol per L to 3.6 mmol per L at the top dose is realistic. Lower than 3.5 mmol per L would not be a typical single-dose finding so the simulation will not produce that.

### Structural design locked
D5 is a repeating instrument firing at multiple events with field-fill patterns differing by event. The simulation iterates over D5-mapped events for each volunteer. At labs events the lab fields populate. At vitals-only events the lab fields remain empty strings honouring the REDCap branching logic. The investigator review section always populates because that section is unbranched in REDCap.

All 18 randomised volunteers get D5 records at every event D5 is mapped to. Reserves do not get D5 records because they were never dosed.

### Eight-section build plan
Section 1 configurations and schema template including reference ranges for each lab test and constants identifying narrative roles. Section 2 event configuration list of dictionaries with one boolean flag per event indicating whether labs fire. Section 3 load D3a filter to Randomised same pattern as D4. Section 4 load D1 for demographics and baseline data including sex which affects some reference ranges. Section 5 deterministic selection of the high-responder volunteer and the volunteers carrying incidental findings using the random seed for reproducibility. Section 6 the make_d5_record function with cohort-driven dose response logic individual baseline carryovers and engineered high-responder pattern. Section 7 nested loop generating all records skipping events D5 is not mapped to. Section 8 verification prints and CSV export.

### Estimated effort
Sections 1 to 4 around 45 minutes. Section 5 short. Section 6 the dense one probably 90 minutes or more because the narrative logic across cohort by event by volunteer narrative role takes careful thought. Sections 7 and 8 around 30 minutes. Total realistic working time across one or two sessions 3 to 4 hours of focused work.

### Next milestone
Build simulate_d5.py starting with Section 1.

---
## 2026-06-04 — simulate_d5.py Sections 1 through 5 complete — narrative cast locked in

### What was built
Completed the configuration setup, event mapping, data loading, and narrative role assignment for simulate_d5.py. Five of the eight planned sections are in place. The simulation has not yet generated any records but the infrastructure that drives the Section 6 record generation is fully established.

### Section 1 configuration locked
Reference ranges for every lab test defined as module-level constants. Sex-specific ranges for haemoglobin and creatinine keyed by REDCap sex code "1" male "2" female rather than translating to letters at load time. Single vocabulary across the project. Drug effect magnitudes by cohort encoded as multiplicative factors. Glucose rise scales 1.05 1.15 1.30 across the three cohorts. Neutrophil rise scales 1.10 1.50 1.80. Lymphocyte drop scales 0.95 0.80 0.65. Potassium drop scales 0.98 0.93 0.88. Day 7 residual glucose effects modest at 1.00 1.02 1.05. High responder boosts defined separately for the engineered Story C narrative. Random seed locked at 42 for reproducibility. d5_template dictionary captures all 31 fields plus three REDCap structural columns (record_id, redcap_repeat_instance, redcap_event_name).

### Section 2 event configuration
D5 fires at 10 of 11 events in the event grid. SRC Review excluded entirely because D5 is not mapped there. Each event entry holds the exact unique event name from REDCap, a human label for debug prints, a day offset relative to dosing day, and a boolean labs flag. Three events have labs True (screening_arm_1, pk_t48h_arm_1, day_7_followup_arm_1). Seven events have labs False. The boolean flag is what drives the conditional logic in Section 6.

### Section 3 data loading
Standard pattern. Load d3a_dose_assignment.csv and filter to Randomised volunteers. 18 volunteers loaded.

### Section 4 demographic data
D1 provides both weight and sex. Initial attempt looked for sex in D2 which raised a KeyError because sex actually lives in D1 as sex_at_birth. Caught the mistake, corrected by collapsing the lookup into D1 only. One CSV read instead of two. The d1_weights and d1_sex dictionaries both populated from a single pass through D1. 100 records loaded.

### Lesson worth recording from the D2/D1 sex confusion
In a project with multiple data sources it is easy to forget which field lives in which CSV. The bigger the project gets, the more this risk grows. Two disciplines help. First, when in doubt about a field's location check the actual CSV rather than reasoning from assumed structure. Memory is unreliable across many files. Second, this is exactly the kind of mapping ambiguity the SDTM mapping specification document captures explicitly. Every variable in the SDTM submission has a table entry saying which source field it comes from. The confusion that just happened is a small-scale example of why that mapping document is valuable in real clinical data work.

### Section 5 narrative roles assigned
Story C cast locked in deterministically because of the random seed. Same volunteers play the same roles every run.
- ZA-CPT-P1-080 high responder. Sentinel in the 8mg cohort. Carries the strongest dose response at T+48h across glucose, neutrophils, and potassium. Develops Grade 1 ALT elevation at Day 7.
- ZA-CPT-P1-078 female volunteer with marginal anaemia. Persists across all three timepoints.
- ZA-CPT-P1-059 mildly elevated baseline ALT around 1.2 times upper limit of normal. Persists across timepoints.
- ZA-CPT-P1-084 dehydration markers at screening with slightly elevated creatinine and upper-normal sodium. Resolves modestly by Day 7.
The other 14 randomised volunteers carry no narrative role and receive textbook-normal labs at baseline with dose-scaled effects at T+48h that resolve by Day 7.

### New Python patterns this session
List comprehensions used heavily for filtering volunteer pools by cohort sentinel status and sex. Sets used for tracking already-taken record_ids to ensure no volunteer plays two narrative roles. The discipline of incremental filtering with running exclusion sets is the cleanest pattern for narrative cast selection from a candidate pool.

### Next milestone
Build Section 6 of simulate_d5.py. The make_d5_record function with cohort-driven dose response logic, individual baseline carryovers for the three incidental finding volunteers, and the engineered high-responder pattern including the Day 7 ALT signal. This is the most ambitious section in the entire simulation pipeline. Plan to build it incrementally in four or five sub-blocks. Vitals generation, baseline lab generation, drug effect application at T+48h, Day 7 lab generation with residual effects and the engineered signal, and the investigator review section. Each sub-block testable before moving to the next.

---
## 2026-06-04 — simulate_d5.py complete — 180 records with engineered safety narrative

### What was built
Completed simulate_d5.py across all eight sections. Reads d3a_dose_assignment.csv to find the 18 Randomised volunteers and d1_eligibility.csv for weight and sex_at_birth. Generates one D5 record per volunteer per D5-mapped event giving 180 records across 10 events. Three of those events populate the full labs panel and seven populate vitals only honouring the REDCap branching logic. Engineered clinical narrative implements one high responder volunteer in the 8mg cohort plus three incidental findings volunteers carrying baseline abnormalities.

### Engineered narrative cast locked deterministically
Random seed 42 produces the same cast every run.
- ZA-CPT-P1-080 high responder. Sentinel in 8mg cohort. Boosted T+48h response across glucose neutrophilia and potassium. Day 7 ALT engineered to 80-100 U/L range falling cleanly in CTCAE Grade 1 territory.
- ZA-CPT-P1-078 female volunteer carrying marginal anaemia. Persists across all timepoints.
- ZA-CPT-P1-059 mildly elevated baseline ALT. Persists across timepoints.
- ZA-CPT-P1-084 dehydration markers at screening with mild creatinine and upper-normal sodium. Resolves modestly by later events.

### Verification output confirms narrative landed correctly
All 18 volunteers got exactly 10 D5 records each. Lab fields are empty at all 7 vitals-only events and populated at all 3 labs events. High responder Day 7 ALT generated at 86 U/L with abnormal flag set to 1. T+48h dose-scaled effects visible in the cohort means. Glucose rises 5.07 to 5.63 to 6.10 mmol per L across cohorts 1 2 3. Neutrophils rise 5.68 to 7.42 to 8.87 across cohorts 1 2 3 with cohorts 4mg and 8mg crossing the upper limit of normal. Potassium falls 4.22 to 3.85 to 3.73 across cohorts 1 2 3 with the 8mg cohort approaching the lower limit of normal. Clean dose-response signal emerging from the data.

### Notable Python concepts demonstrated in this build
List comprehensions used heavily in Section 5 for filtering candidate pools by cohort and sex. Sets used to track already-taken record_ids ensuring no volunteer plays two narrative roles. Helper function generate_lab_value defined once and called repeatedly across all four lab panels reducing code duplication. Dictionary copying with dict(d5_template) to avoid mutating the template across function calls. Tuple unpacking with the star operator for passing the engineered ALT range as separate min and max arguments. Multiplier and shift fraction parameters separated cleanly so drug effects multiply baseline values and incidental findings shift within range without mathematically interacting.

### Bugs caught and fixed during the build
First bug. The sex variable was assumed to live in D2 when it actually lives in D1 as sex_at_birth. The KeyError surfaced this at runtime. Fix collapsed the D1 and D2 loops into a single D1 loop pulling both weight and sex from one CSV read. The lesson is that when a project has multiple data sources it is easy to forget which field lives in which CSV. Checking the actual data dictionary rather than relying on memory is the discipline that prevents this.

Second bug. The sex_at_birth field has three options not two. REDCap codes them 1 male 2 female 3 intersex or indeterminate. Initial HB_RANGE and CREATININE_RANGE dictionaries only defined keys for 1 and 2 causing a KeyError when a code-3 volunteer appeared in the randomised pool. Fix extended both reference range dictionaries to include a key for 3 using a union range covering both male and female bounds. This is the clinically defensible approach when sex-based hormonal profile is indeterminate.

Third bug. An unconditional return record at the wrong indentation level inside make_d5_record caused the function to exit early and VS Code to grey out the unreachable downstream code. The diagnostic skill that resolved it was reading the static analyser greying as a real warning rather than ignoring it. The lesson is that VS Code is telling you something structurally wrong before the code even runs.

### Language audit during finalisation
Removed internal-planning vocabulary that had leaked into code comments and print statements. Specifically replaced Story C labels with descriptive language because Story A and Story B were paths not taken and the letter naming exposed planning shorthand to a public reader. Discipline going forward. Planning labels live in PROGRESS.md as the journal of how we thought through it. Code and documentation describe what the project is not the planning vocabulary that got us there.

### Pipeline status
Six simulation instruments built out of seven total. One remaining.
- simulate_d1.py 100 screened records
- simulate_d2.py 28 eligible records
- simulate_d3a.py 28 dose assignment records
- simulate_d3b.py 18 safety review records
- simulate_d4.py 144 PK sampling records
- simulate_d5.py 180 safety labs and vitals records

### Next milestone
Build simulate_d6.py for the adverse events instrument. D6 captures AEs and SAEs across the trial. The architecture pattern carries forward from D5. Repeating instrument firing at events with conditional logic. The engineered narrative for D6 will include realistic AE rates by cohort consistent with the dexamethasone safety profile. The high responder identified in D5 may also surface in D6 with a related AE to maintain narrative consistency across instruments.

---
## 2026-06-08 — simulate_d6.py design locked — adverse events with engineered SAE

### What was decided
Locked the complete design for simulate_d6.py before any code. D6 is the adverse events instrument capturing AEs and SAEs across the trial. The simulation produces a mix of realistic baseline AEs scaling by cohort, the engineered Grade 1 ALT elevation AE matching the D5 finding for the high responder, and one engineered unrelated SAE demonstrating the safety reporting workflow.

### Event mapping confirmed against REDCap
D6 fires at 5 events in the current event grid: day_0__dosing_arm_1, pk_t8h_arm_1, pk_t24h_arm_1, pk_t48h_arm_1, day_7_followup_arm_1. Confirmed by downloading the instrument designations export from REDCap. D6 correctly does not fire at screening because volunteers are not yet dosed. Does not fire at the early PK timepoints (T+30min through T+4h) because those are brief PK draw visits without substantive clinical assessment.

### Record structure pattern
At each volunteer-event combination either one placeholder record with ae_any equal to 0 (no AEs to report since last assessment), or one or more AE records with ae_any equal to 1 (one record per AE reported at this assessment). Expected total records approximately 95 to 100 across the trial.

### AE pool 14 terms locked
Headache, nausea, fatigue, insomnia, feeling jittery or restless, dry mouth, increased appetite, mood change, cannulation site discomfort, mild dizziness, constipation, dyspepsia, vivid dreams, hot flushes. These are realistic dexamethasone single-dose Phase 1 AEs ordered roughly by frequency. The simulation picks from this pool probabilistically with weights favouring the more common terms.

### AE rates scale by cohort
Overall trial AE rate target 60 to 70 percent of volunteers report at least one AE. Scaled by cohort. 2mg cohort approximately 50 percent (3 of 6 volunteers). 4mg cohort approximately 65 percent (4 of 6 volunteers). 8mg cohort approximately 80 percent (5 of 6 volunteers). Volunteers who report AEs typically report 1 to 3 events distributed across the 5 assessment events. The high responder is guaranteed to report at least the ALT elevation AE plus likely some minor events. The SAE volunteer is guaranteed to report the gastroenteritis SAE plus possibly some minor events.

### Engineered narrative threads
Thread 1 the high responder. ZA-CPT-P1-080 carries through from D5. Reports a Grade 1 ALT elevation AE at Day 7 follow-up matching the D5 lab finding. AE term transaminase elevation. Onset Day 7. Causality probably related. Action none because single dose already complete. Outcome ongoing at end of follow-up. This is the D5 to D6 cross-instrument consistency that real clinical data managers maintain.

Thread 2 the unrelated SAE. One volunteer picked deterministically using the random seed from the 14 non-cast volunteers reports severe gastroenteritis between Day 3 and Day 5. CTCAE Grade 3. Causality unrelated to study drug. Onset between Day 3 and Day 5 specifically between scheduled assessments. Action not applicable single dose complete. Outcome recovered within 48 hours. Meets SAE criterion hospitalisation due to overnight admission for IV rehydration. Sponsor and ethics reporting dates documented within ICH timelines.

### Why the unrelated SAE strengthens the portfolio
Three layers of narrative now visible in the data. Layer 1 the dose-response layer where most volunteers report minor AEs scaling with cohort. Layer 2 the drug-related significant finding layer where the high responder shows the Grade 1 ALT elevation. Layer 3 the unrelated SAE layer where the gastroenteritis hospitalisation is properly captured assessed and excluded as drug-related. A reviewer sees a complete safety reporting workflow demonstrated end to end including the judgement-heavy work of distinguishing drug-related events from unrelated ones. APVAsC training directly applies to layer 3.

### Eight section build plan
Section 1 configurations including the AE term pool with weights cohort AE rate constants engineered narrative constants and d6_template dictionary. Section 2 event configuration listing the 5 D6-mapped events from REDCap. Section 3 load D3a and filter to Randomised. Section 4 load any other upstream demographic data possibly small or skipped because AE generation does not depend on weight or sex. Section 5 assign narrative roles. High responder carries over from D5. SAE volunteer picked from the 14 non-cast volunteers using the random seed. Section 6 the make_d6_record function generating one AE record at a time. Structurally simpler than D5 because no calculated lab values just term selection severity dates and narrative fields. Section 7 the nested loop with variable per-volunteer-event record count. Section 8 verification prints and CSV export.


### Architectural lesson worth keeping
D6 demonstrates cross-instrument narrative consistency. The high responder's Day 7 ALT finding appears once in D5 as a lab abnormality and once in D6 as an adverse event with matching dates matching severity matching causality assessment. This is what good clinical data management looks like in real trials. Most simulations do not capture this discipline and it is one of the things that will mark this portfolio as serious work.

### Next milestone
Build simulate_d6.py starting with Section 1.

---
## 2026-06-09 — simulate_d6.py complete — 90 AE records with two engineered narrative threads

### What was built
Completed simulate_d6.py across all seven sections. Reads d3a_dose_assignment.csv for the 18 Randomised volunteers and d5_cast_assignments.csv to inherit the D5 narrative cast. Generates one D6 record per volunteer per D6-mapped event giving 90 records across 5 events. Each record is either a placeholder with ae_any=0 (no AEs reported at that assessment) or an AE record with ae_any=1 (one record per AE). Two engineered narratives present in the data: the high responder's Grade 1 ALT elevation AE at Day 7 inherited from D5, and an unrelated SAE for gastroenteritis with overnight hospitalisation in a separately picked volunteer.

### Final cast across D5 and D6
- ZA-CPT-P1-080 high responder. Carries forward from D5. Day 7 transaminase elevation AE Grade 1, probably related to study drug, outcome recovering (ongoing at end of follow-up).
- ZA-CPT-P1-010 SAE volunteer. Picked randomly from the 14 non-cast volunteers. Acute gastroenteritis CTCAE Grade 3 onset Day 5, recovered without sequelae within 48 hours, hospitalisation criterion met, assessed as unrelated to study drug.
- ZA-CPT-P1-078 anaemic, ZA-CPT-P1-059 ALT-elevated baseline, ZA-CPT-P1-084 dehydrated. These D5 cast members do not have D6 roles because their D5 findings are sub-clinical and would not generate AE entries in real trials.

### Architectural pattern established this session
D5 writes a cast assignments file to disk. D6 reads it to know which volunteers already have narrative roles. Same pattern will carry forward to D7 and any future downstream scripts. This is the disk-based equivalent of cross-script state passing. It maintains single-source-of-truth across the pipeline because each script's cast decisions are explicitly written and explicitly read rather than reverse-engineered from output data or hardcoded.

### New Python patterns learned this session
Two-pass record generation. First pass builds an AE schedule per volunteer using helper functions. Second pass iterates the schedule and generates records calling the function. Cleaner than trying to make all decisions inline. Helper functions returning dictionaries to pass as specifications to other functions. Random sample for picking events without replacement so the same event does not get chosen twice for routine AEs from the same volunteer. ICH SAE reporting timeline computation using timedelta arithmetic from onset date.

### Bugs caught and fixed during this build
First bug. The d6_template had old field names from a first draft of Section 1 (ae_severity, ae_causality, ae_action_taken, ae_narrative, sae_signoff) while the make_d6_record function used the verified REDCap field names (ae_ctcae_grade, ae_relatedness, ae_action, ae_treatment, plus the new ae_ongoing, ae_onset_time, ae_resolution_date fields). The mismatch did not surface until Section 7 tried to write the CSV and got a ValueError about extra keys. Fix replaced the template with the verified version. The lesson is that the data dictionary verification step has to fully propagate through all references in the file. A partial verification leaves silent inconsistencies that surface much later.

Second bug. The main loop was missing from the file entirely. The helper functions were pasted but the loop that calls them was not. The script ran cleanly through to the end of Section 4 then exited without producing any D6 records and without raising any error because there was nothing missing from a syntax perspective. The fix was adding the main loop. The lesson is that completion at the script level is not the same as completion at the section level. Need to scroll to the end and verify the loop exists before assuming the build is done.

Third issue, not a bug but worth noting. The cohort AE distribution did not land where we designed. Expected pattern of 50/65/80 percent of volunteers reporting AEs produced 5/6, 3/6, 6/6 in this specific run. The 4mg cohort underreported. This is a small-sample-size artefact and a realistic simulation outcome. Real Phase 1 trials at this size produce noisy data that does not always fit the expected dose-response pattern cleanly. Decision is to leave it as-is rather than engineer the seed for prettier numbers. Honest noise beats artificial smoothness.

### Verification confirms narrative landed
Total 90 records across 18 volunteers and 5 events. Both engineered findings present and correctly populated. High responder ALT elevation has onset Day 7, Grade 1, outcome Recovering. SAE has onset Day 5, Grade 3, sponsor reported Day 6 within ICH 24-hour timeline. Cohort AE pattern shows the expected directional trend at the volunteer level even with the middle cohort variance.

### Pipeline status
Six instruments now fully built and tested.
- simulate_d1.py 100 screened records
- simulate_d2.py 28 eligible records
- simulate_d3a.py 28 dose assignment records
- simulate_d4.py 144 PK sampling records
- simulate_d5.py 180 safety labs and vitals records
- simulate_d6.py 90 adverse events and SAE records

Two instruments still need work.
- simulate_d3b.py exists in the repo from an earlier session but its current state needs review. The original D3b was likely built before D4 D5 and D6 contained engineered narratives so its SRC review rationale fields probably do not reference the actual findings the SRC would be reviewing. Status to be verified in next session.
- simulate_d7.py not yet built. Volunteer symptom diary across the first 7 days post-dose. Volunteer-completed survey different in shape from the other instruments.

### Next milestone
Review the existing simulate_d3b.py to determine whether the storyline still matches given the engineered narratives in D4 D5 D6. Decide whether to update or rebuild. Then build simulate_d7.py. After both are complete the simulation phase is genuinely finished and we move to SQL pipeline.

---
## 2026-06-10 — simulate_d7.py design locked — volunteer symptom diary with cross-instrument narrative

### Why D7 comes before D3b
Reordered the build sequence on a sharp clinical observation. D3b is the SRC safety review at Day 21 which reviews all the data that came before it including D4 PK, D5 labs, D6 AEs, and D7 diary. If D7 contains any engineered narrative threads they need to exist before D3b can be written with full narrative consistency. Building D3b first would mean having to come back and edit it once D7 produced findings the SRC would have reviewed. Same temporal causality discipline that drove the original split of D3 into D3a and D3b. Information flows in the direction of time. D3b sits at the end because every other instrument's data is upstream of it.

### The structural realisation about D7
D7 is a volunteer-completed survey not an investigator-captured form. Different voice. Different threshold for capture. Investigators in D6 capture AEs that meet a clinical threshold. Volunteers in D7 record everything they noticed about themselves with no clinical filter. In normal logic that would mean D7 reports more symptoms than D6. But the clinical reality of single-dose IV dexamethasone in healthy young adults cuts through that assumption. The well-known dexamethasone side effects come from chronic exposure or high-dose courses. A single 2 to 8 milligram IV dose produces detectable physiological changes (visible in labs and demargination effects) but does not typically produce strong volunteer-felt symptoms. So D7 should be quiet. Most volunteers most days report None for every symptom. This is realistic AND it tells a meaningful dashboard story. The drug was well-tolerated by volunteer self-report with the dose-dependent biological effects visible in labs but not strongly visible in self-reported symptoms.

### Locked design
D7 fires at 4 events: Day 0 dosing, T+24h, T+48h, Day 7 follow-up. One record per volunteer per event giving 18 times 4 equals 72 records total. No placeholder versus full record distinction. Every record is a complete diary entry. The diary_day field captures which day this entry corresponds to: 1 for Day 0 dosing, 2 for T+24h, 3 for T+48h, 7 for Day 7 follow-up. The 7 symptom severity fields rate the volunteer's experience over the period since their last entry on a 0-3 scale (None, Mild, Moderate, Severe). Symptom rates scale by cohort dose. The 8mg cohort reports slightly higher symptom densities than the 2mg cohort. Symptoms differentiated by common (insomnia, fatigue, appetite) vs uncommon (headache, nausea, mood, gi) because dexamethasone affects sleep and appetite more reliably than mood or gi.

### Engineered narrative threads in D7
Thread 1 the high responder ZA-CPT-P1-080. Reports mild insomnia on Day 1 (Day 0 event entry) consistent with corticosteroid sleep effects. Reports some fatigue across the trial. Their ALT elevation in D5/D6 is biochemically real but subjectively imperceptible so we do not engineer dramatic D7 symptoms for them. Just a slight nudge above their cohort average.

Thread 2 the SAE volunteer ZA-CPT-P1-010. This is the clearest D7 signal. Their Day 1 and Day 2 entries are unremarkable. Their Day 3 entry (T+48h event) shows moderate or severe GI symptoms, severe nausea, moderate fatigue, reflecting the onset of gastroenteritis before formal admission. Their Day 7 entry shows recovery. This means the same SAE volunteer whose SAE was recorded for in D6 has diary entries that biologically precede and follow the formal SAE event. Cross-instrument narrative consistency.

### Why this serves the portfolio
The dashboard story now traces dose-response across three different data sources. Labs in D5 show dose-scaled physiological changes. AEs in D6 show dose-scaled symptom rates with one engineered drug-related signal. Diary in D7 shows dose-scaled subjective symptoms (quietly). The same engineered narratives (high responder, SAE volunteer) thread through all three instruments with biological and temporal consistency. A reviewer sees one coherent clinical story across multiple data sources rather than four disconnected datasets that happen to share record_ids. That is what good clinical data management produces in real trials.

### Architectural patterns continuing from D6
D5 writes a cast assignments file. D6 reads it. D6 writes its own cast file. D7 reads both. Each script's narrative decisions are explicitly written to disk and explicitly read by downstream scripts rather than reverse-engineered from output data or hardcoded. Single source of truth across script boundaries. This is the disk-based equivalent of cross-script state passing.

### Seven-section build plan
Section 1 configurations including symptom rate dictionaries by cohort and by symptom category, narrative constants, d7_template dictionary verified against the data dictionary. Section 2 event configuration with the 4 D7-mapped events and their diary_day mapping. Section 3 load D3a filter to Randomised. Section 4 load D5 and D6 cast assignments. Section 5 make_d7_record function with cohort-scaled symptom generation plus narrative overrides for the engineered volunteers. Section 6 nested loop 18 by 4 producing 72 records. Section 7 verification and CSV export.

### Pipeline status
Six instruments built. D7 design locked, ready to build. D3b in repo but its current state needs review after D7 is complete.

### Next milestone
Build simulate_d7.py starting with Section 1.

---
## 2026-06-10 — simulate_d7.py complete — 72 diary records with cross-instrument narrative consistency

### What was built
Completed simulate_d7.py across all seven sections. Reads d3a_dose_assignment.csv for the 18 Randomised volunteers and inherits the engineered narrative cast from d5_cast_assignments.csv (high responder) and d6_cast_assignments.csv (SAE volunteer). Generates one D7 record per volunteer per D7-mapped event giving 72 records total across 4 events. Symptom severity uniformly rated 0-3 (None, Mild, Moderate, Severe) across 7 symptom categories per record.

### Verification confirms all four narrative beats landed correctly
High responder Day 1 entry shows Moderate insomnia (rating 2) consistent with first-night corticosteroid sleep effect. High responder Day 1 fatigue boosted to 2 as designed. SAE volunteer Day 3 entry shows Severe GI symptoms (rating 3), Severe nausea (rating 3), and Moderate fatigue (rating 2) reflecting the acute gastroenteritis onset before formal hospitalisation. SAE volunteer Day 7 entry shows all seven symptoms reset to None reflecting post-hospitalisation recovery. Cross-instrument consistency intact across D5 D6 and D7 for both engineered narratives.

### Cohort dose-response trend visible in diary data
Mean total severity per record across all 7 symptoms shows clean gradient: 1.79 for 2mg cohort, 2.29 for 4mg cohort, 2.67 for 8mg cohort. The dose-response thread now visible across three different data sources. Labs in D5 show dose-scaled physiological changes. AEs in D6 show dose-scaled symptom rates. Diary in D7 shows dose-scaled subjective symptoms. One coherent clinical story across multiple instruments.

### Architectural pattern fully demonstrated this session
The disk-based cast assignment pattern reached its full expression. D5 wrote a cast file. D6 read D5 and wrote its own. D7 read both D5 and D6 cast files to inherit the full upstream narrative cast. Each script's narrative decisions are explicitly written to disk and explicitly read by downstream scripts rather than hardcoded or reverse-engineered from output data. Single source of truth across script boundaries. This same pattern will let D3b read all four cast files (D5, D6, D7) when we build it.

### New Python patterns this session
Helper function generate_symptom_rating taking cohort code and a boolean is_common flag, looking up the appropriate probability distribution, and using random.choices with weights for a weighted draw from 0-3. Used 7 times per record. The min function for capping the high responder fatigue boost so the boosted value never exceeds the maximum dropdown value of 3. Pattern of generating baseline values first then applying narrative overrides afterward keeping the function readable.

### Honest design choice worth noting
The SAE volunteer's Day 5 hospitalisation does not have a corresponding D7 entry because D7 only fires at Day 0, T+24h, T+48h, and Day 7 not at Day 5. The Day 3 entry captures pre-hospitalisation escalating symptoms. The Day 7 entry captures post-recovery normal symptoms. The gap between them is exactly when the SAE event occurred. This realistically reflects that volunteers do not fill in diary entries while in hospital being treated for an SAE.

### Pipeline status
Seven of seven planned simulation instruments now substantially built.
- simulate_d1.py 100 screened records
- simulate_d2.py 28 eligible records
- simulate_d3a.py 28 dose assignment records
- simulate_d4.py 144 PK sampling records
- simulate_d5.py 180 safety labs and vitals records
- simulate_d6.py 90 adverse events and SAE records
- simulate_d7.py 72 volunteer symptom diary records

One simulation instrument still needs review.
- simulate_d3b.py exists in the repo from an earlier session before the engineered narratives were designed. Its current SRC review rationale fields probably do not reference the actual findings the SRC would be reviewing in D4, D5, D6, and D7. Status to be reviewed in next session. The architectural decision is whether to update D3b to incorporate the engineered findings or rebuild it.

### Next milestone
Review simulate_d3b.py to determine whether the existing storyline still matches given the engineered narratives now present in D4 D5 D6 and D7. The high responder's Day 7 ALT elevation, the unrelated SAE, and the cohort-scaled effects all need to be reflected in the SRC review rationale and decision fields. After D3b is updated or rebuilt the simulation phase is genuinely complete and we move to SQL pipeline then Power BI then SDTM capstone.

---
## 2026-06-10 — simulate_d3b.py rebuilt — simulation phase complete

### What was rebuilt
Updated simulate_d3b.py to incorporate the engineered narratives now present in D5, D6, and D7. The previous version was written before the engineered cast existed and produced 18 identical generic SRC rationales. The new version produces cohort-specific rationales that reference the actual findings the SRC would have reviewed. The 2mg and 4mg cohort rationales describe clean uneventful escalations. The 8mg cohort rationale explicitly adjudicates both engineered findings by record_id: the high responder's Grade 1 ALT elevation at Day 7 (probably related, below DLT threshold) and the unrelated SAE of acute gastroenteritis (unrelated to study drug, sponsor and ethics notified per ICH timelines). 

### Cross-instrument narrative consistency complete
The narrative thread now flows from D5 labs (high responder Day 7 ALT abnormality) to D6 AEs (the Grade 1 transaminase elevation AE entry plus the gastroenteritis SAE) to D7 diary (high responder's mild insomnia and fatigue, SAE volunteer's escalating GI symptoms Day 3 then recovery Day 7) and finally into D3b SRC review where both findings are explicitly named and formally adjudicated. A reviewer reading the dashboard end to end would see one coherent clinical story told through four different data sources, each one adding evidence to the same picture. This is what good clinical data management produces in real trials.

### Design decisions locked
The 8mg cohort src_decision stays at code 1 (escalate) but the rationale acknowledges the Grade 1 ALT signal warranted SRC attention. Grade 1 is below DLT threshold so the trial continues but with cautionary documentation for any future trials extending the dose range. The SAE volunteer's gastroenteritis gets formal SRC adjudication explicitly mentioned in the cohort rationale even though it is unrelated to drug, because real SRC meetings adjudicate all SAEs.

The DLT logic became deterministic. All volunteers have dlt_observed = 0 because no volunteer in the engineered narrative has a true Grade 3+ DLT. The high responder's ALT is Grade 1 below threshold. The SAE is unrelated to drug so not a DLT by definition. The previous 5 percent random DLT rate was removed because random firings would contradict the narrative.

Protocol deviations remain random at 10 percent across all cohorts as realistic background noise.

### Architectural pattern fully demonstrated
D3b reads d5_cast_assignments.csv and d6_cast_assignments.csv to identify the engineered volunteers. Same disk-based cast pattern that flows through the rest of the pipeline. The high responder ID and SAE volunteer ID are then embedded directly in the 8mg cohort rationale via f-string interpolation so a reviewer sees the SRC explicitly naming the volunteers being adjudicated.

### Pipeline status
Simulation phase complete. Seven instruments built and tested.
- simulate_d1.py 100 screened records
- simulate_d2.py 28 eligible records
- simulate_d3a.py 28 dose assignment records
- simulate_d3b.py 18 SRC safety review records with cohort-specific rationale
- simulate_d4.py 144 PK sampling records
- simulate_d5.py 180 safety labs and vitals records
- simulate_d6.py 90 adverse events and SAE records
- simulate_d7.py 72 volunteer symptom diary records

Total simulated records: 660 across 18 volunteers and the 100-volunteer screening pool.

### Next milestone
SQL pipeline. Build a relational schema that loads all seven CSVs into a queryable database. Will demonstrate the data engineering side of clinical data management.

---
## 2026-06-15 — Phase 1 SQL pipeline: schema architecture locked before build

### What was built this session
No SQL written yet, by design. This session locked the full schema architecture and load plan for the Phase 1 SQL pipeline before touching the database — engine, load tool, the layering, and the entity-aligned core table list, each with rationale. 
### Engine and tooling locked
- Oracle Database 21c Express Edition, version 21.3.0.0.0, confirmed via `sqlplus -v`.
- All work targets the pluggable database XEPDB1, not the CDB root. Application schemas live in the PDB — the CDB root rejects non-`C##` users with ORA-65096, so every connection uses the service `.../XEPDB1`.
- Driven from sqlplus, no GUI dependency. SQL*Loader for bulk CSV load.
- Pre-build sanity check before any DDL: `SELECT name, open_mode FROM v$pdbs;` must show XEPDB1 as READ WRITE.

### Three-tier architecture
Reconciles the two things in tension — "load faithfully, identifiers as-is" versus "a clean normalised database."
- Staging — faithful raw mirror of the eight export CSVs, one table per CSV, codes left exactly as REDCap exported them, identifiers untouched. This is where SQL*Loader lands data and where "load as-is" lives.
- Core — the entity-aligned normalised model, shaped as a star schema. Dimensions describe who and when; fact tables record what happened and point back to the dimensions by foreign key.
- Analytics — a thin layer of views that decode codes to labels via the dictionary codelists and shape output for Power BI and the SDTM capstone.

The loader only ever touches staging. Relational quality is built in core. Decoding happens in analytics. Load mechanism and schema shape are independent — SQL*Loader does not split data, it lands one flat table per file; the normalising happens afterward in SQL.

### Reference layer sourced from the REDCap exports
- `data-dictionary.csv` (151 fields, all eight forms, full Choices column) → `field_metadata` + `codelist` tables in a P1_META schema. This is the authoritative source for every code→label mapping. Decoding is never done from memory or model output.
- `event_mapping.csv` (11 events) → the `visit` dimension, loaded directly so event names keep their exact REDCap spelling (e.g. `day_0__dosing_arm_1` with the double underscore).
- Coded values confirmed from the dictionary this session: `ae_relatedness` = 1 Unrelated / 2 Unlikely / 3 Possibly / 4 Probably / 5 Definitely; `sae_criterion` 3 = Hospitalisation. The earlier guess at the relatedness scale was retired by reading the dictionary rather than assuming.

### Core table list — entity-aligned, with grain and keys
Dimensions:
- `subject` — grain: one screened volunteer. 100 rows. Surrogate PK `subject_id`, natural key `record_id` kept UNIQUE. Absorbs the three 1:1 instruments: identity and demographics from D1 (all 100), race/ethnicity/country/medical history from D2 (28 eligible, NULL for screen failures), randomisation status and cohort from D3a. Yields the 100 → 28 → 18 screening funnel as disposition attributes.
- `visit` — grain: one trial event. 11 rows from `event_mapping.csv`. Surrogate PK `visit_id`, natural key `event_name` UNIQUE, plus label, day offset, sort order.

One-to-one with subject:
- `eligibility_assessment` — grain: one screened volunteer. 100 rows. PK `subject_id` (also FK). Holds the i1–i7 / e1–e9 inclusion-exclusion checklist, determination, and screen-failure reason. Split off the spine to keep `subject` lean; can be merged back if preferred.

Exposure and disposition facts:
- `dosing` — grain: one dosed volunteer. 18 rows. FK to `subject`. Administered dose, dose per kg, IMP batch and expiry, dosing signoff. Seed of SDTM EX.
- `src_review` — grain: one randomised volunteer. 18 rows. FK to `subject`. Sentinel 48h pass, DLT observed, SRC decision and rationale, deviations.

Findings facts:
- `pk_concentration` — grain: one volunteer per timepoint. 144 rows. Composite natural key `record_id` + `timepoint`; FK to `subject` and `visit` (the D4 timepoint code is bridged to the event label via `event_mapping`). Already long; nothing to pivot.
- `vital_sign` — grain (if long): one volunteer per visit per parameter. ~1,000 rows from D5. FK to `subject` and `visit`. [PENDING Fork B]
- `lab_result` — grain (if long): one volunteer per lab event per analyte. ~900 rows from D5 (labs drawn at only three events). FK to `subject` and `visit`. Units and reference ranges sourced from the dictionary. [PENDING Fork B]
- `diary_symptom` — grain (if long): one volunteer per diary visit per symptom. ~500 rows from D7. FK to `subject` and `visit`. [PENDING Fork B]

Event fact:
- `adverse_event` — grain: one reported AE. 23 rows (`ae_any` = 1 only). FK to `subject` and `visit`. Term, onset, CTCAE grade, relatedness, outcome, and SAE fields inline. The 67 `ae_any` = 0 placeholders stay in staging; the per-visit "any AE this visit?" assessment is derivable as a view if ever needed.

### Key design decisions
- Entity-aligned over instrument-aligned. Organise by real-world entity — volunteer, visit, measurement — not by CRF form. Queries are cleaner and it pre-positions the SDTM capstone, since the domain tables already echo DM, EX, PC, LB, VS, AE.
- Subject spine drawn at 100, not 28 or 18. Account for every record in the CSV and keep the screening funnel inside the model. Screen-failure rows carry sparse D2 columns; that sparseness is honest, it reflects that full demographics were never collected on screen failures, not dirty data.
- Identifiers loaded faithfully, per-instrument keys preserved in staging. D4 is keyed on `record_id` + `timepoint` (D4 has no event name); D5/D6/D7 on `record_id` + `event_name` + `redcap_repeat_instance`. The D4-versus-rest asymmetry is reconciled in core and views through `event_mapping`, never by rewriting staging.
- `eligible_volunteers.csv` is D1 filtered to `eligibility_determination` = 1 → a view, not a table.
- D6 loaded whole, all 90 rows. The 67 placeholders are "no AE this visit" assessments and stay in staging; the `adverse_event` core table filters to the 23 real events.
- Cast files (`d5/d6/d7_cast_assignments`) are QA and validation reference only — used to assert the engineered narrative survived the pipeline (high responder ZA-CPT-P1-080, SAE volunteer ZA-CPT-P1-010), not clinical trial data.
- Surrogate integer PKs everywhere, with the REDCap natural keys kept as UNIQUE for lineage, and enforced foreign keys on every fact table. The enforcement is the difference between a database and a folder of tables.

### Data facts verified this session
- Funnel: 100 screened → 28 eligible → 18 randomised (6 / 6 / 6 across the 2 / 4 / 8 mg cohorts) + 10 reserve.
- Demographics are split across instruments: D1 carries dob, age, sex, weight, height, bmi for all 100; D2 adds race, ethnicity, country, and medical history for the 28 eligible only.
- D2 medical history is stored as flat `*_any` + `*_details` pairs, not a repeating group — so no `medical_history` child table is needed; it stays as subject attributes.
- D5 is the one genuinely wide instrument (34 columns): vitals at all 10 events, the full lab panel at only 3.
- D6: 23 `ae_any` = 1, 67 placeholders. SAE = ZA-CPT-P1-010, acute gastroenteritis, Grade 3, Unrelated, hospitalisation criterion. High responder ZA-CPT-P1-080 = hot flushes (G1) plus transaminase elevation (G1, Probably related) — matches the engineered cross-instrument narrative.
- D4: eight timepoints, single analyte. Pre-dose and 48h read BLQ at the assay floor, clean rise-and-fall between.

### Open decision carried into next session
Fork B — wide versus long for D5 (labs and vitals) and D7 (diary). Long means tall Findings-class tables (`vital_sign`, `lab_result`, `diary_symptom`), one row per measurement: best for Power BI slicers and it pre-builds SDTM LB/VS/FA, at the cost of heavier transform. Wide means one row per subject-event with analytes as columns: less transform, but it fights Power BI and is not SDTM-shaped. Current lean is long. Not locked — to be decided before those three tables are built. `pk_concentration` and `adverse_event` are unaffected, being already long and event-shaped.

### What I learned this session
- Load mechanism and schema shape are independent axes. SQL*Loader lands one flat staging table per CSV; the normalising into keyed tables happens afterward in SQL, not in the loader.
- Spine — the central table everything else hangs off, here `subject`. Primary key identifies a row; a natural key comes from the data (`record_id`), a surrogate key is an invented counter with no outside meaning.
- A foreign key is a "see-also" pointer — it holds another table's key to link rows. A one-to-many relationship is the shape that forces a separate child table; the moment "many" appears, it earns its own table.
- Dimension table = a roster of things that exist (`subject`, `visit`). Fact table = a record of things that happened, pointing back at the dimensions. Facts arranged around dimensions is a star schema, which is exactly the shape Power BI consumes.
- Grain — what one row means. Defining it is the first move on any fact table, and it hands you the key. When the grain needs two columns to be unique (volunteer + timepoint), the primary key is a composite key.

### Next milestone
Build tier one. Open XEPDB1, create the P1_STAGING schema, write one SQL*Loader control file per CSV, and load the eight instrument CSVs plus the dictionary and event map as-is. Verify row counts against the source (100 / 28 / 28 / 18 / 144 / 180 / 90 / 72). Then settle Fork B and build the core dimensions (`subject`, `visit`) followed by the fact tables.

---
---
## 2026-06-16 — SDTMIG Chapter 2 complete — observation model and domain architecture understood

### What was learned
Completed Chapter 2 of the SDTM Implementation Guide. This chapter fundamentally changed how I think about clinical data. Before this point SDTM looked like a large collection of domains and variables to memorise. After working through the chapter it became clear that SDTM is really a data modelling framework built around clinical observations.

### The observation model
The central concept is that SDTM is built around observations collected about study subjects. Every row in an SDTM dataset represents a single observation and every column describes some aspect of that observation.

The observation framework can be reduced to four questions:

- Who is this about? → Identifier variables
- What is being observed? → Topic variables
- When did it happen? → Timing variables
- What additional details describe it? → Qualifier variables

Using the adverse event example from the guide:

Subject 101 had mild nausea on Study Day 6.

- Subject 101 = Identifier
- Nausea = Topic
- Day 6 = Timing
- Mild = Qualifier

This became the mental model that unlocked the rest of the chapter.

### Variable roles understood
Worked through the five SDTM variable roles and their purpose.

- Identifier variables identify the study subject domain and record
- Topic variables define the actual focus of the observation
- Timing variables describe when the observation occurred
- Qualifier variables add descriptive detail
- Rule variables support Trial Design datasets

The most important insight was that variables are not grouped by data type but by the job they perform within an observation.

### Qualifier hierarchy understood
The qualifier subclasses initially seemed abstract until working through examples.

- Result Qualifiers answer the question raised by the topic
- Record Qualifiers describe the observation as a whole
- Variable Qualifiers describe another variable
- Grouping Qualifiers organise related observations
- Synonym Qualifiers provide alternative names for the same concept

Using a laboratory result:

SUBJ005 CRP Day 7 12 mg/L

- CRP = Topic
- 12 = Result Qualifier
- mg/L = Variable Qualifier

This made the distinction between result values and metadata much clearer.

### The three General Observation Classes
Learned that most SDTM domains belong to one of three classes.

#### Interventions
Something done to the subject.

Examples:
- Study drug exposure
- Vaccination
- Concomitant medication

Question answered:
What did we do?

#### Events
Something that happened to the subject.

Examples:
- Adverse events
- Medical history
- Study completion

Question answered:
What happened?

#### Findings
Something measured or assessed.

Examples:
- Laboratory tests
- Vital signs
- PK concentrations
- Questionnaires

Question answered:
What did we observe?

This became the fastest way to classify new data.

### Special Purpose Domains understood
Learned why some domains sit outside the three observation classes.

- DM describes the subject
- SV describes visits attended
- SE describes study phases
- CO stores comments

The important distinction is that these domains support the trial structure itself rather than recording observations.

### Relational database connection finally clicked
The biggest breakthrough of the chapter was understanding the relationship between relational databases and SDTM.

A relational database stores information in separate linked tables using primary keys and foreign keys.

Example:

SUBJECT
VISIT
LAB_RESULT
EXPOSURE
ADVERSE_EVENT

SDTM represents the same information as submission-ready flat datasets.

The insight was that SDTM is not trying to replace a relational database. It is a standardised way of presenting the data after collection.

Operational Database
→ SDTM
→ ADaM
→ Analysis

The goal is not to build databases that look exactly like SDTM. The goal is to build databases that map naturally into SDTM.

### Data modelling lesson locked in
A principle emerged repeatedly throughout the chapter:

If something can happen many times it usually deserves its own table.

Examples:
- One subject can have many lab results
- One subject can have many PK samples
- One subject can have many adverse events
- One subject can have many doses

This naturally produces tall tables rather than wide tables and aligns closely with both relational database design and SDTM observation modelling.

### Custom domain design understood
Worked through the SDTM process for creating a new domain.

Key lessons:

- Reuse existing domains whenever possible
- Organise data by topic not collection method
- Do not create domains based on time
- Do not create domains based on endpoint importance
- Select the correct observation class first
- Add identifiers topic timing and qualifiers in that order

The process mirrors database design more closely than expected.

### Architectural lesson
The people who designed SDTM were solving the same problem database architects solve:

How do we represent clinical observations consistently without duplication while preserving meaning?

Understanding that connection made the guide far easier to read because the domains stopped looking arbitrary and started looking like modelling decisions.

### Next milestone
Begin Chapter 3 — Using the CDISC Domain Models in Regulatory Submissions.

Primary objectives:

- Understand dataset-level metadata
- Learn how DOMAIN values drive dataset identity
- Understand Define-XML structure and purpose
- Learn how SDTM datasets are formally described for regulatory submission
- Begin reading domain specifications as metadata rather than as lists of variables

## 2026-06-18 — Phase 1 SQL pipeline: staging tier stood up, D1 loaded (100 rows)

### What was built this session
The Oracle environment was brought online after a multi-stage listener and PDB fight, the P1_STAGING schema was created, and the first staging table — D1 — was loaded with all 100 screening records via SQL*Loader. A clean-repo loader layout was established and the D1 control file committed and pushed. Tier one is real, with one table in and the load pattern proven for the remaining seven.

### Environment correction — Enterprise Edition on ORCLPDB, not XE
The install is Oracle 21c Enterprise Edition, database ORCL, pluggable database ORCLPDB — not Express Edition / XEPDB1 as first assumed. All connections target the service `.../ORCLPDB`. Confirmed via the startup banner and `SHOW PDBS`.

### Incident — listener and database registration would not come up
A chain of connection failures, every one rooted in stale addresses left behind by a past machine rename (DESKTOP-UNGAQOD). Recorded because each is a standard Oracle-on-laptop trap.
- ORA-12541 no listener — the TNS listener service was stopped. `net start` reported a silent failure; `lsnrctl start` gave the real cause.
- TNS-12545 target host does not exist — `listener.ora` had HOST pinned to a dead IP, 10.0.0.35. Fixed by editing `C:\oracle\homes\OraDB21Home1\network\admin\listener.ora` to `HOST = localhost`.
- PDB MOUNTED, not open — full Oracle leaves PDBs closed on startup. `ALTER PLUGGABLE DATABASE ORCLPDB OPEN`, then `SAVE STATE` so it reopens on every reboot.
- ORA-12514 service not known — the database was not registering ORCLPDB with the listener. Root cause: `LOCAL_LISTENER` was set to the alias `LISTENER_ORCL`, resolving through a stale `tnsnames` entry. Fixed with `ALTER SYSTEM SET LOCAL_LISTENER='(ADDRESS=(PROTOCOL=TCP)(HOST=localhost)(PORT=1521))' SCOPE=BOTH;` then `ALTER SYSTEM REGISTER`. Service "orclpdb" then showed READY.

### Lesson learned
- A machine rename leaves the old host/IP in at least three places: `listener.ora`, `LOCAL_LISTENER`, and `tnsnames.ora`. Point each at `localhost`, never a literal IP, so a network change cannot break it again.
- `net start` hides errors; `lsnrctl start` / `lsnrctl status` give the real diagnosis. Go to the tool's own diagnostics, not the Windows service wrapper.
- `sql` and `sqlplus` are different programs — `sql` (SQLcl) crashed on a Java class error; `sqlplus` is the reliable client.
- `CONNECT / AS SYSDBA` logs in through Windows with no password and no listener — the way in when the listener is down.

### Staging schema and D1 table
- `CREATE USER p1_staging` in ORCLPDB — in Oracle the user is the schema. Granted CREATE SESSION, CREATE TABLE, and QUOTA UNLIMITED ON USERS.
- `d1_eligibility` staging table: all 26 columns typed VARCHAR2, faithful to the CSV, raw codes untouched. Staging-tier discipline — nothing can be rejected over a type; cleaning happens later in core.
- Loaded with SQL*Loader: 100 rows, 0 rejected.

### Bug caught — table built from wrong column names
The first `CREATE TABLE` used generic `i1`–`i7` / `e1`–`e9` placeholder names and 28 columns. The real D1 header has 26 columns with specific names: inclusion `i1_age, i2_bmi, i3_health, i6_comply, i7_consent` (i4/i5 where removed due to data redundancy in the instrument ) and exclusion `e1_cyp3a4`…`e9_previoustrial`. Caught before loading, dropped and rebuilt from the actual header. Lesson re-locked: read the real header before writing any DDL — never presume or assume  column names.

### Loader pattern locked for the remaining seven tables
- Portable control files in `sql/staging/*.ctl`: column mapping only, no `INFILE`/`BADFILE`/`DISCARDFILE` baked in. File locations supplied on the `sqlldr` command line via `data=`, `log=`, `bad=`, `discard=`.
- `OPTIONS (SKIP=1)` skips the header; `CHARACTERSET AL32UTF8`; `FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '"'` for quoted free-text; `TRAILING NULLCOLS`; `TRUNCATE` so re-runs stay idempotent; explicit `CHAR(n)` on long free-text fields to beat the loader's 255-character default.
- Write control files with a PowerShell here-string and `Set-Content -Encoding ASCII`, not Notepad — Notepad left `d1.ctl` at 0 bytes and the load failed SQL*Loader-501 / 561 until the file was rewritten.
- `.gitignore` excludes `*.log`, `*.bad`, `*.dsc`; the `.ctl` files are committed as real pipeline artifacts.

### Verified this session
- D1 row count: 100.
- Screening funnel intact in the database: `eligibility_determination` 1 = 28, 2 = 72, summing to 100. The funnel the whole schema is built around is now real in Oracle, not just on paper.
- Raw REDCap codes preserved in staging (`sex_at_birth` 1/2, `eligibility_determination` 1/2). Decoding deferred to analytics views, as designed.

### Next milestone
Load D2 (demographics and medical history, 28 rows) with the locked pattern: read the header, build the VARCHAR2 staging table, write `sql/staging/d2.ctl`, run `sqlldr`. Verify 28 rows and that all 28 join back to D1 records marked eligible, with no orphans. Then D3a through D7.

---
## 2026-06-19 — Phase 1 SQL pipeline: staging tier complete, all 8 tables loaded (660 rows)

### What was built this session
The full staging tier is loaded. All eight instrument CSVs are in Oracle as faithful VARCHAR2 mirror tables, 660 rows total, each load verified and idempotent. Eight portable SQL*Loader control files are committed under sql/staging/. Tier one is done; the core build is next.

### Final row counts — verified in-database
d1 100, d2 28, d3a 28, d3b 18, d4 144, d5 180, d6 90, d7 72. Total 660. Confirmed with a single UNION ALL roll-up across all eight tables.


### Staging schema and load pattern
- p1_staging user created in ORCLPDB (user = schema in Oracle); granted CREATE SESSION, CREATE TABLE, QUOTA UNLIMITED ON USERS.
- Every staging table is all-VARCHAR2, faithful to the CSV, raw REDCap codes preserved untouched. Decoding is deferred to the analytics layer.
- Portable control files in sql/staging/*.ctl: column mapping only, no baked-in paths; INFILE/log/bad/discard supplied on the sqlldr command line.
- Standard options locked: OPTIONS (SKIP=1), CHARACTERSET AL32UTF8, FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '"', TRAILING NULLCOLS, TRUNCATE for idempotent re-runs, explicit CHAR(n) on long free-text fields to beat the 255-char default.
- Control files written via PowerShell here-string + Set-Content -Encoding ASCII. Notepad left d1.ctl at 0 bytes (SQL*Loader-501/561) until rewritten — here-string is the reliable method.
- .gitignore excludes *.log, *.bad, *.dsc; .ctl files committed as pipeline artifacts.

### Verified this session — structure and narrative intact in SQL
- Screening funnel: eligibility_determination 1=28, 2=72, total 100.
- Randomisation: 6/6/6 across cohorts 1/2/3 plus 10 reserve (blank cohort) = 28.
- SRC: src_decision = 1 for all 18 reviews, all linking to randomised volunteers — every cohort gate opened, no DLT halted escalation.
- PK: D4 grain 18x8; volunteer ZA-CPT-P1-080 curve correct — BLQ pre-dose, peak 126.65, decay to BLQ by 48h, blq flag set only at the floor readings.
- Labs: D5 grain 18x10; 080 ALT normal at screening (25) and 48h (22), abnormal at day-7 (86) with any_lab_abnormal=1 — a delayed transaminase signal, lab root of the D6 AE.
- AEs: D6 split 23 real / 67 placeholder. 080 = Hot flushes (G1) + Transaminase elevation (G1, relatedness 4). 010 = Acute gastroenteritis, grade 3, relatedness 1 (unrelated), is_sae 1, criterion 3 (hospitalisation) — the serious-but-unrelated SAE that did not stop escalation.
- The cross-instrument narrative (D5 lab signal -> D6 AE; unrelated SAE -> D3b escalation proceeding) is intact and traceable by record_id across staging tables.

### Two-window discipline
sqlplus (SQL>) for DDL and verification queries; PowerShell/VS Code terminal (PS>) for here-strings and sqlldr. Crossing them throws errors — keep them separate. Confirm every load actually ran via its log/summary rather than inferring from a row count, since TRUNCATE makes a stale table look identical to a fresh load.

### Next milestone
Build the core tier. Start with the dimensions — subject (100, drawn from D1+D2+D3a) and visit (from event_mapping) — then the fact tables with surrogate keys and enforced foreign keys. Settle Fork B (wide vs long for D5 labs/vitals and D7 diary) before building those domain tables.

---
## 2026-06-22 — SDTMIG Chapters 3: observation model, metadata architecture, and submission framework understood

### What was learned this session
Completed SDTMIG Chapter 3, The major breakthrough was understanding that SDTM is not a database design standard but a submission standard built around clinical observations. The relationship between normalized relational databases and SDTM domain structures is now much clearer.

### Observation model understood
- SDTM is built around observations collected about study subjects.
- Every observation can be decomposed into:
  - Identifier variables (Who?)
  - Topic variables (What?)
  - Timing variables (When?)
  - Qualifier variables (Additional detail)
- The observation model became the common structure underlying all domains.

### General Observation Classes understood
- Interventions = something done to the subject.
- Events = something that happened to the subject.
- Findings = something measured or assessed.
- Classification now driven by the questions:
  - What did we do?
  - What happened?
  - What did we observe?

### Special Purpose domains understood
- DM describes the subject.
- SV describes visits attended.
- SE describes study phases or study elements.
- CO stores comments and free-text narrative information.
- These domains provide study context rather than observations.

### Relational database and SDTM connection established
- SDTM Findings domains use the same one-observation-per-row philosophy as normalized relational databases.
- Wide structures:
  - ALT, AST, CRP as separate columns
- Vertical structures:
  - TEST + RESULT as rows
- This mirrors the normalized designs planned for the core Oracle schema.

### Key architecture concepts clarified
- Natural key = business facts that uniquely identify an observation.
- Composite key = key composed of multiple columns.
- Surrogate key = artificial identifier created for row management.
- Primary key = identifier chosen by the database to uniquely identify rows.
- Observation uniqueness is determined by protocol and business rules rather than by inspecting data values.

Examples discussed:
- PK sample: Subject + Timepoint
- Laboratory result: Subject + Visit + Test

### Metadata architecture understood
Three metadata layers identified.

#### Dataset Metadata
Describes datasets.

Examples:
- Dataset name
- Structure
- Natural key definition

#### Variable Metadata
Describes variables.

Examples:
- LBTESTCD
- LBORRES
- LBSTRESN

#### Value-Level Metadata
Describes specific values within variables.

Examples:
- ALT
- CRP
- HEIGHT
- BMI

This explains how SDTM can maintain a highly normalized vertical structure while still preserving test-specific definitions, units, origins, and controlled terminology.

### Conformance requirements understood
Conformance requires:

- Standard domain names
- Standard variable names
- Standard datatypes
- Controlled terminology
- Required and Expected variables
- Proper Identifier, Topic, Timing, and Qualifier structure
- Compliance with domain-specific assumptions and business rules

Conformance is therefore more than variable naming; it is adherence to the complete SDTM modelling framework.

### Mental model established
Clinical Reality
→ Data Collection
→ Observations
→ Variables
→ Domains
→ Relational Database
→ SDTM Datasets
→ Metadata
→ Define-XML
→ Conformance Review
→ Regulatory Submission

This workflow now serves as the reference model for understanding future SDTM domains and metadata specifications.

### Next milestone
Continue Chapter 4.

---
## 2026-06-19 — Phase 1 core tier: entity-aligned schema fully planned

### What was decided this session
The complete core-tier schema was designed on paper before any DDL — every table, its grain, and a single home for every column, with no overlaps so joins stay clean. The driving rule throughout: each fact lives in exactly one table; other tables reach it by joining on record_id or visit, never by copying. Build starts next session from this plan.

### The placement rule that settled everything
A field's home is decided by grain, not by data type: how many times was it measured per person? Measured once and never repeats -> it is a stable attribute, lives on the entity's dimension table. Recurs across visits -> it is a finding, lives in a fact table with a visit link. This is the same logic SDTM uses (subject characteristics vs VS/LB findings). It resolved every borderline column this session.

### Person-level cluster — four tables, split by population and concern
Original instinct was one wide subject table; split into four because mixing identity, screening verdict, and trial-entry conflates different events on different populations. The tell that two things belong in separate tables: different row counts.
- subject — 100 rows, one per screened person. Identity and one-time measurements: record_id (natural key) + surrogate subject_id, dob, age_years, sex_at_birth, weight_kg, height_cm, bmi (from D1), race, ethnicity, country_birth, initials (from D2).
- eligibility — 100 rows, one per screened person. The screening verdict and checklist: i1_age/i2_bmi/i3_health/i6_comply/i7_consent, e1_cyp3a4..e9_previoustrial, eligibility_determination, screen_failure_reason, screen_failure_narrative, screening_date, screened_by. Joins to subject on record_id.
- enrollment — 18 rows (randomised only; reserve optional). The trial-entry event: enrolment_status, cohort, cohort_position, is_sentinel, cohort_open_date, planned_dose_mg, dose_per_kg, imp_batch, imp_expiry, pi_dosing_signoff. Exists only for those who entered — the 100-vs-18 asymmetry is real information a combined table could only show as blanks.
- medical_history — 28 rows (eligible only). pmh/surgery/allergy/med any+details, family_history, lifestyle (alcohol_units, caffeine_cups, exercise_freq, vaccine_uptodate, recent_vaccine), pi_assessment. Kept separate, not folded into eligibility: eligibility is 100 rows, medical history is 28 — different population, different table.

### Two placement traps caught by checking the data, not the column name
- Screening vitals (sbp_screen..spo2_screen in D2) looked like yes/no screening fields by name; the values are real numeric measurements (e.g. SBP 123, temp 37.2), identical in kind to D5 on-study vitals. So they are vitals, not eligibility fields — they go to vital_sign, tagged to the screening visit. Lesson re-locked: when column name and data disagree, the data wins.
- Height/weight/BMI are numbers but were measured once at screening and never repeat, so they are attributes on subject, not findings in vital_sign. Weight could be a finding in a trial that re-measures it; in this data it appears only in D1, once — so grain places it on subject. (Could later add the single screening weight to vital_sign as a baseline VS record to anticipate SDTM/Phase 2; deferred.)

### Dimension and fact tables
- visit — dimension, 11 rows from event_mapping.csv. Surrogate visit_id, event_name natural key. Every time-based fact links here.
- dosing — 18 rows, from D3a, FK subject. (Note: dose fields overlap with enrollment; to resolve at build — exposure event vs enrolment attributes.)
- src_review — 18 rows, from D3b, FK subject.
- pk_concentration — 144 rows, from D4, FK subject + visit. Already long in staging.
- adverse_event — 23 rows (ae_any=1 only), from D6, FK subject + visit. The 67 placeholders stay in staging.

### findings tables are LONG
vital_sign, lab_result, diary_symptom built long: one row per single measurement (volunteer, visit, test) with a test-name column and a value column, not one row of many columns.
- Why long: blank cells structurally cannot occur (a row exists only when a measurement happened — solves the empty-lab-cell problem seen in 080's D5 PK-timepoint rows); it is the shape Power BI wants (one value + one test column drives every slicer); 
---

## 2026-06-24 — Core tier: file-based DDL workflow set up, subject table built (100 rows)

### What was built this session
Moved from typing DDL at the prompt to writing saved .sql build scripts run through Oracle's VS Code extension, and built the first core table — subject — clean at 100 rows with its keys enforced. New folders sql/core/ and sql/setup/ hold the build scripts so the whole core is reproducible from the repo.

### Tooling — Oracle SQL Developer extension for VS Code
- Connected via Oracle's official extension (Basic connection, localhost:1521, Service Name ORCLPDB, user p1_staging). The two stale connection profiles it carried — sys@10.0.0.35 from the old machine name — were deleted; the live one points at localhost. Same stale-IP ghost as the listener fight, in a third place.
- Workflow discipline locked: build files (sql/core/*.sql) hold only drop/create/alter/insert/commit. Verification queries run separately by hand in a throwaway scratch.sql, never saved into the build file. Mixing the two earlier caused tangled, mis-ordered runs.

### subject build pattern (the template for the remaining core tables)
- DROP TABLE subject CASCADE CONSTRAINTS at the top so the script is re-runnable; CASCADE CONSTRAINTS so it still drops once child tables FK into it later. First run throws ORA-00942 (nothing to drop) — expected and harmless.
- subject_id NUMBER GENERATED ALWAYS AS IDENTITY as the surrogate key, defined inside CREATE TABLE.
- Named constraints: pk_subject (PRIMARY KEY on subject_id), uq_subject_record_id (UNIQUE on record_id). Naming them means a future violation reports a meaningful name, not a SYS_C string.
- Populated with INSERT...SELECT: D1 LEFT JOIN D2 on record_id, so all 100 D1 rows survive and the 72 screen-failures get NULL D2 columns. dob converted from ISO text with TO_DATE(d1.dob, 'YYYY-MM-DD'); numbers coerce to NUMBER automatically.
- Core types proper now, not staging's all-VARCHAR2: dob DATE, age NUMBER(3), weight/height NUMBER(5,1), bmi NUMBER(4,1). Raw codes (sex_at_birth, race) stay as codes — decoded later in views.

### Bugs caught and fixed
- ORA-01031 insufficient privileges on the identity column. Identity columns create a hidden sequence underneath, which needs CREATE SEQUENCE — never granted to p1_staging. Fixed with GRANT CREATE SEQUENCE TO p1_staging from a SYSDBA session inside ORCLPDB. (CREATE VIEW will likely be needed the same way when the analytics layer is built.)
- Table doubled to 200 rows. An INSERT is additive; re-running the build while the DROP was failing/skipped stacked a second 100 on top, producing duplicate record_ids. The DROP-first pattern plus the uq_subject_record_id unique constraint together make this impossible going forward — a second load now errors instead of silently doubling.
- Misread "race all NULL" as a broken join. The first five rows (001–005) are screen-failures with no D2 row, so NULL race is correct there; checking a row that is in D2 (010) showed race populated. Verified: 100 total, race populated for exactly the 28 eligible.

### Verified this session
subject: 100 rows, one per screened volunteer. race/ethnicity populated for the 28 eligible, NULL for 72 screen-failures (the LEFT JOIN behaving correctly). Constraints confirmed live via user_constraints (PK_SUBJECT type P, UQ_SUBJECT_RECORD_ID type U).

### Next milestone
Build eligibility (100), enrollment (18), medical_history (28), and the visit dimension, each as its own sql/core/*.sql following the subject pattern. Resolve the open enrollment-vs-dosing dose-field overlap when enrollment is built.
---