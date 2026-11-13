"""WO-D02 (WO-LMFG-003): the minimal LEGION adapter between the CAD intake and the real ZTL verification route.

    STEP -> XCAF -> BOM -> sourced requirements      (step_intake.py, pinned Deal-Rescue cad_xcaf / cad027_review)
    -> ZTL brick                                      (Deal-Rescue cad027_review.rail_length_brick, or a stand example)
    -> ZTL Engineer MCP, tools/call check_design      (_deps/ztl-engineer/mcp_server.py, a separate process)
    -> ZTL Stand `python -m ustand.stand` + checker   (_deps/ztl-stand, judge _deps/ZTL)
    -> scoped predicate verdict -> strict aggregation -> receipt layer -> production admission layer

This module computes no engineering result. It sends a brick over stdio JSON-RPC exactly as Deal-Rescue's
cad027_review.check_design does (the reference), keeps the request and the response, maps the stand's own verdict,
binds it to the engineering context it was obtained for, and refuses everything else:

  stand EARNED  -> T  (only for the submitted claim, under the brick's assumptions)
  stand REFUTED -> F  (within the checked scope)
  OPEN, BRICK ERROR, STAND ERROR, STAND FAULT, any unknown verdict, MCP error, malformed reply, timeout,
  server unavailable -> Z.  A transport failure is never F.

Four layers stay separate (WO-D02-D): the stand verdict; the engineering predicate verdict; an independently
authenticated engineering receipt (Deal-Rescue ztl_gate, Ed25519, CAD-025); the production admission (Deal-Rescue
admission.decide). A local MCP process is not an authenticated verifier: without a receipt the global verdict can be
F or Z, never T. Nothing here issues an order, a payment, a supplier request or a manufacturing release.
"""
from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

from legion.engineering import pinned_source as P

T, F, Z = "T", "F", "Z"
DEPS = P.ROOT / "_deps"
DEFAULT_TIME_LIMIT_S = 120

VERDICT_MAP = {"EARNED": T, "REFUTED": F}          # every other stand verdict, and every transport outcome, is Z
POLICY = {
    "schema": "legion.engineering.ztl-policy.v1",
    "verdict_map": {"EARNED": T, "REFUTED": F, "OPEN": Z, "BRICK ERROR": Z, "STAND ERROR": Z, "STAND FAULT": Z,
                    "MCP_TIMEOUT": Z, "MCP_UNAVAILABLE": Z, "MCP_ERROR": Z, "MCP_MALFORMED": Z, "UNKNOWN": Z},
    "aggregation": "any mandatory F -> F; all mandatory T + valid bindings + authenticated receipt -> T; else Z",
    "proof_validity": "same source_sha256, source_commit, drawing_revision, spec_digest, requirements_digest, "
                      "policy_sha256 and brick_sha256 as when the stand was called",
    "mcp_tool": "check_design", "ask_engineer": "never called (paid model API)",
}
CONTEXT_FIELDS = ("source_repository", "source_commit", "source_file", "source_sha256", "drawing_revision",
                  "spec_digest", "requirements_digest")
PREDICATE_FIELDS = ("part_id", "predicate_id", "predicate_inputs", "units", "tolerances", "tolerance_sources")
# a missing predicate field stops the stand call; a missing context field only stops admission
BLOCKS_STAND_CALL = ("predicate_inputs", "units", "tolerances", "tolerance_sources")


def canonical(obj) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def sha256_of(obj) -> str:
    return hashlib.sha256(canonical(obj)).hexdigest()


POLICY_SHA256 = sha256_of(POLICY)


class BindingRejected(ValueError):
    pass


# ---------------------------------------------------------------- runtime (pinned, verified sources)
@dataclass
class Runtime:
    engineer: Path
    stand: Path
    ztl: Path
    commits: dict
    python: str = sys.executable
    materialized: dict = field(default_factory=dict)

    @property
    def server(self) -> Path:
        return self.engineer / "mcp_server.py"

    def env(self) -> dict:
        return dict(os.environ, ZTL_ENGINEER_STAND=str(self.stand), USTAND_ZTL=str(self.ztl),
                    PYTHONIOENCODING="utf-8", PYTHONUTF8="1", PYTHONDONTWRITEBYTECODE="1")


