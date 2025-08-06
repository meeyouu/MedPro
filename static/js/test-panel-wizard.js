/**
 * Interactive Test Panel Selection Wizard
 * Smart test panel recommendations based on patient symptoms and medical history
 */

class TestPanelWizard {
    constructor() {
        this.currentStep = 1;
        this.totalSteps = 4;
        this.selectedTests = new Set();
        this.patientData = {};
        this.recommendations = [];
        this.init();
    }

    init() {
        this.createWizardModal();
        this.loadTestPanels();
        this.setupEventListeners();
    }

    createWizardModal() {
        if (document.getElementById('testPanelWizard')) return;

        const modal = document.createElement('div');
        modal.id = 'testPanelWizard';
        modal.className = 'hidden fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4';
        
        modal.innerHTML = `
            <div class="bg-white dark:bg-gray-800 rounded-xl shadow-2xl max-w-4xl w-full max-h-[90vh] overflow-hidden">
                <!-- Header -->
                <div class="bg-gradient-to-r from-blue-600 to-purple-600 text-white p-6">
                    <div class="flex items-center justify-between">
                        <div>
                            <h2 class="text-2xl font-bold">Test Panel Selection Wizard</h2>
                            <p class="text-blue-100 mt-1">AI-powered test recommendations</p>
                        </div>
                        <button onclick="testPanelWizard.close()" class="text-white hover:text-gray-200">
                            <i class="fas fa-times text-xl"></i>
                        </button>
                    </div>
                    
                    <!-- Progress Bar -->
                    <div class="mt-6">
                        <div class="flex items-center justify-between text-sm text-blue-100 mb-2">
                            <span>Step <span id="currentStepNumber">1</span> of ${this.totalSteps}</span>
                            <span id="progressPercentage">25%</span>
                        </div>
                        <div class="w-full bg-blue-700 rounded-full h-2">
                            <div id="progressBar" class="bg-white rounded-full h-2 transition-all duration-300" style="width: 25%"></div>
                        </div>
                    </div>
                </div>

                <!-- Content -->
                <div id="wizardContent" class="p-6 overflow-y-auto max-h-[60vh]">
                    ${this.getStepContent(1)}
                </div>

                <!-- Footer -->
                <div class="bg-gray-50 dark:bg-gray-700 px-6 py-4 flex justify-between">
                    <button id="prevBtn" onclick="testPanelWizard.previousStep()" 
                            class="px-4 py-2 text-gray-600 dark:text-gray-300 hover:text-gray-800 dark:hover:text-white disabled:opacity-50" 
                            disabled>
                        <i class="fas fa-chevron-left mr-2"></i>Previous
                    </button>
                    <div class="flex space-x-3">
                        <button onclick="testPanelWizard.close()" 
                                class="px-4 py-2 text-gray-600 dark:text-gray-300 hover:text-gray-800 dark:hover:text-white">
                            Cancel
                        </button>
                        <button id="nextBtn" onclick="testPanelWizard.nextStep()" 
                                class="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors">
                            Next <i class="fas fa-chevron-right ml-2"></i>
                        </button>
                    </div>
                </div>
            </div>
        `;

        document.body.appendChild(modal);
    }

    getStepContent(step) {
        switch (step) {
            case 1:
                return this.getPatientInfoStep();
            case 2:
                return this.getSymptomsStep();
            case 3:
                return this.getRecommendationsStep();
            case 4:
                return this.getConfirmationStep();
            default:
                return '';
        }
    }

    getPatientInfoStep() {
        return `
            <div class="space-y-6">
                <div class="text-center mb-8">
                    <div class="w-16 h-16 bg-blue-100 dark:bg-blue-900 rounded-full flex items-center justify-center mx-auto mb-4">
                        <i class="fas fa-user-md text-blue-600 dark:text-blue-400 text-2xl"></i>
                    </div>
                    <h3 class="text-xl font-semibold text-gray-900 dark:text-white">Patient Information</h3>
                    <p class="text-gray-600 dark:text-gray-400">Basic patient details for personalized recommendations</p>
                </div>

                <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div>
                        <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Age</label>
                        <input type="number" id="patientAge" class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white" placeholder="Enter age">
                    </div>
                    <div>
                        <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Gender</label>
                        <select id="patientGender" class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white">
                            <option value="">Select gender</option>
                            <option value="male">Male</option>
                            <option value="female">Female</option>
                            <option value="other">Other</option>
                        </select>
                    </div>
                    <div class="md:col-span-2">
                        <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Medical History</label>
                        <textarea id="medicalHistory" rows="3" class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white" placeholder="Any relevant medical conditions, allergies, or previous diagnoses..."></textarea>
                    </div>
                    <div class="md:col-span-2">
                        <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Current Medications</label>
                        <textarea id="currentMedications" rows="2" class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white" placeholder="List current medications..."></textarea>
                    </div>
                </div>
            </div>
        `;
    }

