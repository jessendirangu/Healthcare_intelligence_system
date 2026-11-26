# Healthcare Intelligence System

**A free, bilingual (English and Kiswahili) community health platform that helps people in Kenya detect, understand and manage chronic conditions early, starting with high blood pressure.**

🌐 **Live app:** https://jesse-healthcare.streamlit.app

Built by **Jesse Kigo Ndirangu, RN**, a Registered Nurse (Nursing Council of Kenya) with experience in emergency care, triage, outpatient and maternal and child health, now moving into AI and data science.

---

## Why this exists

High blood pressure usually has no symptoms. In Kenya, more than half of adults surveyed in 2015 had never had their blood pressure measured (Kenya STEPwise Survey), and only about 16% of people with hypertension knew they had it (Mohamed et al., *BMC Public Health*, 2018). Worldwide, WHO estimates that about 600 million people with hypertension are unaware of it.

As a nurse, I met many patients whose first sign was a stroke, heart failure or kidney damage. High blood pressure is easy to measure and cheap to treat: what is missing is **awareness and follow-up**. This platform aims to close that gap, in the language people speak, on the phones they already have, and through the community health system Kenya already has.

---

## What it does

The app opens on a simple **home screen of 9 icons**, with an emergency button at the top.

| Tool | What it does | Needs equipment? |
|---|---|---|
| 🚨 **Danger signs** | "Do we need to go to hospital?" for adults (FAST stroke signs, heart attack), pregnancy and after birth, sick children (WHO IMCI) and newborns. Gives *Emergency now / Clinic today / Watch at home*, first aid while getting help, and emergency numbers. | No |
| 🤔 **Am I at risk?** | Type 2 diabetes risk using the validated **FINDRISC** score (waist can be measured with a string), plus blood pressure check advice. Answers are not saved. | No |
| ✋ **Measure by hand** | Pulse (30-second timer), a child's breathing rate (WHO fast-breathing cut-offs, with an animated practice baby) and children's mid-upper arm circumference (MUAC) for malnutrition. | No (a string or MUAC tape) |
| 🩺 **My health tracker** | Record blood pressure, pulse, weight and blood sugar. Advice follows the ISH 2020 blood pressure categories and WHO sugar cut-offs, with 7/30/90-day trends. | BP cuff / glucometer |
| 🔥 **Healthy habits** | Daily challenge with streaks, Kenyan food guide (healthy plate, less salt), myth-or-fact quiz, and medicine or BP reminders added to the phone's own calendar. | No |
| 📚 **Learn** | Health education for 8 common conditions in Kenya (malaria, TB, HIV, hypertension, diabetes, pneumonia, asthma, cholera) in **English and Kiswahili**, with a 🔊 read-aloud option, plus live search of WHO ICD-11 and MedlinePlus. | No |
| 🤖 **AI risk** | Machine-learning estimates of diabetes and heart disease risk (logistic regression, scikit-learn), with explanations of what drives each estimate. | Lab values |
| 🏘️ **CHP mode** | For Community Health Promoters: register households (with verbal consent), record readings on home visits with one shared BP machine, refer to a facility and follow up. Tracks **linkage to care**. | One BP cuff per CHP |
| 📋 **Patients** | Practice patient registration with WHO ICD-11 diagnosis coding and clinical analytics (fictional data only). | No |

**Accessibility:** every screen is in English and Kiswahili. Demonstrations are animated and read aloud by the phone in the chosen language, and the app shows each visitor's local date and time.

### Admin and research dashboard

A separate, admin-only website provides:
- analytics on diagnoses, vital signs and users
- home blood pressure control across users, with an **anonymised research export**
- CHP approvals and the **referral completion rate (linkage to care)**
- anonymous "Was this page helpful?" feedback

---

## Privacy and safety

- **Data minimisation:** no ID or passport numbers, no GPS location. Risk check and danger sign answers are never saved.
- **Accounts:** passwords stored only as salted PBKDF2 hashes. Email verification by link or 6-digit code, codes at every sign-in, optional "remember this device" for 30 days, and **automatic sign-out after 5 minutes** without activity.
- **Each person sees only their own data.** A CHP sees only the households they registered. Admin access is limited to emails listed in the secrets.
- **User rights (Kenya Data Protection Act 2019):** a privacy notice in both languages, **download my data**, and **delete my account**, which removes all linked data.
- **Clinical safety:** the app gives general guidance and never diagnoses. Advice follows WHO, ISH and IMCI guidance, and when in doubt it always recommends seeing a health worker.

