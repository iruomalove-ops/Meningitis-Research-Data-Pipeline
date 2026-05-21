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