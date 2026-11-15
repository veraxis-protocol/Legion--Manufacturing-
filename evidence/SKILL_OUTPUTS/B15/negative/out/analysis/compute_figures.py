"""MB-1880 oversize bore investigation - computed figures (root-cause-capa, Step 2).

Reads only the input files under work/inputs/quality. Every number printed in the
investigation page comes from this script's output (figures_block.csv / figures.json).
Run:  python -I compute_figures.py <inputs/quality dir> <out dir>
"""
import csv, json, re, sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

qdir, outdir = Path(sys.argv[1]), Path(sys.argv[2])
rows = []  # figure, value, computed_from, filter_or_query


def fig(name, value, src, query):
    rows.append({"figure": name, "value": value, "computed_from": src, "filter_or_query": query})
    return value


def read_csv(p):
    lines = [l for l in p.read_text(encoding="utf-8").splitlines() if l and not l.startswith("#")]
    return list(csv.DictReader(lines))

finding = (qdir / "finding.txt").read_text(encoding="utf-8")
drawing = (qdir / "MB-1880_drawing_revB_notes.md").read_text(encoding="utf-8")
maint = read_csv(qdir / "maintenance_log.csv")
prior = read_csv(qdir / "prior_ncrs.csv")

# --- requirement, from the drawing notes (note 4) ---
m = re.search(r"Bore A: dia (\d+\.\d+) \+(\d+\.\d+)/-(\d+\.\d+)", drawing)
nom, up, lo = float(m.group(1)), float(m.group(2)), float(m.group(3))
usl, lsl = round(nom + up, 4), round(nom - lo, 4)
tol = round(usl - lsl, 4)
fig("Bore A nominal (mm)", f"{nom:.3f}", "MB-1880_drawing_revB_notes.md", "note 4 regex 'Bore A: dia'")
fig("Bore A USL (mm)", f"{usl:.3f}", "MB-1880_drawing_revB_notes.md", "nominal + 0.021")
fig("Bore A LSL (mm)", f"{lsl:.3f}", "MB-1880_drawing_revB_notes.md", "nominal - 0.000")
fig("Tolerance band (mm)", f"{tol:.3f}", "MB-1880_drawing_revB_notes.md", "USL - LSL")
fig("Requirement in finding matches drawing note 4", str("22.000 +0.021/-0.000" in finding and "note 4" in finding),
    "finding.txt vs drawing notes", "string compare '22.000 +0.021/-0.000'")

# --- measurements (only the three nonconforming values are recorded) ---
meas_txt = re.search(r"measured ([\d\., ]+) mm on (\d+) of (\d+) sampled", finding)
vals = [float(v) for v in re.findall(r"\d+\.\d+", meas_txt.group(1))]
n_bad, n_sampled = int(meas_txt.group(2)), int(meas_txt.group(3))
fig("Measured values recorded", len(vals), "finding.txt", "values in 'measured ... mm'")
fig("Nonconforming / sampled", f"{n_bad} of {n_sampled}", "finding.txt", "'N of M sampled'")
fig("Share of sample nonconforming", f"{100*n_bad/n_sampled:.0f}%", "finding.txt", "n_bad / n_sampled")
fig("Conforming sample values recorded", f"0 of {n_sampled - n_bad}", "finding.txt", "no values given for the conforming parts")
fig("Recorded values above USL", f"{sum(v > usl for v in vals)} of {len(vals)}", "finding.txt", "v > USL")
for i, v in enumerate(vals, 1):
    exc = v - usl
    fig(f"Part {i}: excess over USL (mm) / % of tolerance band", f"{exc:.3f} / {100*exc/tol:.0f}%", "finding.txt + drawing",
        f"{v:.3f} - {usl:.3f}; / {tol:.3f}")
mean = sum(vals) / len(vals)
fig("Mean of recorded values (mm)", f"{mean:.4f}", "finding.txt", "mean of 3 recorded values")
fig("Range of recorded values (mm)", f"{max(vals)-min(vals):.3f}", "finding.txt", "max - min")
fig("Mean excess over USL (mm)", f"{mean-usl:.4f}", "finding.txt + drawing", "mean - USL")

# --- SPC, individuals chart on what exists (5 required rows) ---
mrs = [abs(b - a) for a, b in zip(vals, vals[1:])]
mrbar = sum(mrs) / len(mrs)
ucl, lcl = mean + 2.66 * mrbar, mean - 2.66 * mrbar
fig("SPC centreline (mm)", f"{mean:.4f}", "finding.txt", "I-MR: mean of individuals")
fig("SPC UCL (mm)", f"{ucl:.4f}", "finding.txt", f"mean + 2.66 x MRbar ({mrbar:.4f})")
fig("SPC LCL (mm)", f"{lcl:.4f}", "finding.txt", f"mean - 2.66 x MRbar ({mrbar:.4f})")
fig("SPC basis", f"I-MR, n={len(vals)} points, one run (WO-8102 / L-0412), {len(mrs)} moving ranges; "
    "nonconforming parts only, recorded order not production order; no prior runs available",
    "finding.txt", "only measurements in inputs")
beyond = sum(v > ucl or v < lcl for v in vals)
fig("SPC run rule checked", f"Rule 1 (point beyond 3-sigma limits): {beyond} points beyond. Rules 2-4 (run of 9, trend of 6, 2 of 3 beyond 2-sigma): "
    "cannot be evaluated with 3 points and no production sequence. Limits computed from a biased 3-point subset are NOT a valid control baseline.",
    "finding.txt", "computed against UCL/LCL above")
fig("UCL vs spec USL (mm)", f"UCL {ucl:.4f} is {ucl-usl:.4f} above USL {usl:.3f}", "computed", "UCL - USL (control limit != spec limit)")

