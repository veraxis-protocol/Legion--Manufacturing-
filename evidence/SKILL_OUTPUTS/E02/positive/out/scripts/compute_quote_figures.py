"""quote-build figures for Harbor Robotics Lab reBot inquiry (NOREF-20261112).
Every figure printed in the quote outputs comes from this script's JSON.
Run: python -I compute_quote_figures.py <inputs_dir> <out_dir>
"""
import csv, json, os, sys, datetime

inp, out = sys.argv[1], sys.argv[2]
os.makedirs(out, exist_ok=True)

def read_csv(p):
    with open(p, encoding="utf-8") as f:
        rows = [l for l in f if not l.startswith("#")]
    return list(csv.DictReader(rows))

bom = json.load(open(os.path.join(inp, "02_bom_handoff.json"), encoding="utf-8"))
pos = read_csv(os.path.join(inp, "purchase_orders_5052.csv"))
eq = read_csv(os.path.join(inp, "equipment.csv"))
input_files = sorted(os.path.relpath(os.path.join(d, f), inp).replace("\\", "/")
                     for d, _, fs in os.walk(inp) for f in fs)

F = []  # figures block rows
def fig(name, value, src, filt):
    F.append({"figure": name, "value": value, "computed_from": src, "filter_or_arithmetic": filt})
    return value

QTY_SETS = 20
fig("Sets quoted", QTY_SETS, "intake form line 1 quantities", "quantities[0].qty (EML:L10); user request 'Quote 20 sets'")

parts = bom["cnc_parts"]
n_ids = fig("CNC part ids in BOM handoff", len(parts), "02_bom_handoff.json", "len(cnc_parts)")
pure = [p for p in parts if p["process"] == "CNC"]
sm = [p for p in parts if p["process"] != "CNC"]
fig("Part ids, process == 'CNC'", len(pure), "02_bom_handoff.json", "process == 'CNC'")
fig("Part ids, process == 'CNC + Sheet Metal'", len(sm), "02_bom_handoff.json", "process == 'CNC + Sheet Metal'")
pcs_set = fig("CNC pieces per arm set", sum(p["quantity_per_arm"] for p in parts), "02_bom_handoff.json", "sum(quantity_per_arm)")
fig("CNC pieces per set, process == 'CNC'", sum(p["quantity_per_arm"] for p in pure), "02_bom_handoff.json", "sum(quantity_per_arm) where process=='CNC'")
fig("CNC pieces per set, 'CNC + Sheet Metal'", sum(p["quantity_per_arm"] for p in sm), "02_bom_handoff.json", "sum(quantity_per_arm) where process=='CNC + Sheet Metal'")
fig("CNC pieces for 20 sets", pcs_set * QTY_SETS, "arithmetic", f"{pcs_set} x {QTY_SETS}")
fig("Rails for 20 sets", bom["purchased_rail"]["quantity_per_arm"] * QTY_SETS, "02_bom_handoff.json purchased_rail", f"quantity_per_arm {bom['purchased_rail']['quantity_per_arm']} x {QTY_SETS}")
fig("Distinct tolerance strings in BOM", len({p['tolerance'] for p in parts}), "02_bom_handoff.json", "len(set(tolerance))")
fig("Parts citing readme line 129 for tolerance", sum(p["tolerance_source"] == "readme.md line 129" for p in parts), "02_bom_handoff.json", "tolerance_source == 'readme.md line 129'")
fig("Engineering-missing items in handoff", len(bom["engineering_missing"]), "02_bom_handoff.json", "len(engineering_missing)")
fig("Largest bbox dimension, any part (mm)", max(max(p["geometry_from_step"]["bbox"]) for p in parts), "02_bom_handoff.json", "max over parts of max(bbox)")

# Stock from POs
def stock_rows():
    res = []
    for r in pos:
        d = r["description"]
        # dimensions from description "... <t> mm x <w> x <l>"
        tail = d.split("plate ")[-1] if "plate" in d else d.split("sheet ")[-1]
        t = float(tail.split(" mm")[0]); w, l = [float(x) for x in tail.split(" x ")[1:3]]
        price = float(r["unit_price_usd"])
        res.append({"po": r["po_number"], "po_date": r["po_date"], "received": r["received_date"], "item": r["item"],
                    "desc": d, "t_mm": t, "w_mm": w, "l_mm": l, "unit_price": price,
                    "usd_per_mm2": price / (w * l),
                    "lead_days": (datetime.date.fromisoformat(r["received_date"]) - datetime.date.fromisoformat(r["po_date"])).days})
    return sorted(res, key=lambda s: s["t_mm"])
