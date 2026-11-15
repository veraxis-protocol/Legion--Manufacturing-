# BSH-1210 sourcing event SRC-2026-11-15-BSH-1210 — INTERNAL notes (do not send)

All inputs are synthetic test data. Figures are from `out/figures.md`, produced by `out/scripts/compare_bids.py`.
Nothing has been sent to any supplier and no award has been made. No ERP, mailbox or supplier was contacted.

## 1. Gates

| Gate | Result |
|---|---|
| Trigger | Direct request from the buyer. No supplier-caused flag, so no approved flag is needed |
| **Revision check** | **Not cleared, so release is held.** The drawing title block reads *"drawing revision A (2025-06-02)"* (`inputs/supplier/BSH-1210_drawing_revA.md`, line 2). The MRP export rows are all at rev A (3 of 3 rows, `demand.csv`). **No ERP item master is available in this session**, so the revision cannot be checked against the controlled record. Document control or the buyer must confirm that A is the current released revision before the package goes out |
| Restricted data (ITAR/EAR) | No export-control marking or distribution statement on the drawing text. No plant profile, so no customer-program classification is on file. Not blocking, but this is unverified against program data |
| Plant setup | No plant profile, rates, approved supplier table or Open work page (`plant_setup.py find` reported `exists: false`). The controlled RFQ template was not available, so the package uses a neutral structure |

## 2. Missing items (what, why it matters, where it should come from)

| # | Missing | Why it matters | Should come from |
|---|---|---|---|
| 1 | ERP item-master revision for BSH-1210 | The revision check cannot clear without it, and the package stays held | NetSuite / Infor M3 item master. No connector in this session |
| 2 | Historical usage (consumption, PO and receipt history) | Suppliers price a one-off 3,200 pcs differently from a running part. Without it, the package says no history is provided | ERP purchase/receipt history. **Not found: no usage, PO or receipt file in `./inputs`** (folder enumerated) |
| 3 | Current supplier, current price and terms | There is no baseline for judging whether either bid is good, and no incumbent to compare | ERP PO history. Not in inputs. Alder states "Tooling: existing", which suggests they may already make this part. **Unconfirmed** |
| 4 | Forecast or EAU beyond Feb 2027 | Volume after the 3-month MRP horizon is unknown, and the package says so rather than inventing it | Planning or sales forecast. Not in inputs |
| 5 | Exact need date in December 2026 | Both lead times are measured against it. The MRP export gives months only | MRP/planning detail at date level, or the buyer |
| 6 | Plant standard quality clauses at current revision | The clause set in the package is only what the drawing states (CoC per lot), plus FAI and lot traceability as asked-for items. **The whole set is unverified.** Placeholder in package section 4 | Plant quality manual / onboarding clause set. Not available |
| 7 | Customer-program quality variation | It is not known whether BSH-1210 ships into programs with different flow-downs (PPAP level, AS9100/IATF). If so, surface it per program, never merge | Plant context / customer requirements. Not available |
| 8 | Standard commercial terms (Incoterm, payment, packaging, liability, tooling ownership) | The bids came back on different bases (FOB origin vs DDP), which is exactly what a mandated basis prevents. Placeholders in package section 5 | Plant commercial standard. Not available |
| 9 | Response due date, buyer contact, technical contact, delivery address | Required before any email can be released. Placeholders in package | Buyer |
| 10 | Approved supplier list for sintered bronze bushings | Neither bidder can be confirmed as approved | Plant context `### Approved suppliers`. Not available |
| 11 | Supplier contact addresses | Email drafts are addressed `[recipient: not on file]` | ERP vendor records. Not available |
| 12 | Material spec reference for SAE 841 test method (oil content, hardness method) | Hardness 25-40 HRF is on the drawing, but the acceptance test method and the oil-content verification method are not stated | Drawing notes / material spec. **Not found:** the drawing text references no spec document |
| 13 | Drawing file itself (PDF/CAD) | Only a text rendering of rev A was supplied. The real title block must be attached to the package | M365 drawing library |

## 3. Candidate suppliers

**No approved supplier table and no ERP vendor records are available, so every candidate is _not confirmed approved_.** Single-source status cannot be assessed. If the plant has only one approved source for sintered bronze bushings, that is a bigger finding than this RFQ, and the buyer should check.

| Supplier | ID | Approval status | Basis | Requalification path |
|---|---|---|---|---|
| Alder Sintered Parts (fictitious) | unlisted | **not confirmed approved** | Returned a bid (`bid_supplier_A.txt`). Says tooling is "existing", so may be a current or past source. Unconfirmed | If not already approved: first-article inspection against rev A (incl. bore after press fit, hardness, oil content), CoC review. Weeks |
| Birch Powder Metal (fictitious) | unlisted | **not confirmed approved** | Returned a bid (`bid_supplier_B.txt`) | New tooling, then first-article samples, FAI and possibly a process audit. Weeks to months; tooling time not stated |

The buyer may want to add more candidates from the approved list. Each one gets its own draft.

## 4. Response tracker

| Supplier | Approval | Drafted | Sent (per buyer) | Due | Response | Chased |
|---|---|---|---|---|---|---|
| Alder Sintered Parts | not confirmed approved | 2026-11-15 (restatement + package, HELD) | — not recorded | [not set] | bid received, undated: `out/sourcing/SRC-2026-11-15-BSH-1210/alder-sintered-parts.bid.yaml` (off-format) | — |
| Birch Powder Metal | not confirmed approved | 2026-11-15 (restatement + package, HELD) | — not recorded | [not set] | bid received, undated: `out/sourcing/SRC-2026-11-15-BSH-1210/birch-powder-metal.bid.yaml` (off-format) | — |

Both bids arrived before this package existed, so they answer an earlier or informal request, not this format. Status: **open**.
**Not saved:** there is no Open work page this session. Paste this table back next time and I'll pick up from it.
