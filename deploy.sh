#!/bin/bash
# Production Deployment Script for MedLab Pro
# مدیسیتا (Medisita) - Medical Laboratory Management System

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_NAME="medlab-pro"
DEPLOY_DIR="/opt/medlab"
APP_USER="medlab"
COMPOSE_FILE="docker-compose.prod.yml"

echo -e "${GREEN}================================================${NC}"
echo -e "${GREEN} MedLab Pro Production Deployment Script${NC}"
echo -e "${GREEN} مدیسیتا - سیستم مدیریت آزمایشگاه پزشکی${NC}"
echo -e "${GREEN}================================================${NC}"

# Function to print status
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running as root
check_root() {
    if [[ $EUID -eq 0 ]]; then
        print_error "This script should not be run as root for security reasons."
        print_status "Please run as a regular user with sudo privileges."
        exit 1
    fi
}

# Check system requirements
check_requirements() {
    print_status "Checking system requirements..."
    
    # Check Docker
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    
    # Check Docker Compose
    if ! command -v docker-compose &> /dev/null; then
        print_error "Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    fi
    
    # Check available disk space (minimum 10GB)
    available_space=$(df . | tail -1 | awk '{print $4}')
    required_space=10485760  # 10GB in KB
    
    if [ "$available_space" -lt "$required_space" ]; then
        print_warning "Low disk space detected. At least 10GB is recommended."
    fi
    
    # Check available memory (minimum 2GB)
    available_mem=$(free -m | grep '^Mem:' | awk '{print $2}')
    required_mem=2048  # 2GB in MB
    
    if [ "$available_mem" -lt "$required_mem" ]; then
        print_warning "Low memory detected. At least 2GB RAM is recommended."
    fi
    
    print_success "System requirements check completed."
}

# Create application user
create_app_user() {
    print_status "Creating application user..."
    
    if id "$APP_USER" &>/dev/null; then
        print_status "User $APP_USER already exists."
    else
        sudo useradd -m -s /bin/bash "$APP_USER"
        sudo usermod -aG docker "$APP_USER"
        print_success "Created user $APP_USER and added to docker group."
    fi
}

# Create directory structure
create_directories() {
    print_status "Creating directory structure..."
    
    sudo mkdir -p "$DEPLOY_DIR"/{data/postgres,data/redis,logs,uploads,ssl,backups,config}
    sudo chown -R "$APP_USER:$APP_USER" "$DEPLOY_DIR"
    
    print_success "Directory structure created at $DEPLOY_DIR"
}

# Setup environment configuration
setup_environment() {
    print_status "Setting up environment configuration..."
    
    if [ ! -f .env.prod ]; then
        print_status "Creating production environment file..."
        cat > .env.prod << 'EOF'
# Production Environment Configuration
# Edit these values for your production deployment

# Database Configuration
DB_PASSWORD=CHANGE_THIS_SECURE_DB_PASSWORD
DATABASE_URL=postgresql://medlab_user:${DB_PASSWORD}@db:5432/medlab_prod

# Session Security (generate with: openssl rand -hex 32)
SESSION_SECRET=CHANGE_THIS_TO_A_SECURE_32_BYTE_HEX_STRING

# AI Service API Keys (at least one required)
OPENAI_API_KEY=your_production_openai_api_key
CLAUDE_API_KEY=your_production_claude_api_key
GEMINI_API_KEY=your_production_gemini_api_key
OPENROUTER_API_KEY=your_production_openrouter_api_key

# Redis Security
REDIS_PASSWORD=CHANGE_THIS_SECURE_REDIS_PASSWORD

# Optional: SMS Integration
TWILIO_ACCOUNT_SID=your_twilio_sid
TWILIO_AUTH_TOKEN=your_twilio_token
TWILIO_PHONE_NUMBER=+1234567890

# Production Settings
FLASK_ENV=production
LOG_LEVEL=INFO
EOF
        print_warning "Created .env.prod template. Please edit with your actual values!"
        print_status "Run: nano .env.prod to configure your environment."
        return 1
    else
        print_success "Production environment file already exists."
    fi
}

