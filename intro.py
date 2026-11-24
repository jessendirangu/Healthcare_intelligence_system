"""Welcome page shown when someone first opens the website.

Laid out like an organisation's home page: hero, key facts, vision and
mission, why the project exists, stories, what the site offers, and a
call to action. Everything is in English and Kiswahili.

Facts and sources (checked November 2026):
- WHO hypertension fact sheet, 25 Sept 2025: 1.4 billion adults aged 30-79
  had hypertension in 2024 (33%); about 600 million (44%) were unaware;
  only 23% had it under control.
- Kenya STEPwise survey 2015: 56% of adults had never had their blood
  pressure measured.
- Mohamed SF et al., BMC Public Health 2018 (Kenya STEPS data): only 15.6%
  of Kenyans with hypertension were aware of it.

The stories are illustrative composites of common situations in Kenyan
health facilities, clearly labelled as such. They are not real patients.
"""

import random

import streamlit as st

import i18n
from i18n import t

HEALTH_TIPS = {
    "en": [
        "High blood pressure often has no symptoms. The only way to know is to have it measured.",
        "Eating less salt (under one teaspoon a day) helps keep blood pressure healthy.",
        "Being physically active for at least 150 minutes a week lowers the risk of heart "
        "disease, stroke and type 2 diabetes.",
        "Blood pressure medicine works only if you keep taking it, even when you feel well.",
        "Washing hands with soap and water is one of the most effective ways to prevent "
        "diarrhoea and chest infections.",
        "A cough lasting two weeks or more should be checked at a health facility. "
        "It could be tuberculosis, which is curable.",
    ],
    "sw": [
        "Shinikizo la juu la damu mara nyingi halina dalili. Njia pekee ya kujua ni kupimwa.",
        "Kula chumvi kidogo (chini ya kijiko kimoja cha chai kwa siku) husaidia kuweka "
        "shinikizo la damu katika hali nzuri.",
        "Kufanya mazoezi angalau dakika 150 kwa wiki hupunguza hatari ya ugonjwa wa moyo, "
        "kiharusi na kisukari aina ya 2.",
        "Dawa ya shinikizo la damu hufanya kazi tu ukiendelea kuimeza, hata ukijisikia vizuri.",
        "Kunawa mikono kwa sabuni na maji ni mojawapo ya njia bora zaidi za kuzuia kuhara "
        "na maambukizi ya kifua.",
        "Kikohozi cha wiki mbili au zaidi kinapaswa kuchunguzwa kituo cha afya. "
        "Huenda ikawa kifua kikuu, ambacho kinatibika.",
    ],
}

