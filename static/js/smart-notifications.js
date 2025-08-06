/**
 * Smart Notifications System for MedLab Pro
 * Real-time notifications for test results, critical values, and system updates
 */

class SmartNotifications {
    constructor() {
        this.notifications = [];
        this.isEnabled = this.checkPermission();
        this.socket = null;
        this.init();
    }

    init() {
        this.createNotificationContainer();
        this.requestPermission();
        this.setupEventListeners();
        this.loadStoredNotifications();
    }

    checkPermission() {
        if (!("Notification" in window)) {
            console.warn("Browser doesn't support notifications");
            return false;
        }
        return Notification.permission === "granted";
    }

    async requestPermission() {
        if (!("Notification" in window)) return false;
        
        if (Notification.permission === "default") {
            const permission = await Notification.requestPermission();
            this.isEnabled = permission === "granted";
        }
        return this.isEnabled;
    }

    createNotificationContainer() {
        if (document.getElementById('notificationContainer')) return;
        
        const container = document.createElement('div');
        container.id = 'notificationContainer';
        container.className = 'fixed top-20 right-4 z-50 space-y-2 max-w-sm';
        document.body.appendChild(container);
    }

    showNotification(type, title, message, data = {}) {
        const notification = {
            id: Date.now(),
            type,
            title,
            message,
            data,
            timestamp: new Date(),
            read: false
        };

        this.notifications.unshift(notification);
        this.saveToStorage();
        this.displayInPageNotification(notification);
        
        if (this.isEnabled && document.hidden) {
            this.showBrowserNotification(notification);
        }

        this.updateNotificationBadge();
        return notification.id;
    }

    displayInPageNotification(notification) {
        const container = document.getElementById('notificationContainer');
        if (!container) return;

        const notifElement = document.createElement('div');
        notifElement.id = `notification-${notification.id}`;
        notifElement.className = `
            bg-white dark:bg-gray-800 rounded-lg shadow-lg border-l-4 p-4 
            transform transition-all duration-300 translate-x-full opacity-0
            ${this.getNotificationStyle(notification.type)}
        `;

        notifElement.innerHTML = `
            <div class="flex items-start">
                <div class="flex-shrink-0">
                    <i class="${this.getNotificationIcon(notification.type)} text-lg"></i>
                </div>
                <div class="ml-3 flex-1">
                    <p class="text-sm font-medium text-gray-900 dark:text-white">
                        ${notification.title}
                    </p>
                    <p class="text-sm text-gray-600 dark:text-gray-300 mt-1">
                        ${notification.message}
                    </p>
                    <p class="text-xs text-gray-400 mt-2">
                        ${this.formatTime(notification.timestamp)}
                    </p>
                </div>
                <button onclick="smartNotifications.dismissNotification('${notification.id}')" 
                        class="ml-4 text-gray-400 hover:text-gray-600 dark:hover:text-gray-200">
                    <i class="fas fa-times"></i>
                </button>
            </div>
        `;

        container.appendChild(notifElement);

        // Animate in
        setTimeout(() => {
            notifElement.classList.remove('translate-x-full', 'opacity-0');
        }, 10);

        // Auto dismiss after 5 seconds for non-critical notifications
        if (notification.type !== 'critical') {
            setTimeout(() => {
                this.dismissNotification(notification.id);
            }, 5000);
        }
    }

    showBrowserNotification(notification) {
        if (!this.isEnabled) return;

        const browserNotif = new Notification(notification.title, {
            body: notification.message,
            icon: '/static/img/logo.png',
            badge: '/static/img/badge.png',
            tag: notification.type,
            requireInteraction: notification.type === 'critical'
        });

        browserNotif.onclick = () => {
            window.focus();
            this.handleNotificationClick(notification);
            browserNotif.close();
        };
    }

    handleNotificationClick(notification) {
        // Mark as read
        notification.read = true;
        this.saveToStorage();
        this.updateNotificationBadge();

        // Navigate based on notification type
        switch (notification.type) {
            case 'test_result':
                if (notification.data.patientId) {
                    window.location.href = `/patients/${notification.data.patientId}`;
                }
                break;
            case 'critical':
                if (notification.data.testId) {
                    window.location.href = `/tests/${notification.data.testId}`;
                }
                break;
            case 'report_ready':
                if (notification.data.reportId) {
                    window.location.href = `/reports/${notification.data.reportId}`;
                }
                break;
        }
    }

    dismissNotification(notificationId) {
        const element = document.getElementById(`notification-${notificationId}`);
        if (element) {
            element.classList.add('translate-x-full', 'opacity-0');
            setTimeout(() => element.remove(), 300);
        }

        // Mark as read in storage
        const notification = this.notifications.find(n => n.id == notificationId);
        if (notification) {
            notification.read = true;
            this.saveToStorage();
            this.updateNotificationBadge();
        }
    }

