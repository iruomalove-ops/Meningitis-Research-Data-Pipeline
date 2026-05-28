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
Built simulate_d2.py from scratch using the same pattern locked in with simulate_d1.py. The script reads d1_eligibility.csv filters to the 20 eligible volunteers and generates a complete D2 record for each one. Output saved to d2_demographics_and_medical_history.csv ready for the next pipeline stage.

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
d2_demographics_and_medical_history.csv with 20 rows matching the eligible volunteers from D1. Each row has 25 fields populated with realistic clinically appropriate values.

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
Added record_id as the first field in d2_template. Updated the make_d2_record function return statement to pull record_id from the d1_record parameter using d1_record[record_id]. The make_d2_record function already received the d1_record as input so the data was available, we just had to use it. The d2_demographics_and_medical_history.csv now has record_id as its first column with values matching the eligible volunteers from D1.

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
- d2_demographics_and_medical_history.csv with 28 records for eligible volunteers
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