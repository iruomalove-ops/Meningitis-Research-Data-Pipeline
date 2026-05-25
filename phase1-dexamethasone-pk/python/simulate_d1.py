"""simulate_d1.py
Generates simulated Phase 1 trial data with realistic enrolment funnel.
100 screened, 80 screen failures, 20 eligible, 18 complete.
"""

import random
import csv
from datetime import datetime, timedelta
#The D1 schema/template defines the structure of one volunteer's data record, with all fields initialized to empty strings or zero values.
d1_template = {
    "record_id": "",
    "screening_date": "",
    "screened_by": "",
    "dob": "",
    "age_years": 0,
    "sex_at_birth": 0,
    "weight_kg": 0.0,
    "height_cm": 0.0,
    "bmi": 0.0,
    "i1_age": 0,
    "i2_bmi": 0,
    "i3_health": 0,
    "i6_comply": 0,
    "i7_consent": 0,
    "e1_cyp3a4": 0,
    "e2_meds": 0,
    "e3_diabetes": 0,
    "e4_immune": 0,
    "e5_pregnancy": 0,
    "e6_allergy": 0,
    "e7_smoking": 0,
    "e8_alcohol": 0,
    "e9_previoustrial": 0,
    "eligibility_determination": 0,
    "screen_failure_reason": 0,
    "screen_failure_narrative": "",
}  
#site information
def make_d1_record(volunteer_number):
    record_id =f"ZA-CPT-P1-{volunteer_number:03d}"  # ZA-CPT-P1-001, ZA-CPT-002, etc.
    screening_date = datetime(2025,5,1) 
    screened_by = random.choice(["NMC","TLO","SJM"])
    #demographics 
    dob = screening_date - timedelta(days=random.randint(18*365, 65*365))
    age_years = (screening_date -dob).days // 365
    sex_at_birth = random.choices([1,2,3], weights=[49,49,2], k=1)[0]  #1=male, 2=female, 3=intersex
    #weight and height 
    if sex_at_birth == 1:  #male
        weight_kg = round(random.gauss(78,8),1)  #mean 78kg, sd 8kg
        height_cm =round(random.gauss(175,7),1)  #mean 175cm, sd 7cm
    else:  #female or intersex
        weight_kg = round(random.gauss(65,7),1)  #mean 65kg, sd 7kg
        height_cm = round(random.gauss(162,6),1)  #mean 162cm, sd 6cm
    bmi = round(weight_kg / (height_cm/100)**2,1) #BMI calculation
    #inclusion criteria
    #i1_age
    if age_years >=18 and age_years <=65:
        i1_age =1
    else:
        i1_age =0
    #i2_bmi
    if bmi >=18.5 and bmi <=30:
        i2_bmi =1   
    else:
        i2_bmi =0
    #i3_health
    i3_health = random.choices([1,0], weights=[90,10], k=1)[0]  #90% healthy, 10% unhealthy
    # Inclusion criteria — I4 (normal hepatic) and I5 (normal renal) intentionally removed
    # during design. Covered by I3 (good general health). Numbering gaps preserved for protocol history.
    #i6_comply
    i6_comply = random.choices([1,0], weights = [95,5], k=1)[0]  #95% likely to comply, 5% not
    #i7_consent
    i7_consent = 1  #all volunteers consent
    #exclusion criteria
    e1_cyp3a4 = random.choices([1,0], weights=[5,95], k=1)[0]  #90% normal CYP3A4, 10% poor metabolizer
    e2_meds = random.choices([1,0], weights =[15,85], k=1)[0]  #85% no interacting meds, 15% on interacting meds
    e3_diabetes = random.choices([1,0], weights=[3,97], k=1)[0]  #97% no diabetes, 3% with diabetes
    e4_immune = random.choices([1,0], weights=[2,98], k=1)[0]  #98% no immune disorder, 2% with immune disorder
    #e5_pregnancy
    if sex_at_birth == 2:
        e5_pregnancy =random.choices([1,0], weights=[8,92], k=1)[0]  #92% not pregnant, 8% pregnant
    else:
        e5_pregnancy = ""   #not applicable
    e6_allergy = random.choices([1,0], weights=[2,98], k=1)[0]  #90% no allergy, 10% with allergy
    e7_smoking = random.choices([1,0], weights=[25,80], k=1)[0]  #75% non-smoker, 25% smoker
    e8_alcohol = random.choices([1,0], weights=[30,70], k=1)[0]  #70% non-drinker, 30% drinker
    e9_previoustrial = random.choices([1,0], weights=[20,80], k=1)[0]  #80% no previous trial, 20% previous trial
    #eligibiity conclusion
    #eligibility_determination
    inclusion_criteria = [i1_age, i2_bmi, i3_health, i6_comply, i7_consent]
    exclusion_criteria = [e1_cyp3a4, e2_meds, e3_diabetes, e4_immune, e6_allergy, e7_smoking, e8_alcohol, e9_previoustrial]
    if all(v == 1 for v in inclusion_criteria) and not any(v == 1 for v in exclusion_criteria):
        eligibility_determination = 1  #eligible
    else:
        eligibility_determination = 2  #ineligible

    #screen ailure reason - derived from which criteria failed 
    if eligibility_determination == 1:
        screen_failure_reason = ""  #not applicable
    elif i1_age == 0:
        screen_failure_reason = 5 #age out of range
    elif i2_bmi == 0:
        screen_failure_reason = 4 #BMI out of range
    elif i3_health == 0:
        screen_failure_reason = 1 #unhealthy
    elif i6_comply == 0:
        screen_failure_reason = 7 #non-compliance risk
    elif e1_cyp3a4 == 1 or e2_meds == 1:
        screen_failure_reason = 2 #drug interaction risk
    else:
        screen_failure_reason = 2 #other exclusion criteria
    #screen_failure_narrative - empty for all because reason codes are self-explanatory 
    screen_failure_narrative = ""
    #assemble D1 record
    return {
        "record_id": record_id,
        "screening_date": screening_date.strftime("%Y-%m-%d"),
        "screened_by": screened_by,
        "dob": dob.strftime("%Y-%m-%d"),
        "age_years": age_years,
        "sex_at_birth": sex_at_birth,
        "weight_kg": weight_kg,
        "height_cm": height_cm,
        "bmi": bmi,
        "i1_age": i1_age,
        "i2_bmi": i2_bmi,
        "i3_health": i3_health,
        "i6_comply": i6_comply,
        "i7_consent": i7_consent,
        "e1_cyp3a4": e1_cyp3a4,
        "e2_meds": e2_meds,
        "e3_diabetes": e3_diabetes,
        "e4_immune": e4_immune,
        "e5_pregnancy": e5_pregnancy,
        "e6_allergy": e6_allergy,
        "e7_smoking": e7_smoking,
        "e8_alcohol": e8_alcohol,
        "e9_previoustrial": e9_previoustrial,
        "eligibility_determination": eligibility_determination,
        "screen_failure_reason": screen_failure_reason,
        "screen_failure_narrative": screen_failure_narrative
    }
#Generate 100 d1 records for volunteers
all_d1_records = []
for volunteer_number in range(1,101):
    record = make_d1_record(volunteer_number)
    all_d1_records.append(record)
#verification
print(f"total records generated: {len(all_d1_records)}")
print(f"first record record_id: {all_d1_records[0]['record_id']}")
print(f"last record record_id: {all_d1_records[99]['record_id']}")
# export to csv
with open("d1_eligibility.csv", mode="w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=list(d1_template.keys()))
    writer.writeheader()
    writer.writerows(all_d1_records)
print("D1 eligibility records saved to d1_eligibility.csv")
