"""WO-LMFG-004 C/D/E/F: probe for real access to Autodesk Fusion, Microsoft 365, Oracle NetSuite and Infor M3.

Writes evidence/{FUSION,M365,NETSUITE,INFOR_M3}_LIVE.json. Reuses the existing connectors and the B01..B04 live test
lists (tools/connector_acceptance.py); adds host discovery so a BLOCKED result names the exact missing dependency:
  Fusion    the endpoint from the upstream .mcp.json is actually called (MCP initialize); install folders are checked
  M365      the official routes: a Claude connector for Microsoft 365 in the runtime (--connectors file from
            `claude mcp list` / the session's connector status) or Microsoft Graph credentials in a protected env
  NetSuite  a Claude NetSuite connector or NetSuite REST credentials in a protected env
  Infor M3  an M3 MCP server URL and token in a protected env
No mock transport is used here; a system is LIVE only after a provider-backed readback.
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

import connector_acceptance as CA  # noqa: E402
from lmfg_common import artifact_header, write_json  # noqa: E402

FILES = {"B01 Autodesk Fusion": "FUSION_LIVE.json", "B02 Microsoft 365": "M365_LIVE.json",
         "B03 Oracle NetSuite": "NETSUITE_LIVE.json", "B04 Infor M3": "INFOR_M3_LIVE.json"}
CONNECTOR_WORDS = {"B02 Microsoft 365": ("microsoft", "m365", "outlook", "sharepoint", "office"),
                   "B03 Oracle NetSuite": ("netsuite",), "B04 Infor M3": ("infor", "m3")}
REQUIRED_OPS = {
    "B01 Autodesk Fusion": ["confirm Fusion installed", "MCP initialize", "open authorised reference design",
                            "read parameters", "create variant (original unchanged)", "modify driving parameter",
                            "regenerate + verify geometry", "mass / volume / bounding box",
                            "design-space-explore run", "variant comparison + trade-study handoff"],
    "B02 Microsoft 365": ["discover tools", "identity + permissions (tenant)", "read authorised RFQ email",
                         "attachments", "SharePoint documents (revisions)", "Excel export",
                         "source-bound records into contracts", "customer-inquiry-intake + data-consolidate on them"],
    "B03 Oracle NetSuite": ["authenticated account", "subsidiary/location scope", "items", "vendors", "inventory",
                            "purchase orders", "sales orders", "work orders", "historical purchase cost",
                            "routings/BOMs", "quote from retrieved costs", "no ERP write"],
    "B04 Infor M3": ["M3_MNS150MI_GetUserData_CurrentUser", "MMS200MI_SearchItem", "MMS200MI_GetItmBasic",
                     "MMS060MI_List", "PMS100MI_SearchMO", "PMS100MI_Get", "PMS100MI_LstOperations",
                     "PPS200MI_SearchHead", "PPS200MI_LstLine", "CRS620MI_SearchSupplier", "no write transaction"],
}


def fusion_install() -> dict:
    cands = [Path(os.environ.get("LOCALAPPDATA", "")) / "Autodesk" / "webdeploy",
             Path(os.environ.get("ProgramFiles", r"C:\Program Files")) / "Autodesk",
             Path(os.environ.get("APPDATA", "")) / "Autodesk" / "Autodesk Fusion 360",
             Path("/Applications/Autodesk Fusion.app")]
    return {str(p): p.exists() for p in cands}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(ROOT / "evidence"))
    ap.add_argument("--connectors", help="JSON list of connector/MCP server names visible to the Claude runtime")
    a = ap.parse_args(argv)
    connectors = json.loads(Path(a.connectors).read_text(encoding="utf-8")) if a.connectors else None
    summary = {}
    for system, fname in FILES.items():
        ops = [{"operation": o, "status": "BLOCKED"} for o in REQUIRED_OPS[system]]
        if system.startswith("B01"):
            probe = CA.probe_fusion()
            inst = fusion_install()
            live = probe["state"] == "VERIFIED"
            reason = None if live else (
                f"Autodesk Fusion is not installed on this host (checked {', '.join(k for k in inst)}) and nothing "
                f"answers the plugin's MCP endpoint {probe['endpoint']} ({probe['history'][-1][1]})"
                if not any(inst.values()) else f"Fusion MCP endpoint {probe['endpoint']} did not answer: "
                                               f"{probe['history'][-1][1]}")
            detail = {"mcp_probe": probe, "install_paths": inst}
        else:
            missing = [v for v in CA.REQUIRED_ENV[system] if not os.environ.get(v)]
            seen = None if connectors is None else [c for c in connectors
                                                    if any(w in c.lower() for w in CONNECTOR_WORDS[system])]
            live = False
            reason = (f"no authorised {system[4:]} access: no matching Claude connector in the runtime "
                      f"(visible: {connectors if connectors is not None else 'not listed'}) and the protected-"
                      f"environment credentials {', '.join(missing)} are not set; no request was made"
                      if missing and not seen else
                      "a connector/credential is present but no provider-backed readback has been recorded yet")
            detail = {"required_env": CA.REQUIRED_ENV[system], "missing_env": missing,
                      "runtime_connectors_visible": connectors, "matching_connectors": seen}
        doc = {**artifact_header("python -I tools/live_probe.py", {}), "system": system[4:],
               "live": "LIVE" if live else "BLOCKED", "status": "LIVE" if live else "BLOCKED",
               "blocked_reason": reason, "operations": ops if not live else None, "probe": detail,
               "contract_tests": "evidence/CONNECTOR_CONTRACTS.windows-local.json (mock transport: contract only, never LIVE)",
               "unblock": {"B01 Autodesk Fusion": "install Autodesk Fusion desktop with its MCP add-in on the runner, open an authorised reference design, set FUSION_MCP_PORT if not 27182",
                           "B02 Microsoft 365": "connect the Microsoft 365 connector for the Claude runtime (or provide LMFG_M365_* via a protected environment) on an authorised tenant with an RFQ mailbox, a SharePoint library and an Excel export",
                           "B03 Oracle NetSuite": "connect the NetSuite connector (or LMFG_NETSUITE_* via a protected environment) for an authorised account, read-only role",
                           "B04 Infor M3": "provide the M3 MCP server URL and token (LMFG_M3_*) for an authorised tenant, read-only"}[system]}
        write_json(Path(a.out) / fname, doc)
        summary[system[4:]] = doc["live"]
    print(json.dumps(summary))
    return 0


if __name__ == "__main__":
    sys.exit(main())
