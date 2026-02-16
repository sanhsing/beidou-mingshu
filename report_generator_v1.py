"""
完整命理報告生成器 report_generator.py v2.0
==========================================
整合四術分析，生成專業級完整命理報告
v2.0 新增：五行強弱、格局判斷、神煞分析、四化詳解、輔星分析

建立者：北斗 × 織明
日期：2026-02-07
XTF任務：E+B 融合
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime
from field_translation import (
    get_shishen_translation, get_bagua_translation, get_ziwei_star_translation,
    get_geju_translation, get_shuli_translation, stroke_to_wuxing,
    SHISHEN_TRANSLATION, BAGUA_TRANSLATION, ZIWEI_STAR_TRANSLATION, GEJU_TRANSLATION
)
from wuxing_core import (
    GAN, ZHI, GAN_WX, GAN_YY, ZHI_WX, ZODIAC,
    ten_god, ten_god_field, wx_relation_field, WX_FIELD, WX_SHENG, WX_KE
)

# v2.0 新增：進階分析模組
try:
    from bazi_advanced import (
        analyze_day_master_strength, determine_geju, 
        generate_shensha_analysis, SHENSHA_TRANSLATION, GEJU_DEFINITIONS
    )
    from ziwei_advanced import (
        generate_sihua_report, analyze_auxiliary_stars, get_sihua_info,
        SIHUA_TRANSLATION, AUXILIARY_STARS_TRANSLATION
    )
    ADVANCED_MODULES_LOADED = True
except ImportError:
    ADVANCED_MODULES_LOADED = False


# =============================================================================
# 數據類
# =============================================================================

@dataclass
class BirthData:
    """出生資料"""
    year: int
    month: int
    day: int
    hour: int
    gender: str
    name: Optional[str] = None
    is_lunar: bool = False  # True=農曆, False=西曆


@dataclass 
class BaziResult:
    """八字分析結果"""
    pillars: Dict[str, str]  # 四柱
    day_master: str  # 日主
    day_master_wx: str  # 日主五行
    shishen_analysis: List[Dict]  # 十神分析
    wuxing_count: Dict[str, int]  # 五行統計
    strong_weak: str  # 身強身弱
    geju: Optional[str]  # 格局
    geju_analysis: Optional[Dict]  # 格局分析


@dataclass
class ZiweiResult:
    """紫微分析結果"""
    ju_shu: str  # 局數
    ming_gong: str  # 命宮
    ming_stars: List[str]  # 命宮主星
    shen_gong: str  # 身宮
    shen_stars: List[str]  # 身宮主星
    sihua: Dict[str, str]  # 四化
    star_analysis: List[Dict]  # 主星分析
    twelve_gongs: Dict[str, Dict]  # 十二宮


@dataclass
class NameResult:
    """姓名分析結果"""
    name: str
    strokes: Dict[str, int]
    wuge: Dict[str, int]
    wuge_analysis: Dict[str, Dict]
    sancai: str
    sancai_analysis: Dict


@dataclass
class MeihuaResult:
    """梅花分析結果"""
    upper_gua: str
    lower_gua: str
    ben_gua: str
    dong_yao: int
    bian_gua: str
    upper_analysis: Dict
    lower_analysis: Dict
    judgment: str


# =============================================================================
# 報告模板
# =============================================================================

REPORT_SECTIONS = {
    "header": """
╔══════════════════════════════════════════════════════════════════╗
║                                                                  ║
║                    🌟 北 斗 命 數 分 析 報 告 🌟                   ║
║                                                                  ║
║                      場論詮釋版 v2.0                              ║
║                                                                  ║
╚══════════════════════════════════════════════════════════════════╝
""",
    "disclaimer": """