def runtime(materialize: bool = True, deps_root: Path = DEPS) -> Runtime:
    manifest = P.load_manifest()
    done = P.materialize_all(manifest, deps_root) if materialize else {}
    by = {r["name"]: r for r in manifest["repositories"]}
    return Runtime(engineer=(deps_root / "ztl-engineer").resolve(), stand=(deps_root / "ztl-stand").resolve(),
                   ztl=(deps_root / "ZTL").resolve(), commits={k: v["commit"] for k, v in by.items()},
                   materialized=done)


# ---------------------------------------------------------------- MCP stdio transport (real process)
def stdio_transport(rt: Runtime, lines: list, timeout_s: float) -> dict:
    """Start `python mcp_server.py`, write the JSON-RPC lines, read every reply line. Never raises."""
    t0 = time.time()
    if not rt.server.is_file():
        return {"status": "MCP_UNAVAILABLE", "why": f"server not found: {rt.server}", "seconds": 0.0}
    try:
        p = subprocess.run([rt.python, str(rt.server)], input="\n".join(lines) + "\n", capture_output=True,
                           encoding="utf-8", errors="replace", env=rt.env(), timeout=timeout_s, cwd=str(rt.engineer))
    except subprocess.TimeoutExpired:
        return {"status": "MCP_TIMEOUT", "why": f"no complete reply within {timeout_s} s", "seconds": round(time.time() - t0, 2)}
    except OSError as e:
        return {"status": "MCP_UNAVAILABLE", "why": f"{type(e).__name__}: {e}", "seconds": round(time.time() - t0, 2)}
    return {"status": "EXITED", "returncode": p.returncode, "stdout": p.stdout or "", "stderr_tail": (p.stderr or "")[-1500:],
            "seconds": round(time.time() - t0, 2)}


def _replies(stdout: str) -> tuple[dict, list]:
    by_id, bad = {}, []
    for line in stdout.splitlines():
        if not line.strip():
            continue
        try:
            msg = json.loads(line)
        except ValueError:
            bad.append(line[:300])
            continue
        if isinstance(msg, dict) and "id" in msg:
            by_id[msg["id"]] = msg
        else:
            bad.append(line[:300])
    return by_id, bad


def initialize(rt: Runtime, timeout_s: float = 60, transport=stdio_transport) -> dict:
    """D02-02: the real server answers initialize and lists check_design."""
    msgs = [{"jsonrpc": "2.0", "id": 0, "method": "initialize", "params": {"protocolVersion": "2025-06-18"}},
            {"jsonrpc": "2.0", "method": "notifications/initialized"},
            {"jsonrpc": "2.0", "id": 1, "method": "tools/list"}]
    raw = transport(rt, [json.dumps(m) for m in msgs], timeout_s)
    out = {"requests": msgs, "transport": {k: v for k, v in raw.items() if k != "stdout"}}
    if raw["status"] != "EXITED":
        return {**out, "status": raw["status"], "initialized": False}
    by_id, bad = _replies(raw["stdout"])
    init, tools = by_id.get(0, {}), by_id.get(1, {})
    names = [t.get("name") for t in (tools.get("result") or {}).get("tools", [])]
    ok = "result" in init and "check_design" in names
    return {**out, "status": "OK" if ok else "MCP_MALFORMED", "initialized": ok, "responses": [init, tools],
            "malformed_lines": bad, "server_info": (init.get("result") or {}).get("serverInfo"), "tools": names}


