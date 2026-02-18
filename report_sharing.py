"""
報告分享模組
report_sharing.py | @流祇 @璃語 | 2026-02-18
PYLIB: db_unified

功能：
- 生成分享連結
- 限時/限次分享
- 分享統計
"""
import sqlite3
import secrets
import hashlib
from datetime import datetime, timedelta
from typing import Optional
from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from pydantic import BaseModel

# === 配置 ===
DB_PATH = "beidou_unified.db"
BASE_URL = "https://beidou-mingshu.com"
SHARE_EXPIRE_DAYS = 7
MAX_VIEWS = 10

router = APIRouter(prefix="/api/share", tags=["sharing"])

# === 資料模型 ===
class CreateShareRequest(BaseModel):
    report_id: int
    expire_days: int = 7
    max_views: int = 10
    password: Optional[str] = None

# === 資料庫初始化 ===
def init_share_tables():
    """初始化分享表"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS report_shares (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            share_code TEXT UNIQUE NOT NULL,
            report_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            password_hash TEXT,
            expires_at TEXT,
            max_views INTEGER DEFAULT 10,
            view_count INTEGER DEFAULT 0,
            is_active INTEGER DEFAULT 1,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (report_id) REFERENCES reports(id),
            FOREIGN KEY (user_id) REFERENCES auth_users(id)
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS share_views (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            share_id INTEGER NOT NULL,
            viewer_ip TEXT,
            user_agent TEXT,
            viewed_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (share_id) REFERENCES report_shares(id)
        )
    ''')
    
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_share_code ON report_shares(share_code)')
    
    conn.commit()
    conn.close()

init_share_tables()

# === 工具函數 ===
def generate_share_code() -> str:
    """生成分享碼"""
    return secrets.token_urlsafe(12)

def hash_password(password: str) -> str:
    """哈希密碼"""
    return hashlib.sha256(password.encode()).hexdigest()

# === API 端點 ===
@router.post("/create")
async def create_share(req: CreateShareRequest, request: Request):
    """創建分享連結"""
    from auth_jwt import get_user_id
    
    user_id = get_user_id(request)
    share_code = generate_share_code()
    expires_at = (datetime.now() + timedelta(days=req.expire_days)).isoformat()
    password_hash = hash_password(req.password) if req.password else None
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 確認報告屬於該用戶
    cursor.execute('SELECT id FROM reports WHERE id = ? AND user_id = ?', 
                   (req.report_id, user_id))
    if not cursor.fetchone():
        conn.close()
        raise HTTPException(status_code=404, detail="報告不存在")
    
    cursor.execute('''
        INSERT INTO report_shares 
        (share_code, report_id, user_id, password_hash, expires_at, max_views)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (share_code, req.report_id, user_id, password_hash, expires_at, req.max_views))
    
    conn.commit()
    conn.close()
    
    share_url = f"{BASE_URL}/s/{share_code}"
    
    return {
        "success": True,
        "share_code": share_code,
        "share_url": share_url,
        "expires_at": expires_at,
        "max_views": req.max_views,
        "has_password": bool(req.password)
    }

@router.get("/my")
async def my_shares(request: Request):
    """查詢我的分享"""
    from auth_jwt import get_user_id
    
    user_id = get_user_id(request)
    
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT rs.*, r.report_type, r.name as report_name
        FROM report_shares rs
        JOIN reports r ON rs.report_id = r.id
        WHERE rs.user_id = ?
        ORDER BY rs.created_at DESC
    ''', (user_id,))
    
    shares = [dict(row) for row in cursor.fetchall()]
    conn.close()
    
    return {"shares": shares}

@router.delete("/{share_code}")
async def delete_share(share_code: str, request: Request):
    """刪除分享"""
    from auth_jwt import get_user_id
    
    user_id = get_user_id(request)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        UPDATE report_shares SET is_active = 0 
        WHERE share_code = ? AND user_id = ?
    ''', (share_code, user_id))
    
    if cursor.rowcount == 0:
        conn.close()
        raise HTTPException(status_code=404, detail="分享不存在")
    
    conn.commit()
    conn.close()
    
    return {"success": True, "message": "分享已刪除"}

@router.get("/stats/{share_code}")
async def share_stats(share_code: str, request: Request):
    """分享統計"""
    from auth_jwt import get_user_id
    
    user_id = get_user_id(request)
    
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT * FROM report_shares 
        WHERE share_code = ? AND user_id = ?
    ''', (share_code, user_id))
    
    share = cursor.fetchone()
    if not share:
        conn.close()
        raise HTTPException(status_code=404, detail="分享不存在")
    
    cursor.execute('''
        SELECT viewed_at FROM share_views 
        WHERE share_id = ? 
        ORDER BY viewed_at DESC LIMIT 10
    ''', (share['id'],))
    
    views = [row['viewed_at'] for row in cursor.fetchall()]
    conn.close()
    
    return {
        "share_code": share_code,
        "view_count": share['view_count'],
        "max_views": share['max_views'],
        "expires_at": share['expires_at'],
        "recent_views": views
    }

# === 分享頁面 ===
@router.get("/view/{share_code}", response_class=HTMLResponse)
async def view_shared_report(share_code: str, request: Request, pwd: str = None):
    """查看分享的報告"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM report_shares WHERE share_code = ? AND is_active = 1', 
                   (share_code,))
    share = cursor.fetchone()
    
    if not share:
        conn.close()
        return HTMLResponse('''
            <html><body style="font-family:sans-serif;text-align:center;padding:50px;">
            <h1>😔 分享連結不存在或已失效</h1>
            <p><a href="/">返回首頁</a></p>
            </body></html>
        ''', status_code=404)
    
    # 檢查過期
    if datetime.fromisoformat(share['expires_at']) < datetime.now():
        conn.close()
        return HTMLResponse('''
            <html><body style="font-family:sans-serif;text-align:center;padding:50px;">
            <h1>⏰ 分享連結已過期</h1>
            <p><a href="/">返回首頁</a></p>
            </body></html>
        ''', status_code=410)
    
    # 檢查瀏覽次數
    if share['view_count'] >= share['max_views']:
        conn.close()
        return HTMLResponse('''
            <html><body style="font-family:sans-serif;text-align:center;padding:50px;">
            <h1>👀 瀏覽次數已達上限</h1>
            <p><a href="/">返回首頁</a></p>
            </body></html>
        ''', status_code=410)
    
    # 檢查密碼
    if share['password_hash']:
        if not pwd or hash_password(pwd) != share['password_hash']:
            conn.close()
            return HTMLResponse(f'''
                <html>
                <head><script src="https://cdn.tailwindcss.com"></script></head>
                <body class="bg-gray-50 min-h-screen flex items-center justify-center">
                    <div class="bg-white p-8 rounded-xl shadow-lg max-w-md w-full">
                        <h1 class="text-xl font-bold mb-4">🔒 此報告需要密碼</h1>
                        <form method="get">
                            <input type="password" name="pwd" placeholder="請輸入密碼"
                                   class="w-full px-4 py-2 border rounded-lg mb-4">
                            <button type="submit" 
                                    class="w-full bg-purple-600 text-white py-2 rounded-lg">
                                確認
                            </button>
                        </form>
                    </div>
                </body>
                </html>
            ''')
    
    # 記錄瀏覽
    client_ip = request.client.host if request.client else "unknown"
    user_agent = request.headers.get("user-agent", "unknown")
    
    cursor.execute('''
        INSERT INTO share_views (share_id, viewer_ip, user_agent)
        VALUES (?, ?, ?)
    ''', (share['id'], client_ip, user_agent))
    
    cursor.execute('''
        UPDATE report_shares SET view_count = view_count + 1 
        WHERE id = ?
    ''', (share['id'],))
    
    # 獲取報告
    cursor.execute('SELECT * FROM reports WHERE id = ?', (share['report_id'],))
    report = cursor.fetchone()
    
    conn.commit()
    conn.close()
    
    if not report:
        return HTMLResponse('<h1>報告不存在</h1>', status_code=404)
    
    # 重定向到 PDF 或顯示報告
    return RedirectResponse(f"/api/reports/pdf/{report['id']}?share={share_code}")

print("✓ 報告分享模組已載入")
