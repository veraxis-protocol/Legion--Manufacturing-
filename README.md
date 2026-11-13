# LEGION Manufacturing

LEGION Manufacturing is a functional superset of Anthropic's **Claude for Manufacturing** plugin: its 17 skills, kept
intact, plus LEGION's engineering verification, marketplace, coalition, negotiation and payment controls (work order
WO-LMFG-001).

**Status: INTEGRATION PREVIEW (WO-LMFG-001 Phase A, WO-LMFG-002 capability activation).** Nothing in this repository is
production software. No connector is live, no payment is made, no Claude plugin is distributed, and no claim of
superiority is made. See [docs/WO_LMFG_001_STATUS.md](docs/WO_LMFG_001_STATUS.md) and
[docs/WO_LMFG_002_STATUS.md](docs/WO_LMFG_002_STATUS.md).

## What is here today

| Path | Content |
|---|---|
| `upstream/claude-for-manufacturing/` | The Anthropic plugin, imported **verbatim** from `anthropics/claude-plugins-official@099387b7` (94 files, Apache-2.0). Never edited; LEGION code lives elsewhere. |
| `manifests/UPSTREAM_MANIFEST.json` | Path, mode, git blob and SHA-256 of every imported file |
| `SOURCE_PINS.json`, `LICENSE_MATRIX.json` | Pinned revisions and the license decision for every source |
| `tools/` | Manifest verifier, upstream baseline runner, license/secret policy, protected-repository check (stdlib only) |
| `manufacturing/` | Contract reader and B05 envelope over Anthropic's contracts, four read-only connector adapters, skill catalog, upstream runner, consumer gates ([ARCHITECTURE.md](ARCHITECTURE.md)) |
| `legion/engineering/` | LEGION CAD reuse: Deal-Rescue's STEP/XCAF/BOM code fetched at a pinned commit and verified, handed to the `geometry-estimate` contract |
| `tests/upstream/`, `tests/manufacturing/`, `tests/connectors/`, `tests/engineering/` | Baseline, 17 per-skill suites (`test_c01`..`test_c17`), B01..B05 contract suites, D01 CAD suite |
| `evidence/` | Machine-readable results with a SHA-256 list (`SHA256SUMS`) |
| `product/` | Empty scaffolding for later phases |

## Run the checks

Python 3.9+; the tests also need PyYAML (`pip install --no-deps --require-hashes -r requirements-ci.txt`). The
real-STEP CAD tests run only with `LMFG_REAL_CAD=1` and the OpenCascade wheels in `requirements-cad.txt` (CI job
`engineering-cad`); without them they are reported NOT RUN, never PASS.

```bash
python3 -I tools/upstream_manifest.py verify
python3 -I tools/upstream_baseline.py
python3 -I tools/repo_policy.py
python3 -I tools/protected_pins.py
python3 -m unittest discover -s tests -t . -p "test_*.py" -v
python3 -I tools/test_report.py skills --evidence evidence/SKILL_MATRIX.json
python3 -I tools/connector_acceptance.py --evidence evidence/CONNECTOR_ACCEPTANCE.json
```

CI runs the same checks on every push and pull request (`.github/workflows/ci.yml`).

## Licensing

The imported plugin is Apache-2.0 and keeps its own `LICENSE`. Several LEGION source repositories are PolyForm
Noncommercial or carry no license; they are **not copied** here (see `LICENSE_MATRIX.json`). The license for
LEGION-authored code in this repository has not been chosen by the owner yet, so no root `LICENSE` is included.
