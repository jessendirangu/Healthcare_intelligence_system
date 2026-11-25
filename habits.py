"""Healthy habits: daily check-in with streaks, Kenyan food guide, myth-or-fact
quiz, and reminders added to the phone's own calendar.

Salt guidance: WHO recommends adults eat less than 5 g of salt a day (just
under one teaspoon). Food guide follows the healthy-plate idea: half
vegetables, a quarter starch, a quarter protein.
"""

import uuid
from datetime import date, datetime, timedelta, timezone

import pandas as pd
import streamlit as st

import chp_store as store
import demo
import i18n
from i18n import t

HABITS = ["salt", "active", "veg", "no_tobacco", "medicine"]

i18n.register({
    "hb_title": {"en": "Healthy habits", "sw": "Tabia za afya"},
    "hb_intro": {
        "en": "Small daily habits protect you from high blood pressure, diabetes and heart disease.",
        "sw": "Tabia ndogo za kila siku zinakulinda dhidi ya shinikizo la juu la damu, kisukari na magonjwa ya moyo.",
    },
    "hb_tab_daily": {"en": "🔥 Daily challenge", "sw": "🔥 Changamoto ya kila siku"},
    "hb_tab_food": {"en": "🥬 Food guide", "sw": "🥬 Mwongozo wa chakula"},
    "hb_tab_quiz": {"en": "❓ Myth or fact?", "sw": "❓ Uongo au kweli?"},
    "hb_tab_remind": {"en": "⏰ Reminders", "sw": "⏰ Vikumbusho"},

    # Daily challenge
    "hb_today": {"en": "What did you do today?", "sw": "Umefanya nini leo?"},
    "hb_salt": {"en": "🧂 Ate less salt (no extra salt at the table)", "sw": "🧂 Nimekula chumvi kidogo (bila kuongeza chumvi mezani)"},
    "hb_active": {"en": "🚶 Active for 30 minutes (walking, farming, sports)", "sw": "🚶 Nimefanya mazoezi dakika 30 (kutembea, kulima, michezo)"},
    "hb_veg": {"en": "🥬 Ate vegetables or fruit", "sw": "🥬 Nimekula mboga au matunda"},
    "hb_no_tobacco": {"en": "🚭 No tobacco, and little or no alcohol", "sw": "🚭 Bila tumbaku, na pombe kidogo au bila pombe"},
    "hb_medicine": {"en": "💊 Took my medicine (if I have any)", "sw": "💊 Nimemeza dawa yangu (kama ninazo)"},
    "hb_save": {"en": "Save today", "sw": "Hifadhi leo"},
    "hb_saved": {"en": "Saved! Well done. 👏", "sw": "Imehifadhiwa! Hongera. 👏"},
    "hb_streak": {"en": "Day streak", "sw": "Siku mfululizo"},
    "hb_streak_help": {
        "en": "Days in a row you have checked in with at least one healthy habit.",
        "sw": "Siku mfululizo ulizoandika angalau tabia moja ya afya.",
    },
    "hb_week": {"en": "Healthy habits this week", "sw": "Tabia za afya wiki hii"},
    "hb_best": {"en": "Best day this week", "sw": "Siku bora wiki hii"},
    "hb_chart": {"en": "Days you did each habit (last 7 days)", "sw": "Siku ulizofanya kila tabia (siku 7 zilizopita)"},
    "hb_cheer_0": {"en": "Start today. One small habit is enough to begin.", "sw": "Anza leo. Tabia moja ndogo inatosha kuanza."},
    "hb_cheer_3": {"en": "Great start! Keep going. 🔥", "sw": "Mwanzo mzuri! Endelea. 🔥"},
    "hb_cheer_7": {"en": "A full week! You're building a habit. 🌟", "sw": "Wiki nzima! Unajenga tabia. 🌟"},
    "hb_cheer_30": {"en": "30 days or more! This is now part of your life. 🏆", "sw": "Siku 30 au zaidi! Sasa ni sehemu ya maisha yako. 🏆"},
    "hb_db": {"en": "Couldn't reach the server. Please try again.", "sw": "Imeshindikana kufikia seva. Tafadhali jaribu tena."},

    # Food guide
    "hb_green": {"en": "🟢 Eat often", "sw": "🟢 Kula mara nyingi"},
    "hb_amber": {"en": "🟡 Eat in moderation", "sw": "🟡 Kula kwa kiasi"},
    "hb_red": {"en": "🔴 Limit", "sw": "🔴 Punguza"},
    "hb_green_list": {
        "en": "Sukuma wiki, managu, terere, kunde, cabbage, tomatoes · beans, ndengu, githeri, njahi · fish "
              "(fresh or omena), eggs · sweet potatoes, nduma, arrowroots · ugali from whole maize, brown rice · "
              "fruit: bananas, oranges, pawpaw, mangoes, avocado · water",
        "sw": "Sukuma wiki, managu, terere, kunde, kabichi, nyanya · maharagwe, ndengu, githeri, njahi · samaki "
              "(wabichi au omena), mayai · viazi vitamu, nduma, nduma za maji · ugali wa mahindi yasiyokobolewa, "
              "wali wa kahawia · matunda: ndizi, machungwa, papai, maembe, parachichi · maji",
    },
    "hb_amber_list": {
        "en": "Chapati, white rice, white bread, sifted ugali · chicken, beef, goat (without much fat) · milk, "
              "mursik, yoghurt · tea with little or no sugar · cooking oil (a little)",
        "sw": "Chapati, wali mweupe, mkate mweupe, ugali wa sembe · kuku, nyama ya ng'ombe, mbuzi (bila mafuta "
              "mengi) · maziwa, mursik, mtindi · chai yenye sukari kidogo au bila sukari · mafuta ya kupikia (kidogo)",
    },
    "hb_red_list": {
        "en": "Chips, mandazi and other deep-fried food · soda, juice with added sugar · sausages, smokies, "
              "processed meat · crisps and salty snacks · stock cubes and seasoning powders · lots of sugar in tea · "
              "alcohol",
        "sw": "Chipsi, mandazi na vyakula vingine vya kukaanga · soda, juisi yenye sukari · soseji, smokies, nyama "
              "iliyosindikwa · crisps na vitafunio vyenye chumvi · vidonge vya supu na unga wa viungo · sukari "
              "nyingi kwenye chai · pombe",
    },
    "hb_salt_fact": {
        "en": "**WHO advice:** adults should eat less than 5 g of salt a day, just under one teaspoon in total. "
              "Most people eat about double that.",
        "sw": "**Ushauri wa WHO:** watu wazima wanapaswa kula chini ya gramu 5 za chumvi kwa siku, chini kidogo "
              "ya kijiko kimoja cha chai kwa jumla. Watu wengi hula karibu mara mbili ya hiyo.",
    },

    # Quiz
    "hb_q_intro": {"en": "Is each sentence a myth or a fact? Choose, then check your answers.",
                   "sw": "Je, kila sentensi ni uongo au kweli? Chagua, kisha angalia majibu yako."},
    "hb_myth": {"en": "Myth", "sw": "Uongo"},
    "hb_fact": {"en": "Fact", "sw": "Kweli"},
    "hb_check": {"en": "Check my answers", "sw": "Angalia majibu yangu"},
    "hb_score": {"en": "You got **{n} out of {total}** right.", "sw": "Umepata **{n} kati ya {total}** sahihi."},
    "hb_right": {"en": "✅ Correct", "sw": "✅ Sahihi"},
    "hb_wrong": {"en": "❌ Not quite. The answer is: {a}", "sw": "❌ Si sahihi. Jibu ni: {a}"},
    "hb_unanswered": {"en": "Answer all questions first.", "sw": "Jibu maswali yote kwanza."},

    # Reminders
    "hb_r_intro": {
        "en": "Add a repeating reminder to your phone's calendar. It will ring even when this website is "
              "closed and even without internet.",
        "sw": "Ongeza kikumbusho kinachojirudia kwenye kalenda ya simu yako. Kitalia hata tovuti hii ikiwa "
              "imefungwa na hata bila intaneti.",
    },
    "hb_r_what": {"en": "Reminder", "sw": "Kikumbusho"},
    "hb_r_med": {"en": "💊 Take my medicine (every day)", "sw": "💊 Meza dawa yangu (kila siku)"},
    "hb_r_bp": {"en": "🩺 Check my blood pressure (every week)", "sw": "🩺 Pima shinikizo la damu (kila wiki)"},
    "hb_r_walk": {"en": "🚶 Go for a 30-minute walk (every day)", "sw": "🚶 Tembea dakika 30 (kila siku)"},
    "hb_r_time": {"en": "Time", "sw": "Saa"},
    "hb_r_download": {"en": "📅 Add to my calendar", "sw": "📅 Ongeza kwenye kalenda yangu"},
    "hb_r_how": {
        "en": "Tap the button, then open the downloaded file. Your phone will ask to add it to your calendar.",
        "sw": "Bonyeza kitufe, kisha fungua faili iliyopakuliwa. Simu yako itauliza kuiongeza kwenye kalenda.",
    },
})

