import streamlit as st

from rag_engine import (
    answer_question,
    get_or_create_user,
    create_chat_session,
    get_user_sessions,
    restore_chat,
    rename_chat,
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
# SESSION STATE
# =========================================================

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "user_email" not in st.session_state:
    st.session_state.user_email = ""

if "user_id" not in st.session_state:
    st.session_state.user_id = None

if "session_id" not in st.session_state:
    st.session_state.session_id = None

if "messages" not in st.session_state:
    st.session_state.messages = []

if "sessions" not in st.session_state:
    st.session_state.sessions = []


# =========================================================
# FRONTEND CSS ONLY
# =========================================================

st.markdown(
    """
    <style>

    /* =====================================================
       GLOBAL BACKGROUND
       ===================================================== */

    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Space+Grotesk:wght@500;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    .stApp {
        background:
            radial-gradient(
                circle at 10% 10%,
                rgba(99, 102, 241, 0.20),
                transparent 28%
            ),
            radial-gradient(
                circle at 90% 15%,
                rgba(6, 182, 212, 0.13),
                transparent 25%
            ),
            radial-gradient(
                circle at 70% 90%,
                rgba(139, 92, 246, 0.12),
                transparent 30%
            ),
            linear-gradient(
                135deg,
                #030712 0%,
                #080d24 45%,
                #020617 100%
            );
    }

    .main .block-container {
        max-width: 1250px;
        padding-top: 2rem;
        padding-bottom: 6rem;
    }


    /* =====================================================
       QUANTUM GRID
       ===================================================== */

    .stApp::before {
        content: "";
        position: fixed;
        inset: 0;
        pointer-events: none;

        background-image:
            linear-gradient(
                rgba(148,163,184,0.025) 1px,
                transparent 1px
            ),
            linear-gradient(
                90deg,
                rgba(148,163,184,0.025) 1px,
                transparent 1px
            );

        background-size: 55px 55px;
        z-index: 0;
    }


    /* =====================================================
       SIDEBAR
       ===================================================== */

    section[data-testid="stSidebar"] {
        background:
            linear-gradient(
                180deg,
                #050816 0%,
                #070b1d 100%
            );

        border-right: 1px solid rgba(139, 92, 246, 0.18);
    }

    section[data-testid="stSidebar"] > div {
        padding-top: 1rem;
    }

    section[data-testid="stSidebar"] .stButton button {
        background:
            linear-gradient(
                135deg,
                rgba(20, 26, 55, 0.95),
                rgba(10, 15, 35, 0.95)
            );

        border: 1px solid rgba(139, 92, 246, 0.18);
        border-radius: 12px;

        color: #dbeafe;

        transition: all 0.2s ease;
    }

    section[data-testid="stSidebar"] .stButton button:hover {
        border-color: rgba(139, 92, 246, 0.60);

        background:
            linear-gradient(
                135deg,
                rgba(35, 29, 76, 0.98),
                rgba(15, 23, 50, 0.98)
            );

        transform: translateY(-1px);

        box-shadow:
            0 8px 25px rgba(0, 0, 0, 0.30),
            0 0 20px rgba(139, 92, 246, 0.12);
    }

    section[data-testid="stSidebar"] .stTextInput input {
        background: #090f24;
        border: 1px solid rgba(139, 92, 246, 0.20);
        border-radius: 10px;
        color: white;
    }


    /* =====================================================
       SIDEBAR BRAND
       ===================================================== */

    .sidebar-brand {
        text-align: center;
        padding: 8px 0 15px 0;
    }

    .sidebar-icon {
        font-size: 55px;
        line-height: 1;

        text-shadow:
            0 0 8px rgba(167,139,250,0.90),
            0 0 20px rgba(99,102,241,0.70),
            0 0 40px rgba(59,130,246,0.40);

        animation: quantumGlow 3s ease-in-out infinite;
    }

    @keyframes quantumGlow {
        0%, 100% {
            transform: scale(1);
            filter: brightness(1);
        }

        50% {
            transform: scale(1.08);
            filter: brightness(1.25);
        }
    }

    .sidebar-title {
        font-family: 'Space Grotesk', sans-serif;
        font-size: 20px;
        font-weight: 700;

        letter-spacing: 4px;

        color: #f8fafc;

        margin-top: 8px;
    }

    .sidebar-subtitle {
        color: #7180a5;
        font-size: 9px;

        letter-spacing: 2px;
        text-transform: uppercase;

        margin-top: 4px;
    }


    /* =====================================================
       USER CARD
       ===================================================== */

    .user-card {
        padding: 11px 13px;

        margin: 5px 0 20px 0;

        border-radius: 12px;

        background:
            linear-gradient(
                135deg,
                rgba(20,27,57,0.90),
                rgba(9,14,33,0.90)
            );

        border: 1px solid rgba(139,92,246,0.15);

        color: #cbd5e1;

        font-size: 12px;

        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
    }

    .online-dot {
        display: inline-block;

        width: 7px;
        height: 7px;

        margin-right: 7px;

        border-radius: 50%;

        background: #22c55e;

        box-shadow:
            0 0 8px rgba(34,197,94,0.9);
    }


    /* =====================================================
       SIDEBAR LABELS
       ===================================================== */

    .sidebar-label {
        color: #64748b;

        font-size: 9px;
        font-weight: 700;

        letter-spacing: 2px;

        text-transform: uppercase;

        margin-top: 12px;
        margin-bottom: 8px;
    }


    /* =====================================================
       MAIN QUANTUM ICON
       ===================================================== */

    .main-icon {
        text-align: center;

        font-size: 72px;

        line-height: 1;

        margin-top: 5px;
        margin-bottom: 8px;

        text-shadow:
            0 0 8px rgba(255,255,255,0.80),
            0 0 20px rgba(139,92,246,0.90),
            0 0 45px rgba(99,102,241,0.65),
            0 0 80px rgba(59,130,246,0.35);

        animation: quantumGlow 3s ease-in-out infinite;
    }


    /* =====================================================
       HERO TITLE
       ===================================================== */

    .hero-title {
        text-align: center;

        font-family: 'Space Grotesk', sans-serif;

        font-size: clamp(32px, 5vw, 56px);

        font-weight: 700;

        letter-spacing: 5px;

        background:
            linear-gradient(
                90deg,
                #ffffff,
                #c4b5fd,
                #93c5fd,
                #ffffff
            );

        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;

        margin-top: 4px;
    }

    .hero-subtitle {
        text-align: center;

        max-width: 700px;

        margin: 14px auto 20px auto;

        color: #94a3b8;

        font-size: 14px;

        line-height: 1.8;
    }


    /* =====================================================
       ONLINE STATUS
       ===================================================== */

    .hero-online {
        width: fit-content;

        margin: 0 auto 25px auto;

        padding: 7px 14px;

        border-radius: 999px;

        background: rgba(34,197,94,0.06);

        border: 1px solid rgba(34,197,94,0.18);

        color: #86efac;

        font-size: 10px;

        font-weight: 600;

        letter-spacing: 1.7px;

        text-transform: uppercase;
    }


    /* =====================================================
       HERO SEPARATOR
       ===================================================== */

    .quantum-line {
        width: 200px;

        height: 1px;

        margin: 0 auto 28px auto;

        background:
            linear-gradient(
                90deg,
                transparent,
                rgba(139,92,246,0.70),
                rgba(59,130,246,0.70),
                transparent
            );
    }


    /* =====================================================
       CHAT MESSAGES
       ===================================================== */

    [data-testid="stChatMessage"] {
        border-radius: 16px;

        border: 1px solid rgba(139,92,246,0.10);

        background:
            linear-gradient(
                135deg,
                rgba(17,24,45,0.80),
                rgba(7,12,28,0.80)
            );

        margin-bottom: 10px;

        transition: all 0.2s ease;
    }

    [data-testid="stChatMessage"]:hover {
        border-color: rgba(139,92,246,0.25);
    }

    [data-testid="stChatMessage"] p {
        color: #dbe4f0;
        line-height: 1.7;
    }


    /* =====================================================
       CHAT INPUT
       ===================================================== */

    [data-testid="stChatInput"] > div {
        background:
            linear-gradient(
                135deg,
                rgba(13,18,38,0.98),
                rgba(5,10,25,0.98)
            );

        border: 1px solid rgba(139,92,246,0.22);

        border-radius: 16px;

        box-shadow:
            0 15px 45px rgba(0,0,0,0.30);
    }

    [data-testid="stChatInput"] > div:focus-within {
        border-color: rgba(139,92,246,0.60);

        box-shadow:
            0 0 0 1px rgba(139,92,246,0.20),
            0 15px 50px rgba(0,0,0,0.35);
    }

    [data-testid="stChatInput"] textarea {
        color: #f8fafc !important;
    }

    [data-testid="stChatInput"] textarea::placeholder {
        color: #64748b !important;
    }


    /* =====================================================
       ALERTS
       ===================================================== */

    div[data-testid="stAlert"] {
        border-radius: 13px;
    }


    /* =====================================================
       DIVIDERS
       ===================================================== */

    hr {
        border-color: rgba(255,255,255,0.06);
    }


    /* =====================================================
       MOBILE
       ===================================================== */

    @media (max-width: 768px) {

        .hero-title {
            font-size: 31px;
            letter-spacing: 2px;
        }

        .hero-subtitle {
            font-size: 13px;
        }

        .main-icon {
            font-size: 60px;
        }
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# LOGIN PAGE
# =========================================================

if not st.session_state.logged_in:

    st.markdown(
        '<div class="main-icon">⚛️</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="hero-title">QUANTUM AI TUTOR</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="hero-subtitle">
            Explore quantum computing through an intelligent
            RAG-powered learning environment.
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="hero-online">
            <span class="online-dot"></span>
            AI TUTOR ONLINE
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.subheader("🔐 Login")

    email = st.text_input(
        "Enter your email",
        placeholder="student@example.com",
    )

    if st.button(
        "🚀 Start Learning",
        use_container_width=True,
    ):

        if not email.strip():

            st.error("Please enter your email.")

        else:

            try:

                user_id = get_or_create_user(
                    email.strip()
                )

                st.session_state.logged_in = True

                st.session_state.user_email = (
                    email.strip().lower()
                )

                st.session_state.user_id = user_id

                st.session_state.session_id = None

                st.session_state.messages = []

                st.rerun()

            except Exception as e:

                st.error(
                    f"Login failed: {str(e)}"
                )

    st.stop()


# =========================================================
# SIDEBAR
# =========================================================

with st.sidebar:

    st.markdown(
        """
        <div class="sidebar-brand">

            <div class="sidebar-icon">
                ⚛️
            </div>

            <div class="sidebar-title">
                QUANTUM LAB
            </div>

            <div class="sidebar-subtitle">
                AI Learning Environment
            </div>

        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        f"""
        <div class="user-card">
            <span class="online-dot"></span>
            {st.session_state.user_email}
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="sidebar-label">Workspace</div>',
        unsafe_allow_html=True,
    )

    # -----------------------------------------------------
    # NEW CHAT
    # -----------------------------------------------------

    if st.button(
        "＋  New Quantum Session",
        use_container_width=True,
    ):

        try:

            session_id = create_chat_session(
                st.session_state.user_id
            )

            st.session_state.session_id = session_id

            st.session_state.messages = []

            st.rerun()

        except Exception as e:

            st.error(
                f"Could not create chat: {str(e)}"
            )


    # -----------------------------------------------------
    # LOAD SESSIONS
    # -----------------------------------------------------

    try:

        st.session_state.sessions = get_user_sessions(
            st.session_state.user_id
        )

    except Exception as e:

        st.error(
            f"Could not load chats: {str(e)}"
        )


    # -----------------------------------------------------
    # SESSIONS
    # -----------------------------------------------------

    st.markdown(
        '<div class="sidebar-label">Your Sessions</div>',
        unsafe_allow_html=True,
    )

    for chat in st.session_state.sessions:

        session_id = chat["session_id"]

        title = chat.get(
            "title",
            "New Quantum Chat"
        )

        if st.button(
            f"◈  {title}",
            key=f"chat_{session_id}",
            use_container_width=True,
        ):

            try:

                history = restore_chat(
                    session_id,
                    st.session_state.user_id
                )

                st.session_state.session_id = session_id

                st.session_state.messages = []

                for message in history:

                    st.session_state.messages.append(
                        {
                            "role": (
                                "user"
                                if message["sender"] == "user"
                                else "assistant"
                            ),
                            "content": message["content"],
                        }
                    )

                st.rerun()

            except Exception as e:

                st.error(
                    f"Could not open chat: {str(e)}"
                )


    st.divider()


    # -----------------------------------------------------
    # CHAT SETTINGS
    # -----------------------------------------------------

    if st.session_state.session_id:

        st.markdown(
            '<div class="sidebar-label">Chat Settings</div>',
            unsafe_allow_html=True,
        )

        new_title = st.text_input(
            "Rename chat",
            placeholder="Enter new chat name",
        )

        if st.button(
            "✎  Rename Chat",
            use_container_width=True,
        ):

            if not new_title.strip():

                st.warning(
                    "Enter a chat name."
                )

            else:

                try:

                    rename_chat(
                        st.session_state.session_id,
                        st.session_state.user_id,
                        new_title,
                    )

                    st.success(
                        "Chat renamed."
                    )

                    st.rerun()

                except Exception as e:

                    st.error(
                        f"Rename failed: {str(e)}"
                    )


        if st.button(
            "🗑  Delete Chat",
            use_container_width=True,
        ):

            try:

                delete_chat(
                    st.session_state.session_id,
                    st.session_state.user_id,
                )

                st.session_state.session_id = None

                st.session_state.messages = []

                st.success(
                    "Chat deleted."
                )

                st.rerun()

            except Exception as e:

                st.error(
                    f"Delete failed: {str(e)}"
                )


    st.divider()


    # -----------------------------------------------------
    # LOGOUT
    # -----------------------------------------------------

    if st.button(
        "↪  Logout",
        use_container_width=True,
    ):

        st.session_state.logged_in = False

        st.session_state.user_email = ""

        st.session_state.user_id = None

        st.session_state.session_id = None

        st.session_state.messages = []

        st.rerun()


# =========================================================
# MAIN HEADER
# =========================================================

st.markdown(
    '<div class="main-icon">⚛️</div>',
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="hero-online"><span class="online-dot"></span> AI TUTOR ONLINE</div>',
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="hero-title">QUANTUM AI TUTOR</div>',
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="quantum-line"></div>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="hero-subtitle">
        Learn quantum computing and technical concepts
        through an intelligent RAG-powered learning environment.
    </div>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# REQUIRE CHAT
# =========================================================

if not st.session_state.session_id:

    st.info(
        "✨ Create a new quantum session from the sidebar to start learning."
    )

    st.stop()


# =========================================================
# DISPLAY CHAT HISTORY
# =========================================================

for message in st.session_state.messages:

    with st.chat_message(
        message["role"]
    ):

        st.markdown(
            message["content"]
        )


# =========================================================
# CHAT INPUT
# =========================================================

query = st.chat_input(
    "Ask your quantum question..."
)


# =========================================================
# PROCESS QUESTION
# =========================================================

if query:

    query = query.strip()

    if not query:
        st.stop()


    # -----------------------------------------------------
    # USER MESSAGE
    # -----------------------------------------------------

    st.session_state.messages.append(
        {
            "role": "user",
            "content": query,
        }
    )

    with st.chat_message("user"):

        st.markdown(query)


    # -----------------------------------------------------
    # RAG ANSWER
    # -----------------------------------------------------

    with st.chat_message("assistant"):

        with st.spinner(
            "🔎 Searching the quantum knowledge base..."
        ):

            try:

                answer = answer_question(
                    query=query,
                    session_id=st.session_state.session_id,
                    user_id=st.session_state.user_id,
                )

            except Exception as e:

                answer = (
                    "⚠️ Sorry, something went wrong.\n\n"
                    f"`{str(e)}`"
                )

        st.markdown(answer)


    # -----------------------------------------------------
    # SAVE ANSWER TO SESSION STATE
    # -----------------------------------------------------

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": answer,
        }
    )
