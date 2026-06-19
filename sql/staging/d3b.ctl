OPTIONS (SKIP=1)
LOAD DATA
CHARACTERSET AL32UTF8
INTO TABLE d3b_safety_review
TRUNCATE
FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '"'
TRAILING NULLCOLS
(
  record_id, sentinel_48h_pass, sentinel_review_date,
  dlt_observed, dlt_description CHAR(2000),
  src_meeting_date, src_decision, src_rationale CHAR(2000), src_signed,
  deviation_any, deviation_details CHAR(2000), deviation_reported, deviation_ethics,
  pi_escalation_signoff
)
