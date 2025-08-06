// MedLab Pro JavaScript - Simple Working Version
console.log('Loading MedLab Pro JavaScript - Simple Version');

// Simple initialization without complex class structure
document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM loaded, initializing MedLab Pro...');
    initializeMedLab();
});

function initializeMedLab() {
    console.log('Initializing MedLab Pro...');
    
    // Initialize interactions first
    console.log('Initializing interactions...');
    initializeInteractions();
    
    // Initialize modals
    console.log('Initializing modals...');
    initializeModals();
    
    // Initialize charts with error handling
    console.log('Initializing charts...');
    setTimeout(function() {
        try {
            initializeCharts();
        } catch (e) {
            console.warn('Charts initialization failed:', e);
        }
    }, 100);
}

// Add missing method for compatibility
function initPageCharts() {
    console.log('Legacy initPageCharts method called - delegating to initializeCharts');
    try {
        initializeCharts();
    } catch (e) {
        console.warn('Page charts initialization failed:', e);
    }
}

function initializeCharts() {
    console.log('Initializing charts...');
    
    // Dashboard charts
    const testDistCtx = document.getElementById('testDistributionChart');
    if (testDistCtx) {
        try {
            new Chart(testDistCtx, {
                type: 'doughnut',
                data: {
                    labels: ['Blood Tests', 'Urine Tests', 'Other Tests'],
                    datasets: [{
                        data: [60, 25, 15],
                        backgroundColor: ['#3b82f6', '#10b981', '#f59e0b'],
                        borderWidth: 2,
                        borderColor: '#ffffff'
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            position: 'bottom'
                        }
                    }
                }
            });
            console.log('Test distribution chart initialized');
        } catch (e) {
            console.warn('Test distribution chart failed:', e);
        }
    }

    // Monthly trends chart
    const monthlyCtx = document.getElementById('monthlyTrendsChart');
    if (monthlyCtx) {
        try {
            new Chart(monthlyCtx, {
                type: 'line',
                data: {
                    labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
                    datasets: [{
                        label: 'Tests',
                        data: [120, 190, 300, 500, 200, 300],
                        borderColor: '#3b82f6',
                        backgroundColor: 'rgba(59, 130, 246, 0.1)',
                        tension: 0.1,
                        fill: true
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        y: {
                            beginAtZero: true
                        }
                    }
                }
            });
            console.log('Monthly trends chart initialized');
        } catch (e) {
            console.warn('Monthly trends chart failed:', e);
        }
    }

    // Tests page charts
    const testsCtx = document.getElementById('testsChart');
    if (testsCtx) {
        try {
            new Chart(testsCtx, {
                type: 'bar',
                data: {
                    labels: ['Normal', 'Abnormal', 'Critical'],
                    datasets: [{
                        data: [12, 4, 1],
                        backgroundColor: ['#10b981', '#f59e0b', '#ef4444'],
                        borderRadius: 8
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            display: false
                        }
                    }
                }
            });
            console.log('Tests chart initialized');
        } catch (e) {
            console.warn('Tests chart failed:', e);
        }
    }
}

function initializeInteractions() {
    console.log('Initializing interactions...');
    
    // Initialize modal functionality
    initializeModals();
    
    // Blood test checkboxes
    const bloodTestCheckboxes = document.querySelectorAll('.blood-test-checkbox');
    if (bloodTestCheckboxes.length > 0) {
        console.log(`Found ${bloodTestCheckboxes.length} blood test checkboxes`);
        bloodTestCheckboxes.forEach(function(checkbox) {
            checkbox.addEventListener('change', function(e) {
                console.log(`Blood test ${e.target.value} ${e.target.checked ? 'selected' : 'deselected'}`);
            });
        });
    }
    
    // Test checkboxes
    const testCheckboxes = document.querySelectorAll('.test-checkbox');
    if (testCheckboxes.length > 0) {
        console.log(`Found ${testCheckboxes.length} test checkboxes`);
        testCheckboxes.forEach(function(checkbox) {
            checkbox.addEventListener('change', function(e) {
                const testId = e.target.value;
                const isChecked = e.target.checked;
                console.log(`Test ${testId} ${isChecked ? 'selected' : 'deselected'}`);
                
                // Update UI to show selection
                const panel = e.target.closest('.test-panel');
                if (panel) {
                    panel.classList.toggle('selected', isChecked);
                }
            });
        });
    }
}

// Global functions for template use
function loadPatientInfo() {
    console.log('Loading patient info...');
    const patientSelect = document.getElementById('bloodTestPatientSelect');
    const patientInfoDisplay = document.getElementById('patientInfoDisplay');
    const bloodTestSelection = document.getElementById('bloodTestSelection');
    
    if (!patientSelect || !patientSelect.value) {
        alert('Please select a patient first');
        return;
    }
    
    // Show patient info display
    if (patientInfoDisplay) {
        patientInfoDisplay.classList.remove('hidden');
    }
    
    // Show blood test selection
    if (bloodTestSelection) {
        bloodTestSelection.classList.remove('hidden');
    }
    
    // Populate patient info
    const patientInfoContent = document.getElementById('patientInfoContent');
    if (patientInfoContent) {
        patientInfoContent.innerHTML = `
            <div class="bg-white dark:bg-gray-700 p-4 rounded-lg">
                <h4 class="font-semibold text-gray-800 dark:text-gray-200">Patient Information</h4>
                <p class="text-gray-600 dark:text-gray-400">Patient ID: ${patientSelect.value}</p>
                <p class="text-gray-600 dark:text-gray-400">Name: ${patientSelect.options[patientSelect.selectedIndex].text}</p>
            </div>
        `;
    }
    
    console.log('Patient info loaded successfully');
}

function toggleLanguageMenu() {
    const menu = document.getElementById('languageMenu');
    if (menu) {
        menu.classList.toggle('hidden');
    }
}

function changeLanguage(lang) {
    console.log('Changing language to:', lang);
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
            console.log('Language changed successfully, reloading page...');
            window.location.reload();
        }
    })
    .catch(error => {
        console.error('Language change error:', error);
    });
}

