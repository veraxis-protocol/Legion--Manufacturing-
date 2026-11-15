"""MB-1880 oversize bore - computed pattern checks. Reads inputs/quality, writes out/figures.csv + out/analysis.json.
Usage: python -I scripts/analyze_mb1880.py <inputs/quality dir> <out dir>"""
import csv, json, sys, statistics as st
from datetime import datetime
from pathlib import Path

src, out = Path(sys.argv[1]), Path(sys.argv[2])

def read(name):
    lines = [l for l in (src / name).read_text(encoding="utf-8").splitlines() if l and not l.startswith("#")]
    return list(csv.DictReader(lines))

insp = read("inspection_measurements.csv")
maint = read("maintenance_log.csv")
prior = read("prior_ncrs.csv")
for r in insp:
    r["t"] = datetime.fromisoformat(r["timestamp"]); r["x"] = float(r["bore_dia_mm"]); r["seq"] = int(r["part_seq"])
for m in maint:
    m["t"] = datetime.fromisoformat(m["timestamp"])
insp.sort(key=lambda r: r["t"])

LSL, USL = 22.000, 22.021   # MB-1880 rev B sheet 2 note 4
F = []
def fig(name, value, source, query):
    F.append({"figure": name, "value": value, "computed_from": source, "filter_or_query": query})
    return value
um = lambda v: round(v * 1000, 1)

# ---------- time alignment ----------
offsets = sorted({r["timestamp"][-6:] for r in insp} | {m["timestamp"][-6:] for m in maint})
fig("Distinct UTC offsets across inspection + maintenance timestamps", ";".join(offsets), "both CSVs", "timestamp[-6:]")
naive = sum(1 for r in insp if r["t"].tzinfo is None) + sum(1 for m in maint if m["t"].tzinfo is None)
fig("Zone-naive timestamps", naive, "both CSVs", "tzinfo is None")
chg = [m for m in maint if "insert replaced" in m["event"]][0]
first_new = min((r for r in insp if r["tool_id"] == "T7-0032"), key=lambda r: r["t"])
last_old = max((r for r in insp if r["tool_id"] == "T7-0031"), key=lambda r: r["t"])
gap = (first_new["t"] - chg["t"]).total_seconds() / 60
fig("Anchor: maint insert change -> first T7-0032 inspection (min)", round(gap), "maintenance_log r2; inspection r11", "tool_id=='T7-0032' first row vs event 'insert replaced'")
fig("Anchor ordering consistent (last T7-0031 < change < first T7-0032)", last_old["t"] < chg["t"] < first_new["t"], "both CSVs", "timestamp compare")

# ---------- spec check ----------
oos = [r for r in insp if r["x"] > USL or r["x"] < LSL]
fig("Inspection rows", len(insp), "inspection_measurements.csv", "all data rows")
fig("Rows out of spec (>22.021 or <22.000)", len(oos), "inspection_measurements.csv", "bore_dia_mm outside [22.000,22.021]")
fig("Out-of-spec rows: lots", ";".join(sorted({r['lot'] for r in oos})), "inspection_measurements.csv", "lot of OOS rows")
fig("Out-of-spec rows: part_seq", ";".join(str(r['seq']) for r in oos), "inspection_measurements.csv", "part_seq of OOS rows")
fig("Max bore measured (mm)", max(r["x"] for r in insp), "inspection_measurements.csv", "max(bore_dia_mm)")
fig("Max bore excess over USL (um)", um(max(r["x"] for r in insp) - USL), "inspection_measurements.csv", "max - 22.021")

# ---------- SPC: I-MR on T7-0031 points ----------
old = [r for r in insp if r["tool_id"] == "T7-0031"]
xs = [r["x"] for r in old]
mr = [abs(b - a) for a, b in zip(xs, xs[1:])]
cl = st.mean(xs); mrbar = st.mean(mr); sig = mrbar / 1.128
ucl, lcl = cl + 3 * sig, cl - 3 * sig
fig("SPC basis", f"Individuals (I-MR) chart, n={len(xs)} points, lots {','.join(sorted({r['lot'] for r in old}))}, insert T7-0031 only, sigma=MRbar/1.128", "inspection_measurements.csv", "tool_id=='T7-0031'")
fig("SPC centreline (mm)", round(cl, 4), "same computation", "mean(x)")
fig("SPC MR-bar (um)", um(mrbar), "same computation", "mean(|x_i - x_i-1|)")
fig("SPC sigma-hat (um)", um(sig), "same computation", "MRbar/1.128")
fig("SPC UCL (mm)", round(ucl, 4), "same computation", "CL + 3 sigma")
fig("SPC LCL (mm)", round(lcl, 4), "same computation", "CL - 3 sigma")
beyond = [r for r in old if r["x"] > ucl or r["x"] < lcl]
fig("Points beyond control limits", ";".join(f"{r['lot']}#{r['seq']}={r['x']}" for r in beyond) or "none", "same computation", "x>UCL or x<LCL")
if beyond:
    fig("Max point minus UCL (um)", um(max(xs) - ucl), "same computation", "max(x) - UCL")
