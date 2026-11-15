"""MB-2040 Rev C quote calculation. Every figure in the quote documents comes from this script.
Usage: python -I mb2040_calc.py <inputs_dir> <out_json>
Reads inputs/cost/*.csv. Rates are taken from inputs/rates_memo.txt (finance memo 2026-10-01) and
are hard-coded below with that citation because the memo is prose, not a table.
"""
import csv, json, math, sys, statistics
from pathlib import Path

inp = Path(sys.argv[1]); out = Path(sys.argv[2])

def rows(p):
    with open(p, newline="") as f:
        lines = [l for l in f if not l.startswith("#")]
    return list(csv.DictReader(lines))

routing = rows(inp / "cost/routings.csv")
actuals = rows(inp / "cost/closed_jobs.csv")
pos = rows(inp / "cost/purchase_orders.csv")

F = {}  # figures block: name -> {value, basis}
def fig(name, value, basis):
    F[name] = {"value": value, "basis": basis}
    return value

# ---- rates (rates_memo.txt line 2-3) ----
RATE = {"MILL-V": 95.0, "MILL-H": 145.0, "TURN": 85.0, "INSP": 60.0}
MAT_MARKUP, OSP_MARKUP, MARGIN = 0.12, 0.10, 0.18

QTYS = [250, 500, 1000]  # rfq_email.txt line 10

# ---- counts ----
fig("routing_rows_MB1880_revB", len([r for r in routing if r["part"] == "MB-1880"]), "routings.csv rows where part==MB-1880")
fig("routing_rows_MB2040", len([r for r in routing if r["part"] == "MB-2040"]), "routings.csv rows where part==MB-2040")
wos = sorted({a["work_order"] for a in actuals if a["part"] == "MB-1880"})
fig("closed_WOs_MB1880", len(wos), "distinct work_order in closed_jobs.csv where part==MB-1880: " + ", ".join(wos))
fig("closed_WOs_MB2040", len({a["work_order"] for a in actuals if a["part"] == "MB-2040"}), "closed_jobs.csv where part==MB-2040")
fig("actuals_date_range", [min(a["closed_date"] for a in actuals), max(a["closed_date"] for a in actuals)], "min/max closed_date")
fig("plate_POs", len([p for p in pos if p["item"] == "AL6061-PL-0.5"]), "purchase_orders.csv item==AL6061-PL-0.5")

# ---- scrap rate from actuals (one row per WO; scrap repeated per op row) ----
wo = {}
for a in actuals:
    wo[a["work_order"]] = (int(a["qty_completed"]), int(a["qty_scrapped"]))
good = sum(v[0] for v in wo.values()); scr = sum(v[1] for v in wo.values())
for w, (g, s) in wo.items():
    fig(f"scrap_rate_{w}", round(s / (g + s), 5), f"{s}/({g}+{s})")
scrap = fig("scrap_rate_pooled", scr / (good + scr), f"{scr}/({good}+{scr}) over {', '.join(wo)}")

# ---- hours per op ----
rt = {int(r["op"]): r for r in routing if r["part"] == "MB-1880"}
ops = []
for op, r in sorted(rt.items()):
    rs, rr = float(r["setup_min"]), float(r["run_min_per_unit"])
    acts = [a for a in actuals if int(a["op"]) == op and a["part"] == "MB-1880"]
    a_setup = [float(a["actual_setup_min"]) for a in acts]
    a_run_started = [float(a["actual_run_min_total"]) / (int(a["qty_completed"]) + int(a["qty_scrapped"])) for a in acts]
    a_run_good = [float(a["actual_run_min_total"]) / int(a["qty_completed"]) for a in acts]
    rec = {"op": op, "wc": r["work_center"], "desc": r["description"], "routing_setup_min": rs, "routing_run_min": rr,
           "actuals": [{"wo": a["work_order"], "setup_min": float(a["actual_setup_min"]),
                        "run_min_per_started": round(float(a["actual_run_min_total"]) / (int(a["qty_completed"]) + int(a["qty_scrapped"])), 4),
                        "run_min_per_good": round(float(a["actual_run_min_total"]) / int(a["qty_completed"]), 4),
                        "closed": a["closed_date"]} for a in acts]}
    if acts:
        # probable_standard check: actual within 1% of routing standard
        ps = [abs(x - rr) / rr <= 0.01 for x in a_run_started] + [abs(x - rs) / rs <= 0.01 for x in a_setup]
        rec["probable_standard"] = any(ps)
        rec["setup"] = {"low": min(a_setup + [rs]), "exp": statistics.median(a_setup), "high": max(a_setup + [rs]),
                        "exp_src": "median of MB-1880 actuals " + ", ".join(x["wo"] for x in rec["actuals"])}
        rec["run"] = {"low": min(a_run_started + [rr]), "exp": statistics.median(a_run_started), "high": max(a_run_started + [rr]),
                      "exp_src": "median of MB-1880 actuals per started piece"}
        rec["variance_vs_routing"] = {x["wo"]: {"setup": round((x["setup_min"] - rs) / rs, 4),
                                               "run": round((x["run_min_per_started"] - rr) / rr, 4)} for x in rec["actuals"]}
        for w, v in rec["variance_vs_routing"].items():
            fig(f"var_op{op}_{w}", v, "(actual - MB-1880 routing)/routing; run per started piece")
    else:
        rec["probable_standard"] = None
        rec["setup"] = {"low": rs, "exp": rs, "high": rs, "exp_src": "MB-1880 Rev B routing (no actuals; no spread available)"}
        rec["run"] = {"low": rr, "exp": rr, "high": rr, "exp_src": "MB-1880 Rev B routing (no actuals; no spread available)"}
    ops.append(rec)

