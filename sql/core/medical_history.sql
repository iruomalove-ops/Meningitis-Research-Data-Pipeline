-- medical_history: one row per eligible volunteer (28). Baseline history + lifestyle.
-- Derived from staging D2. Demographics live on subject; screening vitals go to vital_sign.

DROP TABLE medical_history CASCADE CONSTRAINTS;

CREATE TABLE medical_history (
  record_id          VARCHAR2(50),
  pmh_any            VARCHAR2(10),
  pmh_details        VARCHAR2(1000),
  surgery_any        VARCHAR2(10),
  surgery_details    VARCHAR2(1000),
  allergy_any        VARCHAR2(10),
  allergy_details    VARCHAR2(1000),
  med_any            VARCHAR2(10),
  med_list           VARCHAR2(1000),
  alcohol_units      NUMBER(5,1),
  caffeine_cups      NUMBER(5,1),
  exercise_freq      VARCHAR2(50),
  vaccine_uptodate   VARCHAR2(10),
  recent_vaccine     VARCHAR2(200),
  family_history     VARCHAR2(1000),
  pi_assessment      VARCHAR2(2000),
  medical_history_id NUMBER GENERATED ALWAYS AS IDENTITY
);

ALTER TABLE medical_history ADD (
  CONSTRAINT pk_medical_history PRIMARY KEY (medical_history_id),
  CONSTRAINT uq_medical_history_record_id UNIQUE (record_id),
  CONSTRAINT fk_medical_history_subject
    FOREIGN KEY (record_id) REFERENCES subject (record_id)
);

INSERT INTO medical_history (
  record_id, pmh_any, pmh_details, surgery_any, surgery_details,
  allergy_any, allergy_details, med_any, med_list,
  alcohol_units, caffeine_cups, exercise_freq,
  vaccine_uptodate, recent_vaccine, family_history, pi_assessment
)
SELECT
  record_id, pmh_any, pmh_details, surgery_any, surgery_details,
  allergy_any, allergy_details, med_any, med_list,
  alcohol_units, caffeine_cups, exercise_freq,
  vaccine_uptodate, recent_vaccine, family_history, pi_assessment
FROM d2_demographics_medical_history;

COMMIT;