# Meningitis Research Pipeline

An end-to-end clinical data engineering portfolio project demonstrating the lifecycle of clinical trial data from **CRF design and electronic data capture through data simulation, relational database design, clinical data review, SQL analytics, reconciliation, visualization, and CDISC SDTM implementation**.

The project combines clinical domain knowledge from nursing practice with clinical data management, database engineering, programming, analytics, and standards-based workflows used in modern clinical research.

> **Current focus:** Phase 1 simulated IV dexamethasone dose-escalation study in healthy volunteers
> **Future study:** Phase 2 simulated dexamethasone + MenB vaccine combination study in patients with meningitis

---

## Project Snapshot

| Component                   | Details                                                                |
| --------------------------- | ---------------------------------------------------------------------- |
| Study Phase                 | Phase 1                                                                |
| Study Design                | First-in-human IV dexamethasone dose escalation                        |
| Population                  | Healthy volunteers                                                     |
| Screening Pool              | 100 volunteers                                                         |
| Randomised Volunteers       | 18                                                                     |
| Dose Cohorts                | 2 mg, 4 mg, 8 mg                                                       |
| Source Records              | 660                                                                    |
| Normalised Database Records | 2,664                                                                  |
| EDC                         | REDCap                                                                 |
| Database                    | Oracle 21c                                                             |
| Programming                 | Python                                                                 |
| Analytics                   | Oracle SQL, Power BI                                                   |
| Standards                   | CDISC SDTM, MedDRA, NCI EVS                                            |
| Version Control             | Git / GitHub                                                           |
| Current Status              | SQL pipeline and Power BI dashboard complete; SDTM mapping in progress |

---

# Phase 1 — Dexamethasone Dose Escalation

Phase 1 is a simulated first-in-human dose-escalation study of IV dexamethasone in healthy volunteers. The study was designed end-to-end, beginning with CRF development and progressing through data simulation, relational modelling, clinical data review, SQL reporting, reconciliation, and executive visualization.

The Phase 1 architecture establishes reusable patterns for the more complex Phase 2 study planned as a separate repository.

## What This Phase Demonstrates

* Seven REDCap CRF instruments designed around Phase 1 clinical trial conventions, including branching logic, repeating events, and cross-instrument validation.
* Programmatic clinical data simulation in Python producing 660 source records across eight CSV datasets.
* A normalized Oracle relational database supporting clinical data storage, transformation, validation, and analysis.
* Transformation of wide-format source data into normalized long-format clinical records.
* Cross-instrument narrative consistency across laboratory data, adverse events, symptom diaries, and safety review.
* Clinical data reconciliation designed to identify inconsistencies across study instruments and between EDC and safety data.
* SQL-based clinical reporting covering safety, protocol compliance, pharmacokinetics, reconciliation, and subject disposition.
* Power BI executive reporting built on a structured clinical data model.
* Standards-based data structures using CDISC SDTM principles and controlled terminology.
* Version-controlled project development with technical documentation and an engineering development journal.

---

# From Simulation to Database

The Python simulation layer produces **660 wide-format source records** across the study instruments.

These records are loaded into the normalized Oracle schema, where multi-measurement instruments are transformed into long-format structures. Individual laboratory analytes and vital-sign measurements become separate database records.

This expands the dataset from **660 source records to 2,664 normalized database records**.

The two figures represent different stages of the pipeline:

**660 = simulated source records**

**2,664 = normalized database records**

The SQL reconciliation reports verify the integrity of the transformed dataset and its relationship to the original source data.

---

# Trial Design at a Glance

The simulated Phase 1 study includes:

* Three dose cohorts of six randomized volunteers each.
* Dose levels of **2 mg, 4 mg, and 8 mg IV dexamethasone**.
* Sentinel dosing within each cohort.
* Pharmacokinetic sampling across eight timepoints over 48 hours.
* A one-compartment IV pharmacokinetic model using published dexamethasone constants.
* Safety laboratory assessments at three timepoints covering CBC, liver function, renal function, and electrolytes.
* Adverse-event collection across five clinical assessment points.
* Volunteer-reported symptom diaries across four assessment events.
* Safety Review Committee review at Day 21 for cohort escalation decisions.

---

# Engineered Safety Narrative

The simulated dataset includes deliberately engineered clinical scenarios to test whether safety information remains consistent across multiple clinical data sources.

One volunteer in the 8 mg cohort is designated as a high responder, with an above-cohort response at T+48h across glucose, neutrophilia, and potassium. A Grade 1 ALT elevation subsequently emerges at Day 7.

A second volunteer experiences acute gastroenteritis requiring overnight hospitalization between Day 3 and Day 5. The event is formally captured as a serious adverse event and adjudicated as unrelated to study drug.

These scenarios are intentionally represented across multiple instruments, including:

* Safety laboratories
* Adverse events
* Volunteer symptom diary
* SRC safety review

The same study identifiers are maintained across the instruments so that the clinical narratives can be reconciled programmatically.

This provides a realistic test case for **cross-instrument consistency, adverse-event reconciliation, safety review, and clinical data quality checks**.

---

# SQL Pipeline

The project uses a normalized **Oracle 21c** clinical database consisting of:

* 13 core tables
* 1 reference table
* 2 analytical views

The SQL layer produces seven Clinical Study Report–style outputs:

1. Protocol Deviation Listing
2. SAE Line Listing
3. Subject Enrolment / CONSORT Summary
4. Cross-Instrument Reconciliation Report
5. Adverse Event Reconciliation against a simulated safety-database extract
6. Safety Laboratory Summary
7. Pharmacokinetic Summary

