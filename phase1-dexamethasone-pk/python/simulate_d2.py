"""
simulate_d2.py
Generates D2 demographics and medical history records for eligible volunteers.
Reads d1_eligibility.csv and filters to volunteers where eligibility_determination = 1.
"""
import random
import csv
import string
#read D1 eligibility records and filter to eligible volunteers
with open("d1_eligibility.csv","r", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    all_d1_records = list(reader)
#filter to eligible volunteers
eligible_volunteers = []
for records in all_d1_records:
    if records["eligibility_determination"] == "1":
        eligible_volunteers.append(records)
#export the 20 eligible volunteers to seprate csv for refrence
with open("eligible_volunteers.csv", mode="w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=list(all_d1_records[0].keys()))
    writer.writeheader()
    writer.writerows(eligible_volunteers)
#d2_template - defines the dtructure of d2 records.
d2_template = {
    "record_id": "",
    "initials": "",
    "race": 0,
    "ethnicity": 0,
    "country_birth": 0,
    "sbp_screen": 0,
    "dbp_screen": 0,
    "hr_screen": 0,
    "temp_screen": 0.0,
    "rr_screen": 0,
    "spo2_screen": 0,
    "pmh_any": 0,
    "pmh_details": "",
    "surgery_any": 0,
    "surgery_details": "",
    "allergy_any": 0,
    "allergy_details": "",
    "med_any": 0,
    "med_list": "",
    "alcohol_units": 0,
    "caffeine_cups": 0,
    "exercise_freq": 0,
    "vaccine_uptodate": 0,
    "recent_vaccine": 0,
    "family_history": 0,
    "pi_assessment": ""
}
def make_d2_record(d1_record):
    #generate volunteer initials -3 random uppercase letters
    initials = "".join (random.choices(string.ascii_uppercase, k=3))
    #race 1 = Black African,2 = White,3 = Coloured,4 = Indian or Asian,5 = Mixed,6 = Other,7 = Prefer not to say
    race = random.choices([1,2,3,4,5,6,7], weights =[70,18,7,2,1,1,1], k=1)[0]
    #ethnicity 1=hispanic or latino, 2=not hispanic or latino, 3=prefer not to say
    ethnicity = random.choices([1,2,3], weights=[10,97,5], k=1)[0]
    #country of birth #list of countries alphabetically orderd with South Africa as most common, then other African countries, then rest of world
    #country codes -REDCap dropdown list codes for country of birth
    sa_code = 159
    #other African countries
    # Top African migrant countries to South Africa
    # Nigeria, Zimbabwe, Malawi, Lesotho, Somalia, DRC, Mozambique
    african_codes = [124, 195, 101, 95, 153, 45, 117]
    african_weights = [20, 35, 15, 10, 5, 10, 5]  # matching the codes order
    #rest of the world is everything 1-195 excluding SA and the above AFRICA codes
    all_codes = list(range(1,196))
    rest_of_world_code = [code for code in all_codes if code != sa_code and code not in african_codes]
    #country of birth -80% South Africa, 15% other African countries, 5% rest of world
    category = random.choices([sa_code, african_codes, rest_of_world_code], weights=[80,15,5], k=1)[0]
    if category == sa_code:
        country_birth = sa_code 
    elif category == "African":
        country_birth = random.choices(african_codes, weights=african_weights, k=1)[0]
    else:
        country_birth = random.choice(rest_of_world_code)
    # vital signs - all use bell curve with mean and standard deviation based on typical healthy adult ranges
    sbp_screen = int(round(random.gauss(120,10),0)) #systolic blood pressure
    dbp_screen = int(round(random.gauss(75,8),0))#diastolic blood pressure
    hr_screen = int(round(random.gauss(70,10),0)) #heart rate
    temp_screen = round(random.gauss(36.8,0.4),1) #body temperature in Celsius
    rr_screen = int(round(random.gauss(16,2),0)) #respiratory rate    
    spo2_screen = random.randint(97,100) #oxygen saturation
    #medical history 
    pmh_any = random.choices([1,0], weights=[25,75], k=1)[0]  #25% have some past medical history, 75% none
    if pmh_any == 1:
        pmh_details = random.choice([
            "childhood asthma", "last attack age 12, no current symptoms nor treatments ",
            "tonsilitis at age 8, no complications, no ongoing issues",
            "fractured raduis age 15, healed with no sequelae",
            "mild eczema, resolved ",
            "Glandular fever at age 17, full recovery, no ongoing issues",
            "seasonal allergies, mild, no treatment",
        ])
    else:
        pmh_details = ""
    #any past sugeries - 35% yes, 65% no
    surgery_any = random.choices([1,0], weights=[35,65], k=1)[0]
    if surgery_any == 1:
        surgery_details = random.choice([
            "appendectomy age 20, no complications",
            "tonsillectomy age 8, no complications",
            "fracture repair age 15, healed with no sequelae",
            "knee arthroscopy age 25, full recovery",
            "hernia repair age 30, no complications",
            "cesarean section age 28, healthy baby, full recovery"
        ])
    else:
        surgery_details = ""
    #allergies -30% yes, 70% no
    allergy_any = random.choices([1,0], weights=[30,70], k=1)[0]
    if allergy_any == 1:
        allergy_details = random.choice([
            "penicillin allergy, rash and itching, avoid penicillins",
            "peanut allergy, anaphylaxis, carries epipen",
            "seasonal allergies, mild, no treatment",
            "latex allergy, contact dermatitis, avoid latex products",
            "shellfish allergy, hives and swelling, avoid shellfish",
            "bee sting allergy, anaphylaxis, carries epipen"
        ])
    else:
        allergy_details = ""
    #anycurrent medication -10% yes, 90% no,only contraceptives and paracetamol allowed
    med_any = random.choices([1,0], weights=[10,90], k=1)[0]
    if med_any == 1:
        med_list = random.choice([
            "oral contraceptives",
            "paracetamol"
        ])
    else:
        med_list = ""
    #lifestyle factors
    #alcohol unit per week #bell curve, mean 4, SD 3, min 0
    alcohol_units=max(0,int(round(random.gauss(4,3),0)))
    #caffeine cups per day,bell curve, mean 2.5, SD 1.5, min 0
    caffeine_cups =max(0,int(round(random.gauss(2.5,1.5),1)))
    #exercise frequency -None = 1",less than once a week = 2, 1-2 times a week = 3, 3-4 times a week = 4,daily = 5
    exercise_freq = random.choices([1,2,3,4,5], weights=[5, 15, 30, 35, 15], k=1)[0]
    #vaccination status
    #vaccin_uptodate-0=no, 1=yes, 2=unknown, 80% yes, 5% no, 15% unknown
    vaccine_uptodate = random.choices([1, 2, 0], weights=[80, 15, 5], k=1)[0]
    #recent vaccine -1 yes, 0 no, 5% yes, 95% no
    recent_vaccine = random.choices([1,0], weights=[5,95], k=1)[0]
    #family history of significant medical conditions - 1 yes, 0 no, 40% yes, 60% no
    family_history = random.choices([1,0], weights=[40,60], k=1)[0]
    #pi assessment - free text field with overall assessment of health status based on above data, 3 categories: "Excellent health", "Good health", "Fair health", "Poor health"
    if (
        pmh_any == 0
        and surgery_any == 0
        and allergy_any == 0
        and med_any == 0
        and exercise_freq >= 4
        and vaccine_uptodate == 1
        and family_history == 0
    ):
        pi_assessment = "Excellent health"
    else:
        pi_assessment = "Good health"
    return {
        "record_id": d1_record["record_id"],  #use the same record_id as D1 to link records
        "initials": initials,
        "race": race,
        "ethnicity": ethnicity,
        "country_birth": country_birth,
        "sbp_screen": sbp_screen,
        "dbp_screen": dbp_screen,
        "hr_screen": hr_screen,
        "temp_screen": temp_screen,
        "rr_screen": rr_screen,
        "spo2_screen": spo2_screen,
        "pmh_any": pmh_any,
        "pmh_details": pmh_details,
        "surgery_any": surgery_any,
        "surgery_details": surgery_details,
        "allergy_any": allergy_any,
        "allergy_details": allergy_details,
        "med_any": med_any,
        "med_list": med_list,
        "alcohol_units": alcohol_units,
        "caffeine_cups": caffeine_cups,
        "exercise_freq": exercise_freq,
        "vaccine_uptodate": vaccine_uptodate,
        "recent_vaccine": recent_vaccine,
        "family_history": family_history,
        "pi_assessment": pi_assessment
    }
# Test the function with the first eligible volunteer
test_record = make_d2_record(eligible_volunteers[0])
#geneate D2 records for all eligible volunteers
all_d2_records = []
for d1_record in eligible_volunteers:
    d2_record = make_d2_record(d1_record)
    all_d2_records.append(d2_record)
#verification
print(f"Total D2 records generated: {len(all_d2_records)}")
print(f"First record initials: {all_d2_records[0]['initials']}")
print(f"Last record initials: {all_d2_records[-1]['initials']}")
#export to csv
with open("d2_demographics_medical_history.csv", mode="w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=list(d2_template.keys()))
    writer.writeheader()
    writer.writerows(all_d2_records)
print("D2 demographics and medical history records saved to d2_demographics_medical_history.csv")
#verification 
print(all_d2_records[0])





