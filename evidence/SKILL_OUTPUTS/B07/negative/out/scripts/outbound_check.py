"""Outbound document check: reads each delimited SENDABLE/HELD block alone and rejects forbidden content."""
import re, os
OUT = r"C:/LMFG/runs/B07-negative/work/out"
EV = "SRC-2026-11-14-BSH-1210"
text = open(os.path.join(OUT, "RUN_OUTPUT_supplier-quote-request.md"), encoding="utf-8").read()
blocks = re.findall(r"^(=== (SUPPLIER [^=]+?) ===)\n(.*?)^=== END ===", text, flags=re.S | re.M)
suppliers = ["Alder", "Birch"]
price_pat = re.compile(r"\b\d+\.\d{2}\b|USD|\$|1,850|\bPO[- ]?\d|target price|margin", re.I)
lines = []
for hdr, name, body in blocks:
    issues = []
    m = price_pat.findall(body)
    if m: issues.append(f"price/PO/margin pattern: {sorted(set(m))}")
    for s in suppliers:
        if s.lower() in body.lower() and s.lower() not in name.lower():
            issues.append(f"names other supplier {s}")
    if re.search(r"other (bid|supplier|quote)s?|competit", body, re.I) and "bidders" not in body:
        issues.append("mentions other bids")
    lines.append(f"{name}: {'PASS' if not issues else 'REJECT ' + '; '.join(issues)}")
lines.append(f"blocks checked: {len(blocks)}")
open(os.path.join(OUT, "sourcing", EV, "outbound_check.txt"), "w", encoding="utf-8").write("\n".join(lines) + "\n")
print("\n".join(lines))