┌──────────────────────────────────────────────────────────────────┐
│  📐 認識論聲明                                                    │
│                                                                  │
│  術數是個人化決策框架生成器，與天氣預報同構                         │
│  ─ 提供機率性參考，不做命定式裁決                                  │
│  ─ 趨吉避凶：趨和避都是動詞，主語是人                              │
│  ─ 古法是根，場論是枝，用戶是花                                    │
└──────────────────────────────────────────────────────────────────┘
""",
}


# =============================================================================
# 報告生成器
# =============================================================================

class FullReportGenerator:
    """完整命理報告生成器"""
    
    def __init__(self):
        self.sections = []
    
    def add_section(self, title: str, content: str):
        """添加報告段落"""
        self.sections.append({"title": title, "content": content})
    
    def generate_basic_info(self, birth: BirthData, lunar_info: Dict) -> str:
        """生成基本資料區塊"""
        calendar_type = "農曆" if birth.is_lunar else "西曆"
        
        content = f"""
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃  📋 基本資料                                                      ┃
┣━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┫
┃                                                                  ┃
┃  姓名：{birth.name or '未提供':<20}  性別：{birth.gender}                   ┃
┃                                                                  ┃
┃  【輸入曆法】{calendar_type}                                          ┃
┃  {calendar_type}生日：{birth.year}年{birth.month}月{birth.day}日 {birth.hour}時              ┃
┃                                                                  ┃
┃  【轉換結果】                                                     ┃
┃  西曆：{lunar_info.get('solar', '')}                              ┃
┃  農曆：{lunar_info.get('lunar_str', '')}                          ┃
┃  生肖：{lunar_info.get('shengxiao', '')}                                    ┃
┃                                                                  ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
"""
        return content

    def generate_bazi_section(self, bazi: Dict, lunar_info: Dict) -> str:
        """生成八字分析區塊（v2.0 整合進階分析）"""
        pillars = bazi.get("pillars", {})
        day_master = bazi.get("day_master", "")
        day_wx = GAN_WX.get(day_master, "")
        
        # 四柱
        year_p = pillars.get("year", "")
        month_p = pillars.get("month", "")
        day_p = pillars.get("day", "")
        hour_p = pillars.get("hour", "")
        
        # 十神分析
        shishen_lines = []
        for item in bazi.get("shishen_analysis", []):
            god = item.get("god", "")
            info = get_shishen_translation(god)
            if info:
                shishen_lines.append(f"  {item.get('pillar', '')}柱 {item.get('gan', '')}：{god}")
                shishen_lines.append(f"      └─ 白話：{info.get('vernacular', '')}")
                shishen_lines.append(f"      └─ 場論：{info.get('field', '')}")
                shishen_lines.append(f"      └─ 現代：{info.get('modern', '')}")
        
        # 日主五行特性
        wx_info = WX_FIELD.get(day_wx, {})
        
        # v2.0: 進階分析（五行強弱 + 格局判斷）
        strength_section = ""
        geju_section = ""
        
        if ADVANCED_MODULES_LOADED:
            # 五行強弱分析
            strength_result = analyze_day_master_strength(pillars, day_master)
            strength_section = f"""
【身強身弱分析】
  判定：{strength_result['strength']}（能量比 {strength_result['strength_score']}:{100-strength_result['strength_score']}）
  說明：{strength_result['strength_desc']}
  月令：{strength_result['month_state']} — {strength_result['month_desc']}
  
  場論：{strength_result['field_analysis']}
"""
            # 格局判斷
            geju_result = determine_geju(pillars, day_master)
            geju_section = f"""
【八字格局】
  格局：{geju_result['geju']}
  白話：{geju_result['vernacular']}
  場論：{geju_result['field']}
  特質：{geju_result['trait']}
  
  適合職業：{geju_result['career']}
  優勢：{geju_result['strength']}
  風險：{geju_result['weakness']}
