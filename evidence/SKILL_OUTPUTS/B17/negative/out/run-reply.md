# Chain 5 run: supplier escape to alternate source. BSH-1210, lot AS-7781

SYNTHETIC test data, fictitious plant. This file is a copy of the run's full reply. The skill says a document's saved copy goes to Word (.docx). That was not possible this session because python-docx is not installed and the run rules forbid installing it. **No Word copy this session: no Word writer available.**

**Where the chain stopped: Gate 1, after step 2.** The NCR is a draft that a quality owner has not approved. The supplier-caused flag is also a draft with no named owner. Because of that, the 8D (step 3) is blocked and the alternate-source RFQ package (step 4) was not assembled. Nothing went to any supplier, any customer or any system.

Safety status: not assessed. The inputs record no safety use for the part.

## Sources and freshness

| Source | Date | Covers | Status |
|---|---|---|---|
| `inputs/escape/incoming_finding.txt` | 2026-11-12 receiving inspection | Lot AS-7781, plus pass/fail notes on AS-7702 and AS-7744 | Read. No time of day, timezone, inspector name or gage recorded |
| `inputs/escape/BSH-1210_drawing_revA.md` | Rev A, 2025-06-02 | Requirement | Read |
| Plant profile (`## Plant context`) | none | n/a | **Not found.** `plant_setup.py find` returned `exists: false`, there are no artifact tools in this run, and no CLAUDE.local.md exists. The site, NCR/8D template, approved supplier table, clause set, terms and time zones are all missing |
| ERP (NetSuite / Infor M3) | none | n/a | Not available. There are no shipments, no item-master revision, no usage or vendor records |
| Consolidated dataset / `inventory` tab | none | n/a | Not available. On-hand figures come from the inspector's statement and are unverified |
| Quality document library | none | n/a | Not available. Status is `no_searchable_history` |
| Historian / maintenance | none | n/a | Not available. This finding is on a purchased part at receiving, so neither applies |

---

## 1. NCR (draft). Neutral structure: the plant's controlled NCR template was not available

| Field | Value |
|---|---|
| NCR ref | DRAFT-NCR-BSH-1210-AS-7781. This is provisional because the plant's NCR number is not available |
| Site | **not stated** (asked below) |
| Part / revision | BSH-1210 Flanged bushing, rev A |
| Supplier / PO / receipt / lot | Alder Sintered Parts / PO-30655 / RCV-9921 / AS-7781 |
| Lot quantity received | 1,000 each |
| Found at | Receiving inspection, 2026-11-12. Time and timezone were not recorded |
| Found by | Receiving inspection. The inspector's name was not recorded |
| Gage | **Not recorded.** Calibration status cannot be checked, and that is a finding of its own |
| Disposition | Pending |
| Approval | **draft**. Approved by: not given. Approved at: none |

**Condition found.** Hardness was measured at 47, 49, 46, 50 and 48 HRF on 5 samples. All 5 are above the upper limit of 40 HRF. The supplier's C of C for lot AS-7781 states 32 HRF. Oil content was not tested.

**Requirement cited.** Drawing BSH-1210 rev A (2025-06-02), drawing notes line 4: *hardness 25-40 HRF*. The part was received against rev A. The drawing also requires oil impregnation of at least 18 percent by volume and a certificate of conformance per lot. Oil content was not tested, so it is an open check and not a nonconformance.

**Affected quantity.** 1,000 each (`scope_basis: lot`; this is not a minimum). The suspected mechanism is lot-level: either the material of AS-7781 or the way it was measured. A lot-level cause reaches every piece, so the whole lot is suspect until it is dispositioned. The 5 found were an incoming sample, not a full inspection. Lots AS-7702 and AS-7744 are excluded only because they passed incoming hardness checks. That exclusion falls if the tester proves out of calibration. `traceability_complete: false` because the inputs do not record which WO-8150 assemblies used the 400 issued pieces.

## 2. Containment plan. Ordered by urgency, owners blank

