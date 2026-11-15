## Plant context

- **Profile version:** 2
- **Configured:** 2026-11-15
- **Status:** DRAFT - not approved. Not installed at profile_path and not published to a Plant setup page. Every value marked inferred is read from a file and awaits confirm-or-correct
- **Company:** Example Precision Works
- **Sites:** Plant 1 - EPW1, Dayton OH (default)
- **Connectors live:** none
- **Connectors not live:** Oracle NetSuite, Microsoft 365, Autodesk Fusion (no connector tools in this session; none tested)
- **Export folder:** SharePoint "Exports" library (inferred, from plant_overview.md) - exact path not set
- **Export refresh:** MES production CSVs nightly, written 23:30 local (inferred, from plant_overview.md) - other sources not set
- **Standards certified to:** not set - see gaps
- **Templates on file:** none
- **Templates missing:** NCR form, 8D format, quote layout, supplier RFQ package, trade study memo
- **Report depth:** full (default - not asked)
- **Rates:** see Commercial rates - state per rate, values shown only on internal artifacts
- **Gaps open:** 61 - see missing-data-list.html

### Systems

- **ERP:** Oracle NetSuite - file (export only today, no API access granted yet, per plant_overview.md; connector not live this session)
- **CAD:** Autodesk Fusion - file (on two programming workstations, per plant_overview.md; Fusion MCP Server not reachable this session, not tested)
- **CMMS:** none - maintenance kept in a shared spreadsheet (maintenance_log.csv) - file - connector options reviewed 2026-11-15 (no web search)
- **Documents:** Microsoft 365 (SharePoint "Quality" and "Exports" libraries) - file (connector not authorised yet, per plant_overview.md)
- **MES:** name not given - file (writes production CSVs to the Exports library) - connector options not reviewed (name needed)

### ERP scope

- **Record types:** not checked - no NetSuite connector this session
- **Subsidiary:** not set
- **Locations:** not set
- **Parts:** not set
- **Part revision:** not set
- **Cost fields:** not set - Standard Costing on or off not known
- **Production work orders:** not set - NetSuite or MES
- **Source of truth:** not set
- **RFQ stale after:** 5 business days (default, not plant-set)

### Approved normalizations

| Rule | Source spelling | Matches | Approved by | Date |
|---|---|---|---|---|
| none yet | - | - | - | - |

### Documents read at setup

| File | Identified as | Fed | Status |
|---|---|---|---|
| plant_overview.md | Plant overview (site, systems, shifts, export timing) | Steps 1, 3, 4, 6, 7 | inferred - awaiting confirm or correct |
| equipment.csv | Asset / equipment register (5 assets, cells, work centers) | Steps 3, 5, 7 | inferred - awaiting confirm or correct |
| rates_memo.txt | Finance memo on commercial rates | Step 10 | inferred - rates in the approval draft only, awaiting a yes and a name |

### Export files

| File pattern | What it is | System | Cadence | Covers | Status |
|---|---|---|---|---|---|
| MES production CSVs (name pattern not given) | Production output (inferred) | MES | nightly, 23:30 local (inferred) | not set | unconfirmed - no file seen |
| maintenance_log.csv | Maintenance tracking spreadsheet (inferred) | Shared spreadsheet (no CMMS) | manual | not set | unconfirmed - file not provided |
| equipment.csv | Asset register (inferred) | dragged in | manual | 5 assets | unconfirmed |
| MES downtime export | not seen | MES | - | - | missing - export request spec written |
| NetSuite exports (items, sales orders, work orders, purchase orders, inventory, routings, closed-job actuals) | not seen | Oracle NetSuite | - | - | missing - export request spec written |
| Quality / inspection export | not seen | not named | - | - | missing - export request spec written |
| Planning / schedule export | not seen | not named | - | - | missing - export request spec written |
| Historian / sensor export | not known whether one exists | not named | - | - | missing - export request spec written |

### Machining data

| Machine class | Work centers | Cell | Setup hours | Tool change min | Basis |
|---|---|---|---|---|---|
| MILL-H (horizontal machining centre, 500 mm pallet) | HMC-01 | Cell A | not set | not set | not set |
| MILL-V (3-axis vertical machining centre) | VMC-02, VMC-03 | Cell A (VMC-02), Cell B (VMC-03) | not set | not set | not set |
| TURN (CNC lathe, 8 in chuck) | LTH-01 | Cell B | not set | not set | not set |
| INSP (deburr and inspection bench) | DEB-01 | Cell B | not set | - | not set |
| OUTSIDE-FINISH (anodize, outside - inferred from rates_memo.txt) | outside | - | lead time not set | - | not set |

Machine classes, work centers and cells are inferred from equipment.csv (one source) and await confirm or correct.

- **Cutting data:** not set
- **Fusion tool library:** not set
- **Variance flag threshold:** 15% - default, not plant-set
- **Stale interval:** not set

### Approved suppliers

| Commodity | Approved | Notes |
|---|---|---|
| not set | - | approved supplier list not provided |

### Source clocks

| Source | Timezone | Zone-aware | Observed skew | Checked |
|---|---|---|---|---|
| NetSuite export | not set (plant zone America/New_York likely) | not checked | not checked | - |
| MES production export | not set (plant zone America/New_York likely) | not checked | not checked | - |
| MES downtime export | not set | not checked | not checked | - |
| Historian export | not set (existence not known) | not checked | not checked | - |
| Quality export | not set | not checked | not checked | - |
| Planning export | not set | not checked | not checked | - |
| Maintenance spreadsheet (maintenance_log.csv) | not set | not checked | not checked | - |

Offset self-check not run: no two sources were in hand to compare. Declared but unverified for every source.

### Site: Plant 1 - EPW1, Dayton OH (default)

- **Timezone:** America/New_York (inferred, from plant_overview.md)
- **Shift pattern:** two shifts Monday-Friday - 1st 06:00-14:30, 2nd 14:30-23:00 - Saturday overtime on request (inferred, from plant_overview.md)
- **Production day starts:** not set - to be asked directly
- **Cross-midnight shift belongs to:** not set - no scheduled shift crosses midnight (inferred); rule for overrun and Saturday overtime not set
- **Planned production time:** not set
- **Vocabulary:** not set - canonical names in use until the plant gives its own words
- **Capability:** inferred, not confirmed - make-to-order CNC machining, aluminium and steel, 1 to 5,000 pieces (plant_overview.md); horizontal milling, 3-axis vertical milling, CNC turning, deburr and inspection in-house (equipment.csv); anodize outside (rates_memo.txt). Envelope, tolerance capability and certifications not set

### Commercial rates

- **Labor rate:** not set - proposed from rates_memo.txt (finance memo dated 2026-10-01), awaiting a yes and a name; the memo gives fully burdened shop rates per work center, not a labor and burden split
- **Burden rate:** not set - the memo says its work-center rates are fully burdened; awaiting confirmation that burden is included in them
- **Margin rules:** not set - proposed default from rates_memo.txt, awaiting a yes and a name; customer and job-type overrides not asked
- **Material markup:** not set - proposed from rates_memo.txt, awaiting a yes; does not fit the margin rules shape, recorded as said
- **Outside processing markup:** not set - proposed from rates_memo.txt for anodize, awaiting a yes; does not fit the margin rules shape, recorded as said
- **Downtime cost per hour:** not set - see gaps
- **Scrap costing basis:** standard material cost plus value-added labour at the work center where scrapped (inferred, from rates_memo.txt; not sensitive)
- **Environment variables:** not checked this session - if any MFG_ rate variable is set it wins over the rates page
