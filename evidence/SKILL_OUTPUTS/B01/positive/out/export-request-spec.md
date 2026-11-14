# Export request specification - Example Precision Works, Plant 1 (EPW1)

For the plant's IT. Written because these sources were not in the dropped files (onboarding Step 3: a missing
source gets its spec in the same run). Each spec is what the plugin's `data-consolidate`, `daily-production-report`,
`breakdown-diagnosis` and `root-cause-capa` read in place of a live connector.

Common to every file:
- **Format:** CSV, UTF-8, header row, comma-delimited, quoted text fields.
- **Landing path:** the SharePoint "Exports" library (inferred, from plant_overview.md - exact folder to be confirmed, question D2).
- **Cadence:** nightly, landing at the same time as the MES production CSVs (23:30 local per plant_overview.md - to be confirmed).
- **Timestamps:** ISO 8601 **with offset** (e.g. `2026-09-08T06:12:00-04:00`). Naive timestamps break cross-system correlation.
- **IDs:** each system's own ID, unchanged. `asset_id` must be the same ID used in equipment.csv (HMC-01, VMC-02 ...).
- **Late or corrected records:** re-exported in full inside the window; the newest file wins on the record key.
- **Units:** every quantity with its unit of measure column; every duration with its unit stated in the header.

## 1. MES production output - `mes_production_<YYYY-MM-DD>.csv` (exists per plant_overview.md; send one sample to confirm headers)

| Field | Type | Unit / format | Required | Notes |
|---|---|---|---|---|
| `production_wo` | text | - | yes | The job / work order number as NetSuite holds it |
| `part_number` | text | - | yes | |
| `part_revision` | text | - | no | |
| `asset_id` | text | - | yes | Machine the output was made on |
| `work_center` | text | - | yes | MILL-H, MILL-V, TURN, INSP |
| `shift` | text | `1` / `2` / `SAT-OT` | yes | |
| `production_day` | date | YYYY-MM-DD | yes | Per the plant's production-day rule (question E3) |
| `qty_good` | number | | yes | |
| `qty_scrap` | number | | yes | Zero only when none was scrapped; blank if unknown |
| `uom` | text | | yes | |
| `reported_at` | timestamp | ISO 8601 with offset | yes | |
| `lot_number` | text | - | no | |

Window: prior production day, plus re-export of the last 7 days to pick up corrections.

## 2. MES downtime events - `mes_downtime_<YYYY-MM-DD>.csv`

| Field | Type | Unit / format | Required | Notes |
|---|---|---|---|---|
| `event_id` | text | - | yes | |
| `asset_id` | text | - | yes | |
| `start` | timestamp | ISO 8601 with offset | yes | |
| `end` | timestamp | ISO 8601 with offset | when ended | Blank, never zero, while open |
| `minutes` | number | minutes | yes when ended | |
| `reason_code` | text | - | yes | The MES's own code |
| `reason_text` | text | - | no | Verbatim |
| `planned` | text | `planned` / `unplanned` | yes | Planned maintenance windows, breaks, changeovers marked planned |
| `production_wo` | text | - | no | |

Window: prior production day, plus re-export of the last 7 days.

## 3. Maintenance (shared spreadsheet maintenance_log.csv) - `cmms_maintenance_<YYYY-MM-DD>.csv`

| Field | Type | Unit / format | Required | Notes |
|---|---|---|---|---|
| `work_order_id` | text | — | yes | The spreadsheet's own ID, unchanged |
| `asset_id` | text | — | yes | The same asset ID the MES downtime export uses; if the systems differ, both columns |
| `asset_name` | text | — | yes | Plant's name for the machine |
| `type` | text | `corrective` / `preventive` / `inspection` | yes | Map the log's own types; never leave blank |
| `status` | text | `open` / `in_progress` / `closed` | yes | |
| `opened_at` | timestamp | ISO 8601 **with offset** | yes | Naive timestamps break cross-system correlation |
| `closed_at` | timestamp | ISO 8601 with offset | when closed | Blank, never zero, while open |
| `failure_mode` | text | — | no | Failure code or category |
| `close_out_note` | text | — | no | Free text, verbatim; `breakdown-diagnosis` mines it |
| `parts_used` | text | `part_no:qty;…` | no | |
| `labor_hours` | number | hours, decimal | no | |
| `pm_plan_id` | text | — | no | Which PM plan, for preventive work |

- **Naming:** `cmms_maintenance_<YYYY-MM-DD>.csv`, dated the day of export.
- **Window:** a rolling 90 days of `opened_at`, so a work order reopened or closed late is picked up on the next export.
- **Asset register:** a second file, `cmms_assets_<YYYY-MM-DD>.csv` — `asset_id`, `asset_name`, `work_center`, `cell`,
  `make`, `model`, `install_date` — weekly is enough. (equipment.csv today has asset_id, description, cell, work_center,
  install_year; make and model would be added.)

## 4. NetSuite exports (until the connector is enabled) - one file per record type

`ns_items_<date>.csv` (part number, revision, description, UOM, standard / average / last purchase cost with currency),
`ns_sales_orders_<date>.csv` (sales order, line, customer, part, qty, uom, promised date, price, currency),
`ns_work_orders_<date>.csv` (production work order, part, qty ordered, uom, due date, status, sales order, closed date,
actual material / labor / burden / subcontract cost with currency), `ns_purchase_orders_<date>.csv` (PO, line, supplier
ID, supplier, part, qty, uom, cost, currency, delivery date, received qty), `ns_inventory_<date>.csv` (part, location,
lot, on-hand qty, uom), `ns_routings_<date>.csv` (part, revision, op seq, work center, setup hours, run time per unit,
run time unit). Window: open records plus the last 365 days of closed ones. Scope (subsidiary, locations, parts) per
questions I1-I3.

## 5. Quality / inspection - `inspection_<YYYY-MM-DD>.csv` (only if such a system or log exists - question B6)

`inspection_id`, `production_wo`, `part_number`, `part_revision`, `lot_number`, `characteristic`, `nominal`,
`lower_tol`, `upper_tol`, `measured`, `unit`, `result` (`pass`/`fail`), `inspector`, `asset_id` (gauge or machine),
`measured_at` (ISO 8601 with offset). Window: prior production day, plus 7-day re-export.

## 6. Planning - `plan_<YYYY-MM-DD>.csv` (only if a planning tool exists - question B6)

`part_number`, `production_wo`, `work_center`, `planned_qty`, `uom`, `planned_date` (YYYY-MM-DD), `shift`.
Window: next 14 days. Needed for output against plan.

## 7. Historian / sensor - (only if one exists - question B6)

`asset_id`, `tag`, `timestamp` (ISO 8601 with offset), `value`, `unit`. Per-event windows on request rather than a
nightly bulk file.
