# Chain 5 - Supplier escape to alternate source: BSH-1210 lot AS-7781 hardness (SYNTHETIC test data)

This is the full chain reply that the skills require to be printed in full. All inputs are synthetic test data for a fictitious plant. Nothing was sent to any supplier, customer or system.

Skills followed: `supplier-escape-to-alternate-source` (Chain 5), chaining `ncr-writeup` -> `root-cause-capa` -> `supplier-quote-request`.

## Where the chain stopped

- **NCR gate (ncr-writeup): open.** The NCR is a draft (`approval_state: draft`). A quality owner must confirm the finding, requirement, scope and containment. Because of this, **the 8D is blocked** (root-cause-capa Step 5). The ranked candidates and the evidence appendix are produced below as a draft.
- **Gate 1, after step 2: open.** The supplier-caused flag was raised (`determination_made_at` stamped) with `approval_state: draft`. A supplier-caused determination needs a named human owner before it acts.
- **Step 4, the alternate-source RFQ package: not assembled.** `supplier-quote-request` checks the gate and blocks on an unapproved flag. It is also blocked by its first hard stop: there is no ERP item master, so the drawing revision (rev A) cannot be verified. Gate 2 (release) was never reached. Nothing was drafted for, or sent to, any supplier.
- **No Word or Excel copies this session:** no Word or Excel writer is available (python-docx and openpyxl are not installed, and installing is not allowed). This reply holds every document.
- **Plant setup:** `plant_setup.py find` found no profile (`exists: false`). Artifact tools are not allowed in this run, so no setup or Open work page was read. Neutral NCR, 8D and RFQ structures are used: **the plant's controlled templates were not on file.**

---

## Step 1 - NCR (ncr-writeup)

### Summary
Receiving inspection found purchased bushing lot AS-7781 harder than the drawing allows: all 5 samples read 46-50 HRF against 25-40 HRF. The whole lot of 1,000 is suspect. 600 are held in quarantine Q-1. 400 were already issued to assembly line 2 (WO-8150) and need to be held now. No customer exposure was established, but it was **not checked** either.

### NONCONFORMANCE REPORT - DRAFT (neutral structure; plant controlled template not on file)

| Field | Value |
|---|---|
| NCR number | **not assigned** (no number in the inputs; question Q2) |
| Site | **not given** (question Q2) |
| Part / revision | BSH-1210 Flanged bushing, rev A |
| Supplier / PO / receipt / lot | Alder Sintered Parts (fictitious) / PO-30655 / RCV-9921 / AS-7781 |
| Lot quantity | 1,000 each |
| Found at | Receiving inspection |
| Found by | Receiving inspection (inspector name not recorded) |
| Found on | 2026-11-12. **Time and timezone are not recorded** in the finding |
| Disposition | **Pending** |
| Approval | **Draft: awaiting quality owner approval** |

**1. Condition found (as measured)**
- Hardness on 5 samples: 47, 49, 46, 50, 48 HRF. All 5 are above the upper limit. Mean 48 HRF; min 46, max 50.
- Gage: **not recorded**, and neither is its calibration date. Under ncr-writeup Step 1 that is a finding of its own (question Q4).
- The supplier C of C for lot AS-7781 states 32 HRF, which is inside spec. It disagrees with the measurement by 16 HRF (mean minus C of C value).
- Oil content (drawing: 18 percent min by volume) was **not tested**, so its conformance is unknown.

**2. Requirement violated**
- Document: drawing BSH-1210, revision A, dated 2025-06-02 (`BSH-1210_drawing_revA.md`).
- Locator: drawing notes, final line, "Hardness 25-40 HRF".
- Characteristic: hardness. Stated value: 25-40 HRF.
- Revision built to: rev A, per the finding. **The ERP item-master revision was not available to cross-check.**

**3. Affected quantity: 1,000 each (scope basis: lot)**
The suspected mechanism is the material of purchased lot AS-7781. The competing explanation is the receiving hardness test (see Step 2). Either way the cause applies to every piece received on RCV-9921, so all 1,000 pieces are suspect until they are sorted or dispositioned. The 5 parts found were an incoming sample, not a 100% inspection. Prior lots AS-7702 and AS-7744 passed incoming hardness and are not in scope on the evidence available. Traceability on the receipt is complete. **Whether lot identity carries onto WO-8150 assemblies is not verified.**

**4. Containment plan (customer side first; owners left blank for assignment)**