# (statement, is_fact, explanation) in English and Kiswahili
QUIZ = [
    (("I feel fine, so my blood pressure must be normal.", "Najisikia vizuri, kwa hiyo shinikizo langu la damu ni la kawaida."),
     False,
     ("High blood pressure usually has no symptoms. The only way to know is to measure it.",
      "Shinikizo la juu la damu mara nyingi halina dalili. Njia pekee ya kujua ni kupima.")),
    (("Once my blood pressure is normal, I can stop my medicine.", "Shinikizo likiwa la kawaida, naweza kuacha dawa."),
     False,
     ("It is normal *because* of the medicine. Never stop without talking to your health worker.",
      "Liko la kawaida *kwa sababu* ya dawa. Usiache bila kuzungumza na mhudumu wako wa afya.")),
    (("Eating less salt can lower blood pressure.", "Kula chumvi kidogo kunaweza kushusha shinikizo la damu."),
     True,
     ("Yes. WHO advises less than 5 g of salt a day, just under one teaspoon.",
      "Ndiyo. WHO inashauri chini ya gramu 5 za chumvi kwa siku, chini kidogo ya kijiko kimoja cha chai.")),
    (("Only people who eat a lot of sugar get diabetes.", "Ni watu wanaokula sukari nyingi tu wanaopata kisukari."),
     False,
     ("Weight, inactivity, age and family history all raise the risk of type 2 diabetes.",
      "Uzito, kutofanya mazoezi, umri na historia ya familia vyote huongeza hatari ya kisukari aina ya 2.")),
    (("Walking 30 minutes a day lowers the risk of diabetes and heart disease.",
      "Kutembea dakika 30 kwa siku hupunguza hatari ya kisukari na magonjwa ya moyo."),
     True,
     ("Yes. Regular activity helps control weight, blood sugar and blood pressure.",
      "Ndiyo. Mazoezi ya mara kwa mara husaidia kudhibiti uzito, sukari na shinikizo la damu.")),
    (("Herbal remedies can replace hospital medicine for high blood pressure.",
      "Dawa za mitishamba zinaweza kuchukua nafasi ya dawa za hospitali za shinikizo la damu."),
     False,
     ("They are not proven to control blood pressure. Keep taking prescribed medicine and tell your health worker about any herbs you use.",
      "Hazijathibitishwa kudhibiti shinikizo la damu. Endelea na dawa ulizoandikiwa na umweleze mhudumu wa afya kuhusu mitishamba unayotumia.")),
    (("Only old people get high blood pressure.", "Ni wazee tu wanaopata shinikizo la juu la damu."),
     False,
     ("Young adults get it too, especially with overweight, salty food, alcohol or a family history.",
      "Vijana pia hupata, hasa wakiwa na uzito mkubwa, chakula chenye chumvi, pombe au historia ya familia.")),
    (("Untreated high blood pressure can damage the heart, brain, kidneys and eyes.",
      "Shinikizo la juu lisilotibiwa linaweza kuharibu moyo, ubongo, figo na macho."),
     True,
     ("Yes. It is a leading cause of stroke, heart attack and kidney failure.",
      "Ndiyo. Ni chanzo kikuu cha kiharusi, mshtuko wa moyo na figo kushindwa kufanya kazi.")),
    (("A child with diarrhoea should stop drinking and breastfeeding.",
      "Mtoto anayeharisha anapaswa kuacha kunywa na kunyonya."),
     False,
     ("The opposite: give more fluids, ORS and zinc, and keep breastfeeding.",
      "Kinyume chake: mpe maji zaidi, ORS na zinki, na endelea kunyonyesha.")),
    (("Fast breathing in a young child can be a sign of pneumonia.",
      "Kupumua haraka kwa mtoto mdogo kunaweza kuwa dalili ya nimonia."),
     True,
     ("Yes. Count the breaths for one minute and go to a clinic if it is fast.",
      "Ndiyo. Hesabu pumzi kwa dakika moja na uende kliniki kama ni haraka.")),
]


