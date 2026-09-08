import streamlit as st

from rag_engine import (
    answer_question,
    get_or_create_user,
    create_chat_session,
    get_user_sessions,
    restore_chat,
    delete_chat,
)


# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="Quantum Lab | AI Tutor",
    page_icon="⚛️",
    layout="wide",
    initial_sidebar_state="expanded",
)


# =========================================================
# CUSTOM CSS
# =========================================================

st.markdown(
    """
    <style>

    /* =====================================================
       GLOBAL
    ===================================================== */

    .stApp {
        background:
            radial-gradient(
                circle at 10% 10%,
                rgba(110, 80, 255, 0.18),
                transparent 28%
            ),
            radial-gradient(
                circle at 90% 20%,
                rgba(0, 200, 255, 0.12),
                transparent 30%
            ),
            linear-gradient(
                135deg,
                #070714 0%,
                #0b0b1f 50%,
                #080817 100%
            );

        color: #f5f5ff;
    }

    [data-testid="stHeader"] {
        background: transparent;
    }

    /* =====================================================
       SIDEBAR
    ===================================================== */

    [data-testid="stSidebar"] {
        background: rgba(8, 8, 24, 0.96);
        border-right: 1px solid rgba(150, 120, 255, 0.18);
    }

    .sidebar-brand {
        text-align: center;
        padding: 10px 5px 25px 5px;
    }

    .sidebar-logo {
        font-size: 48px;
        margin-bottom: 5px;
    }

    .sidebar-title {
        font-size: 22px;
        font-weight: 800;
        letter-spacing: 1px;
    }

    .sidebar-subtitle {
        color: #9999bb;
        font-size: 13px;
        margin-top: 5px;
    }

    /* =====================================================
       USER CARD
    ===================================================== */

    .user-card {
        background: linear-gradient(
            145deg,
            rgba(100, 80, 220, 0.20),
            rgba(20, 20, 55, 0.55)
        );

        border: 1px solid rgba(130, 110, 255, 0.25);
        border-radius: 15px;
        padding: 14px;
        margin: 10px 0 18px 0;
    }

    .user-title {
        font-weight: 700;
        font-size: 14px;
        margin-bottom: 5px;
    }

    .user-email {
        color: #aaaac4;
        font-size: 12px;
        word-break: break-word;
    }

    /* =====================================================
       SIDE CARDS
    ===================================================== */

    .side-card {
        background: linear-gradient(
            145deg,
            rgba(100, 80, 220, 0.15),
            rgba(20, 20, 55, 0.45)
        );

        border: 1px solid rgba(130, 110, 255, 0.22);
        border-radius: 15px;
        padding: 15px;
        margin: 12px 0;
    }

    .side-card-title {
        font-weight: 700;
        margin-bottom: 7px;
    }

    .side-card-text {
        color: #aaaac4;
        font-size: 13px;
        line-height: 1.5;
    }

    /* =====================================================
       MAIN HERO
    ===================================================== */

    .hero {
        text-align: center;
        padding: 35px 15px 20px 15px;
    }

    .quantum-symbol {
        font-size: 58px;
        line-height: 1;
        margin-bottom: 12px;

        filter:
            drop-shadow(
                0 0 18px
                rgba(120, 100, 255, 0.7)
            );
    }

    .hero-title {
        font-size: clamp(32px, 5vw, 54px);
        font-weight: 850;
        letter-spacing: -1px;

        background:
            linear-gradient(
                90deg,
                #ffffff,
                #b9b1ff,
                #8be9ff
            );

        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }

    .hero-subtitle {
        color: #a9a9c4;
        font-size: 16px;
        margin-top: 10px;
    }

    .status-pill {
        display: inline-block;
        margin-top: 18px;
        padding: 7px 15px;
        border-radius: 30px;

        background: rgba(80, 220, 160, 0.08);

        border: 1px solid rgba(80, 220, 160, 0.25);

        color: #8ff0bd;
        font-size: 12px;
        font-weight: 600;
    }

    /* =====================================================
       WELCOME CARD
    ===================================================== */

    .welcome-card {
        max-width: 850px;
        margin: 20px auto 25px auto;
        padding: 28px;
        border-radius: 22px;

        background: linear-gradient(
            145deg,
            rgba(40, 35, 85, 0.65),
            rgba(15, 15, 38, 0.78)
        );

        border: 1px solid rgba(140, 120, 255, 0.20);

        box-shadow:
            0 20px 60px
            rgba(0, 0, 0, 0.25);
    }

    .welcome-title {
        font-size: 23px;
        font-weight: 750;
        margin-bottom: 8px;
    }

    .welcome-text {
        color: #b4b4cc;
        line-height: 1.6;
        font-size: 14px;
    }

    /* =====================================================
       CHAT
    ===================================================== */

    [data-testid="stChatMessage"] {
        border-radius: 18px;
        padding: 5px 10px;
        margin-bottom: 8px;
    }

    [data-testid="stChatMessageContent"] {
        font-size: 15px;
        line-height: 1.65;
    }

    /* =====================================================
       CHAT INPUT
    ===================================================== */

    [data-testid="stChatInput"] {
        border-radius: 18px;
    }

    [data-testid="stChatInput"] textarea {
        background: rgba(20, 20, 45, 0.85);

        border: 1px solid rgba(140, 120, 255, 0.25);

        border-radius: 16px;
        color: white;
    }

    /* =====================================================
       BUTTONS
    ===================================================== */

    .stButton > button {
        border-radius: 12px;

        border: 1px solid rgba(140, 120, 255, 0.25);

        background: rgba(45, 40, 85, 0.55);

        color: #eeeeff;
        transition: all 0.2s ease;
    }

    .stButton > button:hover {
        border-color: rgba(160, 140, 255, 0.65);
        transform: translateY(-1px);
    }

    /* =====================================================
       DIVIDER
    ===================================================== */

    .glow-line {
        height: 1px;
        width: 100%;
        margin: 15px 0 25px 0;

        background: linear-gradient(
            90deg,
            transparent,
            rgba(140, 120, 255, 0.5),
            rgba(80, 210, 255, 0.5),
            transparent
        );
    }

    /* =====================================================
       FOOTER
    ===================================================== */

    .footer {
        text-align: center;
        color: #666681;
        font-size: 11px;
        margin-top: 35px;
        padding-bottom: 15px;
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# SESSION STATE
# =========================================================

defaults = {
    "logged_in": False,
    "user_id": None,
    "user_email": None,
    "session_id": None,
    "messages": [],
    "sessions": [],
}

for key, value in defaults.items():

    if key not in st.session_state:
        st.session_state[key] = value


# =========================================================
# LOGIN SCREEN
# =========================================================

if not st.session_state.logged_in:

    st.markdown(
        """
        <div class="hero">

            <div class="quantum-symbol">
                ⚛️
            </div>

            <div class="hero-title">
                Quantum AI Tutor
            </div>

            <div class="hero-subtitle">
                Your intelligent learning assistant
            </div>

        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="glow-line"></div>',
        unsafe_allow_html=True,
    )

    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:

        st.markdown(
            """
            <div class="welcome-card">

                <div class="welcome-title">
                    🔐 Welcome
                </div>

                <div class="welcome-text">
                    Enter your email to access your personal
                    AI Tutor and restore your previous chats.
                </div>

            </div>
            """,
            unsafe_allow_html=True,
        )

        email = st.text_input(
            "Email",
            placeholder="student@example.com",
        )

        if st.button(
            "🚀 Enter Quantum Lab",
            use_container_width=True,
        ):

            if not email.strip():

                st.error("Please enter your email.")

            else:

                try:

                    clean_email = email.strip().lower()

                    # =================================================
                    # GET OR CREATE USER
                    # =================================================

                    user_id = get_or_create_user(
                        email=clean_email,
                        role="student",
                    )

                    st.session_state.logged_in = True
                    st.session_state.user_id = user_id
                    st.session_state.user_email = clean_email

                    # =================================================
                    # LOAD PREVIOUS CHATS
                    # =================================================

                    sessions = get_user_sessions(user_id)

                    st.session_state.sessions = sessions

                    # =================================================
                    # RESTORE LATEST CHAT
                    # =================================================

                    if sessions:

                        latest_session = sessions[0]

                        latest_session_id = latest_session[
                            "session_id"
                        ]

                        history = restore_chat(
                            latest_session_id,
                            user_id,
                        )

                        st.session_state.session_id = (
                            latest_session_id
                        )

                        st.session_state.messages = [
                            {
                                "role": (
                                    "user"
                                    if msg["sender"] == "user"
                                    else "assistant"
                                ),
                                "content": msg["content"],
                            }
                            for msg in history
                        ]

                    # =================================================
                    # FIRST LOGIN
                    # =================================================

                    else:

                        new_session_id = create_chat_session(
                            user_id,
                            "Quantum Learning",
                        )

                        st.session_state.session_id = (
                            new_session_id
                        )

                        st.session_state.messages = []

                        st.session_state.sessions = (
                            get_user_sessions(user_id)
                        )

                    st.rerun()

                except Exception as e:

                    st.error(
                        f"Login error: {str(e)}"
                    )

    st.stop()


