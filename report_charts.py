"""
報告圖表模組
M6.5-M6.8 | @璃語 | 2026-02-17
PYLIB: dayun_calculator, liunian_analyzer, report_styles
"""
from reportlab.lib.colors import HexColor
from reportlab.graphics.shapes import Drawing, Rect, Line, String, Circle
from reportlab.graphics.charts.lineplots import LinePlot
from reportlab.graphics.charts.barcharts import VerticalBarChart
from reportlab.graphics.widgets.markers import makeMarker

# === 顏色 ===
PURPLE = HexColor('#667eea')
GOLD = HexColor('#D4AF37')
GRAY = HexColor('#666666')
LIGHT_GRAY = HexColor('#eeeeee')

def create_dayun_chart(dayun_data: list, width=500, height=200) -> Drawing:
    """
    創建大運走勢圖
    dayun_data: [{'age': 10, 'ganzhi': '甲子', 'score': 75}, ...]
    """
    d = Drawing(width, height)
    
    # 背景
    d.add(Rect(0, 0, width, height, fillColor=HexColor('#fafafa'), strokeColor=None))
    
    # 標題
    d.add(String(width / 2, height - 20, '大運走勢圖', 
                 fontSize=14, fontName='SimHei', textAnchor='middle', fillColor=GRAY))
    
    if not dayun_data:
        return d
    
    # 數據準備
    ages = [item['age'] for item in dayun_data]
    scores = [item.get('score', 50) for item in dayun_data]
    ganzhis = [item['ganzhi'] for item in dayun_data]
    
    # 繪製區域
    chart_left = 60
    chart_right = width - 40
    chart_bottom = 50
    chart_top = height - 50
    chart_width = chart_right - chart_left
    chart_height = chart_top - chart_bottom
    
    # 網格線
    for i in range(5):
        y = chart_bottom + (chart_height / 4) * i
        d.add(Line(chart_left, y, chart_right, y, strokeColor=LIGHT_GRAY, strokeWidth=0.5))
    
    # X軸刻度和標籤
    n = len(dayun_data)
    for i, item in enumerate(dayun_data):
        x = chart_left + (chart_width / (n - 1)) * i if n > 1 else chart_left + chart_width / 2
        # 刻度
        d.add(Line(x, chart_bottom, x, chart_bottom - 5, strokeColor=GRAY))
        # 年齡
        d.add(String(x, chart_bottom - 18, f'{item["age"]}歲', 
                     fontSize=8, fontName='SimSun', textAnchor='middle', fillColor=GRAY))
        # 干支
        d.add(String(x, chart_bottom - 30, item['ganzhi'], 
                     fontSize=9, fontName='SimHei', textAnchor='middle', fillColor=PURPLE))
    
    # 繪製折線
    points = []
    for i, score in enumerate(scores):
        x = chart_left + (chart_width / (n - 1)) * i if n > 1 else chart_left + chart_width / 2
        y = chart_bottom + (score / 100) * chart_height
        points.append((x, y))
    
    # 連線
    for i in range(len(points) - 1):
        d.add(Line(points[i][0], points[i][1], points[i+1][0], points[i+1][1],
                   strokeColor=PURPLE, strokeWidth=2))
    
    # 數據點
    for x, y in points:
        d.add(Circle(x, y, 5, fillColor=PURPLE, strokeColor=HexColor('#ffffff'), strokeWidth=2))
    
    # Y軸標籤
    for i, label in enumerate(['低', '中', '高']):
        y = chart_bottom + (chart_height / 2) * i
        d.add(String(chart_left - 10, y, label, 
                     fontSize=9, fontName='SimSun', textAnchor='end', fillColor=GRAY))
    
    return d

