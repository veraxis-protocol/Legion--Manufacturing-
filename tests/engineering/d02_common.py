"""WO-D02 scenarios shared by the D02 tests and tools/d02_run.py (one implementation, asserted by the tests and
serialized as evidence by the tool). Every stand result here comes from the real route:
  _deps/ztl-engineer/mcp_server.py (stdio) -> check_design -> python -m ustand.stand -> ZTL judge,
plus the stand's own independent checker (python -m ustand.stand --dev). Nothing is mocked except where a function
name says TRANSPORT_FAULT_INJECTION (isolated transport-failure tests, labelled as such in the evidence).

Environment:
  LMFG_REAL_CAD=1   the real reBot STEP through OpenCascade (CI engineering-verifier job); a missing input is an error
  LMFG_ZTL_STRICT=1 the CI verifier job: every optional dependency (cryptography) must be present
"""
from __future__ import annotations

import base64
import copy
import hashlib
import importlib.util
import json
import os
import tempfile
import time
from pathlib import Path

from legion.engineering import pinned_source as P

REAL = os.environ.get("LMFG_REAL_CAD") == "1"
STRICT = os.environ.get("LMFG_ZTL_STRICT") == "1"
STAND_EXAMPLES = ["examples/divider-1pct-req-1pct.json", "examples/divider-1pct-req-0.5pct.json",
                  "examples/tasks/t1-thermal-heatsink.json", "examples/tasks/t6-truss-three-bars.json"]
_CACHE: dict = {}


def A():
    from legion.engineering import ztl_adapter
    return ztl_adapter


def runtime():
    if "rt" not in _CACHE:
        P.materialize()
        _CACHE["rt"] = A().runtime(materialize=True)
    return _CACHE["rt"]


def dr():
    """Deal-Rescue's own CAD-027 test module (MINI_XCAF, MINI_README, TEST_ONLY_TOL), pinned and verified."""
    if "dr" not in _CACHE:
        P.materialize()
        P.import_path()
        spec = importlib.util.spec_from_file_location("dr_test_cad027_demo", P.DEPS / "tests" / "test_cad027_demo.py")
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        _CACHE["dr"] = mod
    return _CACHE["dr"]


def fixture_inputs():
    m = dr()
    return copy.deepcopy(m.MINI_XCAF), m.MINI_README, hashlib.sha256(m.MINI_README.encode("utf-8")).hexdigest()


def tolerance_assumption():
    m = dr()
    return m.TEST_ONLY_TOL[0], m.TEST_ONLY_TOL[1] + " (LEGION-Deal-Rescue tests/test_cad027_demo.py TEST_ONLY_TOL @6d5563a)"


def real_inputs():
    """The pinned reBot STEP read by OpenCascade XCAF (Deal-Rescue cad_xcaf), and the pinned readme."""
    if "real" not in _CACHE:
        import OCP  # noqa: F401  (with LMFG_REAL_CAD=1 an ImportError is an error, never a skip)
        files = P.fetch_reference_cad()
        pin = P.load_pin()
        P.import_path()
        from deal_rescue.industrial import cad_xcaf
        xcaf = cad_xcaf.read_assembly(Path(files["step"]["path"]), pin["reference_cad"]["files"]["step"]["sha256"])
        readme = Path(files["readme"]["path"]).read_text(encoding="utf-8")
        _CACHE["real"] = {"files": files, "xcaf": xcaf, "readme": readme,
                          "readme_sha": hashlib.sha256(Path(files["readme"]["path"]).read_bytes()).hexdigest()}
    return _CACHE["real"]


# ---------------------------------------------------------------- D02-A / B
def pins():
    if "pins" not in _CACHE:
        manifest = P.load_manifest()
        done = P.materialize_all(manifest)
        _CACHE["pins"] = {"repositories": done,
                          "unchanged_after_use": {r["name"]: P.verify_tree(r) for r in manifest["repositories"]},
                          "deal_rescue": {k: v for k, v in P.materialize().items() if k != "files"}}
    return _CACHE["pins"]


def mcp_initialize():
    if "init" not in _CACHE:
        _CACHE["init"] = A().initialize(runtime())
    return _CACHE["init"]


