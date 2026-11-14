"""Chain 4 (breakdown-to-next-report) computation for the B13 run.
Reads only C:/LMFG/runs/B13-positive/work/inputs, writes only under .../work/out.
Every figure printed in the outputs comes from FIG below (the figures block).
"""
import csv, json, os, re, html
from datetime import datetime, timezone, timedelta
from collections import defaultdict, Counter

BASE = r"C:/LMFG/runs/B13-positive/work"
INP = BASE + "/inputs"
OUT = BASE + "/out"
RUN_AT = datetime.now(timezone(timedelta(hours=-5)))  # host clock shows -05:00 file times

def read_csv(path):
    with open(path, encoding="utf-8") as f:
        lines = [l for l in f if not l.startswith("#")]
    return list(csv.DictReader(lines))

FIG = []  # rows: figure, value, source, filter
def fig(name, value, source, filt):
    FIG.append({"figure": name, "value": value, "source": source, "filter": filt})
    return value

# ---------------- inputs ----------------
mh = read_csv(INP + "/breakdown/maintenance_history.csv")
sw = read_csv(INP + "/breakdown/sensor_window.csv")
event_txt = open(INP + "/breakdown/event.txt", encoding="utf-8").read()
manual = open(INP + "/breakdown/manual_troubleshooting.md", encoding="utf-8").read()
dt = read_csv(INP + "/pulse_oee/downtime.csv")
outp = read_csv(INP + "/pulse_oee/output.csv")
plan = read_csv(INP + "/pulse_oee/plan.csv")
rout = read_csv(INP + "/pulse_oee/routing.csv")
wos = read_csv(INP + "/pulse_oee/work_orders.csv")

ASSET = "VMC-02"

# ---------------- source freshness ----------------
def mtime(p):
    return datetime.fromtimestamp(os.path.getmtime(p), timezone(timedelta(hours=-5))).isoformat(timespec="seconds")
src = {}
for p in ["breakdown/event.txt", "breakdown/maintenance_history.csv", "breakdown/sensor_window.csv",
          "breakdown/manual_troubleshooting.md", "pulse_oee/downtime.csv", "pulse_oee/output.csv",
          "pulse_oee/plan.csv", "pulse_oee/routing.csv", "pulse_oee/work_orders.csv", "rates_memo.txt"]:
    src[p] = mtime(INP + "/" + p)
prod_days = sorted({r["production_day"] for r in outp})
plan_days = sorted({r["plan_date"] for r in plan})
dt_days = sorted({r["started_at"][:10] for r in dt})
fig("Production days in output export", ", ".join(prod_days), "pulse_oee/output.csv", "distinct production_day")
fig("Plan dates in plan export", ", ".join(plan_days), "pulse_oee/plan.csv", "distinct plan_date")
fig("Start dates in MES downtime export", ", ".join(dt_days), "pulse_oee/downtime.csv", "distinct started_at[:10]")
mh_last = max(r["closed"] for r in mh)
fig("Latest close date in maintenance export", mh_last, "breakdown/maintenance_history.csv", "max(closed)")
ev_date = "2026-11-10"
gap_mh = (datetime.fromisoformat(ev_date) - datetime.fromisoformat(mh_last)).days
fig("Days from last maintenance record to breakdown", gap_mh, "maintenance export + event.txt", "2026-11-10 minus max(closed)")
gap_day = (datetime.fromisoformat(prod_days[-1]) - datetime.fromisoformat(ev_date)).days
fig("Days between breakdown date and report production day", gap_day, "event.txt + output.csv", "production_day minus 2026-11-10")
naive_dt = [r for r in dt if not re.search(r"(Z|[+-]\d\d:\d\d)$", r["started_at"])]
fig("MES downtime rows with naive (zone-less) timestamps", f"{len(naive_dt)} of {len(dt)}", "pulse_oee/downtime.csv", "started_at has no zone suffix")
future = [p for p, t in src.items() if datetime.fromisoformat(t) > RUN_AT]
fig("Sources with a timestamp later than run time", len(future), "file modified times", "mtime > run time")

# ---------------- breakdown: sensor window ----------------
for r in sw:
    for k in ("spindle_vibration_mm_s", "spindle_temp_c", "spindle_load_pct", "coolant_pressure_bar"):
        r[k] = float(r[k])
sw_rows = [r for r in sw if r["asset_id"] == ASSET]
fig("Sensor rows for VMC-02", len(sw_rows), "breakdown/sensor_window.csv", "asset_id == 'VMC-02'")
t0, t1 = sw_rows[0]["timestamp"], sw_rows[-1]["timestamp"]
fig("Sensor window", f"{t0} to {t1}", "sensor_window.csv", "min/max timestamp")
alarm = "2026-11-10T15:24:00-05:00"
fig("Sensor window reaches the alarm minute", t1 == alarm, "sensor_window.csv + event.txt", f"last timestamp == {alarm}")
v0, v1 = sw_rows[0]["spindle_vibration_mm_s"], sw_rows[-1]["spindle_vibration_mm_s"]
fig("Vibration first / last (mm/s)", f"{v0} / {v1}", "sensor_window.csv", "first and last VMC-02 row")
fig("Vibration last ÷ first", round(v1 / v0, 2), "sensor_window.csv", "11.2 / 1.8 from the same rows")
vib_monotonic = all(sw_rows[i+1]["spindle_vibration_mm_s"] >= sw_rows[i]["spindle_vibration_mm_s"] for i in range(len(sw_rows)-1))
fig("Vibration never fell between samples", vib_monotonic, "sensor_window.csv", "each row >= previous")
T0, T1 = sw_rows[0]["spindle_temp_c"], sw_rows[-1]["spindle_temp_c"]
fig("Spindle temp first / last (°C)", f"{T0} / {T1}", "sensor_window.csv", "first and last row")
fig("Spindle temp rise (°C)", round(T1 - T0, 1), "sensor_window.csv", "last - first")
L0, L1 = sw_rows[0]["spindle_load_pct"], sw_rows[-1]["spindle_load_pct"]
fig("Spindle load first / last (%)", f"{L0:g} / {L1:g}", "sensor_window.csv", "first and last row")
cp = [r["coolant_pressure_bar"] for r in sw_rows]
fig("Coolant pressure range (bar)", f"{min(cp)} to {max(cp)}", "sensor_window.csv", "min/max coolant_pressure_bar")
# rate of vibration rise per minute between samples
rates = []
for a, b in zip(sw_rows, sw_rows[1:]):
    mins = (datetime.fromisoformat(b["timestamp"]) - datetime.fromisoformat(a["timestamp"])).total_seconds() / 60
    rates.append((a["timestamp"][11:16], b["timestamp"][11:16], round((b["spindle_vibration_mm_s"] - a["spindle_vibration_mm_s"]) / mins, 3)))
