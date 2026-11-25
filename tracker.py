"""My health tracker.

Each signed-in user records their own blood pressure, pulse, weight and blood
sugar, then sees trends and plain-language guidance in English or Kiswahili.

Clinical cut-offs used (adults):
- Blood pressure: International Society of Hypertension (ISH) 2020 guideline.
  Normal <130/85, high-normal 130-139/85-89, grade 1 hypertension 140-159/90-99,
  grade 2 >=160/100. Readings >=180/110 need same-day care.
- Blood sugar (mmol/L): WHO. Fasting: normal <6.1, raised 6.1-6.9, high >=7.0.
  Random/after a meal: normal <7.8, raised 7.8-11.0, high >=11.1. Low <3.9.

The page gives general guidance only. It never diagnoses: a high average is
a reason to see a health worker, who confirms hypertension or diabetes.
"""

from datetime import datetime, timedelta

import altair as alt
import pandas as pd
import streamlit as st

import demo
import i18n
from i18n import t
from storage import delete_reading, load_readings, save_reading

HIGH_SYS, HIGH_DIA = 140, 90

i18n.register({
    "tr_title": {"en": "My health tracker", "sw": "Kifuatilia afya yangu"},
    "tr_intro": {
        "en": "Record your blood pressure, pulse, weight and blood sugar. You'll see your "
              "trends and what they mean. Only you can see your readings.",
        "sw": "Weka vipimo vyako vya shinikizo la damu, mapigo ya moyo, uzito na sukari "
              "kwenye damu. Utaona mwenendo wako na maana yake. Ni wewe pekee unayeona vipimo vyako.",
    },
    "tr_why": {
        "en": "Why track your blood pressure? High blood pressure usually has no symptoms. "
              "Many people only find out after a stroke or heart attack. Regular readings "
              "catch it early, when it is easier to treat.",
        "sw": "Kwa nini ufuatilie shinikizo la damu? Shinikizo la juu la damu mara nyingi "
              "halina dalili. Watu wengi hugundua baada ya kupata kiharusi au mshtuko wa moyo. "
              "Kupima mara kwa mara hukigundua mapema, wakati ni rahisi kutibu.",
    },
    "tr_add": {"en": "Add a reading", "sw": "Weka kipimo kipya"},
    "tr_date": {"en": "Date", "sw": "Tarehe"},
    "tr_time": {"en": "Time", "sw": "Saa"},
    "tr_systolic": {"en": "Systolic BP (top number)", "sw": "BP ya juu (systolic)"},
    "tr_diastolic": {"en": "Diastolic BP (bottom number)", "sw": "BP ya chini (diastolic)"},
    "tr_bp_help": {
        "en": "In mmHg. A reading of 128/82 means systolic 128 and diastolic 82.",
        "sw": "Kwa mmHg. Kipimo cha 128/82 maana yake ya juu ni 128 na ya chini ni 82.",
    },
    "tr_pulse": {"en": "Pulse (beats per minute)", "sw": "Mapigo ya moyo (kwa dakika)"},
    "tr_weight": {"en": "Weight (kg)", "sw": "Uzito (kg)"},
    "tr_sugar": {"en": "Blood sugar (mmol/L)", "sw": "Sukari kwenye damu (mmol/L)"},
    "tr_sugar_help": {
        "en": "Leave blank if you didn't test. If your meter shows mg/dL, divide by 18.",
        "sw": "Acha wazi kama hukupima. Kama kipimo chako kinaonyesha mg/dL, gawanya kwa 18.",
    },
    "tr_sugar_kind": {"en": "Sugar test type", "sw": "Aina ya kipimo cha sukari"},
    "tr_fasting": {"en": "Fasting (no food for 8 hours)", "sw": "Bila kula (saa 8 bila chakula)"},
    "tr_random": {"en": "Random / after a meal", "sw": "Wakati wowote / baada ya kula"},
    "tr_note": {"en": "Note (optional)", "sw": "Maelezo (si lazima)"},
    "tr_note_ph": {
        "en": "e.g. took medicine, felt dizzy, after exercise",
        "sw": "mf. nimekunywa dawa, nilihisi kizunguzungu, baada ya mazoezi",
    },
    "tr_save": {"en": "Save reading", "sw": "Hifadhi kipimo"},
    "tr_saved": {"en": "Reading saved.", "sw": "Kipimo kimehifadhiwa."},
    "tr_err_empty": {
        "en": "Enter at least one measurement.",
        "sw": "Weka angalau kipimo kimoja.",
    },
    "tr_err_bp_pair": {
        "en": "Enter both blood pressure numbers (top and bottom).",
        "sw": "Weka namba zote mbili za shinikizo la damu (ya juu na ya chini).",
    },
    "tr_err_bp_order": {
        "en": "The top number (systolic) must be higher than the bottom number (diastolic).",
        "sw": "Namba ya juu (systolic) lazima iwe kubwa kuliko ya chini (diastolic).",
    },
    "tr_err_future": {
        "en": "The date and time can't be in the future.",
        "sw": "Tarehe na saa haziwezi kuwa za baadaye.",
    },
    "tr_err_db": {
        "en": "Couldn't reach the readings database. If you are the site owner, run the "
              "'readings' part of supabase_setup.sql in Supabase.",
        "sw": "Imeshindikana kufikia hifadhidata ya vipimo. Kama wewe ni mmiliki wa tovuti, "
              "endesha sehemu ya 'readings' ya supabase_setup.sql kwenye Supabase.",
    },

    # Latest reading
    "tr_latest": {"en": "Your latest reading", "sw": "Kipimo chako cha mwisho"},
    "tr_bp": {"en": "Blood pressure", "sw": "Shinikizo la damu"},
    "tr_sugar_short": {"en": "Blood sugar", "sw": "Sukari"},
    "tr_bmi": {"en": "BMI", "sw": "BMI"},
    "tr_height": {
        "en": "Your height (cm), used for BMI",
        "sw": "Urefu wako (cm), kwa ajili ya BMI",
    },

    # Blood pressure categories
    "bp_normal": {"en": "Normal", "sw": "Kawaida"},
    "bp_normal_msg": {
        "en": "Your blood pressure is in the normal range. Keep checking it at least once a year.",
        "sw": "Shinikizo lako la damu liko kawaida. Endelea kupima angalau mara moja kwa mwaka.",
    },
    "bp_high_normal": {"en": "High-normal", "sw": "Juu kidogo ya kawaida"},
    "bp_high_normal_msg": {
        "en": "Slightly raised. Eat less salt, be active, limit alcohol, avoid tobacco, "
              "and check again within a few months.",
        "sw": "Juu kidogo. Punguza chumvi, fanya mazoezi, punguza pombe, epuka tumbaku, "
              "na upime tena ndani ya miezi michache.",
    },
    "bp_grade1": {"en": "High (grade 1)", "sw": "Juu (daraja la 1)"},
    "bp_grade1_msg": {
        "en": "High. One reading is not a diagnosis. Take readings for 7 days. If they stay "
              "this high, see a health worker within a month.",
        "sw": "Juu. Kipimo kimoja si utambuzi wa ugonjwa. Pima kwa siku 7. Vikiendelea kuwa "
              "juu hivi, muone mhudumu wa afya ndani ya mwezi mmoja.",
    },
    "bp_grade2": {"en": "High (grade 2)", "sw": "Juu (daraja la 2)"},
    "bp_grade2_msg": {
        "en": "Clearly high. Please see a health worker within the next week. You may need treatment.",
        "sw": "Juu kwa kiasi kikubwa. Tafadhali muone mhudumu wa afya ndani ya wiki hii. "
              "Huenda ukahitaji matibabu.",
    },
    "bp_very_high": {"en": "Very high", "sw": "Juu sana"},
    "bp_very_high_msg": {
        "en": "Very high. Rest for 5 minutes and measure again. If it is still this high, go "
              "to a health facility TODAY. Go to emergency NOW if you have chest pain, a severe "
              "headache, weakness on one side, confusion, trouble speaking or blurred vision.",
        "sw": "Juu sana. Pumzika dakika 5 kisha upime tena. Likiendelea kuwa juu hivi, nenda "
              "kituo cha afya LEO. Nenda kwenye huduma ya dharura SASA ukiwa na maumivu ya kifua, "
              "maumivu makali ya kichwa, udhaifu upande mmoja wa mwili, kuchanganyikiwa, shida "
              "ya kuongea au kuona ukungu.",
    },
    "bp_low": {"en": "Low", "sw": "Chini"},
    "bp_low_msg": {
        "en": "Lower than usual. If you feel dizzy, faint or weak, sit or lie down, drink "
              "water and see a health worker.",
        "sw": "Chini kuliko kawaida. Ukihisi kizunguzungu, kuzimia au udhaifu, kaa au lala "
              "chini, kunywa maji na umwone mhudumu wa afya.",
    },

    # Blood sugar categories
    "sugar_normal": {"en": "Normal", "sw": "Kawaida"},
    "sugar_normal_msg": {
        "en": "Your blood sugar is in the normal range.",
        "sw": "Sukari yako kwenye damu iko kawaida.",
    },
    "sugar_raised": {"en": "Raised", "sw": "Juu kidogo"},
    "sugar_raised_msg": {
        "en": "Higher than normal, which can be a warning sign of diabetes. Ask a health "
              "worker for a proper test.",
        "sw": "Juu kuliko kawaida, jambo linaloweza kuwa ishara ya mapema ya kisukari. "
              "Mwombe mhudumu wa afya akupime vizuri.",
    },
    "sugar_high": {"en": "High", "sw": "Juu"},
    "sugar_high_msg": {
        "en": "In the diabetes range. Please see a health worker soon to confirm and get care.",
        "sw": "Iko kwenye kiwango cha kisukari. Tafadhali muone mhudumu wa afya hivi karibuni "
              "kuthibitisha na kupata huduma.",
    },
    "sugar_low": {"en": "Low", "sw": "Chini"},
    "sugar_low_msg": {
        "en": "Low blood sugar. Eat or drink something sugary now (juice, soda, sweets), "
              "then a snack. If you get confused or drowsy, someone should take you to a "
              "health facility immediately.",
        "sw": "Sukari iko chini. Kula au kunywa kitu chenye sukari sasa (juisi, soda, peremende), "
              "kisha chakula kidogo. Ukichanganyikiwa au kusinzia, mtu akupeleke kituo cha afya mara moja.",
    },

    # Trends
    "tr_trends": {"en": "Your trends", "sw": "Mwenendo wako"},
    "tr_period": {"en": "Show", "sw": "Onyesha"},
    "tr_7": {"en": "Last 7 days", "sw": "Siku 7 zilizopita"},
    "tr_30": {"en": "Last 30 days", "sw": "Siku 30 zilizopita"},
    "tr_90": {"en": "Last 3 months", "sw": "Miezi 3 iliyopita"},
    "tr_all": {"en": "All", "sw": "Zote"},
    "tr_avg_bp": {"en": "Average BP", "sw": "Wastani wa BP"},
    "tr_readings": {"en": "BP readings", "sw": "Vipimo vya BP"},
    "tr_high_count": {"en": "High readings (≥140/90)", "sw": "Vipimo vya juu (≥140/90)"},
    "tr_change": {"en": "vs previous 7 days", "sw": "ukilinganisha na siku 7 zilizopita"},
    "tr_need_more": {
        "en": "Add at least 3 blood pressure readings in this period to see your average. "
              "Best practice: measure twice in the morning and twice in the evening for 7 days.",
        "sw": "Weka angalau vipimo 3 vya shinikizo la damu katika kipindi hiki ili kuona wastani. "
              "Njia bora: pima mara mbili asubuhi na mara mbili jioni kwa siku 7.",
    },
    "tr_avg_says": {"en": "Your average is **{category}**.", "sw": "Wastani wako ni **{category}**."},
    "tr_avg_high_msg": {
        "en": "Several readings at home that are high are how hypertension is usually found. "
              "Please show these results to a health worker. You can download them below.",
        "sw": "Vipimo kadhaa vya juu nyumbani ndivyo shinikizo la juu la damu hugunduliwa mara nyingi. "
              "Tafadhali mwonyeshe mhudumu wa afya matokeo haya. Unaweza kuyapakua hapa chini.",
    },
    "tr_chart_bp": {"en": "Blood pressure (mmHg)", "sw": "Shinikizo la damu (mmHg)"},
    "tr_chart_note": {
        "en": "Dashed red lines mark 140 and 90, the levels where blood pressure counts as high.",
        "sw": "Mistari myekundu ya vitone inaonyesha 140 na 90, viwango ambapo shinikizo la damu huhesabiwa kuwa juu.",
    },
    "tr_sys_line": {"en": "Systolic (top)", "sw": "Ya juu (systolic)"},
    "tr_dia_line": {"en": "Diastolic (bottom)", "sw": "Ya chini (diastolic)"},
    "tr_when": {"en": "Date and time", "sw": "Tarehe na saa"},
    "tr_chart_weight": {"en": "Weight (kg)", "sw": "Uzito (kg)"},
    "tr_chart_sugar": {"en": "Blood sugar (mmol/L)", "sw": "Sukari kwenye damu (mmol/L)"},
    "tr_chart_pulse": {"en": "Pulse (bpm)", "sw": "Mapigo ya moyo"},
    "tr_no_period": {
        "en": "No readings in this period.",
        "sw": "Hakuna vipimo katika kipindi hiki.",
    },

    # History
    "tr_history": {"en": "All my readings", "sw": "Vipimo vyangu vyote"},
    "tr_col_bp": {"en": "BP (mmHg)", "sw": "BP (mmHg)"},
    "tr_col_cat": {"en": "BP result", "sw": "Matokeo ya BP"},
    "tr_col_sugar": {"en": "Sugar (mmol/L)", "sw": "Sukari (mmol/L)"},
    "tr_download": {"en": "Download my readings (CSV)", "sw": "Pakua vipimo vyangu (CSV)"},
    "tr_delete_title": {"en": "Delete a reading", "sw": "Futa kipimo"},
    "tr_delete_pick": {"en": "Reading to delete", "sw": "Kipimo cha kufuta"},
    "tr_delete_btn": {"en": "Delete this reading", "sw": "Futa kipimo hiki"},
    "tr_deleted": {"en": "Reading deleted.", "sw": "Kipimo kimefutwa."},
    "tr_empty": {
        "en": "No readings yet. Add your first one above.",
        "sw": "Bado hakuna vipimo. Weka kipimo chako cha kwanza hapo juu.",
    },

    # How to measure
    "tr_howto": {
        "en": "How to measure your blood pressure correctly",
        "sw": "Jinsi ya kupima shinikizo la damu kwa usahihi",
    },
    "tr_howto_body": {
        "en": "1. Don't smoke, drink coffee or tea, or exercise for 30 minutes before.\n"
              "2. Empty your bladder, then sit quietly for 5 minutes with your back supported.\n"
              "3. Keep both feet flat on the floor. Don't cross your legs.\n"
              "4. Rest your arm on a table so the cuff is at the level of your heart.\n"
              "5. Put the cuff on bare skin, not over clothes. Don't talk while measuring.\n"
              "6. Take 2 readings, 1 minute apart, and record both.\n"
              "7. Measure at the same times each day, e.g. morning and evening.",
        "sw": "1. Usivute sigara, usinywe kahawa au chai, wala usifanye mazoezi dakika 30 kabla.\n"
              "2. Kojoa kwanza, kisha kaa kimya kwa dakika 5 mgongo ukiwa umeegemea.\n"
              "3. Weka nyayo zote mbili sakafuni. Usikunje miguu.\n"
              "4. Weka mkono mezani ili kifaa (cuff) kiwe usawa wa moyo.\n"
              "5. Funga cuff kwenye ngozi, si juu ya nguo. Usiongee wakati wa kupima.\n"
              "6. Pima mara 2, dakika 1 kati yake, na uandike vipimo vyote viwili.\n"
              "7. Pima nyakati zile zile kila siku, mf. asubuhi na jioni.",
    },
})


