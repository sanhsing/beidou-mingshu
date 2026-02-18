"""
簡化版五行圖組件
M3.3 | @星殼 | 2026-02-17
PYLIB: wuxing_core
"""

WUXING_COLORS = {
    '木': '#22c55e',  # green
    '火': '#ef4444',  # red
    '土': '#eab308',  # yellow
    '金': '#f5f5f5',  # white/silver
    '水': '#3b82f6',  # blue
}

WUXING_EMOJI = {
    '木': '🌳',
    '火': '🔥',
    '土': '🏔️',
    '金': '⚔️',
    '水': '💧',
}

def generate_wuxing_svg(stats: dict, size: int = 200) -> str:
    """生成五行圓餅圖 SVG"""
    total = sum(stats.values())
    if total == 0:
        total = 1
    
    cx, cy = size // 2, size // 2
    r = size // 2 - 20
    
    svg_parts = [f'<svg width="{size}" height="{size}" xmlns="http://www.w3.org/2000/svg">']
    svg_parts.append(f'<circle cx="{cx}" cy="{cy}" r="{r+10}" fill="#f3f4f6"/>')
    
    start_angle = -90
    elements = ['木', '火', '土', '金', '水']
    
    for elem in elements:
        count = stats.get(elem, 0)
        angle = (count / total) * 360
        
        if angle > 0:
            end_angle = start_angle + angle
            large_arc = 1 if angle > 180 else 0
            
            x1 = cx + r * __import__('math').cos(__import__('math').radians(start_angle))
            y1 = cy + r * __import__('math').sin(__import__('math').radians(start_angle))
            x2 = cx + r * __import__('math').cos(__import__('math').radians(end_angle))
            y2 = cy + r * __import__('math').sin(__import__('math').radians(end_angle))
            
            path = f'M {cx},{cy} L {x1},{y1} A {r},{r} 0 {large_arc},1 {x2},{y2} Z'
            svg_parts.append(f'<path d="{path}" fill="{WUXING_COLORS[elem]}"/>')
            
            start_angle = end_angle
    
    svg_parts.append('</svg>')
    return ''.join(svg_parts)

def generate_wuxing_bars_html(stats: dict) -> str:
    """生成五行條狀圖 HTML"""
    total = sum(stats.values())
    if total == 0:
        total = 1
    
    html = '<div class="space-y-2">'
    elements = ['木', '火', '土', '金', '水']
    
    for elem in elements:
        count = stats.get(elem, 0)
        percent = (count / total) * 100
        color = WUXING_COLORS[elem]
        emoji = WUXING_EMOJI[elem]
        
        html += f'''
        <div class="flex items-center gap-2">
            <span class="w-8 text-lg">{emoji}</span>
            <span class="w-8 font-medium">{elem}</span>
            <div class="flex-1 bg-gray-200 rounded-full h-4">
                <div class="h-4 rounded-full" style="width: {percent}%; background-color: {color};"></div>
            </div>
            <span class="w-8 text-right text-sm text-gray-600">{count}</span>
        </div>'''
    
    html += '</div>'
    return html

def get_wuxing_balance_text(stats: dict) -> dict:
    """分析五行平衡狀態"""
    total = sum(stats.values())
    avg = total / 5
    
    strong = [k for k, v in stats.items() if v > avg + 1]
    weak = [k for k, v in stats.items() if v < avg - 1]
    
    if not strong and not weak:
        balance = "平衡"
        advice = "您的五行分佈較為均衡，性格穩定。"
    elif strong and weak:
        balance = "偏頗"
        advice = f"五行中 {','.join(strong)} 較強，{','.join(weak)} 較弱，可透過後天調整。"
    elif strong:
        balance = "偏強"
        advice = f"{','.join(strong)} 五行較旺，行事風格明顯。"
    else:
        balance = "偏弱"
        advice = f"{','.join(weak)} 五行較缺，可適當補足。"
    
    return {
        'balance': balance,
        'strong': strong,
        'weak': weak,
        'advice': advice
    }

if __name__ == "__main__":
    stats = {'木': 2, '火': 3, '土': 1, '金': 1, '水': 1}
    print(generate_wuxing_bars_html(stats))
    print(get_wuxing_balance_text(stats))
