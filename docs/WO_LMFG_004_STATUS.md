# WO-LMFG-004 — LEGION Manufacturing E2E Activation: status

Status: **overall GO/NO-GO = Z** (evidence/WO_LMFG_004_GO_NO_GO.json: 8 T, 0 F, 5 Z). Every remaining Z is an external dependency (Fusion, Microsoft 365, NetSuite, Infor M3). Not complete under WO §14.
Update 2026-11-15: the Claude Code CLI is signed in; all 16 runnable skills were re-run through the standalone CLI with
plugin discovery (criterion 1 → T). See §2.
Branch `dev/wo-lmfg-001-phase-a`. Every figure below is taken from a committed evidence file; nothing here is a
projection.

## 1. Manufacturing workflow readiness

All 17 original Claude for Manufacturing skills (upstream `plugins/claude-for-manufacturing` @099387b7, 94 files,
byte-identical — `tools/upstream_manifest.py verify` PASS) were executed by a real Claude model on labelled synthetic
inputs (`tests/runtime/inputs/`, every file headed SYNTHETIC) and the existing labelled fixtures.

| | Result |
|---|---|
| Skills executed (positive case) | 17/17 |
| PASS (deterministic checks **and** independent evaluator PASS, no fabrication) | 16 |
| BLOCKED (required live system absent) | 1 — B08 design-space-explore: no Autodesk Fusion. The skill stopped and named what it needs; evaluator PASS on that behaviour |
| FAIL | 0 (B05 attempt 1 = FAIL is kept: `evidence/SKILL_OUTPUTS/B05/attempt1`) |
| Missing-evidence (negative) cases | 16/16 PASS (B08 has no negative case: it cannot run without Fusion) |

Per run (`evidence/SKILL_OUTPUTS/<case>/<variant>/run.json`): the task prompt, input file hashes, model id, the
SKILL.md files the model read, every tool call with its actual response, token usage, the output files with SHA-256,
the deterministic checks, and the independent evaluator's verdict. Transcripts are committed redacted (message
content only) as `transcript.jsonl.gz` / `evaluator.jsonl.gz`.

How a run is judged (`tools/skill_run.py`):
- **Activation**: the model must read the case's original `SKILL.md` (and, for chains, the chained skills' instructions).
- **Deterministic checks** from the case (`tests/runtime/cases.json`): required facts present, fabricated values absent
  (regex on values that are not in the inputs), no web/MCP/messaging tool, inputs and plugin copy unchanged.
- **Independent evaluator**: a separate Claude session with read-only tools grades the work product against the
  skill's own SKILL.md, recomputes the arithmetic and lists any fabrication. PASS needs both.

Gate decisions: B06, B15, B16, B17 correctly stopped at their skills' human approval gates. A second turn supplied
the gate decisions from a named **test operator** ("LEGION WO-LMFG-004 test operator"); B05 attempt 2 received a
test-operator confirmation that the finance memo is the plant's rates. These answers are in the transcripts. Nothing
was sent, released, ordered or written to any external system in any run.

Known limits of the evidence: one run per case (no variance); `duration_s` of runs that were paused by the model
usage limit includes the pause (B05, B06, E02, E03); no XLSX/DOCX outputs (openpyxl and python-docx are not installed
and installing was not permitted), so skills wrote CSV/HTML/Markdown and said so.

### Integrated E2E (evidence/MANUFACTURING_E2E.json — PASS, 17/17 handoff checks)

| Stage | Executor | Result |
|---|---|---|
| RFQ (synthetic, labelled) | input | `tests/runtime/inputs/e2e/rfq_rebot_email.txt` |
| Intake | Claude, customer-inquiry-intake (E01) | PASS (evaluator PASS); tolerances recorded missing |
| Drawing/BOM | LEGION, real reBot B601 STEP → OpenCascade XCAF (Deal-Rescue cad_xcaf) | BOM T, 40/40 positions, 53/53 instances, 21 CNC parts |
| Engineering review | LEGION → real ZTL Engineer MCP → ZTL Stand → checker | reBot verdict **Z** (rail tolerance, joint-2 load, material evidence missing); controlled cases T / F |
| Cost estimate | Claude, quote-build (E02) on the intake + BOM handoff | PASS; material lower bound from named POs; hours and price unknown (no rates on file) |
| Supplier RFQ + comparison | Claude, supplier-quote-request (E03) on two SUPPLIED TEST quotes | PASS; not ranked (freight bases differ, accuracy class unstated) |
| Coalition | LEGION, Deal-Rescue `industrial/core.py` @6d5563a (pinned, verified) | 5 × 20 = 100 meets MOQ 100 — demonstration only; same buyers treated as real → Z; duplicate buyer rejected; 4 × 20 fails MOQ |
| Coalition proposal | `legion.industrial.federation-proposal.v1` (shape from core.run_case) | not admitted, external_effects 0 |
| Marketplace / Federation | — | **BLOCKED**: PolyForm-NC source, no commercial authorisation |

