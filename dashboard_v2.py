"""
儀表板模組 v2 (升級版)
M5.1-M5.8 | @星殼 | 2026-02-17
PYLIB: db_unified, liunian_analyzer, frontend_app
"""
from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from datetime import datetime
from typing import Optional

router = APIRouter(tags=["dashboard"])

DASHBOARD_HTML = '''<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>我的命理中心 - 北斗命數</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        .gradient-bg {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); }}
        .card {{ transition: all 0.3s; }}
        .card:hover {{ transform: translateY(-3px); box-shadow: 0 10px 30px rgba(0,0,0,0.1); }}
    </style>
</head>
<body class="bg-gray-100 min-h-screen">
    <!-- 導航 -->
    <nav class="gradient-bg text-white p-4 shadow-lg">
        <div class="max-w-6xl mx-auto flex justify-between items-center">
            <a href="/" class="text-2xl font-bold">🌟 北斗命數</a>
            <div class="flex items-center gap-4">
                <span class="text-purple-200">👤 {username}</span>
                <a href="/logout" class="bg-white/20 px-4 py-2 rounded-lg hover:bg-white/30">登出</a>
            </div>
        </div>
    </nav>

    <main class="max-w-6xl mx-auto px-6 py-8">
        <!-- 歡迎區 -->
        <div class="bg-white rounded-2xl shadow-lg p-6 mb-6">
            <div class="flex justify-between items-center">
                <div>
                    <h1 class="text-2xl font-bold text-gray-800">您好，{username}！</h1>
                    <p class="text-gray-500 mt-1">{greeting}</p>
                </div>
                <div class="text-right">
                    <div class="text-sm text-gray-500">點數餘額</div>
                    <div class="text-3xl font-bold text-purple-600">{credits}</div>
                    <a href="/pricing" class="text-sm text-purple-500 hover:underline">+ 儲值</a>
                </div>
            </div>
        </div>

        <div class="grid md:grid-cols-3 gap-6">
            <!-- 左側：快捷操作 -->
            <div class="md:col-span-2 space-y-6">
                <!-- 快捷操作 -->
                <div class="bg-white rounded-2xl shadow-lg p-6">
                    <h2 class="text-lg font-bold text-gray-800 mb-4">🚀 快捷操作</h2>
                    <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
                        <a href="/bazi" class="card bg-purple-50 rounded-xl p-4 text-center hover:bg-purple-100">
                            <span class="text-3xl">🎯</span>
                            <div class="text-sm font-medium text-gray-700 mt-2">八字分析</div>
                        </a>
                        <a href="/naming" class="card bg-pink-50 rounded-xl p-4 text-center hover:bg-pink-100">
                            <span class="text-3xl">✏️</span>
                            <div class="text-sm font-medium text-gray-700 mt-2">命名建議</div>
                        </a>
                        <a href="/date-select" class="card bg-blue-50 rounded-xl p-4 text-center hover:bg-blue-100">
                            <span class="text-3xl">📅</span>
                            <div class="text-sm font-medium text-gray-700 mt-2">擇日服務</div>
                        </a>
                        <a href="/matching" class="card bg-red-50 rounded-xl p-4 text-center hover:bg-red-100">
                            <span class="text-3xl">💑</span>
                            <div class="text-sm font-medium text-gray-700 mt-2">合婚配對</div>
                        </a>
                    </div>
                </div>

                <!-- 最近報告 -->
                <div class="bg-white rounded-2xl shadow-lg p-6">
                    <div class="flex justify-between items-center mb-4">
                        <h2 class="text-lg font-bold text-gray-800">📜 最近報告</h2>
                        <a href="/reports" class="text-purple-600 text-sm hover:underline">查看全部 →</a>
                    </div>
                    {reports_html}
                </div>
            </div>

            <!-- 右側：運勢提示 + 會員 -->
            <div class="space-y-6">
                <!-- 今日運勢 -->
                <div class="bg-gradient-to-br from-purple-500 to-pink-500 rounded-2xl shadow-lg p-6 text-white">
                    <h2 class="text-lg font-bold mb-3">✨ 今日運勢提示</h2>
                    <div class="text-purple-100 text-sm space-y-2">
                        <p>📅 {today_date}</p>
                        <p>🌙 {lunar_date}</p>
                        <p>⭐ {daily_tip}</p>
                    </div>
                    <a href="/bazi" class="inline-block mt-4 bg-white/20 px-4 py-2 rounded-lg text-sm hover:bg-white/30">
                        查看詳細運勢 →
                    </a>
                </div>

                <!-- 會員狀態 -->
                <div class="bg-white rounded-2xl shadow-lg p-6">
                    <h2 class="text-lg font-bold text-gray-800 mb-3">👑 會員狀態</h2>
                    <div class="text-center py-4">
                        <span class="text-4xl">{membership_icon}</span>
                        <div class="text-lg font-bold text-gray-800 mt-2">{membership_name}</div>
                        <div class="text-sm text-gray-500">{membership_desc}</div>
                    </div>
                    {membership_cta}
                </div>

                <!-- 統計 -->
                <div class="bg-white rounded-2xl shadow-lg p-6">
                    <h2 class="text-lg font-bold text-gray-800 mb-3">📊 我的統計</h2>
                    <div class="space-y-3">
                        <div class="flex justify-between">
                            <span class="text-gray-600">報告數量</span>
                            <span class="font-bold text-purple-600">{report_count}</span>
                        </div>
                        <div class="flex justify-between">
                            <span class="text-gray-600">已分析命盤</span>
                            <span class="font-bold text-purple-600">{chart_count}</span>
                        </div>
                        <div class="flex justify-between">
                            <span class="text-gray-600">累計消費</span>
                            <span class="font-bold text-purple-600">{total_spent} 點</span>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </main>

    <footer class="bg-gray-800 text-gray-400 text-center p-6 mt-12">
        <p>© 2026 北斗命數. All rights reserved.</p>
    </footer>
</body>
</html>'''

