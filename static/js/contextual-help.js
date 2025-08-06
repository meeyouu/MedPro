/**
 * Contextual Help Tooltips for Medical Terminology
 * Smart help system with medical definitions, reference ranges, and clinical significance
 */

class ContextualHelp {
    constructor() {
        this.medicalTerms = new Map();
        this.helpTooltip = null;
        this.currentTooltip = null;
        this.isEnabled = true;
        this.init();
    }

    init() {
        this.loadMedicalTerminology();
        this.createHelpTooltip();
        this.setupEventListeners();
        this.addHelpIndicators();
    }

    loadMedicalTerminology() {
        // Comprehensive medical terminology database
        const terminology = {
            // Blood Tests
            'CBC': {
                fullName: 'Complete Blood Count',
                definition: 'A blood test that evaluates overall health and detects various disorders including anemia, infection, and leukemia.',
                normalRanges: {
                    'WBC': '4,500-11,000 cells/μL',
                    'RBC': '4.5-5.9 million cells/μL (men), 4.1-5.1 million cells/μL (women)',
                    'Hemoglobin': '14-18 g/dL (men), 12-16 g/dL (women)',
                    'Hematocrit': '42-52% (men), 37-47% (women)'
                },
                clinicalSignificance: 'Used to diagnose blood disorders, infections, immune system disorders, and certain cancers.',
                whenOrdered: 'Routine health screening, symptoms of fatigue, weakness, infection, or bleeding'
            },
            'WBC': {
                fullName: 'White Blood Cells',
                definition: 'Cells that fight infection and are part of the immune system.',
                normalRanges: { 'WBC Count': '4,500-11,000 cells/μL' },
                clinicalSignificance: 'High levels may indicate infection, inflammation, or blood cancer. Low levels may suggest bone marrow problems.',
                whenOrdered: 'To detect infections, immune system disorders, or blood disorders'
            },
            'RBC': {
                fullName: 'Red Blood Cells',
                definition: 'Cells that carry oxygen from lungs to body tissues and carbon dioxide back to lungs.',
                normalRanges: { 'RBC Count': '4.5-5.9 million cells/μL (men), 4.1-5.1 million cells/μL (women)' },
                clinicalSignificance: 'Low levels indicate anemia. High levels may suggest dehydration or heart/lung disease.',
                whenOrdered: 'To diagnose anemia, polycythemia, or monitor blood disorders'
            },
            'Hemoglobin': {
                fullName: 'Hemoglobin',
                definition: 'Protein in red blood cells that carries oxygen throughout the body.',
                normalRanges: { 'Hemoglobin': '14-18 g/dL (men), 12-16 g/dL (women)' },
                clinicalSignificance: 'Low levels indicate anemia. High levels may suggest dehydration or lung disease.',
                whenOrdered: 'To diagnose anemia, monitor blood disorders, or assess oxygen-carrying capacity'
            },
            'Glucose': {
                fullName: 'Blood Glucose',
                definition: 'The amount of sugar (glucose) present in blood. Primary source of energy for body cells.',
                normalRanges: { 
                    'Fasting': '70-100 mg/dL',
                    'Random': '<140 mg/dL',
                    'Post-meal (2hr)': '<140 mg/dL'
                },
                clinicalSignificance: 'High levels may indicate diabetes or prediabetes. Low levels may cause hypoglycemia symptoms.',
                whenOrdered: 'Diabetes screening, monitoring diabetes treatment, symptoms of high/low blood sugar'
            },
            'HbA1c': {
                fullName: 'Hemoglobin A1C',
                definition: 'Measures average blood glucose levels over the past 2-3 months.',
                normalRanges: { 'HbA1c': '<5.7% (normal), 5.7-6.4% (prediabetes), ≥6.5% (diabetes)' },
                clinicalSignificance: 'Used to diagnose diabetes and monitor long-term glucose control in diabetic patients.',
                whenOrdered: 'Diabetes screening, monitoring diabetes treatment effectiveness'
            },
            'Creatinine': {
                fullName: 'Serum Creatinine',
                definition: 'Waste product produced by muscles, filtered out by kidneys. Indicator of kidney function.',
                normalRanges: { 'Creatinine': '0.6-1.2 mg/dL (men), 0.5-1.1 mg/dL (women)' },
                clinicalSignificance: 'High levels may indicate kidney disease or dysfunction.',
                whenOrdered: 'Kidney function assessment, monitoring kidney disease, before contrast procedures'
            },
            'BUN': {
                fullName: 'Blood Urea Nitrogen',
                definition: 'Waste product formed when protein breaks down, removed by kidneys.',
                normalRanges: { 'BUN': '7-20 mg/dL' },
                clinicalSignificance: 'High levels may indicate kidney problems, dehydration, or high protein diet.',
                whenOrdered: 'Kidney function assessment, monitor kidney disease progression'
            },
            'ALT': {
                fullName: 'Alanine Aminotransferase',
                definition: 'Enzyme found mainly in liver cells. Released when liver is damaged or inflamed.',
                normalRanges: { 'ALT': '7-56 units/L' },
                clinicalSignificance: 'High levels indicate liver damage or disease.',
                whenOrdered: 'Liver function assessment, monitor liver disease, medication side effects'
            },
            'AST': {
                fullName: 'Aspartate Aminotransferase',
                definition: 'Enzyme found in liver, heart, muscles, and other organs.',
                normalRanges: { 'AST': '10-40 units/L' },
                clinicalSignificance: 'High levels may indicate liver damage, heart attack, or muscle injury.',
                whenOrdered: 'Liver function assessment, heart attack diagnosis, muscle disease evaluation'
            },
            'TSH': {
                fullName: 'Thyroid Stimulating Hormone',
                definition: 'Hormone that controls thyroid gland function and metabolism.',
                normalRanges: { 'TSH': '0.4-4.0 mIU/L' },
                clinicalSignificance: 'High levels suggest hypothyroidism. Low levels suggest hyperthyroidism.',
                whenOrdered: 'Thyroid function assessment, symptoms of thyroid disorders'
            },
            'Cholesterol': {
                fullName: 'Total Cholesterol',
                definition: 'Waxy substance found in blood, used to build cells but can clog arteries if too high.',
                normalRanges: { 
                    'Total': '<200 mg/dL (desirable)',
                    'LDL': '<100 mg/dL (optimal)',
                    'HDL': '>40 mg/dL (men), >50 mg/dL (women)'
                },
                clinicalSignificance: 'High levels increase risk of heart disease and stroke.',
                whenOrdered: 'Cardiovascular risk assessment, monitor cholesterol-lowering treatment'
            },
            'Triglycerides': {
                fullName: 'Triglycerides',
                definition: 'Type of fat in blood used for energy. High levels linked to heart disease.',
                normalRanges: { 'Triglycerides': '<150 mg/dL' },
                clinicalSignificance: 'High levels increase risk of heart disease and pancreatitis.',
                whenOrdered: 'Cardiovascular risk assessment, evaluate lipid disorders'
            },
            'CRP': {
                fullName: 'C-Reactive Protein',
                definition: 'Protein produced by liver in response to inflammation.',
                normalRanges: { 'CRP': '<3.0 mg/L (low risk), 3.0-10.0 mg/L (moderate risk), >10.0 mg/L (high risk)' },
                clinicalSignificance: 'High levels indicate inflammation, infection, or increased cardiovascular risk.',
                whenOrdered: 'Assess inflammation, cardiovascular risk, monitor inflammatory conditions'
            },
            'Platelet': {
                fullName: 'Platelet Count',
                definition: 'Small blood cells that help blood clot and stop bleeding.',
                normalRanges: { 'Platelets': '150,000-450,000 per μL' },
                clinicalSignificance: 'Low count increases bleeding risk. High count may increase clotting risk.',
                whenOrdered: 'Bleeding disorders, monitor chemotherapy effects, before surgery'
            }
        };

        // Load terminology into Map
        Object.entries(terminology).forEach(([key, value]) => {
            this.medicalTerms.set(key.toLowerCase(), value);
        });
    }