No buyer is real, no supplier quote is real, no order or payment exists.

### A/B baseline (evidence/BASELINE_COMPARISON.json — both runs evaluator PASS)

Same task and inputs (RFQ, reBot readme, the 34.8 MB STEP, POs, rates memo, two supplied rail quotes, coalition
demand). A = original plugin only (case HA). B = same plugin + LEGION's engineering and coalition artifacts (case HB).
Scored by `tools/baseline_compare.py` against the engineering ground truth.

| Metric | A original | B LEGION | |
|---|---|---|---|
| CNC parts named (of 21) | 21 | 21 | no difference |
| STEP file opened by a tool | yes | yes | no difference |
| STEP verification evidence (OpenCascade XCAF, 40/40 positions, 53/53 instances) | no — counted the STEP as text with its own script | yes | **difference** |
| Open engineering requirements named (rail length tolerance, joint-2 load/torque, material grade/certificates) | 1/3 | 3/3 | **difference** |
| Tolerances presented as fact (not in the inputs) | 0 | 0 | no difference |
| MOQ answered / buyer reliance correctly qualified | yes / yes | yes / yes | no difference |
| Independent evaluator | PASS | PASS | no difference |

Measured LEGION capability: CAD-kernel-verified BOM evidence and the engineering gaps found by the real ZTL review.
Not claimed: better BOM coverage (A matched 21/21 and 31 pieces per arm on its own), better cost accuracy (neither
priced: both stopped at the rfq-to-quote gates with no rates on file), or a better coalition answer (both said the
pooled 100 cannot be relied on). Limits: one run per configuration, same model.

## 2. Claude runtime readiness

| Item | Status |
|---|---|
| Claude Code CLI | installed, 2.1.325 (desktop-managed install under `%LOCALAPPDATA%\Claude-Data`) |
| CLI sign-in | **PASS** (2026-11-15, owner signed in in a non-recorded `cmd` window) — `claude auth status`: loggedIn true, authMethod claude.ai, apiProvider firstParty |
| Plugin discovery via `claude -p --plugin-dir` | **PASS** — 16/16 runnable skills (route 1, `evidence/SKILL_OUTPUTS/<case>/cli-positive/`) |
| Model-driven execution (route 2) | **PASS**: subagents of the signed-in desktop session, `claude-opus-5-5`, plugin loaded by path (`<case>/positive|negative/`). Kept as separate evidence; not labelled CLI executions. |

### Route 1: standalone Claude Code CLI (evidence/CLAUDE_RUNTIME.json `cli_runs`)

Each run: `claude -p <task> --plugin-dir <byte-identical plugin copy> --restricted --strict-mcp-config
--permission-mode dontAsk` with a tool allow-list (Read/Write/Edit/Glob/Grep/Skill/Bash; web, curl/wget, pip, git,
ssh, PowerShell denied). Every `ANTHROPIC_*`/`CLAUDE*` variable of the host desktop session is removed, so the CLI can
only use its own sign-in. In every run the CLI listed all 17 manufacturing skills from `--plugin-dir` and the model
entered the case's skill through the **Skill tool** (plugin discovery, not a path given in the prompt).

