import io
import os
import streamlit as st
from groq import Groq


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="Quantum Lab",
    page_icon="⚛️",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================================
# SESSION STATE INITIALIZATION
# ============================================================

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "user_email" not in st.session_state:
    st.session_state.user_email = ""

if "chats" not in st.session_state:
    st.session_state.chats = {
        "Quantum Session 1": []
    }

if "current_chat" not in st.session_state:
    st.session_state.current_chat = "Quantum Session 1"

if "chat_counter" not in st.session_state:
    st.session_state.chat_counter = 1

if "staged_attachments" not in st.session_state:
    st.session_state.staged_attachments = []

if "staged_voice_text" not in st.session_state:
    st.session_state.staged_voice_text = ""


# ============================================================
# GALAXY THEME CSS
# ============================================================

st.markdown(
    """
<style>

@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;500;600;700;800;900&family=Inter:wght@400;500;600;700;800&display=swap');


/* ============================================================
   GLOBAL
   ============================================================ */

html, body {
    font-family: 'Inter', sans-serif;
}

.stApp {
    background:
        radial-gradient(
            circle at 15% 20%,
            rgba(108, 63, 255, 0.18),
            transparent 25%
        ),
        radial-gradient(
            circle at 85% 15%,
            rgba(0, 157, 255, 0.16),
            transparent 28%
        ),
        radial-gradient(
            circle at 50% 80%,
            rgba(168, 52, 255, 0.13),
            transparent 32%
        ),
        linear-gradient(
            135deg,
            #02030d,
            #070b20,
            #030716
        );

    color: #ffffff;
}


/* ============================================================
   MOVING STARS
   ============================================================ */

.stApp::before {
    content: "";
    position: fixed;
    inset: 0;
    pointer-events: none;

    background-image:
        radial-gradient(
            1px 1px at 10% 20%,
            rgba(255,255,255,0.8),
            transparent
        ),
        radial-gradient(
            1px 1px at 20% 80%,
            rgba(160,190,255,0.8),
            transparent
        ),
        radial-gradient(
            1px 1px at 35% 35%,
            rgba(255,255,255,0.7),
            transparent
        ),
        radial-gradient(
            1px 1px at 50% 15%,
            rgba(170,120,255,0.8),
            transparent
        ),
        radial-gradient(
            1px 1px at 65% 70%,
            rgba(255,255,255,0.7),
            transparent
        ),
        radial-gradient(
            1px 1px at 80% 40%,
            rgba(100,180,255,0.8),
            transparent
        ),
        radial-gradient(
            2px 2px at 90% 85%,
            rgba(255,255,255,0.9),
            transparent
        );

    background-size: 250px 250px;

    opacity: 0.7;

    animation: starsMove 25s linear infinite;
}


@keyframes starsMove {

    0% {
        transform: translateY(0px);
    }

    50% {
        transform: translateY(-15px);
    }

    100% {
        transform: translateY(0px);
    }
}


/* ============================================================
   SIDEBAR
   ============================================================ */

[data-testid="stSidebar"] {

    background:
        radial-gradient(
            circle at 30% 5%,
            rgba(105, 65, 255, 0.18),
            transparent 30%
        ),
        radial-gradient(
            circle at 80% 75%,
            rgba(0, 150, 255, 0.10),
            transparent 35%
        ),
        linear-gradient(
            180deg,
            #03040e,
            #070a1c,
            #02030b
        ) !important;

    border-right:
        1px solid rgba(120, 105, 255, 0.25);
}


/* ============================================================
   USER PROFILE
   ============================================================ */

.user-profile-card {

    background:
        linear-gradient(
            135deg,
            rgba(28, 32, 68, 0.75),
            rgba(12, 16, 42, 0.85)
        );

    border:
        1px solid rgba(130, 115, 255, 0.35);

    border-radius: 16px;

    padding: 14px;

    margin-bottom: 18px;

    display: flex;

    align-items: center;

    gap: 12px;
}


.profile-avatar {

    width: 44px;

    height: 44px;

    border-radius: 12px;

    background:
        linear-gradient(
            135deg,
            #7c4dff,
            #1e88e5
        );

    display: flex;

    align-items: center;

    justify-content: center;

    font-size: 22px;

    border:
        1px solid rgba(255, 255, 255, 0.25);

    box-shadow:
        0 0 15px rgba(124, 77, 255, 0.45);
}


.profile-info {
    overflow: hidden;
}


.profile-name {

    font-family: 'Orbitron', sans-serif;

    font-size: 13px;

    font-weight: 700;

    color: #ffffff;

    letter-spacing: 0.5px;
}


.profile-status {

    font-size: 11px;

    color: #4cf0a0;

    letter-spacing: 0.5px;
}


/* ============================================================
   SIDEBAR BUTTONS
   ============================================================ */

[data-testid="stSidebar"] .stButton > button {

    width: 100%;

    min-height: 40px;

    border-radius: 12px;

    background:
        linear-gradient(
            135deg,
            rgba(18,21,48,0.90),
            rgba(8,11,30,0.95)
        );

    border:
        1px solid rgba(105,105,180,0.28);

    color: #bfc6e5;

    font-size: 12px;

    font-weight: 600;

    transition: all 0.25s ease;
}


[data-testid="stSidebar"] .stButton > button:hover {

    transform: translateX(4px);

    background:
        linear-gradient(
            100deg,
            rgba(77,55,180,0.85),
            rgba(27,82,160,0.85)
        );

    border-color:
        rgba(130,115,255,0.8);

    color: #ffffff;

    box-shadow:
        0 4px 18px rgba(70,60,200,0.3);
}


/* ============================================================
   POPOVER
   ============================================================ */

[data-testid="stPopoverBody"] {

    background:
        #080c24 !important;

    border:
        1px solid rgba(120, 105, 255, 0.45) !important;

    border-radius:
        16px !important;

    color:
        #ffffff !important;

    box-shadow:
        0 10px 40px rgba(0,0,0,0.75) !important;
}


.stPopover button {

    border-radius:
        12px !important;

    background:
        rgba(30, 35, 70, 0.65) !important;

    border:
        1px solid rgba(120, 105, 255, 0.30) !important;

    color:
        #bfc6e5 !important;

    min-height:
        42px !important;
}


.stPopover button:hover {

    background:
        rgba(120, 105, 255, 0.35) !important;

    border-color:
        rgba(140, 125, 255, 0.8) !important;

    color:
        #ffffff !important;
}


/* ============================================================
   CUSTOM FIXED BOTTOM COMPOSER
   ============================================================ */

.custom-composer {

    position: fixed;

    left: 320px;

    right: 35px;

    bottom: 22px;

    z-index: 999999;

    background:
        rgba(10, 14, 35, 0.96);

    border:
        1px solid rgba(120, 105, 255, 0.42);

    border-radius: 24px;

    padding: 7px 9px;

    box-shadow:
        0 10px 40px rgba(0,0,0,0.55),
        0 0 25px rgba(80,70,200,0.12);

    backdrop-filter:
        blur(18px);
}


/* ============================================================
   CHAT INPUT
   ============================================================ */

[data-testid="stChatInput"] {

    position: static !important;

    width: 100% !important;

    max-width: none !important;

    padding: 0 !important;

    margin: 0 !important;
}


[data-testid="stChatInput"] > div {

    background:
        transparent !important;

    border:
        none !important;

    box-shadow:
        none !important;

    padding:
        0 !important;
}


[data-testid="stChatInput"] textarea {

    background:
        transparent !important;

    border:
        none !important;

    box-shadow:
        none !important;

    color:
        #ffffff !important;

    font-size:
        15px !important;

    padding:
        10px 12px !important;
}


[data-testid="stChatInput"] textarea::placeholder {

    color:
        #7f89aa !important;
}


[data-testid="stChatInput"] textarea:focus {

    border:
        none !important;

    outline:
        none !important;

    box-shadow:
        none !important;
}


/* ============================================================
   HIDE NATIVE STREAMLIT ATTACHMENT / VOICE BUTTONS
   ============================================================ */

[data-testid="stChatInput"] button[aria-label*="Attach"],
[data-testid="stChatInput"] button[aria-label*="attach"],
[data-testid="stChatInput"] button[title*="Attach"],
[data-testid="stChatInput"] button[title*="attach"] {

    display: none !important;
}


[data-testid="stChatInput"] button[aria-label*="Voice"],
[data-testid="stChatInput"] button[aria-label*="voice"],
[data-testid="stChatInput"] button[title*="Voice"],
[data-testid="stChatInput"] button[title*="voice"] {

    display: none !important;
}


/* ============================================================
   CUSTOM PLUS / MICROPHONE BUTTONS
   ============================================================ */

.composer-btn button {

    min-width:
        42px !important;

    width:
        42px !important;

    height:
        42px !important;

    border-radius:
        50% !important;

    background:
        rgba(30, 35, 70, 0.75) !important;

    border:
        1px solid rgba(120, 105, 255, 0.30) !important;

    color:
        #cbd2ef !important;

    font-size:
        19px !important;

    padding:
        0 !important;
}


.composer-btn button:hover {

    background:
        rgba(110, 90, 220, 0.40) !important;

    border-color:
        rgba(160, 145, 255, 0.75) !important;

    color:
        #ffffff !important;
}


/* ============================================================
   CHAT AREA SPACE
   ============================================================ */

.main .block-container {

    padding-bottom:
        120px !important;
}


/* ============================================================
   LOGIN SCREEN
   ============================================================ */

.login-container {

    width:
        min(460px, 90vw);

    margin:
        10vh auto 22px auto;

    padding:
        38px 40px;

    text-align:
        center;

    border-radius:
        25px;

    background:
        linear-gradient(
            145deg,
            rgba(22,26,60,0.96),
            rgba(6,9,26,0.98)
        );

    border:
        1px solid rgba(120,105,255,0.50);

    box-shadow:
        0 25px 80px rgba(0,0,0,0.50);
}


.login-title {

    font-family:
        'Orbitron',
        sans-serif;

    font-size:
        28px;

    font-weight:
        900;

    background:
        linear-gradient(
            90deg,
            #ffffff,
            #b59cff,
            #67bfff
        );

    -webkit-background-clip:
        text;

    -webkit-text-fill-color:
        transparent;
}


/* ============================================================
   RESPONSIVE
   ============================================================ */

@media (max-width: 900px) {

    .custom-composer {

        left: 15px;

        right: 15px;

        bottom: 15px;
    }
}

</style>
""",
    unsafe_allow_html=True
)


