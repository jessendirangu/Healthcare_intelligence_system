"""Patient records storage, shared by the public app and the admin app.

Each record has an "Owner" (the email of the account that created it), so
users only ever load their own records. Only the admin app loads everyone's.

Storage:
- With SUPABASE_URL and SUPABASE_KEY in secrets, records are kept in the
  online Supabase database (shared by both websites, kept permanently).
- Otherwise they are kept in the local file patients.db (laptop testing).
"""

import sqlite3

import pandas as pd

from auth import supabase_client, use_supabase

DB_PATH = "patients.db"
NUMERIC_COLS = [
    "Age", "Weight (kg)", "Height (cm)", "BMI",
    "Temperature (°C)", "Pulse (bpm)", "Respiratory rate (/min)",
    "Systolic BP (mmHg)", "Diastolic BP (mmHg)", "SpO2 (%)",
]
PAGE_SIZE = 1000  # Supabase returns at most 1000 rows per request


# ---------------------------------------------------------------
# Supabase (online)
# Table "patients": id, owner, patient_id, record (JSON), created_at
# ---------------------------------------------------------------

def _supabase_load(owner):
    rows, start = [], 0
    while True:
        query = supabase_client().table("patients").select("owner, record")
        if owner is not None:
            query = query.eq("owner", owner)
        page = query.order("id").range(start, start + PAGE_SIZE - 1).execute().data
        rows.extend({**r["record"], "Owner": r["owner"]} for r in page)
        if len(page) < PAGE_SIZE:
            return rows
        start += PAGE_SIZE


def _supabase_save(record):
    data = {k: v for k, v in record.items() if k != "Owner"}
    supabase_client().table("patients").insert({
        "owner": record["Owner"],
        "patient_id": record["Patient ID"],
        "record": data,
    }).execute()


def _supabase_last_id():
    rows = (supabase_client().table("patients").select("patient_id")
            .order("id", desc=True).limit(1).execute().data)
    return rows[0]["patient_id"] if rows else None


# ---------------------------------------------------------------
# SQLite (local file)
# ---------------------------------------------------------------

def _local_load(owner):
    with sqlite3.connect(DB_PATH) as conn:
        try:
            if owner is None:
                df = pd.read_sql("SELECT * FROM patients", conn)
            else:
                df = pd.read_sql('SELECT * FROM patients WHERE "Owner" = ?', conn, params=(owner,))
        except Exception:
            # The table (or the Owner column) doesn't exist until the first save
            return []
    return df.to_dict("records")


def _local_save(record):
    with sqlite3.connect(DB_PATH) as conn:
        # Older databases may be missing newer columns (like Owner): add them
        existing = {row[1] for row in conn.execute("PRAGMA table_info(patients)")}
        if existing:
            for column in record:
                if column not in existing:
                    conn.execute(f'ALTER TABLE patients ADD COLUMN "{column}"')
        pd.DataFrame([record]).to_sql("patients", conn, if_exists="append", index=False)


# ---------------------------------------------------------------
# Used by the apps
# ---------------------------------------------------------------

def load_patients(owner=None):
    """Patients created by one user, or every patient if owner is None (admin only)."""
    rows = _supabase_load(owner) if use_supabase() else _local_load(owner)
    if not rows:
        return []
    df = pd.DataFrame(rows)
    for col in NUMERIC_COLS:
        if col in df:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    # Turn missing values into None so the rest of the code treats them as blank
    df = df.astype(object).where(df.notna(), None)
    return df.to_dict("records")


def save_patient(record):
    if use_supabase():
        _supabase_save(record)
    else:
        _local_save(record)


def delete_my_patients(owner):
    if use_supabase():
        supabase_client().table("patients").delete().eq("owner", owner).execute()
        return
    with sqlite3.connect(DB_PATH) as conn:
        try:
            conn.execute('DELETE FROM patients WHERE "Owner" = ?', (owner,))
        except sqlite3.OperationalError:
            pass


