import streamlit as st
import hashlib
import io

from rag_engine import (
    answer_question,
    get_or_create_user,
    create_chat_session,
    get_user_sessions,
    restore_chat,
    rename_chat,
    delete_chat,
)

# Optional speech recognition
try:
    import speech_recognition as sr
    SPEECH_RECOGNITION_AVAILABLE = True
except ImportError:
    SPEECH_RECOGNITION_AVAILABLE = False


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="Quantum AI Tutor",
    page_icon="⚛️",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# SESSION STATE
# ============================================================

if "messages" not in st.session_state:
    st.session_state.messages = []

if "user_id" not in st.session_state:
    st.session_state.user_id = None

if "session_id" not in st.session_state:
    st.session_state.session_id = None

if "uploaded_files" not in st.session_state:
    st.session_state.uploaded_files = []

if "processed_audio_hash" not in st.session_state:
    st.session_state.processed_audio_hash = None


# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown(
    """
<style>

html, body, [class*="css"] {
    font-family: Arial, sans-serif;
}

/* Main background */
.stApp {
    background:
        radial-gradient(circle at 20% 20%, rgba(255,255,255,0.8) 1px, transparent 1.5px),
        radial-gradient(circle at 80% 30%, rgba(255,255,255,0.7) 1px, transparent 1.5px),
        radial-gradient(circle at 40% 70%, rgba(255,255,255,0.8) 1px, transparent 1.5px),
        radial-gradient(circle at 70% 80%, rgba(255,255,255,0.6) 1px, transparent 1.5px),
        radial-gradient(circle at 10% 90%, rgba(255,255,255,0.7) 1px, transparent 1.5px),
        linear-gradient(135deg, #050816 0%, #0b1026 45%, #111936 100%);
    background-size:
        160px 160px,
        220px 220px,
        180px 180px,
        260px 260px,
        200px 200px,
        cover;
    background-attachment: fixed;
}

/* Make Streamlit main area transparent */
[data-testid="stAppViewContainer"] {
    background: transparent;
}

[data-testid="stHeader"] {
    background: transparent;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background: rgba(7, 12, 30, 0.95);
    border-right: 1px solid rgba(255,255,255,0.08);
}

[data-testid="stSidebar"] * {
    color: white;
}

/* Main title */
.quantum-title {
    text-align: center;
    font-size: 42px;
    font-weight: 800;
    color: white;
    margin-top: 10px;
    margin-bottom: 4px;
}

.quantum-subtitle {
    text-align: center;
    color: rgba(255,255,255,0.65);
    font-size: 15px;
    margin-bottom: 25px;
}

/* Chat area */
.chat-container {
    max-width: 900px;
    margin: auto;
}

/* Chat messages */
[data-testid="stChatMessage"] {
    background: rgba(255,255,255,0.05);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 16px;
    padding: 10px 14px;
    margin-bottom: 12px;
}

[data-testid="stChatMessage"] p {
    color: white;
}

</style>
""",
    unsafe_allow_html=True,
)


# ============================================================
# HEADER
# ============================================================

st.markdown(
    """
<div class="quantum-title">
    ⚛️ Quantum AI Tutor
</div>

<div class="quantum-subtitle">
    Your intelligent assistant for Quantum Computing
</div>
""",
    unsafe_allow_html=True,
)


# ============================================================
# CHAT HISTORY / SIDEBAR
# ============================================================

with st.sidebar:

    st.markdown("## 💬 Chat History")

    if st.session_state.user_id:

        try:
            sessions = get_user_sessions(
                st.session_state.user_id
            )

            if sessions:
                for session in sessions:

                    session_name = (
                        session.get("title")
                        or session.get("name")
                        or "New Chat"
                    )

                    session_id = session.get("id")

                    if st.button(
                        session_name,
                        key=f"session_{session_id}",
                        use_container_width=True,
                    ):
                        restored = restore_chat(session_id)

                        if restored:
                            st.session_state.session_id = session_id

                            if isinstance(restored, list):
                                st.session_state.messages = restored

                            st.rerun()

        except Exception:
            pass

    st.divider()

    if st.button(
        "➕ New Chat",
        use_container_width=True
    ):

        try:
            new_session = create_chat_session(
                st.session_state.user_id
            )

            if new_session:
                if isinstance(new_session, dict):
                    st.session_state.session_id = (
                        new_session.get("id")
                        or new_session.get("session_id")
                    )
                else:
                    st.session_state.session_id = new_session

        except Exception:
            pass

        st.session_state.messages = []
        st.rerun()


