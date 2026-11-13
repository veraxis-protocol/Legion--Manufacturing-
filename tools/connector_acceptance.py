"""Live acceptance for the four connectors (WO-B01..B04). Every live test is BLOCKED until an authorized system is
configured; nothing here can turn a contract-test result into a live PASS.

  python -I tools/connector_acceptance.py --evidence evidence/CONNECTOR_ACCEPTANCE.json

Fusion: the endpoint from the upstream `.mcp.json` is actually probed (initialize). On a machine without Fusion
desktop and its MCP add-in the probe is refused, and that refusal is recorded as the BLOCKED reason.
M365 / NetSuite / Infor M3: live runs need the variables below, provided only through a protected environment
(never to pull requests from forks). When they are absent no request is made at all.
A live PASS is recorded only after a provider-backed readback, which this harness does not fake.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(1, str(ROOT / "tools"))

from lmfg_common import artifact_header, write_json  # noqa: E402

TESTS = {
    "B01 Autodesk Fusion": ["Connect to a running Fusion desktop MCP instance", "Read the active design and its document identity",
                            "Read parameters; driving vs non-driving", "Create a variant as a new document; original unmodified",
                            "Geometry regeneration and physical-property readback", "Reject invalid parameter changes",
                            "Document integrity before and after writes", "Validate supported CAM operation estimates",
                            "Deny modification through read-only operations", "Disconnect; fail closed"],
    "B02 Microsoft 365": ["Authenticate with permitted scopes", "Read one actual authorized RFQ", "Fetch its attachments",
                          "Extract fields and preserve source references", "Read a permitted manufacturing export",
                          "Deny unauthorized document access", "Reject expired credentials", "Zero unauthorized writes"],
    "B03 Oracle NetSuite": ["Authorized connection", "Subsidiary and location scoping", "Item record retrieval",
                            "Supplier record retrieval", "Historical cost retrieval", "Purchase-order and demand retrieval",
                            "Missing records not converted to zero", "Cross-tenant access denied", "Unauthorized writes denied",
                            "Source record identity preserved"],
    "B04 Infor M3": ["Signed-in M3 user context", "Company, division, facility and warehouse scopes", "Item master records",
                     "Inventory and inspection status", "Manufacturing-order operations", "Operation time units",
                     "Purchase-order records", "Pagination and date formats", "Unavailable data vs zero",
                     "No write transaction issued"],
}
REQUIRED_ENV = {
    "B02 Microsoft 365": ["LMFG_M365_TENANT_ID", "LMFG_M365_CLIENT_ID", "LMFG_M365_TOKEN"],
    "B03 Oracle NetSuite": ["LMFG_NETSUITE_ACCOUNT", "LMFG_NETSUITE_TOKEN"],
    "B04 Infor M3": ["LMFG_M3_MCP_URL", "LMFG_M3_TOKEN"],
}


def probe_fusion() -> dict:
    from manufacturing.connectors import fusion as F
    url = F.endpoint()
    a = F.Fusion(F.http_transport(url, timeout=3.0), {})
    state = a.connect({"endpoint": url})
    return {"endpoint": url, "state": state, "history": a.lc.history}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--evidence", required=True)
    a = ap.parse_args(argv)
    systems = {}
    for system, tests in TESTS.items():
        if system.startswith("B01"):
            p = probe_fusion()
            live = p["state"] == "VERIFIED"
            reason = ("Fusion MCP answered; live acceptance must be run and read back on that machine"
                      if live else f"no Fusion desktop MCP endpoint: {p['history'][-1][1]}")
            probe = p
        else:
            missing = [v for v in REQUIRED_ENV[system] if not os.environ.get(v)]
            live, probe = False, {"required_env": REQUIRED_ENV[system], "missing": missing}
            reason = ("no authorized tenant configured (" + ", ".join(missing) + " not set); no request was made"
                      if missing else "credentials present but the provider-backed run is not implemented to PASS "
                                      "without a human-reviewed readback")
        systems[system] = {"live_tests": [{"id": f"{system[:3]}-T{i:02d}", "name": n, "status": "BLOCKED",
                                           "reason": reason} for i, n in enumerate(tests, 1)],
                           "probe": probe, "live": "BLOCKED"}
    n = sum(len(s["live_tests"]) for s in systems.values())
    doc = {**artifact_header("python -I tools/connector_acceptance.py", {}), "status": "BLOCKED",
           "counts": {"live_tests": n, "PASS": 0, "FAIL": 0, "BLOCKED": n},
           "gate_b": "4/4 contract implementations are evidenced separately (CONNECTOR_CONTRACTS.json); 0/4 LIVE",
           "systems": systems}
    write_json(Path(a.evidence), doc)
    print(json.dumps(doc["counts"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