# =========================================================
# SIDEBAR
# =========================================================

with st.sidebar:

    # =====================================================
    # BRAND
    # =====================================================

    st.markdown(
        """
        <div class="sidebar-brand">

            <div class="sidebar-logo">
                ⚛️
            </div>

            <div class="sidebar-title">
                QUANTUM LAB
            </div>

            <div class="sidebar-subtitle">
                AI-Powered Learning Space
            </div>

        </div>
        """,
        unsafe_allow_html=True,
    )

    # =====================================================
    # USER
    # =====================================================

    st.markdown(
        f"""
        <div class="user-card">

            <div class="user-title">
                👤 Logged In
            </div>

            <div class="user-email">
                {st.session_state.user_email}
            </div>

        </div>
        """,
        unsafe_allow_html=True,
    )

    # =====================================================
    # NEW CHAT
    # =====================================================

    if st.button(
        "➕ New Chat",
        use_container_width=True,
    ):

        try:

            new_session_id = create_chat_session(
                st.session_state.user_id,
                "New Quantum Chat",
            )

            st.session_state.session_id = new_session_id
            st.session_state.messages = []

            st.session_state.sessions = (
                get_user_sessions(
                    st.session_state.user_id
                )
            )

            st.rerun()

        except Exception as e:

            st.error(
                f"Could not create chat: {str(e)}"
            )

    # =====================================================
    # PREVIOUS CHATS
    # =====================================================

    st.markdown("### 💬 Your Chats")

    try:

        sessions = get_user_sessions(
            st.session_state.user_id
        )

        st.session_state.sessions = sessions

    except Exception as e:

        sessions = []

        st.error(
            f"Could not load chats: {str(e)}"
        )

    if sessions:

        for session in sessions:

            session_id = session["session_id"]

            session_title = session.get(
                "title",
                "Untitled Chat",
            )

            if st.button(
                f"💬 {session_title}",
                key=f"chat_{session_id}",
                use_container_width=True,
            ):

                try:

                    history = restore_chat(
                        session_id,
                        st.session_state.user_id,
                    )

                    st.session_state.session_id = session_id

                    st.session_state.messages = [
                        {
                            "role": (
                                "user"
                                if msg["sender"] == "user"
                                else "assistant"
                            ),
                            "content": msg["content"],
                        }
                        for msg in history
                    ]

                    st.rerun()

                except Exception as e:

                    st.error(
                        f"Could not restore chat: {str(e)}"
                    )

    else:

        st.caption(
            "No previous chats yet."
        )

    # =====================================================
    # DELETE CURRENT CHAT
    # =====================================================

    st.markdown("---")

    if st.button(
        "🗑️ Delete Current Chat",
        use_container_width=True,
    ):

        current_session_id = (
            st.session_state.session_id
        )

        if current_session_id:

            try:

                delete_chat(
                    current_session_id,
                    st.session_state.user_id,
                )

                sessions = get_user_sessions(
                    st.session_state.user_id
                )

                st.session_state.sessions = sessions

                # =============================================
                # OPEN ANOTHER CHAT
                # =============================================

                if sessions:

                    next_session_id = sessions[0][
                        "session_id"
                    ]

                    history = restore_chat(
                        next_session_id,
                        st.session_state.user_id,
                    )

                    st.session_state.session_id = (
                        next_session_id
                    )

                    st.session_state.messages = [
                        {
                            "role": (
                                "user"
                                if msg["sender"] == "user"
                                else "assistant"
                            ),
                            "content": msg["content"],
                        }
                        for msg in history
                    ]

                # =============================================
                # CREATE NEW CHAT
                # =============================================

                else:

                    new_session_id = create_chat_session(
                        st.session_state.user_id,
                        "Quantum Learning",
                    )

                    st.session_state.session_id = (
                        new_session_id
                    )

                    st.session_state.messages = []

                st.rerun()

            except Exception as e:

                st.error(
                    f"Delete error: {str(e)}"
                )

    # =====================================================
    # CLEAR DISPLAYED CONVERSATION
    # =====================================================

    if st.button(
        "🧹 Clear Conversation",
        use_container_width=True,
    ):

        # Only clears Streamlit display.
        # Database messages remain saved.

        st.session_state.messages = []

        st.rerun()

    # =====================================================
    # LOGOUT
    # =====================================================

    if st.button(
        "🚪 Logout",
        use_container_width=True,
    ):

        st.session_state.logged_in = False
        st.session_state.user_id = None
        st.session_state.user_email = None
        st.session_state.session_id = None
        st.session_state.messages = []
        st.session_state.sessions = []

        st.rerun()

    # =====================================================
    # INFORMATION
    # =====================================================

    st.markdown(
        """
        <div class="side-card">

            <div class="side-card-title">
                🧠 AI Tutor
            </div>

            <div class="side-card-text">
                Ask questions about quantum computing,
                programming, mathematics, physics,
                algorithms, Qiskit, or general topics.
            </div>

        </div>

        <div class="side-card">

            <div class="side-card-title">
                💾 Chat Restoration
            </div>

            <div class="side-card-text">
                Your conversations are stored in
                Supabase and can be restored later.
            </div>

        </div>

        <div class="side-card">

            <div class="side-card-title">
                👥 Multi-User Support
            </div>

            <div class="side-card-text">
                Each email is associated with its own
                user account and chat sessions.
            </div>

        </div>

        <div class="side-card">

            <div class="side-card-title">
                🌐 Web Search
            </div>

            <div class="side-card-text">
                Current and external information can
                be searched when required.
            </div>

        </div>
        """,
        unsafe_allow_html=True,
    )


