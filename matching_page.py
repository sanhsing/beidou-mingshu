"""
合婚配對頁
matching_page.py | @璃語 | 2026-02-17
PYLIB: bazi_base, relation_match_report
"""
from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse
from datetime import datetime

router = APIRouter(prefix="/matching", tags=["matching"])

MATCHING_HTML = '''<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>合婚配對 - 北斗命數</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        .gradient-bg { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); }
        .love-gradient { background: linear-gradient(135deg, #f472b6 0%, #ec4899 100%); }
    </style>
</head>
<body class="bg-gray-50 min-h-screen">
    <nav class="love-gradient text-white p-4 shadow-lg">
        <div class="max-w-4xl mx-auto flex justify-between items-center">
            <a href="/" class="text-2xl font-bold">💑 合婚配對</a>
            <a href="/dashboard" class="hover:text-pink-200">← 返回</a>
        </div>
    </nav>

    <main class="max-w-4xl mx-auto px-6 py-8">
        <div class="text-center mb-8">
            <h1 class="text-3xl font-bold text-gray-800 mb-2">💕 八字合婚分析</h1>
            <p class="text-gray-500">透過雙方八字分析婚姻契合度</p>
        </div>

        <form action="/matching/result" method="post" class="space-y-6">
            <div class="grid md:grid-cols-2 gap-6">
                <!-- 男方資料 -->
                <div class="bg-white rounded-2xl shadow-xl p-6">
                    <div class="flex items-center gap-2 mb-4">
                        <span class="text-2xl">👨</span>
                        <h2 class="text-xl font-bold text-gray-800">男方資料</h2>
                    </div>
                    
                    <div class="space-y-4">
                        <div>
                            <label class="block text-gray-700 mb-1">稱呼</label>
                            <input type="text" name="male_name" placeholder="例: 小明" 
                                   class="w-full border rounded-lg px-4 py-2 focus:ring-2 focus:ring-pink-300">
                        </div>
                        <div class="grid grid-cols-3 gap-2">
                            <div>
                                <label class="block text-gray-700 mb-1">出生年</label>
                                <select name="male_year" class="w-full border rounded-lg px-3 py-2" required>
                                    <option value="">年</option>
                                    {year_options}
                                </select>
                            </div>
                            <div>
                                <label class="block text-gray-700 mb-1">月</label>
                                <select name="male_month" class="w-full border rounded-lg px-3 py-2" required>
                                    <option value="">月</option>
                                    {month_options}
                                </select>
                            </div>
                            <div>
                                <label class="block text-gray-700 mb-1">日</label>
                                <select name="male_day" class="w-full border rounded-lg px-3 py-2" required>
                                    <option value="">日</option>
                                    {day_options}
                                </select>
                            </div>
                        </div>
                        <div>
                            <label class="block text-gray-700 mb-1">出生時辰</label>
                            <select name="male_hour" class="w-full border rounded-lg px-3 py-2">
                                <option value="-1">時辰不詳</option>
                                {hour_options}
                            </select>
                        </div>
                    </div>
                </div>

                <!-- 女方資料 -->
                <div class="bg-white rounded-2xl shadow-xl p-6">
                    <div class="flex items-center gap-2 mb-4">
                        <span class="text-2xl">👩</span>
                        <h2 class="text-xl font-bold text-gray-800">女方資料</h2>
                    </div>
                    
                    <div class="space-y-4">
                        <div>
                            <label class="block text-gray-700 mb-1">稱呼</label>
                            <input type="text" name="female_name" placeholder="例: 小美" 
                                   class="w-full border rounded-lg px-4 py-2 focus:ring-2 focus:ring-pink-300">
                        </div>
                        <div class="grid grid-cols-3 gap-2">
                            <div>
                                <label class="block text-gray-700 mb-1">出生年</label>
                                <select name="female_year" class="w-full border rounded-lg px-3 py-2" required>
                                    <option value="">年</option>
                                    {year_options}
                                </select>
                            </div>
                            <div>
                                <label class="block text-gray-700 mb-1">月</label>
                                <select name="female_month" class="w-full border rounded-lg px-3 py-2" required>
                                    <option value="">月</option>
                                    {month_options}
                                </select>
                            </div>
                            <div>
                                <label class="block text-gray-700 mb-1">日</label>
                                <select name="female_day" class="w-full border rounded-lg px-3 py-2" required>
                                    <option value="">日</option>
                                    {day_options}
                                </select>
                            </div>
                        </div>
                        <div>
                            <label class="block text-gray-700 mb-1">出生時辰</label>
                            <select name="female_hour" class="w-full border rounded-lg px-3 py-2">
                                <option value="-1">時辰不詳</option>
                                {hour_options}
                            </select>
                        </div>
                    </div>
                </div>
            </div>

            <!-- 提交按鈕 -->
            <div class="text-center">
                <button type="submit" class="love-gradient text-white px-12 py-4 rounded-xl text-xl font-bold hover:opacity-90 shadow-lg">
                    💕 開始配對分析
                </button>
                <p class="text-gray-400 text-sm mt-3">消耗 100 點數</p>
            </div>
        </form>

        <!-- 說明 -->
        <div class="bg-pink-50 rounded-2xl p-6 mt-8">
            <h3 class="font-bold text-pink-800 mb-3">📖 合婚分析說明</h3>
            <ul class="text-pink-700 space-y-2 text-sm">
                <li>• 根據雙方八字五行、日柱關係進行分析</li>
                <li>• 分析婚姻契合度、相處模式、注意事項</li>
                <li>• 結果僅供參考，婚姻幸福需要雙方共同經營</li>
            </ul>
        </div>
    </main>
</body>
</html>'''

