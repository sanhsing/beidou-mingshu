"""
社交登入模組
social_auth.py | @流祇 @璃語 | 2026-02-18
PYLIB: auth_jwt, db_unified

支援：
- Google OAuth 2.0
- LINE Login
- (未來) Facebook Login

流程：
1. 前端導向 OAuth Provider
2. Provider 回調帶 code
3. 後端用 code 換 token
4. 用 token 取得用戶資料
5. 建立/更新本地用戶
6. 發放 JWT
"""
import os
import sqlite3
import secrets
import httpx
from datetime import datetime
from typing import Optional, Dict, Any
from urllib.parse import urlencode
from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import RedirectResponse, HTMLResponse, JSONResponse

# === 配置 ===
DB_PATH = "beidou_unified.db"
BASE_URL = os.getenv("BASE_URL", "http://localhost:8000")

# Google OAuth
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID", "")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET", "")
GOOGLE_REDIRECT_URI = f"{BASE_URL}/api/auth/google/callback"

# LINE Login
LINE_CHANNEL_ID = os.getenv("LINE_CHANNEL_ID", "")
LINE_CHANNEL_SECRET = os.getenv("LINE_CHANNEL_SECRET", "")
LINE_REDIRECT_URI = f"{BASE_URL}/api/auth/line/callback"

router = APIRouter(prefix="/api/auth", tags=["social-auth"])

