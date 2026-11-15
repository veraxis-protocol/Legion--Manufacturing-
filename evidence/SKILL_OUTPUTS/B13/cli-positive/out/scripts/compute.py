"""Chain 4 compute step: every figure used in the outputs is produced here.
Usage: python -I compute.py <inputs_dir> <out_dir>
"""
import sys, json, re
from datetime import datetime, date
import pandas as pd

IN, OUT = sys.argv[1], sys.argv[2]
RUN_DATE = date(2026, 11, 15)
F = []  # figures block rows: (figure, value, source, filter)
def fig(name, value, src, flt):
    F.append({"figure": name, "value": value, "source": src, "filter": flt})
    return value

# ---------------- Breakdown side ----------------
# close_out_note holds unquoted commas, so split on the first five commas only
_lines = [l.rstrip("\n") for l in open(f"{IN}/breakdown/maintenance_history.csv", encoding="utf-8") if l.strip() and not l.startswith("#")]
_hdr = _lines[0].split(",")
_recs = [l.split(",", len(_hdr) - 1) for l in _lines[1:]]
mh = pd.DataFrame(_recs, columns=_hdr)
fig("Maintenance rows whose note contains an unquoted comma", int(sum(l.count(",") > len(_hdr) - 1 for l in _lines[1:])),
    "maintenance_history.csv", "line has more than 5 commas; parsed by splitting on the first 5")
sw = pd.read_csv(f"{IN}/breakdown/sensor_window.csv", comment="#")
event_txt = open(f"{IN}/breakdown/event.txt", encoding="utf-8").read()

ASSET = "VMC-02"
EVENT_TS = pd.Timestamp("2026-11-10T15:24:00-05:00")
STILL_DOWN_TS = pd.Timestamp("2026-11-10T16:10:00-05:00")

a = mh[mh.asset_id == ASSET]
fig("Maintenance records, VMC-02", f"{len(a)} ({', '.join(a.wo)})", "maintenance_history.csv", 'asset_id == "VMC-02"')
TERSE = re.compile(r"^\s*(fixed|repaired|ok|ok now|done|complete[d]?)\.?\s*$", re.I)
usable = a[a.close_out_note.fillna("").apply(lambda s: len(s.strip()) > 15 and not TERSE.match(s))]
fig("VMC-02 records with usable close-out notes", f"{len(usable)} of {len(a)}", "maintenance_history.csv",
    "note non-empty, >15 chars, not a terse 'fixed/repaired/ok' phrase")
fig("Latest VMC-02 maintenance record", a.closed.max(), "maintenance_history.csv", 'max(closed) where asset_id == "VMC-02"')
fig("Latest record in maintenance export (any asset)", mh.closed.max(), "maintenance_history.csv", "max(closed)")
gap = (EVENT_TS.date() - date.fromisoformat(mh.closed.max())).days
fig("Days from latest maintenance record to breakdown", gap, "computed", "2026-11-10 minus max(closed)")
fig("Maintenance work orders dated on or after 2026-11-10", int((mh.opened >= "2026-11-10").sum()), "maintenance_history.csv",
    'opened >= "2026-11-10" -> no ticket for this breakdown in the export')

sib = mh[mh.asset_id.str.startswith("VMC-") & (mh.asset_id != ASSET)]
fig("Sibling records (asset name prefix VMC-, model not in export)", f"{len(sib)} ({', '.join(sib.asset_id + ' ' + sib.wo)})",
    "maintenance_history.csv", 'asset_id startswith "VMC-" and != "VMC-02"')
SYM = r"spindle|bearing|vib|grind|overtemp|overload|hot|noise|drawbar|taper|chiller"
sib_sym = sib[sib.close_out_note.str.contains(SYM, case=False, na=False)]
fig("Sibling records matching the symptom words", f"{len(sib_sym)}" + (f" ({', '.join(sib_sym.wo)})" if len(sib_sym) else " - query returned nothing"),
    "maintenance_history.csv", f'sibling rows, note matches /{SYM}/i')

grp = mh.groupby("close_out_note").agg(n=("wo", "count"), assets=("asset_id", "nunique")).reset_index()
fig("Template check: distinct note texts / texts on >1 asset", f"{len(grp)} / {int((grp.assets > 1).sum())}",
    "maintenance_history.csv", "group by exact close_out_note; count distinct asset_id (model from asset name prefix, no model column)")

for kw, label in [("rough|vib", "bearing/vibration"), ("drawbar|belleville", "drawbar"), ("chiller|hot", "chiller/heat")]:
    hit = a[a.close_out_note.str.contains(kw, case=False)]
    fig(f"VMC-02 notes mentioning {label}", f"{len(hit)} ({', '.join(hit.wo)})", "maintenance_history.csv", f"VMC-02 rows, note matches /{kw}/i")

