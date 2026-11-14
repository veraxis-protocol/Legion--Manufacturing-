# Chain 5 continuation - BSH-1210 lot AS-7781 (SYNTHETIC test data)

**Approvals recorded, as relayed by the coordinator.** Names are recorded exactly as given.
- **NCR:** approved as drafted by "Test Quality Owner (LEGION WO-LMFG-004 test operator)" at 2026-11-14T17:12-05:00 (run host clock, the time the approval reached this run).
- **Gate 1, supplier-caused determination:** owned and approved by the same named test operator, at the same time, **while the receiving-tester calibration check (candidate C2) is still pending.**
- **Revision:** drawing BSH-1210 rev A confirmed current by document control (the same test operator), because no ERP exists. The revision hard stop is cleared on that confirmation, **not** on an ERP item-master match.

Nothing has been sent, released or written to any system. Gate 2 (release) is still open. No Word or Excel copies were made, because no writer is available.

---

## Step 3 - Corrective action

### 8D - DRAFT (neutral eight-discipline structure; plant or customer controlled template not on file)
Reference: 8D-NCR-UNASSIGNED (NCR number still to be assigned). Part BSH-1210 rev A, lot AS-7781.

**D1 - Team (proposed; the owner edits)**
| Role | Name |
|---|---|
| Quality owner / 8D owner | Test Quality Owner (LEGION WO-LMFG-004 test operator) |
| Receiving inspection | not named in the finding |
| Purchasing / buyer | not named |
| Assembly line 2 (WO-8150) | not named |
| Supplier quality contact, Alder Sintered Parts (fictitious) | not on file |

**D2 - Problem description**
At receiving inspection on 2026-11-12 (time and timezone not recorded), five samples were taken from lot AS-7781 of BSH-1210 rev A flanged bushings. The lot came from Alder Sintered Parts (fictitious) on receipt RCV-9921, PO-30655, quantity 1,000.

All five samples measured 47, 49, 46, 50 and 48 HRF (mean 48; 5 of 5 above the limit). The requirement is 25-40 HRF, from the drawing BSH-1210 rev A notes. The supplier's C of C states 32 HRF. Oil content was not tested.

Suspect quantity is 1,000 each: the whole lot, on lot scope.

**D3 - Interim containment (from the approved NCR; owners still to be assigned)**
| Location | Qty | Action | Status |
|---|---|---|---|
| Installed at customer | **not checked** | Confirm whether any WO-8150 assemblies containing AS-7781 shipped and were installed | open, immediate |
| At customer | **not checked** | Check shipments of WO-8150 output; quarantine at the customer if any shipped | open, immediate |
| In transit | **not checked** | Intercept any WO-8150 output containing AS-7781 | open, immediate |
| WIP, line 2 / WO-8150 | 400 (issue record) | Stop use; hold loose parts and assemblies; count loose vs assembled; tag | open, immediate |
| Receiving quarantine Q-1 (mapped to finished goods) | 600 | Hold and tag; check stores for WO-8150 assemblies | 600 held per finding; stores check open |

Disposition of the 1,000 is still pending. The customer-side locations stay open until they are checked. Escape is not ruled out.

**D4 - Root cause (ranked; not a single verdict)**
- **Leading (medium confidence): C1, supplier material or process on lot AS-7781.**
  - The causal chain: material/process deviation at the supplier -> parts above 40 HRF as received -> the C of C value does not represent the lot.
  - For: 5 of 5 out of spec at receipt, before any plant processing. 1 of 3 lots from this supplier failed, while AS-7702 and AS-7744 passed. That is small numbers.
  - Against: the C of C says 32 HRF. No gage ID or calibration was recorded. There is no supplier mechanism evidence. **The weak point is link 1: there is nothing yet For a specific mechanism.**
- **Second: C2, receiving hardness measurement error.**
  - **Still open.** The calibration check is pending and was not run in this session.
- **Third: C3, lot identity mix-up.**
- **Verification plan (cheapest discriminating test):** verify the receiving tester on a certified HRF reference block. Then re-test 5 parts from Q-1, and a retained AS-7744 part if one exists. If the verified tester reads AS-7781 inside 25-40 HRF, C1 is killed and this 8D, the supplier corrective action request and the sourcing trigger must be revisited.

**D5 - Chosen corrective actions (each names the D4 link it breaks)**
1. **Supplier corrective action request to Alder Sintered Parts** (draft below; held). It asks the supplier to identify the mechanism behind lot AS-7781's hardness, to check their other stock, and to state the basis of the 32 HRF on the C of C.
   - Breaks C1 link 1, *material/process deviation at the supplier*, once the supplier identifies and corrects the mechanism.
   - Effectiveness is judged in D6.
