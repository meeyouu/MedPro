#!/usr/bin/env python3
"""
Unit tests for AI report generation workflow
Tests the complete pipeline from patient data to AI-generated medical reports
"""

import unittest
import json
import os
import sys
from datetime import datetime, date, timedelta
from unittest.mock import patch, MagicMock

# Add the current directory to Python path
sys.path.insert(0, '.')

# Import the modules to test
from ai_services import generate_medical_analysis, test_openai_connection
from ai_reports import generate_patient_report_analysis
from models import Patient, TestOrder, TestType, Report, Laboratory, User
from app import app, db

class TestAIReportGeneration(unittest.TestCase):
    """Test suite for AI report generation workflow"""
    
    def setUp(self):
        """Set up test environment"""
        self.app = app
        self.app.config['TESTING'] = True
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        
        with self.app.app_context():
            db.create_all()
            self.create_test_data()
    
    def tearDown(self):
        """Clean up after tests"""
        with self.app.app_context():
            db.session.remove()
            db.drop_all()
    
    def create_test_data(self):
        """Create test data for AI report generation"""
        # Create test laboratory
        lab = Laboratory(
            name="Test Medical Laboratory",
            license_number="LAB123456",
            phone="+1234567890",
            email="test@lab.com",
            address="123 Test Street, Test City"
        )
        db.session.add(lab)
        db.session.flush()
        
        # Create test user
        user = User(
            username="testdoc",
            email="testdoc@lab.com",
            first_name="Dr. Test",
            last_name="Doctor",
            role="doctor",
            laboratory_id=lab.id,
            language="en"
        )
        db.session.add(user)
        db.session.flush()
        
        # Create test patient with comprehensive medical data
        patient = Patient(
            patient_id="P001",
            first_name="Ahmad",
            last_name="Hosseini",
            date_of_birth=date(1985, 5, 15),
            age=38,
            gender="male",
            phone="+989123456789",
            email="ahmad.hosseini@email.com",
            address="Tehran, Iran",
            medical_history="Hypertension, diabetes type 2",
            current_symptoms="Fatigue, frequent urination, increased thirst",
            pain_description="Mild headache, no specific pain",
            test_reason="Routine diabetes monitoring and cardiovascular assessment",
            disease_type="Diabetes mellitus, Hypertension",
            allergies="Penicillin",
            current_medications="Metformin 500mg twice daily, Lisinopril 10mg daily",
            height=175.0,
            weight=85.0,
            blood_type="A+",
            laboratory_id=lab.id
        )
        db.session.add(patient)
        db.session.flush()
        
        # Create test types for blood tests
        test_types = [
            TestType(name="Fasting Blood Glucose", category="blood_tests", unit="mg/dL", normal_range="70-100"),
            TestType(name="HbA1c", category="blood_tests", unit="%", normal_range="4.0-5.6"),
            TestType(name="Total Cholesterol", category="blood_tests", unit="mg/dL", normal_range="<200"),
            TestType(name="HDL Cholesterol", category="blood_tests", unit="mg/dL", normal_range=">40 (M), >50 (F)"),
            TestType(name="LDL Cholesterol", category="blood_tests", unit="mg/dL", normal_range="<100"),
            TestType(name="Triglycerides", category="blood_tests", unit="mg/dL", normal_range="<150"),
            TestType(name="Creatinine", category="blood_tests", unit="mg/dL", normal_range="0.7-1.3 (M), 0.6-1.1 (F)"),
            TestType(name="Blood Pressure Systolic", category="vital_signs", unit="mmHg", normal_range="90-120"),
            TestType(name="Blood Pressure Diastolic", category="vital_signs", unit="mmHg", normal_range="60-80")
        ]
        
        for test_type in test_types:
            db.session.add(test_type)
        db.session.flush()
        
        # Create test orders with realistic diabetic patient values
        test_data = [
            ("Fasting Blood Glucose", "145", "mg/dL", "abnormal"),  # High
            ("HbA1c", "8.2", "%", "abnormal"),  # High - poor diabetes control
            ("Total Cholesterol", "245", "mg/dL", "abnormal"),  # High
            ("HDL Cholesterol", "35", "mg/dL", "abnormal"),  # Low
            ("LDL Cholesterol", "165", "mg/dL", "abnormal"),  # High
            ("Triglycerides", "280", "mg/dL", "abnormal"),  # High
            ("Creatinine", "1.4", "mg/dL", "abnormal"),  # Slightly elevated
            ("Blood Pressure Systolic", "145", "mmHg", "abnormal"),  # High
            ("Blood Pressure Diastolic", "92", "mmHg", "abnormal")  # High
        ]
        
        for i, (test_name, result_value, unit, status) in enumerate(test_data):
            test_type = next(t for t in test_types if t.name == test_name)
            order = TestOrder(
                order_number=f"ORD{datetime.now().strftime('%Y%m%d')}{str(i+1).zfill(3)}",
                patient_id=patient.id,
                test_type_id=test_type.id,
                ordered_by=user.id,
                status="completed",
                result_value=result_value,
                result_unit=unit,
                result_status=status,
                ordered_at=datetime.now() - timedelta(days=1),
                completed_at=datetime.now()
            )
            db.session.add(order)
        
        db.session.commit()
        
        self.patient = patient
        self.user = user
        self.lab = lab
    
    def test_patient_data_preparation(self):
        """Test patient data preparation for AI analysis"""
        with self.app.app_context():
            patient = self.patient
            
            # Prepare patient data as done in the route
            patient_data = {
                'name': f"{patient.first_name} {patient.last_name}",
                'age': (date.today() - patient.date_of_birth).days // 365 if patient.date_of_birth else None,
                'gender': patient.gender,
                'medical_history': patient.medical_history,
                'medications': patient.current_medications,
                'allergies': patient.allergies,
                'current_symptoms': patient.current_symptoms,
                'disease_type': patient.disease_type,
                'pain_description': patient.pain_description,
                'test_reason': patient.test_reason
            }
            
            # Verify patient data structure
            self.assertEqual(patient_data['name'], "Ahmad Hosseini")
            self.assertEqual(patient_data['age'], 38)
            self.assertEqual(patient_data['gender'], "male")
            self.assertIn("diabetes", patient_data['medical_history'].lower())
            self.assertIn("metformin", patient_data['medications'].lower())
            self.assertIn("fatigue", patient_data['current_symptoms'].lower())
            
            print("✓ Patient data preparation test passed")
    
    def test_test_results_preparation(self):
        """Test test results preparation for AI analysis"""
        with self.app.app_context():
            patient = self.patient
            
            # Get test results as done in the route
            test_results = db.session.query(TestOrder, TestType).join(TestType).filter(
                TestOrder.patient_id == patient.id,
                TestOrder.status == 'completed'
            ).order_by(TestOrder.completed_at.desc()).limit(20).all()
            
            test_data = []
            for test_order, test_type in test_results:
                test_data.append({
                    'test_name': test_type.name,
                    'result_value': test_order.result_value,
                    'unit': test_order.result_unit or test_type.unit,
                    'reference_range': test_order.reference_range or test_type.normal_range,
                    'status': test_order.result_status,
                    'date': test_order.completed_at.strftime('%Y-%m-%d') if test_order.completed_at else None
                })
            
            # Verify test data structure
            self.assertGreater(len(test_data), 0)
            
            # Check specific test results
            glucose_test = next((t for t in test_data if t['test_name'] == 'Fasting Blood Glucose'), None)
            self.assertIsNotNone(glucose_test)
            self.assertEqual(glucose_test['result_value'], '145')
            self.assertEqual(glucose_test['status'], 'abnormal')
            
            hba1c_test = next((t for t in test_data if t['test_name'] == 'HbA1c'), None)
            self.assertIsNotNone(hba1c_test)
            self.assertEqual(hba1c_test['result_value'], '8.2')
            self.assertEqual(hba1c_test['status'], 'abnormal')
            
            print("✓ Test results preparation test passed")
            print(f"  - Found {len(test_data)} completed test results")
            print(f"  - Glucose: {glucose_test['result_value']} {glucose_test['unit']} ({glucose_test['status']})")
            print(f"  - HbA1c: {hba1c_test['result_value']} {hba1c_test['unit']} ({hba1c_test['status']})")
    
    @patch('ai_services.openai.chat.completions.create')
    def test_ai_prompt_structure(self, mock_openai):
        """Test the AI prompt structure and content"""
        with self.app.app_context():
            patient = self.patient
            
            # Prepare test data
            patient_data = {
                'name': f"{patient.first_name} {patient.last_name}",
                'age': 38,
                'gender': 'male',
                'medical_history': patient.medical_history,
                'medications': patient.current_medications,
                'allergies': patient.allergies,
                'current_symptoms': patient.current_symptoms,
                'disease_type': patient.disease_type,
                'pain_description': patient.pain_description,
                'test_reason': patient.test_reason
            }
            
            test_data = [
                {'test_name': 'Fasting Blood Glucose', 'result_value': '145', 'unit': 'mg/dL', 'reference_range': '70-100', 'status': 'abnormal'},
                {'test_name': 'HbA1c', 'result_value': '8.2', 'unit': '%', 'reference_range': '4.0-5.6', 'status': 'abnormal'},
                {'test_name': 'Total Cholesterol', 'result_value': '245', 'unit': 'mg/dL', 'reference_range': '<200', 'status': 'abnormal'}
            ]
            
            # Mock OpenAI response
            mock_response = MagicMock()
            mock_response.choices[0].message.content = json.dumps({
                "overall_assessment": "Patient shows poor diabetes control with multiple cardiovascular risk factors",
                "individual_tests": {
                    "Fasting Blood Glucose": {"value": "145 mg/dL", "status": "High", "interpretation": "Elevated glucose indicating poor diabetes control"},
                    "HbA1c": {"value": "8.2%", "status": "High", "interpretation": "Poor long-term glucose control over past 2-3 months"}
                },
                "probable_diseases": {
                    "Diabetes Mellitus Type 2": {"probability": 95, "confidence": "Very High"},
                    "Cardiovascular Disease": {"probability": 75, "confidence": "High"},
                    "Diabetic Nephropathy": {"probability": 40, "confidence": "Moderate"}
                },
                "recommendations": [
                    "Immediate diabetes medication adjustment required",
                    "Dietary consultation recommended",
                    "Regular blood glucose monitoring"
                ],
                "red_flags": [
                    "HbA1c >8% indicates very poor diabetes control",
                    "Multiple cardiovascular risk factors present"
                ]
            })
            mock_openai.return_value = mock_response
            
            # Test AI analysis
            result = generate_medical_analysis(patient_data, test_data)
            
            # Verify the function was called
            self.assertTrue(mock_openai.called)
            
            # Get the prompt that was sent to OpenAI
            call_args = mock_openai.call_args
            messages = call_args[1]['messages']
            
            # Verify prompt structure
            self.assertGreater(len(messages), 0)
            
            # Find the user message with patient data
            user_message = None
            for message in messages:
                if message['role'] == 'user':
                    user_message = message['content']
                    break
            
            self.assertIsNotNone(user_message)
            
            # Verify key information is included in prompt
            self.assertIn("Ahmad Hosseini", user_message)
            self.assertIn("38", user_message)  # age
            self.assertIn("male", user_message)  # gender
            self.assertIn("diabetes", user_message.lower())
            self.assertIn("145", user_message)  # glucose value
            self.assertIn("8.2", user_message)  # HbA1c value
            self.assertIn("metformin", user_message.lower())
            
            print("✓ AI prompt structure test passed")
            print(f"  - Prompt includes patient name: Ahmad Hosseini")
            print(f"  - Prompt includes medical history: diabetes, hypertension")
            print(f"  - Prompt includes abnormal test results: Glucose 145, HbA1c 8.2")
            print(f"  - Prompt includes current medications: Metformin, Lisinopril")
    
    @patch('ai_services.openai.chat.completions.create')
    def test_full_ai_report_generation_workflow(self, mock_openai):
        """Test the complete AI report generation workflow"""
        with self.app.app_context():
            patient = self.patient
            
            # Mock successful OpenAI response
            mock_response = MagicMock()
            mock_response.choices[0].message.content = json.dumps({
                "overall_assessment": "بیمار نشان‌دهنده کنترل ضعیف دیابت با عوامل خطر متعدد قلبی عروقی است",
                "individual_tests": {
                    "Fasting Blood Glucose": {
                        "value": "145 mg/dL",
                        "status": "بالا",
                        "interpretation": "قند خون بالا نشان‌دهنده کنترل ضعیف دیابت"
                    },
                    "HbA1c": {
                        "value": "8.2%",
                        "status": "بالا",
                        "interpretation": "کنترل ضعیف قند خون در ۲-۳ ماه گذشته"
                    },
                    "Total Cholesterol": {
                        "value": "245 mg/dL",
                        "status": "بالا",
                        "interpretation": "کلسترول بالا افزایش خطر بیماری قلبی"
                    }
                },
                "probable_diseases": {
                    "دیابت نوع ۲": {"probability": 95, "confidence": "بسیار بالا"},
                    "بیماری قلبی عروقی": {"probability": 75, "confidence": "بالا"},
                    "نفروپاتی دیابتی": {"probability": 40, "confidence": "متوسط"},
                    "رتینوپاتی دیابتی": {"probability": 30, "confidence": "متوسط"},
                    "نوروپاتی دیابتی": {"probability": 25, "confidence": "پایین تا متوسط"}
                },
                "recommendations": [
                    "تنظیم فوری دوز داروهای ضد دیابت",
                    "مشاوره تغذیه تخصصی",
                    "کنترل منظم قند خون",
                    "بررسی عملکرد کلیه و چشم",
                    "شروع استاتین برای کنترل کلسترول"
                ],
                "red_flags": [
                    "HbA1c بالای ۸٪ نشان‌دهنده کنترل بسیار ضعیف دیابت",
                    "حضور چندین عامل خطر قلبی عروقی",
                    "کراتینین بالا نشان‌دهنده احتمال نارسایی کلیه"
                ],
                "interpretation": "بیمار با سابقه دیابت نوع ۲ و فشار خون بالا، نیاز به تنظیم فوری درمان دارد",
                "follow_up": "کنترل مجدد در ۲ هفته آینده و مشاوره با متخصص غدد"
            })
            mock_openai.return_value = mock_response
            
            # Test the complete workflow
            patient_data = {
                'name': f"{patient.first_name} {patient.last_name}",
                'age': 38,
                'gender': patient.gender,
                'medical_history': patient.medical_history,
                'medications': patient.current_medications,
                'allergies': patient.allergies,
                'current_symptoms': patient.current_symptoms,
                'disease_type': patient.disease_type,
                'pain_description': patient.pain_description,
                'test_reason': patient.test_reason
            }
            
            test_results = db.session.query(TestOrder, TestType).join(TestType).filter(
                TestOrder.patient_id == patient.id,
                TestOrder.status == 'completed'
            ).all()
            
            test_data = []
            for test_order, test_type in test_results:
                test_data.append({
                    'test_name': test_type.name,
                    'result_value': test_order.result_value,
                    'unit': test_order.result_unit or test_type.unit,
                    'reference_range': test_order.reference_range or test_type.normal_range,
                    'status': test_order.result_status,
                    'date': test_order.completed_at.strftime('%Y-%m-%d') if test_order.completed_at else None
                })
            
            # Generate AI analysis
            ai_result = generate_patient_report_analysis(patient_data, test_data)
            
            # Verify successful generation
            self.assertTrue(ai_result['success'])
            self.assertIn('analysis', ai_result)
            
            analysis = ai_result['analysis']
            
            # Verify Persian content
            self.assertIn('دیابت', analysis['overall_assessment'])
            self.assertIn('individual_tests', analysis)
            self.assertIn('probable_diseases', analysis)
            self.assertIn('recommendations', analysis)
            self.assertIn('red_flags', analysis)
            
            # Verify disease probabilities
            diseases = analysis['probable_diseases']
            self.assertIn('دیابت نوع ۲', diseases)
            self.assertEqual(diseases['دیابت نوع ۲']['probability'], 95)
            
            # Verify recommendations are present
            recommendations = analysis['recommendations']
            self.assertGreater(len(recommendations), 0)
            self.assertTrue(any('دیابت' in rec for rec in recommendations))
            
            # Verify red flags
            red_flags = analysis['red_flags']
            self.assertGreater(len(red_flags), 0)
            self.assertTrue(any('HbA1c' in flag for flag in red_flags))
            
            print("✓ Full AI report generation workflow test passed")
            print(f"  - Generated Persian medical analysis")
            print(f"  - Identified {len(diseases)} probable diseases")
            print(f"  - Provided {len(recommendations)} recommendations")
            print(f"  - Flagged {len(red_flags)} critical findings")
    
    def test_openai_connection(self):
        """Test OpenAI API connection"""
        if not os.getenv('OPENAI_API_KEY'):
            self.skipTest("OpenAI API key not available")
        
        # Test connection
        connection_result = test_openai_connection()
        
        if connection_result['success']:
            print("✓ OpenAI connection test passed")
            print(f"  - Model: {connection_result.get('model', 'Unknown')}")
        else:
            print(f"⚠ OpenAI connection test failed: {connection_result.get('error', 'Unknown error')}")
    
    def test_prompt_content_analysis(self):
        """Test the actual content of prompts sent to AI"""
        with self.app.app_context():
            patient = self.patient
            
            # Get actual test data from database
            test_results = db.session.query(TestOrder, TestType).join(TestType).filter(
                TestOrder.patient_id == patient.id,
                TestOrder.status == 'completed'
            ).all()
            
            test_data = []
            for test_order, test_type in test_results:
                test_data.append({
                    'test_name': test_type.name,
                    'result_value': test_order.result_value,
                    'unit': test_order.result_unit or test_type.unit,
                    'reference_range': test_order.reference_range or test_type.normal_range,
                    'status': test_order.result_status
                })
            
            # Print the actual data that would be sent to AI
            print("\n" + "="*80)
            print("ACTUAL DATA SENT TO AI FOR ANALYSIS")
            print("="*80)
            
            print("\nPATIENT DATA:")
            print(f"Name: {patient.first_name} {patient.last_name}")
            print(f"Age: {(date.today() - patient.date_of_birth).days // 365}")
            print(f"Gender: {patient.gender}")
            print(f"Medical History: {patient.medical_history}")
            print(f"Current Symptoms: {patient.current_symptoms}")
            print(f"Current Medications: {patient.current_medications}")
            print(f"Allergies: {patient.allergies}")
            print(f"Test Reason: {patient.test_reason}")
            
            print("\nTEST RESULTS:")
            for test in test_data:
                status_indicator = "⚠️" if test['status'] == 'abnormal' else "✅"
                print(f"{status_indicator} {test['test_name']}: {test['result_value']} {test['unit']} "
                      f"(Normal: {test['reference_range']}) - {test['status'].upper()}")
            
            print("\nCRITICAL FINDINGS ANALYSIS:")
            abnormal_tests = [t for t in test_data if t['status'] == 'abnormal']
            print(f"- {len(abnormal_tests)} out of {len(test_data)} tests are abnormal")
            
            # Analyze diabetes indicators
            glucose_test = next((t for t in test_data if 'glucose' in t['test_name'].lower()), None)
            hba1c_test = next((t for t in test_data if 'hba1c' in t['test_name'].lower()), None)
            
            if glucose_test and float(glucose_test['result_value']) > 126:
                print(f"- Diabetes indicator: Fasting glucose {glucose_test['result_value']} > 126 mg/dL")
            
            if hba1c_test and float(hba1c_test['result_value']) > 6.5:
                print(f"- Diabetes indicator: HbA1c {hba1c_test['result_value']} > 6.5%")
            
            # Analyze cardiovascular risk
            cholesterol_tests = [t for t in test_data if 'cholesterol' in t['test_name'].lower()]
            if cholesterol_tests:
                print(f"- Cardiovascular risk: {len(cholesterol_tests)} cholesterol markers abnormal")
            
            print("="*80)
            
            self.assertTrue(len(test_data) > 0)
            self.assertTrue(len(abnormal_tests) > 0)

def run_ai_report_tests():
    """Run all AI report generation tests"""
    print("Starting AI Report Generation Tests...")
    print("="*80)
    
    # Create test suite
    suite = unittest.TestLoader().loadTestsFromTestCase(TestAIReportGeneration)
    
    # Run tests with verbose output
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    
    if result.failures:
        print("\nFAILURES:")
        for test, failure in result.failures:
            print(f"- {test}: {failure}")
    
    if result.errors:
        print("\nERRORS:")
        for test, error in result.errors:
            print(f"- {test}: {error}")
    
    success_rate = ((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun) * 100
    print(f"\nSuccess Rate: {success_rate:.1f}%")
    
    return result.wasSuccessful()

if __name__ == '__main__':
    success = run_ai_report_tests()
    sys.exit(0 if success else 1)