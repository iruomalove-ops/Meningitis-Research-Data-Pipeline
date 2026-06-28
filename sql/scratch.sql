SELECT COUNT(*) AS total, COUNT(race) AS race_populated FROM subject;
SELECT constraint_name, constraint_type FROM user_constraints WHERE table_name = 'SUBJECT';
SELECT subject_id, record_id, race FROM subject WHERE record_id IN ('ZA-CPT-P1-001','ZA-CPT-P1-010');
SELECT constraint_name, constraint_type, search_condition
FROM user_constraints
WHERE table_name = 'SUBJECT';
=======
-- enrollment: one row per enrolled volunteer (28), incl. reserve.
-- Derived from staging D3a. Randomisation facts only; dose facts live in dosing.
SELECT enrolment_status, COUNT(*) FROM enrollment GROUP BY enrolment_status;
SELECT table_name FROM user_tables WHERE table_name = 'ENROLLMENT';
SELECT constraint_name, constraint_type FROM user_constraints WHERE table_name = 'ENROLLMENT';
INSERT INTO enrollment (record_id, enrolment_status) VALUES ('ZA-CPT-P1-999', 'Randomised');
=======
-- dosing: one row per DOSED volunteer (18). Exposure facts only.
-- Derived from staging D3a, filtered to Randomised (reserves were never dosed).
SELECT COUNT(*) FROM dosing;
SELECT cohort_open_date, planned_dose_mg, dose_per_kg FROM dosing FETCH FIRST 3 ROWS ONLY;
SELECT constraint_name, constraint_type FROM user_constraints WHERE table_name = 'DOSING';
SELECT planned_dose_mg, COUNT(*) FROM dosing GROUP BY planned_dose_mg ORDER BY planned_dose_mg;
=======
-- eligibility: one row per screened volunteer (100). The screening checklist + verdict.
-- Derived from staging D1. Demographics live on subject; not repeated here.
SELECT COUNT(*) FROM eligibility;
SELECT eligibility_determination, COUNT(*) FROM eligibility GROUP BY eligibility_determination;
SELECT constraint_name, constraint_type FROM user_constraints WHERE table_name = 'ELIGIBILITY';
=======
--medical_history: one row per screened volunteer (100). The medical history checklist.
-- Derived from staging D2. Demographics live on subject; not repeated here.
SELECT COUNT(*) FROM medical_history;
SELECT COUNT(*) AS all_28 FROM medical_history m JOIN subject s ON m.record_id = s.record_id;
SELECT constraint_name, constraint_type FROM user_constraints WHERE table_name = 'MEDICAL_HISTORY';
=======
-- visit: the event dimension. One row per trial event (11).
-- Authored reference table, not derived from staging.
-- hours_from_dose & nominal_day are NOMINAL (protocol-planned) timing; dosing = hour 0.
-- Actual per-draw timing lives in D4 (actual_datetime), not here.
-- visit_category: PK_SCHEDULE (intensive PK sampling grid) vs CLINICAL_VISIT (standalone visit).
SELECT event_name, hours_from_dose, nominal_day, visit_category
FROM visit ORDER BY sort_order;
SELECT visit_category, COUNT(*) FROM visit GROUP BY visit_category;
=======
-- pk_concentration: the PK finding. One row per volunteer per timepoint (144).
-- Derived from staging D4. Sample chain-of-custody lives in sample_handling.
-- D4 carries a numeric timepoint code, not an event name; the CASE bridges
--   code -> visit.event_name so this fact can FK to the visit dimension.
SELECT COUNT(*) FROM pk_concentration;
SELECT v.label, COUNT(*)
FROM pk_concentration p JOIN visit v ON p.visit_id = v.visit_id
GROUP BY v.label ORDER BY MIN(v.sort_order);
-- sample_handling: PK sample chain of custody. One row per volunteer per timepoint (144).
-- Derived from staging D4. The PK finding (concentration) lives in pk_concentration.
-- Same timepoint-code -> visit.event_name bridge as pk_concentration.
SELECT COUNT(*) FROM sample_handling;
SELECT COUNT(*) AS paired
FROM pk_concentration p
JOIN sample_handling s
  ON p.record_id = s.record_id AND p.visit_id = s.visit_id;
=======
-- unpivot verififcation: one row per volunteer per timepoint (144). The unpivoted PK finding.
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
);
=======
-- vital_sign: long findings table. One row per volunteer per visit per vital (≈ 18×10×6).
-- Derived from staging D5 by UNPIVOT (wide vitals columns -> rows).
SELECT COUNT(*) FROM vital_sign;
SELECT vs_test, COUNT(*) FROM vital_sign GROUP BY vs_test ORDER BY vs_test;
SELECT v.label, vs.vs_value
FROM vital_sign vs JOIN visit v ON vs.visit_id = v.visit_id
WHERE vs.record_id = 'ZA-CPT-P1-080' AND vs.vs_test = 'SBP'
ORDER BY v.sort_order;
=======
-- lab_result: long findings table. One row per volunteer per lab visit per analyte (≈ 18×3×17 = 918).
-- Derived from staging D5 by UNPIVOT. Labs populate at only 3 events; UNPIVOT skips the NULL (vitals-only) events automatically.
SELECT COUNT(*) FROM lab_result;
SELECT lab_test, COUNT(*) FROM lab_result GROUP BY lab_test ORDER BY lab_test;
SELECT v.label, lr.lab_value
FROM lab_result lr JOIN visit v ON lr.visit_id = v.visit_id
WHERE lr.record_id = 'ZA-CPT-P1-080' AND lr.lab_test = 'ALT'
ORDER BY v.sort_order;
=======
-- adverse_event: event fact. One row per real AE (23). Already event-shaped — no unpivot.
-- Derived from staging D6, filtered to ae_any=1. The 67 "no AE this visit" placeholders stay in staging.
SELECT COUNT(*) FROM adverse_event;
SELECT record_id, ae_term, ae_ctcae_grade, is_sae FROM adverse_event WHERE is_sae = '1' OR record_id = 'ZA-CPT-P1-080';
SELECT ae_any, COUNT(*) FROM d6_adverse_events_and_saes GROUP BY ae_any;

SELECT COUNT(*) AS d6_real_aes
FROM d6_adverse_events_and_saes
WHERE ae_any = '1';

SELECT COUNT(*) AS after_join
FROM d6_adverse_events_and_saes d6
JOIN visit v ON v.event_name = d6.redcap_event_name
WHERE d6.ae_any = '1';

SELECT record_id, ae_term, ae_ctcae_grade, ae_relatedness, is_sae, sae_criterion
FROM adverse_event
WHERE is_sae = '1' OR record_id = 'ZA-CPT-P1-080'
ORDER BY record_id;
=======
---- diary_symptom: long findings table. One row per volunteer per diary visit per symptom (≈ 72×7 = 504).
-- Derived from staging D7 by UNPIVOT. 7 rated symptoms on a 0-3 severity scale.
SELECT COUNT(*) FROM diary_symptom;
SELECT symptom, COUNT(*) FROM diary_symptom GROUP BY symptom ORDER BY symptom;
SELECT v.label, ds.symptom, ds.severity
FROM diary_symptom ds JOIN visit v ON ds.visit_id = v.visit_id
WHERE ds.record_id = 'ZA-CPT-P1-010' AND ds.symptom IN ('NAUSEA','GI')
ORDER BY v.sort_order, ds.symptom;