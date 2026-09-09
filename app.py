import io
import hashlib
import html
import streamlit as st


# ============================================================
# OPTIONAL SPEECH RECOGNITION
# ============================================================

try:
    import speech_recognition as sr
    SPEECH_RECOGNITION_AVAILABLE = True
except ImportError:
    SPEECH_RECOGNITION_AVAILABLE = False


# ============================================================
# BACKEND
# ============================================================

from rag_engine import (
    answer_question,
    create_chat_session,
    delete_chat,
    get_or_create_user,
    get_user_sessions,
    rename_chat,
    restore_chat,
)


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="Quantum Lab | AI Tutor",
    page_icon="⚛️",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# SESSION STATE
# ============================================================

DEFAULTS = {
    "logged_in": False,
    "user_email": "",
    "user_id": None,

    "session_id": None,
    "messages": [],

    "sessions": [],

    "show_canvas": False,
    "show_more_tools": False,

    "uploaded_files": [],
    "drive_links": [],

    "processed_audio_hash": None,

    # Important:
    # We use a versioned widget key instead of modifying
    # st.session_state.prompt_text after creating the widget.
    "prompt_version": 0,

    "processing": False,

    "rename_session_id": None,
    "rename_value": "",

    "learning_mode": False,
}


for key, value in DEFAULTS.items():

    if key not in st.session_state:
        st.session_state[key] = value


# ============================================================
# CSS
# ============================================================

