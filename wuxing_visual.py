#!/usr/bin/env python3
"""
wuxing_visual.py - 五行互動視覺圖生成器
北斗命數 v3.1 商業版

品牌核心資產：把抽象命理 → 變成「結構模型圖」
差異化：一般命理畫五行圖是「比例」，我們畫的是「流動」

@星殼 × @璃語
"""

from typing import Dict, List, Optional
import math

# ============================================================
# L0: 五行視覺配置
# ============================================================

WUXING_COLORS = {
    "木": {"fill": "#4CAF50", "text": "#FFFFFF", "name": "生長場"},
    "火": {"fill": "#FF5722", "text": "#FFFFFF", "name": "輻射場"},
    "土": {"fill": "#795548", "text": "#FFFFFF", "name": "承載場"},
    "金": {"fill": "#9E9E9E", "text": "#FFFFFF", "name": "收斂場"},
    "水": {"fill": "#2196F3", "text": "#FFFFFF", "name": "流動場"},
}

# 箭頭顏色
ARROW_COLORS = {
    "sheng": "#2196F3",    # 生 = 藍色
    "ke": "#F44336",       # 剋 = 紅色
    "reverse": "#FF9800",  # 反剋 = 橘色
}

# 五行位置（圓形排列）
WUXING_POSITIONS = {
    "木": {"angle": 90, "x": 200, "y": 50},
    "火": {"angle": 162, "x": 50, "y": 140},
    "土": {"angle": 234, "x": 90, "y": 290},
    "金": {"angle": 306, "x": 310, "y": 290},
    "水": {"angle": 18, "x": 350, "y": 140},
}

# ============================================================
# L1: SVG 元件生成
# ============================================================

def create_svg_header(width: int = 500, height: int = 400) -> str:
    """創建 SVG 頭部"""
    return f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}">
  <defs>
    <marker id="arrow-sheng" markerWidth="10" markerHeight="10" refX="9" refY="3" orient="auto" markerUnits="strokeWidth">
      <path d="M0,0 L0,6 L9,3 z" fill="{ARROW_COLORS['sheng']}"/>
    </marker>
    <marker id="arrow-ke" markerWidth="10" markerHeight="10" refX="9" refY="3" orient="auto" markerUnits="strokeWidth">
      <path d="M0,0 L0,6 L9,3 z" fill="{ARROW_COLORS['ke']}"/>
    </marker>
    <marker id="arrow-reverse" markerWidth="10" markerHeight="10" refX="9" refY="3" orient="auto" markerUnits="strokeWidth">
      <path d="M0,0 L0,6 L9,3 z" fill="{ARROW_COLORS['reverse']}"/>
    </marker>
    <filter id="shadow" x="-20%" y="-20%" width="140%" height="140%">
      <feDropShadow dx="2" dy="2" stdDeviation="3" flood-opacity="0.3"/>
    </filter>
  </defs>
  <rect width="100%" height="100%" fill="#FAFAFA"/>
'''

def create_wuxing_circle(wx: str, x: int, y: int, strength: int = 50, is_daymaster: bool = False) -> str:
    """創建五行圓形節點"""
    colors = WUXING_COLORS[wx]
    radius = 35 if is_daymaster else 25
    stroke = 'stroke="#1E3A5F" stroke-width="3"' if is_daymaster else ""
    
    # 強度環
    strength_radius = radius + 8
    strength_arc = strength / 100 * 2 * math.pi
    
    return f'''
  <!-- {wx} -->
  <g transform="translate({x}, {y})">
    <!-- 強度環 -->
    <circle r="{strength_radius}" fill="none" stroke="#E0E0E0" stroke-width="4"/>
    <circle r="{strength_radius}" fill="none" stroke="{colors['fill']}" stroke-width="4" 
            stroke-dasharray="{strength_arc * strength_radius} {(2*math.pi - strength_arc) * strength_radius}"
            transform="rotate(-90)"/>
    <!-- 主圓 -->
    <circle r="{radius}" fill="{colors['fill']}" {stroke} filter="url(#shadow)"/>
    <text y="5" text-anchor="middle" fill="{colors['text']}" font-size="18" font-weight="bold">{wx}</text>
    {'<text y="25" text-anchor="middle" fill="#1E3A5F" font-size="10">日主</text>' if is_daymaster else ''}
  </g>
