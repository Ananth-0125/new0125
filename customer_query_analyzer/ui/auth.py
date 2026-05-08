import os

import requests
import streamlit as st
from streamlit.components.v2 import component as component_v2

from config.firebase_config import FIREBASE_CONFIG


AUTH_DEFAULTS = {
    "is_authenticated": False,
    "auth_user": None,
    "auth_token": "",
    "refresh_token": "",
    "auth_action": "",
}

FIREBASE_ERROR_MESSAGES = {
    "EMAIL_EXISTS": "This email is already registered. Please sign in instead.",
    "EMAIL_NOT_FOUND": "No Firebase user was found for this email.",
    "INVALID_PASSWORD": "The password is incorrect.",
    "INVALID_LOGIN_CREDENTIALS": "Invalid email or password.",
    "USER_DISABLED": "This Firebase user has been disabled.",
    "WEAK_PASSWORD : Password should be at least 6 characters": "Password must be at least 6 characters long.",
    "WEAK_PASSWORD": "Password must be at least 6 characters long.",
    "OPERATION_NOT_ALLOWED": "Enable the requested sign-in method in your Firebase console.",
    "TOO_MANY_ATTEMPTS_TRY_LATER": "Too many attempts. Please try again later.",
    "INVALID_EMAIL": "Enter a valid email address.",
}

AUTH_HTML = """
<div class="fb-auth-card">
    <button id="google-login-btn" class="fb-google-btn" type="button">Continue with Google</button>
    <div class="fb-divider">OR USE EMAIL/PASSWORD</div>

    <div class="fb-tab-row">
        <button class="fb-tab active" data-tab="signin" type="button">Sign In</button>
        <button class="fb-tab" data-tab="signup" type="button">Sign Up</button>
    </div>

    <div id="fb-auth-message" class="fb-message"></div>

    <div class="fb-panel active" data-panel="signin">
        <input id="signin-email" class="fb-input" type="email" placeholder="Email" />
        <input id="signin-password" class="fb-input" type="password" placeholder="Password" />
        <button id="signin-btn" class="fb-primary-btn" type="button">Sign In</button>
    </div>

    <div class="fb-panel" data-panel="signup">
        <input id="signup-email" class="fb-input" type="email" placeholder="Email" />
        <input id="signup-password" class="fb-input" type="password" placeholder="Password" />
        <button id="signup-btn" class="fb-primary-btn" type="button">Create Account</button>
    </div>

    <div class="fb-note">
        Enable Google and Email/Password in Firebase Authentication. Also add your Streamlit app domain to Firebase authorized domains.
    </div>
</div>
"""

AUTH_CSS = """
.fb-auth-card {
    width: 100%;
    max-width: 720px;
    margin: 0 auto;
    padding: 18px;
    border: 1px solid #d8e3ec;
    border-radius: 16px;
    background: linear-gradient(180deg, #f8fbff 0%, #ffffff 100%);
    box-shadow: 0 10px 32px rgba(0, 88, 163, 0.08);
    font-family: "Segoe UI", sans-serif;
}

.fb-google-btn,
.fb-primary-btn,
.fb-tab {
    border: none;
    border-radius: 10px;
    cursor: pointer;
    transition: transform 0.15s ease, box-shadow 0.15s ease, background 0.15s ease;
}

.fb-google-btn {
    width: 100%;
    padding: 12px 14px;
    background: #ffffff;
    color: #0f172a;
    border: 1px solid #d8e3ec;
    font-weight: 700;
    font-size: 0.98rem;
    box-shadow: 0 6px 16px rgba(15, 23, 42, 0.06);
}

.fb-google-btn:hover,
.fb-primary-btn:hover,
.fb-tab:hover {
    transform: translateY(-1px);
}

.fb-divider {
    text-align: center;
    color: #99a0aa;
    font-size: 0.72rem;
    margin: 14px 0 12px 0;
    letter-spacing: 1.3px;
}

.fb-tab-row {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 8px;
    margin-bottom: 12px;
}

.fb-tab {
    padding: 10px 12px;
    background: #edf4fa;
    color: #4b5563;
    font-weight: 700;
    font-size: 0.86rem;
}

.fb-tab.active {
    background: #0058a3;
    color: #ffffff;
    box-shadow: 0 8px 20px rgba(0, 88, 163, 0.18);
}

.fb-panel {
    display: none;
}

.fb-panel.active {
    display: block;
}

.fb-input {
    width: 100%;
    box-sizing: border-box;
    padding: 12px 13px;
    border: 1px solid #c9d7e4;
    border-radius: 10px;
    margin-bottom: 10px;
    font-size: 0.95rem;
    background: #ffffff;
    color: #0f172a;
    caret-color: #0f172a;
    -webkit-text-fill-color: #0f172a;
}

.fb-input::placeholder {
    color: #94a3b8;
    opacity: 1;
}

.fb-input:focus {
    outline: none;
    border-color: #0058a3;
    box-shadow: 0 0 0 3px rgba(0, 88, 163, 0.12);
}

.fb-primary-btn {
    width: 100%;
    padding: 12px 14px;
    background: #0058a3;
    color: #ffffff;
    font-weight: 700;
    font-size: 0.95rem;
}

.fb-primary-btn:disabled,
.fb-google-btn:disabled {
    opacity: 0.7;
    cursor: wait;
}

.fb-message {
    min-height: 20px;
    margin: 0 0 10px 0;
    font-size: 0.85rem;
    color: #475569;
}

.fb-message.error {
    color: #cc2200;
}

.fb-message.success {
    color: #1a7a2a;
}

.fb-note {
    margin-top: 12px;
    color: #7b8794;
    font-size: 0.76rem;
    line-height: 1.45;
}
"""

