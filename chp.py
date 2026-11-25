"""CHP mode: one Community Health Promoter looks after many households.

- The CHP registers households (after verbal consent) and their members.
- On a home visit, the CHP records readings for a member with the same
  tracker everyone uses, and can refer them to a health facility.
- The follow-up list shows pending referrals and people due for a recheck,
  so the CHP can confirm whether each person reached care (linkage to care).

Access: a user requests CHP access here; an admin approves it on the
admin website. A CHP only ever sees the households they registered.
"""

from datetime import datetime, timedelta, timezone

import pandas as pd
import streamlit as st

import chp_store as db
import i18n
import tracker
from i18n import t
from storage import load_readings_many

i18n.register({
    "chp_title": {"en": "CHP mode: my households", "sw": "Hali ya CHP: kaya zangu"},
    "chp_intro": {
        "en": "For Community Health Promoters (CHPs). Register households, record readings on home "
              "visits with one BP machine for everyone, refer people to a facility and follow them up.",
        "sw": "Kwa Wahudumu wa Afya ya Jamii (CHP). Sajili kaya, weka vipimo wakati wa kutembelea "
              "nyumbani kwa kifaa kimoja cha BP kwa wote, wapeleke watu kituo cha afya na uwafuatilie.",
    },
    # Access
    "chp_request_title": {"en": "Request CHP access", "sw": "Omba ruhusa ya CHP"},
    "chp_request_text": {
        "en": "CHP mode is for registered Community Health Promoters. Tell us where you work. An "
              "administrator will check and approve your request.",
        "sw": "Hali ya CHP ni kwa Wahudumu wa Afya ya Jamii waliosajiliwa. Tuambie unapofanya kazi. "
              "Msimamizi atakagua na kuidhinisha ombi lako.",
    },
    "chp_facility": {"en": "Link health facility *", "sw": "Kituo cha afya unachoshirikiana nacho *"},
    "chp_area": {"en": "Community health unit / area *", "sw": "Kitengo cha afya ya jamii / eneo *"},
    "chp_send": {"en": "Send request", "sw": "Tuma ombi"},
    "chp_fill": {"en": "Please fill in both fields.", "sw": "Tafadhali jaza sehemu zote mbili."},
    "chp_pending": {
        "en": "Your request has been sent and is waiting for approval. Check back later.",
        "sw": "Ombi lako limetumwa na linasubiri kuidhinishwa. Angalia tena baadaye.",
    },
    "chp_rejected": {
        "en": "Your CHP request was not approved. Contact the administrator if you think this is a mistake.",
        "sw": "Ombi lako la CHP halikuidhinishwa. Wasiliana na msimamizi kama unadhani ni kosa.",
    },
    # Tabs
    "chp_tab_overview": {"en": "📊 Overview", "sw": "📊 Muhtasari"},
    "chp_tab_households": {"en": "🏠 Households", "sw": "🏠 Kaya"},
    "chp_tab_visit": {"en": "🩺 Home visit", "sw": "🩺 Kutembelea nyumbani"},
    "chp_tab_follow": {"en": "📋 Follow-up", "sw": "📋 Ufuatiliaji"},
    # Overview
    "chp_m_households": {"en": "Households", "sw": "Kaya"},
    "chp_m_people": {"en": "People", "sw": "Watu"},
    "chp_m_screened": {"en": "BP checked (30 days)", "sw": "Waliopimwa BP (siku 30)"},
    "chp_m_high": {"en": "Latest BP high (≥140/90)", "sw": "BP ya mwisho juu (≥140/90)"},
    "chp_m_pending": {"en": "Referrals waiting", "sw": "Rufaa zinazosubiri"},
    "chp_m_linkage": {"en": "Referrals that reached care", "sw": "Rufaa zilizofika kituoni"},
    "chp_empty": {
        "en": "No households yet. Start in the Households tab.",
        "sw": "Bado hakuna kaya. Anza kwenye kichupo cha Kaya.",
    },
    # Households
    "chp_add_hh": {"en": "Register a household", "sw": "Sajili kaya"},
    "chp_head": {"en": "Head of household (name) *", "sw": "Mkuu wa kaya (jina) *"},
    "chp_village": {"en": "Village *", "sw": "Kijiji *"},
    "chp_phone": {"en": "Phone (optional)", "sw": "Simu (si lazima)"},
    "chp_consent": {
        "en": "The household agreed to have their names and health readings recorded, after I "
              "explained why and who can see them (verbal consent). *",
        "sw": "Kaya imekubali majina yao na vipimo vya afya viandikwe, baada ya kueleza sababu na "
              "nani anaweza kuviona (ridhaa ya mdomo). *",
    },
    "chp_save_hh": {"en": "Register household", "sw": "Sajili kaya"},
    "chp_hh_saved": {"en": "Household {code} registered.", "sw": "Kaya {code} imesajiliwa."},
    "chp_hh_need": {
        "en": "Head of household, village and consent are required.",
        "sw": "Mkuu wa kaya, kijiji na ridhaa vinahitajika.",
    },
    "chp_add_member": {"en": "Add a household member", "sw": "Ongeza mwanakaya"},
    "chp_household": {"en": "Household", "sw": "Kaya"},
    "chp_name": {"en": "Name *", "sw": "Jina *"},
    "chp_sex": {"en": "Sex", "sw": "Jinsia"},
    "chp_birth_year": {"en": "Year of birth *", "sw": "Mwaka wa kuzaliwa *"},
    "chp_save_member": {"en": "Add member", "sw": "Ongeza mwanakaya"},
    "chp_member_saved": {"en": "{name} added.", "sw": "{name} ameongezwa."},
    "chp_member_need": {"en": "Name and year of birth are required.", "sw": "Jina na mwaka wa kuzaliwa vinahitajika."},
    "chp_list": {"en": "My households", "sw": "Kaya zangu"},
    "chp_col_code": {"en": "Code", "sw": "Namba"},
    "chp_col_people": {"en": "People", "sw": "Watu"},
    "female": {"en": "Female", "sw": "Mwanamke"},
    "male": {"en": "Male", "sw": "Mwanaume"},
    # Visit
    "chp_pick_hh": {"en": "Household", "sw": "Kaya"},
    "chp_pick_member": {"en": "Family member", "sw": "Mwanakaya"},
    "chp_no_members": {
        "en": "This household has no members yet. Add them in the Households tab.",
        "sw": "Kaya hii bado haina wanakaya. Waongeze kwenye kichupo cha Kaya.",
    },
    "chp_age": {"en": "{age} years", "sw": "Miaka {age}"},
    "chp_refer_now": {
        "en": "⚠️ The latest blood pressure is **{bp}** ({category}). Consider referring this person to a facility.",
        "sw": "⚠️ Shinikizo la damu la mwisho ni **{bp}** ({category}). Fikiria kumpa rufaa kwenda kituo cha afya.",
    },
    "chp_refer": {"en": "🏥 Refer to a health facility", "sw": "🏥 Mpe rufaa kwenda kituo cha afya"},
    "chp_reason": {"en": "Reason", "sw": "Sababu"},
    "chp_note": {"en": "Note (optional)", "sw": "Maelezo (si lazima)"},
    "chp_send_ref": {"en": "Record referral", "sw": "Rekodi rufaa"},
    "chp_ref_saved": {
        "en": "Referral recorded. Follow it up in the Follow-up tab.",
        "sw": "Rufaa imerekodiwa. Ifuatilie kwenye kichupo cha Ufuatiliaji.",
    },
    "chp_tools": {
        "en": "Also use **Danger signs** and **Measure with your hands** from the menu during the visit.",
        "sw": "Pia tumia **Dalili za hatari** na **Pima kwa mikono** kutoka kwenye menyu wakati wa kutembelea.",
    },
    "r_high_bp": {"en": "High blood pressure", "sw": "Shinikizo la juu la damu"},
    "r_very_high_bp": {"en": "Very high blood pressure (180/110+)", "sw": "Shinikizo la juu sana (180/110+)"},
    "r_high_sugar": {"en": "High blood sugar", "sw": "Sukari ya juu"},
    "r_danger": {"en": "Danger sign", "sw": "Dalili ya hatari"},
    "r_malnutrition": {"en": "Malnutrition (MUAC)", "sw": "Utapiamlo (MUAC)"},
    "r_pregnancy": {"en": "Pregnancy care", "sw": "Huduma ya ujauzito"},
    "r_other": {"en": "Other", "sw": "Nyingine"},
    # Follow-up
    "chp_waiting": {"en": "Referrals waiting for follow-up", "sw": "Rufaa zinazosubiri ufuatiliaji"},
    "chp_no_waiting": {"en": "No referrals waiting. 👍", "sw": "Hakuna rufaa zinazosubiri. 👍"},
    "chp_days": {"en": "{n} days ago", "sw": "Siku {n} zilizopita"},
    "chp_pick_ref": {"en": "Update a referral", "sw": "Sasisha rufaa"},
    "chp_went": {"en": "✅ Went to the facility", "sw": "✅ Alienda kituo cha afya"},
    "chp_not_went": {"en": "❌ Did not go", "sw": "❌ Hakwenda"},
    "chp_updated": {"en": "Referral updated.", "sw": "Rufaa imesasishwa."},
    "chp_recheck": {"en": "Due for a blood pressure recheck", "sw": "Wanaostahili kupimwa BP tena"},
    "chp_recheck_note": {
        "en": "Latest BP was high and the last check was more than 14 days ago.",
        "sw": "BP ya mwisho ilikuwa juu na kipimo cha mwisho kilikuwa zaidi ya siku 14 zilizopita.",
    },
    "chp_never": {"en": "Adults never checked", "sw": "Watu wazima ambao hawajawahi kupimwa"},
    "chp_none": {"en": "Nobody in this list. 👍", "sw": "Hakuna mtu kwenye orodha hii. 👍"},
    "chp_col_person": {"en": "Person", "sw": "Mtu"},
    "chp_col_reason": {"en": "Reason", "sw": "Sababu"},
    "chp_col_when": {"en": "Referred", "sw": "Alipewa rufaa"},
    "chp_col_last": {"en": "Last BP", "sw": "BP ya mwisho"},
    "chp_col_village": {"en": "Village", "sw": "Kijiji"},
    "chp_col_phone": {"en": "Phone", "sw": "Simu"},
})