    getSymptomsStep() {
        return `
            <div class="space-y-6">
                <div class="text-center mb-8">
                    <div class="w-16 h-16 bg-green-100 dark:bg-green-900 rounded-full flex items-center justify-center mx-auto mb-4">
                        <i class="fas fa-stethoscope text-green-600 dark:text-green-400 text-2xl"></i>
                    </div>
                    <h3 class="text-xl font-semibold text-gray-900 dark:text-white">Symptoms & Chief Complaint</h3>
                    <p class="text-gray-600 dark:text-gray-400">Help us recommend the most relevant tests</p>
                </div>

                <div class="space-y-4">
                    <div>
                        <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Primary Symptoms</label>
                        <div class="grid grid-cols-2 md:grid-cols-3 gap-3">
                            ${this.getSymptomCheckboxes()}
                        </div>
                    </div>

                    <div>
                        <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Symptom Duration</label>
                        <select id="symptomDuration" class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white">
                            <option value="">Select duration</option>
                            <option value="1-3_days">1-3 days</option>
                            <option value="1_week">About 1 week</option>
                            <option value="2-4_weeks">2-4 weeks</option>
                            <option value="1-3_months">1-3 months</option>
                            <option value="3_months_plus">More than 3 months</option>
                        </select>
                    </div>

                    <div>
                        <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Severity Level</label>
                        <div class="flex space-x-4">
                            <label class="flex items-center">
                                <input type="radio" name="severity" value="mild" class="mr-2">
                                <span class="text-green-600">Mild</span>
                            </label>
                            <label class="flex items-center">
                                <input type="radio" name="severity" value="moderate" class="mr-2">
                                <span class="text-yellow-600">Moderate</span>
                            </label>
                            <label class="flex items-center">
                                <input type="radio" name="severity" value="severe" class="mr-2">
                                <span class="text-red-600">Severe</span>
                            </label>
                        </div>
                    </div>

                    <div>
                        <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Additional Details</label>
                        <textarea id="additionalSymptoms" rows="3" class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white" placeholder="Describe any additional symptoms, triggers, or patterns..."></textarea>
                    </div>
                </div>
            </div>
        `;
    }

    getSymptomCheckboxes() {
        const symptoms = [
            'Fever', 'Fatigue', 'Headache', 'Nausea', 'Vomiting', 'Diarrhea',
            'Constipation', 'Abdominal pain', 'Chest pain', 'Shortness of breath',
            'Cough', 'Sore throat', 'Joint pain', 'Muscle pain', 'Dizziness',
            'Weight loss', 'Weight gain', 'Loss of appetite', 'Skin rash', 'Sleep issues'
        ];

        return symptoms.map(symptom => `
            <label class="flex items-center p-3 border border-gray-300 dark:border-gray-600 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 cursor-pointer">
                <input type="checkbox" value="${symptom}" class="mr-3 symptom-checkbox">
                <span class="text-sm text-gray-700 dark:text-gray-300">${symptom}</span>
            </label>
        `).join('');
    }

    getRecommendationsStep() {
        return `
            <div class="space-y-6">
                <div class="text-center mb-8">
                    <div class="w-16 h-16 bg-purple-100 dark:bg-purple-900 rounded-full flex items-center justify-center mx-auto mb-4">
                        <i class="fas fa-brain text-purple-600 dark:text-purple-400 text-2xl"></i>
                    </div>
                    <h3 class="text-xl font-semibold text-gray-900 dark:text-white">AI Recommendations</h3>
                    <p class="text-gray-600 dark:text-gray-400">Based on the provided information</p>
                </div>

                <div id="recommendationsContent" class="space-y-4">
                    <div class="text-center py-8">
                        <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
                        <p class="text-gray-600 dark:text-gray-400 mt-4">Analyzing symptoms and generating recommendations...</p>
                    </div>
                </div>
            </div>
        `;
    }

