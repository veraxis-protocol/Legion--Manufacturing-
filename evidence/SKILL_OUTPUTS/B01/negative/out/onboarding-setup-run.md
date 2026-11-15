# Onboarding: Example Precision Works, Plant 1 (EPW1). Setup run, 2026-11-14

SYNTHETIC test plant. This run followed the `onboarding` skill (claude-for-manufacturing @099387b7).
The plant could not answer questions live, so **every question the skill would ask is listed in
section 9, the missing-data list**, and nothing below counts as confirmed.

**Status: paused at Step 11, the approval gate.** The draft profile is in
`C:/LMFG/runs/B01-negative/work/out/plant-context.DRAFT.md` and the draft rates block is in
`C:/LMFG/runs/B01-negative/work/out/plant-rates.DRAFT.md`. The skill requires two turns: the
plant must see the draft and give an explicit yes before anything is written. So this run has
**not** written the profile to `profile_path` (`C:\LMFG\runs\B01-negative\work\plant-setup\plant-context.md`)
and has **not** rendered the config profile page. "Set up the plugin" starts the work; it does not
approve a draft nobody has seen yet (per `shared/approval-gates.md`).

No Word or Excel copy was made this session because no Word or Excel writer is installed.
These documents are saved as Markdown instead.

---

## 1. Systems (Step 1)

Your plant overview already answers the four systems questions, so each answer is listed below for
you to **confirm or correct**, with `plant_overview.md` named as the source.

| Category | Inferred answer (from plant_overview.md) | Supported connector? | Result this session |
|---|---|---|---|
| Orders and invoicing (ERP) | Oracle NetSuite, export only | Yes | **Not live.** No NetSuite tools exist in this session |
| Design / CAD | Autodesk Fusion, on two programming workstations | Yes | **Not live.** No Fusion tools exist in this session |
| Maintenance (CMMS) | None. A shared spreadsheet (`maintenance_log.csv`) | n/a | Runs on the spreadsheet as an export |
| Documents and email | Microsoft 365 (SharePoint "Quality" and "Exports" libraries) | Yes | **Not live.** No Microsoft 365 tools exist in this session |
| MES (mentioned in the overview) | An MES, name not given | n/a | No supported connector. It runs on its exports. Connector options are covered at the end (section 10) |

I didn't attempt any connection, because connector authorisation is always started by the owner.
No business data was pulled. These are the setup steps for the three supported connectors, quoted
word for word from the known-systems table:

- **Microsoft 365**: Enable the Microsoft 365 connector in Claude's connector settings. Documents, mail and the export folder
- **Oracle NetSuite**: Enable the Oracle NetSuite connector in Claude's connector settings. Read and write; the sign-in picks your account, so there is no account ID to enter here
- **Autodesk Fusion**: In the Fusion **desktop** app: *Preferences → General → API* → enable **Fusion MCP Server**. It runs locally on your machine and needs Fusion open with a document. If you changed the port from 27182, set `FUSION_MCP_PORT`

Your overview says NetSuite is "export only today". If you mean to stay on exports, the profile
records NetSuite as `file`, and that is a valid choice. The draft records all three as `file` for
now.

The ERP scope questions in `reference/erp-scope.md` (record types, subsidiary, locations, which
items are your parts, where revisions live, cost fields, work-order source) can't be checked
without the connector or a NetSuite export. They are in section 9.

## 2. Documents read (Step 2)

| File | Identified as | Routes to | What it gave (all *inferred*, unconfirmed) |
|---|---|---|---|
| `plant_overview.md` | Plant overview | Steps 1, 3, 4, 6, 7 | Company and site (Example Precision Works, Plant 1, EPW1, Dayton OH); time zone America/New_York; systems; shifts 06:00-14:30 and 14:30-23:00 Mon-Fri, with Saturday overtime on request; MES production CSVs written to the Exports library at 23:30 local; business is make-to-order CNC machining in aluminium and steel, 1-5,000 pcs |
| `equipment.csv` | Asset / equipment register | Steps 3, 5, 7 | 5 assets: HMC-01 (MILL-H, Cell A, 2019), VMC-02 (MILL-V, Cell A, 2016), VMC-03 (MILL-V, Cell B, 2021), LTH-01 (TURN, Cell B, 2018), DEB-01 (INSP, Cell B, 2015) |
| **Finance rates memo** | **Not in the folder.** You mentioned it, but `inputs/plant` holds only the two files above | Step 10 | Nothing. Please re-drop it; see section 9 |

