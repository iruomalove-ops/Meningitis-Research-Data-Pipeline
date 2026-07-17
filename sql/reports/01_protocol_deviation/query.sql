-- Protocol Deviation Listing — Phase 1 dexamethasone PK study
-- Source: src_review (core), joined to enrollment for cohort context.
-- Lists every protocol deviation with its sponsor/ethics reporting status.
-- Standard sponsor deliverable; evidences that deviations were escalated per protocol.
-- NOTE: reporting flags decoded inline (1->Yes/0->No) for readability. When the
--   codelist table is built (SDTM phase), these decodes will source from it.

SELECT
  sr.record_id AS subject,
  e.cohort     AS cohort,
  sr.deviation_details AS deviation,
  sr.src_meeting_date  AS reviewed_on,
  CASE sr.deviation_reported WHEN '1' THEN 'Yes' ELSE 'No' END AS reported_to_sponsor,
  CASE sr.deviation_ethics   WHEN '1' THEN 'Yes' ELSE 'No' END AS reported_to_ethics,
  sr.pi_escalation_signoff AS pi_signoff
FROM src_review sr
JOIN enrollment e ON sr.record_id = e.record_id
WHERE sr.deviation_any = '1'
ORDER BY sr.record_id;