"""Danger signs checker: "Do I need to go to hospital?"

Tick the signs you see; the page says whether to go to EMERGENCY NOW,
to a CLINIC TODAY, or to watch at home. No equipment is needed.

Sources:
- Children 2 months to 5 years: WHO Integrated Management of Childhood
  Illness (IMCI) general danger signs, and fast-breathing cut-offs
  (50+/min at 2-12 months, 40+/min at 1-5 years).
- Young infants under 2 months: WHO IMCI young infant danger signs
  (fast breathing 60+/min, temperature 37.5 C+ or below 35.5 C, etc.).
- Pregnancy and after birth: WHO / Kenya Mother & Child Health booklet
  danger signs.
- Adults: FAST stroke signs and heart attack warning signs.

It never diagnoses. When unsure, it always advises going to a facility.
"""

import streamlit as st

import demo
import i18n
from i18n import t

i18n.register({
    "ds_title": {"en": "Danger signs: do I need to go to hospital?",
                 "sw": "Dalili za hatari: je, niende hospitali?"},
    "ds_intro": {
        "en": "Tick any signs you can see. You'll find out whether to go to emergency now, visit a "
              "clinic today, or watch at home. No equipment needed.",
        "sw": "Weka alama kwenye dalili unazoziona. Utajua kama uende kwenye huduma ya dharura sasa, "
              "uende kliniki leo, au uangalie nyumbani. Hakuna kifaa kinachohitajika.",
    },
    "ds_who": {"en": "Who is unwell?", "sw": "Nani anaumwa?"},
    "ds_g_adult": {"en": "Adult", "sw": "Mtu mzima"},
    "ds_g_pregnant": {"en": "Pregnant or recently gave birth", "sw": "Mjamzito au amejifungua hivi karibuni"},
    "ds_g_child": {"en": "Child (2 months to 5 years)", "sw": "Mtoto (miezi 2 hadi miaka 5)"},
    "ds_g_newborn": {"en": "Baby under 2 months", "sw": "Mtoto chini ya miezi 2"},
    "ds_tick": {"en": "Tick every sign you see:", "sw": "Weka alama kwenye kila dalili unayoiona:"},
    "ds_check": {"en": "Check", "sw": "Angalia"},

    # Results
    "ds_red_title": {"en": "GO TO EMERGENCY NOW", "sw": "NENDA KWENYE HUDUMA YA DHARURA SASA"},
    "ds_red_body": {
        "en": "These are danger signs. Go to the nearest hospital or health facility **immediately**. "
              "Do not wait to see if it gets better.",
        "sw": "Hizi ni dalili za hatari. Nenda hospitali au kituo cha afya kilicho karibu **mara moja**. "
              "Usisubiri kuona kama itapona.",
    },
    "ds_amber_title": {"en": "VISIT A CLINIC TODAY", "sw": "NENDA KLINIKI LEO"},
    "ds_amber_body": {
        "en": "This needs to be checked by a health worker **today**. If any danger sign appears, "
              "go to emergency straight away.",
        "sw": "Hii inahitaji kuchunguzwa na mhudumu wa afya **leo**. Dalili yoyote ya hatari ikitokea, "
              "nenda kwenye huduma ya dharura mara moja.",
    },
    "ds_green_title": {"en": "NO DANGER SIGNS TICKED", "sw": "HUJAWEKA ALAMA KWENYE DALILI YA HATARI"},
    "ds_green_body": {
        "en": "Watch closely at home. Go to a health facility if the person gets worse, any danger "
              "sign appears, or you are worried. **If you are worried, go.**",
        "sw": "Angalia kwa makini nyumbani. Nenda kituo cha afya hali ikizidi kuwa mbaya, dalili yoyote "
              "ya hatari ikitokea, au ukiwa na wasiwasi. **Ukiwa na wasiwasi, nenda.**",
    },
    "ds_signs_seen": {"en": "Signs you ticked:", "sw": "Dalili ulizoweka alama:"},
    "ds_numbers": {
        "en": "**Emergency numbers (Kenya):** 999 or 112 (free) · Kenya Red Cross 1199. "
              "Outside Kenya, call your local emergency number.",
        "sw": "**Namba za dharura (Kenya):** 999 au 112 (bure) · Kenya Red Cross 1199. "
              "Nje ya Kenya, piga namba ya dharura ya nchi yako.",
    },
    "ds_first_aid": {"en": "While you get help", "sw": "Wakati unatafuta msaada"},
    "ds_note": {
        "en": "This checker follows WHO and Kenyan guidance on danger signs. It does not diagnose and "
              "does not replace a health worker. When in doubt, always go to a health facility.",
        "sw": "Kipimo hiki kinafuata miongozo ya WHO na ya Kenya kuhusu dalili za hatari. Hakitoi "
              "utambuzi na hakichukui nafasi ya mhudumu wa afya. Ukiwa na shaka, nenda kituo cha afya.",
    },

    # Adult
    "a_face": {"en": "Face drooping on one side (uneven smile)", "sw": "Uso umelegea upande mmoja (tabasamu si sawa)"},
    "a_arm": {"en": "Sudden weakness or numbness in an arm or leg, especially one side",
              "sw": "Udhaifu au ganzi ya ghafla kwenye mkono au mguu, hasa upande mmoja"},
    "a_speech": {"en": "Sudden slurred speech or can't understand others",
                 "sw": "Ghafla anaongea kwa shida au haelewi wengine"},
    "a_vision": {"en": "Sudden loss of vision or double vision", "sw": "Ghafla kupoteza uwezo wa kuona au kuona vitu viwili"},
    "a_headache": {"en": "Sudden, very severe headache (the worst ever)",
                   "sw": "Maumivu makali sana ya kichwa ya ghafla (makali kuliko yote)"},
    "a_chest": {"en": "Chest pain or pressure, which may spread to the arm, jaw or back",
                "sw": "Maumivu au kubanwa kifuani, yanayoweza kuenea mkononi, tayani au mgongoni"},
    "a_breath": {"en": "Severe difficulty breathing, even when resting",
                 "sw": "Shida kubwa ya kupumua, hata akiwa amepumzika"},
    "a_faint": {"en": "Fainted, collapsed or very confused", "sw": "Amezimia, ameanguka au amechanganyikiwa sana"},
    "a_fit": {"en": "Convulsions (fits)", "sw": "Degedege (kifafa)"},
    "a_bp_symptoms": {"en": "Blood pressure 180/110 or higher AND headache, chest pain or blurred vision",
                      "sw": "Shinikizo la damu 180/110 au zaidi PAMOJA na maumivu ya kichwa, kifua au kuona ukungu"},
    "a_bp_high": {"en": "Blood pressure 180/110 or higher but feeling well",
                  "sw": "Shinikizo la damu 180/110 au zaidi lakini anajisikia vizuri"},
    "a_legs": {"en": "Swollen legs and breathless when lying flat",
               "sw": "Miguu imevimba na anapumua kwa shida akilala chali"},
    "a_fever": {"en": "High fever, or fever lasting more than 2 days",
                "sw": "Homa kali, au homa ya zaidi ya siku 2"},
    "fa_adult": {
        "en": "- **Note the time** the signs started. Stroke treatment works best within hours.\n"
              "- Do **not** give food, drink or medicine by mouth if they may have had a stroke.\n"
              "- If they are drowsy, lay them **on their side**.\n"
              "- For chest pain: keep them resting and calm, sitting up.\n"
              "- During a fit: move hard objects away, put nothing in the mouth, then turn them on their side.",
        "sw": "- **Andika saa** dalili zilipoanza. Matibabu ya kiharusi hufanya kazi vizuri ndani ya saa chache.\n"
              "- **Usimpe** chakula, kinywaji wala dawa kwa mdomo kama huenda amepata kiharusi.\n"
              "- Akiwa na usingizi mzito, mlaze **kwa ubavu**.\n"
              "- Kwa maumivu ya kifua: mwache apumzike kwa utulivu, akiwa amekaa.\n"
              "- Wakati wa degedege: ondoa vitu vigumu karibu, usiweke kitu mdomoni, kisha mlaze kwa ubavu.",
    },

    # Pregnancy and after birth
    "p_bleeding": {"en": "Bleeding from the vagina", "sw": "Kutokwa na damu ukeni"},
    "p_headache": {"en": "Severe headache with blurred vision", "sw": "Maumivu makali ya kichwa na kuona ukungu"},
    "p_fit": {"en": "Convulsions (fits)", "sw": "Degedege (kifafa)"},
    "p_pain": {"en": "Severe pain in the belly", "sw": "Maumivu makali ya tumbo"},
    "p_fever": {"en": "Fever, or too weak to get out of bed", "sw": "Homa, au dhaifu kiasi cha kushindwa kuamka kitandani"},
    "p_water": {"en": "Water breaks before labour pains start", "sw": "Maji yanatoka kabla ya uchungu kuanza"},
    "p_movement": {"en": "Baby moving less than usual, or stopped moving",
                   "sw": "Mtoto tumboni anacheza kidogo kuliko kawaida, au ameacha kucheza"},
    "p_swelling": {"en": "Swelling of the face or hands", "sw": "Kuvimba uso au mikono"},
    "p_breath": {"en": "Fast or difficult breathing", "sw": "Kupumua haraka au kwa shida"},
    "p_early": {"en": "Labour pains before 37 weeks (more than 3 weeks early)",
                "sw": "Uchungu kabla ya wiki 37 (zaidi ya wiki 3 mapema)"},
    "p_after_bleed": {"en": "After birth: heavy bleeding (soaking a pad in less than an hour)",
                      "sw": "Baada ya kujifungua: kutokwa na damu nyingi (pedi kujaa chini ya saa moja)"},
    "p_after_smell": {"en": "After birth: bad-smelling discharge from the vagina",
                      "sw": "Baada ya kujifungua: uchafu unaonuka ukeni"},
    "p_urine": {"en": "Pain or burning when passing urine", "sw": "Maumivu au kuungua wakati wa kukojoa"},
    "p_feet": {"en": "Swelling of the feet only", "sw": "Kuvimba miguu pekee"},
    "fa_pregnant": {
        "en": "- Take the **Mother & Child Health booklet** (pink book) with you.\n"
              "- If bleeding: lie down on her left side while transport is arranged.\n"
              "- During a fit: protect her from injury, put nothing in the mouth, then turn her on her left side.\n"
              "- Ask someone to come with her, ideally a possible blood donor.",
        "sw": "- Beba **kitabu cha Afya ya Mama na Mtoto** (kitabu cha waridi).\n"
              "- Akitokwa na damu: alale kwa ubavu wa kushoto wakati usafiri unatafutwa.\n"
              "- Wakati wa degedege: mkinge asiumie, usiweke kitu mdomoni, kisha mlaze kwa ubavu wa kushoto.\n"
              "- Mtu aandamane naye, ikiwezekana mtu anayeweza kuchangia damu.",
    },

    # Child 2 months to 5 years
    "c_drink": {"en": "Not able to drink or breastfeed", "sw": "Hawezi kunywa wala kunyonya"},
    "c_vomit": {"en": "Vomits everything", "sw": "Anatapika kila kitu"},
    "c_fit": {"en": "Convulsions (fits) during this illness", "sw": "Degedege (kifafa) katika ugonjwa huu"},
    "c_sleepy": {"en": "Very sleepy or hard to wake up", "sw": "Ana usingizi mzito sana au ni vigumu kumwamsha"},
    "c_dehydration": {"en": "Diarrhoea AND sunken eyes or skin goes back very slowly when pinched",
                      "sw": "Kuhara PAMOJA na macho yaliyoingia ndani au ngozi inarudi polepole sana ikifinywa"},
    "c_chest": {"en": "Lower chest sucks in when breathing in", "sw": "Sehemu ya chini ya kifua inaingia ndani anapovuta pumzi"},
    "c_fever": {"en": "Fever (feels hot)", "sw": "Homa (mwili ni wa moto)"},
    "c_blood_stool": {"en": "Blood in the stool", "sw": "Damu kwenye kinyesi"},
    "c_cough": {"en": "Cough or difficult breathing", "sw": "Kikohozi au shida ya kupumua"},
    "c_diarrhoea": {"en": "Diarrhoea (3 or more watery stools a day)", "sw": "Kuhara (kinyesi cha maji mara 3 au zaidi kwa siku)"},
    "c_breaths": {"en": "Optional: breaths in 1 minute (count while the child is calm)",
                  "sw": "Si lazima: pumzi kwa dakika 1 (hesabu mtoto akiwa ametulia)"},
    "c_age": {"en": "Child's age", "sw": "Umri wa mtoto"},
    "c_age_small": {"en": "2 to 12 months", "sw": "Miezi 2 hadi 12"},
    "c_age_big": {"en": "1 to 5 years", "sw": "Mwaka 1 hadi miaka 5"},
    "c_fast": {"en": "Fast breathing ({n} breaths a minute)", "sw": "Kupumua haraka (pumzi {n} kwa dakika)"},
    "c_how_count": {
        "en": "How to count breathing: lift the child's clothes so you can see the chest or belly. "
              "Count each time it rises, for one full minute, while the child is calm (not crying "
              "or feeding).",
        "sw": "Jinsi ya kuhesabu pumzi: inua nguo za mtoto ili uone kifua au tumbo. Hesabu kila "
              "kinapopanda, kwa dakika moja kamili, mtoto akiwa ametulia (halii wala hanyonyi).",
    },
    "fa_child": {
        "en": "- Keep **breastfeeding** or giving fluids if the child can drink.\n"
              "- For diarrhoea: give **ORS** (and zinc if you have it) after every loose stool.\n"
              "- For fever: undress to light clothing. Test for malaria at the facility.\n"
              "- During a fit: lay the child on their side, put nothing in the mouth.\n"
              "- Take the child's **clinic card / MCH booklet**.",
        "sw": "- Endelea **kunyonyesha** au kumpa maji kama mtoto anaweza kunywa.\n"
              "- Kwa kuhara: mpe **ORS** (na zinki kama unayo) baada ya kila choo cha maji.\n"
              "- Kwa homa: mvue nguo nzito abaki na nyepesi. Apimwe malaria kituoni.\n"
              "- Wakati wa degedege: mlaze mtoto kwa ubavu, usiweke kitu mdomoni.\n"
              "- Beba **kadi ya kliniki / kitabu cha MCH** cha mtoto.",
    },

    # Baby under 2 months
    "n_feed": {"en": "Not feeding well or stopped breastfeeding", "sw": "Hanyonyi vizuri au ameacha kunyonya"},
    "n_fit": {"en": "Convulsions (fits)", "sw": "Degedege (kifafa)"},
    "n_breath": {"en": "Fast breathing (60 or more breaths a minute)", "sw": "Kupumua haraka (pumzi 60 au zaidi kwa dakika)"},
    "n_chest": {"en": "Lower chest sucks in a lot when breathing", "sw": "Sehemu ya chini ya kifua inaingia ndani sana anapopumua"},
    "n_temp": {"en": "Feels hot (fever) or feels cold", "sw": "Mwili ni wa moto (homa) au ni wa baridi"},
    "n_move": {"en": "Moves only when touched, or not at all", "sw": "Anajitikisa tu akiguswa, au hajitikisi kabisa"},
    "n_yellow": {"en": "Yellow palms or soles of the feet", "sw": "Viganja au nyayo za njano"},
    "n_cord": {"en": "Redness or pus around the cord (navel) spreading to the skin",
               "sw": "Wekundu au usaha kwenye kitovu unaoenea kwenye ngozi"},
    "fa_newborn": {
        "en": "- **Babies under 2 months can become very sick very fast. Any danger sign = go now.**\n"
              "- Keep the baby **warm**: skin-to-skin on the mother's chest, covered with a cloth.\n"
              "- Keep breastfeeding on the way if the baby can feed.\n"
              "- Take the **MCH booklet**.",
        "sw": "- **Watoto chini ya miezi 2 wanaweza kuugua sana kwa haraka. Dalili yoyote ya hatari = nenda sasa.**\n"
              "- Mweke mtoto katika **joto**: ngozi kwa ngozi kifuani kwa mama, amefunikwa kwa kitambaa.\n"
              "- Endelea kunyonyesha njiani kama mtoto anaweza kunyonya.\n"
              "- Beba **kitabu cha MCH**.",
    },
})


