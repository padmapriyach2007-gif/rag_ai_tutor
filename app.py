import io
import os
import streamlit as st
from groq import Groq

# ============================================================
# PAGE CONFIG & CSS FOR THE GEMINI-STYLE PILL BAR
# ============================================================

st.set_page_config(
    page_title="Quantum Lab",
    page_icon="⚛️",
    layout="wide"
)

st.markdown(
    """
<style>
/* Outer pill container mimicking the Gemini search box */
.gemini-bar-container {
    background: #1e1f22;
    border: 1px solid rgba(255, 255, 255, 0.12);
    border-radius: 30px;
    padding: 6px 16px;
    display: flex;
    align-items: center;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.4);
}

/* Strip default Streamlit borders & backgrounds inside the pill */
.gemini-bar-container [data-testid="stChatInput"] {
    padding: 0 !important;
}

.gemini-bar-container [data-testid="stChatInput"] > div {
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
}

.gemini-bar-container [data-testid="stChatInput"] textarea {
    background: transparent !important;
    border: none !important;
    color: #e3e3e3 !important;
    font-size: 15px !important;
}

.gemini-bar-container [data-testid="stChatInput"] textarea::placeholder {
    color: #8e9196 !important;
}

/* Minimalist icon buttons inside the bar */
.gemini-bar-container .stPopover button, 
.gemini-bar-container .stSelectbox > div > div {
    background: transparent !important;
    border: none !important;
    color: #c4c7c5 !important;
    box-shadow: none !important;
    padding: 0 8px !important;
}

.gemini-bar-container .stPopover button:hover {
    color: #ffffff !important;
    background: rgba(255, 255, 255, 0.08) !important;
    border-radius: 50% !important;
}

/* Align columns vertically within the container */
div[data-testid="column"] {
    display: flex;
    align-items: center;
    justify-content: center;
}
</style>
""",
    unsafe_allow_html=True
)

# Initialize attachment & voice state if not present
if "staged_attachments" not in st.session_state:
    st.session_state.staged_attachments = []
if "staged_voice_text" not in st.session_state:
    st.session_state.staged_voice_text = ""

# ============================================================
# GEMINI-STYLE INTEGRATED PROMPT BAR
# ============================================================

st.markdown('<div class="gemini-bar-container">', unsafe_allow_html=True)

# Define column layout: [Plus, Text Field, Model Dropdown, Mic]
col_plus, col_input, col_model, col_mic = st.columns([0.04, 0.76, 0.14, 0.06])

# 1. Left + (Plus) Attachment Popover
with col_plus:
    with st.popover("➕", help="Add attachment"):
        st.markdown("### Attach Content")
        tab_photos, tab_cam, tab_files = st.tabs(["🖼️ Photos", "📷 Camera", "📎 Files"])
        
        with tab_photos:
            photos = st.file_uploader("Upload photos", type=["png", "jpg", "jpeg"], accept_multiple_files=True, key="gemini_photos")
            if photos:
                for p in photos:
                    st.session_state.staged_attachments.append(f"🖼️ Photo: `{p.name}`")
                st.success("Photos added.")

        with tab_cam:
            cam_pic = st.camera_input("Take picture", key="gemini_cam")
            if cam_pic:
                st.session_state.staged_attachments.append("📷 Camera Snapshot")
                st.success("Snapshot captured.")

        with tab_files:
            files = st.file_uploader("Upload files", type=["pdf", "txt", "docx", "py", "csv"], accept_multiple_files=True, key="gemini_files")
            if files:
                for f in files:
                    st.session_state.staged_attachments.append(f"📎 File: `{f.name}`")
                st.success("Files attached.")

# 2. Middle Text Area ("Ask Gemini...")
with col_input:
    prompt = st.chat_input("Ask Gemini...", key="gemini_chat_input")

# 3. Model Selector Dropdown ("Flash ∨")
with col_model:
    selected_model = st.selectbox(
        "Model",
        ["Flash", "Pro", "Thinking"],
        label_visibility="collapsed",
        key="selected_gemini_model"
    )

# 4. Right Microphone Popover
with col_mic:
    with st.popover("🎙️", help="Voice Input"):
        st.markdown("### Voice Record")
        audio_input = st.audio_input("Speak prompt", key="gemini_voice_input")
        if audio_input:
            st.session_state.staged_voice_text = "[Voice Recording Captured]"
            st.success("Voice note captured!")

st.markdown('</div>', unsafe_allow_html=True)

# ============================================================
# HANDLING SUBMISSIONS
# ============================================================

if prompt:
    user_query = prompt.strip()
    st.write(f"**Selected Model:** {selected_model}")
    st.write(f"**Prompt:** {user_query}")
    if st.session_state.staged_attachments:
        st.write(f"**Attachments:** {st.session_state.staged_attachments}")
    if st.session_state.staged_voice_text:
        st.write(f"**Voice:** {st.session_state.staged_voice_text}")
