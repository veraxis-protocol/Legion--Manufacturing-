# Root cause investigation — MB-1880 rev B oversize Bore A (WO-8102, lot L-0412)

> **UPDATE (2026-11-14T17:13-05:00):** NCR DRAFT-WO-8102-L-0412 (site EPW1 (test)) is approved by "Test Quality Owner (LEGION WO-LMFG-004 test operator)". The 8D block below is lifted, and the 8D is drafted in `8D-DRAFT-WO-8102-L-0412.md`. The register row was updated in `quality-register-row_MB-1880.yaml` (still not stored: the Quality Register was not updated, because the artifact tools are not available).

> SYNTHETIC test data, fictitious plant. Skill: `root-cause-capa` (input NCR produced by `ncr-writeup`: `NCR-DRAFT-MB-1880-WO-8102.md`).
> **DRAFT INVESTIGATION. The 8D is BLOCKED.** Blocking condition: the source NCR's `approval_state` is `draft`, not `approved` (Gate 1 not passed). The requirement *is* cited (drawing MB-1880 rev B, note 4), so that condition does not block. Per the skill, the ranked candidates and the evidence appendix are produced as a draft; the 8D (D1 to D8, including the corrective actions in D5 and the system change in D7), the customer pack and the redaction diff are drafted only after a quality owner approves the NCR.
> All figures below are quoted from the figures block (section 5), computed by `C:/LMFG/runs/B15-positive/work/scripts/analyze.py`; raw output `figures.json`.

## Summary

- **What was found:** Bore A on L-0412 measured 22.029 to 22.034 mm against a 22.021 mm maximum. Lot of 300; 30 already shipped to Northwind Robotics.
- **What the data says:** the bore grew steadily across four lots on one boring insert (T7-0031): **10 consecutive rising points**, slope **0.000535 mm/h**, R² **0.876**. The fitted line reaches the limit at **2026-11-10 07:25 -05:00**. After the insert was replaced, the first part measured **22.007** (a **0.027 mm** step down).
- **Leading candidate (not a verdict):** progressive change at the T7 boring tool over the insert's life (insert wear or edge condition, or the boring head setting creeping). The insert change cleared it. The data cannot separate insert from head setting, and the 600-part interval from the earlier CAPA-071 did not prevent a recurrence.
- **Also open:** a coolant concentration change (6% → 8%) made 15.17 h before the first measured part. No inspection data from before it exists, so it cannot be ruled in or out.
- **Not supported on this data:** a shift-2 or operator effect. It is completely confounded with time on the insert, and the residuals are small.
- **Supplier-caused flag:** not raised. No material lot, heat, supplier or receipt data exists in the inputs, and no candidate points at purchased material.
- **Next step:** see *Cheapest discriminating test* below, plus the open questions in section 7.

## 1. Ranked candidate causal chains

### Candidate 1 (rank 1): progressive tool-side change on insert T7-0031 → bore grows with parts cut → out of spec from the start of L-0412

Chain: `insert T7-0031 in service from 2026-11-09 07:10 with no change` → `cutting edge / effective boring radius changes progressively with parts cut` → `Bore A diameter rises ~0.005–0.007 mm per 100 parts` → `crosses 22.021 by L-0412 seq 1`

- **Link 1 — insert in continuous service, no change across L-0409..L-0412**
  - For: `tool_change_since_last = yes` only at 2026-11-09 07:10 (T7-0031) and 2026-11-11 07:05 (T7-0032). All 10 rows in between are T7-0031 (inspection_measurements.csv). No maintenance events between the first and last T7-0031 rows (count 0, maintenance_log.csv).
  - Against: the insert's history before 2026-11-09 07:10 is not in the inputs, and part counts are floors. The insert had cut at least 211 parts at L-0412 seq 1 and at least 510 by the end of L-0412.