st.markdown(
    """
<style>

/* ============================================================
   GOOGLE FONTS
   ============================================================ */

@import url(
'https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Space+Grotesk:wght@500;600;700&display=swap'
);


/* ============================================================
   ROOT
   ============================================================ */

:root {
    --bg: #020617;
    --panel: rgba(8, 13, 32, 0.86);
    --panel-2: rgba(15, 23, 50, 0.72);

    --purple: #8b5cf6;
    --violet: #a78bfa;
    --blue: #3b82f6;
    --cyan: #22d3ee;

    --text: #eef2ff;
    --muted: #94a3b8;

    --border: rgba(139, 92, 246, 0.24);
}


/* ============================================================
   GLOBAL
   ============================================================ */

html,
body,
[class*="css"] {

    font-family: "Inter", sans-serif;

}


.stApp {

    min-height: 100vh;

    background:

        radial-gradient(
            circle at 8% 8%,
            rgba(124, 58, 237, 0.23),
            transparent 28%
        ),

        radial-gradient(
            circle at 92% 12%,
            rgba(14, 165, 233, 0.14),
            transparent 27%
        ),

        radial-gradient(
            circle at 75% 80%,
            rgba(168, 85, 247, 0.12),
            transparent 30%
        ),

        linear-gradient(
            135deg,
            #020617 0%,
            #070b20 45%,
            #030617 100%
        );

    color: var(--text);

}


/* ============================================================
   HEADER
   ============================================================ */

[data-testid="stHeader"] {

    background: transparent !important;

}


/* ============================================================
   MAIN CONTAINER
   ============================================================ */

.main .block-container {

    max-width: 1350px;

    padding-top: 1.5rem;

    padding-bottom: 5rem;

}


/* ============================================================
   QUANTUM GRID
   ============================================================ */

.stApp::before {

    content: "";

    position: fixed;

    inset: 0;

    pointer-events: none;

    background-image:

        linear-gradient(
            rgba(139,92,246,0.025) 1px,
            transparent 1px
        ),

        linear-gradient(
            90deg,
            rgba(139,92,246,0.025) 1px,
            transparent 1px
        );

    background-size: 50px 50px;

    z-index: 0;

}


/* ============================================================
   STAR FIELD
   ============================================================ */

.quantum-space {

    position: fixed;

    inset: 0;

    pointer-events: none;

    z-index: 0;

    overflow: hidden;

}


.quantum-space::before {

    content: "";

    position: absolute;

    inset: 0;

    background-image:

        radial-gradient(
            circle at 7% 18%,
            white 0px,
            rgba(255,255,255,.5) 1px,
            transparent 2px
        ),

        radial-gradient(
            circle at 18% 72%,
            #a78bfa 0px,
            rgba(167,139,250,.4) 1px,
            transparent 2px
        ),

        radial-gradient(
            circle at 48% 13%,
            #93c5fd 0px,
            rgba(147,197,253,.4) 1px,
            transparent 2px
        ),

        radial-gradient(
            circle at 73% 34%,
            white 0px,
            rgba(255,255,255,.45) 1px,
            transparent 2px
        ),

        radial-gradient(
            circle at 91% 75%,
            #c4b5fd 0px,
            rgba(196,181,253,.4) 1px,
            transparent 2px
        );

    animation: starMove 12s ease-in-out infinite alternate;

}


@keyframes starMove {

    0% {
        transform: translateY(0px);
        opacity: .45;
    }

    50% {
        transform: translateY(-5px);
        opacity: .9;
    }

    100% {
        transform: translateY(4px);
        opacity: .55;
    }

}


/* ============================================================
   SIDEBAR
   ============================================================ */

section[data-testid="stSidebar"] {

    background:

        linear-gradient(
            180deg,
            rgba(2,6,23,.98),
            rgba(5,8,25,.98),
            rgba(2,6,18,.98)
        ) !important;

    border-right:
        1px solid rgba(139,92,246,.20);

}


section[data-testid="stSidebar"] .block-container {

    padding-top: 1.5rem;

}


section[data-testid="stSidebar"] .stButton button {

    min-height: 42px;

    border-radius: 12px;

    background:

        linear-gradient(
            135deg,
            rgba(15,23,55,.96),
            rgba(6,10,28,.96)
        );

    border:
        1px solid rgba(139,92,246,.22);

    color: #dbeafe;

    transition:
        all .18s ease;

}


section[data-testid="stSidebar"] .stButton button:hover {

    transform: translateY(-1px);

    border-color:
        rgba(167,139,250,.75);

    box-shadow:
        0 0 22px rgba(139,92,246,.20);

}


/* ============================================================
   SIDEBAR BRAND
   ============================================================ */

.sidebar-brand {

    text-align: center;

    padding:
        8px 0 16px 0;

}


.sidebar-logo {

    width: 60px;

    height: 60px;

    margin: auto;

    display: flex;

    align-items: center;

    justify-content: center;

    border-radius: 18px;

    font-size: 34px;

    background:

        linear-gradient(
            135deg,
            rgba(139,92,246,.25),
            rgba(59,130,246,.18)
        );

    border:
        1px solid rgba(167,139,250,.40);

    box-shadow:

        0 0 20px rgba(139,92,246,.22),

        inset 0 0 20px rgba(139,92,246,.08);

}


.sidebar-title {

    margin-top: 12px;

    font-family:
        "Space Grotesk",
        sans-serif;

    font-size: 20px;

    font-weight: 700;

    letter-spacing: 2px;

    color: #eef2ff;

}


.sidebar-subtitle {

    margin-top: 4px;

    color: #64748b;

    font-size: 11px;

}


/* ============================================================
   ACCOUNT CARD
   ============================================================ */

.account-card {

    padding: 13px;

    border-radius: 15px;

    background:
        linear-gradient(
            135deg,
            rgba(99,102,241,.12),
            rgba(59,130,246,.05)
        );

    border:
        1px solid rgba(99,102,241,.22);

}


.account-label {

    color: #818cf8;

    font-size: 10px;

    font-weight: 700;

    letter-spacing: 1.5px;

}


.account-email {

    margin-top: 5px;

    color: #e2e8f0;

    font-size: 12px;

    word-break: break-all;

}


/* ============================================================
   CHAT HISTORY
   ============================================================ */

.history-label {

    margin-top: 15px;

    margin-bottom: 8px;

    color: #64748b;

    font-size: 10px;

    font-weight: 700;

    letter-spacing: 1.5px;

}


.chat-row {

    margin-bottom: 3px;

}


.rename-box {

    padding: 8px;

    margin: 4px 0 8px 0;

    border-radius: 12px;

    background:
        rgba(99,102,241,.08);

    border:
        1px solid rgba(99,102,241,.20);

}


/* ============================================================
   HERO
   ============================================================ */

.hero {

    position: relative;

    text-align: center;

    padding:
        12px 20px 20px 20px;

    z-index: 2;

}


.hero-orbit {

    width: 86px;

    height: 86px;

    margin: 0 auto 10px auto;

    border-radius: 50%;

    display: flex;

    align-items: center;

    justify-content: center;

    font-size: 47px;

    position: relative;

    background:
        radial-gradient(
            circle,
            rgba(139,92,246,.25),
            rgba(15,23,42,.85)
        );

    border:
        1px solid rgba(167,139,250,.48);

    box-shadow:

        0 0 20px rgba(139,92,246,.30),

        0 0 60px rgba(99,102,241,.14),

        inset 0 0 25px rgba(139,92,246,.12);

    animation:
        orbitPulse 3s ease-in-out infinite;

}


.hero-orbit::before {

    content: "";

    position: absolute;

    inset: -10px;

    border-radius: 50%;

    border:
        1px solid rgba(59,130,246,.22);

    animation:
        rotateRing 8s linear infinite;

}


@keyframes orbitPulse {

    0%,100% {
        transform: scale(1);
    }

    50% {
        transform: scale(1.06);
    }

}


@keyframes rotateRing {

    from {
        transform: rotate(0deg);
    }

    to {
        transform: rotate(360deg);
    }

}


.hero-title {

    font-family:
        "Space Grotesk",
        sans-serif;

    font-size:
        clamp(34px, 5vw, 58px);

    font-weight: 700;

    letter-spacing: 4px;

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


.hero-subtitle {

    margin-top: 8px;

    color: #94a3b8;

    font-size: 14px;

}


.online-pill {

    width: fit-content;

    margin:
        12px auto 0 auto;

    padding:
        6px 13px;

    border-radius: 999px;

    color: #86efac;

    font-size: 10px;

    font-weight: 700;

    letter-spacing: 1.4px;

    background:
        rgba(34,197,94,.06);

    border:
        1px solid rgba(34,197,94,.20);

}


.online-dot {

    display: inline-block;

    width: 6px;

    height: 6px;

    margin-right: 5px;

    border-radius: 50%;

    background: #4ade80;

    box-shadow:
        0 0 10px #4ade80;

    animation:
        onlinePulse 1.5s infinite;

}


@keyframes onlinePulse {

    0%,100% {
        opacity: 1;
    }

    50% {
        opacity: .3;
    }

}


/* ============================================================
   GLOW LINE
   ============================================================ */

.glow-line {

    width: 300px;

    height: 2px;

    margin:
        8px auto 24px auto;

    background:

        linear-gradient(
            90deg,
            transparent,
            #8b5cf6,
            #3b82f6,
            #8b5cf6,
            transparent
        );

    box-shadow:
        0 0 20px rgba(139,92,246,.60);

    animation:
        lineGlow 2.8s ease-in-out infinite;

}


@keyframes lineGlow {

    0%,100% {
        opacity: .55;
    }

    50% {
        opacity: 1;
        box-shadow:
            0 0 35px rgba(139,92,246,.85);
    }

}


/* ============================================================
   CHAT AREA
   ============================================================ */

[data-testid="stChatMessage"] {

    border-radius: 18px !important;

    border:
        1px solid rgba(139,92,246,.13) !important;

    background:

        linear-gradient(
            135deg,
            rgba(15,23,42,.78),
            rgba(7,12,30,.78)
        ) !important;

    margin-bottom: 12px;

    box-shadow:
        0 8px 30px rgba(0,0,0,.12);

    transition:
        all .2s ease;

}


[data-testid="stChatMessage"]:hover {

    border-color:
        rgba(139,92,246,.34) !important;

    box-shadow:
        0 10px 35px rgba(99,102,241,.10);

}


[data-testid="stChatMessage"] p {

    color: #dbe4f0;

    line-height: 1.75;

}


/* ============================================================
   PROMPT OUTER
   ============================================================ */

.prompt-container {

    position: relative;

    margin-top: 26px;

    padding: 2px;

    border-radius: 23px;

    background:

        linear-gradient(
            110deg,
            rgba(99,102,241,.30),
            rgba(34,211,238,.12),
            rgba(139,92,246,.35)
        );

    box-shadow:

        0 0 35px rgba(99,102,241,.09),

        inset 0 0 20px rgba(99,102,241,.04);

    animation:
        promptGlow 4s ease-in-out infinite;

}


@keyframes promptGlow {

    0%,100% {

        box-shadow:
            0 0 25px rgba(99,102,241,.08);

    }

    50% {

        box-shadow:
            0 0 45px rgba(99,102,241,.18);

    }

}


.prompt-inner {

    border-radius: 21px;

    background:

        linear-gradient(
            135deg,
            rgba(10,15,35,.98),
            rgba(5,10,25,.98)
        );

    padding:
        8px 10px;

}


/* ============================================================
   PROMPT LABEL
   ============================================================ */

.prompt-label {

    color: #64748b;

    font-size: 9px;

    font-weight: 700;

    letter-spacing: 1.5px;

    margin:
        2px 0 5px 5px;

}


/* ============================================================
   TEXT INPUT
   ============================================================ */

.prompt-input input {

    background:
        rgba(15,23,42,.55) !important;

    border:
        1px solid rgba(139,92,246,.10) !important;

    border-radius:
        14px !important;

    color:
        #f8fafc !important;

    min-height:
        48px !important;

    font-size:
        14px !important;

    transition:
        all .2s ease !important;

}


.prompt-input input::placeholder {

    color:
        #64748b !important;

}


.prompt-input input:focus {

    border:
        1px solid rgba(139,92,246,.60) !important;

    box-shadow:

        0 0 0 2px rgba(139,92,246,.08),

        0 0 25px rgba(139,92,246,.15) !important;

}


/* ============================================================
   MICROPHONE
   ============================================================ */

.mic-button {

    position: relative;

}


.mic-button button {

    min-height: 48px !important;

    width: 48px !important;

    padding: 0 !important;

    border-radius: 14px !important;

    font-size: 20px !important;

    color: #c4b5fd !important;

    background:

        linear-gradient(
            135deg,
            rgba(99,102,241,.16),
            rgba(15,23,42,.95)
        ) !important;

    border:
        1px solid rgba(139,92,246,.28) !important;

}


.mic-button button:hover {

    color: white !important;

    border-color:
        rgba(167,139,250,.70) !important;

    box-shadow:
        0 0 22px rgba(139,92,246,.25);

}


/* ============================================================
   SEND
   ============================================================ */

.send-button button {

    min-height: 48px !important;

    border-radius: 14px !important;

    color: white !important;

    font-weight: 700 !important;

    border:
        1px solid rgba(165,180,252,.45) !important;

    background:

        linear-gradient(
            135deg,
            #6366f1,
            #3b82f6
        ) !important;

    box-shadow:
        0 0 25px rgba(99,102,241,.22);

    transition:
        all .18s ease;

}


.send-button button:hover {

    transform:
        translateY(-2px);

    box-shadow:
        0 0 35px rgba(99,102,241,.38);

}


/* ============================================================
   PLUS BUTTON
   ============================================================ */

.plus-button button {

    min-height: 48px !important;

    border-radius: 14px !important;

    font-size: 20px !important;

    background:

        linear-gradient(
            135deg,
            rgba(139,92,246,.18),
            rgba(15,23,42,.95)
        ) !important;

    border:
        1px solid rgba(139,92,246,.30) !important;

    color: #e0e7ff !important;

}


/* ============================================================
   TOOLS
   ============================================================ */

.tool-card {

    padding: 14px;

    margin-bottom: 10px;

    border-radius: 15px;

    background:

        linear-gradient(
            135deg,
            rgba(30,41,75,.60),
            rgba(10,15,35,.85)
        );

    border:
        1px solid rgba(139,92,246,.18);

}


.tool-title {

    color: #e0e7ff;

    font-weight: 700;

    font-size: 14px;

}


.tool-description {

    color: #64748b;

    font-size: 11px;

    margin-top: 4px;

}


/* ============================================================
   CANVAS
   ============================================================ */

.canvas-box {

    margin-top: 20px;

    padding: 22px;

    border-radius: 20px;

    background:

        linear-gradient(
            135deg,
            rgba(15,23,42,.90),
            rgba(10,15,35,.90)
        );

    border:
        1px solid rgba(99,102,241,.28);

    box-shadow:
        0 0 35px rgba(99,102,241,.10);

}


.canvas-title {

    font-family:
        "Space Grotesk",
        sans-serif;

    font-size: 23px;

    font-weight: 700;

    color: #e0e7ff;

}


/* ============================================================
   EMPTY STATE
   ============================================================ */

.empty-state {

    text-align: center;

    padding:
        55px 20px 40px 20px;

}


.empty-icon {

    font-size: 42px;

    opacity: .85;

}


.empty-title {

    margin-top: 12px;

    font-family:
        "Space Grotesk",
        sans-serif;

    font-size: 23px;

    color: #e0e7ff;

}


.empty-text {

    max-width: 580px;

    margin:
        8px auto;

    color: #64748b;

    font-size: 13px;

    line-height: 1.7;

}


/* ============================================================
   LOGIN SCREEN
   ============================================================ */

.login-page {

    min-height:
        78vh;

    display:
        flex;

    align-items:
        center;

    justify-content:
        center;

}


.login-card {

    width:
        min(560px, 92vw);

    padding:
        40px;

    border-radius:
        28px;

    position:
        relative;

    background:

        linear-gradient(
            135deg,
            rgba(15,23,42,.94),
            rgba(5,10,27,.96)
        );

    border:
        1px solid rgba(139,92,246,.30);

    box-shadow:

        0 0 50px rgba(99,102,241,.14),

        inset 0 0 40px rgba(99,102,241,.035);

}


.login-card::before {

    content: "";

    position: absolute;

    inset: -1px;

    border-radius: 28px;

    padding: 1px;

    background:

        linear-gradient(
            120deg,
            transparent,
            rgba(139,92,246,.65),
            rgba(34,211,238,.35),
            transparent
        );

    -webkit-mask:
        linear-gradient(#fff 0 0) content-box,
        linear-gradient(#fff 0 0);

    -webkit-mask-composite:
        xor;

    mask-composite:
        exclude;

    pointer-events: none;

}


.login-icon {

    text-align: center;

    font-size: 68px;

    filter:
        drop-shadow(
            0 0 20px rgba(139,92,246,.65)
        );

}


.login-title {

    text-align: center;

    margin-top: 10px;

    font-family:
        "Space Grotesk",
        sans-serif;

    font-size: 34px;

    font-weight: 700;

    color: #eef2ff;

}


.login-subtitle {

    text-align: center;

    margin-top: 8px;

    color: #64748b;

    font-size: 13px;

    line-height: 1.7;

}


/* ============================================================
   FOOTER
   ============================================================ */

.footer {

    text-align: center;

    margin-top: 35px;

    color: #475569;

    font-size: 10px;

    letter-spacing: .7px;

}


/* ============================================================
   MOBILE
   ============================================================ */

@media (max-width: 800px) {

    .main-title {

        font-size: 34px;

        letter-spacing: 2px;

    }

    .hero-title {

        font-size: 34px;

        letter-spacing: 2px;

    }

    .login-card {

        padding: 28px 20px;

    }

}

</style>

<div class="quantum-space"></div>
""",
    unsafe_allow_html=True,
)


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def refresh_sessions():
    """Load the user's chat sessions once when needed."""

    if not st.session_state.user_id:
        st.session_state.sessions = []
        return

    try:
        st.session_state.sessions = get_user_sessions(
            st.session_state.user_id
        )
    except Exception as e:
        st.session_state.sessions = []
        st.error(f"Could not load chats: {e}")


