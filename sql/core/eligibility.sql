-- eligibility: one row per screened volunteer (100). The screening checklist + verdict.
-- Derived from staging D1. Demographics live on subject; not repeated here.

DROP TABLE eligibility CASCADE CONSTRAINTS;

CREATE TABLE eligibility (
  record_id                 VARCHAR2(50),
  screening_date            DATE,           -- ISO text -> DATE
  screened_by               VARCHAR2(100),
  -- inclusion checklist (raw 1/0)
  i1_age                    VARCHAR2(10),
  i2_bmi                    VARCHAR2(10),
  i3_health                 VARCHAR2(10),
  i6_comply                 VARCHAR2(10),
  i7_consent                VARCHAR2(10),
  -- exclusion checklist (raw 1/0)
  e1_cyp3a4                 VARCHAR2(10),
  e2_meds                   VARCHAR2(10),
  e3_diabetes               VARCHAR2(10),
  e4_immune                 VARCHAR2(10),
  e5_pregnancy              VARCHAR2(10),
  e6_allergy                VARCHAR2(10),
  e7_smoking                VARCHAR2(10),
  e8_alcohol                VARCHAR2(10),
  e9_previoustrial          VARCHAR2(10),
  -- verdict
  eligibility_determination VARCHAR2(10),   -- raw code 1/2
  screen_failure_reason     VARCHAR2(100),
  screen_failure_narrative  VARCHAR2(2000),
  eligibility_id            NUMBER GENERATED ALWAYS AS IDENTITY
);

ALTER TABLE eligibility ADD (
  CONSTRAINT pk_eligibility PRIMARY KEY (eligibility_id),
  CONSTRAINT uq_eligibility_record_id UNIQUE (record_id),
  CONSTRAINT fk_eligibility_subject
    FOREIGN KEY (record_id) REFERENCES subject (record_id)
);

INSERT INTO eligibility (
  record_id, screening_date, screened_by,
  i1_age, i2_bmi, i3_health, i6_comply, i7_consent,
  e1_cyp3a4, e2_meds, e3_diabetes, e4_immune, e5_pregnancy,
  e6_allergy, e7_smoking, e8_alcohol, e9_previoustrial,
  eligibility_determination, screen_failure_reason, screen_failure_narrative
)
SELECT
  record_id, TO_DATE(screening_date, 'YYYY-MM-DD'), screened_by,
  i1_age, i2_bmi, i3_health, i6_comply, i7_consent,
  e1_cyp3a4, e2_meds, e3_diabetes, e4_immune, e5_pregnancy,
  e6_allergy, e7_smoking, e8_alcohol, e9_previoustrial,
  eligibility_determination, screen_failure_reason, screen_failure_narrative
FROM d1_eligibility;

COMMIT;