def check_design(brick: dict, rt: Runtime, time_limit_s: int = DEFAULT_TIME_LIMIT_S, transport=stdio_transport) -> dict:
    """D02-03: one real tools/call check_design. Returns the stand's own JSON untouched, plus the transcript."""
    req = {"jsonrpc": "2.0", "id": 1, "method": "tools/call",
           "params": {"name": "check_design", "arguments": {"brick": brick, "time_limit_s": time_limit_s}}}
    msgs = [{"jsonrpc": "2.0", "id": 0, "method": "initialize", "params": {"protocolVersion": "2025-06-18"}}, req]
    raw = transport(rt, [json.dumps(m) for m in msgs], time_limit_s + 60)
    out = {"request": req, "transport": {k: v for k, v in raw.items() if k != "stdout"},
           "brick_sha256": sha256_of(brick)}
    if raw["status"] != "EXITED":
        return {**out, "status": raw["status"], "stand_called": False, "stand_verdict": None, "stand_result": None}
    by_id, bad = _replies(raw["stdout"])
    reply = by_id.get(1)
    out["response"] = reply
    if bad:
        out["malformed_lines"] = bad
    if not isinstance(reply, dict) or "error" in reply or not isinstance(reply.get("result"), dict):
        status = "MCP_ERROR" if isinstance(reply, dict) and "error" in reply else "MCP_MALFORMED"
        return {**out, "status": status, "stand_called": None, "stand_verdict": None, "stand_result": None}
    content = reply["result"].get("content")
    text = content[0].get("text") if isinstance(content, list) and content and isinstance(content[0], dict) else None
    if not isinstance(text, str):
        return {**out, "status": "MCP_MALFORMED", "stand_called": None, "stand_verdict": None, "stand_result": None}
    if reply["result"].get("isError"):
        return {**out, "status": "MCP_TOOL_ERROR", "stand_called": None, "stand_verdict": None, "stand_result": None,
                "tool_error": text[:800]}
    try:
        result = json.loads(text)
    except ValueError:
        return {**out, "status": "MCP_MALFORMED", "stand_called": None, "stand_verdict": None, "stand_result": None,
                "text": text[:800]}
    if not isinstance(result, dict):
        return {**out, "status": "MCP_MALFORMED", "stand_called": None, "stand_verdict": None, "stand_result": None}
    return {**out, "status": "OK", "stand_called": True, "stand_verdict": result.get("verdict"), "stand_result": result}


def map_verdict(call: dict) -> str:
    if call.get("status") != "OK":
        return Z
    return VERDICT_MAP.get(call.get("stand_verdict"), Z)


def expected_judge(rt: Runtime) -> str:
    """ustand/judge_ztl.ztl_commit() reports `git rev-parse --short HEAD` of USTAND_ZTL; it must be the pinned ZTL."""
    return "ZTL " + rt.commits["ZTL"][:7]


def stand_dev_check(brick: dict, rt: Runtime, time_limit_s: int = DEFAULT_TIME_LIMIT_S) -> dict:
    """The stand's independent checker. ZTL Engineer's check_design runs the stand in its default work mode, where the
    checker does not gate an EARNED ("checker: not run (work mode ...)"). The stand's own CLI flag --dev
    (ustand/mode.py: "the independent checker re-reads every bound, every certificate ... an EARNED needs both") is
    the existing way to run it: `python -m ustand.stand <brick.json> --dev`, same pinned stand, same brick."""
    import tempfile
    t0 = time.time()
    with tempfile.TemporaryDirectory() as d:
        path = Path(d) / "brick.json"
        path.write_text(json.dumps(brick), encoding="utf-8")
        cmd = [rt.python, "-m", "ustand.stand", str(path), "--dev"]
        env = dict(rt.env(), PYTHONPATH=str(rt.stand), OPENBLAS_NUM_THREADS="1")
        try:
            p = subprocess.run(cmd, cwd=d, env=env, capture_output=True, encoding="utf-8", errors="replace",
                               timeout=time_limit_s)
        except subprocess.TimeoutExpired:
            return {"status": "TIMEOUT", "verdict": None, "command": "python -m ustand.stand brick.json --dev",
                    "seconds": round(time.time() - t0, 2)}
    try:
        res = json.loads(p.stdout)
    except ValueError:
        return {"status": "MALFORMED", "verdict": None, "stderr_tail": (p.stderr or "")[-800:],
                "command": "python -m ustand.stand brick.json --dev", "seconds": round(time.time() - t0, 2)}
    return {"status": "OK", "verdict": res.get("verdict"), "checked_by": res.get("checked_by"),
            "checker": res.get("checker"), "judge": res.get("judge"), "result": res,
            "command": "python -m ustand.stand brick.json --dev", "seconds": round(time.time() - t0, 2)}


