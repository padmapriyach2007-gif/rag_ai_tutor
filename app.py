import io
import hashlib
import html

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
# RAG + DATABASE
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
    "voice_error": None,

    "rename_session_id": None,

    "show_canvas": False,
    "show_calculator": False,
    "show_notes": False,
    "learning_mode": False,

    "canvas_text": "",
    "notes_text": "",

    # Used to create a fresh text-input widget
    # after sending a message.
    "prompt_version": 0,

    # Prevents repeated processing.
    "last_processed_prompt": "",
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

/* =========================================================
   GOOGLE FONTS
   ========================================================= */

@import url(
'https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Space+Grotesk:wght@500;600;700&display=swap'
);


/* =========================================================
   GLOBAL
   ========================================================= */

html,
body,
[class*="css"] {

    font-family:
        "Inter",
        sans-serif;
}


.stApp {

    min-height: 100vh;

    background:

        radial-gradient(
            circle at 8% 10%,
            rgba(99,102,241,.18),
            transparent 28%
        ),

        radial-gradient(
            circle at 92% 8%,
            rgba(59,130,246,.13),
            transparent 28%
        ),

        radial-gradient(
            circle at 75% 85%,
            rgba(168,85,247,.12),
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
   GRID BACKGROUND
   ========================================================= */

.stApp::before {

    content: "";

    position: fixed;

    inset: 0;

    pointer-events: none;

    background-image:

        linear-gradient(
            rgba(129,140,248,.025) 1px,
            transparent 1px
        ),

        linear-gradient(
            90deg,
            rgba(129,140,248,.025) 1px,
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
            circle at 5% 12%,
            rgba(255,255,255,.9) 0px,
            transparent 2px
        ),

        radial-gradient(
            circle at 15% 37%,
            rgba(180,210,255,.8) 0px,
            transparent 2px
        ),

        radial-gradient(
            circle at 48% 22%,
            rgba(200,180,255,.8) 0px,
            transparent 2px
        ),

        radial-gradient(
            circle at 76% 68%,
            rgba(180,200,255,.7) 0px,
            transparent 2px
        ),

        radial-gradient(
            circle at 91% 31%,
            rgba(255,255,255,.7) 0px,
            transparent 2px
        );

    animation:
        starFloat 15s ease-in-out infinite alternate;
}


@keyframes starFloat {

    0% {

        transform:
            translateY(0px);

        opacity: .45;
    }

    50% {

        transform:
            translateY(-5px);

        opacity: .85;
    }

    100% {

        transform:
            translateY(4px);

        opacity: .55;
    }
}


/* =========================================================
   MAIN CONTAINER
   ========================================================= */

.main .block-container {

    max-width: 1250px;

    padding-top: 1rem;

    padding-bottom: 10rem;

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

    border-right:
        1px solid rgba(139,92,246,.20);
}


section[data-testid="stSidebar"] .stButton button {

    border-radius: 12px;

    border:
        1px solid rgba(139,92,246,.17);

    background:

        linear-gradient(
            135deg,
            rgba(18,25,53,.95),
            rgba(7,12,29,.95)
        );

    color: #dbeafe;

    transition:
        all .2s ease;
}


section[data-testid="stSidebar"] .stButton button:hover {

    border-color:
        rgba(167,139,250,.70);

    box-shadow:
        0 0 22px rgba(139,92,246,.20);

    transform:
        translateY(-1px);
}


/* =========================================================
   SIDEBAR CHAT BUTTONS
   ========================================================= */

.chat-history-title {

    color: #94a3b8;

    font-size: 10px;

    font-weight: 700;

    letter-spacing: 1.5px;

    margin:
        15px 0 8px 0;
}


/* =========================================================
   HEADER
   ========================================================= */

.quantum-logo {

    text-align: center;

    font-size: 70px;

    line-height: 1;

    margin:
        8px auto 5px auto;

    filter:
        drop-shadow(0 0 8px rgba(167,139,250,.9))
        drop-shadow(0 0 25px rgba(99,102,241,.65));

    animation:
        quantumPulse 3s ease-in-out infinite;
}


@keyframes quantumPulse {

    0%,100% {

        transform: scale(1);

        filter:
            drop-shadow(0 0 8px rgba(167,139,250,.7))
            drop-shadow(0 0 20px rgba(99,102,241,.5));
    }

    50% {

        transform: scale(1.07);

        filter:
            drop-shadow(0 0 12px rgba(255,255,255,.9))
            drop-shadow(0 0 35px rgba(139,92,246,.9));
    }
}


.main-title {

    text-align: center;

    font-family:
        "Space Grotesk",
        sans-serif;

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
        8px auto 15px auto;

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
        1px solid rgba(139,92,246,.12);

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
        rgba(139,92,246,.32);

    box-shadow:
        0 5px 25px rgba(0,0,0,.22);
}


[data-testid="stChatMessage"] p {

    color: #dbe4f0;

    line-height: 1.7;
}


/* =========================================================
   PROMPT CONTAINER
   ========================================================= */

.prompt-shell {

    margin-top: 25px;

    padding: 8px;

    border-radius: 22px;

    border:
        1px solid rgba(139,92,246,.30);

    background:

        linear-gradient(
            135deg,
            rgba(15,23,42,.96),
            rgba(7,12,28,.96)
        );

    box-shadow:

        0 0 30px rgba(99,102,241,.10),

        inset
        0 0 20px rgba(99,102,241,.035);

    transition:
        all .3s ease;
}


.prompt-shell:hover {

    border-color:
        rgba(139,92,246,.52);

    box-shadow:

        0 0 35px rgba(99,102,241,.18),

        inset
        0 0 25px rgba(99,102,241,.05);
}


.prompt-label {

    color: #64748b;

    font-size: 10px;

    font-weight: 700;

    letter-spacing: 1.1px;

    padding:
        2px 8px 4px 8px;
}


/* =========================================================
   TEXT INPUT
   ========================================================= */

.prompt-input input {

    background:
        rgba(15,23,42,.60) !important;

    border:
        1px solid rgba(71,85,105,.25) !important;

    border-radius:
        14px !important;

    color:
        #f8fafc !important;

    min-height:
        47px !important;

    font-size:
        14px !important;

    transition:
        all .2s ease;
}


.prompt-input input:focus {

    border-color:
        rgba(139,92,246,.55) !important;

    box-shadow:
        0 0 0 2px rgba(139,92,246,.07),
        0 0 22px rgba(99,102,241,.12) !important;
}


/* =========================================================
   TOOL BUTTONS
   ========================================================= */

.prompt-tool button {

    min-height:
        47px !important;

    border-radius:
        14px !important;

    background:
        rgba(15,23,42,.78) !important;

    border:
        1px solid rgba(100,116,139,.30) !important;

    color:
        #e2e8f0 !important;

    transition:
        all .2s ease !important;
}


.prompt-tool button:hover {

    transform:
        translateY(-2px);

    border-color:
        rgba(139,92,246,.65) !important;

    box-shadow:
        0 0 20px rgba(99,102,241,.22);
}


/* =========================================================
   THINK BUTTON
   ========================================================= */

.think-button button {

    min-height:
        47px !important;

    border-radius:
        14px !important;

    background:

        linear-gradient(
            135deg,
            rgba(99,102,241,.15),
            rgba(59,130,246,.10)
        ) !important;

    border:
        1px solid rgba(139,92,246,.38) !important;

    color:
        #e0e7ff !important;

    font-weight:
        600 !important;
}


.think-button button:hover {

    box-shadow:
        0 0 22px rgba(139,92,246,.30);
}


/* =========================================================
   SEND BUTTON
   ========================================================= */

.send-button button {

    min-height:
        47px !important;

    border-radius:
        14px !important;

    background:

        linear-gradient(
            135deg,
            #6366f1,
            #4f46e5,
            #3b82f6
        ) !important;

    border:
        1px solid rgba(165,180,252,.55) !important;

    color:
        white !important;

    font-weight:
        700 !important;

    box-shadow:
        0 0 18px rgba(99,102,241,.22);

    transition:
        all .2s ease !important;
}


.send-button button:hover {

    transform:
        translateY(-2px);

    box-shadow:
        0 0 30px rgba(99,102,241,.45);
}


/* =========================================================
   MICROPHONE
   ========================================================= */

.mic-button button {

    min-height:
        47px !important;

    border-radius:
        14px !important;

    background:
        rgba(15,23,42,.90) !important;

    border:
        1px solid rgba(96,165,250,.30) !important;

    color:
        #bfdbfe !important;

    font-size:
        18px !important;

    transition:
        all .2s ease !important;
}


.mic-button button:hover {

    border-color:
        rgba(96,165,250,.75) !important;

    box-shadow:
        0 0 22px rgba(59,130,246,.25);
}


/* =========================================================
   CANVAS
   ========================================================= */

.canvas-box {

    margin-top: 20px;

    padding: 25px;

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
   LOGIN PAGE
   ========================================================= */

.login-page {

    min-height:
        82vh;

    display:
        flex;

    align-items:
        center;

    justify-content:
        center;

    padding:
        30px 20px;
}


.login-card {

    width:
        100%;

    max-width:
        500px;

    margin:
        auto;

    padding:
        40px;

    border-radius:
        28px;

    background:

        linear-gradient(
            145deg,
            rgba(15,23,42,.97),
            rgba(7,12,28,.97)
        );

    border:
        1px solid rgba(139,92,246,.36);

    box-shadow:

        0 0 30px rgba(99,102,241,.14),

        0 0 80px rgba(139,92,246,.08),

        inset
        0 0 30px rgba(99,102,241,.035);

    animation:
        loginAppear .6s ease-out;
}


@keyframes loginAppear {

    from {

        opacity: 0;

        transform:
            translateY(20px)
            scale(.97);
    }

    to {

        opacity: 1;

        transform:
            translateY(0)
            scale(1);
    }
}


.login-logo {

    text-align:
        center;

    font-size:
        72px;

    line-height:
        1;

    margin-bottom:
        15px;

    filter:
        drop-shadow(0 0 8px rgba(167,139,250,.9))
        drop-shadow(0 0 30px rgba(99,102,241,.7));

    animation:
        loginPulse 3s ease-in-out infinite;
}


@keyframes loginPulse {

    0%,100% {

        transform:
            scale(1);
    }

    50% {

        transform:
            scale(1.08);
    }
}


.login-title {

    text-align:
        center;

    font-family:
        "Space Grotesk",
        sans-serif;

    font-size:
        30px;

    font-weight:
        700;

    letter-spacing:
        3px;

    color:
        #e0e7ff;
}


.login-subtitle {

    text-align:
        center;

    color:
        #94a3b8;

    font-size:
        13px;

    line-height:
        1.7;

    margin-top:
        8px;
}


.login-divider {

    width:
        100%;

    height:
        1px;

    margin:
        25px 0;

    background:

        linear-gradient(
            90deg,
            transparent,
            rgba(139,92,246,.55),
            transparent
        );
}


.login-label {

    color:
        #cbd5e1;

    font-size:
        13px;

    font-weight:
        600;

    margin-bottom:
        7px;
}


/* Login input */

.login-input input {

    background:
        rgba(2,6,23,.75) !important;

    border:
        1px solid rgba(139,92,246,.28) !important;

    border-radius:
        14px !important;

    color:
        #f8fafc !important;

    min-height:
        49px !important;
}


.login-input input:focus {

    border-color:
        rgba(139,92,246,.85) !important;

    box-shadow:
        0 0 0 2px rgba(139,92,246,.08),
        0 0 25px rgba(99,102,241,.18) !important;
}


.login-button button {

    min-height:
        49px !important;

    border-radius:
        14px !important;

    background:

        linear-gradient(
            135deg,
            #6366f1,
            #4f46e5,
            #3b82f6
        ) !important;

    border:
        1px solid rgba(165,180,252,.55) !important;

    color:
        white !important;

    font-weight:
        700 !important;

    box-shadow:
        0 0 22px rgba(99,102,241,.25);

    transition:
        all .2s ease;
}


.login-button button:hover {

    transform:
        translateY(-2px);

    box-shadow:
        0 0 35px rgba(99,102,241,.45);
}


.login-status {

    text-align:
        center;

    color:
        #64748b;

    font-size:
        11px;

    margin-top:
        16px;
}


/* =========================================================
   POPUP
   ========================================================= */

.tool-card {

    padding:
        14px;

    border-radius:
        14px;

    border:
        1px solid rgba(139,92,246,.20);

    background:
        rgba(10,15,35,.85);

    margin-bottom:
        10px;
}


/* =========================================================
   HIDE STREAMLIT FOOTER
   ========================================================= */

footer {

    visibility:
        hidden;
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
    """
    Refresh chat sessions only when actually needed.
    Avoid calling this unnecessarily on every rerun.
    """

    if st.session_state.user_id:

        try:

            st.session_state.sessions = get_user_sessions(
                st.session_state.user_id
            )

        except Exception:

            st.session_state.sessions = []


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

        st.session_state.rename_session_id = None

        refresh_sessions()

    except Exception as e:

        st.error(
            f"Could not create chat: {e}"
        )


def clear_current_chat():

    st.session_state.messages = []

    st.session_state.last_processed_prompt = ""


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

    st.session_state.processed_audio_hash = None

    st.session_state.prompt_version += 1


def load_chat(session_id):

    st.session_state.session_id = session_id

    try:

        restored = restore_chat(
            session_id
        )

        if restored is None:
            restored = []

        st.session_state.messages = restored

    except Exception:

        st.session_state.messages = []


def process_query(user_query):

    """
    Send query to RAG engine.
    """

    user_query = user_query.strip()

    if not user_query:
        return

    if not st.session_state.logged_in:

        st.warning(
            "Please log in first."
        )

        return


    # -----------------------------------------------------
    # Create a chat if none exists
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
    # RAG RESPONSE
    # -----------------------------------------------------

    try:

        answer = answer_question(

            query=user_query,

            session_id=
                st.session_state.session_id,

            user_id=
                st.session_state.user_id,
        )

    except Exception as e:

        answer = (
            "⚠️ I couldn't generate a response "
            "right now.\n\n"
            f"Error: `{str(e)}`"
        )


    # -----------------------------------------------------
    # Assistant
    # -----------------------------------------------------

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": answer,
        }
    )


    # -----------------------------------------------------
    # Do NOT refresh database unnecessarily here.
    # -----------------------------------------------------
    # The response is displayed immediately.
    # This reduces perceived response time.


# =========================================================
# CENTERED LOGIN SCREEN
# =========================================================

if not st.session_state.logged_in:

    # -----------------------------------------------------
    # Completely hide sidebar
    # -----------------------------------------------------

    st.markdown(
        """
        <style>

        section[data-testid="stSidebar"] {
            display: none !important;
        }

        [data-testid="collapsedControl"] {
            display: none !important;
        }

        </style>
        """,
        unsafe_allow_html=True,
    )


    # -----------------------------------------------------
    # LOGIN LAYOUT
    # -----------------------------------------------------

    st.markdown(
        """
        <div class="login-page">

            <div class="login-card">

                <div class="login-logo">
                    ⚛️
                </div>

                <div class="login-title">
                    QUANTUM LAB
                </div>

                <div class="login-subtitle">
                    AI-powered learning for
                    Quantum Computing & Advanced Physics
                </div>

                <div class="login-divider"></div>

            </div>

        </div>
        """,
        unsafe_allow_html=True,
    )


    # -----------------------------------------------------
    # Login form positioned centrally
    # -----------------------------------------------------

    left_col, center_col, right_col = st.columns(
        [1, 2, 1]
    )


    with center_col:

        st.markdown(
            """
            <div class="login-label">
                🔐 Account Login
            </div>
            """,
            unsafe_allow_html=True,
        )


        email = st.text_input(
            "Email",

            placeholder=
                "student@example.com",

            label_visibility=
                "collapsed",

            key=
                "login_email",

        )


        st.markdown(
            "<div style='height:8px'></div>",
            unsafe_allow_html=True,
        )


        st.markdown(
            '<div class="login-button">',
            unsafe_allow_html=True,
        )


        login_clicked = st.button(
            "🔑  Enter Quantum Lab",

            use_container_width=True,

            key=
                "center_login",
        )


        st.markdown(
            "</div>",
            unsafe_allow_html=True,
        )


        st.markdown(
            """
            <div class="login-status">
                ✦ Your AI learning workspace awaits ✦
            </div>
            """,
            unsafe_allow_html=True,
        )


        # -------------------------------------------------
        # LOGIN
        # -------------------------------------------------

        if login_clicked:

            clean_email = email.strip()


            if not clean_email:

                st.warning(
                    "Please enter your email address."
                )

            else:

                try:

                    user_id = get_or_create_user(
                        clean_email
                    )


                    st.session_state.user_email = (
                        clean_email
                    )

                    st.session_state.user_id = (
                        user_id
                    )

                    st.session_state.logged_in = True

                    st.session_state.session_id = None

                    st.session_state.messages = []

                    st.session_state.sessions = []

                    st.session_state.prompt_version += 1

                    refresh_sessions()

                    st.rerun()


                except Exception as e:

                    st.error(
                        f"Login failed: {e}"
                    )


    st.stop()


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
            font-size:30px;
            margin-bottom:5px;
            filter:
                drop-shadow(0 0 8px rgba(139,92,246,.8));
        ">
            ⚛️
        </div>

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
        unsafe_allow_html=True,
    )


    st.markdown("---")


    # =====================================================
    # ACCOUNT
    # =====================================================

    st.subheader("🔐 Account")


    safe_email = html.escape(
        st.session_state.user_email
    )


    st.markdown(
        f"""
        <div style="
            padding:12px;
            border-radius:12px;
            background:
                rgba(99,102,241,.08);
            border:
                1px solid rgba(99,102,241,.20);
            color:#cbd5e1;
            font-size:13px;
        ">
            👤 Logged in as<br>
            <strong>{safe_email}</strong>
        </div>
        """,
        unsafe_allow_html=True,
    )


    st.write("")


    if st.button(
        "🚪 Log Out",

        use_container_width=True,

        key="sidebar_logout",
    ):

        logout_user()

        st.rerun()


    st.markdown("---")


    # =====================================================
    # CHATS
    # =====================================================

    st.subheader("💬 Chats")


    # -----------------------------------------------------
    # NEW CHAT
    # -----------------------------------------------------

    if st.button(
        "➕ New Chat",

        use_container_width=True,

        key="sidebar_new_chat",
    ):

        start_new_chat()

        st.rerun()


    st.markdown(
        """
        <div class="chat-history-title">
            CHAT HISTORY
        </div>
        """,
        unsafe_allow_html=True,
    )


    # -----------------------------------------------------
    # Sessions
    # -----------------------------------------------------

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


            selected = (
                session_id ==
                st.session_state.session_id
            )


            prefix = (
                "🟣"
                if selected
                else "💬"
            )


            # -------------------------------------------------
            # Three controls
            # -------------------------------------------------

            col1, col2, col3 = st.columns(
                [0.62, 0.19, 0.19],

                gap="small"
            )


            # -------------------------------------------------
            # OPEN CHAT
            # -------------------------------------------------

            with col1:

                short_title = str(title)

                if len(short_title) > 22:

                    short_title = (
                        short_title[:22]
                        + "..."
                    )


                if st.button(

                    f"{prefix} {short_title}",

                    key=
                        f"chat_{session_id}",

                    use_container_width=True,

                ):

                    load_chat(
                        session_id
                    )

                    st.rerun()


            # -------------------------------------------------
            # RENAME
            # -------------------------------------------------

            with col2:

                if st.button(

                    "✏️",

                    key=
                        f"rename_{session_id}",

                    help=
                        "Rename chat",

                    use_container_width=True,

                ):

                    st.session_state.rename_session_id = (
                        session_id
                    )

                    st.rerun()


            # -------------------------------------------------
            # DELETE
            # -------------------------------------------------

            with col3:

                if st.button(

                    "🗑️",

                    key=
                        f"delete_{session_id}",

                    help=
                        "Delete chat",

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

                        continue


                    # -----------------------------------------
                    # If deleting current chat
                    # -----------------------------------------

                    if (
                        st.session_state.session_id
                        == session_id
                    ):

                        st.session_state.session_id = None

                        st.session_state.messages = []

                        st.session_state.rename_session_id = None


                    refresh_sessions()

                    st.rerun()


            # -------------------------------------------------
            # RENAME BOX
            # -------------------------------------------------

            if (
                st.session_state.rename_session_id
                == session_id
            ):

                st.markdown(
                    "<div style='height:5px'></div>",
                    unsafe_allow_html=True,
                )


                new_title = st.text_input(

                    "New chat name",

                    value=str(title),

                    key=
                        f"title_input_{session_id}",

                )


                rename_col1, rename_col2 = st.columns(
                    2
                )


                # ---------------------------------------------
                # SAVE
                # ---------------------------------------------

                with rename_col1:

                    if st.button(

                        "Save",

                        key=
                            f"save_name_{session_id}",

                        use_container_width=True,

                    ):

                        clean_title = (
                            new_title.strip()
                        )


                        if not clean_title:

                            st.warning(
                                "Chat name cannot be empty."
                            )

                        else:

                            try:

                                # IMPORTANT
                                # This fixes:
                                #
                                # rename_chat()
                                # missing 1 required
                                # positional argument:
                                # 'new_title'
                                #
                                rename_chat(
                                    session_id,
                                    clean_title
                                )


                                st.session_state.rename_session_id = (
                                    None
                                )


                                refresh_sessions()

                                st.rerun()


                            except Exception as e:

                                st.error(
                                    f"Rename failed: {e}"
                                )


                # ---------------------------------------------
                # CANCEL
                # ---------------------------------------------

                with rename_col2:

                    if st.button(

                        "Cancel",

                        key=
                            f"cancel_name_{session_id}",

                        use_container_width=True,

                    ):

                        st.session_state.rename_session_id = (
                            None
                        )

                        st.rerun()


    # =====================================================
    # CLEAR CHAT
    # =====================================================

    st.markdown("---")


    if st.button(

        "🧹 Clear Conversation",

        use_container_width=True,

        key=
            "sidebar_clear_chat",

    ):

        clear_current_chat()

        st.rerun()


    # =====================================================
    # CURRENT CHAT
    # =====================================================

    if st.session_state.session_id:

        st.markdown("---")

        st.caption(
            "Current Chat ID:"
        )

        st.code(
            str(
                st.session_state.session_id
            ),
            language=None,
        )


# =========================================================
# MAIN HEADER
# =========================================================

st.markdown(
    '<div class="quantum-logo">⚛️</div>',
    unsafe_allow_html=True,
)


st.markdown(
    '<div class="main-title">QUANTUM LAB</div>',
    unsafe_allow_html=True,
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


    safe_title = html.escape(
        str(current_title)
    )


    st.markdown(
        f"""
        <div style="
            text-align:center;
            color:#a5b4fc;
            font-size:13px;
            margin-bottom:15px;
        ">
            💬 {safe_title}
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
# CANVAS
# =========================================================

if st.session_state.show_canvas:

    st.markdown(
        """
        <div class="canvas-box">

            <div style="
                font-size:24px;
                font-weight:700;
                color:#e0e7ff;
                margin-bottom:8px;
            ">
                🎨 Canvas Workbench
            </div>

            <div style="
                color:#94a3b8;
                line-height:1.7;
            ">
                Create quantum notes, equations,
                diagrams and ideas.
            </div>

        </div>
        """,
        unsafe_allow_html=True,
    )


    canvas_text = st.text_area(

        "Canvas",

        placeholder=
            "Write your quantum notes, equations or ideas...",

        height=220,

        key="canvas_text",

    )


    canvas_col1, canvas_col2 = st.columns(
        2
    )


    with canvas_col1:

        if st.button(
            "💾 Save Canvas",
            use_container_width=True,
            key="save_canvas",
        ):

            st.success(
                "Canvas saved for this session."
            )


    with canvas_col2:

        if st.button(
            "✖ Close Canvas",
            use_container_width=True,
            key="close_canvas",
        ):

            st.session_state.show_canvas = False

            st.rerun()


# =========================================================
# NOTES
# =========================================================

if st.session_state.show_notes:

    st.markdown(
        """
        <div class="canvas-box">

            <div style="
                font-size:22px;
                font-weight:700;
                color:#e0e7ff;
            ">
                📝 Quantum Notes
            </div>

        </div>
        """,
        unsafe_allow_html=True,
    )


    st.text_area(

        "Notes",

        placeholder=
            "Write your important concepts here...",

        height=200,

        key="notes_text",

    )


# =========================================================
# QUANTUM CALCULATOR
# =========================================================

if st.session_state.show_calculator:

    st.markdown(
        """
        <div class="canvas-box">

            <div style="
                font-size:22px;
                font-weight:700;
                color:#e0e7ff;
                margin-bottom:8px;
            ">
                🧮 Quantum Calculator
            </div>

            <div style="
                color:#94a3b8;
            ">
                Calculate quantum expressions,
                probabilities and basic formulas.
            </div>

        </div>
        """,
        unsafe_allow_html=True,
    )


    calc_expression = st.text_input(

        "Expression",

        placeholder=
            "Example: 0.5 + 0.25",

        key="calculator_expression",

    )


    if st.button(
        "Calculate",
        key="calculate_button",
    ):

        try:

            # Basic demonstration calculator.
            # Avoid eval for untrusted expressions.
            result = float(calc_expression)

            st.success(
                f"Result: {result}"
            )

        except Exception:

            st.info(
                "Enter a valid numeric expression."
            )


# =========================================================
# PROMPT AREA
# =========================================================

st.markdown(
    '<div class="prompt-shell">',
    unsafe_allow_html=True,
)


st.markdown(
    '<div class="prompt-label">ASK YOUR QUANTUM AI TUTOR</div>',
    unsafe_allow_html=True,
)


# =========================================================
# PROMPT ROW
# =========================================================

prompt_col1, prompt_col2, prompt_col3, prompt_col4, prompt_col5 = st.columns(
    [0.08, 0.56, 0.12, 0.10, 0.14],

    gap="small",

    vertical_alignment="center",
)


# =========================================================
# PLUS POPUP
# =========================================================

with prompt_col1:

    st.markdown(
        '<div class="prompt-tool">',
        unsafe_allow_html=True,
    )


    with st.popover(
        "＋",
        use_container_width=True,
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
                "🛠️ More Tools",
            ]
        )


        # =================================================
        # FILES
        # =================================================

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

                key=
                    "quantum_attachments",

            )


            if uploaded:

                st.session_state.uploaded_files = (
                    uploaded
                )


                st.success(
                    f"{len(uploaded)} file(s) attached"
                )


                for file in uploaded:

                    st.caption(
                        f"📎 {file.name}"
                    )


        # =================================================
        # GOOGLE DRIVE
        # =================================================

        with tab2:

            st.markdown(
                """
                <div class="tool-card">

                    ☁️ <strong>Google Drive</strong>

                    <br>

                    <span style="
                        color:#94a3b8;
                        font-size:12px;
                    ">
                        Attach a Google Drive file link.
                    </span>

                </div>
                """,
                unsafe_allow_html=True,
            )


            drive_url = st.text_input(

                "Drive file link",

                placeholder=
                    "Paste Google Drive link",

                key=
                    "drive_url",

            )


            if st.button(

                "Attach Drive File",

                use_container_width=True,

                key=
                    "attach_drive",

            ):

                clean_drive_url = (
                    drive_url.strip()
                )


                if clean_drive_url:

                    if (
                        clean_drive_url
                        not in st.session_state.drive_links
                    ):

                        st.session_state.drive_links.append(
                            clean_drive_url
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

        with tab3:

            st.markdown(
                "### 🛠️ More Tools"
            )


            if st.button(

                "🎨 Canvas",

                use_container_width=True,

                key=
                    "tool_canvas",

            ):

                st.session_state.show_canvas = True

                st.rerun()


            if st.button(

                "🧮 Quantum Calculator",

                use_container_width=True,

                key=
                    "tool_calculator",

            ):

                st.session_state.show_calculator = True

                st.rerun()


            if st.button(

                "📚 Learning Mode",

                use_container_width=True,

                key=
                    "tool_learning",

            ):

                st.session_state.learning_mode = True

                st.success(
                    "Learning Mode activated!"
                )


            if st.button(

                "📝 Notes",

                use_container_width=True,

                key=
                    "tool_notes",

            ):

                st.session_state.show_notes = True

                st.rerun()


    st.markdown(
        "</div>",
        unsafe_allow_html=True,
    )


# =========================================================
# MICROPHONE PROCESSING
# =========================================================
#
# IMPORTANT:
# audio_input is instantiated BEFORE the text_input.
#
# This lets us safely put the recognized text into
# session_state BEFORE the text widget is created.
#
# This prevents:
#
# StreamlitWidgetAlreadyInstantiatedError
#
# =========================================================

voice_query = ""


with prompt_col4:

    st.markdown(
        '<div class="mic-button">',
        unsafe_allow_html=True,
    )


    audio_value = st.audio_input(

        "🎙️",

        key=
            "quantum_microphone",

        label_visibility=
            "collapsed",

    )


    st.markdown(
        "</div>",
        unsafe_allow_html=True,
    )


# =========================================================
# VOICE TRANSCRIPTION
# =========================================================

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

                    st.session_state.voice_error = (
                        "SpeechRecognition is not installed."
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


                        # -------------------------------------
                        # PUT VOICE TEXT INTO PROMPT
                        #
                        # This happens BEFORE text_input()
                        # is instantiated.
                        # -------------------------------------

                        st.session_state.voice_error = None

                        st.session_state.voice_transcript = (
                            voice_query
                        )

                        st.session_state.prompt_version += 1

                        st.rerun()


                    except sr.UnknownValueError:

                        st.session_state.voice_error = (
                            "I couldn't understand the recording."
                        )


                    except sr.RequestError as e:

                        st.session_state.voice_error = (
                            f"Speech service error: {e}"
                        )


    except Exception as e:

        st.session_state.voice_error = (
            f"Microphone transcription failed: {e}"
        )


# =========================================================
# PUT TRANSCRIPT INTO PROMPT
# =========================================================

if "voice_transcript" in st.session_state:

    transcript = (
        st.session_state.voice_transcript
    )


    if transcript:

        # Use a fresh widget key.
        # This avoids modifying an already-instantiated
        # Streamlit widget.

        st.session_state[
            f"voice_prompt_{st.session_state.prompt_version}"
        ] = transcript


        # Remove transcript after transferring it.

        del st.session_state.voice_transcript


# =========================================================
# TEXT PROMPT
# =========================================================

with prompt_col2:

    current_prompt_key = (
        f"custom_prompt_"
        f"{st.session_state.prompt_version}"
    )


    user_prompt = st.text_input(

        "Message",

        placeholder=
            "Ask anything about quantum computing...",

        label_visibility=
            "collapsed",

        key=
            current_prompt_key,

    )


# =========================================================
# THINK BUTTON
# =========================================================

with prompt_col3:

    st.markdown(
        '<div class="think-button">',
        unsafe_allow_html=True,
    )


    think_clicked = st.button(

        "🧠 Think",

        use_container_width=True,

        key=
            "think_button",

    )


    st.markdown(
        "</div>",
        unsafe_allow_html=True,
    )


# =========================================================
# SEND BUTTON
# =========================================================

with prompt_col5:

    st.markdown(
        '<div class="send-button">',
        unsafe_allow_html=True,
    )


    send_clicked = st.button(

        "➤ Send",

        use_container_width=True,

        key=
            "send_button",

    )


    st.markdown(
        "</div>",
        unsafe_allow_html=True,
    )


st.markdown(
    "</div>",
    unsafe_allow_html=True,
)


# =========================================================
# VOICE ERROR
# =========================================================

if st.session_state.voice_error:

    st.warning(
        st.session_state.voice_error
    )

    st.session_state.voice_error = None


# =========================================================
# ATTACHMENTS
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
# LEARNING MODE
# =========================================================

if st.session_state.learning_mode:

    st.info(
        "📚 Learning Mode is active. "
        "The AI Tutor will focus on step-by-step explanations."
    )


# =========================================================
# FINAL QUERY
# =========================================================

final_query = ""


if send_clicked or think_clicked:

    if user_prompt.strip():

        final_query = (
            user_prompt.strip()
        )

    else:

        st.warning(
            "Please enter a question or use the microphone."
        )


# =========================================================
# EXECUTE RAG
# =========================================================

if final_query:

    process_query(
        final_query
    )


    # -----------------------------------------------------
    # Create a fresh prompt widget.
    #
    # IMPORTANT:
    # We do NOT do:
    #
    # st.session_state.custom_prompt = ""
    #
    # because that caused:
    #
    # StreamlitWidgetAlreadyInstantiatedError
    #
    # -----------------------------------------------------

    st.session_state.prompt_version += 1


    # -----------------------------------------------------
    # Clear voice hash so another recording can be used.
    # -----------------------------------------------------

    st.session_state.processed_audio_hash = None


    # -----------------------------------------------------
    # Rerun once so the new message appears immediately.
    # -----------------------------------------------------

    st.rerun()
