import os
import json
from datetime import datetime, date, timedelta
from flask import render_template, request, redirect, url_for, flash, session, jsonify, send_file, make_response
from werkzeug.security import check_password_hash, generate_password_hash
from sqlalchemy import func, desc, and_, or_
from werkzeug.utils import secure_filename
import pandas as pd
import io
from app import app, db
from models import Laboratory, User, Patient, TestType, TestOrder, Sample, Report, AuditLog, Settings
from translations import get_all_translations
from ai_services import test_openai_connection, test_claude_connection, test_gemini_connection, test_openrouter_connection, generate_medical_analysis
from sms_service import test_twilio_connection, send_patient_notification, send_staff_alert
from medisina_api import test_medisina_connection, export_to_medisina, import_from_medisina

def login_required(f):
    """Decorator to require login for protected routes"""
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def get_current_user():
    """Get current logged in user"""
    if 'user_id' in session:
        return User.query.get(session['user_id'])
    return None

def log_activity(action, table_name=None, record_id=None, old_values=None, new_values=None):
    """Log user activity for audit trail"""
    user = get_current_user()
    if user:
        log = AuditLog(
            user_id=user.id,
            action=action,
            table_name=table_name,
            record_id=record_id,
            old_values=json.dumps(old_values) if old_values else None,
            new_values=json.dumps(new_values) if new_values else None,
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent')
        )
        db.session.add(log)
        db.session.commit()

@app.route('/')
def landing():
    """Landing page for مدیسیتا (Medisita)"""
    return render_template('landing.html')

@app.route('/health')
def health_check():
    """Health check endpoint for Docker and load balancers"""
    try:
        # Check database connection
        db.session.execute(db.text('SELECT 1'))
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'version': '1.0.0',
            'database': 'connected'
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'timestamp': datetime.now().isoformat(),
            'error': str(e)
        }), 503

