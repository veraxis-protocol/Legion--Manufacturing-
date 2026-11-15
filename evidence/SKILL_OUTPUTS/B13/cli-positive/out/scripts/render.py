"""Render Chain 4 outputs from figures.json. Usage: python -I render.py <out_dir>"""
import sys, json, html
OUT = sys.argv[1]
D = json.load(open(f"{OUT}/figures.json"))
FV = {f["figure"]: f["value"] for f in D["F"]}
def v(name): return html.escape(str(FV[name]))
e = html.escape
pct = lambda x: f"{x:.1%}"

CSS = """:root{--ink:#1A1D21;--paper:#F2F3F5;--paper-raised:#FFFFFF;--line:#D6D9DD;--accent:#1F5C8B;--accent-soft:#E4EDF4;
--good:#2E7248;--good-soft:#E3EFE7;--warn:#A8641A;--warn-soft:#F7EBDA;--critical:#A93226;--critical-soft:#F9E9E7;
--font-display:'IBM Plex Sans Condensed','Arial Narrow',sans-serif;--font-body:'IBM Plex Sans',-apple-system,BlinkMacSystemFont,sans-serif;--font-mono:'IBM Plex Mono','SF Mono',Consolas,monospace}
body{background:var(--paper);color:var(--ink);font-family:var(--font-body);max-width:1100px;margin:24px auto;padding:0 20px;line-height:1.45;font-size:14px}
h1{font-family:var(--font-display);font-size:26px;margin:0 0 14px}h2{font-family:var(--font-display);font-size:19px;border-bottom:1px solid var(--line);padding-bottom:4px;margin-top:28px}
h3{font-size:15px;margin:16px 0 4px}h4{font-size:13px;margin:10px 0 2px;color:var(--accent);text-transform:uppercase;letter-spacing:.04em}
.card{background:var(--paper-raised);border:1px solid var(--line);border-radius:6px;padding:12px 16px;margin:12px 0}
.safety{background:var(--critical-soft);border:2px solid var(--critical);border-radius:6px;padding:12px 16px;margin:12px 0}
.safety h2{color:var(--critical);border:none;margin-top:0}
.fresh{background:var(--warn-soft);border:1px solid var(--warn);border-radius:6px;padding:10px 16px;margin:12px 0}
table{border-collapse:collapse;width:100%;background:var(--paper-raised);margin:6px 0;font-size:13px}
th,td{border:1px solid var(--line);padding:5px 8px;text-align:left;vertical-align:top}th{background:var(--accent-soft)}
td.n{text-align:right;font-family:var(--font-mono)}code,.mono{font-family:var(--font-mono);font-size:12px}
.pill{display:inline-block;padding:1px 8px;border-radius:10px;font-size:12px;background:var(--accent-soft)}
.pill.crit{background:var(--critical-soft);color:var(--critical)}.pill.warn{background:var(--warn-soft);color:var(--warn)}
details{margin:8px 0}summary{cursor:pointer;font-weight:600}.foot{margin-top:28px;padding-top:8px;border-top:1px solid var(--line);font-size:13px}"""
def page(title, body): return f"<!doctype html><html><head><meta charset='utf-8'><title>{e(title)}</title><style>{CSS}</style></head><body><h1>{e(title)}</h1>{body}</body></html>"
def table(hdr, rows, num=()):
    h = "".join(f"<th>{e(x)}</th>" for x in hdr)
    b = "".join("<tr>" + "".join(f"<td class='n'>{c}</td>" if i in num else f"<td>{c}</td>" for i, c in enumerate(r)) + "</tr>" for r in rows)
    return f"<table><tr>{h}</tr>{b}</table>"
def figblock(names=None):
    rows = [(e(f["figure"]), e(str(f["value"])), e(f["source"]), f"<code>{e(f['filter'])}</code>") for f in D["F"] if names is None or f["figure"] in names]
    return table(["Figure", "Value", "Computed from", "Filter or query"], rows)

LOTO = "<p><b>Follow your plant's lockout procedure before anyone works on this machine. This is not a safety assessment.</b></p>"
SAFETY_REASON = ("Electrical fault, a trip: the spindle drive stopped on a 'SPINDLE OVERLOAD / OVERTEMP' alarm mid-cycle. "
  "The OEM manual (Sect. 7.4) says not to run a spindle that is making a grinding noise, and the operator reported grinding for about 20 minutes before the alarm. "
  "The drawbar's Belleville spring stack is stored energy, and one of the checks below involves it. "
  "The bluish colour on the spindle nose shows it ran hot. Nobody has yet checked whether the spindle turns freely.")
