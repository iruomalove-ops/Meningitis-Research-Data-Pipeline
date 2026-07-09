# Subject Enrolment / Disposition Report

## What this is
A recruitment-tracking deliverable produced weekly during active enrolment,
structured according to CONSORT (the Consolidated Standards of Reporting Trials)
— the international standard for reporting subject disposition. It answers the
three questions every study manager and sponsor asks about recruitment.

## Why it matters in clinical work
Recruitment is where most trials struggle. This report tracks three things
CONSORT requires:

**The screening funnel** — how many were assessed, how many passed, how many
randomised. The narrowing from screened to randomised is the core recruitment
metric; a funnel that's too wide (few passing screening) signals eligibility
criteria that may be too strict or a recruitment source that's poorly matched.

**Enrolment by cohort** — whether the dose groups are filling evenly. In a
dose-escalation study the cohorts must fill in order and in balance; this
confirms 6 per cohort with the sentinel slots filled.

**Screen-failure reasons** — CONSORT explicitly requires the reasons subjects
were not recruited. This is not just bookkeeping: if most failures cluster on
one criterion (say, BMI out of range), that's actionable intelligence — the
recruitment strategy or the criterion itself may need review.

Sentinel *selection methodology* is deliberately excluded — that belongs in the
randomisation report and the statistical analysis plan, not a disposition
report. Keeping each deliverable to its proper scope is itself good practice.

## What the query does
Three aggregations. (1) A stage funnel via UNION ALL of stage counts. (2) A
GROUP BY cohort with a conditional SUM to count sentinels within each group.
(3) A GROUP BY screen_failure_reason over the ineligible subjects.

Pattern: **aggregation with grouping and counting** — moving from listing rows
(Reports 1–2) to summarising them into counts by group.

## Source
- `subject` (core) — all 100 screened
- `eligibility` (core) — determination and screen-failure reason
- `enrollment` (core) — randomisation status, cohort, sentinel flag

## Standard followed
CONSORT flow (assessed → eligible → randomised → allocated), disposition by
arm, and reasons for non-recruitment.