# Rule: trend - longest run of strictly increasing consecutive points
run = best = 1
for a, b in zip(xs, xs[1:]):
    run = run + 1 if b > a else 1; best = max(best, run)
fig("Run rule checked: trend (>=6 consecutive increasing, Nelson rule 3)", f"longest increasing run = {best} points -> {'FIRED' if best >= 6 else 'not fired'}", "same computation", "consecutive x_i > x_i-1")
run = 1
for i in range(1, len(xs)):
    run = run + 1 if xs[i] > xs[i-1] else 1
    if run == 6:
        r6 = old[i]; break
fig("Trend rule first fires at (point, time)", f"{r6['lot']}#{r6['seq']}={r6['x']} at {r6['timestamp']}", "same computation", "6th consecutive increasing point")
fig("Hours from trend-rule signal to first out-of-spec part", round((oos[0]["t"] - r6["t"]).total_seconds() / 3600, 2), "same computation", "t(first OOS) - t(rule fires)")
# Rule: 9 same side of CL
side = run2 = best2 = 0
for x in xs:
    s = 1 if x > cl else -1 if x < cl else 0
    run2 = run2 + 1 if s == side and s != 0 else 1; side = s; best2 = max(best2, run2)
fig("Run rule checked: 9 on one side of CL (Nelson rule 2)", f"longest same-side run = {best2} -> {'FIRED' if best2 >= 9 else 'not fired'}", "same computation", "sign(x - CL)")
# 2 of 3 beyond 2 sigma same side
z = [(x - cl) / sig for x in xs]
r5 = any(sum(1 for v in z[i:i+3] if v > 2) >= 2 or sum(1 for v in z[i:i+3] if v < -2) >= 2 for i in range(len(z) - 2))
fig("Run rule checked: 2 of 3 beyond 2 sigma (Nelson rule 5)", "FIRED" if r5 else "not fired", "same computation", "z=(x-CL)/sigma")
fig("Note: limits computed on a drifting series", "CL/limits are inflated by the trend itself; the trend rule is the valid signal", "interpretation", "-")

# Drift magnitude and slope vs time
t0 = old[0]["t"]
hrs = [(r["t"] - t0).total_seconds() / 3600 for r in old]
mx, my = st.mean(hrs), cl
slope = sum((h - mx) * (x - my) for h, x in zip(hrs, xs)) / sum((h - mx) ** 2 for h in hrs)
ssr = sum((x - (my + slope * (h - mx))) ** 2 for h, x in zip(hrs, xs)); sst = sum((x - my) ** 2 for x in xs)
fig("Total drift on T7-0031, first to last point (um)", um(xs[-1] - xs[0]), "inspection_measurements.csv", "T7-0031 last x - first x")
fig("Elapsed time on T7-0031 measured span (h)", round(hrs[-1], 1), "inspection_measurements.csv", "last t - first t")
fig("Linear slope bore vs time on T7-0031 (um/h)", round(slope * 1000, 3), "same computation", "OLS x ~ hours")
fig("R^2 bore vs time on T7-0031", round(1 - ssr / sst, 3), "same computation", "1-SSR/SST")
# within-lot slopes per part
for lot in sorted({r["lot"] for r in old}):
    rows = [r for r in old if r["lot"] == lot]
    if len(rows) >= 2:
        a, b = rows[0], rows[-1]
        fig(f"Within-lot wear rate {lot} (um/part)", round((b["x"] - a["x"]) * 1000 / (b["seq"] - a["seq"]), 3), "inspection_measurements.csv", f"lot=={lot}, (x_last-x_first)/(seq_last-seq_first)")
# Extrapolate where L-0411 crosses USL using its own within-lot rate and L-0412 rate
l11 = [r for r in old if r["lot"] == "L-0411"]
rate11 = (l11[-1]["x"] - l11[0]["x"]) / (l11[-1]["seq"] - l11[0]["seq"])
cross11 = l11[-1]["seq"] + (USL - l11[-1]["x"]) / rate11
fig("L-0411 headroom to USL at last measured part #70 (um)", um(USL - l11[-1]["x"]), "inspection_measurements.csv", "22.021 - x(L-0411 #70)")
fig("L-0411 projected USL crossing at its own rate (part_seq)", round(cross11), "same computation", "70 + headroom/rate_L-0411 (linear extrapolation, NOT a measurement)")
l12 = [r for r in old if r["lot"] == "L-0412"]
fig("L-0412 first part (#1) bore vs USL (um over)", um(l12[0]["x"] - USL), "inspection_measurements.csv", "x(L-0412 #1) - 22.021")
# Post-change
fig("First part on new insert T7-0032 (mm)", first_new["x"], "inspection_measurements.csv r11", "tool_id=='T7-0032'")
fig("Step change at insert replacement (um)", um(first_new["x"] - last_old["x"]), "inspection_measurements.csv", "x(first T7-0032) - x(last T7-0031)")
fig("First part on T7-0031 (L-0409 #1, mm)", xs[0], "inspection_measurements.csv r1", "first T7-0031 row")