stock = stock_rows()
fig("5052 purchase orders on file", len(stock), "purchase_orders_5052.csv", "data rows")
for s in stock:
    fig(f"{s['po']} price per m2 (USD)", round(s["usd_per_mm2"] * 1e6, 2), "purchase_orders_5052.csv", f"{s['unit_price']} / ({s['w_mm']:.0f} x {s['l_mm']:.0f} mm) x 1e6")
    fig(f"{s['po']} order-to-receipt days", s["lead_days"], "purchase_orders_5052.csv", f"{s['received']} - {s['po_date']}")

rows = []
for p in parts:
    bb = sorted(p["geometry_from_step"]["bbox"])
    t, a, b = bb
    row = {"part_id": p["part_id"], "process": p["process"], "qty_per_arm": p["quantity_per_arm"],
           "bbox_sorted_mm": bb, "volume_mm3": p["geometry_from_step"]["volume"], "faces": p["geometry_from_step"]["faces"]}
    if p["process"] != "CNC":
        row.update(stock=None, status="unknown", reason="CNC + Sheet Metal: sheet gauge and flat pattern not in the handoff; bbox is the formed envelope, not the blank")
    else:
        cand = [s for s in stock if s["t_mm"] >= t]
        if not cand:
            row.update(stock=None, status="unknown", reason=f"smallest bbox dimension {t} mm exceeds every 5052 stock on PO (max {stock[-1]['t_mm']} mm); no price paid on file")
        else:
            s = cand[0]
            area = a * b
            per_pc = area * s["usd_per_mm2"]
            row.update(stock=s["item"], po=s["po"], po_date=s["po_date"], stock_t_mm=s["t_mm"], blank_mm=[a, b], blank_area_mm2=round(area, 1),
                       usd_per_pc=round(per_pc, 4), usd_per_set=round(per_pc * p["quantity_per_arm"], 4),
                       usd_20_sets=round(per_pc * p["quantity_per_arm"] * QTY_SETS, 2),
                       volume_over_blank=round(p["geometry_from_step"]["volume"] / (area * s["t_mm"]), 3),
                       status="lower bound")
    rows.append(row)

priced = [r for r in rows if r["status"] == "lower bound"]
unk = [r for r in rows if r["status"] == "unknown"]
fig("Part ids with a material lower bound", len(priced), "computed table", "status == 'lower bound'")
fig("Part ids with material unknown", len(unk), "computed table", "status == 'unknown'")
fig("Pieces per set with a material lower bound", sum(r["qty_per_arm"] for r in priced), "computed table", "sum(qty_per_arm) where lower bound")
fig("Pieces per set with material unknown", sum(r["qty_per_arm"] for r in unk), "computed table", "sum(qty_per_arm) where unknown")
mat_set = round(sum(r["usd_per_set"] for r in priced), 4)
fig("Material lower bound per set, priced parts only (USD)", mat_set, "computed table", "sum(usd_per_set) over lower-bound parts; excludes unknown parts, scrap allowance, kerf, workholding stock")
fig("Material lower bound, 20 sets, priced parts only (USD)", round(sum(r["usd_20_sets"] for r in priced), 2), "computed table", "sum(usd_20_sets) over lower-bound parts")
for s in stock:
    sel = [r for r in priced if r["po"] == s["po"]]
    fig(f"Part ids priced from {s['po']}", len(sel), "computed table", f"po == {s['po']}")

# Equipment
fig("Assets in equipment list", len(eq), "equipment.csv", "data rows")
wcs = sorted({e["work_center"] for e in eq})
fig("Work centres in equipment list", ", ".join(wcs), "equipment.csv", "distinct work_center")
fig("Assets whose description mentions bend/brake/press/form/sheet", sum(any(k in e["description"].lower() for k in ("bend", "brake", "press", "form", "sheet")) for e in eq), "equipment.csv", "description contains bend|brake|press|form|sheet")
fig("Assets whose description mentions 5-axis", sum("5-axis" in e["description"].lower() for e in eq), "equipment.csv", "description contains '5-axis'")

# Comparables / history
hist_files = [f for f in input_files if any(k in f.lower() for k in ("work_order", "workorder", "routing", "actual", "quote", "sales_order", "planning", "schedule", "load"))]
fig("Input files that are routings, actuals, work orders, prior quotes or planning exports", len(hist_files), "file enumeration of inputs/", "name contains work_order|routing|actual|quote|sales_order|planning|schedule|load")
fig("Input files enumerated", len(input_files), "file enumeration of inputs/", "os.walk")