# ---------------------------------------------------------------
# Clinical rules
# ---------------------------------------------------------------

def bp_category(systolic, diastolic):
    """ISH 2020 adult categories. The higher of the two numbers decides."""
    if systolic >= 180 or diastolic >= 110:
        return "bp_very_high"
    if systolic >= 160 or diastolic >= 100:
        return "bp_grade2"
    if systolic >= 140 or diastolic >= 90:
        return "bp_grade1"
    if systolic >= 130 or diastolic >= 85:
        return "bp_high_normal"
    if systolic < 90 or diastolic < 60:
        return "bp_low"
    return "bp_normal"


def sugar_category(value, kind):
    """WHO cut-offs in mmol/L. kind is 'fasting' or 'random'."""
    if value < 3.9:
        return "sugar_low"
    normal, high = (6.1, 7.0) if kind == "fasting" else (7.8, 11.1)
    if value < normal:
        return "sugar_normal"
    if value < high:
        return "sugar_raised"
    return "sugar_high"


# Which Streamlit box to show each result in
SEVERITY = {
    "bp_normal": st.success, "bp_high_normal": st.info, "bp_grade1": st.warning,
    "bp_grade2": st.error, "bp_very_high": st.error, "bp_low": st.warning,
    "sugar_normal": st.success, "sugar_raised": st.warning,
    "sugar_high": st.error, "sugar_low": st.error,
}


