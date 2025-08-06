#!/usr/bin/env python3
"""
Populate database with 10 real sample patients and their AI reports
Based on the attached medical data structure
"""

import json
from datetime import datetime, date, timedelta
from app import app, db
from models import Laboratory, User, Patient, TestType, TestOrder, Sample, Report, AuditLog

def create_sample_patients():
    """Create 10 realistic patient records with comprehensive medical data"""
    
    # Sample patient data based on attached files structure
    patients_data = [
        {
            "first_name": "محمد",
            "last_name": "رضایی",
            "national_id": "0012345678",
            "date_of_birth": date(1979, 3, 15),  # 45 years old
            "gender": "male",
            "phone": "09123456789",
            "email": "m.rezaei@email.com",
            "address": "تهران، خیابان ولیعصر، پلاک 123",
            "medical_history": "سابقه فشار خون بالا، سکته قلبی در خانواده",
            "current_symptoms": "درد قفسه سینه موقع فعالیت، تنگی نفس",
            "pain_description": "درد فشاری در قفسه سینه هنگام ورزش",
            "test_reason": "بررسی سلامت قلب و عروق",
            "disease_type": "فشار خون بالا",
            "allergies": "آلرژی به آسپرین",
            "current_medications": "لوسارتان ۵۰ میلی‌گرم روزانه",
            "height": 175.0,
            "weight": 82.0,
            "blood_type": "A+",
            "language_preference": "fa"
        },
        {
            "first_name": "فاطمه",
            "last_name": "احمدی",
            "national_id": "0012345679",
            "date_of_birth": date(1985, 7, 20),  # 39 years old
            "gender": "female",
            "phone": "09123456790",
            "email": "f.ahmadi@email.com",
            "address": "تهران، خیابان انقلاب، پلاک 456",
            "medical_history": "سابقه دیابت نوع 2، چاقی",
            "current_symptoms": "خستگی مداوم، تشنگی زیاد",
            "pain_description": "",
            "test_reason": "کنترل قند خون و بررسی عملکرد کلیه",
            "disease_type": "دیابت نوع 2",
            "allergies": "آلرژی به پنی‌سیلین",
            "current_medications": "متفورمین 1000 میلی‌گرم دو بار در روز",
            "height": 165.0,
            "weight": 78.0,
            "blood_type": "B+",
            "language_preference": "fa"
        },
        {
            "first_name": "علی",
            "last_name": "کریمی", 
            "national_id": "0012345680",
            "date_of_birth": date(1992, 11, 8),  # 32 years old
            "gender": "male",
            "phone": "09123456791",
            "email": "a.karimi@email.com", 
            "address": "تهران، خیابان آزادی، پلاک 789",
            "medical_history": "سالم، بدون سابقه بیماری خاص",
            "current_symptoms": "چک‌آپ سالانه",
            "pain_description": "",
            "test_reason": "آزمایش پیشگیری سالانه",
            "disease_type": "",
            "allergies": "",
            "current_medications": "مولتی ویتامین روزانه",
            "height": 180.0,
            "weight": 75.0,
            "blood_type": "O+",
            "language_preference": "fa"
        },
        {
            "first_name": "مریم",
            "last_name": "حسینی",
            "national_id": "0012345681",
            "date_of_birth": date(1975, 5, 12),  # 49 years old
            "gender": "female",
            "phone": "09123456792",
            "email": "m.hosseini@email.com",
            "address": "تهران، خیابان کریمخان، پلاک 321",
            "medical_history": "سابقه هیپوتیروئیدی، فشار خون",
            "current_symptoms": "خستگی، افزایش وزن",
            "pain_description": "",
            "test_reason": "بررسی عملکرد تیروئید و چربی خون",
            "disease_type": "هیپوتیروئیدی",
            "allergies": "",
            "current_medications": "لووتیروکسین 100 میکروگرم، آملودیپین 5 میلی‌گرم",
            "height": 160.0,
            "weight": 68.0,
            "blood_type": "AB+",
            "language_preference": "fa"
        },
        {
            "first_name": "حسن",
            "last_name": "محمدی",
            "national_id": "0012345682",
            "date_of_birth": date(1968, 9, 25),  # 56 years old
            "gender": "male",
            "phone": "09123456793",
            "email": "h.mohammadi@email.com",
            "address": "تهران، خیابان فردوسی، پلاک 654",
            "medical_history": "سابقه سیگار کشیدن 20 سال، بیماری مزمن ریوی",
            "current_symptoms": "سرفه مداوم، تنگی نفس",
            "pain_description": "درد قفسه سینه هنگام سرفه",
            "test_reason": "بررسی التهاب و عملکرد ریه",
            "disease_type": "بیماری مزمن ریوی",
            "allergies": "",
            "current_medications": "سالبوتامول اسپری، پردنیزولون 5 میلی‌گرم",
            "height": 172.0,
            "weight": 65.0,
            "blood_type": "A-",
            "language_preference": "fa"
        },
        {
            "first_name": "زهرا",
            "last_name": "صادقی",
            "national_id": "0012345683",
            "date_of_birth": date(1990, 12, 3),  # 34 years old
            "gender": "female",
            "phone": "09123456794",
            "email": "z.sadeghi@email.com",
            "address": "تهران، خیابان طالقانی، پلاک 987",
            "medical_history": "حاملگی 16 هفته",
            "current_symptoms": "تهوع صبحگاهی، خستگی",
            "pain_description": "",
            "test_reason": "بررسی‌های دوران بارداری",
            "disease_type": "حاملگی",
            "allergies": "",
            "current_medications": "فولیک اسید، ویتامین پرناتال",
            "height": 168.0,
            "weight": 62.0,
            "blood_type": "O-",
            "language_preference": "fa"
        },
        {
            "first_name": "رضا",
            "last_name": "نوری",
            "national_id": "0012345684",
            "date_of_birth": date(1983, 4, 18),  # 41 years old
            "gender": "male",
            "phone": "09123456795",
            "email": "r.nouri@email.com",
            "address": "تهران، خیابان شریعتی، پلاک 147",
            "medical_history": "سابقه کم‌خونی، نقص آهن",
            "current_symptoms": "خستگی، ضعف عمومی",
            "pain_description": "",
            "test_reason": "بررسی کم‌خونی و سطح آهن",
            "disease_type": "کم‌خونی فقر آهن",
            "allergies": "",
            "current_medications": "قرص آهن 325 میلی‌گرم دو بار در روز",
            "height": 177.0,
            "weight": 70.0,
            "blood_type": "B-",
            "language_preference": "fa"
        },
        {
            "first_name": "نگار",
            "last_name": "رحیمی",
            "national_id": "0012345685",
            "date_of_birth": date(1995, 8, 7),  # 29 years old
            "gender": "female",
            "phone": "09123456796",
            "email": "n.rahimi@email.com",
            "address": "تهران، خیابان نیایش، پلاک 258",
            "medical_history": "سالم",
            "current_symptoms": "درخواست آزمایش قبل از ازدواج",
            "pain_description": "",
            "test_reason": "آزمایش‌های قبل از ازدواج",
            "disease_type": "",
            "allergies": "",
            "current_medications": "",
            "height": 163.0,
            "weight": 55.0,
            "blood_type": "A+",
            "language_preference": "fa"
        },
        {
            "first_name": "امیر",
            "last_name": "یوسفی",
            "national_id": "0012345686",
            "date_of_birth": date(1987, 1, 30),  # 37 years old
            "gender": "male", 
            "phone": "09123456797",
            "email": "a.yousefi@email.com",
            "address": "تهران، خیابان جمهوری، پلاک 369",
            "medical_history": "سابقه سنگ کلیه",
            "current_symptoms": "درد کمر، سوزش ادرار",
            "pain_description": "درد کلیوی در ناحیه کمر",
            "test_reason": "بررسی عملکرد کلیه و التهاب ادراری",
            "disease_type": "سنگ کلیه",
            "allergies": "",
            "current_medications": "سیتره پتاسیم، آب فراوان",
            "height": 174.0,
            "weight": 73.0,
            "blood_type": "AB-",
            "language_preference": "fa"
        },
        {
            "first_name": "لیلا",
            "last_name": "فرهادی",
            "national_id": "0012345687",
            "date_of_birth": date(1978, 6, 14),  # 46 years old
            "gender": "female",
            "phone": "09123456798",
            "email": "l.farhadi@email.com",
            "address": "تهران، خیابان مطهری، پلاک 741",
            "medical_history": "سابقه افسردگی، اضطراب",
            "current_symptoms": "کاهش انرژی، اختلال خواب",
            "pain_description": "",
            "test_reason": "بررسی‌های تیروئید و ویتامین‌ها",
            "disease_type": "افسردگی",
            "allergies": "آلرژی به کدئین",
            "current_medications": "سرترالین 50 میلی‌گرم، ویتامین D",
            "height": 167.0,
            "weight": 64.0,
            "blood_type": "O+",
            "language_preference": "fa"
        }
    ]
    
    return patients_data

