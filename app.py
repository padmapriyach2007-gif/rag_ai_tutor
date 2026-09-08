import streamlit as st

# =========================================================
# PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="Quantum Lab",
    page_icon="⚛️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =========================================================
# CUSTOM CSS
# =========================================================

st.markdown("""
<style>

    /* ---------- Main App ---------- */

    .stApp {
        background: #07091a;
        color: white;
    }

    /* ---------- Sidebar ---------- */

    section[data-testid="stSidebar"] {
        background: #08091b;
        border-right: 1px solid #202238;
    }

    section[data-testid="stSidebar"] > div {
        padding: 20px 18px;
    }

    .brand {
        margin-bottom: 28px;
    }

    .brand-title {
        font-size: 24px;
        font-weight: 700;
        color: white;
        margin-bottom: 4px;
    }

    .brand-subtitle {
        font-size: 14px;
        color: #a7aac4;
    }

    .logged-in {
        margin-top: 25px;
        padding: 12px 0;
        color: white;
        font-size: 15px;
    }

    .email {
        color: #8d91ad;
        font-size: 13px;
        margin-top: 5px;
    }

    .section-title {
        color: white;
        font-size: 17px;
        font-weight: 600;
        margin-top: 25px;
        margin-bottom: 14px;
    }

    .chat-item {
        padding: 10px 8px;
        color: #d8d9e8;
        font-size: 15px;
        border-radius: 8px;
    }

    .chat-item:hover {
        background: #17192b;
    }

    .divider {
        height: 1px;
        background: #292b3d;
        margin: 20px 0;
    }

    /* ---------- Sidebar Buttons ---------- */

    section[data-testid="stSidebar"] .stButton > button {
        width: 100%;
        border-radius: 8px;
        border: 1px solid #3b3d50;
        background: #292b37;
        color: white;
        height: 42px;
        font-size: 14px;
        margin-bottom: 8px;
    }

    section[data-testid="stSidebar"] .stButton > button:hover {
        border-color: #6366f1;
        color: white;
        background: #333546;
    }

    /* ---------- Learning Mode ---------- */

    .learning-box {
        margin-top: 22px;
        padding: 18px;
        background: #10294e;
        border-radius: 10px;
        border: 1px solid #193d70;
    }

    .learning-title {
        color: #4da3ff;
        font-size: 16px;
        font-weight: 600;
        margin-bottom: 12px;
    }

    .learning-text {
        color: #b8c0d8;
        font-size: 14px;
        line-height: 1.8;
    }

    /* ---------- Main Content ---------- */

    .main-container {
        max-width: 1000px;
        margin: auto;
        padding-top: 50px;
    }

    .hero {
        background: #191b25;
        border: 1px solid #252837;
        border-radius: 15px;
        padding: 65px 30px;
        text-align: center;
        margin-bottom: 25px;
    }

    .quantum-symbol {
        font-size: 42px;
        margin-bottom: 15px;
    }

    .hero-title {
        color: white;
        font-size: 42px;
        font-weight: 700;
        margin-bottom: 12px;
    }

    .hero-subtitle {
        color: #aeb1c5;
        font-size: 17px;
        margin-bottom: 20px;
    }

    .status {
        color: #b9bbc9;
        font-size: 14px;
    }

    .status-dot {
        color: #42e88b;
    }

    /* ---------- Chat Messages ---------- */

    .user-message {
        background: #252735;
        padding: 14px 18px;
        border-radius: 12px;
        margin: 10px 0;
        color: white;
    }

    .ai-message {
        background: #11131d;
        border: 1px solid #252837;
        padding: 14px 18px;
        border-radius: 12px;
        margin: 10px 0;
        color: #e7e8f0;
    }

    .message-label {
        font-size: 12px;
        color: #8f94ae;
        margin-bottom: 5px;
    }

</style>
""", unsafe_allow_html=True)


# =========================================================
# SESSION STATE
# =========================================================

if "messages" not in st.session_state:
    st.session_state.messages = []

if "chat_name" not in st.session_state:
    st.session_state.chat_name = "Quantum Learning"


# =========================================================
# SIDEBAR
# =========================================================

