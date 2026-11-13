# LEGION Manufacturing

LEGION Manufacturing is a functional superset of Anthropic's **Claude for Manufacturing** plugin: its 17 skills, kept
intact, plus LEGION's engineering verification, marketplace, coalition, negotiation and payment controls (work order
WO-LMFG-001).

**Status: INTEGRATION PREVIEW, Phase A (WO-A01 to WO-A03).** Nothing in this repository is production software. No
connector is live, no payment is made, and no claim of superiority is made yet. See
[docs/WO_LMFG_001_STATUS.md](docs/WO_LMFG_001_STATUS.md) for the gate-by-gate status.

## What is here today

| Path | Content |
|---|---|
| `upstream/claude-for-manufacturing/` | The Anthropic plugin, imported **verbatim** from `anthropics/claude-plugins-official@099387b7` (94 files, Apache-2.0). Never edited; LEGION code lives elsewhere. |
| `manifests/UPSTREAM_MANIFEST.json` | Path, mode, git blob and SHA-256 of every imported file |
| `SOURCE_PINS.json`, `LICENSE_MATRIX.json` | Pinned revisions and the license decision for every source |
| `tools/` | Manifest verifier, upstream baseline runner, license/secret policy, protected-repository check (stdlib only) |
| `tests/upstream/` | Integrity and baseline tests, with a labelled synthetic fixture for the pulse engine |
| `evidence/` | Machine-readable results of the checks above |
| `manufacturing/`, `legion/`, `product/`, `tests/*` | Empty scaffolding for later phases (B to I) |

## Run the checks

Python 3.9+ standard library only; nothing to install.

```bash
python3 -I tools/upstream_manifest.py verify
python3 -I tools/upstream_baseline.py
python3 -I tools/repo_policy.py
python3 -I tools/protected_pins.py
python3 -m unittest discover -s tests -p "test_*.py" -v
```

CI runs the same checks on every push and pull request (`.github/workflows/ci.yml`).

## Licensing

The imported plugin is Apache-2.0 and keeps its own `LICENSE`. Several LEGION source repositories are PolyForm
Noncommercial or carry no license; they are **not copied** here (see `LICENSE_MATRIX.json`). The license for
LEGION-authored code in this repository has not been chosen by the owner yet, so no root `LICENSE` is included.
