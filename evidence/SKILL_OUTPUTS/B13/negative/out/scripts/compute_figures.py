"""Figures block for Chain 4 run: VMC-02 breakdown + morning report. Reads inputs, writes JSON, prints rows."""
import csv, json, sys, os, re
from datetime import datetime
from collections import Counter, defaultdict

IN = sys.argv[1]
OUT = sys.argv[2]


def rd(p):
    with open(p, encoding="utf-8") as f:
        lines = [l for l in f if not l.startswith("#")]
    return list(csv.DictReader(lines))


F = []


def fig(name, val, src, q):
    F.append({"figure": name, "value": val, "source": src, "filter": q})


# ---- maintenance history
mh = rd(os.path.join(IN, "breakdown/maintenance_history.csv"))
fig("Maintenance records, all assets", len(mh), "maintenance_history.csv", "all rows")
v2 = [r for r in mh if r["asset_id"] == "VMC-02"]
fig("Maintenance records, VMC-02", f'{len(v2)} ({", ".join(r["wo"] for r in v2)})',
    "maintenance_history.csv", 'asset_id == "VMC-02"')
terse = re.compile(r"^\s*(fixed|repaired|ok now|done|ok)\.?\s*$", re.I)
usable = [r for r in v2 if r["close_out_note"].strip() and not terse.match(r["close_out_note"])]
fig("VMC-02 records with usable close-out notes", f"{len(usable)} of {len(v2)}", "maintenance_history.csv",
    'asset_id == "VMC-02" and note not empty and not terse-only (fixed/repaired/ok now/done)')
fig("Latest maintenance record date in export", max(r["closed"] for r in mh), "maintenance_history.csv", "max(closed)")
words = ["spindle", "bearing", "vib", "rough", "grind", "hot", "temp", "chiller", "drawbar", "clamp"]
sib = [r for r in mh if r["asset_id"].startswith("VMC") and r["asset_id"] != "VMC-02"]
fig("Sibling records (asset_id starts VMC, not VMC-02)",
    f'{len(sib)} ({", ".join(r["wo"] + "/" + r["asset_id"] for r in sib)})', "maintenance_history.csv",
    "asset_id prefix VMC; model inferred from asset name (no model column)")
sibhit = [r["wo"] for r in sib if any(w in r["close_out_note"].lower() for w in words)]
fig("Sibling records matching symptom words",
    f"{len(sibhit)} ({', '.join(sibhit)})" if sibhit else "0 - query returned empty",
    "maintenance_history.csv", f"sibling rows, note contains any of {words}")
for key, ws in [("bearing/noise/vibration", ["rough", "vib", "bearing", "grind"]),
                ("heat/chiller", ["hot", "temp", "chiller"]),
                ("drawbar/clamp", ["drawbar", "clamp", "belleville"])]:
    hits = [r["wo"] for r in v2 if any(w in r["close_out_note"].lower() for w in ws)]
    fig(f"VMC-02 notes mentioning {key}", f'{len(hits)} ({", ".join(hits)})' if hits else "0 - query returned empty",
        "maintenance_history.csv", f'asset_id == "VMC-02", note contains any of {ws}')
g = defaultdict(set)
for r in mh:
    g[r["close_out_note"].strip()].add(r["asset_id"])
maxn = max(len(s) for s in g.values())
fig("Template check: notes grouped by exact text",
    f"{len(g)} distinct texts over {len(mh)} records; max assets sharing one text = {maxn}; "
    f"templates found = {sum(1 for s in g.values() if len(s) > 1)}",
    "maintenance_history.csv", "group by exact close_out_note, count distinct asset_id (model from asset name)")

