# NONCONFORMANCE REPORT (DRAFT, awaiting quality owner approval)

> **Template not on file.** No plant profile or controlled NCR template was available this run (no `## Plant context`, no plant setup page reachable), so this uses a neutral NCR structure covering the four required questions. Re-cast into the plant's or the customer's controlled template before filing.
> **NCR number not assigned.** `DRAFT-WO-8102-L-0412` is a placeholder for the plant's NCR number. **Site not on file.**
> **Word copy:** No Word copy this session: no Word writer available (python-docx not installed; nothing was installed). This Markdown file holds the same text as the reply.

**Disposition pending: YES.** No disposition (use-as-is, rework, scrap, return) has been decided. That is decided by the MRB / quality owner, not by this report.

---

## 1. Identification

| Field | Value | Source |
|---|---|---|
| NCR reference | DRAFT-WO-8102-L-0412 (placeholder, number to be assigned) | — |
| Site | not on file | — |
| Part / revision | MB-1880, rev B | finding.txt |
| Production work order | WO-8102 | finding.txt |
| Lot | L-0412 | finding.txt |
| Operation where found | Final inspection | finding.txt |
| Made on | VMC-03, 2nd shift, 2026-11-10 | finding.txt |
| Found by | J. Ortiz, inspector (final inspection) | finding.txt |
| Found at | 2026-11-11 10:05, **time zone unresolved** (no plant clock declaration on file) | finding.txt |

## 2. Requirement violated

| Element | Value |
|---|---|
| Source | Drawing |
| Document | MB-1880 drawing, revision B, sheet 2 (notes page) — `inputs/MB-1880_drawing_revB_notes.md` |
| Locator | Sheet 2, note 4 |
| Characteristic | Bore A diameter |
| Stated value | dia 22.000 +0.021 / -0.000 (limits 22.000 to 22.021); Ra 1.6 also called on the same note (not measured in this finding) |
| Revision built to | Rev B, per the finding. Only the rev B notes page was supplied; no other revision was in the inputs, so no revision conflict could be checked |

Points for the quality owner to confirm (not blocking): (a) the finding says "main bore", the drawing note says "Bore A"; the inspector cited note 4, so they are taken as the same feature; (b) the notes page as supplied states no unit for note 4; millimetres is taken from the finding's "mm".

## 3. Condition found

Bore A diameter oversize on 3 of 5 sampled parts from lot L-0412. Measured 22.034, 22.031 and 22.029 mm against an upper limit of 22.021 mm, i.e. 0.013, 0.010 and 0.008 mm over.

| Characteristic | Measured (mm) | Nominal | Tolerance | Over upper limit (mm) | Gage | Source |
|---|---|---|---|---|---|---|
| Bore A dia | 22.034 | 22.000 | +0.021/-0.000 | 0.013 | **not recorded** | finding.txt |
| Bore A dia | 22.031 | 22.000 | +0.021/-0.000 | 0.010 | **not recorded** | finding.txt |
| Bore A dia | 22.029 | 22.000 | +0.021/-0.000 | 0.008 | **not recorded** | finding.txt |

- Quantity found nonconforming: **3** (each), of 5 sampled.
- The readings of the 2 conforming sampled parts were not recorded in the finding.
- Gage and its calibration status are not recorded; calibration could not be checked. A lapsed gage would be a finding of its own.
- Measured, not subjective.

## 4. Affected quantity

**Suspect: at least 300 each** (the whole of lot L-0412), with other MB-1880 lots cut on VMC-03 not yet ruled out.

Reasoning: all 300 parts of L-0412 were machined on one machine (VMC-03) on one shift (2nd shift, 2026-11-10). 3 of the 5 sampled parts were over the limit, and all three readings sit 0.008 to 0.013 mm above it, which looks like a systematic shift in the bore size rather than a one-off part. So the whole lot is suspect until each bore is measured; the 2 passing samples do not clear the other 295 unsampled parts.

