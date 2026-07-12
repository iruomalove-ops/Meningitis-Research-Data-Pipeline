# Cross-instrument Reconciliation Report

## What this is
A data-quality audit that verifies every dosed volunteer has the complete set of
records they should have across every downstream instrument. It is an internal
deliverable a data manager runs before database lock and before any analysis —
you cannot analyse data you cannot first prove is complete.

## Why it matters in clinical work
Analysis assumes completeness. If a volunteer is missing PK samples or lab
results and no one notices, the PK curve or safety summary is silently wrong.
Reconciliation is the check that catches this before it propagates. It answers:
does what's in the database match what the protocol says should have been
collected?

## How discrepancies are handled — the methodology
When actual counts match expected, the volunteer reconciles (OK). When they
don't, the count is only the trigger — the real work is investigation:

1. **Detect** — the query flags the shortfall (e.g. 7 PK samples where 8 are
   expected).
2. **Source** — find why the record is absent. A missing record is never taken
   at face value; it has a cause that must be identified.
3. **Classify** — the cause determines whether it's a true discrepancy or an
   accounted-for absence:
   - **Documented absence** — the record exists but marks itself not-collected
     with a reason (e.g. a sample with `sample_collected = 0`,
     `missed_reason = 'haemolysed in transit'`), or the volunteer withdrew
     consent (a disposition record explains all downstream gaps). These are
     expected absences, reconciled and closed.
   - **Genuine discrepancy** — a record that should exist, doesn't, and has no
     documenting reason. This is a real data gap, flagged for the site to
     resolve.
4. **Record** — the finding and its resolution are documented, not silently
   dropped. A blank you cannot explain is a query waiting to happen.

The principle: a missing record and a missing-record-with-a-reason are different
things. Reconciliation exists to tell them apart.

## Scope
This report reconciles the instruments with a fixed expected count per volunteer
(PK, vitals, labs, diary, SRC review). Adverse events are excluded here because
AE count is legitimately variable — reconciling AEs requires a different method
(cross-source line-by-line comparison on subject, verbatim term, dates, and
grade/causality) and is handled as its own report.

## This dataset
Clean — all 18 volunteers complete, zero gaps. A correct reconciliation result.
The check is written to flag and classify any shortfall; on this data it
confirms completeness.

## What the query does
For each randomised volunteer, counts records in each core instrument via
correlated subqueries and compares against the expected value with a computed
status column (OK / CHECK), so the check is visible in every row rather than
hidden until a failure.

Pattern: **cross-table joins and completeness checks** — a CTE gathering
per-volunteer counts, reconciled against expected values.

## Source
Core instruments: pk_concentration, vital_sign, lab_result, diary_symptom,
src_review — plus enrollment for the randomised cohort.