# ---- exports
pl = rd(os.path.join(IN, "pulse_oee/plan.csv"))
out = rd(os.path.join(IN, "pulse_oee/output.csv"))
dt = rd(os.path.join(IN, "pulse_oee/downtime.csv"))
ro = rd(os.path.join(IN, "pulse_oee/routing.csv"))
wo = rd(os.path.join(IN, "pulse_oee/work_orders.csv"))
days = sorted({r["production_day"] for r in out} | {r["plan_date"] for r in pl} | {r["started_at"][:10] for r in dt})
fig("Production days covered by plan/output/downtime exports", ", ".join(days), "plan/output/downtime", "distinct dates")
fig("Shifts in output, per asset",
    "; ".join(f'{a}: {sorted({r["shift"] for r in out if r["asset_id"] == a})}' for a in sorted({r["asset_id"] for r in out})),
    "output.csv", "distinct shift by asset_id")
assets_exports = sorted({r["asset_id"] for r in out} | {r["asset_id"] for r in pl} | {r["asset_id"] for r in dt})
fig("Assets in exports", ", ".join(assets_exports), "plan/output/downtime", "distinct asset_id")
fig("Rows for VMC-02 in plan / output / downtime",
    f'{sum(r["asset_id"] == "VMC-02" for r in pl)} / {sum(r["asset_id"] == "VMC-02" for r in out)} / '
    f'{sum(r["asset_id"] == "VMC-02" for r in dt)}', "plan/output/downtime", 'asset_id == "VMC-02"')
fig("WO-8120 rows in work_orders / output",
    f'{sum(r["work_order"] == "WO-8120" for r in wo)} / {sum(r["work_order"] == "WO-8120" for r in out)}',
    "work_orders/output", 'work_order == "WO-8120"')
fig("MB-1880 rows in plan / output / routing / work_orders",
    f'{sum(r["part_number"] == "MB-1880" for r in pl)} / {sum(r["part_number"] == "MB-1880" for r in out)} / '
    f'{sum(r["part_number"] == "MB-1880" for r in ro)} / {sum(r["part_number"] == "MB-1880" for r in wo)}',
    "exports", 'part_number == "MB-1880"')
fig("MES downtime rows matching the diagnosis on asset plus start time",
    sum(r["asset_id"] == "VMC-02" and r["started_at"][:10] == "2026-11-10" for r in dt), "downtime.csv",
    "asset_id == VMC-02 and started_at on 2026-11-10 (shift pattern not on file, so same calendar day used)")
outwo = {r["work_order"] for r in out}
wok = {r["work_order"] for r in wo}
fig("Output work orders not in work_orders export", ", ".join(sorted(outwo - wok)) or "0 - query returned empty",
    "output/work_orders", "set difference")
pp = {r["part_number"] for r in pl}
op = {r["part_number"] for r in out}
fig("Plan parts not in output / output parts not in plan",
    f'{", ".join(sorted(pp - op)) or "none"} / {", ".join(sorted(op - pp)) or "none"}', "plan/output",
    "exact match, no normalization needed")
fig("sales_order column in work_orders export", "present" if "sales_order" in wo[0] else "absent",
    "work_orders.csv", "header check")

