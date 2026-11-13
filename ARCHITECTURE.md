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

## Invariants carried by the code (WO-LMFG-001 section 3)

| ID | Where it is enforced in Phase A |
|---|---|
| INV-01 source integrity | `tools/upstream_manifest.py verify`, `tests/upstream/test_source_integrity.py`, CI job `source-integrity` |
| INV-02 baseline preservation | `tools/upstream_baseline.py` (runs on a copy; detects any write into the plugin tree), CI job `upstream-baseline` |
| INV-09 repository protection | `tools/protected_pins.py`, CI job `protected-repos` |
| INV-03..INV-08, INV-10 | later phases (connectors, engineering, commerce, judge) |

## Execution boundaries

- Upstream skills are Markdown instructions run by Claude. They are "available" when imported intact. A live run needs
  the Claude runtime and the plant's connected systems, and is recorded as BLOCKED until those exist.
- Only three upstream files are executable code: `shared/scripts/plant_setup.py`,
  `skills/morning-plant-pulse/scripts/pulse_compute.py` and `render_short.py`. The fourth executable surface, the Fusion
  MCP server in `.mcp.json`, is an external endpoint (`http://127.0.0.1:${FUSION_MCP_PORT:-27182}/mcp`) provided by
  Autodesk Fusion desktop.
- No connector configuration counts as connectivity (INV-03); no payment or supplier contact happens in Phase A.
