"""
CMMS SQLite connector (Tier 4: read-only database access) - SYNTHETIC test target.

Reads assets and maintenance work orders from the CMMS SQLite file and maps them
onto the consolidated dataset schema (contract v6): tabs `assets` and
`maintenance_work_orders`.

Read-only is enforced three ways:
  1. the file is opened with the SQLite URI flag mode=ro (the OS handle is read-only),
  2. PRAGMA query_only=ON on the connection,
  3. SHA-256 of the file is taken before and after the run and must be identical.

No credentials are used: the target is a local file with no authentication.

Usage:
  python -I cmms_sqlite_connector.py <path-to-sqlite> <output-folder>
"""
import csv
import datetime as dt
import hashlib
import json
import pathlib
import sqlite3
import sys

SOURCE_SYSTEM = "cmms"
TODAY = dt.date(2026, 11, 15)  # session date; used for the future_timestamp check

# Schema fingerprint the mapping was built against. Any drift stops the run
# loudly instead of returning wrong or empty data (the Tier 4 failure mode).
EXPECTED_SCHEMA = {
    "assets": ["asset_id", "description", "site"],
    "work_orders": ["wo", "asset_id", "opened", "closed", "wo_type", "downtime_min", "note"],
}

COMMON = ["site", "source_system", "source_ref", "as_of", "join_status",
          "mismatch_class", "contradicted_by", "integrity_flags"]
ASSET_COLS = COMMON + ["asset_id", "asset_id_verbatim", "location"]
MWO_COLS = COMMON + ["maintenance_wo", "asset_id", "asset_id_verbatim",
                     "opened_date", "closed_date", "close_out_notes"]


