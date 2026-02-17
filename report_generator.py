"""
完整命理報告生成器 report_generator.py v2.3
==========================================
整合四術分析，生成專業級完整命理報告
v2.0 新增：五行強弱、格局判斷、神煞分析、四化詳解、輔星分析
v2.3 新增：八字大運、流年分析、紫微大限

建立者：北斗 × 織明
日期：2026-02-07
XTF任務：E+B+D 融合
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
    from wuxing_analyzer import analyze_wuxing_strength, WuxingAnalyzer
    WUXING_ANALYZER_LOADED = True
except ImportError:
    WUXING_ANALYZER_LOADED = False

try:
    from geju_analyzer import analyze_geju, GejuAnalyzer
    GEJU_ANALYZER_LOADED = True
except ImportError:
    GEJU_ANALYZER_LOADED = False

try:
    from sihua_translation import translate_sihua, generate_sihua_report, get_sihua_detail
    SIHUA_LOADED = True
except ImportError:
    SIHUA_LOADED = False

try:
    from shensha_translation import find_shensha, generate_shensha_report
    SHENSHA_LOADED = True
except ImportError:
    SHENSHA_LOADED = False

try:
    from fuzhu_star_translation import translate_fuzhu_stars, generate_fuzhu_report, analyze_fuzhu_balance
    FUZHU_LOADED = True
except ImportError:
    FUZHU_LOADED = False

# v2.3 新增：大運流年模組
try:
    from dayun_calculator import calculate_dayun, get_current_dayun
    from liunian_analyzer import analyze_liunian, analyze_liunian_range
    from daxian_calculator import calculate_daxian, get_current_daxian, get_daxian_meaning
    from fortune_timeline import build_fortune_timeline, generate_fortune_report
    FORTUNE_LOADED = True
except ImportError:
    FORTUNE_LOADED = False

ADVANCED_MODULES_LOADED = all([
    WUXING_ANALYZER_LOADED, GEJU_ANALYZER_LOADED, 
    SIHUA_LOADED, SHENSHA_LOADED, FUZHU_LOADED
])

FORTUNE_MODULES_LOADED = FORTUNE_LOADED


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
        
        # v2.0: 進階分析（五行強弱 + 格局判斷 + 神煞）
        strength_section = ""
        geju_section = ""
        shensha_section = ""
        
        if WUXING_ANALYZER_LOADED and GEJU_ANALYZER_LOADED:
            # 五行強弱分析
            strength_result = analyze_wuxing_strength(day_master, pillars)
            strength_section = f"""
【身強身弱分析】
  判定：{strength_result['strength_level']}（總分 {strength_result['score']['total']}）
  • 月令：{strength_result['score']['month']}分
  • 通根：{strength_result['score']['root']}分
  • 印星：{strength_result['score']['sheng']}分
  • 比劫：{strength_result['score']['help']}分
  • 洩耗：-{strength_result['score']['drain']}分
  
  用神：{strength_result['yongshen']['用神']}
  喜神：{strength_result['yongshen']['喜神']}
  忌神：{strength_result['yongshen']['忌神']}
  建議：{strength_result['yongshen']['建議']}
"""
            # 格局判斷
            geju_result = analyze_geju(day_master, pillars)
            geju_info = geju_result['geju_info']
            geju_section = f"""
【八字格局】
  格局：{geju_result['geju_name']}
  白話：{geju_info.get('vernacular', '')}
  場論：{geju_info.get('field', '')}
  
  適合職業：{geju_info.get('modern', '')}
  建議：{geju_result['advice']}
"""
        
        if SHENSHA_LOADED:
            # 神煞分析
            shensha_list = find_shensha(day_master, pillars)
            if shensha_list:
                ji = [s for s in shensha_list if s["category"] == "吉神"]
                sha = [s for s in shensha_list if s["category"] in ["凶煞", "中性"]]
                shensha_section = """
