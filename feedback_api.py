#!/usr/bin/env python3
"""
feedback_api.py - 回饋系統 API 端點
北斗命數 v3.1.1

提供：
1. POST /api/v1/feedback - 提交回饋
2. GET /api/v1/feedback/stats - 回饋統計（需認證）
3. GET /feedback - 回饋表單頁面

@流祇
"""

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse, FileResponse
from pydantic import BaseModel
from typing import Optional
import os

from feedback_system import (
    FeedbackEntry, 
    init_feedback_db, 
    save_feedback, 
    get_feedback_stats,
    get_all_feedback,
    generate_feedback_report,
    FEEDBACK_DB_PATH
)

# 創建路由
router = APIRouter()

# 初始化資料庫
init_feedback_db()

# ============================================================
# 請求模型
# ============================================================

class FeedbackRequest(BaseModel):
    """回饋請求"""
    client_name: str = "匿名"
    service_level: str = ""
    session_id: str = ""
    
    # 核心 3 問
    most_impactful: str
    new_perspective: str
    improvement: str
    
    # 可選
    would_return: str = ""
    would_recommend: str = ""
    overall_rating: int = 0

class FeedbackResponse(BaseModel):
    """回饋響應"""
    success: bool
    message: str
    feedback_id: str = ""

# ============================================================
# API 端點
# ============================================================

@router.post("/api/v1/feedback", response_model=FeedbackResponse)
async def submit_feedback(request: Request, feedback: FeedbackRequest):
    """
    提交回饋
    
    POST /api/v1/feedback
    
    Request Body:
    {
        "client_name": "用戶名",
        "service_level": "L1/L2/L3/L4",
        "most_impactful": "最有感的一句話",
        "new_perspective": "新角度理解",
        "improvement": "改進建議",
        "would_return": "非常願意/願意/考慮中/不需要",
        "would_recommend": "非常願意/願意/考慮中/不會",
        "overall_rating": 1-5
    }
    """
    try:
        # 取得客戶端資訊
        client_ip = request.client.host if request.client else ""
        user_agent = request.headers.get("user-agent", "")
        
        # 創建回饋條目
        entry = FeedbackEntry(
            session_id=feedback.session_id,
            client_name=feedback.client_name,
            service_level=feedback.service_level,
            most_impactful=feedback.most_impactful,
            new_perspective=feedback.new_perspective,
            improvement=feedback.improvement,
            would_return=feedback.would_return,
            would_recommend=feedback.would_recommend,
            overall_rating=feedback.overall_rating,
            client_ip=client_ip,
            user_agent=user_agent[:200] if user_agent else "",
        )
        
        # 儲存
        success = save_feedback(entry)
        
        if success:
            return FeedbackResponse(
                success=True,
                message="感謝你的回饋！",
                feedback_id=entry.id
            )
        else:
            raise HTTPException(500, "儲存失敗")
            
    except Exception as e:
        raise HTTPException(400, str(e))

@router.get("/api/v1/feedback/stats")
async def get_stats(key: str = ""):
    """
    取得回饋統計
    
    GET /api/v1/feedback/stats?key=admin_key
    
    需要管理員金鑰
    """
    # 簡易認證（生產環境應使用更安全的方式）
    admin_key = os.environ.get("FEEDBACK_ADMIN_KEY", "beidou_admin_2026")
    
    if key != admin_key:
        raise HTTPException(403, "需要管理員權限")
    
    stats = get_feedback_stats()
    
    return {
        "success": True,
        "stats": stats,
    }

@router.get("/api/v1/feedback/list")
async def list_feedback(key: str = "", limit: int = 50):
    """
    列出回饋（需認證）
    
    GET /api/v1/feedback/list?key=admin_key&limit=50
    """
    admin_key = os.environ.get("FEEDBACK_ADMIN_KEY", "beidou_admin_2026")
    
    if key != admin_key:
        raise HTTPException(403, "需要管理員權限")
    
    feedbacks = get_all_feedback(limit=limit)
    
    return {
        "success": True,
        "count": len(feedbacks),
        "feedbacks": feedbacks,
    }

@router.get("/api/v1/feedback/report", response_class=HTMLResponse)
async def get_report(key: str = ""):
    """
    生成回饋報告
    
    GET /api/v1/feedback/report?key=admin_key
    """
    admin_key = os.environ.get("FEEDBACK_ADMIN_KEY", "beidou_admin_2026")
    
    if key != admin_key:
        raise HTTPException(403, "需要管理員權限")
    
    report = generate_feedback_report()
    
    # 轉換為 HTML
    html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>回饋報告 | 北斗命數</title>
    <style>
        body {{
            font-family: 'Courier New', monospace;
            background: #1E3A5F;
            color: #E0E0E0;
            padding: 40px;
            line-height: 1.6;
        }}
        pre {{
            white-space: pre-wrap;
            font-size: 14px;
        }}
    </style>
</head>
<body>
<pre>{report}</pre>
</body>
</html>
"""
    return HTMLResponse(content=html)

# ============================================================
# 頁面路由
# ============================================================

@router.get("/feedback", response_class=HTMLResponse)
async def feedback_page():
    """回饋表單頁面"""
    html_path = os.path.join(os.path.dirname(__file__), "frontend", "feedback.html")
    
    if os.path.exists(html_path):
        with open(html_path, "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    else:
        return HTMLResponse(content="""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>回饋 | 北斗命數</title>
</head>
<body style="font-family: sans-serif; text-align: center; padding: 50px;">
    <h1>回饋頁面載入中...</h1>
    <p>如果持續看到此訊息，請聯繫管理員。</p>
</body>
</html>
""")

# ============================================================
# 工具函數
# ============================================================

def register_feedback_routes(app):
    """註冊回饋路由到主應用"""
    app.include_router(router, tags=["feedback"])
    print("✅ 回饋系統路由已註冊")