# Which signs mean "emergency now" (red) and which mean "clinic today" (amber)
# Demonstrations shown for each group
GROUP_DEMOS = {
    "adult": ["fast"],
    "pregnant": ["pregnancy_danger"],
    "child": ["child_danger", "child_breathing"],
    "newborn": ["newborn_danger"],
}

GROUPS = {
    "adult": {
        "red": ["a_face", "a_arm", "a_speech", "a_vision", "a_headache", "a_chest",
                "a_breath", "a_faint", "a_fit", "a_bp_symptoms"],
        "amber": ["a_bp_high", "a_legs", "a_fever"],
        "first_aid": "fa_adult",
    },
    "pregnant": {
        "red": ["p_bleeding", "p_headache", "p_fit", "p_pain", "p_fever", "p_water",
                "p_movement", "p_swelling", "p_breath", "p_early", "p_after_bleed", "p_after_smell"],
        "amber": ["p_urine", "p_feet"],
        "first_aid": "fa_pregnant",
    },
    "child": {
        "red": ["c_drink", "c_vomit", "c_fit", "c_sleepy", "c_dehydration"],
        "amber": ["c_chest", "c_fever", "c_blood_stool"],
        "first_aid": "fa_child",
    },
    "newborn": {
        "red": ["n_feed", "n_fit", "n_breath", "n_chest", "n_temp", "n_move", "n_yellow", "n_cord"],
        "amber": [],
        "first_aid": "fa_newborn",
    },
}

