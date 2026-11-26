"""My account and privacy.

- Privacy notice (English and Kiswahili), written for Kenya's Data Protection
  Act 2019: what is collected, why, where it is stored, for how long, and the
  user's rights (to be informed, access, correct, delete, object, complain).
- Download my data: everything stored about the account, as one JSON file.
- Delete my account: removes the account and all data linked to it, after the
  password is confirmed.
"""

import json
from datetime import datetime, timezone

import streamlit as st

import auth
import chp_store
import i18n
from i18n import t
from storage import delete_my_patients, delete_readings, load_patients, load_readings

CONTACT_EMAIL = "healthintelligence.ke@gmail.com"
LAST_UPDATED = {"en": "26 November 2026", "sw": "26 Novemba 2026"}

PRIVACY = {
    "en": f"""
**Last updated:** {LAST_UPDATED['en']}

**1. Who we are**
The Healthcare Intelligence System is a health education and self-monitoring website built and run by
Jesse Kigo Ndirangu, a Registered Nurse in Kenya. It is a project in development. Contact: **{CONTACT_EMAIL}**.

**2. What we collect**
- **Your account:** name, email, phone number and country. Your password is never stored, only a
  scrambled version (hash) that cannot be turned back into the password.
- **Health information you choose to enter:** blood pressure, pulse, weight, blood sugar, notes, and your
  daily healthy-habit ticks.
- **If you are a Community Health Promoter (CHP):** the households you register (head of household,
  village, optional phone), their members (name, sex, year of birth), their readings and referrals.
- **Remembered devices:** a random code that lets a device skip the email code. We store only its hash.
- **Feedback** ("Was this page helpful?"): stored anonymously, without your name or email.

**We do not collect:** ID or passport numbers, your GPS location (only your device's time zone is used,
to show the right time, and it is not saved), or your answers in *Am I at risk?* and *Danger signs*,
which are never saved.

**3. Why we use it**
Only to provide the features you use: your tracker, reminders, CHP follow-up and account security. We
may study **anonymised** statistics (no names, emails or phone numbers) to improve the service and for
health research. We **never sell** your data or use it for advertising.

**4. Your consent**
We process your data because you agreed when you created your account. You can withdraw your consent at
any time by deleting your account (below).

**5. Where your data is stored and who can see it**
Your data is stored with **Supabase** (servers in Ireland, European Union) and the website runs on
**Streamlit Community Cloud** (servers outside Kenya). Verification emails are sent through Gmail.
Data travels encrypted (HTTPS). By creating an account you consent to this storage outside Kenya.
- **You** can see your own data.
- **Your CHP** can see readings recorded during home visits for your household.
- **The administrator** can access data only to run and protect the service and to produce anonymised
  statistics.

**6. How long we keep it**
Until you delete your account. Email codes expire after 10 minutes, unconfirmed sign-ups after 24 hours,
and remembered devices after 30 days.

**7. Your rights (Data Protection Act 2019)**
You have the right to be informed, to **access** your data (use *Download my data*), to **correct** it,
to **delete** it (use *Delete my account*), and to **object** to its use. If you are unhappy with how
your data is handled, contact us first, or complain to the **Office of the Data Protection
Commissioner (ODPC)** at www.odpc.go.ke.

**8. Security**
Hashed passwords, email verification, automatic sign-out after 5 minutes without activity, and data
separated so each person sees only their own records.

**9. Children**
Accounts are for adults aged 18 and over. Information about children should only be entered by a parent,
guardian or CHP with the caregiver's permission.

**10. Not medical advice**
This website gives general guidance and does not diagnose. Always follow the advice of a health worker.
""",
    "sw": f"""
**Ilisasishwa:** {LAST_UPDATED['sw']}

**1. Sisi ni nani**
Healthcare Intelligence System ni tovuti ya elimu ya afya na kujifuatilia afya iliyotengenezwa na
kuendeshwa na Jesse Kigo Ndirangu, Muuguzi Aliyesajiliwa nchini Kenya. Ni mradi unaoendelea kuboreshwa.
Mawasiliano: **{CONTACT_EMAIL}**.

**2. Tunachokusanya**
- **Akaunti yako:** jina, barua pepe, nambari ya simu na nchi. Nenosiri lako halihifadhiwi kamwe, ni
  toleo lililochanganywa (hash) tu ambalo haliwezi kurudishwa kuwa nenosiri.
- **Taarifa za afya unazochagua kuweka:** shinikizo la damu, mapigo ya moyo, uzito, sukari, maelezo, na
  alama zako za tabia za afya za kila siku.
- **Ukiwa Mhudumu wa Afya ya Jamii (CHP):** kaya unazosajili (mkuu wa kaya, kijiji, simu si lazima),
  wanakaya (jina, jinsia, mwaka wa kuzaliwa), vipimo vyao na rufaa zao.
- **Vifaa vinavyokumbukwa:** namba ya nasibu inayoruhusu kifaa kuruka namba ya barua pepe. Tunahifadhi
  hash yake tu.
- **Maoni** ("Je, ukurasa huu umekusaidia?"): yanahifadhiwa bila jina, bila jina lako wala barua pepe.

**Hatukusanyi:** namba za kitambulisho au pasipoti, mahali ulipo kwa GPS (tunatumia tu saa za eneo la
kifaa chako kuonyesha saa sahihi, na haihifadhiwi), wala majibu yako ya *Niko hatarini?* na *Dalili za
hatari*, ambayo hayahifadhiwi kamwe.

**3. Kwa nini tunaitumia**
Ili tu kutoa huduma unazotumia: kifuatilia chako, vikumbusho, ufuatiliaji wa CHP na usalama wa akaunti.
Tunaweza kuchunguza takwimu **zisizo na majina** (bila majina, barua pepe wala simu) kuboresha huduma na
kwa utafiti wa afya. **Hatuuzi kamwe** data yako wala kuitumia kwa matangazo.

**4. Ridhaa yako**
Tunashughulikia data yako kwa sababu ulikubali ulipofungua akaunti. Unaweza kuondoa ridhaa yako wakati
wowote kwa kufuta akaunti yako (hapa chini).

**5. Data yako inahifadhiwa wapi na nani anaiona**
Data yako inahifadhiwa na **Supabase** (seva Ireland, Umoja wa Ulaya) na tovuti inaendeshwa kwenye
**Streamlit Community Cloud** (seva nje ya Kenya). Barua pepe za uthibitisho zinatumwa kupitia Gmail.
Data husafiri ikiwa imesimbwa (HTTPS). Kwa kufungua akaunti unakubali uhifadhi huu nje ya Kenya.
- **Wewe** unaweza kuona data yako.
- **CHP wako** anaweza kuona vipimo vilivyowekwa wakati wa kutembelea kaya yako.
- **Msimamizi** anaweza kufikia data ili tu kuendesha na kulinda huduma na kutengeneza takwimu zisizo na majina.

**6. Tunaihifadhi kwa muda gani**
Hadi utakapofuta akaunti yako. Namba za barua pepe huisha baada ya dakika 10, usajili usiothibitishwa
baada ya saa 24, na vifaa vinavyokumbukwa baada ya siku 30.

**7. Haki zako (Sheria ya Ulinzi wa Data 2019)**
Una haki ya kujulishwa, **kupata** data yako (tumia *Pakua data yangu*), **kuirekebisha**, **kuifuta**
(tumia *Futa akaunti yangu*), na **kupinga** matumizi yake. Kama huridhiki na jinsi data yako
inavyoshughulikiwa, wasiliana nasi kwanza, au toa malalamiko kwa **Ofisi ya Kamishna wa Ulinzi wa Data
(ODPC)** kupitia www.odpc.go.ke.

**8. Usalama**
Manenosiri yaliyochanganywa, uthibitisho wa barua pepe, kutolewa kiotomatiki baada ya dakika 5 bila
kutumia, na data iliyotenganishwa ili kila mtu aone rekodi zake tu.

**9. Watoto**
Akaunti ni kwa watu wazima wenye miaka 18 na zaidi. Taarifa za watoto ziwekwe tu na mzazi, mlezi au CHP
kwa ruhusa ya mlezi.

**10. Si ushauri wa kitabibu**
Tovuti hii inatoa mwongozo wa jumla na haitoi utambuzi wa ugonjwa. Daima fuata ushauri wa mhudumu wa afya.
""",
}

