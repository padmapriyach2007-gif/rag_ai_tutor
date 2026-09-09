import io
import hashlib
import ast
import operator as op

import streamlit as st


# =========================================================
# OPTIONAL SPEECH RECOGNITION
# =========================================================

try:
    import speech_recognition as sr
    SPEECH_RECOGNITION_AVAILABLE = True
except ImportError:
    sr = None
    SPEECH_RECOGNITION_AVAILABLE = False


# =========================================================
# EXISTING RAG ENGINE
# DO NOT CHANGE THESE IMPORTS
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

DEFAULTS = {
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

    "calculator_result": None,

    # Used to show a temporary message
    "tool_message": "",
}


for key, value in DEFAULTS.items():

    if key not in st.session_state:

        st.session_state[key] = value


# =========================================================
# CUSTOM CSS
# =========================================================

st.markdown(
    """
<style>

/* =====================================================
   FONTS
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

    min-height: 100vh;

    background:

        radial-gradient(
            circle at 10% 15%,
            rgba(99,102,241,0.20),
            transparent 28%
        ),

        radial-gradient(
            circle at 90% 10%,
            rgba(59,130,246,0.15),
            transparent 27%
        ),

        radial-gradient(
            circle at 75% 80%,
            rgba(139,92,246,0.16),
            transparent 30%
        ),

        linear-gradient(
            135deg,
            #020617 0%,
            #080b22 48%,
            #020617 100%
        );

}


/* =====================================================
   GRID
===================================================== */

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


/* =====================================================
   MAIN
===================================================== */

.main .block-container {

    max-width: 1250px;

    padding-top: 1.5rem;

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
            #030611,
            #070b1d,
            #02040c
        );

    border-right:

        1px solid rgba(139,92,246,0.20);

}


section[data-testid="stSidebar"] .stButton button {

    border-radius: 12px;

    border:

        1px solid rgba(139,92,246,0.16);

    background:

        linear-gradient(
            135deg,
            rgba(18,25,53,0.96),
            rgba(7,12,29,0.96)
        );

    color: #dbeafe;

    transition: all 0.2s ease;

}


section[data-testid="stSidebar"] .stButton button:hover {

    border-color:

        rgba(167,139,250,0.65);

    box-shadow:

        0 0 22px rgba(139,92,246,0.18);

    transform:

        translateY(-1px);

}


/* =====================================================
   LOGO
===================================================== */

.quantum-logo {

    text-align: center;

    font-size: 70px;

    line-height: 1;

    margin: 12px auto;

    text-shadow:

        0 0 10px #ffffff,

        0 0 25px rgba(139,92,246,1),

        0 0 50px rgba(59,130,246,0.9);

    animation:

        quantumPulse 3s ease-in-out infinite;

}


@keyframes quantumPulse {

    0%,
    100% {

        transform: scale(1);

        filter: brightness(1);

    }

    50% {

        transform: scale(1.07);

        filter: brightness(1.2);

    }

}


/* =====================================================
   MAIN TITLE
===================================================== */

.main-title {

    text-align: center;

    font-family: "Space Grotesk", sans-serif;

    font-size:

        clamp(38px, 5vw, 60px);

    font-weight: 700;

    letter-spacing: 6px;

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

    max-width: 800px;

    margin: 10px auto;

    color: #94a3b8;

    font-size: 15px;

    line-height: 1.8;

}


.online-badge {

    width: fit-content;

    margin: 18px auto;

    padding: 7px 16px;

    border-radius: 999px;

    color: #86efac;

    background:

        rgba(34,197,94,0.06);

    border:

        1px solid rgba(34,197,94,0.22);

    font-size: 10px;

    font-weight: 700;

    letter-spacing: 1.6px;

}


/* =====================================================
   CHAT
===================================================== */

[data-testid="stChatMessage"] {

    border-radius: 18px;

    border:

        1px solid rgba(139,92,246,0.12);

    background:

        linear-gradient(
            135deg,
            rgba(15,23,42,0.84),
            rgba(7,12,28,0.84)
        );

    margin-bottom: 12px;

    box-shadow:

        0 8px 30px rgba(0,0,0,0.12);

}


[data-testid="stChatMessage"] p {

    color: #dbe4f0;

    line-height: 1.75;

}


/* =====================================================
   LOGIN
===================================================== */

.login-title {

    text-align: center;

    font-family: "Space Grotesk", sans-serif;

    font-size:

        clamp(40px, 6vw, 70px);

    font-weight: 700;

    letter-spacing: 5px;

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

    max-width: 680px;

    margin: auto;

    color: #94a3b8;

    font-size: 15px;

    line-height: 1.8;

}


.feature-card {

    padding: 20px;

    min-height: 125px;

    text-align: center;

    border-radius: 18px;

    background:

        linear-gradient(
            135deg,
            rgba(15,23,42,0.80),
            rgba(7,12,28,0.80)
        );

    border:

        1px solid rgba(139,92,246,0.18);

}


/* =====================================================
   STATUS
===================================================== */

.status-card {

    padding: 12px;

    border-radius: 12px;

    background:

        rgba(99,102,241,0.08);

    border:

        1px solid rgba(99,102,241,0.20);

    color: #cbd5e1;

    font-size: 13px;

}


/* =====================================================
   WORKSPACE
===================================================== */

.workspace {

    padding: 25px;

    margin-top: 20px;

    border-radius: 22px;

    background:

        linear-gradient(
            135deg,
            rgba(15,23,42,0.94),
            rgba(8,12,30,0.94)
        );

    border:

        1px solid rgba(139,92,246,0.25);

    box-shadow:

        0 0 40px rgba(99,102,241,0.10);

}


/* =====================================================
   PROMPT
===================================================== */

.prompt-box {

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

        0 0 35px rgba(99,102,241,0.12);

}


.prompt-label {

    color: #818cf8;

    font-size: 10px;

    font-weight: 700;

    letter-spacing: 1.6px;

    margin-left: 8px;

    margin-bottom: 8px;

}


/* =====================================================
   INPUT
===================================================== */

[data-testid="stTextInput"] input {

    background:

        rgba(15,23,42,0.72) !important;

    border:

        1px solid rgba(139,92,246,0.18) !important;

    border-radius: 14px !important;

    color: #f8fafc !important;

    min-height: 48px !important;

}


[data-testid="stTextInput"] input:focus {

    border-color:

        rgba(139,92,246,0.75) !important;

    box-shadow:

        0 0 18px rgba(139,92,246,0.16) !important;

}


/* =====================================================
   PROMPT BUTTONS
===================================================== */

.prompt-box .stButton button {

    min-height: 48px;

    border-radius: 14px;

    border:

        1px solid rgba(139,92,246,0.25);

    background:

        linear-gradient(
            135deg,
            rgba(30,41,75,0.96),
            rgba(10,15,35,0.96)
        );

    color: #dbeafe;

}


.prompt-box .stButton button:hover {

    border-color:

        rgba(167,139,250,0.75);

    box-shadow:

        0 0 20px rgba(99,102,241,0.20);

}


/* =====================================================
   SEND
===================================================== */

.send-button button {

    background:

        linear-gradient(
            135deg,
            #7c3aed,
            #2563eb
        ) !important;

    color: white !important;

    border:

        1px solid rgba(196,181,253,0.60) !important;

    box-shadow:

        0 0 22px rgba(99,102,241,0.28);

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

}


/* =====================================================
   FILES
===================================================== */

.file-card {

    padding: 10px 12px;

    margin: 5px 0;

    border-radius: 10px;

    background:

        rgba(99,102,241,0.07);

    border:

        1px solid rgba(99,102,241,0.13);

    color: #cbd5e1;

}


/* =====================================================
   DIVIDER
===================================================== */

.quantum-divider {

    width: 240px;

    height: 1px;

    margin: 0 auto 25px auto;

    background:

        linear-gradient(
            90deg,
            transparent,
            #8b5cf6,
            #3b82f6,
            transparent
        );

    box-shadow:

        0 0 15px rgba(139,92,246,0.45);

}

</style>
""",
    unsafe_allow_html=True,
)


