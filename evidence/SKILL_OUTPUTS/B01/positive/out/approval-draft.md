# Approval draft - Plant setup: Example Precision Works

Status: DRAFT, shown for approval. Nothing has been saved as the plant's setup and no rates file has been written.
Onboarding Step 11 writes the profile only after an explicit yes given after this draft has been seen;
"set up the plugin" started the work, it does not approve a draft nobody had seen yet.

All values come from three SYNTHETIC dropped files (plant_overview.md, equipment.csv, rates_memo.txt) and are labelled
*inferred* until someone confirms them in their own step. Open questions are in `missing-data-list.md`.

## 1. The `## Plant context` block (no rate values)

The full draft block is `out/plant-setup-draft/plant-context.md` (rendered as `out/config-profile-page/index.html`).
It is reproduced here for review:

- Company: Example Precision Works - one site, Plant 1, EPW1, Dayton OH (default)
- Systems: ERP Oracle NetSuite - file; CAD Autodesk Fusion - file; CMMS none (shared spreadsheet) - file;
  Documents Microsoft 365 - file; MES (product not named) - file. No connector live this session.
- Export folder: SharePoint "Exports" library; MES production CSVs nightly at 23:30 local (inferred)
- ERP scope: every line not set (record types not checked - no connector); RFQ stale after 5 business days (default, not plant-set)
- Documents read: plant_overview.md, equipment.csv, rates_memo.txt - all inferred, not confirmed
- Export files: equipment.csv (manual), MES production CSVs (not provided), maintenance_log.csv (not provided)
- Machining data: MILL-H (HMC-01, Cell A), MILL-V (VMC-02 Cell A, VMC-03 Cell B), TURN (LTH-01, Cell B),
  INSP (DEB-01, Cell B), OUTSIDE-FINISH (anodize). Setup hours, tool-change times, cutting data, stale interval: not set.
  Variance flag threshold 15% - default, not plant-set
- Approved suppliers: none on file
- Source clocks: eight sources, one row each, all not checked; offset self-check not run (no shared event)
- Site block: America/New_York; shifts 06:00-14:30 and 14:30-23:00 Mon-Fri, Saturday overtime on request;
  production-day boundary, cross-midnight / Saturday attribution, planned production time, vocabulary,
  capability: not set
- Report depth: full (default)
- Commercial rates: each by state only - see section 2 for the values

## 2. Commercial rates - internal, check these before you say yes

Where they go: onto the plant's private rates page in your Claude account (`plant-setup/plant-rates.md` in this
folder), never the setup page, never a customer quote. Anyone at the plant who can see this plugin's memory can read
it. A plant that wants the stricter route can set the `MFG_*` environment variables instead.
Environment check (by name, values not printed): MFG_LABOR_RATE, MFG_BURDEN_RATE, MFG_MARGIN_RULES,
MFG_DOWNTIME_COST_PER_HOUR, MFG_SCRAP_COSTING_BASIS - none set.

Source for every figure below: `rates_memo.txt` (finance memo dated 1 Oct 2026). Shown here once.

| Rate | Proposed rates-file line | Fits the plugin's field? |
|---|---|---|
| Labor rate | not set | The memo gives no separate labor rate |
| Burden rate | not set | The memo gives no separate burden rate |
| Fully burdened shop rate by work center (as said) | MILL-H 145 USD/h - MILL-V 95 USD/h - TURN 85 USD/h - INSP 60 USD/h | **No.** The plugin's fields are one labor rate plus one burden rate; a per-work-center fully burdened rate is recorded as said and is on the gaps list until the plant says how it should be used |
| Margin rules | `{"default":0.18,"by_customer":{},"by_job_type":{}}` (memo: "Target margin 18 percent") | Yes, as a default. No customer or job-type overrides stated |
| Material markup (as said) | 12 percent | **No** - not a margin-rules field; recorded as said, on the gaps list |
| Outside processing (anodize) markup (as said) | 10 percent | **No** - not a margin-rules field; recorded as said, on the gaps list |
| Downtime cost per hour | not set | Not in the memo; asked, never derived |
| Scrap costing basis (not sensitive) | standard material plus value-added labour at the work centre where scrapped | Yes |

**Given by:** not stated in the memo or the request. Each confirmed rate must carry the name of the person giving it
and the date; the name is asked, never inferred.

## 3. What is needed to approve

- **Who should I record as giving these rates, and as approving this setup?**
- Reply **"yes"** (writes `plant-setup/plant-context.md` and `plant-setup/plant-rates.md` in this folder and saves
  both private pages, so every new task finds them) or **"yes, folder only"** (files only, no pages).
- Or correct any line first. A yes covers exactly what is shown above, nothing added afterwards.
