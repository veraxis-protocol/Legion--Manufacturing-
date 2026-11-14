#!/usr/bin/env python3
"""Read-only probe for the synthetic CMMS SQLite database (custom-connector, Tier 4 / Step 10).

Opens the database with SQLite URI mode=ro (no writes possible through this handle),
lists tables/views and their columns, and prints up to N sample rows per object.
It never creates the file: if the path does not exist it reports that and exits 2.
Usage: python -I cmms_readonly_probe.py <path-to-sqlite> [--rows 5]
"""
import json, os, pathlib, sqlite3, sys

def main():
    if len(sys.argv) < 2:
        print("usage: cmms_readonly_probe.py <db> [--rows N]"); return 64
    db = pathlib.Path(sys.argv[1])
    rows = int(sys.argv[sys.argv.index("--rows") + 1]) if "--rows" in sys.argv else 5
    result = {"db_path": str(db), "exists": db.is_file()}
    if not db.is_file():
        result["status"] = "Untested: not registered"
        result["reason"] = "database file not found at the given path; nothing was opened or created"
        print(json.dumps(result, indent=2)); return 2
    con = sqlite3.connect(db.resolve().as_uri() + "?mode=ro", uri=True)
    con.execute("PRAGMA query_only = ON")
    objs = con.execute("SELECT type, name FROM sqlite_master WHERE type IN ('table','view') "
                       "AND name NOT LIKE 'sqlite_%' ORDER BY type, name").fetchall()
    result["objects"] = []
    for typ, name in objs:
        cols = [r[1] for r in con.execute(f'PRAGMA table_info("{name}")')]
        count = con.execute(f'SELECT COUNT(*) FROM "{name}"').fetchone()[0]
        sample = [dict(zip(cols, r)) for r in con.execute(f'SELECT * FROM "{name}" LIMIT ?', (rows,))]
        result["objects"].append({"type": typ, "name": name, "columns": cols,
                                  "row_count": count, "sample": sample})
    con.close()
    result["status"] = "read back; awaiting user confirmation of mapping"
    print(json.dumps(result, indent=2, default=str)); return 0

if __name__ == "__main__":
    sys.exit(main())
