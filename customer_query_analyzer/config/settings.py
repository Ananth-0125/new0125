
# Groq LLM
GROQ_MODEL  = "llama-3.1-8b-instant"
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"

# HuggingFace
HF_REPO_ID  = "YamiChowdary/customer-query-analyzer-bert"

# BERT
BERT_BASE_MODEL = "bert-base-uncased"
MAX_LENGTH      = 64
DROPOUT         = 0.3
NUM_SENTIMENTS  = 3

# Classification
LOW_CONF_THRESHOLD = 0.20

# Sentiment
SENTIMENT_NAMES = ["negative", "neutral", "positive"]
SENTIMENT_LABEL = {
    "negative": "Negative",
    "neutral" : "Neutral",
    "positive": "Positive",
}
