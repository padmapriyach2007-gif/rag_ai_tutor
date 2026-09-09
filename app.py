import io
import hashlib
import streamlit as st

# =========================================================
# OPTIONAL SPEECH RECOGNITION
# =========================================================

try:
    import speech_recognition as sr
    SPEECH_RECOGNITION_AVAILABLE = True
except ImportError:
    SPEECH_RECOGNITION_AVAILABLE = False


# =========================================================
# EXISTING RAG + DATABASE IMPORTS
# DO NOT CHANGE
# =========================================================

from rag_engine import (
    answer_question,
    create_chat_session,
    delete_chat,
    get_or_create_user,
    get_user_sessions,
    rename_chat,
    restore_chat,
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

defaults = {
    "logged_in": False,
    "user_email": "",
    "user_id": None,
    "session_id": None,
    "messages": [],
    "sessions": [],
    "uploaded_files": [],
    "drive_links": [],
    "processed_audio_hash": None,
    "rename_session_id": None,
    "show_canvas": False,
    "show_more_tools": False,
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value


# =========================================================
# CUSTOM CSS
# =========================================================

st.markdown(
    """
<style>

/* =========================================================
   IMPORT FONTS
   ========================================================= */

@import url(
'https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Space+Grotesk:wght@500;600;700&display=swap'
);


/* =========================================================
   GLOBAL
   ========================================================= */

html, body, [class*="css"] {
    font-family: "Inter", sans-serif;
}

.stApp {
    min-height: 100vh;

    background:
        radial-gradient(
            circle at 10% 15%,
            rgba(88, 70, 220, 0.20),
            transparent 28%
        ),
        radial-gradient(
            circle at 88% 12%,
            rgba(0, 180, 255, 0.13),
            transparent 27%
        ),
        radial-gradient(
            circle at 75% 80%,
            rgba(151, 80, 255, 0.13),
            transparent 30%
        ),
        linear-gradient(
            135deg,
            #020617 0%,
            #080b22 48%,
            #020617 100%
        );
}


/* =========================================================
   QUANTUM GRID
   ========================================================= */

.stApp::before {
    content: "";
    position: fixed;
    inset: 0;
    pointer-events: none;

    background-image:
        linear-gradient(
            rgba(129,140,248,0.025) 1px,
            transparent 1px
        ),
        linear-gradient(
            90deg,
            rgba(129,140,248,0.025) 1px,
            transparent 1px
        );

    background-size: 55px 55px;
    z-index: 0;
}


/* =========================================================
   STARS
   ========================================================= */

.quantum-space {
    position: fixed;
    inset: 0;
    pointer-events: none;
    overflow: hidden;
    z-index: 0;
}

.quantum-space::before {
    content: "";
    position: absolute;
    inset: 0;

    background-image:
        radial-gradient(
            circle at 4% 12%,
            rgba(255,255,255,.95) 0px,
            rgba(255,255,255,.55) 1px,
            transparent 2px
        ),
        radial-gradient(
            circle at 11% 34%,
            rgba(180,210,255,.85) 0px,
            rgba(180,210,255,.35) 1px,
            transparent 2px
        ),
        radial-gradient(
            circle at 58% 27%,
            rgba(200,180,255,.95) 0px,
            rgba(200,180,255,.35) 1px,
            transparent 2px
        ),
        radial-gradient(
            circle at 89% 74%,
            rgba(200,180,255,.9) 0px,
            rgba(200,180,255,.35) 1px,
            transparent 2px
        );

    animation: starDrift 18s ease-in-out infinite alternate;
}

@keyframes starDrift {
    0% {
        transform: translate3d(0,0,0);
        opacity: .62;
    }

    50% {
        transform: translate3d(0,-4px,0);
        opacity: .88;
    }

    100% {
        transform: translate3d(0,3px,0);
        opacity: .68;
    }
}


/* =========================================================
   MAIN CONTAINER
   ========================================================= */

.main .block-container {
    max-width: 1250px;
    padding-top: 1rem;
    padding-bottom: 8rem;
    position: relative;
    z-index: 2;
}


/* =========================================================
   SIDEBAR
   ========================================================= */

section[data-testid="stSidebar"] {
    background:
        linear-gradient(
            180deg,
            #030611,
            #070b1d,
            #02040c
        );

    border-right: 1px solid rgba(139,92,246,.18);
}

section[data-testid="stSidebar"] .stButton button {
    border-radius: 12px;

    border: 1px solid rgba(139,92,246,.16);

    background:
        linear-gradient(
            135deg,
            rgba(18,25,53,.96),
            rgba(7,12,29,.96)
        );

    color: #dbeafe;

    transition: all .2s ease;
}

section[data-testid="stSidebar"] .stButton button:hover {
    border-color: rgba(167,139,250,.60);

    box-shadow:
        0 0 22px rgba(139,92,246,.16);

    transform: translateY(-1px);
}


/* =========================================================
   HEADER
   ========================================================= */

.quantum-logo {
    text-align: center;

    font-size: 70px;

    line-height: 1;

    margin: 10px auto 5px auto;

    text-shadow:
        0 0 8px #ffffff,
        0 0 20px rgba(139,92,246,1),
        0 0 45px rgba(99,102,241,.9);

    animation:
        quantumPulse 3s ease-in-out infinite;
}

@keyframes quantumPulse {

    0%,100% {
        transform: scale(1);
        filter: brightness(1);
    }

    50% {
        transform: scale(1.07);
        filter: brightness(1.25);
    }
}

.main-title {
    text-align: center;

    font-family: "Space Grotesk", sans-serif;

    font-size:
        clamp(34px, 5vw, 58px);

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
}

.subtitle {
    text-align: center;

    max-width: 780px;

    margin:
        10px auto 18px auto;

    color: #94a3b8;

    font-size: 14px;

    line-height: 1.8;
}

.online {
    width: fit-content;

    margin:
        0 auto 18px auto;

    padding:
        6px 14px;

    border-radius: 999px;

    color: #86efac;

    background:
        rgba(34,197,94,.05);

    border:
        1px solid rgba(34,197,94,.20);

    font-size: 10px;

    font-weight: 700;

    letter-spacing: 1.7px;

    box-shadow:
        0 0 20px rgba(34,197,94,.08);
}

.quantum-line {
    width: 230px;

    height: 1px;

    margin:
        0 auto 22px auto;

    background:
        linear-gradient(
            90deg,
            transparent,
            rgba(139,92,246,.9),
            rgba(59,130,246,.9),
            transparent
        );

    box-shadow:
        0 0 14px rgba(139,92,246,.4);
}


/* =========================================================
   CHAT MESSAGES
   ========================================================= */

[data-testid="stChatMessage"] {
    border-radius: 16px;

    border:
        1px solid rgba(139,92,246,.11);

    background:
        linear-gradient(
            135deg,
            rgba(15,23,42,.82),
            rgba(7,12,28,.82)
        );

    margin-bottom: 10px;

    transition: all .2s ease;
}

[data-testid="stChatMessage"]:hover {
    border-color:
        rgba(139,92,246,.30);

    box-shadow:
        0 5px 25px rgba(0,0,0,.20);
}

[data-testid="stChatMessage"] p {
    color: #dbe4f0;
    line-height: 1.7;
}


/* =========================================================
   PROMPT AREA
   ========================================================= */

.prompt-wrapper {
    margin-top: 25px;

    padding:
        10px;

    border-radius: 20px;

    border:
        1px solid rgba(139,92,246,.30);

    background:
        linear-gradient(
            135deg,
            rgba(15,23,42,.96),
            rgba(7,12,28,.96)
        );

    box-shadow:
        0 0 30px rgba(99,102,241,.12),
        inset 0 0 20px rgba(99,102,241,.04);
}

.prompt-title {
    color: #94a3b8;
    font-size: 11px;
    padding-left: 8px;
    margin-bottom: 4px;
}

.prompt-input input {
    background: transparent !important;
    border: none !important;
    color: #f1f5f9 !important;
    font-size: 15px !important;
}

.prompt-input input:focus {
    box-shadow: none !important;
}


/* =========================================================
   PROMPT BUTTONS
   ========================================================= */

.prompt-wrapper .stButton button {
    min-height: 48px;

    border-radius: 14px;

    border:
        1px solid rgba(139,92,246,.28);

    background:
        linear-gradient(
            135deg,
            rgba(30,41,75,.95),
            rgba(10,15,35,.95)
        );

    color: #dbeafe;

    font-size: 20px;

    transition:
        transform .2s ease,
        box-shadow .2s ease,
        border-color .2s ease;
}

.prompt-wrapper .stButton button:hover {
    transform:
        translateY(-2px);

    border-color:
        rgba(139,92,246,.75);

    box-shadow:
        0 0 20px rgba(99,102,241,.30);
}


/* =========================================================
   SEND BUTTON
   ========================================================= */

.send-button button {
    background:
        linear-gradient(
            135deg,
            #6366f1,
            #3b82f6
        ) !important;

    color: white !important;

    border:
        1px solid rgba(165,180,252,.55) !important;

    box-shadow:
        0 0 20px rgba(99,102,241,.25);
}


/* =========================================================
   TOOL POPUP
   ========================================================= */

.tool-card {
    padding: 12px;

    border-radius: 14px;

    border:
        1px solid rgba(139,92,246,.20);

    background:
        rgba(10,15,35,.90);

    margin-bottom: 8px;
}


/* =========================================================
   CANVAS
   ========================================================= */

.canvas-box {
    margin-top: 20px;

    padding: 25px;

    min-height: 300px;

    border-radius: 20px;

    border:
        1px solid rgba(99,102,241,.30);

    background:
        linear-gradient(
            135deg,
            rgba(15,23,42,.92),
            rgba(10,15,35,.92)
        );

    box-shadow:
        0 0 35px rgba(99,102,241,.10);
}


/* =========================================================
   LOGIN
   ========================================================= */

.login-box {
    max-width: 520px;

    margin:
        40px auto;

    padding:
        35px;

    border-radius: 24px;

    border:
        1px solid rgba(139,92,246,.25);

    background:
        linear-gradient(
            135deg,
            rgba(15,23,42,.94),
            rgba(7,12,28,.94)
        );

    box-shadow:
        0 0 40px rgba(99,102,241,.12);
}

</style>

<div class="quantum-space"></div>
""",
    unsafe_allow_html=True,
)


# =========================================================
# HELPER FUNCTIONS
# =========================================================

def refresh_sessions():
    """Reload chat history from database."""
    if st.session_state.user_id:
        st.session_state.sessions = get_user_sessions(
            st.session_state.user_id
        )


def start_new_chat():
    """Create a new database chat."""
    if not st.session_state.logged_in:
        return

    new_session_id = create_chat_session(
        st.session_state.user_id,
        "New Chat"
    )

    st.session_state.session_id = new_session_id
    st.session_state.messages = []

    refresh_sessions()


def clear_current_chat():
    """Clear messages currently displayed."""
    st.session_state.messages = []


def logout_user():
    """Log out current user."""
    st.session_state.logged_in = False
    st.session_state.user_email = ""
    st.session_state.user_id = None
    st.session_state.session_id = None
    st.session_state.messages = []
    st.session_state.sessions = []
    st.session_state.uploaded_files = []
    st.session_state.drive_links = []


def process_query(user_query):
    """Send query to RAG engine."""

    if not user_query:
        return

    if not st.session_state.logged_in:
        st.warning("Please log in first.")
        return

    # -----------------------------------------------------
    # Create chat automatically if none exists
    # -----------------------------------------------------

    if st.session_state.session_id is None:
        start_new_chat()

    # -----------------------------------------------------
    # User message
    # -----------------------------------------------------

    st.session_state.messages.append(
        {
            "role": "user",
            "content": user_query,
        }
    )

    # -----------------------------------------------------
    # RAG response
    # -----------------------------------------------------

    try:

        answer = answer_question(
            query=user_query,
            session_id=st.session_state.session_id,
            user_id=st.session_state.user_id,
        )

    except Exception as e:

        answer = (
            "⚠️ I couldn't generate a response right now.\n\n"
            f"Error: `{str(e)}`"
        )

    # -----------------------------------------------------
    # Assistant message
    # -----------------------------------------------------

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": answer,
        }
    )


