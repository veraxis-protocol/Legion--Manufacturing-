# Outbound document check (shared/secret-config.md) on every delimited block in the continuation reply.
import re, sys, io
text = io.open(sys.argv[1], encoding="utf-8").read()
blocks = re.findall(r"^=== (SUPPLIER [^\n]*?) ===\n(.*?)^=== END ===", text, re.S | re.M)
suppliers = ["Alder", "Birch", "Cedar"]
fail = False
for head, body in blocks:
    addressee = next((s for s in suppliers if s in head), None)
    problems = []
    if re.search(r"PO-\d+", body) and "CORRECTIVE ACTION" not in head:
        problems.append("PO number")
    if re.search(r"[$€£]\s?\d|\bunit price\s*[:=]\s*\d", body, re.I):
        problems.append("price value")
    if re.search(r"margin|target price", body, re.I):
        problems.append("margin/target price")
    for s in suppliers:
        if s != addressee and s in body:
            problems.append("other supplier name: " + s)
    if "PACKAGE" in head and re.search(r"\b1,?000\b", body):
        problems.append("PO-history quantity")
    print(head, "->", "PASS" if not problems else "REJECT " + ", ".join(problems))
    fail |= bool(problems)
print("blocks checked:", len(blocks))
sys.exit(1 if fail else 0)
