OPTIONS (SKIP=1)
LOAD DATA
CHARACTERSET AL32UTF8
INTO TABLE d1_eligibility
TRUNCATE
FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '"'
TRAILING NULLCOLS
(
  record_id, screening_date, screened_by, dob, age_years, sex_at_birth,
  weight_kg, height_cm, bmi,
  i1_age, i2_bmi, i3_health, i6_comply, i7_consent,
  e1_cyp3a4, e2_meds, e3_diabetes, e4_immune, e5_pregnancy, e6_allergy,
  e7_smoking, e8_alcohol, e9_previoustrial,
  eligibility_determination,
  screen_failure_reason     CHAR(100),
  screen_failure_narrative  CHAR(2000)
)
