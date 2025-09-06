// University Chatbot Frontend JavaScript
class UniversityChatbot {
    constructor() {
        console.log('UniversityChatbot constructor called');
        
        // API base URL
        // - Local dev: talk to FastAPI on localhost:8001
        // - Production (e.g., Vercel): use relative "/api" and let Vercel rewrite to Railway
        this.apiBaseUrl = window.location.hostname === 'localhost'
            ? 'http://localhost:8001'
            : '/api';
        
        // Check if we should use the fixed API
        this.useFixedAPI = true;
        this.sessionId = this.generateSessionId();
        this.messageCount = 0;
        this.responseTimes = [];
        
        // Ensure DOM is ready before initializing
        if (document.readyState === 'loading') {
            console.log('DOM still loading, waiting...');
            document.addEventListener('DOMContentLoaded', () => {
                this.initializeElements();
                this.bindEvents();
                this.loadSystemStatus();
                this.startStatusPolling();
            });
        } else {
            console.log('DOM already loaded, initializing immediately');
            this.initializeElements();
            this.bindEvents();
            this.loadSystemStatus();
            this.startStatusPolling();
        }
    }

    initializeElements() {
        // Chat elements
        this.chatMessages = document.getElementById('chatMessages');
        this.chatInput = document.getElementById('chatInput');
        this.sendButton = document.getElementById('sendMessage');
        this.loadingOverlay = document.getElementById('loadingOverlay');
        
        // Sidebar elements
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
        
        // Debug logging
        console.log('Elements initialized:');
        console.log('Chat Messages:', this.chatMessages);
        console.log('Chat Input:', this.chatInput);
        console.log('Send Button:', this.sendButton);
        console.log('Loading Overlay:', this.loadingOverlay);
        console.log('API Status:', this.apiStatus);
        console.log('Document Count:', this.documentCount);
        console.log('University Count:', this.universityCount);
        console.log('Enhanced Features:', this.enhancedFeatures);
        console.log('Stats Modal:', this.statsModal);
        console.log('View Stats Button:', this.viewStatsBtn);
        console.log('Close Stats Modal:', this.closeStatsModal);
        console.log('Clear Chat Button:', this.clearChatBtn);
        console.log('Total Documents:', this.totalDocuments);
        console.log('Total Universities:', this.totalUniversities);
        console.log('Total Messages:', this.totalMessages);
        console.log('Avg Response Time:', this.avgResponseTime);
    }

    bindEvents() {
        console.log('Binding events...');
        
        // Chat events
        if (this.sendButton) {
            console.log('Adding event listener to sendButton');
            this.sendButton.addEventListener('click', () => this.sendMessage());
        } else {
            console.error('sendButton not found');
        }
        
        if (this.chatInput) {
            console.log('Adding event listener to chatInput');
            this.chatInput.addEventListener('keypress', (e) => {
                if (e.key === 'Enter') this.sendMessage();
            });
        } else {
            console.error('chatInput not found');
        }

        // Suggestion events - check for both suggestion-btn and suggestion-item classes
        const suggestionBtns = document.querySelectorAll('.suggestion-btn');
        const suggestionItems = document.querySelectorAll('.suggestion-item');
        
        console.log('Found suggestion buttons:', suggestionBtns.length);
        console.log('Found suggestion items:', suggestionItems.length);
        
        // Add event listeners to suggestion buttons
        suggestionBtns.forEach((btn, index) => {
            console.log(`Adding event listener to suggestion button ${index}:`, btn.textContent.trim());
            btn.addEventListener('click', (e) => {
                console.log('Suggestion button clicked:', e.currentTarget.dataset.query);
                if (this.chatInput) {
                    this.chatInput.value = e.currentTarget.dataset.query;
                    console.log('Setting chat input value to:', e.currentTarget.dataset.query);
                    this.sendMessage();
                } else {
                    console.error('Chat input element not found');
                }
            });
        });
        
        // Add event listeners to suggestion items
        suggestionItems.forEach((item, index) => {
            console.log(`Adding event listener to suggestion item ${index}:`, item.textContent.trim());
            item.addEventListener('click', (e) => {
                console.log('Suggestion item clicked:', e.currentTarget.dataset.query);
                if (this.chatInput) {
                    this.chatInput.value = e.currentTarget.dataset.query;
                    console.log('Setting chat input value to:', e.currentTarget.dataset.query);
                    this.sendMessage();
                } else {
                    console.error('Chat input element not found');
                }
            });
        });

        // Modal events
        if (this.viewStatsBtn) {
            console.log('Adding event listener to viewStatsBtn');
            this.viewStatsBtn.addEventListener('click', () => {
                console.log('View Stats button clicked');
                this.showStatsModal();
            });
        } else {
            console.error('viewStatsBtn not found');
        }
        if (this.closeStatsModal) {
            console.log('Adding event listener to closeStatsModal');
            this.closeStatsModal.addEventListener('click', () => {
                console.log('Close Stats Modal button clicked');
                this.hideStatsModal();
            });
        } else {
            console.error('closeStatsModal not found');
        }
        if (this.clearChatBtn) {
            console.log('Adding event listener to clearChatBtn');
            this.clearChatBtn.addEventListener('click', () => {
                console.log('Clear Chat button clicked');
                this.clearChat();
            });
        } else {
            console.error('clearChatBtn not found');
        }

        // Close modal when clicking outside
        if (this.statsModal) {
            this.statsModal.addEventListener('click', (e) => {
                if (e.target === this.statsModal) this.hideStatsModal();
            });
        }
    }

