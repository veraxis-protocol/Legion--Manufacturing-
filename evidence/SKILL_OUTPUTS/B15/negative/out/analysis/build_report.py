import json, sys, html
from pathlib import Path
out = Path(sys.argv[1])
rows = json.loads((out / "analysis" / "figures.json").read_text(encoding="utf-8"))
t = ["<table><tr><th>Figure</th><th>Value</th><th>Computed from</th><th>Filter or query</th></tr>"]
for r in rows:
    t.append("<tr>" + "".join(f"<td{' class=\"n\"' if k=='value' else ''}>{html.escape(str(r[k]))}</td>" for k in ("figure","value","computed_from","filter_or_query")) + "</tr>")
t.append("</table>")
tpl = (out / "analysis" / "report_template.html").read_text(encoding="utf-8")
(out / "MB-1880_root_cause_investigation_DRAFT.html").write_text(tpl.replace("{{FIGURES}}", "\n".join(t)), encoding="utf-8")
print("ok", len(rows), "figures")
