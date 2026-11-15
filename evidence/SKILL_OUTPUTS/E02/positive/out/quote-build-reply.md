# quote-build — Harbor Robotics Lab, reBot B601 DM part sets (NOREF-20261112) — DRAFT

Run 2026-11-14. Skill followed: `quote-build` (Chain 1 final step). SYNTHETIC test data, fictitious plant. Nothing was sent or written to any system.
Quote reference used here: `Q-HARBOR-ROBOTICS-LAB-NOREF-20261112-01` (the customer gave no RFQ reference).

## Notes to the estimator (outside both documents)

**Headline: this draft has no price.** Every hour is unknown (no routing, no closed-job actuals, no confirmed geometry estimate, no plant machining data), and no labour, burden or margin rate is on file in either route the skill accepts. Material is the only cost line with a sourced number, and only as a partial lower bound. Per the skill, no job total and no unit price is produced by any route.

**Plant setup.** `plant_setup.py find` (run from the work folder) returned `exists: false` and `rates_exists: false` for `work/plant-setup/plant-context.md` and `plant-rates.md`. Artifact tools were not used in this run (run rules), so the setup and rates pages were not looked up; no `CLAUDE.local.md` profile exists in the work folder. Result: no Plant context, no machining data, no demonstrated tolerance capability, no plant quote template, no standard commercial terms.

**Rates.** `MFG_LABOR_RATE`, `MFG_BURDEN_RATE`, `MFG_MARGIN_RULES`, `MFG_SCRAP_COSTING_BASIS`: none set (checked by name). The finance memo you supplied (`inputs/rates_memo.txt`, dated 1 Oct 2026) holds per-work-centre burdened shop rates, a material markup, a target margin figure, an outside-processing markup and a scrap-costing rule. **It is not a rate on file**: a rate handed to this run is not used and is not repeated here. To make it the plant's number, say *"update our labour rate"* (onboarding step 10, records each rate with a name and date on the plant's private rates page), or set `MFG_LABOR_RATE` / `MFG_BURDEN_RATE` / `MFG_MARGIN_RULES` in the environment. The quote completes as soon as they are set **and** hours exist. Note for onboarding: the memo states one burdened rate per work centre, while the profile holds labour and burden separately; onboarding should record which way the plant wants it.

**Gate state.** `bid_decision_state: draft`, `recommendation: bid` with `recommendation_provisional: true`, `gates_passed: []`. The request said "build the draft quote", so this run proceeded **on an unconfirmed recommendation**, recorded on both documents' internal side. Gate 1 (open questions) has not been sent; Gate 3 (design / tolerance reading / operation list) has not been passed, so no geometry-derived hour may be priced.

**Provenance of the BOM handoff.** The intake form (2026-11-14) recorded the STEP and BOM as named but **not received**. `02_bom_handoff.json` now gives a part list read from a STEP named `reBot_B601_DM_v1.1_20260625.step` (sha256 recorded in the handoff) plus the project readme, sourced from a public repository commit. It is not recorded as the file the customer sent. Its `bom_status` is `T`, its `engineering_verdict` is `Z` (not a verified pass) and it lists 7 engineering-missing items, including per-part tolerances, finish, inspection and functional requirements. The file name and revision (v1.1) match the intake line's `revision`, so there is no revision block, but the customer should confirm it is their file (question below).

### Questions recorded instead of asked

To the estimator (internal):
1. Gate 4: who should be recorded as approving release of this quote? (Name not given; not inferred.)
2. Do you want the finance memo's rates recorded through onboarding ("update our labour rate" and the burden / margin equivalents) so this and later quotes can price?
3. Gate 3: the handoff carries bounding boxes, volumes and face counts only. Who will produce the operation list per part (or a geometry estimate) and confirm it, so hours can be derived?
4. Six pieces per set are `CNC + Sheet Metal`. The equipment list has no forming asset. Quote forming through an outside partner (needs a sourced price), or offer those parts as excluded / no-bid?
5. `02_SLIDER_EXTENSION` (smallest dimension 17.8 mm) is thicker than any 5052 stock on our POs. Bar or thick plate needs a supplier quote.
6. The bid decision is still `draft`. Confirm bid / no-bid at Gate 2 before this goes further.

