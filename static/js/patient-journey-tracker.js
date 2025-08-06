/**
 * Animated Patient Journey Progress Tracker
 * Visual timeline showing patient's testing journey with real-time updates
 */

class PatientJourneyTracker {
    constructor() {
        this.journeySteps = [
            { id: 'registration', name: 'Registration', icon: 'fas fa-user-plus', description: 'Patient registered' },
            { id: 'consultation', name: 'Consultation', icon: 'fas fa-stethoscope', description: 'Medical consultation' },
            { id: 'test_order', name: 'Test Ordered', icon: 'fas fa-clipboard-list', description: 'Tests ordered by physician' },
            { id: 'sample_collection', name: 'Sample Collection', icon: 'fas fa-vial', description: 'Samples collected' },
            { id: 'laboratory_processing', name: 'Lab Processing', icon: 'fas fa-microscope', description: 'Tests being processed' },
            { id: 'quality_control', name: 'Quality Control', icon: 'fas fa-check-double', description: 'Results verified' },
            { id: 'results_ready', name: 'Results Ready', icon: 'fas fa-file-medical-alt', description: 'Results available' },
            { id: 'physician_review', name: 'Physician Review', icon: 'fas fa-user-md', description: 'Doctor reviewing results' },
            { id: 'report_delivery', name: 'Report Delivered', icon: 'fas fa-paper-plane', description: 'Final report sent' }
        ];
        this.currentPatientJourney = {};
        this.init();
    }

    init() {
        this.createJourneyWidget();
        this.setupEventListeners();
    }

    createJourneyWidget() {
        if (document.getElementById('patientJourneyTracker')) return;

        const widget = document.createElement('div');
        widget.id = 'patientJourneyTracker';
        widget.className = 'hidden fixed top-20 right-4 w-80 bg-white dark:bg-gray-800 rounded-xl shadow-2xl border border-gray-200 dark:border-gray-700 z-40 max-h-[80vh] overflow-hidden';
        
        widget.innerHTML = `
            <!-- Header -->
            <div class="bg-gradient-to-r from-blue-600 to-purple-600 text-white p-4">
                <div class="flex items-center justify-between">
                    <div>
                        <h3 class="font-semibold">Patient Journey</h3>
                        <p class="text-xs text-blue-100" id="journeyPatientName">Select a patient</p>
                    </div>
                    <button onclick="patientJourneyTracker.close()" class="text-white hover:text-gray-200">
                        <i class="fas fa-times"></i>
                    </button>
                </div>
                
                <!-- Progress Overview -->
                <div class="mt-3">
                    <div class="flex justify-between text-xs text-blue-100 mb-1">
                        <span>Progress</span>
                        <span id="journeyProgress">0%</span>
                    </div>
                    <div class="w-full bg-blue-700 rounded-full h-2">
                        <div id="journeyProgressBar" class="bg-white rounded-full h-2 transition-all duration-500" style="width: 0%"></div>
                    </div>
                </div>
            </div>

            <!-- Journey Timeline -->
            <div class="p-4 overflow-y-auto max-h-96">
                <div id="journeyTimeline" class="space-y-4">
                    ${this.generateTimelineHTML()}
                </div>
            </div>

            <!-- Actions -->
            <div class="border-t border-gray-200 dark:border-gray-600 p-4">
                <button onclick="patientJourneyTracker.refreshJourney()" 
                        class="w-full px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors text-sm">
                    <i class="fas fa-sync-alt mr-2"></i>Refresh Status
                </button>
            </div>
        `;

        document.body.appendChild(widget);
    }

