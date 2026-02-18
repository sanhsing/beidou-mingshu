"""
會員管理頁
membership_page.py | @璃語 | 2026-02-17
PYLIB: membership_service, dashboard_v2
"""
from fastapi import APIRouter, Request, Depends, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from datetime import datetime

router = APIRouter(prefix="/membership", tags=["membership"])

MEMBERSHIP_HTML = '''<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>會員管理 - 北斗命數</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>.gradient-bg {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); }}</style>
</head>
<body class="bg-gray-50 min-h-screen">
    <nav class="gradient-bg text-white p-4 shadow-lg">
        <div class="max-w-4xl mx-auto flex justify-between items-center">
            <a href="/" class="text-2xl font-bold">🌟 北斗命數</a>
            <a href="/dashboard" class="hover:text-purple-200">← 返回儀表板</a>
        </div>
    </nav>

    <main class="max-w-2xl mx-auto px-6 py-8">
        <h1 class="text-3xl font-bold text-gray-800 text-center mb-8">👑 會員管理</h1>

        <!-- 當前會員狀態 -->
        <div class="bg-white rounded-2xl shadow-xl p-6 mb-6">
            <div class="flex items-center gap-4 mb-6">
                <span class="text-5xl">{tier_icon}</span>
                <div>
                    <h2 class="text-2xl font-bold text-gray-800">{tier_name}</h2>
                    <p class="text-gray-500">{tier_desc}</p>
                </div>
            </div>

            {status_section}
        </div>

        <!-- 會員權益 -->
        <div class="bg-white rounded-2xl shadow-xl p-6 mb-6">
            <h3 class="text-lg font-bold text-gray-800 mb-4">📋 您的會員權益</h3>
            <div class="grid grid-cols-2 gap-3">
                {benefits_html}
            </div>
        </div>

        <!-- 操作區 -->
        <div class="bg-white rounded-2xl shadow-xl p-6 mb-6">
            <h3 class="text-lg font-bold text-gray-800 mb-4">⚙️ 會員操作</h3>
            {actions_html}
        </div>

        <!-- 訂閱歷史 -->
        <div class="bg-white rounded-2xl shadow-xl p-6">
            <h3 class="text-lg font-bold text-gray-800 mb-4">📜 訂閱歷史</h3>
            {history_html}
        </div>
    </main>
</body>
</html>'''

# 會員等級配置
TIER_CONFIG = {
    'free': {
        'icon': '🆓',
        'name': '免費用戶',
        'desc': '基礎功能',
        'benefits': ['免費八字試算', '基礎五行分析'],
    },
    'basic': {
        'icon': '🌟',
        'name': '基礎會員',
        'desc': '單次購買',
        'benefits': ['八字四柱排盤', '五行分析', '十神分析', 'PDF報告'],
    },
    'premium': {
        'icon': '💎',
        'name': '尊榮會員',
        'desc': '年費訂閱',
        'benefits': ['完整命理分析', '紫微斗數', '每月運勢更新', '3次擇日服務', '1次命名分析', '無限合婚配對', '專屬客服'],
    },
    'family': {
        'icon': '👑',
        'name': '家族方案',
        'desc': '年費 / 5人共享',
        'benefits': ['尊榮會員全部權益', '5人共享', '家族關係分析', '12次擇日服務', '5次命名分析', '優先客服支援'],
    },
}


def render_benefits(benefits: list) -> str:
    """渲染權益列表"""
    html = ''
    for b in benefits:
        html += f'<div class="flex items-center gap-2 text-gray-600"><span class="text-green-500">✓</span>{b}</div>'
    return html


def render_status_section(membership: dict) -> str:
    """渲染狀態區域"""
    if membership['tier'] == 'free':
        return '''
        <div class="bg-purple-50 rounded-xl p-4">
            <p class="text-gray-600 mb-3">升級會員享受更多專屬服務！</p>
            <a href="/pricing" class="inline-block gradient-bg text-white px-6 py-2 rounded-lg font-bold hover:opacity-90">
                查看方案 →
            </a>
        </div>
        '''
    
    if not membership.get('is_active'):
        return '''
        <div class="bg-red-50 rounded-xl p-4">
            <p class="text-red-600 font-bold">⚠️ 會員已過期</p>
            <p class="text-gray-600 mt-2">續訂以繼續享受會員權益</p>
            <a href="/checkout" class="inline-block mt-3 gradient-bg text-white px-6 py-2 rounded-lg font-bold">
                立即續訂 →
            </a>
        </div>
        '''
    
    days_left = membership.get('days_left', 0)
    end_date = membership.get('end_date', '')[:10] if membership.get('end_date') else ''
    auto_renew = membership.get('auto_renew', False)
    
    status_color = 'green' if days_left > 30 else 'yellow' if days_left > 7 else 'red'
    
    return f'''
    <div class="space-y-3">
        <div class="flex justify-between items-center py-2 border-b">
            <span class="text-gray-600">到期日期</span>
            <span class="font-bold text-gray-800">{end_date}</span>
        </div>
        <div class="flex justify-between items-center py-2 border-b">
            <span class="text-gray-600">剩餘天數</span>
            <span class="font-bold text-{status_color}-600">{days_left} 天</span>
        </div>
        <div class="flex justify-between items-center py-2">
            <span class="text-gray-600">自動續訂</span>
            <span class="font-bold {'text-green-600' if auto_renew else 'text-gray-400'}">
                {'已開啟' if auto_renew else '已關閉'}
            </span>
        </div>
    </div>
    '''