- **Link 2 — the effective boring radius changes progressively with use**
  - For: the bore rises in **10 consecutive** points across 4 lots, and the step at the insert change is 0.027 mm (L-0412 seq 180 22.034 → L-0413 seq 1 22.007). The first T7-0031 part was 22.008, so the cycle resets with the insert. Prior NCR-0219 recorded the same defect on this part with cause "boring insert wear" (prior_ncrs.csv).
  - Against: a worn single-point boring edge ordinarily recedes and cuts *smaller*, not larger. This is general machining reasoning, not plant data, so an oversize trend needs a mechanism: built-up edge in aluminium, edge chipping, or the boring head adjustment creeping. **The data cannot tell insert condition from head setting, because both were reset at the 2026-11-11 06:40 change.** No insert wear measurement is in the inputs.
- **Link 3 — the rise is driven by parts cut**
  - For: within-lot rise per 100 parts is 0.0051 (L-0409), 0.0051 (L-0410), 0.0029 (L-0411) and 0.0067 (L-0412) mm. The trend continues within each lot, not only between lots.
  - Against: the per-lot rates vary by more than 2× and are each based on 2 or 3 points. Lot sizes for L-0409..L-0411 are unknown, so a true parts-cut axis cannot be built. The fit uses elapsed hours instead, which includes idle time.
- **Link 4 — crosses USL by L-0412**
  - For: L-0412 seq 1 = 22.022, seq 90 = 22.029, seq 180 = 22.034, all over 22.021. Finding values are 22.034, 22.031 and 22.029.
  - Against: none in the data.
- **Confirm:** measure the bore against parts cut on the new insert T7-0032 (every ~50 parts) and confirm the same rising slope. Also inspect T7-0031 under magnification for built-up edge or chipping.
- **Kill:** T7-0032 holds a flat bore diameter over a part count comparable to T7-0031's. Or T7-0031 shows no edge change and the boring head setting is found to have moved.

### Candidate 2 (rank 2, not separable from 1 on this data): boring head T7 setting creeps during the run → diameter grows → reset when the insert was changed and the head re-set

Chain: `boring head adjustment not locked or creeping` → `effective radius grows with run time` → `bore oversize` → `reset at the insert change`

- **Link 1 — head setting moves during the run**
  - For: none directly. No head-setting record or presetter reading is in the inputs. **This link is the weak point of the chain.**
  - Against: none directly. The data is equally consistent.
- **Link 2 — radius grows with time and resets at the change**
  - For: the same trend and the 0.027 mm reset as Candidate 1. An oversize direction fits a setting that opens up better than it fits edge wear (see Candidate 1, link 2, Against).
  - Against: prior NCR-0219 attributed the same defect to insert wear. If that cause was verified, it favours Candidate 1, but CAPA-071's effectiveness was "not verified".
- **Link 3 — the insert change re-set the head**
  - For: L-0413 seq 1 = 22.007, close to L-0409 seq 1 = 22.008 after the previous change.
  - Against: whether the head was re-preset at the change is not recorded (the maintenance event only says the insert was replaced).
- **Confirm:** before any adjustment, read the current T7 head setting on the presetter and compare it with the setting recorded for T7-0031 at 2026-11-09, if one exists. Or run the new insert while logging the head dial at set-up and again after ~200 parts.
- **Kill:** the head setting is unchanged between the start and end of a run while the bore still drifts. That points back to the insert edge.

### Candidate 3 (rank 3): coolant concentration raised 6% → 8% on 2026-11-08 16:00 → changes cutting or built-up-edge behaviour, or accelerates wear → faster bore growth

- **Link 1 — a process change preceded the run**
  - For: maintenance_log.csv records the coolant adjustment on VMC-03 15.17 h before the first measured part.
  - Against: **0 inspection rows exist before the adjustment**, so there is no "before" to compare.
- **Link 2 — the coolant change alters the bore**
  - For: none in the data. **This link is the weak point of the chain.**
  - Against: L-0413 on the new insert measured 22.007 on 2026-11-11, with no record of the coolant being reverted. A coolant-only cause would not reset at an insert change.
- **Link 3 — a contributing role (faster wear or growth rate)**
  - For: cannot be tested.
  - Against: no prior-run growth rate exists to compare against.
