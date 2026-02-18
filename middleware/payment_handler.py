"""支付異常處理 | @星殼"""
import sqlite3
from datetime import datetime, timedelta

DB_PATH = 'beidou_unified.db'

class PaymentException(Exception):
    def __init__(self, code: str, message: str, order_no: str = None):
        self.code = code
        self.message = message
        self.order_no = order_no

def handle_payment_error(order_no: str, error_code: str, error_msg: str):
    """記錄支付錯誤"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        UPDATE orders SET 
            status = 'error',
            payment_error = ?,
            updated_at = ?
        WHERE order_no = ?
    ''', (f"{error_code}: {error_msg}", datetime.now().isoformat(), order_no))
    
    conn.commit()
    conn.close()

def retry_payment(order_no: str, max_retries: int = 3) -> bool:
    """重試支付 (P4.9 的一部分)"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('SELECT retry_count FROM orders WHERE order_no = ?', (order_no,))
    row = cursor.fetchone()
    
    if not row:
        return False
    
    retry_count = row[0] or 0
    if retry_count >= max_retries:
        return False
    
    cursor.execute('''
        UPDATE orders SET retry_count = ?, updated_at = ? WHERE order_no = ?
    ''', (retry_count + 1, datetime.now().isoformat(), order_no))
    
    conn.commit()
    conn.close()
    return True
