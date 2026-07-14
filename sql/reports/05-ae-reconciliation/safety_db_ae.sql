-- ============================================================================
-- safety_db_extract_argus — SIMULATED safety-database extract (Argus-style)
-- ============================================================================
-- *** DEMONSTRATION ARTIFACT — a simulated EXTRACT from an Argus-style safety
-- database, NOT organic trial data and NOT a live system. ***
--
-- In real pharmacovigilance, the safety team pulls an EXTRACT (a file) from the
-- safety database (Argus/ARISg) and reconciles it against the EDC line-by-line.
-- This project has one database; this extract is constructed to demonstrate that
-- reconciliation process. It holds the reportable subset only (serious OR grade
-- 3+ OR a related event of special interest).
--
-- FOUR DISCREPANCIES DELIBERATELY SEEDED (constructed, not real findings):
--   Verbatim/PT term : 010 — "Gastroenteritis, viral" vs EDC "Acute gastroenteritis"
--   Onset date       : 056 — off by one day
--   CTCAE grade      : 056 — Grade 2 vs EDC Grade 3
--   Existence        : 080 transaminase elevation ABSENT (reportable event that
--                      never reached the safety database)
-- ============================================================================

DROP TABLE safety_db_extract_argus CASCADE CONSTRAINTS;

CREATE TABLE safety_db_extract_argus (
  safety_case_id           VARCHAR2(20),    -- Argus case number
  initial_or_followup      VARCHAR2(15),    -- Initial / Follow-up (cases version as they update)
  receipt_date             DATE,            -- when safety dept received the case
  record_id                VARCHAR2(50),    -- subject; soft link to EDC
  ae_verbatim              VARCHAR2(200),   -- verbatim term as reported
  meddra_pt                VARCHAR2(100),   -- MedDRA Preferred Term (coded)
  onset_date               DATE,
  ctcae_grade              VARCHAR2(10),
  investigator_relatedness VARCHAR2(20),    -- investigator's causality
  sponsor_relatedness      VARCHAR2(20),    -- sponsor causality (can differ from investigator)
  seriousness_flag         VARCHAR2(5),     -- Yes / No
  seriousness_reason       VARCHAR2(60),    -- Hospitalisation / Death / Medically important / etc.
  outcome                  VARCHAR2(30),    -- Recovered / Recovering / Fatal / Unknown
  action_taken             VARCHAR2(40),    -- Drug withdrawn / Dose reduced / None / etc.
  safety_extract_id        NUMBER GENERATED ALWAYS AS IDENTITY
);

ALTER TABLE safety_db_extract_argus ADD (
  CONSTRAINT pk_safety_db_extract PRIMARY KEY (safety_extract_id)
);

-- 010 SAE gastroenteritis — TERM seeded different (verbatim + PT), otherwise matches
INSERT INTO safety_db_extract_argus (
  safety_case_id, initial_or_followup, receipt_date, record_id,
  ae_verbatim, meddra_pt, onset_date, ctcae_grade,
  investigator_relatedness, sponsor_relatedness,
  seriousness_flag, seriousness_reason, outcome, action_taken)
VALUES (
  'SAF-2025-0001', 'Initial', TO_DATE('2025-07-06','YYYY-MM-DD'), 'ZA-CPT-P1-010',
  'Gastroenteritis, viral', 'Gastroenteritis viral', TO_DATE('2025-07-05','YYYY-MM-DD'), '3',
  'Unrelated', 'Unrelated',
  'Yes', 'Hospitalisation or prolongation', 'Recovered without sequelae', 'Not applicable');

-- 056 Grade 3 fatigue — DATE seeded +1 day, GRADE seeded 2 (vs EDC 3)
INSERT INTO safety_db_extract_argus (
  safety_case_id, initial_or_followup, receipt_date, record_id,
  ae_verbatim, meddra_pt, onset_date, ctcae_grade,
  investigator_relatedness, sponsor_relatedness,
  seriousness_flag, seriousness_reason, outcome, action_taken)
VALUES (
  'SAF-2025-0002', 'Initial', TO_DATE('2025-06-11','YYYY-MM-DD'), 'ZA-CPT-P1-056',
  'Fatigue', 'Fatigue', TO_DATE('2025-06-10','YYYY-MM-DD'), '2',
  'Possibly related', 'Possibly related',
  'No', NULL, 'Recovered without sequelae', 'None');

-- 080 transaminase elevation — DELIBERATELY OMITTED (missing-record discrepancy)

COMMIT;