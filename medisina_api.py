"""
MediSina API Integration Module
Handles patient data exchange with MediSina platform in JSON/Excel formats
"""
import json
import logging
import requests
import pandas as pd
from datetime import datetime, timedelta
from io import BytesIO
import base64

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_medisina_connection(api_url, api_key, username, password):
    """Test MediSina API connection"""
    try:
        if not all([api_url, api_key]):
            return {'success': False, 'error': 'API URL and API Key are required'}
        
        # Remove trailing slash from URL
        api_url = api_url.rstrip('/')
        
        # Test authentication endpoint
        auth_data = {}
        if username and password:
            auth_data = {'username': username, 'password': password}
        
        headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        
        # Test with a simple endpoint (usually /health or /status)
        test_endpoints = ['/health', '/status', '/api/v1/health', '/ping']
        
        for endpoint in test_endpoints:
            try:
                response = requests.get(
                    f"{api_url}{endpoint}",
                    headers=headers,
                    timeout=30
                )
                
                if response.status_code in [200, 201, 202]:
                    return {
                        'success': True,
                        'message': 'MediSina API connection successful',
                        'endpoint': endpoint,
                        'status_code': response.status_code,
                        'api_url': api_url
                    }
                    
            except requests.exceptions.RequestException:
                continue
        
        # If health endpoints fail, try authentication endpoint
        try:
            auth_response = requests.post(
                f"{api_url}/auth/login",
                headers=headers,
                json=auth_data,
                timeout=30
            )
            
            if auth_response.status_code in [200, 201, 401]:  # 401 is acceptable for testing
                return {
                    'success': True,
                    'message': 'MediSina API connection successful (auth endpoint)',
                    'status_code': auth_response.status_code,
                    'api_url': api_url
                }
                
        except requests.exceptions.RequestException:
            pass
        
        return {'success': False, 'error': 'Unable to connect to MediSina API. Check URL and credentials.'}
        
    except Exception as e:
        logger.error(f"MediSina connection test failed: {str(e)}")
        return {'success': False, 'error': f'Connection failed: {str(e)}'}

def export_to_medisina(settings, patient_ids=None):
    """Export patient data to MediSina platform"""
    try:
        from models import Patient, TestOrder, Report
        from app import db
        
        if not settings.medisina_enabled:
            return {'success': False, 'error': 'MediSina integration not enabled'}
        
        # Build query for patients
        query = Patient.query.filter_by(laboratory_id=settings.laboratory_id)
        if patient_ids:
            query = query.filter(Patient.id.in_(patient_ids))
        
        patients = query.all()
        
        if not patients:
            return {'success': False, 'error': 'No patients found for export'}
        
        # Prepare data for export
        export_data = {
            'export_info': {
                'timestamp': datetime.utcnow().isoformat(),
                'laboratory_id': settings.laboratory_id,
                'total_patients': len(patients),
                'export_format': 'medisina_v1'
            },
            'patients': []
        }
        
        for patient in patients:
            # Get patient's latest test results
            test_results = TestOrder.query.filter_by(
                patient_id=patient.id
            ).order_by(TestOrder.ordered_at.desc()).limit(50).all()
            
            # Get patient's latest reports
            reports = Report.query.filter_by(
                patient_id=patient.id
            ).order_by(Report.created_at.desc()).limit(10).all()
            
            patient_data = {
                'patient_info': {
                    'patient_id': patient.patient_id,
                    'first_name': patient.first_name,
                    'last_name': patient.last_name,
                    'date_of_birth': patient.date_of_birth.isoformat() if patient.date_of_birth else None,
                    'age': patient.age,
                    'gender': patient.gender,
                    'phone': patient.phone,
                    'email': patient.email,
                    'national_id': patient.national_id,
                    'address': patient.address,
                    'blood_type': patient.blood_type,
                    'height': patient.height,
                    'weight': patient.weight,
                    'bmi': patient.bmi
                },
                'medical_info': {
                    'medical_history': patient.medical_history,
                    'current_symptoms': patient.current_symptoms,
                    'pain_description': patient.pain_description,
                    'test_reason': patient.test_reason,
                    'disease_type': patient.disease_type,
                    'allergies': patient.allergies,
                    'current_medications': patient.current_medications
                },
                'emergency_contact': {
                    'name': patient.emergency_contact,
                    'phone': patient.emergency_phone,
                    'relation': patient.emergency_relation
                },
                'test_results': [],
                'ai_reports': []
            }
            
            # Add test results
            for test in test_results:
                patient_data['test_results'].append({
                    'order_number': test.order_number,
                    'test_type': test.test_type.name if test.test_type else None,
                    'result_value': test.result_value,
                    'result_unit': test.result_unit,
                    'result_status': test.result_status,
                    'reference_range': test.reference_range,
                    'ordered_at': test.ordered_at.isoformat() if test.ordered_at else None,
                    'completed_at': test.completed_at.isoformat() if test.completed_at else None,
                    'status': test.status
                })
            
            # Add AI reports
            for report in reports:
                report_data = {
                    'report_number': report.report_number,
                    'report_type': report.report_type,
                    'title': report.title,
                    'overall_assessment': report.overall_assessment,
                    'interpretation': report.interpretation,
                    'follow_up': report.follow_up,
                    'created_at': report.created_at.isoformat() if report.created_at else None,
                    'ai_confidence_score': report.ai_confidence_score
                }
                
                # Parse JSON fields
                if report.individual_tests:
                    try:
                        report_data['individual_tests'] = json.loads(report.individual_tests)
                    except:
                        pass
                
                if report.probable_diseases:
                    try:
                        report_data['probable_diseases'] = json.loads(report.probable_diseases)
                    except:
                        pass
                
                if report.recommendations:
                    try:
                        report_data['recommendations'] = json.loads(report.recommendations)
                    except:
                        pass
                
                patient_data['ai_reports'].append(report_data)
            
            export_data['patients'].append(patient_data)
        
        # Send data to MediSina API
        headers = {
            'Authorization': f'Bearer {settings.medisina_api_key}',
            'Content-Type': 'application/json'
        }
        
        api_url = settings.medisina_api_url.rstrip('/')
        
        response = requests.post(
            f"{api_url}/api/v1/patients/import",
            headers=headers,
            json=export_data,
            timeout=120
        )
        
        if response.status_code in [200, 201, 202]:
            result = response.json() if response.content else {}
            return {
                'success': True,
                'message': 'Data exported to MediSina successfully',
                'patient_count': len(patients),
                'medisina_response': result
            }
        else:
            return {
                'success': False,
                'error': f'MediSina API error: {response.status_code} - {response.text}'
            }
        
    except Exception as e:
        logger.error(f"MediSina export failed: {str(e)}")
        return {'success': False, 'error': f'Export failed: {str(e)}'}

