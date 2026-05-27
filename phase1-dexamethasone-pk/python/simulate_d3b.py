"""
simulate_d3b.py
Generates simulated Phase 1 Safety Review and SRC Escalation records (D3b).
Day 2 through Day 21 instrument capturing sentinel review DLT observations
SRC escalation decisions and protocol deviations.
Reads d3a_dose_assignment.csv and filters to Randomised volunteers only.
Reserves do not get a D3b record because they were never dosed.
"""

import random
import csv
from datetime import datetime, timedelta

# ==========================================
# SECTION 1: CONFIGURATIONS & TEMPLATE
# ==========================================

# D3b schema template - 14 safety and escalation fields
d3b_template = {
    "record_id": "",
    "sentinel_48h_pass": "",
    "sentinel_review_date": "",
    "dlt_observed": "",
    "dlt_description": "",
    "src_meeting_date": "",
    "src_decision": "",
    "src_rationale": "",
    "src_signed": "",
    "deviation_any": "",
    "deviation_details": "",
    "deviation_reported": "",
    "deviation_ethics": "",
    "pi_escalation_signoff": ""
}


# ==========================================
# SECTION 2: LOAD D3A AND FILTER TO RANDOMISED
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
# SECTION 3: BUILD MAKE_D3B_RECORD FUNCTION
# ==========================================

def make_d3b_record(d3a_record):
    
    # Sentinel-specific fields - only if is_sentinel is "1" in D3a CSV (strings)
    if d3a_record["is_sentinel"] == "1":
        sentinel_48h_pass = 1
        # Review date is 2 days after cohort_open_date
        open_dt = datetime.strptime(d3a_record["cohort_open_date"], "%Y-%m-%d")
        sentinel_review_date = (open_dt + timedelta(days=2)).strftime("%Y-%m-%d")
    else:
        sentinel_48h_pass = ""
        sentinel_review_date = ""
    
    # DLT observation - 5% rate
    dlt_observed = random.choices([1, 0], weights=[5, 95], k=1)[0]
    if dlt_observed == 1:
        dlt_description = random.choice([
            "CTCAE Grade 3 nausea persisting beyond 48 hours, related to study drug, antiemetic given",
            "CTCAE Grade 3 fatigue, related to study drug, supportive care provided",
            "CTCAE Grade 3 headache, related to study drug, analgesics administered"
        ])
    else:
        dlt_description = ""
    
    # SRC meeting date - 3 weeks after cohort opens
    open_dt = datetime.strptime(d3a_record["cohort_open_date"], "%Y-%m-%d")
    src_meeting_date = (open_dt + timedelta(days=21)).strftime("%Y-%m-%d")
    
    # SRC decision - based on DLT outcome
    if dlt_observed == 1:
        src_decision = 2  # Repeat current dose
        src_rationale = "DLT observed in this volunteer. SRC recommends repeating current dose with additional safety monitoring before escalation to next cohort."
    else:
        src_decision = 1  # Escalate
        src_rationale = "No DLTs observed. PK profile within expected range. SRC approves escalation to next dose level."
    
    src_signed = 1
    
    # Protocol deviations - 10% rate
    deviation_any = random.choices([1, 0], weights=[10, 90], k=1)[0]
    if deviation_any == 1:
        deviation_details = random.choice([
            "PK sample collected 15 minutes outside protocol window at T+4h timepoint",
            "Vital signs check missed at T+1h timepoint, captured at T+1h15min instead",
            "Volunteer ate light meal 30 minutes before scheduled fasting period ended"
        ])
        deviation_reported = 1
        deviation_ethics = 1
    else:
        deviation_details = ""
        deviation_reported = ""
        deviation_ethics = ""
    
    # Investigator escalation sign-off
    pi_escalation_signoff = random.choice(["NMC", "TLO", "SJM"])
    
    # Build the complete D3b record
    return {
        "record_id": d3a_record["record_id"],
        "sentinel_48h_pass": sentinel_48h_pass,
        "sentinel_review_date": sentinel_review_date,
        "dlt_observed": dlt_observed,
        "dlt_description": dlt_description,
        "src_meeting_date": src_meeting_date,
        "src_decision": src_decision,
        "src_rationale": src_rationale,
        "src_signed": src_signed,
        "deviation_any": deviation_any,
        "deviation_details": deviation_details,
        "deviation_reported": deviation_reported,
        "deviation_ethics": deviation_ethics,
        "pi_escalation_signoff": pi_escalation_signoff
    }
# ==========================================
# SECTION 4: LOOP THROUGH RANDOMISED VOLUNTEERS
# ==========================================

all_d3b_records = []

for d3a_record in randomised_volunteers:
    d3b_record = make_d3b_record(d3a_record)
    all_d3b_records.append(d3b_record)


# ==========================================
# SECTION 5: VERIFICATION PRINTS
# ==========================================

print(f"\nD3b records generated:")
print(f"  Total: {len(all_d3b_records)}")

dlt_count = sum(1 for r in all_d3b_records if r["dlt_observed"] == 1)
print(f"  DLT observed: {dlt_count}")

deviation_count = sum(1 for r in all_d3b_records if r["deviation_any"] == 1)
print(f"  Protocol deviations: {deviation_count}")

sentinel_records = sum(1 for r in all_d3b_records if r["sentinel_48h_pass"] != "")
print(f"  Sentinel reviews completed: {sentinel_records}")

escalation_count = sum(1 for r in all_d3b_records if r["src_decision"] == 1)
repeat_count = sum(1 for r in all_d3b_records if r["src_decision"] == 2)
print(f"  SRC escalate decisions: {escalation_count}")
print(f"  SRC repeat dose decisions: {repeat_count}")


# ==========================================
# SECTION 6: EXPORT TO CSV
# ==========================================

with open("d3b_safety_review.csv", mode="w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=list(d3b_template.keys()))
    writer.writeheader()
    writer.writerows(all_d3b_records)

print(f"\nD3b records saved to d3b_safety_review.csv")