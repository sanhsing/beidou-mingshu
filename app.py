#!/usr/bin/env python3
"""
app.py - 北斗命數統一入口
版本：v1.0.0

═══════════════════════════════════════════════════════════════════════
XTF8 結構：
  L0: 配置載入
  L1: 應用初始化
  L2: 路由整合
  L3: 中間件
  L4: 啟動
═══════════════════════════════════════════════════════════════════════

XTF Task Chain: A2 (🔴 瓶頸點 1)
@11星協作：@織明(統籌) @星殼(架構) @流祇(連結)
確定度：★★★★☆
"""

import os
import sys
import time
import logging
from datetime import datetime
from contextlib import asynccontextmanager
from typing import Optional

from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

# 載入配置
from config import settings, get_settings, REPORT_PLANS, CREDIT_PLANS

# ════════════════════════════════════════════════════════════════════
# Sentry 錯誤追蹤 (可選)
# ════════════════════════════════════════════════════════════════════
SENTRY_DSN = os.getenv("SENTRY_DSN", "")
if SENTRY_DSN:
    try:
        import sentry_sdk
        from sentry_sdk.integrations.fastapi import FastApiIntegration
        from sentry_sdk.integrations.starlette import StarletteIntegration
        
        sentry_sdk.init(
            dsn=SENTRY_DSN,
            integrations=[
                StarletteIntegration(),
                FastApiIntegration(),
            ],
            traces_sample_rate=0.1,  # 10% 性能追蹤
            environment=os.getenv("ENVIRONMENT", "production"),
            release=f"beidou-mingshu@{settings.app.APP_VERSION}",
        )
        print("✅ Sentry 錯誤追蹤已啟用")
    except ImportError:
        print("⚠️ Sentry SDK 未安裝，跳過錯誤追蹤")

# ════════════════════════════════════════════════════════════════════
# L0: 日誌配置
# ════════════════════════════════════════════════════════════════════

logging.basicConfig(
    level=logging.DEBUG if settings.app.DEBUG else logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("beidou")

# ════════════════════════════════════════════════════════════════════
# L1: 應用初始化
# ════════════════════════════════════════════════════════════════════

@asynccontextmanager
async def lifespan(app: FastAPI):
    """應用生命週期"""
    # 啟動
    logger.info("=" * 60)
    logger.info(f"🌟 {settings.app.APP_NAME} v{settings.app.APP_VERSION} 啟動中...")
    logger.info(f"   環境: {settings.app.ENV}")
    logger.info(f"   DEBUG: {settings.app.DEBUG}")
    logger.info(f"   DB: {settings.db.DB_PATH}")
    logger.info("=" * 60)
    
    yield
    
    # 關閉
    logger.info("👋 服務關閉")

app = FastAPI(
    title=settings.app.APP_NAME,
    version=settings.app.APP_VERSION,
    description="個人化決策框架生成系統 | 命理分析 × 科技",
    docs_url="/docs" if settings.app.DEBUG else None,
    redoc_url="/redoc" if settings.app.DEBUG else None,
    lifespan=lifespan,
)

# ════════════════════════════════════════════════════════════════════
# L2: 中間件
# ════════════════════════════════════════════════════════════════════

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors.ALLOW_ORIGINS,
    allow_credentials=settings.cors.ALLOW_CREDENTIALS,
    allow_methods=settings.cors.ALLOW_METHODS,
    allow_headers=settings.cors.ALLOW_HEADERS,
)

# GA4 自動注入（如果設定了 GA4_ID）
GA4_ID = os.getenv('GA4_ID', '')
if GA4_ID:
    try:
        from middleware.analytics import GA4Middleware
        app.add_middleware(GA4Middleware)
        print(f"✅ GA4 追蹤已啟用: {GA4_ID}")
    except ImportError:
        print("⚠️ GA4 中間件載入失敗")

# 請求日誌
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = (time.time() - start_time) * 1000
    
    # 只記錄 API 請求
    if request.url.path.startswith("/api"):
        logger.info(
            f"{request.method} {request.url.path} "
            f"→ {response.status_code} ({process_time:.1f}ms)"
        )
    
    response.headers["X-Process-Time"] = f"{process_time:.1f}ms"
    return response

# 全局錯誤處理
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": exc.detail,
            "status_code": exc.status_code,
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    logger.error(f"未處理錯誤: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": "內部伺服器錯誤" if not settings.app.DEBUG else str(exc),
            "status_code": 500,
        }
    )

# ════════════════════════════════════════════════════════════════════
# L3: 路由整合
# ════════════════════════════════════════════════════════════════════

