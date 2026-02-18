"""
Email 驗證模組
email_verification.py | @流祇 | 2026-02-18
PYLIB: email_service, db_unified, password_api (token機制)

功能：
- 生成驗證碼
- 發送驗證郵件
- 驗證碼校驗
- 重發驗證碼
"""
import sqlite3
import secrets
import hashlib
from datetime import datetime, timedelta
from typing import Optional, Tuple
from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel, EmailStr

# === 配置 ===
DB_PATH = "beidou_unified.db"
VERIFY_CODE_EXPIRE_MINUTES = 30
VERIFY_CODE_LENGTH = 6

router = APIRouter(prefix="/api/auth", tags=["email-verification"])

# === 資料模型 ===
class SendVerifyRequest(BaseModel):
    email: EmailStr

class VerifyCodeRequest(BaseModel):
    email: EmailStr
    code: str

# === 資料庫初始化 ===
def init_verification_table():
    """初始化驗證碼表"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS email_verifications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            email TEXT NOT NULL,
            code TEXT NOT NULL,
            code_hash TEXT NOT NULL,
            is_used INTEGER DEFAULT 0,
            expires_at TEXT NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES auth_users(id)
        )
    ''')
    
    # 索引
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_verify_email ON email_verifications(email)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_verify_code ON email_verifications(code_hash)')
    
    conn.commit()
    conn.close()

# 初始化
init_verification_table()

# === 工具函數 ===
def generate_verify_code() -> str:
    """生成 6 位數驗證碼"""
    return ''.join([str(secrets.randbelow(10)) for _ in range(VERIFY_CODE_LENGTH)])

def hash_code(code: str) -> str:
    """哈希驗證碼"""
    return hashlib.sha256(code.encode()).hexdigest()

def get_user_by_email(email: str) -> Optional[dict]:
    """根據 Email 獲取用戶"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM auth_users WHERE email = ?', (email,))
    row = cursor.fetchone()
    conn.close()
    
    return dict(row) if row else None

def create_verification_code(user_id: int, email: str) -> str:
    """創建驗證碼"""
    code = generate_verify_code()
    code_hash = hash_code(code)
    expires_at = (datetime.now() + timedelta(minutes=VERIFY_CODE_EXPIRE_MINUTES)).isoformat()
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 使舊的未使用驗證碼失效
    cursor.execute('''
        UPDATE email_verifications 
        SET is_used = 1 
        WHERE email = ? AND is_used = 0
    ''', (email,))
    
    # 插入新驗證碼
    cursor.execute('''
        INSERT INTO email_verifications (user_id, email, code, code_hash, expires_at)
        VALUES (?, ?, ?, ?, ?)
    ''', (user_id, email, code, code_hash, expires_at))
    
    conn.commit()
    conn.close()
    
    return code

