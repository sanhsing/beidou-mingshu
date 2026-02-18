"""
密碼管理 API
password_api.py | @星殼 | 2026-02-17

功能：
- 變更密碼
- 忘記密碼（發送重設郵件）
- 重設密碼（使用 Token）
"""
import os
import secrets
import hashlib
import sqlite3
from datetime import datetime, timedelta
from typing import Optional, Tuple
from fastapi import APIRouter, HTTPException, Depends, Request
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, EmailStr

router = APIRouter(prefix="/api/auth", tags=["password"])

DB_PATH = 'beidou_unified.db'
SITE_URL = os.getenv('SITE_URL', 'http://localhost:8000')

# === 請求模型 ===

class ChangePasswordRequest(BaseModel):
    old_password: str
    new_password: str

class ForgotPasswordRequest(BaseModel):
    email: str

class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str


# === 初始化重設密碼表 ===
def init_password_reset_table():
    """建立密碼重設 Token 表"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS password_resets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            token TEXT UNIQUE NOT NULL,
            expires_at TEXT NOT NULL,
            used INTEGER DEFAULT 0,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES auth_users(id)
        )
    ''')
    
    conn.commit()
    conn.close()

init_password_reset_table()


# === 工具函數 ===

def generate_reset_token() -> str:
    """生成安全的重設 Token"""
    return secrets.token_urlsafe(32)


def hash_password(password: str, salt: str) -> str:
    """密碼雜湊"""
    return hashlib.sha256(f"{password}{salt}".encode()).hexdigest()


def generate_salt() -> str:
    """生成鹽值"""
    return secrets.token_hex(16)


def get_user_by_email(email: str) -> Optional[dict]:
    """透過 Email 查找用戶"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT id, username, email, salt, password_hash 
        FROM auth_users WHERE email = ?
    ''', (email,))
    
    row = cursor.fetchone()
    conn.close()
    
    if row:
        return {
            'id': row[0],
            'username': row[1],
            'email': row[2],
            'salt': row[3],
            'password_hash': row[4]
        }
    return None


def get_user_by_id(user_id: int) -> Optional[dict]:
    """透過 ID 查找用戶"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT id, username, email, salt, password_hash 
        FROM auth_users WHERE id = ?
    ''', (user_id,))
    
    row = cursor.fetchone()
    conn.close()
    
    if row:
        return {
            'id': row[0],
            'username': row[1],
            'email': row[2],
            'salt': row[3],
            'password_hash': row[4]
        }
    return None


def update_password(user_id: int, new_password: str) -> bool:
    """更新用戶密碼"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    new_salt = generate_salt()
    new_hash = hash_password(new_password, new_salt)
    
    cursor.execute('''
        UPDATE auth_users 
        SET salt = ?, password_hash = ?, updated_at = ?
        WHERE id = ?
    ''', (new_salt, new_hash, datetime.now().isoformat(), user_id))
    
    affected = cursor.rowcount
    conn.commit()
    conn.close()
    
    return affected > 0


def create_reset_token(user_id: int) -> str:
    """建立密碼重設 Token"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 作廢舊的 Token
    cursor.execute('''
        UPDATE password_resets SET used = 1 WHERE user_id = ? AND used = 0
    ''', (user_id,))
    
    # 建立新 Token (24 小時有效)
    token = generate_reset_token()
    expires_at = (datetime.now() + timedelta(hours=24)).isoformat()
    
    cursor.execute('''
        INSERT INTO password_resets (user_id, token, expires_at)
        VALUES (?, ?, ?)
    ''', (user_id, token, expires_at))
    
    conn.commit()
    conn.close()
    
    return token


