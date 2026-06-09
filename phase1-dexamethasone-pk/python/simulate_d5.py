"""
simulate_d5.py
Generates simulated Phase 1 Safety Labs and Vitals records (D5).
Reads d3a_dose_assignment.csv to find the 18 Randomised volunteers,
d1_eligibility.csv for body weight and sex_at_birth (needed for
sex-specific reference ranges).
D5 fires at multiple events per volunteer. Lab fields populate only at
labs events (Screening, T+48h, Day 7) matching the REDCap branching logic.
Vital signs populate at every D5-mapped event.
Implements a clinical narrative with one engineered high-responder
volunteer in the 8mg cohort showing a Day 7 Grade 1 ALT elevation.
"""

import random
import csv
from datetime import datetime, timedelta
# ==========================================
# SECTION 1: CONFIGURATIONS & TEMPLATE
# ==========================================

# Lab reference ranges (lower bound, upper bound).
# Sources: standard adult clinical reference ranges from major textbooks.
# Some tests have sex-specific ranges — those are dictionaries keyed by sex.

# Haematology - full blood count
HB_RANGE = {
    "1": (135, 175),     # Male
    "2": (120, 155),     # Female
    "3": (120, 175)      # Intersex or indeterminate - union range covering both
}
WCC_RANGE = (4.0, 11.0)         # 10^9/L
NEUTROPHIL_RANGE = (2.0, 7.5)   # 10^9/L
LYMPHOCYTE_RANGE = (1.0, 4.0)   # 10^9/L
PLATELET_RANGE = (150, 400)     # 10^9/L

# Liver function tests
ALT_RANGE = (10, 40)            # U/L
AST_RANGE = (10, 40)            # U/L
BILIRUBIN_RANGE = (3, 21)       # umol/L
ALP_RANGE = (30, 130)           # U/L
ALBUMIN_RANGE = (35, 50)        # g/L

# Renal function and electrolytes
CREATININE_RANGE = {
    "1": (60, 110),     # Male
    "2": (45, 90),      # Female
    "3": (45, 110)      # Intersex or indeterminate - union range covering both
}
UREA_RANGE = (2.5, 7.5)         # mmol/L
EGFR_NORMAL = (90, 120)         # mL/min/1.73m2
SODIUM_RANGE = (135, 145)       # mmol/L
POTASSIUM_RANGE = (3.5, 5.0)    # mmol/L
CHLORIDE_RANGE = (98, 107)      # mmol/L

# Glucose
GLUCOSE_FASTED_RANGE = (3.9, 5.5)    # mmol/L, fasted
GLUCOSE_NONFASTED_RANGE = (3.9, 7.8) # mmol/L, non-fasted
# Drug effects at T+48h scale with cohort dose.
# These are multiplicative adjustments to the baseline value.
# 1.0 means no change. 1.2 means 20 percent above baseline.

# Glucose rise (transient hyperglycaemia from gluconeogenesis)
GLUCOSE_EFFECT_T48H = {
    "1": 1.05,  # 2mg cohort - slight uptick
    "2": 1.15,  # 4mg cohort - clearer rise
    "3": 1.30   # 8mg cohort - prominent rise
}

# Neutrophil rise (demargination effect)
NEUTROPHIL_EFFECT_T48H = {
    "1": 1.10,
    "2": 1.50,
    "3": 1.80
}

# Lymphocyte drop (redistribution effect)
LYMPHOCYTE_EFFECT_T48H = {
    "1": 0.95,
    "2": 0.80,
    "3": 0.65
}

# Potassium drop (transient hypokalaemia from mineralocorticoid effect)
POTASSIUM_EFFECT_T48H = {
    "1": 0.98,
    "2": 0.93,
    "3": 0.88
}

# At Day 7 most drug effects have resolved. Small residual on glucose only.
DAY7_RESIDUAL_GLUCOSE = {
    "1": 1.00,
    "2": 1.02,
    "3": 1.05
}
# Story C engineered narrative
# One volunteer in the 8mg cohort is the high responder.
# Selected deterministically in Section 5 using the random seed.
# Their T+48h values come from the upper end of the 8mg distributions.
# Their Day 7 ALT is engineered to land in CTCAE Grade 1 territory.

