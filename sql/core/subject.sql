-- subject: the spine. One row per screened volunteer (100).
-- Derived from staging D1 + D2.

DROP TABLE subject CASCADE CONSTRAINTS;

CREATE TABLE subject (
  record_id      VARCHAR2(50),
  dob            DATE,
  age_years      NUMBER(3),
  sex_at_birth   VARCHAR2(10),
  weight_kg      NUMBER(5,1),
  height_cm      NUMBER(5,1),
  bmi            NUMBER(4,1),
  race           VARCHAR2(10),
  ethnicity      VARCHAR2(10),
  country_birth  VARCHAR2(100),
  initials       VARCHAR2(20),
  subject_id     NUMBER GENERATED ALWAYS AS IDENTITY
);

ALTER TABLE subject ADD (
  CONSTRAINT pk_subject PRIMARY KEY (subject_id),
  CONSTRAINT uq_subject_record_id UNIQUE (record_id)
);

INSERT INTO subject (
  record_id, dob, age_years, sex_at_birth,
  weight_kg, height_cm, bmi,
  race, ethnicity, country_birth, initials
)
SELECT
  d1.record_id,
  TO_DATE(d1.dob, 'YYYY-MM-DD'),
  d1.age_years, d1.sex_at_birth,
  d1.weight_kg, d1.height_cm, d1.bmi,
  d2.race, d2.ethnicity, d2.country_birth, d2.initials
FROM d1_eligibility d1
LEFT JOIN d2_demographics_medical_history d2
  ON d1.record_id = d2.record_id;

COMMIT;


