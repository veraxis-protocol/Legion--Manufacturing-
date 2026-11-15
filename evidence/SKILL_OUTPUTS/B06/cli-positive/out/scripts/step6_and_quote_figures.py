"""Chain 1 step 6 (file-only consolidation + backflush check) and quote-build figures for MB-2040 rev C.
Reads ./inputs/cost and ./inputs/plant as data only. Writes ./out/dataset/*.csv and ./out/figures.json.
Rates are NOT read: no MFG_* variable is set and no confirmed plant rates file exists."""
import csv, json, math, os, statistics, sys

sys.stdout.reconfigure(encoding="utf-8")
ROOT = sys.argv[1]
INP = os.path.join(ROOT, "inputs")
OUT = os.path.join(ROOT, "out")
os.makedirs(os.path.join(OUT, "dataset"), exist_ok=True)

def read(rel):
    with open(os.path.join(INP, rel), newline="", encoding="utf-8") as f:
        lines = [l for l in f if not l.startswith("#")]
    return list(csv.DictReader(lines))

routings = read("cost/routings.csv")
jobs = read("cost/closed_jobs.csv")
pos = read("cost/purchase_orders.csv")
equip = read("plant/equipment.csv")

F = []  # figures block rows
def fig(name, value, src, how):
    F.append({"figure": name, "value": value, "computed_from": src, "filter_or_arithmetic": how})
    return value

fig("Routing rows", len(routings), "routings.csv", "all data rows")
fig("Routing rows for MB-2040 (any rev)", sum(r["part"] == "MB-2040" for r in routings), "routings.csv", "part == 'MB-2040'")
fig("Closed-job operation rows", len(jobs), "closed_jobs.csv", "all data rows")
fig("Closed-job rows for MB-2040", sum(j["part"] == "MB-2040" for j in jobs), "closed_jobs.csv", "part == 'MB-2040'")
wos = sorted({j["work_order"] for j in jobs})
fig("Closed work orders (distinct)", len(wos), "closed_jobs.csv", "distinct work_order: " + ", ".join(wos))
fig("PO rows", len(pos), "purchase_orders.csv", "all data rows")

# ---- join actuals to routing (part, rev, op, work_center) ----
rkey = {(r["part"], r["rev"], r["op"], r["work_center"]): r for r in routings}
actuals = []
for j in jobs:
    k = (j["part"], j["rev"], j["op"], j["work_center"])
    r = rkey.get(k)
    qty = int(j["qty_completed"])
    run_pu = float(j["actual_run_min_total"]) / qty
    row = dict(j)
    row["run_min_per_unit"] = round(run_pu, 4)
    row["routing_match"] = "exact" if r else "unmatched"
    row["routing_run_min_per_unit"] = r["run_min_per_unit"] if r else ""
    row["dev_vs_routing_run"] = round(run_pu / float(r["run_min_per_unit"]) - 1, 4) if r else ""
    actuals.append(row)
fig("Actuals rows joined to routing exactly", sum(a["routing_match"] == "exact" for a in actuals), "closed_jobs x routings", "key (part, rev, op, work_center)")
fig("Actuals rows unmatched", sum(a["routing_match"] != "exact" for a in actuals), "closed_jobs x routings", "same key")
ops_with_actuals = {(a["part"], a["rev"], a["op"]) for a in actuals}
one_sided = [r for r in routings if (r["part"], r["rev"], r["op"]) not in ops_with_actuals]
fig("Routing ops with no actuals (one-sided, class 6)", len(one_sided), "routings vs closed_jobs", "ops: " + ", ".join(r["op"] for r in one_sided))

# ---- backflush check ----
for a in actuals:
    reasons = []
    if a["dev_vs_routing_run"] != "" and abs(a["dev_vs_routing_run"]) <= 0.01:
        reasons.append("run/unit within 1% of routing standard")
    peers = [b for b in actuals if b is not a and (b["part"], b["op"]) == (a["part"], a["op"])]
    for b in peers:
        if abs(b["run_min_per_unit"] / a["run_min_per_unit"] - 1) <= 0.01:
            reasons.append(f"agrees within 1% with {b['work_order']}")
    a["actuals_confidence"] = "probable_standard" if reasons else "recorded"
    a["confidence_reason"] = "; ".join(reasons) or "deviates from routing and from peer WO by more than 1%"
fig("Actuals rows flagged probable_standard", sum(a["actuals_confidence"] == "probable_standard" for a in actuals), "backflush check", "|run/unit ÷ routing − 1| ≤ 1% or peer WO agreement ≤ 1%")
for a in actuals:
    fig(f"{a['work_order']} op{a['op']} run min/pc (actual)", a["run_min_per_unit"], "closed_jobs.csv", f"{a['actual_run_min_total']} ÷ {a['qty_completed']}")
    fig(f"{a['work_order']} op{a['op']} deviation vs MB-1880 routing run", f"{a['dev_vs_routing_run']*100:.1f}%", "closed_jobs x routings", f"{a['run_min_per_unit']} ÷ {a['routing_run_min_per_unit']} − 1")