REASONS = ["high_bp", "very_high_bp", "high_sugar", "danger", "malnutrition", "pregnancy", "other"]


def _age(birth_year):
    return i18n.local_now().year - int(birth_year) if birth_year else None


def _days_ago(iso):
    when = pd.to_datetime(iso, utc=True)
    return (datetime.now(timezone.utc) - when.to_pydatetime()).days


# ---------------------------------------------------------------
# Data for one CHP, gathered once per page load
# ---------------------------------------------------------------

def _load(chp):
    hh = pd.DataFrame(db.households(chp))
    mem = pd.DataFrame(db.members(chp))
    refs = pd.DataFrame(db.referrals(chp))
    owners = [db.member_owner(m) for m in mem["id"]] if not mem.empty else []
    readings = tracker.readings_frame(load_readings_many(owners))
    return hh, mem, refs, readings


def latest_bp(readings):
    """One row per owner: their most recent BP reading."""
    if readings.empty:
        return pd.DataFrame(columns=["owner", "taken_at", "systolic", "diastolic"])
    bp = readings.dropna(subset=["systolic", "diastolic"])
    return bp.sort_values("taken_at").groupby("owner").tail(1)


def follow_up_lists(mem, readings, today=None):
    """(people due for a BP recheck, adults never checked)."""
    today = today or datetime.now(timezone.utc)
    if mem.empty:
        return pd.DataFrame(), pd.DataFrame()
    mem = mem.assign(owner=mem["id"].map(db.member_owner))
    last = latest_bp(readings).set_index("owner")
    recheck, never = [], []
    for _, m in mem.iterrows():
        if m["owner"] in last.index:
            r = last.loc[m["owner"]]
            high = r["systolic"] >= 140 or r["diastolic"] >= 90
            old = (today - r["taken_at"].to_pydatetime()).days > 14
            if high and old:
                recheck.append({**m, "last": f"{int(r['systolic'])}/{int(r['diastolic'])}",
                                "taken_at": r["taken_at"]})
        elif (_age(m.get("birth_year")) or 0) >= 18:
            never.append(dict(m))
    return pd.DataFrame(recheck), pd.DataFrame(never)


