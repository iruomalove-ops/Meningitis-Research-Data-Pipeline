-- enrollment: one row per enrolled volunteer (28), incl. reserve.
-- Derived from staging D3a. Randomisation facts only; dose facts live in dosing.

DROP TABLE enrollment CASCADE CONSTRAINTS;

CREATE TABLE enrollment (
  record_id        VARCHAR2(50),
  enrolment_status VARCHAR2(20),   -- Randomised / Reserve (raw, from D3a)
  cohort           VARCHAR2(10),   -- raw code 1/2/3; blank for reserve
  cohort_position  VARCHAR2(10),
  is_sentinel      VARCHAR2(10),   -- raw 1/0
  enrollment_id    NUMBER GENERATED ALWAYS AS IDENTITY
);

ALTER TABLE enrollment ADD (
  CONSTRAINT pk_enrollment PRIMARY KEY (enrollment_id),
  CONSTRAINT uq_enrollment_record_id UNIQUE (record_id),
  CONSTRAINT fk_enrollment_subject
    FOREIGN KEY (record_id) REFERENCES subject (record_id)
);

INSERT INTO enrollment (
  record_id, enrolment_status, cohort, cohort_position, is_sentinel
)
SELECT
  record_id, enrolment_status, cohort, cohort_position, is_sentinel
FROM d3a_dose_assignment;

COMMIT;