# =========================================================
# HELPER FUNCTIONS
# =========================================================

def refresh_sessions():

    if not st.session_state.user_id:
        return

    try:

        st.session_state.sessions = get_user_sessions(
            st.session_state.user_id
        )

    except Exception as e:

        st.error(
            f"Unable to load chats: {e}"
        )


def start_new_chat():

    if not st.session_state.logged_in:
        return

    try:

        new_session_id = create_chat_session(
            st.session_state.user_id,
            "New Chat"
        )

        st.session_state.session_id = new_session_id

        st.session_state.messages = []

        refresh_sessions()

    except Exception as e:

        st.error(
            f"Unable to create chat: {e}"
        )


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

    st.session_state.show_canvas = False

    st.session_state.show_calculator = False

    st.session_state.show_notes = False

    st.session_state.learning_mode = False


def process_query(user_query):

    if not user_query.strip():
        return

    if not st.session_state.logged_in:

        st.warning(
            "Please log in first."
        )

        return


    # Create chat automatically

    if st.session_state.session_id is None:

        start_new_chat()


    # User message

    st.session_state.messages.append(
        {
            "role": "user",
            "content": user_query
        }
    )


    # AI response

    try:

        answer = answer_question(
            query=user_query,
            session_id=st.session_state.session_id,
            user_id=st.session_state.user_id,
        )

    except Exception as e:

        answer = (
            "⚠️ **I couldn't generate the answer right now.**\n\n"
            f"Error: `{str(e)}`"
        )


    # Assistant message

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": answer
        }
    )