- **Confirm:** inspection data from MB-1880 runs before 2026-11-08 at 6% (if retained) shows a materially slower growth per 100 parts than 0.003–0.007 mm.
- **Kill:** pre-adjustment runs show the same growth rate. Or T7-0032 at 8% shows the same slope as runs at 6%.

### Candidate 4 (rank 4, weak): shift-2 practice (offset or set-up handling) adds bias → L-0412 pushed over

Stated as a pattern, not a person.

- **Link 1 — out-of-spec parts cluster on shift 2**
  - For: all 3 out-of-spec rows are shift 2 (3/5 shift-2 rows, against 0/6 on shift 1; shift 2 is 45% of rows).
  - Against: shift and operator are completely confounded (only the pairs shift 1/OP-11 and shift 2/OP-23 appear). Shift 2's last lot is also the latest on the insert. With 3 failures this is small numbers, not a pattern.
- **Link 2 — shift 2 sits above the time trend**
  - For: mean residual from the time trend is +0.0012 mm on shift 2 against -0.0012 mm on shift 1 (n = 5 each).
  - Against: 0.0012 mm is small next to the 0.027 mm reset at the insert change. L-0410 on shift 2 was in spec and on trend.
- **Link 3 — an offset practice mechanism**
  - For: NCR-0244 (MB-1500) had "wrong offset after tool change", a different part with the machine unknown.
  - Against: there was no tool change on shift 2 during L-0410 or L-0412.
- **Confirm:** run shift 2 on the new insert and compare residuals at equal parts cut.
- **Kill:** shift-2 parts on T7-0032 match the shift-1 trend.

### Not raised as candidates (and why)

- **Material lot:** the inputs carry no material heat, lot, supplier or receipt fields (query: 0 fields found). L-04xx are production lots. The material check could not run.
- **Measurement system:** two finding values (22.034, 22.029) match in-process values, which argues against a gage error at final inspection only. The gage and its calibration are not recorded, so this could not be fully checked.

### Ranking statement

Candidates 1 and 2 are **tied on the evidence for the mechanism**: both explain the trend and the reset, and the data cannot separate them. Together they are clearly ahead of 3 and 4. Candidate 3 is not excluded, only untested.

**Cheapest discriminating test:** before VMC-03 cuts more MB-1880 on T7-0032, record the T7 head setting on the presetter and measure Bore A every ~50 parts for the first ~300 parts. Keep removed insert T7-0031 and inspect its edge. This separates Candidates 1 and 2: if the head setting is unchanged and the bore still rises, it is the edge; if the setting moved, it is the head. The same data at 8% coolant gives the growth rate to compare with pre-2026-11-08 records, which tests Candidate 3. Splitting the run across both shifts also tests Candidate 4.

## 2. Supplier-caused flag

**Not raised.** No candidate points at purchased material, and no material lot, supplier or receipt data exists in the inputs.

## 3. 8D — BLOCKED

Blocked because the NCR (`NCR-DRAFT-MB-1880-WO-8102.md`) is `approval_state: draft`. Nothing is drafted for D1 to D8 until a quality owner approves the NCR. When it is approved, the 8D will be drafted with D1 to D5 and D7 populated and D6 and D8 as empty placeholders. In that 8D:

- D4 will carry the tie above.
- Every D5 action will name the chain link it breaks.
- D7 must address **why CAPA-071 (insert change every 600 parts) did not prevent recurrence**. CAPA-071 was never verified effective, and a recurrence appeared with the insert at a computed floor of 211 parts (true count unknown).

Restating CAPA-071 is not an acceptable D7.

Containment (sorting and holding the 300 and the L-0411 tail) is NCR containment, not corrective action. It is in the NCR's section 5.

## 4. Customer pack and redaction

Blocked with the 8D. No diff exists yet.

**Pending redaction log:** no removal requests were made in this run, so none were refused. When the diff is built, the recurrence (NCR-0219 / CAPA-071) stays in. Operator IDs (OP-11, OP-23), the inspector's name and any cost come out.

## 5. Evidence appendix

### 5.1 Sources and freshness (all export-sourced files; no live system)

