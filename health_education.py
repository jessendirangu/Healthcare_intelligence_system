"""Health education content for common conditions seen in Kenyan practice.

General educational information only. Treatment sections describe the
types of treatment used, not doses - those follow national guidelines
and a clinician's prescription.
"""

import html
import re
import xml.etree.ElementTree as ET

import requests
import streamlit as st

import demo
import i18n
from health_education_sw import DISEASES_SW
from i18n import t

MEDLINEPLUS_URL = "https://wsearch.nlm.nih.gov/ws/query"

DISEASES = {
    "Malaria": {
        "category": "Infectious disease",
        "overview": (
            "A life-threatening disease caused by Plasmodium parasites. "
            "Plasmodium falciparum, the most dangerous species, is the most "
            "common in Kenya. Children under 5 and pregnant women are at highest risk."
        ),
        "causes": [
            "Bite of an infected female Anopheles mosquito (mostly at night)",
            "Less commonly: blood transfusion or from mother to baby",
            "Higher risk in lake, coastal and lowland areas and during rainy seasons",
        ],
        "symptoms": [
            "Fever, chills and sweating",
            "Headache, body aches and tiredness",
            "Nausea, vomiting, loss of appetite",
            "Severe malaria: confusion, convulsions, difficulty breathing, "
            "dark urine, severe anaemia, inability to sit or drink",
        ],
        "diagnosis": [
            "Malaria rapid diagnostic test (mRDT)",
            "Blood smear microscopy",
            "Every suspected case should be tested before treatment",
        ],
        "treatment": [
            "Uncomplicated malaria: artemisinin-based combination therapy (ACT), "
            "such as artemether-lumefantrine",
            "Severe malaria: injectable artesunate in hospital, then a full ACT course",
            "Supportive care: fever control, fluids, treatment of anaemia if severe",
        ],
        "management": [
            "Complete the full course of medicine even if feeling better",
            "Sleep under an insecticide-treated mosquito net every night",
            "Indoor residual spraying and clearing stagnant water",
            "Preventive treatment in pregnancy (IPTp) through antenatal care",
            "Malaria vaccine for young children in eligible areas",
        ],
        "urgent": "Convulsions, confusion, very drowsy, unable to drink, or breathing difficulty.",
        "link": "https://www.who.int/news-room/fact-sheets/detail/malaria",
    },
    "Tuberculosis (TB)": {
        "category": "Infectious disease",
        "overview": (
            "A bacterial infection that mainly affects the lungs but can affect any "
            "part of the body. It is curable and preventable."
        ),
        "causes": [
            "Mycobacterium tuberculosis, spread through the air when a person "
            "with lung TB coughs, sneezes or talks",
            "Higher risk: HIV, diabetes, malnutrition, smoking, crowded or poorly "
            "ventilated housing, close contact with a TB patient",
        ],
        "symptoms": [
            "Cough lasting 2 weeks or more, sometimes with blood",
            "Fever and night sweats",
            "Weight loss and loss of appetite",
            "Chest pain and tiredness",
        ],
        "diagnosis": [
            "Sputum molecular test (e.g. GeneXpert), which also detects rifampicin resistance",
            "Sputum smear microscopy",
            "Chest X-ray",
            "HIV testing for every person diagnosed with TB",
        ],
        "treatment": [
            "Drug-sensitive TB: a 6-month combination of antibiotics "
            "(rifampicin, isoniazid, pyrazinamide and ethambutol in the first phase)",
            "Drug-resistant TB: longer or different regimens under specialist care",
            "Treatment is free in Kenyan public health facilities",
        ],
        "management": [
            "Take medicines daily for the full course; treatment support (DOT) helps adherence",
            "Screen household contacts and offer TB preventive therapy where eligible",
            "Good nutrition and ventilation; cover coughs",
            "BCG vaccination for newborns",
        ],
        "urgent": "Coughing up large amounts of blood or severe breathlessness.",
        "link": "https://www.who.int/news-room/fact-sheets/detail/tuberculosis",
    },
    "HIV disease": {
        "category": "Infectious disease",
        "overview": (
            "HIV attacks the immune system. Without treatment it can progress to AIDS. "
            "With effective treatment, people with HIV live long, healthy lives."
        ),
        "causes": [
            "Unprotected sex with a person living with HIV",
            "Mother to child during pregnancy, birth or breastfeeding",
            "Sharing needles or exposure to infected blood",
        ],
        "symptoms": [
            "Often no symptoms for many years",
            "Early: flu-like illness a few weeks after infection",
            "Later: weight loss, recurrent infections, chronic diarrhoea, fever",
        ],
        "diagnosis": [
            "Rapid HIV tests, confirmed using the national testing algorithm",
            "Viral load testing to monitor treatment",
            "CD4 count in some situations",
        ],
        "treatment": [
            "Lifelong antiretroviral therapy (ART), started as soon as possible after diagnosis",
            "Dolutegravir-based combinations are widely used first-line",
            "Preventive therapy for opportunistic infections where indicated",
        ],
        "management": [
            "Take ART daily; an undetectable viral load means HIV is not passed on sexually (U=U)",
            "Regular viral load checks and clinic follow-up",
            "Prevention: condoms, PrEP, PEP within 72 hours of exposure, "
            "prevention of mother-to-child transmission, voluntary medical male circumcision",
        ],
        "urgent": "Possible exposure (start PEP within 72 hours), or severe illness while on treatment.",
        "link": "https://www.who.int/news-room/fact-sheets/detail/hiv-aids",
    },
    "Hypertension": {
        "category": "Cardiovascular disease",
        "overview": (
            "Blood pressure that is persistently 140/90 mmHg or higher. "
            "Often called the 'silent killer' because most people have no symptoms."
        ),
        "causes": [
            "Usually no single cause (primary hypertension)",
            "Risk factors: older age, family history, high salt intake, overweight, "
            "physical inactivity, alcohol, smoking, stress",
            "Sometimes due to kidney or hormonal disease (secondary hypertension)",
        ],
        "symptoms": [
            "Usually none",
            "Very high readings: severe headache, blurred vision, chest pain, "
            "shortness of breath, confusion",
        ],
        "diagnosis": [
            "Blood pressure measured correctly on at least two separate occasions",
            "Tests for causes and damage: kidney function, urine, blood sugar, cholesterol, ECG",
        ],
        "treatment": [
            "Lifestyle changes for everyone",
            "Medicines such as calcium channel blockers, ACE inhibitors or ARBs, "
            "and thiazide diuretics, often in combination",
        ],
        "management": [
            "Take medicines daily, even when you feel well",
            "Reduce salt, eat more vegetables and fruit, keep a healthy weight",
            "Be active for at least 150 minutes a week",
            "Limit alcohol and stop smoking",
            "Check blood pressure regularly",
        ],
        "urgent": "Chest pain, sudden weakness or numbness, trouble speaking, or a severe headache.",
        "link": "https://www.who.int/news-room/fact-sheets/detail/hypertension",
    },
    "Diabetes mellitus (Type 2)": {
        "category": "Endocrine and metabolic disease",
        "overview": (
            "A long-term condition where the body does not use insulin properly, "
            "leading to high blood sugar. Type 2 is the most common form in adults."
        ),
        "causes": [
            "Insulin resistance and reduced insulin production",
            "Risk factors: overweight, physical inactivity, unhealthy diet, "
            "family history, older age, diabetes in pregnancy",
        ],
        "symptoms": [
            "Increased thirst and frequent urination",
            "Tiredness and blurred vision",
            "Slow-healing wounds and frequent infections",
            "Many people have no symptoms early on",
        ],
        "diagnosis": [
            "Fasting plasma glucose of 7.0 mmol/L or higher",
            "HbA1c of 6.5% or higher",
            "Random glucose of 11.1 mmol/L or higher with symptoms",
            "Oral glucose tolerance test",
        ],
        "treatment": [
            "Healthy eating, physical activity and weight loss",
            "Metformin is usually the first medicine",
            "Other tablets or insulin when needed",
        ],
        "management": [
            "Regular blood sugar monitoring",
            "Daily foot checks and yearly eye checks",
            "Control blood pressure and cholesterol",
            "Know the signs of low blood sugar: shaking, sweating, confusion",
        ],
        "urgent": "Confusion, fainting, very high or very low blood sugar, or a foot wound that is getting worse.",
        "link": "https://www.who.int/news-room/fact-sheets/detail/diabetes",
    },
    "Pneumonia": {
        "category": "Respiratory disease",
        "overview": (
            "An infection of the lungs. It is a leading cause of death in children "
            "under 5, but most cases are preventable and treatable."
        ),
        "causes": [
            "Bacteria (e.g. Streptococcus pneumoniae), viruses or fungi",
            "Higher risk: young children, older adults, malnutrition, HIV, "
            "indoor smoke from cooking fuels",
        ],
        "symptoms": [
            "Cough and fever",
            "Fast or difficult breathing",
            "Chest pain when breathing",
            "In children: lower chest wall indrawing",
        ],
        "diagnosis": [
            "Clinical examination, including counting the breathing rate",
            "Oxygen saturation (pulse oximetry)",
            "Chest X-ray when available",
        ],
        "treatment": [
            "Bacterial pneumonia: antibiotics such as amoxicillin",
            "Severe pneumonia: hospital care, oxygen and injectable antibiotics",
        ],
        "management": [
            "Finish the full antibiotic course",
            "Vaccines: pneumococcal (PCV), Hib, measles and pertussis",
            "Exclusive breastfeeding for the first 6 months and good nutrition",
            "Reduce indoor smoke and wash hands",
        ],
        "urgent": "Unable to drink, convulsions, very sleepy, blue lips, or severe difficulty breathing.",
        "link": "https://www.who.int/news-room/fact-sheets/detail/pneumonia",
    },
    "Asthma": {
        "category": "Respiratory disease",
        "overview": (
            "A long-term condition where the airways become inflamed and narrow, "
            "making breathing difficult during attacks."
        ),
        "causes": [
            "Airway inflammation, often with allergies or family history",
            "Common triggers: dust, smoke, pollen, cold air, exercise, chest infections",
        ],
        "symptoms": [
            "Wheezing and cough, often worse at night",
            "Chest tightness",
            "Shortness of breath",
        ],
        "diagnosis": [
            "Clinical history and examination",
            "Spirometry showing reversible airway narrowing",
            "Peak flow monitoring",
        ],
        "treatment": [
            "Reliever inhalers to open the airways quickly during symptoms",
            "Controller (preventer) inhalers containing an inhaled corticosteroid "
            "to reduce inflammation",
            "Severe attacks: emergency care, oxygen and other medicines",
        ],
        "management": [
            "Learn correct inhaler technique; a spacer helps",
            "Follow a written asthma action plan",
            "Avoid known triggers and smoke",
            "Regular review with a health worker",
        ],
        "urgent": "Too breathless to speak, blue lips, or a reliever inhaler that is not helping.",
        "link": "https://www.who.int/news-room/fact-sheets/detail/asthma",
    },
    "Cholera": {
        "category": "Infectious disease",
        "overview": (
            "An acute diarrhoeal infection that can kill within hours if untreated, "
            "but is easily treated with rapid rehydration."
        ),
        "causes": [
            "Vibrio cholerae bacteria in contaminated water or food",
            "Poor sanitation and unsafe drinking water",
        ],
        "symptoms": [
            "Sudden, large amounts of watery diarrhoea ('rice-water' stools)",
            "Vomiting",
            "Signs of dehydration: thirst, sunken eyes, reduced urine, weakness",
        ],
        "diagnosis": [
            "Clinical diagnosis during an outbreak",
            "Rapid diagnostic tests and stool culture to confirm",
        ],
        "treatment": [
            "Oral rehydration solution (ORS) for most patients",
            "Severe dehydration: intravenous fluids",
            "Antibiotics for severe cases; zinc for children",
        ],
        "management": [
            "Drink safe, boiled or treated water",
            "Wash hands with soap after the toilet and before eating",
            "Use latrines; cook food well and eat it hot",
            "Oral cholera vaccine in high-risk areas and outbreaks",
        ],
        "urgent": "Continuous watery diarrhoea, unable to drink, or signs of severe dehydration.",
        "link": "https://www.who.int/news-room/fact-sheets/detail/cholera",
    },
}


