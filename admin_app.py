"""Admin website: analytics across ALL users and patients.

Run it separately from the public app:
    python -m streamlit run admin_app.py

Only emails listed in ADMIN_EMAILS (in secrets) can get in.
"""

import re
from collections import Counter

import pandas as pd
import streamlit as st

import auth
from storage import load_patients

st.set_page_config(page_title="HIS Admin", page_icon="📊", layout="wide")

ACCENT = "#2F7D6D"
AGE_ORDER = ["Children/Adolescents", "Adults", "Older Adults"]


# ---------------------------------------------------------------
# Admin-only access
# ---------------------------------------------------------------

if not st.session_state.get("user"):
    _, middle, _ = st.columns([1, 2, 1])
    with middle:
        st.title("📊 Admin sign in")
        st.caption("Healthcare Intelligence System: administrators only.")
        auth.sign_in_form()
    st.stop()

if not auth.is_admin():
    st.error("Access denied. This account is not an administrator.")
    if st.button("Sign out"):
        st.session_state.pop("user")
        st.rerun()
    st.stop()

st.sidebar.markdown("### 📊 HIS Admin")
auth.sidebar_account()


# ---------------------------------------------------------------
# Load everything
# ---------------------------------------------------------------

users = pd.DataFrame(auth.list_users())
patients = pd.DataFrame(load_patients())

st.title("Admin analytics")
st.caption("All users and all patient records across the Healthcare Intelligence System.")

if patients.empty:
    st.info("No patient records yet. Analytics will appear once users add patients.")
else:
    patients["Registered At"] = pd.to_datetime(patients["Registered At"], errors="coerce")
    patients["Disease / Diagnosis"] = patients["Disease / Diagnosis"].fillna("").replace("", "Not recorded")


# ---------------------------------------------------------------
# Filters
# ---------------------------------------------------------------

filtered = patients.copy()
if not patients.empty:
    st.sidebar.header("Filters")

    dates = patients["Registered At"].dropna()
    if not dates.empty:
        chosen = st.sidebar.date_input(
            "Registered between", (dates.min().date(), dates.max().date())
        )
        # While picking, only a start date may be chosen yet
        if isinstance(chosen, (tuple, list)) and len(chosen) == 2:
            filtered = filtered[filtered["Registered At"].dt.date.between(*chosen)]

    def pick(label, column):
        global filtered
        if column in patients:
            options = sorted(patients[column].dropna().astype(str).unique())
            chosen = st.sidebar.multiselect(label, options)
            if chosen:
                filtered = filtered[filtered[column].astype(str).isin(chosen)]

    pick("Diagnosis", "Disease / Diagnosis")
    pick("Age group", "Category")
    pick("Gender", "Gender")
    pick("Country of residence", "Country of Residence")
    pick("Registered by (user)", "Owner")

    st.sidebar.caption(f"Showing {len(filtered)} of {len(patients)} patients")


# ---------------------------------------------------------------
# Key numbers
# ---------------------------------------------------------------

k1, k2, k3, k4, k5 = st.columns(5)
k1.metric("Registered users", len(users))
k2.metric("Patients", len(filtered))
if not filtered.empty:
    k3.metric("Average age", f"{filtered['Age'].mean():.0f}")
    with_alerts = filtered["Alerts"].fillna("").astype(str).str.len().gt(0).mean() if "Alerts" in filtered else 0
    k4.metric("With abnormal vitals", f"{with_alerts:.0%}")
    top = filtered.loc[filtered["Disease / Diagnosis"] != "Not recorded", "Disease / Diagnosis"]
    k5.metric("Most common diagnosis", top.mode().iloc[0] if not top.empty else "–")

tab_overview, tab_disease, tab_vitals, tab_users, tab_data = st.tabs(
    ["Overview", "Diseases", "Vital signs", "Users", "Data"]
)


def counts(column, order=None):
    data = filtered[column].fillna("Not recorded").astype(str).value_counts()
    if order:
        data = data.reindex([o for o in order if o in data.index])
    return data.rename("Patients")


# ---------------------------------------------------------------
# Overview
# ---------------------------------------------------------------

with tab_overview:
    if filtered.empty:
        st.info("No patients match the current filters.")
    else:
        c1, c2 = st.columns(2)
        with c1:
            st.subheader("Patients by age group")
            st.bar_chart(counts("Category", AGE_ORDER), color=ACCENT)
        with c2:
            st.subheader("Patients by gender")
            st.bar_chart(counts("Gender"), color="#6B8FA3")

        c3, c4 = st.columns(2)
        with c3:
            st.subheader("Registrations per week")
            weekly = filtered.set_index("Registered At").resample("W")["Patient ID"].count()
            st.line_chart(weekly.rename("Patients"), color=ACCENT)
        with c4:
            st.subheader("Patients by country of residence")
            st.bar_chart(counts("Country of Residence").head(10), color="#6B8FA3", horizontal=True)

        if "City of Residence" in filtered:
            st.subheader("Top cities / towns")
            cities = filtered["City of Residence"].fillna("").replace("", None).dropna()
            if not cities.empty:
                st.bar_chart(cities.str.title().value_counts().head(10).rename("Patients"),
                             color=ACCENT, horizontal=True)