def create_sample_ai_reports():
    """Create AI analysis reports based on attached JSON structure"""
    
    reports_data = [
        {
            "patient_index": 0,  # محمد رضایی
            "report_type": "comprehensive",
            "title": "تحلیل جامع آزمایشات قلبی-عروقی",
            "overall_assessment": "مرد ۴۵ ساله با فشار خون بالا شناخته شده و سابقه خانوادگی سکته قلبی که دارای اختلال شدید چربی خون و علائم مشکوک به آنژین صدری است، در معرض ریسک بسیار بالای حوادث قلبی-عروقی حاد قرار دارد و نیاز به مداخله فوری دارد",
            "bmp_results": json.dumps({
                "Glucose": "95",
                "BUN": "18", 
                "Creatinine": "1.0",
                "Sodium": "140",
                "Potassium": "4.0"
            }),
            "lipid_results": json.dumps({
                "Total_Cholesterol": "265",
                "LDL": "180",
                "HDL": "32",
                "Triglycerides": "210"
            }),
            "individual_tests": json.dumps({
                "Glucose": {
                    "status": "normal",
                    "findings": "قند خون ۹۵ میلی‌گرم در دسی‌لیتر در محدوده طبیعی (۷۰-۱۰۰)",
                    "clinical_significance": "عدم وجود دیابت که یکی از عوامل خطر اصلی قلبی-عروقی محسوب می‌شود، نکته مثبت برای کنترل ریسک"
                },
                "LDL": {
                    "status": "critical",
                    "findings": "کلسترول LDL برابر ۱۸۰ میلی‌گرم در دسی‌لیتر که در سطح خطرناک بالا قرار دارد",
                    "clinical_significance": "ریسک بسیار بالای تشکیل پلاک آترواسکلروتیک و سکته قلبی حاد"
                }
            }),
            "probable_diseases": json.dumps({
                "بیماری عروق کرونر": {
                    "probability": 88,
                    "reasoning": "LDL بسیار بالا، HDL بحرانی پایین، علائم آنژین ورزشی، فشار خون بالا، سابقه خانوادگی"
                },
                "آنژین صدری پایدار": {
                    "probability": 82,
                    "reasoning": "درد فشاری قفسه سینه هنگام ورزش با الگوی کلاسیک آنژین"
                }
            }),
            "recommendations": json.dumps([
                "شروع فوری استاتین پرقدرت (آتورواستاتین ۸۰ میلی‌گرم)",
                "تجویز کلوپیدوگرل ۷۵ میلی‌گرم روزانه به‌جای آسپرین",
                "بهینه‌سازی درمان فشار خون با اضافه کردن ACE inhibitor"
            ]),
            "red_flags": json.dumps([
                "LDL در سطح خطرناک ۱۸۰ میلی‌گرم که ریسک فوری سکته قلبی ایجاد می‌کند",
                "HDL بحرانی پایین ۳۲ میلی‌گرم که محافظت قلبی-عروقی را از بین برده است"
            ]),
            "ai_confidence_score": 0.92,
            "priority": "urgent"
        },
        {
            "patient_index": 1,  # فاطمه احمدی
            "report_type": "comprehensive",
            "title": "بررسی کنترل دیابت و عملکرد کلیه",
            "overall_assessment": "زن ۳۹ ساله با دیابت نوع ۲ تحت کنترل که نیاز به تنظیم دارو و پایش دقیق‌تر قند خون دارد",
            "bmp_results": json.dumps({
                "Glucose": "145",
                "BUN": "22",
                "Creatinine": "0.9",
                "HbA1c": "7.8"
            }),
            "individual_tests": json.dumps({
                "Glucose": {
                    "status": "abnormal",
                    "findings": "قند خون ۱۴۵ میلی‌گرم، بالاتر از حد طبیعی",
                    "clinical_significance": "نیاز به بهبود کنترل قند خون"
                }
            }),
            "probable_diseases": json.dumps({
                "دیابت نوع ۲ تحت کنترل": {
                    "probability": 95,
                    "reasoning": "سابقه دیابت و قند خون کمی بالا"
                }
            }),
            "ai_confidence_score": 0.87
        },
        {
            "patient_index": 2,  # علی کریمی
            "report_type": "comprehensive", 
            "title": "نتایج چک‌آپ سالانه",
            "overall_assessment": "مرد ۳۲ ساله کاملاً سالم با تمام پارامترهای آزمایشگاهی در محدوده طبیعی",
            "bmp_results": json.dumps({
                "Glucose": "88",
                "BUN": "15",
                "Creatinine": "0.8"
            }),
            "lipid_results": json.dumps({
                "Total_Cholesterol": "175",
                "LDL": "105",
                "HDL": "55",
                "Triglycerides": "90"
            }),
            "ai_confidence_score": 0.95
        }
    ]
    
    return reports_data

