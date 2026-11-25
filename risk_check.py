"""Am I at risk? A check that needs no equipment.

Part 1 - Type 2 diabetes risk: the Finnish Diabetes Risk Score (FINDRISC),
Lindstrom & Tuomilehto, Diabetes Care 2003;26:725-31. Eight questions,
0-26 points, estimating the chance of developing type 2 diabetes in the
next 10 years. Waist can be measured with a piece of string; weight and
height are optional (if unknown, the BMI question scores 0 and the result
is shown as a minimum).

Part 2 - Blood pressure: advice on when to get it checked, based on the
WHO recommendation that adults know their blood pressure.

Note: FINDRISC was developed in Finland. It is widely used in many
countries, but it has not been fully validated in Kenyan populations, so
the result is a guide for who should get tested, not a diagnosis.
"""

import streamlit as st

import demo
import i18n
from i18n import t

i18n.register({
    "rk_title": {"en": "Am I at risk?", "sw": "Je, niko hatarini?"},
    "rk_intro": {
        "en": "No machine needed. Answer a few questions to find out your risk of type 2 diabetes "
              "and whether you should get your blood pressure checked. It takes about 2 minutes.",
        "sw": "Hakuna kifaa kinachohitajika. Jibu maswali machache ujue hatari yako ya kupata kisukari "
              "aina ya 2 na kama unapaswa kupima shinikizo la damu. Inachukua takriban dakika 2.",
    },
    "rk_part1": {"en": "Part 1: Diabetes risk", "sw": "Sehemu ya 1: Hatari ya kisukari"},
    "rk_sex": {"en": "Sex", "sw": "Jinsia"},
    "rk_male": {"en": "Male", "sw": "Mwanaume"},
    "rk_female": {"en": "Female", "sw": "Mwanamke"},
    "rk_age": {"en": "Age (years)", "sw": "Umri (miaka)"},
    "rk_waist": {"en": "Waist size (cm)", "sw": "Mzunguko wa kiuno (cm)"},
    "rk_waist_help": {
        "en": "Measure around your waist at the level of your belly button.",
        "sw": "Pima kuzunguka kiuno chako usawa wa kitovu.",
    },
    "rk_waist_unknown": {"en": "I can't measure my waist now", "sw": "Siwezi kupima kiuno sasa"},
    "rk_how_waist": {
        "en": "How to measure your waist with a piece of string",
        "sw": "Jinsi ya kupima kiuno kwa kamba",
    },
    "rk_how_waist_body": {
        "en": "1. Stand up straight and breathe out normally.\n"
              "2. Put a string or cloth tape around your waist at the level of your **belly button**, "
              "on bare skin or over thin clothing. Keep it straight, not tight.\n"
              "3. Hold the place where the string meets, then lay it flat.\n"
              "4. Measure the string with a ruler or tape measure. A school ruler is 30 cm, so "
              "count how many rulers long it is.\n"
              "5. Or ask a health worker, tailor (fundi) or pharmacy to measure it for you.",
        "sw": "1. Simama wima na upumue kawaida.\n"
              "2. Zungusha kamba au tepu ya kitambaa kiunoni usawa wa **kitovu**, kwenye ngozi au "
              "juu ya nguo nyepesi. Iwe sawa, isibane.\n"
              "3. Shika mahali kamba inapokutana, kisha uilaze chini.\n"
              "4. Pima kamba kwa rula au tepu. Rula ya shule ni cm 30, kwa hiyo hesabu ni rula "
              "ngapi.\n"
              "5. Au mwombe mhudumu wa afya, fundi cherehani au duka la dawa akupime.",
    },
    "rk_weight_known": {
        "en": "I know my weight and height",
        "sw": "Najua uzito na urefu wangu",
    },
    "rk_weight": {"en": "Weight (kg)", "sw": "Uzito (kg)"},
    "rk_height": {"en": "Height (cm)", "sw": "Urefu (cm)"},
    "rk_active": {
        "en": "Are you physically active for at least 30 minutes most days? "
              "(walking, farming, digging, carrying, sports or active work)",
        "sw": "Je, unafanya kazi ya kutumia nguvu angalau dakika 30 siku nyingi? "
              "(kutembea, kulima, kuchimba, kubeba, michezo au kazi ya nguvu)",
    },
    "rk_veg": {
        "en": "Do you eat vegetables or fruit every day? (e.g. sukuma, managu, cabbage, "
              "tomatoes, bananas, mangoes, oranges)",
        "sw": "Je, unakula mboga au matunda kila siku? (mf. sukuma, managu, kabichi, "
              "nyanya, ndizi, maembe, machungwa)",
    },
    "rk_bp_meds": {
        "en": "Have you ever taken medicine for high blood pressure regularly?",
        "sw": "Je, umewahi kumeza dawa ya shinikizo la juu la damu mara kwa mara?",
    },
    "rk_high_sugar": {
        "en": "Have you ever been told your blood sugar was high? (at a check-up, during an "
              "illness or during pregnancy)",
        "sw": "Je, umewahi kuambiwa sukari yako kwenye damu iko juu? (kwenye uchunguzi, ukiwa "
              "mgonjwa au ukiwa mjamzito)",
    },
    "rk_family": {
        "en": "Has anyone in your family had diabetes (type 1 or 2)?",
        "sw": "Je, kuna mtu katika familia yako aliyewahi kuwa na kisukari (aina ya 1 au 2)?",
    },
    "rk_fam_no": {"en": "No", "sw": "Hapana"},
    "rk_fam_far": {
        "en": "Yes: grandparent, aunt, uncle or cousin",
        "sw": "Ndiyo: babu/bibi, shangazi, mjomba, baba/mama mdogo au binamu",
    },
    "rk_fam_close": {
        "en": "Yes: parent, brother, sister or my child",
        "sw": "Ndiyo: mzazi, kaka, dada au mtoto wangu",
    },
    "yes": {"en": "Yes", "sw": "Ndiyo"},
    "no": {"en": "No", "sw": "Hapana"},

    "rk_part2": {"en": "Part 2: Blood pressure", "sw": "Sehemu ya 2: Shinikizo la damu"},
    "rk_last_bp": {
        "en": "When was your blood pressure last measured?",
        "sw": "Shinikizo lako la damu lilipimwa lini mara ya mwisho?",
    },
    "rk_bp_recent": {"en": "In the last 12 months", "sw": "Ndani ya miezi 12 iliyopita"},
    "rk_bp_old": {"en": "More than a year ago", "sw": "Zaidi ya mwaka mmoja uliopita"},
    "rk_bp_never": {"en": "Never / I don't know", "sw": "Sijawahi / Sijui"},
    "rk_bp_told_high": {
        "en": "Were you told it was high?",
        "sw": "Je, uliambiwa liko juu?",
    },
    "rk_submit": {"en": "See my result", "sw": "Ona matokeo yangu"},

    # Results
    "rk_result": {"en": "Your result", "sw": "Matokeo yako"},
    "rk_score": {"en": "Diabetes risk score", "sw": "Alama ya hatari ya kisukari"},
    "rk_score_min": {
        "en": "At least {score} of 26. Without your weight and height the score may be "
              "up to 3 points higher.",
        "sw": "Angalau {score} kati ya 26. Bila uzito na urefu wako, alama inaweza kuwa "
              "juu kwa hadi pointi 3.",
    },
    "rk_score_waist": {
        "en": "Without your waist size the score may be up to 4 points higher.",
        "sw": "Bila kipimo cha kiuno, alama inaweza kuwa juu kwa hadi pointi 4.",
    },
    "rk_cat_low": {"en": "Low risk", "sw": "Hatari ndogo"},
    "rk_cat_slight": {"en": "Slightly raised risk", "sw": "Hatari imeongezeka kidogo"},
    "rk_cat_moderate": {"en": "Moderate risk", "sw": "Hatari ya wastani"},
    "rk_cat_high": {"en": "High risk", "sw": "Hatari kubwa"},
    "rk_cat_very_high": {"en": "Very high risk", "sw": "Hatari kubwa sana"},
    "rk_chance": {
        "en": "Estimated chance of developing type 2 diabetes in the next 10 years: **about {chance}**.",
        "sw": "Uwezekano unaokadiriwa wa kupata kisukari aina ya 2 katika miaka 10 ijayo: "
              "**takriban {chance}**.",
    },
    "rk_c_low": {"en": "1 in 100 people", "sw": "mtu 1 kati ya 100"},
    "rk_c_slight": {"en": "1 in 25 people", "sw": "mtu 1 kati ya 25"},
    "rk_c_moderate": {"en": "1 in 6 people", "sw": "mtu 1 kati ya 6"},
    "rk_c_high": {"en": "1 in 3 people", "sw": "mtu 1 kati ya 3"},
    "rk_c_very_high": {"en": "1 in 2 people", "sw": "mtu 1 kati ya 2"},
    "rk_adv_low": {
        "en": "Keep up your healthy habits: stay active, eat vegetables every day and keep a "
              "healthy weight.",
        "sw": "Endelea na tabia zako nzuri: fanya mazoezi, kula mboga kila siku na dumisha uzito mzuri.",
    },
    "rk_adv_mid": {
        "en": "You can lower your risk: be active for 30 minutes a day, eat vegetables every day, "
              "cut down on sugar, soda and white bread, and lose some weight if you can. "
              "Ask for a blood sugar test at your next clinic visit.",
        "sw": "Unaweza kupunguza hatari yako: fanya mazoezi dakika 30 kwa siku, kula mboga kila "
              "siku, punguza sukari, soda na mkate mweupe, na upunguze uzito ukiweza. Omba kupimwa "
              "sukari utakapoenda kliniki tena.",
    },
    "rk_adv_high": {
        "en": "Please get your **blood sugar tested** at a health facility, pharmacy or community "
              "health outreach soon. Many people with diabetes don't know they have it. Lifestyle "
              "changes can prevent or delay diabetes, even at this level of risk.",
        "sw": "Tafadhali **pima sukari kwenye damu** katika kituo cha afya, duka la dawa au kambi ya "
              "afya ya jamii hivi karibuni. Watu wengi wenye kisukari hawajui kuwa wanacho. Kubadilisha "
              "mtindo wa maisha kunaweza kuzuia au kuchelewesha kisukari, hata katika kiwango hiki.",
    },
    "rk_change_title": {
        "en": "What you can change",
        "sw": "Unachoweza kubadilisha",
    },
    "rk_change_active": {
        "en": "Being active for 30 minutes a day would lower your score by 2 points.",
        "sw": "Kufanya mazoezi dakika 30 kwa siku kungepunguza alama yako kwa pointi 2.",
    },
    "rk_change_veg": {
        "en": "Eating vegetables or fruit every day would lower your score by 1 point.",
        "sw": "Kula mboga au matunda kila siku kungepunguza alama yako kwa pointi 1.",
    },
    "rk_change_waist": {
        "en": "Reducing your waist size (by losing weight) can lower your score by up to 4 points.",
        "sw": "Kupunguza mzunguko wa kiuno (kwa kupunguza uzito) kunaweza kupunguza alama yako kwa hadi pointi 4.",
    },
    "rk_change_none": {
        "en": "Your habits are already helping. Keep them up!",
        "sw": "Tabia zako tayari zinakusaidia. Endelea hivyo!",
    },
    "rk_bp_result": {"en": "Blood pressure", "sw": "Shinikizo la damu"},
    "rk_bp_adv_ok": {
        "en": "Good. Keep getting it checked at least once a year, even when you feel well.",
        "sw": "Vizuri. Endelea kupima angalau mara moja kwa mwaka, hata ukijisikia vizuri.",
    },
    "rk_bp_adv_due": {
        "en": "**Please get your blood pressure checked soon.** High blood pressure usually has no "
              "symptoms. A check is quick and often free at health facilities, pharmacies, "
              "community health volunteers (CHVs) and outreach camps.",
        "sw": "**Tafadhali pima shinikizo la damu hivi karibuni.** Shinikizo la juu mara nyingi halina "
              "dalili. Kupima ni haraka na mara nyingi ni bure katika vituo vya afya, maduka ya dawa, "
              "wahudumu wa afya wa jamii (CHV) na kambi za afya.",
    },
    "rk_bp_adv_high": {
        "en": "**You were told your blood pressure was high.** Please see a health worker to confirm "
              "it and discuss treatment. Once you have a reading, record it in *My health tracker*.",
        "sw": "**Uliambiwa shinikizo lako la damu liko juu.** Tafadhali muone mhudumu wa afya "
              "kuthibitisha na kuzungumzia matibabu. Ukipata kipimo, kiweke kwenye *Kifuatilia afya yangu*.",
    },
    "rk_bp_adv_risk": {
        "en": "Your answers also suggest a higher risk of high blood pressure (age, weight or family "
              "history), so a check is especially important for you.",
        "sw": "Majibu yako pia yanaonyesha hatari kubwa zaidi ya shinikizo la juu la damu (umri, "
              "uzito au historia ya familia), kwa hiyo kupima ni muhimu sana kwako.",
    },
    "rk_about": {
        "en": "About this check: the diabetes score is the Finnish Diabetes Risk Score (FINDRISC), "
              "a questionnaire used worldwide to find people who should be tested. It was developed "
              "in Finland and is not yet fully validated for Kenyan populations. It is a guide, "
              "not a diagnosis: only a blood test can show if you have diabetes. Your answers are "
              "not saved.",
        "sw": "Kuhusu kipimo hiki: alama ya kisukari ni Finnish Diabetes Risk Score (FINDRISC), dodoso "
              "linalotumika duniani kote kutambua watu wanaopaswa kupimwa. Lilitengenezwa Finland na "
              "bado halijathibitishwa kikamilifu kwa watu wa Kenya. Ni mwongozo, si utambuzi: kipimo "
              "cha damu pekee kinaweza kuonyesha kama una kisukari. Majibu yako hayahifadhiwi.",
    },
    "rk_under18": {
        "en": "This check is for adults aged 18 and over.",
        "sw": "Kipimo hiki ni kwa watu wazima wenye umri wa miaka 18 na zaidi.",
    },
})


