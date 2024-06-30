document.addEventListener('DOMContentLoaded', () => {

    document.getElementById('message-form').addEventListener('submit', function(e) {
        e.preventDefault(); 
        sendMessage();
    });

    function sendMessage() {
        let userMessage = document.getElementById('user-input').value.trim();
        if (userMessage === '') return;

        appendUserMessage(userMessage); 
        document.getElementById('user-input').value = '';

        fetch('/get_response', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: 'user_message=' + encodeURIComponent(userMessage),
        })
        .then(response => response.json())
        .then(data => {
            appendBotMessage(data.response); 
        })
        .catch(error => console.error('Error:', error));
    }

    function appendUserMessage(message) {
        let chatBox = document.getElementById('chat-box');
        let userMessageElement = document.createElement('div');
        userMessageElement.classList.add('user-message');
        userMessageElement.textContent = message;
        chatBox.appendChild(userMessageElement);
    }

    function appendBotMessage(message) {
        let chatBox = document.getElementById('chat-box');
        let botMessageElement = document.createElement('div');
        botMessageElement.classList.add('bot-message');
        botMessageElement.textContent = message;
        chatBox.appendChild(botMessageElement);
    }
});