-- ============================================================================
-- v_pk_parameters — analytics view: per-volunteer PK parameters
-- ============================================================================
-- One row per volunteer: Cmax, Tmax, and AUC(0-48h). Computes the three
-- descriptive PK parameters once, for consumption by the PK Summary report and
-- Power BI. BLQ set to 0 (pre-dose has no drug; PK convention).
-- Half-life (t½) is intentionally absent — it requires log-linear regression on
--   the terminal elimination phase, which belongs in specialised PK software.
-- AUC is by the linear trapezoidal rule (LEAD fetches the next sample to form
--   each trapezoid); it is AUC over the sampling window (0-48h), not AUC_inf.
-- ============================================================================

CREATE OR REPLACE VIEW v_pk_parameters AS
WITH samples AS (
  SELECT
    p.record_id,
    v.hours_from_dose AS t_hours,
    CASE WHEN p.blq = '1' THEN 0 ELSE p.plasma_concentration END AS conc
  FROM pk_concentration p
  JOIN visit v ON p.visit_id = v.visit_id
),
auc_calc AS (
  -- trapezoidal AUC per volunteer
  SELECT
    record_id,
    SUM( 0.5 * (t_next - t_hours) * (conc + conc_next) ) AS auc_0_48h
  FROM (
    SELECT
      record_id, t_hours, conc,
      LEAD(t_hours) OVER (PARTITION BY record_id ORDER BY t_hours) AS t_next,
      LEAD(conc)    OVER (PARTITION BY record_id ORDER BY t_hours) AS conc_next
    FROM samples
  )
  WHERE t_next IS NOT NULL
  GROUP BY record_id
),
cmax_tmax AS (
  -- peak concentration and the time it occurred, per volunteer
  SELECT record_id, cmax, tmax_hours
  FROM (
    SELECT
      p.record_id,
      p.plasma_concentration AS cmax,
      v.hours_from_dose      AS tmax_hours,
      ROW_NUMBER() OVER (PARTITION BY p.record_id ORDER BY p.plasma_concentration DESC) AS rn
    FROM pk_concentration p
    JOIN visit v ON p.visit_id = v.visit_id
  )
  WHERE rn = 1
)
SELECT
  ct.record_id,
  e.cohort,
  d.planned_dose_mg,
  ct.cmax,
  ct.tmax_hours,
  ROUND(a.auc_0_48h, 2) AS auc_0_48h
FROM cmax_tmax ct
JOIN auc_calc a   ON ct.record_id = a.record_id
JOIN enrollment e ON ct.record_id = e.record_id
JOIN dosing d     ON ct.record_id = d.record_id;