    generateSessionId() {
        return 'session_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
    }

    async loadSystemStatus() {
        try {
            console.log('Loading system status...');
            
            // Check enhanced API health
            const healthResponse = await fetch(`${this.apiBaseUrl}/health/enhanced`);
            console.log('Health response status:', healthResponse.status);
            
            if (healthResponse.ok) {
                const healthData = await healthResponse.json();
                console.log('Health data:', healthData);
                
                if (this.apiStatus) {
                    this.apiStatus.textContent = 'Online';
                    this.apiStatus.className = 'status-value online';
                }
                
                // Update enhanced features status
                if (this.enhancedFeatures) {
                    if (healthData.features && healthData.features.active_features !== undefined) {
                        const activeFeatures = healthData.features.active_features;
                        const totalFeatures = healthData.features.total_features || 4;
                        console.log('Active features count:', activeFeatures);
                        this.enhancedFeatures.textContent = `${activeFeatures}/${totalFeatures} Active`;
                        this.enhancedFeatures.className = activeFeatures > 0 ? 'status-value online' : 'status-value offline';
                    } else {
                        // Fallback to default count
                        console.log('No features data, using fallback');
                        this.enhancedFeatures.textContent = '4/4 Active';
                        this.enhancedFeatures.className = 'status-value online';
                    }
                }
            } else {
                console.log('Enhanced health check failed, trying basic...');
                // Fallback to basic health check
                const basicHealthResponse = await fetch(`${this.apiBaseUrl}/`);
                if (basicHealthResponse.ok) {
                    if (this.apiStatus) {
                        this.apiStatus.textContent = 'Online (Basic)';
                        this.apiStatus.className = 'status-value online';
                    }
                    if (this.enhancedFeatures) {
                        this.enhancedFeatures.textContent = '4/4 Active';
                        this.enhancedFeatures.className = 'status-value online';
                    }
                } else {
                    if (this.apiStatus) {
                        this.apiStatus.textContent = 'Offline';
                        this.apiStatus.className = 'status-value offline';
                    }
                    if (this.enhancedFeatures) {
                        this.enhancedFeatures.textContent = 'Offline';
                        this.enhancedFeatures.className = 'status-value offline';
                    }
                }
            }

            // Get document and university counts
            await this.updateCounts();
        } catch (error) {
            console.error('Error loading system status:', error);
            if (this.apiStatus) {
                this.apiStatus.textContent = 'Offline';
                this.apiStatus.className = 'status-value offline';
            }
            if (this.enhancedFeatures) {
                this.enhancedFeatures.textContent = 'Offline';
                this.enhancedFeatures.className = 'status-value offline';
            }
        }
    }

