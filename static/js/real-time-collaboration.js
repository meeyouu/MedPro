/**
 * Real-time Collaboration Notes for Lab Technicians
 * Live commenting, annotations, and team communication on test results
 */

class RealTimeCollaboration {
    constructor() {
        this.currentUser = null;
        this.activeUsers = new Map();
        this.comments = new Map();
        this.annotations = new Map();
        this.isConnected = false;
        this.init();
    }

    init() {
        this.getCurrentUser();
        this.createCollaborationPanel();
        this.setupEventListeners();
        this.initializePresence();
    }

    getCurrentUser() {
        // In a real implementation, this would get the current user from session
        this.currentUser = {
            id: 'user_' + Math.random().toString(36).substr(2, 9),
            name: 'Current User',
            role: 'Lab Technician',
            avatar: '/static/img/default-avatar.png',
            color: this.generateUserColor()
        };
    }

    generateUserColor() {
        const colors = ['#3B82F6', '#10B981', '#8B5CF6', '#F59E0B', '#EF4444', '#06B6D4'];
        return colors[Math.floor(Math.random() * colors.length)];
    }

    createCollaborationPanel() {
        if (document.getElementById('collaborationPanel')) return;

        const panel = document.createElement('div');
        panel.id = 'collaborationPanel';
        panel.className = 'hidden fixed bottom-4 right-4 w-80 bg-white dark:bg-gray-800 rounded-xl shadow-2xl border border-gray-200 dark:border-gray-700 z-40 max-h-96 overflow-hidden';
        
        panel.innerHTML = `
            <!-- Header -->
            <div class="bg-gradient-to-r from-green-600 to-blue-600 text-white p-4">
                <div class="flex items-center justify-between">
                    <div>
                        <h3 class="font-semibold text-sm">Team Collaboration</h3>
                        <p class="text-xs text-green-100" id="connectionStatus">Connecting...</p>
                    </div>
                    <div class="flex items-center space-x-2">
                        <div id="activeUsersIndicator" class="flex -space-x-2">
                            <!-- Active users will be shown here -->
                        </div>
                        <button onclick="realTimeCollaboration.toggle()" class="text-white hover:text-gray-200">
                            <i class="fas fa-minus text-sm"></i>
                        </button>
                    </div>
                </div>
            </div>

            <!-- Tabs -->
            <div class="border-b border-gray-200 dark:border-gray-600">
                <nav class="flex">
                    <button id="commentsTab" onclick="realTimeCollaboration.switchTab('comments')" 
                            class="flex-1 py-2 px-4 text-sm font-medium text-blue-600 border-b-2 border-blue-600 bg-blue-50 dark:bg-blue-900/20">
                        Comments
                    </button>
                    <button id="annotationsTab" onclick="realTimeCollaboration.switchTab('annotations')" 
                            class="flex-1 py-2 px-4 text-sm font-medium text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-200">
                        Annotations
                    </button>
                    <button id="activityTab" onclick="realTimeCollaboration.switchTab('activity')" 
                            class="flex-1 py-2 px-4 text-sm font-medium text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-200">
                        Activity
                    </button>
                </nav>
            </div>

            <!-- Content -->
            <div id="collaborationContent" class="h-64 overflow-y-auto">
                <!-- Comments Tab -->
                <div id="commentsContent" class="p-4 space-y-3">
                    <div id="commentsList">
                        <div class="text-center py-8 text-gray-500 dark:text-gray-400 text-sm">
                            No comments yet. Start a discussion!
                        </div>
                    </div>
                    <div class="border-t border-gray-200 dark:border-gray-600 pt-3">
                        <div class="flex space-x-2">
                            <input type="text" id="commentInput" placeholder="Add a comment..." 
                                   class="flex-1 px-3 py-2 text-sm border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
                                   onkeypress="realTimeCollaboration.handleCommentKeyPress(event)">
                            <button onclick="realTimeCollaboration.addComment()" 
                                    class="px-3 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 text-sm">
                                <i class="fas fa-paper-plane"></i>
                            </button>
                        </div>
                    </div>
                </div>

                <!-- Annotations Tab -->
                <div id="annotationsContent" class="hidden p-4 space-y-3">
                    <div class="text-sm text-gray-600 dark:text-gray-400 mb-3">
                        Click on test results to add annotations
                    </div>
                    <div id="annotationsList">
                        <div class="text-center py-8 text-gray-500 dark:text-gray-400 text-sm">
                            No annotations yet
                        </div>
                    </div>
                </div>

                <!-- Activity Tab -->
                <div id="activityContent" class="hidden p-4 space-y-2">
                    <div id="activityFeed">
                        <div class="text-center py-8 text-gray-500 dark:text-gray-400 text-sm">
                            No recent activity
                        </div>
                    </div>
                </div>
            </div>
        `;

        document.body.appendChild(panel);
    }

