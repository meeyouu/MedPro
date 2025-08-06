"""
Enhanced report generation script for all patients with synchronized data
"""

import json
from app import app, db
from models import Patient, Report
from ai_reports import generate_patient_report_analysis
from ai_report_prompts import get_detailed_disease_analysis_prompt

def generate_all_enhanced_reports():
    """Generate enhanced reports for all patients with proper disease analysis"""
    
    with app.app_context():
        patients = Patient.query.all()
        
        # Sample lab results for each patient type
        lab_results_templates = {
            1: [  # Cardiovascular patient
                {'test_name': 'کلسترول کل', 'result_value': '265', 'unit': 'mg/dL', 'reference_range': '<200', 'status': 'بالا'},
                {'test_name': 'LDL', 'result_value': '180', 'unit': 'mg/dL', 'reference_range': '<100', 'status': 'بسیار بالا'},
                {'test_name': 'HDL', 'result_value': '32', 'unit': 'mg/dL', 'reference_range': '>40', 'status': 'پایین'},
                {'test_name': 'تری‌گلیسرید', 'result_value': '210', 'unit': 'mg/dL', 'reference_range': '<150', 'status': 'بالا'},
                {'test_name': 'فشار خون', 'result_value': '145/95', 'unit': 'mmHg', 'reference_range': '<120/80', 'status': 'بالا'}
            ],
            2: [  # Diabetes patient
                {'test_name': 'گلوکز ناشتا', 'result_value': '185', 'unit': 'mg/dL', 'reference_range': '70-100', 'status': 'بسیار بالا'},
                {'test_name': 'HbA1c', 'result_value': '8.2', 'unit': '%', 'reference_range': '<7', 'status': 'بالا'},
                {'test_name': 'کراتینین', 'result_value': '1.4', 'unit': 'mg/dL', 'reference_range': '0.7-1.3', 'status': 'بالا'},
                {'test_name': 'BUN', 'result_value': '28', 'unit': 'mg/dL', 'reference_range': '7-20', 'status': 'بالا'},
                {'test_name': 'تری‌گلیسرید', 'result_value': '280', 'unit': 'mg/dL', 'reference_range': '<150', 'status': 'بسیار بالا'}
            ],
            3: [  # Healthy patient
                {'test_name': 'گلوکز ناشتا', 'result_value': '88', 'unit': 'mg/dL', 'reference_range': '70-100', 'status': 'طبیعی'},
                {'test_name': 'کلسترول کل', 'result_value': '175', 'unit': 'mg/dL', 'reference_range': '<200', 'status': 'طبیعی'},
                {'test_name': 'HDL', 'result_value': '55', 'unit': 'mg/dL', 'reference_range': '>40', 'status': 'طبیعی'},
                {'test_name': 'کراتینین', 'result_value': '1.0', 'unit': 'mg/dL', 'reference_range': '0.7-1.3', 'status': 'طبیعی'},
                {'test_name': 'ALT', 'result_value': '22', 'unit': 'U/L', 'reference_range': '<40', 'status': 'طبیعی'}
            ],
            4: [  # Thyroid patient
                {'test_name': 'TSH', 'result_value': '12.5', 'unit': 'mIU/L', 'reference_range': '0.4-4.0', 'status': 'بسیار بالا'},
                {'test_name': 'T4 آزاد', 'result_value': '4.2', 'unit': 'μg/dL', 'reference_range': '4.5-12.0', 'status': 'پایین'},
                {'test_name': 'کلسترول کل', 'result_value': '245', 'unit': 'mg/dL', 'reference_range': '<200', 'status': 'بالا'},
                {'test_name': 'LDL', 'result_value': '155', 'unit': 'mg/dL', 'reference_range': '<100', 'status': 'بالا'},
                {'test_name': 'هموگلوبین', 'result_value': '11.2', 'unit': 'g/dL', 'reference_range': '12-15', 'status': 'پایین'}
            ],
            5: [  # COPD patient
                {'test_name': 'هموگلوبین', 'result_value': '16.8', 'unit': 'g/dL', 'reference_range': '13.5-17.5', 'status': 'بالا'},
                {'test_name': 'هماتوکریت', 'result_value': '52', 'unit': '%', 'reference_range': '41-50', 'status': 'بالا'},
                {'test_name': 'گلبول‌های قرمز', 'result_value': '5.8', 'unit': 'M/μL', 'reference_range': '4.7-6.1', 'status': 'بالا'},
                {'test_name': 'اکسیژن خون', 'result_value': '88', 'unit': '%', 'reference_range': '>95', 'status': 'پایین'},
                {'test_name': 'CO2', 'result_value': '48', 'unit': 'mmHg', 'reference_range': '35-45', 'status': 'بالا'}
            ],
            6: [  # Iron deficiency patient
                {'test_name': 'هموگلوبین', 'result_value': '8.5', 'unit': 'g/dL', 'reference_range': '12-15', 'status': 'بسیار پایین'},
                {'test_name': 'فریتین', 'result_value': '8', 'unit': 'ng/mL', 'reference_range': '15-150', 'status': 'بسیار پایین'},
                {'test_name': 'آهن سرم', 'result_value': '45', 'unit': 'μg/dL', 'reference_range': '60-170', 'status': 'پایین'},
                {'test_name': 'TIBC', 'result_value': '450', 'unit': 'μg/dL', 'reference_range': '250-400', 'status': 'بالا'},
                {'test_name': 'هماتوکریت', 'result_value': '25', 'unit': '%', 'reference_range': '36-46', 'status': 'بسیار پایین'}
            ],
            7: [  # Kidney stone patient
                {'test_name': 'کراتینین', 'result_value': '1.6', 'unit': 'mg/dL', 'reference_range': '0.7-1.3', 'status': 'بالا'},
                {'test_name': 'BUN', 'result_value': '32', 'unit': 'mg/dL', 'reference_range': '7-20', 'status': 'بالا'},
                {'test_name': 'کلسیم', 'result_value': '11.2', 'unit': 'mg/dL', 'reference_range': '8.5-10.5', 'status': 'بالا'},
                {'test_name': 'اوریک اسید', 'result_value': '8.5', 'unit': 'mg/dL', 'reference_range': '3.5-7.2', 'status': 'بالا'},
                {'test_name': 'فسفر', 'result_value': '2.8', 'unit': 'mg/dL', 'reference_range': '2.5-4.5', 'status': 'طبیعی'}
            ],
            8: [  # Pregnancy patient
                {'test_name': 'هموگلوبین', 'result_value': '10.8', 'unit': 'g/dL', 'reference_range': '11-14', 'status': 'پایین'},
                {'test_name': 'فریتین', 'result_value': '18', 'unit': 'ng/mL', 'reference_range': '15-150', 'status': 'پایین'},
                {'test_name': 'گلوکز', 'result_value': '92', 'unit': 'mg/dL', 'reference_range': '70-100', 'status': 'طبیعی'},
                {'test_name': 'فولیک اسید', 'result_value': '12', 'unit': 'ng/mL', 'reference_range': '>6', 'status': 'طبیعی'},
                {'test_name': 'Beta-hCG', 'result_value': '45000', 'unit': 'mIU/mL', 'reference_range': '25700-288000', 'status': 'طبیعی'}
            ],
            9: [  # Depression patient
                {'test_name': 'ویتامین D', 'result_value': '18', 'unit': 'ng/mL', 'reference_range': '30-100', 'status': 'پایین'},
                {'test_name': 'ویتامین B12', 'result_value': '285', 'unit': 'pg/mL', 'reference_range': '300-900', 'status': 'پایین'},
                {'test_name': 'TSH', 'result_value': '2.8', 'unit': 'mIU/L', 'reference_range': '0.4-4.0', 'status': 'طبیعی'},
                {'test_name': 'هموگلوبین', 'result_value': '13.2', 'unit': 'g/dL', 'reference_range': '13.5-17.5', 'status': 'کمی پایین'},
                {'test_name': 'فولیک اسید', 'result_value': '8', 'unit': 'ng/mL', 'reference_range': '>6', 'status': 'طبیعی'}
            ],
            10: [  # Healthy patient
                {'test_name': 'گلوکز ناشتا', 'result_value': '85', 'unit': 'mg/dL', 'reference_range': '70-100', 'status': 'طبیعی'},
                {'test_name': 'کلسترول کل', 'result_value': '165', 'unit': 'mg/dL', 'reference_range': '<200', 'status': 'طبیعی'},
                {'test_name': 'HDL', 'result_value': '62', 'unit': 'mg/dL', 'reference_range': '>50', 'status': 'طبیعی'},
                {'test_name': 'هموگلوبین', 'result_value': '13.8', 'unit': 'g/dL', 'reference_range': '12-15', 'status': 'طبیعی'},
                {'test_name': 'TSH', 'result_value': '1.5', 'unit': 'mIU/L', 'reference_range': '0.4-4.0', 'status': 'طبیعی'}
            ]
        }
        
        for patient in patients:
            print(f"Processing patient {patient.id}: {patient.first_name} {patient.last_name}")
            
            # Get lab results for this patient
            lab_results = lab_results_templates.get(patient.id, lab_results_templates[3])  # Default to healthy
            
            # Prepare patient data
            patient_data = {
                'first_name': patient.first_name,
                'last_name': patient.last_name,
                'age': 2024 - patient.date_of_birth.year if patient.date_of_birth else 35,
                'gender': patient.gender,
                'current_symptoms': patient.current_symptoms,
                'pain_description': patient.pain_description,
                'test_reason': patient.test_reason,
                'disease_type': patient.disease_type,
                'current_medications': patient.current_medications,
                'medical_history': patient.medical_history,
                'allergies': patient.allergies or 'آلرژی شناخته‌شده‌ای ندارد'
            }
            
            try:
                # Generate AI analysis
                analysis = generate_patient_report_analysis(patient_data, lab_results)
                print(f"Generated analysis for patient {patient.id}")
                
            except Exception as e:
                print(f"Error generating analysis for patient {patient.id}: {e}")
                continue

if __name__ == "__main__":
    generate_all_enhanced_reports()