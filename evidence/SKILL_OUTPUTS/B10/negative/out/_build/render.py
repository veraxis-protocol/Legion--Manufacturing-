"""Render the data quality report and the morning report from report_model.json.
Every number is looked up from the figures block; nothing is retyped."""
import json, html, pathlib, datetime

OUT = pathlib.Path(r"C:/LMFG/runs/B10-negative/work/out")
M = json.load(open(OUT / "report_model.json", encoding="utf-8"))
FIG = {f["figure"]: f["value"] for f in M["figures"]}
def F(name):
    if name not in FIG:
        raise KeyError("figure not in block: " + name)
    return FIG[name]
e = html.escape
site = ", ".join(M["site"])
day = M["latest_day"]; dd = datetime.date.fromisoformat(day)
day_label = f"{dd.day} {dd.strftime('%b')}"
exp = M["expected_day"]; ed = datetime.date.fromisoformat(exp); exp_label = f"{ed.day} {ed.strftime('%b')}"
run_at = M["run_at"].replace("T", " ")

CSS = """
:root{--ink:#1A1D21;--paper:#F2F3F5;--paper-raised:#FFFFFF;--line:#D6D9DD;--accent:#1F5C8B;--accent-soft:#E4EDF4;
--good:#2E7248;--good-soft:#E3EFE7;--warn:#A8641A;--warn-soft:#F7EBDA;--critical:#A93226;--critical-soft:#F9E9E7;
--font-display:'IBM Plex Sans Condensed','Arial Narrow',sans-serif;--font-body:'IBM Plex Sans',-apple-system,BlinkMacSystemFont,sans-serif;
--font-mono:'IBM Plex Mono','SF Mono',Consolas,monospace;--text-xs:0.75rem;--text-sm:0.875rem;--text-base:1rem;--text-lg:1.125rem;--text-xl:1.375rem;--text-2xl:1.75rem;--text-3xl:2.25rem}
@media (prefers-color-scheme: dark){:root:not([data-theme="light"]){--ink:#E8EAEC;--paper:#15181B;--paper-raised:#1D2126;--line:#2E343A;--accent:#6BA8D4;--accent-soft:#1B2C39;--good:#6FBF88;--good-soft:#1B2E22;--warn:#D9A15C;--warn-soft:#33271A;--critical:#DE8378;--critical-soft:#35201E}}
:root[data-theme="dark"]{--ink:#E8EAEC;--paper:#15181B;--paper-raised:#1D2126;--line:#2E343A;--accent:#6BA8D4;--accent-soft:#1B2C39;--good:#6FBF88;--good-soft:#1B2E22;--warn:#D9A15C;--warn-soft:#33271A;--critical:#DE8378;--critical-soft:#35201E}
body{margin:0;background:var(--paper);color:var(--ink);font-family:var(--font-body);font-size:var(--text-base);line-height:1.5}
.page{display:flex;flex-direction:column;gap:1.25rem;max-width:900px;margin:0 auto;padding:2rem 1.5rem}
.panel{background:var(--paper-raised);border:1px solid var(--line);border-radius:4px;padding:1.5rem}
h1,h2,h3{font-family:var(--font-display);font-weight:600;margin:0 0 .5rem}
h1{font-size:var(--text-2xl)}h2{font-size:var(--text-xl)}h3{font-size:var(--text-lg)}
.meta{color:var(--ink);opacity:.75;font-size:var(--text-sm);margin:.25rem 0 0}
.table-scroll{overflow-x:auto}
table{border-collapse:collapse;width:100%;font-size:var(--text-sm)}
th,td{text-align:left;padding:.4rem .5rem;border-bottom:1px solid var(--line);vertical-align:top}
td.num,th.num{text-align:right;font-family:var(--font-mono);font-variant-numeric:tabular-nums}
code,.mono{font-family:var(--font-mono)}
.status{display:inline-block;padding:.15rem .55rem;border-radius:2px;font:600 var(--text-xs) var(--font-body);text-transform:uppercase;letter-spacing:.04em}
.status--good{background:var(--good-soft);color:var(--good)}.status--warn{background:var(--warn-soft);color:var(--warn)}.status--critical{background:var(--critical-soft);color:var(--critical)}
.tiles{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:1rem}
.stat-tile{border:1px solid var(--line);border-radius:4px;padding:1rem;background:var(--paper-raised)}
.stat-figure{font-family:var(--font-mono);font-size:var(--text-3xl);font-variant-numeric:tabular-nums;line-height:1.1}
.stat-label{font-weight:600}.stat-context{font-size:var(--text-sm);margin:.25rem 0 0}
.note{font-size:var(--text-sm)}
details>summary{cursor:pointer;font-family:var(--font-display);font-weight:600;font-size:var(--text-xl)}
.page-footer{font-size:var(--text-xs);opacity:.75}
.safety{border-left:4px solid var(--warn)}
.fresh{border-left:4px solid var(--critical)}
"""
HEAD = """<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title}</title><link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans+Condensed:wght@500;600&family=IBM+Plex+Sans:wght@400;500;600&family=IBM+Plex+Mono:wght@500&display=swap" rel="stylesheet">
<style>{css}</style></head><body><main class="page">"""