def show_advice(category, label):
    SEVERITY[category](f"**{label}: {t(category)}.** {t(category + '_msg')}")


# ---------------------------------------------------------------
# Data helpers
# ---------------------------------------------------------------

def readings_frame(rows):
    df = pd.DataFrame(rows)
    if df.empty:
        return df
    df["taken_at"] = pd.to_datetime(df["taken_at"], utc=True, format="ISO8601").dt.tz_convert(i18n.user_tz())
    for col in ["systolic", "diastolic", "pulse", "weight_kg", "glucose_mmol"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    return df.sort_values("taken_at").reset_index(drop=True)


def bp_summary(df):
    """Average BP, number of readings and number of high readings."""
    bp = df.dropna(subset=["systolic", "diastolic"])
    if bp.empty:
        return None
    return {
        "n": len(bp),
        "sys": round(bp["systolic"].mean()),
        "dia": round(bp["diastolic"].mean()),
        "high": int(((bp["systolic"] >= HIGH_SYS) | (bp["diastolic"] >= HIGH_DIA)).sum()),
    }


def line_chart(df, column, title, color, rules=()):
    data = df.dropna(subset=[column])
    if data.empty:
        return
    chart = alt.Chart(data).mark_line(point=True, color=color).encode(
        x=alt.X("taken_at:T", title=t("tr_when")),
        y=alt.Y(f"{column}:Q", title=title, scale=alt.Scale(zero=False)),
        tooltip=[alt.Tooltip("taken_at:T", title=t("tr_when"), format="%d %b %Y %H:%M"),
                 alt.Tooltip(f"{column}:Q", title=title)],
    )
    for value in rules:
        chart += alt.Chart(pd.DataFrame({"y": [value]})).mark_rule(
            color="#C0392B", strokeDash=[6, 4]).encode(y="y:Q")
    st.altair_chart(chart.properties(height=260))


def bp_chart(df):
    bp = df.dropna(subset=["systolic", "diastolic"])
    if bp.empty:
        return
    long = bp.melt(id_vars="taken_at", value_vars=["systolic", "diastolic"],
                   var_name="measure", value_name="mmHg")
    names = {"systolic": t("tr_sys_line"), "diastolic": t("tr_dia_line")}
    long["measure"] = long["measure"].map(names)
    lines = alt.Chart(long).mark_line(point=True).encode(
        x=alt.X("taken_at:T", title=t("tr_when")),
        y=alt.Y("mmHg:Q", title=t("tr_chart_bp"), scale=alt.Scale(zero=False)),
        color=alt.Color("measure:N", title=None,
                        scale=alt.Scale(domain=list(names.values()), range=["#2F7D6D", "#6B8FA3"]),
                        legend=alt.Legend(orient="bottom")),
        tooltip=[alt.Tooltip("taken_at:T", title=t("tr_when"), format="%d %b %Y %H:%M"),
                 alt.Tooltip("measure:N", title=" "), alt.Tooltip("mmHg:Q")],
    )
    rules = alt.Chart(pd.DataFrame({"y": [HIGH_SYS, HIGH_DIA]})).mark_rule(
        color="#C0392B", strokeDash=[6, 4]).encode(y="y:Q")
    st.altair_chart((lines + rules).properties(height=320))
    st.caption(t("tr_chart_note"))


def history_table(df):
    table = pd.DataFrame({
        t("tr_when"): df["taken_at"].map(i18n.short_datetime),
        t("tr_col_bp"): [
            f"{int(s)}/{int(d)}" if pd.notna(s) and pd.notna(d) else ""
            for s, d in zip(df["systolic"], df["diastolic"])
        ],
        t("tr_col_cat"): [
            t(bp_category(s, d)) if pd.notna(s) and pd.notna(d) else ""
            for s, d in zip(df["systolic"], df["diastolic"])
        ],
        t("tr_pulse"): df["pulse"].map(lambda v: "" if pd.isna(v) else int(v)),
        t("tr_weight"): df["weight_kg"].map(lambda v: "" if pd.isna(v) else v),
        t("tr_col_sugar"): [
            "" if pd.isna(v) else f"{v} ({t('tr_' + k).split(' (')[0]})"
            for v, k in zip(df["glucose_mmol"], df["glucose_type"])
        ],
        t("tr_note").split(" (")[0]: df["note"].fillna(""),
    })
    return table.iloc[::-1]  # newest first


# ---------------------------------------------------------------
# Page
# ---------------------------------------------------------------

def _entry_form(owner):
    now = i18n.local_now()
    st.subheader(t("tr_add"))
    with st.form("reading_form", clear_on_submit=True):
        c1, c2 = st.columns(2)
        day = c1.date_input(t("tr_date"), value=now.date(), max_value=now.date(), format="DD/MM/YYYY")
        clock = c2.time_input(t("tr_time"), value=now.time().replace(second=0, microsecond=0), step=300)

        b1, b2, b3 = st.columns(3)
        systolic = b1.number_input(t("tr_systolic"), 50, 260, value=None, help=t("tr_bp_help"))
        diastolic = b2.number_input(t("tr_diastolic"), 30, 160, value=None, help=t("tr_bp_help"))
        pulse = b3.number_input(t("tr_pulse"), 20, 250, value=None)

        w1, w2, w3 = st.columns(3)
        weight = w1.number_input(t("tr_weight"), 1.0, 300.0, value=None, step=0.5)
        sugar = w2.number_input(t("tr_sugar"), 1.0, 35.0, value=None, step=0.1,
                                format="%.1f", help=t("tr_sugar_help"))
        sugar_kind = w3.selectbox(t("tr_sugar_kind"), ["fasting", "random"],
                                  format_func=lambda k: t("tr_" + k))
        note = st.text_input(t("tr_note"), placeholder=t("tr_note_ph"), max_chars=200)
        submitted = st.form_submit_button(t("tr_save"), type="primary", width="stretch")

    if not submitted:
        return

    taken_at = datetime.combine(day, clock, tzinfo=i18n.user_tz())
    problems = []
    if all(v is None for v in (systolic, diastolic, pulse, weight, sugar)):
        problems.append(t("tr_err_empty"))
    if (systolic is None) != (diastolic is None):
        problems.append(t("tr_err_bp_pair"))
    elif systolic is not None and systolic <= diastolic:
        problems.append(t("tr_err_bp_order"))
    if taken_at > now + timedelta(minutes=5):
        problems.append(t("tr_err_future"))
    if problems:
        for p in problems:
            st.error(p)
        return

    try:
        save_reading({
            "owner": owner,
            "taken_at": taken_at.isoformat(),
            "systolic": systolic, "diastolic": diastolic, "pulse": pulse,
            "weight_kg": weight,
            "glucose_mmol": round(sugar, 1) if sugar is not None else None,
            "glucose_type": sugar_kind if sugar is not None else None,
            "note": note.strip() or None,
        })
    except Exception:
        st.error(t("tr_err_db"))
        return
    st.session_state.tracker_flash = t("tr_saved")
    st.rerun()


def _latest(df):
    st.subheader(t("tr_latest"))
    last_bp = df.dropna(subset=["systolic", "diastolic"]).tail(1)
    last_sugar = df.dropna(subset=["glucose_mmol"]).tail(1)
    last_weight = df.dropna(subset=["weight_kg"]).tail(1)

    m1, m2, m3 = st.columns(3)
    if not last_bp.empty:
        r = last_bp.iloc[0]
        m1.metric(t("tr_bp"), f"{int(r.systolic)}/{int(r.diastolic)}",
                  help=i18n.short_datetime(r.taken_at))
    if not last_sugar.empty:
        r = last_sugar.iloc[0]
        m2.metric(t("tr_sugar_short"), f"{r.glucose_mmol} mmol/L",
                  help=i18n.short_datetime(r.taken_at))
    if not last_weight.empty:
        r = last_weight.iloc[0]
        height = m3.number_input(t("tr_height"), 100.0, 230.0, value=None, step=0.5,
                                 key="tracker_height")
        bmi = f" · BMI {r.weight_kg / (height / 100) ** 2:.1f}" if height else ""
        m3.metric(t("tr_weight"), f"{r.weight_kg} kg{bmi}")

    if not last_bp.empty:
        r = last_bp.iloc[0]
        show_advice(bp_category(r.systolic, r.diastolic), t("tr_bp"))
    if not last_sugar.empty:
        r = last_sugar.iloc[0]
        show_advice(sugar_category(r.glucose_mmol, r.glucose_type), t("tr_sugar_short"))


def _trends(df):
    st.subheader(t("tr_trends"))
    periods = {"tr_7": 7, "tr_30": 30, "tr_90": 90, "tr_all": None}
    choice = st.segmented_control(t("tr_period"), list(periods), default="tr_30",
                                  format_func=t, key="tracker_period") or "tr_30"
    now = i18n.local_now()
    days = periods[choice]
    shown = df if days is None else df[df["taken_at"] >= now - timedelta(days=days)]

    if shown.empty:
        st.info(t("tr_no_period"))
        return

    summary = bp_summary(shown)
    if summary and summary["n"] >= 3:
        k1, k2, k3 = st.columns(3)
        # Change in average systolic compared with the 7 days before this week
        delta = None
        this_week = bp_summary(df[df["taken_at"] >= now - timedelta(days=7)])
        last_week = bp_summary(df[(df["taken_at"] < now - timedelta(days=7))
                                  & (df["taken_at"] >= now - timedelta(days=14))])
        if choice == "tr_7" and this_week and last_week and last_week["n"] >= 3:
            delta = f"{this_week['sys'] - last_week['sys']:+d} mmHg {t('tr_change')}"
        k1.metric(t("tr_avg_bp"), f"{summary['sys']}/{summary['dia']}",
                  delta=delta, delta_color="inverse")
        k2.metric(t("tr_readings"), summary["n"])
        k3.metric(t("tr_high_count"), summary["high"])

        category = bp_category(summary["sys"], summary["dia"])
        message = t("tr_avg_says", category=t(category).lower()) + " " + t(category + "_msg")
        if category in ("bp_grade1", "bp_grade2", "bp_very_high"):
            message += " " + t("tr_avg_high_msg")
        SEVERITY[category](message)
    else:
        st.info(t("tr_need_more"))

    bp_chart(shown)
    left, right = st.columns(2)
    with left:
        line_chart(shown, "weight_kg", t("tr_chart_weight"), "#6B8FA3")
        line_chart(shown, "pulse", t("tr_chart_pulse"), "#8E6BA3", rules=(100,))
    with right:
        line_chart(shown, "glucose_mmol", t("tr_chart_sugar"), "#C27C2C", rules=(7.0, 11.1))


def _history(df, owner):
    st.subheader(t("tr_history"))
    table = history_table(df)
    st.dataframe(table, width="stretch", hide_index=True)
    st.download_button(
        t("tr_download"),
        table.to_csv(index=False).encode("utf-8"),
        file_name="my_health_readings.csv",
        mime="text/csv",
    )
    with st.expander(t("tr_delete_title")):
        labels = {
            int(row.id): f"{i18n.short_datetime(row.taken_at)} · "
                         + (f"{int(row.systolic)}/{int(row.diastolic)}" if pd.notna(row.systolic) else "")
            for row in df.iloc[::-1].itertuples()
        }
        chosen = st.selectbox(t("tr_delete_pick"), list(labels), format_func=labels.get)
        if st.button(t("tr_delete_btn")):
            delete_reading(owner, chosen)
            st.session_state.tracker_flash = t("tr_deleted")
            st.rerun()


def render(owner):
    st.header(t("tr_title"))
    st.write(t("tr_intro"))
    st.caption(t("tr_why"))

    if "tracker_flash" in st.session_state:
        st.success(st.session_state.pop("tracker_flash"))

    try:
        df = readings_frame(load_readings(owner))
    except Exception:
        st.error(t("tr_err_db"))
        return

    if not df.empty:
        _latest(df)
        st.divider()

    _entry_form(owner)

    with st.expander(t("tr_howto")):
        demo.show("bp")
        st.markdown(t("tr_howto_body"))

    st.divider()
    if df.empty:
        st.info(t("tr_empty"))
        return
    _trends(df)
    st.divider()
    _history(df, owner)