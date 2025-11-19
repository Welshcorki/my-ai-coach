document.addEventListener("DOMContentLoaded", () => {
    const chatForm = document.getElementById("chat-form");
    const messageInput = document.getElementById("message-input");
    const chatBox = document.getElementById("chat-box");

    chatForm.addEventListener("submit", async (e) => {
        e.preventDefault();

        const userMessage = messageInput.value.trim();
        if (!userMessage) {
            return;
        }

        // Display user's message
        addMessage(userMessage, "user");

        // Clear the input
        messageInput.value = "";

        try {
            // Send message to the backend
            const response = await fetch("/api/v1/chat", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({ content: userMessage, sender: "user" }),
            });

            if (!response.ok) {
                throw new Error("Network response was not ok");
            }

            const aiMessage = await response.json();

            // Display AI's response
            addMessage(aiMessage.content, "ai");

        } catch (error) {
            console.error("Error during chat:", error);
            addMessage("Sorry, something went wrong. Please try again.", "ai");
        }
    });

    function addMessage(content, sender) {
        const messageElement = document.createElement("div");
        messageElement.classList.add("message", sender);
        messageElement.textContent = content;
        chatBox.appendChild(messageElement);
        chatBox.scrollTop = chatBox.scrollHeight; // Auto-scroll to the bottom
    }

    console.log("main.js loaded and chat initialized");
});
