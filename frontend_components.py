"""
前端組件生成器
frontend_components.py | @璃語 @星殼 | 2026-02-18

生成：
- 白話卡片 HTML/React
- 場論圖表
- 十神/八卦/宮位視覺化
"""
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

# 導入白話資料
try:
    from classical_enhancement import (
        SHISHEN_GLOSSARY, BAGUA_GLOSSARY, GEJU_GLOSSARY, 
        GONGWEI_GLOSSARY, ZIWEI_STAR_GLOSSARY,
        get_shishen_glossary, get_bagua_glossary, get_gongwei_glossary
    )
    HAS_GLOSSARY = True
except ImportError:
    HAS_GLOSSARY = False

# ════════════════════════════════════════════════════════════════════
# 白話卡片 HTML 生成
# ════════════════════════════════════════════════════════════════════

def generate_shishen_card_html(shishen_name: str) -> str:
    """生成十神白話卡片 HTML"""
    if not HAS_GLOSSARY or shishen_name not in SHISHEN_GLOSSARY:
        return f"<div class='card error'>找不到：{shishen_name}</div>"
    
    g = SHISHEN_GLOSSARY[shishen_name]
    return f'''
<div class="shishen-card" data-shishen="{shishen_name}">
  <div class="card-header">
    <h3 class="shishen-name">{shishen_name}</h3>
    <span class="classical">{g.classical[:15]}...</span>
  </div>
  <div class="card-body">
    <div class="vernacular">
      <span class="label">白話</span>
      <p class="value">{g.vernacular}</p>
    </div>
    <div class="field-theory">
      <span class="label">場論</span>
      <p class="value">{g.field_theory}</p>
    </div>
    <div class="modern">
      <span class="label">現代</span>
      <p class="value">{g.modern_analogy}</p>
    </div>
  </div>
  <div class="card-footer">
    <div class="field-states">
      <span class="strong">✅ {g.field_strong}</span>
      <span class="excess">⚠️ {g.field_excess}</span>
      <span class="weak">❌ {g.field_weak}</span>
    </div>
    <div class="remedy">
      <span class="label">調場</span>
      <span class="value">{g.remedy}</span>
    </div>
  </div>
</div>
'''

def generate_bagua_card_html(gua_name: str) -> str:
    """生成八卦白話卡片 HTML"""
    if not HAS_GLOSSARY or gua_name not in BAGUA_GLOSSARY:
        return f"<div class='card error'>找不到：{gua_name}</div>"
    
    g = BAGUA_GLOSSARY[gua_name]
    return f'''
<div class="bagua-card" data-gua="{gua_name}">
  <div class="card-header">
    <span class="symbol">{g.symbol}</span>
    <h3 class="gua-name">{gua_name}卦</h3>
  </div>
  <div class="card-body">
    <div class="vernacular">
      <p class="value">{g.vernacular}</p>
    </div>
    <div class="field-theory">
      <span class="label">場論</span>
      <p class="value">{g.field_theory}</p>
    </div>
    <div class="modern">
      <span class="label">比喻</span>
      <p class="value">{g.modern_analogy}</p>
    </div>
  </div>
  <div class="card-footer">
    <span class="strength">✅ {g.strength}</span>
    <span class="weakness">❌ {g.weakness}</span>
  </div>
</div>
'''

def generate_gongwei_card_html(gong_name: str) -> str:
    """生成宮位場論卡片 HTML"""
    if not HAS_GLOSSARY or gong_name not in GONGWEI_GLOSSARY:
        return f"<div class='card error'>找不到：{gong_name}</div>"
    
    g = GONGWEI_GLOSSARY[gong_name]
    return f'''
<div class="gongwei-card" data-gong="{gong_name}">
  <div class="card-header">
    <h3 class="gong-name">{gong_name}</h3>
    <span class="field-role">{g.field_role}</span>
  </div>
  <div class="card-body">
    <div class="vernacular">
      <p class="value">{g.vernacular}</p>
    </div>
    <div class="field-trait">
      <span class="label">能量</span>
      <p class="value">{g.field_trait}</p>
    </div>
    <div class="modern">
      <span class="label">現代</span>
      <p class="value">{g.modern_meaning}</p>
    </div>
  </div>
  <div class="card-footer">
    <span class="opposite">對沖：{g.opposite}</span>
  </div>
</div>
'''

# ════════════════════════════════════════════════════════════════════
# 批量生成
# ════════════════════════════════════════════════════════════════════

def generate_all_shishen_cards() -> str:
    """生成所有十神卡片"""
    if not HAS_GLOSSARY:
        return "<div class='error'>白話模組未載入</div>"
    
    cards = [generate_shishen_card_html(name) for name in SHISHEN_GLOSSARY.keys()]
    return f'<div class="shishen-grid">{"".join(cards)}</div>'

def generate_all_bagua_cards() -> str:
    """生成所有八卦卡片"""
    if not HAS_GLOSSARY:
        return "<div class='error'>白話模組未載入</div>"
    
    cards = [generate_bagua_card_html(name) for name in BAGUA_GLOSSARY.keys()]
    return f'<div class="bagua-grid">{"".join(cards)}</div>'