    getNotificationStyle(type) {
        const styles = {
            'info': 'border-blue-400',
            'success': 'border-green-400',
            'warning': 'border-yellow-400',
            'error': 'border-red-400',
            'critical': 'border-red-600 bg-red-50 dark:bg-red-900/20',
            'test_result': 'border-blue-400',
            'report_ready': 'border-green-400'
        };
        return styles[type] || 'border-gray-400';
    }

    getNotificationIcon(type) {
        const icons = {
            'info': 'fas fa-info-circle text-blue-500',
            'success': 'fas fa-check-circle text-green-500',
            'warning': 'fas fa-exclamation-triangle text-yellow-500',
            'error': 'fas fa-times-circle text-red-500',
            'critical': 'fas fa-exclamation-circle text-red-600',
            'test_result': 'fas fa-flask text-blue-500',
            'report_ready': 'fas fa-file-alt text-green-500'
        };
        return icons[type] || 'fas fa-bell text-gray-500';
    }

    formatTime(timestamp) {
        const now = new Date();
        const diff = now - timestamp;
        const minutes = Math.floor(diff / 60000);
        
        if (minutes < 1) return 'Just now';
        if (minutes < 60) return `${minutes}m ago`;
        if (minutes < 1440) return `${Math.floor(minutes / 60)}h ago`;
        return timestamp.toLocaleDateString();
    }

    updateNotificationBadge() {
        const unreadCount = this.notifications.filter(n => !n.read).length;
        const badge = document.getElementById('notificationBadge');
        
        if (badge) {
            if (unreadCount > 0) {
                badge.textContent = unreadCount > 99 ? '99+' : unreadCount;
                badge.classList.remove('hidden');
            } else {
                badge.classList.add('hidden');
            }
        }
    }

    loadStoredNotifications() {
        const stored = localStorage.getItem('medlab_notifications');
        if (stored) {
            this.notifications = JSON.parse(stored).map(n => ({
                ...n,
                timestamp: new Date(n.timestamp)
            }));
            this.updateNotificationBadge();
        }
    }

    saveToStorage() {
        // Keep only last 50 notifications
        const toStore = this.notifications.slice(0, 50);
        localStorage.setItem('medlab_notifications', JSON.stringify(toStore));
    }

    setupEventListeners() {
        // Listen for test result updates
        document.addEventListener('testResultUpdate', (event) => {
            const { patient, test, result } = event.detail;
            this.showNotification(
                result.status === 'critical' ? 'critical' : 'test_result',
                'Test Result Available',
                `${test.name} results for ${patient.name} are ready`,
                { patientId: patient.id, testId: test.id }
            );
        });

        // Listen for critical values
        document.addEventListener('criticalValue', (event) => {
            const { patient, test, value } = event.detail;
            this.showNotification(
                'critical',
                'Critical Value Alert',
                `${test.name}: ${value} for ${patient.name} requires immediate attention`,
                { patientId: patient.id, testId: test.id }
            );
        });

        // Listen for report generation
        document.addEventListener('reportGenerated', (event) => {
            const { patient, reportType } = event.detail;
            this.showNotification(
                'report_ready',
                'AI Report Generated',
                `${reportType} report for ${patient.name} is ready for review`,
                { reportId: event.detail.reportId }
            );
        });
    }

    // API methods for external use
    notifyTestResult(patient, test, result) {
        const event = new CustomEvent('testResultUpdate', {
            detail: { patient, test, result }
        });
        document.dispatchEvent(event);
    }

    notifyCriticalValue(patient, test, value) {
        const event = new CustomEvent('criticalValue', {
            detail: { patient, test, value }
        });
        document.dispatchEvent(event);
    }

    notifyReportReady(patient, reportType, reportId) {
        const event = new CustomEvent('reportGenerated', {
            detail: { patient, reportType, reportId }
        });
        document.dispatchEvent(event);
    }

    showCustomNotification(type, title, message, data = {}) {
        return this.showNotification(type, title, message, data);
    }

    clearAllNotifications() {
        this.notifications = [];
        this.saveToStorage();
        this.updateNotificationBadge();
        
        const container = document.getElementById('notificationContainer');
        if (container) {
            container.innerHTML = '';
        }
    }

    markAllAsRead() {
        this.notifications.forEach(n => n.read = true);
        this.saveToStorage();
        this.updateNotificationBadge();
    }

    getUnreadNotifications() {
        return this.notifications.filter(n => !n.read);
    }

    getAllNotifications() {
        return this.notifications;
    }
}

// Initialize global instance
window.smartNotifications = new SmartNotifications();

// Demo function for testing
function demoNotifications() {
    smartNotifications.showCustomNotification('info', 'System Info', 'MedLab Pro is running smoothly');
    
    setTimeout(() => {
        smartNotifications.showCustomNotification('test_result', 'Test Complete', 'Blood panel results are available for John Doe');
    }, 1000);
    
    setTimeout(() => {
        smartNotifications.showCustomNotification('critical', 'Critical Alert', 'High glucose level detected - requires immediate review');
    }, 2000);
    
    setTimeout(() => {
        smartNotifications.showCustomNotification('report_ready', 'Report Ready', 'AI analysis report has been generated');
    }, 3000);
}