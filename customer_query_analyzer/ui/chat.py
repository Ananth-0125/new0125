import time
import streamlit as st
from datetime import datetime
from config.settings import SENTIMENT_LABEL
from model.classifier import classify
from pipeline.llm import get_ai_response


EXAMPLES = [
    "What is my account balance?",
    "I lost my card, block it now",
    "Someone hacked my account",
    "Book a flight to Chennai",
    "Translate hello to French",
    "Late delivery, I am frustrated",
]


def render_chat(api_key: str) -> None:
    """Renders the full chat interface column."""

    st.markdown('<div class="section-label">▸ Chat Interface</div>', unsafe_allow_html=True)

    # ── Chat window ──────────────────────────────────────
    if not st.session_state.messages:
        chat_html = """
        <div class="chat-window">
            <div class="empty-state">
                <div style="font-size:2.5rem;margin-bottom:12px;opacity:0.25;color:#0058A3;">▶</div>
                <div class="text">Model loaded — start a conversation</div>
                <div class="hint">
                    Try: "What is my account balance?" &nbsp;&middot;&nbsp;
                    "Someone hacked my account" &nbsp;&middot;&nbsp;
                    "I lost my card"
                </div>
            </div>
        </div>"""
    else:
        chat_html = '<div class="chat-window"><div style="overflow:auto">'
        for msg in st.session_state.messages:
            if msg["role"] == "user":
                chat_html += (
                    f'<div class="bubble-user">{msg["content"]}</div>'
                    f'<div class="msg-meta" style="justify-content:flex-end;">'
                    f'{msg["time"]}</div>'
                )
            else:
                is_sec  = msg.get("pre_classified", False)
                is_low  = msg.get("low_confidence", False)
                bubble  = "bubble-security" if is_sec else "bubble-bot"
                i_label = msg.get("intent", "").replace("_", " ").upper()
                s       = msg.get("sentiment", "neutral")
                s_cls   = {"negative":"t-neg","neutral":"t-neu","positive":"t-pos"}.get(s, "t-neu")
                fb      = msg.get("feedback", "")
                fb_tag  = ""
                if fb == "up":     fb_tag = ' <span class="tag t-good">▲ HELPFUL</span>'
                elif fb == "down": fb_tag = ' <span class="tag t-bad">▼ NOT HELPFUL</span>'

                tags = (
                    f'<span class="tag t-intent">{i_label}</span> '
                    f'<span class="tag {s_cls}">{SENTIMENT_LABEL.get(s, s).upper()}</span>'
                )
                if is_sec: tags += ' <span class="tag t-sec">⚠ SECURITY</span>'
                if is_low: tags += ' <span class="tag t-low">~ LOW CONF</span>'
                tags += (
                    f'{fb_tag} <span style="color:#C0CDD8;font-size:0.6rem;">'
                    f'{msg.get("time","")} &middot; {msg.get("latency","")}</span>'
                )
                chat_html += (
                    f'<div class="{bubble}">{msg["content"]}</div>'
                    f'<div class="msg-meta">{tags}</div>'
                )
        chat_html += '</div></div>'

    st.markdown(chat_html, unsafe_allow_html=True)

    # ── Input form ───────────────────────────────────────
    with st.form("chat_form", clear_on_submit=True):
        input_col, arrow_col = st.columns([11, 1])
        with input_col:
            user_input = st.text_input(
                "input_field",
                label_visibility="collapsed",
                placeholder="Type your query here...",
            )
        with arrow_col:
            submitted = st.form_submit_button("➡️", use_container_width=True)

    # ── Feedback ─────────────────────────────────────────
    bot_msgs = [m for m in st.session_state.messages if m["role"] == "bot"]
    if bot_msgs:
        last_idx = len(st.session_state.messages) - 1
        while last_idx >= 0 and st.session_state.messages[last_idx]["role"] != "bot":
            last_idx -= 1
        if last_idx >= 0 and st.session_state.messages[last_idx].get("feedback", "") == "":
            st.markdown(
                "<div style='font-size:0.67rem;color:#99A0AA;margin:2px 0 4px 2px;"
                "font-family:Roboto Mono,monospace;'>WAS THIS RESPONSE HELPFUL?</div>",
                unsafe_allow_html=True,
            )
            fb1, fb2, _ = st.columns([1, 1, 6])
            with fb1:
                if st.button("▲ Yes", key="fb_up", use_container_width=True):
                    st.session_state.messages[last_idx]["feedback"] = "up"
                    if st.session_state.history_log:
                        st.session_state.history_log[-1]["Feedback"] = "Yes"
                    st.rerun()
            with fb2:
                if st.button("▼ No", key="fb_down", use_container_width=True):
                    st.session_state.messages[last_idx]["feedback"] = "down"
                    if st.session_state.history_log:
                        st.session_state.history_log[-1]["Feedback"] = "No"
                    st.rerun()

    # ── Quick examples ───────────────────────────────────
    st.markdown(
        "<div style='font-size:0.63rem;color:#99A0AA;margin:8px 0 5px 0;"
        "font-family:Roboto Mono,monospace;letter-spacing:1.5px;'>▸ QUICK EXAMPLES</div>",
        unsafe_allow_html=True,
    )
    eq1, eq2, eq3 = st.columns(3)
    for col, ex in zip([eq1, eq2, eq3, eq1, eq2, eq3], EXAMPLES):
        with col:
            if st.button(ex, key=f"ex_{ex[:10].replace(' ','_')}", use_container_width=True):
                st.session_state["_prefill"] = ex
                st.rerun()

    if "_prefill" in st.session_state:
        user_input = st.session_state.pop("_prefill")
        submitted  = True

    # ── Process query ────────────────────────────────────
    if submitted and user_input and user_input.strip():
        if not st.session_state.bert_loaded:
            st.warning("Model not loaded. Please wait.")
        elif not api_key:
            st.warning("Please paste your Groq API key in the sidebar.")
        else:
            with st.spinner("Analyzing..."):
                t0 = time.time()
                result = classify(
                    user_input,
                    st.session_state.model,
                    st.session_state.tokenizer,
                    st.session_state.id2intent,
                    st.session_state.oos_id,
                    st.session_state.device,
                )
                response = get_ai_response(
                    user_input,
                    result["intent"],
                    result["sentiment"],
                    result["intent_confidence"],
                    api_key,
                    st.session_state.conv_history,
                )
                latency = round((time.time() - t0) * 1000)
                now     = datetime.now().strftime("%H:%M")

            # Update history
            st.session_state.conv_history.append({"role": "user",  "content": user_input})
            st.session_state.conv_history.append({"role": "model", "content": response})

            st.session_state.messages.append({"role": "user", "content": user_input, "time": now})
            st.session_state.messages.append({
                "role"          : "bot",
                "content"       : response,
                "intent"        : result["intent"],
                "sentiment"     : result["sentiment"],
                "pre_classified": result["pre_classified"],
                "low_confidence": result["low_confidence"],
                "time"          : now,
                "latency"       : f"{latency}ms",
                "feedback"      : "",
            })

            st.session_state.total_queries += 1
            st.session_state.sentiment_counts[result["sentiment"]] += 1
            st.session_state.latencies.append(latency)
            if result["pre_classified"]: st.session_state.security_count += 1
            if result["low_confidence"]: st.session_state.lowconf_count  += 1

            ik = result["intent"].replace("_", " ")
            st.session_state.intent_freq[ik] = st.session_state.intent_freq.get(ik, 0) + 1
            st.session_state.last_result = {
                **result, "response": response, "latency": latency, "query": user_input
            }

            flag = (
                "Security" if result["pre_classified"]
                else ("Low conf" if result["low_confidence"] else "OK")
            )
            st.session_state.history_log.append({
                "Time"      : now,
                "Query"     : user_input[:44] + "..." if len(user_input) > 44 else user_input,
                "Intent"    : ik,
                "Confidence": f"{result['intent_confidence']*100:.1f}%",
                "Sentiment" : SENTIMENT_LABEL.get(result["sentiment"], result["sentiment"]),
                "Status"    : flag,
                "Latency"   : f"{latency}ms",
                "Feedback"  : "",
            })
            st.rerun()