def import_from_medisina(settings):
    """Import patient data from MediSina platform"""
    try:
        from models import Patient, TestType, TestOrder
        from app import db
        
        if not settings.medisina_enabled:
            return {'success': False, 'error': 'MediSina integration not enabled'}
        
        headers = {
            'Authorization': f'Bearer {settings.medisina_api_key}',
            'Content-Type': 'application/json'
        }
        
        api_url = settings.medisina_api_url.rstrip('/')
        
        # Get updated patient data from MediSina
        response = requests.get(
            f"{api_url}/api/v1/patients/export",
            headers=headers,
            params={
                'laboratory_id': settings.laboratory_id,
                'updated_since': (datetime.utcnow() - timedelta(days=7)).isoformat()
            },
            timeout=120
        )
        
        if response.status_code != 200:
            return {
                'success': False,
                'error': f'MediSina API error: {response.status_code} - {response.text}'
            }
        
        import_data = response.json()
        patients_data = import_data.get('patients', [])
        
        imported_count = 0
        updated_count = 0
        errors = []
        
        for patient_data in patients_data:
            try:
                patient_info = patient_data.get('patient_info', {})
                medical_info = patient_data.get('medical_info', {})
                
                # Find existing patient or create new
                existing_patient = Patient.query.filter_by(
                    patient_id=patient_info.get('patient_id'),
                    laboratory_id=settings.laboratory_id
                ).first()
                
                if existing_patient:
                    # Update existing patient
                    existing_patient.first_name = patient_info.get('first_name', existing_patient.first_name)
                    existing_patient.last_name = patient_info.get('last_name', existing_patient.last_name)
                    existing_patient.phone = patient_info.get('phone', existing_patient.phone)
                    existing_patient.email = patient_info.get('email', existing_patient.email)
                    existing_patient.medical_history = medical_info.get('medical_history', existing_patient.medical_history)
                    existing_patient.current_medications = medical_info.get('current_medications', existing_patient.current_medications)
                    updated_count += 1
                else:
                    # Create new patient
                    new_patient = Patient(
                        patient_id=patient_info.get('patient_id'),
                        first_name=patient_info.get('first_name'),
                        last_name=patient_info.get('last_name'),
                        date_of_birth=datetime.fromisoformat(patient_info['date_of_birth']).date() if patient_info.get('date_of_birth') else None,
                        age=patient_info.get('age'),
                        gender=patient_info.get('gender'),
                        phone=patient_info.get('phone'),
                        email=patient_info.get('email'),
                        national_id=patient_info.get('national_id'),
                        address=patient_info.get('address'),
                        medical_history=medical_info.get('medical_history'),
                        current_symptoms=medical_info.get('current_symptoms'),
                        allergies=medical_info.get('allergies'),
                        current_medications=medical_info.get('current_medications'),
                        laboratory_id=settings.laboratory_id
                    )
                    db.session.add(new_patient)
                    imported_count += 1
                
                db.session.commit()
                
            except Exception as e:
                errors.append({
                    'patient_id': patient_info.get('patient_id', 'Unknown'),
                    'error': str(e)
                })
                db.session.rollback()
        
        return {
            'success': True,
            'message': 'Data imported from MediSina successfully',
            'imported_count': imported_count,
            'updated_count': updated_count,
            'total_processed': len(patients_data),
            'errors': errors
        }
        
    except Exception as e:
        logger.error(f"MediSina import failed: {str(e)}")
        return {'success': False, 'error': f'Import failed: {str(e)}'}

