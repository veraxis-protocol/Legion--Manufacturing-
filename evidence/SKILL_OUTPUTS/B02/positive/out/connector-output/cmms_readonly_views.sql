-- DRAFT read-only view definitions for the plant CMMS (SQLite file cmms_synthetic.sqlite)
-- Produced by the custom-connector skill, Tier 4 (read-only database view).
-- Status: PROPOSED, for the CMMS database owner / DBA to review, own and create.
-- Mapping target: shared/contracts/consolidated-dataset.md, contract version 6.
--
-- A Claude skill produces artifacts; it does not stand up or host infrastructure.
-- Nothing in this file has been created in the CMMS database. The connector
-- (cmms_connector.py) runs these same SELECTs as TEMP views on a read-only
-- connection, so the source file is never written.
--
-- Scope (Step 2): maintenance work orders and the assets they hang off.
-- Nothing else is exposed. No write path.
--
-- Fields with NO home in the consolidated dataset (left out, see the mapping):
--   work_orders.wo_type, work_orders.downtime_min, assets.description,
--   and work_orders.note on an OPEN work order (it is a problem description,
--   not a close-out note). They stay out until the contract gains them with a
--   version bump.

-- Tab: assets  (one row per machine, key: asset ID)
CREATE VIEW lmfg_assets AS
SELECT
  a.site                                   AS site,               -- site (rule 7); read verbatim from assets.site
  'cmms'                                   AS source_system,      -- source_system
  'cmms_synthetic.sqlite:assets/' || a.asset_id AS source_ref,    -- source_ref (rule 6)
  NULL                                     AS as_of,              -- as_of: UNRESOLVED, source holds no record timestamp
  'matched'                                AS join_status,        -- CMMS is the source of truth for asset ID
  NULL                                     AS mismatch_class,
  NULL                                     AS contradicted_by,
  NULL                                     AS integrity_flags,
  a.asset_id                               AS asset_id,           -- asset_id (normalized = verbatim: CMMS is source of truth)
  a.asset_id                               AS asset_id_verbatim,  -- asset_id_verbatim
  NULL                                     AS location            -- location: source holds no location below site
FROM assets a;

-- Tab: maintenance_work_orders  (one row per maintenance ticket, joins on asset)
CREATE VIEW lmfg_maintenance_work_orders AS
SELECT
  a.site                                   AS site,               -- site, via the asset (work_orders has no site column)
  'cmms'                                   AS source_system,
  'cmms_synthetic.sqlite:work_orders/' || w.wo AS source_ref,
  NULL                                     AS as_of,              -- UNRESOLVED: dates are date-only, no zone, no plant clock on file
  CASE WHEN a.asset_id IS NOT NULL THEN 'matched' ELSE 'unmatched' END AS join_status,
  NULL                                     AS mismatch_class,     -- classified by data-consolidate, not here
  NULL                                     AS contradicted_by,
  CASE WHEN w.closed IS NOT NULL AND w.closed < w.opened
       THEN 'end_before_start' END         AS integrity_flags,
  w.wo                                     AS maintenance_wo,     -- maintenance_wo (never "work_order")
  w.asset_id                               AS asset_id,
  w.asset_id                               AS asset_id_verbatim,
  w.opened                                 AS opened_date,        -- "dates": column name PROPOSED, contract names none
  w.closed                                 AS closed_date,        -- "dates": NULL = still open (same rule as the source's v_open_work_orders)
  CASE WHEN w.closed IS NOT NULL THEN w.note END AS close_out_notes -- "close-out notes": column name PROPOSED
FROM work_orders w
LEFT JOIN assets a ON a.asset_id = w.asset_id;
