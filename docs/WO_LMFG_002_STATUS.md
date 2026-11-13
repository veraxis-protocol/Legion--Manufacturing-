# WO-LMFG-002 status: manufacturing capability activation

Format per WO-LMFG-001 section 15. **PASS** means a test ran and its assertion held. **NOT RUN** and **BLOCKED** are
never counted as PASS: NOT RUN marks a model-driven step that needs the Claude runtime; BLOCKED marks a step that
needs a live external system that is not available here.

## Item 1: Phase A pull request

**BLOCKED.** No `gh` CLI on this host, the browser pane is not signed in to GitHub, and reading stored git credentials
to call the API was refused earlier in this engagement and was not retried. Work continues on the existing branch
`dev/wo-lmfg-001-phase-a`, as the WO allows. Compare link for the owner:
https://github.com/veraxis-protocol/Legion--Manufacturing-/pull/new/dev/wo-lmfg-001-phase-a

## Item 2: skill classification (17/17)

Each classification is bound to a sentence in the skill's own SKILL.md (`manufacturing/runtime/catalog.py`; the
quote must be found or `test_4_provenance` fails). Three independent axes:

- **File-capable:** 12 skills run from supplied files with no connector, as their Degradation sections state; 3 more
  are chains of file-capable skills. A missing ERP degrades them; it does not block them.
- **Live system required:** 2. `custom-connector` needs the target system to test against; `design-space-explore`
  "cannot generate variants" without Fusion desktop.
- **Claude runtime:** all 17. The reasoning steps are Markdown instructions executed by Claude. A model-driven run is
  **NOT RUN** here: no Claude runtime or model credential is used, and no model output is claimed from a fixture.

| ID | Skill | Mode | Upstream code executed | File-only (SKILL.md) | Live system required | PASS | FAIL | NOT RUN | BLOCKED |
|---|---|---|---|---|---|---|---|---|---|
| C01 | `onboarding` | FILE_CAPABLE | plant_setup.py find, render, install, stamp | yes, line 3 | - | 13 | 0 | 1 | 0 |
| C02 | `custom-connector` | LIVE_SYSTEM_REQUIRED | plant_setup.py find | no | the target system | 11 | 0 | 1 | 1 |
| C03 | `data-consolidate` | FILE_CAPABLE | plant_setup.py find | yes, line 67 | - | 14 | 0 | 1 | 0 |
| C04 | `customer-inquiry-intake` | FILE_CAPABLE | plant_setup.py find | yes, line 356 | - | 12 | 0 | 1 | 0 |
| C05 | `quote-build` | FILE_CAPABLE | plant_setup.py find | yes, line 446 | - | 12 | 0 | 1 | 0 |
| C06 | `rfq-to-quote` | FILE_CAPABLE | plant_setup.py find | yes, line 296 | - | 11 | 0 | 1 | 0 |
| C07 | `supplier-quote-request` | FILE_CAPABLE | plant_setup.py find | yes, line 362 | - | 11 | 0 | 1 | 0 |
| C08 | `design-space-explore` | LIVE_SYSTEM_REQUIRED | - | no | Fusion desktop, base model open | 10 | 0 | 1 | 1 |
| C09 | `trade-study-report` | FILE_CAPABLE | plant_setup.py find | yes, line 4 | - | 11 | 0 | 2 | 0 |
| C10 | `daily-production-report` | FILE_CAPABLE | plant_setup.py find (+ pulse engine, Chain 3) | yes, line 449 | - | 13 | 0 | 1 | 0 |
| C11 | `morning-plant-pulse` | FILE_CAPABLE | plant_setup.py find, pulse_compute.py, render_short.py | yes, line 331 | - | 13 | 0 | 1 | 0 |
| C12 | `breakdown-diagnosis` | FILE_CAPABLE | plant_setup.py find | yes, line 316 | - | 11 | 0 | 2 | 0 |
| C13 | `breakdown-to-next-report` | FILE_CAPABLE_CHAIN | via member skills | yes, line 177 | - | 11 | 0 | 1 | 0 |
| C14 | `ncr-writeup` | FILE_CAPABLE | plant_setup.py find | yes, line 333 | - | 13 | 0 | 1 | 0 |
| C15 | `root-cause-capa` | FILE_CAPABLE | plant_setup.py find | yes, line 350 | - | 11 | 0 | 2 | 0 |
| C16 | `inspection-to-capa` | FILE_CAPABLE_CHAIN | via member skills | yes, line 153 | - | 10 | 0 | 1 | 0 |
| C17 | `supplier-escape-to-alternate-source` | FILE_CAPABLE_CHAIN | via member skills | yes, line 171 | - | 11 | 0 | 1 | 0 |
| | **Total (Windows local, commit df0f8b6; Linux CI identical)** | | | | | **198** | **0** | **20** | **2** |