    getConfirmationStep() {
        return `
            <div class="space-y-6">
                <div class="text-center mb-8">
                    <div class="w-16 h-16 bg-green-100 dark:bg-green-900 rounded-full flex items-center justify-center mx-auto mb-4">
                        <i class="fas fa-check-circle text-green-600 dark:text-green-400 text-2xl"></i>
                    </div>
                    <h3 class="text-xl font-semibold text-gray-900 dark:text-white">Confirm Test Selection</h3>
                    <p class="text-gray-600 dark:text-gray-400">Review and confirm your test panel selection</p>
                </div>

                <div id="confirmationContent">
                    <div class="bg-blue-50 dark:bg-blue-900/20 rounded-lg p-6 mb-6">
                        <h4 class="font-semibold text-blue-800 dark:text-blue-200 mb-3">Selected Tests</h4>
                        <div id="selectedTestsList" class="space-y-2"></div>
                    </div>

                    <div class="bg-gray-50 dark:bg-gray-700 rounded-lg p-6">
                        <h4 class="font-semibold text-gray-800 dark:text-gray-200 mb-3">Summary</h4>
                        <div class="grid grid-cols-2 gap-4 text-sm">
                            <div>
                                <span class="text-gray-600 dark:text-gray-400">Total Tests:</span>
                                <span id="totalTestsCount" class="font-medium ml-2">0</span>
                            </div>
                            <div>
                                <span class="text-gray-600 dark:text-gray-400">Estimated Time:</span>
                                <span id="estimatedTime" class="font-medium ml-2">0 min</span>
                            </div>
                        </div>
                    </div>

                    <div class="mt-6">
                        <label class="flex items-center">
                            <input type="checkbox" id="urgentProcessing" class="mr-3">
                            <span class="text-sm text-gray-700 dark:text-gray-300">Mark as urgent processing</span>
                        </label>
                    </div>
                </div>
            </div>
        `;
    }

    open(patientId = null) {
        this.patientId = patientId;
        this.currentStep = 1;
        this.selectedTests.clear();
        this.updateWizardDisplay();
        document.getElementById('testPanelWizard').classList.remove('hidden');
        
        // If patient ID provided, pre-fill some data
        if (patientId) {
            this.loadPatientData(patientId);
        }
    }

    close() {
        document.getElementById('testPanelWizard').classList.add('hidden');
        this.reset();
    }

    reset() {
        this.currentStep = 1;
        this.selectedTests.clear();
        this.patientData = {};
        this.recommendations = [];
    }

    nextStep() {
        if (this.validateCurrentStep()) {
            this.saveCurrentStepData();
            
            if (this.currentStep < this.totalSteps) {
                this.currentStep++;
                this.updateWizardDisplay();
                
                // Trigger AI recommendations when moving to step 3
                if (this.currentStep === 3) {
                    this.generateRecommendations();
                }
                
                // Update confirmation when moving to step 4
                if (this.currentStep === 4) {
                    this.updateConfirmation();
                }
            } else {
                this.submitTestOrder();
            }
        }
    }

    previousStep() {
        if (this.currentStep > 1) {
            this.currentStep--;
            this.updateWizardDisplay();
        }
    }

    updateWizardDisplay() {
        const content = document.getElementById('wizardContent');
        const currentStepNumber = document.getElementById('currentStepNumber');
        const progressBar = document.getElementById('progressBar');
        const progressPercentage = document.getElementById('progressPercentage');
        const prevBtn = document.getElementById('prevBtn');
        const nextBtn = document.getElementById('nextBtn');

        // Update content
        content.innerHTML = this.getStepContent(this.currentStep);

        // Update progress
        const progress = (this.currentStep / this.totalSteps) * 100;
        currentStepNumber.textContent = this.currentStep;
        progressBar.style.width = `${progress}%`;
        progressPercentage.textContent = `${Math.round(progress)}%`;

        // Update buttons
        prevBtn.disabled = this.currentStep === 1;
        nextBtn.textContent = this.currentStep === this.totalSteps ? 
            'Order Tests' : 'Next';
        
        if (this.currentStep === this.totalSteps) {
            nextBtn.innerHTML = '<i class="fas fa-check mr-2"></i>Order Tests';
        } else {
            nextBtn.innerHTML = 'Next <i class="fas fa-chevron-right ml-2"></i>';
        }
    }