def table(headers, rows, num=()):
    h = "".join(f'<th class="num">{e(x)}</th>' if i in num else f"<th>{e(x)}</th>" for i, x in enumerate(headers))
    b = ""
    for r in rows:
        b += "<tr>" + "".join(f'<td class="num">{c}</td>' if i in num else f"<td>{c}</td>" for i, c in enumerate(r)) + "</tr>"
    return f'<div class="table-scroll"><table><thead><tr>{h}</tr></thead><tbody>{b}</tbody></table></div>'

def pill(kind, text): return f'<span class="status status--{kind}">{e(text)}</span>'

files = M["files"]
def fm(k): return files[k].replace("T", " ")

# ---------- freshness banner (shared) ----------
src_rows = [
    ["Production output, production day " + e(exp), "-", "-", pill("critical", "did not land")],
    ["Downtime events (MES / historian)", "-", "-", pill("critical", "not in the drop")],
    ["Maintenance work orders (CMMS or export)", "-", "-", pill("critical", "not in the drop: open maintenance not visible")],
    ["Item master / standard cost (ERP)", "-", "-", pill("critical", "not in the drop: scrap unpriced")],
    ["Inspection, NCRs, inventory, sales orders", "-", "-", pill("warn", "not in the drop")],
    ["<code>pulse_oee/output.csv</code> (production output, export)", e(fm("pulse_oee/output.csv")), e(F("Production days in output export")), pill("warn", f"covers {day} only")],
    ["<code>pulse_oee/plan.csv</code> (plan, export)", e(fm("pulse_oee/plan.csv")), e(F("Plan dates in plan export")), pill("warn", f"covers {day} only")],
    ["<code>pulse_oee/work_orders.csv</code> (production work orders, export)", e(fm("pulse_oee/work_orders.csv")), "no date column; due dates 13 to 15 Nov", pill("warn", "as-of unknown")],
    ["<code>pulse_oee/routing.csv</code> (run standards, export)", e(fm("pulse_oee/routing.csv")), "no revision, no effective date", pill("warn", "revision unknown")],
]
fresh_html = f"""<section class="panel fresh"><h2>Data freshness</h2>
<p><strong>Last night's export for production day {e(exp)} did not land.</strong> The newest production day in the folder is {e(F('Latest production day present'))};
this report covers {e(day)} only, run on {e(F('Run date'))}. Nothing from {e(exp)} has been reused or assumed. No plant profile is on file, so the day reported is the latest
complete production day present in the exports, and the day boundary is the calendar day.</p>
<p>Shifts in the day: CNC-01 shifts {e(F('Shifts with output rows, CNC-01'))}; CNC-02 shift {e(F('Shifts with output rows, CNC-02'))}. The plant's shift pattern is not on file,
so whether this is a complete plant day cannot be confirmed. Every source is export-sourced; nothing is live, maintenance included.</p>
{table(['Source','File modified','Covers','Status'], src_rows)}
<p class="note">No source carries a timestamp later than the run ({e(str(F('Files with a modified time later than the run')))} files, {e(str(F('Activity rows dated after the run date')))} activity rows). The exports carry dates only, no time or zone.</p>
</section>"""

