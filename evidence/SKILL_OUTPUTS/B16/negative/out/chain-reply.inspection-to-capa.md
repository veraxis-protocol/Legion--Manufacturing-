# Inspection to CAPA (Chain 2) - MB-1880 main bore, WO-8102 / L-0412

*This file is the chain's reply, captured in full. SYNTHETIC test data. No Word copy this session: no Word writer available (python-docx / openpyxl not installed; not installed per rules).*

**Paused at Gate 1, after step 2. The NCR is a draft and is BLOCKED: the requirement could not be located. A quality owner confirms four things before step 4 - the finding, the cited requirement, the suspect scope, and the containment plan. Steps 4 to 7 (timeline, candidate causes, 8D, customer pack) did not run.** Fixing the citation alone does not unblock the chain; the owner's confirmation does.

Nothing was sent to anyone. Northwind Robotics was not contacted, per your instruction and the chain's own rule.

---

## Freshness and inputs (stated first)

- You pointed at `inputs/quality`. **That folder does not exist.** The two files used are directly in `C:/LMFG/runs/B16-negative/work/inputs`: `finding.txt` and `inspection_measurements.csv`. Please confirm these are the intended inputs.
- `inspection_measurements.csv` covers **2026-11-09T07:10-05:00 to 2026-11-11T07:05-05:00**. It **ends before the final inspection at 10:05 on 2026-11-11**, so the three final-inspection values are **not** in the export; they come only from the inspector's note.
- `finding.txt` carries a **zone-naive** time ("2026-11-11 10:05"). The export uses -05:00. No plant profile is on file, so the finding's zone is not assumed.
- No plant profile, no rates, no open-work page (`plant_setup.py find`: profile, rates and work files do not exist; artifact tools not used in this run). The plant's NCR and 8D templates are **not on file**: a neutral NCR structure is used and flagged.
- No ERP, M365, CMMS or quality library in this run. Shipments, inventory and history are therefore from the inspector's text only, **unverified**.

---

## NCR (DRAFT - BLOCKED) - neutral structure, controlled template not on file

| Field | Value |
|---|---|
| NCR ref | **not assigned** (placeholder DRAFT-MB-1880-WO-8102-L-0412) |
| Site | **not given** |
| Part / rev | MB-1880 rev B (revision as stated by inspector) |
| Production WO / lot | WO-8102 / L-0412 |
| Made on | VMC-03, 2nd shift, 2026-11-10 (per finding) |
| Found at | Final inspection |
| Found by / when | J. Ortiz, 2026-11-11 10:05 (zone not stated) |
| Gage | **not recorded**; calibration status unknown |
| Disposition | pending |
| Approval state | draft (approved by: not given) |

**1. What was found.** Main bore diameter measured **22.034, 22.031, 22.029 mm** on **3 of 5** sampled parts. The inspector believes this is oversize. No values are recorded for the other 2 sampled parts.

**2. Against which requirement - NOT LOCATABLE. This NCR is blocking.**
> I could not locate a requirement for the MB-1880 main bore. I searched the inputs folder (`finding.txt`, `inspection_measurements.csv`); the requested `inputs/quality` folder does not exist. No MB-1880 drawing at rev B or any other revision, no internal spec, no standard clause and no Northwind Robotics PO flow-down was available, and no document library or ERP was reachable. The finding itself says the drawing was not at the bench and the requirement had not been looked up. **No nominal or tolerance has been assumed.** Whether 22.029-22.034 mm is nonconforming is therefore not established. This NCR is blocked until someone supplies the drawing (at the revision L-0412 was built to) with the locator, characteristic and stated value.

**3. How many parts.** **At least 300** (lot L-0412, WO-8102). Assumption: if a cause exists it acted on the run, not single parts - all 300 were made on VMC-03 with tool T7-0031 and no tool change recorded, and only 5 were sampled. It is a floor: T7-0031 also ran **L-0409, L-0410, L-0411 (WO-8099, WO-8100, WO-8101)** with no tool change recorded between 2026-11-09 07:10 and 2026-11-11 07:05. Whether those lots are affected cannot be judged without the requirement, and their quantities and locations are not in the inputs.

