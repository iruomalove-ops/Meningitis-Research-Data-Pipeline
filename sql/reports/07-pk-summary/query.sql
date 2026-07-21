-- PK Summary — per-volunteer parameters
SELECT * FROM v_pk_parameters ORDER BY cohort, record_id;

-- PK Summary — by cohort (the headline CSR table)
SELECT
  cohort,
  planned_dose_mg,
  COUNT(*) AS n,
  ROUND(AVG(cmax),2) AS mean_cmax,  ROUND(MIN(cmax),2) AS min_cmax,  ROUND(MAX(cmax),2) AS max_cmax,
  ROUND(AVG(auc_0_48h),2) AS mean_auc, ROUND(MIN(auc_0_48h),2) AS min_auc, ROUND(MAX(auc_0_48h),2) AS max_auc,
  ROUND(STDDEV(cmax)/AVG(cmax)*100,1) AS cmax_cv_pct
FROM v_pk_parameters
GROUP BY cohort, planned_dose_mg
ORDER BY cohort;