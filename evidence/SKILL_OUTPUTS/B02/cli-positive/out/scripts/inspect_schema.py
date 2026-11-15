"""Read-only schema inspection of the CMMS SQLite file. Opens with mode=ro + query_only."""
import sqlite3, sys, pathlib

p = pathlib.Path(sys.argv[1]).resolve()
con = sqlite3.connect(f"file:{p.as_posix()}?mode=ro", uri=True)
con.execute("PRAGMA query_only=ON")
for t, n, sql in con.execute("select type,name,sql from sqlite_master order by type,name").fetchall():
    print(f"--- {t} {n}\n{sql}")
    if t in ("table", "view"):
        print("rows:", con.execute(f'select count(*) from "{n}"').fetchone()[0])
print("--- meta")
for r in con.execute("select * from meta"):
    print(r)
for t in ("assets", "work_orders", "v_open_work_orders"):
    print(f"--- sample {t}")
    cur = con.execute(f'select * from "{t}" limit 4')
    print([d[0] for d in cur.description])
    for r in cur:
        print(r)
