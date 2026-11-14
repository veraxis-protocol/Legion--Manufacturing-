# ncr-writeup reply (as it would be printed in the conversation)

**Summary.** Bore A on MB-1880 rev B, lot L-0412 (WO-8102) is oversize: 3 of 5 samples at 22.029 to 22.034 mm against the 22.021 mm limit on drawing MB-1880 rev B, sheet 2, note 4. Suspect: **at least 300** (the whole lot; other VMC-03 lots not ruled out). Reported locations: 120 at the VMC-03 queue, 150 in FG-2 rack 14, 30 shipped to Northwind Robotics on PS-5521 (none verified against system records). **This is a recurrence and the previous fix did not hold** (NCR-0219, same part and defect, CAPA-071 never verified). Customer escape is possible; a conditional notification to Northwind Robotics is drafted, contractual window unknown. Next: confirm PS-5521 delivery status, hold all lot L-0412 stock, and quality owner approval.

> Date check: the finding is dated 2026-11-11, but this session's date is 2026-11-14. If the request's "this morning" is right, the dates need reconciling; if the finding really is from 2026-11-11, it is 3 days old and any customer notification clock may already be running.

## Figures block (computed by work/scripts/figures.py)

| Figure | Value | Computed from | Filter or query |
|---|---|---|---|
| Upper limit, Bore A | 22.021 | drawing note 4 | 22.000 + 0.021 |
| Lower limit, Bore A | 22.000 | drawing note 4 | 22.000 - 0.000 |
| Excess over upper limit, part reading 22.034 | 0.013 | finding.txt + note 4 | 22.034 - 22.021 |
| Excess over upper limit, part reading 22.031 | 0.010 | finding.txt + note 4 | 22.031 - 22.021 |
| Excess over upper limit, part reading 22.029 | 0.008 | finding.txt + note 4 | 22.029 - 22.021 |
| Readings recorded | 3 | finding.txt | values listed after "measured" |
| Readings above upper limit | 3 | finding.txt + note 4 | measured > USL |
| Max reading | 22.034 | finding.txt | max |
| Parts failing / sampled | 3 of 5 | finding.txt | "3 of 5 sampled" |
| Fail fraction of sample | 60% | finding.txt | 3/5 |
| Lot size | 300 | finding.txt | "Lot size 300" |
| Reported at VMC-03 queue | 120 | finding.txt |  |
| Reported in FG-2 rack 14 | 150 | finding.txt |  |
| Reported shipped (PS-5521) | 30 | finding.txt |  |
| Sum of reported locations | 300 | computed | 120+150+30 |
| Sum equals lot size | True | computed | sum == lot |
| Unsampled parts in lot | 295 | computed | 300-5 |
| Prior NCR rows in prior_ncrs.csv | 2 | prior_ncrs.csv | all rows |
| Prior NCRs, same part MB-1880 | 1 (NCR-0219) | prior_ncrs.csv | part == "MB-1880" |
| Prior NCRs, same defect (bore oversize, any part) | 1 (NCR-0219) | prior_ncrs.csv | defect contains "bore" and "oversize" |
| Prior NCRs, same machine VMC-03 | not searchable (file has no machine/cell column) | prior_ncrs.csv | columns: ncr|date|part|defect|cause|capa|capa_effective |
| Prior NCRs, same supplier/material lot | not searchable (file has no supplier/material column) | prior_ncrs.csv |  |
| NCR-0219 reading over then-USL | 0.005 | prior_ncrs.csv + note 4 | 22.026 - 22.021 (assumes same requirement) |
| Days NCR-0219 to this finding | 211 | computed | 2026-11-11 - 2026-04-14 |
| Age of NCR at writing (days) | 3 | session date - finding date | 2026-11-14 - 2026-11-11 (counted by reading, not computed) |

Note: the NCR-0219 excess (0.005) assumes NCR-0219 was measured against the same note 4 requirement; prior_ncrs.csv does not record the revision.

## Register row (not stored)

