"""會員到期提醒 | @流祇"""
import sqlite3
from datetime import datetime, timedelta
def get_expiring_members(db='beidou_unified.db', days=7):
    conn = sqlite3.connect(db)
    cursor = conn.cursor()
    threshold = (datetime.now() + timedelta(days=days)).isoformat()
    cursor.execute("SELECT user_id, email FROM memberships WHERE status='active' AND end_date<?", (threshold,))
    members = cursor.fetchall()
    conn.close()
    return members