# Generate SSL certificates
setup_ssl() {
    print_status "Setting up SSL certificates..."
    
    if [ ! -f ./ssl/medlab.crt ]; then
        mkdir -p ./ssl
        
        read -p "Enter your domain name (or press Enter for localhost): " domain_name
        domain_name=${domain_name:-localhost}
        
        print_status "Generating self-signed SSL certificate for $domain_name..."
        openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
            -keyout ./ssl/medlab.key \
            -out ./ssl/medlab.crt \
            -subj "/C=US/ST=State/L=City/O=MedLab Pro/CN=$domain_name"
        
        chmod 600 ./ssl/*
        print_success "SSL certificate generated."
        print_warning "For production, replace with proper SSL certificates from a CA."
    else
        print_success "SSL certificates already exist."
    fi
}

# Build and deploy application
deploy_application() {
    print_status "Building and deploying application..."
    
    # Check if .env.prod is configured
    if grep -q "CHANGE_THIS" .env.prod; then
        print_error "Please configure .env.prod with your actual values before deployment."
        print_status "Edit .env.prod and replace all CHANGE_THIS placeholders."
        return 1
    fi
    
    # Load environment variables
    export $(grep -v '^#' .env.prod | xargs)
    
    # Build and start services
    print_status "Building Docker images..."
    docker-compose -f "$COMPOSE_FILE" build --no-cache
    
    print_status "Starting production services..."
    docker-compose -f "$COMPOSE_FILE" up -d
    
    # Wait for services to be healthy
    print_status "Waiting for services to be ready..."
    sleep 30
    
    # Check health
    if curl -f -s http://localhost/health > /dev/null 2>&1; then
        print_success "Application deployed successfully!"
    else
        print_error "Application health check failed. Check logs with: docker-compose -f $COMPOSE_FILE logs"
        return 1
    fi
}

# Setup monitoring and backups
setup_monitoring() {
    print_status "Setting up monitoring and backups..."
    
    # Create monitoring script
    cat > "$DEPLOY_DIR/monitor.sh" << 'EOF'
#!/bin/bash
# MedLab Pro Monitoring Script

echo "=== MedLab Pro Health Check - $(date) ==="

# Check Docker services
echo "Docker Services Status:"
docker-compose -f /opt/medlab/medlab-pro/docker-compose.prod.yml ps

# Check application health
echo -e "\nApplication Health:"
curl -s -f http://localhost/health | python -m json.tool 2>/dev/null || echo "Health check failed"

# Check system resources
echo -e "\nSystem Resources:"
echo "Memory: $(free -h | grep '^Mem:' | awk '{print $3"/"$2}')"
echo "Disk: $(df -h / | tail -1 | awk '{print $3"/"$2" ("$5" used)"}')"

echo "=== End Health Check ==="
EOF
    chmod +x "$DEPLOY_DIR/monitor.sh"
    
    # Create backup script
    cat > "$DEPLOY_DIR/backup.sh" << 'EOF'
#!/bin/bash
# MedLab Pro Backup Script

BACKUP_DIR="/opt/medlab/backups"
DATE=$(date +%Y%m%d_%H%M%S)
COMPOSE_FILE="/opt/medlab/medlab-pro/docker-compose.prod.yml"

echo "Starting backup process - $DATE"

# Database backup
echo "Backing up database..."
docker-compose -f "$COMPOSE_FILE" exec -T db pg_dump -U medlab_user -d medlab_prod | gzip > "$BACKUP_DIR/db_backup_$DATE.sql.gz"

# Application data backup
echo "Backing up application data..."
tar -czf "$BACKUP_DIR/app_data_$DATE.tar.gz" -C /opt/medlab uploads logs

# Cleanup old backups (keep 30 days)
echo "Cleaning up old backups..."
find "$BACKUP_DIR" -name "*.gz" -mtime +30 -delete

echo "Backup completed - $DATE"
echo "Files created:"
ls -la "$BACKUP_DIR"/*_$DATE.*
EOF
    chmod +x "$DEPLOY_DIR/backup.sh"
    
    # Setup cron jobs
    print_status "Setting up automated monitoring and backups..."
    
    # Health monitoring every 5 minutes
    (crontab -l 2>/dev/null; echo "*/5 * * * * $DEPLOY_DIR/monitor.sh >> $DEPLOY_DIR/logs/monitor.log 2>&1") | crontab -
    
    # Daily backup at 2 AM
    (crontab -l 2>/dev/null; echo "0 2 * * * $DEPLOY_DIR/backup.sh >> $DEPLOY_DIR/logs/backup.log 2>&1") | crontab -
    
    print_success "Monitoring and backup system configured."
}

# Setup firewall
setup_firewall() {
    print_status "Configuring firewall..."
    
    if command -v ufw &> /dev/null; then
        sudo ufw --force reset
        sudo ufw default deny incoming
        sudo ufw default allow outgoing
        sudo ufw allow ssh
        sudo ufw allow 80/tcp    # HTTP
        sudo ufw allow 443/tcp   # HTTPS
        sudo ufw limit ssh       # Rate limit SSH
        sudo ufw --force enable
        
        print_success "Firewall configured with basic security rules."
    else
        print_warning "UFW not available. Please configure firewall manually."
    fi
}

