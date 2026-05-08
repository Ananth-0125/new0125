# Customer Query Analyzer
  project that combines a fine-tuned BERT model with a large language model to build an intelligent customer service chatbot. The system classifies what a customer is asking about, detects their emotional tone, and generates a helpful, context-aware response — all in real time.

This project was built from scratch, including dataset preprocessing, model training, pipeline design, and a fully deployed web application.

---

## What This Project Does 

When a customer types a message, three things happen in sequence:

1. The message is first checked against a safety net that catches security-critical queries like fraud reports or unauthorized account access. These are handled immediately without waiting for the model, because speed matters in security situations.

2. The message is then passed to a fine-tuned BERT model that was trained on the CLINC150 dataset. The model predicts the customer's intent (what they want) and their sentiment (how they feel about it) at the same time using two separate classification heads.

3. The predicted intent, sentiment, and the full conversation history are combined into a structured prompt that is sent to the Groq LLM. The LLM generates a natural, human-sounding response that is aware of everything said earlier in the conversation.

The result is a chatbot that understands not just what the customer is asking, but also how they feel, and responds appropriately.

---

## The Dataset

The model was trained on **CLINC150** (clinc/clinc_oos, "plus" variant), a benchmark intent classification dataset widely used in NLP research.

- 151 intent classes covering a wide range of customer service topics
- Topics include banking, travel, orders, cards, loans, app issues, and more
- Includes an out-of-scope (OOS) class for queries the model cannot confidently classify
- Training, validation, and test splits provided

The dataset does not include security-critical intents like fraud or unauthorized access. These were handled separately through the safety net layer, which is a deliberate design decision consistent with how production NLU systems handle high-priority edge cases.

---

## Model Architecture

The model is a multi-task BERT built on top of `bert-base-uncased`. Instead of training two separate models for intent and sentiment, both tasks share the same BERT backbone. This reduces compute, improves generalization through shared representations, and keeps the deployment simple.

```
Input Query
    |
BertModel (bert-base-uncased)
    |
[CLS] token representation
    |
    |--- Dropout
    |       |
    |       |--- Intent Head: Linear(768, 512) -> GELU -> Dropout -> Linear(512, 151)
    |       |
    |       |--- Sentiment Head: Linear(768, 256) -> GELU -> Dropout -> Linear(256, 3)
```

Both heads are trained simultaneously using cross-entropy loss on their respective targets. The model learns to extract features that are useful for both tasks at the same time.

---

## Training Details

| Parameter | Value |
|---|---|
| Base model | bert-base-uncased |
| Epochs | 15 |
| Best checkpoint | Epoch 10 |
| Max sequence length | 64 tokens |
| Dropout | 0.3 |
| Device | GPU |
| Optimizer | AdamW |

---

## Model Performance

| Task | Accuracy | F1 Score |
|-----------------------|--------|--------|
| Intent Classification | 86.20% | 0.8502 |
| Sentiment Analysis | 93.13% | 0.9263 |

These results were evaluated on the CLINC150 test set. The model handles typos and informal phrasing reasonably well due to BERT's subword tokenization.

---

## The Safety Net

One important design decision in this project is the pre-classification safety net. CLINC150 does not include intents like fraud detection, unauthorized account access, or emergency card blocking. Rather than ignoring these, a keyword-based layer was added that runs before BERT.

If the query contains phrases associated with security incidents, the system immediately classifies it as one of four high-priority intents and flags it with a security alert in the UI. This approach is consistent with how production systems like Bank of America's Erica, PayPal's assistant, and Amazon Alexa handle high-priority queries that fall outside the training distribution.

Covered security intents:
- `unauthorized_access` — someone using the account without permission
- `report_fraud` — unauthorized transactions, scams, stolen money
- `emergency_block` — lost or stolen card
- `account_compromised` — locked out, password changed by someone else

---

## The Full Pipeline

```
Customer Query
      |
      v
Safety Net (keyword matching)
      |
      |-- Match found --> Security intent (confidence: 0.95) --> Flag as SECURITY ALERT
      |
      |-- No match --> BERT Model
                           |
                           |-- Intent classification (151 classes)
                           |-- Sentiment analysis (negative / neutral / positive)
                           |
                           v
                     Confidence check
                           |
                           |-- Below threshold (0.20) --> out_of_scope
                           |-- Above threshold --> predicted intent
                           |
                           v
                     Prompt Builder
                           |
                           |-- Full conversation history included
                           |-- Intent and sentiment tone guidance
                           |
                           v
                     Groq LLM (llama-3.1-8b-instant)
                           |
                           v
                     Response displayed in chat
```

---

## Conversation Memory

Unlike simple chatbots that treat every message in isolation, this system maintains the full conversation history across the entire session. Every time a new message is sent, the complete history of what the customer and the assistant said before is included in the prompt sent to the LLM.

This means the chatbot can handle follow-up questions, remember context from earlier in the conversation, and give responses that feel natural and connected rather than disconnected one-off replies.

