"""WO-D01: Drawing / STEP -> Engineering Intake -> BOM -> Requirements -> Verification, reusing LEGION-Deal-Rescue.

All CAD work is done by the pinned Deal-Rescue modules (cad_xcaf, cad_bom, cad027_review), imported from the verified
copy that pinned_source.py writes. This module only orders the stages and hands the result to Anthropic's contracts:
each CNC part becomes a path-C1 `geometry-estimate` (contracts/geometry-estimate.md) inside a B05 envelope.

What is never done: a material or tolerance read from geometry, a feature list recognised from faces, an hours or a
price figure. Stage 4 (verification) is Z unless a ZTL runtime is passed (WO-D02, ztl_adapter.rebot_case); even then
it is F or Z, never T, without an independently authenticated receipt.
"""
from __future__ import annotations

import hashlib
from pathlib import Path

from legion.engineering import pinned_source as P
from manufacturing.adapters import envelope as E

T, F, Z = "T", "F", "Z"


def _modules():
    P.import_path()
    from deal_rescue.industrial import cad027_review, cad_bom, cad_xcaf  # noqa: E402 (pinned, verified copy)
    return cad_xcaf, cad_bom, cad027_review


def drawing_intake(filename: str, data: bytes) -> dict:
    """2D drawing / BOM files (CSV, JSON, DXF, SVG, text PDF) through Deal-Rescue cad_bom. STL and unsupported -> Z."""
    _, cad_bom, _ = _modules()
    if filename.lower().endswith((".step", ".stp")):
        return {"extraction": Z, "reason": "STEP_GOES_THROUGH_XCAF_INTAKE", "bom": []}
    try:
        out = cad_bom.extract(filename, data)
    except cad_bom.IntakeError as e:
        return {"extraction": Z, "reason": str(e), "bom": [], "file_sha256": hashlib.sha256(data).hexdigest()}
    out["engineering_verdict"] = Z
    return out


def _line_with(text: str, needle: str):
    for i, line in enumerate(text.splitlines(), 1):
        if needle in line:
            return i, line.strip()
    return None, None


def step_intake(step_path, readme_path, expected_step_sha256: str, site: str, inquiry_ref: str,
                tenant: str = "legion-reference", verifier=None) -> dict:
    cad_xcaf, _, R = _modules()
    step_path, readme_path = Path(step_path), Path(readme_path)
    out = {"schema": "legion.manufacturing.cad-intake.v1", "stages": {}, "engineering_verdict": Z}
    # 1 intake: the pinned file, hash first (cad_xcaf checks it before loading OpenCascade)
    try:
        xcaf = cad_xcaf.read_assembly(step_path, expected_step_sha256)
    except cad_xcaf.SourceMismatch as e:
        out["stages"]["intake"] = {"status": F, "reason": str(e)}
        return out
    except Exception as e:  # an exception inside OpenCascade is a failed read, never a result
        out["stages"]["intake"] = {"status": Z, "reason": f"STEP_READ_EXCEPTION {type(e).__name__}: {e}"}
        return out
    if xcaf.get("verdict") != "T_XCAF_STRUCTURE":
        out["stages"]["intake"] = {"status": Z, "reason": xcaf.get("verdict"), "sha256": xcaf.get("sha256")}
        return out
    out["stages"]["intake"] = {"status": T, "file": xcaf["file"], "sha256": xcaf["sha256"], "bytes": xcaf["bytes"],
                               "length_unit": xcaf["length_unit"], "assemblies": xcaf["assemblies"],
                               "leaf_definitions": xcaf["leaf_definitions"], "leaf_instances": xcaf["leaf_instances"],
                               "inferred_fields": xcaf["inferred_fields"]}
    readme_text = readme_path.read_text(encoding="utf-8")
    readme_sha = hashlib.sha256(readme_path.read_bytes()).hexdigest()
    return assemble(out, xcaf, readme_text, readme_sha, site, inquiry_ref, tenant, verifier)


