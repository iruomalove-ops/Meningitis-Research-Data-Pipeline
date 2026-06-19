OPTIONS (SKIP=1)
LOAD DATA
CHARACTERSET AL32UTF8
INTO TABLE d6_adverse_events_and_saes
TRUNCATE
FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '"'
TRAILING NULLCOLS
(
  record_id, redcap_repeat_instance, redcap_event_name,
  ae_any, ae_term CHAR(200),
  ae_onset_date, ae_onset_time, ae_resolution_date, ae_ongoing,
  ae_ctcae_grade, ae_relatedness, ae_outcome, ae_action,
  ae_treatment CHAR(500),
  is_sae, sae_criterion, sae_reported_sponsor_date, sae_reported_ethics_date,
  ae_pi_signoff
)
