"""Computed figures for the MB-1880 bore NCR chain.
Run from the task folder:  python -I out/analysis/compute_figures.py inputs/quality out/analysis
"""
import csv, sys, json, statistics as st
from datetime import datetime
from pathlib import Path

src, out = Path(sys.argv[1]), Path(sys.argv[2])


def read(name):
    lines = [l for l in (src / name).read_text(encoding="utf-8").splitlines()
             if l.strip() and not l.startswith("#")]
    return list(csv.DictReader(lines))


insp = read("inspection_measurements.csv")
mx = read("maintenance_log.csv")
prior = read("prior_ncrs.csv")
for r in insp:
    r["t"] = datetime.fromisoformat(r["timestamp"])
    r["x"] = float(r["bore_dia_mm"])
    r["seq"] = int(r["part_seq"])
for r in mx:
    r["t"] = datetime.fromisoformat(r["timestamp"])
insp.sort(key=lambda r: r["t"])
USL, LSL = 22.021, 22.000
F = []


def fig(name, value, frm, q):
    F.append((name, value, frm, q))
    return value


fig("Inspection rows (all)", len(insp), "inspection_measurements.csv", "all data rows")
zones = sorted({r["t"].utcoffset().total_seconds() / 3600 for r in insp + mx})
fig("UTC offsets present (inspection + maintenance)", ",".join(f"{z:+.0f}h" for z in zones), "both CSVs", "utcoffset of every timestamp")
fig("Coverage, inspection export", f"{insp[0]['timestamp']} to {insp[-1]['timestamp']}", "inspection_measurements.csv", "min/max timestamp")
fig("Coverage, maintenance export", f"{min(r['timestamp'] for r in mx)} to {max(r['timestamp'] for r in mx)}", "maintenance_log.csv", "min/max timestamp")

oos = [r for r in insp if r["x"] > USL or r["x"] < LSL]
fig("In-process readings outside 22.000-22.021", f"{len(oos)} of {len(insp)}: " + "; ".join(f"{r['lot']} seq {r['seq']} = {r['x']:.3f}" for r in oos), "inspection_measurements.csv", "bore_dia_mm > 22.021 or < 22.000")
first_oos = oos[0]
fig("First out-of-spec in-process reading", f"{first_oos['timestamp']} {first_oos['lot']} seq {first_oos['seq']} = {first_oos['x']:.3f} ({(first_oos['x'] - USL) * 1000:+.0f} um over USL)", "inspection_measurements.csv", "earliest row with bore > 22.021")
for v in (22.034, 22.031, 22.029):
    fig(f"Final-inspection value {v:.3f} over USL", f"{(v - USL) * 1000:+.0f} um", "finding.txt", "measured - 22.021")
fig("Final-inspection values present in the inspection export", ", ".join(f"{v:.3f}:{'yes' if any(abs(r['x'] - v) < 1e-9 for r in insp) else 'no'}" for v in (22.034, 22.031, 22.029)), "finding.txt vs inspection export", "exact value match")

t31 = [r for r in insp if r["tool_id"] == "T7-0031"]
fig("Readings on insert T7-0031", len(t31), "inspection export", "tool_id == T7-0031")
inc = sum(1 for a, b in zip(t31, t31[1:]) if b["x"] > a["x"])
fig("Increasing steps across T7-0031 readings", f"{inc} of {len(t31) - 1}", "inspection export", "x[i] > x[i-1], T7-0031, time order")