def get_current_chat():
    """Return current chat dictionary."""

    current_id = st.session_state.session_id

    for chat in st.session_state.sessions:

        sid = chat.get("session_id")

        if sid == current_id:
            return chat

    return None


def create_new_chat():
    """Create a new chat and make it active."""

    if not st.session_state.logged_in:
        return

    try:

        new_id = create_chat_session(
            st.session_state.user_id,
            "New Chat"
        )

        st.session_state.session_id = new_id

        st.session_state.messages = []

        st.session_state.rename_session_id = None

        refresh_sessions()

        st.toast("✨ New chat created!")

    except Exception as e:

        st.error(f"Could not create new chat: {e}")


def open_chat(session_id):
    """Restore selected chat."""

    try:

        messages = restore_chat(
            session_id,
            st.session_state.user_id
        )

        st.session_state.session_id = session_id

        st.session_state.messages = messages or []

        st.session_state.rename_session_id = None

    except Exception as e:

        st.error(f"Could not open chat: {e}")


def rename_current_chat(session_id, new_title):
    """
    IMPORTANT:
    rag_engine.rename_chat requires:
        session_id
        user_id
        new_title
    """

    new_title = new_title.strip()

    if not new_title:

        st.warning("Chat name cannot be empty.")

        return False

    try:

        rename_chat(
            session_id,
            st.session_state.user_id,
            new_title
        )

        st.session_state.rename_session_id = None

        st.toast("✏️ Chat renamed successfully!")

        refresh_sessions()

        return True

    except Exception as e:

        st.error(
            f"Rename failed: {e}"
        )

        return False


