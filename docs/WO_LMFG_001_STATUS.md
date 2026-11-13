# WO-LMFG-001 status

Format per WO section 15. A gate is **T** only when its evidence exists and CI reproduces it; **Z** means not yet
established; **F** means a check failed.

## WO-A01 - Repository initialization

- **Changed files:** repository skeleton, `README.md`, `ARCHITECTURE.md`, `SOURCE_PINS.json`, `LICENSE_MATRIX.json`,
  `DEPENDENCY_LOCK`, `.github/workflows/ci.yml`, `tools/*`, `tests/upstream/*`
- **Upstream source reused:** none modified; tooling is stdlib Python
- **Tests executed:** `tools/repo_policy.py` (secret scan + license rules), `tools/protected_pins.py`
- **Negative tests:** secret patterns; forbidden copies of DO-NOT-COPY trees (Commerce, Marketplace, Federation, Formal-Core)
- **Evidence:** `evidence/LICENSE_REPORT.json`, `evidence/PROTECTED_REPOS.json`
- **Remaining obligations:** owner decisions in `LICENSE_MATRIX.json` (repository license; commercial use of PolyForm sources)

## WO-A02 - Exact Anthropic import

- **Upstream source reused:** `anthropics/claude-plugins-official@099387b7a2ea02022bb850becca750246ae12562`,
  `plugins/claude-for-manufacturing/` (94 files, 17 skills, Apache-2.0), imported with `git archive`
  (`core.autocrlf=false`) into `upstream/claude-for-manufacturing/`
- **Tests executed:** `tools/upstream_manifest.py verify`, `tests/upstream/test_source_integrity.py`
- **Result (local, Windows):** 94/94 files byte-identical (git blob and SHA-256), 0 missing, 0 extra, 17/17 skills with
  `SKILL.md`, LICENSE present; local references resolve (two `setup/*.md` mentions are file names inside the runtime
  plant page that `plant_setup.py` builds, recorded separately, not repository files)
- **Negative tests:** a one-byte change is detected by both digests
- **Evidence:** `manifests/UPSTREAM_MANIFEST.json`, `evidence/SOURCE_MANIFEST.json`

## WO-A03 - Upstream executable baseline

- **Entrypoints found:** 3 Python scripts + 1 MCP server declaration (Fusion)
- **Local Windows run** (`evidence/UPSTREAM_BASELINE.windows-local.json`): 9 PASS / 1 FAIL / 1 BLOCKED
  - PASS: compile and `--help` of all 3 scripts; `pulse_compute.py` on the synthetic fixture (47 self-checks, 0 failed;
    OEE reported absent, not 0); `render_short.py` (page checks passed); no writes into the plugin tree
  - FAIL: `plant_setup.py --selftest` on Windows only. Upstream defect: line 1113 asserts a POSIX `/` separator in
    `work_path`; Windows returns `\`. The tested `install()` call itself succeeded. Baseline not edited.
  - BLOCKED: `.mcp.json#fusion` needs Autodesk Fusion desktop with its MCP add-in
- **Authoritative Linux run:** CI job `upstream-baseline` on ubuntu-24.04 (see the pull request's checks)
- **Skills:** 17/17 AVAILABLE; 1 with local code (morning-plant-pulse, scripts PASS); the live model-driven run of all
  17 is BLOCKED here (needs the Claude runtime, a plant profile and authorized connectors)
- **Fixture:** `tests/upstream/fixtures/pulse_minimal` is LEGION-authored synthetic data, because upstream ships none

## Gate A

**Z** until the pull request's CI reproduces the baseline on Linux. Then **T** for the import and the locally executable
baseline, with Fusion and every live, model-driven skill run explicitly BLOCKED.

## Next executable WO

WO-B05 (connector contract adapter over the upstream contracts, local contract tests) and WO-D01 (CAD intake reuse from
LEGION-Deal-Rescue, Apache-2.0) can proceed without external systems. WO-B01 to WO-B04 live acceptance is BLOCKED until
Fusion, Microsoft 365, NetSuite and Infor M3 tenants with authorized credentials are provided.
