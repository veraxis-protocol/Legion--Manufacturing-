# Quote build - Northwind Robotics MB-2040 Rev C - DRAFT (estimator review)

Skill followed: `quote-build` (plugin skills/quote-build/SKILL.md, references hours-ladder, cost-buildup, date-and-load, revisions; shared secret-config, computed-figures, replies, contracts/intake-form). All data SYNTHETIC.
This file is the full reply of the run, saved as a copy. **No Word or Excel copy this session: no Word writer (python-docx) and no Excel writer (openpyxl) is installed, and installing packages is not allowed in this run.**

## Headline for the estimator

**No price can be produced. Every dollar line is blocked**, so the sendable block below contains no prices and is not releasable:

1. **No purchase orders in the inputs.** The request says our purchase orders are in `inputs/cost`; that folder holds only `closed_jobs.csv` and `routings.csv` (figures F1-F2). With no PO, no supplier quote and no standard cost, the material line has no source. It is not filled in.
2. **No rate is on file.** No `MFG_LABOR_RATE`, `MFG_BURDEN_RATE` or `MFG_MARGIN_RULES` is set, and no plant profile or plant rates file exists (`plant_setup.py find`: `exists: false`, `rates_exists: false`). Finance's memo (`inputs/rates_memo.txt`, 1 Oct 2026) is not a rate on file: under the skill's rules, a rate handed to a quote run is **not used for that run and not repeated back**. To use it, record it through `onboarding` ("update our labour rate", plus burden, margin rules and scrap costing basis), which stores it with a name and date, or set `MFG_LABOR_RATE` / `MFG_BURDEN_RATE` / `MFG_MARGIN_RULES` in the environment. The quote then completes. Note: the memo gives one fully burdened rate per work centre, while the plugin keeps labour and burden separate. Onboarding needs to record how that maps.
3. **No anodize vendor price or lead time** in the inputs. The outside-processing line is blocked.
4. **No MB-2040 routing or actuals** exist (F3, F5). All hours are rung 4, a stand-in from the similar MB-1880 Rev B bracket.
5. **No drawing is in the package.** The spec sheet is text only, so the geometry path is **A**. Any price, once rates and material exist, is **a budgetary estimate, never a firm quote**.

---

=== CUSTOMER QUOTE — SENDABLE ===

**BUDGETARY ESTIMATE - DRAFT - NOT FOR RELEASE (prices pending)**

To: Dana Whitfield, Northwind Robotics
Re: Motor bracket MB-2040, Revision C - your request of 2 Nov 2026
Template: plant quote template not on file; neutral structure used.

| Line | Part | Description | Qty | Unit price | Extended |
|---|---|---|---|---|---|
| 1 | MB-2040 Rev C | Motor bracket, 6061-T6 aluminium plate, black Type II anodize, laser-marked | 250 | pending | pending |
| 1 | MB-2040 Rev C | as above | 500 | pending | pending |
| 1 | MB-2040 Rev C | as above | 1,000 | pending | pending |

Delivery: first articles requested by 15 Jan 2027, monthly production deliveries after that. **Delivery date to be confirmed.**
Validity: to be stated.
Terms: payment, freight, packaging and liability were not stated in your request. Our standard terms will apply and will be stated on the issued estimate.

Assumptions and scope:
- This is a budgetary estimate based on the written specifications you provided, for planning only. It is not an offer. We will send a firm quotation on receipt of a released drawing.
- Priced to MB-2040 Revision C specification sheet dated 27 Oct 2026, with the M5 pattern at the Rev C position. Rev B drawings are excluded, per your engineering note of 29 Oct 2026.
- Tolerances as read: main bore dia 22.000 mm +0.021/-0.000 (H7); all other dimensions ISO 2768-m per the general note; Ra 1.6 um on the bore, Ra 3.2 um elsewhere; edge break 0.2-0.5 mm.
- Mounting-face flatness is not yet specified. This estimate excludes any flatness requirement until you confirm it, and may change when you do.
- Includes black Type II sulfuric anodize per MIL-A-8625, a material certificate with each lot, part number and lot code laser etched, and an AS9102 first article inspection report on the first lot.
- Laser-mark location to be advised by you.
- Quantities 250, 500 and 1,000 pcs are priced as separate release quantities. The indicated annual volume of about 4,000 pcs is not assumed.

Questions for you (recorded here; not sent):
1. Please send the released Rev C drawing.
2. What is the mounting-face flatness requirement?
3. Where should the part number and lot code be marked?
4. What are your payment, freight, packaging and liability terms?

=== END ===

