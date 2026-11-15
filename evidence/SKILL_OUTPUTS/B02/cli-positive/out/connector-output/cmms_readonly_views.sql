-- DRAFT for the CMMS database owner to review, create and own. NOT applied:
-- this run had read-only access and created nothing in the source file.
-- Purpose: give the plugin a stable, narrow read surface so a change to the
-- underlying tables breaks loudly at the view (owner edits the view) instead of
-- silently changing what the connector returns.
-- Scope: assets and maintenance work orders only (open AND closed). The existing
-- v_open_work_orders view omits closed work orders, close dates and downtime,
-- which breakdown-diagnosis needs for history, so it is not sufficient alone.

CREATE VIEW IF NOT EXISTS v_plugin_assets AS
SELECT
  asset_id,      -- -> assets.asset_id_verbatim (normalized copy -> assets.asset_id)
  site           -- -> assets.site
  -- description: no column on the dataset's assets tab; held out (see mapping)
  -- location: not held by this CMMS -> assets.location stays null
FROM assets;

CREATE VIEW IF NOT EXISTS v_plugin_maintenance_work_orders AS
SELECT
  w.wo           AS maintenance_wo,     -- -> maintenance_work_orders.maintenance_wo
  w.asset_id     AS asset_id,           -- -> asset_id_verbatim (normalized -> asset_id)
  a.site         AS site,               -- -> site (work_orders has no site; via asset)
  w.opened       AS opened_date,        -- -> opened_date (date only, zone unstated)
  w.closed       AS closed_date,        -- -> closed_date (NULL = still open, not unknown)
  w.note         AS note,               -- -> close_out_notes (verbatim; see open question)
  w.wo_type      AS wo_type,            -- no dataset column yet (contract bump needed)
  w.downtime_min AS downtime_min        -- no dataset column yet (contract bump needed)
FROM work_orders w
LEFT JOIN assets a ON a.asset_id = w.asset_id;

-- SQLite has no GRANT. Read-only access is enforced by the consumer opening the
-- file with mode=ro and PRAGMA query_only=ON, and by file-system permissions:
-- the account the connector runs under should have read, not write, on the file.
-- For a server-hosted CMMS database the equivalent is a dedicated integration
-- login granted SELECT on these two views only.