# === 資料庫初始化 ===
def init_social_auth_table():
    """初始化社交登入表"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 社交帳號關聯表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS social_accounts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            provider TEXT NOT NULL,
            provider_user_id TEXT NOT NULL,
            email TEXT,
            display_name TEXT,
            avatar_url TEXT,
            access_token TEXT,
            refresh_token TEXT,
            token_expires_at TEXT,
            raw_data TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES auth_users(id),
            UNIQUE(provider, provider_user_id)
        )
    ''')
    
    # OAuth state 表（防 CSRF）
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS oauth_states (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            state TEXT UNIQUE NOT NULL,
            provider TEXT NOT NULL,
            redirect_url TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            expires_at TEXT NOT NULL
        )
    ''')
    
    conn.commit()
    conn.close()

# 初始化
init_social_auth_table()

# === 工具函數 ===
def generate_state() -> str:
    """生成 OAuth state"""
    return secrets.token_urlsafe(32)

def save_state(state: str, provider: str, redirect_url: str = "/dashboard"):
    """保存 state"""
    from datetime import timedelta
    expires_at = (datetime.now() + timedelta(minutes=10)).isoformat()
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO oauth_states (state, provider, redirect_url, expires_at)
        VALUES (?, ?, ?, ?)
    ''', (state, provider, redirect_url, expires_at))
    conn.commit()
    conn.close()

def verify_state(state: str, provider: str) -> Optional[str]:
    """驗證 state，返回 redirect_url"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT * FROM oauth_states 
        WHERE state = ? AND provider = ?
    ''', (state, provider))
    
    row = cursor.fetchone()
    
    if not row:
        conn.close()
        return None
    
    record = dict(row)
    
    # 刪除已使用的 state
    cursor.execute('DELETE FROM oauth_states WHERE id = ?', (record['id'],))
    conn.commit()
    conn.close()
    
    # 檢查是否過期
    expires_at = datetime.fromisoformat(record['expires_at'])
    if datetime.now() > expires_at:
        return None
    
    return record['redirect_url']

def find_or_create_user(provider: str, provider_user_id: str, email: str, 
                        display_name: str, avatar_url: str = None) -> Dict[str, Any]:
    """查找或創建用戶"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # 先查找是否已有社交帳號關聯
    cursor.execute('''
        SELECT user_id FROM social_accounts 
        WHERE provider = ? AND provider_user_id = ?
    ''', (provider, provider_user_id))
    
    row = cursor.fetchone()
    
    if row:
        # 已有關聯，返回用戶
        user_id = row['user_id']
        cursor.execute('SELECT * FROM auth_users WHERE id = ?', (user_id,))
        user = dict(cursor.fetchone())
        conn.close()
        return user
    
    # 查找是否有相同 email 的用戶
    if email:
        cursor.execute('SELECT * FROM auth_users WHERE email = ?', (email,))
        existing = cursor.fetchone()
        
        if existing:
            user = dict(existing)
            # 關聯社交帳號
            cursor.execute('''
                INSERT INTO social_accounts (user_id, provider, provider_user_id, email, display_name, avatar_url)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (user['id'], provider, provider_user_id, email, display_name, avatar_url))
            conn.commit()
            conn.close()
            return user
    
    # 創建新用戶
    import uuid
    user_uuid = str(uuid.uuid4())
    username = f"{provider}_{provider_user_id[:8]}"
    
    # 確保 username 唯一
    cursor.execute('SELECT id FROM auth_users WHERE username = ?', (username,))
    if cursor.fetchone():
        username = f"{provider}_{secrets.token_hex(4)}"
    
    cursor.execute('''
        INSERT INTO auth_users (uuid, username, email, password_hash, salt, display_name, avatar_url, is_verified, credits)
        VALUES (?, ?, ?, '', '', ?, ?, 1, 100)
    ''', (user_uuid, username, email, display_name, avatar_url))
    
    user_id = cursor.lastrowid
    
    # 關聯社交帳號
    cursor.execute('''
        INSERT INTO social_accounts (user_id, provider, provider_user_id, email, display_name, avatar_url)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (user_id, provider, provider_user_id, email, display_name, avatar_url))
    
    conn.commit()
    
    # 獲取完整用戶資料
    cursor.execute('SELECT * FROM auth_users WHERE id = ?', (user_id,))
    user = dict(cursor.fetchone())
    conn.close()
    
    return user

def create_jwt_token(user: Dict[str, Any]) -> str:
    """創建 JWT Token"""
    from auth_jwt import JWTManager, TokenPayload
    
    jwt_manager = JWTManager()
    payload = TokenPayload(
        user_id=user['id'],
        username=user['username'],
        email=user.get('email', ''),
        tier=user.get('tier', 'free')
    )
    return jwt_manager.create_token(payload)

# === Google OAuth ===
@router.get("/google/login")
async def google_login(redirect: str = "/dashboard"):
    """Google 登入"""
    if not GOOGLE_CLIENT_ID:
        raise HTTPException(status_code=503, detail="Google 登入尚未配置")
    
    state = generate_state()
    save_state(state, "google", redirect)
    
    params = {
        "client_id": GOOGLE_CLIENT_ID,
        "redirect_uri": GOOGLE_REDIRECT_URI,
        "response_type": "code",
        "scope": "openid email profile",
        "state": state,
        "access_type": "offline",
        "prompt": "select_account"
    }
    
    url = f"https://accounts.google.com/o/oauth2/v2/auth?{urlencode(params)}"
    return RedirectResponse(url)

@router.get("/google/callback")
async def google_callback(code: str = None, state: str = None, error: str = None):
    """Google 回調"""
    if error:
        return RedirectResponse(f"/login?error={error}")
    
    if not code or not state:
        return RedirectResponse("/login?error=invalid_request")
    
    redirect_url = verify_state(state, "google")
    if not redirect_url:
        return RedirectResponse("/login?error=invalid_state")
    
    try:
        # 用 code 換 token
        async with httpx.AsyncClient() as client:
            token_res = await client.post(
                "https://oauth2.googleapis.com/token",
                data={
                    "client_id": GOOGLE_CLIENT_ID,
                    "client_secret": GOOGLE_CLIENT_SECRET,
                    "code": code,
                    "grant_type": "authorization_code",
                    "redirect_uri": GOOGLE_REDIRECT_URI
                }
            )
            token_data = token_res.json()
            
            if "error" in token_data:
                return RedirectResponse(f"/login?error={token_data['error']}")
            
            # 用 token 取得用戶資料
            user_res = await client.get(
                "https://www.googleapis.com/oauth2/v2/userinfo",
                headers={"Authorization": f"Bearer {token_data['access_token']}"}
            )
            user_data = user_res.json()
        
        # 創建或更新用戶
        user = find_or_create_user(
            provider="google",
            provider_user_id=user_data["id"],
            email=user_data.get("email"),
            display_name=user_data.get("name"),
            avatar_url=user_data.get("picture")
        )
        
        # 創建 JWT
        token = create_jwt_token(user)
        
        # 設置 Cookie 並重定向
        response = RedirectResponse(redirect_url)
        response.set_cookie(
            key="auth_token",
            value=token,
            max_age=7*24*60*60,  # 7 天
            httponly=True,
            samesite="lax"
        )
        return response
        
    except Exception as e:
        print(f"[Google Auth] Error: {e}")
        return RedirectResponse(f"/login?error=auth_failed")

# === LINE Login ===
@router.get("/line/login")
async def line_login(redirect: str = "/dashboard"):
    """LINE 登入"""
    if not LINE_CHANNEL_ID:
        raise HTTPException(status_code=503, detail="LINE 登入尚未配置")
    
    state = generate_state()
    save_state(state, "line", redirect)
    
    params = {
        "response_type": "code",
        "client_id": LINE_CHANNEL_ID,
        "redirect_uri": LINE_REDIRECT_URI,
        "state": state,
        "scope": "profile openid email"
    }
    
    url = f"https://access.line.me/oauth2/v2.1/authorize?{urlencode(params)}"
    return RedirectResponse(url)

@router.get("/line/callback")
async def line_callback(code: str = None, state: str = None, error: str = None):
    """LINE 回調"""
    if error:
        return RedirectResponse(f"/login?error={error}")
    
    if not code or not state:
        return RedirectResponse("/login?error=invalid_request")
    
    redirect_url = verify_state(state, "line")
    if not redirect_url:
        return RedirectResponse("/login?error=invalid_state")
    
    try:
        async with httpx.AsyncClient() as client:
            # 用 code 換 token
            token_res = await client.post(
                "https://api.line.me/oauth2/v2.1/token",
                data={
                    "grant_type": "authorization_code",
                    "code": code,
                    "redirect_uri": LINE_REDIRECT_URI,
                    "client_id": LINE_CHANNEL_ID,
                    "client_secret": LINE_CHANNEL_SECRET
                }
            )
            token_data = token_res.json()
            
            if "error" in token_data:
                return RedirectResponse(f"/login?error={token_data['error']}")
            
            # 用 token 取得用戶資料
            user_res = await client.get(
                "https://api.line.me/v2/profile",
                headers={"Authorization": f"Bearer {token_data['access_token']}"}
            )
            user_data = user_res.json()
            
            # LINE 的 email 需要從 id_token 解碼
            email = None
            if "id_token" in token_data:
                import base64
                import json
                payload = token_data["id_token"].split(".")[1]
                payload += "=" * (4 - len(payload) % 4)
                id_token_data = json.loads(base64.urlsafe_b64decode(payload))
                email = id_token_data.get("email")
        
        # 創建或更新用戶
        user = find_or_create_user(
            provider="line",
            provider_user_id=user_data["userId"],
            email=email,
            display_name=user_data.get("displayName"),
            avatar_url=user_data.get("pictureUrl")
        )
        
        # 創建 JWT
        token = create_jwt_token(user)
        
        # 設置 Cookie 並重定向
        response = RedirectResponse(redirect_url)
        response.set_cookie(
            key="auth_token",
            value=token,
            max_age=7*24*60*60,
            httponly=True,
            samesite="lax"
        )
        return response
        
    except Exception as e:
        print(f"[LINE Auth] Error: {e}")
        return RedirectResponse(f"/login?error=auth_failed")

# === 社交帳號管理 ===
@router.get("/social-accounts")
async def get_social_accounts(request: Request):
    """獲取已連結的社交帳號"""
    from auth_jwt import get_user_id
    
    user_id = get_user_id(request)
    
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT provider, display_name, avatar_url, created_at 
        FROM social_accounts WHERE user_id = ?
    ''', (user_id,))
    
    accounts = [dict(row) for row in cursor.fetchall()]
    conn.close()
    
    return {"accounts": accounts}

