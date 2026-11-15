import os, json, re, sys
from datetime import datetime
root = sys.argv[1]
bd = os.path.join(root, "inputs", "breakdown")
files = sorted(os.listdir(bd))
allf = []
for d, _, fs in os.walk(os.path.join(root, "inputs")):
    allf += [os.path.relpath(os.path.join(d, f), root).replace("\\", "/") for f in fs]
sensor = [f for f in allf if f.lower().endswith((".csv", ".xlsx", ".parquet")) or re.search(r"sensor|historian|vib|temp", f, re.I)]
maint = [f for f in allf if re.search(r"maint|cmms|work.?order|history|limble", f, re.I)]
photos = [f for f in allf if f.lower().endswith((".jpg", ".jpeg", ".png", ".heic"))]
ev = open(os.path.join(bd, "event.txt"), encoding="utf-8").read()
m = re.search(r"(\d{4}-\d{2}-\d{2} \d{2}:\d{2}) local", ev)
t0 = datetime.strptime(m.group(1), "%Y-%m-%d %H:%M")
m2 = re.search(r"still down at (\d{2}:\d{2})", ev)
t1 = datetime.strptime(m.group(1)[:10] + " " + m2.group(1), "%Y-%m-%d %H:%M")
mins = int((t1 - t0).total_seconds() // 60)
wo_hits = re.findall(r"\b(?:LMB|MWO|PM)-?\d+\b", ev)
out = {
 "input_files_enumerated": allf,
 "input_file_count": len(allf),
 "sensor_files": sensor, "sensor_file_count": len(sensor),
 "maintenance_files": maint, "maintenance_file_count": len(maint),
 "photo_files": photos, "photo_file_count": len(photos),
 "maintenance_records_this_asset": 0 if not maint else None,
 "sibling_records": 0 if not maint else None,
 "closeout_note_groups": 0 if not maint else None,
 "alarm_time_verbatim": m.group(0),
 "last_confirmed_down_verbatim": m2.group(0),
 "minutes_alarm_to_last_confirmed_down": mins,
 "maintenance_wo_refs_in_event_note": wo_hits,
}
print(json.dumps(out, indent=1))