def populate_database():
    """Main function to populate database with sample data"""
    
    print("Starting database population...")
    
    # Get the laboratory (assuming first one exists)
    lab = Laboratory.query.first()
    if not lab:
        print("No laboratory found. Creating default laboratory...")
        lab = Laboratory(
            name="آزمایشگاه مدلب پرو",
            address="تهران، خیابان ولیعصر، پلاک 1",
            phone="021-88776655",
            email="info@medlabpro.com",
            license_number="LAB-001-2024"
        )
        db.session.add(lab)
        db.session.commit()
    
    # Get default user (assuming first admin exists)
    admin_user = User.query.filter_by(role='admin').first()
    if not admin_user:
        print("No admin user found. Creating default admin...")
        admin_user = User(
            username="admin",
            email="admin@medlabpro.com",
            full_name="Administrator",
            role="admin",
            laboratory_id=lab.id
        )
        admin_user.set_password("admin123")
        db.session.add(admin_user)
        db.session.commit()
    
    # Create patients
    patients_data = create_sample_patients()
    created_patients = []
    
    for i, patient_data in enumerate(patients_data):
        # Calculate BMI
        if patient_data['height'] and patient_data['weight']:
            height_m = patient_data['height'] / 100
            bmi = patient_data['weight'] / (height_m ** 2)
        else:
            bmi = None
            
        # Generate patient ID
        patient_id = f"P{str(i + 1).zfill(6)}"
        
        patient = Patient(
            patient_id=patient_id,
            first_name=patient_data['first_name'],
            last_name=patient_data['last_name'],
            national_id=patient_data['national_id'],
            date_of_birth=patient_data['date_of_birth'],
            gender=patient_data['gender'],
            phone=patient_data['phone'],
            email=patient_data['email'],
            address=patient_data['address'],
            medical_history=patient_data['medical_history'],
            current_symptoms=patient_data['current_symptoms'],
            pain_description=patient_data['pain_description'],
            test_reason=patient_data['test_reason'],
            disease_type=patient_data['disease_type'],
            allergies=patient_data['allergies'],
            current_medications=patient_data['current_medications'],
            height=patient_data['height'],
            weight=patient_data['weight'],
            bmi=bmi,
            blood_type=patient_data['blood_type'],
            language_preference=patient_data['language_preference'],
            laboratory_id=lab.id
        )
        
        db.session.add(patient)
        created_patients.append(patient)
    
    db.session.commit()
    print(f"Created {len(created_patients)} patients")
    
    # Create AI reports
    reports_data = create_sample_ai_reports()
    created_reports = []
    
    for report_data in reports_data:
        patient = created_patients[report_data['patient_index']]
        
        # Generate report number
        report_number = f"RPT{datetime.now().strftime('%Y%m%d')}{str(len(created_reports) + 1).zfill(4)}"
        
        report = Report(
            report_number=report_number,
            patient_id=patient.id,
            report_type=report_data['report_type'],
            title=report_data['title'],
            overall_assessment=report_data['overall_assessment'],
            bmp_results=report_data.get('bmp_results'),
            lipid_results=report_data.get('lipid_results'),
            individual_tests=report_data.get('individual_tests'),
            probable_diseases=report_data.get('probable_diseases'),
            recommendations=report_data.get('recommendations'),
            red_flags=report_data.get('red_flags'),
            ai_confidence_score=report_data.get('ai_confidence_score', 0.85),
            priority=report_data.get('priority', 'normal'),
            language="fa",
            status="final",
            generated_by=admin_user.id,
            finalized_at=datetime.utcnow()
        )
        
        db.session.add(report)
        created_reports.append(report)
    
    db.session.commit()
    print(f"Created {len(created_reports)} AI reports")
    
    # Create some test orders and samples
    test_types = TestType.query.all()
    if not test_types:
        # Create basic test types
        basic_tests = [
            {"code": "BMP", "name": "Basic Metabolic Panel", "category": "Chemistry"},
            {"code": "LIPID", "name": "Lipid Panel", "category": "Chemistry"},
            {"code": "CBC", "name": "Complete Blood Count", "category": "Hematology"},
            {"code": "LFT", "name": "Liver Function Tests", "category": "Chemistry"},
            {"code": "TSH", "name": "Thyroid Stimulating Hormone", "category": "Endocrinology"}
        ]
        
        for test_data in basic_tests:
            test_type = TestType(
                code=test_data["code"],
                name=test_data["name"],
                category=test_data["category"],
                sample_type="blood",
                unit="Various",
                price=50.00,
                turnaround_time=24
            )
            db.session.add(test_type)
        
        db.session.commit()
        test_types = TestType.query.all()
    
    # Create test orders for patients with reports
    for i, patient in enumerate(created_patients[:3]):  # First 3 patients
        for test_type in test_types[:2]:  # BMP and LIPID
            order_number = f"ORD{datetime.now().strftime('%Y%m%d')}{str(i * 2 + test_types.index(test_type) + 1).zfill(4)}"
            
            test_order = TestOrder(
                order_number=order_number,
                patient_id=patient.id,
                test_type_id=test_type.id,
                ordered_by="Dr. رضا محمدی",
                status="completed",
                ordered_at=datetime.utcnow() - timedelta(days=1),
                completed_at=datetime.utcnow()
            )
            db.session.add(test_order)
    
    db.session.commit()
    print("Sample data population completed successfully!")

if __name__ == "__main__":
    with app.app_context():
        populate_database()