# ---------- data quality report ----------
id_rows = [[f"<code>{e(i['file'])}</code>", e(i["identified_as"]), e(i["tab"] or "not loaded")] for i in M["identified"]]
dq_fig_rows = [[e(f["figure"]), e(str(f["value"])), e(f["computed_from"]), f"<code>{e(f['filter'])}</code>"] for f in M["figures"]]
dq = HEAD.format(title="SITE-1 Data Quality", css=CSS) + f"""
<header><h1>{e(site)}: data quality report, {e(day_label)}</h1><p class="meta">Generated {e(run_at)} · data as of production day {e(day)} (date only) · data-consolidate, file-only run</p></header>
<section class="panel"><p><strong>No normalizations are waiting for approval.</strong> Every key matched as written. The real next action is getting the {e(exp)} production export and a downtime export into the drop, then re-running.</p></section>
{fresh_html}
<section class="panel"><h2>Files identified</h2>{table(['File','Identified as','Dataset tab'], id_rows)}</section>
<section class="panel"><h2>Rows in, rows joined</h2><div class="tiles">
<div class="stat-tile"><div class="stat-figure">{F('Output rows whose work order matches work_orders.csv exactly')} / {F('Output rows')}</div><div class="stat-label">Output rows joined to a work order</div><p class="stat-context">All matched exactly; part agrees with the work order on {F("Output rows whose part equals the work order's part")}.</p></div>
<div class="stat-tile"><div class="stat-figure">{F('Plan parts matching an output part exactly')} / {F('Plan rows')}</div><div class="stat-label">Plan rows joined to output</div><p class="stat-context">Assets agree on {F('Plan assets matching an output asset exactly')} of them.</p></div>
<div class="stat-tile"><div class="stat-figure">{F('Normalizations fired')}</div><div class="stat-label">Normalizations applied or proposed</div><p class="stat-context">Ladder rungs 1 to 5 not needed.</p></div></div>
<p class="note">Example row: <code>pulse_oee/output.csv:2</code> WO-1001, PN-100, CNC-01, shift 1, 480 good, 12 scrap, matched to <code>work_orders.csv:2</code> WO-1001, PN-100, 500 ordered, due 2026-11-14.</p></section>
<section class="panel"><h2>Mismatches by class</h2>
<p>{pill('good','none fired')} Date window (class 7): {F('Output rows outside plan window (class 7)')} output rows outside the plan's window. Duplicate key (class 8): {F('Duplicate keys at production_output grain (WO, shift, day)')} at the work order, shift and day grain (WO-1001 and WO-1003 both run PN-100 on CNC-01, on different work orders and shifts). Orphans (class 1): none. One-sided records (class 6): {F('Work orders with no output rows (class 6 candidates)')} work orders with no output, {F('Planned parts with no output (class 6 candidates)')} planned parts with no output.</p>
<p>Format drift, leading zeros, revision suffix, case and whitespace (classes 2 to 5): none fired. The verbatim lookup demonstration is <em>not applicable: every key was spelled the same in every file</em>, so there is no second spelling to search by.</p>
<p>Integrity flags: none raised (no downtime rows to test for end-before-start or duration mismatch; no sales lines; no NCRs; no future timestamps).</p></section>
<section class="panel"><h2>Findings that are not mismatches</h2>
{table(['Finding','What it means for the plant'], [
 ['No unit-of-measure column in output, plan or work orders (' + str(F('Exports carrying a unit-of-measure column')) + ' of 3 carry one)', 'Quantities are reported as each file states them. Same-part rows from one file are added up; nothing is totalled across parts. The plant should confirm what unit the quantity columns count.'],
 ['<code>routing.csv</code> has no setup-time column', 'It does not meet the routing signature, so no <code>routings</code> tab was built (named missing, not empty). Its run standard is still read raw by the morning report as the ideal cycle time, labelled.'],
 ['Routing rows carry no revision (' + str(F('Routing rows carrying a revision')) + ' of 2)', 'Revision unknown, never assumed current.'],
 ['Work orders carry no sales order link (' + str(F('Work orders carrying a sales order link')) + ' of 3)', 'Commitment impact of a late work order cannot be traced to a customer order.'],
 ['No site on plan or work orders', 'Site SITE-1 is taken from the output export only.'],
 ['Rows carry a date only, no time or zone', 'Usable for counting; not for correlating across sources or for cross-midnight attribution.'],
 ['Work centre VMC has no cell map', 'No Plant context; the cell comes only from the output file (CELL-A).'],
])}</section>
<section class="panel"><h2>Tabs built and tabs missing</h2>
<p>Built (CSV, one file per tab, in <code>out/dataset/</code>): <code>production_output</code>, <code>plan</code>, <code>production_work_orders</code>. No XLSX writer is available in this session, so the workbook was written as one CSV per tab; the shape is the contract's.</p>
<p>Missing, not empty: <code>parts</code> (no item master, so no standard cost), <code>sales_orders</code>, <code>lots</code>, <code>assets</code>, <code>inventory</code>, <code>purchase_orders</code>, <code>downtime_events</code>, <code>inspection_results</code>, <code>maintenance_work_orders</code>, <code>ncrs</code>, <code>routings</code> (see above), <code>operation_actuals</code>.</p></section>
<section class="panel"><h2>Figures block</h2>{table(['Figure','Value','Computed from','Filter or query'], dq_fig_rows)}</section>
<footer class="page-footer">Generated by <strong>data-consolidate</strong>, Manufacturing · SYNTHETIC test data</footer></main></body></html>"""
(OUT / "data-quality-report.html").write_text(dq, encoding="utf-8")

