# VMC-02 breakdown diagnosis: 2026-11-10 15:24, SPINDLE OVERLOAD / OVERTEMP

*SYNTHETIC test data for a fictitious plant. This diagnosis is ADVISORY and has not been confirmed by a technician.*

> **Follow your plant's lockout procedure before anyone works on this machine. This is not a safety assessment.**

## ⚠ Safety: flagged

- **Do not run the spindle.** The operator heard a grinding noise for about 20 minutes before the alarm. OEM manual §7.4 says: *"Do not run a spindle showing grinding noise"* and *"Lock out the spindle drive before any manual rotation or inspection."* Vibration reached 11.2 mm/s at the alarm. A bearing in this state can seize if the spindle is powered again.
- **Stored energy (drawbar).** Candidate 3 involves the drawbar Belleville spring stack, which is a compressed spring pack. Only use the OEM procedure to release or adjust it. MW-131 shows that this stack has been adjusted on this machine before.
- **Heat.** The spindle nose and taper show bluish discolouration, which means the steel got very hot at that spot. Let the spindle cool before anyone touches the nose or taper.
- **Do not take the shortcut of restarting.** Do not reset the alarm and "run it to see". The manual's vibration-spectrum check needs a running spindle, so it is **excluded** while the grinding noise is unexplained.

## Event (as reported, not translated)

| | |
|---|---|
| Asset | VMC-02 |
| Down at | 2026-11-10 15:24 local (sensor export stamps −05:00) |
| Alarm | SPINDLE OVERLOAD / OVERTEMP. The machine stopped mid-cycle |
| Job interrupted | WO-8120 op 20 (MB-1880) |
| Operator | "grinding noise from spindle for ~20 min before alarm, chips looked normal" |
| Photo | **No photo file.** Text description only: "bluish discolouration visible on the spindle nose / taper area" |
| Status | Still down at 16:10, the last status received. The current state is unknown |

## Sensor observation summary

The window runs from 13:00 to 15:24 and covers the event. The last sample is at the alarm time. There is no data after the alarm.

| Time | Vib mm/s | Temp °C | Load % | Coolant bar |
|---|---|---|---|---|
| 13:00 | 1.8 | 31.0 | 42 | 20.1 |
| 13:30 | 1.9 | 31.4 | 44 | 20.0 |
| 14:00 | 2.4 | 33.2 | 45 | 19.9 |
| 14:30 | 3.1 | 36.0 | 47 | 20.1 |
| 15:00 | 4.6 | 40.8 | 49 | 20.0 |
| 15:20 | 7.9 | 47.5 | 58 | 19.8 |
| 15:24 | 11.2 | 52.1 | 71 | 19.9 |

- **Vibration started climbing first and kept speeding up.** It was flat until 13:30. After that it rose by 0.5, 0.7, 1.5, 3.3 and then 3.3 mm/s between samples, and the last rise took only 4 minutes. This is a runaway shape, not a step change.
- **Temperature followed vibration.** It rose 21.1 °C across the window. The steepest rise matched the steepest vibration rise.
- **Spindle load stayed level (42→49 %) until 15:00 and then jumped to 71 %.** That suggests the load rose because of friction late in the failure, not because the cut got heavier. This fits the operator's "chips looked normal".
- **Coolant pressure was flat (19.8–20.1 bar).** This channel is not labelled as chiller flow. It looks like cutting or through-spindle coolant pressure, so **it says nothing about the spindle chiller.** There is no chiller channel in the export.
- Samples are unevenly spaced (30, 30, 30, 30, 20 and 4 min). The trend is clear, but the exact time of onset cannot be pinned down.

## Maintenance history and close-out notes

The maintenance export holds 5 records in total: 4 for VMC-02 and 1 for VMC-03. **All four VMC-02 notes are specific observations.** None of them is a template (see the figures block).

| WO | Date | Type | Close-out note (verbatim) |
|---|---|---|---|
| MW-118 | 2026-03-02 | PM | "quarterly PM done. greased ways. spindle sounded a bit rough at 8k, monitor" |
| MW-131 | 2026-05-19 | CM | "spindle alarm 2nd shift. found drawbar clamp low, adjusted belleville stack. ran ok" |
| MW-140 | 2026-07-08 | PM | "PM. vib reading 2.1 mm/s at 8k (was 1.4 last yr). told sup" |
| MW-160 | 2026-09-23 | CM | "spindle hot after long cycle. checked chiller - low on fluid topped up. temp ok after" |

The notes show a spindle getting worse over eight months. Twice it was flagged ("monitor", "told sup") and **no follow-up work order exists in the export**. That absence is not found by search: the filter was VMC-02 records after 2026-07-08 that mention vib, spindle or bearing, and it returned only MW-160, which was a chiller job.

**Sibling search:** VMC-03 is the only other VMC in the export. Its one record is MW-152, "coolant pump replaced - not related". It has no spindle, bearing, drawbar or chiller history. **The make and model could not be confirmed.** There is no model column, and the asset names do not state it, so VMC-03 is treated as a likely sibling but this is not verified.