HIGH_RESPONDER_ALT_DAY7_RANGE = (80, 100)  # U/L, clearly Grade 1
HIGH_RESPONDER_GLUCOSE_BOOST_T48H = 1.10   # additional 10% above cohort average
HIGH_RESPONDER_NEUTROPHIL_BOOST_T48H = 1.15
HIGH_RESPONDER_POTASSIUM_DROP_T48H = 0.95  # extra 5% drop below cohort average
# Lock the random seed for reproducibility
random.seed(42)
# D5 schema template - 31 fields plus REDCap structural columns
d5_template = {
    "record_id": "",
    "redcap_repeat_instance": "",
    "redcap_event_name": "",
    "d5_lab_collection_date": "",
    "d5_lab_collection_time": "",
    "d5_fasting_status": "",
    "d5_sbp": "",
    "d5_dbp": "",
    "d5_hr": "",
    "d5_temp": "",
    "d5_rr": "",
    "d5_spo2": "",
    "d5_hb": "",
    "d5_wcc": "",
    "d5_neutrophils": "",
    "d5_lymphocytes": "",
    "d5_platelets": "",
    "d5_alt": "",
    "d5_ast": "",
    "d5_bilirubin": "",
    "d5_alp": "",
    "d5_albumin": "",
    "d5_creatinine": "",
    "d5_urea": "",
    "d5_egfr": "",
    "d5_sodium": "",
    "d5_potassium": "",
    "d5_chloride": "",
    "d5_glucose": "",
    "d5_glucose_high_flag": "",
    "d5_any_lab_abnormal": "",
    "d5_abnormal_details": "",
    "d5_action_taken": "",
    "d5_pi_signoff": ""
}
# ==========================================
# SECTION 2: EVENT CONFIGURATION
# ==========================================

# D5 fires at 10 of the 11 events in the event grid.
# Lab fields are conditionally populated at the three labs events,
# matching the REDCap branching logic on the lab fields.
# Vitals always populate at every D5-mapped event.
# SRC Review is not in this list because D5 is not mapped to that event.

