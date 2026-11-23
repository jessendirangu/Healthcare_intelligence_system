import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
from datetime import datetime
from collections import Counter
import requests

# ==========================================
# WHO ICD-11 API CONNECTION
# ==========================================

WHO_TOKEN_URL = "https://icdaccessmanagement.who.int/connect/token"

WHO_SEARCH_URL = "https://id.who.int/icd/release/11/2026-01/mms/search"


@st.cache_data(ttl=3300, show_spinner=False)
def get_who_token():
    """Get an access token from the WHO ICD API."""

    client_id = st.secrets["WHO_CLIENT_ID"]
    client_secret = st.secrets["WHO_CLIENT_SECRET"]

    response = requests.post(
        WHO_TOKEN_URL,
        data={
            "grant_type": "client_credentials",
            "scope": "icdapi_access"
        },
        auth=(client_id, client_secret),
        timeout=30
    )

    response.raise_for_status()

    return response.json()["access_token"]


def search_who_diseases(search_term):
    """Search the WHO ICD-11 catalogue."""

    if not search_term or len(search_term.strip()) < 2:
        return []

    token = get_who_token()

    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json",
        "Accept-Language": "en",
        "API-Version": "v2"
    }

    response = requests.get(
        WHO_SEARCH_URL,
        headers=headers,
        params={"q": search_term.strip()},
        timeout=30
    )

    response.raise_for_status()

    results = response.json()

    return results.get("destinationEntities", [])

# --------------------------------------------------
# 1. PAGE CONFIGURATION
# --------------------------------------------------

st.set_page_config(
    page_title="Healthcare Intelligence System",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)


# --------------------------------------------------
# 2. CINEMATIC DESIGN
# --------------------------------------------------

st.markdown("""
<style>

.stApp {
    background:
        radial-gradient(circle at top right, #123D55 0%, transparent 35%),
        linear-gradient(135deg, #061321, #0A2235, #071827);
    color: #EAF7FF;
}

header[data-testid="stHeader"] {
    background: rgba(5, 18, 32, 0.8);
}

h1, h2, h3 {
    color: #EAF7FF !important;
    font-weight: 800 !important;
}

.hero-banner {
    padding: 40px;
    border-radius: 22px;
    background: linear-gradient(
        120deg,
        #063B50,
        #087E8B,
        #102A43
    );
    border: 1px solid rgba(80, 220, 220, 0.5);
    box-shadow: 0 12px 40px rgba(0,0,0,0.4);
    margin-bottom: 25px;
}

.hero-tag {
    color: #66F0DB;
    font-size: 12px;
    letter-spacing: 4px;
    font-weight: bold;
}

.hero-banner h1 {
    color: white !important;
    font-size: 38px;
    margin-top: 15px;
}

.hero-banner p {
    color: #C5EAF1;
    font-size: 16px;
}

div[data-testid="stMetric"] {
    background: linear-gradient(145deg, #12364A, #0B263A);
    border: 1px solid #267D91;
    padding: 22px;
    border-radius: 17px;
    box-shadow: 0 8px 25px #00000055;
    transition: 0.3s ease;
}

div[data-testid="stMetric"]:hover {
    border: 1px solid #55E6D3;
    transform: translateY(-3px);
}

div[data-testid="stMetricValue"] {
    color: #55E6D3 !important;
}

div[data-testid="stForm"] {
    background: linear-gradient(145deg, #102B40, #0A2032);
    border: 1px solid #267D91;
    padding: 25px;
    border-radius: 18px;
}

.stButton > button,
.stFormSubmitButton > button {
    background: linear-gradient(90deg, #087F8C, #20B8AD);
    color: white;
    border-radius: 10px;
    border: none;
    font-weight: bold;
    padding: 10px 22px;
}

.stButton > button:hover,
.stFormSubmitButton > button:hover {
    background: linear-gradient(90deg, #20B8AD, #45DCCB);
    color: white;
}

section[data-testid="stSidebar"] {
    background: #081B2B;
    border-right: 1px solid #267D91;
}

div[data-testid="stDataFrame"] {
    border: 1px solid #267D91;
    border-radius: 12px;
}

hr {
    border-color: #267D91;
}

</style>
""", unsafe_allow_html=True)


# --------------------------------------------------
# 3. LIVE CLOCK
# --------------------------------------------------

