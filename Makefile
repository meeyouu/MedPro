# MedLab Pro - Medical Laboratory Management System
# Makefile for development and production operations

# Variables
COMPOSE_FILE_DEV = docker-compose.yml
COMPOSE_FILE_PROD = docker-compose.prod.yml
PROJECT_NAME = medlab-pro
BACKUP_DIR = ./backups
LOG_DIR = ./logs

# Colors for output
GREEN = \033[0;32m
YELLOW = \033[1;33m
RED = \033[0;31m
NC = \033[0m # No Color

.PHONY: help dev prod build clean logs backup restore test lint health monitor

# Default target
all: help

help: ## Show this help message
	@echo "$(GREEN)MedLab Pro - Medical Laboratory Management System$(NC)"
	@echo "$(YELLOW)Available commands:$(NC)"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(GREEN)%-15s$(NC) %s\n", $$1, $$2}'

# Development Commands
dev: ## Start development environment
	@echo "$(GREEN)Starting development environment...$(NC)"
	docker-compose -f $(COMPOSE_FILE_DEV) up -d
	@echo "$(GREEN)Development server running at http://localhost:5000$(NC)"

dev-build: ## Build and start development environment
	@echo "$(GREEN)Building and starting development environment...$(NC)"
	docker-compose -f $(COMPOSE_FILE_DEV) up --build -d

dev-stop: ## Stop development environment
	@echo "$(YELLOW)Stopping development environment...$(NC)"
	docker-compose -f $(COMPOSE_FILE_DEV) down

dev-logs: ## Show development logs
	docker-compose -f $(COMPOSE_FILE_DEV) logs -f

# Production Commands
prod: ## Start production environment
	@echo "$(GREEN)Starting production environment...$(NC)"
	@if [ ! -f .env.prod ]; then \
		echo "$(RED)Error: .env.prod file not found. Copy .env.example to .env.prod and configure.$(NC)"; \
		exit 1; \
	fi
	docker-compose -f $(COMPOSE_FILE_PROD) up -d
	@echo "$(GREEN)Production server running$(NC)"

prod-build: ## Build and start production environment
	@echo "$(GREEN)Building and starting production environment...$(NC)"
	docker-compose -f $(COMPOSE_FILE_PROD) up --build -d

prod-stop: ## Stop production environment
	@echo "$(YELLOW)Stopping production environment...$(NC)"
	docker-compose -f $(COMPOSE_FILE_PROD) down

prod-restart: ## Restart production environment
	@echo "$(YELLOW)Restarting production environment...$(NC)"
	docker-compose -f $(COMPOSE_FILE_PROD) restart

# Build Commands
build: ## Build application images
	@echo "$(GREEN)Building application images...$(NC)"
	docker build -t $(PROJECT_NAME):latest .

clean: ## Clean up Docker resources
	@echo "$(YELLOW)Cleaning up Docker resources...$(NC)"
	docker-compose -f $(COMPOSE_FILE_DEV) down -v --remove-orphans
	docker-compose -f $(COMPOSE_FILE_PROD) down -v --remove-orphans
	docker system prune -f
	@echo "$(GREEN)Cleanup completed$(NC)"

# Logging and Monitoring
logs: ## Show production logs
	docker-compose -f $(COMPOSE_FILE_PROD) logs -f

logs-web: ## Show web application logs only
	docker-compose -f $(COMPOSE_FILE_PROD) logs -f web

logs-db: ## Show database logs only
	docker-compose -f $(COMPOSE_FILE_PROD) logs -f db

logs-nginx: ## Show nginx logs only
	docker-compose -f $(COMPOSE_FILE_PROD) logs -f nginx

health: ## Check application health
	@echo "$(GREEN)Checking application health...$(NC)"
	@curl -s -f http://localhost/health | python -m json.tool || echo "$(RED)Health check failed$(NC)"

status: ## Show service status
	@echo "$(GREEN)Service Status:$(NC)"
	docker-compose -f $(COMPOSE_FILE_PROD) ps

# Database Operations
db-backup: ## Create database backup
	@echo "$(GREEN)Creating database backup...$(NC)"
	@mkdir -p $(BACKUP_DIR)
	@TIMESTAMP=$$(date +"%Y%m%d_%H%M%S"); \
	docker-compose -f $(COMPOSE_FILE_PROD) exec -T db pg_dump -U medlab_user -d medlab_prod | gzip > $(BACKUP_DIR)/medlab_backup_$$TIMESTAMP.sql.gz
	@echo "$(GREEN)Backup created in $(BACKUP_DIR)$(NC)"

db-restore: ## Restore database from backup (usage: make db-restore BACKUP=filename.sql.gz)
	@if [ -z "$(BACKUP)" ]; then \
		echo "$(RED)Error: Specify backup file with BACKUP=filename.sql.gz$(NC)"; \
		exit 1; \
	fi
	@echo "$(YELLOW)Restoring database from $(BACKUP)...$(NC)"
	@gunzip -c $(BACKUP_DIR)/$(BACKUP) | docker-compose -f $(COMPOSE_FILE_PROD) exec -T db psql -U medlab_user -d medlab_prod
	@echo "$(GREEN)Database restored$(NC)"

db-connect: ## Connect to production database
	docker-compose -f $(COMPOSE_FILE_PROD) exec db psql -U medlab_user -d medlab_prod

db-migrations: ## Run database migrations
	@echo "$(GREEN)Running database migrations...$(NC)"
	docker-compose -f $(COMPOSE_FILE_PROD) exec web python -c "from app import app, db; app.app_context().push(); db.create_all()"

# Security and Maintenance
ssl-generate: ## Generate self-signed SSL certificate
	@echo "$(GREEN)Generating self-signed SSL certificate...$(NC)"
	@mkdir -p ./ssl
	openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
		-keyout ./ssl/medlab.key \
		-out ./ssl/medlab.crt \
		-subj "/C=US/ST=State/L=City/O=MedLab Pro/CN=localhost"
	@echo "$(GREEN)SSL certificate generated in ./ssl/$(NC)"

security-scan: ## Run basic security scan
	@echo "$(GREEN)Running security scan...$(NC)"
	@echo "Checking for common security issues..."
	@grep -r "SECRET_KEY.*=" . --exclude-dir=.git || echo "No hardcoded secrets found"
	@echo "Checking file permissions..."
	@find . -name "*.py" -perm /o+w -exec echo "Warning: {} is world-writable" \;

update: ## Update application to latest version
	@echo "$(GREEN)Updating application...$(NC)"
	git pull origin main
	docker-compose -f $(COMPOSE_FILE_PROD) pull
	docker-compose -f $(COMPOSE_FILE_PROD) up -d --build

# Testing Commands
test: ## Run application tests
	@echo "$(GREEN)Running tests...$(NC)"
	docker-compose -f $(COMPOSE_FILE_DEV) exec web python -m pytest tests/

test-ai: ## Test AI integration
	@echo "$(GREEN)Testing AI integration...$(NC)"
	docker-compose -f $(COMPOSE_FILE_DEV) exec web python test_ai_report_generation.py

test-workflow: ## Test complete workflow
	@echo "$(GREEN)Testing complete workflow...$(NC)"
	docker-compose -f $(COMPOSE_FILE_DEV) exec web python test_workflow_integration.py

lint: ## Run code linting
	@echo "$(GREEN)Running code linting...$(NC)"
	docker-compose -f $(COMPOSE_FILE_DEV) exec web flake8 *.py
	docker-compose -f $(COMPOSE_FILE_DEV) exec web pylint *.py

# Monitoring and Performance
monitor: ## Start monitoring dashboard
	@echo "$(GREEN)Starting monitoring dashboard...$(NC)"
	docker-compose -f $(COMPOSE_FILE_PROD) --profile monitoring up -d monitoring
	@echo "$(GREEN)Prometheus available at http://localhost:9090$(NC)"

performance: ## Show performance metrics
	@echo "$(GREEN)Performance Metrics:$(NC)"
	@echo "Docker container stats:"
	docker stats --no-stream
	@echo "\nDisk usage:"
	df -h
	@echo "\nMemory usage:"
	free -h

# Data Management
export-data: ## Export patient data
	@echo "$(GREEN)Exporting patient data...$(NC)"
	@mkdir -p ./exports
	docker-compose -f $(COMPOSE_FILE_PROD) exec web python -c "
from routes import export_all_patients_data
from app import app
with app.app_context():
    export_all_patients_data()
"

import-data: ## Import patient data (usage: make import-data FILE=data.xlsx)
	@if [ -z "$(FILE)" ]; then \
		echo "$(RED)Error: Specify data file with FILE=data.xlsx$(NC)"; \
		exit 1; \
	fi
	@echo "$(GREEN)Importing patient data from $(FILE)...$(NC)"
	docker-compose -f $(COMPOSE_FILE_PROD) exec -T web python scripts/import_patients.py < $(FILE)

# Installation and Setup
install: ## Install production environment
	@echo "$(GREEN)Installing MedLab Pro production environment...$(NC)"
	@echo "Creating directories..."
	@sudo mkdir -p /opt/medlab/{data/postgres,data/redis,logs,uploads,ssl,backups}
	@echo "Setting permissions..."
	@sudo chown -R $$USER:$$USER /opt/medlab
	@echo "Copying configuration files..."
	@cp docker-compose.prod.yml /opt/medlab/
	@cp nginx.prod.conf /opt/medlab/
	@cp postgresql.conf /opt/medlab/
	@cp redis.conf /opt/medlab/
	@echo "$(GREEN)Installation completed. Configure .env.prod and run 'make prod'$(NC)"

uninstall: ## Remove production environment
	@echo "$(YELLOW)Removing MedLab Pro production environment...$(NC)"
	@read -p "This will remove all data. Continue? [y/N] " confirm && [ "$$confirm" = "y" ]
	docker-compose -f $(COMPOSE_FILE_PROD) down -v
	docker rmi $(PROJECT_NAME):latest
	@sudo rm -rf /opt/medlab
	@echo "$(GREEN)Uninstallation completed$(NC)"

# Development Utilities
shell: ## Access web container shell
	docker-compose -f $(COMPOSE_FILE_PROD) exec web /bin/bash

shell-db: ## Access database container shell
	docker-compose -f $(COMPOSE_FILE_PROD) exec db /bin/bash

reset-dev: ## Reset development environment
	@echo "$(YELLOW)Resetting development environment...$(NC)"
	docker-compose -f $(COMPOSE_FILE_DEV) down -v
	docker-compose -f $(COMPOSE_FILE_DEV) up --build -d
	@echo "$(GREEN)Development environment reset$(NC)"

# Quick Commands
quick-start: ## Quick start for development
	@echo "$(GREEN)Quick starting MedLab Pro...$(NC)"
	@if [ ! -f .env ]; then cp .env.example .env; echo "$(YELLOW)Created .env from template. Please configure API keys.$(NC)"; fi
	make dev-build
	@echo "$(GREEN)MedLab Pro is running at http://localhost:5000$(NC)"
	@echo "$(YELLOW)Demo login: admin/admin/Demo Lab$(NC)"

quick-prod: ## Quick start for production
	@echo "$(GREEN)Quick starting production environment...$(NC)"
	@if [ ! -f .env.prod ]; then echo "$(RED)Create .env.prod first$(NC)"; exit 1; fi
	make ssl-generate
	make prod-build
	make health

# Documentation
docs: ## Generate documentation
	@echo "$(GREEN)Generating documentation...$(NC)"
	@echo "Available documentation:"
	@ls -la *.md
	@echo "\nProject structure:"
	@tree -I '__pycache__|*.pyc|.git|.env*' -L 2

# Version and Info
version: ## Show version information
	@echo "$(GREEN)MedLab Pro - Medical Laboratory Management System$(NC)"
	@echo "Version: 1.3.0"
	@echo "Build: Production-ready Docker deployment"
	@echo "Features: AI-powered reports, Multilingual support, SaaS landing page"
	@echo "$(YELLOW)For more information, see README.md$(NC)"

info: ## Show system information
	@echo "$(GREEN)System Information:$(NC)"
	@echo "OS: $$(uname -s -r)"
	@echo "Docker: $$(docker --version)"
	@echo "Docker Compose: $$(docker-compose --version)"
	@echo "Python: $$(python3 --version)"
	@echo "Available disk space:"
	@df -h .
	@echo "Available memory:"
	@free -h | head -2