# Dates
today = datetime.date(2026, 11, 14)
req = datetime.date(2027, 1, 31)
fig("Calendar days, today (2026-11-14) to requested 2027-01-31", (req - today).days, "arithmetic", "2027-01-31 - 2026-11-14")
fig("Calendar days, receipt (2026-11-12) to requested 2027-01-31", (req - datetime.date(2026, 11, 12)).days, "arithmetic", "2027-01-31 - 2026-11-12")
fig("Variance threshold", "15% - default threshold, not plant-set", "no Plant context", "hours-ladder.md default")
fig("Operations with a variance computed", 0, "hours table", "fewer than two rungs exist for every operation")

# MFG_* by name only
set_vars = [v for v in ("MFG_LABOR_RATE", "MFG_BURDEN_RATE", "MFG_MARGIN_RULES", "MFG_SCRAP_COSTING_BASIS") if os.environ.get(v)]
fig("MFG_* rate variables set", len(set_vars), "environment", "names checked: MFG_LABOR_RATE, MFG_BURDEN_RATE, MFG_MARGIN_RULES, MFG_SCRAP_COSTING_BASIS (values never read out)")

json.dump({"figures": F, "material_table": rows, "stock": stock, "input_files": input_files, "history_files": hist_files},
          open(os.path.join(out, "figures.json"), "w", encoding="utf-8"), indent=1)
with open(os.path.join(out, "material-basis.csv"), "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["# INTERNAL - NOT FOR CUSTOMER. Material lower bound per part, quote-build, Harbor Robotics Lab NOREF-20261112. SYNTHETIC data."])
    w.writerow(["part_id", "process", "qty_per_arm", "bbox_sorted_mm", "stock_item", "po", "po_date", "stock_t_mm", "blank_mm", "blank_area_mm2", "usd_per_pc", "usd_per_set", "usd_20_sets", "volume_over_blank", "status", "reason"])
    for r in rows:
        w.writerow([r["part_id"], r["process"], r["qty_per_arm"], "x".join(str(x) for x in r["bbox_sorted_mm"]), r.get("stock"), r.get("po"), r.get("po_date"), r.get("stock_t_mm"),
                    "x".join(str(x) for x in r.get("blank_mm", [])) or None, r.get("blank_area_mm2"), r.get("usd_per_pc"), r.get("usd_per_set"), r.get("usd_20_sets"), r.get("volume_over_blank"), r["status"], r.get("reason")])
for x in F:
    print(f"{x['figure']} | {x['value']} | {x['computed_from']} | {x['filter_or_arithmetic']}")
print()
for r in rows:
    print(r["part_id"], r["qty_per_arm"], r["bbox_sorted_mm"], r.get("stock"), r.get("usd_per_pc"), r.get("usd_per_set"), r.get("volume_over_blank"), r["status"])

# markdown tables for the reply
def md(rows_, cols):
    out_=["| "+" | ".join(c for c,_ in cols)+" |","|"+"---|"*len(cols)]
    for r in rows_:
        out_.append("| "+" | ".join(str(fn(r)) for _,fn in cols)+" |")
    return chr(10).join(out_)
mt = md(rows, [("Part id",lambda r:r["part_id"]),("Process",lambda r:r["process"]),("Qty/set",lambda r:r["qty_per_arm"]),
  ("BBox sorted (mm)",lambda r:" x ".join(str(x) for x in r["bbox_sorted_mm"])),
  ("Stock (PO, date)",lambda r:f'{r["stock"]} ({r["po"]}, {r["po_date"]})' if r.get("stock") else "none"),
  ("Blank (mm)",lambda r:" x ".join(str(x) for x in r["blank_mm"]) if r.get("blank_mm") else "-"),
  ("USD/pc",lambda r:r.get("usd_per_pc","unknown") if r.get("usd_per_pc") is not None else "unknown"),
  ("USD/set",lambda r:r.get("usd_per_set") if r.get("usd_per_set") is not None else "unknown"),
  ("USD 20 sets",lambda r:r.get("usd_20_sets") if r.get("usd_20_sets") is not None else "unknown"),
  ("Part vol / blank vol",lambda r:r.get("volume_over_blank","-")),
  ("Status",lambda r:r["status"] + (": "+r["reason"] if r.get("reason") else ""))])
ft = md(F, [("Figure",lambda x:x["figure"]),("Value",lambda x:x["value"]),("Computed from",lambda x:x["computed_from"]),("Filter or arithmetic",lambda x:x["filter_or_arithmetic"])])
open(os.path.join(out,"_material_table.md"),"w",encoding="utf-8").write(mt)
open(os.path.join(out,"_figures_table.md"),"w",encoding="utf-8").write(ft)
