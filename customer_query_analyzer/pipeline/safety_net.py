SAFETY_PATTERNS = {
    "unauthorized_access": [
        "someone else", "someone is using", "unauthori", "hacked", "hack",
        "not me", "wasn't me", "i didn't do", "suspicious login", "unknown login",
        "someone logged", "someone accessed", "strange activity", "unusual activity",
        "unknown transaction", "i didn't make this", "i did not make", "fraudulent login",
    ],
    "report_fraud": [
        "fraud", "scam", "scammed", "cheated", "stolen", "stole", "theft",
        "fake transaction", "unauthorized transaction", "didn't authorize",
        "did not authorize", "money missing", "money gone", "money disappeared",
        "deducted without", "charged without", "debited without my",
    ],
    "emergency_block": [
        "block immediately", "block my card now", "freeze immediately",
        "lost my card", "card stolen", "stolen card", "i lost my",
        "cant find my card", "missing card", "card is missing",
    ],
    "account_compromised": [
        "account compromised", "account breached", "password changed",
        "someone changed my password", "locked out", "cant access my account",
        "cant log in", "cant login", "login not working", "otp not received",
        "not receiving otp", "verification not working",
    ],
}


def pre_classify(query: str):
    """
    Checks query against security keyword patterns.
    Returns (intent, confidence) if matched, else (None, None).
    """
    q = query.lower()
    for intent, keywords in SAFETY_PATTERNS.items():
        for kw in keywords:
            if kw in q:
                return intent, 0.95
    return None, None
