-- lab_result: long findings table. One row per volunteer per lab visit per analyte (918).
-- Derived from staging D5 by UNPIVOT. Labs populate at only 3 events; UNPIVOT skips
--   the NULL (vitals-only) events automatically.
-- fasting_status carried from D5 (raw code: 1 = Fasted >=8h, 0 = Not fasted, 2 = N/A)
--   because the glucose reference range depends on it — the classification must
--   resolve the correct range from the data, not from a hardcoded assumption.
--   Mirrors SDTM LB's LBFAST variable.
-- Visit-level abnormal flags intentionally excluded — visit-level qualifiers, not
--   per-analyte facts; abnormality is derived from reference ranges.

DROP TABLE lab_result CASCADE CONSTRAINTS;

CREATE TABLE lab_result (
  record_id      VARCHAR2(50),
  visit_id       NUMBER,
  lab_test       VARCHAR2(20),
  lab_value      NUMBER(10,2),
  fasting_status VARCHAR2(10),   -- raw code from D5; 1 = Fasted >=8h
  lab_result_id  NUMBER GENERATED ALWAYS AS IDENTITY
);

ALTER TABLE lab_result ADD (
  CONSTRAINT pk_lab_result PRIMARY KEY (lab_result_id),
  CONSTRAINT uq_lab_rec_visit_test UNIQUE (record_id, visit_id, lab_test),
  CONSTRAINT fk_lab_subject FOREIGN KEY (record_id) REFERENCES subject (record_id),
  CONSTRAINT fk_lab_visit   FOREIGN KEY (visit_id)  REFERENCES visit (visit_id)
);

INSERT INTO lab_result (record_id, visit_id, lab_test, lab_value, fasting_status)
SELECT u.record_id, v.visit_id, u.lab_test, u.lab_value, u.fasting_status
FROM (
  SELECT record_id, redcap_event_name, d5_fasting_status AS fasting_status, lab_test, lab_value
  FROM d5_safety_labs_and_vitals
  UNPIVOT (
    lab_value FOR lab_test IN (
      d5_hb          AS 'HB',
      d5_wcc         AS 'WCC',
      d5_neutrophils AS 'NEUTROPHILS',
      d5_lymphocytes AS 'LYMPHOCYTES',
      d5_platelets   AS 'PLATELETS',
      d5_alt         AS 'ALT',
      d5_ast         AS 'AST',
      d5_bilirubin   AS 'BILIRUBIN',
      d5_alp         AS 'ALP',
      d5_albumin     AS 'ALBUMIN',
      d5_creatinine  AS 'CREATININE',
      d5_urea        AS 'UREA',
      d5_egfr        AS 'EGFR',
      d5_sodium      AS 'SODIUM',
      d5_potassium   AS 'POTASSIUM',
      d5_chloride    AS 'CHLORIDE',
      d5_glucose     AS 'GLUCOSE'
    )
  )
) u
JOIN visit v ON v.event_name = u.redcap_event_name;

COMMIT;