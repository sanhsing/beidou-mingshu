"""
法律頁面路由模組
M1.8-M1.9 | @澄書 | 2026-02-17
"""
from fastapi import APIRouter
from fastapi.responses import HTMLResponse
import markdown
from pathlib import Path

router = APIRouter(prefix="/legal", tags=["legal"])

LEGAL_DIR = Path(__file__).parent / "legal"

def render_legal_page(title: str, content_md: str) -> str:
    """渲染法律頁面 HTML"""
    content_html = markdown.markdown(content_md, extensions=['tables'])
    
    return f'''<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} - 北斗命數</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-gray-50 min-h-screen">
    <nav class="bg-purple-900 text-white p-4">
        <div class="max-w-4xl mx-auto flex justify-between items-center">
            <a href="/" class="text-xl font-bold">🌟 北斗命數</a>
            <a href="/" class="text-purple-200 hover:text-white">← 返回首頁</a>
        </div>
    </nav>
    
    <main class="max-w-4xl mx-auto p-6 bg-white my-8 rounded-lg shadow">
        <article class="prose prose-purple max-w-none">
            {content_html}
        </article>
    </main>
    
    <footer class="bg-gray-800 text-gray-400 text-center p-4 text-sm">
        © 2026 北斗命數. All rights reserved.
    </footer>
</body>
</html>'''

@router.get("/privacy", response_class=HTMLResponse)
async def privacy_policy():
    """隱私權政策"""
    content = (LEGAL_DIR / "privacy.md").read_text(encoding="utf-8")
    return render_legal_page("隱私權政策", content)

@router.get("/terms", response_class=HTMLResponse)
async def terms_of_service():
    """服務條款"""
    content = (LEGAL_DIR / "terms.md").read_text(encoding="utf-8")
    return render_legal_page("服務條款", content)

@router.get("/refund", response_class=HTMLResponse)
async def refund_policy():
    """退款政策"""
    content = (LEGAL_DIR / "refund.md").read_text(encoding="utf-8")
    return render_legal_page("退款政策", content)

@router.get("/disclaimer", response_class=HTMLResponse)
async def disclaimer():
    """免責聲明"""
    content = (LEGAL_DIR / "disclaimer.md").read_text(encoding="utf-8")
    return render_legal_page("免責聲明", content)

# 法律頁面索引
@router.get("/", response_class=HTMLResponse)
async def legal_index():
    """法律文件索引"""
    return '''<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>法律文件 - 北斗命數</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-gray-50 min-h-screen">
    <nav class="bg-purple-900 text-white p-4">
        <div class="max-w-4xl mx-auto flex justify-between items-center">
            <a href="/" class="text-xl font-bold">🌟 北斗命數</a>
            <a href="/" class="text-purple-200 hover:text-white">← 返回首頁</a>
        </div>
    </nav>
    
    <main class="max-w-4xl mx-auto p-6 my-8">
        <h1 class="text-3xl font-bold text-gray-800 mb-8">法律文件</h1>
        
        <div class="grid gap-4">
            <a href="/legal/privacy" class="bg-white p-6 rounded-lg shadow hover:shadow-md transition">
                <h2 class="text-xl font-semibold text-purple-900">🔒 隱私權政策</h2>
                <p class="text-gray-600 mt-2">了解我們如何收集、使用及保護您的個人資料</p>
            </a>
            
            <a href="/legal/terms" class="bg-white p-6 rounded-lg shadow hover:shadow-md transition">
                <h2 class="text-xl font-semibold text-purple-900">📜 服務條款</h2>
                <p class="text-gray-600 mt-2">使用本服務的規範與約定</p>
            </a>
            
            <a href="/legal/refund" class="bg-white p-6 rounded-lg shadow hover:shadow-md transition">
                <h2 class="text-xl font-semibold text-purple-900">💰 退款政策</h2>
                <p class="text-gray-600 mt-2">關於點數購買與訂閱的退款說明</p>
            </a>
            
            <a href="/legal/disclaimer" class="bg-white p-6 rounded-lg shadow hover:shadow-md transition">
                <h2 class="text-xl font-semibold text-purple-900">⚠️ 免責聲明</h2>
                <p class="text-gray-600 mt-2">關於命理分析服務的重要聲明</p>
            </a>
        </div>
    </main>
    
    <footer class="bg-gray-800 text-gray-400 text-center p-4 text-sm">
        © 2026 北斗命數. All rights reserved.
    </footer>
</body>
</html>'''

# Cookie 政策路由
@router.get("/legal/cookie", response_class=HTMLResponse)
async def cookie_policy():
    """Cookie 政策頁面"""
    content = load_legal_doc("cookie.md")
    return render_legal_page("Cookie 政策", content, "🍪")

# 兒童保護政策路由
@router.get("/legal/children", response_class=HTMLResponse)
async def children_policy():
    """兒童保護政策頁面"""
    content = load_legal_doc("children.md")
    return render_legal_page("兒童保護政策", content, "👶")
