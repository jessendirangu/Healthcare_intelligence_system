"""Storage for CHP (Community Health Promoter) mode.

Tables
- chp_roles:  who has asked to be / is approved as a CHP (by email)
- households: households registered by a CHP (after verbal consent)
- members:    people in each household (name, sex, year of birth only)
- referrals:  referrals to a health facility and whether the person went

Readings for household members reuse the "readings" table with
owner = "member:<member id>", so all tracker features work for them.

Uses Supabase when configured, otherwise a local SQLite file (chp.db).
"""

import sqlite3
from datetime import datetime, timezone

from auth import _with_retry, supabase_client, use_supabase

LOCAL_DB = "chp.db"

_LOCAL_SCHEMA = """
CREATE TABLE IF NOT EXISTS chp_roles (
    email TEXT PRIMARY KEY, status TEXT NOT NULL, facility TEXT, area TEXT,
    requested_at TEXT, decided_at TEXT);
CREATE TABLE IF NOT EXISTS households (
    id INTEGER PRIMARY KEY AUTOINCREMENT, chp TEXT NOT NULL, code TEXT NOT NULL,
    head_name TEXT NOT NULL, village TEXT, phone TEXT, consent INTEGER NOT NULL,
    created_at TEXT);
CREATE TABLE IF NOT EXISTS members (
    id INTEGER PRIMARY KEY AUTOINCREMENT, household_id INTEGER NOT NULL, chp TEXT NOT NULL,
    name TEXT NOT NULL, sex TEXT, birth_year INTEGER, created_at TEXT);
CREATE TABLE IF NOT EXISTS habit_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT, owner TEXT NOT NULL, day TEXT NOT NULL,
    habits TEXT, created_at TEXT, UNIQUE (owner, day));
CREATE TABLE IF NOT EXISTS referrals (
    id INTEGER PRIMARY KEY AUTOINCREMENT, member_id INTEGER NOT NULL, chp TEXT NOT NULL,
    reason TEXT NOT NULL, note TEXT, referred_at TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'pending', updated_at TEXT);
"""


def _now():
    return datetime.now(timezone.utc).isoformat()


def _local():
    conn = sqlite3.connect(LOCAL_DB)
    conn.row_factory = sqlite3.Row
    conn.executescript(_LOCAL_SCHEMA)
    return conn


# ---------------------------------------------------------------
# Small generic helpers (select / insert / update)
# ---------------------------------------------------------------

def _select(table, order=None, **filters):
    if use_supabase():
        def run():
            query = supabase_client().table(table).select("*")
            for column, value in filters.items():
                query = query.eq(column, value)
            if order:
                query = query.order(order)
            return query.execute().data
        return _with_retry(run)
    where = " AND ".join(f"{c} = ?" for c in filters) or "1 = 1"
    sql = f"SELECT * FROM {table} WHERE {where}" + (f" ORDER BY {order}" if order else "")
    with _local() as conn:
        return [dict(r) for r in conn.execute(sql, list(filters.values()))]


def _insert(table, row):
    if use_supabase():
        return _with_retry(lambda: supabase_client().table(table).insert(row).execute().data)
    with _local() as conn:
        conn.execute(f"INSERT INTO {table} ({', '.join(row)}) VALUES ({', '.join('?' * len(row))})",
                     list(row.values()))


def _update(table, values, **filters):
    if use_supabase():
        def run():
            query = supabase_client().table(table).update(values)
            for column, value in filters.items():
                query = query.eq(column, value)
            return query.execute().data
        return _with_retry(run)
    sets = ", ".join(f"{c} = ?" for c in values)
    where = " AND ".join(f"{c} = ?" for c in filters)
    with _local() as conn:
        conn.execute(f"UPDATE {table} SET {sets} WHERE {where}",
                     list(values.values()) + list(filters.values()))


# ---------------------------------------------------------------
# CHP roles
# ---------------------------------------------------------------

def chp_status(email):
    """'approved', 'pending', 'rejected' or None."""
    rows = _select("chp_roles", email=email)
    return rows[0]["status"] if rows else None


def request_chp(email, facility, area):
    _insert("chp_roles", {"email": email, "status": "pending", "facility": facility,
                          "area": area, "requested_at": _now()})


def list_chp_requests():
    return _select("chp_roles", order="requested_at")


def decide_chp(email, approve):
    _update("chp_roles", {"status": "approved" if approve else "rejected", "decided_at": _now()},
            email=email)


# ---------------------------------------------------------------
# Households and members (always filtered by the CHP who owns them)
# ---------------------------------------------------------------

def households(chp):
    return _select("households", order="id", chp=chp)


def add_household(chp, head_name, village, phone):
    code = f"HH-{len(households(chp)) + 1:04d}"
    _insert("households", {"chp": chp, "code": code, "head_name": head_name, "village": village,
                           "phone": phone or None, "consent": True, "created_at": _now()})
    return code


def members(chp, household_id=None):
    if household_id is None:
        return _select("members", order="id", chp=chp)
    return _select("members", order="id", chp=chp, household_id=household_id)


def add_member(chp, household_id, name, sex, birth_year):
    _insert("members", {"chp": chp, "household_id": household_id, "name": name, "sex": sex,
                        "birth_year": birth_year, "created_at": _now()})


def member_owner(member_id):
    """The 'owner' value used for this member's readings."""
    return f"member:{member_id}"


# ---------------------------------------------------------------
# Referrals
# ---------------------------------------------------------------

def add_referral(chp, member_id, reason, note):
    _insert("referrals", {"chp": chp, "member_id": member_id, "reason": reason,
                          "note": note or None, "referred_at": _now(), "status": "pending"})


def referrals(chp=None):
    return _select("referrals", order="referred_at") if chp is None else \
        _select("referrals", order="referred_at", chp=chp)


def set_referral_status(chp, referral_id, status):
    _update("referrals", {"status": status, "updated_at": _now()}, id=referral_id, chp=chp)


def all_households():
    return _select("households", order="id")


def all_members():
    return _select("members", order="id")


# ---------------------------------------------------------------
# Daily healthy-habit check-ins (used by the Healthy habits page)
# ---------------------------------------------------------------

def habit_logs(owner):
    return _select("habit_logs", order="day", owner=owner)


def save_habits(owner, day, habits):
    """One row per person per day; saving again replaces that day's ticks."""
    value = ",".join(habits)
    if _select("habit_logs", owner=owner, day=day):
        _update("habit_logs", {"habits": value}, owner=owner, day=day)
    else:
        _insert("habit_logs", {"owner": owner, "day": day, "habits": value, "created_at": _now()})