D5_EVENTS = [
    {"name": "screening_arm_1",        "label": "Screening",     "day_offset": -7,  "labs": True},
    {"name": "day_0__dosing_arm_1",    "label": "Day 0 Dosing",  "day_offset": 0,   "labs": False},
    {"name": "pk_t30min_arm_1",        "label": "PK T+30min",    "day_offset": 0,   "labs": False},
    {"name": "pk_t1h_arm_1",           "label": "PK T+1h",       "day_offset": 0,   "labs": False},
    {"name": "pk_t2h_arm_1",           "label": "PK T+2h",       "day_offset": 0,   "labs": False},
    {"name": "pk_t4h_arm_1",           "label": "PK T+4h",       "day_offset": 0,   "labs": False},
    {"name": "pk_t8h_arm_1",           "label": "PK T+8h",       "day_offset": 0,   "labs": False},
    {"name": "pk_t24h_arm_1",          "label": "PK T+24h",      "day_offset": 1,   "labs": False},
    {"name": "pk_t48h_arm_1",          "label": "PK T+48h",      "day_offset": 2,   "labs": True},
    {"name": "day_7_followup_arm_1",   "label": "Day 7",         "day_offset": 7,   "labs": True}
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
# SECTION 4: LOAD D1 FOR DEMOGRAPHIC DATA
# ==========================================

# D1 gives us weight and sex_at_birth.
# Sex is needed for sex-specific reference ranges on Hb and creatinine.
# Stored as REDCap code: "1" male, "2" female. Used directly as the dictionary key.

d1_weights = {}
d1_sex = {}

with open("d1_eligibility.csv", mode="r", newline="", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        d1_weights[row["record_id"]] = float(row["weight_kg"])
        d1_sex[row["record_id"]] = row["sex_at_birth"]

print(f"D1 demographics loaded: {len(d1_weights)} records (weight and sex)")
# ==========================================
# SECTION 5: ASSIGN NARRATIVE ROLES
# ==========================================

# Selections are deterministic because of random.seed(42) locked in Section 1.
# Same volunteers get the same roles every run.

narrative_roles = {}  # record_id -> role name
taken_ids = set()     # track record_ids already assigned a role

# Selection 1: high responder - must be a sentinel in the 8mg cohort (cohort 3)
high_responder_candidates = [
    v for v in randomised_volunteers
    if v["cohort"] == "3" and v["is_sentinel"] == "1"
]
high_responder = random.choice(high_responder_candidates)
narrative_roles[high_responder["record_id"]] = "high_responder"
taken_ids.add(high_responder["record_id"])

# Selection 2: anaemic volunteer - must be female, not already taken
anaemic_candidates = [
    v for v in randomised_volunteers
    if d1_sex[v["record_id"]] == "2" and v["record_id"] not in taken_ids
]
anaemic = random.choice(anaemic_candidates)
narrative_roles[anaemic["record_id"]] = "anaemic"
taken_ids.add(anaemic["record_id"])

# Selection 3: ALT-elevated volunteer - any sex, not already taken
alt_candidates = [
    v for v in randomised_volunteers
    if v["record_id"] not in taken_ids
]
alt_carrier = random.choice(alt_candidates)
narrative_roles[alt_carrier["record_id"]] = "alt_elevated"
taken_ids.add(alt_carrier["record_id"])

# Selection 4: dehydrated volunteer - any sex, not already taken
dehydrated_candidates = [
    v for v in randomised_volunteers
    if v["record_id"] not in taken_ids
]
dehydrated = random.choice(dehydrated_candidates)
narrative_roles[dehydrated["record_id"]] = "dehydrated"
taken_ids.add(dehydrated["record_id"])

# Verification print
print(f"\nNarrative role assignments:")
print(f"  High responder (8mg sentinel): {high_responder['record_id']}")
print(f"  Anaemic (female):              {anaemic['record_id']}")
print(f"  ALT elevated:                  {alt_carrier['record_id']}")
print(f"  Dehydrated:                    {dehydrated['record_id']}")
print(f"  Normal volunteers:             {18 - len(taken_ids)}")
# ==========================================
# SECTION 6: BUILD MAKE_D5_RECORD FUNCTION
# ==========================================

def generate_lab_value(ref_range, multiplier=1.0, shift_fraction=0.0):
    """
    Generate one realistic lab value within or near a reference range.
    
    ref_range       -- tuple of (low, high) defining the normal range
    multiplier      -- multiplicative adjustment (1.0 = no change, 1.3 = 30% higher)
    shift_fraction  -- positive shifts toward upper bound, negative toward lower
                       (e.g. 0.5 pushes the value 50% of the way toward the upper limit)
    
    Returns a value drawn from a Gaussian distribution centred near the middle
    of the range with realistic spread, then adjusted by multiplier and shift.
    """
    low, high = ref_range
    midpoint = (low + high) / 2
    spread = (high - low) / 6  # standard deviation = 1/6 of the range
    
    # Apply shift fraction to move the centre of the distribution
    if shift_fraction > 0:
        target_centre = midpoint + (high - midpoint) * shift_fraction
    elif shift_fraction < 0:
        target_centre = midpoint + (midpoint - low) * shift_fraction
    else:
        target_centre = midpoint
    
    value = random.gauss(target_centre, spread)
    value = value * multiplier
    
    return value


def make_d5_record(volunteer, event):
    """
    Build one D5 record for one volunteer at one event.
    
    volunteer -- D3a record dict (Randomised only)
    event     -- one entry from D5_EVENTS list
    
    Returns a fully populated D5 record dict.
    """
    
    # ---------- Pull upstream values ----------
    record_id = volunteer["record_id"]
    cohort = volunteer["cohort"]
    cohort_open_date = volunteer["cohort_open_date"]
    sex = d1_sex[record_id]
    
    # Narrative role (None if this is a normal volunteer)
    role = narrative_roles.get(record_id)
    
    # ---------- Visit context fields ----------
    open_dt = datetime.strptime(cohort_open_date, "%Y-%m-%d")
    visit_date = open_dt + timedelta(days=event["day_offset"])
    
    if event["labs"]:
        collection_hour = random.randint(7, 9)
    else:
        collection_hour = random.randint(8, 16)
    collection_minute = random.randint(0, 59)
    collection_time_str = f"{collection_hour:02d}:{collection_minute:02d}"
    
    if event["labs"]:
        fasting_status = 1
    else:
        fasting_status = 3
    
    # ---------- Initialise the record with template defaults ----------
    record = dict(d5_template)
    record["record_id"] = record_id
    record["redcap_event_name"] = event["name"]
    record["d5_lab_collection_date"] = visit_date.strftime("%Y-%m-%d")
    record["d5_lab_collection_time"] = collection_time_str
    record["d5_fasting_status"] = fasting_status
    
    # ---------- Vitals (populate at every event) ----------
    record["d5_sbp"] = round(random.gauss(120, 8))
    record["d5_dbp"] = round(random.gauss(78, 6))
    record["d5_hr"] = round(random.gauss(72, 8))
    record["d5_temp"] = round(random.gauss(36.7, 0.2), 1)
    record["d5_rr"] = round(random.gauss(15, 2))
    record["d5_spo2"] = round(random.gauss(98, 1))
    
    # ---------- Event conditional fork ----------
    if not event["labs"]:
        record["d5_any_lab_abnormal"] = 0
        record["d5_abnormal_details"] = ""
        record["d5_action_taken"] = ""
        record["d5_pi_signoff"] = random.choice(["NMC", "TLO", "SJM"])
        return record
# ---------- Labs event reached ----------
    # Block 6d generates lab values for screening, T+48h, and Day 7 events.
    # Logic flows in two layers:
    #   1. Determine event-specific multipliers and shifts based on cohort and role
    #   2. Generate each lab value using the helper, applying those adjustments
    
    # Event identification for branching
    is_screening = event["name"] == "screening_arm_1"
    is_t48h = event["name"] == "pk_t48h_arm_1"
    is_day7 = event["name"] == "day_7_followup_arm_1"
    
    # ---------- Role-driven multipliers and shifts ----------
    # Default: no role effects
    glucose_mult = 1.0
    neutrophil_mult = 1.0
    lymphocyte_mult = 1.0
    potassium_mult = 1.0
    
    alt_shift = 0.0       # shift fraction for ALT (positive shifts toward upper bound)
    hb_shift = 0.0        # shift fraction for haemoglobin (negative shifts toward lower bound)
    creatinine_shift = 0.0
    sodium_shift = 0.0
    
    # Apply incidental findings (these persist across all events)
    if role == "alt_elevated":
        alt_shift = 0.8   # ALT pushed toward upper end of normal at all events
    elif role == "anaemic":
        hb_shift = -0.8   # Hb pushed toward lower end of normal at all events
    elif role == "dehydrated":
        if is_screening:
            creatinine_shift = 0.6
            sodium_shift = 0.5
        else:
            creatinine_shift = 0.3   # resolves modestly after admission/rehydration
            sodium_shift = 0.2
    
    # Apply drug effects at T+48h (cohort-scaled)
    if is_t48h:
        glucose_mult = GLUCOSE_EFFECT_T48H[cohort]
        neutrophil_mult = NEUTROPHIL_EFFECT_T48H[cohort]
        lymphocyte_mult = LYMPHOCYTE_EFFECT_T48H[cohort]
        potassium_mult = POTASSIUM_EFFECT_T48H[cohort]
        
        # High responder boost on top of cohort effect
        if role == "high_responder":
            glucose_mult = glucose_mult * HIGH_RESPONDER_GLUCOSE_BOOST_T48H
            neutrophil_mult = neutrophil_mult * HIGH_RESPONDER_NEUTROPHIL_BOOST_T48H
            potassium_mult = potassium_mult * HIGH_RESPONDER_POTASSIUM_DROP_T48H
    
    # Apply mostly-resolved residual at Day 7
    if is_day7:
        glucose_mult = DAY7_RESIDUAL_GLUCOSE[cohort]
    
    # ---------- Haematology panel ----------
    record["d5_hb"] = round(generate_lab_value(HB_RANGE[sex], shift_fraction=hb_shift))
    record["d5_wcc"] = round(generate_lab_value(WCC_RANGE), 1)
    record["d5_neutrophils"] = round(generate_lab_value(NEUTROPHIL_RANGE, multiplier=neutrophil_mult), 1)
    record["d5_lymphocytes"] = round(generate_lab_value(LYMPHOCYTE_RANGE, multiplier=lymphocyte_mult), 1)
    record["d5_platelets"] = round(generate_lab_value(PLATELET_RANGE))
    
    # ---------- Liver function panel ----------
    # ALT carries the engineered Day 7 signal for the high responder
    if is_day7 and role == "high_responder":
        # Engineered Grade 1 ALT elevation 80-100 U/L
        alt_value = random.uniform(*HIGH_RESPONDER_ALT_DAY7_RANGE)
    else:
        alt_value = generate_lab_value(ALT_RANGE, shift_fraction=alt_shift)
    record["d5_alt"] = round(alt_value)
    
    record["d5_ast"] = round(generate_lab_value(AST_RANGE))
    record["d5_bilirubin"] = round(generate_lab_value(BILIRUBIN_RANGE))
    record["d5_alp"] = round(generate_lab_value(ALP_RANGE))
    record["d5_albumin"] = round(generate_lab_value(ALBUMIN_RANGE))
    
    # ---------- Renal function and electrolytes ----------
    record["d5_creatinine"] = round(generate_lab_value(CREATININE_RANGE[sex], shift_fraction=creatinine_shift))
    record["d5_urea"] = round(generate_lab_value(UREA_RANGE), 1)
    record["d5_egfr"] = round(generate_lab_value(EGFR_NORMAL))
    record["d5_sodium"] = round(generate_lab_value(SODIUM_RANGE, shift_fraction=sodium_shift))
    record["d5_potassium"] = round(generate_lab_value(POTASSIUM_RANGE, multiplier=potassium_mult), 1)
    record["d5_chloride"] = round(generate_lab_value(CHLORIDE_RANGE))
    
    # ---------- Glucose ----------
    # Use fasted range at labs events (volunteers fasted overnight)
    record["d5_glucose"] = round(generate_lab_value(GLUCOSE_FASTED_RANGE, multiplier=glucose_mult), 1)
    
    # d5_glucose_high_flag is descriptive (display-only in REDCap), leave empty
    record["d5_glucose_high_flag"] = ""
    
   # ---------- Investigator review ----------
    # Flag clinically significant findings based on what was actually generated.
    # Not every out-of-range value gets flagged - mirroring investigator judgement.
    
    abnormal = 0
    details = ""
    action = ""
    
    alt_value = record["d5_alt"]
    glucose_value = record["d5_glucose"]
    
    #  engineered signal: high responder Grade 1 ALT at Day 7
    if is_day7 and role == "high_responder" and alt_value >= 80:
        abnormal = 1
        details = (
            f"ALT elevated to {alt_value} U/L (CTCAE Grade 1, "
            f">ULN up to 3xULN). Volunteer is sentinel in 8mg cohort and showed "
            f"strongest cohort response at T+48h across glucose neutrophilia and "
            f"potassium. Day 7 ALT represents emerging late finding warranting "
            f"SRC review and consideration of additional safety monitoring."
        )
        action = "Repeat ALT in 48 hours. Notify medical monitor. Flag for SRC discussion."
    
    # ALT-elevated incidental carrier with actual abnormal ALT at this event
    elif role == "alt_elevated" and alt_value > 40:
        abnormal = 1
        details = (
            f"ALT {alt_value} U/L, above ULN of 40. Consistent with this "
            f"volunteer's baseline mildly elevated transaminases noted at "
            f"screening. Not considered drug-related given consistency across "
            f"visits and absence of trend."
        )
        action = "Continue routine monitoring. No protocol-specified action required."
    
    # 8mg cohort at T+48h with prominent transient hyperglycaemia
    elif is_t48h and cohort == "3" and glucose_value > 7.0:
        abnormal = 1
        details = (
            f"Fasted glucose {glucose_value} mmol/L, above upper normal of "
            f"5.5. Consistent with expected transient corticosteroid-induced "
            f"hyperglycaemia in 8mg cohort. Expected to resolve by Day 7."
        )
        action = "No immediate action. Repeat glucose at Day 7 follow-up."
    
    record["d5_any_lab_abnormal"] = abnormal
    record["d5_abnormal_details"] = details
    record["d5_action_taken"] = action
    record["d5_pi_signoff"] = random.choice(["NMC", "TLO", "SJM"])
    
    return record
# ==========================================
# SECTION 7: NESTED LOOP GENERATING ALL D5 RECORDS
# ==========================================

# Each volunteer gets one D5 record per event D5 is mapped to.
# 18 Randomised volunteers × 10 D5-mapped events = 180 records.

all_d5_records = []

for volunteer in randomised_volunteers:
    repeat_instance = 0
    for event in D5_EVENTS:
        repeat_instance = repeat_instance + 1
        d5_record = make_d5_record(volunteer, event)
        d5_record["redcap_repeat_instance"] = repeat_instance
        all_d5_records.append(d5_record)

print(f"\nD5 records generated: {len(all_d5_records)}")
# ==========================================
# SECTION 8: VERIFICATION AND CSV EXPORT
# ==========================================

# Verify each volunteer got exactly 10 records
records_per_volunteer = {}
for record in all_d5_records:
    rid = record["record_id"]
    if rid not in records_per_volunteer:
        records_per_volunteer[rid] = 0
    records_per_volunteer[rid] = records_per_volunteer[rid] + 1

all_have_ten = all(count == 10 for count in records_per_volunteer.values())
print(f"All volunteers have 10 records: {all_have_ten}")
print(f"Unique volunteers: {len(records_per_volunteer)}")

# Verify lab fields empty at vitals-only events and populated at labs events
labs_event_names = {"screening_arm_1", "pk_t48h_arm_1", "day_7_followup_arm_1"}
vitals_only_with_labs_populated = 0
labs_events_with_labs_empty = 0
for record in all_d5_records:
    is_labs_event = record["redcap_event_name"] in labs_event_names
    hb_populated = record["d5_hb"] != ""
    if is_labs_event and not hb_populated:
        labs_events_with_labs_empty += 1
    elif (not is_labs_event) and hb_populated:
        vitals_only_with_labs_populated += 1
print(f"Vitals-only events with labs incorrectly populated: {vitals_only_with_labs_populated} (should be 0)")
print(f"Labs events with labs incorrectly empty: {labs_events_with_labs_empty} (should be 0)")

# Verify the engineered Story C signal
high_responder_id = high_responder["record_id"]
print(f"\nEngineered signal verification:")
for record in all_d5_records:
    if record["record_id"] == high_responder_id and record["redcap_event_name"] == "day_7_followup_arm_1":
        print(f"  High responder Day 7 ALT: {record['d5_alt']} U/L (expected 80-100)")
        print(f"  High responder Day 7 abnormal flag: {record['d5_any_lab_abnormal']} (expected 1)")

# Verify dose-scaled effects at T+48h
print(f"\nT+48h dose-scaled effects (mean values by cohort):")
for cohort_code in ["1", "2", "3"]:
    cohort_records = [r for r in all_d5_records 
                      if r["redcap_event_name"] == "pk_t48h_arm_1"
                      and any(v["cohort"] == cohort_code and v["record_id"] == r["record_id"] for v in randomised_volunteers)]
    if cohort_records:
        mean_glucose = sum(float(r["d5_glucose"]) for r in cohort_records) / len(cohort_records)
        mean_neutrophils = sum(float(r["d5_neutrophils"]) for r in cohort_records) / len(cohort_records)
        mean_potassium = sum(float(r["d5_potassium"]) for r in cohort_records) / len(cohort_records)
        cohort_label = {"1": "2mg", "2": "4mg", "3": "8mg"}[cohort_code]
        print(f"  Cohort {cohort_label}: glucose={mean_glucose:.2f}  neutrophils={mean_neutrophils:.2f}  potassium={mean_potassium:.2f}")

# Export to CSV
with open("d5_safety_labs_and_vitals.csv", mode="w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=list(d5_template.keys()))
    writer.writeheader()
    writer.writerows(all_d5_records)

print(f"\nD5 records saved to d5_safety_labs_and_vitals.csv")
with open("d5_cast_assignments.csv", mode="w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["record_id", "role"])
    for rid, role in narrative_roles.items():
        writer.writerow([rid, role])