# ---------------------------------------------------------------
# Screens
# ---------------------------------------------------------------

def _request_access(email):
    status = db.chp_status(email)
    if status == "pending":
        st.info(t("chp_pending"))
        return
    if status == "rejected":
        st.warning(t("chp_rejected"))
        return
    st.subheader(t("chp_request_title"))
    st.write(t("chp_request_text"))
    with st.form("chp_request"):
        facility = st.text_input(t("chp_facility"))
        area = st.text_input(t("chp_area"))
        if st.form_submit_button(t("chp_send"), type="primary"):
            if facility.strip() and area.strip():
                db.request_chp(email, facility.strip(), area.strip())
                st.rerun()
            else:
                st.error(t("chp_fill"))


def _overview(hh, mem, refs, readings):
    if hh.empty:
        st.info(t("chp_empty"))
        return
    recent = readings[readings["taken_at"] >= pd.Timestamp.now(tz="UTC") - pd.Timedelta(days=30)] \
        if not readings.empty else readings
    screened = recent.dropna(subset=["systolic"])["owner"].nunique() if not recent.empty else 0
    last = latest_bp(readings)
    high = int(((last["systolic"] >= 140) | (last["diastolic"] >= 90)).sum()) if not last.empty else 0
    pending = int((refs["status"] == "pending").sum()) if not refs.empty else 0
    decided = refs[refs["status"] != "pending"] if not refs.empty else refs
    linkage = f"{(decided['status'] == 'attended').mean():.0%}" if len(decided) else "–"

    c1, c2, c3 = st.columns(3)
    c1.metric(t("chp_m_households"), len(hh))
    c2.metric(t("chp_m_people"), len(mem))
    c3.metric(t("chp_m_screened"), screened)
    c4, c5, c6 = st.columns(3)
    c4.metric(t("chp_m_high"), high)
    c5.metric(t("chp_m_pending"), pending)
    c6.metric(t("chp_m_linkage"), linkage)