clock_html = """
<div style="
    background: linear-gradient(145deg, #102B40, #071827);
    border: 1px solid #35CFC0;
    border-radius: 18px;
    padding: 20px;
    text-align: center;
    font-family: Arial, sans-serif;
">

    <div style="
        color: #65E9D7;
        font-size: 11px;
        letter-spacing: 3px;
        font-weight: bold;
    ">
        LIVE LOCAL TIME
    </div>

    <div id="clock" style="
        color: #FFFFFF;
        font-size: 38px;
        font-weight: bold;
        margin-top: 12px;
        text-shadow: 0 0 15px #25CFC0;
    ">
        00:00:00
    </div>

    <div id="day" style="
        color: #65E9D7;
        font-size: 16px;
        margin-top: 8px;
    ">
        Loading...
    </div>

    <div id="date" style="
        color: #B9D8E5;
        font-size: 13px;
        margin-top: 5px;
    ">
        Loading date...
    </div>

    <div style="
        color: #8AAFC0;
        font-size: 11px;
        margin-top: 12px;
    ">
        NAIROBI • EAST AFRICA TIME
    </div>

</div>

<script>

function updateClock() {

    const now = new Date();

    const timeOptions = {
        timeZone: "Africa/Nairobi",
        hour: "2-digit",
        minute: "2-digit",
        second: "2-digit",
        hour12: false
    };

    const dayOptions = {
        timeZone: "Africa/Nairobi",
        weekday: "long"
    };

    const dateOptions = {
        timeZone: "Africa/Nairobi",
        day: "numeric",
        month: "long",
        year: "numeric"
    };

    document.getElementById("clock").textContent =
        new Intl.DateTimeFormat("en-GB", timeOptions).format(now);

    document.getElementById("day").textContent =
        new Intl.DateTimeFormat("en-GB", dayOptions).format(now);

    document.getElementById("date").textContent =
        new Intl.DateTimeFormat("en-GB", dateOptions).format(now);
}

updateClock();
setInterval(updateClock, 1000);

</script>
"""


# --------------------------------------------------
# 4. HERO SECTION
# --------------------------------------------------

st.html("""
<div class="hero-banner">

    <div class="hero-tag">
        ADVANCED HEALTHCARE ANALYTICS
    </div>

    <h1>🏥 Healthcare Intelligence System</h1>

    <p>
        Transforming healthcare data into meaningful
        insights for better clinical decisions.
    </p>

</div>
""")


# --------------------------------------------------
# 5. CLOCK AND SYSTEM STATUS
# --------------------------------------------------

clock_col, status_col = st.columns([2, 1])

with clock_col:

    components.html(
        clock_html,
        height=175,
        scrolling=False
    )

with status_col:

    st.markdown("### System Status")
    st.success("SYSTEM ONLINE")
    st.caption("Healthcare analytics dashboard")
    st.caption("Live patient monitoring interface")


# --------------------------------------------------
# 6. PATIENT DATABASE IN SESSION
# --------------------------------------------------

if "patients" not in st.session_state:
    st.session_state.patients = []

if "next_patient_id" not in st.session_state:
    st.session_state.next_patient_id = 1

patients = st.session_state.patients


# --------------------------------------------------
# 7. PATIENT ANALYTICS
# --------------------------------------------------

st.divider()

st.header("📊 Clinical Overview")

total_patients = len(patients)

children = sum(
    1 for p in patients
    if p["Category"] == "Children/Adolescents"
)

adults = sum(
    1 for p in patients
    if p["Category"] == "Adults"
)

older_adults = sum(
    1 for p in patients
    if p["Category"] == "Older Adults"
)

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Total Patients", total_patients)

with col2:
    st.metric("Children / Adolescents", children)

with col3:
    st.metric("Adults", adults)

with col4:
    st.metric("Older Adults", older_adults)


# --------------------------------------------------
# 8. PATIENT POPULATION CHART
# --------------------------------------------------

st.divider()

st.header("📈 Patient Population Analysis")

population_data = pd.DataFrame({
    "Age Group": [
        "Children",
        "Adults",
        "Older Adults"
    ],
    "Patients": [
        children,
        adults,
        older_adults
    ]
})

chart_col1, chart_col2 = st.columns(2)

with chart_col1:

    st.subheader("Age Group Distribution")

    st.bar_chart(
        population_data.set_index("Age Group"),
        color="#27CDBD"
    )

with chart_col2:

    st.subheader("Patient Gender Distribution")

    if patients:

        gender_counts = Counter(
            p["Gender"] for p in patients
        )

        gender_data = pd.DataFrame(
            list(gender_counts.items()),
            columns=["Gender", "Patients"]
        )

        st.bar_chart(
            gender_data.set_index("Gender"),
            color="#40A9E0"
        )

    else:

        st.info(
            "Register patients to view gender statistics."
        )


# --------------------------------------------------
# 9. DISEASE DATABASE
# --------------------------------------------------