To the customer (add to the Gate 1 email, which has not been sent; questions 1, 2 and 8 of the intake draft still stand as written except where noted):
- Q1/Q2 update: we have a v1.1 STEP (`reBot_B601_DM_v1.1_20260625.step`) and the project readme parts list, giving 21 CNC aluminium part numbers, 31 pieces per arm set. Please confirm this is your file and your set composition, and that 3D-printed parts and fasteners are not part of this request.
- Q3 update: the readme states "Key dimension tolerance: ±0.02 mm GB/T1840-M" (readme line 129). Which dimensions on each part are the key dimensions? Please confirm the standard designation as written, and what applies to every other dimension.
- Q4 update: the readme states 5052; temper is not stated. Is 5052-H32 acceptable?
- Q5 unchanged, plus: the manufacturer tolerance for the MGN9-170 rail is not stated.

=== CUSTOMER QUOTE — SENDABLE ===

**DRAFT QUOTATION — NOT RELEASED — PRICES PENDING**
Reference: Q-HARBOR-ROBOTICS-LAB-NOREF-20261112-01 (draft 1)
To: Lena Okafor, Harbor Robotics Lab
Your request: email of 12 November 2026, "CNC aluminium part sets for reBot B601 DM arm (v1.1 STEP)"
Date: 14 November 2026

| Line | Description | Quantity | Unit price | Extended |
|---|---|---|---|---|
| 1 | CNC-machined aluminium 5052 parts for the reBot B601 DM arm, one complete per-arm set of 21 part numbers / 31 pieces, as machined | 20 sets | To follow | To follow |
| 2 | MGN9 linear rail, 170 mm (budgetary, see assumption 6) | 20 each | To follow | To follow |

**Delivery.** Your requested delivery of 31 January 2027 is noted. It is not yet confirmed; a delivery date will be stated in the released quotation.

**Validity.** To be stated in the released quotation. Aluminium prices move; any price will be valid only for the period stated.

**Terms.** You did not state payment, freight, packaging or liability terms. The released quotation will be on our standard terms for each, which will be attached to it.

**Assumptions**
1. Priced to the design file reBot_B601_DM_v1.1_20260625.step (revision v1.1, 25 June 2026) and the project parts list. No 2D drawings exist.
2. Tolerances as read: "Key dimension tolerance: ±0.02 mm GB/T1840-M" as stated in the project readme (line 129), applying to every CNC part. Which dimensions are key dimensions is not identified, and no tolerance is stated for other dimensions; our ability to hold ±0.02 mm on these parts is subject to confirmation once the key dimensions are identified.
3. Material: aluminium 5052 per the project parts list; temper not stated by you.
4. Finish: as machined. No anodize, per your request. Any other finish (bead blast, edge treatment beyond deburring) is not included.
5. Six of the pieces in each set (03_LINK1, 03_LINK2 ×2, 03_LINK3_L, 03_LINK3_R, 03_LINK5) are formed sheet-metal parts with machined features; their inclusion is subject to confirmation.
6. Line 2: this is a budgetary estimate based on the written specifications you provided, for planning only. It is not an offer; we will send a firm quotation on receipt of a released drawing, or for the rail, the confirmed carriage type, preload, accuracy grade and brand.

**Exclusions**
- 3D-printed parts, fasteners and any purchased part other than line 2.
- Material certificates, inspection reports and certifications (none requested).
- Payment, freight, packaging and liability terms other than our standard terms (none stated by you).
- Pricing for quantities other than 20 sets.

This is a draft for internal review. It is not an offer.

=== END ===

Outbound check on the block above (read alone): no hours, ranges, rungs, paths or basis labels; no rate value; the word "margin" does not appear; no purchase-order number, paid price or supplier name; no customer name other than the addressee's; no pricing-rule description. Passed. It carries no price, so it cannot be released as a quotation until the internal sheet below is complete.


=== INTERNAL COST SHEET — NOT FOR CUSTOMER ===

**Line 2: ROM — rough order of magnitude. Path A: text specs, no drawing. Not a firm quote and not releasable as one.** (Line 1 is path C1: STEP-derived part list, no drawing.)

Quote Q-HARBOR-ROBOTICS-LAB-NOREF-20261112-01, draft 1, 2026-11-14. Inquiry NOREF-20261112, Harbor Robotics Lab. Proceeded on an **unconfirmed recommendation** (`bid_decision_state: draft`, `recommendation_provisional: true`) because the request asked for a draft quote. Plant quote template: **not on file** (no plant profile); neutral structure used. Site: not set.

### 1. Status of every cost line (20 sets)

