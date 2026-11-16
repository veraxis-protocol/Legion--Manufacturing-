"""WO-B01: Autodesk Fusion, through the Fusion desktop MCP endpoint the upstream plugin declares in `.mcp.json`.

No CAD engine is implemented here. This is a client and a guard around the existing interface
(`fusion_mcp_read` / `fusion_mcp_execute`, script feature type), applying the rules in upstream
`skills/design-space-explore/reference/cad-adapter.md` before anything reaches Fusion:
  - a script defines run(context) and never calls run() itself (a script that calls it executes twice)
  - every inspection call is readOnly: true
  - a write happens only in a new document made by "save as new", after the active document's name has been read
    back and differs from the base model; the base model's version is read again after the run and a move stops it
  - regeneration health is each timeline item's healthState; an unhealthy item makes the variant failed, unmeasured
  - an invalid parameter change (unknown or non-driving parameter, unit missing) is rejected before any call
The endpoint is `http://127.0.0.1:${FUSION_MCP_PORT:-27182}/mcp`, read from `.mcp.json`, never hard-coded.
"""
from __future__ import annotations

import ast
import json
import os
import re
import urllib.error
import urllib.request
from pathlib import Path

from manufacturing.connectors.common import Adapter
from manufacturing.connectors.lifecycle import LifecycleError, WriteRefused

MCP_JSON = Path(__file__).resolve().parents[2] / "upstream" / "claude-for-manufacturing" / ".mcp.json"
READ_TOOL, EXEC_TOOL = "fusion_mcp_read", "fusion_mcp_execute"


def endpoint(env=None) -> str:
    env = os.environ if env is None else env
    url = json.loads(MCP_JSON.read_text(encoding="utf-8"))["mcpServers"]["fusion"]["url"]
    return re.sub(r"\$\{([A-Z_]+):-([^}]*)\}", lambda m: env.get(m.group(1)) or m.group(2), url)


class ScriptRejected(ValueError):
    pass


def check_script(source: str):
    """cad-adapter.md: define run(context); never call run() at top level; no top-level statements doing work."""
    try:
        tree = ast.parse(source)
    except SyntaxError as e:
        raise ScriptRejected(f"script does not parse: {e}") from e
    defs = [n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "run"]
    if not defs or [a.arg for a in defs[0].args.args] != ["context"]:
        raise ScriptRejected("a script must define run(context)")
    for node in tree.body:
        if isinstance(node, (ast.Import, ast.ImportFrom, ast.FunctionDef, ast.ClassDef)):
            continue
        if isinstance(node, ast.Expr) and isinstance(node.value, ast.Constant):
            continue                                                  # docstring
        raise ScriptRejected("top-level code is not allowed (the tool calls run() itself; a call here runs twice)")


def http_transport(url: str, timeout: float = 5.0):
    """Streamable-HTTP MCP JSON-RPC transport. Used only by live acceptance; contract tests pass their own."""
    counter = {"id": 0}

    def call(method, params):
        counter["id"] += 1
        body = json.dumps({"jsonrpc": "2.0", "id": counter["id"], "method": method, "params": params}).encode()
        req = urllib.request.Request(url, data=body, method="POST",
                                     headers={"Content-Type": "application/json",
                                              "Accept": "application/json, text/event-stream"})
        with urllib.request.urlopen(req, timeout=timeout) as r:
            raw = r.read().decode("utf-8", "replace")
        if raw.startswith("event:") or "\ndata:" in raw or raw.startswith("data:"):
            raw = [l[5:].strip() for l in raw.splitlines() if l.startswith("data:")][-1]
        return json.loads(raw)
    return call


