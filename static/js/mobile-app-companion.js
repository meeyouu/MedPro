/**
 * Mobile App Companion for MedLab Pro
 * PWA features and mobile-optimized interface components
 */

class MobileAppCompanion {
    constructor() {
        this.isInstalled = false;
        this.deferredPrompt = null;
        this.isMobile = this.detectMobile();
        this.isStandalone = this.detectStandalone();
        this.init();
    }

    init() {
        this.setupPWA();
        this.createMobileInterface();
        this.setupEventListeners();
        this.optimizeForMobile();
    }

    detectMobile() {
        return /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);
    }

    detectStandalone() {
        return window.matchMedia('(display-mode: standalone)').matches || 
               window.navigator.standalone || 
               document.referrer.includes('android-app://');
    }

    setupPWA() {
        // Register service worker
        if ('serviceWorker' in navigator) {
            navigator.serviceWorker.register('/static/js/sw.js')
                .then(registration => {
                    console.log('SW registered:', registration);
                })
                .catch(error => {
                    console.log('SW registration failed:', error);
                });
        }

        // Handle install prompt
        window.addEventListener('beforeinstallprompt', (e) => {
            e.preventDefault();
            this.deferredPrompt = e;
            this.showInstallButton();
        });

        // Handle app installed
        window.addEventListener('appinstalled', () => {
            this.isInstalled = true;
            this.hideInstallButton();
            this.showWelcomeMessage();
        });
    }

    createMobileInterface() {
        if (!this.isMobile) return;

        // Create mobile navigation
        this.createMobileNav();
        
        // Create quick action bar
        this.createQuickActionBar();
        
        // Create mobile-optimized modals
        this.optimizeModals();
        
        // Add mobile-specific styles
        this.addMobileStyles();
    }

    createMobileNav() {
        const mobileNav = document.createElement('div');
        mobileNav.id = 'mobileNav';
        mobileNav.className = 'hidden md:hidden fixed bottom-0 left-0 right-0 bg-white dark:bg-gray-800 border-t border-gray-200 dark:border-gray-700 z-50';
        
        mobileNav.innerHTML = `
            <div class="flex justify-around py-2">
                <a href="/dashboard" class="flex flex-col items-center py-2 px-3 text-gray-600 dark:text-gray-400 hover:text-blue-600 dark:hover:text-blue-400">
                    <i class="fas fa-home text-lg"></i>
                    <span class="text-xs mt-1">Home</span>
                </a>
                <a href="/patients" class="flex flex-col items-center py-2 px-3 text-gray-600 dark:text-gray-400 hover:text-blue-600 dark:hover:text-blue-400">
                    <i class="fas fa-users text-lg"></i>
                    <span class="text-xs mt-1">Patients</span>
                </a>
                <button onclick="openTestPanelWizard()" class="flex flex-col items-center py-2 px-3 text-gray-600 dark:text-gray-400 hover:text-blue-600 dark:hover:text-blue-400">
                    <i class="fas fa-flask text-lg"></i>
                    <span class="text-xs mt-1">Tests</span>
                </button>
                <a href="/reports" class="flex flex-col items-center py-2 px-3 text-gray-600 dark:text-gray-400 hover:text-blue-600 dark:hover:text-blue-400">
                    <i class="fas fa-chart-bar text-lg"></i>
                    <span class="text-xs mt-1">Reports</span>
                </a>
                <button onclick="mobileAppCompanion.openMobileMenu()" class="flex flex-col items-center py-2 px-3 text-gray-600 dark:text-gray-400 hover:text-blue-600 dark:hover:text-blue-400">
                    <i class="fas fa-ellipsis-h text-lg"></i>
                    <span class="text-xs mt-1">More</span>
                </button>
            </div>
        `;

        document.body.appendChild(mobileNav);
        
        // Show mobile nav on mobile devices
        if (this.isMobile) {
            mobileNav.classList.remove('hidden');
            // Add bottom padding to main content
            document.body.style.paddingBottom = '80px';
        }
    }

    createQuickActionBar() {
        const quickActions = document.createElement('div');
        quickActions.id = 'mobileQuickActions';
        quickActions.className = 'hidden md:hidden fixed top-16 left-0 right-0 bg-gradient-to-r from-blue-600 to-purple-600 text-white p-3 z-40';
        
        quickActions.innerHTML = `
            <div class="flex space-x-3 overflow-x-auto">
                <button onclick="openTestPanelWizard()" class="flex-shrink-0 bg-white bg-opacity-20 rounded-lg px-4 py-2 text-sm font-medium">
                    <i class="fas fa-magic mr-2"></i>AI Tests
                </button>
                <button onclick="mobileAppCompanion.quickAddPatient()" class="flex-shrink-0 bg-white bg-opacity-20 rounded-lg px-4 py-2 text-sm font-medium">
                    <i class="fas fa-user-plus mr-2"></i>Add Patient
                </button>
                <button onclick="realTimeCollaboration.toggle()" class="flex-shrink-0 bg-white bg-opacity-20 rounded-lg px-4 py-2 text-sm font-medium">
                    <i class="fas fa-users mr-2"></i>Collaborate
                </button>
                <button onclick="mobileAppCompanion.scanQR()" class="flex-shrink-0 bg-white bg-opacity-20 rounded-lg px-4 py-2 text-sm font-medium">
                    <i class="fas fa-qrcode mr-2"></i>Scan
                </button>
            </div>
        `;

        document.body.appendChild(quickActions);
        
        if (this.isMobile) {
            quickActions.classList.remove('hidden');
        }
    }

    optimizeModals() {
        // Make modals full-screen on mobile
        const style = document.createElement('style');
        style.textContent = `
            @media (max-width: 768px) {
                .mobile-optimized-modal {
                    position: fixed !important;
                    inset: 0 !important;
                    margin: 0 !important;
                    max-width: none !important;
                    max-height: none !important;
                    border-radius: 0 !important;
                }
                
                .mobile-optimized-modal .modal-content {
                    height: 100vh;
                    overflow-y: auto;
                }
            }
        `;
        document.head.appendChild(style);
    }

    addMobileStyles() {
        const style = document.createElement('style');
        style.textContent = `
            @media (max-width: 768px) {
                /* Touch-friendly buttons */
                button, .btn {
                    min-height: 44px;
                    min-width: 44px;
                }
                
                /* Larger form inputs */
                input[type="text"], input[type="email"], input[type="password"], 
                select, textarea {
                    font-size: 16px;
                    padding: 12px;
                }
                
                /* Improved table scrolling */
                .table-container {
                    overflow-x: auto;
                    -webkit-overflow-scrolling: touch;
                }
                
                /* Better spacing for mobile */
                .mobile-padding {
                    padding: 1rem;
                }
                
                /* Swipe gestures visual feedback */
                .swipe-action {
                    position: relative;
                    overflow: hidden;
                }
                
                .swipe-action::before {
                    content: '';
                    position: absolute;
                    top: 0;
                    left: -100%;
                    width: 100%;
                    height: 100%;
                    background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent);
                    transition: left 0.3s ease;
                }
                
                .swipe-action.swiping::before {
                    left: 100%;
                }
            }
        `;
        document.head.appendChild(style);
    }

    showInstallButton() {
        if (this.isInstalled || !this.isMobile) return;

        const installButton = document.createElement('div');
        installButton.id = 'installPrompt';
        installButton.className = 'fixed top-4 left-4 right-4 bg-blue-600 text-white p-4 rounded-lg shadow-lg z-50 flex items-center justify-between';
        
        installButton.innerHTML = `
            <div class="flex items-center">
                <i class="fas fa-mobile-alt text-xl mr-3"></i>
                <div>
                    <p class="font-medium">Install MedLab Pro</p>
                    <p class="text-sm text-blue-100">Add to home screen for quick access</p>
                </div>
            </div>
            <div class="flex space-x-2">
                <button onclick="mobileAppCompanion.installApp()" class="bg-white text-blue-600 px-4 py-2 rounded font-medium">
                    Install
                </button>
                <button onclick="mobileAppCompanion.dismissInstall()" class="text-blue-100 hover:text-white">
                    <i class="fas fa-times"></i>
                </button>
            </div>
        `;

        document.body.appendChild(installButton);
    }

    hideInstallButton() {
        const installButton = document.getElementById('installPrompt');
        if (installButton) {
            installButton.remove();
        }
    }

    async installApp() {
        if (!this.deferredPrompt) return;

        this.deferredPrompt.prompt();
        const { outcome } = await this.deferredPrompt.userChoice;
        
        if (outcome === 'accepted') {
            this.isInstalled = true;
        }
        
        this.deferredPrompt = null;
        this.hideInstallButton();
    }

    dismissInstall() {
        this.hideInstallButton();
        localStorage.setItem('installDismissed', 'true');
    }

    showWelcomeMessage() {
        if (window.smartNotifications) {
            window.smartNotifications.showCustomNotification(
                'success',
                'Welcome to MedLab Pro!',
                'App installed successfully. Enjoy the enhanced mobile experience!'
            );
        }
    }

    openMobileMenu() {
        const menu = document.createElement('div');
        menu.id = 'mobileMenuOverlay';
        menu.className = 'fixed inset-0 bg-black bg-opacity-50 z-50 flex items-end';
        
        menu.innerHTML = `
            <div class="bg-white dark:bg-gray-800 w-full rounded-t-xl p-6 transform transition-transform duration-300 translate-y-full">
                <div class="flex items-center justify-between mb-6">
                    <h3 class="text-lg font-semibold text-gray-900 dark:text-white">Quick Actions</h3>
                    <button onclick="mobileAppCompanion.closeMobileMenu()" class="text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200">
                        <i class="fas fa-times text-xl"></i>
                    </button>
                </div>
                
                <div class="grid grid-cols-2 gap-4">
                    <button onclick="openPatientJourney('demo', 'Demo Patient')" class="flex flex-col items-center p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
                        <i class="fas fa-route text-blue-600 dark:text-blue-400 text-2xl mb-2"></i>
                        <span class="text-sm font-medium text-gray-900 dark:text-white">Patient Journey</span>
                    </button>
                    
                    <button onclick="generatePDFReport({})" class="flex flex-col items-center p-4 bg-purple-50 dark:bg-purple-900/20 rounded-lg">
                        <i class="fas fa-file-pdf text-purple-600 dark:text-purple-400 text-2xl mb-2"></i>
                        <span class="text-sm font-medium text-gray-900 dark:text-white">PDF Reports</span>
                    </button>
                    
                    <button onclick="realTimeCollaboration.toggle()" class="flex flex-col items-center p-4 bg-green-50 dark:bg-green-900/20 rounded-lg">
                        <i class="fas fa-users text-green-600 dark:text-green-400 text-2xl mb-2"></i>
                        <span class="text-sm font-medium text-gray-900 dark:text-white">Collaboration</span>
                    </button>
                    
                    <button onclick="toggleContextualHelp()" class="flex flex-col items-center p-4 bg-yellow-50 dark:bg-yellow-900/20 rounded-lg">
                        <i class="fas fa-question-circle text-yellow-600 dark:text-yellow-400 text-2xl mb-2"></i>
                        <span class="text-sm font-medium text-gray-900 dark:text-white">Medical Help</span>
                    </button>
                    
                    <button onclick="mobileAppCompanion.shareApp()" class="flex flex-col items-center p-4 bg-indigo-50 dark:bg-indigo-900/20 rounded-lg">
                        <i class="fas fa-share text-indigo-600 dark:text-indigo-400 text-2xl mb-2"></i>
                        <span class="text-sm font-medium text-gray-900 dark:text-white">Share App</span>
                    </button>
                    
                    <button onclick="mobileAppCompanion.goOffline()" class="flex flex-col items-center p-4 bg-gray-50 dark:bg-gray-700 rounded-lg">
                        <i class="fas fa-wifi-slash text-gray-600 dark:text-gray-400 text-2xl mb-2"></i>
                        <span class="text-sm font-medium text-gray-900 dark:text-white">Offline Mode</span>
                    </button>
                </div>
                
                <div class="mt-6 pt-6 border-t border-gray-200 dark:border-gray-600">
                    <div class="flex items-center justify-between text-sm text-gray-600 dark:text-gray-400">
                        <span>App Version: 1.0.0</span>
                        <span>Connection: ${navigator.onLine ? 'Online' : 'Offline'}</span>
                    </div>
                </div>
            </div>
        `;

        document.body.appendChild(menu);
        
        // Animate in
        setTimeout(() => {
            menu.querySelector('div').classList.remove('translate-y-full');
        }, 10);
        
        // Close on backdrop click
        menu.addEventListener('click', (e) => {
            if (e.target === menu) {
                this.closeMobileMenu();
            }
        });
    }

    closeMobileMenu() {
        const menu = document.getElementById('mobileMenuOverlay');
        if (menu) {
            menu.querySelector('div').classList.add('translate-y-full');
            setTimeout(() => menu.remove(), 300);
        }
    }

    quickAddPatient() {
        // Open a simplified patient registration form for mobile
        const form = document.createElement('div');
        form.id = 'mobilePatientForm';
        form.className = 'fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4';
        
        form.innerHTML = `
            <div class="bg-white dark:bg-gray-800 rounded-xl w-full max-w-md p-6">
                <div class="flex items-center justify-between mb-6">
                    <h3 class="text-lg font-semibold text-gray-900 dark:text-white">Quick Add Patient</h3>
                    <button onclick="mobileAppCompanion.closeQuickForm()" class="text-gray-500 hover:text-gray-700 dark:text-gray-400">
                        <i class="fas fa-times"></i>
                    </button>
                </div>
                
                <form class="space-y-4">
                    <div>
                        <input type="text" placeholder="First Name" class="w-full px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white text-base">
                    </div>
                    <div>
                        <input type="text" placeholder="Last Name" class="w-full px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white text-base">
                    </div>
                    <div>
                        <input type="tel" placeholder="Phone Number" class="w-full px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white text-base">
                    </div>
                    <div>
                        <input type="date" placeholder="Date of Birth" class="w-full px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white text-base">
                    </div>
                    <button type="submit" class="w-full bg-blue-600 text-white py-3 rounded-lg font-medium hover:bg-blue-700 transition-colors">
                        Add Patient
                    </button>
                </form>
            </div>
        `;

        document.body.appendChild(form);
    }

    closeQuickForm() {
        const form = document.getElementById('mobilePatientForm');
        if (form) form.remove();
    }

    scanQR() {
        // Simulate QR code scanning for patient identification
        if (window.smartNotifications) {
            window.smartNotifications.showCustomNotification(
                'info',
                'QR Scanner',
                'QR code scanning feature would open camera here'
            );
        }
    }

    shareApp() {
        if (navigator.share) {
            navigator.share({
                title: 'MedLab Pro',
                text: 'Professional laboratory management system',
                url: window.location.origin
            });
        } else {
            // Fallback for browsers without Web Share API
            const url = window.location.origin;
            navigator.clipboard.writeText(url).then(() => {
                if (window.smartNotifications) {
                    window.smartNotifications.showCustomNotification(
                        'success',
                        'Link Copied',
                        'App link copied to clipboard'
                    );
                }
            });
        }
    }

    goOffline() {
        // Toggle offline mode
        if (window.smartNotifications) {
            window.smartNotifications.showCustomNotification(
                'info',
                'Offline Mode',
                'Offline capabilities would be enabled here'
            );
        }
    }

    optimizeForMobile() {
        if (!this.isMobile) return;

        // Add mobile-specific meta tags
        const viewport = document.querySelector('meta[name="viewport"]');
        if (viewport) {
            viewport.content = 'width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no';
        }

        // Prevent zoom on input focus
        document.addEventListener('focusin', (e) => {
            if (e.target.matches('input, select, textarea')) {
                document.querySelector('meta[name="viewport"]').content = 'width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no';
            }
        });

        document.addEventListener('focusout', (e) => {
            if (e.target.matches('input, select, textarea')) {
                document.querySelector('meta[name="viewport"]').content = 'width=device-width, initial-scale=1.0';
            }
        });

        // Add swipe gestures
        this.addSwipeGestures();
        
        // Optimize touch interactions
        this.optimizeTouchInteractions();
    }

    addSwipeGestures() {
        let startX, startY, startTime;
        
        document.addEventListener('touchstart', (e) => {
            startX = e.touches[0].clientX;
            startY = e.touches[0].clientY;
            startTime = Date.now();
        });

        document.addEventListener('touchend', (e) => {
            if (!startX || !startY) return;

            const endX = e.changedTouches[0].clientX;
            const endY = e.changedTouches[0].clientY;
            const diffX = startX - endX;
            const diffY = startY - endY;
            const diffTime = Date.now() - startTime;

            // Only register swipes that are fast enough and long enough
            if (diffTime < 1000 && Math.abs(diffX) > 50 && Math.abs(diffY) < 100) {
                if (diffX > 0) {
                    // Swipe left - next page or action
                    this.handleSwipeLeft();
                } else {
                    // Swipe right - previous page or action
                    this.handleSwipeRight();
                }
            }

            startX = startY = null;
        });
    }

    handleSwipeLeft() {
        // Implement swipe left functionality
        console.log('Swipe left detected');
    }

    handleSwipeRight() {
        // Implement swipe right functionality
        console.log('Swipe right detected');
    }

    optimizeTouchInteractions() {
        // Add touch feedback to interactive elements
        const style = document.createElement('style');
        style.textContent = `
            .touch-feedback {
                transition: transform 0.1s ease;
            }
            
            .touch-feedback:active {
                transform: scale(0.95);
            }
            
            @media (max-width: 768px) {
                button, .btn, a[role="button"] {
                    position: relative;
                    overflow: hidden;
                }
                
                button::after, .btn::after, a[role="button"]::after {
                    content: '';
                    position: absolute;
                    top: 50%;
                    left: 50%;
                    width: 0;
                    height: 0;
                    border-radius: 50%;
                    background: rgba(255, 255, 255, 0.3);
                    transform: translate(-50%, -50%);
                    transition: width 0.3s ease, height 0.3s ease;
                }
                
                button:active::after, .btn:active::after, a[role="button"]:active::after {
                    width: 200px;
                    height: 200px;
                }
            }
        `;
        document.head.appendChild(style);

        // Add touch feedback class to interactive elements
        document.querySelectorAll('button, .btn, a[role="button"]').forEach(el => {
            el.classList.add('touch-feedback');
        });
    }

    setupEventListeners() {
        // Online/offline detection
        window.addEventListener('online', () => {
            if (window.smartNotifications) {
                window.smartNotifications.showCustomNotification(
                    'success',
                    'Back Online',
                    'Connection restored'
                );
            }
        });

        window.addEventListener('offline', () => {
            if (window.smartNotifications) {
                window.smartNotifications.showCustomNotification(
                    'warning',
                    'Offline Mode',
                    'Limited functionality available'
                );
            }
        });

        // Orientation change
        window.addEventListener('orientationchange', () => {
            setTimeout(() => {
                // Recalculate layout after orientation change
                this.optimizeLayout();
            }, 100);
        });
    }

    optimizeLayout() {
        // Adjust layout based on orientation and screen size
        const isLandscape = window.innerWidth > window.innerHeight;
        document.body.classList.toggle('landscape', isLandscape);
        document.body.classList.toggle('portrait', !isLandscape);
    }

    // Public API methods
    static isMobileDevice() {
        return window.mobileAppCompanion?.isMobile || false;
    }

    static isAppInstalled() {
        return window.mobileAppCompanion?.isInstalled || false;
    }

    static showMobileNotification(title, message, type = 'info') {
        if (window.smartNotifications) {
            window.smartNotifications.showCustomNotification(type, title, message);
        }
    }
}

// Initialize global instance
window.mobileAppCompanion = new MobileAppCompanion();

// Global functions for template use
function isMobileDevice() {
    return MobileAppCompanion.isMobileDevice();
}

function showMobileNotification(title, message, type = 'info') {
    MobileAppCompanion.showMobileNotification(title, message, type);
}