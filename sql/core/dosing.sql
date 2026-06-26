-- dosing: one row per DOSED volunteer (18). Exposure facts only.
-- Derived from staging D3a, filtered to Randomised (reserves were never dosed).
-- Note: cohort_open_date retained from d3a.cohort_open_date by CDM convention —
--   name preserved through every layer; represents the cohort's dosing-window
--   open date, kept here as the operational dosing-start timestamp.

DROP TABLE dosing CASCADE CONSTRAINTS;

CREATE TABLE dosing (
  record_id         VARCHAR2(50),
  cohort_open_date  DATE,           -- ISO text in staging -> real DATE here
  planned_dose_mg   NUMBER(5,1),    -- e.g. 2.0 / 4.0 / 8.0
  dose_per_kg       NUMBER(6,4),    -- small fraction, e.g. 0.1377
  imp_batch         VARCHAR2(50),
  imp_expiry        DATE,           -- ISO text -> DATE
  pi_dosing_signoff VARCHAR2(100),
  dosing_id         NUMBER GENERATED ALWAYS AS IDENTITY
);

ALTER TABLE dosing ADD (
  CONSTRAINT pk_dosing PRIMARY KEY (dosing_id),
  CONSTRAINT uq_dosing_record_id UNIQUE (record_id),
  CONSTRAINT fk_dosing_subject
    FOREIGN KEY (record_id) REFERENCES subject (record_id)
);

INSERT INTO dosing (
  record_id, cohort_open_date, planned_dose_mg, dose_per_kg,
  imp_batch, imp_expiry, pi_dosing_signoff
)
SELECT
  record_id,
  TO_DATE(cohort_open_date, 'YYYY-MM-DD'),
  planned_dose_mg,
  dose_per_kg,
  imp_batch,
  TO_DATE(imp_expiry, 'YYYY-MM-DD'),
  pi_dosing_signoff
FROM d3a_dose_assignment
WHERE enrolment_status = 'Randomised';

COMMIT;