def create_liunian_chart(liunian_data: list, width=500, height=180) -> Drawing:
    """
    創建流年運勢圖
    liunian_data: [{'year': 2026, 'score': 70, 'element': '木'}, ...]
    """
    d = Drawing(width, height)
    
    # 背景
    d.add(Rect(0, 0, width, height, fillColor=HexColor('#fafafa'), strokeColor=None))
    
    # 標題
    d.add(String(width / 2, height - 20, '流年運勢預測', 
                 fontSize=14, fontName='SimHei', textAnchor='middle', fillColor=GRAY))
    
    if not liunian_data:
        return d
    
    # 繪製區域
    chart_left = 50
    chart_bottom = 40
    chart_height = height - 80
    bar_width = (width - 100) / len(liunian_data) * 0.7
    gap = (width - 100) / len(liunian_data) * 0.3
    
    element_colors = {
        '木': HexColor('#22c55e'),
        '火': HexColor('#ef4444'),
        '土': HexColor('#eab308'),
        '金': HexColor('#94a3b8'),
        '水': HexColor('#3b82f6'),
    }
    
    for i, item in enumerate(liunian_data):
        x = chart_left + i * (bar_width + gap)
        score = item.get('score', 50)
        bar_height = (score / 100) * chart_height
        color = element_colors.get(item.get('element', '木'), PURPLE)
        
        # 柱子
        d.add(Rect(x, chart_bottom, bar_width, bar_height, 
                   fillColor=color, strokeColor=None, rx=3, ry=3))
        
        # 分數
        d.add(String(x + bar_width / 2, chart_bottom + bar_height + 5, f'{score}',
                     fontSize=9, fontName='SimHei', textAnchor='middle', fillColor=GRAY))
        
        # 年份
        d.add(String(x + bar_width / 2, chart_bottom - 15, str(item['year']),
                     fontSize=9, fontName='SimSun', textAnchor='middle', fillColor=GRAY))
    
    return d

def create_wuxing_radar(stats: dict, size=200) -> Drawing:
    """
    創建五行雷達圖
    stats: {'木': 2, '火': 3, '土': 1, '金': 2, '水': 2}
    """
    import math
    
    d = Drawing(size, size)
    cx, cy = size / 2, size / 2
    radius = size / 2 - 30
    
    # 背景圓
    for r in [radius * 0.33, radius * 0.66, radius]:
        d.add(Circle(cx, cy, r, fillColor=None, strokeColor=LIGHT_GRAY, strokeWidth=0.5))
    
    elements = ['木', '火', '土', '金', '水']
    element_colors = {
        '木': HexColor('#22c55e'),
        '火': HexColor('#ef4444'),
        '土': HexColor('#eab308'),
        '金': HexColor('#94a3b8'),
        '水': HexColor('#3b82f6'),
    }
    
    max_val = max(stats.values()) if stats.values() else 1
    
    # 軸線和標籤
    points = []
    for i, elem in enumerate(elements):
        angle = math.radians(90 - i * 72)
        
        # 軸線
        ex = cx + radius * math.cos(angle)
        ey = cy + radius * math.sin(angle)
        d.add(Line(cx, cy, ex, ey, strokeColor=LIGHT_GRAY, strokeWidth=0.5))
        
        # 標籤
        lx = cx + (radius + 15) * math.cos(angle)
        ly = cy + (radius + 15) * math.sin(angle)
        d.add(String(lx, ly, elem, fontSize=10, fontName='SimHei', 
                     textAnchor='middle', fillColor=element_colors[elem]))
        
        # 數據點
        val = stats.get(elem, 0)
        r = (val / max_val) * radius if max_val > 0 else 0
        px = cx + r * math.cos(angle)
        py = cy + r * math.sin(angle)
        points.append((px, py))
    
    # 連接數據點形成多邊形
    if len(points) > 2:
        path_data = f'M {points[0][0]} {points[0][1]} '
        for p in points[1:]:
            path_data += f'L {p[0]} {p[1]} '
        path_data += 'Z'
        
        # 填充
        from reportlab.graphics.shapes import Polygon
        poly_points = []
        for p in points:
            poly_points.extend([p[0], p[1]])
        d.add(Polygon(poly_points, fillColor=HexColor('#667eea33'), 
                      strokeColor=PURPLE, strokeWidth=2))
    
    # 數據點
    for px, py in points:
        d.add(Circle(px, py, 4, fillColor=PURPLE, strokeColor=HexColor('#ffffff'), strokeWidth=1))
    
    return d

print("✓ 報告圖表模組已載入")
