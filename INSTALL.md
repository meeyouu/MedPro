# Installation Guide - MedLab Pro

## راهنمای نصب سیستم مدیریت آزمایشگاه پزشکی مدیسیتا

This guide provides step-by-step instructions for installing and deploying MedLab Pro in both development and production environments.

## 📋 Prerequisites

### System Requirements
- **Operating System**: Linux (Ubuntu 20.04+, CentOS 8+, RHEL 8+)
- **CPU**: 2+ cores (4+ cores recommended for production)
- **Memory**: 4GB RAM minimum (8GB+ recommended for production)
- **Storage**: 20GB available space (50GB+ recommended for production)
- **Network**: Internet connection for AI services and updates

### Required Software
- **Docker**: Version 20.10 or higher
- **Docker Compose**: Version 2.0 or higher
- **Git**: For repository cloning
- **Text Editor**: For configuration file editing

## 🛠️ Development Installation

### Step 1: Clone Repository
```bash
# Clone the repository
git clone https://github.com/your-org/medlab-pro.git
cd medlab-pro

# Verify files are present
ls -la
```

### Step 2: Environment Setup
```bash
# Copy environment template
cp .env.example .env

# Edit environment variables
nano .env
```

Required environment variables:
```bash
# Database Configuration
DATABASE_URL=postgresql://medlab:your_password@localhost:5432/medlab_dev

# Session Security (generate a strong random key)
SESSION_SECRET=your_very_secure_session_secret_key_here

# AI Service API Keys (at least one required)
OPENAI_API_KEY=sk-your_openai_api_key_here
CLAUDE_API_KEY=sk-ant-your_claude_api_key
GEMINI_API_KEY=your_gemini_api_key
OPENROUTER_API_KEY=sk-or-your_openrouter_key

# Optional: SMS Integration
TWILIO_ACCOUNT_SID=your_twilio_sid
TWILIO_AUTH_TOKEN=your_twilio_token
TWILIO_PHONE_NUMBER=+1234567890

# Redis Configuration
REDIS_URL=redis://localhost:6379/0
```

### Step 3: Install Dependencies
```bash
# For Python development
pip install -r requirements.txt

# Or use the automated Replit environment
# Dependencies are automatically managed
```

### Step 4: Database Setup
```bash
# Start PostgreSQL (if using Docker)
docker run -d --name medlab-postgres \
  -e POSTGRES_DB=medlab_dev \
  -e POSTGRES_USER=medlab \
  -e POSTGRES_PASSWORD=your_password \
  -p 5432:5432 \
  postgres:15-alpine

# Initialize database tables
python -c "from app import app, db; app.app_context().push(); db.create_all()"
```

### Step 5: Run Development Server
```bash
# Start the application
gunicorn --bind 0.0.0.0:5000 --reuse-port --reload main:app

# Or use Python directly
python main.py
```

### Step 6: Access Application
- **Landing Page**: http://localhost:5000/
- **Login Page**: http://localhost:5000/login
- **Dashboard**: http://localhost:5000/dashboard (after login)

**Demo Credentials**:
- Username: `admin`
- Password: `admin` 
- Laboratory: `Demo Lab`

## 🚀 Production Installation

### Step 1: Prepare Production Environment
```bash
# Create application user
sudo useradd -m -s /bin/bash medlab
sudo usermod -aG docker medlab

# Create directory structure
sudo mkdir -p /opt/medlab/{data/postgres,data/redis,logs,uploads,ssl,backups}
sudo chown -R medlab:medlab /opt/medlab

# Switch to application user
sudo su - medlab
cd /opt/medlab
```

### Step 2: Clone and Configure
```bash
# Clone repository
git clone https://github.com/your-org/medlab-pro.git
cd medlab-pro

# Create production environment file
cp .env.example .env.prod
```

Edit `.env.prod` with production values:
```bash
# Production Database
DB_PASSWORD=very_secure_production_password
DATABASE_URL=postgresql://medlab_user:${DB_PASSWORD}@db:5432/medlab_prod

# Strong Session Secret (generate with: openssl rand -hex 32)
SESSION_SECRET=generate_a_32_byte_hex_string_here

# Production API Keys
OPENAI_API_KEY=your_production_openai_key
CLAUDE_API_KEY=your_production_claude_key
GEMINI_API_KEY=your_production_gemini_key
OPENROUTER_API_KEY=your_production_openrouter_key

# Redis Security
REDIS_PASSWORD=secure_redis_password

# Optional Production Features
TWILIO_ACCOUNT_SID=production_twilio_sid
TWILIO_AUTH_TOKEN=production_twilio_token
TWILIO_PHONE_NUMBER=+1234567890

# Environment
FLASK_ENV=production
LOG_LEVEL=INFO
```

