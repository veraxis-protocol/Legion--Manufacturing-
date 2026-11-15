"""Build the full Operations Command Center fallback page from the engine's output.

Selects and formats only: every number comes from pulse_model.json, figures.csv
or day_records.json written by pulse_compute.py in this run. No arithmetic here.
Usage: python -I build_operations_page.py <pulse-output folder> <drop folder>
"""
import csv, html, json, os, sys

out_dir, drop_dir = sys.argv[1], sys.argv[2]
m = json.load(open(os.path.join(out_dir, "pulse_model.json"), encoding="utf-8"))
recs = json.load(open(os.path.join(out_dir, "day_records.json"), encoding="utf-8"))
figs = list(csv.DictReader(open(os.path.join(out_dir, "figures.csv"), encoding="utf-8")))
F = {r["id"]: r for r in figs}
e = lambda s: html.escape("" if s is None else str(s))


def fv(fid):
    """A figure's value, printed from the block, with its id carried on the page."""
    r = F[fid]
    return '<span class="num" title="figure %s">%s</span>' % (e(fid), e(r["value"]))


ctx, fr, td, dp = m["context"], m["freshness"], m["today"], m["data_problems"]
day = fr["production_day"]
site = ctx["site"]
rec = [r for r in recs if r["production_day"] == day][0]
drop_files = sorted(os.listdir(drop_dir))

P = []
a = P.append
a("""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>%s: Operations Command Center</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans+Condensed:wght@500;600&family=IBM+Plex+Sans:wght@400;500;600&family=IBM+Plex+Mono:wght@500&display=swap" rel="stylesheet">
<style>
:root{--ink:#1A1D21;--paper:#F2F3F5;--paper-raised:#FFFFFF;--line:#D6D9DD;--accent:#1F5C8B;--accent-soft:#E4EDF4;
--good:#2E7248;--good-soft:#E3EFE7;--warn:#A8641A;--warn-soft:#F7EBDA;--critical:#A93226;--critical-soft:#F9E9E7;
--font-display:'IBM Plex Sans Condensed','Arial Narrow',sans-serif;--font-body:'IBM Plex Sans',-apple-system,BlinkMacSystemFont,sans-serif;
--font-mono:'IBM Plex Mono','SF Mono',Consolas,monospace}
@media (prefers-color-scheme: dark){:root:not([data-theme="light"]){--ink:#E8EAEC;--paper:#15181B;--paper-raised:#1D2126;--line:#2E343A;--accent:#6BA8D4;--accent-soft:#1B2C39;--good:#6FBF88;--good-soft:#1B2E22;--warn:#D9A15C;--warn-soft:#33271A;--critical:#DE8378;--critical-soft:#35201E}}
:root[data-theme="dark"]{--ink:#E8EAEC;--paper:#15181B;--paper-raised:#1D2126;--line:#2E343A;--accent:#6BA8D4;--accent-soft:#1B2C39;--good:#6FBF88;--good-soft:#1B2E22;--warn:#D9A15C;--warn-soft:#33271A;--critical:#DE8378;--critical-soft:#35201E}
body{margin:0;background:var(--paper);color:var(--ink);font-family:var(--font-body);line-height:1.45}
.page{display:flex;flex-direction:column;gap:1.25rem;max-width:900px;margin:0 auto;padding:2rem 1rem}
.panel{background:var(--paper-raised);border:1px solid var(--line);border-radius:4px;padding:1.25rem 1.5rem}
h1,h2,h3{font-family:var(--font-display);font-weight:600;margin:0 0 .5rem}
h1{font-size:1.75rem}h2{font-size:1.375rem}h3{font-size:1.125rem;margin-top:1rem}
.meta{color:var(--ink);opacity:.75;font-size:.875rem;margin:.15rem 0}
.num,td.n,code{font-family:var(--font-mono);font-variant-numeric:tabular-nums}
.tw{overflow-x:auto}table{border-collapse:collapse;width:100%%;font-size:.875rem}
th,td{border-bottom:1px solid var(--line);padding:.35rem .5rem;text-align:left;vertical-align:top}
th{font-weight:600}
.pill{display:inline-block;padding:.05rem .5rem;border-radius:999px;font-size:.75rem;font-weight:600}
.pill--critical{background:var(--critical-soft);color:var(--critical)}.pill--warn{background:var(--warn-soft);color:var(--warn)}
.pill--good{background:var(--good-soft);color:var(--good)}.pill--neutral{background:var(--accent-soft);color:var(--accent)}
.banner{border-left:4px solid var(--critical)}.safety{border-left:4px solid var(--warn)}
.note{font-size:.875rem;opacity:.85}
details summary{cursor:pointer;font-weight:600}
</style></head><body><main class="page">""" % e(site))

