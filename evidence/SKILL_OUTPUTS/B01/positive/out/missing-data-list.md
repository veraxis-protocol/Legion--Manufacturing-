# Missing-data list - Example Precision Works (Plant 1, EPW1)

Onboarding could not run its interview live, so every question it would have asked is recorded here instead of
waiting. Where a dropped file already answered, the question is *confirm or correct* and names the file. Nothing
below blocks setup; each unanswered item stays a gap, and the column on the right says which skills it limits and
how they degrade (from the onboarding degradation map). Gap items never show a rate value.

Sources read: `plant_overview.md`, `equipment.csv`, `rates_memo.txt` (all SYNTHETIC test data).

## A. Approval (Step 11) - blocks writing the profile, not setup

| # | Question | Affects | Until answered |
|---|---|---|---|
| A1 | Do you approve the draft in `approval-draft.md`? Reply "yes" (files plus both private pages) or "yes, folder only". | Every skill | No `## Plant context` or `## Plant rates` file is written; every skill finds no profile and runs on defaults, asking each run |
| A2 | Who should I record as approving the setup and as the source of the commercial rates? | Every confirmed rate; `quote-build`, `daily-production-report`, `breakdown-diagnosis` | Rates cannot be recorded as confirmed (no name to put on them) |

## B. Systems (Step 1)

| # | Question | Affects | Until answered |
|---|---|---|---|
| B1 | Confirm or correct: ERP is Oracle NetSuite, export only, no API access granted yet (plant_overview.md). | All ERP readers: `data-consolidate`, `quote-build`, `customer-inquiry-intake`, `supplier-quote-request`, `ncr-writeup`, `root-cause-capa`, `daily-production-report` | File-only path; every ERP-sourced figure named as export-sourced. NetSuite connector not live this session; setup step quoted in setup-summary.md |
| B2 | Confirm or correct: CAD/CAM is Autodesk Fusion on two programming workstations (plant_overview.md). | `design-space-explore`, `rfq-to-quote` | Fusion not live this session: `design-space-explore` cannot generate variants; `rfq-to-quote` skips its design step and hours fall down the ladder, labelled |
| B3 | Confirm or correct: no CMMS - maintenance kept in a shared spreadsheet, maintenance_log.csv (plant_overview.md). Can that spreadsheet be exported on a schedule (spec in export-request-spec.md)? | `breakdown-diagnosis`, `breakdown-to-next-report`, `daily-production-report`, `morning-plant-pulse`, `data-consolidate`, `root-cause-capa` | `breakdown-diagnosis` has no live asset records, open tickets or PM plan and reads history from the export only; `daily-production-report` loses its maintenance-work-orders-in-progress line (from the export where one exists, else omitted and said); the others name maintenance as export-sourced |
| B4 | Confirm or correct: documents and email are Microsoft 365, SharePoint "Quality" and "Exports" libraries, connector not authorised yet (plant_overview.md). | Every skill reading documents, templates, exports | Files must be dropped in; Microsoft 365 connector not live this session |
| B5 | What is the MES product called? (plant_overview.md says "the MES" but does not name it.) | Step 12 connector options; `data-consolidate`, `daily-production-report`, `morning-plant-pulse` | Runs on exports; connector options not reviewed for the MES |
| B6 | Do you have a historian / sensor system, a quality / inspection system, and a planning / scheduling tool? If so, what are they? | `root-cause-capa`, `breakdown-diagnosis`, `daily-production-report`, `inspection-to-capa` | Sensor windows, inspection results and plan-vs-actual unavailable; output against plan cannot be computed without a plan source |

## C. Documents (Step 2)

| # | Question | Affects | Until answered |
|---|---|---|---|
| C1 | Can you drop in: a recent NCR, a recent 8D, inspection / FAI records, your quality manual or ISO certificate, a recent customer quote, your supplier RFQ package, standard supplier quality clauses and commercial terms, a trade study memo (if any), a part master / routing export from NetSuite, machine setup times or cutting data, and the approved supplier list? | Steps 7-9 | Each later question is asked directly instead of confirm-or-correct |

