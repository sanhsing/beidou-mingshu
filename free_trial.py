"""
免費試算頁面路由
M3.4-M3.7 | @星殼 | 2026-02-17
PYLIB: bazi_free, wuxing_simple, frontend_app
"""
from fastapi import APIRouter, Form
from fastapi.responses import HTMLResponse
from bazi_free import free_bazi_analyze
from wuxing_simple import generate_wuxing_bars_html, get_wuxing_balance_text

router = APIRouter(tags=["free"])

FREE_PAGE_TEMPLATE = '''<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>免費八字速算 - 北斗命數</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        .gradient-bg { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); }
    </style>
</head>
<body class="bg-gray-50 min-h-screen">
    <!-- 導航 -->
    <nav class="gradient-bg text-white p-4 shadow-lg">
        <div class="max-w-4xl mx-auto flex justify-between items-center">
            <a href="/" class="text-2xl font-bold">🌟 北斗命數</a>
            <div class="space-x-4">
                <a href="/login" class="hover:text-purple-200">登入</a>
                <a href="/register" class="bg-white text-purple-700 px-4 py-2 rounded-lg hover:bg-purple-100">免費註冊</a>
            </div>
        </div>
    </nav>

    <main class="max-w-4xl mx-auto p-6">
        <!-- 標題 -->
        <div class="text-center my-8">
            <h1 class="text-4xl font-bold text-gray-800 mb-4">🔮 免費八字速算</h1>
            <p class="text-gray-600 text-lg">輸入您的出生時間，立即獲得基礎命盤分析</p>
        </div>

        <!-- 輸入表單 -->
        <div class="bg-white rounded-2xl shadow-xl p-8 mb-8">
            <form id="baziForm" action="/free/result" method="post" class="space-y-6">
                <div class="grid md:grid-cols-4 gap-4">
                    <div>
                        <label class="block text-gray-700 font-medium mb-2">出生年</label>
                        <select name="year" required class="w-full p-3 border rounded-lg focus:ring-2 focus:ring-purple-500">
                            {year_options}
                        </select>
                    </div>
                    <div>
                        <label class="block text-gray-700 font-medium mb-2">月</label>
                        <select name="month" required class="w-full p-3 border rounded-lg focus:ring-2 focus:ring-purple-500">
                            {month_options}
                        </select>
                    </div>
                    <div>
                        <label class="block text-gray-700 font-medium mb-2">日</label>
                        <select name="day" required class="w-full p-3 border rounded-lg focus:ring-2 focus:ring-purple-500">
                            {day_options}
                        </select>
                    </div>
                    <div>
                        <label class="block text-gray-700 font-medium mb-2">時辰</label>
                        <select name="hour" required class="w-full p-3 border rounded-lg focus:ring-2 focus:ring-purple-500">
                            {hour_options}
                        </select>
                    </div>
                </div>
                
                <button type="submit" class="w-full gradient-bg text-white py-4 rounded-xl text-xl font-bold hover:opacity-90 transition">
                    ✨ 立即算命
                </button>
            </form>
        </div>

        <!-- 說明 -->
        <div class="bg-purple-50 rounded-xl p-6 border border-purple-200">
            <h3 class="font-bold text-purple-900 mb-2">📌 免費版包含：</h3>
            <ul class="text-purple-800 space-y-1">
                <li>✅ 八字四柱排盤</li>
                <li>✅ 五行分佈分析</li>
                <li>✅ 日主性格特質</li>
            </ul>
            <p class="text-purple-600 mt-4 text-sm">升級完整報告可獲得：十神分析、格局判定、大運走勢、流年運勢等深度解讀</p>
        </div>
    </main>

    <footer class="bg-gray-800 text-gray-400 text-center p-6 mt-12">
        <p>© 2026 北斗命數. All rights reserved.</p>
        <div class="mt-2 space-x-4 text-sm">
            <a href="/legal/privacy" class="hover:text-white">隱私政策</a>
            <a href="/legal/terms" class="hover:text-white">服務條款</a>
            <a href="/legal/disclaimer" class="hover:text-white">免責聲明</a>
        </div>
    </footer>
</body>
</html>'''

