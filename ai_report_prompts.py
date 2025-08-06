"""
Enhanced AI Report Generation Prompts for MedLab Pro
Comprehensive medical analysis with 5-disease probability assessment
"""

def get_comprehensive_analysis_prompt(patient_data, lab_results):
    """
    Generate a comprehensive medical analysis prompt with Persian output
    """
    
    # Patient information
    patient_info = f"""
بیمار: {patient_data.get('name', 'نامشخص')}
سن: {patient_data.get('age', 'نامشخص')} سال
جنسیت: {patient_data.get('gender', 'نامشخص')}
علائم فعلی: {patient_data.get('current_symptoms', 'نامشخص')}
توصیف درد: {patient_data.get('pain_description', 'ندارد')}
دلیل آزمایش: {patient_data.get('test_reason', 'نامشخص')}
نوع بیماری: {patient_data.get('disease_type', 'نامشخص')}
داروهای فعلی: {patient_data.get('current_medications', 'ندارد')}
سابقه پزشکی: {patient_data.get('medical_history', 'ندارد')}
"""
    
    # Laboratory results formatting
    lab_results_text = ""
    if lab_results:
        for test_name, value in lab_results.items():
            lab_results_text += f"{test_name}: {value}\n"
    
    prompt = f"""
شما یک پزشک متخصص آزمایشگاه هستید که باید تحلیل جامع و دقیق از نتایج آزمایش ارائه دهید.

اطلاعات بیمار:
{patient_info}

نتایج آزمایشگاهی:
{lab_results_text}

لطفاً تحلیل جامع به شرح زیر ارائه دهید:

1. ارزیابی کلی (overall_assessment):
- تحلیل کلی وضعیت سلامت بیمار
- نتیجه‌گیری از نتایج آزمایش‌ها
- وضعیت عمومی بیمار

2. تحلیل تک‌تک آزمایش‌ها (individual_tests):
برای هر آزمایش:
- نام آزمایش
- مقدار
- محدوده طبیعی
- وضعیت (طبیعی/غیرطبیعی)
- تفسیر کلینیکی

3. **۵ بیماری محتمل (probable_diseases)** - بخش مهم:
برای هر بیماری:
- نام بیماری (فارسی)
- درصد احتمال (0-100)
- توضیح کامل (چرا این تشخیص محتمل است)
- علل و عوامل ریسک
- یافته‌های کلینیکی و آزمایشگاهی
- توصیه‌های تشخیصی و درمانی

4. توصیه‌های درمانی (recommendations):
- آزمایش‌های تکمیلی مورد نیاز
- مشاوره‌های تخصصی
- تغییرات سبک زندگی
- درمان‌های پیشنهادی

5. علائم خطرناک (red_flags):
- علائم هشداردهنده
- موارد اورژانسی
- زمان‌بندی مراجعه

6. تفسیر نهایی (interpretation):
- خلاصه تشخیص
- پروگنوز
- نکات مهم برای بیمار

7. پیگیری (follow_up):
- زمان‌بندی آزمایش‌های بعدی
- کنترل‌های دوره‌ای
- نظارت بر علائم

**نکات مهم:**
- همه پاسخ‌ها باید به زبان فارسی باشد
- از اصطلاحات پزشکی دقیق استفاده کنید
- درصد احتمال بیماری‌ها باید واقعی و بر اساس یافته‌ها باشد
- توضیحات باید جامع و قابل فهم برای پزشک باشد
- حتماً ۵ بیماری محتمل ارائه دهید
- اگر بیمار سالم است، بیماری‌های با احتمال پایین یا ریسک‌های آینده را ذکر کنید
"""
    
    return prompt