| Cost line | Status | Basis / source | What unblocks it |
|---|---|---|---|
| Material | **Partial lower bound**: 15 of 21 part ids (23 of 31 pcs/set): USD 19.0026 per set, USD 380.05 for 20 sets. 6 part ids (8 pcs/set) unknown | Price actually paid on PO-30710 (2026-10-20), PO-30711 (2026-10-20), PO-30744 (2026-11-02), 5052-H32, pro-rata by area (section 3) | Sheet gauge and flat patterns for the formed parts; a supplier quote for >10 mm stock; plant scrap allowance; nesting / kerf / workholding allowance |
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
| Tolerance | ±0.02 mm on key dimensions, all 21 part ids (readme line 129, "GB/T1840-M" as written) | **Unknown**: no demonstrated capability on file (no Plant context) | Cannot confirm; stated as scope in customer assumption 2. Key dimensions not identified |
| Forming | 5 part ids / 6 pcs per set are "CNC + Sheet Metal" | Equipment list (5 assets, work centres INSP, MILL-H, MILL-V, TURN): 0 assets mention bend/brake/press/form/sheet | No in-house forming route visible; outside source or exclusion needed |
| Size envelope | Largest bbox dimension 321.0 mm (03_LINK2) | Machine travels are not in equipment.csv | Unknown |
| Multi-axis | Not determinable (no feature list) | 0 assets mention 5-axis | Unknown until an operation list exists |
| Intake `constraint_violations` | [] (check was not run against a profile) | — | carried |

### 3. Material basis (price paid on named POs, dated)

Method (assumptions, all labelled): each pure-CNC part is cut from the thinnest 5052-H32 stock on PO whose thickness is at least the part's smallest bounding-box dimension; blank = the part's two larger bbox dimensions; cost = blank area × (PO unit price ÷ sheet area). **Lower bound**: no saw kerf, no workholding or facing stock (parts at 3.0 mm from 3 mm sheet have none), no nesting loss, no remnant credit, no scrap allowance. 5052-H32 is the temper we bought; the customer's temper is not stated. Prices as of 20 Oct and 2 Nov 2026; aluminium is volatile, so the customer quote carries a validity caveat.

Stock on PO: PO-30710 2026-10-20, AL5052-SH-3, 3 mm × 1220 × 2440, USD 148.60 each = USD 49.92/m². PO-30711 2026-10-20, AL5052-PL-6, 6.35 mm × 610 × 1220, USD 171.25 = USD 230.11/m². PO-30744 2026-11-02, AL5052-PL-10, 10 mm × 610 × 1220, USD 262.80 = USD 353.13/m².

