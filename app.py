import io
import hashlib
import inspect
import html

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
# EXISTING RAG + DATABASE IMPORTS
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
    "learning_mode": False,
    "show_notes": False,

    "canvas_text": "",
    "notes_text": "",

    # IMPORTANT:
    # We use a changing widget key instead of
    # modifying st.session_state.custom_prompt
    # after the widget is created.
    "prompt_nonce": 0,

    "voice_recording_nonce": 0,
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

    font-family: "Inter", sans-serif;

}

.stApp {

    min-height: 100vh;

    background:
        radial-gradient(
            circle at 10% 10%,
            rgba(99,102,241,0.18),
            transparent 28%
        ),

        radial-gradient(
            circle at 88% 12%,
            rgba(59,130,246,0.13),
            transparent 25%
        ),

        radial-gradient(
            circle at 72% 78%,
            rgba(168,85,247,0.13),
            transparent 28%
        ),

        linear-gradient(
            135deg,
            #020617 0%,
            #070a20 45%,
            #030615 100%
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

    background-size: 52px 52px;

    z-index: 0;

}


/* =========================================================
   STAR FIELD
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
            circle at 5% 15%,
            rgba(255,255,255,.95) 0px,
            transparent 2px
        ),

        radial-gradient(
            circle at 14% 38%,
            rgba(180,210,255,.80) 0px,
            transparent 2px
        ),

        radial-gradient(
            circle at 29% 18%,
            rgba(200,180,255,.85) 0px,
            transparent 2px
        ),

        radial-gradient(
            circle at 58% 28%,
            rgba(200,180,255,.95) 0px,
            transparent 2px
        ),

        radial-gradient(
            circle at 82% 18%,
            rgba(180,210,255,.75) 0px,
            transparent 2px
        ),

        radial-gradient(
            circle at 91% 70%,
            rgba(200,180,255,.85) 0px,
            transparent 2px
        );

    animation: starFloat 18s ease-in-out infinite alternate;

}


@keyframes starFloat {

    0% {

        transform:
            translate3d(0,0,0);

        opacity: .55;

    }

    50% {

        transform:
            translate3d(0,-5px,0);

        opacity: .9;

    }

    100% {

        transform:
            translate3d(0,4px,0);

        opacity: .65;

    }

}


/* =========================================================
   MAIN CONTAINER
   ========================================================= */

.main .block-container {

    max-width: 1280px;

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
            #030611 0%,
            #070b1d 50%,
            #02040c 100%
        );

    border-right:
        1px solid rgba(139,92,246,.20);

}


section[data-testid="stSidebar"] > div {

    padding-top: 1.2rem;

}


section[data-testid="stSidebar"] .stButton button {

    border-radius: 12px;

    border:
        1px solid rgba(139,92,246,.16);

    background:
        linear-gradient(
            135deg,
            rgba(18,25,53,.96),
            rgba(7,12,29,.96)
        );

    color: #dbeafe;

    transition:
        all .2s ease;

}


section[data-testid="stSidebar"] .stButton button:hover {

    border-color:
        rgba(167,139,250,.60);

    box-shadow:
        0 0 22px rgba(139,92,246,.18);

    transform:
        translateY(-1px);

}


/* =========================================================
   SIDEBAR LOGO
   ========================================================= */

.sidebar-atom {

    text-align: center;

    font-size: 38px;

    margin-bottom: 4px;

    filter:
        drop-shadow(
            0 0 12px
            rgba(139,92,246,.85)
        );

}


.sidebar-title {

    text-align: center;

    font-family:
        "Space Grotesk",
        sans-serif;

    font-size: 20px;

    font-weight: 700;

    letter-spacing: 2px;

    color: #e0e7ff;

}


/* =========================================================
   MAIN LOGO
   ========================================================= */

.quantum-logo {

    text-align: center;

    font-size: 64px;

    line-height: 1;

    margin:
        8px auto 5px auto;

    text-shadow:

        0 0 8px #ffffff,

        0 0 20px
        rgba(139,92,246,1),

        0 0 45px
        rgba(99,102,241,.9);

    animation:
        quantumPulse 3s
        ease-in-out infinite;

}


@keyframes quantumPulse {

    0%,
    100% {

        transform:
            scale(1);

        filter:
            brightness(1);

    }

    50% {

        transform:
            scale(1.06);

        filter:
            brightness(1.22);

    }

}


