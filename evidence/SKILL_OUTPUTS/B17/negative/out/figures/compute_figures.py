"""Computes every figure the BSH-1210 / lot AS-7781 run states. Reads the inputs only."""
import re, json, statistics, sys, pathlib
base = pathlib.Path(sys.argv[1])
finding = (base / "incoming_finding.txt").read_text(encoding="utf-8")
drawing = (base / "BSH-1210_drawing_revA.md").read_text(encoding="utf-8")

# measurements as recorded
m = re.search(r"Hardness measured ([\d, ]+) HRF on (\d+) samples", finding)
vals = [int(v) for v in m.group(1).split(",")]
n_stated = int(m.group(2))
spec = re.search(r"Hardness (\d+)-(\d+) HRF", drawing)
lsl, usl = int(spec.group(1)), int(spec.group(2))
coc = int(re.search(r"C of C for lot AS-7781 states hardness (\d+) HRF", finding).group(1))
qty = re.search(r"qty ([\d,]+)\.", finding).group(1)
lot_qty = int(qty.replace(",", ""))
issued = int(re.search(r"(\d+) pcs already issued", finding).group(1))
quar = int(re.search(r"(\d+) pcs in receiving quarantine", finding).group(1))
prior_lots = re.findall(r"(AS-\d+) \((\d{4}-\d{2})\)", finding)

mean = statistics.mean(vals)
mrs = [abs(b - a) for a, b in zip(vals, vals[1:])]
mrbar = statistics.mean(mrs)
sigma = mrbar / 1.128
ucl, lcl = mean + 3 * sigma, mean - 3 * sigma
above_usl = sum(v > usl for v in vals)
below_lsl = sum(v < lsl for v in vals)
beyond_ucl = sum(v > ucl for v in vals); beyond_lcl = sum(v < lcl for v in vals)
# run rule: 7+ consecutive on one side of centreline (Nelson rule 2 variant) - only 5 points
sides = [1 if v > mean else (-1 if v < mean else 0) for v in vals]
longest = 1; cur = 1
for a, b in zip(sides, sides[1:]):
    cur = cur + 1 if (a == b and a != 0) else 1
    longest = max(longest, cur)

fig = {
 "samples_measured": len(vals), "samples_stated_in_finding": n_stated,
 "values_HRF": vals, "min_HRF": min(vals), "max_HRF": max(vals), "mean_HRF": mean,
 "spec_LSL_HRF": lsl, "spec_USL_HRF": usl,
 "samples_above_USL": above_usl, "samples_below_LSL": below_lsl,
 "fraction_samples_failing": f"{above_usl + below_lsl} of {len(vals)}",
 "min_minus_USL_HRF": min(vals) - usl, "mean_minus_USL_HRF": mean - usl,
 "mean_over_USL_ratio": round(mean / usl, 3),
 "coc_stated_HRF": coc, "mean_minus_coc_HRF": mean - coc, "coc_within_spec": lsl <= coc <= usl,
 "imr_centreline": mean, "moving_ranges": mrs, "mr_bar": mrbar,
 "sigma_est_mrbar_over_1.128": round(sigma, 3),
 "imr_UCL": round(ucl, 2), "imr_LCL": round(lcl, 2),
 "points_beyond_UCL": beyond_ucl, "points_beyond_LCL": beyond_lcl,
 "longest_run_one_side_of_centreline": longest,
 "lot_qty_received": lot_qty, "qty_issued_WO8150": issued, "qty_quarantine_Q1": quar,
 "issued_plus_quarantine": issued + quar, "reconciles_to_lot": issued + quar == lot_qty,
 "prior_lots_named": [l for l, _ in prior_lots], "prior_lots_count": len(prior_lots),
 "lots_with_incoming_hardness_failure": "1 of 3 (AS-7781); AS-7702 and AS-7744 recorded as passed, values not recorded",
}
print(json.dumps(fig, indent=1))
