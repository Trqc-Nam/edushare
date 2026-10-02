# -*- coding: utf-8 -*-
"""
database.py - Thread-safe SQLite manager for EduShare-KNTT v2.0.
Handles schema creation and idempotent seed data insertion.
"""
import sqlite3

DB_PATH = "edushare.db"

_DDL = """
CREATE TABLE IF NOT EXISTS students (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    name        TEXT    NOT NULL,
    class_name  TEXT    NOT NULL,
    has_book    INTEGER NOT NULL,
    is_myopic   INTEGER NOT NULL,
    can_lend    INTEGER NOT NULL
);
CREATE TABLE IF NOT EXISTS timetable (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    day         INTEGER NOT NULL,
    period      INTEGER NOT NULL,
    class_name  TEXT    NOT NULL,
    subject     TEXT    NOT NULL
);
CREATE TABLE IF NOT EXISTS inventory (
    subject     TEXT    PRIMARY KEY,
    cart_qty    INTEGER NOT NULL
);
CREATE TABLE IF NOT EXISTS allocations_log (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    day         INTEGER NOT NULL,
    period      INTEGER NOT NULL,
    class_name  TEXT    NOT NULL,
    subject     TEXT    NOT NULL,
    status      TEXT    NOT NULL,
    alert_msg   TEXT    NOT NULL
);
"""

SEED_STUDENTS = [
    # Class 6A - 8 students, ratio 62.5%
    ("Nguy\u1ec5n V\u0103n An",    "6A", 1, 0, 1),
    ("Tr\u1ea7n Th\u1ecb B\u00ecnh", "6A", 0, 1, 0),
    ("L\u00ea Ho\u00e0ng C\u01b0\u1eddng", "6A", 1, 1, 1),
    ("Ph\u1ea1m Th\u1ecb Duy\u00ean", "6A", 0, 0, 0),
    ("Ho\u00e0ng V\u0103n Em",     "6A", 1, 0, 0),
    ("\u0110\u1ed7 Mai Ph\u01b0\u01a1ng", "6A", 1, 0, 0),
    ("V\u0169 \u0110\u1ee9c Th\u1eafng", "6A", 0, 1, 0),
    ("B\u00f9i Ng\u1ecdc \u00c1nh", "6A", 1, 0, 1),
    # Class 6B - 7 students, ratio 28.5%
    ("\u0110inh Gia B\u1ea3o",     "6B", 1, 0, 0),
    ("Nguy\u1ec5n C\u1ea9m Ly",    "6B", 1, 1, 1),
    ("Phan Tr\u1ecdng H\u01b0ng",  "6B", 0, 0, 0),
    ("Tr\u01b0\u01a1ng Qu\u1ef3nh Nga", "6B", 0, 1, 0),
    ("V\u00f5 Minh Qu\u00e2n",     "6B", 0, 0, 0),
    ("L\u00e2m Kh\u00e1nh V\u00e2n", "6B", 0, 0, 0),
    ("\u0110\u00e0o Qu\u1ed1c Huy", "6B", 0, 0, 0),
]

SEED_INVENTORY = [
    ("To\u00e1n",      1),
    ("Ng\u1eef v\u0103n", 2),
    ("KHTN",            1),
    ("Ti\u1ebfng Anh",  1),
]

SEED_TIMETABLE = [
    (2, 1, "6A", "To\u00e1n"),
    (2, 1, "6B", "Ng\u1eef v\u0103n"),
    (2, 2, "6A", "To\u00e1n"),
    (2, 2, "6B", "To\u00e1n"),       # Intentional collision - cart_qty=1
    (3, 2, "6A", "Ng\u1eef v\u0103n"),
    (3, 2, "6B", "Ng\u1eef v\u0103n"), # Concurrent - no collision (cart_qty=2)
]


def get_connection() -> sqlite3.Connection:
    """Return a new SQLite connection (check_same_thread=False for Streamlit)."""
    return sqlite3.connect(DB_PATH, check_same_thread=False)


def init_db() -> None:
    """Create tables and insert seed data idempotently."""
    with get_connection() as conn:
        conn.executescript(_DDL)
        conn.commit()
        cur = conn.execute("SELECT count(*) FROM students")
        if cur.fetchone()[0] == 0:
            conn.executemany(
                "INSERT INTO students (name, class_name, has_book, is_myopic, can_lend) "
                "VALUES (?, ?, ?, ?, ?)",
                SEED_STUDENTS,
            )
            conn.executemany(
                "INSERT OR IGNORE INTO inventory (subject, cart_qty) VALUES (?, ?)",
                SEED_INVENTORY,
            )
            conn.executemany(
                "INSERT INTO timetable (day, period, class_name, subject) VALUES (?, ?, ?, ?)",
                SEED_TIMETABLE,
            )
            conn.commit()