@router.delete("/social-accounts/{provider}")
async def unlink_social_account(provider: str, request: Request):
    """取消連結社交帳號"""
    from auth_jwt import get_user_id
    
    user_id = get_user_id(request)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 確保用戶至少有密碼或另一個社交帳號
    cursor.execute('SELECT password_hash FROM auth_users WHERE id = ?', (user_id,))
    user = cursor.fetchone()
    
    cursor.execute('SELECT COUNT(*) FROM social_accounts WHERE user_id = ?', (user_id,))
    social_count = cursor.fetchone()[0]
    
    if not user[0] and social_count <= 1:
        conn.close()
        raise HTTPException(
            status_code=400, 
            detail="無法取消連結，請先設定密碼或連結其他社交帳號"
        )
    
    cursor.execute('''
        DELETE FROM social_accounts WHERE user_id = ? AND provider = ?
    ''', (user_id, provider))
    
    conn.commit()
    conn.close()
    
    return {"success": True, "message": f"已取消 {provider} 連結"}

# === 狀態檢查 ===
@router.get("/social-status")
async def social_status():
    """檢查社交登入配置狀態"""
    return {
        "google": bool(GOOGLE_CLIENT_ID),
        "line": bool(LINE_CHANNEL_ID),
        "facebook": False  # 未來支援
    }

print("✓ 社交登入模組已載入")
