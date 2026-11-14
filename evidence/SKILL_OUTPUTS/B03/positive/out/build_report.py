"""Render the data quality report (house artifact style) from build_dataset.py outputs.
Every number printed is read from figures_block.csv / the logs, never retyped."""
import csv, json, html

OUT = r"C:/LMFG/runs/B03-positive/work/out"
F = {r["figure"]: r["value"] for r in csv.DictReader(open(f"{OUT}/figures_block.csv", encoding="utf-8"))}
FR = list(csv.DictReader(open(f"{OUT}/figures_block.csv", encoding="utf-8")))
LOG = list(csv.DictReader(open(f"{OUT}/key_mismatch_log.csv", encoding="utf-8")))
MISSING = list(csv.DictReader(open(f"{OUT}/dataset/_tabs_missing.csv", encoding="utf-8")))
facts = json.load(open(f"{OUT}/_run_facts.json"))
def tab(name): return list(csv.DictReader(open(f"{OUT}/dataset/{name}.csv", encoding="utf-8")))
e = html.escape

def table(headers, rows, numcols=()):
    h = "".join(f"<th>{e(x)}</th>" for x in headers)
    b = "".join("<tr>" + "".join(
        f'<td class="{"num" if i in numcols else ""}">{c if str(c).startswith("<") else e(str(c))}</td>'
        for i, c in enumerate(r)) + "</tr>" for r in rows)
    return f'<div class="table-scroll"><table><thead><tr>{h}</tr></thead><tbody>{b}</tbody></table></div>'

def pill(kind, text): return f'<span class="status status--{kind}">{e(text)}</span>'

po, dt, pl, assets, pwo = tab("production_output"), tab("downtime_events"), tab("plan"), tab("assets"), tab("production_work_orders")

# ---- freshness ----
mt = facts["mtimes"]; win = facts["windows"]
fresh_rows = [
    ["Equipment list (equipment.csv)", mt["equipment.csv"], "No dates in file (reference list)", pill("warn", "Undated")],
    ["Production output (MES export, output.csv)", mt["pulse_oee/output.csv"], " to ".join(win["output.csv"]), pill("good", "In window")],
    ["Downtime (MES export, downtime.csv)", mt["pulse_oee/downtime.csv"], " to ".join(win["downtime.csv"]), pill("good", "In window")],
    ["Plan (planning export, plan.csv)", mt["pulse_oee/plan.csv"], " to ".join(win["plan.csv"]), pill("good", "In window")],
    ["Production work orders (work_orders.csv, ERP not named)", mt["pulse_oee/work_orders.csv"], "Open commitments (status RELEASED); kept by status", pill("good", "Kept by status")],
    ["Routing (routing.csv)", mt["pulse_oee/routing.csv"], "Not loaded", pill("critical", "Set aside: unrecognized")],
    ["ERP item master, sales orders, inventory, POs", "-", "-", pill("critical", "Not available")],
    ["CMMS maintenance work orders", "-", "-", pill("critical", "Not available")],
    ["Quality / inspection / NCR / lots", "-", "-", pill("critical", "Not available")],
]
# sort critical first
order = {"critical": 0, "warn": 1, "good": 2}
fresh_rows.sort(key=lambda r: order[r[3].split("status--")[1].split('"')[0]])

ident = [[e(a), e(b), e(c or "-"), e(d or "")] for a, b, c, d in facts["identified"]]

per_entity = [[t, F[f"Rows in, {t}"], F[f"Rows fully joined, {t}"]] for t in
              ["production_work_orders", "production_output", "downtime_events", "plan", "assets"]]

orph = [m for m in LOG if m["mismatch_class"] == "1"]
orph_ex = []
for r in po:
    if r["mismatch_class"] == "1": orph_ex.append([r["source_ref"], "production output", r["asset_id_verbatim"], f'{r["production_wo_verbatim"]} / {r["part_number_verbatim"]}, {r["qty_good"]} good, {r["qty_scrap"]} scrap, shift {r["shift"]}, {r["production_day"]}'])
for r in dt:
    if r["mismatch_class"] == "1": orph_ex.append([r["source_ref"], "downtime", r["asset_id_verbatim"], f'{r["started_at"]} to {r["ended_at"]}, {r["duration_minutes"]} min, {r["reason_code"]} {r["reason_text"]}'])