RESULT_PAGE_TEMPLATE = '''<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>您的八字分析 - 北斗命數</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        .gradient-bg {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); }}
        .locked {{ filter: blur(4px); pointer-events: none; }}
    </style>
</head>
<body class="bg-gray-50 min-h-screen">
    <nav class="gradient-bg text-white p-4 shadow-lg">
        <div class="max-w-4xl mx-auto flex justify-between items-center">
            <a href="/" class="text-2xl font-bold">🌟 北斗命數</a>
            <a href="/free" class="hover:text-purple-200">← 重新試算</a>
        </div>
    </nav>

    <main class="max-w-4xl mx-auto p-6">
        <!-- 八字展示 -->
        <div class="bg-white rounded-2xl shadow-xl p-8 mb-6">
            <h2 class="text-2xl font-bold text-gray-800 mb-6 text-center">📜 您的八字命盤</h2>
            
            <div class="grid grid-cols-4 gap-4 text-center mb-8">
                <div class="bg-purple-50 rounded-xl p-4">
                    <div class="text-sm text-gray-500 mb-1">年柱</div>
                    <div class="text-3xl font-bold text-purple-900">{year_gz}</div>
                </div>
                <div class="bg-purple-50 rounded-xl p-4">
                    <div class="text-sm text-gray-500 mb-1">月柱</div>
                    <div class="text-3xl font-bold text-purple-900">{month_gz}</div>
                </div>
                <div class="bg-purple-50 rounded-xl p-4 ring-2 ring-purple-500">
                    <div class="text-sm text-gray-500 mb-1">日柱（日主）</div>
                    <div class="text-3xl font-bold text-purple-900">{day_gz}</div>
                </div>
                <div class="bg-purple-50 rounded-xl p-4">
                    <div class="text-sm text-gray-500 mb-1">時柱</div>
                    <div class="text-3xl font-bold text-purple-900">{hour_gz}</div>
                </div>
            </div>

            <!-- 日主特質 -->
            <div class="bg-gradient-to-r from-purple-100 to-pink-100 rounded-xl p-6 mb-6">
                <div class="flex items-center gap-4">
                    <span class="text-5xl">{day_emoji}</span>
                    <div>
                        <h3 class="text-xl font-bold text-purple-900">日主：{day_master} {day_element}</h3>
                        <p class="text-gray-700 mt-1">{day_trait}</p>
                    </div>
                </div>
            </div>

            <!-- 五行分佈 -->
            <div class="mb-6">
                <h3 class="text-lg font-bold text-gray-800 mb-4">🎯 五行分佈</h3>
                {wuxing_chart}
            </div>

            <!-- 五行分析 -->
            <div class="bg-gray-50 rounded-xl p-4">
                <p class="text-gray-700"><strong>五行狀態：</strong>{balance_status}</p>
                <p class="text-gray-600 mt-2">{balance_advice}</p>
            </div>
        </div>

        <!-- 鎖定內容預覽 -->
        <div class="bg-white rounded-2xl shadow-xl p-8 mb-6 relative">
            <div class="absolute inset-0 bg-white/80 rounded-2xl flex items-center justify-center z-10">
                <div class="text-center p-6">
                    <span class="text-5xl">🔒</span>
                    <h3 class="text-xl font-bold text-gray-800 mt-4">解鎖完整報告</h3>
                    <p class="text-gray-600 mt-2">註冊即送 50 點，可免費兌換基礎分析報告</p>
                    <a href="/register" class="inline-block mt-4 gradient-bg text-white px-8 py-3 rounded-xl font-bold hover:opacity-90">
                        🎁 免費註冊領取
                    </a>
                </div>
            </div>
            
            <div class="locked">
                <h3 class="text-lg font-bold text-gray-800 mb-4">完整報告包含：</h3>
                <div class="grid md:grid-cols-2 gap-4">
                    <div class="p-4 bg-gray-50 rounded-lg">
                        <h4 class="font-bold">🎭 十神分析</h4>
                        <p class="text-gray-400">揭示您的人際關係模式...</p>
                    </div>
                    <div class="p-4 bg-gray-50 rounded-lg">
                        <h4 class="font-bold">📊 格局判定</h4>
                        <p class="text-gray-400">分析您的命格類型...</p>
                    </div>
                    <div class="p-4 bg-gray-50 rounded-lg">
                        <h4 class="font-bold">📈 大運走勢</h4>
                        <p class="text-gray-400">十年運勢詳細解讀...</p>
                    </div>
                    <div class="p-4 bg-gray-50 rounded-lg">
                        <h4 class="font-bold">🌟 流年運勢</h4>
                        <p class="text-gray-400">今年運勢重點提示...</p>
                    </div>
                </div>
            </div>
        </div>

        <!-- CTA -->
        <div class="text-center">
            <a href="/register" class="inline-block gradient-bg text-white px-12 py-4 rounded-xl text-xl font-bold hover:opacity-90 shadow-lg">
                🚀 立即註冊，獲取完整報告
            </a>
            <p class="text-gray-500 mt-4 text-sm">已有帳戶？<a href="/login" class="text-purple-600 hover:underline">登入</a></p>
        </div>
    </main>

    <footer class="bg-gray-800 text-gray-400 text-center p-6 mt-12">
        <p>© 2026 北斗命數. All rights reserved.</p>
    </footer>
</body>
</html>'''

def generate_options():
    """生成表單選項"""
    from datetime import datetime
    current_year = datetime.now().year
    
    years = ''.join([f'<option value="{y}">{y}</option>' for y in range(current_year - 80, current_year + 1)])
    months = ''.join([f'<option value="{m}">{m}月</option>' for m in range(1, 13)])
    days = ''.join([f'<option value="{d}">{d}日</option>' for d in range(1, 32)])
    hours = ''.join([f'<option value="{h}">{h:02d}:00-{(h+1)%24:02d}:00</option>' for h in range(0, 24, 2)])
    
    return years, months, days, hours

@router.get("/free", response_class=HTMLResponse)
async def free_trial_page():
    """免費試算頁面"""
    years, months, days, hours = generate_options()
    
    html = FREE_PAGE_TEMPLATE.format(
        year_options=years,
        month_options=months,
        day_options=days,
        hour_options=hours
    )
    return html

@router.post("/free/result", response_class=HTMLResponse)
async def free_trial_result(
    year: int = Form(...),
    month: int = Form(...),
    day: int = Form(...),
    hour: int = Form(...)
):
    """免費試算結果"""
    # 執行分析
    result = free_bazi_analyze(year, month, day, hour)
    
    # 生成五行圖
    wuxing_chart = generate_wuxing_bars_html(result['wuxing'])
    balance = get_wuxing_balance_text(result['wuxing'])
    
    # 渲染結果
    html = RESULT_PAGE_TEMPLATE.format(
        year_gz=result['bazi']['year']['ganzhi'],
        month_gz=result['bazi']['month']['ganzhi'],
        day_gz=result['bazi']['day']['ganzhi'],
        hour_gz=result['bazi']['hour']['ganzhi'],
        day_master=result['day_master'],
        day_element=result['day_master_element'],
        day_emoji=result['day_master_emoji'],
        day_trait=result['day_master_trait'],
        wuxing_chart=wuxing_chart,
        balance_status=balance['balance'],
        balance_advice=balance['advice']
    )
    return html
