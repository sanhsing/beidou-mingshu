"""
訂閱制服務模組
subscription_service.py | @星殼 @流祇 | 2026-02-18
PYLIB: payment_service, membership_service, email_service, db_unified

功能：
- 訂閱方案管理
- 綠界定期定額整合
- 訂閱狀態追蹤
- 自動續訂/取消
"""
import os
import sqlite3
import hashlib
import json
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from enum import Enum
from dataclasses import dataclass, asdict
from urllib.parse import urlencode
from fastapi import APIRouter, Request, HTTPException, Form
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from pydantic import BaseModel

# === 配置 ===
DB_PATH = "beidou_unified.db"
BASE_URL = os.getenv("BASE_URL", "http://localhost:8000")

# 綠界配置
ECPAY_MERCHANT_ID = os.getenv("ECPAY_MERCHANT_ID", "3483910")
ECPAY_HASH_KEY = os.getenv("ECPAY_HASH_KEY", "")
ECPAY_HASH_IV = os.getenv("ECPAY_HASH_IV", "")
ECPAY_PERIOD_URL = "https://payment.ecpay.com.tw/Cashier/AioCheckOut/V5"
ECPAY_PERIOD_URL_STAGE = "https://payment-stage.ecpay.com.tw/Cashier/AioCheckOut/V5"

# 是否使用測試環境
IS_PRODUCTION = os.getenv("ECPAY_PRODUCTION", "false").lower() == "true"

router = APIRouter(prefix="/api/subscription", tags=["subscription"])

# === 訂閱方案定義 ===
class SubscriptionPlan(Enum):
    BASIC_MONTHLY = "basic_monthly"
    BASIC_YEARLY = "basic_yearly"
    PREMIUM_MONTHLY = "premium_monthly"
    PREMIUM_YEARLY = "premium_yearly"
    VIP_MONTHLY = "vip_monthly"
    VIP_YEARLY = "vip_yearly"

@dataclass
class PlanDetail:
    id: str
    name: str
    price: int
    period_type: str  # M=月, Y=年
    period_amount: int  # 執行次數
    exec_times: int  # 總執行次數
    features: List[str]
    tier: str
    credits_per_period: int

PLANS = {
    "basic_monthly": PlanDetail(
        id="basic_monthly",
        name="基礎會員（月繳）",
        price=199,
        period_type="M",
        period_amount=1,
        exec_times=99,
        features=["每月 3 份基礎報告", "八字/紫微分析", "每月運勢"],
        tier="basic",
        credits_per_period=150
    ),
    "basic_yearly": PlanDetail(
        id="basic_yearly",
        name="基礎會員（年繳）",
        price=1990,
        period_type="Y",
        period_amount=1,
        exec_times=99,
        features=["每月 3 份基礎報告", "八字/紫微分析", "每月運勢", "省 $398"],
        tier="basic",
        credits_per_period=1800
    ),
    "premium_monthly": PlanDetail(
        id="premium_monthly",
        name="專業會員（月繳）",
        price=499,
        period_type="M",
        period_amount=1,
        exec_times=99,
        features=["無限基礎報告", "每月 2 份進階報告", "AI 解讀", "優先客服"],
        tier="premium",
        credits_per_period=500
    ),
    "premium_yearly": PlanDetail(
        id="premium_yearly",
        name="專業會員（年繳）",
        price=4990,
        period_type="Y",
        period_amount=1,
        exec_times=99,
        features=["無限基礎報告", "每月 2 份進階報告", "AI 解讀", "優先客服", "省 $998"],
        tier="premium",
        credits_per_period=6000
    ),
    "vip_monthly": PlanDetail(
        id="vip_monthly",
        name="尊榮會員（月繳）",
        price=999,
        period_type="M",
        period_amount=1,
        exec_times=99,
        features=["全功能無限使用", "專屬 AI 顧問", "1對1 客服", "家庭共享 3 人"],
        tier="vip",
        credits_per_period=9999
    ),
    "vip_yearly": PlanDetail(
        id="vip_yearly",
        name="尊榮會員（年繳）",
        price=9990,
        period_type="Y",
        period_amount=1,
        exec_times=99,
        features=["全功能無限使用", "專屬 AI 顧問", "1對1 客服", "家庭共享 5 人", "省 $1998"],
        tier="vip",
        credits_per_period=99999
    ),
}