| Part id | Process | Qty/set | BBox sorted (mm) | Stock (PO, date) | Blank (mm) | USD/pc | USD/set | USD 20 sets | Part vol / blank vol | Status |
|---|---|---|---|---|---|---|---|---|---|---|
| 02_BASE_REINFORCEMENT_PART | CNC | 1 | 6.955 x 92.005 x 92.005 | AL5052-PL-10 (PO-30744, 2026-11-02) | 92.005 x 92.005 | 2.9892 | 2.9892 | 59.78 | 0.322 | lower bound |
| 02_ARM_YAW_LIMIT | CNC | 1 | 7.102 x 77.002 x 77.002 | AL5052-PL-10 (PO-30744, 2026-11-02) | 77.002 x 77.002 | 2.0938 | 2.0938 | 41.88 | 0.213 | lower bound |
| 02_MOTOR_FRONT_SPACER | CNC | 4 | 4.0 x 34.8 x 34.8 | AL5052-PL-6 (PO-30711, 2026-10-20) | 34.8 x 34.8 | 0.2787 | 1.1147 | 22.29 | 0.355 | lower bound |
| 02_MOTOR_BACK_SPACER | CNC | 3 | 5.0 x 57.0 x 57.0 | AL5052-PL-6 (PO-30711, 2026-10-20) | 57.0 x 57.0 | 0.7476 | 2.2429 | 44.86 | 0.471 | lower bound |
| 02_FLANGE | CNC | 3 | 9.75 x 34.8 x 34.8 | AL5052-PL-10 (PO-30744, 2026-11-02) | 34.8 x 34.8 | 0.4277 | 1.283 | 25.66 | 0.343 | lower bound |
| 02_WRIST_BRACKET | CNC | 1 | 8.0 x 60.75 x 92.922 | AL5052-PL-10 (PO-30744, 2026-11-02) | 60.75 x 92.922 | 1.9934 | 1.9934 | 39.87 | 0.423 | lower bound |
| 02_GRIPPER_CONNECTOR_A | CNC | 1 | 6.02 x 34.433 x 35.62 | AL5052-PL-6 (PO-30711, 2026-10-20) | 34.433 x 35.62 | 0.2822 | 0.2822 | 5.64 | 0.411 | lower bound |
| 02_GRIPPER_CONNECTOR_B | CNC | 1 | 9.502 x 56.802 x 56.802 | AL5052-PL-10 (PO-30744, 2026-11-02) | 56.802 x 56.802 | 1.1394 | 1.1394 | 22.79 | 0.468 | lower bound |
| 02_SLIDER_BRACKET | CNC | 1 | 3.0 x 68.466 x 176.285 | AL5052-SH-3 (PO-30710, 2026-10-20) | 68.466 x 176.285 | 0.6025 | 0.6025 | 12.05 | 0.226 | lower bound |
| 02_SLIDER_EXTENSION | CNC | 2 | 17.8 x 26.2 x 38.44 | none | - | unknown | unknown | unknown | - | unknown: smallest bbox dimension 17.8 mm exceeds every 5052 stock on PO (max 10.0 mm); no price paid on file |
| 02_LOWER_UPPER_LINK_L | CNC | 1 | 5.0 x 76.177 x 99.0 | AL5052-PL-6 (PO-30711, 2026-10-20) | 76.177 x 99.0 | 1.7354 | 1.7354 | 34.71 | 0.405 | lower bound |
| 02_LOWER_UPPER_LINK_R | CNC | 1 | 5.0 x 76.177 x 99.0 | AL5052-PL-6 (PO-30711, 2026-10-20) | 76.177 x 99.0 | 1.7354 | 1.7354 | 34.71 | 0.405 | lower bound |
| 02_LOWER_WRIST_LINK_L | CNC | 1 | 3.0 x 82.963 x 103.943 | AL5052-SH-3 (PO-30710, 2026-10-20) | 82.963 x 103.943 | 0.4305 | 0.4305 | 8.61 | 0.475 | lower bound |
| 02_LOWER_WRIST_LINK_R | CNC | 1 | 3.0 x 82.963 x 103.943 | AL5052-SH-3 (PO-30710, 2026-10-20) | 82.963 x 103.943 | 0.4305 | 0.4305 | 8.61 | 0.475 | lower bound |
| 02_GEAR_CONNECTOR | CNC | 1 | 9.502 x 35.002 x 35.002 | AL5052-PL-10 (PO-30744, 2026-11-02) | 35.002 x 35.002 | 0.4326 | 0.4326 | 8.65 | 0.196 | lower bound |
| 02_RACK | CNC | 2 | 6.0 x 12.002 x 89.999 | AL5052-PL-6 (PO-30711, 2026-10-20) | 12.002 x 89.999 | 0.2486 | 0.4971 | 9.94 | 0.815 | lower bound |
| 03_LINK1 | CNC + Sheet Metal | 1 | 77.533 x 83.89 x 84.192 | none | - | unknown | unknown | unknown | - | unknown: CNC + Sheet Metal: sheet gauge and flat pattern not in the handoff; bbox is the formed envelope, not the blank |
| 03_LINK2 | CNC + Sheet Metal | 2 | 23.0 x 57.0 x 321.0 | none | - | unknown | unknown | unknown | - | unknown: CNC + Sheet Metal: sheet gauge and flat pattern not in the handoff; bbox is the formed envelope, not the blank |
| 03_LINK3_L | CNC + Sheet Metal | 1 | 28.625 x 57.0 x 297.826 | none | - | unknown | unknown | unknown | - | unknown: CNC + Sheet Metal: sheet gauge and flat pattern not in the handoff; bbox is the formed envelope, not the blank |
| 03_LINK3_R | CNC + Sheet Metal | 1 | 27.625 x 57.0 x 297.826 | none | - | unknown | unknown | unknown | - | unknown: CNC + Sheet Metal: sheet gauge and flat pattern not in the handoff; bbox is the formed envelope, not the blank |
| 03_LINK5 | CNC + Sheet Metal | 1 | 50.0 x 60.0 x 60.0 | none | - | unknown | unknown | unknown | - | unknown: CNC + Sheet Metal: sheet gauge and flat pattern not in the handoff; bbox is the formed envelope, not the blank |

### 4. Hours basis, per operation

