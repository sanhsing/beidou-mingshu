"""
用戶設定 API
user_settings_api.py | @星殼 | 2026-02-17
PYLIB: auth_jwt, db_unified
"""
from fastapi import APIRouter, Request, Depends, HTTPException, Form
from fastapi.responses import JSONResponse
from pydantic import BaseModel, EmailStr
from typing import Optional
import sqlite3
from datetime import datetime
import hashlib

router = APIRouter(prefix="/api/user", tags=["user-settings"])

DB_PATH = 'beidou_unified.db'

# === Pydantic Models ===
class ProfileUpdate(BaseModel):
    nickname: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    birth_year: Optional[int] = None
    birth_month: Optional[int] = None
    birth_day: Optional[int] = None
    birth_hour: Optional[int] = None
    gender: Optional[str] = None

class PasswordChange(BaseModel):
    old_password: str
    new_password: str
    confirm_password: str

class NotificationSettings(BaseModel):
    email_marketing: bool = True
    email_report: bool = True
    email_reminder: bool = True
    push_enabled: bool = False

# === 輔助函數 ===
def get_user_id(request: Request) -> int:
    """從請求獲取用戶ID (TODO: 整合 JWT)"""
    # 暫時硬編碼，實際應從 JWT 獲取
    return 1

def hash_password(password: str) -> str:
    """密碼哈希"""
    return hashlib.sha256(password.encode()).hexdigest()

# === API 端點 ===

@router.get("/profile")
async def get_profile(request: Request):
    """
    A3.2: GET /api/user/profile
    獲取用戶個人資料
    """
    user_id = get_user_id(request)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            SELECT id, username, email, nickname, phone, 
                   birth_year, birth_month, birth_day, birth_hour,
                   gender, credits, created_at
            FROM users WHERE id = ?
        ''', (user_id,))
        
        row = cursor.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="用戶不存在")
        
        columns = ['id', 'username', 'email', 'nickname', 'phone',
                   'birth_year', 'birth_month', 'birth_day', 'birth_hour',
                   'gender', 'credits', 'created_at']
        
        profile = dict(zip(columns, row))
        # 移除敏感欄位
        profile.pop('id', None)
        
        return {"success": True, "profile": profile}
        
    finally:
        conn.close()


@router.put("/profile")
async def update_profile(request: Request, data: ProfileUpdate):
    """
    A3.3: PUT /api/user/profile
    更新用戶個人資料
    """
    user_id = get_user_id(request)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # 構建更新語句
        updates = []
        values = []
        
        if data.nickname is not None:
            updates.append("nickname = ?")
            values.append(data.nickname)
        if data.email is not None:
            updates.append("email = ?")
            values.append(data.email)
        if data.phone is not None:
            updates.append("phone = ?")
            values.append(data.phone)
        if data.birth_year is not None:
            updates.append("birth_year = ?")
            values.append(data.birth_year)
        if data.birth_month is not None:
            updates.append("birth_month = ?")
            values.append(data.birth_month)
        if data.birth_day is not None:
            updates.append("birth_day = ?")
            values.append(data.birth_day)
        if data.birth_hour is not None:
            updates.append("birth_hour = ?")
            values.append(data.birth_hour)
        if data.gender is not None:
            updates.append("gender = ?")
            values.append(data.gender)
        
        if not updates:
            return {"success": True, "message": "無需更新"}
        
        updates.append("updated_at = ?")
        values.append(datetime.now().isoformat())
        values.append(user_id)
        
        sql = f"UPDATE users SET {', '.join(updates)} WHERE id = ?"
        cursor.execute(sql, values)
        conn.commit()
        
        return {"success": True, "message": "資料已更新"}
        
    finally:
        conn.close()


@router.post("/password")
async def change_password(request: Request, data: PasswordChange):
    """
    A3.4: POST /api/user/password
    修改密碼
    """
    user_id = get_user_id(request)
    
    # 驗證新密碼
    if data.new_password != data.confirm_password:
        raise HTTPException(status_code=400, detail="新密碼與確認密碼不一致")
    
    if len(data.new_password) < 8:
        raise HTTPException(status_code=400, detail="密碼長度至少 8 個字元")
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # 驗證舊密碼
        cursor.execute('SELECT password_hash FROM users WHERE id = ?', (user_id,))
        row = cursor.fetchone()
        
        if not row:
            raise HTTPException(status_code=404, detail="用戶不存在")
        
        if row[0] != hash_password(data.old_password):
            raise HTTPException(status_code=400, detail="舊密碼不正確")
        
        # 更新密碼
        new_hash = hash_password(data.new_password)
        cursor.execute('''
            UPDATE users SET password_hash = ?, updated_at = ? WHERE id = ?
        ''', (new_hash, datetime.now().isoformat(), user_id))
        
        conn.commit()
        
        return {"success": True, "message": "密碼已更新"}
        
    finally:
        conn.close()


@router.get("/notifications")
async def get_notifications(request: Request):
    """
    獲取通知設定
    """
    user_id = get_user_id(request)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            SELECT email_marketing, email_report, email_reminder, push_enabled
            FROM user_settings WHERE user_id = ?
        ''', (user_id,))
        
        row = cursor.fetchone()
        
        if row:
            settings = {
                'email_marketing': bool(row[0]),
                'email_report': bool(row[1]),
                'email_reminder': bool(row[2]),
                'push_enabled': bool(row[3])
            }
        else:
            # 返回預設值
            settings = {
                'email_marketing': True,
                'email_report': True,
                'email_reminder': True,
                'push_enabled': False
            }
        
        return {"success": True, "settings": settings}
        
    except:
        # 表可能不存在，返回預設值
        return {"success": True, "settings": {
            'email_marketing': True,
            'email_report': True,
            'email_reminder': True,
            'push_enabled': False
        }}
    finally:
        conn.close()


