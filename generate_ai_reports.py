#!/usr/bin/env python3
"""
Generate comprehensive AI reports for all sample patients
"""
import json
from datetime import datetime, date
from app import app, db
from models import Patient, Report, TestOrder, TestType
from ai_reports import generate_patient_report_analysis

def create_sample_test_data():
    """Create sample test results for patients based on their medical conditions"""
    
    # Sample test data for different medical conditions
    test_profiles = {
        'فشار خون بالا': {
            'Glucose': {'value': 95, 'unit': 'mg/dL', 'reference': '70-100', 'status': 'normal'},
            'BUN': {'value': 18, 'unit': 'mg/dL', 'reference': '6-24', 'status': 'normal'},
            'Creatinine': {'value': 1.0, 'unit': 'mg/dL', 'reference': '0.6-1.3', 'status': 'normal'},
            'Sodium': {'value': 140, 'unit': 'mEq/L', 'reference': '136-146', 'status': 'normal'},
            'Potassium': {'value': 4.0, 'unit': 'mEq/L', 'reference': '3.5-5.0', 'status': 'normal'},
            'Total_Cholesterol': {'value': 265, 'unit': 'mg/dL', 'reference': '<200', 'status': 'abnormal'},
            'LDL': {'value': 180, 'unit': 'mg/dL', 'reference': '<100', 'status': 'critical'},
            'HDL': {'value': 32, 'unit': 'mg/dL', 'reference': '>40', 'status': 'critical'},
            'Triglycerides': {'value': 210, 'unit': 'mg/dL', 'reference': '<150', 'status': 'abnormal'}
        },
        'دیابت نوع 2': {
            'Glucose': {'value': 185, 'unit': 'mg/dL', 'reference': '70-100', 'status': 'critical'},
            'HbA1c': {'value': 8.2, 'unit': '%', 'reference': '<7.0', 'status': 'abnormal'},
            'BUN': {'value': 28, 'unit': 'mg/dL', 'reference': '6-24', 'status': 'abnormal'},
            'Creatinine': {'value': 1.4, 'unit': 'mg/dL', 'reference': '0.6-1.3', 'status': 'abnormal'},
            'Total_Cholesterol': {'value': 220, 'unit': 'mg/dL', 'reference': '<200', 'status': 'abnormal'},
            'LDL': {'value': 135, 'unit': 'mg/dL', 'reference': '<100', 'status': 'abnormal'},
            'HDL': {'value': 38, 'unit': 'mg/dL', 'reference': '>40', 'status': 'low'},
            'Triglycerides': {'value': 280, 'unit': 'mg/dL', 'reference': '<150', 'status': 'abnormal'}
        },
        'هیپوتیروئیدی': {
            'TSH': {'value': 12.5, 'unit': 'mIU/L', 'reference': '0.4-4.0', 'status': 'critical'},
            'T4': {'value': 4.2, 'unit': 'μg/dL', 'reference': '4.5-12.0', 'status': 'low'},
            'T3': {'value': 75, 'unit': 'ng/dL', 'reference': '80-200', 'status': 'low'},
            'Glucose': {'value': 88, 'unit': 'mg/dL', 'reference': '70-100', 'status': 'normal'},
            'Total_Cholesterol': {'value': 245, 'unit': 'mg/dL', 'reference': '<200', 'status': 'abnormal'},
            'LDL': {'value': 155, 'unit': 'mg/dL', 'reference': '<100', 'status': 'abnormal'}
        },
        'بیماری مزمن ریوی': {
            'Hemoglobin': {'value': 16.8, 'unit': 'g/dL', 'reference': '12.0-15.5', 'status': 'abnormal'},
            'Hematocrit': {'value': 52, 'unit': '%', 'reference': '36-46', 'status': 'abnormal'},
            'WBC': {'value': 8500, 'unit': '/μL', 'reference': '4000-11000', 'status': 'normal'},
            'BUN': {'value': 22, 'unit': 'mg/dL', 'reference': '6-24', 'status': 'normal'},
            'Creatinine': {'value': 1.1, 'unit': 'mg/dL', 'reference': '0.6-1.3', 'status': 'normal'}
        },
        'کم‌خونی فقر آهن': {
            'Hemoglobin': {'value': 8.5, 'unit': 'g/dL', 'reference': '12.0-15.5', 'status': 'critical'},
            'Hematocrit': {'value': 24, 'unit': '%', 'reference': '36-46', 'status': 'critical'},
            'Iron': {'value': 35, 'unit': 'μg/dL', 'reference': '60-170', 'status': 'low'},
            'TIBC': {'value': 420, 'unit': 'μg/dL', 'reference': '250-400', 'status': 'abnormal'},
            'Ferritin': {'value': 8, 'unit': 'ng/mL', 'reference': '15-150', 'status': 'critical'}
        },
        'سنگ کلیه': {
            'BUN': {'value': 32, 'unit': 'mg/dL', 'reference': '6-24', 'status': 'abnormal'},
            'Creatinine': {'value': 1.6, 'unit': 'mg/dL', 'reference': '0.6-1.3', 'status': 'abnormal'},
            'Calcium': {'value': 11.2, 'unit': 'mg/dL', 'reference': '8.5-10.5', 'status': 'abnormal'},
            'Uric_Acid': {'value': 8.8, 'unit': 'mg/dL', 'reference': '3.4-7.0', 'status': 'abnormal'},
            'Phosphorus': {'value': 4.8, 'unit': 'mg/dL', 'reference': '2.5-4.5', 'status': 'abnormal'}
        },
        'حاملگی': {
            'Hemoglobin': {'value': 10.8, 'unit': 'g/dL', 'reference': '11.0-14.0', 'status': 'low'},
            'Hematocrit': {'value': 32, 'unit': '%', 'reference': '33-40', 'status': 'low'},
            'Glucose': {'value': 92, 'unit': 'mg/dL', 'reference': '70-100', 'status': 'normal'},
            'Iron': {'value': 55, 'unit': 'μg/dL', 'reference': '60-170', 'status': 'low'},
            'Ferritin': {'value': 18, 'unit': 'ng/mL', 'reference': '15-150', 'status': 'normal'}
        },
        'normal': {
            'Glucose': {'value': 85, 'unit': 'mg/dL', 'reference': '70-100', 'status': 'normal'},
            'BUN': {'value': 15, 'unit': 'mg/dL', 'reference': '6-24', 'status': 'normal'},
            'Creatinine': {'value': 0.9, 'unit': 'mg/dL', 'reference': '0.6-1.3', 'status': 'normal'},
            'Total_Cholesterol': {'value': 165, 'unit': 'mg/dL', 'reference': '<200', 'status': 'normal'},
            'LDL': {'value': 95, 'unit': 'mg/dL', 'reference': '<100', 'status': 'normal'},
            'HDL': {'value': 52, 'unit': 'mg/dL', 'reference': '>40', 'status': 'normal'},
            'Hemoglobin': {'value': 14.2, 'unit': 'g/dL', 'reference': '12.0-15.5', 'status': 'normal'}
        },
        'افسردگی': {
            'Glucose': {'value': 88, 'unit': 'mg/dL', 'reference': '70-100', 'status': 'normal'},
            'TSH': {'value': 2.8, 'unit': 'mIU/L', 'reference': '0.4-4.0', 'status': 'normal'},
            'T4': {'value': 7.2, 'unit': 'μg/dL', 'reference': '4.5-12.0', 'status': 'normal'},
            'Vitamin_D': {'value': 18, 'unit': 'ng/mL', 'reference': '30-100', 'status': 'low'},
            'B12': {'value': 285, 'unit': 'pg/mL', 'reference': '300-900', 'status': 'low'}
        }
    }
    
    return test_profiles