SAFETY_HTML = f"""<div class='safety'><h2>Safety: VMC-02, flagged</h2>{LOTO}
<ul><li><b>Do not run the spindle, and do not jog it to 'listen' or to take a vibration spectrum.</b> The OEM manual (Sect. 7.4) says: <i>"Do not run a spindle showing grinding noise."</i> The operator reported grinding for about 20 min before the alarm.</li>
<li><b>Lock out the spindle drive before any hand rotation or inspection</b> (OEM Sect. 7.4). The spindle has not been hand-turned yet, so nobody knows whether it is seized or partly seized.</li>
<li><b>The drawbar clamp is a stored-energy assembly</b> (Belleville spring stack). Use the plant's drawbar procedure for the clamp-force check in candidate 2.</li>
<li>The bluish discolouration on the spindle nose and taper means that area overheated. Let it cool before handling it.</li></ul>
<p class='mono'>safety_flagged: true &middot; safety_reason: {e(SAFETY_REASON)}</p></div>"""

# ---------------- Diagnosis page ----------------
CANDS = [
 dict(n=1, name="Spindle bearing damage or loss of preload, a progressive failure", conf="medium",
  ev=f"""<ul><li><b>Sensor data:</b> spindle vibration rose at every sample, {v('Spindle vibration first -> last (mm/s)')}. Temperature rose with it, {v('Spindle temperature first -> last (C)')} &deg;C, and spindle load went {v('Spindle load first -> last (%)')}. This is a steady, accelerating climb, which is the pattern progressive wear produces, not a step change.</li>
<li><b>OEM manual Sect. 7.4:</b> "Overtemp with rising vibration → spindle bearing wear / preload loss". "Grinding noise → bearing damage or contamination".</li>
<li><b>Operator:</b> grinding noise for ~20 min before the alarm, and chips looked normal, which points away from a cutting problem. The vibration jump between 15:00 and 15:20 matches when the noise started.</li>
<li><b>Photo description</b> (no image file was supplied): bluish discolouration on the spindle nose and taper. That shows heat at the front of the spindle. It does not say which part produced the heat, and a front-bearing failure and a slipping tool holder would both leave this mark.</li>
<li><b>History:</b> two VMC-02 notes recorded early bearing symptoms, and neither was followed up with a work order in this export (cited below).</li></ul>""",
  cite=[("MW-118", "2026-03-02", "quarterly PM done. greased ways. spindle sounded a bit rough at 8k, monitor"),
        ("MW-140", "2026-07-08", "PM. vib reading 2.1 mm/s at 8k (was 1.4 last yr). told sup")],
  test="""<ol><li><b>Spindle drive locked out:</b> turn the spindle by hand (about 5 min, OEM Sect. 7.4). If it feels rough, notchy or draggy, the bearings are confirmed. If it turns smoothly, candidates 2 and 3 move up.</li>
<li>If it turns, check run-out at the taper with a test bar and an indicator. The OEM limit is <b>&lt; 3 &micro;m</b> (Sect. 7.4). Out of limit means bearings or a damaged taper.</li>
<li>The vibration spectrum at bearing frequencies, the manual's other check, needs the spindle running. Grinding noise rules that out. Leave it to the spindle rebuilder.</li></ol>""",
  fix="Remove the spindle cartridge and have it rebuilt or replaced: new bearings, preload reset. Inspect the taper for heat damage and regrind or replace it. Run in, then record a new vibration baseline at a fixed speed. Do this together with candidate 3's chiller check. A new bearing on a spindle with poor cooling can fail the same way. This is a long-lead repair, so get a rebuild quote now."),
 dict(n=2, name="Chiller low on fluid or flow: inadequate spindle cooling that contributed to or caused the failure", conf="low",
  ev=f"""<ul><li><b>History:</b> in September the chiller was found low on fluid and topped up. The note does not say why it was low, so a leak was never ruled out (cited below).</li>
<li><b>OEM manual Sect. 7.4:</b> "Overtemp, normal vibration → chiller low flow / fluid level".</li>
<li><b>Against it as the sole cause:</b> vibration did <i>not</i> stay normal ({v('Spindle vibration first -> last (mm/s)')}), so by the manual's own table this is not a pure cooling fault.</li>
<li><b>The sensor data cannot test this.</b> <code>coolant_pressure_bar</code> held at {v('Coolant pressure range (bar)')} bar, but that is very likely cutting-coolant pressure, not chiller flow. There is no chiller channel in the export.</li></ul>""",
  cite=[("MW-160", "2026-09-23", "spindle hot after long cycle. checked chiller - low on fluid topped up. temp ok after")],
  test="Check the chiller fluid level and flow, and look for leaks (about 5 min; the spindle does not need to be touched, but follow your lockout procedure). If the level is low again after the September top-up, there is a leak, and cooling becomes the likely root cause behind candidate 1, not an alternative to it.",
  fix="Find and fix the fluid loss. Verify chiller flow against the OEM spec, which is not in the excerpt supplied. Add chiller level to the PM (see the PM draft below)."),
 dict(n=3, name="Drawbar clamp force low: tool holder slipping or fretting in the taper", conf="low",
  ev=f"""<ul><li><b>History:</b> in May a spindle alarm was traced to low drawbar clamp force, and the Belleville stack was <i>adjusted</i>, not replaced (cited below).</li>
<li>An overload alarm and heat colour at the taper are both consistent with a holder slipping.</li>
<li><b>OEM manual Sect. 7.4:</b> "Overload with tool pull-out marks → drawbar clamp force low".</li>
<li><b>Against it:</b> no tool pull-out marks are reported, chips looked normal, and grinding noise plus a steadily rising vibration fit bearings better.</li></ul>""",
  cite=[("MW-131", "2026-05-19", "spindle alarm 2nd shift. found drawbar clamp low, adjusted belleville stack. ran ok")],
  test="Pull the tool holder from WO-8120 op 20 and look at its taper and the spindle taper for fretting or pull-out marks (about 5 min). Then measure clamp force with the gauge. The OEM spec is <b>8.0-9.5 kN</b> (Sect. 7.4). Belleville stack: stored energy, use the drawbar procedure. Clamp force in spec and no marks rules this candidate out.",
  fix="Replace the Belleville stack rather than adjust it again, because May's adjustment did not hold if the force is low now. Clean the taper, or regrind it if fretted. Replace a damaged tool holder."),
]
def cand_html(c):
    cites = "".join(f"<li><b>{w}</b> ({d}): <i>\"{e(t)}\"</i></li>" for w, d, t in c["cite"])
    return f"""<div class='card'><h3>{c['n']}. {e(c['name'])} <span class='pill'>confidence: {c['conf']}</span> <span class='pill warn'>advisory</span></h3>
<h4>Evidence</h4>{c['ev']}<p><b>Cited work orders</b> (VMC-02 export; each note appears on one asset only, see the template check):</p><ul>{cites}</ul>
<h4>First check</h4>{c['test'] if c['test'].startswith('<') else '<p>'+c['test']+'</p>'}
<h4>Expected fix and repair path</h4><p>{c['fix']}</p></div>"""