# scrap
scr = {}
for j in jobs:
    scr[j["work_order"]] = (int(j["qty_completed"]), int(j["qty_scrapped"]))
for wo, (c, s) in scr.items():
    fig(f"{wo} scrap rate", f"{s/(c+s)*100:.2f}%", "closed_jobs.csv", f"{s} ÷ ({c}+{s})")
tc = sum(c for c, s in scr.values()); ts = sum(s for c, s in scr.values())
scrap_rate = ts / (tc + ts)
fig("Pooled scrap rate MB-1880 (material allowance basis)", f"{scrap_rate*100:.2f}%", "closed_jobs.csv", f"{ts} ÷ ({tc}+{ts}), WO-7702 + WO-7811")

# cell map from equipment
wc_cells = {}
for e in equip:
    wc_cells.setdefault(e["work_center"], set()).add(e["cell"])
fig("Work centers mapping to more than one cell", ", ".join(f"{k}: {sorted(v)}" for k, v in wc_cells.items() if len(v) > 1) or "none", "equipment.csv", "distinct cell per work_center")

# ---- hours, rung 4 (similar part MB-1880 rev B), per op ----
TH = 0.15
ops = []
for r in routings:
    acts = [a for a in actuals if a["op"] == r["op"] and a["actuals_confidence"] == "recorded"]
    rs, rr = float(r["setup_min"]), float(r["run_min_per_unit"])
    if acts:
        s_vals = [float(a["actual_setup_min"]) for a in acts]
        r_vals = [a["run_min_per_unit"] for a in acts]
        s_exp, r_exp = statistics.median(s_vals), statistics.median(r_vals)
        s_lo, s_hi = min(s_vals + [rs]), max(s_vals + [rs])
        r_lo, r_hi = min(r_vals + [rr]), max(r_vals + [rr])
        basis = f"median of MB-1880 rev B closed-job actuals ({', '.join(a['work_order'] for a in acts)}); low/high = min/max of those actuals and the MB-1880 routing standard"
        s_var = statistics.median(s_vals) / rs - 1
        r_var = statistics.median(r_vals) / rr - 1
    else:
        s_exp = s_lo = s_hi = rs; r_exp = r_lo = r_hi = rr
        basis = "MB-1880 rev B routing standard only; no spread available"
        s_var = r_var = None
    ops.append({
        "op": r["op"], "description": r["description"], "work_center": r["work_center"],
        "setup_h": [round(s_lo/60, 3), round(s_exp/60, 3), round(s_hi/60, 3)],
        "run_min_pc": [round(r_lo, 3), round(r_exp, 3), round(r_hi, 3)],
        "basis": basis,
        "analog_actual_vs_routing_setup": None if s_var is None else round(s_var, 4),
        "analog_actual_vs_routing_run": None if r_var is None else round(r_var, 4),
        "flag_over_threshold": None if s_var is None else (abs(s_var) > TH or abs(r_var) > TH),
    })
    o = ops[-1]
    fig(f"Op{o['op']} setup h low/exp/high (rung 4)", o["setup_h"], "routings + closed_jobs (MB-1880 rev B)", basis)
    fig(f"Op{o['op']} run min/pc low/exp/high (rung 4)", o["run_min_pc"], "routings + closed_jobs (MB-1880 rev B)", basis)
    if s_var is not None:
        fig(f"Op{o['op']} MB-1880 actuals median vs MB-1880 routing (setup / run)", f"{s_var*100:+.1f}% / {r_var*100:+.1f}%", "same", "median ÷ routing − 1; threshold 15% — default threshold, not plant-set")

breaks = [250, 500, 1000]
by_break = {}
for q in breaks:
    wc = {}
    rows = []
    for o in ops:
        s = o["setup_h"][1]; run_h = q * o["run_min_pc"][1] / 60
        wc[o["work_center"]] = round(wc.get(o["work_center"], 0) + s + run_h, 2)
        rows.append({"op": o["op"], "setup_h": s, "setup_h_per_pc": round(s / q, 5), "run_h": round(run_h, 2)})
    tot_setup = sum(o["setup_h"][1] for o in ops)
    tot_setup_lo = sum(o["setup_h"][0] for o in ops); tot_setup_hi = sum(o["setup_h"][2] for o in ops)
    tot_run_lo = q * sum(o["run_min_pc"][0] for o in ops) / 60
    tot_run_hi = q * sum(o["run_min_pc"][2] for o in ops) / 60
    by_break[q] = {"ops": rows, "work_content_h_by_wc_expected": wc,
                   "total_setup_h_exp": round(tot_setup, 3), "setup_h_per_pc_exp": round(tot_setup / q, 5),
                   "run_h_total_low_exp_high": [round(tot_run_lo, 2), round(q*sum(o['run_min_pc'][1] for o in ops)/60, 2), round(tot_run_hi, 2)],
                   "setup_h_total_low_exp_high": [round(tot_setup_lo, 3), round(tot_setup, 3), round(tot_setup_hi, 3)]}
    fig(f"Qty {q}: setup h per piece (expected, one setup per op)", by_break[q]["setup_h_per_pc_exp"], "ops table", f"{round(tot_setup,3)} h ÷ {q}")
    fig(f"Qty {q}: work content by work center, expected h", wc, "ops table", "Σ(setup + qty × run/60) by work_center")
    fig(f"Qty {q}: total run h low/exp/high", by_break[q]["run_h_total_low_exp_high"], "ops table", "qty × Σ run min/pc ÷ 60")