/* =========================================================
   MAIN TITLE
   ========================================================= */

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
        1px solid rgba(34,197,94,.22);

    font-size: 10px;

    font-weight: 700;

    letter-spacing: 1.7px;

    box-shadow:
        0 0 20px
        rgba(34,197,94,.08);

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
        0 0 14px
        rgba(139,92,246,.4);

}


/* =========================================================
   CHAT MESSAGES
   ========================================================= */

[data-testid="stChatMessage"] {

    border-radius: 18px;

    border:
        1px solid
        rgba(139,92,246,.12);

    background:

        linear-gradient(
            135deg,
            rgba(15,23,42,.84),
            rgba(7,12,28,.84)
        );

    margin-bottom: 10px;

    transition:
        all .2s ease;

}


[data-testid="stChatMessage"]:hover {

    border-color:
        rgba(139,92,246,.32);

    box-shadow:
        0 8px 30px
        rgba(0,0,0,.20);

}


[data-testid="stChatMessage"] p {

    color: #dbe4f0;

    line-height: 1.7;

}


/* =========================================================
   PROMPT CONTAINER
   ========================================================= */

.prompt-shell {

    width: 100%;

    margin:
        30px auto 8px auto;

    padding: 4px;

    border-radius: 23px;

    background:

        linear-gradient(
            135deg,
            rgba(255,255,255,.055),
            rgba(99,102,241,.09),
            rgba(255,255,255,.025)
        );

    border:
        1px solid
        rgba(139,92,246,.28);

    box-shadow:

        0 0 0 1px
        rgba(99,102,241,.025),

        0 0 28px
        rgba(99,102,241,.08);

    transition:
        all .3s ease;

}


.prompt-shell:focus-within {

    border-color:
        rgba(129,140,248,.72);

    box-shadow:

        0 0 0 1px
        rgba(99,102,241,.10),

        0 0 25px
        rgba(99,102,241,.18),

        0 0 55px
        rgba(139,92,246,.10);

}


.prompt-inner {

    min-height: 60px;

    display: flex;

    align-items: center;

    padding:
        3px 5px;

    border-radius: 19px;

    background:

        linear-gradient(
            135deg,
            #202020,
            #242424
        );

}


/* =========================================================
   PROMPT INPUT
   ========================================================= */

.prompt-input {

    padding:
        0 5px;

}


.prompt-input div[data-baseweb="input"] {

    background:
        transparent !important;

    border:
        none !important;

    box-shadow:
        none !important;

}


.prompt-input input {

    background:
        transparent !important;

    border:
        none !important;

    outline:
        none !important;

    box-shadow:
        none !important;

    color:
        #f8fafc !important;

    font-size:
        15px !important;

}


.prompt-input input::placeholder {

    color:
        #a1a1aa !important;

    opacity:
        1 !important;

}


/* =========================================================
   REMOVE STREAMLIT INPUT OUTER BORDER
   ========================================================= */

.prompt-input [data-baseweb="input"] {

    border:
        none !important;

}


/* =========================================================
   THINK BUTTON
   ========================================================= */

.think-area button {

    background:
        transparent !important;

    border:
        none !important;

    color:
        #b8b8bd !important;

    font-size:
        14px !important;

    font-weight:
        500 !important;

    min-height:
        42px !important;

    padding:
        8px 10px !important;

    box-shadow:
        none !important;

}


.think-area button:hover {

    color:
        #ffffff !important;

    background:
        rgba(255,255,255,.07) !important;

    border-radius:
        12px !important;

}


/* =========================================================
   MICROPHONE BUTTON
   ========================================================= */

.mic-area {

    display:
        flex;

    align-items:
        center;

    justify-content:
        center;

}


.mic-area button {

    width:
        42px !important;

    height:
        42px !important;

    min-height:
        42px !important;

    padding:
        0 !important;

    border:
        none !important;

    border-radius:
        50% !important;

    background:
        transparent !important;

    color:
        #eeeeee !important;

    font-size:
        19px !important;

    box-shadow:
        none !important;

    transition:
        all .2s ease;

}


.mic-area button:hover {

    background:
        rgba(255,255,255,.09) !important;

    transform:
        scale(1.08);

}


