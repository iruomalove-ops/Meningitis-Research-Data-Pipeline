-- adverse_event: event fact. One row per real AE (23). Already event-shaped — no unpivot.
-- Derived from staging D6, filtered to ae_any=1. The 67 "no AE this visit" placeholders stay in staging.
-- SAE fields kept inline (SDTM AE keeps seriousness as qualifiers, not a separate domain).

DROP TABLE adverse_event CASCADE CONSTRAINTS;

CREATE TABLE adverse_event (
  record_id                 VARCHAR2(50),
  visit_id                  NUMBER,
  repeat_instance           NUMBER(3),
  ae_term                   VARCHAR2(200),
  ae_onset_date             DATE,
  ae_onset_time             VARCHAR2(20),
  ae_resolution_date        DATE,
  ae_ongoing                VARCHAR2(10),
  ae_ctcae_grade            VARCHAR2(10),
  ae_relatedness            VARCHAR2(10),
  ae_outcome                VARCHAR2(50),
  ae_action                 VARCHAR2(100),
  ae_treatment              VARCHAR2(500),
  is_sae                    VARCHAR2(10),
  sae_criterion             VARCHAR2(50),
  sae_reported_sponsor_date DATE,
  sae_reported_ethics_date  DATE,
  ae_pi_signoff             VARCHAR2(100),
  adverse_event_id          NUMBER GENERATED ALWAYS AS IDENTITY
);

ALTER TABLE adverse_event ADD (
  CONSTRAINT pk_adverse_event PRIMARY KEY (adverse_event_id),
  CONSTRAINT uq_ae_rec_instance UNIQUE (record_id, repeat_instance),
  CONSTRAINT fk_ae_subject FOREIGN KEY (record_id) REFERENCES subject (record_id),
  CONSTRAINT fk_ae_visit   FOREIGN KEY (visit_id)  REFERENCES visit (visit_id)
);

INSERT INTO adverse_event (
  record_id, visit_id, repeat_instance,
  ae_term, ae_onset_date, ae_onset_time, ae_resolution_date, ae_ongoing,
  ae_ctcae_grade, ae_relatedness, ae_outcome, ae_action, ae_treatment,
  is_sae, sae_criterion, sae_reported_sponsor_date, sae_reported_ethics_date,
  ae_pi_signoff
)
SELECT
  d6.record_id,
  v.visit_id,
  d6.redcap_repeat_instance,
  d6.ae_term,
  TO_DATE(d6.ae_onset_date, 'YYYY-MM-DD'),
  d6.ae_onset_time,
  TO_DATE(d6.ae_resolution_date, 'YYYY-MM-DD'),
  d6.ae_ongoing,
  d6.ae_ctcae_grade,
  d6.ae_relatedness,
  d6.ae_outcome,
  d6.ae_action,
  d6.ae_treatment,
  d6.is_sae,
  d6.sae_criterion,
  TO_DATE(d6.sae_reported_sponsor_date, 'YYYY-MM-DD'),
  TO_DATE(d6.sae_reported_ethics_date, 'YYYY-MM-DD'),
  d6.ae_pi_signoff
FROM d6_adverse_events_and_saes d6
JOIN visit v ON v.event_name = d6.redcap_event_name
WHERE d6.ae_any = '1';
commit;