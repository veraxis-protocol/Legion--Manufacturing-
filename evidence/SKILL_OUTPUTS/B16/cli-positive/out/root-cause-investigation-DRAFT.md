# Root-cause investigation — DRAFT (NCR approved 2026-11-15; carried into 8D-INTERNAL-DRAFT-WO-8102-L-0412.md D4)

SYNTHETIC test data. Every number is quoted from the figures block (`analysis/figures_block.md`, F-numbers).

## Ranked candidate causal chains

Ranking is by evidential strength. **No single cause is established.** The data shows clearly *where* the change sits (the T7 boring tool state, which was reset at the insert change). It does not yet show *which mechanism* inside that tool state moved the diameter **upward**.

### Candidate 1 — Edge condition of insert T7-0031 grew the effective cutting radius (built-up edge on 6061, or edge damage), and the insert ran past its usable life
`T7-0031 cutting edge changes with use` → `effective bore radius grows (≈0.535 µm/h)` → `USL crossed ≈13:48 on 11-10` → `L-0412 cut entirely above limit`

- **Link 1: edge changes with use.**
  - *For:* The bore rose on 9 of 9 consecutive readings from install to removal (F12). Replacing the insert dropped the bore 27 µm back to 22.007 (F34, F35). No other maintenance event occurred during the insert's life (F47). NCR-0219 had the same symptom on the same part and was attributed to insert wear (prior_ncrs.csv).
  - *Against:* The removed insert has not been examined. **Ordinary flank wear on a boring insert normally makes a bore *smaller*, not larger.** So "insert wear", as NCR-0219 stated it, does not explain an oversize by itself. The mechanism has to be built-up edge or edge damage, and no evidence yet distinguishes those.
- **Link 2: radius grows steadily.**
  - *For:* The fit against time is r = 0.936 (F23). The overnight idle added only +1 µm (F28), which is consistent with a cumulative tool state and not with thermal recovery.
  - *Against:* The rate is not constant. L-0412 drifted 1.80 µm/h, against 0.53–0.79 µm/h in the earlier lots (F24–F27). End-of-life acceleration would explain that, but so would a shift-2 factor (Candidate 4).
- **Link 3: past usable life.**
  - *For:* CAPA-071 sets a 600-part life (F33).
  - *Against:* The provable floor of parts cut on this insert is 510, below 600 (F59). Lot sizes for L-0409–L-0411 are not on file. **This link has no direct evidence for it yet. It is the weak point of the chain.**
- **Confirm:** Microscope or photo of retained insert T7-0031 shows built-up edge or edge chipping, and the work-order quantities for WO-8099–8101 put the insert past 600 parts.
- **Kill:** Insert T7-0031 shows a clean edge with normal flank wear only, **or** a fresh insert reproduces the drift over a short run.

### Candidate 2 — Boring-head or cartridge diameter setting crept outward (mechanical loosening), and was reset at the insert change
`boring-head adjustment not locked / cartridge loose` → `set diameter walks outward under cutting load` → `bore grows steadily` → `out of spec`

- **Link 1: adjustment not locked.**
  - *For:* An insert change on a boring head usually involves re-setting the diameter, which would explain the full −27 µm reset (F35) just as well as Candidate 1 does.
  - *Against:* There is no record of the head setting before or after the change, and no tool-presetter record. **This link has nothing under For apart from compatibility with the reset. It is the weak point.**
- **Link 2: setting walks under load.**
  - *For:* The drift is monotone across both shifts (F12).
  - *Against:* The overnight +1 µm (F28) is a cumulative change, which fits creep as well as wear, so this does not discriminate.
- **Confirm:** The head is still set on the presetter as it came off the machine (if it was not re-zeroed) and reads larger than its documented set diameter, or the lock screw is found loose.
- **Kill:** Presetter or setup records show the head was not adjusted at the insert change, and only the insert was swapped.

**Candidates 1 and 2 are effectively tied on the data on hand.** Both predict a monotone rise and a reset at the change.

### Candidate 3 — Tool wear-offset or compensation entered in the wrong direction
`wear-offset entries on T7` → `sign or magnitude wrong` → `stepwise growth` → `out of spec`

- **For:**
  - A wrong offset after a tool change happened before at this plant (NCR-0244, a different part).
  - The 30 parts shipped 80 min after an "inspection hold" (F56), which suggests someone was already reacting. Offsets may have been touched.