    toggle() {
        const panel = document.getElementById('collaborationPanel');
        panel.classList.toggle('hidden');
        
        if (!panel.classList.contains('hidden')) {
            this.loadCollaborationData();
        }
    }

    switchTab(tabName) {
        // Update tab buttons
        const tabs = ['comments', 'annotations', 'activity'];
        tabs.forEach(tab => {
            const button = document.getElementById(`${tab}Tab`);
            const content = document.getElementById(`${tab}Content`);
            
            if (tab === tabName) {
                button.className = 'flex-1 py-2 px-4 text-sm font-medium text-blue-600 border-b-2 border-blue-600 bg-blue-50 dark:bg-blue-900/20';
                content.classList.remove('hidden');
            } else {
                button.className = 'flex-1 py-2 px-4 text-sm font-medium text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-200';
                content.classList.add('hidden');
            }
        });

        // Load tab-specific data
        this.loadTabData(tabName);
    }

    loadTabData(tabName) {
        switch (tabName) {
            case 'comments':
                this.loadComments();
                break;
            case 'annotations':
                this.loadAnnotations();
                break;
            case 'activity':
                this.loadActivity();
                break;
        }
    }

    loadComments() {
        const commentsList = document.getElementById('commentsList');
        const comments = Array.from(this.comments.values()).sort((a, b) => new Date(a.timestamp) - new Date(b.timestamp));
        
        if (comments.length === 0) {
            commentsList.innerHTML = `
                <div class="text-center py-8 text-gray-500 dark:text-gray-400 text-sm">
                    No comments yet. Start a discussion!
                </div>
            `;
            return;
        }

        commentsList.innerHTML = comments.map(comment => `
            <div class="flex space-x-3 p-3 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700">
                <div class="flex-shrink-0">
                    <div class="w-8 h-8 rounded-full flex items-center justify-center text-white text-xs font-semibold"
                         style="background-color: ${comment.user.color}">
                        ${comment.user.name.charAt(0).toUpperCase()}
                    </div>
                </div>
                <div class="flex-1 min-w-0">
                    <div class="flex items-center space-x-2">
                        <span class="text-sm font-medium text-gray-900 dark:text-white">${comment.user.name}</span>
                        <span class="text-xs text-gray-500 dark:text-gray-400">${this.formatTimestamp(comment.timestamp)}</span>
                    </div>
                    <p class="text-sm text-gray-700 dark:text-gray-300 mt-1">${comment.text}</p>
                    ${comment.targetElement ? `
                        <div class="text-xs text-blue-600 dark:text-blue-400 mt-1">
                            📌 ${comment.targetElement}
                        </div>
                    ` : ''}
                </div>
                ${comment.user.id === this.currentUser.id ? `
                    <button onclick="realTimeCollaboration.deleteComment('${comment.id}')" 
                            class="text-gray-400 hover:text-red-500 text-xs">
                        <i class="fas fa-trash"></i>
                    </button>
                ` : ''}
            </div>
        `).join('');
    }

    addComment() {
        const input = document.getElementById('commentInput');
        const text = input.value.trim();
        
        if (!text) return;

        const comment = {
            id: 'comment_' + Date.now(),
            text: text,
            user: this.currentUser,
            timestamp: new Date().toISOString(),
            targetElement: this.getSelectedElement()
        };

        this.comments.set(comment.id, comment);
        input.value = '';
        this.loadComments();
        this.broadcastComment(comment);
        this.addToActivity('comment', `${this.currentUser.name} added a comment`);
    }

    handleCommentKeyPress(event) {
        if (event.key === 'Enter') {
            this.addComment();
        }
    }

    deleteComment(commentId) {
        if (this.comments.has(commentId)) {
            const comment = this.comments.get(commentId);
            if (comment.user.id === this.currentUser.id) {
                this.comments.delete(commentId);
                this.loadComments();
                this.broadcastCommentDeletion(commentId);
            }
        }
    }

    loadAnnotations() {
        const annotationsList = document.getElementById('annotationsList');
        const annotations = Array.from(this.annotations.values());
        
        if (annotations.length === 0) {
            annotationsList.innerHTML = `
                <div class="text-center py-8 text-gray-500 dark:text-gray-400 text-sm">
                    No annotations yet
                </div>
            `;
            return;
        }

        annotationsList.innerHTML = annotations.map(annotation => `
            <div class="border border-gray-200 dark:border-gray-600 rounded-lg p-3">
                <div class="flex items-center justify-between mb-2">
                    <span class="text-sm font-medium text-gray-900 dark:text-white">${annotation.element}</span>
                    <span class="text-xs text-gray-500 dark:text-gray-400">${this.formatTimestamp(annotation.timestamp)}</span>
                </div>
                <p class="text-sm text-gray-700 dark:text-gray-300">${annotation.note}</p>
                <div class="flex items-center mt-2">
                    <div class="w-6 h-6 rounded-full flex items-center justify-center text-white text-xs"
                         style="background-color: ${annotation.user.color}">
                        ${annotation.user.name.charAt(0).toUpperCase()}
                    </div>
                    <span class="text-xs text-gray-500 dark:text-gray-400 ml-2">${annotation.user.name}</span>
                </div>
            </div>
        `).join('');
    }

