-- src_review: one row per randomised volunteer (18). Safety review + SRC escalation + deviations.
-- Derived from staging D3b. Recorded at the SRC meeting; deviation fields ride along at the same grain.

DROP TABLE src_review CASCADE CONSTRAINTS;

CREATE TABLE src_review (
  record_id             VARCHAR2(50),
  sentinel_48h_pass     VARCHAR2(10),   -- blank for non-sentinels, 1 for reviewed sentinels
  sentinel_review_date  DATE,
  dlt_observed          VARCHAR2(10),   -- raw 1/0
  dlt_description       VARCHAR2(2000),
  src_meeting_date      DATE,
  src_decision          VARCHAR2(10),   -- raw code (1 = escalate)
  src_rationale         VARCHAR2(2000),
  src_signed            VARCHAR2(100),
  deviation_any         VARCHAR2(10),   -- raw 1/0
  deviation_details     VARCHAR2(2000),
  deviation_reported    VARCHAR2(50),
  deviation_ethics      VARCHAR2(50),
  pi_escalation_signoff VARCHAR2(100),
  src_review_id         NUMBER GENERATED ALWAYS AS IDENTITY
);

ALTER TABLE src_review ADD (
  CONSTRAINT pk_src_review PRIMARY KEY (src_review_id),
  CONSTRAINT uq_src_review_record_id UNIQUE (record_id),
  CONSTRAINT fk_src_review_subject
    FOREIGN KEY (record_id) REFERENCES subject (record_id)
);

INSERT INTO src_review (
  record_id, sentinel_48h_pass, sentinel_review_date,
  dlt_observed, dlt_description,
  src_meeting_date, src_decision, src_rationale, src_signed,
  deviation_any, deviation_details, deviation_reported, deviation_ethics,
  pi_escalation_signoff
)
SELECT
  record_id, sentinel_48h_pass,
  TO_DATE(sentinel_review_date, 'YYYY-MM-DD'),
  dlt_observed, dlt_description,
  TO_DATE(src_meeting_date, 'YYYY-MM-DD'),
  src_decision, src_rationale, src_signed,
  deviation_any, deviation_details, deviation_reported, deviation_ethics,
  pi_escalation_signoff
FROM d3b_safety_review;

COMMIT;