i18n.register({
    "page_account": {"en": "My account & privacy", "sw": "Akaunti yangu na faragha"},
    "ac_title": {"en": "My account & privacy", "sw": "Akaunti yangu na faragha"},
    "ac_tab_privacy": {"en": "🔒 Privacy notice", "sw": "🔒 Taarifa ya faragha"},
    "ac_tab_data": {"en": "📥 Download my data", "sw": "📥 Pakua data yangu"},
    "ac_tab_delete": {"en": "🗑️ Delete my account", "sw": "🗑️ Futa akaunti yangu"},
    "ac_privacy_title": {"en": "Privacy notice", "sw": "Taarifa ya faragha"},
    "ac_read_privacy": {"en": "Read the privacy notice", "sw": "Soma taarifa ya faragha"},
    "ac_data_intro": {
        "en": "Download a copy of everything we store about your account: your details, readings, "
              "habit check-ins, and any households you registered as a CHP.",
        "sw": "Pakua nakala ya kila kitu tunachohifadhi kuhusu akaunti yako: taarifa zako, vipimo, "
              "alama za tabia, na kaya zozote ulizosajili kama CHP.",
    },
    "ac_prepare": {"en": "Prepare my data", "sw": "Andaa data yangu"},
    "ac_download": {"en": "📥 Download (JSON file)", "sw": "📥 Pakua (faili ya JSON)"},
    "ac_correct": {
        "en": "To correct your name or phone number, email us at {email} from your registered email address.",
        "sw": "Kurekebisha jina au nambari ya simu, tutumie barua pepe {email} kutoka kwa barua pepe uliyosajili.",
    },
    "ac_delete_warn": {
        "en": "**This cannot be undone.** Your account and everything linked to it will be permanently "
              "deleted: your readings, habit check-ins, remembered devices, practice patient records, and "
              "any households, members and referrals you registered as a CHP. Download your data first if "
              "you want a copy.",
        "sw": "**Hili haliwezi kurudishwa.** Akaunti yako na kila kitu kilichounganishwa nayo kitafutwa "
              "kabisa: vipimo vyako, alama za tabia, vifaa vinavyokumbukwa, rekodi za wagonjwa za mazoezi, "
              "na kaya, wanakaya na rufaa zozote ulizosajili kama CHP. Pakua data yako kwanza kama unataka nakala.",
    },
    "ac_confirm_word": {"en": "DELETE", "sw": "FUTA"},
    "ac_type": {"en": "Type {word} to confirm", "sw": "Andika {word} kuthibitisha"},
    "ac_password": {"en": "Your password", "sw": "Nenosiri lako"},
    "ac_delete_btn": {"en": "Permanently delete my account", "sw": "Futa akaunti yangu kabisa"},
    "ac_wrong": {"en": "The confirmation word or password is not correct.",
                 "sw": "Neno la uthibitisho au nenosiri si sahihi."},
    "ac_deleted": {"en": "Your account and all its data have been deleted. Thank you for using the service.",
                   "sw": "Akaunti yako na data yake yote zimefutwa. Asante kwa kutumia huduma hii."},
    "ac_failed": {"en": "Something went wrong and not everything could be deleted. Please try again, or "
                        "email {email}.",
                  "sw": "Kuna tatizo na si kila kitu kimefutwa. Tafadhali jaribu tena, au tuma barua pepe {email}."},
})