# =========================================================
# SIDEBAR
# =========================================================

with st.sidebar:

    st.markdown(
        """
        <div style="
            text-align:center;
            font-size:30px;
            margin-bottom:5px;
        ">
            ⚛️
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div style="
            text-align:center;
            font-size:22px;
            font-weight:700;
            color:#e0e7ff;
        ">
            QUANTUM LAB
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("---")


    # =====================================================
    # LOGIN SYSTEM
    # =====================================================

    st.subheader("🔐 Account")

    if not st.session_state.logged_in:

        email = st.text_input(
            "Email",
            placeholder="student@example.com",
            key="login_email"
        )

        if st.button(
            "🔑 Log In",
            use_container_width=True
        ):

            if email.strip():

                try:

                    user_id = get_or_create_user(
                        email.strip()
                    )

                    st.session_state.user_email = email.strip()
                    st.session_state.user_id = user_id
                    st.session_state.logged_in = True

                    refresh_sessions()

                    st.success("Login successful!")

                    st.rerun()

                except Exception as e:

                    st.error(
                        f"Login failed: {str(e)}"
                    )

            else:

                st.warning(
                    "Please enter your email."
                )

    else:

        st.markdown(
            f"""
            <div style="
                padding:12px;
                border-radius:12px;
                background:rgba(99,102,241,.10);
                border:1px solid rgba(99,102,241,.20);
                color:#cbd5e1;
                font-size:13px;
            ">
                👤 Logged in as<br>
                <strong>{st.session_state.user_email}</strong>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.write("")

        if st.button(
            "🚪 Log Out",
            use_container_width=True
        ):

            logout_user()
            st.rerun()


    # =====================================================
    # CHAT CONTROLS
    # =====================================================

    if st.session_state.logged_in:

        st.markdown("---")

        st.subheader("💬 Chats")

        # -------------------------------------------------
        # NEW CHAT
        # -------------------------------------------------

        if st.button(
            "➕ New Chat",
            use_container_width=True
        ):

            start_new_chat()
            st.rerun()


        # -------------------------------------------------
        # CHAT HISTORY
        # -------------------------------------------------

        st.markdown(
            """
            <div style="
                color:#94a3b8;
                font-size:11px;
                font-weight:600;
                letter-spacing:1px;
                margin:12px 0 8px 0;
            ">
                CHAT HISTORY
            </div>
            """,
            unsafe_allow_html=True,
        )

        refresh_sessions()

        if not st.session_state.sessions:

            st.caption(
                "No conversations yet."
            )

        else:

            for chat in st.session_state.sessions:

                session_id = (
                    chat.get("session_id")
                    or chat.get("id")
                )

                title = chat.get(
                    "title",
                    "Untitled Chat"
                )

                if not title:
                    title = "Untitled Chat"


                # -----------------------------------------
                # Chat selection
                # -----------------------------------------

                selected = (
                    session_id ==
                    st.session_state.session_id
                )

                if selected:
                    prefix = "🟣"
                else:
                    prefix = "💬"


                col1, col2, col3 = st.columns(
                    [0.62, 0.19, 0.19],
                    gap="small"
                )


                with col1:

                    short_title = title

                    if len(short_title) > 22:
                        short_title = (
                            short_title[:22] + "..."
                        )

                    if st.button(
                        f"{prefix} {short_title}",
                        key=f"chat_{session_id}",
                        use_container_width=True,
                    ):

                        st.session_state.session_id = session_id

                        try:
                            st.session_state.messages = (
                                restore_chat(session_id)
                            )
                        except Exception:
                            st.session_state.messages = []

                        st.rerun()


                # -----------------------------------------
                # RENAME
                # -----------------------------------------

                with col2:

                    if st.button(
                        "✏️",
                        key=f"rename_{session_id}",
                        help="Rename chat",
                        use_container_width=True,
                    ):

                        st.session_state.rename_session_id = (
                            session_id
                        )

                        st.rerun()


                # -----------------------------------------
                # DELETE
                # -----------------------------------------

                with col3:

                    if st.button(
                        "🗑️",
                        key=f"delete_{session_id}",
                        help="Delete chat",
                        use_container_width=True,
                    ):

                        try:

                            delete_chat(
                                session_id
                            )

                        except Exception as e:

                            st.error(
                                f"Delete failed: {e}"
                            )

                        if (
                            st.session_state.session_id
                            == session_id
                        ):

                            st.session_state.session_id = None
                            st.session_state.messages = []

                        refresh_sessions()

                        st.rerun()


                # -----------------------------------------
                # RENAME BOX
                # -----------------------------------------

                if (
                    st.session_state.rename_session_id
                    == session_id
                ):

                    new_title = st.text_input(
                        "Chat name",
                        value=title,
                        key=f"title_input_{session_id}",
                    )

                    rename_col1, rename_col2 = st.columns(2)

                    with rename_col1:

                        if st.button(
                            "Save",
                            key=f"save_name_{session_id}",
                            use_container_width=True,
                        ):

                            if new_title.strip():

                                rename_chat(
                                    session_id,
                                    new_title.strip()
                                )

                            st.session_state.rename_session_id = None

                            refresh_sessions()

                            st.rerun()

                    with rename_col2:

                        if st.button(
                            "Cancel",
                            key=f"cancel_name_{session_id}",
                            use_container_width=True,
                        ):

                            st.session_state.rename_session_id = None

                            st.rerun()


        # -------------------------------------------------
        # CLEAR CONVERSATION
        # -------------------------------------------------

        st.markdown("---")

        if st.button(
            "🧹 Clear Conversation",
            use_container_width=True,
        ):

            clear_current_chat()

            st.success(
                "Current conversation cleared."
            )

            st.rerun()


        # -------------------------------------------------
        # CURRENT CHAT INFO
        # -------------------------------------------------

        if st.session_state.session_id:

            st.markdown("---")

            st.caption(
                f"Current Chat ID: "
                f"{st.session_state.session_id}"
            )


# =========================================================
# LOGIN SCREEN
# =========================================================

if not st.session_state.logged_in:

    st.markdown(
        """
        <div class="login-box">

            <div style="
                text-align:center;
                font-size:65px;
            ">
                ⚛️
            </div>

            <div style="
                text-align:center;
                font-family:'Space Grotesk';
                font-size:30px;
                font-weight:700;
                color:#e0e7ff;
                margin-top:10px;
            ">
                QUANTUM AI TUTOR
            </div>

            <div style="
                text-align:center;
                color:#94a3b8;
                margin-top:10px;
                line-height:1.7;
            ">
                Explore quantum computing through
                interactive AI-powered learning.
            </div>

        </div>
        """,
        unsafe_allow_html=True,
    )

    st.info(
        "🔐 Enter your email in the sidebar to start learning."
    )

    st.stop()


# =========================================================
# HEADER
# =========================================================

st.markdown(
    '<div class="quantum-logo">⚛️</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="main-title">QUANTUM LAB</div>',
    unsafe_allow_html=True
)

st.markdown(
    """
    <div class="subtitle">
        Interactive AI Tutor for Quantum Computing
        & Advanced Physics
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="online">● AI TUTOR ONLINE</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="quantum-line"></div>',
    unsafe_allow_html=True
)


# =========================================================
# ACTIVE CHAT TITLE
# =========================================================

if st.session_state.session_id:

    current_title = "New Chat"

    for chat in st.session_state.sessions:

        sid = (
            chat.get("session_id")
            or chat.get("id")
        )

        if sid == st.session_state.session_id:

            current_title = chat.get(
                "title",
                "New Chat"
            )

            break

    st.markdown(
        f"""
        <div style="
            text-align:center;
            color:#a5b4fc;
            font-size:13px;
            margin-bottom:15px;
        ">
            💬 {current_title}
        </div>
        """,
        unsafe_allow_html=True,
    )


# =========================================================
# DISPLAY CHAT
# =========================================================

for message in st.session_state.messages:

    with st.chat_message(
        message["role"]
    ):

        st.markdown(
            message["content"]
        )


# =========================================================
# CANVAS WORKSPACE
# =========================================================

if st.session_state.show_canvas:

    st.markdown(
        """
        <div class="canvas-box">

            <div style="
                font-size:24px;
                font-weight:700;
                color:#e0e7ff;
                margin-bottom:10px;
            ">
                🎨 Canvas Workbench
            </div>

            <div style="
                color:#94a3b8;
                line-height:1.7;
            ">
                Use this workspace for quantum notes,
                equations, ideas, diagrams and explanations.
            </div>

        </div>
        """,
        unsafe_allow_html=True,
    )

    canvas_text = st.text_area(
        "Canvas",
        placeholder=(
            "Write your quantum computing notes, "
            "equations or ideas here..."
        ),
        height=220,
        key="canvas_text"
    )

    canvas_col1, canvas_col2 = st.columns(2)

    with canvas_col1:

        if st.button(
            "💾 Save Canvas",
            use_container_width=True
        ):

            st.success(
                "Canvas content saved for this session."
            )

    with canvas_col2:

        if st.button(
            "✖ Close Canvas",
            use_container_width=True
        ):

            st.session_state.show_canvas = False
            st.rerun()


# =========================================================
# PROMPT AREA
# =========================================================

st.markdown(
    '<div class="prompt-wrapper">',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="prompt-title">ASK YOUR QUANTUM AI TUTOR</div>',
    unsafe_allow_html=True
)


prompt_col1, prompt_col2, prompt_col3, prompt_col4 = st.columns(
    [0.09, 0.67, 0.09, 0.15],
    vertical_alignment="center"
)


# =========================================================
# PLUS BUTTON
# =========================================================

with prompt_col1:

    with st.popover(
        "＋",
        use_container_width=True
    ):

        st.markdown(
            """
            <div style="
                font-size:18px;
                font-weight:700;
                color:#e0e7ff;
                margin-bottom:12px;
            ">
                Tools & Attachments
            </div>
            """,
            unsafe_allow_html=True,
        )


        tab1, tab2, tab3 = st.tabs(
            [
                "📁 Photos & Files",
                "☁️ Drive",
                "🛠️ More Tools"
            ]
        )


        # -------------------------------------------------
        # PHOTOS & FILES
        # -------------------------------------------------

        with tab1:

            uploaded = st.file_uploader(
                "Upload photos or files",
                type=[
                    "png",
                    "jpg",
                    "jpeg",
                    "webp",
                    "pdf",
                    "txt",
                    "docx",
                    "csv",
                    "xlsx",
                    "py",
                    "java",
                    "c",
                ],
                accept_multiple_files=True,
                key="quantum_attachments",
            )

            if uploaded:

                st.session_state.uploaded_files = uploaded

                st.success(
                    f"{len(uploaded)} file(s) attached"
                )

                for file in uploaded:

                    st.caption(
                        f"📎 {file.name}"
                    )


        # -------------------------------------------------
        # GOOGLE DRIVE
        # -------------------------------------------------

        with tab2:

            st.markdown(
                """
                <div class="tool-card">
                    ☁️ <strong>Google Drive</strong><br>
                    <span style="color:#94a3b8;">
                    Attach a Google Drive file link.
                    </span>
                </div>
                """,
                unsafe_allow_html=True,
            )

            drive_url = st.text_input(
                "Drive file link",
                placeholder="Paste Google Drive link",
                key="drive_url",
            )

            if st.button(
                "Attach Drive File",
                use_container_width=True,
            ):

                if drive_url.strip():

                    st.session_state.drive_links.append(
                        drive_url.strip()
                    )

                    st.success(
                        "Google Drive link attached."
                    )

                else:

                    st.warning(
                        "Please paste a Drive link."
                    )


        # -------------------------------------------------
        # MORE TOOLS
        # -------------------------------------------------

        with tab3:

            st.markdown(
                "### 🛠️ More Tools"
            )

            if st.button(
                "🎨 Canvas",
                use_container_width=True,
            ):

                st.session_state.show_canvas = True
                st.rerun()

            if st.button(
                "🧮 Quantum Calculator",
                use_container_width=True,
            ):

                st.info(
                    "Quantum Calculator tool activated."
                )

            if st.button(
                "📚 Learning Mode",
                use_container_width=True,
            ):

                st.info(
                    "Learning Mode activated. "
                    "Ask a quantum computing question."
                )

            if st.button(
                "📝 Notes",
                use_container_width=True,
            ):

                st.info(
                    "Notes tool activated."
                )


# =========================================================
# TEXT INPUT
# =========================================================

with prompt_col2:

    user_prompt = st.text_input(
        "Message",
        placeholder="Ask anything about quantum computing...",
        label_visibility="collapsed",
        key="custom_prompt",
    )


# =========================================================
# MICROPHONE
# =========================================================

with prompt_col3:

    audio_value = st.audio_input(
        "🎤",
        key="quantum_microphone",
        label_visibility="collapsed",
    )


# =========================================================
# SEND
# =========================================================

with prompt_col4:

    st.markdown(
        '<div class="send-button">',
        unsafe_allow_html=True
    )

    send_clicked = st.button(
        "➤ Send",
        use_container_width=True,
    )

    st.markdown(
        '</div>',
        unsafe_allow_html=True
    )


st.markdown(
    '</div>',
    unsafe_allow_html=True
)


# =========================================================
# ATTACHMENT INFORMATION
# =========================================================

if st.session_state.uploaded_files:

    st.markdown(
        "### 📎 Attached Files"
    )

    for file in st.session_state.uploaded_files:

        st.caption(
            f"• {file.name}"
        )


if st.session_state.drive_links:

    st.markdown(
        "### ☁️ Attached Drive Files"
    )

    for link in st.session_state.drive_links:

        st.caption(
            f"• {link}"
        )


# =========================================================
# MICROPHONE → SPEECH TO TEXT
# =========================================================

voice_query = ""

if audio_value is not None:

    try:

        audio_bytes = audio_value.getvalue()

        audio_hash = hashlib.md5(
            audio_bytes
        ).hexdigest()

        if (
            st.session_state.processed_audio_hash
            != audio_hash
        ):

            st.session_state.processed_audio_hash = (
                audio_hash
            )

            if SPEECH_RECOGNITION_AVAILABLE:

                recognizer = sr.Recognizer()

                audio_stream = io.BytesIO(
                    audio_bytes
                )

                with sr.AudioFile(
                    audio_stream
                ) as source:

                    recorded_audio = (
                        recognizer.record(source)
                    )

                voice_query = (
                    recognizer.recognize_google(
                        recorded_audio
                    )
                )

            else:

                st.warning(
                    "Install SpeechRecognition for "
                    "microphone transcription."
                )

    except sr.UnknownValueError:

        st.warning(
            "I couldn't understand the recording."
        )

    except Exception as e:

        st.warning(
            f"Microphone transcription failed: {e}"
        )


# =========================================================
# FINAL QUERY
# =========================================================

final_query = ""

if send_clicked:

    if user_prompt.strip():

        final_query = user_prompt.strip()

    elif voice_query.strip():

        final_query = voice_query.strip()

    else:

        st.warning(
            "Please type a question or use the microphone."
        )


# =========================================================
# EXECUTE RAG
# =========================================================

if final_query:

    process_query(final_query)

    # Clear prompt after processing
    st.session_state.custom_prompt = ""

    st.rerun()