i18n.register({
    "he_title": {"en": "Health education", "sw": "Elimu ya afya"},
    "he_caption": {
        "en": "General information for learning and health promotion. It does not replace advice from a "
              "qualified health worker. Medicine doses follow national guidelines and a clinician's prescription.",
        "sw": "Taarifa za jumla kwa kujifunza na kukuza afya. Hazichukui nafasi ya ushauri wa mhudumu wa afya "
              "aliyehitimu. Dozi za dawa hufuata miongozo ya kitaifa na maagizo ya mhudumu wa afya.",
    },
    "he_mode_guides": {"en": "📘 Guides: common conditions in Kenya", "sw": "📘 Miongozo: magonjwa ya kawaida Kenya"},
    "he_mode_search": {"en": "🔎 Search any disease", "sw": "🔎 Tafuta ugonjwa wowote"},
    "he_choose": {"en": "Choose", "sw": "Chagua"},
    "he_filter": {"en": "Filter guides", "sw": "Chuja miongozo"},
    "he_filter_ph": {"en": "e.g. malaria", "sw": "mf. malaria"},
    "he_none": {"en": "No matching guide. Try 'Search any disease' instead.",
                "sw": "Hakuna mwongozo unaolingana. Jaribu 'Tafuta ugonjwa wowote'."},
    "he_condition": {"en": "Choose a condition", "sw": "Chagua ugonjwa"},
    "he_listen": {"en": "🔊 Listen to this guide", "sw": "🔊 Sikiliza mwongozo huu"},
    "he_causes": {"en": "Causes", "sw": "Visababishi"},
    "he_symptoms": {"en": "Symptoms", "sw": "Dalili"},
    "he_diagnosis": {"en": "Diagnosis", "sw": "Utambuzi"},
    "he_treatment": {"en": "Treatment", "sw": "Matibabu"},
    "he_management": {"en": "Management & prevention", "sw": "Udhibiti na kinga"},
    "he_urgent": {"en": "Seek urgent care if:", "sw": "Tafuta huduma ya haraka ikiwa:"},
    "he_overview": {"en": "Overview", "sw": "Muhtasari"},
    "he_read_more": {"en": "Read more: [WHO fact sheet]({link}) (English)",
                     "sw": "Soma zaidi: [Taarifa ya WHO]({link}) (Kiingereza)"},
    "he_in_records": {"en": "{n} patient(s) in your records have this diagnosis.",
                      "sw": "Wagonjwa {n} katika rekodi zako wana utambuzi huu."},
    "he_search_en_only": {
        "en": "",
        "sw": "Taarifa za utafutaji huu zinatoka moja kwa moja kwa WHO na MedlinePlus, na zinapatikana kwa "
              "Kiingereza pekee. Kwa Kiswahili, tumia **Miongozo** hapo juu.",
    },
})


