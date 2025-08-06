// MedLab Pro - Main Application JavaScript

// Global application state
const MedLabPro = {
    theme: 'light',
    language: 'en',
    user: null,
    charts: {},
    
    // Initialize the application
    init() {
        this.setupEventListeners();
        this.loadTheme();
        this.initializeCharts();
        this.setupTooltips();
        this.setupFormValidation();
        this.startPeriodicUpdates();
    },
    
    // Setup global event listeners
    setupEventListeners() {
        // Theme toggle
        document.addEventListener('click', (e) => {
            if (e.target.matches('[data-theme-toggle]')) {
                this.toggleTheme();
            }
        });
        
        // Language toggle
        document.addEventListener('click', (e) => {
            if (e.target.matches('[data-lang]')) {
                this.setLanguage(e.target.dataset.lang);
            }
        });
        
        // Modal handling
        document.addEventListener('click', (e) => {
            if (e.target.matches('[data-modal-open]')) {
                this.openModal(e.target.dataset.modalOpen);
            }
            if (e.target.matches('[data-modal-close]')) {
                this.closeModal(e.target.dataset.modalClose);
            }
        });
        
        // Form submission handlers
        document.addEventListener('submit', (e) => {
            if (e.target.matches('[data-ajax-form]')) {
                this.handleAjaxForm(e);
            }
        });
        
        // Keyboard shortcuts
        document.addEventListener('keydown', (e) => {
            this.handleKeyboardShortcuts(e);
        });
        
        // Handle window resize for responsive charts
        window.addEventListener('resize', this.debounce(() => {
            this.resizeCharts();
        }, 250));
    },
    
    // Theme management
    loadTheme() {
        const savedTheme = localStorage.getItem('theme') || 'light';
        this.setTheme(savedTheme);
    },
    
    setTheme(theme) {
        this.theme = theme;
        document.documentElement.classList.toggle('dark', theme === 'dark');
        localStorage.setItem('theme', theme);
        
        // Update theme toggle button
        const themeToggle = document.querySelector('[data-theme-toggle]');
        if (themeToggle) {
            const icon = themeToggle.querySelector('i');
            if (icon) {
                icon.className = theme === 'dark' ? 'fas fa-sun' : 'fas fa-moon';
            }
        }
        
        // Update charts colors for theme
        this.updateChartsTheme();
    },
    
    toggleTheme() {
        const newTheme = this.theme === 'light' ? 'dark' : 'light';
        this.setTheme(newTheme);
        
        // Send theme preference to server
        this.updateUserPreference('theme', newTheme);
    },
    
    // Language management
    setLanguage(lang) {
        this.language = lang;
        document.documentElement.setAttribute('lang', lang);
        document.documentElement.setAttribute('dir', lang === 'fa' ? 'rtl' : 'ltr');
        localStorage.setItem('language', lang);
        
        // Update language toggle buttons
        document.querySelectorAll('[data-lang]').forEach(btn => {
            btn.classList.toggle('active', btn.dataset.lang === lang);
        });
        
        // Send language preference to server
        this.updateUserPreference('language', lang);
    },
    
    // Modal management
    openModal(modalId) {
        const modal = document.getElementById(modalId);
        if (modal) {
            modal.classList.remove('hidden');
            document.body.style.overflow = 'hidden';
            
            // Focus first input in modal
            const firstInput = modal.querySelector('input, textarea, select');
            if (firstInput) {
                setTimeout(() => firstInput.focus(), 100);
            }
            
            // Add animation class
            const content = modal.querySelector('.modal-content');
            if (content) {
                content.classList.add('animate-scale-in');
            }
        }
    },
    
    closeModal(modalId) {
        const modal = document.getElementById(modalId);
        if (modal) {
            modal.classList.add('hidden');
            document.body.style.overflow = 'auto';
            
            // Reset form if exists
            const form = modal.querySelector('form');
            if (form) {
                form.reset();
                this.clearFormErrors(form);
            }
        }
    },
    
    // Chart management
    initializeCharts() {
        // Initialize dashboard charts if on dashboard page
        if (document.getElementById('testDistributionChart')) {
            this.initDashboardCharts();
        }
        
        // Initialize other page-specific charts
        this.initPageCharts();
    },
    
    updateChartsTheme() {
        const isDark = this.theme === 'dark';
        const textColor = isDark ? '#f3f4f6' : '#374151';
        const gridColor = isDark ? '#374151' : '#e5e7eb';
        
        Object.values(this.charts).forEach(chart => {
            if (chart && chart.options) {
                // Update scales colors
                if (chart.options.scales) {
                    Object.values(chart.options.scales).forEach(scale => {
                        if (scale.ticks) scale.ticks.color = textColor;
                        if (scale.grid) scale.grid.color = gridColor;
                    });
                }
                
                // Update legend colors
                if (chart.options.plugins && chart.options.plugins.legend) {
                    chart.options.plugins.legend.labels.color = textColor;
                }
                
                chart.update();
            }
        });
    },
    
    resizeCharts() {
        Object.values(this.charts).forEach(chart => {
            if (chart && chart.resize) {
                chart.resize();
            }
        });
    },
    
    // Form handling
    handleAjaxForm(event) {
        event.preventDefault();
        const form = event.target;
        const formData = new FormData(form);
        const submitBtn = form.querySelector('button[type="submit"]');
        
        // Show loading state
        this.setButtonLoading(submitBtn, true);
        
        fetch(form.action, {
            method: form.method,
            body: formData,
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                this.showNotification(data.message || 'Operation completed successfully', 'success');
                this.closeModal(form.closest('.modal')?.id);
                
                // Refresh page data if needed
                if (data.refresh) {
                    setTimeout(() => window.location.reload(), 1000);
                }
            } else {
                this.showFormErrors(form, data.errors || {});
                this.showNotification(data.message || 'Please correct the errors below', 'error');
            }
        })
        .catch(error => {
            console.error('Form submission error:', error);
            this.showNotification('An error occurred. Please try again.', 'error');
        })
        .finally(() => {
            this.setButtonLoading(submitBtn, false);
        });
    },
    
    setButtonLoading(button, loading) {
        if (!button) return;
        
        if (loading) {
            button.disabled = true;
            const originalText = button.innerHTML;
            button.dataset.originalText = originalText;
            button.innerHTML = '<i class="fas fa-spinner fa-spin mr-2"></i>Loading...';
        } else {
            button.disabled = false;
            button.innerHTML = button.dataset.originalText || button.innerHTML;
        }
    },
    
    // Form validation
    setupFormValidation() {
        document.addEventListener('input', (e) => {
            if (e.target.matches('input, textarea, select')) {
                this.validateField(e.target);
            }
        });
        
        document.addEventListener('blur', (e) => {
            if (e.target.matches('input, textarea, select')) {
                this.validateField(e.target);
            }
        });
    },
    
    validateField(field) {
        const errors = [];
        
        // Required field validation
        if (field.hasAttribute('required') && !field.value.trim()) {
            errors.push('This field is required');
        }
        
        // Email validation
        if (field.type === 'email' && field.value) {
            const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            if (!emailRegex.test(field.value)) {
                errors.push('Please enter a valid email address');
            }
        }
        
        // Password confirmation
        if (field.name === 'confirm_password') {
            const passwordField = field.form.querySelector('input[name="password"], input[name="new_password"]');
            if (passwordField && field.value !== passwordField.value) {
                errors.push('Passwords do not match');
            }
        }
        
        // Phone number validation
        if (field.type === 'tel' && field.value) {
            const phoneRegex = /^[\+]?[1-9][\d]{0,15}$/;
            if (!phoneRegex.test(field.value.replace(/[\s\-\(\)]/g, ''))) {
                errors.push('Please enter a valid phone number');
            }
        }
        
        this.setFieldError(field, errors[0] || null);
    },
    
    setFieldError(field, message) {
        const errorElement = field.parentNode.querySelector('.error-message');
        
        if (message) {
            field.classList.add('form-error');
            if (errorElement) {
                errorElement.textContent = message;
            } else {
                const error = document.createElement('div');
                error.className = 'error-message';
                error.textContent = message;
                field.parentNode.appendChild(error);
            }
        } else {
            field.classList.remove('form-error');
            if (errorElement) {
                errorElement.remove();
            }
        }
    },
    
    showFormErrors(form, errors) {
        Object.entries(errors).forEach(([fieldName, message]) => {
            const field = form.querySelector(`[name="${fieldName}"]`);
            if (field) {
                this.setFieldError(field, message);
            }
        });
    },
    
    clearFormErrors(form) {
        form.querySelectorAll('.form-error').forEach(field => {
            field.classList.remove('form-error');
        });
        form.querySelectorAll('.error-message').forEach(error => {
            error.remove();
        });
    },
    
    // Notifications
    showNotification(message, type = 'info', duration = 5000) {
        const notification = document.createElement('div');
        notification.className = `fixed top-4 right-4 z-50 p-4 rounded-lg shadow-lg max-w-sm animate-slide-down ${this.getNotificationClasses(type)}`;
        
        notification.innerHTML = `
            <div class="flex items-center">
                <i class="${this.getNotificationIcon(type)} mr-3"></i>
                <p class="text-sm font-medium">${message}</p>
                <button class="ml-auto text-gray-400 hover:text-gray-600" onclick="this.parentNode.parentNode.remove()">
                    <i class="fas fa-times"></i>
                </button>
            </div>
        `;
        
        document.body.appendChild(notification);
        
        // Auto remove
        setTimeout(() => {
            if (notification.parentNode) {
                notification.style.opacity = '0';
                notification.style.transform = 'translateX(100%)';
                setTimeout(() => notification.remove(), 300);
            }
        }, duration);
    },
    
    getNotificationClasses(type) {
        const classes = {
            success: 'bg-green-50 border-l-4 border-green-500 text-green-800',
            error: 'bg-red-50 border-l-4 border-red-500 text-red-800',
            warning: 'bg-yellow-50 border-l-4 border-yellow-500 text-yellow-800',
            info: 'bg-blue-50 border-l-4 border-blue-500 text-blue-800'
        };
        return classes[type] || classes.info;
    },
    
    getNotificationIcon(type) {
        const icons = {
            success: 'fas fa-check-circle text-green-500',
            error: 'fas fa-exclamation-circle text-red-500',
            warning: 'fas fa-exclamation-triangle text-yellow-500',
            info: 'fas fa-info-circle text-blue-500'
        };
        return icons[type] || icons.info;
    },
    
    // Tooltips
    setupTooltips() {
        document.addEventListener('mouseenter', (e) => {
            if (e.target.hasAttribute('title') || e.target.hasAttribute('data-tooltip')) {
                this.showTooltip(e.target);
            }
        });
        
        document.addEventListener('mouseleave', (e) => {
            if (e.target.hasAttribute('title') || e.target.hasAttribute('data-tooltip')) {
                this.hideTooltip();
            }
        });
    },
    
    showTooltip(element) {
        const text = element.getAttribute('data-tooltip') || element.getAttribute('title');
        if (!text) return;
        
        const tooltip = document.createElement('div');
        tooltip.className = 'tooltip show';
        tooltip.textContent = text;
        tooltip.id = 'global-tooltip';
        
        document.body.appendChild(tooltip);
        
        // Position tooltip
        const rect = element.getBoundingClientRect();
        tooltip.style.left = rect.left + (rect.width / 2) - (tooltip.offsetWidth / 2) + 'px';
        tooltip.style.top = rect.top - tooltip.offsetHeight - 8 + 'px';
        
        // Hide original title
        if (element.hasAttribute('title')) {
            element.dataset.originalTitle = element.getAttribute('title');
            element.removeAttribute('title');
        }
    },
    
    hideTooltip() {
        const tooltip = document.getElementById('global-tooltip');
        if (tooltip) {
            tooltip.remove();
        }
        
        // Restore original title
        document.querySelectorAll('[data-original-title]').forEach(el => {
            el.setAttribute('title', el.dataset.originalTitle);
            delete el.dataset.originalTitle;
        });
    },
    
    // Keyboard shortcuts
    handleKeyboardShortcuts(event) {
        // Escape key closes modals
        if (event.key === 'Escape') {
            const openModal = document.querySelector('.modal:not(.hidden)');
            if (openModal) {
                this.closeModal(openModal.id);
            }
        }
        
        // Ctrl/Cmd + K for search
        if ((event.ctrlKey || event.metaKey) && event.key === 'k') {
            event.preventDefault();
            const searchInput = document.querySelector('input[type="search"], input[placeholder*="search" i]');
            if (searchInput) {
                searchInput.focus();
            }
        }
        
        // Ctrl/Cmd + N for new item
        if ((event.ctrlKey || event.metaKey) && event.key === 'n') {
            event.preventDefault();
            const addButton = document.querySelector('[data-modal-open]');
            if (addButton) {
                addButton.click();
            }
        }
    },
    
    // User preferences
    updateUserPreference(key, value) {
        fetch('/settings/update', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
                'X-Requested-With': 'XMLHttpRequest'
            },
            body: `${key}=${encodeURIComponent(value)}`
        }).catch(error => {
            console.warn('Failed to update user preference:', error);
        });
    },
    
    // Periodic updates
    startPeriodicUpdates() {
        // Update dashboard stats every 30 seconds
        if (document.getElementById('dashboard-stats')) {
            setInterval(() => this.updateDashboardStats(), 30000);
        }
        
        // Check for notifications every minute
        setInterval(() => this.checkNotifications(), 60000);
    },
    
    updateDashboardStats() {
        fetch('/api/dashboard-stats')
            .then(response => response.json())
            .then(data => {
                // Update stats cards
                this.updateStatsCards(data);
                
                // Update charts
                this.updateDashboardCharts(data);
            })
            .catch(error => {
                console.warn('Failed to update dashboard stats:', error);
            });
    },
    
    checkNotifications() {
        // Check for system notifications
        fetch('/api/notifications')
            .then(response => response.json())
            .then(data => {
                data.notifications?.forEach(notification => {
                    this.showNotification(notification.message, notification.type);
                });
            })
            .catch(error => {
                console.warn('Failed to check notifications:', error);
            });
    },
    
    // Utility functions
    debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    },
    
    formatNumber(number) {
        return new Intl.NumberFormat().format(number);
    },
    
    formatDate(date, options = {}) {
        return new Intl.DateTimeFormat(this.language, options).format(new Date(date));
    },
    
    formatCurrency(amount, currency = 'USD') {
        return new Intl.NumberFormat(this.language, {
            style: 'currency',
            currency: currency
        }).format(amount);
    }
};

