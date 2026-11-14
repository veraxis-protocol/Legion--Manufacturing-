"""Outbound document check (shared/secret-config.md) on the CUSTOMER QUOTE block alone, plus the date-gap figure.
Run from the work folder: python -I out/calc/outbound_check.py out/reply_quote-build_MB-2040.md out/calc/outbound_check.json"""
import json, re, sys
from datetime import date

text = open(sys.argv[1], encoding="utf-8").read()
start = text.index("=== CUSTOMER QUOTE — SENDABLE ===")
end = text.index("=== END ===", start)
block = text[start:end]
memo = open("inputs/rates_memo.txt", encoding="utf-8").read()
memo_numbers = sorted(set(re.findall(r"\b\d+(?:\.\d+)?\b", memo.split("\n", 1)[1])) - {"1", "2026"})
patterns = {
    "hours/time": r"\b(hours?|hrs?|min/pc|minutes?|cycle time|machine time|setup)\b",
    "rung/path/basis": r"\b(rung|routing|actuals?|CAM|feature path|geometry estimate|first principles|plant_library|estimator_entered|fusion_default|library defaults?|probable_standard|cost_down)\b",
    "variance/range": r"\b(variance|low|expected|high)\b",
    "margin (any form)": r"margin",
    "pricing rule": r"\b(default rule|customer-specific|discount tier|markup)\b",
    "PO / supplier": r"\bPO-\d+|Metals Supply|Bright Anodize",
    "path A method words": r"\b(ROM|rough order|text spec|path A)\b",
    "other customer names": r"\b(Example|MB-1880)\b",
}
hits = {k: sorted(set(m.group(0) for m in re.finditer(p, block, re.I))) for k, p in patterns.items()}
num_hits = [n for n in memo_numbers if re.search(r"(?<![\d.])%s(?![\d.])" % re.escape(n), block)]
result = {"block_chars": len(block), "hits": {k: v for k, v in hits.items() if v},
          "memo_rate_numbers_in_block": num_hits,
          "days_from_2026-11-14_to_2027-01-15": (date(2027, 1, 15) - date(2026, 11, 14)).days}
result["pass"] = not result["hits"] and not num_hits
json.dump(result, open(sys.argv[2], "w", encoding="utf-8"), indent=2)
print(json.dumps(result, indent=2))