def stand_examples():
    """The four existing ztl-stand examples through MCP and through the stand's checker; verdicts as observed."""
    if "examples" not in _CACHE:
        rt, a = runtime(), A()
        out = []
        for e in STAND_EXAMPLES:
            data = (rt.stand / e).read_bytes()
            brick = json.loads(data)
            call = a.check_design(brick, rt)
            dev = a.stand_dev_check(brick, rt)
            v, why = a.confirmed_verdict(call, dev, rt)
            out.append({"example": e, "source_repository": "https://github.com/inventor1975/ztl-stand",
                        "source_commit": rt.commits["ztl-stand"], "source_sha256": hashlib.sha256(data).hexdigest(),
                        "brick_sha256": a.sha256_of(brick), "mcp": call, "stand_verdict": call.get("stand_verdict"),
                        "independent_checker": {k: dev.get(k) for k in ("status", "verdict", "checked_by", "checker",
                                                                        "judge", "command", "seconds")},
                        "legion_verdict": v, "why": why,
                        "scope": "ztl-stand's own example problem: integration health only, says nothing about reBot"})
        _CACHE["examples"] = out
    return _CACHE["examples"]


def deal_rescue_check_design_parity():
    """The reference implementation (Deal-Rescue cad027_review.check_design) on the same brick, same server."""
    rt, a = runtime(), A()
    R, _, _ = a._deal_rescue()
    brick = json.loads((rt.stand / STAND_EXAMPLES[0]).read_text(encoding="utf-8"))
    old = {k: os.environ.get(k) for k in ("ZTL_ENGINEER_STAND", "USTAND_ZTL")}
    os.environ.update(ZTL_ENGINEER_STAND=str(rt.stand), USTAND_ZTL=str(rt.ztl))
    try:
        ref = R.check_design(brick, str(rt.engineer))
    finally:
        for k, v in old.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v
    ours = a.check_design(brick, rt)
    return {"deal_rescue_verdict": ref.get("verdict"), "legion_adapter_verdict": ours.get("stand_verdict"),
            "deal_rescue_judge": ref.get("judge"), "legion_judge": (ours.get("stand_result") or {}).get("judge")}


# ---------------------------------------------------------------- D02-E controlled cases
def controlled(real: bool = False):
    key = f"controlled_{real}"
    if key not in _CACHE:
        if real:
            r = real_inputs()
            xcaf, readme, sha = r["xcaf"], r["readme"], r["readme_sha"]
        else:
            xcaf, readme, sha = fixture_inputs()
        tol, src = tolerance_assumption()
        cases = A().controlled_rail_cases(xcaf, readme, sha, runtime(), tol, src)
        for c in cases:
            c["input_basis"] = ("the pinned reBot STEP (OpenCascade XCAF) and readme" if real else
                                "Deal-Rescue's offline CAD-027 fixture (MINI_XCAF / MINI_README), not the real STEP")
        _CACHE[key] = cases
    return _CACHE[key]


# ---------------------------------------------------------------- D02-F reBot
def rebot(real: bool = False):
    key = f"rebot_{real}"
    if key not in _CACHE:
        from legion.engineering import step_intake as S
        if real:
            files, pin = P.fetch_reference_cad(), P.load_pin()
            res = S.step_intake(files["step"]["path"], files["readme"]["path"],
                                pin["reference_cad"]["files"]["step"]["sha256"], "Reference", "REBOT-B601",
                                verifier=runtime())
        else:
            xcaf, readme, sha = fixture_inputs()
            res = S.assemble({"stages": {}, "engineering_verdict": "Z"}, xcaf, readme, sha, "Fairview", "REBOT-MINI",
                             verifier=runtime())
        res["input_basis"] = ("the pinned reBot STEP and readme" if real else
                              "Deal-Rescue's offline CAD-027 fixture (MINI_XCAF / MINI_README)")
        _CACHE[key] = res
    return _CACHE[key]


# ---------------------------------------------------------------- negatives
def missing_rail_tolerance():
    """D02-06: the rail predicate exactly as the sources allow: no tolerance stated for the purchased rail."""
    res = rebot(False)
    p = next(x for x in res["stages"]["verification"]["predicates"] if x["predicate_id"] == "rail_length_tolerance")
    R, _, _ = A()._deal_rescue()
    _, readme, _ = fixture_inputs()
    return {"predicate": p, "deal_rescue_tolerance_finding": R.tolerance_for_purchased_rail(readme)}


