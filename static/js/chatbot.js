// Chatbot functionality
class Chatbot {
    constructor() {
        this.modal = document.getElementById('chatbot-modal');
        this.messagesContainer = document.getElementById('chatbot-messages');
        this.input = document.getElementById('chatbot-input');
        this.sendButton = document.getElementById('chatbot-send');
        this.closeButton = document.getElementById('close-chatbot');
        this.currentProject = null;
        this.sessionId = this.generateSessionId();

        this.initializeEventListeners();
    }

    generateSessionId() {
        return 'session_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
    }

    initializeEventListeners() {
        // Send message on button click
        this.sendButton.addEventListener('click', () => this.sendMessage());

        // Send message on Enter (Shift+Enter for new line)
        this.input.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });

        // Auto-resize textarea
        this.input.addEventListener('input', () => {
            this.input.style.height = 'auto';
            this.input.style.height = this.input.scrollHeight + 'px';
        });

        // Close chatbot
        this.closeButton.addEventListener('click', () => this.close());

        // Close on backdrop click
        this.modal.addEventListener('click', (e) => {
            if (e.target === this.modal) {
                this.close();
            }
        });

        // Close on Escape key
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && this.modal.classList.contains('active')) {
                this.close();
            }
        });

        // Update project cards to open chatbot
        document.querySelectorAll('.project-card').forEach(card => {
            card.addEventListener('click', (e) => {
                e.preventDefault();
                const projectId = card.getAttribute('href').split('/').pop();
                this.openForProject(projectId);
            });
        });
    }

    async openForProject(projectId) {
        // Fetch project details
        try {
            const response = await fetch('/api/projects');
            const projects = await response.json();
            const project = projects.find(p => p.id === projectId);

            if (project) {
                this.currentProject = project;

                // Update chatbot header
                document.getElementById('chatbot-icon').textContent = project.icon;
                document.getElementById('chatbot-title').textContent = project.name;
                document.getElementById('chatbot-subtitle').textContent = project.description;

                // Clear previous messages except welcome
                const welcomeMsg = this.messagesContainer.querySelector('.welcome-message');
                this.messagesContainer.innerHTML = '';
                if (welcomeMsg) {
                    this.messagesContainer.appendChild(welcomeMsg);
                }

                // Add initial context message
                this.addBotMessage(`I'm ready to help you with ${project.name}. You can ask me to run programs, explain code, or answer questions about this project.`);

                this.open();
            }
        } catch (error) {
            console.error('Error loading project:', error);
        }
    }

    open() {
        this.modal.classList.add('active');
        document.body.style.overflow = 'hidden';

        // Focus on input after animation
        setTimeout(() => {
            this.input.focus();
        }, 300);
    }

    close() {
        this.modal.classList.remove('active');
        document.body.style.overflow = '';
        this.currentProject = null;
    }

    async sendMessage() {
        const message = this.input.value.trim();

        if (!message) return;

        // Add user message to chat
        this.addUserMessage(message);

        // Clear input
        this.input.value = '';
        this.input.style.height = 'auto';

        // Disable send button while processing
        this.sendButton.disabled = true;

        // Show typing indicator
        this.showTypingIndicator();

        try {
            // Send message to backend
            const response = await fetch('/api/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    message: message,
                    project_id: this.currentProject?.id,
                    session_id: this.sessionId
                })
            });

            const data = await response.json();

            // Remove typing indicator
            this.hideTypingIndicator();

            // Add bot response
            if (data.response) {
                this.addBotMessage(data.response);
            }

            // Update session ID if provided
            if (data.session_id) {
                this.sessionId = data.session_id;
            }

            // If there's output from running a program
            if (data.output) {
                this.addBotMessage(`Program output:\n\`\`\`\n${data.output}\n\`\`\``);
            }

        } catch (error) {
            this.hideTypingIndicator();
            this.addBotMessage('Sorry, I encountered an error processing your request. Please try again.');
            console.error('Chat error:', error);
        } finally {
            this.sendButton.disabled = false;
            this.input.focus();
        }
    }

    addUserMessage(text) {
        const messageDiv = document.createElement('div');
        messageDiv.className = 'message user';
        messageDiv.innerHTML = `
            <div class="message-avatar">👤</div>
            <div class="message-content">${this.escapeHtml(text)}</div>
        `;
        this.messagesContainer.appendChild(messageDiv);
        this.scrollToBottom();
    }

    addBotMessage(text) {
        const messageDiv = document.createElement('div');
        messageDiv.className = 'message bot';

        // Parse markdown-style code blocks
        const formattedText = this.formatMessage(text);

        messageDiv.innerHTML = `
            <div class="message-avatar">🤖</div>
            <div class="message-content">${formattedText}</div>
        `;
        this.messagesContainer.appendChild(messageDiv);
        this.scrollToBottom();
    }

    showTypingIndicator() {
        const typingDiv = document.createElement('div');
        typingDiv.className = 'message bot typing-message';
        typingDiv.innerHTML = `
            <div class="message-avatar">🤖</div>
            <div class="message-content">
                <div class="typing-indicator">
                    <div class="typing-dot"></div>
                    <div class="typing-dot"></div>
                    <div class="typing-dot"></div>
                </div>
            </div>
        `;
        this.messagesContainer.appendChild(typingDiv);
        this.scrollToBottom();
    }

    hideTypingIndicator() {
        const typingMessage = this.messagesContainer.querySelector('.typing-message');
        if (typingMessage) {
            typingMessage.remove();
        }
    }

    formatMessage(text) {
        // Convert markdown-style code blocks to HTML
        let formatted = this.escapeHtml(text);

        // Handle code blocks (```code```)
        formatted = formatted.replace(/```([\s\S]*?)```/g, '<pre><code>$1</code></pre>');

        // Handle inline code (`code`)
        formatted = formatted.replace(/`([^`]+)`/g, '<code>$1</code>');

        // Handle line breaks
        formatted = formatted.replace(/\n/g, '<br>');

        return formatted;
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    scrollToBottom() {
        this.messagesContainer.scrollTop = this.messagesContainer.scrollHeight;
    }
}

// Initialize chatbot when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.chatbot = new Chatbot();
});