**Outbound check on the block above** (secret-config, *The outbound document check*): no hours, ranges, rungs or paths; no rate value; the word margin is absent; no customer name except the addressee; no PO data; no pricing-rule description. **Passed.** It remains **not releasable** because every price is pending. Gate 4 belongs to the estimator: who should I record as releasing it? (Question recorded, not asked.)

---

=== INTERNAL COST SHEET — NOT FOR CUSTOMER ===

**ROM - rough order of magnitude. Path A: text specs, no drawing. Not a firm quote and not releasable as one.**

Part MB-2040, Rev C, priced to `MB-2040_spec_revC.md` (2026-10-27). Derived 2026-11-14. Intake: minimal, built by this run from the RFQ files (customer-inquiry-intake did not run). `bid_decision_state: draft`: no bid/no-bid ruling, so this proceeded on an unconfirmed recommendation at the user's request ("build the quote").

### Rates (secret-config resolution order)
| Rate | MFG_* variable | Plant rates file | State | Lines blocked |
|---|---|---|---|---|
| Labour rate | `MFG_LABOR_RATE` not set | no file at rates_path | **not set** | Labour, Setup $ |
| Burden rate | `MFG_BURDEN_RATE` not set | no file | **not set** | Machine & burden, Setup $ |
| Margin rules | `MFG_MARGIN_RULES` not set | no file | **not set** | Margin, all prices |
| Scrap costing basis | `MFG_SCRAP_COSTING_BASIS` not set | no file | **not set** | Scrap allowance $ |
| Outside-processing markup | (no plugin field) | no file | **not set** | Anodize sell |

The finance memo `inputs/rates_memo.txt` (1 Oct 2026) holds values for these but is not on file. It was not used, and its values are not restated here. Record them via onboarding step 10.

### Cost buildup (seven lines)
| Line | Status | Source / what is missing |
|---|---|---|
| Material (6061-T6 plate, 120x80x12 mm envelope) | **BLOCKED** | No PO (F2 = 0 files), no supplier quote, no standard cost in inputs. Blank size / stock allowance not defined (no drawing). Needs a PO with number and date, or a current supplier quote |
| Scrap allowance | Structure only | MB-1880 history: 1.96% (WO-7702) and 1.77% (WO-7811) (F9-F10). Shown as history for a similar part, not adopted. $ blocked (material price, scrap costing basis) |
| Labour | **BLOCKED $** | Hours below (rung 4). Rate not set |
| Machine & burden | **BLOCKED $** | Same hours. Rate not set |
| Setup | Structure shown, **$ blocked** | 105 min = 1.750 h per job (F11). Per pc: 0.00700 h @250, 0.00350 h @500, 0.00175 h @1000 (F31, F36, F41) |
| Outside processing (Type II black anodize) | **BLOCKED** | No vendor, price, date, lot charge or lead time in inputs |
| Tooling / NRE | **Not determined** | No fixture data. H7 bore and laser-mark fixture unknown. Amortized vs NRE: undecided; tooling ownership: undecided |
| Margin (own line) | **BLOCKED** | Margin rules not set |

**No job total and no unit price at any break is produced.** Every route to one (standard cost x qty, prior sell x qty, ballpark) is closed while rates and material are unset.

### Hours basis (per operation): all rung 4
Why not higher: rung 1, no MB-2040 routing (F3 = 0); rung 2, no MB-2040 closed jobs (F5 = 0); rung 3, no geometry estimate (path A text spec, design step did not run, no Fusion in this run). MB-1880 Rev B is a *different part*, so its routing and its actuals are both first-principles stand-ins. Cutting data basis: n/a. Toolpath check: not run, no CAM. Machining data / variance threshold: no Plant context, so **15% - default threshold, not plant-set**.

| Op | WC | Setup min (low/exp/high) | Run min/pc (low/exp/high) | Cross-checks (MB-1880 actuals vs MB-1880 routing) | Drivers / firm-up |
|---|---|---|---|---|---|
| 10 Saw & face blank | MILL-V | 20/20/20, no spread available | 1.5/1.5/1.5, no spread available | none (F13 = 0 rows) | MB-2040 routing |
| 20 Mill profile, bore, holes op1 | MILL-V | 45/45/52 | 6.2/6.2/6.700 | WO-7702: setup +15.6% **FLAG**, run +8.1%; WO-7811: setup +4.4%, run +4.5% | WO-7702 setup flag driver not recorded in data (first run of the two). H7 bore and Ra 1.6 finishing method not in the stand-in routing. Rev C hole positions differ from MB-1880 |
| 30 Op2 flip & finish | MILL-V | 29/30/34 | 3.1/3.1/3.350 | WO-7702: setup +13.3%, run +8.1%; WO-7811: setup -3.3%, run +2.6% | Flatness TBD may add finishing |
| 40 Deburr & inspect | INSP | 10/10/10, no spread available | 2.0/2.0/2.0, no spread available | none (F30 = 0 rows) | 0.2-0.5 mm edge break, AS9102 FAI effort |
| (not timed) Laser etch | - | - | - | - | No op in stand-in routing |
| (not timed) Anodize | outside | - | - | - | Outside process, lead time unknown |