def delete_current_chat(session_id):
    """
    IMPORTANT:
    rag_engine.delete_chat requires:
        session_id
        user_id
    """

    if not session_id:
        return

    try:

        delete_chat(
            session_id,
            st.session_state.user_id
        )

        refresh_sessions()

        if st.session_state.sessions:

            next_id = (
                st.session_state.sessions[0]
                .get("session_id")
            )

            st.session_state.session_id = next_id

            try:

                st.session_state.messages = (
                    restore_chat(
                        next_id,
                        st.session_state.user_id
                    )
                    or []
                )

            except Exception:

                st.session_state.messages = []

        else:

            new_id = create_chat_session(
                st.session_state.user_id,
                "New Chat"
            )

            st.session_state.session_id = new_id

            st.session_state.messages = []

            refresh_sessions()

        st.session_state.rename_session_id = None

        st.toast("🗑️ Chat deleted successfully!")

    except Exception as e:

        st.error(
            f"Delete failed: {e}"
        )


def clear_conversation():
    """
    Clear only the current conversation.

    We create a fresh chat instead of modifying
    the existing database structure.
    """

    try:

        old_id = st.session_state.session_id

        if old_id:

            delete_chat(
                old_id,
                st.session_state.user_id
            )

        new_id = create_chat_session(
            st.session_state.user_id,
            "New Chat"
        )

        st.session_state.session_id = new_id

        st.session_state.messages = []

        refresh_sessions()

        st.toast("🧹 Conversation cleared!")

    except Exception as e:

        st.error(
            f"Could not clear conversation: {e}"
        )


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