    validateCurrentStep() {
        switch (this.currentStep) {
            case 1:
                const age = document.getElementById('patientAge').value;
                const gender = document.getElementById('patientGender').value;
                if (!age || !gender) {
                    this.showValidationError('Please fill in all required fields');
                    return false;
                }
                break;
            case 2:
                const symptoms = document.querySelectorAll('.symptom-checkbox:checked');
                if (symptoms.length === 0) {
                    this.showValidationError('Please select at least one symptom');
                    return false;
                }
                break;
            case 3:
                if (this.selectedTests.size === 0) {
                    this.showValidationError('Please select at least one test');
                    return false;
                }
                break;
        }
        return true;
    }

    saveCurrentStepData() {
        switch (this.currentStep) {
            case 1:
                this.patientData.age = document.getElementById('patientAge').value;
                this.patientData.gender = document.getElementById('patientGender').value;
                this.patientData.medicalHistory = document.getElementById('medicalHistory').value;
                this.patientData.currentMedications = document.getElementById('currentMedications').value;
                break;
            case 2:
                this.patientData.symptoms = Array.from(document.querySelectorAll('.symptom-checkbox:checked'))
                    .map(cb => cb.value);
                this.patientData.symptomDuration = document.getElementById('symptomDuration').value;
                this.patientData.severity = document.querySelector('input[name="severity"]:checked')?.value;
                this.patientData.additionalSymptoms = document.getElementById('additionalSymptoms').value;
                break;
        }
    }

    async generateRecommendations() {
        try {
            // Simulate AI recommendation generation
            setTimeout(() => {
                this.recommendations = this.getTestRecommendations();
                this.displayRecommendations();
            }, 2000);
        } catch (error) {
            console.error('Error generating recommendations:', error);
            this.showValidationError('Error generating recommendations. Please try again.');
        }
    }

    getTestRecommendations() {
        // Simulated AI-based test recommendations
        const allTests = [
            { id: 'cbc', name: 'Complete Blood Count (CBC)', category: 'Hematology', priority: 'high', reason: 'Fatigue and general symptoms' },
            { id: 'bmp', name: 'Basic Metabolic Panel', category: 'Chemistry', priority: 'high', reason: 'Overall health assessment' },
            { id: 'lipid', name: 'Lipid Panel', category: 'Chemistry', priority: 'medium', reason: 'Cardiovascular risk assessment' },
            { id: 'tsh', name: 'Thyroid Stimulating Hormone', category: 'Endocrinology', priority: 'medium', reason: 'Fatigue and weight changes' },
            { id: 'glucose', name: 'Fasting Glucose', category: 'Chemistry', priority: 'high', reason: 'Metabolic health screening' },
            { id: 'hba1c', name: 'Hemoglobin A1C', category: 'Chemistry', priority: 'medium', reason: 'Diabetes screening' },
            { id: 'crp', name: 'C-Reactive Protein', category: 'Immunology', priority: 'medium', reason: 'Inflammation marker' },
            { id: 'urine', name: 'Urinalysis', category: 'Urinalysis', priority: 'medium', reason: 'General health screening' }
        ];

        // Filter based on symptoms and patient data
        return allTests.filter(test => {
            if (this.patientData.symptoms.includes('Fatigue')) return true;
            if (this.patientData.symptoms.includes('Fever') && test.category === 'Immunology') return true;
            if (this.patientData.symptoms.includes('Weight loss') && test.id === 'tsh') return true;
            return test.priority === 'high';
        });
    }

    displayRecommendations() {
        const content = document.getElementById('recommendationsContent');
        
        const recommendationsHTML = this.recommendations.map(test => `
            <div class="border border-gray-300 dark:border-gray-600 rounded-lg p-4 hover:bg-gray-50 dark:hover:bg-gray-700">
                <label class="flex items-start cursor-pointer">
                    <input type="checkbox" value="${test.id}" class="mt-1 mr-4 test-recommendation-checkbox" 
                           ${test.priority === 'high' ? 'checked' : ''} 
                           onchange="testPanelWizard.toggleTestSelection('${test.id}')">
                    <div class="flex-1">
                        <div class="flex items-center justify-between">
                            <h4 class="font-medium text-gray-900 dark:text-white">${test.name}</h4>
                            <span class="px-2 py-1 text-xs rounded-full ${test.priority === 'high' ? 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200' : 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200'}">${test.priority} priority</span>
                        </div>
                        <p class="text-sm text-gray-600 dark:text-gray-400 mt-1">${test.category}</p>
                        <p class="text-sm text-blue-600 dark:text-blue-400 mt-2">${test.reason}</p>
                    </div>
                </label>
            </div>
        `).join('');

        content.innerHTML = `
            <div class="mb-6">
                <div class="bg-blue-50 dark:bg-blue-900/20 rounded-lg p-4 mb-4">
                    <div class="flex items-center">
                        <i class="fas fa-lightbulb text-blue-600 dark:text-blue-400 mr-3"></i>
                        <div>
                            <h4 class="font-medium text-blue-800 dark:text-blue-200">AI Recommendations</h4>
                            <p class="text-sm text-blue-600 dark:text-blue-400">Based on symptoms and medical history</p>
                        </div>
                    </div>
                </div>
                <div class="space-y-3">
                    ${recommendationsHTML}
                </div>
            </div>
        `;

        // Auto-select high priority tests
        this.recommendations.forEach(test => {
            if (test.priority === 'high') {
                this.selectedTests.add(test.id);
            }
        });
    }

