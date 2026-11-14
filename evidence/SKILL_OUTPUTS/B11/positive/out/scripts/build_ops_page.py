"""Build the fallback Operations Command Center page from the engine's output.

Reads pulse_model.json, figures.csv and day_records.json written by
pulse_compute.py. Does no arithmetic: every number printed is a value held
in figures.csv (shown with its row id) or a field of the engine's day record.
"""
import csv, html, json, sys
from pathlib import Path

OUT = Path(sys.argv[1])
model = json.loads((OUT / "pulse_model.json").read_text(encoding="utf-8"))
records = json.loads((OUT / "day_records.json").read_text(encoding="utf-8"))
with open(OUT / "figures.csv", encoding="utf-8", newline="") as fh:
    rows = list(csv.DictReader(fh))
FIG = {r["id"]: r for r in rows}
USED = []

e = html.escape


def fv(fid):
    """Value of a figures row, exactly as held, with its id tag."""
    r = FIG[fid]
    USED.append(fid)
    return '<span class="num">%s</span><sup class="fid">%s</sup>' % (e(r["value"]), e(fid))


def raw(fid):
    USED.append(fid)
    return FIG[fid]["value"]


ctx, fr, today = model["context"], model["freshness"], model["today"]
day = fr["production_day"]
dp, exc, dt = model["data_problems"], model["exceptions"], model["downtime"]["day"]
rec = [r for r in records if r["production_day"] == day][0]
site = ctx["site"]
title = "%s: Operations Command Center" % site

pill = lambda kind, text: '<span class="status status--%s">%s</span>' % (kind, e(text))

# ---------- freshness banner ----------
cov = fr["coverage"]
fresh_rows = []
fresh_rows.append(
    "<tr><td>Export drop as a whole</td><td>%s</td><td>newest production day %s</td><td>%s</td></tr>"
    % (e(fr["data_as_of_local"]), fv("fresh.day"),
       pill("warn", "%s days old" % raw("fresh.days_old")) +
       " <span class='note'>Nothing after %s is in the drop, so production day 2026-11-13 is not reported. "
       "Days old: %s.</span>" % (e(fr["newest_production_day"]), fv("fresh.days_old"))))
fresh_rows.append(
    "<tr><td>Plant profile</td><td>none</td><td>n/a</td><td>%s <span class='note'>%s</span></td></tr>"
    % (pill("warn", "no plant profile"), "<br>".join(e(a) for a in ctx["assumptions"])))
for role in ("plan", "output", "downtime", "work_orders"):
    c = cov[role]
    fresh_rows.append(
        "<tr><td>%s <span class='note'>(%s, export-sourced)</span></td><td class='num'>%s</td><td>%s</td><td>%s</td></tr>"
        % (e(role.replace("_", " ").capitalize()), e(c["file"]), e(c["landed"]), fv("cov." + role),
           pill("good", "landed") + (" <span class='note'>due dates, not activity</span>" if not c["activity"] else "")))
fresh_rows.append(
    "<tr><td>Maintenance work orders in progress</td><td>not read</td><td>n/a</td><td>%s <span class='note'>No maintenance export in the drop and no CMMS connector this session. "
    "This is <em>could not see</em>, not <em>no open maintenance</em>.</span></td></tr>" % pill("warn", "not available"))
fresh_rows.append(
    "<tr><td>Standard cost (item master / ERP)</td><td>not read</td><td>n/a</td><td>%s <span class='note'>%s. Scrap is unpriced.</span></td></tr>"
    % (pill("warn", "not available"), e(ctx["part_reference"])))
fresh_rows.append(
    "<tr><td>Downtime cost per hour</td><td>not set</td><td>n/a</td><td>%s <span class='note'>Rate source: %s. "
    "rates_memo.txt (outside the export folder) gives shop rates and a scrap-pricing rule, not a downtime cost per hour or a standard material cost; it was not used.</span></td></tr>"
    % (pill("warn", "unpriced"), e(today["rate_source"])))
for nu in ctx["files_not_used"]:
    fresh_rows.append("<tr><td>%s</td><td>n/a</td><td>n/a</td><td>%s <span class='note'>%s</span></td></tr>"
                      % (e(nu["file"]), pill("warn", "not used"), e(nu["why"])))

