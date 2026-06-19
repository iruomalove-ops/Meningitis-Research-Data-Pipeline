OPTIONS (SKIP=1)
LOAD DATA
CHARACTERSET AL32UTF8
INTO TABLE d4_pk_sampling
TRUNCATE
FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '"'
TRAILING NULLCOLS
(
  record_id, redcap_repeat_instance, timepoint,
  scheduled_datetime, actual_datetime,
  sample_collected, missed_reason CHAR(200), cannula_site,
  sample_volume, tube_type, centrifuge_time,
  plasma_aliquoted, storage_temp, shipped,
  plasma_concentration, blq, assay_date,
  sample_notes CHAR(500)
)