def process_query(query):

    """Send a query to the AI backend."""

    query = query.strip()

    if not query:
        return

    if not st.session_state.logged_in:

        st.warning(
            "Please log in first."
        )

        return

    if st.session_state.session_id is None:

        create_new_chat()

    # --------------------------------------------------------
    # Display user message immediately
    # --------------------------------------------------------

    st.session_state.messages.append(
        {
            "sender": "user",
            "content": query
        }
    )

    # --------------------------------------------------------
    # AI
    # --------------------------------------------------------

    try:

        with st.spinner("⚛️ Quantum AI is thinking..."):

            answer = answer_question(
                query=query,
                session_id=st.session_state.session_id,
                user_id=st.session_state.user_id,
            )

    except Exception as e:

        answer = (
            "⚠️ I couldn't generate the answer.\n\n"
            f"**Error:** `{str(e)}`"
        )

    # --------------------------------------------------------
    # Display assistant response
    # --------------------------------------------------------

    st.session_state.messages.append(
        {
            "sender": "assistant",
            "content": answer
        }
    )


def transcribe_audio(audio_bytes):

    """Convert microphone audio into text."""

    if not SPEECH_RECOGNITION_AVAILABLE:

        st.warning(
            "Speech recognition is not installed. "
            "Run: pip install SpeechRecognition"
        )

        return ""

    try:

        recognizer = sr.Recognizer()

        audio_stream = io.BytesIO(
            audio_bytes
        )

        with sr.AudioFile(audio_stream) as source:

            audio_data = recognizer.record(
                source
            )

        return recognizer.recognize_google(
            audio_data
        )

    except sr.UnknownValueError:

        st.warning(
            "🎤 I couldn't understand the recording."
        )

        return ""

    except Exception as e:

        st.warning(
            f"🎤 Voice transcription failed: {e}"
        )

        return ""


# ============================================================
# LOGIN PAGE
# ============================================================

