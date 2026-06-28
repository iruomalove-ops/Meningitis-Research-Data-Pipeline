-- visit: the event dimension. One row per trial event (11).
-- Authored reference table, not derived from staging.
-- hours_from_dose & nominal_day are NOMINAL (protocol-planned) timing; dosing = hour 0.
-- Actual per-draw timing lives in D4 (actual_datetime), not here.
-- visit_category: PK_SCHEDULE (intensive PK sampling grid) vs CLINICAL_VISIT (standalone visit).

DROP TABLE visit CASCADE CONSTRAINTS;

CREATE TABLE visit (
  event_name      VARCHAR2(50),    -- natural key, exact REDCap spelling
  label           VARCHAR2(50),
  sort_order      NUMBER(3),       -- chronological ordering
  hours_from_dose NUMBER(8,2),     -- nominal hours since dosing; dosing = 0
  nominal_day     NUMBER(4),       -- protocol day; dosing = 0
  visit_category  VARCHAR2(20),    -- PK_SCHEDULE | CLINICAL_VISIT
  visit_id        NUMBER GENERATED ALWAYS AS IDENTITY
);

ALTER TABLE visit ADD (
  CONSTRAINT pk_visit PRIMARY KEY (visit_id),
  CONSTRAINT uq_visit_event_name UNIQUE (event_name)
);

INSERT INTO visit (event_name, label, sort_order, hours_from_dose, nominal_day, visit_category) VALUES ('screening_arm_1',      'Screening',        1, -168,   -7, 'CLINICAL_VISIT');
INSERT INTO visit (event_name, label, sort_order, hours_from_dose, nominal_day, visit_category) VALUES ('day_0__dosing_arm_1',  'Day 0 Dosing',     2,    0,    0, 'CLINICAL_VISIT');
INSERT INTO visit (event_name, label, sort_order, hours_from_dose, nominal_day, visit_category) VALUES ('pk_t30min_arm_1',      'PK +30 min',       3,  0.5,    0, 'PK_SCHEDULE');
INSERT INTO visit (event_name, label, sort_order, hours_from_dose, nominal_day, visit_category) VALUES ('pk_t1h_arm_1',         'PK +1 h',          4,    1,    0, 'PK_SCHEDULE');
INSERT INTO visit (event_name, label, sort_order, hours_from_dose, nominal_day, visit_category) VALUES ('pk_t2h_arm_1',         'PK +2 h',          5,    2,    0, 'PK_SCHEDULE');
INSERT INTO visit (event_name, label, sort_order, hours_from_dose, nominal_day, visit_category) VALUES ('pk_t4h_arm_1',         'PK +4 h',          6,    4,    0, 'PK_SCHEDULE');
INSERT INTO visit (event_name, label, sort_order, hours_from_dose, nominal_day, visit_category) VALUES ('pk_t8h_arm_1',         'PK +8 h',          7,    8,    0, 'PK_SCHEDULE');
INSERT INTO visit (event_name, label, sort_order, hours_from_dose, nominal_day, visit_category) VALUES ('pk_t24h_arm_1',        'PK +24 h',         8,   24,    1, 'PK_SCHEDULE');
INSERT INTO visit (event_name, label, sort_order, hours_from_dose, nominal_day, visit_category) VALUES ('pk_t48h_arm_1',        'PK +48 h',         9,   48,    2, 'PK_SCHEDULE');
INSERT INTO visit (event_name, label, sort_order, hours_from_dose, nominal_day, visit_category) VALUES ('day_7_followup_arm_1', 'Day 7 Follow-up', 10,  168,    7, 'CLINICAL_VISIT');
INSERT INTO visit (event_name, label, sort_order, hours_from_dose, nominal_day, visit_category) VALUES ('src_review_arm_1',     'SRC Review',      11,  504,   21, 'CLINICAL_VISIT');

COMMIT;