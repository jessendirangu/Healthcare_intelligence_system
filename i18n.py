"""English / Kiswahili text for the website.

Every piece of text shown to visitors is stored here in both languages and
fetched with t("key"). The chosen language is kept in st.session_state.lang.
Other files can add their own text with register({...}).
"""

import streamlit as st

LANGUAGES = {"en": "English", "sw": "Kiswahili"}

TEXT = {
    # Menu and layout
    "menu": {"en": "Menu", "sw": "Menyu"},
    "theme": {"en": "Theme", "sw": "Mandhari"},
    "language": {"en": "🌐 Language / Lugha", "sw": "🌐 Lugha / Language"},
    "page_tracker": {"en": "My health tracker", "sw": "Kifuatilia afya yangu"},
    "page_dashboard": {"en": "Patient dashboard", "sw": "Dashibodi ya wagonjwa"},
    "page_education": {"en": "Health education", "sw": "Elimu ya afya"},
    "page_diabetes": {"en": "Diabetes risk (AI)", "sw": "Hatari ya kisukari (AI)"},
    "page_heart": {"en": "Heart disease risk (AI)", "sw": "Hatari ya ugonjwa wa moyo (AI)"},
    "tagline": {
        "en": "Self-monitoring, health education and clinical analytics",
        "sw": "Kujifuatilia afya, elimu ya afya na takwimu za kliniki",
    },
    "english_only": {
        "en": "",
        "sw": "Ukurasa huu bado unapatikana kwa Kiingereza pekee. Tafsiri ya Kiswahili inakuja hivi karibuni.",
    },
    "footer_disclaimer": {
        "en": "For education and self-monitoring support only. It does not diagnose and is "
              "not a substitute for advice from a health worker. Use fictional data on the "
              "patient dashboard.",
        "sw": "Kwa elimu na kusaidia kujifuatilia afya tu. Haitoi utambuzi wa ugonjwa na "
              "haichukui nafasi ya ushauri wa mhudumu wa afya. Tumia data ya kubuni kwenye "
              "dashibodi ya wagonjwa.",
    },

    # Welcome screen
    "intro_sub": {
        "en": "Track your blood pressure, learn about your health and see how AI "
              "estimates risk. Built by a nurse, in English and Kiswahili.",
        "sw": "Fuatilia shinikizo lako la damu, jifunze kuhusu afya yako na uone jinsi "
              "AI inavyokadiria hatari. Imetengenezwa na muuguzi, kwa Kiingereza na Kiswahili.",
    },
    "intro_tip_label": {"en": "HEALTH TIP", "sw": "DONDOO LA AFYA"},
    "intro_enter": {"en": "Enter the website →", "sw": "Ingia kwenye tovuti →"},
    "intro_caption": {
        "en": "For education and self-monitoring support. Not a substitute for professional medical advice.",
        "sw": "Kwa elimu na kusaidia kujifuatilia. Haichukui nafasi ya ushauri wa kitaalamu wa afya.",
    },

    # Accounts
    "welcome": {"en": "Welcome", "sw": "Karibu"},
    "welcome_caption": {
        "en": "Sign in or create a free account to use the Healthcare Intelligence System.",
        "sw": "Ingia au fungua akaunti ya bure ili kutumia Healthcare Intelligence System.",
    },
    "sign_in": {"en": "Sign in", "sw": "Ingia"},
    "create_account": {"en": "Create account", "sw": "Fungua akaunti"},
    "login_label": {"en": "Email or phone number", "sw": "Barua pepe au nambari ya simu"},
    "login_help": {
        "en": "Outside Kenya, type your phone number with its + country code.",
        "sw": "Ukiwa nje ya Kenya, andika nambari yako ya simu pamoja na msimbo wa nchi (+).",
    },
    "password": {"en": "Password", "sw": "Nenosiri"},
    "too_many_attempts": {
        "en": "Too many failed attempts. Refresh the page to try again.",
        "sw": "Umejaribu mara nyingi bila mafanikio. Onyesha upya ukurasa ujaribu tena.",
    },
    "login_failed": {
        "en": "Incorrect email/phone or password.",
        "sw": "Barua pepe/simu au nenosiri si sahihi.",
    },
    "required_note": {"en": "Fields marked * are required.", "sw": "Sehemu zenye * ni lazima kujazwa."},
    "first_name": {"en": "First name *", "sw": "Jina la kwanza *"},
    "last_name": {"en": "Last name *", "sw": "Jina la mwisho *"},
    "email": {"en": "Email *", "sw": "Barua pepe *"},
    "phone_code": {"en": "Phone country code *", "sw": "Msimbo wa nchi wa simu *"},
    "phone": {"en": "Phone number *", "sw": "Nambari ya simu *"},
    "phone_ph": {"en": "e.g. 712 345 678", "sw": "mf. 712 345 678"},
    "country_residence": {"en": "Country of residence *", "sw": "Nchi unayoishi *"},
    "password_star": {"en": "Password *", "sw": "Nenosiri *"},
    "password_help": {
        "en": "At least 8 characters, with letters and numbers.",
        "sw": "Angalau herufi 8, zikiwa na herufi na nambari.",
    },
    "confirm_password": {"en": "Confirm password *", "sw": "Thibitisha nenosiri *"},
    "consent": {
        "en": "I agree that my name, email, phone number and the health readings I enter "
              "are stored to give me an account, in line with Kenya's Data Protection Act 2019. *",
        "sw": "Ninakubali jina langu, barua pepe, nambari ya simu na vipimo vya afya ninavyoweka "
              "vihifadhiwe ili nipate akaunti, kulingana na Sheria ya Ulinzi wa Data ya Kenya 2019. *",
    },
    "err_first": {"en": "First name is required.", "sw": "Jina la kwanza linahitajika."},
    "err_last": {"en": "Last name is required.", "sw": "Jina la mwisho linahitajika."},
    "err_email": {"en": "A valid email address is required.", "sw": "Barua pepe sahihi inahitajika."},
    "err_phone": {
        "en": "Enter a valid phone number for {dial}.",
        "sw": "Weka nambari sahihi ya simu ya {dial}.",
    },
    "err_pw_short": {
        "en": "Password must be at least 8 characters.",
        "sw": "Nenosiri lazima liwe na angalau herufi 8.",
    },
    "err_pw_mix": {
        "en": "Password must contain both letters and numbers.",
        "sw": "Nenosiri lazima liwe na herufi na nambari.",
    },
    "err_pw_match": {"en": "The two passwords do not match.", "sw": "Manenosiri mawili hayalingani."},
    "err_consent": {
        "en": "Please agree to the data statement to continue.",
        "sw": "Tafadhali kubali taarifa ya data ili kuendelea.",
    },
    "err_email_taken": {
        "en": "An account with this email already exists. Sign in instead.",
        "sw": "Akaunti yenye barua pepe hii tayari ipo. Ingia badala yake.",
    },
    "err_phone_taken": {
        "en": "An account with this phone number already exists. Sign in instead.",
        "sw": "Akaunti yenye nambari hii ya simu tayari ipo. Ingia badala yake.",
    },
    "account_created": {
        "en": "Your email is verified and your account is ready. Sign in below.",
        "sw": "Barua pepe yako imethibitishwa na akaunti yako iko tayari. Ingia hapa chini.",
    },

    # Email verification link (sign-up)
    "link_email_subject": {
        "en": "Verify your email for Healthcare Intelligence System",
        "sw": "Thibitisha barua pepe yako kwa Healthcare Intelligence System",
    },
    "link_email_intro": {
        "en": "Welcome! Please confirm your email address to finish creating your account.",
        "sw": "Karibu! Tafadhali thibitisha barua pepe yako ili ukamilishe kufungua akaunti.",
    },
    "link_button": {"en": "Verify my email", "sw": "Thibitisha barua pepe yangu"},
    "link_valid": {
        "en": "This link works once and expires in {hours} hours.",
        "sw": "Kiungo hiki kinatumika mara moja na kitaisha baada ya saa {hours}.",
    },
    "link_or_code": {
        "en": "Or type this code on the website instead:",
        "sw": "Au andika namba hii kwenye tovuti badala yake:",
    },
    "link_email_text": {
        "en": "Welcome! Open this link to verify your email (it expires in {hours} hours): {link}",
        "sw": "Karibu! Fungua kiungo hiki kuthibitisha barua pepe yako (kitaisha baada ya saa {hours}): {link}",
    },
    "link_or_code_screen": {
        "en": "Click the **Verify my email** button in the email, or type the code below.",
        "sw": "Bonyeza kitufe cha **Thibitisha barua pepe yangu** kwenye barua pepe, au andika namba hapa chini.",
    },
    "link_invalid": {
        "en": "This verification link has expired or was already used. Please create your account again.",
        "sw": "Kiungo hiki cha uthibitisho kimeisha muda au kimeshatumika. Tafadhali fungua akaunti tena.",
    },

    # Email verification codes
    "otp_title": {"en": "Check your email", "sw": "Angalia barua pepe yako"},
    "otp_sent": {
        "en": "We sent a 6-digit code to **{email}**. Enter it below. It expires in {minutes} minutes. "
              "If you can't find it, check your spam folder.",
        "sw": "Tumetuma namba ya tarakimu 6 kwa **{email}**. Iweke hapa chini. Itaisha baada ya "
              "dakika {minutes}. Usipoiona, angalia folda ya spam.",
    },
    "otp_label": {"en": "Verification code", "sw": "Namba ya uthibitisho"},
    "otp_verify": {"en": "Verify", "sw": "Thibitisha"},
    "otp_resend": {"en": "Send a new code", "sw": "Tuma namba mpya"},
    "otp_resend_wait": {"en": "New code in {s}s", "sw": "Namba mpya baada ya sekunde {s}"},
    "otp_resent": {"en": "A new code has been sent.", "sw": "Namba mpya imetumwa."},
    "otp_cancel": {"en": "Cancel", "sw": "Ghairi"},
    "otp_wrong": {
        "en": "That code is not correct. {n} tries left.",
        "sw": "Namba hiyo si sahihi. Umebakiza majaribio {n}.",
    },
    "otp_expired": {
        "en": "This code has expired. Send a new code.",
        "sw": "Namba hii imeisha muda. Tuma namba mpya.",
    },
    "otp_locked": {
        "en": "Too many wrong codes. Send a new code or cancel and start again.",
        "sw": "Umekosea mara nyingi. Tuma namba mpya au ghairi uanze upya.",
    },
    "otp_send_failed": {
        "en": "We couldn't send the email. Please try again in a few minutes.",
        "sw": "Imeshindikana kutuma barua pepe. Tafadhali jaribu tena baada ya dakika chache.",
    },
    "otp_test_mode": {
        "en": "Test mode: email isn't set up on this computer, so the code was printed in the terminal.",
        "sw": "Hali ya majaribio: barua pepe haijawekwa kwenye kompyuta hii, kwa hiyo namba imeonyeshwa kwenye terminal.",
    },
    "otp_email_subject": {
        "en": "{code} is your verification code",
        "sw": "{code} ni namba yako ya uthibitisho",
    },
    "otp_email_intro": {
        "en": "Your verification code for the Healthcare Intelligence System is:",
        "sw": "Namba yako ya uthibitisho ya Healthcare Intelligence System ni:",
    },
    "otp_email_note": {
        "en": "It expires in {minutes} minutes. Never share this code with anyone. "
              "If you didn't request it, you can ignore this email.",
        "sw": "Itaisha baada ya dakika {minutes}. Usimpe mtu yeyote namba hii. "
              "Kama hukuiomba, puuza barua pepe hii.",
    },
    "otp_email_text": {
        "en": "Your Healthcare Intelligence System verification code is {code}. "
              "It expires in {minutes} minutes. Never share this code with anyone.",
        "sw": "Namba yako ya uthibitisho ya Healthcare Intelligence System ni {code}. "
              "Itaisha baada ya dakika {minutes}. Usimpe mtu yeyote namba hii.",
    },
    "signed_in_as": {"en": "Signed in as **{name}**", "sw": "Umeingia kama **{name}**"},
    "sign_out": {"en": "Sign out", "sw": "Toka"},
}