def confirmed_verdict(call: dict, dev: dict | None, rt: Runtime) -> tuple[str, str]:
    """T or F only when the MCP result, the judge identity and the checker run all agree; anything else is Z."""
    v = map_verdict(call)
    if call.get("status") != "OK":
        return Z, call.get("status")
    if v == Z:
        return Z, f"STAND_{str(call.get('stand_verdict')).replace(' ', '_')}"
    judge = (call.get("stand_result") or {}).get("judge")
    if judge != expected_judge(rt):
        return Z, f"VERIFIER_IDENTITY_MISMATCH: judge {judge!r}, pinned {expected_judge(rt)!r}"
    if not dev or dev.get("status") != "OK":
        return Z, f"CHECKER_NOT_RUN: {(dev or {}).get('status')}"
    if VERDICT_MAP.get(dev.get("verdict"), Z) != v:
        return Z, f"CHECKER_DISAGREES: mcp {call.get('stand_verdict')} vs dev {dev.get('verdict')}"
    if v == T and "independent checker" not in str(dev.get("checked_by")):
        return Z, "CHECKER_NOT_CONFIRMED_EARNED"
    return v, "CONFIRMED: MCP check_design and the stand's independent checker (--dev) agree"


def checker_result(stand_result: dict | None) -> dict | None:
    """The stand's own checker evidence, as the stand reported it (no re-computation)."""
    if not isinstance(stand_result, dict):
        return None
    keep = ("checker", "checked_by", "judge", "how", "rests_on", "guaranteed", "guaranteed_unit", "requirements",
            "its_violating_point", "value_there", "requirement", "why", "reasons", "undecided", "stand")
    return {k: stand_result[k] for k in keep if k in stand_result}


# ---------------------------------------------------------------- engineering context and predicates
def engineering_context(*, source_repository, source_commit, source_file, source_sha256, drawing_revision,
                        spec_digest, requirements_digest) -> dict:
    return {"source_repository": source_repository, "source_commit": source_commit, "source_file": source_file,
            "source_sha256": source_sha256, "drawing_revision": drawing_revision, "spec_digest": spec_digest,
            "requirements_digest": requirements_digest, "policy_sha256": POLICY_SHA256}


def bind_source(ctx: dict, data: bytes) -> dict:
    """D02-08: the bytes actually read must be the bytes the context names; otherwise the binding is rejected."""
    got = hashlib.sha256(data).hexdigest()
    if got != ctx.get("source_sha256"):
        raise BindingRejected(f"SOURCE_SHA256_MISMATCH: context {ctx.get('source_sha256')} file {got}")
    return {**ctx, "source_bytes_verified": True}


def predicate(*, predicate_id, part_id, requirement, inputs, units, tolerances, tolerance_sources, brick=None,
              mandatory=True, missing=(), scope="", assumptions=(), controlled_case=False, origin="") -> dict:
    return {"predicate_id": predicate_id, "part_id": part_id, "requirement": requirement, "predicate_inputs": inputs,
            "units": units, "tolerances": tolerances, "tolerance_sources": tolerance_sources, "brick": brick,
            "mandatory": mandatory, "missing": list(missing), "scope": scope, "assumptions": list(assumptions),
            "controlled_case": controlled_case, "origin": origin}


def _missing(pred: dict, ctx: dict) -> tuple[list, list]:
    stand = [k for k in BLOCKS_STAND_CALL if pred.get(k) in (None, {}, [], "")]
    stand += [m for m in pred.get("missing", [])]
    if pred.get("brick") is None:
        stand.append("brick (no sourced engineering problem can be written)")
    if isinstance(pred.get("predicate_inputs"), dict):
        stand += [f"input {k}" for k, v in pred["predicate_inputs"].items()
                  if not isinstance(v, dict) or v.get("value") in (None, "") or not v.get("source")]
    admission = [k for k in CONTEXT_FIELDS if ctx.get(k) in (None, "")]
    return stand, admission


