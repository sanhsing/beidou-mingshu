"""
PDF報告白話區塊
pdf_vernacular_section.py | 2026-02-18
"""
from typing import Dict, List, Any

# 導入白話資料
try:
    from classical_enhancement import (
        SHISHEN_GLOSSARY, BAGUA_GLOSSARY, GEJU_GLOSSARY,
        GONGWEI_GLOSSARY, ZIWEI_STAR_GLOSSARY
    )
    HAS_GLOSSARY = True
except ImportError:
    HAS_GLOSSARY = False

def create_shishen_table_data(shishen_list: List[str]) -> List[List[str]]:
    """建立十神白話表格數據"""
    if not HAS_GLOSSARY:
        return []
    
    data = [["十神", "白話含義", "場論詮釋", "調場建議"]]
    
    for ss in shishen_list:
        if ss in SHISHEN_GLOSSARY:
            g = SHISHEN_GLOSSARY[ss]
            data.append([
                ss,
                g.vernacular,
                g.field_theory[:30] + "..." if len(g.field_theory) > 30 else g.field_theory,
                g.remedy[:25] + "..." if len(g.remedy) > 25 else g.remedy
            ])
    return data

def create_geju_data(geju_name: str) -> Dict:
    """建立格局白話數據"""
    if not HAS_GLOSSARY or geju_name not in GEJU_GLOSSARY:
        return {}
    
    g = GEJU_GLOSSARY[geju_name]
    return {
        "name": geju_name,
        "vernacular": g.vernacular,
        "field_theory": g.field_theory,
        "condition": g.condition,
        "modern_career": g.modern_career,
        "yongshen_tip": g.yongshen_tip,
        "strength": g.strength,
        "weakness": g.weakness
    }

def create_gongwei_table_data(gongwei_list: List[str]) -> List[List[str]]:
    """建立宮位白話表格數據"""
    if not HAS_GLOSSARY:
        return []
    
    data = [["宮位", "場論角色", "白話含義", "對沖宮位"]]
    
    for gong in gongwei_list:
        if gong in GONGWEI_GLOSSARY:
            g = GONGWEI_GLOSSARY[gong]
            data.append([
                gong,
                g.field_role.split("(")[0].strip(),
                g.vernacular,
                g.opposite.split("（")[0].strip() if "（" in g.opposite else g.opposite
            ])
    return data

def create_bagua_data(gua_name: str) -> Dict:
    """建立八卦白話數據"""
    if not HAS_GLOSSARY or gua_name not in BAGUA_GLOSSARY:
        return {}
    
    g = BAGUA_GLOSSARY[gua_name]
    return {
        "name": gua_name,
        "symbol": g.symbol,
        "vernacular": g.vernacular,
        "field_theory": g.field_theory,
        "modern_analogy": g.modern_analogy,
        "strength": g.strength,
        "weakness": g.weakness
    }

def create_methodology_text() -> str:
    """建立方法論說明文字"""
    return """
三層詮釋體系：
1. 古典原文：典籍引用，標明出處
2. 白話翻譯：讓一般人看得懂
3. 場論詮釋：用現代語言重新理解

核心定位：術數是個人化決策框架生成器，與天氣預報同構。
提供機率性參考，不做命定式裁決。
"""

def get_vernacular_report_data(
    shishen_list: List[str] = None,
    geju_name: str = None,
    gongwei_list: List[str] = None,
    bagua_name: str = None
) -> Dict:
    """獲取完整白話報告數據"""
    return {
        "methodology": create_methodology_text(),
        "shishen": create_shishen_table_data(shishen_list or []),
        "geju": create_geju_data(geju_name) if geju_name else {},
        "gongwei": create_gongwei_table_data(gongwei_list or []),
        "bagua": create_bagua_data(bagua_name) if bagua_name else {}
    }

print("PDF白話區塊已載入")
