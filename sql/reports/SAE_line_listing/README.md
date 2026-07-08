# SAE Line Listing

## What this is
A Serious Adverse Event (SAE) Line Listing is a pharmacovigilance deliverable —
one line per serious event — submitted to the safety monitoring board, the
sponsor, and regulatory authorities. It is one of the most scrutinised outputs
of any trial.

## Why it matters in clinical work
Not every adverse event is serious. An event becomes an **SAE** when it meets a
defined seriousness criterion: death, life-threatening, hospitalisation,
persistent disability, congenital anomaly, or another medically important event.
SAEs trigger mandatory expedited reporting under ICH — the site must notify the
sponsor rapidly (typically within 24 hours of awareness), and onward reporting
to authorities follows defined windows (7 days for fatal/life-threatening, 15
for other serious events).

Two judgments make this listing more than a filter:

**Causality.** Every SAE must be assessed for its relationship to the study drug,
independent of its seriousness. This is the judgment-heavy core of
pharmacovigilance. The one SAE here — acute gastroenteritis requiring overnight
hospitalisation — is serious (it meets the hospitalisation criterion) but was
assessed as **unrelated** to dexamethasone: the timing, viral/food-borne clinical
picture, and absence of any plausible single-dose corticosteroid mechanism all
point away from the drug. A serious-but-unrelated event is still fully reported —
seriousness and causality are separate , and both are documented.

**Reporting timeliness.** The listing computes days from onset to each
notification (sponsor and ethics) so a reviewer can confirm ICH timelines were
met. Here: sponsor notified 1 day after onset, ethics 7 days — both well within
window.

## What the query does
Reads `adverse_event` (filtered to `is_sae = 1`), joins `enrollment` for cohort,
decodes CTCAE grade / causality / seriousness criterion to readable terms, and
computes the reporting intervals by subtracting the stored dates
(`sponsor_date − onset_date`). The date arithmetic works directly because these
are typed as real DATE columns in the core.

Pattern: **filter with clinical logic** — filter to serious events, then apply
pharmacovigilance decoding and derive the compliance intervals.
This makes all neccesary information visible at a glance.

## Source
- `adverse_event` (core) — event, grade, causality, seriousness, reporting dates
- `enrollment` (core) — cohort assignment

## The one SAE found
Volunteer ZA-CPT-P1-010 (Cohort 3, 8 mg): Grade 3 acute gastroenteritis,
overnight hospitalisation for IV rehydration, resolved in 48 hours, assessed
unrelated to study drug, reported to sponsor (1 day) and ethics (7 days) within
ICH timelines.