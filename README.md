# Meningitis Research Data Pipeline
### A full-stack clinical data portfolio project — from CRF design to dashboard

---

## Overview

This project simulates a complete, three-phase clinical research programme investigating meningococcal disease — from a first-in-human pharmacokinetic study through to a large-scale federated vaccine efficacy trial.

It is built as a portfolio project to demonstrate end-to-end clinical data skills across the tools used in real-world drug development and health informatics: **REDCap, SQL, Python, Power BI, and OMOP CDM**.

The project was designed by a registered nurse with clinical experience in meningitis management, pharmacovigilance training (APVAsC), and intermediate skills in data management and analysis. Every design decision — from CRF field type to OMOP table mapping — is grounded in clinical reasoning, not just technical convention.

---

## The research question

> Can we reduce death and long-term disability from bacterial meningitis through adjuvant therapy and targeted vaccination — and can we build a research data infrastructure that captures, standardises, and analyses that evidence across three phases of development?

---

## Project structure

```
meningitis-research-pipeline/
│
├── README.md
│
├── phase1-dexamethasone-pk/
│   ├── redcap/
│   │   ├── crf-codebook.pdf          # Exported REDCap codebook — all instruments
│   │   ├── data-dictionary.csv       # REDCap data dictionary — importable
│   │   └── instruments/
│   │       ├── D1_eligibility.pdf
│   │       ├── D2_demographics.pdf
│   │       ├── D3_dose_escalation.pdf
│   │       ├── D4_pk_sampling.pdf
│   │       ├── D5_safety_labs.pdf
│   │       ├── D6_ae_sae.pdf
│   │       └── D7_symptom_diary.pdf
│   ├── data/
│   │   ├── simulated_pk_data.csv     # Simulated PK concentration-time data
│   │   ├── simulated_ae_data.csv     # Simulated adverse event data
│   │   └── simulated_demographics.csv
│   ├── sql/
│   │   ├── schema.sql                # Relational database schema from REDCap export
│   │   ├── pk_queries.sql            # PK time-series queries — Cmax, AUC, half-life
│   │   ├── ae_safety_listings.sql    # Adverse event listings and summaries
│   │   ├── enrolment_queries.sql     # Screen failure, cohort fill, eligibility
│   │   └── cohort_comparison.sql     # Dose cohort comparison queries
│   ├── python/
│   │   ├── pk_analysis.ipynb         # PK curve plotting, AUC, Cmax, half-life
│   │   ├── safety_analysis.ipynb     # AE data cleaning, CTCAE grading summary
│   │   └── requirements.txt
│   └── powerbi/
│       ├── phase1_dashboard.pbix     # Power BI file — 5 page dashboard
│       └── screenshots/
│           ├── pk_curve_page.png
│           ├── safety_monitoring_page.png
│           ├── enrolment_tracker_page.png
│           ├── vitals_page.png
│           └── dose_escalation_page.png
│
├── phase2-menb-vaccine-omop/
│   ├── omop/
│   │   ├── crf_to_omop_mapping.md    # Field-level mapping from CRF to OMOP CDM
│   │   ├── omop_schema_overview.md   # OMOP tables used and their clinical meaning
│   │   └── insert_statements.sql     # SQL to load simulated data into OMOP tables
│   ├── data/
│   │   ├── simulated_ehr_data.csv    # Simulated EHR data in OMOP format
│   │   └── simulated_titres.csv      # SBA antibody titre data
│   ├── sql/
│   │   ├── omop_cohort_queries.sql   # Cohort definition in OMOP standard
│   │   ├── titre_analysis.sql        # SBA titre queries, fold-rise, seroconversion
│   │   └── safety_omop.sql           # AE queries using OMOP condition_occurrence
│   ├── python/
│   │   ├── immunogenicity_analysis.ipynb  # GMT, seroconversion rate, titre plots
│   │   └── requirements.txt
│   └── powerbi/
│       ├── phase2_dashboard.pbix
│       └── screenshots/
│           ├── titre_response_page.png
│           ├── injection_site_heatmap.png
│           └── seroconversion_kpi_page.png
│
├── phase3-menb-vaccine-federated/
│   ├── shrine/
│   │   ├── federated_query_concepts.md   # How SHRINE queries work without sharing data
│   │   └── cohort_query_examples.sql     # Example i2b2 / SHRINE query structure
│   ├── python/
│   │   ├── survival_analysis.ipynb       # Kaplan-Meier, Cox regression, vaccine efficacy
│   │   └── requirements.txt
│   └── powerbi/
│       ├── phase3_dashboard.pbix
│       └── screenshots/
│           ├── kaplan_meier_page.png
│           ├── multisite_map_page.png
│           └── forest_plot_page.png
│
└── docs/
    ├── protocol-summary.md           # Plain language protocol summary
    ├── data-management-plan.md       # DMP — data handling, storage, access
    ├── crf-completion-guidelines.md  # Instructions for trial nurses completing CRF
    ├── sae-reporting-sop.md          # SAE reporting procedure
    └── glossary.md                   # Clinical and data terms defined
```

---

## Phase 1 — Dexamethasone adjuvant · First-in-human PK study

**Drug:** IV dexamethasone 0.15 mg/kg  
**Population:** 20–30 healthy volunteers · three dose escalation cohorts  
**Primary objective:** Safety, tolerability, and pharmacokinetic characterisation  
**Data collection:** REDCap CRF — 7 instruments, 200+ fields, branching logic  