sw["ts"] = pd.to_datetime(sw.timestamp)
sw = sw[sw.asset_id == ASSET].sort_values("ts")
fig("Sensor rows, VMC-02", len(sw), "sensor_window.csv", 'asset_id == "VMC-02"')
fig("Sensor window", f"{sw.ts.min().isoformat()} to {sw.ts.max().isoformat()}", "sensor_window.csv", "min/max timestamp")
covers = bool(sw.ts.min() < EVENT_TS <= sw.ts.max())
fig("Window covers the 15:24 alarm", "yes - last sample is the alarm minute" if sw.ts.max() == EVENT_TS else str(covers), "sensor_window.csv", "min(ts) < 15:24-05:00 <= max(ts)")
v0, v1 = sw.spindle_vibration_mm_s.iloc[0], sw.spindle_vibration_mm_s.iloc[-1]
fig("Spindle vibration first -> last (mm/s)", f"{v0} -> {v1} ({v1/v0:.1f}x)", "sensor_window.csv", "first and last row")
t0, t1 = sw.spindle_temp_c.iloc[0], sw.spindle_temp_c.iloc[-1]
fig("Spindle temperature first -> last (C)", f"{t0} -> {t1} (+{t1-t0:.1f})", "sensor_window.csv", "first and last row")
l0, l1 = sw.spindle_load_pct.iloc[0], sw.spindle_load_pct.iloc[-1]
fig("Spindle load first -> last (%)", f"{l0} -> {l1}", "sensor_window.csv", "first and last row")
fig("Coolant pressure range (bar)", f"{sw.coolant_pressure_bar.min()} - {sw.coolant_pressure_bar.max()}", "sensor_window.csv", "min/max")
mono = bool(sw.spindle_vibration_mm_s.is_monotonic_increasing and sw.spindle_temp_c.is_monotonic_increasing)
fig("Vibration and temperature rise at every sample", "yes" if mono else "no", "sensor_window.csv", "is_monotonic_increasing on both")
x = sw[sw.spindle_vibration_mm_s > 2.1].iloc[0]
fig("First sample above MW-140's 2.1 mm/s", f"{x.ts.strftime('%H:%M')} ({x.spindle_vibration_mm_s}), {int((EVENT_TS-x.ts).total_seconds()//60)} min before alarm",
    "sensor_window.csv", "first row vibration > 2.1 (MW-140 reading was at 8k rpm; window has no rpm column)")
y = sw[sw.spindle_vibration_mm_s > 2 * v0].iloc[0]
fig("First sample above 2x window-start vibration", f"{y.ts.strftime('%H:%M')} ({y.spindle_vibration_mm_s}), {int((EVENT_TS-y.ts).total_seconds()//60)} min before alarm",
    "sensor_window.csv", f"first row vibration > {2*v0}")
