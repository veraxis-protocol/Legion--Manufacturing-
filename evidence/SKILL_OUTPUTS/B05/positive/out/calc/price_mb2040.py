"""Priced buildup for MB-2040 from figures_MB-2040.json and the confirmed plant rates file.
Run from the work folder: python -I out/calc/price_mb2040.py out/calc/figures_MB-2040.json plant-setup/plant-rates.md out/calc/pricing_MB-2040.json"""
import json, re, sys

d = json.load(open(sys.argv[1], encoding="utf-8"))
rates_txt = open(sys.argv[2], encoding="utf-8").read()
lab = re.search(r"\*\*Labor rate:\*\* confirmed.*", rates_txt).group(0)
wc_rate = {k: float(v) for k, v in re.findall(r"(MILL-H|MILL-V|TURN|INSP) (\d+\.\d+)/hr", lab)}
margin = json.loads(re.search(r"\*\*Margin rules:\*\* confirmed `(\{.*?\})`", rates_txt).group(1))["default"]
mat_mu = float(re.search(r"material markup (\d+) percent", rates_txt).group(1)) / 100
osp_mu = float(re.search(r"anodize\) markup (\d+) percent", rates_txt).group(1)) / 100

F = []
def fig(name, value, how):
    F.append({"figure": name, "value": value, "arithmetic": how})

out = []
for b in d["breaks"]:
    q = b["qty"]
    conv = {}
    for wc, h in b["by_work_center"].items():
        conv[wc] = {"setup_usd": round(h["setup_h"] * wc_rate[wc], 2), "run_usd": round(h["run_h"] * wc_rate[wc], 2)}
    setup_usd = sum(v["setup_usd"] for v in conv.values())
    run_usd = sum(v["run_usd"] for v in conv.values())
    conv_usd = setup_usd + run_usd
    res = {"qty": q, "conversion_by_wc": conv, "setup_usd": round(setup_usd, 2), "setup_usd_per_pc": round(setup_usd / q, 4),
           "run_usd": round(run_usd, 2), "conversion_usd": round(conv_usd, 2), "cases": {}}
    for case, mat in (("27_per_plate_PRICED", b["material_usd_if_27"]), ("30_per_plate_alt", b["material_usd"])):
        osp = b["anodize_usd"]
        cost = mat + osp + conv_usd
        mat_up = mat * mat_mu; osp_up = osp * osp_mu
        conv_margin = conv_usd / (1 - margin) - conv_usd
        price = cost + mat_up + osp_up + conv_margin          # non-stacked reading (priced)
        stacked = (mat * (1 + mat_mu) + osp * (1 + osp_mu) + conv_usd) / (1 - margin)  # alternative reading
        flat = cost / (1 - margin)                             # margin only, no markups
        unit = round(price / q, 2)
        c = {"material_usd": mat, "anodize_usd": osp, "cost_usd": round(cost, 2), "cost_per_pc": round(cost / q, 4),
             "material_markup_usd": round(mat_up, 2), "osp_markup_usd": round(osp_up, 2), "margin_on_conversion_usd": round(conv_margin, 2),
             "uplift_total_usd": round(price - cost, 2), "price_usd": round(price, 2), "unit_price_usd": unit,
             "extended_at_rounded_unit": round(unit * q, 2), "uplift_share_of_price": round((price - cost) / price, 4),
             "alt_stacked_unit": round(stacked / q, 2), "alt_margin_only_unit": round(flat / q, 2)}
        res["cases"][case] = c
        for k in ("cost_usd", "material_markup_usd", "osp_markup_usd", "margin_on_conversion_usd", "unit_price_usd", "extended_at_rounded_unit", "alt_stacked_unit", "alt_margin_only_unit"):
            fig("Q%d %s %s" % (q, case, k), c[k], "see price_mb2040.py")
    for k in ("setup_usd", "setup_usd_per_pc", "run_usd", "conversion_usd"):
        fig("Q%d %s" % (q, k), res[k], "hours x work-centre rate")
    out.append(res)

json.dump({"rates_source": "plant-setup/plant-rates.md (confirmed 2026-11-14)", "margin_default": margin,
           "breaks": out, "figures": F}, open(sys.argv[3], "w", encoding="utf-8"), indent=2)
print(json.dumps(out, indent=1))
