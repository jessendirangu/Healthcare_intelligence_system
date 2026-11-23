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