The NOT RUN rows: 17 model-driven runs, plus C09 sensitivity reproducibility, C12 cause ranking and C15 pattern checks,
which are computed by the Claude-run skill.

## Item 3: what actually executed, per skill

Every suite runs the six WO classes: positive, negative input, missing data, source provenance, approval and security
boundary, and regression against the Phase A manifest.

- **Upstream code, unchanged, from a copy in a task folder:**
  - `plant_setup.py find` runs for the 13 skills that call it, against a profile assembled from the upstream
    `config-profile.md` blocks (line ranges recorded). It is also run from inside the plugin folder, where the
    script must refuse.
  - `render`, `install` and `stamp` run for onboarding. The profile persists across task folders through
    `CLAUDE_PLUGIN_DATA`, and `render` refuses a rate value or an email address.
  - `pulse_compute.py` and `render_short.py` run on two labelled synthetic export drops. The plugin tree digest is
    checked unchanged after every run.
- **C10 OEE reconciliation.** The upstream engine computes availability 0.9549, performance 0.8679, quality 0.9852,
  OEE 0.8165 and downtime $130 at a 120/h rate. An independent recomputation from the fixture with the `oee.md`
  definitions agrees to 3 decimals. Scrap is reported unpriced because no standard cost exists, never as zero.
- **C11 stale data.** A day with no data produces no day record, and the engine names the gap.
- **Handoffs through the upstream contracts.** All 9 contracts with record examples are checked, and every complete
  worked example is accepted unchanged.
  - Out-of-contract values and a removed Required field give BLOCK, naming the field.
  - A Degrades field gives DEGRADED and is never filled.
- **Consumer gates.** 16 "Blocks" rows are encoded from five contracts, and each row's text must be found in the
  upstream file. They give Z for:
  - a draft or declined geometry estimate, or one with foreign geometry
  - an unapproved or revision-less supplier-caused flag
  - an NCR with no requirement, or an unapproved NCR used for anything customer-facing
  - a declined or superseded inquiry
  - an unknown safety flag

## Item 4: WO-B05 connector contract compatibility

`manufacturing/contracts/upstream.py` and `manufacturing/adapters/envelope.py` do not replace Anthropic's schema:
the record is carried unchanged, and LEGION adds bindings, scope and verification beside it. Tests:
`tests/connectors/test_b05_envelope.py`, 7 PASS.

| B05 acceptance | Result |
|---|---|
| Four connector contract suites pass | B01 11, B02 8, B03 11, B04 14: 44/44 PASS |
| Tenant isolation | PASS (wrap and combine refuse mixed tenants; adapters refuse cross-tenant responses) |
| Source references survive normalization | PASS (bindings and verbatim keys survive; any change to a wrapped record is detected) |
| Permission scope survives every transformation | PASS (scope is the intersection of the inputs; a write scope cannot be created) |
| No missing field silently filled | PASS |
| Disconnected systems do not produce false success | PASS (any state other than VERIFIED gives UNAVAILABLE with no record) |

## Item 5: LEGION CAD/STEP integration (WO-D01)

- **Pinned reuse.** Deal-Rescue `deal_rescue/industrial` (cad_xcaf, cad_bom, cad027_review, ztl_gate, pmix_adapter) is
  read at `6d5563af` from git objects. Each file must match its git blob SHA-1, size and SHA-256
  (`legion/engineering/DEAL_RESCUE_PIN.json`). The files go into git-ignored `_deps/` and are not copied or modified.
- **License.** Apache-2.0, per Deal-Rescue's own PROVENANCE_AND_LICENSE.md at that commit.
- **Pipeline.** STEP → XCAF → BOM against the factory readme → requirements (material and tolerance only where the
  readme states them) → verification Z. Each CNC part becomes a draft path-C1 `geometry-estimate` inside a B05
  envelope; the contract check never gives BLOCK, and the gate gives Z until Gate 3.

| Test | Windows local | Linux CI (real reBot STEP) |
|---|---|---|
| Offline: pins verified, tampered pin refused, BOM T/F on Deal-Rescue's own fixture, materials and tolerances only from sources, revision and missing requirements recorded, C1 handoff valid, STL/IGES/STEP-as-drawing/path-traversal give Z, samples reproduce 20 x SLS-BRACKET-REV-C | 9 PASS | 9 PASS |
| D01-T01/T02 real STEP hash and XCAF structure (33 assemblies, 64 definitions, 326 instances, mm) | NOT RUN (no OCP locally) | PASS |
| D01-T03/T08 BOM 40/40 positions, 53/53 instances, 27 purchased rows | NOT RUN | PASS |
| D01-T04..T06 requirements, revision, handoff on the real part list | NOT RUN | PASS |
| D01-T07 tampered STEP is F; unreadable STEP is Z with no estimate | NOT RUN | PASS |
| **Total** | 9 PASS, 4 NOT RUN | **13/13 PASS** (run 43498728219, `CAD_INTEGRATION.json` sha256 `aadf3a92...c5de8`, public annotation) |

