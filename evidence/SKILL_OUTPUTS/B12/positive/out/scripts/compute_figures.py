"""Figures block for VMC-02 breakdown diagnosis. Reads inputs, prints JSON."""
import csv, json, re, sys
from collections import defaultdict
base = sys.argv[1]; out = sys.argv[2]
def rows(p):
    with open(p, encoding="utf-8") as f:
        lines = [l for l in f if not l.startswith("#")]
    return list(csv.DictReader(lines))
mh = rows(f"{base}/maintenance_history.csv")
sw = rows(f"{base}/sensor_window.csv")
F = {}
F["maint_records_total"] = {"value": len(mh), "query": "all rows, maintenance_history.csv"}
asset = [r for r in mh if r["asset_id"] == "VMC-02"]
F["maint_records_VMC-02"] = {"value": len(asset), "wos": [r["wo"] for r in asset], "query": 'asset_id == "VMC-02"'}
# model: no model column; derive from asset name prefix
model = lambda a: re.sub(r"-\d+$", "", a)
sib = [r for r in mh if model(r["asset_id"]) == "VMC" and r["asset_id"] != "VMC-02"]
F["sibling_assets_by_name_prefix"] = {"value": sorted({r["asset_id"] for r in sib}), "query": 'asset name prefix "VMC" (no model column), asset_id != "VMC-02"'}
terms = ["spindle", "grind", "bearing", "overtemp", "overload", "hot", "temp", "vib", "drawbar", "chiller"]
pat = re.compile("|".join(terms), re.I)
F["sibling_records_symptom_match"] = {"value": len([r for r in sib if pat.search(r["close_out_note"])]),
    "wos": [r["wo"] for r in sib if pat.search(r["close_out_note"])], "query": f"siblings, note matches /{'|'.join(terms)}/i"}
F["VMC-02_records_symptom_match"] = {"value": len([r for r in asset if pat.search(r["close_out_note"])]),
    "wos": [r["wo"] for r in asset if pat.search(r["close_out_note"])], "query": "VMC-02, same regex"}
terse = re.compile(r"^\s*(fixed|repaired|ok now|done|ok)\.?\s*$", re.I)
F["VMC-02_substantive_notes"] = {"value": len([r for r in asset if r["close_out_note"].strip() and not terse.match(r["close_out_note"])]),
    "of": len(asset), "query": "VMC-02 notes non-empty and not a bare 'fixed/repaired/ok now'"}
g = defaultdict(set)
for r in mh: g[r["close_out_note"].strip()].add(r["asset_id"])
F["template_check"] = {"groups": len(g), "groups_on_more_than_one_asset": sum(1 for v in g.values() if len(v) > 1),
    "query": "group all notes by exact text; count distinct assets/models (model from asset-name prefix, no model column)"}
F["last_maint_record_closed"] = {"value": max(r["closed"] for r in mh), "query": "max(closed)"}
# sensor
seen = set(); dedup = []
for r in sw:
    k = tuple(r.values())
    if k not in seen: seen.add(k); dedup.append(r)
F["sensor_rows_raw"] = {"value": len(sw)}
F["sensor_rows_exact_duplicates_removed"] = {"value": len(sw) - len(dedup), "query": "identical full rows"}
F["sensor_rows_used"] = {"value": len(dedup)}
F["sensor_first_ts"] = {"value": dedup[0]["timestamp"]}; F["sensor_last_ts"] = {"value": dedup[-1]["timestamp"]}
for c in ["spindle_vibration_mm_s", "spindle_temp_c", "spindle_load_pct", "coolant_pressure_bar"]:
    v = [float(r[c]) for r in dedup]
    F[c] = {"first": v[0], "last": v[-1], "min": min(v), "max": max(v), "last_over_first": round(v[-1] / v[0], 2),
            "delta": round(v[-1] - v[0], 2), "series": v}
v = [float(r["spindle_vibration_mm_s"]) for r in dedup]
F["vibration_monotonic_nondecreasing"] = {"value": all(b >= a for a, b in zip(v, v[1:]))}
F["MW-140_vib_ratio_2.1_over_1.4"] = {"value": round(2.1 / 1.4, 2), "query": "values quoted in MW-140 note"}
from datetime import datetime
ts=[datetime.fromisoformat(r["timestamp"]) for r in dedup]
F["window_minutes"] = {"value": int((ts[-1]-ts[0]).total_seconds()//60), "query": "last minus first sensor timestamp"}
F["vib_rate_per_interval_mm_s_per_min"] = {"value": [round((v[i+1]-v[i])/((ts[i+1]-ts[i]).total_seconds()/60),3) for i in range(len(v)-1)], "query": "delta vib / delta minutes per consecutive sample"}
json.dump(F, open(out, "w"), indent=1)
for k, x in F.items(): print(k, {kk: vv for kk, vv in x.items() if kk != "series"})
