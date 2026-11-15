"""Morning production report builder (daily-production-report skill, standalone run).

Reads the raw exports under inputs/pulse_oee, computes every figure in code,
writes the figures block (JSON + CSV) and the HTML page under out/report-output.
Usage: python -I build_report.py <inputs_dir> <out_dir>
"""
import csv, json, os, sys, html
from datetime import datetime, date
from collections import defaultdict, OrderedDict

IN, OUT = sys.argv[1], sys.argv[2]
RUN_DATE = date(2026, 11, 15)          # session date
GENERATED = datetime.now().strftime("%Y-%m-%d %H:%M")
os.makedirs(OUT, exist_ok=True)

def rd(name):
    with open(os.path.join(IN, name), newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))

plan, output, downtime = rd("plan.csv"), rd("output.csv"), rd("downtime.csv")
routing, wos = rd("routing.csv"), rd("work_orders.csv")

FIG = []  # figures block
def fig(name, value, src, flt):
    FIG.append({"figure": name, "value": value, "computed_from": src, "filter": flt})
    return value

def pct(x):
    return None if x is None else round(100 * x, 2)

# ---------------- Step 1: freshness ----------------
files = ["plan.csv", "output.csv", "downtime.csv", "routing.csv", "work_orders.csv"]
fresh = []
for fn in files:
    st = os.stat(os.path.join(IN, fn))
    fresh.append({"file": fn, "modified": datetime.fromtimestamp(st.st_mtime).strftime("%Y-%m-%d %H:%M")})
prod_days = sorted({r["production_day"] for r in output})
plan_days = sorted({r["plan_date"] for r in plan})
dt_days = sorted({r["started_at"][:10] for r in downtime})
fig("Production days in output export", ", ".join(prod_days), "output.csv", "distinct production_day")
fig("Plan dates in plan export", ", ".join(plan_days), "plan.csv", "distinct plan_date")
fig("Downtime event dates", ", ".join(dt_days), "downtime.csv", "distinct date(started_at)")
PDAY = prod_days[-1]
age_days = (RUN_DATE - date.fromisoformat(PDAY)).days
fig("Latest production day age (days before 2026-11-15)", age_days, "output.csv", "2026-11-15 minus max(production_day)")
missing_days = [str(date.fromordinal(d)) for d in range(date.fromisoformat(PDAY).toordinal() + 1, RUN_DATE.toordinal())]
fig("Production days with no export in the drop", ", ".join(missing_days), "output.csv / plan.csv / downtime.csv", "days between latest production_day and 2026-11-15, exclusive")
shifts_by_asset = defaultdict(set)
for r in output:
    shifts_by_asset[r["asset_id"]].add(r["shift"])
shifts_all = sorted({r["shift"] for r in output})
fig("Shifts present in output", ", ".join(shifts_all), "output.csv", "distinct shift")
for a in sorted(shifts_by_asset):
    fig(f"Shifts reported, {a}", ", ".join(sorted(shifts_by_asset[a])), "output.csv", f"asset_id == {a}")
future = [r for r in downtime if datetime.fromisoformat(r["started_at"]).date() > RUN_DATE]
fig("Rows with future timestamps", len(future), "downtime.csv", "started_at > 2026-11-15")
env_rate_set = "MFG_DOWNTIME_COST_PER_HOUR" in os.environ
fig("MFG_DOWNTIME_COST_PER_HOUR set", env_rate_set, "environment", "checked by name; value not read")

# ---------------- Key checks (raw exports, no consolidated dataset) ----------------
pn_plan = {r["part_number"] for r in plan}
pn_out = {r["part_number"] for r in output}
pn_rt = {r["part_number"] for r in routing}
pn_wo = {r["part_number"] for r in wos}
fig("Part numbers in plan not in output", sorted(pn_plan - pn_out) or "none", "plan.csv vs output.csv", "set difference, exact match")
fig("Part numbers in output not in plan", sorted(pn_out - pn_plan) or "none", "output.csv vs plan.csv", "set difference, exact match")
fig("Part numbers in output with no routing", sorted(pn_out - pn_rt) or "none", "output.csv vs routing.csv", "set difference, exact match")
wo_out = {r["work_order"] for r in output}
wo_erp = {r["work_order"] for r in wos}
fig("Work orders in output not in WO export", sorted(wo_out - wo_erp) or "none", "output.csv vs work_orders.csv", "set difference")
fig("Work orders in WO export with no output", sorted(wo_erp - wo_out) or "none", "work_orders.csv vs output.csv", "set difference")
dup = defaultdict(int)
for r in output:
    dup[(r["work_order"], r["production_day"], r["shift"])] += 1
fig("Duplicate output keys (WO, day, shift)", sum(1 for v in dup.values() if v > 1), "output.csv", "count of keys with >1 row")
has_so = "sales_order" in (wos[0].keys() if wos else [])
fig("Work order export carries sales_order", has_so, "work_orders.csv", "column present")
has_rework = "qty_rework" in (output[0].keys() if output else []) or "rework" in (output[0].keys() if output else [])
fig("Output export carries a rework column", has_rework, "output.csv", "column 'qty_rework' or 'rework' present")

# ---------------- Step 2: output against plan ----------------
oap = []
for p in plan:
    rows = [r for r in output if r["part_number"] == p["part_number"] and r["production_day"] == p["plan_date"] and r["asset_id"] == p["asset_id"]]
    good = sum(int(r["qty_good"]) for r in rows)
    scrap = sum(int(r["qty_scrap"]) for r in rows)
    planned = int(p["planned_qty"])
    cell = ", ".join(sorted({r["cell"] for r in rows})) or "—"
    d = {"part": p["part_number"], "work_center": p["work_center"], "asset": p["asset_id"], "cell": cell,
         "plan": planned, "good": good, "scrap": scrap, "total": good + scrap,
         "variance_good": good - planned, "attain_good_pct": round(100 * good / planned, 2)}
    oap.append(d)
    k = f"{p['part_number']} / {p['asset_id']} / {p['plan_date']}"
    fig(f"Planned qty, {k}", planned, "plan.csv", f"part_number=={p['part_number']}, asset_id=={p['asset_id']}")
    fig(f"Good qty, {k}", good, "output.csv", f"same keys, sum qty_good over {len(rows)} rows")
    fig(f"Scrap qty, {k}", scrap, "output.csv", "same keys, sum qty_scrap")
    fig(f"Total qty (good+scrap), {k}", good + scrap, "output.csv", "good + scrap")
    fig(f"Variance good vs plan, {k}", good - planned, "computed", "good - planned")
    fig(f"Plan attainment (good), {k} %", d["attain_good_pct"], "computed", "good / planned")
