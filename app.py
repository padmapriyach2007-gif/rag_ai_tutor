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
# RAG + DATABASE IMPORTS
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
    page_title="Quantum AI Tutor",
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
    "show_tools": False,
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

/* =====================================================
   GOOGLE FONTS
   ===================================================== */

@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Space+Grotesk:wght@500;600;700&display=swap');


/* =====================================================
   GLOBAL
   ===================================================== */

html,
body,
[data-testid="stAppViewContainer"],
[data-testid="stAppViewBlockContainer"] {
    font-family: "Inter", sans-serif;
}

.stApp {
    min-height: 100vh;

    background:
        radial-gradient(
            circle at 15% 10%,
            rgba(91, 70, 220, 0.28),
            transparent 25%
        ),
        radial-gradient(
            circle at 85% 12%,
            rgba(0, 180, 255, 0.18),
            transparent 24%
        ),
        radial-gradient(
            circle at 75% 80%,
            rgba(170, 70, 255, 0.18),
            transparent 28%
        ),
        linear-gradient(
            135deg,
            #020617 0%,
            #070b24 45%,
            #030712 100%
        );

    color: #e2e8f0;
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
            rgba(129, 140, 248, 0.035) 1px,
            transparent 1px
        ),
        linear-gradient(
            90deg,
            rgba(129, 140, 248, 0.035) 1px,
            transparent 1px
        );

    background-size: 55px 55px;
    z-index: 0;
}


/* =====================================================
   MAIN CONTAINER
   ===================================================== */

.main .block-container {
    max-width: 1250px;
    padding-top: 1.2rem;
    padding-bottom: 8rem;

    position: relative;
    z-index: 2;
}


/* =====================================================
   SIDEBAR
   ===================================================== */

section[data-testid="stSidebar"] {
    background:
        linear-gradient(
            180deg,
            #030611 0%,
            #070b20 55%,
            #02040c 100%
        );

    border-right:
        1px solid rgba(139, 92, 246, 0.22);
}

section[data-testid="stSidebar"] h1,
section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] h3 {
    color: #eef2ff;
}

section[data-testid="stSidebar"] .stButton button {
    border-radius: 11px;

    border:
        1px solid rgba(139, 92, 246, 0.18);

    background:
        linear-gradient(
            135deg,
            rgba(20, 28, 60, 0.95),
            rgba(7, 12, 29, 0.95)
        );

    color: #dbeafe;

    transition: 0.2s ease;
}

section[data-testid="stSidebar"] .stButton button:hover {
    border-color:
        rgba(167, 139, 250, 0.70);

    box-shadow:
        0 0 20px rgba(99, 102, 241, 0.22);

    transform:
        translateY(-1px);
}


/* =====================================================
   LOGIN SCREEN
   ===================================================== */

.login-container {
    width: min(560px, 92%);
    margin: 8vh auto 0 auto;

    padding: 45px 45px 40px 45px;

    border-radius: 28px;

    background:
        linear-gradient(
            145deg,
            rgba(15, 23, 55, 0.96),
            rgba(5, 10, 28, 0.96)
        );

    border:
        1px solid rgba(139, 92, 246, 0.35);

    box-shadow:
        0 0 60px rgba(99, 102, 241, 0.18),
        inset 0 0 35px rgba(99, 102, 241, 0.04);

    text-align: center;
}

.login-icon {
    font-size: 80px;

    margin-bottom: 10px;

    text-shadow:
        0 0 15px rgba(139, 92, 246, 0.9),
        0 0 45px rgba(59, 130, 246, 0.55);
}

