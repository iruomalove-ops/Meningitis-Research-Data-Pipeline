"""
simulate_d6.py
Generates simulated Phase 1 Adverse Events and SAE records (D6).
Reads d3a_dose_assignment.csv to find the 18 Randomised volunteers.
D6 fires at 5 events per volunteer: Day 0 dosing, T+8h, T+24h, T+48h, and Day 7.
At each volunteer-event combination, either one placeholder record with
ae_any=0 (no AEs to report) or one or more AE records with ae_any=1.
Implements a clinical narrative with:
  - Realistic baseline AEs scaling by cohort (50%/65%/80% across 2mg/4mg/8mg)
  - One engineered Grade 1 ALT elevation AE at Day 7 for the high responder
    (carries over from D5 cast member ZA-CPT-P1-080)
  - One engineered unrelated SAE: severe gastroenteritis with hospitalisation
    in a randomly selected non-cast volunteer between Day 3 and Day 5
"""

import random
import csv
from datetime import datetime, timedelta
# ==========================================
# SECTION 1: CONFIGURATIONS & TEMPLATE
# ==========================================

# 14 realistic dexamethasone single-dose Phase 1 AE terms with picking weights.
# Higher weight = more likely to be selected. Weights reflect real-world AE
# frequency in Phase 1 corticosteroid trials.
AE_TERM_POOL = [
    ("Headache",                              25),
    ("Nausea",                                20),
    ("Fatigue",                               15),
    ("Insomnia",                              12),
    ("Feeling jittery or restless",           10),
    ("Dry mouth",                              8),
    ("Increased appetite",                     8),
    ("Cannulation site discomfort",            7),
    ("Mild dizziness",                         6),
    ("Dyspepsia",                              5),
    ("Vivid dreams",                           5),
    ("Hot flushes",                            4),
    ("Mood change (irritability)",             3),
    ("Constipation",                           3)
]
# Probability each volunteer reports at least one AE across the trial.
# Scaled by cohort dose. Higher dose = higher AE probability.
COHORT_AE_RATE = {
    "1": 0.50,   # 2mg cohort - ~50% of volunteers report AEs
    "2": 0.65,   # 4mg cohort - ~65%
    "3": 0.80    # 8mg cohort - ~80%
}

# For volunteers who do report AEs, how many AEs they report total across the trial.
# Most volunteers with AEs report 1-2. A few report 3.
AE_COUNT_OPTIONS = [1, 2, 3]
AE_COUNT_WEIGHTS = [50, 35, 15]  # 50% report 1 AE, 35% report 2, 15% report 3
# Engineered narrative constants
## Engineered narrative constants - VERIFIED against REDCap data dictionary
# Thread 1: high responder Day 7 ALT elevation AE (matches D5 lab finding)
HIGH_RESPONDER_AE_TERM = "Transaminase elevation"
HIGH_RESPONDER_AE_GRADE = 1          # CTCAE Grade 1 mild
HIGH_RESPONDER_AE_RELATEDNESS = 4    # Probably related
HIGH_RESPONDER_AE_ONSET_DAY = 7
HIGH_RESPONDER_AE_OUTCOME = 3        # Recovering (ongoing at end of follow-up)
HIGH_RESPONDER_AE_ACTION = 1         # None (single-dose trial)

# Thread 2: unrelated SAE - severe gastroenteritis with hospitalisation
SAE_AE_TERM = "Acute gastroenteritis"
SAE_AE_GRADE = 3                  # CTCAE Grade 3 severe
SAE_AE_RELATEDNESS = 1            # Unrelated
SAE_AE_OUTCOME = 1                # Recovered without sequelae
SAE_AE_ACTION = 5                 # Not applicable (single-dose already complete)
SAE_ONSET_DAY_RANGE = (3, 5)      # Between Day 3 and Day 5
SAE_DURATION_DAYS = 2             # Recovers within 48 hours
SAE_CRITERION_CODE = 3            # Hospitalisation or prolongation
# Lock the random seed for reproducibility
random.seed(42)


