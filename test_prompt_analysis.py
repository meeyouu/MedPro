#!/usr/bin/env python3
"""
Test and analyze AI prompts used in medical report generation
"""

import json
import sys
import os
from datetime import date, datetime, timedelta

# Add current directory to path
sys.path.insert(0, '.')

def analyze_prompt_structure():
    """Analyze the actual prompt structure used for AI medical analysis"""
    
    print("="*80)
    print("AI MEDICAL REPORT PROMPT ANALYSIS")
    print("="*80)
    
    # Sample patient data (realistic diabetic patient)
    patient_data = {
        'name': 'Ahmad Hosseini',
        'age': 38,
        'gender': 'male',
        'medical_history': 'Hypertension, diabetes type 2',
        'current_symptoms': 'Fatigue, frequent urination, increased thirst',
        'pain_description': 'Mild headache, no specific pain',
        'test_reason': 'Routine diabetes monitoring and cardiovascular assessment',
        'disease_type': 'Diabetes mellitus, Hypertension',
        'allergies': 'Penicillin',
        'current_medications': 'Metformin 500mg twice daily, Lisinopril 10mg daily',
    }
    
    # Sample test results (abnormal diabetic values)
    test_results = [
        {'test_name': 'Fasting Blood Glucose', 'result_value': '145', 'unit': 'mg/dL', 'reference_range': '70-100', 'status': 'abnormal'},
        {'test_name': 'HbA1c', 'result_value': '8.2', 'unit': '%', 'reference_range': '4.0-5.6', 'status': 'abnormal'},
        {'test_name': 'Total Cholesterol', 'result_value': '245', 'unit': 'mg/dL', 'reference_range': '<200', 'status': 'abnormal'},
        {'test_name': 'HDL Cholesterol', 'result_value': '35', 'unit': 'mg/dL', 'reference_range': '>40 (M)', 'status': 'abnormal'},
        {'test_name': 'LDL Cholesterol', 'result_value': '165', 'unit': 'mg/dL', 'reference_range': '<100', 'status': 'abnormal'},
        {'test_name': 'Triglycerides', 'result_value': '280', 'unit': 'mg/dL', 'reference_range': '<150', 'status': 'abnormal'},
        {'test_name': 'Creatinine', 'result_value': '1.4', 'unit': 'mg/dL', 'reference_range': '0.7-1.3 (M)', 'status': 'abnormal'},
    ]
    
    print("\n1. PATIENT INFORMATION SENT TO AI:")
    print("-" * 40)
    for key, value in patient_data.items():
        print(f"{key.replace('_', ' ').title()}: {value}")
    
    print("\n2. TEST RESULTS SENT TO AI:")
    print("-" * 40)
    abnormal_count = 0
    for test in test_results:
        status_icon = "⚠️" if test['status'] == 'abnormal' else "✅"
        if test['status'] == 'abnormal':
            abnormal_count += 1
        print(f"{status_icon} {test['test_name']}: {test['result_value']} {test['unit']} "
              f"(Normal: {test['reference_range']}) - {test['status'].upper()}")
    
    print(f"\nCRITICAL ANALYSIS: {abnormal_count}/{len(test_results)} tests are ABNORMAL")
    
    # Show what the AI prompt construction looks like
    print("\n3. AI PROMPT STRUCTURE:")
    print("-" * 40)
    
    # Simulate the prompt building from ai_reports.py
    test_context = "Laboratory test results:\n"
    for test in test_results:
        test_context += f"- {test['test_name']}: {test['result_value']} {test['unit']} (Normal range: {test['reference_range']}) - Status: {test['status']}\n"
    
    print("SYSTEM MESSAGE:")
    system_msg = """You are an expert laboratory physician and pathologist with years of experience in interpreting medical tests. Your expertise includes diagnosing various diseases based on laboratory findings, providing evidence-based treatment recommendations, and identifying critical warning signs. Your analyses should be accurate, comprehensive, and based on current medical standards. Always note that this analysis is AI-generated and should be reviewed by a qualified physician."""
    print(system_msg)
    
    print("\nUSER MESSAGE (PATIENT DATA + TEST RESULTS):")
    print(f"Patient: {patient_data['name']}")
    print(f"Age: {patient_data['age']} years")
    print(f"Gender: {patient_data['gender']}")
    print(f"Medical History: {patient_data['medical_history']}")
    print(f"Current Symptoms: {patient_data['current_symptoms']}")
    print(f"Current Medications: {patient_data['current_medications']}")
    print(f"Test Reason: {patient_data['test_reason']}")
    print("\n" + test_context)
    
    print("\n4. EXPECTED AI RESPONSE STRUCTURE:")
    print("-" * 40)
    expected_response = {
        "overall_assessment": "Patient shows poor diabetes control with multiple cardiovascular risk factors",
        "individual_tests": {
            "Fasting Blood Glucose": {
                "value": "145 mg/dL",
                "status": "High",
                "interpretation": "Elevated glucose indicating poor diabetes control"
            },
            "HbA1c": {
                "value": "8.2%", 
                "status": "High",
                "interpretation": "Poor long-term glucose control over past 2-3 months"
            }
        },
        "probable_diseases": {
            "Diabetes Mellitus Type 2": {"probability": 95, "confidence": "Very High"},
            "Cardiovascular Disease": {"probability": 75, "confidence": "High"},
            "Diabetic Nephropathy": {"probability": 40, "confidence": "Moderate"},
            "Diabetic Retinopathy": {"probability": 30, "confidence": "Moderate"},
            "Diabetic Neuropathy": {"probability": 25, "confidence": "Low-Moderate"}
        },
        "recommendations": [
            "Immediate diabetes medication adjustment required",
            "Dietary consultation recommended", 
            "Regular blood glucose monitoring",
            "Kidney function evaluation",
            "Eye examination for diabetic retinopathy"
        ],
        "red_flags": [
            "HbA1c >8% indicates very poor diabetes control",
            "Multiple cardiovascular risk factors present",
            "Elevated creatinine suggests kidney involvement"
        ]
    }
    
    print(json.dumps(expected_response, indent=2, ensure_ascii=False))
    
    return patient_data, test_results