    generateTimelineHTML() {
        return this.journeySteps.map((step, index) => `
            <div id="step-${step.id}" class="journey-step flex items-start group">
                <!-- Step Icon -->
                <div class="flex-shrink-0 relative">
                    <div class="w-10 h-10 rounded-full border-2 flex items-center justify-center transition-all duration-300
                                border-gray-300 bg-gray-100 text-gray-400
                                step-icon-${step.id}">
                        <i class="${step.icon} text-sm"></i>
                    </div>
                    
                    <!-- Connecting Line -->
                    ${index < this.journeySteps.length - 1 ? `
                        <div class="absolute top-10 left-1/2 transform -translate-x-1/2 w-0.5 h-8 
                                    bg-gray-300 dark:bg-gray-600 transition-all duration-500
                                    step-line-${step.id}"></div>
                    ` : ''}
                </div>

                <!-- Step Content -->
                <div class="ml-4 flex-1 min-w-0">
                    <div class="flex items-center justify-between">
                        <h4 class="text-sm font-medium text-gray-900 dark:text-white group-hover:text-blue-600 dark:group-hover:text-blue-400 transition-colors">
                            ${step.name}
                        </h4>
                        <div class="step-status-${step.id}">
                            <!-- Status indicator will be inserted here -->
                        </div>
                    </div>
                    <p class="text-xs text-gray-500 dark:text-gray-400 mt-1">${step.description}</p>
                    <div class="step-timestamp-${step.id} text-xs text-gray-400 mt-1 hidden">
                        <!-- Timestamp will be inserted here -->
                    </div>
                </div>
            </div>
        `).join('');
    }

    open(patientId, patientName = 'Unknown Patient') {
        this.currentPatientId = patientId;
        document.getElementById('journeyPatientName').textContent = patientName;
        document.getElementById('patientJourneyTracker').classList.remove('hidden');
        this.loadPatientJourney(patientId);
    }

    close() {
        document.getElementById('patientJourneyTracker').classList.add('hidden');
        this.currentPatientId = null;
    }

    async loadPatientJourney(patientId) {
        try {
            // Show loading state
            this.showLoadingState();

            // Simulate API call to get patient journey data
            await new Promise(resolve => setTimeout(resolve, 1000));

            // Mock journey data
            this.currentPatientJourney = {
                patientId: patientId,
                steps: {
                    'registration': { status: 'completed', timestamp: '2024-08-01 09:00:00', duration: 5 },
                    'consultation': { status: 'completed', timestamp: '2024-08-01 09:30:00', duration: 15 },
                    'test_order': { status: 'completed', timestamp: '2024-08-01 09:45:00', duration: 2 },
                    'sample_collection': { status: 'completed', timestamp: '2024-08-01 10:00:00', duration: 10 },
                    'laboratory_processing': { status: 'in_progress', timestamp: '2024-08-01 10:15:00', estimatedCompletion: '2024-08-01 14:00:00' },
                    'quality_control': { status: 'pending' },
                    'results_ready': { status: 'pending' },
                    'physician_review': { status: 'pending' },
                    'report_delivery': { status: 'pending' }
                }
            };

            this.updateJourneyDisplay();

        } catch (error) {
            console.error('Error loading patient journey:', error);
            this.showErrorState();
        }
    }

    updateJourneyDisplay() {
        const journeyData = this.currentPatientJourney;
        let completedSteps = 0;
        let totalSteps = this.journeySteps.length;

        this.journeySteps.forEach((step, index) => {
            const stepData = journeyData.steps[step.id];
            this.updateStepDisplay(step, stepData, index);

            if (stepData && stepData.status === 'completed') {
                completedSteps++;
            }
        });

        // Update progress bar
        const progress = (completedSteps / totalSteps) * 100;
        document.getElementById('journeyProgress').textContent = `${Math.round(progress)}%`;
        document.getElementById('journeyProgressBar').style.width = `${progress}%`;
    }

