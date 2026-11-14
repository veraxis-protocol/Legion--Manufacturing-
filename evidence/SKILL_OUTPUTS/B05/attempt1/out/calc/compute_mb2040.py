"""Figures block for the MB-2040 quote build. Every number used in the outputs is computed here
from the input CSVs. Run from the work folder: python -I out/calc/compute_mb2040.py inputs out/calc/figures_MB-2040.json"""
import csv, json, math, sys, pathlib
from datetime import date

inp = pathlib.Path(sys.argv[1]); out = pathlib.Path(sys.argv[2])


def rows(p):
    with open(p, encoding="utf-8") as f:
        lines = [l for l in f if not l.startswith("#")]
    return list(csv.DictReader(lines))


routings = rows(inp / "cost/routings.csv")
jobs = rows(inp / "cost/closed_jobs.csv")
pos = rows(inp / "cost/purchase_orders.csv")
F = []


def fig(name, value, src, flt):
    F.append({"figure": name, "value": value, "computed_from": src, "filter_or_arithmetic": flt})
    return value


QTYS = [250, 500, 1000]
THRESH = 0.15  # default threshold, not plant-set

# ---- counts / negative claims
fig("Routing rows for MB-2040 (any rev)", sum(r["part"] == "MB-2040" for r in routings), "cost/routings.csv", 'part == "MB-2040"')
fig("Closed-job rows for MB-2040 (any rev)", sum(r["part"] == "MB-2040" for r in jobs), "cost/closed_jobs.csv", 'part == "MB-2040"')
fig("Routing rows for MB-1880 rev B", sum(r["part"] == "MB-1880" and r["rev"] == "B" for r in routings), "cost/routings.csv", 'part == "MB-1880" and rev == "B"')
fig("Closed-job rows for MB-1880", sum(r["part"] == "MB-1880" for r in jobs), "cost/closed_jobs.csv", 'part == "MB-1880"')
wos = sorted({r["work_order"] for r in jobs if r["part"] == "MB-1880"})
fig("Distinct closed work orders, MB-1880", "%d (%s)" % (len(wos), ", ".join(wos)), "cost/closed_jobs.csv", 'distinct work_order where part == "MB-1880"')
dates = sorted({r["closed_date"] for r in jobs})
fig("Closed-date span of MB-1880 work orders", "%s to %s" % (dates[0], dates[-1]), "cost/closed_jobs.csv", "min/max closed_date")
fig("Aluminium plate PO lines (item AL6061-PL-0.5)", sum(p["item"] == "AL6061-PL-0.5" for p in pos), "cost/purchase_orders.csv", 'item == "AL6061-PL-0.5"')
fig("Anodize PO lines (item OSP-ANOD-II-BLK)", sum(p["item"] == "OSP-ANOD-II-BLK" for p in pos), "cost/purchase_orders.csv", 'item == "OSP-ANOD-II-BLK"')
fig("Prior Northwind orders / quotes in inputs", "0 - no sales-order or quote-history file in inputs", "inputs folder listing", "no file of that kind present; no ERP searched")

# ---- scrap
per_wo = {}
for r in jobs:
    per_wo[r["work_order"]] = (int(r["qty_completed"]), int(r["qty_scrapped"]))
for wo, (c, s) in sorted(per_wo.items()):
    fig("Scrap rate %s (scrapped / (completed+scrapped))" % wo, round(s / (c + s), 4), "cost/closed_jobs.csv", "%d / (%d+%d)" % (s, c, s))
tc = sum(c for c, s in per_wo.values()); ts = sum(s for c, s in per_wo.values())
scrap = ts / (tc + ts)
fig("Pooled scrap rate, MB-1880 WOs (allowance used)", round(scrap, 4), "cost/closed_jobs.csv", "%d / (%d+%d), one row per WO" % (ts, tc, ts))

# ---- routing ops (rung 4: similar-part routing)
ops = {}
for r in routings:
    if r["part"] == "MB-1880":
        ops[int(r["op"])] = {"wc": r["work_center"], "desc": r["description"], "setup_min": float(r["setup_min"]),
                             "run_min": float(r["run_min_per_unit"]), "actuals": []}
for r in jobs:
    c = int(r["qty_completed"]); s = int(r["qty_scrapped"])
    ops[int(r["op"])]["actuals"].append({"wo": r["work_order"], "rev": r["rev"], "closed": r["closed_date"],
                                         "setup_min": float(r["actual_setup_min"]),
                                         "run_min_pc": float(r["actual_run_min_total"]) / c,
                                         "run_min_pc_incl_scrap": float(r["actual_run_min_total"]) / (c + s)})

