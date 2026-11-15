# Consolidated dataset — manifest (SYNTHETIC test data)

Built 2026-11-15 from `./inputs` only. This was a file-only run: no ERP or CMMS connector was used and nothing was written to any external system.
Contract: `consolidated-dataset.md` v6. **The writer is CSV, one file per tab, not XLSX.** Code execution was unavailable in this session, so no workbook could be generated. The column shapes follow the contract.
**All counts were made by reading the files, not computed in code. Verify them before relying on them.**

## Tabs present

| Tab | Rows | Built from | Window kind |
|---|---|---|---|
| parts | 2 | derived from work_orders.csv (no item master in drop) | reference |
| production_work_orders | 3 | inputs/pulse_oee/work_orders.csv | open commitments (all RELEASED; kept by status) |
| production_output | 3 | inputs/pulse_oee/output.csv | activity, 2026-11-12 |
| plan | 2 | inputs/pulse_oee/plan.csv | activity, 2026-11-12 |
| downtime_events | 2 | inputs/pulse_oee/downtime.csv | activity, 2026-11-12 |
| assets | 5 | inputs/equipment.csv | reference |
| key_mismatch_log | 11 lines | every unmatched key and pending proposal | — |

## Tabs missing — named gaps, not empty

- **routings**: `routing.csv` was **set aside**. It has no setup-time column and no revision, so it fails the routing signature. Its 2 rows (PN-100 op 10 VMC 1.0 min/unit; PN-200 op 10 VMC 1.8 min/unit) are shown in the report. With no routing tab, `quote-build` cannot start from a routing.
- **operation_actuals**: there was no source in the drop, so the backflush (`probable_standard`) check was not run.
- **sales_orders, lots, inventory, purchase_orders, inspection_results, maintenance_work_orders, ncrs**: there was no source in the drop.

## Columns that could not be filled

- `uom` is `not_stated` on every quantity. No file declares a unit, and units are never inferred.
- `site` is `SITE-1` on production_output, which is the only file that names a site. Every other tab has `not_stated`.
- `as_of` has no zone on any row. Output and plan carry dates only. Downtime has local times with no zone. work_orders.csv has no record date at all.
- `cell` on plan is null, because the plant context has no work-center-to-cell map.
