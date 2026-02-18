"""
報告樣式模組 (增強版)
M6.1-M6.4 | @璃語 | 2026-02-17
PYLIB: pdf_report_api, wuxing_visual
"""
from reportlab.lib.colors import HexColor, Color
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY

# === 品牌色彩 ===
COLORS = {
    'primary': HexColor('#667eea'),
    'secondary': HexColor('#764ba2'),
    'gold': HexColor('#D4AF37'),
    'dark': HexColor('#1a1a2e'),
    'light': HexColor('#f8f9fa'),
    'wood': HexColor('#22c55e'),
    'fire': HexColor('#ef4444'),
    'earth': HexColor('#eab308'),
    'metal': HexColor('#94a3b8'),
    'water': HexColor('#3b82f6'),
}

# === 五行顏色映射 ===
WUXING_COLORS = {
    '木': COLORS['wood'],
    '火': COLORS['fire'],
    '土': COLORS['earth'],
    '金': COLORS['metal'],
    '水': COLORS['water'],
}

# === 段落樣式 ===
STYLES_CONFIG = {
    'title': {
        'fontSize': 28,
        'fontName': 'SimHei',
        'textColor': COLORS['dark'],
        'alignment': TA_CENTER,
        'spaceAfter': 20,
    },
    'subtitle': {
        'fontSize': 16,
        'fontName': 'SimSun',
        'textColor': COLORS['primary'],
        'alignment': TA_CENTER,
        'spaceAfter': 30,
    },
    'heading1': {
        'fontSize': 18,
        'fontName': 'SimHei',
        'textColor': COLORS['primary'],
        'spaceBefore': 20,
        'spaceAfter': 12,
        'leftIndent': 0,
    },
    'heading2': {
        'fontSize': 14,
        'fontName': 'SimHei',
        'textColor': COLORS['secondary'],
        'spaceBefore': 15,
        'spaceAfter': 8,
        'leftIndent': 10,
    },
    'body': {
        'fontSize': 11,
        'fontName': 'SimSun',
        'textColor': COLORS['dark'],
        'alignment': TA_JUSTIFY,
        'spaceBefore': 6,
        'spaceAfter': 6,
        'leading': 18,
    },
    'quote': {
        'fontSize': 10,
        'fontName': 'SimKai',
        'textColor': HexColor('#666666'),
        'alignment': TA_CENTER,
        'spaceBefore': 10,
        'spaceAfter': 10,
        'leftIndent': 30,
        'rightIndent': 30,
    },
    'footer': {
        'fontSize': 9,
        'fontName': 'SimSun',
        'textColor': HexColor('#999999'),
        'alignment': TA_CENTER,
    },
}

def create_paragraph_styles():
    """創建段落樣式字典"""
    styles = {}
    for name, config in STYLES_CONFIG.items():
        styles[name] = ParagraphStyle(name, **config)
    return styles

# === 封面設計 ===
def draw_cover(canvas, doc, title, subtitle, birth_info):
    """繪製報告封面"""
    width, height = doc.pagesize
    
    # 漸層背景 (模擬)
    canvas.setFillColor(COLORS['primary'])
    canvas.rect(0, height - 200, width, 200, fill=1, stroke=0)
    
    # 金色裝飾線
    canvas.setStrokeColor(COLORS['gold'])
    canvas.setLineWidth(3)
    canvas.line(50, height - 220, width - 50, height - 220)
    
    # 品牌 Logo
    canvas.setFillColor(HexColor('#ffffff'))
    canvas.setFont('SimHei', 36)
    canvas.drawCentredString(width / 2, height - 100, '🌟 北斗命數')
    
    # 標題
    canvas.setFillColor(COLORS['dark'])
    canvas.setFont('SimHei', 28)
    canvas.drawCentredString(width / 2, height - 300, title)
    
    # 副標題
    canvas.setFont('SimSun', 14)
    canvas.setFillColor(COLORS['secondary'])
    canvas.drawCentredString(width / 2, height - 340, subtitle)
    
    # 出生資訊
    canvas.setFont('SimSun', 12)
    canvas.setFillColor(COLORS['dark'])
    y = height - 420
    for line in birth_info:
        canvas.drawCentredString(width / 2, y, line)
        y -= 20
    
    # 生成日期
    from datetime import datetime
    canvas.setFont('SimSun', 10)
    canvas.setFillColor(HexColor('#999999'))
    canvas.drawCentredString(width / 2, 100, f'報告生成日期：{datetime.now().strftime("%Y年%m月%d日")}')
    
    # 底部裝飾
    canvas.setStrokeColor(COLORS['gold'])
    canvas.setLineWidth(1)
    canvas.line(100, 80, width - 100, 80)