def _bullets(items):
    st.markdown("\n".join(f"- {item}" for item in items))


def _html_to_text(raw):
    # MedlinePlus summaries come as HTML; turn them into simple markdown
    text = html.unescape(raw or "")
    text = re.sub(r"<li[^>]*>", "\n- ", text)
    text = re.sub(r"</p>|<br\s*/?>|</ul>", "\n\n", text)
    text = re.sub(r"<[^>]+>", "", text)
    text = html.unescape(text)
    return re.sub(r"\n{3,}", "\n\n", text).strip()


@st.cache_data(ttl=86400, show_spinner="Searching MedlinePlus...")
def search_medlineplus(term):
    response = requests.get(
        MEDLINEPLUS_URL,
        params={"db": "healthTopics", "term": term, "retmax": 5},
        timeout=30,
    )
    response.raise_for_status()
    root = ET.fromstring(response.content)

    topics = []
    for doc in root.iter("document"):
        fields = {}
        for content in doc.findall("content"):
            name = content.get("name")
            if name not in fields:
                fields[name] = "".join(content.itertext())
        topics.append({
            "title": _html_to_text(fields.get("title", "")),
            "summary": _html_to_text(fields.get("FullSummary", "")),
            "url": doc.get("url", ""),
        })
    return [t for t in topics if t["title"]]