The Quality Register was not updated: the artifact tools are not available in this session. The Quality page for this NCR only is saved as `out/quality-page.html` (offered page; save it where the Quality Register lives). Internal: it lists customer names and notification deadlines. Check who you share it with.

| Field | Value |
|---|---|
| record_key | not-on-file_DRAFT-WO-8102-L-0412 (site and NCR number are placeholders) |
| status | awaiting_approval |
| approval_state | draft |
| containment_summary | 5 of 5 locations addressed; quantities reported by inspector, none verified; at/installed at customer not checked |
| escape_clock | null (escape_clock_unknown: true) |
| recurrence | recurrence_prior_capa_failed |
| prior_ncr_refs | NCR-0219 |
| previous_fix_held | false |
| owner / due_date | unassigned / no due date |

Full record: `out/quality-register-row.yaml`. Structured NCR for root-cause-capa: `out/ncr-record.yaml` (key fields: requirement_not_locatable false, qty_suspect 300 with qty_suspect_is_minimum true, traceability_complete false, escape_possible true, approval_state draft).

## Questions for the user (recorded, not asked)

1. Who should I record as approving this NCR? (quality owner name)
2. Where are Northwind Robotics's contractual notification terms recorded? No deadline is computed until then.
3. Has PS-5521 been delivered to Northwind Robotics, or can it still be intercepted? Have any of the 30 been installed?
4. Which gage measured Bore A, and is its calibration current? What did the 2 conforming samples read?
5. Is the finding's "main bore" the drawing's "Bore A" (note 4), and is the unit mm (the notes page states none)?
6. What NCR number and site name should replace the placeholders, and where is the plant's controlled NCR template? (No plant setup page or profile was found.)
7. What is the plant time zone for the 10:05 finding time?
8. When was the VMC-03 boring insert last changed, how many parts had it cut at lot L-0412, and was CAPA-071's 600-part change being followed? Which other MB-1880 lots were cut on that insert?
9. Can you confirm on-hand counts at the VMC-03 queue (120) and FG-2 rack 14 (150) from inventory or the ERP?

---

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

---

# DRAFT customer notification: Northwind Robotics (CONDITIONAL, not sent)

> **Contractual clock: UNKNOWN.** Northwind Robotics's notification window was not in the inputs, so no deadline is computed and none is guessed. Ask the quality owner where Northwind's terms are recorded. Finding time: 2026-11-11 10:05 (time zone unresolved).
> **Conditional:** send only if the shipment check confirms PS-5521 was delivered (or if the quality owner decides to notify while it is in transit). Nothing goes to the customer until a person approves and sends it.
> **Word copy:** No Word copy this session: no Word writer available.

---

**To:** Northwind Robotics, quality contact (to be filled in by the sender)
**Subject:** Nonconformance notification: MB-1880 rev B, lot L-0412, packing slip PS-5521 (our ref. [NCR number])

Dear [name],

We are writing to tell you about a nonconformance affecting parts we shipped to you.

**What is affected.** Part MB-1880, revision B, lot L-0412 (our work order WO-8102): 30 pieces, shipped 2026-11-11 08:00 on packing slip PS-5521.

**What the nonconformance is.** At our final inspection on 2026-11-11, the diameter of Bore A was over its drawing limit on 3 of 5 sampled parts from this lot. Drawing MB-1880 rev B, note 4, requires 22.000 +0.021/-0.000 mm; we measured 22.034, 22.031 and 22.029 mm. We are treating the whole lot as suspect, including the 30 pieces sent to you.

**What we ask you to do.**
1. Quarantine the PS-5521 receipt and do not use these parts.
2. Tell us whether any of the 30 pieces have already been installed or shipped on, and if so, where.

**What we are doing.** [Sender: confirm these are done before sending] We have placed the rest of the lot on hold at our plant (in process and in finished goods) and are measuring the bore on every part. We are investigating the cause. We will contact you by [date and time to be committed by the sender] with the inspection results and the arrangements for the 30 pieces.

Our reference: [NCR number] (draft ref. DRAFT-WO-8102-L-0412).

Regards,
[name, title]
