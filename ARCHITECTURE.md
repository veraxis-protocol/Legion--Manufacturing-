# Architecture

## Principle

`LEGION Manufacturing = Claude for Manufacturing capabilities + LEGION economic capabilities + independent consequence control`

Reuse first: the Anthropic plugin is vendored byte-for-byte; LEGION mechanisms are reused through pinned, license-checked
sources or adapters. Nothing is re-implemented as a mock or a prompt-only simulation.

## Layers

```text
upstream/claude-for-manufacturing/   Anthropic plugin, verbatim (17 skills, shared contracts, 3 Python scripts, .mcp.json)
            |
manufacturing/                        LEGION side of the manufacturing domain
  contracts/    extensions of the upstream contracts (source bindings, verification metadata); never replaces them
  connectors/   Fusion, Microsoft 365, NetSuite, Infor M3 lifecycle:
                DISCONNECTED -> CONFIGURED -> AUTHENTICATED -> SCOPED -> VERIFIED (any failure: unavailable)
  adapters/     unified data adapter over the upstream normalized schema
  runtime/      runs upstream skills/scripts unchanged and records their events
            |
legion/                               reused LEGION mechanisms, behind adapters
  engineering/  CAD intake (Deal-Rescue industrial, Apache-2.0) + ZTL Engineer (Apache-2.0)
  marketplace/  demand/supply matching       (LEGION-Marketplace: PolyForm-NC, external pinned dependency)
  federation/   coalitions, negotiation      (LEGION-Federation: PolyForm-NC, external pinned dependency)
  admission/    consequence gate: VERDICT = Z => no consequential execution (INV-07)
  commerce/     PayPal Sandbox via commerce_adapter (Apache-2.0 copy in Deal-Rescue), never live payments
            |
product/                              buyer, manufacturer and enterprise journeys over the integrated backend
```

## What exists after WO-LMFG-002

| Path | What it is |
|---|---|
| `manufacturing/contracts/upstream.py` | Reads Anthropic's `shared/contracts/*.md` at run time: field tables, Required/Degrades/Optional, enums, YAML and CSV worked examples with their line ranges. Checks a record; never fills a value |
| `manufacturing/adapters/envelope.py` | WO-B05. The upstream record travels unchanged inside a LEGION envelope with source bindings, a read-only permission scope (only narrows) and verification metadata. Tenant isolation, tamper detection, UNAVAILABLE instead of empty success |
| `manufacturing/adapters/dataset_rows.py` | Checks connector-pulled rows against `consolidated-dataset.md` (common columns, key pairs, uom/currency rules) |
| `manufacturing/connectors/` | `lifecycle.py` (DISCONNECTED -> ... -> VERIFIED, UNAVAILABLE on failure or expiry, no execution authority). `fusion.py` (MCP client and guard around the endpoint in `.mcp.json`), `m365.py` (Microsoft Graph, GET allow-list), `netsuite.py` (REST record service, record types from `erp-connectors.md`), `infor_m3.py` (M3 MI transactions parsed from `erp-connectors.md`) |
| `manufacturing/runtime/` | `catalog.py` (17 skills classified, each bound to a quote in its SKILL.md), `upstream_exec.py` (runs upstream scripts from a copy in a task folder), `gates.py` (consumer **Blocks** rows from the contracts as T/Z gates) |
| `legion/engineering/` | WO-D01. `DEAL_RESCUE_PIN.json` + `pinned_source.py` fetch and verify Deal-Rescue's CAD modules at a pinned commit (not copied); `step_intake.py` orders STEP -> XCAF -> BOM -> requirements -> verification (Z) and hands CNC parts to `geometry-estimate` path C1 |

## Invariants carried by the code (WO-LMFG-001 section 3)

| ID | Where it is enforced |
|---|---|
| INV-01 source integrity | `tools/upstream_manifest.py verify`, `tests/upstream/test_source_integrity.py`, CI job `source-integrity`; per-skill regression test `test_6_*` |
| INV-02 baseline preservation | upstream code only runs from a copy (`upstream_exec.TaskFolder`, `upstream_baseline.py`); tree digest checked before and after |
| INV-03 config is not connectivity | `Lifecycle`: a configuration stops at CONFIGURED; only a readback reaches VERIFIED; `tools/connector_acceptance.py` never records a live PASS |
| INV-07 Z => no consequential execution | `manufacturing/runtime/gates.py` (`consequential_execution_allowed`), CAD `engineering_verdict` Z |
| INV-09 repository protection | `tools/protected_pins.py`, CI job `protected-repos`; Deal-Rescue read through git objects only |
| INV-04..06, INV-08, INV-10 | later phases (marketplace, federation, commerce, judge) |

## Execution boundaries

- Upstream skills are Markdown instructions run by Claude. They are "available" when imported intact. A live run needs
  the Claude runtime and the plant's connected systems, and is recorded as BLOCKED until those exist.
- Only three upstream files are executable code: `shared/scripts/plant_setup.py`,
  `skills/morning-plant-pulse/scripts/pulse_compute.py` and `render_short.py`. The fourth executable surface, the Fusion
  MCP server in `.mcp.json`, is an external endpoint (`http://127.0.0.1:${FUSION_MCP_PORT:-27182}/mcp`) provided by
  Autodesk Fusion desktop.
- No connector configuration counts as connectivity (INV-03); no payment or supplier contact happens in Phase A.