2. **Require measured hardness values, with the test method and the test record reference, on each lot's C of C for BSH-1210**, in place of a single stated value.
   - Breaks C1 link 3, *the C of C does not represent the lot*. It makes the certificate a checkable test record that incoming inspection compares against.
   - This needs the quality owner's decision on wording.

Not in D5:
- **Containment, moved to D3:** quarantine, sort and disposition of the 1,000.
- **Verification, not corrective action:** the tester calibration check and re-test. This is the D4 test.
- **Improvement, not corrective action:** sourcing an alternate supplier (Step 4). It removes single-source exposure but breaks no link in the chain.

**D7 - Prevent recurrence (system level)**
- **Receiving hold until disposition.** 400 of the 1,000 pieces reached assembly line 2 (WO-8150) while the lot failed incoming hardness. Purchased lots should not be issued before the receiving inspection disposition is recorded. *Whether the issue happened before or after the test is not recorded in the finding. Confirm before adopting this as written.*
- **Receiving inspection records carry the gage ID and calibration due date** for every measured characteristic. Their absence is what leaves C2 open in this investigation.
- **Incoming verification of C of C claims for hardness on sintered bronze parts.** A stated value that disagrees with measurement triggers a hold, not just an NCR.
- Recurrence status: there is no searchable history, so D7 does not address a prior failed fix. Whether this has happened before is unknown.