def _households(chp, hh, mem):
    with st.expander(t("chp_add_hh"), expanded=hh.empty):
        with st.form("chp_hh_form", clear_on_submit=True):
            head = st.text_input(t("chp_head"))
            c1, c2 = st.columns(2)
            village = c1.text_input(t("chp_village"))
            phone = c2.text_input(t("chp_phone"))
            consent = st.checkbox(t("chp_consent"))
            if st.form_submit_button(t("chp_save_hh"), type="primary"):
                if head.strip() and village.strip() and consent:
                    code = db.add_household(chp, head.strip(), village.strip(), phone.strip())
                    st.session_state.chp_flash = t("chp_hh_saved", code=code)
                    st.rerun()
                st.error(t("chp_hh_need"))

    if hh.empty:
        return
    labels = {int(r.id): f"{r.code} · {r.head_name} · {r.village}" for r in hh.itertuples()}
    with st.expander(t("chp_add_member"), expanded=mem.empty):
        with st.form("chp_member_form", clear_on_submit=True):
            household = st.selectbox(t("chp_household"), list(labels), format_func=labels.get)
            name = st.text_input(t("chp_name"))
            c1, c2 = st.columns(2)
            sex = c1.radio(t("chp_sex"), ["female", "male"], format_func=t, horizontal=True)
            year = c2.number_input(t("chp_birth_year"), 1900, i18n.local_now().year, value=None)
            if st.form_submit_button(t("chp_save_member"), type="primary"):
                if name.strip() and year:
                    db.add_member(chp, household, name.strip(), sex, int(year))
                    st.session_state.chp_flash = t("chp_member_saved", name=name.strip())
                    st.rerun()
                st.error(t("chp_member_need"))

    st.subheader(t("chp_list"))
    counts = mem.groupby("household_id").size() if not mem.empty else pd.Series(dtype=int)
    table = pd.DataFrame({
        t("chp_col_code"): hh["code"],
        t("chp_head").rstrip(" *"): hh["head_name"],
        t("chp_col_village"): hh["village"],
        t("chp_col_phone"): hh["phone"].fillna(""),
        t("chp_col_people"): hh["id"].map(counts).fillna(0).astype(int),
    })
    st.dataframe(table, width="stretch", hide_index=True)


def _visit(chp, hh, mem, readings):
    if hh.empty:
        st.info(t("chp_empty"))
        return
    labels = {int(r.id): f"{r.code} · {r.head_name} · {r.village}" for r in hh.itertuples()}
    household = st.selectbox(t("chp_pick_hh"), list(labels), format_func=labels.get, key="chp_v_hh")
    people = mem[mem["household_id"] == household] if not mem.empty else mem
    if people.empty:
        st.info(t("chp_no_members"))
        return
    names = {int(r.id): f"{r.name} · {t(r.sex)} · {t('chp_age', age=_age(r.birth_year))}"
             for r in people.itertuples()}
    member = st.selectbox(t("chp_pick_member"), list(names), format_func=names.get, key="chp_v_m")
    owner = db.member_owner(member)

    last = latest_bp(readings)
    last = last[last["owner"] == owner]
    if not last.empty:
        r = last.iloc[0]
        category = tracker.bp_category(r.systolic, r.diastolic)
        if category in ("bp_grade1", "bp_grade2", "bp_very_high"):
            st.warning(t("chp_refer_now", bp=f"{int(r.systolic)}/{int(r.diastolic)}",
                         category=t(category)))

    with st.expander(t("chp_refer")):
        with st.form("chp_ref_form", clear_on_submit=True):
            reason = st.selectbox(t("chp_reason"), REASONS, format_func=lambda k: t("r_" + k))
            note = st.text_input(t("chp_note"), max_chars=200)
            if st.form_submit_button(t("chp_send_ref"), type="primary"):
                db.add_referral(chp, member, reason, note.strip())
                st.session_state.chp_flash = t("chp_ref_saved")
                st.rerun()

    st.caption(t("chp_tools"))
    st.divider()
    tracker.render(owner, show_header=False)