| Source | Covers | Clock |
|---|---|---|
| inspection_measurements.csv (quality export) | 2026-11-09T07:10 to 2026-11-11T07:05, 11 rows | zone-aware, -05:00 |
| maintenance_log.csv (CMMS export, not live) | 2026-11-08T16:00 to 2026-11-11T06:40, 2 rows (VMC-03) | zone-aware, -05:00 |
| finding.txt | 2026-11-11 10:05 | **naive, zone unknown** |
| prior_ncrs.csv | NCR-0219 (2026-04-14), NCR-0244 (2026-08-02) | dates only |
| MB-1880_drawing_revB_notes.md | rev B, sheet 2 | — |

No historian or sensor export was provided, so there is no sensor evidence; VMC-03 may not be instrumented. A repair logged after the CMMS export would not appear here.

### 5.2 Time alignment

- No `## Plant context` block or plant profile was found (`plant_setup.py find`: `exists: false`), so no declared source clocks, measured skew or shift-boundary rule is available.
- Both CSVs carry an explicit -05:00 offset on every row.
- **Anchor event in two sources:** the insert-replaced entry (maintenance, 06:40) precedes the first T7-0032 row (inspection, 07:05, `tool_change_since_last = yes`) by 25.0 min. The ordering is consistent.
- Residual uncertainty: skew is not measured, only order-consistent to the 25-minute anchor gap. The maintenance correlation only uses gaps of 15 h or more (coolant event to first part), which no plausible zone or entry-lag error closes. Correlation at sub-hour resolution was not attempted.
- **Unresolved:** finding.txt (10:05, naive) versus the maintenance entry "insert replaced … after inspection hold" at 06:40 on the same day. The hold is logged 3 h 25 min before the final-inspection finding time, read at face value. Either an earlier (in-process) hold triggered it, or the finding's clock is in another zone (for example UTC, which would make it 05:05 -05:00). This also decides whether PS-5521 (08:00) shipped before or after the finding. It is reported as a finding and not resolved here.
- Shift boundary rule: not on file. Shift is taken as recorded on each inspection row.

### 5.3 SPC (computed)

| Point (time order) | Lot | Shift | Insert | Seq | Bore mm | vs baseline limits | vs spec 22.000–22.021 |
|---|---|---|---|---|---|---|---|
| 11-09 07:10 | L-0409 | 1 | T7-0031 | 1 | 22.008 | below LCL | in |
| 11-09 09:40 | L-0409 | 1 | T7-0031 | 40 | 22.010 | in | in |
| 11-09 12:15 | L-0409 | 1 | T7-0031 | 80 | 22.012 | in | in |
| 11-09 15:30 | L-0410 | 2 | T7-0031 | 1 | 22.013 | in | in |
| 11-09 19:45 | L-0410 | 2 | T7-0031 | 60 | 22.016 | in | in |
| 11-10 07:20 | L-0411 | 1 | T7-0031 | 1 | 22.017 | in | in |
| 11-10 11:05 | L-0411 | 1 | T7-0031 | 70 | 22.019 | above UCL | in |
| 11-10 15:10 | L-0412 | 2 | T7-0031 | 1 | 22.022 | above UCL | **out** |
| 11-10 18:30 | L-0412 | 2 | T7-0031 | 90 | 22.029 | above UCL | **out** |
| 11-10 21:50 | L-0412 | 2 | T7-0031 | 180 | 22.034 | above UCL | **out** |
| 11-11 07:05 | L-0413 | 1 | T7-0032 | 1 | 22.007 | below LCL | in |

Control limits are not specification limits. L-0411 seq 70 was in spec but already beyond the control limit. The baseline used for the limits is itself trending (7 of 7 points rising), so the limits are a reference, not a statement of capability.

### 5.4 Clustering (against base rates)

- **By lot:** 3/3 L-0412 rows out; 0 in other lots.
- **By insert:** T7-0031 3/10 out; T7-0032 0/1 (one point only).
- **By shift:** 3/5 shift 2 against 0/6 shift 1 (45% / 55% of rows).
- **By operator:** identical to shift (fully confounded).
- **By machine:** VMC-03 only, so the comparison could not run.