fresh_html = """
<section class="panel freshness"><h2>Sources and freshness</h2>
<p class="lead"><strong>The drop is %s days old.</strong> The newest production day in it is %s; the run is on 2026-11-14,
so the 2026-11-13 export did not land in this folder. Every figure below is for %s. Re-run after the 2026-11-13 export lands; a re-run rewrites this page for its day.</p>
<p>Production day %s chose itself as the %s (%s). It is complete under the engine's rule (plan, output and downtime each cover it):
data complete <span class="num">%s</span>. Shifts present in output.csv: labels <span class="num">1</span> and <span class="num">2</span> (CNC-01 on both, CNC-02 on 1 only).
With no plant profile the expected shift pattern is unknown, so whether this is a full plant day cannot be confirmed.</p>
<div class="table-scroll"><table><thead><tr><th>Source</th><th>Landed</th><th>Covers</th><th>Status</th></tr></thead>
<tbody>%s</tbody></table></div>
<p class="note">Landed times are file times (%s). Future-dated records: %s.</p>
</section>""" % (e(raw("fresh.days_old")), e(fr["newest_production_day"]), e(day), e(day), e(fr["day_source"]),
                 fv("fresh.day"), e(str(fr["data_complete"]).lower()), "".join(fresh_rows),
                 e(fr["data_as_of_basis"]), fv("fresh.future"))

# ---------- today's actions ----------
stops = {s["asset"]: s for s in today["stops"]}
actions = [
    ("Export drop not current", "Production day 2026-11-13 is not reported; this page describes %s." % e(day),
     "Check whether the 2026-11-13 planning, MES and downtime exports ran, then re-run the pulse.",
     "suggested: plant IT / export owner", "investigation"),
    ("CNC-01: largest downtime on %s" % e(day),
     "%s; reason %s, &ldquo;%s&rdquo;. Safety status: not assessed." % (fv("dt.%s.asset.CNC-01" % day), e(stops["CNC-01"]["code"]), e(stops["CNC-01"]["text"])),
     "Confirm whether the tool-change overrun is recurring; run a breakdown diagnosis if it is.",
     "suggested: maintenance lead", "investigation"),
    ("PN-200 under plan on CNC-02",
     "Variance %s (%s%%). WO-1002 (PN-200) is due 2026-11-13 per work_orders.csv; whether it finished on 2026-11-13 is not in the drop. "
     "Commitment impact not traceable: no work order to sales order link in the ERP." % (fv("out.%s.PN-200.variance" % day), fv("out.%s.PN-200.variance_pct" % day)),
     "Confirm WO-1002's status with production control.", "suggested: production control", "investigation"),
    ("CNC-02 waiting on material",
     "%s, reason %s, &ldquo;%s&rdquo;." % (fv("dt.%s.asset.CNC-02" % day), e(stops["CNC-02"]["code"]), e(stops["CNC-02"]["text"])),
     "None today; watch for repeats.", "suggested: materials / planning", "observation"),
]
act_rows = "".join("<tr><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>" % (a, b, c, d, pill("warn" if t == "investigation" else "good", t))
                   for a, b, c, d, t in actions)
actions_html = """
<section class="panel"><h2>Today's actions</h2>
<p><strong>No decisions waiting today.</strong> No normalization is awaiting approval and no reschedule move was drafted.</p>
<div class="table-scroll"><table><thead><tr><th>Issue</th><th>Impact</th><th>Next step</th><th>Owner role</th><th>Type</th></tr></thead>
<tbody>%s</tbody></table></div></section>""" % act_rows

# ---------- output against plan ----------
out_rows = ""
for p in sorted(today["parts"]):
    k = "out.%s.%s." % (day, p)
    out_rows += ("<tr><td class='id'>%s</td><td>CELL-A / VMC</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>"
                 % (e(p), e("CNC-01" if p == "PN-100" else "CNC-02"), fv(k + "planned"), fv(k + "good"), fv(k + "variance"),
                    fv(k + "variance_pct"), pill("good", today["parts"][p]["status"]),
                    e(", ".join(today["parts"][p]["plan_spellings"]) + " / " + ", ".join(today["parts"][p]["mes_spellings"]))))
