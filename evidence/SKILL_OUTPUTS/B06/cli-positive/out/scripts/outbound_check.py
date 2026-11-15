import re, sys
sys.stdout.reconfigure(encoding="utf-8")
t = open(sys.argv[1], encoding="utf-8").read()
m = re.search(r"=== CUSTOMER QUOTE — SENDABLE ===(.*?)=== END ===", t, re.S)
block = m.group(1)
terms = ["hour", " hrs", "setup", "set-up", "cycle", "machine time", "run time", "min/pc", "low", "expected", "high",
 "rung", "path", "routing", "actual", "cam", "feature", "geometry", "first principles", "plant_library", "estimator_entered",
 "fusion", "library", "variance", "probable_standard", "rate", "margin", "markup", "mark-up", "burden", "labour", "labor",
 "rom", "rough order", "text spec", "po-", "purchase order", "mb-1880", "bright anodize", "metals supply", "wo-", "cost_down",
 "cost-down", "default rule", "discount", "219", "212", "385", "%", "legion", "test estimator", "model"]
hits = [w for w in terms if re.search(r"(?<![a-z])" + re.escape(w), block.lower())]
names = set(re.findall(r"\b(?:Northwind Robotics|Example Precision Works)\b", block))
print("block chars:", len(block))
print("forbidden-term hits:", hits or "none")
print("company names in block:", sorted(names))
