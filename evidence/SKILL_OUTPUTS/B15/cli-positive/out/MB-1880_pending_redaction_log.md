# MB-1880 — Pending redaction log (customer pack for Northwind Robotics)

Status (updated 2026-11-15): NCR DRAFT-WO-8102-L-0412 is now approved, so the customer pack is **unblocked but not built**. Nobody has requested it, and this is a test run where nothing goes to a customer. When it is built, this log becomes its redaction diff, and the quality owner approves that diff before anything leaves.

## Planned removals (internal 8D → customer version)
| Location | Internal | Customer version | Why |
|---|---|---|---|
| D1, D3, §2 | Inspector name; operator codes OP-11 / OP-23 | Roles only ("final inspection", "2nd shift") | Personnel |
| §5 | NCR-0244 (MB-1500, slot width) | removed | Unrelated finding |
| §3 | Rack locations (FG-2 rack 14), queue location | "finished goods", "in-process at the machine" | Internal process detail |
| §4 C3 / §5 | SPC limits, wear rates, insert IDs | Kept in summary form: trend and step change stated with their values | Internal detail. Quality owner decides how much SPC detail the customer gets |

## Must stay in (not redactable)
- The requirement, the measurements (up to 22.034 against 22.021 max), and the scope of **at least 300** plus the unquantified L-0411 tail.
- **The recurrence:** NCR-0219 in 2026-04 on the same characteristic, and the fact that CAPA-071 did not hold. Removing either would be misrepresentation.
- D4 uncertainty: C1 and C2 are tied pending the discriminating test.

## Removal requests received
None so far. Any request is recorded here, including refused ones, with who asked, what, the decision and why.

Approval of the diff: quality owner (name to be given). Not approved.