Why it is a floor and not a total: the earlier case of this defect (NCR-0219) was attributed to boring insert wear, which is a drifting, cumulative mechanism that is not bounded by a lot. Parts cut on VMC-03 with the same insert before or after L-0412 (other lots, other work orders) could be affected. The inputs contain no insert-change record, no VMC-03 production record and no inventory export, so those parts cannot be counted or excluded. Traceability within the lot is complete (the three reported locations add up to the lot size of 300); traceability to the tool is not.

## 5. Where the parts are, and containment (ordered by urgency; owners blank for assignment)

Location quantities come from the inspector's finding, **not** from an inventory tab, ERP or shipment record (none was available). Each is therefore reported but not yet verified.

| # | Location | Suspect qty | Action | Urgency | Owner |
|---|---|---|---|---|---|
| 1 | Installed at customer (Northwind Robotics) | **not checked** | Ask Northwind Robotics whether any of the 30 parts on PS-5521 have been installed or shipped on | immediate | |
| 2 | At customer (Northwind Robotics) | **not checked** (delivery of PS-5521 not confirmed) | Confirm whether PS-5521 has been delivered. If delivered: notify and ask Northwind to quarantine the PS-5521 receipt | immediate | |
| 3 | In transit (PS-5521 to Northwind Robotics) | 30 reported shipped 2026-11-11 08:00, **not verified** | Check with shipping / the carrier; intercept PS-5521 if still in transit | immediate | |
| 4 | WIP at machine (VMC-03 queue) | 120 reported, **not verified** | Hold at VMC-03, tag with this NCR, stop the next operation (anodize, per drawing note 5). Do not run further MB-1880 bores on VMC-03 until the bore size is verified on the first piece | immediate | |
| 5 | Finished goods (FG-2 rack 14) | 150 reported, **not verified** | Move to quarantine, tag with this NCR. Also check FG for any other MB-1880 lot cut on VMC-03 (scope is a floor) | same_day | |

The 30 shipped parts are in exactly one of rows 1 to 3; until delivery is known they are carried under in transit. Reported total 120 + 150 + 30 = 300 = lot size.

## 6. Has this happened before

**Yes: recurrence; the previous fix did not hold.**

- **NCR-0219, 2026-04-14, same part MB-1880, same defect** (bore oversize, 22.026). Cause recorded: boring insert wear beyond 900 parts. Corrective action CAPA-071: change the insert every 600 parts. CAPA effectiveness: **"not verified"**. The same defect has now recurred on the same part 211 days later, so CAPA-071 did not prevent it. Whether CAPA-071 was not followed, was not enough, or whether this event has a different cause is not established; that is for root-cause investigation.
- NCR-0244 (2026-08-02, MB-1500, slot width undersize, CAPA-080 verified 2026-09-01): different part, different defect, not counted as related.
- Searched: `inputs/prior_ncrs.csv` (2 records), by part and by defect. **Not searchable:** same machine or cell and same supplier or material lot, because the file has no machine, cell, supplier or material column. No separate CAPA library was available beyond the `capa` and `capa_effective` columns.

## 7. Customer escape

**Escape possible, not yet confirmed.** 30 suspect parts were shipped to Northwind Robotics on PS-5521 at 08:00 on 2026-11-11, about two hours before the finding. A conditional notification to Northwind Robotics is drafted (separate document). It goes only once the shipment check confirms delivery (or if the quality owner decides to notify anyway), and only after a person approves and sends it. **Contractual notification window: unknown.** No deadline is computed; where are Northwind Robotics's notification terms recorded?

Shipment check: *Confirm with shipping or the carrier whether PS-5521 (30 pcs MB-1880 rev B, lot L-0412, WO-8102, shipped 2026-11-11 08:00) has been delivered to Northwind Robotics; if not, intercept it.*

## 8. Approval

| Field | Value |
|---|---|
| Approval state | draft |
| Approved by | (not given) |
| Approved at | (not given) |

A quality owner confirms the finding, the cited requirement, the suspect scope and the containment plan before this NCR is final. Nothing has been sent to any customer, and nothing was written to the ERP or the quality system.