# === 頁眉頁腳 ===
def draw_header_footer(canvas, doc, page_num, total_pages=None):
    """繪製頁眉頁腳"""
    width, height = doc.pagesize
    
    # 頁眉
    canvas.setStrokeColor(COLORS['primary'])
    canvas.setLineWidth(0.5)
    canvas.line(50, height - 50, width - 50, height - 50)
    
    canvas.setFont('SimSun', 9)
    canvas.setFillColor(COLORS['primary'])
    canvas.drawString(50, height - 40, '🌟 北斗命數')
    canvas.drawRightString(width - 50, height - 40, '專業命理分析報告')
    
    # 頁腳
    canvas.line(50, 50, width - 50, 50)
    canvas.setFillColor(HexColor('#999999'))
    page_text = f'第 {page_num} 頁' + (f' / 共 {total_pages} 頁' if total_pages else '')
    canvas.drawCentredString(width / 2, 35, page_text)
    canvas.drawString(50, 35, '© 2026 北斗命數')
    canvas.drawRightString(width - 50, 35, '僅供參考')

# === 五行圓餅圖 ===
def draw_wuxing_pie(canvas, x, y, stats, size=150):
    """繪製五行圓餅圖"""
    import math
    
    total = sum(stats.values())
    if total == 0:
        return
    
    start_angle = 90
    cx, cy = x + size / 2, y + size / 2
    radius = size / 2 - 10
    
    elements = ['木', '火', '土', '金', '水']
    for elem in elements:
        count = stats.get(elem, 0)
        if count == 0:
            continue
        
        sweep = (count / total) * 360
        color = WUXING_COLORS[elem]
        
        canvas.setFillColor(color)
        canvas.wedge(cx - radius, cy - radius, cx + radius, cy + radius,
                     start_angle, sweep, fill=1, stroke=0)
        
        # 標籤
        mid_angle = math.radians(start_angle + sweep / 2)
        label_r = radius * 0.7
        lx = cx + label_r * math.cos(mid_angle)
        ly = cy + label_r * math.sin(mid_angle)
        
        canvas.setFillColor(HexColor('#ffffff'))
        canvas.setFont('SimHei', 10)
        canvas.drawCentredString(lx, ly, f'{elem}{count}')
        
        start_angle += sweep

# === 圖例 ===
def draw_wuxing_legend(canvas, x, y, stats):
    """繪製五行圖例"""
    elements = ['木', '火', '土', '金', '水']
    emojis = {'木': '🌳', '火': '🔥', '土': '🏔️', '金': '⚔️', '水': '💧'}
    
    for i, elem in enumerate(elements):
        count = stats.get(elem, 0)
        color = WUXING_COLORS[elem]
        
        # 色塊
        canvas.setFillColor(color)
        canvas.rect(x, y - i * 20, 15, 12, fill=1, stroke=0)
        
        # 文字
        canvas.setFillColor(COLORS['dark'])
        canvas.setFont('SimSun', 10)
        canvas.drawString(x + 20, y - i * 20, f'{emojis[elem]} {elem}: {count}')

print("✓ 報告樣式模組已載入")