AUTH_JS = """
const firebaseSdkPromise = Promise.all([
  import("https://www.gstatic.com/firebasejs/10.12.5/firebase-app.js"),
  import("https://www.gstatic.com/firebasejs/10.12.5/firebase-auth.js"),
]);

let authObserverCleanup = null;

function renderAuthUI(root) {
  if (root.dataset.rendered === "true") {
    return;
  }
  root.dataset.rendered = "true";
}

function setBusy(root, busy) {
  root.querySelectorAll("button").forEach((button) => {
    button.disabled = busy;
  });
}

function setMessage(root, text, tone = "") {
  const msg = root.querySelector("#fb-auth-message");
  msg.textContent = text || "";
  msg.className = "fb-message";
  if (tone) {
    msg.classList.add(tone);
  }
}

function activateTab(root, tabName) {
  root.querySelectorAll(".fb-tab").forEach((button) => {
    button.classList.toggle("active", button.dataset.tab === tabName);
  });
  root.querySelectorAll(".fb-panel").forEach((panel) => {
    panel.classList.toggle("active", panel.dataset.panel === tabName);
  });
}

function normalizeError(error) {
  if (!error) {
    return "Authentication failed.";
  }
  return error.message || String(error);
}

export default function(component) {
  const { data, parentElement, setStateValue } = component;
  const root = parentElement.querySelector(".fb-auth-card");
  renderAuthUI(root);

  firebaseSdkPromise.then(async ([appMod, authMod]) => {
    const { initializeApp, getApps } = appMod;
    const {
      getAuth,
      GoogleAuthProvider,
      browserSessionPersistence,
      createUserWithEmailAndPassword,
      onAuthStateChanged,
      setPersistence,
      signInWithEmailAndPassword,
      signInWithPopup,
      signOut,
    } = authMod;

    const config = data.firebaseConfig || {};
    const existing = getApps().find((app) => app.name === "streamlit-firebase-auth");
    const app = existing || initializeApp(config, "streamlit-firebase-auth");
    const auth = getAuth(app);

    await setPersistence(auth, browserSessionPersistence).catch(() => {});

    const googleBtn = root.querySelector("#google-login-btn");
    const signinBtn = root.querySelector("#signin-btn");
    const signupBtn = root.querySelector("#signup-btn");

    root.querySelectorAll(".fb-tab").forEach((button) => {
      button.onclick = () => {
        activateTab(root, button.dataset.tab);
        setMessage(root, "");
      };
    });

    googleBtn.onclick = async () => {
      setBusy(root, true);
      setMessage(root, "Opening Google sign-in...", "");
      try {
        const provider = new GoogleAuthProvider();
        provider.setCustomParameters({ prompt: "select_account" });
        await signInWithPopup(auth, provider);
        setMessage(root, "Signed in with Google.", "success");
      } catch (error) {
        setMessage(root, normalizeError(error), "error");
      } finally {
        setBusy(root, false);
      }
    };

    signinBtn.onclick = async () => {
      const email = root.querySelector("#signin-email").value.trim();
      const password = root.querySelector("#signin-password").value;
      if (!email || !password) {
        setMessage(root, "Enter both email and password.", "error");
        return;
      }

      setBusy(root, true);
      setMessage(root, "Signing in...", "");
      try {
        await signInWithEmailAndPassword(auth, email, password);
        setMessage(root, "Signed in successfully.", "success");
      } catch (error) {
        setMessage(root, normalizeError(error), "error");
      } finally {
        setBusy(root, false);
      }
    };

    signupBtn.onclick = async () => {
      const email = root.querySelector("#signup-email").value.trim();
      const password = root.querySelector("#signup-password").value;
      if (!email || !password) {
        setMessage(root, "Enter email and password to create an account.", "error");
        return;
      }

      setBusy(root, true);
      setMessage(root, "Creating account...", "");
      try {
        await createUserWithEmailAndPassword(auth, email, password);
        setMessage(root, "Account created successfully.", "success");
      } catch (error) {
        setMessage(root, normalizeError(error), "error");
      } finally {
        setBusy(root, false);
      }
    };

    if (authObserverCleanup) {
      authObserverCleanup();
      authObserverCleanup = null;
    }

    authObserverCleanup = onAuthStateChanged(auth, async (user) => {
      if (user) {
        const token = await user.getIdToken();
        const provider = (user.providerData && user.providerData[0] && user.providerData[0].providerId) || "";
        setStateValue("auth_state", {
          status: "authenticated",
          idToken: token,
          email: user.email || "",
          displayName: user.displayName || "",
          provider: provider,
          nonce: Date.now(),
        });
      } else {
        setStateValue("auth_state", {
          status: "signed_out",
          nonce: Date.now(),
        });
      }
    });

    if (data.action === "logout") {
      setBusy(root, true);
      await signOut(auth).catch(() => {});
      setBusy(root, false);
      setMessage(root, "Signed out.", "success");
    }
  }).catch((error) => {
    setMessage(root, "Failed to load Firebase authentication UI: " + normalizeError(error), "error");
  });

  return () => {
    if (authObserverCleanup) {
      authObserverCleanup();
      authObserverCleanup = null;
    }
  };
}
"""