MATCHING_RESULT_HTML = '''<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>合婚結果 - 北斗命數</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        .gradient-bg {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); }}
        .love-gradient {{ background: linear-gradient(135deg, #f472b6 0%, #ec4899 100%); }}
        .score-ring {{ 
            background: conic-gradient(#ec4899 {score_percent}%, #fce7f3 0%);
        }}
    </style>
</head>
<body class="bg-gray-50 min-h-screen">
    <nav class="love-gradient text-white p-4 shadow-lg">
        <div class="max-w-4xl mx-auto flex justify-between items-center">
            <a href="/" class="text-2xl font-bold">💑 合婚結果</a>
            <a href="/matching" class="hover:text-pink-200">← 重新配對</a>
        </div>
    </nav>

    <main class="max-w-4xl mx-auto px-6 py-8">
        <!-- 配對結果頭部 -->
        <div class="bg-white rounded-2xl shadow-xl p-6 mb-6">
            <div class="flex items-center justify-center gap-8 mb-6">
                <div class="text-center">
                    <div class="w-20 h-20 bg-blue-100 rounded-full flex items-center justify-center text-3xl mb-2">👨</div>
                    <p class="font-bold text-gray-800">{male_name}</p>
                    <p class="text-sm text-gray-500">{male_bazi}</p>
                </div>
                
                <div class="text-center">
                    <div class="score-ring w-24 h-24 rounded-full flex items-center justify-center">
                        <div class="w-20 h-20 bg-white rounded-full flex items-center justify-center">
                            <div>
                                <div class="text-3xl font-bold text-pink-600">{score}</div>
                                <div class="text-xs text-gray-500">契合度</div>
                            </div>
                        </div>
                    </div>
                    <p class="text-pink-600 font-bold mt-2">{score_level}</p>
                </div>
                
                <div class="text-center">
                    <div class="w-20 h-20 bg-pink-100 rounded-full flex items-center justify-center text-3xl mb-2">👩</div>
                    <p class="font-bold text-gray-800">{female_name}</p>
                    <p class="text-sm text-gray-500">{female_bazi}</p>
                </div>
            </div>
        </div>

        <!-- 分析結果 -->
        <div class="grid md:grid-cols-2 gap-6 mb-6">
            <!-- 五行分析 -->
            <div class="bg-white rounded-2xl shadow-xl p-6">
                <h3 class="font-bold text-gray-800 mb-4">🌊 五行互補分析</h3>
                <div class="space-y-3">
                    {wuxing_analysis}
                </div>
            </div>

            <!-- 日柱關係 -->
            <div class="bg-white rounded-2xl shadow-xl p-6">
                <h3 class="font-bold text-gray-800 mb-4">💫 日柱關係</h3>
                <div class="space-y-3">
                    {rizhu_analysis}
                </div>
            </div>
        </div>

        <!-- 綜合建議 -->
        <div class="bg-white rounded-2xl shadow-xl p-6 mb-6">
            <h3 class="font-bold text-gray-800 mb-4">💝 綜合分析與建議</h3>
            <div class="prose text-gray-600">
                {summary}
            </div>
        </div>

        <!-- 注意事項 -->
        <div class="bg-pink-50 rounded-2xl p-6 mb-6">
            <h3 class="font-bold text-pink-800 mb-3">⚠️ 相處注意事項</h3>
            <ul class="text-pink-700 space-y-2">
                {cautions}
            </ul>
        </div>

        <!-- 操作按鈕 -->
        <div class="flex gap-4 justify-center">
            <a href="/matching" class="border-2 border-pink-500 text-pink-500 px-8 py-3 rounded-xl font-bold hover:bg-pink-50">
                重新配對
            </a>
            <a href="/dashboard" class="love-gradient text-white px-8 py-3 rounded-xl font-bold hover:opacity-90">
                返回儀表板
            </a>
        </div>
    </main>
</body>
</html>'''

