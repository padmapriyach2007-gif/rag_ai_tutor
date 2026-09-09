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

if "staged_voice_text" not in st.session_state:
    st.session_state.staged_voice_text = ""

# ============================================================
# GALAXY THEME CSS
# ============================================================

st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;500;600;700;800;900&family=Inter:wght@400;500;600;700;800&display=swap');

html, body {
    font-family: 'Inter', sans-serif;
}

.stApp {
    background:
        radial-gradient(circle at 15% 20%, rgba(108, 63, 255, 0.18), transparent 25%),
        radial-gradient(circle at 85% 15%, rgba(0, 157, 255, 0.16), transparent 28%),
        radial-gradient(circle at 50% 80%, rgba(168, 52, 255, 0.13), transparent 32%),
        linear-gradient(135deg, #02030d, #070b20, #030716);
    color: #ffffff;
}

.stApp::before {
    content: "";
    position: fixed;
    inset: 0;
    pointer-events: none;
    background-image:
        radial-gradient(1px 1px at 10% 20%, rgba(255,255,255,0.8), transparent),
        radial-gradient(1px 1px at 20% 80%, rgba(160,190,255,0.8), transparent),
        radial-gradient(1px 1px at 35% 35%, rgba(255,255,255,0.7), transparent),
        radial-gradient(1px 1px at 50% 15%, rgba(170,120,255,0.8), transparent),
        radial-gradient(1px 1px at 65% 70%, rgba(255,255,255,0.7), transparent),
        radial-gradient(1px 1px at 80% 40%, rgba(100,180,255,0.8), transparent),
        radial-gradient(2px 2px at 90% 85%, rgba(255,255,255,0.9), transparent);
    background-size: 250px 250px;
    opacity: 0.7;
    animation: starsMove 25s linear infinite;
}

@keyframes starsMove {
    0% { transform: translateY(0px); }
    50% { transform: translateY(-15px); }
    100% { transform: translateY(0px); }
}

/* Sidebar Styles */
[data-testid="stSidebar"] {
    background:
        radial-gradient(circle at 30% 5%, rgba(105, 65, 255, 0.18), transparent 30%),
        radial-gradient(circle at 80% 75%, rgba(0, 150, 255, 0.10), transparent 35%),
        linear-gradient(180deg, #03040e, #070a1c, #02030b) !important;
    border-right: 1px solid rgba(120, 105, 255, 0.25);
}

.user-profile-card {
    background: linear-gradient(135deg, rgba(28, 32, 68, 0.75), rgba(12, 16, 42, 0.85));
    border: 1px solid rgba(130, 115, 255, 0.35);
    border-radius: 16px;
    padding: 14px;
    margin-bottom: 18px;
    display: flex;
    align-items: center;
    gap: 12px;
}

.profile-avatar {
    width: 44px;
    height: 44px;
    border-radius: 12px;
    background: linear-gradient(135deg, #7c4dff, #1e88e5);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 22px;
    border: 1px solid rgba(255, 255, 255, 0.25);
    box-shadow: 0 0 15px rgba(124, 77, 255, 0.45);
}

.profile-info {
    overflow: hidden;
}

.profile-name {
    font-family: 'Orbitron', sans-serif;
    font-size: 13px;
    font-weight: 700;
    color: #ffffff;
    letter-spacing: 0.5px;
}

.profile-status {
    font-size: 11px;
    color: #4cf0a0;
    letter-spacing: 0.5px;
}

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
    box-shadow: 0 4px 18px rgba(70,60,200,0.3);
}

/* Prompt Dock Toolbar */
.prompt-dock-wrapper {
    background: rgba(10, 14, 38, 0.90);
    backdrop-filter: blur(12px);
    border: 1px solid rgba(120, 105, 255, 0.35);
    border-radius: 14px;
    padding: 6px 12px;
    margin-bottom: 8px;
}

[data-testid="stPopoverBody"] {
    background: #080c24 !important;
    border: 1px solid rgba(120, 105, 255, 0.45) !important;
    border-radius: 16px !important;
    color: #ffffff !important;
    box-shadow: 0 10px 40px rgba(0,0,0,0.75) !important;
}

/* Chat Input custom glow */
[data-testid="stChatInput"] textarea {
    background: rgba(6, 9, 27, 0.94) !important;
    border: 1px solid rgba(105, 105, 175, 0.38) !important;
    color: white !important;
    border-radius: 15px !important;
}

[data-testid="stChatInput"] textarea:focus {
    border-color: rgba(120, 105, 255, 0.85) !important;
    box-shadow: 0 0 20px rgba(90, 75, 255, 0.25) !important;
}

/* Login Screen */
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
        "content": (
            "You are Quantum Lab AI, an intelligent, helpful, and adaptive assistant. "
            "You answer questions clearly across technical, scientific, and everyday domains. "
            "When analyzing attached files or transcripts, integrate your reasoning seamlessly."
        )
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
        if isinstance(audio_data, bytes):
            audio_file = io.BytesIO(audio_data)
        else:
            audio_file = audio_data
        audio_file.name = "audio.wav"
        transcription = client.audio.transcriptions.create(
            file=audio_file,
            model="whisper-large-v3"
        )
        return transcription.text
    except Exception as e:
        st.error(f"Voice transcription failed: {e}")
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
# SIDEBAR (TOP-LEFT MENU: PROFILE, NEW CHAT, CHAT HISTORY)
# ============================================================

with st.sidebar:
    # 1. Profile
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

    # 2. New Chat
    if st.button("➕ New Chat", use_container_width=True):
        st.session_state.chat_counter += 1
        new_session = f"Quantum Session {st.session_state.chat_counter}"
        st.session_state.chats[new_session] = []
        st.session_state.current_chat = new_session
        st.rerun()

    st.markdown("<div style='margin: 10px 0; height: 1px; background: rgba(255,255,255,0.08);'></div>", unsafe_allow_html=True)
    st.caption("**CHAT SESSIONS**")

    # 3. Chat History Switcher
    for chat_name in list(st.session_state.chats.keys()):
        is_active = (chat_name == st.session_state.current_chat)
        label = f"👉 {chat_name}" if is_active else f"💬 {chat_name}"
        if st.button(label, key=f"session_btn_{chat_name}", use_container_width=True):
            st.session_state.current_chat = chat_name
            st.rerun()

    st.markdown("<div style='margin: 14px 0; height: 1px; background: rgba(255,255,255,0.08);'></div>", unsafe_allow_html=True)
    st.caption("**SESSION TOOLS**")

    # 4. Session Operations
    with st.expander("⚙️ Manage Session"):
        rename_input = st.text_input("Rename Title", value=st.session_state.current_chat)
        if st.button("Confirm Rename"):
            if rename_input and rename_input != st.session_state.current_chat:
                st.session_state.chats[rename_input] = st.session_state.chats.pop(st.session_state.current_chat)
                st.session_state.current_chat = rename_input
                st.rerun()

        if st.button("🗑️ Delete Current Chat"):
            if len(st.session_state.chats) > 1:
                del st.session_state.chats[st.session_state.current_chat]
                st.session_state.current_chat = list(st.session_state.chats.keys())[0]
                st.rerun()
            else:
                st.warning("Cannot delete the only remaining session.")

        if st.button("🧹 Clear Messages"):
            st.session_state.chats[st.session_state.current_chat] = []
            st.rerun()

    # 5. Logout
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

# ============================================================
# PROMPT SPACE: ATTACHMENTS (CAMERA, PHOTOS, FILES) & MIC
# ============================================================

st.markdown("<div class='prompt-dock-wrapper'>", unsafe_allow_html=True)

col_attach, col_mic, col_status = st.columns([1.2, 1.2, 5])

attachment_notes = []

# Attachments Popover: Camera, Photos, Files
with col_attach:
    with st.popover("📎 Attach"):
        tab_cam, tab_photos, tab_files = st.tabs(["📷 Camera", "🖼️ Photos", "📁 Files"])

        with tab_cam:
            cam_capture = st.camera_input("Capture with Camera", key="dock_cam")
            if cam_capture:
                attachment_notes.append("📷 *Live Camera snapshot attached.*")
                st.success("Snapshot staged.")

        with tab_photos:
            photo_uploads = st.file_uploader(
                "Upload photos",
                type=["png", "jpg", "jpeg", "webp"],
                accept_multiple_files=True,
                key="dock_photos"
            )
            if photo_uploads:
                for photo in photo_uploads:
                    attachment_notes.append(f"🖼️ *Photo:* `{photo.name}` ({round(photo.size / 1024, 1)} KB)")
                st.success(f"{len(photo_uploads)} photo(s) staged.")

        with tab_files:
            file_uploads = st.file_uploader(
                "Upload documents, code, or datasets",
                type=["pdf", "txt", "csv", "py", "json", "docx"],
                accept_multiple_files=True,
                key="dock_files"
            )
            if file_uploads:
                for fl in file_uploads:
                    attachment_notes.append(f"📁 *Document:* `{fl.name}` ({round(fl.size / 1024, 1)} KB)")
                st.success(f"{len(file_uploads)} file(s) staged.")

# Microphone Popover: Record and Whisper Transcribe
with col_mic:
    with st.popover("🎙️ Voice"):
        st.caption("Record voice prompt:")
        audio_stream = st.audio_input("Record Audio", key="dock_mic")
        if audio_stream:
            with st.spinner("Transcribing quantum voice note..."):
                transcription = transcribe_audio(audio_stream.read())
                if transcription:
                    st.session_state.staged_voice_text = transcription
                    st.success("Transcribed successfully!")

with col_status:
    # Notification pills showing staged items
    status_badges = []
    if attachment_notes:
        status_badges.append(f"📎 {len(attachment_notes)} item(s) attached")
    if st.session_state.staged_voice_text:
        status_badges.append(f"🎙️ Voice: \"{st.session_state.staged_voice_text[:35]}...\"")

    if status_badges:
        st.markdown(
            f"<div style='padding: 6px 0; font-size: 11px; color: #62b0ff;'>{' | '.join(status_badges)}</div>",
            unsafe_allow_html=True
        )

st.markdown("</div>", unsafe_allow_html=True)

# Main Text Input Bar
typed_prompt = st.chat_input("Ask anything or submit instructions...")

# Determine final query between typed or voice inputs
chosen_text = typed_prompt if typed_prompt else (st.session_state.staged_voice_text if typed_prompt is None and st.session_state.staged_voice_text and not typed_prompt else None)

if typed_prompt or (st.session_state.staged_voice_text and not typed_prompt and st.button("🚀 Send Voice Prompt")):
    final_query = typed_prompt if typed_prompt else st.session_state.staged_voice_text

    # Merge attachments metadata with the prompt
    if attachment_notes:
        full_query = f"{final_query}\n\n" + "\n".join(attachment_notes)
    else:
        full_query = final_query

    # Reset staged voice
    st.session_state.staged_voice_text = ""

    # Append & display user message
    current_messages.append({"role": "user", "content": full_query})
    with st.chat_message("user", avatar="👨‍🚀"):
        st.markdown(full_query)

    # Compute AI response
    with st.chat_message("assistant", avatar="⚛️"):
        with st.spinner("Computing response..."):
            reply = ai_response(current_messages)
            st.markdown(reply)

    current_messages.append({"role": "assistant", "content": reply})