known_down = int((STILL_DOWN_TS - EVENT_TS).total_seconds() // 60)
fig("Known down at least (min), as of 16:10 note", known_down, "event.txt", "16:10 minus 15:24; NOT a duration - end unknown")

# ---------------- Production side (MES / planning exports) ----------------
out = pd.read_csv(f"{IN}/pulse_oee/output.csv")
plan = pd.read_csv(f"{IN}/pulse_oee/plan.csv")
dt = pd.read_csv(f"{IN}/pulse_oee/downtime.csv")
rt = pd.read_csv(f"{IN}/pulse_oee/routing.csv")
wo = pd.read_csv(f"{IN}/pulse_oee/work_orders.csv")

days = sorted(set(out.production_day) | set(plan.plan_date) | set(dt.started_at.str[:10]))
fig("Production days in the drop", ", ".join(days), "output/plan/downtime", "distinct production_day / plan_date / started_at date")
missing = [d.isoformat() for d in pd.date_range("2026-11-13", "2026-11-14").date]
fig("Production days missing before today (2026-11-15)", ", ".join(missing), "computed", "days after latest in drop up to yesterday")
fig("MES downtime rows matching VMC-02", int((dt.asset_id == ASSET).sum()), "downtime.csv", 'asset_id == "VMC-02" (any time)')
fig("VMC-02 rows in plan / output", f"{int((plan.asset_id==ASSET).sum())} / {int((out.asset_id==ASSET).sum())}", "plan.csv, output.csv", 'asset_id == "VMC-02"')
fig("WO-8120 in work_orders export", int((wo.work_order == "WO-8120").sum()), "work_orders.csv", 'work_order == "WO-8120"')
fig("Sites in output export", ", ".join(sorted(out.site.unique())), "output.csv", "distinct site")

dt["s"] = pd.to_datetime(dt.started_at); dt["e"] = pd.to_datetime(dt.ended_at)
dt["calc"] = ((dt.e - dt.s).dt.total_seconds() // 60).astype(int)
bad = dt[(dt.e < dt.s) | (dt.calc != dt.duration_minutes)]
fig("Downtime rows failing end/start/duration check", len(bad), "downtime.csv", "ended<started or minutes != stated")
oth = dt[dt.reason_code.isna() | dt.reason_code.str.upper().isin(["OTHER", ""])]
fig("Downtime events with no usable reason code", f"{len(oth)} of {len(dt)}", "downtime.csv", "reason_code blank or Other")
fig("Downtime timestamps carry a zone", "no - naive (plant zone not on file)", "downtime.csv", "started_at format")

rows = []
for _, p in plan.iterrows():
    o = out[(out.asset_id == p.asset_id) & (out.part_number == p.part_number) & (out.production_day == p.plan_date)]
    good, scrap = int(o.qty_good.sum()), int(o.qty_scrap.sum())
    total = good + scrap
    planned_min = p.planned_hours * 60
    down = int(dt[(dt.asset_id == p.asset_id) & (dt.started_at.str[:10] == p.plan_date)].duration_minutes.sum())
    run = planned_min - down
    ict = float(rt[rt.part_number == p.part_number].run_min_per_unit.iloc[0])
    A, P, Q = run / planned_min, ict * total / run, good / total
    r = dict(asset=p.asset_id, cell=o.cell.iloc[0], part=p.part_number, shifts=",".join(map(str, sorted(o["shift"].unique()))),
             plan=int(p.planned_qty), good=good, scrap=scrap, total=total, var=good - int(p.planned_qty),
             pct=good / p.planned_qty, planned_min=int(planned_min), down=down, run=int(run), ict=ict,
             A=A, P=P, Q=Q, OEE=A * P * Q)
    rows.append(r)
    fig(f"{r['asset']} {r['part']} good / plan", f"{good} / {r['plan']} ({r['pct']:.1%}, {r['var']:+d})", "output.csv, plan.csv", f"asset_id=={r['asset']}, part=={r['part']}, day {p.plan_date}")
    fig(f"{r['asset']} scrap units", scrap, "output.csv", f"sum qty_scrap, asset_id=={r['asset']}")
    fig(f"{r['asset']} availability", f"{A:.1%} ({int(run)}/{int(planned_min)} min)", "plan.csv, downtime.csv", "(planned_hours*60 - downtime min)/planned")
    fig(f"{r['asset']} performance", f"{P:.1%} ({ict} min x {total} / {int(run)} min)", "routing.csv, output.csv", "ideal min/unit x (good+scrap) / run min")
    fig(f"{r['asset']} quality", f"{Q:.1%} ({good}/{total})", "output.csv", "good/(good+scrap)")
    fig(f"{r['asset']} OEE", f"{A*P*Q:.1%}", "computed", "A x P x Q from the three rows above")
tg, tp, ts_ = sum(r["good"] for r in rows), sum(r["plan"] for r in rows), sum(r["scrap"] for r in rows)
fig("Plant good / plan, 2026-11-12", f"{tg} / {tp} ({tg/tp:.1%})", "output.csv, plan.csv", "sum over plan rows")
fig("Total output (good+scrap)", tg + ts_, "output.csv", "sum")
fig("Scrap units, 2026-11-12", ts_, "output.csv", "sum qty_scrap")
fig("MES downtime minutes, 2026-11-12", int(dt.duration_minutes.sum()), "downtime.csv", "sum duration_minutes (diagnosis record excluded: null duration, production_day 2026-11-10)")
fig("MES downtime events, 2026-11-12", len(dt), "downtime.csv", "count rows")
pm = sum(r["planned_min"] for r in rows); dm = sum(r["down"] for r in rows)
idl = sum(r["ict"] * r["total"] for r in rows); rn = sum(r["run"] for r in rows)
A_, P_, Q_ = (pm - dm) / pm, idl / rn, tg / (tg + ts_)
fig("Plant availability / performance / quality / OEE (time-weighted)", f"{A_:.1%} / {P_:.1%} / {Q_:.1%} / {A_*P_*Q_:.1%}", "computed", "pooled minutes and counts across both assets")

wos = []
for _, w in wo.iterrows():
    o = out[out.work_order == w.work_order]
    g = int(o.qty_good.sum())
    wos.append(dict(wo=w.work_order, part=w.part_number, ordered=int(w.qty_ordered), good=g, short=int(w.qty_ordered) - g,
                    due=w.due_date, status=w.status, past_due=w.due_date < RUN_DATE.isoformat()))
    fig(f"{w.work_order} good vs ordered (through 2026-11-12)", f"{g} / {w.qty_ordered}, due {w.due_date}", "output.csv, work_orders.csv", f"work_order == {w.work_order}")
fig("Work orders with a sales-order link", "0 - no sales_order column in work_orders.csv", "work_orders.csv", "column check")

res = dict(F=F, rows=rows, wos=wos, dt=dt.drop(columns=["s", "e"]).to_dict("records"),
           sensor=sw.drop(columns=["ts"]).to_dict("records"), mh=mh.to_dict("records"),
           grp=grp.to_dict("records"), plant=dict(A=A_, P=P_, Q=Q_, OEE=A_*P_*Q_, good=tg, plan=tp, scrap=ts_))
json.dump(res, open(f"{OUT}/figures.json", "w"), indent=2, default=str)
for f_ in F:
    print(f"{f_['figure']:<62} | {f_['value']}")