# ---------- clustering vs base rate ----------
def cluster(key):
    res = {}
    for k in sorted({r[key] for r in insp}):
        n = sum(1 for r in insp if r[key] == k); o = sum(1 for r in oos if r[key] == k)
        res[k] = (o, n)
    return res
for key in ["lot", "shift", "operator", "machine", "tool_id"]:
    c = cluster(key)
    fig(f"Cluster by {key}: OOS/sampled", "; ".join(f"{k} {o}/{n}" for k, (o, n) in c.items()), "inspection_measurements.csv", f"group by {key}")
# shift-boundary continuity: shift 2 evening vs next shift 1 morning (no overnight reset => not thermal)
pairs = []
for a, b in zip(old, old[1:]):
    if a["shift"] != b["shift"]:
        pairs.append(f"{a['lot']}#{a['seq']}(s{a['shift']})={a['x']} -> {b['lot']}#{b['seq']}(s{b['shift']})={b['x']} ({um(b['x']-a['x']):+} um)")
fig("Shift-boundary transitions on T7-0031", " | ".join(pairs), "inspection_measurements.csv", "consecutive rows with shift change")
fig("Shift vs operator confounded", all((r["shift"] == "1") == (r["operator"] == "OP-11") for r in insp), "inspection_measurements.csv", "shift==1 <=> operator==OP-11 for every row")
fig("Tool changes recorded on T7-0031 rows after first", sum(1 for r in old[1:] if r["tool_change_since_last"] == "yes"), "inspection_measurements.csv", "tool_id=='T7-0031' and tool_change_since_last=='yes', excluding first row")
fig("Lots run on insert T7-0031", len({r['lot'] for r in old}), "inspection_measurements.csv", "distinct lot where tool_id=='T7-0031'")
min_parts = sum(max(r["seq"] for r in old if r["lot"] == l) for l in {r['lot'] for r in old})
fig("Parts on T7-0031 - LOWER BOUND from highest sampled part_seq per lot", min_parts, "inspection_measurements.csv", "sum over lots of max(part_seq); true count needs WO quantities")
fig("Parts on T7-0031 if L-0409..L-0411 were also 300 (assumption, unverified)", 3 * 300 + 180, "assumption", "3x300 + L-0412 #180")

# ---------- maintenance correlation ----------
for m in maint:
    before = [r for r in insp if r["t"] < m["t"]]
    fig(f"Maint event {m['timestamp']} '{m['event']}': inspection rows before / after", f"{len(before)}/{len(insp)-len(before)}", "maintenance_log.csv + inspection", "t < event time")
coolant = [m for m in maint if "coolant" in m["event"]][0]
fig("Hours from coolant change to first measurement", round((insp[0]["t"] - coolant["t"]).total_seconds() / 3600, 1), "both CSVs", "first insp t - coolant event t")
fig("Coolant changes recorded after 2026-11-08 16:00 (incl. reversal)", sum(1 for m in maint if "coolant" in m["event"] and m["t"] > coolant["t"]), "maintenance_log.csv", "event contains 'coolant' and t > 2026-11-08T16:00")
fig("Maintenance records on VMC-03 in log", sum(1 for m in maint if m["asset_id"] == "VMC-03"), "maintenance_log.csv", "asset_id=='VMC-03'")

# ---------- recurrence ----------
same = [p for p in prior if p["part"] == "MB-1880" and "bore oversize" in p["defect"]]
fig("Prior NCRs same part + 'bore oversize'", ";".join(p["ncr"] for p in same), "prior_ncrs.csv", "part=='MB-1880' and defect contains 'bore oversize'")
fig("Prior NCRs total in file", len(prior), "prior_ncrs.csv", "all rows")
for p in same:
    fig(f"{p['ncr']} CAPA and effectiveness", f"{p['capa']} | capa_effective={p['capa_effective']}", "prior_ncrs.csv", f"ncr=='{p['ncr']}'")

(out / "figures.csv").write_text("", encoding="utf-8")
with open(out / "MB-1880_figures_block.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=["figure", "value", "computed_from", "filter_or_query"]); w.writeheader(); w.writerows(F)
(out / "figures.csv").unlink()
for row in F:
    print(f"{row['figure']} = {row['value']}")