Small numbers throughout (3 failures).

### 5.5 Checks: three states

- **Came back clean / not supported:** shift or operator as an independent cause (small residual, confounded). No maintenance event during the T7-0031 run (count 0).
- **Fired:** trend rule (10 consecutive rising points). Rule 1 (6 points beyond the baseline limits: 4 above UCL, L-0411 seq 70 and L-0412 seq 1/90/180; 2 below LCL, L-0409 seq 1 and L-0413 seq 1, both fresh-insert points). Lot clustering on L-0412. Reset at the insert change.
- **Could not run:**
  - Material lot clustering (no material or heat data).
  - Sensor correlation (no historian export).
  - Gage calibration (gage not recorded).
  - Coolant before/after comparison (0 rows before the adjustment).
  - Parts-cut axis (lot sizes for L-0409..L-0411 unknown).
  - Measured clock skew (no plant context).

### 5.6 Figures block (internal; computed by scripts/analyze.py)

| Figure | Value | Computed from | Filter or query |
|---|---|---|---|
| Inspection rows | 11 | inspection_measurements.csv | all non-comment rows |
| Maintenance rows, VMC-03 | 2 | maintenance_log.csv | asset_id == "VMC-03" |
| UTC offset on every timestamp | -05:00 | both CSVs | utcoffset() |
| Inspection rows out of spec | 3 of 11: L-0412 seq 1 22.022, seq 90 22.029, seq 180 22.034 | inspection CSV | >22.021 or <22.000 |
| SPC basis | I-MR; limits from 7 points, L-0409/L-0410/L-0411 (WO-8099..8101, T7-0031, 11-09 07:10 to 11-10 11:05); L-0412, L-0413 plotted against them | inspection CSV | lot in baseline |
| SPC centreline | 22.0136 mm | inspection CSV | mean of baseline |
| SPC MR-bar / sigma | 0.0018 / 0.00163 mm | inspection CSV | MR-bar/1.128 |
| SPC UCL | 22.0184 mm | inspection CSV | CL + 3σ |
| SPC LCL | 22.0087 mm | inspection CSV | CL − 3σ |
| Points beyond baseline limits | 6: L-0409 seq1 (below), L-0411 seq70 (above), L-0412 seq1/90/180 (above), L-0413 seq1 (below) | inspection CSV | x>UCL or x<LCL |
| L-0412 (x−CL)/(UCL−CL) | seq1 1.73; seq90 3.16; seq180 4.19 | inspection CSV | same computation |
| Run rule checked | Trend rule (6+ consecutive rising/falling) and rule 1 | inspection CSV | time order, 11 points |
| Run rule result | 10 consecutive rising points (points 1–10, all T7-0031): FIRES | inspection CSV | x[i]>x[i−1] |
| Baseline itself trending | 7 of 7 rising: True | inspection CSV | baseline only |
| I-MR on all 11 points CL/UCL/LCL | 22.0170 / 22.0311 / 22.0029 | inspection CSV | all rows (MR inflated by reset) |
| Trend slope, T7-0031 | 0.000535 mm/h, intercept 22.0080, R² 0.876 (10 points) | inspection CSV | OLS vs hours since 11-09 07:10 |
| Fitted line reaches USL | 24.3 h → 2026-11-10T07:25-05:00 | inspection CSV | (22.021−b)/m |
| Shift residuals from trend | shift 1: n 5, −0.0012; shift 2: n 5, +0.0012 mm | inspection CSV | by shift |
| Within-lot rise per 100 parts | L-0409 0.0051; L-0410 0.0051; L-0411 0.0029; L-0412 0.0067 mm | inspection CSV | (last−first)/Δseq×100 |
| Highest seq per lot (T7-0031) | L-0409 80, L-0410 60, L-0411 70, L-0412 180 | inspection CSV | max(seq) by lot |
| Parts on T7-0031 at L-0412 seq 1 | at least 211 | inspection CSV | floor; lot sizes unknown |
| Parts on T7-0031 at end of L-0412 | at least 510 (210 + 300) | inspection CSV + finding.txt | floor |
| OOS by shift | 1: 0/6 (55% of rows); 2: 3/5 (45%) | inspection CSV | group by shift |
| OOS by operator | OP-11 0/6; OP-23 3/5 | inspection CSV | group by operator |
| OOS by lot | L-0409 0/3; L-0410 0/2; L-0411 0/2; L-0412 3/3; L-0413 0/1 | inspection CSV | group by lot |
| OOS by insert | T7-0031 3/10; T7-0032 0/1 | inspection CSV | group by tool_id |
| Shift–operator pairs | (1, OP-11), (2, OP-23) only | inspection CSV | distinct pairs |
| Step at insert change | 0.027 mm (22.034 → 22.007) | inspection CSV | L-0412 seq180 − L-0413 seq1 |
| Coolant adjustment to first inspection row | 15.17 h | both CSVs | time difference |
| Inspection rows before coolant adjustment | 0 | inspection CSV | ts < 2026-11-08T16:00-05:00 |
| Anchor gap (insert replaced → first T7-0032 row) | 25.0 min | both CSVs | time difference |
| Maintenance events during T7-0031 run | 0 | maintenance_log.csv | ts in [11-09 07:10, 11-10 21:50] |
| Finding: nonconforming of sampled | 3 of 5 | finding.txt | as written |
| Finding values over USL | 0.013, 0.010, 0.008 mm | finding.txt | measured − 22.021 |
| Finding values also in inspection CSV | 22.034, 22.029 | both | exact value match |
| Containment quantities reported | 120 + 150 + 30 = 300 | finding.txt | sum |
| Prior NCRs, same part | 1: NCR-0219 (CAPA-071, effectiveness not verified) | prior_ncrs.csv | part == "MB-1880" |
| Prior NCRs, other parts | 1: NCR-0244 MB-1500 | prior_ncrs.csv | part != "MB-1880" |
| Prior NCRs naming VMC-03 | 0 (file has no machine column) | prior_ncrs.csv | text contains "VMC-03" |
| Material/supplier/receipt fields | 0 | all 5 inputs | column and text search |