// Data tables functionality
const DataTable = {
    init(tableId, options = {}) {
        const table = document.getElementById(tableId);
        if (!table) return;
        
        this.setupSorting(table);
        this.setupFiltering(table, options.filters);
        this.setupPagination(table, options.pageSize || 10);
    },
    
    setupSorting(table) {
        const headers = table.querySelectorAll('th[data-sort]');
        headers.forEach(header => {
            header.style.cursor = 'pointer';
            header.addEventListener('click', () => {
                this.sortTable(table, header.dataset.sort, header);
            });
        });
    },
    
    sortTable(table, column, header) {
        const tbody = table.querySelector('tbody');
        const rows = Array.from(tbody.querySelectorAll('tr'));
        const isAscending = !header.classList.contains('sort-asc');
        
        // Remove sort classes from all headers
        table.querySelectorAll('th').forEach(th => {
            th.classList.remove('sort-asc', 'sort-desc');
        });
        
        // Add sort class to current header
        header.classList.add(isAscending ? 'sort-asc' : 'sort-desc');
        
        rows.sort((a, b) => {
            const aValue = a.querySelector(`td:nth-child(${this.getColumnIndex(header)})`).textContent.trim();
            const bValue = b.querySelector(`td:nth-child(${this.getColumnIndex(header)})`).textContent.trim();
            
            const comparison = aValue.localeCompare(bValue, undefined, { numeric: true });
            return isAscending ? comparison : -comparison;
        });
        
        rows.forEach(row => tbody.appendChild(row));
    },
    
    getColumnIndex(header) {
        return Array.from(header.parentNode.children).indexOf(header) + 1;
    }
};

// Search functionality
const Search = {
    init() {
        document.addEventListener('input', (e) => {
            if (e.target.matches('[data-search]')) {
                this.handleSearch(e.target);
            }
        });
    },
    
    handleSearch(input) {
        const target = input.dataset.search;
        const query = input.value.toLowerCase();
        const items = document.querySelectorAll(target);
        
        items.forEach(item => {
            const text = item.textContent.toLowerCase();
            const matches = text.includes(query);
            item.style.display = matches ? '' : 'none';
        });
    }
};

// Initialize application when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    MedLabPro.init();
    DataTable.init('main-table');
    Search.init();
});

// Global functions for template use
window.showModal = (modalId) => MedLabPro.openModal(modalId);
window.hideModal = (modalId) => MedLabPro.closeModal(modalId);
window.showNotification = (message, type, duration) => MedLabPro.showNotification(message, type, duration);
window.toggleTheme = () => MedLabPro.toggleTheme();
window.setLanguage = (lang) => MedLabPro.setLanguage(lang);

// Export for module use
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { MedLabPro, DataTable, Search };
}
