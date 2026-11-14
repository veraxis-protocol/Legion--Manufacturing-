# WO-LMFG-003 — ZTL Engineer integration (WO-D02): status

Branch `dev/wo-lmfg-001-phase-a`, started at `eb45ea5`. The evidence in `evidence/` was produced at code commit
`27a207d` on Linux (WSL Ubuntu 24.04, Python 3.12.3, real reBot STEP, OpenCascade 8.0.1.1). CI run
[43537122368](https://github.com/veraxis-protocol/Legion--Manufacturing-/actions/runs/43537122368) on the same
commit passed 10/10 jobs and published the same counts as public annotations.

**Gate D02: T.** All 22 acceptance obligations PASS. This gate is about the integration only. **It is not an engineering
admission.** The real reBot engineering verdict is **Z**, and nothing authorizes procurement, payment or a
manufacturing release.

## The route that now runs

STEP → OpenCascade XCAF → BOM → sourced requirements (`legion/engineering/step_intake.py`, Deal-Rescue
`cad_xcaf` / `cad027_review` @`6d5563a`) → ZTL brick (Deal-Rescue `rail_length_brick`, or a ztl-stand example) →
**ZTL Engineer MCP** (`_deps/ztl-engineer/mcp_server.py`, stdio JSON-RPC, tool `check_design`) → **ZTL Stand**
(`python -m ustand.stand`) → **the stand's independent checker** (`python -m ustand.stand <brick> --dev`) → scoped
predicate verdict → strict aggregation → receipt layer (Deal-Rescue `ztl_gate`, Ed25519, CAD-025) → production layer
(Deal-Rescue `admission.decide`).

New code in this repository: `legion/engineering/ztl_adapter.py` (the adapter), `tools/ztl_pins.py`,
`tools/d02_run.py`, `tests/engineering/d02_common.py`, `tests/engineering/test_d02_*.py` (4 files), the
`engineering-verifier` CI job and `requirements-ztl.txt`. `step_intake.py` gained an optional verifier stage, and
`pinned_source.py` a generic pinned-repository materializer. No CAD parser, BOM extractor, solver, prover or checker was
written. Deal-Rescue, ztl-engineer, ztl-stand and ZTL were not modified.

### Findings that shaped the adapter

1. **The MCP tool runs the stand in work mode.** In that mode the independent checker does not gate an EARNED: the
   stand itself reports "checker: not run (work mode ...)". So LEGION maps a stand result to T or F only when three
   things agree: the MCP result, the pinned judge identity, and the stand's own `--dev` run of the same brick, which
   runs the checker. Anything else is Z (`confirmed_verdict`).
2. **The judge identity was wrong at first.** `ustand/judge_ztl.ztl_commit()` asks git for the commit of
   `USTAND_ZTL`. A plain copy of ZTL made it report this repository's HEAD (`ZTL eb45ea5`). `_deps/<name>` is now a
   sparse git checkout of the pinned commit, and the stand reports `ZTL 2ba7c20`. A judge that differs from the pin
   is Z (`VERIFIER_IDENTITY_MISMATCH`).
3. **Deal-Rescue's `ztl_review` combines only the predicates that got a verdict.** One EARNED plus one OPEN predicate
   gives `production_verdict = EARNED`; this was demonstrated on the pinned function and is recorded in
   `ENGINEERING_NEGATIVES.json`. LEGION does not use that rule for any global decision. Its own `aggregate` returns F
   if any mandatory predicate is F. It returns T only when every mandatory predicate is T, every proof is still valid,
   no context field is missing and an authenticated receipt exists. In every other case it returns Z.
4. **ZTL Stand imports `numpy` when it loads.** Without numpy the MCP server dies before answering. In CI run
   43529671557 every D02 call therefore came back Z and the D02 tests failed, as they should. The unit-test job now
   installs `requirements-ztl.txt`, and a server that exits without answering is reported as `MCP_SERVER_EXITED` (Z).

## Results (evidence at `27a207d`)

| Area | Result |
|---|---|
| Pinned sources | ztl-engineer `91d11672` (14 files, Apache-2.0); ztl-stand `0b4d718f` (1987 files, Apache-2.0 OR MIT); ZTL `2ba7c209` (171 files, Apache-2.0 OR MIT). Every file is checked as the git object at the pin and as the bytes on disk (blob SHA-1, size, SHA-256). Nothing changed after use. |
| MCP server | `initialize` OK; serverInfo `ztl-engineer 0.1`; tools `brick_format`, `check_design`, `ask_engineer`. `ask_engineer` is never called. |
| Real ZTL calls (evidence run) | **14** `check_design` calls reached the stand: **7 EARNED, 4 REFUTED, 3 BRICK ERROR**, plus 1 call the MCP server rejected before the stand. The independent checker (`--dev`) ran 11 times and agreed every time. |
| ztl-stand examples | divider 1 % / req 1 % EARNED → T; divider 1 % / req 0.5 % REFUTED → F; t1 heatsink EARNED → T; t6 truss EARNED → T. Deal-Rescue's own `check_design` gives the same verdict and judge. |
| ztl-stand's own suite (`tests/test_stand.py`) | **437 OK, 3 BLOCKED, 0 other failures.** The 3 BLOCKED are the stand's optional `--prove` feature, which writes Lean theorems and checks them with `lake`. No Lean toolchain is installed, and neither `check_design` nor this WO uses that feature. They are BLOCKED only if every failing check is a `--prove` check and `lake` is absent; any other failure makes the suite FAIL. |
| Controlled positive (D02-04) | Real reBot STEP rail length (XCAF) against the readme spec `MGN9-170mm`, with a tolerance window of ±0.02 mm. The window is an identified assumption (Deal-Rescue `TEST_ONLY_TOL`), not a reBot source. Stand result EARNED (`dL` guaranteed [0, 0]); the checker agrees; LEGION verdict **scoped T**, `admissible_for_rebot: false`. |
| Controlled negative (D02-05) | The same model with the spec deliberately changed to `MGN9-150mm`. Stand result REFUTED with `dL = 20` mm at the violating point; the checker agrees; LEGION verdict **scoped F**. |
| Real reBot case (D02-18) | Intake T: SHA-256 `a1e301ee…`, 40/40 mandatory BOM positions, 53/53 mandatory instances. Mandatory predicates: `cad_bom_extraction` T; `rail_length_tolerance` Z (no tolerance stated for the purchased rail; the CNC tolerance is not applied to it); `joint2_load_torque` Z; `cnc_material_evidence` Z (no certificates). No reBot predicate was sent to the stand on invented values. **Engineering verdict Z.** Receipt layer Z (`PART_FIELD_MISSING_MATERIAL_GRADE`). Production admission Z. |
| Negatives | 18/18 PASS. Missing tolerance → Z. Missing material → Z. Altered source SHA-256 → binding rejected. Changed revision, requirement digest, policy or brick → old proof invalid. Malformed bricks → BRICK ERROR → Z. 6 labelled TRANSPORT_FAULT_INJECTION replies → Z. Server missing → `MCP_UNAVAILABLE` (Z). Server dying at start → `MCP_SERVER_EXITED` (Z). Timeout → `MCP_TIMEOUT` (Z). T + Z → global Z, even with a claimed receipt. T + F → global F. Unsigned receipt, local stand JSON or garbage as a receipt → not admitted. Signed receipts replayed from an old epoch, after expiry, onto a changed spec or with an untrusted key → refused. A fresh test-signed receipt is accepted at the receipt layer only, as a positive control (key generated in memory per run). |
| Regressions | D01 CAD 13/13 PASS on the real STEP. Skills, connectors and upstream: 290 tests, 268 PASS, 0 FAIL, 20 NOT RUN, 2 BLOCKED, all unchanged from WO-LMFG-002. Anthropic upstream 94/94 byte-identical. |
| Protected repositories | 6/6 unchanged (Deal-Rescue, Commerce, Marketplace, Federation, Formal-Core, ztl-engineer); 0 modified. ztl-stand and ZTL are listed as third-party pins (informational). |
| Evidence manifest | `evidence/SHA256SUMS` verified before the run; it also covers `manifests/ZTL_SOURCE_PINS.json`. |

### The 22 obligations

| ID | Condition | Required | Status |
|---|---|---|---|
| D02-01 | Pinned ZTL source integrity | PASS | PASS |
| D02-02 | Real MCP initializes | PASS | PASS |
| D02-03 | Real `check_design` executes (and the stand's own suite passes) | PASS | PASS (3 `--prove` self-checks BLOCKED, listed) |
| D02-04 | Fully supported positive predicate | Scoped T | PASS (fixture and real STEP) |
| D02-05 | Violated engineering predicate | Scoped F | PASS (fixture and real STEP) |
| D02-06 | Missing manufacturing tolerance | Z | PASS |
| D02-07 | Missing material evidence | Z | PASS |
| D02-08 | Altered source SHA-256 | Reject binding | PASS |
| D02-09 | Changed engineering revision | Old proof invalid | PASS |
| D02-10 | Altered requirement digest | Old proof invalid | PASS |
| D02-11 | Malformed ZTL brick | Z | PASS |
| D02-12 | Malformed MCP response | Z | PASS (TRANSPORT_FAULT_INJECTION, labelled) |
| D02-13 | MCP server unavailable | Z | PASS |
| D02-14 | Verification timeout | Z | PASS |
| D02-15 | One mandatory T, one mandatory Z | Global Z | PASS |
| D02-16 | One mandatory T, one mandatory F | Global F | PASS |
| D02-17 | Replayed or unauthenticated receipt | No admission | PASS |
| D02-18 | Real reBot reference case | Engineering Z | PASS |
| D02-19 | Existing CAD-D01 regression | No regression | PASS |
| D02-20 | Existing Anthropic and connector tests | No regression | PASS |
| D02-21 | Protected repositories | No modifications | PASS |
| D02-22 | Evidence manifest and source hashes | Verified | PASS |

## CI history of this WO (successful and unsuccessful attempts)

| Run | Commit | Conclusion | What it showed |
|---|---|---|---|
| [43529671557](https://github.com/veraxis-protocol/Legion--Manufacturing-/actions/runs/43529671557) | `7354432` | failure | The unit-test venv had no numpy, so the real MCP server died on import and every D02 call was Z (tests failed, correctly). `SHA256SUMS` was stale for the changed pin files. |
| [43529761118](https://github.com/veraxis-protocol/Legion--Manufacturing-/actions/runs/43529761118) | `8ec589f` | failure | Same two causes. |
| [43530119179](https://github.com/veraxis-protocol/Legion--Manufacturing-/actions/runs/43530119179) | `7b49413` | success, **gate wrong** | Published `gate_d02=T` while the stand's own suite had stopped early: a `redteam/decks` file was missing, and the suite was not tied to any obligation. |
| [43532495774](https://github.com/veraxis-protocol/Legion--Manufacturing-/actions/runs/43532495774) | `9208e18` | success, gate wrong | Same gap (fixed in the next commit). |
| [43532574497](https://github.com/veraxis-protocol/Legion--Manufacturing-/actions/runs/43532574497) | `e9b0c51` | failure (correct) | D02-03 now requires the stand's own suite: 3 `--prove` (Lean) failures, so `gate_d02=F`. |
| [43537122368](https://github.com/veraxis-protocol/Legion--Manufacturing-/actions/runs/43537122368) | `27a207d` | **success** | `gate_d02=T`, 22/22; stand suite 437 OK with 3 BLOCKED (published as public warnings). |

Earlier local Linux runs found two problems before CI did. The stand's suite stopped on a missing deck (now pinned).
Three self-checks also failed because the WSL setup used `PYTHONPATH`, which the stand's sub-suites replace (now a
venv `.pth`; CI was never affected).

## What remains (engineering T for reBot is not available from the current sources)

The blocking list is computed in `D02_GO_NO_GO.json`, field `remaining_obligations_for_engineering_T`:

- a manufacturer length tolerance for the purchased MGN9-170 rail (a datasheet);
- arm self-weight and centre of mass, the joint-2 motor and its rated torque, and the joint-2 axis position;
- material grade certificates for the CNC parts;
- a drawing revision (the package is a STEP model and a readme, with no drawing);
- a configured independent ZTL attestation service: Ed25519 key, key id, epoch, policy SHA-256 and stand commit
  (Deal-Rescue `ztl_gate`, CAD-025). A local MCP process is not an authenticated verifier.

**Optional:** a Lean 4 toolchain would let the stand's 3 `--prove` self-checks run; they are not needed for this route.

The Phase A pull request is still not opened: there is no `gh` CLI and no GitHub sign-in in this environment. It can
be opened at <https://github.com/veraxis-protocol/Legion--Manufacturing-/pull/new/dev/wo-lmfg-001-phase-a>.

## Not done, by instruction

No change to LEGION-Deal-Rescue, ztl-engineer, ztl-stand or ZTL. No supplier order, PayPal call or website change. No
Claude plugin distribution. No Marketplace, Federation or Formal-Core code. No paid model API: `ask_engineer` is never
called, and no Meta, NVIDIA or Anthropic credential is used.
