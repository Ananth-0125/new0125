import os
from datetime import datetime

import streamlit as st

from ui.auth import render_auth_status
from ui.reporting import build_history_pdf


def latency_stats() -> dict:
    lats = st.session_state.latencies
    if not lats:
        return None
    return {
        "avg": round(sum(lats) / len(lats)),
        "min": min(lats),
        "max": max(lats),
    }


def render_sidebar(_defaults: dict) -> str:
    """
    Renders the full sidebar.
    Returns the API key entered by the user (or loaded from secrets).
    """
    with st.sidebar:
        st.markdown(
            """
            <div style='padding:6px 0 14px 0; border-bottom:1px solid #C0CDD8; margin-bottom:2px;'>
                <div style='font-size:0.95rem;font-weight:700;color:#333333;font-family:Oswald,sans-serif;letter-spacing:0.5px;'>QUERY ANALYZER</div>
                <div style='font-size:0.62rem;color:#99A0AA;margin-top:2px;font-family:Roboto Mono,monospace;'>BERT + GROQ ENGINE</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        render_auth_status()

        st.markdown(
            "<div style='height:1px;background:#D8E3EC;margin:10px 0;'></div>",
            unsafe_allow_html=True,
        )
        st.markdown("<div class='sb-sec'>API KEY (GROQ)</div>", unsafe_allow_html=True)

        api_key = ""
        on_cloud = (
            os.environ.get("STREAMLIT_SHARING_MODE") or
            os.path.exists("/mount/src")
        )

        if on_cloud:
            try:
                api_key = st.secrets["GROQ_API_KEY"]
                st.markdown(
                    "<div style='font-size:0.69rem;color:#1A7A2A;margin-bottom:8px;font-family:Roboto Mono,monospace;'>"
                    "KEY LOADED FROM SECRETS</div>",
                    unsafe_allow_html=True,
                )
            except Exception:
                api_key = ""

        if not api_key:
            api_key = st.text_input(
                "api_key_input",
                label_visibility="collapsed",
                type="password",
                placeholder="Paste your Groq API key...",
            )
            if api_key:
                masked = (
                    api_key[:4] + "x" * min(len(api_key) - 8, 10) + api_key[-4:]
                    if len(api_key) > 8
                    else "x" * len(api_key)
                )
                st.markdown(
                    f"<div style='font-size:0.69rem;color:#1A7A2A;margin:-2px 0 6px 0;font-family:Roboto Mono,monospace;'>"
                    f"KEY SET: {masked}</div>",
                    unsafe_allow_html=True,
                )

        st.markdown(
            "<div style='font-size:0.68rem;color:#99A0AA;margin:4px 0 8px 0;font-family:Roboto Mono,monospace;'>"
            "FREE · <a href='https://console.groq.com' style='color:#0058A3;text-decoration:none;'>"
            "CONSOLE.GROQ.COM</a></div>",
            unsafe_allow_html=True,
        )

        st.markdown(
            "<div style='height:1px;background:#D8E3EC;margin:10px 0;'></div>",
            unsafe_allow_html=True,
        )
        st.markdown("<div class='sb-sec'>SESSION STATS</div>", unsafe_allow_html=True)

        total = st.session_state.total_queries
        neg = st.session_state.sentiment_counts["negative"]
        neu = st.session_state.sentiment_counts["neutral"]
        pos = st.session_state.sentiment_counts["positive"]
        sec = st.session_state.security_count
        low = st.session_state.lowconf_count
        ls = latency_stats()

        rows = [
            ("TOTAL QUERIES", str(total), "#0058A3"),
            ("NEGATIVE", str(neg), "#CC2200"),
            ("NEUTRAL", str(neu), "#666677"),
            ("POSITIVE", str(pos), "#1A7A2A"),
            ("SECURITY ALERTS", str(sec), "#CC2200"),
            ("LOW CONFIDENCE", str(low), "#A06000"),
        ]
        if ls:
            rows += [
                ("AVG LATENCY", f"{ls['avg']} ms", "#0058A3"),
                ("MIN LATENCY", f"{ls['min']} ms", "#1A7A2A"),
                ("MAX LATENCY", f"{ls['max']} ms", "#CC2200"),
            ]

        for label, value, color in rows:
            st.markdown(
                f"<div style='display:flex;justify-content:space-between;"
                f"font-size:0.76rem;padding:4px 0;border-bottom:1px solid #EEF3FA;font-family:Roboto Mono,monospace;'>"
                f"<span style='color:#99A0AA;'>{label}</span>"
                f"<span style='font-weight:700;color:{color};'>{value}</span>"
                f"</div>",
                unsafe_allow_html=True,
            )

        st.markdown(
            "<div style='height:1px;background:#D8E3EC;margin:12px 0;'></div>",
            unsafe_allow_html=True,
        )

        if st.session_state.history_log:
            pdf_data = build_history_pdf(
                history_log=st.session_state.history_log,
                total_queries=st.session_state.total_queries,
                sentiment_counts=st.session_state.sentiment_counts,
                security_count=st.session_state.security_count,
                lowconf_count=st.session_state.lowconf_count,
                latencies=st.session_state.latencies,
                user_email=(st.session_state.auth_user or {}).get("email", ""),
            )
            st.download_button(
                label="Download History (PDF)",
                data=pdf_data,
                file_name=f"queries_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf",
                mime="application/pdf",
                use_container_width=True,
            )
            st.markdown("<div style='height:6px;'></div>", unsafe_allow_html=True)

        if st.button("Clear Conversation", use_container_width=True):
            for key, value in _defaults.items():
                if isinstance(value, dict):
                    st.session_state[key] = value.copy()
                elif isinstance(value, list):
                    st.session_state[key] = []
                else:
                    st.session_state[key] = value
            st.rerun()

    return api_key