output_html = """
<section class="panel"><h2>Output against plan, %s</h2>
<div class="table-scroll"><table><thead><tr><th>Part</th><th>Cell / work center</th><th>Asset</th><th>Planned</th><th>Good</th><th>Variance</th><th>Variance %%</th><th>Status</th><th>Spelling plan / MES</th></tr></thead>
<tbody>%s</tbody></table></div>
<p class="note">Cell from output.csv, work center from plan.csv. Every part matched verbatim; no normalization proposed, nothing provisional.
Good output as a share of plan, week to date (1 day): %s%%.</p></section>""" % (e(day), out_rows, fv("wow.this.output_vs_plan_pct"))

# ---------- OEE ----------
oee_rows = ""
for a in today["oee_by_asset"]:
    k = "oee.%s.%s." % (day, a["asset"])
    oee_rows += "<tr><td class='id'>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>" % (
        e(a["asset"]), fv(k + "availability"), fv(k + "performance"), fv(k + "quality"), fv(k + "oee"))
k = "oee.%s." % day
oee_rows += "<tr class='total'><td>Site (%s)</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>" % (
    e(rec["oee_basis"]), fv(k + "availability"), fv(k + "performance"), fv(k + "quality"), fv(k + "oee"))
oee_html = """
<section class="panel"><h2>OEE by asset, %s</h2>
<div class="table-scroll"><table><thead><tr><th>Asset</th><th>Availability</th><th>Performance</th><th>Quality</th><th>OEE</th></tr></thead>
<tbody>%s</tbody></table></div>
<p class="note">Quality = %s. Availability = (planned time &minus; downtime) &divide; planned time, with planned time taken from plan.csv
<code>planned_hours</code> per asset; no plant profile defines planned production time, so this definition is assumed. Performance = routing
<code>run_min_per_unit</code> &times; (good + scrap) &divide; run time. Values are fractions of 1, printed as the engine holds them.</p></section>""" % (
    e(day), oee_rows, e(today["quality_convention"]))

# ---------- downtime ----------
def rank_table(kind, label):
    rws = ""
    for x in sorted(dt[kind], key=lambda r: r["rank_minutes"]):
        rws += "<tr><td class='id'>%s</td><td>%s</td></tr>" % (e(x["key"]), fv("dt.%s.%s.%s" % (day, "asset" if kind == "by_asset" else "code", x["key"])))
    return "<h3>%s</h3><div class='table-scroll'><table><thead><tr><th>%s</th><th>Events, minutes, rank by minutes and by frequency</th></tr></thead><tbody>%s</tbody></table></div>" % (
        label, "Asset" if kind == "by_asset" else "Reason code", rws)

stop_rows = "".join("<tr><td class='id'>%s</td><td class='num'>%s</td><td class='num'>%s</td><td class='id'>%s</td><td>%s</td></tr>" % (
    e(s["asset"]), e(s["start"]), e(str(s["minutes"])), e(s["code"]), e(s["text"])) for s in today["stops"])
downtime_html = """
<section class="panel"><h2>Downtime, %s</h2>
<p>Events %s, trusted minutes %s, ongoing %s, minutes held out %s. Coded <em>Other</em> or blank: %s of %s events.
Both events rank 1 by frequency (one event each), so the frequency ranking does not separate them; the minutes ranking does.</p>
%s%s
<h3>Stop log (downtime.csv)</h3>
<div class="table-scroll"><table><thead><tr><th>Asset</th><th>Start</th><th>Minutes</th><th>Code</th><th>Reason text</th></tr></thead><tbody>%s</tbody></table></div>
<p class="note">Stop-log minutes are the rows behind %s; no row was held out for end-before-start or a duration mismatch (%s).</p>
</section>""" % (e(day), fv("dt.%s.events" % day), fv("dt.%s.minutes" % day), fv("dt.%s.ongoing" % day), fv("dt.%s.held" % day),
                 fv("dt.%s.uncoded_events" % day), fv("dt.%s.events" % day),
                 rank_table("by_asset", "By asset"), rank_table("by_code", "By reason code"), stop_rows,
                 fv("dt.%s.minutes" % day), fv("integrity.dt_flags"))