Variance threshold: **15% — default threshold, not plant-set.** No variance computed: no operation has two rungs.

Rung 1 (routing): none — no routing for any part in the inputs. Rung 2 (closed-job actuals): none — no work-order or actuals file. Rung 3 (geometry-derived): **refused** — there is no geometry estimate in contract form; the handoff carries bbox, volume and face count only, no feature list, no setups, no operation list, no `approval`, and `engineering_verdict: Z`; Gate 3 not passed; no Fusion and no plant cutting data. Rung 4 (first principles): **not quantified** — no plant setup hours, tool-change time or cutting data exist, and no hour is supplied by the model.

| Op | Work centre / cell | Rung | Path | Cutting data basis | Setup h (low/exp/high) | Run min/pc (low/exp/high) | Other rungs | Variance drivers | Toolpath check |
|---|---|---|---|---|---|---|---|---|---|
| Each of the 21 part ids: machining ops (operation list not established) | Not assigned. Candidates in equipment.csv: MILL-V (VMC-02 Cell A, VMC-03 Cell B), MILL-H (HMC-01 Cell A); deburr/inspection INSP (DEB-01) | 4 (why not higher: no routing, no actuals, no confirmed geometry estimate) | first principles | n/a | unknown / unknown / unknown | unknown / unknown / unknown | none | n/a | not run — no Fusion, feature path not run |
| Forming, 5 part ids | No work centre | 4 | first principles | n/a | unknown | unknown | none | n/a | n/a |

What would firm the hours up: a current routing per part for v1.1, or a geometry estimate per part with its operation list confirmed at Gate 3, plus the Plant context `Machine classes` (setup hours, tool-change min) and `Cutting data` for 5052.

### 5. Quantity break and setup amortization

One break only: 20 sets (620 CNC pieces; 20 rails). No other breaks were requested (intake missing register).
Structure: setup cost per set = Σ over part ids (setup hours × burdened rate of its work centre) ÷ 20; run cost per set = Σ (run h/pc × qty per set × rate). Dollar values blocked (hours and rates). Setup and run are kept separate; no lumped source exists.

### 6. Margin

Margin line: **blocked — margin rules not on file.** No customer-specific or job-type rule could be read.

### 7. Comparables

None. 7 input files enumerated; 0 are routings, actuals, work orders, prior quotes or planning exports (filter in figures block). No ERP connected. This is a new part set for this plant on the evidence available; no confident number is produced off nothing. Prior quotes for this customer: none found in the inputs (not a statement that the relationship is new).

### 8. Date check

Requested delivery 2027-01-31: 78 calendar days from today, 80 from receipt. **Not checked against shop load** — no planning or schedule export was available. Work content is unknown (section 4), so no lead time can be stated. Material: the three 5052 POs each took 7 days order-to-receipt (as of Oct–Nov 2026); thick stock for 02_SLIDER_EXTENSION, the forming outside process and the rail have no lead time on file. The holiday period falls inside the window. Confirm with scheduling before release.

### 9. Assumptions (internal)
- Proceeded on a draft bid decision and a provisional recommendation; outstanding intake questions Q1–Q8 (updated above) are what this price will rest on.
- Commercial terms: none stated by the customer; plant standard terms are not on file, so the customer quote promises them as an attachment.
- Part list taken from `02_bom_handoff.json` (engineering verdict Z), not yet confirmed by the customer.
- Material lower bound per section 3 assumptions.

### 10. Figures block (produced by `compute_quote_figures.py`)