# =========================================================
# SAFE CALCULATOR
# =========================================================

ALLOWED_OPERATORS = {
    ast.Add: op.add,
    ast.Sub: op.sub,
    ast.Mult: op.mul,
    ast.Div: op.truediv,
    ast.Pow: op.pow,
    ast.Mod: op.mod,
    ast.USub: op.neg,
    ast.UAdd: op.pos,
}


def safe_calculate(expression):

    def evaluate(node):

        if isinstance(node, ast.Constant):

            if isinstance(node.value, (int, float)):

                return node.value

            raise ValueError("Invalid value")


        if isinstance(node, ast.BinOp):

            operator_type = type(node.op)

            if operator_type not in ALLOWED_OPERATORS:

                raise ValueError(
                    "Operator not allowed"
                )

            left = evaluate(node.left)

            right = evaluate(node.right)

            return ALLOWED_OPERATORS[
                operator_type
            ](
                left,
                right
            )


        if isinstance(node, ast.UnaryOp):

            operator_type = type(node.op)

            if operator_type not in ALLOWED_OPERATORS:

                raise ValueError(
                    "Operator not allowed"
                )

            return ALLOWED_OPERATORS[
                operator_type
            ](
                evaluate(node.operand)
            )


        raise ValueError(
            "Invalid mathematical expression"
        )


    tree = ast.parse(
        expression,
        mode="eval"
    )

    return evaluate(tree.body)


# =========================================================
# SIDEBAR
# =========================================================

