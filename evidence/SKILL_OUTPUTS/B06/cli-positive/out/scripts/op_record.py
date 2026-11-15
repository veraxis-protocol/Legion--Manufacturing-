import json, csv, sys
from datetime import date
d = json.load(open("out/figures.json"))
days = (date(2027,1,15) - date(2026,11,15)).days
with open("out/dataset/figures_block.csv", "a", newline="", encoding="utf-8") as f:
    csv.writer(f).writerow(["Calendar days to requested FAI date", days, "intake required_delivery", "2027-01-15 - 2026-11-15"])
rows = []
for o in d["ops"]:
    rows.append({"part":"MB-2040","revision_priced_to":"C (spec sheet; no drawing)","op_seq":o["op"],"work_center":o["work_center"],
      "machine_class":o["work_center"],"rung":4,"path":"first principles: similar-part MB-1880 rev B","cutting_data_basis":"n/a",
      "setup_h_low_exp_high":"/".join(map(str,o["setup_h"])),"run_min_pc_low_exp_high":"/".join(map(str,o["run_min_pc"])),
      "quantity_breaks":"250/500/1000","sources":o["basis"],"geometry_estimate":"geometry-estimate_MB-2040_L1.txt (hand_entered, draft)",
      "date_derived":"2026-11-15"})
for op, desc in [("50","Anodize OSP - no machine time"),("60","Laser mark OSP - not timed"),("70","FAI/final inspect - not timed")]:
    rows.append({"part":"MB-2040","revision_priced_to":"C (spec sheet; no drawing)","op_seq":op,"work_center":"outside" if op!="70" else "INSP","machine_class":"","rung":"","path":desc,"cutting_data_basis":"n/a","setup_h_low_exp_high":"","run_min_pc_low_exp_high":"","quantity_breaks":"250/500/1000","sources":"","geometry_estimate":"draft","date_derived":"2026-11-15"})
w = csv.DictWriter(open("out/operation-record_Q-NORTHWIND-MB2040-01.csv","w",newline="",encoding="utf-8"), fieldnames=list(rows[0]))
w.writeheader(); w.writerows(rows)
print("days", days, "op rows", len(rows))