"""
        
        # 五行統計（視覺化）
        wx_count = bazi.get("wuxing_count", {"木": 0, "火": 0, "土": 0, "金": 0, "水": 0})
        wx_bar = ""
        for wx in ["木", "火", "土", "金", "水"]:
            count = wx_count.get(wx, 0)
            wx_bar += f"  {wx}：{'█' * count}{'░' * (5 - count)} ({count})\n"
        
        content = f"""
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃  🎯 八字命盤分析                                                  ┃
┣━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┫
┃                                                                  ┃
┃  【四柱八字】                                                     ┃
┃  ┌────────┬────────┬────────┬────────┐                          ┃
┃  │  年柱  │  月柱  │  日柱  │  時柱  │                          ┃
┃  ├────────┼────────┼────────┼────────┤                          ┃
┃  │  {year_p:^6}│  {month_p:^6}│  {day_p:^6}│  {hour_p:^6}│                          ┃
┃  └────────┴────────┴────────┴────────┘                          ┃
┃                                                                  ┃
┃  【日主分析】                                                     ┃
┃  日主：{day_master}（{day_wx}）                                         ┃
┃  場態：{wx_info.get('場態', '')}                                  ┃
┃  特徵：{wx_info.get('特徵', '')}                                  ┃
┃  現代：{wx_info.get('現代', '')}                                  ┃
┃                                                                  ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
{strength_section}
{geju_section}
【十神詳解】
{chr(10).join(shishen_lines)}

【五行分布】
{wx_bar}

【場論詮釋】
日主 {day_master} 屬 {day_wx}，代表你的核心能量是「{wx_info.get('場態', '')}」。

{day_wx}的特質是{wx_info.get('特徵', '')}，在現代語境中對應{wx_info.get('現代', '')}。

你的能量場需要：
• {WX_SHENG.get(day_wx, '')}（我生）— 輸出才華的方向
• 被{[k for k, v in WX_SHENG.items() if v == day_wx][0] if any(v == day_wx for v in WX_SHENG.values()) else ''}生 — 獲得支援的來源
• 注意{WX_KE.get(day_wx, '')}（我剋）— 消耗精力的地方
"""
        return content

    def generate_ziwei_section(self, ziwei: Dict, year_gan: str = "") -> str:
        """生成紫微斗數區塊（v2.0 整合四化+輔星）"""
        ming_stars = ziwei.get("ming_stars", [])
        shen_stars = ziwei.get("shen_stars", [])
        
        # 主星分析
        star_analysis_lines = []
        for star in ming_stars:
            info = get_ziwei_star_translation(star)
            if info:
                star_analysis_lines.append(f"""
  ★ {star}星
    ├─ 五行：{info.get('wuxing', '')}
    ├─ 古典：{info.get('classic', '')}
    ├─ 白話：{info.get('vernacular', '')}
    ├─ 場論：{info.get('field', '')}
    ├─ 現代：{info.get('modern', '')}
    ├─ 優勢：{info.get('strength', '')}
    ├─ 風險：{info.get('weakness', '')}
    └─ 適合職業：{info.get('career', '')}
""")
        
        # 十二宮簡表
        gongs = ziwei.get("gongs", {})
        gong_lines = []
        for gong_name, gong_data in list(gongs.items())[:6]:
            stars_str = "、".join(gong_data.get("main_stars", [])[:2]) or "無主星"
            gong_lines.append(f"  {gong_name}：{stars_str}")
        
        # v2.0: 四化分析
        sihua_section = ""
        if ADVANCED_MODULES_LOADED and year_gan:
            sihua_report = generate_sihua_report(year_gan, [])
            sihua_lines = []
            for item in sihua_report.get("sihua_details", []):
                sihua_info = get_sihua_info(item.get("sihua", ""))
                sihua_lines.append(f"  {item.get('star', '')} {item.get('sihua', '')}：{sihua_info.get('vernacular', '') if sihua_info else ''}")
                sihua_lines.append(f"      └─ 場論：{sihua_info.get('field', '') if sihua_info else ''}")
                sihua_lines.append(f"      └─ 建議：{sihua_info.get('advice', '') if sihua_info else ''}")
            
            sihua_section = f"""
【四化分析】（{year_gan}年生）
{chr(10).join(sihua_lines)}

  化祿：好事來了，把握機會
  化權：有話語權，善用影響力
  化科：有名聲，珍惜但要有實力
  化忌：這邊卡住了，是功課不是詛咒
