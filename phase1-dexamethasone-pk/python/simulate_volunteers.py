"""simulate_volunteers.py
generates 16 simulated healthy volunteers for the phase 1 dexamethasone PK trial simulation
output: csv file matching the REDCap export schema.
"""

import random
import csv
#The D1 schema/template defines the structure of one volunteer's data record, with all fields initialized to empty strings or zero values.
d1_template = {
    "site_id": "",
    "screening_date": "",
    "screened_by": "",
    "dob": "",
    "age_years": 0,
    "sex_at_birth": 0,
    "weight_kg": 0.0,
    "height_cm": 0.0,
    "bmi": 0.0,
    "i1-age": 0,
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

volunteer_number = 1