if not st.session_state.logged_in:

    st.markdown(
        """
        <div class="login-page">

            <div class="login-card">

                <div class="login-icon">
                    ⚛️
                </div>

                <div class="login-title">
                    QUANTUM AI TUTOR
                </div>

                <div class="login-subtitle">
                    Your intelligent learning companion for
                    Quantum Computing, Physics, Mathematics,
                    Programming and more.
                </div>

                <div style="
                    height:1px;
                    margin:24px 0;
                    background:
                    linear-gradient(
                        90deg,
                        transparent,
                        rgba(139,92,246,.45),
                        transparent
                    );
                "></div>

            </div>

        </div>
        """,
        unsafe_allow_html=True
    )

    # --------------------------------------------------------
    # Login box
    # --------------------------------------------------------

    login_col1, login_col2, login_col3 = st.columns(
        [1, 2, 1]
    )

    with login_col2:

        st.markdown(
            """
            <div style="
                color:#818cf8;
                font-size:11px;
                font-weight:700;
                letter-spacing:1.5px;
                margin-bottom:6px;
            ">
                SECURE LEARNING ACCESS
            </div>
            """,
            unsafe_allow_html=True
        )

        email = st.text_input(
            "Email address",
            placeholder="student@example.com",
            key="login_email",
        )

        if st.button(
            "🚀 Enter Quantum Lab",
            use_container_width=True,
            type="primary",
        ):

            clean_email = email.strip().lower()

            if not clean_email:

                st.error(
                    "Please enter your email address."
                )

            elif "@" not in clean_email:

                st.error(
                    "Please enter a valid email address."
                )

            else:

                try:

                    user_id = get_or_create_user(
                        clean_email
                    )

                    sessions = get_user_sessions(
                        user_id
                    )

                    if sessions:

                        active_session = sessions[0][
                            "session_id"
                        ]

                    else:

                        active_session = (
                            create_chat_session(
                                user_id,
                                "New Chat"
                            )
                        )

                    st.session_state.user_email = (
                        clean_email
                    )

                    st.session_state.user_id = (
                        user_id
                    )

                    st.session_state.session_id = (
                        active_session
                    )

                    st.session_state.logged_in = True

                    st.session_state.messages = []

                    st.session_state.sessions = (
                        sessions
                    )

                    if not sessions:

                        refresh_sessions()

                    # Restore existing conversation

                    try:

                        st.session_state.messages = (
                            restore_chat(
                                active_session,
                                user_id
                            )
                            or []
                        )

                    except Exception:

                        st.session_state.messages = []

                    st.toast(
                        "⚛️ Welcome to Quantum Lab!"
                    )

                    st.rerun()

                except Exception as e:

                    st.error(
                        f"Login failed: {e}"
                    )

        st.markdown(
            """
            <div style="
                text-align:center;
                margin-top:18px;
                color:#475569;
                font-size:10px;
            ">
                AI-powered • Context-aware • Interactive
            </div>
            """,
            unsafe_allow_html=True
        )

    st.stop()


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    # --------------------------------------------------------
    # BRAND
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # ACCOUNT
    # --------------------------------------------------------

    st.markdown(
        """
        <div class="account-card">

            <div class="account-label">
                ACCOUNT
            </div>

        </div>
        """,
        unsafe_allow_html=True
    )

    st.caption(
        st.session_state.user_email
    )

    if st.button(
        "🚪 Log Out",
        use_container_width=True,
    ):

        logout_user()

        st.rerun()

    st.markdown("---")

    # --------------------------------------------------------
    # NEW CHAT
    # --------------------------------------------------------

    if st.button(
        "＋  New Chat",
        use_container_width=True,
    ):

        create_new_chat()

        st.rerun()

    # --------------------------------------------------------
    # REFRESH CHAT LIST
    # --------------------------------------------------------

    refresh_sessions()

    # --------------------------------------------------------
    # CHAT HISTORY
    # --------------------------------------------------------

    st.markdown(
        '<div class="history-label">CHAT HISTORY</div>',
        unsafe_allow_html=True
    )

    if not st.session_state.sessions:

        st.caption(
            "No conversations yet."
        )

    else:

        for chat in st.session_state.sessions:

            session_id = chat.get(
                "session_id"
            )

            title = chat.get(
                "title",
                "New Chat"
            )

            if not title:
                title = "New Chat"

            is_current = (
                session_id
                ==
                st.session_state.session_id
            )

            if is_current:

                icon = "🟣"

            else:

                icon = "💬"

            # --------------------------------------------
            # Chat row
            # --------------------------------------------

            col_chat, col_edit, col_delete = st.columns(
                [0.62, 0.19, 0.19],
                gap="small"
            )

            with col_chat:

                display_title = title

                if len(display_title) > 20:

                    display_title = (
                        display_title[:20]
                        + "..."
                    )

                if st.button(
                    f"{icon} {display_title}",
                    key=f"open_chat_{session_id}",
                    use_container_width=True,
                ):

                    open_chat(
                        session_id
                    )

                    st.rerun()

            # --------------------------------------------
            # RENAME
            # --------------------------------------------

            with col_edit:

                if st.button(
                    "✏️",
                    key=f"edit_chat_{session_id}",
                    help="Rename chat",
                    use_container_width=True,
                ):

                    st.session_state.rename_session_id = (
                        session_id
                    )

                    st.session_state.rename_value = (
                        title
                    )

                    st.rerun()

            # --------------------------------------------
            # DELETE
            # --------------------------------------------

            with col_delete:

                if st.button(
                    "🗑️",
                    key=f"delete_chat_{session_id}",
                    help="Delete chat",
                    use_container_width=True,
                ):

                    delete_current_chat(
                        session_id
                    )

                    st.rerun()

            # --------------------------------------------
            # RENAME PANEL
            # --------------------------------------------

            if (
                st.session_state.rename_session_id
                == session_id
            ):

                st.markdown(
                    '<div class="rename-box">',
                    unsafe_allow_html=True
                )

                new_title = st.text_input(
                    "Chat name",
                    value=st.session_state.rename_value,
                    key=f"rename_input_{session_id}",
                )

                rename_col1, rename_col2 = st.columns(2)

                with rename_col1:

                    if st.button(
                        "Save",
                        key=f"save_rename_{session_id}",
                        use_container_width=True,
                    ):

                        if rename_current_chat(
                            session_id,
                            new_title
                        ):

                            st.rerun()

                with rename_col2:

                    if st.button(
                        "Cancel",
                        key=f"cancel_rename_{session_id}",
                        use_container_width=True,
                    ):

                        st.session_state.rename_session_id = (
                            None
                        )

                        st.rerun()

                st.markdown(
                    "</div>",
                    unsafe_allow_html=True
                )

    # --------------------------------------------------------
    # CHAT ACTIONS
    # --------------------------------------------------------

    st.markdown("---")

    if st.button(
        "🧹 Clear Conversation",
        use_container_width=True,
    ):

        clear_conversation()

        st.rerun()

    # --------------------------------------------------------
    # LEARNING INFO
    # --------------------------------------------------------

    st.markdown("---")

    st.markdown(
        """
        <div class="tool-card">

            <div class="tool-title">
                🧠 Learning Mode
            </div>

            <div class="tool-description">
                Ask naturally about quantum computing,
                programming, mathematics, physics and more.
            </div>

        </div>

        <div class="tool-card">

            <div class="tool-title">
                🌐 Smart Knowledge
            </div>

            <div class="tool-description">
                Conversation context and web knowledge
                can be used by the AI tutor when required.
            </div>

        </div>
        """,
        unsafe_allow_html=True
    )


