-- diary_symptom: long findings table. One row per volunteer per diary visit per symptom (≈ 72×7 = 504).
-- Derived from staging D7 by UNPIVOT. 7 rated symptoms on a 0-3 severity scale.
-- Free-text sym_other and medication fields excluded — not rated symptoms (visit-level notes; later diary_note table if wanted).

DROP TABLE diary_symptom CASCADE CONSTRAINTS;

CREATE TABLE diary_symptom (
  record_id        VARCHAR2(50),
  visit_id         NUMBER,
  symptom          VARCHAR2(20),   -- HEADACHE / FATIGUE / NAUSEA / INSOMNIA / MOOD / APPETITE / GI
  severity         NUMBER(1),      -- 0 None / 1 Mild / 2 Moderate / 3 Severe (ordinal)
  diary_symptom_id NUMBER GENERATED ALWAYS AS IDENTITY
);

ALTER TABLE diary_symptom ADD (
  CONSTRAINT pk_diary_symptom PRIMARY KEY (diary_symptom_id),
  CONSTRAINT uq_diary_rec_visit_symptom UNIQUE (record_id, visit_id, symptom),
  CONSTRAINT fk_diary_subject FOREIGN KEY (record_id) REFERENCES subject (record_id),
  CONSTRAINT fk_diary_visit   FOREIGN KEY (visit_id)  REFERENCES visit (visit_id)
);

INSERT INTO diary_symptom (record_id, visit_id, symptom, severity)
SELECT u.record_id, v.visit_id, u.symptom, u.severity
FROM (
  SELECT record_id, redcap_event_name, symptom, severity
  FROM d7_volunteer_symptom_diary
  UNPIVOT (
    severity FOR symptom IN (
      sym_headache AS 'HEADACHE',
      sym_fatigue  AS 'FATIGUE',
      sym_nausea   AS 'NAUSEA',
      sym_insomnia AS 'INSOMNIA',
      sym_mood     AS 'MOOD',
      sym_appetite AS 'APPETITE',
      sym_gi       AS 'GI'
    )
  )
) u
JOIN visit v ON v.event_name = u.redcap_event_name;

COMMIT;