### Step 3: SSL Certificate Setup (Recommended)
```bash
# Option 1: Self-signed certificate (development/testing)
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout ./ssl/medlab.key \
  -out ./ssl/medlab.crt \
  -subj "/C=US/ST=State/L=City/O=Organization/CN=yourdomain.com"

# Option 2: Let's Encrypt (production)
# Install certbot and obtain certificates
sudo certbot certonly --standalone -d yourdomain.com
sudo cp /etc/letsencrypt/live/yourdomain.com/fullchain.pem ./ssl/medlab.crt
sudo cp /etc/letsencrypt/live/yourdomain.com/privkey.pem ./ssl/medlab.key
sudo chown medlab:medlab ./ssl/*
```

### Step 4: Deploy with Docker Compose
```bash
# Load environment variables
source .env.prod

# Build and start services
docker-compose -f docker-compose.prod.yml up --build -d

# Verify deployment
docker-compose -f docker-compose.prod.yml ps
```

### Step 5: Verify Installation
```bash
# Check application health
curl -f http://localhost/health

# Check SSL (if configured)
curl -f https://yourdomain.com/health

# View application logs
docker-compose -f docker-compose.prod.yml logs -f web

# Check database connectivity
docker-compose -f docker-compose.prod.yml exec web python -c "
from app import db
try:
    db.session.execute(db.text('SELECT version()'))
    print('Database connected successfully')
except Exception as e:
    print(f'Database error: {e}')
"
```

## 🔧 Advanced Configuration

### Nginx Reverse Proxy Configuration
Edit `nginx.prod.conf` for custom domains:
```nginx
server {
    listen 443 ssl http2;
    server_name yourdomain.com www.yourdomain.com;
    
    ssl_certificate /etc/nginx/ssl/medlab.crt;
    ssl_certificate_key /etc/nginx/ssl/medlab.key;
    
    # Add your custom configuration here
}
```

### Database Performance Tuning
Edit `postgresql.conf` for production optimization:
```bash
# Memory Configuration (adjust based on available RAM)
shared_buffers = 256MB                  # 25% of RAM
effective_cache_size = 1GB              # 75% of RAM
work_mem = 4MB                          # Per connection
maintenance_work_mem = 64MB

# Connection Settings
max_connections = 100
listen_addresses = '*'

# Logging
log_statement = 'mod'
log_min_duration_statement = 1000       # Log slow queries
log_connections = on
log_disconnections = on
```

### Redis Configuration
Edit `redis.conf` for production:
```bash
# Security
requirepass your_redis_password
protected-mode yes

# Persistence
save 900 1      # Save if at least 1 key changed in 900 seconds
save 300 10     # Save if at least 10 keys changed in 300 seconds
save 60 10000   # Save if at least 10000 keys changed in 60 seconds

# Memory Management
maxmemory 512mb
maxmemory-policy allkeys-lru

# Networking
bind 127.0.0.1
port 6379
```

## 📊 Monitoring and Maintenance

### Health Monitoring
```bash
# Create monitoring script
cat > /opt/medlab/monitor.sh << 'EOF'
#!/bin/bash
# Simple monitoring script for MedLab Pro

echo "=== MedLab Pro Health Check ==="
echo "Date: $(date)"

# Check Docker services
echo "Docker Services:"
docker-compose -f /opt/medlab/medlab-pro/docker-compose.prod.yml ps

# Check application health
echo -e "\nApplication Health:"
curl -s http://localhost/health | python -m json.tool

# Check disk usage
echo -e "\nDisk Usage:"
df -h /opt/medlab

# Check memory usage
echo -e "\nMemory Usage:"
free -h

echo "=== End Health Check ==="
EOF

chmod +x /opt/medlab/monitor.sh

# Schedule monitoring (crontab)
echo "*/5 * * * * /opt/medlab/monitor.sh >> /opt/medlab/logs/monitor.log 2>&1" | crontab -
```

### Backup Configuration
```bash
# Create backup script
cat > /opt/medlab/backup.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="/opt/medlab/backups"
DATE=$(date +%Y%m%d_%H%M%S)

# Database backup
docker-compose -f /opt/medlab/medlab-pro/docker-compose.prod.yml exec -T db \
  pg_dump -U medlab_user -d medlab_prod | gzip > "$BACKUP_DIR/db_backup_$DATE.sql.gz"

# Application data backup
tar -czf "$BACKUP_DIR/app_data_$DATE.tar.gz" /opt/medlab/uploads /opt/medlab/logs

# Cleanup old backups (keep 30 days)
find $BACKUP_DIR -name "*.gz" -mtime +30 -delete

echo "Backup completed: $DATE"
EOF

chmod +x /opt/medlab/backup.sh

# Schedule daily backups at 2 AM
echo "0 2 * * * /opt/medlab/backup.sh >> /opt/medlab/logs/backup.log 2>&1" | crontab -
```

