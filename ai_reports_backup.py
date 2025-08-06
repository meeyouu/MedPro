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
            'age': patient_data.get('age', 'نامشخص'),
            'gender': patient_data.get('gender', 'نامشخص'),
            'current_symptoms': patient_data.get('current_symptoms', 'علائمی گزارش نشده'),
            'pain_description': patient_data.get('pain_description', 'ندارد'),
            'test_reason': patient_data.get('test_reason', 'نامشخص'),
            'disease_type': patient_data.get('disease_type', 'نامشخص'),
            'current_medications': patient_data.get('current_medications', 'ندارد'),
            'medical_history': patient_data.get('medical_history', 'سابقه خاصی گزارش نشده'),
            'allergies': patient_data.get('allergies', 'آلرژی شناخته‌شده‌ای ندارد')
        }
        
        # Enhanced test results processing
        lab_results = {}
        test_context = "نتایج آزمایش‌های انجام شده:\n"
        
        for test in test_results:
            test_name = test.get('test_name', 'آزمایش نامشخص')
            result_value = test.get('result_value', 'N/A')
            unit = test.get('unit', '')
            reference_range = test.get('reference_range', 'محدوده مرجع نامشخص')
            status = test.get('status', 'وضعیت نامشخص')
            
            test_context += f"- {test_name}: {result_value} {unit} (محدوده طبیعی: {reference_range}) - وضعیت: {status}\n"
            lab_results[test_name] = {
                'value': result_value,
                'unit': unit,
                'reference': reference_range,
                'status': status
            }
        
        # Use the comprehensive analysis prompt
        prompt = get_comprehensive_analysis_prompt(patient_context, lab_results)

        {{
            "overall_assessment": "ارزیابی کلی وضعیت سلامت بیمار در ۲-۳ جمله تخصصی",
            "individual_tests": {{
                "نام_آزمایش": {{
                    "status": "normal/abnormal/critical",
                    "findings": "یافته‌های تفصیلی این آزمایش",
                    "clinical_significance": "اهمیت بالینی و ارتباط با سایر یافته‌ها"
                }}
            }},
            "probable_diseases": {{
                "نام_بیماری": {{
                    "probability": عدد_بین_0_تا_100,
                    "reasoning": "دلیل تشخیص بر اساس یافته‌های آزمایشگاهی و علائم"
                }}
            }},
            "recommendations": [
                "توصیه‌های درمانی و بالینی تفصیلی",
                "دستورالعمل‌های دارویی مشخص",
                "تغییرات سبک زندگی ضروری"
            ],
            "follow_up": "برنامه پیگیری و آزمایش‌های بعدی مورد نیاز",
            "red_flags": [
                "علائم خطر و یافته‌های بحرانی که نیاز به توجه فوری دارند"
            ],
            "interpretation": "تفسیر کامل وضعیت بیمار با در نظر گیری تمام عوامل"
        }}

        اطلاعات بیمار:
        - سن: {age} سال
        - جنسیت: {gender}
        - سابقه پزشکی: {medical_history}
        - داروهای فعلی: {current_medications}
        - آلرژی‌ها: {allergies}
        - علائم فعلی: {symptoms}
        - بیماری شناخته شده: {disease_type}

        {test_context}

        نکات مهم:
        1. تحلیل را بر اساس استانداردهای پزشکی ایران و راهنماهای بین‌المللی انجام دهید
        2. احتمال بیماری‌ها را بر اساس شواهد علمی و الگوهای آزمایشگاهی تعیین کنید
        3. توصیه‌های درمانی باید شامل داروهای مشخص با دوز باشد
        4. علائم خطر (red flags) را با دقت شناسایی کنید
        5. در صورت وجود مقادیر بحرانی، اولویت فوری را مشخص کنید
        6. پاسخ کاملاً به زبان فارسی و با اصطلاحات پزشکی دقیق باشد
        """
        
        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": "شما یک پزشک متخصص آزمایشگاه و پاتولوژی با سال‌ها تجربه در تفسیر آزمایش‌های طبی هستید. تخصص شما در تشخیص بیماری‌های مختلف بر اساس یافته‌های آزمایشگاهی، ارائه توصیه‌های درمانی مبتنی بر شواهد علمی، و شناسایی علائم خطر است. تحلیل‌های شما باید دقیق، جامع، و بر اساس استانداردهای پزشکی روز دنیا باشد. همیشه اشاره کنید که این تحلیل توسط هوش مصنوعی تولید شده و باید توسط پزشک متخصص بررسی شود."
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
            "error": f"Failed to generate AI analysis: {str(e)}",
            "generated_at": datetime.utcnow().isoformat()
        }

def generate_trend_analysis(patient_id, historical_data):
    """Generate trend analysis for a patient's historical test results"""
    try:
        # Prepare historical data context
        trends_context = "Historical Test Data:\n"
        for record in historical_data:
            trends_context += f"Date: {record.get('date')} - {record.get('test_name')}: {record.get('value')} {record.get('unit')} (Status: {record.get('status')})\n"
        
        prompt = f"""
        Analyze the following historical laboratory test data for trends, patterns, and clinical progression.
        Provide analysis in JSON format with this structure:
        
        {{
            "trend_summary": "Overall trend description",
            "improving_parameters": ["Tests showing improvement"],
            "declining_parameters": ["Tests showing decline"],
            "stable_parameters": ["Tests remaining stable"],
            "pattern_insights": ["Notable patterns or cycles"],
            "clinical_progression": "Assessment of overall health progression",
            "monitoring_recommendations": ["Recommendations for future monitoring"]
        }}
        
        {trends_context}
        
        Focus on identifying clinically significant trends and provide actionable insights for patient monitoring.
        """
        
        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": "You are a clinical laboratory specialist focused on longitudinal data analysis and trend identification in laboratory medicine."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            response_format={"type": "json_object"},
            temperature=0.3,
            max_tokens=1500
        )
        
        result = json.loads(response.choices[0].message.content)
        return {
            "success": True,
            "trend_analysis": result,
            "generated_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to generate trend analysis: {str(e)}"
        }