## 6. Quality Register row (not stored)

**The Quality Register was not updated:** the artifact tools are not available in this run. The row is saved to `quality-register-row_MB-1880.yaml`. Register banner: *"Tracks NCRs run through this plugin since [date unknown: the register was not reachable this run]. Not your full quality library."*

| Field | Value |
|---|---|
| record_key | `<site not given>_<NCR ref not assigned>` |
| status | awaiting_approval |
| approval_state | draft |
| customers | Northwind Robotics |
| escape_clock | null; escape_clock_unknown: true |
| recurrence | recurrence_prior_capa_failed (NCR-0219; previous_fix_held: false) |
| eight_d_step | null (8D blocked: NCR not approved) |
| leading_cause | Candidate (tied): progressive change at T7 boring tool over insert life, insert edge or head setting; not established |
| supplier_caused | false |
| owner / due_date | unassigned / no due date |

## 7. Questions for the quality owner (recorded instead of asked)

1. Do you approve the draft NCR (finding, cited requirement, suspect scope of at least 300, containment)? **Who should I record as approving it?** The 8D and the corrective-action plan are drafted only after this.
2. What is the NCR number, and which site is this?
3. What are Northwind Robotics's notification terms (window), and who is the contact? Has PS-5521 been delivered?
4. What were the lot sizes of L-0409, L-0410 and L-0411, and how many L-0411 parts were made after seq 70? Where are they now?
5. How many parts had insert T7-0031 cut before 2026-11-09 07:10? This settles whether CAPA-071's 600-part interval was exceeded or simply too long.
6. What "inspection hold" triggered the 06:40 insert change, and in which timezone is the finding's 10:05 recorded?
7. Which gage measured Bore A, and is it in calibration?
8. Is any MB-1880 bore data from before the 2026-11-08 coolant change retained?
9. Is there a plant or customer (Northwind Robotics) 8D template to use? None is on file.
