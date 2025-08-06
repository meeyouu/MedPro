/**
 * One-click PDF Report Generation with Custom Branding
 * Advanced PDF generation with charts, custom layouts, and laboratory branding
 */

class PDFReportGenerator {
    constructor() {
        this.currentReportData = null;
        this.brandingConfig = {
            logoUrl: '/static/img/logo.png',
            labName: 'MedLab Pro',
            address: '123 Medical Center Drive',
            phone: '+1 (555) 123-4567',
            email: 'info@medlabpro.com',
            website: 'www.medlabpro.com',
            primaryColor: '#2563EB',
            secondaryColor: '#7C3AED'
        };
        this.init();
    }

    init() {
        this.loadPDFLibrary();
        this.createGeneratorModal();
        this.setupEventListeners();
    }

    async loadPDFLibrary() {
        // Load jsPDF and html2canvas for PDF generation
        if (!window.jsPDF) {
            const script = document.createElement('script');
            script.src = 'https://cdnjs.cloudflare.com/ajax/libs/jspdf/2.5.1/jspdf.umd.min.js';
            document.head.appendChild(script);
            
            const canvasScript = document.createElement('script');
            canvasScript.src = 'https://cdnjs.cloudflare.com/ajax/libs/html2canvas/1.4.1/html2canvas.min.js';
            document.head.appendChild(canvasScript);
        }
    }

