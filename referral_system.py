"""
推薦系統模組
referral_system.py | @星殼 @流祇 | 2026-02-18
PYLIB: db_unified, email_service

功能：
- 推薦碼生成
- 推薦獎勵
- 推薦統計
- 病毒式傳播
"""
import sqlite3
import secrets
from datetime import datetime
from typing import Optional, List
from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from pydantic import BaseModel, EmailStr

# === 配置 ===
DB_PATH = "beidou_unified.db"
BASE_URL = "https://beidou-mingshu.com"

# 獎勵設定
REFERRER_CREDITS = 50      # 推薦人獲得點數
REFEREE_CREDITS = 30       # 被推薦人獲得點數
REFERRER_DISCOUNT = 10     # 推薦人折扣 %
REFEREE_DISCOUNT = 20      # 被推薦人首購折扣 %

router = APIRouter(prefix="/api/referral", tags=["referral"])

# === 資料模型 ===
class InviteEmailRequest(BaseModel):
    emails: List[EmailStr]
    message: Optional[str] = None

# === 資料庫初始化 ===
def init_referral_tables():
    """初始化推薦表"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS referral_codes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER UNIQUE NOT NULL,
            code TEXT UNIQUE NOT NULL,
            total_referrals INTEGER DEFAULT 0,
            total_credits_earned INTEGER DEFAULT 0,
            is_active INTEGER DEFAULT 1,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES auth_users(id)
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS referrals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            referrer_id INTEGER NOT NULL,
            referee_id INTEGER NOT NULL,
            referral_code TEXT NOT NULL,
            status TEXT DEFAULT 'pending',
            referrer_credited INTEGER DEFAULT 0,
            referee_credited INTEGER DEFAULT 0,
            first_purchase_at TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (referrer_id) REFERENCES auth_users(id),
            FOREIGN KEY (referee_id) REFERENCES auth_users(id)
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS referral_invites (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            email TEXT NOT NULL,
            status TEXT DEFAULT 'sent',
            sent_at TEXT DEFAULT CURRENT_TIMESTAMP,
            registered_at TEXT,
            FOREIGN KEY (user_id) REFERENCES auth_users(id)
        )
    ''')
    
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_referral_code ON referral_codes(code)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_referrals_referrer ON referrals(referrer_id)')
    
    conn.commit()
    conn.close()

init_referral_tables()

# === 工具函數 ===
def generate_referral_code(username: str) -> str:
    """生成推薦碼"""
    prefix = username[:3].upper() if len(username) >= 3 else username.upper()
    suffix = secrets.token_hex(3).upper()
    return f"{prefix}{suffix}"

def get_or_create_referral_code(user_id: int, username: str) -> str:
    """獲取或創建推薦碼"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('SELECT code FROM referral_codes WHERE user_id = ?', (user_id,))
    row = cursor.fetchone()
    
    if row:
        conn.close()
        return row[0]
    
    code = generate_referral_code(username)
    
    # 確保唯一
    while True:
        cursor.execute('SELECT id FROM referral_codes WHERE code = ?', (code,))
        if not cursor.fetchone():
            break
        code = generate_referral_code(username)
    
    cursor.execute('''
        INSERT INTO referral_codes (user_id, code)
        VALUES (?, ?)
    ''', (user_id, code))
    
    conn.commit()
    conn.close()
    
    return code

