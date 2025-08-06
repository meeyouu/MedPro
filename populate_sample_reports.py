#!/usr/bin/env python3
"""
Populate comprehensive AI reports for all sample patients
"""
import json
from datetime import datetime, date
from app import app, db
from models import Patient, Report

def create_comprehensive_reports():
    """Create comprehensive AI reports for all patients without using OpenAI API"""
    
    with app.app_context():
        # Get all patients
        patients = Patient.query.all()
        
        # Comprehensive report templates based on medical conditions
        report_templates = {
            'فشار خون بالا': {
                'overall_assessment': 'مرد ۴۵ ساله با فشار خون بالا شناخته شده و سابقه خانوادگی سکته قلبی که دارای اختلال شدید چربی خون و علائم مشکوک به آنژین صدری است، در معرض ریسک بسیار بالای حوادث قلبی-عروقی حاد قرار دارد و نیاز به مداخله فوری دارد.',
                'individual_tests': {
                    'LDL کلسترول': {
                        'status': 'critical',
                        'findings': 'کلسترول LDL برابر ۱۸۰ میلی‌گرم در دسی‌لیتر که در سطح خطرناک بالا قرار دارد',
                        'clinical_significance': 'ریسک بسیار بالای تشکیل پلاک آترواسکلروتیک و سکته قلبی حاد'
                    },
                    'HDL کلسترول': {
                        'status': 'critical',
                        'findings': 'HDL برابر ۳۲ میلی‌گرم در دسی‌لیتر که به شدت پایین است',
                        'clinical_significance': 'عدم حمایت کافی از عروق در برابر آترواسکلروز'
                    },
                    'تری‌گلیسرید': {
                        'status': 'abnormal',
                        'findings': 'سطح تری‌گلیسرید ۲۱۰ میلی‌گرم در دسی‌لیتر که بالا است',
                        'clinical_significance': 'افزایش ریسک پانکراتیت و بیماری‌های قلبی-عروقی'
                    }
                },
                'probable_diseases': {
                    'بیماری عروق کرونر': {
                        'probability': 88,
                        'reasoning': 'LDL بسیار بالا، HDL بحرانی پایین، علائم آنژین ورزشی، فشار خون بالا، سابقه خانوادگی'
                    },
                    'آنژین صدری پایدار': {
                        'probability': 82,
                        'reasoning': 'درد فشاری قفسه سینه هنگام ورزش با الگوی کلاسیک آنژین'
                    }
                },
                'recommendations': [
                    'شروع فوری استاتین با دوز بالا (آتورواستاتین ۸۰ میلی‌گرم شبانه)',
                    'آسپرین ۸۱ میلی‌گرم روزانه برای پیشگیری ثانویه',
                    'تنظیم دقیق فشار خون با هدف کمتر از ۱۳۰/۸۰',
                    'رژیم غذایی مدیترانه‌ای با محدودیت شدید چربی اشباع'
                ],
                'red_flags': [
                    'ریسک بالای سکته قلبی حاد در ۶ ماه آینده',
                    'نیاز به ارجاع فوری به کاردیولوژیست',
                    'در صورت تشدید درد قفسه سینه، مراجعه اورژانسی'
                ],
                'follow_up': 'کنترل چربی خون و عملکرد کبد پس از ۴ هفته، اکوکاردیوگرافی و تست ورزش در صورت امکان',
                'interpretation': 'بیمار دارای سندرم متابولیک با تمرکز بر اختلال چربی خون شدید است. با توجه به سابقه خانوادگی مثبت و علائم بالینی، احتمال بیماری عروق کرونر بسیار بالا بوده و نیاز به مداخله دارویی فوری و تغییرات اساسی سبک زندگی دارد.'
            },
            'دیابت نوع 2': {
                'overall_assessment': 'زن ۳۹ ساله با دیابت نوع ۲ تحت کنترل نسبی که علی‌رغم مصرف متفورمین، کنترل گلیسمی مطلوب ندارد و نیاز به تنظیم درمان دارد.',
                'individual_tests': {
                    'قند خون ناشتا': {
                        'status': 'critical',
                        'findings': 'قند خون ناشتا ۱۸۵ میلی‌گرم در دسی‌لیتر که به شدت بالا است',
                        'clinical_significance': 'عدم کنترل مطلوب دیابت و ریسک عوارض میکرو و ماکرووسکولار'
                    },
                    'هموگلوبین A1c': {
                        'status': 'abnormal',
                        'findings': 'HbA1c برابر ۸.۲ درصد که بالاتر از هدف درمانی است',
                        'clinical_significance': 'متوسط قند خون در ۳ ماه گذشته نامطلوب بوده'
                    },
                    'کراتینین': {
                        'status': 'abnormal',
                        'findings': 'کراتینین ۱.۴ میلی‌گرم در دسی‌لیتر که مرزی بالا است',
                        'clinical_significance': 'احتمال شروع نفروپاتی دیابتی'
                    }
                },
                'probable_diseases': {
                    'دیابت نوع ۲ کنترل‌نشده': {
                        'probability': 95,
                        'reasoning': 'قند بالا، HbA1c بالای ۷٪، علائم بالینی'
                    },
                    'نفروپاتی دیابتی ابتدایی': {
                        'probability': 70,
                        'reasoning': 'کراتینین مرزی بالا در بیمار دیابتی'
                    }
                },
                'recommendations': [
                    'افزایش دوز متفورمین به ۱۰۰۰ میلی‌گرم دو بار در روز',
                    'اضافه کردن اینیبیتور SGLT2 (امپاگلیفلوزین ۱۰ میلی‌گرم)',
                    'شروع لیراگلوتاید برای کنترل وزن و قند',
                    'رژیم غذایی کم کربوهیدرات با مشاوره تغذیه'
                ],
                'red_flags': [
                    'ریسک بالای عوارض دیابتی در صورت عدم کنترل',
                    'نیاز به پایش دقیق عملکرد کلیه'
                ],
                'follow_up': 'کنترل قند خون هفتگی، HbA1c و عملکرد کلیه پس از ۳ ماه، معاینه چشم‌پزشکی سالانه',
                'interpretation': 'بیمار نیاز به تنظیم مجدد درمان دیابت دارد. با توجه به علائم اولیه نفروپاتی، اولویت بر کنترل دقیق قند خون و حفاظت از کلیه‌ها است.'
            },
            'هیپوتیروئیدی': {
                'overall_assessment': 'زن ۲۸ ساله با علائم کلاسیک هیپوتیروئیدی که نیاز به شروع درمان جایگزینی هورمون تیروئید دارد.',
                'individual_tests': {
                    'TSH': {
                        'status': 'critical',
                        'findings': 'TSH برابر ۱۲.۵ میلی‌واحد در لیتر که به شدت بالا است',
                        'clinical_significance': 'نشان‌دهنده هیپوتیروئیدی آشکار'
                    },
                    'T4 آزاد': {
                        'status': 'low',
                        'findings': 'T4 آزاد ۴.۲ میکروگرم در دسی‌لیتر که پایین است',
                        'clinical_significance': 'تأیید کمبود هورمون تیروئید'
                    }
                },
                'probable_diseases': {
                    'هیپوتیروئیدی اولیه': {
                        'probability': 98,
                        'reasoning': 'TSH بالا، T4 پایین، علائم بالینی مطابق'
                    }
                },
                'recommendations': [
                    'شروع لووتیروکسین ۵۰ میکروگرم صبح ناشتا',
                    'پرهیز از مکمل‌های کلسیم و آهن تا ۴ ساعت بعد از دارو',
                    'کنترل وزن و ورزش منظم'
                ],
                'red_flags': [
                    'در صورت علائم شدید مثل میکسدم، مراجعه فوری'
                ],
                'follow_up': 'کنترل TSH و T4 پس از ۶-۸ هفته، تنظیم دوز بر اساس نتایج',
                'interpretation': 'تشخیص هیپوتیروئیدی قطعی است و نیاز به درمان جایگزینی دارد.'
            },
            'normal': {
                'overall_assessment': 'مرد ۳۲ ساله کاملاً سالم با تمام پارامترهای آزمایشگاهی در محدوده طبیعی که برای چک‌آپ سالانه مراجعه کرده.',
                'individual_tests': {
                    'قند خون': {
                        'status': 'normal',
                        'findings': 'قند خون ۸۵ میلی‌گرم در دسی‌لیتر در محدوده طبیعی',
                        'clinical_significance': 'عدم وجود دیابت یا پیش‌دیابت'
                    },
                    'کلسترول کل': {
                        'status': 'normal',
                        'findings': 'کلسترول کل ۱۶۵ میلی‌گرم در دسی‌لیتر در حد مطلوب',
                        'clinical_significance': 'ریسک پایین بیماری‌های قلبی-عروقی'
                    }
                },
                'probable_diseases': {
                    'وضعیت سالم': {
                        'probability': 100,
                        'reasoning': 'تمام آزمایش‌ها طبیعی، عدم علائم بیماری'
                    }
                },
                'recommendations': [
                    'ادامه سبک زندگی سالم',
                    'ورزش منظم حداقل ۱۵۰ دقیقه در هفته',
                    'رژیم غذایی متعادل غنی از میوه و سبزیجات'
                ],
                'red_flags': [],
                'follow_up': 'چک‌آپ سالانه، کنترل فشار خون هر ۶ ماه',
                'interpretation': 'بیمار در وضعیت سلامت مطلوبی قرار دارد و توصیه می‌شود سبک زندگی سالم خود را ادامه دهد.'
            }
        }
        
        reports_created = 0
        
        for patient in patients:
            # Skip if patient already has reports
            existing_reports = Report.query.filter_by(patient_id=patient.id).count()
            if existing_reports > 0:
                continue
                
            # Determine report template based on patient's disease type
            disease_type = patient.disease_type or 'normal'
            if disease_type not in report_templates:
                disease_type = 'normal'
            
            template = report_templates[disease_type]
            
            # Generate unique report number
            report_count = Report.query.count()
            report_number = f"RPT{datetime.now().strftime('%Y%m%d')}{str(report_count + 1).zfill(4)}"
            
            # Create appropriate title based on patient condition
            if disease_type == 'normal':
                title = f"گزارش چک‌آپ سالانه - {patient.first_name} {patient.last_name}"
            elif disease_type == 'فشار خون بالا':
                title = f"تحلیل جامع آزمایشات قلبی-عروقی - {patient.first_name} {patient.last_name}"
            elif disease_type == 'دیابت نوع 2':
                title = f"بررسی کنترل دیابت و عملکرد کلیه - {patient.first_name} {patient.last_name}"
            else:
                title = f"تحلیل جامع آزمایشات - {patient.first_name} {patient.last_name}"
            
            report = Report(
                report_number=report_number,
                patient_id=patient.id,
                report_type='comprehensive',
                title=title,
                overall_assessment=template['overall_assessment'],
                individual_tests=json.dumps(template['individual_tests'], ensure_ascii=False),
                probable_diseases=json.dumps(template['probable_diseases'], ensure_ascii=False),
                recommendations=json.dumps(template['recommendations'], ensure_ascii=False),
                red_flags=json.dumps(template['red_flags'], ensure_ascii=False),
                interpretation=template['interpretation'],
                follow_up=template['follow_up'],
                ai_confidence_score=0.92,
                language='fa',
                status='final'
            )
            
            db.session.add(report)
            reports_created += 1
            
            print(f"Created report for patient: {patient.first_name} {patient.last_name} ({disease_type})")
        
        db.session.commit()
        print(f"\nSuccessfully created {reports_created} comprehensive AI reports!")
        
        # Print summary
        total_reports = Report.query.count()
        total_patients = Patient.query.count()
        print(f"Total patients: {total_patients}")
        print(f"Total reports: {total_reports}")

if __name__ == "__main__":
    create_comprehensive_reports()