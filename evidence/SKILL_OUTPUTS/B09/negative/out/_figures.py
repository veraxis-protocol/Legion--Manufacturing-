import json, re, pathlib
root = pathlib.Path(r"C:/LMFG/runs/B09-negative/work/inputs")
files = sorted(p for p in root.rglob("*") if p.is_file())
matrix_like = [p for p in files if p.suffix.lower() in {".xlsx",".xls",".csv",".docx",".json",".yaml",".yml"}]
manifest = [p for p in files if "manifest" in p.name.lower()]
notes = (root/"trade"/"analysis_notes.md").read_text(encoding="utf-8")
body = "\n".join(l for l in notes.splitlines() if not l.startswith("<!--"))
fea_ids = re.findall(r"FEA-\d{4}-\d{2}(?:\.\.\d{2})?", body)
m = re.search(r"FEA-(\d{4})-(\d{2})\.\.(\d{2})", body)
fea_count = int(m.group(3)) - int(m.group(2)) + 1 if m else 0
options_named = sorted(set(re.findall(r"Option ([A-Z])", body)))
hz_results = re.findall(r"(\d+(?:\.\d+)?)\s*Hz", body)
weights = re.findall(r"\d+\s*%", body)
fig = {
 "input_files_total": len(files),
 "input_files": [str(p) for p in files],
 "matrix_like_files (xlsx/xls/csv/docx/json/yaml)": len(matrix_like),
 "variant_manifest_files": len(manifest),
 "fea_ids_referenced": fea_ids, "fea_runs_in_range": fea_count,
 "options_named_in_notes": options_named,
 "Hz_values_in_notes": hz_results,
 "percent_weights_in_notes": weights,
}
print(json.dumps(fig, indent=1))
json.dump(fig, open(r"C:/LMFG/runs/B09-negative/work/out/figures.json","w"), indent=1)