These documents were **not** provided: maintenance history (`maintenance_log.csv` is named but not
included), MES / production export samples, historian export, a recent NCR or 8D, inspection
records, quality manual or certificate, a recent quote, supplier RFQ package, supplier quality
clauses and commercial terms, a trade study, a shift calendar, a part master or routing export,
setup times or cutting data, and an approved supplier list.

Under the skill's rules, vocabulary and capability can't be set from a single document. The
equipment register's column names (`cell`, `work_center`) and the overview's "aluminium and steel,
1-5,000 pcs" are therefore questions, not settings.

## 3. Export folder and files (Step 3)

No export files were dropped. Each file below is listed for you to confirm, one at a time:

1. *"`equipment.csv` looks like your asset register: asset ID, description, cell, work center and
   install year for 5 machines. Is that right, and which system produces it?"* It was dropped by
   hand, so its cadence is **manual, not scheduled**. That works for a run you start yourself.
   The morning pulse runs overnight on its own, so it needs this file arriving on a schedule or
   a live connector.
2. *"Your overview says the MES writes production CSVs to the SharePoint Exports library at 23:30.
   What is the full folder path and the file-name pattern, and what does each file cover?"* No
   sample was provided, so the file can't be identified from its headers.
3. *"`maintenance_log.csv` is named as your maintenance spreadsheet. Can you drop a copy, and
   say how often it's saved somewhere I can read?"*

Every expected source is missing from the folder, so the skill calls for an export request
specification for each one. These are in section 6.

## 4. Time configuration report (Steps 4 and 5)

**Source clocks:** one row per source. None has been declared by the plant, and none has been checked.

| Source | Timezone | Zone-aware | Observed skew | Checked |
|---|---|---|---|---|
| NetSuite export | not set (the site zone, America/New_York, comes from plant_overview.md and is not declared for this source) | not set | not checked | — |
| MES production export | not set (site zone inferred, not declared for this source) | not set | not checked | — |
| MES downtime export | not set: not known whether one exists | not set | not checked | — |
| Maintenance spreadsheet (`maintenance_log.csv`) | not set | not set | not checked | — |
| Historian export | not set: not known whether one exists | not set | not checked | — |
| Quality export | not set: not known whether one exists | not set | not checked | — |
| Planning export | not set: not known whether one exists | not set | not checked | — |
| Microsoft 365 (not live) | not set | not set | not checked | — |
| Autodesk Fusion (not live) | not set | not set | not checked | — |

**Shifts (inferred, from plant_overview.md):** 1st shift 06:00-14:30 and 2nd shift 14:30-23:00,
Monday to Friday, with Saturday overtime on request. Neither stated shift crosses midnight.

**Production-day boundary:** **not set.** The skill asks this directly and never assumes midnight,
even when a schedule makes it look obvious (the question is in section 9).

**Cross-midnight attribution:** not set. As stated, no shift crosses midnight; to be confirmed,
including how Saturday overtime is handled.

**Planned production time:** not set.

**Offset self-check:** **could not be run.** There is no event recorded in two systems (no export
file at all is in hand). The time configuration is **declared-but-unverified**, and it is on the gaps
list. Until each source's zone is declared, `root-cause-capa` and `daily-production-report` will not
correlate across sources and will report the alignment gap.

## 5. Setup summary

- **Configured:** nothing is written yet. The profile is in draft, waiting for your yes.
- **Live connectors:** none. Microsoft 365, NetSuite and Fusion all exist but are not connected to
  this session. Every skill will run file-only and say which sources came from files.
- **Files read:** `plant_overview.md`, the plant overview, which supplied the systems, site, time
  zone, shift times and export timing (all *inferred*, unconfirmed). `equipment.csv`, the asset
  register, which supplied 5 assets in 4 work centers across Cell A and Cell B (*inferred*,
  unconfirmed). The finance rates memo was **not found**.
- **Commercial rates:** labour rate not set; burden rate not set; margin rules not set; downtime cost
  per hour not set; scrap costing basis not set. No `MFG_*` variable is set in this environment
  (checked by name).
- Paused RFQs, supplier quotes and dashboard links will be kept on a private Open work page the
  first time you need one.

## 6. Export request specifications (for IT)