# ---- material ----
plate = [p for p in pos if p["item"] == "AL6061-PL-0.5"]
plate.sort(key=lambda p: p["po_date"])
latest = plate[-1]; prior = plate[-2]
fig("Plate price used (latest PO)", f"{latest['po_number']} {latest['po_date']} USD {latest['unit_price_usd']}/sheet", "purchase_orders.csv", "item == AL6061-PL-0.5, latest po_date")
fig("Plate price change vs prior PO", f"{(float(latest['unit_price_usd'])/float(prior['unit_price_usd'])-1)*100:+.2f}%", "purchase_orders.csv", f"{latest['unit_price_usd']} ÷ {prior['unit_price_usd']} − 1 ({prior['po_number']})")
for p in plate:
    from datetime import date
    d = (date.fromisoformat(p["received_date"]) - date.fromisoformat(p["po_date"])).days
    fig(f"{p['po_number']} order-to-receipt days", d, "purchase_orders.csv", "received_date − po_date")
sheet_w, sheet_l = 12 * 25.4, 48 * 25.4
def per_sheet(bw, bl):
    return max((int(sheet_w // bw)) * int(sheet_l // bl), int(sheet_w // bl) * int(sheet_l // bw))
ALLOW = 3.0  # mm per blank in L and W, ASSUMED (saw kerf + cleanup) — not plant data
n0 = fig("Blanks per sheet, zero allowance (physical upper bound)", per_sheet(80, 120), "geometry", "12x48 in sheet, 120x80 mm part, best of two orientations")
n = fig("Blanks per sheet with 3 mm assumed kerf/cleanup allowance", per_sheet(80 + ALLOW, 120 + ALLOW), "geometry", "blank 123x83 mm, best of two orientations — ALLOWANCE ASSUMED")
fig("Thickness cleanup available", f"{12.7-12.0:.1f} mm total ({(12.7-12.0)/2:.2f} mm per side)", "PO item description vs spec", "0.5 in = 12.7 mm stock − 12 mm part")
price = float(latest["unit_price_usd"])
mat = {}
for q in breaks:
    starts = math.ceil(q / (1 - scrap_rate))
    sheets = math.ceil(starts / n)
    cost = round(sheets * price, 2)
    mat[q] = {"starts": starts, "sheets": sheets, "material_cost_usd": cost, "per_pc_usd": round(cost / q, 4)}
    fig(f"Qty {q}: material starts / sheets / cost / per pc", f"{starts} / {sheets} / USD {cost:.2f} / USD {cost/q:.2f}", "purchase_orders.csv + scrap rate", f"ceil({q}÷(1−{scrap_rate:.4f})); ceil(starts÷{n}); sheets × {price}")

# ---- outside processing: anodize ----
an = [p for p in pos if p["item"] == "OSP-ANOD-II-BLK"][0]
lot = float(an["unit_price_usd"])
fig("Anodize OSP lead time (PO to receipt)", (date.fromisoformat(an["received_date"]) - date.fromisoformat(an["po_date"])).days, "purchase_orders.csv", f"{an['po_number']} received_date − po_date (calendar days)")
osp = {}
for q in breaks:
    lots = math.ceil(q / 300)
    osp[q] = {"lots": lots, "cost_usd": round(lots * lot, 2), "per_pc_usd": round(lots * lot / q, 4)}
    fig(f"Qty {q}: anodize lots / cost / per pc", f"{lots} / USD {lots*lot:.2f} / USD {lots*lot/q:.2f}", "purchase_orders.csv", f"ceil({q}÷300) × {lot} ({an['po_number']}, {an['po_date']}); assumes one anodize shipment per 300 pcs")

# ---- write dataset tabs ----
def write(name, rows):
    if not rows: return
    with open(os.path.join(OUT, "dataset", name), "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
write("routings.csv", [dict(r, revision_status="other part (MB-1880 rev B) — similar-part analog, rung 4 only for MB-2040") for r in routings])
write("operation_actuals.csv", actuals)
write("purchase_orders.csv", pos)
write("assets.csv", equip)
write("figures_block.csv", [{k: (json.dumps(v) if not isinstance(v, str) else v) for k, v in r.items()} for r in F])
json.dump({"figures": F, "ops": ops, "by_break": by_break, "material": mat, "anodize": osp,
           "blanks_per_sheet": n, "scrap_rate": scrap_rate}, open(os.path.join(OUT, "figures.json"), "w"), indent=1, default=str)
for r in F:
    print(f"{r['figure']}: {r['value']}   [{r['filter_or_arithmetic']}]")
print(json.dumps(by_break, indent=1))
