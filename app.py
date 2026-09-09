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
# RAG ENGINE IMPORTS
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
    "show_calculator": False,
    "show_notes": False,
    "learning_mode": False,

    "canvas_content": "",
    "notes_content": "",
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
   GOOGLE FONT
===================================================== */

@import url(
'https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Space+Grotesk:wght@500;600;700&display=swap'
);


/* =====================================================
   GLOBAL
===================================================== */

html,
body,
[class*="css"] {
    font-family: "Inter", sans-serif;
}

.stApp {
    background:
        radial-gradient(
            circle at 15% 20%,
            rgba(99,102,241,0.18),
            transparent 28%
        ),
        radial-gradient(
            circle at 85% 15%,
            rgba(59,130,246,0.14),
            transparent 25%
        ),
        radial-gradient(
            circle at 70% 80%,
            rgba(139,92,246,0.15),
            transparent 30%
        ),
        linear-gradient(
            135deg,
            #020617,
            #080b1e,
            #020617
        );

    min-height: 100vh;
}


/* =====================================================
   GRID BACKGROUND
===================================================== */

.stApp:before {

    content: "";

    position: fixed;

    inset: 0;

    pointer-events: none;

    background-image:

        linear-gradient(
            rgba(99,102,241,0.035) 1px,
            transparent 1px
        ),

        linear-gradient(
            90deg,
            rgba(99,102,241,0.035) 1px,
            transparent 1px
        );

    background-size: 55px 55px;

    z-index: 0;
}


/* =====================================================
   MAIN CONTENT
===================================================== */

.main .block-container {

    max-width: 1250px;

    padding-top: 2rem;

    padding-bottom: 7rem;

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
            #030712,
            #070b1c,
            #02040c
        );

    border-right:

        1px solid rgba(139,92,246,0.18);
}


section[data-testid="stSidebar"] .block-container {

    padding-top: 1.5rem;
}


/* Sidebar Buttons */

section[data-testid="stSidebar"] .stButton button {

    min-height: 43px;

    border-radius: 12px;

    border:

        1px solid rgba(139,92,246,0.18);

    background:

        linear-gradient(
            135deg,
            rgba(20,28,55,0.95),
            rgba(7,12,30,0.95)
        );

    color: #dbeafe;

    transition: 0.2s ease;
}


section[data-testid="stSidebar"] .stButton button:hover {

    border-color:

        rgba(167,139,250,0.7);

    transform:

        translateY(-1px);

    box-shadow:

        0 0 20px rgba(139,92,246,0.18);
}


/* =====================================================
   LOGIN PAGE
===================================================== */

