# 8D REPORT — INTERNAL DRAFT — DRAFT-WO-8102-L-0412

> SYNTHETIC test data, fictitious plant. Site EPW1 (test). The plant's or customer's controlled 8D template is **not on file**, so the standard eight-discipline structure is used. **INTERNAL:** this version carries personnel, machine and process detail and the history search. The customer version is `8D-CUSTOMER-PACK-DRAFT-WO-8102-L-0412.md`, and the changes are in `redaction-diff-WO-8102-L-0412.md`. Figures are quoted as F-numbers from `analysis/figures_block.md`.

| Field | Value |
|---|---|
| Part / rev | MB-1880 rev B |
| Customer | Northwind Robotics |
| NCR | DRAFT-WO-8102-L-0412 (approved 2026-11-15, Test Quality Owner) |
| Prior related | NCR-0219 / CAPA-071 — **recurrence: the previous fix did not hold** |
| 8D status | D1–D5 and D7 drafted. D6 and D8 are open placeholders |

## D1 — Team (proposed; the owner edits)

| Role | Name |
|---|---|
| Champion / quality owner | Test Quality Owner (LEGION WO-LMFG-004 test operator) |
| Finder, final inspection | J. Ortiz, Inspector |
| Manufacturing engineer, VMC-03 bore operation | _to assign_ |
| Tooling / maintenance (T7 boring head, presetter) | _to assign_ |
| Production lead, shifts 1 and 2 | _to assign_ |
| Shipping / logistics (release control) | _to assign_ |

## D2 — Problem description

- **What:** Bore A on MB-1880 rev B is oversize: 22.034, 22.031 and 22.029 mm against **Ø22.000 +0.021/−0.000 mm** (drawing MB-1880 rev B, sheet 2, note 4). That is 8–13 µm over the upper limit (F7–F9).
- **Where:** VMC-03, bore operation, insert T7-0031.
- **When:** Lot L-0412 / WO-8102 was produced on 2nd shift, 2026-11-10. In-process data has it out of spec from part 1 at 15:10 (F6). Final inspection found it at 2026-11-11 10:05 (−05:00 assumed).
- **How found:** Final inspection sample, 3 of 5 above the limit (F55).
- **How many:** **at least 300** suspect. That is all of L-0412, plus an uncounted tail of L-0411 / WO-8101, whose last reading was 22.019, 2 µm under the limit (F30).
- **Escaped:** 30 parts shipped to Northwind Robotics on PS-5521, 2026-11-11 08:00.
- **Recurrence:** NCR-0219 (2026-04-14) was the same part and the same characteristic, at 22.026. CAPA-071's effectiveness was never verified.

## D3 — Interim containment

| Location | Qty | Action | Status |
|---|---|---|---|
| Installed at Northwind | **not checked** | Ask Northwind whether any are installed or shipped on | Open |
| At Northwind (PS-5521) | 30 shipped, delivery not confirmed | Request quarantine of the receipt | Open. Notification drafted, **not sent**; the contractual window is not on file, and at least 85.9 h had elapsed by 2026-11-15 (F58) |
| In transit | **not checked** | Carrier check / intercept | Open |
| WIP, VMC-03 queue | 120 | Hold and tag | Action stated. **Execution not confirmed in records** |
| Finished goods, FG-2 rack 14 | 150 | Quarantine and tag | Action stated. **Execution not confirmed in records** |
| L-0411 / WO-8101, all locations | **not checked** | Locate, hold, re-measure Bore A. Run the ERP shipment check for any customer | Open. `escape_possible` |
| Source | — | Insert T7-0031 replaced by T7-0032 at 2026-11-11 06:40. The first part after it read 22.007 (F34) | Done (maintenance log) |

Disposition of the held parts stays with MRB. Bore A is masked at anodize and an oversize bore cannot be recovered by re-machining; disposition is MRB's decision, not this draft's.

## D4 — Root cause (ranked candidates; not concluded)

**Occurrence: where the change sits is clear, the mechanism is not.** The bore rose on 9 of 9 consecutive readings on T7-0031 (F12), r = 0.936 against time (F23), and stepped −27 µm at the insert change (F35). No other maintenance event happened in the window (F47).

| Rank | Candidate chain | Strongest For | Strongest Against | Status |
|---|---|---|---|---|
| 1= | T7-0031 cutting-edge condition (built-up edge on 6061 or edge damage) → effective radius grows → USL crossed ≈13:48 on 11-10 (F29) | Monotone rise and reset at the change (F12, F35); same symptom in NCR-0219 | Normal flank wear makes a bore *smaller*; the insert has not been examined; **the "ran past life" link is unproven**, because the floor of 510 parts is below 600 (F59) | **Tied** |
| 1= | Boring head / cartridge setting creeps outward → reset when the insert was changed | Explains the −27 µm reset equally well | No presetter or setup record; no direct evidence for the first link | **Tied** |
| 3 | T7 wear offset entered with the wrong sign or size | A similar offset error happened before at the site | The growth is smooth, not stepwise (F12); no offset record | Weak |
| 4 | Shift-2 practice factor | 3 of 3 out-of-spec readings on shift 2 (F37); residual +1.20 µm (F42) | n = 5 per shift; confounded with operator and tool age (F40); L-0410 on shift 2 drifted normally (F25) | Weak; a pattern, not a person |
| 5 | Coolant 6% → 8% (11-08) promoting built-up edge | The only prior process change (F45) | The new insert at 8% read 22.007 (F34) | Contributor at most |
| 6 | Gage error | Gage ID and calibration not recorded | The readings reset at a tool change, which a gage error would not do (F34) | Unlikely |

