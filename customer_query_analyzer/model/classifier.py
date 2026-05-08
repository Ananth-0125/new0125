import re
import torch
from config.settings import SENTIMENT_NAMES, LOW_CONF_THRESHOLD, MAX_LENGTH
from pipeline.safety_net import pre_classify


def clean_text(text: str) -> str:
    """Normalizes query text before feeding to BERT."""
    text = text.strip().lower()
    text = re.sub(r"\s+", " ", text)
    text = re.sub(r"[^\w\s\'\-\?\!\.,]", "", text)
    text = re.sub(r"(\w)\1{3,}", r"\1\1", text)
    return text


@torch.no_grad()
def classify(query: str, model, tokenizer, id2intent: dict, oos_id: int, device) -> dict:
    """
    Runs the full classification pipeline on a query.
    Returns intent, confidence, top3, sentiment, scores, flags.
    """
    cq = clean_text(query)

    # Safety net check first
    override_intent, override_conf = pre_classify(cq)

    # BERT inference
    enc = tokenizer(
        cq,
        max_length=MAX_LENGTH,
        padding="max_length",
        truncation=True,
        return_tensors="pt",
    )
    intent_logits, sentiment_logits = model(
        enc["input_ids"].to(device),
        enc["attention_mask"].to(device),
        enc["token_type_ids"].to(device),
    )

    ip   = torch.softmax(intent_logits,   dim=-1)[0]
    sp   = torch.softmax(sentiment_logits, dim=-1)[0]
    iid  = ip.argmax().item()
    sid  = sp.argmax().item()
    conf = ip[iid].item()

    # Determine final intent
    if override_intent:
        intent_name = override_intent
        conf        = override_conf
        low         = False
        pre         = True
    elif conf < LOW_CONF_THRESHOLD and oos_id >= 0:
        intent_name = "out_of_scope"
        low         = True
        pre         = False
    else:
        intent_name = id2intent[str(iid)]
        low         = False
        pre         = False

    # Top 3 predictions
    t3i = ip.topk(3).indices.cpu().numpy()
    t3s = ip.topk(3).values.cpu().numpy()

    return {
        "intent"              : intent_name,
        "intent_confidence"   : round(conf, 4),
        "top3_intents"        : [
            (id2intent[str(i)], round(float(s) * 100, 1))
            for i, s in zip(t3i, t3s)
        ],
        "sentiment"           : SENTIMENT_NAMES[sid],
        "sentiment_confidence": round(sp[sid].item(), 4),
        "sentiment_scores"    : {
            "negative": round(sp[0].item() * 100, 1),
            "neutral" : round(sp[1].item() * 100, 1),
            "positive": round(sp[2].item() * 100, 1),
        },
        "low_confidence": low,
        "pre_classified": pre,
    }
