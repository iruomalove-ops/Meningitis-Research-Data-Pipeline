"""
simulate_d5.py
Generates simulated Phase 1 Safety Labs and Vitals records (D5).
Reads d3a_dose_assignment.csv to find the 18 Randomised volunteers,
d2_demographics_and_medical_history.csv for sex (needed for sex-specific
reference ranges), and d1_eligibility.csv for body weight.
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
HB_RANGE = {"1": (135, 175), "2": (120, 155)}        # keyed by REDCap sex code: 1=male, 2=female
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
CREATININE_RANGE = {"1": (60, 110), "2": (45, 90)}  #keyed by REDCap sex code
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
print(f"Defined {len(D5_EVENTS)} D5-mapped events:")
labs_count = sum(1 for e in D5_EVENTS if e["labs"])
vitals_only_count = sum(1 for e in D5_EVENTS if not e["labs"])
print(f"  Labs events: {labs_count} (should be 3)")
print(f"  Vitals-only events: {vitals_only_count} (should be 7)")
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