| | Result |
|---|---|
| Positive cases through the CLI | 16/16 PASS (B08 not run: Fusion absent) — model `claude-opus-5-5` |
| Gated skills (B06, B15, B16, B17) | stopped at their approval gates; the named test operator's decision was given as a resumed second turn (`--resume`), same text as route 2 (`operator_turn` in cases.json) |
| Independent evaluator | B01–B05: Claude Code CLI (claude-opus-5-5, read-only tools). B06–B17: **NVIDIA NIM `nvidia/nemotron-3.5-lightning-30b-a3b`** (owner decision 2026-11-15, to save Claude usage; a different model family, no tools, SKILL.md + inputs + outputs in the prompt, nothing truncated except B10's two largest inputs at 30 000 chars) |
| Negative cases | not re-run on route 1 (16/16 PASS on route 2) |

Harness corrections made during route 1 (each recorded in the run where it applied): the 8.3 short temp path
(`ADMINI~1`) made the CLI treat `./out` as outside its working directory (Write denied) → long path; a prefix-only
Bash allow-list denied ordinary shell loops (B11 could not run its engine) → Bash allowed with network/install/VCS
commands denied; the Pro "5-hour limit" message was not recognised (B13–B17 first recorded FAIL in 1–6 s) → detected
as BLOCKED and re-run; chained-skill reads by `cat` were not counted on route 1 (B13 false FAIL) → same detection as
route 2, checks recomputed from the recorded tool calls (`--recheck`, no model call); NIM reasoning used up the
output budget on B06/B10/B11 (no verdict) → larger budget with a no-reasoning fallback, re-judged (`--re-evaluate`).
Known limit: NIM is a weaker judge than Opus; one NIM verdict (B10) returned the template text as its notes.

Earlier sign-in diagnosis (2026-11-14, no credential value read or shown): there is one Windows account
(`Administrator`); no `.credentials.json` under `C:\Users\Administrator\.claude` (checked inside and outside the
sandbox); no Claude entry in Windows Credential Manager; no `CLAUDE_CONFIG_DIR` override (user or machine); no
credential in the desktop package folder; no CLI in WSL. The desktop app authenticates its own sessions through a
host proxy that the standalone CLI cannot use. Conclusion: the `claude auth login` flow did not complete on this
account (the browser step finishes, but the code is never returned to the CLI), so no CLI credential was stored. It is
not a second account or store. Unblock: complete `claude auth login` in a non-recorded terminal until
`claude auth status` shows loggedIn true, then `python tools/skill_run.py B04` runs route 1. Resolved 2026-11-15 (see above).

## 3. Enterprise connector readiness

All four BLOCKED (evidence/*_LIVE.json, `tools/live_probe.py`; contract suites 51/51 PASS are contract tests only):

| System | Exact blocker |
|---|---|
| Microsoft 365 | no Microsoft 365 connector in the Claude runtime; `LMFG_M365_*` not provided |
| Autodesk Fusion | not installed; nothing answers `http://127.0.0.1:27182/mcp` (from the plugin's `.mcp.json`) |
| Oracle NetSuite | no NetSuite connector; `LMFG_NETSUITE_*` not provided |
| Infor M3 | no M3 MCP server URL/token (`LMFG_M3_*`) for an authorised tenant |

No mock was used to satisfy any live criterion.

## 4. Overall WO-LMFG-004 status

13 criteria (WO §14), from `tools/wo004_gate.py`:

| # | Criterion | Verdict |
|---|---|---|
| 1 | Real Claude runtime demonstrated | T (standalone CLI, plugin discovery via `--plugin-dir`, 16/16 PASS) |
| 2 | All 17 skills executed in their required environments | Z (16 PASS, B08 BLOCKED on Fusion) |
| 3 | All skill outputs independently evaluated | T |
| 4–7 | Microsoft 365 / Fusion / NetSuite / Infor M3 live | Z ×4 (BLOCKED) |
| 8 | Integrated E2E workflow | T |
| 9 | Measured LEGION capability beyond baseline | T (2 measured differences, 5 equal metrics) |
| 10 | No critical regressions | T — CI run 43774729539 on 683d41c green 11/11 (skills 198 PASS / 0 FAIL / 20 NOT RUN / 2 BLOCKED; connectors 51/51; D01; D02 incl. ztl-stand suite; runtime 6/6; upstream 94/94) |
| 11 | No unauthorised consequential actions | T |
| 12 | GitHub CI PASS on the final commit | T — https://github.com/veraxis-protocol/Legion--Manufacturing-/actions/runs/43774729539 (683d41c); the evidence-only follow-up commit is re-verified by its own run |
| 13 | Reproducible evidence published | T — evidence/SHA256SUMS + EVIDENCE_MANIFEST.json (31 files) verified in CI; every skill output hash-checked by the runtime-evidence job |

Protected repository modifications: 0 (Deal-Rescue, ZTL repos, Marketplace, Federation, Commerce, Formal-Core read only).

## Remaining work (external / owner)

1. Autodesk Fusion desktop with its MCP add-in and an authorised reference design (B08 and WO §6).
2. Authorised Microsoft 365, NetSuite and Infor M3 tenants (read-only), provided through a protected environment.
3. Commercial authorisation for LEGION Marketplace / Federation (PolyForm-NC) before the coalition proposal can be
   admitted.