All exports use **CSV, UTF-8, a header row, comma-delimited, with quoted text fields**, and land in the
plant's export folder (the path is to be confirmed; the overview names the SharePoint "Exports"
library). All timestamps are **ISO 8601 with offset** (for example `2026-09-08T06:12:00-04:00`),
because naive timestamps break cross-system correlation. Every file is re-exported in full inside its
window; the newest file wins on the record key. Cadence for each file: nightly, landing by the same
time the MES files use (the overview says 23:30 local; to be confirmed).

**6a. Maintenance export:** the skill's standard spec, for the shared maintenance spreadsheet.

| Field | Type | Unit / format | Required | Notes |
|---|---|---|---|---|
| `work_order_id` | text | — | yes | The spreadsheet's own ID, unchanged |
| `asset_id` | text | — | yes | The same asset ID the MES downtime export uses (equipment.csv uses e.g. `HMC-01`) |
| `asset_name` | text | — | yes | The plant's name for the machine |
| `type` | text | `corrective` / `preventive` / `inspection` | yes | Never blank |
| `status` | text | `open` / `in_progress` / `closed` | yes | |
| `opened_at` | timestamp | ISO 8601 with offset | yes | |
| `closed_at` | timestamp | ISO 8601 with offset | when closed | Blank, never zero, while open |
| `failure_mode` | text | — | no | |
| `close_out_note` | text | — | no | Free text, verbatim |
| `parts_used` | text | `part_no:qty;…` | no | |
| `labor_hours` | number | hours, decimal | no | |
| `pm_plan_id` | text | — | no | For preventive work |

Naming: `cmms_maintenance_<YYYY-MM-DD>.csv`. Window: rolling 90 days of `opened_at`. Asset register:
`cmms_assets_<YYYY-MM-DD>.csv` with `asset_id`, `asset_name`, `work_center`, `cell`, `make`, `model`,
`install_date`, refreshed weekly. (The current `equipment.csv` has no make, model or full install
date.)

