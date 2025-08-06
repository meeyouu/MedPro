"""
SMS Service Integration Module
Handles Twilio SMS notifications for patients and staff
"""
import logging
from datetime import datetime
from twilio.rest import Client
from twilio.base.exceptions import TwilioException

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_twilio_connection(account_sid, auth_token, phone_number):
    """Test Twilio SMS service connection"""
    try:
        if not all([account_sid, auth_token, phone_number]):
            return {'success': False, 'error': 'Account SID, Auth Token, and Phone Number are required'}
        
        client = Client(account_sid, auth_token)
        
        # Test by fetching account information
        account = client.api.accounts(account_sid).fetch()
        
        if account.status == 'active':
            # Validate phone number format
            phone_numbers = client.incoming_phone_numbers.list(limit=10)
            valid_numbers = [num.phone_number for num in phone_numbers]
            
            if phone_number in valid_numbers or phone_number.startswith('+'):
                return {
                    'success': True,
                    'message': 'Twilio connection successful',
                    'account_name': account.friendly_name,
                    'phone_number': phone_number,
                    'status': account.status
                }
            else:
                return {'success': False, 'error': 'Phone number not found in account or invalid format'}
        else:
            return {'success': False, 'error': f'Account status: {account.status}'}
            
    except TwilioException as e:
        logger.error(f"Twilio connection test failed: {str(e)}")
        return {'success': False, 'error': f'Twilio error: {str(e)}'}
    except Exception as e:
        logger.error(f"SMS connection test failed: {str(e)}")
        return {'success': False, 'error': f'Connection failed: {str(e)}'}

def send_patient_notification(settings, patient_phone, message_type, data):
    """Send SMS notification to patient"""
    try:
        if not settings.sms_enabled or not all([settings.twilio_account_sid, settings.twilio_auth_token, settings.twilio_phone_number]):
            return {'success': False, 'error': 'SMS service not configured'}
        
        client = Client(settings.twilio_account_sid, settings.twilio_auth_token)
        
        # Generate message based on type
        message_content = _generate_patient_message(message_type, data)
        
        if not message_content:
            return {'success': False, 'error': 'Invalid message type'}
        
        # Send SMS
        message = client.messages.create(
            body=message_content,
            from_=settings.twilio_phone_number,
            to=patient_phone
        )
        
        return {
            'success': True,
            'message_sid': message.sid,
            'status': message.status,
            'message_type': message_type
        }
        
    except TwilioException as e:
        logger.error(f"Patient SMS notification failed: {str(e)}")
        return {'success': False, 'error': f'SMS send failed: {str(e)}'}
    except Exception as e:
        logger.error(f"Patient notification failed: {str(e)}")
        return {'success': False, 'error': f'Notification failed: {str(e)}'}

def send_staff_alert(settings, recipient_phone, alert_type, data):
    """Send SMS alert to laboratory staff"""
    try:
        if not settings.sms_enabled or not all([settings.twilio_account_sid, settings.twilio_auth_token, settings.twilio_phone_number]):
            return {'success': False, 'error': 'SMS service not configured'}
        
        client = Client(settings.twilio_account_sid, settings.twilio_auth_token)
        
        # Generate alert message
        message_content = _generate_staff_alert(alert_type, data)
        
        if not message_content:
            return {'success': False, 'error': 'Invalid alert type'}
        
        # Send SMS
        message = client.messages.create(
            body=message_content,
            from_=settings.twilio_phone_number,
            to=recipient_phone
        )
        
        return {
            'success': True,
            'message_sid': message.sid,
            'status': message.status,
            'alert_type': alert_type
        }
        
    except TwilioException as e:
        logger.error(f"Staff SMS alert failed: {str(e)}")
        return {'success': False, 'error': f'SMS send failed: {str(e)}'}
    except Exception as e:
        logger.error(f"Staff alert failed: {str(e)}")
        return {'success': False, 'error': f'Alert failed: {str(e)}'}

