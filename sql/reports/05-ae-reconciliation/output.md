# AE Reconciliation — Output

Phase 1 Dexamethasone PK Study (ZA-CPT-P1)
EDC (`adverse_event`) reconciled against a **simulated Argus-style safety database extract**.
Reportable events only (serious OR Grade 3+ OR related event of special interest).

> **Note:** the safety extract is a constructed demonstration artifact with
> discrepancies deliberately seeded to show the reconciliation firing. These are
> not organic findings — see the README and the extract build script.

## Result: 4 discrepancies across 3 cases

| Subject | Pillar | Finding |
|---------|--------|---------|
| ZA-CPT-P1-010 | TERM | EDC "Acute gastroenteritis" vs SAFETY "Gastroenteritis, viral" |
| ZA-CPT-P1-056 | GRADE | EDC Grade 3 vs SAFETY Grade 2 |
| ZA-CPT-P1-056 | ONSET DATE | EDC 09-Jun-25 vs SAFETY 10-Jun-25 |
| ZA-CPT-P1-080 | EXISTENCE | Reportable EDC event not in safety DB |

## Interpretation

**ZA-CPT-P1-010 — term mismatch.** The safety database holds a normalised/coded
term where the EDC holds the site's verbatim. Common and usually benign, but must
be documented — the two systems must be traceable to the same event.

**ZA-CPT-P1-056 — grade and date mismatch.** Two discrepancies on one case. The
grade difference is the material one: Grade 3 (severe) in the EDC vs Grade 2
(moderate) in safety. Severity drives reportability, so the systems must agree
before lock. The one-day onset difference is a transcription divergence.

**ZA-CPT-P1-080 — missing from safety DB.** The highest-severity finding. A
probably-related transaminase elevation — a hepatic signal of special interest —
exists in the EDC but was never entered into the safety database. This is exactly
what AE reconciliation exists to catch: a reportable event that never reached
the system responsible for regulatory reporting.

*Each discrepancy would be raised as a query, investigated against source
documents, and resolved in one or both systems before database lock.*