def get_detailed_disease_analysis_prompt(patient_data, lab_results, context=""):
    """
    Generate prompt specifically for detailed 5-disease analysis
    """
    
    prompt = f"""
بر اساس اطلاعات بیمار و نتایج آزمایشگاهی، لطفاً تحلیل دقیق ۵ بیماری محتمل ارائه دهید:

بیمار: {patient_data.get('name', '')}
علائم: {patient_data.get('current_symptoms', '')}
نتایج آزمایش: {context}

برای هر یک از ۵ بیماری محتمل، موارد زیر را به طور کامل ارائه دهید:

1. **نام بیماری** (به فارسی)
2. **درصد احتمال** (عددی بین 0 تا 100)
3. **توضیح کامل** (چرا این تشخیص محتمل است - حداقل 2 جمله)
4. **علل و عوامل ریسک** (فهرست 3-5 مورد)
5. **یافته‌های کلینیکی** (علائم و نشانه‌ها - فهرست 3-4 مورد)
6. **توصیه‌های تشخیصی و درمانی** (آزمایش‌ها، درمان‌ها - یک جمله مختصر)

**قوانین مهم:**
- همه پاسخ‌ها فقط به فارسی
- درصدها باید واقع‌بینانه باشد
- حتماً ۵ بیماری کامل ارائه دهید
- اگر بیمار سالم است، ریسک‌های آینده یا بیماری‌های با احتمال پایین بنویسید
- از اصطلاحات پزشکی دقیق استفاده کنید

فرمت خروجی JSON:
{{
  "diseases": [
    {{
      "name": "نام بیماری",
      "probability": عدد,
      "explanation": "توضیح کامل",
      "causes": ["علت 1", "علت 2", "علت 3"],
      "findings": ["یافته 1", "یافته 2", "یافته 3"],
      "recommendation": "توصیه درمانی"
    }}
  ]
}}
"""
    
    return prompt

def get_chart_data_generation_prompt(lab_results):
    """
    Generate prompt for creating chart data from lab results
    """
    
    prompt = f"""
بر اساس نتایج آزمایشگاهی زیر، داده‌های مناسب برای نمودارها تولید کنید:

نتایج آزمایش:
{lab_results}

لطفاً موارد زیر را تولید کنید:

1. **داده‌های نمودار چربی‌ها:**
- کلسترول کل
- LDL
- HDL  
- تری‌گلیسرید
(مقادیر فعلی و حد طبیعی)

2. **داده‌های نمودار عملکرد کلیه:**
- گلوکز
- BUN
- کراتینین
- سدیم
- پتاسیم
(مقادیر فعلی و حد طبیعی)

3. **توزیع ریسک برای نمودار دایره‌ای:**
- درصد وضعیت سالم
- درصد ریسک متوسط
- درصد ریسک بالا

فرمت JSON خروجی:
{{
  "cholesterol_chart": {{
    "current_values": [مقدار1, مقدار2, مقدار3, مقدار4],
    "normal_limits": [حد1, حد2, حد3, حد4],
    "labels": ["کلسترول کل", "LDL", "HDL", "تری‌گلیسرید"]
  }},
  "kidney_chart": {{
    "current_values": [مقدار1, مقدار2, مقدار3, مقدار4, مقدار5],
    "normal_limits": [حد1, حد2, حد3, حد4, حد5],
    "labels": ["گلوکز", "BUN", "کراتینین", "سدیم", "پتاسیم"]
  }},
  "risk_distribution": {{
    "healthy": درصد,
    "moderate_risk": درصد,
    "high_risk": درصد
  }}
}}
"""
    
    return prompt

def get_critical_values_prompt(lab_results):
    """
    Generate prompt for identifying critical values
    """
    
    prompt = f"""
از نتایج آزمایشگاهی زیر، مقادیر بحرانی و خطرناک را شناسایی کنید:

{lab_results}

لطفاً موارد زیر را مشخص کنید:
1. **مقادیر بحرانی** (نیاز به اقدام فوری)
2. **مقادیر غیرطبیعی** (خارج از محدوده طبیعی)
3. **هشدارها** (مواردی که نیاز به توجه دارد)
4. **اولویت‌بندی** (کدام موارد مهم‌تر است)

همه پاسخ‌ها به فارسی و با جزئیات کامل.
"""
    
    return prompt