i18n.register({
    "in_kicker": {"en": "HEALTHCARE INTELLIGENCE SYSTEM", "sw": "HEALTHCARE INTELLIGENCE SYSTEM"},
    "in_headline": {
        "en": "Know your numbers.<br>Act before it's an emergency.",
        "sw": "Jua vipimo vyako.<br>Chukua hatua kabla ya dharura.",
    },
    "in_lead": {
        "en": "A free, bilingual health platform that helps people track their blood pressure, "
              "understand their health and reach care early. Built by a Kenyan nurse.",
        "sw": "Jukwaa la afya la bure, kwa lugha mbili, linalosaidia watu kufuatilia shinikizo "
              "la damu, kuelewa afya yao na kupata huduma mapema. Limetengenezwa na muuguzi Mkenya.",
    },
    "in_enter": {"en": "Enter the website →", "sw": "Ingia kwenye tovuti →"},
    "in_enter_bottom": {"en": "Start tracking your health →", "sw": "Anza kufuatilia afya yako →"},

    # Facts band
    "in_facts_title": {"en": "The silent problem", "sw": "Tatizo lisilo na sauti"},
    "f1_num": {"en": "1 in 3", "sw": "1 kati ya 3"},
    "f1_text": {
        "en": "adults aged 30–79 worldwide have high blood pressure",
        "sw": "ya watu wazima wenye miaka 30–79 duniani wana shinikizo la juu la damu",
    },
    "f2_num": {"en": "600 million", "sw": "Milioni 600"},
    "f2_text": {
        "en": "people with hypertension don't know they have it",
        "sw": "ya watu wenye shinikizo la juu la damu hawajui kuwa wanalo",
    },
    "f3_num": {"en": "56%", "sw": "56%"},
    "f3_text": {
        "en": "of Kenyan adults had never had their blood pressure measured",
        "sw": "ya watu wazima Kenya hawakuwahi kupimwa shinikizo la damu",
    },
    "f4_num": {"en": "Only 16%", "sw": "Ni 16% tu"},
    "f4_text": {
        "en": "of Kenyans with hypertension knew they had it",
        "sw": "ya Wakenya wenye shinikizo la juu la damu walijua kuwa wanalo",
    },
    "in_sources": {
        "en": "Sources: WHO Hypertension fact sheet (2025); Kenya STEPwise Survey (2015); "
              "Mohamed et al., BMC Public Health (2018).",
        "sw": "Vyanzo: WHO, Taarifa kuhusu shinikizo la juu la damu (2025); Utafiti wa STEPwise "
              "Kenya (2015); Mohamed na wenzake, BMC Public Health (2018).",
    },

    # Vision, mission, values
    "in_vision_label": {"en": "OUR VISION", "sw": "MAONO YETU"},
    "in_vision": {
        "en": "A Kenya where no one discovers a silent disease too late.",
        "sw": "Kenya ambayo hakuna mtu anayegundua ugonjwa usio na dalili akiwa amechelewa.",
    },
    "in_mission_label": {"en": "OUR MISSION", "sw": "DHAMIRA YETU"},
    "in_mission": {
        "en": "To help people detect, understand and manage chronic conditions early, starting "
              "with high blood pressure, through simple bilingual digital tools built on "
              "clinical evidence and responsible use of data and AI.",
        "sw": "Kusaidia watu kugundua, kuelewa na kudhibiti magonjwa sugu mapema, tukianza na "
              "shinikizo la juu la damu, kupitia zana rahisi za kidijitali za lugha mbili "
              "zinazotegemea ushahidi wa kitabibu na matumizi ya data na AI kwa uwajibikaji.",
    },
    "in_values_label": {"en": "OUR VALUES", "sw": "MAADILI YETU"},
    "v1_t": {"en": "Evidence first", "sw": "Ushahidi kwanza"},
    "v1_d": {
        "en": "Advice follows WHO and international clinical guidelines.",
        "sw": "Ushauri unafuata miongozo ya WHO na ya kimataifa ya kitabibu.",
    },
    "v2_t": {"en": "Privacy by design", "sw": "Faragha tangu mwanzo"},
    "v2_d": {
        "en": "Only you see your readings. We collect the minimum, in line with Kenya's Data Protection Act.",
        "sw": "Ni wewe pekee unayeona vipimo vyako. Tunakusanya kidogo tu, kulingana na Sheria ya Ulinzi wa Data.",
    },
    "v3_t": {"en": "For everyone", "sw": "Kwa kila mtu"},
    "v3_d": {
        "en": "Free, in English and Kiswahili, and works on any phone with a browser.",
        "sw": "Ni bure, kwa Kiingereza na Kiswahili, na inafanya kazi kwenye simu yoyote yenye kivinjari.",
    },
    "v4_t": {"en": "Safe, not a diagnosis", "sw": "Salama, si utambuzi"},
    "v4_d": {
        "en": "We help you know when to see a health worker. We never replace one.",
        "sw": "Tunakusaidia kujua wakati wa kumwona mhudumu wa afya. Hatuchukui nafasi yake.",
    },

    # Why
    "in_why_label": {"en": "WHY THIS EXISTS", "sw": "KWA NINI TUMEANZISHA HII"},
    "in_why_title": {
        "en": "A note from the founder",
        "sw": "Ujumbe kutoka kwa mwanzilishi",
    },
    "in_why_body": {
        "en": "As a registered nurse working in emergency, triage and outpatient clinics in Kenya, "
              "I met too many patients whose first sign of high blood pressure was a stroke, "
              "heart failure or kidney damage. Most had never had their blood pressure measured. "
              "Others had been diagnosed but stopped their medicine because they felt well.<br><br>"
              "High blood pressure is easy to measure and cheap to treat. What is missing is "
              "awareness and follow-up. I built this platform so that people can know their "
              "numbers, understand what they mean in their own language, and reach care before "
              "it becomes an emergency.",
        "sw": "Kama muuguzi aliyesajiliwa nikifanya kazi katika huduma za dharura, upimaji wa awali "
              "(triage) na kliniki za wagonjwa wa nje nchini Kenya, nilikutana na wagonjwa wengi "
              "ambao dalili yao ya kwanza ya shinikizo la juu la damu ilikuwa kiharusi, moyo "
              "kushindwa kufanya kazi au figo kuharibika. Wengi hawakuwahi kupimwa shinikizo la damu. "
              "Wengine waligunduliwa lakini wakaacha dawa kwa sababu walijisikia vizuri.<br><br>"
              "Shinikizo la juu la damu ni rahisi kupima na ni nafuu kutibu. Kinachokosekana ni "
              "ufahamu na ufuatiliaji. Nimetengeneza jukwaa hili ili watu wajue vipimo vyao, "
              "waelewe maana yake kwa lugha yao, na wafikie huduma kabla ya dharura.",
    },
    "in_why_sign": {
        "en": "Jesse Kigo Ndirangu, RN · Founder",
        "sw": "Jesse Kigo Ndirangu, Muuguzi · Mwanzilishi",
    },

    # Stories
    "in_stories_label": {"en": "STORIES FROM THE WARD", "sw": "HADITHI KUTOKA WODINI"},
    "in_stories_title": {
        "en": "Why early detection matters",
        "sw": "Kwa nini kugundua mapema ni muhimu",
    },
    "in_stories_note": {
        "en": "Illustrative stories based on situations commonly seen in Kenyan health facilities. "
              "Names and details are changed; they are not real patients.",
        "sw": "Hadithi za mfano zinazotokana na hali zinazoonekana mara nyingi katika vituo vya afya "
              "Kenya. Majina na maelezo yamebadilishwa; si wagonjwa halisi.",
    },
    "s1_name": {"en": "Mama Achieng', 52 · market trader", "sw": "Mama Achieng', 52 · mfanyabiashara sokoni"},
    "s1_body": {
        "en": "For months she treated her headaches with painkillers from the shop. She arrived in "
              "the emergency room with weakness on one side of her body. Her blood pressure was "
              "210/120. She had a stroke. She had never had her blood pressure checked.",
        "sw": "Kwa miezi kadhaa alitibu maumivu ya kichwa kwa dawa za dukani. Alifika kwenye chumba "
              "cha dharura akiwa na udhaifu upande mmoja wa mwili. Shinikizo lake la damu lilikuwa "
              "210/120. Alipata kiharusi. Hakuwahi kupimwa shinikizo la damu.",
    },
    "s1_lesson": {
        "en": "A two-minute check could have found it years earlier.",
        "sw": "Kipimo cha dakika mbili kingeweza kuligundua miaka kadhaa mapema.",
    },
    "s2_name": {"en": "Mzee Kiprono, 64 · retired teacher", "sw": "Mzee Kiprono, 64 · mwalimu mstaafu"},
    "s2_body": {
        "en": "He was diagnosed with hypertension and given tablets. When he felt better, and money "
              "was tight, he stopped taking them. Two years later he came back breathless, with "
              "swollen legs: heart failure.",
        "sw": "Aligunduliwa na shinikizo la juu la damu na akapewa vidonge. Alipojisikia vizuri, na "
              "pesa zikiwa chache, aliacha kuvimeza. Miaka miwili baadaye alirudi akiwa anapumua kwa "
              "shida na miguu imevimba: moyo ulikuwa umeshindwa kufanya kazi vizuri.",
    },
    "s2_lesson": {
        "en": "Hypertension is lifelong. Follow-up saves lives.",
        "sw": "Shinikizo la damu ni la maisha yote. Ufuatiliaji huokoa maisha.",
    },
    "s3_name": {"en": "Wanjiru, 38 · mother of three", "sw": "Wanjiru, 38 · mama wa watoto watatu"},
    "s3_body": {
        "en": "At a community screening, a health volunteer found her blood pressure at 150/95. "
              "She measured it at home for a week and the average stayed high. She saw a clinician, "
              "started treatment and changed her diet. Today her blood pressure is normal.",
        "sw": "Kwenye upimaji wa jamii, mhudumu wa afya wa kujitolea alikuta shinikizo lake ni 150/95. "
              "Alipima nyumbani kwa wiki moja na wastani ukabaki juu. Alimwona mhudumu wa afya, akaanza "
              "matibabu na kubadilisha lishe. Leo shinikizo lake la damu ni la kawaida.",
    },
    "s3_lesson": {
        "en": "Found early, it is simple to control.",
        "sw": "Likigunduliwa mapema, ni rahisi kudhibiti.",
    },

    # Features
    "in_offer_label": {"en": "WHAT YOU CAN DO HERE", "sw": "UNACHOWEZA KUFANYA HAPA"},
    "o1_t": {"en": "Track your health", "sw": "Fuatilia afya yako"},
    "o1_d": {
        "en": "Record blood pressure, sugar and weight. See your trends and clear advice on what to do next.",
        "sw": "Weka vipimo vya shinikizo la damu, sukari na uzito. Ona mwenendo wako na ushauri wa nini cha kufanya.",
    },
    "o2_t": {"en": "Learn about diseases", "sw": "Jifunze kuhusu magonjwa"},
    "o2_d": {
        "en": "Causes, symptoms, diagnosis, treatment and prevention, from WHO and MedlinePlus.",
        "sw": "Visababishi, dalili, utambuzi, matibabu na kinga, kutoka WHO na MedlinePlus.",
    },
    "o3_t": {"en": "Check your risk", "sw": "Pima hatari yako"},
    "o3_d": {
        "en": "See how AI estimates the risk of diabetes and heart disease, and what drives it.",
        "sw": "Ona jinsi AI inavyokadiria hatari ya kisukari na ugonjwa wa moyo, na kinachoichangia.",
    },
    "o4_t": {"en": "For health workers", "sw": "Kwa wahudumu wa afya"},
    "o4_d": {
        "en": "Register patients, record vital signs and see analytics coded with WHO ICD-11.",
        "sw": "Sajili wagonjwa, weka vipimo muhimu na uone takwimu kwa misimbo ya WHO ICD-11.",
    },
    "in_tip_label": {"en": "HEALTH TIP OF THE DAY", "sw": "DONDOO LA AFYA LA LEO"},
    "in_cta": {
        "en": "Your health starts with one reading.",
        "sw": "Afya yako inaanza na kipimo kimoja.",
    },
    "in_caption": {
        "en": "For education and self-monitoring support. Not a substitute for professional medical advice.",
        "sw": "Kwa elimu na kusaidia kujifuatilia. Haichukui nafasi ya ushauri wa kitaalamu wa afya.",
    },
})


