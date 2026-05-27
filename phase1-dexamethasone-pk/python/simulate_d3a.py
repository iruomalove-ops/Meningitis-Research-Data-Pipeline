"""
simulate_d3a.py
Generates simulated Phase 1 Dose Assignment records (D3a).
Day 0 instrument capturing cohort assignment and dosing details for all eligible volunteers.
Reserves receive a record but with empty cohort fields.
Safety review and SRC escalation captured separately in simulate_d3b.py.
"""

import random
import csv
from datetime import datetime, timedelta
# Lock random seed for reproducible data
random.seed(42)


# ==========================================
# SECTION 1: CONFIGURATIONS & TEMPLATE
# ==========================================

# Cohort specifications - one source of truth for dose and batch info
COHORT_SPECS = {
    1: {"name": "Cohort A - Low dose", "dose_mg": 2.0, "batch": "DEX-P1-2MG-L01"},
    2: {"name": "Cohort B - Mid dose", "dose_mg": 4.0, "batch": "DEX-P1-4MG-L01"},
    3: {"name": "Cohort C - High dose", "dose_mg": 8.0, "batch": "DEX-P1-8MG-L01"}
}

# Cohort opening dates - one source of truth for trial timeline
COHORT_DATES = {
    1: "2025-05-19",
    2: "2025-06-09",
    3: "2025-06-30"
}

# D3 schema template - all 22 D3 fields plus record_id and enrolment_status
# D3a schema template - Dose Assignment fields only
d3a_template = {
    "record_id": "",
    "enrolment_status": "",
    "cohort": "",
    "cohort_position": "",
    "is_sentinel": "",
    "cohort_open_date": "",
    "planned_dose_mg": 0.0,
    "dose_per_kg": 0.0,
    "imp_batch": "",
    "imp_expiry": "2028-05-01",
    "pi_dosing_signoff": ""
}
# ==========================================
# SECTION 2: LOAD D2 DATA AND STRATIFY
# ==========================================

# Three empty piles for stratified randomisation
strata_1_excellent = []
strata_2_standard = []
strata_3_history = []

print("Loading D2 data and stratifying volunteers...")

