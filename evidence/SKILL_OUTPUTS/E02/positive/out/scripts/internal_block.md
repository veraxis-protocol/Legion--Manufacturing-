=== INTERNAL COST SHEET — NOT FOR CUSTOMER ===

**Line 2: ROM — rough order of magnitude. Path A: text specs, no drawing. Not a firm quote and not releasable as one.** (Line 1 is path C1: STEP-derived part list, no drawing.)

Quote Q-HARBOR-ROBOTICS-LAB-NOREF-20261112-01, draft 1, 2026-11-14. Inquiry NOREF-20261112, Harbor Robotics Lab. Proceeded on an **unconfirmed recommendation** (`bid_decision_state: draft`, `recommendation_provisional: true`) because the request asked for a draft quote. Plant quote template: **not on file** (no plant profile); neutral structure used. Site: not set.

### 1. Status of every cost line (20 sets)

| Cost line | Status | Basis / source | What unblocks it |
|---|---|---|---|
| Material | **Partial lower bound**: {{PRICED_IDS}} of {{PIDS}} part ids ({{PRICED_PCS}} of {{PCS}} pcs/set): USD {{MAT_SET}} per set, USD {{MAT_20}} for 20 sets. {{UNK_IDS}} part ids ({{UNK_PCS}} pcs/set) unknown | Price actually paid on PO-30710 (2026-10-20), PO-30711 (2026-10-20), PO-30744 (2026-11-02), 5052-H32, pro-rata by area (section 3) | Sheet gauge and flat patterns for the formed parts; a supplier quote for >10 mm stock; plant scrap allowance; nesting / kerf / workholding allowance |
| Scrap allowance | **Unknown** | No plant scrap allowance on file; the memo's scrap-costing rule is not a rate on file | Plant Context or `MFG_SCRAP_COSTING_BASIS` |
| Labour | **Blocked**: hours unknown; labour rate not on file | none | Hours (section 4) and labour rate |
| Machine and burden | **Blocked**: hours unknown; burden rate not on file | none | Same hours; burden rate |
| Setup | **Blocked**: setup hours unknown per part; structure in section 5 | none | Setup hours per part per work centre |
| Outside processing | Anodize: **excluded** by customer (EML:L13). Forming of 6 pcs/set: **unknown, unsourced** (no forming asset in equipment list). Material for the 17.8 mm part: unsourced | intake form; equipment.csv | Supplier quote (`supplier-quote-request`) or a no-bid on the formed parts |
| Inspection to ±0.02 mm (INSP) | **Unknown** | Inspection requirements are on the handoff's missing list | Customer's key-dimension list and inspection requirement |
| Tooling / fixtures | **Unknown**; amortized vs NRE not decided; ownership not decided | none | Operation list; estimator decision |
| Line 2 rail (purchased) | **Unknown** | No PO and no supplier quote for MGN9-170 in the inputs | Rail spec from customer, then a supplier quote |
| Margin | **Blocked**: margin rules not on file | none | `MFG_MARGIN_RULES` or a confirmed rate on the plant rates page |
| **Job total / unit price** | **Not produced** (required rates unset; hours unknown) | — | All of the above |

Rates: labour rate — not set (MFG_LABOR_RATE not set; no plant rates file). Burden rate — not set. Margin rules — not set. Scrap costing basis — not set. A finance memo was supplied with the inputs; it is not a rate on file and was not used. Blocked lines: labour, machine and burden, setup, margin, and therefore every price.

### 2. Capability flags (before any price)

| Flag | Value | Plant capability | Effect |
|---|---|---|---|
| Tolerance | ±0.02 mm on key dimensions, all {{PIDS}} part ids (readme line 129, "GB/T1840-M" as written) | **Unknown**: no demonstrated capability on file (no Plant context) | Cannot confirm; stated as scope in customer assumption 2. Key dimensions not identified |
| Forming | 5 part ids / 6 pcs per set are "CNC + Sheet Metal" | Equipment list ({{N_ASSETS}} assets, work centres {{WCS}}): {{N_FORM}} assets mention bend/brake/press/form/sheet | No in-house forming route visible; outside source or exclusion needed |
| Size envelope | Largest bbox dimension {{MAXDIM}} mm (03_LINK2) | Machine travels are not in equipment.csv | Unknown |
| Multi-axis | Not determinable (no feature list) | {{N_5AX}} assets mention 5-axis | Unknown until an operation list exists |
| Intake `constraint_violations` | [] (check was not run against a profile) | — | carried |

### 3. Material basis (price paid on named POs, dated)

