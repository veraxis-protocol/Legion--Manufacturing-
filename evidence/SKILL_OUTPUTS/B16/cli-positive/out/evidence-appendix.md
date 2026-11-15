# Evidence appendix — MB-1880 / L-0412 bore oversize (INTERNAL — never in the customer pack)

## Sources and coverage

| Source | File | Coverage | Clock |
|---|---|---|---|
| Finding | inputs/quality/finding.txt | 2026-11-10 to 2026-11-11 events | **Zone-naive.** Assumed plant local −05:00. Not anchored to a second source |
| Drawing notes | inputs/quality/MB-1880_drawing_revB_notes.md | rev B, sheet 2 | n/a |
| In-process inspection | inputs/quality/inspection_measurements.csv | 2026-11-09T07:10 to 2026-11-11T07:05 −05:00 (F3) | Zone-aware −05:00 (F2) |
| Maintenance | inputs/quality/maintenance_log.csv — **export-sourced, not a live CMMS.** A repair logged after the export would be missing | 2026-11-08T16:00 to 2026-11-11T06:40 −05:00 (F4) | Zone-aware −05:00 |
| Prior NCRs/CAPAs | inputs/quality/prior_ncrs.csv | 2 rows (F52) | dates only |
| Historian / sensor data | — | **Not available.** No spindle-load, temperature or coolant trace | — |
| ERP (shipments, WO quantities, material receipts) | — | **Not available** | — |

**The inspection export does not cover the final-inspection sample itself.** 22.031 is not in it (F10). The 22.034 and 22.029 values match in-process readings by value only, and are not confirmed to be the same parts.

## Time alignment
- Every timestamp in both CSVs carries −05:00 (F2). That is EST and is consistent with US DST having ended on 2026-11-01. Nothing in these sources crosses a DST change.
- **Anchor in two sources:** the maintenance log has the insert replaced at 06:40. The inspection export shows the first T7-0032 reading at 07:05, flagged `tool_change_since_last=yes`. That is +25 min, in the expected order (F48).
- **Residual uncertainty:** ordering is verified, but exact skew is not. The maintenance time may be the time of entry. Conclusions here work on hour-to-day scales, so correlating inspection and maintenance is allowed with that ±25 min caveat.
- **finding.txt is not anchored to anything.** Statements that rely on its times (F56, F57, F58) assume −05:00 local and are labelled that way.
- Shift boundary and production-day rule: **not on file** (no plant profile). Shift labels are taken as recorded.

## Timeline (−05:00)

| Time | Source | Event |
|---|---|---|
| 11-08 16:00 | maint | Coolant 6% → 8% |
| 11-09 07:10 | insp | New insert T7-0031; L-0409 part 1 = 22.008 |
| 11-09 12:15 | insp | L-0409 part 80 = 22.012 |
| 11-09 15:30–19:45 | insp | L-0410 (shift 2) 22.013 → 22.016 |
| 11-10 07:20 | insp | L-0411 part 1 = 22.017. **AIAG trend rule fires (F19)** |
| 11-10 11:05 | insp | L-0411 part 70 = 22.019. Nelson rule 3 fires (F20). 2 µm margin (F30) |
| 11-10 ~13:48 | computed | Interpolated USL crossing (assumes linear drift) (F29) |
| 11-10 15:10 | insp | **L-0412 part 1 = 22.022, first out-of-spec reading (F6)** |
| 11-10 18:30 / 21:50 | insp | L-0412 parts 90 / 180 = 22.029 / 22.034 |
| 11-11 06:40 | maint | Insert replaced "after inspection hold" |
| 11-11 07:05 | insp | L-0413 on T7-0032 = 22.007 |
| 11-11 08:00 | finding | 30 × L-0412 shipped to Northwind, PS-5521. **80 min after the hold (F56)** |
| 11-11 10:05 | finding | Final inspection: 3 of 5 out of spec. **125 min after the shipment (F57)** |

## SPC (computed, T7-0031 readings)
- Individuals/MR chart, n = 10 (F16). **CL 22.0180, UCL 22.0257, LCL 22.0103 mm** (F13–F15). These are control limits, **not** spec limits. The UCL sits 4.7 µm above the USL (F18).
- Points beyond the limits: 4, at both ends of the trend (F17). The limits come from a trending series with no stable baseline, so they are wide and the chart's main signal is the trend.
- **Run rule checked:**
  - Six points steadily increasing (AIAG) **fired at 2026-11-10 07:20** (L-0411, 22.017, still in spec), **7.83 h before** the first out-of-spec reading (F19, F21).
  - Nelson rule 3 fired at 11:05 (F20).
  - Nine-in-a-row above the centreline did **not** fire: the longest run was 4 (F22).

## Clustering (against base rates)
- **Shift:** shift 2 had 5 of 11 readings (45%) and 3 of 3 out-of-spec (F37). Shift 1 had 6 of 11 (55%) and 0 of 3 (F36). **That is small numbers, and it is confounded with tool age.** All 3 out-of-spec readings are from the last lot on the insert. Not a pattern on its own.
- **Operator:** identical to shift, because the two are fully confounded (F40). Reported as a pattern, not a person.
- **Machine:** VMC-03 only (F43). No comparison possible.
- **Tool change:** the strongest signal. The bore rose on 9 of 9 steps while on T7-0031 (F12), then stepped −27 µm at the change (F35).
- **Material lot: could not run.** There is no lot or heat column (F44).

## Maintenance correlation
- The only event during T7-0031's life other than its replacement: **0** (F47).
- The coolant change came 15 h before the insert was installed (F45), so the whole drift happened at 8%. The new insert at 8% read 22.007 (F34).

## Checks that came back clean
- No maintenance event inside the drift window (F47).
- No points below the LSL (F5).
- The overnight idle produced no step (+1 µm, F28), which argues against a thermal cause.
- L-0412 locations reconcile to the lot size (F54).

## Checks that could not run
- **Material/heat clustering:** no material lot data (F44).
- **Sensor correlation:** no historian export.
- **Recurrence search by machine and by supplier:** no such fields in prior NCRs (F51).
- **Gage calibration:** gage not recorded.
- **Shipment verification:** no ERP.

## Figures block
See `analysis/figures_block.md` (F1–F60), produced by `analysis/compute_figures.py` from the input files. It is printed in full in the chat reply.