| Figure | Value | Computed from | Filter or arithmetic |
|---|---|---|---|
| Sets quoted | 20 | intake form line 1 quantities | quantities[0].qty (EML:L10); user request 'Quote 20 sets' |
| CNC part ids in BOM handoff | 21 | 02_bom_handoff.json | len(cnc_parts) |
| Part ids, process == 'CNC' | 16 | 02_bom_handoff.json | process == 'CNC' |
| Part ids, process == 'CNC + Sheet Metal' | 5 | 02_bom_handoff.json | process == 'CNC + Sheet Metal' |
| CNC pieces per arm set | 31 | 02_bom_handoff.json | sum(quantity_per_arm) |
| CNC pieces per set, process == 'CNC' | 25 | 02_bom_handoff.json | sum(quantity_per_arm) where process=='CNC' |
| CNC pieces per set, 'CNC + Sheet Metal' | 6 | 02_bom_handoff.json | sum(quantity_per_arm) where process=='CNC + Sheet Metal' |
| CNC pieces for 20 sets | 620 | arithmetic | 31 x 20 |
| Rails for 20 sets | 20 | 02_bom_handoff.json purchased_rail | quantity_per_arm 1 x 20 |
| Distinct tolerance strings in BOM | 1 | 02_bom_handoff.json | len(set(tolerance)) |
| Parts citing readme line 129 for tolerance | 21 | 02_bom_handoff.json | tolerance_source == 'readme.md line 129' |
| Engineering-missing items in handoff | 7 | 02_bom_handoff.json | len(engineering_missing) |
| Largest bbox dimension, any part (mm) | 321.0 | 02_bom_handoff.json | max over parts of max(bbox) |
| 5052 purchase orders on file | 3 | purchase_orders_5052.csv | data rows |
| PO-30710 price per m2 (USD) | 49.92 | purchase_orders_5052.csv | 148.6 / (1220 x 2440 mm) x 1e6 |
| PO-30710 order-to-receipt days | 7 | purchase_orders_5052.csv | 2026-10-27 - 2026-10-20 |
| PO-30711 price per m2 (USD) | 230.11 | purchase_orders_5052.csv | 171.25 / (610 x 1220 mm) x 1e6 |
| PO-30711 order-to-receipt days | 7 | purchase_orders_5052.csv | 2026-10-27 - 2026-10-20 |
| PO-30744 price per m2 (USD) | 353.13 | purchase_orders_5052.csv | 262.8 / (610 x 1220 mm) x 1e6 |
| PO-30744 order-to-receipt days | 7 | purchase_orders_5052.csv | 2026-11-09 - 2026-11-02 |
| Part ids with a material lower bound | 15 | computed table | status == 'lower bound' |
| Part ids with material unknown | 6 | computed table | status == 'unknown' |
| Pieces per set with a material lower bound | 23 | computed table | sum(qty_per_arm) where lower bound |
| Pieces per set with material unknown | 8 | computed table | sum(qty_per_arm) where unknown |
| Material lower bound per set, priced parts only (USD) | 19.0026 | computed table | sum(usd_per_set) over lower-bound parts; excludes unknown parts, scrap allowance, kerf, workholding stock |
| Material lower bound, 20 sets, priced parts only (USD) | 380.05 | computed table | sum(usd_20_sets) over lower-bound parts |
| Part ids priced from PO-30710 | 3 | computed table | po == PO-30710 |
| Part ids priced from PO-30711 | 6 | computed table | po == PO-30711 |
| Part ids priced from PO-30744 | 6 | computed table | po == PO-30744 |
| Assets in equipment list | 5 | equipment.csv | data rows |
| Work centres in equipment list | INSP, MILL-H, MILL-V, TURN | equipment.csv | distinct work_center |
| Assets whose description mentions bend/brake/press/form/sheet | 0 | equipment.csv | description contains bend|brake|press|form|sheet |
| Assets whose description mentions 5-axis | 0 | equipment.csv | description contains '5-axis' |
| Input files that are routings, actuals, work orders, prior quotes or planning exports | 0 | file enumeration of inputs/ | name contains work_order|routing|actual|quote|sales_order|planning|schedule|load |
| Input files enumerated | 7 | file enumeration of inputs/ | os.walk |
| Calendar days, today (2026-11-14) to requested 2027-01-31 | 78 | arithmetic | 2027-01-31 - 2026-11-14 |
| Calendar days, receipt (2026-11-12) to requested 2027-01-31 | 80 | arithmetic | 2027-01-31 - 2026-11-12 |
| Variance threshold | 15% - default threshold, not plant-set | no Plant context | hours-ladder.md default |
| Operations with a variance computed | 0 | hours table | fewer than two rungs exist for every operation |
| MFG_* rate variables set | 0 | environment | names checked: MFG_LABOR_RATE, MFG_BURDEN_RATE, MFG_MARGIN_RULES, MFG_SCRAP_COSTING_BASIS (values never read out) |

=== END ===


## Files written by this run
- `out/quote-build-reply.md` — this reply, both delimited documents in full
- `out/figures.json`, `out/material-basis.csv` — figures block and material table, produced by `out/scripts/compute_quote_figures.py`
- `out/operation-record.json` — the operation record kept with the quote
- `out/sales-command-center.html` — the Sales command-center page, offered

No Word or Excel copy this run: no Word or Excel writer available (python-docx and openpyxl are not installed, and installing is outside the run rules).
