// University Chatbot Frontend JavaScript
class UniversityChatbot {
    constructor() {
        this.apiBaseUrl = 'http://localhost:8001';
        this.sessionId = this.generateSessionId();
        this.messageCount = 0;
        this.responseTimes = [];
        
        this.initializeElements();
        this.bindEvents();
        this.loadSystemStatus();
        this.startStatusPolling();
    }

    initializeElements() {
        // Chat elements
        this.chatMessages = document.getElementById('chatMessages');
        this.chatInput = document.getElementById('chatInput');
        this.sendButton = document.getElementById('sendMessage');
        this.loadingOverlay = document.getElementById('loadingOverlay');
        
        // Sidebar elements
        this.quickSearch = document.getElementById('quickSearch');
        this.searchBtn = document.getElementById('searchBtn');
        this.apiStatus = document.getElementById('apiStatus');
        this.documentCount = document.getElementById('documentCount');
        this.universityCount = document.getElementById('universityCount');
        this.enhancedFeatures = document.getElementById('enhancedFeatures');
        
        // Modal elements
        this.statsModal = document.getElementById('statsModal');
        this.viewStatsBtn = document.getElementById('viewStats');
        this.closeStatsModal = document.getElementById('closeStatsModal');
        this.clearChatBtn = document.getElementById('clearChat');
        
        // Stats elements
        this.totalDocuments = document.getElementById('totalDocuments');
        this.totalUniversities = document.getElementById('totalUniversities');
        this.totalMessages = document.getElementById('totalMessages');
        this.avgResponseTime = document.getElementById('avgResponseTime');
    }