    async updateCounts() {
        try {
            console.log('Updating counts...');
            
            // Get document count from the documents endpoint
            const documentsResponse = await fetch(`${this.apiBaseUrl}/documents`);
            console.log('Documents response status:', documentsResponse.status);
            
            if (documentsResponse.ok) {
                const documentsData = await documentsResponse.json();
                console.log('Documents data:', documentsData);
                
                if (this.documentCount) {
                    if (documentsData.total_documents) {
                        this.documentCount.textContent = documentsData.total_documents.toLocaleString();
                        console.log('Set document count to:', documentsData.total_documents.toLocaleString());
                    } else {
                        this.documentCount.textContent = '110,086';
                        console.log('No total_documents, using fallback');
                    }
                }
            } else {
                if (this.documentCount) {
                    this.documentCount.textContent = '110,086';
                    console.log('Documents response failed, using fallback');
                }
            }

            // Get university count (Northeastern only)
            if (this.universityCount) {
                this.universityCount.textContent = '1';
                console.log('Set university count to: 1');
            }
        } catch (error) {
            console.error('Error updating counts:', error);
            if (this.documentCount) {
                this.documentCount.textContent = '110,086';
            }
            if (this.universityCount) {
                this.universityCount.textContent = '1';
            }
        }
    }

    startStatusPolling() {
        // Update system status every 30 seconds
        setInterval(() => this.loadSystemStatus(), 30000);
    }