def send_bulk_notifications(settings, recipients, message_type, data):
    """Send bulk SMS notifications"""
    try:
        if not settings.sms_enabled or not all([settings.twilio_account_sid, settings.twilio_auth_token, settings.twilio_phone_number]):
            return {'success': False, 'error': 'SMS service not configured'}
        
        client = Client(settings.twilio_account_sid, settings.twilio_auth_token)
        results = []
        
        for recipient in recipients:
            try:
                phone = recipient.get('phone')
                patient_data = recipient.get('data', data)
                
                if not phone:
                    results.append({
                        'recipient': recipient.get('name', 'Unknown'),
                        'success': False,
                        'error': 'No phone number'
                    })
                    continue
                
                message_content = _generate_patient_message(message_type, patient_data)
                
                message = client.messages.create(
                    body=message_content,
                    from_=settings.twilio_phone_number,
                    to=phone
                )
                
                results.append({
                    'recipient': recipient.get('name', phone),
                    'success': True,
                    'message_sid': message.sid,
                    'status': message.status
                })
                
            except Exception as e:
                results.append({
                    'recipient': recipient.get('name', 'Unknown'),
                    'success': False,
                    'error': str(e)
                })
        
        successful = len([r for r in results if r['success']])
        
        return {
            'success': True,
            'total_sent': successful,
            'total_recipients': len(recipients),
            'results': results
        }
        
    except Exception as e:
        logger.error(f"Bulk SMS notification failed: {str(e)}")
        return {'success': False, 'error': f'Bulk notification failed: {str(e)}'}

def _generate_patient_message(message_type, data):
    """Generate patient SMS message content"""
    messages = {
        'test_ready': f"""
سلام {data.get('patient_name', '')},

آزمایش‌های شما آماده شده است.
شماره آزمایش: {data.get('test_number', '')}
تاریخ: {data.get('date', datetime.now().strftime('%Y-%m-%d'))}

لطفاً برای دریافت نتایج با آزمایشگاه تماس بگیرید.

آزمایشگاه مدلب پرو
        """,
        
        'appointment_reminder': f"""
یادآوری نوبت آزمایش

سلام {data.get('patient_name', '')},

نوبت آزمایش شما:
تاریخ: {data.get('appointment_date', '')}
ساعت: {data.get('appointment_time', '')}
آزمایش: {data.get('test_type', '')}

لطفاً ناشتا مراجعه کنید.

آزمایشگاه مدلب پرو
        """,
        
        'critical_result': f"""
⚠️ نتیجه مهم آزمایش

سلام {data.get('patient_name', '')},

نتایج آزمایش شما نیاز به مراجعه فوری دارد.
لطفاً هرچه سریع‌تر با پزشک معالج خود تماس بگیرید.

شماره آزمایش: {data.get('test_number', '')}

آزمایشگاه مدلب پرو
        """,
        
        'report_ready': f"""
گزارش AI آماده شد

سلام {data.get('patient_name', '')},

گزارش تحلیل هوش مصنوعی آزمایش‌های شما آماده است.
شماره گزارش: {data.get('report_number', '')}

می‌توانید از پورتال بیمار دریافت کنید.

آزمایشگاه مدلب پرو
        """
    }
    
    return messages.get(message_type)

def _generate_staff_alert(alert_type, data):
    """Generate staff SMS alert content"""
    alerts = {
        'critical_result': f"""
🚨 CRITICAL RESULT ALERT

Patient: {data.get('patient_name', '')}
Test: {data.get('test_name', '')}
Value: {data.get('critical_value', '')}
Reference: {data.get('reference_range', '')}

Immediate attention required.

MedLab Pro System
        """,
        
        'system_error': f"""
⚠️ SYSTEM ALERT

Error Type: {data.get('error_type', '')}
Location: {data.get('location', '')}
Time: {datetime.now().strftime('%Y-%m-%d %H:%M')}

Check system immediately.

MedLab Pro System
        """,
        
        'new_urgent_test': f"""
🔴 URGENT TEST ORDER

Patient: {data.get('patient_name', '')}
Test: {data.get('test_type', '')}
Ordered by: {data.get('doctor_name', '')}
Priority: URGENT

Process immediately.

MedLab Pro System
        """,
        
        'equipment_maintenance': f"""
🔧 EQUIPMENT ALERT

Equipment: {data.get('equipment_name', '')}
Issue: {data.get('issue', '')}
Status: {data.get('status', '')}

Maintenance required.

MedLab Pro System
        """
    }
    
    return alerts.get(alert_type)