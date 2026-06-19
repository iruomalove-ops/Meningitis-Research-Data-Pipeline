OPTIONS (SKIP=1)
LOAD DATA
CHARACTERSET AL32UTF8
INTO TABLE d5_safety_labs_and_vitals
TRUNCATE
FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '"'
TRAILING NULLCOLS
(
  record_id, redcap_repeat_instance, redcap_event_name,
  d5_lab_collection_date, d5_lab_collection_time, d5_fasting_status,
  d5_sbp, d5_dbp, d5_hr, d5_temp, d5_rr, d5_spo2,
  d5_hb, d5_wcc, d5_neutrophils, d5_lymphocytes, d5_platelets,
  d5_alt, d5_ast, d5_bilirubin, d5_alp, d5_albumin,
  d5_creatinine, d5_urea, d5_egfr,
  d5_sodium, d5_potassium, d5_chloride, d5_glucose,
  d5_glucose_high_flag, d5_any_lab_abnormal,
  d5_abnormal_details CHAR(2000), d5_action_taken CHAR(500), d5_pi_signoff
)