def render_actions(membership: dict) -> str:
    """渲染操作區"""
    if membership['tier'] == 'free':
        return '''
        <a href="/pricing" class="block w-full text-center gradient-bg text-white py-3 rounded-xl font-bold hover:opacity-90">
            升級會員
        </a>
        '''
    
    actions = []
    
    if membership.get('is_active'):
        if membership.get('auto_renew'):
            actions.append('''
            <form action="/membership/cancel-auto-renew" method="post" onsubmit="return confirm('確定要關閉自動續訂嗎？')">
                <button type="submit" class="w-full border-2 border-gray-300 text-gray-600 py-3 rounded-xl font-bold hover:bg-gray-50">
                    關閉自動續訂
                </button>
            </form>
            ''')
        else:
            actions.append('''
            <form action="/membership/enable-auto-renew" method="post">
                <button type="submit" class="w-full gradient-bg text-white py-3 rounded-xl font-bold hover:opacity-90">
                    開啟自動續訂
                </button>
            </form>
            ''')
        
        actions.append('''
        <a href="/checkout" class="block w-full text-center border-2 border-purple-600 text-purple-600 py-3 rounded-xl font-bold hover:bg-purple-50 mt-3">
            升級方案
        </a>
        ''')
    else:
        actions.append('''
        <a href="/checkout" class="block w-full text-center gradient-bg text-white py-3 rounded-xl font-bold hover:opacity-90">
            重新訂閱
        </a>
        ''')
    
    return '\n'.join(actions)


def render_history(history: list) -> str:
    """渲染訂閱歷史"""
    if not history:
        return '<p class="text-gray-500 text-center py-4">暫無訂閱記錄</p>'
    
    html = '<div class="space-y-3">'
    for h in history[:10]:
        action_map = {'subscribe': '訂閱', 'renew': '續訂', 'cancel': '取消', 'upgrade': '升級'}
        action = action_map.get(h.get('action', ''), h.get('action', ''))
        date = h.get('created_at', '')[:10] if h.get('created_at') else ''
        tier = h.get('tier', '')
        amount = h.get('amount', 0)
        
        html += f'''
        <div class="flex justify-between items-center py-2 border-b">
            <div>
                <span class="font-medium text-gray-800">{action}</span>
                {f'<span class="text-gray-500 text-sm ml-2">{tier}</span>' if tier else ''}
            </div>
            <div class="text-right">
                {f'<span class="text-purple-600 font-bold">NT${amount}</span>' if amount else ''}
                <span class="text-gray-400 text-sm block">{date}</span>
            </div>
        </div>
        '''
    html += '</div>'
    return html


@router.get("", response_class=HTMLResponse)
@router.get("/", response_class=HTMLResponse)
async def membership_page(request: Request):
    """會員管理頁"""
    # TODO: 從 JWT 獲取 user_id
    user_id = 1
    
    # 獲取會員狀態
    try:
        from membership_service import MembershipService
        ms = MembershipService()
        membership = ms.get_membership(user_id)
    except:
        membership = {'tier': 'free', 'is_active': True}
    
    tier = membership.get('tier', 'free')
    config = TIER_CONFIG.get(tier, TIER_CONFIG['free'])
    
    # 獲取訂閱歷史
    try:
        import sqlite3
        conn = sqlite3.connect('beidou_unified.db')
        cursor = conn.cursor()
        cursor.execute('''
            SELECT action, tier, amount, created_at FROM membership_history
            WHERE user_id = ? ORDER BY created_at DESC LIMIT 10
        ''', (user_id,))
        history = [{'action': r[0], 'tier': r[1], 'amount': r[2], 'created_at': r[3]} for r in cursor.fetchall()]
        conn.close()
    except:
        history = []
    
    html = MEMBERSHIP_HTML.format(
        tier_icon=config['icon'],
        tier_name=config['name'],
        tier_desc=config['desc'],
        status_section=render_status_section(membership),
        benefits_html=render_benefits(config['benefits']),
        actions_html=render_actions(membership),
        history_html=render_history(history)
    )
    
    return html


@router.post("/cancel-auto-renew")
async def cancel_auto_renew(request: Request):
    """取消自動續訂"""
    user_id = 1  # TODO: JWT
    
    try:
        from membership_service import MembershipService
        ms = MembershipService()
        ms.cancel_subscription(user_id)
    except:
        pass
    
    return RedirectResponse(url="/membership", status_code=303)


@router.post("/enable-auto-renew")
async def enable_auto_renew(request: Request):
    """開啟自動續訂"""
    user_id = 1  # TODO: JWT
    
    # TODO: 實現自動續訂開啟邏輯
    
    return RedirectResponse(url="/membership", status_code=303)
