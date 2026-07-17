-- Safety Lab Summary by Cohort — Phase 1 dexamethasone PK study
-- Source: v_lab_classified (analytics view: lab_result + reference range + Low/Normal/High)
-- CSR safety-lab deliverable for the SRC and Clinical Study Report.

-- ============================================================================
-- Component 1: Descriptive statistics per cohort x visit x analyte
-- ============================================================================
SELECT
  cohort,
  visit_label,
  lab_test,
  unit,
  COUNT(*)                    AS n,
  ROUND(AVG(lab_value), 2)    AS mean_value,
  MIN(lab_value)              AS min_value,
  MAX(lab_value)              AS max_value,
  SUM(CASE WHEN classification <> 'Normal' THEN 1 ELSE 0 END) AS n_out_of_range,
  SUM(CASE WHEN classification = 'Low'  THEN 1 ELSE 0 END)    AS n_low,
  SUM(CASE WHEN classification = 'High' THEN 1 ELSE 0 END)    AS n_high
FROM v_lab_classified
GROUP BY cohort, visit_label, lab_test, unit, visit_order
ORDER BY cohort, visit_order, lab_test;
-- ============================================================================
-- Component 2: Change from baseline, per subject x visit x analyte
-- ============================================================================
-- FIRST_VALUE window function fetches each subject's own screening value for the
-- same analyte, so every row can compute its change from that baseline.
-- PARTITION BY = the group within which to look (this subject, this analyte)
-- ORDER BY visit_order = so "first" means screening, the earliest visit.

WITH with_baseline AS (
  SELECT
    record_id,
    cohort,
    visit_label,
    visit_order,
    lab_test,
    lab_value,
    unit,
    classification,
    FIRST_VALUE(lab_value) OVER (
      PARTITION BY record_id, lab_test
      ORDER BY visit_order
    ) AS baseline_value
  FROM v_lab_classified
)
SELECT
  record_id,
  cohort,
  visit_label,
  lab_test,
  unit,
  baseline_value,
  lab_value                                   AS current_value,
  ROUND(lab_value - baseline_value, 2)        AS change_from_baseline,
  classification
FROM with_baseline
WHERE visit_label <> 'Screening'   -- baseline itself has no change to report
ORDER BY record_id, visit_order, lab_test;
-- ============================================================================
-- Component 3: Shift table — baseline classification -> post-dose classification
-- ============================================================================
-- Counts subject movements between reference-range categories. A Normal->High
-- shift is a drug effect; a High->High is a pre-existing finding. Endpoint counts
-- alone cannot distinguish them, which is why CSRs present shifts.
-- Long format: one row per cohort x visit x analyte x shift. Pivot for display.

WITH with_baseline_class AS (
  SELECT
    record_id,
    cohort,
    visit_label,
    visit_order,
    lab_test,
    classification,
    FIRST_VALUE(classification) OVER (
      PARTITION BY record_id, lab_test
      ORDER BY visit_order
    ) AS baseline_class
  FROM v_lab_classified
)
SELECT
  cohort,
  visit_label,
  lab_test,
  baseline_class || ' -> ' || classification AS shift,
  COUNT(*) AS n
FROM with_baseline_class
WHERE visit_label <> 'Screening'
GROUP BY cohort, visit_label, lab_test, baseline_class, classification, visit_order
ORDER BY cohort, visit_order, lab_test, shift;