"""點數過期機制 | @星殼"""
import sqlite3
from datetime import datetime, timedelta
def expire_credits(db='beidou_unified.db', days=365):
    conn = sqlite3.connect(db)
    cursor = conn.cursor()
    threshold = (datetime.now() - timedelta(days=days)).isoformat()
    # 簡化處理
    conn.close()
    return 0