    bindEvents() {
        // Chat events
        this.sendButton.addEventListener('click', () => this.sendMessage());
        this.chatInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') this.sendMessage();
        });

        // Search events
        this.searchBtn.addEventListener('click', () => this.performSearch());
        this.quickSearch.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') this.performSearch();
        });

        // Suggestion events
        document.querySelectorAll('.suggestion-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                this.chatInput.value = e.target.dataset.query;
                this.sendMessage();
            });
        });

        document.querySelectorAll('.suggestion-item').forEach(item => {
            item.addEventListener('click', (e) => {
                this.chatInput.value = e.currentTarget.dataset.query;
                this.sendMessage();
            });
        });

        // Modal events
        this.viewStatsBtn.addEventListener('click', () => this.showStatsModal());
        this.closeStatsModal.addEventListener('click', () => this.hideStatsModal());
        this.clearChatBtn.addEventListener('click', () => this.clearChat());

        // Close modal when clicking outside
        this.statsModal.addEventListener('click', (e) => {
            if (e.target === this.statsModal) this.hideStatsModal();
        });
    }

    generateSessionId() {
        return 'session_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
    }

    async loadSystemStatus() {
        try {
            // Check enhanced API health
            const healthResponse = await fetch(`${this.apiBaseUrl}/health/enhanced`);
            if (healthResponse.ok) {
                const healthData = await healthResponse.json();
                this.apiStatus.textContent = 'Online';
                this.apiStatus.className = 'status-value online';
                
                // Update enhanced features status
                if (healthData.features) {
                    const enabledFeatures = Object.values(healthData.features).filter(status => status === 'enabled').length;
                    this.enhancedFeatures.textContent = `${enabledFeatures}/4 Active`;
                    this.enhancedFeatures.className = 'status-value online';
                }
            } else {
                // Fallback to basic health check
                const basicHealthResponse = await fetch(`${this.apiBaseUrl}/`);
                if (basicHealthResponse.ok) {
                    this.apiStatus.textContent = 'Online (Basic)';
                    this.apiStatus.className = 'status-value online';
                    this.enhancedFeatures.textContent = 'Not Available';
                    this.enhancedFeatures.className = 'status-value offline';
                } else {
                    this.apiStatus.textContent = 'Offline';
                    this.apiStatus.className = 'status-value offline';
                    this.enhancedFeatures.textContent = 'Offline';
                    this.enhancedFeatures.className = 'status-value offline';
                }
            }

            // Get document and university counts
            await this.updateCounts();
        } catch (error) {
            console.error('Error loading system status:', error);
            this.apiStatus.textContent = 'Offline';
            this.apiStatus.className = 'status-value offline';
            this.enhancedFeatures.textContent = 'Offline';
            this.enhancedFeatures.className = 'status-value offline';
        }
    }

    async updateCounts() {
        try {
            // Get document count
            const searchResponse = await fetch(`${this.apiBaseUrl}/search?query=test&k=1`);
            if (searchResponse.ok) {
                const searchData = await searchResponse.json();
                // This is a workaround - we'll get the actual count from the stats modal
                this.documentCount.textContent = 'Available';
            }

            // Get university count (this would need a separate endpoint)
            this.universityCount.textContent = 'Available';
        } catch (error) {
            console.error('Error updating counts:', error);
            this.documentCount.textContent = 'Error';
            this.universityCount.textContent = 'Error';
        }
    }

    startStatusPolling() {
        // Update system status every 30 seconds
        setInterval(() => this.loadSystemStatus(), 30000);
    }

    async sendMessage() {
        const message = this.chatInput.value.trim();
        if (!message) return;

        const startTime = Date.now();
        this.showLoading();

        // Add user message to chat
        this.addMessage(message, 'user');
        this.chatInput.value = '';

        try {
            const response = await fetch(`${this.apiBaseUrl}/chat`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    question: message,
                    session_id: this.sessionId
                })
            });

            const responseTime = Date.now() - startTime;
            this.responseTimes.push(responseTime);

            if (response.ok) {
                const data = await response.json();
                this.addMessage(data.answer, 'bot', data.sources, data.confidence, data);
                this.messageCount++;
            } else {
                const errorData = await response.json();
                this.addMessage(`Sorry, I encountered an error: ${errorData.detail || 'Unknown error'}`, 'bot');
            }
        } catch (error) {
            console.error('Error sending message:', error);
            this.addMessage('Sorry, I\'m having trouble connecting to the server. Please try again later.', 'bot');
        } finally {
            this.hideLoading();
        }
    }

    async performSearch() {
        const query = this.quickSearch.value.trim();
        if (!query) return;

        this.showLoading();

        try {
            const response = await fetch(`${this.apiBaseUrl}/search?query=${encodeURIComponent(query)}&k=5`);
            
            if (response.ok) {
                const data = await response.json();
                this.displaySearchResults(data.documents, query);
            } else {
                this.addMessage('Sorry, the search failed. Please try again.', 'bot');
            }
        } catch (error) {
            console.error('Error performing search:', error);
            this.addMessage('Sorry, I\'m having trouble with the search. Please try again later.', 'bot');
        } finally {
            this.hideLoading();
        }
    }

    displaySearchResults(documents, query) {
        if (documents.length === 0) {
            this.addMessage(`No documents found for "${query}". Try a different search term.`, 'bot');
            return;
        }

        let message = `Found ${documents.length} documents for "${query}":\n\n`;
        documents.forEach((doc, index) => {
            message += `${index + 1}. **${doc.title}**\n`;
            message += `   Similarity: ${(doc.similarity * 100).toFixed(1)}%\n`;
            message += `   URL: ${doc.source_url}\n\n`;
        });

        this.addMessage(message, 'bot');
    }

    addMessage(text, sender, sources = null, confidence = null, enhancedData = null) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${sender}-message`;

        const avatar = document.createElement('div');
        avatar.className = 'message-avatar';
        avatar.innerHTML = sender === 'user' ? '<i class="fas fa-user"></i>' : '<i class="fas fa-robot"></i>';

        const content = document.createElement('div');
        content.className = 'message-content';

        const messageText = document.createElement('div');
        messageText.className = 'message-text';
        messageText.innerHTML = text;

        const messageTime = document.createElement('div');
        messageTime.className = 'message-time';
        messageTime.textContent = this.formatTime(new Date());

        content.appendChild(messageText);
        content.appendChild(messageTime);

        // Add enhanced features info
        if (enhancedData && sender === 'bot') {
            const enhancedDiv = document.createElement('div');
            enhancedDiv.className = 'message-enhanced';
            
            // Show search queries used
            if (enhancedData.search_queries && enhancedData.search_queries.length > 1) {
                const queriesDiv = document.createElement('div');
                queriesDiv.className = 'search-queries';
                queriesDiv.innerHTML = '<small><strong>🔍 Search queries:</strong><br>';
                enhancedData.search_queries.slice(0, 3).forEach((query, index) => {
                    queriesDiv.innerHTML += `${index + 1}. ${query}<br>`;
                });
                queriesDiv.innerHTML += '</small>';
                enhancedDiv.appendChild(queriesDiv);
            }
            
            // Show retrieval method
            if (enhancedData.retrieval_method) {
                const methodDiv = document.createElement('div');
                methodDiv.className = 'retrieval-method';
                methodDiv.innerHTML = `<small><strong>🔧 Method:</strong> ${enhancedData.retrieval_method}</small>`;
                enhancedDiv.appendChild(methodDiv);
            }
            
            content.appendChild(enhancedDiv);
        }

        // Add sources if available
        if (sources && sources.length > 0) {
            const sourcesDiv = document.createElement('div');
            sourcesDiv.className = 'message-sources';
            sourcesDiv.innerHTML = `<small><strong>📚 Sources:</strong> ${sources.length} documents</small>`;
            
            // Show top source with similarity
            if (sources[0] && sources[0].similarity !== undefined) {
                sourcesDiv.innerHTML += ` (Top: ${(sources[0].similarity * 100).toFixed(1)}%)`;
            }
            
            content.appendChild(sourcesDiv);
        }

        // Add confidence if available
        if (confidence !== null) {
            const confidenceDiv = document.createElement('div');
            confidenceDiv.className = 'message-confidence';
            const confidencePercent = (confidence * 100).toFixed(1);
            const confidenceClass = confidence > 0.7 ? 'high' : confidence > 0.4 ? 'medium' : 'low';
            confidenceDiv.innerHTML = `<small><strong>📊 Confidence:</strong> <span class="confidence-${confidenceClass}">${confidencePercent}%</span></small>`;
            content.appendChild(confidenceDiv);
        }

        messageDiv.appendChild(avatar);
        messageDiv.appendChild(content);

        this.chatMessages.appendChild(messageDiv);
        this.scrollToBottom();
    }

    formatTime(date) {
        return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    }

    scrollToBottom() {
        this.chatMessages.scrollTop = this.chatMessages.scrollHeight;
    }

    showLoading() {
        this.loadingOverlay.classList.remove('hidden');
    }

    hideLoading() {
        this.loadingOverlay.classList.add('hidden');
    }

    clearChat() {
        // Keep only the welcome message
        const welcomeMessage = this.chatMessages.querySelector('.bot-message');
        this.chatMessages.innerHTML = '';
        if (welcomeMessage) {
            this.chatMessages.appendChild(welcomeMessage);
        }
        this.messageCount = 0;
        this.responseTimes = [];
    }

    async showStatsModal() {
        try {
            // Get system statistics
            const healthResponse = await fetch(`${this.apiBaseUrl}/`);
            const searchResponse = await fetch(`${this.apiBaseUrl}/search?query=test&k=1`);
            
            let documentCount = 'N/A';
            let universityCount = 'N/A';
            
            if (searchResponse.ok) {
                const searchData = await searchResponse.json();
                // This is a placeholder - in a real implementation, you'd have a dedicated stats endpoint
                documentCount = '201+'; // Based on your earlier testing
                universityCount = '5'; // Based on your earlier testing
            }

            // Update stats
            this.totalDocuments.textContent = documentCount;
            this.totalUniversities.textContent = universityCount;
            this.totalMessages.textContent = this.messageCount;

            // Calculate average response time
            if (this.responseTimes.length > 0) {
                const avgTime = this.responseTimes.reduce((a, b) => a + b, 0) / this.responseTimes.length;
                this.avgResponseTime.textContent = Math.round(avgTime);
            } else {
                this.avgResponseTime.textContent = 'N/A';
            }

            this.statsModal.classList.remove('hidden');
        } catch (error) {
            console.error('Error loading stats:', error);
            alert('Error loading statistics. Please try again.');
        }
    }

    hideStatsModal() {
        this.statsModal.classList.add('hidden');
    }

    // Utility method to handle API errors
    handleApiError(error, context) {
        console.error(`API Error in ${context}:`, error);
        this.addMessage(`Sorry, I encountered an error while ${context}. Please try again later.`, 'bot');
    }
}

// Initialize the chatbot when the page loads
document.addEventListener('DOMContentLoaded', () => {
    window.chatbot = new UniversityChatbot();
});

// Add some CSS for additional message elements
const additionalStyles = `
    .message-sources, .message-confidence, .message-enhanced {
        margin-top: 0.5rem;
        font-size: 0.8rem;
        opacity: 0.8;
    }
    
    .message-sources small, .message-confidence small, .message-enhanced small {
        color: inherit;
    }
    
    .confidence-high {
        color: #28a745;
        font-weight: 600;
    }
    
    .confidence-medium {
        color: #ffc107;
        font-weight: 600;
    }
    
    .confidence-low {
        color: #dc3545;
        font-weight: 600;
    }
    
    .search-queries {
        background: rgba(211, 47, 47, 0.1);
        padding: 0.5rem;
        border-radius: 8px;
        margin-bottom: 0.5rem;
    }
    
    .retrieval-method {
        background: rgba(211, 47, 47, 0.1);
        padding: 0.25rem 0.5rem;
        border-radius: 4px;
        display: inline-block;
    }
`;

// Inject additional styles
const styleSheet = document.createElement('style');
styleSheet.textContent = additionalStyles;
document.head.appendChild(styleSheet); 