The safety laboratory analysis includes descriptive statistics, change-from-baseline analysis, and shift tables.

The pharmacokinetic analysis calculates:

* Cmax
* Tmax
* AUC(0–48h)

AUC is calculated using the linear trapezoidal rule.

Each report is documented with its SQL logic, output, and clinical reasoning.

---

# Power BI Dashboard

The Phase 1 project includes a single-page executive Power BI dashboard built using a **galaxy-schema data model**.

The model uses conformed SUBJECT and VISIT dimensions with fact and satellite tables to support clinical and operational reporting.

The dashboard includes:

* Trial KPI summary
* Subject disposition funnel
* Screen-failure breakdown
* Dose-escalation summary
* SRC sign-off status
* Cross-instrument reconciliation
* Protocol exceptions
* SAE listing
* PK dose-proportionality analysis
* Safety laboratory biomarker analysis
* High-responder subject profile

Live DAX measures are used where the underlying data supports dynamic calculation, including counts, means, CV%, and fold-rise metrics.

Curated findings are used where the result represents a documented study outcome rather than a metric that should be recalculated dynamically.

This distinction is deliberate and reflects the difference between **derived analytics and documented clinical findings**.

---

# Tools & Standards

### Clinical Data Capture

* REDCap

### Programming & Data Engineering

* Python
* Pandas
* NumPy
* Oracle SQL
* SQL*Loader

### Analytics & Visualization

* Power BI
* DAX
* Excel

### Clinical Data Standards

* CDISC SDTM
* MedDRA
* NCI EVS
* GCP principles

### Clinical Safety

* Adverse Event reconciliation
* SAE review
* Safety laboratory analysis
* Protocol deviation reporting

### Development & Documentation

* Git
* GitHub
* Technical documentation
* AI-assisted development and technical problem-solving

AI tools were used as part of the development workflow for activities including SQL/Python development, debugging, data analysis, documentation, and technical problem-solving. All resulting logic and outputs were reviewed and validated within the project workflow.

---

# Current Status

| Component                                 | Status      |
| ----------------------------------------- | ----------- |
| Phase 1 REDCap CRF design — 7 instruments | Complete    |
| Phase 1 simulation scripts                | Complete    |
| Phase 1 simulated dataset — 660 records   | Complete    |
| Cross-instrument narrative consistency    | Complete    |
| SQL pipeline and relational schema        | Complete    |
| Clinical Study Report–style SQL outputs   | Complete    |
| Power BI executive dashboard              | Complete    |
| SDTM mapping capstone                     | In progress |
| Phase 2 combination trial                 | Planned     |

---

# Repository Structure

```text
meningitis-research-pipeline/
│
├── README.md
├── PROGRESS.md
│
├── phase1-dexamethasone-pk/
│   ├── redcap/
│   │   ├── crf-codebook.pdf
│   │   └── data-dictionary.csv
│   │
│   ├── python/
│   │   ├── simulate_d1.py
│   │   ├── simulate_d2.py
│   │   ├── simulate_d3a.py
│   │   ├── simulate_d3b.py
│   │   ├── simulate_d4.py
│   │   ├── simulate_d5.py
│   │   ├── simulate_d6.py
│   │   └── simulate_d7.py
│   │
│   ├── data/
│   │   └── [simulated CSVs]
│   │
│   ├── sql/
│   │   └── [schema, views, reports]
│   │
│   ├── powerbi/
│   │   └── [executive dashboard]
│   │
│   └── sdtm/
│       └── [SDTM mapping]
│
└── docs/
    └── [project documentation]
```

---

# About the Project

I am an acute-care registered nurse with five years of clinical experience and training in pharmacovigilance, clinical data management, Oracle database technologies, and clinical data standards.

This portfolio represents a transition from direct clinical practice into **clinical data management and clinical data engineering**, combining clinical knowledge with technical data skills.

The project is designed around a broader research arc.

The next planned study is a simulated **Phase 2 tolerability and combination-safety trial of dexamethasone co-administered with a MenB vaccine in patients with meningitis**.

The Phase 2 study will introduce additional complexity, including:

* Patient-population trial design
* More complex baseline conditions
* Combination-product safety assessment
* Broader adverse-event profiles
* Vaccine-related safety reporting
* Phase 2 efficacy endpoint framing

The Phase 1 repository therefore serves as the architectural foundation for the subsequent Phase 2 work.

---

# Development Journal

`PROGRESS.md` documents the engineering process behind the project, including:

* Architectural decisions
* Data-modeling choices
* Bugs encountered and resolved
* Validation logic
* Clinical reasoning
* SQL design decisions
* Power BI modelling decisions
* Lessons learned throughout development

The journal provides additional context for reviewers interested not only in the final outputs, but also in **how clinical data problems were approached and solved**.

---

# Roadmap

### Phase 1 — Current Repository

**Simulated IV dexamethasone dose-escalation study in healthy volunteers**

Simulation, relational database, SQL analytics, reconciliation, and Power BI dashboard are complete. SDTM mapping is currently in progress.

### Phase 2 — Next Repository

**Simulated dexamethasone + MenB vaccine combination study in patients with meningitis**

The Phase 2 project will build on the Phase 1 architecture while introducing:

* Patient-population complexity
* Combination-study design
* Vaccine-related safety reporting
* More complex AE adjudication
* Phase 2 efficacy endpoints
* Expanded clinical data-management workflows

---

# License

MIT
