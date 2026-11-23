"""AI risk prediction pages (machine learning demonstrations)."""

import pandas as pd
import streamlit as st

from train_model import (
    DIABETES_FEATURES, HEART_FEATURES, explain, train_diabetes, train_heart,
)


@st.cache_resource(show_spinner="Training the diabetes model...")
def diabetes_model():
    return train_diabetes()


@st.cache_resource(show_spinner="Training the heart disease model...")
def heart_model():
    return train_heart()


# ---------------------------------------------------------------
# Shared display helpers
# ---------------------------------------------------------------

def show_result(risk, extra_metric=None):
    if risk < 0.2:
        level, box = "Low", st.success
    elif risk < 0.5:
        level, box = "Moderate", st.warning
    else:
        level, box = "High", st.error

    cols = st.columns(2)
    cols[0].metric("Estimated risk", f"{risk:.0%}")
    if extra_metric:
        cols[1].metric(*extra_metric)
    box(f"**{level} risk** according to this model.")
    return level


def show_factors(model, patient, names):
    st.subheader("What influenced this result")
    for feature, effect in explain(model, patient):
        if abs(effect) < 0.05:
            continue  # too small to matter
        direction = "raised" if effect > 0 else "lowered"
        st.write(f"- **{names[feature]}** {direction} the risk")


def show_quality(metrics):
    with st.expander("How good is this model?"):
        st.write(
            f"Trained on {metrics['n_train']} patients and tested on "
            f"{metrics['n_test']} patients it had never seen."
        )
        a, b, c = st.columns(3)
        a.metric("Accuracy", f"{metrics['accuracy']:.0%}")
        b.metric("AUC", f"{metrics['auc']:.2f}")
        c.metric("Sensitivity", f"{metrics['sensitivity']:.0%}")
        st.caption(
            "Accuracy: share of test patients classified correctly. "
            "AUC: how well the model separates sick from not sick "
            "(0.5 = guessing, 1.0 = perfect). "
            "Sensitivity: share of sick patients that the model flagged."
        )


def load(trainer):
    try:
        return trainer()
    except Exception as error:
        st.error(f"The model could not be trained: {error}")
        return None, None


# ---------------------------------------------------------------
# Diabetes
# ---------------------------------------------------------------

DIABETES_NAMES = {
    "Pregnancies": "Number of pregnancies",
    "Glucose": "Blood glucose",
    "BloodPressure": "Diastolic blood pressure",
    "BMI": "Body mass index (BMI)",
    "Age": "Age",
}


def render_diabetes():
    st.header("Diabetes risk prediction (machine learning)")
    st.warning(
        "**Learning demonstration, not a diagnostic tool.** Trained on 768 women of "
        "Pima Indian heritage in the USA. Not tested on Kenyan patients, men or "
        "children. Diabetes is diagnosed with fasting glucose, HbA1c or a glucose "
        "tolerance test interpreted by a clinician."
    )
    model, metrics = load(diabetes_model)
    if model is None:
        return

    with st.form("diabetes_form"):
        c1, c2, c3 = st.columns(3)
        age = c1.number_input("Age (years)", 18, 100, 40)
        sex = c2.selectbox("Sex", ["Female", "Male"])
        pregnancies = c3.number_input("Number of pregnancies", 0, 20, 0, help="0 for men.")

        c4, c5, c6, c7 = st.columns(4)
        glucose = c4.number_input(
            "Blood glucose (mmol/L)", 2.0, 35.0, 6.0, step=0.1,
            help="The model learned from glucose 2 hours after a glucose drink (OGTT). "
                 "Fasting or random results give a rougher estimate.",
        )
        diastolic = c5.number_input("Diastolic BP (mmHg)", 30, 140, 80)
        weight = c6.number_input("Weight (kg)", 20.0, 250.0, 70.0, step=0.5)
        height = c7.number_input("Height (cm)", 100.0, 220.0, 165.0, step=0.5)
        submitted = st.form_submit_button("Predict risk", width="stretch")

    if submitted:
        bmi = weight / (height / 100) ** 2
        patient = pd.DataFrame([{
            "Pregnancies": pregnancies if sex == "Female" else 0,
            "Glucose": glucose * 18,  # model uses mg/dL
            "BloodPressure": diastolic,
            "BMI": bmi,
            "Age": age,
        }])[DIABETES_FEATURES]

        level = show_result(model.predict_proba(patient)[0, 1], ("BMI", f"{bmi:.1f}"))
        show_factors(model, patient, DIABETES_NAMES)

        st.subheader("Suggested next step")
        st.write({
            "High": "Refer for a confirmatory test (fasting glucose or HbA1c) and clinical review.",
            "Moderate": "Advise on healthy eating and activity, and consider a screening test.",
            "Low": "Encourage a healthy lifestyle and routine screening as per guidelines.",
        }[level])

    show_quality(metrics)