'''

def create_arrow(x1: int, y1: int, x2: int, y2: int, arrow_type: str, label: str = "") -> str:
    """創建箭頭連線"""
    color = ARROW_COLORS.get(arrow_type, ARROW_COLORS["sheng"])
    marker = f"url(#arrow-{arrow_type})"
    dash = 'stroke-dasharray="5,5"' if arrow_type == "reverse" else ""
    
    # 計算中點用於標籤
    mx, my = (x1 + x2) / 2, (y1 + y2) / 2
    
    # 縮短箭頭（不要碰到圓）
    dx, dy = x2 - x1, y2 - y1
    length = math.sqrt(dx*dx + dy*dy)
    offset = 40  # 圓半徑 + 間距
    
    nx1 = x1 + (dx / length) * offset
    ny1 = y1 + (dy / length) * offset
    nx2 = x2 - (dx / length) * offset
    ny2 = y2 - (dy / length) * offset
    
    return f'''
  <line x1="{nx1}" y1="{ny1}" x2="{nx2}" y2="{ny2}" 
        stroke="{color}" stroke-width="2" marker-end="{marker}" {dash}/>
  {f'<text x="{mx}" y="{my-5}" text-anchor="middle" fill="{color}" font-size="10">{label}</text>' if label else ''}
'''

def create_center_label(day_wx: str, strength_level: str) -> str:
    """創建中心日主標籤"""
    return f'''
  <g transform="translate(200, 180)">
    <rect x="-60" y="-20" width="120" height="40" rx="5" fill="#1E3A5F" filter="url(#shadow)"/>
    <text y="5" text-anchor="middle" fill="white" font-size="14" font-weight="bold">
      {day_wx}｜{WUXING_COLORS[day_wx]['name']}
    </text>
  </g>
  <text x="200" y="220" text-anchor="middle" fill="#666" font-size="12">
    能量傾向：{strength_level}
  </text>
'''

def create_legend() -> str:
    """創建圖例"""
    return f'''
  <g transform="translate(380, 320)">
    <text x="0" y="0" fill="#333" font-size="10" font-weight="bold">圖例</text>
    <line x1="0" y1="15" x2="30" y2="15" stroke="{ARROW_COLORS['sheng']}" stroke-width="2"/>
    <text x="35" y="18" fill="#666" font-size="9">生（能量流出）</text>
    <line x1="0" y1="30" x2="30" y2="30" stroke="{ARROW_COLORS['ke']}" stroke-width="2"/>
    <text x="35" y="33" fill="#666" font-size="9">剋（壓力來源）</text>
    <line x1="0" y1="45" x2="30" y2="45" stroke="{ARROW_COLORS['reverse']}" stroke-width="2" stroke-dasharray="5,5"/>
    <text x="35" y="48" fill="#666" font-size="9">反剋（阻力轉推力）</text>
  </g>
'''

# ============================================================
# L2: 完整圖生成
# ============================================================

def generate_wuxing_flow_svg(
    day_wx: str,
    wuxing_count: Dict[str, int],
    yongshen: str,
    jishen: str,
    is_strong: bool,
    strength_level: str = "偏強"
) -> str:
    """
    生成五行流動 SVG 圖
    
    差異化：
    - 一般命理畫五行圖是「比例」
    - 我們畫的是「流動」
    """
    
    # 計算各五行強度百分比
    total = sum(wuxing_count.values()) or 1
    strengths = {wx: (count / total) * 100 for wx, count in wuxing_count.items()}
    
    # 相生相剋關係
    SHENG = {"木": "火", "火": "土", "土": "金", "金": "水", "水": "木"}
    KE = {"木": "土", "土": "水", "水": "火", "火": "金", "金": "木"}
    
    svg = create_svg_header(500, 400)
    
    # 標題
    svg += '''
  <text x="200" y="25" text-anchor="middle" fill="#1E3A5F" font-size="16" font-weight="bold">
    五行流動結構圖
  </text>
'''
    
    # 畫五行節點
    positions = {
        "木": (200, 60),
        "火": (80, 150),
        "土": (120, 280),
        "金": (280, 280),
        "水": (320, 150),
    }
    
    for wx, (x, y) in positions.items():
        is_dm = (wx == day_wx)
        strength = min(100, max(20, strengths.get(wx, 30) * 2))
        svg += create_wuxing_circle(wx, x, y, int(strength), is_dm)
    
    # 畫主要流動箭頭（日主 → 用神）
    wo_sheng = SHENG[day_wx]
    dx, dy = positions[day_wx]
    yx, yy = positions[wo_sheng]
    svg += create_arrow(dx, dy, yx, yy, "sheng", "流動")
    
    # 畫用神 → 財的箭頭
    yong_sheng = SHENG.get(wo_sheng)
    if yong_sheng:
        yx2, yy2 = positions[yong_sheng]
        svg += create_arrow(yx, yy, yx2, yy2, "sheng", "")
    
    # 畫剋我的箭頭
    ke_wo = [k for k, v in KE.items() if v == day_wx]
    if ke_wo:
        kx, ky = positions[ke_wo[0]]
        svg += create_arrow(kx, ky, dx, dy, "ke", "壓力")
    
    # 畫反剋（如果忌神過強）
    if jishen and wuxing_count.get(jishen, 0) > 2:
        jx, jy = positions.get(jishen, (200, 200))
        svg += create_arrow(jx, jy, dx, dy, "reverse", "反壓")
    
    # 中心標籤
    svg += create_center_label(day_wx, strength_level)
    
    # 圖例
    svg += create_legend()
    
    # 底部說明
    svg += f'''
  <text x="200" y="380" text-anchor="middle" fill="#999" font-size="10">
    用神：{yongshen}（流動出口）｜忌神：{jishen}（能量阻塞）
  </text>