op_table = []
for n, o in sorted(ops.items()):
    row = {"op": n, "wc": o["wc"], "desc": o["desc"], "rung": 4, "setup_min_expected": o["setup_min"], "run_min_expected": o["run_min"]}
    su = [o["setup_min"]] + [a["setup_min"] for a in o["actuals"]]
    ru = [o["run_min"]] + [a["run_min_pc"] for a in o["actuals"]]
    row["setup_min_low"], row["setup_min_high"] = min(su), max(su)
    row["run_min_low"], row["run_min_high"] = round(min(ru), 3), round(max(ru), 3)
    row["cross_checks"] = []
    for a in o["actuals"]:
        vs = (a["setup_min"] - o["setup_min"]) / o["setup_min"]
        vr = (a["run_min_pc"] - o["run_min"]) / o["run_min"]
        ps = abs(vs) <= 0.01 and abs(vr) <= 0.01
        cc = dict(a)
        cc.update({"run_min_pc": round(a["run_min_pc"], 3), "run_min_pc_incl_scrap": round(a["run_min_pc_incl_scrap"], 3),
                   "setup_var": round(vs, 4), "run_var": round(vr, 4), "setup_flag": abs(vs) > THRESH, "run_flag": abs(vr) > THRESH,
                   "actuals_confidence": "probable_standard" if ps else "recorded"})
        row["cross_checks"].append(cc)
        fig("Op %d %s actual run min/pc" % (n, a["wo"]), cc["run_min_pc"], "cost/closed_jobs.csv", "actual_run_min_total / qty_completed")
        fig("Op %d %s setup variance vs MB-1880 routing" % (n, a["wo"]), "%+.1f%%%s" % (vs * 100, " FLAG" if abs(vs) > THRESH else ""),
            "closed_jobs vs routings", "(%g - %g) / %g" % (a["setup_min"], o["setup_min"], o["setup_min"]))
        fig("Op %d %s run variance vs MB-1880 routing" % (n, a["wo"]), "%+.1f%%%s" % (vr * 100, " FLAG" if abs(vr) > THRESH else ""),
            "closed_jobs vs routings", "(%s - %g) / %g" % (cc["run_min_pc"], o["run_min"], o["run_min"]))
        fig("Op %d %s actuals_confidence" % (n, a["wo"]), cc["actuals_confidence"], "variance test", "probable_standard if |setup var| and |run var| <= 1%")
    op_table.append(row)

setup_total = sum(o["setup_min"] for o in ops.values())
run_pc = sum(o["run_min"] for o in ops.values())
fig("Setup per job, all ops (MB-1880 routing)", "%g min = %.2f h" % (setup_total, setup_total / 60), "cost/routings.csv", "sum setup_min ops 10-40")
fig("Run per piece, all ops (MB-1880 routing)", "%g min/pc = %.4f h/pc" % (run_pc, run_pc / 60), "cost/routings.csv", "sum run_min_per_unit ops 10-40")

# ---- plate nesting (zero-allowance upper bound)
plate = (12 * 25.4, 48 * 25.4, 0.5 * 25.4); part = (80.0, 120.0, 12.0)
a = math.floor(plate[0] / part[0]) * math.floor(plate[1] / part[1])
b = math.floor(plate[0] / part[1]) * math.floor(plate[1] / part[0])
per_plate = max(a, b)
fig("Blanks per plate, zero cut allowance (upper bound)", per_plate, "spec envelope 120x80 mm; PO plate 12x48 in",
    "max(floor(304.8/80)*floor(1219.2/120)=%d, floor(304.8/120)*floor(1219.2/80)=%d)" % (a, b))
left = plate[1] - 10 * part[1]
fig("Spare length along 48 in for 10 blanks of 120 mm", "%.1f mm (%.2f mm per blank)" % (left, left / 10), "same", "1219.2 - 10*120; / 10")
alt_pp = 3 * 9
fig("Blanks per plate if per-blank allowance > 1.92 mm on the 120 mm direction", alt_pp, "same", "3 across x 9 along")
fig("Plate thickness vs finished thickness", "%.1f mm vs 12 mm (%.1f mm stock)" % (plate[2], plate[2] - 12), "PO description; spec envelope", "0.5*25.4 - 12")