    createGeneratorModal() {
        if (document.getElementById('pdfGeneratorModal')) return;

        const modal = document.createElement('div');
        modal.id = 'pdfGeneratorModal';
        modal.className = 'hidden fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4';
        
        modal.innerHTML = `
            <div class="bg-white dark:bg-gray-800 rounded-xl shadow-2xl max-w-2xl w-full max-h-[90vh] overflow-hidden">
                <!-- Header -->
                <div class="bg-gradient-to-r from-blue-600 to-purple-600 text-white p-6">
                    <div class="flex items-center justify-between">
                        <div>
                            <h2 class="text-2xl font-bold">Generate PDF Report</h2>
                            <p class="text-blue-100 mt-1">Custom branded laboratory reports</p>
                        </div>
                        <button onclick="pdfReportGenerator.close()" class="text-white hover:text-gray-200">
                            <i class="fas fa-times text-xl"></i>
                        </button>
                    </div>
                </div>

                <!-- Content -->
                <div class="p-6">
                    <div class="space-y-6">
                        <!-- Report Type Selection -->
                        <div>
                            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">Report Type</label>
                            <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
                                <label class="flex items-center p-4 border border-gray-300 dark:border-gray-600 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 cursor-pointer">
                                    <input type="radio" name="reportType" value="patient_results" class="mr-3" checked>
                                    <div>
                                        <div class="font-medium text-gray-900 dark:text-white">Patient Results</div>
                                        <div class="text-sm text-gray-500 dark:text-gray-400">Complete test results for patient</div>
                                    </div>
                                </label>
                                <label class="flex items-center p-4 border border-gray-300 dark:border-gray-600 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 cursor-pointer">
                                    <input type="radio" name="reportType" value="ai_analysis" class="mr-3">
                                    <div>
                                        <div class="font-medium text-gray-900 dark:text-white">AI Analysis Report</div>
                                        <div class="text-sm text-gray-500 dark:text-gray-400">AI-generated insights and recommendations</div>
                                    </div>
                                </label>
                                <label class="flex items-center p-4 border border-gray-300 dark:border-gray-600 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 cursor-pointer">
                                    <input type="radio" name="reportType" value="lab_summary" class="mr-3">
                                    <div>
                                        <div class="font-medium text-gray-900 dark:text-white">Laboratory Summary</div>
                                        <div class="text-sm text-gray-500 dark:text-gray-400">Comprehensive lab analytics</div>
                                    </div>
                                </label>
                                <label class="flex items-center p-4 border border-gray-300 dark:border-gray-600 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 cursor-pointer">
                                    <input type="radio" name="reportType" value="custom" class="mr-3">
                                    <div>
                                        <div class="font-medium text-gray-900 dark:text-white">Custom Report</div>
                                        <div class="text-sm text-gray-500 dark:text-gray-400">Custom layout and content</div>
                                    </div>
                                </label>
                            </div>
                        </div>

                        <!-- Report Options -->
                        <div>
                            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">Report Options</label>
                            <div class="space-y-3">
                                <label class="flex items-center">
                                    <input type="checkbox" id="includeCharts" class="mr-3" checked>
                                    <span class="text-sm text-gray-700 dark:text-gray-300">Include charts and graphs</span>
                                </label>
                                <label class="flex items-center">
                                    <input type="checkbox" id="includeRecommendations" class="mr-3" checked>
                                    <span class="text-sm text-gray-700 dark:text-gray-300">Include AI recommendations</span>
                                </label>
                                <label class="flex items-center">
                                    <input type="checkbox" id="includeHistoricalData" class="mr-3">
                                    <span class="text-sm text-gray-700 dark:text-gray-300">Include historical comparison</span>
                                </label>
                                <label class="flex items-center">
                                    <input type="checkbox" id="includeBranding" class="mr-3" checked>
                                    <span class="text-sm text-gray-700 dark:text-gray-300">Include laboratory branding</span>
                                </label>
                            </div>
                        </div>

                        <!-- Page Layout -->
                        <div>
                            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">Page Layout</label>
                            <select id="pageLayout" class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white">
                                <option value="portrait">Portrait (A4)</option>
                                <option value="landscape">Landscape (A4)</option>
                                <option value="letter">Letter Size</option>
                                <option value="legal">Legal Size</option>
                            </select>
                        </div>

                        <!-- Custom Sections (for custom reports) -->
                        <div id="customSections" class="hidden">
                            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">Custom Sections</label>
                            <div class="space-y-2">
                                <div class="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-700 rounded-lg">
                                    <span class="text-sm text-gray-700 dark:text-gray-300">Patient Demographics</span>
                                    <input type="checkbox" class="custom-section" data-section="demographics" checked>
                                </div>
                                <div class="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-700 rounded-lg">
                                    <span class="text-sm text-gray-700 dark:text-gray-300">Test Results Table</span>
                                    <input type="checkbox" class="custom-section" data-section="results" checked>
                                </div>
                                <div class="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-700 rounded-lg">
                                    <span class="text-sm text-gray-700 dark:text-gray-300">Reference Ranges</span>
                                    <input type="checkbox" class="custom-section" data-section="ranges" checked>
                                </div>
                                <div class="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-700 rounded-lg">
                                    <span class="text-sm text-gray-700 dark:text-gray-300">Physician Notes</span>
                                    <input type="checkbox" class="custom-section" data-section="notes">
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Footer -->
                <div class="bg-gray-50 dark:bg-gray-700 px-6 py-4 flex justify-between">
                    <button onclick="pdfReportGenerator.close()" 
                            class="px-4 py-2 text-gray-600 dark:text-gray-300 hover:text-gray-800 dark:hover:text-white">
                        Cancel
                    </button>
                    <div class="flex space-x-3">
                        <button onclick="pdfReportGenerator.previewReport()" 
                                class="px-4 py-2 border border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-600">
                            <i class="fas fa-eye mr-2"></i>Preview
                        </button>
                        <button id="generatePdfBtn" onclick="pdfReportGenerator.generatePDF()" 
                                class="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors">
                            <i class="fas fa-file-pdf mr-2"></i>Generate PDF
                        </button>
                    </div>
                </div>
            </div>
        `;

        document.body.appendChild(modal);
    }

    open(reportData) {
        this.currentReportData = reportData;
        document.getElementById('pdfGeneratorModal').classList.remove('hidden');
        this.updateModalForReportType();
    }

