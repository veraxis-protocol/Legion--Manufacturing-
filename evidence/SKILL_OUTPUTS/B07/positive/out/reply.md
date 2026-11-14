# Sourcing event SRC-2026-11-14-BSH-1210 — BSH-1210 flanged bushing

Skill followed: `supplier-quote-request` (Claude for Manufacturing plugin). SYNTHETIC test data for a fictitious plant. **Nothing has been sent to any supplier and nothing has been awarded or ordered.** No ERP, M365 or Open work page was reachable in this session.

Safety status: not assessed (not applicable to a sourcing package).

---

## 1. Gates — read before the package

**Revision check: UNVERIFIED — package release is blocked until confirmed (hard stop, `reference/hard-stops.md`).**

| Check | Revision | Source | Date |
|---|---|---|---|
| Drawing document itself | **A** | `BSH-1210_drawing_revA.md`, heading line "drawing revision A (2025-06-02)" — a document heading, not a formal title block; the filename also says revA, but the filename was not relied on | 2025-06-02 |
| Document library record (M365 metadata) | not available | no M365 connection this session | — |
| ERP item master | **not available** | no ERP connection and no item-master export among the inputs; the revision location in the ERP is not set (no plant profile) | — |
| Revision the current demand is stated against | **A** | `demand.csv`, column `rev`, all 3 rows | export date not stated |

The drawing and the MRP demand agree on Rev A, but the ERP item master — the check this gate requires — could not be read, so the revision cannot clear. **Owner question (document control): confirm that BSH-1210 Rev A (2025-06-02) is the current released revision on the item master.** Until then the package below is a draft held at the release gate and every supplier email is HELD.

**Restricted-data gate: nothing found by search.** The four input files were searched for ITAR, EAR, export-control, distribution-statement, "restricted" and "controlled" markings (case-insensitive): no match. The customer program this part serves is not known (no plant context on file), so a controlled-program flag could not be checked. Not a block; recorded.

**Trigger:** direct request (no supplier-caused flag; nothing to approve on that gate).

---

## 2. The supplier RFQ package (draft, release blocked on the revision check)

Template: **the plant's controlled RFQ template is not on file** (no plant profile / onboarding) — neutral structure used, flagged. Bracketed items are for the buyer to fill; they are listed in section 4.

=== SUPPLIER RFQ PACKAGE — SENDABLE ===
REQUEST FOR QUOTATION — SRC-2026-11-14-BSH-1210
Part: BSH-1210 Flanged bushing — drawing revision A, dated 2025-06-02
Issued by: [buyer name, company and site — not on file]
Response due: [date — to be set by the buyer]

1. TECHNICAL PACKAGE (quote against Revision A only)
Attached: BSH-1210 drawing, revision A (2025-06-02). Requirements as stated on that drawing:
- Material: sintered bronze SAE 841, oil impregnated 18 percent minimum by volume
- ID 12.000 +0.018/+0.000 after press fit
- OD 16.000 +0.034/+0.023
- Length 10.0 +/-0.1
- Flange OD 22 x 2.0 thick
- Hardness 25-40 HRF
- Certificate of conformance per lot
State the drawing revision you quoted against. A bid that does not state Revision A cannot be evaluated.

2. QUANTITIES AND DEMAND
Historical usage: no purchase or receipt history is provided with this request.
Open demand (planning requirement, not a purchase order): 3,200 pieces over December 2026 to February 2027 —
  December 2026: 800 pcs; January 2027: 1,200 pcs; February 2027: 1,200 pcs.
Forecast / estimated annual usage: none supplied; annual volume beyond February 2027 is not yet established.
Quantity breaks to quote, each separately: 800 pcs, 1,200 pcs, 3,200 pcs.

3. DELIVERY REQUIREMENTS
First requirement: 800 pcs in December 2026.
Required first article date: [to be set by the buyer].
Production schedule to land against: monthly quantities as in section 2.

