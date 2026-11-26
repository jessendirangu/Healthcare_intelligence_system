import re
from collections import Counter
from datetime import datetime, timedelta, timezone

import pandas as pd
import pycountry
import requests
import streamlit as st

import danger_signs
import risk_check
import risk_pages
from storage import delete_my_patients, load_patients, next_patient_id, save_patient
import auth
import chp
import habits
import health_education
import home
import i18n
import intro
import measure
import tracker
from i18n import t
from themes import THEMES, theme_css


# ---------------------------------------------------------------
# Settings
# ---------------------------------------------------------------

TOKEN_URL = "https://icdaccessmanagement.who.int/connect/token"
SEARCH_URL = "https://id.who.int/icd/release/11/2026-01/mms/search"

COUNTRIES = sorted(country.name for country in pycountry.countries)

# Backup list, used when the WHO API can't be reached
# (no credentials, no internet, or no match for the search).
LOCAL_DISEASES = {
    "Infectious diseases": [
        "Malaria", "Tuberculosis", "HIV disease", "Pneumonia", "Cholera",
        "Hepatitis B", "Hepatitis C", "Influenza", "Dengue",
        "Ebola virus disease", "Other infectious disease",
    ],
    "Cardiovascular diseases": [
        "Hypertension", "Heart failure", "Coronary artery disease",
        "Stroke", "Other cardiovascular disease",
    ],
    "Respiratory diseases": [
        "Asthma", "Chronic obstructive pulmonary disease (COPD)",
        "Bronchitis", "Other respiratory disease",
    ],
    "Endocrine and metabolic diseases": [
        "Diabetes mellitus", "Obesity", "Thyroid disorder",
        "Other endocrine or metabolic disease",
    ],
    "Cancers": [
        "Breast cancer", "Cervical cancer", "Prostate cancer",
        "Lung cancer", "Colorectal cancer", "Other cancer",
    ],
    "Neurological diseases": [
        "Epilepsy", "Alzheimer disease", "Parkinson disease",
        "Migraine", "Other neurological disease",
    ],
    "Mental health conditions": [
        "Depressive disorder", "Anxiety disorder", "Bipolar disorder",
        "Schizophrenia", "Other mental health condition",
    ],
    "Digestive diseases": [
        "Gastritis", "Peptic ulcer disease", "Crohn disease",
        "Liver disease", "Other digestive disease",
    ],
    "Renal diseases": [
        "Chronic kidney disease", "Acute kidney injury", "Other renal disease",
    ],
    "Other / not yet classified": [
        "Other condition", "Diagnosis not yet established",
    ],
}


# ---------------------------------------------------------------
# WHO ICD-11 API
# ---------------------------------------------------------------

@st.cache_data(ttl=3300, show_spinner=False)
def get_who_token():
    # WHO tokens expire after an hour, so keep one for 55 minutes.
    response = requests.post(
        TOKEN_URL,
        data={"grant_type": "client_credentials", "scope": "icdapi_access"},
        auth=(st.secrets["WHO_CLIENT_ID"], st.secrets["WHO_CLIENT_SECRET"]),
        timeout=30,
    )
    response.raise_for_status()
    return response.json()["access_token"]


@st.cache_data(ttl=3600, show_spinner="Searching WHO ICD-11...")
def search_who(term):
    # Cached because Streamlit reruns the whole script on every click,
    # and we don't want to call the API again each time.
    headers = {
        "Authorization": f"Bearer {get_who_token()}",
        "Accept": "application/json",
        "Accept-Language": "en",
        "API-Version": "v2",
    }
    response = requests.get(
        SEARCH_URL, headers=headers, params={"q": term}, timeout=30
    )
    response.raise_for_status()

    matches = []
    for item in response.json().get("destinationEntities", []):
        title = item.get("title", "")
        if isinstance(title, dict):
            title = title.get("@value", "")
        # WHO highlights the search word with <em> tags - remove them
        title = re.sub(r"<[^>]+>", "", title).strip()
        matches.append({
            "title": title or "Unknown condition",
            "code": item.get("theCode", ""),
            "uri": item.get("id", ""),
        })

    # Show specific diseases first. In ICD-11, codes ending in "Z" mean
    # "unspecified" and codes ending in "Y" mean "other specified", so
    # those general catch-all entries go to the bottom of the list.
    def generality(match):
        title = match["title"].lower()
        code = match["code"].split("&")[0].split("/")[0]
        if "unspecified" in title or code.endswith("Z"):
            return 2
        if "other specified" in title or code.endswith("Y"):
            return 1
        return 0

    matches.sort(key=generality)  # stable sort keeps WHO's ranking within each group
    return matches