    updateStepDisplay(step, stepData, index) {
        const iconElement = document.querySelector(`.step-icon-${step.id}`);
        const statusElement = document.querySelector(`.step-status-${step.id}`);
        const timestampElement = document.querySelector(`.step-timestamp-${step.id}`);
        const lineElement = document.querySelector(`.step-line-${step.id}`);

        if (!stepData) {
            return; // Step not started
        }

        // Update icon and status based on step status
        switch (stepData.status) {
            case 'completed':
                iconElement.className = iconElement.className.replace(
                    'border-gray-300 bg-gray-100 text-gray-400',
                    'border-green-500 bg-green-500 text-white'
                );
                statusElement.innerHTML = '<i class="fas fa-check text-green-500 text-sm"></i>';
                timestampElement.textContent = `Completed: ${this.formatTimestamp(stepData.timestamp)}`;
                timestampElement.classList.remove('hidden');
                
                // Animate the connecting line
                if (lineElement) {
                    lineElement.classList.add('bg-green-500');
                    lineElement.classList.remove('bg-gray-300', 'dark:bg-gray-600');
                }
                break;

            case 'in_progress':
                iconElement.className = iconElement.className.replace(
                    'border-gray-300 bg-gray-100 text-gray-400',
                    'border-blue-500 bg-blue-500 text-white'
                );
                iconElement.innerHTML = `<i class="fas fa-spinner fa-spin text-sm"></i>`;
                statusElement.innerHTML = '<div class="flex items-center"><div class="w-2 h-2 bg-blue-500 rounded-full animate-pulse"></div><span class="text-xs text-blue-600 ml-1">In Progress</span></div>';
                
                if (stepData.timestamp) {
                    timestampElement.textContent = `Started: ${this.formatTimestamp(stepData.timestamp)}`;
                    timestampElement.classList.remove('hidden');
                }
                
                if (stepData.estimatedCompletion) {
                    const eta = document.createElement('div');
                    eta.className = 'text-xs text-blue-600 mt-1';
                    eta.textContent = `ETA: ${this.formatTimestamp(stepData.estimatedCompletion)}`;
                    timestampElement.appendChild(eta);
                }
                break;

            case 'pending':
                iconElement.className = iconElement.className.replace(
                    'border-gray-300 bg-gray-100 text-gray-400',
                    'border-gray-300 bg-gray-100 text-gray-400'
                );
                statusElement.innerHTML = '<span class="text-xs text-gray-400">Pending</span>';
                break;

            case 'delayed':
                iconElement.className = iconElement.className.replace(
                    'border-gray-300 bg-gray-100 text-gray-400',
                    'border-yellow-500 bg-yellow-500 text-white'
                );
                statusElement.innerHTML = '<i class="fas fa-clock text-yellow-500 text-sm"></i>';
                timestampElement.textContent = `Delayed since: ${this.formatTimestamp(stepData.timestamp)}`;
                timestampElement.classList.remove('hidden');
                break;

            case 'error':
                iconElement.className = iconElement.className.replace(
                    'border-gray-300 bg-gray-100 text-gray-400',
                    'border-red-500 bg-red-500 text-white'
                );
                statusElement.innerHTML = '<i class="fas fa-exclamation-triangle text-red-500 text-sm"></i>';
                timestampElement.textContent = `Error occurred: ${this.formatTimestamp(stepData.timestamp)}`;
                timestampElement.classList.remove('hidden');
                break;
        }

        // Add step completion animation
        if (stepData.status === 'completed') {
            setTimeout(() => {
                iconElement.classList.add('animate-pulse');
                setTimeout(() => {
                    iconElement.classList.remove('animate-pulse');
                }, 1000);
            }, index * 200);
        }
    }