    close() {
        document.getElementById('pdfGeneratorModal').classList.add('hidden');
        this.currentReportData = null;
    }

    updateModalForReportType() {
        const customSections = document.getElementById('customSections');
        const reportTypeInputs = document.querySelectorAll('input[name="reportType"]');
        
        reportTypeInputs.forEach(input => {
            input.addEventListener('change', (e) => {
                if (e.target.value === 'custom') {
                    customSections.classList.remove('hidden');
                } else {
                    customSections.classList.add('hidden');
                }
            });
        });
    }

    async generatePDF() {
        const generateBtn = document.getElementById('generatePdfBtn');
        generateBtn.disabled = true;
        generateBtn.innerHTML = '<i class="fas fa-spinner fa-spin mr-2"></i>Generating...';

        try {
            const options = this.getReportOptions();
            const reportContent = await this.buildReportContent(options);
            const pdf = await this.createPDFDocument(reportContent, options);
            
            this.downloadPDF(pdf, this.getFileName(options));
            
            if (window.smartNotifications) {
                window.smartNotifications.showCustomNotification(
                    'success',
                    'PDF Generated',
                    'Report has been generated and downloaded successfully'
                );
            }

            this.close();

        } catch (error) {
            console.error('Error generating PDF:', error);
            if (window.smartNotifications) {
                window.smartNotifications.showCustomNotification(
                    'error',
                    'Generation Failed',
                    'Failed to generate PDF report'
                );
            }
        } finally {
            generateBtn.disabled = false;
            generateBtn.innerHTML = '<i class="fas fa-file-pdf mr-2"></i>Generate PDF';
        }
    }

    getReportOptions() {
        const reportType = document.querySelector('input[name="reportType"]:checked').value;
        const pageLayout = document.getElementById('pageLayout').value;
        
        return {
            reportType,
            pageLayout,
            includeCharts: document.getElementById('includeCharts').checked,
            includeRecommendations: document.getElementById('includeRecommendations').checked,
            includeHistoricalData: document.getElementById('includeHistoricalData').checked,
            includeBranding: document.getElementById('includeBranding').checked,
            customSections: Array.from(document.querySelectorAll('.custom-section:checked'))
                .map(cb => cb.getAttribute('data-section'))
        };
    }

    async buildReportContent(options) {
        const content = {
            header: this.buildHeader(options),
            patientInfo: this.buildPatientInfo(options),
            testResults: this.buildTestResults(options),
            charts: options.includeCharts ? await this.buildCharts(options) : null,
            recommendations: options.includeRecommendations ? this.buildRecommendations(options) : null,
            footer: this.buildFooter(options)
        };

        return content;
    }

    buildHeader(options) {
        if (!options.includeBranding) {
            return { title: 'Laboratory Report' };
        }

        return {
            logo: this.brandingConfig.logoUrl,
            labName: this.brandingConfig.labName,
            address: this.brandingConfig.address,
            phone: this.brandingConfig.phone,
            email: this.brandingConfig.email,
            website: this.brandingConfig.website,
            reportTitle: this.getReportTitle(options.reportType),
            date: new Date().toLocaleDateString(),
            reportId: `RPT-${Date.now()}`
        };
    }

    buildPatientInfo(options) {
        if (!this.currentReportData || !this.currentReportData.patient) {
            return null;
        }

        const patient = this.currentReportData.patient;
        return {
            name: `${patient.first_name} ${patient.last_name}`,
            id: patient.patient_id,
            dateOfBirth: patient.date_of_birth,
            gender: patient.gender,
            age: this.calculateAge(patient.date_of_birth),
            phone: patient.phone,
            email: patient.email
        };
    }

    buildTestResults(options) {
        if (!this.currentReportData || !this.currentReportData.tests) {
            return null;
        }

        return this.currentReportData.tests.map(test => ({
            name: test.test_name,
            category: test.category,
            result: test.result_value,
            unit: test.unit,
            referenceRange: test.reference_range,
            status: test.result_status,
            date: test.completed_at,
            interpretation: test.interpretation
        }));
    }

