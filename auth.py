"""User accounts: sign up, sign in and sign out.

Passwords are never stored. Only a salted PBKDF2 hash is kept, so even the
site owner cannot read them. Only the minimum personal data needed for an
account is collected (data minimisation): no ID documents or ID numbers.

Verification:
- Create account: an email with a "Verify my email" link AND a 6-digit code.
  Either one confirms the email is real; only then is the account created.
  Pending sign-ups are kept in the database table pending_signups, so the
  link works even if it opens in another browser or on another device.
- Sign in: a 6-digit code is emailed every time (two-step sign-in). Codes are random, stored only as hashes, expire
after 10 minutes and lock after 5 wrong tries.

Storage:
- If SUPABASE_URL and SUPABASE_KEY are in secrets, accounts are saved in the
  online Supabase database (they survive app restarts).
- Otherwise they are saved in the local file users.db (for testing on a laptop).
"""

import hashlib
import hmac
import json
import re
import secrets
import smtplib
import sqlite3
import time
from datetime import datetime, timedelta, timezone
from email.message import EmailMessage

import phonenumbers
import pycountry
import streamlit as st

import i18n
from i18n import t

LOCAL_DB = "users.db"
MAX_ATTEMPTS = 5      # wrong passwords before the sign-in form locks
OTP_MINUTES = 10      # how long an email code stays valid
OTP_MAX_TRIES = 5     # wrong codes allowed before starting again
RESEND_WAIT = 60      # seconds before a new code can be requested
MAX_SENDS = 5         # codes per attempt, so codes can't be guessed endlessly
LINK_HOURS = 24       # how long a sign-up verification link stays valid
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
        return t("err_pw_short")
    if not re.search(r"[A-Za-z]", password) or not re.search(r"\d", password):
        return t("err_pw_mix")
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
    conn.execute("""
        CREATE TABLE IF NOT EXISTS pending_signups (
            token_hash TEXT PRIMARY KEY,
            email TEXT NOT NULL,
            payload TEXT NOT NULL,
            expires_at TEXT NOT NULL
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
# Pending sign-ups (waiting for the email link or code)
# Only a hash of each link token is stored, never the token itself.
# ---------------------------------------------------------------

def _pending_save(token_hash, email, payload):
    expires = (datetime.now(timezone.utc) + timedelta(hours=LINK_HOURS)).isoformat()
    _pending_delete(email)  # only the newest link for an email works
    if use_supabase():
        supabase_client().table("pending_signups").insert({
            "token_hash": token_hash, "email": email,
            "payload": payload, "expires_at": expires,
        }).execute()
        return
    with _local() as conn:
        conn.execute("INSERT INTO pending_signups VALUES (?, ?, ?, ?)",
                     (token_hash, email, json.dumps(payload), expires))


def _pending_take(token_hash):
    """Return the waiting sign-up for this link (and remove it), or None."""
    if use_supabase():
        rows = (supabase_client().table("pending_signups").select("*")
                .eq("token_hash", token_hash).limit(1).execute().data)
        row = rows[0] if rows else None
    else:
        with _local() as conn:
            found = conn.execute("SELECT * FROM pending_signups WHERE token_hash = ?",
                                 (token_hash,)).fetchone()
        row = dict(found) if found else None
        if row:
            row["payload"] = json.loads(row["payload"])
    if not row:
        return None
    _pending_delete(row["email"])
    expires = datetime.fromisoformat(str(row["expires_at"]).replace("Z", "+00:00"))
    return row["payload"] if expires > datetime.now(timezone.utc) else None


def _pending_delete(email):
    if use_supabase():
        supabase_client().table("pending_signups").delete().eq("email", email).execute()
        return
    with _local() as conn:
        conn.execute("DELETE FROM pending_signups WHERE email = ?", (email,))


def finish_sign_up(new_user):
    """Create the account after the email is confirmed. Returns an error key or None."""
    existing = find_user("email", new_user["email"])
    if existing:
        # Already confirmed (e.g. the link was clicked, then the code typed too)
        return None if existing["phone"] == new_user["phone"] else "err_email_taken"
    if find_user("phone", new_user["phone"]):
        return "err_phone_taken"
    create_user(new_user)
    _pending_delete(new_user["email"])
    return None


def go_to_sign_in(email, message_key):
    st.session_state.auth_mode = "sign_in"
    st.session_state.prefill_login = email
    st.session_state.auth_flash = t(message_key)


def app_url():
    try:
        return st.secrets.get("APP_URL", "http://localhost:8501").rstrip("/")
    except Exception:
        return "http://localhost:8501"


def handle_verification_link():
    """Call at the top of app.py. Handles https://site/?verify=TOKEN from the email."""
    token = st.query_params.get("verify")
    if not token:
        return
    st.query_params.clear()  # remove the token from the address bar
    st.session_state.entered = True  # skip the welcome page
    new_user = _pending_take(_code_hash(token))
    if new_user is None:
        st.session_state.auth_mode = "sign_up"
        st.session_state.link_error = t("link_invalid")
        return
    error = finish_sign_up(new_user)
    if error:
        st.session_state.auth_mode = "sign_up"
        st.session_state.link_error = t(error)
    else:
        go_to_sign_in(new_user["email"], "account_created")


# ---------------------------------------------------------------
# One-time codes (OTP) sent by email
# ---------------------------------------------------------------

def email_configured():
    try:
        return "SMTP_USER" in st.secrets and "SMTP_PASSWORD" in st.secrets
    except Exception:
        return False


def send_email(to, subject, text, html):
    """Send an email through the SMTP account in secrets (Gmail by default)."""
    user = st.secrets["SMTP_USER"]
    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = st.secrets.get("SMTP_FROM", f"Healthcare Intelligence System <{user}>")
    msg["To"] = to
    msg.set_content(text)
    msg.add_alternative(html, subtype="html")
    host = st.secrets.get("SMTP_HOST", "smtp.gmail.com")
    password = st.secrets["SMTP_PASSWORD"].replace(" ", "")

    # Try the secure port 465 first. Some networks and antivirus programs block it,
    # so if the connection is cut, try port 587 (STARTTLS), the other standard option.
    try:
        with smtplib.SMTP_SSL(host, 465, timeout=20) as server:
            server.login(user, password)
            server.send_message(msg)
            return
    except smtplib.SMTPAuthenticationError:
        raise  # wrong password: trying another port won't help
    except (smtplib.SMTPServerDisconnected, ConnectionError, OSError) as error:
        print(f"[EMAIL] Port 465 failed ({error!r}). Trying port 587...", flush=True)

    with smtplib.SMTP(host, 587, timeout=20) as server:
        server.ehlo()
        server.starttls()
        server.ehlo()
        server.login(user, password)
        server.send_message(msg)


def mask_email(email):
    name, _, domain = email.partition("@")
    return f"{name[0]}{'*' * max(len(name) - 1, 3)}@{domain}"


def _code_hash(code):
    return hashlib.sha256(code.encode()).hexdigest()


def _send_code(otp):
    """Make a new code for this pending verification and email it."""
    if otp.get("sends", 0) >= MAX_SENDS:
        return False
    otp["sends"] = otp.get("sends", 0) + 1
    code = f"{secrets.randbelow(10 ** 6):06d}"
    otp.update(hash=_code_hash(code), expires=time.time() + OTP_MINUTES * 60,
               tries=0, sent_at=time.time())

    # Sign-up emails also carry a one-click verification link
    link = ""
    if otp["purpose"] == "sign_up":
        token = secrets.token_urlsafe(32)
        try:
            _pending_save(_code_hash(token), otp["email"], otp["payload"])
        except Exception as error:
            print(f"[EMAIL ERROR] Could not save the pending sign-up. Has the "
                  f"pending_signups table been created in Supabase? Details: {error!r}", flush=True)
            return False
        link = f"{app_url()}/?verify={token}"

    if not email_configured():
        # Laptop testing without an email account: show the code (and link) in the terminal only
        print(f"\n[TEST MODE] Verification code for {otp['email']}: {code}", flush=True)
        if link:
            print(f"[TEST MODE] Verification link: {link}", flush=True)
        otp["test_mode"] = True
        return True

    text = t("otp_email_text", code=code, minutes=OTP_MINUTES)
    button = ""
    if link:
        text = t("link_email_text", link=link, hours=LINK_HOURS) + "\n\n" + text
        button = f"""
      <p style="font-size:16px;color:#1F2D2B">{t("link_email_intro")}</p>
      <p style="text-align:center;margin:22px 0">
        <a href="{link}" style="background:#2F7D6D;color:#FFFFFF;text-decoration:none;
           font-weight:700;padding:14px 28px;border-radius:10px;display:inline-block">
           {t("link_button")}</a></p>
      <p style="font-size:13px;color:#5B6B67">{t("link_valid", hours=LINK_HOURS)}</p>
      <hr style="border:none;border-top:1px solid #DCE5E2;margin:20px 0">
      <p style="font-size:14px;color:#5B6B67">{t("link_or_code")}</p>"""
    html = f"""<div style="font-family:sans-serif;max-width:480px;margin:auto;padding:24px;
                border:1px solid #DCE5E2;border-radius:12px">
      <div style="color:#2F7D6D;font-weight:700;letter-spacing:2px;font-size:12px">
        HEALTHCARE INTELLIGENCE SYSTEM</div>{button}
      <p style="font-size:16px;color:#1F2D2B">{t("otp_email_intro")}</p>
      <div style="font-size:34px;font-weight:800;letter-spacing:8px;color:#1F2D2B;
                  background:#EEF4F2;border-radius:10px;padding:14px;text-align:center">{code}</div>
      <p style="font-size:14px;color:#5B6B67">{t("otp_email_note", minutes=OTP_MINUTES)}</p>
    </div>"""
    try:
        subject = t("link_email_subject") if link else t("otp_email_subject", code=code)
        send_email(otp["email"], subject, text, html)
        return True
    except smtplib.SMTPAuthenticationError as error:
        print(f"[EMAIL ERROR] Gmail refused the login. Check SMTP_USER and the 16-letter "
              f"app password (not your normal Gmail password). Details: {error!r}", flush=True)
        return False
    except Exception as error:
        print(f"[EMAIL ERROR] Could not send the email. Details: {error!r}", flush=True)
        return False


def start_verification(purpose, email, payload):
    """purpose: 'sign_up' or 'sign_in'. payload is used once the code is right."""
    otp = {"purpose": purpose, "email": email, "payload": payload}
    if _send_code(otp):
        st.session_state.otp = otp
        st.rerun()
    st.error(t("otp_send_failed"))


def _verification_screen():
    """Ask for the emailed code. Returns the payload once the right code is entered."""
    otp = st.session_state.otp
    st.markdown(f"#### {t('otp_title')}")
    st.write(t("otp_sent", email=mask_email(otp["email"]), minutes=OTP_MINUTES))
    if otp.get("test_mode"):
        st.info(t("otp_test_mode"))

    with st.form("otp_form"):
        code = st.text_input(t("otp_label"), max_chars=6, placeholder="123456")
        verify = st.form_submit_button(t("otp_verify"), type="primary", width="stretch")

    left, right = st.columns(2)
    wait = int(RESEND_WAIT - (time.time() - otp["sent_at"]))
    if left.button(t("otp_resend") if wait <= 0 else t("otp_resend_wait", s=wait),
                   disabled=wait > 0, width="stretch"):
        if _send_code(otp):
            st.success(t("otp_resent"))
        else:
            st.error(t("otp_send_failed"))
    if right.button(t("otp_cancel"), width="stretch"):
        st.session_state.pop("otp")
        st.rerun()

    if not verify:
        return None
    if time.time() > otp["expires"]:
        st.error(t("otp_expired"))
        return None
    if otp["tries"] >= OTP_MAX_TRIES:
        st.error(t("otp_locked"))
        return None
    if hmac.compare_digest(_code_hash(code.strip()), otp["hash"]):
        return st.session_state.pop("otp")["payload"]
    otp["tries"] += 1
    left_tries = OTP_MAX_TRIES - otp["tries"]
    st.error(t("otp_wrong", n=left_tries) if left_tries else t("otp_locked"))
    return None


def _pending(purpose):
    otp = st.session_state.get("otp")
    return otp is not None and otp["purpose"] == purpose


# ---------------------------------------------------------------
# Pages
# ---------------------------------------------------------------

def sign_in_form():
    # Step 2: the password was right, now check the emailed code
    if _pending("sign_in"):
        user = _verification_screen()
        if user:
            st.session_state.user = user
            st.rerun()
        return

    if "auth_flash" in st.session_state:
        st.success(st.session_state.pop("auth_flash"))

    attempts = st.session_state.get("failed_logins", 0)
    if attempts >= MAX_ATTEMPTS:
        st.error(t("too_many_attempts"))
        return

    with st.form("sign_in"):
        login = st.text_input(
            t("login_label"),
            value=st.session_state.get("prefill_login", ""),
            placeholder="you@example.com / +254712345678",
            help=t("login_help"),
        )
        password = st.text_input(t("password"), type="password")
        submitted = st.form_submit_button(t("sign_in"), type="primary", width="stretch")

    if submitted:
        email, phone = clean_email(login), clean_phone(login)
        user = find_user("email", email) if email else find_user("phone", phone) if phone else None
        if user and check_password(password, user["password_hash"]):
            st.session_state.failed_logins = 0
            st.session_state.pop("prefill_login", None)
            start_verification("sign_in", user["email"],
                               {"name": user["full_name"], "email": user["email"]})
        else:
            # Same message either way, so nobody can check which emails exist
            st.session_state.failed_logins = attempts + 1
            st.error(t("login_failed"))


def _sign_up():
    # Step 2: the form was fine, now check the emailed code
    if _pending("sign_up"):
        st.info(t("link_or_code_screen"))
        new_user = _verification_screen()
        if new_user:
            error = finish_sign_up(new_user)
            if error:
                st.error(t(error))
                return
            # Go straight to the sign-in screen with the email filled in
            go_to_sign_in(new_user["email"], "account_created")
            st.rerun()
        return

    if "link_error" in st.session_state:
        st.error(st.session_state.pop("link_error"))
    st.caption(t("required_note"))
    with st.form("sign_up"):
        c1, c2 = st.columns(2)
        first = c1.text_input(t("first_name"))
        last = c2.text_input(t("last_name"))
        email = st.text_input(t("email"))
        c3, c4 = st.columns([1, 1])
        dial = c3.selectbox(
            t("phone_code"), list(DIAL_CODES),
            index=list(DIAL_CODES).index("Kenya (+254)"),
        )
        phone = c4.text_input(t("phone"), placeholder=t("phone_ph"))
        country = st.selectbox(t("country_residence"), COUNTRIES, index=COUNTRIES.index("Kenya"))
        c7, c8 = st.columns(2)
        password = c7.text_input(t("password_star"), type="password", help=t("password_help"))
        confirm = c8.text_input(t("confirm_password"), type="password")
        consent = st.checkbox(t("consent"))
        submitted = st.form_submit_button(t("create_account"), type="primary", width="stretch")

    if not submitted:
        return

    clean_mail = clean_email(email)
    clean_tel = clean_phone(phone, DIAL_CODES[dial])
    problems = []
    if len(first.strip()) < 2:
        problems.append(t("err_first"))
    if len(last.strip()) < 2:
        problems.append(t("err_last"))
    if not clean_mail:
        problems.append(t("err_email"))
    if not clean_tel:
        problems.append(t("err_phone", dial=dial))
    if password_problem(password):
        problems.append(password_problem(password))
    if password != confirm:
        problems.append(t("err_pw_match"))
    if not consent:
        problems.append(t("err_consent"))
    if not problems:
        if find_user("email", clean_mail):
            problems.append(t("err_email_taken"))
        elif find_user("phone", clean_tel):
            problems.append(t("err_phone_taken"))

    if problems:
        for p in problems:
            st.error(p)
        return

    # The account is only created after the emailed code is confirmed
    start_verification("sign_up", clean_mail, {
        "full_name": f"{first.strip()} {last.strip()}",
        "email": clean_mail,
        "phone": clean_tel,
        "password_hash": hash_password(password),
        "country": country,
        "created_at": datetime.now(timezone.utc).isoformat(),
    })


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
        i18n.language_picker(key="lang_login")
        st.subheader(t("welcome"))
        st.caption(t("welcome_caption"))
        # A switch instead of tabs, so the page can move to "Sign in" by itself
        # after an account is created. Hidden while a code is being checked.
        if _pending("sign_in"):
            mode = "sign_in"
        elif _pending("sign_up"):
            mode = "sign_up"
        else:
            st.session_state.setdefault("auth_mode", "sign_in")
            mode = st.segmented_control(
                " ", ["sign_in", "sign_up"], key="auth_mode",
                format_func=lambda m: t("sign_in") if m == "sign_in" else t("create_account"),
                label_visibility="collapsed",
            ) or "sign_in"
        if mode == "sign_in":
            sign_in_form()
        else:
            _sign_up()
    return False


def sidebar_account():
    user = st.session_state.get("user")
    if user:
        role = " (admin)" if is_admin() else ""
        st.sidebar.caption(t("signed_in_as", name=user["name"]) + role)
        if st.sidebar.button(t("sign_out"), width="stretch"):
            st.session_state.pop("user")
            st.rerun()