def process_referral_reward(referrer_id: int, referee_id: int, referral_code: str):
    """處理推薦獎勵"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 給推薦人加點數
    cursor.execute('''
        UPDATE auth_users SET credits = credits + ? WHERE id = ?
    ''', (REFERRER_CREDITS, referrer_id))
    
    # 給被推薦人加點數
    cursor.execute('''
        UPDATE auth_users SET credits = credits + ? WHERE id = ?
    ''', (REFEREE_CREDITS, referee_id))
    
    # 更新推薦記錄
    cursor.execute('''
        UPDATE referrals SET 
            status = 'completed',
            referrer_credited = ?,
            referee_credited = ?
        WHERE referrer_id = ? AND referee_id = ?
    ''', (REFERRER_CREDITS, REFEREE_CREDITS, referrer_id, referee_id))
    
    # 更新推薦碼統計
    cursor.execute('''
        UPDATE referral_codes SET 
            total_referrals = total_referrals + 1,
            total_credits_earned = total_credits_earned + ?
        WHERE code = ?
    ''', (REFERRER_CREDITS, referral_code))
    
    conn.commit()
    conn.close()

# === API 端點 ===
@router.get("/my-code")
async def get_my_code(request: Request):
    """獲取我的推薦碼"""
    from auth_jwt import get_user_id
    
    user_id = get_user_id(request)
    
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute('SELECT username FROM auth_users WHERE id = ?', (user_id,))
    user = cursor.fetchone()
    conn.close()
    
    if not user:
        raise HTTPException(status_code=404, detail="用戶不存在")
    
    code = get_or_create_referral_code(user_id, user['username'])
    referral_url = f"{BASE_URL}/r/{code}"
    
    return {
        "code": code,
        "referral_url": referral_url,
        "rewards": {
            "referrer_credits": REFERRER_CREDITS,
            "referee_credits": REFEREE_CREDITS,
            "referrer_discount": REFERRER_DISCOUNT,
            "referee_discount": REFEREE_DISCOUNT
        }
    }

@router.get("/stats")
async def referral_stats(request: Request):
    """推薦統計"""
    from auth_jwt import get_user_id
    
    user_id = get_user_id(request)
    
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # 獲取推薦碼資訊
    cursor.execute('SELECT * FROM referral_codes WHERE user_id = ?', (user_id,))
    code_info = cursor.fetchone()
    
    # 獲取推薦明細
    cursor.execute('''
        SELECT r.*, u.username as referee_name, u.created_at as referee_joined
        FROM referrals r
        JOIN auth_users u ON r.referee_id = u.id
        WHERE r.referrer_id = ?
        ORDER BY r.created_at DESC
    ''', (user_id,))
    
    referrals = [dict(row) for row in cursor.fetchall()]
    
    # 統計
    cursor.execute('''
        SELECT 
            COUNT(*) as total,
            SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) as completed,
            SUM(referrer_credited) as total_earned
        FROM referrals WHERE referrer_id = ?
    ''', (user_id,))
    
    stats = dict(cursor.fetchone())
    conn.close()
    
    return {
        "code": code_info['code'] if code_info else None,
        "stats": stats,
        "referrals": referrals[:20]  # 最近 20 筆
    }

@router.post("/invite")
async def send_invites(req: InviteEmailRequest, request: Request):
    """發送邀請 Email"""
    from auth_jwt import get_user_id
    from email_service import EmailService
    
    user_id = get_user_id(request)
    
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute('SELECT username, display_name FROM auth_users WHERE id = ?', (user_id,))
    user = cursor.fetchone()
    
    code = get_or_create_referral_code(user_id, user['username'])
    referral_url = f"{BASE_URL}/r/{code}"
    
    display_name = user['display_name'] or user['username']
    custom_message = req.message or ""
    
    email_service = EmailService()
    sent_count = 0
    
    for email in req.emails[:10]:  # 限制每次最多 10 封
        # 記錄邀請
        cursor.execute('''
            INSERT INTO referral_invites (user_id, email)
            VALUES (?, ?)
        ''', (user_id, email))
        
        # 發送郵件
        html = f'''
        <div style="max-width:600px;margin:0 auto;font-family:sans-serif;">
            <div style="background:linear-gradient(135deg,#667eea 0%,#764ba2 100%);padding:30px;text-align:center;">
                <h1 style="color:white;margin:0;">🌟 北斗命數</h1>
            </div>
            <div style="padding:30px;background:#f9fafb;">
                <h2 style="color:#1f2937;">{display_name} 邀請您加入北斗命數</h2>
                {f'<p style="color:#4b5563;background:#fff;padding:15px;border-radius:8px;border-left:4px solid #667eea;">{custom_message}</p>' if custom_message else ''}
                <p style="color:#4b5563;">北斗命數是一個結合傳統命理與現代科技的專業分析平台，提供八字、紫微、梅花易數等多種命理服務。</p>
                <div style="text-align:center;margin:30px 0;">
                    <a href="{referral_url}" 
                       style="background:#667eea;color:white;padding:15px 30px;border-radius:8px;text-decoration:none;font-weight:bold;">
                        立即加入，獲得 {REFEREE_CREDITS} 點數
                    </a>
                </div>
                <p style="color:#6b7280;font-size:14px;text-align:center;">
                    使用邀請碼 <strong>{code}</strong> 註冊，即可獲得專屬優惠！
                </p>
            </div>
        </div>
        '''
        
        if email_service._send(email, f'{display_name} 邀請您體驗北斗命數', html):
            sent_count += 1
    
    conn.commit()
    conn.close()
    
    return {
        "success": True,
        "sent_count": sent_count,
        "message": f"已發送 {sent_count} 封邀請"
    }

@router.get("/validate/{code}")
async def validate_code(code: str):
    """驗證推薦碼"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT rc.*, u.username, u.display_name
        FROM referral_codes rc
        JOIN auth_users u ON rc.user_id = u.id
        WHERE rc.code = ? AND rc.is_active = 1
    ''', (code,))
    
    row = cursor.fetchone()
    conn.close()
    
    if not row:
        return {"valid": False}
    
    return {
        "valid": True,
        "referrer_name": row['display_name'] or row['username'],
        "bonus_credits": REFEREE_CREDITS,
        "first_purchase_discount": REFEREE_DISCOUNT
    }

@router.post("/apply/{code}")
async def apply_referral(code: str, request: Request):
    """套用推薦碼（註冊時調用）"""
    from auth_jwt import get_user_id
    
    referee_id = get_user_id(request)
    
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # 獲取推薦碼資訊
    cursor.execute('''
        SELECT * FROM referral_codes WHERE code = ? AND is_active = 1
    ''', (code,))
    
    referral_code = cursor.fetchone()
    if not referral_code:
        conn.close()
        raise HTTPException(status_code=400, detail="無效的推薦碼")
    
    referrer_id = referral_code['user_id']
    
    # 不能自己推薦自己
    if referrer_id == referee_id:
        conn.close()
        raise HTTPException(status_code=400, detail="不能使用自己的推薦碼")
    
    # 檢查是否已被推薦過
    cursor.execute('''
        SELECT id FROM referrals WHERE referee_id = ?
    ''', (referee_id,))
    
    if cursor.fetchone():
        conn.close()
        raise HTTPException(status_code=400, detail="您已使用過推薦碼")
    
    # 創建推薦記錄
    cursor.execute('''
        INSERT INTO referrals (referrer_id, referee_id, referral_code, status)
        VALUES (?, ?, ?, 'pending')
    ''', (referrer_id, referee_id, code))
    
    conn.commit()
    conn.close()
    
    # 處理獎勵
    process_referral_reward(referrer_id, referee_id, code)
    
    return {
        "success": True,
        "credits_earned": REFEREE_CREDITS,
        "message": f"成功套用推薦碼，已獲得 {REFEREE_CREDITS} 點數！"
    }

# === 推薦落地頁 ===
@router.get("/landing/{code}", response_class=HTMLResponse)
async def referral_landing(code: str):
    """推薦落地頁"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT rc.*, u.display_name, u.username
        FROM referral_codes rc
        JOIN auth_users u ON rc.user_id = u.id
        WHERE rc.code = ? AND rc.is_active = 1
    ''', (code,))
    
    row = cursor.fetchone()
    conn.close()
    
    if not row:
        return RedirectResponse("/")
    
    referrer_name = row['display_name'] or row['username']
    
    return f'''<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>接受 {referrer_name} 的邀請 - 北斗命數</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-gradient-to-br from-purple-600 to-indigo-800 min-h-screen flex items-center justify-center p-4">
    <div class="bg-white rounded-2xl shadow-2xl max-w-md w-full p-8 text-center">
        <div class="text-5xl mb-4">🌟</div>
        <h1 class="text-2xl font-bold text-gray-800 mb-2">
            {referrer_name} 邀請您加入
        </h1>
        <h2 class="text-3xl font-bold text-purple-600 mb-6">北斗命數</h2>
        
        <div class="bg-purple-50 rounded-xl p-4 mb-6">
            <p class="text-purple-600 font-medium">專屬新用戶禮物</p>
            <div class="flex justify-center gap-4 mt-3">
                <div class="text-center">
                    <p class="text-3xl font-bold text-purple-600">{REFEREE_CREDITS}</p>
                    <p class="text-sm text-gray-600">免費點數</p>
                </div>
                <div class="text-center">
                    <p class="text-3xl font-bold text-purple-600">{REFEREE_DISCOUNT}%</p>
                    <p class="text-sm text-gray-600">首購折扣</p>
                </div>
            </div>
        </div>
        
        <div class="space-y-3">
            <a href="/register?ref={code}" 
               class="block w-full bg-purple-600 text-white py-3 rounded-lg font-medium hover:bg-purple-700 transition">
                立即註冊領取
            </a>
            <a href="/login?ref={code}" 
               class="block w-full border border-purple-600 text-purple-600 py-3 rounded-lg font-medium hover:bg-purple-50 transition">
                已有帳號？登入
            </a>
        </div>
        
        <p class="text-gray-500 text-sm mt-6">
            邀請碼：<span class="font-mono font-bold">{code}</span>
        </p>
    </div>
</body>
</html>'''

# === 簡短網址重定向 ===
@router.get("/r/{code}")
async def short_referral_redirect(code: str):
    """簡短推薦網址重定向"""
    return RedirectResponse(f"/api/referral/landing/{code}")

print("✓ 推薦系統模組已載入")