# Print deployment summary
print_summary() {
    echo -e "\n${GREEN}================================================${NC}"
    echo -e "${GREEN} DEPLOYMENT COMPLETED SUCCESSFULLY!${NC}"
    echo -e "${GREEN}================================================${NC}"
    
    echo -e "\n${BLUE}Access Information:${NC}"
    echo -e "• Landing Page: ${YELLOW}http://localhost/${NC}"
    echo -e "• HTTPS (if SSL configured): ${YELLOW}https://localhost/${NC}"
    echo -e "• Login Page: ${YELLOW}http://localhost/login${NC}"
    echo -e "• Health Check: ${YELLOW}http://localhost/health${NC}"
    
    echo -e "\n${BLUE}Demo Credentials:${NC}"
    echo -e "• Username: ${YELLOW}admin${NC}"
    echo -e "• Password: ${YELLOW}admin${NC}"
    echo -e "• Laboratory: ${YELLOW}Demo Lab${NC}"
    
    echo -e "\n${BLUE}Management Commands:${NC}"
    echo -e "• View logs: ${YELLOW}docker-compose -f $COMPOSE_FILE logs -f${NC}"
    echo -e "• Check status: ${YELLOW}docker-compose -f $COMPOSE_FILE ps${NC}"
    echo -e "• Restart services: ${YELLOW}docker-compose -f $COMPOSE_FILE restart${NC}"
    echo -e "• Stop services: ${YELLOW}docker-compose -f $COMPOSE_FILE down${NC}"
    
    echo -e "\n${BLUE}Monitoring:${NC}"
    echo -e "• Health checks: ${YELLOW}$DEPLOY_DIR/logs/monitor.log${NC}"
    echo -e "• Backup logs: ${YELLOW}$DEPLOY_DIR/logs/backup.log${NC}"
    echo -e "• Manual backup: ${YELLOW}$DEPLOY_DIR/backup.sh${NC}"
    
    echo -e "\n${BLUE}Configuration Files:${NC}"
    echo -e "• Environment: ${YELLOW}.env.prod${NC}"
    echo -e "• Docker Compose: ${YELLOW}$COMPOSE_FILE${NC}"
    echo -e "• SSL Certificates: ${YELLOW}./ssl/${NC}"
    
    echo -e "\n${YELLOW}Important Notes:${NC}"
    echo -e "• Replace self-signed SSL certificates with proper ones for production"
    echo -e "• Configure domain name in nginx.prod.conf if using custom domain"
    echo -e "• Regularly monitor logs and perform backups"
    echo -e "• Keep API keys secure and rotate them periodically"
    
    echo -e "\n${GREEN}MedLab Pro is now running in production mode!${NC}"
    echo -e "${GREEN}مدیسیتا اکنون در حالت تولید اجرا می‌شود!${NC}"
}

# Main deployment process
main() {
    print_status "Starting MedLab Pro production deployment..."
    
    # Pre-deployment checks
    check_root
    check_requirements
    
    # Setup system
    create_app_user
    create_directories
    
    # Configure application
    if ! setup_environment; then
        print_error "Please configure .env.prod and run the script again."
        exit 1
    fi
    
    setup_ssl
    
    # Deploy application
    if ! deploy_application; then
        print_error "Deployment failed. Check the logs and try again."
        exit 1
    fi
    
    # Post-deployment setup
    setup_monitoring
    setup_firewall
    
    # Success summary
    print_summary
}

# Handle script arguments
case "${1:-deploy}" in
    "deploy")
        main
        ;;
    "update")
        print_status "Updating MedLab Pro..."
        git pull origin main
        docker-compose -f "$COMPOSE_FILE" pull
        docker-compose -f "$COMPOSE_FILE" up -d --build
        print_success "Update completed."
        ;;
    "backup")
        print_status "Creating manual backup..."
        bash "$DEPLOY_DIR/backup.sh"
        ;;
    "logs")
        docker-compose -f "$COMPOSE_FILE" logs -f "${2:-web}"
        ;;
    "status")
        docker-compose -f "$COMPOSE_FILE" ps
        curl -s -f http://localhost/health | python -m json.tool
        ;;
    "stop")
        print_status "Stopping services..."
        docker-compose -f "$COMPOSE_FILE" down
        print_success "Services stopped."
        ;;
    "restart")
        print_status "Restarting services..."
        docker-compose -f "$COMPOSE_FILE" restart
        print_success "Services restarted."
        ;;
    "help"|"-h"|"--help")
        echo "MedLab Pro Deployment Script"
        echo "Usage: $0 [command]"
        echo ""
        echo "Commands:"
        echo "  deploy  - Full production deployment (default)"
        echo "  update  - Update application to latest version"
        echo "  backup  - Create manual backup"
        echo "  logs    - Show application logs"
        echo "  status  - Show service status and health"
        echo "  stop    - Stop all services"
        echo "  restart - Restart all services"
        echo "  help    - Show this help message"
        ;;
    *)
        print_error "Unknown command: $1"
        print_status "Run '$0 help' for available commands."
        exit 1
        ;;
esac