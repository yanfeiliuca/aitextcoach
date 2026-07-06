#!/bin/bash
# AITextCoach Database Backup Script
# Run this periodically to export all user data

# Usage: ./backup_db.sh
# Output: backup/aitextcoach_YYYY-MM-DD.json

DB_URL="${DATABASE_URL:-}"
BACKUP_DIR="./backup"
TIMESTAMP=$(date +%Y-%m-%d_%H-%M-%S)
BACKUP_FILE="$BACKUP_DIR/aitextcoach_${TIMESTAMP}.json"

if [ -z "$DB_URL" ]; then
    echo "Error: DATABASE_URL not set"
    exit 1
fi

mkdir -p "$BACKUP_DIR"

echo "Backing up AITextCoach database..."

# Export users table
python3 << PYTHON
import json, psycopg2, os, sys
from urllib.parse import urlparse

url = os.environ.get('DATABASE_URL')
if not url:
    print("DATABASE_URL not set")
    sys.exit(1)

try:
    conn = psycopg2.connect(url, sslmode='require')
    with conn.cursor() as cur:
        # Export users
        cur.execute("SELECT email, is_pro, subscription_id, created_at FROM users")
        users = []
        for row in cur.fetchall():
            users.append({
                'email': row[0],
                'is_pro': row[1],
                'subscription_id': row[2],
                'created_at': str(row[3])
            })
        
        # Export usage stats
        cur.execute("SELECT email, chars_used, usage_date FROM usage_stats")
        usage = []
        for row in cur.fetchall():
            usage.append({
                'email': row[0],
                'chars_used': row[1],
                'usage_date': str(row[2])
            })
        
        # Export click stats
        cur.execute("SELECT button_type, click_date, count FROM click_stats")
        clicks = []
        for row in cur.fetchall():
            clicks.append({
                'button': row[0],
                'date': str(row[1]),
                'count': row[2]
            })
        
        backup = {
            'exported_at': '$TIMESTAMP',
            'users': users,
            'usage_stats': usage,
            'click_stats': clicks
        }
        
        with open('$BACKUP_FILE', 'w') as f:
            json.dump(backup, f, indent=2)
        
        print(f"Backup saved: {len(users)} users, {len(usage)} usage records, {len(clicks)} click records")
    conn.close()
except Exception as e:
    print(f"Backup failed: {e}")
    sys.exit(1)
PYTHON

echo "Done: $BACKUP_FILE"
