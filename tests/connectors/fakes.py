"""Scripted provider transports for the connector CONTRACT suites.

SYNTHETIC: every record below is LEGION-authored test data, shaped with the field names the upstream document
names for that provider (shared/erp-connectors.md, Record by record; cad-adapter.md for Fusion) or with the
provider's own published response shape (Microsoft Graph, NetSuite REST record collections). None of it was read
from a real tenant, and a contract suite passing on it is never reported as connectivity.
"""
from __future__ import annotations


class M3Fake:
    """M3 MCP tools: returns {"rows": [...]} or {"error": "..."} like the M3 server's tool results."""

    def __init__(self, user=None, data=None, errors=None):
        self.user = user if user is not None else {"Company": "100", "Division": "AAA", "Facility": "F01",
                                                   "Warehouse": "W01"}
        self.data, self.errors, self.calls = data or {}, errors or {}, []

    def __call__(self, tool, args):
        self.calls.append((tool, args))
        call = tool[3:]
        if call in self.errors:
            return {"error": self.errors[call]}
        if call == "MNS150MI_GetUserData_CurrentUser":
            return {"rows": [self.user] if self.user else []}
        src = self.data.get(call, [])
        if callable(src):
            return {"rows": src(args)}
        return {"rows": list(src)}


class NetSuiteFake:
    def __init__(self, account="TSTDRV1234567", data=None, status=None, pages=None):
        self.account, self.data, self.status, self.pages, self.calls = account, data or {}, status or {}, pages or {}, []

    def __call__(self, method, path, params):
        self.calls.append((method, path, params))
        if path.endswith("metadata-catalog"):
            st = self.status.get("catalog", 200)
            return {"status": st, "account": self.account if st == 200 else None}
        rtype = path.rsplit("/", 1)[-1]
        st = self.status.get(rtype, 200)
        if st != 200:
            return {"status": st, "feature_blocked": st == 403, "detail": "feature not enabled or no permission"}
        items = self.data.get(rtype, [])
        size = self.pages.get(rtype, len(items) or 1)
        off = params.get("offset", 0)
        chunk = items[off:off + size]
        return {"status": 200, "account": self.account, "items": chunk, "count": len(chunk),
                "hasMore": off + size < len(items), "offset": off}


class GraphFake:
    def __init__(self, tenant="00000000-0000-0000-0000-00000000c0de", routes=None):
        self.tenant, self.routes, self.calls = tenant, routes or {}, []

    def __call__(self, method, url, params):
        self.calls.append((method, url, params))
        path = url.split("/v1.0", 1)[1]
        if path == "/organization":
            r = self.routes.get(path)
            return r if r is not None else {"status": 200, "value": [{"id": self.tenant}]}
        for k, v in self.routes.items():
            if path == k or path.startswith(k + "?"):
                return v
        return {"status": 404}


class FusionFake:
    """A stand-in for the Fusion MCP endpoint: answers the scripts the adapter sends by recognising them."""

    def __init__(self, doc=None, params=None, healthy=True, tools=("fusion_mcp_read", "fusion_mcp_execute"),
                 reachable=True, move_base=False):
        self.docs = {(doc or {"name": "Bracket_Base", "version": 7})["name"]: dict(doc or {"name": "Bracket_Base", "version": 7})}
        self.active = next(iter(self.docs))
        self.params = params if params is not None else {
            "flange_length": {"expression": "20 mm", "unit": "mm", "driving": True},
            "label_text": {"expression": "'A'", "unit": "", "driving": False}}
        self.healthy, self.tools, self.reachable, self.move_base = healthy, tools, reachable, move_base
        self.calls, self.writes = [], []

    def __call__(self, method, params):
        if not self.reachable:
            raise ConnectionRefusedError("[WinError 10061] connection refused (no Fusion desktop MCP add-in)")
        self.calls.append((method, params))
        if method == "initialize":
            return {"result": {"serverInfo": {"name": "fusion-mcp-fake"}}}
        if method == "tools/list":
            return {"result": {"tools": [{"name": t} for t in self.tools]}}
        args = params["arguments"]
        script, ro = args["script"], args["readOnly"]
        if params["name"] == "fusion_mcp_read" and not ro:
            return {"error": "fusion_mcp_read requires readOnly"}
        import json
        if "saveAs" in script:
            if ro:
                return {"error": "cannot modify a read-only call"}
            new = script.split("d.saveAs(", 1)[1].split(",", 1)[0].strip().strip('"')
            self.docs[new] = {"name": new, "version": 1}
            self.active = new
            self.writes.append(("saveAs", new))
            out = {"saved_as": new}
        elif "userParameters.itemByName" in script:
            if ro:
                return {"error": "cannot modify a read-only call"}
            self.writes.append(("apply", self.active))
            if self.move_base:
                base = [d for d in self.docs if d != self.active][0]
                self.docs[base]["version"] += 1
            out = {"applied": True}
        elif "for d in app.documents" in script:
            name = script.split("if d.name == ", 1)[1].split(":", 1)[0].strip().strip('"')
            out = self.docs.get(name, {"name": name, "version": None})
        elif "activeDocument" in script:
            out = {**self.docs[self.active], "modified": False}
        elif "userParameters" in script:
            out = self.params
        elif "timeline" in script:
            out = {"timeline": [{"name": "Extrude1", "healthState": "healthy" if self.healthy else "error"}]}
        elif "physicalProperties" in script:
            out = {"bodies": [{"body": "Body1", "mass_kg": 0.12, "volume_cm3": 44.4, "bbox_cm": [5.0, 3.0, 1.2]}]}
        else:
            out = {}
        return {"result": {"content": [{"type": "text", "text": json.dumps(out)}]}}