def test_medical_analysis_logic():
    """Test the medical analysis logic"""
    print("\n" + "="*80)
    print("MEDICAL ANALYSIS LOGIC TEST")
    print("="*80)
    
    patient_data, test_results = analyze_prompt_structure()
    
    # Clinical reasoning checks
    print("\n5. CLINICAL REASONING VALIDATION:")
    print("-" * 40)
    
    # Diabetes indicators
    glucose_test = next((t for t in test_results if 'glucose' in t['test_name'].lower()), None)
    hba1c_test = next((t for t in test_results if 'hba1c' in t['test_name'].lower()), None)
    
    if glucose_test:
        glucose_value = float(glucose_test['result_value'])
        print(f"✓ Fasting Glucose: {glucose_value} mg/dL")
        if glucose_value >= 126:
            print(f"  → DIABETES CONFIRMED (≥126 mg/dL)")
        elif glucose_value >= 100:
            print(f"  → PRE-DIABETES (100-125 mg/dL)")
        else:
            print(f"  → NORMAL (<100 mg/dL)")
    
    if hba1c_test:
        hba1c_value = float(hba1c_test['result_value'])
        print(f"✓ HbA1c: {hba1c_value}%")
        if hba1c_value >= 6.5:
            print(f"  → DIABETES CONFIRMED (≥6.5%)")
            if hba1c_value >= 8.0:
                print(f"  → POOR CONTROL (≥8.0%) - URGENT ACTION NEEDED")
        elif hba1c_value >= 5.7:
            print(f"  → PRE-DIABETES (5.7-6.4%)")
        else:
            print(f"  → NORMAL (<5.7%)")
    
    # Cardiovascular risk assessment
    cholesterol_tests = [t for t in test_results if 'cholesterol' in t['test_name'].lower()]
    cv_risk_factors = 0
    
    for test in cholesterol_tests:
        if test['status'] == 'abnormal':
            cv_risk_factors += 1
            print(f"✓ {test['test_name']}: {test['result_value']} {test['unit']} - ABNORMAL")
    
    triglycerides_test = next((t for t in test_results if 'triglycerides' in t['test_name'].lower()), None)
    if triglycerides_test and triglycerides_test['status'] == 'abnormal':
        cv_risk_factors += 1
        print(f"✓ Triglycerides: {triglycerides_test['result_value']} {triglycerides_test['unit']} - ABNORMAL")
    
    print(f"\n→ CARDIOVASCULAR RISK FACTORS: {cv_risk_factors}")
    if cv_risk_factors >= 3:
        print("  → HIGH CARDIOVASCULAR RISK")
    elif cv_risk_factors >= 2:
        print("  → MODERATE CARDIOVASCULAR RISK")
    else:
        print("  → LOW CARDIOVASCULAR RISK")
    
    # Kidney function assessment
    creatinine_test = next((t for t in test_results if 'creatinine' in t['test_name'].lower()), None)
    if creatinine_test:
        creatinine_value = float(creatinine_test['result_value'])
        print(f"✓ Creatinine: {creatinine_value} mg/dL")
        if creatinine_value > 1.3:  # Upper normal for males
            print(f"  → POSSIBLE KIDNEY IMPAIRMENT (>1.3 mg/dL for males)")
        else:
            print(f"  → NORMAL KIDNEY FUNCTION")
    
    print("\n6. DISEASE PROBABILITY CALCULATION:")
    print("-" * 40)
    
    # Calculate disease probabilities based on findings
    diseases = {
        "Diabetes Mellitus Type 2": 0,
        "Cardiovascular Disease": 0, 
        "Diabetic Nephropathy": 0,
        "Diabetic Retinopathy": 0,
        "Metabolic Syndrome": 0
    }
    
    # Diabetes probability
    if glucose_test and float(glucose_test['result_value']) >= 126:
        diseases["Diabetes Mellitus Type 2"] += 40
    if hba1c_test and float(hba1c_test['result_value']) >= 6.5:
        diseases["Diabetes Mellitus Type 2"] += 40
    if "diabetes" in patient_data['medical_history'].lower():
        diseases["Diabetes Mellitus Type 2"] += 20
    
    # Cardiovascular disease probability
    diseases["Cardiovascular Disease"] = min(cv_risk_factors * 15, 80)
    if "hypertension" in patient_data['medical_history'].lower():
        diseases["Cardiovascular Disease"] += 15
    
    # Diabetic complications
    if diseases["Diabetes Mellitus Type 2"] > 70:
        if creatinine_test and float(creatinine_test['result_value']) > 1.3:
            diseases["Diabetic Nephropathy"] = 45
        diseases["Diabetic Retinopathy"] = 35
        diseases["Metabolic Syndrome"] = 60
    
    for disease, probability in diseases.items():
        confidence = "Very High" if probability >= 80 else "High" if probability >= 60 else "Moderate" if probability >= 40 else "Low" if probability >= 20 else "Very Low"
        print(f"• {disease}: {probability}% ({confidence})")
    
    print("\n" + "="*80)
    print("PROMPT ANALYSIS COMPLETE - AI SHOULD PROCESS THIS DATA ACCURATELY")
    print("="*80)