def sha256(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def norm_key(v):
    """Ladder rungs 1-2 only (trim, upper-case). Nothing more aggressive is applied."""
    return None if v is None else v.strip().upper()


def parse_date(v):
    try:
        return dt.date.fromisoformat(v) if v else None
    except ValueError:
        return "unparseable"


def main(db_path, out_dir):
    db = pathlib.Path(db_path).resolve()
    out = pathlib.Path(out_dir).resolve()
    out.mkdir(parents=True, exist_ok=True)
    hash_before = sha256(db)

    con = sqlite3.connect(f"file:{db.as_posix()}?mode=ro", uri=True)
    con.execute("PRAGMA query_only=ON")
    query_only = con.execute("PRAGMA query_only").fetchone()[0]

    # --- schema drift check -------------------------------------------------
    drift = {}
    for table, cols in EXPECTED_SCHEMA.items():
        actual = [r[1] for r in con.execute(f'PRAGMA table_info("{table}")')]
        if actual != cols:
            drift[table] = {"expected": cols, "actual": actual}
    if drift:
        raise SystemExit(f"SCHEMA DRIFT - mapping not applied: {json.dumps(drift)}")

    # --- pull (explicit column lists, never SELECT *) ------------------------
    assets_raw = con.execute(
        "SELECT rowid, asset_id, description, site FROM assets ORDER BY asset_id").fetchall()
    wos_raw = con.execute(
        "SELECT rowid, wo, asset_id, opened, closed, wo_type, downtime_min, note "
        "FROM work_orders ORDER BY opened, wo").fetchall()

    # independent counts from the source itself (same file - see test notes)
    n_assets_src = con.execute("SELECT count(*) FROM assets").fetchone()[0]
    n_wo_src = con.execute("SELECT count(*) FROM work_orders").fetchone()[0]
    n_open_view = con.execute("SELECT count(*) FROM v_open_work_orders").fetchone()[0]
    n_open_tbl = con.execute("SELECT count(*) FROM work_orders WHERE closed IS NULL").fetchone()[0]
    meta = [r[0] for r in con.execute("SELECT note FROM meta")]
    con.close()

    # --- map: assets ------------------------------------------------------------
    asset_site = {}
    assets = []
    for rowid, aid, desc, site in assets_raw:
        key = norm_key(aid)
        asset_site[key] = site
        assets.append({
            "site": site,
            "source_system": SOURCE_SYSTEM,
            "source_ref": f"{db.name}:assets/{aid}",
            "as_of": None,  # source holds no record timestamp for assets
            "join_status": "matched" if key == aid else "normalized",
            "mismatch_class": None,
            "contradicted_by": None,
            "integrity_flags": None,
            "asset_id": key,
            "asset_id_verbatim": aid,
            "location": None,  # source has no location field
        })

    # --- map: maintenance_work_orders ------------------------------------------
    mwos, unmapped_values = [], []
    for rowid, wo, aid, opened, closed, wo_type, downtime_min, note in wos_raw:
        key = norm_key(aid)
        flags = []
        od, cd = parse_date(opened), parse_date(closed)
        if isinstance(od, dt.date) and isinstance(cd, dt.date) and cd < od:
            flags.append("end_before_start")
        for d in (od, cd):
            if isinstance(d, dt.date) and d > TODAY:
                flags.append("future_timestamp")
        matched = key in asset_site
        mwos.append({
            "site": asset_site.get(key),  # work_orders has no site; inherited via asset
            "source_system": SOURCE_SYSTEM,
            "source_ref": f"{db.name}:work_orders/{wo}",
            "as_of": closed or opened,  # date only, zone not stated by the source
            "join_status": ("matched" if key == aid else "normalized") if matched else "unmatched",
            "mismatch_class": None if matched else 1,
            "contradicted_by": None,
            "integrity_flags": ";".join(sorted(set(flags))) or None,
            "maintenance_wo": wo,
            "asset_id": key,
            "asset_id_verbatim": aid,
            "opened_date": opened,
            "closed_date": closed,
            "close_out_notes": note,
        })
        unmapped_values.append({"maintenance_wo": wo, "wo_type": wo_type,
                                "downtime_min": downtime_min})

    # --- write ------------------------------------------------------------------
    def write_csv(name, cols, rows):
        with open(out / name, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=cols)
            w.writeheader()
            w.writerows(rows)

    write_csv("assets.csv", ASSET_COLS, assets)
    write_csv("maintenance_work_orders.csv", MWO_COLS, mwos)

    hash_after = sha256(db)
    results = {
        "run_at": dt.datetime.now().astimezone().isoformat(timespec="seconds"),
        "source_file": db.name,
        "source_meta": meta,
        "read_only": {
            "uri_mode": "ro",
            "pragma_query_only": query_only,
            "sha256_before": hash_before,
            "sha256_after": hash_after,
            "file_unchanged": hash_before == hash_after,
        },
        "schema_drift": None,
        "completeness": {
            "assets": {"source_count": n_assets_src, "mapped": len(assets)},
            "work_orders": {"source_count": n_wo_src, "mapped": len(mwos)},
            "open_wos": {"v_open_work_orders": n_open_view,
                         "work_orders_closed_is_null": n_open_tbl,
                         "mapped_open": sum(1 for m in mwos if m["closed_date"] is None)},
        },
        "join": {"unmatched_work_orders": [m["maintenance_wo"] for m in mwos
                                          if m["join_status"] == "unmatched"]},
        "integrity_flags": {m["maintenance_wo"]: m["integrity_flags"]
                            for m in mwos if m["integrity_flags"]},
        "unmapped_fields_held_out": unmapped_values,
    }
    (out / "test-results.json").write_text(json.dumps(results, indent=2), encoding="utf-8")

    print(json.dumps(results, indent=2))
    print("\n=== assets (mapped) ===")
    for a in assets:
        print(a)
    print("\n=== maintenance_work_orders (mapped) ===")
    for m in mwos:
        print(m)
    if hash_before != hash_after:
        raise SystemExit("SOURCE FILE CHANGED DURING RUN - investigate")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