def _pick(pair):
    return pair[1] if i18n.lang() == "sw" else pair[0]


# ---------------------------------------------------------------
# Streaks and calendar files
# ---------------------------------------------------------------

def streak(days, today):
    """Number of days in a row with a check-in, ending today (or yesterday, if today isn't done yet)."""
    done = set(days)
    start = today if today in done else today - timedelta(days=1)
    count = 0
    while start - timedelta(days=count) in done:
        count += 1
    return count


def calendar_file(title, start_local, weekly=False):
    """An .ics calendar file with a repeating event and an alarm at the start time."""
    start = start_local.astimezone(timezone.utc)
    end = start + timedelta(minutes=10)
    fmt = "%Y%m%dT%H%M%SZ"
    lines = [
        "BEGIN:VCALENDAR", "VERSION:2.0", "PRODID:-//Healthcare Intelligence System//EN",
        "BEGIN:VEVENT",
        f"UID:{uuid.uuid4()}@healthcare-intelligence",
        f"DTSTAMP:{datetime.now(timezone.utc):{fmt}}",
        f"DTSTART:{start:{fmt}}", f"DTEND:{end:{fmt}}",
        f"RRULE:FREQ={'WEEKLY' if weekly else 'DAILY'}",
        f"SUMMARY:{title}",
        "BEGIN:VALARM", "ACTION:DISPLAY", f"DESCRIPTION:{title}", "TRIGGER:PT0M", "END:VALARM",
        "END:VEVENT", "END:VCALENDAR",
    ]
    return "\r\n".join(lines) + "\r\n"