| Location | Suspect qty | Action | Urgency | Owner |
|---|---|---|---|---|
| Installed at customer | **not checked** | Confirm whether any WO-8150 assembly built with AS-7781 bushings has shipped and been installed | immediate | |
| At customer | **not checked** | Check shipment records for WO-8150 assemblies shipped since 2026-11-12 | immediate | |
| In transit | **not checked** | Check open shipments of WO-8150 assemblies and intercept any that carry AS-7781 | immediate | |
| WIP (assembly line 2, WO-8150) | 400 (per the receiving finding; not verified against inventory) | Stop issuing AS-7781 to line 2. Hold the loose bushings and every assembly built with them. Tag with the NCR reference. Count how many were consumed | immediate | |
| Stock (receiving quarantine Q-1) | 600 (per the receiving finding; not verified against inventory) | Keep on hold in Q-1, tagged, and do not release. Finished WO-8150 assemblies in stock: **not checked** | routine | |

The 400 and the 600 add up to the lot quantity of 1,000 (computed; see the figures block). Q-1 was mapped to the "finished goods" (on-hand stock) location type because the plant vocabulary is not on file.

## 3. Recurrence

**No searchable history available.** There is no quality document library this run, so 0 prior NCRs were found because no search ran. This is not a first occurrence. Related receipts that are not NCRs: AS-7702 (2026-09) and AS-7744 (2026-10) from the same supplier passed incoming hardness checks. Whether any earlier fix held cannot be judged.

## 4. Escape notification

**Not drafted.** Containment did not place any parts at or past a customer, so `escape_occurred` is false and `escape_detected_at` is null. The three customer locations are **not checked**. The inputs name no customer, order or shipment, so `escape_possible` was set to false. That leaves an open action: *"Confirm with shipping / the ERP whether any WO-8150 assembly containing AS-7781 bushings has shipped since 2026-11-12."* If any has shipped, the notification must be drafted right away against the customer's contractual window. That window is not on file and was not guessed.

---

## 5. Root cause. Ranked candidates (draft investigation; 8D blocked)

**Time alignment.** There is only one dated source, with dates and no times. No cross-source correlation was attempted, and none of the checks below depends on clocks.

**Candidate 1: supplier lot AS-7781 produced above the hardness requirement (leading, confidence low)**
Chain: `supplier process or material deviation on AS-7781` → `lot hardness above 40 HRF` → `C of C reported 32 HRF and did not catch it` → `nonconforming lot received`

- Link 1, supplier deviation. **For:** nothing direct. The only indirect support is that the failure is confined to this lot (AS-7702 and AS-7744 passed, incoming_finding.txt line 5). **Against:** the supplier's process data for AS-7781 is not available. **This is the weak point of the chain: there is no direct evidence for the mechanism.**
- Link 2, hardness above 40 HRF. **For:** 5 of 5 samples measured 46-50 HRF, mean 48 (incoming_finding.txt line 3; figures block). **Against:** the gage and its calibration are not recorded (line 3).
- Link 3, C of C misreported. **For:** the C of C states 32 HRF, 16 HRF below the measured mean (line 4). **Against:** if our measurement is wrong, the C of C is correct.
- **Confirm:** re-test retained AS-7781 parts on a verified HRF tester and get readings above 40, and/or the supplier's raw hardness data for AS-7781 shows readings above 40.
- **Kill:** re-test on a tester verified against a certified HRF reference block gives 25-40 HRF.

**Candidate 2: our receiving hardness measurement reads high (ranked second)**
Chain: `tester, scale or method error at receiving` → `false-high readings of 46-50 HRF` → `false reject of a conforming lot`

- Link 1. **For:** the gage, its calibration and the method are not recorded (line 3). **Against:** prior lots passed the same incoming hardness check (line 5). The finding does not say whether the method or tester was the same.
- Link 2. **For:** the C of C states 32 HRF (line 4). **Against:** the readings are internally consistent (mean moving range 2.75 HRF; figures block).
- **Confirm:** the tester fails verification on a reference block, or a retained AS-7744 part also reads above 40.
- **Kill:** the tester verifies on a reference block and AS-7781 still reads above 40.

**Candidate 3: the parts in AS-7781 are not the parts the C of C test describes, i.e. a mixed or mis-certified lot (ranked third, supplier-side)**