.login-title {
    font-family: "Space Grotesk", sans-serif;

    font-size: 34px;

    font-weight: 700;

    letter-spacing: 2px;

    background:
        linear-gradient(
            90deg,
            #ffffff,
            #c4b5fd,
            #93c5fd
        );

    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.login-subtitle {
    margin-top: 12px;

    color: #94a3b8;

    font-size: 14px;

    line-height: 1.7;
}


/* =====================================================
   HEADER
   ===================================================== */

.hero {
    text-align: center;

    padding-top: 20px;

    margin-bottom: 20px;
}

.hero-icon {
    font-size: 72px;

    line-height: 1;

    text-shadow:
        0 0 10px #ffffff,
        0 0 25px rgba(139, 92, 246, 0.95),
        0 0 50px rgba(59, 130, 246, 0.75);

    animation:
        pulse 3s infinite ease-in-out;
}

@keyframes pulse {

    0%, 100% {
        transform: scale(1);
    }

    50% {
        transform: scale(1.07);
    }
}

.hero-title {
    font-family:
        "Space Grotesk",
        sans-serif;

    font-size:
        clamp(36px, 5vw, 60px);

    font-weight: 700;

    letter-spacing: 4px;

    margin-top: 10px;

    background:
        linear-gradient(
            90deg,
            #ffffff,
            #c4b5fd,
            #60a5fa,
            #ffffff
        );

    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.hero-subtitle {
    color: #94a3b8;

    font-size: 15px;

    margin-top: 10px;

    letter-spacing: 0.5px;
}

.online-badge {
    display: inline-block;

    margin-top: 15px;

    padding:
        7px 16px;

    border-radius: 50px;

    color: #86efac;

    border:
        1px solid rgba(34, 197, 94, 0.25);

    background:
        rgba(34, 197, 94, 0.06);

    font-size: 10px;

    font-weight: 700;

    letter-spacing: 1.8px;

    box-shadow:
        0 0 20px rgba(34, 197, 94, 0.08);
}

.quantum-divider {
    width: 260px;

    height: 1px;

    margin:
        22px auto;

    background:
        linear-gradient(
            90deg,
            transparent,
            rgba(139, 92, 246, 0.9),
            rgba(59, 130, 246, 0.9),
            transparent
        );

    box-shadow:
        0 0 15px rgba(99, 102, 241, 0.4);
}


/* =====================================================
   WELCOME CARD
   ===================================================== */

.welcome-card {
    max-width: 820px;

    margin:
        30px auto;

    padding:
        28px;

    text-align: center;

    border-radius: 22px;

    background:
        linear-gradient(
            145deg,
            rgba(15, 23, 42, 0.70),
            rgba(7, 12, 28, 0.70)
        );

    border:
        1px solid rgba(139, 92, 246, 0.15);

    box-shadow:
        0 0 35px rgba(99, 102, 241, 0.08);
}

.welcome-title {
    color: #c4b5fd;

    font-size: 19px;

    font-weight: 700;

    margin-bottom: 10px;
}

.welcome-text {
    color: #94a3b8;

    line-height: 1.8;

    font-size: 14px;
}


/* =====================================================
   CHAT MESSAGE
   ===================================================== */

[data-testid="stChatMessage"] {
    border-radius: 17px;

    border:
        1px solid rgba(139, 92, 246, 0.12);

    background:
        linear-gradient(
            135deg,
            rgba(15, 23, 42, 0.82),
            rgba(7, 12, 28, 0.88)
        );

    margin-bottom: 10px;

    box-shadow:
        0 4px 20px rgba(0, 0, 0, 0.12);
}

[data-testid="stChatMessage"] p {
    color: #dbe4f0;

    line-height: 1.7;
}


/* =====================================================
   BOTTOM PROMPT CONTAINER
   ===================================================== */

.prompt-shell {
    width: 100%;

    margin-top: 25px;

    padding:
        9px;

    border-radius: 20px;

    background:
        linear-gradient(
            145deg,
            rgba(15, 23, 42, 0.97),
            rgba(5, 10, 27, 0.97)
        );

    border:
        1px solid rgba(139, 92, 246, 0.35);

    box-shadow:
        0 0 35px rgba(99, 102, 241, 0.12),
        inset 0 0 20px rgba(99, 102, 241, 0.04);
}


/* =====================================================
   INPUT
   ===================================================== */

.prompt-shell input {
    color: #f8fafc !important;

    background:
        transparent !important;

    border:
        1px solid rgba(139, 92, 246, 0.12) !important;

    border-radius:
        13px !important;

    min-height:
        48px !important;
}

.prompt-shell input:focus {
    border:
        1px solid rgba(139, 92, 246, 0.50) !important;

    box-shadow:
        0 0 18px rgba(99, 102, 241, 0.12) !important;
}


/* =====================================================
   PROMPT BUTTONS
   ===================================================== */

.prompt-shell .stButton button {
    min-height: 48px;

    border-radius: 13px;

    background:
        linear-gradient(
            135deg,
            rgba(26, 36, 73, 0.95),
            rgba(8, 14, 34, 0.95)
        );

    border:
        1px solid rgba(139, 92, 246, 0.25);

    color: #e0e7ff;

    font-weight: 600;

    transition: 0.2s ease;
}

.prompt-shell .stButton button:hover {
    border-color:
        rgba(139, 92, 246, 0.70);

    box-shadow:
        0 0 20px rgba(99, 102, 241, 0.25);

    transform:
        translateY(-1px);
}


/* =====================================================
   SEND BUTTON
   ===================================================== */

.send-button button {
    background:
        linear-gradient(
            135deg,
            #6366f1,
            #3b82f6
        ) !important;

    color: white !important;

    border:
        1px solid rgba(191, 219, 254, 0.5) !important;

    box-shadow:
        0 0 20px rgba(99, 102, 241, 0.28);
}


/* =====================================================
   FILE / TOOL CARDS
   ===================================================== */

.tool-card {
    padding: 12px;

    margin-bottom: 8px;

    border-radius: 13px;

    background:
        rgba(15, 23, 42, 0.75);

    border:
        1px solid rgba(139, 92, 246, 0.18);

    color: #cbd5e1;
}


/* =====================================================
   CANVAS
   ===================================================== */

.canvas-container {
    margin-top: 20px;

    padding: 25px;

    border-radius: 22px;

    border:
        1px solid rgba(99, 102, 241, 0.30);

    background:
        linear-gradient(
            145deg,
            rgba(15, 23, 42, 0.90),
            rgba(7, 12, 28, 0.90)
        );

    box-shadow:
        0 0 40px rgba(99, 102, 241, 0.10);
}


/* =====================================================
   HIDE DEFAULT STREAMLIT FOOTER
   ===================================================== */

footer {
    visibility: hidden;
}

</style>
""",
    unsafe_allow_html=True,
)


# =========================================================
# HELPER FUNCTIONS
# =========================================================

def refresh_sessions():
    if st.session_state.user_id:
        try:
            st.session_state.sessions = get_user_sessions(
                st.session_state.user_id
            )
        except Exception:
            st.session_state.sessions = []


def create_new_chat():
    if not st.session_state.logged_in:
        return

    try:
        new_id = create_chat_session(
            st.session_state.user_id,
            "New Chat"
        )

        st.session_state.session_id = new_id
        st.session_state.messages = []

        refresh_sessions()

    except Exception as e:
        st.error(f"Could not create new chat: {e}")


def logout():
    st.session_state.logged_in = False
    st.session_state.user_email = ""
    st.session_state.user_id = None
    st.session_state.session_id = None
    st.session_state.messages = []
    st.session_state.sessions = []
    st.session_state.uploaded_files = []
    st.session_state.drive_links = []


def send_question(question):
    question = question.strip()

    if not question:
        return

    # -----------------------------------------------------
    # Automatically create chat if needed
    # -----------------------------------------------------

    if st.session_state.session_id is None:
        create_new_chat()

    # -----------------------------------------------------
    # User message
    # -----------------------------------------------------

    st.session_state.messages.append(
        {
            "role": "user",
            "content": question
        }
    )

    # -----------------------------------------------------
    # RAG
    # -----------------------------------------------------

    try:

        response = answer_question(
            query=question,
            session_id=st.session_state.session_id,
            user_id=st.session_state.user_id,
        )

    except Exception as e:

        response = (
            "⚠️ Something went wrong while generating "
            "the answer.\n\n"
            f"`{str(e)}`"
        )

    # -----------------------------------------------------
    # Assistant message
    # -----------------------------------------------------

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": response
        }
    )


# =========================================================
# LOGIN SCREEN
# =========================================================

if not st.session_state.logged_in:

    # Keep sidebar visually empty before login
    with st.sidebar:
        st.markdown(
            """
            <div style="
                text-align:center;
                margin-top:40px;
                color:#64748b;
                font-size:13px;
            ">
                🔐 Login required
            </div>
            """,
            unsafe_allow_html=True
        )

    st.markdown(
        """
        <div class="login-container">

            <div class="login-icon">
                ⚛️
            </div>

            <div class="login-title">
                QUANTUM AI TUTOR
            </div>

            <div class="login-subtitle">
                Your intelligent AI learning assistant
                for Quantum Computing, Physics and
                advanced technical concepts.
            </div>

            <div style="
                margin-top:20px;
                color:#86efac;
                font-size:11px;
                font-weight:700;
                letter-spacing:1.5px;
            ">
                ● AI LEARNING SYSTEM ONLINE
            </div>

        </div>
        """,
        unsafe_allow_html=True,
    )

    # -----------------------------------------------------
    # Center login form
    # -----------------------------------------------------

    left, center, right = st.columns(
        [1, 2, 1]
    )

    with center:

        st.markdown(
            "<div style='height:15px'></div>",
            unsafe_allow_html=True
        )

        with st.form(
            "login_form"
        ):

            email = st.text_input(
                "📧 Email Address",
                placeholder="Enter your email",
            )

            login_submit = st.form_submit_button(
                "🔐 LOGIN TO QUANTUM LAB",
                use_container_width=True,
            )

            if login_submit:

                if not email.strip():

                    st.warning(
                        "Please enter your email address."
                    )

                else:

                    try:

                        user_id = get_or_create_user(
                            email.strip()
                        )

                        st.session_state.user_email = (
                            email.strip()
                        )

                        st.session_state.user_id = user_id

                        st.session_state.logged_in = True

                        refresh_sessions()

                        st.rerun()

                    except Exception as e:

                        st.error(
                            f"Login failed: {e}"
                        )

    st.stop()


# =========================================================
# SIDEBAR AFTER LOGIN
# =========================================================

with st.sidebar:

    st.markdown(
        """
        <div style="
            text-align:center;
            font-size:35px;
            margin-bottom:5px;
        ">
            ⚛️
        </div>

        <div style="
            text-align:center;
            font-family:'Space Grotesk';
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
    # USER PROFILE
    # =====================================================

    st.subheader("👤 Account")

    st.markdown(
        f"""
        <div style="
            padding:12px;
            border-radius:13px;
            background:rgba(99,102,241,0.08);
            border:1px solid rgba(99,102,241,0.20);
            color:#cbd5e1;
            font-size:12px;
        ">
            Logged in as<br>
            <strong>{st.session_state.user_email}</strong>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.write("")

    if st.button(
        "🚪 Logout",
        use_container_width=True
    ):

        logout()
        st.rerun()

    # =====================================================
    # NEW CHAT
    # =====================================================

    st.markdown("---")

    st.subheader("💬 Conversations")

    if st.button(
        "➕ New Chat",
        use_container_width=True
    ):

        create_new_chat()
        st.rerun()

    # =====================================================
    # CHAT HISTORY
    # =====================================================

    refresh_sessions()

    if st.session_state.sessions:

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

            # -------------------------------------------------
            # SELECT + RENAME + DELETE
            # -------------------------------------------------

            c1, c2, c3 = st.columns(
                [0.62, 0.19, 0.19],
                gap="small"
            )

            with c1:

                display_title = title

                if len(display_title) > 20:
                    display_title = (
                        display_title[:20] + "..."
                    )

                icon = (
                    "🟣"
                    if session_id ==
                    st.session_state.session_id
                    else "💬"
                )

                if st.button(
                    f"{icon} {display_title}",
                    key=f"open_chat_{session_id}",
                    use_container_width=True,
                ):

                    st.session_state.session_id = (
                        session_id
                    )

                    try:

                        st.session_state.messages = (
                            restore_chat(session_id)
                        )

                    except Exception:

                        st.session_state.messages = []

                    st.rerun()

            with c2:

                if st.button(
                    "✏️",
                    key=f"rename_chat_{session_id}",
                    help="Rename chat",
                    use_container_width=True,
                ):

                    st.session_state.rename_session_id = (
                        session_id
                    )

                    st.rerun()

            with c3:

                if st.button(
                    "🗑️",
                    key=f"delete_chat_{session_id}",
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

            # -------------------------------------------------
            # RENAME UI
            # -------------------------------------------------

            if (
                st.session_state.rename_session_id
                == session_id
            ):

                new_name = st.text_input(
                    "New chat name",
                    value=title,
                    key=f"new_name_{session_id}"
                )

                r1, r2 = st.columns(2)

                with r1:

                    if st.button(
                        "Save",
                        key=f"save_{session_id}",
                        use_container_width=True
                    ):

                        if new_name.strip():

                            try:

                                rename_chat(
                                    session_id,
                                    new_name.strip()
                                )

                                st.session_state.rename_session_id = None

                                refresh_sessions()

                                st.rerun()

                            except Exception as e:

                                st.error(
                                    f"Rename failed: {e}"
                                )

                with r2:

                    if st.button(
                        "Cancel",
                        key=f"cancel_{session_id}",
                        use_container_width=True
                    ):

                        st.session_state.rename_session_id = None
                        st.rerun()

    else:

        st.caption(
            "No chats yet. Click New Chat to begin."
        )

    # =====================================================
    # CLEAR
    # =====================================================

    st.markdown("---")

    if st.button(
        "🧹 Clear Conversation",
        use_container_width=True
    ):

        st.session_state.messages = []

        st.rerun()


# =========================================================
# MAIN HEADER
# =========================================================

st.markdown(
    """
    <div class="hero">

        <div class="hero-icon">
            ⚛️
        </div>

        <div class="hero-title">
            QUANTUM AI TUTOR
        </div>

        <div class="hero-subtitle">
            Your AI Learning Assistant for
            Quantum Computing
        </div>

        <div class="online-badge">
            ● AI LEARNING ASSISTANT ONLINE
        </div>

        <div class="quantum-divider"></div>

    </div>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# WELCOME MESSAGE
# =========================================================

if not st.session_state.messages:

    st.markdown(
        """
        <div class="welcome-card">

            <div class="welcome-title">
                🧠 Learn. Explore. Understand.
            </div>

            <div class="welcome-text">
                Ask me anything about quantum computing,
                quantum mechanics, qubits, quantum gates,
                algorithms, mathematics or advanced physics.
                <br><br>
                You can also upload files, use your microphone,
                connect a Drive link or open the Canvas workspace.
            </div>

        </div>
        """,
        unsafe_allow_html=True,
    )


# =========================================================
# CHAT MESSAGES
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
        <div class="canvas-container">

            <div style="
                font-family:'Space Grotesk';
                font-size:25px;
                font-weight:700;
                color:#e0e7ff;
            ">
                🎨 Canvas Workbench
            </div>

            <div style="
                color:#94a3b8;
                margin-top:8px;
                margin-bottom:15px;
            ">
                Create notes, equations, ideas and
                quantum computing explanations.
            </div>

        </div>
        """,
        unsafe_allow_html=True,
    )

    canvas_content = st.text_area(
        "Canvas workspace",
        placeholder=(
            "Write your notes, equations or ideas here..."
        ),
        height=250,
        key="canvas_content",
    )

    c1, c2 = st.columns(2)

    with c1:

        if st.button(
            "💾 Save Canvas",
            use_container_width=True
        ):

            st.success(
                "Canvas saved for this session."
            )

    with c2:

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
    '<div class="prompt-shell">',
    unsafe_allow_html=True,
)


# =========================================================
# FORM
#
# IMPORTANT:
# clear_on_submit=True
#
# This fixes:
# - text remaining after Send
# - Enter key submission
# =========================================================

with st.form(
    "quantum_prompt_form",
    clear_on_submit=True,
):

    # -----------------------------------------------------
    # PROMPT ROW
    # -----------------------------------------------------

    p1, p2, p3, p4 = st.columns(
        [0.08, 0.68, 0.10, 0.14],
        vertical_alignment="bottom"
    )


    # =====================================================
    # PLUS POPUP
    # =====================================================

    with p1:

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
                    margin-bottom:10px;
                ">
                    Tools & Attachments
                </div>
                """,
                unsafe_allow_html=True,
            )

            tab1, tab2, tab3 = st.tabs(
                [
                    "📁 Files",
                    "☁️ Drive",
                    "🛠️ More Tools"
                ]
            )

            # =============================================
            # FILES
            # =============================================

            with tab1:

                uploaded = st.file_uploader(
                    "Photos & Files",
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
                    key="file_upload",
                )

                if uploaded:

                    st.session_state.uploaded_files = uploaded

                    st.success(
                        f"{len(uploaded)} file(s) selected"
                    )

                    for file in uploaded:

                        st.caption(
                            f"📎 {file.name}"
                        )


            # =============================================
            # GOOGLE DRIVE
            # =============================================

            with tab2:

                st.markdown(
                    """
                    <div class="tool-card">
                        ☁️ <strong>Google Drive</strong><br>
                        <span style="color:#94a3b8;">
                        Paste a Google Drive share link.
                        </span>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

                drive_link = st.text_input(
                    "Drive link",
                    placeholder="https://drive.google.com/...",
                    key="drive_link_input",
                )

                if st.form_submit_button(
                    "Attach Drive Link"
                ):

                    if drive_link.strip():

                        st.session_state.drive_links.append(
                            drive_link.strip()
                        )

                        st.success(
                            "Drive link attached."
                        )

                    else:

                        st.warning(
                            "Please enter a Drive link."
                        )


            # =============================================
            # MORE TOOLS
            # =============================================

            with tab3:

                st.markdown(
                    "### 🛠️ More Tools"
                )

                if st.form_submit_button(
                    "🎨 Canvas"
                ):

                    st.session_state.show_canvas = True

                if st.form_submit_button(
                    "🧮 Quantum Calculator"
                ):

                    st.info(
                        "Quantum Calculator selected."
                    )

                if st.form_submit_button(
                    "📚 Learning Mode"
                ):

                    st.info(
                        "Learning Mode selected."
                    )

                if st.form_submit_button(
                    "📝 Notes"
                ):

                    st.info(
                        "Notes tool selected."
                    )


    # =====================================================
    # USER MESSAGE
    # =====================================================

    with p2:

        user_message = st.text_input(
            "Your message",
            placeholder=(
                "Ask your quantum question..."
            ),
            label_visibility="collapsed",
            key="message_input",
        )


    # =====================================================
    # MICROPHONE
    # =====================================================

    with p3:

        microphone = st.audio_input(
            "🎤",
            key="microphone_input",
            label_visibility="collapsed",
        )


    # =====================================================
    # SEND BUTTON
    # =====================================================

    with p4:

        st.markdown(
            '<div class="send-button">',
            unsafe_allow_html=True
        )

        send = st.form_submit_button(
            "➤ Send",
            use_container_width=True,
        )

        st.markdown(
            '</div>',
            unsafe_allow_html=True
        )


st.markdown(
    '</div>',
    unsafe_allow_html=True,
)


# =========================================================
# VOICE PROCESSING
# =========================================================

voice_question = ""

if microphone is not None:

    try:

        audio_bytes = microphone.getvalue()

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

                    audio_data = (
                        recognizer.record(source)
                    )

                voice_question = (
                    recognizer.recognize_google(
                        audio_data
                    )
                )

            else:

                st.warning(
                    "SpeechRecognition is not installed."
                )

    except sr.UnknownValueError:

        st.warning(
            "I could not understand your voice."
        )

    except Exception as e:

        st.warning(
            f"Voice processing error: {e}"
        )


# =========================================================
# DETERMINE QUESTION
# =========================================================

final_question = ""

# ---------------------------------------------------------
# Send button OR Enter key
#
# st.form_submit_button is triggered when:
# 1. User clicks Send
# 2. User presses Enter in the text input
# ---------------------------------------------------------

if send:

    if user_message.strip():

        final_question = (
            user_message.strip()
        )

    elif voice_question.strip():

        final_question = (
            voice_question.strip()
        )

    else:

        st.warning(
            "Please enter a question or use the microphone."
        )


# =========================================================
# SEND TO RAG ENGINE
# =========================================================

if final_question:

    # -----------------------------------------------------
    # Make sure a chat exists
    # -----------------------------------------------------

    if st.session_state.session_id is None:

        create_new_chat()


    # -----------------------------------------------------
    # Add user message
    # -----------------------------------------------------

    st.session_state.messages.append(
        {
            "role": "user",
            "content": final_question
        }
    )


    # -----------------------------------------------------
    # Generate answer
    # -----------------------------------------------------

    try:

        answer = answer_question(
            query=final_question,
            session_id=st.session_state.session_id,
            user_id=st.session_state.user_id,
        )

    except Exception as e:

        answer = (
            "⚠️ Unable to generate the answer.\n\n"
            f"Error: `{str(e)}`"
        )


    # -----------------------------------------------------
    # Add assistant message
    # -----------------------------------------------------

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": answer
        }
    )


    # -----------------------------------------------------
    # Rerun
    #
    # Because the form has clear_on_submit=True,
    # the text box will now be empty.
    # -----------------------------------------------------

    st.rerun()
    