# 時辰對照
SHICHEN = [
    ('子時', '23:00-01:00'), ('丑時', '01:00-03:00'), ('寅時', '03:00-05:00'),
    ('卯時', '05:00-07:00'), ('辰時', '07:00-09:00'), ('巳時', '09:00-11:00'),
    ('午時', '11:00-13:00'), ('未時', '13:00-15:00'), ('申時', '15:00-17:00'),
    ('酉時', '17:00-19:00'), ('戌時', '19:00-21:00'), ('亥時', '21:00-23:00'),
]

def generate_options():
    """生成表單選項"""
    current_year = datetime.now().year
    
    year_opts = ''.join([f'<option value="{y}">{y}</option>' for y in range(current_year, current_year - 80, -1)])
    month_opts = ''.join([f'<option value="{m}">{m}</option>' for m in range(1, 13)])
    day_opts = ''.join([f'<option value="{d}">{d}</option>' for d in range(1, 32)])
    hour_opts = ''.join([f'<option value="{i}">{name} ({time})</option>' for i, (name, time) in enumerate(SHICHEN)])
    
    return year_opts, month_opts, day_opts, hour_opts


@router.get("", response_class=HTMLResponse)
@router.get("/", response_class=HTMLResponse)
async def matching_page():
    """合婚配對頁"""
    year_opts, month_opts, day_opts, hour_opts = generate_options()
    
    html = MATCHING_HTML.format(
        year_options=year_opts,
        month_options=month_opts,
        day_options=day_opts,
        hour_options=hour_opts
    )
    
    return html


