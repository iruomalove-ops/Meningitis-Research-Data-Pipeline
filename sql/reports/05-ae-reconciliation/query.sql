-- AE Reconciliation — EDC (core adverse_event) vs simulated Argus safety extract
-- Phase 1 dexamethasone PK study.
-- Line-by-line comparison on four cross-system pillars:
--   (1) existence  (2) verbatim/PT term  (3) onset date  (4) CTCAE grade
-- Safety extract is SIMULATED with seeded discrepancies (see build script).
-- Reports EVERY differing pillar per record (a record with two mismatches shows
--   two findings), which is how real reconciliation lists discrepancies.

WITH edc AS (
  -- EDC side: the reportable subset, by the safety-DB entry rule
  SELECT record_id, ae_term, ae_onset_date, ae_ctcae_grade
  FROM adverse_event
  WHERE is_sae = '1'
     OR ae_ctcae_grade = '3'
     OR (ae_term = 'Transaminase elevation' AND ae_relatedness = '4')
),
paired AS (
  SELECT
    COALESCE(e.record_id, s.record_id) AS subject,
    e.record_id AS edc_id, s.record_id AS saf_id,
    e.ae_term, s.ae_verbatim,
    e.ae_onset_date, s.onset_date,
    e.ae_ctcae_grade AS edc_grade, s.ctcae_grade AS saf_grade
  FROM edc e
  FULL OUTER JOIN safety_db_extract_argus s ON e.record_id = s.record_id
)
-- Pillar 1: existence
SELECT subject, 'EXISTENCE' AS pillar,
       'Reportable EDC event not in safety DB' AS finding
FROM paired WHERE saf_id IS NULL
UNION ALL
SELECT subject, 'EXISTENCE',
       'Safety DB event not in EDC'
FROM paired WHERE edc_id IS NULL
UNION ALL
-- Pillar 2: verbatim term
SELECT subject, 'TERM',
       'EDC "'||ae_term||'" vs SAFETY "'||ae_verbatim||'"'
FROM paired WHERE edc_id IS NOT NULL AND saf_id IS NOT NULL AND ae_term <> ae_verbatim
UNION ALL
-- Pillar 3: onset date
SELECT subject, 'ONSET DATE',
       'EDC '||TO_CHAR(ae_onset_date,'DD-Mon-YY')||' vs SAFETY '||TO_CHAR(onset_date,'DD-Mon-YY')
FROM paired WHERE edc_id IS NOT NULL AND saf_id IS NOT NULL AND ae_onset_date <> onset_date
UNION ALL
-- Pillar 4: CTCAE grade
SELECT subject, 'GRADE',
       'EDC Grade '||edc_grade||' vs SAFETY Grade '||saf_grade
FROM paired WHERE edc_id IS NOT NULL AND saf_id IS NOT NULL AND edc_grade <> saf_grade
ORDER BY 1, 2;