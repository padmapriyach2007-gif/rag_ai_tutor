import io
import os
import streamlit as st
from groq import Groq

# ============================================================
# PAGE CONFIGURATION
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
# STYLING (FIXED BOTTOM DOCK + INTEGRATED PROMPT PILL)
# ============================================================

st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@500;700;900&family=Inter:wght@400;500;600;700&display=swap');

html, body {
    font-family: 'Inter', sans-serif;
}

/* Deep Space Theme Background */
.stApp {
    background:
        radial-gradient(circle at 15% 20%, rgba(108, 63, 255, 0.18), transparent 25%),
        radial-gradient(circle at 85% 15%, rgba(0, 157, 255, 0.16), transparent 28%),
        radial-gradient(circle at 50% 80%, rgba(168, 52, 255, 0.13), transparent 32%),
        linear-gradient(135deg, #02030d, #070b20, #030716);
    color: #ffffff;
}

/* Main chat container padding bottom so messages are not hidden by fixed dock */
.main .block-container {
    padding-bottom: 140px !important;
}

/* Sidebar Custom Styling */
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
    width: 40px;
    height: 40px;
    border-radius: 12px;
    background: linear-gradient(135deg, #7c4dff, #1e88e5);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 20px;
    border: 1px solid rgba(255, 255, 255, 0.25);
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

/* Sticky Fixed Bottom Wrapper */
div[data-testid="stVerticalBlock"] > div:has(.bottom-dock-wrapper) {
    position: fixed;
    bottom: 24px;
    left: 50%;
    transform: translateX(-50%);
    width: min(840px, 92vw);
    z-index: 9999;
}

/* Seamless Rounded Input Pill Box */
.bottom-dock-wrapper {
    background: rgba(16, 20, 42, 0.95);
    border: 1px solid rgba(120, 105, 255, 0.35);
    border-radius: 30px;
    padding: 4px 12px;
    box-shadow: 0 12px 35px rgba(0, 0, 0, 0.6);
    backdrop-filter: blur(14px);
}

/* Column vertical alignment */
.bottom-dock-wrapper div[data-testid="column"] {
    display: flex;
    align-items: center;
    justify-content: center;
}

/* Customizing chat input inside the pill */
.bottom-dock-wrapper [data-testid="stChatInput"] {
    padding: 0 !important;
}

.bottom-dock-wrapper [data-testid="stChatInput"] > div {
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
}

.bottom-dock-wrapper [data-testid="stChatInput"] textarea {
    background: transparent !important;
    border: none !important;
    color: #ffffff !important;
    font-size: 15px !important;
}

/* Subdued popover buttons matching Gemini interface */
.bottom-dock-wrapper .stPopover button {
    border-radius: 50% !important;
    background: transparent !important;
    border: none !important;
    color: #bfc6e5 !important;
    height: 38px !important;
    width: 38px !important;
    padding: 0 !important;
    transition: all 0.2s ease;
}

.bottom-dock-wrapper .stPopover button:hover {
    background: rgba(120, 105, 255, 0.25) !important;
    color: #ffffff !important;
}

/* Login Card */
.login-container {
    width: min(440px, 90vw);
    margin: 12vh auto 20px auto;
    padding: 36px;
    text-align: center;
    border-radius: 24px;
    background: linear-gradient(145deg, rgba(22,26,60,0.96), rgba(6,9,26,0.98));
    border: 1px solid rgba(120,105,255,0.45);
    box-shadow: 0 20px 60px rgba(0,0,0,0.6);
}

.login-title {
    font-family: 'Orbitron', sans-serif;
    font-size: 26px;
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
# API HELPERS
# ============================================================

def get_groq_client():
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        return None
    return Groq(api_key=api_key)

def fetch_ai_response(messages):
    client = get_groq_client()
    if not client:
        return "⚠️ **Groq API Key Missing.** Please set `GROQ_API_KEY` in your environment variables."

    system_msg = {
        "role": "system",
        "content": "You are Quantum AI, an advanced intelligent system providing concise, accurate, and helpful answers."
    }
    
    try:
        res = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[system_msg] + messages
        )
        return res.choices[0].message.content
    except Exception as e:
        return f"⚠️ **API Error:** `{str(e)}`"

def transcribe_voice(audio_bytes):
    client = get_groq_client()
    if not client:
        return ""
    try:
        f = io.BytesIO(audio_bytes)
        f.name = "recording.wav"
        res = client.audio.transcriptions.create(
            file=f,
            model="whisper-large-v3"
        )
        return res.text
    except Exception:
        return ""

# ============================================================
# LOGIN FLOW
# ============================================================

if not st.session_state.logged_in:
    st.markdown(
        """
        <div class="login-container">
            <div style="font-size: 42px; margin-bottom: 8px;">⚛️</div>
            <div class="login-title">QUANTUM LAB</div>
            <p style="color: #8c98ba; font-size: 13px; margin-top: 4px;">Sign in to access your workspace</p>
        </div>
        """,
        unsafe_allow_html=True
    )

    _, col2, _ = st.columns([1, 1.2, 1])
    with col2:
        email = st.text_input("Email", placeholder="user@quantum.lab")
        pwd = st.text_input("Password", type="password", placeholder="••••••••")
        if st.button("Enter Terminal", use_container_width=True):
            if email:
                st.session_state.logged_in = True
                st.session_state.user_email = email
                st.rerun()
            else:
                st.warning("Please provide your email.")
    st.stop()

# ============================================================
# SIDEBAR NAVIGATION
# ============================================================

with st.sidebar:
    username = st.session_state.user_email.split("@")[0].capitalize()
    st.markdown(
        f"""
        <div class="user-profile-card">
            <div class="profile-avatar">👨‍🚀</div>
            <div style="overflow:hidden;">
                <div class="profile-name">{username}</div>
                <div class="profile-status">● Workspace Active</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    if st.button("➕ New Chat Session", use_container_width=True):
        st.session_state.chat_counter += 1
        new_name = f"Quantum Session {st.session_state.chat_counter}"
        st.session_state.chats[new_name] = []
        st.session_state.current_chat = new_name
        st.rerun()

    st.markdown("<div style='margin: 10px 0; height: 1px; background: rgba(255,255,255,0.1);'></div>", unsafe_allow_html=True)
    st.caption("**SESSIONS**")

    for chat_title in list(st.session_state.chats.keys()):
        is_active = (chat_title == st.session_state.current_chat)
        lbl = f"👉 {chat_title}" if is_active else f"💬 {chat_title}"
        if st.button(lbl, key=f"sess_{chat_title}", use_container_width=True):
            st.session_state.current_chat = chat_title
            st.rerun()

    st.markdown("<div style='margin: 10px 0; height: 1px; background: rgba(255,255,255,0.1);'></div>", unsafe_allow_html=True)

    if st.button("🚪 Log Out", use_container_width=True):
        st.session_state.logged_in = False
        st.session_state.user_email = ""
        st.rerun()

# ============================================================
# CONVERSATION VIEW
# ============================================================

messages = st.session_state.chats[st.session_state.current_chat]

for msg in messages:
    avatar = "👨‍🚀" if msg["role"] == "user" else "⚛️"
    with st.chat_message(msg["role"], avatar=avatar):
        st.markdown(msg["content"])

# Displays active staged items directly above the bottom input bar
staged_list = []
if st.session_state.staged_attachments:
    staged_list.append(f"📎 {len(st.session_state.staged_attachments)} file(s) attached")
if st.session_state.staged_voice_text:
    staged_list.append(f"🎙️ Voice note staged")

if staged_list:
    st.info(" | ".join(staged_list))

# ============================================================
# FIXED BOTTOM PROMPT BOX (PLUS - CHAT INPUT - MIC)
# ============================================================

st.markdown('<div class="bottom-dock-wrapper">', unsafe_allow_html=True)

col_plus, col_input, col_mic = st.columns([0.06, 0.88, 0.06])

# 1. Plus Icon Popover (Photos, Camera, Files)
with col_plus:
    with st.popover("＋", help="Attach Photos, Camera, Files"):
        st.markdown("### Attach Content")
        tab_photos, tab_cam, tab_files = st.tabs(["🖼️ Photos", "📷 Camera", "📎 Files"])

        with tab_photos:
            photos = st.file_uploader("Upload photos", type=["png", "jpg", "jpeg", "webp"], accept_multiple_files=True, key="photos_up")
            if photos:
                for p in photos:
                    st.session_state.staged_attachments.append(f"🖼️ Photo: `{p.name}`")
                st.success(f"{len(photos)} photo(s) added.")

        with tab_cam:
            cam_pic = st.camera_input("Take snapshot", key="cam_up")
            if cam_pic:
                st.session_state.staged_attachments.append("📷 Camera Snapshot")
                st.success("Snapshot added.")

        with tab_files:
            files = st.file_uploader("Upload files", type=["pdf", "txt", "docx", "py", "csv"], accept_multiple_files=True, key="files_up")
            if files:
                for f in files:
                    st.session_state.staged_attachments.append(f"📎 Document: `{f.name}`")
                st.success(f"{len(files)} file(s) added.")

# 2. Centered Native Prompt Input Box
with col_input:
    prompt = st.chat_input("Ask anything...", key="unified_dock_input")

# 3. Microphone Icon Popover
with col_mic:
    with st.popover("🎤", help="Record audio note"):
        st.markdown("### Voice Input")
        audio_stream = st.audio_input("Record message", key="voice_rec")
        if audio_stream:
            txt = transcribe_voice(audio_stream.read())
            if txt:
                st.session_state.staged_voice_text = txt
                st.success("Voice transcribed and staged!")
            else:
                st.session_state.staged_voice_text = "[Voice Recording Captured]"
                st.success("Voice recording captured!")

st.markdown('</div>', unsafe_allow_html=True)

# ============================================================
# RESPONSE GENERATION
# ============================================================

if prompt:
    user_entry = prompt.strip()

    combined_query = []
    if user_entry:
        combined_query.append(user_entry)
    if st.session_state.staged_voice_text:
        combined_query.append(f"🎙️ Transcribed Voice: \"{st.session_state.staged_voice_text}\"")
    if st.session_state.staged_attachments:
        combined_query.append("\n".join(st.session_state.staged_attachments))

    full_text = "\n\n".join(combined_query)

    # Reset staged items
    st.session_state.staged_attachments = []
    st.session_state.staged_voice_text = ""

    # Add user message
    messages.append({"role": "user", "content": full_text})

    # Fetch and store AI response
    reply = fetch_ai_response(messages)
    messages.append({"role": "assistant", "content": reply})

    st.rerun()