## D. Export folder and files (Step 3) - one at a time

| # | Question | Affects | Until answered |
|---|---|---|---|
| D1 | `equipment.csv` looks like your asset register - asset_id, description, cell, work_center, install_year, five machines. Is that right, and is it kept anywhere on a schedule or only by hand? | `data-consolidate`, `breakdown-diagnosis`, `daily-production-report` | Identity unconfirmed; recorded as manual, not scheduled |
| D2 | What is the exact path of the "Exports" library folder the MES writes to? | `data-consolidate`, `daily-production-report`, `morning-plant-pulse` | Asked once per run; scheduled skills cannot find the files |
| D3 | What are the MES production CSV file names, and what does each cover (prior day, shift, rolling window)? Can you drop one in so I can read its headers? | Same | Not identified; `morning-plant-pulse` cannot run unattended |
| D4 | Does the MES also export downtime events? If not, spec provided in export-request-spec.md. | `daily-production-report` (availability, downtime log), `breakdown-diagnosis`, `morning-plant-pulse` | Downtime log and availability cannot be computed |
| D5 | Can maintenance_log.csv be dropped in, and saved to the Exports library on a schedule? | See B3 | See B3 |
| D6 | Can NetSuite exports (items, sales orders, work orders, purchase orders, inventory, routings) be scheduled to the Exports library? | `data-consolidate`, `quote-build`, `ncr-writeup`, `supplier-quote-request` | ERP data only when dropped by hand |
| D7 | Quality / inspection and planning exports: do they exist? If not, specs provided in export-request-spec.md. | `root-cause-capa`, `inspection-to-capa`, `daily-production-report` | Missing sources named in every freshness banner |

## E. Time configuration (Step 4) - highest-risk group

| # | Question | Affects | Until answered |
|---|---|---|---|
| E1 | Confirm or correct: the plant runs on America/New_York time (plant_overview.md). | `root-cause-capa`, `daily-production-report` | Site timezone inferred only |
| E2 | For each source - NetSuite export, MES production export, MES downtime export, maintenance spreadsheet, historian, quality export, planning export, Microsoft 365 - what timezone are its timestamps in, and do they carry an offset or are they bare local time? | `root-cause-capa`, `daily-production-report`, `breakdown-diagnosis` | A naive source with no declared zone: any skill correlating it refuses and reports the alignment gap |
| E3 | When does your production day begin? (Asked directly whatever the shift times suggest.) Your 2nd shift ends at 23:00 - does any work run past midnight, and if so which day does it belong to, the day it started or the day it ended? | `daily-production-report`, `root-cause-capa`, `morning-plant-pulse` | `daily-production-report` cannot compute availability (output only, says why); `root-cause-capa` cannot run its shift-clustering check and treats cross-midnight attribution as unresolved |
| E4 | Confirm or correct: 1st shift 06:00-14:30, 2nd shift 14:30-23:00, Monday-Friday (plant_overview.md). | Same | Shift pattern inferred only |
| E5 | Saturday overtime "on request": which production day does it belong to, and does it count as planned production time when it runs? | `daily-production-report` | Saturday output attribution and availability unresolved |
| E6 | What counts as planned production time - scheduled shift hours minus what (breaks, planned maintenance windows, scheduled changeovers)? | `daily-production-report` (OEE availability) | Availability denominator undefined |
| E7 | Offset self-check: please provide one event recorded in two systems (e.g. a work order completion in both the NetSuite export and the MES export). | `root-cause-capa`, `daily-production-report` | Clock config declared but unverified; cross-source correlation reported as unverified |

## F. Vocabulary and report depth (Step 5)

