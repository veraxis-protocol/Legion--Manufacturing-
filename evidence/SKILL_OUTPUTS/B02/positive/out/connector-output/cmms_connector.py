"""Read-only CMMS connector (Tier 4, read-only view) - custom-connector skill output.

Opens the CMMS SQLite file read-only (URI mode=ro), creates the proposed views from
cmms_readonly_views.sql as TEMP views (connection-local, never written to the file),
switches the connection to query_only, and emits the two mapped tabs as CSV plus a
test report. The source file is hashed before and after to prove it was not changed.

Usage:  python -I cmms_connector.py <path-to-cmms.sqlite> <out-dir>
No credentials: access is governed by file-system read permission only.
"""
import csv
import hashlib
import json
import os
import re
import sqlite3
import sys
from datetime import datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
VIEWS_SQL = os.path.join(HERE, "cmms_readonly_views.sql")
TABS = {"assets": "lmfg_assets", "maintenance_work_orders": "lmfg_maintenance_work_orders"}


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        h.update(f.read())
    return h.hexdigest()


def main(db_path, out_dir):
    os.makedirs(out_dir, exist_ok=True)
    before = sha256(db_path)
    mtime_before = os.path.getmtime(db_path)
    uri = "file:" + db_path.replace("\\", "/") + "?mode=ro"
    con = sqlite3.connect(uri, uri=True)
    report = {"run_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
              "target": db_path, "access": "sqlite URI mode=ro + PRAGMA query_only=ON",
              "checks": [], "tabs": {}}

    def check(name, ok, detail):
        report["checks"].append({"check": name, "pass": bool(ok), "detail": detail})

    # 1. Create the proposed views as TEMP views (temp schema only).
    sql = open(VIEWS_SQL, encoding="utf-8").read()
    sql = re.sub(r"CREATE VIEW", "CREATE TEMP VIEW", sql)
    con.executescript(sql)
    con.execute("PRAGMA query_only=ON")

    # 2. Prove writes are refused on this connection.
    try:
        con.execute("INSERT INTO work_orders(wo) VALUES('__probe__')")
        check("write refused", False, "an INSERT was accepted - connector is NOT read-only")
        con.rollback()
    except sqlite3.Error as e:
        check("write refused", True, f"INSERT refused: {e}")

    # 3. Pull each mapped tab.
    for tab, view in TABS.items():
        cur = con.execute(f"SELECT * FROM {view}")
        cols = [d[0] for d in cur.description]
        rows = cur.fetchall()
        with open(os.path.join(out_dir, f"{tab}.csv"), "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(cols)
            w.writerows(rows)
        report["tabs"][tab] = {"columns": cols, "rows": [dict(zip(cols, r)) for r in rows]}

    # 4. Completeness: mapped rows vs the source's own counts.
    src_wo = con.execute("SELECT count(*) FROM work_orders").fetchone()[0]
    src_as = con.execute("SELECT count(*) FROM assets").fetchone()[0]
    n_wo = len(report["tabs"]["maintenance_work_orders"]["rows"])
    n_as = len(report["tabs"]["assets"]["rows"])
    check("maintenance_work_orders row count = source work_orders count", n_wo == src_wo, f"{n_wo} vs {src_wo}")
    check("assets row count = source assets count", n_as == src_as, f"{n_as} vs {src_as}")
    src_open = con.execute("SELECT count(*) FROM v_open_work_orders").fetchone()[0]
    n_open = sum(1 for r in report["tabs"]["maintenance_work_orders"]["rows"] if r["closed_date"] is None)
    check("open tickets = source's own v_open_work_orders", n_open == src_open, f"{n_open} vs {src_open}")

    # 5. Record-by-record comparison against the raw table.
    raw = {r[0]: r for r in con.execute("SELECT wo, asset_id, opened, closed, note FROM work_orders")}
    mism = []
    for r in report["tabs"]["maintenance_work_orders"]["rows"]:
        wo, asset, opened, closed, note = raw[r["maintenance_wo"]]
        exp_note = note if closed is not None else None
        if (r["asset_id_verbatim"], r["opened_date"], r["closed_date"], r["close_out_notes"]) != (asset, opened, closed, exp_note):
            mism.append(wo)
    check("each maintenance work order matches its raw record", not mism, f"{n_wo} compared, mismatches: {mism or 'none'}")
    unmatched = [r["maintenance_wo"] for r in report["tabs"]["maintenance_work_orders"]["rows"] if r["join_status"] != "matched"]
    check("every maintenance work order's asset exists on assets", not unmatched, f"unmatched: {unmatched or 'none'}")
    flagged = [r["maintenance_wo"] for r in report["tabs"]["maintenance_work_orders"]["rows"] if r["integrity_flags"]]
    check("no end_before_start", not flagged, f"flagged: {flagged or 'none'}")

    # 6. Fields read but left out (no home in contract v6).
    report["unmapped_in_source"] = {
        "work_orders.wo_type": sorted({r[0] for r in con.execute("SELECT wo_type FROM work_orders")}),
        "work_orders.downtime_min": [list(r) for r in con.execute("SELECT wo, downtime_min FROM work_orders")],
        "assets.description": [list(r) for r in con.execute("SELECT asset_id, description FROM assets")],
        "work_orders.note on open tickets": [list(r) for r in con.execute("SELECT wo, note FROM work_orders WHERE closed IS NULL")],
    }
    con.close()

    after = sha256(db_path)
    check("source file unchanged (sha256 + mtime)",
          before == after and os.path.getmtime(db_path) == mtime_before, f"sha256 {before[:16]}... before and after")
    report["source_sha256"] = before
    report["all_pass"] = all(c["pass"] for c in report["checks"])
    with open(os.path.join(out_dir, "test_results.json"), "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)
    for c in report["checks"]:
        print(("PASS " if c["pass"] else "FAIL ") + c["check"] + " - " + c["detail"])
    print("ALL PASS" if report["all_pass"] else "FAILURES PRESENT")
    return 0 if report["all_pass"] else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1], sys.argv[2]))