T_plan = fig("Total planned qty", sum(d["plan"] for d in oap), "plan.csv", "sum planned_qty")
T_good = fig("Total good qty", sum(d["good"] for d in oap), "output.csv", "sum qty_good, matched to plan rows")
T_scrap = fig("Total scrap qty", sum(d["scrap"] for d in oap), "output.csv", "sum qty_scrap, matched to plan rows")
T_total = fig("Total output (good+scrap)", T_good + T_scrap, "computed", "good + scrap")
fig("Total good qty, all output rows (reconciliation)", sum(int(r["qty_good"]) for r in output), "output.csv", "sum qty_good, all rows")
T_var = fig("Total variance good vs plan", T_good - T_plan, "computed", "good - planned")
T_att = fig("Total plan attainment (good) %", round(100 * T_good / T_plan, 2), "computed", "good / planned")
by_cell = defaultdict(lambda: [0, 0, 0])
for d in oap:
    by_cell[d["cell"]][0] += d["plan"]; by_cell[d["cell"]][1] += d["good"]; by_cell[d["cell"]][2] += d["scrap"]
for c, (pl, g, s) in by_cell.items():
    fig(f"Cell {c}: plan / good / scrap", f"{pl} / {g} / {s}", "plan.csv + output.csv", f"cell=={c}")

# ---------------- Step 3: OEE per asset ----------------
ict = {r["part_number"]: float(r["run_min_per_unit"]) for r in routing}
dt_valid, dt_bad = [], []
for r in downtime:
    s, e = datetime.fromisoformat(r["started_at"]), datetime.fromisoformat(r["ended_at"])
    stated = float(r["duration_minutes"])
    span = (e - s).total_seconds() / 60
    if e < s:
        dt_bad.append((r, "end_before_start"))
    elif abs(span - stated) > 0.5:
        dt_bad.append((r, f"duration_mismatch (span {span:g} min)"))
    else:
        dt_valid.append(r)
fig("Downtime events, total", len(downtime), "downtime.csv", "all rows")
fig("Downtime events with untrustworthy minutes", len(dt_bad), "downtime.csv", "ended_at < started_at, or |span - duration_minutes| > 0.5")

oee = []
agg = {"planned": 0.0, "down": 0.0, "ideal": 0.0, "good": 0, "total": 0}
for p in plan:
    a = p["asset_id"]
    planned_min = float(p["planned_hours"]) * 60
    down = sum(float(r["duration_minutes"]) for r in dt_valid if r["asset_id"] == a and r["started_at"][:10] == p["plan_date"])
    run = planned_min - down
    rows = [r for r in output if r["asset_id"] == a and r["production_day"] == p["plan_date"]]
    good = sum(int(r["qty_good"]) for r in rows)
    total = sum(int(r["qty_good"]) + int(r["qty_scrap"]) for r in rows)
    ideal = sum(ict[r["part_number"]] * (int(r["qty_good"]) + int(r["qty_scrap"])) for r in rows if r["part_number"] in ict)
    A = run / planned_min if planned_min else None
    P = ideal / run if run and all(r["part_number"] in ict for r in rows) else None
    Q = good / total if total else None
    O = A * P * Q if None not in (A, P, Q) else None
    oee.append({"asset": a, "work_center": p["work_center"], "planned_min": planned_min, "down_min": down, "run_min": run,
                "ideal_min": round(ideal, 2), "good": good, "total": total,
                "A": pct(A), "P": pct(P), "Q": pct(Q), "OEE": pct(O)})
    for k, v, f_ in [("Planned production time (min)", planned_min, "plan.csv planned_hours x 60"),
                     ("Downtime (min)", down, "downtime.csv sum duration_minutes, valid rows, same day"),
                     ("Run time (min)", run, "planned - downtime"),
                     ("Ideal time (min)", round(ideal, 2), "sum run_min_per_unit x (good+scrap)"),
                     ("Availability %", pct(A), "run / planned"),
                     ("Performance %", pct(P), "ideal / run"),
                     ("Quality %", pct(Q), "good / (good+scrap)"),
                     ("OEE %", pct(O), "A x P x Q")]:
        fig(f"{k}, {a}", v, "computed", f_)
    agg["planned"] += planned_min; agg["down"] += down; agg["ideal"] += ideal; agg["good"] += good; agg["total"] += total
runT = agg["planned"] - agg["down"]
pA, pP, pQ = runT / agg["planned"], agg["ideal"] / runT, agg["good"] / agg["total"]
plant = {"A": pct(pA), "P": pct(pP), "Q": pct(pQ), "OEE": pct(pA * pP * pQ)}
fig("Plant roll-up planned time (min)", agg["planned"], "computed", "sum over assets")
fig("Plant roll-up run time (min)", runT, "computed", "sum over assets")
for k in ["A", "P", "Q", "OEE"]:
    fig(f"Plant roll-up {dict(A='Availability',P='Performance',Q='Quality',OEE='OEE')[k]} %", plant[k], "computed", "time-weighted: sums of numerators / sums of denominators")
assets_planned = {p["asset_id"] for p in plan}
fig("Planned assets with no output", sorted(assets_planned - {r['asset_id'] for r in output}) or "none", "plan.csv vs output.csv", "set difference")