Method (assumptions, all labelled): each pure-CNC part is cut from the thinnest 5052-H32 stock on PO whose thickness is at least the part's smallest bounding-box dimension; blank = the part's two larger bbox dimensions; cost = blank area × (PO unit price ÷ sheet area). **Lower bound**: no saw kerf, no workholding or facing stock (parts at 3.0 mm from 3 mm sheet have none), no nesting loss, no remnant credit, no scrap allowance. 5052-H32 is the temper we bought; the customer's temper is not stated. Prices as of 20 Oct and 2 Nov 2026; aluminium is volatile, so the customer quote carries a validity caveat.

Stock on PO: PO-30710 2026-10-20, AL5052-SH-3, 3 mm × 1220 × 2440, USD 148.60 each = USD {{P30710}}/m². PO-30711 2026-10-20, AL5052-PL-6, 6.35 mm × 610 × 1220, USD 171.25 = USD {{P30711}}/m². PO-30744 2026-11-02, AL5052-PL-10, 10 mm × 610 × 1220, USD 262.80 = USD {{P30744}}/m².

{{MATERIAL_TABLE}}

### 4. Hours basis, per operation

Variance threshold: **15% — default threshold, not plant-set.** No variance computed: no operation has two rungs.

Rung 1 (routing): none — no routing for any part in the inputs. Rung 2 (closed-job actuals): none — no work-order or actuals file. Rung 3 (geometry-derived): **refused** — there is no geometry estimate in contract form; the handoff carries bbox, volume and face count only, no feature list, no setups, no operation list, no `approval`, and `engineering_verdict: Z`; Gate 3 not passed; no Fusion and no plant cutting data. Rung 4 (first principles): **not quantified** — no plant setup hours, tool-change time or cutting data exist, and no hour is supplied by the model.

| Op | Work centre / cell | Rung | Path | Cutting data basis | Setup h (low/exp/high) | Run min/pc (low/exp/high) | Other rungs | Variance drivers | Toolpath check |
|---|---|---|---|---|---|---|---|---|---|
| Each of the {{PIDS}} part ids: machining ops (operation list not established) | Not assigned. Candidates in equipment.csv: MILL-V (VMC-02 Cell A, VMC-03 Cell B), MILL-H (HMC-01 Cell A); deburr/inspection INSP (DEB-01) | 4 (why not higher: no routing, no actuals, no confirmed geometry estimate) | first principles | n/a | unknown / unknown / unknown | unknown / unknown / unknown | none | n/a | not run — no Fusion, feature path not run |
| Forming, 5 part ids | No work centre | 4 | first principles | n/a | unknown | unknown | none | n/a | n/a |

What would firm the hours up: a current routing per part for v1.1, or a geometry estimate per part with its operation list confirmed at Gate 3, plus the Plant context `Machine classes` (setup hours, tool-change min) and `Cutting data` for 5052.

### 5. Quantity break and setup amortization

One break only: 20 sets ({{PCS20}} CNC pieces; 20 rails). No other breaks were requested (intake missing register).
Structure: setup cost per set = Σ over part ids (setup hours × burdened rate of its work centre) ÷ 20; run cost per set = Σ (run h/pc × qty per set × rate). Dollar values blocked (hours and rates). Setup and run are kept separate; no lumped source exists.

### 6. Margin

Margin line: **blocked — margin rules not on file.** No customer-specific or job-type rule could be read.

### 7. Comparables

None. {{N_INPUTS}} input files enumerated; {{N_HIST}} are routings, actuals, work orders, prior quotes or planning exports (filter in figures block). No ERP connected. This is a new part set for this plant on the evidence available; no confident number is produced off nothing. Prior quotes for this customer: none found in the inputs (not a statement that the relationship is new).

### 8. Date check

Requested delivery 2027-01-31: {{D_TODAY}} calendar days from today, {{D_RECV}} from receipt. **Not checked against shop load** — no planning or schedule export was available. Work content is unknown (section 4), so no lead time can be stated. Material: the three 5052 POs each took {{LEAD}} days order-to-receipt (as of Oct–Nov 2026); thick stock for 02_SLIDER_EXTENSION, the forming outside process and the rail have no lead time on file. The holiday period falls inside the window. Confirm with scheduling before release.

### 9. Assumptions (internal)
- Proceeded on a draft bid decision and a provisional recommendation; outstanding intake questions Q1–Q8 (updated above) are what this price will rest on.
- Commercial terms: none stated by the customer; plant standard terms are not on file, so the customer quote promises them as an attachment.
- Part list taken from `02_bom_handoff.json` (engineering verdict Z), not yet confirmed by the customer.
- Material lower bound per section 3 assumptions.

### 10. Figures block (produced by `compute_quote_figures.py`)

{{FIGURES_TABLE}}

=== END ===