4. QUALITY REQUIREMENTS
- Certificate of conformance with each lot (drawing requirement).
- [Further quality clauses — certification standard, material certification, first article inspection, PPAP level if any, right of access, change notification, record retention, lot traceability — to be inserted by the buyer from the plant's current clause list.]
State acceptance of each clause, or list each exception in your own words.

5. COMMERCIAL TERMS (quote on this basis)
- Freight / Incoterm: [buyer to state one basis and delivery point]
- Payment terms: [buyer to state]
- Packaging: [buyer to state]
- Liability: [buyer to state]
- Tooling ownership: [buyer to state the plant's position]

6. MANDATED RESPONSE FORMAT
Reply in this structure. A bid returned in a different shape will be sent back for restatement rather than normalised on our side.
a. Drawing revision quoted against
b. Unit price at 800, at 1,200 and at 3,200 pcs — one line each, per piece, not per lot
c. Currency
d. Tooling / NRE: one-time price stated separately (or state in writing that no tooling charge applies), never folded into the piece price
e. Tooling ownership at end of contract
f. Lead time to first article, from a named event (e.g. receipt of order)
g. Lead time for production quantities, from a named event
h. Minimum order quantity
i. Price validity, as a date
j. Freight basis as quoted, if different from section 5
k. Acceptance of each quality requirement in section 4, or the exception
l. Every exclusion or assumption, listed

7. RESPONSE SCHEDULE
Send your bid to: [buyer name and email]
Technical questions to: [named technical contact and email]. Answers given to one bidder will be shared with all bidders.
=== END ===

**Outbound check on the block above (read alone):** no unit price, PO number or total from purchase-order history (none on file); no other supplier's name; no target price; no rate value; no margin wording. Passes. Note: it contains no reference to either returned bid.

---

## 3. Internal notes (not for any supplier)

- **What the plant pays today: unknown.** No purchase-order history was supplied, so there is no incumbent price to compare against, and no incumbent supplier is identified. The package is being sourced blind to current cost — say so to the buyer.
- **Quantity breaks 800 / 1,200 / 3,200 are proposed from the MRP export** (first month, largest month, three-month total). They are not plant-given; the buyer should confirm them before release.
- **No forecast was inflated or invented.** The package states only the MRP requirement and the absence of history and forecast.
- Clause set is **unverified as a whole**: only the certificate-of-conformance requirement was found on the part record (the drawing). No standard list was assembled.

---

## 4. Missing items (internal)

| # | Missing | Why it matters | Where it should have come from | Search that did not find it |
|---|---|---|---|---|
| 1 | ERP item-master revision for BSH-1210 | Revision gate cannot clear; package blocked | ERP item master (NetSuite / Infor M3) or an item-master export | No ERP connector; 4 input files enumerated, no item-master file |
| 2 | Historical usage (POs, receipts) | Suppliers price volume; no incumbent price for comparison | ERP purchase-order and receipt history | Inputs enumerated; none present |
| 3 | Forecast / EAU beyond Feb 2027 | 3,200 pcs over 3 months is all a supplier can price against | ERP forecast or planning | `demand.csv` holds MRP requirement only |
| 4 | As-of date of the MRP export | Demand picture freshness cannot be stated | Export file header or filename | Not in `demand.csv` (comment line says only "MRP export (fictitious)") |
| 5 | Required first article date | Lead-time readiness cannot be judged | Planning data or buyer | Not in drawing, demand or request |
| 6 | Response due date | Every email draft is HELD; no days-past-due possible | Buyer | Not in request |
| 7 | Plant quality clause list (current revision) | Bids quoted without clauses are quoting a different job | `## Plant context` from onboarding / M365 template | No plant profile (`plant_setup.py find`: exists false) |
| 8 | Plant standard commercial terms (freight, payment, packaging, liability, tooling ownership) | Bids returned on FOB origin vs DDP — not comparable | `## Plant context` | Same |
| 9 | Approved supplier table for commodity "sintered bronze / powder-metal bushings" | No supplier can be confirmed approved; single-source cannot be assessed | `### Approved suppliers` in `## Plant context` | Same |
| 10 | Supplier contact emails | Drafts carry `[recipient: not on file]` | ERP vendor records | No vendor records |
| 11 | Plant RFQ template | Package uses a neutral structure | onboarding templates / M365 | Not on file |
| 12 | Buyer name, site, technical contact | Package section 7 and header placeholders | Buyer / plant profile | Not on file |
| 13 | Customer program for BSH-1210 | Restricted-data and program-specific clause variation cannot be checked | `## Plant context` | Not on file |

---

## 5. Figures block (internal, computed by `out/scripts/sourcing_compute.py`)

See `out/figures-block.md` for the full table (32 rows). Key rows: MRP rows 3; total 3,200 pcs; window 2026-12 to 2027-02; 800 / 1,200 / 1,200 by month; demand revision A; PO/receipt history rows 0 (none supplied); forecast rows 0; bids received 2; conforming 0; confirmed approved 0; Birch extended at 3,200 = 1,568.00 USD, first-order total incl. tooling 3,418.00 USD; Alder at its own 1,000 = 620.00 USD, at its own 3,000 = 1,650.00 USD; Alder 3,000-pc quote short of the 3,200 requirement by 200 pcs; fields_missing Alder 10, Birch 9.

---

## 6. Candidate suppliers (internal)

| Supplier | ID | Approval status | Basis | Requalification |
|---|---|---|---|---|
| Alder Sintered Parts | unlisted | **not confirmed approved** | Named on returned bid only; no approved-supplier table, no ERP vendor record on file | First article and approval per the plant's process — not known; ask |
| Birch Powder Metal | unlisted | **not confirmed approved** | Same | Same |
| Incumbent | unknown | — | No PO history supplied | — |

**Single-source status: cannot be assessed** — no approved-supplier table. Count of confirmed-approved suppliers for this commodity: 0 (by absence of the table, not by finding). The buyer should name any other candidates and the incumbent. Requalification lead time is not claimed.

---

## 7. Supplier email drafts — nothing sent

**Held, all drafts: drawing revision not verified against the ERP item master; no response due date in the package; no contact email on file; supplier not confirmed approved and no requalification decision from the buyer.**

Held: the shared conditions above.
=== SUPPLIER EMAIL — HELD — Alder Sintered Parts ===
To: [recipient: not on file]
Subject: RFQ SRC-2026-11-14-BSH-1210 — BSH-1210 flanged bushing, Rev A

Hello,

Please find attached our request for quotation SRC-2026-11-14-BSH-1210 for BSH-1210 Flanged bushing, drawing revision A (2025-06-02).

Your quotation is due by [response due date]. Please send it to [buyer name and email]; technical questions to [technical contact]. Answers given to one bidder will be shared with all bidders.

Please quote in the response format set out in section 6 of the package — unit price at each of 800, 1,200 and 3,200 pieces, tooling separately, lead time to first article and to production from a named event, MOQ, currency, validity as a date, and acceptance or exceptions for each quality requirement. Bids in another format will be returned for restatement.

Regards,
[buyer name]
=== END ===

Held: the shared conditions above.
=== SUPPLIER EMAIL — HELD — Birch Powder Metal ===
To: [recipient: not on file]
Subject: RFQ SRC-2026-11-14-BSH-1210 — BSH-1210 flanged bushing, Rev A

Hello,

Please find attached our request for quotation SRC-2026-11-14-BSH-1210 for BSH-1210 Flanged bushing, drawing revision A (2025-06-02).

Your quotation is due by [response due date]. Please send it to [buyer name and email]; technical questions to [technical contact]. Answers given to one bidder will be shared with all bidders.

Please quote in the response format set out in section 6 of the package — unit price at each of 800, 1,200 and 3,200 pieces, tooling separately, lead time to first article and to production from a named event, MOQ, currency, validity as a date, and acceptance or exceptions for each quality requirement. Bids in another format will be returned for restatement.

Regards,
[buyer name]
=== END ===

### Restatement requests (off-format bids) — drafted, not sent

Held: the shared conditions above.
=== SUPPLIER EMAIL — HELD — Alder Sintered Parts (restatement, quote Q-A-118) ===
To: [recipient: not on file]
Subject: Restatement requested — your quote Q-A-118, BSH-1210 Rev A (SRC-2026-11-14-BSH-1210)

Hello,

Thank you for quote Q-A-118. To evaluate it we need it restated in the format of RFQ SRC-2026-11-14-BSH-1210 (attached). The following were not supplied:
- Unit price at 800, at 1,200 and at 3,200 pieces
- Lead time to first article, from a named event, and production lead time separately
- Tooling: a one-time price, or a written statement that no tooling charge applies (your quote says "Tooling: existing")
- Tooling ownership
- Price validity as a date (your quote says "valid 30 days" without a start date)
- Acceptance of the certificate-of-conformance-per-lot requirement and the other quality requirements in section 4
- Payment terms

Your quote lists an exception of hardness 25-45 HRF; the drawing requires 25-40 HRF. Please confirm whether you can quote to 25-40 HRF as drawn, and keep any exception listed explicitly.

Please reply by [new date].

Regards,
[buyer name]
=== END ===

Held: the shared conditions above.
=== SUPPLIER EMAIL — HELD — Birch Powder Metal (restatement, ref BPM-77) ===
To: [recipient: not on file]
Subject: Restatement requested — your ref BPM-77, BSH-1210 (SRC-2026-11-14-BSH-1210)

Hello,

Thank you for your quotation BPM-77. To evaluate it we need it restated in the format of RFQ SRC-2026-11-14-BSH-1210 (attached). The following were not supplied:
- The drawing revision you quoted against (we require Revision A, 2025-06-02)
- Unit price at 800 and at 1,200 pieces
- Lead time to first article and production lead time, each from a named event (your quote says "6-7 weeks")
- Tooling ownership
- Minimum order quantity
- Price validity as a date
- Acceptance of the certificate-of-conformance-per-lot requirement and the other quality requirements in section 4

Please reply by [new date].

Regards,
[buyer name]
=== END ===

**Outbound check on every email block (read alone):** each is addressed to one supplier; no other supplier's name; no price from another bid or PO history; no count of bids; no target price; no rate. Each restatement quotes only that supplier's own bid back to them. Passes.

---

## 8. Response tracker

Not saved: your Open work page couldn't be written (no artifact tools in this session). Paste this table back next time and I'll pick up from it.

### SRC-2026-11-14-BSH-1210 — BSH-1210 Rev A flanged bushing (site not stated)
Trigger: direct | Breaks: 800, 1,200, 3,200 each (proposed) | Due: not set | Status: open

| Supplier | Approval | Drafted | Sent (per buyer) | Due | Response | Chased |
|---|---|---|---|---|---|---|
| Alder Sintered Parts | not confirmed approved | 2026-11-14 (RFQ + restatement, HELD) | not recorded | not set | bid Q-A-118 (undated), out/sourcing/SRC-2026-11-14-BSH-1210/alder-sintered-parts.bid.txt | - |
| Birch Powder Metal | not confirmed approved | 2026-11-14 (RFQ + restatement, HELD) | not recorded | not set | bid BPM-77 (undated), out/sourcing/SRC-2026-11-14-BSH-1210/birch-powder-metal.bid.txt | - |

Both bids arrived before this package existed, against a request not on file; they responded to something other than this package's format. Days past due: not computable (no due date). Event stays open.

---

## 9. Bid records (saved; summary)

| Supplier | Source file | Breaks as quoted | `fields_missing` |
|---|---|---|---|
| Alder Sintered Parts | bid_supplier_A.txt | 1,000 pcs 0.62 USD/ea; 3,000 pcs 0.55 USD/ea; MOQ 1,000; tooling "existing"; 4 weeks ARO; FOB origin; valid 30 days; exception hardness 25-45 HRF | unit price at 800 / 1,200 / 3,200; FA lead time from named event; FA/production split; tooling price or no-charge statement; tooling ownership; validity as date; quality clause acceptance; payment terms (10) |
| Birch Powder Metal | bid_supplier_B.txt | 0.49 USD at 3,200 pcs; tooling 1,850 USD one time; 6-7 weeks; DDP Dayton; net 45; revision not stated | drawing revision; unit price at 800 / 1,200; FA lead time from named event; production lead time from named event; tooling ownership; MOQ; validity; quality clause acceptance (9) |

Both: `conformance: off_format`, `approval_status: not_confirmed_approved`, `quality_clause_acceptance: not_stated`, `received_at: null` (nothing dates either bid), `restatement_requested: true`.

---

## 10. Comparison and recommendation (full page: `out/sourcing-output/bid-comparison.html`)

**Provisional recommendation: pursue Alder Sintered Parts, conditional — neither bid is ready for buyer review.** Alder quoted Rev A, existing tooling, 4 weeks ARO and the lower first-order outlay at its own quantities (1,650.00 USD for 3,000 pcs vs Birch 3,418.00 USD for 3,200 pcs including 1,850.00 USD tooling) — but those are different quantities and different freight bases (FOB origin vs DDP), so they are **not ranked against each other**. Against Alder: a hardness exception (25-45 HRF vs drawing 25-40 HRF) that engineering must accept or reject; MOQ 1,000 is above the December need of 800; its 3,000-pc quote is 200 pcs short of the 3,200 requirement. Against Birch: **revision not stated** (a bid of unknown revision cannot be evaluated), 6-7 weeks with no start event (illustratively 2026-12-26 to 2027-01-02 if counted from today, which may miss the December requirement), only one break priced.

Open before any award (both bids): revision gate cleared; restated bids at 800 / 1,200 / 3,200; quality clause acceptance; supplier approval/requalification; first article date set; one freight basis.

**Next step: pursue Alder Sintered Parts, look into the alternatives, or ask both suppliers to restate?** This is a recommendation only; nothing is selected or awarded, and no selection record is written until the buyer states a decision and a name.

---

## 11. Questions recorded for the buyer (not asked live in this run)

1. Document control: is BSH-1210 Rev A (2025-06-02) the current released revision on the ERP item master?
2. Confirm the quantity breaks 800 / 1,200 / 3,200, or give the ones to use.
3. What response due date, and what first article date, should the package state?
4. Which freight basis / Incoterm and delivery point, payment terms, packaging, liability and tooling-ownership position should every bid assume?
5. What is the plant's current quality clause list for this part (and does it vary by customer program)?
6. Is either supplier on the plant's approved list for sintered bronze bushings, and who else should be invited (incumbent included)?
7. Contact email for each supplier; buyer and technical-contact names for the package.
8. Engineering: is the Alder hardness exception (25-45 HRF against 25-40 HRF) acceptable?
9. Is there purchase-order history or a forecast/EAU for BSH-1210 to add to the demand picture?

No Word copy this session: no Word writer available (python-docx not installed; not installed per the rules). No Excel copy: openpyxl not installed. The Supply Chain command-center page is offered at `out/supply-chain-command-center.html`; nothing was published or written to any system.
