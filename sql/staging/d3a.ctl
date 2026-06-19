OPTIONS (SKIP=1)
LOAD DATA
CHARACTERSET AL32UTF8
INTO TABLE d3a_dose_assignment
TRUNCATE
FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '"'
TRAILING NULLCOLS
(
  record_id, enrolment_status, cohort, cohort_position, is_sentinel,
  cohort_open_date, planned_dose_mg, dose_per_kg,
  imp_batch, imp_expiry, pi_dosing_signoff
)