The 40/40 and 53/53 figures were not replayed from Deal-Rescue's evidence. They were recomputed by the integrated
pipeline on the downloaded STEP and compared with the recorded baseline in the pin file.

## Item 6: four connector acceptance harnesses

`tools/connector_acceptance.py` gives 38 live tests (B01 10, B02 8, B03 10, B04 10), and all 38 are **BLOCKED**.

- **Fusion:** the endpoint from `.mcp.json` was probed and refused the connection (WinError 10061 locally).
- **M365, NetSuite, M3:** no authorized tenant is configured, so no request was made.
- **Credentials:** the CI workflow references no secret.
- **Gate B:** 4/4 contract implementations pass; 0/4 live.

## Item 7: licensing

Restricted LEGION implementations copied: 0. Imported or executed: 0.

- **Marketplace, Federation, Formal-Core (PolyForm-NC):** commercial use of the current code needs the owner's
  written grant. The earlier Apache snapshots are explicitly not treated as authorization (`LICENSE_MATRIX.json`,
  `wo_lmfg_002_item_7`).
- **Phase E** is BLOCKED on this decision.

## Item 8: execution placement and disk

- **CI-only:** OpenCascade (three hash-pinned wheels, `--no-deps`) and the 34.8 MB reference STEP, which is removed at
  job end.
- **Locally:** blob-less fetch of one Deal-Rescue commit, plus git-ignored `_deps/` (≈110 KB) and `.lmfg_cache/`.

## CI

Run [43498728219](https://github.com/veraxis-protocol/Legion--Manufacturing-/actions/runs/43498728219) on `1326519`.
These numbers come from the public annotations, which can be read without signing in:

| Job | Result |
|---|---|
| 17 manufacturing skills | success. 220 tests: 198 PASS, 0 FAIL, 20 NOT RUN, 2 BLOCKED (same as Windows) |
| Connector contract suites | success. 51/51 PASS |
| Live connector acceptance | 38/38 BLOCKED |
| Real-STEP CAD | success. 13/13 PASS |
| Unit tests, policy, protected repositories | success |
| Evidence SHA-256 manifest | success |
| Source integrity, upstream baseline | failure |

The two failures were in the summary step only. Every verification step succeeded; the "Publish evidence" step
crashed in `tools/ci_summary.py`. This is fixed in `df0f8b6`. The final commit's run is recorded in
`evidence/CI_RUNS.json`.

## Next blocking dependency

1. **Live connector acceptance (Gate B live, B01..B04):**
   - an authorized Fusion desktop with its MCP add-in
   - an M365 tenant with read scopes
   - a NetSuite account with read roles
   - an Infor M3 tenant with the M3 MCP tools

   Provide them through a protected GitHub environment, never through pull requests.
2. **Model-driven runs of the 17 skills:** a Claude runtime with an authorized credential, under the owner's control.
3. **Phase E:** the owner's commercial-license decision on Marketplace, Federation and Formal-Core.
4. **The Phase A pull request:** someone signed in to GitHub has to open it.

## Evidence

| File | What it holds |
|---|---|
| `evidence/SKILL_MATRIX.windows-local.json` | Per skill: classification, per-class counts, every test result |
| `evidence/CONNECTOR_CONTRACTS.windows-local.json` | B01..B05 suite results |
| `evidence/CONNECTOR_ACCEPTANCE.windows-local.json` | 38 live tests BLOCKED, with probe results |
| `evidence/CAD_INTEGRATION.windows-local.json` | D01 offline results; real STEP NOT RUN locally |
| `evidence/UPSTREAM_BASELINE.windows-local.json`, `SOURCE_MANIFEST.json`, `LICENSE_REPORT.json`, `PROTECTED_REPOS.json` | Baseline (no regression), 94/94 import, 0 secret findings, 6/6 protected repositories unchanged |
| `evidence/SHA256SUMS`, `evidence/EVIDENCE_MANIFEST.json` | SHA-256 of every evidence file and of the pin and manifest files |
| CI artifacts `evidence-*` plus `evidence-manifest` | The Linux results and a SHA-256 list of every artifact. The digests are also published as public annotations |