.login-title {

    text-align: center;

    font-family: "Space Grotesk", sans-serif;

    font-size: clamp(40px, 6vw, 70px);

    font-weight: 700;

    letter-spacing: 4px;

    margin-bottom: 5px;

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


.login-subtitle {

    text-align: center;

    color: #94a3b8;

    font-size: 16px;

    line-height: 1.8;

    max-width: 650px;

    margin: 0 auto;
}


.login-feature {

    padding: 18px;

    border-radius: 18px;

    background:

        linear-gradient(
            135deg,
            rgba(15,23,42,0.8),
            rgba(10,15,35,0.8)
        );

    border:

        1px solid rgba(139,92,246,0.18);

    text-align: center;

    min-height: 120px;
}


/* =====================================================
   HEADER
===================================================== */

.quantum-logo {

    text-align: center;

    font-size: 70px;

    margin-bottom: 5px;

    animation:

        quantumPulse 3s ease-in-out infinite;

    text-shadow:

        0 0 12px #ffffff,

        0 0 30px rgba(139,92,246,1),

        0 0 55px rgba(59,130,246,0.8);
}


@keyframes quantumPulse {

    0%,
    100% {

        transform: scale(1);

    }

    50% {

        transform: scale(1.08);

    }
}


.main-title {

    text-align: center;

    font-family: "Space Grotesk", sans-serif;

    font-size: clamp(36px, 5vw, 60px);

    font-weight: 700;

    letter-spacing: 6px;

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


.subtitle {

    text-align: center;

    color: #94a3b8;

    margin-top: 10px;

    font-size: 15px;
}


.online-badge {

    width: fit-content;

    margin: 20px auto;

    padding: 7px 16px;

    border-radius: 50px;

    color: #86efac;

    font-size: 11px;

    font-weight: 700;

    letter-spacing: 1.5px;

    background:

        rgba(34,197,94,0.06);

    border:

        1px solid rgba(34,197,94,0.22);

    box-shadow:

        0 0 20px rgba(34,197,94,0.08);
}


/* =====================================================
   CHAT MESSAGE
===================================================== */

[data-testid="stChatMessage"] {

    border-radius: 18px;

    border:

        1px solid rgba(139,92,246,0.14);

    background:

        linear-gradient(
            135deg,
            rgba(15,23,42,0.82),
            rgba(7,12,28,0.82)
        );

    margin-bottom: 12px;

    box-shadow:

        0 8px 25px rgba(0,0,0,0.12);
}


/* =====================================================
   TOOL / WORKSPACE CARDS
===================================================== */

.workspace-card {

    padding: 24px;

    border-radius: 22px;

    margin-top: 20px;

    background:

        linear-gradient(
            135deg,
            rgba(15,23,42,0.92),
            rgba(8,12,30,0.92)
        );

    border:

        1px solid rgba(139,92,246,0.25);

    box-shadow:

        0 0 35px rgba(99,102,241,0.10);
}


/* =====================================================
   PROMPT CONTAINER
===================================================== */

.prompt-container {

    margin-top: 30px;

    padding: 12px;

    border-radius: 22px;

    background:

        linear-gradient(
            135deg,
            rgba(15,23,42,0.98),
            rgba(6,10,25,0.98)
        );

    border:

        1px solid rgba(139,92,246,0.32);

    box-shadow:

        0 0 35px rgba(99,102,241,0.13),

        inset 0 0 30px rgba(99,102,241,0.03);
}


.prompt-label {

    color: #818cf8;

    font-size: 11px;

    font-weight: 700;

    letter-spacing: 1.5px;

    margin-left: 8px;

    margin-bottom: 8px;
}


/* Prompt Input */

[data-testid="stTextInput"] input {

    background:

        rgba(15,23,42,0.65) !important;

    border:

        1px solid rgba(139,92,246,0.15) !important;

    border-radius: 14px !important;

    color: #f8fafc !important;

    min-height: 48px;
}


[data-testid="stTextInput"] input:focus {

    border-color:

        rgba(139,92,246,0.7) !important;

    box-shadow:

        0 0 15px rgba(139,92,246,0.15) !important;
}


/* Buttons inside prompt */

.prompt-container .stButton button {

    min-height: 48px;

    border-radius: 14px;

    font-weight: 600;

    border:

        1px solid rgba(139,92,246,0.25);

    background:

        linear-gradient(
            135deg,
            rgba(30,41,75,0.95),
            rgba(10,15,35,0.95)
        );

    color: #e0e7ff;
}


.prompt-container .stButton button:hover {

    border-color:

        rgba(167,139,250,0.75);

    box-shadow:

        0 0 20px rgba(139,92,246,0.18);
}


/* Send Button */

.send-button button {

    background:

        linear-gradient(
            135deg,
            #7c3aed,
            #2563eb
        ) !important;

    color: white !important;

    border:

        1px solid rgba(196,181,253,0.6) !important;

    box-shadow:

        0 0 20px rgba(99,102,241,0.25);
}


/* =====================================================
   POPOVER
===================================================== */

[data-testid="stPopoverBody"] {

    background:

        linear-gradient(
            135deg,
            #0b1024,
            #060a18
        );

    border:

        1px solid rgba(139,92,246,0.25);

    border-radius: 18px;
}


/* =====================================================
   STATUS CARD
===================================================== */

.status-card {

    padding: 12px;

    border-radius: 12px;

    background:

        rgba(99,102,241,0.08);

    border:

        1px solid rgba(99,102,241,0.18);

    color: #cbd5e1;

    font-size: 13px;
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

        st.session_state.sessions = get_user_sessions(
            st.session_state.user_id
        )


def start_new_chat():

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

    st.session_state.messages = []


def logout_user():

    st.session_state.logged_in = False

    st.session_state.user_email = ""

    st.session_state.user_id = None

    st.session_state.session_id = None

    st.session_state.messages = []

    st.session_state.sessions = []

    st.session_state.uploaded_files = []

    st.session_state.drive_links = []

    st.session_state.rename_session_id = None


def process_query(user_query):

    if not user_query:
        return

    if not st.session_state.logged_in:

        st.warning("Please log in first.")

        return

    # Automatically create chat

    if st.session_state.session_id is None:

        start_new_chat()

    # Add user message

    st.session_state.messages.append(
        {
            "role": "user",
            "content": user_query
        }
    )

    # Get AI answer

    try:

        answer = answer_question(
            query=user_query,
            session_id=st.session_state.session_id,
            user_id=st.session_state.user_id,
        )

    except Exception as e:

        answer = (
            "⚠️ **Something went wrong while generating the response.**\n\n"
            f"`{str(e)}`"
        )

    # Add assistant answer

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": answer
        }
    )


# =========================================================
# SIDEBAR
# =========================================================

with st.sidebar:

    st.markdown(
        "<div style='text-align:center;font-size:38px;'>⚛️</div>",
        unsafe_allow_html=True
    )

    st.markdown(
        """
        <div style="
            text-align:center;
            font-size:22px;
            font-weight:700;
            color:#e0e7ff;
            letter-spacing:1px;
        ">
            QUANTUM LAB
        </div>
        """,
        unsafe_allow_html=True
    )

    st.caption("AI-Powered Learning Environment")

    st.markdown("---")


    # =====================================================
    # LOGIN / USER AREA
    # =====================================================

    if not st.session_state.logged_in:

        st.subheader("🔐 Login")

        email = st.text_input(
            "Email",
            placeholder="student@example.com",
            key="login_email"
        )

        if st.button(
            "🚀 Enter Quantum Lab",
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
            <div class="status-card">
                👤 <b>Logged in as</b><br>
                {st.session_state.user_email}
            </div>
            """,
            unsafe_allow_html=True
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

        st.subheader("💬 Conversations")


        # NEW CHAT

        if st.button(
            "➕ New Chat",
            use_container_width=True
        ):

            start_new_chat()

            st.rerun()


        st.markdown(
            """
            <div style="
                color:#818cf8;
                font-size:11px;
                font-weight:700;
                letter-spacing:1.5px;
                margin-top:18px;
                margin-bottom:8px;
            ">
                CHAT HISTORY
            </div>
            """,
            unsafe_allow_html=True
        )


        refresh_sessions()


        # =================================================
        # CHAT HISTORY
        # =================================================

        if not st.session_state.sessions:

            st.caption("No conversations yet.")

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


                selected = (
                    session_id
                    == st.session_state.session_id
                )


                prefix = "🟣" if selected else "💬"


                chat_col, rename_col, delete_col = st.columns(
                    [0.62, 0.19, 0.19],
                    gap="small"
                )


                # -----------------------------------------
                # OPEN CHAT
                # -----------------------------------------

                with chat_col:

                    short_title = title

                    if len(short_title) > 18:

                        short_title = short_title[:18] + "..."

                    if st.button(
                        f"{prefix} {short_title}",
                        key=f"chat_{session_id}",
                        use_container_width=True
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
                # RENAME CHAT
                # -----------------------------------------

                with rename_col:

                    if st.button(
                        "✏️",
                        key=f"rename_{session_id}",
                        help="Rename Chat",
                        use_container_width=True
                    ):

                        st.session_state.rename_session_id = session_id

                        st.rerun()


                # -----------------------------------------
                # DELETE CHAT
                # -----------------------------------------

                with delete_col:

                    if st.button(
                        "🗑️",
                        key=f"delete_{session_id}",
                        help="Delete Chat",
                        use_container_width=True
                    ):

                        try:

                            delete_chat(session_id)

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
                # RENAME INPUT
                # -----------------------------------------

                if (
                    st.session_state.rename_session_id
                    == session_id
                ):

                    new_title = st.text_input(
                        "Rename chat",
                        value=title,
                        key=f"rename_input_{session_id}"
                    )

                    save_col, cancel_col = st.columns(2)


                    with save_col:

                        if st.button(
                            "Save",
                            key=f"save_{session_id}",
                            use_container_width=True
                        ):

                            if new_title.strip():

                                rename_chat(
                                    session_id,
                                    new_title.strip()
                                )

                            st.session_state.rename_session_id = None

                            refresh_sessions()

                            st.rerun()


                    with cancel_col:

                        if st.button(
                            "Cancel",
                            key=f"cancel_{session_id}",
                            use_container_width=True
                        ):

                            st.session_state.rename_session_id = None

                            st.rerun()


        # =================================================
        # CLEAR CONVERSATION
        # =================================================

        st.markdown("---")

        if st.button(
            "🧹 Clear Current Conversation",
            use_container_width=True
        ):

            clear_current_chat()

            st.rerun()


# =========================================================
# LOGIN SCREEN
# =========================================================

if not st.session_state.logged_in:

    st.markdown("<br><br>", unsafe_allow_html=True)

    st.markdown(
        '<div class="quantum-logo">⚛️</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="login-title">QUANTUM LAB</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        """
        <div class="login-subtitle">
            Your intelligent learning companion for Quantum Computing,
            Advanced Physics and AI-powered exploration.
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown("<br><br>", unsafe_allow_html=True)

    feature1, feature2, feature3 = st.columns(3)

    with feature1:

        st.markdown(
            """
            <div class="login-feature">
                <div style="font-size:30px;">🤖</div>
                <b style="color:#e0e7ff;">AI Tutor</b>
                <br>
                <span style="color:#94a3b8;font-size:13px;">
                    Intelligent explanations
                </span>
            </div>
            """,
            unsafe_allow_html=True
        )

    with feature2:

        st.markdown(
            """
            <div class="login-feature">
                <div style="font-size:30px;">📚</div>
                <b style="color:#e0e7ff;">Smart Learning</b>
                <br>
                <span style="color:#94a3b8;font-size:13px;">
                    Learn complex concepts
                </span>
            </div>
            """,
            unsafe_allow_html=True
        )

    with feature3:

        st.markdown(
            """
            <div class="login-feature">
                <div style="font-size:30px;">🎤</div>
                <b style="color:#e0e7ff;">Interactive Tools</b>
                <br>
                <span style="color:#94a3b8;font-size:13px;">
                    Files, voice and workspace
                </span>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.markdown("<br>", unsafe_allow_html=True)

    st.info(
        "👈 Enter your email in the sidebar to enter Quantum Lab."
    )

    st.stop()


# =========================================================
# MAIN PAGE HEADER
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
        Your AI-powered Quantum Computing and Advanced Physics Tutor
    </div>
    """,
    unsafe_allow_html=True
)

st.markdown(
    '<div class="online-badge">● AI TUTOR ONLINE</div>',
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
            margin-bottom:18px;
        ">
            💬 {current_title}
        </div>
        """,
        unsafe_allow_html=True
    )


# =========================================================
# DISPLAY CHAT
# =========================================================

for message in st.session_state.messages:

    with st.chat_message(message["role"]):

        st.markdown(message["content"])


# =========================================================
# CANVAS WORKSPACE
# =========================================================

if st.session_state.show_canvas:

    st.markdown(
        """
        <div class="workspace-card">

        <h3 style="color:#e0e7ff;">
        🎨 Quantum Canvas
        </h3>

        <p style="color:#94a3b8;">
        Use this workspace for equations, ideas,
        quantum circuits and study notes.
        </p>

        </div>
        """,
        unsafe_allow_html=True
    )

    st.session_state.canvas_content = st.text_area(
        "Canvas Workspace",
        value=st.session_state.canvas_content,
        placeholder=(
            "Write equations, notes, ideas or "
            "quantum computing concepts here..."
        ),
        height=250
    )

    canvas_save, canvas_close = st.columns(2)

    with canvas_save:

        if st.button(
            "💾 Save Canvas",
            use_container_width=True
        ):

            st.success(
                "Canvas saved for this session!"
            )

    with canvas_close:

        if st.button(
            "✖ Close Canvas",
            use_container_width=True
        ):

            st.session_state.show_canvas = False

            st.rerun()


# =========================================================
# QUANTUM CALCULATOR
# =========================================================

if st.session_state.show_calculator:

    st.markdown(
        """
        <div class="workspace-card">

        <h3 style="color:#e0e7ff;">
        🧮 Quantum Calculator
        </h3>

        <p style="color:#94a3b8;">
        Enter a mathematical expression.
        </p>

        </div>
        """,
        unsafe_allow_html=True
    )

    calc_input = st.text_input(
        "Expression",
        placeholder="Example: 2 * (5 + 10)"
    )

    calc_col1, calc_col2 = st.columns(2)

    with calc_col1:

        if st.button(
            "Calculate",
            use_container_width=True
        ):

            try:

                result = eval(
                    calc_input,
                    {
                        "__builtins__": {}
                    }
                )

                st.success(
                    f"Result: {result}"
                )

            except Exception:

                st.error(
                    "Invalid mathematical expression."
                )

    with calc_col2:

        if st.button(
            "Close Calculator",
            use_container_width=True
        ):

            st.session_state.show_calculator = False

            st.rerun()


# =========================================================
# NOTES
# =========================================================

if st.session_state.show_notes:

    st.markdown(
        """
        <div class="workspace-card">

        <h3 style="color:#e0e7ff;">
        📝 Study Notes
        </h3>

        <p style="color:#94a3b8;">
        Save quick notes while learning.
        </p>

        </div>
        """,
        unsafe_allow_html=True
    )

    st.session_state.notes_content = st.text_area(
        "My Notes",
        value=st.session_state.notes_content,
        height=220
    )

    notes_col1, notes_col2 = st.columns(2)

    with notes_col1:

        if st.button(
            "💾 Save Notes",
            use_container_width=True
        ):

            st.success(
                "Notes saved for this session!"
            )

    with notes_col2:

        if st.button(
            "✖ Close Notes",
            use_container_width=True
        ):

            st.session_state.show_notes = False

            st.rerun()


# =========================================================
# PROMPT AREA
# =========================================================

st.markdown(
    '<div class="prompt-container">',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="prompt-label">ASK QUANTUM AI</div>',
    unsafe_allow_html=True
)


prompt_col1, prompt_col2, prompt_col3, prompt_col4 = st.columns(
    [0.08, 0.70, 0.08, 0.14],
    vertical_alignment="center"
)


# =========================================================
# + BUTTON AND POPUP
# =========================================================

with prompt_col1:

    with st.popover(
        "＋",
        use_container_width=True
    ):

        st.markdown(
            "### ✨ Add to your question"
        )


        tab1, tab2, tab3 = st.tabs(
            [
                "📁 Files",
                "☁️ Drive",
                "🛠️ Tools"
            ]
        )


        # -------------------------------------------------
        # FILES
        # -------------------------------------------------

        with tab1:

            uploaded = st.file_uploader(
                "Upload photos or documents",
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
                    "cpp"
                ],
                accept_multiple_files=True,
                key="quantum_files"
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

            drive_url = st.text_input(
                "Google Drive Link",
                placeholder="Paste Drive link here...",
                key="drive_link_input"
            )

            if st.button(
                "Attach Drive Link",
                use_container_width=True
            ):

                if drive_url.strip():

                    if (
                        drive_url.strip()
                        not in st.session_state.drive_links
                    ):

                        st.session_state.drive_links.append(
                            drive_url.strip()
                        )

                    st.success(
                        "Drive file attached!"
                    )

                else:

                    st.warning(
                        "Paste a Google Drive link first."
                    )


        # -------------------------------------------------
        # MORE TOOLS
        # -------------------------------------------------

        with tab3:

            if st.button(
                "🎨 Open Canvas",
                use_container_width=True
            ):

                st.session_state.show_canvas = True

                st.rerun()


            if st.button(
                "🧮 Quantum Calculator",
                use_container_width=True
            ):

                st.session_state.show_calculator = True

                st.rerun()


            if st.button(
                "📚 Learning Mode",
                use_container_width=True
            ):

                st.session_state.learning_mode = (
                    not st.session_state.learning_mode
                )

                if st.session_state.learning_mode:

                    st.success(
                        "Learning Mode ON 📚"
                    )

                else:

                    st.info(
                        "Learning Mode OFF"
                    )


            if st.button(
                "📝 Notes",
                use_container_width=True
            ):

                st.session_state.show_notes = True

                st.rerun()


# =========================================================
# USER INPUT
# =========================================================

with prompt_col2:

    user_prompt = st.text_input(
        "Message",
        placeholder=(
            "Ask anything about quantum computing..."
        ),
        label_visibility="collapsed",
        key="custom_prompt"
    )


# =========================================================
# MICROPHONE
# =========================================================

with prompt_col3:

    audio_value = st.audio_input(
        "🎤",
        label_visibility="collapsed",
        key="quantum_microphone"
    )


# =========================================================
# SEND BUTTON
# =========================================================

with prompt_col4:

    st.markdown(
        '<div class="send-button">',
        unsafe_allow_html=True
    )

    send_clicked = st.button(
        "➤ Send",
        use_container_width=True
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
# ATTACHED FILE DISPLAY
# =========================================================

if st.session_state.uploaded_files:

    with st.expander(
        "📎 Attached Files",
        expanded=False
    ):

        for file in st.session_state.uploaded_files:

            st.write(
                f"• {file.name}"
            )


if st.session_state.drive_links:

    with st.expander(
        "☁️ Google Drive Files",
        expanded=False
    ):

        for link in st.session_state.drive_links:

            st.write(
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

            st.session_state.processed_audio_hash = audio_hash


            if SPEECH_RECOGNITION_AVAILABLE:

                recognizer = sr.Recognizer()

                audio_stream = io.BytesIO(
                    audio_bytes
                )

                with sr.AudioFile(
                    audio_stream
                ) as source:

                    recorded_audio = recognizer.record(
                        source
                    )


                voice_query = recognizer.recognize_google(
                    recorded_audio
                )


                if voice_query:

                    st.success(
                        f"🎤 Recognized: {voice_query}"
                    )


            else:

                st.warning(
                    "Install SpeechRecognition to use "
                    "voice transcription."
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
# EXECUTE AI
# =========================================================

if final_query:

    if st.session_state.learning_mode:

        final_query = (
            "Explain this in Learning Mode. "
            "Give a clear concept explanation, "
            "an example, and a short summary.\n\n"
            + final_query
        )


    process_query(final_query)


    st.session_state.custom_prompt = ""


    st.rerun()
