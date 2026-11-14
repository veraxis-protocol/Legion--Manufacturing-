## Plant context

- **Profile version:** 2
- **Configured:** 2026-11-14 (DRAFT - not approved; every value below is inferred from the dropped documents until confirmed)
- **Company:** Example Precision Works
- **Sites:** Plant 1, EPW1 (default) - inferred, from plant_overview.md; whether other plants exist not asked yet
- **Connectors live:** none (no connector tools in this session)
- **Connectors not live:** Microsoft 365, Oracle NetSuite, Autodesk Fusion
- **Export folder:** SharePoint "Exports" library - inferred, from plant_overview.md; exact path not confirmed
- **Export refresh:** MES production CSVs written nightly at 23:30 local - inferred, from plant_overview.md; not confirmed
- **Standards certified to:** not set - see gaps
- **Templates on file:** none
- **Templates missing:** NCR form, 8D format, quote layout, supplier RFQ package, trade study memo
- **Report depth:** full (default - not asked)
- **Rates:** see Commercial rates - state per rate, values shown only on internal artifacts
- **Gaps open:** 59 (see missing-data-list.md)

### Systems

- **ERP:** Oracle NetSuite - file - inferred, from plant_overview.md ("export only today"); not live in this session; not tested
- **CAD:** Autodesk Fusion - file - inferred, from plant_overview.md (two programming workstations); not live in this session; not tested
- **CMMS:** none - shared maintenance spreadsheet (maintenance_log.csv, not provided) - file - connector options reviewed 2026-11-14
- **Documents:** Microsoft 365 (SharePoint "Quality" and "Exports" libraries) - file - inferred, from plant_overview.md ("connector not authorised yet"); not live in this session
- **MES:** product not named - file - connector options not reviewed (product name needed)

### ERP scope

- **Record types:** not checked - NetSuite connector not live; export only
- **Subsidiary:** not set
- **Locations:** not set
- **Parts:** not set
- **Part revision:** not set
- **Cost fields:** not set
- **Production work orders:** not set (ERP or MES only not yet asked)
- **Source of truth:** not set
- **RFQ stale after:** 5 business days (default, not plant-set)

### Approved normalizations

| Rule | Source spelling | Matches | Approved by | Date |
|---|---|---|---|---|

### Documents read at setup

| File | Identified as | Fed | Status |
|---|---|---|---|
| plant_overview.md | Plant overview (site, systems, shifts, export timing) | Steps 1, 3, 4, 6, 7 | inferred - not confirmed |
| equipment.csv | Asset / equipment register (asset, cell, work center) | Steps 3, 5, 7 | inferred - not confirmed |
| rates_memo.txt | Finance rates memo | Step 10 (and scrap costing basis) | inferred - not confirmed; values in the approval draft only |

### Export files

| File pattern | What it is | System | Cadence | Covers |
|---|---|---|---|---|
| equipment.csv | Asset register: asset_id, description, cell, work_center, install_year (inferred, unconfirmed) | not stated | manual | current asset list |
| MES production CSVs (name not known, not provided) | Production output (inferred, from plant_overview.md) | MES | nightly 23:30 local (inferred) | not set |
| maintenance_log.csv (not provided) | Maintenance log spreadsheet (inferred, from plant_overview.md) | shared spreadsheet | not set | not set |

### Machining data

| Machine class | Work centers | Cell | Setup hours | Tool change min | Basis |
|---|---|---|---|---|---|
| MILL-H (horizontal machining centre, 500 mm pallet) | HMC-01 | Cell A | not set | not set | - |
| MILL-V (vertical machining centre, 3-axis) | VMC-02, VMC-03 | Cell A (VMC-02), Cell B (VMC-03) | not set | not set | - |
| TURN (CNC lathe, 8in chuck) | LTH-01 | Cell B | not set | not set | - |
| INSP (deburr and inspection bench) | DEB-01 | Cell B | not set | not set | - |
| OUTSIDE-FINISH (anodize, outside) | (outside) | - | not set | - | - |

Machine classes, work centers and cells are inferred, from equipment.csv; the anodize outside process is inferred, from rates_memo.txt. None confirmed.

- **Cutting data:** not set
- **Fusion tool library:** not set (Fusion is used for CAM per plant_overview.md; library name not asked)
- **Variance flag threshold:** 15% - default, not plant-set
- **Stale interval:** not set

### Approved suppliers

| Commodity | Approved | Notes |
|---|---|---|
| (none on file) | - | not set - see gaps |

### Source clocks

| Source | Timezone | Zone-aware | Observed skew | Checked |
|---|---|---|---|---|
| NetSuite export | not set (plant zone America/New_York inferred) | not set | not checked | — |
| MES production export | not set (plant zone America/New_York inferred) | not set | not checked | — |
| MES downtime export | not set | not set | not checked (source not confirmed to exist) | — |
| Maintenance spreadsheet (maintenance_log.csv) | not set | not set | not checked | — |
| Historian export | not set | not set | not checked (source not confirmed to exist) | — |
| Quality / inspection export | not set | not set | not checked (source not confirmed to exist) | — |
| Planning export | not set | not set | not checked (source not confirmed to exist) | — |
| Microsoft 365 documents | not set | not set | not checked | — |

Offset self-check: not run - no export data was provided and no event recorded in two systems is available. Declared but unverified.

### Commercial rates

- **Labor rate:** not set - pending approval; candidate figures found in rates_memo.txt are shown only in the approval draft
- **Burden rate:** not set - pending approval; the memo gives fully burdened shop rates per work center, not a separate burden rate
- **Margin rules:** not set - pending approval; candidate default found in rates_memo.txt
- **Downtime cost per hour:** not set - see gaps
- **Scrap costing basis:** standard material plus value-added labour at the work centre where scrapped - inferred, from rates_memo.txt; not confirmed

### Site: Plant 1, EPW1 (default)

- **Location:** Dayton OH - inferred, from plant_overview.md
- **Timezone:** America/New_York - inferred, from plant_overview.md; not confirmed
- **Shift pattern:** two shifts - 1st 06:00-14:30, 2nd 14:30-23:00, Monday-Friday; Saturday overtime on request - inferred, from plant_overview.md; not confirmed
- **Production day starts:** not set - asked directly, not answered yet
- **Cross-midnight shift belongs to:** not set - no shift shown crossing midnight; Saturday overtime attribution not set
- **Planned production time:** not set
- **Vocabulary:** not set - equipment.csv uses asset_id, cell, work_center (one document only; not confirmed)
- **Capability:** not set - candidate from plant_overview.md and equipment.csv: make-to-order CNC machining, aluminium and steel, 1-5,000 pcs; horizontal and 3-axis vertical milling, turning, deburr and inspection in-house; anodize outside. Size envelope, demonstrated tolerances and certifications not given