def generate_reports_for_all_patients():
    """Generate AI reports for all patients"""
    
    with app.app_context():
        # Get all patients
        patients = Patient.query.all()
        test_profiles = create_sample_test_data()
        
        reports_created = 0
        
        for patient in patients:
            # Skip if patient already has reports
            existing_reports = Report.query.filter_by(patient_id=patient.id).count()
            if existing_reports > 0:
                continue
                
            # Determine test profile based on patient's disease type
            disease_type = patient.disease_type or 'normal'
            if disease_type not in test_profiles:
                disease_type = 'normal'
            
            test_data = test_profiles[disease_type]
            
            # Prepare patient data for AI analysis
            patient_data = {
                'name': f"{patient.first_name} {patient.last_name}",
                'age': (date.today() - patient.date_of_birth).days // 365 if patient.date_of_birth else None,
                'gender': patient.gender,
                'medical_history': patient.medical_history,
                'medications': getattr(patient, 'current_medications', '') or getattr(patient, 'medications', ''),
                'allergies': patient.allergies,
                'current_symptoms': patient.current_symptoms,
                'disease_type': patient.disease_type,
                'chief_complaint': getattr(patient, 'chief_complaint', ''),
                'pain_description': getattr(patient, 'pain_description', ''),
                'test_reason': getattr(patient, 'test_reason', '')
            }
            
            # Convert test data to expected format
            test_results = []
            for test_name, test_info in test_data.items():
                test_results.append({
                    'test_name': test_name,
                    'result_value': test_info['value'],
                    'unit': test_info['unit'],
                    'reference_range': test_info['reference'],
                    'status': test_info['status']
                })
            
            # Generate AI analysis
            ai_analysis = generate_patient_report_analysis(patient_data, test_results)
            
            if ai_analysis['success']:
                # Generate unique report number
                report_count = Report.query.count()
                report_number = f"RPT{datetime.now().strftime('%Y%m%d')}{str(report_count + 1).zfill(4)}"
                
                # Create report record
                analysis_data = ai_analysis['analysis']
                
                # Create appropriate title based on patient condition
                if disease_type == 'normal':
                    title = f"گزارش چک‌آپ سالانه - {patient.first_name} {patient.last_name}"
                else:
                    title = f"تحلیل جامع آزمایشات - {patient.first_name} {patient.last_name}"
                
                report = Report(
                    report_number=report_number,
                    patient_id=patient.id,
                    report_type='comprehensive',
                    title=title,
                    overall_assessment=analysis_data.get('overall_assessment', ''),
                    individual_tests=json.dumps(analysis_data.get('individual_tests', {}), ensure_ascii=False),
                    probable_diseases=json.dumps(analysis_data.get('probable_diseases', {}), ensure_ascii=False),
                    recommendations=json.dumps(analysis_data.get('recommendations', []), ensure_ascii=False),
                    red_flags=json.dumps(analysis_data.get('red_flags', []), ensure_ascii=False),
                    interpretation=analysis_data.get('interpretation', ''),
                    follow_up=analysis_data.get('follow_up', ''),
                    ai_confidence_score=0.85,
                    language='fa',
                    status='final'
                )
                
                db.session.add(report)
                reports_created += 1
                
                print(f"Created report for patient: {patient.first_name} {patient.last_name}")
        
        db.session.commit()
        print(f"\nSuccessfully created {reports_created} AI reports!")
        
        # Print summary
        total_reports = Report.query.count()
        total_patients = Patient.query.count()
        print(f"Total patients: {total_patients}")
        print(f"Total reports: {total_reports}")

if __name__ == "__main__":
    generate_reports_for_all_patients()