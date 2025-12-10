// Chatbot functionality for project detail page
(function() {
    'use strict';

    // Get DOM elements
    const chatInput = document.getElementById('chatbot-input');
    const chatSend = document.getElementById('chatbot-send');
    const chatMessages = document.getElementById('chatbot-messages');
    const sidebarToggle = document.getElementById('sidebar-toggle');
    const chatSidebar = document.getElementById('chat-sidebar');
    const newChatBtn = document.getElementById('new-chat-btn');
    const sidebarConversations = document.getElementById('sidebar-conversations');

    // Get project data from window
    const projectData = window.projectData || {};

    // Session management
    let currentSessionId = null;
    let messageHistory = [];
    let isWaitingForResponse = false;
    let conversations = [];
    let deleteModal = null;
    let pendingDeleteConversation = null;

    // Create delete confirmation modal
    function createDeleteModal() {
        const modalHTML = `
            <div class="delete-modal-overlay" id="delete-modal-overlay">
                <div class="delete-modal">
                    <div class="delete-modal-header">
                        <div class="delete-modal-icon">⚠️</div>
                        <div class="delete-modal-title">Delete Conversation</div>
                    </div>
                    <div class="delete-modal-body">
                        Are you sure you want to delete <span class="delete-modal-conversation-name" id="delete-modal-conversation-name"></span>? This action cannot be undone.
                    </div>
                    <div class="delete-modal-actions">
                        <button class="delete-modal-btn delete-modal-btn-cancel" id="delete-modal-cancel">Cancel</button>
                        <button class="delete-modal-btn delete-modal-btn-delete" id="delete-modal-confirm">Delete</button>
                    </div>
                </div>
            </div>
        `;

        document.body.insertAdjacentHTML('beforeend', modalHTML);
        deleteModal = document.getElementById('delete-modal-overlay');

        // Close modal on overlay click
        deleteModal.addEventListener('click', function(e) {
            if (e.target === deleteModal) {
                closeDeleteModal();
            }
        });

        // Cancel button
        document.getElementById('delete-modal-cancel').addEventListener('click', closeDeleteModal);

        // Confirm button
        document.getElementById('delete-modal-confirm').addEventListener('click', confirmDelete);

        // Close on Escape key
        document.addEventListener('keydown', function(e) {
            if (e.key === 'Escape' && deleteModal.classList.contains('active')) {
                closeDeleteModal();
            }
        });
    }

    // Show delete modal
    function showDeleteModal(conversationId, conversationTitle) {
        pendingDeleteConversation = conversationId;
        document.getElementById('delete-modal-conversation-name').textContent = `"${conversationTitle}"`;
        deleteModal.classList.add('active');
    }

    // Close delete modal
    function closeDeleteModal() {
        deleteModal.classList.remove('active');
        pendingDeleteConversation = null;
    }

    // Confirm delete
    async function confirmDelete() {
        if (pendingDeleteConversation) {
            await performDelete(pendingDeleteConversation);
            closeDeleteModal();
        }
    }

    // Initialize chatbot
    async function init() {
        // Create delete modal
        createDeleteModal();
        // Auto-resize textarea
        chatInput.addEventListener('input', autoResize);

        // Send message on button click
        chatSend.addEventListener('click', sendMessage);

        // Send message on Enter (Shift+Enter for new line)
        chatInput.addEventListener('keydown', function(e) {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                sendMessage();
            }
        });

        // Sidebar toggle
        sidebarToggle.addEventListener('click', function() {
            chatSidebar.classList.toggle('collapsed');
        });

        // New chat button
        newChatBtn.addEventListener('click', startNewChat);

        // Load conversations from database
        await loadConversations();

        // If no conversations exist, create a default one
        if (conversations.length === 0) {
            await createNewConversation('default', 'New Conversation');
        } else {
            // Load the most recent conversation
            currentSessionId = conversations[0].id;
            await loadConversationMessages(currentSessionId);
        }

        // Update sidebar
        updateSidebar();

        // Focus input on load
        chatInput.focus();
    }

    // Load conversations from database
    async function loadConversations() {
        try {
            const response = await fetch(`/api/conversations/${projectData.id}`);
            if (response.ok) {
                conversations = await response.json();
            }
        } catch (error) {
            console.error('Error loading conversations:', error);
        }
    }

    // Load messages for a conversation
    async function loadConversationMessages(conversationId) {
        try {
            const response = await fetch(`/api/conversations/${conversationId}/messages`);
            if (response.ok) {
                const messages = await response.json();

                // Clear current messages
                chatMessages.innerHTML = '';
                messageHistory = [];

                // Add messages to UI
                messages.forEach(msg => {
                    addMessage(msg.role, msg.content, false); // false = don't save to DB
                    messageHistory.push({ role: msg.role, content: msg.content });
                });

                // If no messages, show welcome
                if (messages.length === 0) {
                    showWelcomeMessage();
                }
            }
        } catch (error) {
            console.error('Error loading messages:', error);
            showWelcomeMessage();
        }
    }

    // Create a new conversation
    async function createNewConversation(id, title) {
        try {
            const response = await fetch('/api/conversations', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    id: id,
                    project_id: projectData.id,
                    title: title
                })
            });

            if (response.ok) {
                const result = await response.json();
                currentSessionId = result.id;

                // Add to local conversations array
                conversations.unshift({
                    id: result.id,
                    title: title,
                    preview: 'No messages yet',
                    created_at: new Date().toISOString(),
                    updated_at: new Date().toISOString()
                });

                return result.id;
            }
        } catch (error) {
            console.error('Error creating conversation:', error);
        }
    }

    // Save message to database
    async function saveMessage(role, content) {
        if (!currentSessionId) return;

        try {
            await fetch(`/api/conversations/${currentSessionId}/messages`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    role: role,
                    content: content
                })
            });
        } catch (error) {
            console.error('Error saving message:', error);
        }
    }

    // Delete conversation - show modal
    function deleteConversation(conversationId, conversationTitle, event) {
        event.stopPropagation(); // Prevent switching to conversation
        showDeleteModal(conversationId, conversationTitle);
    }

    // Perform the actual delete operation
    async function performDelete(conversationId) {
        try {
            const response = await fetch(`/api/conversations/${conversationId}`, {
                method: 'DELETE'
            });

            if (response.ok) {
                // Remove from local array
                conversations = conversations.filter(c => c.id !== conversationId);

                // If we deleted the current conversation, switch to another or create new
                if (conversationId === currentSessionId) {
                    if (conversations.length > 0) {
                        await switchConversation(conversations[0].id);
                    } else {
                        await startNewChat();
                    }
                }

                updateSidebar();
            }
        } catch (error) {
            console.error('Error deleting conversation:', error);
            // Show error in modal or alert
            alert('Failed to delete conversation');
        }
    }

    // Update sidebar with conversations
    function updateSidebar() {
        if (!sidebarConversations) return;

        sidebarConversations.innerHTML = '';

        conversations.forEach(conversation => {
            const convItem = document.createElement('div');
            convItem.className = 'conversation-item' + (conversation.id === currentSessionId ? ' active' : '');
            convItem.dataset.sessionId = conversation.id;

            convItem.innerHTML = `
                <div class="conversation-icon">💬</div>
                <div class="conversation-details">
                    <div class="conversation-title">${conversation.title}</div>
                    <div class="conversation-preview">${conversation.preview || 'No messages yet'}</div>
                </div>
                <button class="conversation-delete" title="Delete conversation">🗑️</button>
            `;

            // Click on conversation to switch
            convItem.addEventListener('click', function(e) {
                if (!e.target.classList.contains('conversation-delete')) {
                    switchConversation(conversation.id);
                }
            });

            // Delete button
            const deleteBtn = convItem.querySelector('.conversation-delete');
            deleteBtn.addEventListener('click', function(e) {
                deleteConversation(conversation.id, conversation.title, e);
            });

            sidebarConversations.appendChild(convItem);
        });
    }

    // Switch to a different conversation
    async function switchConversation(sessionId) {
        if (sessionId === currentSessionId) return;

        currentSessionId = sessionId;
        messageHistory = [];

        // Load conversation messages
        await loadConversationMessages(sessionId);

        // Update sidebar to show active conversation
        updateSidebar();

        // Focus input
        chatInput.focus();
    }

    // Update conversation preview
    function updateConversationPreview(sessionId, preview) {
        const conversation = conversations.find(c => c.id === sessionId);
        if (conversation) {
            conversation.preview = preview.substring(0, 50) + (preview.length > 50 ? '...' : '');
            conversation.updated_at = new Date().toISOString();
            updateSidebar();
        }
    }

    // Update conversation title
    async function updateConversationTitle(sessionId, title) {
        try {
            const response = await fetch(`/api/conversations/${sessionId}/title`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    title: title
                })
            });

            if (response.ok) {
                const conversation = conversations.find(c => c.id === sessionId);
                if (conversation) {
                    conversation.title = title;
                    updateSidebar();
                }
            }
        } catch (error) {
            console.error('Error updating conversation title:', error);
        }
    }

    // Show welcome message
    function showWelcomeMessage() {
        const welcomeHTML = `
            <div class="welcome-message-container">
                <div class="welcome-project-icon">${projectData.icon}</div>
                <h1 class="welcome-project-title">${projectData.name}</h1>
                <p class="welcome-project-description">${projectData.description}</p>
                <div class="welcome-divider"></div>
                <p class="welcome-instructions">I'm your AI assistant for this project. How can I help you today?</p>
            </div>
        `;
        chatMessages.innerHTML = welcomeHTML;
    }

    // Auto-resize textarea
    function autoResize() {
        this.style.height = 'auto';
        this.style.height = Math.min(this.scrollHeight, 200) + 'px';
    }

    // Send message
    async function sendMessage() {
        const message = chatInput.value.trim();

        if (!message || isWaitingForResponse) {
            return;
        }

        // Disable input while waiting
        isWaitingForResponse = true;
        chatInput.disabled = true;
        chatSend.disabled = true;

        // Remove welcome message if present
        const welcomeContainer = chatMessages.querySelector('.welcome-message-container');
        if (welcomeContainer) {
            welcomeContainer.remove();
        }

        // Add user message to UI and save to database
        addMessage('user', message, true);
        messageHistory.push({ role: 'user', content: message });

        // Clear input
        chatInput.value = '';
        chatInput.style.height = 'auto';

        // Add typing indicator
        const typingId = addTypingIndicator();

        try {
            // Send to backend
            const response = await fetch('/api/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    message: message,
                    project_id: projectData.id,
                    session_id: currentSessionId
                })
            });

            const data = await response.json();

            // Remove typing indicator
            removeTypingIndicator(typingId);

            // Add assistant response
            const responseText = data.response || 'No response received';
            addMessage('assistant', responseText, true);
            messageHistory.push({ role: 'assistant', content: responseText });

            // Update conversation preview
            updateConversationPreview(currentSessionId, message);

            // Update conversation title with first assistant response (if this is the first message)
            const conversation = conversations.find(c => c.id === currentSessionId);
            if (conversation && conversation.title === 'New Conversation' && messageHistory.length === 2) {
                // Extract first line or sentence from the response as title
                let newTitle = responseText.split('\n')[0]; // Get first line

                // Strip markdown formatting
                newTitle = newTitle
                    .replace(/[*_~`#]/g, '') // Remove markdown symbols
                    .replace(/\[([^\]]+)\]\([^\)]+\)/g, '$1') // Convert links to text
                    .replace(/!\[([^\]]*)\]\([^\)]+\)/g, '$1') // Convert images to alt text
                    .trim();

                // If first line is too long, truncate it
                if (newTitle.length > 50) {
                    newTitle = newTitle.substring(0, 47) + '...';
                }
                await updateConversationTitle(currentSessionId, newTitle);
            }

            // Re-enable input
            isWaitingForResponse = false;
            chatInput.disabled = false;
            chatSend.disabled = false;
            chatInput.focus();

        } catch (error) {
            // Remove typing indicator
            removeTypingIndicator(typingId);

            // Show error message
            addMessage('assistant', 'Sorry, there was an error processing your request. Please try again.', false);
            console.error('Chat error:', error);

            // Re-enable input
            isWaitingForResponse = false;
            chatInput.disabled = false;
            chatSend.disabled = false;
            chatInput.focus();
        }
    }

    // Add message to chat
    function addMessage(role, content, saveToDb = true) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `chat-message ${role}-message`;

        const avatarDiv = document.createElement('div');
        avatarDiv.className = 'message-avatar';
        avatarDiv.textContent = role === 'user' ? '👤' : projectData.icon || '🤖';

        const contentDiv = document.createElement('div');
        contentDiv.className = 'message-content';

        // Parse markdown if marked is available
        if (typeof marked !== 'undefined') {
            contentDiv.innerHTML = marked.parse(content);
        } else {
            contentDiv.textContent = content;
        }

        messageDiv.appendChild(avatarDiv);
        messageDiv.appendChild(contentDiv);
        chatMessages.appendChild(messageDiv);

        // Scroll behavior based on role
        if (role === 'user') {
            // For user messages, scroll to bottom
            chatMessages.scrollTop = chatMessages.scrollHeight;
        } else if (role === 'assistant') {
            // For assistant messages, scroll to show the top of the new message
            messageDiv.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }

        // Save to database
        if (saveToDb) {
            saveMessage(role, content);
        }
    }

    // Add typing indicator
    function addTypingIndicator() {
        const typingDiv = document.createElement('div');
        typingDiv.className = 'chat-message assistant-message typing-indicator';
        typingDiv.id = 'typing-' + Date.now();

        const avatarDiv = document.createElement('div');
        avatarDiv.className = 'message-avatar';
        avatarDiv.textContent = projectData.icon || '🤖';

        const contentDiv = document.createElement('div');
        contentDiv.className = 'message-content';
        contentDiv.innerHTML = '<div class="typing-dots"><span></span><span></span><span></span></div>';

        typingDiv.appendChild(avatarDiv);
        typingDiv.appendChild(contentDiv);
        chatMessages.appendChild(typingDiv);

        // Scroll to bottom
        chatMessages.scrollTop = chatMessages.scrollHeight;

        return typingDiv.id;
    }

    // Remove typing indicator
    function removeTypingIndicator(id) {
        const typingDiv = document.getElementById(id);
        if (typingDiv) {
            typingDiv.remove();
        }
    }

    // Start new chat
    async function startNewChat() {
        // Generate new session ID
        const newSessionId = 'session-' + Date.now();

        // Create conversation in database
        await createNewConversation(newSessionId, 'New Conversation');

        // Clear messages
        messageHistory = [];
        chatMessages.innerHTML = '';

        // Show welcome message
        showWelcomeMessage();

        // Update sidebar
        updateSidebar();

        // Focus input
        chatInput.focus();
    }

    // Initialize on DOM ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();
