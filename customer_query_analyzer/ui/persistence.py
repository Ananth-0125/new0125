from streamlit.components.v2 import component as component_v2


PERSISTENCE_JS = """
export default function(component) {
  const { data, setStateValue } = component;
  const uid = data && data.uid ? data.uid : "";
  const state = data ? data.state : undefined;

  if (!uid) {
    return;
  }

  const storageKey = `cqa_user_state:${uid}`;

  if (state === null || state === undefined) {
    let stored = null;
    try {
      const raw = window.localStorage.getItem(storageKey);
      if (raw) {
        stored = JSON.parse(raw);
      }
    } catch (error) {
      stored = null;
    }

    setStateValue("payload", {
      uid: uid,
      stored: stored,
      nonce: Date.now(),
    });
    return;
  }

  try {
    window.localStorage.setItem(storageKey, JSON.stringify(state));
  } catch (error) {
    // Ignore localStorage write errors and continue gracefully.
  }
}
"""

LOCAL_USER_STATE = component_v2(
    "local_user_state",
    js=PERSISTENCE_JS,
)


def sync_local_user_state(uid: str, state: dict | None, *, key: str):
    result = LOCAL_USER_STATE(
        data={"uid": uid, "state": state},
        key=key,
        on_payload_change=lambda: None,
    )
    return getattr(result, "payload", None)
