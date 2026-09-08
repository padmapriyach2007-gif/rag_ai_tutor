import streamlit as st
from rag_engine import (
    get_or_create_user,
    create_chat_session,
    get_user_sessions,
    get_chat_history,
    answer_question,
    delete_chat
)


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

if "user_id" not in st.session_state:
    st.session_state.user_id = None

if "current_session_id" not in st.session_state:
    st.session_state.current_session_id = None


# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown(
    """
<style>

    /* MAIN APP */
    .stApp {
        background-color: #07091a;
    }

    [data-testid="stMain"] {
        background-color: #07091a;
    }

    /* SIDEBAR */
    [data-testid="stSidebar"] {
        background-color: #08091b;
    }

    [data-testid="stSidebar"] h1 {
        color: white;
    }

    /* BUTTONS */
    [data-testid="stSidebar"] .stButton > button {
        width: 100%;
        border-radius: 8px;
        min-height: 42px;
        background-color: #292b37;
        border: 1px solid #3c3e50;
        color: white;
    }

    [data-testid="stSidebar"] .stButton > button:hover {
        background-color: #363847;
        border-color: #6c63ff;
    }

    /* HERO BOX */
    .hero-box {
        background-color: #191b25;
        border: 1px solid #292c3a;
        border-radius: 15px;
        padding: 55px 20px;
        text-align: center;
        margin-top: 25px;
        margin-bottom: 25px;
    }

    .hero-icon {
        font-size: 48px;
    }

    .hero-title {
        font-size: 42px;
        font-weight: 700;
        color: white;
        margin-top: 10px;
    }

    .hero-subtitle {
        font-size: 17px;
        color: #aeb1c5;
        margin-top: 10px;
    }

    .online {
        color: #42e88b;
        font-size: 14px;
        margin-top: 18px;
    }

    /* LOGIN BOX */
    .login-box {
        max-width: 550px;
        margin: 100px auto;
        background-color: #191b25;
        border: 1px solid #292c3a;
        border-radius: 15px;
        padding: 40px;
        text-align: center;
    }

</style>
""",
    unsafe_allow_html=True
)


# ============================================================
# LOGIN SCREEN
# ============================================================

if not st.session_state.logged_in:

    st.markdown(
        """
<div class="login-box">
    <div class="hero-icon">⚛️</div>
    <h1>Quantum Lab</h1>
    <p>AI-Powered Learning Space</p>
</div>
""",
        unsafe_allow_html=True
    )

    st.subheader("🔐 Login")

    email = st.text_input(
        "Email address",
        placeholder="Enter your email"
    )

    if st.button("🚀 Login", use_container_width=True):

        if email.strip() == "":
            st.error("Please enter your email address.")

        else:
            try:
                user_id = get_or_create_user(email)
                st.session_state.user_email = email.strip()
                st.session_state.user_id = user_id
                st.session_state.logged_in = True

                # Load existing user sessions or create a new default one
                sessions = get_user_sessions(user_id)
                if sessions:
                    st.session_state.current_session_id = sessions[0]["session_id"]
                else:
                    new_session_id = create_chat_session(user_id, "Quantum Learning")
                    st.session_state.current_session_id = new_session_id

                st.success("Login successful!")
                st.rerun()

            except Exception as e:
                st.error(f"Authentication failed: {str(e)}")

    st.stop()


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.title("⚛️ QUANTUM LAB")
    st.caption("AI-Powered Learning Space")

    st.markdown("---")
    st.write("👤 **Logged In**")
    st.caption(st.session_state.user_email)

    # --------------------------------------------------------
    # NEW CHAT
    # --------------------------------------------------------
    st.markdown("---")

    if st.button("➕ New Chat", use_container_width=True):

        sessions = get_user_sessions(st.session_state.user_id)
        chat_number = len(sessions) + 1
        new_title = f"New Quantum Chat {chat_number}"

        try:
            new_session_id = create_chat_session(
                st.session_state.user_id,
                title=new_title
            )
            st.session_state.current_session_id = new_session_id
            st.toast("New chat created!")
            st.rerun()
        except Exception as e:
            st.error(f"Failed to create chat: {str(e)}")

    # --------------------------------------------------------
    # YOUR CHATS
    # --------------------------------------------------------
    st.markdown("---")
    st.subheader("💬 Your Chats")

    sessions = get_user_sessions(st.session_state.user_id)

    for session in sessions:
        s_id = session["session_id"]
        s_title = session.get("title", "Untitled Chat")

        is_current = (s_id == st.session_state.current_session_id)
        button_text = f"🟣 {s_title}" if is_current else f"💬 {s_title}"

        if st.button(
            button_text,
            key=f"session_{s_id}",
            use_container_width=True
        ):
            st.session_state.current_session_id = s_id
            st.rerun()

    # --------------------------------------------------------
    # DELETE CURRENT CHAT
    # --------------------------------------------------------
    st.markdown("---")

    if st.button("🗑️ Delete Current Chat", use_container_width=True):
        if st.session_state.current_session_id:
            try:
                delete_chat(
                    st.session_state.current_session_id,
                    st.session_state.user_id
                )
                st.toast("Chat deleted!")

                # Switch to remaining session or create new
                remaining = get_user_sessions(st.session_state.user_id)
                if remaining:
                    st.session_state.current_session_id = remaining[0]["session_id"]
                else:
                    new_id = create_chat_session(st.session_state.user_id, "Quantum Learning")
                    st.session_state.current_session_id = new_id

                st.rerun()
            except Exception as e:
                st.error(f"Failed to delete chat: {str(e)}")

    # --------------------------------------------------------
    # LOGOUT
    # --------------------------------------------------------
    if st.button("🚪 Logout", use_container_width=True):
        st.session_state.logged_in = False
        st.session_state.user_email = ""
        st.session_state.user_id = None
        st.session_state.current_session_id = None
        st.rerun()

    # --------------------------------------------------------
    # LEARNING MODE
    # --------------------------------------------------------
    st.markdown("---")
    st.info(
        """
🧠 **Learning Mode Active**

Ask dynamic questions regarding:
• Quantum Computing & Mechanics
• Qiskit Code & Algorithms
• General Science & Programming
• Live Web & Current Contexts
        """
    )


# ============================================================
# MAIN AREA - HERO BOX
# ============================================================

st.markdown(
    """
<div class="hero-box">
    <div class="hero-icon">⚛️</div>
    <div class="hero-title">Quantum AI Tutor</div>
    <div class="hero-subtitle">Explore quantum computing through conversation</div>
    <div class="online">● AI TUTOR ONLINE</div>
</div>
""",
    unsafe_allow_html=True
)


# ============================================================
# DISPLAY CHAT HISTORY FROM SUPABASE
# ============================================================

if st.session_state.current_session_id:
    chat_history = get_chat_history(st.session_state.current_session_id)

    for msg in chat_history:
        role = "user" if msg["sender"] == "user" else "assistant"
        with st.chat_message(role):
            st.markdown(msg["content"])


# ============================================================
# DYNAMIC CHAT INPUT & AI GENERATION
# ============================================================

question = st.chat_input("Ask anything about quantum computing, programming, or general topics...")

if question:

    # Display user input immediately
    with st.chat_message("user"):
        st.markdown(question)

    # Process answer via RAG Engine
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            answer = answer_question(
                query=question,
                session_id=st.session_state.current_session_id,
                user_id=st.session_state.user_id
            )
            st.markdown(answer)

    st.rerun()