def _search_any_disease(who_search, who_definition):
    st.write(
        "Search any disease or condition. Results come live from the "
        "**WHO International Classification of Diseases (ICD-11)** and "
        "**MedlinePlus** (US National Library of Medicine)."
    )
    term = st.text_input(
        "Disease or condition", placeholder="e.g. typhoid, sickle cell, epilepsy"
    ).strip()
    if len(term) < 2:
        return

    who_col, mlp_col = st.columns(2)

    with who_col:
        st.markdown("#### WHO ICD-11")
        try:
            matches = who_search(term)
        except Exception:
            matches = None
            st.warning("The WHO service couldn't be reached right now.")
        if matches:
            choice = st.selectbox(
                "Matching diagnoses",
                range(len(matches)),
                format_func=lambda i: (
                    f"{matches[i]['title']} ({matches[i]['code'] or 'no code'})"
                ),
            )
            picked = matches[choice]
            st.markdown(f"**{picked['title']}**  \nICD-11 code: `{picked['code'] or 'none'}`")
            try:
                definition = who_definition(picked.get("uri", ""))
            except Exception:
                definition = ""
            st.write(definition or "No WHO definition is available for this entry.")
        elif matches is not None:
            st.info("No WHO match. Try another spelling.")

    with mlp_col:
        st.markdown("#### Plain-language guide (MedlinePlus)")
        try:
            topics = search_medlineplus(term)
        except Exception:
            topics = None
            st.warning("MedlinePlus couldn't be reached right now.")
        if topics:
            pick = st.selectbox(
                "Health topics", range(len(topics)),
                format_func=lambda i: topics[i]["title"],
            )
            topic = topics[pick]
            st.markdown(f"**{topic['title']}**")
            with st.container(height=420):
                st.markdown(topic["summary"] or "No summary available.")
            if topic["url"]:
                st.markdown(f"[Read the full MedlinePlus page]({topic['url']})")
            st.caption(
                "MedlinePlus is written for a US audience. Medicines and services "
                "may differ in Kenya, so follow national guidelines."
            )
        elif topics is not None:
            st.info("No MedlinePlus topic found. Try a more common name.")


