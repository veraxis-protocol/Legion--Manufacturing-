# MB-1880 rev B — Oversize Bore A: Root Cause Investigation and Corrective Action Plan

**Status: INTERNAL DRAFT. Not the issued 8D.** The formal 8D and the customer pack are **blocked**: no NCR has been raised from the 2026-11-11 inspection finding, so no NCR `approval_state = approved` exists. The requirement *is* locatable (MB-1880 rev B, sheet 2, note 4), so that is not the blocker. To unblock, raise and approve the NCR via `ncr-writeup`. The investigation below runs as a draft in the meantime.

Prepared 2026-11-15 from SYNTHETIC test data in `inputs/quality/`. Every number below comes from `out/MB-1880_figures_block.csv`, which `scripts/analyze_mb1880.py` produced.

---

## 0. Summary

- **What was found:** Bore A on MB-1880 rev B measured as large as **22.034 mm** against **22.000 +0.021/−0.000** (USL 22.021). That is **13.0 µm over the upper limit**. In-process data puts **3 of 3** sampled L-0412 parts out of spec (part #1, #90, #180). Final inspection found 3 of 5 out (finding.txt).
- **Act today — escape:** 30 parts from lot L-0412 shipped to **Northwind Robotics on 2026-11-11 08:00 (PS-5521)**. That was four days ago and no customer notification is on file. Check the contractual notification clock now. It may already have passed.
- **The scope is larger than the finding:** **at least 300** (all of L-0412), **plus the tail of L-0411 / WO-8101**, whose quantity and location are not in the data (§3).
- **Leading cause (candidate, not concluded):** insert **T7-0031** stayed in the boring head through **4 lots** with **no recorded change**. Bore A grew **26.0 µm** in a monotonic trend (longest increasing run **10 points**; R² vs time **0.876**). Replacing the insert brought the next part back to **22.007** (step **−27.0 µm**). The fault sits with the T7 insert-in-service condition. The data **cannot yet separate** two growth mechanisms: insert-edge degradation (C1) and T7 offset or boring-head setting drift that the insert change reset (C2). One cheap test separates them (§5).
- **This is a recurrence:** NCR-0219 (2026-04-14) had the same part, characteristic and stated cause. **CAPA-071 (change the insert every 600 parts) was never verified effective, and it did not hold.** The SPC trend rule fired at **2026-11-10 07:20**, **7.83 h** before the first out-of-spec part. No reaction plan existed to act on it.
- **Supplier-caused flag: not raised.** No candidate points at purchased material.

---

## 1. Requirement

| Item | Value | Source |
|---|---|---|
| Document | MB-1880 drawing rev B, sheet 2 (notes page) | `MB-1880_drawing_revB_notes.md` |
| Locator | Note 4, Bore A | same |
| Characteristic | Diameter, Ra 1.6 | same |
| Stated value | Ø22.000 +0.021/−0.000 mm (22.000–22.021) | same |
| Related note | Note 5: anodize Type II black after machining, bore masked | same. The coating cannot be the cause (it is masked, and anodize would shrink a bore, not enlarge it) |

---

## 2. Problem description (D2 content)

At 2026-11-11 10:05, final inspection (inspector named in finding.txt) measured Bore A at 22.034, 22.031 and 22.029 mm on 3 of 5 sampled parts from **WO-8102 / lot L-0412**. These parts were machined on **VMC-03, 2nd shift, 2026-11-10**. The in-process inspection export agrees: L-0412 #1 = 22.022, #90 = 22.029, #180 = 22.034, all above the 22.021 USL. The out-of-spec rows came from one lot only (L-0412). The defect is a measured dimensional nonconformance, not a subjective one.

`qty_found` is 3 (final-inspection sample of 5) and 3 in-process rows. These may overlap: the export carries no part serials to tell.

---

## 3. Suspect scope and containment (D3 content — feeds the NCR)

### Scope: at least 300, plus an unquantified L-0411 tail

| Lot / WO | Reasoning | Suspect |
|---|---|---|
| **L-0412 / WO-8102** | Every sampled part is out, from part #1 (22.022, 1.0 µm over) to #180. The insert was unchanged through the whole lot. 2 of the 5 final samples were in spec, so the lot needs a 100 % sort, not blanket scrap. | **300** (whole lot) |
| **L-0411 / WO-8101** | The last measured part, #70, read 22.019, only **2.0 µm** below USL. The next measured part on the same insert is L-0412 #1 at 22.022. The drift is monotonic (trend rule fired), so L-0411 parts after #70 lie between 22.019 and 22.022 and may be over the limit. Linear extrapolation at L-0411's own wear rate puts the crossing near **part #139**. That is an estimate, not a measurement. **Lot quantity and location are not in the data.** | **unknown, so suspect from #71 to end of lot** |
| L-0410 / WO-8100 | Bounded by monotonic drift: every L-0410 part was cut before L-0411 #1 (22.017), which is in spec. | Not suspect (bounding assumption: monotonic drift) |
| L-0409 / WO-8099 | Max measured 22.012. Bounded the same way. | Not suspect |
| L-0413 / WO-8103 | New insert T7-0032. First part 22.007. | Not suspect on current data |

`qty_suspect` = **at least 300**. `qty_suspect_is_minimum` = **true**: the L-0411 tail has not been counted or located.

### Containment, by location

| Location | Qty | Checked | Action | Urgency |
|---|---|---|---|---|
| At customer: Northwind Robotics (PS-5521, shipped 2026-11-11 08:00) | 30 | Yes, per finding.txt | Notify Northwind and ask them to quarantine the PS-5521 receipt. Offer replacement or sort. **Check the contractual notification clock first. Four days have passed.** | **Immediate** |
| Installed at customer | unknown | **No** | Ask Northwind whether any of the 30 have been assembled | **Immediate** |
| In transit | 0 recorded | **No** | Confirm with shipping whether PS-5521 was delivered. Confirm no other shipment carries L-0412 or the L-0411 tail | Immediate |
| WIP at machine (VMC-03 queue) | 120 | Yes, per finding.txt | Hold-tag NCR. 100 % air-gauge or bore-gauge Bore A. Segregate >22.021 | Same day |
| Finished goods FG-2 rack 14 | 150 | Yes, per finding.txt | Move to quarantine. 100 % measure Bore A | Same day |
| **L-0411 / WO-8101 (all locations)** | unknown | **No** | Find quantity and every location, including shipments, through ERP/shipping. Hold and measure parts after #70. If any have shipped, they are a second possible escape | **Immediate** |

`escape_occurred` = true (30 at Northwind). `escape_detected_at` is no later than 2026-11-11 10:05, when the finding recorded the shipment. The customer notification is `ncr-writeup`'s to draft against the contract clock. **Run it first.**

---

## 4. Ranked candidate causal chains (D4 content)

Each link carries its own For and Against lines, with citations. Insp = `inspection_measurements.csv`, Maint = `maintenance_log.csv`, Prior = `prior_ncrs.csv`.

### Shared trunk: confirmed by the data and common to C1 and C2

> **T1. Insert T7-0031 stayed in service across 4 lots, from 2026-11-09 07:10 to 2026-11-10 21:50, with no change**
> **For:** `tool_change_since_last = no` on all 9 T7-0031 rows after the first (Insp r2–r10). Maint has no T7 event until 2026-11-11 06:40.
> **Against:** The inspection export is a sample. An unlogged reset or offset touch between samples cannot be ruled out, but tool_id never changes.
>
> **T2. Bore A grew steadily while T7-0031 stayed in, and returned to nominal when it came out**
> **For:** +26.0 µm from first to last T7-0031 point. Longest increasing run 10 points (Nelson rule 3 fired). R² vs time 0.876. After the insert change, L-0413 #1 = 22.007 (step −27.0 µm), which matches the 22.008 start on T7-0031 (Insp r1, r11; Maint r2).
> **Against:** Only one post-change point exists. One point shows a reset. It does not show sustained capability.

### C1 (tied first): insert-edge degradation on T7-0031 grew the cut diameter

`T7-0031 kept past its useful life (T1)` → **`count exceeded the CAPA-071 600-part limit`** → `edge condition changed (wear, chipping or built-up edge on 6061)` → `bore cut progressively larger` → `oversize from the end of L-0411 / start of L-0412`

| Link | For | Against |
|---|---|---|
| **Count exceeded 600 parts** | At 300 per lot, like L-0412, the insert would have cut about 1080 parts. That figure is an **assumption** (figures block). | The only computed lower bound is **390 parts** (sum of the highest sampled part_seq per lot). Lot quantities for WO-8099/8100/8101 are not in the data. **This link has no verified For evidence. It is the weak point of this chain.** |
| Edge condition changed | NCR-0219 named "boring insert wear beyond 900 parts" for the same defect (Prior r1). Built-up edge is a common failure mode in 6061. | Nobody has examined T7-0031. **Plain flank wear on a boring insert normally makes the bore *smaller*, not larger.** To produce oversize, the mechanism has to be BUE, chipping or a geometry change, and none of those is evidenced yet. |
| Bore cut larger | T2 | Same as T2 |
| L-0412 out from part #1 | L-0412 #1 = 22.022, 1.0 µm over. L-0411 #70 headroom was 2.0 µm (Insp r7–r8). | None |

- **Confirm:** Examine retained insert T7-0031 under magnification. BUE, chipping or a changed nose geometry confirms C1. A test cut with T7-0031 refitted at the **current** T7 offset that reproduces about 22.03 also confirms it.
- **Kill:** T7-0031 shows only normal flank wear and no BUE or chipping. Or T7-0031 refitted at the current offset cuts near nominal.

### C1 = C2 (tied first): T7 offset or boring-head setting drifted outward, and the insert change reset it

`T7 diameter set by a wear offset or adjustable boring head` → **`offset was incremented, or the head setting crept outward, during the run`** → `bore cut progressively larger` → `insert change at 06:40 on 11-11 reset the setting` → `size returned to 22.007`

| Link | For | Against |
|---|---|---|
| Diameter set by offset/head | Standard practice for a precision 21 µm bore. Also, the size reset exactly at the insert change (T2). | The tooling setup is not in the inputs. **Unevidenced.** |
| **Offset incremented or head crept** | Oversize growth is easier to explain this way than by flank wear (see C1 Against). | **No offset log or head-setting record is in the data. This link has nothing under For from records. It is the weak point of this chain.** |
| Insert change reset the setting | Size returned to 22.007 (Insp r11) | Also fully explained by C1 |

- **Confirm:** The VMC-03 control's offset/wear history (or an operator offset log) shows T7 diameter-wear entries in the outward direction during 2026-11-09 to 11-10. Or the boring-head dial or setting record changed at the insert change.
- **Kill:** The T7 offset history shows no change from 2026-11-09 07:10 to 2026-11-11 06:40, and the head setting was not touched at the insert change.

**Why C1 and C2 are tied:** both are reset by the same 2026-11-11 06:40 event, so the inspection data cannot separate them. The prior NCR's "insert wear" cause supports C1, but it was asserted rather than verified, and its fix failed. Ranking C1 ahead on that basis would repeat the earlier conclusion without new evidence.

### C3 (low): Coolant concentration change of 6 % to 8 % (2026-11-08 16:00) accelerated wear or BUE

`coolant change` → `changed edge behaviour or thermal state` → `faster bore growth`

| Link | For | Against |
|---|---|---|
| Coolant change | A process change on VMC-03 **15.2 h** before the first measurement (Maint r1) | **0** inspection rows exist before the change, so there is no baseline to compare against (figures block) |
| Changed edge/thermal behaviour | None in data | A higher concentration normally *reduces* BUE in aluminium. **No For evidence. Weak point.** |
| Faster growth | None | Size returned to 22.007 with a new insert and **no coolant reversal recorded** (0 later coolant events). Coolant alone cannot explain the size. At most it changes the wear rate |

- **Confirm:** On insert T7-0032 at 8 %, the bore-growth rate per part clearly exceeds the rate at 6 % concentration, from historical runs.
- **Kill:** The T7-0032 growth rate at 8 % matches the pre-2026-11-08 rate, if any history exists.

### C4 (low, effectively killed): thermal drift, shift effect, or operator practice

`2nd shift / evening thermal state or practice` → `larger bores`

| Link | For | Against |
|---|---|---|
| Shift/operator effect | 3 of 5 shift-2 samples were out of spec. 0 of 6 shift-1 samples were. | Shift and operator are **fully confounded** (shift 1 is OP-11 and shift 2 is OP-23 on every row), so they cannot be separated. The drift ran **through** shift changes without resetting (+1.0, +1.0, +3.0 µm at the three boundaries). Shift-1 values also rose (22.008 to 22.019). The out-of-spec parts fell on shift 2 because that is when the trend crossed USL. **Small numbers: 11 samples.** |
| Thermal | None | There was no overnight cool-down reset (L-0410 #60 at 22.016, then L-0411 #1 at 22.017 the next morning) |

- **Confirm:** Repeated measurements show a within-shift rise and an overnight drop on the new insert.
- **Kill:** Already largely killed by the shift-boundary continuity. A run on T7-0032 across a shift change with no step would close it.

### C5 (low): measurement error

- **For:** None.
- **Against:** In-process and final inspection agree (22.034 and 22.029 appear in both). A new insert gives 22.007 on the same process.
- **Confirm:** A GR&R or calibration check on the bore gauge fails.
- **Kill:** Re-measure 5 quarantined L-0412 parts on a second, calibrated gauge or CMM and get the same values within gauge uncertainty.

**Cheapest discriminating test:** pull the VMC-03 T7 tool-offset/wear history for 2026-11-09 07:00 to 2026-11-11 07:05 (the control's offset log or the operator log) **and** put retained insert T7-0031 under a loupe or microscope. This is about 30 minutes of work with no machine time. It separates **C1 from C2**, the tie at the top. In the same pull, take the **WO-8099/8100/8101 completed quantities** from the ERP or traveller. That settles C1's weak link (were 600 parts exceeded?), and with it whether CAPA-071 was **not followed** or was **set wrong**.

---

## 5. Pattern checks (computed)

| Check | Result |
|---|---|
| SPC drift | **Fired.** I-MR on the 10 T7-0031 points: CL 22.018, UCL 22.0257, LCL 22.0103. Trend rule (6 increasing) fired, longest run 10. 2-of-3 beyond 2σ fired. 9-on-one-side did not fire (longest 6). The limits are inflated by the drift itself, so the trend rule is the valid signal. Max point 8.3 µm above UCL. **Control limits are not spec limits:** the spec USL is 22.021. |
| Clustering, lot | L-0412 3/3 out. All other lots 0 out (L-0409 0/3, L-0410 0/2, L-0411 0/2, L-0413 0/1). This is time order on one insert, not material variation. |
| Clustering, shift / operator | 2nd shift (OP-23) 3/5. 1st shift (OP-11) 0/6. Confounded with each other and with time on the insert. Not a pattern on its own (see C4). |
| Clustering, machine | All rows are VMC-03 (3/11). No comparison machine exists, so this cannot discriminate. |
| Clustering, tool | T7-0031 3/10, T7-0032 0/1. |
| Maintenance correlation | Clocks verified (§6). The coolant change came before all data (0/11 rows before). The insert change separates 10 old-insert rows from 1 new-insert row. Size reset at the change. |
| Recurrence | NCR-0219 (2026-04-14, MB-1880, bore oversize 22.026, "insert wear beyond 900 parts"). CAPA-071 "insert change every 600 parts", effectiveness **not verified**. **recurrence_prior_capa_failed.** 1 matching prior NCR out of 2 in the file. NCR-0244 is a different part and defect. |

**Checks that could not run:** sensor/historian (spindle load, temperature), because no historian export was supplied. Material lot/heat clustering, because no ERP receipts or heat numbers were supplied (the "lot" field is the production lot). Ra 1.6, because it was not measured in the export. Gauge identity and calibration, because no gauge field exists. Cumulative insert part count, because WO quantities are absent (only a lower bound of 390). T7 offset history, because it was not supplied.

---

## 6. Corrective Action Plan (8D-structured, DRAFT)

### D1 — Proposed team (owner to edit)
Quality engineer (owner), the VMC-03 cell lead, the manufacturing/tooling engineer, the final inspector who raised the finding, maintenance (VMC-03), and the customer-quality contact for Northwind Robotics. Names to be assigned.

### D2 — Problem
See §2. Bore A on MB-1880 rev B was oversize, up to 22.034 against 22.021 max. Scope is at least 300 parts (L-0412) plus an unquantified L-0411 tail. 30 parts are at Northwind Robotics. This is a recurrence of NCR-0219.

### D3 — Interim containment
| # | Action | Due |
|---|---|---|
| 3.1 | Check the Northwind notification clock, then notify (via `ncr-writeup` escape draft). Request quarantine of the PS-5521 receipt and confirm installed status | Immediately |
| 3.2 | Hold and 100 % measure Bore A on 120 WIP (VMC-03) and 150 FG (FG-2 r14). Segregate >22.021 to MRB | Same day |
| 3.3 | Find the WO-8101 / L-0411 quantity and every location, including shipments. Hold and measure parts after #70 | Immediately |
| 3.4 | Temporary rule on VMC-03 for MB-1880: measure Bore A on the first part and every 25th part. Change the T7 insert at ≥22.015 (6 µm guard band) or at every lot start, whichever comes first, until D5 is in place | Immediately |
| 3.5 | Quarantine insert T7-0031. **Do not discard it.** It is the evidence for the discriminating test | Immediately |

### D4 — Root cause (candidate, with uncertainty kept)
**Confirmed:** the oversize comes from insert T7-0031's in-service condition. The insert stayed in through 4 lots without a change, bore size climbed steadily, and it reset on replacement.
**Open and tied:** whether the growth came from insert-edge degradation (C1) or from T7 offset/head-setting drift (C2).
**Escape point:** the SPC trend signal existed 7.83 h before the first bad part, but no in-process reaction plan acted on it, so the condition reached final inspection and one shipment.
**System cause:** CAPA-071's 600-part limit was not enforced by any mechanism, and its effectiveness was never checked.

### D5 — Corrective actions (each names the link it breaks)
| # | Action | Breaks link |
|---|---|---|
| 5.1 | Put a **tool-life counter** in the VMC-03 control for T7 on MB-1880. It must alarm and block cycle start at the limit, and reset only when an insert change is logged | Breaks **T1 / C1 link "count exceeded limit"**: the insert cannot stay in past its life |
| 5.2 | Set the insert-life limit **from data**: measure bore growth per part on T7-0032 to the 22.015 guard band, then set the life at ≤70 % of the parts to reach it. Replace the unverified "600" | Breaks **C1 link "count exceeded limit"** by making the limit fit the actual wear rate |
| 5.3 | Add an **in-process SPC reaction plan** for Bore A: an individuals chart at every 25th part, with a trend rule (6 increasing) or ≥22.015 triggering insert inspection or change before the next part | Breaks **T2 → "oversize reaches parts"**. Covers **C1 and C2 both**, which matters while they are tied |
| 5.4 | **If the test confirms C2:** lock the T7 diameter offset (wear-offset entries need a recorded reason and are capped per shift), add a head-setting witness mark, and add a setting check at each insert change | Breaks **C2 link "offset incremented / head crept"** |
| 5.5 | **If the test confirms C1 by BUE:** review insert grade and coating for 6061 (polished, sharp, uncoated or DLC) and coolant delivery to the bore | Breaks **C1 link "edge condition changed"** |

Actions 5.4 and 5.5 are conditional. Commit to them only after the discriminating test.
*Improvement, not corrective action:* a GR&R on the Bore A gauge. No link depends on it, but it supports 5.3.

### D6 — Implement and verify (placeholder: needs real-world outcome)
| Field | Entry |
|---|---|
| Action implemented (ref) | |
| Implemented by / date | |
| Verification method | |
| Verification data (runs, n, result) | |
| Cpk on Bore A after change | |
| Result accepted by / date | |

### D7 — Prevent recurrence: why CAPA-071 did not hold
1. **The control was a number on paper, not a mechanism.** CAPA-071 said "change every 600 parts", but nothing counted parts or stopped the machine, and the insert ran through 4 lot changes with `tool_change_since_last = no`. **Change:** tool-life limits on critical-feature tools are enforced in the machine control (5.1), and a lot or WO change prompts a tool-life check on the setup sheet.
2. **The CAPA was never verified, and nothing flagged that.** CAPA-071 still reads `not verified` seven months on. **Change:** a CAPA cannot close, or stay open past 60 days, without a D6 effectiveness record. Add an aged-unverified-CAPA line to the quality review.
3. **The 2026-04 root cause may itself have been wrong.** "Insert wear" was recorded without examining the insert or the offsets, and flank wear does not naturally enlarge a bore. **Change:** NCR-0219's cause is re-opened alongside this one. Dimensional root causes on bores require the offset history and a physical examination of the tool before a cause is accepted.
4. **No in-process detection for a 21 µm feature.** **Change:** every drawing characteristic with a total tolerance ≤25 µm gets an in-process SPC plan with a reaction rule at release (control plan / PFMEA update), not only final-inspection sampling.
5. **Escape path:** a lot shipped before final inspection was complete. The parts went out at 08:00 and the finding came at 10:05 on 2026-11-11. **Change:** confirm the ship-release gate requires final-inspection sign-off on the lot.

### D8 — Close and recognize (placeholder: needs human sign-off)
| Field | Entry |
|---|---|
| D6 verified effective (Y/N, ref) | |
| Customer accepted (Northwind) | |
| CAPA-071 / NCR-0219 disposition | |
| Closed by (name) | |
| Closed date | |
| Team recognized | |

---

## 7. Evidence appendix

**Timeline (single zone, UTC−05:00, as recorded in the sources):**

| Time (−05:00) | Event | Source |
|---|---|---|
| 2026-11-08 16:00 | Coolant concentration 6 % to 8 %, VMC-03 | Maint r1 |
| 2026-11-09 07:10 | T7-0031 in (tool change = yes). L-0409 #1 = 22.008 | Insp r1 |
| 2026-11-09 15:30 | L-0410 start, 22.013 | Insp r4 |
| 2026-11-10 07:20 | L-0411 #1 = 22.017. **SPC trend rule fires** | Insp r6 |
| 2026-11-10 11:05 | L-0411 #70 = 22.019 (2.0 µm headroom) | Insp r7 |
| 2026-11-10 15:10 | **L-0412 #1 = 22.022, first part out of spec** | Insp r8 |
| 2026-11-10 21:50 | L-0412 #180 = 22.034 | Insp r10 |
| 2026-11-11 06:40 | T7 insert replaced, T7-0031 to T7-0032 | Maint r2 |
| 2026-11-11 07:05 | L-0413 #1 = 22.007 on T7-0032 | Insp r11 |
| 2026-11-11 08:00 | 30 × L-0412 shipped to Northwind Robotics, PS-5521 | finding.txt |
| 2026-11-11 10:05 | Final inspection finding: 3 of 5 out | finding.txt |

**Time alignment:** No plant profile was available, so the per-source clocks and the onboarding skew self-check were not on file. All timestamps in both CSVs are zone-aware with a single offset (−05:00, 0 naive). That is consistent with US Eastern after the 2026-11-01 DST change. **Anchor event in two sources:** the insert change (Maint 06:40) falls between the last T7-0031 row and the first T7-0032 row (07:05). The ordering is consistent, with a 25-minute gap. **Residual uncertainty:** maintenance entries may be logged at entry time rather than event time, which is good to roughly ±25 min. Every correlation used here spans hours to days, so the alignment holds for these conclusions. finding.txt times are local and assumed to be −05:00.
**Shift boundary:** inferred from data, not from a plant profile. Shift 1 rows fall 07:05–12:15 and shift 2 rows 15:10–21:50. No row crosses midnight, so the cross-midnight attribution rule does not affect any result.
**Maintenance source:** export file `maintenance_log.csv`, not a live CMMS. Repairs logged after the export are not included.
**Figures block:** `out/MB-1880_figures_block.csv` (every figure, with its computation and filter).
**Absence claims:** "no T7 change between 11-09 07:10 and 11-11 06:40" comes from filter `tool_change_since_last=='yes'` on T7-0031 rows after the first (returned 0) plus the maintenance log, which has 2 VMC-03 records. "No coolant reversal" comes from `event contains 'coolant' and t > 2026-11-08T16:00`, which returned 0.
**Sources:** `inputs/quality/finding.txt`, `inspection_measurements.csv`, `maintenance_log.csv`, `prior_ncrs.csv`, `MB-1880_drawing_revB_notes.md`.

---

## 8. Supplier-caused flag
**Not raised.** No candidate implicates purchased material: the size reset on a tooling change. Material heat and receipt data were not available (no ERP in session), so the material question could not be fully assessed. Nothing in the evidence points there.

## 9. Gates and next steps
1. **Now:** run `ncr-writeup` on the finding to raise the NCR with the containment above and draft the Northwind escape notification against its contractual clock. A person sends it. Nothing was sent from this session.
2. Run the cheapest discriminating test (§4), then re-rank C1/C2.
3. Approve the NCR. The 8D and the customer pack then unblock, with the redaction diff for quality-owner approval (see `MB-1880_pending_redaction_log.md`).