# ---------------------------------------------------------------
# FINDRISC scoring (Lindstrom & Tuomilehto 2003)
# ---------------------------------------------------------------

def age_points(age):
    if age < 45:
        return 0
    if age < 55:
        return 2
    if age < 65:
        return 3
    return 4


def bmi_points(bmi):
    if bmi is None:
        return 0
    if bmi < 25:
        return 0
    if bmi <= 30:
        return 1
    return 3


def waist_points(waist_cm, sex):
    if waist_cm is None:
        return 0
    low, high = (94, 102) if sex == "male" else (80, 88)
    if waist_cm < low:
        return 0
    if waist_cm <= high:
        return 3
    return 4


FAMILY_POINTS = {"no": 0, "far": 3, "close": 5}


def findrisc(age, sex, waist_cm, bmi, active, vegetables, bp_meds, high_sugar, family):
    """Returns the total score (0-26) and the points for each question."""
    parts = {
        "age": age_points(age),
        "bmi": bmi_points(bmi),
        "waist": waist_points(waist_cm, sex),
        "active": 0 if active else 2,
        "veg": 0 if vegetables else 1,
        "bp_meds": 2 if bp_meds else 0,
        "high_sugar": 5 if high_sugar else 0,
        "family": FAMILY_POINTS[family],
    }
    return sum(parts.values()), parts