disease_options = {

    "Infectious diseases": [
        "Malaria",
        "Tuberculosis",
        "HIV disease",
        "Pneumonia",
        "Cholera",
        "Hepatitis B",
        "Hepatitis C",
        "Influenza",
        "Dengue",
        "Ebola virus disease",
        "Other infectious disease"
    ],

    "Cardiovascular diseases": [
        "Hypertension",
        "Heart failure",
        "Coronary artery disease",
        "Stroke",
        "Other cardiovascular disease"
    ],

    "Respiratory diseases": [
        "Asthma",
        "Chronic obstructive pulmonary disease (COPD)",
        "Bronchitis",
        "Other respiratory disease"
    ],

    "Endocrine and metabolic diseases": [
        "Diabetes mellitus",
        "Obesity",
        "Thyroid disorder",
        "Other endocrine or metabolic disease"
    ],

    "Cancers": [
        "Breast cancer",
        "Cervical cancer",
        "Prostate cancer",
        "Lung cancer",
        "Colorectal cancer",
        "Other cancer"
    ],

    "Neurological diseases": [
        "Epilepsy",
        "Alzheimer disease",
        "Parkinson disease",
        "Migraine",
        "Other neurological disease"
    ],

    "Mental health conditions": [
        "Depressive disorder",
        "Anxiety disorder",
        "Bipolar disorder",
        "Schizophrenia",
        "Other mental health condition"
    ],

    "Digestive diseases": [
        "Gastritis",
        "Peptic ulcer disease",
        "Crohn disease",
        "Liver disease",
        "Other digestive disease"
    ],

    "Renal diseases": [
        "Chronic kidney disease",
        "Acute kidney injury",
        "Other renal disease"
    ],

    "Other / not yet classified": [
        "Other condition",
        "Diagnosis not yet established"
    ]
}


# --------------------------------------------------
# 10. PATIENT REGISTRATION
# --------------------------------------------------

st.divider()

st.header("🩺 Patient Registration")

st.caption(
    "Use fictional records while developing this prototype. "
    "Sensitive demographic fields are optional and self-reported."
)

with st.form("patient_form", border=True):

    full_name = st.text_input(
        "Patient Full Name",
        placeholder="Enter patient name"
    )

    col1, col2 = st.columns(2)

    with col1:

        age = st.number_input(
            "Patient Age",
            min_value=0,
            max_value=120,
            value=25
        )

    with col2:

        gender = st.selectbox(
            "Gender",
            [
                "Female",
                "Male",
                "Other",
                "Prefer not to say"
            ]
        )

    # DISEASE INFORMATION

    st.markdown("#### 🦠 Disease and Diagnosis")

    # WHO ICD-11 DISEASE SEARCH

    st.markdown("#### 🌍 WHO International Disease Classification")

    disease_search = st.text_input(
        "Search disease or diagnosis",
        placeholder="For example: Diabetes, Malaria, Tuberculosis..."
    )

    disease = ""
    disease_code = ""

    if disease_search:
        try:
            who_results = search_who_diseases(disease_search)

            if who_results:
                disease_labels = {}

                for item in who_results:
                    title = item.get("title", "Unknown condition")

                    if isinstance(title, dict):
                        title = title.get("@value", "Unknown condition")

                    if isinstance(title, str):
                        import re
                        title = re.sub(r"<[^>]+>", "", title)

                    code = item.get("theCode", "No code")

                    label = f"{title} (ICD-11: {code})"
                    disease_labels[label] = item

                selected_disease = st.selectbox(
                    "Select the correct WHO diagnosis",
                    list(disease_labels.keys())
                )

                selected_item = disease_labels[selected_disease]

                disease = selected_item.get("title", "")
                disease_code = selected_item.get("theCode", "")

            else:
                st.warning(
                    "No matching WHO diagnosis found. "
                    "Try another search term."
                )

        except Exception as e:
            st.error(f"WHO disease search failed: {e}")

    diagnosis_status = st.selectbox(
        "Diagnosis Status",
        [
            "Confirmed",
            "Suspected",
            "Under investigation",
            "Historical"
        ]
    )

    # LOCATION INFORMATION

    st.markdown("#### 🌍 Location and Nationality")

    col3, col4 = st.columns(2)

    with col3:

        country_residence = st.text_input(
            "Country of Residence",
            placeholder="e.g. Kenya"
        )

        city_residence = st.text_input(
            "City of Residence",
            placeholder="e.g. Nairobi"
        )

        country_birth = st.text_input(
            "Country of Birth",
            placeholder="e.g. Kenya"
        )

    with col4:

        city_birth = st.text_input(
            "City of Birth",
            placeholder="e.g. Kisumu"
        )

        nationality = st.text_input(
            "Nationality",
            placeholder="e.g. Kenyan"
        )

    # OPTIONAL DEMOGRAPHICS

    st.markdown("#### 👥 Optional Demographic Information")

    race = st.selectbox(
        "Race (self-reported)",
        [
            "Prefer not to say",
            "Black or African American",
            "White",
            "Asian",
            "American Indian or Alaska Native",
            "Native Hawaiian or Other Pacific Islander",
            "Mixed race",
            "Other"
        ]
    )

    religion = st.selectbox(
        "Religion (self-reported)",
        [
            "Prefer not to say",
            "Christian",
            "Muslim",
            "Hindu",
            "Buddhist",
            "Traditional / Indigenous beliefs",
            "Other"
        ]
    )

    submitted = st.form_submit_button(
        "➕ Register Patient",
        use_container_width=True
    )

    if submitted:

        if not full_name.strip():

            st.error(
                "Please enter the patient's full name."
            )

        else:

            if age < 18:
                category = "Children/Adolescents"

            elif age < 60:
                category = "Adults"

            else:
                category = "Older Adults"

            patient_id = (
                f"HIS-{st.session_state.next_patient_id:05d}"
            )

            patient_record = {

                "Patient ID": patient_id,
                "Full Name": full_name.strip(),
                "Age": int(age),
                "Gender": gender,
                "Category": category,

"Disease / Diagnosis": disease,
"ICD-11 Code": disease_code,
                "Diagnosis Status": diagnosis_status,

                "Country of Residence": country_residence.strip(),
                "City of Residence": city_residence.strip(),

                "Country of Birth": country_birth.strip(),
                "City of Birth": city_birth.strip(),

                "Nationality": nationality.strip(),

                "Race": race,
                "Religion": religion,

                "Registered At": datetime.now().strftime(
                    "%Y-%m-%d %H:%M:%S"
                )
            }

            st.session_state.patients.append(
                patient_record
            )

            st.session_state.next_patient_id += 1

            st.success(
                f"Patient {patient_id} registered successfully!"
            )

            st.rerun()


