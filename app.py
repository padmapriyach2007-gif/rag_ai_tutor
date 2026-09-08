import streamlit as st

st.set_page_config(
    page_title="Quantum AI Tutor",
    page_icon="⚛️",
    layout="wide"
)

# -----------------------------
# CSS
# -----------------------------
st.markdown("""
<style>

body {
    background-color: #070a1c;
}

.stApp {
    background-color: #070a1c;
    color: white;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background-color: #08081b;
}

/* Main title */
.hero {
    background: #191b25;
    padding: 45px;
    border-radius: 12px;
    text-align: center;
    margin-top: 80px;
}

.quantum-symbol {
    font-size: 55px;
    margin-bottom: 15px;
}

.hero-title {
    font-size: 36px;
    font-weight: bold;
    color: white;
}

.hero-subtitle {
    font-size: 18px;
    color: #c9c7d8;
    margin-top: 15px;
}

.status {
    display: inline-block;
    margin-top: 25px;
    padding: 10px 20px;
    border-radius: 25px;
    background: #15152a;
    color: #ffffff;
}

/* Chat messages */
.user-message {
    background: #332b68;
    padding: 12px 18px;
    border-radius: 12px;
    margin: 10px 0;
    text-align: right;
}

.ai-message {
    background: #20212c;
    padding: 12px 18px;
    border-radius: 12px;
    margin: 10px 0;
}

/* Input */
.stTextInput input {
    background-color: #17162f;
    color: white;
}

</style>
""", unsafe_allow_html=True)


# -----------------------------
# SIDEBAR
# -----------------------------

with st.sidebar:

    st.title("💬 Your Chats")

    if st.button("＋ New Chat", use_container_width=True):
        st.session_state.messages = []

    st.markdown("### 💬 Quantum Learning")

    st.divider()

    if st.button("🗑️ Delete Current Chat", use_container_width=True):
        st.session_state.messages = []

    if st.button("🧹 Clear Conversation", use_container_width=True):
        st.session_state.messages = []

    st.button("🚪 Logout", use_container_width=True)

    st.markdown("---")

    st.info("""
    🧠 **Learning Mode**

    Ask questions about:

    • Quantum Computing  
    • Qubits  
    • Quantum Gates  
    • Qiskit  
    • Algorithms
    """)


# -----------------------------
# SESSION STATE
# -----------------------------

if "messages" not in st.session_state:
    st.session_state.messages = []


# -----------------------------
# HERO SECTION
# -----------------------------

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
        ● &nbsp; AI TUTOR ONLINE
    </div>

</div>
""", unsafe_allow_html=True)


# -----------------------------
# DISPLAY CHAT
# -----------------------------

for message in st.session_state.messages:

    if message["role"] == "user":

        st.markdown(
            f'<div class="user-message">{message["content"]}</div>',
            unsafe_allow_html=True
        )

    else:

        st.markdown(
            f'<div class="ai-message">{message["content"]}</div>',
            unsafe_allow_html=True
        )


# -----------------------------
# AI RESPONSE
# -----------------------------

def quantum_response(question):

    q = question.lower()

    if "qubit" in q:
        return """
        A **qubit** is the basic unit of quantum information.
        Unlike a classical bit, which is either 0 or 1, a qubit
        can exist in a superposition of |0⟩ and |1⟩.
        """

    elif "superposition" in q:
        return """
        **Superposition** means a quantum system can exist in a
        combination of multiple states at the same time.
        """

    elif "entanglement" in q:
        return """
        **Quantum entanglement** is a phenomenon where quantum
        states of two or more particles become correlated.
        """

    elif "hadamard" in q:
        return """
        The **Hadamard (H) gate** creates a superposition.
        For example:

        H|0⟩ = (|0⟩ + |1⟩) / √2
        """

    elif "cnot" in q:
        return """
        **CNOT** is a two-qubit controlled-NOT gate.
        It flips the target qubit when the control qubit is |1⟩.
        """

    elif "qiskit" in q:
        return """
        **Qiskit** is an open-source framework for programming
        and experimenting with quantum computers.
        """

    elif "quantum gate" in q:
        return """
        Common quantum gates include **X, Y, Z, H, S, T and CNOT**.
        They are used to manipulate qubits.
        """

    elif "hello" in q or "hi" in q:
        return """
        Hello! 👋 I'm your **Quantum AI Tutor**.

        Ask me about qubits, superposition, entanglement,
        quantum gates, Qiskit or quantum algorithms.
        """

    else:
        return """
        I can help you learn **quantum computing**.

        Try asking me about:
        - Qubits
        - Superposition
        - Entanglement
        - Quantum gates
        - Hadamard gate
        - CNOT
        - Qiskit
        """


# -----------------------------
# CHAT INPUT
# -----------------------------

question = st.chat_input(
    "Ask anything about quantum computing..."
)

if question:

    # Add user message
    st.session_state.messages.append({
        "role": "user",
        "content": question
    })

    # Generate response
    answer = quantum_response(question)

    # Add AI message
    st.session_state.messages.append({
        "role": "assistant",
        "content": answer
    })

    # Refresh
    st.rerun()
