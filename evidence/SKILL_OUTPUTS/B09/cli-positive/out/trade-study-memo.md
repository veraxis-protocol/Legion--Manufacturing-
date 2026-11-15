# Trade Study Decision Memo: Motor Bracket Material and Process

**SYNTHETIC TEST DATA.** The plant, parts and sources are fictitious (WO-LMFG-004).
**Status:** DRAFT for engineering review. This memo recommends; the decision belongs to the engineer who signs it.
**Prepared by / approved by:** _not given (to be completed by the signing engineer)_
**Date:** 2026-11-15
**Format:** No plant trade-study template or prior study was on file, so this memo uses a plain neutral structure.
**Score basis (15 scores):** 6 analysis, 9 estimate, 0 judgment.
**Inputs:** `inputs/trade/trade_matrix.csv`, `inputs/trade/analysis_notes.md`

---

## 1. Recommendation

**Option A, 6061 machined.** It ranks first at the stated weights with 85.6/100 (B 78.3, C 70.0). It also stays first across every plausible weighting except those where unit cost carries roughly 45–50% or more of the weight, or where cost is about 40% and lead time is near zero.

## 2. Reasoning

- **A against B.** A is equal to or better than B on four of the five criteria: 24% cheaper per unit ($18.40 vs $24.10), 8 g lighter, and 3 days faster to first article. B's only advantage is 6 Hz of first-mode stiffness (418 vs 412 Hz, about 1.5%). Both clear the 350 Hz requirement by a wide margin (+68 and +62 Hz), and a 1.5% difference is probably inside FEA modelling uncertainty. B would win only if stiffness carried more than **87.7%** of the total weight.
- **A against C.** C's unit price is the lowest at $9.80, nearly half of A's. That earns C the full 30 points on cost, but it loses on everything else. Its 63-day first-article lead time is the main reason (4.8 of 20 points, against A's 20). The $14,500 die and a weaker stiffness margin (365 Hz) add to the gap.
- **Amortization check.** If the $14,500 die is spread over 1,000 pieces, C's effective unit cost is **$24.30**. That is above both A ($18.40) and B ($24.10). Folding tooling into cost this way widens A's lead to 99.6 vs 86.6 (B) vs 70.3 (C). Die casting is cheaper than A only above **about 1,690 pieces** ($14,500 / $8.60). Impregnation cost is not included, so the real break-even is higher.

## 3. Sensitivity finding

**The decision rests on the unit-cost weight, with lead time as the counterweight.**

| Question | Finding |
|---|---|
| Does the winner change? | Yes, in one direction only: A goes to C as cost weight rises. |
| Where does it flip? | Cost weight **47.5%** (other weights scaled in proportion). With lead time at 0%, A beats C by only 0.44 points, which is a tie. With cost at 40% and lead time at 0%, C wins by 1.45. |
| Most decision-sensitive criterion | **Unit cost** (it drives the A→C flip). **Lead time** is close behind: almost all of A's margin over C comes from it. |
| Criteria that never flip it | Tooling, mass and stiffness. Varying any of them from 0–100% never lets C overtake A. Stiffness only lets B overtake A above 87.7%. |
| Option that never wins in a plausible range | **B.** It wins only above 87.7% stiffness weight, and nobody would weight the study that way. |
| Within noise? | At the stated weights, no: A leads by 7.3 and 15.6 points. Two regimes are within noise: lead time dropped (0.44) and the unit-cost-only case with tooling dropped (0.91). |

Regime winners: stated **A**; equal weights **A**; performance-led **A**; schedule-led **A**; cost-led (50/10/20/10/10) **C**; unit cost only **A (tie with C)**; lead time dropped **A (tie with C)**; tooling amortized into cost **A**, with a wider lead. All figures are in `out/sensitivity-analysis.csv`.

**What this means for the review:** choosing A is the same as saying the first article in 15 days matters, or that volume stays below about 1,700 pieces. If the program is high-volume and schedule is not a factor, re-weight the study and look at C again. Do not simply carry A forward.

## 4. Constraint compliance

| Hard requirement | A | B | C |
|---|---|---|---|
| First mode > 350 Hz (FEA-2040-01..03, analysis_notes.md) | 412 Hz, pass (+62) | 418 Hz, pass (+68) | 365 Hz, pass (+15, 4.3%) |

**No option is disqualified.** That was the only hard requirement provided. If the bracket has other requirements (envelope, load cases, finish, certification), they were not part of the inputs and were not checked.

## 5. Ruled-out options

- **B, 7075 machined.** It never wins under any plausible weighting, so it is not a real alternative to A. Its 6 Hz stiffness edge costs $5.70 more per piece and 3 more days. Recommend dropping it.
- **C, A380 die cast.** It does not win at the stated weights. It does win when unit cost carries 47.5% or more of the weight, or about 40% cost with lead time near zero. It also becomes cheaper than A above about 1,690 pieces. It is ruled out for this decision but not dismissed; see the trigger in section 3.

## 6. Residual risks in Option A

1. **Unit cost is an estimate** (quote-build Q-118), not a firm supplier price. A 24% cost advantage over B is comfortable. Against C, the result depends on the cost weight.
2. **Lead time is a schedule estimate.** A's win over C depends heavily on the 15-day first-article lead time. If shop load pushes it out, the margin over C shrinks.
3. **Tooling is entered as $0 for A and B with no cited source.** Fixtures or soft jaws are probably not zero. Confirm this. A small fixture cost would barely affect A vs B, but under ratio normalization it would change how the tooling criterion scores.
4. **Production volume is not stated.** The matrix prices at 1,000 pieces. Above about 1,700 pieces over the program's life, machining A loses its cost case.
5. **The FEA boundary conditions are idealized:** fixed mounting face, with the 0.9 kg motor lumped at the bore centre. Mounting compliance in the real assembly will lower all three first-mode values. A has 62 Hz of margin, which is comfortable, but the result is still unverified by test.

## 7. Method notes and data findings

- **Weights** were 0.30 / 0.10 / 0.25 / 0.15 / 0.20, which sum to 1.00. Every option was scored on every criterion, so nothing was imputed.
- **Direction** was checked per criterion against the matrix `better` column. Lower is better for unit cost, tooling, mass and lead time. Higher is better for first-mode stiffness. Checked before totals were computed.
- **Normalization** is ratio: best ÷ value for lower-is-better and value ÷ best for higher-is-better. Min-max was not used because there are only three options.
- **Tooling caveat.** Ratio normalization with a best value of $0 makes the tooling criterion binary: A and B score 1.0, and C scores 0.0 whatever the die costs. The amortization check in section 2 addresses this, and the result holds or strengthens under it.
- **C's figures are optimistic in two ways.** Its unit cost leaves out impregnation for bore porosity (analysis_notes.md), and porosity is not modelled in the FEA. Correcting either would weaken C further, so neither changes the recommendation.
- **Not checked:** the volume requirement, other hard requirements, and supplier qualification for any option.

---

## Scored comparison (stated weights)

Ratio normalization. Each cell shows raw value → normalized score → contribution (normalized × weight × 100).

| Rank | Option | Unit cost @1k, 30%, lower | Tooling, 10%, lower | First mode, 25%, higher | Mass, 15%, lower | Lead time FA, 20%, lower | **Total** |
|---|---|---|---|---|---|---|---|
| 1 | A 6061 machined | $18.40 → 0.533 → **15.98** | $0 → 1.000 → **10.00** | 412 Hz → 0.986 → **24.64** | 198 g → 1.000 → **15.00** | 15 d → 1.000 → **20.00** | **85.62** |
| 2 | B 7075 machined | $24.10 → 0.407 → **12.20** | $0 → 1.000 → **10.00** | 418 Hz → 1.000 → **25.00** | 206 g → 0.961 → **14.42** | 18 d → 0.833 → **16.67** | **78.28** |
| 3 | C A380 die cast | $9.80 → 1.000 → **30.00** | $14,500 → 0.000 → **0.00** | 365 Hz → 0.873 → **21.83** | 221 g → 0.896 → **13.44** | 63 d → 0.238 → **4.76** | **70.03** |
| | Basis / source | estimate: quote-build Q-118/119/120 | estimate: die quote D-55 (C); A/B uncited | analysis: FEA-2040-01..03 | analysis: CAD mass properties | estimate: supplier/shop schedule | |

The per-cell table with sources is in `out/scored-comparison.csv`.