/* =========================================================
   SEND BUTTON
   ========================================================= */

.send-area {

    display:
        flex;

    align-items:
        center;

    justify-content:
        center;

}


.send-area button {

    width:
        45px !important;

    height:
        45px !important;

    min-height:
        45px !important;

    padding:
        0 !important;

    border-radius:
        50% !important;

    border:
        1px solid
        rgba(147,197,253,.55) !important;

    background:

        linear-gradient(
            135deg,
            #3b82f6,
            #2563eb
        ) !important;

    color:
        white !important;

    font-size:
        23px !important;

    font-weight:
        700 !important;

    box-shadow:
        0 0 18px
        rgba(59,130,246,.32);

    transition:
        all .2s ease;

}


.send-area button:hover {

    transform:
        scale(1.09);

    box-shadow:
        0 0 30px
        rgba(59,130,246,.55);

}


/* =========================================================
   PROMPT FOOTER
   ========================================================= */

.prompt-hint {

    text-align:
        center;

    color:
        #64748b;

    font-size:
        10px;

    margin-top:
        7px;

}


/* =========================================================
   TOOL CARD
   ========================================================= */

.tool-card {

    padding:
        13px;

    border-radius:
        14px;

    border:
        1px solid
        rgba(139,92,246,.20);

    background:
        rgba(10,15,35,.90);

    margin-bottom:
        9px;

}


/* =========================================================
   CANVAS
   ========================================================= */

.canvas-box {

    margin-top:
        20px;

    padding:
        25px;

    min-height:
        300px;

    border-radius:
        20px;

    border:
        1px solid
        rgba(99,102,241,.30);

    background:

        linear-gradient(
            135deg,
            rgba(15,23,42,.94),
            rgba(10,15,35,.94)
        );

    box-shadow:
        0 0 35px
        rgba(99,102,241,.10);

}


/* =========================================================
   LOGIN BOX
   ========================================================= */

.login-box {

    max-width:
        540px;

    margin:
        50px auto;

    padding:
        40px;

    border-radius:
        26px;

    border:
        1px solid
        rgba(139,92,246,.28);

    background:

        linear-gradient(
            135deg,
            rgba(15,23,42,.95),
            rgba(7,12,28,.95)
        );

    box-shadow:

        0 0 50px
        rgba(99,102,241,.13),

        inset 0 0 35px
        rgba(99,102,241,.035);

}


/* =========================================================
   LOGIN BUTTON
   ========================================================= */

.login-button button {

    background:

        linear-gradient(
            135deg,
            #6366f1,
            #3b82f6
        ) !important;

    color:
        white !important;

    border:
        1px solid
        rgba(165,180,252,.55) !important;

    box-shadow:
        0 0 20px
        rgba(99,102,241,.25);

}


/* =========================================================
   SIDEBAR CHAT ACTIVE
   ========================================================= */

.chat-active {

    border:
        1px solid
        rgba(139,92,246,.40);

    background:
        rgba(99,102,241,.08);

}


/* =========================================================
   VOICE RECORDING AREA
   ========================================================= */

.voice-box {

    margin-top:
        10px;

    padding:
        14px;

    border-radius:
        16px;

    border:
        1px solid
        rgba(99,102,241,.25);

    background:
        rgba(10,15,35,.88);

}


/* =========================================================
   HIDE UNNECESSARY INPUT LABELS
   ========================================================= */

.prompt-shell label {

    display:
        none !important;

}

</style>

