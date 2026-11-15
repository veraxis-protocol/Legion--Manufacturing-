# NCR writeup: MB-1880 rev B, lot L-0412 (SYNTHETIC)

This is the reply text the ncr-writeup skill would print in full. No Word copy this session: no Word writer available (python-docx not installed, and installing it is not allowed). The structured records are saved in `NCR-record.yaml` and `register-row.yaml` next to this file.

**Status: BLOCKED. No requirement located.** This NCR cannot go final, and root-cause-capa cannot start, until someone cites the MB-1880 rev B main bore requirement.

**Escape: 30 parts shipped to Northwind Robotics** on 2026-11-11 08:00 (PS-5521), about two hours before the finding. The contractual notification window is unknown. The finding is dated 3 days before this run, so any 24–48 h window may already have run out.

**Data note:** there is no inspection export, no consolidated dataset, no ERP and no quality library. Every quantity and location below comes from the inspector's free-text note (`inputs/finding.txt`) and is unverified. The request says "this morning's final inspection", but the note is dated 2026-11-11 10:05 and this run is 2026-11-14. Please confirm which inspection this is.

Controlled NCR template: not on file (no plant profile). A neutral structure covering the four questions is used below.

---

## 1. Identification

| Field | Value |
|---|---|
| NCR number | Not assigned. The plant needs to issue one |
| Site | Not given |
| Part / revision | MB-1880 rev B |
| Production work order | WO-8102 |
| Lot | L-0412 (lot size 300) |
| Where made | VMC-03, 2nd shift, 2026-11-10 |
| Found at | Final inspection |
| Found by | J. Ortiz, inspector |
| Found at (time) | 2026-11-11 10:05. **Time zone not recorded** |
| Disposition | Pending |
| Approval | Draft. Not approved |

## 2. Condition found

Main bore diameter measured **22.034, 22.031 and 22.029 mm** on 3 of 5 sampled parts.

- The values for the other 2 sampled parts were not recorded.
- The gage was not recorded, so its calibration status could not be checked.
- The inspector believes these are oversize. However, the drawing was not at the bench. Until a requirement is cited, these are measurements, not an established nonconformance.

Quantity found: 3 each (the three high readings out of a sample of 5).

## 3. Requirement violated: NOT LOCATED (blocking)

I could not find a requirement for the main bore diameter on MB-1880 rev B.

What I searched:
- `inputs/finding.txt`. It says the drawing was not at the bench and the requirement has not been looked up.
- `inputs/prior_ncrs.csv`. NCR-0219 on the same part records "bore oversize 22.026" but gives no requirement, document or limit.

Not available this run: the MB-1880 drawing at rev B, internal specs, the Northwind Robotics PO flow-down, and the quality document library.

I have not inferred a limit. In particular, I did not take one from NCR-0219's 22.026 reading. **This NCR is blocked until someone cites the document, the locator, the characteristic and the stated value at rev B.** The quickest lead is the requirement NCR-0219 was written against. That NCR's own record should cite it. Check that the citation is at rev B.

## 4. Suspect quantity: at least 300

**Scope basis:** lot. Traceability is incomplete.

**Reasoning:**
- All 300 parts of lot L-0412 (WO-8102) were machined on VMC-03 on one shift, and 3 of 5 parts in the sample read high on the same bore. So the whole lot is suspect until it is sorted.
- The suspected mechanism, going by NCR-0219, is boring insert wear. That kind of wear builds up gradually and does not stop at a lot boundary.
- Any other lot or work order run on VMC-03 on the same insert, before or after this lot, is therefore also suspect.
- No insert-change record and no VMC-03 production log was available to put limits on that window. **At least 300** is a floor, not a ceiling.

## 5. Where the parts are, and containment (ordered by urgency; owners blank)

| Location | Suspect qty | Action | Urgency | Owner | Source |
|---|---|---|---|---|---|
| Installed at customer (Northwind Robotics) | **not checked** | Ask Northwind Robotics whether any of the 30 on PS-5521 have been installed or shipped on | immediate | | Not visible in our records |
| At customer (Northwind Robotics) | 30 reported shipped, **delivery not verified** | Confirm delivery of PS-5521. If delivered, ask Northwind Robotics to quarantine the receipt | immediate | | Inspector note; no ERP shipment record read |
| In transit | **not checked**: these are the same 30 if PS-5521 has not been delivered yet | If PS-5521 has not arrived, stop it at the carrier | immediate | | No ERP shipment record read |
| WIP at machine (VMC-03 queue) | 120 reported, **not verified** | Hold the parts and tag them with the NCR number. Stop further operations on them. Check whether VMC-03 is still running on the same insert | immediate | | Inspector note; no inventory/production_output |
| Finished goods (FG-2 rack 14) | 150 reported, **not verified** | Move the parts to quarantine, tag them and block them from picking | same day | | Inspector note; no inventory tab |

