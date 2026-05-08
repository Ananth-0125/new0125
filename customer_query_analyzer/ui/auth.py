import os
from urllib.parse import urlencode

import requests
import streamlit as st
from google_auth_oauthlib.flow import Flow

from config.firebase_config import FIREBASE_CONFIG


AUTH_DEFAULTS = {
    "is_authenticated": False,
    "auth_user": None,
    "auth_token": "",
    "refresh_token": "",
    "google_oauth_state": "",
}

FIREBASE_ERROR_MESSAGES = {
    "EMAIL_EXISTS": "This email is already registered. Please sign in instead.",
    "EMAIL_NOT_FOUND": "No Firebase user was found for this email.",
    "INVALID_PASSWORD": "The password is incorrect.",
    "INVALID_LOGIN_CREDENTIALS": "Invalid email or password.",
    "USER_DISABLED": "This Firebase user has been disabled.",
    "WEAK_PASSWORD : Password should be at least 6 characters": "Password must be at least 6 characters long.",
    "WEAK_PASSWORD": "Password must be at least 6 characters long.",
    "OPERATION_NOT_ALLOWED": "Enable Email/Password sign-in in your Firebase console.",
    "TOO_MANY_ATTEMPTS_TRY_LATER": "Too many attempts. Please try again later.",
    "INVALID_EMAIL": "Enter a valid email address.",
}


def init_auth_state() -> None:
    for key, value in AUTH_DEFAULTS.items():
        if key not in st.session_state:
            st.session_state[key] = value


def _get_secret_value(key: str, default: str = "") -> str:
    value = os.environ.get(key)
    if value:
        return value

    try:
        if key in st.secrets:
            return str(st.secrets[key])
    except Exception:
        pass

    return default


def _get_firebase_config() -> dict:
    config = FIREBASE_CONFIG.copy()
    keys = {
        "apiKey": "FIREBASE_API_KEY",
        "authDomain": "FIREBASE_AUTH_DOMAIN",
        "projectId": "FIREBASE_PROJECT_ID",
        "storageBucket": "FIREBASE_STORAGE_BUCKET",
        "messagingSenderId": "FIREBASE_MESSAGING_SENDER_ID",
        "appId": "FIREBASE_APP_ID",
        "measurementId": "FIREBASE_MEASUREMENT_ID",
    }

    for field, env_key in keys.items():
        value = _get_secret_value(env_key)
        if value:
            config[field] = value

    return config


def _get_google_oauth_config() -> dict | None:
    client_id = _get_secret_value("GOOGLE_CLIENT_ID")
    client_secret = _get_secret_value("GOOGLE_CLIENT_SECRET")
    redirect_uri = _get_secret_value("GOOGLE_REDIRECT_URI")

    if not client_id or not client_secret or not redirect_uri:
        return None

    return {
        "client_id": client_id,
        "client_secret": client_secret,
        "redirect_uri": redirect_uri,
    }


def _build_google_flow(config: dict, state: str | None = None) -> Flow:
    flow = Flow.from_client_config(
        {
            "web": {
                "client_id": config["client_id"],
                "client_secret": config["client_secret"],
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "redirect_uris": [config["redirect_uri"]],
            }
        },
        scopes=["openid", "email", "profile"],
        state=state,
    )
    flow.redirect_uri = config["redirect_uri"]
    return flow


def _build_google_auth_url(config: dict) -> str:
    flow = _build_google_flow(config)
    authorization_url, state = flow.authorization_url(
        access_type="offline",
        include_granted_scopes="true",
        prompt="select_account",
    )
    st.session_state.google_oauth_state = state
    return authorization_url


def _firebase_error_message(error_payload: dict) -> str:
    code = (
        error_payload.get("error", {})
        .get("message", "Firebase authentication failed.")
    )
    return FIREBASE_ERROR_MESSAGES.get(code, code.replace("_", " ").title())


