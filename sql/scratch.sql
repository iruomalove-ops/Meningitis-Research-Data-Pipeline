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