# ─────────────────────────────────────────────────────────────────────
# 3.1 數據庫 & 認證 API (from db_unified)
# ─────────────────────────────────────────────────────────────────────
try:
    from db_unified import (
        UnifiedDB, 
        create_token, 
        verify_token,
        get_current_user,
        require_auth,
    )
    from db_unified import app as db_app
    
    # 複製路由
    for route in db_app.routes:
        if hasattr(route, 'path') and route.path.startswith('/api'):
            app.routes.append(route)
    
    logger.info("✅ 數據庫 & 認證 API 載入")
except ImportError as e:
    logger.warning(f"⚠️ 數據庫 API 載入失敗: {e}")

# ─────────────────────────────────────────────────────────────────────
# 3.2 命理 API (from main_api)
# ─────────────────────────────────────────────────────────────────────
try:
    from main_api import app as mingshu_app
    
    # 複製路由（排除重複）
    existing_paths = {r.path for r in app.routes if hasattr(r, 'path')}
    for route in mingshu_app.routes:
        if hasattr(route, 'path') and route.path.startswith('/api'):
            if route.path not in existing_paths:
                app.routes.append(route)
    
    logger.info("✅ 命理 API 載入")
except ImportError as e:
    logger.warning(f"⚠️ 命理 API 載入失敗: {e}")

# ─────────────────────────────────────────────────────────────────────
# 3.3 PDF 報告 API (from pdf_report_api)
# ─────────────────────────────────────────────────────────────────────
try:
    from pdf_report_api import app as pdf_app
    
    existing_paths = {r.path for r in app.routes if hasattr(r, 'path')}
    for route in pdf_app.routes:
        if hasattr(route, 'path') and route.path.startswith('/api'):
            if route.path not in existing_paths:
                app.routes.append(route)
    
    logger.info("✅ PDF 報告 API 載入")
except ImportError as e:
    logger.warning(f"⚠️ PDF API 載入失敗: {e}")

# ─────────────────────────────────────────────────────────────────────
# 3.4 支付 API (from payment_service)
# ─────────────────────────────────────────────────────────────────────
try:
    from payment_service import app as payment_app
    
    existing_paths = {r.path for r in app.routes if hasattr(r, 'path')}
    for route in payment_app.routes:
        if hasattr(route, 'path') and route.path.startswith('/api'):
            if route.path not in existing_paths:
                app.routes.append(route)
    
    logger.info("✅ 支付 API 載入")
except ImportError as e:
    logger.warning(f"⚠️ 支付 API 載入失敗: {e}")

# ─────────────────────────────────────────────────────────────────────
# 3.5 前端頁面 (from frontend_app)
# ─────────────────────────────────────────────────────────────────────
try:
    from frontend_app import app as frontend
    from frontend_app import (
        render_page, 
        render_navbar,
        COMMON_STYLES,
        COMMON_JS,
    )
    
    # 複製前端路由
    for route in frontend.routes:
        if hasattr(route, 'path'):
            path = route.path
            # 排除 API 和內建路由
            if not path.startswith('/api') and not path.startswith('/openapi') and not path.startswith('/docs'):
                existing_paths = {r.path for r in app.routes if hasattr(r, 'path')}
                if path not in existing_paths:
                    app.routes.append(route)
    
    logger.info("✅ 前端頁面載入")
except ImportError as e:
    logger.warning(f"⚠️ 前端載入失敗: {e}")
    
    # 基本首頁
    @app.get("/", response_class=HTMLResponse)
    async def fallback_home():
        return """
        <!DOCTYPE html>
        <html><head><title>北斗命數</title></head>
        <body style="font-family:sans-serif;text-align:center;padding:50px;">
            <h1>🌟 北斗命數</h1>
            <p>個人化決策框架生成系統</p>
            <p><a href="/docs">API 文檔</a></p>
        </body></html>
        """

# ════════════════════════════════════════════════════════════════════
# L4: 核心端點
# ════════════════════════════════════════════════════════════════════

@app.get("/api/status")
async def system_status():
    """系統狀態"""
    try:
        from db_unified import UnifiedDB
        db = UnifiedDB()
        stats = db.get_stats()
    except:
        stats = {}
    
    return {
        "success": True,
        "status": "running",
        "app": settings.app.APP_NAME,
        "version": settings.app.APP_VERSION,
        "env": settings.app.ENV,
        "debug": settings.app.DEBUG,
        "timestamp": datetime.now().isoformat(),
        "stats": stats,
    }