**Freshness:** the event was on 2026-11-10 and today is 2026-11-15. This is a static export. Anything done on VMC-02 since the stoppage, including any teardown findings, is **not in this data**.

## OEM manual: VMC spindle troubleshooting, Section 7.4

| Manual row | Match to this event |
|---|---|
| Overtemp with rising vibration → spindle bearing wear / preload loss | **Matches.** Both rose together |
| Overtemp, normal vibration → chiller low flow / fluid level | Does not match as the primary cause, because vibration was not normal. It may be a contributor |
| Overload with tool pull-out marks → drawbar clamp force low (spec 8.0–9.5 kN) | Overload is present. **Pull-out marks were not reported and not yet looked for** |
| Grinding noise → bearing damage or contamination | **Matches** the operator report |

---

## Ranked candidate causes

### 1. Spindle bearing failure (wear or preload loss, possibly contamination). Likelihood: high

**Evidence**
- The OEM §7.4 row "Overtemp with rising vibration" fits exactly, and so does the "Grinding noise → bearing damage" row.
- The sensor window shows vibration rising first and speeding up, from 1.8 to 11.2 mm/s (6.2×), with temperature following.
- History shows the same trend over months. In MW-118 (Mar) the spindle was "a bit rough at 8k, monitor". In MW-140 (Jul) vibration was "2.1 mm/s at 8k (was 1.4 last yr)", a 50 % rise, "told sup". Neither note led to a follow-up.
- The blue discolouration at the nose and taper fits heat from the front bearing. The photo is a text description only, so it is not conclusive (see candidate 3).

**First check (spindle locked out and cooled)**
1. Turn the spindle by hand and feel for roughness, notching or tight spots (manual §7.4, grinding row).
2. Measure run-out at the taper with a dial indicator. The OEM spec is **< 3 µm**.

Rough rotation or run-out over 3 µm confirms this candidate. Smooth rotation with run-out in spec makes it much less likely, and you should move to candidates 2 and 3. This takes about 15 minutes with a dial indicator and a test bar, and needs no power.

**Expected fix and repair path**
- Replace the spindle bearings or the spindle cartridge (OEM or a spindle rebuild shop). Before ordering, check for coolant contamination of the bearings, because through-spindle coolant runs at about 20 bar.
- When the spindle comes out, inspect the taper and the drawbar too.
- After the rebuild, record a new baseline vibration reading at 8k rpm.

*Cited: MW-118, MW-140. Sensor window. OEM §7.4 rows 1 and 4.*

### 2. Spindle chiller low fluid or low flow (recurring). Likelihood: medium as a contributor, low as the sole cause

**Evidence**
- MW-160 (Sep) on this asset says "spindle hot after long cycle. checked chiller - low on fluid topped up". The cause of the fluid loss was not recorded, so it may have dropped again.
- The OEM row for chiller causes says "normal vibration". Here vibration was not normal, so the chiller does not explain the grinding on its own.
- It could be the reason the bearings ran hot. Thermal growth raises bearing preload, which speeds up candidate 1.
- The sensor export has **no chiller channel**. The flat coolant pressure is not evidence either way.

**First check**
- Read the chiller fluid level (sight glass) and its flow indicator. This takes about 2 minutes and needs no tools or spindle rotation.
- Low fluid **plus** a smooth spindle on hand rotation points to the chiller as the primary cause. Low fluid **plus** a rough spindle points to candidate 1 with the chiller as a contributor. Both need fixing.

**Expected fix and repair path**
- Top up the chiller and find the leak, because this is the second time the fluid has been low.
- Check the chiller flow and filter.
- If the bearings are confirmed damaged, the chiller fix goes alongside the bearing repair, not in place of it.

*Cited: MW-160. OEM §7.4 row 2.*

### 3. Low drawbar clamp force (tool fretting in the taper). Likelihood: low to medium

**Evidence**
- MW-131 (May) on this asset says "spindle alarm 2nd shift. found drawbar clamp low, adjusted belleville stack. ran ok". So the Belleville stack has drifted before.
- A tool moving in a loosely clamped taper heats the taper locally. That would fit **blue discolouration at the taper specifically**, plus the overload.
- Against it: the OEM row needs **tool pull-out marks**, and none have been reported yet. Rising vibration and grinding fit bearings better.

**First check**
- Pull the tool that was in the spindle on WO-8120 op 20. Look at the shank and the spindle taper for fretting, pull-out marks or bluing on the tool side. This is a free visual check and takes about 5 minutes.
- If there are marks, measure clamp force with the clamp force gauge. The spec is 8.0–9.5 kN. Mind the stored spring energy (see Safety).

**Expected fix and repair path**
- Re-shim or replace the Belleville stack and re-check the clamp force.
- Inspect the taper for damage and regrind it if needed.
- Note that this is the second drift since May.

*Cited: MW-131. OEM §7.4 row 3.*

## The cheapest test to tell them apart

