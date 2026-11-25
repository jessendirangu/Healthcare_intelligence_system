"""Measure with your hands: pulse, a child's breathing, and a child's arm (MUAC).

No machine needed, just fingers, a timer and a tape or string.

Cut-offs used:
- Adult resting pulse: 60-100 beats a minute is normal. Above 100 at rest is
  fast, below 60 is slow (can be normal for fit people). An irregular beat,
  or any abnormal pulse with chest pain, fainting or breathlessness, needs care.
- Child breathing (WHO IMCI): fast if 60+ under 2 months, 50+ at 2-12 months,
  40+ at 1-5 years.
- MUAC, children 6-59 months (WHO/UNICEF 2009): below 11.5 cm = severe acute
  malnutrition; 11.5 to 12.4 cm = moderate; 12.5 cm or more = normal.
  Swelling (pitting oedema) of both feet = severe acute malnutrition.
"""

import streamlit as st

import demo
import i18n
from i18n import t
from storage import save_reading

i18n.register({
    "yes": {"en": "Yes", "sw": "Ndiyo"},
    "no": {"en": "No", "sw": "Hapana"},
    "ms_title": {"en": "Measure with your hands", "sw": "Pima kwa mikono yako"},
    "ms_intro": {
        "en": "No machine needed: just your fingers, a timer and a tape or string. Watch the "
              "demonstration first, then measure.",
        "sw": "Hakuna kifaa kinachohitajika: vidole vyako, kipima muda na tepu au kamba tu. Tazama "
              "maonyesho kwanza, kisha upime.",
    },
    "ms_tab_pulse": {"en": "❤️ Pulse", "sw": "❤️ Mapigo ya moyo"},
    "ms_tab_breath": {"en": "🫁 Child's breathing", "sw": "🫁 Pumzi za mtoto"},
    "ms_tab_muac": {"en": "📏 Child's arm (MUAC)", "sw": "📏 Mkono wa mtoto (MUAC)"},

    # Pulse
    "ms_pulse_for": {"en": "For adults (18 years and over), sitting and rested.",
                     "sw": "Kwa watu wazima (miaka 18 na zaidi), wakiwa wamekaa na kupumzika."},
    "ms_beats30": {"en": "Beats you counted in 30 seconds", "sw": "Mapigo uliyohesabu kwa sekunde 30"},
    "ms_irregular": {"en": "The beat felt irregular (uneven, skipping or fluttering)",
                     "sw": "Mapigo hayakuwa sawa (yanaruka, hayana mpangilio au yanapepesuka)"},
    "ms_symptoms": {"en": "I also have chest pain, fainting or severe breathlessness",
                    "sw": "Pia nina maumivu ya kifua, kuzimia au shida kubwa ya kupumua"},
    "ms_result_bpm": {"en": "Your pulse: **{bpm} beats a minute**", "sw": "Mapigo yako: **{bpm} kwa dakika**"},
    "ms_p_emergency": {
        "en": "**Go to emergency now.** Chest pain, fainting or severe breathlessness with an "
              "abnormal pulse can be serious. Call 999 or 112.",
        "sw": "**Nenda kwenye huduma ya dharura sasa.** Maumivu ya kifua, kuzimia au shida kubwa ya "
              "kupumua pamoja na mapigo yasiyo ya kawaida inaweza kuwa hatari. Piga 999 au 112.",
    },
    "ms_p_normal": {"en": "**Normal.** A resting pulse of 60 to 100 is healthy.",
                    "sw": "**Kawaida.** Mapigo ya 60 hadi 100 ukiwa umepumzika ni mazuri."},
    "ms_p_slow": {
        "en": "**Slower than usual.** This can be normal for very fit people. If you feel dizzy, "
              "faint or tired, see a health worker.",
        "sw": "**Polepole kuliko kawaida.** Hii inaweza kuwa kawaida kwa watu wenye mazoezi mengi. "
              "Ukihisi kizunguzungu, kuzimia au uchovu, muone mhudumu wa afya.",
    },
    "ms_p_fast": {
        "en": "**Fast for resting.** Rest for 10 minutes and measure again. Fever, worry, coffee or "
              "dehydration can raise it. If it stays above 100, see a health worker.",
        "sw": "**Haraka kwa mtu aliyepumzika.** Pumzika dakika 10 kisha upime tena. Homa, wasiwasi, "
              "kahawa au upungufu wa maji vinaweza kuyaongeza. Yakibaki zaidi ya 100, muone mhudumu wa afya.",
    },
    "ms_p_very": {
        "en": "**Very fast or very slow.** Please see a health worker today.",
        "sw": "**Haraka sana au polepole sana.** Tafadhali muone mhudumu wa afya leo.",
    },
    "ms_p_irregular": {
        "en": "An irregular beat should be checked by a health worker. It can be a sign of a heart "
              "rhythm problem that raises the risk of stroke.",
        "sw": "Mapigo yasiyo na mpangilio yanapaswa kuchunguzwa na mhudumu wa afya. Yanaweza kuwa "
              "dalili ya tatizo la mpangilio wa moyo linaloongeza hatari ya kiharusi.",
    },
    "ms_save": {"en": "Save to My health tracker", "sw": "Hifadhi kwenye Kifuatilia afya yangu"},
    "ms_saved": {"en": "Saved to your tracker.", "sw": "Imehifadhiwa kwenye kifuatilia chako."},
    "ms_save_failed": {"en": "Couldn't save just now. Please try again.",
                       "sw": "Imeshindikana kuhifadhi sasa. Tafadhali jaribu tena."},
    "ms_check": {"en": "Check", "sw": "Angalia"},

    # Breathing
    "ms_b_age": {"en": "Child's age", "sw": "Umri wa mtoto"},
    "ms_b_infant": {"en": "Under 2 months", "sw": "Chini ya miezi 2"},
    "ms_b_small": {"en": "2 to 12 months", "sw": "Miezi 2 hadi 12"},
    "ms_b_big": {"en": "1 to 5 years", "sw": "Mwaka 1 hadi miaka 5"},
    "ms_b_count": {"en": "Breaths you counted in 60 seconds", "sw": "Pumzi ulizohesabu kwa sekunde 60"},
    "ms_b_fast_infant": {
        "en": "**Fast breathing ({n} a minute) in a baby under 2 months is a danger sign. Go to a "
              "health facility now.**",
        "sw": "**Kupumua haraka (mara {n} kwa dakika) kwa mtoto chini ya miezi 2 ni dalili ya hatari. "
              "Nenda kituo cha afya sasa.**",
    },
    "ms_b_fast": {
        "en": "**Fast breathing ({n} a minute).** This can be a sign of pneumonia. Take the child to "
              "a clinic today. Go now if the lower chest sucks in, or the child can't drink.",
        "sw": "**Kupumua haraka (mara {n} kwa dakika).** Hii inaweza kuwa dalili ya nimonia. Mpeleke "
              "mtoto kliniki leo. Nenda sasa kama sehemu ya chini ya kifua inaingia ndani, au mtoto "
              "hawezi kunywa.",
    },
    "ms_b_normal": {
        "en": "**Not fast breathing ({n} a minute)** for this age. Keep watching. Use *Danger signs* "
              "to check for other signs.",
        "sw": "**Si kupumua haraka (mara {n} kwa dakika)** kwa umri huu. Endelea kuangalia. Tumia "
              "*Dalili za hatari* kuangalia dalili nyingine.",
    },
    "ms_b_practice": {"en": "Practise first with an animated baby", "sw": "Fanya mazoezi kwanza na mtoto wa picha"},

    # MUAC
    "ms_m_for": {
        "en": "For children aged 6 months to 5 years. Use a MUAC tape (free from health facilities "
              "and CHPs), or a string and a ruler.",
        "sw": "Kwa watoto wa miezi 6 hadi miaka 5. Tumia tepu ya MUAC (bure kutoka vituo vya afya na "
              "wahudumu wa afya ya jamii), au kamba na rula.",
    },
    "ms_m_cm": {"en": "Arm measurement (cm)", "sw": "Kipimo cha mkono (cm)"},
    "ms_m_oedema": {"en": "When you press both feet for 3 seconds, does a dent stay on BOTH feet?",
                    "sw": "Ukibonyeza nyayo zote mbili kwa sekunde 3, je, shimo linabaki kwenye nyayo ZOTE mbili?"},
    "ms_m_red": {
        "en": "**Severe acute malnutrition. Go to a health facility now.** This child needs urgent "
              "treatment, which is usually free. Keep breastfeeding and offering food on the way.",
        "sw": "**Utapiamlo mkali. Nenda kituo cha afya sasa.** Mtoto huyu anahitaji matibabu ya haraka, "
              "ambayo mara nyingi ni bure. Endelea kunyonyesha na kumpa chakula njiani.",
    },
    "ms_m_amber": {
        "en": "**Moderate acute malnutrition.** Take the child to a clinic this week for a nutrition "
              "check and support. Feed small meals often, with beans, eggs, milk, fish, meat, "
              "vegetables and fruit.",
        "sw": "**Utapiamlo wa wastani.** Mpeleke mtoto kliniki wiki hii kwa uchunguzi na msaada wa lishe. "
              "Mlishe milo midogo mara nyingi, yenye maharagwe, mayai, maziwa, samaki, nyama, mboga na matunda.",
    },
    "ms_m_green": {
        "en": "**Good.** The arm measurement is in the healthy range. Keep weighing the child at "
              "clinic visits.",
        "sw": "**Vizuri.** Kipimo cha mkono kiko katika kiwango kizuri. Endelea kumpima mtoto uzito "
              "kila unapoenda kliniki.",
    },
    "ms_m_about": {
        "en": "Cut-offs from WHO and UNICEF for children 6-59 months: below 11.5 cm severe, 11.5-12.4 cm "
              "moderate. For babies under 6 months, MUAC is not used: ask a health worker to check weight.",
        "sw": "Viwango kutoka WHO na UNICEF kwa watoto wa miezi 6-59: chini ya cm 11.5 ni mkali, cm "
              "11.5-12.4 ni wa wastani. Kwa watoto chini ya miezi 6, MUAC haitumiki: mwombe mhudumu wa afya apime uzito.",
    },
})


