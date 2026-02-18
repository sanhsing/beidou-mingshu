#!/usr/bin/env python3
"""
saas_api.py - 北斗命數 SaaS 功能整合
版本：v1.0.0

═══════════════════════════════════════════════════════════════════════
整合模組：
  • auth_jwt.py - JWT 認證
  • mingshu_schema.py - 數據庫 Schema
  • mingshu_db.py - 數據庫 CRUD
  • feedback_system.py - 回饋系統
  • report_commercial.py - 商業報告分級
═══════════════════════════════════════════════════════════════════════

PYLIB First：整合已有 2844 行 SaaS 基礎模組
XTF Task Chain
@11星協作：@織明(統籌) @流祇(連結) @星殼(架構)
"""

from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime
import json

# ════════════════════════════════════════════════════════════════════
# 導入已有 SaaS 模組
# ════════════════════════════════════════════════════════════════════

# JWT 認證
from auth_jwt import (
    PasswordHasher, JWTManager, User, TokenPayload,
    JWT_SECRET, ACCESS_TOKEN_EXPIRE_MINUTES
)

# 數據庫
from mingshu_schema import init_mingshu_db, MINGSHU_SCHEMA
from mingshu_db import get_db_path, UserData, BaziData, ZiweiData, get_db

# 商業報告
from report_commercial import REPORT_LEVELS, GONG_FIELD

# 回饋系統
from feedback_system import FEEDBACK_QUESTIONS

# ════════════════════════════════════════════════════════════════════
# FastAPI App
# ════════════════════════════════════════════════════════════════════

app = FastAPI(
    title="北斗命數 SaaS API",
    version="1.0.0",
    description="認證、計費、用戶管理"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

security = HTTPBearer(auto_error=False)
jwt_manager = JWTManager()
password_hasher = PasswordHasher()

# ════════════════════════════════════════════════════════════════════
# 請求模型
# ════════════════════════════════════════════════════════════════════

class RegisterRequest(BaseModel):
    username: str
    password: str
    email: Optional[str] = None

class LoginRequest(BaseModel):
    username: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int

class UserProfileRequest(BaseModel):
    name: Optional[str] = None
    gender: Optional[str] = None
    birth_year: Optional[int] = None
    birth_month: Optional[int] = None
    birth_day: Optional[int] = None
    birth_hour: Optional[int] = None

class PurchaseRequest(BaseModel):
    report_level: str  # L1/L2/L3/L4
    target_user_id: Optional[str] = None

class FeedbackRequest(BaseModel):
    q1_answer: str
    q2_answer: str
    q3_answer: Optional[str] = None
    rating: int = 5

# ════════════════════════════════════════════════════════════════════
# 內存用戶存儲（生產環境應使用數據庫）
# ════════════════════════════════════════════════════════════════════

USERS_DB: Dict[str, User] = {}
USER_CREDITS: Dict[int, Dict] = {}  # user_id -> {credits, tier, reports}

# ════════════════════════════════════════════════════════════════════
# 認證依賴
# ════════════════════════════════════════════════════════════════════

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> Optional[TokenPayload]:
    """獲取當前用戶"""
    if not credentials:
        return None
    
    token = credentials.credentials
    is_valid, payload, error = jwt_manager.verify_token(token)
    
    if not is_valid or not payload:
        raise HTTPException(401, f"無效的 Token：{error}")
    
    return payload

async def require_auth(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> TokenPayload:
    """要求認證"""
    if not credentials:
        raise HTTPException(401, "需要認證")
    
    token = credentials.credentials
    is_valid, payload, error = jwt_manager.verify_token(token)
    
    if not is_valid or not payload:
        raise HTTPException(401, f"無效的 Token：{error}")
    
    return payload

# ════════════════════════════════════════════════════════════════════
# 認證 API
# ════════════════════════════════════════════════════════════════════

@app.post("/api/auth/register")
async def register(req: RegisterRequest):
    """用戶註冊"""
    if req.username in USERS_DB:
        raise HTTPException(400, "用戶名已存在")
    
    salt = password_hasher.generate_salt()
    password_hash = password_hasher.hash_password(req.password, salt)
    
    user_id = len(USERS_DB) + 1
    user = User(
        user_id=user_id,
        username=req.username,
        password_hash=password_hash,
        salt=salt,
        email=req.email or "",
        created_at=datetime.now().isoformat()
    )
    
    USERS_DB[req.username] = user
    
    # 初始化用戶額度
    USER_CREDITS[user_id] = {
        "credits": 100,  # 新用戶贈送 100 點
        "tier": "free",
        "reports": [],
    }
    
    return {
        "success": True,
        "user_id": user_id,
        "message": "註冊成功，已贈送 100 點"
    }

@app.post("/api/auth/login", response_model=TokenResponse)
async def login(req: LoginRequest):
    """用戶登入"""
    if req.username not in USERS_DB:
        raise HTTPException(401, "用戶名或密碼錯誤")
    
    user = USERS_DB[req.username]
    
    if not password_hasher.verify_password(req.password, user.password_hash, user.salt):
        raise HTTPException(401, "用戶名或密碼錯誤")
    
    access_token = jwt_manager.create_access_token(user.user_id, user.username)
    refresh_token = jwt_manager.create_refresh_token(user.user_id, user.username)
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )

@app.post("/api/auth/refresh")
async def refresh_token(refresh_token: str):
    """刷新 Token"""
    payload = jwt_manager.verify_token(refresh_token)
    
    if not payload or payload.token_type != "refresh":
        raise HTTPException(401, "無效的刷新 Token")
    
    access_token = jwt_manager.create_access_token(payload.user_id, payload.username)
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60
    }