    createHelpTooltip() {
        if (document.getElementById('contextualHelpTooltip')) return;

        const tooltip = document.createElement('div');
        tooltip.id = 'contextualHelpTooltip';
        tooltip.className = 'hidden fixed z-50 max-w-sm bg-white dark:bg-gray-800 rounded-lg shadow-xl border border-gray-200 dark:border-gray-700 p-4';
        tooltip.style.pointerEvents = 'none';
        
        document.body.appendChild(tooltip);
        this.helpTooltip = tooltip;
    }

    setupEventListeners() {
        // Add hover listeners for medical terms
        document.addEventListener('mouseover', (event) => {
            const element = event.target;
            if (this.isHelpCandidate(element)) {
                this.showHelp(element, event);
            }
        });

        document.addEventListener('mouseout', (event) => {
            const element = event.target;
            if (this.isHelpCandidate(element)) {
                this.hideHelp();
            }
        });

        // Add click listeners for detailed help
        document.addEventListener('click', (event) => {
            const element = event.target;
            if (element.classList.contains('help-indicator')) {
                event.preventDefault();
                this.showDetailedHelp(element.getAttribute('data-term'));
            }
        });

        // Close help on escape key
        document.addEventListener('keydown', (event) => {
            if (event.key === 'Escape') {
                this.hideHelp();
                this.hideDetailedHelp();
            }
        });
    }