# ============================================================
# BACKEND API UTILS
# ============================================================

def get_groq_client():

    api_key = os.environ.get("GROQ_API_KEY")

    if not api_key:
        return None

    return Groq(api_key=api_key)


def ai_response(chat_history):

    client = get_groq_client()

    if not client:

        return (
            "⚠️ **Groq API key missing.** "
            "Please set your `GROQ_API_KEY` in your environment."
        )


    system_message = {

        "role": "system",

        "content": (

            "You are Quantum Lab AI, an intelligent, helpful, "
            "and adaptive assistant. "

            "You answer questions clearly across technical, "
            "scientific, and everyday domains. "

            "When analyzing attached files or transcripts, "
            "integrate your reasoning seamlessly."

        )
    }


    full_messages = [
        system_message
    ] + chat_history


    try:

        response = client.chat.completions.create(

            model="llama-3.3-70b-versatile",

            messages=full_messages
        )

        return response.choices[0].message.content


    except Exception as e:

        return f"⚠️ **Inference error:** `{str(e)}`"


def transcribe_audio(audio_data):

    client = get_groq_client()

    if not client:
        return ""


    try:

        if isinstance(audio_data, bytes):

            audio_file = io.BytesIO(audio_data)

        else:

            audio_file = audio_data


        audio_file.name = "audio.wav"


        transcription = client.audio.transcriptions.create(

            file=audio_file,

            model="whisper-large-v3"
        )


        return transcription.text


    except Exception as e:

        st.error(
            f"Voice transcription failed: {e}"
        )

        return ""