@app.get("/api/health")
async def health_check():
    """健康檢查"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.get("/api/config/plans")
async def get_plans():
    """獲取定價方案"""
    return {
        "report_plans": REPORT_PLANS,
        "credit_plans": CREDIT_PLANS,
    }

# ════════════════════════════════════════════════════════════════════
# L5: 靜態文件
# ════════════════════════════════════════════════════════════════════

FRONTEND_DIR = os.path.join(os.path.dirname(__file__), "frontend")
if os.path.exists(FRONTEND_DIR):
    app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")
    logger.info(f"✅ 靜態文件: {FRONTEND_DIR}")

# ════════════════════════════════════════════════════════════════════
# 啟動
# ════════════════════════════════════════════════════════════════════

def get_all_routes():
    """獲取所有路由"""
    routes = []
    for route in app.routes:
        if hasattr(route, 'path') and hasattr(route, 'methods'):
            methods = list(route.methods - {'HEAD', 'OPTIONS'})
            if methods:
                routes.append((methods[0], route.path))
    return sorted(routes, key=lambda x: x[1])

if __name__ == "__main__":
    import uvicorn
    
    print("\n" + "═" * 60)
    print(f"  🌟 {settings.app.APP_NAME} v{settings.app.APP_VERSION}")
    print("═" * 60)
    
    # 列出所有路由
    routes = get_all_routes()
    print(f"\n📡 API 端點 ({len(routes)} 個):")
    for method, path in routes:
        if path.startswith('/api'):
            print(f"  {method:6} {path}")
    
    print(f"\n🌐 啟動服務...")
    print(f"   地址: http://{settings.app.HOST}:{settings.app.PORT}")
    print(f"   文檔: http://{settings.app.HOST}:{settings.app.PORT}/docs")
    print("═" * 60 + "\n")
    
    uvicorn.run(
        "app:app",
        host=settings.app.HOST,
        port=settings.app.PORT,
        reload=settings.app.DEBUG,
        workers=settings.app.WORKERS if not settings.app.DEBUG else 1,
    )

# === 新增模組整合 (M1-M3) ===
try:
    from legal_routes import router as legal_router
    app.include_router(legal_router)
    print("✓ 法律頁面路由已載入")
except Exception as e:
    print(f"⚠ 法律頁面路由載入失敗: {e}")

try:
    from landing_page import router as landing_router
    # 用新落地頁替換舊首頁
    @app.get("/", response_class=HTMLResponse, include_in_schema=False)
    async def home_redirect():
        from landing_page import LANDING_HTML
        return LANDING_HTML
    print("✓ 落地頁路由已載入")
except Exception as e:
    print(f"⚠ 落地頁路由載入失敗: {e}")

try:
    from free_trial import router as free_router
    app.include_router(free_router)
    print("✓ 免費試算路由已載入")
except Exception as e:
    print(f"⚠ 免費試算路由載入失敗: {e}")

try:
    from auth_pages import router as auth_pages_router
    app.include_router(auth_pages_router)
    print("✓ 認證頁面路由已載入")
except Exception as e:
    print(f"⚠ 認證頁面路由載入失敗: {e}")

# === Phase 2 模組整合 (M4, M7, M12) ===
try:
    from pricing_page import router as pricing_router
    app.include_router(pricing_router)
    print("✓ 定價頁路由已載入")
except Exception as e:
    print(f"⚠ 定價頁路由載入失敗: {e}")

try:
    from faq_page import router as faq_router
    app.include_router(faq_router)
    print("✓ FAQ 路由已載入")
except Exception as e:
    print(f"⚠ FAQ 路由載入失敗: {e}")

try:
    from email_service import email_service
    print("✓ Email 服務已載入")
except Exception as e:
    print(f"⚠ Email 服務載入失敗: {e}")

# === Phase 2-3 模組整合 (M5, M6, M8, M10) ===
try:
    from dashboard_v2 import router as dashboard_router
    app.include_router(dashboard_router)
    print("✓ 儀表板 v2 路由已載入")
except Exception as e:
    print(f"⚠ 儀表板載入失敗: {e}")

try:
    from membership_service import membership_service
    print("✓ 會員服務已載入")
except Exception as e:
    print(f"⚠ 會員服務載入失敗: {e}")

try:
    from health_check import router as health_router
    app.include_router(health_router)
    print("✓ 健康檢查路由已載入")
except Exception as e:
    print(f"⚠ 健康檢查載入失敗: {e}")

# === 商業閉環模組整合 (P0) ===
try:
    from checkout import router as checkout_router
    app.include_router(checkout_router)
    print("✓ 購買頁路由已載入")
except Exception as e:
    print(f"⚠ 購買頁載入失敗: {e}")

try:
    from credits_api import router as credits_router
    app.include_router(credits_router)
    print("✓ 點數API路由已載入")
except Exception as e:
    print(f"⚠ 點數API載入失敗: {e}")

try:
    from password_api import router as password_router
    app.include_router(password_router)
    print("✓ 密碼管理API已載入")
except Exception as e:
    print(f"⚠ 密碼管理API載入失敗: {e}")

try:
    from payment_flow import OrderService, ECPayService
    print("✓ 支付流程模組已載入")
except Exception as e:
    print(f"⚠ 支付流程載入失敗: {e}")

# === 剩餘 10% 補完 ===
try:
    from membership_page import router as membership_page_router
    app.include_router(membership_page_router)
    print("✓ 會員管理頁路由已載入")
except Exception as e:
    print(f"⚠ 會員管理頁載入失敗: {e}")

try:
    from matching_page import router as matching_page_router
    app.include_router(matching_page_router)
    print("✓ 合婚配對頁路由已載入")
except Exception as e:
    print(f"⚠ 合婚配對頁載入失敗: {e}")

# === XTF Task Chain Phase 1 模組 ===
try:
    from about_page import router as about_router
    app.include_router(about_router)
    print("✓ 關於頁路由已載入")
except Exception as e:
    print(f"⚠ 關於頁載入失敗: {e}")

try:
    from error_pages import router as error_router
    app.include_router(error_router)
    print("✓ 錯誤頁路由已載入")
except Exception as e:
    print(f"⚠ 錯誤頁載入失敗: {e}")

try:
    from user_settings_api import router as user_settings_router
    app.include_router(user_settings_router)
    print("✓ 用戶設定API已載入")
except Exception as e:
    print(f"⚠ 用戶設定API載入失敗: {e}")

try:
    from admin_stats_api import router as admin_stats_router
    app.include_router(admin_stats_router)
    print("✓ 管理統計API已載入")
except Exception as e:
    print(f"⚠ 管理統計API載入失敗: {e}")

try:
    from coupon_service import router as coupon_router
    app.include_router(coupon_router)
    print("✓ 優惠券服務已載入")
except Exception as e:
    print(f"⚠ 優惠券服務載入失敗: {e}")

try:
    from invoice_service import router as invoice_router
    app.include_router(invoice_router)
    print("✓ 發票服務已載入")
except Exception as e:
    print(f"⚠ 發票服務載入失敗: {e}")

# 典籍增強
try:
    from classical_enhancement import enhance_analysis
    print("✓ 典籍增強模組已載入")
except Exception as e:
    print(f"⚠ 典籍增強模組載入失敗: {e}")

# 功能權限
try:
    from feature_access import router as feature_access_router
    app.include_router(feature_access_router)
    print("✓ 功能權限服務已載入")
except Exception as e:
    print(f"⚠ 功能權限服務載入失敗: {e}")

# Email 驗證
try:
    from email_verification import router as email_verify_router
    app.include_router(email_verify_router)
    print("✓ Email 驗證服務已載入")
except Exception as e:
    print(f"⚠ Email 驗證服務載入失敗: {e}")

# 社交登入
try:
    from social_auth import router as social_auth_router
    app.include_router(social_auth_router)
    print("✓ 社交登入服務已載入")
except Exception as e:
    print(f"⚠ 社交登入服務載入失敗: {e}")

# 訂閱制服務
try:
    from subscription_service import router as subscription_router
    app.include_router(subscription_router)
    print("✓ 訂閱制服務已載入")
except Exception as e:
    print(f"⚠ 訂閱制服務載入失敗: {e}")

# 客服支援
try:
    from contact_support import router as support_router
    app.include_router(support_router)
    print("✓ 客服支援已載入")
except Exception as e:
    print(f"⚠ 客服支援載入失敗: {e}")

# 報告分享
try:
    from report_sharing import router as share_router
    app.include_router(share_router)
    print("✓ 報告分享已載入")
except Exception as e:
    print(f"⚠ 報告分享載入失敗: {e}")

# 推薦系統
try:
    from referral_system import router as referral_router
    app.include_router(referral_router)
    print("✓ 推薦系統已載入")
except Exception as e:
    print(f"⚠ 推薦系統載入失敗: {e}")

# 隱私優先
try:
    from privacy_first import router as privacy_router
    app.include_router(privacy_router)
    print("✓ 隱私優先模組已載入")
except Exception as e:
    print(f"⚠ 隱私優先模組載入失敗: {e}")

# 增強分析 API（三層詮釋體系）
try:
    from enhanced_analysis_api import router as enhanced_router
    app.include_router(enhanced_router)
    print("✓ 增強分析 API 已載入")
except Exception as e:
    print(f"⚠ 增強分析 API 載入失敗: {e}")

# 關於頁 API（方法論/織明揭示）
try:
    from about_api import router as about_router
    app.include_router(about_router)
    print("✓ 關於頁 API 已載入")
except Exception as e:
    print(f"⚠ 關於頁 API 載入失敗: {e}")