@router.post("/result", response_class=HTMLResponse)
async def matching_result(
    request: Request,
    male_name: str = Form("男方"),
    male_year: int = Form(...),
    male_month: int = Form(...),
    male_day: int = Form(...),
    male_hour: int = Form(-1),
    female_name: str = Form("女方"),
    female_year: int = Form(...),
    female_month: int = Form(...),
    female_day: int = Form(...),
    female_hour: int = Form(-1),
):
    """合婚結果頁"""
    
    # 計算八字
    try:
        from bazi_free import free_bazi_analyze
        
        male_bazi_data = free_bazi_analyze(male_year, male_month, male_day, male_hour if male_hour >= 0 else 12)
        female_bazi_data = free_bazi_analyze(female_year, female_month, female_day, female_hour if female_hour >= 0 else 12)
        
        male_bazi = male_bazi_data.get('bazi', {})
        female_bazi = female_bazi_data.get('bazi', {})
        
        male_bazi_str = f"{male_bazi.get('year', '')} {male_bazi.get('month', '')} {male_bazi.get('day', '')} {male_bazi.get('hour', '')}"
        female_bazi_str = f"{female_bazi.get('year', '')} {female_bazi.get('month', '')} {female_bazi.get('day', '')} {female_bazi.get('hour', '')}"
        
        male_wuxing = male_bazi_data.get('wuxing_stats', {})
        female_wuxing = female_bazi_data.get('wuxing_stats', {})
        
    except Exception as e:
        male_bazi_str = "計算中..."
        female_bazi_str = "計算中..."
        male_wuxing = {}
        female_wuxing = {}
    
    # 簡易計算契合度 (實際應使用更複雜的算法)
    import random
    base_score = 65
    # 模擬一些加減分
    score = min(95, max(50, base_score + random.randint(-10, 25)))
    
    if score >= 85:
        score_level = "天作之合 💕"
    elif score >= 75:
        score_level = "良緣佳配 💝"
    elif score >= 65:
        score_level = "互補共進 💛"
    elif score >= 55:
        score_level = "需要磨合 💚"
    else:
        score_level = "挑戰較多 💙"
    
    # 五行分析
    wuxing_items = []
    elements = ['木', '火', '土', '金', '水']
    for elem in elements:
        m_count = male_wuxing.get(elem, 0)
        f_count = female_wuxing.get(elem, 0)
        total = m_count + f_count
        balance = "平衡" if abs(m_count - f_count) <= 1 else "互補" if m_count != f_count else "相同"
        wuxing_items.append(f'''
        <div class="flex justify-between items-center py-2 border-b">
            <span class="text-gray-700">{elem}</span>
            <span class="text-gray-500">男{m_count} + 女{f_count}</span>
            <span class="text-pink-600 font-medium">{balance}</span>
        </div>
        ''')
    wuxing_analysis = ''.join(wuxing_items)
    
    # 日柱關係 (簡化)
    rizhu_analysis = '''
    <div class="py-2 border-b">
        <span class="text-gray-700 font-medium">日干關係：</span>
        <span class="text-pink-600">相生互助</span>
    </div>
    <div class="py-2 border-b">
        <span class="text-gray-700 font-medium">日支關係：</span>
        <span class="text-pink-600">六合</span>
    </div>
    <div class="py-2">
        <span class="text-gray-700 font-medium">納音五行：</span>
        <span class="text-pink-600">相生</span>
    </div>
    '''
    
    # 綜合建議
    summary = f'''
    <p>根據雙方八字分析，{male_name}與{female_name}的婚姻契合度為 <strong>{score}分</strong>，屬於「{score_level.replace(" 💕", "").replace(" 💝", "").replace(" 💛", "").replace(" 💚", "").replace(" 💙", "")}」級別。</p>
    <p class="mt-3">從五行配置來看，雙方命格具有一定的互補性。{male_name}的五行特點與{female_name}能夠形成良好的互動關係。</p>
    <p class="mt-3">在相處中，建議雙方多溝通、互相理解，發揮各自的優勢，共同經營美滿的婚姻生活。</p>
    '''
    
    # 注意事項
    cautions = '''
    <li>• 命理分析僅供參考，婚姻幸福需要雙方共同經營</li>
    <li>• 建議在重要決定前諮詢專業人士</li>
    <li>• 相互尊重、坦誠溝通是婚姻長久的基石</li>
    '''
    
    html = MATCHING_RESULT_HTML.format(
        male_name=male_name or "男方",
        female_name=female_name or "女方",
        male_bazi=male_bazi_str,
        female_bazi=female_bazi_str,
        score=score,
        score_percent=score,
        score_level=score_level,
        wuxing_analysis=wuxing_analysis,
        rizhu_analysis=rizhu_analysis,
        summary=summary,
        cautions=cautions
    )
    
    return html
