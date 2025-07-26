// CHATBOT - Calls your Flask backend
document.getElementById("sendBtn").addEventListener("click", sendMessage);
document.getElementById("chatInput").addEventListener("keydown", function (e) {
    if (e.key === "Enter") sendMessage();
});

async function sendMessage() {
    const chatInput = document.getElementById("chatInput");
    const chatBox = document.getElementById("chatBox");
    const msg = chatInput.value.trim();
    if (!msg) return;

    chatBox.innerHTML += `
        <div class="chat-message user-message">
            <div class="message-avatar user-avatar"><i class="fas fa-user"></i></div>
            <div class="message-bubble">${msg}</div>
        </div>
    `;
    chatInput.value = '';
    chatBox.scrollTop = chatBox.scrollHeight;

    try {
        const response = await fetch('/chatbot', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message: msg })
        });
        const data = await response.json();
        chatBox.innerHTML += `
            <div class="chat-message bot-message">
                <div class="message-avatar bot-avatar"><i class="fas fa-robot"></i></div>
                <div class="message-bubble">${data.response}</div>
            </div>
        `;
        chatBox.scrollTop = chatBox.scrollHeight;
    } catch (err) {
        chatBox.innerHTML += `
            <div class="chat-message bot-message">
                <div class="message-avatar bot-avatar"><i class="fas fa-robot"></i></div>
                <div class="message-bubble">Sorry, something went wrong. Please try again later.</div>
            </div>
        `;
        chatBox.scrollTop = chatBox.scrollHeight;
    }
}
