# NONCONFORMANCE REPORT — DRAFT (not approved)

> SYNTHETIC test data, fictitious plant. Written by `ncr-writeup` as the input `root-cause-capa` requires (no NCR existed; only the inspector's finding).
> **Status: DRAFT, awaiting approval (Gate 1).** A quality owner confirms four things before the 8D can be drafted: the finding, the cited requirement, the suspect scope and the containment plan.
> **Template:** the plant's controlled NCR template is not on file (no plant profile found by `plant_setup.py find`; `exists: false`). Neutral NCR structure used; flag this as *template not on file*.
> No Word copy this session: no Word writer available (python-docx not installed). Saved as Markdown only because this run requires every work product as a file.

## 0. Urgent before anything else

- **Escape: 30 suspect parts were shipped to Northwind Robotics on 2026-11-11 08:00 (packing slip PS-5521).** The customer notification draft is in section 7. It has not been sent; a person sends it.
- **Contractual notification window: unknown.** No customer terms are in the inputs, so no deadline is computed. Where are Northwind Robotics's notification terms recorded?
- The finding is dated 2026-11-11; this NCR is written 2026-11-14 17:09 -05:00. Roughly three days have already elapsed against whatever window applies.

## 1. Identification

| Field | Value | Source |
|---|---|---|
| NCR reference | **not assigned** — the plant's NCR number is needed | — |
| Site | **not given** — the finding does not name the site | — |
| Part / revision | MB-1880 rev B | finding.txt |
| Production work order | WO-8102 | finding.txt; inspection_measurements.csv (L-0412 rows) |
| Lot | L-0412 (production lot; lot size 300) | finding.txt |
| Operation found at | Final inspection | finding.txt |
| Machine / shift made | VMC-03, 2nd shift, 2026-11-10 | finding.txt; inspection CSV |
| Found by | J. Ortiz, final inspection | finding.txt |
| Found at | 2026-11-11 10:05 — **zone not stated in the source (naive timestamp); unresolved** | finding.txt |
| Disposition | pending | — |

## 2. Requirement violated

| | |
|---|---|
| Source | Drawing |
| Document | MB-1880 drawing revision B, sheet 2 (notes page) — `MB-1880_drawing_revB_notes.md` |
| Locator | Note 4, Bore A |
| Characteristic | Diameter |
| Stated value | 22.000 +0.021 / -0.000 mm (22.000 to 22.021 mm), Ra 1.6 |
| Revision | Part built and found against rev B (finding states rev B; drawing notes are rev B). No other revision in the inputs. |

## 3. Condition found

Main bore (Bore A) diameter measured **22.034, 22.031 and 22.029 mm** on 3 of 5 sampled parts, against a 22.021 mm maximum: **0.013, 0.010 and 0.008 mm over the upper limit**. Gage: **not recorded** in the finding; calibration status cannot be checked.

Measured, not subjective (`is_subjective: false`). `qty_found`: 3 nonconforming of 5 sampled.

Separately, the in-process inspection export holds three L-0412 rows, all over 22.021 mm: seq 1 = 22.022, seq 90 = 22.029, seq 180 = 22.034. Two of these values match finding values; whether they are the same parts is not recorded, so the two records are not merged.

## 4. Suspect quantity and reasoning

**Suspect: at least 300 parts (all of lot L-0412 / WO-8102). `qty_suspect_is_minimum: true`, scope basis: production window.**

Reasoning: the bore grew steadily across four consecutive lots on one boring insert (T7-0031) with no tool change from 2026-11-09 07:10 until the insert was replaced at 2026-11-11 06:40 (computed trend: 10 consecutive rising points). The first L-0412 part measured (seq 1, 15:10) was already 22.022, so the whole of L-0412 is suspect, not just the three found. The scope is a floor because **lot L-0411 (WO-8101) is not ruled out**: its last measured part (seq 70, 11:05 on 2026-11-10) was 22.019, 0.002 mm under the limit and still rising, and any L-0411 parts made after seq 70 were not measured. The L-0411 lot size is not in the inputs, so those parts cannot be counted. Lots L-0409 and L-0410 measured in spec on their samples. Traceability within the inputs is complete for L-0412 (lot, WO, machine, insert all on the rows); it is incomplete for the L-0411 tail.

## 5. Containment plan (ordered by urgency; owners left blank for assignment)

No inventory export or ERP shipment record is available this session. Every quantity below is **as reported in finding.txt and not yet verified** against inventory or shipping records.

| # | Location | Suspect qty | Action | Urgency | Owner |
|---|---|---|---|---|---|
| 1 | Installed at customer (Northwind Robotics) | **not checked** | Ask Northwind Robotics whether any of the 30 have been installed or shipped on | immediate | |
| 2 | At customer (Northwind Robotics) | 30 reported shipped 2026-11-11 08:00, PS-5521 — delivery not confirmed | Notify Northwind Robotics (draft, section 7); request quarantine of the PS-5521 receipt | immediate | |
| 3 | In transit | **not checked** — the same 30 may still be with the carrier if not delivered | Confirm PS-5521 delivery status with shipping; intercept if still in transit | immediate | |
| 4 | WIP at machine (VMC-03 queue) | 120 reported, not verified | Hold at VMC-03, tag with NCR reference; stop any further operation (anodize) on them | immediate | |
| 5 | Finished goods (FG-2 rack 14) | 150 reported, not verified | Move to quarantine, tag with NCR reference | same day | |
| 6 | L-0411 / WO-8101 (any parts after seq 70) | **not checked** — quantity and location unknown | Locate and hold L-0411; 100% bore check of parts after seq 70 | same day | |

Note: drawing note 5 calls Type II anodize after machining with the bore masked; parts held before anodize avoid adding process cost to suspect parts.

## 6. Recurrence (searched at writing)

Searched `prior_ncrs.csv` (the only history in the inputs) by part, defect, process and supplier.

- **NCR-0219, 2026-04-14, MB-1880, bore oversize 22.026** — cause recorded as boring insert wear beyond 900 parts; CAPA-071: insert change every 600 parts; effectiveness **not verified**.
- NCR-0244, 2026-08-02, MB-1500, slot width undersize, cause "wrong offset after tool change" — different part and defect; possibly the same process class (offset handling at tool change), but the file has no machine column, so a link to VMC-03 cannot be confirmed. Listed as unverified-related, not counted.

**Recurrence: `recurrence_prior_capa_failed`.** The same defect on the same part has recurred after CAPA-071, whose effectiveness was never verified. Prior NCRs found: 1. Whether CAPA-071 failed because the 600-part interval is wrong or because it was not followed cannot be settled from the inputs: insert T7-0031 had cut **at least 211** parts when the first oversize L-0412 part was made and **at least 510** by the end of L-0412; the true count depends on the L-0409 to L-0411 lot sizes, which are not in the inputs. The insert's history before 2026-11-09 07:10 is also not in the inputs.

## 7. Customer escape notification — DRAFT, not sent

> **Contractual clock: unknown — no notification window found in the inputs. Do not assume one; confirm Northwind Robotics's terms.**
> Conditional elements: delivery of PS-5521 is not yet confirmed.

To: Northwind Robotics, quality contact (to be filled)
Subject: Nonconformance notification — MB-1880 rev B, packing slip PS-5521

We have found a nonconformance on part MB-1880 revision B shipped to you on 2026-11-11 under packing slip PS-5521 (30 parts).

Bore A diameter, specified on drawing MB-1880 rev B note 4 as 22.000 +0.021/-0.000 mm, measured 22.029 to 22.034 mm on sampled parts from the same production lot. All 30 parts on PS-5521 should be treated as suspect.

We ask you to: quarantine the PS-5521 receipt; confirm whether any of the 30 parts have been installed or shipped on; and tell us how you would like them returned or sorted.

On our side, the remaining parts of the lot are being held, the machining insert involved has been replaced, and a root-cause investigation is under way. We will update you by [date to be set by the quality owner] with our containment status and the corrective action plan.

Reference: NCR [number to be assigned].

[Name, title — to be filled by the sender]

## 8. Approval

| approval_state | approved_by | approved_at |
|---|---|---|
| draft | — (ask: who should be recorded as approving this NCR?) | — |

**Update, same run:** approved as drafted by "Test Quality Owner (LEGION WO-LMFG-004 test operator)". NCR number DRAFT-WO-8102-L-0412; site "EPW1 (test)". Recorded 2026-11-14T17:13-05:00, the time this run received the approval. Gate 1 is passed and the 8D is drafted in `8D-DRAFT-WO-8102-L-0412.md`.