@st.cache_data(ttl=86400, show_spinner=False)
def who_definition(uri):
    # Fetch the full ICD-11 entry for one disease and return its definition
    if not uri:
        return ""
    headers = {
        "Authorization": f"Bearer {get_who_token()}",
        "Accept": "application/json",
        "Accept-Language": "en",
        "API-Version": "v2",
    }
    response = requests.get(
        uri.replace("http://", "https://"), headers=headers, timeout=30
    )
    response.raise_for_status()
    definition = response.json().get("definition", "")
    if isinstance(definition, dict):
        definition = definition.get("@value", "")
    return definition


def age_category(age):
    if age < 18:
        return "Children/Adolescents"
    if age < 60:
        return "Adults"
    return "Older Adults"


def calculate_bmi(weight_kg, height_cm):
    if not weight_kg or not height_cm:
        return None
    height_m = height_cm / 100
    return round(weight_kg / height_m ** 2, 1)


def bmi_class(bmi):
    if bmi is None:
        return ""
    if bmi < 18.5:
        return "Underweight"
    if bmi < 25:
        return "Normal"
    if bmi < 30:
        return "Overweight"
    return "Obese"


# Adult reference ranges: (low, high). A reading outside the range is flagged.
# Children have different normal ranges, so they are not flagged here.
ADULT_RANGES = {
    "Temperature (°C)": (36.0, 37.5),
    "Pulse (bpm)": (60, 100),
    "Respiratory rate (/min)": (12, 20),
    "Systolic BP (mmHg)": (90, 139),
    "Diastolic BP (mmHg)": (60, 89),
    "SpO2 (%)": (94, 100),
}


def vital_alerts(vitals, age):
    if age < 18:
        return []
    alerts = []
    for name, value in vitals.items():
        if value is None:
            continue
        low, high = ADULT_RANGES[name]
        if value < low:
            alerts.append(f"Low {name.split(' (')[0]} ({value})")
        elif value > high:
            alerts.append(f"High {name.split(' (')[0]} ({value})")
    return alerts


# ---------------------------------------------------------------
# Page setup and styling
# ---------------------------------------------------------------

st.set_page_config(
    page_title="Healthcare Intelligence System",
    page_icon="🏥",
    layout="wide",
)

# Navigation: a Home screen with step-by-step tiles (see home.py),
# plus a Home button and a "go to" list in the sidebar.
home.sidebar()
page = home.current()
if page != "home" and page not in home.PAGES and page not in ("page_diabetes", "page_heart"):
    page = "home"

st.sidebar.divider()
i18n.language_picker(st.sidebar, key="lang_sidebar")
theme_name = st.sidebar.selectbox(t("theme"), list(THEMES), key="theme")
theme = THEMES[theme_name]
st.markdown(theme_css(theme), unsafe_allow_html=True)

# Someone clicked "Verify my email" in their sign-up email
auth.handle_verification_link()

# Welcome screen, shown once per visit until the visitor clicks "Enter"
if not st.session_state.get("entered"):
    intro.render(theme)
    st.stop()


# ---------------------------------------------------------------
# Header and footer
# ---------------------------------------------------------------

# Date, time and place in the visitor's own time zone (from their browser)
now = i18n.local_now()
today = f"{i18n.long_date(now)} · {now:%H:%M}"

st.sidebar.markdown("### 🏥 Healthcare Intelligence")

st.html(f"""
<div style="display:flex; justify-content:space-between; align-items:center;
            flex-wrap:wrap; gap:12px; padding:18px 24px; margin-bottom:8px;
            background:{theme['surface']}; border:1px solid {theme['border']};
            border-top:4px solid {theme['accent']}; border-radius:12px;
            font-family:sans-serif;">
  <div style="display:flex; align-items:center; gap:14px;">
    <div style="width:46px; height:46px; border-radius:10px; background:{theme['accent']};
                display:flex; align-items:center; justify-content:center;
                color:#fff; font-size:22px; font-weight:700;">H</div>
    <div>
      <div style="font-size:22px; font-weight:700; color:{theme['text']};">
        Healthcare Intelligence System</div>
      <div style="font-size:14px; color:{theme['muted']};">
        {t("tagline")}</div>
    </div>
  </div>
  <div style="font-size:13px; color:{theme['muted']}; text-align:right;">
    {today}<br>{i18n.place_label()}
  </div>
</div>
""")