**4. Where they are - containment plan** (customer side first; quantities as reported in the finding, **none verified**; owners blank for assignment)

| Location | Suspect qty | Action | Urgency | Owner | Source |
|---|---|---|---|---|---|
| Installed at customer (Northwind Robotics) | **not checked** | Ask whether any PS-5521 parts were installed - only once nonconformance is confirmed and a person releases the notification | immediate | | not visible in our records |
| At customer (Northwind Robotics) | **not checked** | Confirm whether PS-5521 has been delivered | immediate | | finding.txt l.6; ERP unavailable |
| In transit (Northwind Robotics) | **not verified** - finding reports 30 shipped 2026-11-11 08:00 on PS-5521; delivered vs in transit unknown | Check with shipping/carrier; intercept if still in transit | immediate | | finding.txt l.6 |
| WIP at machine (VMC-03 queue) | **not verified** - finding reports 120 | Hold at VMC-03, stop next operation, tag | immediate | | finding.txt l.5 |
| Finished goods (FG-2 rack 14) | **not verified** - finding reports 150 | Quarantine, tag, block from picking | same_day | | finding.txt l.5 |

Reported quantities 120 + 150 + 30 = 300, reconciling to the lot size (figures block). Lots L-0409 to L-0411: **not checked** at any location.

---

## Step 3 - History search (run at write time)

**No searchable history available.** No quality document library, prior NCR or CAPA was reachable; only the inputs folder was enumerated (2 files, neither a prior NCR or CAPA). Same part, same defect, same process (VMC-03 / T7 tool), same supplier: none searchable. `recurrence: no_searchable_history`, `prior_ncrs_found: 0`. **This is not a first occurrence**, and whether any earlier fix held cannot be judged.

---

## Escape notification - CONDITIONAL DRAFT, not sent, not to be sent

**Conditional on two checks:** (a) the main-bore requirement confirms these values nonconform, and (b) PS-5521 is confirmed delivered or in Northwind Robotics' hands. **Contractual notification window: unknown, not guessed** - where are Northwind Robotics' quality terms recorded? `notification_deadline: null`, `escape_detected_at: null`.

> To: Northwind Robotics, Supplier Quality *(contact to be filled in)*
> Subject: Potential nonconformance - MB-1880 rev B, packing slip PS-5521
>
> We are reviewing a potential nonconformance on MB-1880 rev B main bore diameter, lot L-0412. 30 pieces from this lot were shipped to you on 2026-11-11 on packing slip PS-5521. Measured bore values on sampled parts were 22.029 to 22.034 mm against [requirement - drawing, locator and stated value to be inserted once confirmed].
>
> Please quarantine the PS-5521 receipt and tell us whether any of these parts have been installed or shipped onward.
>
> Our remaining stock of this lot is on hold. We will update you by [date/time to be set by quality owner] with the results of our review. Reference: [NCR number to be assigned].

The release of this draft is a step a person performs; nothing was sent.

---

## Steps 4-7 - not run (behind Gate 1)

- **Step 4 timeline / clocks** - not run. Noted for later: finding time is zone-naive, export is -05:00, and no plant clock/skew record exists, so alignment is currently unverifiable; the export also ends before the final inspection.
- **Step 5 ranked candidate causes** - not run. No SPC limits, run rules or clustering computed; no causal claim is made.
- **Step 6 8D** - **blocked** by both conditions in `contracts/ncr.md`: `requirement_cited` null with `requirement_not_locatable` true, and `approval_state` draft. No D1-D8 content drafted.
- **Step 7 customer pack / redaction diff (Gate 2)** - **blocked**; no pack and no diff exist. No removal requests were made, so the pending redaction log has no entries. Nothing goes to the customer.
- **Supplier-caused flag** - not raised (no investigation; no material evidence in inputs).

---

## Structured NCR (record for root-cause-capa) - saved, not pasted

Saved: `C:/LMFG/runs/B16-negative/work/out/ncr-record.MB-1880-WO-8102-L-0412.yaml`