    async sendMessage() {
        if (!this.chatInput) {
            console.error('Chat input element not found');
            return;
        }
        
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
                // Add debug logging
                console.log('Chat response data:', data);
                if (data.sources) {
                    console.log('Source documents:', data.sources);
                }
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



    addMessage(text, sender, sources = null, confidence = null, enhancedData = null) {
        if (!this.chatMessages) {
            console.error('Chat messages element not found');
            return;
        }
        
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${sender}-message`;

        const avatar = document.createElement('div');
        avatar.className = 'message-avatar';
        avatar.innerHTML = sender === 'user' ? '<i class="fas fa-user"></i>' : '<i class="fas fa-robot"></i>';

        const content = document.createElement('div');
        content.className = 'message-content';

        const messageText = document.createElement('div');
        messageText.className = 'message-text';
        let formattedText = text;
        // Add paragraph breaks and bullets for bot responses
        if (sender === 'bot') {
            // Convert newlines to paragraphs
            formattedText = formattedText
                .replace(/\n{2,}/g, '</p><p>') // double newlines to paragraph
                .replace(/\n/g, ' '); // single newlines to space
            // Add <p> tags around the whole thing
            formattedText = '<p>' + formattedText + '</p>';
            // Convert markdown-style bullets to HTML lists
            if (/\n[-*] /.test(text) || /\n\d+\. /.test(text)) {
                // Unordered list
                formattedText = formattedText.replace(/(<p>)([-*] .+?)(<\/p>)/gs, function(_, p1, p2, p3) {
                    const items = p2.split(/[-*] /).filter(Boolean).map(i => `<li>${i.trim()}</li>`).join('');
                    return `<ul style="margin: 0.5em 0 1em 2em;">${items}</ul>`;
                });
                // Ordered list
                formattedText = formattedText.replace(/(<p>)(\d+\. .+?)(<\/p>)/gs, function(_, p1, p2, p3) {
                    const items = p2.split(/\d+\. /).filter(Boolean).map(i => `<li>${i.trim()}</li>`).join('');
                    return `<ol style="margin: 0.5em 0 1em 2em;">${items}</ol>`;
                });
            }
        }
        messageText.innerHTML = formattedText;
        // Beautify bot response content
        if (sender === 'bot') {
            messageText.style.background = 'rgba(235, 243, 255, 0.98)';
            messageText.style.border = '1px solid #d0e3fa';
            messageText.style.borderLeft = '6px solid #4a90e2';
            messageText.style.borderRadius = '10px';
            messageText.style.padding = '1.3em 1.7em';
            messageText.style.marginBottom = '0.9em';
            messageText.style.fontSize = '1.13em';
            messageText.style.lineHeight = '1.85';
            messageText.style.color = '#1a2633';
            messageText.style.fontFamily = 'Segoe UI, Arial, sans-serif';
            messageText.style.boxShadow = '0 2px 12px rgba(74,144,226,0.07)';
        }

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
            sourcesDiv.innerHTML = `<strong>📚 All Source Documents (${sources.length} total):</strong>`;

            const sourcesList = document.createElement('ol');
            sourcesList.className = 'sources-list';

            sources.forEach((source, index) => {
                const item = document.createElement('li');
                const title = source.title || source.file_name || 'Untitled Document';
                const fileName = source.file_name ? ` <span class="file-name">(${source.file_name})</span>` : '';
                
                // Handle relevance score - backend sends it as a string with "%" or as a number
                let relevanceDisplay = 'N/A';
                if (source.relevance) {
                    // If it's already a string with %, use it directly
                    if (typeof source.relevance === 'string' && source.relevance.includes('%')) {
                        relevanceDisplay = source.relevance;
                    } else if (typeof source.relevance === 'number') {
                        relevanceDisplay = `${source.relevance.toFixed(1)}%`;
                    } else if (typeof source.relevance === 'string') {
                        // Try to parse as number
                        const num = parseFloat(source.relevance);
                        if (!isNaN(num)) {
                            relevanceDisplay = `${num.toFixed(1)}%`;
                        } else {
                            relevanceDisplay = source.relevance;
                        }
                    }
                } else if (source.similarity) {
                    // Fallback to similarity if relevance not available
                    const similarity = (source.similarity * 100).toFixed(1);
                    relevanceDisplay = `${similarity}%`;
                }
                
                // Handle URL display and validation
                let urlDisplay = '';
                if (source.url && source.url.trim()) {
                    // Ensure URL is properly formatted
                    let url = source.url.trim();
                    if (!url.startsWith('http://') && !url.startsWith('https://')) {
                        url = 'https://' + url;
                    }
                    
                    // Create clickable link with proper styling
                    urlDisplay = `<a href="${url}" target="_blank" rel="noopener noreferrer" class="source-link" style="color: #4a90e2; text-decoration: none; font-weight: 500; padding: 4px 8px; border: 1px solid #4a90e2; border-radius: 4px; background: rgba(74, 144, 226, 0.1); transition: all 0.2s ease;">🌐 Visit Website</a>`;
                } else {
                    urlDisplay = '<span style="color: #999; font-style: italic;">No URL available</span>';
                }
                
                item.innerHTML = `
                    <div style="margin-bottom: 0.5em; padding: 8px; border-left: 3px solid #4a90e2; background: rgba(74, 144, 226, 0.05); border-radius: 4px;">
                        <div style="margin-bottom: 0.3em; font-weight: 600; color: #2c3e50;">
                            ${index + 1}. ${title}${fileName}
                        </div>
                        <div style="font-size: 0.9em; margin-bottom: 0.3em; color: #7f8c8d;">
                            <span class="similarity-score"><strong>Relevance:</strong> <span style="color: #e74c3c; font-weight: 600;">${relevanceDisplay}</span></span>
                        </div>
                        <div style="font-size: 0.9em;">
                            ${urlDisplay}
                        </div>
                    </div>
                `;
                sourcesList.appendChild(item);
            });

            sourcesDiv.appendChild(sourcesList);
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
        if (this.chatMessages) {
            this.chatMessages.scrollTop = this.chatMessages.scrollHeight;
        }
    }

    showLoading() {
        if (this.loadingOverlay) {
            this.loadingOverlay.classList.remove('hidden');
        }
    }

    hideLoading() {
        if (this.loadingOverlay) {
            this.loadingOverlay.classList.add('hidden');
        }
    }

    clearChat() {
        console.log('clearChat called');
        if (!this.chatMessages) {
            console.error('Chat messages element not found');
            return;
        }
        
        console.log('Clearing chat messages');
        // Keep only the welcome message
        const welcomeMessage = this.chatMessages.querySelector('.bot-message');
        this.chatMessages.innerHTML = '';
        if (welcomeMessage) {
            this.chatMessages.appendChild(welcomeMessage);
        }
        this.messageCount = 0;
        this.responseTimes = [];
        console.log('Chat cleared successfully');
    }

    async showStatsModal() {
        console.log('showStatsModal called');
        console.log('Stats modal elements:', {
            statsModal: this.statsModal,
            totalDocuments: this.totalDocuments,
            totalUniversities: this.totalUniversities,
            totalMessages: this.totalMessages,
            avgResponseTime: this.avgResponseTime
        });
        
        if (!this.statsModal || !this.totalDocuments || !this.totalUniversities || !this.totalMessages || !this.avgResponseTime) {
            console.error('Stats modal elements not found');
            return;
        }
        
        try {
            // Get system statistics from the documents endpoint
            const documentsResponse = await fetch(`${this.apiBaseUrl}/documents`);
            
            let documentCount = '110,086';
            let universityCount = '1';
            
            if (documentsResponse.ok) {
                const documentsData = await documentsResponse.json();
                console.log('Documents data for stats:', documentsData);
                if (documentsData.total_documents) {
                    documentCount = documentsData.total_documents.toLocaleString();
                }
                if (documentsData.total_universities) {
                    universityCount = documentsData.total_universities.toString();
                }
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

            console.log('Showing stats modal');
            this.statsModal.classList.remove('hidden');
        } catch (error) {
            console.error('Error loading stats:', error);
            alert('Error loading statistics. Please try again.');
        }
    }

    hideStatsModal() {
        if (this.statsModal) {
            this.statsModal.classList.add('hidden');
        }
    }

    // Utility method to handle API errors
    handleApiError(error, context) {
        console.error(`API Error in ${context}:`, error);
        this.addMessage(`Sorry, I encountered an error while ${context}. Please try again later.`, 'bot');
    }
}

// Initialize the chatbot when the page loads
function initializeChatbot() {
    try {
        console.log('Initializing chatbot...');
        window.chatbot = new UniversityChatbot();
        console.log('Chatbot initialized successfully');
    } catch (error) {
        console.error('Error initializing chatbot:', error);
        // Retry after a short delay
        setTimeout(() => {
            console.log('Retrying chatbot initialization...');
            try {
                window.chatbot = new UniversityChatbot();
                console.log('Chatbot initialized successfully on retry');
            } catch (retryError) {
                console.error('Failed to initialize chatbot on retry:', retryError);
            }
        }, 100);
    }
}

// Try multiple initialization methods
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initializeChatbot);
} else {
    // DOM is already loaded
    initializeChatbot();
}

// Fallback initialization
window.addEventListener('load', () => {
    if (!window.chatbot) {
        console.log('Fallback initialization...');
        initializeChatbot();
    }
});

// Add some CSS for additional message elements
const additionalStyles = `
    .message-sources {
        margin-top: 1rem;
        font-size: 0.9rem;
        background: rgba(0, 0, 0, 0.03);
        padding: 1rem;
        border-radius: 8px;
        border: 1px solid rgba(0, 0, 0, 0.1);
    }
    
    .sources-list {
        list-style: decimal;
        margin: 0.5rem 0 0 1.5rem;
        padding: 0;
    }
    
    .sources-list li {
        margin-bottom: 0.5rem;
        padding: 0.5rem;
        background: white;
        border-radius: 4px;
        border: 1px solid rgba(0, 0, 0, 0.05);
    }
    
    .similarity-score {
        color: #2196F3;
        margin: 0 0.5rem;
    }
    
    .file-name {
        color: #4CAF50;
        margin-left: 0.5rem;
        font-family: monospace;
    }
    
    .message-sources a {
        color: #1976D2;
        text-decoration: none;
        margin-left: 0.5rem;
    }
    
    .message-sources a:hover {
        text-decoration: underline;
    }
    
    .message-confidence, .message-enhanced {
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
    
    /* Enhanced Source Display Styles */
    .sources-header {
        margin-bottom: 0.5rem;
        font-weight: 600;
    }
    
    .sources-list {
        display: flex;
        flex-direction: column;
        gap: 0.5rem;
    }
    
    .source-item {
        background: rgba(0, 123, 255, 0.05);
        border: 1px solid rgba(0, 123, 255, 0.1);
        border-radius: 8px;
        padding: 0.75rem;
        transition: all 0.2s ease;
        position: relative;
    }
    
    .source-item:hover {
        background: rgba(0, 123, 255, 0.08);
        border-color: rgba(0, 123, 255, 0.2);
        transform: translateY(-1px);
    }
    
    .top-source {
        background: rgba(40, 167, 69, 0.08);
        border: 2px solid rgba(40, 167, 69, 0.3);
        box-shadow: 0 2px 8px rgba(40, 167, 69, 0.1);
    }
`;

// Inject additional styles
const styleSheet = document.createElement('style');
styleSheet.textContent = additionalStyles;
document.head.appendChild(styleSheet); 