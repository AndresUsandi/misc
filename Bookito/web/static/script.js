(function () {
  const form     = document.getElementById('chatForm');
  const input    = document.getElementById('messageInput');
  const chatArea = document.getElementById('chatArea');
  const empty    = document.getElementById('emptyState');

  // Dummy garbage responses
  const garbage = [
    "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.",
    "Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.",
    "Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur.",
    "Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.",
    "Sed ut perspiciatis unde omnis iste natus error sit voluptatem accusantium doloremque laudantium totam rem.",
    "Nemo enim ipsam voluptatem quia voluptas sit aspernatur aut odit aut fugit, sed quia consequuntur magni dolores.",
    "Neque porro quisquam est, qui dolorem ipsum quia dolor sit amet, consectetur, adipisci velit sed quia non numquam.",
    "At vero eos et accusamus et iusto odio dignissimos ducimus qui blanditiis praesentium voluptatum deleniti atque.",
  ];

  let idx = 0;

  function appendMessage(role, text) {
    const row = document.createElement('div');
    row.className = 'message-row ' + role;

    const bubble = document.createElement('div');
    bubble.className = 'message-bubble';
    bubble.textContent = text;

    row.appendChild(bubble);
    chatArea.appendChild(row);
    chatArea.scrollTop = chatArea.scrollHeight;
    return bubble;           // handle typing indicator
  }

  function showTypingIndicators() {
    const row = document.createElement('div');
    row.className = 'message-row bot';
    row.id = 'typingRow';

    const bubble = document.createElement('div');
    bubble.className = 'message-bubble';
    bubble.innerHTML =
      '<span class="typing-dots"><span></span><span></span><span></span></span>';

    row.appendChild(bubble);
    chatArea.appendChild(row);
    chatArea.scrollTop = chatArea.scrollHeight;
  }

  function removeTypingIndicators() {
    const el = document.getElementById('typingRow');
    if (el) el.remove();
  }

  // hide welcome screen on first message
  let hasStarted = false;
  function maybeHideWelcome() {
    if (!hasStarted) {
      empty.classList.add('hidden');
      hasStarted = true;
    }
  }

  input.addEventListener('input', function() {
    this.style.height = 'auto';
    this.style.height = this.scrollHeight + 'px';
  });

  input.addEventListener('keydown', function(e) {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      form.dispatchEvent(new Event('submit', { cancelable: true }));
    }
  });

  form.addEventListener('submit', async function (e) {
    e.preventDefault();
    const text = input.value.trim();
    if (!text) return;

    maybeHideWelcome();
    appendMessage('user', text);
    input.value = '';
    input.style.height = 'auto';

    showTypingIndicators();

    try {
      const res = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: text }),
      });

      removeTypingIndicators();

      if (!res.ok) throw new Error('Network response was not ok');

      const reader = res.body.getReader();
      const decoder = new TextDecoder();
      const botBubble = appendMessage('bot', '');
      let buffer = "";

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        buffer += decoder.decode(value, { stream: true });
        botBubble.innerHTML = marked.parse(buffer);
        chatArea.scrollTop = chatArea.scrollHeight;
      }

    } catch (_) {
      // Fallback when backend isn't running
      removeTypingIndicators();
      setTimeout(function () {
        const dummy = garbage[idx % garbage.length];
        idx++;
        appendMessage('bot', text + '\n\n' + dummy);
      }, 600);
    }

    input.focus();
  });

  input.focus();
})();