def _css(c):
    return f"""
<style>
  section[data-testid="stSidebar"], [data-testid="stSidebarCollapsedControl"] {{ display: none; }}
  .lp {{ font-family: sans-serif; color: {c['text']}; }}
  .lp h2 {{ font-size: clamp(22px, 3.2vw, 30px); margin: 0 0 6px; color: {c['text']}; }}
  .lp-label {{ font-size: 12px; font-weight: 700; letter-spacing: 2px; color: {c['accent']}; margin-bottom: 8px; }}
  .lp-section {{ max-width: 1100px; margin: 34px auto 0; padding: 0 8px; }}
  .lp-grid {{ display: grid; gap: 16px; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); }}
  .lp-card {{ background: {c['surface']}; border: 1px solid {c['border']}; border-radius: 14px; padding: 20px; }}
  .lp-card h3 {{ margin: 0 0 6px; font-size: 17px; color: {c['text']}; }}
  .lp-card p {{ margin: 0; font-size: 14.5px; line-height: 1.55; color: {c['muted']}; }}

  /* Hero */
  .lp-hero {{
      text-align: center; padding: 44px 20px 30px; border-radius: 20px;
      background: radial-gradient(circle at 50% 0%, {c['accent']}26 0%, transparent 70%);
  }}
  .lp-heart {{
      width: 60px; height: 60px; margin: 0 auto 6px; border-radius: 50%;
      background: {c['accent']}; color: #fff; font-size: 28px; line-height: 60px;
      animation: lp-pulse 1.6s ease-in-out infinite;
  }}
  .lp-ecg {{ width: 100%; max-width: 620px; height: 60px; margin: 0 auto; display: block; }}
  .lp-ecg path {{
      fill: none; stroke: {c['accent']}; stroke-width: 3; stroke-linecap: round; stroke-linejoin: round;
      stroke-dasharray: 900; stroke-dashoffset: 900; animation: lp-draw 2.8s ease-in-out infinite;
  }}
  .lp-kicker {{ font-size: 13px; letter-spacing: 3px; font-weight: 700; color: {c['accent']}; margin-top: 6px; }}
  .lp-headline {{
      font-size: clamp(30px, 5.5vw, 52px); font-weight: 800; line-height: 1.12; margin: 10px 0 12px;
      opacity: 0; animation: lp-up .9s ease-out .2s forwards;
  }}
  .lp-lead {{
      font-size: 18px; color: {c['muted']}; max-width: 700px; margin: 0 auto; line-height: 1.55;
      opacity: 0; animation: lp-up .9s ease-out .5s forwards;
  }}

  /* Facts */
  .lp-facts {{ background: {c['accent']}; border-radius: 18px; padding: 26px 22px; color: #fff; }}
  .lp-facts h2 {{ color: #fff; }}
  .lp-fact-num {{ font-size: clamp(28px, 4vw, 38px); font-weight: 800; }}
  .lp-fact-text {{ font-size: 14.5px; line-height: 1.45; opacity: .93; }}
  .lp-sources {{ font-size: 12px; opacity: .85; margin-top: 16px; }}

  /* Vision and mission */
  .lp-vm {{ display: grid; gap: 16px; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); }}
  .lp-vm .lp-card {{ border-top: 5px solid {c['accent']}; }}
  .lp-statement {{ font-size: 19px; line-height: 1.5; font-weight: 600; color: {c['text']}; }}

  /* Founder note */
  .lp-note {{
      background: {c['surface']}; border: 1px solid {c['border']}; border-left: 6px solid {c['accent']};
      border-radius: 14px; padding: 24px 26px;
  }}
  .lp-note p {{ font-size: 16px; line-height: 1.7; color: {c['text']}; margin: 10px 0 0; }}
  .lp-sign {{ margin-top: 14px; font-weight: 700; color: {c['accent']}; }}

  /* Stories */
  .lp-story {{ display: flex; flex-direction: column; }}
  .lp-story .lp-who {{ font-weight: 700; color: {c['text']}; margin-bottom: 8px; }}
  .lp-story .lp-lesson {{
      margin-top: auto; padding-top: 12px; font-weight: 700; color: {c['accent']}; font-size: 14.5px;
  }}
  .lp-note-small {{ font-size: 12.5px; color: {c['muted']}; margin: 4px 0 14px; font-style: italic; }}

  /* Tip and closing line */
  .lp-tip {{ border-left: 5px solid {c['accent']}; }}
  .lp-cta {{ text-align: center; font-size: clamp(22px, 3vw, 30px); font-weight: 800; margin: 40px 0 14px; }}

  .lp-reveal {{ opacity: 0; animation: lp-up .9s ease-out .8s forwards; }}
  @keyframes lp-up {{ from {{ opacity: 0; transform: translateY(14px); }} to {{ opacity: 1; transform: none; }} }}
  @keyframes lp-draw {{ 0% {{ stroke-dashoffset: 900; }} 60% {{ stroke-dashoffset: 0; }} 100% {{ stroke-dashoffset: -900; }} }}
  @keyframes lp-pulse {{
      0%, 100% {{ transform: scale(1); box-shadow: 0 0 0 0 {c['accent']}55; }}
      15% {{ transform: scale(1.12); }}
      30% {{ transform: scale(1); box-shadow: 0 0 0 18px {c['accent']}00; }}
  }}
  @media (prefers-reduced-motion: reduce) {{
      .lp *, .lp {{ animation: none !important; opacity: 1 !important; }}
      .lp-ecg path {{ stroke-dashoffset: 0; }}
  }}
</style>"""


