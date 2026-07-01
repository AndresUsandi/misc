function clearChat() {
    vscode.postMessage({
        command: 'clear_chat'
    });
}

function submitOnEnter(event) {
    if (event.key === 'Enter' && !event.shiftKey) {
        event.preventDefault();
        handleChatSubmit(event);
    }
}

function renderHistory(history, activeModel) {
    const chatHistory = document.getElementById('chatHistory');
    chatHistory.innerHTML = '';
    if (history.length === 0) {
        chatHistory.innerHTML = `
            <div class="empty-state" id="emptyState">
                <div class="empty-icon">✦</div>
                <h3>Chatsito for VS Code</h3>
                <p>Start a conversation. The context window will adapt dynamically.</p>
                ${activeModel ? `<p style="font-size: 11px; opacity: 0.7; margin-top: 8px;">Active Model: <code>${activeModel}</code></p>` : ''}
            </div>
        `;
        return;
    }
    history.forEach(msg => {
        if (!msg.role) return;
        const role = msg.role.toLowerCase();
        
        if (role === 'assistant' && msg.tool_calls && msg.tool_calls.length > 0) {
            return;
        }
        
        if (role === 'user') {
            appendUserMessage(msg.displayContent || msg.content);
        } else if (role === 'assistant' && msg.content) {
            appendAssistantMessage(msg.content);
        }
    });
    scrollToBottom();
}

window.addEventListener('DOMContentLoaded', () => {
    const textarea = document.getElementById('promptInput');
    if (textarea) {
        textarea.addEventListener('input', function() {
            this.style.height = 'auto';
            this.style.height = (this.scrollHeight) + 'px';
        });
        textarea.focus();
    }
    
    // Request initial state
    vscode.postMessage({
        command: 'get_session_state'
    });
});

let currentLoaderId = null;

window.addEventListener('message', async (event) => {
    const message = event.data;
    switch (message.command) {
        case 'stateUpdate':
            renderHistory(message.state.conversationHistory, message.state.activeModel);
            const modelSelect = document.getElementById('modelSelect');
            if (modelSelect && message.state.availableModels) {
                const currentSelection = message.state.activeModel;
                modelSelect.innerHTML = '';
                message.state.availableModels.forEach(m => {
                    const opt = document.createElement('option');
                    opt.value = m;
                    opt.textContent = m;
                    if (m === currentSelection) {
                        opt.selected = true;
                    }
                    modelSelect.appendChild(opt);
                });
                if (message.state.availableModels.length === 0) {
                    const opt = document.createElement('option');
                    opt.value = "";
                    opt.textContent = "No models installed";
                    modelSelect.appendChild(opt);
                }
            }
            const modeSelect = document.getElementById('modeSelect');
            if (modeSelect && message.state.selectedMode) {
                modeSelect.value = message.state.selectedMode;
            }
            break;
        case 'progress':
            if (!currentLoaderId) {
                currentLoaderId = appendLoadingIndicator();
            }
            const textNode = document.getElementById(currentLoaderId)?.querySelector('.loading-text');
            if (textNode) {
                textNode.textContent = message.text;
            }
            scrollToBottom();
            break;
        case 'error':
            if (currentLoaderId) {
                const loader = document.getElementById(currentLoaderId);
                if (loader) loader.remove();
                currentLoaderId = null;
            }
            appendErrorBanner(message.message);
            
            const txtAreaErr = document.getElementById('promptInput');
            const btnSendErr = document.getElementById('sendBtn');
            if (txtAreaErr) txtAreaErr.disabled = false;
            if (btnSendErr) btnSendErr.disabled = false;
            if (txtAreaErr) txtAreaErr.focus();
            scrollToBottom();
            break;
        case 'cycleFinished':
            if (currentLoaderId) {
                const loader = document.getElementById(currentLoaderId);
                if (loader) loader.remove();
                currentLoaderId = null;
            }
            
            const txtAreaFin = document.getElementById('promptInput');
            const btnSendFin = document.getElementById('sendBtn');
            if (txtAreaFin) txtAreaFin.disabled = false;
            if (btnSendFin) btnSendFin.disabled = false;
            if (txtAreaFin) txtAreaFin.focus();
            scrollToBottom();
            break;
        case 'exportResult':
            try {
                await navigator.clipboard.writeText(message.json);
                alert("Session JSON exported and copied to clipboard!");
            } catch (err) {
                console.log("Exported JSON:", message.json);
            }
            break;
    }
});

function handleModelChange(val) {
    vscode.postMessage({
        command: 'change_model',
        arguments: {
            model: val
        }
    });
}

function handleModeChange(val) {
    vscode.postMessage({
        command: 'change_mode',
        arguments: {
            mode: val
        }
    });
}