@router.put("/notifications")
async def update_notifications(request: Request, data: NotificationSettings):
    """
    A3.5: PUT /api/user/notifications
    更新通知設定
    """
    user_id = get_user_id(request)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # 確保表存在
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_settings (
                user_id INTEGER PRIMARY KEY,
                email_marketing INTEGER DEFAULT 1,
                email_report INTEGER DEFAULT 1,
                email_reminder INTEGER DEFAULT 1,
                push_enabled INTEGER DEFAULT 0,
                updated_at TEXT
            )
        ''')
        
        # 插入或更新
        cursor.execute('''
            INSERT INTO user_settings (user_id, email_marketing, email_report, email_reminder, push_enabled, updated_at)
            VALUES (?, ?, ?, ?, ?, ?)
            ON CONFLICT(user_id) DO UPDATE SET
                email_marketing = ?,
                email_report = ?,
                email_reminder = ?,
                push_enabled = ?,
                updated_at = ?
        ''', (
            user_id, 
            int(data.email_marketing), int(data.email_report), 
            int(data.email_reminder), int(data.push_enabled),
            datetime.now().isoformat(),
            int(data.email_marketing), int(data.email_report),
            int(data.email_reminder), int(data.push_enabled),
            datetime.now().isoformat()
        ))
        
        conn.commit()
        
        return {"success": True, "message": "通知設定已更新"}
        
    finally:
        conn.close()


@router.delete("/account")
async def delete_account(request: Request, password: str = Form(...)):
    """
    刪除帳號
    """
    user_id = get_user_id(request)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # 驗證密碼
        cursor.execute('SELECT password_hash FROM users WHERE id = ?', (user_id,))
        row = cursor.fetchone()
        
        if not row or row[0] != hash_password(password):
            raise HTTPException(status_code=400, detail="密碼不正確")
        
        # 軟刪除 (標記為已刪除)
        cursor.execute('''
            UPDATE users SET 
                status = 'deleted',
                email = CONCAT('deleted_', id, '_', email),
                updated_at = ?
            WHERE id = ?
        ''', (datetime.now().isoformat(), user_id))
        
        conn.commit()
        
        return {"success": True, "message": "帳號已刪除"}
        
    finally:
        conn.close()