def _cards(items):
    return "".join(
        f'<div class="lp-card"><h3>{t(title)}</h3><p>{t(text)}</p></div>'
        for title, text in items
    )


def _enter_button(label_key, key):
    _, middle, _ = st.columns([1, 1.2, 1])
    with middle:
        if st.button(t(label_key), type="primary", width="stretch", key=key):
            st.session_state.entered = True
            st.rerun()


def render(theme):
    c = theme  # colours
    if not isinstance(st.session_state.get("tip"), int):
        st.session_state.tip = random.randrange(len(HEALTH_TIPS["en"]))
    tip = HEALTH_TIPS[i18n.lang()][st.session_state.tip]

    st.html(_css(c))

    _, picker, _ = st.columns([1, 1, 1])
    with picker:
        i18n.language_picker(key="lang_intro")

    # 1. Hero
    st.html(f"""
<div class="lp"><div class="lp-hero">
  <div class="lp-heart">♥</div>
  <svg class="lp-ecg" viewBox="0 0 640 60" aria-hidden="true">
    <path d="M0 34 H170 L190 34 L205 14 L220 50 L240 4 L258 56 L272 34 H360
             L375 27 L390 34 H470 L485 34 L500 16 L515 48 L532 8 L548 54 L560 34 H640"/>
  </svg>
  <div class="lp-kicker">{t("in_kicker")}</div>
  <div class="lp-headline">{t("in_headline")}</div>
  <div class="lp-lead">{t("in_lead")}</div>
</div></div>""")
    _enter_button("in_enter", "enter_top")

    # 2. Facts  3. Vision, mission, values  4. Founder note  5. Stories  6. Offer  7. Tip
    facts = "".join(
        f'<div><div class="lp-fact-num">{t(f"f{i}_num")}</div>'
        f'<div class="lp-fact-text">{t(f"f{i}_text")}</div></div>'
        for i in range(1, 5)
    )
    stories = "".join(
        f"""<div class="lp-card lp-story">
              <div class="lp-who">{t(f"s{i}_name")}</div>
              <p>{t(f"s{i}_body")}</p>
              <div class="lp-lesson">→ {t(f"s{i}_lesson")}</div>
            </div>"""
        for i in range(1, 4)
    )
    st.html(f"""
<div class="lp lp-reveal">

  <div class="lp-section"><div class="lp-facts">
    <h2>{t("in_facts_title")}</h2>
    <div class="lp-grid" style="margin-top:14px">{facts}</div>
    <div class="lp-sources">{t("in_sources")}</div>
  </div></div>

  <div class="lp-section lp-vm">
    <div class="lp-card"><div class="lp-label">{t("in_vision_label")}</div>
      <div class="lp-statement">{t("in_vision")}</div></div>
    <div class="lp-card"><div class="lp-label">{t("in_mission_label")}</div>
      <div class="lp-statement" style="font-size:16.5px; font-weight:500">{t("in_mission")}</div></div>
  </div>

  <div class="lp-section">
    <div class="lp-label">{t("in_values_label")}</div>
    <div class="lp-grid">{_cards([(f"v{i}_t", f"v{i}_d") for i in range(1, 5)])}</div>
  </div>

  <div class="lp-section"><div class="lp-note">
    <div class="lp-label">{t("in_why_label")}</div>
    <h2>{t("in_why_title")}</h2>
    <p>{t("in_why_body")}</p>
    <div class="lp-sign">{t("in_why_sign")}</div>
  </div></div>

  <div class="lp-section">
    <div class="lp-label">{t("in_stories_label")}</div>
    <h2>{t("in_stories_title")}</h2>
    <div class="lp-note-small">{t("in_stories_note")}</div>
    <div class="lp-grid">{stories}</div>
  </div>

  <div class="lp-section">
    <div class="lp-label">{t("in_offer_label")}</div>
    <div class="lp-grid">{_cards([(f"o{i}_t", f"o{i}_d") for i in range(1, 5)])}</div>
  </div>

  <div class="lp-section"><div class="lp-card lp-tip">
    <div class="lp-label">{t("in_tip_label")}</div>
    <p style="font-size:16px; color:{c['text']}">{tip}</p>
  </div></div>

  <div class="lp-cta">{t("in_cta")}</div>
</div>""")
    _enter_button("in_enter_bottom", "enter_bottom")
    st.caption(t("in_caption"))