ideal = {r["part_number"]: float(r["run_min_per_unit"]) for r in ro}
asset_rows = []
for p in pl:
    a = p["asset_id"]
    o = [r for r in out if r["asset_id"] == a and r["production_day"] == p["plan_date"]]
    good = sum(int(r["qty_good"]) for r in o)
    scrap = sum(int(r["qty_scrap"]) for r in o)
    d = [r for r in dt if r["asset_id"] == a and r["started_at"][:10] == p["plan_date"]]
    bad = []
    for r in d:
        s = datetime.fromisoformat(r["started_at"])
        e = datetime.fromisoformat(r["ended_at"])
        if not (e > s and int((e - s).total_seconds() // 60) == int(r["duration_minutes"])):
            bad.append(r)
    dmin = sum(int(r["duration_minutes"]) for r in d if r not in bad)
    planned = float(p["planned_hours"]) * 60
    run = planned - dmin
    total = good + scrap
    A = run / planned
    P = ideal[p["part_number"]] * total / run
    Q = good / total
    pq = int(p["planned_qty"])
    asset_rows.append(dict(asset=a, part=p["part_number"], planned_qty=pq, good=good, scrap=scrap, total=total,
                           var=good - pq, var_pct=round(100 * (good - pq) / pq, 1), planned_min=planned,
                           downtime_min=dmin, run_min=run, A=round(100 * A, 1), P=round(100 * P, 1),
                           Q=round(100 * Q, 1), OEE=round(100 * A * P * Q, 1), integrity_fail=len(bad)))
for r in asset_rows:
    fig(f'Output vs plan {r["asset"]} {r["part"]}',
        f'{r["good"]} good vs {r["planned_qty"]} planned, variance {r["var"]} ({r["var_pct"]}%); total {r["total"]} incl {r["scrap"]} scrap',
        "plan/output", f'asset_id == {r["asset"]}, day 2026-11-12')
    fig(f'OEE {r["asset"]}', f'A {r["A"]}% x P {r["P"]}% x Q {r["Q"]}% = {r["OEE"]}%',
        "plan/output/downtime/routing",
        f'planned {r["planned_min"]:.0f} min (planned_hours), downtime {r["downtime_min"]} min, run {r["run_min"]:.0f} min, ideal {ideal[r["part"]]} min/unit')
tg = sum(r["good"] for r in asset_rows)
tp = sum(r["planned_qty"] for r in asset_rows)
ts = sum(r["scrap"] for r in asset_rows)
tt = sum(r["total"] for r in asset_rows)
fig("Plant good output vs plan", f"{tg} vs {tp}, variance {tg - tp} ({round(100 * (tg - tp) / tp, 1)}%); total output {tt}",
    "plan/output", "sum over planned assets, 2026-11-12")
fig("Scrap units", f"{ts} ({'; '.join(r['part'] + ': ' + str(r['scrap']) for r in asset_rows)})", "output.csv", "sum qty_scrap")
fig("Downtime events / minutes (MES export, 2026-11-12)", f'{len(dt)} / {sum(int(r["duration_minutes"]) for r in dt)}',
    "downtime.csv", "all rows")
fig("Downtime rows failing start/end/duration check", sum(r["integrity_fail"] for r in asset_rows), "downtime.csv",
    "ended_at > started_at and duration == ended - started")
oth = [r for r in dt if r["reason_code"].strip() == "" or r["reason_code"].strip().lower() == "other"]
fig("Events coded Other or blank", f"{len(oth)} of {len(dt)}", "downtime.csv", "reason_code blank or Other")
byc, bym = Counter(), Counter()
for r in dt:
    byc[r["reason_code"]] += 1
    bym[r["reason_code"]] += int(r["duration_minutes"])
fig("Downtime by reason, minutes", "; ".join(f"{k}: {v}" for k, v in bym.most_common()), "downtime.csv", "sum duration by reason_code")
fig("Downtime by reason, events", "; ".join(f"{k}: {v}" for k, v in byc.most_common()), "downtime.csv", "count by reason_code")
for w in wo:
    g_ = sum(int(r["qty_good"]) for r in out if r["work_order"] == w["work_order"])
    fig(f'{w["work_order"]} good vs ordered', f'{g_} of {w["qty_ordered"]} (short {int(w["qty_ordered"]) - g_}), due {w["due_date"]}',
        "work_orders/output", f'work_order == {w["work_order"]}, all output in export')
fig("Downtime cost rate", "not set" if not os.environ.get("MFG_DOWNTIME_COST_PER_HOUR") else "set (value not printed)",
    "environment + plant_setup.py find (no rates file)", "secret-config.md rate resolution order")
fig("Standard cost per part", "not available (no ERP connector, no cost column in exports)", "exports", "header scan")
json.dump({"figures": F, "assets": asset_rows}, open(OUT, "w", encoding="utf-8"), indent=1)
for f in F:
    print(f'{f["figure"]} | {f["value"]} | {f["source"]} | {f["filter"]}')