xs = [r["x"] for r in t31]
mrs = [abs(b - a) for a, b in zip(xs, xs[1:])]
cl = st.mean(xs); mrbar = st.mean(mrs); sig = mrbar / 1.128
ucl, lcl = cl + 3 * sig, cl - 3 * sig
fig("SPC centreline (I chart)", f"{cl:.4f} mm", "inspection export", "mean of T7-0031 readings")
fig("SPC UCL (I chart)", f"{ucl:.4f} mm", "inspection export", "CL + 2.66*MRbar")
fig("SPC LCL (I chart)", f"{lcl:.4f} mm", "inspection export", "CL - 2.66*MRbar")
fig("SPC basis", f"Individuals/moving range, n={len(xs)} points, lots L-0409..L-0412 on insert T7-0031, MRbar={mrbar * 1000:.2f} um, sigma_hat={sig * 1000:.2f} um. No stable baseline exists; limits are inflated by the trend itself", "inspection export", "MR of consecutive readings")
beyond = [r for r in t31 if r["x"] > ucl or r["x"] < lcl]
fig("Points beyond I-chart limits", f"{len(beyond)}" + (": " + ", ".join(f"{r['lot']} seq {r['seq']} = {r['x']:.3f}" for r in beyond) if beyond else ""), "computed", "x > UCL or x < LCL")
fig("UCL vs spec USL", f"UCL {ucl:.4f} is {(ucl - USL) * 1000:+.1f} um vs USL 22.021 (control limit, not spec limit)", "computed", "UCL - USL")


def first_trend(points, steps):
    run = 0
    for i in range(1, len(points)):
        run = run + 1 if points[i]["x"] > points[i - 1]["x"] else 0
        if run >= steps:
            return points[i]


fa = first_trend(t31, 5)
fn = first_trend(t31, 6)
fig("Run rule checked: 6 points in a row increasing (AIAG trend rule) - first fires", f"{fa['timestamp']} {fa['lot']} seq {fa['seq']} = {fa['x']:.3f} (in spec)", "computed", "5 consecutive increases")
fig("Run rule checked: Nelson rule 3 (6 consecutive increases) - first fires", f"{fn['timestamp']} {fn['lot']} seq {fn['seq']} = {fn['x']:.3f} (in spec)", "computed", "6 consecutive increases")
lead_h = (first_oos["t"] - fa["t"]).total_seconds() / 3600
fig("Hours from first trend-rule signal to first out-of-spec reading", f"{lead_h:.2f} h", "computed", "first_oos.t - trend_fire.t")
run = best = 0
for r in t31:
    run = run + 1 if r["x"] > cl else 0
    best = max(best, run)
fig("Longest run above centreline", best, "computed", "consecutive x > CL (rule needs 9; not fired)")

t0 = t31[0]["t"]
hrs = [(r["t"] - t0).total_seconds() / 3600 for r in t31]
mh = st.mean(hrs); mxv = st.mean(xs)
slope = sum((h - mh) * (x - mxv) for h, x in zip(hrs, xs)) / sum((h - mh) ** 2 for h in hrs)
fig("Linear drift vs elapsed time, T7-0031", f"{slope * 1000:.3f} um/h (r = {st.correlation(hrs, xs):.3f})", "computed", "OLS bore ~ hours since 2026-11-09T07:10")
for lot in ["L-0409", "L-0410", "L-0411", "L-0412"]:
    p = [r for r in t31 if r["lot"] == lot]
    dh = (p[-1]["t"] - p[0]["t"]).total_seconds() / 3600
    dx = p[-1]["x"] - p[0]["x"]; dn = p[-1]["seq"] - p[0]["seq"]
    fig(f"Within-lot drift {lot} (shift {p[0]['shift']})", f"{dx * 1000:+.0f} um over {dh:.2f} h ({dx / dh * 1000:.2f} um/h) and {dn} parts ({dx / dn * 1000:.3f} um/part)", "computed", f"first vs last reading in {lot}")