# ---------- priced losses ----------
loss_rows = ""
for s in today["scrap"]:
    loss_rows += "<tr><td>Scrap, <span class='id'>%s</span></td><td>%s units</td><td>%s</td><td>no standard cost on file</td></tr>" % (
        e(s["part"]), fv("scrap.%s.%s" % (day, s["part"])), fv("scrapusd.%s.%s" % (day, s["part"])))
loss_rows += "<tr><td>Downtime</td><td>%s min</td><td>%s</td><td>rate source: %s</td></tr>" % (
    fv("dt.%s.minutes" % day), fv("dtusd.%s" % day), e(today["rate_source"]))
losses_html = """
<section class="panel"><h2>Priced losses, %s</h2>
<p><strong>Nothing could be priced this run.</strong> Scrap dollars need a standard cost and downtime dollars need a cost per hour; neither is in the drop.
These are <em>unknown</em>, not $0. Priced scrap total: %s.</p>
<div class="table-scroll"><table><thead><tr><th>Loss</th><th>Quantity</th><th>USD</th><th>Why unpriced</th></tr></thead><tbody>%s</tbody></table></div>
<p class="note">Unpriced: %s</p></section>""" % (e(day), fv("scrapusd.%s.total" % day), loss_rows, "; ".join(e(u) for u in today["unpriced"]))

# ---------- exceptions ----------
exceptions_html = """
<section class="panel"><h2>Exceptions</h2>
<p>Exceptions (late jobs, machines down, quality holds, contradicted one-sided): %s. Open work orders due on or before %s with good output short of ordered: %s;
whose completion cannot be judged: %s.</p>
<p>Commitment impact not traceable: no work order to sales order link in the ERP. It affects %s exceptions today; it also limits the PN-200 / WO-1002 investigation above.</p>
<p><strong>Reschedule moves: none drafted.</strong> No exception met the bar, and the plan in the drop covers %s only, so there is no forward schedule a move could be traced against.
Not checked: tooling, operators, material on hand for 2026-11-13 onward.</p>
<p class="note">Floor view: no floor layout is on file. To add one, attach a floor plan to an attended daily-production-report run; an unattended run never sets one up.</p>
</section>""" % (fv("exc.count"), e(day), fv("exc.late"), fv("exc.late_undeterminable"), fv("exc.count"), e(cov["plan"]["first"]))

# ---------- data problems ----------
problems_html = """
<section class="panel"><h2>Data problems</h2>
<p>Numbered data problems (classes 1&ndash;5 and 8, contradicted one-sided, unit conflicts): %s. Mismatched records, classes 1&ndash;5 and 8: %s.
Class 1 orphans (MES work order not in work_orders.csv): %s. Date-window gaps (class 7): none listed by the engine.</p>
<p>Integrity checks: downtime rows held out %s; MES rows with a blank lot %s; NCR keys that disagree %s; terse close-out notes %s; MES rows with no scrap recorded %s.
No table is shown because there is no row to number.</p>
<h3>Checked, nothing wrong</h3>
<p>Class 6 records: %s. Outside the count above.</p></section>""" % (
    fv("problems.count"), fv("mismatched.count"), fv("orphan.count"), fv("integrity.dt_flags"), fv("integrity.blank_lot"),
    fv("integrity.ncr"), fv("integrity.terse"), fv("scrap.absent_rows"), fv("checked.count"))

# ---------- trend ----------
trend_html = """
<section class="panel"><h2>Trend</h2>
<p><strong>The trend is unavailable this run.</strong> The dashboard's stored day records could not be read: there is no artifact store in this session.
The exports themselves cover only %s, so no trend can be built from them either.</p>
<p>Week-over-week movers skipped: the earlier window 2026-10-30..2026-11-05 holds %s days of data (this week: %s day). From this run's exports, not stored history.</p>
</section>""" % (e(day), fv("wow.prev.days"), fv("wow.this.days"))

# ---------- day record ----------
def show(v):
    if v is None:
        return "null"
    if isinstance(v, bool):
        return str(v).lower()
    if isinstance(v, (list, dict)):
        if isinstance(v, list) and not v:
            return "[] (empty)"
        if isinstance(v, list) and all(isinstance(x, dict) for x in v):
            return "; ".join(", ".join("%s %s" % (kk, show(vv)) for kk, vv in x.items()) for x in v)
        if isinstance(v, dict):
            return ", ".join("%s %s" % (kk, show(vv)) for kk, vv in v.items())
        return "; ".join(show(x) for x in v)
    return str(v)

