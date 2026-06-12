"""
simulate_d7.py
Generates simulated Phase 1 Volunteer Symptom Diary records (D7).
Reads d3a_dose_assignment.csv for the 18 Randomised volunteers and
d5_cast_assignments.csv and d6_cast_assignments.csv to inherit the
engineered narrative cast from upstream instruments.
D7 fires at 4 events per volunteer giving 72 records total.
Each record is one diary entry covering the period since the last entry.
Symptom severity uniformly rated 0-3 (None, Mild, Moderate, Severe).
Implements the following clinical narrative:
  - Realistic baseline: D7 is quiet because single-dose dexamethasone is
    well-tolerated in healthy volunteers. Most ratings are 0 None.
  - Cohort-scaled symptom density: 8mg cohort reports slightly more than 2mg.
  - High responder ZA-CPT-P1-080 reports mild insomnia and fatigue.
  - SAE volunteer ZA-CPT-P1-010 reports escalating GI symptoms on Day 3
    leading up to the formal SAE, then recovery by Day 7.
"""

import random
import csv
from datetime import datetime, timedelta


# ==========================================
# SECTION 1: CONFIGURATIONS & TEMPLATE
# ==========================================

# Baseline symptom severity probabilities by cohort.
# Each symptom on a given day has a probability of being rated at each level.
# Probabilities sum to 1.0 for each (cohort, symptom-category) combination.
# Most ratings are 0 (None) reflecting that single-dose dex is well-tolerated.

# Probabilities of each rating [P(None), P(Mild), P(Moderate), P(Severe)]
# by cohort, for COMMON symptoms (insomnia, fatigue, appetite)
COMMON_SYMPTOM_RATES = {
    "1": [0.75, 0.20, 0.05, 0.00],   # 2mg cohort - mostly None
    "2": [0.68, 0.25, 0.06, 0.01],   # 4mg cohort - slightly more
    "3": [0.60, 0.30, 0.09, 0.01]    # 8mg cohort - slightly more again
}

# Probabilities for LESS COMMON symptoms (headache, nausea, mood, gi)
UNCOMMON_SYMPTOM_RATES = {
    "1": [0.90, 0.08, 0.02, 0.00],   # 2mg cohort - very quiet
    "2": [0.85, 0.12, 0.03, 0.00],   # 4mg cohort
    "3": [0.80, 0.16, 0.04, 0.00]    # 8mg cohort
}

# Engineered narrative constants
HIGH_RESPONDER_INSOMNIA_DAY1 = 2     # Moderate insomnia first night post-dose
HIGH_RESPONDER_FATIGUE_BOOST = 1     # Extra 1 level boost on fatigue across the trial

# SAE volunteer GI symptoms escalate Day 3 then recover
SAE_GI_DAY3_RATING = 3               # Severe GI by T+48h event (Day 3)
SAE_NAUSEA_DAY3_RATING = 3           # Severe nausea
SAE_FATIGUE_DAY3_RATING = 2          # Moderate fatigue from illness
SAE_DAY7_RECOVERY_RATING = 0         # All resolved by Day 7

# Lock the random seed for reproducibility
random.seed(42)


# D7 schema template - 14 fields plus REDCap structural columns
# Verified against the D7 data dictionary
d7_template = {
    "record_id": "",
    "redcap_repeat_instance": "",
    "redcap_event_name": "",
    "diary_date": "",
    "diary_day": "",
    "sym_headache": "",
    "sym_fatigue": "",
    "sym_nausea": "",
    "sym_insomnia": "",
    "sym_mood": "",
    "sym_appetite": "",
    "sym_gi": "",
    "sym_other": "",
    "sym_other_details": "",
    "diary_medication": "",
    "diary_med_details": "",
    "diary_completed_by": ""
}
# ==========================================
# SECTION 2: EVENT CONFIGURATION
# ==========================================

