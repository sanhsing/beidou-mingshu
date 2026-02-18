"""支付超時自動取消 | @星殼"""
import sqlite3
from datetime import datetime, timedelta
def cancel_timeout_orders(db='beidou_unified.db', minutes=30):
    conn = sqlite3.connect(db)
    cursor = conn.cursor()
    threshold = (datetime.now() - timedelta(minutes=minutes)).isoformat()
    cursor.execute("UPDATE orders SET status='cancelled', cancel_reason='timeout' WHERE status='pending' AND created_at<?", (threshold,))
    cancelled = cursor.rowcount
    conn.commit()
    conn.close()
    return cancelled