class Fusion(Adapter):
    system = "fusion"
    source_system = "fusion"

    def connect(self, config: dict):
        self.lc.configure(config)
        if self.lc.state != "CONFIGURED":
            return self.lc.state
        try:
            init = self.transport("initialize", {"protocolVersion": "2025-06-18", "capabilities": {},
                                                 "clientInfo": {"name": "legion-manufacturing", "version": "0.2"}})
        except (urllib.error.URLError, OSError, TimeoutError) as e:
            return self.lc.fail(f"FUSION_MCP_UNREACHABLE {e}")
        if "error" in init:
            return self.lc.fail(f"INITIALIZE_ERROR {init['error']}")
        tools = self.transport("tools/list", {})
        names = {t["name"] for t in (tools.get("result") or {}).get("tools", [])}
        if not {READ_TOOL, EXEC_TOOL} <= names:
            return self.lc.fail(f"FUSION_TOOLS_MISSING have={sorted(names)}")
        server = (init.get("result") or {}).get("serverInfo", {})
        self.lc.authenticated(f"fusion-desktop:{server.get('name', 'unknown')}", None)
        self.lc.scoped(["design:read", "design:new-document-write"])
        doc = self.read_document()
        self.lc.verified(bool(doc.get("name")), "no open document")
        self.base = doc if self.lc.state == "VERIFIED" else None
        return self.lc.state

    def _tool(self, tool, script, read_only):
        check_script(script)
        if tool == READ_TOOL and not read_only:
            raise ScriptRejected("fusion_mcp_read is always readOnly: true")
        self.log.add("read" if read_only else "write", tool, {"readOnly": read_only})
        res = self.transport("tools/call", {"name": tool, "arguments": {"script": script, "readOnly": read_only}})
        if "error" in res:
            msg = str(res["error"])
            if "cannot modify" in msg.lower():
                self.lc.fail("RETAINED_SCRIPT_SUSPECTED: restart Fusion (cad-adapter.md)")
            raise LifecycleError(f"{tool}: {msg}")
        content = (res.get("result") or {}).get("content") or []
        text = "\n".join(c.get("text", "") for c in content if c.get("type") == "text")
        try:
            return json.loads(text.strip().splitlines()[-1]) if text.strip() else {}
        except json.JSONDecodeError:
            return {"printed": text}

    def inspect(self, script):
        return self._tool(READ_TOOL, script, True)

    def read_document(self):
        return self._tool(READ_TOOL, _READ_DOC, True)

    def read_parameters(self):
        self.lc.require_verified()
        return self.inspect(_READ_PARAMS)

    def save_as_new(self, new_name: str):
        self.lc.require_verified()
        if not new_name or new_name == self.base["name"]:
            raise WriteRefused("the variant needs its own new document name")
        self._tool(EXEC_TOOL, _SAVE_AS_NEW.replace("@NAME@", json.dumps(new_name)), False)
        active = self.read_document()
        if active.get("name") != new_name or active.get("name") == self.base["name"]:
            self.lc.fail("ACTIVE_DOCUMENT_IS_NOT_THE_NEW_DOCUMENT")
            raise WriteRefused(f"after save-as-new the active document is {active.get('name')!r}")
        self.active = active
        return active

    def apply_parameters(self, values: dict, params: dict):
        """Reject invalid changes before any call; write only in the new document; check health and read back."""
        self.lc.require_verified()
        if getattr(self, "active", None) is None or self.active.get("name") == self.base["name"]:
            raise WriteRefused("parameters are applied only in a new document made by save_as_new")
        for k, v in values.items():
            p = params.get(k)
            if p is None:
                raise ScriptRejected(f"unknown parameter {k}")
            if not p.get("driving"):
                raise ScriptRejected(f"{k} does not drive geometry (parametric-check.md); varying it changes nothing")
            if not isinstance(v, str) or not re.match(r"^-?\d+(\.\d+)?\s*[a-z]+$", v.strip()):
                raise ScriptRejected(f"{k}={v!r}: a value with its unit is required, e.g. '12 mm'")
        res = self._tool(EXEC_TOOL, _APPLY.replace("@VALUES@", json.dumps(values)), False)
        health = self.inspect(_HEALTH)
        bad = [t for t in health.get("timeline", []) if t.get("healthState") != "healthy"]
        if bad:
            return {"variant": "failed", "unhealthy": bad, "properties": None}
        props = self.inspect(_PROPS)
        return {"variant": "ok", "applied": res, "properties": props}

    def confirm_base_unchanged(self):
        now = self._tool(READ_TOOL, _READ_DOC_BY_NAME.replace("@NAME@", json.dumps(self.base["name"])), True)
        if now.get("version") != self.base.get("version"):
            self.lc.fail("BASE_MODEL_VERSION_MOVED")
            return False
        return True


_READ_DOC = '''import adsk.core, json
def run(context):
    app = adsk.core.Application.get(); d = app.activeDocument
    print(json.dumps({"name": d.name, "version": d.dataFile.versionNumber if d.dataFile else None,
                      "modified": d.isModified}))
'''
_READ_DOC_BY_NAME = '''import adsk.core, json
def run(context):
    app = adsk.core.Application.get()
    for d in app.documents:
        if d.name == @NAME@:
            print(json.dumps({"name": d.name, "version": d.dataFile.versionNumber if d.dataFile else None})); return
    print(json.dumps({"name": @NAME@, "version": None}))
'''
_READ_PARAMS = '''import adsk.core, adsk.fusion, json
def run(context):
    des = adsk.fusion.Design.cast(adsk.core.Application.get().activeProduct)
    out = {}
    for p in des.userParameters:
        out[p.name] = {"expression": p.expression, "unit": p.unit, "driving": len(p.dependentParameters) > 0 or p.isFavorite}
    print(json.dumps(out))
'''
_SAVE_AS_NEW = '''import adsk.core, json
def run(context):
    app = adsk.core.Application.get(); d = app.activeDocument
    d.saveAs(@NAME@, d.dataFile.parentFolder, "LEGION variant", "")
    print(json.dumps({"saved_as": @NAME@}))
'''
_APPLY = '''import adsk.core, adsk.fusion, json
def run(context):
    des = adsk.fusion.Design.cast(adsk.core.Application.get().activeProduct)
    vals = @VALUES@
    for k, v in vals.items():
        des.userParameters.itemByName(k).expression = v
    print(json.dumps({"applied": sorted(vals)}))
'''
_HEALTH = '''import adsk.core, adsk.fusion, json
def run(context):
    des = adsk.fusion.Design.cast(adsk.core.Application.get().activeProduct)
    print(json.dumps({"timeline": [{"name": t.name, "healthState": "healthy" if t.healthState == 0 else str(t.healthState)}
                                   for t in des.timeline]}))
'''
_PROPS = '''import adsk.core, adsk.fusion, json
def run(context):
    des = adsk.fusion.Design.cast(adsk.core.Application.get().activeProduct)
    out = []
    for b in des.rootComponent.bRepBodies:
        pp = b.physicalProperties; bb = b.boundingBox
        out.append({"body": b.name, "mass_kg": pp.mass, "volume_cm3": pp.volume,
                    "bbox_cm": [bb.maxPoint.x - bb.minPoint.x, bb.maxPoint.y - bb.minPoint.y, bb.maxPoint.z - bb.minPoint.z]})
    print(json.dumps({"bodies": out}))
'''