def _firebase_post(action: str, payload: dict) -> dict:
    api_key = _get_firebase_config()["apiKey"]
    url = f"https://identitytoolkit.googleapis.com/v1/accounts:{action}?key={api_key}"

    response = requests.post(url, json=payload, timeout=15)
    data = response.json()

    if not response.ok:
        raise ValueError(_firebase_error_message(data))

    return data


def _set_authenticated_user(auth_data: dict) -> None:
    st.session_state.is_authenticated = True
    st.session_state.auth_token = auth_data.get("idToken", "")
    st.session_state.refresh_token = auth_data.get("refreshToken", "")
    st.session_state.auth_user = {
        "email": auth_data.get("email", ""),
        "uid": auth_data.get("localId", ""),
        "display_name": auth_data.get("displayName", ""),
        "photo_url": auth_data.get("photoUrl", ""),
        "provider": auth_data.get("providerId", ""),
    }


def logout_user() -> None:
    st.session_state.is_authenticated = False
    st.session_state.auth_token = ""
    st.session_state.refresh_token = ""
    st.session_state.auth_user = None
    st.session_state.google_oauth_state = ""


def _finalize_google_sign_in(config: dict, google_id_token: str) -> dict:
    post_body = urlencode(
        {
            "id_token": google_id_token,
            "providerId": "google.com",
        }
    )
    return _firebase_post(
        "signInWithIdp",
        {
            "postBody": post_body,
            "requestUri": config["redirect_uri"],
            "returnIdpCredential": True,
            "returnSecureToken": True,
        },
    )


def handle_google_callback() -> None:
    query_params = st.query_params
    code = query_params.get("code")
    state = query_params.get("state")
    error = query_params.get("error")

    if error:
        st.error(f"Google sign-in failed: {error}")
        st.query_params.clear()
        return

    if not code:
        return

    config = _get_google_oauth_config()
    if not config:
        st.error(
            "Google sign-in is not configured. Add GOOGLE_CLIENT_ID, "
            "GOOGLE_CLIENT_SECRET, and GOOGLE_REDIRECT_URI to Streamlit secrets."
        )
        st.query_params.clear()
        return

    expected_state = st.session_state.google_oauth_state
    if expected_state and state and state != expected_state:
        st.error("Google sign-in state mismatch. Please try again.")
        st.query_params.clear()
        st.session_state.google_oauth_state = ""
        return

    try:
        flow = _build_google_flow(config, state=state)
        flow.fetch_token(code=code)
        credentials = flow.credentials

        if not credentials.id_token:
            raise ValueError("Google did not return an ID token.")

        auth_data = _finalize_google_sign_in(config, credentials.id_token)
        _set_authenticated_user(auth_data)
        st.session_state.google_oauth_state = ""
        st.query_params.clear()
        st.rerun()
    except Exception as exc:
        st.error(f"Google sign-in failed: {exc}")
        st.query_params.clear()
        st.session_state.google_oauth_state = ""


def render_auth_status() -> None:
    user = st.session_state.auth_user or {}
    display_name = user.get("display_name", "")
    email = user.get("email", "Signed-in user")
    provider = user.get("provider", "password")
    provider_label = "GOOGLE" if provider == "google.com" else "EMAIL"

    st.markdown(
        "<div class='sb-sec'>AUTHENTICATION</div>",
        unsafe_allow_html=True,
    )
    st.markdown(
        f"<div style='font-size:0.72rem;color:#1A7A2A;margin:4px 0 10px 0;font-family:Roboto Mono,monospace;'>"
        f"SIGNED IN VIA {provider_label}</div>",
        unsafe_allow_html=True,
    )
    st.markdown(
        f"<div style='font-size:0.7rem;color:#666677;margin:-2px 0 10px 0;font-family:Roboto Mono,monospace;'>"
        f"{(display_name or email).upper()}</div>",
        unsafe_allow_html=True,
    )

    if st.button("Log Out", use_container_width=True):
        logout_user()
        st.rerun()