    formatTimestamp(timestamp) {
        const date = new Date(timestamp);
        return date.toLocaleString('en-US', {
            month: 'short',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
    }

    showLoadingState() {
        const timeline = document.getElementById('journeyTimeline');
        timeline.innerHTML = `
            <div class="text-center py-8">
                <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
                <p class="text-gray-600 dark:text-gray-400 mt-4 text-sm">Loading patient journey...</p>
            </div>
        `;
    }

    showErrorState() {
        const timeline = document.getElementById('journeyTimeline');
        timeline.innerHTML = `
            <div class="text-center py-8">
                <i class="fas fa-exclamation-triangle text-red-500 text-2xl"></i>
                <p class="text-gray-600 dark:text-gray-400 mt-4 text-sm">Error loading journey data</p>
                <button onclick="patientJourneyTracker.refreshJourney()" 
                        class="mt-2 px-4 py-2 bg-blue-600 text-white rounded text-sm hover:bg-blue-700">
                    Try Again
                </button>
            </div>
        `;
    }

    refreshJourney() {
        if (this.currentPatientId) {
            this.loadPatientJourney(this.currentPatientId);
        }
    }

    // Method to update a specific step (called by external events)
    updateStepStatus(stepId, status, timestamp = null, additionalData = {}) {
        if (!this.currentPatientJourney.steps) {
            this.currentPatientJourney.steps = {};
        }

        this.currentPatientJourney.steps[stepId] = {
            status: status,
            timestamp: timestamp || new Date().toISOString(),
            ...additionalData
        };

        this.updateJourneyDisplay();

        // Show notification for step completion
        if (status === 'completed') {
            const step = this.journeySteps.find(s => s.id === stepId);
            if (step && window.smartNotifications) {
                window.smartNotifications.showCustomNotification(
                    'success',
                    'Step Completed',
                    `${step.name} has been completed`
                );
            }
        }
    }

    // Method to simulate real-time updates
    simulateRealTimeUpdates() {
        // This would normally connect to WebSocket or polling mechanism
        setInterval(() => {
            if (this.currentPatientId && this.currentPatientJourney.steps) {
                // Simulate progress
                const inProgressStep = Object.keys(this.currentPatientJourney.steps)
                    .find(stepId => this.currentPatientJourney.steps[stepId].status === 'in_progress');

                if (inProgressStep === 'laboratory_processing') {
                    // Simulate completion after some time
                    const startTime = new Date(this.currentPatientJourney.steps[inProgressStep].timestamp);
                    const now = new Date();
                    const elapsed = (now - startTime) / 1000 / 60; // minutes

                    if (elapsed > 5) { // Simulate 5 minute processing
                        this.updateStepStatus('laboratory_processing', 'completed');
                        this.updateStepStatus('quality_control', 'in_progress');
                    }
                }
            }
        }, 30000); // Check every 30 seconds
    }

    setupEventListeners() {
        // Listen for journey update events
        document.addEventListener('patientJourneyUpdate', (event) => {
            const { patientId, stepId, status, timestamp, additionalData } = event.detail;
            
            if (patientId === this.currentPatientId) {
                this.updateStepStatus(stepId, status, timestamp, additionalData);
            }
        });

        // Close when clicking outside
        document.addEventListener('click', (event) => {
            const tracker = document.getElementById('patientJourneyTracker');
            if (tracker && !tracker.contains(event.target) && !tracker.classList.contains('hidden')) {
                // Don't auto-close, let user manually close
            }
        });
    }

    // Public API methods
    static updatePatientStep(patientId, stepId, status, additionalData = {}) {
        const event = new CustomEvent('patientJourneyUpdate', {
            detail: {
                patientId,
                stepId,
                status,
                timestamp: new Date().toISOString(),
                additionalData
            }
        });
        document.dispatchEvent(event);
    }

    static openForPatient(patientId, patientName) {
        if (window.patientJourneyTracker) {
            window.patientJourneyTracker.open(patientId, patientName);
        }
    }
}

// Initialize global instance
window.patientJourneyTracker = new PatientJourneyTracker();

// Global functions for template use
function openPatientJourney(patientId, patientName = 'Unknown Patient') {
    window.patientJourneyTracker.open(patientId, patientName);
}

function updatePatientJourneyStep(patientId, stepId, status) {
    PatientJourneyTracker.updatePatientStep(patientId, stepId, status);
}