# ---------------------------------------------------------------
# Tabs
# ---------------------------------------------------------------

def _daily(owner):
    today = i18n.local_now().date()
    try:
        logs = store.habit_logs(owner)
    except Exception:
        st.error(t("hb_db"))
        return
    by_day = {date.fromisoformat(str(r["day"])[:10]): (r["habits"] or "").split(",") for r in logs}
    done_today = by_day.get(today, [])

    with st.form("habits_today"):
        st.markdown(f"**{t('hb_today')}**")
        ticked = [h for h in HABITS if st.checkbox(t("hb_" + h), value=h in done_today, key=f"hb_{h}")]
        if st.form_submit_button(t("hb_save"), type="primary", width="stretch"):
            try:
                store.save_habits(owner, today.isoformat(), ticked)
                st.session_state.hb_flash = t("hb_saved")
                st.rerun()
            except Exception:
                st.error(t("hb_db"))
    if "hb_flash" in st.session_state:
        st.success(st.session_state.pop("hb_flash"))

    active_days = [d for d, h in by_day.items() if any(h)]
    days_in_row = streak(active_days, today)
    week = [today - timedelta(days=k) for k in range(7)]
    week_total = sum(len([h for h in by_day.get(d, []) if h]) for d in week)

    c1, c2 = st.columns(2)
    c1.metric(t("hb_streak"), f"🔥 {days_in_row}", help=t("hb_streak_help"))
    c2.metric(t("hb_week"), f"{week_total} / {7 * len(HABITS)}")
    cheer = "hb_cheer_30" if days_in_row >= 30 else "hb_cheer_7" if days_in_row >= 7 else \
        "hb_cheer_3" if days_in_row >= 1 else "hb_cheer_0"
    st.info(t(cheer))

    counts = pd.Series({t("hb_" + h): sum(h in by_day.get(d, []) for d in week) for h in HABITS},
                       name=t("hb_chart"))
    st.caption(t("hb_chart"))
    st.bar_chart(counts, horizontal=True, color="#2F7D6D")