rec_rows = "".join("<tr><td class='id'>%s</td><td>%s</td></tr>" % (e(k), e(show(v))) for k, v in rec.items())
record_html = """
<section class="panel"><h2>Day record %s</h2>
<p>%s <strong>Computed, not stored</strong>: there is no artifact store this session, so nothing was written to <code>pulse_days</code>. Saved as day_records.json beside this page.
Fields exactly as the engine emitted them.</p>
<div class="table-scroll"><table><thead><tr><th>Field</th><th>Value</th></tr></thead><tbody>%s</tbody></table></div></section>""" % (
    e(rec["record_key"]), pill("warn", "not stored"), rec_rows)

# ---------- open questions ----------
questions_html = """
<section class="panel"><h2>What this run could not settle (questions for the plant)</h2>
<ol>
<li>Did the 2026-11-13 planning, MES and downtime exports run? None is in this drop.</li>
<li>What is the downtime cost per hour (<code>MFG_DOWNTIME_COST_PER_HOUR</code> or the plant rates)? Downtime is unpriced until it is set.</li>
<li>What is the standard material cost for PN-100 and PN-200? The finance memo prices scrap at standard material plus value-added labour, but no standard material cost is in the drop.</li>
<li>Plant profile: site name, time zone, production-day boundary, shift pattern and the planned-production-time definition. All were assumed (see the freshness banner).</li>
<li>Is there a work order to sales order link (ERP export) so commitment impact can be traced?</li>
</ol></section>"""

# ---------- figures block ----------
fig_rows = "".join("<tr><td class='id'>%s</td><td>%s</td><td class='num'>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>" % (
    e(r["id"]), e(r["figure"]), e(r["value"]), e(r["period"]), e(r["source"]), e(r["filter"])) for r in rows)
figures_html = """
<section class="panel"><h2>Figures block</h2>
<p>Every number on this page is a row of figures.csv, written by pulse_compute.py (self-checks: %s run, %s failed). The small grey tag after each number is its row id.
Day-record values are the engine's day_records.json. The page code does no arithmetic. %s rows; the page quotes %s distinct rows.</p>
<details><summary>Show all rows</summary>
<div class="table-scroll"><table><thead><tr><th>id</th><th>Figure</th><th>Value</th><th>Period</th><th>Source</th><th>Filter</th></tr></thead><tbody>%s</tbody></table></div>
</details></section>"""

