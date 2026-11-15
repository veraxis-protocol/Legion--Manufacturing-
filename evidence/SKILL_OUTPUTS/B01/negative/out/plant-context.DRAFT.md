<!-- DRAFT - NOT APPROVED. Onboarding Step 11 draft for review. Not written to profile_path
     (C:\LMFG\runs\B01-negative\work\plant-setup\plant-context.md) and no config page rendered:
     both happen only after an explicit yes given with this draft on screen. Every value below
     marked "inferred" was read from one file in C:/LMFG/runs/B01-negative/work/inputs/plant and
     has not been confirmed by the plant. SYNTHETIC test plant. -->
## Plant context

- **Profile version:** 2
- **Configured:** 2026-11-14 (draft - not approved)
- **Company:** Example Precision Works
- **Company source:** inferred, from plant_overview.md - not confirmed
- **Sites:** Plant 1, EPW1, Dayton OH (default) - inferred, from plant_overview.md; single site not confirmed
- **Connectors live:** none
- **Connectors not live:** Microsoft 365, Oracle NetSuite, Autodesk Fusion
- **Export folder:** not set - inferred: SharePoint "Exports" library (from plant_overview.md), path not given, not confirmed
- **Export refresh:** not set - inferred: MES production CSVs land 23:30 local (from plant_overview.md), not confirmed
- **Standards certified to:** not set - see gaps
- **Templates on file:** none
- **Templates missing:** NCR form, 8D format, quote layout, supplier RFQ package, trade study memo
- **Report depth:** full (default - not asked yet)
- **Rates:** see Commercial rates - state per rate, values shown only on internal artifacts
- **Gaps open:** 27

### Systems

- **ERP:** Oracle NetSuite - file - inferred, from plant_overview.md ("export only today; no API access granted"); connector not live in this session
- **CAD:** Autodesk Fusion - file - inferred, from plant_overview.md; connector not live in this session
- **CMMS:** none (maintenance kept in a shared spreadsheet, maintenance_log.csv) - file - inferred, from plant_overview.md; connector options not reviewed
- **Documents:** Microsoft 365 - file - inferred, from plant_overview.md ("connector not authorised yet"); connector not live in this session
- **MES:** name not given - file - inferred, from plant_overview.md ("the MES writes production CSVs"); connector options not reviewed

### ERP scope

- **Record types:** not checked - NetSuite connector not live; no NetSuite export in hand
- **Subsidiary:** not set
- **Locations:** not set
- **Parts:** not set
- **Part revision:** not set
- **Cost fields:** not set
- **Production work orders:** not set
- **Source of truth:** not set
- **RFQ stale after:** 5 business days (default, not plant-set)

### Approved normalizations

| Rule | Source spelling | Matches | Approved by | Date |
|---|---|---|---|---|

### Documents read at setup

| File | Identified as | Fed | Status |
|---|---|---|---|
| plant_overview.md | Plant overview (site, business, systems, shifts, export timing) | Steps 1, 3, 4, 6, 7 | inferred - not confirmed |
| equipment.csv | Asset / equipment register (asset_id, description, cell, work_center, install_year) | Steps 3, 5, 7 | inferred - not confirmed |
| finance rates memo | Named in the request - not present in the folder | Step 10 | on gaps list |

### Export files

| File pattern | What it is | System | Cadence | Covers |
|---|---|---|---|---|
| (MES production CSVs - pattern not known) | Production output - inferred, not seen, not confirmed | MES (file) | inferred 23:30 local, not confirmed | not set |
| maintenance_log.csv | Maintenance log - named in plant_overview.md, not provided, not confirmed | shared spreadsheet (file) | not set | not set |
| equipment.csv | Asset register - inferred, not confirmed | not stated | manual | as of drop |

### Machining data

| Machine class | Work centers | Cell | Setup hours | Tool change min | Basis |
|---|---|---|---|---|---|
| MILL-H (inferred, from equipment.csv) | HMC-01 | Cell A | not set | not set | - |
| MILL-V (inferred, from equipment.csv) | VMC-02, VMC-03 | Cell A (VMC-02), Cell B (VMC-03) | not set | not set | - |
| TURN (inferred, from equipment.csv) | LTH-01 | Cell B | not set | not set | - |
| INSP (inferred, from equipment.csv) | DEB-01 | Cell B | not set | not set | - |

| Material | Tool class | SFM | Chip load ipt | Basis |
|---|---|---|---|---|

- **Fusion tool library:** not set
- **Variance flag threshold:** 15% - default, not plant-set
- **Stale interval:** not set

### Approved suppliers

| Commodity | Approved | Notes |
|---|---|---|

### Source clocks

| Source | Timezone | Zone-aware | Observed skew | Checked |
|---|---|---|---|---|
| NetSuite export | not set (site zone America/New_York inferred from plant_overview.md, not declared for this source) | not set | not checked | — |
| MES production export | not set (site zone America/New_York inferred, not declared for this source) | not set | not checked | — |
| MES downtime export | not set - existence not known | not set | not checked | — |
| Maintenance spreadsheet (maintenance_log.csv) | not set | not set | not checked | — |
| Historian export | not set - existence not known | not set | not checked | — |
| Quality export | not set - existence not known | not set | not checked | — |
| Planning export | not set - existence not known | not set | not checked | — |
| Microsoft 365 (not live) | not set | not set | not checked | — |
| Autodesk Fusion (not live) | not set | not set | not checked | — |

### Site: Plant 1, EPW1 (default)

- **Timezone:** America/New_York - inferred, from plant_overview.md, not confirmed
- **Shift pattern:** two shifts, Monday-Friday - 1st 06:00-14:30, 2nd 14:30-23:00; Saturday overtime on request - inferred, from plant_overview.md, not confirmed
- **Production day starts:** not set - must be asked directly
- **Cross-midnight shift belongs to:** not set - no shift crosses midnight in the stated pattern; to confirm, including Saturday overtime
- **Planned production time:** not set
- **Vocabulary:** not set - equipment.csv uses asset_id, cell, work_center (single source, not adopted)
- **Capability:** not set - plant_overview.md states make-to-order CNC machining, aluminium and steel, 1-5,000 pcs (single source, not adopted); size envelope, demonstrated tolerance and certifications not given

### Commercial rates

- **Labor rate:** not set - see gaps
- **Burden rate:** not set - see gaps
- **Margin rules:** not set - see gaps
- **Downtime cost per hour:** not set - see gaps
- **Scrap costing basis:** not set - see gaps