FIREBASE_AUTH_WIDGET = component_v2(
    "firebase_auth_widget",
    html=AUTH_HTML,
    css=AUTH_CSS,
    js=AUTH_JS,
    isolate_styles=False,
)


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


def _lookup_user_by_token(id_token: str) -> dict:
    data = _firebase_post("lookup", {"idToken": id_token})
    users = data.get("users", [])
    if not users:
        raise ValueError("Firebase did not return user details for this session.")
    return users[0]


def _set_authenticated_user(user_data: dict, id_token: str) -> None:
    provider_info = user_data.get("providerUserInfo", [])
    provider = provider_info[0].get("providerId", "") if provider_info else ""

    st.session_state.is_authenticated = True
    st.session_state.auth_token = id_token
    st.session_state.refresh_token = ""
    st.session_state.auth_user = {
        "email": user_data.get("email", ""),
        "uid": user_data.get("localId", ""),
        "display_name": user_data.get("displayName", ""),
        "photo_url": user_data.get("photoUrl", ""),
        "provider": provider,
    }


def logout_user() -> None:
    st.session_state.is_authenticated = False
    st.session_state.auth_token = ""
    st.session_state.refresh_token = ""
    st.session_state.auth_user = None
    st.session_state.auth_action = "logout"


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
    st.markdown(
        """
        <div class="page-header" style="max-width:780px;margin:28px auto 24px auto;">
            <div class="header-tags">
                <span class="htag">FIREBASE AUTH</span>
                <span class="htag">GOOGLE + EMAIL</span>
                <span class="htag">SECURED ACCESS</span>
            </div>
            <h1>Customer Query Analyzer</h1>
            <p>Sign in with Firebase before using the analyzer.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    _, center, _ = st.columns([1, 1.25, 1])
    with center:
        result = FIREBASE_AUTH_WIDGET(
            data={
                "firebaseConfig": _get_firebase_config(),
                "action": st.session_state.auth_action,
            },
            key="firebase_auth_widget_mount",
            on_auth_state_change=lambda: None,
        )

        auth_state = getattr(result, "auth_state", None)
        if auth_state:
            status = auth_state.get("status", "")
            if status == "authenticated":
                token = auth_state.get("idToken", "")
                if token and token != st.session_state.auth_token:
                    try:
                        user_data = _lookup_user_by_token(token)
                        _set_authenticated_user(user_data, token)
                        st.session_state.auth_action = ""
                        st.rerun()
                    except Exception as exc:
                        st.error(str(exc))
            elif status == "signed_out" and st.session_state.auth_action == "logout":
                st.session_state.auth_action = ""

        st.caption(
            "Enable Google and Email/Password in Firebase Authentication. Add your Streamlit app domain to Firebase authorized domains."
        )