# ---------- morning report ----------
oap = M["output_vs_plan"]; oee = M["oee"]; wos = {w["wo"]: w for w in M["work_orders"]}
def sgn(v): return f"{v:+d}" if isinstance(v, int) else f"{v:+.1f}"
oap_rows = [[e(r["part"]), e(r["asset"]), e(", ".join(r["cell"])), e(r["work_center"]), str(F(f"Planned qty {r['part']}")), str(F(f"Good qty {r['part']}")),
             str(F(f"Scrap qty {r['part']}")), str(F(f"Total qty (good+scrap) {r['part']}")), sgn(F(f"Good vs plan {r['part']}")), sgn(F(f"Good vs plan % {r['part']}")) + "%"] for r in oap]
oee_rows = [[e(o["asset"]), e(o["work_center"]), str(F(f"Planned hours {o['asset']}")), "not computable", "not computable",
             f"{F('Quality % ' + o['asset'])}%", f"{F('Availability x performance combined % ' + o['asset'])}%", "not reported"] for o in oee]
w1, w2, w3 = wos["WO-1001"], wos["WO-1002"], wos["WO-1003"]
actions = [
 ["Investigation", f"Production export for {e(exp)} not in the folder", "This report covers 12 Nov only; 13 Nov output, scrap and progress on WO-1001 and WO-1002 are unseen", f"Check the scheduled export job for {e(exp)}, then re-run this report", "suggested: production systems owner"],
 ["Investigation", "No downtime export in the drop", "Availability, performance, composite OEE, both downtime rankings and downtime dollars are unavailable", "Add the MES or historian stoppage export to the drop", "suggested: MES administrator"],
 ["Investigation", f"WO-1002 (PN-200) due {e(w2['due'])}: {F('Good recorded vs ordered WO-1002')} good recorded through 12 Nov, {F('Short vs order WO-1002')} short, still {e(w2['status'])}", "Possibly past due. Commitment impact not traceable: no work order to sales order link", "Confirm 13 Nov output on CNC-02 before the meeting", "suggested: production scheduler"],
 ["Investigation", f"WO-1001 (PN-100) due today, {e(w1['due'])}: {F('Good recorded vs ordered WO-1001')} good recorded through 12 Nov, {F('Short vs order WO-1001')} short", "Due today. Commitment impact not traceable: no work order to sales order link", "Confirm 13 Nov output on CNC-01", "suggested: production scheduler"],
 ["Observation", f"WO-1003 (PN-100): {F('Good recorded vs ordered WO-1003')} good recorded, still {e(w3['status'])}, due {e(w3['due'])}", "None today; may be ready to close", "Check whether it is waiting on inspection or close-out", "suggested: production supervisor"],
 ["Observation", "Scrap and downtime cannot be priced", "Losses are shown in units only", "Add an item master or standard-cost export; record a downtime cost per hour through onboarding", "suggested: cost accountant"],
]
detail_fig_rows = [[e(f["figure"]), e(str(f["value"])), e(f["computed_from"]), f"<code>{e(f['filter'])}</code>"] for f in M["figures"]]
qual_line = "quality = good ÷ (good + scrap); no rework column, so first-pass yield could not be applied." if not M["rework_col"] else "quality = good ÷ (good + scrap + rework), first-pass yield."

