import streamlit as st
from groq import Groq
import os

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
# SESSION STATE
# ============================================================

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "user_email" not in st.session_state:
    st.session_state.user_email = ""

if "chats" not in st.session_state:
    st.session_state.chats = {
        "Quantum Learning": []
    }

if "current_chat" not in st.session_state:
    st.session_state.current_chat = "Quantum Learning"


# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown(
    """
<style>

    /* ========================================================
       GOOGLE FONT
       ======================================================== */

    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Space+Grotesk:wght@400;500;600;700&display=swap');


    /* ========================================================
       GLOBAL APP
       ======================================================== */

    .stApp {
        background:
            radial-gradient(
                circle at 15% 15%,
                rgba(78, 55, 180, 0.22) 0%,
                transparent 30%
            ),
            radial-gradient(
                circle at 85% 20%,
                rgba(0, 140, 255, 0.16) 0%,
                transparent 28%
            ),
            radial-gradient(
                circle at 50% 90%,
                rgba(116, 44, 255, 0.12) 0%,
                transparent 30%
            ),
            linear-gradient(
                135deg,
                #030511 0%,
                #070a1f 45%,
                #040718 100%
            );

        color: #ffffff;
        font-family: 'Inter', sans-serif;
    }


    /* ========================================================
       QUANTUM GRID BACKGROUND
       ======================================================== */

    .stApp::before {
        content: "";
        position: fixed;
        inset: 0;

        background-image:
            linear-gradient(
                rgba(100, 110, 255, 0.045) 1px,
                transparent 1px
            ),
            linear-gradient(
                90deg,
                rgba(100, 110, 255, 0.045) 1px,
                transparent 1px
            );

        background-size: 45px 45px;
        pointer-events: none;
        z-index: 0;
    }


    /* ========================================================
       QUANTUM GLOW
       ======================================================== */

    .stApp::after {
        content: "";
        position: fixed;
        width: 500px;
        height: 500px;

        left: 50%;
        top: 50%;

        transform: translate(-50%, -50%);

        background:
            radial-gradient(
                circle,
                rgba(90, 80, 255, 0.08) 0%,
                transparent 65%
            );

        filter: blur(20px);
        pointer-events: none;
        z-index: 0;
    }


    /* ========================================================
       MAIN CONTENT
       ======================================================== */

    [data-testid="stMain"] {
        background: transparent;
    }

    .main .block-container {
        position: relative;
        z-index: 2;
        padding-top: 1.5rem;
        padding-bottom: 3rem;
        max-width: 1250px;
    }


    /* ========================================================
       SIDEBAR
       ======================================================== */

    [data-testid="stSidebar"] {
        background:
            linear-gradient(
                180deg,
                #060817 0%,
                #080b20 50%,
                #050714 100%
            );

        border-right: 1px solid rgba(125, 105, 255, 0.20);
    }

    [data-testid="stSidebar"] > div:first-child {
        background: transparent;
    }

    [data-testid="stSidebar"] h1 {
        color: #ffffff !important;
        font-family: 'Space Grotesk', sans-serif;
        font-weight: 700;
        letter-spacing: 1px;
    }

    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3 {
        color: #e8e9ff !important;
        font-family: 'Space Grotesk', sans-serif;
    }

    [data-testid="stSidebar"] p {
        color: #9fa6c7;
    }


    /* ========================================================
       SIDEBAR BUTTONS
       ======================================================== */

    [data-testid="stSidebar"] .stButton > button {
        width: 100%;
        min-height: 44px;

        border-radius: 10px;

        background:
            linear-gradient(
                135deg,
                rgba(36, 39, 65, 0.95),
                rgba(21, 24, 45, 0.95)
            );

        border: 1px solid rgba(111, 105, 180, 0.25);

        color: #e9eaff;

        font-family: 'Inter', sans-serif;
        font-weight: 500;

        transition:
            all 0.2s ease;

        box-shadow:
            0 4px 15px rgba(0, 0, 0, 0.18);
    }

    [data-testid="stSidebar"] .stButton > button:hover {
        background:
            linear-gradient(
                135deg,
                rgba(77, 66, 150, 0.75),
                rgba(31, 47, 94, 0.85)
            );

        border-color: rgba(125, 110, 255, 0.70);

        color: white;

        transform: translateY(-1px);

        box-shadow:
            0 6px 20px rgba(84, 65, 255, 0.20);
    }


    /* ========================================================
       SIDEBAR DIVIDERS
       ======================================================== */

    [data-testid="stSidebar"] hr {
        border-color: rgba(120, 120, 170, 0.14);
    }


    /* ========================================================
       HERO BOX
       ======================================================== */

    .hero-box {
        position: relative;
        overflow: hidden;

        background:
            linear-gradient(
                135deg,
                rgba(24, 28, 61, 0.88),
                rgba(9, 13, 36, 0.92)
            );

        border:
            1px solid rgba(120, 105, 255, 0.30);

        border-radius: 24px;

        padding: 55px 25px;

        text-align: center;

        margin-top: 15px;
        margin-bottom: 28px;

        box-shadow:
            0 20px 60px rgba(0, 0, 0, 0.35),
            inset 0 1px 0 rgba(255, 255, 255, 0.05);
    }


    /* Decorative quantum glow */

    .hero-box::before {
        content: "";

        position: absolute;

        width: 300px;
        height: 300px;

        left: -100px;
        top: -150px;

        background:
            radial-gradient(
                circle,
                rgba(102, 74, 255, 0.22),
                transparent 70%
            );

        pointer-events: none;
    }

    .hero-box::after {
        content: "";

        position: absolute;

        width: 300px;
        height: 300px;

        right: -120px;
        bottom: -160px;

        background:
            radial-gradient(
                circle,
                rgba(0, 174, 255, 0.18),
                transparent 70%
            );

        pointer-events: none;
    }


    /* ========================================================
       HERO ICON
       ======================================================== */

    .hero-icon {
        font-size: 52px;

        text-shadow:
            0 0 10px rgba(123, 103, 255, 0.9),
            0 0 25px rgba(66, 180, 255, 0.5);

        position: relative;
        z-index: 2;
    }


    /* ========================================================
       HERO TITLE
       ======================================================== */

    .hero-title {
        font-family: 'Space Grotesk', sans-serif;

        font-size: 44px;

        font-weight: 700;

        letter-spacing: -1px;

        color: #ffffff;

        margin-top: 10px;

        position: relative;
        z-index: 2;

        text-shadow:
            0 0 25px rgba(120, 105, 255, 0.30);
    }


    /* ========================================================
       HERO SUBTITLE
       ======================================================== */

    .hero-subtitle {
        font-size: 17px;

        color: #aeb5d8;

        margin-top: 10px;

        position: relative;
        z-index: 2;
    }


    /* ========================================================
       ONLINE STATUS
       ======================================================== */

    .online {
        color: #45f29a;

        font-size: 13px;

        font-weight: 600;

        letter-spacing: 1px;

        margin-top: 18px;

        position: relative;
        z-index: 2;

        text-shadow:
            0 0 12px rgba(69, 242, 154, 0.50);
    }


    /* ========================================================
       LEARNING BOX
       ======================================================== */

    .learning-box {
        background:
            linear-gradient(
                135deg,
                rgba(22, 48, 94, 0.85),
                rgba(11, 28, 58, 0.85)
            );

        border:
            1px solid rgba(65, 139, 255, 0.30);

        border-radius: 12px;

        padding: 16px;

        margin-top: 20px;

        box-shadow:
            0 8px 25px rgba(0, 0, 0, 0.20);
    }


    /* ========================================================
       LOGIN BOX
       ======================================================== */

    .login-box {
        position: relative;
        overflow: hidden;

        max-width: 550px;

        margin: 90px auto 30px auto;

        background:
            linear-gradient(
                145deg,
                rgba(25, 30, 65, 0.94),
                rgba(9, 12, 31, 0.96)
            );

        border:
            1px solid rgba(120, 105, 255, 0.35);

        border-radius: 24px;

        padding: 45px;

        text-align: center;

        box-shadow:
            0 25px 80px rgba(0, 0, 0, 0.50),
            0 0 50px rgba(74, 65, 255, 0.08);

        backdrop-filter: blur(15px);
    }

    .login-box::before {
        content: "";

        position: absolute;

        width: 220px;
        height: 220px;

        top: -100px;
        left: -80px;

        background:
            radial-gradient(
                circle,
                rgba(92, 68, 255, 0.20),
                transparent 70%
            );
    }

    .login-box h1 {
        font-family: 'Space Grotesk', sans-serif;

        color: white;

        font-size: 36px;
    }

    .login-box p {
        color: #aeb5d8;
        font-size: 16px;
    }


    /* ========================================================
       TEXT INPUTS
       ======================================================== */

    .stTextInput input {
        background-color: rgba(10, 13, 32, 0.85) !important;

        color: white !important;

        border:
            1px solid rgba(100, 100, 160, 0.30) !important;

        border-radius: 10px !important;

        min-height: 45px;
    }

    .stTextInput input:focus {
        border-color:
            rgba(112, 96, 255, 0.80) !important;

        box-shadow:
            0 0 15px rgba(96, 78, 255, 0.15) !important;
    }


    /* ========================================================
       LOGIN BUTTON
       ======================================================== */

    .stButton > button {
        border-radius: 10px;

        min-height: 45px;

        font-weight: 600;

        background:
            linear-gradient(
                135deg,
                #5146d8,
                #2869d8
            );

        border: 1px solid rgba(150, 140, 255, 0.35);

        color: white;

        box-shadow:
            0 8px 25px rgba(61, 75, 220, 0.20);

        transition: all 0.2s ease;
    }

    .stButton > button:hover {
        transform: translateY(-1px);

        box-shadow:
            0 10px 30px rgba(61, 75, 220, 0.35);
    }


    /* ========================================================
       CHAT MESSAGES
       ======================================================== */

    [data-testid="stChatMessage"] {
        border-radius: 15px;

        margin-bottom: 12px;
    }


    /* ========================================================
       CHAT INPUT
       ======================================================== */

    [data-testid="stChatInput"] {
        border-radius: 15px;
    }

    [data-testid="stChatInput"] textarea {
        background-color: rgba(11, 15, 36, 0.95) !important;

        color: white !important;

        border:
            1px solid rgba(108, 99, 255, 0.35) !important;

        border-radius: 15px !important;
    }


    /* ========================================================
       EXPANDER
       ======================================================== */

    [data-testid="stSidebar"] [data-testid="stExpander"] {
        background-color: rgba(18, 21, 43, 0.80);

        border:
            1px solid rgba(100, 100, 160, 0.20);

        border-radius: 10px;
    }


    /* ========================================================
       INFO BOX
       ======================================================== */

    [data-testid="stSidebar"] .stAlert {
        background:
            linear-gradient(
                135deg,
                rgba(20, 42, 80, 0.85),
                rgba(12, 28, 58, 0.85)
            );

        border:
            1px solid rgba(55, 125, 220, 0.30);

        border-radius: 12px;
    }


    /* ========================================================
       CHAT TEXT
       ======================================================== */

    [data-testid="stChatMessage"] p {
        line-height: 1.65;
    }


    /* ========================================================
       SCROLLBAR
       ======================================================== */

    ::-webkit-scrollbar {
        width: 7px;
    }

    ::-webkit-scrollbar-track {
        background: #050713;
    }

    ::-webkit-scrollbar-thumb {
        background: #35365b;
        border-radius: 10px;
    }

    ::-webkit-scrollbar-thumb:hover {
        background: #5a55a0;
    }


    /* ========================================================
       RESPONSIVE
       ======================================================== */

    @media (max-width: 768px) {

        .hero-title {
            font-size: 32px;
        }

        .hero-subtitle {
            font-size: 15px;
        }

        .hero-box {
            padding: 40px 15px;
        }

        .login-box {
            margin: 50px auto;
            padding: 30px 20px;
        }

    }

</style>
""",
    unsafe_allow_html=True
)