# ---------------- Step 4: downtime log ----------------
other = [r for r in downtime if r["reason_code"].strip().upper() in ("", "OTHER")]
fig("Downtime events coded Other or blank", f"{len(other)} of {len(downtime)}", "downtime.csv", "reason_code in ('', 'Other')")
fig("Downtime minutes coded Other or blank", sum(float(r["duration_minutes"]) for r in other), "downtime.csv", "same filter")
named = [r for r in dt_valid if r not in other]
by_code = defaultdict(lambda: {"minutes": 0.0, "events": 0, "assets": set(), "text": set()})
for r in named:
    c = by_code[r["reason_code"]]
    c["minutes"] += float(r["duration_minutes"]); c["events"] += 1; c["assets"].add(r["asset_id"]); c["text"].add(r["reason_text"])
for code, c in by_code.items():
    fig(f"Downtime minutes, reason {code}", c["minutes"], "downtime.csv", f"reason_code=={code}, valid rows")
    fig(f"Downtime events, reason {code}", c["events"], "downtime.csv", f"reason_code=={code}")
rank_min = sorted(by_code.items(), key=lambda kv: (-kv[1]["minutes"], kv[0]))
rank_freq = sorted(by_code.items(), key=lambda kv: (-kv[1]["events"], -kv[1]["minutes"], kv[0]))
DT_MIN = fig("Total downtime minutes (valid rows)", sum(float(r["duration_minutes"]) for r in dt_valid), "downtime.csv", "sum duration_minutes, valid rows")
DT_EV = fig("Total downtime events", len(downtime), "downtime.csv", "all rows")
fig("Downtime minutes as share of planned time %", round(100 * DT_MIN / agg["planned"], 2), "computed", "downtime / planned production time")

# ---------------- Step 5: priced losses ----------------
# No plant profile, no rates file, no MFG_ variable. rates_memo.txt holds burdened shop rates by work centre
# (MILL-H, MILL-V, TURN, INSP) but the exports use work centre 'VMC', which is not on the memo.
memo_wc = ["MILL-H", "MILL-V", "TURN", "INSP"]
export_wc = sorted({r["work_center"] for r in plan} | {r["work_center"] for r in routing})
fig("Work centres in exports", ", ".join(export_wc), "plan.csv + routing.csv", "distinct work_center")
fig("Export work centres found verbatim in rates memo", [w for w in export_wc if w in memo_wc] or "none", "rates_memo.txt", "exact string match")
fig("Standard material cost available", False, "inputs/ (all files)", "no column or file carrying standard or material cost per part")
fig("Downtime dollars", "unpriced - no confirmed downtime cost rate", "secret-config resolution", "env var not set; no plant profile; memo rate is a shop rate on a work-centre name not in the exports")
fig("Scrap dollars", "unpriced - no standard cost", "inputs/", "no standard material cost per part")
scrap_by_part = {d["part"]: d["scrap"] for d in oap}
for p_, s in scrap_by_part.items():
    fig(f"Scrap share of units, {p_} %", round(100 * s / T_scrap, 2), "output.csv", "part scrap / total scrap")
# Value-added machine minutes embedded in scrap (rate-independent, from routing)
for p_, s in scrap_by_part.items():
    fig(f"Machine minutes lost in scrap, {p_}", round(s * ict[p_], 2), "output.csv x routing.csv", "scrap x run_min_per_unit")
SCRAP_MIN = fig("Machine minutes lost in scrap, total", round(sum(s * ict[p_] for p_, s in scrap_by_part.items()), 2), "computed", "sum")

# ---------------- Step 8: exceptions (work orders) ----------------
wo_rows = []
for w in wos:
    rows = [r for r in output if r["work_order"] == w["work_order"]]
    good = sum(int(r["qty_good"]) for r in rows)
    scrap = sum(int(r["qty_scrap"]) for r in rows)
    ordered = int(w["qty_ordered"])
    due = date.fromisoformat(w["due_date"])
    short = max(ordered - good, 0)
    last_day = max((r["production_day"] for r in rows), default="—")
    if short > 0 and due < RUN_DATE:
        state = "past due, short as of last export"
    elif short > 0:
        state = "short, due later"
    else:
        state = "quantity complete; status still " + w["status"]
    days_past = (RUN_DATE - due).days
    d = {"wo": w["work_order"], "part": w["part_number"], "ordered": ordered, "good": good, "scrap": scrap,
         "short": short, "due": w["due_date"], "status": w["status"], "days_past_due": days_past,
         "last_output_day": last_day, "state": state,
         "asset": ", ".join(sorted({r['asset_id'] for r in rows})),
         "make_up_min": round(short * ict.get(w["part_number"], 0), 2)}
    wo_rows.append(d)
    fig(f"{w['work_order']}: good to date in drop", good, "output.csv", f"work_order=={w['work_order']}")
    fig(f"{w['work_order']}: shortfall vs ordered", short, "computed", "max(ordered - good, 0)")
    fig(f"{w['work_order']}: days past due at 2026-11-15", days_past, "work_orders.csv", "2026-11-15 - due_date")
    fig(f"{w['work_order']}: ideal run minutes to make up shortfall", d["make_up_min"], "routing.csv", "shortfall x run_min_per_unit (no scrap allowance, no setup)")
late = [d for d in wo_rows if d["state"].startswith("past due")]
fig("Work orders past due and short as of last export", f"{len(late)} of {len(wo_rows)}", "work_orders.csv + output.csv", "due_date < 2026-11-15 and good < qty_ordered")
fig("Work orders whose commitment impact is not traceable", len(late), "work_orders.csv", "no sales_order column")