SENSOR_TXT = f"""<p>The historian window is {v('Sensor window')}, {v('Sensor rows, VMC-02')} samples. {v('Window covers the 15:24 alarm')}, so it covers the event. Nothing after the alarm is in the file.</p>
<ul><li>Vibration: {v('Spindle vibration first -> last (mm/s)')}. It rose at every sample ({v('Vibration and temperature rise at every sample')}) and climbed faster toward the end. It first went above MW-140's July PM reading at <b>{v("First sample above MW-140's 2.1 mm/s")}</b>. It first doubled from the window start at <b>{v('First sample above 2x window-start vibration')}</b>. Caveat: MW-140's 2.1 mm/s was measured at 8,000 rpm and the window has no rpm column, so the two are not strictly comparable.</li>
<li>Temperature: {v('Spindle temperature first -> last (C)')} &deg;C, rising together with vibration. Samples are 30 minutes apart, so the data cannot show which rose first.</li>
<li>Spindle load: {v('Spindle load first -> last (%)')}. Coolant pressure stayed flat at {v('Coolant pressure range (bar)')} bar.</li>
<li>Shape: a steady, accelerating climb with no step change and no recovery. The manual and the reference material associate this with progressive wear. The drift was visible well over an hour before the alarm and never tripped one.</li></ul>"""

TIMELINE = table(["Time (-05:00)", "Vibration mm/s", "Temp &deg;C", "Load %", "Coolant bar"],
  [(e(s["timestamp"][11:16]), s["spindle_vibration_mm_s"], s["spindle_temp_c"], s["spindle_load_pct"], s["coolant_pressure_bar"]) for s in D["sensor"]], num=(1, 2, 3, 4))

