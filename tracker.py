import sqlite3
import os
import secrets

DB_PATH = os.environ.get("DB_PATH", os.path.join(os.path.dirname(__file__), "tracker.db"))


def init_db():
    con = sqlite3.connect(DB_PATH)
    con.execute("""
        CREATE TABLE IF NOT EXISTS businesses (
            place_id TEXT PRIMARY KEY,
            name TEXT,
            city TEXT,
            category TEXT,
            email TEXT,
            preview_url TEXT,
            status TEXT,
            token TEXT,
            html TEXT,
            custom_html TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    # Migrate existing DBs that don't have new columns
    for col, definition in [("token","TEXT"), ("html","TEXT"), ("custom_html","TEXT")]:
        try:
            con.execute(f"ALTER TABLE businesses ADD COLUMN {col} {definition}")
        except Exception:
            pass
    con.commit()
    con.close()


def already_processed(place_id: str) -> bool:
    con = sqlite3.connect(DB_PATH)
    row = con.execute("SELECT 1 FROM businesses WHERE place_id = ?", (place_id,)).fetchone()
    con.close()
    return row is not None


def mark_processed(place_id: str, name: str, city: str, category: str,
                   email: str, preview_url: str, status: str,
                   html: str = "", token: str = ""):
    if not token:
        token = secrets.token_urlsafe(16)
    con = sqlite3.connect(DB_PATH)
    con.execute(
        """INSERT OR REPLACE INTO businesses
           (place_id, name, city, category, email, preview_url, status, html, token)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (place_id, name, city, category, email, preview_url, status, html, token),
    )
    con.commit()
    con.close()
    return token


def get_by_token(token: str) -> dict | None:
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    row = con.execute("SELECT * FROM businesses WHERE token=?", (token,)).fetchone()
    con.close()
    return dict(row) if row else None


def save_custom_html(token: str, html: str):
    con = sqlite3.connect(DB_PATH)
    con.execute("UPDATE businesses SET custom_html=? WHERE token=?", (html, token))
    con.commit()
    con.close()


def list_all():
    con = sqlite3.connect(DB_PATH)
    rows = con.execute(
        "SELECT name, city, email, preview_url, status, created_at FROM businesses ORDER BY created_at DESC"
    ).fetchall()
    con.close()
    return rows