def evaluate(pred: dict, ctx: dict, rt: Runtime | None, time_limit_s: int = DEFAULT_TIME_LIMIT_S,
             transport=stdio_transport) -> dict:
    """One predicate through the real route. Missing evidence -> Z without a stand call (nothing is invented)."""
    stand_missing, admission_missing = _missing(pred, ctx)
    binding = {**{k: ctx.get(k) for k in CONTEXT_FIELDS}, "policy_sha256": ctx.get("policy_sha256"),
               **{k: pred.get(k) for k in PREDICATE_FIELDS},
               "brick_sha256": sha256_of(pred["brick"]) if pred.get("brick") is not None else None,
               "ztl_engineer_commit": rt.commits.get("ztl-engineer") if rt else None,
               "ztl_stand_commit": rt.commits.get("ztl-stand") if rt else None,
               "ztl_commit": rt.commits.get("ZTL") if rt else None}
    rec = {"predicate_id": pred["predicate_id"], "requirement": pred["requirement"], "mandatory": pred["mandatory"],
           "scope": pred["scope"], "assumptions": pred["assumptions"], "controlled_case": pred["controlled_case"],
           "origin": pred["origin"], "binding": binding, "missing_blocks_stand_call": stand_missing,
           "missing_blocks_admission": admission_missing}
    if stand_missing or rt is None:
        why = "MISSING_EVIDENCE" if stand_missing else "NO_RUNTIME"
        rec.update(verdict=Z, why=why, stand_called=False, stand_verdict=None, checker_result=None, mcp=None,
                   execution_timestamp=None)
        rec["binding"].update(stand_verdict=None, checker_result=None, execution_timestamp=None)
        return rec
    ts = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    call = check_design(pred["brick"], rt, time_limit_s, transport)
    dev = stand_dev_check(pred["brick"], rt, time_limit_s) if map_verdict(call) in (T, F) else None
    verdict, why = confirmed_verdict(call, dev, rt)
    chk = {"mcp_work_mode": checker_result(call.get("stand_result")),
           "independent_checker_dev_mode": None if dev is None else
           {k: dev.get(k) for k in ("status", "verdict", "checked_by", "checker", "judge", "command", "seconds")}}
    rec.update(verdict=verdict, why=why, stand_called=call.get("stand_called"), stand_verdict=call.get("stand_verdict"),
               checker_result=chk, mcp=call, execution_timestamp=ts)
    rec["binding"].update(stand_verdict=call.get("stand_verdict"), checker_result=chk, execution_timestamp=ts)
    rec["proof_id"] = sha256_of({k: rec["binding"][k] for k in (*CONTEXT_FIELDS, "policy_sha256", "predicate_id",
                                                                "brick_sha256", "stand_verdict")})
    return rec


def proof_valid_for(rec: dict, ctx: dict, brick: dict | None = None) -> tuple[bool, list]:
    """VALID_PROOF => SAME_SOURCE and SAME_REVISION and SAME_REQUIREMENTS and SAME_POLICY (and the same brick)."""
    b, reasons = rec["binding"], []
    for k in ("source_sha256", "source_commit", "source_file", "drawing_revision", "spec_digest",
              "requirements_digest", "policy_sha256"):
        if b.get(k) != ctx.get(k):
            reasons.append(f"{k.upper()}_CHANGED")
    if brick is not None and b.get("brick_sha256") != sha256_of(brick):
        reasons.append("BRICK_CHANGED")
    return (not reasons), reasons