# D6 schema template - field names verified against REDCap data dictionary
d6_template = {
    "record_id": "",
    "redcap_repeat_instance": "",
    "redcap_event_name": "",
    "ae_any": "",
    "ae_term": "",
    "ae_onset_date": "",
    "ae_onset_time": "",
    "ae_resolution_date": "",
    "ae_ongoing": "",
    "ae_ctcae_grade": "",
    "ae_relatedness": "",
    "ae_outcome": "",
    "ae_action": "",
    "ae_treatment": "",
    "is_sae": "",
    "sae_criterion": "",
    "sae_reported_sponsor_date": "",
    "sae_reported_ethics_date": "",
    "ae_pi_signoff": ""
}
# ==========================================
# SECTION 2: EVENT CONFIGURATION
# ==========================================

# D6 fires at 5 of the 11 events in the event grid.
# AEs are assessed at substantive clinical check-ins, not at every PK draw.
# Screening is excluded because volunteers are not yet dosed.
# T+30min through T+4h are excluded because those are brief PK visits.

D6_EVENTS = [
    {"name": "day_0__dosing_arm_1",    "label": "Day 0 Dosing",  "day_offset": 0},
    {"name": "pk_t8h_arm_1",           "label": "PK T+8h",       "day_offset": 0},
    {"name": "pk_t24h_arm_1",          "label": "PK T+24h",      "day_offset": 1},
    {"name": "pk_t48h_arm_1",          "label": "PK T+48h",      "day_offset": 2},
    {"name": "day_7_followup_arm_1",   "label": "Day 7",         "day_offset": 7}
]
# ==========================================
# SECTION 3: LOAD D3A AND FILTER TO RANDOMISED
# ==========================================

randomised_volunteers = []

print("Loading D3a data and filtering to Randomised volunteers...")