"""
        
        # v2.0: 輔星分析（從宮位收集所有星）
        auxiliary_section = ""
        if ADVANCED_MODULES_LOADED:
            all_stars = []
            for gong_name, gong_data in gongs.items():
                all_stars.extend(gong_data.get("lucky_stars", []))
                all_stars.extend(gong_data.get("sha_stars", []))
            
            if all_stars:
                aux_analysis = analyze_auxiliary_stars(all_stars)
                combo_lines = []
                for combo in aux_analysis.get("special_combos", []):
                    combo_lines.append(f"  • {combo.get('name', '')}（{combo.get('type', '')}）：{combo.get('effect', '')}")
                
                auxiliary_section = f"""
【輔星組合分析】
  吉星數：{aux_analysis.get('ji_count', 0)} | 煞星數：{aux_analysis.get('sha_count', 0)}
  總評：{aux_analysis.get('summary', '')}

{'特殊組合：' + chr(10) + chr(10).join(combo_lines) if combo_lines else ''}
"""
        
        content = f"""
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃  ⭐ 紫微斗數分析                                                  ┃
┣━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┫
┃                                                                  ┃
┃  【基本資訊】                                                     ┃
┃  局數：{ziwei.get('ju_shu', '')}                                        ┃
┃  命宮：{ziwei.get('ming_gong', '')}                                     ┃
┃  身宮：{ziwei.get('shen_gong', '')}                                     ┃
┃                                                                  ┃
┃  【命宮主星】{', '.join(ming_stars) if ming_stars else '無主星'}           ┃
┃  【身宮主星】{', '.join(shen_stars) if shen_stars else '無主星'}           ┃
┃                                                                  ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

【命宮主星詳解】
{''.join(star_analysis_lines) if star_analysis_lines else '  （無主星或借星安命）'}
{sihua_section}
{auxiliary_section}
【十二宮速覽】
{chr(10).join(gong_lines)}

【場論詮釋】
紫微斗數是性格特質的分類系統，14主星代表14種人格原型。

你的命宮主星是「{ming_stars[0] if ming_stars else '無'}」，這代表：
{get_ziwei_star_translation(ming_stars[0]).get('vernacular', '') if ming_stars else '需要看借星情況'}

建議發展方向：
{get_ziwei_star_translation(ming_stars[0]).get('career', '') if ming_stars else '根據完整盤面判斷'}
"""
        return content

    def generate_name_section(self, name_data: Dict) -> str:
        """生成姓名學區塊"""
        wuge = name_data.get("wuge", {})
        wuge_analysis = name_data.get("wuge_analysis", {})
        sancai = name_data.get("sancai", "")
        strokes = name_data.get("strokes", {})
        
        # 五格詳解
        wuge_lines = []
        for ge_name, ge_key in [("天格", "tian"), ("人格", "ren"), ("地格", "di"), ("外格", "wai"), ("總格", "zong")]:
            ge_data = wuge_analysis.get(ge_key, {})
            shuli = ge_data.get("shuli", {})
            value = ge_data.get("value", wuge.get(ge_key, 0))
            wx = ge_data.get("wuxing", stroke_to_wuxing(value))
            
            type_mark = "✅" if shuli.get("type") == "大吉" else ("❌" if shuli.get("type") == "凶" else "⚪")
            
            wuge_lines.append(f"""
  {ge_name}：{value}（{wx}）{type_mark}
    ├─ 數理：{shuli.get('name', '')}
    ├─ 吉凶：{shuli.get('type', '')}
    └─ 含義：{shuli.get('meaning', '')}
""")
        
        # 三才分析
        sancai_wx = [stroke_to_wuxing(wuge.get(k, 1)) for k in ["tian", "ren", "di"]]
        
        content = f"""
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃  📛 姓名學分析                                                    ┃
┣━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┫
┃                                                                  ┃
┃  【姓名】{name_data.get('name', '')}                                      ┃
┃  【筆畫】{' + '.join([f"{c}({s})" for c, s in strokes.items()])} = {sum(strokes.values())}畫  ┃
┃  【三才】{sancai} → {sancai_wx[0]}→{sancai_wx[1]}→{sancai_wx[2]}                     ┃
┃                                                                  ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

【五格詳解】
{''.join(wuge_lines)}

【三才配置分析】
三才 {sancai_wx[0]}→{sancai_wx[1]}→{sancai_wx[2]} 代表：