with st.sidebar:

    # -----------------------------------------------------
    # LOGO
    # -----------------------------------------------------

    st.markdown(
        """
        <div style="
            text-align:center;
            font-size:40px;
            margin-bottom:5px;
        ">
            ⚛️
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        """
        <div style="
            text-align:center;
            font-family:'Space Grotesk';
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

    st.markdown(
        """
        <div style="
            text-align:center;
            color:#64748b;
            font-size:11px;
            margin-top:5px;
        ">
            AI POWERED LEARNING
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown("---")


    # =====================================================
    # LOGIN
    # =====================================================

    if not st.session_state.logged_in:

        st.subheader("🔐 Account")

        email = st.text_input(
            "Email",
            placeholder="student@example.com",
            key="login_email"
        )


        if st.button(
            "🚀 Enter Quantum Lab",
            use_container_width=True
        ):

            email_value = email.strip()


            if not email_value:

                st.warning(
                    "Please enter your email."
                )

            else:

                try:

                    user_id = get_or_create_user(
                        email_value
                    )

                    st.session_state.user_email = (
                        email_value
                    )

                    st.session_state.user_id = user_id

                    st.session_state.logged_in = True

                    refresh_sessions()

                    st.rerun()


                except Exception as e:

                    st.error(
                        f"Login failed: {e}"
                    )


    # =====================================================
    # LOGGED-IN USER
    # =====================================================

    else:

        st.markdown(
            f"""
            <div class="status-card">

                👤 <b>Logged in as</b>

                <br><br>

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
    # CHAT SECTION
    # =====================================================

    if st.session_state.logged_in:

        st.markdown("---")

        st.subheader("💬 Chats")


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
                font-size:10px;
                font-weight:700;
                letter-spacing:1.5px;
                margin:18px 0 8px 0;
            ">
                CHAT HISTORY
            </div>
            """,
            unsafe_allow_html=True
        )


        refresh_sessions()


        # =================================================
        # NO CHATS
        # =================================================

        if not st.session_state.sessions:

            st.caption(
                "No conversations yet."
            )


        # =================================================
        # CHAT LIST
        # =================================================

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


                prefix = (
                    "🟣"
                    if selected
                    else "💬"
                )


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

                        short_title = (
                            short_title[:18]
                            + "..."
                        )


                    if st.button(
                        f"{prefix} {short_title}",
                        key=f"chat_{session_id}",
                        use_container_width=True
                    ):

                        st.session_state.session_id = (
                            session_id
                        )


                        try:

                            st.session_state.messages = (
                                restore_chat(
                                    session_id
                                )
                            )

                        except Exception:

                            st.session_state.messages = []


                        st.rerun()


                # -----------------------------------------
                # RENAME
                # -----------------------------------------

                with rename_col:

                    if st.button(
                        "✏️",
                        key=f"rename_{session_id}",
                        help="Rename chat",
                        use_container_width=True
                    ):

                        st.session_state.rename_session_id = (
                            session_id
                        )

                        st.rerun()


                # -----------------------------------------
                # DELETE
                # -----------------------------------------

                with delete_col:

                    if st.button(
                        "🗑️",
                        key=f"delete_{session_id}",
                        help="Delete chat",
                        use_container_width=True
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
                        "New chat name",
                        value=title,
                        key=f"title_input_{session_id}"
                    )


                    rename_save, rename_cancel = st.columns(2)


                    with rename_save:

                        if st.button(
                            "Save",
                            key=f"save_{session_id}",
                            use_container_width=True
                        ):

                            if new_title.strip():

                                try:

                                    rename_chat(
                                        session_id,
                                        new_title.strip()
                                    )

                                except Exception as e:

                                    st.error(
                                        f"Rename failed: {e}"
                                    )


                            st.session_state.rename_session_id = None

                            refresh_sessions()

                            st.rerun()


                    with rename_cancel:

                        if st.button(
                            "Cancel",
                            key=f"cancel_{session_id}",
                            use_container_width=True
                        ):

                            st.session_state.rename_session_id = None

                            st.rerun()


        # =================================================
        # CLEAR
        # =================================================

        st.markdown("---")


        if st.button(
            "🧹 Clear Conversation",
            use_container_width=True
        ):

            clear_current_chat()

            st.rerun()


        # =================================================
        # CHAT ID
        # =================================================

        if st.session_state.session_id:

            st.caption(
                f"Chat ID: {st.session_state.session_id}"
            )


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

            Your intelligent AI learning companion for

            <b style="color:#c4b5fd;">
                Quantum Computing
            </b>

            and

            <b style="color:#93c5fd;">
                Advanced Physics
            </b>.

        </div>
        """,
        unsafe_allow_html=True
    )


    st.markdown(
        "<br><br>",
        unsafe_allow_html=True
    )


    # Feature cards

    c1, c2, c3 = st.columns(3)


    with c1:

        st.markdown(
            """
            <div class="feature-card">

                <div style="font-size:32px;">
                    🤖
                </div>

                <b style="color:#e0e7ff;">
                    AI Tutor
                </b>

                <br>

                <span style="
                    color:#94a3b8;
                    font-size:12px;
                ">
                    Intelligent explanations
                </span>

            </div>
            """,
            unsafe_allow_html=True
        )


    with c2:

        st.markdown(
            """
            <div class="feature-card">

                <div style="font-size:32px;">
                    📚
                </div>

                <b style="color:#e0e7ff;">
                    Smart Learning
                </b>

                <br>

                <span style="
                    color:#94a3b8;
                    font-size:12px;
                ">
                    Learn complex concepts
                </span>

            </div>
            """,
            unsafe_allow_html=True
        )


    with c3:

        st.markdown(
            """
            <div class="feature-card">

                <div style="font-size:32px;">
                    ⚛️
                </div>

                <b style="color:#e0e7ff;">
                    Quantum Tools
                </b>

                <br>

                <span style="
                    color:#94a3b8;
                    font-size:12px;
                ">
                    Interactive workspace
                </span>

            </div>
            """,
            unsafe_allow_html=True
        )


    st.markdown(
        "<br>",
        unsafe_allow_html=True
    )


    st.info(
        "🔐 Enter your email in the sidebar to start learning."
    )


    st.stop()


# =========================================================
# MAIN HEADER
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

        Interactive AI Tutor for

        <b style="color:#c4b5fd;">
            Quantum Computing
        </b>

        &

        <b style="color:#93c5fd;">
            Advanced Physics
        </b>

    </div>
    """,
    unsafe_allow_html=True
)


st.markdown(
    '<div class="online-badge">● AI TUTOR ONLINE</div>',
    unsafe_allow_html=True
)


st.markdown(
    '<div class="quantum-divider"></div>',
    unsafe_allow_html=True
)


# =========================================================
# CURRENT CHAT TITLE
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
            margin-bottom:20px;
        ">
            💬 {current_title}
        </div>
        """,
        unsafe_allow_html=True
    )


