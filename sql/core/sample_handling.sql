-- sample_handling: PK sample chain of custody. One row per volunteer per timepoint (144).
-- Derived from staging D4. The PK finding (concentration) lives in pk_concentration.
-- Same timepoint-code -> visit.event_name bridge as pk_concentration.

DROP TABLE sample_handling CASCADE CONSTRAINTS;

CREATE TABLE sample_handling (
  record_id          VARCHAR2(50),
  visit_id           NUMBER,
  repeat_instance    NUMBER(3),
  sample_collected   VARCHAR2(10),
  missed_reason      VARCHAR2(200),
  cannula_site       VARCHAR2(10),
  sample_volume      NUMBER(5,1),
  tube_type          VARCHAR2(10),
  centrifuge_time    DATE,
  plasma_aliquoted   VARCHAR2(10),
  storage_temp       VARCHAR2(10),
  shipped            VARCHAR2(10),
  sample_notes       VARCHAR2(500),
  sample_handling_id NUMBER GENERATED ALWAYS AS IDENTITY
);

ALTER TABLE sample_handling ADD (
  CONSTRAINT pk_sample_handling PRIMARY KEY (sample_handling_id),
  CONSTRAINT uq_samp_hand_rec_visit UNIQUE (record_id, visit_id),
  CONSTRAINT fk_samp_hand_subject FOREIGN KEY (record_id) REFERENCES subject (record_id),
  CONSTRAINT fk_samp_hand_visit   FOREIGN KEY (visit_id)  REFERENCES visit (visit_id)
);

INSERT INTO sample_handling (
  record_id, visit_id, repeat_instance,
  sample_collected, missed_reason, cannula_site, sample_volume,
  tube_type, centrifuge_time, plasma_aliquoted, storage_temp, shipped, sample_notes
)
SELECT
  d4.record_id,
  v.visit_id,
  d4.redcap_repeat_instance,
  d4.sample_collected,
  d4.missed_reason,
  d4.cannula_site,
  d4.sample_volume,
  d4.tube_type,
  TO_DATE(d4.centrifuge_time, 'YYYY-MM-DD HH24:MI'),
  d4.plasma_aliquoted,
  d4.storage_temp,
  d4.shipped,
  d4.sample_notes
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