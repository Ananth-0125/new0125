from datetime import datetime
from io import BytesIO

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle


def summarize_session_sentiment(sentiment_counts: dict) -> str:
    total = sum(sentiment_counts.values())
    if total == 0:
        return "No session data"

    winners = [
        name for name, value in sentiment_counts.items()
        if value == max(sentiment_counts.values()) and value > 0
    ]
    if len(winners) == 1:
        return winners[0].title()
    return "Mixed"


def _safe(value) -> str:
    return "" if value is None else str(value)


def build_history_pdf(
    history_log: list,
    total_queries: int,
    sentiment_counts: dict,
    security_count: int,
    lowconf_count: int,
    latencies: list,
    user_email: str = "",
) -> bytes:
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=36,
        rightMargin=36,
        topMargin=36,
        bottomMargin=36,
    )

    styles = getSampleStyleSheet()
    title_style = styles["Title"]
    title_style.textColor = colors.HexColor("#0058A3")

    body_style = styles["BodyText"]
    body_style.fontSize = 10
    body_style.leading = 13

    table_text_style = ParagraphStyle(
        "TableText",
        parent=styles["BodyText"],
        fontSize=8.5,
        leading=10.5,
    )

    session_sentiment = summarize_session_sentiment(sentiment_counts)
    avg_latency = f"{round(sum(latencies) / len(latencies))} ms" if latencies else "N/A"
    min_latency = f"{min(latencies)} ms" if latencies else "N/A"
    max_latency = f"{max(latencies)} ms" if latencies else "N/A"
    sentiment_breakdown = (
        f"Negative: {sentiment_counts.get('negative', 0)} | "
        f"Neutral: {sentiment_counts.get('neutral', 0)} | "
        f"Positive: {sentiment_counts.get('positive', 0)}"
    )

    story = [
        Paragraph("Customer Query Analyzer Session Report", title_style),
        Spacer(1, 0.15 * inch),
        Paragraph(
            f"Generated on {datetime.now().strftime('%Y-%m-%d %H:%M')}<br/>"
            f"Signed-in user: {_safe(user_email) or 'N/A'}",
            body_style,
        ),
        Spacer(1, 0.2 * inch),
    ]

    summary_table = Table(
        [
            ["Metric", "Value"],
            ["Total Queries", _safe(total_queries)],
            ["Session Sentiment", session_sentiment],
            ["Sentiment Breakdown", sentiment_breakdown],
            ["Security Alerts", _safe(security_count)],
            ["Low Confidence", _safe(lowconf_count)],
            ["Average Latency", avg_latency],
            ["Minimum Latency", min_latency],
            ["Maximum Latency", max_latency],
        ],
        colWidths=[2.1 * inch, 4.9 * inch],
        repeatRows=1,
    )
    summary_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0058A3")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
                ("FONTSIZE", (0, 0), (-1, -1), 9),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#C0CDD8")),
                ("BACKGROUND", (0, 1), (-1, -1), colors.HexColor("#F7FAFD")),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 6),
                ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ]
        )
    )
    story.extend([summary_table, Spacer(1, 0.25 * inch)])

    table_rows = [
        ["Time", "Query", "Intent", "Confidence", "Sentiment", "Status", "Latency", "Feedback"]
    ]
    for item in history_log:
        table_rows.append(
            [
                Paragraph(_safe(item.get("Time")), table_text_style),
                Paragraph(_safe(item.get("Query")), table_text_style),
                Paragraph(_safe(item.get("Intent")), table_text_style),
                Paragraph(_safe(item.get("Confidence")), table_text_style),
                Paragraph(_safe(item.get("Sentiment")), table_text_style),
                Paragraph(_safe(item.get("Status")), table_text_style),
                Paragraph(_safe(item.get("Latency")), table_text_style),
                Paragraph(_safe(item.get("Feedback")), table_text_style),
            ]
        )

    history_table = Table(
        table_rows,
        colWidths=[0.65 * inch, 1.85 * inch, 1.15 * inch, 0.8 * inch, 0.85 * inch, 0.75 * inch, 0.7 * inch, 0.7 * inch],
        repeatRows=1,
    )
    history_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0F172A")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, 0), 8.5),
                ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#D8E3EC")),
                ("BACKGROUND", (0, 1), (-1, -1), colors.white),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 4),
                ("RIGHTPADDING", (0, 0), (-1, -1), 4),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ]
        )
    )

    story.append(Paragraph("Session Query History", styles["Heading2"]))
    story.append(Spacer(1, 0.1 * inch))
    story.append(history_table)

    doc.build(story)
    return buffer.getvalue()