PM_DRAFT = f"""<div class='card'><p><b>DRAFT for the maintenance planner, not applied.</b> No CMMS connector is live and there is no PM plan in the inputs, so <b>first: what is VMC-02's current PM interval and task list?</b> The export shows PMs on 2026-03-02 (MW-118) and 2026-07-08 (MW-140), which suggests roughly quarterly. That is inferred from two records, not read from a plan.</p>
<p>Failure mode: progressive spindle bearing degradation. It was noted twice (MW-118 "rough… monitor", MW-140 "vib 2.1 (was 1.4)… told sup") and neither note produced a follow-up work order. Proposed changes for VMC-02:</p>
<ol><li><b>Spindle vibration reading at a fixed speed (8,000 rpm), monthly</b> instead of only at the quarterly PM, logged as a number against a baseline set after the repair. Suggested action limit for the planner to confirm: any reading above 1.5&times; that baseline raises a corrective work order automatically.</li>
<li><b>Historian alert on vibration trend</b>, not only the alarm limit. In this event vibration passed the July PM reading {v("First sample above MW-140's 2.1 mm/s")} and doubled {v('First sample above 2x window-start vibration')}.</li>
<li><b>Chiller fluid level and flow</b> added to every PM, plus a weekly operator check, until the cause of the September fluid loss (MW-160) is found.</li>
<li><b>Drawbar clamp force against the 8.0-9.5 kN spec, and taper run-out under 3 &micro;m</b>, both added to the quarterly PM (OEM Sect. 7.4), given MW-131.</li>
<li><b>Procedure change:</b> a close-out note containing "monitor" or "told sup" opens a follow-up work order with an owner, so it is not left in a text field.</li></ol>
<p>VMC-03 is a sibling by asset name only, because the export has no model column. If it is the same model, items 1 and 4 should apply to it as well. Its single record (MW-152, coolant pump) has nothing on the spindle.</p></div>"""

CLOSEOUT = """<div class='card'><p><b>DRAFT close-out note.</b> Nothing has been written to any CMMS. No connector is live, and this export has no ticket for the breakdown. Edit it to match what the technician actually finds, then paste it:</p>
<p class='mono'>2026-11-10 15:24 VMC-02 stopped on SPINDLE OVERLOAD / OVERTEMP during WO-8120 op 20 (MB-1880). Operator heard grinding ~20 min before. Historian: spindle vib 1.8→11.2 mm/s and temp 31.0→52.1 C from 13:00 to 15:24, coolant pressure steady. Bluish colour at spindle nose/taper. Spindle locked out, not run. Hand rotation: [rough / smooth]. Taper run-out: [__ um] (OEM <3). Drawbar clamp: [__ kN] (OEM 8.0-9.5). Chiller level/flow: [__]. Found: [__]. Done: [__]. Watch: vibration at 8k against the new baseline; chiller level. History: MW-118, MW-140 (early bearing signs), MW-131 (drawbar), MW-160 (chiller low).</p></div>"""

diag_names = ["Maintenance rows whose note contains an unquoted comma", "Maintenance records, VMC-02", "VMC-02 records with usable close-out notes",
  "Latest VMC-02 maintenance record", "Latest record in maintenance export (any asset)", "Days from latest maintenance record to breakdown",
  "Maintenance work orders dated on or after 2026-11-10", "Sibling records (asset name prefix VMC-, model not in export)",
  "Sibling records matching the symptom words", "Template check: distinct note texts / texts on >1 asset", "VMC-02 notes mentioning bearing/vibration",
  "VMC-02 notes mentioning drawbar", "VMC-02 notes mentioning chiller/heat", "Sensor rows, VMC-02", "Sensor window", "Window covers the 15:24 alarm",
  "Spindle vibration first -> last (mm/s)", "Spindle temperature first -> last (C)", "Spindle load first -> last (%)", "Coolant pressure range (bar)",
  "Vibration and temperature rise at every sample", "First sample above MW-140's 2.1 mm/s", "First sample above 2x window-start vibration",
  "Known down at least (min), as of 16:10 note", "MES downtime rows matching VMC-02", "VMC-02 rows in plan / output", "WO-8120 in work_orders export"]

TEMPLATE = table(["Close-out note (exact text)", "Records", "Distinct assets"], [(e(g["close_out_note"]), g["n"], g["assets"]) for g in D["grp"]], num=(1, 2))

