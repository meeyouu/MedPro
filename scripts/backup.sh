#!/bin/bash
# Database backup script for MedLab Pro

set -e

# Configuration
DB_HOST="${POSTGRES_HOST:-db}"
DB_NAME="${POSTGRES_DB:-medlabpro}"
DB_USER="${POSTGRES_USER:-medlab}"
BACKUP_DIR="/backups"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_FILE="${BACKUP_DIR}/medlabpro_backup_${TIMESTAMP}.sql.gz"

# Create backup directory if it doesn't exist
mkdir -p "${BACKUP_DIR}"

# Create backup
echo "Creating backup: ${BACKUP_FILE}"
pg_dump -h "${DB_HOST}" -U "${DB_USER}" -d "${DB_NAME}" --verbose | gzip > "${BACKUP_FILE}"

# Verify backup
if [ -f "${BACKUP_FILE}" ] && [ -s "${BACKUP_FILE}" ]; then
    echo "Backup created successfully: ${BACKUP_FILE}"
    echo "Backup size: $(du -h ${BACKUP_FILE} | cut -f1)"
else
    echo "ERROR: Backup failed or file is empty"
    exit 1
fi

# Clean up old backups (keep last 7 days)
echo "Cleaning up old backups..."
find "${BACKUP_DIR}" -name "medlabpro_backup_*.sql.gz" -mtime +7 -delete
echo "Backup cleanup completed"

# List remaining backups
echo "Available backups:"
ls -lah "${BACKUP_DIR}"/medlabpro_backup_*.sql.gz 2>/dev/null || echo "No backups found"