'''
    
    svg += '</svg>'
    
    return svg


def generate_wuxing_flow_ascii(
    day_wx: str,
    yongshen: str,
    jishen: str,
    is_strong: bool
) -> str:
    """生成 ASCII 版五行流動圖（用於文字報告）"""
    
    SHENG = {"木": "火", "火": "土", "土": "金", "金": "水", "水": "木"}
    KE = {"木": "土", "土": "水", "水": "火", "火": "金", "金": "木"}
    SHENG_WO = {v: k for k, v in SHENG.items()}
    
    wo_sheng = SHENG[day_wx]
    sheng_wo = SHENG_WO.get(day_wx, "?")
    ke_wo = [k for k, v in KE.items() if v == day_wx][0] if any(v == day_wx for v in KE.values()) else "?"
    wo_sheng_sheng = SHENG.get(wo_sheng, "?")
    
    if is_strong:
        diagram = f"""
    ╔═══════════════════════════════════════════════════════════════╗
    ║                    五行流動結構圖                              ║
    ╚═══════════════════════════════════════════════════════════════╝
    
                        {ke_wo}（剋我：壓力場）
                           │
                           ▼
    {sheng_wo}（印星：保護場）──▶【 {day_wx} 】──▶ {wo_sheng}（輸出場）──▶ {wo_sheng_sheng}（財場）
                           ▲         │
                           └─────────┘
                              ↑
                         最佳流動路徑
    
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    ▶ 藍色箭頭：生（能量流出）    
    ▶ 紅色箭頭：剋（壓力來源）
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
    else:
        diagram = f"""
    ╔═══════════════════════════════════════════════════════════════╗
    ║                    五行流動結構圖                              ║
    ╚═══════════════════════════════════════════════════════════════╝
    
                        {ke_wo}（剋我：壓力場）
                           │
                           ▼
    {sheng_wo}（印星：保護場）──▶【 {day_wx} 】
          ▲                    
          │                    
      最佳補充路徑
    
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    身弱：需要生扶，減少輸出
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
    
    return diagram


# ============================================================
# L3: HTML 嵌入版本
# ============================================================

def generate_wuxing_html(
    day_wx: str,
    wuxing_count: Dict[str, int],
    yongshen: str,
    jishen: str,
    is_strong: bool,
    strength_level: str = "偏強"
) -> str:
    """生成可嵌入 HTML 的五行圖"""
    
    svg = generate_wuxing_flow_svg(
        day_wx, wuxing_count, yongshen, jishen, is_strong, strength_level
    )
    
    html = f'''
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>五行流動結構圖</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            margin: 0;
            background: #f5f5f5;
        }}
        .container {{
            background: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }}
        .title {{
            text-align: center;
            color: #1E3A5F;
            margin-bottom: 20px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h2 class="title">個人能量流動結構圖</h2>
        {svg}
    </div>
</body>
</html>
'''
    return html


# ============================================================
# 測試
# ============================================================

if __name__ == "__main__":
    print("=== 五行流動圖測試 ===\n")
    
    # 測試數據
    day_wx = "金"
    wuxing_count = {"木": 1, "火": 0, "土": 2, "金": 2, "水": 3}
    yongshen = "水"
    jishen = "土"
    is_strong = True
    
    # 生成 ASCII 版
    print(generate_wuxing_flow_ascii(day_wx, yongshen, jishen, is_strong))
    
    # 生成 SVG 版
    svg = generate_wuxing_flow_svg(day_wx, wuxing_count, yongshen, jishen, is_strong)
    
    # 保存
    with open("/tmp/wuxing_flow.svg", "w", encoding="utf-8") as f:
        f.write(svg)
    print("✅ SVG 已保存到 /tmp/wuxing_flow.svg")
    
    # 生成 HTML 版
    html = generate_wuxing_html(day_wx, wuxing_count, yongshen, jishen, is_strong)
    with open("/tmp/wuxing_flow.html", "w", encoding="utf-8") as f:
        f.write(html)
    print("✅ HTML 已保存到 /tmp/wuxing_flow.html")