plates = {p["po_number"]: p for p in pos}
p_now = float(plates["PO-30588"]["unit_price_usd"]); p_prev = float(plates["PO-30411"]["unit_price_usd"])
fig("Plate price change PO-30411 -> PO-30588", "%+.2f%%" % ((p_now - p_prev) / p_prev * 100), "cost/purchase_orders.csv", "(%g - %g) / %g" % (p_now, p_prev, p_prev))
for k in ("PO-30411", "PO-30588", "PO-30602"):
    p = plates[k]
    d = (date.fromisoformat(p["received_date"]) - date.fromisoformat(p["po_date"])).days
    fig("%s PO-to-receipt days" % k, d, "cost/purchase_orders.csv", "%s - %s" % (p["received_date"], p["po_date"]))
anod = float(plates["PO-30602"]["unit_price_usd"])

breaks = []
for q in QTYS:
    starts = math.ceil(q / (1 - scrap))
    n_pl = math.ceil(starts / per_plate); n_pl_alt = math.ceil(starts / alt_pp)
    mat = n_pl * p_now; mat_alt = n_pl_alt * p_now
    lots = math.ceil(starts / 300)
    run_h = starts * run_pc / 60
    wc = {}
    for o in ops.values():
        w = wc.setdefault(o["wc"], {"setup_h": 0.0, "run_h": 0.0})
        w["setup_h"] += o["setup_min"] / 60; w["run_h"] += starts * o["run_min"] / 60
    br = {"qty": q, "starts": starts, "plates": n_pl, "plates_if_27": n_pl_alt,
          "material_usd": round(mat, 2), "material_usd_per_good_pc": round(mat / q, 4),
          "material_usd_if_27": round(mat_alt, 2), "material_usd_per_good_pc_if_27": round(mat_alt / q, 4),
          "anodize_lots": lots, "anodize_usd": round(lots * anod, 2), "anodize_usd_per_good_pc": round(lots * anod / q, 4),
          "setup_h": round(setup_total / 60, 3), "setup_min_per_good_pc": round(setup_total / q, 4),
          "run_h": round(run_h, 2), "work_h_total": round(setup_total / 60 + run_h, 2),
          "by_work_center": {k: {"setup_h": round(v["setup_h"], 3), "run_h": round(v["run_h"], 2)} for k, v in wc.items()}}
    breaks.append(br)
    fig("Q%d: starts incl. scrap allowance" % q, starts, "qty, pooled scrap", "ceil(%d / (1 - %.4f))" % (q, scrap))
    fig("Q%d: plates (30/plate)" % q, n_pl, "starts", "ceil(%d/30)" % starts)
    fig("Q%d: material cost at PO-30588 (30/plate)" % q, "$%.2f ($%.4f/good pc)" % (mat, mat / q), "PO-30588 unit price", "%d x %g; / %d" % (n_pl, p_now, q))
    fig("Q%d: plates (27/plate case)" % q, n_pl_alt, "starts", "ceil(%d/27)" % starts)
    fig("Q%d: material cost at PO-30588 (27/plate case)" % q, "$%.2f ($%.4f/good pc)" % (mat_alt, mat_alt / q), "PO-30588 unit price", "%d x %g; / %d" % (n_pl_alt, p_now, q))
    fig("Q%d: anodize lots (<=300 pcs/lot)" % q, lots, "PO-30602 lot definition", "ceil(%d/300)" % starts)
    fig("Q%d: anodize cost at PO-30602" % q, "$%.2f ($%.4f/good pc)" % (lots * anod, lots * anod / q), "PO-30602 unit price", "%d x %g; / %d" % (lots, anod, q))
    fig("Q%d: setup minutes per good piece" % q, round(setup_total / q, 4), "routing setup total", "%g / %d" % (setup_total, q))
    fig("Q%d: run hours (on starts)" % q, round(run_h, 2), "routing run/pc", "%d x %g / 60" % (starts, run_pc))
    fig("Q%d: work content hours (setup + run)" % q, round(setup_total / 60 + run_h, 2), "routing", "%.3f + %.2f" % (setup_total / 60, run_h))
    for k, v in br["by_work_center"].items():
        fig("Q%d: %s hours setup / run" % (q, k), "%s / %s" % (v["setup_h"], v["run_h"]), "routing by work_center", "sum per work_center")

json.dump({"scrap_rate": round(scrap, 4), "ops": op_table, "breaks": breaks, "plate_price": p_now, "anodize_lot": anod,
           "figures": F}, open(out, "w", encoding="utf-8"), indent=2)
for f in F:
    print("| %s | %s | %s | %s |" % (f["figure"], f["value"], f["computed_from"], f["filter_or_arithmetic"]))