def missing_material():
    res = rebot(False)
    p = next(x for x in res["stages"]["verification"]["predicates"] if x["predicate_id"] == "cnc_material_evidence")
    # the same predicate with the material input itself removed (the stated alloy deleted from the inputs)
    a = A()
    q = a.predicate(predicate_id="material_input_removed", part_id="CNC part", requirement="material evidenced",
                    inputs={"material": {"value": None, "source": None}}, units={"material": "-"},
                    tolerances={"-": "-"}, tolerance_sources={"-": "-"},
                    brick={"stand": "ztl-stand/1", "quantities": {}}, scope="negative: material absent")
    ctx = res["stages"]["verification"]["context"]
    return {"cnc_material_evidence": p, "material_input_removed": a.evaluate(q, ctx, runtime())}


def malformed_bricks():
    """D02-11: real stand, real MCP, bricks it cannot judge."""
    if "malformed" in _CACHE:
        return _CACHE["malformed"]
    rt, a = runtime(), A()
    out = []
    for label, brick in (("quantities is not an object", {"stand": "ztl-stand/1", "quantities": "garbage"}),
                         ("law references an unknown quantity", {"stand": "ztl-stand/1", "quantities": {
                             "x": {"role": "given", "value": "1", "unit": "mm"}}, "slots": {}, "catalog": {},
                             "laws": [{"zfl": "y == x + q"}], "requirements": [{"quantity": "y", "op": "<=",
                                                                                "value": "2"}]}),
                         ("empty object", {})):
        call = a.check_design(brick, rt)
        v, why = a.confirmed_verdict(call, None, rt)
        out.append({"case": label, "brick": brick, "status": call["status"], "stand_verdict": call.get("stand_verdict"),
                    "tool_error": call.get("tool_error"), "legion_verdict": v, "why": why,
                    "stand_why": str((call.get("stand_result") or {}).get("why"))[:400], "mcp": call})
    # not a JSON object at all: the server's own argument check (isError)
    call = a.check_design(["not", "an", "object"], rt)  # type: ignore[arg-type]
    out.append({"case": "brick is a list", "status": call["status"], "tool_error": call.get("tool_error"),
                "legion_verdict": a.confirmed_verdict(call, None, rt)[0], "mcp": call})
    _CACHE["malformed"] = out
    return out


def transport_fault_injection():
    """D02-12. TRANSPORT_FAULT_INJECTION (labelled mock): the transport returns what a broken server could return.
    No stand outcome is mocked; each must map to Z, never F."""
    rt, a = runtime(), A()
    brick = json.loads((rt.stand / STAND_EXAMPLES[1]).read_text(encoding="utf-8"))   # a REFUTED brick
    faults = {
        "garbage on stdout": "this is not json\n",
        "json-rpc error": json.dumps({"jsonrpc": "2.0", "id": 1, "error": {"code": -32603, "message": "boom"}}),
        "result without content": json.dumps({"jsonrpc": "2.0", "id": 1, "result": {}}),
        "content text not json": json.dumps({"jsonrpc": "2.0", "id": 1, "result": {"content": [
            {"type": "text", "text": "REFUTED (but not as JSON)"}]}}),
        "reply for another id": json.dumps({"jsonrpc": "2.0", "id": 7, "result": {"content": [
            {"type": "text", "text": json.dumps({"verdict": "REFUTED"})}]}}),
        "empty stdout": "",
    }
    out = []
    for label, stdout in faults.items():
        def transport(_rt, _lines, _t, s=stdout):
            return {"status": "EXITED", "returncode": 0, "stdout": s, "stderr_tail": "", "seconds": 0.0}
        call = a.check_design(brick, rt, transport=transport)
        out.append({"case": label, "label": "TRANSPORT_FAULT_INJECTION", "status": call["status"],
                    "legion_verdict": a.confirmed_verdict(call, None, rt)[0]})
    return out