    isHelpCandidate(element) {
        if (!this.isEnabled) return false;
        
        // Check if element has help data or contains medical terminology
        return element.hasAttribute('data-help-term') || 
               element.classList.contains('medical-term') ||
               this.containsMedicalTerm(element.textContent);
    }

    containsMedicalTerm(text) {
        if (!text) return false;
        
        const words = text.split(/\s+/);
        return words.some(word => {
            const cleanWord = word.replace(/[^\w]/g, '').toLowerCase();
            return this.medicalTerms.has(cleanWord);
        });
    }

    showHelp(element, event) {
        const term = this.extractMedicalTerm(element);
        if (!term) return;

        const termData = this.medicalTerms.get(term.toLowerCase());
        if (!termData) return;

        const tooltip = this.helpTooltip;
        tooltip.innerHTML = this.generateTooltipContent(term, termData);
        
        // Position tooltip
        const rect = element.getBoundingClientRect();
        const tooltipRect = tooltip.getBoundingClientRect();
        
        let left = rect.left + (rect.width / 2) - (tooltipRect.width / 2);
        let top = rect.top - tooltipRect.height - 10;
        
        // Adjust if tooltip goes off screen
        if (left < 10) left = 10;
        if (left + tooltipRect.width > window.innerWidth - 10) {
            left = window.innerWidth - tooltipRect.width - 10;
        }
        if (top < 10) {
            top = rect.bottom + 10;
        }
        
        tooltip.style.left = `${left}px`;
        tooltip.style.top = `${top}px`;
        tooltip.classList.remove('hidden');
        
        this.currentTooltip = { element, term };
    }

    hideHelp() {
        if (this.helpTooltip) {
            this.helpTooltip.classList.add('hidden');
        }
        this.currentTooltip = null;
    }

    extractMedicalTerm(element) {
        // Check for explicit help term
        if (element.hasAttribute('data-help-term')) {
            return element.getAttribute('data-help-term');
        }
        
        // Extract from text content
        const text = element.textContent;
        const words = text.split(/\s+/);
        
        for (let word of words) {
            const cleanWord = word.replace(/[^\w]/g, '').toLowerCase();
            if (this.medicalTerms.has(cleanWord)) {
                return cleanWord;
            }
        }
        
        return null;
    }

    generateTooltipContent(term, termData) {
        return `
            <div class="space-y-3">
                <div class="border-b border-gray-200 dark:border-gray-600 pb-2">
                    <h3 class="font-semibold text-gray-900 dark:text-white text-sm">
                        ${termData.fullName}
                    </h3>
                    <p class="text-xs text-blue-600 dark:text-blue-400">${term.toUpperCase()}</p>
                </div>
                
                <div>
                    <p class="text-sm text-gray-700 dark:text-gray-300">
                        ${termData.definition}
                    </p>
                </div>
                
                ${termData.normalRanges ? `
                    <div>
                        <h4 class="font-medium text-gray-900 dark:text-white text-xs mb-1">Normal Ranges:</h4>
                        <div class="text-xs text-gray-600 dark:text-gray-400 space-y-1">
                            ${Object.entries(termData.normalRanges).map(([key, value]) => 
                                `<div><span class="font-medium">${key}:</span> ${value}</div>`
                            ).join('')}
                        </div>
                    </div>
                ` : ''}
                
                <div class="text-xs text-gray-500 dark:text-gray-400 border-t border-gray-200 dark:border-gray-600 pt-2">
                    <i class="fas fa-info-circle mr-1"></i>
                    Click for detailed information
                </div>
            </div>
        `;
    }