# ============================================================
# LOGIN FLOW
# ============================================================

if not st.session_state.logged_in:

    st.markdown(
        """
        <div class="login-container">

            <div style="
                font-size: 44px;
                margin-bottom: 10px;
            ">
                ⚛️
            </div>

            <div class="login-title">
                QUANTUM LAB
            </div>

            <p style="
                color: #8c98ba;
                font-size: 13px;
                margin-top: 6px;
            ">
                Sign in to your Quantum Workspace
            </p>

        </div>
        """,
        unsafe_allow_html=True
    )


    _, col2, _ = st.columns(
        [1, 1.2, 1]
    )


    with col2:

        email = st.text_input(
            "Email",
            placeholder="researcher@quantum.lab"
        )


        password = st.text_input(
            "Password",
            type="password",
            placeholder="••••••••"
        )


        if st.button(
            "Initialize Terminal",
            use_container_width=True
        ):

            if email:

                st.session_state.logged_in = True

                st.session_state.user_email = email

                st.rerun()

            else:

                st.warning(
                    "Please provide a valid email."
                )


    st.stop()


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    username = (
        st.session_state.user_email
        .split("@")[0]
        .capitalize()
    )


    st.markdown(
        f"""
        <div class="user-profile-card">

            <div class="profile-avatar">
                👨‍🚀
            </div>

            <div class="profile-info">

                <div class="profile-name">
                    {username}
                </div>

                <div class="profile-status">
                    ● Quantum Node Online
                </div>

            </div>

        </div>
        """,
        unsafe_allow_html=True
    )


    # --------------------------------------------------------
    # NEW CHAT
    # --------------------------------------------------------

    if st.button(
        "➕ New Chat",
        use_container_width=True
    ):

        st.session_state.chat_counter += 1

        new_session = (
            f"Quantum Session "
            f"{st.session_state.chat_counter}"
        )

        st.session_state.chats[new_session] = []

        st.session_state.current_chat = new_session

        st.rerun()


    st.markdown(
        """
        <div style="
            margin: 10px 0;
            height: 1px;
            background: rgba(255,255,255,0.08);
        ">
        </div>
        """,
        unsafe_allow_html=True
    )


    st.caption(
        "**CHAT SESSIONS**"
    )


    # --------------------------------------------------------
    # CHAT SESSIONS
    # --------------------------------------------------------

    for chat_name in list(
        st.session_state.chats.keys()
    ):

        is_active = (
            chat_name ==
            st.session_state.current_chat
        )


        label = (
            f"👉 {chat_name}"
            if is_active
            else
            f"💬 {chat_name}"
        )


        if st.button(
            label,
            key=f"session_btn_{chat_name}",
            use_container_width=True
        ):

            st.session_state.current_chat = chat_name

            st.rerun()


    st.markdown(
        """
        <div style="
            margin: 14px 0;
            height: 1px;
            background: rgba(255,255,255,0.08);
        ">
        </div>
        """,
        unsafe_allow_html=True
    )


    st.caption(
        "**SESSION TOOLS**"
    )


    # --------------------------------------------------------
    # SESSION MANAGEMENT
    # --------------------------------------------------------

    with st.expander(
        "⚙️ Manage Session"
    ):

        rename_input = st.text_input(
            "Rename Title",
            value=st.session_state.current_chat
        )


        if st.button(
            "Confirm Rename"
        ):

            if (
                rename_input
                and
                rename_input
                !=
                st.session_state.current_chat
            ):

                st.session_state.chats[
                    rename_input
                ] = st.session_state.chats.pop(
                    st.session_state.current_chat
                )

                st.session_state.current_chat = (
                    rename_input
                )

                st.rerun()


        if st.button(
            "🗑️ Delete Current Chat"
        ):

            if len(
                st.session_state.chats
            ) > 1:

                del st.session_state.chats[
                    st.session_state.current_chat
                ]

                st.session_state.current_chat = (
                    list(
                        st.session_state.chats.keys()
                    )[0]
                )

                st.rerun()

            else:

                st.warning(
                    "Cannot delete the only remaining session."
                )


        if st.button(
            "🧹 Clear Messages"
        ):

            st.session_state.chats[
                st.session_state.current_chat
            ] = []

            st.rerun()


    # --------------------------------------------------------
    # LOGOUT
    # --------------------------------------------------------

    if st.button(
        "🚪 Logout",
        use_container_width=True
    ):

        st.session_state.logged_in = False

        st.session_state.user_email = ""

        st.rerun()