### What this phase demonstrates

**REDCap CRF design** — 7 purpose-built instruments including eligibility with branching logic, a PK sampling schedule capturing blood draws at 8 timepoints per volunteer, a dose escalation log with sentinel dosing rules, a safety laboratory domain, and a volunteer symptom diary configured as a survey.

**PK data analysis** — plasma concentration-time curves built in Python using `matplotlib`, AUC calculation using `scipy.integrate.trapz`, Cmax extraction, half-life estimation, and dose-exposure scatter plots showing linearity across cohorts.

**SQL querying** — relational schema built from REDCap export. Queries include time-series PK data extraction, window functions for Cmax per volunteer per cohort, AE safety listings joined to demographics, and cohort comparison aggregations.

**Power BI dashboard** — 5 pages: PK concentration-time curve with individual volunteer lines and cohort mean overlay, safety monitoring with CTCAE grade distribution, enrolment tracker with screen failure analysis, vital signs time series, and dose escalation cohort summary.

---

## Phase 2 — MenB vaccine · Preliminary efficacy · OMOP CDM

**Vaccine:** Hypothetical novel MenB vaccine · IM injection · two-dose schedule  
**Population:** 100–300 meningitis patients vaccinated post-recovery  
**Primary objective:** Immunogenicity signal and safety in target population  
**Data source:** Simulated EHR data mapped to OMOP Common Data Model  

### What this phase demonstrates

**OMOP CDM mapping** — field-level mapping from Phase 1 CRF variables to OMOP standard tables: `person`, `visit_occurrence`, `measurement`, `drug_exposure`, `condition_occurrence`, `observation`. SQL INSERT statements to load data into OMOP structure.

**Immunogenicity analysis** — serum bactericidal antibody (SBA) titre analysis in Python: geometric mean titre calculation, seroconversion rate (≥4-fold rise from baseline), and titre trajectory plots across the dosing schedule.

**SQL across OMOP** — multi-table JOINs across 5 OMOP tables, cohort definition queries, titre fold-rise calculation, and safety signal detection using `condition_occurrence`.

**Power BI** — antibody titre response charts, injection site reaction heatmap (volunteers × days post-dose × severity), and seroconversion rate KPI cards.

---

## Phase 3 — MenB vaccine · Definitive efficacy · Federated EHR

**Population:** 1,000–5,000 patients · multiple hospital sites  
**Primary objective:** Vaccine efficacy against confirmed MenB disease  
**Data source:** Federated EHR queries via SHRINE / i2b2 — no central data sharing  

### What this phase demonstrates

**Federated query concepts** — SHRINE and i2b2 query architecture, patient counting without transferring individual records, site-level aggregation, and privacy-preserving data access for multi-site research.

**Survival analysis** — Kaplan-Meier curves built with the `lifelines` Python library, Cox proportional hazards regression, vaccine efficacy calculation `(1 - relative risk) × 100`, and subgroup forest plots.

**Multi-site Power BI** — geographic enrolment map, site-level performance comparison, Kaplan-Meier visualisation, and efficacy by subgroup forest plot.

---

## Tools and technologies

| Tool | Used for | Phase |
|---|---|---|
| REDCap | Electronic data capture — CRF design, branching logic, visit scheduling | 1 |
| SQL (SQLite / PostgreSQL) | Relational schema, PK queries, AE listings, OMOP queries | 1, 2, 3 |
| Python | PK analysis, immunogenicity, survival analysis, data cleaning | 1, 2, 3 |
| Power BI | Clinical trial dashboards — PK, safety, enrolment, efficacy | 1, 2, 3 |
| OMOP CDM | EHR data standardisation and interoperability | 2, 3 |
| SHRINE / i2b2 | Federated query concepts for multi-site research | 3 |
| GitHub | Version control, project documentation, portfolio presentation | All |

---

## Clinical background

This project is designed with clinical accuracy at its foundation. The disease biology, trial design decisions, CRF field choices, safety monitoring framework, and endpoint definitions are all grounded in real meningitis research practice — not invented for a data exercise.

Key clinical concepts embedded in the project include the pathophysiology of bacterial meningitis (cytokine cascade, BBB breach, raised ICP), the pharmacological rationale for adjuvant dexamethasone (blunting post-antibiotic inflammatory surge), GCP-compliant data collection standards, CTCAE adverse event grading, ICH SAE definition and reporting timelines, and meningococcal vaccine immunogenicity assessment using serum bactericidal antibody assays.

---

## Project status

| Phase | CRF build | Data simulation | SQL | Python | Power BI |
|---|---|---|---|---|---|
| Phase 1 — Dexamethasone | 🔨 In progress | ⬜ Not started | ⬜ Not started | ⬜ Not started | ⬜ Not started |
| Phase 2 — MenB vaccine OMOP | ⬜ Not started | ⬜ Not started | ⬜ Not started | ⬜ Not started | ⬜ Not started |
| Phase 3 — Federated EHR | ⬜ Not started | ⬜ Not started | ⬜ Not started | ⬜ Not started | ⬜ Not started |

---

## About the author

Registered nurse with clinical experience in acute care and infectious disease management, pharmacovigilance training (APVAsC), and developing skills in clinical data management, health informatics, and research data science.

This project represents the intersection of clinical knowledge and data skills — built to demonstrate that understanding *why* data exists is as important as knowing how to query and visualise it.

---

*Built with REDCap · SQL · Python · Power BI · OMOP CDM*