def verify_code(email: str, code: str) -> Tuple[bool, str, Optional[int]]:
    """
    驗證驗證碼
    Returns: (is_valid, message, user_id)
    """
    code_hash = hash_code(code)
    
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT * FROM email_verifications 
        WHERE email = ? AND code_hash = ? AND is_used = 0
        ORDER BY created_at DESC LIMIT 1
    ''', (email, code_hash))
    
    row = cursor.fetchone()
    
    if not row:
        conn.close()
        return False, "驗證碼錯誤", None
    
    record = dict(row)
    
    # 檢查是否過期
    expires_at = datetime.fromisoformat(record['expires_at'])
    if datetime.now() > expires_at:
        conn.close()
        return False, "驗證碼已過期，請重新發送", None
    
    # 標記為已使用
    cursor.execute('UPDATE email_verifications SET is_used = 1 WHERE id = ?', (record['id'],))
    
    # 更新用戶為已驗證
    cursor.execute('UPDATE auth_users SET is_verified = 1 WHERE email = ?', (email,))
    
    conn.commit()
    conn.close()
    
    return True, "驗證成功", record['user_id']

# === Email 發送 ===
def send_verification_email(email: str, code: str) -> bool:
    """發送驗證郵件"""
    try:
        from email_service import EmailService
        
        service = EmailService()
        
        html = f'''
        <div style="max-width:600px;margin:0 auto;font-family:sans-serif;">
            <div style="background:linear-gradient(135deg,#667eea 0%,#764ba2 100%);padding:30px;text-align:center;">
                <h1 style="color:white;margin:0;">🌟 北斗命數</h1>
            </div>
            <div style="padding:30px;background:#f9fafb;">
                <h2 style="color:#1f2937;">Email 驗證</h2>
                <p style="color:#4b5563;">請使用以下驗證碼完成 Email 驗證：</p>
                <div style="background:#fff;border:2px dashed #667eea;padding:20px;text-align:center;margin:20px 0;">
                    <span style="font-size:32px;font-weight:bold;color:#667eea;letter-spacing:8px;">{code}</span>
                </div>
                <p style="color:#6b7280;font-size:14px;">
                    此驗證碼將在 {VERIFY_CODE_EXPIRE_MINUTES} 分鐘後失效。<br>
                    如果這不是您的操作，請忽略此郵件。
                </p>
            </div>
            <div style="padding:20px;text-align:center;color:#9ca3af;font-size:12px;">
                © 2026 北斗命數 | 此為系統自動發送，請勿回覆
            </div>
        </div>
        '''
        
        return service._send(email, '【北斗命數】Email 驗證碼', html)
    except Exception as e:
        print(f"[EmailVerify] 發送失敗: {e}")
        return False

# === API 端點 ===
@router.post("/send-verification")
async def send_verification(req: SendVerifyRequest):
    """發送驗證碼"""
    user = get_user_by_email(req.email)
    
    if not user:
        # 安全起見，不透露用戶是否存在
        return {"success": True, "message": "如果該 Email 已註冊，驗證碼已發送"}
    
    if user.get('is_verified'):
        return {"success": True, "message": "此 Email 已驗證"}
    
    # 生成並發送驗證碼
    code = create_verification_code(user['id'], req.email)
    send_verification_email(req.email, code)
    
    return {
        "success": True,
        "message": f"驗證碼已發送至 {req.email}，{VERIFY_CODE_EXPIRE_MINUTES} 分鐘內有效"
    }

@router.post("/verify-email")
async def verify_email(req: VerifyCodeRequest):
    """驗證 Email"""
    is_valid, message, user_id = verify_code(req.email, req.code)
    
    if not is_valid:
        raise HTTPException(status_code=400, detail=message)
    
    return {
        "success": True,
        "message": "Email 驗證成功",
        "verified": True
    }

@router.get("/verification-status")
async def verification_status(email: str):
    """查詢驗證狀態"""
    user = get_user_by_email(email)
    
    if not user:
        raise HTTPException(status_code=404, detail="用戶不存在")
    
    return {
        "email": email,
        "is_verified": bool(user.get('is_verified', 0))
    }

# === 驗證頁面 ===
@router.get("/verify-email-page", response_class=HTMLResponse)
async def verify_email_page(email: str = ""):
    """Email 驗證頁面"""
    return f'''<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Email 驗證 - 北斗命數</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-gray-50 min-h-screen flex items-center justify-center">
    <div class="max-w-md w-full bg-white rounded-xl shadow-lg p-8">
        <div class="text-center mb-8">
            <h1 class="text-3xl font-bold text-purple-600">🌟 北斗命數</h1>
            <p class="text-gray-600 mt-2">Email 驗證</p>
        </div>
        
        <div id="step1" class="space-y-4">
            <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Email</label>
                <input type="email" id="email" value="{email}"
                       class="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-purple-500"
                       placeholder="your@email.com">
            </div>
            <button onclick="sendCode()" 
                    class="w-full bg-purple-600 text-white py-2 rounded-lg hover:bg-purple-700">
                發送驗證碼
            </button>
        </div>
        
        <div id="step2" class="hidden space-y-4">
            <p class="text-center text-gray-600">驗證碼已發送至 <span id="sentEmail" class="font-medium"></span></p>
            <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">驗證碼</label>
                <input type="text" id="code" maxlength="6"
                       class="w-full px-4 py-2 border rounded-lg text-center text-2xl tracking-widest focus:ring-2 focus:ring-purple-500"
                       placeholder="000000">
            </div>
            <button onclick="verifyCode()" 
                    class="w-full bg-purple-600 text-white py-2 rounded-lg hover:bg-purple-700">
                驗證
            </button>
            <button onclick="sendCode()" 
                    class="w-full text-purple-600 py-2 hover:underline">
                重新發送驗證碼
            </button>
        </div>
        
        <div id="success" class="hidden text-center">
            <div class="text-6xl mb-4">✅</div>
            <h2 class="text-xl font-bold text-green-600">驗證成功！</h2>
            <p class="text-gray-600 mt-2">您的 Email 已驗證完成</p>
            <a href="/dashboard" class="inline-block mt-4 bg-purple-600 text-white px-6 py-2 rounded-lg">
                進入儀表板
            </a>
        </div>
        
        <div id="message" class="mt-4 text-center text-sm"></div>
    </div>
    
    <script>
        async function sendCode() {{
            const email = document.getElementById('email').value;
            if (!email) return alert('請輸入 Email');
            
            try {{
                const res = await fetch('/api/auth/send-verification', {{
                    method: 'POST',
                    headers: {{'Content-Type': 'application/json'}},
                    body: JSON.stringify({{ email }})
                }});
                const data = await res.json();
                
                if (data.success) {{
                    document.getElementById('step1').classList.add('hidden');
                    document.getElementById('step2').classList.remove('hidden');
                    document.getElementById('sentEmail').textContent = email;
                    showMessage(data.message, 'green');
                }}
            }} catch (e) {{
                showMessage('發送失敗，請稍後再試', 'red');
            }}
        }}
        
        async function verifyCode() {{
            const email = document.getElementById('email').value;
            const code = document.getElementById('code').value;
            if (!code || code.length !== 6) return alert('請輸入 6 位驗證碼');
            
            try {{
                const res = await fetch('/api/auth/verify-email', {{
                    method: 'POST',
                    headers: {{'Content-Type': 'application/json'}},
                    body: JSON.stringify({{ email, code }})
                }});
                
                if (res.ok) {{
                    document.getElementById('step2').classList.add('hidden');
                    document.getElementById('success').classList.remove('hidden');
                }} else {{
                    const data = await res.json();
                    showMessage(data.detail || '驗證失敗', 'red');
                }}
            }} catch (e) {{
                showMessage('驗證失敗，請稍後再試', 'red');
            }}
        }}
        
        function showMessage(msg, color) {{
            const el = document.getElementById('message');
            el.textContent = msg;
            el.className = 'mt-4 text-center text-sm text-' + color + '-600';
        }}
    </script>
</body>
</html>'''

print("✓ Email 驗證模組已載入")
