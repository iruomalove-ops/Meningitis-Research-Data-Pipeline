-- ============================================================================
-- 01_create_schema.sql — Phase 1 pipeline schema setup
-- ============================================================================
-- Run ONCE, as SYSDBA, connected to the ORCLPDB pluggable database, BEFORE any
-- staging or core build. Creates the p1_staging schema (in Oracle, the user IS
-- the schema) and grants every privilege the pipeline needs.
--
-- This reconstructs the setup performed live during the build so the whole
-- database is reproducible from the repo, from zero, in order. The privileges
-- were originally granted reactively as each was hit (CREATE SEQUENCE when the
-- first IDENTITY column threw ORA-01031; CREATE VIEW for the analytics layer);
-- they are consolidated here so a fresh build hits none of those surprises.
--
-- How to run:  sqlplus / as sysdba   then   @sql/setup/01_create_schema.sql
-- ============================================================================

ALTER SESSION SET CONTAINER = ORCLPDB;
-- NOTE: password in plaintext is fine for this local demo schema (throwaway, no
-- real data). In production this would be parameterized or use a secrets vault.

CREATE USER p1_staging IDENTIFIED BY Staging_2026;

GRANT CREATE SESSION           TO p1_staging;   -- log in
GRANT CREATE TABLE             TO p1_staging;   -- staging + core tables
GRANT CREATE SEQUENCE          TO p1_staging;   -- IDENTITY columns need a hidden sequence
GRANT CREATE VIEW              TO p1_staging;   -- analytics layer (decode/derive views)
GRANT QUOTA UNLIMITED ON USERS TO p1_staging;   -- space to store the data