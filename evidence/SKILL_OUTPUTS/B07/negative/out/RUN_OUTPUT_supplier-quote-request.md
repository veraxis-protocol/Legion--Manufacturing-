# supplier-quote-request — BSH-1210 — event SRC-2026-11-14-BSH-1210

This file is the skill's reply as it would be printed in the conversation (documents in full, records summarised). Synthetic test data. **Nothing has been sent to any supplier, and nothing has been awarded or ordered.**

Plant setup: `plant_setup.py find` returned no profile (`exists: false`, no rates, no open work); no artifact tools were used in this run (run rules), so no Plant setup / Open work page was looked for. Site: not stated.

---

## 1. Blocking condition (stated before the package)

**The package is assembled but cannot be released: the drawing revision is unverified.**

- No drawing file was supplied. `C:/LMFG/runs/B07-negative/work/inputs/supplier` holds only `demand.csv`, `bid_supplier_A.txt` and `bid_supplier_B.txt` (folder enumerated). The request mentions a drawing; it was not found in the inputs — *not found by enumerating the folder*, not proof it does not exist.
- No ERP item master is available, so there is no item-master revision to check against.
- The only revision evidence: `demand.csv` (MRP export) carries rev **A** on all 3 rows; Alder's quote states "rev A"; Birch's quote states no revision. An MRP row and a supplier's quote are not the controlled drawing. The title block has not been read because there is no drawing.
- Per the skill's degradation rule the revision comparison **cannot clear**, and the package stays blocked until document control confirms the revision and the drawing at that revision is attached.

**Restricted data (ITAR / EAR / export-controlled): not assessed.** No drawing title block or border to read and no plant program list on file. Nothing found in the inputs indicates restricted data, but the check could not be performed; it must be done when the drawing is attached, before release.

**Supplier-caused flag:** none. This is a direct request (`triggered_by: direct`), not a response to a supplier failure.

---

## 2. The supplier RFQ package

Template: the plant's controlled RFQ template is **not on file**; a neutral structure covering every required section is used. Placeholders in [brackets] must be filled by the buyer before release. No Word copy this session: no Word writer available (python-docx not installed; installing is not permitted).

=== SUPPLIER RFQ PACKAGE — SENDABLE ===
REQUEST FOR QUOTATION — SRC-2026-11-14-BSH-1210

1. Cover
We request your quotation for the part below, in the response format in Section 6. Issued by: [buyer name, company]. Date of issue: [date of release].

2. Technical package
- Part number: BSH-1210
- Description: Bronze flanged bushing 12x16x10 mm SAE 841
- Drawing: BSH-1210, revision [to be confirmed by document control — attach the drawing at that revision]
- Material / specification: SAE 841, as named in the part description. [Attach the specification document and any hardness, porosity, oil-impregnation or finish requirement exactly as the drawing states them.]
- Quote against the drawing revision stated above only. State that revision in your response.

3. Quantities and delivery requirements
- Historical usage: no purchase or receipt history for this part is provided with this request.
- Open demand (planned requirement from our MRP; export date [to be stated by buyer]):
  - December 2026: 800 each
  - January 2027: 1,200 each
  - February 2027: 1,200 each
  - Total over December 2026 to February 2027: 3,200 each
- Forecast beyond February 2027: no forecast is provided with this request.
- Required first article date: [to be set by buyer].
- Production deliveries: in the monthly quantities above; required delivery day within each month [to be set by buyer].