- **Against:**
  - The growth is smooth on every reading (F12, F23) and not stepwise.
  - There was no tool change during the drift. NCR-0244's mechanism was triggered by a tool change.
  - No offset record exists in the data. **No link has direct evidence for it.**
- **Confirm:** The CNC offset/parameter history for T7 on VMC-03 shows wear-comp edits between 2026-11-09 07:10 and 2026-11-11 06:40 that add up to about +26 µm on diameter.
- **Kill:** The offset history shows no T7 edits in that window.

### Candidate 4 — A shift-2 practice factor added to the drift
`shift-2 practice (feed/speed override, offset touch, coolant top-up)` → `faster growth on shift 2` → `L-0412 crossed sooner`

- **For:**
  - All 3 out-of-spec readings came on shift 2 (F37).
  - The mean residual from the time trend is +1.20 µm on shift 2 and −1.20 µm on shift 1 (F41, F42).
  - L-0412 drifted at 1.80 µm/h (F27).
- **Against:**
  - Shift 2 also ran L-0410, which drifted at 0.71 µm/h, no faster than shift 1 (F25).
  - The numbers are small: n = 5 per shift.
  - Shift is **fully confounded** with operator (F40) and with tool age: L-0412 was simply the last lot on the insert.
  - **This is not established as a pattern.** It is reported as a pattern, not as a person.
- **Confirm:** The machine log shows feed/speed overrides or offset edits during L-0412 that did not occur on shift 1.
- **Kill:** The machine log shows identical program, overrides and offsets across both shifts.

### Candidate 5 — Coolant concentration change (6% → 8%, 2026-11-08 16:00) promoting built-up edge
- **For:** It is the only process change before the drift (F45). All T7-0031 parts were cut after it.
- **Against:**
  - The new insert T7-0032, also at 8%, read 22.007 (F34).
  - There is no data on this tool at 6% to compare against.
  - At most this is a contributor to Candidate 1. It does not explain the oversize alone.
- **Confirm:** The removed insert shows built-up edge (Candidate 1 confirm), **and** a short run at 6% on a fresh insert shows a slower drift.
- **Kill:** The drift rate on T7-0032 at 8% matches pre-11-08 history at 6%, if that history exists.

### Candidate 6 — Measurement or gage error (low)
- **For:** Gage IDs and calibration status are not recorded.
- **Against:**
  - In-process and final inspection agree on the direction and the magnitude.
  - The same measurement stream read 22.007 immediately after the insert change (F34). A gage error would not reset at a tool change.
- **Confirm:** Calibration of the bore gage(s) is lapsed, or a gage R&R shows a bias of 5 µm or more.
- **Kill:** Calibration is current, and a re-measure of 5 retained L-0412 parts on a CMM reproduces 22.029–22.034.

### Separate chain — why it escaped (detection and containment)
This is not the cause of the oversize. It is why 300 parts were cut and 30 shipped.

`in-process reading 22.022 on part 1 of L-0412 (F6)` → `no stop / reaction plan triggered` → `lot ran to completion` → `30 shipped 80 min after an inspection hold (F56) and 125 min before final inspection completed (F57)`

- **For:**
  - The in-process readings are in the export with production-time timestamps.
  - A computed trend rule would have signalled at 2026-11-10 07:20, **7.83 h before the first out-of-spec reading** (F19, F21).
- **Against / unknown:**
  - It is not confirmed that the export is a real-time in-process check rather than data entered later.
  - The reaction plan for VMC-03 bore readings is not on file.

## Cheapest discriminating test
**Pull insert T7-0031 and the T7 boring head, inspect the insert edge under magnification, and read the head on the presetter before anyone re-sets it. In the same visit, export the VMC-03 offset history for T7 (2026-11-09 07:10 → 2026-11-11 06:40).**

This takes about an hour, needs no production time, and separates Candidates 1, 2 and 3:
- Built-up edge or a chipped edge points to Candidate 1.
- A head reading oversize or a loose lock points to Candidate 2.
- T7 offset edits point to Candidate 3.

Pulling the WO-8099–8101 quantities from the ERP at the same time settles Link 3 of Candidate 1, which is whether CAPA-071's 600-part interval was followed.

## Supplier-caused flag
**Not raised.** No candidate points at purchased material. Material lot/heat is not in the inspection export (F44), so a material check **could not run**. That does not show material is ruled out; the data to test it is not there.
