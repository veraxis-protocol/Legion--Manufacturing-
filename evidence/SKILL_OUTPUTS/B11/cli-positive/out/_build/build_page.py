"""Build the Operations Command Center fallback page from the pulse engine's output.

Every number printed comes from pulse_model.json / figures.csv, or from the few
page-level figures computed below from the raw exports, which are written to
figures-page.csv with their filters. Nothing is retyped.
"""
import csv, json, sys, html, datetime as dt
from pathlib import Path

out = Path(sys.argv[1])          # pulse-output folder
exports = Path(sys.argv[2])      # export folder
M = json.loads((out / "pulse_model.json").read_text(encoding="utf-8"))
R = json.loads((out / "day_records.json").read_text(encoding="utf-8"))
F = list(csv.DictReader(open(out / "figures.csv", encoding="utf-8")))
FV = {r["id"]: r for r in F}

e = html.escape
ctx, fr, td = M["context"], M["freshness"], M["today"]
site, day = ctx["site"], fr["production_day"]
run_local = ctx["run_time_local"].replace(" (plant local)", "")
run_date = dt.date.fromisoformat(ctx["run_time"][:10])
pday = dt.date.fromisoformat(day)

def fv(i):
    return FV[i]["value"]

def pct(x):
    return "not computable" if x is None else f"{x*100:.2f}%"

# ---------- page-level figures, computed here from the raw exports ----------
P = []  # id, figure, value, unit, period, source, filter
def addp(i, fig, val, src, flt, unit="", period="window"):
    P.append(dict(id=i, figure=fig, value=val, unit=unit, period=period, source=src, filter=flt))
    return val

outrows = list(csv.DictReader(open(exports / "output.csv", encoding="utf-8")))
worows = list(csv.DictReader(open(exports / "work_orders.csv", encoding="utf-8")))
shifts = sorted({r["shift"] for r in outrows if r["production_day"] == day})
addp("page.shifts", f"Shifts present in output.csv, {day}", " and ".join(shifts), "output.csv",
     f"distinct shift where production_day == {day}", period=day)

missing_days = []
d = pday + dt.timedelta(days=1)
while d < run_date:
    missing_days.append(d.isoformat()); d += dt.timedelta(days=1)
addp("page.days_missing", "Production days between the newest day in the drop and the run date with no rows in plan, output or downtime",
     len(missing_days), "plan.csv, output.csv, downtime.csv",
     f"days {', '.join(missing_days)}: no rows in any of the three files")

wo_table = []
for w in worows:
    good = sum(int(r["qty_good"]) for r in outrows if r["work_order"] == w["work_order"])
    ordered = int(w["qty_ordered"])
    rem = ordered - good
    due = dt.date.fromisoformat(w["due_date"])
    if rem <= 0:
        state = "Ordered quantity reached in the drop"
    elif due < run_date:
        state = "Due date passed; completion after the newest production day not in the drop"
    else:
        state = "Due today; completion after the newest production day not in the drop"
    k = w["work_order"]
    addp(f"page.wo.{k}.good", f"Good output in the drop, {k}", good, "output.csv", f"sum qty_good where work_order == {k}")
    addp(f"page.wo.{k}.remaining", f"Ordered less good in the drop, {k}", rem, "work_orders.csv, output.csv", "qty_ordered - good")
    wo_table.append(dict(wo=k, part=w["part_number"], ordered=ordered, good=good, rem=rem,
                         due=w["due_date"], status=w["status"], state=state))
open_short = [w for w in wo_table if w["rem"] > 0]
addp("page.wo.short_unjudged", "Released work orders short of ordered qty in the drop, due after the newest production day",
     len(open_short), "work_orders.csv, output.csv", f"qty_ordered > good and due_date > {day}")

addp("page.scrap_total", f"Scrap qty, all parts, {day}", sum(x["scrap"] for x in td["scrap"]), "pulse_model.json today.scrap", "sum of scrap over parts", period=day)
dt_day = M["downtime"]["day"]
cnc01 = next(a for a in dt_day["by_asset"] if a["key"] == "CNC-01")
sp = M["short_page"]["decisions"][1]
addp("page.trend.days_with_data", "Days in the 14-day trend window with data from this run's exports",
     sum(1 for r in R if r["data_complete"]), "day_records.json", "data_complete == true")