fig("Vibration rise rate per interval (mm/s per min)", "; ".join(f"{a}-{b}: {r}" for a, b, r in rates), "sensor_window.csv", "Δvibration / Δminutes per consecutive pair")
fig("Sensor channels present", "vibration, temp, load, coolant pressure (no spindle rpm, no chiller flow/level)", "sensor_window.csv header", "column list")
still_down_obs = "2026-11-10T16:10:00-05:00"
mins_obs = int((datetime.fromisoformat(still_down_obs) - datetime.fromisoformat(alarm)).total_seconds() / 60)
fig("Minutes from alarm to last 'still down' observation (lower bound, not a duration)", mins_obs, "event.txt", "16:10 - 15:24")

# ---------------- breakdown: maintenance history ----------------
asset_q = [r for r in mh if r["asset_id"] == ASSET]
fig("Maintenance records, VMC-02", f"{len(asset_q)} ({', '.join(r['wo'] for r in asset_q)})", "maintenance_history.csv", "asset_id == 'VMC-02'")
terse = re.compile(r"^\s*(fixed|repaired|ok now|ok|done)\.?\s*$", re.I)
usable = [r for r in asset_q if r["close_out_note"].strip() and not terse.match(r["close_out_note"])]
fig("VMC-02 records with substantive close-out notes", f"{len(usable)} of {len(asset_q)}", "maintenance_history.csv", "note non-empty and not just fixed/repaired/ok")
model_prefix = ASSET.split("-")[0]
sib_assets = sorted({r["asset_id"] for r in mh if r["asset_id"] != ASSET and r["asset_id"].split("-")[0] == model_prefix})
fig("Sibling assets (model taken from asset-name prefix 'VMC'; no model column)", ", ".join(sib_assets) or "none", "maintenance_history.csv", "asset_id prefix == 'VMC' and != VMC-02")
sym_words = ["spindle", "bearing", "vib", "overtemp", "overload", "temp", "hot", "grind", "noise", "rough", "drawbar", "chiller", "taper"]
sib_q = [r for r in mh if r["asset_id"] in sib_assets and any(w in r["close_out_note"].lower() for w in sym_words)]
fig("Sibling records matching symptom words", f"{len(sib_q)} — none returned" if not sib_q else ", ".join(r["wo"] for r in sib_q),
    "maintenance_history.csv", "sibling asset AND note contains any of " + "/".join(sym_words))
groups = defaultdict(set)
for r in mh:
    groups[r["close_out_note"].strip()].add(r["asset_id"])
templ = {k: v for k, v in groups.items() if len(v) > 1}
fig("Close-out note texts grouped (exact text)", f"{len(groups)} distinct texts across {len(mh)} records; texts on >1 asset: {len(templ)}",
    "maintenance_history.csv", "group by exact close_out_note; count distinct asset_id")
def has(r, *ws): return any(w in r["close_out_note"].lower() for w in ws)
bearing_q = [r["wo"] for r in asset_q if has(r, "rough", "vib", "bearing")]
chiller_q = [r["wo"] for r in asset_q if has(r, "chiller", "hot", "temp")]
drawbar_q = [r["wo"] for r in asset_q if has(r, "drawbar", "clamp", "belleville")]
fig("VMC-02 notes citing rough/vibration/bearing", ", ".join(bearing_q), "maintenance_history.csv", "VMC-02 AND note contains rough|vib|bearing")
fig("VMC-02 notes citing chiller/hot/temp", ", ".join(chiller_q), "maintenance_history.csv", "VMC-02 AND note contains chiller|hot|temp")
fig("VMC-02 notes citing drawbar/clamp/belleville", ", ".join(drawbar_q), "maintenance_history.csv", "VMC-02 AND note contains drawbar|clamp|belleville")
pm_q = [r for r in asset_q if r["type"] == "PM"]
fig("VMC-02 PM records", ", ".join(f"{r['wo']} ({r['opened']})" for r in pm_q), "maintenance_history.csv", "VMC-02 AND type == PM")
pm_gap = (datetime.fromisoformat(pm_q[-1]["opened"]) - datetime.fromisoformat(pm_q[0]["opened"])).days
fig("Days between the two VMC-02 PMs", pm_gap, "maintenance_history.csv", "MW-140.opened - MW-118.opened")
days_since_pm = (datetime.fromisoformat(ev_date) - datetime.fromisoformat(pm_q[-1]["opened"])).days
fig("Days from last PM in export to breakdown", days_since_pm, "maintenance_history.csv + event.txt", "2026-11-10 - MW-140.opened")
open_mwo = [r for r in mh if not r["closed"].strip()]
fig("Open maintenance WOs in export", len(open_mwo), "maintenance_history.csv", "closed is blank")

# ---------------- production: output vs plan ----------------
for r in outp:
    r["qty_good"] = int(r["qty_good"]); r["qty_scrap"] = int(r["qty_scrap"])
for r in plan:
    r["planned_qty"] = int(r["planned_qty"]); r["planned_hours"] = float(r["planned_hours"])
rt = {r["part_number"]: float(r["run_min_per_unit"]) for r in rout}
good_by_part = defaultdict(int); scrap_by_part = defaultdict(int)
for r in outp:
    good_by_part[r["part_number"]] += r["qty_good"]; scrap_by_part[r["part_number"]] += r["qty_scrap"]
oap = []
for p in plan:
    g = good_by_part.get(p["part_number"], 0); s = scrap_by_part.get(p["part_number"], 0)
    v = g - p["planned_qty"]
    oap.append({"part": p["part_number"], "asset": p["asset_id"], "plan": p["planned_qty"], "good": g, "total": g + s, "scrap": s,
                "var": v, "var_pct": round(100 * v / p["planned_qty"], 1)})
    fig(f"Output vs plan {p['part_number']}", f"plan {p['planned_qty']}, good {g}, total {g+s}, variance {v} ({round(100*v/p['planned_qty'],1)}%)",
        "plan.csv + output.csv", f"part_number == {p['part_number']}, day 2026-11-12")
tot_plan = sum(p["planned_qty"] for p in plan); tot_good = sum(good_by_part.values()); tot_scrap = sum(scrap_by_part.values())
fig("Plant good vs plan (CELL-A, SITE-1)", f"good {tot_good} vs plan {tot_plan} = {round(100*tot_good/tot_plan,1)}%; total {tot_good+tot_scrap}", "plan.csv + output.csv", "all rows, 2026-11-12")
fig("Scrap units", f"{tot_scrap} ({', '.join(f'{k}: {v}' for k,v in sorted(scrap_by_part.items()))})", "output.csv", "sum qty_scrap by part")
plan_parts = {p["part_number"] for p in plan}; out_parts = set(good_by_part); rout_parts = set(rt); wo_parts = {w["part_number"] for w in wos}
fig("Part keys matched exactly across plan/output/routing/WO", f"{len(plan_parts & out_parts & rout_parts & wo_parts)} of {len(plan_parts | out_parts | rout_parts | wo_parts)}",
    "pulse_oee exports", "set intersection on part_number, no normalization")
