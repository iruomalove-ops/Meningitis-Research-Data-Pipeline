-- Subject Enrolment / Disposition Report — Phase 1 dexamethasone PK study
-- Source: subject, eligibility, enrollment (core).
-- Recruitment-tracking deliverable, produced weekly during active enrolment.
-- Structured per CONSORT: screening funnel, enrolment by cohort, and
--   screen-failure reasons. Sentinel selection methodology is out of scope
--   (belongs in the randomisation/SAP documentation, not a disposition report).

-- (1) Screening funnel — how recruitment narrowed through each stage
SELECT 'Screened'   AS stage, COUNT(*) AS n FROM subject
UNION ALL
SELECT 'Eligible',   COUNT(*) FROM eligibility WHERE eligibility_determination = '1'
UNION ALL
SELECT 'Randomised', COUNT(*) FROM enrollment  WHERE enrolment_status = 'Randomised'
UNION ALL
SELECT 'Reserve',    COUNT(*) FROM enrollment  WHERE enrolment_status = 'Reserve'
ORDER BY 1;

-- (2) Enrolment by cohort — are the dose groups balanced?
SELECT
  e.cohort AS cohort,
  COUNT(*) AS randomised,
  SUM(CASE WHEN e.is_sentinel = '1' THEN 1 ELSE 0 END) AS sentinels
FROM enrollment e
WHERE e.enrolment_status = 'Randomised'
GROUP BY e.cohort
ORDER BY e.cohort;

-- (3) Screen failures by reason — CONSORT requires reasons for non-recruitment
-- Reason codes decoded per the REDCap data dictionary (screen_failure_reason field).
SELECT
  CASE sr.screen_failure_reason
    WHEN '1' THEN 'Inclusion criterion not met'
    WHEN '2' THEN 'Exclusion criterion present'
    WHEN '3' THEN 'Abnormal screening labs'
    WHEN '4' THEN 'BMI out of range'
    WHEN '5' THEN 'Age out of range'
    WHEN '6' THEN 'Prohibited medication'
    WHEN '7' THEN 'Volunteer withdrew consent'
    WHEN '8' THEN 'Other'
  END AS reason,
  COUNT(*) AS n
FROM eligibility sr
WHERE sr.eligibility_determination = '2'
GROUP BY sr.screen_failure_reason
ORDER BY n DESC;