# D7 fires at 4 events. Each event corresponds to one diary entry covering
# the period since the last entry. diary_day records which day of the trial
# this entry represents per the REDCap dropdown (1=dose day, 2=Day 2, etc).

D7_EVENTS = [
    {"name": "day_0__dosing_arm_1",   "label": "Day 0 Dosing",  "day_offset": 0,  "diary_day": 1},
    {"name": "pk_t24h_arm_1",         "label": "PK T+24h",      "day_offset": 1,  "diary_day": 2},
    {"name": "pk_t48h_arm_1",         "label": "PK T+48h",      "day_offset": 2,  "diary_day": 3},
    {"name": "day_7_followup_arm_1",  "label": "Day 7",         "day_offset": 7,  "diary_day": 7}
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
# SECTION 4: LOAD CAST ASSIGNMENTS FROM D5 AND D6
# ==========================================

# D7 inherits engineered narrative roles from upstream instruments.
# D5 wrote the high responder, anaemic, ALT-elevated, and dehydrated cast.
# D6 wrote the high responder (carried from D5) and the SAE volunteer.
# D7 only needs the two volunteers whose symptoms it will engineer:
#   high responder (mild insomnia and fatigue)
#   SAE volunteer (escalating GI symptoms Day 3, recovery by Day 7)

high_responder_id = None
sae_volunteer_id = None

# Read D5 cast to identify the high responder
with open("d5_cast_assignments.csv", mode="r", newline="", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        if row["role"] == "high_responder":
            high_responder_id = row["record_id"]

# Read D6 cast to identify the SAE volunteer
with open("d6_cast_assignments.csv", mode="r", newline="", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        if row["role"] == "sae_volunteer":
            sae_volunteer_id = row["record_id"]

# Verification print
print(f"\nD7 narrative role assignments (inherited from upstream):")
print(f"  High responder (from D5): {high_responder_id}")
print(f"  SAE volunteer (from D6):  {sae_volunteer_id}")
# ==========================================
# SECTION 5: BUILD MAKE_D7_RECORD FUNCTION
# ==========================================

def generate_symptom_rating(cohort, is_common):
    """
    Draw one symptom rating (0-3) based on cohort-scaled probabilities.
    is_common -- True for common symptoms (insomnia, fatigue, appetite)
                 False for uncommon symptoms (headache, nausea, mood, gi)
    """
    if is_common:
        rates = COMMON_SYMPTOM_RATES[cohort]
    else:
        rates = UNCOMMON_SYMPTOM_RATES[cohort]
    return random.choices([0, 1, 2, 3], weights=rates, k=1)[0]


def make_d7_record(volunteer, event):
    """
    Build one D7 record for one volunteer at one event.
    
    volunteer -- D3a record dict (Randomised only)
    event     -- one entry from D7_EVENTS list
    
    Returns a fully populated D7 record dict.
    """
    
    # ---------- Pull upstream values ----------
    record_id = volunteer["record_id"]
    cohort = volunteer["cohort"]
    cohort_open_date = volunteer["cohort_open_date"]
    diary_day = event["diary_day"]
    
    # Determine narrative role for this volunteer
    if record_id == high_responder_id:
        role = "high_responder"
    elif record_id == sae_volunteer_id:
        role = "sae_volunteer"
    else:
        role = None
    
    # ---------- Compute diary date ----------
    open_dt = datetime.strptime(cohort_open_date, "%Y-%m-%d")
    diary_dt = open_dt + timedelta(days=event["day_offset"])
    
    # ---------- Initialise record from template ----------
    record = dict(d7_template)
    record["record_id"] = record_id
    record["redcap_event_name"] = event["name"]
    record["diary_date"] = diary_dt.strftime("%Y-%m-%d")
    record["diary_day"] = diary_day
    
    # ---------- Generate symptom ratings ----------
    # Common symptoms (insomnia, fatigue, appetite)
    record["sym_insomnia"] = generate_symptom_rating(cohort, is_common=True)
    record["sym_fatigue"] = generate_symptom_rating(cohort, is_common=True)
    record["sym_appetite"] = generate_symptom_rating(cohort, is_common=True)
    
    # Uncommon symptoms (headache, nausea, mood, gi)
    record["sym_headache"] = generate_symptom_rating(cohort, is_common=False)
    record["sym_nausea"] = generate_symptom_rating(cohort, is_common=False)
    record["sym_mood"] = generate_symptom_rating(cohort, is_common=False)
    record["sym_gi"] = generate_symptom_rating(cohort, is_common=False)
    
    # ---------- Apply narrative overrides ----------
    # High responder: moderate insomnia on Day 1, boosted fatigue across the trial
    if role == "high_responder":
        if diary_day == 1:
            record["sym_insomnia"] = HIGH_RESPONDER_INSOMNIA_DAY1
        # Fatigue boost: add 1 level, capped at 3
        current_fatigue = record["sym_fatigue"]
        record["sym_fatigue"] = min(current_fatigue + HIGH_RESPONDER_FATIGUE_BOOST, 3)
    
    # SAE volunteer: severe GI symptoms on Day 3, recovery by Day 7
    if role == "sae_volunteer":
        if diary_day == 3:
            record["sym_gi"] = SAE_GI_DAY3_RATING
            record["sym_nausea"] = SAE_NAUSEA_DAY3_RATING
            record["sym_fatigue"] = SAE_FATIGUE_DAY3_RATING
        elif diary_day == 7:
            # All symptoms resolved post-recovery
            record["sym_headache"] = SAE_DAY7_RECOVERY_RATING
            record["sym_fatigue"] = SAE_DAY7_RECOVERY_RATING
            record["sym_nausea"] = SAE_DAY7_RECOVERY_RATING
            record["sym_insomnia"] = SAE_DAY7_RECOVERY_RATING
            record["sym_mood"] = SAE_DAY7_RECOVERY_RATING
            record["sym_appetite"] = SAE_DAY7_RECOVERY_RATING
            record["sym_gi"] = SAE_DAY7_RECOVERY_RATING
    
    # ---------- Other symptoms gateway ----------
    # Most volunteers do not have "other" symptoms to report
    has_other = random.choices([0, 1], weights=[95, 5], k=1)[0]
    record["sym_other"] = has_other
    if has_other == 1:
        record["sym_other_details"] = random.choice([
            "Slight chills in the evening",
            "Mild back ache, possibly from lying in bed",
            "Dry skin, more noticeable than usual",
            "Mild metallic taste in mouth"
        ])
    else:
        record["sym_other_details"] = ""
    
    # ---------- Concomitant medications ----------
    # Most volunteers take no concomitant meds. A few take paracetamol for headache.
    took_med = random.choices([0, 1], weights=[85, 15], k=1)[0]
    record["diary_medication"] = took_med
    if took_med == 1:
        # Pick a realistic OTC medication
        if record["sym_headache"] >= 1 or record["sym_fatigue"] >= 2:
            record["diary_med_details"] = "Paracetamol 500mg, taken once or twice for headache/fatigue"
        else:
            record["diary_med_details"] = random.choice([
                "Multivitamin, daily routine",
                "Antacid tablet for mild indigestion",
                "Sleep tea, herbal, evening"
            ])
    else:
        record["diary_med_details"] = ""
    
    # ---------- Diary completion ----------
    # Mostly volunteer completed, occasionally with assistance or site staff
    record["diary_completed_by"] = random.choices([1, 2, 3], weights=[85, 10, 5], k=1)[0]
    
    return record
# ==========================================
# SECTION 6: NESTED LOOP GENERATING ALL D7 RECORDS
# ==========================================

# Each volunteer gets one D7 record per D7-mapped event.
# 18 Randomised volunteers x 4 events = 72 records total.

all_d7_records = []

for volunteer in randomised_volunteers:
    repeat_instance = 0
    for event in D7_EVENTS:
        repeat_instance = repeat_instance + 1
        d7_record = make_d7_record(volunteer, event)
        d7_record["redcap_repeat_instance"] = repeat_instance
        all_d7_records.append(d7_record)

print(f"\nD7 records generated: {len(all_d7_records)}")
# ==========================================
# SECTION 7: VERIFICATION AND CSV EXPORT
# ==========================================

# Verify total coverage
print(f"\nAll volunteers covered: {len(set(r['record_id'] for r in all_d7_records))} (expected 18)")
print(f"Records per volunteer: {len(all_d7_records) // 18} (expected 4)")

# Verify engineered narratives
print(f"\nEngineered narrative verification:")

# High responder Day 1 insomnia check
hr_day1 = [r for r in all_d7_records 
           if r["record_id"] == high_responder_id and r["diary_day"] == 1]
if hr_day1:
    r = hr_day1[0]
    print(f"  High responder Day 1 insomnia: {r['sym_insomnia']} (expected 2 Moderate)")
    print(f"  High responder Day 1 fatigue:  {r['sym_fatigue']} (boosted)")

# SAE volunteer Day 3 GI symptoms
sae_day3 = [r for r in all_d7_records 
            if r["record_id"] == sae_volunteer_id and r["diary_day"] == 3]
if sae_day3:
    r = sae_day3[0]
    print(f"  SAE volunteer Day 3 GI:        {r['sym_gi']} (expected 3 Severe)")
    print(f"  SAE volunteer Day 3 nausea:    {r['sym_nausea']} (expected 3 Severe)")
    print(f"  SAE volunteer Day 3 fatigue:   {r['sym_fatigue']} (expected 2 Moderate)")

# SAE volunteer Day 7 recovery
sae_day7 = [r for r in all_d7_records 
            if r["record_id"] == sae_volunteer_id and r["diary_day"] == 7]
if sae_day7:
    r = sae_day7[0]
    all_zero = all(r[f"sym_{s}"] == 0 for s in 
                   ["headache", "fatigue", "nausea", "insomnia", "mood", "appetite", "gi"])
    print(f"  SAE volunteer Day 7 all symptoms None: {all_zero} (expected True)")

# Cohort-level symptom density check
print(f"\nCohort symptom density (mean total severity per record across all 7 symptoms):")
cohort_lookup = {v["record_id"]: v["cohort"] for v in randomised_volunteers}
for cohort_code in ["1", "2", "3"]:
    cohort_records = [r for r in all_d7_records 
                      if cohort_lookup[r["record_id"]] == cohort_code]
    total_severity = 0
    for r in cohort_records:
        for sym in ["headache", "fatigue", "nausea", "insomnia", "mood", "appetite", "gi"]:
            total_severity = total_severity + r[f"sym_{sym}"]
    mean_severity = total_severity / len(cohort_records) if cohort_records else 0
    label = {"1": "2mg", "2": "4mg", "3": "8mg"}[cohort_code]
    print(f"  {label} cohort: mean total severity per record = {mean_severity:.2f}")

# Severe rating distribution check
severe_count = sum(1 for r in all_d7_records 
                   for sym in ["headache", "fatigue", "nausea", "insomnia", "mood", "appetite", "gi"]
                   if r[f"sym_{sym}"] == 3)
print(f"\nTotal Severe (3) ratings across all records: {severe_count}")
print(f"  (Expected concentrated around SAE volunteer Day 3)")

# Export to CSV
with open("d7_volunteer_symptom_diary.csv", mode="w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=list(d7_template.keys()))
    writer.writeheader()
    writer.writerows(all_d7_records)

# Write D7 cast assignments file for downstream scripts (D3b)
with open("d7_cast_assignments.csv", mode="w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["record_id", "role"])
    writer.writerow([high_responder_id, "high_responder"])
    writer.writerow([sae_volunteer_id, "sae_volunteer"])

print(f"\nD7 records saved to d7_volunteer_symptom_diary.csv")
print(f"D7 cast assignments saved to d7_cast_assignments.csv")