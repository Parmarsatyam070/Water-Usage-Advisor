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

    // Check authentication state before sending
    if (!this.apiClient.isAuthenticated()) {
      const authBubble = document.createElement("div");
      authBubble.className = "chat-bubble bot";
      authBubble.style.borderLeft = "3px solid var(--accent-amber)";
      authBubble.innerHTML = `
        <p style="color: var(--text-primary); margin-bottom: 0.5rem;">
          🔒 <strong>Authentication Required:</strong> Please log in to consult the AI Water Conservation Advisor.
        </p>
        <button type="button" class="btn-chat-login-action" style="font-size: 0.8rem; padding: 0.35rem 0.75rem; background: var(--accent-cyan); color: #000; font-weight: 600; border: none; border-radius: var(--radius-sm); cursor: pointer;">
          Log In to Chat
        </button>
      `;
      this.messagesEl.appendChild(authBubble);
      const loginBtn = authBubble.querySelector(".btn-chat-login-action");
      if (loginBtn) {
        loginBtn.addEventListener("click", () => {
          if (window.smartWaterApp && window.smartWaterApp.openAuthModal) {
            window.smartWaterApp.openAuthModal();
          }
        });
      }
      this.scrollToBottom();
      return;
    }

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
      const is401 = err.message && err.message.includes("401");
      const errBubble = document.createElement("div");
      errBubble.className = "chat-bubble bot";
      errBubble.style.borderColor = is401 ? "var(--accent-amber)" : "var(--status-critical)";

      if (is401) {
        errBubble.innerHTML = `
          <p style="color: var(--text-primary); margin-bottom: 0.5rem;">
            🔒 <strong>Authentication Required:</strong> Your session has expired or login is required to consult the advisor.
          </p>
          <button type="button" class="btn-chat-login-action" style="font-size: 0.8rem; padding: 0.35rem 0.75rem; background: var(--accent-cyan); color: #000; font-weight: 600; border: none; border-radius: var(--radius-sm); cursor: pointer;">
            Log In Again
          </button>
        `;
        const loginBtn = errBubble.querySelector(".btn-chat-login-action");
        if (loginBtn) {
          loginBtn.addEventListener("click", () => {
            if (window.smartWaterApp && window.smartWaterApp.openAuthModal) {
              window.smartWaterApp.openAuthModal();
            }
          });
        }
      } else {
        errBubble.innerHTML = `<p style="color: var(--status-critical);">⚠️ Unable to connect to the local advisor service. Please verify that the server is running.</p>`;
      }
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