with st.sidebar:

    # Brand
    st.markdown("""
    <div class="brand">
        <div class="brand-title">⚛️ QUANTUM LAB</div>
        <div class="brand-subtitle">AI-Powered Learning Space</div>
    </div>
    """, unsafe_allow_html=True)

    # Logged in
    st.markdown("""
    <div class="logged-in">
        👤 <b>Logged In</b>
        <div class="email">your@email.com</div>
    </div>
    """, unsafe_allow_html=True)

    # New Chat
    if st.button("➕  New Chat", use_container_width=True):
        st.session_state.messages = []
        st.session_state.chat_name = "New Quantum Chat"
        st.rerun()

    # Your Chats
    st.markdown('<div class="section-title">💬 Your Chats</div>',
                unsafe_allow_html=True)

    st.markdown("""
    <div class="chat-item">💬 Quantum Learning</div>
    <div class="chat-item">💬 New Quantum Chat</div>
    """, unsafe_allow_html=True)

    # Divider
    st.markdown('<div class="divider"></div>',
                unsafe_allow_html=True)

    # Delete Current Chat
    if st.button("🗑️  Delete Current Chat", use_container_width=True):
        st.session_state.messages = []
        st.session_state.chat_name = "Quantum Learning"
        st.rerun()

    # Clear Conversation
    if st.button("🧹  Clear Conversation", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

    # Logout
    if st.button("🚪  Logout", use_container_width=True):
        st.session_state.messages = []
        st.session_state.chat_name = "Quantum Learning"
        st.rerun()

    # Divider
    st.markdown('<div class="divider"></div>',
                unsafe_allow_html=True)

    # Learning Mode
    st.markdown("""
    <div class="learning-box">
        <div class="learning-title">🧠 Learning Mode</div>

        <div class="learning-text">
            Ask questions about:<br><br>
            • Quantum Computing<br>
            • Qubits<br>
            • Quantum Gates<br>
            • Qiskit
        </div>
    </div>
    """, unsafe_allow_html=True)


# =========================================================
# MAIN AREA
# =========================================================

st.markdown('<div class="main-container">', unsafe_allow_html=True)

# Hero section
st.markdown("""
<div class="hero">

    <div class="quantum-symbol">
        ⚛️
    </div>

    <div class="hero-title">
        Quantum AI Tutor
    </div>

    <div class="hero-subtitle">
        Explore quantum computing through conversation
    </div>

    <div class="status">
        <span class="status-dot">●</span>
        &nbsp; AI TUTOR ONLINE
    </div>

</div>
""", unsafe_allow_html=True)


# =========================================================
# AI RESPONSE FUNCTION
# =========================================================

def quantum_response(question):

    q = question.lower().strip()

    if "qubit" in q:
        return """
        A **qubit** is the basic unit of quantum information.

        Unlike a classical bit, which can be either 0 or 1,
        a qubit can exist in a **superposition of |0⟩ and |1⟩**.

        Example:

        |ψ⟩ = α|0⟩ + β|1⟩

        where α and β are probability amplitudes.
        """

    elif "superposition" in q:
        return """
        **Superposition** means that a quantum system can exist
        in a combination of multiple states at the same time.

        For a qubit:

        |ψ⟩ = α|0⟩ + β|1⟩

        When measured, the qubit gives either 0 or 1.
        """

    elif "entanglement" in q:
        return """
        **Quantum entanglement** is a phenomenon where two or more
        qubits become correlated so strongly that their quantum
        states cannot be described independently.

        Measuring one entangled qubit gives information about the
        other qubit.
        """

    elif "hadamard" in q:
        return """
        The **Hadamard gate (H)** creates superposition.

        For example:

        |0⟩ → (|0⟩ + |1⟩) / √2

        It is one of the most commonly used quantum gates.
        """

    elif "cnot" in q:
        return """
        **CNOT (Controlled-NOT)** is a two-qubit quantum gate.

        It has:
        • Control qubit
        • Target qubit

        The target qubit is flipped only when the control qubit
        is in state |1⟩.
        """

    elif "qiskit" in q:
        return """
        **Qiskit** is an open-source framework used for programming
        and experimenting with quantum computers.

        You can use Python with Qiskit to create quantum circuits,
        apply quantum gates, and run simulations.
        """

    elif "quantum gate" in q or "quantum gates" in q:
        return """
        Quantum gates manipulate qubits.

        Common quantum gates include:

        • X gate – quantum NOT
        • Y gate
        • Z gate
        • H gate – creates superposition
        • S gate
        • T gate
        • CNOT – controlled operation
        """

    elif "hello" in q or "hi" in q or "hey" in q:
        return """
        Hello! 👋

        I'm your **Quantum AI Tutor**.

        Ask me anything about:
        • Qubits
        • Superposition
        • Entanglement
        • Quantum gates
        • Quantum circuits
        • Qiskit
        """

    else:
        return f"""
        That's an interesting question about quantum computing! ⚛️

        You asked:

        **{question}**

        I can help you learn topics such as **qubits,
        superposition, entanglement, quantum gates,
        quantum circuits, and Qiskit**.

        Try asking something like:

        **"What is a qubit?"**
        """


# =========================================================
# DISPLAY PREVIOUS MESSAGES
# =========================================================

for message in st.session_state.messages:

    if message["role"] == "user":

        st.markdown(
            f"""
            <div class="user-message">
                <div class="message-label">You</div>
                {message["content"]}
            </div>
            """,
            unsafe_allow_html=True
        )

    else:

        st.markdown(
            f"""
            <div class="ai-message">
                <div class="message-label">⚛️ Quantum AI Tutor</div>
                {message["content"]}
            </div>
            """,
            unsafe_allow_html=True
        )


# =========================================================
# CHAT INPUT
# =========================================================

question = st.chat_input(
    "Ask anything about quantum computing..."
)

if question:

    # Store user message
    st.session_state.messages.append({
        "role": "user",
        "content": question
    })

    # Generate response
    answer = quantum_response(question)

    # Store AI response
    st.session_state.messages.append({
        "role": "assistant",
        "content": answer
    })

    st.rerun()


st.markdown('</div>', unsafe_allow_html=True)
