-- vital_sign: long findings table. One row per volunteer per visit per vital (≈ 18×10×6).
-- Derived from staging D5 by UNPIVOT (wide vitals columns -> rows).
-- D5 carries redcap_event_name directly, so the visit join needs no code bridge.

DROP TABLE vital_sign CASCADE CONSTRAINTS;

CREATE TABLE vital_sign (
  record_id     VARCHAR2(50),
  visit_id      NUMBER,
  vs_test       VARCHAR2(20),    -- SBP / DBP / HR / TEMP / RR / SPO2
  vs_value      NUMBER(6,1),
  vital_sign_id NUMBER GENERATED ALWAYS AS IDENTITY
);

ALTER TABLE vital_sign ADD (
  CONSTRAINT pk_vital_sign PRIMARY KEY (vital_sign_id),
  CONSTRAINT uq_vs_rec_visit_test UNIQUE (record_id, visit_id, vs_test),
  CONSTRAINT fk_vs_subject FOREIGN KEY (record_id) REFERENCES subject (record_id),
  CONSTRAINT fk_vs_visit   FOREIGN KEY (visit_id)  REFERENCES visit (visit_id)
);

INSERT INTO vital_sign (record_id, visit_id, vs_test, vs_value)
SELECT
  u.record_id,
  v.visit_id,
  u.vs_test,
  u.vs_value
FROM (
  SELECT record_id, redcap_event_name, vs_test, vs_value
  FROM d5_safety_labs_and_vitals
  UNPIVOT (
    vs_value FOR vs_test IN (
      d5_sbp  AS 'SBP',
      d5_dbp  AS 'DBP',
      d5_hr   AS 'HR',
      d5_temp AS 'TEMP',
      d5_rr   AS 'RR',
      d5_spo2 AS 'SPO2'
    )
  )
) u
JOIN visit v ON v.event_name = u.redcap_event_name;

COMMIT;