def server_unavailable():
    """D02-13: a real attempt against a folder without the server (no mock)."""
    a = A()
    rt = runtime()
    with tempfile.TemporaryDirectory() as d:
        gone = a.Runtime(engineer=Path(d), stand=rt.stand, ztl=rt.ztl, commits=rt.commits)
        brick = json.loads((rt.stand / STAND_EXAMPLES[0]).read_text(encoding="utf-8"))
        call = a.check_design(brick, gone)
        init = a.initialize(gone)
        # the real server, started with no stand behind it: it dies on import before answering
        broken = a.Runtime(engineer=rt.engineer, stand=Path(d), ztl=rt.ztl, commits=rt.commits)
        crash = a.check_design(brick, broken)
    return {"check_design_status": call["status"], "initialize_status": init["status"],
            "legion_verdict": a.confirmed_verdict(call, None, rt)[0],
            "server_crashes_on_start": {"status": crash["status"],
                                        "legion_verdict": a.confirmed_verdict(crash, None, rt)[0],
                                        "stderr_tail": crash["transport"].get("stderr_tail", "")[-400:]}}


def timeout():
    """D02-14: the real server, a real process timeout (the transport's limit set below the server's start-up)."""
    rt, a = runtime(), A()
    brick = json.loads((rt.stand / STAND_EXAMPLES[0]).read_text(encoding="utf-8"))
    call = a.check_design(brick, rt, transport=lambda r, lines, t: a.stdio_transport(r, lines, 0.05))
    return {"status": call["status"], "legion_verdict": a.confirmed_verdict(call, None, rt)[0],
            "transport": call["transport"]}


def mixed(second: str):
    """D02-15 / D02-16: two mandatory predicates in ONE engineering context, both through the real route.
    first: the controlled rail predicate (EARNED); second: 'Z' = the rail tolerance as sourced (missing),
    'F' = the same rail brick with the window deliberately set to [0.01, 0.02] mm, which excludes the nominal dL = 0."""
    a, rt = A(), runtime()
    R, _, _ = a._deal_rescue()
    xcaf, readme, sha = fixture_inputs()
    tol, src = tolerance_assumption()
    ctx = a.rebot_context(xcaf, sha, None, R.production_predicates(xcaf, readme, None))
    b1 = R.rail_length_brick(xcaf, readme, tol, src)
    p1 = a.predicate(predicate_id="rail_within_assumed_window", part_id="RAIL-170", requirement="dL within window",
                     inputs={"L_cad": {"value": b1["quantities"]["L_cad"]["value"], "source": "fixture XCAF bbox"},
                             "L_spec": {"value": b1["quantities"]["L_spec"]["value"], "source": "fixture readme"}},
                     units={"dL": "mm"}, tolerances={"dL": list(tol)}, tolerance_sources={"dL": src}, brick=b1,
                     controlled_case=True)
    if second == "Z":
        p2 = a.predicate(predicate_id="rail_manufacturing_tolerance", part_id="RAIL-170",
                         requirement="rail length within its manufacturing tolerance",
                         inputs={"L_cad": {"value": "170.000", "source": "fixture XCAF bbox"}}, units={"dL": "mm"},
                         tolerances=None, tolerance_sources=None, brick=None,
                         missing=["manufacturer length tolerance for MGN9-170 rail (datasheet)"])
    else:
        win = ("0.01", "0.02")
        b2 = R.rail_length_brick(xcaf, readme, win, "WO-LMFG-003 D02-16: window deliberately excludes dL = 0")
        p2 = a.predicate(predicate_id="rail_offset_window_violated", part_id="RAIL-170",
                         requirement="dL within [0.01, 0.02] mm (deliberately violated)",
                         inputs={"L_cad": {"value": b2["quantities"]["L_cad"]["value"], "source": "fixture XCAF bbox"},
                                 "L_spec": {"value": b2["quantities"]["L_spec"]["value"], "source": "fixture readme"}},
                         units={"dL": "mm"}, tolerances={"dL": list(win)},
                         tolerance_sources={"dL": "deliberate violation"}, brick=b2, controlled_case=True)
    results = [a.evaluate(p1, ctx, rt), a.evaluate(p2, ctx, rt)]
    # even a receipt claimed as T (SYNTHETIC, not from a verifier) cannot lift a Z or F predicate to T
    agg_no_receipt = a.aggregate(results, ctx)
    agg_claimed = a.aggregate(results, ctx, receipt={"verdict": "T", "code": "SYNTHETIC_CLAIM_FOR_TEST"})
    return {"results": results, "aggregate": agg_no_receipt, "aggregate_with_synthetic_receipt_claim": agg_claimed}


