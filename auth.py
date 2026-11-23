"""User accounts: sign up, sign in and sign out.

Passwords are never stored. Only a salted PBKDF2 hash is kept, so even the
site owner cannot read them. Only the minimum personal data needed for an
account is collected (data minimisation): no ID documents or ID numbers.

Storage:
- If SUPABASE_URL and SUPABASE_KEY are in secrets, accounts are saved in the
  online Supabase database (they survive app restarts).
- Otherwise they are saved in the local file users.db (for testing on a laptop).
"""

import hashlib
import hmac
import re
import secrets
import sqlite3
from datetime import datetime, timezone

import phonenumbers
import pycountry
import streamlit as st

LOCAL_DB = "users.db"
MAX_ATTEMPTS = 5
COUNTRIES = sorted(c.name for c in pycountry.countries)


def _dial_codes():
    """Every country with its phone code, e.g. 'Kenya (+254)' -> 'KE'."""
    codes = {}
    for country in pycountry.countries:
        number = phonenumbers.country_code_for_region(country.alpha_2)
        if number:
            codes[f"{country.name} (+{number})"] = country.alpha_2
    return dict(sorted(codes.items()))


DIAL_CODES = _dial_codes()


# ---------------------------------------------------------------
# Password hashing
# ---------------------------------------------------------------

def hash_password(password):
    salt = secrets.token_bytes(16)
    rounds = 200_000
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, rounds)
    return f"pbkdf2_sha256${rounds}${salt.hex()}${digest.hex()}"


def check_password(password, stored):
    try:
        _, rounds, salt, digest = stored.split("$")
        new = hashlib.pbkdf2_hmac("sha256", password.encode(), bytes.fromhex(salt), int(rounds))
        return hmac.compare_digest(new.hex(), digest)
    except (ValueError, AttributeError):
        return False


# ---------------------------------------------------------------
# Input checks
# ---------------------------------------------------------------

def clean_email(email):
    email = email.strip().lower()
    return email if re.fullmatch(r"[^@\s]+@[^@\s]+\.[a-z]{2,}", email) else None


def clean_phone(phone, region="KE"):
    """Check a phone number for the chosen country and return it in
    international form (e.g. +254712345678). Returns None if invalid.
    Numbers typed with a + code are understood whatever the region."""
    try:
        parsed = phonenumbers.parse(phone, region)
    except phonenumbers.NumberParseException:
        return None
    if not phonenumbers.is_valid_number(parsed):
        return None
    return phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.E164)


def password_problem(password):
    if len(password) < 8:
        return "Password must be at least 8 characters."
    if not re.search(r"[A-Za-z]", password) or not re.search(r"\d", password):
        return "Password must contain both letters and numbers."
    return None


# ---------------------------------------------------------------
# Storage
# ---------------------------------------------------------------

def use_supabase():
    try:
        return "SUPABASE_URL" in st.secrets and "SUPABASE_KEY" in st.secrets
    except Exception:
        return False


@st.cache_resource
def supabase_client():
    from supabase import create_client
    return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])


