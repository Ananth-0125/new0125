import json
import os
from pathlib import Path

import torch
import streamlit as st
from transformers import BertTokenizer
from huggingface_hub import snapshot_download

from config.settings import HF_REPO_ID
from model.bert_model import MultiTaskBERT


@st.cache_resource(show_spinner=False)
def get_model_path() -> str:
    """
    Downloads model files from HuggingFace Hub if not already cached.
    Returns path to the local cache directory.
    """
    cache_dir = (
        Path.home() / ".cache" / "hf_models" / HF_REPO_ID.replace("/", "_")
    )
    cache_dir.mkdir(parents=True, exist_ok=True)

    bert_file = cache_dir / "bert_best.pt"
    map_file = cache_dir / "intent_label_map.json"

    if not bert_file.exists() or not map_file.exists():
        with st.spinner("Downloading model from Hugging Face... (~1-2 minutes)"):
            snapshot_download(
                repo_id=HF_REPO_ID,
                local_dir=str(cache_dir),
                local_dir_use_symlinks=False,
                resume_download=True,
            )
    return str(cache_dir)


@st.cache_resource(show_spinner=False)
def load_model(model_dir: str, data_dir: str):
    """
    Loads BERT model, tokenizer and intent label map from disk.
    Returns: (model, tokenizer, id2intent, oos_id, device)
    """
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    with open(os.path.join(data_dir, "intent_label_map.json")) as f:
        id2intent = json.load(f)

    n      = len(id2intent)
    oos_id = next((int(k) for k, v in id2intent.items() if v == "oos"), -1)

    tokenizer = BertTokenizer.from_pretrained(model_dir)

    model = MultiTaskBERT(num_intents=n, num_sentiments=3)
    model.load_state_dict(
        torch.load(
            os.path.join(model_dir, "bert_best.pt"),
            map_location=device,
            weights_only=True,
        )
    )
    model.to(device).eval()

    return model, tokenizer, id2intent, oos_id, device
