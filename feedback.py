"""'Was this page helpful?' at the bottom of every page.

Feedback is anonymous: only the page, thumbs up/down, an optional comment,
the language and the time are stored. No name or email.
"""

import streamlit as st

import chp_store
import i18n
from i18n import t

i18n.register({
    "fb_question": {"en": "Was this page helpful?", "sw": "Je, ukurasa huu umekusaidia?"},
    "fb_comment": {"en": "What could be better? (optional, don't include personal details)",
                   "sw": "Nini kingeweza kuwa bora? (si lazima, usiweke taarifa zako binafsi)"},
    "fb_send": {"en": "Send feedback", "sw": "Tuma maoni"},
    "fb_thanks": {"en": "Thank you! Your feedback helps improve this service. 🙏",
                  "sw": "Asante! Maoni yako yanasaidia kuboresha huduma hii. 🙏"},
    "fb_anon": {"en": "Feedback is anonymous: your name and email are not saved with it.",
                "sw": "Maoni hayana jina: jina lako na barua pepe hazihifadhiwi pamoja nayo."},
})


def render(page):
    done = st.session_state.setdefault("fb_done", set())
    with st.container(border=True):
        if page in done:
            st.caption(t("fb_thanks"))
            return
        st.markdown(f"**{t('fb_question')}**")
        rating = st.feedback("thumbs", key=f"fb_rating_{page}")  # 1 = 👍, 0 = 👎
        if rating is None:
            return
        comment = st.text_area(t("fb_comment"), max_chars=500, key=f"fb_comment_{page}")
        if st.button(t("fb_send"), key=f"fb_send_{page}", type="primary"):
            try:
                chp_store.save_feedback(page, rating == 1, comment.strip(), i18n.lang())
                done.add(page)
                st.rerun()
            except Exception:
                st.error(t("db_unavailable"))
        st.caption(t("fb_anon"))