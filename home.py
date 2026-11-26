"""Home screen: a simple, step-by-step way into the app.

Instead of one long menu, people see:
- "What do you need today?" quick buttons
- Step 1 Learn and stay safe -> Step 2 Check yourself -> Step 3 Track and
  improve -> Step 4 Advanced AI tools
- A separate section for health workers

The current page is kept in st.session_state.page ("home" by default).
"""

import streamlit as st

import i18n
from i18n import t

# page key -> (icon, step)
PAGES = {
    "page_danger": ("🚨", 1), "page_education": ("📚", 1),
    "page_risk": ("🤔", 2), "page_measure": ("✋", 2),
    "page_tracker": ("🩺", 3), "page_habits": ("🔥", 3),
    "page_ai": ("🤖", 4),
    "page_chp": ("🏘️", 5), "page_dashboard": ("📋", 5),
}

i18n.register({
    "home": {"en": "Home", "sw": "Mwanzo"},
    "home_back": {"en": "← Home", "sw": "← Mwanzo"},
    "home_hello": {"en": "Hello, {name} 👋", "sw": "Habari, {name} 👋"},
    "home_sub": {
        "en": "Start with Step 1 and move on at your own pace. Everything here is free.",
        "sw": "Anza na Hatua ya 1 na uendelee kwa kasi yako. Kila kitu hapa ni bure.",
    },
    "home_need": {"en": "What do you need today?", "sw": "Unahitaji nini leo?"},
    "q_unwell": {"en": "🚨 Someone is sick: should we go to hospital?", "sw": "🚨 Mtu anaumwa: twende hospitali?"},
    "q_risk": {"en": "🤔 Am I at risk of diabetes or high BP?", "sw": "🤔 Je, niko hatarini ya kisukari au BP?"},
    "q_reading": {"en": "🩺 I have a BP or sugar reading to record", "sw": "🩺 Nina kipimo cha BP au sukari cha kuweka"},
    "q_learn": {"en": "📚 I want to learn about a disease", "sw": "📚 Nataka kujifunza kuhusu ugonjwa"},
    "home_all": {"en": "Or follow the steps", "sw": "Au fuata hatua"},
    "home_open": {"en": "Open →", "sw": "Fungua →"},
    "home_start": {"en": "⭐ Start here", "sw": "⭐ Anza hapa"},
    "jump": {"en": "Go to a page", "sw": "Nenda kwenye ukurasa"},
    "page_ai": {"en": "AI risk tools", "sw": "Zana za AI za hatari"},
    "home_choose": {"en": "Choose a tool. New here? Start with ⭐",
                    "sw": "Chagua zana. Mgeni hapa? Anza na ⭐"},
    "home_sos": {"en": "🚨 Someone is very sick? Check danger signs",
                 "sw": "🚨 Mtu anaumwa sana? Angalia dalili za hatari"},
    "home_tap": {"en": "Tap any icon to open · 🏠 Home is always in the menu",
                 "sw": "Gusa ikoni yoyote kufungua · 🏠 Mwanzo iko kwenye menyu daima"},
    "ai_pick": {"en": "Which risk?", "sw": "Hatari ipi?"},
    "s_page_danger": {"en": "Danger signs ⭐", "sw": "Dalili za hatari ⭐"},
    "s_page_risk": {"en": "Am I at risk?", "sw": "Niko hatarini?"},
    "s_page_measure": {"en": "Measure by hand", "sw": "Pima kwa mkono"},
    "s_page_tracker": {"en": "My tracker", "sw": "Kifuatilia changu"},
    "s_page_habits": {"en": "Habits", "sw": "Tabia"},
    "s_page_education": {"en": "Learn", "sw": "Jifunze"},
    "s_page_ai": {"en": "AI risk", "sw": "Hatari kwa AI"},
    "s_page_chp": {"en": "CHP mode", "sw": "Hali ya CHP"},
    "s_page_dashboard": {"en": "Patients", "sw": "Wagonjwa"},
    "d_page_ai": {"en": "AI estimates of diabetes and heart disease risk.",
                  "sw": "Makadirio ya AI ya hatari ya kisukari na ugonjwa wa moyo."},

    "step_1": {"en": "Step 1 · Learn and stay safe", "sw": "Hatua ya 1 · Jifunze na uwe salama"},
    "step_1_sub": {"en": "No equipment, no numbers. Know the warning signs.",
                   "sw": "Bila kifaa, bila namba. Jua dalili za hatari."},
    "step_2": {"en": "Step 2 · Check yourself (no machine needed)", "sw": "Hatua ya 2 · Jipime (bila kifaa)"},
    "step_2_sub": {"en": "Simple questions and your own hands.",
                   "sw": "Maswali rahisi na mikono yako mwenyewe."},
    "step_3": {"en": "Step 3 · Track and improve", "sw": "Hatua ya 3 · Fuatilia na uboreshe"},
    "step_3_sub": {"en": "Record readings over time and build healthy habits.",
                   "sw": "Weka vipimo kwa muda na ujenge tabia za afya."},
    "step_4": {"en": "Step 4 · Advanced: AI risk tools", "sw": "Hatua ya 4 · Ya juu: zana za AI"},
    "step_4_sub": {"en": "For people who know their lab results (glucose, cholesterol).",
                   "sw": "Kwa wanaojua matokeo yao ya maabara (sukari, kolesteroli)."},
    "step_5": {"en": "For health workers", "sw": "Kwa wahudumu wa afya"},
    "step_5_sub": {"en": "Community Health Promoters and clinic staff.",
                   "sw": "Wahudumu wa Afya ya Jamii na wafanyakazi wa kliniki."},

    "d_page_danger": {"en": "Signs that mean go to hospital now: adults, pregnancy, children, newborns.",
                      "sw": "Dalili zinazomaanisha nenda hospitali sasa: watu wazima, ujauzito, watoto, wachanga."},
    "d_page_education": {"en": "Causes, symptoms, treatment and prevention of any disease.",
                         "sw": "Visababishi, dalili, matibabu na kinga ya ugonjwa wowote."},
    "d_page_risk": {"en": "8 quick questions about your diabetes and blood pressure risk.",
                    "sw": "Maswali 8 ya haraka kuhusu hatari yako ya kisukari na shinikizo la damu."},
    "d_page_measure": {"en": "Check a pulse, a child's breathing or a child's arm (MUAC).",
                       "sw": "Pima mapigo ya moyo, pumzi za mtoto au mkono wa mtoto (MUAC)."},
    "d_page_tracker": {"en": "Save your BP, sugar and weight and see your trends.",
                       "sw": "Hifadhi BP, sukari na uzito wako na uone mwenendo."},
    "d_page_habits": {"en": "Daily challenge, Kenyan food guide, quiz and reminders.",
                      "sw": "Changamoto ya kila siku, mwongozo wa chakula, maswali na vikumbusho."},
    "d_page_diabetes": {"en": "AI estimate of diabetes risk from lab values.",
                        "sw": "Makadirio ya AI ya hatari ya kisukari kutoka vipimo vya maabara."},
    "d_page_heart": {"en": "AI estimate of heart disease risk from clinical values.",
                     "sw": "Makadirio ya AI ya hatari ya ugonjwa wa moyo kutoka vipimo vya kliniki."},
    "d_page_chp": {"en": "Register households, record home visits, refer and follow up.",
                   "sw": "Sajili kaya, rekodi kutembelea nyumbani, toa rufaa na fuatilia."},
    "d_page_dashboard": {"en": "Register patients with ICD-11 diagnoses and see analytics.",
                         "sw": "Sajili wagonjwa kwa misimbo ya ICD-11 na uone takwimu."},
})