def deal_rescue_partial_proof_demo():
    """WO-D02-D: Deal-Rescue cad027_review.ztl_review (pinned, unchanged) given one EARNED and one OPEN predicate
    aggregates over decided predicates only. Its two inner calls are replaced for this demonstration only."""
    R, _, _ = A()._deal_rescue()
    saved = R.production_predicates, R.integration_test_scenario
    R.production_predicates = lambda *a, **k: [{"id": "p1", "verdict": "EARNED", "stand_called": True},
                                               {"id": "p2", "verdict": "OPEN", "stand_called": False}]
    R.integration_test_scenario = lambda *a, **k: {"label": "not run in this demonstration"}
    try:
        out = R.ztl_review({}, "", None, None)
    finally:
        R.production_predicates, R.integration_test_scenario = saved
    return {"deal_rescue_production_verdict": out["production_verdict"], "predicates": ["EARNED", "OPEN"],
            "label": "DEMONSTRATION: inner calls replaced; shows why this aggregation is not used for admission"}


# ---------------------------------------------------------------- D02-17 receipts (Deal-Rescue ztl_gate, CAD-025)
SYNTH_DOC, SYNTH_POLICY, SYNTH_STAND = "b" * 64, "f" * 64, "d" * 40
SYNTH_CATEGORIES = ("material", "dimensions", "tolerances", "manufacturing_process", "inspection", "functional")


def synthetic_spec(drawing: str = "e" * 64) -> dict:
    """SYNTHETIC complete spec in the CAD-025 shape (as in Deal-Rescue tests/test_cad025_ztl_gate.py): it exists only
    so the gate reaches the receipt checks; it describes no real part."""
    return {"drawing_sha256": drawing, "drawing_revision": "SYNTHETIC-REV-A",
            "source_documents": [{"document_id": "SYNTHETIC_STEP", "kind": "CAD_STEP", "sha256": drawing},
                                 {"document_id": "SYNTHETIC_SPEC", "kind": "TEST_SPEC", "sha256": SYNTH_DOC}],
            "bom": [{"part_number": "SYNTH-PART", "quantity": 1, "material": "SYNTHETIC", "material_grade": "SYNTHETIC",
                     "manufacturing_process": "SYNTHETIC", "dimensional_requirements": "SYNTHETIC",
                     "dimensional_tolerances": "SYNTHETIC", "surface_finish": "SYNTHETIC",
                     "inspection_requirements": "SYNTHETIC", "functional_requirements": "SYNTHETIC",
                     "source_sha256": SYNTH_DOC}],
            "requirements": [{"id": "synth_" + k, "part_number": "SYNTH-PART", "category": k,
                              "statement": "SYNTHETIC_" + k, "source_sha256": SYNTH_DOC} for k in SYNTH_CATEGORIES]}


def _b64(x: bytes) -> str:
    return base64.urlsafe_b64encode(x).rstrip(b"=").decode("ascii")


def have_cryptography() -> bool:
    try:
        import cryptography  # noqa: F401
        return True
    except ImportError:
        return False


class TestSigner:
    """A key generated in memory for this test run only (never stored); kid TEST_KEY_ONLY."""

    def __init__(self):
        from cryptography.hazmat.primitives import serialization
        from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
        self.key = Ed25519PrivateKey.generate()
        pem = self.key.public_key().public_bytes(serialization.Encoding.PEM,
                                                 serialization.PublicFormat.SubjectPublicKeyInfo).decode()
        self.env = {"LEGION_ZTL_VERIFY_KEY_PEM": pem, "LEGION_ZTL_VERIFY_KID": "TEST_KEY_ONLY",
                    "LEGION_ZTL_CURRENT_EPOCH": "epoch_2", "LEGION_ZTL_POLICY_SHA256": SYNTH_POLICY,
                    "LEGION_ZTL_STAND_COMMIT": SYNTH_STAND,
                    "LEGION_ZTL_ATTESTATION_URL": "https://verifier.example.com/engineering/v1",
                    "LEGION_BACKEND_TOKEN": "TEST-ONLY-NOT-A-CREDENTIAL"}

    def jws(self, spec: dict, epoch="epoch_2", issued=None, ttl=1200, key=None) -> str:
        _, G, _ = A()._deal_rescue()
        now = int(time.time()) if issued is None else issued
        body = {"schema": "LEGION_ZTL_ENGINEERING_ATTESTATION_V1", "audience": "LEGION_PROCUREMENT",
                "proof_scope": "MANUFACTURING_REQUIREMENTS", "contract_id": "contract_d02_17",
                "spec_digest": G.spec_digest(spec), "drawing_sha256": spec["drawing_sha256"],
                "policy_sha256": SYNTH_POLICY, "epoch": epoch, "issued_at": now, "expires_at": now + ttl,
                "verdict": "EARNED", "ztl": {"engine": "ztl-stand", "verdict": "EARNED", "commit": SYNTH_STAND,
                                             "evidence_sha256": "c" * 64},
                "coverage": {"all_parts_accounted": True, "verified_parts": 1, "required_checks": 6,
                             "part_numbers": ["SYNTH-PART"]},
                "checks": [{"id": r["id"], "verdict": "EARNED", "proof_sha256": "c" * 64, "source_sha256": SYNTH_DOC}
                           for r in spec["requirements"]]}
        head = {"alg": "EdDSA", "typ": "LEGION-ZTL-ENGINEERING-V1", "kid": "TEST_KEY_ONLY"}
        seg = _b64(json.dumps(head).encode()) + "." + _b64(json.dumps(body).encode())
        return seg + "." + _b64((key or self.key).sign(seg.encode()))


