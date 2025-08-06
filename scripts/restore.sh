#!/bin/bash
# Database restore script for MedLab Pro

set -e

# Configuration
DB_HOST="${POSTGRES_HOST:-db}"
DB_NAME="${POSTGRES_DB:-medlabpro}"
DB_USER="${POSTGRES_USER:-medlab}"
BACKUP_DIR="/backups"

# Check if backup file is provided
if [ -z "$1" ]; then
    echo "Usage: $0 <backup_file>"
    echo "Available backups:"
    ls -lah "${BACKUP_DIR}"/medlabpro_backup_*.sql.gz 2>/dev/null || echo "No backups found"
    exit 1
fi

BACKUP_FILE="$1"

# Check if backup file exists
if [ ! -f "${BACKUP_FILE}" ]; then
    echo "ERROR: Backup file not found: ${BACKUP_FILE}"
    exit 1
fi

# Confirm restore operation
echo "WARNING: This will replace all data in database '${DB_NAME}'"
echo "Backup file: ${BACKUP_FILE}"
echo "Database: ${DB_USER}@${DB_HOST}/${DB_NAME}"
read -p "Are you sure you want to continue? (yes/no): " -r
if [[ ! $REPLY =~ ^[Yy][Ee][Ss]$ ]]; then
    echo "Restore cancelled"
    exit 0
fi

# Drop existing connections
echo "Terminating existing connections..."
psql -h "${DB_HOST}" -U "${DB_USER}" -d postgres -c "
    SELECT pg_terminate_backend(pid) 
    FROM pg_stat_activity 
    WHERE datname = '${DB_NAME}' AND pid <> pg_backend_pid();
"

# Drop and recreate database
echo "Recreating database..."
psql -h "${DB_HOST}" -U "${DB_USER}" -d postgres -c "DROP DATABASE IF EXISTS ${DB_NAME};"
psql -h "${DB_HOST}" -U "${DB_USER}" -d postgres -c "CREATE DATABASE ${DB_NAME};"

# Restore from backup
echo "Restoring from backup: ${BACKUP_FILE}"
gunzip -c "${BACKUP_FILE}" | psql -h "${DB_HOST}" -U "${DB_USER}" -d "${DB_NAME}" --verbose

echo "Database restore completed successfully"

# Verify restore
echo "Verifying restore..."
TABLES=$(psql -h "${DB_HOST}" -U "${DB_USER}" -d "${DB_NAME}" -t -c "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public';")
echo "Tables restored: ${TABLES}"

if [ "${TABLES}" -gt 0 ]; then
    echo "Restore verification successful"
else
    echo "WARNING: No tables found in restored database"
fi