def current():
    return st.session_state.get("page", "home")


def go(page):
    st.session_state.page = page


def _jumped():
    go(st.session_state.nav_jump)


def sidebar():
    """Home button and a compact 'go to' list for people who know where they're going."""
    st.sidebar.button("🏠 " + t("home"), on_click=go, args=("home",), width="stretch")
    options = ["home"] + list(PAGES)
    st.session_state.nav_jump = current() if current() in options else "home"
    st.sidebar.selectbox(
        t("jump"), options, key="nav_jump", on_change=_jumped,
        format_func=lambda p: "🏠 " + t("home") if p == "home" else f"{PAGES[p][0]} {t(p)}",
    )


def back_bar(page):
    """'← Home' button and the step this page belongs to, shown at the top of each page."""
    left, right = st.columns([1, 3])
    left.button(t("home_back"), on_click=go, args=("home",), key="back_home")
    icon, step = PAGES.get(page, ("", 0))
    if step:
        right.caption(t(f"step_{step}"))


# Order of the icons in the 3 x 3 grid
GRID = ["page_danger", "page_risk", "page_measure",
        "page_tracker", "page_habits", "page_education",
        "page_ai", "page_chp", "page_dashboard"]


def _css(theme):
    a, border, text = theme["accent"], theme["border"], theme["text"]
    return f"""<style>
    /* Keep 3 icons per row, even on narrow phone screens */
    .st-key-home_grid [data-testid="stHorizontalBlock"] {{ flex-wrap: nowrap !important; gap: 8px !important; }}
    .st-key-home_grid [data-testid="stColumn"] {{ min-width: 0 !important; flex: 1 1 0 !important; width: auto !important; }}
    /* Big square app-style buttons: icon on top, short label below */
    .st-key-home_grid button {{
        height: 104px; width: 100%; border-radius: 16px !important; background: #FFFFFF !important;
        border: 1px solid {border} !important; padding: 6px 4px !important; }}
    .st-key-home_grid button:hover {{ border-color: {a} !important; box-shadow: 0 2px 8px {a}33; }}
    .st-key-home_grid button > div {{ flex-direction: column !important; gap: 4px !important; }}
    .st-key-home_grid button [data-testid="stIconEmoji"] {{ font-size: 32px !important; margin: 0 !important; }}
    .st-key-home_grid button p {{ color: {text} !important; font-size: 13px !important; font-weight: 600 !important;
        line-height: 1.2 !important; white-space: normal !important; }}
    /* Red emergency button */
    .st-key-home_sos button {{ background: #C0392B !important; border: none !important; border-radius: 14px !important;
        padding: 12px !important; }}
    .st-key-home_sos button p {{ color: #FFFFFF !important; font-weight: 700 !important; font-size: 15px !important; }}
    </style>"""


def render(theme, user_name):
    st.html(_css(theme))
    first = (user_name or "").split(" ")[0]
    st.markdown(f"### {t('home_hello', name=first)}")
    st.caption(t("home_choose"))

    with st.container(key="home_sos"):
        st.button(t("home_sos"), on_click=go, args=("page_danger",), width="stretch")

    with st.container(key="home_grid"):
        for row in range(3):
            cols = st.columns(3)
            for col, page in zip(cols, GRID[row * 3:row * 3 + 3]):
                with col:
                    st.button(t("s_" + page), icon=PAGES[page][0], key=f"tile_{page}",
                              on_click=go, args=(page,), width="stretch")
    st.caption(t("home_tap"))