def generate_quality_control_insights(qc_data):
    """Generate insights for laboratory quality control data"""
    try:
        qc_context = "Quality Control Data:\n"
        for qc in qc_data:
            qc_context += f"Test: {qc.get('test_name')} - Control Level: {qc.get('level')} - Result: {qc.get('result')} - Expected: {qc.get('expected_range')} - Date: {qc.get('date')}\n"
        
        prompt = f"""
        Analyze the quality control data and provide insights about laboratory performance.
        Return analysis in JSON format:
        
        {{
            "performance_summary": "Overall QC performance assessment",
            "out_of_control_tests": ["Tests showing control issues"],
            "trending_issues": ["Tests showing concerning trends"],
            "recommendations": ["QC improvement recommendations"],
            "calibration_needs": ["Tests that may need recalibration"],
            "stability_assessment": "Assessment of analytical stability"
        }}
        
        {qc_context}
        """
        
        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": "You are a clinical laboratory quality assurance specialist with expertise in statistical quality control and laboratory accreditation standards."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            response_format={"type": "json_object"},
            temperature=0.2,
            max_tokens=1200
        )
        
        result = json.loads(response.choices[0].message.content)
        return {
            "success": True,
            "qc_insights": result,
            "generated_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to generate QC insights: {str(e)}"
        }

def generate_lab_efficiency_report(operational_data):
    """Generate operational efficiency insights for the laboratory"""
    try:
        ops_context = f"""
        Laboratory Operational Data:
        - Total Tests Processed: {operational_data.get('total_tests', 0)}
        - Average Turnaround Time: {operational_data.get('avg_turnaround', 'N/A')} hours
        - Tests by Status: {operational_data.get('status_breakdown', {})}
        - Peak Hours: {operational_data.get('peak_hours', 'N/A')}
        - Resource Utilization: {operational_data.get('resource_utilization', 'N/A')}
        - Error Rate: {operational_data.get('error_rate', 'N/A')}%
        """
        
        prompt = f"""
        Analyze laboratory operational efficiency and provide improvement recommendations.
        Format response as JSON:
        
        {{
            "efficiency_score": "Overall efficiency rating (1-10)",
            "performance_highlights": ["Key positive performance indicators"],
            "bottlenecks": ["Identified operational bottlenecks"],
            "improvement_opportunities": ["Specific areas for improvement"],
            "resource_optimization": ["Recommendations for resource optimization"],
            "workflow_suggestions": ["Workflow improvement suggestions"],
            "cost_saving_opportunities": ["Potential cost reduction areas"]
        }}
        
        {ops_context}
        """
        
        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": "You are a healthcare operations specialist with expertise in laboratory management, workflow optimization, and healthcare efficiency analysis."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            response_format={"type": "json_object"},
            temperature=0.3,
            max_tokens=1500
        )
        
        result = json.loads(response.choices[0].message.content)
        return {
            "success": True,
            "efficiency_report": result,
            "generated_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to generate efficiency report: {str(e)}"
        }