# ---------------------------------------------------------------- strict aggregation and the two upper layers
def aggregate(results: list, ctx: dict, receipt: dict | None = None, admission_context: dict | None = None) -> dict:
    """WO-D02-D. Only mandatory predicates count; a result bound to another context is Z (never reused)."""
    mand = [r for r in results if r.get("mandatory")]
    per, stale = {}, {}
    for r in mand:
        ok, why = proof_valid_for(r, ctx)
        per[r["predicate_id"]] = r["verdict"] if ok else Z
        if not ok:
            stale[r["predicate_id"]] = why
    vals = list(per.values())
    pred_verdict = Z if not vals else F if F in vals else T if all(v == T for v in vals) else Z
    admission_missing = sorted({m for r in mand for m in r.get("missing_blocks_admission", [])})
    receipt_verdict = (receipt or {}).get("verdict", Z)
    if pred_verdict == F:
        eng = F
    elif pred_verdict == T and receipt_verdict == T and not admission_missing and not stale:
        eng = T
    else:
        eng = Z
    blockers = []
    if pred_verdict != T:
        blockers += [f"{k}={v}" for k, v in per.items() if v != T]
    if receipt_verdict != T:
        blockers.append(f"authenticated_receipt={receipt_verdict} ({(receipt or {}).get('code', 'NO_RECEIPT')})")
    blockers += [f"context field missing: {m}" for m in admission_missing]
    blockers += [f"stale proof {k}: {v}" for k, v in stale.items()]
    prod = production_admission(admission_context, eng)
    return {"schema": "legion.engineering.verdict.v1", "policy_sha256": POLICY_SHA256,
            "mandatory_predicates": per, "stale_proofs": stale, "predicate_layer_verdict": pred_verdict,
            "receipt_layer": receipt or {"verdict": Z, "code": "NO_RECEIPT"}, "ENGINEERING_VERDICT": eng,
            "blocking": blockers, "production_admission": prod,
            "procurement_authorized": False, "payment_authorized": False, "manufacturing_release": False,
            "supplier_requests_sent": 0, "paypal_calls": 0}


def _deal_rescue():
    P.import_path()
    from deal_rescue.industrial import admission, cad027_review, ztl_gate  # noqa: E402 (pinned, verified copy)
    return cad027_review, ztl_gate, admission


def authenticated_receipt(spec: dict, contract_id: str, env: dict | None = None, http_post=None, now_sec=None) -> dict:
    """The independent-verifier layer is Deal-Rescue's CAD-025 gate, unchanged: only an Ed25519-signed attestation
    from the configured verifier is T. No verifier configured -> Z; a refused receipt -> its gate code."""
    _, G, _ = _deal_rescue()
    try:
        r = G.engineering_admission(contract_id, spec, env=env if env is not None else {}, http_post=http_post,
                                    now_sec=now_sec)
        return {"verdict": T, "code": "ATTESTATION_VERIFIED", "gate": "deal_rescue.industrial.ztl_gate",
                "detail": r}
    except G.GateError as e:
        # a receipt layer that is not T is Z for the engineering verdict: a refused or absent receipt says nothing
        # about the design (only a predicate F does); the gate's own code is kept
        return {"verdict": Z, "code": e.code, "refused": e.code not in (
                    "TRUSTED_ZTL_SERVICE_NOT_CONFIGURED", "INDEPENDENT_ZTL_VERIFIER_UNAVAILABLE"),
                "gate": "deal_rescue.industrial.ztl_gate", "admitted": False}


def production_admission(admission_context: dict | None, engineering_verdict: str) -> dict:
    """Deal-Rescue admission.decide with no independent verifier bound: every obligation stays Z or F, so the
    production verdict is never T here. Recorded, never executed."""
    _, _, A = _deal_rescue()
    d = A.decide(admission_context or {}, {}, independent_verifier=None)
    return {"verdict": d["verdict"], "why": d.get("why", d.get("next")), "engineering_input": engineering_verdict,
            "missing": d.get("missing"),
            "execute_supplier_order": d["execute_supplier_order"], "execute_paypal": d["execute_paypal"],
            "module": "deal_rescue.industrial.admission.decide"}


# ---------------------------------------------------------------- the reBot case (WO-D02-C / D02-F)
REBOT_CASE_SCOPE = ("the pinned reBot B601-DM STEP and readme as emitted by step_intake (WO-D01); predicates whose "
                    "inputs and requirement are not stated by those sources stay Z and are never sent to the stand")