a = [r for r in t31 if r["lot"] == "L-0410"][-1]; b = [r for r in t31 if r["lot"] == "L-0411"][0]
fig("Change across overnight idle (L-0410 last -> L-0411 first)", f"{(b['x'] - a['x']) * 1000:+.0f} um over {(b['t'] - a['t']).total_seconds() / 3600:.2f} h", "computed", "readings either side of the night")
a = [r for r in t31 if r["lot"] == "L-0411"][-1]; b = [r for r in t31 if r["lot"] == "L-0412"][0]
frac = (USL - a["x"]) / (b["x"] - a["x"]); tc = a["t"] + (b["t"] - a["t"]) * frac
fig("Interpolated USL crossing (ASSUMES linear drift between readings)", f"{tc.isoformat()} - between {a['lot']} seq {a['seq']} ({a['timestamp']}) and {b['lot']} seq {b['seq']} ({b['timestamp']})", "computed", "interpolate 22.021 between bracketing readings")
fig("L-0411 last reading margin to USL", f"{(USL - a['x']) * 1000:.0f} um", "computed", "22.021 - 22.019")
mins = {lot: max(r["seq"] for r in t31 if r["lot"] == lot) for lot in ["L-0409", "L-0410", "L-0411", "L-0412"]}
mins["L-0412"] = max(mins["L-0412"], 300)
fig("Parts cut on insert T7-0031, floor", f"at least {sum(mins.values())} ({' + '.join(f'{k}:{v}' for k, v in mins.items())}); L-0409..L-0411 = highest part_seq sampled, lot sizes not on file; L-0412 = lot size 300 per finding", "inspection export + finding.txt", "sum")
fig("Parts on T7-0031 before L-0412 seq 1, floor", f"at least {mins['L-0409'] + mins['L-0410'] + mins['L-0411']}", "computed", "highest seq sampled in L-0409..L-0411")
fig("CAPA-071 insert-change interval", "600 parts", "prior_ncrs.csv", "row NCR-0219")
post = [r for r in insp if r["tool_id"] == "T7-0032"]
fig("First reading after insert change", f"{post[0]['timestamp']} {post[0]['lot']} = {post[0]['x']:.3f} (first reading on new T7-0031 was {t31[0]['x']:.3f})", "inspection export", "tool_id == T7-0032")
fig("Step at insert change (last T7-0031 -> first T7-0032)", f"{(post[0]['x'] - t31[-1]['x']) * 1000:+.0f} um", "computed", "")

for key in ("shift", "operator"):
    groups = {}
    for r in insp:
        groups.setdefault(r[key], []).append(r)
    for g, rs in sorted(groups.items()):
        o = sum(1 for r in rs if r["x"] > USL)
        fig(f"Readings by {key} {g}", f"{len(rs)} of {len(insp)} readings ({len(rs) / len(insp):.0%}); {o} of {len(oos)} out-of-spec", "inspection export", f"group by {key}")
conf = all((r["shift"] == "1") == (r["operator"] == "OP-11") for r in insp)
fig("Shift and operator confounded", "yes: every shift-1 reading is OP-11, every shift-2 reading is OP-23" if conf else "no", "inspection export", "cross-tab shift x operator")
res = {}
for r, h in zip(t31, hrs):
    res.setdefault(r["shift"], []).append(r["x"] - (mxv + slope * (h - mh)))
for s, v in sorted(res.items()):
    fig(f"Mean residual from time trend, shift {s}", f"{st.mean(v) * 1000:+.2f} um (n={len(v)})", "computed", "x - OLS fit, T7-0031")
fig("Machines in inspection export", ",".join(sorted({r['machine'] for r in insp})), "inspection export", "distinct machine")
fig("Material lot / heat in inspection export", "absent - no such column", "inspection export header", "column list")
for r in mx:
    fig(f"Maintenance event {r['timestamp']} ({r['asset_id']})", r["event"], "maintenance_log.csv", f"asset_id == {r['asset_id']}")