# ============================================================
# QUANTUM AI RESPONSE
# ============================================================

def ai_response(chat_history):

    # Get Groq API key
    api_key = os.environ.get("GROQ_API_KEY")

    if not api_key:
        return (
            "⚠️ **Groq API key is missing.**\n\n"
            "Please set your `GROQ_API_KEY` environment variable."
        )

    # Create Groq client
    client = Groq(
        api_key=api_key
    )

    # System instructions
    system_message = {
        "role": "system",
        "content": """
You are a helpful, intelligent AI assistant.

You can answer questions about any subject, including:
science, mathematics, programming, technology, education,
history, general knowledge, writing, and everyday questions.

Do not restrict yourself strictly to quantum computing.

Explain things clearly and adapt your answer to the user's level.

If the user asks for code, provide working code and explain it.

If the user asks a conceptual question, explain it with examples.

If the question is unclear, ask a useful clarification.
"""
    }

    # Combine system message and conversation history
    full_messages = [system_message] + chat_history

    try:

        response = client.chat.completions.create(
            model="openai/gpt-oss-20b",
            messages=full_messages
        )

        return response.choices[0].message.content

    except Exception as e:

        return (
            "⚠️ **Sorry, I could not generate a response right now.**\n\n"
            f"Error details: `{str(e)}`"
        )


