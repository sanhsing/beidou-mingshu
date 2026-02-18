"""
點數API + 支付回調路由
credits_api.py | @星殼 | 2026-02-17
PYLIB: payment_flow, db_unified, auth_jwt

功能：
- 點數餘額查詢
- 點數使用記錄
- 支付回調處理
- 支付結果頁
"""
from fastapi import APIRouter, Request, Depends, HTTPException, Form
from fastapi.responses import HTMLResponse, PlainTextResponse
from typing import Optional
import sqlite3
from datetime import datetime

router = APIRouter(tags=["credits"])

DB_PATH = 'beidou_unified.db'

# === 初始化點數相關表 ===
def init_credit_tables():
    """初始化點數表 (安全版本)"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # 檢查 users 表是否存在
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
        if cursor.fetchone():
            # users 表存在，檢查是否有 credits 欄位
            cursor.execute("PRAGMA table_info(users)")
            columns = [row[1] for row in cursor.fetchall()]
            if 'credits' not in columns:
                cursor.execute('ALTER TABLE users ADD COLUMN credits INTEGER DEFAULT 0')
                print("[Credits] 已添加 credits 欄位到 users 表")
    except Exception as e:
        print(f"[Credits] users 表處理: {e}")
    
    # 點數記錄表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS credit_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            amount INTEGER NOT NULL,
            balance_after INTEGER,
            reason TEXT,
            order_no TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()
    print("[Credits] 點數表初始化完成")

# 延遲初始化 (只在實際使用時)
_initialized = False

def ensure_init():
    global _initialized
    if not _initialized:
        init_credit_tables()
        _initialized = True


# === API 路由 ===

@router.get("/api/user/credits")
async def get_user_credits(request: Request):
    """獲取用戶點數餘額"""
    ensure_init()
    
    # TODO: 從 JWT 獲取 user_id
    user_id = 1  # 暫時硬編碼
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        cursor.execute('SELECT credits FROM users WHERE id = ?', (user_id,))
        row = cursor.fetchone()
        credits = row[0] if row else 0
    except:
        credits = 0
    
    # 最近記錄
    try:
        cursor.execute('''
            SELECT amount, reason, created_at FROM credit_logs 
            WHERE user_id = ? ORDER BY created_at DESC LIMIT 10
        ''', (user_id,))
        logs = [{'amount': r[0], 'reason': r[1], 'date': r[2]} for r in cursor.fetchall()]
    except:
        logs = []
    
    conn.close()
    
    return {
        'credits': credits,
        'recent_logs': logs
    }


@router.post("/api/user/credits/use")
async def use_credits(request: Request, amount: int = Form(...), reason: str = Form(...)):
    """使用點數"""
    ensure_init()
    
    user_id = 1  # TODO: 從 JWT 獲取
    
    if amount <= 0:
        raise HTTPException(status_code=400, detail="金額必須大於 0")
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 檢查餘額
    cursor.execute('SELECT credits FROM users WHERE id = ?', (user_id,))
    row = cursor.fetchone()
    
    if not row or row[0] < amount:
        conn.close()
        raise HTTPException(status_code=400, detail="點數不足")
    
    # 扣除點數
    new_balance = row[0] - amount
    cursor.execute('UPDATE users SET credits = ?, updated_at = ? WHERE id = ?',
                   (new_balance, datetime.now().isoformat(), user_id))
    
    # 記錄
    cursor.execute('''
        INSERT INTO credit_logs (user_id, amount, balance_after, reason, created_at)
        VALUES (?, ?, ?, ?, ?)
    ''', (user_id, -amount, new_balance, reason, datetime.now().isoformat()))
    
    conn.commit()
    conn.close()
    
    return {
        'success': True,
        'used': amount,
        'balance': new_balance
    }


# === 支付回調路由 ===

@router.post("/api/payment/notify")
async def payment_notify(request: Request):
    """
    綠界背景通知 (Server to Server)
    """
    ensure_init()
    
    form_data = await request.form()
    post_data = dict(form_data)
    
    print(f"[Payment] 收到綠界通知: {post_data.get('MerchantTradeNo')}")
    
    try:
        from payment_flow import process_payment_callback
        
        result = process_payment_callback(post_data)
        
        if result.get('success'):
            print(f"[Payment] 處理成功: {result.get('order_no')}")
            return PlainTextResponse("1|OK")
        else:
            print(f"[Payment] 處理失敗: {result.get('error')}")
            return PlainTextResponse(f"0|{result.get('error', 'Error')}")
    
    except Exception as e:
        print(f"[Payment] 異常: {e}")
        import traceback
        traceback.print_exc()
        return PlainTextResponse(f"0|{str(e)}")


# === 支付結果頁 ===

PAYMENT_RESULT_HTML = '''<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} - 北斗命數</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>.gradient-bg {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); }}</style>
</head>
<body class="bg-gray-50 min-h-screen flex items-center justify-center">
    <div class="bg-white rounded-2xl shadow-xl p-8 max-w-md mx-4 text-center">
        <div class="text-6xl mb-4">{icon}</div>
        <h1 class="text-2xl font-bold text-gray-800 mb-2">{title}</h1>
        <p class="text-gray-600 mb-6">{message}</p>
        
        {details_html}
        
        <div class="space-y-3 mt-6">
            <a href="/dashboard" class="block w-full gradient-bg text-white py-3 rounded-xl font-bold hover:opacity-90">
                返回儀表板
            </a>
            <a href="/checkout" class="block w-full border-2 border-purple-600 text-purple-600 py-3 rounded-xl font-bold hover:bg-purple-50">
                繼續購買
            </a>
        </div>
    </div>
</body>
</html>'''


@router.get("/checkout/return", response_class=HTMLResponse)
@router.post("/checkout/return", response_class=HTMLResponse)
async def payment_return(request: Request):
    """支付完成後前台返回頁"""
    ensure_init()
    
    if request.method == "POST":
        form_data = await request.form()
        params = dict(form_data)
    else:
        params = dict(request.query_params)
    
    order_no = params.get('MerchantTradeNo', '')
    rtn_code = params.get('RtnCode', '0')
    rtn_msg = params.get('RtnMsg', '')
    
    if rtn_code == '1':
        try:
            from payment_flow import OrderService
            os = OrderService()
            order = os.get_order(order_no)
            
            if order:
                details_html = f'''
                <div class="bg-green-50 rounded-xl p-4 mb-4 text-left">
                    <p class="text-gray-600"><span class="font-bold">訂單編號:</span> {order_no}</p>
                    <p class="text-gray-600"><span class="font-bold">商品:</span> {order.get('product_name', '')}</p>
                    <p class="text-gray-600"><span class="font-bold">金額:</span> NT${order.get('amount', 0)}</p>
                    {f"<p class='text-gray-600'><span class='font-bold'>獲得點數:</span> {order.get('credits', 0)} 點</p>" if order.get('credits') else ""}
                </div>
                '''
            else:
                details_html = f'<p class="text-gray-500">訂單編號: {order_no}</p>'
        except:
            details_html = f'<p class="text-gray-500">訂單編號: {order_no}</p>'
        
        html = PAYMENT_RESULT_HTML.format(
            icon='✅',
            title='支付成功',
            message='感謝您的購買！點數/會員已即時入帳。',
            details_html=details_html
        )
    else:
        details_html = f'''
        <div class="bg-red-50 rounded-xl p-4 mb-4">
            <p class="text-gray-600">訂單編號: {order_no}</p>
            <p class="text-red-600">原因: {rtn_msg or "用戶取消或支付失敗"}</p>
        </div>
        '''
        
        html = PAYMENT_RESULT_HTML.format(
            icon='❌',
            title='支付未完成',
            message='您的支付未成功完成，請重試。',
            details_html=details_html
        )
    
    return html


# === 訂單查詢 ===

@router.get("/api/user/orders")
async def get_user_orders(request: Request):
    """獲取用戶訂單列表"""
    ensure_init()
    
    user_id = 1  # TODO: 從 JWT 獲取
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            SELECT order_no, product_name, amount, credits, status, created_at, paid_at
            FROM orders WHERE user_id = ? ORDER BY created_at DESC LIMIT 20
        ''', (user_id,))
        
        orders = []
        for row in cursor.fetchall():
            orders.append({
                'order_no': row[0],
                'product_name': row[1],
                'amount': row[2],
                'credits': row[3],
                'status': row[4],
                'created_at': row[5],
                'paid_at': row[6]
            })
    except:
        orders = []
    
    conn.close()
    
    return {'orders': orders}


@router.get("/api/order/{order_no}")
async def get_order_detail(order_no: str, request: Request):
    """獲取訂單詳情"""
    ensure_init()
    
    user_id = 1  # TODO: 從 JWT 獲取
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM orders WHERE order_no = ? AND user_id = ?', (order_no, user_id))
    row = cursor.fetchone()
    conn.close()
    
    if not row:
        raise HTTPException(status_code=404, detail="訂單不存在")
    
    columns = ['id', 'order_no', 'user_id', 'product_id', 'product_name',
               'amount', 'credits', 'order_type', 'status', 'payment_method',
               'payment_no', 'paid_at', 'created_at', 'updated_at']
    
    return dict(zip(columns, row))

# A3.11: 分頁支援
@router.get("/api/user/credits/history")
async def get_credits_history(
    request: Request,
    page: int = 1,
    limit: int = 20
):
    """點數歷史 (分頁)"""
    user_id = 1  # TODO: JWT
    offset = (page - 1) * limit
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('SELECT COUNT(*) FROM credit_logs WHERE user_id = ?', (user_id,))
    total = cursor.fetchone()[0]
    
    cursor.execute('''
        SELECT amount, reason, created_at FROM credit_logs 
        WHERE user_id = ? ORDER BY created_at DESC LIMIT ? OFFSET ?
    ''', (user_id, limit, offset))
    
    logs = [{'amount': r[0], 'reason': r[1], 'date': r[2]} for r in cursor.fetchall()]
    conn.close()
    
    return {
        'logs': logs,
        'pagination': {
            'page': page,
            'limit': limit,
            'total': total,
            'pages': (total + limit - 1) // limit
        }
    }