def privacy_text():
    return PRIVACY["sw" if i18n.lang() == "sw" else "en"]


def export_data(email):
    """Everything stored for this account, as a JSON-ready dict (no password hash)."""
    user = auth.find_user("email", email) or {}
    member_rows = chp_store.members(email)
    member_ids = [m["id"] for m in member_rows]
    return {
        "exported_at": datetime.now(timezone.utc).isoformat(),
        "account": {k: user.get(k) for k in ("full_name", "email", "phone", "country", "created_at")},
        "readings": load_readings(email),
        "habit_check_ins": chp_store.habit_logs(email),
        "practice_patient_records": load_patients(owner=email),
        "chp": {
            "status": chp_store.chp_status(email),
            "households": chp_store.households(email),
            "members": member_rows,
            "member_readings": [r for mid in member_ids for r in load_readings(chp_store.member_owner(mid))],
            "referrals": chp_store.referrals(email),
        },
    }


def delete_account(email):
    """Delete the account and all linked data. Order matters for linked tables."""
    member_ids = chp_store.delete_everything_for(email)
    for member_id in member_ids:
        delete_readings(chp_store.member_owner(member_id))
    delete_readings(email)
    delete_my_patients(email)
    auth.delete_user(email)


def render(email):
    st.header(t("ac_title"))
    privacy, data, delete = st.tabs([t("ac_tab_privacy"), t("ac_tab_data"), t("ac_tab_delete")])

    with privacy:
        st.markdown(privacy_text())

    with data:
        st.write(t("ac_data_intro"))
        if st.button(t("ac_prepare"), key="ac_prepare_btn"):
            try:
                st.session_state.ac_export = json.dumps(export_data(email), indent=2, default=str)
            except Exception:
                st.error(t("db_unavailable"))
        if "ac_export" in st.session_state:
            st.download_button(t("ac_download"), st.session_state.ac_export.encode("utf-8"),
                               file_name="my_health_data.json", mime="application/json", type="primary")
        st.caption(t("ac_correct", email=CONTACT_EMAIL))

    with delete:
        st.warning(t("ac_delete_warn"))
        word = t("ac_confirm_word")
        with st.form("ac_delete_form"):
            typed = st.text_input(t("ac_type", word=word))
            password = st.text_input(t("ac_password"), type="password", autocomplete="current-password")
            go = st.form_submit_button(t("ac_delete_btn"), type="primary")
        if go:
            user = auth.find_user("email", email)
            if typed.strip().upper() != word or not user or not auth.check_password(password, user["password_hash"]):
                st.error(t("ac_wrong"))
                return
            try:
                delete_account(email)
            except Exception:
                st.error(t("ac_failed", email=CONTACT_EMAIL))
                return
            auth.forget_device(email)
            auth.sign_out()
            st.session_state.auth_flash = t("ac_deleted")
            st.rerun()