【神煞分析】
"""
                if ji:
                    shensha_section += "  吉神：\n"
                    for s in ji[:3]:
                        shensha_section += f"    ★ {s['name']}：{s['vernacular']}\n"
                if sha:
                    shensha_section += "  凶煞/中性：\n"
                    for s in sha[:3]:
                        shensha_section += f"    ⚠ {s['name']}：{s['vernacular']}\n"
        
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
{shensha_section}
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
        if SIHUA_LOADED and year_gan:
            sihua_list = translate_sihua(year_gan)
            sihua_lines = []
            for item in sihua_list:
                sihua_lines.append(f"  ★ {item.get('star', '')}{item.get('hua', '')}")
                sihua_lines.append(f"      └─ 白話：{item.get('vernacular', '')}")
                sihua_lines.append(f"      └─ 場論：{item.get('field', '')}")
                sihua_lines.append(f"      └─ 建議：{item.get('advice', '')}")
            
            sihua_section = f"""
【四化分析】（{year_gan}年生）
{chr(10).join(sihua_lines)}

  提示：
  • 化祿：好事來了，把握機會
  • 化權：有話語權，善用影響力
  • 化科：有名聲，珍惜但要有實力
  • 化忌：這邊卡住了，是功課不是詛咒
"""
        
        # v2.0: 輔星分析（從宮位收集所有星）
        auxiliary_section = ""
        if FUZHU_LOADED:
            all_stars = []
            for gong_name, gong_data in gongs.items():
                all_stars.extend(gong_data.get("lucky_stars", []))
            
            if all_stars:
                aux_result = translate_fuzhu_stars(all_stars[:6])
                balance = analyze_fuzhu_balance(all_stars)
                
                aux_lines = []
                for item in aux_result:
                    aux_lines.append(f"  • {item.get('star', '')}：{item.get('vernacular', '')}")
                
                auxiliary_section = f"""
【輔星分析】
  吉星數：{balance.get('ji_count', 0)} | 煞星數：{balance.get('sha_count', 0)}
  總評：{balance.get('balance', '')}