### Log Rotation
```bash
# Configure logrotate
sudo tee /etc/logrotate.d/medlab << 'EOF'
/opt/medlab/logs/*.log {
    daily
    rotate 30
    compress
    delaycompress
    missingok
    notifempty
    copytruncate
    postrotate
        docker-compose -f /opt/medlab/medlab-pro/docker-compose.prod.yml restart web
    endscript
}
EOF
```

## 🔒 Security Hardening

### Firewall Configuration
```bash
# Configure UFW firewall
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw allow 80/tcp    # HTTP
sudo ufw allow 443/tcp   # HTTPS
sudo ufw enable

# Optional: Restrict SSH access
sudo ufw limit ssh
```

### Docker Security
```bash
# Create non-root Docker execution
sudo usermod -aG docker medlab

# Set secure Docker daemon configuration
sudo tee /etc/docker/daemon.json << 'EOF'
{
    "live-restore": true,
    "userland-proxy": false,
    "no-new-privileges": true,
    "seccomp-profile": "/etc/docker/seccomp.json"
}
EOF

sudo systemctl restart docker
```

### Application Security
```bash
# Set secure file permissions
find /opt/medlab -type f -name "*.py" -exec chmod 644 {} \;
find /opt/medlab -type d -exec chmod 755 {} \;
chmod 600 /opt/medlab/medlab-pro/.env.prod
chmod 600 /opt/medlab/ssl/*

# Regular security updates
sudo apt update && sudo apt upgrade -y
```

## 🚨 Troubleshooting

### Common Installation Issues

1. **Docker Permission Denied**
```bash
# Fix Docker permissions
sudo usermod -aG docker $USER
# Log out and log back in, or run:
newgrp docker
```

2. **Database Connection Failed**
```bash
# Check PostgreSQL container
docker-compose -f docker-compose.prod.yml logs db

# Verify database credentials
docker-compose -f docker-compose.prod.yml exec db psql -U medlab_user -d medlab_prod -c "SELECT version();"
```

3. **AI Service Authentication Failed**
```bash
# Verify API key format
echo $OPENAI_API_KEY | grep -o "sk-[A-Za-z0-9]*"

# Test API connection
curl -H "Authorization: Bearer $OPENAI_API_KEY" \
  https://api.openai.com/v1/models
```

4. **SSL Certificate Issues**
```bash
# Check certificate validity
openssl x509 -in ./ssl/medlab.crt -text -noout

# Test SSL configuration
openssl s_client -connect yourdomain.com:443 -servername yourdomain.com
```

5. **Application Not Starting**
```bash
# Check container logs
docker-compose -f docker-compose.prod.yml logs web

# Verify environment variables
docker-compose -f docker-compose.prod.yml exec web env | grep -E "(DATABASE_URL|SESSION_SECRET|OPENAI_API_KEY)"

# Test health endpoint
curl -v http://localhost:5000/health
```

### Performance Issues

1. **Slow Database Queries**
```bash
# Enable query logging
docker-compose -f docker-compose.prod.yml exec db \
  psql -U medlab_user -d medlab_prod -c "
    ALTER SYSTEM SET log_min_duration_statement = 1000;
    SELECT pg_reload_conf();
  "

# Monitor slow queries
docker-compose -f docker-compose.prod.yml logs db | grep "duration:"
```

2. **High Memory Usage**
```bash
# Check container resource usage
docker stats

# Adjust container memory limits in docker-compose.prod.yml
# Restart services
docker-compose -f docker-compose.prod.yml restart
```

3. **AI Service Timeouts**
```bash
# Increase timeout values in gunicorn configuration
# Edit Dockerfile CMD section:
CMD ["gunicorn", "--timeout", "300", "--workers", "4", ...]
```

## 📞 Support and Next Steps

### Post-Installation Checklist
- [ ] Application accessible via web browser
- [ ] Demo login working (admin/admin/Demo Lab)
- [ ] Database connectivity verified
- [ ] AI services responding (test report generation)
- [ ] SSL certificate valid (if configured)
- [ ] Backup system operational
- [ ] Monitoring alerts configured
- [ ] Firewall rules applied
- [ ] Log rotation configured

### Getting Help
- **Documentation**: Refer to README.md for detailed feature information
- **Technical Issues**: Check the troubleshooting section above
- **API Keys**: Contact respective AI service providers
- **Custom Configuration**: Consult the advanced configuration sections

### Next Steps
1. **User Training**: Familiarize staff with the interface
2. **Data Migration**: Import existing patient data using Excel import feature
3. **Custom Branding**: Modify templates and styling for your laboratory
4. **Integration**: Set up external system integrations if needed
5. **Monitoring**: Implement comprehensive monitoring and alerting

---

**مدیسیتا (Medisita)** - نظام پیشرفته مدیریت آزمایشگاه پزشکی با هوش مصنوعی

For additional installation support, please contact the development team or refer to the comprehensive documentation provided.