function toggleUserMenu() {
    const menu = document.getElementById('userMenu');
    if (menu) {
        menu.classList.toggle('hidden');
    }
}

function toggleTheme() {
    document.documentElement.classList.toggle('dark');
    const isDark = document.documentElement.classList.contains('dark');
    localStorage.setItem('theme', isDark ? 'dark' : 'light');
}

// Initialize theme from localStorage
if (localStorage.getItem('theme') === 'dark') {
    document.documentElement.classList.add('dark');
}

// Close dropdowns when clicking outside
document.addEventListener('click', function(event) {
    const languageMenu = document.getElementById('languageMenu');
    const userMenu = document.getElementById('userMenu');
    const languageToggle = event.target.closest('[onclick="toggleLanguageMenu()"]');
    const userToggle = event.target.closest('[onclick="toggleUserMenu()"]');
    
    if (languageMenu && !languageToggle && !languageMenu.contains(event.target)) {
        languageMenu.classList.add('hidden');
    }
    
    if (userMenu && !userToggle && !userMenu.contains(event.target)) {
        userMenu.classList.add('hidden');
    }
});

console.log('MedLab Pro JavaScript fully loaded - Simple Version');

// Modal functionality
function initializeModals() {
    console.log('Initializing modals...');
    
    // Handle modal open buttons
    const modalButtons = document.querySelectorAll('[data-modal]');
    modalButtons.forEach(function(button) {
        button.addEventListener('click', function() {
            const modalId = this.getAttribute('data-modal');
            const modal = document.getElementById(modalId);
            if (modal) {
                modal.classList.remove('hidden');
                console.log('Opened modal:', modalId);
            }
        });
    });
    
    // Handle modal close buttons and overlay clicks
    const modals = document.querySelectorAll('.fixed.inset-0');
    modals.forEach(function(modal) {
        // Close button
        const closeBtn = modal.querySelector('[data-close-modal]');
        if (closeBtn) {
            closeBtn.addEventListener('click', function() {
                modal.classList.add('hidden');
                console.log('Closed modal via close button');
            });
        }
        
        // Overlay click
        modal.addEventListener('click', function(e) {
            if (e.target === modal) {
                modal.classList.add('hidden');
                console.log('Closed modal via overlay click');
            }
        });
    });
    
    // ESC key to close modals
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
            const openModal = document.querySelector('.fixed.inset-0:not(.hidden)');
            if (openModal) {
                openModal.classList.add('hidden');
                console.log('Closed modal via ESC key');
            }
        }
    });
}

// Import/Export functionality
function exportPatientData(patientId, format) {
    console.log('Exporting patient data:', patientId, format);
    
    // Create a form and submit it
    const form = document.createElement('form');
    form.method = 'POST';
    form.action = '/export-patient-data';
    
    const patientInput = document.createElement('input');
    patientInput.type = 'hidden';
    patientInput.name = 'patient_id';
    patientInput.value = patientId;
    
    const formatInput = document.createElement('input');
    formatInput.type = 'hidden';
    formatInput.name = 'format';
    formatInput.value = format;
    
    form.appendChild(patientInput);
    form.appendChild(formatInput);
    document.body.appendChild(form);
    form.submit();
    document.body.removeChild(form);
}

function viewPatientDetails(patientId) {
    console.log('Viewing patient details:', patientId);
    window.location.href = '/patient/' + patientId;
}

function handleFileUpload(input) {
    const file = input.files[0];
    if (file) {
        console.log('File selected:', file.name);
        
        // Show file info
        const fileInfo = input.parentElement.querySelector('.file-info');
        if (fileInfo) {
            fileInfo.textContent = `Selected: ${file.name} (${(file.size / 1024).toFixed(2)} KB)`;
            fileInfo.classList.remove('hidden');
        }
        
        // Enable submit button
        const submitBtn = document.querySelector('#importForm button[type="submit"]');
        if (submitBtn) {
            submitBtn.disabled = false;
            submitBtn.classList.remove('opacity-50', 'cursor-not-allowed');
        }
    }
}