    async buildCharts(options) {
        // This would generate chart images for inclusion in PDF
        const charts = [];
        
        if (this.currentReportData && this.currentReportData.chartData) {
            // Convert charts to images using html2canvas
            const chartElements = document.querySelectorAll('.chart-container canvas');
            
            for (let chart of chartElements) {
                try {
                    const canvas = await html2canvas(chart);
                    charts.push({
                        type: chart.getAttribute('data-chart-type') || 'unknown',
                        image: canvas.toDataURL('image/png')
                    });
                } catch (error) {
                    console.warn('Failed to capture chart:', error);
                }
            }
        }

        return charts;
    }

    buildRecommendations(options) {
        if (!this.currentReportData || !this.currentReportData.aiAnalysis) {
            return null;
        }

        return {
            summary: this.currentReportData.aiAnalysis.summary,
            clinicalInsights: this.currentReportData.aiAnalysis.clinical_insights,
            recommendations: this.currentReportData.aiAnalysis.recommendations,
            flaggedValues: this.currentReportData.aiAnalysis.flagged_values
        };
    }

    buildFooter(options) {
        return {
            disclaimer: 'This report is for medical professional use only. Results should be interpreted in conjunction with clinical findings.',
            generatedBy: 'MedLab Pro - AI-Powered Laboratory Management System',
            timestamp: new Date().toISOString(),
            pageNumbers: true
        };
    }

    async createPDFDocument(content, options) {
        // Wait for jsPDF to load
        while (!window.jsPDF) {
            await new Promise(resolve => setTimeout(resolve, 100));
        }

        const { jsPDF } = window.jsPDF;
        const orientation = options.pageLayout === 'landscape' ? 'landscape' : 'portrait';
        const format = options.pageLayout.includes('letter') ? 'letter' : 'a4';
        
        const pdf = new jsPDF({
            orientation: orientation,
            unit: 'mm',
            format: format
        });

        let yPosition = 20;
        const pageWidth = pdf.internal.pageSize.getWidth();
        const pageHeight = pdf.internal.pageSize.getHeight();
        const margin = 20;

        // Header
        if (content.header && options.includeBranding) {
            yPosition = this.addHeader(pdf, content.header, yPosition, pageWidth, margin);
        }

        // Patient Information
        if (content.patientInfo) {
            yPosition = this.addPatientInfo(pdf, content.patientInfo, yPosition, pageWidth, margin);
        }

        // Test Results
        if (content.testResults) {
            yPosition = this.addTestResults(pdf, content.testResults, yPosition, pageWidth, margin, pageHeight);
        }

        // Charts
        if (content.charts && content.charts.length > 0) {
            yPosition = this.addCharts(pdf, content.charts, yPosition, pageWidth, margin, pageHeight);
        }

        // Recommendations
        if (content.recommendations) {
            yPosition = this.addRecommendations(pdf, content.recommendations, yPosition, pageWidth, margin, pageHeight);
        }

        // Footer
        this.addFooter(pdf, content.footer, pageWidth, pageHeight, margin);

        return pdf;
    }