def next_patient_id():
    # IDs are unique across ALL users, not just the current one
    if use_supabase():
        last = _supabase_last_id()
    else:
        everyone = _local_load(None)
        last = max((p["Patient ID"] for p in everyone), default=None,
                   key=lambda pid: int(pid.split("-")[1]))
    number = int(last.split("-")[1]) + 1 if last else 1
    return f"HIS-{number:05d}"


# ---------------------------------------------------------------
# Personal health readings (My health tracker)
# Table "readings": one row per measurement, always tied to its owner.
# ---------------------------------------------------------------

READING_FIELDS = [
    "taken_at", "systolic", "diastolic", "pulse",
    "weight_kg", "glucose_mmol", "glucose_type", "note",
]


def _local_readings(conn):
    conn.execute("""
        CREATE TABLE IF NOT EXISTS readings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            owner TEXT NOT NULL,
            taken_at TEXT NOT NULL,
            systolic INTEGER, diastolic INTEGER, pulse INTEGER,
            weight_kg REAL, glucose_mmol REAL, glucose_type TEXT, note TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )""")
    return conn


def load_readings(owner=None):
    """One user's readings (oldest first), or everyone's if owner is None (admin only)."""
    columns = "id, owner, " + ", ".join(READING_FIELDS)
    if use_supabase():
        rows, start = [], 0
        while True:
            query = supabase_client().table("readings").select(columns)
            if owner is not None:
                query = query.eq("owner", owner)
            page = query.order("taken_at").range(start, start + PAGE_SIZE - 1).execute().data
            rows.extend(page)
            if len(page) < PAGE_SIZE:
                return rows
            start += PAGE_SIZE
    with sqlite3.connect(DB_PATH) as conn:
        _local_readings(conn).row_factory = sqlite3.Row
        if owner is None:
            found = conn.execute(f"SELECT {columns} FROM readings ORDER BY taken_at")
        else:
            found = conn.execute(
                f"SELECT {columns} FROM readings WHERE owner = ? ORDER BY taken_at", (owner,)
            )
        return [dict(r) for r in found]


def save_reading(reading):
    """reading: dict with "owner" plus the READING_FIELDS."""
    row = {k: reading.get(k) for k in ["owner"] + READING_FIELDS}
    if use_supabase():
        supabase_client().table("readings").insert(row).execute()
        return
    with sqlite3.connect(DB_PATH) as conn:
        _local_readings(conn).execute(
            f"INSERT INTO readings ({', '.join(row)}) VALUES ({', '.join('?' * len(row))})",
            list(row.values()),
        )


def delete_reading(owner, reading_id):
    """Delete one reading. The owner check means nobody can delete someone else's."""
    if use_supabase():
        (supabase_client().table("readings").delete()
         .eq("id", reading_id).eq("owner", owner).execute())
        return
    with sqlite3.connect(DB_PATH) as conn:
        _local_readings(conn).execute(
            "DELETE FROM readings WHERE id = ? AND owner = ?", (reading_id, owner)
        )


def load_readings_many(owners):
    """Readings for several owners at once (e.g. all members a CHP looks after)."""
    owners = list(owners)
    if not owners:
        return []
    columns = "id, owner, " + ", ".join(READING_FIELDS)
    if use_supabase():
        rows = []
        for i in range(0, len(owners), 100):  # keep each request a sensible size
            chunk, start = owners[i:i + 100], 0
            while True:
                page = (supabase_client().table("readings").select(columns).in_("owner", chunk)
                        .order("taken_at").range(start, start + PAGE_SIZE - 1).execute().data)
                rows.extend(page)
                if len(page) < PAGE_SIZE:
                    break
                start += PAGE_SIZE
        return rows
    with sqlite3.connect(DB_PATH) as conn:
        _local_readings(conn).row_factory = sqlite3.Row
        marks = ", ".join("?" * len(owners))
        return [dict(r) for r in conn.execute(
            f"SELECT {columns} FROM readings WHERE owner IN ({marks}) ORDER BY taken_at", owners)]