fig("Run minutes not explained by ideal time (performance loss), roll-up", round(runT - agg["ideal"], 2), "computed", "run time - ideal time, both assets")
fig("Performance loss minutes / logged downtime minutes", round((runT - agg["ideal"]) / DT_MIN, 2), "computed", "same computation")
_perf = {o["asset"]: o["P"] for o in oee}
for d in wo_rows:
    if d["short"] > 0:
        fig(f"{d['wo']}: make-up minutes at 12 Nov performance", round(d["make_up_min"] / (_perf[d["asset"]] / 100)), "computed", "ideal make-up minutes / asset performance")

# ---------------- write structured data ----------------
data = OrderedDict(production_day=PDAY, site=sorted({r['site'] for r in output}), generated=GENERATED,
                   freshness=fresh, output_vs_plan=oap, oee_per_asset=oee, oee_plant_rollup=plant,
                   downtime_events=downtime, downtime_excluded=[{"row": r, "reason": why} for r, why in dt_bad],
                   downtime_rank_minutes=[{"code": k, "minutes": v["minutes"], "events": v["events"]} for k, v in rank_min],
                   downtime_rank_frequency=[{"code": k, "events": v["events"], "minutes": v["minutes"]} for k, v in rank_freq],
                   work_orders=wo_rows, figures_block=FIG)
