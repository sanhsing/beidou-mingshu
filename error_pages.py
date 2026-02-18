"""
錯誤頁面
error_pages.py | @星殼 | 2026-02-17
PYLIB: landing_page (共用樣式)
"""
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.exceptions import HTTPException

router = APIRouter(tags=["errors"])

ERROR_TEMPLATE = '''<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} - 北斗命數</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        .gradient-bg {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); }}
        @keyframes float {{ 0%, 100% {{ transform: translateY(0); }} 50% {{ transform: translateY(-20px); }} }}
        .float {{ animation: float 3s ease-in-out infinite; }}
    </style>
</head>
<body class="bg-gray-50 min-h-screen flex items-center justify-center">
    <div class="text-center px-6">
        <div class="text-8xl mb-6 float">{icon}</div>
        <h1 class="text-6xl font-bold text-gray-800 mb-4">{code}</h1>
        <h2 class="text-2xl font-bold text-gray-700 mb-4">{title}</h2>
        <p class="text-gray-500 mb-8 max-w-md mx-auto">{message}</p>
        <div class="space-x-4">
            <a href="/" class="inline-block gradient-bg text-white px-8 py-3 rounded-xl font-bold hover:opacity-90">
                返回首頁
            </a>
            <a href="javascript:history.back()" class="inline-block border-2 border-purple-600 text-purple-600 px-8 py-3 rounded-xl font-bold hover:bg-purple-50">
                返回上一頁
            </a>
        </div>
        <p class="text-gray-400 text-sm mt-12">
            需要幫助？<a href="/help" class="text-purple-600 hover:underline">聯繫客服</a>
        </p>
    </div>
</body>
</html>'''

def render_error_page(code: int, title: str, message: str, icon: str) -> str:
    """渲染錯誤頁面"""
    return ERROR_TEMPLATE.format(
        code=code,
        title=title,
        message=message,
        icon=icon
    )

# 404 頁面
PAGE_404 = render_error_page(
    code=404,
    title="頁面不存在",
    message="您要找的頁面可能已被移除、名稱已更改，或暫時無法使用。請確認網址是否正確。",
    icon="🔍"
)

# 500 頁面
PAGE_500 = render_error_page(
    code=500,
    title="伺服器錯誤",
    message="抱歉，系統暫時發生問題。我們已收到通知並正在處理中，請稍後再試。",
    icon="🔧"
)

# 403 頁面
PAGE_403 = render_error_page(
    code=403,
    title="存取被拒",
    message="您沒有權限存取此頁面。如果您認為這是錯誤，請聯繫客服。",
    icon="🚫"
)

# 401 頁面
PAGE_401 = render_error_page(
    code=401,
    title="請先登入",
    message="此頁面需要登入才能存取。請登入您的帳號後再試。",
    icon="🔐"
)

# 維護頁面
PAGE_MAINTENANCE = '''<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>系統維護中 - 北斗命數</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        .gradient-bg { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); }
        @keyframes spin { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }
        .spin { animation: spin 2s linear infinite; }
    </style>
</head>
<body class="gradient-bg min-h-screen flex items-center justify-center">
    <div class="text-center text-white px-6">
        <div class="text-8xl mb-6 spin">⚙️</div>
        <h1 class="text-4xl font-bold mb-4">系統維護中</h1>
        <p class="text-purple-100 mb-8 max-w-md mx-auto">
            我們正在進行系統升級，預計將於短時間內完成。<br>
            感謝您的耐心等候。
        </p>
        <div class="bg-white/20 rounded-xl p-4 inline-block">
            <p class="text-sm">預計完成時間</p>
            <p class="text-2xl font-bold">30 分鐘內</p>
        </div>
    </div>
</body>
</html>'''

@router.get("/error/404", response_class=HTMLResponse)
async def error_404():
    """404 錯誤頁面"""
    return PAGE_404

@router.get("/error/500", response_class=HTMLResponse)
async def error_500():
    """500 錯誤頁面"""
    return PAGE_500

@router.get("/error/403", response_class=HTMLResponse)
async def error_403():
    """403 錯誤頁面"""
    return PAGE_403

@router.get("/error/401", response_class=HTMLResponse)
async def error_401():
    """401 錯誤頁面"""
    return PAGE_401

@router.get("/maintenance", response_class=HTMLResponse)
async def maintenance():
    """維護頁面"""
    return PAGE_MAINTENANCE

# 全局異常處理器 (需在 app.py 中註冊)
async def not_found_handler(request: Request, exc: HTTPException):
    """404 異常處理"""
    return HTMLResponse(content=PAGE_404, status_code=404)

async def server_error_handler(request: Request, exc: Exception):
    """500 異常處理"""
    return HTMLResponse(content=PAGE_500, status_code=500)