# Header (fallback page: "Generated", not "Updated")
a('<header class="panel"><h1>%s: Operations Command Center</h1>' % e(site))
a('<p class="meta">%s · Generated %s · data as of %s</p>' % (e(site), e(ctx["run_time_local"]), e(fr["data_as_of_local"])))
a('<p class="meta">Production day: <span class="num">%s</span> (%s) · day boundary: %s</p>' % (
    e(day), e(fr["day_source"]), e(ctx["day_boundary"])))
a('<p class="meta">Offered page, not a published dashboard: the dashboard was not updated (no artifact store in this session).</p></header>')

# 1-2. Safety
a('<section class="panel safety"><h2>Safety</h2>')
if m["diagnoses"]["safety_flagged"]:
    for s in m["diagnoses"]["safety_flagged"]:
        a("<p>%s</p>" % e(s))
else:
    a("<p><strong>Safety status: not assessed</strong> (no breakdown diagnosis records in this drop).</p>")
a('<p class="note">Blocked — safety status unknown: %s records (figure <code>diag.blocked</code>).</p></section>' % fv("diag.blocked"))

# 3. Freshness banner
a('<section class="panel banner"><h2>Freshness</h2>')
for g in fr["gaps"]:
    a('<p><span class="pill pill--critical">MISSING</span> <strong>%s.</strong> Output against plan, availability, performance and OEE are not computed for %s. This day is recorded <code>data_complete: false</code>.</p>' % (e(g[0].upper() + g[1:]), e(day)))
if "README.txt" in drop_files and not any(f.lower().startswith("plan") for f in drop_files):
    a('<p class="note">The drop\'s own README.txt describes a plan.csv; no file named plan.* is in the drop folder (folder listing: %s).</p>' % e(", ".join(drop_files)))
a('<p><span class="pill pill--warn">STALE</span> Newest production day %s is %s days before this run.</p>' % (fv("fresh.day"), fv("fresh.days_old")))
a('<div class="tw"><table><tr><th>Source</th><th>File</th><th>Covers</th><th>Rows</th><th>Landed</th></tr>')
names = {"output": "Production (MES output) export", "downtime": "Downtime export", "work_orders": "ERP work orders export"}
a('<tr><td>Planning export</td><td>none</td><td colspan="3"><span class="pill pill--critical">did not land</span></td></tr>')
for k, c in fr["coverage"].items():
    a('<tr><td>%s</td><td><code>%s</code></td><td class="n">%s</td><td class="n">%s</td><td class="n">%s</td></tr>' % (
        e(names.get(k, k)), e(c["file"]), fv("cov." + k), e(c["rows"]), e(c["landed"])))
a('<tr><td>Routings</td><td><code>%s</code></td><td colspan="3">read for standard run time; not dated</td></tr>' % e(ctx["files_used"].get("routings")))
a('<tr><td>Maintenance (CMMS)</td><td>none</td><td colspan="3">No CMMS connector and no maintenance export in the drop: maintenance work orders in progress could not be seen. This is not "no open maintenance".</td></tr>')
a("</table></div>")
a('<p class="note">All sources are export-sourced files, not live systems. Records timestamped after the run: %s. Files not used: %s.</p>' % (
    fv("fresh.future"), e("; ".join("%s (%s)" % (x["file"], x["why"]) for x in ctx["files_not_used"]))))
a('<p class="note">Run assumptions: %s No plant profile: the latest complete production day in the exports was used.</p></section>' % e(" ".join(ctx["assumptions"])))

# 4. Today's actions
a('<section class="panel"><h2>Today\'s actions</h2><div class="tw"><table><tr><th>#</th><th>Issue</th><th>Impact</th><th>Next step</th><th>Owner role</th><th>Type</th></tr>')
mach = m["short_page"]["decisions"][1] if len(m["short_page"]["decisions"]) > 1 else None
rows = [("Planning export did not land for %s." % e(day),
         "No plan to compare against: output against plan and OEE not computed; the day is a gap in the trend.",
         "Restore the planning export, then re-run the pulse for %s; the re-run overwrites this day's record." % e(day),
         "suggested: planning / export owner", "investigation")]