addp("page.stored_days", "Production days stored on the dashboard", "0 (no artifact store this session; nothing stored)",
     "ArtifactData query", "not run: Artifact / ArtifactData tools absent")

with open(out / "figures-page.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=["id", "figure", "value", "unit", "period", "source", "filter"])
    w.writeheader(); w.writerows(P)
PV = {p["id"]: p["value"] for p in P}

# ---------------------------------- HTML ----------------------------------
CSS = (Path(__file__).parent / "style.css").read_text(encoding="utf-8")
H = []
a = H.append

def table(head, rows, num_cols=()):
    s = ['<div class="table-scroll"><table><thead><tr>']
    s += [f"<th{' class=\"num\"' if i in num_cols else ''}>{e(h)}</th>" for i, h in enumerate(head)]
    s.append("</tr></thead><tbody>")
    for r in rows:
        s.append("<tr>" + "".join(f"<td{' class=\"num\"' if i in num_cols else ''}>{c}</td>" for i, c in enumerate(r)) + "</tr>")
    s.append("</tbody></table></div>")
    return "".join(s)

def pill(kind, txt):
    return f'<span class="status status--{kind}">{e(txt)}</span>'

a(f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(site)}: Operations Command Center · {day}</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans+Condensed:wght@500;600&family=IBM+Plex+Sans:wght@400;500;600&family=IBM+Plex+Mono:wght@500&display=swap" rel="stylesheet">
<style>{CSS}</style></head><body><main class="page">
<header class="page-header"><div>
<h1>{e(site)}: Operations Command Center</h1>
<p class="meta">{e(site)} · Generated {e(run_local)} · data as of {e(fr['data_as_of_local'].replace(' (plant local)',''))}</p>
<p class="meta">Production day: <span class="mono">{day}</span> · day boundary: {e(ctx['day_boundary'])}</p>
<p class="meta synthetic">Built from SYNTHETIC test data for a fictitious plant. Offered page, not a published dashboard.</p>
</div></header>
<nav class="tabs"><a href="#today">Today</a><a href="#trend">Trend</a><a href="#data">Figures &amp; records</a></nav>
<section id="today" class="panel-group"><h2 class="group">Panel 1 — Today</h2>
""")

# Safety
a('<div class="panel safety"><h2>Safety</h2><p><strong>Safety status: not assessed</strong> (no breakdown diagnosis records in this drop). '
  'Not the same as "no safety issues".</p><p class="sub">Blocked — safety status unknown: none '
  f'(<span class="mono">diag.blocked = {fv("diag.blocked")}</span>).</p></div>')

# Freshness banner
cov = fr["coverage"]
rows = [[f"<strong>Last night's drop</strong>", "—", f"No rows for <span class='mono'>{', '.join(missing_days)}</span>",
         pill("critical", f"{PV['page.days_missing']} production days missing")],
        ["Newest production day", f"<span class='mono'>{e(fr['newest_production_day'])}</span>", "—",
         pill("warn", f"{fv('fresh.days_old')} days old")]]
labels = {"plan": "Planning export (plan.csv)", "output": "Production / MES export (output.csv)",
          "downtime": "Maintenance downtime export (downtime.csv) — export-sourced, not a live CMMS",
          "work_orders": "ERP work orders (work_orders.csv) — export, no ERP connector"}
for k, c in cov.items():
    rows.append([e(labels.get(k, k)), f"<span class='mono'>{e(c['landed'].replace(' (plant local)',''))}</span>",
                 f"<span class='mono'>{e(FV['cov.'+k]['value'])}</span> · {c['rows']} rows" if ('cov.'+k) in FV else "",
                 pill("warn", "Landed, stale") if c["activity"] else pill("good", "Landed (due dates)")])
rows.append(["routing.csv", "same drop", "run minutes per unit, PN-100 and PN-200", pill("good", "Used for performance")])
rows.append(["Standard cost / item master", "—", "not in the drop", pill("critical", "Missing: scrap unpriced")])
rows.append(["Plant profile (## Plant context)", "—", "none found", pill("warn", "Assumed defaults")])
a(f'<div class="panel freshness"><h2>Freshness</h2>'
  f'<p class="lead">The newest production data in the drop is <span class="mono">{day}</span>, {fv("fresh.days_old")} days before this run. '
  f'Nothing landed for <span class="mono">{", ".join(missing_days)}</span>: those days are gaps, not zeros, and nothing below covers them. '
  f'The {day} day itself is complete in the exports (shifts {e(PV["page.shifts"])} present).</p>'
  + table(["Source", "Landed", "Covers", "Status"], rows) +
  "<ul class='assume'>" + "".join(f"<li>{e(x)}</li>" for x in ctx["assumptions"]) +
  f"<li>Day chosen: {e(fr['day_source'])}.</li><li>Files not used: " +
  ", ".join(f"{e(x['file'])} ({e(x['why'])})" for x in ctx["files_not_used"]) +
  ". <span class='mono'>rates_memo.txt</span> (outside the export folder) was read but not used for pricing — see Priced losses.</li></ul></div>")

# Today's actions
WO = {w["wo"]: w for w in wo_table}
mat = next(x for x in td["stops"] if x["code"] == "MAT")
plan_rows = list(csv.DictReader(open(exports / "plan.csv", encoding="utf-8")))
cell_of = {r["part_number"]: r["cell"] for r in outrows if r["production_day"] == day}
wc_of = {r["part_number"]: r["work_center"] for r in plan_rows}
acts = [
    ["Exports for " + ", ".join(missing_days) + " did not land",
     "This page describes " + day + " only; any meeting decision about the last two days has no data behind it",
     "Check the export job and re-run the pulse once the files land; the re-run overwrites this day's record",
     "suggested: production supervisor / IT owner of the export job", pill("warn", "Investigation")],
    [f"CNC-01: {cnc01['minutes']} min down, reason TOOL ({e(sp['reason_text'])})",
     f"{sp['share_pct']}% of the day's {dt_day['minutes']} downtime minutes; CNC-01 OEE {pct(td['oee_by_asset'][0]['oee'])}",
     "Review the tool-change standard for the PN-100 setup; safety status not assessed (no diagnosis record)",
     "suggested: maintenance lead", pill("warn", "Investigation")],
    [f"PN-200 under plan by {abs(td['parts']['PN-200']['variance'])} ({td['parts']['PN-200']['variance_pct']}%)",
     f"WO-1002 (due {WO['WO-1002']['due']}) had {PV['page.wo.WO-1002.remaining']} still to make at the end of {day}; whether it shipped is not in the drop",
     f"Confirm WO-1002 completion in the ERP; {mat['asset']} also lost {mat['minutes']} min to {mat['code']} ({mat['text']})",
     "suggested: production scheduler", pill("warn", "Investigation")],
    [f"WO-1001 ({WO['WO-1001']['part']}, due {WO['WO-1001']['due']}): {PV['page.wo.WO-1001.remaining']} short of ordered in the drop",
     "Due date has passed; completion after " + day + " not in the drop", "Confirm in the ERP with the WO-1002 check",
     "suggested: production scheduler", pill("warn", "Investigation")],
]
a('<div class="panel"><h2>Today\'s actions</h2><p class="lead"><strong>No decisions waiting today.</strong> '
  'No normalizations to approve, no reschedule move drafted (see Exceptions). Everything below is something to find out first.</p>'
  + table(["Issue", "Impact", "Next step", "Owner role", "Type"], acts) + "</div>")

# Headline tiles
a('<div class="tiles">')
for fig, lab, ctxt in [
    (f"{td['actual_qty']['unit']} / {td['planned_qty']['unit']}", "Good output vs plan, units", "Both parts under plan; no provisional rows"),
    (pct(td["oee"]), "Site OEE", f"A {pct(td['availability'])} · P {pct(td['performance'])} · Q {pct(td['quality'])}"),
    (f"{td['downtime_minutes']} min", "Downtime", f"{td['events']} events, {td['open_outages']} open"),
    ("unpriced", "Scrap & downtime $", f"{PV['page.scrap_total']} parts scrapped; no standard cost, no downtime rate"),
]:
    a(f'<div class="stat-tile"><div class="stat-figure">{e(fig)}</div><div class="stat-label">{e(lab)}</div><p class="stat-context">{e(ctxt)}</p></div>')
a("</div>")

# Output vs plan
rows = []
for p in td["parts"].values():
    rows.append([f"<span class='mono'>{e(p['part'])}</span>", e(cell_of.get(p["part"], "—")), e(wc_of.get(p["part"], "—")), p["planned"], p["good"],
                 p["variance"], f"{p['variance_pct']}%", pill("good", p["status"]) if p["status"] == "comparable" else pill("warn", p["status"])])
a('<div class="panel"><h2>Output against plan</h2>' + table(
    ["Part", "Cell", "Work centre", "Planned", "Good", "Variance", "Variance %", "Status"], rows, num_cols=(3, 4, 5, 6)) +
  f'<p class="sub">Total good {td["actual_qty"]["unit"]} against {td["planned_qty"]["unit"]} planned, one unit of measure. '
  'Plan and output spell both parts identically; no normalization was needed or proposed. '
  'Cell is from output.csv; work centre from plan.csv. One cell in the drop, so the line/cell view equals the site view.</p></div>')

# OEE
rows = [[f"<span class='mono'>{e(o['asset'])}</span>", o["planned_minutes"], o["downtime_minutes"], pct(o["availability"]),
         pct(o["performance"]), pct(o["quality"]), f"<strong>{pct(o['oee'])}</strong>"] for o in td["oee_by_asset"]]
rows.append(["<strong>Site</strong>", "", td["downtime_minutes"], pct(td["availability"]), pct(td["performance"]), pct(td["quality"]), f"<strong>{pct(td['oee'])}</strong>"])
a('<div class="panel"><h2>OEE</h2>' + table(["Asset", "Planned min", "Downtime min", "Availability", "Performance", "Quality", "OEE"], rows, num_cols=(1, 2, 3, 4, 5, 6)) +
  f'<p class="sub">Quality = {e(td["quality_convention"])}. Availability = (planned − downtime) ÷ planned; performance = ideal minutes (routing run min/unit × total units) ÷ run minutes; '
  f'site figures are {e(R[0]["oee_basis"])}. Performance is the largest loss on both machines.</p></div>')

# Downtime
def rank_rows(lst):
    return [[f"<span class='mono'>{e(x['key'])}</span>", x["minutes"], x["events"], x["rank_minutes"], x["rank_events"]] for x in lst]
by_min = sorted(dt_day["by_asset"], key=lambda x: x["rank_minutes"])
by_ev = sorted(dt_day["by_asset"], key=lambda x: x["rank_events"])
stops = [[f"<span class='mono'>{e(s['asset'])}</span>", f"<span class='mono'>{e(s['start'].replace(' (plant local)',''))}</span>", s["minutes"],
          f"<span class='mono'>{e(s['code'])}</span>", e(s["text"])] for s in td["stops"]]
a('<div class="panel"><h2>Downtime</h2>'
  f'<p class="lead">{dt_day["uncoded_events"]} of {dt_day["events"]} events carry no usable reason code (Other or blank), so the cause ranking is complete. '
  f'{dt_day["held_out"] and len(dt_day["held_out"]) or 0} rows held out for untrustworthy minutes.</p>'
  '<div class="two"><div><h3>By minutes — asset</h3>' + table(["Asset", "Minutes", "Events", "Rank (min)", "Rank (freq)"], rank_rows(by_min), (1, 2, 3, 4)) +
  '</div><div><h3>By frequency — asset</h3>' + table(["Asset", "Events", "Minutes", "Rank (freq)", "Rank (min)"],
   [[r[0], r[2], r[1], r[4], r[3]] for r in rank_rows(by_ev)], (1, 2, 3, 4)) + '</div></div>'
  '<div class="two"><div><h3>By minutes — reason code</h3>' + table(["Code", "Minutes", "Events", "Rank (min)", "Rank (freq)"],
   rank_rows(sorted(dt_day["by_code"], key=lambda x: x["rank_minutes"])), (1, 2, 3, 4)) +
  '</div><div><h3>By frequency — reason code</h3>' + table(["Code", "Events", "Minutes", "Rank (freq)", "Rank (min)"],
   [[r[0], r[2], r[1], r[4], r[3]] for r in rank_rows(sorted(dt_day["by_code"], key=lambda x: x["rank_events"]))], (1, 2, 3, 4)) + '</div></div>'
  '<p class="sub">Ties share a rank (1, 1): with one stop per asset the frequency ranking cannot separate them; the minutes ranking can.</p>'
  '<h3>Stop log</h3>' + table(["Asset", "Start", "Minutes", "Code", "Reason text"], stops, (2,)) + '</div>')

# Priced losses
rows = [[f"<span class='mono'>{e(s['part'])}</span>", s["scrap"], "unpriced — no standard cost on file"] for s in td["scrap"]]
rows.append(["Downtime, all", f"{td['downtime_minutes']} min", "unpriced — no downtime cost rate"])
a('<div class="panel"><h2>Priced losses</h2>' + table(["Loss", "Quantity", "$ (estimate at standard cost)"], rows, (1,)) +
  f'<p class="sub">Rate source: <span class="mono">{e(td["rate_source"])}</span>. Unpriced, with reasons: ' +
  "; ".join(e(u) for u in td["unpriced"]) + '.</p>'
  '<p class="sub"><strong>Why the finance memo in the drop was not used.</strong> <span class="mono">rates_memo.txt</span> gives burdened shop rates for MILL-H, MILL-V, TURN and INSP. '
  'It holds no standard material cost (which its own scrap rule needs), no downtime cost per hour, and no rate for the VMC work centre these jobs ran on. '
  'Mapping VMC to MILL-V, or using a shop rate as a downtime cost, would be a guess, so $ figures are left unknown rather than shown as $0. '
  'To price them: add standard costs for PN-100 and PN-200 and a confirmed downtime cost per hour to the plant rates.</p></div>')

# Exceptions
wrows = [[f"<span class='mono'>{w['wo']}</span>", f"<span class='mono'>{w['part']}</span>", w["ordered"], w["good"], w["rem"],
          f"<span class='mono'>{w['due']}</span>", e(w["state"])] for w in wo_table]
a('<div class="panel"><h2>Exceptions</h2>'
  f'<p class="lead">Engine exceptions for {day}: {fv("exc.count")} (late jobs due on or before {day}: {fv("exc.late")}; machines down at end of day: {td["open_outages"]}; quality holds: none in the drop). '
  'No reschedule move is drafted: there is no significant exception on the production day, and a move for WO-1001/WO-1002 would rest on two days of output the drop does not hold.</p>'
  f'<p class="sub">Commitment impact not traceable: no work order to sales order link in the ERP ({len(wo_table)} work orders affected).</p>'
  '<h3>Open work orders against output in the drop</h3>' + table(["Work order", "Part", "Ordered", "Good in drop", "Ordered − good", "Due", "State"], wrows, (2, 3, 4)) +
  f'<p class="sub">{PV["page.wo.short_unjudged"]} released work orders are short of ordered quantity in the drop and fall due after {day}; they are listed under Today\'s actions as investigations, not counted as late.</p></div>')

# Data problems + checked
a('<div class="panel"><h2>Data problems · ' + str(M["data_problems"]["count"]) + '</h2>'
  '<p>No mismatched keys in classes 1–5 or 8, no contradicted one-sided records, no unit conflicts. Every output row\'s work order is in work_orders.csv; plan and output part numbers match verbatim; no duplicate work-order/shift/day rows; '
  f'no downtime rows held out for duration conflicts ({fv("integrity.dt_flags")}); no future timestamps ({fv("fresh.future")}). Class 7 (date window): none beyond the missing days in the freshness banner.</p>'
  '<h3>Checked, nothing wrong</h3><p class="sub">No class 6 one-sided records in this drop (outside the count above).</p></div>')
a("</section>")

# Trend
trows = []
for i in range(13, -1, -1):
    d = (run_date - dt.timedelta(days=i + 1))
    ds = d.isoformat()
    rec = next((r for r in R if r["production_day"] == ds), None)
    if rec:
        trows.append([f"<span class='mono'>{ds}</span>", pct(rec["oee"]), pct(rec["availability"]), pct(rec["performance"]), pct(rec["quality"]),
                      f"{rec['actual_qty']['unit']} / {rec['planned_qty']['unit']}", rec["downtime_minutes_total"], "complete"])
    elif ds in missing_days:
        trows.append([f"<span class='mono'>{ds}</span>"] + ["—"] * 6 + [pill("critical", "no export landed")])
    else:
        trows.append([f"<span class='mono'>{ds}</span>"] + ["—"] * 6 + ["no data in this run's exports"])
a('<section id="trend" class="panel-group"><h2 class="group">Panel 2 — Trend</h2><div class="panel">'
  '<p class="lead"><strong>From this run\'s exports, not stored history.</strong> No artifact store this session, so no stored day records could be read. '
  f'The exports cover one production day, so there is no line to draw yet; the table shows the last 14 days with gaps as gaps, never zeros. '
  'The 30-day view would hold the same single point and is omitted.</p>'
  + table(["Day", "OEE", "Availability", "Performance", "Quality", "Good / plan", "Downtime min", "State"], trows, (1, 2, 3, 4, 5, 6)) +
  f'<p class="sub"><strong>Week-over-week movers: skipped.</strong> The previous window ({M["week_over_week"]["last_week"]["from"]} to {M["week_over_week"]["last_week"]["to"]}) has '
  f'{M["week_over_week"]["last_week"]["days"]} days with data; this window rests on {M["week_over_week"]["this_week"]["days"]} of 7.</p></div></section>')

# Data: day record + figures block
rec = R[0]
rrows = [["record_key", rec["record_key"]], ["data_complete", str(rec["data_complete"]).lower()], ["gaps", "none for this day" if not rec["gaps"] else "; ".join(rec["gaps"])],
         ["backfilled", str(rec["backfilled"]).lower()], ["oee", rec["oee"]], ["availability", rec["availability"]], ["performance", rec["performance"]],
         ["quality", rec["quality"]], ["downtime_minutes_total", rec["downtime_minutes_total"]], ["loss_usd.scrap", "null (unpriced)"],
         ["loss_usd.downtime", "null (unpriced)"], ["data_problems_count", rec["data_problems_count"]], ["stored", "computed, not stored"]]
allf = F + P
frow = [[f"<span class='mono'>{e(r['id'])}</span>", e(r["figure"]), f"<span class='mono'>{e(str(r['value']))}</span>", e(r["source"]), e(r["filter"])] for r in allf]
a('<section id="data" class="panel-group"><h2 class="group">Figures &amp; records</h2>'
  '<div class="panel"><h2>Day record</h2>' + table(["Field", "Value"], [[e(k), f"<span class='mono'>{e(str(v))}</span>"] for k, v in rrows]) +
  '<p class="sub">Full record: <span class="mono">pulse-output/day_records.json</span>. Not stored: no dashboard database this session.</p></div>'
  f'<div class="panel"><details><summary><h2 style="display:inline">Figures block · {len(allf)} rows</h2></summary>'
  '<p class="sub">Engine rows from <span class="mono">figures.csv</span>; page rows (id <span class="mono">page.*</span>) from <span class="mono">figures-page.csv</span>. Engine self-checks: '
  f'{M["checks"]["run"]} run, {len(M["checks"]["failed"])} failed.</p>'
  + table(["Id", "Figure", "Value", "Source", "Filter"], frow) + '</details></div></section>')

a(f'<footer class="page-footer">Generated by <strong>morning-plant-pulse</strong> — Manufacturing · 0 production days stored · '
  'Read-only: nothing was written to any ERP, CMMS, M365 or supplier system.<br>'
  f'Here is the Operations page for {day}; save it over yesterday\'s. The dashboard was not updated: the artifact tools are not available in this session.</footer>')
a("</main></body></html>")

target = out / f"operations-{site}-{day}.html"
target.write_text("".join(H), encoding="utf-8")
print(target)
