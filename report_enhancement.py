"""
報告增強整合器
report_enhancement.py | @星殼 @璃語 | 2026-02-18

整合 classical_enhancement v2.0 到報告生成流程
"""
from typing import Dict, List, Any, Optional

# 導入增強模組
try:
    from classical_enhancement import (
        get_shishen_glossary,
        get_ziwei_star_glossary,
        get_all_shishen_vernacular,
        get_all_ziwei_vernacular,
        SHISHEN_GLOSSARY,
        ZIWEI_STAR_GLOSSARY,
        SHISHEN_XTFS_MAPPING,
        SHISHEN_FIELD_DIAGNOSIS,
        WUXING_TRAITS
    )
    HAS_ENHANCEMENT = True
except ImportError:
    HAS_ENHANCEMENT = False

# ════════════════════════════════════════════════════════════════════
# 報告增強函數
# ════════════════════════════════════════════════════════════════════

def enhance_bazi_report(raw_report: Dict) -> Dict:
    """
    增強八字報告內容
    
    添加：
    - 十神白話翻譯
    - 場論詮釋
    - 場態分析
    - 調場建議
    """
    if not HAS_ENHANCEMENT:
        return raw_report
    
    enhanced = raw_report.copy()
    
    # 添加十神白話區塊
    if "shishen" in raw_report or "ten_gods" in raw_report:
        shishen_list = raw_report.get("shishen", raw_report.get("ten_gods", []))
        vernacular_section = []
        
        for ss in shishen_list:
            if isinstance(ss, str) and ss in SHISHEN_GLOSSARY:
                g = SHISHEN_GLOSSARY[ss]
                vernacular_section.append({
                    "name": ss,
                    "vernacular": g.vernacular,
                    "field_theory": g.field_theory,
                    "modern_analogy": g.modern_analogy,
                    "field_states": {
                        "場增強時": g.field_strong,
                        "場過強時": g.field_excess,
                        "場過弱時": g.field_weak,
                    },
                    "remedy": g.remedy,
                })
        
        enhanced["vernacular_section"] = {
            "title": "【白話解讀】",
            "subtitle": "十神 = 能量的動態特徵",
            "items": vernacular_section,
        }
    
    # 添加五行場論區塊
    if "day_master_wx" in raw_report:
        wx = raw_report["day_master_wx"]
        if wx in WUXING_TRAITS:
            trait = WUXING_TRAITS[wx]
            enhanced["wuxing_field_theory"] = {
                "title": "【五行場論】",
                "wuxing": wx,
                "strength": trait["strength"],
                "weakness": trait["weakness"],
                "opportunity": trait["opportunity"],
                "threat": trait["threat"],
            }
    
    # 添加方法論標記
    enhanced["methodology_note"] = {
        "layer_1": "古典原文：典籍可查",
        "layer_2": "白話翻譯：人人可懂",
        "layer_3": "場論詮釋：現代語言",
        "principle": "術數是個人化決策框架生成器",
        "disclaimer": "提供機率性參考，不做命定式裁決",
    }
    
    return enhanced

def enhance_ziwei_report(raw_report: Dict) -> Dict:
    """
    增強紫微報告內容
    
    添加：
    - 星曜白話翻譯
    - 場論詮釋
    - 優勢/風險分析
    """
    if not HAS_ENHANCEMENT:
        return raw_report
    
    enhanced = raw_report.copy()
    
    # 添加星曜白話區塊
    stars = raw_report.get("stars", raw_report.get("ming_stars", []))
    if stars:
        vernacular_section = []
        
        for star in stars:
            if isinstance(star, str) and star in ZIWEI_STAR_GLOSSARY:
                s = ZIWEI_STAR_GLOSSARY[star]
                vernacular_section.append({
                    "name": star,
                    "wuxing": s.wuxing,
                    "vernacular": s.vernacular,
                    "field_theory": s.field_theory,
                    "modern_career": s.modern_career,
                    "strength": s.strength,
                    "weakness": s.weakness,
                })
        
        enhanced["vernacular_section"] = {
            "title": "【白話解讀】",
            "subtitle": "星曜 = 性格特質的投射",
            "items": vernacular_section,
        }
    
    # 添加方法論標記
    enhanced["methodology_note"] = {
        "layer_1": "古典原文：典籍可查",
        "layer_2": "白話翻譯：人人可懂",
        "layer_3": "場論詮釋：現代語言",
        "principle": "術數是個人化決策框架生成器",
        "disclaimer": "提供機率性參考，不做命定式裁決",
    }
    
    return enhanced

def get_vernacular_summary(shishen_list: List[str]) -> str:
    """
    生成十神白話摘要（用於報告首頁）
    """
    if not HAS_ENHANCEMENT:
        return ""
    
    summaries = []
    for ss in shishen_list[:3]:  # 取前三個
        if ss in SHISHEN_GLOSSARY:
            g = SHISHEN_GLOSSARY[ss]
            summaries.append(f"【{ss}】{g.vernacular}")
    
    return " | ".join(summaries)

def get_field_theory_summary(wuxing: str) -> str:
    """
    生成五行場論摘要
    """
    if not HAS_ENHANCEMENT or wuxing not in WUXING_TRAITS:
        return ""
    
    trait = WUXING_TRAITS[wuxing]
    return f"日主屬{wuxing}，核心特質：{trait['strength']}。機會領域：{trait['opportunity']}。"

def format_report_section(title: str, items: List[Dict], format_type: str = "text") -> str:
    """
    格式化報告區塊
    
    format_type: "text" | "html" | "markdown"
    """
    if format_type == "text":
        lines = [f"\n{'═' * 60}", f"  {title}", f"{'═' * 60}"]
        for item in items:
            lines.append(f"\n【{item.get('name', '')}】")
            lines.append(f"  白話：{item.get('vernacular', '')}")
            lines.append(f"  場論：{item.get('field_theory', '')}")
            if 'remedy' in item:
                lines.append(f"  調場：{item.get('remedy', '')}")
        return "\n".join(lines)
    
    elif format_type == "html":
        html = f"<div class='section'><h3>{title}</h3>"
        for item in items:
            html += f"""
            <div class='item'>
                <h4>{item.get('name', '')}</h4>
                <p><strong>白話：</strong>{item.get('vernacular', '')}</p>
                <p><strong>場論：</strong>{item.get('field_theory', '')}</p>
            </div>
            """
        html += "</div>"
        return html
    
    elif format_type == "markdown":
        md = f"\n## {title}\n\n"
        for item in items:
            md += f"### {item.get('name', '')}\n\n"
            md += f"- **白話**：{item.get('vernacular', '')}\n"
            md += f"- **場論**：{item.get('field_theory', '')}\n"
            if 'remedy' in item:
                md += f"- **調場**：{item.get('remedy', '')}\n"
            md += "\n"
        return md
    
    return ""

# ════════════════════════════════════════════════════════════════════
# 模組載入
# ════════════════════════════════════════════════════════════════════

print(f"✓ 報告增強整合器已載入 | enhancement: {'✓' if HAS_ENHANCEMENT else '✗'}")