with open("d3a_dose_assignment.csv", mode="r", newline="", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        if row["enrolment_status"] == "Randomised":
            randomised_volunteers.append(row)

print(f"Randomised volunteers found: {len(randomised_volunteers)}")
# ==========================================
# SECTION 4: ASSIGN NARRATIVE ROLES
# ==========================================

# Read the D5 cast assignments so D6 knows which volunteers already have
# narrative roles. D6 must not assign the SAE to any of these volunteers
# to keep the narrative threads from overlapping.

d5_cast = {}  # record_id -> D5 role
high_responder_id = None

with open("d5_cast_assignments.csv", mode="r", newline="", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        d5_cast[row["record_id"]] = row["role"]
        if row["role"] == "high_responder":
            high_responder_id = row["record_id"]

# Pick the SAE volunteer randomly from the 14 non-cast volunteers.
# The high responder already has the engineered ALT AE so they cannot
# also carry the SAE. The other three D5 cast members are excluded to
# keep narrative threads cleanly separated per volunteer.
sae_candidates = [
    v for v in randomised_volunteers
    if v["record_id"] not in d5_cast
]
sae_volunteer = random.choice(sae_candidates)
sae_volunteer_id = sae_volunteer["record_id"]

# Verification print
print(f"\nD6 narrative role assignments:")
print(f"  High responder (carries from D5): {high_responder_id}")
print(f"  SAE volunteer (gastroenteritis):  {sae_volunteer_id}")
print(f"  D5 cast excluded from SAE pick:   {len(d5_cast)}")
print(f"  SAE candidate pool size:          {len(sae_candidates)} (should be 14)")
ae_spec = {
    "is_placeholder": False,        # True for ae_any=0 records
    "term": "Headache",
    "grade": 1,                     # CTCAE grade 1-5
    "relatedness": 3,               # 1=Unrelated through 5=Definitely related
    "onset_day": 0,                 # days from dosing
    "duration_days": 1,             # how long the AE lasts
    "outcome": 1,                   # outcome code
    "action": 1,                    # action taken code
    "treatment_notes": "Paracetamol PRN. Self-limited.",
    "is_sae": False,                # True for the gastroenteritis SAE
    "sae_criterion": None           # populated only if is_sae True
}
# ==========================================
# SECTION 5: BUILD MAKE_D6_RECORD FUNCTION
# ==========================================

def make_d6_record(volunteer, event, ae_spec):
    """
    Build one D6 record for one volunteer at one event for one AE specification.
    
    volunteer -- D3a record dict (Randomised only)
    event     -- one entry from D6_EVENTS list
    ae_spec   -- dictionary describing this AE record. Keys:
                 is_placeholder (bool), term, grade, relatedness, onset_day,
                 duration_days, outcome, action, treatment_notes, is_sae,
                 sae_criterion
    
    Returns a fully populated D6 record dict.
    """
    
    # ---------- Pull upstream values ----------
    record_id = volunteer["record_id"]
    cohort_open_date = volunteer["cohort_open_date"]
    open_dt = datetime.strptime(cohort_open_date, "%Y-%m-%d")
    
    # ---------- Initialise record from template ----------
    record = dict(d6_template)
    record["record_id"] = record_id
    record["redcap_event_name"] = event["name"]
    record["ae_pi_signoff"] = random.choice(["NMC", "TLO", "SJM"])
    
    # ---------- Placeholder case (no AEs at this assessment) ----------
    if ae_spec["is_placeholder"]:
        record["ae_any"] = 0
        return record
    
    # ---------- AE record case (an actual AE is reported) ----------
    record["ae_any"] = 1
    record["ae_term"] = ae_spec["term"]
    record["ae_ctcae_grade"] = ae_spec["grade"]
    record["ae_relatedness"] = ae_spec["relatedness"]
    record["ae_outcome"] = ae_spec["outcome"]
    record["ae_action"] = ae_spec["action"]
    record["ae_treatment"] = ae_spec["treatment_notes"]
    
    # Onset date and time
    onset_dt = open_dt + timedelta(days=ae_spec["onset_day"])
    record["ae_onset_date"] = onset_dt.strftime("%Y-%m-%d")
    onset_hour = random.randint(8, 20)
    onset_minute = random.randint(0, 59)
    record["ae_onset_time"] = f"{onset_hour:02d}:{onset_minute:02d}"
    
    # Resolution date and ongoing flag
    # If outcome is 3 (Recovering) the AE is still ongoing - no resolution date
    if ae_spec["outcome"] == 3:
        record["ae_ongoing"] = 1
        record["ae_resolution_date"] = ""
    else:
        record["ae_ongoing"] = 0
        resolution_dt = onset_dt + timedelta(days=ae_spec["duration_days"])
        record["ae_resolution_date"] = resolution_dt.strftime("%Y-%m-%d")
    
    # ---------- SAE-specific fields ----------
    if ae_spec["is_sae"]:
        record["is_sae"] = 1
        record["sae_criterion"] = ae_spec["sae_criterion"]
        # SAE reporting timelines per ICH GCP
        # Sponsor report: within 24h for fatal/life-threatening, 7 days otherwise
        # Ethics report: within 15 calendar days typically
        sponsor_report_dt = onset_dt + timedelta(days=1)  # within 24h
        ethics_report_dt = onset_dt + timedelta(days=7)   # well within 15 days
        record["sae_reported_sponsor_date"] = sponsor_report_dt.strftime("%Y-%m-%d")
        record["sae_reported_ethics_date"] = ethics_report_dt.strftime("%Y-%m-%d")
    else:
        record["is_sae"] = 0
    
    return record
# ==========================================
# SECTION 6: BUILD AE SCHEDULES AND GENERATE RECORDS
# ==========================================

def build_routine_ae_spec(onset_day):
    """
    Build a specification for one routine baseline AE.
    Term picked weighted from the pool. Grade mostly 1, sometimes 2.
    Onset day passed in by caller; duration and outcome derived.
    """
    # Pick term using weighted choice
    terms = [t for t, w in AE_TERM_POOL]
    weights = [w for t, w in AE_TERM_POOL]
    term = random.choices(terms, weights=weights, k=1)[0]
    
    # CTCAE grade: 80% Grade 1, 18% Grade 2, 2% Grade 3
    grade = random.choices([1, 2, 3], weights=[80, 18, 2], k=1)[0]
    
    # Relatedness: most routine AEs are possibly or probably related
    # Cannulation site discomfort is procedural, not drug-related
    if term == "Cannulation site discomfort":
        relatedness = 2  # Unlikely related (procedural)
    else:
        relatedness = random.choices([2, 3, 4], weights=[20, 50, 30], k=1)[0]
    
    # Duration: 1-3 days typical for these minor AEs
    duration = random.choices([1, 2, 3], weights=[50, 35, 15], k=1)[0]
    
    return {
        "is_placeholder": False,
        "term": term,
        "grade": grade,
        "relatedness": relatedness,
        "onset_day": onset_day,
        "duration_days": duration,
        "outcome": 1,  # Recovered without sequelae
        "action": 1,   # None
        "treatment_notes": "Self-limited. Symptomatic management as needed.",
        "is_sae": False,
        "sae_criterion": ""
    }


def build_high_responder_engineered_spec():
    """Build the engineered Grade 1 ALT elevation AE spec for the high responder."""
    return {
        "is_placeholder": False,
        "term": HIGH_RESPONDER_AE_TERM,
        "grade": HIGH_RESPONDER_AE_GRADE,
        "relatedness": HIGH_RESPONDER_AE_RELATEDNESS,
        "onset_day": HIGH_RESPONDER_AE_ONSET_DAY,
        "duration_days": 0,   # Not used because outcome is Recovering (ongoing)
        "outcome": HIGH_RESPONDER_AE_OUTCOME,
        "action": HIGH_RESPONDER_AE_ACTION,
        "treatment_notes": (
            "Mild ALT elevation noted at Day 7 follow-up. Volunteer is sentinel "
            "in 8mg cohort with strong T+48h response across glucose, neutrophilia "
            "and potassium. Considered probably related to study drug. No specific "
            "treatment indicated. Repeat LFTs scheduled in 48 hours. Flagged for "
            "SRC discussion."
        ),
        "is_sae": False,
        "sae_criterion": ""
    }


def build_sae_engineered_spec():
    """Build the engineered gastroenteritis SAE spec."""
    onset_day = random.randint(*SAE_ONSET_DAY_RANGE)
    return {
        "is_placeholder": False,
        "term": SAE_AE_TERM,
        "grade": SAE_AE_GRADE,
        "relatedness": SAE_AE_RELATEDNESS,
        "onset_day": onset_day,
        "duration_days": SAE_DURATION_DAYS,
        "outcome": SAE_AE_OUTCOME,
        "action": SAE_AE_ACTION,
        "treatment_notes": (
            f"Acute onset gastroenteritis with vomiting and diarrhoea. "
            f"Volunteer presented to emergency on Day {onset_day} with signs of "
            f"moderate dehydration. Admitted for overnight IV rehydration. "
            f"Symptoms resolved within 48 hours. Likely viral or food-borne. "
            f"Assessed as unrelated to study drug given clinical picture, timing "
            f"and absence of plausible mechanism for single-dose corticosteroid."
        ),
        "is_sae": True,
        "sae_criterion": SAE_CRITERION_CODE
    }


def build_ae_schedule_for_volunteer(volunteer):
    """
    Decide what AEs this volunteer reports and at which events.
    Returns a dict keyed by event name with a list of AE specs for that event.
    Empty list at an event means a placeholder record will be generated there.
    """
    record_id = volunteer["record_id"]
    cohort = volunteer["cohort"]
    schedule = {event["name"]: [] for event in D6_EVENTS}
    
    # Add engineered AEs first
    if record_id == high_responder_id:
        # ALT elevation at Day 7
        schedule["day_7_followup_arm_1"].append(build_high_responder_engineered_spec())
    
    if record_id == sae_volunteer_id:
        # Gastroenteritis SAE attached to Day 7 (the next event after onset)
        schedule["day_7_followup_arm_1"].append(build_sae_engineered_spec())
    
    # Decide if this volunteer reports any routine AEs based on cohort probability
    if random.random() < COHORT_AE_RATE[cohort]:
        # Yes - this volunteer reports routine AEs. How many?
        ae_count = random.choices(AE_COUNT_OPTIONS, weights=AE_COUNT_WEIGHTS, k=1)[0]
        
        # Pick which events the AEs occur at (one AE per event, can be different events)
        chosen_events = random.sample(D6_EVENTS, min(ae_count, len(D6_EVENTS)))
        
        for event in chosen_events:
            # Onset day matches the event day_offset
            onset_day = event["day_offset"]
            ae_spec = build_routine_ae_spec(onset_day)
            schedule[event["name"]].append(ae_spec)
    
    return schedule
# ---------- Main loop: generate all D6 records ----------
all_d6_records = []

for volunteer in randomised_volunteers:
    schedule = build_ae_schedule_for_volunteer(volunteer)
    repeat_instance = 0
    
    for event in D6_EVENTS:
        event_aes = schedule[event["name"]]
        
        if len(event_aes) == 0:
            # No AEs at this event - generate placeholder record
            repeat_instance = repeat_instance + 1
            placeholder_spec = {"is_placeholder": True}
            d6_record = make_d6_record(volunteer, event, placeholder_spec)
            d6_record["redcap_repeat_instance"] = repeat_instance
            all_d6_records.append(d6_record)
        else:
            # One or more AEs at this event - generate one record each
            for ae_spec in event_aes:
                repeat_instance = repeat_instance + 1
                d6_record = make_d6_record(volunteer, event, ae_spec)
                d6_record["redcap_repeat_instance"] = repeat_instance
                all_d6_records.append(d6_record)

print(f"\nD6 records generated: {len(all_d6_records)}")
# ==========================================
# SECTION 7: VERIFICATION AND CSV EXPORT
# ==========================================

# Verify total record count
print(f"\nAll volunteers covered: {len(set(r['record_id'] for r in all_d6_records))} (expected 18)")

# Count AE distribution by cohort
cohort_lookup = {v["record_id"]: v["cohort"] for v in randomised_volunteers}
ae_by_cohort = {"1": 0, "2": 0, "3": 0}
volunteers_with_aes_by_cohort = {"1": set(), "2": set(), "3": set()}
for record in all_d6_records:
    if record["ae_any"] == 1:
        cohort = cohort_lookup[record["record_id"]]
        ae_by_cohort[cohort] += 1
        volunteers_with_aes_by_cohort[cohort].add(record["record_id"])

print(f"\nAE distribution by cohort:")
for cohort_code in ["1", "2", "3"]:
    label = {"1": "2mg", "2": "4mg", "3": "8mg"}[cohort_code]
    n_aes = ae_by_cohort[cohort_code]
    n_vols = len(volunteers_with_aes_by_cohort[cohort_code])
    print(f"  {label} cohort: {n_aes} total AE records across {n_vols} of 6 volunteers")

# Verify engineered findings
print(f"\nEngineered findings verification:")
high_responder_ae = [r for r in all_d6_records 
                     if r["record_id"] == high_responder_id 
                     and r["ae_term"] == "Transaminase elevation"]
sae_record = [r for r in all_d6_records 
              if r["record_id"] == sae_volunteer_id 
              and r["is_sae"] == 1]
print(f"  High responder ALT elevation records: {len(high_responder_ae)} (expected 1)")
print(f"  SAE gastroenteritis records: {len(sae_record)} (expected 1)")
if high_responder_ae:
    r = high_responder_ae[0]
    print(f"    Onset: {r['ae_onset_date']}, Grade: {r['ae_ctcae_grade']}, Outcome: {r['ae_outcome']}")
if sae_record:
    r = sae_record[0]
    print(f"    Onset: {r['ae_onset_date']}, Grade: {r['ae_ctcae_grade']}, Sponsor report: {r['sae_reported_sponsor_date']}")

# Export to CSV
with open("d6_adverse_events_and_saes.csv", mode="w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=list(d6_template.keys()))
    writer.writeheader()
    writer.writerows(all_d6_records)

# Write the D6 cast assignments file for downstream scripts (D7 etc)
with open("d6_cast_assignments.csv", mode="w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["record_id", "role"])
    writer.writerow([high_responder_id, "high_responder"])
    writer.writerow([sae_volunteer_id, "sae_volunteer"])

print(f"\nD6 records saved to d6_adverse_events_and_saes.csv")
print(f"D6 cast assignments saved to d6_cast_assignments.csv")