| Field | Value |
|---|---|
| ncr_ref | null (not assigned) |
| requirement_cited / requirement_not_locatable | null / true |
| qty_found / uom | 3 / each |
| qty_suspect / qty_suspect_is_minimum | 300 / true |
| scope_basis | lot |
| recurrence / prior_ncrs_found | no_searchable_history / 0 |
| escape_occurred / escape_possible | false / true |
| notification_deadline | null (window unknown) |
| approval_state | draft |

## Register row - not stored

Saved locally: `C:/LMFG/runs/B16-negative/work/out/register-row.MB-1880-WO-8102-L-0412.yaml` (key would be `<site>_<ncr_ref>`; both not given). status `blocked`, approval_state `draft`, recurrence `no_searchable_history`, previous_fix_held null, 8D fields null.

**The Quality Register was not updated: the artifact tools are not permitted in this run, and the site and NCR number are not given.** The Quality page for this NCR only is at `C:/LMFG/runs/B16-negative/work/out/quality-register-fallback.html`.

---

## Questions for the quality owner (recorded, not asked)

1. Where is the MB-1880 drawing at the revision L-0412 was built to (rev B per inspector)? Need document, locator, characteristic and stated value for the main bore.
2. Who is the quality owner confirming Gate 1, and what name should be recorded as approving it?
3. What NCR number and site should this carry?
4. What timezone is the inspector's "2026-11-11 10:05"? Which gage measured the bore, and is it in calibration?
5. Has PS-5521 (30 pcs) been delivered to Northwind Robotics? What is their contractual notification window, and where are their terms recorded?
6. How many parts from L-0409, L-0410 and L-0411 (same tool T7-0031) exist, and where are they? Did any ship?
7. Where is the plant's quality document library (prior NCRs/CAPAs), and the controlled NCR and 8D templates?
8. The request named `inputs/quality`, which does not exist - are `inputs/finding.txt` and `inputs/inspection_measurements.csv` the intended files?

---

## Evidence appendix - figures block (computed by `work/scripts/figures.py`; full JSON in `out/figures-block.json`)

| Figure | Value | Computed from | Filter or query |
|---|---|---|---|
| Bore values in finding (mm) | 22.034, 22.031, 22.029 | finding.txt | regex 22\.\d{3} |
| Parts with bore value given / sampled | 3 of 5 | finding.txt | 'N of M sampled' |
| Lot size L-0412 | 300 | finding.txt | 'Lot size N' |
| Reported at VMC-03 queue | 120 | finding.txt | 'N still at VMC-03 queue' |
| Reported in FG-2 rack 14 | 150 | finding.txt | 'N in finished goods' |
| Reported shipped to Northwind Robotics (PS-5521) | 30 | finding.txt | 'N already shipped' |
| Sum of reported locations / reconciles | 300 / True | computed | wip+fg+shipped == lot |
| Inspection export rows | 11 | inspection_measurements.csv | all data rows |
| Export rows for L-0412 | 3 (part_seq 1, 90, 180: 22.022, 22.029, 22.034) | inspection_measurements.csv | lot == 'L-0412' |
| Finding values also present as export values | 22.029, 22.034 | computed | value match only - NOT a part-level join (finding has no part id) |
| Export coverage window | 2026-11-09T07:10-05:00 to 2026-11-11T07:05-05:00 | inspection_measurements.csv | min/max timestamp |
| Lots / WOs on tool T7-0031 | L-0409..L-0412 / WO-8099..WO-8102 | inspection_measurements.csv | tool_id == 'T7-0031' |
| Tool changes recorded | 2026-11-09 07:10 (T7-0031, L-0409); 2026-11-11 07:05 (T7-0032, L-0413) | inspection_measurements.csv | tool_change_since_last == 'yes' |
| Prior NCR / CAPA documents found | 0 - no library available | work/inputs | folder enumerated |
| Requirement documents found | 0 - not found | work/inputs | folder enumerated |

SPC rows (centreline, UCL, LCL, basis, run rule): **not computed - step 4/5 did not run because the chain is paused at Gate 1.**

Sources and coverage: `finding.txt` (inspector note, naive time); `inspection_measurements.csv` (export, -05:00, ends 2026-11-11 07:05). Maintenance history: none supplied (no CMMS export). Sensor history: none supplied.