4. Quality requirements
[Quality clause list at its current revision — to be attached by the buyer: quality system certification, material certification, first article inspection, PPAP submission level if any, certificate of conformance, right of access, change notification, record retention, lot traceability, as the plant's standard and the customer program require.] State acceptance of each clause, or list each exception with your words.

5. Commercial terms
[Plant standard terms — to be inserted by the buyer: payment terms, Incoterm / freight basis and named place, packaging, liability, tooling ownership.] Quote on this basis. Do not substitute your own freight or payment basis; if you cannot quote on it, say so as an exception.

6. Mandated response format
Respond with every item below. A quotation returned in a different shape will be returned for restatement rather than interpreted on our side.
- Drawing revision quoted against.
- Unit price at each quantity, separately: 800 each; 1,200 each; 3,200 each. Not a lot price, not a blended rate.
- Currency, stated explicitly.
- Tooling and any NRE priced separately, never folded into the piece price; or a written statement that none is needed.
- Tooling ownership at the end of the contract.
- Lead time for first article, and lead time for production, each stated from a named event (for example, receipt of order, or approval of first article).
- Minimum order quantity.
- Price validity, as a date.
- Acceptance of each quality clause in Section 4, or each exception with your words.
- Any other exclusions or assumptions, listed rather than implied.

7. Response schedule
- Response due: [date — to be set by buyer]
- Send your response to: [buyer name and address]
- Technical questions: [named technical contact]. Answers given to one bidder will be shared with all bidders.
=== END ===

**Outbound check on the block above (run in code, `scripts/outbound_check.py`):** see section 9 — no unit price, PO number or total from purchase-order history (none exists in the inputs), no supplier name, no target price, no rate value, no "margin". Passed. Quantities in it are the MRP figures from the figures block.

---

## 3. Missing-items list (internal)

| # | Missing | Why it matters | Where it should have come from |
|---|---|---|---|
| 1 | Drawing BSH-1210 (any revision) | Suppliers quote what they are sent; revision cannot be verified; title block not readable; ITAR check impossible | M365 drawing library or an upload; not in `inputs/supplier` (folder enumerated) |
| 2 | ERP item-master revision for BSH-1210 | The hard-stop revision check cannot clear without it | NetSuite / Infor M3 item master, or the profile's `### ERP scope` revision field — neither available |
| 3 | Material/specification document for SAE 841 and any drawing hardness requirement | Alder's exception "hardness 25-45 HRF" cannot be judged against a requirement nobody has | Drawing notes / spec library — not supplied |
| 4 | Historical usage (POs, receipts) | Suppliers price volume; states only an absence | ERP purchase-order and receipt history — no such file in the inputs |
| 5 | Current price and incumbent | Cannot compare the bids with what is paid today | ERP PO history — not supplied |
| 6 | Forecast beyond Feb 2027 | Annual volume drives pricing | Planning / customer forecast — not supplied |
| 7 | MRP export date (as-of) | Demand picture cannot be dated | `demand.csv` has no export timestamp |
| 8 | First article date and required day within each month | Lead times cannot be judged against need | Planning data — not supplied; ask buyer |
| 9 | Quality clause set at current revision | Package incomplete; bids cannot accept clauses never issued. Flagged unverified; no plausible list assembled | `## Plant context` from onboarding / M365 template — no profile |
| 10 | Commercial terms standard | Bids came back on different freight bases (FOB origin vs DDP) | `## Plant context` — no profile |
| 11 | Approved supplier list | Every supplier is *not confirmed approved*; single-source status unknowable | `### Approved suppliers` in `## Plant context` — no profile |
| 12 | Supplier contact addresses | Email drafts held | ERP vendor records — not available |
| 13 | Response due date, buyer contact, technical contact | Package and drafts cannot go out | Buyer |
| 14 | Plant RFQ template | Neutral structure used | onboarding templates — not available |
| 15 | Dates on the two bids | Validity ("30 days") cannot be converted to a date; received_at null | The original emails/PDFs |
| 16 | Send history for the earlier RFQ that produced these two bids | Cannot tell what package or revision they were quoting against | Buyer — not reconstructed |

---

## 4. Candidate suppliers (internal)

| Supplier | ID | Approval status | Basis | Requalification |
|---|---|---|---|---|
| Alder Sintered Parts | unlisted | **not confirmed approved** | Named in `bid_supplier_A.txt`; no approved table, no ERP vendor records | Not known; at least first article; PPAP level unknown |
| Birch Powder Metal | unlisted | **not confirmed approved** | Named in `bid_supplier_B.txt`; same | Same |

Single-source risk: **cannot be determined** — no approved supplier table and no PO history, so the incumbent (if any) is unknown. No other candidate is named in the inputs; none is invented.

---

## 5. Supplier email drafts — not sent

Both are restatement requests that also carry the package. Nothing was sent; the buyer sends each from their own mailbox once the hold conditions are cleared.

Held, both drafts: no contact address on file for either supplier; no response due date set in the package; drawing revision not verified (no drawing and no ERP item master in this run); neither supplier confirmed approved, and no requalification decision from the buyer.

Held: the shared conditions above.
=== SUPPLIER EMAIL — HELD — Alder Sintered Parts ===
To: [recipient: not on file]
Subject: SRC-2026-11-14-BSH-1210 — restatement requested, BSH-1210 bronze flanged bushing (your quote Q-A-118)

Thank you for quote Q-A-118 for BSH-1210 rev A.

Attached is our RFQ package SRC-2026-11-14-BSH-1210 for BSH-1210, drawing revision [to be confirmed by document control before sending]. Please restate your quote in the mandated response format in Section 6 of the package. Specifically, your quote did not state:

- unit price at each requested quantity: 800, 1,200 and 3,200 each
- lead time for first article and for production, each from a named event
- tooling: a price, or a written statement that none is needed, and who owns the tooling
- price validity as a date
- acceptance of each quality clause in Section 4, with any exception listed
- payment terms, on the commercial basis in Section 5

Please also confirm whether the hardness exception in your quote still applies once you have reviewed the drawing and specification in the package, and state it against the drawing requirement it departs from.

Please reply by [response due date — to be set by the buyer] to [buyer name and address]. Technical questions to [technical contact]; answers given to one bidder are shared with all bidders. A quote in a different shape will be returned for restatement.

[Buyer name]
=== END ===

Held: the shared conditions above.
=== SUPPLIER EMAIL — HELD — Birch Powder Metal ===
To: [recipient: not on file]
Subject: SRC-2026-11-14-BSH-1210 — restatement requested, BSH-1210 bronze flanged bushing (your ref BPM-77)

Thank you for your quote BPM-77 for BSH-1210.

Attached is our RFQ package SRC-2026-11-14-BSH-1210 for BSH-1210, drawing revision [to be confirmed by document control before sending]. Please restate your quote in the mandated response format in Section 6 of the package. Specifically, your quote did not state:

- the drawing revision you quoted against
- unit price at 800 and at 1,200 each (in addition to 3,200)
- lead time for first article and for production, each from a named event
- tooling ownership
- minimum order quantity
- price validity as a date
- acceptance of each quality clause in Section 4, with any exception listed

Please quote on the commercial basis in Section 5 of the package.

Please reply by [response due date — to be set by the buyer] to [buyer name and address]. Technical questions to [technical contact]; answers given to one bidder are shared with all bidders. A quote in a different shape will be returned for restatement.

[Buyer name]
=== END ===

Outbound check on both email blocks (code, section 9): neither names the other supplier, quotes any price, PO, target price or rate, or says anything about other bids. Passed.

---

## 6. Bid records (summary; full records saved)

| Supplier | Source file | Prices as quoted | conformance | fields_missing |
|---|---|---|---|---|
| Alder Sintered Parts | bid_supplier_A.txt | 1,000 pcs 0.62 USD/ea; 3,000 pcs 0.55 USD/ea | off_format | unit price at 800, 1,200, 3,200; lead time FA and production from a named event ("4 weeks ARO", not split); tooling price or none-needed statement ("Tooling: existing."); tooling ownership; validity as a date ("30 days", undated quote); quality clause acceptance; payment terms |
| Birch Powder Metal | bid_supplier_B.txt | Unit price 0.49 USD at 3,200 pcs | off_format | unit price at 800, 1,200; lead time FA and production from a named event ("6-7 weeks"); tooling ownership; MOQ; price validity; quality clause acceptance; drawing revision quoted against |

Other mapped values: Alder — rev A, currency USD, MOQ 1,000, FOB origin, exception "hardness 25-45 HRF". Birch — revision not stated, currency USD, tooling 1,850 USD one time (separate from unit price), DDP Dayton, net 45. Both: `approval_status: not_confirmed_approved`, `received_at: null` (bids undated), `quality_clause_acceptance: not_stated`.

Saved: `out/sourcing/SRC-2026-11-14-BSH-1210/alder-sintered-parts.bid.txt`, `out/sourcing/SRC-2026-11-14-BSH-1210/birch-powder-metal.bid.txt`.

---

## 7. Comparison and recommendation (summary)

Full page: `C:/LMFG/runs/B07-negative/work/out/sourcing-output/bid-comparison.html` (offered page; the dashboard was not updated: no artifact tools in this run).

Safety status: not assessed (sourcing event; no safety record involved). Freshness: MRP export undated; bids undated.
No bid is ready for buyer review (0 of 2); provisional recommendation is to request restatement from both against the package once the revision is confirmed. Birch is the only bid priced per unit at the 3,200 requirement (0.49 USD, extended 1,568.00 USD, 3,418.00 USD first-order total including 1,850.00 USD tooling) but does not state its revision and gives 6-7 weeks with no start event. Alder quoted rev A with existing tooling and 4 weeks ARO but priced 1,000/3,000 only, MOQ 1,000 exceeds the 800 December bucket, and takes a hardness exception (25-45 HRF). Freight bases differ (FOB origin vs DDP Dayton) and are not comparable. Illustrative: ordered today, Alder arrives 2026-12-12; Birch 2026-12-26 to 2027-01-02 (start event not stated) — whether either meets December cannot be judged without a required date.

**Next step: ask both suppliers to restate against the package, look into other suppliers, or pursue one of these bids?** No selection is recorded; the buyer decides, with their name.

---

## 8. Response tracker — `## Sourcing events`

Not saved to your Open work page: no artifact tools in this run. Written to `out/plant-setup/open-work/open-work.md` instead (lasts only as long as that folder). Paste this table back next time.

### SRC-2026-11-14-BSH-1210 — BSH-1210 bronze flanged bushing, rev A (unverified)
Trigger: direct | Breaks: 800, 1,200, 3,200 each | Due: not set | Status: open (package blocked: revision unverified)

| Supplier | Approval | Drafted | Sent (per buyer) | Due | Response | Chased |
|---|---|---|---|---|---|---|
| Alder Sintered Parts | not confirmed approved | 2026-11-14 (restatement, HELD) | not known — not reconstructed | not set | bid Q-A-118 (undated), sourcing/SRC-2026-11-14-BSH-1210/alder-sintered-parts.bid.txt | - |
| Birch Powder Metal | not confirmed approved | 2026-11-14 (restatement, HELD) | not known — not reconstructed | not set | bid BPM-77 (undated), sourcing/SRC-2026-11-14-BSH-1210/birch-powder-metal.bid.txt | - |

Days past due: not computable (no due date). 2 of 2 known suppliers have responded; whether anyone else was asked is not known.

---

## 9. Figures block (internal; computed by `scripts/compute_bsh1210.py`)

| Figure | Value | Computed from | Filter |
|---|---|---|---|
| MRP rows for BSH-1210 | 3 | demand.csv | item == 'BSH-1210' |
| Revisions on those rows | A | demand.csv | distinct rev |
| MRP window | 2026-12 to 2027-02 | demand.csv | min/max month |
| MRP requirement total | 3,200 | demand.csv | sum qty_required |
| MRP requirement 2026-12 / 2027-01 / 2027-02 | 800 / 1,200 / 1,200 | demand.csv | per month |
| Quantity breaks | 800, 1,200, 3,200 | computed | min monthly, max monthly, window total |
| Historical usage rows | 0 — not found by enumerating inputs/supplier | inputs folder | no PO/receipt file present |
| Bids received | 2 | inputs/supplier | bid_*.txt |
| Bids off_format | 2 | bid records | conformance == off_format |
| Bids ready for buyer review | 0 | bid records | all four prerequisites |
| Alder fields_missing count | 10 | bid record | mandated fields checked one by one |
| Birch fields_missing count | 9 | bid record | same |
| Bids priced per unit at 800 / 1,200 / 3,200 | 0 / 0 / 1 | bid records | unit_price not null at break |
| Birch extended at 3,200 | 1,568.00 USD | bid record | 0.49 × 3,200 |
| Birch first-order total at 3,200 (incl. tooling) | 3,418.00 USD | bid record | 1,568.00 + 1,850 |
| Alder extended at own qty 1,000 / 3,000 (not requested breaks) | 620.00 / 1,650.00 USD | bid record | 0.62 × 1,000; 0.55 × 3,000 |
| Alder arrival if ordered 2026-11-14 (illustrative) | 2026-12-12 | bid + session date | 4 weeks ARO |
| Birch arrival if ordered 2026-11-14 (illustrative) | 2026-12-26 to 2027-01-02 | bid + session date | 6-7 weeks, start event not stated |
| Approved suppliers known | not available | plant profile | plant_setup.py find: exists=false |

Outbound check results: see `out/sourcing/SRC-2026-11-14-BSH-1210/outbound_check.txt`.

---

## 10. Questions for the buyer (recorded, not asked)

1. Which drawing revision is this sourcing action against? Please supply the drawing (title block will be read) and confirm the ERP item-master revision with document control. The package is blocked until then.
2. Is any of the BSH-1210 technical data export-controlled (ITAR/EAR) or under a restricted customer program?
3. What is the required first article date, and the required delivery day within each MRP month?
4. What is the response due date, the buyer contact and the technical contact for the package?
5. Please supply the current quality clause set and the plant's standard commercial terms (payment, Incoterm and place, packaging, liability, tooling ownership). Does the clause set vary by customer program for this part?
6. Which suppliers are approved for sintered bronze bushings, and is there an incumbent and a current price? Are Alder and Birch approved, and if not, which requalification path applies?
7. Contact addresses for Alder Sintered Parts and Birch Powder Metal?
8. Are 800 / 1,200 / 3,200 the right quantity breaks, and is there a forecast beyond February 2027 and any usage history to state?
9. When, and against what package and revision, were the earlier requests sent that produced quotes Q-A-118 and BPM-77, and on what dates did the quotes arrive?
10. Does the drawing specify hardness for BSH-1210, so Alder's "25-45 HRF" exception can be assessed?
11. What company / plant name should the Open work page and event be filed under?
12. Next step: restate both, look further, or pursue one bid? (Any selection needs your decision and your name.)