# =========================================================
# LEARNING MODE STATUS
# =========================================================

if st.session_state.learning_mode:

    st.success(
        "📚 Learning Mode is ON — "
        "answers will include explanations and examples."
    )


# =========================================================
# CHAT DISPLAY
# =========================================================

for message in st.session_state.messages:

    with st.chat_message(
        message["role"]
    ):

        st.markdown(
            message["content"]
        )


# =========================================================
# CANVAS
# =========================================================

if st.session_state.show_canvas:

    st.markdown(
        """
        <div class="workspace">

            <h2 style="color:#e0e7ff;">
                🎨 Quantum Canvas
            </h2>

            <p style="color:#94a3b8;">
                Write equations, concepts, ideas,
                diagrams or study notes.
            </p>

        </div>
        """,
        unsafe_allow_html=True
    )


    st.session_state.canvas_content = st.text_area(
        "Canvas",
        value=st.session_state.canvas_content,
        placeholder=(
            "Start writing your quantum notes..."
        ),
        height=250,
        key="canvas_editor"
    )


    save_canvas, close_canvas = st.columns(2)


    with save_canvas:

        if st.button(
            "💾 Save Canvas",
            use_container_width=True
        ):

            st.success(
                "Canvas saved for this session."
            )


    with close_canvas:

        if st.button(
            "✖ Close Canvas",
            use_container_width=True
        ):

            st.session_state.show_canvas = False

            st.rerun()


