#!/usr/bin/env python3
import sqlite3
import shutil
import os
import datetime
import sys

PROJECT_DIR = "/home/rsalars/Projects/dreamweaving"
DB_FILE = os.path.join(PROJECT_DIR, "data", "automation_state.db")
BACKUP_DIR = os.path.join(PROJECT_DIR, "data", "backups")
LOG_FILE = os.path.join(PROJECT_DIR, "data", "logs", "automation", "backup.log")

def log(message):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a") as f:
        f.write(f"[{timestamp}] {message}\n")
    print(message)

def backup():
    if not os.path.exists(BACKUP_DIR):
        os.makedirs(BACKUP_DIR)
    
    if not os.path.dirname(LOG_FILE):
        os.makedirs(os.path.dirname(LOG_FILE))

    if not os.path.exists(DB_FILE):
        log(f"ERROR: Database file not found at {DB_FILE}")
        sys.exit(1)

    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = os.path.join(BACKUP_DIR, f"automation_state_{timestamp}.db")

    try:
        # Use SQLite API to backup safely
        src = sqlite3.connect(DB_FILE)
        dst = sqlite3.connect(backup_file)
        with dst:
            src.backup(dst)
        dst.close()
        src.close()
        log(f"Backup successful: {backup_file}")
        
        # Cleanup old backups (keep last 30 days)
        now = datetime.datetime.now()
        cleanup_count = 0
        for filename in os.listdir(BACKUP_DIR):
            if filename.startswith("automation_state_") and filename.endswith(".db"):
                file_path = os.path.join(BACKUP_DIR, filename)
                file_mtime = datetime.datetime.fromtimestamp(os.path.getmtime(file_path))
                if (now - file_mtime).days > 30:
                    os.remove(file_path)
                    cleanup_count += 1
        
        if cleanup_count > 0:
            log(f"Cleaned up {cleanup_count} old backups")
            
    except Exception as e:
        log(f"ERROR: Backup failed - {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    backup()
