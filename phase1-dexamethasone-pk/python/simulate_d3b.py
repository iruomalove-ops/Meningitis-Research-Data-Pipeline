"""
simulate_d3b.py
Generates simulated Phase 1 Safety Review and SRC Escalation records (D3b).
Day 21 cohort-level SRC review. Reads d3a_dose_assignment.csv for the 18
Randomised volunteers, plus d5_cast_assignments.csv, d6_cast_assignments.csv,
and d7_cast_assignments.csv to inherit the engineered narrative cast.
Reserves do not get a D3b record because they were never dosed.
The SRC rationale is cohort-specific and references the actual findings the
SRC would have reviewed from D4 PK, D5 labs, D6 AEs, and D7 diary data.
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


# Cohort-specific SRC rationale templates.
# 2mg and 4mg cohorts are clean. 8mg cohort references both engineered findings.

RATIONALE_2MG = (
    "SRC reviewed cumulative safety data for the 2mg cohort. No DLTs observed. "
    "PK exposure within predicted range based on the one-compartment IV model. "
    "Minor transient AEs reported (headache, mild insomnia, mild fatigue) "
    "consistent with single-dose corticosteroid exposure and within expected "
    "Phase 1 background rates. No clinically significant lab abnormalities. "
    "Volunteer-reported symptoms in diary consistent with mild well-tolerated "
    "drug profile. SRC approves escalation to the 4mg dose level."
)

RATIONALE_4MG = (
    "SRC reviewed cumulative safety data for the 4mg cohort. No DLTs observed. "
    "PK exposure scaled proportionally from the 2mg cohort consistent with "
    "linear pharmacokinetics. Mild transient post-dose effects observed in "
    "haematology (modest neutrophil elevation, mild lymphopenia) and a small "
    "transient glucose rise, all within reference ranges and resolving by Day 7. "
    "AE profile remains favourable with mild headache, insomnia, and fatigue "
    "the most commonly reported. SRC approves escalation to the 8mg dose level."
)

# 8mg cohort rationale will be assembled dynamically because it has to reference
# both the high responder by record_id and the unrelated SAE by record_id. We
# build it inside the function once we know the specific volunteer IDs.


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
# SECTION 3: LOAD CAST ASSIGNMENTS
# ==========================================

# D3b inherits the engineered narrative cast from upstream instruments.
# Same disk-based cast pattern used throughout the pipeline.

high_responder_id = None
sae_volunteer_id = None

with open("d5_cast_assignments.csv", mode="r", newline="", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        if row["role"] == "high_responder":
            high_responder_id = row["record_id"]

with open("d6_cast_assignments.csv", mode="r", newline="", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        if row["role"] == "sae_volunteer":
            sae_volunteer_id = row["record_id"]

print(f"\nD3b narrative cast loaded:")
print(f"  High responder: {high_responder_id}")
print(f"  SAE volunteer:  {sae_volunteer_id}")


def build_rationale_8mg():
    """
    Construct the 8mg cohort SRC rationale. References both engineered findings
    by specific record_id so a reviewer reading the data sees the SRC explicitly
    adjudicating each finding.
    """
    return (
        f"SRC reviewed cumulative safety data for the 8mg cohort. No DLTs observed. "
        f"PK exposure scaled proportionally from the lower cohorts confirming linear "
        f"pharmacokinetics across the dose range. Most prominent transient post-dose "
        f"effects observed at this dose level: neutrophilia approximately 1.8x baseline, "
        f"lymphopenia approximately 0.65x baseline, transient glucose elevation, and "
        f"mild hypokalaemia. All effects resolved or trending to resolution by Day 7. "
        f"TWO ITEMS REQUIRED SRC ADJUDICATION. First, volunteer {high_responder_id} "
        f"(sentinel) presented at Day 7 follow-up with mild ALT elevation in the "
        f"80-100 U/L range meeting CTCAE Grade 1 criteria. This volunteer also showed "
        f"above-cohort response at T+48h across glucose, neutrophilia, and potassium. "
        f"SRC assessed the finding as probably related to study drug, below DLT "
        f"threshold (Grade 1 not Grade 3+), and consistent with a strong individual "
        f"response. Repeat LFTs scheduled to confirm trend to resolution. Second, "
        f"volunteer {sae_volunteer_id} experienced acute gastroenteritis requiring "
        f"overnight hospitalisation between Day 3 and Day 5. Meets SAE criterion of "
        f"hospitalisation. SRC adjudicated as unrelated to study drug given the "
        f"clinical picture (vomiting and diarrhoea consistent with viral or food-borne "
        f"aetiology), the timing relative to dosing, and the absence of plausible "
        f"mechanism for single-dose corticosteroid. Sponsor and ethics notified within "
        f"ICH reporting timelines. Both events were reviewed and do not constitute a "
        f"stop signal for the dose escalation programme. SRC approves continued "
        f"monitoring per protocol with cautionary note regarding the ALT signal for "
        f"any future trials extending the dose range or duration."
    )


# ==========================================
# SECTION 4: BUILD MAKE_D3B_RECORD FUNCTION
# ==========================================

def make_d3b_record(d3a_record):
    
    record_id = d3a_record["record_id"]
    cohort = d3a_record["cohort"]
    
    # ---------- Sentinel-specific fields ----------
    if d3a_record["is_sentinel"] == "1":
        sentinel_48h_pass = 1
        open_dt = datetime.strptime(d3a_record["cohort_open_date"], "%Y-%m-%d")
        sentinel_review_date = (open_dt + timedelta(days=2)).strftime("%Y-%m-%d")
    else:
        sentinel_48h_pass = ""
        sentinel_review_date = ""
    
    # ---------- DLT observation ----------
    # No volunteer in the engineered narrative has a true Grade 3+ DLT.
    # The high responder's ALT is Grade 1 (below DLT threshold).
    # The SAE is unrelated to study drug so not a DLT by definition.
    # All volunteers therefore have dlt_observed = 0.
    dlt_observed = 0
    dlt_description = ""
    
    # ---------- SRC meeting date ----------
    open_dt = datetime.strptime(d3a_record["cohort_open_date"], "%Y-%m-%d")
    src_meeting_date = (open_dt + timedelta(days=21)).strftime("%Y-%m-%d")
    
    # ---------- SRC decision and rationale (cohort-driven) ----------
    src_decision = 1  # All cohorts escalate per protocol
    src_signed = 1
    
    if cohort == "1":
        src_rationale = RATIONALE_2MG
    elif cohort == "2":
        src_rationale = RATIONALE_4MG
    elif cohort == "3":
        src_rationale = build_rationale_8mg()
    else:
        src_rationale = "Cohort not recognised."
    
    # ---------- Protocol deviations - 10% rate ----------
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
    
    pi_escalation_signoff = random.choice(["NMC", "TLO", "SJM"])
    
    return {
        "record_id": record_id,
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
# SECTION 5: LOOP THROUGH RANDOMISED VOLUNTEERS
# ==========================================

all_d3b_records = []

for d3a_record in randomised_volunteers:
    d3b_record = make_d3b_record(d3a_record)
    all_d3b_records.append(d3b_record)


# ==========================================
# SECTION 6: VERIFICATION PRINTS
# ==========================================

print(f"\nD3b records generated:")
print(f"  Total: {len(all_d3b_records)}")

# Sentinel reviews
sentinel_records = sum(1 for r in all_d3b_records if r["sentinel_48h_pass"] != "")
print(f"  Sentinel reviews completed: {sentinel_records} (expected 6)")

# Cohort rationale verification
cohort_lookup = {v["record_id"]: v["cohort"] for v in randomised_volunteers}
for cohort_code in ["1", "2", "3"]:
    cohort_records = [r for r in all_d3b_records 
                      if cohort_lookup[r["record_id"]] == cohort_code]
    if cohort_records:
        sample_rationale = cohort_records[0]["src_rationale"]
        label = {"1": "2mg", "2": "4mg", "3": "8mg"}[cohort_code]
        print(f"  Cohort {label} records: {len(cohort_records)}, rationale length: {len(sample_rationale)} chars")

# Verify 8mg rationale references both narrative volunteers
cohort_3_records = [r for r in all_d3b_records 
                    if cohort_lookup[r["record_id"]] == "3"]
if cohort_3_records:
    rationale = cohort_3_records[0]["src_rationale"]
    hr_referenced = high_responder_id in rationale
    sae_referenced = sae_volunteer_id in rationale
    print(f"\n  8mg rationale references high responder ID: {hr_referenced}")
    print(f"  8mg rationale references SAE volunteer ID:  {sae_referenced}")

deviation_count = sum(1 for r in all_d3b_records if r["deviation_any"] == 1)
print(f"\n  Protocol deviations: {deviation_count}")


# ==========================================
# SECTION 7: EXPORT TO CSV
# ==========================================

with open("d3b_safety_review.csv", mode="w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=list(d3b_template.keys()))
    writer.writeheader()
    writer.writerows(all_d3b_records)

print(f"\nD3b records saved to d3b_safety_review.csv")