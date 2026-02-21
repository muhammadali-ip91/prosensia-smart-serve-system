#!/bin/bash

# ================================================
# ProSensia Smart-Serve — Database Backup
# ================================================
# Creates a timestamped backup of the PostgreSQL database.
# Usage: ./scripts/backup_db.sh
# ================================================

set -e

echo "╔══════════════════════════════════════════════╗"
echo "║   ProSensia — Database Backup                ║"
echo "╚══════════════════════════════════════════════╝"
echo ""

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

# Load environment
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | xargs) 2>/dev/null
fi

# Default values
DB_HOST="${DB_HOST:-localhost}"
DB_PORT="${DB_PORT:-5432}"
DB_NAME="${POSTGRES_DB:-prosensia}"
DB_USER="${POSTGRES_USER:-prosensia_user}"

# Backup directory
BACKUP_DIR="$PROJECT_ROOT/backups"
mkdir -p "$BACKUP_DIR"

# Timestamp
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/prosensia_backup_${TIMESTAMP}.sql"

echo "Database: $DB_NAME"
echo "Host:     $DB_HOST:$DB_PORT"
echo "User:     $DB_USER"
echo "Output:   $BACKUP_FILE"
echo ""

# Check if using Docker
if docker ps --format '{{.Names}}' | grep -q "prosensia-db\|prosensia_db\|db"; then
    echo "Backing up from Docker container..."
    CONTAINER_NAME=$(docker ps --format '{{.Names}}' | grep -E "prosensia.*db|db" | head -1)
    
    docker exec "$CONTAINER_NAME" \
        pg_dump -U "$DB_USER" "$DB_NAME" > "$BACKUP_FILE"
else
    echo "Backing up from local PostgreSQL..."
    PGPASSWORD="$POSTGRES_PASSWORD" pg_dump \
        -h "$DB_HOST" \
        -p "$DB_PORT" \
        -U "$DB_USER" \
        "$DB_NAME" > "$BACKUP_FILE"
fi

# Check if backup was created
if [ -f "$BACKUP_FILE" ] && [ -s "$BACKUP_FILE" ]; then
    BACKUP_SIZE=$(du -h "$BACKUP_FILE" | cut -f1)
    echo ""
    echo "[✓] Backup created successfully!"
    echo "    File: $BACKUP_FILE"
    echo "    Size: $BACKUP_SIZE"
else
    echo ""
    echo "[✗] Backup failed or file is empty!"
    exit 1
fi

# Keep only last 7 backups
echo ""
echo "Cleaning old backups (keeping last 7)..."
ls -t "$BACKUP_DIR"/prosensia_backup_*.sql 2>/dev/null | \
    tail -n +8 | xargs rm -f 2>/dev/null
echo "[✓] Cleanup complete"

# List existing backups
echo ""
echo "Available backups:"
ls -lh "$BACKUP_DIR"/prosensia_backup_*.sql 2>/dev/null | \
    awk '{print "  " $NF " (" $5 ")"}'