def _local():
    conn = sqlite3.connect(LOCAL_DB)
    conn.row_factory = sqlite3.Row
    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            phone TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            country TEXT,
            created_at TEXT
        )""")
    return conn


def find_user(column, value):
    """Look up one user by email or phone. Returns a dict or None."""
    if column not in ("email", "phone"):
        raise ValueError("Can only search by email or phone")
    if use_supabase():
        rows = supabase_client().table("users").select("*").eq(column, value).limit(1).execute().data
        return rows[0] if rows else None
    with _local() as conn:
        row = conn.execute(f"SELECT * FROM users WHERE {column} = ?", (value,)).fetchone()
        return dict(row) if row else None


def list_users():
    """All accounts for the admin page. Password hashes are never returned."""
    columns = "full_name, email, phone, country, created_at"
    if use_supabase():
        return supabase_client().table("users").select(columns).order("created_at").execute().data
    with _local() as conn:
        return [dict(r) for r in conn.execute(f"SELECT {columns} FROM users ORDER BY created_at")]


def is_admin():
    """Admins are listed in secrets (ADMIN_EMAILS), never chosen on the website."""
    user = st.session_state.get("user")
    if not user:
        return False
    try:
        admins = [e.strip().lower() for e in st.secrets.get("ADMIN_EMAILS", [])]
    except Exception:
        return False
    return user["email"] in admins


def create_user(user):
    if use_supabase():
        supabase_client().table("users").insert(user).execute()
    else:
        with _local() as conn:
            conn.execute(
                "INSERT INTO users (full_name, email, phone, password_hash, country, created_at) "
                "VALUES (:full_name, :email, :phone, :password_hash, :country, :created_at)",
                user,
            )


# ---------------------------------------------------------------
# Pages
# ---------------------------------------------------------------

def sign_in_form():
    attempts = st.session_state.get("failed_logins", 0)
    if attempts >= MAX_ATTEMPTS:
        st.error("Too many failed attempts. Refresh the page to try again.")
        return

    with st.form("sign_in"):
        login = st.text_input(
            "Email or phone number",
            placeholder="you@example.com or +254712345678",
            help="Outside Kenya, type your phone number with its + country code.",
        )
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Sign in", type="primary", width="stretch")

    if submitted:
        email, phone = clean_email(login), clean_phone(login)
        user = find_user("email", email) if email else find_user("phone", phone) if phone else None
        if user and check_password(password, user["password_hash"]):
            st.session_state.user = {"name": user["full_name"], "email": user["email"]}
            st.session_state.failed_logins = 0
            st.rerun()
        else:
            # Same message either way, so nobody can check which emails exist
            st.session_state.failed_logins = attempts + 1
            st.error("Incorrect email/phone or password.")


def _sign_up():
    st.caption("Fields marked * are required.")
    with st.form("sign_up"):
        c1, c2 = st.columns(2)
        first = c1.text_input("First name *")
        last = c2.text_input("Last name *")
        email = st.text_input("Email *")
        c3, c4 = st.columns([1, 1])
        dial = c3.selectbox(
            "Phone country code *", list(DIAL_CODES),
            index=list(DIAL_CODES).index("Kenya (+254)"),
        )
        phone = c4.text_input("Phone number *", placeholder="e.g. 712 345 678")
        country = st.selectbox("Country of residence *", COUNTRIES, index=COUNTRIES.index("Kenya"))
        c7, c8 = st.columns(2)
        password = c7.text_input("Password *", type="password", help="At least 8 characters, with letters and numbers.")
        confirm = c8.text_input("Confirm password *", type="password")
        consent = st.checkbox(
            "I agree that my name, email and phone number are stored to give me an "
            "account, in line with Kenya's Data Protection Act 2019. *"
        )
        submitted = st.form_submit_button("Create account", type="primary", width="stretch")

    if not submitted:
        return

    clean_mail = clean_email(email)
    clean_tel = clean_phone(phone, DIAL_CODES[dial])
    problems = []
    if len(first.strip()) < 2:
        problems.append("First name is required.")
    if len(last.strip()) < 2:
        problems.append("Last name is required.")
    if not clean_mail:
        problems.append("A valid email address is required.")
    if not clean_tel:
        problems.append(f"Enter a valid phone number for {dial}.")
    if password_problem(password):
        problems.append(password_problem(password))
    if password != confirm:
        problems.append("The two passwords do not match.")
    if not consent:
        problems.append("Please agree to the data statement to continue.")
    if not problems:
        if find_user("email", clean_mail):
            problems.append("An account with this email already exists. Sign in instead.")
        elif find_user("phone", clean_tel):
            problems.append("An account with this phone number already exists. Sign in instead.")

    if problems:
        for p in problems:
            st.error(p)
        return

    create_user({
        "full_name": f"{first.strip()} {last.strip()}",
        "email": clean_mail,
        "phone": clean_tel,
        "password_hash": hash_password(password),
        "country": country,
        "created_at": datetime.now(timezone.utc).isoformat(),
    })
    st.success("Account created. You can now sign in.")


def require_login():
    """Show the sign-in page until the visitor is signed in."""
    if st.session_state.get("user"):
        return True

    st.html("""
    <style>
      section[data-testid="stSidebar"], [data-testid="stSidebarCollapsedControl"] { display: none; }
    </style>""")
    _, middle, _ = st.columns([1, 2, 1])
    with middle:
        st.subheader("Welcome")
        st.caption("Sign in or create a free account to use the Healthcare Intelligence System.")
        sign_in_tab, sign_up_tab = st.tabs(["Sign in", "Create account"])
        with sign_in_tab:
            sign_in_form()
        with sign_up_tab:
            _sign_up()
    return False


def sidebar_account():
    user = st.session_state.get("user")
    if user:
        role = " (admin)" if is_admin() else ""
        st.sidebar.caption(f"Signed in as **{user['name']}**{role}")
        if st.sidebar.button("Sign out", width="stretch"):
            st.session_state.pop("user")
            st.rerun()