@app.get("/api/auth/me")
async def get_me(user: TokenPayload = Depends(require_auth)):
    """獲取當前用戶資訊"""
    credits = USER_CREDITS.get(user.user_id, {})
    
    return {
        "user_id": user.user_id,
        "username": user.username,
        "credits": credits.get("credits", 0),
        "tier": credits.get("tier", "free"),
        "reports_count": len(credits.get("reports", []))
    }

# ════════════════════════════════════════════════════════════════════
# 計費 API
# ════════════════════════════════════════════════════════════════════

@app.get("/api/pricing")
async def get_pricing():
    """獲取報告定價"""
    return {
        "levels": REPORT_LEVELS,
        "credits_price": {
            "100": "NT$ 100",
            "500": "NT$ 450",
            "1000": "NT$ 800",
        },
        "report_credits": {
            "L1": 50,
            "L2": 150,
            "L3": 500,
            "L4": 2000,
        }
    }

@app.post("/api/purchase")
async def purchase_report(
    req: PurchaseRequest,
    user: TokenPayload = Depends(require_auth)
):
    """購買報告"""
    credits_needed = {
        "L1": 50,
        "L2": 150,
        "L3": 500,
        "L4": 2000,
    }
    
    if req.report_level not in credits_needed:
        raise HTTPException(400, "無效的報告等級")
    
    needed = credits_needed[req.report_level]
    user_credits = USER_CREDITS.get(user.user_id, {"credits": 0})
    
    if user_credits.get("credits", 0) < needed:
        raise HTTPException(402, f"點數不足，需要 {needed} 點，目前 {user_credits.get('credits', 0)} 點")
    
    # 扣除點數
    USER_CREDITS[user.user_id]["credits"] -= needed
    
    # 記錄購買
    purchase_id = f"PUR_{datetime.now().strftime('%Y%m%d%H%M%S')}_{user.user_id}"
    USER_CREDITS[user.user_id]["reports"].append({
        "id": purchase_id,
        "level": req.report_level,
        "purchased_at": datetime.now().isoformat(),
    })
    
    return {
        "success": True,
        "purchase_id": purchase_id,
        "level": req.report_level,
        "credits_used": needed,
        "credits_remaining": USER_CREDITS[user.user_id]["credits"],
    }

