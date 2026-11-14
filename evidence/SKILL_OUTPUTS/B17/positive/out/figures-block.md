| Figure | Value | Computed from | Filter or query |
|---|---|---|---|
| Hardness readings parsed | 5 | incoming_finding.txt | regex 'Hardness measured ... HRF on N samples' |
| Samples stated in finding | 5 | incoming_finding.txt | same |
| Spec limits (LSL-USL) | 25-40 HRF | BSH-1210_drawing_revA.md | regex 'Hardness (\d+)-(\d+) HRF' |
| Readings above USL | 5 of 5 | incoming_finding.txt | value > 40 |
| Readings below LSL | 0 of 5 | incoming_finding.txt | value < 25 |
| Mean hardness | 48 | incoming_finding.txt | mean of 5 readings |
| Min / max hardness | 46 / 50 | incoming_finding.txt | min, max |
| Sample std dev | 1.581 | incoming_finding.txt | stdev (n-1) |
| Min reading minus USL | 6 HRF | computed | min - USL |
| Max reading minus USL | 10 HRF | computed | max - USL |
| Mean minus USL | 8 HRF | computed | mean - USL |
| Mean / USL | 1.2 | computed | mean / USL |
| Mean minus C of C value | 16 HRF | computed | mean - 32 |
| C of C value within spec | True | incoming_finding.txt | 25<= 32 <=40 |
| SPC centreline (X-bar of individuals) | 48 | computed | individuals chart |
| SPC UCL | 55.31 | computed | CL + 2.66 x MRbar |
| SPC LCL | 40.69 | computed | CL - 2.66 x MRbar |
| SPC basis | individuals/MR chart, n=5 points, MRbar=2.75, lot AS-7781 only (no prior-lot measurements supplied) | computed | order as listed in finding |
| SPC run rule checked | WE rule 1 (point beyond 3-sigma): 0 points; rule 2 (8 on one side) not evaluable with 5 points | computed |  |
| Distance of LCL above USL | 0.69 HRF | computed | LCL - USL (control limits vs spec limits) |
| Lots from supplier in finding | 3 | incoming_finding.txt | AS-7702, AS-7744, AS-7781 |
| Lots failing incoming hardness | 1 of 3 | incoming_finding.txt |  |
| Lot quantity received | 1000 | incoming_finding.txt | 'qty 1,000' |
| Issued to line 2 (WO-8150) | 400 | incoming_finding.txt |  |
| In receiving quarantine Q-1 | 600 | incoming_finding.txt |  |
| Issued + quarantined | 1000 | computed |  |
| Reconciles to lot qty | True | computed |  |
| Share of lot already issued | 40.0% | computed | issued/lot |
| Suppliers on approved list (all rows) | 3 | approved_suppliers.csv | all rows |
| Rows matching commodity 'bronze' | 3 | approved_suppliers.csv | commodity contains 'bronze' |
| Approved for bronze commodity | 2 (Alder Sintered Parts (fictitious), Birch Powder Metal (fictitious)) | approved_suppliers.csv | status == approved |
| Approved, excluding implicated supplier | 1 | approved_suppliers.csv |  |
| Rows naming BSH-1210 as current source | 1 | approved_suppliers.csv | notes contains 'current source BSH-1210' |
| Conditional / not approved | 1 | approved_suppliers.csv | status != approved |
| Days since last audit, Alder Sintered Parts (fictitious) | 376 | approved_suppliers.csv | 2026-11-14 - last_audit |
| Days since last audit, Birch Powder Metal (fictitious) | 267 | approved_suppliers.csv | 2026-11-14 - last_audit |
| Days since last audit, Cedar Bearings Inc (fictitious) | 882 | approved_suppliers.csv | 2026-11-14 - last_audit |
| Days from found (2026-11-12) to this run (2026-11-14) | 2 | computed |  |