| # | Question | Affects | Until answered |
|---|---|---|---|
| F1 | Do you call it a job, a work order, or a traveler? (Maintenance tickets are also "work orders" - what do you call each?) | `data-consolidate`, `breakdown-diagnosis`, every report | Canonical names used, labelled as not the plant's |
| F2 | equipment.csv uses both "cell" (Cell A, Cell B) and "work_center" (MILL-H, MILL-V, TURN, INSP). Are those the words you use on the floor, and what do you call parts, lots, sales orders and suppliers? (Only one document so far, so not recorded.) | Same | Same |
| F3 | When I write up an NCR or 8D, summary first or full detail? | `ncr-writeup`, `root-cause-capa` | Full detail (default) |

## G. Sites (Step 6)

| # | Question | Affects | Until answered |
|---|---|---|---|
| G1 | plant_overview.md says "Plant 1 (site code EPW1)". Is this your only plant, or are there others? If others, which is the default? | Everything | Treated as single-site; any site-scoped value is asked before it is applied to another site |

## H. Capability and machining data (Step 7)

| # | Question | Affects | Until answered |
|---|---|---|---|
| H1 | Confirm or correct: make-to-order CNC machining, aluminium and steel, 1-5,000 pieces (plant_overview.md). Which alloys/grades routinely, and any you won't run? | `customer-inquiry-intake`, `rfq-to-quote` | Bid/no-bid degrades to a constraint-free recommendation and says so |
| H2 | Confirm or correct: in-house horizontal milling (HMC-01), 3-axis vertical milling (VMC-02, VMC-03), turning (LTH-01), deburr and inspection (DEB-01) (equipment.csv); anodize outside (rates_memo.txt). Anything else outside (heat treat, plating)? | Same | Same |
| H3 | Largest part each machine takes (equipment.csv gives only a 500 mm pallet on HMC-01 and an 8in chuck on LTH-01; no envelopes for VMC-02/03). | Same | Size envelope not set |
| H4 | Tightest tolerances you have demonstrated, by process (milling, turning)? | Same | Tolerance capability not set |
| H5 | Certifications held, with expiry dates? | `customer-inquiry-intake`, `supplier-quote-request` | Not set |
| H6 | Confirm or correct the machine classes: MILL-H = HMC-01 (Cell A); MILL-V = VMC-02 (Cell A) and VMC-03 (Cell B); TURN = LTH-01 (Cell B); INSP = DEB-01 (Cell B) (equipment.csv). | `quote-build`, `rfq-to-quote`, `data-consolidate` | Map unconfirmed; `cell` on routings degrades |
| H7 | Typical setup hours per machine class, and tool-change time on the mills and lathe - measured or a best guess? | `quote-build`, `rfq-to-quote` | Hours from a drawing run on library defaults, labelled "library defaults, not plant data" |
| H8 | Cutting data (SFM and chip load per material and tool class), or the name of your Fusion tool library? | Same | Same |
| H9 | How far apart can two estimates of the same operation be before you want it flagged? | `quote-build` | 15% default, labelled not plant-set |
| H10 | How old can a cost or an actual be before you'd stop trusting it (days)? | `quote-build` | Stale interval not set |

## I. ERP scope (Step 1, per erp-scope.md) - to answer once NetSuite exports or the connector are in hand

| # | Question | Affects | Until answered |
|---|---|---|---|
| I1 | Does your NetSuite account have more than one subsidiary; which is this plant? | `data-consolidate`, every ERP reader | *Scope not set*; nothing pulled whose scope would be guessed |
| I2 | Which NetSuite locations are Plant 1? | Same | Same |
| I3 | Which items are your parts (item class, prefix, or list)? | Same | Same |
| I4 | Where does the part revision live - a named field, the item-ID suffix, or the drawing only? | `supplier-quote-request`, `quote-build` | Revision check says the location is not set; the hard stop holds |
| I5 | Which cost field holds standard cost, average cost, last purchase price, purchase price? Is Standard Costing on? | `quote-build`, `supplier-quote-request`, `daily-production-report` | Reads standard, then average, then last purchase, naming the field; never a field equal to sell price |
| I6 | Do production work orders live in NetSuite or only in the MES? | `data-consolidate` | ERP treated as the work-order source |
| I7 | Where a NetSuite connector and export overlap later, which wins, per entity? | `data-consolidate` | Asked when it arises |
| I8 | How many business days may an RFQ wait on a customer before it is stale? | `customer-inquiry-intake`, `rfq-to-quote` | 5 business days, default, not plant-set |