def rebot_context(xcaf: dict, readme_sha: str, bom: dict | None, preds: list) -> dict:
    """The engineering context of the reBot sources. No drawing exists (STEP + readme, path C1), so drawing_revision
    stays missing; spec_digest and requirements_digest are Deal-Rescue's own (ztl_gate.spec_digest of cad025_spec,
    cad027_review.requirements_digest)."""
    R, G, _ = _deal_rescue()
    ref = P.load_pin()["reference_cad"]
    spec_digest = None
    if bom is not None:
        try:
            spec_digest = G.spec_digest(R.cad025_spec(bom, xcaf["sha256"], readme_sha))
        except G.GateError:
            spec_digest = None
    pinned = xcaf["sha256"] == ref["files"]["step"]["sha256"]
    return engineering_context(
        source_repository=ref["repository"] if pinned else "LEGION-Deal-Rescue tests/test_cad027_demo.py (fixture)",
        source_commit=ref["commit"] if pinned else P.load_pin()["commit"],
        source_file=ref["files"]["step"]["path"] if pinned else xcaf.get("file"),
        source_sha256=xcaf["sha256"], drawing_revision=None, spec_digest=spec_digest,
        requirements_digest=R.requirements_digest(preds))


def extraction_result(ctx: dict, bom_status: str, bom_stage: dict) -> dict:
    """The CAD/BOM extraction obligation (WO-D01 result, not a stand call): T only where D01 established it."""
    binding = {**{k: ctx.get(k) for k in CONTEXT_FIELDS}, "policy_sha256": ctx.get("policy_sha256"),
               "part_id": "reBot B601-DM assembly", "predicate_id": "cad_bom_extraction",
               "predicate_inputs": {k: bom_stage.get(k) for k in ("mandatory_positions", "mandatory_positions_matched",
                                                                   "mandatory_instances_readme",
                                                                   "mandatory_instances_step")},
               "units": None, "tolerances": None, "tolerance_sources": None, "brick_sha256": None,
               "stand_verdict": None, "checker_result": None, "execution_timestamp": None}
    return {"predicate_id": "cad_bom_extraction", "requirement": "every mandatory BOM position and instance of the "
            "readme is present in the STEP (Deal-Rescue cad027_review.reconcile)", "mandatory": True,
            "verdict": bom_status, "why": "WO-D01 reconciliation (OpenCascade XCAF vs readme); not a ZTL proof",
            "stand_called": False, "binding": binding, "missing_blocks_stand_call": [],
            "missing_blocks_admission": [k for k in CONTEXT_FIELDS if ctx.get(k) in (None, "")],
            "origin": "legion/engineering/step_intake.py stage bom", "scope": "structure only", "assumptions": [],
            "controlled_case": False}


def rebot_predicates(xcaf: dict, readme_text: str, perf_text: str | None, reqs: list) -> list:
    """The mandatory engineering predicates, built only from the pinned sources (Deal-Rescue's own builders)."""
    R, _, _ = _deal_rescue()
    dr = {p["id"]: p for p in R.production_predicates(xcaf, readme_text, perf_text)}
    rail = dr["rail_length_tolerance"]
    try:
        brick = R.rail_length_brick(xcaf, readme_text)          # no tolerance argument: none is sourced
        why = None
    except R.ToleranceUnsupported as e:
        brick, why = None, str(e)
    out = [predicate(
        predicate_id="rail_length_tolerance", part_id="RAIL-170 (MGN9-170mm, purchased)",
        requirement=rail["requirement"],
        inputs={k: {"value": v["value"], "source": v["source"]} for k, v in rail["inputs"].items()},
        units={"L_cad": "mm", "L_spec": "mm", "dL": "mm"}, tolerances=None, tolerance_sources=None, brick=brick,
        missing=rail["missing"] + ([why] if why else []),
        scope="nominal CAD length of the purchased rail against its purchase specification",
        origin="Deal-Rescue cad027_review.production_predicates / rail_length_brick @6d5563a")]
    load = dr["joint2_load_torque"]
    out.append(predicate(
        predicate_id="joint2_load_torque", part_id="joint 2 motor", requirement=load["requirement"],
        inputs={k: {"value": v["value"], "source": v["source"]} for k, v in (load.get("inputs") or {}).items()} or None,
        units=None, tolerances=None, tolerance_sources=None, brick=None, missing=load["missing"],
        scope="holding torque at the recommended load", origin="Deal-Rescue cad027_review.production_predicates"))
    cnc = [r for r in reqs if r.get("group") == "cnc"]
    out.append(predicate(
        predicate_id="cnc_material_evidence", part_id=f"{len(cnc)} CNC machined parts",
        requirement="each CNC part's material grade is evidenced (certificate or datasheet) for the stated alloy",
        inputs={r["part_id"]: {"value": r["material"], "source": r["material_source"]} for r in cnc} or None,
        units=None, tolerances={r["part_id"]: r["tolerance"] for r in cnc} or None,
        tolerance_sources={r["part_id"]: r["tolerance_source"] for r in cnc} or None, brick=None,
        missing=["material grade certificates (no certificate or datasheet in the sources)"],
        scope="material evidence, not geometry", origin="step_intake stage requirements (readme lines)"))
    return out