# ============================================================
# CHAT CONVERSATION VIEW
# ============================================================

current_messages = (
    st.session_state.chats[
        st.session_state.current_chat
    ]
)


for message in current_messages:

    role = message["role"]

    avatar = (
        "👨‍🚀"
        if role == "user"
        else
        "⚛️"
    )


    with st.chat_message(
        role,
        avatar=avatar
    ):

        st.markdown(
            message["content"]
        )


# ============================================================
# STAGED ATTACHMENT / VOICE STATUS
# ============================================================

staged_info = []


if st.session_state.staged_attachments:

    staged_info.append(
        f"📎 "
        f"{len(st.session_state.staged_attachments)} "
        f"item(s) attached"
    )


if st.session_state.staged_voice_text:

    staged_info.append(
        f"🎙️ Voice text staged: "
        f"\"{st.session_state.staged_voice_text[:30]}...\""
    )


if staged_info:

    st.info(
        " | ".join(staged_info)
    )


# ============================================================
# CUSTOM FIXED BOTTOM CHAT COMPOSER
# ============================================================

st.markdown(
    '<div class="custom-composer">',
    unsafe_allow_html=True
)


composer_left, composer_input, composer_right = st.columns(
    [0.07, 0.86, 0.07],
    vertical_alignment="center"
)


# ============================================================
# PLUS BUTTON
# ============================================================