| Location | Suspect qty | Action | Urgency | Owner | Source |
|---|---|---|---|---|---|
| Installed at customer | **not checked** | Confirm whether any WO-8150 assemblies containing lot AS-7781 have shipped and been installed. No customer is identified in the inputs | immediate | | No shipment records or ERP in inputs |
| At customer | **not checked** | Check shipment records for WO-8150 output since the 2026-11-12 issue. If any shipped, identify the customer and request quarantine | immediate | | Same |
| In transit | **not checked** | Check open shipments of WO-8150 output and intercept any carrying lot AS-7781 | immediate | | Same |
| WIP (assembly line 2, WO-8150) | 400 (per issue record; not physically counted) | Stop consuming AS-7781. Hold loose parts and any assemblies built with them. Count loose vs assembled and tag with the NCR reference | immediate | | incoming_finding.txt: "400 pcs already issued to assembly line 2 (WO-8150)" |
| Finished goods / stores (receiving quarantine Q-1 mapped here) | 600 (held) | Keep in Q-1 and tag with the NCR reference. Separately check stores for any WO-8150 assemblies built with AS-7781: **not checked** | same_day | | incoming_finding.txt: "600 pcs in receiving quarantine Q-1" |

The 400 issued plus the 600 quarantined reconcile to the 1,000 received. 40.0% of the lot is already on the line.

**5. Recurrence finding**
**No searchable history available.** No quality document library was supplied, so prior NCRs and CAPAs were not searched (`no_searchable_history`, `prior_ncrs_found: 0`, `history_searched: false`). This is **not** a first occurrence. Related receipts (not NCRs): AS-7702 (2026-09) and AS-7744 (2026-10) from the same supplier both passed incoming hardness checks. Whether any earlier fix held cannot be judged.

**6. Escape**
No escape notification was drafted. Containment placed no parts at or past a customer (`escape_occurred: false`). The inputs hold no order, shipment status or customer for WO-8150 output, so `escape_possible` is also false. **The three customer-side locations are unchecked, not clear.** If the shipment check finds WO-8150 assemblies shipped, an escape notification must be drafted right away against the customer's contractual window. That window is unknown (question Q5). `escape_detected_at` stays null.

Structured NCR saved as `out/records/ncr.yaml` (contract ncr.md v4):

| Field | Value |
|---|---|
| ncr_ref | NCR-UNASSIGNED |
| approval_state | draft |
| requirement_not_locatable | false |
| qty_suspect / is_minimum | 1000 / false |
| recurrence | no_searchable_history |
| escape_occurred / escape_possible | false / false |
| escape_detected_at | null |

---

## Step 2 - Root cause against the supplier (root-cause-capa)

### Ranked candidate causal chains (DRAFT; 8D blocked)

**C1 (leading, medium confidence): supplier material or process on lot AS-7781**
Lot AS-7781 material/process deviation at the supplier -> parts above 40 HRF as shipped -> C of C value does not represent the lot shipped.
- Link 1, *a material/process deviation at the supplier on this lot*
  - For: **nothing.** No density, oil-content or supplier process data. **This is the weak point of the chain.**
  - Against: no supplier data either way. Oil content not tested (incoming_finding.txt).
- Link 2, *parts above 40 HRF as received*
  - For: 5 of 5 samples 46-50 HRF vs 25-40 HRF (incoming_finding.txt line 3; drawing notes). Tested at receiving, before any plant processing (RCV-9921).
  - Against: gage, calibration, scale/load and test location not recorded (incoming_finding.txt).
- Link 3, *the C of C does not represent the lot*
  - For: C of C states 32 HRF while the measured mean is 48 (incoming_finding.txt line 4).
  - Against: the same 16 HRF gap is explained equally well by C2.
- Lot clustering: 1 of 3 recorded lots from this supplier failed. AS-7702 and AS-7744 passed the same incoming check. **These are small numbers (3 lots):** the clustering is suggestive, not a pattern.
- **Confirm:** a verified hardness tester (checked on a certified HRF reference block) reproduces 41+ HRF on AS-7781 parts from Q-1, and an independent lab or supplier retest agrees.
- **Kill:** the verified tester reads AS-7781 parts inside 25-40 HRF.

**C2 (second): receiving hardness measurement error**
Tester out of calibration, wrong scale/load, or an unsuitable test location -> readings high -> false reject.
- Link 1, *a tester or method error*
  - For: gage ID and calibration not recorded. The supplier C of C (32 HRF) contradicts our readings.
  - Against: the same incoming hardness check passed AS-7702 and AS-7744. This is weak, because the method and dates of those checks are not recorded.
- Link 2, *readings biased high*
  - For: nothing beyond Link 1. **This is the weak point.**
  - Against: the readings are tightly grouped (std dev 1.581). That is consistent with either a bias or a real shift, so it separates nothing.
- **Confirm:** the tester reads high on a certified reference block, or a retained AS-7744 part now reads above 40 HRF.
- **Kill:** the tester verifies on the reference block and AS-7781 still reads above 40 HRF.