with open("d2_demographics_medical_history.csv", mode="r", newline="", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    
    for row in reader:
        assessment = row["pi_assessment"]
        has_family_history = row["family_history"] == "1"
        
        if assessment == "Excellent health":
            strata_1_excellent.append(row)
        elif has_family_history:
            strata_3_history.append(row)
        else:
            strata_2_standard.append(row)

print(f"Stratification complete:")
print(f"  Strata 1 (Excellent): {len(strata_1_excellent)} volunteers")
print(f"  Strata 2 (Standard): {len(strata_2_standard)} volunteers")
print(f"  Strata 3 (Family history): {len(strata_3_history)} volunteers")
print(f"  Total: {len(strata_1_excellent) + len(strata_2_standard) + len(strata_3_history)}")
# ==========================================
# SECTION 3: RESERVE WITHDRAWAL  [DISABLED]
# ==========================================
# 
# Original design pulled 2 reserves from the Family History pile upfront
# because that pile was overrepresented (11 family history vs 6 standard
# in the original 20-volunteer scenario).
# 
# This logic was disabled after the random seed was set and D2 now produces
# 28 eligible volunteers with a different stratum distribution:
#   Strata 1 (Excellent): 3
#   Strata 2 (Standard): 16
#   Strata 3 (Family history): 9
# 
# With 9 Family History exactly matching the 9 needed for randomisation
# (3 per cohort), pulling reserves from Family History would leave a
# shortage. Reserves now emerge naturally as leftover volunteers from
# whichever stratum is overrepresented (currently Standard with 10 leftover).
# 
# Kept here as design history. Section 6 handles reserves dynamically.
#
# reserves = random.sample(strata_3_history, 2)
# for reserve in reserves:
#     strata_3_history.remove(reserve)
# 
# print(f"\nReserve withdrawal complete:")
# print(f"  Reserves pulled: {len(reserves)} volunteers")
# print(f"  Strata 3 (Family history) now has: {len(strata_3_history)} volunteers")
# print(f"  Available for randomisation: {len(strata_1_excellent) + len(strata_2_standard) + len(strata_3_history)}")
# ==========================================
# SECTION 4: SHUFFLE EACH STRATUM
# ==========================================

# Shuffle each pile so volunteers within a stratum are in random order
random.shuffle(strata_1_excellent)
random.shuffle(strata_2_standard)
random.shuffle(strata_3_history)

print(f"\nStrata shuffled. Ready for block randomisation.")
# ==========================================
# SECTION 5: BLOCK RANDOMISATION
# ==========================================

# Each cohort gets 1 Excellent + 2 Standard + 3 Family History = 6 volunteers
# Position 1 = Sentinel 1 (the Excellent volunteer)
# Position 2 = Sentinel 2 (one of the Standard volunteers)
# Positions 3-6 = remaining Standard + 3 Family History (random order)

assignments = []

for cohort_num in [1, 2, 3]:
    
    cohort_volunteers = []
    
    # Position 1 - Sentinel 1 (Excellent)
    cohort_volunteers.append(strata_1_excellent.pop(0))
    
    # Position 2 - Sentinel 2 (Standard)
    cohort_volunteers.append(strata_2_standard.pop(0))
    
    # Positions 3 to 6 - collect 1 more Standard + 3 Family History then shuffle
    remaining = []
    remaining.append(strata_2_standard.pop(0))
    remaining.append(strata_3_history.pop(0))
    remaining.append(strata_3_history.pop(0))
    remaining.append(strata_3_history.pop(0))
    random.shuffle(remaining)
    
    cohort_volunteers.extend(remaining)
    
    # Build assignment dictionary for each cohort member
    for position, volunteer in enumerate(cohort_volunteers, start=1):
        assignment = {
            "record_id": volunteer["record_id"],
            "cohort": cohort_num,
            "cohort_position": position,
            "is_sentinel": 1 if position <= 2 else 0,
            "enrolment_status": "Randomised"
        }
        assignments.append(assignment)


# Verification - print cohort summary
print(f"\nBlock randomisation complete:")
print(f"  Total assignments: {len(assignments)}")
for cohort_num in [1, 2, 3]:
    cohort_count = sum(1 for a in assignments if a["cohort"] == cohort_num)
    sentinel_count = sum(1 for a in assignments if a["cohort"] == cohort_num and a["is_sentinel"] == 1)
    print(f"  Cohort {cohort_num}: {cohort_count} volunteers ({sentinel_count} sentinels)")
print(f"\nReserves remaining in strata:")
print(f"  Strata 1 (Excellent): {len(strata_1_excellent)} leftover")
print(f"  Strata 2 (Standard): {len(strata_2_standard)} leftover")
print(f"  Strata 3 (Family history): {len(strata_3_history)} leftover")
# ==========================================
# SECTION 6: ADD RESERVES AS RECORDS
# ==========================================

# Collect all leftover volunteers from any stratum
reserves = []
reserves.extend(strata_1_excellent)
reserves.extend(strata_2_standard)
reserves.extend(strata_3_history)

# Build a D3 assignment record for each reserve
for volunteer in reserves:
    assignment = {
        "record_id": volunteer["record_id"],
        "cohort": "",
        "cohort_position": "",
        "is_sentinel": 0,
        "enrolment_status": "Reserve"
    }
    assignments.append(assignment)

# Verification
print(f"\nReserve records added:")
print(f"  Total reserves: {len(reserves)}")
print(f"  Total assignments now: {len(assignments)}")
randomised_count = sum(1 for a in assignments if a["enrolment_status"] == "Randomised")
reserve_count = sum(1 for a in assignments if a["enrolment_status"] == "Reserve")
print(f"  Randomised: {randomised_count}")
print(f"  Reserve: {reserve_count}")
# ==========================================
# LOAD D1 WEIGHTS FOR DOSE CALCULATIONS
# ==========================================

# Build a lookup dictionary: record_id -> weight_kg
d1_weights = {}

with open("d1_eligibility.csv", mode="r", newline="", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        d1_weights[row["record_id"]] = float(row["weight_kg"])

print(f"\nD1 weight lookup loaded: {len(d1_weights)} records")
def make_d3a_record(assignment):
    
    # Handle Reserve volunteers - mostly empty record
    if assignment["enrolment_status"] == "Reserve":
        return {
            "record_id": assignment["record_id"],
            "enrolment_status": "Reserve",
            "cohort": "",
            "cohort_position": "",
            "is_sentinel": 0,
            "cohort_open_date": "",
            "planned_dose_mg": "",
            "dose_per_kg": "",
            "imp_batch": "",
            "imp_expiry": "",
            "pi_dosing_signoff": ""
        }
    
    # Below this line - Randomised volunteers only
    
    # Pull cohort metadata from COHORT_SPECS
    cohort_num = assignment["cohort"]
    cohort_spec = COHORT_SPECS[cohort_num]
    cohort_open_date = COHORT_DATES[cohort_num]
    
    # Pull weight from D1 lookup, calculate dose per kg
    weight_kg = d1_weights[assignment["record_id"]]
    planned_dose_mg = cohort_spec["dose_mg"]
    dose_per_kg = round(planned_dose_mg / weight_kg, 4)
    
    # PI dosing sign-off
    pi_dosing_signoff = random.choice(["NMC", "TLO", "SJM"])
    
    # Build the complete D3a record
    return {
        "record_id": assignment["record_id"],
        "enrolment_status": assignment["enrolment_status"],
        "cohort": cohort_num,
        "cohort_position": assignment["cohort_position"],
        "is_sentinel": assignment["is_sentinel"],
        "cohort_open_date": cohort_open_date,
        "planned_dose_mg": planned_dose_mg,
        "dose_per_kg": dose_per_kg,
        "imp_batch": cohort_spec["batch"],
        "imp_expiry": "2028-05-01",
        "pi_dosing_signoff": pi_dosing_signoff
    }
# Quick test - build one Randomised record and one Reserve record
print(f"\n--- Testing make_d3a_record ---")
print(f"\nRandomised test:")
test_randomised = make_d3a_record(assignments[0])
for key, value in test_randomised.items():
    print(f"  {key}: {value}")

print(f"\nReserve test:")
for a in assignments:
    if a["enrolment_status"] == "Reserve":
        test_reserve = make_d3a_record(a)
        for key, value in test_reserve.items():
            print(f"  {key}: {value}")
        break
# ==========================================
# SECTION 8: LOOP THROUGH ASSIGNMENTS
# ==========================================

all_d3a_records = []

for assignment in assignments:
    d3a_record = make_d3a_record(assignment)
    all_d3a_records.append(d3a_record)

# Verification
print(f"\nD3a records generated:")
print(f"  Total: {len(all_d3a_records)}")
randomised_count = sum(1 for r in all_d3a_records if r["enrolment_status"] == "Randomised")
reserve_count = sum(1 for r in all_d3a_records if r["enrolment_status"] == "Reserve")
print(f"  Randomised: {randomised_count}")
print(f"  Reserve: {reserve_count}")
# ==========================================
# SECTION 9: EXPORT TO CSV
# ==========================================

with open("d3a_dose_assignment.csv", mode="w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=list(d3a_template.keys()))
    writer.writeheader()
    writer.writerows(all_d3a_records)

print(f"\nD3a records saved to d3a_dose_assignment.csv")