mr = HEAD.format(title=f"{site} Morning Report {day_label}", css=CSS) + f"""
<header><h1>{e(site)}: morning report, {e(day_label)}</h1><p class="meta">Generated {e(run_at)} · data as of production day {e(day)} (date only; no export time in the files)</p></header>
<section class="panel safety"><h2>Safety</h2><p><strong>Safety status: not assessed (no breakdown diagnosis records in this drop).</strong> No maintenance or quality export was in the drop either, so open maintenance and quality holds are not visible, not clear.</p></section>
{fresh_html}
<section class="panel"><h2>Headline, production day {e(day)}</h2><div class="tiles">
<div class="stat-tile"><div class="stat-figure">{F('Good qty PN-100')} / {F('Planned qty PN-100')}</div><div class="stat-label">PN-100 good vs plan (CNC-01)</div><p class="stat-context">{sgn(F('Good vs plan PN-100'))} ({sgn(F('Good vs plan % PN-100'))}%). Total {F('Total qty (good+scrap) PN-100')} with scrap. Unit not stated in the exports.</p></div>
<div class="stat-tile"><div class="stat-figure">{F('Good qty PN-200')} / {F('Planned qty PN-200')}</div><div class="stat-label">PN-200 good vs plan (CNC-02)</div><p class="stat-context">{sgn(F('Good vs plan PN-200'))} ({sgn(F('Good vs plan % PN-200'))}%). Total {F('Total qty (good+scrap) PN-200')} with scrap.</p></div>
<div class="stat-tile"><div class="stat-figure">n/a</div><div class="stat-label">OEE</div><p class="stat-context">Not computed: no downtime export, so availability and performance cannot be separated. Quality CNC-01 {F('Quality % CNC-01')}%, CNC-02 {F('Quality % CNC-02')}%.</p></div>
<div class="stat-tile"><div class="stat-figure">unknown</div><div class="stat-label">Downtime minutes</div><p class="stat-context">No downtime export. Not zero.</p></div>
<div class="stat-tile"><div class="stat-figure">unpriced</div><div class="stat-label">Scrap at standard cost</div><p class="stat-context">PN-100 {F('Scrap units PN-100 (for pricing table)')}, PN-200 {F('Scrap units PN-200 (for pricing table)')} units; no standard cost in the drop.</p></div>
</div></section>
<section class="panel"><h2>Today's actions</h2>
<p><strong>No decisions waiting today.</strong> No normalization is pending and no reschedule move could be drafted (reason below). The rows are investigations and observations.</p>
{table(['Type','Issue','Impact','Next step','Owner role'], actions)}</section>
<section class="panel"><h2>Floor view</h2><p>No floor layout is on file. Attach a floor plan (PDF or image) to set one up.</p></section>
<section class="panel"><details open><summary>Output against plan</summary>
{table(['Part','Asset','Cell','Work centre','Planned','Good','Scrap','Total','Good vs plan','%'], oap_rows, num=(4,5,6,7,8,9))}
<p class="note">Grain: by part and asset, which is the plan's grain (the plan holds no work order). Every key matched as written; nothing here is provisional. No unit-of-measure column in either file: quantities are compared as stated. Line: none named in the data; the cell comes from the output export, and "work centre" from the plan. Plan comparison for {e(exp)} unavailable: no export.</p>
</details></section>
<section class="panel"><details open><summary>OEE by asset</summary>
{table(['Asset','Work centre','Planned h','Availability','Performance','Quality','A × P combined','Composite OEE'], oee_rows, num=(2,3,4,5,6,7))}
<p class="note">{e(qual_line)}</p>
<p class="note">Availability needs run time, and run time needs the downtime export, which is not in the drop. Performance needs run time too. Neither is assumed to be 100%, and composite OEE is not reported, because the components are what tell the meeting whether this is a maintenance or a speed problem. <em>A × P combined</em> is ideal minutes of every part made (good + scrap × routing run standard) ÷ planned minutes: CNC-01 {F('Ideal minutes of parts made CNC-01')} of {int(F('Planned hours CNC-01')*60)} min, CNC-02 {F('Ideal minutes of parts made CNC-02')} of {int(F('Planned hours CNC-02')*60)} min. It cannot be split into its two parts.</p>
<p class="note">Planned production time is the plan export's <code>planned_hours</code>; the plant's definition (what is excluded for breaks, PM, changeover) is not on file. Ideal cycle time is <code>routing.csv</code> <code>run_min_per_unit</code>, revision unknown. Grain: per asset.</p>
</details></section>
<section class="panel"><details open><summary>Downtime log</summary>
<p><strong>No downtime export was in the drop, so both rankings (by minutes and by frequency) are unavailable.</strong> This is not a day with no downtime: stoppages were not measured in anything this report could read. Reason-code coverage cannot be stated. No breakdown diagnosis records to fold in ({F('Breakdown diagnosis records in drop')}). Maintenance work orders in progress: not visible, no CMMS connector and no maintenance export.</p>
</details></section>
<section class="panel"><details open><summary>Priced losses</summary>
{table(['Loss','Quantity','Dollars','Basis'], [
 ['Scrap PN-100 (WO-1001, CNC-01)', str(F('Scrap units PN-100 (for pricing table)')), 'unpriced', 'no standard cost in the drop'],
 ['Scrap PN-200 (WO-1002, CNC-02)', str(F('Scrap units PN-200 (for pricing table)')), 'unpriced', 'no standard cost in the drop'],
 ['Downtime', 'unknown', 'unknown', 'no downtime export; downtime cost per hour not set'],
], num=(1,))}
<p class="note">Scrap would be an estimate at standard cost; there is no item master or standard-cost export in the drop, so no figure is printed. Downtime rate: <code>MFG_DOWNTIME_COST_PER_HOUR</code> is not set and no plant rates file exists, so downtime is unpriced. <code>rates_memo.txt</code>, a finance memo, was read: it gives shop rates for four named work centres (none is VMC), a scrap-costing basis of standard material plus value-added labour, and no downtime cost per hour and no standard material cost. It is not a confirmed plant rate, so it prices nothing here; its values are not restated. To record rates, say "update our labour rate" (onboarding) or set the environment variable.</p>
</details></section>
<section class="panel"><details open><summary>Exceptions</summary>
{table(['Exception','Detail','Commitment impact'], [
 ['Late or at risk', f"WO-1002, PN-200, due {e(w2['due'])}: {F('Good recorded vs ordered WO-1002')} good, {F('Short vs order WO-1002')} short as of 12 Nov. PN-200 ran {F('Good vs plan PN-200')} ({F('Good vs plan % PN-200')}%) against plan on 12 Nov.", 'not traceable: no work order to sales order link in the export'],
 ['Late or at risk', f"WO-1001, PN-100, due {e(w1['due'])}: {F('Good recorded vs ordered WO-1001')} good, {F('Short vs order WO-1001')} short as of 12 Nov.", 'not traceable: no work order to sales order link in the export'],
 ['Machines down', 'Not visible: no downtime or maintenance export.', '-'],
 ['Material shortages', 'Not visible: no inventory or purchase-order export.', '-'],
 ['Quality holds', 'Not visible: no inspection or NCR export.', '-'],
])}
<p class="note">Commitment impact not traceable: no work order to sales order link in the export ({F('Work orders whose commitment impact is not traceable')} work orders affected).</p>
<h3>Checked, nothing wrong</h3><p>No one-sided records: {F('Work orders with no output rows (class 6 candidates)')} work orders without output, {F('Planned parts with no output (class 6 candidates)')} planned parts without output, {F('Produced parts not on the plan')} produced parts off-plan.</p>
</details></section>
<section class="panel"><details open><summary>Reschedule proposals</summary>
<p><strong>No move proposed for WO-1002 or WO-1001.</strong> The plan export covers {e(day)} only, so there is no schedule for today to move a job within, and there is no changeover data. Whether either job is still short after 13 Nov is also unknown. Drafting a move on this would be a guess, so the exceptions above carry their impact without one.</p>
</details></section>
<section class="panel"><details><summary>Sources, methods and assumptions</summary>
<ul class="note">
<li>Primary input: the consolidated dataset from data-consolidate (CSV tabs in <code>out/dataset/</code>, data quality report <code>out/data-quality-report.html</code>). Raw exports read alongside it; the two agree on every count.</li>
<li>No plant profile on file: no vocabulary, shift pattern, day boundary, planned-time definition, OEE thresholds or approved normalizations. Canonical terms used.</li>
<li>Week-over-week movers omitted: the exports hold one production day and there is no stored history.</li>
<li>Read-only: nothing was written to any system of record; nothing was posted or sent.</li>
</ul>
<h3>Questions for the plant (recorded, not asked)</h3>
<ul class="note">
<li>Should the {e(exp)} production export have landed, and where is it?</li>
<li>Which file carries downtime events with reason codes, and can it join the drop?</li>
<li>What is the plant's definition of planned production time, and its shift pattern and production-day boundary?</li>
<li>What unit do the quantity columns count?</li>
<li>Is <code>run_min_per_unit</code> the current standard, and for which revision of PN-100 and PN-200?</li>
<li>Where does standard cost come from (ERP item master export)?</li>
<li>What downtime cost per hour should the plant record, and who confirms it? Should the finance memo's rates be recorded through onboarding, and which of its work centres is VMC?</li>
<li>Which of these items are your plant's parts? (Only PN-100 and PN-200 appear; no ERP scope is set.)</li>
<li>Can WO-1002 and WO-1001 be linked to their sales orders?</li>
</ul>
<h3>Figures block</h3>{table(['Figure','Value','Computed from','Filter or query'], detail_fig_rows)}
</details></section>
<footer class="page-footer">Generated by <strong>daily-production-report</strong>, Manufacturing · SYNTHETIC test data · Here is the morning report for {e(day_label)}; save it over yesterday's.</footer>
</main></body></html>"""
(OUT / "report-output" / "morning-report.html").write_text(mr, encoding="utf-8")
print("ok")
