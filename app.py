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

if "rename_chat" not in st.session_state:
    st.session_state.rename_chat = None

if "clear_chat" not in st.session_state:
    st.session_state.clear_chat = None

if "delete_chat" not in st.session_state:
    st.session_state.delete_chat = None

if "staged_attachments" not in st.session_state:
    st.session_state.staged_attachments = []

if "staged_voice_text" not in st.session_state:
    st.session_state.staged_voice_text = ""

if "learning_mode" not in st.session_state:
    st.session_state.learning_mode = False

if "learning_topic" not in st.session_state:
    st.session_state.learning_topic = "Quantum Computing Basics"

if "learning_progress" not in st.session_state:
    st.session_state.learning_progress = {}


# ============================================================
# GALAXY THEME & FIXED BOTTOM BAR CSS
# ============================================================

st.markdown(
    """
<style>

@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;500;600;700;800;900&family=Inter:wght@400;500;600;700;800&display=swap');


/* ============================================================
   GENERAL
   ============================================================ */

html, body {
    font-family: 'Inter', sans-serif;
}

.stApp {
    background:
        radial-gradient(circle at 15% 20%, rgba(108, 63, 255, 0.18), transparent 25%),
        radial-gradient(circle at 85% 15%, rgba(0, 157, 255, 0.16), transparent 28%),
        radial-gradient(circle at 50% 80%, rgba(168, 52, 255, 0.13), transparent 32%),
        linear-gradient(135deg, #02030d, #070b20, #030716);
    color: #ffffff;
}


/* ============================================================
   BOTTOM PADDING
   ============================================================ */

.main .block-container {
    padding-bottom: 160px !important;
}


/* ============================================================
   SIDEBAR
   ============================================================ */

[data-testid="stSidebar"] {
    background:
        radial-gradient(circle at 30% 5%, rgba(105, 65, 255, 0.18), transparent 30%),
        linear-gradient(180deg, #03040e, #070a1c, #02030b) !important;

    border-right: 1px solid rgba(120, 105, 255, 0.25);
}


/* ============================================================
   QUANTUM AI TUTOR - CENTER HEADER
   ============================================================ */

.quantum-tutor-header {
    width: 100%;
    text-align: center;

    margin-top: 65px;
    margin-bottom: 45px;

    padding: 10px 20px;
}


/* Main Title */

.quantum-tutor-title {
    font-family: 'Orbitron', sans-serif;

    font-size: 42px;
    font-weight: 900;

    letter-spacing: 3px;

    background: linear-gradient(
        90deg,
        #ffffff,
        #b59cff,
        #67bfff,
        #ffffff
    );

    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;

    text-shadow:
        0 0 20px rgba(103, 191, 255, 0.25),
        0 0 45px rgba(120, 105, 255, 0.18);
}


/* Subtitle */

.quantum-tutor-subtitle {
    margin-top: 12px;

    font-size: 14px;

    color: #8c98ba;

    letter-spacing: 1px;
}


/* Online Status */

.quantum-tutor-status {
    margin-top: 14px;

    font-size: 12px;

    color: #4cf0a0;

    letter-spacing: 1px;

    font-weight: 600;
}


/* ============================================================
   LEARNING MODE
   ============================================================ */

.learning-panel {
    background:
        linear-gradient(
            135deg,
            rgba(24, 30, 75, 0.88),
            rgba(8, 12, 35, 0.92)
        );

    border:
        1px solid rgba(120, 105, 255, 0.35);

    border-radius: 18px;

    padding: 20px;

    margin-bottom: 20px;

    box-shadow:
        0 15px 45px rgba(0, 0, 0, 0.35);
}


.learning-title {
    font-family: 'Orbitron', sans-serif;

    font-size: 18px;

    font-weight: 800;

    background:
        linear-gradient(
            90deg,
            #ffffff,
            #b59cff,
            #67bfff
        );

    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}


.learning-subtitle {
    color: #8c98ba;

    font-size: 13px;

    margin-top: 7px;
}


.learning-card {
    background: rgba(12, 16, 42, 0.72);

    border:
        1px solid rgba(120, 105, 255, 0.25);

    border-radius: 16px;

    padding: 18px;

    margin: 12px 0;
}


.learning-card h3 {
    margin-top: 0;

    color: #ffffff;
}


.learning-card p {
    color: #c5cbea;

    line-height: 1.65;
}


/* ============================================================
   LOGIN BOX
   ============================================================ */

.login-container {
    width: min(460px, 90vw);

    margin: 10vh auto 22px auto;

    padding: 38px 40px;

    text-align: center;

    border-radius: 25px;

    background:
        linear-gradient(
            145deg,
            rgba(22, 26, 60, 0.96),
            rgba(6, 9, 26, 0.98)
        );

    border:
        1px solid rgba(120, 105, 255, 0.50);

    box-shadow:
        0 25px 80px rgba(0, 0, 0, 0.50);
}


.login-title {
    font-family: 'Orbitron', sans-serif;

    font-size: 28px;

    font-weight: 900;

    background:
        linear-gradient(
            90deg,
            #ffffff,
            #b59cff,
            #67bfff
        );

    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}


/* ============================================================
   CHAT MESSAGE AREA
   ============================================================ */

[data-testid="stChatMessage"] {
    border-radius: 14px;
}


/* ============================================================
   CHAT INPUT
   ============================================================ */

[data-testid="stChatInput"] {
    border-radius: 25px;
}


/* ============================================================
   BUTTONS
   ============================================================ */

.stButton > button {
    border-radius: 10px;

    border: 1px solid rgba(120, 105, 255, 0.35);

    background:
        rgba(20, 25, 55, 0.85);

    color: white;

    transition: all 0.2s ease;
}


.stButton > button:hover {
    border-color: rgba(103, 191, 255, 0.75);

    box-shadow:
        0 0 20px rgba(103, 191, 255, 0.20);
}


/* ============================================================
   COMPOSER
   ============================================================ */

.composer-anchor {
    height: 1px;
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

    if st.session_state.get("learning_mode", False):

        system_content = (
            "You are Quantum Lab AI Tutor in Learning Mode. "
            "Teach quantum computing step by step using clear, "
            "beginner-friendly explanations. Define technical terms, "
            "use intuitive examples, show equations when useful, "
            "and ask short practice questions when appropriate. "
            "Focus on the user's selected topic: "
            f"{st.session_state.get('learning_topic', 'Quantum Computing Basics')}."
        )

    else:

        system_content = (
            "You are Quantum Lab AI, an intelligent assistant."
        )

    system_message = {
        "role": "system",
        "content": system_content
    }

    full_messages = [system_message] + chat_history

    try:

        response = client.chat.completions.create(
            model="openai/gpt-oss-120b",
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

        audio_file = (
            io.BytesIO(audio_data)
            if isinstance(audio_data, bytes)
            else audio_data
        )

        audio_file.name = "audio.wav"

        transcription = client.audio.transcriptions.create(
            file=audio_file,
            model="whisper-large-v3"
        )

        return transcription.text

    except Exception:
        return ""


# ============================================================
# LOGIN FLOW
# ============================================================

if not st.session_state.logged_in:

    st.markdown(
        """
        <div class="login-container">

            <div style="font-size: 44px; margin-bottom: 10px;">
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

    _, col2, _ = st.columns([1, 1.2, 1])

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
        <div style="
            text-align:center;
            padding:15px 5px 20px 5px;
        ">

            <div style="
                font-size:40px;
            ">
                ⚛️
            </div>

            <div style="
                font-family:Orbitron;
                font-size:18px;
                font-weight:800;
            ">
                QUANTUM LAB
            </div>

            <div style="
                color:#8c98ba;
                font-size:12px;
                margin-top:5px;
            ">
                Welcome, {username}
            </div>

        </div>
        """,
        unsafe_allow_html=True
    )


    # ========================================================
    # NEW CHAT
    # ========================================================

    if st.button(
        "＋ New Chat",
        use_container_width=True
    ):

        st.session_state.chat_counter += 1

        new_chat = (
            f"Quantum Session "
            f"{st.session_state.chat_counter}"
        )

        st.session_state.chats[new_chat] = []

        st.session_state.current_chat = new_chat

        st.rerun()


    st.markdown("### 💬 Chats")


    # ========================================================
    # CHAT LIST
    # ========================================================

    for chat_name in list(
        st.session_state.chats.keys()
    ):

        col1, col2 = st.columns([0.85, 0.15])

        with col1:

            if st.button(
                chat_name,
                key=f"chat_{chat_name}",
                use_container_width=True
            ):

                st.session_state.current_chat = chat_name

                st.rerun()


        with col2:

            with st.popover(
                "⋮",
                help="Chat options"
            ):

                if st.button(
                    "✏️ Rename",
                    key=f"rename_{chat_name}",
                    use_container_width=True
                ):

                    st.session_state.rename_chat = chat_name


                if st.button(
                    "🗑️ Delete",
                    key=f"delete_{chat_name}",
                    use_container_width=True
                ):

                    st.session_state.delete_chat = chat_name


                if st.button(
                    "🧹 Clear",
                    key=f"clear_{chat_name}",
                    use_container_width=True
                ):

                    st.session_state.clear_chat = chat_name


    # ========================================================
    # RENAME CHAT
    # ========================================================

    if st.session_state.rename_chat:

        old_name = st.session_state.rename_chat

        st.markdown("### ✏️ Rename Chat")

        new_name = st.text_input(
            "New chat name",
            value=old_name,
            key="rename_input"
        )

        col1, col2 = st.columns(2)

        with col1:

            if st.button(
                "Save",
                key="save_rename",
                use_container_width=True
            ):

                if new_name.strip():

                    new_name = new_name.strip()

                    if new_name != old_name:

                        st.session_state.chats[
                            new_name
                        ] = st.session_state.chats.pop(
                            old_name
                        )

                        if (
                            st.session_state.current_chat
                            == old_name
                        ):

                            st.session_state.current_chat = new_name

                    st.session_state.rename_chat = None

                    st.rerun()

        with col2:

            if st.button(
                "Cancel",
                key="cancel_rename",
                use_container_width=True
            ):

                st.session_state.rename_chat = None

                st.rerun()


    # ========================================================
    # DELETE CHAT
    # ========================================================

    if st.session_state.delete_chat:

        chat_to_delete = (
            st.session_state.delete_chat
        )

        if len(st.session_state.chats) > 1:

            del st.session_state.chats[
                chat_to_delete
            ]

            if (
                st.session_state.current_chat
                == chat_to_delete
            ):

                st.session_state.current_chat = (
                    list(
                        st.session_state.chats.keys()
                    )[0]
                )

            st.session_state.delete_chat = None

            st.rerun()

        else:

            st.warning(
                "You must keep at least one chat."
            )

            if st.button(
                "Cancel Delete",
                key="cancel_delete"
            ):

                st.session_state.delete_chat = None

                st.rerun()


    # ========================================================
    # CLEAR CHAT
    # ========================================================

    if st.session_state.clear_chat:

        chat_to_clear = (
            st.session_state.clear_chat
        )

        st.session_state.chats[
            chat_to_clear
        ] = []

        st.session_state.clear_chat = None

        st.rerun()


    # ========================================================
    # LEARNING MODE TOGGLE
    # ========================================================

    st.markdown("---")

    learning_toggle = st.toggle(
        "🧠 Quantum Learning Mode",
        value=st.session_state.learning_mode
    )

    if learning_toggle != st.session_state.learning_mode:

        st.session_state.learning_mode = learning_toggle

        st.rerun()


    # ========================================================
    # LEARNING TOPICS
    # ========================================================

    learning_topics = [
        "Quantum Computing Basics",
        "Qubits & Superposition",
        "Entanglement",
        "Quantum Gates",
        "Quantum Circuits",
        "Measurement",
        "Grover's Algorithm",
        "Shor's Algorithm"
    ]


    if st.session_state.learning_mode:

        lessons = {

            "Quantum Computing Basics": {
                "intro":
                    "Quantum computing uses quantum-mechanical "
                    "effects to process information. Instead of "
                    "classical bits, quantum computers use qubits.",

                "points": [
                    "A classical bit is either 0 or 1.",
                    "A qubit can be in a superposition of |0⟩ and |1⟩.",
                    "Quantum algorithms use interference and entanglement.",
                    "Measurement produces a classical result."
                ],

                "example":
                    "A classical bit is like a switch that is OFF "
                    "or ON. A qubit is described using amplitudes "
                    "for |0⟩ and |1⟩."
            },

            "Qubits & Superposition": {
                "intro":
                    "A qubit is the basic unit of quantum information. "
                    "Superposition allows a qubit to be represented "
                    "as a combination of |0⟩ and |1⟩.",

                "points": [
                    "A qubit can be written as α|0⟩ + β|1⟩.",
                    "The measurement probabilities are |α|² and |β|².",
                    "The probabilities satisfy |α|² + |β|² = 1.",
                    "Measurement gives a classical value."
                ],

                "example":
                    "For (|0⟩ + |1⟩)/√2, an ideal "
                    "computational-basis measurement gives "
                    "0 or 1 with equal probability."
            },

            "Entanglement": {
                "intro":
                    "Entanglement is a quantum correlation where "
                    "the joint state of multiple qubits cannot be "
                    "described as independent states of each qubit.",

                "points": [
                    "Entangled qubits share a joint quantum state.",
                    "Measurements can reveal strong correlations.",
                    "Entanglement is useful in quantum communication and computing.",
                    "Entanglement does not enable faster-than-light communication."
                ],

                "example":
                    "The Bell state "
                    "(|00⟩ + |11⟩)/√2 produces correlated "
                    "measurement outcomes."
            },

            "Quantum Gates": {
                "intro":
                    "Quantum gates are operations that change "
                    "quantum states.",

                "points": [
                    "X is similar to a NOT operation on computational-basis states.",
                    "H (Hadamard) creates equal superposition from |0⟩.",
                    "Z changes the phase of the |1⟩ component.",
                    "CNOT is a two-qubit controlled operation."
                ],

                "example":
                    "Starting with |0⟩ and applying H produces "
                    "(|0⟩ + |1⟩)/√2."
            },

            "Quantum Circuits": {
                "intro":
                    "A quantum circuit is a sequence of quantum "
                    "gates applied to qubits, usually followed "
                    "by measurement.",

                "points": [
                    "Qubits are shown as horizontal wires.",
                    "Gates are placed along the wires.",
                    "Multi-qubit gates connect multiple wires.",
                    "Circuits can be simulated or run on quantum hardware."
                ],

                "example":
                    "A simple circuit can prepare |0⟩, apply H, "
                    "and then measure the qubit."
            },

            "Measurement": {
                "intro":
                    "Measurement extracts classical information "
                    "from a quantum state and generally changes "
                    "that state.",

                "points": [
                    "A computational-basis measurement of one qubit gives 0 or 1.",
                    "Probabilities depend on squared amplitude magnitudes.",
                    "A superposition does not mean both classical values are directly observed.",
                    "Repeated measurements estimate an output distribution."
                ],

                "example":
                    "For (|0⟩ + |1⟩)/√2, ideal measurements "
                    "produce approximately half 0s and half 1s."
            },

            "Grover's Algorithm": {
                "intro":
                    "Grover's algorithm gives a quadratic speedup "
                    "for searching an unstructured space in the "
                    "standard quantum query model.",

                "points": [
                    "The algorithm prepares a superposition of candidates.",
                    "An oracle marks the desired state.",
                    "Amplitude amplification increases the marked state's probability.",
                    "The ideal query complexity is O(√N)."
                ],

                "example":
                    "A classical black-box search can require "
                    "O(N) queries, while Grover's algorithm "
                    "requires O(√N) queries."
            },

            "Shor's Algorithm": {
                "intro":
                    "Shor's algorithm is a quantum algorithm for "
                    "integer factoring using efficient quantum "
                    "period finding.",

                "points": [
                    "Period finding is the key quantum subroutine.",
                    "The Quantum Fourier Transform is an important component.",
                    "It has important implications for public-key cryptography.",
                    "Practical cryptographic-scale factoring requires large fault-tolerant quantum computers."
                ],

                "example":
                    "Shor's algorithm converts a factoring problem "
                    "into a period-finding problem that can be "
                    "processed using quantum interference."
            }
        }


        st.markdown(
            """
            <div class="learning-panel">

                <div class="learning-title">
                    🧠 QUANTUM COMPUTING LEARNING MODE
                </div>

                <div class="learning-subtitle">
                    Learn quantum computing step by step with
                    explanations, examples, and practice.
                </div>

            </div>
            """,
            unsafe_allow_html=True
        )


        topics = list(lessons.keys())


        selected_topic = st.selectbox(
            "Choose a quantum computing topic",
            topics,

            index=(
                topics.index(
                    st.session_state.learning_topic
                )

                if st.session_state.learning_topic in topics
                else 0
            )
        )


        st.session_state.learning_topic = selected_topic

        lesson = lessons[selected_topic]


        st.markdown(
            f"### ⚛️ {selected_topic}"
        )


        st.markdown(
            f"""
            <div class="learning-card">

                <h3>📘 Lesson</h3>

                <p>
                    {lesson["intro"]}
                </p>

            </div>
            """,
            unsafe_allow_html=True
        )


        st.markdown("#### 🔑 Key Concepts")


        for point in lesson["points"]:

            st.markdown(
                f"- {point}"
            )


        st.markdown(
            f"""
            <div class="learning-card">

                <h3>💡 Example</h3>

                <p>
                    {lesson["example"]}
                </p>

            </div>
            """,
            unsafe_allow_html=True
        )


        st.info(
            f"Learning Mode is active for **{selected_topic}**. "
            "Ask the AI Tutor about this topic using the prompt box below."
        )


        completed = sum(
            1
            for topic in topics
            if st.session_state.learning_progress.get(
                topic,
                False
            )
        )


        st.progress(
            completed / len(topics),

            text=(
                f"Learning progress: "
                f"{completed}/{len(topics)} topics completed"
            )
        )


# ============================================================
# CENTER QUANTUM AI TUTOR HEADER
# ============================================================

st.markdown(
    """
    <div class="quantum-tutor-header">

        <div class="quantum-tutor-title">
            ⚛️ QUANTUM AI TUTOR
        </div>

        <div class="quantum-tutor-subtitle">
            Explore quantum computing through conversation
        </div>

        <div class="quantum-tutor-status">
            ● AI TUTOR ONLINE
        </div>

    </div>
    """,
    unsafe_allow_html=True
)


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
        else "⚛️"
    )

    with st.chat_message(
        role,
        avatar=avatar
    ):

        st.markdown(
            message["content"]
        )


# ============================================================
# ATTACHMENT / VOICE STATUS
# ============================================================

if (
    st.session_state.staged_attachments
    or st.session_state.staged_voice_text
):

    info_items = []


    if st.session_state.staged_attachments:

        info_items.append(
            f"📎 "
            f"{len(st.session_state.staged_attachments)} "
            f"item(s) attached"
        )


    if st.session_state.staged_voice_text:

        info_items.append(
            "🎙️ Voice text staged"
        )


    st.info(
        " | ".join(info_items)
    )


# ============================================================
# FIXED BOTTOM CHAT COMPOSER
# ============================================================

composer_left, composer_input, composer_right = st.columns(
    [0.07, 0.86, 0.07]
)


# ============================================================
# PLUS / ATTACHMENTS
# ============================================================

with composer_left:

    st.markdown(
        '<div class="composer-anchor"></div>',
        unsafe_allow_html=True
    )


    with st.popover(
        "＋",
        help="Add photos, camera, or files"
    ):

        st.markdown("### Attach")


        tab_photos, tab_camera, tab_files = st.tabs(
            [
                "🖼️ Photos",
                "📷 Camera",
                "📎 Files"
            ]
        )


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
                        f"🖼️ Photo: `{photo.name}` "
                        f"({round(photo.size / 1024, 1)} KB)"
                    )


                    if note not in st.session_state.staged_attachments:

                        st.session_state.staged_attachments.append(
                            note
                        )


                st.success(
                    f"{len(photos)} photo(s) attached."
                )


        with tab_camera:

            camera_photo = st.camera_input(
                "Take a snapshot",
                key="custom_input_camera"
            )


            if camera_photo:

                note = "📷 *Camera Snapshot*"


                if note not in st.session_state.staged_attachments:

                    st.session_state.staged_attachments.append(
                        note
                    )


                st.success(
                    "Snapshot attached."
                )


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
                        f"📎 Document: `{file.name}` "
                        f"({round(file.size / 1024, 1)} KB)"
                    )


                    if note not in st.session_state.staged_attachments:

                        st.session_state.staged_attachments.append(
                            note
                        )


                st.success(
                    f"{len(files)} file(s) attached."
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
# VOICE INPUT
# ============================================================

with composer_right:

    with st.popover(
        "🎤",
        help="Voice recording"
    ):

        st.markdown("### Voice Input")


        audio_stream = st.audio_input(
            "Record audio note",
            key="custom_input_voice"
        )


        if audio_stream:

            transcription = transcribe_audio(
                audio_stream.read()
            )


            if transcription:

                st.session_state.staged_voice_text = (
                    transcription
                )

                st.success(
                    "Voice transcribed! Text staged for prompt."
                )


# ============================================================
# PROCESS USER INPUT
# ============================================================

if prompt:

    user_text = prompt.strip()

    combined_parts = []


    if user_text:

        combined_parts.append(
            user_text
        )


    if st.session_state.staged_voice_text:

        combined_parts.append(
            "🎙️ Transcribed Voice Note: "
            f"\"{st.session_state.staged_voice_text}\""
        )


    if st.session_state.staged_attachments:

        combined_parts.append(
            "\n".join(
                st.session_state.staged_attachments
            )
        )


    final_user_message = "\n\n".join(
        combined_parts
    )


    # Add user message

    st.session_state.chats[
        st.session_state.current_chat
    ].append(
        {
            "role": "user",
            "content": final_user_message
        }
    )


    # Generate AI response

    with st.spinner(
        "⚛️ Quantum AI is thinking..."
    ):

        answer = ai_response(
            st.session_state.chats[
                st.session_state.current_chat
            ]
        )


    # Add AI response

    st.session_state.chats[
        st.session_state.current_chat
    ].append(
        {
            "role": "assistant",
            "content": answer
        }
    )


    # Clear staged input

    st.session_state.staged_attachments = []

    st.session_state.staged_voice_text = ""


    st.rerun()
