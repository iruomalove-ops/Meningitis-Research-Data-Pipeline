# Cross-instrument Reconciliation Report — Output

Phase 1 Dexamethasone PK Study (ZA-CPT-P1)
Data-quality audit across core instruments. 18 randomised volunteers checked.

## Result: COMPLETE — no unexplained gaps

All 18 randomised volunteers hold the expected number of records in every
checked instrument. Every status returned OK.

| Instrument | Expected per volunteer | Total expected | Status (all 18) |
|-----------|------------------------|----------------|-----------------|
| PK samples (pk_concentration) | 8 | 144 | OK |
| Vital signs (vital_sign) | 60 (6 vitals × 10 events) | 1,080 | OK |
| Lab results (lab_result) | 51 (17 analytes × 3 lab events) | 918 | OK |
| Diary symptoms (diary_symptom) | 28 (7 symptoms × 4 entries) | 504 | OK |
| SRC review (src_review) | 1 | 18 | OK |

Every per-volunteer count matched its expected value; the full 18-row listing is
uniform (all OK) and summarised here rather than repeated in full.

*Adverse events are reconciled separately (Report 5) — AE count is legitimately
variable per volunteer and cannot be checked by counting; it requires
cross-source line-by-line comparison.*