{chr(10).join(aux_lines) if aux_lines else '  （無特別輔星）'}
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

    def generate_fortune_section(self, birth: 'BirthData', bazi: Dict, ziwei: Dict) -> str:
        """生成大運流年分析區塊 v3.0.4 修正"""
        if not FORTUNE_LOADED:
            return "\n【大運流年分析】\n（大運流年模組未載入）\n"
        
        # v3.0.4: 空值防護
        if not bazi:
            return "\n【大運流年分析】\n（八字資料缺失，無法分析）\n"
        
        content = """
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃  📅 大運流年分析                                                  ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
"""
        
        # v3.0.4: 安全取值函數
        def safe_get_char(val, idx, default=""):
            """安全取得字串或列表中的字元"""
            if not val:
                return default
            if isinstance(val, list):
                return val[idx] if len(val) > idx else default
            if isinstance(val, str):
                return val[idx] if len(val) > idx else default
            return default
        
        try:
            # v3.0.4: 安全取得必要資料
            year_val = bazi.get("year", "") or bazi.get("pillars", {}).get("year", "")
            year_gan = safe_get_char(year_val, 0, "")
            
            month_val = bazi.get("month", "") or bazi.get("pillars", {}).get("month", "")
            if isinstance(month_val, list):
                month_ganzhi = "".join(month_val) if month_val else ""
            else:
                month_ganzhi = month_val or ""
            
            day_master = bazi.get("day_master", "")
            
            # v3.0.4: 優先使用 bazi["pillars"]，其次拼湊
            if bazi.get("pillars"):
                pillars = bazi["pillars"]
            else:
                pillars = {}
                for p in ["year", "month", "day", "hour"]:
                    val = bazi.get(p, "")
                    if isinstance(val, list):
                        pillars[p] = "".join(val) if val else ""
                    else:
                        pillars[p] = val or ""
            
            # v3.0.4: 檢查必要資料是否存在
            if not day_master:
                return content + "\n（日主資料缺失，無法分析流年）\n"
            
            if not year_gan:
                return content + "\n（年柱資料缺失，無法分析大運）\n"
            
            # 紫微資料
            ju_shu = ziwei.get("ju_shu", "") if ziwei else ""
            ming_gong_idx = ziwei.get("ming_gong_idx", 0) if ziwei else 0
            
            # 判斷身強身弱
            strength_level = bazi.get("strength_level", "")
            if not strength_level and bazi.get("strength"):
                strength_level = bazi.get("strength", {}).get("strength_level", "")
            is_strong = strength_level in ["極強", "偏強", "中和偏強"]
            
            current_year = datetime.now().year
            
            # 八字大運
            if year_gan and month_ganzhi:
                dayun_result = calculate_dayun(
                    year_gan, month_ganzhi, birth.gender,
                    birth.year, birth.month, birth.day, 8
                )
                current_dayun = get_current_dayun(dayun_result, current_year)
                
                content += f"""
【八字大運】
方向：{dayun_result['direction']}
起運：{dayun_result['qiyun_age']}歲（{dayun_result['qiyun_year']}年）

當前大運：{current_dayun['ganzhi'] if current_dayun else '待定'}
期間：{current_dayun['start_age']}～{current_dayun['end_age']}歲（{current_dayun['start_year']}～{current_dayun['end_year']}年）

【大運列表】
"""
                for d in dayun_result['dayun_list'][:6]:
                    marker = "→" if current_dayun and d['ganzhi'] == current_dayun['ganzhi'] else "  "
                    content += f"{marker} 第{d['order']}運：{d['ganzhi']}（{d['wx']}）{d['start_age']}～{d['end_age']}歲\n"
            
            # 八字流年
            if day_master and pillars:
                content += f"""
【{current_year}年流年分析】
"""
                liunian = analyze_liunian(day_master, pillars, current_year, is_strong)
                tendency_emoji = {"吉": "🟢", "平": "🟡", "凶": "🔴"}.get(liunian.get('tendency', ''), "⚪")
                
                content += f"""流年干支：{liunian['ganzhi']}
流年十神：{liunian['gan_shishen']}
整體傾向：{tendency_emoji} {liunian['tendency']}
建議：{liunian['advice']}
"""
                
                if liunian.get('interactions'):
                    content += f"與命局互動：{'、'.join(liunian['interactions'])}\n"
                
                # 未來5年速覽
                content += "\n【未來5年流年速覽】\n"
                future_years = analyze_liunian_range(day_master, pillars, current_year, 5, is_strong)
                for ly in future_years:
                    emoji = {"吉": "🟢", "平": "🟡", "凶": "🔴"}.get(ly.get('tendency', ''), "⚪")
                    content += f"  {ly['year']}年 {ly['ganzhi']}：{ly['gan_shishen']} {emoji}\n"
            
            # 紫微大限
            if ju_shu:
                content += "\n【紫微大限】\n"
                daxian_result = calculate_daxian(
                    year_gan, birth.gender, ju_shu, ming_gong_idx, birth.year
                )
                current_daxian = get_current_daxian(daxian_result, current_year)
                
                content += f"""方向：{daxian_result['direction']}
起限：{daxian_result['start_age']}歲

當前大限：{current_daxian['gong_name'] if current_daxian else '待定'}宮
期間：{current_daxian['start_age']}～{current_daxian['end_age']}歲（{current_daxian['start_year']}～{current_daxian['end_year']}年）
"""
                
                if current_daxian:
                    meaning = get_daxian_meaning(current_daxian['gong_name'])
                    content += f"""
主題：{meaning.get('vernacular', '')}
建議：{meaning.get('advice', '')}
"""
            
            # XTF8 確定度標註
            content += """
【XTF8 確定度標註】
★★★★★ 大運/大限計算（可驗證公式）
★★★☆☆ 吉凶傾向（經驗統計參考）
★★☆☆☆ 具體事件（高度不確定）

提醒：大運流年是「能量傾向參考」，不是「命運劇本」。
"""
        except Exception as e:
            content += f"\n（分析過程發生錯誤：{str(e)}）\n"
        
        return content

    def generate_full_report(self, birth: BirthData, lunar_info: Dict, 
                            bazi: Dict, ziwei: Dict, 
                            name_data: Optional[Dict] = None,
                            meihua: Optional[Dict] = None,
                            year_gan: str = "") -> str:
        """生成完整報告 v2.3"""
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
        
        # v2.3 新增：大運流年分析
        report += self.generate_fortune_section(birth, bazi, ziwei)
        
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
║  北斗命數分析報告 v2.3 | 大運流年版                                ║
║  建立者：北斗 × 織明 | 框架版本 2.0                                ║
║  v2.3 新增：八字大運、流年分析、紫微大限                           ║
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