if mach:
    rows.append(("%s: most downtime minutes, reason %s (&ldquo;%s&rdquo;)." % (e(mach["asset"]), e(td["stops"][0]["code"]), e(mach["reason_text"])),
                 "%s of %s downtime minutes month to date (%s%%). Safety status: not assessed." % (e(mach["minutes"]), e(mach["total_minutes"]), e(mach["share_pct"])),
                 "Confirm %s's current state; run a breakdown diagnosis if the overrun repeats." % e(mach["asset"]),
                 "suggested: maintenance lead", "investigation"))
rows.append(("Losses unpriced.", "Scrap and downtime dollars unknown, not $0.",
             "Supply a downtime cost per hour and standard costs for PN-100 and PN-200 through onboarding.",
             "suggested: plant controller", "observation"))
for i, r in enumerate(rows, 1):
    a("<tr><td class=\"n\">%d</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>" % ((i,) + r))
a("</table></div><p><strong>No decisions waiting today.</strong> Nothing is awaiting an approval: no normalizations proposed, no reschedule move drafted.</p></section>")

# 5. Output against plan
a('<section class="panel"><h2>Output against plan</h2>')
a('<p>Plan comparison unavailable: the planning export did not land. Actual good output only.</p>')
a('<div class="tw"><table><tr><th>Part</th><th>Planned</th><th>Good</th><th>Variance</th><th>Status</th><th>MES spelling</th></tr>')
for p, x in td["parts"].items():
    a('<tr><td><code>%s</code></td><td class="n">%s</td><td class="n">%s</td><td>not computed</td><td>%s</td><td><code>%s</code></td></tr>' % (
        e(p), fv("out.%s.%s.planned" % (day, p)), fv("out.%s.%s.good" % (day, p)), e(x["status"]), e(", ".join(x["mes_spellings"]))))
a('</table></div><p class="note">Total good output, %s: <span class="num">%s</span> (unit not stated in the exports; day record <code>actual_qty</code>). Planned quantity: null (not 0). Normalizations relied on: none.</p></section>' % (
    e(day), e(", ".join(str(v) for v in rec["actual_qty"].values()))))

# 6. OEE
a('<section class="panel"><h2>OEE</h2><div class="tw"><table><tr><th>Scope</th><th>Availability</th><th>Performance</th><th>Quality</th><th>OEE</th></tr>')
a('<tr><td>Site, %s</td><td class="n">%s</td><td class="n">%s</td><td class="n">%s</td><td class="n">%s</td></tr></table></div>' % (
    e(day), fv("oee.%s.availability" % day), fv("oee.%s.performance" % day), fv("oee.%s.quality" % day), fv("oee.%s.oee" % day)))
a('<p class="note">Why not: no planned production time for any asset (the planning export carries planned hours and did not land, and there is no plant profile with shift hours), so no per-asset OEE row could be built (%d assets computed). A missing component is never taken as 1.0.</p>' % len(td["oee_by_asset"]))
a('<p class="note">Quality convention: %s.</p></section>' % e(td["quality_convention"]))

# 7. Downtime, both rankings
dd = m["downtime"]["day"]
a('<section class="panel"><h2>Downtime, %s</h2>' % e(day))
a('<p>%s events, %s minutes (trusted rows), %s ongoing, %s held out for untrusted minutes. Events coded Other or blank: %s of %s.</p>' % (
    fv("dt.%s.events" % day), fv("dt.%s.minutes" % day), fv("dt.%s.ongoing" % day), fv("dt.%s.held" % day), fv("dt.%s.uncoded_events" % day), fv("dt.%s.events" % day)))
for title, key in (("By asset", "by_asset"), ("By reason code", "by_code")):
    for rank, lab in (("rank_minutes", "ranked by minutes"), ("rank_events", "ranked by frequency")):
        rows_ = sorted(dd[key], key=lambda r: (r[rank], r["key"]))
        a('<h3>%s, %s</h3><div class="tw"><table><tr><th>Rank</th><th>%s</th><th>Events</th><th>Minutes</th></tr>' % (lab.capitalize(), title, "Asset" if key == "by_asset" else "Code"))
        for r in rows_:
            a('<tr><td class="n">%s</td><td><code>%s</code></td><td class="n">%s</td><td class="n">%s</td></tr>' % (e(r[rank]), e(r["key"]), e(r["events"]), e(r["minutes"])))
        a("</table></div>")
a('<h3>Downtime log</h3><div class="tw"><table><tr><th>Asset</th><th>Start</th><th>Minutes</th><th>Code</th><th>Reason text</th></tr>')
for s in td["stops"]:
    a('<tr><td><code>%s</code></td><td class="n">%s</td><td class="n">%s</td><td><code>%s</code></td><td>%s</td></tr>' % (e(s["asset"]), e(s["start"]), e(s["minutes"]), e(s["code"]), e(s["text"])))