    showDetailedHelp(term) {
        const termData = this.medicalTerms.get(term.toLowerCase());
        if (!termData) return;

        // Create detailed help modal
        const modal = document.createElement('div');
        modal.id = 'detailedHelpModal';
        modal.className = 'fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4';
        
        modal.innerHTML = `
            <div class="bg-white dark:bg-gray-800 rounded-xl shadow-2xl max-w-2xl w-full max-h-[90vh] overflow-hidden">
                <!-- Header -->
                <div class="bg-gradient-to-r from-blue-600 to-purple-600 text-white p-6">
                    <div class="flex items-center justify-between">
                        <div>
                            <h2 class="text-xl font-bold">${termData.fullName}</h2>
                            <p class="text-blue-100 text-sm">${term.toUpperCase()} - Medical Information</p>
                        </div>
                        <button onclick="contextualHelp.hideDetailedHelp()" class="text-white hover:text-gray-200">
                            <i class="fas fa-times text-xl"></i>
                        </button>
                    </div>
                </div>

                <!-- Content -->
                <div class="p-6 overflow-y-auto max-h-[70vh] space-y-6">
                    <!-- Definition -->
                    <div>
                        <h3 class="font-semibold text-gray-900 dark:text-white mb-2">Definition</h3>
                        <p class="text-gray-700 dark:text-gray-300">${termData.definition}</p>
                    </div>

                    <!-- Normal Ranges -->
                    ${termData.normalRanges ? `
                        <div>
                            <h3 class="font-semibold text-gray-900 dark:text-white mb-2">Normal Ranges</h3>
                            <div class="bg-green-50 dark:bg-green-900/20 rounded-lg p-4">
                                ${Object.entries(termData.normalRanges).map(([key, value]) => `
                                    <div class="flex justify-between items-center py-1">
                                        <span class="font-medium text-gray-700 dark:text-gray-300">${key}:</span>
                                        <span class="text-green-600 dark:text-green-400 font-mono text-sm">${value}</span>
                                    </div>
                                `).join('')}
                            </div>
                        </div>
                    ` : ''}

                    <!-- Clinical Significance -->
                    <div>
                        <h3 class="font-semibold text-gray-900 dark:text-white mb-2">Clinical Significance</h3>
                        <p class="text-gray-700 dark:text-gray-300">${termData.clinicalSignificance}</p>
                    </div>

                    <!-- When Ordered -->
                    <div>
                        <h3 class="font-semibold text-gray-900 dark:text-white mb-2">When This Test is Ordered</h3>
                        <p class="text-gray-700 dark:text-gray-300">${termData.whenOrdered}</p>
                    </div>

                    <!-- Additional Resources -->
                    <div class="bg-blue-50 dark:bg-blue-900/20 rounded-lg p-4">
                        <h4 class="font-medium text-blue-800 dark:text-blue-200 mb-2">
                            <i class="fas fa-lightbulb mr-2"></i>Quick Tips
                        </h4>
                        <ul class="text-sm text-blue-700 dark:text-blue-300 space-y-1">
                            <li>• Always consider patient's clinical history when interpreting results</li>
                            <li>• Reference ranges may vary between laboratories</li>
                            <li>• Consult with physicians for abnormal values</li>
                            <li>• Consider factors like age, sex, and medications</li>
                        </ul>
                    </div>
                </div>

                <!-- Footer -->
                <div class="bg-gray-50 dark:bg-gray-700 px-6 py-4 flex justify-between">
                    <button onclick="contextualHelp.hideDetailedHelp()" 
                            class="px-4 py-2 text-gray-600 dark:text-gray-300 hover:text-gray-800 dark:hover:text-white">
                        Close
                    </button>
                    <button onclick="contextualHelp.printHelpInfo('${term}')" 
                            class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors">
                        <i class="fas fa-print mr-2"></i>Print Reference
                    </button>
                </div>
            </div>
        `;

        document.body.appendChild(modal);

        // Add click outside to close
        modal.addEventListener('click', (event) => {
            if (event.target === modal) {
                this.hideDetailedHelp();
            }
        });
    }

    hideDetailedHelp() {
        const modal = document.getElementById('detailedHelpModal');
        if (modal) {
            modal.remove();
        }
    }

    addHelpIndicators() {
        // Add help indicators to medical terms on the page
        const observer = new MutationObserver((mutations) => {
            mutations.forEach((mutation) => {
                mutation.addedNodes.forEach((node) => {
                    if (node.nodeType === Node.ELEMENT_NODE) {
                        this.processElementForHelp(node);
                    }
                });
            });
        });

        observer.observe(document.body, {
            childList: true,
            subtree: true
        });

        // Process existing elements
        this.processElementForHelp(document.body);
    }

    processElementForHelp(element) {
        // Find text nodes with medical terms
        const walker = document.createTreeWalker(
            element,
            NodeFilter.SHOW_TEXT,
            null,
            false
        );

        const textNodes = [];
        let node;
        while (node = walker.nextNode()) {
            if (this.containsMedicalTerm(node.textContent)) {
                textNodes.push(node);
            }
        }

        textNodes.forEach(textNode => {
            this.enhanceTextNodeWithHelp(textNode);
        });
    }

