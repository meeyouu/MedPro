/**
 * MedLab Pro Language System
 * Automatic language switching with RTL/LTR support
 */

class LanguageSystem {
    constructor() {
        this.currentLanguage = this.getCurrentLanguage();
        this.init();
    }

    init() {
        this.applyLanguageSettings();
        this.initEventListeners();
    }

    getCurrentLanguage() {
        return document.documentElement.lang || 'en';
    }

    applyLanguageSettings() {
        const isRTL = this.currentLanguage === 'fa';
        
        // Update HTML attributes
        document.documentElement.lang = this.currentLanguage;
        document.documentElement.dir = isRTL ? 'rtl' : 'ltr';
        
        // Update font classes
        document.documentElement.classList.remove('font-inter', 'font-vazir');
        document.documentElement.classList.add(isRTL ? 'font-vazir' : 'font-inter');
        
        // Update body font classes
        document.body.classList.remove('font-inter', 'font-vazir');
        document.body.classList.add(isRTL ? 'font-vazir' : 'font-inter');
        
        // Update navigation spacing for RTL
        this.updateNavigationSpacing(isRTL);
        
        // Update language indicator
        this.updateLanguageIndicator();
    }

    updateNavigationSpacing(isRTL) {
        const nav = document.querySelector('nav');
        if (nav) {
            // Update flex direction and spacing for RTL
            const items = nav.querySelectorAll('.space-x-2, .space-x-4, .space-x-6');
            items.forEach(item => {
                if (isRTL) {
                    item.style.flexDirection = 'row-reverse';
                } else {
                    item.style.flexDirection = '';
                }
            });
        }
    }

    updateLanguageIndicator() {
        const indicator = document.querySelector('.language-indicator');
        if (indicator) {
            indicator.textContent = this.currentLanguage === 'en' ? 'EN' : 'فا';
        }
    }

    changeLanguage(newLanguage) {
        if (newLanguage === this.currentLanguage) return;

        // Show loading state
        this.showLoadingState();

        // Call API to change language
        fetch('/api/change-language', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ language: newLanguage })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Update current language
                this.currentLanguage = newLanguage;
                
                // Apply new settings immediately
                this.applyLanguageSettings();
                
                // Reload page to get translated content
                setTimeout(() => {
                    window.location.reload();
                }, 100);
            } else {
                this.hideLoadingState();
                this.showError('Failed to change language');
            }
        })
        .catch(error => {
            this.hideLoadingState();
            this.showError('Network error occurred');
            console.error('Language change error:', error);
        });
    }

    showLoadingState() {
        const button = document.querySelector('[onclick*="toggleLanguageMenu"]');
        if (button) {
            button.disabled = true;
            button.style.opacity = '0.6';
        }
    }

    hideLoadingState() {
        const button = document.querySelector('[onclick*="toggleLanguageMenu"]');
        if (button) {
            button.disabled = false;
            button.style.opacity = '';
        }
    }

    showError(message) {
        // Simple error notification
        const notification = document.createElement('div');
        notification.className = 'fixed top-4 right-4 bg-red-500 text-white px-4 py-2 rounded-lg shadow-lg z-50';
        notification.textContent = message;
        document.body.appendChild(notification);
        
        setTimeout(() => {
            notification.remove();
        }, 3000);
    }

    initEventListeners() {
        // Close language menu when clicking outside
        document.addEventListener('click', (event) => {
            const languageMenu = document.getElementById('languageMenu');
            const languageButton = event.target.closest('[onclick*="toggleLanguageMenu"]');
            
            if (languageMenu && !languageButton && !languageMenu.contains(event.target)) {
                languageMenu.classList.add('hidden');
            }
        });

        // Handle keyboard navigation
        document.addEventListener('keydown', (event) => {
            if (event.key === 'Escape') {
                const languageMenu = document.getElementById('languageMenu');
                if (languageMenu && !languageMenu.classList.contains('hidden')) {
                    languageMenu.classList.add('hidden');
                }
            }
        });
    }
}

// Global functions for template use
function toggleLanguageMenu() {
    const menu = document.getElementById('languageMenu');
    if (menu) {
        menu.classList.toggle('hidden');
    }
}

function changeLanguage(lang) {
    if (window.languageSystem) {
        window.languageSystem.changeLanguage(lang);
    } else {
        // Fallback for direct API call
        fetch('/api/change-language', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ language: lang })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                window.location.reload();
            }
        })
        .catch(error => {
            console.error('Language change error:', error);
        });
    }
}

// Initialize language system when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    window.languageSystem = new LanguageSystem();
});

// Additional utility functions for RTL support
function updateRTLStyles() {
    const isRTL = document.documentElement.dir === 'rtl';
    
    // Update table alignment
    const tables = document.querySelectorAll('table');
    tables.forEach(table => {
        if (isRTL) {
            table.style.direction = 'rtl';
        } else {
            table.style.direction = '';
        }
    });
    
    // Update form alignment
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        if (isRTL) {
            form.style.direction = 'rtl';
        } else {
            form.style.direction = '';
        }
    });
}