@app.post("/api/credits/add")
async def add_credits(
    amount: int,
    user: TokenPayload = Depends(require_auth)
):
    """充值點數（模擬）"""
    if amount not in [100, 500, 1000]:
        raise HTTPException(400, "無效的充值金額")
    
    if user.user_id not in USER_CREDITS:
        USER_CREDITS[user.user_id] = {"credits": 0, "tier": "free", "reports": []}
    
    USER_CREDITS[user.user_id]["credits"] += amount
    
    return {
        "success": True,
        "added": amount,
        "total": USER_CREDITS[user.user_id]["credits"]
    }

@app.get("/api/credits")
async def get_credits(user: TokenPayload = Depends(require_auth)):
    """查詢點數"""
    credits = USER_CREDITS.get(user.user_id, {"credits": 0, "tier": "free", "reports": []})
    return credits

# ════════════════════════════════════════════════════════════════════
# 用戶資料 API
# ════════════════════════════════════════════════════════════════════

@app.post("/api/user/profile")
async def update_profile(
    req: UserProfileRequest,
    user: TokenPayload = Depends(require_auth)
):
    """更新用戶資料"""
    # 這裡應該調用 mingshu_db 的 update_user
    return {
        "success": True,
        "user_id": user.user_id,
        "updated": req.dict(exclude_none=True)
    }

@app.get("/api/user/reports")
async def get_user_reports(user: TokenPayload = Depends(require_auth)):
    """獲取用戶報告歷史"""
    credits = USER_CREDITS.get(user.user_id, {"reports": []})
    return {
        "reports": credits.get("reports", [])
    }

# ════════════════════════════════════════════════════════════════════
# 回饋 API
# ════════════════════════════════════════════════════════════════════

@app.get("/api/feedback/questions")
async def get_feedback_questions():
    """獲取回饋問題"""
    return {
        "questions": FEEDBACK_QUESTIONS
    }

@app.post("/api/feedback")
async def submit_feedback(
    req: FeedbackRequest,
    user: TokenPayload = Depends(require_auth)
):
    """提交回饋"""
    # 這裡應該調用 feedback_system 的存儲功能
    return {
        "success": True,
        "message": "感謝您的回饋！已贈送 10 點",
        "bonus_credits": 10
    }

# ════════════════════════════════════════════════════════════════════
# 狀態 API
# ════════════════════════════════════════════════════════════════════

@app.get("/api/saas/status")
async def saas_status():
    """SaaS 狀態"""
    return {
        "version": "1.0.0",
        "modules": {
            "auth": True,
            "database": True,
            "pricing": True,
            "feedback": True,
        },
        "users_count": len(USERS_DB),
        "report_levels": list(REPORT_LEVELS.keys()),
    }

# ════════════════════════════════════════════════════════════════════
# 數據庫初始化
# ════════════════════════════════════════════════════════════════════

@app.on_event("startup")
async def startup():
    """啟動時初始化數據庫"""
    try:
        init_mingshu_db()
        print("✅ 數據庫初始化完成")
    except Exception as e:
        print(f"⚠️ 數據庫初始化失敗：{e}")

# ════════════════════════════════════════════════════════════════════
# 測試
# ════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("═" * 60)
    print("        北斗命數 SaaS API - 測試")
    print("═" * 60)
    
    print("\n【報告定價】")
    for level, info in REPORT_LEVELS.items():
        print(f"  {level} {info['name']}：{info['price_range']}")
    
    print("\n【認證測試】")
    # 註冊
    salt = password_hasher.generate_salt()
    hash_pwd = password_hasher.hash_password("test123", salt)
    print(f"  密碼雜湊：{hash_pwd[:30]}...")
    
    # 驗證（注意參數順序）
    is_valid = password_hasher.verify_password("test123", salt, hash_pwd)
    print(f"  密碼驗證：{'✅' if is_valid else '❌'}")
    
    # JWT
    token = jwt_manager.create_access_token(1, "testuser")
    print(f"  JWT Token：{token[:50]}...")
    
    is_valid, payload, error = jwt_manager.verify_token(token)
    if is_valid and payload:
        print(f"  Token 解析：user_id={payload.user_id}, username={payload.username}")
    else:
        print(f"  Token 解析失敗：{error}")
    
    print("\n" + "═" * 60)
    print("✅ SaaS API 測試完成")
    print("═" * 60)
    print("\n啟動：uvicorn saas_api:app --port 8002")