`probable_standard` test: no actual row is within 1% of the routing (F17, F21, F25, F29). Actuals are `recorded`, still for a different part. Actual run min/pc = total / qty_completed. Whether scrapped pieces' run time is inside the total is unknown. Units are declared in the file headers (minutes).

### Quantity breaks (hours only; $ blocked)
| Qty | Setup h/job | Setup h/pc | Run h/job | MILL-V h | INSP h | Total h |
|---|---|---|---|---|---|---|
| 250 | 1.750 | 0.00700 | 53.33 | 46.58 | 8.50 | 55.08 |
| 500 | 1.750 | 0.00350 | 106.67 | 91.58 | 16.83 | 108.42 |
| 1,000 | 1.750 | 0.00175 | 213.33 | 181.58 | 33.50 | 215.08 |

**Extrapolation flag:** 1,000 pcs is 2.0x the largest closed job (500, WO-7811) (F8, F46), and that job was for a different part.

### Capability flags (before price)
No Plant context, so demonstrated capability is unknown. **Unchecked:** H7 bore +0.021/-0.000 on dia 22, Ra 1.6 on the bore. Not flagged as exceeding capability; flagged as **not checked**. Flatness is unspecified.

### Comparables
| Comparable | Why comparable | How MB-2040 differs / unknown |
|---|---|---|
| MB-1880 Rev B, WO-7702 (300 pcs, closed 2026-07-18) | Labelled "similar bracket" in routings.csv `source` | Different part. MB-1880 material, size, finish and tolerances are not in the inputs. No cost data in the closed-jobs file (minutes only). Rev C hole pattern |
| MB-1880 Rev B, WO-7811 (500 pcs, closed 2026-09-26) | same | same. Smaller than the 1,000 break |
No prior quote or order for Northwind or MB-2040 exists in the inputs (no quote files present). That is no precedent, not evidence of a new relationship.

### Date check
**Not checked against shop load:** no planning export. Work content on the stand-in basis (rung 4, MB-1880 routing): MILL-V 46.58 h / INSP 8.50 h at 250 (other breaks above). Material lead time unknown (no PO / supplier). Anodize lead time unknown. **No lead time can be stated, and 15 Jan 2027 FAI is not confirmed.** Confirm with scheduling, purchasing and the anodize vendor.

### Assumptions / exclusions (internal)
- Proceeded on a `draft` bid decision (no Gate 2) and an unconfirmed operation list (no Gate 3).
- Commercial terms null: plant standard terms are not on file either, so they need to be set.
- Ambiguity: Rev B vs Rev C hole pattern. Priced to Rev C; Rev B treated as superseded per customer engineering (rfq_email.txt line 21).
- Material cert, AS9102 FAI and laser etch are in scope but untimed or unpriced.

### Figures block
Computed by `work/scripts/figures.py` and saved at `out/figures-block_MB-2040.csv` (46 rows, F1-F46 in file order). Key rows: F1 files in inputs/cost = 2; F2 PO files under inputs = 0; F3 MB-2040 routing rows = 0; F4 MB-1880 B routing rows = 4; F5 MB-2040 closed-job rows = 0; F6 MB-1880 closed WOs = 2 (WO-7702, WO-7811); F7 span 2026-07-18 to 2026-09-26; all variances and break hours as in the tables above.

=== END ===

## Gaps (names only, no values)
Material price (PO); anodize vendor price and lead time; labour rate; burden rate; margin rules; scrap costing basis; outside-processing markup; plant profile (capability, machining data, quote template, standard terms, validity); planning export; MB-2040 drawing and routing; flatness requirement; marking location.

## Not produced
- Sales command-center page: nothing was quoted or sent, so there is nothing for it to read from.
- Word/Excel copies: no writer installed.
- Revision history: first draft, none.

## Records saved
- `out/records/intake_MB-2040_minimal.yaml`: `geometry_path: A`, `bid_decision_state: draft`, `line_bid_decision: draft`, missing register 8 rows, ambiguous register 1 row.
- `out/records/operation-record_MB-2040_revC.yaml`: 4 ops, all rung 4. 3 ops not timed.