DAYS = {
    "en": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"],
    "sw": ["Jumatatu", "Jumanne", "Jumatano", "Alhamisi", "Ijumaa", "Jumamosi", "Jumapili"],
}
MONTHS = {
    "en": ["January", "February", "March", "April", "May", "June", "July",
           "August", "September", "October", "November", "December"],
    "sw": ["Januari", "Februari", "Machi", "Aprili", "Mei", "Juni", "Julai",
           "Agosti", "Septemba", "Oktoba", "Novemba", "Desemba"],
}


def register(entries):
    """Add another file's text, e.g. register({"key": {"en": ..., "sw": ...}})."""
    TEXT.update(entries)


def lang():
    return st.session_state.get("lang", "en")


def t(key, **values):
    """Text for `key` in the chosen language (English if no translation)."""
    entry = TEXT.get(key)
    if entry is None:
        return key
    text = entry.get(lang()) or entry["en"]
    return text.format(**values) if values else text


def long_date(when):
    """e.g. 'Tuesday, 24 November 2026' or 'Jumanne, 24 Novemba 2026'."""
    code = lang()
    return f"{DAYS[code][when.weekday()]}, {when.day} {MONTHS[code][when.month - 1]} {when.year}"


def short_datetime(when):
    """e.g. '24 Nov 2026, 08:30'."""
    month = MONTHS[lang()][when.month - 1][:3]
    return f"{when.day} {month} {when.year}, {when:%H:%M}"


def _changed(widget_key):
    st.session_state.lang = st.session_state[widget_key]


def language_picker(where=st, key="lang_picker"):
    """Language switch. Several can appear on different screens; they stay in sync."""
    st.session_state[key] = lang()
    where.radio(
        TEXT["language"][lang()],
        list(LANGUAGES),
        format_func=LANGUAGES.get,
        key=key,
        horizontal=True,
        on_change=_changed,
        args=(key,),
    )