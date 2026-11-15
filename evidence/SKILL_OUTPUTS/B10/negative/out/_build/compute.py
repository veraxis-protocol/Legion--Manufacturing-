"""Consolidate the export drop and compute every figure for the morning report.
Reads C:/LMFG/runs/B10-negative/work/inputs, writes under work/out. No network, no installs."""
import csv, json, os, datetime, collections, pathlib

ROOT = pathlib.Path(r"C:/LMFG/runs/B10-negative/work")
INP = ROOT / "inputs"
EXP = INP / "pulse_oee"
OUT = ROOT / "out"
RUN_AT = datetime.datetime.now().astimezone()

def read(name):
    p = EXP / name
    with open(p, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    return rows, list(rows[0].keys()) if rows else []

def mtime(p):
    return datetime.datetime.fromtimestamp(os.path.getmtime(p)).astimezone()

figs = []
def fig(name, value, source, filt):
    figs.append({"figure": name, "value": value, "computed_from": source, "filter": filt})
    return value

# ---------- Step 1 discover ----------
files = {}
for p in sorted(INP.rglob("*")):
    if p.is_file():
        files[str(p.relative_to(INP)).replace("\\", "/")] = mtime(p)

output, out_cols = read("output.csv")
plan, plan_cols = read("plan.csv")
routing, rt_cols = read("routing.csv")
wos, wo_cols = read("work_orders.csv")

identified = [
    {"file": "pulse_oee/output.csv", "identified_as": "production output (MES-type export)", "tab": "production_output", "columns": out_cols},
    {"file": "pulse_oee/plan.csv", "identified_as": "production plan (planning export)", "tab": "plan", "columns": plan_cols},
    {"file": "pulse_oee/work_orders.csv", "identified_as": "production work orders (ERP-type export)", "tab": "production_work_orders", "columns": wo_cols},
    {"file": "pulse_oee/routing.csv", "identified_as": "run standards per part and operation; NOT loaded as a routings tab: no setup-time column, which the routing signature requires", "tab": None, "columns": rt_cols},
    {"file": "pulse_oee/README.txt", "identified_as": "note describing the drop; not data", "tab": None, "columns": []},
    {"file": "rates_memo.txt", "identified_as": "finance memo of shop rates and scrap-costing basis; not an export, not a confirmed plant rate", "tab": None, "columns": []},
]
fig("Files in input folder", len(files), "input folder listing", "all files, recursive")

# ---------- Step 2 freshness / windows ----------
out_days = sorted({r["production_day"] for r in output})
plan_days = sorted({r["plan_date"] for r in plan})
fig("Production days in output export", ", ".join(out_days), "output.csv", "distinct production_day")
fig("Plan dates in plan export", ", ".join(plan_days), "plan.csv", "distinct plan_date")
latest_day = max(out_days)
run_date = RUN_AT.date()
expected_day = (run_date - datetime.timedelta(days=1)).isoformat()
fig("Run date", run_date.isoformat(), "system clock", "")
fig("Production day expected for this morning (run date - 1)", expected_day, "run date", "no plant day-boundary rule on file; calendar day before the run")
fig("Latest production day present", latest_day, "output.csv", "max(production_day)")
missing_days = []
d = datetime.date.fromisoformat(latest_day) + datetime.timedelta(days=1)
while d <= datetime.date.fromisoformat(expected_day):
    missing_days.append(d.isoformat()); d += datetime.timedelta(days=1)
fig("Production days with no export (after latest present, up to expected)", ", ".join(missing_days) or "none", "output.csv vs run date", "dates between latest production_day+1 and run date-1")
future = [f for f, t in files.items() if t > RUN_AT]
fig("Files with a modified time later than the run", len(future), "file system", "mtime > run time")
date_cols_checked = {"output.csv": "production_day", "plan.csv": "plan_date"}
future_rows = [r for r in output if r["production_day"] > run_date.isoformat()] + [r for r in plan if r["plan_date"] > run_date.isoformat()]
fig("Activity rows dated after the run date", len(future_rows), "output.csv, plan.csv", "production_day / plan_date > run date (due dates excluded: commitments)")

# ---------- Step 4-6 join + classify ----------
wo_by = {w["work_order"]: w for w in wos}
plan_parts = {r["part_number"] for r in plan}
rt_parts = {r["part_number"] for r in routing}
out_parts = {r["part_number"] for r in output}
out_wos = {r["work_order"] for r in output}

wo_exact = sum(1 for r in output if r["work_order"] in wo_by)
fig("Output rows", len(output), "output.csv", "all rows")
fig("Output rows whose work order matches work_orders.csv exactly", wo_exact, "output.csv x work_orders.csv", "work_order equal, no normalization")
part_agree = sum(1 for r in output if r["work_order"] in wo_by and wo_by[r["work_order"]]["part_number"] == r["part_number"])
fig("Output rows whose part equals the work order's part", part_agree, "output.csv x work_orders.csv", "part_number equal")
fig("Plan rows", len(plan), "plan.csv", "all rows")
fig("Plan parts matching an output part exactly", len(plan_parts & out_parts), "plan.csv x output.csv", "part_number equal")
fig("Plan assets matching an output asset exactly", len({r['asset_id'] for r in plan} & {r['asset_id'] for r in output}), "plan.csv x output.csv", "asset_id equal")
fig("Normalizations fired", 0, "join log", "ladder rungs 1-5; every key matched as-is")

# duplicates at grain WO x shift x day
grain = collections.Counter((r["work_order"], r["shift"], r["production_day"]) for r in output)
dups = [k for k, c in grain.items() if c > 1]
fig("Duplicate keys at production_output grain (WO, shift, day)", len(dups), "output.csv", "count>1 per (work_order, shift, production_day)")
# class 6 candidates: WO with no output, planned part with no output
wo_no_out = [w for w in wo_by if w not in out_wos]
fig("Work orders with no output rows (class 6 candidates)", len(wo_no_out), "work_orders.csv vs output.csv", "work_order not in output")
plan_no_out = [p for p in plan_parts if p not in out_parts]
fig("Planned parts with no output (class 6 candidates)", len(plan_no_out), "plan.csv vs output.csv", "part not in output")
out_not_planned = [p for p in out_parts if p not in plan_parts]
fig("Produced parts not on the plan", len(out_not_planned), "output.csv vs plan.csv", "part not in plan")
fig("Output rows outside plan window (class 7)", sum(1 for r in output if r["production_day"] not in plan_days), "output.csv vs plan.csv", "production_day not in plan dates")
uom_cols = [f for f, cols in [("output.csv", out_cols), ("plan.csv", plan_cols), ("work_orders.csv", wo_cols)] if any(c.lower() in ("uom", "unit", "unit_of_measure") for c in cols)]
fig("Exports carrying a unit-of-measure column", len(uom_cols), "output.csv, plan.csv, work_orders.csv headers", "column named uom/unit/unit_of_measure")
rework_col = any("rework" in c.lower() for c in out_cols)
fig("Output export has a rework column", "yes" if rework_col else "no", "output.csv header", "column containing 'rework'")
fig("Routing rows carrying a revision", sum(1 for r in routing if r.get("part_revision") or r.get("revision")), "routing.csv", "revision column present and populated")
fig("Work orders carrying a sales order link", sum(1 for w in wos if w.get("sales_order")), "work_orders.csv", "sales_order column present and populated")

# ---------- write dataset tabs (CSV; no XLSX writer in this session) ----------
def write_tab(name, rows, cols):
    with open(OUT / "dataset" / f"{name}.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols); w.writeheader(); [w.writerow(r) for r in rows]

common = ["site", "source_system", "source_ref", "as_of", "join_status", "mismatch_class", "contradicted_by", "integrity_flags"]
po_rows = []
for i, r in enumerate(output, start=2):
    po_rows.append({"site": r["site"], "source_system": "mes_export", "source_ref": f"pulse_oee/output.csv:{i}",
                    "as_of": r["production_day"] + " (date only; no time or zone in export)", "join_status": "matched",
                    "mismatch_class": "", "contradicted_by": "", "integrity_flags": "",
                    "production_wo": r["work_order"], "production_wo_verbatim": r["work_order"],
                    "part_number": r["part_number"], "part_number_verbatim": r["part_number"], "part_revision": "",
                    "asset_id": r["asset_id"], "asset_id_verbatim": r["asset_id"], "cell": r["cell"],
                    "qty_good": r["qty_good"], "qty_scrap": r["qty_scrap"], "uom": "", "shift": r["shift"], "production_day": r["production_day"]})
write_tab("production_output", po_rows, list(po_rows[0].keys()))
pl_rows = []
for i, r in enumerate(plan, start=2):
    pl_rows.append({"site": "not stated in export", "source_system": "planning_export", "source_ref": f"pulse_oee/plan.csv:{i}",
                    "as_of": r["plan_date"] + " (date only)", "join_status": "matched", "mismatch_class": "", "contradicted_by": "", "integrity_flags": "",
                    "part_number": r["part_number"], "part_number_verbatim": r["part_number"], "planned_qty": r["planned_qty"], "uom": "",
                    "plan_date": r["plan_date"], "work_center": r["work_center"], "asset_id": r["asset_id"], "asset_id_verbatim": r["asset_id"],
                    "planned_hours": r["planned_hours"]})
write_tab("plan", pl_rows, list(pl_rows[0].keys()))
wo_rows = []
for i, r in enumerate(wos, start=2):
    wo_rows.append({"site": "not stated in export", "source_system": "manual", "source_ref": f"pulse_oee/work_orders.csv:{i}",
                    "as_of": "unknown (no date column; file modified %s)" % files["pulse_oee/work_orders.csv"].isoformat(timespec="minutes"),
                    "join_status": "matched", "mismatch_class": "", "contradicted_by": "", "integrity_flags": "",
                    "production_wo": r["work_order"], "production_wo_verbatim": r["work_order"], "part_number": r["part_number"],
                    "part_number_verbatim": r["part_number"], "qty": r["qty_ordered"], "uom": "", "status": r["status"], "due_date": r["due_date"],
                    "sales_order": "", "sales_order_verbatim": ""})
write_tab("production_work_orders", wo_rows, list(wo_rows[0].keys()))

# ---------- Output against plan ----------
by_part = collections.defaultdict(lambda: {"good": 0, "scrap": 0, "rows": 0})
for r in output:
    b = by_part[r["part_number"]]; b["good"] += int(r["qty_good"]); b["scrap"] += int(r["qty_scrap"]); b["rows"] += 1
oap = []
for p in plan:
    pn = p["part_number"]; b = by_part.get(pn)
    planned = int(p["planned_qty"])
    good = b["good"] if b else None
    row = {"part": pn, "asset": p["asset_id"], "work_center": p["work_center"],
           "cell": sorted({r["cell"] for r in output if r["part_number"] == pn}),
           "planned": planned, "good": good, "scrap": b["scrap"] if b else None,
           "total": (b["good"] + b["scrap"]) if b else None,
           "variance_good": (good - planned) if b else None,
           "variance_pct": round(100.0 * (good - planned) / planned, 1) if b else None,
           "output_rows": b["rows"] if b else 0}
    oap.append(row)
    fig(f"Planned qty {pn}", planned, "plan.csv", f"part_number=={pn}, plan_date={p['plan_date']}")
    fig(f"Good qty {pn}", good, "output.csv", f"sum qty_good, part_number=={pn}, production_day={latest_day} ({row['output_rows']} rows)")
    fig(f"Scrap qty {pn}", row["scrap"], "output.csv", f"sum qty_scrap, part_number=={pn}")
    fig(f"Total qty (good+scrap) {pn}", row["total"], "output.csv", f"good + scrap, part_number=={pn}")
    fig(f"Good vs plan {pn}", row["variance_good"], "output.csv - plan.csv", f"good - planned, {pn}")
    fig(f"Good vs plan % {pn}", row["variance_pct"], "same computation", "(good - planned)/planned x 100, 1 dp")

# output by shift (for the shift statement)
shifts = collections.defaultdict(set)
for r in output: shifts[r["asset_id"]].add(r["shift"])
for a, s in sorted(shifts.items()):
    fig(f"Shifts with output rows, {a}", ", ".join(sorted(s)), "output.csv", f"distinct shift, asset_id=={a}")

# ---------- OEE ----------
std = {r["part_number"]: float(r["run_min_per_unit"]) for r in routing}
oee = []
for p in plan:
    a = p["asset_id"]
    rows = [r for r in output if r["asset_id"] == a]
    good = sum(int(r["qty_good"]) for r in rows); scrap = sum(int(r["qty_scrap"]) for r in rows); total = good + scrap
    ideal_min = sum((int(r["qty_good"]) + int(r["qty_scrap"])) * std[r["part_number"]] for r in rows)
    planned_min = float(p["planned_hours"]) * 60
    q = good / total if total else None
    ap = ideal_min / planned_min if planned_min else None
    oee.append({"asset": a, "work_center": p["work_center"], "planned_hours": float(p["planned_hours"]),
                "ideal_minutes": round(ideal_min, 1), "good": good, "scrap": scrap, "total": total,
                "availability": None, "availability_reason": "no downtime export, so run time is unknown",
                "performance": None, "performance_reason": "needs run time, which needs the downtime export",
                "quality_pct": round(100 * q, 1) if q is not None else None,
                "a_x_p_pct": round(100 * ap, 1) if ap is not None else None,
                "oee": None, "oee_reason": "availability and performance not computable separately"})
    fig(f"Planned hours {a}", float(p["planned_hours"]), "plan.csv", f"planned_hours, asset_id=={a}")
    fig(f"Ideal minutes of parts made {a}", round(ideal_min, 1), "output.csv x routing.csv", f"sum (good+scrap) x run_min_per_unit, asset_id=={a}")
    fig(f"Quality % {a}", round(100 * q, 1), "output.csv", f"good/(good+scrap) x 100, asset_id=={a}: {good}/{total}")
    fig(f"Availability x performance combined % {a}", round(100 * ap, 1), "same computation", f"ideal minutes / (planned_hours x 60): {round(ideal_min,1)}/{planned_min:.0f}")
    fig(f"Availability {a}", "not computable", "-", "no downtime export in the drop")
    fig(f"Performance {a}", "not computable", "-", "run time unknown without downtime export")
    fig(f"Composite OEE {a}", "not reported", "-", "components cannot be separated")

# ---------- Downtime ----------
fig("Downtime events read", "unknown: no downtime export", "input folder listing", "no file with asset + start/end + reason code headers")
fig("Downtime minutes", "unknown: no downtime export", "-", "not zero; not measured")
fig("Breakdown diagnosis records in drop", 0, "input folder listing", "no downtime-record contract files (source_system breakdown_diagnosis)")

# ---------- Priced losses ----------
for pn, b in sorted(by_part.items()):
    fig(f"Scrap units {pn} (for pricing table)", b["scrap"], "output.csv", f"sum qty_scrap, part_number=={pn}")
fig("Standard cost rows available", 0, "input folder listing", "no item master / parts / standard cost file")
fig("Downtime cost per hour", "not set", "MFG_DOWNTIME_COST_PER_HOUR unset; no plant rates file", "secret-config resolution order")
fig("Scrap dollars", "unpriced: no standard cost", "-", "")
fig("Downtime dollars", "unknown: no downtime data and no downtime rate", "-", "")

# ---------- Work orders / exceptions ----------
wo_status = []
good_by_wo = collections.defaultdict(int)
for r in output: good_by_wo[r["work_order"]] += int(r["qty_good"])
for w in wos:
    g = good_by_wo.get(w["work_order"], 0); o = int(w["qty_ordered"])
    due = w["due_date"]
    if g >= o: state = "complete_but_open"
    elif due < run_date.isoformat(): state = "past_due_short"
    elif due == run_date.isoformat(): state = "due_today_short"
    else: state = "open_short"
    wo_status.append({"wo": w["work_order"], "part": w["part_number"], "ordered": o, "good_recorded": g,
                      "short": max(o - g, 0), "due": due, "status": w["status"], "state": state})
    fig(f"Good recorded vs ordered {w['work_order']}", f"{g} of {o}", "output.csv x work_orders.csv", f"sum qty_good through {latest_day}, work_order=={w['work_order']}")
    fig(f"Short vs order {w['work_order']}", max(o - g, 0), "same computation", "ordered - good recorded, floor 0")
fig("Work orders past due and short", sum(1 for x in wo_status if x["state"] == "past_due_short"), "work_orders.csv", f"due_date < {run_date} and good < ordered")
fig("Work orders due today and short", sum(1 for x in wo_status if x["state"] == "due_today_short"), "work_orders.csv", f"due_date == {run_date} and good < ordered")
fig("Work orders complete by output but still RELEASED", sum(1 for x in wo_status if x["state"] == "complete_but_open"), "work_orders.csv", "good >= ordered and status RELEASED")
fig("Work orders whose commitment impact is not traceable", len(wos), "work_orders.csv", "no sales_order column")

model = {"run_at": RUN_AT.isoformat(timespec="minutes"), "site": sorted({r["site"] for r in output}),
         "latest_day": latest_day, "expected_day": expected_day, "missing_days": missing_days,
         "files": {k: v.isoformat(timespec="minutes") for k, v in files.items()}, "identified": identified,
         "output_vs_plan": oap, "oee": oee, "shifts": {k: sorted(v) for k, v in shifts.items()},
         "work_orders": wo_status, "dups": dups, "rework_col": rework_col, "figures": figs}
json.dump(model, open(OUT / "report_model.json", "w", encoding="utf-8"), indent=2)
with open(OUT / "figures.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=["figure", "value", "computed_from", "filter"]); w.writeheader(); [w.writerow(x) for x in figs]
for x in figs: print(f"{x['figure']}: {x['value']}")