<div class="quantum-space"></div>
""",
    unsafe_allow_html=True,
)


# =========================================================
# DATABASE COMPATIBILITY HELPERS
# =========================================================

def call_with_supported_signature(function, values):
    """
    Calls a database function using the arguments that its
    actual signature supports.

    This makes the app compatible with common versions of
    rename_chat() and delete_chat().
    """

    try:

        signature = inspect.signature(function)

        parameters = [
            parameter
            for parameter in signature.parameters.values()
            if parameter.kind
            in (
                inspect.Parameter.POSITIONAL_ONLY,
                inspect.Parameter.POSITIONAL_OR_KEYWORD,
            )
        ]

        required_count = len(
            [
                parameter
                for parameter in parameters
                if parameter.default
                is inspect.Parameter.empty
            ]
        )

        parameter_names = [
            parameter.name.lower()
            for parameter in parameters
        ]

        # -------------------------------------------------
        # Named argument matching
        # -------------------------------------------------

        mapped = {}

        for name in parameter_names:

            if name in ("user_id", "userid", "user"):

                mapped[name] = values.get("user_id")

            elif name in (
                "session_id",
                "sessionid",
                "chat_id",
                "chatid",
            ):

                mapped[name] = values.get("session_id")

            elif name in (
                "new_title",
                "title",
                "chat_title",
                "name",
            ):

                mapped[name] = values.get("new_title")

        if len(mapped) >= required_count:

            try:

                return function(**mapped)

            except TypeError:

                pass

        # -------------------------------------------------
        # Positional fallback
        # -------------------------------------------------

        possible_orders = [

            [
                values.get("user_id"),
                values.get("session_id"),
                values.get("new_title"),
            ],

            [
                values.get("session_id"),
                values.get("new_title"),
                values.get("user_id"),
            ],

            [
                values.get("session_id"),
                values.get("new_title"),
            ],

            [
                values.get("user_id"),
                values.get("session_id"),
            ],

            [
                values.get("session_id"),
            ],
        ]

        for arguments in possible_orders:

            arguments = arguments[: len(parameters)]

            if len(arguments) < required_count:

                continue

            try:

                return function(*arguments)

            except TypeError:

                continue

        raise TypeError(
            f"Could not determine arguments for "
            f"{function.__name__}()"
        )

    except Exception:

        raise


# =========================================================
# REFRESH CHAT HISTORY
# =========================================================

def refresh_sessions():

    if not st.session_state.user_id:

        st.session_state.sessions = []

        return

    try:

        result = get_user_sessions(
            st.session_state.user_id
        )

        if result is None:

            result = []

        st.session_state.sessions = result

    except Exception as error:

        st.error(
            f"Could not load chat history: {error}"
        )

        st.session_state.sessions = []


# =========================================================
# CREATE NEW CHAT
# =========================================================

def start_new_chat():

    if not st.session_state.logged_in:

        return

    try:

        new_session_id = create_chat_session(
            st.session_state.user_id,
            "New Chat",
        )

        st.session_state.session_id = (
            new_session_id
        )

        st.session_state.messages = []

        st.session_state.rename_session_id = None

        refresh_sessions()

    except Exception as error:

        st.error(
            f"Could not create new chat: {error}"
        )


# =========================================================
# RESTORE CHAT
# =========================================================

def load_chat(session_id):

    try:

        restored_messages = restore_chat(
            session_id
        )

        if restored_messages is None:

            restored_messages = []

        st.session_state.session_id = (
            session_id
        )

        st.session_state.messages = (
            restored_messages
        )

        st.session_state.rename_session_id = None

    except Exception as error:

        st.error(
            f"Could not restore chat: {error}"
        )


# =========================================================
# DELETE CHAT
# =========================================================

def remove_chat(session_id):

    try:

        call_with_supported_signature(
            delete_chat,
            {
                "user_id":
                    st.session_state.user_id,

                "session_id":
                    session_id,

                "new_title":
                    None,
            },
        )

    except Exception as error:

        st.error(
            f"Delete failed: {error}"
        )

        return False

    # -----------------------------------------------------
    # If deleted chat was active
    # -----------------------------------------------------

    if (
        st.session_state.session_id
        == session_id
    ):

        st.session_state.session_id = None

        st.session_state.messages = []

    refresh_sessions()

    return True


# =========================================================
# RENAME CHAT
# =========================================================

def rename_current_chat(
    session_id,
    new_title,
):

    if not new_title.strip():

        st.warning(
            "Chat name cannot be empty."
        )

        return False

    try:

        call_with_supported_signature(
            rename_chat,
            {
                "user_id":
                    st.session_state.user_id,

                "session_id":
                    session_id,

                "new_title":
                    new_title.strip(),
            },
        )

        refresh_sessions()

        return True

    except Exception as error:

        st.error(
            f"Rename failed: {error}"
        )

        return False


# =========================================================
# LOGOUT
# =========================================================

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

    st.session_state.learning_mode = False

    st.session_state.show_notes = False

    st.session_state.prompt_nonce += 1


# =========================================================
# PROCESS QUERY
# =========================================================

def process_query(user_query):

    if not user_query:

        return

    if not st.session_state.logged_in:

        st.warning(
            "Please log in first."
        )

        return

    # -----------------------------------------------------
    # Automatically create chat
    # -----------------------------------------------------

    if st.session_state.session_id is None:

        start_new_chat()

    if st.session_state.session_id is None:

        st.error(
            "Unable to create a chat session."
        )

        return

    # -----------------------------------------------------
    # Add user message
    # -----------------------------------------------------

    st.session_state.messages.append(
        {
            "role": "user",
            "content": user_query,
        }
    )

    # -----------------------------------------------------
    # Ask RAG engine
    # -----------------------------------------------------

    try:

        with st.spinner(
            "⚛️ Quantum AI is thinking..."
        ):

            answer = answer_question(
                query=user_query,

                session_id=
                    st.session_state.session_id,

                user_id=
                    st.session_state.user_id,
            )

    except Exception as error:

        answer = (
            "⚠️ I couldn't generate a response "
            "right now.\n\n"
            f"**Error:** `{str(error)}`"
        )

    # -----------------------------------------------------
    # Add assistant message
    # -----------------------------------------------------

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": answer,
        }
    )

    # -----------------------------------------------------
    # Refresh chat list
    # -----------------------------------------------------

    refresh_sessions()


# =========================================================
# SIDEBAR
# =========================================================

with st.sidebar:

    st.markdown(
        """
        <div class="sidebar-atom">
            ⚛️
        </div>

        <div class="sidebar-title">
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


    if not st.session_state.logged_in:

        email = st.text_input(
            "Email",
            placeholder="student@example.com",
            key="login_email",
        )

        st.markdown(
            '<div class="login-button">',
            unsafe_allow_html=True,
        )

        login_clicked = st.button(
            "🔑 Log In",
            use_container_width=True,
        )

        st.markdown(
            "</div>",
            unsafe_allow_html=True,
        )


        if login_clicked:

            clean_email = email.strip()

            if not clean_email:

                st.warning(
                    "Please enter your email."
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

                    refresh_sessions()

                    st.rerun()

                except Exception as error:

                    st.error(
                        f"Login failed: {error}"
                    )


    else:

        safe_email = html.escape(
            st.session_state.user_email
        )

        st.markdown(
            f"""
            <div style="
                padding:13px;
                border-radius:13px;

                background:
                    linear-gradient(
                        135deg,
                        rgba(99,102,241,.13),
                        rgba(59,130,246,.06)
                    );

                border:
                    1px solid
                    rgba(99,102,241,.24);

                color:#cbd5e1;

                font-size:12px;
            ">

                <span style="
                    color:#94a3b8;
                ">
                    👤 Logged in as
                </span>

                <br>

                <strong style="
                    color:#e0e7ff;
                ">
                    {safe_email}
                </strong>

            </div>
            """,
            unsafe_allow_html=True,
        )

        st.write("")

        if st.button(
            "🚪 Log Out",
            use_container_width=True,
        ):

            logout_user()

            st.rerun()


    # =====================================================
    # CHAT SECTION
    # =====================================================

    if st.session_state.logged_in:

        st.markdown("---")

        st.subheader("💬 Chats")


        # =================================================
        # NEW CHAT
        # =================================================

        if st.button(
            "＋  New Chat",
            use_container_width=True,
        ):

            start_new_chat()

            st.rerun()


        st.markdown(
            """
            <div style="
                color:#94a3b8;
                font-size:10px;
                font-weight:700;
                letter-spacing:1.5px;
                margin:14px 0 9px 0;
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
                    "New Chat",
                )

                if not title:

                    title = "New Chat"

                safe_title = html.escape(
                    str(title)
                )

                selected = (
                    session_id
                    ==
                    st.session_state.session_id
                )


                # =========================================
                # CHAT ROW
                # =========================================

                col1, col2, col3 = st.columns(
                    [0.62, 0.19, 0.19],
                    gap="small",
                )


                # =========================================
                # SELECT CHAT
                # =========================================

                with col1:

                    prefix = (
                        "🟣"
                        if selected
                        else "💬"
                    )

                    display_title = str(
                        title
                    )

                    if len(display_title) > 21:

                        display_title = (
                            display_title[:21]
                            + "..."
                        )

                    if st.button(
                        f"{prefix} {display_title}",
                        key=f"open_chat_{session_id}",
                        use_container_width=True,
                    ):

                        load_chat(
                            session_id
                        )

                        st.rerun()


                # =========================================
                # RENAME
                # =========================================

                with col2:

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


                # =========================================
                # DELETE
                # =========================================

                with col3:

                    if st.button(
                        "🗑️",
                        key=f"delete_chat_{session_id}",
                        help="Delete chat",
                        use_container_width=True,
                    ):

                        if remove_chat(
                            session_id
                        ):

                            st.session_state.rename_session_id = (
                                None
                            )

                            st.rerun()


                # =========================================
                # RENAME PANEL
                # =========================================

                if (
                    st.session_state.rename_session_id
                    == session_id
                ):

                    new_title = st.text_input(
                        "New chat name",
                        value=str(title),
                        key=f"rename_input_{session_id}",
                    )


                    rename_col1, rename_col2 = (
                        st.columns(2)
                    )


                    with rename_col1:

                        if st.button(
                            "Save",
                            key=f"save_rename_{session_id}",
                            use_container_width=True,
                        ):

                            if rename_current_chat(
                                session_id,
                                new_title,
                            ):

                                st.session_state.rename_session_id = (
                                    None
                                )

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


        # =================================================
        # CLEAR CONVERSATION
        # =================================================

        st.markdown("---")

        if st.button(
            "🧹 Clear Conversation",
            use_container_width=True,
        ):

            st.session_state.messages = []

            st.success(
                "Current conversation cleared."
            )

            st.rerun()


        # =================================================
        # CURRENT CHAT
        # =================================================

        if st.session_state.session_id:

            st.markdown("---")

            st.caption(
                "Current Chat"
            )

            st.code(
                str(
                    st.session_state.session_id
                ),
                language="text",
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
                font-size:72px;

                text-shadow:
                    0 0 12px #fff,
                    0 0 28px rgba(139,92,246,.9);
            ">
                ⚛️
            </div>

            <div style="
                text-align:center;

                font-family:
                    'Space Grotesk';

                font-size:31px;

                font-weight:700;

                letter-spacing:2px;

                color:#e0e7ff;

                margin-top:12px;
            ">
                QUANTUM AI TUTOR
            </div>

            <div style="
                text-align:center;

                color:#94a3b8;

                margin-top:13px;

                line-height:1.8;

                font-size:14px;
            ">
                Explore quantum computing,
                advanced physics and complex concepts
                through an intelligent AI-powered tutor.
            </div>

            <div style="
                text-align:center;

                margin-top:22px;

                color:#6366f1;

                font-size:11px;

                letter-spacing:2px;

                font-weight:700;
            ">
                LEARN • EXPLORE • DISCOVER
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
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="quantum-line"></div>',
    unsafe_allow_html=True,
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

        if (
            sid
            ==
            st.session_state.session_id
        ):

            current_title = chat.get(
                "title",
                "New Chat",
            )

            break

    safe_current_title = html.escape(
        str(current_title)
    )

    st.markdown(
        f"""
        <div style="
            text-align:center;

            color:#a5b4fc;

            font-size:13px;

            margin-bottom:15px;

            font-weight:500;
        ">
            💬 {safe_current_title}
        </div>
        """,
        unsafe_allow_html=True,
    )


# =========================================================
# CHAT DISPLAY
# =========================================================

for message in st.session_state.messages:

    role = message.get(
        "role",
        "assistant",
    )

    content = message.get(
        "content",
        "",
    )

    with st.chat_message(role):

        st.markdown(content)


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
            ">
                🎨 Canvas Workbench
            </div>

            <div style="
                color:#94a3b8;
                margin-top:7px;
                line-height:1.7;
            ">
                Create quantum notes, equations,
                explanations, diagrams and ideas.
            </div>

        </div>
        """,
        unsafe_allow_html=True,
    )

    canvas_text = st.text_area(
        "Canvas",
        value=st.session_state.canvas_text,
        placeholder=(
            "Write your quantum computing "
            "notes, equations or ideas..."
        ),
        height=230,
        key="canvas_editor",
    )

    canvas_col1, canvas_col2 = (
        st.columns(2)
    )


    with canvas_col1:

        if st.button(
            "💾 Save Canvas",
            use_container_width=True,
        ):

            st.session_state.canvas_text = (
                canvas_text
            )

            st.success(
                "Canvas saved for this session."
            )


    with canvas_col2:

        if st.button(
            "✖ Close Canvas",
            use_container_width=True,
        ):

            st.session_state.show_canvas = False

            st.rerun()


# =========================================================
# QUANTUM CALCULATOR
# =========================================================

if st.session_state.show_calculator:

    st.markdown("---")

    st.subheader(
        "🧮 Quantum Calculator"
    )

    calc_expression = st.text_input(
        "Expression",
        placeholder="Example: 2**3 + 5",
        key="calculator_expression",
    )

    if st.button(
        "Calculate",
        key="calculate_button",
    ):

        try:

            # Basic calculator only.
            # No builtins/functions are exposed.
            allowed = {
                "abs": abs,
                "round": round,
            }

            result = eval(
                calc_expression,
                {
                    "__builtins__": {}
                },
                allowed,
            )

            st.success(
                f"Result: {result}"
            )

        except Exception as error:

            st.error(
                f"Invalid expression: {error}"
            )


# =========================================================
# LEARNING MODE
# =========================================================

if st.session_state.learning_mode:

    st.markdown(
        """
        <div class="tool-card">

            <strong>
                📚 Learning Mode Active
            </strong>

            <br><br>

            <span style="
                color:#94a3b8;
            ">
                Ask a question and the tutor will
                explain the concept step-by-step.
            </span>

        </div>
        """,
        unsafe_allow_html=True,
    )


# =========================================================
# NOTES
# =========================================================

if st.session_state.show_notes:

    st.markdown("---")

    st.subheader(
        "📝 Quick Notes"
    )

    notes_text = st.text_area(
        "Notes",
        value=st.session_state.notes_text,
        placeholder="Write your notes here...",
        height=180,
        key="notes_editor",
    )

    if st.button(
        "💾 Save Notes",
        key="save_notes",
    ):

        st.session_state.notes_text = (
            notes_text
        )

        st.success(
            "Notes saved for this session."
        )


# =========================================================
# PROMPT AREA
# =========================================================

st.markdown(
    """
    <div class="prompt-shell">

        <div class="prompt-inner">
    """,
    unsafe_allow_html=True,
)


# =========================================================
# PROMPT COLUMNS
# =========================================================

prompt_col1, prompt_col2, prompt_col3, prompt_col4, prompt_col5 = (
    st.columns(
        [
            0.075,
            0.60,
            0.11,
            0.07,
            0.075,
        ],
        vertical_alignment="center",
    )
)


# =========================================================
# PLUS POPUP
# =========================================================

with prompt_col1:

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
        # PHOTOS & FILES
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

                key="quantum_attachments",
            )


            if uploaded:

                st.session_state.uploaded_files = (
                    uploaded
                )

                st.success(
                    f"{len(uploaded)} file(s) attached."
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

                    ☁️ <strong>
                        Google Drive
                    </strong>

                    <br>

                    <span style="
                        color:#94a3b8;
                    ">
                        Attach a Google Drive
                        file link.
                    </span>

                </div>
                """,
                unsafe_allow_html=True,
            )


            drive_url = st.text_input(
                "Drive file link",

                placeholder=
                    "Paste Google Drive link",

                key="drive_url",
            )


            if st.button(
                "Attach Drive File",
                use_container_width=True,
                key="attach_drive",
            ):

                clean_drive_url = (
                    drive_url.strip()
                )

                if clean_drive_url:

                    if (
                        clean_drive_url
                        not in
                        st.session_state.drive_links
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
                key="tool_canvas",
            ):

                st.session_state.show_canvas = True

                st.rerun()


            if st.button(
                "🧮 Quantum Calculator",
                use_container_width=True,
                key="tool_calculator",
            ):

                st.session_state.show_calculator = True

                st.rerun()


            if st.button(
                "📚 Learning Mode",
                use_container_width=True,
                key="tool_learning",
            ):

                st.session_state.learning_mode = (
                    not st.session_state.learning_mode
                )

                st.rerun()


            if st.button(
                "📝 Notes",
                use_container_width=True,
                key="tool_notes",
            ):

                st.session_state.show_notes = True

                st.rerun()


# =========================================================
# TEXT INPUT
# =========================================================

with prompt_col2:

    st.markdown(
        '<div class="prompt-input">',
        unsafe_allow_html=True,
    )

    prompt_key = (
        f"custom_prompt_"
        f"{st.session_state.prompt_nonce}"
    )

    user_prompt = st.text_input(
        "Message",

        placeholder="Ask anything",

        label_visibility="collapsed",

        key=prompt_key,
    )

    st.markdown(
        "</div>",
        unsafe_allow_html=True,
    )


# =========================================================
# THINK
# =========================================================

with prompt_col3:

    st.markdown(
        '<div class="think-area">',
        unsafe_allow_html=True,
    )

    think_clicked = st.button(
        "🧠 Think",
        key="think_button",
        help="Use deeper reasoning mode",
    )

    st.markdown(
        "</div>",
        unsafe_allow_html=True,
    )


# =========================================================
# MICROPHONE SYMBOL
# =========================================================

with prompt_col4:

    st.markdown(
        '<div class="mic-area">',
        unsafe_allow_html=True,
    )

    mic_clicked = st.button(
        "🎙",
        key="microphone_button",
        help="Voice input",
    )

    st.markdown(
        "</div>",
        unsafe_allow_html=True,
    )


# =========================================================
# SEND
# =========================================================

with prompt_col5:

    st.markdown(
        '<div class="send-area">',
        unsafe_allow_html=True,
    )

    send_clicked = st.button(
        "↑",
        key="send_button",
        help="Send message",
    )

    st.markdown(
        "</div>",
        unsafe_allow_html=True,
    )


# =========================================================
# CLOSE PROMPT HTML
# =========================================================

st.markdown(
    """
        </div>

    </div>

    <div class="prompt-hint">
        Quantum AI can make mistakes.
        Verify important information.
    </div>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# MICROPHONE
# =========================================================

voice_query = ""


if mic_clicked:

    st.markdown(
        """
        <div class="voice-box">

            <strong style="
                color:#e0e7ff;
            ">
                🎙 Voice Input
            </strong>

            <div style="
                color:#94a3b8;
                font-size:12px;
                margin-top:5px;
            ">
                Record your question and
                send it to the AI tutor.
            </div>

        </div>
        """,
        unsafe_allow_html=True,
    )


    audio_key = (
        "voice_recording_"
        f"{st.session_state.voice_recording_nonce}"
    )


    audio_value = st.audio_input(
        "Record",

        key=audio_key,

        label_visibility="collapsed",
    )


    if audio_value is not None:

        try:

            audio_bytes = (
                audio_value.getvalue()
            )

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
                        "SpeechRecognition is not installed. "
                        "Run: pip install SpeechRecognition"
                    )

                else:

                    recognizer = (
                        sr.Recognizer()
                    )


                    audio_stream = (
                        io.BytesIO(
                            audio_bytes
                        )
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
                            recognizer
                            .recognize_google(
                                recorded_audio
                            )
                        )

                        st.success(
                            f"Recognized: {voice_query}"
                        )

                    except sr.UnknownValueError:

                        st.warning(
                            "I couldn't understand "
                            "the recording."
                        )

                    except sr.RequestError as error:

                        st.warning(
                            "Speech recognition "
                            f"service unavailable: {error}"
                        )


        except Exception as error:

            st.warning(
                f"Voice processing failed: {error}"
            )


# =========================================================
# THINK MODE
# =========================================================

if think_clicked:

    st.toast(
        "🧠 Think mode enabled",
        icon="🧠",
    )


# =========================================================
# FINAL QUERY
# =========================================================

final_query = ""


if send_clicked:

    if user_prompt.strip():

        final_query = (
            user_prompt.strip()
        )

    elif voice_query.strip():

        final_query = (
            voice_query.strip()
        )

    else:

        st.warning(
            "Please enter a question "
            "or record your voice."
        )


# =========================================================
# EXECUTE QUERY
# =========================================================

if final_query:

    process_query(
        final_query
    )

    # =====================================================
    # IMPORTANT BUG FIX
    # =====================================================
    #
    # NEVER DO:
    #
    # st.session_state.custom_prompt = ""
    #
    # because the widget has already been instantiated.
    #
    # Instead we change the widget key.
    # =====================================================

    st.session_state.prompt_nonce += 1

    st.session_state.processed_audio_hash = None

    st.rerun()
