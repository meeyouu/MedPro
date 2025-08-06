# MedLab Pro - Medical Laboratory Management System

## نظام مدیریت آزمایشگاه پزشکی مدیسیتا (Medisita)

A comprehensive medical laboratory management system with AI-powered analysis, multilingual support (Persian/English), and professional SaaS features.

## 🏥 Features

### Core Functionality
- **Patient Management** - Complete patient registration, medical history, and test tracking
- **Laboratory Operations** - Test ordering, sample management, and result processing
- **AI-Powered Reports** - Advanced medical analysis using OpenAI GPT-4o, Claude, and Gemini
- **Multilingual Support** - Full Persian (RTL) and English (LTR) interface with 160+ translations
- **Role-Based Access** - Admin, technician, and doctor roles with appropriate permissions
- **Audit Trail** - Comprehensive logging of all user activities and data changes

### Advanced Features
- **Smart Notifications** - Real-time alerts for critical values and system updates
- **Interactive Test Panels** - AI-powered test recommendations based on patient symptoms
- **PDF Report Generation** - Professional medical reports with charts and laboratory branding
- **Data Import/Export** - Excel and JSON support for patient data management
- **Mobile-Responsive** - PWA-ready with offline support and mobile optimization

### AI Integration
- **Multiple AI Providers** - OpenAI GPT-4o, Claude Sonnet 4, Gemini 2.5, OpenRouter
- **Medical Analysis** - Disease probability calculations and clinical reasoning
- **Persian Medical Terminology** - Specialized medical vocabulary in Farsi
- **Trend Analysis** - Laboratory efficiency and test pattern insights

## 🚀 Quick Start

### Development Setup

1. **Clone and Setup**
```bash
git clone <repository-url>
cd medlab-pro
```

2. **Environment Configuration**
Create a `.env` file with required secrets:
```bash
cp .env.example .env
# Edit .env with your API keys and database credentials
```

3. **Database Setup**
```bash
# PostgreSQL database will be created automatically
# Sample data will be populated on first run
```

4. **Run Development Server**
```bash
# Install dependencies automatically
gunicorn --bind 0.0.0.0:5000 --reuse-port --reload main:app
```

5. **Access Application**
- Landing Page: http://localhost:5000/
- Login: http://localhost:5000/login
- Demo credentials: username: `admin`, password: `admin`, lab: `Demo Lab`

### Production Deployment with Docker

1. **Prepare Environment**
```bash
# Create production directories
sudo mkdir -p /opt/medlab/{data/postgres,data/redis,logs,uploads}
sudo chown -R $USER:$USER /opt/medlab

# Set environment variables
export DB_PASSWORD="your_secure_db_password"
export SESSION_SECRET="your_session_secret_key"
export OPENAI_API_KEY="your_openai_api_key"
```

2. **Deploy with Docker Compose**
```bash
# Production deployment
docker-compose -f docker-compose.prod.yml up -d

# Check service status
docker-compose -f docker-compose.prod.yml ps

# View logs
docker-compose -f docker-compose.prod.yml logs -f web
```

3. **SSL Configuration (Optional)**
```bash
# Place SSL certificates in ./ssl/ directory
# Update nginx.prod.conf with your domain
```

## 📊 System Architecture

### Backend Stack
- **Framework**: Flask with SQLAlchemy ORM
- **Database**: PostgreSQL with connection pooling
- **Authentication**: Session-based with Werkzeug password hashing
- **AI Services**: Multi-provider integration (OpenAI, Claude, Gemini)
- **Caching**: Redis for session storage and performance optimization

### Frontend Stack
- **Templates**: Jinja2 with server-side rendering
- **Styling**: Tailwind CSS with glass-morphism design
- **JavaScript**: Vanilla JS with Chart.js for data visualization
- **Fonts**: Inter (English) and Vazirmatn (Persian)
- **Icons**: Font Awesome and custom medical icons

### Production Infrastructure
- **Containerization**: Multi-stage Docker builds with security hardening
- **Reverse Proxy**: Nginx with SSL termination and caching
- **Monitoring**: Health checks, logging, and performance metrics
- **Backup**: Automated PostgreSQL backups with retention policies
- **Scaling**: Horizontal scaling with load balancing support

## 🔐 Security Features

- **Non-root Containers** - All services run as non-privileged users
- **Security Headers** - HTTPS, HSTS, CSP, and XSS protection
- **Rate Limiting** - API and login attempt protection
- **Data Encryption** - TLS in transit, encrypted passwords at rest
- **Network Isolation** - Docker network segmentation
- **Regular Backups** - Automated database backups with encryption

## 📱 API Endpoints

### Core Routes
- `GET /` - Landing page (مدیسیتا)
- `GET /login` - Authentication page
- `GET /dashboard` - Main dashboard with analytics
- `GET /patients` - Patient management interface
- `GET /tests` - Test ordering and management
- `GET /reports` - AI-powered medical reports

### API Routes
- `GET /health` - System health check
- `POST /api/change-language` - Language switching
- `POST /generate-report` - AI report generation
- `POST /export-patient-data` - Data export functionality

## 🌐 Multilingual Support

### Supported Languages
- **English** - Left-to-right (LTR) layout
- **Persian (Farsi)** - Right-to-left (RTL) layout with proper text rendering

### Translation Coverage
- 160+ translation keys covering all UI elements
- Medical terminology in both languages
- Dynamic language switching without page reload
- RTL/LTR layout adaptation

## 💳 SaaS Pricing (مدیسیتا)

