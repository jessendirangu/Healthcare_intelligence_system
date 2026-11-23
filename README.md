# Healthcare Intelligence System

A Streamlit web app for registering patients and exploring basic clinical analytics. Diagnoses are coded using the WHO ICD-11 classification.

I built this while moving from nursing into AI and data science. It draws on my clinical experience in emergency care and triage.

> **Prototype only.** Use fictional patient data. This app is not a medical device and must not be used for real clinical decisions.

## Features

- **Patient registration**: demographics, location and optional self-reported details
- **WHO ICD-11 diagnosis search**: live lookup of diagnoses and codes through the WHO ICD API, with a local fallback list if the API can't be reached
- **Vital signs**: temperature, pulse, respiratory rate, blood pressure, SpO2, weight and height
- **Automatic BMI**: calculated from weight and height and classified as underweight, normal, overweight or obese
- **Abnormal vitals alerts**: adult readings outside normal reference ranges are flagged, similar to a triage screen
- **Analytics dashboard**: patients by age group and gender, most recorded diagnoses, diagnosis status and registrations over time
- **Persistent storage**: patients are saved in a local SQLite database
- **CSV export** of all records

## Tech stack

Python · Streamlit · pandas · SQLite · WHO ICD-11 API

## Running it locally

1. Install the requirements:

   ```
   python -m pip install -r requirements.txt
   ```

2. Get free API credentials from the [WHO ICD API](https://icd.who.int/icdapi). Then create `.streamlit/secrets.toml`:

   ```toml
   WHO_CLIENT_ID = "your-client-id"
   WHO_CLIENT_SECRET = "your-client-secret"
   ```

   Without credentials, the app still works and uses the local diagnosis list.

3. Start the app:

   ```
   python -m streamlit run app.py
   ```

   It opens at http://localhost:8501.

## Project structure

```
app.py                  main application
requirements.txt        Python dependencies
.streamlit/config.toml  colour theme
.streamlit/secrets.toml WHO API keys (not committed)
patients.db             local database (created on first use, not committed)
```

## Notes on the clinical logic

- Vital sign alerts use general adult reference ranges (for example, pulse 60–100 bpm and SpO2 94–100%). Children are not flagged, because their normal ranges vary with age.
- Race and religion are optional and default to "Prefer not to say". This is sensitive personal data under Kenya's Data Protection Act 2019.

## Planned improvements

- Machine learning model to predict health risk (for example, diabetes) from patient data
- Search, edit and delete individual patients
- Staff login
- County-level map of cases in Kenya

## Author

Jesse Kigo Ndirangu, Registered Nurse (NCK), BSc (Hons) Nursing