def footer():
    st.divider()
    st.html(f"""
    <div style="font-family:sans-serif; font-size:13px; color:{theme['muted']};
                display:flex; justify-content:space-between; flex-wrap:wrap; gap:8px;">
      <div>© {i18n.local_now().year} Jesse Kigo Ndirangu · Healthcare Intelligence System</div>
      <div>Data: WHO ICD-11 · MedlinePlus · UCI · NIDDK</div>
    </div>
    <div style="font-family:sans-serif; font-size:12px; color:{theme['muted']}; margin-top:6px;">
      {t("footer_disclaimer")}
    </div>
    """)


# Sign-in required to use the app
if not auth.require_login():
    footer()
    st.stop()
auth.sidebar_account()


# ---------------------------------------------------------------
# This user's patient records (see storage.py)
# ---------------------------------------------------------------

current_email = st.session_state.user["email"]
patients = load_patients(owner=current_email)


# ---------------------------------------------------------------
# Navigation
# ---------------------------------------------------------------

if page == "home":
    st.divider()
    home.render(theme, st.session_state.user.get("name", ""))
    footer()
    st.stop()

home.back_bar(page)

if page == "page_tracker":
    st.divider()
    tracker.render(current_email)
    footer()
    st.stop()

if page == "page_danger":
    st.divider()
    danger_signs.render()
    footer()
    st.stop()

if page == "page_measure":
    st.divider()
    measure.render(current_email)
    footer()
    st.stop()

if page == "page_chp":
    st.divider()
    chp.render(current_email)
    footer()
    st.stop()

if page == "page_habits":
    st.divider()
    habits.render(current_email)
    footer()
    st.stop()

if page == "page_risk":
    st.divider()
    risk_check.render()
    footer()
    st.stop()

# The remaining pages are not translated yet
if i18n.lang() == "sw":
    st.info(t("english_only"))

if page == "page_education":
    st.divider()
    health_education.render(patients, search_who, who_definition)
    footer()
    st.stop()

if page == "page_ai":
    st.divider()
    which = st.segmented_control(t("ai_pick"), ["page_diabetes", "page_heart"],
                                 default="page_diabetes", format_func=t, key="ai_which") or "page_diabetes"
    if which == "page_diabetes":
        risk_pages.render_diabetes()
    else:
        risk_pages.render_heart()
    footer()
    st.stop()

if page == "page_diabetes":
    st.divider()
    risk_pages.render_diabetes()
    footer()
    st.stop()

if page == "page_heart":
    st.divider()
    risk_pages.render_heart()
    footer()
    st.stop()


# ---------------------------------------------------------------
# Overview
# ---------------------------------------------------------------

st.divider()
st.header("Clinical overview")

category_counts = Counter(p["Category"] for p in patients)
children = category_counts["Children/Adolescents"]
adults = category_counts["Adults"]
older_adults = category_counts["Older Adults"]

c1, c2, c3, c4 = st.columns(4)
c1.metric("Total patients", len(patients))
c2.metric("Children / adolescents", children)
c3.metric("Adults (18-59)", adults)
c4.metric("Older adults (60+)", older_adults)

st.divider()
st.header("Patient population")

left, right = st.columns(2)
with left:
    st.subheader("By age group")
    age_df = pd.DataFrame({
        "Age group": ["Children", "Adults", "Older adults"],
        "Patients": [children, adults, older_adults],
    })
    st.bar_chart(age_df.set_index("Age group"), color="#2F7D6D")

with right:
    st.subheader("By gender")
    if patients:
        gender_df = pd.DataFrame(
            Counter(p["Gender"] for p in patients).items(),
            columns=["Gender", "Patients"],
        )
        st.bar_chart(gender_df.set_index("Gender"), color="#6B8FA3")
    else:
        st.info("Register patients to see the gender breakdown.")


# ---------------------------------------------------------------
# Patient registration
# ---------------------------------------------------------------

st.divider()
st.header("Register a patient")

