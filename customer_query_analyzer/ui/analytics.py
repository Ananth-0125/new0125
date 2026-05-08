import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from config.settings import SENTIMENT_LABEL


def render_analytics() -> None:
    """Renders the full analytics panel column."""

    st.markdown('<div class="section-label">▸ Analysis Panel</div>', unsafe_allow_html=True)

    if st.session_state.last_result:
        r = st.session_state.last_result

        # ── Metric tiles ─────────────────────────────────
        m1, m2, m3 = st.columns(3)
        with m1:
            st.markdown(
                f'<div class="metric-tile">'
                f'<div class="val" style="font-size:0.72rem;line-height:1.4;word-break:break-word;">'
                f'{r["intent"].replace("_"," ").upper()}</div>'
                f'<div class="lbl">Intent</div></div>',
                unsafe_allow_html=True,
            )
        with m2:
            st.markdown(
                f'<div class="metric-tile">'
                f'<div class="val" style="font-size:0.85rem;">'
                f'{SENTIMENT_LABEL.get(r["sentiment"], r["sentiment"]).upper()}</div>'
                f'<div class="lbl">Sentiment</div></div>',
                unsafe_allow_html=True,
            )
        with m3:
            fl = "SECURITY" if r["pre_classified"] else ("LOW CONF" if r["low_confidence"] else "NORMAL")
            fv = "#CC2200" if r["pre_classified"] else ("#A06000" if r["low_confidence"] else "#1A7A2A")
            st.markdown(
                f'<div class="metric-tile">'
                f'<div class="val" style="font-size:0.78rem;color:{fv};">{fl}</div>'
                f'<div class="lbl">Status</div></div>',
                unsafe_allow_html=True,
            )

        st.markdown("<div style='height:14px;'></div>", unsafe_allow_html=True)

        # ── Confidence gauge ─────────────────────────────
        st.markdown('<div class="section-label">▸ Intent Confidence</div>', unsafe_allow_html=True)
        conf_pct    = round(r["intent_confidence"] * 100, 1)
        gauge_color = "#CC2200" if r["pre_classified"] else ("#F59E0B" if conf_pct < 50 else "#0058A3")
        fig_g = go.Figure(go.Indicator(
            mode="gauge+number", value=conf_pct,
            number={"suffix": "%", "font": {"size": 20, "color": "#333333", "family": "Roboto Mono"}},
            gauge={
                "axis"       : {"range": [0, 100], "tickwidth": 1, "tickcolor": "#C0CDD8",
                                "tickfont": {"size": 9, "color": "#99A0AA"}},
                "bar"        : {"color": gauge_color, "thickness": 0.24},
                "bgcolor"    : "#F5F5F5",
                "bordercolor": "#C0CDD8",
                "borderwidth": 1,
                "steps"      : [
                    {"range": [0,  40], "color": "#FEE8E8"},
                    {"range": [40, 70], "color": "#FFF8E0"},
                    {"range": [70,100], "color": "#E8FEEE"},
                ],
            },
        ))
        fig_g.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", height=155,
            margin=dict(l=16, r=16, t=8, b=8),
            font=dict(family="Roboto Mono", color="#333333"),
        )
        st.plotly_chart(fig_g, use_container_width=True, config={"displayModeBar": False})

        # ── Top 3 predictions ────────────────────────────
        st.markdown('<div class="section-label">▸ Top 3 Predictions</div>', unsafe_allow_html=True)
        bar_cls = "bar-red" if r["pre_classified"] else "bar-blue"
        for name, score in r["top3_intents"]:
            st.markdown(
                f'<div style="margin-bottom:9px;">'
                f'<div style="display:flex;justify-content:space-between;font-size:0.74rem;margin-bottom:3px;font-family:Roboto Mono,monospace;">'
                f'<span style="color:#666677;">{name.replace("_"," ").upper()}</span>'
                f'<span style="color:#0058A3;font-weight:700;">{score}%</span>'
                f'</div>'
                f'<div class="bar-track"><div class="{bar_cls}" style="width:{min(score,100)}%;"></div></div>'
                f'</div>',
                unsafe_allow_html=True,
            )

        # ── Sentiment breakdown ──────────────────────────
        st.markdown('<div class="section-label">▸ Sentiment Breakdown</div>', unsafe_allow_html=True)
        ss  = r["sentiment_scores"]
        fig = go.Figure(go.Bar(
            x=list(ss.values()), y=["Negative", "Neutral", "Positive"],
            orientation="h", marker_color=["#CC2200", "#99A0AA", "#1A7A2A"],
            text=[f"{v}%" for v in ss.values()], textposition="auto",
            textfont=dict(color="#333333", size=11, family="Roboto Mono"),
        ))
        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#666677", family="Roboto Mono"), height=125,
            margin=dict(l=0, r=0, t=0, b=0),
            xaxis=dict(showgrid=False, showticklabels=False, range=[0, 115]),
            yaxis=dict(showgrid=False, tickfont=dict(size=10, color="#666677")),
            showlegend=False,
        )
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    else:
        st.markdown(
            '<div style="text-align:center;padding:60px 20px;background:#FFFFFF;'
            'border:1px solid #C0CDD8;border-radius:8px;">'
            '<div style="font-size:2rem;margin-bottom:10px;opacity:0.2;color:#0058A3;">▶</div>'
            '<div style="font-size:0.84rem;color:#99A0AA;font-family:Roboto Mono,monospace;">ANALYSIS RESULTS WILL APPEAR AFTER YOUR FIRST QUERY.</div>'
            '<div style="font-size:0.73rem;color:#C0CDD8;margin-top:5px;font-family:Roboto Mono,monospace;">TYPE A QUERY ABOVE AND CLICK SEND</div>'
            '</div>',
            unsafe_allow_html=True,
        )

    # ── Session sentiment pie ────────────────────────────
    if st.session_state.total_queries > 0:
        st.markdown("<div style='height:10px;'></div>", unsafe_allow_html=True)
        st.markdown('<div class="section-label">▸ Session Sentiment</div>', unsafe_allow_html=True)
        counts = st.session_state.sentiment_counts
        fig2   = go.Figure(go.Pie(
            labels=["Negative", "Neutral", "Positive"],
            values=[counts["negative"], counts["neutral"], counts["positive"]],
            hole=0.55, marker_colors=["#CC2200", "#99A0AA", "#1A7A2A"],
            textfont=dict(size=10, family="Roboto Mono"),
        ))
        fig2.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", font=dict(color="#666677", family="Roboto Mono"),
            height=185, margin=dict(l=0, r=0, t=0, b=0), showlegend=True,
            legend=dict(orientation="h", yanchor="bottom", y=-0.22, xanchor="center", x=0.5, font=dict(size=10, color="#666677")),
            annotations=[dict(
                text=f"<b>{st.session_state.total_queries}</b>",
                x=0.5, y=0.5, font=dict(size=16, color="#0058A3", family="Oswald"), showarrow=False,
            )],
        )
        st.plotly_chart(fig2, use_container_width=True, config={"displayModeBar": False})

    # ── Intent frequency ─────────────────────────────────
    if st.session_state.intent_freq:
        st.markdown("<div style='height:10px;'></div>", unsafe_allow_html=True)
        st.markdown('<div class="section-label">▸ Intent Frequency</div>', unsafe_allow_html=True)
        sorted_i = sorted(
            st.session_state.intent_freq.items(), key=lambda x: x[1], reverse=True
        )[:6]
        fig3 = go.Figure(go.Bar(
            x=[x[1] for x in sorted_i], y=[x[0].upper() for x in sorted_i],
            orientation="h", marker_color="#0058A3", opacity=0.85,
            text=[x[1] for x in sorted_i], textposition="auto",
            textfont=dict(color="#ffffff", size=10, family="Roboto Mono"),
        ))
        fig3.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#666677", family="Roboto Mono"),
            height=max(110, len(sorted_i) * 30),
            margin=dict(l=0, r=0, t=0, b=0),
            xaxis=dict(showgrid=False, showticklabels=False),
            yaxis=dict(showgrid=False, tickfont=dict(size=9, color="#666677")),
            showlegend=False,
        )
        st.plotly_chart(fig3, use_container_width=True, config={"displayModeBar": False})


def render_history_table() -> None:
    """Renders the query history table below the main layout."""
    if st.session_state.history_log:
        st.markdown("<div style='height:6px;'></div>", unsafe_allow_html=True)
        st.markdown('<div class="section-label">▸ Query History</div>', unsafe_allow_html=True)
        df = pd.DataFrame(st.session_state.history_log)
        st.dataframe(
            df, use_container_width=True, hide_index=True,
            column_config={
                "Query"     : st.column_config.TextColumn("Query",     width="large"),
                "Intent"    : st.column_config.TextColumn("Intent",    width="medium"),
                "Confidence": st.column_config.TextColumn("Conf",      width="small"),
                "Sentiment" : st.column_config.TextColumn("Sentiment", width="small"),
                "Status"    : st.column_config.TextColumn("Status",    width="small"),
                "Latency"   : st.column_config.TextColumn("Latency",   width="small"),
                "Feedback"  : st.column_config.TextColumn("Feedback",  width="small"),
            },
        )
