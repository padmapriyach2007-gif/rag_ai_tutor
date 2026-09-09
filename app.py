import streamlit as st

from rag_engine import (
    get_or_create_user,
    create_chat_session,
    get_user_sessions,
    restore_chat,
    rename_chat,
    delete_chat,
    clear_chat,
    answer_question_stream, # Updated to import the streaming version
    initialize_knowledge_base
)

# =========================================================
# PAGE CONFIG & CSS
# =========================================================
st.set_page_config(page_title="Quantum Lab | AI Tutor", page_icon="⚛️", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
    <style>
    .stApp { background-color: #0b0f14; }
    .hero { text-align: center; padding: 40px 20px 20px 20px; }
    .hero-icon { font-size: 70px; margin-bottom: 10px; }
    .hero-title { font-size: 42px; font-weight: 800; letter-spacing: 2px; }
    .hero-subtitle { font-size: 18px; opacity: 0.75; margin-top: 8px; }
    .online { margin-top: 15px; font-size: 14px; font-weight: 600; }
    .learning-header { display: flex; align-items: center; gap: 12px; margin-top: 20px; margin-bottom: 15px; }
    .learning-icon { font-size: 28px; }
    .learning-title { font-size: 24px; font-weight: 700; }
    .info-card { padding: 20px; border-radius: 15px; background-color: #141a21; border: 1px solid #27303a; margin-bottom: 20px; }
    section[data-testid="stSidebar"] { background-color: #0d1117; }
    [data-testid="stChatMessage"] { border-radius: 12px; }
    [data-testid="stChatInput"] { border-radius: 15px; }
    </style>
""", unsafe_allow_html=True)

# =========================================================
# SESSION STATE
# =========================================================
for key in ["logged_in", "knowledge_initialized"]:
    if key not in st.session_state: st.session_state[key] = False
for key in ["user_email", "user_id", "session_id"]:
    if key not in st.session_state: st.session_state[key] = None
for key in ["messages", "sessions"]:
    if key not in st.session_state: st.session_state[key] = []

# =========================================================
# HELPER FUNCTIONS
# =========================================================
def start_new_chat():
    try:
        session_id = create_chat_session(st.session_state.user_id, "New Quantum Chat")
        st.session_state.session_id = session_id
        st.session_state.messages = []
        st.session_state.sessions = get_user_sessions(st.session_state.user_id)
    except Exception as e: st.error(f"Could not create chat: {e}")

def load_chat(session_id: str):
    try:
        history = restore_chat(session_id, st.session_state.user_id)
        st.session_state.session_id = session_id
        st.session_state.messages = [{"role": m["sender"], "content": m["content"]} for m in history if m["sender"] in ["user", "assistant"]]
    except Exception as e: st.error(f"Could not restore chat: {e}")

# =========================================================
# LOGIN PAGE
# =========================================================
def login_page():
    st.markdown("""<div class="hero"><div class="hero-icon">⚛️</div><div class="hero-title">QUANTUM AI TUTOR</div>
        <div class="hero-subtitle">Explore quantum computing through conversation</div><div class="online">● AI TUTOR ONLINE</div></div><br>""", unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.subheader("Welcome to Quantum Lab")
        email = st.text_input("Email address", placeholder="student@example.com")
        if st.button("🚀 Start Learning", use_container_width=True):
            if not email.strip(): return st.error("Please enter your email.")
            try:
                st.session_state.user_id = get_or_create_user(email)
                st.session_state.logged_in = True
                st.session_state.user_email = email.strip().lower()
                st.session_state.session_id = None
                st.session_state.messages = []
                st.session_state.sessions = get_user_sessions(st.session_state.user_id)
                st.rerun()
            except Exception as e: st.error(f"Login failed: {e}")

# =========================================================
# SIDEBAR
# =========================================================
def sidebar():
    with st.sidebar:
        st.markdown("""<div style="text-align:center; font-size:28px; font-weight:800; margin-bottom:20px;">⚛️ Quantum Lab</div>""", unsafe_allow_html=True)
        st.markdown("---")
        st.write(f"👤 {st.session_state.user_email}")
        st.markdown("---")

        if st.button("＋ New Chat", use_container_width=True):
            start_new_chat()
            st.rerun()
            
        st.markdown("### 💬 My Chats")
        if st.button("🔄 Refresh", use_container_width=True):
            st.session_state.sessions = get_user_sessions(st.session_state.user_id)
            st.rerun()

        if not st.session_state.sessions: st.caption("No chats yet.")
        else:
            for chat in st.session_state.sessions:
                s_id = chat.get("session_id")
                title = (chat.get("title") or "Untitled Chat")[:28] + ("..." if len(chat.get("title") or "") > 28 else "")
                if st.button(f"💬 {title}", key=f"chat_{s_id}", use_container_width=True):
                    load_chat(s_id)
                    st.rerun()

        if st.session_state.session_id:
            st.markdown("---")
            st.markdown("### ⚙️ Chat Actions")
            new_title = st.text_input("Rename chat", placeholder="Enter new chat name", key="rename_input")
            if st.button("✏️ Rename Chat", use_container_width=True):
                if new_title.strip():
                    try:
                        rename_chat(st.session_state.session_id, st.session_state.user_id, new_title)
                        st.session_state.sessions = get_user_sessions(st.session_state.user_id)
                        st.success("Chat renamed.")
                        st.rerun()
                    except Exception as e: st.error(str(e))
                else: st.warning("Enter a chat name.")
            if st.button("🧹 Clear Chat", use_container_width=True):
                clear_chat(st.session_state.session_id, st.session_state.user_id)
                st.session_state.messages = []
                st.rerun()
            if st.button("🗑️ Delete Chat", use_container_width=True):
                delete_chat(st.session_state.session_id, st.session_state.user_id)
                st.session_state.session_id = None
                st.session_state.messages = []
                st.session_state.sessions = get_user_sessions(st.session_state.user_id)
                st.rerun()

        st.markdown("---")
        st.markdown("### 📚 Knowledge Base")
        st.caption("RAG documents are stored in Supabase.")
        if st.button("📥 Index Documents", use_container_width=True):
            with st.spinner("Indexing documents..."):
                count = initialize_knowledge_base()
                if count > 0: st.success(f"Indexed {count} new document(s).")
                else: st.info("No new documents to index.")

        st.markdown("---")
        if st.button("🚪 Logout", use_container_width=True):
            for key in ["logged_in", "user_email", "user_id", "session_id", "messages", "sessions"]: st.session_state[key] = None
            st.rerun()

# =========================================================
# MAIN TUTOR PAGE
# =========================================================
def tutor_page():
    st.markdown("""<div class="hero"><div class="hero-icon">⚛️</div><div class="hero-title">QUANTUM AI TUTOR</div><div class="online">● AI TUTOR ONLINE</div></div>""", unsafe_allow_html=True)
    st.markdown("""<div class="learning-header"><div class="learning-icon">🧠</div><div class="learning-title">Learning Mode</div></div>""", unsafe_allow_html=True)

    if not st.session_state.session_id:
        return st.info("Start a new chat from the sidebar to begin learning.")

    for message in st.session_state.messages:
        with st.chat_message(message["role"]): st.markdown(message["content"])

    if prompt := st.chat_input("Ask your AI Tutor anything..."):
        prompt = prompt.strip()
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"): st.markdown(prompt)

        with st.chat_message("assistant"):
            try:
                # Capture the stream directly to the UI
                stream = answer_question_stream(query=prompt, session_id=st.session_state.session_id, user_id=st.session_state.user_id)
                response = st.write_stream(stream) 
            except Exception as e:
                response = f"⚠️ Something went wrong.\n\n`{str(e)}`"
                st.markdown(response)

        # Save the full generated response to Streamlit state
        st.session_state.messages.append({"role": "assistant", "content": response})

# =========================================================
# APPLICATION
# =========================================================
if not st.session_state.logged_in: login_page()
else:
    sidebar()
    tutor_page()