def get_greeting():
    """根據時間返回問候語"""
    hour = datetime.now().hour
    if hour < 6:
        return "夜深了，注意休息 🌙"
    elif hour < 12:
        return "早安！今天也是美好的一天 ☀️"
    elif hour < 18:
        return "午安！下午也要保持好心情 🌤️"
    else:
        return "晚安！辛苦了一天 🌆"

def get_daily_tip():
    """每日運勢提示 (簡化版)"""
    tips = [
        "宜靜心思考，不宜衝動決策",
        "貴人運佳，適合拓展人脈",
        "財運平穩，投資宜保守",
        "感情運旺，適合表達心意",
        "事業運強，把握機會展現",
        "健康運需注意，多休息養生",
        "學習運佳，適合進修充電",
    ]
    return tips[datetime.now().day % len(tips)]

def get_lunar_date():
    """獲取農曆日期 (簡化顯示)"""
    # 實際應該用 lunar_calendar_v2 計算
    return "農曆正月十九"

def render_reports_list(reports: list) -> str:
    """渲染報告列表"""
    if not reports:
        return '''
        <div class="text-center py-8 text-gray-500">
            <span class="text-4xl">📭</span>
            <p class="mt-2">還沒有報告</p>
            <a href="/bazi" class="inline-block mt-4 text-purple-600 hover:underline">立即分析 →</a>
        </div>
        '''
    
    html = '<div class="space-y-3">'
    for r in reports[:5]:
        html += f'''
        <a href="/report/{r['id']}" class="card flex items-center gap-4 p-3 rounded-lg bg-gray-50 hover:bg-purple-50">
            <span class="text-2xl">{r.get('icon', '📜')}</span>
            <div class="flex-1">
                <div class="font-medium text-gray-800">{r['title']}</div>
                <div class="text-sm text-gray-500">{r['date']}</div>
            </div>
            <span class="text-purple-500">→</span>
        </a>
        '''
    html += '</div>'
    return html

def render_membership_cta(is_member: bool) -> str:
    """渲染會員 CTA"""
    if is_member:
        return '<a href="/membership" class="block text-center text-purple-600 text-sm hover:underline">管理會員 →</a>'
    return '<a href="/pricing" class="block w-full text-center gradient-bg text-white py-2 rounded-lg font-bold hover:opacity-90 mt-4">升級會員</a>'

@router.get("/dashboard", response_class=HTMLResponse)
async def dashboard_page(request: Request):
    """用戶儀表板"""
    # 模擬用戶數據 (實際應從 session/db 獲取)
    user = {
        'username': '用戶',
        'credits': 150,
        'is_member': False,
        'membership': 'free',
        'report_count': 3,
        'chart_count': 5,
        'total_spent': 450,
    }
    
    # 模擬報告列表
    reports = [
        {'id': 1, 'title': '八字命理報告', 'date': '2026-02-15', 'icon': '🎯'},
        {'id': 2, 'title': '流年運勢分析', 'date': '2026-02-10', 'icon': '📊'},
    ]
    
    # 會員狀態
    membership_map = {
        'free': ('🆓', '免費用戶', '升級享受更多服務'),
        'basic': ('🌟', '基礎會員', '有效期至 2026-12-31'),
        'premium': ('💎', '尊榮會員', '有效期至 2026-12-31'),
        'family': ('👑', '家族方案', '5人共享'),
    }
    m = membership_map.get(user['membership'], membership_map['free'])
    
    html = DASHBOARD_HTML.format(
        username=user['username'],
        greeting=get_greeting(),
        credits=user['credits'],
        today_date=datetime.now().strftime('%Y年%m月%d日'),
        lunar_date=get_lunar_date(),
        daily_tip=get_daily_tip(),
        reports_html=render_reports_list(reports),
        membership_icon=m[0],
        membership_name=m[1],
        membership_desc=m[2],
        membership_cta=render_membership_cta(user['is_member']),
        report_count=user['report_count'],
        chart_count=user['chart_count'],
        total_spent=user['total_spent'],
    )
    
    return html