def _guide(name):
    """The guide in the chosen language (falls back to English)."""
    info = dict(DISEASES[name])
    if i18n.lang() == "sw" and name in DISEASES_SW:
        info.update(DISEASES_SW[name])
    else:
        info["name"] = name
    return info


SECTIONS = [("causes", "🦠"), ("symptoms", "🤒"), ("diagnosis", "🔬"), ("treatment", "💊"), ("management", "🛡️")]


def _detailed_guides(patients):
    search = st.text_input(t("he_filter"), placeholder=t("he_filter_ph")).strip().lower()
    names = [n for n in DISEASES if not search or search in n.lower() or search in _guide(n)["name"].lower()]
    if not names:
        st.info(t("he_none"))
        return

    name = st.selectbox(t("he_condition"), names, format_func=lambda n: _guide(n)["name"])
    info = _guide(name)

    st.subheader(info["name"])
    st.caption(info["category"])
    st.write(info["overview"])

    with st.expander(t("he_listen")):
        sections = [("📖", info["overview"], False)]
        sections += [(icon, f"{t('he_' + key)}. " + ". ".join(info[key]) + ".", False) for key, icon in SECTIONS]
        sections.append(("🚨", f"{t('he_urgent')} {info['urgent']}", True))
        demo.read_aloud(info["name"], sections)

    if patients:
        count = sum(
            1 for p in patients
            if name.split(" (")[0].lower() in (p.get("Disease / Diagnosis") or "").lower()
        )
        if count:
            st.info(t("he_in_records", n=count))

    tabs = st.tabs([f"{icon} {t('he_' + key)}" for key, icon in SECTIONS])
    for tab, (key, _) in zip(tabs, SECTIONS):
        with tab:
            _bullets(info[key])

    st.error(f"**{t('he_urgent')}** {info['urgent']}")
    st.markdown(t("he_read_more", link=info["link"]))


def render(patients=None, who_search=None, who_definition=None):
    st.header(t("he_title"))
    st.caption(t("he_caption"))

    mode = st.radio(t("he_choose"), ["guides", "search"],
                    format_func=lambda m: t("he_mode_" + m), horizontal=True, key="he_mode")
    if mode == "guides":
        _detailed_guides(patients)
    else:
        if i18n.lang() == "sw":
            st.info(t("he_search_en_only"))
        _search_any_disease(who_search, who_definition)