# ---- material ----
plate_po = max((p for p in pos if p["item"] == "AL6061-PL-0.5"), key=lambda p: p["po_date"])
plate_price = float(plate_po["unit_price_usd"])
older = [p for p in pos if p["item"] == "AL6061-PL-0.5" and p is not plate_po][0]
fig("plate_price_change", round((plate_price - float(older["unit_price_usd"])) / float(older["unit_price_usd"]), 4),
    f"({plate_po['po_number']} - {older['po_number']})/{older['po_number']}")
plate_w, plate_l = 12 * 25.4, 48 * 25.4  # 12in x 48in
KERF = 3.0
def blanks(allow):
    bw, bl = 80 + allow, 120 + allow
    a = math.floor((plate_w + KERF) / (bw + KERF)) * math.floor((plate_l + KERF) / (bl + KERF))
    b = math.floor((plate_w + KERF) / (bl + KERF)) * math.floor((plate_l + KERF) / (bw + KERF))
    return max(a, b)
nest = {allow: blanks(allow) for allow in (0, 5, 10)}
fig("blanks_per_plate_by_allowance_mm", nest, "nest 80+a x 120+a mm in 304.8 x 1219.2 mm, 3 mm kerf, best orientation")
BPP = nest[5]
fig("blanks_per_plate_used", BPP, "5 mm allowance case")
fig("stock_thickness_mm", 0.5 * 25.4, "0.5 in plate vs 12 mm finished: 0.7 mm total to face")

# ---- anodize ----
anod_po = [p for p in pos if p["item"] == "OSP-ANOD-II-BLK"][0]
lot_price, LOT = float(anod_po["unit_price_usd"]), 300

def cost_at(q, case):
    starts = math.ceil(q / (1 - scrap))
    plates = math.ceil(starts / BPP)
    mat = plates * plate_price
    mat_m = mat * (1 + MAT_MARKUP)
    lots = math.ceil(q / LOT)
    osp = lots * lot_price
    osp_m = osp * (1 + OSP_MARKUP)
    setup = sum(o["setup"][case] / 60 * RATE[o["wc"]] for o in ops)
    run = sum(o["run"][case] / 60 * RATE[o["wc"]] for o in ops) * starts
    conv = setup + run
    sub = mat_m + osp_m + conv
    price = sub / (1 - MARGIN)
    margin = price - sub
    alt_price = mat_m + osp_m + conv / (1 - MARGIN)  # sensitivity: margin on conversion only
    hrs = {}
    for o in ops:
        h = hrs.setdefault(o["wc"], {"setup_h": 0, "run_h": 0})
        h["setup_h"] += o["setup"][case] / 60
        h["run_h"] += o["run"][case] * starts / 60
    r2 = lambda x: round(x, 2)
    return {"qty": q, "starts": starts, "scrap_pcs_allowed": starts - q, "plates": plates, "blanks_bought": plates * BPP,
            "material": r2(mat), "material_markup": r2(mat_m - mat), "material_sell_basis": r2(mat_m),
            "anod_lots": lots, "osp": r2(osp), "osp_markup": r2(osp_m - osp), "osp_sell_basis": r2(osp_m),
            "setup_cost": r2(setup), "setup_per_pc": round(setup / q, 4), "run_cost": r2(run), "conversion": r2(conv),
            "subtotal": r2(sub), "margin": r2(margin), "price_total": r2(price), "unit_price": r2(price / q),
            "alt_unit_price_margin_on_conversion_only": r2(alt_price / q),
            "hours_by_wc": {k: {kk: round(vv, 2) for kk, vv in v.items()} for k, v in hrs.items()}}

res = {c: [cost_at(q, c) for q in QTYS] for c in ("low", "exp", "high")}
for c in res:
    for r in res[c]:
        fig(f"unit_price_{c}_{r['qty']}", r["unit_price"], f"case {c}; (subtotal/(1-0.18))/qty")

json.dump({"ops": ops, "plate_po": plate_po, "anod_po": anod_po, "scrap": scrap, "results": res, "figures": F},
          open(out, "w"), indent=1, default=str)
for r in res["exp"]:
    print(json.dumps(r))
for c in ("low", "high"):
    print(c, [r["unit_price"] for r in res[c]])
print(json.dumps(F, indent=0, default=str))