@app.route('/home')
def index():
    """Home page - redirect to dashboard if logged in, otherwise show login"""
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login page"""
    if request.method == 'POST':
        lab_name = request.form.get('labName') or request.form.get('lab_name') or 'Demo Lab'
        username = request.form.get('username')
        password = request.form.get('password')
        
        # Find laboratory by name
        laboratory = Laboratory.query.filter_by(name=lab_name).first()
        if not laboratory:
            # Create demo laboratory if it doesn't exist
            laboratory = Laboratory(
                name=lab_name,
                address="Demo Laboratory Address",
                phone="555-0123",
                email="demo@medlabpro.com",
                license_number="DEMO-001"
            )
            db.session.add(laboratory)
            db.session.commit()
        
        # Find user by username and laboratory
        user = User.query.filter_by(username=username, laboratory_id=laboratory.id).first()
        
        if not user:
            # Create demo user if it doesn't exist
            user = User(
                username=username,
                password_hash=generate_password_hash(password),
                full_name="Demo User",
                email="demo@medlab.com",
                role="admin",
                laboratory_id=laboratory.id
            )
            db.session.add(user)
            db.session.commit()
        
        if user and user.check_password(password):
            session['user_id'] = user.id
            session['laboratory_id'] = user.laboratory_id
            user.last_login = datetime.utcnow()
            db.session.commit()
            
            log_activity("User Login")
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid credentials', 'error')
    
    current_lang = session.get('language', 'en')
    return render_template('login.html', translations=get_all_translations(current_lang))

@app.route('/api/change-language', methods=['POST'])
def change_language():
    """Change user language preference"""
    data = request.get_json()
    language = data.get('language', 'en')
    
    if language in ['en', 'fa']:
        session['language'] = language
        return jsonify({'success': True, 'language': language})
    else:
        return jsonify({'success': False, 'error': 'Invalid language'})

@app.route('/logout')
@login_required
def logout():
    """Logout user"""
    log_activity("User Logout")
    session.clear()
    flash('You have been logged out', 'info')
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    """Main dashboard"""
    user = get_current_user()
    
    # Get dashboard statistics
    total_tests = TestOrder.query.filter_by().count()
    pending_results = TestOrder.query.filter_by(status='processing').count()
    completed_today = TestOrder.query.filter(
        func.date(TestOrder.completed_at) == date.today()
    ).count()
    critical_values = TestOrder.query.filter_by(result_status='critical').count()
    
    # Get recent activity (last 10 test orders)
    recent_tests = TestOrder.query.join(Patient).join(TestType).order_by(
        desc(TestOrder.ordered_at)
    ).limit(10).all()
    
    # Get test distribution by category
    test_distribution = db.session.query(
        TestType.category,
        func.count(TestOrder.id).label('count')
    ).join(TestOrder).group_by(TestType.category).all()
    
    # Get monthly trends (last 6 months) - PostgreSQL compatible
    six_months_ago = datetime.utcnow() - timedelta(days=180)
    monthly_trends = db.session.query(
        func.to_char(TestOrder.ordered_at, 'YYYY-MM').label('month'),
        func.count(TestOrder.id).label('count')
    ).filter(TestOrder.ordered_at >= six_months_ago).group_by('month').all()
    
    stats = {
        'total_tests': total_tests,
        'pending_results': pending_results,
        'completed_today': completed_today,
        'critical_values': critical_values
    }
    
    return render_template('dashboard.html', 
                         user=user, 
                         stats=stats,
                         recent_tests=recent_tests,
                         test_distribution=test_distribution,
                         monthly_trends=monthly_trends,
                         translations=get_all_translations(session.get('language', 'en')))

@app.route('/patients')
@login_required
def patients():
    """Patients list page"""
    user = get_current_user()
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '')
    
    query = Patient.query.filter_by(laboratory_id=user.laboratory_id)
    
    if search:
        query = query.filter(
            or_(
                Patient.first_name.contains(search),
                Patient.last_name.contains(search),
                Patient.patient_id.contains(search),
                Patient.phone.contains(search),
                Patient.email.contains(search)
            )
        )
    
    patients_pagination = query.order_by(desc(Patient.created_at)).paginate(
        page=page, per_page=20, error_out=False
    )
    
    return render_template('patients.html', 
                         user=user,
                         patients=patients_pagination.items,
                         pagination=patients_pagination,
                         search=search,
                         translations=get_all_translations(session.get('language', 'en')))

@app.route('/patients/add', methods=['GET', 'POST'])
@login_required
def add_patient():
    """Add new patient"""
    user = get_current_user()
    
    if request.method == 'POST':
        # Generate unique patient ID
        patient_count = Patient.query.filter_by(laboratory_id=user.laboratory_id).count()
        patient_id = f"P{str(patient_count + 1).zfill(6)}"
        
        dob_str = request.form.get('date_of_birth')
        dob = None
        if dob_str:
            try:
                dob = datetime.strptime(dob_str, '%Y-%m-%d').date()
            except ValueError:
                flash('Invalid date format', 'error')
                return redirect(url_for('add_patient'))
        
        # Calculate age from date of birth if provided
        age = request.form.get('age')
        if not age and dob:
            age = (date.today() - dob).days // 365

        patient = Patient(
            patient_id=patient_id,
            first_name=request.form.get('first_name'),
            last_name=request.form.get('last_name'),
            date_of_birth=dob,
            age=int(age) if age else None,
            gender=request.form.get('gender'),
            phone=request.form.get('phone'),
            email=request.form.get('email'),
            address=request.form.get('address'),
            national_id=request.form.get('national_id'),
            emergency_contact=request.form.get('emergency_contact'),
            emergency_phone=request.form.get('emergency_phone'),
            
            # Medical history and comprehensive fields
            medical_history=request.form.get('medical_history'),
            current_symptoms=request.form.get('current_symptoms'),
            pain_description=request.form.get('pain_description'),
            test_reason=request.form.get('test_reason'),
            disease_type=request.form.get('disease_type'),
            allergies=request.form.get('allergies'),
            current_medications=request.form.get('current_medications'),
            
            laboratory_id=user.laboratory_id
        )
        
        db.session.add(patient)
        db.session.commit()
        
        log_activity("Patient Added", "patients", patient.id, None, {
            'patient_id': patient.patient_id,
            'name': f"{patient.first_name} {patient.last_name}"
        })
        
        flash('Patient added successfully!', 'success')
        return redirect(url_for('patients'))
    
    return render_template('patients.html', 
                         user=user,
                         show_add_form=True,
                         translations=get_all_translations(session.get('language', 'en')))

@app.route('/tests')
@login_required
def tests():
    """Test orders page"""
    user = get_current_user()
    page = request.args.get('page', 1, type=int)
    status_filter = request.args.get('status', '')
    
    query = TestOrder.query.join(Patient).filter(
        Patient.laboratory_id == user.laboratory_id
    )
    
    if status_filter:
        query = query.filter(TestOrder.status == status_filter)
    
    test_orders = query.order_by(desc(TestOrder.ordered_at)).paginate(
        page=page, per_page=20, error_out=False
    )
    
    # Get available test types
    test_types = TestType.query.filter_by(is_active=True).all()
    
    # Get patients for new order form
    patients_list = Patient.query.filter_by(laboratory_id=user.laboratory_id).order_by(
        Patient.first_name, Patient.last_name
    ).all()
    
    return render_template('tests.html',
                         user=user,
                         test_orders=test_orders.items,
                         pagination=test_orders,
                         test_types=test_types,
                         patients=patients_list,
                         status_filter=status_filter,
                         translations=get_all_translations(session.get('language', 'en')))

@app.route('/tests/add', methods=['POST'])
@login_required
def add_test_order():
    """Add new test order"""
    user = get_current_user()
    
    # Generate unique order number
    order_count = TestOrder.query.count()
    order_number = f"ORD{datetime.now().strftime('%Y%m%d')}{str(order_count + 1).zfill(4)}"
    
    test_order = TestOrder(
        order_number=order_number,
        patient_id=int(request.form.get('patient_id')),
        test_type_id=int(request.form.get('test_type_id')),
        ordered_by=request.form.get('ordered_by', user.full_name if user else 'Unknown'),
        priority=request.form.get('priority', 'normal'),
        technician_id=user.id if user else None
    )
    
    db.session.add(test_order)
    db.session.commit()
    
    log_activity("Test Order Created", "test_orders", test_order.id, None, {
        'order_number': test_order.order_number,
        'patient_id': test_order.patient_id,
        'test_type_id': test_order.test_type_id
    })
    
    flash('Test order created successfully!', 'success')
    return redirect(url_for('tests'))

@app.route('/samples')
@login_required
def samples():
    """Sample tracking page"""
    user = get_current_user()
    page = request.args.get('page', 1, type=int)
    status_filter = request.args.get('status', '')
    
    query = Sample.query.join(TestOrder).join(Patient).filter(
        Patient.laboratory_id == user.laboratory_id
    )
    
    if status_filter:
        query = query.filter(Sample.status == status_filter)
    
    samples_pagination = query.order_by(desc(Sample.collection_date)).paginate(
        page=page, per_page=20, error_out=False
    )
    
    # Get test orders for new sample form
    test_orders = TestOrder.query.join(Patient).filter(
        Patient.laboratory_id == user.laboratory_id,
        TestOrder.status.in_(['pending', 'processing'])
    ).all()
    
    return render_template('samples.html',
                         user=user,
                         samples=samples_pagination.items,
                         test_orders=test_orders,
                         pagination=samples_pagination,
                         status_filter=status_filter,
                         translations=get_all_translations(session.get('language', 'en')))

@app.route('/reports')
@login_required
def reports():
    """Reports page"""
    user = get_current_user()
    
    # Get recent reports
    recent_reports = Report.query.join(Patient).filter(
        Patient.laboratory_id == user.laboratory_id
    ).order_by(desc(Report.created_at)).limit(10).all()
    
    return render_template('reports.html',
                         user=user,
                         recent_reports=recent_reports,
                         translations=get_all_translations(session.get('language', 'en')))

@app.route('/samples/add', methods=['POST'])
@login_required
def add_sample():
    """Add new sample"""
    user = get_current_user()
    
    # Generate unique sample ID
    sample_count = Sample.query.count()
    sample_id = f"SMP{datetime.now().strftime('%Y%m%d')}{str(sample_count + 1).zfill(4)}"
    
    collected_str = request.form.get('collected_at')
    collection_date = None
    if collected_str:
        try:
            collection_date = datetime.strptime(collected_str, '%Y-%m-%dT%H:%M')
        except ValueError:
            collection_date = datetime.utcnow()
    else:
        collection_date = datetime.utcnow()
    
    # Get the test order to find patient_id
    test_order = TestOrder.query.get_or_404(request.form.get('test_order_id'))
    
    sample = Sample(
        sample_id=sample_id,
        test_order_id=test_order.id,
        patient_id=test_order.patient_id,
        sample_type=request.form.get('sample_type'),
        collection_date=collection_date,
        volume=request.form.get('volume'),
        storage_condition=request.form.get('storage_conditions'),
        notes=request.form.get('collection_notes'),
        status='collected'
    )
    
    db.session.add(sample)
    db.session.commit()
    
    log_activity("Sample Added", "samples", sample.id, None, {
        'sample_id': sample.sample_id,
        'test_order_id': sample.test_order_id
    })
    
    flash('Sample added successfully!', 'success')
    return redirect(url_for('samples'))

@app.route('/patient-reports')
@login_required
def patient_reports():
    """Patient reports management page with import/export functionality"""
    user = get_current_user()
    page = request.args.get('page', 1, type=int)
    
    # Get patients with pagination
    patients_query = Patient.query.filter_by(laboratory_id=user.laboratory_id).order_by(desc(Patient.created_at))
    patients_pagination = patients_query.paginate(page=page, per_page=15, error_out=False)
    
    # Get statistics
    total_patients = Patient.query.filter_by(laboratory_id=user.laboratory_id).count()
    total_reports = Report.query.join(Patient).filter(Patient.laboratory_id == user.laboratory_id).count()
    imports_today = AuditLog.query.filter(
        AuditLog.action.like('%Import%'),
        func.date(AuditLog.timestamp) == date.today()
    ).count()
    exports_today = AuditLog.query.filter(
        AuditLog.action.like('%Export%'),
        func.date(AuditLog.timestamp) == date.today()
    ).count()
    
    # Get import/export history
    import_export_logs = AuditLog.query.filter(
        or_(AuditLog.action.like('%Import%'), AuditLog.action.like('%Export%'))
    ).order_by(desc(AuditLog.timestamp)).limit(20).all()
    
    return render_template('patient_reports.html',
                         user=user,
                         patients=patients_pagination.items,
                         pagination=patients_pagination,
                         total_patients=total_patients,
                         total_reports=total_reports,
                         imports_today=imports_today,
                         exports_today=exports_today,
                         import_export_logs=import_export_logs,
                         date_today=date.today(),
                         translations=get_all_translations(session.get('language', 'en')))

@app.route('/import-patient-reports', methods=['POST'])
@login_required
def import_patient_reports():
    """Import patient reports from JSON or Excel"""
    user = get_current_user()
    
    if 'import_file' not in request.files:
        flash('No file selected', 'error')
        return redirect(url_for('patient_reports'))
    
    file = request.files['import_file']
    if file.filename == '':
        flash('No file selected', 'error')
        return redirect(url_for('patient_reports'))
    
    import_format = request.form.get('import_format')
    validate_data = request.form.get('validate_data') == 'on'
    
    try:
        if import_format == 'json':
            # Handle JSON import
            data = json.load(file.stream)
            imported_count = _import_from_json(data, user, validate_data)
        elif import_format == 'excel':
            # Handle Excel import
            df = pd.read_excel(file)
            imported_count = _import_from_excel(df, user, validate_data)
        else:
            flash('Invalid file format', 'error')
            return redirect(url_for('patient_reports'))
        
        log_activity("Patient Data Import", "patients", None, None, {
            'format': import_format,
            'records_imported': imported_count,
            'file_name': secure_filename(file.filename or 'unknown')
        })
        
        flash(f'Successfully imported {imported_count} records', 'success')
        
    except Exception as e:
        flash(f'Import failed: {str(e)}', 'error')
        log_activity("Patient Data Import Failed", "patients", None, None, {
            'error': str(e),
            'file_name': secure_filename(file.filename or 'unknown')
        })
    
    return redirect(url_for('patient_reports'))

@app.route('/export-patient-reports', methods=['GET', 'POST'])
@login_required
def export_patient_reports():
    """Export patient reports to JSON or Excel"""
    user = get_current_user()
    
    # Handle GET request for single patient export
    if request.method == 'GET':
        patient_id = request.args.get('patient_id')
        export_format = request.args.get('format', 'json')
        
        if patient_id:
            patient = Patient.query.get_or_404(patient_id)
            if patient.laboratory_id != user.laboratory_id:
                flash('Access denied', 'error')
                return redirect(url_for('patient_reports'))
            
            return _export_single_patient(patient, export_format, user)
    
    # Handle POST request for bulk export
    export_format = request.form.get('export_format')
    date_range = request.form.get('date_range')
    include_fields = request.form.getlist('include_fields')
    patient_ids = request.form.getlist('patient_ids')
    
    # Build query based on parameters
    query = Patient.query.filter_by(laboratory_id=user.laboratory_id)
    
    # Filter by specific patients if provided
    if patient_ids:
        query = query.filter(Patient.id.in_(patient_ids))
    
    # Filter by date range
    if date_range != 'all':
        end_date = datetime.utcnow()
        if date_range == 'last_30':
            start_date = end_date - timedelta(days=30)
        elif date_range == 'last_90':
            start_date = end_date - timedelta(days=90)
        elif date_range == 'last_year':
            start_date = end_date - timedelta(days=365)
        elif date_range == 'custom':
            start_date_str = request.form.get('start_date')
            end_date_str = request.form.get('end_date')
            if start_date_str and end_date_str:
                start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
                end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
            else:
                start_date = end_date - timedelta(days=30)
        
        if date_range != 'all':
            query = query.filter(Patient.created_at.between(start_date, end_date))
    
    patients = query.all()
    
    if not patients:
        flash('No patients found for export', 'warning')
        return redirect(url_for('patient_reports'))
    
    try:
        if export_format == 'json':
            return _export_patients_json(patients, include_fields, user)
        elif export_format == 'excel':
            return _export_patients_excel(patients, include_fields, user)
        else:
            flash('Invalid export format', 'error')
            return redirect(url_for('patient_reports'))
    
    except Exception as e:
        flash(f'Export failed: {str(e)}', 'error')
        return redirect(url_for('patient_reports'))

def _import_from_json(data, user, validate_data):
    """Import patients from JSON data"""
    imported_count = 0
    
    if isinstance(data, dict) and 'patients' in data:
        patients_data = data['patients']
    elif isinstance(data, list):
        patients_data = data
    else:
        raise ValueError("Invalid JSON structure")
    
    for patient_data in patients_data:
        if validate_data:
            # Basic validation
            required_fields = ['first_name', 'last_name']
            for field in required_fields:
                if field not in patient_data:
                    continue  # Skip invalid records
        
        # Check if patient already exists
        existing_patient = Patient.query.filter_by(
            national_id=patient_data.get('national_id'),
            laboratory_id=user.laboratory_id
        ).first()
        
        if existing_patient:
            continue  # Skip existing patients
        
        # Generate unique patient ID
        patient_count = Patient.query.filter_by(laboratory_id=user.laboratory_id).count()
        patient_id = f"P{str(patient_count + imported_count + 1).zfill(6)}"
        
        # Parse date of birth
        dob = None
        if patient_data.get('date_of_birth'):
            try:
                dob = datetime.strptime(patient_data['date_of_birth'], '%Y-%m-%d').date()
            except ValueError:
                pass
        
        # Create new patient
        patient = Patient(
            patient_id=patient_id,
            first_name=patient_data.get('first_name'),
            last_name=patient_data.get('last_name'),
            date_of_birth=dob,
            gender=patient_data.get('gender'),
            phone=patient_data.get('phone'),
            email=patient_data.get('email'),
            address=patient_data.get('address'),
            national_id=patient_data.get('national_id'),
            emergency_contact=patient_data.get('emergency_contact'),
            emergency_phone=patient_data.get('emergency_phone'),
            medical_history=patient_data.get('medical_history'),
            allergies=patient_data.get('allergies'),
            medications=patient_data.get('medications'),
            laboratory_id=user.laboratory_id
        )
        
        db.session.add(patient)
        imported_count += 1
    
    db.session.commit()
    return imported_count

def _import_from_excel(df, user, validate_data):
    """Import patients from Excel DataFrame"""
    imported_count = 0
    
    # Map Excel columns to database fields
    column_mapping = {
        'First Name': 'first_name',
        'Last Name': 'last_name',
        'Date of Birth': 'date_of_birth',
        'Gender': 'gender',
        'Phone': 'phone',
        'Email': 'email',
        'Address': 'address',
        'National ID': 'national_id',
        'Emergency Contact': 'emergency_contact',
        'Emergency Phone': 'emergency_phone',
        'Medical History': 'medical_history',
        'Allergies': 'allergies',
        'Medications': 'medications'
    }
    
    for _, row in df.iterrows():
        patient_data = {}
        for excel_col, db_field in column_mapping.items():
            if excel_col in df.columns:
                patient_data[db_field] = row[excel_col] if pd.notna(row[excel_col]) else None
        
        if validate_data:
            # Basic validation
            if not patient_data.get('first_name') or not patient_data.get('last_name'):
                continue  # Skip invalid records
        
        # Check if patient already exists
        existing_patient = Patient.query.filter_by(
            national_id=patient_data.get('national_id'),
            laboratory_id=user.laboratory_id
        ).first()
        
        if existing_patient:
            continue  # Skip existing patients
        
        # Generate unique patient ID
        patient_count = Patient.query.filter_by(laboratory_id=user.laboratory_id).count()
        patient_id = f"P{str(patient_count + imported_count + 1).zfill(6)}"
        
        # Parse date of birth
        dob = None
        if patient_data.get('date_of_birth'):
            try:
                if isinstance(patient_data['date_of_birth'], str):
                    dob = datetime.strptime(patient_data['date_of_birth'], '%Y-%m-%d').date()
                else:
                    dob = patient_data['date_of_birth'].date()
            except (ValueError, AttributeError):
                pass
        
        # Create new patient
        patient = Patient(
            patient_id=patient_id,
            first_name=patient_data.get('first_name'),
            last_name=patient_data.get('last_name'),
            date_of_birth=dob,
            gender=patient_data.get('gender'),
            phone=patient_data.get('phone'),
            email=patient_data.get('email'),
            address=patient_data.get('address'),
            national_id=patient_data.get('national_id'),
            emergency_contact=patient_data.get('emergency_contact'),
            emergency_phone=patient_data.get('emergency_phone'),
            medical_history=patient_data.get('medical_history'),
            allergies=patient_data.get('allergies'),
            medications=patient_data.get('medications'),
            laboratory_id=user.laboratory_id
        )
        
        db.session.add(patient)
        imported_count += 1
    
    db.session.commit()
    return imported_count

def _export_single_patient(patient, export_format, user):
    """Export single patient data"""
    patient_data = _format_patient_data([patient], ['basic_info', 'test_results', 'medical_history', 'reports'])
    
    if export_format == 'json':
        json_data = json.dumps(patient_data, indent=2, default=str)
        
        response = make_response(json_data)
        response.headers['Content-Type'] = 'application/json'
        response.headers['Content-Disposition'] = f'attachment; filename=patient_{patient.patient_id}.json'
        
        log_activity("Patient Data Export", "patients", patient.id, None, {
            'format': 'json',
            'patient_id': patient.patient_id
        })
        
        return response
    
    elif export_format == 'excel':
        # Create Excel file
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            # Patient basic info
            basic_df = pd.DataFrame([{
                'Patient ID': patient.patient_id,
                'First Name': patient.first_name,
                'Last Name': patient.last_name,
                'Date of Birth': patient.date_of_birth,
                'Gender': patient.gender,
                'Phone': patient.phone,
                'Email': patient.email,
                'Address': patient.address,
                'National ID': patient.national_id,
                'Emergency Contact': patient.emergency_contact,
                'Emergency Phone': patient.emergency_phone,
                'Medical History': patient.medical_history,
                'Allergies': patient.allergies,
                'Medications': patient.medications
            }])
            basic_df.to_excel(writer, sheet_name='Patient Info', index=False)
            
            # Test results
            if patient.test_orders:
                test_data = []
                for test_order in patient.test_orders:
                    test_data.append({
                        'Order Number': test_order.order_number,
                        'Test Type': test_order.test_type.name if test_order.test_type else '',
                        'Ordered Date': test_order.ordered_at,
                        'Status': test_order.status,
                        'Result Value': test_order.result_value,
                        'Result Unit': test_order.result_unit,
                        'Result Status': test_order.result_status,
                        'Notes': test_order.result_notes
                    })
                
                if test_data:
                    test_df = pd.DataFrame(test_data)
                    test_df.to_excel(writer, sheet_name='Test Results', index=False)
            
            # Reports
            if patient.reports:
                report_data = []
                for report in patient.reports:
                    report_data.append({
                        'Report Number': report.report_number,
                        'Type': report.report_type,
                        'Title': report.title,
                        'Status': report.status,
                        'Created Date': report.created_at,
                        'AI Analysis': report.ai_analysis
                    })
                
                if report_data:
                    report_df = pd.DataFrame(report_data)
                    report_df.to_excel(writer, sheet_name='Reports', index=False)
        
        output.seek(0)
        
        log_activity("Patient Data Export", "patients", patient.id, None, {
            'format': 'excel',
            'patient_id': patient.patient_id
        })
        
        return send_file(
            output,
            as_attachment=True,
            download_name=f'patient_{patient.patient_id}.xlsx',
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )

def _export_patients_json(patients, include_fields, user):
    """Export multiple patients to JSON"""
    patients_data = _format_patient_data(patients, include_fields)
    
    json_data = json.dumps({
        'export_info': {
            'exported_at': datetime.utcnow().isoformat(),
            'exported_by': user.full_name,
            'total_patients': len(patients),
            'include_fields': include_fields
        },
        'patients': patients_data
    }, indent=2, default=str)
    
    response = make_response(json_data)
    response.headers['Content-Type'] = 'application/json'
    response.headers['Content-Disposition'] = f'attachment; filename=patients_export_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
    
    log_activity("Bulk Patient Data Export", "patients", None, None, {
        'format': 'json',
        'patient_count': len(patients),
        'include_fields': include_fields
    })
    
    return response

def _export_patients_excel(patients, include_fields, user):
    """Export multiple patients to Excel"""
    output = io.BytesIO()
    
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        # Patients basic info sheet
        if 'basic_info' in include_fields:
            patients_data = []
            for patient in patients:
                patients_data.append({
                    'Patient ID': patient.patient_id,
                    'First Name': patient.first_name,
                    'Last Name': patient.last_name,
                    'Date of Birth': patient.date_of_birth,
                    'Gender': patient.gender,
                    'Phone': patient.phone,
                    'Email': patient.email,
                    'Address': patient.address,
                    'National ID': patient.national_id,
                    'Emergency Contact': patient.emergency_contact,
                    'Emergency Phone': patient.emergency_phone,
                    'Created Date': patient.created_at
                })
            
            df = pd.DataFrame(patients_data)
            df.to_excel(writer, sheet_name='Patients', index=False)
        
        # Medical history sheet
        if 'medical_history' in include_fields:
            medical_data = []
            for patient in patients:
                medical_data.append({
                    'Patient ID': patient.patient_id,
                    'Patient Name': f"{patient.first_name} {patient.last_name}",
                    'Medical History': patient.medical_history,
                    'Allergies': patient.allergies,
                    'Medications': patient.medications
                })
            
            df = pd.DataFrame(medical_data)
            df.to_excel(writer, sheet_name='Medical History', index=False)
        
        # Test results sheet
        if 'test_results' in include_fields:
            test_data = []
            for patient in patients:
                for test_order in patient.test_orders:
                    test_data.append({
                        'Patient ID': patient.patient_id,
                        'Patient Name': f"{patient.first_name} {patient.last_name}",
                        'Order Number': test_order.order_number,
                        'Test Type': test_order.test_type.name if test_order.test_type else '',
                        'Ordered Date': test_order.ordered_at,
                        'Status': test_order.status,
                        'Result Value': test_order.result_value,
                        'Result Unit': test_order.result_unit,
                        'Result Status': test_order.result_status,
                        'Notes': test_order.result_notes
                    })
            
            if test_data:
                df = pd.DataFrame(test_data)
                df.to_excel(writer, sheet_name='Test Results', index=False)
        
        # Reports sheet
        if 'reports' in include_fields:
            report_data = []
            for patient in patients:
                for report in patient.reports:
                    report_data.append({
                        'Patient ID': patient.patient_id,
                        'Patient Name': f"{patient.first_name} {patient.last_name}",
                        'Report Number': report.report_number,
                        'Type': report.report_type,
                        'Title': report.title,
                        'Status': report.status,
                        'Created Date': report.created_at,
                        'AI Analysis': report.ai_analysis
                    })
            
            if report_data:
                df = pd.DataFrame(report_data)
                df.to_excel(writer, sheet_name='Reports', index=False)
    
    output.seek(0)
    
    log_activity("Bulk Patient Data Export", "patients", None, None, {
        'format': 'excel',
        'patient_count': len(patients),
        'include_fields': include_fields
    })
    
    return send_file(
        output,
        as_attachment=True,
        download_name=f'patients_export_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx',
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )

def _format_patient_data(patients, include_fields):
    """Format patient data for export"""
    patients_data = []
    
    for patient in patients:
        patient_dict = {}
        
        if 'basic_info' in include_fields:
            patient_dict.update({
                'patient_id': patient.patient_id,
                'first_name': patient.first_name,
                'last_name': patient.last_name,
                'date_of_birth': patient.date_of_birth.isoformat() if patient.date_of_birth else None,
                'gender': patient.gender,
                'phone': patient.phone,
                'email': patient.email,
                'address': patient.address,
                'national_id': patient.national_id,
                'emergency_contact': patient.emergency_contact,
                'emergency_phone': patient.emergency_phone,
                'created_at': patient.created_at.isoformat() if patient.created_at else None
            })
        
        if 'medical_history' in include_fields:
            patient_dict.update({
                'medical_history': patient.medical_history,
                'allergies': patient.allergies,
                'medications': patient.medications
            })
        
        if 'test_results' in include_fields:
            test_results = []
            for test_order in patient.test_orders:
                test_results.append({
                    'order_number': test_order.order_number,
                    'test_type': test_order.test_type.name if test_order.test_type else None,
                    'ordered_at': test_order.ordered_at.isoformat() if test_order.ordered_at else None,
                    'status': test_order.status,
                    'result_value': test_order.result_value,
                    'result_unit': test_order.result_unit,
                    'result_status': test_order.result_status,
                    'result_notes': test_order.result_notes
                })
            patient_dict['test_results'] = test_results
        
        if 'reports' in include_fields:
            reports = []
            for report in patient.reports:
                reports.append({
                    'report_number': report.report_number,
                    'report_type': report.report_type,
                    'title': report.title,
                    'status': report.status,
                    'created_at': report.created_at.isoformat() if report.created_at else None,
                    'ai_analysis': json.loads(report.ai_analysis) if report.ai_analysis else None
                })
            patient_dict['reports'] = reports
        
        patients_data.append(patient_dict)
    
    return patients_data

@app.route('/reports/generate', methods=['GET', 'POST'])
@login_required
def generate_report():
    """Generate AI-powered patient report"""
    user = get_current_user()
    
    # Handle GET request to display the page
    if request.method == 'GET':
        # Get all patients for the dropdown
        patients = Patient.query.filter_by(laboratory_id=user.laboratory_id).all()
        return render_template('generate_report.html',
                             user=user,
                             patients=patients,
                             translations=get_all_translations(user.language if user and hasattr(user, 'language') else 'en'))
    
    # Handle POST request to generate report
    patient_id = request.form.get('patient_id')
    report_type = request.form.get('report_type', 'comprehensive')
    
    patient = Patient.query.get_or_404(patient_id)
    
    # Get patient's test results
    test_results = db.session.query(TestOrder, TestType).join(TestType).filter(
        TestOrder.patient_id == patient_id,
        TestOrder.status == 'completed'
    ).order_by(desc(TestOrder.completed_at)).limit(20).all()
    
    # Prepare comprehensive data for AI analysis
    patient_data = {
        'name': f"{patient.first_name} {patient.last_name}",
        'age': (date.today() - patient.date_of_birth).days // 365 if patient.date_of_birth else None,
        'gender': patient.gender,
        'medical_history': patient.medical_history,
        'medications': patient.current_medications,
        'allergies': patient.allergies,
        'current_symptoms': patient.current_symptoms,
        'disease_type': patient.disease_type,
        'chief_complaint': patient.chief_complaint,
        'pain_description': patient.pain_description,
        'test_reason': patient.test_reason
    }
    
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
    ai_analysis = generate_patient_report_analysis(patient_data, test_data)
    
    if ai_analysis['success']:
        # Generate unique report number
        report_count = Report.query.count()
        report_number = f"RPT{datetime.now().strftime('%Y%m%d')}{str(report_count + 1).zfill(4)}"
        
        # Create report record
        analysis_data = ai_analysis['analysis']
        report = Report(
            report_number=report_number,
            patient_id=patient_id,
            report_type=report_type,
            title=f"Comprehensive Laboratory Report - {patient.first_name} {patient.last_name}",
            overall_assessment=analysis_data.get('overall_assessment', ''),
            individual_tests=json.dumps(analysis_data.get('individual_tests', {}), ensure_ascii=False),
            probable_diseases=json.dumps(analysis_data.get('probable_diseases', {}), ensure_ascii=False),
            recommendations=json.dumps(analysis_data.get('recommendations', []), ensure_ascii=False),
            red_flags=json.dumps(analysis_data.get('red_flags', []), ensure_ascii=False),
            interpretation=analysis_data.get('interpretation', ''),
            follow_up=analysis_data.get('follow_up', ''),
            ai_confidence_score=0.85,
            language='fa',
            generated_by=user.id if user else None,
            status='final'
        )
        
        db.session.add(report)
        db.session.commit()
        
        log_activity("AI Report Generated", "reports", report.id, None, {
            'report_number': report.report_number,
            'patient_id': patient_id,
            'type': report_type
        })
        
        flash('AI-powered report generated successfully!', 'success')
        return redirect(url_for('view_report', report_id=report.id))
    else:
        flash(f'Failed to generate report: {ai_analysis["error"]}', 'error')
        return redirect(url_for('reports'))

@app.route('/reports/<int:report_id>')
@login_required
def view_report(report_id):
    """View individual report"""
    user = get_current_user()
    
    report = Report.query.get_or_404(report_id)
    
    # Parse AI analysis from new fields
    ai_analysis = {
        'overall_assessment': report.overall_assessment,
        'individual_tests': json.loads(report.individual_tests) if report.individual_tests else {},
        'probable_diseases': json.loads(report.probable_diseases) if report.probable_diseases else {},
        'recommendations': json.loads(report.recommendations) if report.recommendations else [],
        'red_flags': json.loads(report.red_flags) if report.red_flags else [],
        'interpretation': report.interpretation,
        'follow_up': report.follow_up
    }
    
    # Check if this should be the comprehensive format
    if report.report_type == 'comprehensive':
        from datetime import date
        return render_template('comprehensive_report.html',
                             user=user,
                             report=report,
                             ai_analysis=ai_analysis,
                             date=date,
                             translations=get_all_translations(user.language if user and hasattr(user, 'language') else 'en'))
    else:
        return render_template('report_detail.html',
                             user=user,
                             report=report,
                             ai_analysis=ai_analysis,
                             translations=get_all_translations(user.language if user and hasattr(user, 'language') else 'en'))

@app.route('/reports/<int:report_id>/download')
@login_required
def download_report(report_id):
    """Download report as PDF"""
    user = get_current_user()
    report = Report.query.get_or_404(report_id)
    
    # For now, return JSON format - can be extended to PDF generation
    ai_analysis = {
        'overall_assessment': report.overall_assessment,
        'individual_tests': json.loads(report.individual_tests) if report.individual_tests else {},
        'probable_diseases': json.loads(report.probable_diseases) if report.probable_diseases else {},
        'recommendations': json.loads(report.recommendations) if report.recommendations else [],
        'red_flags': json.loads(report.red_flags) if report.red_flags else [],
        'interpretation': report.interpretation,
        'follow_up': report.follow_up
    }
    
    from flask import Response
    
    report_data = {
        'report_number': report.report_number,
        'title': report.title,
        'patient': {
            'name': f"{report.patient.first_name} {report.patient.last_name}",
            'age': (date.today() - report.patient.date_of_birth).days // 365 if report.patient.date_of_birth else None,
            'gender': report.patient.gender
        },
        'ai_analysis': ai_analysis,
        'created_at': report.created_at.isoformat() if report.created_at else None
    }
    
    response = Response(
        json.dumps(report_data, ensure_ascii=False, indent=2),
        mimetype='application/json',
        headers={'Content-Disposition': f'attachment; filename=report_{report.report_number}.json'}
    )
    
    return response

@app.route('/reports/<int:report_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_report(report_id):
    """Edit existing report"""
    user = get_current_user()
    report = Report.query.get_or_404(report_id)
    
    if request.method == 'POST':
        # Update report fields
        report.title = request.form.get('title', report.title)
        report.overall_assessment = request.form.get('overall_assessment', report.overall_assessment)
        report.interpretation = request.form.get('interpretation', report.interpretation)
        report.follow_up = request.form.get('follow_up', report.follow_up)
        
        db.session.commit()
        flash('Report updated successfully!', 'success')
        return redirect(url_for('view_report', report_id=report.id))
    
    # Parse AI analysis for editing
    ai_analysis = {
        'overall_assessment': report.overall_assessment,
        'individual_tests': json.loads(report.individual_tests) if report.individual_tests else {},
        'probable_diseases': json.loads(report.probable_diseases) if report.probable_diseases else {},
        'recommendations': json.loads(report.recommendations) if report.recommendations else [],
        'red_flags': json.loads(report.red_flags) if report.red_flags else [],
        'interpretation': report.interpretation,
        'follow_up': report.follow_up
    }
    
    return render_template('edit_report.html',
                         user=user,
                         report=report,
                         ai_analysis=ai_analysis,
                         translations=get_all_translations(user.language if user and hasattr(user, 'language') else 'en'))

@app.route('/reports/<int:report_id>/delete', methods=['POST'])
@login_required  
def delete_report(report_id):
    """Delete a report"""
    user = get_current_user()
    report = Report.query.get_or_404(report_id)
    
    # Log the deletion
    log_activity("Report Deleted", "reports", report.id, None, {
        'report_number': report.report_number,
        'patient_id': report.patient_id
    })
    
    db.session.delete(report)
    db.session.commit()
    
    flash('Report deleted successfully!', 'success')
    return redirect(url_for('reports'))

@app.route('/settings')
@login_required
def settings():
    """Settings page - comprehensive integrations configuration"""
    user = get_current_user()
    laboratory = Laboratory.query.get(user.laboratory_id)
    
    # Get or create settings for this laboratory
    settings = Settings.query.filter_by(laboratory_id=user.laboratory_id).first()
    if not settings:
        settings = Settings(laboratory_id=user.laboratory_id)
        db.session.add(settings)
        db.session.commit()
    
    return render_template('settings.html',
                         user=user,
                         laboratory=laboratory,
                         settings=settings,
                         translations=get_all_translations(user.language if user and hasattr(user, 'language') else 'en'))

@app.route('/settings/update', methods=['POST'])
@login_required
def update_settings():
    """Update comprehensive system settings"""
    user = get_current_user()
    
    # Update user settings
    user.language = request.form.get('language', 'en')
    user.theme = request.form.get('theme', 'light')
    
    if request.form.get('full_name'):
        user.full_name = request.form.get('full_name')
    
    if request.form.get('email'):
        user.email = request.form.get('email')
    
    # Update password if provided
    new_password = request.form.get('new_password')
    if new_password:
        user.set_password(new_password)
    
    # Update laboratory settings
    laboratory = Laboratory.query.get(user.laboratory_id)
    if laboratory and user.role == 'admin':
        laboratory.address = request.form.get('lab_address', laboratory.address)
        laboratory.phone = request.form.get('lab_phone', laboratory.phone)
        laboratory.email = request.form.get('lab_email', laboratory.email)
        laboratory.license_number = request.form.get('license_number', laboratory.license_number)
    
    db.session.commit()
    
    log_activity("Settings Updated")
    flash('Settings updated successfully!', 'success')
    return redirect(url_for('settings'))

@app.route('/settings/integrations', methods=['GET', 'POST'])
@login_required
def integration_settings():
    """Manage AI LLM, SMS, and MediSina API integrations"""
    user = get_current_user()
    
    # Only admin users can modify integration settings
    if user.role != 'admin':
        flash('Access denied. Only administrators can modify integration settings.', 'error')
        return redirect(url_for('settings'))
    
    # Get or create settings for this laboratory
    settings = Settings.query.filter_by(laboratory_id=user.laboratory_id).first()
    if not settings:
        settings = Settings(laboratory_id=user.laboratory_id)
        db.session.add(settings)
        db.session.commit()
    
    if request.method == 'POST':
        # AI LLM Settings
        settings.openai_api_key = request.form.get('openai_api_key', '').strip()
        settings.openai_model = request.form.get('openai_model', 'gpt-4o')
        settings.openai_enabled = request.form.get('openai_enabled') == 'on'
        
        settings.claude_api_key = request.form.get('claude_api_key', '').strip()
        settings.claude_model = request.form.get('claude_model', 'claude-sonnet-4-20250514')
        settings.claude_enabled = request.form.get('claude_enabled') == 'on'
        
        settings.gemini_api_key = request.form.get('gemini_api_key', '').strip()
        settings.gemini_model = request.form.get('gemini_model', 'gemini-2.5-flash')
        settings.gemini_enabled = request.form.get('gemini_enabled') == 'on'
        
        settings.openrouter_api_key = request.form.get('openrouter_api_key', '').strip()
        settings.openrouter_model = request.form.get('openrouter_model', '')
        settings.openrouter_enabled = request.form.get('openrouter_enabled') == 'on'
        
        settings.default_ai_service = request.form.get('default_ai_service', 'openai')
        
        # LangChain/LangSmith Settings
        settings.langchain_api_key = request.form.get('langchain_api_key', '').strip()
        settings.langsmith_enabled = request.form.get('langsmith_enabled') == 'on'
        settings.langsmith_project = request.form.get('langsmith_project', '')
        
        # SMS Settings
        settings.twilio_account_sid = request.form.get('twilio_account_sid', '').strip()
        settings.twilio_auth_token = request.form.get('twilio_auth_token', '').strip()
        settings.twilio_phone_number = request.form.get('twilio_phone_number', '').strip()
        settings.sms_enabled = request.form.get('sms_enabled') == 'on'
        
        # MediSina API Settings
        settings.medisina_api_url = request.form.get('medisina_api_url', '').strip()
        settings.medisina_api_key = request.form.get('medisina_api_key', '').strip()
        settings.medisina_username = request.form.get('medisina_username', '').strip()
        settings.medisina_password = request.form.get('medisina_password', '').strip()
        settings.medisina_enabled = request.form.get('medisina_enabled') == 'on'
        settings.medisina_sync_interval = int(request.form.get('medisina_sync_interval', '60'))
        settings.medisina_auto_sync = request.form.get('medisina_auto_sync') == 'on'
        
        # Export/Notification Settings
        settings.default_export_format = request.form.get('default_export_format', 'json')
        settings.include_ai_analysis = request.form.get('include_ai_analysis') == 'on'
        settings.include_patient_photos = request.form.get('include_patient_photos') == 'on'
        settings.email_notifications = request.form.get('email_notifications') == 'on'
        settings.sms_notifications = request.form.get('sms_notifications') == 'on'
        settings.critical_alerts_only = request.form.get('critical_alerts_only') == 'on'
        
        # System Settings
        settings.ai_analysis_language = request.form.get('ai_analysis_language', 'en')
        settings.max_concurrent_ai_requests = int(request.form.get('max_concurrent_ai_requests', '5'))
        settings.ai_timeout_seconds = int(request.form.get('ai_timeout_seconds', '120'))
        settings.updated_by = user.id
        
        db.session.commit()
        
        log_activity("Integration Settings Updated", "settings", settings.id, None, {
            'openai_enabled': settings.openai_enabled,
            'claude_enabled': settings.claude_enabled,
            'gemini_enabled': settings.gemini_enabled,
            'sms_enabled': settings.sms_enabled,
            'medisina_enabled': settings.medisina_enabled
        })
        
        flash('Integration settings updated successfully!', 'success')
        return redirect(url_for('integration_settings'))
    
    return render_template('integration_settings.html',
                         user=user,
                         settings=settings,
                         translations=get_all_translations(user.language if user and hasattr(user, 'language') else 'en'))

@app.route('/settings/test-connection', methods=['POST'])
@login_required
def test_connection():
    """Test external service connections"""
    user = get_current_user()
    
    if user.role != 'admin':
        return jsonify({'success': False, 'error': 'Access denied'})
    
    service = request.json.get('service')
    settings = Settings.query.filter_by(laboratory_id=user.laboratory_id).first()
    
    if not settings:
        return jsonify({'success': False, 'error': 'Settings not found'})
    
    try:
        if service == 'openai':
            result = test_openai_connection(settings.openai_api_key, settings.openai_model)
        elif service == 'claude':
            result = test_claude_connection(settings.claude_api_key, settings.claude_model)
        elif service == 'gemini':
            result = test_gemini_connection(settings.gemini_api_key, settings.gemini_model)
        elif service == 'openrouter':
            result = test_openrouter_connection(settings.openrouter_api_key, settings.openrouter_model)
        elif service == 'twilio':
            result = test_twilio_connection(settings.twilio_account_sid, settings.twilio_auth_token, settings.twilio_phone_number)
        elif service == 'medisina':
            result = test_medisina_connection(settings.medisina_api_url, settings.medisina_api_key, settings.medisina_username, settings.medisina_password)
        else:
            return jsonify({'success': False, 'error': 'Unknown service'})
        
        log_activity(f"Connection Test - {service.title()}", "settings", settings.id, None, {
            'service': service,
            'success': result['success']
        })
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/medisina/sync', methods=['POST'])
@login_required
def medisina_sync():
    """Sync patient data with MediSina API"""
    user = get_current_user()
    
    if user.role != 'admin':
        return jsonify({'success': False, 'error': 'Access denied'})
    
    settings = Settings.query.filter_by(laboratory_id=user.laboratory_id).first()
    
    if not settings or not settings.medisina_enabled:
        return jsonify({'success': False, 'error': 'MediSina integration not enabled'})
    
    try:
        # Get sync direction from request
        sync_direction = request.json.get('direction', 'export')  # export, import
        patient_ids = request.json.get('patient_ids', [])  # specific patients or empty for all
        
        if sync_direction == 'export':
            result = export_to_medisina(settings, patient_ids)
        else:
            result = import_from_medisina(settings)
        
        log_activity(f"MediSina Sync - {sync_direction.title()}", "settings", settings.id, None, {
            'direction': sync_direction,
            'patient_count': result.get('patient_count', 0),
            'success': result['success']
        })
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

# API endpoints for charts and dynamic data
@app.route('/api/dashboard-stats')
@login_required
def api_dashboard_stats():
    """API endpoint for dashboard statistics"""
    user = get_current_user()
    
    # Get test status distribution
    status_counts = db.session.query(
        TestOrder.status,
        func.count(TestOrder.id).label('count')
    ).join(Patient).filter(
        Patient.laboratory_id == user.laboratory_id
    ).group_by(TestOrder.status).all()
    
    # Get daily test counts for the last 30 days
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    daily_counts = db.session.query(
        func.date(TestOrder.ordered_at).label('date'),
        func.count(TestOrder.id).label('count')
    ).join(Patient).filter(
        Patient.laboratory_id == user.laboratory_id,
        TestOrder.ordered_at >= thirty_days_ago
    ).group_by('date').all()
    
    return jsonify({
        'status_distribution': [{'status': s[0], 'count': s[1]} for s in status_counts],
        'daily_counts': [{'date': str(d[0]), 'count': d[1]} for d in daily_counts]
    })

# Error handlers
@app.errorhandler(404)
def not_found_error(error):
    return render_template('base.html', error_message='Page not found', translations=get_all_translations('en')), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('base.html', error_message='Internal server error', translations=get_all_translations('en')), 500

# Context processors
@app.context_processor
def inject_user():
    """Inject current user and translations into all templates"""
    user = get_current_user()
    return dict(
        current_user=user,
        translations=get_all_translations(user.language if user and hasattr(user, 'language') else 'en')
    )

# Initialize sample data 
def create_sample_data():
    """Create sample test types and initial data"""
    if TestType.query.count() == 0:
        sample_tests = [
            TestType(code='CBC', name='Complete Blood Count', category='Hematology', sample_type='blood', unit='cells/μL', price=25.00),
            TestType(code='BMP', name='Basic Metabolic Panel', category='Chemistry', sample_type='blood', unit='mg/dL', price=35.00),
            TestType(code='LIPID', name='Lipid Panel', category='Chemistry', sample_type='blood', unit='mg/dL', price=40.00),
            TestType(code='TSH', name='Thyroid Stimulating Hormone', category='Endocrinology', sample_type='blood', unit='mIU/L', price=30.00),
            TestType(code='HBA1C', name='Hemoglobin A1c', category='Chemistry', sample_type='blood', unit='%', price=45.00)
        ]
        
        for test_type in sample_tests:
            db.session.add(test_type)
        
        db.session.commit()

# Call this function during startup in app.py

@app.route('/export-patient-data', methods=['POST'])
@login_required
def export_patient_data():
    """Export individual patient data (called from JavaScript)"""
    user = get_current_user()
    patient_id = request.form.get('patient_id')
    export_format = request.form.get('format', 'json')
    
    if not patient_id:
        flash('Patient ID is required', 'error')
        return redirect(url_for('patient_reports'))
    
    patient = Patient.query.filter_by(
        id=patient_id, 
        laboratory_id=user.laboratory_id
    ).first()
    
    if not patient:
        flash('Patient not found', 'error')
        return redirect(url_for('patient_reports'))
    
    try:
        return _export_single_patient(patient, export_format, user)
    except Exception as e:
        flash(f'Export failed: {str(e)}', 'error')
        return redirect(url_for('patient_reports'))