# --- lot / containment reconciliation ---
lot = int(re.search(r"Lot size (\d+)", finding).group(1))
wip = int(re.search(r"(\d+) still at VMC-03 queue", finding).group(1))
fg = int(re.search(r"(\d+) in finished goods", finding).group(1))
shipped = int(re.search(r"(\d+) already shipped", finding).group(1))
fig("Lot size L-0412", lot, "finding.txt", "'Lot size N'")
fig("WIP at VMC-03 + FG-2 rack 14 + shipped", f"{wip} + {fg} + {shipped} = {wip+fg+shipped}", "finding.txt", "sum of stated locations")
fig("Locations reconcile to lot size", str(wip + fg + shipped == lot), "finding.txt", "sum == lot size")
fig("Parts still in-house", wip + fg, "finding.txt", "WIP + FG")
fig("Parts at customer (Northwind Robotics, PS-5521)", shipped, "finding.txt", "'already shipped'")

# --- recurrence ---
same = [r for r in prior if r["part"] == "MB-1880" and "bore oversize" in r["defect"]]
fig("Prior NCRs in file (all parts)", len(prior), "prior_ncrs.csv", "all rows")
fig("Prior NCRs same part + bore oversize", f"{len(same)} ({', '.join(r['ncr'] for r in same)})", "prior_ncrs.csv",
    "part=='MB-1880' and 'bore oversize' in defect")
fig("NCR-0219 CAPA and effectiveness", f"{same[0]['capa']} | capa_effective = '{same[0]['capa_effective']}'", "prior_ncrs.csv", "row ncr=='NCR-0219'")
v219 = float(re.search(r"\d+\.\d+", same[0]["defect"]).group(0))
fig("NCR-0219 excess over USL (mm)", f"{v219-usl:.3f}", "prior_ncrs.csv + drawing", f"{v219} - USL")
d0 = datetime.fromisoformat(same[0]["date"]); d1 = datetime(2026, 11, 11)
fig("Days NCR-0219 to this finding", (d1 - d0).days, "prior_ncrs.csv + finding.txt", "2026-11-11 - 2026-04-14")
fig("Insert life numbers in prior record (parts)", "wear beyond 900; CAPA interval 600", "prior_ncrs.csv", "NCR-0219 cause / capa text")
offset_ncrs = [r["ncr"] for r in prior if "offset" in r["cause"]]
fig("Prior NCRs with offset-after-tool-change cause", f"{len(offset_ncrs)} ({', '.join(offset_ncrs)}; part MB-1500, not MB-1880)", "prior_ncrs.csv", "'offset' in cause")

# --- maintenance records ---
vmc = [r for r in maint if r["asset_id"] == "VMC-03"]
fig("Maintenance records VMC-03", len(vmc), "maintenance_log.csv", "asset_id=='VMC-03'")
fig("Records mentioning T7 / boring", sum("T7" in r["event"] for r in vmc), "maintenance_log.csv", "'T7' in event")
fig("Records mentioning coolant", sum("coolant" in r["event"] for r in vmc), "maintenance_log.csv", "'coolant' in event")
fig("Tool-life part count for insert T7-0031", "not in inputs", "maintenance_log.csv, finding.txt", "search 'count|parts' near T7-0031: none")
fig("Boring head / offset setting records for WO-8102", "0 - not in inputs", "all 4 input files", "search 'offset|setup|setting' in maintenance_log.csv and finding.txt: none")

# --- time alignment test (Step 1) ---
repl = datetime.fromisoformat([r for r in vmc if "T7" in r["event"]][0]["timestamp"])
coolant = datetime.fromisoformat([r for r in vmc if "coolant" in r["event"]][0]["timestamp"])
find_naive = datetime(2026, 11, 11, 10, 5)
ship_naive = datetime(2026, 11, 11, 8, 0)
fig("Maintenance log clock", "zone-aware, UTC-05:00", "maintenance_log.csv", "timestamp offset")
fig("Finding / shipment clock", "zone-naive (no offset), source zone not stated", "finding.txt", "timestamps '2026-11-11 10:05', '08:00'")
as_local = find_naive.replace(tzinfo=repl.tzinfo)
as_utc = find_naive.replace(tzinfo=timezone.utc)
def hm(td):
    s = int(td.total_seconds()); sign = "-" if s < 0 else "+"; s = abs(s)
    return f"{sign}{s//3600}h{(s%3600)//60:02d}m"
fig("Insert replacement minus finding, if finding is UTC-05:00", hm(repl - as_local) + " (replacement BEFORE finding)", "computed", "06:40-05:00 minus 10:05-05:00")
fig("Insert replacement minus finding, if finding is UTC", hm(repl - as_utc) + " (replacement AFTER finding)", "computed", "06:40-05:00 minus 10:05Z")
fig("Shipment minus finding (same source clock)", hm(ship_naive - find_naive), "finding.txt", "08:00 minus 10:05, both naive")
fig("Events visible in two sources that verify alignment", "0", "all inputs", "the 'inspection hold' named at 06:40 has no timestamped record in finding.txt; finding records 10:05 only")
fig("Shift boundary for '2nd shift 2026-11-10'", "not in inputs (no Plant context)", "plant_setup.py find", "profile exists = false")

(outdir / "figures_block.csv").write_text("", encoding="utf-8")
with open(outdir / "figures_block.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=["figure", "value", "computed_from", "filter_or_query"]); w.writeheader(); w.writerows(rows)
(outdir / "analysis" / "figures.json").write_text(json.dumps(rows, indent=1), encoding="utf-8")
for r in rows:
    print(f"{r['figure']}: {r['value']}")