def _food():
    st.info(t("hb_salt_fact"))
    with st.expander(demo.watch_label() + " · " + demo._pick(demo.DEMOS["plate"]["title"]), expanded=True):
        demo.show("plate")
    for colour, box in (("green", st.success), ("amber", st.warning), ("red", st.error)):
        box(f"**{t('hb_' + colour)}**\n\n{t('hb_' + colour + '_list')}")
    with st.expander(demo.watch_label() + " · " + demo._pick(demo.DEMOS["salt"]["title"])):
        demo.show("salt")


def _quiz():
    st.write(t("hb_q_intro"))
    answers = []
    for k, (statement, _, _) in enumerate(QUIZ):
        choice = st.radio(f"{k + 1}. {_pick(statement)}", ["myth", "fact"], index=None,
                          format_func=lambda c: t("hb_" + c), horizontal=True, key=f"hb_q{k}")
        answers.append(choice)
    if not st.button(t("hb_check"), type="primary", width="stretch"):
        return
    if None in answers:
        st.warning(t("hb_unanswered"))
        return
    score = 0
    for k, ((statement, is_fact, explanation), choice) in enumerate(zip(QUIZ, answers)):
        correct = (choice == "fact") == is_fact
        score += correct
        verdict = t("hb_right") if correct else t("hb_wrong", a=t("hb_fact" if is_fact else "hb_myth"))
        (st.success if correct else st.error)(f"**{k + 1}. {verdict}.** {_pick(explanation)}")
    st.metric("🏅", t("hb_score", n=score, total=len(QUIZ)).replace("**", ""))
    if score == len(QUIZ):
        st.balloons()


def _reminders():
    st.write(t("hb_r_intro"))
    kind = st.radio(t("hb_r_what"), ["med", "bp", "walk"], format_func=lambda k: t("hb_r_" + k), key="hb_r_kind")
    when = st.time_input(t("hb_r_time"), value=datetime.strptime("08:00", "%H:%M").time(), step=900,
                         key="hb_r_time")
    title = t("hb_r_" + kind).split(" (")[0].split(" ", 1)[1]  # text without emoji and repeat note
    tomorrow = i18n.local_now().date() + timedelta(days=1)
    start = datetime.combine(tomorrow, when, tzinfo=i18n.user_tz())
    ics = calendar_file(title, start, weekly=(kind == "bp"))
    st.download_button(t("hb_r_download"), ics.encode("utf-8"), file_name=f"reminder_{kind}.ics",
                       mime="text/calendar", type="primary", width="stretch")
    st.caption(t("hb_r_how"))


def render(owner):
    st.header(t("hb_title"))
    st.write(t("hb_intro"))
    daily, food, quiz, remind = st.tabs([t("hb_tab_daily"), t("hb_tab_food"), t("hb_tab_quiz"), t("hb_tab_remind")])
    with daily:
        _daily(owner)
    with food:
        _food()
    with quiz:
        _quiz()
    with remind:
        _reminders()