# Diagnosis lookup sits outside the form so the results
# update as soon as you type a search term.
st.markdown("#### Diagnosis (WHO ICD-11)")

disease, disease_code = "", ""
use_local_list = False

search_term = st.text_input(
    "Search disease or diagnosis",
    placeholder="e.g. diabetes, malaria, tuberculosis",
).strip()

if len(search_term) >= 2:
    try:
        matches = search_who(search_term)
    except Exception:
        st.warning(
            "Couldn't reach the WHO ICD-11 service. "
            "Pick the diagnosis from the local list instead."
        )
        use_local_list = True
    else:
        if matches:
            choice = st.selectbox(
                "Select the matching diagnosis",
                range(len(matches)),
                format_func=lambda i: (
                    f"{matches[i]['title']} "
                    f"(ICD-11: {matches[i]['code'] or 'no code'})"
                ),
            )
            disease = matches[choice]["title"]
            disease_code = matches[choice]["code"]
        else:
            st.info("No WHO match. Try another term, or use the local list below.")
            use_local_list = True

if use_local_list:
    group = st.selectbox("Disease group", list(LOCAL_DISEASES))
    disease = st.selectbox("Diagnosis", LOCAL_DISEASES[group])

with st.form("patient_form", clear_on_submit=True):
    full_name = st.text_input("Full name")

    col1, col2, col3 = st.columns(3)
    age = col1.number_input("Age", min_value=0, max_value=120, value=25)
    gender = col2.selectbox(
        "Gender", ["Female", "Male", "Other", "Prefer not to say"]
    )
    diagnosis_status = col3.selectbox(
        "Diagnosis status",
        ["Confirmed", "Suspected", "Under investigation", "Historical"],
    )

    st.markdown("#### Vital signs")
    st.caption("Leave blank if not taken. Abnormal readings are flagged for adults (18+).")
    v1, v2, v3, v4 = st.columns(4)
    temperature = v1.number_input(
        "Temperature (°C)", 30.0, 45.0, value=None, step=0.1, format="%.1f"
    )
    pulse = v2.number_input("Pulse (bpm)", 20, 250, value=None)
    resp_rate = v3.number_input("Respiratory rate (/min)", 4, 80, value=None)
    spo2 = v4.number_input("SpO2 (%)", 50, 100, value=None)

    v5, v6, v7, v8 = st.columns(4)
    systolic = v5.number_input("Systolic BP (mmHg)", 50, 260, value=None)
    diastolic = v6.number_input("Diastolic BP (mmHg)", 30, 160, value=None)
    weight = v7.number_input("Weight (kg)", 1.0, 300.0, value=None, step=0.5)
    height = v8.number_input("Height (cm)", 40.0, 230.0, value=None, step=0.5)

    st.markdown("#### Location and nationality")
    col4, col5 = st.columns(2)
    with col4:
        country_residence = st.selectbox(
            "Country of residence", COUNTRIES, index=COUNTRIES.index("Kenya")
        )
        city_residence = st.text_input("City of residence", placeholder="e.g. Nairobi")
        country_birth = st.selectbox(
            "Country of birth", COUNTRIES, index=COUNTRIES.index("Kenya")
        )
    with col5:
        city_birth = st.text_input("City of birth", placeholder="e.g. Kisumu")
        nationality = st.text_input("Nationality", placeholder="e.g. Kenyan")

    st.markdown("#### Optional (self-reported)")
    col6, col7 = st.columns(2)
    race = col6.selectbox(
        "Race",
        [
            "Prefer not to say", "Black or African American", "White",
            "Asian", "American Indian or Alaska Native",
            "Native Hawaiian or Other Pacific Islander", "Mixed race", "Other",
        ],
    )
    religion = col7.selectbox(
        "Religion",
        [
            "Prefer not to say", "Christian", "Muslim", "Hindu", "Buddhist",
            "Traditional / Indigenous beliefs", "Other",
        ],
    )

    submitted = st.form_submit_button("Register patient", width="stretch")

