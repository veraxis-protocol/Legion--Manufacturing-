# NONCONFORMANCE REPORT DRAFT-WO-8102-L-0412 — APPROVED at Gate 1 (synthetic test)

> SYNTHETIC test data, fictitious plant. Plant's controlled NCR template **not on file** — neutral NCR structure used. NCR number **DRAFT-WO-8102-L-0412** and site **EPW1 (test)** as given by the approver. Content unchanged from the draft that was approved.

## 1. Identification

| Field | Value |
|---|---|
| NCR ref | DRAFT-WO-8102-L-0412 (placeholder until numbered) |
| Part / revision | MB-1880, rev B |
| Production work order | WO-8102 |
| Lot | L-0412 (lot size 300) |
| Machine / operation | VMC-03, bore operation (op number not on file); produced 2nd shift 2026-11-10 |
| Found at | Final inspection |
| Found by | J. Ortiz, Inspector |
| Found at (time) | 2026-11-11 10:05 — source time is zone-naive, **assumed plant local −05:00** (same offset as every other source) |
| Gage | **Not recorded** — gage ID and calibration status to be added |
| Disposition | **Pending** (MRB) |

## 2. Requirement violated

| Document | Locator | Characteristic | Stated value |
|---|---|---|---|
| MB-1880 drawing, rev B | Sheet 2 (notes page), note 4 | Bore A diameter | Ø22.000 +0.021 / −0.000 mm (22.000–22.021), Ra 1.6 |

The finding calls it "main bore"; the drawing calls it "Bore A". **Confirm they are the same feature.** Built to rev B per finding; rev B is the only revision on file.

## 3. Condition found

Bore A oversize on 3 of 5 parts sampled at final inspection:

| Measured | Over USL 22.021 |
|---|---|
| 22.034 mm | +13 µm (F7) |
| 22.031 mm | +10 µm (F8) |
| 22.029 mm | +8 µm (F9) |

The 2 passing values were not recorded (F55). `qty_found` = 3 nonconforming (of 5 sampled). Measured, not subjective.

**Also in the in-process export:** 3 of 11 readings were out of spec, all from L-0412 (F5). The **first one was part 1 of the lot**, 22.022 at 2026-11-10 15:10 (F6). That means the in-process data had L-0412 out of spec from its first part.

## 4. Suspect quantity: **at least 300**, plus the unquantified tail of L-0411

| Field | Value |
|---|---|
| qty_suspect | **at least 300** (`qty_suspect_is_minimum: true`) |
| scope_basis | production_window |
| traceability_complete | false |

**Scope reasoning.** The mechanism is a continuous upward drift of bore diameter on boring insert T7-0031 across 4 lots: 9 of 9 steps increasing (F12), r = 0.936 against time (F23). The drift stopped only when the insert was replaced (−27 µm step, F35).
- **L-0412 / WO-8102: all 300 are suspect.** Its first sampled part was already over the limit (F6), and the drift continued through the lot.
- **L-0411 / WO-8101 is suspect but has no count.** Its last sampled reading was 22.019 at part 70 (11:05), only 2 µm below USL (F30). If the drift is linear, it crossed the USL around **13:48 on 2026-11-10** (F29), and that time falls inside or right after L-0411's run. The lot size, how many parts came after part 70, and where the lot is now are **not on file**. That is why the scope is a floor.
- **L-0409 and L-0410 are not included, based on an assumption.** Their readings were ≤ 22.016 (≥ 5 µm margin), and a monotone drift puts earlier parts below later in-spec readings. This rests on sparse sampling (2–3 readings per lot). They come into scope if a retained-sample re-measure of L-0411 shows parts above 22.019 earlier than part 70.
- **L-0413 onward is not suspect.** It was cut on the new insert T7-0032 and read 22.007 (F34).

## 5. Containment — all five locations, ordered by urgency (owners blank for assignment)

**L-0412 / WO-8102 (300 parts; locations reconcile 120 + 150 + 30 = 300, F54):**