# ============================================================
# CREATE USER / SESSION
# ============================================================

if st.session_state.user_id is None:

    try:
        user = get_or_create_user()

        if isinstance(user, dict):
            st.session_state.user_id = (
                user.get("id")
                or user.get("user_id")
            )
        else:
            st.session_state.user_id = user

    except Exception:
        pass


if (
    st.session_state.session_id is None
    and st.session_state.user_id is not None
):

    try:
        new_session = create_chat_session(
            st.session_state.user_id
        )

        if isinstance(new_session, dict):
            st.session_state.session_id = (
                new_session.get("id")
                or new_session.get("session_id")
            )
        else:
            st.session_state.session_id = new_session

    except Exception:
        pass


# ============================================================
# DISPLAY CHAT MESSAGES
# ============================================================

for message in st.session_state.messages:

    role = message.get("role")
    content = message.get("content", "")

    if role == "user":

        with st.chat_message("user"):
            st.markdown(content)

    elif role == "assistant":

        with st.chat_message("assistant"):
            st.markdown(content)


# ============================================================
# QUANTUM CHAT INPUT BAR
# ============================================================

st.markdown(
    """
<style>

/* Chat input */
[data-testid="stChatInput"] {
    border-radius: 18px !important;
}

[data-testid="stChatInput"] textarea {
    background: rgba(255,255,255,0.08) !important;
    color: white !important;
    border: 1px solid rgba(255,255,255,0.15) !important;
    border-radius: 16px !important;
}

[data-testid="stChatInput"] textarea::placeholder {
    color: rgba(255,255,255,0.5) !important;
}

/* Attachment button */
.attachment-label {
    color: white;
    font-size: 22px;
    text-align: center;
}

/* Microphone */
.mic-label {
    color: white;
    font-size: 22px;
    text-align: center;
}

</style>
""",
    unsafe_allow_html=True,
)


# ============================================================
# INPUT LAYOUT
# ============================================================

left, center, right = st.columns(
    [0.11, 0.78, 0.11],
    vertical_alignment="bottom"
)


# ============================================================
# ATTACHMENT BUTTON
# ============================================================

with left:

    with st.popover("📎"):

        st.markdown(
            "### 📎 Attach File"
        )

        attachments = st.file_uploader(
            "Choose a file",
            type=[
                "png",
                "jpg",
                "jpeg",
                "webp",
                "pdf",
                "txt",
                "docx",
                "csv",
            ],
            accept_multiple_files=True,
            label_visibility="collapsed",
        )

        if attachments:

            st.session_state.uploaded_files = attachments

            for file in attachments:
                st.caption(
                    f"📄 {file.name}"
                )


# ============================================================
# MAIN PROMPT BAR
# ============================================================

with center:

    prompt = st.chat_input(
        "Ask anything about quantum computing...",
        key="quantum_chat_input",
    )


# ============================================================
# MICROPHONE
# ============================================================

with right:

    audio_value = st.audio_input(
        "Microphone",
        key="quantum_microphone",
        label_visibility="collapsed",
    )


# ============================================================
# MICROPHONE → TEXT
# ============================================================

if audio_value is not None:

    try:

        audio_bytes = audio_value.getvalue()

        current_audio_hash = hashlib.md5(
            audio_bytes
        ).hexdigest()

        if (
            current_audio_hash
            != st.session_state.processed_audio_hash
        ):

            st.session_state.processed_audio_hash = (
                current_audio_hash
            )

            if SPEECH_RECOGNITION_AVAILABLE:

                recognizer = sr.Recognizer()

                audio_file = io.BytesIO(
                    audio_bytes
                )

                with sr.AudioFile(
                    audio_file
                ) as source:

                    audio_data = recognizer.record(
                        source
                    )

                try:

                    spoken_text = recognizer.recognize_google(
                        audio_data
                    )

                    if spoken_text:

                        st.session_state.messages.append(
                            {
                                "role": "user",
                                "content": spoken_text
                            }
                        )

                        st.rerun()

                except sr.UnknownValueError:

                    st.warning(
                        "Sorry, I couldn't understand the recording."
                    )

                except sr.RequestError:

                    st.error(
                        "Speech recognition service is unavailable."
                    )

            else:

                st.warning(
                    "Speech recognition is not installed."
                )

    except Exception as e:

        st.error(
            f"Microphone error: {e}"
        )


# ============================================================
# FINAL QUERY
# ============================================================

final_query = prompt