def risk_category(score):
    if score < 7:
        return "low"
    if score <= 11:
        return "slight"
    if score <= 14:
        return "moderate"
    if score <= 20:
        return "high"
    return "very_high"


BOX = {"low": st.success, "slight": st.info, "moderate": st.warning,
       "high": st.error, "very_high": st.error}


# ---------------------------------------------------------------
# Page
# ---------------------------------------------------------------

def _yes_no(label, key):
    return st.radio(label, ["no", "yes"], format_func=t, horizontal=True, key=key) == "yes"


def render():
    st.header(t("rk_title"))
    st.write(t("rk_intro"))

    st.subheader(t("rk_part1"))
    c1, c2 = st.columns(2)
    sex = c1.radio(t("rk_sex"), ["female", "male"], format_func=lambda s: t("rk_" + s),
                   horizontal=True, key="rk_sex_in")
    age = c2.number_input(t("rk_age"), 10, 110, value=None, key="rk_age_in")

    no_waist = st.checkbox(t("rk_waist_unknown"), key="rk_no_waist")
    waist = None
    if not no_waist:
        waist = st.number_input(t("rk_waist"), 40, 200, value=None, help=t("rk_waist_help"),
                                key="rk_waist_in")
    with st.expander(t("rk_how_waist")):
        demo.show("waist")
        st.markdown(t("rk_how_waist_body"))

    bmi = None
    if st.checkbox(t("rk_weight_known"), key="rk_bmi_known"):
        w1, w2 = st.columns(2)
        weight = w1.number_input(t("rk_weight"), 20.0, 300.0, value=None, step=0.5, key="rk_w")
        height = w2.number_input(t("rk_height"), 100.0, 230.0, value=None, step=0.5, key="rk_h")
        if weight and height:
            bmi = round(weight / (height / 100) ** 2, 1)
            st.caption(f"BMI: {bmi}")

    active = _yes_no(t("rk_active"), "rk_act")
    vegetables = _yes_no(t("rk_veg"), "rk_veg_in")
    bp_meds = _yes_no(t("rk_bp_meds"), "rk_bpm")
    high_sugar = _yes_no(t("rk_high_sugar"), "rk_hs")
    family = st.radio(t("rk_family"), ["no", "far", "close"],
                      format_func=lambda f: t("rk_fam_" + f), key="rk_fam")

    st.subheader(t("rk_part2"))
    last_bp = st.radio(t("rk_last_bp"), ["recent", "old", "never"],
                       format_func=lambda v: t("rk_bp_" + v), key="rk_lbp")
    told_high = False
    if last_bp != "never":
        told_high = _yes_no(t("rk_bp_told_high"), "rk_th")

    if not st.button(t("rk_submit"), type="primary", width="stretch"):
        st.caption(t("rk_about"))
        return
    if age is None or age < 18:
        st.warning(t("rk_under18"))
        return

    score, parts = findrisc(age, sex, waist, bmi, active, vegetables, bp_meds, high_sugar, family)
    category = risk_category(score)

    st.divider()
    st.subheader(t("rk_result"))
    left, right = st.columns([1, 2])
    left.metric(t("rk_score"), f"{score} / 26")
    with right:
        st.progress(score / 26)
        if bmi is None:
            st.caption(t("rk_score_min", score=score))
        if waist is None:
            st.caption(t("rk_score_waist"))

    advice = "rk_adv_low" if category == "low" else "rk_adv_mid" if category in ("slight", "moderate") else "rk_adv_high"
    BOX[category](
        f"**{t('rk_cat_' + category)}.** "
        + t("rk_chance", chance=t("rk_c_" + category)) + "\n\n" + t(advice)
    )

    st.markdown(f"**{t('rk_change_title')}**")
    changes = []
    if parts["active"]:
        changes.append(t("rk_change_active"))
    if parts["veg"]:
        changes.append(t("rk_change_veg"))
    if parts["waist"]:
        changes.append(t("rk_change_waist"))
    st.markdown("\n".join(f"- {c}" for c in changes) if changes else t("rk_change_none"))

    # Blood pressure advice
    st.markdown(f"**{t('rk_bp_result')}**")
    if told_high or bp_meds:
        st.error(t("rk_bp_adv_high"))
    elif last_bp == "recent":
        st.success(t("rk_bp_adv_ok"))
    else:
        message = t("rk_bp_adv_due")
        if parts["age"] >= 2 or parts["bmi"] >= 1 or parts["waist"] >= 3 or family != "no":
            message += " " + t("rk_bp_adv_risk")
        st.warning(message)

    st.caption(t("rk_about"))