between = [r for r in mx if t31[0]["t"] < r["t"] < post[0]["t"] and "replaced" not in r["event"]]
fig("Maintenance events during T7-0031 life other than its replacement", len(between), "maintenance_log.csv", "t in (2026-11-09T07:10, 2026-11-11T07:05), event not 'replaced'")
anchor = [r for r in mx if "T7-0032" in r["event"]][0]
fig("Clock anchor: insert replacement (maint) -> first T7-0032 reading (insp)", f"+{(post[0]['t'] - anchor['t']).total_seconds() / 60:.0f} min, expected order", "both CSVs", "event visible in two sources")
same_part = [p for p in prior if p["part"] == "MB-1880"]
fig("Prior NCRs, same part MB-1880", f"{len(same_part)}: " + ", ".join(p["ncr"] for p in same_part), "prior_ncrs.csv", "part == 'MB-1880'")
fig("Prior NCRs, same defect (bore) any part", sum(1 for p in prior if "bore" in p["defect"]), "prior_ncrs.csv", "defect contains 'bore'")
fig("Prior NCRs searchable by machine or supplier/lot", "no - prior_ncrs.csv has no machine, supplier or lot column", "prior_ncrs.csv header", "column list")
fig("Prior NCR rows screened", len(prior), "prior_ncrs.csv", "all rows")
fig("NCR-0219 measured vs this event max", f"22.026 then; 22.034 now ({(22.034 - 22.026) * 1000:+.0f} um)", "prior_ncrs.csv + finding.txt", "")
lot, wip, fg, ship = 300, 120, 150, 30
fig("Lot L-0412 location reconciliation", f"{wip} + {fg} + {ship} = {wip + fg + ship} vs lot size {lot} ({'reconciles' if wip + fg + ship == lot else 'DOES NOT reconcile'})", "finding.txt", "")
fig("Final inspection sample", "3 of 5 above USL; the 2 passing values not recorded", "finding.txt", "")
# finding.txt times are zone-naive; ASSUMED plant local -05:00 (same offset as both CSVs)
from datetime import timedelta, timezone
EST = timezone(timedelta(hours=-5))
found = datetime(2026, 11, 11, 10, 5, tzinfo=EST)
shipped = datetime(2026, 11, 11, 8, 0, tzinfo=EST)
hold = anchor["t"]
fig("'Inspection hold' (maint log) before shipment PS-5521", f"{(shipped - hold).total_seconds() / 60:.0f} min (hold-triggered insert change {hold.isoformat()}, shipment {shipped.isoformat()})", "maintenance_log.csv + finding.txt", "shipped - replacement time (finding time ASSUMED -05:00)")
fig("Shipment PS-5521 before final-inspection finding", f"{(found - shipped).total_seconds() / 60:.0f} min", "finding.txt", "found - shipped")
ref = datetime(2026, 11, 15, 0, 0, tzinfo=EST)
el = ref - found
fig("Elapsed from finding to start of 2026-11-15 (today)", f"at least {el.days} d {el.seconds // 3600} h {(el.seconds % 3600) // 60} min ({el.total_seconds() / 3600:.1f} h)", "finding.txt + session date", "2026-11-15T00:00-05:00 - found_at")
fig("Floor of parts on T7-0031 vs CAPA-071 interval", f"floor {sum(mins.values())} vs 600: {'below - cannot show interval exceeded' if sum(mins.values()) < 600 else 'exceeded'}", "computed", "F31 vs F33")
fig("If L-0409..L-0411 were each 300 (UNVERIFIED hypothetical)", f"{300 * 4} parts on T7-0031; 600 reached during lot {['L-0409', 'L-0410', 'L-0411', 'L-0412'][(600 - 1) // 300]}", "computed", "hypothetical only - lot sizes not on file")

(out / "figures.json").write_text(json.dumps(F, indent=1), encoding="utf-8")
rows = ["| # | Figure | Value | Computed from | Filter or query |", "|---|---|---|---|---|"]
for i, (a_, b_, c_, d_) in enumerate(F, 1):
    rows.append(f"| F{i} | {a_} | {b_} | {c_} | " + (f"`{d_}`" if d_ else "—") + " |")
(out / "figures_block.md").write_text("\n".join(rows) + "\n", encoding="utf-8")
print("\n".join(rows))
