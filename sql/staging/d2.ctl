OPTIONS (SKIP=1)
LOAD DATA
CHARACTERSET AL32UTF8
INTO TABLE d2_demographics_medical_history
TRUNCATE
FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '"'
TRAILING NULLCOLS
(
  record_id, initials, race, ethnicity, country_birth,
  sbp_screen, dbp_screen, hr_screen, temp_screen, rr_screen, spo2_screen,
  pmh_any, pmh_details CHAR(1000),
  surgery_any, surgery_details CHAR(1000),
  allergy_any, allergy_details CHAR(1000),
  med_any, med_list CHAR(1000),
  alcohol_units, caffeine_cups, exercise_freq,
  vaccine_uptodate, recent_vaccine CHAR(200),
  family_history CHAR(1000),
  pi_assessment CHAR(2000)
)
