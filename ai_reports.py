import json
import os
from datetime import datetime
from openai import OpenAI
from ai_report_prompts import (
    get_comprehensive_analysis_prompt, 
    get_detailed_disease_analysis_prompt,
    get_chart_data_generation_prompt,
    get_critical_values_prompt
)

# the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
# do not change this unless explicitly requested by the user
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
openai = OpenAI(api_key=OPENAI_API_KEY)

def generate_patient_report_analysis(patient_data, test_results):
    """Generate comprehensive AI-powered medical analysis with enhanced 5-disease analysis"""
    try:
        # Enhanced patient context preparation
        patient_context = {
            'name': f"{patient_data.get('first_name', '')} {patient_data.get('last_name', '')}",
            'age': patient_data.get('age', 'unknown'),
            'gender': patient_data.get('gender', 'unknown'),
            'current_symptoms': patient_data.get('current_symptoms', 'no symptoms reported'),
            'pain_description': patient_data.get('pain_description', 'none'),
            'test_reason': patient_data.get('test_reason', 'unknown'),
            'disease_type': patient_data.get('disease_type', 'unknown'),
            'current_medications': patient_data.get('current_medications', 'none'),
            'medical_history': patient_data.get('medical_history', 'no significant history'),
            'allergies': patient_data.get('allergies', 'no known allergies')
        }
        
        # Enhanced test results processing
        lab_results = {}
        test_context = "Laboratory test results:\n"
        
        for test in test_results:
            test_name = test.get('test_name', 'Unknown test')
            result_value = test.get('result_value', 'N/A')
            unit = test.get('unit', '')
            reference_range = test.get('reference_range', 'Unknown range')
            status = test.get('status', 'Unknown status')
            
            test_context += f"- {test_name}: {result_value} {unit} (Normal range: {reference_range}) - Status: {status}\n"
            lab_results[test_name] = {
                'value': result_value,
                'unit': unit,
                'reference': reference_range,
                'status': status
            }
        
        # Use the comprehensive analysis prompt
        prompt = get_comprehensive_analysis_prompt(patient_context, lab_results)
        
        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert laboratory physician and pathologist with years of experience in interpreting medical tests. Your expertise includes diagnosing various diseases based on laboratory findings, providing evidence-based treatment recommendations, and identifying critical warning signs. Your analyses should be accurate, comprehensive, and based on current medical standards. Always note that this analysis is AI-generated and should be reviewed by a qualified physician."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            response_format={"type": "json_object"},
            temperature=0.2,
            max_tokens=4000
        )
        
        result = json.loads(response.choices[0].message.content)
        return {
            "success": True,
            "analysis": result,
            "generated_at": datetime.utcnow().isoformat(),
            "model_used": "gpt-4o"
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "generated_at": datetime.utcnow().isoformat()
        }

def generate_detailed_disease_analysis(patient_data, lab_results_context):
    """Generate detailed 5-disease analysis using enhanced prompts"""
    try:
        prompt = get_detailed_disease_analysis_prompt(patient_data, {}, lab_results_context)
        
        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system", 
                    "content": "You are a medical expert specializing in differential diagnosis. Generate detailed analysis of 5 most probable diseases based on patient data and lab results. Always respond in Persian/Farsi with medical terminology."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            response_format={"type": "json_object"},
            temperature=0.3,
            max_tokens=3000
        )
        
        result = json.loads(response.choices[0].message.content)
        return {
            "success": True,
            "diseases": result.get("diseases", []),
            "generated_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "generated_at": datetime.utcnow().isoformat()
        }

def generate_trend_analysis(lab_data, time_period="monthly"):
    """Generate trend analysis for laboratory efficiency and patterns"""
    try:
        summary_prompt = f"""
        Analyze the following laboratory data trends for {time_period} reporting:
        
        Data: {json.dumps(lab_data, indent=2)}
        
        Please provide a comprehensive trend analysis in Persian including:
        1. Test volume trends
        2. Abnormal result patterns  
        3. Critical value frequencies
        4. Processing time efficiency
        5. Quality metrics
        6. Recommendations for improvement
        
        Format as JSON with Persian text.
        """
        
        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": "You are a laboratory management expert specializing in data analysis and quality improvement. Provide insights in Persian."
                },
                {
                    "role": "user", 
                    "content": summary_prompt
                }
            ],
            response_format={"type": "json_object"},
            temperature=0.1,
            max_tokens=2000
        )
        
        result = json.loads(response.choices[0].message.content)
        return {
            "success": True,
            "analysis": result,
            "period": time_period,
            "generated_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "generated_at": datetime.utcnow().isoformat()
        }

def generate_lab_efficiency_report(efficiency_data):
    """Generate laboratory efficiency and performance analysis"""
    try:
        efficiency_prompt = f"""
        Analyze laboratory efficiency metrics and generate improvement recommendations:
        
        Efficiency Data: {json.dumps(efficiency_data, indent=2)}
        
        Provide analysis in Persian covering:
        1. Processing time analysis
        2. Resource utilization 
        3. Quality control metrics
        4. Throughput optimization
        5. Cost efficiency measures
        6. Staff performance indicators
        7. Equipment utilization
        8. Actionable recommendations
        
        Format as comprehensive JSON report in Persian.
        """
        
        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": "You are a healthcare operations expert specializing in laboratory efficiency and quality management. Provide detailed analysis in Persian."
                },
                {
                    "role": "user",
                    "content": efficiency_prompt
                }
            ],
            response_format={"type": "json_object"},
            temperature=0.1,
            max_tokens=2500
        )
        
        result = json.loads(response.choices[0].message.content)
        return {
            "success": True,
            "efficiency_analysis": result,
            "generated_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "generated_at": datetime.utcnow().isoformat()
        }

def analyze_critical_values(test_results):
    """Identify and analyze critical values requiring immediate attention"""
    try:
        prompt = get_critical_values_prompt(test_results)
        
        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": "You are a clinical pathologist expert in identifying critical laboratory values that require immediate medical attention. Respond in Persian with urgent clinical recommendations."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            response_format={"type": "json_object"},
            temperature=0.1,
            max_tokens=1500
        )
        
        result = json.loads(response.choices[0].message.content)
        return {
            "success": True,
            "critical_analysis": result,
            "urgency_level": "high" if result.get("critical_values") else "normal",
            "generated_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "generated_at": datetime.utcnow().isoformat()
        }