function scrollToBottom() {
    const chatHistory = document.getElementById('chatHistory');
    chatHistory.scrollTop = chatHistory.scrollHeight;
}

function appendUserMessage(content) {
    const chatHistory = document.getElementById('chatHistory');
    
    const wrapper = document.createElement('div');
    wrapper.className = 'message-wrapper user-wrapper';
    
    const bubble = document.createElement('div');
    bubble.className = 'message-bubble user-bubble';
    
    const meta = document.createElement('div');
    meta.className = 'message-meta';
    meta.textContent = 'You';
    
    const text = document.createElement('div');
    text.className = 'message-text';
    text.textContent = content;

    bubble.appendChild(meta);
    bubble.appendChild(text);
    wrapper.appendChild(bubble);
    chatHistory.appendChild(wrapper);
}

function appendAssistantMessage(content) {
    const chatHistory = document.getElementById('chatHistory');
    
    const wrapper = document.createElement('div');
    wrapper.className = 'message-wrapper assistant-wrapper';
    
    const bubble = document.createElement('div');
    bubble.className = 'message-bubble assistant-bubble';
    
    const meta = document.createElement('div');
    meta.className = 'message-meta';
    meta.textContent = 'Chatsito';
    
    const text = document.createElement('div');
    text.className = 'message-text';
    text.innerHTML = marked.parse(content);

    bubble.appendChild(meta);
    bubble.appendChild(text);
    wrapper.appendChild(bubble);
    chatHistory.appendChild(wrapper);
}

function appendLoadingIndicator() {
    const chatHistory = document.getElementById('chatHistory');
    const id = 'loader_' + Date.now();

    const wrapper = document.createElement('div');
    wrapper.className = 'loading-wrapper';
    wrapper.id = id;

    const loader = document.createElement('span');
    loader.className = 'hourglass-loader';

    const text = document.createElement('span');
    text.className = 'loading-text';
    text.textContent = 'Chatsito is thinking...';

    wrapper.appendChild(loader);
    wrapper.appendChild(text);
    chatHistory.appendChild(wrapper);

    return id;
}

function appendErrorBanner(message) {
    const chatHistory = document.getElementById('chatHistory');

    const banner = document.createElement('div');
    banner.className = 'error-banner';
    banner.textContent = 'Error: ' + message;

    chatHistory.appendChild(banner);
}