    addHeader(pdf, header, yPosition, pageWidth, margin) {
        // Add logo if available
        if (header.logo) {
            try {
                // In a real implementation, you'd load and add the actual logo
                pdf.setFontSize(20);
                pdf.setTextColor(37, 99, 235); // Blue color
                pdf.text(header.labName, margin, yPosition);
                yPosition += 10;
            } catch (error) {
                console.warn('Could not add logo:', error);
            }
        }

        // Lab information
        pdf.setFontSize(12);
        pdf.setTextColor(0, 0, 0);
        pdf.text(header.address, margin, yPosition);
        yPosition += 5;
        pdf.text(`${header.phone} | ${header.email}`, margin, yPosition);
        yPosition += 5;
        pdf.text(header.website, margin, yPosition);
        yPosition += 15;

        // Report title
        pdf.setFontSize(18);
        pdf.setFont(undefined, 'bold');
        pdf.text(header.reportTitle, margin, yPosition);
        yPosition += 10;

        // Report details
        pdf.setFontSize(10);
        pdf.setFont(undefined, 'normal');
        pdf.text(`Report ID: ${header.reportId}`, margin, yPosition);
        pdf.text(`Generated: ${header.date}`, pageWidth - margin - 40, yPosition);
        yPosition += 15;

        return yPosition;
    }

    addPatientInfo(pdf, patientInfo, yPosition, pageWidth, margin) {
        pdf.setFontSize(14);
        pdf.setFont(undefined, 'bold');
        pdf.text('Patient Information', margin, yPosition);
        yPosition += 8;

        pdf.setFontSize(10);
        pdf.setFont(undefined, 'normal');
        
        const info = [
            `Name: ${patientInfo.name}`,
            `Patient ID: ${patientInfo.id}`,
            `Date of Birth: ${patientInfo.dateOfBirth}`,
            `Age: ${patientInfo.age}`,
            `Gender: ${patientInfo.gender}`,
            `Phone: ${patientInfo.phone}`,
            `Email: ${patientInfo.email}`
        ];

        info.forEach(line => {
            pdf.text(line, margin, yPosition);
            yPosition += 5;
        });

        yPosition += 10;
        return yPosition;
    }

    addTestResults(pdf, testResults, yPosition, pageWidth, margin, pageHeight) {
        pdf.setFontSize(14);
        pdf.setFont(undefined, 'bold');
        pdf.text('Test Results', margin, yPosition);
        yPosition += 10;

        // Table headers
        const headers = ['Test Name', 'Result', 'Unit', 'Reference Range', 'Status'];
        const colWidths = [50, 25, 15, 35, 20];
        let xPosition = margin;

        pdf.setFontSize(9);
        pdf.setFont(undefined, 'bold');
        
        headers.forEach((header, index) => {
            pdf.text(header, xPosition, yPosition);
            xPosition += colWidths[index];
        });
        
        yPosition += 7;

        // Table rows
        pdf.setFont(undefined, 'normal');
        testResults.forEach(test => {
            if (yPosition > pageHeight - 30) {
                pdf.addPage();
                yPosition = 20;
            }

            xPosition = margin;
            const values = [
                test.name,
                test.result,
                test.unit || '',
                test.referenceRange || '',
                test.status || 'Normal'
            ];

            // Set color based on status
            switch (test.status) {
                case 'Critical':
                    pdf.setTextColor(220, 38, 38); // Red
                    break;
                case 'Abnormal':
                    pdf.setTextColor(245, 158, 11); // Yellow
                    break;
                default:
                    pdf.setTextColor(0, 0, 0); // Black
            }

            values.forEach((value, index) => {
                pdf.text(String(value), xPosition, yPosition);
                xPosition += colWidths[index];
            });

            pdf.setTextColor(0, 0, 0); // Reset color
            yPosition += 6;
        });

        yPosition += 10;
        return yPosition;
    }

    addCharts(pdf, charts, yPosition, pageWidth, margin, pageHeight) {
        pdf.setFontSize(14);
        pdf.setFont(undefined, 'bold');
        pdf.text('Charts and Visualizations', margin, yPosition);
        yPosition += 10;

        charts.forEach((chart, index) => {
            if (yPosition > pageHeight - 80) {
                pdf.addPage();
                yPosition = 20;
            }

            try {
                const imgWidth = pageWidth - (margin * 2);
                const imgHeight = 60;
                
                pdf.addImage(chart.image, 'PNG', margin, yPosition, imgWidth, imgHeight);
                yPosition += imgHeight + 10;
            } catch (error) {
                console.warn('Could not add chart:', error);
                pdf.setFontSize(10);
                pdf.text(`[Chart: ${chart.type}]`, margin, yPosition);
                yPosition += 10;
            }
        });

        return yPosition;
    }