# ============================================================
# MAIN HERO
# ============================================================

st.markdown(
    """
    <div class="hero">

        <div class="hero-orbit">
            ⚛️
        </div>

        <div class="hero-title">
            QUANTUM LAB
        </div>

        <div class="hero-subtitle">
            Interactive AI Tutor for Quantum Computing
            & Advanced Learning
        </div>

        <div class="online-pill">
            <span class="online-dot"></span>
            AI TUTOR ONLINE
        </div>

    </div>

    <div class="glow-line"></div>
    """,
    unsafe_allow_html=True
)


# ============================================================
# CURRENT CHAT TITLE
# ============================================================

current_chat = get_current_chat()

if current_chat:

    safe_title = html.escape(
        current_chat.get(
            "title",
            "New Chat"
        )
    )

    st.markdown(
        f"""
        <div style="
            text-align:center;
            margin-bottom:18px;
            color:#a5b4fc;
            font-size:13px;
        ">
            ◈ {safe_title}
        </div>
        """,
        unsafe_allow_html=True
    )


# ============================================================
# EMPTY STATE
# ============================================================

if not st.session_state.messages:

    st.markdown(
        """
        <div class="empty-state">

            <div class="empty-icon">
                ✦
            </div>

            <div class="empty-title">
                What will you explore today?
            </div>

            <div class="empty-text">
                Ask your AI tutor anything — from qubits,
                superposition and quantum gates to Java,
                Python, mathematics, physics and programming.
            </div>

        </div>
        """,
        unsafe_allow_html=True
    )


# ============================================================
# CHAT MESSAGES
# ============================================================

for message in st.session_state.messages:

    sender = message.get(
        "sender",
        message.get("role", "assistant")
    )

    content = message.get(
        "content",
        ""
    )

    role = (
        "user"
        if sender == "user"
        else "assistant"
    )

    with st.chat_message(role):

        st.markdown(
            content
        )


# ============================================================
# CANVAS
# ============================================================

if st.session_state.show_canvas:

    st.markdown(
        """
        <div class="canvas-box">

            <div class="canvas-title">
                🎨 Quantum Canvas
            </div>

            <div style="
                color:#64748b;
                margin-top:5px;
                margin-bottom:14px;
                font-size:12px;
            ">
                Write equations, concepts, ideas,
                diagrams or study notes.
            </div>

        </div>
        """,
        unsafe_allow_html=True
    )

    canvas_text = st.text_area(
        "Canvas workspace",
        placeholder=(
            "Start writing your quantum notes here..."
        ),
        height=250,
        key="canvas_workspace",
        label_visibility="collapsed",
    )

    canvas_col1, canvas_col2 = st.columns(2)

    with canvas_col1:

        if st.button(
            "💾 Save Canvas",
            use_container_width=True,
        ):

            st.toast(
                "Canvas saved for this session."
            )

    with canvas_col2:

        if st.button(
            "✕ Close Canvas",
            use_container_width=True,
        ):

            st.session_state.show_canvas = False

            st.rerun()


# ============================================================
# PROMPT AREA
# ============================================================

st.markdown(
    """
    <div class="prompt-container">
        <div class="prompt-inner">
            <div class="prompt-label">
                ASK YOUR QUANTUM AI TUTOR
            </div>
    """,
    unsafe_allow_html=True
)


# ============================================================
# PROMPT ROW
# ============================================================

prompt_col1, prompt_col2, prompt_col3, prompt_col4 = st.columns(
    [0.08, 0.68, 0.08, 0.16],
    vertical_alignment="center"
)


# ============================================================
# PLUS POPUP
# ============================================================

