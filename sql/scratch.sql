SELECT COUNT(*) AS total, COUNT(race) AS race_populated FROM subject;
SELECT constraint_name, constraint_type FROM user_constraints WHERE table_name = 'SUBJECT';
SELECT subject_id, record_id, race FROM subject WHERE record_id IN ('ZA-CPT-P1-001','ZA-CPT-P1-010');
SELECT constraint_name, constraint_type, search_condition
FROM user_constraints
WHERE table_name = 'SUBJECT';