shifts = sorted({(r["asset_id"], r["shift"]) for r in outp})
fig("Shifts in output export", "; ".join(f"{a} shift {s}" for a, s in shifts), "output.csv", "distinct asset_id, shift")

# ---------------- OEE per asset ----------------
dt_by_asset = defaultdict(int)
dt_check = []
for r in dt:
    s = datetime.fromisoformat(r["started_at"]); e = datetime.fromisoformat(r["ended_at"])
    calc = int((e - s).total_seconds() / 60); stated = int(r["duration_minutes"])
    ok = e >= s and calc == stated
    dt_check.append((r["asset_id"], ok))
    if ok: dt_by_asset[r["asset_id"]] += stated
fig("MES downtime rows passing start/end/duration check", f"{sum(1 for _, ok in dt_check if ok)} of {len(dt_check)}", "downtime.csv", "ended_at >= started_at and minutes == stated")
oee = []
for p in plan:
    a = p["asset_id"]; ppt = p["planned_hours"] * 60
    rows = [r for r in outp if r["asset_id"] == a]
    good = sum(r["qty_good"] for r in rows); total = good + sum(r["qty_scrap"] for r in rows)
    run = ppt - dt_by_asset[a]
    ideal = sum((r["qty_good"] + r["qty_scrap"]) * rt[r["part_number"]] for r in rows)
    A = run / ppt; P = ideal / run; Q = good / total
    oee.append({"asset": a, "ppt": ppt, "down": dt_by_asset[a], "run": run, "ideal": ideal, "good": good, "total": total,
                "A": A, "P": P, "Q": Q, "OEE": A * P * Q})
    fig(f"OEE {a}", f"A {A:.1%}, P {P:.1%}, Q {Q:.1%}, OEE {A*P*Q:.1%} (planned {ppt:g} min, down {dt_by_asset[a]} min, run {run:g} min, ideal {ideal:g} min, good {good}/{total})",
        "plan.csv + downtime.csv + output.csv + routing.csv", f"asset_id == {a}")
cppt = sum(o["ppt"] for o in oee); crun = sum(o["run"] for o in oee); cideal = sum(o["ideal"] for o in oee)
cgood = sum(o["good"] for o in oee); ctot = sum(o["total"] for o in oee)
CA, CP, CQ = crun / cppt, cideal / crun, cgood / ctot
fig("OEE CELL-A (time-weighted over CNC-01, CNC-02)", f"A {CA:.1%}, P {CP:.1%}, Q {CQ:.1%}, OEE {CA*CP*CQ:.1%}", "same", "sums of planned/run/ideal minutes and counts")
fig("Assets in plan without output", ", ".join(sorted({p['asset_id'] for p in plan} - {r['asset_id'] for r in outp})) or "none", "plan.csv vs output.csv", "plan assets not in output")
fig("VMC-02 rows in plan / output / MES downtime", f"{sum(1 for p in plan if p['asset_id']==ASSET)} / {sum(1 for r in outp if r['asset_id']==ASSET)} / {sum(1 for r in dt if r['asset_id']==ASSET)}",
    "plan.csv, output.csv, downtime.csv", "asset_id == 'VMC-02'")
fig("WO-8120 / MB-1880 in work_orders, routing, plan", f"WO-8120: {sum(1 for w in wos if w['work_order']=='WO-8120')}; MB-1880 routing: {sum(1 for r in rout if r['part_number']=='MB-1880')}; MB-1880 plan: {sum(1 for p in plan if p['part_number']=='MB-1880')}",
    "work_orders.csv, routing.csv, plan.csv", "exact key match")

# ---------------- downtime log (MES rows + carried breakdown record) ----------------
mes_total = sum(int(r["duration_minutes"]) for r in dt)
fig("MES downtime, 2026-11-12", f"{len(dt)} events, {mes_total} min", "downtime.csv", "all rows")
by_code_min = Counter(); by_code_n = Counter()
for r in dt:
    by_code_min[r["reason_code"]] += int(r["duration_minutes"]); by_code_n[r["reason_code"]] += 1
fig("Downtime by reason code (minutes)", "; ".join(f"{k} {v}" for k, v in by_code_min.most_common()), "downtime.csv", "sum minutes by reason_code")
fig("Downtime by reason code (events)", "; ".join(f"{k} {v}" for k, v in sorted(by_code_n.items(), key=lambda x: (-x[1], x[0]))), "downtime.csv", "count by reason_code")
blank = [r for r in dt if r["reason_code"].strip() == "" or r["reason_code"].strip().lower() == "other"]
fig("MES events coded Other or blank", f"{len(blank)} of {len(dt)}", "downtime.csv", "reason_code blank or 'Other'")
match_rows = [r for r in dt if r["asset_id"] == ASSET]
fig("MES rows matching the diagnosis record (asset + start within shift)", len(match_rows), "downtime.csv", "asset_id == 'VMC-02' (no rows, so start-time test not reached)")

# ---------------- work orders / exceptions ----------------
wo_rows = []
for w in wos:
    rows = [r for r in outp if r["work_order"] == w["work_order"]]
    g = sum(r["qty_good"] for r in rows); s = sum(r["qty_scrap"] for r in rows)
    short = int(w["qty_ordered"]) - g
    wo_rows.append({**w, "good": g, "scrap": s, "short": short})
    fig(f"{w['work_order']} good on 2026-11-12 vs ordered", f"{g} of {w['qty_ordered']} (short {short}), scrap {s}, due {w['due_date']}", "work_orders.csv + output.csv", f"work_order == {w['work_order']}")
fig("Work orders with a sales_order column", "0 — no sales_order column in work_orders.csv", "work_orders.csv header", "column list")
past_due = [w["work_order"] for w in wo_rows if w["short"] > 0 and w["due_date"] < RUN_AT.date().isoformat()]
fig("Short WOs whose due date is before run date " + RUN_AT.date().isoformat(), ", ".join(past_due) or "none", "work_orders.csv", "short > 0 and due_date < run date")

json.dump({"run_at": RUN_AT.isoformat(timespec="seconds"), "sources_modified": src, "figures": FIG}, open(OUT + "/figures.json", "w", encoding="utf-8"), indent=2, ensure_ascii=False)

