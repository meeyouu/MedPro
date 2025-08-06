from datetime import datetime
from app import db
from werkzeug.security import generate_password_hash, check_password_hash

class Laboratory(db.Model):
    __tablename__ = 'laboratories'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    address = db.Column(db.Text)
    phone = db.Column(db.String(20))
    email = db.Column(db.String(100))
    license_number = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    users = db.relationship('User', backref='laboratory', lazy=True)
    patients = db.relationship('Patient', backref='laboratory', lazy=True)

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    email = db.Column(db.String(100))
    full_name = db.Column(db.String(100))
    role = db.Column(db.String(20), default='technician')  # admin, technician, doctor
    language = db.Column(db.String(5), default='en')
    theme = db.Column(db.String(10), default='light')
    laboratory_id = db.Column(db.Integer, db.ForeignKey('laboratories.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    is_active = db.Column(db.Boolean, default=True)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def is_authenticated(self):
        return True
    
    def is_active_user(self):
        return self.is_active
    
    def get_id(self):
        return str(self.id)

class Patient(db.Model):
    __tablename__ = 'patients'
    
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.String(20), unique=True, nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    date_of_birth = db.Column(db.Date)
    age = db.Column(db.Integer)
    gender = db.Column(db.String(10))
    phone = db.Column(db.String(20))
    email = db.Column(db.String(100))
    address = db.Column(db.Text)
    national_id = db.Column(db.String(20))
    
    # Emergency contact information
    emergency_contact = db.Column(db.String(100))
    emergency_phone = db.Column(db.String(20))
    emergency_relation = db.Column(db.String(50))
    
    # Medical information from attached file
    medical_history = db.Column(db.Text)  # شرح حال پزشکی
    current_symptoms = db.Column(db.Text)  # علائم فعلی
    pain_description = db.Column(db.Text)  # توصیف درد
    test_reason = db.Column(db.Text)  # دلیل آزمایش
    disease_type = db.Column(db.String(100))  # نوع بیماری
    allergies = db.Column(db.Text)  # آلرژی‌ها
    current_medications = db.Column(db.Text)  # داروهای فعلی
    
    # Physical characteristics
    height = db.Column(db.Float)  # cm
    weight = db.Column(db.Float)  # kg
    bmi = db.Column(db.Float)
    blood_type = db.Column(db.String(5))
    
    # Insurance and billing
    insurance_provider = db.Column(db.String(100))
    insurance_number = db.Column(db.String(50))
    
    # Status and metadata
    status = db.Column(db.String(20), default='active')  # active, inactive, deceased
    language_preference = db.Column(db.String(5), default='en')
    laboratory_id = db.Column(db.Integer, db.ForeignKey('laboratories.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    test_orders = db.relationship('TestOrder', backref='patient', lazy=True)
    samples = db.relationship('Sample', backref='patient', lazy=True)

class TestType(db.Model):
    __tablename__ = 'test_types'
    
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(20), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    category = db.Column(db.String(50))
    sample_type = db.Column(db.String(50))  # blood, urine, saliva, etc.
    normal_range = db.Column(db.Text)
    unit = db.Column(db.String(20))
    price = db.Column(db.Numeric(10, 2))
    turnaround_time = db.Column(db.Integer)  # in hours
    preparation_instructions = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    test_orders = db.relationship('TestOrder', backref='test_type', lazy=True)

class TestOrder(db.Model):
    __tablename__ = 'test_orders'
    
    id = db.Column(db.Integer, primary_key=True)
    order_number = db.Column(db.String(20), unique=True, nullable=False)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id'), nullable=False)
    test_type_id = db.Column(db.Integer, db.ForeignKey('test_types.id'), nullable=False)
    ordered_by = db.Column(db.String(100))  # Doctor name
    priority = db.Column(db.String(20), default='normal')  # urgent, normal, routine
    status = db.Column(db.String(20), default='ordered')  # ordered, collected, processing, completed, reported
    result_value = db.Column(db.String(100))
    result_unit = db.Column(db.String(20))
    result_status = db.Column(db.String(20))  # normal, abnormal, critical
    result_notes = db.Column(db.Text)
    reference_range = db.Column(db.String(100))
    ordered_at = db.Column(db.DateTime, default=datetime.utcnow)
    collected_at = db.Column(db.DateTime)
    processed_at = db.Column(db.DateTime)
    completed_at = db.Column(db.DateTime)
    reported_at = db.Column(db.DateTime)
    technician_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    verified_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    # Relationships
    samples = db.relationship('Sample', backref='test_order', lazy=True)
    technician = db.relationship('User', foreign_keys=[technician_id], backref='processed_tests')
    verifier = db.relationship('User', foreign_keys=[verified_by], backref='verified_tests')

class Sample(db.Model):
    __tablename__ = 'samples'
    
    id = db.Column(db.Integer, primary_key=True)
    sample_id = db.Column(db.String(20), unique=True, nullable=False)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id'), nullable=False)
    test_order_id = db.Column(db.Integer, db.ForeignKey('test_orders.id'), nullable=False)
    sample_type = db.Column(db.String(50), nullable=False)
    collection_method = db.Column(db.String(50))
    collection_site = db.Column(db.String(50))
    volume = db.Column(db.String(20))
    container_type = db.Column(db.String(50))
    collection_date = db.Column(db.DateTime, nullable=False)
    collection_time = db.Column(db.Time)
    collected_by = db.Column(db.String(100))
    storage_condition = db.Column(db.String(50))
    storage_location = db.Column(db.String(100))
    status = db.Column(db.String(20), default='collected')  # collected, stored, processing, consumed, discarded
    quality_status = db.Column(db.String(20), default='acceptable')  # acceptable, rejected, hemolyzed, clotted
    rejection_reason = db.Column(db.Text)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Report(db.Model):
    __tablename__ = 'reports'
    
    id = db.Column(db.Integer, primary_key=True)
    report_number = db.Column(db.String(20), unique=True, nullable=False)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id'), nullable=False)
    report_type = db.Column(db.String(50), nullable=False)  # individual_test, comprehensive, ai_summary
    title = db.Column(db.String(200))
    
    # Basic report content
    content = db.Column(db.Text)
    language = db.Column(db.String(5), default='en')
    
    # AI Analysis fields based on attached JSON structure
    overall_assessment = db.Column(db.Text)  # ارزیابی کلی وضعیت سلامت
    individual_tests = db.Column(db.Text)  # JSON of individual test analysis
    probable_diseases = db.Column(db.Text)  # JSON of probable diseases with probabilities
    recommendations = db.Column(db.Text)  # JSON array of clinical recommendations
    follow_up = db.Column(db.Text)  # دستورالعمل‌های پیگیری
    red_flags = db.Column(db.Text)  # JSON array of critical findings
    interpretation = db.Column(db.Text)  # تفسیر پزشکی تفصیلی
    
    # Lab test results (JSON format)
    bmp_results = db.Column(db.Text)  # Basic Metabolic Panel results
    lipid_results = db.Column(db.Text)  # Lipid panel results
    cbc_results = db.Column(db.Text)  # Complete Blood Count results
    liver_function_results = db.Column(db.Text)  # Liver function tests
    thyroid_results = db.Column(db.Text)  # Thyroid function tests
    other_results = db.Column(db.Text)  # Other test results
    
    # Critical values and flags
    critical_values = db.Column(db.Text)
    abnormal_flags = db.Column(db.Text)
    
    # Medical context
    symptoms_at_time = db.Column(db.Text)  # Patient symptoms when tests were taken
    medications_at_time = db.Column(db.Text)  # Medications at time of testing
    clinical_context = db.Column(db.Text)  # Clinical reason for testing
    
    # Report metadata
    status = db.Column(db.String(20), default='draft')  # draft, final, delivered
    priority = db.Column(db.String(20), default='normal')  # urgent, normal, routine
    ai_confidence_score = db.Column(db.Float)  # AI analysis confidence (0-1)
    
    # User references
    generated_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    reviewed_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    finalized_at = db.Column(db.DateTime)
    delivered_at = db.Column(db.DateTime)
    
    # Relationships
    patient = db.relationship('Patient', backref='reports')
    generator = db.relationship('User', foreign_keys=[generated_by], backref='generated_reports')
    reviewer = db.relationship('User', foreign_keys=[reviewed_by], backref='reviewed_reports')

class Settings(db.Model):
    __tablename__ = 'settings'
    
    id = db.Column(db.Integer, primary_key=True)
    laboratory_id = db.Column(db.Integer, db.ForeignKey('laboratories.id'), nullable=False)
    
    # AI LLM Service Settings
    openai_api_key = db.Column(db.String(500))
    openai_model = db.Column(db.String(50), default='gpt-4o')
    openai_enabled = db.Column(db.Boolean, default=False)
    
    claude_api_key = db.Column(db.String(500))
    claude_model = db.Column(db.String(50), default='claude-sonnet-4-20250514')
    claude_enabled = db.Column(db.Boolean, default=False)
    
    gemini_api_key = db.Column(db.String(500))
    gemini_model = db.Column(db.String(50), default='gemini-2.5-flash')
    gemini_enabled = db.Column(db.Boolean, default=False)
    
    openrouter_api_key = db.Column(db.String(500))
    openrouter_model = db.Column(db.String(100))
    openrouter_enabled = db.Column(db.Boolean, default=False)
    
    # Default AI service to use
    default_ai_service = db.Column(db.String(20), default='openai')
    
    # LangChain & LangSmith Settings
    langchain_api_key = db.Column(db.String(500))
    langsmith_enabled = db.Column(db.Boolean, default=False)
    langsmith_project = db.Column(db.String(100))
    
    # SMS Center Settings (Twilio)
    twilio_account_sid = db.Column(db.String(500))
    twilio_auth_token = db.Column(db.String(500))
    twilio_phone_number = db.Column(db.String(20))
    sms_enabled = db.Column(db.Boolean, default=False)
    
    # MediSina API Settings
    medisina_api_url = db.Column(db.String(500))
    medisina_api_key = db.Column(db.String(500))
    medisina_username = db.Column(db.String(100))
    medisina_password = db.Column(db.String(500))
    medisina_enabled = db.Column(db.Boolean, default=False)
    medisina_sync_interval = db.Column(db.Integer, default=60)  # minutes
    medisina_auto_sync = db.Column(db.Boolean, default=False)
    
    # Export/Import Settings
    default_export_format = db.Column(db.String(10), default='json')  # json, excel
    include_ai_analysis = db.Column(db.Boolean, default=True)
    include_patient_photos = db.Column(db.Boolean, default=False)
    
    # Notification Settings
    email_notifications = db.Column(db.Boolean, default=True)
    sms_notifications = db.Column(db.Boolean, default=False)
    critical_alerts_only = db.Column(db.Boolean, default=False)
    
    # System Settings
    ai_analysis_language = db.Column(db.String(5), default='en')
    max_concurrent_ai_requests = db.Column(db.Integer, default=5)
    ai_timeout_seconds = db.Column(db.Integer, default=120)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    updated_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    # Relationships
    laboratory = db.relationship('Laboratory', backref='settings')
    updater = db.relationship('User', backref='updated_settings')

class AuditLog(db.Model):
    __tablename__ = 'audit_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    action = db.Column(db.String(100), nullable=False)
    table_name = db.Column(db.String(50))
    record_id = db.Column(db.Integer)
    old_values = db.Column(db.Text)
    new_values = db.Column(db.Text)
    ip_address = db.Column(db.String(45))
    user_agent = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref='audit_logs')