    addAnnotation(element, note) {
        const annotation = {
            id: 'annotation_' + Date.now(),
            element: element,
            note: note,
            user: this.currentUser,
            timestamp: new Date().toISOString()
        };

        this.annotations.set(annotation.id, annotation);
        this.loadAnnotations();
        this.addToActivity('annotation', `${this.currentUser.name} added an annotation to ${element}`);
        this.highlightAnnotatedElement(element);
    }

    highlightAnnotatedElement(element) {
        // Add visual indicator to the annotated element
        const targetElement = document.querySelector(`[data-test-name="${element}"]`);
        if (targetElement) {
            targetElement.classList.add('annotated-element');
            targetElement.style.position = 'relative';
            
            const indicator = document.createElement('div');
            indicator.className = 'annotation-indicator';
            indicator.innerHTML = '<i class="fas fa-comment-dots text-blue-500"></i>';
            indicator.style.cssText = 'position: absolute; top: -8px; right: -8px; background: white; border-radius: 50%; padding: 2px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);';
            targetElement.appendChild(indicator);
        }
    }

    loadActivity() {
        const activityFeed = document.getElementById('activityFeed');
        const activities = this.getRecentActivities();
        
        if (activities.length === 0) {
            activityFeed.innerHTML = `
                <div class="text-center py-8 text-gray-500 dark:text-gray-400 text-sm">
                    No recent activity
                </div>
            `;
            return;
        }

        activityFeed.innerHTML = activities.map(activity => `
            <div class="flex items-center space-x-3 py-2">
                <div class="flex-shrink-0">
                    <i class="${this.getActivityIcon(activity.type)} text-gray-400"></i>
                </div>
                <div class="flex-1">
                    <p class="text-sm text-gray-700 dark:text-gray-300">${activity.message}</p>
                    <p class="text-xs text-gray-500 dark:text-gray-400">${this.formatTimestamp(activity.timestamp)}</p>
                </div>
            </div>
        `).join('');
    }

    getActivityIcon(type) {
        const icons = {
            'comment': 'fas fa-comment',
            'annotation': 'fas fa-sticky-note',
            'user_join': 'fas fa-user-plus',
            'user_leave': 'fas fa-user-minus',
            'test_update': 'fas fa-flask',
            'result_change': 'fas fa-edit'
        };
        return icons[type] || 'fas fa-circle';
    }

    addToActivity(type, message) {
        const activity = {
            id: 'activity_' + Date.now(),
            type: type,
            message: message,
            timestamp: new Date().toISOString(),
            user: this.currentUser
        };

        // Store activity (in real app, this would go to server)
        const activities = JSON.parse(localStorage.getItem('collaboration_activities') || '[]');
        activities.unshift(activity);
        activities.splice(50); // Keep only last 50 activities
        localStorage.setItem('collaboration_activities', JSON.stringify(activities));
    }

    getRecentActivities() {
        return JSON.parse(localStorage.getItem('collaboration_activities') || '[]');
    }

    initializePresence() {
        // Simulate presence system
        this.isConnected = true;
        this.updateConnectionStatus('Connected');
        this.addActiveUser(this.currentUser);
        
        // Simulate other users joining
        setTimeout(() => {
            this.addActiveUser({
                id: 'user_demo1',
                name: 'Dr. Smith',
                role: 'Physician',
                color: '#10B981'
            });
        }, 2000);

        setTimeout(() => {
            this.addActiveUser({
                id: 'user_demo2',
                name: 'Technician Jane',
                role: 'Lab Technician',
                color: '#8B5CF6'
            });
        }, 4000);
    }

    updateConnectionStatus(status) {
        const statusElement = document.getElementById('connectionStatus');
        if (statusElement) {
            statusElement.textContent = status;
        }
    }

    addActiveUser(user) {
        this.activeUsers.set(user.id, user);
        this.updateActiveUsersDisplay();
        
        if (user.id !== this.currentUser.id) {
            this.addToActivity('user_join', `${user.name} joined the collaboration`);
        }
    }

    removeActiveUser(userId) {
        const user = this.activeUsers.get(userId);
        if (user) {
            this.activeUsers.delete(userId);
            this.updateActiveUsersDisplay();
            this.addToActivity('user_leave', `${user.name} left the collaboration`);
        }
    }