def _follow_up(chp, hh, mem, refs, readings):
    st.subheader(t("chp_waiting"))
    pending = refs[refs["status"] == "pending"] if not refs.empty else refs
    if pending.empty:
        st.success(t("chp_no_waiting"))
    else:
        people = mem.set_index("id") if not mem.empty else mem
        homes = hh.set_index("id")

        def describe(row):
            m = people.loc[row.member_id]
            home = homes.loc[m["household_id"]]
            phone = home["phone"]
            return m["name"], home["village"], "" if pd.isna(phone) else phone

        rows = [describe(r) for r in pending.itertuples()]
        st.dataframe(pd.DataFrame({
            t("chp_col_person"): [r[0] for r in rows],
            t("chp_col_village"): [r[1] for r in rows],
            t("chp_col_phone"): [r[2] for r in rows],
            t("chp_col_reason"): [t("r_" + x) for x in pending["reason"]],
            t("chp_col_when"): [t("chp_days", n=_days_ago(x)) for x in pending["referred_at"]],
        }), width="stretch", hide_index=True)

        options = {int(r.id): f"{rows[i][0]} · {t('r_' + r.reason)}"
                   for i, r in enumerate(pending.itertuples())}
        chosen = st.selectbox(t("chp_pick_ref"), list(options), format_func=options.get)
        c1, c2 = st.columns(2)
        if c1.button(t("chp_went"), width="stretch"):
            db.set_referral_status(chp, chosen, "attended")
            st.session_state.chp_flash = t("chp_updated")
            st.rerun()
        if c2.button(t("chp_not_went"), width="stretch"):
            db.set_referral_status(chp, chosen, "not_attended")
            st.session_state.chp_flash = t("chp_updated")
            st.rerun()

    recheck, never = follow_up_lists(mem, readings)
    homes = hh.set_index("id") if not hh.empty else hh
    st.subheader(t("chp_recheck"))
    st.caption(t("chp_recheck_note"))
    if recheck.empty:
        st.success(t("chp_none"))
    else:
        st.dataframe(pd.DataFrame({
            t("chp_col_person"): recheck["name"],
            t("chp_col_village"): recheck["household_id"].map(homes["village"]),
            t("chp_col_last"): recheck["last"],
            t("tr_when"): recheck["taken_at"].map(i18n.short_datetime),
        }), width="stretch", hide_index=True)

    st.subheader(t("chp_never"))
    if never.empty:
        st.success(t("chp_none"))
    else:
        st.dataframe(pd.DataFrame({
            t("chp_col_person"): never["name"],
            t("chp_col_village"): never["household_id"].map(homes["village"]),
            t("chp_col_phone"): never["household_id"].map(homes["phone"]).fillna(""),
        }), width="stretch", hide_index=True)


def render(email):
    st.header(t("chp_title"))
    st.write(t("chp_intro"))
    try:
        status = db.chp_status(email)
    except Exception:
        st.error(t("db_unavailable"))
        return
    if status != "approved":
        _request_access(email)
        return

    if "chp_flash" in st.session_state:
        st.success(st.session_state.pop("chp_flash"))
    try:
        hh, mem, refs, readings = _load(email)
    except Exception:
        st.error(t("db_unavailable"))
        return

    overview, homes, visit, follow = st.tabs([t("chp_tab_overview"), t("chp_tab_households"),
                                              t("chp_tab_visit"), t("chp_tab_follow")])
    with overview:
        _overview(hh, mem, refs, readings)
    with homes:
        _households(email, hh, mem)
    with visit:
        _visit(email, hh, mem, readings)
    with follow:
        _follow_up(email, hh, mem, refs, readings)