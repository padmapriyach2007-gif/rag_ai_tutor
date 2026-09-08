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
# CUSTOM DESIGN
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
       MAIN HEADER
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

        background: rgba(
            80,
            220,
            160,
            0.08
        );

        border: 1px solid rgba(
            80,
            220,
            160,
            0.25
        );

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

        border: 1px solid rgba(
            140,
            120,
            255,
            0.20
        );

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
        background: rgba(
            20,
            20,
            45,
            0.85
        );

        border: 1px solid rgba(
            140,
            120,
            255,
            0.25
        );

        border-radius: 16px;
        color: white;
    }


    /* =====================================================
       BUTTONS
    ===================================================== */

    .stButton > button {
        border-radius: 12px;

        border: 1px solid rgba(
            140,
            120,
            255,
            0.25
        );

        background: rgba(
            45,
            40,
            85,
            0.55
        );

        color: #eeeeff;
        transition: all 0.2s ease;
    }

    .stButton > button:hover {
        border-color: rgba(
            160,
            140,
            255,
            0.65
        );

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

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "user_id" not in st.session_state:
    st.session_state.user_id = None

if "user_email" not in st.session_state:
    st.session_state.user_email = None

if "session_id" not in st.session_state:
    st.session_state.session_id = None

if "messages" not in st.session_state:
    st.session_state.messages = []

if "sessions" not in st.session_state:
    st.session_state.sessions = []


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
                Sign in to access your personal learning space
            </div>

        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="glow-line"></div>',
        unsafe_allow_html=True
    )

    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:

        st.markdown(
            """
            <div class="welcome-card">

                <div class="welcome-title">
                    🔐 Welcome Back
                </div>

                <div class="welcome-text">
                    Enter your email to access your AI Tutor
                    conversations and continue learning.
                </div>

            </div>
            """,
            unsafe_allow_html=True
        )

        email = st.text_input(
            "Email",
            placeholder="student@example.com"
        )

        if st.button(
            "🚀 Enter Quantum Lab",
            use_container_width=True
        ):

            if not email.strip():

                st.error(
                    "Please enter your email."
                )

            else:

                try:

                    clean_email = email.strip().lower()

                    # Get existing user or create new user
                    user_id = get_or_create_user(
                        email=clean_email,
                        role="student"
                    )

                    st.session_state.logged_in = True
                    st.session_state.user_id = user_id
                    st.session_state.user_email = clean_email

                    # -------------------------------------------------
                    # LOAD USER'S PREVIOUS CHAT SESSIONS
                    # -------------------------------------------------

                    sessions = get_user_sessions(user_id)

                    st.session_state.sessions = sessions

                    # -------------------------------------------------
                    # RESTORE LATEST CHAT
                    # -------------------------------------------------

                    if sessions:

                        latest_session = sessions[0]

                        latest_session_id = latest_session[
                            "session_id"
                        ]

                        st.session_state.session_id = (
                            latest_session_id
                        )

                        history = restore_chat(
                            latest_session_id,
                            user_id
                        )

                        st.session_state.messages = [
                            {
                                "role": (
                                    "user"
                                    if msg["sender"] == "user"
                                    else "assistant"
                                ),
                                "content": msg["content"]
                            }
                            for msg in history
                        ]

                    # -------------------------------------------------
                    # CREATE FIRST CHAT
                    # -------------------------------------------------

                    else:

                        new_session_id = create_chat_session(
                            user_id,
                            "Quantum Learning"
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
        unsafe_allow_html=True
    )


    # =====================================================
    # CURRENT USER
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
        unsafe_allow_html=True
    )


    # =====================================================
    # NEW CHAT
    # =====================================================

    if st.button(
        "➕ New Chat",
        use_container_width=True
    ):

        try:

            new_session_id = create_chat_session(
                st.session_state.user_id,
                "New Quantum Chat"
            )

            st.session_state.session_id = (
                new_session_id
            )

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

    sessions = get_user_sessions(
        st.session_state.user_id
    )

    st.session_state.sessions = sessions

    if sessions:

        for session in sessions:

            session_title = session.get(
                "title",
                "Untitled Chat"
            )

            session_id = session["session_id"]

            if st.button(
                f"💬 {session_title}",
                key=f"chat_{session_id}",
                use_container_width=True
            ):

                try:

                    history = restore_chat(
                        session_id,
                        st.session_state.user_id
                    )

                    st.session_state.session_id = (
                        session_id
                    )

                    st.session_state.messages = [
                        {
                            "role": (
                                "user"
                                if msg["sender"] == "user"
                                else "assistant"
                            ),
                            "content": msg["content"]
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
        use_container_width=True
    ):

        current_session_id = (
            st.session_state.session_id
        )

        if current_session_id:

            try:

                delete_chat(
                    current_session_id,
                    st.session_state.user_id
                )

                sessions = get_user_sessions(
                    st.session_state.user_id
                )

                st.session_state.sessions = sessions

                # ---------------------------------------------
                # Open another existing chat
                # ---------------------------------------------

                if sessions:

                    next_session_id = sessions[0][
                        "session_id"
                    ]

                    history = restore_chat(
                        next_session_id,
                        st.session_state.user_id
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
                            "content": msg["content"]
                        }
                        for msg in history
                    ]

                # ---------------------------------------------
                # No chats left -> create new chat
                # ---------------------------------------------

                else:

                    new_session_id = create_chat_session(
                        st.session_state.user_id,
                        "Quantum Learning"
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
    # CLEAR CURRENT CONVERSATION
    # =====================================================

    if st.button(
        "🧹 Clear Conversation",
        use_container_width=True
    ):

        # Clears only the displayed conversation.
        # Database history remains available.

        st.session_state.messages = []

        st.rerun()


    # =====================================================
    # LOGOUT
    # =====================================================

    if st.button(
        "🚪 Logout",
        use_container_width=True
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
                🧠 Learning Mode
            </div>

            <div class="side-card-text">
                Ask questions about quantum computing,
                Qiskit, qubits, algorithms, circuits,
                programming, mathematics, or physics.
            </div>

        </div>


        <div class="side-card">

            <div class="side-card-title">
                📚 RAG Knowledge Base
            </div>

            <div class="side-card-text">
                Your Quantum/Qiskit study material is
                retrieved when relevant.
            </div>

        </div>


        <div class="side-card">

            <div class="side-card-title">
                🌐 Web Search
            </div>

            <div class="side-card-text">
                Current and external information can be
                searched when necessary.
            </div>

        </div>


        <div class="side-card">

            <div class="side-card-title">
                💾 Chat Restoration
            </div>

            <div class="side-card-text">
                Your conversations are stored so you can
                return to previous learning sessions.
            </div>

        </div>
        """,
        unsafe_allow_html=True
    )


# =========================================================
# HERO
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
            Explore quantum computing through conversation
        </div>

        <div class="status-pill">
            ● AI TUTOR ONLINE
        </div>

    </div>

    <div class="glow-line"></div>
    """,
    unsafe_allow_html=True
)


# =========================================================
# WELCOME SCREEN
# =========================================================

if not st.session_state.messages:

    st.markdown(
        """
        <div class="welcome-card">

            <div class="welcome-title">
                👋 Welcome to your Quantum Learning Space
            </div>

            <div class="welcome-text">
                I'm your AI tutor. Ask me to explain a concept,
                simplify a difficult topic, explore an algorithm,
                or help you understand quantum computing
                step by step.
            </div>

        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown("### 💡 Try asking")

    col1, col2 = st.columns(2)

    with col1:

        if st.button(
            "⚛️ What is a qubit?",
            use_container_width=True
        ):

            st.session_state.pending_question = (
                "What is a qubit?"
            )

            st.rerun()

        if st.button(
            "🌌 Explain quantum superposition",
            use_container_width=True
        ):

            st.session_state.pending_question = (
                "Explain quantum superposition"
            )

            st.rerun()

    with col2:

        if st.button(
            "🔗 What is quantum entanglement?",
            use_container_width=True
        ):

            st.session_state.pending_question = (
                "What is quantum entanglement?"
            )

            st.rerun()

        if st.button(
            "🐣 Explain quantum computing like I'm a beginner",
            use_container_width=True
        ):

            st.session_state.pending_question = (
                "Explain quantum computing like I'm a beginner"
            )

            st.rerun()


# =========================================================
# DISPLAY CHAT HISTORY
# =========================================================

for message in st.session_state.messages:

    with st.chat_message(
        message["role"],
        avatar=(
            "👩‍💻"
            if message["role"] == "user"
            else "⚛️"
        )
    ):

        st.markdown(
            message["content"]
        )


# =========================================================
# CHAT INPUT
# =========================================================

prompt = st.chat_input(
    "Ask anything about quantum computing..."
)


# =========================================================
# HANDLE EXAMPLE BUTTON
# =========================================================

if "pending_question" in st.session_state:

    prompt = st.session_state.pending_question

    del st.session_state.pending_question


# =========================================================
# PROCESS QUESTION
# =========================================================

if prompt:

    # -----------------------------------------------------
    # Make sure a chat session exists
    # -----------------------------------------------------

    if not st.session_state.session_id:

        try:

            st.session_state.session_id = (
                create_chat_session(
                    st.session_state.user_id,
                    "Quantum Learning"
                )
            )

        except Exception as e:

            st.error(
                f"Could not create chat session: {str(e)}"
            )

            st.stop()


    # -----------------------------------------------------
    # Display user message
    # -----------------------------------------------------

    st.session_state.messages.append(
        {
            "role": "user",
            "content": prompt
        }
    )

    with st.chat_message(
        "user",
        avatar="👩‍💻"
    ):

        st.markdown(
            prompt
        )


    # -----------------------------------------------------
    # Generate AI response
    # -----------------------------------------------------

    with st.chat_message(
        "assistant",
        avatar="⚛️"
    ):

        with st.spinner(
            "🧠 Thinking..."
        ):

            try:

                response = answer_question(
                    query=prompt,
                    session_id=(
                        st.session_state.session_id
                    ),
                    user_id=(
                        st.session_state.user_id
                    )
                )

            except Exception as e:

                response = (
                    "⚠️ I couldn't process that "
                    "question right now.\n\n"
                    f"**Error:** `{str(e)}`"
                )

        st.markdown(
            response
        )


    # -----------------------------------------------------
    # Store assistant message locally
    # -----------------------------------------------------

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": response
        }
    )


    # -----------------------------------------------------
    # Refresh session list
    # -----------------------------------------------------

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

        ⚛️ Powered by RAG + AI + Supabase
        <br>
        Built for interactive quantum learning

    </div>
    """,
    unsafe_allow_html=True
)
