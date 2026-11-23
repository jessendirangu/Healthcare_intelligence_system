"""Patient records storage, shared by the public app and the admin app.

Each record has an "Owner" (the email of the account that created it), so
users only ever load their own records. Only the admin app loads everyone's.
"""

import sqlite3

import pandas as pd

DB_PATH = "patients.db"
NUMERIC_COLS = [
    "Age", "Weight (kg)", "Height (cm)", "BMI",
    "Temperature (°C)", "Pulse (bpm)", "Respiratory rate (/min)",
    "Systolic BP (mmHg)", "Diastolic BP (mmHg)", "SpO2 (%)",
]


def load_patients(owner=None):
    """Patients created by one user, or every patient if owner is None (admin only)."""
    with sqlite3.connect(DB_PATH) as conn:
        try:
            if owner is None:
                df = pd.read_sql("SELECT * FROM patients", conn)
            else:
                df = pd.read_sql('SELECT * FROM patients WHERE "Owner" = ?', conn, params=(owner,))
        except Exception:
            # The table (or the Owner column) doesn't exist until the first save
            return []
    for col in NUMERIC_COLS:
        if col in df:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    # Turn SQL NULLs into None so the rest of the code treats them as blank
    df = df.astype(object).where(df.notna(), None)
    return df.to_dict("records")


def save_patient(record):
    with sqlite3.connect(DB_PATH) as conn:
        # Older databases may be missing newer columns (like Owner): add them
        existing = {row[1] for row in conn.execute("PRAGMA table_info(patients)")}
        if existing:
            for column in record:
                if column not in existing:
                    conn.execute(f'ALTER TABLE patients ADD COLUMN "{column}"')
        pd.DataFrame([record]).to_sql("patients", conn, if_exists="append", index=False)


def delete_my_patients(owner):
    with sqlite3.connect(DB_PATH) as conn:
        try:
            conn.execute('DELETE FROM patients WHERE "Owner" = ?', (owner,))
        except sqlite3.OperationalError:
            pass


def next_patient_id():
    # IDs are unique across ALL users, not just the current one
    everyone = load_patients()
    if not everyone:
        return "HIS-00001"
    last = max(int(p["Patient ID"].split("-")[1]) for p in everyone)
    return f"HIS-{last + 1:05d}"