- Link 1, parts differ from the certified sample. **For:** the C of C and the measurements disagree (line 4). **Against:** none recorded, and the readings are tightly grouped. **Weak point: there is no direct evidence.**
- **Confirm:** the supplier's traceability shows the C of C test was not made on AS-7781 parts, or a material or dimensional check shows a different part or grade.
- **Kill:** the supplier's traceability ties the certified test to these parts.

**Cheapest discriminating test:** verify the receiving hardness tester on a certified HRF reference block, then re-test 5 retained AS-7781 parts and, if one was retained, an AS-7744 part. This separates Candidate 2 from Candidates 1 and 3.

The candidates are not tied. Candidate 1 leads because the same incoming check passed the two prior lots. Confidence is low until the tester is verified.

## 6. Checks

| Check | State |
|---|---|
| Spec comparison | Ran: 5 of 5 above USL 40 HRF, 0 below LSL 25 |
| SPC drift (individuals chart) | Ran on 5 points from one lot. No point beyond the limits and no run rule fired. There are too few points for meaningful control limits, and no prior-lot values exist |
| Lot clustering | Ran on pass/fail by lot: 1 failing lot of 3. Small numbers |
| Shift / operator / machine / tool-change clustering | **Could not run.** This is a purchased part at receiving with no process records |
| Maintenance correlation | **Could not run.** There is no maintenance data and no clock alignment |
| Recurrence | `no_searchable_history` (no library) |

## 7. Figures block. Computed by `out/figures/compute_figures.py` over the two input files (output: `out/figures/figures.json`)

| Figure | Value | Computed from | Filter or query |
|---|---|---|---|
| Samples measured | 5 | incoming_finding.txt | regex on "Hardness measured ... on N samples" |
| Values (HRF) | 47, 49, 46, 50, 48 | same | same |
| Min / max / mean | 46 / 50 / 48 HRF | same | |
| Spec LSL / USL | 25 / 40 HRF | drawing rev A | regex on "Hardness N-N HRF" |
| Samples above USL / below LSL | 5 / 0 | values vs spec | |
| Min − USL / mean − USL | 6 / 8 HRF | same computation | |
| Mean ÷ USL | 1.2 | same computation | |
| C of C stated / mean − C of C | 32 / 16 HRF | incoming_finding.txt | |
| I-chart centreline | 48 HRF | values | individuals, n=5, lot AS-7781 only |
| Moving ranges / MR-bar | 2, 3, 4, 2 / 2.75 | values | |
| Sigma estimate (MR-bar ÷ 1.128) | 2.438 | same | |
| UCL / LCL (control limits, not spec limits) | 55.31 / 40.69 HRF | same | |
| Points beyond UCL / LCL | 0 / 0 | same | |
| Run rule (consecutive points on one side of centreline) | longest run 1; did not fire | same | |
| Lot received / issued WO-8150 / quarantine Q-1 | 1,000 / 400 / 600 | incoming_finding.txt | |
| Issued + quarantine | 1,000; reconciles to lot: yes | same computation | |
| Prior lots named | 2 (AS-7702, AS-7744) | incoming_finding.txt | regex "AS-NNNN (YYYY-MM)" |
| Prior NCRs | 0 because **no search ran** | none | no quality library available |

## 8. 8D. **Blocked**

The source NCR's `approval_state` is **draft**. Under the rules, that blocks the 8D, the customer pack and the redaction diff. The ranked candidates and evidence above stand as the draft investigation. **No corrective action has been recorded (chain step 3)**: D5 and D7 are not drafted until a quality owner approves the NCR. No customer pack was requested. No removal requests were made, so there is no pending redaction log.

## 9. Supplier-caused flag. **Raised as a DRAFT and awaiting a Gate 1 owner**

Saved to `out/records/supplier-caused-flag.yaml`.

| Field | Value |
|---|---|
| determination / confidence | supplier_caused / **low** |
| is_leading_candidate | true. Competing: Candidate 2 (measurement) and Candidate 3 (mis-certified lot) |
| supplier_name / supplier_id | Alder Sintered Parts / **not in the inputs** (required) |
| part_revision | A. **Not verified against an ERP item master** |
| evidence_against | 3 entries, present |
| escape_occurred / escape_detected_at | false / null |
| determination_made_at | 2026-11-14T22:04-05:00, from the session clock (the plant timezone is not configured). **determination_made_at is the middle of the three timestamps; it cannot be reconstructed afterwards.** |
| approval_state / approved_by | **draft** / not given |

