# Customer Query Analyzer

This repository is ready to upload to GitHub and deploy on Streamlit Community Cloud.

## Deploy Entry Point

- Main file: `app.py`
- Python dependencies: `requirements.txt`

The root `app.py` is a lightweight launcher that starts the real Streamlit app from `customer_query_analyzer/app.py`, so deployment from the repo root is straightforward.

## Streamlit Secrets

Create `.streamlit/secrets.toml` in Streamlit Cloud with at least:

```toml
GROQ_API_KEY = "your_groq_api_key_here"
```

Optional Firebase overrides if you do not want to rely on the values in code:

```toml
FIREBASE_API_KEY = "your_firebase_api_key"
FIREBASE_AUTH_DOMAIN = "your-project.firebaseapp.com"
FIREBASE_PROJECT_ID = "your-project-id"
FIREBASE_STORAGE_BUCKET = "your-project.firebasestorage.app"
FIREBASE_MESSAGING_SENDER_ID = "your_sender_id"
FIREBASE_APP_ID = "your_app_id"
FIREBASE_MEASUREMENT_ID = "your_measurement_id"
```

## Streamlit Cloud Settings

Use these values when creating the app:

- Repository: your GitHub repo
- Branch: `main`
- Main file path: `app.py`

## Notes

- Enable Firebase Email/Password authentication in your Firebase console.
- Enable Firebase Google authentication in your Firebase console if you want the Google button to work.
- Add your Streamlit app domain to Firebase Authentication authorized domains.
- The first app boot downloads the BERT model from Hugging Face, so the first startup will take longer than later restarts.
- Training scripts are kept in `train/` but are not used by the deployed Streamlit app.
