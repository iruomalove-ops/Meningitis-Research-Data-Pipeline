# Meningitis Research Pipeline

A clinical data engineering portfolio documenting the transition from registered nursing to clinical data management. Built as a two-phase journey toward a Phase 2 trial of dexamethasone combined with a MenB vaccine in meningitis patients. This repository houses the Phase 1 stepping-stone (complete simulation phase, downstream work in progress) and points toward the Phase 2 work ahead.

## Phase 1 — Dexamethasone dose escalation in healthy volunteers

A simulated first-in-human Phase 1 dose escalation trial of IV dexamethasone, built end-to-end from CRF design to data simulation to analysis. This is the warmup project, scoped deliberately to a single-agent Phase 1 because it is my first end-to-end pipeline build.

### What this phase demonstrates

Seven REDCap CRF instruments designed against real Phase 1 trial conventions, with branching logic, repeating events, and cross-instrument validation. Programmatic data simulation in Python producing 660 simulated records across 18 randomised volunteers and a 100-volunteer screening pool. Cross-instrument narrative consistency where two engineered safety findings thread coherently across labs, adverse events, volunteer diary, and SRC safety review. Architectural discipline including disk-based cast assignment files that maintain single-source-of-truth across script boundaries.

### Trial design at a glance

Three dose cohorts of six randomised volunteers each, dosed at 2mg, 4mg, and 8mg IV dexamethasone. Sentinel dosing in each cohort. PK sampling at 8 timepoints across 48 hours using a one-compartment IV model with published dexamethasone constants. Safety labs at three timepoints with full CBC, liver function, renal function, and electrolytes. Adverse events captured at five clinical check-ins. Volunteer self-reported symptom diary at four assessment events. SRC safety review at Day 21 for each cohort's escalation decision.

### Engineered safety narrative

One volunteer designated as the "high responder" in the 8mg cohort shows above-cohort response at T+48h across glucose, neutrophilia, and potassium, with a Grade 1 ALT elevation emerging at Day 7. One separately selected volunteer experiences acute gastroenteritis requiring overnight hospitalisation between Day 3 and Day 5, formally documented as an SAE but adjudicated as unrelated to study drug. Both narratives thread consistently across D5 labs, D6 AEs, D7 diary, and D3b SRC review, with the same record_ids referenced in each instrument's data.

### Tools

REDCap for CRF design and electronic data capture. Python for data simulation and analysis. SQL for relational schema and query work. Power BI for clinical dashboards. CDISC SDTM standards for regulatory-grade data structure.

## Current status

| Component | Status |
|---|---|
| Phase 1 REDCap CRF design — 7 instruments | Complete |
| Phase 1 simulation scripts — 7 Python files | Complete |
| Phase 1 simulated dataset — 660 records | Complete |
| Cross-instrument narrative consistency | Complete |
| SQL pipeline and relational schema | In progress |
| Power BI dashboards | Planned |
| SDTM mapping capstone | Planned |
| Phase 2 combination trial in patients | Planned (next project, separate repository) |

## Repository structure
meningitis-research-pipeline/
│
├── README.md                          # This document
├── PROGRESS.md                        # Development journal — design decisions and reasoning
│
├── phase1-dexamethasone-pk/
│   ├── redcap/
│   │   ├── crf-codebook.pdf           # Exported REDCap codebook for all 7 instruments
│   │   └── data-dictionary.csv        # REDCap data dictionary
│   ├── python/
│   │   ├── simulate_d1.py             # Eligibility (100 records)
│   │   ├── simulate_d2.py             # Demographics & medical history (28 records)
│   │   ├── simulate_d3a.py            # Dose assignment (28 records)
│   │   ├── simulate_d3b.py            # SRC safety review (18 records)
│   │   ├── simulate_d4.py             # PK sampling (144 records)
│   │   ├── simulate_d5.py             # Safety labs and vitals (180 records)
│   │   ├── simulate_d6.py             # Adverse events and SAEs (90 records)
│   │   └── simulate_d7.py             # Volunteer symptom diary (72 records)
│   ├── data/
│   │   └── [simulated CSVs from each instrument]
│   ├── sql/                           # In progress
│   ├── powerbi/                       # Planned
│   └── sdtm/                          # Planned
│
└── docs/                              # Project-level documentation
## About this work

I am an acute care registered nurse with five years of clinical experience, pharmacovigilance training (CCRPS APVAsC), the Oracle Explorer badge, and coursework in clinical data through Vanderbilt and Johns Hopkins. This portfolio documents my transition into clinical data management.

The ultimate goal of this research arc is a Phase 2 trial of dexamethasone combined with a MenB vaccine in patients with meningitis — testing whether the combination is tolerable in the patient population that would ultimately benefit from both. The Phase 2 work is more substantial than what is captured in this repository: real patients with active disease, more complex baseline conditions, wider AE profiles, and a different safety reporting environment than healthy-volunteer Phase 1 work.

I chose to start with the Phase 1 dexamethasone dose escalation as the stepping stone because this is my first end-to-end pipeline project. Building a focused single-agent Phase 1 first lets me establish the architectural patterns and discipline that the Phase 2 build will need, rather than starting from zero on a more complex study. Real engineering teams make this kind of trade-off every week. The Phase 1 work in this repository is a complete and self-contained portfolio piece that prepares me for the substantive Phase 2 work to come.

## Development journal

PROGRESS.md is a detailed engineering journal documenting every architectural decision, every bug caught and fixed, and the clinical reasoning behind design choices across the build. It is a substantial document and represents the thinking behind the code. A reviewer interested in how I approach clinical data problems will find that thinking documented there.

## Roadmap

**This repository (Phase 1):** Simulated Phase 1 dose escalation of IV dexamethasone in healthy volunteers. Simulation complete. SQL pipeline, Power BI dashboards, and SDTM mapping capstone in progress.

**Next project (Phase 2, separate repository):** Simulated Phase 2 tolerability and combination safety study of dexamethasone co-administered with a MenB vaccine in patients with meningitis. Will build on the architectural patterns established here (cross-instrument narrative consistency, disk-based cast pattern, section-by-section build methodology) and add the new complexity of patient-population trial design, combination AE adjudication, vaccine-related safety reporting, and Phase 2 efficacy endpoint framing.

## License

MIT