def export_to_excel(patients_data, include_ai_analysis=True):
    """Export patient data to Excel format for MediSina compatibility"""
    try:
        output = BytesIO()
        
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            # Patient information sheet
            patient_info = []
            for patient in patients_data:
                info = patient.get('patient_info', {})
                patient_info.append({
                    'Patient ID': info.get('patient_id'),
                    'First Name': info.get('first_name'),
                    'Last Name': info.get('last_name'),
                    'Date of Birth': info.get('date_of_birth'),
                    'Age': info.get('age'),
                    'Gender': info.get('gender'),
                    'Phone': info.get('phone'),
                    'Email': info.get('email'),
                    'National ID': info.get('national_id'),
                    'Address': info.get('address'),
                    'Blood Type': info.get('blood_type'),
                    'Height (cm)': info.get('height'),
                    'Weight (kg)': info.get('weight'),
                    'BMI': info.get('bmi')
                })
            
            if patient_info:
                df = pd.DataFrame(patient_info)
                df.to_excel(writer, sheet_name='Patient_Info', index=False)
            
            # Medical information sheet
            medical_info = []
            for patient in patients_data:
                info = patient.get('patient_info', {})
                medical = patient.get('medical_info', {})
                medical_info.append({
                    'Patient ID': info.get('patient_id'),
                    'Patient Name': f"{info.get('first_name', '')} {info.get('last_name', '')}",
                    'Medical History': medical.get('medical_history'),
                    'Current Symptoms': medical.get('current_symptoms'),
                    'Pain Description': medical.get('pain_description'),
                    'Test Reason': medical.get('test_reason'),
                    'Disease Type': medical.get('disease_type'),
                    'Allergies': medical.get('allergies'),
                    'Current Medications': medical.get('current_medications')
                })
            
            if medical_info:
                df = pd.DataFrame(medical_info)
                df.to_excel(writer, sheet_name='Medical_Info', index=False)
            
            # Test results sheet
            test_results = []
            for patient in patients_data:
                info = patient.get('patient_info', {})
                for test in patient.get('test_results', []):
                    test_results.append({
                        'Patient ID': info.get('patient_id'),
                        'Patient Name': f"{info.get('first_name', '')} {info.get('last_name', '')}",
                        'Order Number': test.get('order_number'),
                        'Test Type': test.get('test_type'),
                        'Result Value': test.get('result_value'),
                        'Result Unit': test.get('result_unit'),
                        'Result Status': test.get('result_status'),
                        'Reference Range': test.get('reference_range'),
                        'Ordered Date': test.get('ordered_at'),
                        'Completed Date': test.get('completed_at'),
                        'Status': test.get('status')
                    })
            
            if test_results:
                df = pd.DataFrame(test_results)
                df.to_excel(writer, sheet_name='Test_Results', index=False)
            
            # AI Reports sheet (if enabled)
            if include_ai_analysis:
                ai_reports = []
                for patient in patients_data:
                    info = patient.get('patient_info', {})
                    for report in patient.get('ai_reports', []):
                        ai_reports.append({
                            'Patient ID': info.get('patient_id'),
                            'Patient Name': f"{info.get('first_name', '')} {info.get('last_name', '')}",
                            'Report Number': report.get('report_number'),
                            'Report Type': report.get('report_type'),
                            'Title': report.get('title'),
                            'Overall Assessment': report.get('overall_assessment'),
                            'Interpretation': report.get('interpretation'),
                            'Follow Up': report.get('follow_up'),
                            'AI Confidence': report.get('ai_confidence_score'),
                            'Created Date': report.get('created_at')
                        })
                
                if ai_reports:
                    df = pd.DataFrame(ai_reports)
                    df.to_excel(writer, sheet_name='AI_Reports', index=False)
        
        output.seek(0)
        return {
            'success': True,
            'excel_data': output.getvalue(),
            'filename': f'medisina_export_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
        }
        
    except Exception as e:
        logger.error(f"Excel export failed: {str(e)}")
        return {'success': False, 'error': f'Excel export failed: {str(e)}'}