---

## Project Structure

```
customer_query_analyzer/
|
|-- app.py                      Main entry point, run this with streamlit
|-- requirements.txt            Python dependencies
|-- .gitignore                  Files excluded from GitHub
|-- README.md                   This file
|
|-- config/
|   |-- __init__.py
|   |-- settings.py             All constants: model name, thresholds, HF repo ID
|
|-- model/
|   |-- __init__.py
|   |-- bert_model.py           MultiTaskBERT class definition
|   |-- loader.py               Downloads model from HuggingFace, loads into memory
|   |-- classifier.py           Text cleaning, BERT inference, result formatting
|
|-- pipeline/
|   |-- __init__.py
|   |-- safety_net.py           Security keyword patterns and pre_classify()
|   |-- prompt_builder.py       Builds LLM prompt with full conversation history
|   |-- llm.py                  Sends prompt to Groq API, returns response
|
|-- ui/
    |-- __init__.py
    |-- styles.py               All CSS for the Streamlit app
    |-- sidebar.py              Sidebar: API key input, session stats, controls
    |-- chat.py                 Chat window, input form, feedback, quick examples
    |-- analytics.py            Gauge chart, top predictions, sentiment chart, history
```

---

## Dashboard Features

The Streamlit dashboard has three main sections:

**Chat Interface**
A real-time chat window where the customer types queries and receives responses. Each response is tagged with the detected intent, sentiment, and any alert flags. A feedback button (Yes/No) lets users rate each response. Six quick example buttons are provided to test common scenarios quickly.

**Analysis Panel**
Shown alongside the chat, this updates after every query with:
- Intent, Sentiment, and Status metric tiles
- A confidence gauge showing how certain the model was
- Top 3 predicted intents with confidence bars
- A sentiment breakdown bar chart
- A session sentiment donut chart
- An intent frequency bar chart showing the most queried topics

**Query History Table**
A full log of every query in the session with intent, confidence, sentiment, status, latency, and user feedback. Can be downloaded as a CSV file.

---

## Running Locally

Make sure Python 3.9 or higher is installed.

```bash
pip install -r requirements.txt
streamlit run app.py
```

When the app loads, it will automatically download the BERT model from HuggingFace on the first run. This takes about 1-2 minutes and only happens once — after that it is cached locally.

Paste your Groq API key in the sidebar to enable LLM responses.
Get a free key at: https://console.groq.com

---

## Deploying to Streamlit Cloud

1. Push the project folder to a GitHub repository
2. Go to https://share.streamlit.io
3. Sign in with GitHub and click New App
4. Select the repository and set the main file path to `app.py`
5. Click Deploy
6. Once deployed, go to Settings > Secrets and add:

```
GROQ_API_KEY = "your_groq_api_key_here"
```

7. Save and reboot the app

The BERT model is hosted on HuggingFace at `YamiChowdary/customer-query-analyzer-bert` and is downloaded automatically when the app starts on the cloud server.

---

## Model Files on HuggingFace

The trained model weights are too large for GitHub (441 MB) so they are hosted separately on HuggingFace Hub.

Repository: https://huggingface.co/YamiChowdary/customer-query-analyzer-bert

Files hosted:
- `bert_best.pt` — trained model weights (best checkpoint from epoch 10)
- `bert_config.json` — model configuration
- `tokenizer.json` — tokenizer vocabulary
- `tokenizer_config.json` — tokenizer settings
- `intent_label_map.json` — mapping from integer IDs to intent names

These files are downloaded automatically on first load and cached locally. The app requires an internet connection on the very first run.

---

## Technologies Used

- PyTorch — model training and inference
- HuggingFace Transformers — BERT tokenizer and base model
- HuggingFace Hub — model file hosting
- CLINC150 Dataset — intent classification training data
- Streamlit — web dashboard
- Plotly — interactive charts and gauges
- Groq API — LLM response generation (llama-3.1-8b-instant)
- Pandas — data handling and CSV export

---

## Key Design Decisions

**Why multi-task learning?**
Training intent and sentiment on the same BERT backbone is more efficient than two separate models. The shared representation also tends to generalize better because the model learns features that are useful for understanding language broadly, not just for one narrow task.

**Why a safety net instead of training on security intents?**
Security-critical queries require immediate, reliable detection. A keyword-based layer is deterministic and fast. BERT could potentially miss or misclassify these queries, especially with novel phrasing. The hybrid approach — rules for high-stakes intents, ML for everything else — reflects real-world production NLU design.

**Why Groq?**
Groq's API is free, has a generous rate limit, and is significantly faster than most alternatives. For a demo and student project, it is the most practical choice.

**Why HuggingFace for model hosting?**
GitHub has a 25MB file size limit. The trained model is 441MB. HuggingFace Hub is the standard platform for hosting ML model weights and integrates cleanly with Python through the `huggingface_hub` library.


