import requests
from config.settings import GROQ_MODEL, GROQ_API_URL
from pipeline.prompt_builder import build_prompt


def get_ai_response(query: str, intent: str, sentiment: str,
                    confidence: float, api_key: str,
                    history: list = None) -> str:
    """
    Sends query + conversation history to Groq LLM.
    Returns the generated response string.
    """
    prompt = build_prompt(query, intent, sentiment, confidence, history)

    try:
        r = requests.post(
            GROQ_API_URL,
            headers={
                "Authorization" : f"Bearer {api_key}",
                "Content-Type"  : "application/json",
            },
            json={
                "model"      : GROQ_MODEL,
                "messages"   : [{"role": "user", "content": prompt}],
                "max_tokens" : 250,
                "temperature": 0.7,
            },
            timeout=30,
        )
        if r.status_code == 200:
            return r.json()["choices"][0]["message"]["content"].strip()
        return f"API Error {r.status_code} — check your key."
    except Exception as e:
        return f"Connection error: {str(e)[:80]}"