**C3 (third): lot identity mix-up**
The parts received as AS-7781 are not the material the C of C covers.
- Link 1, *a mixed or mislabelled lot*
  - For: only the disagreement between the C of C and the measurement.
  - Against: no evidence of mixed labels. All 5 readings are consistent. **This is the weak point.**
- **Confirm:** packaging or labels show mixed lot marks.
- **Kill:** lot marking is consistent across all containers.

**Cheapest discriminating test:** verify the receiving hardness tester on a certified HRF reference block. Then re-test 5 parts from Q-1, and a retained AS-7744 part if one exists, on the same tester at the same location and scale. This separates C1 from C2 and needs nothing from the supplier.

### 8D - BLOCKED
The 8D is not produced. **Blocking condition: the source NCR's `approval_state` is `draft`, not `approved`** (root-cause-capa Step 5; ncr.md missing behaviour). It will be drafted once the NCR is approved: D1-D5 and D7 populated, with D6 and D8 left as empty placeholders. D7 will need to address incoming verification of supplier C of C claims. **Corrective action is therefore not yet recorded.** No customer pack was requested, and there were no removal requests, so there is no pending redaction log entry.

### Evidence appendix
- **Timeline / time alignment:** there is a single source (the receiving finding), dated 2026-11-12 with no time or zone. No cross-source correlation was attempted. Plant clocks and the shift boundary are unknown because there is no Plant context. The timestamps in this run come from the run host clock (UTC-05:00); the plant timezone is not confirmed.
- **SPC (computed):** individuals/MR chart on lot AS-7781's 5 readings. Centreline 48, UCL 55.31, LCL 40.69 (MRbar 2.75). Run rule WE-1: 0 points beyond the limits. The 8-on-one-side rule cannot be evaluated with 5 points. **Control limits are not specification limits:** this lot is in statistical control around 48, and its LCL sits 0.69 HRF above the 40 HRF spec limit. In plain terms, the whole lot's distribution is out of spec. Drift across lots cannot be computed because prior-lot measurements were not supplied.
- **Clustering:** by lot, 1 of 3 lots failed (small numbers). Clustering by shift, operator, machine and tool change **could not run**: there is no data, and these do not apply to a purchased part at receiving.
- **Maintenance correlation:** **could not run** (no maintenance data, no verified clocks).
- **Recurrence:** no_searchable_history, carried forward from the NCR.
- **Historian:** not available.
- **Sources:** inputs/escape/incoming_finding.txt, BSH-1210_drawing_revA.md, approved_suppliers.csv.

### Figures block (computed by `out/scripts/figures.py`; full table in `out/figures-block.md`)
Key rows:

| Figure | Value |
|---|---|
| Readings above USL | 5 of 5 |
| Mean / min / max | 48 / 46 / 50 HRF |
| Std dev | 1.581 |
| Mean minus USL | 8 HRF |
| Mean / USL | 1.2 |
| Mean minus C of C | 16 HRF |
| SPC CL / UCL / LCL | 48 / 55.31 / 40.69 |
| SPC run rule | WE-1: 0 points beyond; 8-on-one-side not evaluable (n=5) |
| LCL minus USL | 0.69 HRF |
| Lots failing | 1 of 3 |
| Issued + quarantined | 400 + 600 = 1000 (reconciles) |
| Approved for bronze commodity | 2 |
| Rows naming BSH-1210 as current source | 1 |

### Supplier-caused flag (Gate 1)
Saved as `out/records/supplier-caused-flag.yaml` (contract v2):

| Field | Value |
|---|---|
| determination / confidence | supplier_caused / medium |
| is_leading_candidate | true |
| competing_candidates | C2 receiving tester error; C3 lot mix-up |
| supplier | Alder Sintered Parts (fictitious), PO-30655, lot AS-7781 |
| part_revision | A |
| evidence_against | present (3 items) |
| recurrence | no_searchable_history |
| escape_occurred | false |
| approval_state | **draft. Needs a named human owner** |

### Three timestamps

| Stamp | Value |
|---|---|
| escape_detected_at | null: no parts were placed at or past a customer (customer locations not checked) |
| determination_made_at | **2026-11-14T17:02-05:00** (run host clock). *determination_made_at is the middle of the three; this cannot be reconstructed afterwards.* |
| rfq_issued_at | not recorded: no RFQ issued (blocked at Gate 1) |

### Quality Register row
Row key `not given_NCR-UNASSIGNED`. Status awaiting_approval. 8D step: null (blocked). Leading cause recorded as a candidate. `supplier_caused: true`. Saved as `out/records/quality-register-row.yaml`, **not stored in a register.** The Quality page is offered as `out/pages/quality-page.html` and shows this NCR only. **The Quality Register was not updated: artifact tools are not permitted in this run.**

---