• 天格（{sancai_wx[0]}）：先天運，來自家族的能量場
• 人格（{sancai_wx[1]}）：主運，你的核心能量（最重要）
• 地格（{sancai_wx[2]}）：前運，早年和基礎運勢

天人關係（{sancai_wx[0]}→{sancai_wx[1]}）：
{_analyze_sancai_relation(sancai_wx[0], sancai_wx[1])}

人地關係（{sancai_wx[1]}→{sancai_wx[2]}）：
{_analyze_sancai_relation(sancai_wx[1], sancai_wx[2])}

【場論詮釋】
姓名學的本質是「符號場」—— 名字是一個被反覆呼喚的咒語，
形成固定的能量振動模式，影響自我認同和他人期待。

人格{wuge.get('ren', 0)}是你的核心場，數理「{wuge_analysis.get('ren', {}).get('shuli', {}).get('name', '')}」
意味著：{wuge_analysis.get('ren', {}).get('shuli', {}).get('meaning', '')}
"""
        return content

    def generate_meihua_section(self, meihua: Dict) -> str:
        """生成梅花易數區塊"""
        upper = meihua.get("upper_gua", "")
        lower = meihua.get("lower_gua", "")
        dong_yao = meihua.get("dong_yao", 1)
        
        upper_info = get_bagua_translation(upper)
        lower_info = get_bagua_translation(lower)
        
        content = f"""
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃  🌸 梅花易數分析                                                  ┃
┣━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┫
┃                                                                  ┃
┃  【本卦】{upper}{lower}卦（上{upper}下{lower}）                              ┃
┃  【動爻】第{dong_yao}爻                                               ┃
┃                                                                  ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

【上卦分析】{upper}卦 {upper_info.get('symbol', '')}
  ├─ 古典：{upper_info.get('classic', '')}
  ├─ 白話：{upper_info.get('vernacular', '')}
  ├─ 場論：{upper_info.get('field', '')}
  ├─ 現代：{upper_info.get('modern', '')}
  ├─ 優勢：{upper_info.get('strength', '')}
  ├─ 風險：{upper_info.get('weakness', '')}
  └─ 適用：{upper_info.get('scenario', '')}

【下卦分析】{lower}卦 {lower_info.get('symbol', '')}
  ├─ 古典：{lower_info.get('classic', '')}
  ├─ 白話：{lower_info.get('vernacular', '')}
  ├─ 場論：{lower_info.get('field', '')}
  ├─ 現代：{lower_info.get('modern', '')}
  ├─ 優勢：{lower_info.get('strength', '')}
  ├─ 風險：{lower_info.get('weakness', '')}
  └─ 適用：{lower_info.get('scenario', '')}

【綜合判斷】
上卦{upper}（{upper_info.get('vernacular', '')}）+ 下卦{lower}（{lower_info.get('vernacular', '')}）

這個卦象組合表示：
• 外在環境/結果：{upper_info.get('field', '')}
• 內在動力/基礎：{lower_info.get('field', '')}

【場論詮釋】
梅花易數的本質是「決策場快照」—— 
在特定時刻捕捉宇宙能量狀態，映射到你的問題上。

八卦是八種基本能量狀態，三爻結構代表場的三層特徵（天人地）。
"""
        return content

    def generate_summary(self, bazi: Dict, ziwei: Dict, name_data: Optional[Dict]) -> str:
        """生成綜合建議"""
        day_master = bazi.get("day_master", "")
        day_wx = GAN_WX.get(day_master, "")
        ming_stars = ziwei.get("ming_stars", [])
        main_star = ming_stars[0] if ming_stars else ""
        star_info = get_ziwei_star_translation(main_star) if main_star else {}
        
        content = f"""
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃  💡 綜合分析與建議                                                ┃
┣━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┫
┃                                                                  ┃
┃  【核心特質】                                                     ┃
┃  八字日主：{day_master}（{day_wx}）— {WX_FIELD.get(day_wx, {}).get('場態', '')}     ┃
┃  紫微命星：{main_star or '無'}（{star_info.get('field', '') or '—'}）         ┃
┃                                                                  ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

