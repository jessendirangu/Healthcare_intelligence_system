"""Diabetes risk page: a machine learning demonstration."""

import pandas as pd
import streamlit as st

from train_model import FEATURES, train

FRIENDLY_NAMES = {
    "Pregnancies": "Number of pregnancies",
    "Glucose": "Blood glucose",
    "BloodPressure": "Diastolic blood pressure",
    "BMI": "Body mass index (BMI)",
    "Age": "Age",
}


@st.cache_resource(show_spinner="Training the model...")
def get_model():
    # Trained once when the app starts, then reused for every prediction
    return train()


def explain(model, patient):
    """How much each measurement pushed this patient's risk up or down."""
    filled = model.named_steps["fill_missing"].transform(patient)
    scaled = model.named_steps["scale"].transform(filled)
    weights = model.named_steps["classify"].coef_[0]
    effects = scaled[0] * weights
    return sorted(zip(FEATURES, effects), key=lambda item: abs(item[1]), reverse=True)


def render():
    st.header("Diabetes risk prediction (machine learning)")
    st.warning(
        "**Learning demonstration, not a diagnostic tool.** The model was trained on "
        "768 women of Pima Indian heritage in the USA. It has not been tested on "
        "Kenyan patients, men or children. Diabetes is diagnosed with a fasting "
        "glucose, HbA1c or glucose tolerance test interpreted by a clinician."
    )

    try:
        model, metrics = get_model()
    except Exception as error:
        st.error(f"The model could not be trained: {error}")
        return

    with st.form("risk_form"):
        c1, c2, c3 = st.columns(3)
        age = c1.number_input("Age (years)", 18, 100, 40)
        sex = c2.selectbox("Sex", ["Female", "Male"])
        pregnancies = c3.number_input(
            "Number of pregnancies", 0, 20, 0, help="Enter 0 for men."
        )

        c4, c5, c6 = st.columns(3)
        glucose = c4.number_input(
            "Blood glucose (mmol/L)", 2.0, 35.0, 6.0, step=0.1,
            help="The model learned from glucose taken 2 hours after a glucose "
                 "drink (OGTT). Fasting or random results give a rougher estimate.",
        )
        diastolic = c5.number_input("Diastolic BP (mmHg)", 30, 140, 80)
        weight = c6.number_input("Weight (kg)", 20.0, 250.0, 70.0, step=0.5)
        height = st.number_input("Height (cm)", 100.0, 220.0, 165.0, step=0.5)

        submitted = st.form_submit_button("Predict risk", width="stretch")

    if not submitted:
        return

    bmi = weight / (height / 100) ** 2
    patient = pd.DataFrame([{
        "Pregnancies": pregnancies if sex == "Female" else 0,
        "Glucose": glucose * 18,  # model uses mg/dL; 1 mmol/L = 18 mg/dL
        "BloodPressure": diastolic,
        "BMI": bmi,
        "Age": age,
    }])[FEATURES]

    risk = model.predict_proba(patient)[0, 1]

    if risk < 0.2:
        level, show = "Low", st.success
    elif risk < 0.5:
        level, show = "Moderate", st.warning
    else:
        level, show = "High", st.error

    m1, m2 = st.columns(2)
    m1.metric("Estimated risk", f"{risk:.0%}")
    m2.metric("BMI", f"{bmi:.1f}")
    show(f"**{level} risk** according to this model.")

    st.subheader("What influenced this result")
    for feature, effect in explain(model, patient):
        direction = "raised" if effect > 0 else "lowered"
        st.write(f"- **{FRIENDLY_NAMES[feature]}** {direction} the risk")

    st.subheader("Suggested next step")
    if level == "High":
        st.write("Refer for a confirmatory test (fasting glucose or HbA1c) and clinical review.")
    elif level == "Moderate":
        st.write("Advise on healthy eating and activity, and consider a screening test.")
    else:
        st.write("Encourage a healthy lifestyle and routine screening as per guidelines.")

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
            "AUC: how well the model separates people with and without diabetes "
            "(0.5 = guessing, 1.0 = perfect). "
            "Sensitivity: share of people with diabetes that the model flagged."
        )