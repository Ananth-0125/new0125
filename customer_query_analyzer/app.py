from copy import deepcopy

import streamlit as st

from ui.styles    import CSS
from ui.auth      import init_auth_state, render_auth_page
from ui.sidebar   import render_sidebar
from ui.chat      import render_chat
from ui.analytics import render_analytics, render_history_table
from model.loader import get_model_path, load_model


USER_STATE_DEFAULTS = {
    "messages": [],
    "conv_history": [],
    "history_log": [],
    "total_queries": 0,
    "sentiment_counts": {"negative": 0, "neutral": 0, "positive": 0},
    "security_count": 0,
    "lowconf_count": 0,
    "last_result": None,
    "intent_freq": {},
    "latencies": [],
    "feedback": {},
}

GLOBAL_DEFAULTS = {
    "bert_loaded": False,
    "api_key": "",
    "active_user_uid": "",
    "user_state_store": {},
}


def _clone_default(value):
    return deepcopy(value)


def _init_state(defaults: dict) -> None:
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = _clone_default(value)


def _save_user_state(uid: str) -> None:
    if not uid:
        return

    st.session_state.user_state_store[uid] = {
        key: _clone_default(st.session_state[key])
        for key in USER_STATE_DEFAULTS
    }


def _load_user_state(uid: str) -> None:
    saved = st.session_state.user_state_store.get(uid)
    source = saved if saved is not None else USER_STATE_DEFAULTS
    for key, value in source.items():
        st.session_state[key] = _clone_default(value)


st.set_page_config(
    page_title="Customer Query Analyzer",
    page_icon="Q",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(CSS, unsafe_allow_html=True)

_init_state(USER_STATE_DEFAULTS)
_init_state(GLOBAL_DEFAULTS)
init_auth_state()

if not st.session_state.is_authenticated:
    pending_logout_uid = st.session_state.get("pending_logout_uid", "")
    if pending_logout_uid:
        _save_user_state(pending_logout_uid)
        st.session_state.active_user_uid = ""
        st.session_state.pending_logout_uid = ""
    render_auth_page()
    st.stop()

current_uid = (st.session_state.auth_user or {}).get("uid", "")
previous_uid = st.session_state.active_user_uid

if current_uid and current_uid != previous_uid:
    if previous_uid:
        _save_user_state(previous_uid)
    _load_user_state(current_uid)
    st.session_state.active_user_uid = current_uid
    st.session_state.pending_logout_uid = ""

api_key = render_sidebar(USER_STATE_DEFAULTS)
st.session_state.api_key = api_key

if not st.session_state.bert_loaded:
    with st.spinner("Loading BERT model from Hugging Face... (first time ~1-2 minutes)"):
        try:
            model_path = get_model_path()
            mdl, tok, i2i, oid, dev = load_model(model_path, model_path)
            st.session_state.update({
                "bert_loaded": True,
                "model": mdl,
                "tokenizer": tok,
                "id2intent": i2i,
                "oos_id": oid,
                "device": dev,
            })
            st.success("BERT model loaded successfully!")
        except Exception as exc:
            st.error(f"Failed to load model: {exc}")
            st.info("Please check internet connection and that the Hugging Face repo is public.")
            st.stop()

st.markdown(
    """
    <div class="page-header">
        <div class="header-tags">
            <span class="htag">BERT MULTI-TASK</span>
            <span class="htag">151 INTENTS</span>
            <span class="htag">SAFETY NET</span>
            <span class="htag">GROQ LLM</span>
        </div>
        <h1>▶ Customer Query Analyzer</h1>
        <p>INTENT CLASSIFICATION &middot; SENTIMENT ANALYSIS &middot; AUTOMATED RESPONSE GENERATION</p>
    </div>
    """,
    unsafe_allow_html=True,
)

col_chat, col_right = st.columns([1.05, 0.95], gap="large")

with col_chat:
    render_chat(api_key)

with col_right:
    render_analytics()

render_history_table()