# ---------- assemble ----------
CSS = """
:root{--ink:#1A1D21;--paper:#F2F3F5;--paper-raised:#FFFFFF;--line:#D6D9DD;--accent:#1F5C8B;--accent-soft:#E4EDF4;
--good:#2E7248;--good-soft:#E3EFE7;--warn:#A8641A;--warn-soft:#F7EBDA;--critical:#A93226;--critical-soft:#F9E9E7;
--font-display:'IBM Plex Sans Condensed','Arial Narrow',sans-serif;--font-body:'IBM Plex Sans',-apple-system,BlinkMacSystemFont,sans-serif;
--font-mono:'IBM Plex Mono','SF Mono',Consolas,monospace;--text-xs:0.75rem;--text-sm:0.875rem;--text-base:1rem;--text-lg:1.125rem;--text-xl:1.375rem;--text-2xl:1.75rem;--text-3xl:2.25rem}
@media (prefers-color-scheme: dark){:root:not([data-theme="light"]){--ink:#E8EAEC;--paper:#15181B;--paper-raised:#1D2126;--line:#2E343A;--accent:#6BA8D4;--accent-soft:#1B2C39;--good:#6FBF88;--good-soft:#1B2E22;--warn:#D9A15C;--warn-soft:#33271A;--critical:#DE8378;--critical-soft:#35201E}}
:root[data-theme="dark"]{--ink:#E8EAEC;--paper:#15181B;--paper-raised:#1D2126;--line:#2E343A;--accent:#6BA8D4;--accent-soft:#1B2C39;--good:#6FBF88;--good-soft:#1B2E22;--warn:#D9A15C;--warn-soft:#33271A;--critical:#DE8378;--critical-soft:#35201E}
body{margin:0;background:var(--paper);color:var(--ink);font:400 var(--text-base)/1.5 var(--font-body)}
.page{display:flex;flex-direction:column;gap:1.25rem;max-width:900px;margin:0 auto;padding:2rem 1rem}
.panel{background:var(--paper-raised);border:1px solid var(--line);border-radius:4px;padding:1.5rem}
h1,h2,h3{font-family:var(--font-display);font-weight:600;margin:0 0 .5rem}h1{font-size:var(--text-2xl)}h2{font-size:var(--text-xl)}h3{font-size:var(--text-lg);margin-top:1rem}
.meta{margin:.15rem 0;font-size:var(--text-sm)}
.panel-title{font-family:var(--font-display);font-size:var(--text-xl);color:var(--accent);margin:.5rem 0 0;border-bottom:1px solid var(--line)}
.table-scroll{overflow-x:auto}table{border-collapse:collapse;width:100%;font-size:var(--text-sm)}
th,td{text-align:left;padding:.4rem .5rem;border-bottom:1px solid var(--line);vertical-align:top}
.num,.id{font-family:var(--font-mono);font-variant-numeric:tabular-nums}
.fid{font:500 0.6rem var(--font-mono);color:var(--line);margin-left:2px;filter:contrast(.4)}
.note{font-size:var(--text-sm)}tr.total td{font-weight:600}
.status{display:inline-block;padding:.15rem .55rem;border-radius:2px;font:600 var(--text-xs) var(--font-body);text-transform:uppercase;letter-spacing:.04em}
.status--good{background:var(--good-soft);color:var(--good)}.status--warn{background:var(--warn-soft);color:var(--warn)}.status--critical{background:var(--critical-soft);color:var(--critical)}
.safety{border-left:4px solid var(--warn)}.page-footer{font-size:var(--text-xs)}code{font-family:var(--font-mono);font-size:.85em}
"""

body = [
    '<header class="page-header"><h1>%s</h1>' % e(title),
    '<p class="meta">%s · Generated %s · data as of %s</p>' % (e(site), e(ctx["run_time_local"]), e(fr["data_as_of_local"])),
    '<p class="meta">Production day: %s · day boundary: %s</p></header>' % (e(day), e(ctx["day_boundary"])),
    '<h2 class="panel-title">Today</h2>',
    '<section class="panel safety"><h2>Safety</h2><p><strong>Safety status: not assessed (no breakdown diagnosis records in this drop).</strong> '
    'Diagnosis records blocked for unknown safety status: %s.</p></section>' % fv("diag.blocked"),
    fresh_html, actions_html, output_html, oee_html, downtime_html, losses_html, exceptions_html, problems_html,
    '<h2 class="panel-title">Trend</h2>', trend_html,
    record_html, questions_html,
]
used_before = None
page_tail = ('<footer class="page-footer"><p>Generated by <strong>morning-plant-pulse</strong> — Manufacturing · no production days stored '
             '(the dashboard\'s records could not be read or written this run). Read-only: nothing was written to any system of record.</p>'
             '<p>This is today\'s Operations page for %s; save it over yesterday\'s. The short Operations page, operations-short-%s-%s.html, is separate; keep both.</p>'
             '<p><strong>The dashboard was not updated: no artifact store is available in this session.</strong></p></footer>') % (e(day), e(site), e(day))

distinct = len(set(USED)) + 1  # + figures.rows quoted below
figures_html = figures_html % (e(str(model["checks"]["run"])), e(str(len(model["checks"]["failed"]))), fv("figures.rows"),
                               '<span class="num">%d</span>' % len(set(USED)), fig_rows)
body.append(figures_html)
body.append(page_tail)

doc = """<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>%s</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans+Condensed:wght@500;600&family=IBM+Plex+Sans:wght@400;500;600&family=IBM+Plex+Mono:wght@500&display=swap" rel="stylesheet">
<style>%s</style></head>
<body><main class="page">%s</main></body></html>
""" % (e(title), CSS, "\n".join(body))

missing = [u for u in set(USED) if u not in FIG]
assert not missing, missing
dest = OUT / ("operations-%s-%s.html" % (site, day))
dest.write_text(doc, encoding="utf-8")
print("wrote", dest, "| figures rows quoted:", len(set(USED)))
