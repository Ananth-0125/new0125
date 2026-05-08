import streamlit as st

from ui.styles    import CSS
from ui.auth      import init_auth_state, render_auth_page
from ui.sidebar   import render_sidebar
from ui.chat      import render_chat
from ui.analytics import render_analytics, render_history_table
from model.loader import get_model_path, load_model


def _reset_analyzer_state(defaults: dict) -> None:
    for key, value in defaults.items():
        if isinstance(value, dict):
            st.session_state[key] = value.copy()
        elif isinstance(value, list):
            st.session_state[key] = []
        else:
            st.session_state[key] = value


st.set_page_config(
    page_title="Customer Query Analyzer",
    page_icon="Q",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(CSS, unsafe_allow_html=True)

_defaults = {
    "messages": [],
    "conv_history": [],
    "history_log": [],
    "total_queries": 0,
    "sentiment_counts": {"negative": 0, "neutral": 0, "positive": 0},
    "security_count": 0,
    "lowconf_count": 0,
    "bert_loaded": False,
    "last_result": None,
    "intent_freq": {},
    "latencies": [],
    "feedback": {},
    "api_key": "",
    "active_user_uid": "",
}

for key, value in _defaults.items():
    if key not in st.session_state:
        if isinstance(value, dict):
            st.session_state[key] = value.copy()
        elif isinstance(value, list):
            st.session_state[key] = []
        else:
            st.session_state[key] = value

init_auth_state()

if not st.session_state.is_authenticated:
    render_auth_page()
    st.stop()

current_uid = (st.session_state.auth_user or {}).get("uid", "")
if current_uid and st.session_state.active_user_uid != current_uid:
    _reset_analyzer_state(_defaults)
    st.session_state.active_user_uid = current_uid

api_key = render_sidebar(_defaults)
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