diag_body = SAFETY_HTML + f"""
<div class='fresh'><b>Sources and how current they are.</b> Everything here comes from files; no CMMS or historian connector is live.
<ul><li><b>Date conflict:</b> the request says VMC-02 went down "yesterday afternoon", which would be 14 Nov. <code>event.txt</code> and the sensor window both say <b>10 Nov 2026, 15:24</b>. This diagnosis uses the files' date. If there was a second stoppage on 14 Nov, these files do not cover it.</li>
<li>Maintenance export: newest record {v('Latest record in maintenance export (any asset)')}, {v('Days from latest maintenance record to breakdown')} days before the breakdown. It holds {v('Maintenance work orders dated on or after 2026-11-10')} tickets dated on or after 10 Nov, so any ticket raised for this breakdown is not in it. From the file alone, a stalled export and a quiet period look the same.</li>
<li>{v('Maintenance rows whose note contains an unquoted comma')} rows in the maintenance export have unquoted commas in the close-out note. They were parsed by splitting on the first five commas, and no note text was lost. Worth fixing in the export job.</li>
<li>Sensor window: covers the alarm (see Sensor data). No photo file was supplied, only a text description of it.</li>
<li>Machine status after the 16:10 note on 10 Nov is <b>unknown</b>. Nothing in the inputs says whether it was repaired or restarted.</li></ul></div>
<h2>Event</h2><div class='card'><p><b>VMC-02</b>. Down at <b>2026-11-10 15:24 -05:00</b>, mid-cycle on <b>WO-8120 op 20 (MB-1880)</b>. Alarm text: <i>'SPINDLE OVERLOAD / OVERTEMP'</i>. Operator: <i>"grinding noise from spindle for ~20 min before alarm, chips looked normal."</i> Still down at 16:10, so it was down at least {v('Known down at least (min), as of 16:10 note')} min. The end time is unknown. Technician photo (description only): <i>"bluish discolouration visible on the spindle nose / taper area."</i></p>
<p><b>Technician step: skipped.</b> This was folded into the report straight away, so the causes below are proposed and nobody has confirmed them at the machine.</p></div>
<h2>Ranked candidate causes</h2>
<p><b>Do these checks in this order. Together they take under 30 minutes and separate all three candidates:</b> (a) chiller level and flow, with no spindle contact; (b) lock out, then turn the spindle by hand; (c) if it turns, run-out at the taper; (d) pull the holder, inspect both tapers, then measure clamp force. A rough spindle at (b) confirms candidate 1. Even then, still do (a) and (d), because they find out <i>why</i> it failed before a new spindle goes in.</p>
{''.join(cand_html(c) for c in CANDS)}
<h2>Sensor data</h2>{SENSOR_TXT}{TIMELINE}
<h2>Maintenance history and close-out notes</h2>
<p>VMC-02 has {v('Maintenance records, VMC-02')} records in the export, and {v('VMC-02 records with usable close-out notes')} have usable notes. The search across siblings (asset names starting <code>VMC-</code>; there is no model column, so "same model" could not be checked) found {v('Sibling records (asset name prefix VMC-, model not in export)')}. Of those, {v('Sibling records matching the symptom words')} match the symptom words, so there is no fleet pattern to cite. <b>Template check:</b> every note text appears on one asset only ({v('Template check: distinct note texts / texts on >1 asset')}), so each cited note is evidence about this machine, not a stock phrase.</p>{TEMPLATE}
<p>The words that matter: <i>"monitor"</i> (MW-118) and <i>"told sup"</i> (MW-140). Both were open-ended, and neither led to a follow-up work order in the export. <i>"adjusted"</i> (MW-131) and <i>"topped up"</i> (MW-160) dealt with the symptom, and neither note records a cause.</p>
<h2>PM plan adjustment</h2>{PM_DRAFT}
<h2>Close-out note</h2>{CLOSEOUT}
<h2>Figures</h2>{figblock(diag_names)}
<p class='foot'>Advisory diagnosis. A technician applies it; nothing has been written to any system of record. Source files: <code>inputs/breakdown/*</code>.</p>"""
open(f"{OUT}/VMC-02-diagnosis-2026-11-10.html", "w", encoding="utf-8").write(page("VMC-02: breakdown diagnosis, 10 Nov 2026", diag_body))

# ---------------- Downtime record (contract v3, YAML) ----------------
REC = f"""# Downtime record, contract version 3: breakdown_diagnosis -> daily-production-report
# Advisory. Not written to any system of record.
contract_version: 3
site: null            # not stated in event.txt; the only site in the production drop is SITE-1, and VMC-02 is not in it. Confirm.
asset_id: VMC-02
asset_id_verbatim: "VMC-02"
started_at: 2026-11-10T15:24:00-05:00
ended_at: null        # status after the 16:10 'still down' note is unknown
duration_minutes: null   # not zero; at least {FV['Known down at least (min), as of 16:10 note']} min known
reason_code: null     # no plant reason code in the event; alarm text kept in reason_text
reason_text: "SPINDLE OVERLOAD / OVERTEMP alarm; grinding noise ~20 min before; stopped mid-cycle"
production_wo: WO-8120
production_wo_verbatim: "WO-8120"
shift: null           # shift pattern not on file
production_day: 2026-11-10
source_system: breakdown_diagnosis
source_ref: "inputs/breakdown/event.txt"

diagnosis_ref: "out/VMC-02-diagnosis-2026-11-10.html"
leading_cause: "Spindle bearing damage / preload loss (progressive); chiller cooling deficit possible contributor"
leading_cause_confidence: medium
cited_work_orders: ["MW-118", "MW-140"]
safety_flagged: true
safety_reason: "{SAFETY_REASON}"
pm_adjustment_proposed: true
maintenance_wo: null  # no ticket for this event in the maintenance export (latest record 2026-09-24)
diagnosis_state: advisory
technician_step: skipped
"""
open(f"{OUT}/downtime-record-VMC-02-2026-11-10.yaml", "w", encoding="utf-8").write(REC)