# =========================================================
# CALCULATOR
# =========================================================

if st.session_state.show_calculator:

    st.markdown(
        """
        <div class="workspace">

            <h2 style="color:#e0e7ff;">
                🧮 Quantum Calculator
            </h2>

            <p style="color:#94a3b8;">
                Perform basic mathematical calculations.
            </p>

        </div>
        """,
        unsafe_allow_html=True
    )


    calculator_input = st.text_input(
        "Expression",
        placeholder="Example: 2 * (5 + 10)",
        key="calculator_input"
    )


    calc1, calc2 = st.columns(2)


    with calc1:

        if st.button(
            "🧮 Calculate",
            use_container_width=True
        ):

            try:

                result = safe_calculate(
                    calculator_input
                )

                st.session_state.calculator_result = result

                st.success(
                    f"Result: {result}"
                )

            except Exception:

                st.error(
                    "Invalid mathematical expression."
                )


    with calc2:

        if st.button(
            "✖ Close Calculator",
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
        <div class="workspace">

            <h2 style="color:#e0e7ff;">
                📝 Study Notes
            </h2>

            <p style="color:#94a3b8;">
                Write and save your learning notes.
            </p>

        </div>
        """,
        unsafe_allow_html=True
    )


    st.session_state.notes_content = st.text_area(
        "My Notes",
        value=st.session_state.notes_content,
        height=220,
        key="notes_editor"
    )


    notes1, notes2 = st.columns(2)


    with notes1:

        if st.button(
            "💾 Save Notes",
            use_container_width=True
        ):

            st.success(
                "Notes saved for this session."
            )


    with notes2:

        if st.button(
            "✖ Close Notes",
            use_container_width=True
        ):

            st.session_state.show_notes = False

            st.rerun()


# =========================================================
# PROMPT CONTAINER
# =========================================================

st.markdown(
    '<div class="prompt-box">',
    unsafe_allow_html=True
)


st.markdown(
    '<div class="prompt-label">ASK YOUR QUANTUM AI TUTOR</div>',
    unsafe_allow_html=True
)


# =========================================================
# PROMPT COLUMNS
# =========================================================

prompt_col1, prompt_col2, prompt_col3, prompt_col4 = st.columns(
    [0.08, 0.69, 0.08, 0.15],
    vertical_alignment="center"
)


# =========================================================
# PLUS POPUP
# =========================================================

with prompt_col1:

    with st.popover(
        "＋",
        use_container_width=True
    ):

        st.markdown(
            """
            <h3 style="color:#e0e7ff;">
                ✨ Add to your question
            </h3>
            """,
            unsafe_allow_html=True
        )


        tab_files, tab_drive, tab_tools = st.tabs(
            [
                "📁 Photos & Files",
                "☁️ Drive",
                "🛠️ More Tools"
            ]
        )


        # =================================================
        # FILES
        # =================================================

        with tab_files:

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
                    "cpp"
                ],
                accept_multiple_files=True,
                key="quantum_attachments"
            )


            if uploaded:

                st.session_state.uploaded_files = uploaded


                st.success(
                    f"{len(uploaded)} file(s) attached."
                )


                for file in uploaded:

                    st.markdown(
                        f"""
                        <div class="file-card">
                            📎 {file.name}
                        </div>
                        """,
                        unsafe_allow_html=True
                    )


        # =================================================
        # GOOGLE DRIVE
        # =================================================

        with tab_drive:

            st.markdown(
                """
                <p style="color:#94a3b8;">
                    Paste a Google Drive file link.
                </p>
                """,
                unsafe_allow_html=True
            )


            drive_url = st.text_input(
                "Google Drive Link",
                placeholder="https://drive.google.com/...",
                key="drive_url"
            )


            if st.button(
                "☁️ Attach Drive File",
                use_container_width=True
            ):

                clean_url = drive_url.strip()


                if clean_url:

                    if (
                        clean_url
                        not in st.session_state.drive_links
                    ):

                        st.session_state.drive_links.append(
                            clean_url
                        )


                    st.success(
                        "Google Drive link attached."
                    )

                else:

                    st.warning(
                        "Please paste a Drive link."
                    )


        # =================================================
        # MORE TOOLS
        # =================================================

        with tab_tools:

            st.markdown(
                "### 🛠️ More Tools"
            )


            # Canvas

            if st.button(
                "🎨 Canvas",
                use_container_width=True
            ):

                st.session_state.show_canvas = True

                st.rerun()


            # Calculator

            if st.button(
                "🧮 Quantum Calculator",
                use_container_width=True
            ):

                st.session_state.show_calculator = True

                st.rerun()


            # Learning Mode

            if st.button(
                "📚 Learning Mode",
                use_container_width=True
            ):

                st.session_state.learning_mode = (
                    not st.session_state.learning_mode
                )

                st.rerun()


            # Notes

            if st.button(
                "📝 Notes",
                use_container_width=True
            ):

                st.session_state.show_notes = True

                st.rerun()


# =========================================================
# TEXT PROMPT
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
# SEND
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
# SHOW ATTACHED FILES
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


# =========================================================
# SHOW DRIVE FILES
# =========================================================

if st.session_state.drive_links:

    with st.expander(
        "☁️ Attached Drive Files",
        expanded=False
    ):

        for link in st.session_state.drive_links:

            st.write(
                f"• {link}"
            )


# =========================================================
# MICROPHONE TRANSCRIPTION
# =========================================================

voice_query = ""


if audio_value is not None:

    try:

        audio_bytes = audio_value.getvalue()


        if audio_bytes:

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


                if not SPEECH_RECOGNITION_AVAILABLE:

                    st.warning(
                        "Microphone transcription requires "
                        "SpeechRecognition."
                    )

                else:

                    recognizer = sr.Recognizer()


                    audio_stream = io.BytesIO(
                        audio_bytes
                    )


                    with sr.AudioFile(
                        audio_stream
                    ) as source:

                        recorded_audio = (
                            recognizer.record(
                                source
                            )
                        )


                    try:

                        voice_query = (
                            recognizer.recognize_google(
                                recorded_audio
                            )
                        )


                        if voice_query:

                            st.success(
                                f"🎤 Recognized: {voice_query}"
                            )


                    except sr.UnknownValueError:

                        st.warning(
                            "I couldn't understand the recording."
                        )


                    except sr.RequestError as e:

                        st.warning(
                            "Speech recognition service "
                            f"is unavailable: {e}"
                        )


    except Exception as e:

        st.warning(
            f"Microphone processing failed: {e}"
        )


# =========================================================
# FINAL QUERY
# =========================================================

final_query = ""


if send_clicked:

    typed_query = user_prompt.strip()

    spoken_query = voice_query.strip()


    if typed_query:

        final_query = typed_query


    elif spoken_query:

        final_query = spoken_query


    else:

        st.warning(
            "Please type a question or use the microphone."
        )


# =========================================================
# LEARNING MODE
# =========================================================

if final_query and st.session_state.learning_mode:

    final_query = (
        "Answer this in Learning Mode.\n\n"
        "Structure the response as:\n"
        "1. Simple explanation\n"
        "2. Detailed concept\n"
        "3. Example\n"
        "4. Important points\n"
        "5. Short summary\n\n"
        f"Question:\n{final_query}"
    )


# =========================================================
# PROCESS QUERY
# =========================================================

if final_query:

    process_query(
        final_query
    )

    # IMPORTANT:
    #
    # DO NOT DO THIS:
    #
    # st.session_state.custom_prompt = ""
    #
    # because custom_prompt belongs to the
    # already-created text_input widget.
    #
    # We intentionally leave the widget state alone.

    st.rerun()