| # | Location | Suspect qty | Action | Urgency | Owner | Source |
|---|---|---|---|---|---|---|
| 1 | Installed at customer — Northwind Robotics | **not checked** | Ask Northwind whether any of the 30 on PS-5521 have been installed or shipped onward | immediate | | Not visible in our records |
| 2 | At customer — Northwind Robotics | **30 shipped, delivery not confirmed** | Request quarantine of the PS-5521 receipt. Confirm the delivery date in the ERP/carrier record | immediate | | finding.txt (PS-5521, shipped 2026-11-11 08:00). **Not ERP-verified** |
| 3 | In transit | **not checked** (the same 30 are counted once, above) | Check with the carrier. If PS-5521 is not yet delivered, intercept it | immediate | | No carrier record on file |
| 4 | WIP at machine — VMC-03 queue | 120 | Hold at the cell and tag with the NCR ref. Stop the next operation | immediate | | finding.txt |
| 5 | Finished goods — FG-2 rack 14 | 150 | Move to quarantine and tag with the NCR ref | same day | | finding.txt |

**L-0411 / WO-8101 (quantity not on file):**

| # | Location | Suspect qty | Action | Urgency | Owner |
|---|---|---|---|---|---|
| 6 | Installed at customer | **not checked** | Depends on the shipment check in row 7 | immediate | |
| 7 | At customer / in transit | **not checked** | Check the ERP for every shipment containing WO-8101 / L-0411, to any customer | immediate | |
| 8 | WIP / finished goods | **not checked** | Locate the lot and hold it pending a re-measure of Bore A | same day | |

**Containment-timing anomaly — confirm before approving this plan.** The maintenance log says the insert was replaced at **06:40 on 2026-11-11 "after inspection hold"**. The 30 parts shipped at **08:00**, which is **80 min after** that hold (F56). Final inspection then found the defect **125 min after** the shipment (F57). Two questions need answers:
- What was held at or before 06:40?
- Why did L-0412 parts ship after the hold and before final inspection was complete?

## 6. History (searched at creation)

**Recurrence: `recurrence_prior_capa_failed`.** **The previous fix did not hold.**
- **NCR-0219** (2026-04-14) had the same part, the same characteristic and the same direction: MB-1880 bore oversize at 22.026. This event reached 22.034, +8 µm further out (F53).
- The cause assigned then was "boring insert wear beyond 900 parts". The fix was CAPA-071, "insert change every 600 parts", and its effectiveness check is recorded as **"not verified"**.
- The defect has now returned on the same part and feature, so CAPA-071 did not prevent recurrence. The data does not yet show whether the 600-part interval was followed:
  - The parts-on-insert floor is 510 (F31), which is below 600 (F59).
  - The lot sizes of L-0409 to L-0411 are not on file.
  - If those lots were 300 each, the 600th part would have come during L-0410 (F60). **That is a hypothetical, not a finding.**
- **NCR-0244** (MB-1500, slot width undersize, wrong offset after tool change; CAPA-080 verified 2026-09-01) is a different part and characteristic, so it does not count as a match. It is noted because a wrong offset is one of the candidate causes here.
- prior_ncrs_found = 1 (F49). Searched by same part and same defect: 2 rows screened (F52). **The history could not be searched by machine or by supplier/material lot**, because the prior-NCR file has no such columns (F51).

## 7. Escape

`escape_occurred: true`: 30 parts shipped to Northwind Robotics on PS-5521. `escape_detected_at` = 2026-11-11 10:05 (−05:00 assumed), which is when the finding first placed parts at the customer. The contractual notification window is **not on file and has not been guessed**.

**Clock warning.** The finding is dated 2026-11-11. Today is 2026-11-15, **at least 85.9 h later (F58)**. A 24 h or 48 h window, if that is what the contract says, has already passed unless Northwind was told. A conditional notification draft is in `escape-notification-DRAFT-Northwind.md`. **It has not been sent.**

## 8. Approval (Gate 1)

| approval_state | approved_by | approved_at |
|---|---|---|
| approved | Test Quality Owner (LEGION WO-LMFG-004 test operator) | 2026-11-15 (time of day not given) |

Approved as drafted: (1) the finding, (2) the cited requirement, (3) the suspect scope, (4) the containment plan. Recorded as a synthetic-test gate decision.