def verify_reset_token(token: str) -> Tuple[bool, Optional[int], str]:
    """驗證重設 Token"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT user_id, expires_at, used FROM password_resets WHERE token = ?
    ''', (token,))
    
    row = cursor.fetchone()
    conn.close()
    
    if not row:
        return False, None, "無效的重設連結"
    
    user_id, expires_at, used = row
    
    if used:
        return False, None, "此連結已使用過"
    
    if datetime.fromisoformat(expires_at) < datetime.now():
        return False, None, "連結已過期，請重新申請"
    
    return True, user_id, "OK"


def mark_token_used(token: str):
    """標記 Token 已使用"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        UPDATE password_resets SET used = 1 WHERE token = ?
    ''', (token,))
    
    conn.commit()
    conn.close()


# === API 路由 ===

@router.post("/change-password")
async def change_password(req: ChangePasswordRequest, request: Request):
    """
    變更密碼
    需要登入狀態，提供舊密碼和新密碼
    """
    # 從 Authorization header 取得 user_id
    auth_header = request.headers.get('Authorization', '')
    if not auth_header.startswith('Bearer '):
        raise HTTPException(status_code=401, detail="請先登入")
    
    token = auth_header.replace('Bearer ', '')
    
    # 驗證 Token 並取得用戶
    try:
        from auth_jwt import get_auth_manager
        auth = get_auth_manager()
        valid, user, msg = auth.verify(token)
        
        if not valid or not user:
            raise HTTPException(status_code=401, detail="登入已過期，請重新登入")
        
        user_data = get_user_by_id(user.id)
        if not user_data:
            raise HTTPException(status_code=404, detail="用戶不存在")
        
    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))
    
    # 驗證舊密碼
    old_hash = hash_password(req.old_password, user_data['salt'])
    if old_hash != user_data['password_hash']:
        raise HTTPException(status_code=400, detail="原密碼錯誤")
    
    # 驗證新密碼
    if len(req.new_password) < 6:
        raise HTTPException(status_code=400, detail="新密碼至少 6 個字符")
    
    if req.old_password == req.new_password:
        raise HTTPException(status_code=400, detail="新密碼不能與舊密碼相同")
    
    # 更新密碼
    if update_password(user_data['id'], req.new_password):
        return {"success": True, "message": "密碼修改成功"}
    else:
        raise HTTPException(status_code=500, detail="密碼修改失敗")


@router.post("/forgot-password")
async def forgot_password(req: ForgotPasswordRequest):
    """
    忘記密碼
    發送密碼重設郵件
    """
    # 查找用戶
    user = get_user_by_email(req.email)
    
    # 不管用戶是否存在，都返回相同訊息（安全考量）
    if not user:
        return {
            "success": True, 
            "message": "如果此信箱已註冊，您將收到密碼重設郵件"
        }
    
    # 建立重設 Token
    token = create_reset_token(user['id'])
    reset_url = f"{SITE_URL}/reset-password?token={token}"
    
    # 發送郵件
    try:
        from email_service import email_service
        
        subject = "【北斗命數】密碼重設"
        body = f"""
您好 {user['username']}，

您申請了密碼重設，請點擊以下連結重設密碼：

{reset_url}

此連結 24 小時內有效。

如果您沒有申請密碼重設，請忽略此郵件。

北斗命數團隊
"""
        email_service.send(to=req.email, subject=subject, body=body)
        print(f"[Password] 密碼重設郵件已發送: {req.email}")
        
    except Exception as e:
        print(f"[Password] 郵件發送失敗: {e}")
        # 即使郵件失敗，也返回成功（避免洩露用戶存在與否）
    
    return {
        "success": True, 
        "message": "如果此信箱已註冊，您將收到密碼重設郵件"
    }


@router.post("/reset-password")
async def reset_password(req: ResetPasswordRequest):
    """
    重設密碼
    使用 Token 設定新密碼
    """
    # 驗證 Token
    valid, user_id, msg = verify_reset_token(req.token)
    
    if not valid:
        raise HTTPException(status_code=400, detail=msg)
    
    # 驗證新密碼
    if len(req.new_password) < 6:
        raise HTTPException(status_code=400, detail="密碼至少 6 個字符")
    
    # 更新密碼
    if not update_password(user_id, req.new_password):
        raise HTTPException(status_code=500, detail="密碼重設失敗")
    
    # 標記 Token 已使用
    mark_token_used(req.token)
    
    return {"success": True, "message": "密碼重設成功，請使用新密碼登入"}


@router.get("/reset-password/verify")
async def verify_reset_link(token: str):
    """
    驗證重設連結是否有效
    前端用於顯示適當的頁面
    """
    valid, user_id, msg = verify_reset_token(token)
    
    return {
        "valid": valid,
        "message": msg if not valid else "連結有效"
    }


# === 重設密碼頁面 ===

RESET_PASSWORD_PAGE = '''<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>重設密碼 - 北斗命數</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-gray-50 min-h-screen flex items-center justify-center">
    <div class="bg-white rounded-2xl shadow-xl p-8 max-w-md w-full mx-4">
        <h1 class="text-2xl font-bold text-center mb-6">重設密碼</h1>
        
        <div id="loading" class="text-center py-8">
            <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-600 mx-auto"></div>
            <p class="mt-4 text-gray-600">驗證中...</p>
        </div>
        
        <div id="invalid" class="hidden text-center py-8">
            <div class="text-6xl mb-4">❌</div>
            <h2 class="text-xl font-bold text-red-600 mb-2">連結無效</h2>
            <p id="error-msg" class="text-gray-600 mb-6"></p>
            <a href="/forgot-password" class="text-purple-600 hover:underline">重新申請密碼重設</a>
        </div>
        
        <form id="reset-form" class="hidden space-y-4">
            <div>
                <label class="block text-gray-700 mb-2">新密碼</label>
                <input type="password" id="password" required minlength="6"
                       class="w-full px-4 py-3 border rounded-xl focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                       placeholder="至少 6 個字符">
            </div>
            <div>
                <label class="block text-gray-700 mb-2">確認密碼</label>
                <input type="password" id="confirm" required
                       class="w-full px-4 py-3 border rounded-xl focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                       placeholder="再次輸入新密碼">
            </div>
            <button type="submit" 
                    class="w-full bg-purple-600 text-white py-3 rounded-xl font-bold hover:bg-purple-700">
                重設密碼
            </button>
        </form>
        
        <div id="success" class="hidden text-center py-8">
            <div class="text-6xl mb-4">✅</div>
            <h2 class="text-xl font-bold text-green-600 mb-2">密碼重設成功</h2>
            <p class="text-gray-600 mb-6">請使用新密碼登入</p>
            <a href="/login" class="block w-full bg-purple-600 text-white py-3 rounded-xl font-bold text-center hover:bg-purple-700">
                前往登入
            </a>
        </div>
    </div>
    
    <script>
        const token = new URLSearchParams(window.location.search).get('token');
        
        async function verifyToken() {
            if (!token) {
                showInvalid('缺少重設連結');
                return;
            }
            
            try {
                const res = await fetch(`/api/auth/reset-password/verify?token=${token}`);
                const data = await res.json();
                
                if (data.valid) {
                    document.getElementById('loading').classList.add('hidden');
                    document.getElementById('reset-form').classList.remove('hidden');
                } else {
                    showInvalid(data.message);
                }
            } catch (e) {
                showInvalid('驗證失敗，請稍後再試');
            }
        }
        
        function showInvalid(msg) {
            document.getElementById('loading').classList.add('hidden');
            document.getElementById('invalid').classList.remove('hidden');
            document.getElementById('error-msg').textContent = msg;
        }
        
        document.getElementById('reset-form').addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const password = document.getElementById('password').value;
            const confirm = document.getElementById('confirm').value;
            
            if (password !== confirm) {
                alert('兩次輸入的密碼不一致');
                return;
            }
            
            try {
                const res = await fetch('/api/auth/reset-password', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({ token, new_password: password })
                });
                
                const data = await res.json();
                
                if (data.success) {
                    document.getElementById('reset-form').classList.add('hidden');
                    document.getElementById('success').classList.remove('hidden');
                } else {
                    alert(data.detail || '重設失敗');
                }
            } catch (e) {
                alert('請求失敗，請稍後再試');
            }
        });
        
        verifyToken();
    </script>
</body>
</html>'''


@router.get("/reset-password-page", response_class=HTMLResponse)
async def reset_password_page():
    """重設密碼頁面"""
    from fastapi.responses import HTMLResponse
    return HTMLResponse(content=RESET_PASSWORD_PAGE)


print("✓ 密碼管理 API 已載入")
