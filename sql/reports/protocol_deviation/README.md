# Protocol Deviation Listing

## What this is
A Protocol Deviation Listing documents every departure from the approved study
protocol during a clinical trial. It is a standard sponsor deliverable and a
routine output reviewed by monitors, the sponsor, and the ethics committee.

## Why it matters in clinical work
Protocol deviations are inevitable in real trials — a missed assessment window,
an out-of-schedule visit, a procedure done slightly out of order. What matters
to regulators is not that deviations never happen, but that every one is
**captured, classified, and reported** through the correct channels. This
listing is the evidence of that discipline: it shows each deviation was
recorded and escalated to the sponsor and ethics committee as required.

A trial with zero documented deviations is more suspicious than one with a few
minor ones honestly logged — it usually means deviations occurred but weren't
caught. This study shows one minor, properly-reported timing deviation across
18 volunteers, which is a realistic and healthy result.

## What the query does
Reads the `src_review` core table (the SRC safety-review record, which carries
the deviation fields), filters to volunteers where `deviation_any = 1`, and
joins `enrollment` to show which dose cohort the deviation occurred in. The
sponsor and ethics reporting flags are decoded to Yes/No for readability.

Pattern: **filter and select** — the foundational reporting pattern. Isolate
the rows that meet a condition, present the fields the deliverable needs.

## Source
- `src_review` (core) — deviation details, review date, reporting status, PI sign-off
- `enrollment` (core) — cohort assignment

## The one deviation found
Volunteer ZA-CPT-P1-056 (Cohort 2, 4 mg): a T+1h vital-signs check captured 15
minutes late. Minor, no safety or data-integrity impact, reported to sponsor and
ethics.