"""
HDG History Module — SQLite-backed audit trail for chemical additions.

Database is stored at .tmp/hdg_history.db (created automatically on first use).

Column naming note: SQLite column names are case-insensitive, so abbreviations
like VB/Vb or L/l cannot coexist. Descriptive lowercase names are used instead.
"""

import sqlite3
import os
from datetime import datetime

_DB_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '.tmp'))
_DB_PATH = os.path.join(_DB_DIR, 'hdg_history.db')


def _get_connection():
    os.makedirs(_DB_DIR, exist_ok=True)
    return sqlite3.connect(_DB_PATH)


def init_db():
    """Create tables if they don't exist. Safe to call multiple times."""
    conn = _get_connection()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS additions (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp       TEXT    NOT NULL,
            -- Tank dimensions
            length          REAL    NOT NULL,
            width           REAL    NOT NULL,
            height          REAL    NOT NULL,
            niveau_boues    REAL    NOT NULL,
            n               REAL    NOT NULL,
            ve_pct          REAL    NOT NULL,
            -- Concentrations
            conc_i          REAL    NOT NULL,
            conc_souhaitee  REAL    NOT NULL,
            conc_min        REAL    NOT NULL,
            conc_max        REAL    NOT NULL,
            -- Calculated volumes (descriptive names to avoid SQLite case conflicts)
            vol_bath        REAL    NOT NULL,   -- VB
            vol_sludge      REAL    NOT NULL,   -- Vb
            vol_headspace   REAL    NOT NULL,   -- Vn
            vol_empty       REAL    NOT NULL,   -- Ve_L
            vol_final       REAL    NOT NULL,   -- Vsf
            vol_initial     REAL    NOT NULL,   -- Vsi
            -- Masses
            mass_total      REAL    NOT NULL,   -- m_Total
            mass_adj        REAL    NOT NULL,   -- mf
            -- Status
            conc_status     TEXT    NOT NULL,
            operator_note   TEXT    DEFAULT ''
        )
    """)
    conn.commit()
    conn.close()


def save_entry(inputs, outputs, operator_note=''):
    """Persist a calculation result to the database."""
    init_db()
    conn = _get_connection()
    conn.execute("""
        INSERT INTO additions (
            timestamp, length, width, height, niveau_boues, n, ve_pct,
            conc_i, conc_souhaitee, conc_min, conc_max,
            vol_bath, vol_sludge, vol_headspace, vol_empty,
            vol_final, vol_initial, mass_total, mass_adj,
            conc_status, operator_note
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        inputs.L, inputs.l, inputs.h,
        inputs.niveau_boues, inputs.n, inputs.Ve,
        inputs.conc_i, inputs.conc_souhaitee,
        inputs.conc_min, inputs.conc_max,
        outputs.VB, outputs.Vb, outputs.Vn, outputs.Ve_L,
        outputs.Vsf, outputs.Vsi, outputs.m_Total, outputs.mf,
        outputs.conc_status, operator_note,
    ))
    conn.commit()
    conn.close()


def get_last_entry():
    """Return the most recent entry as a dict, or None if no entries exist."""
    init_db()
    conn = _get_connection()
    conn.row_factory = sqlite3.Row
    row = conn.execute(
        "SELECT * FROM additions ORDER BY id DESC LIMIT 1"
    ).fetchone()
    conn.close()
    return dict(row) if row else None


def get_all_entries():
    """Return all entries as a list of dicts, newest first."""
    init_db()
    conn = _get_connection()
    conn.row_factory = sqlite3.Row
    rows = conn.execute(
        "SELECT * FROM additions ORDER BY id DESC"
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_entries_for_chart():
    """Return all entries oldest-first for trend charts."""
    init_db()
    conn = _get_connection()
    conn.row_factory = sqlite3.Row
    rows = conn.execute(
        "SELECT * FROM additions ORDER BY id ASC"
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]
