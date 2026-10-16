"""SQLite storage + auto requisition number + search/status helpers."""
import sqlite3
from datetime import datetime

DB = "requisitions.db"


def _conn():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with _conn() as c:
        c.execute("""CREATE TABLE IF NOT EXISTS requisitions(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            req_no TEXT UNIQUE, created_at TEXT, department TEXT, name TEXT, roll_no TEXT,
            semester TEXT, division TEXT, contact TEXT, app_type TEXT, purpose TEXT,
            docs_attached TEXT, doc_names TEXT, form_date TEXT, status TEXT DEFAULT 'Submitted')""")


def save(d: dict) -> str:
    """Insert a record and return the auto-generated requisition number (REQ-YYYY-0001)."""
    with _conn() as c:
        cur = c.execute(
            """INSERT INTO requisitions(created_at, department, name, roll_no, semester, division,
               contact, app_type, purpose, docs_attached, doc_names, form_date)
               VALUES(?,?,?,?,?,?,?,?,?,?,?,?)""",
            (datetime.now().isoformat(timespec="seconds"), d["department"], d["name"], d["roll_no"],
             d["semester"], d["division"], d["contact"], d["app_type"], d["purpose"],
             "Yes" if d["docs_attached"] else "No", d["doc_names"], d["date"]))
        req_no = f"REQ-{datetime.now().year}-{cur.lastrowid:04d}"
        c.execute("UPDATE requisitions SET req_no=? WHERE id=?", (req_no, cur.lastrowid))
    return req_no


def search(q: str = "", status: str = "All"):
    sql, args = "SELECT * FROM requisitions WHERE 1=1", []
    if q:
        sql += " AND (name LIKE ? OR roll_no LIKE ? OR req_no LIKE ? OR app_type LIKE ?)"
        args += [f"%{q}%"] * 4
    if status != "All":
        sql += " AND status=?"; args.append(status)
    with _conn() as c:
        return [dict(r) for r in c.execute(sql + " ORDER BY id DESC", args)]


def get_by_req(req_no: str):
    with _conn() as c:
        r = c.execute("SELECT * FROM requisitions WHERE req_no=?", (req_no.strip(),)).fetchone()
    return dict(r) if r else None


def update_status(req_no: str, status: str):
    with _conn() as c:
        c.execute("UPDATE requisitions SET status=? WHERE req_no=?", (status, req_no))
