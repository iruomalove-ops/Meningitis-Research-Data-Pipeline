-- SAE Line Listing — Phase 1 dexamethasone PK study
-- Source: adverse_event (core, is_sae=1), joined to subject + enrollment.
-- Pharmacovigilance deliverable for the safety monitoring board and regulators.
-- Shows causality, seriousness criterion, and computed ICH reporting intervals.

SELECT
  ae.record_id AS subject,
  e.cohort     AS cohort,
  ae.ae_term   AS event,
  ae.ae_ctcae_grade AS ctcae_grade,
  CASE ae.ae_relatedness
    WHEN '1' THEN 'Unrelated' WHEN '2' THEN 'Unlikely' WHEN '3' THEN 'Possibly'
    WHEN '4' THEN 'Probably'  WHEN '5' THEN 'Definitely' END AS causality,
  CASE ae.sae_criterion
    WHEN '1' THEN 'Death' WHEN '2' THEN 'Life-threatening'
    WHEN '3' THEN 'Hospitalisation' WHEN '4' THEN 'Disability'
    WHEN '5' THEN 'Congenital anomaly' WHEN '6' THEN 'Other important' END AS sae_criterion,
  ae.ae_onset_date AS onset,
  ae.ae_resolution_date AS resolved,
  ae.sae_reported_sponsor_date AS sponsor_notified,
  ae.sae_reported_sponsor_date - ae.ae_onset_date AS days_onset_to_sponsor,
  ae.sae_reported_ethics_date  AS ethics_notified,
  ae.sae_reported_ethics_date  - ae.ae_onset_date AS days_onset_to_ethics,
  ae.ae_pi_signoff AS pi_signoff
FROM adverse_event ae
JOIN enrollment e ON ae.record_id = e.record_id
WHERE ae.is_sae = '1'
ORDER BY ae.record_id;