    updateActiveUsersDisplay() {
        const indicator = document.getElementById('activeUsersIndicator');
        if (!indicator) return;

        const users = Array.from(this.activeUsers.values()).slice(0, 4); // Show max 4 users
        
        indicator.innerHTML = users.map(user => `
            <div class="w-6 h-6 rounded-full border-2 border-white flex items-center justify-center text-white text-xs font-semibold"
                 style="background-color: ${user.color}"
                 title="${user.name} (${user.role})">
                ${user.name.charAt(0).toUpperCase()}
            </div>
        `).join('');

        if (this.activeUsers.size > 4) {
            indicator.innerHTML += `
                <div class="w-6 h-6 rounded-full border-2 border-white bg-gray-500 flex items-center justify-center text-white text-xs">
                    +${this.activeUsers.size - 4}
                </div>
            `;
        }
    }

    getSelectedElement() {
        // Get currently focused/selected test result or element
        const activeElement = document.activeElement;
        if (activeElement && activeElement.getAttribute('data-test-name')) {
            return activeElement.getAttribute('data-test-name');
        }
        return null;
    }

    formatTimestamp(timestamp) {
        const date = new Date(timestamp);
        const now = new Date();
        const diff = now - date;
        const minutes = Math.floor(diff / 60000);
        
        if (minutes < 1) return 'Just now';
        if (minutes < 60) return `${minutes}m ago`;
        if (minutes < 1440) return `${Math.floor(minutes / 60)}h ago`;
        return date.toLocaleDateString();
    }

    loadCollaborationData() {
        // Simulate loading comments and annotations
        if (this.comments.size === 0) {
            // Add some demo comments
            this.comments.set('demo1', {
                id: 'demo1',
                text: 'This glucose level looks elevated. Should we run additional tests?',
                user: { id: 'user_demo1', name: 'Dr. Smith', color: '#10B981' },
                timestamp: new Date(Date.now() - 300000).toISOString(), // 5 minutes ago
                targetElement: 'Glucose'
            });

            this.comments.set('demo2', {
                id: 'demo2',
                text: 'Patient mentioned they were fasting for 12 hours before the test.',
                user: { id: 'user_demo2', name: 'Technician Jane', color: '#8B5CF6' },
                timestamp: new Date(Date.now() - 120000).toISOString(), // 2 minutes ago
                targetElement: null
            });
        }

        this.loadComments();
    }

    broadcastComment(comment) {
        // In a real implementation, this would send the comment to other users via WebSocket
        console.log('Broadcasting comment:', comment);
    }

    broadcastCommentDeletion(commentId) {
        // In a real implementation, this would notify other users of comment deletion
        console.log('Broadcasting comment deletion:', commentId);
    }

    setupEventListeners() {
        // Listen for test result clicks to enable annotations
        document.addEventListener('click', (event) => {
            const testElement = event.target.closest('[data-test-name]');
            if (testElement && event.ctrlKey) {
                const testName = testElement.getAttribute('data-test-name');
                const note = prompt(`Add annotation for ${testName}:`);
                if (note) {
                    this.addAnnotation(testName, note);
                }
            }
        });

        // Listen for collaboration events
        document.addEventListener('collaborationEvent', (event) => {
            const { type, data } = event.detail;
            this.handleCollaborationEvent(type, data);
        });
    }

    handleCollaborationEvent(type, data) {
        switch (type) {
            case 'comment_added':
                this.comments.set(data.id, data);
                this.loadComments();
                break;
            case 'comment_deleted':
                this.comments.delete(data.commentId);
                this.loadComments();
                break;
            case 'annotation_added':
                this.annotations.set(data.id, data);
                this.loadAnnotations();
                break;
            case 'user_joined':
                this.addActiveUser(data.user);
                break;
            case 'user_left':
                this.removeActiveUser(data.userId);
                break;
        }
    }

    // Public API methods
    showForElement(elementName) {
        this.toggle();
        this.switchTab('comments');
        document.getElementById('commentInput').placeholder = `Comment on ${elementName}...`;
    }

    addQuickComment(elementName, comment) {
        const commentData = {
            id: 'comment_' + Date.now(),
            text: comment,
            user: this.currentUser,
            timestamp: new Date().toISOString(),
            targetElement: elementName
        };

        this.comments.set(commentData.id, commentData);
        this.loadComments();
        this.addToActivity('comment', `${this.currentUser.name} commented on ${elementName}`);
    }
}

// Initialize global instance
window.realTimeCollaboration = new RealTimeCollaboration();

// Global functions for template use
function openCollaboration() {
    window.realTimeCollaboration.toggle();
}

function addCommentToElement(elementName, comment) {
    window.realTimeCollaboration.addQuickComment(elementName, comment);
}

function showCollaborationForElement(elementName) {
    window.realTimeCollaboration.showForElement(elementName);
}