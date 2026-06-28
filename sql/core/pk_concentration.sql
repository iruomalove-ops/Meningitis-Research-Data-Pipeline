-- pk_concentration: the PK finding. One row per volunteer per timepoint (144).
-- Derived from staging D4. Sample chain-of-custody lives in sample_handling.
-- D4 carries a numeric timepoint code, not an event name; the CASE bridges
--   code -> visit.event_name so this fact can FK to the visit dimension.

DROP TABLE pk_concentration CASCADE CONSTRAINTS;

CREATE TABLE pk_concentration (
  record_id            VARCHAR2(50),
  visit_id             NUMBER,          -- FK to visit (resolved via the bridge)
  repeat_instance      NUMBER(3),
  scheduled_datetime   DATE,
  actual_datetime      DATE,
  plasma_concentration NUMBER(10,3),
  blq                  VARCHAR2(10),
  assay_date           DATE,
  pk_concentration_id  NUMBER GENERATED ALWAYS AS IDENTITY
);

ALTER TABLE pk_concentration ADD (
  CONSTRAINT pk_pk_concentration PRIMARY KEY (pk_concentration_id),
  CONSTRAINT uq_pk_conc_rec_visit UNIQUE (record_id, visit_id),
  CONSTRAINT fk_pk_conc_subject FOREIGN KEY (record_id) REFERENCES subject (record_id),
  CONSTRAINT fk_pk_conc_visit   FOREIGN KEY (visit_id)  REFERENCES visit (visit_id)
);

INSERT INTO pk_concentration (
  record_id, visit_id, repeat_instance,
  scheduled_datetime, actual_datetime,
  plasma_concentration, blq, assay_date
)
SELECT
  d4.record_id,
  v.visit_id,
  d4.redcap_repeat_instance,
  TO_DATE(d4.scheduled_datetime, 'YYYY-MM-DD HH24:MI'),
  TO_DATE(d4.actual_datetime,    'YYYY-MM-DD HH24:MI'),
  d4.plasma_concentration,
  d4.blq,
  TO_DATE(d4.assay_date, 'YYYY-MM-DD')
FROM d4_pk_sampling d4
JOIN visit v
  ON v.event_name =
     CASE d4.timepoint
       WHEN '1' THEN 'day_0__dosing_arm_1'
       WHEN '2' THEN 'pk_t30min_arm_1'
       WHEN '3' THEN 'pk_t1h_arm_1'
       WHEN '4' THEN 'pk_t2h_arm_1'
       WHEN '5' THEN 'pk_t4h_arm_1'
       WHEN '6' THEN 'pk_t8h_arm_1'
       WHEN '7' THEN 'pk_t24h_arm_1'
       WHEN '8' THEN 'pk_t48h_arm_1'
     END;

COMMIT;