# ---------------- Morning report ----------------
P = D["plant"]; R = D["rows"]
out_rows = [(r["asset"], r["cell"], r["part"], r["shifts"], r["plan"], r["good"], r["scrap"], f"{r['var']:+d}", pct(r["pct"])) for r in R]
oee_rows = [(r["asset"], pct(r["A"]), pct(r["P"]), pct(r["Q"]), pct(r["OEE"]), f"{r['run']} / {r['planned_min']}", f"{r['ict']} min") for r in R]
oee_rows.append(("<b>Both assets (pooled)</b>", pct(P["A"]), pct(P["P"]), pct(P["Q"]), pct(P["OEE"]), "", ""))
dts = D["dt"]
by_min = sorted(dts, key=lambda d: -d["duration_minutes"])
log_min = [(i + 1, d["asset_id"], d["reason_code"], e(d["reason_text"]), d["duration_minutes"], d["started_at"]) for i, d in enumerate(by_min)]
freq = {}
for d in dts: freq.setdefault(d["reason_code"], [0, 0]); freq[d["reason_code"]][0] += 1; freq[d["reason_code"]][1] += d["duration_minutes"]
log_freq = [(k, n, m) for k, (n, m) in sorted(freq.items(), key=lambda kv: (-kv[1][0], -kv[1][1]))]
wo_rows = [(w["wo"], w["part"], w["ordered"], w["good"], w["short"], w["due"], w["status"]) for w in D["wos"]]

ACTIONS = table(["#", "Issue", "Impact", "Next step", "Owner role", "Type"], [
 ("1", "<b>VMC-02 down since 10 Nov 15:24</b>. Spindle overload/overtemp with grinding noise. Status after 16:10 that day is unknown. Leading cause <i>proposed, not confirmed</i>: spindle bearing damage (confidence medium, advisory; technician step skipped).",
  "WO-8120 op 20 (MB-1880) stopped mid-cycle. WO-8120 is not in the work-order export, so the commitment impact cannot be traced.",
  "Confirm whether VMC-02 is still down. If so, work the diagnosis checks with the spindle locked out and do not run it. Get a spindle rebuild quote.", "suggested: maintenance lead", "investigation"),
 ("2", "<b>Does CMMS asset <code>VMC-02</code> = MES asset <code>CNC-02</code>?</b> Both are in work centre VMC, and the CMMS and MES use different ID schemes. Not matched: nothing in the data links them.",
  "If they are the same machine, it ran 223 parts on 12 Nov, and nothing in the drop shows a spindle repair between 10 and 12 Nov.",
  "Maintenance confirms the asset cross-reference and, if they are the same, that the spindle was inspected before restart. No normalization applied; it needs your yes.", "suggested: maintenance planner", "investigation"),
 ("3", f"<b>WO-1002</b> (PN-200): {v('WO-1002 good vs ordered (through 2026-11-12)')}.", "Past due as of 15 Nov on the last data seen. Output for 13-14 Nov is missing, so it may already be complete. No WO-to-sales-order link.",
  "Scheduler checks actual completion in the ERP or MES.", "suggested: production scheduler", "investigation"),
 ("4", f"<b>WO-1001</b> (PN-100): {v('WO-1001 good vs ordered (through 2026-11-12)')}.", "Past due as of 15 Nov on the last data seen. Same data gap.",
  "Same as #3.", "suggested: production scheduler", "investigation"),
 ("5", "<b>Missing exports for 13 and 14 Nov.</b>", "The report shows 12 Nov, not yesterday.", "Check the scheduled MES and planning export jobs.", "suggested: IT / MES admin", "investigation"),
])

