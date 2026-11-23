"""Welcome screen shown the first time someone opens the website."""

import random

import streamlit as st

HEALTH_TIPS = [
    "Washing hands with soap and water is one of the most effective ways to "
    "prevent diarrhoea and chest infections.",
    "Sleeping under an insecticide-treated mosquito net every night helps "
    "protect you and your family from malaria.",
    "High blood pressure often has no symptoms. The only way to know is to "
    "have it measured.",
    "Exclusive breastfeeding for the first 6 months helps protect babies "
    "against infections and supports healthy growth.",
    "Being physically active for at least 150 minutes a week lowers the risk "
    "of heart disease, stroke and type 2 diabetes.",
    "A cough lasting two weeks or more should be checked at a health facility. "
    "It could be tuberculosis, which is curable.",
    "Drinking safe, boiled or treated water helps prevent cholera and typhoid.",
    "Eating less salt helps keep blood pressure healthy.",
]

FEATURES = [
    ("Patient records", "Register patients, record vital signs and see clinical "
                        "analytics, with diagnoses coded using WHO ICD-11."),
    ("Health education", "Look up any disease: causes, symptoms, diagnosis, "
                         "treatment and prevention, from WHO and MedlinePlus."),
    ("AI risk prediction", "See how machine learning estimates the risk of "
                           "diabetes and heart disease, and what drives it."),
]


def render(theme):
    if "tip" not in st.session_state:
        st.session_state.tip = random.choice(HEALTH_TIPS)

    t = theme
    cards = "".join(
        f"""<div class="intro-card" style="animation-delay:{1.4 + i * 0.2}s">
              <div class="intro-card-title">{title}</div>
              <div class="intro-card-text">{text}</div>
            </div>"""
        for i, (title, text) in enumerate(FEATURES)
    )

    st.html(f"""
<style>
  /* Hide the sidebar while the welcome screen is showing */
  section[data-testid="stSidebar"], [data-testid="stSidebarCollapsedControl"] {{
      display: none;
  }}
  .intro {{
      font-family: sans-serif; text-align: center;
      padding: 48px 20px 24px; border-radius: 18px;
      background: radial-gradient(circle at 50% 0%, {t['accent']}22 0%, transparent 65%);
  }}
  .intro-heart {{
      width: 64px; height: 64px; margin: 0 auto 10px; border-radius: 50%;
      background: {t['accent']}; color: #fff; font-size: 30px; line-height: 64px;
      animation: intro-pulse 1.6s ease-in-out infinite;
  }}
  .intro-ecg {{ width: 100%; max-width: 640px; height: 70px; margin: 0 auto; display: block; }}
  .intro-ecg path {{
      fill: none; stroke: {t['accent']}; stroke-width: 3;
      stroke-linecap: round; stroke-linejoin: round;
      stroke-dasharray: 900; stroke-dashoffset: 900;
      animation: intro-draw 2.8s ease-in-out infinite;
  }}
  .intro-title {{
      font-size: clamp(28px, 5vw, 46px); font-weight: 800; color: {t['text']};
      margin: 8px 0 6px; opacity: 0; animation: intro-up 0.9s ease-out 0.3s forwards;
  }}
  .intro-sub {{
      font-size: 17px; color: {t['muted']}; max-width: 620px; margin: 0 auto;
      opacity: 0; animation: intro-up 0.9s ease-out 0.7s forwards;
  }}
  .intro-tip {{
      max-width: 620px; margin: 26px auto 0; padding: 16px 20px; text-align: left;
      background: {t['surface']}; border: 1px solid {t['border']};
      border-left: 5px solid {t['accent']}; border-radius: 12px;
      opacity: 0; animation: intro-up 0.9s ease-out 1.1s forwards;
  }}
  .intro-tip-label {{
      font-size: 12px; font-weight: 700; letter-spacing: 2px;
      color: {t['accent']}; margin-bottom: 6px;
  }}
  .intro-tip-text {{ font-size: 15px; color: {t['text']}; line-height: 1.5; }}
  .intro-cards {{
      display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
      gap: 14px; max-width: 900px; margin: 26px auto 0;
  }}
  .intro-card {{
      background: {t['surface']}; border: 1px solid {t['border']}; border-radius: 12px;
      padding: 16px; text-align: left; opacity: 0;
      animation: intro-up 0.8s ease-out forwards;
  }}
  .intro-card-title {{ font-weight: 700; color: {t['text']}; margin-bottom: 6px; }}
  .intro-card-text {{ font-size: 14px; color: {t['muted']}; line-height: 1.45; }}

  @keyframes intro-up {{
      from {{ opacity: 0; transform: translateY(14px); }}
      to   {{ opacity: 1; transform: translateY(0); }}
  }}
  @keyframes intro-draw {{
      0%   {{ stroke-dashoffset: 900; }}
      60%  {{ stroke-dashoffset: 0; }}
      100% {{ stroke-dashoffset: -900; }}
  }}
  @keyframes intro-pulse {{
      0%, 100% {{ transform: scale(1);    box-shadow: 0 0 0 0 {t['accent']}55; }}
      15%      {{ transform: scale(1.12); }}
      30%      {{ transform: scale(1);    box-shadow: 0 0 0 18px {t['accent']}00; }}
  }}
  /* Respect visitors who prefer less motion */
  @media (prefers-reduced-motion: reduce) {{
      .intro *, .intro {{ animation: none !important; opacity: 1 !important; }}
      .intro-ecg path {{ stroke-dashoffset: 0; }}
  }}
</style>

<div class="intro">
  <div class="intro-heart">♥</div>
  <svg class="intro-ecg" viewBox="0 0 640 70" aria-hidden="true">
    <path d="M0 40 H170 L190 40 L205 18 L220 58 L240 6 L258 64 L272 40 H360
             L375 32 L390 40 H470 L485 40 L500 20 L515 56 L532 10 L548 62 L560 40 H640"/>
  </svg>
  <div class="intro-title">Healthcare Intelligence System</div>
  <div class="intro-sub">
    Health education, clinical analytics and AI, built by a nurse,
    for learning and better care.
  </div>

  <div class="intro-tip">
    <div class="intro-tip-label">HEALTH TIP</div>
    <div class="intro-tip-text">{st.session_state.tip}</div>
  </div>

  <div class="intro-cards">{cards}</div>
</div>
""")

    left, middle, right = st.columns([1, 1, 1])
    with middle:
        if st.button("Enter the website →", type="primary", width="stretch"):
            st.session_state.entered = True
            st.rerun()

    st.caption(
        "For education and demonstration only. Not a substitute for "
        "professional medical advice."
    )