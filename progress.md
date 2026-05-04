# Project Progress Log

A running diary of milestones, decisions, and lessons learned as the meningitis research data pipeline is built.

---

## 2026-05-04 — Phase 1 D1 Healthy Volunteer Eligibility instrument complete

### What was built
Completed the first REDCap instrument for the Phase 1 dexamethasone pharmacokinetic study in healthy volunteers. The instrument is fully functional in REDCap with all field types, validation rules, and branching logic in place.

### Final structure
- **30 fields** across five sections — site identification, demographics, inclusion criteria, exclusion criteria, eligibility conclusion
- **7 inclusion criteria** — age 18–55, BMI 18–35, good general health, normal hepatic function, normal renal function,willingness to comply with procedures, written informed consent
- **9 exclusion criteria** — including CYP3A4 drug interactions, recent medication use, diabetes, immunosuppression, pregnancy, corticosteroid allergy, smoking, excess alcohol, recent trial participation
- **3 branching logic rules** — pregnancy field shows only for female volunteers, screen failure reason and narrative show only when eligibility = screen failure
- **2 calculated fields** — age computed from date of birth, BMI computed from weight and height

### Key design decisions
- Kept the inclusion criterion "good general health" as a broad clinical judgement rather than adding redundant specific disease exclusions. A volunteer in good general health by definition does not have uncontrolled hypertension, peptic ulcer disease, or adrenal insufficiency. This avoids internal data contradictions that would generate monitor queries.
- Retained CYP3A4 drug interaction exclusion because dexamethasone is metabolised by this enzyme. Volunteers on CYP3A4 inducers or inhibitors would corrupt the pharmacokinetic curve.
- Used radio buttons coded 1=Yes, 0=No for all eligibility criteria to enable clean SQL queries and Power BI filters later.

### Tested
Form previewed and tested — branching logic fires correctly, calculated fields update live as inputs change, all required fields blocked saving when empty.

### Next milestone
Build D2 Demographics and Medical History instrument.