# ---------------------------------------------------------------
# Rules
# ---------------------------------------------------------------

def pulse_result(bpm, irregular=False, symptoms=False):
    """Returns (level, message keys). Levels: red, amber, green."""
    if symptoms:  # chest pain, fainting or severe breathlessness is always an emergency
        return "red", ["ms_p_emergency"]
    if bpm < 40 or bpm > 130:
        keys, level = ["ms_p_very"], "amber"
    elif bpm > 100:
        keys, level = ["ms_p_fast"], "amber"
    elif bpm < 60:
        keys, level = ["ms_p_slow"], ("green" if bpm >= 50 else "amber")
    else:
        keys, level = ["ms_p_normal"], "green"
    if irregular:
        keys.append("ms_p_irregular")
        level = "amber"
    return level, keys


BREATH_CUTOFF = {"infant": 60, "small": 50, "big": 40}


def breathing_result(age_band, breaths):
    if breaths >= BREATH_CUTOFF[age_band]:
        return ("red", "ms_b_fast_infant") if age_band == "infant" else ("amber", "ms_b_fast")
    return "green", "ms_b_normal"


def muac_result(cm, oedema):
    if oedema or cm < 11.5:
        return "red", "ms_m_red"
    if cm < 12.5:
        return "amber", "ms_m_amber"
    return "green", "ms_m_green"