    enhanceTextNodeWithHelp(textNode) {
        const text = textNode.textContent;
        const words = text.split(/(\s+)/);
        let hasChanges = false;
        
        const enhancedContent = words.map(word => {
            const cleanWord = word.replace(/[^\w]/g, '').toLowerCase();
            if (this.medicalTerms.has(cleanWord)) {
                hasChanges = true;
                return `<span class="medical-term cursor-help underline decoration-dotted decoration-blue-400 hover:bg-blue-50 dark:hover:bg-blue-900/20 px-1 rounded" data-help-term="${cleanWord}" title="Click for medical information">${word}</span>`;
            }
            return word;
        }).join('');

        if (hasChanges && textNode.parentNode) {
            const wrapper = document.createElement('span');
            wrapper.innerHTML = enhancedContent;
            textNode.parentNode.replaceChild(wrapper, textNode);
        }
    }

    printHelpInfo(term) {
        const termData = this.medicalTerms.get(term.toLowerCase());
        if (!termData) return;

        const printWindow = window.open('', '_blank');
        printWindow.document.write(`
            <!DOCTYPE html>
            <html>
            <head>
                <title>${termData.fullName} - Medical Reference</title>
                <style>
                    body { font-family: Arial, sans-serif; margin: 20px; }
                    .header { border-bottom: 2px solid #2563EB; padding-bottom: 10px; margin-bottom: 20px; }
                    .section { margin-bottom: 20px; }
                    .ranges { background-color: #f0f9ff; padding: 15px; border-radius: 8px; }
                    .ranges table { width: 100%; border-collapse: collapse; }
                    .ranges th, .ranges td { border: 1px solid #ddd; padding: 8px; text-align: left; }
                    .ranges th { background-color: #e0f2fe; }
                </style>
            </head>
            <body>
                <div class="header">
                    <h1>${termData.fullName} (${term.toUpperCase()})</h1>
                    <p>Medical Reference - MedLab Pro</p>
                </div>
                
                <div class="section">
                    <h2>Definition</h2>
                    <p>${termData.definition}</p>
                </div>

                ${termData.normalRanges ? `
                    <div class="section">
                        <h2>Normal Ranges</h2>
                        <div class="ranges">
                            <table>
                                <thead>
                                    <tr><th>Parameter</th><th>Normal Range</th></tr>
                                </thead>
                                <tbody>
                                    ${Object.entries(termData.normalRanges).map(([key, value]) => 
                                        `<tr><td>${key}</td><td>${value}</td></tr>`
                                    ).join('')}
                                </tbody>
                            </table>
                        </div>
                    </div>
                ` : ''}

                <div class="section">
                    <h2>Clinical Significance</h2>
                    <p>${termData.clinicalSignificance}</p>
                </div>

                <div class="section">
                    <h2>When This Test is Ordered</h2>
                    <p>${termData.whenOrdered}</p>
                </div>

                <div style="margin-top: 30px; font-size: 12px; color: #666;">
                    Generated by MedLab Pro - ${new Date().toLocaleString()}
                </div>
            </body>
            </html>
        `);
        
        printWindow.document.close();
        printWindow.print();
    }

    // Public API methods
    toggle() {
        this.isEnabled = !this.isEnabled;
        if (!this.isEnabled) {
            this.hideHelp();
            this.hideDetailedHelp();
        }
    }

    addCustomTerm(term, data) {
        this.medicalTerms.set(term.toLowerCase(), data);
    }

    showHelpForTerm(term) {
        const termData = this.medicalTerms.get(term.toLowerCase());
        if (termData) {
            this.showDetailedHelp(term);
        }
    }

    searchTerms(query) {
        const results = [];
        const searchQuery = query.toLowerCase();
        
        for (let [term, data] of this.medicalTerms) {
            if (term.includes(searchQuery) || 
                data.fullName.toLowerCase().includes(searchQuery) ||
                data.definition.toLowerCase().includes(searchQuery)) {
                results.push({ term, data });
            }
        }
        
        return results;
    }
}

// Initialize global instance
window.contextualHelp = new ContextualHelp();

// Global functions for template use
function toggleContextualHelp() {
    window.contextualHelp.toggle();
}

function showMedicalHelp(term) {
    window.contextualHelp.showHelpForTerm(term);
}

function searchMedicalTerms(query) {
    return window.contextualHelp.searchTerms(query);
}