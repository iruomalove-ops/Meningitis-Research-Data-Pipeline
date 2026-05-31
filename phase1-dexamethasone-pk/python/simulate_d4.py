"""
simulate_d4.py
Generates simulated Phase 1 PK sampling records (D4).
Reads d3a_dose_assignment.csv to find the 18 Randomised volunteers
and d1_eligibility.csv for body weights, then generates 8 PK timepoint
records per volunteer using an IV one-compartment pharmacokinetic model.
Outputs 144 records to d4_pk_sampling.csv.
"""
import random
import csv
from datetime import datetime, timedelta
import math
# ==========================================
# SECTION 1: CONFIGURATIONS & TEMPLATE
# ==========================================

# Pharmacokinetic model constants
# IV one-compartment model: C(t) = (D/V) * exp(-ke*t)
HALF_LIFE_HOURS = 4.0          # dexamethasone plasma half-life, StatPearls NIH
KE = 0.693 / HALF_LIFE_HOURS   # elimination rate constant, per hour
V_PER_KG = 1.0                 # volume of distribution, L per kg body weight
LLOQ = 0.5                     # lower limit of quantification, ng/mL
ASSAY_NOISE = 0.05             # plus or minus 5% measurement noise
# D4 schema template - 16 fields plus REDCap structural columns
d4_template = {
    "record_id": "",
    "redcap_repeat_instance": "",
    "timepoint": "",
    "scheduled_datetime": "",
    "actual_datetime": "",
    "sample_collected": "",
    "missed_reason": "",
    "cannula_site": "",
    "sample_volume": "",
    "tube_type": "",
    "centrifuge_time": "",
    "plasma_aliquoted": "",
    "storage_temp": "",
    "shipped": "",
    "plasma_concentration": "",
    "blq": "",
    "assay_date": "",
    "sample_notes": ""
}
# ==========================================
# SECTION 2: TIMEPOINT DEFINITIONS
# ==========================================

# 8 PK timepoints driving the repeating instrument structure.
# Each volunteer gets one record per timepoint.
# Hours measured from time of dosing.
TIMEPOINTS = [
    {"code": 1, "label": "Pre-dose T0",  "hours": 0},
    {"code": 2, "label": "30 minutes",   "hours": 0.5},
    {"code": 3, "label": "1 hour",       "hours": 1},
    {"code": 4, "label": "2 hours",      "hours": 2},
    {"code": 5, "label": "4 hours",      "hours": 4},
    {"code": 6, "label": "8 hours",      "hours": 8},
    {"code": 7, "label": "24 hours",     "hours": 24},
    {"code": 8, "label": "48 hours",     "hours": 48}
]
print(f"Defined {len(TIMEPOINTS)} timepoints")
for tp in TIMEPOINTS:
    print(f"  Code {tp['code']}: {tp['label']} at {tp['hours']}h")
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
# SECTION 4: LOAD D1 WEIGHTS FOR DOSE CALCULATIONS
# ==========================================

d1_weights = {}