    addRecommendations(pdf, recommendations, yPosition, pageWidth, margin, pageHeight) {
        if (yPosition > pageHeight - 50) {
            pdf.addPage();
            yPosition = 20;
        }

        pdf.setFontSize(14);
        pdf.setFont(undefined, 'bold');
        pdf.text('AI Analysis & Recommendations', margin, yPosition);
        yPosition += 10;

        if (recommendations.summary) {
            pdf.setFontSize(12);
            pdf.setFont(undefined, 'bold');
            pdf.text('Summary', margin, yPosition);
            yPosition += 7;

            pdf.setFontSize(10);
            pdf.setFont(undefined, 'normal');
            const summaryLines = pdf.splitTextToSize(recommendations.summary, pageWidth - (margin * 2));
            pdf.text(summaryLines, margin, yPosition);
            yPosition += summaryLines.length * 5 + 10;
        }

        if (recommendations.recommendations && recommendations.recommendations.length > 0) {
            pdf.setFontSize(12);
            pdf.setFont(undefined, 'bold');
            pdf.text('Recommendations', margin, yPosition);
            yPosition += 7;

            pdf.setFontSize(10);
            pdf.setFont(undefined, 'normal');
            recommendations.recommendations.forEach((rec, index) => {
                pdf.text(`${index + 1}. ${rec}`, margin, yPosition);
                yPosition += 6;
            });
        }

        return yPosition;
    }

    addFooter(pdf, footer, pageWidth, pageHeight, margin) {
        const footerY = pageHeight - 15;
        
        pdf.setFontSize(8);
        pdf.setTextColor(128, 128, 128);
        
        if (footer.disclaimer) {
            const disclaimerLines = pdf.splitTextToSize(footer.disclaimer, pageWidth - (margin * 2));
            pdf.text(disclaimerLines, margin, footerY - 10);
        }

        pdf.text(footer.generatedBy, margin, footerY);
        pdf.text(`Generated: ${new Date(footer.timestamp).toLocaleString()}`, pageWidth - margin - 40, footerY);
    }

    downloadPDF(pdf, filename) {
        pdf.save(filename);
    }

    getFileName(options) {
        const date = new Date().toISOString().split('T')[0];
        const reportType = options.reportType.replace('_', '-');
        const patientName = this.currentReportData?.patient?.last_name || 'patient';
        
        return `${reportType}-${patientName}-${date}.pdf`;
    }

    getReportTitle(reportType) {
        const titles = {
            'patient_results': 'Laboratory Test Results',
            'ai_analysis': 'AI Analysis Report',
            'lab_summary': 'Laboratory Summary Report',
            'custom': 'Custom Laboratory Report'
        };
        return titles[reportType] || 'Laboratory Report';
    }

    calculateAge(dateOfBirth) {
        const today = new Date();
        const birthDate = new Date(dateOfBirth);
        let age = today.getFullYear() - birthDate.getFullYear();
        const monthDiff = today.getMonth() - birthDate.getMonth();
        
        if (monthDiff < 0 || (monthDiff === 0 && today.getDate() < birthDate.getDate())) {
            age--;
        }
        
        return age;
    }

    async previewReport() {
        // Create a preview modal or new window with report content
        const previewWindow = window.open('', '_blank', 'width=800,height=1000');
        const options = this.getReportOptions();
        const content = await this.buildReportContent(options);
        
        const previewHTML = this.buildPreviewHTML(content, options);
        previewWindow.document.write(previewHTML);
        previewWindow.document.close();
    }