# ---------------- downtime record (contract v3) ----------------
record = {
    "contract_version": 3,
    "site": None,
    "asset_id": "VMC-02", "asset_id_verbatim": "VMC-02",
    "started_at": alarm,
    "ended_at": None, "duration_minutes": None,
    "reason_code": None,
    "reason_text": "SPINDLE OVERLOAD / OVERTEMP; grinding noise from spindle ~20 min before alarm (operator)",
    "production_wo": "WO-8120", "production_wo_verbatim": "WO-8120",
    "shift": None,
    "production_day": "2026-11-10",
    "source_system": "breakdown_diagnosis",
    "source_ref": "diagnosis/2026-11-10/VMC-02 (inputs/breakdown/event.txt)",
    "diagnosis_ref": "out/diagnosis/VMC-02-2026-11-10-diagnosis.html",
    "leading_cause": "Spindle bearing damage / preload loss (progressive wear)",
    "leading_cause_confidence": "high",
    "cited_work_orders": ["MW-118", "MW-140"],
    "safety_flagged": True,
    "safety_reason": ("electrical fault: a trip - spindle drive stopped mid-cycle on 'SPINDLE OVERLOAD / OVERTEMP' (event.txt); "
                      "rotating-part hazard per OEM manual 7.4: grinding noise reported, 'do not run a spindle showing grinding noise', "
                      "lock out the spindle drive before manual rotation; drawbar Belleville stack is stored spring energy if the clamp check is done"),
    "pm_adjustment_proposed": True,
    "maintenance_wo": None,
    "diagnosis_state": "advisory",
    "technician_step": "pending",
}
def yv(v):
    if v is None: return "null"
    if v is True: return "true"
    if v is False: return "false"
    if isinstance(v, int): return str(v)
    if isinstance(v, list): return "[" + ", ".join(json.dumps(x) for x in v) + "]"
    return json.dumps(v, ensure_ascii=False)
notes = {
    "site": "not stated in the breakdown inputs; no plant profile on file. Unresolved, not assumed to be SITE-1",
    "started_at": "event.txt says 15:24 local; zone -05:00 taken from the historian row for VMC-02 at the same minute (sensor_window.csv)",
    "ended_at": "machine still down at 16:10 per event.txt; no end recorded",
    "reason_code": "no plant reason code given; alarm text kept verbatim in reason_text",
    "shift": "unresolved: no shift pattern on file",
    "production_day": "calendar day of started_at; site day-boundary rule not on file (unconfirmed)",
    "production_wo": "WO-8120 op 20 (MB-1880) per event.txt; not present in work_orders.csv",
    "maintenance_wo": "no maintenance ticket number given; no CMMS connector",
}
with open(OUT + "/records/downtime-record_VMC-02_2026-11-10.yaml", "w", encoding="utf-8") as f:
    f.write("# Downtime record, contract v3 (shared/contracts/downtime-record.md). Draft, advisory. Not written to any system.\n")
    for k, v in record.items():
        f.write(f"{k}: {yv(v)}" + (f"   # {notes[k]}" if k in notes else "") + "\n")

# downtime_events log as the report consumes it: MES rows as-is + the record appended (no transformation)
cols = ["asset_id", "started_at", "ended_at", "duration_minutes", "reason_code", "reason_text", "production_day", "source_system",
        "safety_flagged", "leading_cause", "leading_cause_confidence", "diagnosis_state", "technician_step", "note"]
