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
# FRONTEND CSS
# =========================================================

st.markdown(
    """
    <style>

    /* =====================================================
       GLOBAL
       ===================================================== */

    @import url(
        'https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Space+Grotesk:wght@500;600;700&display=swap'
    );

    html,
    body,
    [class*="css"] {
        font-family: "Inter", sans-serif;
    }

    .stApp {
        background:
            radial-gradient(
                circle at 10% 10%,
                rgba(99, 102, 241, 0.18),
                transparent 28%
            ),
            radial-gradient(
                circle at 90% 15%,
                rgba(6, 182, 212, 0.12),
                transparent 25%
            ),
            radial-gradient(
                circle at 70% 85%,
                rgba(139, 92, 246, 0.12),
                transparent 30%
            ),
            linear-gradient(
                135deg,
                #020617 0%,
                #080d24 48%,
                #020617 100%
            );
    }


    /* =====================================================
       BACKGROUND GRID
       ===================================================== */

    .stApp::before {
        content: "";
        position: fixed;
        inset: 0;
        pointer-events: none;

        background-image:
            linear-gradient(
                rgba(148, 163, 184, 0.025) 1px,
                transparent 1px
            ),
            linear-gradient(
                90deg,
                rgba(148, 163, 184, 0.025) 1px,
                transparent 1px
            );

        background-size: 55px 55px;

        mask-image: linear-gradient(
            to bottom,
            rgba(0,0,0,0.9),
            transparent
        );
    }


    /* =====================================================
       MAIN CONTAINER
       ===================================================== */

    .main .block-container {
        max-width: 1250px;
        padding-top: 2rem;
        padding-bottom: 6rem;
    }


    /* =====================================================
       SIDEBAR
       ===================================================== */

    section[data-testid="stSidebar"] {
        background:
            linear-gradient(
                180deg,
                #040713 0%,
                #070b1d 55%,
                #030611 100%
            );

        border-right: 1px solid rgba(139, 92, 246, 0.20);
    }

    section[data-testid="stSidebar"] > div {
        padding-top: 1rem;
    }


    /* Sidebar title */

    section[data-testid="stSidebar"] h1 {
        font-family: "Space Grotesk", sans-serif;

        font-size: 22px;

        font-weight: 700;

        letter-spacing: 2px;

        color: #f8fafc;
    }


    /* Sidebar subtitles */

    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3 {
        font-family: "Space Grotesk", sans-serif;

        color: #dbeafe;

        letter-spacing: 0.5px;
    }


    /* =====================================================
       SIDEBAR BUTTONS
       ===================================================== */

    section[data-testid="stSidebar"] .stButton button {

        min-height: 43px;

        border-radius: 12px;

        border: 1px solid rgba(139, 92, 246, 0.18);

        background:
            linear-gradient(
                135deg,
                rgba(19, 27, 57, 0.95),
                rgba(9, 14, 32, 0.95)
            );

        color: #dbeafe;

        font-weight: 500;

        transition:
            all 0.2s ease;
    }

    section[data-testid="stSidebar"] .stButton button:hover {

        border-color: rgba(139, 92, 246, 0.60);

        background:
            linear-gradient(
                135deg,
                rgba(39, 31, 82, 0.98),
                rgba(13, 21, 48, 0.98)
            );

        transform: translateY(-1px);

        box-shadow:
            0 8px 25px rgba(0,0,0,0.30),
            0 0 20px rgba(139,92,246,0.12);
    }


    /* =====================================================
       SIDEBAR TEXT INPUT
       ===================================================== */

    section[data-testid="stSidebar"] input {

        background: #080d22 !important;

        color: #f8fafc !important;

        border: 1px solid rgba(139,92,246,0.20) !important;

        border-radius: 10px !important;
    }

    section[data-testid="stSidebar"] input:focus {

        border-color: rgba(139,92,246,0.65) !important;

        box-shadow:
            0 0 0 1px rgba(139,92,246,0.20) !important;
    }


    /* =====================================================
       MAIN TITLE
       ===================================================== */

    .main-title {

        font-family: "Space Grotesk", sans-serif;

        text-align: center;

        font-size: clamp(
            34px,
            5vw,
            58px
        );

        font-weight: 700;

        letter-spacing: 5px;

        margin-top: 8px;

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
    }


    /* =====================================================
       SUBTITLE
       ===================================================== */

    .subtitle {

        text-align: center;

        max-width: 750px;

        margin: 15px auto 22px auto;

        color: #94a3b8;

        font-size: 14px;

        line-height: 1.8;
    }


    /* =====================================================
       QUANTUM ICON
       ===================================================== */

    .quantum-icon {

        text-align: center;

        font-size: 76px;

        line-height: 1;

        margin-bottom: 8px;

        text-shadow:
            0 0 8px rgba(255,255,255,0.9),
            0 0 20px rgba(139,92,246,0.9),
            0 0 45px rgba(99,102,241,0.7),
            0 0 80px rgba(59,130,246,0.4);

        animation: quantum-pulse 3s ease-in-out infinite;
    }

    @keyframes quantum-pulse {

        0%,
        100% {
            transform: scale(1);
            filter: brightness(1);
        }

        50% {
            transform: scale(1.08);
            filter: brightness(1.25);
        }
    }


    /* =====================================================
       ONLINE STATUS
       ===================================================== */

    .online {

        width: fit-content;

        margin: 0 auto 28px auto;

        padding: 7px 15px;

        border-radius: 999px;

        background: rgba(34,197,94,0.06);

        border: 1px solid rgba(34,197,94,0.20);

        color: #86efac;

        font-size: 10px;

        font-weight: 700;

        letter-spacing: 1.8px;
    }


    /* =====================================================
       QUANTUM LINE
       ===================================================== */

    .quantum-line {

        width: 220px;

        height: 1px;

        margin: 0 auto 25px auto;

        background:
            linear-gradient(
                90deg,
                transparent,
                rgba(139,92,246,0.8),
                rgba(59,130,246,0.8),
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
                rgba(15,23,42,0.78),
                rgba(7,12,28,0.78)
            );

        margin-bottom: 11px;

        transition:
            border-color 0.2s ease,
            transform 0.2s ease;
    }

    [data-testid="stChatMessage"]:hover {

        border-color:
            rgba(139,92,246,0.25);

        transform:
            translateY(-1px);
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
                rgba(12,18,38,0.98),
                rgba(5,10,25,0.98)
            );

        border: 1px solid rgba(139,92,246,0.25);

        border-radius: 16px;

        box-shadow:
            0 15px 45px rgba(0,0,0,0.30);
    }

    [data-testid="stChatInput"] > div:focus-within {

        border-color:
            rgba(139,92,246,0.65);

        box-shadow:
            0 0 0 1px rgba(139,92,246,0.20),
            0 15px 50px rgba(0,0,0,0.35);
    }

    [data-testid="stChatInput"] textarea {

        color: #f8fafc !important;

        font-size: 14px !important;
    }

    [data-testid="stChatInput"] textarea::placeholder {

        color: #64748b !important;
    }


    /* =====================================================
       NORMAL BUTTONS
       ===================================================== */

    .stButton button {

        border-radius: 11px;

        transition:
            all 0.2s ease;
    }

    .stButton button:hover {

        transform:
            translateY(-1px);
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

        border-color:
            rgba(255,255,255,0.06);
    }


    /* =====================================================
       SCROLLBAR
       ===================================================== */

    ::-webkit-scrollbar {

        width: 7px;
    }

    ::-webkit-scrollbar-track {

        background:
            rgba(2,6,23,0.8);
    }

    ::-webkit-scrollbar-thumb {

        background:
            rgba(100,116,139,0.45);

        border-radius:
            10px;
    }


    /* =====================================================
       MOBILE
       ===================================================== */

    @media (max-width: 768px) {

        .main-title {

            font-size: 32px;

            letter-spacing: 2px;
        }

        .subtitle {

            font-size: 13px;
        }

        .quantum-icon {

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
        '<div class="quantum-icon">⚛️</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="main-title">QUANTUM AI TUTOR</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="subtitle">Explore quantum computing through an intelligent RAG-powered learning environment.</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="online">🟢 AI TUTOR ONLINE</div>',
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

            st.error(
                "Please enter your email."
            )

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

            except Exception:

                st.error(
                    "Unable to complete login. "
                    "Please check your connection and try again."
                )

    st.stop()


# =========================================================
# SIDEBAR
# =========================================================

with st.sidebar:

    st.markdown(
        """
        <div style="
            text-align:center;
            padding:8px 0 12px 0;
        ">
            <div style="
                font-size:48px;
                text-shadow:
                    0 0 12px rgba(139,92,246,0.9),
                    0 0 30px rgba(99,102,241,0.7);
            ">
                ⚛️
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.title("QUANTUM LAB")

    st.caption(
        "AI LEARNING ENVIRONMENT"
    )

    st.markdown(
        f"🟢  {st.session_state.user_email}"
    )

    st.divider()


    # =====================================================
    # NEW CHAT
    # =====================================================

    st.caption("WORKSPACE")

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

        except Exception:

            st.error(
                "Unable to create a new chat right now."
            )


    # =====================================================
    # LOAD CHAT SESSIONS
    # =====================================================

    try:

        st.session_state.sessions = get_user_sessions(
            st.session_state.user_id
        )

    except Exception:

        st.session_state.sessions = []

        st.warning(
            "Chat history is temporarily unavailable. "
            "Your RAG tutor is still available for a new session."
        )


    # =====================================================
    # SESSION LIST
    # =====================================================

    st.caption("YOUR SESSIONS")

    if not st.session_state.sessions:

        st.caption(
            "No saved sessions available."
        )

    else:

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

                    st.session_state.session_id = (
                        session_id
                    )

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

                except Exception:

                    st.error(
                        "Unable to open this chat right now."
                    )


    st.divider()


    # =====================================================
    # CHAT MANAGEMENT
    # =====================================================

    if st.session_state.session_id:

        st.caption("CHAT SETTINGS")

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
                        "Chat renamed successfully."
                    )

                    st.rerun()

                except Exception:

                    st.error(
                        "Unable to rename this chat."
                    )


        if st.button(
            "🗑️  Delete Chat",
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
                    "Chat deleted successfully."
                )

                st.rerun()

            except Exception:

                st.error(
                    "Unable to delete this chat."
                )


    st.divider()


    # =====================================================
    # LOGOUT
    # =====================================================

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
    '<div class="quantum-icon">⚛️</div>',
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="online">🟢 AI TUTOR ONLINE</div>',
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="main-title">QUANTUM AI TUTOR</div>',
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="quantum-line"></div>',
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="subtitle">
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


    # =====================================================
    # USER MESSAGE
    # =====================================================

    st.session_state.messages.append(
        {
            "role": "user",
            "content": query,
        }
    )

    with st.chat_message("user"):

        st.markdown(query)


    # =====================================================
    # RAG ANSWER
    # =====================================================

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


    # =====================================================
    # SAVE ANSWER TO UI STATE
    # =====================================================

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": answer,
        }
    )
