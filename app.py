import io
import os
import streamlit as st
from groq import Groq

# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="Quantum Lab",
    page_icon="⚛️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================
# SESSION STATE INITIALIZATION
# ============================================================

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "user_email" not in st.session_state:
    st.session_state.user_email = ""

if "chats" not in st.session_state:
    st.session_state.chats = {
        "Quantum Session 1": []
    }

if "current_chat" not in st.session_state:
    st.session_state.current_chat = "Quantum Session 1"

if "chat_counter" not in st.session_state:
    st.session_state.chat_counter = 1

if "staged_attachments" not in st.session_state:
    st.session_state.staged_attachments = []

if "staged_voice_text" not in st.session_state:
    st.session_state.staged_voice_text = ""

# ============================================================
# GALAXY THEME & FIXED BOTTOM BAR CSS
# ============================================================

st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;500;600;700;800;900&family=Inter:wght@400;500;600;700;800&display=swap');

html, body {
    font-family: 'Inter', sans-serif;
}

/* Background Galaxy Theme */
.stApp {
    background:
        radial-gradient(circle at 15% 20%, rgba(108, 63, 255, 0.18), transparent 25%),
        radial-gradient(circle at 85% 15%, rgba(0, 157, 255, 0.16), transparent 28%),
        radial-gradient(circle at 50% 80%, rgba(168, 52, 255, 0.13), transparent 32%),
        linear-gradient(135deg, #02030d, #070b20, #030716);
    color: #ffffff;
}

/* Add bottom padding so chat history isn't obscured by the bottom input bar */
.main .block-container {
    padding-bottom: 160px !important;
}

/* Sidebar Styling */
[data-testid="stSidebar"] {
    background:
        radial-gradient(circle at 30% 5%, rgba(105, 65, 255, 0.18), transparent 30%),
        linear-gradient(180deg, #03040e, #070a1c, #02030b) !important;
    border-right: 1px solid rgba(120, 105, 255, 0.25);
}

.user-profile-card {
    background: linear-gradient(135deg, rgba(28, 32, 68, 0.75), rgba(12, 16, 42, 0.85));
    border: 1px solid rgba(130, 115, 255, 0.35);
    border-radius: 16px;
    padding: 12px 14px;
    margin-bottom: 18px;
    display: flex;
    align-items: center;
    gap: 12px;
}

.profile-avatar {
    width: 42px;
    height: 42px;
    border-radius: 12px;
    background: linear-gradient(135deg, #7c4dff, #1e88e5);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 20px;
    border: 1px solid rgba(255, 255, 255, 0.25);
}

.profile-info {
    overflow: hidden;
}

.profile-name {
    font-family: 'Orbitron', sans-serif;
    font-size: 13px;
    font-weight: 700;
    color: #ffffff;
}

.profile-status {
    font-size: 11px;
    color: #4cf0a0;
}

/* Sidebar Buttons */
[data-testid="stSidebar"] .stButton > button {
    width: 100%;
    min-height: 40px;
    border-radius: 12px;
    background: linear-gradient(135deg, rgba(18,21,48,0.90), rgba(8,11,30,0.95));
    border: 1px solid rgba(105,105,180,0.28);
    color: #bfc6e5;
    font-size: 12px;
    font-weight: 600;
    transition: all 0.25s ease;
}

[data-testid="stSidebar"] .stButton > button:hover {
    transform: translateX(4px);
    background: linear-gradient(100deg, rgba(77,55,180,0.85), rgba(27,82,160,0.85));
    border-color: rgba(130,115,255,0.8);
    color: #ffffff;
}

/* FIX: Target Column Container to Pin Prompt Input Bar strictly at Bottom */
div[data-testid="stHorizontalBlock"]:has(div[key="custom_input_photos"]) {
    position: fixed !important;
    bottom: 24px !important;
    left: calc(50% + 120px) !important;
    transform: translateX(-50%) !important;
    width: min(850px, 75vw) !important;
    z-index: 999999 !important;
    background: rgba(18, 22, 45, 0.95) !important;
    border: 1px solid rgba(120, 105, 255, 0.45) !important;
    border-radius: 40px !important;
    padding: 6px 14px !important;
    box-shadow: 0 12px 40px rgba(0, 0, 0, 0.65), 0 0 20px rgba(108, 63, 255, 0.25) !important;
    backdrop-filter: blur(16px) !important;
    display: flex !important;
    align-items: center !important;
}

/* Adjust position when sidebar is collapsed */
[data-testid="stSidebar"][aria-expanded="false"] ~ .main div[data-testid="stHorizontalBlock"]:has(div[key="custom_input_photos"]) {
    left: 50% !important;
    width: min(850px, 90vw) !important;
}

/* Vertical Alignment for Inner Columns */
div[data-testid="stHorizontalBlock"]:has(div[key="custom_input_photos"]) > div[data-testid="column"] {
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
}

/* Chat Input Interior Styling */
[data-testid="stChatInput"] {
    padding: 0 !important;
    margin: 0 !important;
    background: transparent !important;
}

[data-testid="stChatInput"] > div {
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
}

[data-testid="stChatInput"] textarea {
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
    color: #ffffff !important;
    font-size: 15px !important;
}

[data-testid="stChatInput"] textarea::placeholder {
    color: #7f89aa !important;
}

/* Circular Buttons for Popovers */
.stPopover button {
    border-radius: 50% !important;
    background: rgba(30, 35, 70, 0.75) !important;
    border: 1px solid rgba(120, 105, 255, 0.35) !important;
    color: #cbd2ef !important;
    height: 40px !important;
    width: 40px !important;
    min-height: 40px !important;
    padding: 0 !important;
    font-size: 18px !important;
}

.stPopover button:hover {
    background: rgba(110, 90, 220, 0.50) !important;
    border-color: rgba(160, 145, 255, 0.75) !important;
    color: #ffffff !important;
}

/* Login Box */
.login-container {
    width: min(460px, 90vw);
    margin: 10vh auto 22px auto;
    padding: 38px 40px;
    text-align: center;
    border-radius: 25px;
    background: linear-gradient(145deg, rgba(22,26,60,0.96), rgba(6,9,26,0.98));
    border: 1px solid rgba(120,105,255,0.50);
    box-shadow: 0 25px 80px rgba(0,0,0,0.50);
}

.login-title {
    font-family: 'Orbitron', sans-serif;
    font-size: 28px;
    font-weight: 900;
    background: linear-gradient(90deg, #ffffff, #b59cff, #67bfff);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}
</style>
""",
    unsafe_allow_html=True
)

# ============================================================
# BACKEND API UTILS
# ============================================================

def get_groq_client():
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        return None
    return Groq(api_key=api_key)

def ai_response(chat_history):
    client = get_groq_client()
    if not client:
        return "⚠️ **Groq API key missing.** Please set your `GROQ_API_KEY` in your environment."

    system_message = {
        "role": "system",
        "content": "You are Quantum Lab AI, an intelligent assistant."
    }
    full_messages = [system_message] + chat_history

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=full_messages
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"⚠️ **Inference error:** `{str(e)}`"

def transcribe_audio(audio_data):
    client = get_groq_client()
    if not client:
        return ""
    try:
        audio_file = io.BytesIO(audio_data) if isinstance(audio_data, bytes) else audio_data
        audio_file.name = "audio.wav"
        transcription = client.audio.transcriptions.create(
            file=audio_file,
            model="whisper-large-v3"
        )
        return transcription.text
    except Exception:
        return ""

# ============================================================
# LOGIN FLOW
# ============================================================

if not st.session_state.logged_in:
    st.markdown(
        """
        <div class="login-container">
            <div style="font-size: 44px; margin-bottom: 10px;">⚛️</div>
            <div class="login-title">QUANTUM LAB</div>
            <p style="color: #8c98ba; font-size: 13px; margin-top: 6px;">Sign in to your Quantum Workspace</p>
        </div>
        """,
        unsafe_allow_html=True
    )

    _, col2, _ = st.columns([1, 1.2, 1])
    with col2:
        email = st.text_input("Email", placeholder="researcher@quantum.lab")
        password = st.text_input("Password", type="password", placeholder="••••••••")
        if st.button("Initialize Terminal", use_container_width=True):
            if email:
                st.session_state.logged_in = True
                st.session_state.user_email = email
                st.rerun()
            else:
                st.warning("Please provide a valid email.")
    st.stop()

# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:
    username = st.session_state.user_email.split("@")[0].capitalize()

    st.markdown(
        f"""
        <div class="user-profile-card">
            <div class="profile-avatar">👨‍🚀</div>
            <div class="profile-info">
                <div class="profile-name">{username}</div>
                <div class="profile-status">● Quantum Node Online</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    if st.button("➕ New Chat", use_container_width=True):
        st.session_state.chat_counter += 1
        new_session = f"Quantum Session {st.session_state.chat_counter}"
        st.session_state.chats[new_session] = []
        st.session_state.current_chat = new_session
        st.rerun()

    st.markdown("<div style='margin: 10px 0; height: 1px; background: rgba(255,255,255,0.08);'></div>", unsafe_allow_html=True)
    st.caption("**CHAT SESSIONS**")

    for chat_name in list(st.session_state.chats.keys()):
        is_active = (chat_name == st.session_state.current_chat)
        label = f"👉 {chat_name}" if is_active else f"💬 {chat_name}"
        if st.button(label, key=f"session_btn_{chat_name}", use_container_width=True):
            st.session_state.current_chat = chat_name
            st.rerun()

    st.markdown("<div style='margin: 14px 0; height: 1px; background: rgba(255,255,255,0.08);'></div>", unsafe_allow_html=True)

    if st.button("🚪 Logout", use_container_width=True):
        st.session_state.logged_in = False
        st.session_state.user_email = ""
        st.rerun()

# ============================================================
# CHAT CONVERSATION VIEW
# ============================================================

current_messages = st.session_state.chats[st.session_state.current_chat]

for message in current_messages:
    role = message["role"]
    avatar = "👨‍🚀" if role == "user" else "⚛️"
    with st.chat_message(role, avatar=avatar):
        st.markdown(message["content"])

if st.session_state.staged_attachments or st.session_state.staged_voice_text:
    info_items = []
    if st.session_state.staged_attachments:
        info_items.append(f"📎 {len(st.session_state.staged_attachments)} item(s) attached")
    if st.session_state.staged_voice_text:
        info_items.append("🎙️ Voice text staged")
    st.info(" | ".join(info_items))

# ============================================================
# FIXED BOTTOM CHAT COMPOSER (GEMINI/CHATGPT PILL)
# ============================================================

composer_left, composer_input, composer_right = st.columns([0.07, 0.86, 0.07])

with composer_left:
    with st.popover("＋", help="Add photos, camera, or files"):
        st.markdown("### Attach")
        tab_photos, tab_camera, tab_files = st.tabs(["🖼️ Photos", "📷 Camera", "📎 Files"])

        with tab_photos:
            photos = st.file_uploader("Upload photos", type=["png", "jpg", "jpeg", "webp"], accept_multiple_files=True, key="custom_input_photos")
            if photos:
                for photo in photos:
                    note = f"🖼️ Photo: `{photo.name}` ({round(photo.size / 1024, 1)} KB)"
                    if note not in st.session_state.staged_attachments:
                        st.session_state.staged_attachments.append(note)
                st.success(f"{len(photos)} photo(s) attached.")

        with tab_camera:
            camera_photo = st.camera_input("Take a snapshot", key="custom_input_camera")
            if camera_photo:
                note = "📷 *Camera Snapshot*"
                if note not in st.session_state.staged_attachments:
                    st.session_state.staged_attachments.append(note)
                st.success("Snapshot attached.")

        with tab_files:
            files = st.file_uploader("Upload documents/code", type=["pdf", "txt", "docx", "csv", "xlsx", "py", "json"], accept_multiple_files=True, key="custom_input_files")
            if files:
                for file in files:
                    note = f"📎 Document: `{file.name}` ({round(file.size / 1024, 1)} KB)"
                    if note not in st.session_state.staged_attachments:
                        st.session_state.staged_attachments.append(note)
                st.success(f"{len(files)} file(s) attached.")

with composer_input:
    prompt = st.chat_input("Ask anything...", key="main_chat_input")

with composer_right:
    with st.popover("🎤", help="Voice recording"):
        st.markdown("### Voice Input")
        audio_stream = st.audio_input("Record audio note", key="custom_input_voice")
        if audio_stream:
            transcription = transcribe_audio(audio_stream.read())
            if transcription:
                st.session_state.staged_voice_text = transcription
                st.success("Voice transcribed! Text staged for prompt.")

# ============================================================
# PROCESS USER INPUT
# ============================================================

if prompt:
    user_text = prompt.strip()
    combined_parts = []
    if user_text:
        combined_parts.append(user_text)
    if st.session_state.staged_voice_text:
        combined_parts.append(f"🎙️ Transcribed Voice Note: \"{st.session_state.staged_voice_text}\"")
    if st.session_state.staged_attachments:
        combined_parts.append("\n".join(st.session_state.staged_attachments))

    full_query = "\n\n".join(combined_parts)
    st.session_state.staged_attachments = []
    st.session_state.staged_voice_text = ""

    current_messages.append({"role": "user", "content": full_query})
    response_text = ai_response(current_messages)
    current_messages.append({"role": "assistant", "content": response_text})

    st.rerun()