for r in pl:
    if r["mismatch_class"] == "1": orph_ex.append([r["source_ref"], "plan", r["asset_id_verbatim"], f'{r["part_number_verbatim"]} {r["qty"]} planned, {r["planned_hours"]} h, work center {r["work_center_verbatim"]}, {r["plan_date"]}'])
one_sided = [[r["source_ref"], r["asset_id_verbatim"], r["location"]] for r in assets if r["mismatch_class"] == "6"]

zero_classes = [("Format drift", 2), ("Leading-zero loss", 3), ("Revision suffix mismatch", 4),
                ("Case and whitespace", 5), ("Date-window mismatch", 7), ("Duplicate key", 8)]

flag_rows = [[fl, F[f"Rows flagged {fl}"]] for fl in ["sign_convention", "mixed_sign", "end_before_start", "duration_mismatch",
             "ncr_part_differs", "ncr_dated_before_wo", "future_timestamp", "units_conflict"]]
dur = [[a, b, f"{c:g}"] for a, b, c in facts["dur_checks"]]

questions = [
    "Asset numbering: the MES and planning exports call the machines <code>CNC-01</code> and <code>CNC-02</code>; the equipment list uses <code>HMC-01</code>, <code>VMC-02</code>, <code>VMC-03</code>, <code>LTH-01</code>, <code>DEB-01</code>. Which list is authoritative for asset ID, and which equipment-list asset is each of CNC-01 and CNC-02? (Not guessed: no ladder rung links them.)",
    "Work center vocabulary: plan.csv and routing.csv say <code>VMC</code>; the equipment list says <code>MILL-V</code>, <code>MILL-H</code>, <code>TURN</code>, <code>INSP</code>. Are these the same work centers under two names? A machine-class to work-center to cell map belongs in the plant profile.",
    "Routing: routing.csv has no setup-time column and no revision. Is setup zero for these operations, or is there a fuller routing export? Which revision is it written for?",
    "Site: only output.csv names a site (<code>SITE-1</code>). Do the equipment list, plan, downtime and work-order exports belong to SITE-1?",
    "Units of measure: no file states a UOM for quantities. What unit are qty_good, qty_scrap, planned_qty and qty_ordered in?",
    "Time zone: no file carries a zone and there is no plant profile. Which zone are the plant clocks in?",
    "Work-order source: which ERP does work_orders.csv come from, and is there an item master (parts list) export to anchor part numbers?",
    "No plant profile exists (onboarding has not been run). The canonical names <em>production work order</em>, <em>asset</em> and <em>cell</em> are used here rather than the plant's own words. Run onboarding so the next run reads the folder, vocabulary and machine map instead of asking.",
]

fig_rows = [[r["figure"], r["value"], r["computed_from"], r["filter"]] for r in FR]
lookup = [m for m in LOG if m["status"] == "matched"][:2]

page = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Data Quality Report</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans+Condensed:wght@500;600&family=IBM+Plex+Sans:wght@400;500;600&family=IBM+Plex+Mono:wght@500&display=swap" rel="stylesheet">
<style>
:root{{--ink:#1A1D21;--paper:#F2F3F5;--paper-raised:#FFFFFF;--line:#D6D9DD;--accent:#1F5C8B;--accent-soft:#E4EDF4;
--good:#2E7248;--good-soft:#E3EFE7;--warn:#A8641A;--warn-soft:#F7EBDA;--critical:#A93226;--critical-soft:#F9E9E7;
--font-display:'IBM Plex Sans Condensed','Arial Narrow',sans-serif;--font-body:'IBM Plex Sans',-apple-system,BlinkMacSystemFont,sans-serif;
--font-mono:'IBM Plex Mono','SF Mono',Consolas,monospace;--text-xs:.75rem;--text-sm:.875rem;--text-base:1rem;--text-lg:1.125rem;--text-xl:1.375rem;--text-2xl:1.75rem;--text-3xl:2.25rem}}
@media (prefers-color-scheme: dark){{:root:not([data-theme="light"]){{--ink:#E8EAEC;--paper:#15181B;--paper-raised:#1D2126;--line:#2E343A;--accent:#6BA8D4;--accent-soft:#1B2C39;--good:#6FBF88;--good-soft:#1B2E22;--warn:#D9A15C;--warn-soft:#33271A;--critical:#DE8378;--critical-soft:#35201E}}}}
:root[data-theme="dark"]{{--ink:#E8EAEC;--paper:#15181B;--paper-raised:#1D2126;--line:#2E343A;--accent:#6BA8D4;--accent-soft:#1B2C39;--good:#6FBF88;--good-soft:#1B2E22;--warn:#D9A15C;--warn-soft:#33271A;--critical:#DE8378;--critical-soft:#35201E}}
body{{margin:0;background:var(--paper);color:var(--ink);font:400 var(--text-base)/1.5 var(--font-body)}}
.page{{display:flex;flex-direction:column;gap:1.25rem;max-width:900px;margin:0 auto;padding:2rem 1rem}}
.panel{{background:var(--paper-raised);border:1px solid var(--line);border-radius:4px;padding:1.5rem}}
h1,h2,h3{{font-family:var(--font-display);font-weight:600;margin:0 0 .6rem}} h1{{font-size:var(--text-3xl)}} h2{{font-size:var(--text-xl)}} h3{{font-size:var(--text-lg)}}
.meta{{color:var(--ink);opacity:.75;font-size:var(--text-sm);margin:.2rem 0 0}}
.table-scroll{{overflow-x:auto}} table{{border-collapse:collapse;width:100%;font-size:var(--text-sm)}}
th,td{{text-align:left;padding:.4rem .5rem;border-bottom:1px solid var(--line);vertical-align:top}}
td.num,code{{font-family:var(--font-mono);font-variant-numeric:tabular-nums}} td.num{{text-align:right}}
.status{{display:inline-block;padding:.15rem .55rem;border-radius:2px;font:600 var(--text-xs) var(--font-body);text-transform:uppercase;letter-spacing:.04em}}
.status--good{{background:var(--good-soft);color:var(--good)}} .status--warn{{background:var(--warn-soft);color:var(--warn)}} .status--critical{{background:var(--critical-soft);color:var(--critical)}}
.tiles{{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:1rem}}
.stat-figure{{font:500 var(--text-3xl) var(--font-mono);font-variant-numeric:tabular-nums}} .stat-label{{font-weight:600}} .stat-context{{font-size:var(--text-sm);margin:.3rem 0 0}}
.decision{{border-left:4px solid var(--accent)}} .proposal{{border-left:4px solid var(--warn)}}
.page-footer{{font-size:var(--text-xs);opacity:.7;text-align:center}} li{{margin:.3rem 0}}
</style></head>
<body><main class="page">
<header class="page-header"><div><h1>Data Quality Report</h1>
<p class="meta">Site not confirmed (only output.csv names <code>SITE-1</code>) &middot; Generated {facts["run"].replace("T"," ")} (local clock, zone not set) &middot; Synthetic test data, fictitious plant</p></div></header>

<div class="panel decision"><h2>Decision required</h2>
<p><strong>No normalization is awaiting approval.</strong> No ladder rung fired on any key, so there is nothing to approve or reject.</p>
<p><strong>Next action:</strong> tell us which equipment-list asset is <code>CNC-01</code> and which is <code>CNC-02</code> (or send the asset list the MES uses). Until then, {F["Output rows with orphan asset"]} output rows, {F["Downtime rows with orphan asset"]} downtime events ({F["Downtime minutes on orphan assets"]} minutes) and {F["Plan rows with orphan asset"]} plan rows cannot be tied to a machine on the equipment list. This is a question, not a formatting fix, so no yes can apply it.</p></div>

<div class="panel freshness"><h2>Sources</h2>
<p>All sources are file exports; no ERP or CMMS connector was used. "Last refreshed" is the file's modified time on disk (the exports carry no export timestamp). Maintenance data: none was supplied; the equipment list is an undated reference list, not live CMMS.</p>
{table(["Source","Last refreshed","Covers","Status"], fresh_rows, (1,))}
<p>Activity window: every activity file covers {F["Activity overlap window start"]} to {F["Activity overlap window end"]}; the overlap is complete, so no window narrowing was needed and <strong>no row is a date-window mismatch</strong>. No source timestamp is later than the run time. Tab scoping: <code>production_output</code>, <code>downtime_events</code>, <code>plan</code> as activity; <code>production_work_orders</code> as open commitments (kept by status); <code>assets</code> as reference.</p>
<h3>What each file was identified as</h3>
{table(["File","Identified as","Tab","Note"], ident)}
</div>

<div class="tiles">
<div class="panel stat-tile"><div class="stat-figure">{F["Rows fully joined, all tabs"]} / {F["Rows in, all loaded files"]}</div><div class="stat-label">Rows fully joined</div><p class="stat-context">Only the {F["Rows in, production_work_orders"]} work orders join on every key. Every output, downtime and plan row fails on asset.</p></div>
<div class="panel stat-tile"><div class="stat-figure">{F["Key checks matched exactly"]} / {F["Key checks run (non-asset-list rows)"]}</div><div class="stat-label">Key checks matched</div><p class="stat-context">All part and work-order keys match exactly; all {F["Key checks unmatched"]} failures are asset IDs.</p></div>
<div class="panel stat-tile"><div class="stat-figure">{F["Of those, on the equipment list"]} / {F["Asset IDs used in output/downtime/plan"]}</div><div class="stat-label">Asset IDs found on equipment list</div><p class="stat-context">Zero overlap: the two asset lists look like two numbering schemes.</p></div>
</div>

<div class="panel"><h2>Rows in versus rows joined, per entity</h2>
{table(["Tab","Rows in","Fully joined"], per_entity, (1,2))}
<p>"Fully joined" means every key on the row matched. Part and production work order matched on all output and plan rows; the asset key is what holds them back.</p></div>

<div class="panel"><h2>Mismatches by class</h2>
<p>Checked in order: date window first (nothing outside the window), then key shape (nothing), then one-sided records.</p>

<h3>Orphan record (class 1) {pill("critical","Question, no automatic fix")}</h3>
<p><strong>{F["Records in class 1"]} rows</strong> reference asset IDs <code>CNC-01</code> and <code>CNC-02</code>, which are on no row of the equipment list under any ladder rung (trim, case, punctuation, leading zeros, revision). Would join if a fix were applied: none automatically; all {F["Records in class 1"]} would join once the plant supplies a crosswalk to the equipment list.</p>
{table(["Source row","Record","Asset ID as printed","Detail"], orph_ex)}
<p><strong>Which explanation fits:</strong> not a date gap (all files cover the same day) and not a deleted record (both IDs recur across three files). The evidence points to the MES/planning system and the equipment list using different machine identifiers. It is not guessed which equipment asset is which: plan and routing say work center <code>VMC</code>, and the equipment list has two vertical machining centres (<code>VMC-02</code>, <code>VMC-03</code>, work center <code>MILL-V</code>), so even the work center does not settle it.</p>
<p><strong>What it means for the plant:</strong> OEE, downtime and output cannot be reported per machine against the equipment list (cell, install year) until the IDs are reconciled.</p>

<h3>Genuine one-sided record (class 6) {pill("good","Report, do not alarm")}</h3>
<p><strong>{F["Equipment assets with no activity (class 6)"]} assets</strong> on the equipment list appear in no output, downtime or plan row. No other source (no NCR, inspection or lot export was supplied) records activity on them, so none is marked contradicted. No automatic fix; most likely the same naming split as above, since no equipment asset shows any activity at all.</p>
{table(["Source row","Asset ID","Location (cell)"], one_sided)}
<p><strong>What it means:</strong> nothing is wrong with these machines; they simply cannot be seen in the production data under these IDs.</p>
<p>Production work orders with no output: {F["Work orders with no output (class 6)"]}. All three released work orders have output on {F["Activity overlap window start"]}.</p>

<h3>Classes that did not fire</h3>
{table(["Class","Records","Status"], [[f"{n} (class {c})", F[f"Records in class {c}"], pill("good","None found")] for n,c in zero_classes], (1,))}
<p>Duplicate key was checked at each tab's grain (output: work order + shift + production day; plan: part + date; work orders; assets): no collisions.</p>
</div>

<div class="panel"><h2>Normalization rules applied</h2>
<p>{F["Normalization rules applied"]}. No rung fired: every matched key matched as printed. Approved-normalization list: none on file (no plant profile).</p>
<h3>Verbatim lookup</h3>
<p>Format-drift, revision-suffix and case-and-whitespace lookups: <strong>not applicable</strong>, because no such second spelling occurs in these inputs. The <code>_verbatim</code> columns still answer a search by the spelling a source prints, for example:</p>
{table(["Search","Finds"], [[f"<code>{e(m['value_verbatim'])}</code> in <code>production_work_orders.production_wo_verbatim</code>" if m["key"]=="production work order" else f"<code>{e(m['value_verbatim'])}</code>", e(m["source_ref"])] for m in lookup] + [["<code>CNC-02</code> in <code>downtime_events.asset_id_verbatim</code>", e(dt[1]["source_ref"])]])}
</div>

<div class="panel"><h2>Routings, actuals and work centers</h2>
<p><strong>Routing tab: named missing.</strong> routing.csv carries part, operation, work center (<code>VMC</code>) and <code>run_min_per_unit</code> (unit declared: minutes), but no setup time and no revision, so it does not meet the routing signature and was set aside rather than loaded with the gap filled.</p>
<p><strong>Operation actuals: named missing.</strong> No actuals file. The backflush check had nothing to run on; no row is <code>probable_standard</code>. Time-unit flags: none (no routing or actuals rows loaded).</p>
<p><strong>Work center to cell:</strong> no plant profile, so the machine-class map is missing from the Plant context; no cell is filled from it. Work center <code>VMC</code> (plan.csv) appears nowhere on the equipment list, whose work centers are <code>MILL-H</code>, <code>MILL-V</code>, <code>TURN</code>, <code>INSP</code>. Output.csv prints cell <code>CELL-A</code>; the equipment list prints <code>Cell A</code>. Cell is not a join key, so nothing was changed.</p>
</div>

<div class="panel"><h2>Integrity checks</h2>
{table(["Flag","Rows"], flag_rows, (1,))}
<p>Downtime duration check (stated vs end minus start, in code):</p>
{table(["Row","Stated min","End minus start"], dur, (1,2))}
<p><strong>Gaps carried on every row, not integrity flags:</strong></p>
<ul>
<li>Unit of measure not stated on {F["Rows with no UOM stated"]} quantity rows. Quantities are reported as printed; no total across them is offered.</li>
<li>Time zone unresolved on all {F["Rows with as_of zone unresolved"]} rows (no zone in any file, no source-clock row). Rows are usable for counting, not for cross-source correlation (root-cause-capa) or cross-midnight attribution (daily-production-report). Work-order and equipment rows have no date of their own; their <code>as_of</code> is the file modified date, labelled as such.</li>
<li>Site not stated in source on {F["Rows with site not stated in source"]} rows; left as "not stated in source" rather than assumed to be SITE-1.</li>
</ul></div>

<div class="panel"><h2>Tabs named missing (not empty)</h2>
{table(["Tab","Status","Why"], [[m["tab"], m["status"], m["why"]] for m in MISSING])}</div>

<div class="panel"><h2>Questions for the plant</h2><ol>{"".join(f"<li>{q}</li>" for q in questions)}</ol></div>

<div class="panel"><h2>Figures block</h2>
<p>Every count on this page, as computed by <code>build_dataset.py</code>. Reconciled: exact ({F["Key checks matched exactly"]}) + normalized ({F["Key checks matched after normalization"]}) = matched ({F["Key checks matched (exact + normalized)"]}); matched + awaiting fix ({F["Key checks awaiting a proposed fix (classes 2-5)"]}) + unmatched ({F["Key checks unmatched"]}) = key checks run ({F["Key checks run (non-asset-list rows)"]}); awaiting fix = sum of classes 2 to 5.</p>
{table(["Figure","Value","Computed from","Filter or query"], fig_rows, (1,))}</div>

<footer class="page-footer">Generated by <strong>data-consolidate</strong> &mdash; Manufacturing. Writes nothing to any system of record.</footer>
</main></body></html>"""
open(f"{OUT}/data_quality_report.html", "w", encoding="utf-8").write(page)
print("ok", len(page))
