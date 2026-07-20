const vscode = acquireVsCodeApi();

function logDebug(msg, data) {
    console.log(msg, data || '');
    vscode.postMessage({
        command: 'log_debug',
        message: msg + (data ? " " + (typeof data === 'string' ? data : JSON.stringify(data)) : "")
    });
}

function handleChatSubmit(event) {
    event.preventDefault();

    const textarea = document.getElementById('promptInput');
    const promptText = textarea.value.trim();
    if (!promptText) return;

    textarea.value = '';
    textarea.style.height = 'auto';

    const sendBtn = document.getElementById('sendBtn');
    textarea.disabled = true;
    sendBtn.disabled = true;

    logDebug("[Chatsito Webview] User submitted prompt");

    // Send the prompt to the host
    vscode.postMessage({
        command: 'submit_prompt',
        arguments: {
            prompt: promptText
        }
    });
}