with open(os.path.join(OUT, "morning-report-data.json"), "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2, default=list)
with open(os.path.join(OUT, "figures-block.csv"), "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=["figure", "value", "computed_from", "filter"])
    w.writeheader()
    for r in FIG:
        w.writerow({k: (json.dumps(v) if isinstance(v, (list, bool)) else v) for k, v in r.items()})

# ---------------- HTML ----------------
E = html.escape
def n(x):
    if x is None: return "—"
    if isinstance(x, float) and x.is_integer(): x = int(x)
    return f"{x:,}" if isinstance(x, int) else f"{x}"
def p_(x): return "N/A" if x is None else f"{x:.1f}%"
def sgn(x): return f"+{x:,}" if x > 0 else f"{x:,}"
site = ", ".join(data["site"])
pday = datetime.fromisoformat(PDAY).strftime("%d %b %Y")
fresh_rows = "".join(f"<tr><td>{E(r['file'])}</td><td class='num'>{E(r['modified'])}</td><td class='num'>{E(cov)}</td><td>{st}</td></tr>"
    for r, cov, st in [
        (fresh[1], PDAY + " (shifts " + ", ".join(shifts_all) + ")", "<span class='status status--critical'>%d days old</span>" % age_days),
        (fresh[0], ", ".join(plan_days), "<span class='status status--critical'>no plan after %s</span>" % plan_days[-1]),
        (fresh[2], ", ".join(dt_days), "<span class='status status--critical'>%d days old</span>" % age_days),
        (fresh[4], "3 open WOs, due 13–15 Nov", "<span class='status status--warn'>no as-of; no sales order link</span>"),
        (fresh[3], "PN-100, PN-200", "<span class='status status--good'>read</span>")])

oap_rows = "".join(f"<tr><td class='num'>{E(d['cell'])}</td><td class='num'>{E(d['work_center'])}</td><td class='num'>{E(d['asset'])}</td><td class='num'>{E(d['part'])}</td>"
                   f"<td class='num'>{n(d['plan'])}</td><td class='num'>{n(d['good'])}</td><td class='num'>{n(d['scrap'])}</td><td class='num'>{n(d['total'])}</td>"
                   f"<td class='num'>{sgn(d['variance_good'])}</td><td class='num'>{d['attain_good_pct']:.1f}%</td></tr>" for d in oap)
oap_rows += (f"<tr class='tot'><td colspan='4'>Total ({E(site)})</td><td class='num'>{n(T_plan)}</td><td class='num'>{n(T_good)}</td><td class='num'>{n(T_scrap)}</td>"
             f"<td class='num'>{n(T_total)}</td><td class='num'>{sgn(T_var)}</td><td class='num'>{T_att:.1f}%</td></tr>")
oee_rows = "".join(f"<tr><td class='num'>{E(o['asset'])}</td><td class='num'>{n(o['planned_min'])}</td><td class='num'>{n(o['down_min'])}</td><td class='num'>{n(o['run_min'])}</td>"
                   f"<td class='num'>{p_(o['A'])}</td><td class='num'>{p_(o['P'])}</td><td class='num'>{p_(o['Q'])}</td><td class='num'><b>{p_(o['OEE'])}</b></td></tr>" for o in oee)
oee_rows += (f"<tr class='tot'><td>Roll-up (time-weighted)</td><td class='num'>{n(agg['planned'])}</td><td class='num'>{n(agg['down'])}</td><td class='num'>{n(runT)}</td>"
             f"<td class='num'>{p_(plant['A'])}</td><td class='num'>{p_(plant['P'])}</td><td class='num'>{p_(plant['Q'])}</td><td class='num'><b>{p_(plant['OEE'])}</b></td></tr>")
def rank_tbl(rk, first):
    out = ""
    for i, (k, v) in enumerate(rk, 1):
        cols = [n(v["minutes"]), n(v["events"])] if first == "min" else [n(v["events"]), n(v["minutes"])]
        out += (f"<tr><td class='num'>{i}</td><td class='num'>{E(k)}</td><td>{E('; '.join(sorted(v['text'])))}</td><td class='num'>{E(', '.join(sorted(v['assets'])))}</td>"
                f"<td class='num'>{cols[0]}</td><td class='num'>{cols[1]}</td></tr>")
    return out
dt_log = "".join(f"<tr><td class='num'>{E(r['asset_id'])}</td><td class='num'>{E(r['started_at'].replace('T',' '))}</td><td class='num'>{E(r['ended_at'][11:16])}</td>"
                 f"<td class='num'>{E(r['duration_minutes'])}</td><td class='num'>{E(r['reason_code'])}</td><td>{E(r['reason_text'])}</td></tr>" for r in downtime)
ties = len({v["events"] for _, v in rank_freq}) == 1 and len(rank_freq) > 1
wo_tbl = "".join(f"<tr><td class='num'>{E(d['wo'])}</td><td class='num'>{E(d['part'])}</td><td class='num'>{E(d['asset'])}</td><td class='num'>{n(d['ordered'])}</td><td class='num'>{n(d['good'])}</td>"
                 f"<td class='num'>{n(d['scrap'])}</td><td class='num'>{n(d['short'])}</td><td class='num'>{E(d['due'])}</td><td class='num'>{E(d['status'])}</td><td>{E(d['state'])}</td></tr>" for d in wo_rows)
figs = "".join(f"<tr><td>{E(r['figure'])}</td><td class='num'>{E(json.dumps(r['value']) if isinstance(r['value'], (list, bool)) else str(r['value']))}</td><td>{E(r['computed_from'])}</td><td><code>{E(r['filter'])}</code></td></tr>" for r in FIG)
W = {d["wo"]: d for d in wo_rows}
o1 = next(o for o in oee if o["asset"] == "CNC-01"); o2 = next(o for o in oee if o["asset"] == "CNC-02")
s100, s200 = scrap_by_part.get("PN-100", 0), scrap_by_part.get("PN-200", 0)
sh100 = round(100 * s100 / T_scrap, 1)

PAGE = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{E(site)}: morning report, {E(pday)}</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans+Condensed:wght@500;600&family=IBM+Plex+Sans:wght@400;500;600&family=IBM+Plex+Mono:wght@500&display=swap" rel="stylesheet">
<style>
:root{{--ink:#1A1D21;--paper:#F2F3F5;--paper-raised:#FFFFFF;--line:#D6D9DD;--accent:#1F5C8B;--accent-soft:#E4EDF4;--good:#2E7248;--good-soft:#E3EFE7;--warn:#A8641A;--warn-soft:#F7EBDA;--critical:#A93226;--critical-soft:#F9E9E7;
--font-display:'IBM Plex Sans Condensed','Arial Narrow',sans-serif;--font-body:'IBM Plex Sans',-apple-system,BlinkMacSystemFont,sans-serif;--font-mono:'IBM Plex Mono','SF Mono',Consolas,monospace;
--text-xs:.75rem;--text-sm:.875rem;--text-base:1rem;--text-lg:1.125rem;--text-xl:1.375rem;--text-2xl:1.75rem;--text-3xl:2.25rem}}
@media (prefers-color-scheme:dark){{:root:not([data-theme="light"]){{--ink:#E8EAEC;--paper:#15181B;--paper-raised:#1D2126;--line:#2E343A;--accent:#6BA8D4;--accent-soft:#1B2C39;--good:#6FBF88;--good-soft:#1B2E22;--warn:#D9A15C;--warn-soft:#33271A;--critical:#DE8378;--critical-soft:#35201E}}}}
:root[data-theme="dark"]{{--ink:#E8EAEC;--paper:#15181B;--paper-raised:#1D2126;--line:#2E343A;--accent:#6BA8D4;--accent-soft:#1B2C39;--good:#6FBF88;--good-soft:#1B2E22;--warn:#D9A15C;--warn-soft:#33271A;--critical:#DE8378;--critical-soft:#35201E}}
body{{margin:0;background:var(--paper);color:var(--ink);font:400 var(--text-base)/1.5 var(--font-body)}}
.page{{display:flex;flex-direction:column;gap:1.25rem;max-width:960px;margin:0 auto;padding:2rem 1.5rem}}
h1,h2,h3{{font-family:var(--font-display);font-weight:600;margin:0 0 .5rem}} h1{{font-size:var(--text-2xl)}} h2{{font-size:var(--text-xl)}} h3{{font-size:var(--text-lg)}}
.meta{{font-size:var(--text-sm);opacity:.8;margin:0}}
.panel{{background:var(--paper-raised);border:1px solid var(--line);border-radius:4px;padding:1.5rem}}
.table-scroll{{overflow-x:auto}} table{{border-collapse:collapse;width:100%;font-size:var(--text-sm)}}
th,td{{text-align:left;padding:.4rem .5rem;border-bottom:1px solid var(--line);vertical-align:top}} th{{font-weight:600}}
.num{{font-family:var(--font-mono);font-variant-numeric:tabular-nums;text-align:right;white-space:nowrap}}
tr.tot td{{font-weight:600;border-top:2px solid var(--line)}}
.status{{display:inline-block;padding:.15rem .55rem;border-radius:2px;font:600 var(--text-xs) var(--font-body);text-transform:uppercase;letter-spacing:.04em}}
.status--good{{background:var(--good-soft);color:var(--good)}}.status--warn{{background:var(--warn-soft);color:var(--warn)}}.status--critical{{background:var(--critical-soft);color:var(--critical)}}
.tiles{{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:1rem}}
.stat-tile{{border:1px solid var(--line);border-radius:4px;padding:1rem}} .stat-figure{{font:500 var(--text-3xl) var(--font-mono);font-variant-numeric:tabular-nums}}
.stat-label{{font-weight:600}} .stat-context{{font-size:var(--text-sm);margin:.25rem 0 0}}
.note{{font-size:var(--text-sm)}} .crit{{border-left:4px solid var(--critical)}} .warnb{{border-left:4px solid var(--warn)}}
details>summary{{cursor:pointer;font:600 var(--text-lg) var(--font-display)}} details{{margin-top:.25rem}}
code{{font-family:var(--font-mono);font-size:var(--text-xs)}} .page-footer{{font-size:var(--text-xs);opacity:.7}}
</style></head><body><main class="page">

<header class="page-header"><h1>{E(site)}: morning report, {E(pday)}</h1>
<p class="meta">Generated {E(GENERATED)} · data as of production day {E(PDAY)} (latest in the drop) · SYNTHETIC test data, fictitious plant</p></header>

<div class="panel warnb"><h2>Safety</h2><p>Safety status: not assessed (no breakdown diagnosis records in this drop).</p></div>

<div class="panel freshness crit"><h2>Sources and freshness</h2>
<p><span class="status status--critical">Stale</span> <b>The newest production day in last night's drop is {E(PDAY)}, {age_days} days before today (2026-11-15). There is no output, plan or downtime for {E(' or '.join(missing_days))}.</b>
This report is about {E(pday)} only. It is not yesterday, and nothing in it says what happened on 13 or 14 Nov, including whether the late work orders below were finished.</p>
<p class="note">Shifts in the day: CNC-01 reported shifts {E(', '.join(sorted(shifts_by_asset['CNC-01'])))}, and CNC-02 reported shift {E(', '.join(sorted(shifts_by_asset['CNC-02'])))} only. That matches the plan (16 h and 8 h). No site shift calendar is on file, so I can't say whether this was a full plant day.
The MES <code>production_day</code> column is used as given. No cross-midnight attribution rule is configured for this site.
I read the raw exports directly because no consolidated dataset was in the drop. Part numbers, work orders and assets matched exactly across all five files, so no key needed normalizing (figures block).
There's no maintenance or CMMS export in the drop, so open maintenance work orders can't be seen. That is not the same as none being open.</p>
<div class="table-scroll"><table><thead><tr><th>Source</th><th>File modified</th><th>Covers</th><th>Status</th></tr></thead><tbody>{fresh_rows}
<tr><td>Maintenance / CMMS export</td><td class="num">—</td><td class="num">—</td><td><span class="status status--critical">not in drop</span></td></tr>
<tr><td>Standard cost / downtime rate</td><td class="num">—</td><td class="num">—</td><td><span class="status status--critical">not available</span></td></tr></tbody></table></div></div>

<div class="panel"><h2>Headline figures, {E(pday)}</h2><div class="tiles">
<div class="stat-tile"><div class="stat-figure">{n(T_good)} / {n(T_plan)}</div><div class="stat-label">Good output against plan</div>
<p class="stat-context">{T_att:.1f}% attainment, {sgn(T_var)} units. Total output including scrap was {n(T_total)}.</p></div>
<div class="stat-tile"><div class="stat-figure">{p_(plant['OEE'])}</div><div class="stat-label">OEE, time-weighted across 2 assets</div>
<p class="stat-context">Availability {p_(plant['A'])} · Performance {p_(plant['P'])} · Quality {p_(plant['Q'])}. <b>Performance is the main loss.</b></p></div>
<div class="stat-tile"><div class="stat-figure">{n(DT_MIN)} min</div><div class="stat-label">Unplanned downtime, {DT_EV} events</div>
<p class="stat-context">Dollars <b>unpriced</b>: there's no confirmed downtime cost rate (see priced losses).</p></div>
<div class="stat-tile"><div class="stat-figure">{n(T_scrap)} units</div><div class="stat-label">Scrap</div>
<p class="stat-context">Dollars <b>unpriced</b>: no standard cost in the drop. {n(SCRAP_MIN)} machine-minutes were spent making it. {sh100}% of the scrapped units are PN-100.</p></div>
</div></div>

<div class="panel"><h2>Today's actions</h2><div class="table-scroll"><table>
<thead><tr><th>#</th><th>Issue</th><th>Impact</th><th>Next step</th><th>Owner</th><th>Type</th></tr></thead><tbody>
<tr><td class="num">1</td><td><b>WO-1002</b> (PN-200, CNC-02): {n(W['WO-1002']['good'])} good of {n(W['WO-1002']['ordered'])}, so <b>{n(W['WO-1002']['short'])} short</b> as of {E(PDAY)}. Due {E(W['WO-1002']['due'])}, {W['WO-1002']['days_past_due']} days ago. Status still RELEASED.</td>
<td>Past due if 13 Nov output didn't close the gap. Commitment impact not traceable: there's no work order to sales order link in the export.</td><td>Confirm 13–14 Nov output for WO-1002. If it's still short, decide on draft move A below (about {n(W['WO-1002']['make_up_min'])} ideal run minutes on CNC-02).</td><td>suggested: production scheduler</td><td><span class="status status--warn">Decision</span></td></tr>
<tr><td class="num">2</td><td><b>WO-1001</b> (PN-100, CNC-01): {n(W['WO-1001']['good'])} good of {n(W['WO-1001']['ordered'])}, so <b>{n(W['WO-1001']['short'])} short</b>. Due {E(W['WO-1001']['due'])}, {W['WO-1001']['days_past_due']} day ago. Status RELEASED.</td>
<td>Past due if 13–14 Nov output didn't close the gap. Commitment impact not traceable (no sales order link).</td><td>Confirm 13–14 Nov output. If it's still short, decide on draft move B (about {n(W['WO-1001']['make_up_min'])} ideal run minutes on CNC-01).</td><td>suggested: production scheduler</td><td><span class="status status--warn">Decision</span></td></tr>
<tr><td class="num">3</td><td>The 13 and 14 Nov exports did not land. The newest data is {age_days} days old.</td><td>Every figure on this page describes 12 Nov. Neither late work order's status can be confirmed.</td><td>Find out why the export job didn't deliver 13–14 Nov, and re-run once it lands.</td><td>suggested: MES / IT export owner</td><td><span class="status status--warn">Investigation</span></td></tr>
<tr><td class="num">4</td><td>There's no downtime cost rate and no standard cost, so no loss can be priced.</td><td>Losses are reported in minutes and units only.</td><td>Set a downtime cost per hour (say "update our labour rate", or set <code>MFG_DOWNTIME_COST_PER_HOUR</code>). Supply standard material cost for PN-100 and PN-200. Also confirm whether finance's "MILL-V" rate applies to work centre "VMC".</td><td>suggested: plant controller</td><td><span class="status status--warn">Decision</span></td></tr>
<tr><td class="num">5</td><td>Performance is about 87% on both machines (CNC-01 {p_(o1['P'])}, CNC-02 {p_(o2['P'])}). That is roughly {n(round(runT - agg['ideal']))} run-minutes unaccounted for, which is more than twice the logged downtime.</td>
<td>This is the largest OEE loss. It is spread across both machines and it is uncoded.</td><td>Check whether the routing standards (1.0 and 1.8 min/unit) include load/unload, and whether there were short stops that weren't logged.</td><td>suggested: manufacturing engineer</td><td><span class="status status--warn">Investigation</span></td></tr>
<tr><td class="num">6</td><td>CNC-02 lost 20 min waiting on material (MAT, 13:00).</td><td>No shortage is visible in the drop: there's no inventory or PO export.</td><td>None today unless it recurs.</td><td>suggested: materials planner</td><td><span class="status">Observation</span></td></tr>
</tbody></table></div></div>

<div class="panel"><h2>Floor view</h2><p class="note">There's no floor layout on file for {E(site)}. To set one up, attach a floor plan and ask for a floor view. I'll propose the machine matches for you to confirm.</p></div>

<div class="panel"><details open><summary>Output against plan, {E(pday)}</summary>
<div class="table-scroll"><table><thead><tr><th>Cell</th><th>WC</th><th>Asset</th><th>Part</th><th class="num">Plan</th><th class="num">Good</th><th class="num">Scrap</th><th class="num">Total</th><th class="num">Var (good)</th><th class="num">Attain</th></tr></thead>
<tbody>{oap_rows}</tbody></table></div>
<p class="note">Variance is good units against planned units. Part numbers matched exactly between plan and MES (PN-100, PN-200), so nothing here is provisional and no normalization is pending.
CELL-A is the only cell, and both lines above are in it.</p></details></div>

<div class="panel"><details open><summary>OEE per asset (grain: asset)</summary>
<div class="table-scroll"><table><thead><tr><th>Asset</th><th class="num">Planned min</th><th class="num">Downtime min</th><th class="num">Run min</th><th class="num">Availability</th><th class="num">Performance</th><th class="num">Quality</th><th class="num">OEE</th></tr></thead>
<tbody>{oee_rows}</tbody></table></div>
<p class="note"><b>Quality = good ÷ (good + scrap); no rework column, so first-pass yield could not be applied.</b><br>
Planned production time = the plan export's <code>planned_hours</code> per asset. No onboarding definition is on file, so it's unknown whether breaks and planned maintenance were already taken out.
Availability = (planned − logged unplanned downtime) ÷ planned. Performance = Σ(routing <code>run_min_per_unit</code> × (good + scrap)) ÷ run time. All three components were computed from data, and none were substituted.
Every planned asset reported output. No component is above 100%.</p></details></div>

<div class="panel"><details open><summary>Downtime: ranked by minutes and by frequency</summary>
<p class="note">Reason-code coverage: {len(other)} of {len(downtime)} events carry Other or blank, so every event is coded. Every row's duration agreed with its own start and end, so {len(dt_bad)} rows were held out.
That is only {DT_EV} events, which is too few to call a pattern.</p>
<h3>By total minutes</h3><div class="table-scroll"><table><thead><tr><th class="num">#</th><th>Code</th><th>Text</th><th>Asset</th><th class="num">Minutes</th><th class="num">Events</th></tr></thead><tbody>{rank_tbl(rank_min,'min')}</tbody></table></div>
<h3>By frequency</h3><div class="table-scroll"><table><thead><tr><th class="num">#</th><th>Code</th><th>Text</th><th>Asset</th><th class="num">Events</th><th class="num">Minutes</th></tr></thead><tbody>{rank_tbl(rank_freq,'freq')}</tbody></table></div>
{"<p class='note'>The two codes are tied on frequency at one event each. Order within the tie is by minutes.</p>" if ties else ""}
<h3>Event log</h3><div class="table-scroll"><table><thead><tr><th>Asset</th><th>Start</th><th>End</th><th class="num">Min</th><th>Code</th><th>Text</th></tr></thead><tbody>{dt_log}</tbody></table></div>
<p class="note">Maintenance work orders in progress: not shown, because no CMMS connector or maintenance export is in this drop.</p></details></div>

<div class="panel"><details open><summary>Priced losses</summary>
<div class="table-scroll"><table><thead><tr><th>Loss</th><th class="num">Quantity</th><th class="num">Dollars</th><th>Why</th></tr></thead><tbody>
<tr><td>Scrap PN-100 (CNC-01)</td><td class="num">{n(s100)} units</td><td class="num">unpriced</td><td>No standard cost for PN-100 in the drop. {n(round(s100*ict['PN-100'],2))} machine-min embedded.</td></tr>
<tr><td>Scrap PN-200 (CNC-02)</td><td class="num">{n(s200)} units</td><td class="num">unpriced</td><td>No standard cost for PN-200 in the drop. {n(round(s200*ict['PN-200'],2))} machine-min embedded.</td></tr>
<tr><td>Downtime TOOL (CNC-01)</td><td class="num">{n(by_code['TOOL']['minutes'])} min</td><td class="num">unpriced</td><td rowspan="2">There's no confirmed downtime cost rate (see below).</td></tr>
<tr><td>Downtime MAT (CNC-02)</td><td class="num">{n(by_code['MAT']['minutes'])} min</td><td class="num">unpriced</td></tr>
</tbody></table></div>
<p class="note"><b>Rate assumption:</b> none. The rate was resolved in this order: (1) <code>MFG_DOWNTIME_COST_PER_HOUR</code>, not set; (2) a confirmed rate in the plant profile, but no profile exists; (3) a placeholder there, likewise none.
<code>inputs/rates_memo.txt</code> (finance memo, 1 Oct 2026) is a candidate source, but I didn't price on it for two reasons. First, it lists burdened <i>shop</i> rates for MILL-H, MILL-V, TURN and INSP, while these exports use work centre <code>VMC</code>, which isn't on the memo. Mapping VMC to MILL-V would be a guess that nobody has approved. Second, a shop rate is not a downtime cost per hour.
The memo's scrap rule is standard material plus value-added labour at the scrapping work centre. It needs a standard material cost, and the drop has none.
Once someone confirms the VMC rate and supplies material cost per part, the next run will price both lines. Until then the dollar figures are <i>unknown</i>, not $0.</p></details></div>

<div class="panel"><details open><summary>Week-over-week movers</summary><p class="note">Skipped. The drop holds one production day ({E(PDAY)}), so there's no earlier day to compare against. This is a standalone run, so it has no stored day history.</p></details></div>

<div class="panel"><details open><summary>Exceptions and commitment impact</summary>
<div class="table-scroll"><table><thead><tr><th>WO</th><th>Part</th><th>Asset</th><th class="num">Ordered</th><th class="num">Good</th><th class="num">Scrap</th><th class="num">Short</th><th>Due</th><th>Status</th><th>State as of {E(PDAY)}</th></tr></thead><tbody>{wo_tbl}</tbody></table></div>
<p class="note">Commitment impact not traceable: there's no work order to sales order link in the work order export. This affects {len(late)} work orders (WO-1001, WO-1002). The order behind each one has not been inferred from part number.</p>
<h3>Checked, nothing wrong</h3><ul class="note">
<li><b>WO-1003</b> (PN-100, CNC-01): {n(W['WO-1003']['good'])} good of {n(W['WO-1003']['ordered'])} ordered, due today (15 Nov). The quantity is complete. Its status still reads RELEASED, which is a housekeeping close-out and not a problem.</li>
<li>Data integrity: there were no duplicate output keys and no downtime rows with bad times. No key mismatches were found between plan, MES, routing and work orders.</li></ul></details></div>

<div class="panel"><details open><summary>Reschedule proposals (drafted for the scheduler, not applied)</summary>
<p class="note">Both moves depend on 13–14 Nov output, which isn't in the drop. Each move is valid only if that work order is still short. The two moves use different machines, so they don't interact.</p>
<h3>A. WO-1002: finish the remaining {n(W['WO-1002']['short'])} × PN-200 on CNC-02</h3>
<p><b>Move:</b> run {n(W['WO-1002']['short'])} PN-200 on CNC-02 in its next available shift. That is about {n(W['WO-1002']['make_up_min'])} ideal minutes at 1.8 min/unit. At the {p_(o2['P'])} performance seen on 12 Nov it would be roughly {n(round(W['WO-1002']['make_up_min']/(o2['P']/100)))} minutes, with no scrap allowance. If CNC-02 is still set up for PN-200, there's no changeover. If it has moved to another part, the changeover cost can't be estimated because the drop has no changeover data.<br>
<b>Displaces:</b> unknown. The plan export holds 12 Nov only, so I can't see what CNC-02 is loaded with next.<br>
<b>Still misses:</b> WO-1002 is already {W['WO-1002']['days_past_due']} days past its 13 Nov due date, so this move limits the lateness and can't recover the date.<br>
<b>Checked:</b> due dates, quantities, the routing time for PN-200 on VMC, and the 12 Nov asset assignment. <b>Not checked:</b> 13–14 Nov output, CNC-02's current load and setup, material on hand (CNC-02 waited on material on 12 Nov), operator availability, and the customer order behind the WO.</p>
<h3>B. WO-1001: finish the remaining {n(W['WO-1001']['short'])} × PN-100 on CNC-01</h3>
<p><b>Move:</b> run {n(W['WO-1001']['short'])} PN-100 on CNC-01. That is about {n(W['WO-1001']['make_up_min'])} ideal minutes, or roughly {n(round(W['WO-1001']['make_up_min']/(o1['P']/100)))} at 12 Nov performance. CNC-01 also ran WO-1003 (the same part), so if it's still on PN-100 there's no changeover. Otherwise the changeover cost is unknown.<br>
<b>Displaces:</b> unknown, because there's no plan after 12 Nov.<br>
<b>Still misses:</b> WO-1001 is {W['WO-1001']['days_past_due']} day past due, so the date itself can't be recovered.<br>
<b>Checked:</b> due dates, quantities, and the PN-100 routing on VMC. <b>Not checked:</b> 13–14 Nov output, CNC-01's current load, tooling (CNC-01 lost 45 min to a tool change overrun on 12 Nov), material, and the customer order.</p></details></div>

<div class="panel"><details><summary>Sources, methods and assumptions</summary><ul class="note">
<li>Inputs: <code>inputs/pulse_oee/</code> plan.csv, output.csv, downtime.csv, routing.csv and work_orders.csv; <code>inputs/rates_memo.txt</code>. All are SYNTHETIC.</li>
<li>No plant profile or rates page is on file. The site name comes from the MES <code>site</code> column. The defaults are used and labelled.</li>
<li>Production day is the MES <code>production_day</code> column. Downtime was attributed to the day of <code>started_at</code>.</li>
<li>The OEE roll-up is time-weighted (sum of numerators over sum of denominators), not an average of percentages.</li>
<li>This report is read-only. Nothing was written to any system, and the reschedule moves are drafts.</li>
<li>Structured data: <code>morning-report-data.json</code>. Figures block: <code>figures-block.csv</code> (below).</li></ul></details></div>

<div class="panel"><details><summary>Figures block ({len(FIG)} rows, computed in code)</summary>
<div class="table-scroll"><table><thead><tr><th>Figure</th><th class="num">Value</th><th>From</th><th>Filter</th></tr></thead><tbody>{figs}</tbody></table></div></details></div>

<footer class="page-footer">Generated by <strong>daily-production-report</strong> (standalone run) — Manufacturing. Not published to any dashboard. Save it over yesterday's.</footer>
</main></body></html>"""
with open(os.path.join(OUT, "morning-report.html"), "w", encoding="utf-8") as f:
    f.write(PAGE)
print(json.dumps({"oap": oap, "oee": oee, "plant": plant, "wo": wo_rows, "dt_bad": len(dt_bad), "scrap_min": SCRAP_MIN,
                  "unaccounted_run_min": round(runT - agg['ideal'], 2), "figs": len(FIG)}, indent=1))