rep_body = f"""<div class='safety'><h2>Safety: VMC-02 breakdown, flagged</h2>{LOTO}
<p><b>VMC-02</b>, started 2026-11-10 15:24 -05:00, production day 10 Nov, <b>still down at last report</b> (end unknown). {e(SAFETY_REASON)}</p>
<p><b>Do not run the spindle. Lock out the spindle drive before hand rotation or inspection</b> (OEM Sect. 7.4). Proposed cause: spindle bearing damage, confidence medium, <i>advisory: proposed, technician step skipped</i>. Full diagnosis: <code>VMC-02-diagnosis-2026-11-10.html</code>.</p>
<p>No records blocked for unknown safety status: the one diagnosis record in this drop has its safety flag set.</p></div>
<div class='fresh'><b>Data freshness: this is not yesterday's report.</b>
<ul><li>The production drop (plan, output, downtime, routing, work orders; files written 13 Nov 14:54) holds <b>one production day: {v('Production days in the drop')}</b>. Exports for <b>{v('Production days missing before today (2026-11-15)')}</b> did not land. Nothing older was reused.</li>
<li>Shifts in the day: CNC-01 shifts 1 and 2, CNC-02 shift 1 only. The shift pattern is not on file, so I can't say whether the day is complete.</li>
<li>The breakdown is dated <b>10 Nov</b>, while the request said "yesterday afternoon" (14 Nov). I used the files' date.</li>
<li>Maintenance comes from an export, newest record 24 Sep 2026, with no ticket for the VMC-02 breakdown. Downtime timestamps have no time zone. No ERP or CMMS connector is live; everything comes from files.</li></ul></div>
<h2>Headline: production day 12 Nov 2026</h2>
<div class='card'><ul><li><b>Good output vs plan:</b> {v('Plant good / plan, 2026-11-12')}. Total output, good plus scrap: {v('Total output (good+scrap)')}.</li>
<li><b>OEE (pooled across the two reported assets):</b> {pct(P['OEE'])}. Availability {pct(P['A'])}, performance {pct(P['P'])}, quality {pct(P['Q'])}. VMC-02 is not in the plan or output for 12 Nov ({v('VMC-02 rows in plan / output')} rows), so it is <b>unreported, not 0%</b>, and it is left out of the OEE.</li>
<li><b>Downtime:</b> {v('MES downtime minutes, 2026-11-12')} min across {v('MES downtime events, 2026-11-12')} MES events. <b>Unpriced:</b> no downtime cost rate is set, either as <code>MFG_DOWNTIME_COST_PER_HOUR</code> or in the plant profile. The VMC-02 outage is <b>not in these minutes</b>: its duration is null and it belongs to production day 10 Nov.</li>
<li><b>Scrap:</b> {v('Scrap units, 2026-11-12')} units. <b>Unpriced:</b> no standard cost per part is available, because there is no ERP connector and no cost column in the exports.</li></ul></div>
<h2>Today's actions</h2>{ACTIONS}
<p>No decisions waiting today: none of these is waiting on an approval yet. <b>No reschedule move is drafted.</b> One would need MB-1880's routing, WO-8120's order record, and a schedule after 12 Nov. None of those is in the drop, so a move could not be traced and would be a guess.</p>
<h2>Floor view</h2><p>No floor layout is on file. Attach a floor plan and ask for a floor view to set one up.</p>
<h2>Detail</h2>
<details open><summary>Output against plan, 12 Nov (by asset and part; cell CELL-A)</summary>{table(['Asset','Cell','Part','Shifts','Plan','Good','Scrap','Var (good-plan)','Good/plan'], out_rows, num=(4,5,6,7,8))}
<p>Parts match exactly between plan and output (PN-100, PN-200), so no normalization was used.</p></details>
<details open><summary>OEE by asset</summary>{table(['Asset','Availability','Performance','Quality','OEE','Run / planned min','Ideal cycle'], oee_rows, num=(1,2,3,4,5,6))}
<p>Quality = good &divide; (good + scrap). The export has no rework column, so first-pass yield could not be applied. Planned production time = <code>planned_hours</code> from plan.csv, because no site definition is on file. Every MES stop counts against availability, including waiting on material. These definitions are defaults until the plant confirms its own.</p></details>
<details open><summary>Downtime log: by minutes</summary>{table(['Rank','Asset','Reason code','Reason text','Minutes','Started (no zone)'], log_min, num=(4,))}
<p><b>Left out of the minutes ranking:</b> VMC-02, 10 Nov 15:24, ongoing or status unknown (null duration, production day 10 Nov). It leads the exceptions instead. Reason-code coverage: {v('Downtime events with no usable reason code')} MES events have no usable code. The VMC-02 record has <i>no plant reason code</i>, only alarm text. Every MES row passed the start, end and duration check ({v('Downtime rows failing end/start/duration check')} failures).</p></details>
<details open><summary>Downtime log: by frequency</summary>{table(['Reason code','Events','Minutes'], log_freq, num=(1,2))}<p>Two events, one per code, so frequency does not separate them.</p></details>
<details open><summary>The VMC-02 diagnosis record and how it was matched to the MES log</summary>
<p><b>Match rule:</b> asset plus start time. A match needs the same <code>asset_id</code>, with <code>started_at</code> in the same shift. <b>No MES row matched</b> ({v('MES downtime rows matching VMC-02')} downtime rows for VMC-02 at any time), so the diagnosis record stands alone as the only row for this stoppage, <b>counted once</b>. The MES rows (CNC-01, CNC-02 on 12 Nov) are a different asset ID and a different day, and they were left exactly as exported.</p>
{table(['Field','Value'], [('asset_id','VMC-02'),('started_at','2026-11-10T15:24:00-05:00'),('ended_at / duration_minutes','null / null (at least '+v('Known down at least (min), as of 16:10 note')+' min known, not counted)'),('production_day','2026-11-10'),('production_wo','WO-8120'),('reason_code','null (alarm text only)'),('leading_cause','Spindle bearing damage / preload loss (proposed)'),('leading_cause_confidence','medium'),('cited_work_orders','MW-118, MW-140'),('safety_flagged','true'),('diagnosis_state','advisory'),('technician_step','skipped'),('site','null (not stated; confirm)')])}</details>
<details open><summary>Priced losses</summary><p>Scrap: {v('Scrap units, 2026-11-12')} units (CNC-01 {v('CNC-01 scrap units')}, CNC-02 {v('CNC-02 scrap units')}): <b>unpriced</b>, because there is no standard cost. The finance memo (<code>rates_memo.txt</code>, 1 Oct) prices scrap at standard material plus labour at the work centre. There is no material standard in the drop, and the mapping from work centre "VMC" to the memo's rate codes is not on file, so labour alone was not priced either. A partial figure would read as the total. Downtime: <b>unpriced</b>. The memo holds burdened shop rates, which are not a downtime cost per hour. To set one, say "update our downtime cost" or set <code>MFG_DOWNTIME_COST_PER_HOUR</code>.</p></details>
<details open><summary>Open work orders</summary>{table(['WO','Part','Ordered','Good through 12 Nov','Short','Due','Status'], wo_rows, num=(2,3,4))}
<p>No WO-to-sales-order link in the ERP export ({v('Work orders with a sales-order link')}), so commitment impact cannot be traced for all 3 WOs. WO-8120 (the VMC-02 job) is not in the export ({v('WO-8120 in work_orders export')} rows).</p></details>
<details><summary>Checked, nothing wrong</summary><ul><li>WO-1003 (PN-100): 300 of 300 good through 12 Nov, due 15 Nov. Complete on quantity, still status RELEASED. Close-out pending, not an exception.</li></ul></details>
<details><summary>Week-over-week movers</summary><p>Skipped. The drop holds one production day, so there is nothing earlier to compare against.</p></details>
<details><summary>Figures, with the query behind each</summary>{figblock()}</details>
<p class='foot'>Sources: <code>inputs/pulse_oee/*</code>, <code>inputs/breakdown/*</code>, <code>inputs/rates_memo.txt</code>. Read-only: nothing was written to any system. The Operations dashboard was not updated: this is a standalone Chain 4 run, and only the overnight pulse publishes it. Here is the page for 12 Nov; save it over yesterday's.</p>"""
open(f"{OUT}/morning-report.html", "w", encoding="utf-8").write(page("SITE-1: morning report, 12 Nov 2026", rep_body))