**D6 - Implement and verify (PLACEHOLDER; needs real-world outcome)**
| Field | Value |
|---|---|
| Action implemented (D5 #) | |
| Date implemented | |
| Verification method | |
| Evidence of effectiveness (lots, readings) | |
| Verified by | |
| Effectiveness check due | |

**D8 - Close and recognize (PLACEHOLDER; needs human sign-off)**
| Field | Value |
|---|---|
| Closure approved by | |
| Date | |
| Team recognized | |

### Supplier corrective action request (draft; HELD)
Held for two reasons: no supplier contact address is on file, and the quality owner and buyer must release it. The C2 tester check is pending; the quality owner chose to act anyway, and the request says our re-check is under way.

```
=== SUPPLIER CORRECTIVE ACTION REQUEST — HELD — Alder Sintered Parts (fictitious) ===
To: [recipient: not on file], Alder Sintered Parts (fictitious)
Subject: Supplier corrective action request - BSH-1210 rev A, lot AS-7781 - hardness above drawing limit
Our reference: NCR [number to be assigned]

Part: BSH-1210 Flanged bushing, drawing revision A (2025-06-02)
Your lot: AS-7781, our receipt RCV-9921 on PO-30655, quantity 1,000

Nonconformance: Drawing BSH-1210 rev A requires hardness 25-40 HRF. Our receiving
inspection on 2026-11-12 measured 47, 49, 46, 50 and 48 HRF on five samples (all
above 40 HRF). The certificate of conformance supplied with lot AS-7781 states 32 HRF.
We are re-verifying our hardness tester and re-testing retained parts, and will share
the results.

Lot AS-7781 is held at our site pending disposition.

Please respond by [date: to be set by the quality owner] with:
1. Containment: any other stock, WIP or shipments of BSH-1210 from the same material
   lot or production run as AS-7781, and their status.
2. The hardness test record behind the 32 HRF on the C of C: method, scale, load,
   instrument, calibration status, sample size and individual readings.
3. Retained-sample hardness and oil content results for lot AS-7781.
4. Root cause of the hardness deviation, and corrective actions with dates.
5. How future C of Cs for BSH-1210 will report measured hardness values per lot.

Contact for questions: [quality contact: to be named]
=== END ===
```
Outbound check, this block: no price, no other supplier's name, no alternate-sourcing information, no rate. **Pass.**

---

## Step 4 - Alternate-source RFQ package (supplier-quote-request)

**Trigger:** the supplier-caused flag is **approved**: supplier_caused, medium confidence, leading candidate. Its evidence carries forward with it.
- **Evidence against is open:** the C of C states 32 HRF, and no gage or calibration was recorded.
- **Competing candidate C2 (receiving tester error) is untested.**

This is therefore a sourcing action against a supplier-caused finding that is **approved but not yet confirmed**. If the tester check kills C1, the buyer should revisit this event.

**Gate check:** flag approved. Revision rev A confirmed by document control (test operator), with no ERP to cross-check. Restricted data: no ITAR, EAR or export marking found in the drawing text, and the program status was not stated; this is recorded, not cleared by an owner. **Release (Gate 2): NOT given. Nothing is sent.**

**SINGLE-SOURCE RISK, stated first.** approved_suppliers.csv records only the implicated supplier, Alder, as a current source for BSH-1210. **The table lists no supplier as qualified on this part other than the implicated one.** One other supplier, Birch, is approved for the commodity, and its part qualification is not recorded. Requalification of any alternate (samples, first article, PPAP) takes weeks to months, and this RFQ starts that clock. It does not shorten it.

### The package

```
=== SUPPLIER RFQ PACKAGE — SENDABLE ===
REQUEST FOR QUOTATION
Reference: SRC-2026-11-14-BSH-1210
Plant RFQ template: not on file - neutral structure used

1. Part and technical package
   Part: BSH-1210 Flanged bushing
   Drawing: BSH-1210, revision A, dated 2025-06-02 (attached). Quote against revision A only.
   Material: sintered bronze SAE 841, oil impregnated, 18 percent min by volume.
   Key characteristics (per drawing): ID 12.000 +0.018/+0.000 after press fit;
   OD 16.000 +0.034/+0.023; length 10.0 +/-0.1; flange OD 22 x 2.0 thick;
   hardness 25-40 HRF.

2. Demand picture
   Quantities to quote (each break priced separately): [quantity breaks: to be set by buyer]
   Historical usage: [to be stated by buyer, with its window and as-of date]
   Open demand: [to be stated by buyer]
   Forecast annual volume: [to be stated by buyer, labelled as a forecast]

3. Delivery requirements
   Required first article date: [to be set by buyer]
   Production schedule to support: [to be set by buyer]

4. Quality requirements
   - Certificate of conformance per lot (drawing BSH-1210 rev A).
   - [Plant standard quality clause set to be attached: certification level, material
     certification, first article inspection, PPAP level, right of access, change
     notification, record retention, lot traceability - not on file, unverified]

5. Commercial terms (the bid must assume these)
   Payment terms: [plant standard - not on file]
   Incoterms / freight basis: [plant standard - not on file]
   Packaging: [plant standard - not on file]
   Tooling ownership: [plant standard - not on file]

6. Mandated response format - bids in any other shape will be returned for restatement,
   not normalised by us
   a. Unit price at EACH quantity break above, one line per break (no averages or blends).
   b. Tooling and NRE priced separately, never included in the unit price.
   c. Tooling ownership at the end of the contract, stated.
   d. Lead time split into (i) first article and (ii) production, each stated in weeks
      from a named event (receipt of order, or approval of first article).
   e. Minimum order quantity.
   f. Currency, stated explicitly.
   g. Price validity period.
   h. Exclusions and assumptions, listed. Anything not listed is taken as included.
   i. Confirmation of each quality requirement in section 4: accepted, or the exception.

7. Response schedule
   Response due: [date: to be set by buyer]
   Send bids to: [buyer name and address: to be set]
   Technical questions: [named contact: to be set]. Answers given to one bidder are
   shared with all bidders.
=== END ===
```

**Outbound check on the package:** I read the block alone and checked it with code (`out/scripts/outbound_check.py`).
- No unit price, PO number or total from PO history. PO-30655 and the 1,000 receipt quantity are kept out.
- No supplier name, no target price, no rate, no "margin".
- **Result: PASS.**
- It holds unfilled placeholders, listed below. **The buyer must fill them before release.**

### Missing items (internal)
| Missing | Why it matters | Should come from |
|---|---|---|
| Quantity breaks, usage history, open demand, forecast | A bid without volume context is priced defensively | ERP usage and planning. No ERP; not in inputs. *Internal note: 3 receipts from Alder are recorded (Sep, Oct, Nov 2026); only the latest quantity (1,000) is stated. This is not put in the package* |
| First article date, production schedule | The buyer's delivery requirement | Planning. Not in inputs |
| Standard quality clause set (incl. PPAP level) | Part of the price; **set unverified** | Plant context from onboarding. Not on file |
| Commercial terms | Comparability (delivered vs ex-works) | Plant standard. Not on file |
| Due date, bid recipient, technical contact | Response schedule | Buyer |
| Supplier contact addresses, vendor IDs | Emails are held without them | ERP vendor records. Not available |
| Current price and terms (internal baseline only) | Buyer comparison; never in the package | PO-30655 price. Not in inputs |
| Export-control status of the program | Restricted-data gate | Compliance owner. Not stated |
| Revision Birch quoted in 2026-10 | That earlier quote may be against another revision and is not reusable until checked | Buyer / Birch quote file. Not in inputs |

### Candidate suppliers (internal; from approved_suppliers.csv only)
| Supplier | Approval status | Basis | Requalification | Invite? |
|---|---|---|---|---|
| Birch Powder Metal (fictitious) | **approved** (commodity) | Row "sintered bronze and iron", matched on "sintered bronze"; audit 2026-02-20 | Part qualification not recorded: samples, FAI, PPAP. Weeks to months | Yes (draft below) |
| Cedar Bearings Inc (fictitious) | **conditional: not confirmed approved**; audit overdue (2024-06-15) | Row "bronze bushings" | Audit plus FAI before production | Draft held pending the buyer's requalification decision |
| Alder Sintered Parts (fictitious) | approved; **incumbent, implicated** | Row "sintered bronze"; current source BSH-1210 | n/a | The buyer's call. No draft |

Counts (computed): 3 rows; 2 approved for bronze; 1 approved excluding the implicated supplier; 1 conditional.

### Supplier emails (one per supplier; none sent)
**Held, both drafts:** no contact email is on file, and the package has no response due date yet. These conditions apply to both. Nothing has been sent. The buyer sends each one from their own mailbox after release.

Held: the shared conditions above.
```
=== SUPPLIER EMAIL — HELD — Birch Powder Metal (fictitious) ===
To: [recipient: not on file]
Subject: RFQ SRC-2026-11-14-BSH-1210 - BSH-1210 flanged bushing, drawing rev A

Hello,

Please find attached our request for quotation SRC-2026-11-14-BSH-1210 for the
BSH-1210 flanged bushing, drawing BSH-1210 revision A (2025-06-02). Please quote
against revision A only.

Responses are due by [date: to be set by buyer] to [buyer name and address: to be set].
Your bid must follow the mandated response format in section 6 of the package; bids
in another format will be returned for restatement. Technical questions to
[named contact: to be set]; answers are shared with all bidders.

Regards,
[buyer name]
=== END ===
```

Held: the shared conditions above, and Cedar Bearings Inc is not confirmed approved (conditional, audit overdue). It needs the buyer's requalification decision.
```
=== SUPPLIER EMAIL — HELD — Cedar Bearings Inc (fictitious) ===
To: [recipient: not on file]
Subject: RFQ SRC-2026-11-14-BSH-1210 - BSH-1210 flanged bushing, drawing rev A

Hello,

Please find attached our request for quotation SRC-2026-11-14-BSH-1210 for the
BSH-1210 flanged bushing, drawing BSH-1210 revision A (2025-06-02). Please quote
against revision A only.

Responses are due by [date: to be set by buyer] to [buyer name and address: to be set].
Your bid must follow the mandated response format in section 6 of the package; bids
in another format will be returned for restatement. Technical questions to
[named contact: to be set]; answers are shared with all bidders.

Regards,
[buyer name]
=== END ===
```
Outbound check on both emails (code): no other supplier's name, no price, no PO number, nothing about other bids. **PASS.**

### Response tracker (printed; **not saved**)
There is no Open work page, and artifact tools are not permitted this run. Paste this table back next time and the event picks up from it.

| Supplier | Approval | Drafted | Sent (per buyer) | Due | Response | Chased |
|---|---|---|---|---|---|---|
| Birch Powder Metal (fictitious) | approved | 2026-11-14 (held) | - | not set | - | - |
| Cedar Bearings Inc (fictitious) | not confirmed approved | 2026-11-14 (held) | - | not set | - | - |

Status: open. 0 of 0 sent. No bids, so no comparison or recommendation yet. Sourcing event record: `out/records/sourcing-event-SRC-2026-11-14-BSH-1210.yaml`.

### Three timestamps
| Stamp | Value |
|---|---|
| escape_detected_at | null: no parts were placed at or past a customer. The customer side has not been checked |
| determination_made_at | 2026-11-14T17:02-05:00. *determination_made_at is the middle of the three; this cannot be reconstructed afterwards.* |
| rfq_issued_at | **not recorded.** It is recorded only when the buyer says the package went out, with their date |

### Pages and register
- `out/pages/quality-page.html`: Quality register view, updated for the approved NCR and the drafted 8D. **The Quality Register was not updated: artifact tools are not permitted in this run.**
- `out/pages/supply-chain-page.html`: Supply Chain page, updated with the package status. It is an offered page.

### Still open
1. Gate 2: the buyer fills the placeholders and releases the package and emails.
2. The C2 tester calibration check (it could invalidate C1).
3. The customer-side shipment check for WO-8150.
4. Disposition of the 1,000 pieces.
5. NCR number and site.
6. Contact addresses.
7. Whether Alder is invited back.
8. A requalification decision for Cedar.
