from config.settings import LOW_CONF_THRESHOLD


def build_conversation_context(history: list) -> str:
    """Formats full conversation history into a readable string for the LLM."""
    if not history:
        return ""
    ctx = "\n--- Previous Conversation ---\n"
    for turn in history:
        role = "Customer" if turn["role"] == "user" else "Assistant"
        ctx += f"{role}: {turn['content']}\n"
    ctx += "--- End of Previous Conversation ---\n\n"
    return ctx


def build_prompt(query: str, intent: str, sentiment: str,
                 confidence: float, history: list = None) -> str:
    """
    Builds the full prompt sent to the Groq LLM.
    Includes conversation history, intent, sentiment tone guidance.
    No topic restrictions — responds to anything.
    """
    conv_ctx = build_conversation_context(history)
    ir       = intent.replace("_", " ")

    tone = {
        "negative": "User is frustrated. Be empathetic, calm and solution-focused.",
        "neutral" : "User is making a calm request. Be clear and concise.",
        "positive": "User is happy. Match their energy warmly.",
    }.get(sentiment, "Be helpful and polite.")

    return (
        f"You are a helpful and friendly AI assistant.\n\n"
        f"{conv_ctx}"
        f"User's latest message: \"{query}\"\n"
        f"Detected topic: {ir}\n\n"
        f"Tone guidance: {tone}\n\n"
        f"Use the conversation history above to give a contextually aware response. "
        f"Be natural, helpful and conversational. "
        f"Do not mention intent names, confidence scores or system labels.\n"
    )
