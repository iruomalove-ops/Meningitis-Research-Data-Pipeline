-- ============================================================================
-- v_lab_classified — analytics view: lab results with reference range + classification
-- ============================================================================
-- The first view of the analytics tier. Derives what the core deliberately does
-- not store: each lab result's applicable reference range and its Low/Normal/High
-- classification. Consumers: the Safety Lab Summary report (all components) and
-- Power BI later — written once here so the resolution logic has one home.
--
-- Two resolution rules live in this view:
--   sex-specific ranges — lab_reference.sex_code is 'ALL' for tests that don't
--     vary by sex; the OR in the join is what makes 'ALL' a wildcard (Oracle has
--     no built-in notion of it). HB and creatinine resolve to the sex row.
--   glucose fasting     — the glucose range depends on fasting state, resolved
--     from lab_result.fasting_status so a rebuilt database classifies correctly
--     from its own data rather than a hardcoded assumption.
-- ============================================================================

CREATE OR REPLACE VIEW v_lab_classified AS
SELECT
  lr.record_id,
  lr.visit_id,
  v.label       AS visit_label,
  v.sort_order  AS visit_order,
  e.cohort,
  s.sex_at_birth,
  lr.lab_test,
  lr.lab_value,
  lr.fasting_status,
  ref.unit,
  ref.range_low,
  ref.range_high,
  CASE
    WHEN lr.lab_value < ref.range_low  THEN 'Low'
    WHEN lr.lab_value > ref.range_high THEN 'High'
    ELSE 'Normal'
  END AS classification
FROM lab_result lr
JOIN subject s    ON lr.record_id = s.record_id
JOIN visit   v    ON lr.visit_id  = v.visit_id
JOIN enrollment e ON lr.record_id = e.record_id
JOIN lab_reference ref
  ON ref.lab_test = CASE
       WHEN lr.lab_test <> 'GLUCOSE'            THEN lr.lab_test
       WHEN lr.fasting_status = '1'             THEN 'GLUCOSE_FASTED'
       WHEN lr.fasting_status = '0'             THEN 'GLUCOSE_NONFASTED'
       ELSE NULL   -- fasting status unknown/NA: no range resolves, row surfaces as unclassified
     END
 AND (ref.sex_code = s.sex_at_birth OR ref.sex_code = 'ALL')