with composer_left:

    st.markdown(
        '<div class="composer-btn">',
        unsafe_allow_html=True
    )


    with st.popover(
        "＋",
        help="Add photos, camera, or files"
    ):

        st.markdown(
            "### Attach"
        )


        tab_photos, tab_camera, tab_files = st.tabs(
            [
                "🖼️ Photos",
                "📷 Camera",
                "📎 Files"
            ]
        )


        # ====================================================
        # PHOTOS
        # ====================================================

        with tab_photos:

            photos = st.file_uploader(

                "Upload photos",

                type=[
                    "png",
                    "jpg",
                    "jpeg",
                    "webp"
                ],

                accept_multiple_files=True,

                key="custom_input_photos"
            )


            if photos:

                for photo in photos:

                    note = (
                        f"🖼️ Photo: "
                        f"`{photo.name}` "
                        f"({round(photo.size / 1024, 1)} KB)"
                    )


                    if (
                        note
                        not in
                        st.session_state.staged_attachments
                    ):

                        st.session_state.staged_attachments.append(
                            note
                        )


                st.success(
                    f"{len(photos)} photo(s) attached."
                )


        # ====================================================
        # CAMERA
        # ====================================================

        with tab_camera:

            camera_photo = st.camera_input(

                "Take a snapshot",

                key="custom_input_camera"
            )


            if camera_photo:

                note = (
                    "📷 *Camera Snapshot*"
                )


                if (
                    note
                    not in
                    st.session_state.staged_attachments
                ):

                    st.session_state.staged_attachments.append(
                        note
                    )


                st.success(
                    "Snapshot attached."
                )


        # ====================================================
        # FILES
        # ====================================================

        with tab_files:

            files = st.file_uploader(

                "Upload documents/code",

                type=[
                    "pdf",
                    "txt",
                    "docx",
                    "csv",
                    "xlsx",
                    "py",
                    "json"
                ],

                accept_multiple_files=True,

                key="custom_input_files"
            )


            if files:

                for file in files:

                    note = (
                        f"📎 Document: "
                        f"`{file.name}` "
                        f"({round(file.size / 1024, 1)} KB)"
                    )


                    if (
                        note
                        not in
                        st.session_state.staged_attachments
                    ):

                        st.session_state.staged_attachments.append(
                            note
                        )


                st.success(
                    f"{len(files)} file(s) attached."
                )


    st.markdown(
        '</div>',
        unsafe_allow_html=True
    )


# ============================================================
# MAIN CHAT INPUT
# ============================================================

with composer_input:

    prompt = st.chat_input(
        "Ask anything...",
        key="main_chat_input"
    )


# ============================================================
# VOICE BUTTON
# ============================================================

with composer_right:

    st.markdown(
        '<div class="composer-btn">',
        unsafe_allow_html=True
    )


    with st.popover(
        "🎤",
        help="Voice recording"
    ):

        st.markdown(
            "### Voice Input"
        )


        audio_stream = st.audio_input(

            "Record audio note",

            key="custom_input_voice"
        )


        if audio_stream:

            with st.spinner(
                "Transcribing voice..."
            ):

                transcription = transcribe_audio(
                    audio_stream.read()
                )


            if transcription:

                st.session_state.staged_voice_text = (
                    transcription
                )


                st.success(
                    "Voice transcribed! "
                    "Text staged for prompt."
                )


    st.markdown(
        '</div>',
        unsafe_allow_html=True
    )


st.markdown(
    '</div>',
    unsafe_allow_html=True
)


# ============================================================
# PROCESS USER INPUT & GENERATE RESPONSE
# ============================================================

if prompt:

    user_text = prompt.strip()


    # --------------------------------------------------------
    # COMBINE USER INPUT
    # --------------------------------------------------------

    combined_parts = []


    if user_text:

        combined_parts.append(
            user_text
        )


    if st.session_state.staged_voice_text:

        combined_parts.append(
            f"🎙️ Transcribed Voice Note: "
            f"\"{st.session_state.staged_voice_text}\""
        )


    if st.session_state.staged_attachments:

        combined_parts.append(
            "\n".join(
                st.session_state.staged_attachments
            )
        )


    full_query = (
        "\n\n".join(
            combined_parts
        )
    )


    # --------------------------------------------------------
    # CLEAR STAGED DATA
    # --------------------------------------------------------

    st.session_state.staged_attachments = []

    st.session_state.staged_voice_text = ""


    # --------------------------------------------------------
    # SAVE USER MESSAGE
    # --------------------------------------------------------

    current_messages.append(
        {
            "role": "user",
            "content": full_query
        }
    )


    # --------------------------------------------------------
    # GENERATE AI RESPONSE
    # --------------------------------------------------------

    response_text = ai_response(
        current_messages
    )


    current_messages.append(
        {
            "role": "assistant",
            "content": response_text
        }
    )


    # --------------------------------------------------------
    # REFRESH
    # --------------------------------------------------------

    st.rerun()