## Step 3 - Corrective action
**Not recorded.** The 8D is blocked on NCR approval (see Step 2).

## Step 4 - Alternate-source RFQ (supplier-quote-request): BLOCKED, no package assembled

**Why it is blocked:**
1. The supplier-caused flag is `draft`. This is an unapproved finding and needs an owner (question Q3). It is not acted on.
2. Hard stop, revision: with no ERP item master, the revision comparison cannot clear. The library drawing is rev A (dated 2025-06-02, read from the file header, not the filename). The item-master revision is **unknown**. The package stays blocked until document control confirms the revision.
3. Restricted data: no ITAR, EAR or export marking was found in the drawing text. The program is unknown, so this check is not cleared either.

**SINGLE-SOURCE RISK (internal; stated first)**
By the approved table, two suppliers are approved for sintered bronze, so the commodity is not single-source by the table's rule. However, only one row records BSH-1210 as a current source: **Alder, the implicated supplier.** Birch Powder Metal (fictitious) is approved for the commodity and quoted BSH-1210 in 2026-10 with **revision not stated**, but nothing records it as qualified on this part. **In practice, the only part-qualified source may be the implicated supplier.** That is the most serious form of single-source risk, and the buyer should confirm it (question Q9).

**Candidate suppliers (internal)**

| Supplier | Approval status | Basis | Requalification |
|---|---|---|---|
| Alder Sintered Parts (fictitious) | approved; **incumbent, implicated** | approved_suppliers.csv row "sintered bronze"; current source BSH-1210; last audit 2025-11-03 (376 days) | n/a. Whether to invite back is the buyer's call |
| Birch Powder Metal (fictitious) | approved (commodity) | Row "sintered bronze and iron", matched on "sintered bronze"; last audit 2026-02-20 (267 days); prior 2026-10 quote, rev not stated | Part qualification not recorded: samples, first article, PPAP level TBD. Weeks to months |
| Cedar Bearings Inc (fictitious) | **conditional, not confirmed approved** | Row "bronze bushings"; audit overdue (last 2024-06-15, 882 days) | Audit plus first article before production. Buyer decision needed |

**Missing items for the package (internal), with where each should come from**

| Missing | Why it matters | Should come from |
|---|---|---|
| ERP item-master revision for BSH-1210 | Hard stop: the revision cannot be verified | ERP item master. Not available (no ERP in session) |
| Historical usage, open demand, forecast | Without them, suppliers price defensively | ERP usage/PO history and planning. Not found in inputs |
| First article date and production schedule | The buyer's delivery requirement | Planning data. Not found; ask (Q7) |
| Standard quality clause set (cert level, PPAP level, C of C, traceability, change notification, retention) | Part of the price | Plant context from onboarding. Not on file. The only clause found on the part record is the drawing's "Certificate of conformance per lot". **The set is unverified** |
| Commercial terms (payment, Incoterms/freight, packaging, tooling ownership) | Makes bids comparable | Plant standard. Not on file |
| Response due date, bid recipient, technical contact | Response schedule | Buyer. Not given |
| Vendor IDs and contact addresses | Emails would be HELD without them | ERP vendor records. Not available |
| Plant RFQ template | Controlled document | Onboarding. Not on file |
| Current price and terms (internal comparison only) | The buyer's own baseline; never goes in the package | PO history (PO-30655 price not in inputs) |

**When the gates clear, the package must carry the mandated bid format** (per bid-comparability.md): unit price per quantity break, tooling and NRE priced separately, tooling ownership, lead time split into first article and production from a named event, MOQ, currency, validity, and listed exclusions. A non-conforming bid gets sent back for restatement.

The Supply Chain page is offered as `out/pages/supply-chain-page.html`. It is an offered page, not a write.

---

## Questions recorded (not asked, per run rules)
- Q1. Who is the quality owner approving the NCR? (Name to record.)
- Q2. What NCR number and site name should be used?
- Q3. Gate 1: who owns the supplier-caused determination against Alder Sintered Parts? (Name to record.)
- Q4. Which hardness tester took the 5 readings? What are its calibration status, scale/load and test location (flange or body)? What time and timezone was the finding made?
- Q5. Have any WO-8150 assemblies containing lot AS-7781 shipped? If so, to which customer, and what is the contractual notification window?
- Q6. What revision does the ERP item master record for BSH-1210? Which revision did Birch quote in 2026-10?
- Q7. What are the usage history, open demand and forecast for BSH-1210? What first article date and production schedule does the plant need?
- Q8. Where are the plant's NCR, 8D and RFQ templates, standard quality clause set and commercial terms?
- Q9. Is Birch qualified on BSH-1210 specifically? Should Cedar (conditional, audit overdue) be invited, and with what requalification? Should Alder be invited back?
- Q10. Is BSH-1210 under any export-controlled program?