with open(OUT + "/dataset/downtime_events.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=cols); w.writeheader()
    for r in dt:
        w.writerow({"asset_id": r["asset_id"], "started_at": r["started_at"], "ended_at": r["ended_at"], "duration_minutes": r["duration_minutes"],
                    "reason_code": r["reason_code"], "reason_text": r["reason_text"], "production_day": r["started_at"][:10], "source_system": "mes_export",
                    "note": "naive timestamp in source; zone unresolved (no source-clock declaration on file)"})
    w.writerow({"asset_id": "VMC-02", "started_at": alarm, "ended_at": "", "duration_minutes": "", "reason_code": "", "reason_text": record["reason_text"],
                "production_day": "2026-11-10", "source_system": "breakdown_diagnosis", "safety_flagged": "true", "leading_cause": record["leading_cause"],
                "leading_cause_confidence": "high", "diagnosis_state": "advisory", "technician_step": "pending",
                "note": "ongoing as of 2026-11-10 16:10; null duration; no MES row matched; counted once"})
with open(OUT + "/dataset/oee_by_asset.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f); w.writerow(["asset_id", "planned_min", "unplanned_down_min", "run_min", "ideal_min", "good", "total", "availability", "performance", "quality", "oee"])
    for o in oee:
        w.writerow([o["asset"], o["ppt"], o["down"], o["run"], round(o["ideal"], 1), o["good"], o["total"], round(o["A"], 4), round(o["P"], 4), round(o["Q"], 4), round(o["OEE"], 4)])
with open(OUT + "/dataset/figures_block.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=["figure", "value", "source", "filter"]); w.writeheader(); w.writerows(FIG)

# ---------------- HTML ----------------
F = {r["figure"]: r["value"] for r in FIG}
E = html.escape
CSS = """
:root{--ink:#1A1D21;--paper:#F2F3F5;--paper-raised:#FFFFFF;--line:#D6D9DD;--accent:#1F5C8B;--accent-soft:#E4EDF4;--good:#2E7248;--good-soft:#E3EFE7;--warn:#A8641A;--warn-soft:#F7EBDA;--critical:#A93226;--critical-soft:#F9E9E7;
--font-display:'IBM Plex Sans Condensed','Arial Narrow',sans-serif;--font-body:'IBM Plex Sans',-apple-system,BlinkMacSystemFont,sans-serif;--font-mono:'IBM Plex Mono','SF Mono',Consolas,monospace}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){--ink:#E8EAEC;--paper:#15181B;--paper-raised:#1D2126;--line:#2E343A;--accent:#6BA8D4;--accent-soft:#1B2C39;--good:#6FBF88;--good-soft:#1B2E22;--warn:#D9A15C;--warn-soft:#33271A;--critical:#DE8378;--critical-soft:#35201E}}
:root[data-theme="dark"]{--ink:#E8EAEC;--paper:#15181B;--paper-raised:#1D2126;--line:#2E343A;--accent:#6BA8D4;--accent-soft:#1B2C39;--good:#6FBF88;--good-soft:#1B2E22;--warn:#D9A15C;--warn-soft:#33271A;--critical:#DE8378;--critical-soft:#35201E}
body{background:var(--paper);color:var(--ink);font-family:var(--font-body);margin:0;padding:16px;line-height:1.45}
main{max-width:1080px;margin:0 auto;display:flex;flex-direction:column;gap:14px}
h1,h2,h3{font-family:var(--font-display);font-weight:600;margin:0 0 8px}
h1{font-size:1.75rem}h2{font-size:1.375rem}h3{font-size:1.125rem;margin-top:10px}
.panel{background:var(--paper-raised);border:1px solid var(--line);border-radius:4px;padding:14px 16px}
.critical{background:var(--critical-soft);border-color:var(--critical)}.warn{background:var(--warn-soft);border-color:var(--warn)}
.tw{overflow-x:auto}table{border-collapse:collapse;width:100%;font-size:.875rem}th,td{border-bottom:1px solid var(--line);padding:5px 8px;text-align:left;vertical-align:top}
th{font-family:var(--font-display);font-weight:600}td.n,.mono{font-family:var(--font-mono);font-variant-numeric:tabular-nums}
.pill{display:inline-block;padding:1px 8px;border-radius:10px;font-size:.75rem;background:var(--accent-soft);color:var(--accent)}
.pill.c{background:var(--critical-soft);color:var(--critical)}.pill.w{background:var(--warn-soft);color:var(--warn)}
.tiles{display:grid;grid-template-columns:repeat(auto-fit,minmax(170px,1fr));gap:10px}.tile{border:1px solid var(--line);border-radius:4px;padding:10px;background:var(--paper-raised)}
.tile .v{font-family:var(--font-mono);font-size:1.375rem}.tile .l{font-size:.75rem}
details summary{cursor:pointer;font-family:var(--font-display);font-weight:600;font-size:1.125rem}
small,.muted{font-size:.8rem;opacity:.85}
"""
HEAD = '<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{t}</title><link rel="preconnect" href="https://fonts.googleapis.com"><link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans+Condensed:wght@500;600&family=IBM+Plex+Sans:wght@400;500;600&family=IBM+Plex+Mono:wght@500&display=swap" rel="stylesheet"><style>' + CSS + '</style></head><body><main>'
def table(headers, rows, numcols=()):
    h = "".join(f"<th>{E(x)}</th>" for x in headers)
    b = "".join("<tr>" + "".join(f'<td class="{"n" if i in numcols else ""}">{x}</td>' for i, x in enumerate(r)) + "</tr>" for r in rows)
    return f'<div class="tw"><table><thead><tr>{h}</tr></thead><tbody>{b}</tbody></table></div>'
fig_table = table(["Figure", "Value", "Computed from", "Filter or query"], [[E(r["figure"]), f'<span class="mono">{E(str(r["value"]))}</span>', E(r["source"]), f'<span class="mono">{E(r["filter"])}</span>'] for r in FIG])

SAFETY = f"""<section class="panel critical"><h2>Safety first: VMC-02 <span class="pill c">safety_flagged: true</span></h2>
<p><strong>Follow your plant's lockout procedure before anyone works on this machine. This is not a safety assessment.</strong></p>
<ul>
<li><strong>Do not run the spindle.</strong> Grinding noise was reported for about 20 minutes before the alarm, and the OEM manual (Section 7.4, Grinding noise row and SAFETY note) says not to run a spindle showing grinding noise.</li>
<li><strong>Lock out the spindle drive</strong> before any manual rotation or inspection (manual 7.4 SAFETY note). The drive tripped mid-cycle on <span class="mono">SPINDLE OVERLOAD / OVERTEMP</span>: trigger <em>electrical fault: a trip</em>.</li>
<li><strong>Hot surface:</strong> last spindle temperature in the historian was <span class="mono">{E(F['Spindle temp first / last (°C)'].split(' / ')[1])} °C</span>, and blue discolouration was described at the spindle nose / taper.</li>
<li><strong>Stored energy:</strong> if the drawbar clamp is checked (candidate 3), the Belleville spring stack is stored spring energy; use the OEM procedure.</li>
</ul></section>"""

cand = """
<section class="panel"><h2>Ranked candidate causes <span class="pill w">advisory, technician step pending</span></h2>
<h3>1. Spindle bearing damage / preload loss (progressive wear) <span class="pill">confidence: high</span></h3>
<p><strong>Evidence.</strong> Sensor: vibration rose every sample from {v} mm/s ({vr}x), temperature rose {tr} °C, load {ld} %; the rise accelerated in the last 24 minutes (rates: {rates}). That is the steady-climb shape of progressive wear, and the OEM tree's first row, <em>Overtemp with rising vibration → spindle bearing wear / preload loss</em>. Operator: grinding noise about 20 minutes before the alarm (manual: <em>Grinding noise → bearing damage or contamination</em>). Photo description (no photo file): bluish discolouration at the spindle nose / taper, consistent with heat there but not, on its own, a diagnosis. History: <span class="mono">MW-118</span> (2026-03-02, PM) <em>"spindle sounded a bit rough at 8k, monitor"</em>; <span class="mono">MW-140</span> (2026-07-08, PM) <em>"vib reading 2.1 mm/s at 8k (was 1.4 last yr). told sup"</em>. Two PMs logged the same developing condition and no corrective work order follows in the export.</p>
<p><strong>First check.</strong> Under lockout, rotate the spindle by hand and feel for roughness or notchiness (manual 7.4, Grinding noise row), then indicate run-out at the taper against the OEM limit of &lt; 3 µm (manual 7.4, row 1). Do not run the spindle for a vibration spectrum while grinding is present. Rough rotation or run-out over 3 µm confirms this candidate and makes candidates 2 and 3 contributors at most.</p>
<p><strong>Expected fix and repair path.</strong> Spindle bearing replacement or spindle cartridge rebuild per OEM; inspect the taper and spindle nose for heat damage given the discolouration; after rebuild, record a baseline vibration reading. Check candidate 2 (cooling) before restart so the new bearings are not run hot.</p>
<p class="muted">Cited: MW-118, MW-140.</p>

<h3>2. Spindle chiller low flow / low fluid level <span class="pill">confidence: medium as a contributor, low as the sole cause</span></h3>
<p><strong>Evidence.</strong> <span class="mono">MW-160</span> (2026-09-23, CM) <em>"spindle hot after long cycle. checked chiller - low on fluid topped up. temp ok after"</em>: the same machine overheated about seven weeks earlier from low chiller fluid; no follow-up on why the level dropped. Against it as the sole cause: the OEM tree's chiller row is <em>Overtemp, normal vibration</em>, and vibration here rose {vr}x. The historian export has no chiller flow or level channel; coolant pressure ({cp} bar) is flat but that is cutting-coolant, not the spindle chiller, so it does not test this candidate.</p>
<p><strong>First check.</strong> Chiller fluid level and flow (manual 7.4, row 2). Five minutes, no spindle rotation needed. Low level again points to a leak or consumption since MW-160 and to a cooling contribution to the overtemp.</p>
<p><strong>Expected fix and repair path.</strong> Restore level and flow, find where the fluid is going (leak check on lines and fittings), and confirm before any spindle restart.</p>
<p class="muted">Cited: MW-160.</p>

<h3>3. Drawbar clamp force low <span class="pill">confidence: low</span></h3>
<p><strong>Evidence.</strong> <span class="mono">MW-131</span> (2026-05-19, CM) <em>"spindle alarm 2nd shift. found drawbar clamp low, adjusted belleville stack. ran ok"</em>: a prior spindle alarm on this machine traced to the drawbar. The OEM row is <em>Overload with tool pull-out marks</em>. Against it: no pull-out marks were reported, the operator said chips looked normal, and the load rise tracked the vibration and temperature rise rather than appearing as a step. The taper discolouration cannot tell heat from bearings apart from fretting at a poorly clamped holder from a description alone.</p>
<p><strong>First check.</strong> With the drive locked out, inspect the tool holder taper for pull-out or fretting marks, then measure clamp force with the gauge against OEM spec 8.0–9.5 kN (manual 7.4, row 3).</p>
<p><strong>Expected fix and repair path.</strong> Re-adjust or replace the Belleville stack per OEM procedure (stored spring energy); clean and inspect the taper.</p>
<p class="muted">Cited: MW-131.</p>
</section>
""".format(v=E(F["Vibration first / last (mm/s)"]), vr=F["Vibration last ÷ first"], tr=F["Spindle temp rise (°C)"], ld=E(F["Spindle load first / last (%)"]),
           rates=E(F["Vibration rise rate per interval (mm/s per min)"]), cp=E(F["Coolant pressure range (bar)"]))

questions = """<ul>
<li><strong>Which production day is "this morning's report"?</strong> The breakdown is dated 2026-11-10; the production exports cover 2026-11-12 only; today's run date is {run}. "Yesterday afternoon" does not match either date. Two options: (1) report on 2026-11-12 (done here) with the VMC-02 record carried in as an ongoing exception, or (2) wait for the export covering the breakdown day or the latest day and re-run.</li>
<li><strong>Is VMC-02 still down?</strong> Last observation: still down at 2026-11-10 16:10. If it has restarted, give the end time so the duration can be recorded.</li>
<li><strong>Which site is VMC-02 at?</strong> The breakdown inputs do not say; the record carries site as unresolved.</li>
<li><strong>What is VMC-02's current PM interval and checklist?</strong> No PM plan was available; MW-118 calls it "quarterly", which is all the export says.</li>
<li><strong>Are there maintenance tickets for VMC-02 after 2026-09-24?</strong> The export ends there, {gap} days before the breakdown; an on-demand export, pasted tickets, or a technician's description of recent work would fill it.</li>
<li><strong>Is there a status and due date for WO-8120 (MB-1880)?</strong> It is not in the work order export, so its commitment impact cannot be traced.</li>
<li><strong>Downtime cost per hour:</strong> not set. Set <span class="mono">MFG_DOWNTIME_COST_PER_HOUR</span> or say "update our downtime cost" to record it in the plant profile. The finance memo's shop rates are not a downtime cost and were not used.</li>
</ul>""".format(run=RUN_AT.date().isoformat(), gap=gap_mh)

pm = """<section class="panel"><h2>PM plan adjustment (draft for the maintenance planner)</h2>
<p>The current PM plan for VMC-02 was not available (no CMMS connector; not in the inputs). <strong>First: what is today's PM interval and checklist for VMC-02?</strong> MW-118 calls the PM "quarterly". The export holds two PMs, {pmq}, {pg} days apart, and none in the {ds} days from the last one to the breakdown.</p>
<ol>
<li><strong>Spindle vibration trend at every PM, with an action limit and an owner.</strong> MW-140 recorded 2.1 mm/s at 8k against 1.4 the previous year and ended "told sup", with no corrective work order in the export. Record the reading at a fixed speed every PM, and open a corrective ticket automatically when it exceeds an action limit the planner sets from the OEM data (not set here: no OEM vibration limit is in the manual excerpt).</li>
<li><strong>Taper run-out check at every PM</strong> against the OEM limit &lt; 3 µm (manual 7.4).</li>
<li><strong>Chiller level and flow check</strong>, added to the PM and to a shorter operator check, given MW-160 (low fluid, spindle hot) and this overtemp.</li>
<li><strong>Drawbar clamp force gauge check at every PM</strong>, spec 8.0–9.5 kN (manual 7.4), given MW-131.</li>
<li><strong>A "rough" or rising-vibration PM note triggers a follow-up ticket</strong> rather than "monitor": MW-118 said "monitor" in March.</li>
</ol>
<p class="muted">Draft only. The planner owns the schedule; nothing is written to any system.</p></section>""".format(
    pmq=E(F["VMC-02 PM records"]), pg=pm_gap, ds=days_since_pm)

sensor_summary = f"""<section class="panel"><h2>What the sensor data showed</h2>
<p>Window {E(F['Sensor window'])}, {F['Sensor rows for VMC-02']} samples, ending at the alarm minute (window covers the event onset; nothing after the alarm). Vibration {E(F['Vibration first / last (mm/s)'])} mm/s, rising at every sample ({F['Vibration last ÷ first']}x overall), accelerating sharply after 15:00. Spindle temperature {E(F['Spindle temp first / last (°C)'])} °C (+{F['Spindle temp rise (°C)']} °C). Spindle load {E(F['Spindle load first / last (%)'])} %. Coolant pressure flat at {E(F['Coolant pressure range (bar)'])} bar. Shape: a steady climb that steepened in the final 24 minutes, which is progressive wear rather than a step change. Limits: samples are irregular (30, 20 and 4 minutes apart), there is no spindle rpm channel, so the readings cannot be compared directly with MW-140's "2.1 mm/s at 8k", and there is no chiller flow or level channel.</p></section>"""

history = f"""<section class="panel"><h2>Maintenance history and close-out notes</h2>
<p>{E(F['Maintenance records, VMC-02'])} records on VMC-02; {E(F['VMC-02 records with substantive close-out notes'])} carry substantive close-out notes, so the citations rest on all of them. Template check: {E(F['Close-out note texts grouped (exact text)'])}, so no note is a stock phrase. Sibling search (model taken from the asset-name prefix "VMC", as the export has no model column): siblings {E(F['Sibling assets (model taken from asset-name prefix \'VMC\'; no model column)'])}; symptom-word query on siblings: {E(F['Sibling records matching symptom words'])}. MW-152 on VMC-03 is a coolant pump replacement its own note marks "not related". Freshness: the export's latest close date is {mh_last}, {gap_mh} days before the breakdown; tickets nearest the event may be missing.</p>
{table(['WO','Asset','Opened','Closed','Type','Close-out note (verbatim)','Cited by'], [[f'<span class="mono">{r["wo"]}</span>', r['asset_id'], r['opened'], r['closed'], r['type'], E(r['close_out_note']), {'MW-118':'Candidate 1','MW-140':'Candidate 1','MW-160':'Candidate 2','MW-131':'Candidate 3'}.get(r['wo'],'not cited (other asset, unrelated)')] for r in mh])}
</section>"""

handoff = f"""<section class="panel"><h2>Downtime record handed to the morning report</h2>
<p>Saved as <span class="mono">out/records/downtime-record_VMC-02_2026-11-10.yaml</span> (contract v3, no transformation).</p>
{table(['Field','Value'], [[k, E(yv(record[k]))] for k in ['asset_id','started_at','ended_at','duration_minutes','production_day','production_wo','site','safety_flagged','leading_cause_confidence','cited_work_orders','diagnosis_state','technician_step']])}
<p>Match rule: asset plus start time (same <span class="mono">asset_id</span>, <span class="mono">started_at</span> within the same shift). No MES row matched the diagnosis record on asset plus start time: the MES downtime export holds {F['MES rows matching the diagnosis record (asset + start within shift)']} rows for VMC-02. The diagnosis record stands alone as the row; counted once.</p>
<p>Technician step: <strong>pending</strong>, cause proposed, technician still working (no confirmation in the inputs).</p></section>"""

diag_html = HEAD.replace("{t}", "VMC-02 breakdown diagnosis") + f"""
<h1>VMC-02: breakdown diagnosis, 10 Nov 2026</h1>
{SAFETY}
<section class="panel"><h2>The event, as reported</h2><p>2026-11-10 15:24 local (-05:00 per historian): alarm <span class="mono">SPINDLE OVERLOAD / OVERTEMP</span>; machine stopped mid-cycle on <span class="mono">WO-8120</span> op 20 (<span class="mono">MB-1880</span>). Operator: grinding noise from the spindle for about 20 minutes before the alarm; chips looked normal. Still down at 16:10. Technician photo: description only, no photo file: bluish discolouration at the spindle nose / taper area. Diagnosis is advisory; nothing has been written to a ticket.</p></section>
{cand}
{sensor_summary}
{history}
{pm}
{handoff}
<section class="panel warn"><h2>Questions recorded (not asked in this run)</h2>{questions}</section>
<section class="panel"><details><summary>Figures block (computed in this session)</summary>{fig_table}</details></section>
<section class="panel"><p>Operations page, maintenance section: this page is offered, not published. Save it over yesterday's. The dashboard was not updated: Chain 4 never publishes the Operations dashboard, and no artifact tools were used in this run.</p></section>
</main></body></html>"""
open(OUT + "/diagnosis/VMC-02-2026-11-10-diagnosis.html", "w", encoding="utf-8").write(diag_html)

# ---------------- morning report ----------------
oee_rows = [[o["asset"], "CELL-A", f'{o["A"]:.1%}', f'{o["P"]:.1%}', f'{o["Q"]:.1%}', f'{o["OEE"]:.1%}', f'{o["ppt"]:g}', f'{o["down"]}', f'{o["run"]:g}', f'{o["ideal"]:g}', f'{o["good"]} / {o["total"]}'] for o in oee]
oee_rows.append(["CELL-A total", "CELL-A", f"{CA:.1%}", f"{CP:.1%}", f"{CQ:.1%}", f"{CA*CP*CQ:.1%}", f"{cppt:g}", f"{sum(o['down'] for o in oee)}", f"{crun:g}", f"{cideal:g}", f"{cgood} / {ctot}"])
log_rows = [[r["asset_id"], r["started_at"], r["ended_at"], r["duration_minutes"], r["reason_code"], E(r["reason_text"]), r["started_at"][:10], "mes_export", "—"] for r in dt]
log_rows.insert(0, ["<strong>VMC-02</strong>", alarm, "null (still down at 16:10)", "null", "none given", E(record["reason_text"]), "2026-11-10", "breakdown_diagnosis",
                    "Proposed: spindle bearing damage / preload loss (high); proposed, technician still working; safety flagged"])
min_rank = sorted(dt, key=lambda r: -int(r["duration_minutes"]))
freq = sorted(by_code_n.items(), key=lambda x: (-x[1], x[0]))
actions = [
    ["VMC-02 down since 2026-11-10 15:24, safety flagged; last seen down at 16:10", "WO-8120 op 20 (MB-1880) interrupted; commitment impact not traceable (WO-8120 not in the work order export)", "Lockout; technician works the ranked list, first checks: hand-rotation feel and taper run-out, chiller level/flow; confirm current status", "suggested: maintenance supervisor", "Investigation"],
    ["WO-1002 (PN-200): 220 good of 250 ordered on 2026-11-12, 30 short; due 2026-11-13", "Due date is before today's run date; output after 2026-11-12 is not in this drop. Customer commitment not traceable: no sales order link", "Confirm whether the 30 ran on 2026-11-13", "suggested: production scheduler", "Investigation"],
    ["WO-1001 (PN-100): 480 good of 500 ordered, 12 scrapped on 2026-11-12; due 2026-11-14", "20 short against today's due date, on this drop's output only", "Confirm remaining quantity and whether it runs today", "suggested: production scheduler", "Investigation"],
    ["Breakdown date does not match the report day", "Breakdown 2026-11-10 vs production day 2026-11-12 vs run date " + RUN_AT.date().isoformat(), "Choose: keep this 2026-11-12 report with VMC-02 carried as an ongoing exception, or wait for the matching export and re-run", "suggested: production manager", "Decision"],
]
report_html = HEAD.replace("{t}", "SITE-1 morning report") + f"""
<h1>SITE-1: morning report, 12 Nov 2026</h1>
<section class="panel critical"><h2>Safety: VMC-02 down, safety flagged</h2>
<p><strong>Follow your plant's lockout procedure before anyone works on this machine. This is not a safety assessment.</strong></p>
<p>VMC-02 tripped on <span class="mono">SPINDLE OVERLOAD / OVERTEMP</span> at 2026-11-10 15:24 -05:00 after about 20 minutes of reported grinding noise. Safety reason: {E(record['safety_reason'])}. Do not run the spindle; lock out the spindle drive before manual rotation (OEM manual 7.4). Ongoing as of the last observation (16:10 on 10 Nov); duration null, so it is listed here and in the exceptions, and excluded from the minutes ranking. Site for VMC-02 is not stated in the breakdown inputs.</p></section>
<section class="panel warn"><h2>Freshness</h2><ul>
<li>Production exports (plan, output, downtime, routing, work orders) cover production day <strong>2026-11-12 only</strong>; files modified {src['pulse_oee/output.csv']}. Run date is {RUN_AT.date().isoformat()}: <strong>no export for 2026-11-13 is in the folder</strong>. If one was expected, it did not land, and this report is not yesterday's day.</li>
<li>Shifts in the day: {E(F['Shifts in output export'])}. The site's shift pattern is not on file, so whether that is a complete plant day cannot be said.</li>
<li>Breakdown inputs: event 2026-11-10 (last observation 16:10); historian window {E(F['Sensor window'])}; maintenance export, latest close {mh_last} ({gap_mh} days before the breakdown), export-sourced, no CMMS connector. Date-window mismatch (class 7): the breakdown day is {gap_day} days before the report's production day, so it has no MES partner in this drop.</li>
<li>MES downtime timestamps are naive ({E(F['MES downtime rows with naive (zone-less) timestamps'])}); zone unresolved, no source-clock declaration on file.</li>
<li>No plant profile on file (plant_setup.py find: profile and rates absent). No timestamps later than the run time ({F['Sources with a timestamp later than run time']}).</li>
<li>Maintenance work orders in progress: could not be seen. The maintenance export shows {F['Open maintenance WOs in export']} open, but it ends {mh_last} and covers the breakdown folder only.</li>
</ul></section>
<section class="panel"><h2>Headline, 2026-11-12, CELL-A</h2><div class="tiles">
<div class="tile"><div class="v">{tot_good} / {tot_plan}</div><div class="l">good vs plan ({round(100*tot_good/tot_plan,1)}%); total output {tot_good+tot_scrap}</div></div>
<div class="tile"><div class="v">{CA*CP*CQ:.1%}</div><div class="l">OEE CELL-A: A {CA:.1%} · P {CP:.1%} · Q {CQ:.1%}</div></div>
<div class="tile"><div class="v">{mes_total} min</div><div class="l">MES downtime, {len(dt)} events; plus VMC-02 ongoing (unpriced, not in this total)</div></div>
<div class="tile"><div class="v">{tot_scrap} units</div><div class="l">scrap; unpriced: no standard cost in the drop</div></div>
</div><p class="muted">Downtime is unpriced: no downtime cost per hour is set (<span class="mono">MFG_DOWNTIME_COST_PER_HOUR</span> not set; no plant profile). Set it or say "update our downtime cost". The finance memo's shop rates are not a downtime rate and were not used.</p></section>
<section class="panel"><h2>Today's actions</h2>{table(['Issue','Impact','Next step','Owner','Type'], actions)}
<p class="muted">Commitment impact not traceable: no work order to sales order link in the ERP export (affects all 3 work orders in the export, and WO-8120).</p></section>
<section class="panel"><h2>Floor view</h2><p>No floor layout on file for SITE-1. Attach a floor plan (PDF or image) and ask for a floor view to set one up.</p></section>
<section class="panel"><details open><summary>Detail</summary>
<h3>Output against plan, 2026-11-12 (by product; cell CELL-A, site SITE-1)</h3>
{table(['Part','Asset','Plan','Good','Total','Scrap','Variance (good − plan)','Variance %'], [[o['part'],o['asset'],o['plan'],o['good'],o['total'],o['scrap'],o['var'],f"{o['var_pct']}%"] for o in oap] + [['CELL-A total','',tot_plan,tot_good,tot_good+tot_scrap,tot_scrap,tot_good-tot_plan,f"{round(100*(tot_good-tot_plan)/tot_plan,1)}%"]], numcols=(2,3,4,5,6,7))}
<p class="muted">Part keys matched exactly across plan, output, routing and work orders ({E(F['Part keys matched exactly across plan/output/routing/WO'])}); no normalization applied or pending. VMC-02 is not in the plan for 2026-11-12, so the breakdown has no output-against-plan effect on this day.</p>
<h3>OEE per asset</h3>
{table(['Asset','Cell','Availability','Performance','Quality','OEE','Planned min','Unplanned down min','Run min','Ideal min','Good / total'], oee_rows, numcols=tuple(range(2,11)))}
<p class="muted">quality = good ÷ (good + scrap); no rework column, so first-pass yield could not be applied. Planned production time = the plan export's planned_hours (the site's definition is not on file; unconfirmed). Performance uses routing run_min_per_unit as ideal cycle time. VMC-02: not in the plan or output for this day, so no OEE (not 0%).</p>
<h3>Downtime log (MES export plus carried-in breakdown record)</h3>
{table(['Asset','Started','Ended','Minutes','Reason code','Reason text','Production day','Source','Diagnosis'], log_rows)}
<p>Matching: asset plus start time (same asset_id, started_at within the same shift). No MES row matched the diagnosis record on asset plus start time ({F['MES rows matching the diagnosis record (asset + start within shift)']} VMC-02 rows in the MES export); the diagnosis record stands alone as the row; counted once. Cause shown as proposed, technician still working (technician_step: pending, diagnosis_state: advisory).</p>
<h3>Ranked by minutes (2026-11-12)</h3>{table(['Rank','Asset','Reason','Minutes'], [[i+1, r['asset_id'], r['reason_code'], r['duration_minutes']] for i, r in enumerate(min_rank)])}
<h3>Ranked by frequency (2026-11-12)</h3>{table(['Rank','Reason code','Events','Minutes'], [[i+1, k, n, by_code_min[k]] for i, (k, n) in enumerate(freq)])}
<p class="muted">Excluded from both rankings: VMC-02 breakdown (null duration, ongoing; production day 2026-11-10, not this day). MES events coded Other or blank: {E(F['MES events coded Other or blank'])}. Integrity: {E(F['MES downtime rows passing start/end/duration check'])} MES rows pass the start/end/duration check.</p>
<h3>Priced losses</h3>{table(['Item','Quantity','Dollars','Basis'], [['Scrap PN-100', scrap_by_part['PN-100'], 'unpriced', 'no standard cost in the drop'], ['Scrap PN-200', scrap_by_part['PN-200'], 'unpriced', 'no standard cost in the drop'], ['Downtime (MES)', f'{mes_total} min', 'unpriced', 'no downtime cost rate set'], ['VMC-02 breakdown', 'ongoing, null', 'unpriced so far', 'duration unknown; no rate set']])}
<h3>Week-over-week movers</h3><p>Skipped: the drop holds one production day and no stored day history.</p>
<h3>Reschedule proposals</h3><p>None proposed. VMC-02 / WO-8120: no routing, work order record or forward schedule for MB-1880 in the drop. WO-1002 and WO-1001: the plan export covers 2026-11-12 only, with no forward schedule to trace a move against. Reported with impact, no move.</p>
<h3>Checked, nothing wrong</h3><ul><li>WO-1003 (PN-100): 300 good of 300 ordered on 2026-11-12, due 2026-11-15.</li><li>VMC-03: in the maintenance export (MW-152, coolant pump), not in production records for this day. One-sided, not an exception.</li></ul>
<h3>Sources, methods and assumptions</h3><ul>
<li>Inputs: inputs/pulse_oee/*.csv (production), inputs/breakdown/* (event, historian window, maintenance export, OEM manual excerpt 7.4), inputs/rates_memo.txt (shop rates; not a downtime or standard cost). All marked synthetic test data.</li>
<li>No consolidated XLSX dataset: no Excel writer in this session. Joins were done in code on the raw exports (exact key matches only) and the tabs written as CSV under out/dataset/.</li>
<li>Production-day attribution: calendar day of start; site rule not on file.</li>
<li>Diagnosis: out/diagnosis/VMC-02-2026-11-10-diagnosis.html. Downtime record: out/records/downtime-record_VMC-02_2026-11-10.yaml.</li></ul>
</details></section>
<section class="panel"><details><summary>Figures block (computed in this session)</summary>{fig_table}</details></section>
<section class="panel"><p>This page is offered, not published: save it over yesterday's. The Operations dashboard was not updated: only the morning-plant-pulse chain publishes it, and no artifact tools were used in this run.</p></section>
</main></body></html>"""
open(OUT + "/report-output/morning-report.html", "w", encoding="utf-8").write(report_html)
for r in FIG:
    print(f"{r['figure']}: {r['value']}")