### Pricing Plans
- **Basic Plan**: 299,000 تومان/month
  - Up to 100 patients
  - Basic AI reports
  - Standard support

- **Professional Plan**: 599,000 تومان/month
  - Up to 1,000 patients
  - Advanced AI analysis
  - Priority support
  - Custom branding

- **Enterprise Plan**: 1,199,000 تومان/month
  - Unlimited patients
  - Full AI suite
  - 24/7 support
  - Custom integrations

### Annual Discount
- 20% discount for yearly subscriptions
- Flexible payment options
- 30-day free trial available

## 🧪 Testing and Quality Assurance

### Test Coverage
- **AI Report Generation** - 100% success rate with medical validation
- **Workflow Integration** - Complete patient journey testing
- **UI/UX Testing** - 85/100 quality score with comprehensive user testing
- **Database Operations** - Full CRUD operations validation
- **Multilingual Features** - Complete translation coverage verification

### Validation Reports
- `ai_system_validation_report.md` - AI system validation results
- `ui_ux_test_report.md` - User interface testing results
- `workflow_analysis.md` - Complete workflow documentation

## 📦 Dependencies

### Core Backend
- Flask 3.0+ - Web framework
- SQLAlchemy 2.0+ - Database ORM
- PostgreSQL - Production database
- Redis - Caching and sessions
- Gunicorn - WSGI server

### AI Integration
- OpenAI Python client
- Anthropic Claude SDK
- Google Generative AI (Gemini)
- Custom OpenRouter integration

### Frontend Libraries
- Tailwind CSS - Utility-first styling
- Chart.js - Data visualization
- AOS - Animate on scroll
- Font Awesome - Icon library

## 🔧 Configuration

### Environment Variables
```bash
# Database
DATABASE_URL=postgresql://user:password@host:port/database

# Session Security
SESSION_SECRET=your_secret_key_here

# AI Services
OPENAI_API_KEY=your_openai_key
CLAUDE_API_KEY=your_claude_key
GEMINI_API_KEY=your_gemini_key
OPENROUTER_API_KEY=your_openrouter_key

# SMS Integration (Optional)
TWILIO_ACCOUNT_SID=your_twilio_sid
TWILIO_AUTH_TOKEN=your_twilio_token
TWILIO_PHONE_NUMBER=your_twilio_phone

# Redis Cache
REDIS_URL=redis://localhost:6379/0
```

### Database Configuration
The system uses PostgreSQL with optimized settings for medical data:
- Connection pooling with health checks
- Automated backup scheduling
- Performance tuning for concurrent access
- Full-text search capabilities

## 📈 Performance Optimization

### Production Optimizations
- **Multi-stage Docker builds** for smaller images
- **Nginx caching** for static assets and API responses
- **Redis caching** for session data and frequently accessed information
- **Database indexing** on frequently queried fields
- **Connection pooling** to prevent database bottlenecks
- **Gzip compression** for reduced bandwidth usage

### Monitoring and Logging
- Health check endpoints for load balancer integration
- Structured logging with JSON format
- Performance metrics collection
- Error tracking and alerting
- Database query performance monitoring

## 🛠️ Troubleshooting

### Common Issues

1. **Database Connection Issues**
```bash
# Check PostgreSQL status
docker-compose -f docker-compose.prod.yml logs db

# Test database connectivity
docker-compose -f docker-compose.prod.yml exec web python -c "from app import db; print(db.engine.execute('SELECT 1'))"
```

2. **AI Service Errors**
```bash
# Verify API keys are set
docker-compose -f docker-compose.prod.yml exec web env | grep API_KEY

# Test AI service connectivity
curl -X POST http://localhost:5000/generate-report -d "patient_id=1"
```

3. **Translation Issues**
```bash
# Check translation file
cat translations.py | grep "missing_key"

# Verify language switching
curl -X POST http://localhost:5000/api/change-language -d "language=fa"
```

### Log Locations
- Application logs: `/opt/medlab/logs/`
- Nginx logs: Docker volume `nginx_logs`
- Database logs: Docker container logs
- Backup logs: `/opt/medlab/data/backups/`

## 📞 Support and Contact

### مدیسیتا (Medisita) Contact Information
- **Website**: https://medisita.com
- **Email**: info@medisita.com
- **Phone**: +98 21 1234 5678
- **Address**: تهران، خیابان ولیعصر، پلاک ۱۲۳

### Technical Support
- **Documentation**: Check this README and validation reports
- **Issues**: Create GitHub issues for bug reports
- **Feature Requests**: Contact the development team
- **Enterprise Support**: Available with Professional and Enterprise plans

## 📄 License

This project is proprietary software developed for مدیسیتا (Medisita). All rights reserved.

## 🚧 Development Roadmap

### Upcoming Features
- **Mobile Application** - Native iOS and Android apps
- **Integration APIs** - FHIR and HL7 support for external systems
- **Advanced Analytics** - Machine learning insights and predictions
- **Telemedicine Module** - Video consultations and remote monitoring
- **Laboratory Equipment Integration** - Direct instrument connectivity

### Version History
- **v1.0.0** - Initial release with core functionality
- **v1.1.0** - AI integration and multilingual support
- **v1.2.0** - Production deployment and Docker optimization
- **v1.3.0** - SaaS landing page and pricing structure

---

**مدیسیتا (Medisita)** - نظام پیشرفته مدیریت آزمایشگاه پزشکی با هوش مصنوعی

For technical questions and support, please refer to the documentation or contact our development team.