# ---------------------------------------------------------------
# Heart disease
# ---------------------------------------------------------------

HEART_NAMES = {
    "Age": "Age",
    "Sex": "Sex",
    "ChestPain": "Type of chest pain",
    "RestingBP": "Systolic blood pressure",
    "Cholesterol": "Cholesterol",
    "FastingBS": "Fasting blood sugar",
    "ExerciseAngina": "Chest pain on exertion",
}

CHEST_PAIN = {
    "Typical angina (pressure-like, on exertion, relieved by rest)": 1,
    "Atypical angina (has some, not all, of those features)": 2,
    "Non-cardiac type chest pain": 3,
    "No chest pain": 4,
}


def render_heart():
    st.header("Heart disease risk prediction (machine learning)")
    st.warning(
        "**Learning demonstration, not a diagnostic tool.** Trained on 303 patients in "
        "the USA who were already referred for heart tests, so it overestimates risk "
        "in the general population. Not tested on Kenyan patients. Chest pain can be "
        "an emergency: anyone with severe or ongoing chest pain needs urgent care."
    )
    model, metrics = load(heart_model)
    if model is None:
        return

    with st.form("heart_form"):
        c1, c2, c3 = st.columns(3)
        age = c1.number_input("Age (years)", 18, 100, 50)
        sex = c2.selectbox("Sex", ["Female", "Male"])
        systolic = c3.number_input("Systolic BP (mmHg)", 70, 250, 130)

        pain = st.selectbox("Type of chest pain", list(CHEST_PAIN))

        c4, c5, c6 = st.columns(3)
        cholesterol = c4.number_input("Total cholesterol (mmol/L)", 2.0, 15.0, 5.2, step=0.1)
        sugar = c5.selectbox("Fasting blood sugar above 6.7 mmol/L?", ["No", "Yes", "Not known"])
        exertion = c6.selectbox("Chest pain brought on by exertion?", ["No", "Yes"])
        submitted = st.form_submit_button("Predict risk", width="stretch")

    if submitted:
        patient = pd.DataFrame([{
            "Age": age,
            "Sex": 1 if sex == "Male" else 0,
            "RestingBP": systolic,
            "Cholesterol": cholesterol * 38.67,  # model uses mg/dL
            "FastingBS": {"Yes": 1, "No": 0, "Not known": None}[sugar],
            "ExerciseAngina": 1 if exertion == "Yes" else 0,
            "ChestPain": CHEST_PAIN[pain],
        }])[HEART_FEATURES]

        level = show_result(model.predict_proba(patient)[0, 1])
        show_factors(model, patient, HEART_NAMES)

        st.subheader("Suggested next step")
        st.write({
            "High": "Refer for clinical review, ECG and further cardiac assessment.",
            "Moderate": "Review blood pressure, cholesterol and lifestyle; consider referral.",
            "Low": "Encourage a heart-healthy lifestyle and regular blood pressure checks.",
        }[level])

    show_quality(metrics)