def answer_question(question, chat_history):
    return ai_response(chat_history)


# ============================================================
# LOGIN SCREEN
# ============================================================

if not st.session_state.logged_in:

    st.markdown(
        """
<div class="login-box">

    <div class="hero-icon">
        ⚛️
    </div>

    <h1>
        Quantum Lab
    </h1>

    <p>
        AI-Powered Learning Space
    </p>

</div>
""",
        unsafe_allow_html=True
    )

    st.subheader("🔐 Login")

    email = st.text_input(
        "Email address",
        placeholder="Enter your email"
    )

    if st.button(
        "🚀 Login",
        use_container_width=True
    ):

        if email.strip() == "":
            st.error("Please enter your email address.")

        else:
            st.session_state.user_email = email.strip()
            st.session_state.logged_in = True

            st.success("Login successful!")

            st.rerun()

    st.stop()


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    # --------------------------------------------------------
    # BRAND
    # --------------------------------------------------------

    st.title("⚛️ QUANTUM LAB")

    st.caption("AI-Powered Learning Space")


    # --------------------------------------------------------
    # USER
    # --------------------------------------------------------

    st.markdown("---")

    st.write("👤 **Logged In**")

    st.caption(st.session_state.user_email)


    # --------------------------------------------------------
    # NEW CHAT
    # --------------------------------------------------------

    st.markdown("---")

    if st.button(
        "➕ New Chat",
        use_container_width=True
    ):

        chat_number = 1

        while f"New Quantum Chat {chat_number}" in st.session_state.chats:
            chat_number += 1

        new_chat_name = f"New Quantum Chat {chat_number}"

        st.session_state.chats[new_chat_name] = []

        st.session_state.current_chat = new_chat_name

        st.toast("New chat created!")

        st.rerun()


    # --------------------------------------------------------
    # YOUR CHATS
    # --------------------------------------------------------

    st.markdown("---")

    st.subheader("💬 Your Chats")

    chat_names = list(st.session_state.chats.keys())

    for chat_name in chat_names:

        is_current = (
            chat_name == st.session_state.current_chat
        )

        button_text = (
            f"🟣 {chat_name}"
            if is_current
            else f"💬 {chat_name}"
        )

        if st.button(
            button_text,
            key=f"open_{chat_name}",
            use_container_width=True
        ):

            st.session_state.current_chat = chat_name

            st.rerun()


    # --------------------------------------------------------
    # RENAME CHAT
    # --------------------------------------------------------

    st.markdown("---")

    with st.expander("✏️ Rename Current Chat"):

        current_name = st.session_state.current_chat

        new_name = st.text_input(
            "New chat name",
            value=current_name,
            key="rename_input"
        )

        if st.button(
            "Save New Name",
            use_container_width=True
        ):

            new_name = new_name.strip()

            if new_name == "":
                st.error("Chat name cannot be empty.")

            elif new_name == current_name:
                st.info("This is already the current name.")

            elif new_name in st.session_state.chats:
                st.error("A chat with this name already exists.")

            else:

                st.session_state.chats[new_name] = (
                    st.session_state.chats.pop(current_name)
                )

                st.session_state.current_chat = new_name

                st.success("Chat renamed!")

                st.rerun()


    # --------------------------------------------------------
    # DELETE CURRENT CHAT
    # --------------------------------------------------------

    st.markdown("---")

    if st.button(
        "🗑️ Delete Current Chat",
        use_container_width=True
    ):

        current_name = st.session_state.current_chat

        if len(st.session_state.chats) == 1:

            st.session_state.chats[current_name] = []

            st.toast("Chat cleared!")

        else:

            del st.session_state.chats[current_name]

            remaining_chats = list(
                st.session_state.chats.keys()
            )

            st.session_state.current_chat = remaining_chats[0]

            st.toast("Chat deleted!")

        st.rerun()


    # --------------------------------------------------------
    # CLEAR CONVERSATION
    # --------------------------------------------------------

    if st.button(
        "🧹 Clear Conversation",
        use_container_width=True
    ):

        current_name = st.session_state.current_chat

        st.session_state.chats[current_name] = []

        st.toast("Conversation cleared!")

        st.rerun()


    # --------------------------------------------------------
    # LOGOUT
    # --------------------------------------------------------

    if st.button(
        "🚪 Logout",
        use_container_width=True
    ):

        st.session_state.logged_in = False

        st.rerun()


    # --------------------------------------------------------
    # LEARNING MODE
    # --------------------------------------------------------

    st.markdown("---")

    st.info(
        """
🧠 **Learning Mode**

Ask questions about:

• Quantum Computing

• Qubits

• Quantum Gates

• Qiskit
"""
    )


