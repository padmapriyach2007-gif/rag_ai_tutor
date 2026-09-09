import streamlit as st
import io

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

# ---------------------------------------------------------
# FRONTEND-ONLY STATE
# ---------------------------------------------------------

if "uploaded_files" not in st.session_state:
    st.session_state.uploaded_files = []

if "processed_audio_hash" not in st.session_state:
    st.session_state.processed_audio_hash = None


# =========================================================
# COMPLETE FRONTEND
# =========================================================

st.markdown(
    """
<style>

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
   REALISTIC STAR FIELD
   NO TEXT / NO STAR CHARACTERS
   ========================================================= */

.quantum-space {
    position: fixed;
    inset: 0;

    pointer-events: none;

    overflow: hidden;

    z-index: 0;
}


/*
   Different star layers are created entirely
   with radial gradients.
*/

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
            circle at 18% 70%,
            rgba(255,255,255,.9) 0px,
            rgba(255,255,255,.35) 1px,
            transparent 2px
        ),

        radial-gradient(
            circle at 26% 18%,
            rgba(200,180,255,.9) 0px,
            rgba(200,180,255,.35) 1px,
            transparent 2px
        ),

        radial-gradient(
            circle at 34% 43%,
            rgba(255,255,255,.85) 0px,
            rgba(255,255,255,.35) 1px,
            transparent 2px
        ),

        radial-gradient(
            circle at 43% 9%,
            rgba(190,210,255,.9) 0px,
            rgba(190,210,255,.35) 1px,
            transparent 2px
        ),

        radial-gradient(
            circle at 50% 72%,
            rgba(255,255,255,.9) 0px,
            rgba(255,255,255,.3) 1px,
            transparent 2px
        ),

        radial-gradient(
            circle at 58% 27%,
            rgba(200,180,255,.95) 0px,
            rgba(200,180,255,.35) 1px,
            transparent 2px
        ),

        radial-gradient(
            circle at 66% 55%,
            rgba(255,255,255,.85) 0px,
            rgba(255,255,255,.3) 1px,
            transparent 2px
        ),

        radial-gradient(
            circle at 73% 14%,
            rgba(180,220,255,.95) 0px,
            rgba(180,220,255,.35) 1px,
            transparent 2px
        ),

        radial-gradient(
            circle at 81% 39%,
            rgba(255,255,255,.9) 0px,
            rgba(255,255,255,.3) 1px,
            transparent 2px
        ),

        radial-gradient(
            circle at 89% 74%,
            rgba(200,180,255,.9) 0px,
            rgba(200,180,255,.35) 1px,
            transparent 2px
        ),

        radial-gradient(
            circle at 95% 22%,
            rgba(255,255,255,.9) 0px,
            rgba(255,255,255,.3) 1px,
            transparent 2px
        ),

        radial-gradient(
            circle at 47% 53%,
            rgba(190,220,255,.85) 0px,
            rgba(190,220,255,.3) 1px,
            transparent 2px
        ),

        radial-gradient(
            circle at 7% 84%,
            rgba(255,255,255,.9) 0px,
            rgba(255,255,255,.3) 1px,
            transparent 2px
        );

    animation:
        starDrift 18s ease-in-out infinite alternate;
}


.quantum-space::after {

    content: "";

    position: absolute;
    inset: 0;

    background-image:

        radial-gradient(
            circle at 14% 24%,
            rgba(255,255,255,.7) 0px,
            transparent 1.8px
        ),

        radial-gradient(
            circle at 22% 55%,
            rgba(160,190,255,.8) 0px,
            transparent 1.5px
        ),

        radial-gradient(
            circle at 31% 78%,
            rgba(255,255,255,.7) 0px,
            transparent 1.5px
        ),

        radial-gradient(
            circle at 39% 29%,
            rgba(190,170,255,.8) 0px,
            transparent 1.5px
        ),

        radial-gradient(
            circle at 55% 17%,
            rgba(255,255,255,.8) 0px,
            transparent 1.5px
        ),

        radial-gradient(
            circle at 63% 82%,
            rgba(170,210,255,.7) 0px,
            transparent 1.5px
        ),

        radial-gradient(
            circle at 71% 48%,
            rgba(255,255,255,.7) 0px,
            transparent 1.5px
        ),

        radial-gradient(
            circle at 78% 68%,
            rgba(200,180,255,.7) 0px,
            transparent 1.5px
        ),

        radial-gradient(
            circle at 86% 30%,
            rgba(255,255,255,.75) 0px,
            transparent 1.5px
        );

    opacity: .65;

    animation:
        starTwinkle 4s ease-in-out infinite alternate;
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


@keyframes starTwinkle {

    0% {
        opacity: .30;
        filter: brightness(.7);
    }

    50% {
        opacity: .95;
        filter: brightness(1.4);
    }

    100% {
        opacity: .45;
        filter: brightness(.9);
    }
}


/* =========================================================
   MAIN CONTENT
   ========================================================= */

.main .block-container {

    max-width: 1250px;

    padding-top: 1rem;
    padding-bottom: 6rem;

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
        1px solid rgba(139,92,246,.18);
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

    transition: all .2s ease;
}


section[data-testid="stSidebar"] .stButton button:hover {

    border-color:
        rgba(167,139,250,.60);

    box-shadow:
        0 0 22px rgba(139,92,246,.16);

    transform:
        translateY(-1px);
}


/* =========================================================
   LOGO
   ========================================================= */

.quantum-logo {

    text-align: center;

    font-size: 70px;

    line-height: 1;

    margin:
        10px auto 5px auto;

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


/* =========================================================
   TITLE
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

    -webkit-background-clip:
        text;

    -webkit-text-fill-color:
        transparent;
}


.subtitle {

    text-align: center;

    max-width: 780px;

    margin: 10px auto 18px auto;

    color: #94a3b8;

    font-size: 14px;

    line-height: 1.8;
}


.online {

    width: fit-content;

    margin: 0 auto 18px auto;

    padding: 6px 14px;

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

    margin: 0 auto 18px auto;

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
# =========================================================
# QUANTUM CHAT INPUT BAR
# =========================================================

# Extra state for attachments
if "uploaded_files" not in st.session_state:
    st.session_state.uploaded_files = []


# =========================================================
# INPUT BAR LAYOUT
# =========================================================

input_left, input_center, input_right = st.columns(
    [0.09, 0.78, 0.13],
    vertical_alignment="bottom"
)


# =========================================================
# LEFT — ATTACHMENTS
# =========================================================

with input_left:

    st.markdown(
        """
        <style>

        /* =====================================================
           ATTACHMENT POPOVER BUTTON
           ===================================================== */

        div[data-testid="stPopover"] > button {
            width: 52px !important;
            height: 52px !important;
            border-radius: 50% !important;

            border: 1px solid rgba(120,180,255,0.45) !important;

            background:
                radial-gradient(
                    circle at 35% 30%,
                    rgba(130,220,255,0.30),
                    rgba(20,30,60,0.95)
                ) !important;

            box-shadow:
                0 0 12px rgba(70,170,255,0.35),
                inset 0 0 12px rgba(100,200,255,0.12) !important;

            font-size: 24px !important;

            transition:
                all 0.25s ease !important;
        }

        div[data-testid="stPopover"] > button:hover {
            transform:
                translateY(-2px) scale(1.05);

            box-shadow:
                0 0 20px rgba(80,190,255,0.65),
                0 0 40px rgba(80,120,255,0.25),
                inset 0 0 15px rgba(100,220,255,0.18) !important;
        }

        </style>
        """,
        unsafe_allow_html=True
    )

    with st.popover("＋"):

        st.markdown(
            """
            <div style="
                font-size:17px;
                font-weight:700;
                margin-bottom:10px;
            ">
                Add to your question
            </div>
            """,
            unsafe_allow_html=True
        )

        uploaded = st.file_uploader(
            "📎 Add photos & files",
            type=[
                "png",
                "jpg",
                "jpeg",
                "pdf",
                "txt",
                "docx",
                "csv"
            ],
            accept_multiple_files=True,
            key="quantum_attachments"
        )

        if uploaded:

            st.session_state.uploaded_files = uploaded

            st.success(
                f"{len(uploaded)} file(s) attached"
            )

            for file in uploaded:

                st.caption(
                    f"📄 {file.name}"
                )


# =========================================================
# CENTER — MAIN PROMPT BAR
# =========================================================

with input_center:

    query = st.chat_input(
        "Ask anything about quantum computing...",
        key="quantum_chat_input"
    )


# =========================================================
# RIGHT — CREATIVE MICROPHONE
# =========================================================

with input_right:

    st.markdown(
        """
        <style>

        /* =====================================================
           MICROPHONE
           ===================================================== */

        div[data-testid="stAudioInput"] {

            width: 62px !important;
            min-width: 62px !important;
            height: 52px !important;

            border-radius: 26px !important;

            background:
                radial-gradient(
                    circle at 30% 25%,
                    rgba(150,230,255,0.35),
                    rgba(20,25,55,0.98)
                ) !important;

            border:
                1px solid rgba(100,200,255,0.55) !important;

            box-shadow:
                0 0 12px rgba(70,190,255,0.45),
                0 0 28px rgba(90,100,255,0.18),
                inset 0 0 15px rgba(100,220,255,0.12) !important;

            transition:
                transform 0.25s ease,
                box-shadow 0.25s ease !important;

            overflow: hidden !important;
        }

        div[data-testid="stAudioInput"]:hover {

            transform:
                translateY(-2px) scale(1.04);

            box-shadow:
                0 0 18px rgba(70,210,255,0.75),
                0 0 35px rgba(90,110,255,0.35),
                inset 0 0 18px rgba(120,230,255,0.18) !important;
        }

        /* Hide unnecessary audio-input text */

        div[data-testid="stAudioInput"] label {
            display: none !important;
        }

        div[data-testid="stAudioInput"] button {

            border: none !important;

            background:
                transparent !important;

            box-shadow:
                none !important;
        }

        </style>
        """,
        unsafe_allow_html=True
    )

    audio_value = st.audio_input(
        "Microphone",
        key="quantum_microphone",
        label_visibility="collapsed"
    )


# =========================================================
# SEND BUTTON STYLING
# =========================================================

st.markdown(
    """
    <style>

    /* =====================================================
       CHAT INPUT / SEND BUTTON
       ===================================================== */

    [data-testid="stChatInput"] {

        border-radius: 18px !important;

        border:
            1px solid rgba(139,92,246,0.30) !important;

        background:
            linear-gradient(
                135deg,
                rgba(15,23,42,0.95),
                rgba(7,12,28,0.95)
            ) !important;

        box-shadow:
            0 0 25px rgba(99,102,241,0.12),
            inset 0 0 15px rgba(99,102,241,0.05) !important;
    }

    [data-testid="stChatInput"] button {

        border-radius: 11px !important;

        border:
            1px solid rgba(139,92,246,0.35) !important;

        background:
            linear-gradient(
                135deg,
                rgba(99,102,241,0.85),
                rgba(59,130,246,0.85)
            ) !important;

        transition:
            all 0.2s ease !important;
    }

    [data-testid="stChatInput"] button:hover {

        transform:
            translateY(-1px) scale(1.04);

        box-shadow:
            0 0 18px rgba(99,102,241,0.45) !important;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# =========================================================
# MICROPHONE → SPEECH TO TEXT
# =========================================================

voice_query = ""

if audio_value is not None:

    try:

        import speech_recognition as sr
        import io

        audio_bytes = audio_value.getvalue()

        # Prevent processing the same recording repeatedly
        audio_hash = hash(audio_bytes)

        if st.session_state.get(
            "last_audio_hash"
        ) != audio_hash:

            st.session_state.last_audio_hash = audio_hash

            recognizer = sr.Recognizer()

            audio_stream = io.BytesIO(
                audio_bytes
            )

            with sr.AudioFile(audio_stream) as source:

                recorded_audio = recognizer.record(
                    source
                )

            voice_query = recognizer.recognize_google(
                recorded_audio
            )

    except ImportError:

        st.warning(
            "Microphone transcription requires "
            "the SpeechRecognition package."
        )

    except sr.UnknownValueError:

        st.warning(
            "I couldn't understand the recording."
        )

    except Exception as e:

        st.warning(
            f"Microphone transcription failed: {str(e)}"
        )


# =========================================================
# FINAL QUERY
# =========================================================

final_query = ""

if query:

    final_query = query.strip()

elif voice_query:

    final_query = voice_query.strip()


# =========================================================
# EXISTING RAG FUNCTIONALITY — DO NOT CHANGE
# =========================================================

if final_query:

    # Show user message
    st.session_state.messages.append(
        {
            "role": "user",
            "content": final_query
        }
    )

    # Your EXISTING RAG call
    answer = answer_question(
        query=final_query,
        session_id=st.session_state.session_id,
        user_id=st.session_state.user_id,
    )

    # Save assistant response
    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": answer
        }
    )

    st.rerun()
