# AE Reconciliation (EDC vs Safety Database)

## What this is
AE reconciliation is the pharmacovigilance process of comparing the clinical
database (EDC) against the safety database (Argus, ARISg) line-by-line, to
confirm the two systems tell the same story about the same events. It is
performed before database lock and is a regulatory expectation.

## Why two systems exist — and why they diverge
The same adverse event is entered **twice, by different people, into different
systems**. The site enters it into the EDC as trial data; the pharmacovigilance
team enters it independently into the safety database for regulatory reporting.
Two independent entries of the same event will, inevitably, sometimes disagree —
a coder normalises a verbatim term, a reviewer assesses severity differently, a
date gets transcribed wrong, or an event fails to reach one system entirely.

This matters because the regulator sees the safety database and the analysis sees
the EDC. If they disagree, the trial tells two different stories about the same
patient event.

## The four reconciliation pillars
Every reportable event is compared on:

1. **Existence** — does the event appear in both systems? An event in one and not
   the other is the most serious finding. (This is why the query uses a FULL
   OUTER JOIN: an inner join would silently drop exactly the records you most
   need to catch.)
2. **Verbatim term** — do the systems describe the same event? "Severe headache"
   vs "Cephalea" is the classic divergence.
3. **Onset and resolution dates** — do the dates match? Dates drive reporting
   clocks.
4. **Severity and causality** — do grade and drug-relationship agree? These drive
   reportability, so disagreement is material.

## Design note — pairing vs comparing
Records are paired on `record_id` alone, not on term or date. You cannot pair on
a field you are also checking for discrepancies — pairing on onset date would
break the pairing for a case whose date is the discrepancy, and it would surface
as two "missing" records instead of one date mismatch. Pair on a stable
identifier; compare the volatile fields.

The report lists **every** differing pillar per case, not just the first, because
the safety team needs the complete list to resolve a case.

## Scope — which events the safety database holds
Real safety databases hold the reportable subset, not every minor AE. Entry rule
applied here: **serious (SAE) OR Grade 3+ OR a related event of special interest**
(e.g. a probably-related hepatic signal). This is deliberately multi-dimensional —
causality alone doesn't decide entry, and all SAEs enter regardless of causality.

## Honest framing of this artifact
This project has **one** database. There is no independent safety system to
reconcile against. The safety extract (`safety_db_extract_argus.sql`) is a
**constructed simulation** of what an Argus extract would contain, with four
discrepancies **deliberately seeded** — one per pillar — so the reconciliation
can be demonstrated firing. The discrepancies are not organic findings; they are
a test harness. This is stated in the build script and in the output.

## Source
- `adverse_event` (core) — the EDC side
- `safety_db_extract_argus` — the simulated safety extract