## J. Standards, clauses, approved suppliers (Step 8)

| # | Question | Affects | Until answered |
|---|---|---|---|
| J1 | Which standards are you certified to, with revision (ISO 9001, AS9100, IATF 16949, other)? | `supplier-quote-request`, `customer-inquiry-intake` | Not set |
| J2 | Your standard supplier quality clauses (certs, FAI, PPAP level, right of access) - as a document? | `supplier-quote-request` | Clauses found on the part record listed and flagged unverified |
| J3 | Your standard commercial terms (payment, freight, packaging, liability, tooling)? | `supplier-quote-request` | Not set |
| J4 | Approved supplier list by commodity (bar stock, anodize, etc.)? | `supplier-quote-request` | Candidates from ERP vendors only, each flagged not confirmed approved; anodize single-source status unknown |

## K. Templates (Step 9)

| # | Question | Affects | Until answered |
|---|---|---|---|
| K1 | One real example each of: NCR form, 8D format, quote layout, supplier RFQ package, trade study memo (defer any you don't use). | `ncr-writeup`, `root-cause-capa`, `quote-build`, `supplier-quote-request`, `trade-study-report` | Neutral structure, flagged as not the plant's controlled format |

## L. Commercial rates (Step 10) - names only, values are in the approval draft

| # | Question | Affects | Until answered |
|---|---|---|---|
| L1 | Labor rate: the finance memo gives fully burdened shop rates per work center, not a labor rate and a burden rate. Should quotes use the per-work-center fully burdened rates (and if so how - as labor with zero separate burden?), or do you have a separate labor rate? | `quote-build`, `rfq-to-quote`, `daily-production-report`, `breakdown-diagnosis` | Not set: `quote-build` blocks the labor line |
| L2 | Burden rate: separate figure, or already inside the fully burdened rates? | Same | Not set: `quote-build` blocks the burden line |
| L3 | Margin: confirm the default from the finance memo; is any customer or kind of job (prototypes, rush) quoted differently? | `quote-build`, `rfq-to-quote` | Not set: margin line blocked |
| L4 | Material markup and outside-processing (anodize) markup in the memo do not fit the plugin's margin-rules shape (default / by customer / by job type). How should they be applied? Recorded as said meanwhile. | `quote-build` | Recorded as said, not applied |
| L5 | What does an hour of downtime cost you? (Asked, never derived from the shop rates.) | `daily-production-report`, `morning-plant-pulse`, `breakdown-diagnosis` | Morning report prices scrap only and says downtime is unpriced; `breakdown-diagnosis` reports downtime in hours only |
| L6 | Confirm or correct scrap costing basis: standard material plus value-added labour at the work centre where scrapped (rates_memo.txt). | `daily-production-report` | Inferred only |
| L7 | Is the finance memo of 1 Oct 2026 still current? | All rate consumers | - |

## M. Connector options (Step 12)

| # | Question | Affects | Until answered |
|---|---|---|---|
| M1 | Name the MES product (B5) so its connector options can be reviewed. | MES-fed skills | Connector options not reviewed |
| M2 | Web search was not available in this run: check your MES vendor's docs for an MCP server. | Same | Stays on exports |

**Total open items: 59 questions across 13 groups (A-M).** The profile's *Gaps open* line counts these.