def render_auth_page() -> None:
    handle_google_callback()

    st.markdown(
        """
        <div class="page-header" style="max-width:780px;margin:28px auto 24px auto;">
            <div class="header-tags">
                <span class="htag">FIREBASE AUTH</span>
                <span class="htag">EMAIL LOGIN</span>
                <span class="htag">SECURED ACCESS</span>
            </div>
            <h1>Customer Query Analyzer</h1>
            <p>Sign in with your Firebase account before using the analyzer.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    left, center, right = st.columns([1, 1.2, 1])
    with center:
        google_config = _get_google_oauth_config()
        st.markdown(
            "<div style='font-size:0.72rem;color:#666677;margin:0 0 8px 0;font-family:Roboto Mono,monospace;'>"
            "SIGN IN OPTIONS</div>",
            unsafe_allow_html=True,
        )
        if google_config:
            st.link_button(
                "Continue with Google",
                _build_google_auth_url(google_config),
                use_container_width=True,
            )
        else:
            st.info(
                "To enable Google sign-in, add GOOGLE_CLIENT_ID, "
                "GOOGLE_CLIENT_SECRET, and GOOGLE_REDIRECT_URI to Streamlit secrets."
            )

        st.markdown(
            "<div style='text-align:center;color:#99A0AA;font-size:0.72rem;margin:10px 0 6px 0;font-family:Roboto Mono,monospace;'>"
            "OR USE EMAIL/PASSWORD</div>",
            unsafe_allow_html=True,
        )

        login_tab, register_tab, reset_tab = st.tabs(
            ["Sign In", "Register", "Reset Password"]
        )

        with login_tab:
            with st.form("firebase_login_form"):
                email = st.text_input("Email", placeholder="you@example.com")
                password = st.text_input("Password", type="password")
                submitted = st.form_submit_button("Sign In", use_container_width=True)

            if submitted:
                if not email or not password:
                    st.error("Enter both email and password.")
                else:
                    try:
                        auth_data = _firebase_post(
                            "signInWithPassword",
                            {
                                "email": email.strip(),
                                "password": password,
                                "returnSecureToken": True,
                            },
                        )
                        _set_authenticated_user(auth_data)
                        st.rerun()
                    except Exception as exc:
                        st.error(str(exc))

        with register_tab:
            with st.form("firebase_register_form"):
                email = st.text_input("New Email", placeholder="you@example.com")
                password = st.text_input("New Password", type="password")
                confirm_password = st.text_input("Confirm Password", type="password")
                submitted = st.form_submit_button("Create Account", use_container_width=True)

            if submitted:
                if not email or not password or not confirm_password:
                    st.error("Fill in all registration fields.")
                elif password != confirm_password:
                    st.error("Passwords do not match.")
                else:
                    try:
                        auth_data = _firebase_post(
                            "signUp",
                            {
                                "email": email.strip(),
                                "password": password,
                                "returnSecureToken": True,
                            },
                        )
                        _set_authenticated_user(auth_data)
                        st.success("Firebase account created successfully.")
                        st.rerun()
                    except Exception as exc:
                        st.error(str(exc))

        with reset_tab:
            with st.form("firebase_reset_form"):
                email = st.text_input("Registered Email", placeholder="you@example.com")
                submitted = st.form_submit_button("Send Reset Link", use_container_width=True)

            if submitted:
                if not email:
                    st.error("Enter your registered email address.")
                else:
                    try:
                        _firebase_post(
                            "sendOobCode",
                            {
                                "requestType": "PASSWORD_RESET",
                                "email": email.strip(),
                            },
                        )
                        st.success("Password reset email sent.")
                    except Exception as exc:
                        st.error(str(exc))

        st.caption(
            "Enable Email/Password and Google in Firebase Authentication before deploying these sign-in methods."
        )
