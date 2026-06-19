OPTIONS (SKIP=1)
LOAD DATA
CHARACTERSET AL32UTF8
INTO TABLE d7_volunteer_symptom_diary
TRUNCATE
FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '"'
TRAILING NULLCOLS
(
  record_id, redcap_repeat_instance, redcap_event_name,
  diary_date, diary_day,
  sym_headache, sym_fatigue, sym_nausea, sym_insomnia,
  sym_mood, sym_appetite, sym_gi,
  sym_other, sym_other_details CHAR(1000),
  diary_medication, diary_med_details CHAR(1000),
  diary_completed_by
)