# ---------------------------------------------------------------
# Diseases
# ---------------------------------------------------------------

with tab_disease:
    if filtered.empty:
        st.info("No patients match the current filters.")
    else:
        st.subheader("Most common diagnoses")
        st.bar_chart(counts("Disease / Diagnosis").head(15), color=ACCENT, horizontal=True)

        c1, c2 = st.columns(2)
        with c1:
            st.subheader("Diagnosis status")
            st.bar_chart(counts("Diagnosis Status"), color="#6B8FA3")
        with c2:
            st.subheader("Average age per diagnosis")
            st.dataframe(
                filtered.groupby("Disease / Diagnosis")["Age"]
                .agg(Patients="count", Average_age="mean")
                .round(1).sort_values("Patients", ascending=False),
                width="stretch",
            )

        st.subheader("Diagnoses by age group")
        st.caption("Number of patients with each diagnosis in each age group.")
        table = pd.crosstab(filtered["Disease / Diagnosis"], filtered["Category"])
        table = table[[c for c in AGE_ORDER if c in table.columns]]
        st.dataframe(table, width="stretch")

        st.subheader("Diagnoses by gender")
        st.dataframe(pd.crosstab(filtered["Disease / Diagnosis"], filtered["Gender"]), width="stretch")


# ---------------------------------------------------------------
# Vital signs
# ---------------------------------------------------------------

with tab_vitals:
    if filtered.empty:
        st.info("No patients match the current filters.")
    else:
        if "BMI Class" in filtered:
            st.subheader("BMI classes")
            bmi = filtered["BMI Class"].fillna("").replace("", None).dropna()
            if not bmi.empty:
                st.bar_chart(bmi.value_counts().rename("Patients"), color=ACCENT)

        if "Alerts" in filtered:
            st.subheader("Most common abnormal vital signs")
            alerts = Counter(
                re.sub(r"\s*\(.*\)", "", item.strip())
                for cell in filtered["Alerts"].dropna().astype(str)
                for item in cell.split(";") if item.strip()
            )
            if alerts:
                st.bar_chart(pd.Series(alerts, name="Patients").sort_values(ascending=False),
                             color="#C8553D", horizontal=True)
            else:
                st.info("No abnormal vital signs recorded.")

        vitals = [c for c in ["Temperature (°C)", "Pulse (bpm)", "Respiratory rate (/min)",
                              "Systolic BP (mmHg)", "Diastolic BP (mmHg)", "SpO2 (%)", "BMI"]
                  if c in filtered]
        if vitals:
            st.subheader("Vital signs summary")
            summary = filtered[vitals].apply(pd.to_numeric, errors="coerce").describe().T
            summary = summary.rename(columns={"count": "Recorded", "mean": "Average",
                                              "min": "Lowest", "max": "Highest"})
            st.dataframe(summary[["Recorded", "Average", "Lowest", "Highest"]].round(1), width="stretch")


# ---------------------------------------------------------------
# Users
# ---------------------------------------------------------------

with tab_users:
    if users.empty:
        st.info("No users yet.")
    else:
        users["created_at"] = pd.to_datetime(users["created_at"], errors="coerce", utc=True)
        st.subheader("New users per week")
        st.line_chart(
            users.set_index("created_at").resample("W")["email"].count().rename("New users"),
            color=ACCENT,
        )
        if not patients.empty:
            per_user = patients["Owner"].value_counts().rename("Patients")
            users["Patients"] = users["email"].map(per_user).fillna(0).astype(int)
        st.subheader("All users")
        st.dataframe(users, width="stretch", hide_index=True)


# ---------------------------------------------------------------
# Data
# ---------------------------------------------------------------

with tab_data:
    if filtered.empty:
        st.info("No patients match the current filters.")
    else:
        cols = ["Owner"] + [c for c in filtered.columns if c != "Owner"]
        st.dataframe(filtered[cols], width="stretch", hide_index=True)
        st.download_button(
            "Download filtered data (CSV)",
            filtered[cols].to_csv(index=False).encode("utf-8"),
            file_name="his_patients_filtered.csv", mime="text/csv",
        )

st.divider()
st.caption("HIS Admin · Contains personal data: keep this site and any downloads private.")