**Verification test, which settles the tie:** pull insert T7-0031 and the T7 head, and inspect them before anyone re-sets them:
- inspect the edge under magnification
- read the head on the presetter
- export the VMC-03 T7 offset history for 2026-11-09 07:10 → 2026-11-11 06:40
- pull the WO-8099–8101 quantities

**Escape point: why it was not detected or contained.**
`in-process reading 22.022 on part 1 of L-0412 (F6)` → `no stop or reaction` → `full lot produced` → `30 shipped 80 min after an "inspection hold" was raised (F56) and 125 min before final inspection completed (F57)`.

- A trend rule would have signalled at 2026-11-10 07:20, **7.83 h before** the first out-of-spec part (F19, F21).
- Open: whether the in-process export is real-time, and what the 06:40 hold covered.

**Why CAPA-071 did not hold:**
1. Its effectiveness was never verified.
2. Its mechanism, "insert wear causes oversize", was never tested. Wear normally makes a bore smaller.
3. It relied on a part-count interval that nothing recorded here enforces or evidences.

## D5 — Chosen corrective actions (each names the link it breaks)

| # | Action | Breaks | Condition |
|---|---|---|---|
| CA1 | Reaction plan at VMC-03 for Bore A: any in-process reading above 22.021 stops the machine and quarantines every part made since the last conforming reading | Escape chain, link 2: "no stop / reaction triggered" | Unconditional |
| CA2 | Individuals chart with the six-increasing-points trend rule on Bore A, plotted at the machine; a signal requires a tool check before continuing | Escape chain, link 1→2: a drift seen only once out of spec | Unconditional. Sampling frequency and reaction limit to be set from a capability study, **not** set here |
| CA3 | Shipping release interlock: no lot ships without a completed final-inspection record, and none while a hold is open on that part number or machine | Escape chain, link 4: "shipped after hold, before final inspection" | Unconditional |
| CA4 | Machine-enforced tool-life counter on T7 (CNC tool-life management), with a hard stop at a validated interval | Candidate 1, link 3: "insert ran past usable life" | Interval set **after** the D4 test and a drift-versus-count study. 600 is not carried forward unverified |
| CA5 | At every T7 insert change: preset the head, torque-check and record the lock, record the set diameter | Candidate 2, link 1: "adjustment not locked" | Applies if the D4 test confirms Candidate 2. Kept as a precaution regardless |
| CA6 | Insert grade/geometry for 6061 (polished, sharp edge for aluminium) and coolant-concentration window review | Candidate 1, link 1 (built-up edge) and Candidate 5 | Only if the D4 test finds built-up edge |

Moved out of D5:
- Inspecting T7-0031, the offset export and the ERP quantity pull are D4 verification.
- Holds, quarantine and the Northwind notification are D3.

## D6 — Implement and verify (PLACEHOLDER: needs real-world outcome)

| Action | Implemented by | Date implemented | Verification method | Verification result | Verified by | Date |
|---|---|---|---|---|---|---|
| CA1 | | | | | | |
| CA2 | | | | | | |
| CA3 | | | | | | |
| CA4 | | | | | | |
| CA5 | | | | | | |
| CA6 | | | | | | |

Effectiveness check (date not committed): ______

## D7 — Prevent recurrence (system level)

1. **No CAPA closes without an effectiveness check.** CAPA-071 sat at "not verified" and the defect came back. CAPA closure in the quality system requires a verification record with data, and an open CAPA with no check by its due date is escalated. *This addresses why CAPA-071 did not hold.*
2. **The mechanism is confirmed before the corrective action is approved.** CAPA-071 acted on "insert wear causes oversize" without a test. Physically, wear points the other way. A D4 test record is required before D5 sign-off.
3. **Life limits are enforced by the machine, not by counting.** Every tool life limit that exists because of an NCR moves into CNC tool-life management. Applies site-wide, not only to T7.
4. **Control plan and PFMEA update.** Any characteristic with a prior NCR is given in-process SPC with a trend rule and a written reaction plan. Bore A on MB-1880 is the first case.
5. **Hold-to-shipping linkage.** Inspection holds are visible to and enforced in shipping release, so a hold on a machine or part blocks shipment of the related lots.
6. **History searchable by machine and supplier.** The NCR log gains machine and material-lot fields. This search could not run this time (F51).

## D8 — Close and recognize (PLACEHOLDER: needs human sign-off)

| Field | Value |
|---|---|
| Closure approved by | |
| Date | |
| Customer acceptance (if required) | |
| Team recognized | |
| Lessons learned recorded at | |