def receipts():
    """Every receipt case through Deal-Rescue's ztl_gate.engineering_admission (unchanged). Returns observed codes."""
    a = A()
    spec = synthetic_spec()
    post = lambda jws: (lambda url, body, token: {"attestation_jws": jws})  # noqa: E731
    out = {"no_verifier_configured": a.authenticated_receipt(spec, "contract_d02_17", env={})}
    env_only = {k: "x" for k in ("LEGION_ZTL_ATTESTATION_URL",)}
    out["no_verifier_configured_partial_env"] = a.authenticated_receipt(spec, "contract_d02_17", env=env_only)
    signer_env = {"LEGION_ZTL_VERIFY_KEY_PEM": "-", "LEGION_ZTL_VERIFY_KID": "TEST_KEY_ONLY",
                  "LEGION_ZTL_CURRENT_EPOCH": "epoch_2", "LEGION_ZTL_POLICY_SHA256": SYNTH_POLICY,
                  "LEGION_ZTL_STAND_COMMIT": SYNTH_STAND,
                  "LEGION_ZTL_ATTESTATION_URL": "https://verifier.example.com/engineering/v1",
                  "LEGION_BACKEND_TOKEN": "TEST-ONLY-NOT-A-CREDENTIAL"}
    out["unsigned_receipt"] = a.authenticated_receipt(spec, "contract_d02_17", env=signer_env, http_post=post(None))
    stand_json = json.dumps({"verdict": "EARNED", "judge": "ZTL local"})
    out["local_mcp_result_as_receipt"] = a.authenticated_receipt(spec, "contract_d02_17", env=signer_env,
                                                                 http_post=post(stand_json))
    out["three_part_garbage"] = a.authenticated_receipt(spec, "contract_d02_17", env=signer_env,
                                                        http_post=post("a.b.c"))
    if have_cryptography():
        s = TestSigner()
        from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
        now = int(time.time())
        out["fresh_test_signed_receipt_POSITIVE_CONTROL"] = a.authenticated_receipt(
            spec, "contract_d02_17", env=s.env, http_post=post(s.jws(spec)))
        out["replayed_from_previous_epoch"] = a.authenticated_receipt(
            spec, "contract_d02_17", env=s.env, http_post=post(s.jws(spec, epoch="epoch_1")))
        out["replayed_after_expiry"] = a.authenticated_receipt(
            spec, "contract_d02_17", env=s.env, http_post=post(s.jws(spec, issued=now - 7200, ttl=1200)))
        changed = synthetic_spec()
        changed["bom"][0]["material"] = "SYNTHETIC_CHANGED"
        out["replayed_onto_changed_spec"] = a.authenticated_receipt(
            changed, "contract_d02_17", env=s.env, http_post=post(s.jws(spec)))
        out["signed_by_untrusted_key"] = a.authenticated_receipt(
            spec, "contract_d02_17", env=s.env, http_post=post(s.jws(spec, key=Ed25519PrivateKey.generate())))
    else:
        out["signed_cases"] = {"verdict": "NOT_RUN", "code": "cryptography not installed in this environment"}
    return out