The three Chain 5 timestamps:

| Stamp | Value |
|---|---|
| `escape_detected_at` | null, because no escape |
| `determination_made_at` | 2026-11-14T22:04-05:00. *The middle of the three; this cannot be reconstructed afterwards.* |
| `rfq_issued_at` | none. No package was issued |

## 10. Alternate-source RFQ (step 4). **Blocked. No package assembled**

`supplier-quote-request` checked the gate before acting, and the package was blocked for these reasons:

1. **The flag is unapproved (Gate 1).** A supplier-caused determination against Alder Sintered Parts is a commercial claim, and it needs a named human owner before any sourcing action starts. The flag is reported as a finding that needs an owner.
2. **The revision check cannot clear.** There is no ERP item master, so rev A, read from the drawing title, cannot be compared against it. That makes it unverified, and the package is treated as blocked.
3. **The flag is missing `supplier_id` and `site`**, both of which are required.

Once Gate 1 is approved, the confidence is still low. The search would then run as an **exploratory alternate-source search** and be labelled that way, not as a response to an established supplier failure.

**Single-source risk: not determinable.** There is no approved-supplier table and there are no ERP vendor records. The only supplier visible in the inputs for BSH-1210 is the implicated one, Alder Sintered Parts. If it is the only qualified source, that is the most urgent finding of this run. Requalifying an alternate (samples, first article, PPAP level to be set) takes weeks to months, which is why it is worth starting as soon as Gate 1 clears.

**Missing items for the package (internal; each one names the search that came back empty):**

| Missing | Why it matters | Where it should come from |
|---|---|---|
| ERP item-master revision for BSH-1210 | Hard stop: the revision cannot be verified | NetSuite / Infor M3 item master. No ERP this run |
| Demand picture (historical usage, open demand, forecast) | Suppliers price against volume | ERP usage and open orders. Not in the inputs; the lot quantity of 1,000 is one receipt, not a usage figure |
| Buyer's first-article date and production schedule | Delivery requirement | Planning export, or ask the buyer |
| Standard quality clause set | Clauses are part of the price | `## Plant context`. Not found. Clauses on the part record: material SAE 841, oil ≥18% by volume, hardness 25-40 HRF, C of C per lot. **Unverified set** |
| Commercial terms (payment, freight/Incoterms, packaging, liability, tooling ownership) | Comparable bids | Plant standard terms. Not found |
| Response due date, bid recipient, technical contact | Response schedule | Buyer |
| Approved suppliers for sintered bronze bushings | Candidate list | `### Approved suppliers` in Plant context. Not found |
| Plant RFQ template | Controlled document | Onboarding. Not found |
| Restricted-data status | Gate before assembly | The drawing text was searched and contains no ITAR/EAR/export marking. The customer program is unknown |

## 11. Quality register row and pages

The row was saved to `out/records/quality-register-row.yaml` with **status awaiting_approval** and key `<site>_DRAFT-NCR-BSH-1210-AS-7781`. It is **not stored in a register**.

**The Quality Register was not updated: the artifact tools are not available in this run.** The Quality page, showing this NCR only, is saved at `out/pages/quality-page.html`. Save it over the previous Quality page.

The Supply Chain page is offered at `out/pages/supply-chain-page.html`. It is internal, and the plant should save it where the last Supply Chain page lives.

## 12. Questions (recorded, not asked)

1. Gate 1: who owns the supplier-caused determination against Alder Sintered Parts? Who should I record as approving it, and when?
2. NCR approval: which quality owner approves this NCR, and under what name?
3. What site is this, and what NCR number does the plant assign?
4. Which hardness tester and scale were used, and when was it last calibrated?
5. Have any WO-8150 assemblies containing AS-7781 bushings shipped? To which customer, and what is their notification window?
6. What is Alder Sintered Parts' vendor ID? What revision does the ERP item master hold for BSH-1210?
7. Is Alder Sintered Parts the only approved source for BSH-1210?
8. What are the plant timezone and the time of the 2026-11-12 finding?
