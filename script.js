// ==========================================
// QUANTUM AI TUTOR - JAVASCRIPT
// ==========================================

// Get HTML elements
const input = document.getElementById("messageInput");
const sendButton = document.querySelector(".chat-box button");

// Create chat messages container
const chatContainer = document.createElement("div");
chatContainer.className = "chat-container";

// Insert chat container before chat box
document.querySelector(".main").insertBefore(
    chatContainer,
    document.querySelector(".chat-box")
);


// ==========================================
// SEND MESSAGE
// ==========================================

function sendMessage() {

    const message = input.value.trim();

    // Don't send empty messages
    if (message === "") {
        return;
    }

    // Display user message
    addMessage(message, "user");

    // Clear input
    input.value = "";

    // Generate AI response
    setTimeout(() => {

        const response = getQuantumResponse(message);

        addMessage(response, "ai");

    }, 500);
}


// ==========================================
// ADD MESSAGE TO CHAT
// ==========================================

function addMessage(message, sender) {

    const messageDiv = document.createElement("div");

    messageDiv.classList.add("message", sender);

    // IMPORTANT:
    // textContent prevents HTML from being interpreted
    // as code entered by the user.
    messageDiv.textContent = message;

    chatContainer.appendChild(messageDiv);

    // Automatically scroll to latest message
    chatContainer.scrollTop = chatContainer.scrollHeight;
}


// ==========================================
// ENTER KEY SUPPORT
// ==========================================

input.addEventListener("keydown", function(event) {

    if (event.key === "Enter") {
        sendMessage();
    }

});


// ==========================================
// QUANTUM AI RESPONSES
// ==========================================

function getQuantumResponse(question) {

    const q = question.toLowerCase();


    // Qubit
    if (q.includes("qubit")) {

        return "A qubit is the basic unit of quantum information. Unlike a classical bit, which can be either 0 or 1, a qubit can exist in a superposition of |0⟩ and |1⟩.";
    }


    // Superposition
    if (q.includes("superposition")) {

        return "Superposition means a quantum system can exist in a combination of multiple states at the same time. For a qubit, we can write it as α|0⟩ + β|1⟩.";
    }


    // Entanglement
    if (q.includes("entanglement")) {

        return "Quantum entanglement is a phenomenon where two or more qubits become correlated so that the state of one is related to the state of the other, even when separated.";
    }


    // Quantum gates
    if (
        q.includes("quantum gate") ||
        q.includes("gates")
    ) {

        return "Quantum gates manipulate qubits. Common gates include X, Y, Z, H (Hadamard), S, T and CNOT.";
    }


    // Hadamard
    if (
        q.includes("hadamard") ||
        q.includes("h gate")
    ) {

        return "The Hadamard (H) gate creates superposition. For example, applying H to |0⟩ produces (|0⟩ + |1⟩)/√2.";
    }


    // CNOT
    if (q.includes("cnot")) {

        return "CNOT is a two-qubit controlled-NOT gate. It flips the target qubit when the control qubit is in state |1⟩.";
    }


    // Measurement
    if (q.includes("measurement")) {

        return "Quantum measurement converts a quantum state into a classical result. Measuring a qubit in the computational basis gives either 0 or 1.";
    }


    // Qiskit
    if (q.includes("qiskit")) {

        return "Qiskit is an open-source software framework for working with quantum computers. It allows you to create quantum circuits, simulate them and run them on quantum hardware.";
    }


    // Quantum computer
    if (
        q.includes("quantum computer") ||
        q.includes("quantum computing")
    ) {

        return "Quantum computing uses quantum-mechanical phenomena such as superposition and entanglement to process information using qubits.";
    }


    // Classical vs quantum
    if (
        q.includes("classical") ||
        q.includes("difference")
    ) {

        return "A classical computer uses bits that are either 0 or 1. A quantum computer uses qubits that can exist in superpositions and can also be entangled.";
    }


    // Greeting
    if (
        q.includes("hello") ||
        q.includes("hi") ||
        q.includes("hey")
    ) {

        return "Hello! 👋 I am your Quantum AI Tutor. Ask me about qubits, quantum gates, superposition, entanglement, Qiskit or quantum algorithms.";
    }


    // Default response
    return "I can help you learn quantum computing. Try asking about qubits, superposition, entanglement, quantum gates, Hadamard gates, CNOT, measurement, Qiskit or quantum algorithms.";
}