# === 資料庫初始化 ===
def init_subscription_tables():
    """初始化訂閱表"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS subscriptions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            plan_id TEXT NOT NULL,
            status TEXT DEFAULT 'pending',
            
            -- 綠界定期定額資訊
            merchant_trade_no TEXT UNIQUE,
            period_type TEXT,
            frequency INTEGER DEFAULT 1,
            exec_times INTEGER,
            period_return_url TEXT,
            
            -- 訂閱週期
            current_period_start TEXT,
            current_period_end TEXT,
            next_billing_date TEXT,
            
            -- 自動續訂
            auto_renew INTEGER DEFAULT 1,
            cancel_at_period_end INTEGER DEFAULT 0,
            
            -- 時間戳
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
            cancelled_at TEXT,
            
            FOREIGN KEY (user_id) REFERENCES auth_users(id)
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS subscription_payments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            subscription_id INTEGER NOT NULL,
            merchant_trade_no TEXT,
            trade_no TEXT,
            amount INTEGER,
            status TEXT DEFAULT 'pending',
            period_no INTEGER,
            paid_at TEXT,
            raw_data TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (subscription_id) REFERENCES subscriptions(id)
        )
    ''')
    
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_sub_user ON subscriptions(user_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_sub_status ON subscriptions(status)')
    
    conn.commit()
    conn.close()

# 初始化
init_subscription_tables()

# === 工具函數 ===
def generate_trade_no() -> str:
    """生成訂單編號"""
    import secrets
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    random_str = secrets.token_hex(4).upper()
    return f"SUB{timestamp}{random_str}"

def ecpay_check_mac_value(params: Dict[str, Any]) -> str:
    """計算綠界 CheckMacValue"""
    # 排序參數
    sorted_params = sorted(params.items())
    
    # 組合字串
    param_str = "&".join([f"{k}={v}" for k, v in sorted_params])
    param_str = f"HashKey={ECPAY_HASH_KEY}&{param_str}&HashIV={ECPAY_HASH_IV}"
    
    # URL encode
    import urllib.parse
    encoded = urllib.parse.quote_plus(param_str).lower()
    
    # 特殊字元處理（綠界規則）
    encoded = encoded.replace('%2d', '-').replace('%5f', '_').replace('%2e', '.')
    encoded = encoded.replace('%21', '!').replace('%2a', '*').replace('%28', '(').replace('%29', ')')
    
    # SHA256
    return hashlib.sha256(encoded.encode('utf-8')).hexdigest().upper()

# === API 端點 ===
@router.get("/plans")
async def get_plans():
    """獲取所有訂閱方案"""
    return {
        "plans": [asdict(plan) for plan in PLANS.values()]
    }

@router.get("/plans/{plan_id}")
async def get_plan(plan_id: str):
    """獲取單一方案"""
    if plan_id not in PLANS:
        raise HTTPException(status_code=404, detail="方案不存在")
    return asdict(PLANS[plan_id])

@router.post("/create")
async def create_subscription(request: Request, plan_id: str = Form(...)):
    """創建訂閱"""
    from auth_jwt import get_user_id
    
    user_id = get_user_id(request)
    
    if plan_id not in PLANS:
        raise HTTPException(status_code=400, detail="無效的方案")
    
    plan = PLANS[plan_id]
    merchant_trade_no = generate_trade_no()
    
    # 創建訂閱記錄
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO subscriptions (
            user_id, plan_id, merchant_trade_no, 
            period_type, exec_times, status
        ) VALUES (?, ?, ?, ?, ?, 'pending')
    ''', (user_id, plan_id, merchant_trade_no, plan.period_type, plan.exec_times))
    
    subscription_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    # 組合綠界定期定額參數
    trade_date = datetime.now().strftime("%Y/%m/%d %H:%M:%S")
    
    params = {
        "MerchantID": ECPAY_MERCHANT_ID,
        "MerchantTradeNo": merchant_trade_no,
        "MerchantTradeDate": trade_date,
        "PaymentType": "aio",
        "TotalAmount": plan.price,
        "TradeDesc": f"北斗命數-{plan.name}",
        "ItemName": plan.name,
        "ReturnURL": f"{BASE_URL}/api/subscription/notify",
        "ClientBackURL": f"{BASE_URL}/subscription/success",
        "ChoosePayment": "Credit",
        "EncryptType": 1,
        
        # 定期定額參數
        "PeriodAmount": plan.price,
        "PeriodType": plan.period_type,
        "Frequency": plan.period_amount,
        "ExecTimes": plan.exec_times,
        "PeriodReturnURL": f"{BASE_URL}/api/subscription/period-notify",
    }
    
    params["CheckMacValue"] = ecpay_check_mac_value(params)
    
    # 返回表單 HTML
    payment_url = ECPAY_PERIOD_URL if IS_PRODUCTION else ECPAY_PERIOD_URL_STAGE
    
    form_html = f'''
    <form id="ecpay-form" method="post" action="{payment_url}">
    '''
    for key, value in params.items():
        form_html += f'<input type="hidden" name="{key}" value="{value}">\n'
    form_html += '</form><script>document.getElementById("ecpay-form").submit();</script>'
    
    return HTMLResponse(form_html)

@router.post("/notify")
async def subscription_notify(request: Request):
    """綠界首次付款通知"""
    form_data = await request.form()
    data = dict(form_data)
    
    merchant_trade_no = data.get("MerchantTradeNo")
    rtn_code = data.get("RtnCode")
    trade_no = data.get("TradeNo")
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    if rtn_code == "1":
        # 付款成功
        now = datetime.now()
        
        # 計算訂閱週期
        cursor.execute('SELECT * FROM subscriptions WHERE merchant_trade_no = ?', (merchant_trade_no,))
        sub = cursor.fetchone()
        
        if sub:
            plan_id = sub[2]  # plan_id column
            plan = PLANS.get(plan_id)
            
            if plan:
                if plan.period_type == "M":
                    period_end = now + timedelta(days=30)
                else:
                    period_end = now + timedelta(days=365)
                
                cursor.execute('''
                    UPDATE subscriptions SET 
                        status = 'active',
                        current_period_start = ?,
                        current_period_end = ?,
                        next_billing_date = ?,
                        updated_at = ?
                    WHERE merchant_trade_no = ?
                ''', (now.isoformat(), period_end.isoformat(), 
                      period_end.isoformat(), now.isoformat(), merchant_trade_no))
                
                # 記錄付款
                cursor.execute('''
                    INSERT INTO subscription_payments 
                    (subscription_id, merchant_trade_no, trade_no, amount, status, period_no, paid_at, raw_data)
                    VALUES (?, ?, ?, ?, 'paid', 1, ?, ?)
                ''', (sub[0], merchant_trade_no, trade_no, plan.price, now.isoformat(), json.dumps(data)))
                
                # 更新用戶等級和點數
                user_id = sub[1]
                cursor.execute('''
                    UPDATE auth_users SET 
                        tier = ?,
                        tier_expires_at = ?,
                        credits = credits + ?
                    WHERE id = ?
                ''', (plan.tier, period_end.isoformat(), plan.credits_per_period, user_id))
    
    conn.commit()
    conn.close()
    
    return "1|OK"

@router.post("/period-notify")
async def period_notify(request: Request):
    """綠界定期扣款通知"""
    form_data = await request.form()
    data = dict(form_data)
    
    merchant_trade_no = data.get("MerchantTradeNo")
    rtn_code = data.get("RtnCode")
    period_no = data.get("TotalSuccessTimes")
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM subscriptions WHERE merchant_trade_no = ?', (merchant_trade_no,))
    sub = cursor.fetchone()
    
    if sub and rtn_code == "1":
        now = datetime.now()
        plan = PLANS.get(sub[2])
        
        if plan:
            if plan.period_type == "M":
                period_end = now + timedelta(days=30)
            else:
                period_end = now + timedelta(days=365)
            
            # 更新訂閱週期
            cursor.execute('''
                UPDATE subscriptions SET 
                    current_period_start = ?,
                    current_period_end = ?,
                    next_billing_date = ?,
                    updated_at = ?
                WHERE id = ?
            ''', (now.isoformat(), period_end.isoformat(), 
                  period_end.isoformat(), now.isoformat(), sub[0]))
            
            # 記錄付款
            cursor.execute('''
                INSERT INTO subscription_payments 
                (subscription_id, merchant_trade_no, amount, status, period_no, paid_at, raw_data)
                VALUES (?, ?, ?, 'paid', ?, ?, ?)
            ''', (sub[0], merchant_trade_no, plan.price, period_no, now.isoformat(), json.dumps(data)))
            
            # 更新用戶等級和點數
            user_id = sub[1]
            cursor.execute('''
                UPDATE auth_users SET 
                    tier = ?,
                    tier_expires_at = ?,
                    credits = credits + ?
                WHERE id = ?
            ''', (plan.tier, period_end.isoformat(), plan.credits_per_period, user_id))
    
    conn.commit()
    conn.close()
    
    return "1|OK"

@router.get("/my")
async def my_subscription(request: Request):
    """查詢我的訂閱"""
    from auth_jwt import get_user_id
    
    user_id = get_user_id(request)
    
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT s.*, 
               (SELECT COUNT(*) FROM subscription_payments WHERE subscription_id = s.id) as payment_count
        FROM subscriptions s
        WHERE s.user_id = ? AND s.status = 'active'
        ORDER BY s.created_at DESC
    ''', (user_id,))
    
    subscriptions = [dict(row) for row in cursor.fetchall()]
    conn.close()
    
    # 加入方案詳情
    for sub in subscriptions:
        if sub['plan_id'] in PLANS:
            sub['plan'] = asdict(PLANS[sub['plan_id']])
    
    return {"subscriptions": subscriptions}

@router.post("/cancel/{subscription_id}")
async def cancel_subscription(subscription_id: int, request: Request):
    """取消訂閱（週期結束後生效）"""
    from auth_jwt import get_user_id
    
    user_id = get_user_id(request)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 確認訂閱屬於該用戶
    cursor.execute('SELECT * FROM subscriptions WHERE id = ? AND user_id = ?', 
                   (subscription_id, user_id))
    sub = cursor.fetchone()
    
    if not sub:
        conn.close()
        raise HTTPException(status_code=404, detail="訂閱不存在")
    
    # 標記為週期結束後取消
    cursor.execute('''
        UPDATE subscriptions SET 
            cancel_at_period_end = 1,
            auto_renew = 0,
            updated_at = ?
        WHERE id = ?
    ''', (datetime.now().isoformat(), subscription_id))
    
    conn.commit()
    conn.close()
    
    return {"success": True, "message": "訂閱將在當前週期結束後取消"}

@router.get("/history")
async def subscription_history(request: Request):
    """訂閱付款歷史"""
    from auth_jwt import get_user_id
    
    user_id = get_user_id(request)
    
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT sp.*, s.plan_id 
        FROM subscription_payments sp
        JOIN subscriptions s ON sp.subscription_id = s.id
        WHERE s.user_id = ?
        ORDER BY sp.paid_at DESC
        LIMIT 50
    ''', (user_id,))
    
    payments = [dict(row) for row in cursor.fetchall()]
    conn.close()
    
    return {"payments": payments}

print("✓ 訂閱制服務模組已載入")