# ============================================================
# MAIN AREA
# ============================================================

st.markdown(
    """
<div class="hero-box">

<div class="hero-icon">
⚛️
</div>

<div class="hero-title">
Quantum AI Tutor
</div>

<div class="hero-subtitle">
Explore quantum computing through conversation
</div>

<div class="online">
● AI TUTOR ONLINE
</div>

</div>
""",
    unsafe_allow_html=True
)


# ============================================================
# CURRENT CHAT
# ============================================================

current_chat = st.session_state.current_chat

messages = st.session_state.chats[current_chat]


# ============================================================
# DISPLAY CHAT
# ============================================================

for message in messages:

    if message["role"] == "user":

        with st.chat_message("user"):
            st.markdown(message["content"])

    else:

        with st.chat_message("assistant"):
            st.markdown(message["content"])


# ============================================================
# CHAT INPUT & LOGIC
# ============================================================

question = st.chat_input(
    "Ask anything about quantum computing..."
)


if question:

    # 1. Append user message
    messages.append({
        "role": "user",
        "content": question
    })

    # 2. Render user message
    with st.chat_message("user"):
        st.markdown(question)

    # 3. Generate response
    with st.chat_message("assistant"):

        with st.spinner("Thinking..."):

            answer = answer_question(
                question,
                messages
            )

            st.markdown(answer)

    # 4. Append AI response
    messages.append({
        "role": "assistant",
        "content": answer
    })

    # 5. Save updated state
    st.session_state.chats[current_chat] = messages

    st.rerun()