if submitted:
    if not full_name.strip():
        st.error("Please enter the patient's full name.")
    else:
        patient_id = next_patient_id()
        vitals = {
            "Temperature (°C)": temperature,
            "Pulse (bpm)": pulse,
            "Respiratory rate (/min)": resp_rate,
            "Systolic BP (mmHg)": systolic,
            "Diastolic BP (mmHg)": diastolic,
            "SpO2 (%)": spo2,
        }
        bmi = calculate_bmi(weight, height)
        alerts = vital_alerts(vitals, age)

        save_patient({
            "Owner": current_email,
            "Patient ID": patient_id,
            "Full Name": full_name.strip(),
            "Age": int(age),
            "Gender": gender,
            "Category": age_category(age),
            "Disease / Diagnosis": disease,
            "ICD-11 Code": disease_code,
            "Diagnosis Status": diagnosis_status,
            **vitals,
            "Weight (kg)": weight,
            "Height (cm)": height,
            "BMI": bmi,
            "BMI Class": bmi_class(bmi),
            "Alerts": "; ".join(alerts),
            "Country of Residence": country_residence,
            "City of Residence": city_residence.strip(),
            "Country of Birth": country_birth,
            "City of Birth": city_birth.strip(),
            "Nationality": nationality.strip(),
            "Race": race,
            "Religion": religion,
            "Registered At": i18n.local_now().strftime("%Y-%m-%d %H:%M:%S"),
        })
        # st.rerun() wipes anything shown on this run, so save the
        # message and show it after the page reloads.
        st.session_state.flash = f"Patient {patient_id} registered."
        st.rerun()

if "flash" in st.session_state:
    st.success(st.session_state.pop("flash"))


# ---------------------------------------------------------------
# Patient records
# ---------------------------------------------------------------

st.divider()
st.header("Vital sign alerts")

flagged = [p for p in patients if p.get("Alerts")]
if flagged:
    for p in flagged:
        st.warning(f"**{p['Patient ID']} · {p['Full Name']}**: {p['Alerts']}")
elif patients:
    st.success("No abnormal vital signs recorded.")
else:
    st.info("Alerts will appear here when a patient has abnormal vitals.")

st.divider()
st.header("Patient records")

if patients:
    st.caption("Only patients you registered are shown. Other users cannot see them.")
    patient_df = pd.DataFrame(patients).drop(columns=["Owner"], errors="ignore")
    st.dataframe(patient_df, width="stretch", hide_index=True)
    st.download_button(
        "Download records (CSV)",
        patient_df.to_csv(index=False).encode("utf-8"),
        file_name="patients.csv",
        mime="text/csv",
    )

    with st.expander("Delete my test records"):
        st.caption("Removes all patients that you registered. This can't be undone.")
        confirm = st.checkbox("Yes, I want to delete my records")
        if st.button("Delete my records", disabled=not confirm):
            delete_my_patients(current_email)
            st.session_state.flash = "Your records were deleted."
            st.rerun()
else:
    st.info("No patients registered yet. Use the form above.")


# ---------------------------------------------------------------
# Disease analytics
# ---------------------------------------------------------------

st.divider()
st.header("Disease analytics")

diagnosed = [p for p in patients if p["Disease / Diagnosis"]]

if diagnosed:
    disease_df = pd.DataFrame(
        Counter(p["Disease / Diagnosis"] for p in diagnosed).most_common(),
        columns=["Disease", "Patients"],
    )
    status_df = pd.DataFrame(
        Counter(p["Diagnosis Status"] for p in diagnosed).items(),
        columns=["Diagnosis status", "Patients"],
    )

    left, right = st.columns(2)
    with left:
        st.subheader("Most recorded diagnoses")
        st.bar_chart(disease_df.set_index("Disease"), color="#2F7D6D", horizontal=True)
    with right:
        st.subheader("Diagnosis status")
        st.bar_chart(
            status_df.set_index("Diagnosis status"), color="#6B8FA3", horizontal=True
        )
elif patients:
    st.info("Disease charts will appear once patients have a diagnosis recorded.")
else:
    st.info("Register some fictional test patients to see disease analytics.")


# ---------------------------------------------------------------
# Registrations over time
# ---------------------------------------------------------------

st.divider()
st.header("Registrations over time")

if patients:
    activity_df = pd.DataFrame(
        sorted(Counter(p["Registered At"][:10] for p in patients).items()),
        columns=["Date", "Registrations"],
    )
    activity_df["Date"] = pd.to_datetime(activity_df["Date"])
    st.line_chart(activity_df.set_index("Date"), color="#2F7D6D")
else:
    st.info("Registration activity will show here once patients are added.")


footer()