def assemble(out, xcaf, readme_text, readme_sha, site, inquiry_ref, tenant="legion-reference", verifier=None) -> dict:
    """Stages 2-4 and the contract handoff, on an XCAF result (real, or Deal-Rescue's own offline fixture)."""
    _, _, R = _modules()
    # 2 BOM against the factory readme
    bom = R.reconcile(xcaf, R.parse_readme(readme_text), readme_sha)
    out["stages"]["bom"] = {"status": R.bom_status(bom), "mandatory_positions": bom["mandatory_positions"],
                            "mandatory_positions_matched": bom["mandatory_positions_matched"],
                            "mandatory_instances_readme": bom["mandatory_instances_readme"],
                            "mandatory_instances_step": bom["mandatory_instances_step"],
                            "purchased_readme_positions": bom["purchased_readme_positions"],
                            "mismatches": bom["mismatches"], "readme_sha256": readme_sha}
    # 3 requirements: only what a named source states for the part
    tol_line, tol_text = _line_with(readme_text, "Key dimension tolerance")
    reqs = []
    for r in bom["rows"]:
        reqs.append({"part_id": r["part_id"], "group": r["group"], "quantity": r["quantity"],
                     "material": r["material"], "material_source": f"readme.md line {r['readme_line']}",
                     "process": r["manufacturing_process"],
                     "tolerance": tol_text if r["group"] == "cnc" and tol_line else None,
                     "tolerance_source": f"readme.md line {tol_line}" if r["group"] == "cnc" and tol_line else None,
                     "missing_requirements": r["missing_requirements"],
                     "geometry_observed": r["geometry"]})
    out["stages"]["requirements"] = {"status": T if reqs else Z, "parts": reqs,
                                     "missing_for_engineering_T": list(R.MISSING_FOR_ENGINEERING_T),
                                     "materials_from_geometry": 0, "tolerances_from_geometry": 0}
    # 4 verification: Z until ZTL Engineer (WO-D02) and an independent attestation exist
    out["stages"]["verification"] = {"status": Z, "why": "no verifier runtime given (WO-D02: pass "
                                                        "verifier=ztl_adapter.runtime()). Nothing here certifies "
                                                        "compliance."}
    if verifier is not None:                          # WO-D02: the real ZTL route on what stages 1-3 emitted
        from legion.engineering import ztl_adapter as A
        case = A.rebot_case(out, xcaf, readme_text, readme_sha, verifier)
        out["stages"]["verification"] = {"status": case["verdict"]["ENGINEERING_VERDICT"], **case}
        out["engineering_verdict"] = case["verdict"]["ENGINEERING_VERDICT"]
    # handoff to Anthropic's quote chain: one path-C1 geometry estimate per CNC part
    revision = {"step_file": xcaf["file"], "step_sha256": xcaf["sha256"],
                "source_commit": P.load_pin()["reference_cad"]["commit"] if xcaf["sha256"] == P.load_pin()[
                    "reference_cad"]["files"]["step"]["sha256"] else None, "drawing_revision": None,
                "why_no_drawing_revision": "the package is a STEP model and a readme; no drawing (path C1)"}
    out["revision_evidence"] = revision
    scope = E.scope(tenant, ["cad:read"])
    envs = []
    for n, r in enumerate([q for q in reqs if q["group"] == "cnc"], 1):
        rec = geometry_estimate_c1(r, n, site, inquiry_ref, xcaf, readme_sha, tol_line, tol_text)
        envs.append(E.wrap("geometry-estimate", rec, [
            E.binding("stock.material", "rebot-readme", tenant, f"readme.md:{r['material_source']}", r["material"]),
            E.binding("model.model_checks", "deal-rescue-cad_xcaf", tenant, f"{xcaf['file']}#{r['part_id']}",
                      r["geometry_observed"])], scope))
    out["geometry_estimates"] = envs
    return out


def geometry_estimate_c1(r, line_no, site, inquiry_ref, xcaf, readme_sha, tol_line, tol_text) -> dict:
    geo = r["geometry_observed"] or {}
    bb = geo.get("bbox")
    unit = xcaf["length_unit"]
    src_readme = f"readme.md sha256 {readme_sha[:12]}"
    return {
        "contract_version": 1, "site": site, "inquiry_ref": inquiry_ref, "line_no": line_no,
        "part_number": r["part_id"], "part_number_verbatim": r["part_id"],
        "geometry_path": "C1", "drawing_revision_priced_to": None,
        "model": {
            "origin": "customer_step", "document_ref": None, "base_model_ref": None, "cad_backend": "none",
            "generated_at": None,
            "document_integrity": {"result": "not_applicable", "bodies_before": None, "bodies_after": None,
                                   "sketches_before": None, "sketches_after": None, "checked_at": None,
                                   "detail": "STEP read with OpenCascade XCAF by LEGION (Deal-Rescue cad_xcaf, pinned), "
                                             "not a Fusion import: unverified, per path C1"},
            "model_checks": None if not bb else {
                "bounding_box": f"{bb[0]} x {bb[1]} x {bb[2]} {unit} (XCAF, nominal model; no hand calculation)",
                "volume": f"{geo.get('volume')} {unit}3 (XCAF, nominal model; no hand calculation)"}},
        "stock": {"material": r["material"], "form": None, "size": None, "fit_check": None,
                  "source_ref": f"{src_readme}, {r['material_source']}"},
        "datums": [],
        "features": [],
        "setups": [],
        "operations": [],
        "tolerances": ([{"characteristic": "key dimensions", "value": tol_text, "reading_basis": "general_note",
                         "source_ref": f"{src_readme}, line {tol_line}", "key_characteristic": None}]
                       if tol_line else []),
        "unreadables": [
            {"what": "feature list", "where": xcaf["file"],
             "why": "a STEP file carries bodies, not features; recognising features from faces is unverified and was not run"},
            {"what": "datums", "where": xcaf["file"], "why": "no drawing identifies datum features"},
            {"what": "per-feature tolerances and surface finish", "where": "readme.md",
             "why": "only a general key-dimension tolerance is stated; a firm price depends on the per-feature callouts"},
            {"what": "operations and setups", "where": "-",
             "why": "not proposed: no feature list to plan from; the estimator decides at Gate 3"}],
        "questions_for_estimator": [
            "Path C1 without CAD features: supply the drawing, or a hand-entered feature list, before hours are derived.",
            f"Material is taken from the factory readme ({r['material_source']}); confirm the grade and certificate."],
        "approval": {"status": "draft", "by": None, "at": None, "note": None},
    }
