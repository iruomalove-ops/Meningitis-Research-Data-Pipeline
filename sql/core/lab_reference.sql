-- lab_reference: analyte units + normal reference ranges. Authored reference table.
-- Ranges sourced from simulate_d5.py (lines 21-57, "standard adult clinical reference ranges").
-- Units sourced from the REDCap data dictionary field notes.
-- sex_code: 1 male / 2 female / 3 intersex-or-indeterminate; 'ALL' = not sex-specific.
-- HB & creatinine are sex-specific (3 rows each); glucose split fasted/non-fasted (2 rows).

DROP TABLE lab_reference CASCADE CONSTRAINTS;

CREATE TABLE lab_reference (
  lab_test         VARCHAR2(20),
  sex_code         VARCHAR2(5),     -- 1 / 2 / 3 / ALL
  range_low        NUMBER(10,2),
  range_high       NUMBER(10,2),
  unit             VARCHAR2(30),
  lab_reference_id NUMBER GENERATED ALWAYS AS IDENTITY
);

ALTER TABLE lab_reference ADD (
  CONSTRAINT pk_lab_reference PRIMARY KEY (lab_reference_id),
  CONSTRAINT uq_lab_ref_test_sex UNIQUE (lab_test, sex_code)
);

-- non-sex-specific tests (sex_code = 'ALL')
INSERT INTO lab_reference (lab_test, sex_code, range_low, range_high, unit) VALUES ('WCC',         'ALL',   4.0,  11.0, '10^9/L');
INSERT INTO lab_reference (lab_test, sex_code, range_low, range_high, unit) VALUES ('NEUTROPHILS', 'ALL',   2.0,   7.5, '10^9/L');
INSERT INTO lab_reference (lab_test, sex_code, range_low, range_high, unit) VALUES ('LYMPHOCYTES', 'ALL',   1.0,   4.0, '10^9/L');
INSERT INTO lab_reference (lab_test, sex_code, range_low, range_high, unit) VALUES ('PLATELETS',   'ALL', 150.0, 400.0, '10^9/L');
INSERT INTO lab_reference (lab_test, sex_code, range_low, range_high, unit) VALUES ('ALT',         'ALL',  10.0,  40.0, 'U/L');
INSERT INTO lab_reference (lab_test, sex_code, range_low, range_high, unit) VALUES ('AST',         'ALL',  10.0,  40.0, 'U/L');
INSERT INTO lab_reference (lab_test, sex_code, range_low, range_high, unit) VALUES ('BILIRUBIN',   'ALL',   3.0,  21.0, 'umol/L');
INSERT INTO lab_reference (lab_test, sex_code, range_low, range_high, unit) VALUES ('ALP',         'ALL',  30.0, 130.0, 'U/L');
INSERT INTO lab_reference (lab_test, sex_code, range_low, range_high, unit) VALUES ('ALBUMIN',     'ALL',  35.0,  50.0, 'g/L');
INSERT INTO lab_reference (lab_test, sex_code, range_low, range_high, unit) VALUES ('UREA',        'ALL',   2.5,   7.5, 'mmol/L');
INSERT INTO lab_reference (lab_test, sex_code, range_low, range_high, unit) VALUES ('EGFR',        'ALL',  90.0, 120.0, 'mL/min/1.73m2');
INSERT INTO lab_reference (lab_test, sex_code, range_low, range_high, unit) VALUES ('SODIUM',      'ALL', 135.0, 145.0, 'mmol/L');
INSERT INTO lab_reference (lab_test, sex_code, range_low, range_high, unit) VALUES ('POTASSIUM',   'ALL',   3.5,   5.0, 'mmol/L');
INSERT INTO lab_reference (lab_test, sex_code, range_low, range_high, unit) VALUES ('CHLORIDE',    'ALL',  98.0, 107.0, 'mmol/L');

-- glucose: fasted vs non-fasted (both non-sex-specific)
INSERT INTO lab_reference (lab_test, sex_code, range_low, range_high, unit) VALUES ('GLUCOSE_FASTED',    'ALL', 3.9, 5.5, 'mmol/L');
INSERT INTO lab_reference (lab_test, sex_code, range_low, range_high, unit) VALUES ('GLUCOSE_NONFASTED', 'ALL', 3.9, 7.8, 'mmol/L');

-- sex-specific: HB — ranges & scale from simulate_d5.py (g/L, SI); data confirmed 122-167 g/L.
-- NOTE: dictionary field note says "g/dL" but the actual data is g/L — data wins, discrepancy logged.
INSERT INTO lab_reference (lab_test, sex_code, range_low, range_high, unit) VALUES ('HB', '1', 135.0, 175.0, 'g/L');
INSERT INTO lab_reference (lab_test, sex_code, range_low, range_high, unit) VALUES ('HB', '2', 120.0, 155.0, 'g/L');
INSERT INTO lab_reference (lab_test, sex_code, range_low, range_high, unit) VALUES ('HB', '3', 120.0, 175.0, 'g/L');

-- sex-specific: creatinine (umol/L)
INSERT INTO lab_reference (lab_test, sex_code, range_low, range_high, unit) VALUES ('CREATININE', '1', 60.0, 110.0, 'umol/L');
INSERT INTO lab_reference (lab_test, sex_code, range_low, range_high, unit) VALUES ('CREATININE', '2', 45.0,  90.0, 'umol/L');
INSERT INTO lab_reference (lab_test, sex_code, range_low, range_high, unit) VALUES ('CREATININE', '3', 45.0, 110.0, 'umol/L');

COMMIT;