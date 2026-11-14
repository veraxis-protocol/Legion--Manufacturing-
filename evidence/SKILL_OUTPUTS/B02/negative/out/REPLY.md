# custom-connector reply — synthetic CMMS (SQLite)

**Status: Untested: not registered.** I could not read anything back. The database is not at
`C:/LMFG/runs/B02-negative/work/inputs/connector/cmms_synthetic.sqlite`. The only file in that folder is `README.txt`.

## What I set up
- Tier: **4, a read-only database read** (selected). The README says it is a local SQLite file with tables `meta`, `assets`, `work_orders` and a view `v_open_work_orders`, and that no credentials are needed. Tiers 1 and 2 were **not checked**: the product is not named, and web or registry search was not allowed in this run.
- Read-only probe: `out/scripts/cmms_readonly_probe.py`. It opens the file with SQLite `mode=ro` and `PRAGMA query_only`, lists the tables, views and columns, and prints sample rows. It never creates the file.

## Test results against real data
| Check | Result |
|---|---|
| Path exists | **No** |
| File opened | No (nothing was opened or created) |
| Records read | **0** |
| Probe exit code | 2 (`out/connector-output/test-run-result.json`) |

Validated for: nothing. No mapping is confirmed.

## Field mapping (proposed, unverified, entity-level only)
| Source | Destination (contract v6) | Key | Status |
|---|---|---|---|
| `assets` | `assets` | `asset_id` / `asset_id_verbatim` | proposed |
| `work_orders` | `maintenance_work_orders` (`maintenance_wo`) | `asset_id` / `asset_id_verbatim` | proposed |
| `v_open_work_orders` | subset of `maintenance_work_orders` | same | proposed |
| `meta` | no tab | — | unmapped, contents unknown |

There is no column-level mapping and no transforms: the column names are unknown. The draft view in the plan uses `<placeholder>` column names.

## Open questions (not asked; recorded)
1. **Person asking:** where is `cmms_synthetic.sqlite`? Please supply it at that path or give the correct path.
2. **CMMS administrator:** which CMMS product and version is this? Is the file the live database or a copy, and if it is a copy, how often is it refreshed?
3. **Person asking:** which flow is needed first (asset list, open maintenance work orders, history with close-out notes), and for which skill?

## How it will break
- **Schema drift** returns wrong or empty data with no error.
- **A moved or missing file** breaks it, as it did in this run.
- **File locks** can block a read while the CMMS is writing.
- **A copied file** is only as fresh as the last copy.
- **Owner:** the CMMS/database administrator (role).

Connection plan: `out/connector-output/connection-plan.html`.
