/**
 * Smart Water Usage Advisor - AI Conservation Chatbot Drawer Component
 * Location: 4_DEVELOPMENT/frontend/js/components/chatbot.js
 * 
 * Manages the slide-out conversational drawer, message streaming,
 * source citation display, and plumbing safety disclaimers.
 */

export class ChatbotDrawer {
  constructor(apiClient, getActiveUserId) {
    this.apiClient = apiClient;
    this.getActiveUserId = getActiveUserId;
    this.isOpen = false;
    this.backdropEl = document.getElementById("chat-drawer-backdrop");
    this.openBtn = document.getElementById("open-chat-btn");
    this.closeBtn = document.getElementById("btn-close-chat");
    this.messagesEl = document.getElementById("chat-messages");
    this.chatForm = document.getElementById("chat-form");
    this.chatInput = document.getElementById("chat-input");
    this.contextTextEl = document.getElementById("chat-context-text");

    this._initEvents();
  }

  _initEvents() {
    if (this.openBtn) {
      this.openBtn.addEventListener("click", () => this.open());
    }

    if (this.closeBtn) {
      this.closeBtn.addEventListener("click", () => this.close());
    }

    if (this.backdropEl) {
      this.backdropEl.addEventListener("click", (e) => {
        if (e.target === this.backdropEl) this.close();
      });
    }

    document.addEventListener("keydown", (e) => {
      if (e.key === "Escape" && this.isOpen) this.close();
    });

    // Quick prompt pills
    document.querySelectorAll(".prompt-pill").forEach(pill => {
      pill.addEventListener("click", () => {
        const promptText = pill.getAttribute("data-prompt");
        if (promptText) {
          if (!this.isOpen) this.open();
          this.sendMessage(promptText);
        }
      });
    });

    // Form submit
    if (this.chatForm) {
      this.chatForm.addEventListener("submit", (e) => {
        e.preventDefault();
        const text = this.chatInput ? this.chatInput.value.trim() : "";
        if (text) {
          this.sendMessage(text);
          if (this.chatInput) this.chatInput.value = "";
        }
      });
    }
  }

  open() {
    this.isOpen = true;
    if (this.backdropEl) {
      this.backdropEl.classList.add("open");
      this.backdropEl.setAttribute("aria-hidden", "false");
    }
    if (this.openBtn) {
      this.openBtn.setAttribute("aria-expanded", "true");
    }
    setTimeout(() => {
      if (this.chatInput) this.chatInput.focus();
    }, 150);
  }

  close() {
    this.isOpen = false;
    if (this.backdropEl) {
      this.backdropEl.classList.remove("open");
      this.backdropEl.setAttribute("aria-hidden", "true");
    }
    if (this.openBtn) {
      this.openBtn.setAttribute("aria-expanded", "false");
    }
  }

  updateContextText(meterId, profileName) {
    if (this.contextTextEl) {
      this.contextTextEl.textContent = `Grounded in Meter #${meterId} (${profileName}) Telemetry & Models`;
    }
  }

  async sendMessage(userMessage) {
    if (!userMessage || !this.messagesEl) return;

    // 1. Append User Bubble
    const userBubble = document.createElement("div");
    userBubble.className = "chat-bubble user";
    userBubble.textContent = userMessage;
    this.messagesEl.appendChild(userBubble);
    this.scrollToBottom();

    // 2. Append Optimistic Loading Indicator
    const typingBubble = document.createElement("div");
    typingBubble.className = "chat-bubble bot typing-indicator";
    typingBubble.innerHTML = `<em>Thinking & synthesizing water context...</em>`;
    this.messagesEl.appendChild(typingBubble);
    this.scrollToBottom();

    const userId = this.getActiveUserId ? this.getActiveUserId() : 1;

    try {
      const res = await this.apiClient.sendChatMessage(userId, userMessage);
      typingBubble.remove();

      // 3. Render Bot Response Bubble
      const botBubble = document.createElement("div");
      botBubble.className = "chat-bubble bot";

      const answerText = res.answer || res.conversational_response || "I am analyzing your query. Please ask again.";
      let innerHtml = `<p>${this.escapeHtml(answerText)}</p>`;

      // Source Citations
      const evidence = res.evidence || res.source_citations || [];
      if (evidence.length > 0) {
        innerHtml += `<div class="chat-sources">`;
        innerHtml += `<span style="font-size: 0.65rem; color: var(--text-muted); width: 100%;">Sources cited:</span>`;
        evidence.forEach(item => {
          const title = item.title || item.entry_id || "Knowledge Base";
          innerHtml += `<span class="source-chip" title="${this.escapeHtml(item.snippet || "")}">📚 ${this.escapeHtml(title)}</span>`;
        });
        innerHtml += `</div>`;
      }

      // Plumbing Emergency Disclaimer
      const safety = res.safety_disclaimer || res.plumbing_safety_note;
      if (safety) {
        innerHtml += `
          <div class="chat-safety-warning" role="alert">
            <span>🚨</span>
            <div><strong>Safety Advisory:</strong> ${this.escapeHtml(safety)}</div>
          </div>
        `;
      }

      botBubble.innerHTML = innerHtml;
      this.messagesEl.appendChild(botBubble);
      this.scrollToBottom();

    } catch (err) {
      typingBubble.remove();
      const errBubble = document.createElement("div");
      errBubble.className = "chat-bubble bot";
      errBubble.style.borderColor = "var(--status-critical)";
      errBubble.innerHTML = `<p style="color: var(--status-critical);">⚠️ Unable to connect to the local advisor service. Please verify that the server is running.</p>`;
      this.messagesEl.appendChild(errBubble);
      this.scrollToBottom();
    }
  }

  scrollToBottom() {
    if (this.messagesEl) {
      this.messagesEl.scrollTop = this.messagesEl.scrollHeight;
    }
  }

  escapeHtml(str) {
    if (!str) return "";
    const div = document.createElement("div");
    div.textContent = str;
    return div.innerHTML;
  }
}
