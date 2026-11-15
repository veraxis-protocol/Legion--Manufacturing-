# 8D REPORT — CUSTOMER VERSION — DRAFT, HELD AT GATE 2 — NOT SENT

> SYNTHETIC test data. **Held for review of the redaction diff (`redaction-diff-WO-8102-L-0412.md`). Per this session's instruction, nothing goes to the customer.** Standard 8D structure; the customer's controlled template is not on file.

| Field | Value |
|---|---|
| Customer | Northwind Robotics |
| Part / rev | MB-1880 rev B |
| Our reference | DRAFT-WO-8102-L-0412 |
| Related prior report | NCR-0219 / CAPA-071 (April 2026) — **recurrence** |
| Status | D1–D5 and D7 drafted. D6 and D8 open |

## D1 — Team
Quality owner (champion); final inspection; manufacturing engineering; tooling/maintenance; production; shipping. Contact: [to be filled by the sender].

## D2 — Problem description
- **Defect:** Bore A diameter on MB-1880 rev B measured **22.034, 22.031 and 22.029 mm** against drawing MB-1880 rev B, sheet 2, note 4: **Ø22.000 +0.021/−0.000 mm**. That is 8–13 µm over the upper limit.
- **Lot and dates:** lot L-0412, produced 2026-11-10. Found at our final inspection on 2026-11-11, where 3 of 5 sampled parts were over the limit.
- **Suspect quantity: at least 300** (the whole of lot L-0412). An earlier lot, L-0411, is also suspect; we are establishing its quantity and whether any of it shipped to you.
- **Shipped to you:** 30 parts on packing slip PS-5521, 2026-11-11.
- **This is a recurrence.** The same oversize condition on the same bore was reported in NCR-0219 (April 2026, 22.026 mm). The corrective action from that event, a scheduled insert-replacement interval, was **never verified as effective**, and it did not prevent this recurrence.

## D3 — Interim containment

| Location | Qty | Action | Status |
|---|---|---|---|
| Installed in your product | not yet known | Please tell us whether any of the 30 have been installed or shipped on | Open — your input needed |
| At your site (PS-5521) | 30 | Please quarantine the receipt | Open |
| In transit | being confirmed | Carrier check / intercept if not delivered | Open |
| Work in process at our site | 120 | Held and tagged | Action in place, confirmation pending |
| Finished goods at our site | 150 | Quarantined and tagged | Action in place, confirmation pending |
| Earlier lot L-0411 | being established | Locate, hold, re-measure. Shipment check in progress | Open; we will tell you whether any reached you |
| Process | — | Cutting insert replaced 2026-11-11. The first part after the change measured 22.007 mm | Done |

Disposition of held parts: pending.

## D4 — Root cause (investigation in progress, not concluded)

**Occurrence.** The bore diameter rose steadily on every in-process reading while one boring insert was in use (10 consecutive readings over about two days). It dropped back to 22.007 mm when the insert was replaced. No other maintenance took place in that period. The cause is located in the condition of the boring tool, but **which mechanism** is responsible is not yet confirmed. Two candidates are currently equally supported:

1. The insert's cutting-edge condition (material build-up or edge damage) enlarged the cut.
2. The boring head's diameter setting moved outward in use and was reset when the insert was changed.

Less supported candidates still open:
- a tool-offset entry error
- a shift-related process factor
- a coolant concentration change made the day before the run
- measurement error, considered unlikely

**Verification under way:** we are examining the removed insert and the boring head setting, and the machine's tool-offset history, before anything is reset.

**Why it was not detected.**
- An in-process reading on the **first part** of lot L-0412 was already above the limit, and production was not stopped.
- In-process data showed a rising trend about 8 hours before the first out-of-spec part, and no trend rule was in place to flag it.
- The 30 parts shipped **after an inspection hold had been raised at our site and before final inspection of the lot was complete**. We are still establishing what that hold covered.

**Why the April 2026 corrective action did not hold:**
1. It was never verified as effective.
2. The mechanism it assumed was not tested.
3. Its replacement interval depended on manual counting that was not enforced.

## D5 — Corrective actions

| # | Action | Addresses |
|---|---|---|
| CA1 | Any in-process bore reading above the limit stops the machine, and every part since the last conforming reading is quarantined | Non-detection: no reaction to an out-of-spec reading |
| CA2 | Statistical process control with a trend rule on Bore A at the machine; a signal requires a tool check before production continues | Non-detection: drift not seen until out of spec |
| CA3 | Shipping interlock: no lot ships without completed final inspection, and none while a related hold is open | Escape: shipment after a hold and before final inspection |
| CA4 | Machine-enforced tool-life limit on the boring tool, at an interval validated by test | Root cause candidate 1 (tool run past usable life) |
| CA5 | Preset, lock-check and record the boring-head diameter at every insert change | Root cause candidate 2 (head setting movement) |
| CA6 | Insert grade and coolant review for this aluminium alloy, if material build-up is confirmed | Root cause candidate 1 (edge build-up) |

## D6 — Implementation and verification
Open. To be completed with implementation dates and verification results.

## D7 — Prevent recurrence
1. Corrective actions are not closed without a data-based effectiveness check. This is the failure behind the April 2026 recurrence.
2. The root-cause mechanism is confirmed by test before corrective actions are approved.
3. Tool-life limits that come from a nonconformance are enforced by the machine, site-wide.
4. Control plan update: characteristics with a nonconformance history get in-process SPC with a written reaction plan.
5. Inspection holds are linked to shipping release.

## D8 — Closure
Open.