def rebot_case(out: dict, xcaf: dict, readme_text: str, readme_sha: str, rt: Runtime | None,
               perf_text: str | None = None, receipt_env: dict | None = None) -> dict:
    """Stage 4 of the intake, on what stages 1-3 emitted. Returns the full verdict record; never T without new,
    independently supported requirements and an authenticated receipt."""
    R, _, _ = _deal_rescue()
    bom = R.reconcile(xcaf, R.parse_readme(readme_text), readme_sha)
    preds = rebot_predicates(xcaf, readme_text, perf_text, out["stages"]["requirements"]["parts"])
    dr_preds = R.production_predicates(xcaf, readme_text, perf_text)
    ctx = rebot_context(xcaf, readme_sha, bom, dr_preds)
    results = [extraction_result(ctx, out["stages"]["bom"]["status"], out["stages"]["bom"])]
    results += [evaluate(p, ctx, rt) for p in preds]
    spec = R.cad025_spec(bom, xcaf["sha256"], readme_sha)
    receipt = authenticated_receipt(spec, "LMFG_REBOT_B601", env=receipt_env)
    agg = aggregate(results, ctx, receipt)
    return {"scope": REBOT_CASE_SCOPE, "context": ctx, "predicates": results, "verdict": agg,
            "missing_for_engineering_T": list(R.MISSING_FOR_ENGINEERING_T)}


def controlled_rail_cases(xcaf: dict, readme_text: str, readme_sha: str, rt: Runtime, tol: tuple,
                          tol_source: str) -> list:
    """WO-D02-E. The same Deal-Rescue rail brick with an explicitly identified, NON-reBot tolerance assumption:
      positive: the readme as pinned (MGN9-170mm against the CAD length)
      negative: the same model, the purchase spec deliberately changed to MGN9-150mm (requirement violated by 20 mm)
    Both go through MCP -> stand -> checker. Neither is evidence of reBot compliance (controlled_case=True)."""
    R, _, _ = _deal_rescue()
    out = []
    for case, text, change in (
            ("controlled_positive", readme_text, None),
            ("controlled_negative", readme_text.replace("MGN9-170mm", "MGN9-150mm"),
             "readme purchase spec MGN9-170mm replaced by MGN9-150mm; expected: the stand refutes dL within the "
             "window, dL = 20 mm")):
        brick = R.rail_length_brick(xcaf, text, tol, tol_source)
        dr_preds = R.production_predicates(xcaf, text, None)
        ctx = rebot_context(xcaf, hashlib.sha256(text.encode("utf-8")).hexdigest() if change else readme_sha,
                            None, dr_preds)
        p = predicate(
            predicate_id=f"rail_length_{case}", part_id="RAIL-170 (MGN9, purchased)",
            requirement=f"dL = L_cad - L_spec within [{tol[0]}, {tol[1]}] mm",
            inputs={k: {"value": v["value"], "source": v["ground"]} for k, v in brick["quantities"].items()
                    if v.get("role") == "given"},
            units={k: v["unit"] for k, v in brick["quantities"].items()}, tolerances={"dL": list(tol)},
            tolerance_sources={"dL": tol_source}, brick=brick, mandatory=True,
            scope="controlled verification case: nominal CAD rail length vs purchase spec under an assumed window",
            assumptions=[f"tolerance window {tol} mm: {tol_source}", "STEP length is the nominal model value"],
            controlled_case=True, origin="Deal-Rescue cad027_review.rail_length_brick @6d5563a")
        r = evaluate(p, ctx, rt)
        r["deliberate_change"] = change
        r["admissible_for_rebot"] = False
        out.append(r)
    return out