> ⚠️ This is a project in development, for education and self-monitoring support. It is not a medical device and does not replace a health worker.

---

## Technology

- **Python** and **Streamlit** (web app), **pandas**, **Altair** (charts)
- **Supabase** (PostgreSQL with row-level security) for storage, with a local SQLite fallback for development
- **scikit-learn** for the risk models (`train_model.py`)
- **WHO ICD-11 API** and **MedlinePlus** web service for disease information
- Browser **speech synthesis** for read-aloud demonstrations, SVG animations
- Gmail SMTP for verification emails, **phonenumbers** and **pycountry** for international phone numbers

### Project structure

| File | Purpose |
|---|---|
| `app.py` | Main public website and page routing |
| `admin_app.py` | Admin and research dashboard (separate website) |
| `home.py` | Home screen icon grid and navigation |
| `auth.py` | Accounts, email verification, remembered devices, auto sign-out |
| `i18n.py` | English / Kiswahili text and local time |
| `intro.py` | Welcome page: vision, mission, facts and stories |
| `tracker.py` | My health tracker |
| `danger_signs.py`, `measure.py`, `risk_check.py` | No-equipment tools |
| `habits.py` | Healthy habits, food guide, quiz, calendar reminders |
| `health_education.py`, `health_education_sw.py` | Disease guides in both languages |
| `chp.py`, `chp_store.py` | CHP mode and its storage |
| `demo.py` | Narrated animated demonstrations and timers |
| `account.py`, `feedback.py` | Privacy, data export and deletion; feedback |
| `risk_pages.py`, `train_model.py` | AI risk models |
| `storage.py`, `themes.py` | Data storage and colour themes |
| `supabase_setup.sql` | Database tables (run once in Supabase) |

---

## Running it yourself

```bash
pip install -r requirements.txt
python -m streamlit run app.py          # public site: http://localhost:8501
python -m streamlit run admin_app.py --server.port 8502   # admin site
```

Create `.streamlit/secrets.toml` (never commit this file):

```toml
WHO_CLIENT_ID = "..."          # from https://icd.who.int/icdapi
WHO_CLIENT_SECRET = "..."
SUPABASE_URL = "https://your-project.supabase.co"
SUPABASE_KEY = "sb_secret_..." # server-side secret key
ADMIN_EMAILS = ["you@example.com"]
SMTP_USER = "your.app@gmail.com"
SMTP_PASSWORD = "your 16-letter app password"
APP_URL = "https://your-app.streamlit.app"
```

Run `supabase_setup.sql` once in the Supabase SQL Editor. Without Supabase settings the app uses local SQLite files. Without email settings, verification codes are printed in the terminal (test mode).

---

## Roadmap

- Pilot with Community Health Promoters and measure blood pressure control and linkage to care
- Train and validate risk models on **Kenyan data** (Kenya STEPS / DHS)
- Short demonstration videos in English and Kiswahili
- SMS / WhatsApp reminders for people without smartphones
- Registration with Kenya's Office of the Data Protection Commissioner

---

## Sources

- WHO, *Hypertension* fact sheet (2025)
- Kenya Ministry of Health, *Kenya STEPwise Survey for NCD Risk Factors* (2015)
- Mohamed SF et al., *Prevalence, awareness, treatment and control of hypertension in Kenya*, BMC Public Health (2018)
- Unger T et al., *2020 International Society of Hypertension Global Hypertension Practice Guidelines*
- Lindström J, Tuomilehto J, *The Diabetes Risk Score*, Diabetes Care (2003)
- WHO, *Integrated Management of Childhood Illness (IMCI)* chart booklet
- WHO and UNICEF, *Child growth standards and the identification of severe acute malnutrition* (2009)
- WHO, *Salt reduction* fact sheet

---

© 2026 Jesse Kigo Ndirangu · Contact: healthintelligence.ke@gmail.com