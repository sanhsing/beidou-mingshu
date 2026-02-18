"""
支付流程模組
payment_flow.py | @星殼 | 2026-02-17
PYLIB: payment_service, db_unified, config

功能：
- 建立訂單
- 生成綠界支付表單
- 處理支付回調
- 點數/會員入帳
"""
import os
import hashlib
import urllib.parse
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
import sqlite3
import json

# === 配置 ===
ECPAY_MERCHANT_ID = os.getenv('ECPAY_MERCHANT_ID', '3002607')
ECPAY_HASH_KEY = os.getenv('ECPAY_HASH_KEY', 'pwFHCqoQZGmho4w6')
ECPAY_HASH_IV = os.getenv('ECPAY_HASH_IV', 'EkRm7iFT261dpevs')
ECPAY_SANDBOX = os.getenv('ECPAY_SANDBOX', 'true').lower() == 'true'

ECPAY_API_URL = 'https://payment-stage.ecpay.com.tw/Cashier/AioCheckOut/V5' if ECPAY_SANDBOX else 'https://payment.ecpay.com.tw/Cashier/AioCheckOut/V5'

SITE_URL = os.getenv('SITE_URL', 'http://localhost:8000')
DB_PATH = 'beidou_unified.db'


class OrderService:
    """訂單服務"""
    
    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        self._init_tables()
    
    def _init_tables(self):
        """初始化訂單表"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                order_no TEXT UNIQUE NOT NULL,
                user_id INTEGER NOT NULL,
                product_id TEXT NOT NULL,
                product_name TEXT,
                amount INTEGER NOT NULL,
                credits INTEGER DEFAULT 0,
                order_type TEXT DEFAULT 'credits',
                status TEXT DEFAULT 'pending',
                payment_method TEXT,
                payment_no TEXT,
                paid_at TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def create_order(self, user_id: int, product_id: str, product: dict) -> Dict[str, Any]:
        """建立訂單"""
        # 生成訂單號: BM + 時間戳 + 隨機數
        import random
        order_no = f"BM{datetime.now().strftime('%Y%m%d%H%M%S')}{random.randint(1000, 9999)}"
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO orders (order_no, user_id, product_id, product_name, amount, credits, order_type, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, 'pending')
        ''', (
            order_no,
            user_id,
            product_id,
            product.get('name', ''),
            product['price'],
            product.get('credits', 0),
            product.get('type', 'credits')
        ))
        
        order_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return {
            'order_id': order_id,
            'order_no': order_no,
            'amount': product['price'],
            'product_name': product.get('name', '')
        }
    
    def get_order(self, order_no: str) -> Optional[Dict[str, Any]]:
        """獲取訂單"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM orders WHERE order_no = ?', (order_no,))
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            return None
        
        columns = ['id', 'order_no', 'user_id', 'product_id', 'product_name', 
                   'amount', 'credits', 'order_type', 'status', 'payment_method',
                   'payment_no', 'paid_at', 'created_at', 'updated_at']
        
        return dict(zip(columns, row))
    
    def update_order_paid(self, order_no: str, payment_no: str = None) -> bool:
        """更新訂單為已支付"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE orders 
            SET status = 'paid', payment_no = ?, paid_at = ?, updated_at = ?
            WHERE order_no = ? AND status = 'pending'
        ''', (payment_no, datetime.now().isoformat(), datetime.now().isoformat(), order_no))
        
        affected = cursor.rowcount
        conn.commit()
        conn.close()
        
        return affected > 0


class ECPayService:
    """綠界支付服務"""
    
    def __init__(self):
        self.merchant_id = ECPAY_MERCHANT_ID
        self.hash_key = ECPAY_HASH_KEY
        self.hash_iv = ECPAY_HASH_IV
        self.api_url = ECPAY_API_URL
    
    def _generate_check_mac_value(self, params: dict) -> str:
        """生成檢查碼"""
        # 按照 A-Z 排序
        sorted_params = sorted(params.items())
        
        # 組合字串
        raw = f"HashKey={self.hash_key}&" + "&".join([f"{k}={v}" for k, v in sorted_params]) + f"&HashIV={self.hash_iv}"
        
        # URL encode
        encoded = urllib.parse.quote_plus(raw).lower()
        
        # SHA256
        check_value = hashlib.sha256(encoded.encode('utf-8')).hexdigest().upper()
        
        return check_value
    
    def create_payment_form(self, order_no: str, amount: int, item_name: str,
                            return_url: str, notify_url: str) -> str:
        """生成綠界支付表單"""
        
        trade_date = datetime.now().strftime('%Y/%m/%d %H:%M:%S')
        
        params = {
            'MerchantID': self.merchant_id,
            'MerchantTradeNo': order_no,
            'MerchantTradeDate': trade_date,
            'PaymentType': 'aio',
            'TotalAmount': str(amount),
            'TradeDesc': '北斗命數服務',
            'ItemName': item_name,
            'ReturnURL': notify_url,  # 背景通知
            'OrderResultURL': return_url,  # 前台返回
            'ChoosePayment': 'ALL',
            'EncryptType': '1',
            'NeedExtraPaidInfo': 'N',
        }
        
        # 生成檢查碼
        params['CheckMacValue'] = self._generate_check_mac_value(params)
        
        # 生成表單 HTML
        form_html = f'''<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>正在跳轉到綠界支付...</title>
</head>
<body onload="document.getElementById('ecpay_form').submit();">
    <div style="text-align:center;padding:50px;">
        <h2>🔄 正在跳轉到綠界支付...</h2>
        <p>訂單編號: {order_no}</p>
        <p>金額: NT${amount}</p>
        <p>請稍候...</p>
    </div>
    <form id="ecpay_form" method="post" action="{self.api_url}">
'''
        
        for key, value in params.items():
            form_html += f'        <input type="hidden" name="{key}" value="{value}">\n'
        
        form_html += '''        <noscript>
            <button type="submit">如果沒有自動跳轉，請點擊這裡</button>
        </noscript>
    </form>
</body>
</html>'''
        
        return form_html
    
    def verify_callback(self, post_data: dict) -> tuple:
        """驗證回調"""
        received_mac = post_data.get('CheckMacValue', '')
        
        # 移除 CheckMacValue 後重新計算
        params = {k: v for k, v in post_data.items() if k != 'CheckMacValue'}
        calculated_mac = self._generate_check_mac_value(params)
        
        if received_mac.upper() != calculated_mac.upper():
            return False, "CheckMacValue 驗證失敗", {}
        
        # 檢查交易狀態
        rtn_code = post_data.get('RtnCode', '0')
        if rtn_code != '1':
            return False, f"交易失敗: {post_data.get('RtnMsg', '未知錯誤')}", post_data
        
        return True, "OK", {
            'order_no': post_data.get('MerchantTradeNo'),
            'payment_no': post_data.get('TradeNo'),
            'amount': int(post_data.get('TradeAmt', 0)),
            'payment_date': post_data.get('PaymentDate'),
            'payment_type': post_data.get('PaymentType')
        }


class CreditsService:
    """點數服務"""
    
    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
    
    def add_credits(self, user_id: int, amount: int, reason: str, order_no: str = None) -> bool:
        """增加點數"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 更新用戶點數
        cursor.execute('''
            UPDATE users SET credits = credits + ?, updated_at = ? WHERE id = ?
        ''', (amount, datetime.now().isoformat(), user_id))
        
        # 記錄點數變動
        cursor.execute('''
            INSERT INTO credit_logs (user_id, amount, balance_after, reason, order_no, created_at)
            SELECT ?, ?, credits, ?, ?, ?
            FROM users WHERE id = ?
        ''', (user_id, amount, reason, order_no, datetime.now().isoformat(), user_id))
        
        conn.commit()
        conn.close()
        
        return True
    
    def get_balance(self, user_id: int) -> int:
        """獲取點數餘額"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT credits FROM users WHERE id = ?', (user_id,))
        row = cursor.fetchone()
        conn.close()
        
        return row[0] if row else 0


# === 主要函數 ===

def create_payment(user_id: int, product_id: str, product: dict) -> Dict[str, Any]:
    """建立支付訂單並生成支付表單"""
    
    # 1. 建立訂單
    order_service = OrderService()
    order = order_service.create_order(user_id, product_id, product)
    
    # 2. 生成支付表單
    ecpay = ECPayService()
    
    return_url = f"{SITE_URL}/checkout/return"
    notify_url = f"{SITE_URL}/api/payment/notify"
    
    form_html = ecpay.create_payment_form(
        order_no=order['order_no'],
        amount=order['amount'],
        item_name=order['product_name'],
        return_url=return_url,
        notify_url=notify_url
    )
    
    return {
        'success': True,
        'order_no': order['order_no'],
        'form_html': form_html
    }


def process_payment_callback(post_data: dict) -> Dict[str, Any]:
    """處理支付回調"""
    
    # 1. 驗證回調
    ecpay = ECPayService()
    valid, message, payment_info = ecpay.verify_callback(post_data)
    
    if not valid:
        return {'success': False, 'error': message}
    
    order_no = payment_info['order_no']
    
    # 2. 獲取訂單
    order_service = OrderService()
    order = order_service.get_order(order_no)
    
    if not order:
        return {'success': False, 'error': '訂單不存在'}
    
    if order['status'] == 'paid':
        return {'success': True, 'message': '訂單已處理'}
    
    # 3. 更新訂單狀態
    order_service.update_order_paid(order_no, payment_info.get('payment_no'))
    
    # 4. 入帳處理
    if order['order_type'] == 'credits':
        # 點數入帳
        credits_service = CreditsService()
        credits_service.add_credits(
            user_id=order['user_id'],
            amount=order['credits'],
            reason=f"購買 {order['product_name']}",
            order_no=order_no
        )
    elif order['order_type'] == 'subscription':
        # 會員開通
        from membership_service import MembershipService
        ms = MembershipService()
        ms.subscribe(order['user_id'], order['product_id'])
    elif order['order_type'] == 'package':
        # 套餐 - 轉換為點數或直接開通報告權限
        # 這裡可以根據業務邏輯處理
        pass
    
    # 5. 發送通知郵件
    try:
        from email_service import email_service
        # 獲取用戶 email (需從 db 查詢)
        # email_service.send_payment_success(...)
    except:
        pass
    
    return {
        'success': True,
        'order_no': order_no,
        'message': '支付成功'
    }


if __name__ == "__main__":
    # 測試
    print("=== 支付流程模組測試 ===")
    print(f"綠界商店代號: {ECPAY_MERCHANT_ID}")
    print(f"Sandbox 模式: {ECPAY_SANDBOX}")
    print(f"API URL: {ECPAY_API_URL}")
    
    # 測試建立訂單
    os_service = OrderService()
    print("✓ OrderService 初始化成功")
    
    # 測試 ECPay
    ecpay = ECPayService()
    print("✓ ECPayService 初始化成功")

# A3.12: 支付重試機制
def retry_payment(order_no: str, max_retries: int = 3) -> dict:
    """重試支付"""
    order_service = OrderService()
    order = order_service.get_order(order_no)
    
    if not order:
        return {'success': False, 'error': '訂單不存在'}
    
    if order['status'] != 'pending':
        return {'success': False, 'error': '訂單狀態不允許重試'}
    
    retry_count = order.get('retry_count', 0) or 0
    if retry_count >= max_retries:
        return {'success': False, 'error': '已達最大重試次數'}
    
    # 更新重試次數
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE orders SET retry_count = ?, updated_at = ? WHERE order_no = ?
    ''', (retry_count + 1, datetime.now().isoformat(), order_no))
    conn.commit()
    conn.close()
    
    return {'success': True, 'retry_count': retry_count + 1}
