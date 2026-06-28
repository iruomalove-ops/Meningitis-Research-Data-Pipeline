-- lab_result: long findings table. One row per volunteer per lab visit per analyte (≈ 18×3×17 = 918).
-- Derived from staging D5 by UNPIVOT. Labs populate at only 3 events; UNPIVOT skips the NULL (vitals-only) events automatically.
-- Visit-level abnormal flags (d5_any_lab_abnormal etc.) intentionally excluded — they are visit-level qualifiers, not per-analyte facts; derive abnormality from reference ranges in the analytics layer.

DROP TABLE lab_result CASCADE CONSTRAINTS;

CREATE TABLE lab_result (
  record_id     VARCHAR2(50),
  visit_id      NUMBER,
  lab_test      VARCHAR2(20),
  lab_value     NUMBER(10,2),
  lab_result_id NUMBER GENERATED ALWAYS AS IDENTITY
);

ALTER TABLE lab_result ADD (
  CONSTRAINT pk_lab_result PRIMARY KEY (lab_result_id),
  CONSTRAINT uq_lab_rec_visit_test UNIQUE (record_id, visit_id, lab_test),
  CONSTRAINT fk_lab_subject FOREIGN KEY (record_id) REFERENCES subject (record_id),
  CONSTRAINT fk_lab_visit   FOREIGN KEY (visit_id)  REFERENCES visit (visit_id)
);

INSERT INTO lab_result (record_id, visit_id, lab_test, lab_value)
SELECT u.record_id, v.visit_id, u.lab_test, u.lab_value
FROM (
  SELECT record_id, redcap_event_name, lab_test, lab_value
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