# --------------------------------------------------
# 11. REGISTERED PATIENT RECORDS
# --------------------------------------------------

st.divider()

st.header("📋 Registered Patient Records")

if patients:

    patient_df = pd.DataFrame(patients)

    st.dataframe(
        patient_df,
        use_container_width=True,
        hide_index=True
    )

    st.metric(
        "Total Registered Patients",
        len(patients)
    )

else:

    st.info(
        "No patients have been registered yet. "
        "Use the registration form above."
    )


# --------------------------------------------------
# 12. DISEASE ANALYTICS
# --------------------------------------------------

st.divider()

st.header("🦠 Disease Intelligence")

if patients:

    disease_records = [
        p.get("Disease / Diagnosis", "")
        for p in patients
        if p.get("Disease / Diagnosis")
    ]

    if disease_records:

        disease_counts = Counter(disease_records)

        disease_df = pd.DataFrame(
            disease_counts.items(),
            columns=["Disease", "Patients"]
        ).sort_values(
            "Patients",
            ascending=False
        )

        disease_col1, disease_col2 = st.columns(2)

        with disease_col1:

            st.subheader(
                "Most Frequently Recorded Diseases"
            )

            st.bar_chart(
                disease_df.set_index("Disease"),
                color="#27CDBD"
            )

        with disease_col2:

            st.subheader(
                "Disease Category Distribution"
            )

            category_records = [
                p.get("Disease Category", "")
                for p in patients
                if p.get("Disease Category")
            ]

            category_counts = Counter(category_records)

            category_df = pd.DataFrame(
                category_counts.items(),
                columns=["Disease Category", "Patients"]
            )

            st.bar_chart(
                category_df.set_index("Disease Category"),
                color="#40A9E0"
            )

    else:

        st.info(
            "Disease analytics will appear after diagnoses are recorded."
        )

else:

    st.info(
        "Register fictional test patients to view disease analytics."
    )


# --------------------------------------------------
# 13. REGISTRATION ACTIVITY
# --------------------------------------------------

st.divider()

st.header("📅 Patient Registration Activity")

if patients:

    registration_dates = Counter(
        p["Registered At"][:10]
        for p in patients
    )

    activity_df = pd.DataFrame(
        sorted(registration_dates.items()),
        columns=["Date", "Registrations"]
    )

    activity_df["Date"] = pd.to_datetime(
        activity_df["Date"]
    )

    st.line_chart(
        activity_df.set_index("Date"),
        color="#35D6C4"
    )

else:

    st.info(
        "Registration activity will appear here "
        "after patients are added."
    )


# --------------------------------------------------
# 14. FOOTER
# --------------------------------------------------

st.divider()

st.html("""
<div style="
    text-align: center;
    padding: 20px;
    color: #8BAFC0;
">

    <p>
        HEALTHCARE INTELLIGENCE SYSTEM
    </p>

    <p style="font-size: 12px;">
        Clinical Data • Patient Analytics • Digital Healthcare
    </p>

</div>
""")