BOX = {"red": st.error, "amber": st.warning, "green": st.success}


# ---------------------------------------------------------------
# Page
# ---------------------------------------------------------------

def _pulse(owner):
    st.caption(t("ms_pulse_for"))
    with st.expander(demo.watch_label(), expanded=True):
        demo.show("pulse")
    demo.timer(30)
    beats = st.number_input(t("ms_beats30"), 5, 120, value=None, key="ms_beats")
    irregular = st.checkbox(t("ms_irregular"), key="ms_irr")
    symptoms = st.checkbox(t("ms_symptoms"), key="ms_sym")
    if st.button(t("ms_check"), type="primary", width="stretch", key="ms_pulse_btn") and beats:
        st.session_state.ms_last_bpm = beats * 2
    bpm = st.session_state.get("ms_last_bpm")
    if not bpm:
        return
    level, keys = pulse_result(bpm, irregular, symptoms)
    BOX[level](t("ms_result_bpm", bpm=bpm) + "\n\n" + "\n\n".join(t(k) for k in keys))
    if st.button(t("ms_save"), key="ms_save_btn"):
        try:
            save_reading({"owner": owner, "taken_at": i18n.local_now().isoformat(), "pulse": bpm,
                          "note": "pulse by hand"})
            st.success(t("ms_saved"))
            st.session_state.pop("ms_last_bpm")
        except Exception:
            st.error(t("ms_save_failed"))


def _breathing():
    band = st.radio(t("ms_b_age"), ["infant", "small", "big"],
                    format_func=lambda b: t("ms_b_" + b), horizontal=True, key="ms_band")
    with st.expander(demo.watch_label()):
        demo.show("child_breathing")
    with st.expander(t("ms_b_practice")):
        demo.breathing_practice()
    demo.timer(60)
    breaths = st.number_input(t("ms_b_count"), 5, 150, value=None, key="ms_breaths")
    if st.button(t("ms_check"), type="primary", width="stretch", key="ms_breath_btn") and breaths:
        level, key = breathing_result(band, breaths)
        BOX[level](t(key, n=breaths))


def _muac():
    st.caption(t("ms_m_for"))
    with st.expander(demo.watch_label(), expanded=True):
        demo.show("muac")
    cm = st.number_input(t("ms_m_cm"), 5.0, 30.0, value=None, step=0.1, format="%.1f", key="ms_cm")
    oedema = st.radio(t("ms_m_oedema"), ["no", "yes"], format_func=t, horizontal=True,
                      key="ms_oed") == "yes"
    if st.button(t("ms_check"), type="primary", width="stretch", key="ms_muac_btn") and (cm or oedema):
        level, key = muac_result(cm if cm else 99, oedema)
        BOX[level](t(key))
    st.caption(t("ms_m_about"))


def render(owner):
    st.header(t("ms_title"))
    st.write(t("ms_intro"))
    pulse_tab, breath_tab, muac_tab = st.tabs([t("ms_tab_pulse"), t("ms_tab_breath"), t("ms_tab_muac")])
    with pulse_tab:
        _pulse(owner)
    with breath_tab:
        _breathing()
    with muac_tab:
        _muac()