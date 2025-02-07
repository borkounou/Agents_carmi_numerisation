#!/bin/bash
# Define the backup directory (mounted to /backup in the container)
BACKUP_DIR="/home/carmi/backup"
BACKUP_FILE="$BACKUP_DIR/backup_$(date +\%Y\%m\%d_\%H\%M\%S).dump"

# Run pg_dump inside the container and save the backup to /backup
docker exec archicarmi-db pg_dump -U ${POSTGRES_USER} -d ${POSTGRES_DB} -F c -b -v -f /backup/backup_file.dump

# Rename the backup file with a timestamp
mv /home/carmi/backup/backup_file.dump $BACKUP_FILE

echo "Backup created at $BACKUP_FILE"