The reported quantities add up to the lot: 30 + 120 + 150 = 300. None of the five locations has been confirmed against a system record. Parts from other VMC-03 lots on the same insert have not been located, because those lots have not been identified.

## 6. Has this happened before? Yes. The earlier fix has not been shown to hold.

| Prior record | Date | Match | Did the fix hold? |
|---|---|---|---|
| NCR-0219 | 2026-04-14 | Same part (MB-1880) and same defect: bore oversize, measured 22.026. Cause: boring insert wear beyond 900 parts | **No (provisional).** CAPA-071 set an insert change every 600 parts, but its effectiveness is recorded as "not verified", and the same defect is now reported on the same part |
| NCR-0244 | 2026-08-02 | Not a match: different part (MB-1500) and different defect (slot width undersize). Machine not recorded, so a same-process match cannot be judged | n/a |

**Finding:** this is a recurrence on MB-1880 after CAPA-071. That CAPA was never verified as effective.
- The "failed" judgment depends on the cited requirement confirming that lot L-0412 is nonconforming.
- It is also not known whether the 600-part insert change was ever actually put into practice on VMC-03.
- The search covered only the 2 records in `inputs/prior_ncrs.csv`, not the plant's full quality library.
- NCR-0219's part label could not be cross-checked against the ERP.

## 7. Escape notification: DRAFT, not sent; sending is the quality owner's decision

> **Notification deadline: UNKNOWN.** The contractual window with Northwind Robotics is not recorded in the inputs and has not been guessed. Shipment was 2026-11-11 08:00, and the finding was recorded at 2026-11-11 10:05.
>
> To: Northwind Robotics, quality contact [to be filled]
> Subject: Suspect nonconformance: MB-1880 rev B, lot L-0412, packing slip PS-5521
>
> We are notifying you of a suspected nonconformance on parts shipped to you.
>
> - Part: MB-1880 rev B, lot L-0412, 30 pieces shipped 2026-11-11 on packing slip PS-5521.
> - Issue: at our final inspection, the main bore measured 22.029 to 22.034 mm on 3 of 5 sampled parts from the same lot. We are confirming these readings against the drawing requirement for the main bore [requirement to be cited before sending].
> - What we ask: please quarantine the 30 parts received on PS-5521. Please also tell us whether any have been installed or shipped on.
> - What we are doing: the rest of the lot is on hold at our site, and we are investigating the cause.
> - Next update from us: [date/time to be filled by the quality owner].
> - Our reference: NCR [number to be assigned].

Before sending, the shipment check in the containment table needs to be done and the requirement needs to be cited.

## 8. Quality Register: offered in the conversation, not published

*Tracks NCRs run through this plugin since [date unknown: the register was not reachable this run]. Not your full quality library.*

This page shows this NCR only. The other rows could not be read, so no open count is given.

| record_key | status | approval_state | containment_summary | escape_clock | recurrence | previous_fix_held |
|---|---|---|---|---|---|---|
| UNKNOWN_UNASSIGNED | blocked (no locatable requirement) | draft | 5 of 5 addressed; none verified; installed at customer not checked | window unknown | recurrence_prior_capa_failed | false |

**The Quality Register was not updated:** the artifact tools are not allowed in this run. The row is saved in `register-row.yaml`, marked not stored.

## 9. Questions for the plant (recorded instead of asked)

1. Where is the MB-1880 rev B drawing, or the spec or PO clause, that controls the main bore diameter, and what is the locator and stated value? (This is the block.)
2. What NCR number and site should this carry?
3. Is this the 2026-11-11 10:05 inspection? The request says "this morning", but today is 2026-11-14.
4. What time zone is the 10:05 timestamp in?
5. What gage measured the bore, and is its calibration current? What did the other 2 sampled parts read?
6. Has PS-5521 been delivered to Northwind Robotics? Where are Northwind's notification terms (the contractual window) recorded?
7. Has any of lot L-0412 been installed at Northwind?
8. When was the boring insert on VMC-03 last changed, and what other lots or work orders ran on it? Was CAPA-071's 600-part change ever in effect on VMC-03?
9. Can someone walk the VMC-03 queue and FG-2 rack 14 and confirm the 120 and 150?
10. Who owns each containment action, and who should be recorded as approving this NCR?