with open("d1_eligibility.csv", mode="r", newline="", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        d1_weights[row["record_id"]] = float(row["weight_kg"])

print(f"D1 weight lookup loaded: {len(d1_weights)} records")
# ==========================================
# SECTION 5: BUILD MAKE_D4_RECORD FUNCTION
# ==========================================

def make_d4_record(d3a_record, timepoint):
    """
    Build one D4 PK sampling record for one volunteer at one timepoint.
    Inputs:
        d3a_record -- one row from d3a_dose_assignment.csv (Randomised only)
        timepoint  -- one dictionary from the TIMEPOINTS list
    Returns:
        a dictionary with all D4 fields populated for this volunteer-timepoint pair
    """
    
    # Step 1: pull upstream values
    record_id = d3a_record["record_id"]
    cohort = d3a_record["cohort"]
    planned_dose_mg = float(d3a_record["planned_dose_mg"])
    cohort_open_date = d3a_record["cohort_open_date"]
    weight_kg = d1_weights[record_id]
    hours = timepoint["hours"]
    
    # Step 2: volunteer-specific volume of distribution
    V = V_PER_KG * weight_kg
    
    # Step 3: true plasma concentration from the PK model (ng/mL)
    true_concentration = (planned_dose_mg / V) * math.exp(-KE * hours) * 1000
    
    # Step 4: apply assay measurement noise
    noise_factor = random.uniform(1 - ASSAY_NOISE, 1 + ASSAY_NOISE)
    measured_concentration = true_concentration * noise_factor
    
    # Step 5: T0 is pre-dose, force to zero
    if hours == 0:
        measured_concentration = 0.0
    
    # Step 6: apply BLQ rule
    if measured_concentration < LLOQ:
        blq = 1
        plasma_concentration = LLOQ
    else:
        blq = 0
        plasma_concentration = round(measured_concentration, 2)
    
    # Step 7: compute timing fields
    # Dosing time is randomised per volunteer between 08:00 and 10:00
    dosing_hour = random.randint(8, 9)
    dosing_minute = random.randint(0, 59)
    dosing_time_string = f"{dosing_hour:02d}:{dosing_minute:02d}"
    dosing_datetime = datetime.strptime(cohort_open_date + " " + dosing_time_string, "%Y-%m-%d %H:%M")
    
    scheduled_datetime = dosing_datetime + timedelta(hours=hours)
    actual_drift_minutes = random.randint(-5, 5)
    actual_datetime = scheduled_datetime + timedelta(minutes=actual_drift_minutes)
    centrifuge_delay_minutes = random.randint(15, 25)
    centrifuge_datetime = actual_datetime + timedelta(minutes=centrifuge_delay_minutes)
    
    # Step 8: logistics fields with realistic defaults
    sample_volume = round(random.gauss(4.0, 0.2), 1)
    cannula_site = random.choices([1, 2, 3, 4], weights=[40, 40, 10, 10], k=1)[0]
    
    # Assay date is 7 days after dosing (lab batch processing)
    assay_datetime = dosing_datetime + timedelta(days=7)
    assay_date = assay_datetime.strftime("%Y-%m-%d")
    
    # Step 9: return complete D4 record
    return {
        "record_id": record_id,
        "redcap_repeat_instance": "",  # filled by outer loop in Section 6
        "timepoint": timepoint["code"],
        "scheduled_datetime": scheduled_datetime.strftime("%Y-%m-%d %H:%M"),
        "actual_datetime": actual_datetime.strftime("%Y-%m-%d %H:%M"),
        "sample_collected": 1,
        "missed_reason": "",
        "cannula_site": cannula_site,
        "sample_volume": sample_volume,
        "tube_type": 1,
        "centrifuge_time": centrifuge_datetime.strftime("%Y-%m-%d %H:%M"),
        "plasma_aliquoted": 1,
        "storage_temp": 1,
        "shipped": 1,
        "plasma_concentration": plasma_concentration,
        "blq": blq,
        "assay_date": assay_date,
        "sample_notes": ""
    }
# ==========================================
# SECTION 6: NESTED LOOP GENERATING ALL D4 RECORDS
# ==========================================

# Each volunteer gets 8 PK records (one per timepoint).
# Two distinct counters:
#   - repeat_instance: the sequence position within this volunteer's repeating
#     instrument, used to populate redcap_repeat_instance
#   - timepoint["code"]: the REDCap dropdown code for the type of timepoint
# Currently they happen to be identical 1-8 but they are computed independently
# so that any future change to TIMEPOINTS order or content cannot silently
# couple them.

all_d4_records = []

for volunteer in randomised_volunteers:
    repeat_instance = 0  # reset at the start of each volunteer
    for timepoint in TIMEPOINTS:
        repeat_instance = repeat_instance + 1
        d4_record = make_d4_record(volunteer, timepoint)
        d4_record["redcap_repeat_instance"] = repeat_instance
        all_d4_records.append(d4_record)

print(f"D4 records generated: {len(all_d4_records)}")
# ==========================================
# SECTION 7: VERIFICATION AND CSV EXPORT
# ==========================================

# Verify each volunteer got exactly 8 records
records_per_volunteer = {}
for record in all_d4_records:
    rid = record["record_id"]
    if rid not in records_per_volunteer:
        records_per_volunteer[rid] = 0
    records_per_volunteer[rid] = records_per_volunteer[rid] + 1

all_have_eight = all(count == 8 for count in records_per_volunteer.values())
print(f"All volunteers have 8 records: {all_have_eight}")
print(f"Unique volunteers: {len(records_per_volunteer)}")

# BLQ distribution by timepoint (sanity check on the PK model shape)
print(f"\nBLQ counts by timepoint:")
for tp in TIMEPOINTS:
    blq_count = sum(1 for r in all_d4_records if r["timepoint"] == tp["code"] and r["blq"] == 1)
    total_at_tp = sum(1 for r in all_d4_records if r["timepoint"] == tp["code"])
    print(f"  {tp['label']:14s}: {blq_count}/{total_at_tp} BLQ")

# Export to CSV
with open("d4_pk_sampling.csv", mode="w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=list(d4_template.keys()))
    writer.writeheader()
    writer.writerows(all_d4_records)

print(f"\nD4 records saved to d4_pk_sampling.csv")