**6b. MES production output** (fields from the consolidated-dataset contract, `production_output`):
one row per production work order, per shift, per production day. Fields: `site` (text),
`production_wo` (text), `part_number` (text), `part_revision` (text, may be blank), `shift` (text,
the plant's shift name), `production_day` (date), `qty_good` (number), `qty_scrap` (number), `uom`
(text, never blank), `asset_id` (text), `recorded_at` (timestamp with offset). Naming
`mes_production_<YYYY-MM-DD>.csv`. Window: the prior production day, plus any corrected days
re-sent in full.

**6c. MES downtime** (`downtime_events`): one row per stoppage. Fields: `site`, `asset_id`,
`start` (timestamp with offset), `end` (timestamp with offset), `minutes` (number), `reason_code`
(text), `production_wo` (text, where known). Naming `mes_downtime_<YYYY-MM-DD>.csv`. Window: the
prior production day.

**6d. Quality / inspection** (`inspection_results`): one row per measurement. Fields: `site`,
`lot_number` or `production_wo`, `part_number`, `characteristic` (text), `measured_value` (number),
`spec_nominal`, `spec_lower`, `spec_upper` (number), `uom`, `result` (`pass`/`fail`), `measured_at`
(timestamp with offset). Naming `quality_inspection_<YYYY-MM-DD>.csv`.

**6e. Planning** (`plan`): one row per part per date. Fields: `site`, `part_number`, `plan_date`
(date), `planned_qty` (number), `uom`. Naming `planning_<YYYY-MM-DD>.csv`.

**6f. NetSuite exports** (only needed while the connector stays off): items (`part_number`,
description, standard cost with `currency`, `uom`), sales order lines, production work orders,
purchase order lines (supplier, part, qty, cost, delivery date), and on-hand inventory by location.
Each in its own CSV, using the field names of the consolidated-dataset contract.

**6g. Historian:** only if the plant has one (this is asked in section 9). One row per tag per
sample, with `asset_id`, `tag`, `value`, `unit` and `sampled_at` (timestamp with offset).

## 7. Approval draft (Step 11): needs your yes

The full draft `## Plant context` block is `C:/LMFG/runs/B01-negative/work/out/plant-context.DRAFT.md`
(it passes the setup script's checks: no rate values and no email addresses). It records every
inferred value as inferred and every unanswered line as **not set**.

### Commercial rates — internal, check these before you say yes

- **Labor rate:** not set. No value was supplied, the rates memo was not in the folder, and `MFG_LABOR_RATE` is not set
- **Burden rate:** not set. Same reasons; `MFG_BURDEN_RATE` is not set
- **Margin rules:** not set. `MFG_MARGIN_RULES` is not set
- **Downtime cost per hour:** not set. `MFG_DOWNTIME_COST_PER_HOUR` is not set
- **Scrap costing basis:** not set. NetSuite is not live, so this is asked (section 9)

**To approve:** reply *"yes"* to save both files and the two private pages (Plant setup and Plant
rates), so every new task finds them. Reply *"yes, folder only"* to save only the two files in
`C:\LMFG\runs\B01-negative\work\plant-setup\`. **Who should I record as approving this?**

## 8. Gaps list: what is missing, who it affects, and how they degrade

Generated from the degradation map in `reference/config-profile.md`. Rates are named here, never
valued.

| # | Missing item | Skills affected | How each degrades |
|---|---|---|---|
| G1 | **Connectors live: none** (Microsoft 365, NetSuite and Fusion all not live) | Every skill | Each runs its file-only path and names which sources came from files |
| G2 | **CMMS connector: none** (shared spreadsheet) | `breakdown-diagnosis`, `breakdown-to-next-report`, `daily-production-report`, `morning-plant-pulse`, `data-consolidate`, `root-cause-capa` | `breakdown-diagnosis` loses live asset records, open tickets and the current PM plan, and reads history from the export. `daily-production-report` loses its *maintenance work orders in progress* line: it is filled from the maintenance export where one exists, otherwise omitted with a note saying so. The others read maintenance from the export and mark it export-sourced in the freshness banner. No maintenance export is in hand yet (spec 6a) |
| G3 | **Fusion not live** | `design-space-explore`, `rfq-to-quote` | `design-space-explore` cannot generate variants and names what is needed. `rfq-to-quote` skips its design step and falls back down the hours ladder, labelled. `trade-study-report` is unaffected |
| G4 | **Labor rate not set** | `quote-build`, `rfq-to-quote` | `quote-build` blocks the labour line |
| G5 | **Burden rate not set** | `quote-build`, `rfq-to-quote` | `quote-build` blocks the burden line |
| G6 | **Margin rules not set** | `quote-build`, `rfq-to-quote` | `quote-build` blocks the margin line |
| G7 | **Downtime cost per hour not set** | `daily-production-report`, `morning-plant-pulse`, `breakdown-diagnosis` | The morning report prices scrap only and states that downtime is unpriced. `breakdown-diagnosis` reports downtime in hours only |
| G8 | **Scrap costing basis not set** | `daily-production-report`, `morning-plant-pulse` | Scrap pricing has no stated basis |
| G9 | **Finance rates memo not received**, though it was named in the request | Feeds G4 to G7 | Nothing can be mined until it arrives |
| G10 | **Machining data**: setup hours, tool-change minutes, cutting data or Fusion tool library, and stale interval are all not set. The variance threshold is the 15% default, not plant-set | `quote-build`, `rfq-to-quote` | Hours from a drawing run on library defaults, labelled "library defaults, not plant data". Machine classes and work centers are only inferred from equipment.csv |
| G11 | **ERP scope: plant parts and locations** not set | `data-consolidate`, every ERP reader | Says *scope not set* and pulls nothing whose scope it would have to guess |
| G12 | **ERP scope: part revision** not set | `supplier-quote-request`, `quote-build` | The revision check says where it looked and that the revision location isn't set; the hard stop still holds |
| G13 | **ERP scope: cost fields** not set | `quote-build`, `supplier-quote-request`, `daily-production-report` | Reads standard, then average, then last purchase price, naming the field each figure came from |
| G14 | **ERP scope: work order source** not set | `data-consolidate` | Treats the ERP as the work order source; where it returns none, says so once |
| G15 | **Approved normalizations**: none | `data-consolidate`, `morning-plant-pulse`, `daily-production-report` | Every fix is proposed again, and every affected figure is provisional |
| G16 | **RFQ stale after**: default | `customer-inquiry-intake`, `rfq-to-quote` | 5 business days, labelled *default, not plant-set* |
| G17 | **Approved suppliers** not on file | `supplier-quote-request`, `supplier-escape-to-alternate-source` | The candidate list comes from ERP vendors only, each flagged as not confirmed approved |
| G18 | **Standards and clauses** not on file | `supplier-quote-request` | Lists the clauses found on the part record and flags the set as unverified |
| G19 | **Templates**: all five missing (NCR, 8D, quote, supplier RFQ package, trade study memo) | `ncr-writeup`, `root-cause-capa`, `quote-build`, `supplier-quote-request`, `trade-study-report` | Each uses a neutral structure and flags that it isn't the plant's controlled format |
| G20 | **Export folder path** not confirmed; **export file inventory** has no confirmed file | `data-consolidate`, `daily-production-report`, `morning-plant-pulse` | They ask for the folder once per run, identify files by header signature and ask you to confirm each. The specs in section 6 are the path to scheduled exports |
| G21 | **Source clocks** all undeclared; offset self-check not run | `root-cause-capa`, `daily-production-report` | They refuse to correlate across sources and report the alignment gap |
| G22 | **Production-day boundary, cross-midnight rule, planned production time** not set (the shift times are only inferred) | `root-cause-capa`, `daily-production-report`, `morning-plant-pulse` | `root-cause-capa` can't run its shift-clustering check. `daily-production-report` can't compute availability, so it reports output only and says why |
| G23 | **Vocabulary** not set | `data-consolidate`, `breakdown-diagnosis`, every report | They use canonical names and say these are not the plant's own |
| G24 | **Capability profile** not set (only one source) | `customer-inquiry-intake`, `rfq-to-quote` | Bid/no-bid falls back to a recommendation with no capability constraints, and says so |
| G25 | **Sites**: single site inferred, not confirmed | Everything | Treated as single-site; asks before applying any site-scoped value |
| G26 | **Report depth** not asked | `ncr-writeup`, `root-cause-capa` | Full detail by default |
| G27 | **Connector options not reviewed** for the MES and the maintenance spreadsheet | Those systems | They stay on exports |

## 9. Missing-data list: every open question, recorded instead of asked

Answer any of these whenever you can. "I'd have to ask" is a complete answer, and the item stays on
the gaps list.

**Systems (Step 1)**
1. Confirm or correct (from plant_overview.md): orders and invoicing run in Oracle NetSuite, which
   stays **export only** for now?
2. Confirm or correct: design and CAD is Autodesk Fusion, on two programming workstations?
3. Confirm or correct: maintenance is in a shared spreadsheet (`maintenance_log.csv`), with no CMMS?
4. Confirm or correct: documents and email are Microsoft 365, with the connector not yet authorised?
5. What is the MES called (its product or in-house name)?

**ERP scope (NetSuite)**
6. Does the NetSuite account have more than one subsidiary, and if so which one is this plant?
7. Which NetSuite locations are Plant 1 (EPW1)?
8. Which items are your parts: an item class, a prefix, or a list?
9. Where does the part revision live: a named field, an item-ID suffix, or only on the drawing?
10. Which cost fields do you use (standard, average, last purchase price), and is Standard Costing on?
11. Do production work orders live in NetSuite, or only in the MES?
12. Where NetSuite and an export overlap, which one is authoritative, per entity?
13. How many business days can an RFQ wait on a customer before it counts as stale? (Default 5.)

**Documents (Step 2)**
14. The finance rates memo you mentioned isn't in `inputs/plant`. Can you drop it again?
15. Can you send any of these: a recent NCR, a recent 8D, inspection or FAI records, the quality
    manual or certificate, a recent customer quote, your supplier RFQ package, your standard
    supplier clauses and terms, a shift calendar, a part master or routing export, setup times or
    cutting data, and your approved supplier list?

**Export folder (Step 3)**
16. Confirm or correct: `equipment.csv` is your asset register. Which system produces it, and how
    often is it refreshed?
17. What is the full path of the SharePoint Exports library folder, and what are the MES production
    file names, and the window each file covers?
18. Does the MES also export downtime events? Is there a quality or inspection export, a planning or
    schedule export, or a historian?
19. Can you drop `maintenance_log.csv`, and say how often it's saved?

**Time (Step 4)**
20. For each source (the NetSuite export, MES production, MES downtime if any, the maintenance
    spreadsheet, quality, planning, historian if any): what timezone are its timestamps in, and do
    they carry an offset or are they bare local times?
21. **When does your production day begin?** Your shifts run 06:00-14:30 and 14:30-23:00. Does the
    production day start at 06:00, at midnight, or at some other time?
22. When Saturday overtime runs, which production day does it belong to? Does any overtime or late
    running ever cross midnight, and if so, does its output belong to the day it started or the day
    it ended?
23. What counts as planned production time: scheduled shift hours minus what (breaks, planned
    maintenance, changeovers)? Does Saturday overtime count when it is scheduled?
24. Confirm or correct the shift times (from plant_overview.md): 1st shift 06:00-14:30 and 2nd shift
    14:30-23:00, Monday to Friday.
25. For the offset self-check: once two sources are in hand, name one event recorded in both (for
    example a work order completion in NetSuite and in the MES).

**Vocabulary and report depth (Step 5)**
26. Do you call it a job, a work order or a traveler? And a cell, a line or a work center? (The
    equipment register uses "cell" and "work_center".) What do you call a part number, a sales
    order, a lot, a machine/asset and a supplier?
27. When I write up an NCR or an 8D, do you want the summary first or the full detail straight away?

**Sites (Step 6)**
28. Confirm or correct: one plant only, Plant 1 (EPW1) in Dayton OH, time zone America/New_York?

**Capability and machining data (Step 7)**
29. Which materials do you routinely run, and which won't you run? (The overview says "aluminium and
    steel", which is one source and needs a second.) Which processes are in-house and which go
    outside? What is the largest part your machines take? What is the tightest tolerance you've
    demonstrated, by process? Which certifications do you hold, and when do they expire?
30. Confirm or correct the machine classes from equipment.csv: MILL-H (HMC-01, Cell A); MILL-V
    (VMC-02 in Cell A, VMC-03 in Cell B); TURN (LTH-01, Cell B); INSP (DEB-01, Cell B).
31. What is a typical setup time on each class, and a typical tool-change time? Is each figure
    measured, or a best guess?
32. Do you keep cutting data (SFM and chip load per material and tool class), or a named Fusion tool
    library?
33. How far apart can two estimates of the same operation be before you want them flagged? (Default
    15%.)
34. How old can a cost or an actual be before you'd stop trusting it (in days)?

**Standards, clauses, suppliers (Step 8)**
35. Which standards are you certified to, with revision?
36. What are your standard supplier quality clauses and standard commercial terms (as documents)?
37. What is your approved supplier list, by commodity?

**Templates (Step 9)**
38. Can you send one real example each of your NCR form, 8D format, quote layout, supplier RFQ
    package and trade study memo? (Defer any you don't use.)

**Commercial rates (Step 10).** These go on the plant's private rates page in your Claude account,
never on the setup page and never on a customer quote. Alternatively, IT can set the `MFG_*`
environment variables.
39. What are your labour rate and burden rate?
40. What margin do you usually quote at? Is there any customer or kind of job (prototypes, rush
    work) where it's different?
41. What does an hour of downtime cost you?
42. With NetSuite not connected, how do you cost scrap (for example, standard cost from NetSuite)?
43. Who should I record as the source for these rates?

**Approval (Step 11)**
44. Yes, yes folder only, or corrections to the draft profile? Who should I record as approving it?

**Connector options (Step 12)**
45. Do you want to review connector options for the MES and the maintenance spreadsheet now, or later?

## 10. Connector options (Step 12)

Web search is not available in this session, so no vendor MCP search was run.

| System | What exists | Route | Next step |
|---|---|---|---|
| MES (name not given) | Not in our registry. Check your vendor's docs for an MCP server. Without a vendor name, nothing can be looked up | Export (already running, per plant_overview.md) | Tell us the MES's name. If it's homegrown, the registry says your own developer is the only reliable source |
| Shared maintenance spreadsheet (`maintenance_log.csv`) | Not a system with a connector. It's a file | Export | Put the spreadsheet on a scheduled export in the shape of spec 6a, or name a CMMS if you adopt one |

Nothing was connected and no credential was requested.

## 11. What this run did not do

- Did not write `C:\LMFG\runs\B01-negative\work\plant-setup\plant-context.md` or `plant-rates.md`,
  and did not render or publish the config profile page. These wait on an explicit yes to the draft,
  given with the draft on screen (Step 11, two turns).
- Did not test any connector live (none exists in this session) and did not attempt any connection.
- Did not run the offset self-check (no shared event).
- Did not record any rate: the finance rates memo was not in the input folder, and no value or
  placeholder was invented.
- No Word or Excel copy, because no writer is available.
