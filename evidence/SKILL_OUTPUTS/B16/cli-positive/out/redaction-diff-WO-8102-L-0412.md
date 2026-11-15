# Redaction diff — internal 8D → customer pack, DRAFT-WO-8102-L-0412 (Gate 2: for quality-owner review)

> SYNTHETIC test data. **The quality owner approves this diff, not the clean customer version.** Nothing has been sent. Removal requests received: **none**, so there are no refusals to record.

## Changes made

| # | Location | Internal | Customer version | Why |
|---|---|---|---|---|
| 1 | Header | Approver name "Test Quality Owner (LEGION WO-LMFG-004 test operator)", approval date | Removed; contact left for the sender | Personnel |
| 2 | D1 | Named champion; "J. Ortiz, Inspector"; open role slots | Roles only | Personnel |
| 3 | Throughout | F-number citations to the internal figures block | Removed; the figures themselves are kept where stated | Figures block stays internal |
| 4 | D2, D4 | "VMC-03", "insert T7-0031 / T7-0032", "T7 head" | "the machine", "the boring insert", "the boring head" | Internal process detail — **owner's call**. The meaning is unchanged |
| 5 | D2 | "2nd shift"; "in-process data out of spec from part 1 at 15:10" | "in-process reading on the first part … already above the limit" (moved to D4) | Shift detail is internal; **the finding is kept** |
| 6 | D3 | "notification drafted, not sent; window not on file; at least 85.9 h elapsed" | Removed | Internal notification status |
| 7 | D3 | "ERP shipment check for any customer" for L-0411 | "shipment check in progress; we will tell you whether any reached you" | Other customers. No other customer name appears anywhere, internal or external |
| 8 | D3 | "Execution not confirmed in records" | "Action in place, confirmation pending" | Same meaning. **Reviewer: confirm this wording does not overstate.** If the holds are not physically in place, it must say so |
| 9 | D3 | MRB / anodize-masking / not recoverable by re-machining | "Disposition of held parts: pending" | Internal disposition reasoning |
| 10 | D4 table | Ranked table with For/Against and F-numbers; "shift-2 residual +1.20 µm, 3 of 3 on shift 2"; "coolant 6% → 8%" | Two tied candidates stated, the others listed; "a shift-related process factor"; "a coolant concentration change" | Personnel-adjacent (shift = one operator, F40) and process parameters. **The ranking and the tie are kept** |
| 11 | D4 | "A similar offset error happened before at the site" (NCR-0244, another part) | Removed | Unrelated finding from the history search |
| 12 | D4 | Interpolated USL crossing ≈13:48; trend rule fired 07:20, 7.83 h before | "rising trend about 8 hours before the first out-of-spec part" | Rounded, not softened. 7.83 h is stated as "about 8 hours" |
| 13 | D4 | "Wear normally makes a bore smaller" (physics note against NCR-0219's cause) | "The mechanism it assumed was not tested" | Internal engineering argument. **The substance is kept** |
| 14 | D4 | Verification test detail (presetter, offset export window, ERP pull of WO-8099–8101) | "examining the removed insert and the boring head setting, and the machine's tool-offset history" | Internal work orders and process detail |
| 15 | D5 | "Breaks link N" column; conditions ("after D4 test", "600 not carried forward") | "Addresses" column, in plain terms | Internal chain notation. The traceability to the root cause is kept |
| 16 | D7 item 6 | NCR log gets machine and material-lot fields | Removed | Internal quality-system housekeeping |
| 17 | D6, D8 | Placeholder tables | "Open" | Placeholders. Nothing pre-filled in either version |

## Kept on purpose (not redacted)

| Item | Why it stays |
|---|---|
| **NCR-0219 recurrence, 22.026 mm, and CAPA-071 "never verified as effective, did not prevent recurrence"** | Removing a recurrence is misrepresentation, not redaction |
| "At least 300" and L-0411 still open | The scope is printed as a floor everywhere. The open shipment check stays open |
| First-part reading above the limit and no stop | It is the detection failure. Removing it would soften the finding |
| **Shipment after an inspection hold and before final inspection was complete** | It is how the escape happened. Wording states only what is known; what the hold covered is still being established |
| All measurements, the requirement citation, dates, PS-5521 | Required content |

## For the reviewer to decide
- Row 4: whether to name the machine and insert IDs (some customers require them in 8D D4).
- Row 8: the D3 wording, given that hold execution is not confirmed in records.
- Whether to state the CAPA-071 replacement interval (600 parts) to the customer. It is currently omitted as internal detail; the recurrence itself is stated in full.

## Gate 2
Approval of this diff: **not given.** It is recorded with the reviewer's own name when they give it. Even after approval, the pack is handed to a person to send, and this session sends nothing.