with prompt_col1:

    st.markdown(
        '<div class="plus-button">',
        unsafe_allow_html=True
    )

    with st.popover(
        "＋",
        use_container_width=True
    ):

        st.markdown(
            """
            <div style="
                font-family:'Space Grotesk';
                font-size:19px;
                font-weight:700;
                color:#e0e7ff;
                margin-bottom:4px;
            ">
                Tools & Attachments
            </div>

            <div style="
                color:#64748b;
                font-size:11px;
                margin-bottom:14px;
            ">
                Enhance your learning session
            </div>
            """,
            unsafe_allow_html=True
        )

        tab_files, tab_drive, tab_tools = st.tabs(
            [
                "📁 Files",
                "☁️ Drive",
                "🛠️ Tools"
            ]
        )

        # ----------------------------------------------------
        # FILES
        # ----------------------------------------------------

        with tab_files:

            uploaded = st.file_uploader(
                "Photos & files",
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
                    "cpp",
                    "md",
                ],
                accept_multiple_files=True,
                key="quantum_attachments",
            )

            if uploaded:

                st.session_state.uploaded_files = (
                    uploaded
                )

                st.success(
                    f"📎 {len(uploaded)} file(s) attached"
                )

                for file in uploaded:

                    st.caption(
                        f"• {file.name}"
                    )

        # ----------------------------------------------------
        # GOOGLE DRIVE
        # ----------------------------------------------------

        with tab_drive:

            st.markdown(
                """
                <div class="tool-card">

                    <div class="tool-title">
                        ☁️ Google Drive
                    </div>

                    <div class="tool-description">
                        Paste a Drive file link to attach
                        it to your learning session.
                    </div>

                </div>
                """,
                unsafe_allow_html=True
            )

            drive_url = st.text_input(
                "Drive link",
                placeholder="Paste Google Drive link",
                key="drive_link_input",
            )

            if st.button(
                "Attach Drive File",
                use_container_width=True,
            ):

                clean_link = drive_url.strip()

                if clean_link:

                    if clean_link not in (
                        st.session_state.drive_links
                    ):

                        st.session_state.drive_links.append(
                            clean_link
                        )

                    st.success(
                        "☁️ Drive file attached."
                    )

                else:

                    st.warning(
                        "Paste a Google Drive link first."
                    )

        # ----------------------------------------------------
        # TOOLS
        # ----------------------------------------------------

        with tab_tools:

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
                    "Quantum Calculator activated."
                )

            if st.button(
                "🧠 Learning Mode",
                use_container_width=True,
            ):

                st.session_state.learning_mode = True

                st.success(
                    "Learning Mode activated."
                )

            if st.button(
                "📝 Notes",
                use_container_width=True,
            ):

                st.session_state.show_canvas = True

                st.rerun()

    st.markdown(
        "</div>",
        unsafe_allow_html=True
    )


# ============================================================
# TEXT INPUT
# ============================================================

with prompt_col2:

    # IMPORTANT:
    # Versioned key solves:
    #
    # StreamlitWidgetAlreadyInstantiatedError
    #
    # We NEVER do:
    #
    # st.session_state.custom_prompt = ""
    #
    # after creating the widget.

    prompt_key = (
        f"prompt_input_{st.session_state.prompt_version}"
    )

    user_prompt = st.text_input(
        "Message",
        placeholder=(
            "Ask anything about quantum computing..."
        ),
        key=prompt_key,
        label_visibility="collapsed",
    )


# ============================================================
# MICROPHONE
# ============================================================

with prompt_col3:

    st.markdown(
        '<div class="mic-button">',
        unsafe_allow_html=True
    )

    audio_value = st.audio_input(
        "🎤",
        key="quantum_microphone",
        label_visibility="collapsed",
    )

    st.markdown(
        "</div>",
        unsafe_allow_html=True
    )


# ============================================================
# SEND
# ============================================================

with prompt_col4:

    st.markdown(
        '<div class="send-button">',
        unsafe_allow_html=True
    )

    send_clicked = st.button(
        "➤ Send",
        use_container_width=True,
        disabled=st.session_state.processing,
    )

    st.markdown(
        "</div>",
        unsafe_allow_html=True
    )


st.markdown(
    """
        </div>
    </div>
    """,
    unsafe_allow_html=True
)


# ============================================================
# ATTACHMENT STATUS
# ============================================================

if (
    st.session_state.uploaded_files
    or st.session_state.drive_links
):

    attachment_col1, attachment_col2 = st.columns(2)

    with attachment_col1:

        if st.session_state.uploaded_files:

            st.caption(
                "📎 "
                +
                ", ".join(
                    file.name
                    for file in
                    st.session_state.uploaded_files
                )
            )

    with attachment_col2:

        if st.session_state.drive_links:

            st.caption(
                f"☁️ "
                f"{len(st.session_state.drive_links)} "
                f"Drive file(s) attached"
            )


# ============================================================
# VOICE PROCESSING
# ============================================================

voice_query = ""

if (
    audio_value is not None
    and send_clicked
):

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

        voice_query = transcribe_audio(
            audio_bytes
        )


# ============================================================
# FINAL QUERY
# ============================================================

final_query = ""

if send_clicked:

    typed_query = (
        user_prompt.strip()
        if user_prompt
        else ""
    )

    if typed_query:

        final_query = typed_query

    elif voice_query:

        final_query = voice_query

    else:

        st.warning(
            "Type a question or record a voice message."
        )


# ============================================================
# PROCESS
# ============================================================

if final_query:

    st.session_state.processing = True

    process_query(
        final_query
    )

    st.session_state.processing = False

    # --------------------------------------------------------
    # Instead of changing the already-created widget state,
    # create a new widget key on the next rerun.
    # --------------------------------------------------------

    st.session_state.prompt_version += 1

    st.rerun()


# ============================================================
# FOOTER
# ============================================================

st.markdown(
    """
    <div class="footer">

        ⚛️ QUANTUM LAB AI TUTOR
        &nbsp;•&nbsp;
        Intelligent Learning Environment

    </div>
    """,
    unsafe_allow_html=True
)