Do this as one no-power sequence of about 20 minutes, under lockout, after the spindle has cooled:

1. **Chiller sight glass and flow** (about 2 min). This confirms or clears candidate 2's contribution.
2. **Pull the tool and inspect the shank and taper for fretting or pull-out marks** (about 5 min). This confirms or clears candidate 3.
3. **Hand-rotate the spindle and dial-indicate the taper run-out against the < 3 µm spec** (about 15 min). **This is the one test that confirms or clears the leading candidate.**

**Do not** run the spindle for a vibration spectrum. The manual lists the spectrum as the bearing check, but its own safety note forbids running a spindle that is grinding.

These causes are not mutually exclusive. The most likely chain is a bearing worn since spring (candidate 1), possibly sped up by low chiller fluid (candidate 2). All three checks are cheap, so do all three before ordering parts.

---

## PM plan adjustment: DRAFT for the maintenance planner

*The current PM plan was not available, because there is no CMMS connector. "Quarterly PM" is inferred from MW-118. **Planner: please confirm today's interval and task list for VMC-02 first.***

For VMC-02, failure mode: spindle bearing degradation and spindle overheating.

1. **Make the spindle vibration reading at 8k rpm a recorded PM step with an action limit.** Right now the reading is taken, but a rise produces "monitor" or "told sup" and nothing else. Proposed rule: if the reading is ≥ 1.5× the post-rebuild baseline, the PM automatically opens a CM work order for a vibration spectrum and run-out check. The planner should set the limit. 1.5× is the rise that MW-140 recorded and nobody acted on.
2. **Procedure change:** a close-out note containing "monitor", "rough" or "told sup" must create a dated follow-up work order. It cannot be closed as text only.
3. **Chiller:** add a monthly fluid level and flow check, and require the cause of any top-up to be recorded. Fluid was low in September (MW-160). Ask whether the 2026-11-10 check finds it low again.
4. **Drawbar:** add a clamp force gauge check (8.0–9.5 kN) to the quarterly PM. It drifted out once already (MW-131).
5. **Optional, since a historian channel already exists:** add an alarm on spindle vibration rate of change. On 2026-11-10 vibration was rising for more than an hour before the overtemp alarm tripped.
6. **Fleet:** apply items 1–4 to VMC-03 once it is confirmed to be the same make and model.

## Close-out note: DRAFT (paste into the ticket only once confirmed)

*Nothing has been written to any system. No CMMS connector is live.*

> Spindle overload/overtemp alarm 15:24, grinding ~20 min prior. Historian: vib 1.8→11.2 mm/s, temp 31→52 °C over 2.5 h, coolant pressure normal. LOTO checks: chiller level/flow [__], tool shank/taper marks [__], hand rotation [__], taper run-out [__ µm, spec <3]. Cause confirmed: [__]. Work done: [__]. New baseline vib @8k: [__ mm/s]. Watch: chiller level (low Sep, MW-160), drawbar clamp (adjusted May, MW-131).

---

## Figures block

**Counted by reading, not computed. Verify before relying on it.** Code execution was not available in this session.

| Figure | Value | Computed from | Filter or query |
|---|---|---|---|
| Maintenance records, all assets | 5 | maintenance_history.csv | all data rows |
| Maintenance records, VMC-02 | 4 (MW-118, MW-131, MW-140, MW-160) | maintenance_history.csv | `asset_id == "VMC-02"` |
| Records on sibling VMC assets | 1 (MW-152, VMC-03) | maintenance_history.csv | `asset_id startswith "VMC" and != "VMC-02"` |
| Sibling records mentioning spindle/bearing/vib/drawbar/chiller/hot/grinding | 0. **The query returned nothing** | maintenance_history.csv | VMC-03 rows, note contains any of those words |
| VMC-02 follow-up WO after MW-140 on vibration/bearing | 0, **not found in the export** | maintenance_history.csv | VMC-02, opened > 2026-07-08, note contains vib/bearing/rough; MW-160 is a chiller job |
| Template check: distinct close-out texts / texts on >1 asset | 5 / 0 | maintenance_history.csv | group by exact note text, count distinct asset_id. No model column, and the model cannot be derived from the asset names |
| Usable (specific) VMC-02 notes | 4 of 4 | maintenance_history.csv | by reading |
| Vibration start → alarm | 1.8 → 11.2 mm/s (6.2×) | sensor_window.csv | 13:00 row vs 15:24 row |
| Temperature rise over window | 21.1 °C (31.0 → 52.1) | sensor_window.csv | same rows |
| Load before / at alarm | 49 % (15:00) → 71 % (15:24) | sensor_window.csv | |
| Coolant pressure range | 19.8–20.1 bar | sensor_window.csv | all rows |
| MW-140 vibration vs prior year | 2.1 / 1.4 = 1.5× | MW-140 note | |
| Known downtime at last status | ≥ 46 min (15:24 → 16:10). **The machine is still down, so this is not a duration** | event.txt | |
| Sensor rows in window | 7 | sensor_window.csv | |
