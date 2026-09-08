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

    /* =========================
       MAIN APP
       ========================= */

    .stApp {
        background-color: #07091a;
    }

    [data-testid="stMain"] {
        background-color: #07091a;
    }


    /* =========================
       SIDEBAR
       ========================= */

    [data-testid="stSidebar"] {
        background-color: #08091b;
    }

    [data-testid="stSidebar"] h1 {
        color: white;
    }


    /* =========================
       BUTTONS
       ========================= */

    [data-testid="stSidebar"] .stButton > button {
        width: 100%;
        border-radius: 8px;
        min-height: 42px;
        background-color: #292b37;
        border: 1px solid #3c3e50;
        color: white;
    }

    [data-testid="stSidebar"] .stButton > button:hover {
        background-color: #363847;
        border-color: #6c63ff;
    }


    /* =========================
       HERO
       ========================= */

    .hero-box {
        background-color: #191b25;
        border: 1px solid #292c3a;
        border-radius: 15px;
        padding: 55px 20px;
        text-align: center;
        margin-top: 25px;
        margin-bottom: 25px;
    }

    .hero-icon {
        font-size: 48px;
    }

    .hero-title {
        font-size: 42px;
        font-weight: 700;
        color: white;
        margin-top: 10px;
    }

    .hero-subtitle {
        font-size: 17px;
        color: #aeb1c5;
        margin-top: 10px;
    }

    .online {
        color: #42e88b;
        font-size: 14px;
        margin-top: 18px;
    }


    /* =========================
       LEARNING BOX
       ========================= */

    .learning-box {
        background-color: #10294e;
        border: 1px solid #193d70;
        border-radius: 10px;
        padding: 16px;
        margin-top: 20px;
    }


    /* =========================
       LOGIN
       ========================= */

    .login-box {
        max-width: 550px;
        margin: 100px auto;
        background-color: #191b25;
        border: 1px solid #292c3a;
        border-radius: 15px;
        padding: 40px;
        text-align: center;
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
    <div class="hero-icon">⚛️</div>
    <h1>Quantum Lab</h1>
    <p>AI-Powered Learning Space</p>
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