# WHO IMCI fast-breathing cut-offs (breaths per minute)
FAST_BREATHING = {"small": 50, "big": 40}


def triage(group, ticked, breaths=None, child_age="big"):
    """Returns ('red'|'amber'|'green', list of sign texts that led to it)."""
    rules = GROUPS[group]
    red = [s for s in ticked if s in rules["red"]]
    amber = [s for s in ticked if s in rules["amber"]]
    reasons = [t(s) for s in red + amber]
    fast = (group == "child" and breaths is not None
            and breaths >= FAST_BREATHING[child_age])
    if fast:
        reasons.append(t("c_fast", n=breaths))
    if red:
        return "red", reasons
    if amber or fast:
        return "amber", reasons
    return "green", reasons


def render():
    st.header(t("ds_title"))
    st.write(t("ds_intro"))
    st.info(t("ds_numbers"))

    group = st.radio(t("ds_who"), list(GROUPS), format_func=lambda g: t("ds_g_" + g),
                     key="ds_group")
    rules = GROUPS[group]

    with st.expander(demo.watch_label(), expanded=False):
        for name in GROUP_DEMOS[group]:
            demo.show(name)

    st.markdown(f"**{t('ds_tick')}**")
    ticked = [s for s in rules["red"] + rules["amber"]
              if st.checkbox(t(s), key=f"ds_{s}")]

    breaths, child_age = None, "big"
    if group == "child":
        with st.expander(t("c_breaths")):
            st.caption(t("c_how_count"))
            child_age = st.radio(t("c_age"), ["small", "big"],
                                 format_func=lambda a: t("c_age_" + a), horizontal=True,
                                 key="ds_child_age")
            breaths = st.number_input(t("c_breaths"), 5, 150, value=None,
                                      label_visibility="collapsed", key="ds_breaths")
            demo.breathing_practice()

    if not st.button(t("ds_check"), type="primary", width="stretch"):
        st.caption(t("ds_note"))
        return

    level, reasons = triage(group, ticked, breaths, child_age)
    box = {"red": st.error, "amber": st.warning, "green": st.success}[level]
    text = f"### {t('ds_' + level + '_title')}\n{t('ds_' + level + '_body')}"
    if reasons:
        text += f"\n\n**{t('ds_signs_seen')}**\n" + "\n".join(f"- {r}" for r in reasons)
    box(text)

    if level != "green":
        st.markdown(f"**{t('ds_first_aid')}**")
        st.markdown(t(rules["first_aid"]))
        st.info(t("ds_numbers"))
    st.caption(t("ds_note"))