def generate_all_gongwei_cards() -> str:
    """生成所有宮位卡片"""
    if not HAS_GLOSSARY:
        return "<div class='error'>白話模組未載入</div>"
    
    cards = [generate_gongwei_card_html(name) for name in GONGWEI_GLOSSARY.keys()]
    return f'<div class="gongwei-grid">{"".join(cards)}</div>'

# ════════════════════════════════════════════════════════════════════
# CSS 樣式
# ════════════════════════════════════════════════════════════════════

CARD_STYLES = '''
<style>
/* 卡片基礎樣式 */
.shishen-card, .bagua-card, .gongwei-card {
  border: 1px solid #e0e0e0;
  border-radius: 12px;
  padding: 16px;
  margin: 8px;
  background: linear-gradient(135deg, #fafafa 0%, #f5f5f5 100%);
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  transition: transform 0.2s, box-shadow 0.2s;
}

.shishen-card:hover, .bagua-card:hover, .gongwei-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 4px 16px rgba(0,0,0,0.15);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid #eee;
  padding-bottom: 12px;
  margin-bottom: 12px;
}

.card-header h3 {
  margin: 0;
  font-size: 1.25rem;
  color: #333;
}

.symbol {
  font-size: 2rem;
}

.label {
  display: inline-block;
  background: #e3f2fd;
  color: #1976d2;
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 0.75rem;
  margin-bottom: 4px;
}

.vernacular .value {
  font-size: 1.1rem;
  color: #1976d2;
  font-weight: 500;
}

.field-theory .value {
  font-size: 0.9rem;
  color: #666;
}

.card-footer {
  border-top: 1px solid #eee;
  padding-top: 12px;
  margin-top: 12px;
  font-size: 0.85rem;
}

.strong { color: #4caf50; }
.excess { color: #ff9800; }
.weak { color: #f44336; }

/* 網格佈局 */
.shishen-grid, .bagua-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 16px;
}

.gongwei-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 16px;
}
</style>
'''

# ════════════════════════════════════════════════════════════════════
# React 組件生成
# ════════════════════════════════════════════════════════════════════

def generate_react_shishen_component() -> str:
    """生成 React 十神卡片組件"""
    return '''
import React from 'react';

const ShiShenCard = ({ data }) => {
  const { name, vernacular, field_theory, modern_analogy, 
          field_strong, field_excess, field_weak, remedy } = data;
  
  return (
    <div className="shishen-card">
      <div className="card-header">
        <h3>{name}</h3>
      </div>
      <div className="card-body">
        <div className="vernacular">
          <span className="label">白話</span>
          <p>{vernacular}</p>
        </div>
        <div className="field-theory">
          <span className="label">場論</span>
          <p>{field_theory}</p>
        </div>
        <div className="modern">
          <span className="label">現代</span>
          <p>{modern_analogy}</p>
        </div>
      </div>
      <div className="card-footer">
        <div className="field-states">
          <span className="strong">✅ {field_strong}</span>
          <span className="excess">⚠️ {field_excess}</span>
          <span className="weak">❌ {field_weak}</span>
        </div>
        <div className="remedy">
          <span className="label">調場</span>
          <span>{remedy}</span>
        </div>
      </div>
    </div>
  );
};

export default ShiShenCard;
'''

# ════════════════════════════════════════════════════════════════════
# API 數據格式化
# ════════════════════════════════════════════════════════════════════

def format_for_frontend(glossary_type: str) -> Dict:
    """格式化白話資料供前端使用"""
    if not HAS_GLOSSARY:
        return {"error": "白話模組未載入"}
    
    if glossary_type == "shishen":
        return {
            "type": "shishen",
            "count": len(SHISHEN_GLOSSARY),
            "items": [
                {
                    "name": name,
                    "vernacular": g.vernacular,
                    "field_theory": g.field_theory,
                    "modern_analogy": g.modern_analogy,
                    "field_states": {
                        "strong": g.field_strong,
                        "excess": g.field_excess,
                        "weak": g.field_weak
                    },
                    "remedy": g.remedy
                }
                for name, g in SHISHEN_GLOSSARY.items()
            ]
        }
    elif glossary_type == "bagua":
        return {
            "type": "bagua",
            "count": len(BAGUA_GLOSSARY),
            "items": [
                {
                    "name": name,
                    "symbol": g.symbol,
                    "vernacular": g.vernacular,
                    "field_theory": g.field_theory,
                    "modern_analogy": g.modern_analogy,
                    "strength": g.strength,
                    "weakness": g.weakness
                }
                for name, g in BAGUA_GLOSSARY.items()
            ]
        }
    elif glossary_type == "gongwei":
        return {
            "type": "gongwei",
            "count": len(GONGWEI_GLOSSARY),
            "items": [
                {
                    "name": name,
                    "field_role": g.field_role,
                    "vernacular": g.vernacular,
                    "field_trait": g.field_trait,
                    "modern_meaning": g.modern_meaning,
                    "opposite": g.opposite
                }
                for name, g in GONGWEI_GLOSSARY.items()
            ]
        }
    return {"error": f"未知類型：{glossary_type}"}

print("✓ 前端組件生成器已載入")
print(f"  - HTML卡片: shishen/bagua/gongwei")
print(f"  - React組件: ShiShenCard")
print(f"  - CSS樣式: CARD_STYLES")