# =========================================================
# MAIN HERO
# =========================================================

st.markdown(
    """
    <div class="hero">

        <div class="quantum-symbol">
            ⚛️
        </div>

        <div class="hero-title">
            Quantum AI Tutor
        </div>

        <div class="hero-subtitle">
            Ask questions and learn through conversation
        </div>

        <div class="status-pill">
            ● AI TUTOR ONLINE
        </div>

    </div>

    <div class="glow-line"></div>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# WELCOME SCREEN
# =========================================================

if not st.session_state.messages:

    st.markdown(
        """
        <div class="welcome-card">

            <div class="welcome-title">
                👋 Welcome to your AI Learning Space
            </div>

            <div class="welcome-text">
                Ask me anything. I can explain concepts,
                solve programming problems, help with
                mathematics and physics, explain quantum
                computing, or provide general knowledge.
            </div>

        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("### 💡 Try asking")

    col1, col2 = st.columns(2)

    with col1:

        if st.button(
            "⚛️ What is a qubit?",
            use_container_width=True,
        ):

            st.session_state.pending_question = (
                "What is a qubit?"
            )

            st.rerun()

        if st.button(
            "💻 Explain Python loops",
            use_container_width=True,
        ):

            st.session_state.pending_question = (
                "Explain Python loops with examples"
            )

            st.rerun()

    with col2:

        if st.button(
            "🧮 Explain recursion",
            use_container_width=True,
        ):

            st.session_state.pending_question = (
                "Explain recursion in programming"
            )

            st.rerun()

        if st.button(
            "🌐 What is artificial intelligence?",
            use_container_width=True,
        ):

            st.session_state.pending_question = (
                "What is artificial intelligence?"
            )

            st.rerun()


# =========================================================
# DISPLAY EXISTING CHAT
# =========================================================

for message in st.session_state.messages:

    with st.chat_message(
        message["role"],
        avatar=(
            "👩‍💻"
            if message["role"] == "user"
            else "⚛️"
        ),
    ):

        st.markdown(
            message["content"],
            unsafe_allow_html=True,
        )


# =========================================================
# CHAT INPUT
# =========================================================

prompt = st.chat_input(
    "Ask anything..."
)


# =========================================================
# EXAMPLE QUESTION
# =========================================================

if "pending_question" in st.session_state:

    prompt = st.session_state.pending_question

    del st.session_state.pending_question


# =========================================================
# PROCESS QUESTION
# =========================================================

if prompt:

    # =====================================================
    # MAKE SURE SESSION EXISTS
    # =====================================================

    if not st.session_state.session_id:

        try:

            st.session_state.session_id = (
                create_chat_session(
                    st.session_state.user_id,
                    "Quantum Learning",
                )
            )

        except Exception as e:

            st.error(
                f"Could not create chat session: {str(e)}"
            )

            st.stop()

    # =====================================================
    # DISPLAY USER QUESTION
    # =====================================================

    st.session_state.messages.append(
        {
            "role": "user",
            "content": prompt,
        }
    )

    with st.chat_message(
        "user",
        avatar="👩‍💻",
    ):

        st.markdown(prompt, unsafe_allow_html=True)

    # =====================================================
    # GENERATE AI RESPONSE
    # =====================================================

    with st.chat_message(
        "assistant",
        avatar="⚛️",
    ):

        with st.spinner("🧠 Thinking..."):

            try:

                response = answer_question(
                    query=prompt,
                    session_id=(
                        st.session_state.session_id
                    ),
                    user_id=(
                        st.session_state.user_id
                    ),
                )

            except Exception as e:

                response = (
                    "⚠️ I couldn't process that question.\n\n"
                    f"**Error:** `{str(e)}`"
                )

        st.markdown(response, unsafe_allow_html=True)

    # =====================================================
    # SAVE RESPONSE IN LOCAL SESSION
    # =====================================================

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": response,
        }
    )

    # =====================================================
    # REFRESH CHAT LIST
    # =====================================================

    try:

        st.session_state.sessions = (
            get_user_sessions(
                st.session_state.user_id
            )
        )

    except Exception:
        pass


# =========================================================
# FOOTER
# =========================================================

st.markdown(
    """
    <div class="footer">

        ⚛️ Powered by AI + RAG + Supabase
        <br>
        Built for interactive learning

    </div>
    """,
    unsafe_allow_html=True,
)
