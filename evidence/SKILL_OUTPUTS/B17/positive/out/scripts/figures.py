# Computes every figure used in the BSH-1210 chain outputs from the input files.
import csv, re, statistics, sys, json, datetime
base = sys.argv[1]
finding = open(base + "/incoming_finding.txt", encoding="utf-8").read()
drawing = open(base + "/BSH-1210_drawing_revA.md", encoding="utf-8").read()
rows = [r for r in csv.DictReader(l for l in open(base + "/approved_suppliers.csv", encoding="utf-8") if not l.startswith("#"))]
F = []
def add(name, value, src, filt): F.append((name, value, src, filt))
m = re.search(r"Hardness measured ([\d, ]+) HRF on (\d+) samples", finding)
vals = [int(v) for v in m.group(1).split(",")]
n_stated = int(m.group(2))
lo, hi = map(int, re.search(r"Hardness (\d+)-(\d+) HRF", drawing).groups())
coc = int(re.search(r"C of C for lot AS-7781 states hardness (\d+) HRF", finding).group(1))
add("Hardness readings parsed", len(vals), "incoming_finding.txt", "regex 'Hardness measured ... HRF on N samples'")
add("Samples stated in finding", n_stated, "incoming_finding.txt", "same")
add("Spec limits (LSL-USL)", f"{lo}-{hi} HRF", "BSH-1210_drawing_revA.md", "regex 'Hardness (\d+)-(\d+) HRF'")
oos = [v for v in vals if v > hi or v < lo]
add("Readings above USL", f"{len([v for v in vals if v>hi])} of {len(vals)}", "incoming_finding.txt", f"value > {hi}")
add("Readings below LSL", f"{len([v for v in vals if v<lo])} of {len(vals)}", "incoming_finding.txt", f"value < {lo}")
mean = statistics.mean(vals); sd = statistics.stdev(vals)
add("Mean hardness", round(mean,2), "incoming_finding.txt", "mean of 5 readings")
add("Min / max hardness", f"{min(vals)} / {max(vals)}", "incoming_finding.txt", "min, max")
add("Sample std dev", round(sd,3), "incoming_finding.txt", "stdev (n-1)")
add("Min reading minus USL", f"{min(vals)-hi} HRF", "computed", "min - USL")
add("Max reading minus USL", f"{max(vals)-hi} HRF", "computed", "max - USL")
add("Mean minus USL", f"{round(mean-hi,2)} HRF", "computed", "mean - USL")
add("Mean / USL", round(mean/hi,3), "computed", "mean / USL")
add("Mean minus C of C value", f"{round(mean-coc,2)} HRF", "computed", f"mean - {coc}")
add("C of C value within spec", lo <= coc <= hi, "incoming_finding.txt", f"{lo}<= {coc} <={hi}")
# Individuals chart from this lot's 5 points only
mrs = [abs(vals[i]-vals[i-1]) for i in range(1,len(vals))]
mrbar = statistics.mean(mrs)
ucl = mean + 2.66*mrbar; lcl = mean - 2.66*mrbar
add("SPC centreline (X-bar of individuals)", round(mean,2), "computed", "individuals chart")
add("SPC UCL", round(ucl,2), "computed", "CL + 2.66 x MRbar")
add("SPC LCL", round(lcl,2), "computed", "CL - 2.66 x MRbar")
add("SPC basis", f"individuals/MR chart, n={len(vals)} points, MRbar={round(mrbar,2)}, lot AS-7781 only (no prior-lot measurements supplied)", "computed", "order as listed in finding")
beyond = [v for v in vals if v>ucl or v<lcl]
side = all(v>mean for v in vals) or all(v<mean for v in vals)
add("SPC run rule checked", f"WE rule 1 (point beyond 3-sigma): {len(beyond)} points; rule 2 (8 on one side) not evaluable with {len(vals)} points", "computed", "")
add("Distance of LCL above USL", f"{round(lcl-hi,2)} HRF", "computed", "LCL - USL (control limits vs spec limits)")
# lot clustering
lots = {"AS-7702":"pass","AS-7744":"pass","AS-7781":"fail"}
add("Lots from supplier in finding", len(lots), "incoming_finding.txt", "AS-7702, AS-7744, AS-7781")
add("Lots failing incoming hardness", f"{sum(1 for v in lots.values() if v=='fail')} of {len(lots)}", "incoming_finding.txt", "")
# quantities
q_lot = int(re.search(r"qty ([\d,]+)\.", finding).group(1).replace(",",""))
q_issued = int(re.search(r"(\d+) pcs already issued", finding).group(1))
q_quar = int(re.search(r"(\d+) pcs in receiving quarantine", finding).group(1))
add("Lot quantity received", q_lot, "incoming_finding.txt", "'qty 1,000'")
add("Issued to line 2 (WO-8150)", q_issued, "incoming_finding.txt", "")
add("In receiving quarantine Q-1", q_quar, "incoming_finding.txt", "")
add("Issued + quarantined", q_issued+q_quar, "computed", "")
add("Reconciles to lot qty", q_issued+q_quar == q_lot, "computed", "")
add("Share of lot already issued", f"{round(100*q_issued/q_lot,1)}%", "computed", "issued/lot")
# suppliers
comm = [r for r in rows if "bronze" in r["commodity"]]
appr = [r for r in comm if r["status"]=="approved"]
add("Suppliers on approved list (all rows)", len(rows), "approved_suppliers.csv", "all rows")
add("Rows matching commodity 'bronze'", len(comm), "approved_suppliers.csv", "commodity contains 'bronze'")
add("Approved for bronze commodity", f"{len(appr)} ({', '.join(r['supplier'] for r in appr)})", "approved_suppliers.csv", "status == approved")
add("Approved, excluding implicated supplier", len([r for r in appr if not r['supplier'].startswith('Alder')]), "approved_suppliers.csv", "")
add("Rows naming BSH-1210 as current source", len([r for r in rows if 'current source BSH-1210' in r['notes']]), "approved_suppliers.csv", "notes contains 'current source BSH-1210'")
add("Conditional / not approved", len([r for r in comm if r['status']!='approved']), "approved_suppliers.csv", "status != approved")
today = datetime.date(2026,11,14)
d_audit = {r['supplier']:(today-datetime.date.fromisoformat(r['last_audit'])).days for r in rows}
for k,v in d_audit.items(): add(f"Days since last audit, {k}", v, "approved_suppliers.csv", "2026-11-14 - last_audit")
add("Days from found (2026-11-12) to this run (2026-11-14)", (today-datetime.date(2026,11,12)).days, "computed", "")
print("| Figure | Value | Computed from | Filter or query |\n|---|---|---|---|")
for f in F: print("| " + " | ".join(str(x) for x in f) + " |")