# ---------------- Operations command-center page, maintenance section ----------------
ops = SAFETY_HTML + f"""<h2>Maintenance</h2>{table(['Asset','Down since','Status','Proposed cause','Confidence','Technician step','Next check','Cited WOs'],
 [('VMC-02','2026-11-10 15:24 -05:00','Unknown after 16:10 on 10 Nov (at least '+v('Known down at least (min), as of 16:10 note')+' min)','Spindle bearing damage / preload loss','medium (advisory)','skipped','Chiller level, then hand-rotation with the spindle locked out','MW-118, MW-140')])}
<p>PM change drafted for the planner, not applied: monthly spindle vibration reading at 8,000 rpm, a historian trend alert, chiller level checks, and clamp-force and run-out checks at PM. Maintenance work orders in progress: <b>unknown</b>. No CMMS connector is live, and the maintenance export (newest record 24 Sep) has no open tickets, which means they cannot be seen here, not that none are open.</p>
<p>Open question: is CMMS <code>VMC-02</code> the same machine as MES <code>CNC-02</code>?</p>
<p class='foot'>The dashboard was not updated: this is a standalone Chain 4 run, and only the overnight pulse publishes the Operations dashboard. Here is the Operations page, maintenance section, for 15 Nov; save it over the last one.</p>"""
open(f"{OUT}/operations-command-center-maintenance.html", "w", encoding="utf-8").write(page("Operations, maintenance section: 15 Nov 2026 (site of VMC-02 not stated)", ops))
print("written")