a('</table></div><p class="note">Ties in the frequency ranking share a rank. Source: downtime export, not live.</p></section>')

# 8. Priced losses
a('<section class="panel"><h2>Priced losses</h2><div class="tw"><table><tr><th>Item</th><th>Quantity</th><th>USD</th></tr>')
for s in td["scrap"]:
    a('<tr><td>Scrap <code>%s</code></td><td class="n">%s</td><td class="n">%s</td></tr>' % (e(s["part"]), fv("scrap.%s.%s" % (day, s["part"])), fv("scrapusd.%s.%s" % (day, s["part"]))))
a('<tr><td>Downtime</td><td class="n">%s min</td><td class="n">%s</td></tr></table></div>' % (fv("dt.%s.minutes" % day), fv("dtusd.%s" % day)))
a('<p>Rate source: <code>%s</code>. Unpriced:</p><ul>' % e(td["rate_source"]))
for u in td["unpriced"]:
    a("<li>%s</li>" % e(u))
a('</ul><p class="note">The rates_memo.txt in the drop holds burdened shop rates and quoting markups, not a downtime cost per hour or standard material costs, and is not a <code>## Plant rates</code> file; it was not used to price anything. Dollars are unknown, not $0.</p></section>')

# 9. Exceptions
a('<section class="panel"><h2>Exceptions</h2><p>Exceptions found: %s. Late jobs (open work orders due on or before %s with good output short): %s; completion undeterminable: %s. No reschedule move drafted, none needed.</p>' % (
    fv("exc.count"), e(day), fv("exc.late"), fv("exc.late_undeterminable")))
a('<p class="note">The ERP work-order export carries no sales-order link, so commitment impact would not be traceable for any exception.</p></section>')

# 10-11. Data problems and Checked, nothing wrong
a('<section class="panel"><h2>Data problems · %s</h2>' % fv("problems.count"))
a('<p>No mismatched keys in classes 1–5 or 8 (figure <code>mismatched.count</code> = %s; orphans %s). Coverage (class 7): stated in the freshness banner. Integrity flags: downtime duration conflicts %s, blank lots %s.</p>' % (
    fv("mismatched.count"), fv("orphan.count"), fv("integrity.dt_flags"), fv("integrity.blank_lot")))
a('<h3>Checked, nothing wrong</h3><p>%s records (outside the count).</p></section>' % fv("checked.count"))

# Trend
a('<section class="panel"><h2>Trend</h2><p>Trend unavailable: the dashboard\'s stored day records could not be read (no artifact store in this session), and this run\'s exports cover a single production day (%s). No history to chart.</p>' % e(day))
a('<p>Week-over-week skipped: the earlier week has %s days of data (this week: %s day). From this run\'s exports, not stored history.</p></section>' % (fv("wow.prev.days"), fv("wow.this.days")))

# Day record
a('<section class="panel"><h2>Day record <code>%s</code></h2><p>Computed, not stored: no artifact store in this session.</p><div class="tw"><table><tr><th>Field</th><th>Value</th></tr>' % e(rec["record_key"]))
for k, v in rec.items():
    a('<tr><td><code>%s</code></td><td class="n">%s</td></tr>' % (e(k), e(json.dumps(v, ensure_ascii=False) if isinstance(v, (dict, list)) or v is None or isinstance(v, bool) else v)))
a("</table></div></section>")

# Figures block
a('<section class="panel"><details><summary>Figures block (%s rows, figures.csv)</summary><div class="tw"><table><tr><th>id</th><th>Figure</th><th>Value</th><th>Unit</th><th>Source</th><th>Filter</th></tr>' % fv("figures.rows"))
for r in figs:
    a('<tr><td><code>%s</code></td><td>%s</td><td class="n">%s</td><td>%s</td><td>%s</td><td>%s</td></tr>' % tuple(e(r[k]) for k in ("id", "figure", "value", "unit", "source", "filter")))
a("</table></div></details></section>")

a('<footer class="panel note"><p>Generated by morning-plant-pulse — Manufacturing · stored production days: not read (no artifact store this run) · engine self-checks: %d run, %d failed.</p>' % (m["checks"]["run"], len(m["checks"]["failed"])))
a('<p>Here is the Operations page for %s; save it over yesterday\'s. The dashboard was not updated: there is no artifact store in this session.</p></footer>' % e(day))
a("</main></body></html>")

path = os.path.join(out_dir, "operations-%s-%s.html" % (site, day))
open(path, "w", encoding="utf-8").write("\n".join(P))
print(path)