    toggleTestSelection(testId) {
        if (this.selectedTests.has(testId)) {
            this.selectedTests.delete(testId);
        } else {
            this.selectedTests.add(testId);
        }
    }

    updateConfirmation() {
        const selectedTestsList = document.getElementById('selectedTestsList');
        const totalTestsCount = document.getElementById('totalTestsCount');
        const estimatedTime = document.getElementById('estimatedTime');

        const selectedTests = this.recommendations.filter(test => 
            this.selectedTests.has(test.id)
        );

        selectedTestsList.innerHTML = selectedTests.map(test => `
            <div class="flex items-center justify-between bg-white dark:bg-gray-800 rounded-lg p-3 border border-gray-200 dark:border-gray-600">
                <div>
                    <span class="font-medium text-gray-900 dark:text-white">${test.name}</span>
                    <span class="text-sm text-gray-500 dark:text-gray-400 ml-2">(${test.category})</span>
                </div>
                <span class="px-2 py-1 text-xs rounded-full ${test.priority === 'high' ? 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200' : 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200'}">${test.priority}</span>
            </div>
        `).join('');

        totalTestsCount.textContent = selectedTests.length;
        estimatedTime.textContent = `${selectedTests.length * 15} min`;
    }

    async submitTestOrder() {
        try {
            const orderData = {
                patientId: this.patientId,
                patientData: this.patientData,
                selectedTests: Array.from(this.selectedTests),
                urgent: document.getElementById('urgentProcessing')?.checked || false,
                timestamp: new Date().toISOString()
            };

            // Show loading state
            const nextBtn = document.getElementById('nextBtn');
            nextBtn.disabled = true;
            nextBtn.innerHTML = '<i class="fas fa-spinner fa-spin mr-2"></i>Ordering Tests...';

            // Simulate API call
            await new Promise(resolve => setTimeout(resolve, 2000));

            // Success
            if (window.smartNotifications) {
                window.smartNotifications.showCustomNotification(
                    'success',
                    'Test Order Created',
                    `Successfully ordered ${this.selectedTests.size} tests for the patient`
                );
            }

            this.close();
            
            // Optionally redirect or refresh
            if (this.patientId) {
                window.location.href = `/patients/${this.patientId}/tests`;
            } else {
                window.location.reload();
            }

        } catch (error) {
            console.error('Error submitting test order:', error);
            this.showValidationError('Error creating test order. Please try again.');
            
            const nextBtn = document.getElementById('nextBtn');
            nextBtn.disabled = false;
            nextBtn.innerHTML = '<i class="fas fa-check mr-2"></i>Order Tests';
        }
    }

    showValidationError(message) {
        if (window.smartNotifications) {
            window.smartNotifications.showCustomNotification('error', 'Validation Error', message);
        } else {
            alert(message);
        }
    }

    loadPatientData(patientId) {
        // In a real implementation, this would fetch patient data from the API
        console.log(`Loading patient data for ID: ${patientId}`);
    }

    setupEventListeners() {
        // Close wizard when clicking outside
        document.addEventListener('click', (event) => {
            const wizard = document.getElementById('testPanelWizard');
            if (wizard && event.target === wizard) {
                this.close();
            }
        });

        // Keyboard navigation
        document.addEventListener('keydown', (event) => {
            const wizard = document.getElementById('testPanelWizard');
            if (wizard && !wizard.classList.contains('hidden')) {
                if (event.key === 'Escape') {
                    this.close();
                } else if (event.key === 'Enter' && event.ctrlKey) {
                    this.nextStep();
                }
            }
        });
    }
}

// Initialize global instance
window.testPanelWizard = new TestPanelWizard();

// Function to open wizard from templates
function openTestPanelWizard(patientId = null) {
    window.testPanelWizard.open(patientId);
}