    buildPreviewHTML(content, options) {
        return `
            <!DOCTYPE html>
            <html>
            <head>
                <title>Report Preview</title>
                <style>
                    body { font-family: Arial, sans-serif; margin: 20px; }
                    .header { border-bottom: 2px solid #2563EB; padding-bottom: 10px; margin-bottom: 20px; }
                    .section { margin-bottom: 20px; }
                    .section h3 { color: #2563EB; border-bottom: 1px solid #e5e7eb; padding-bottom: 5px; }
                    table { width: 100%; border-collapse: collapse; margin-top: 10px; }
                    th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
                    th { background-color: #f8f9fa; }
                    .critical { color: #dc2626; font-weight: bold; }
                    .abnormal { color: #f59e0b; font-weight: bold; }
                    .normal { color: #16a34a; }
                </style>
            </head>
            <body>
                ${this.generatePreviewContent(content, options)}
            </body>
            </html>
        `;
    }

    generatePreviewContent(content, options) {
        let html = '';

        if (content.header && options.includeBranding) {
            html += `
                <div class="header">
                    <h1>${content.header.labName}</h1>
                    <p>${content.header.address}<br>
                    ${content.header.phone} | ${content.header.email}<br>
                    ${content.header.website}</p>
                    <h2>${content.header.reportTitle}</h2>
                    <p>Report ID: ${content.header.reportId} | Date: ${content.header.date}</p>
                </div>
            `;
        }

        if (content.patientInfo) {
            html += `
                <div class="section">
                    <h3>Patient Information</h3>
                    <p><strong>Name:</strong> ${content.patientInfo.name}<br>
                    <strong>Patient ID:</strong> ${content.patientInfo.id}<br>
                    <strong>Date of Birth:</strong> ${content.patientInfo.dateOfBirth}<br>
                    <strong>Age:</strong> ${content.patientInfo.age}<br>
                    <strong>Gender:</strong> ${content.patientInfo.gender}</p>
                </div>
            `;
        }

        if (content.testResults) {
            html += `
                <div class="section">
                    <h3>Test Results</h3>
                    <table>
                        <thead>
                            <tr>
                                <th>Test Name</th>
                                <th>Result</th>
                                <th>Unit</th>
                                <th>Reference Range</th>
                                <th>Status</th>
                            </tr>
                        </thead>
                        <tbody>
            `;

            content.testResults.forEach(test => {
                const statusClass = test.status === 'Critical' ? 'critical' : 
                                  test.status === 'Abnormal' ? 'abnormal' : 'normal';
                html += `
                    <tr>
                        <td>${test.name}</td>
                        <td>${test.result}</td>
                        <td>${test.unit || ''}</td>
                        <td>${test.referenceRange || ''}</td>
                        <td class="${statusClass}">${test.status || 'Normal'}</td>
                    </tr>
                `;
            });

            html += `
                        </tbody>
                    </table>
                </div>
            `;
        }

        if (content.recommendations) {
            html += `
                <div class="section">
                    <h3>AI Analysis & Recommendations</h3>
                    ${content.recommendations.summary ? `<p><strong>Summary:</strong> ${content.recommendations.summary}</p>` : ''}
                    ${content.recommendations.recommendations ? `
                        <h4>Recommendations:</h4>
                        <ul>
                            ${content.recommendations.recommendations.map(rec => `<li>${rec}</li>`).join('')}
                        </ul>
                    ` : ''}
                </div>
            `;
        }

        return html;
    }

    setupEventListeners() {
        // Listen for report generation requests
        document.addEventListener('generatePDFReport', (event) => {
            this.open(event.detail.reportData);
        });
    }

    // Static method to trigger PDF generation
    static generateReport(reportData) {
        const event = new CustomEvent('generatePDFReport', {
            detail: { reportData }
        });
        document.dispatchEvent(event);
    }
}

// Initialize global instance
window.pdfReportGenerator = new PDFReportGenerator();

// Global function for template use
function generatePDFReport(reportData) {
    window.pdfReportGenerator.open(reportData);
}