【四術交叉驗證】

1. 八字看「先天能量結構」
   → 你的核心是{day_wx}，特質是{WX_FIELD.get(day_wx, {}).get('特徵', '')}
   
2. 紫微看「性格特質原型」
   → 命宮{main_star or '借星'}，{star_info.get('vernacular', '需看借星') if star_info else '根據完整盤面判斷'}
   
3. 姓名看「社會能量場」
   → 名字形成的振動模式影響自我認同

4. 梅花看「當下能量快照」
   → 特定問題的即時決策參考

【綜合建議】

✅ 發揮優勢：
• {day_wx}的特長：{WX_FIELD.get(day_wx, {}).get('現代', '')}
• {main_star}的優勢：{star_info.get('strength', '') if star_info else '根據完整盤面判斷'}

⚠️ 注意風險：
• {day_wx}的弱點：容易{WX_KE.get(day_wx, '')}消耗
• {main_star}的風險：{star_info.get('weakness', '') if star_info else '根據完整盤面判斷'}

💼 適合方向：
• {star_info.get('career', '') if star_info else '需要完整分析'}

【重要提醒】
命理分析是「決策輔助工具」，不是「命運判決書」。
所有分析都是機率性參考，最終決策權在你手上。

記住：趨吉避凶——趨和避都是動詞，主語是人。
"""
        return content

    def generate_full_report(self, birth: BirthData, lunar_info: Dict, 
                            bazi: Dict, ziwei: Dict, 
                            name_data: Optional[Dict] = None,
                            meihua: Optional[Dict] = None,
                            year_gan: str = "") -> str:
        """生成完整報告 v2.0"""
        report_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        report = REPORT_SECTIONS["header"]
        report += f"\n生成時間：{report_time}\n"
        report += REPORT_SECTIONS["disclaimer"]
        
        # 基本資料
        report += self.generate_basic_info(birth, lunar_info)
        
        # 八字分析（v2.0 含五行強弱+格局）
        report += self.generate_bazi_section(bazi, lunar_info)
        
        # 紫微分析（v2.0 含四化+輔星）
        report += self.generate_ziwei_section(ziwei, year_gan)
        
        # 姓名分析（如果有）
        if name_data:
            report += self.generate_name_section(name_data)
        
        # 梅花分析（如果有）
        if meihua:
            report += self.generate_meihua_section(meihua)
        
        # 綜合建議
        report += self.generate_summary(bazi, ziwei, name_data)
        
        # 頁尾
        report += """
╔══════════════════════════════════════════════════════════════════╗
║                                                                  ║
║  北斗命數分析報告 v2.1 | 進階場論版                                ║
║  建立者：北斗 × 織明 | 框架版本 1.9                                ║
║  v2.1 新增：五行強弱、格局判斷、四化詳解、輔星分析                  ║
║                                                                  ║
║  古法是根，場論是枝，用戶是花                                      ║
║                                                                  ║
╚══════════════════════════════════════════════════════════════════╝
"""
        return report


# =============================================================================
# 輔助函數
# =============================================================================

def _analyze_sancai_relation(wx1: str, wx2: str) -> str:
    """分析三才關係"""
    if wx1 == wx2:
        return f"  {wx1}與{wx2}比和 — 同頻能量，穩定但缺乏變化"
    elif WX_SHENG.get(wx1) == wx2:
        return f"  {wx1}生{wx2} — 順生關係，上對下支援，關係和諧"
    elif WX_KE.get(wx1) == wx2:
        return f"  {wx1}剋{wx2} — 相剋關係，可能有壓力或阻礙"
    elif WX_SHENG.get(wx2) == wx1:
        return f"  {wx2}生{wx1} — 被生關係，下對上支援，基礎穩固"
    elif WX_KE.get(wx2) == wx1:
        return f"  {wx2}剋{wx1} — 被剋關係，可能受到限制"
    return "  關係需進一步分析"


if __name__ == "__main__":
    # 測試
    gen = FullReportGenerator()
    print("報告生成器載入成功")