def test_actual_ai_generation():
    """Test actual AI generation if API key is available"""
    if not os.getenv('OPENAI_API_KEY'):
        print("\n⚠️ OPENAI_API_KEY not available - skipping live AI test")
        return
    
    print("\n" + "="*80)
    print("LIVE AI GENERATION TEST")
    print("="*80)
    
    try:
        from ai_reports import generate_patient_report_analysis
        
        patient_data = {
            'name': 'Ahmad Hosseini',
            'age': 38,
            'gender': 'male',
            'medical_history': 'Hypertension, diabetes type 2',
            'current_symptoms': 'Fatigue, frequent urination, increased thirst',
            'current_medications': 'Metformin 500mg twice daily, Lisinopril 10mg daily',
            'allergies': 'Penicillin',
            'test_reason': 'Routine diabetes monitoring'
        }
        
        test_results = [
            {'test_name': 'Fasting Blood Glucose', 'result_value': '145', 'unit': 'mg/dL', 'reference_range': '70-100', 'status': 'abnormal'},
            {'test_name': 'HbA1c', 'result_value': '8.2', 'unit': '%', 'reference_range': '4.0-5.6', 'status': 'abnormal'},
            {'test_name': 'Total Cholesterol', 'result_value': '245', 'unit': 'mg/dL', 'reference_range': '<200', 'status': 'abnormal'}
        ]
        
        print("Sending request to OpenAI...")
        result = generate_patient_report_analysis(patient_data, test_results)
        
        if result['success']:
            analysis = result['analysis']
            print("✅ AI GENERATION SUCCESSFUL")
            print(f"Model Used: {result.get('model_used', 'Unknown')}")
            print(f"Generated At: {result.get('generated_at', 'Unknown')}")
            
            print("\nAI Response Summary:")
            print(f"• Overall Assessment: {analysis.get('overall_assessment', 'N/A')[:100]}...")
            print(f"• Individual Tests Analyzed: {len(analysis.get('individual_tests', {}))}")
            print(f"• Diseases Identified: {len(analysis.get('probable_diseases', {}))}")
            print(f"• Recommendations: {len(analysis.get('recommendations', []))}")
            print(f"• Red Flags: {len(analysis.get('red_flags', []))}")
            
            if analysis.get('probable_diseases'):
                print("\nTop Disease Probabilities:")
                for disease, data in list(analysis['probable_diseases'].items())[:3]:
                    prob = data.get('probability', 0) if isinstance(data, dict) else 0
                    print(f"  • {disease}: {prob}%")
        else:
            print(f"❌ AI GENERATION FAILED: {result.get('error', 'Unknown error')}")
            
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")

if __name__ == '__main__':
    print("Testing AI Medical Report Generation Workflow")
    test_medical_analysis_logic()
    test_actual_ai_generation()
    print("\nTest complete. Review the analysis above to verify prompt accuracy.")