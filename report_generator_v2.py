"""
完整命理報告生成器 report_generator_v2.py v2.0
=============================================
XTF任務：融-F1 | 執行星：織明（全局）+ 星殼（架構）

整合：
- 五行強弱分析
- 格局智能判斷
- 四化詳解
- 神煞白話
- 輔星白話
- PDF 輸出支援

建立者：北斗 × 織明
日期：2026-02-07
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime
import os

# 導入整合翻譯模組
from field_translation_v2 import (
    FieldTranslator, full_bazi_analysis, full_ziwei_analysis,
    generate_full_field_report, translate_sihua, generate_sihua_report,
    find_shensha, translate_fuzhu_stars, analyze_fuzhu_balance,
    get_shishen_translation, get_ziwei_star_translation, get_shuli_translation,
    stroke_to_wuxing, FRAMEWORK_INFO_V2
)
from wuxing_analyzer import analyze_wuxing_strength, GAN_WX, ZHI_WX
from geju_analyzer import analyze_geju, calc_shishen
from wuxing_core import WX_FIELD, WX_SHENG, WX_KE


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
    is_lunar: bool = False


# =============================================================================
# 報告模板
# =============================================================================

REPORT_HEADER = """
╔══════════════════════════════════════════════════════════════════╗
║                                                                  ║
║                    🌟 北 斗 命 數 分 析 報 告 🌟                   ║
║                                                                  ║
║                      場論詮釋版 v2.0                              ║
║                                                                  ║
╚══════════════════════════════════════════════════════════════════╝
"""

DISCLAIMER = """
┌──────────────────────────────────────────────────────────────────┐
│  📐 認識論聲明                                                    │
│                                                                  │
│  術數是個人化決策框架生成器，與天氣預報同構                         │
│  ─ 提供機率性參考，不做命定式裁決                                  │
│  ─ 趨吉避凶：趨和避都是動詞，主語是人                              │
│  ─ 古法是根，場論是枝，用戶是花                                    │
└──────────────────────────────────────────────────────────────────┘
"""


# =============================================================================
# 完整報告生成器 v2.0
# =============================================================================

class FullReportGeneratorV2:
    """完整命理報告生成器 v2.0"""
    
    def __init__(self):
        self.sections = []
        self.version = "2.0"
    
    def generate_basic_info(self, birth: BirthData, lunar_info: Dict) -> str:
        """生成基本資料區塊"""
        calendar_type = "農曆" if birth.is_lunar else "西曆"
        
        return f"""
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃  📋 基本資料                                                      ┃
┣━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┫
┃                                                                  ┃
┃  姓名：{birth.name or '未提供':<20}  性別：{birth.gender}           ┃
┃                                                                  ┃
┃  【輸入曆法】{calendar_type}                                      ┃
┃  {calendar_type}生日：{birth.year}年{birth.month}月{birth.day}日 {birth.hour}時  ┃
┃                                                                  ┃
┃  【轉換結果】                                                     ┃
┃  西曆：{lunar_info.get('solar', '')}                              ┃
┃  農曆：{lunar_info.get('lunar_str', '')}                          ┃
┃  生肖：{lunar_info.get('shengxiao', '')}                          ┃
┃                                                                  ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
"""

    def generate_bazi_section(self, bazi_analysis: Dict, pillars: Dict) -> str:
        """生成八字分析區塊（v2.0 增強版）"""
        
        # 基本資訊
        wuxing = bazi_analysis.get("wuxing", {})
        geju = bazi_analysis.get("geju", {})
        day_master = wuxing.get("day_master", "")
        day_wx = wuxing.get("day_wx", "")
        
        # 四柱
        year_p = pillars.get("year", "")
        month_p = pillars.get("month", "")
        day_p = pillars.get("day", "")
        hour_p = pillars.get("hour", "")
        
        # 五行統計
        score = wuxing.get("score", {})
        strength_level = wuxing.get("strength_level", "")
        is_strong = wuxing.get("is_strong", False)
        
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
┃  日主：{day_master}（{day_wx}）| 身強弱：{strength_level}                 ┃
┃  格局：{geju.get('geju_name', '')}                                       ┃
┃                                                                  ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

{wuxing.get('analysis', '')}

{geju.get('detailed_analysis', '')}
"""
        
        # 十神分析
        shishen_list = bazi_analysis.get("shishen", [])
        if shishen_list:
            content += "\n【十神詳解】\n"
            for item in shishen_list:
                info = item.get("info", {})
                if info:
                    content += f"""
  {item.get('pillar', '')}柱 {item.get('gan', '')}：{item.get('shishen', '')}
    ├─ 白話：{info.get('vernacular', '')}
    ├─ 場論：{info.get('field', '')}
    └─ 現代：{info.get('modern', '')}
"""
        
        # 神煞分析
        shensha_list = bazi_analysis.get("shensha", [])
        if shensha_list:
            content += "\n【神煞分析】\n"
            jishen = [s for s in shensha_list if s.get("category") == "吉神"]
            xiongsha = [s for s in shensha_list if s.get("category") != "吉神"]
            
            if jishen:
                content += "\n★ 吉神：\n"
                for s in jishen:
                    content += f"  ✅ {s['name']}（{s.get('found_in', '')}）：{s['vernacular']}\n"
                    content += f"     場論：{s['field']} | 建議：{s['advice']}\n"
            
            if xiongsha:
                content += "\n★ 凶煞/中性：\n"
                for s in xiongsha:
                    mark = "⚠️" if s.get("category") == "凶煞" else "⚪"
                    content += f"  {mark} {s['name']}（{s.get('found_in', '')}）：{s['vernacular']}\n"
                    content += f"     場論：{s['field']} | 建議：{s['advice']}\n"
        
        # 用神建議
        yongshen = wuxing.get("yongshen", {})
        if yongshen:
            content += f"""
【用神分析】
  用神：{yongshen.get('用神', '')}
  喜神：{yongshen.get('喜神', '')}
  忌神：{yongshen.get('忌神', '')}
  建議：{yongshen.get('建議', '')}
"""
        
        return content

    def generate_ziwei_section(self, ziwei_analysis: Dict, chart_data: Dict) -> str:
        """生成紫微斗數區塊（v2.0 增強版）"""
        
        ming_stars = ziwei_analysis.get("ming_stars", [])
        ming_fuzhu = ziwei_analysis.get("ming_fuzhu", [])
        balance = ziwei_analysis.get("balance", {})
        
        content = f"""
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃  ⭐ 紫微斗數分析                                                  ┃
┣━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┫
┃                                                                  ┃
┃  【基本資訊】                                                     ┃
┃  局數：{chart_data.get('ju_shu', '')}                                   ┃
┃  命宮：{chart_data.get('ming_gong', '')}                                ┃
┃  身宮：{chart_data.get('shen_gong', '')}                                ┃
┃                                                                  ┃
┃  【命宮主星】{', '.join([s.get('star', '') for s in ming_stars]) if ming_stars else '無主星'}  ┃
┃  【吉凶平衡】吉星{balance.get('ji_count', 0)}個，煞星{balance.get('sha_count', 0)}個 — {balance.get('balance', '')}  ┃
┃                                                                  ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
"""
        
        # 主星詳解
        if ming_stars:
            content += "\n【命宮主星詳解】\n"
            for star in ming_stars:
                content += f"""
  ★ {star.get('star', '')}星
    ├─ 五行：{star.get('wuxing', '')}
    ├─ 白話：{star.get('vernacular', '')}
    ├─ 場論：{star.get('field', '')}
    ├─ 優勢：{star.get('strength', '')}
    ├─ 風險：{star.get('weakness', '')}
    └─ 適合：{star.get('career', '')}
"""
        
        # 輔星詳解
        if ming_fuzhu:
            content += "\n【命宮輔星詳解】\n"
            for star in ming_fuzhu:
                cat = star.get('category', '')
                mark = "✅" if cat == "吉星" else ("⚠️" if cat == "煞星" else "⚪")
                content += f"""
  {mark} {star.get('star', '')}（{cat}）
    ├─ 白話：{star.get('vernacular', '')}
    ├─ 場論：{star.get('field', '')}
    ├─ 優勢：{star.get('strength', '')}
    └─ 注意：{star.get('weakness', '')}
"""
        
        # 四化分析
        sihua = chart_data.get("sihua", {})
        if sihua:
            content += "\n【四化分析】\n"
            for hua_type, star in sihua.items():
                content += f"  {star}{hua_type}\n"
        
        return content

    def generate_name_section(self, name_data: Dict) -> str:
        """生成姓名學區塊"""
        if not name_data:
            return ""
        
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
            
            type_mark = "✅" if shuli.get("type") == "大吉" else ("⚠️" if shuli.get("type") == "凶" else "⚪")
            
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
┃  【三才】{sancai} → {sancai_wx[0]}→{sancai_wx[1]}→{sancai_wx[2]}          ┃
┃                                                                  ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

【五格詳解】
{''.join(wuge_lines)}

【三才配置分析】
三才 {sancai_wx[0]}→{sancai_wx[1]}→{sancai_wx[2]} 代表：
• 天格（{sancai_wx[0]}）：先天運，來自家族的能量場
• 人格（{sancai_wx[1]}）：主運，你的核心能量（最重要）
• 地格（{sancai_wx[2]}）：前運，早年和基礎運勢
"""
        
        return content

    def generate_summary(self, bazi_analysis: Dict, ziwei_analysis: Dict) -> str:
        """生成綜合建議（v2.0 增強版）"""
        
        wuxing = bazi_analysis.get("wuxing", {})
        geju = bazi_analysis.get("geju", {})
        ming_stars = ziwei_analysis.get("ming_stars", [])
        
        day_master = wuxing.get("day_master", "")
        day_wx = wuxing.get("day_wx", "")
        strength_level = wuxing.get("strength_level", "")
        geju_name = geju.get("geju_name", "")
        main_star = ming_stars[0] if ming_stars else {}
        
        content = f"""
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃  💡 綜合分析與建議                                                ┃
┣━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┫
┃                                                                  ┃
┃  【核心特質】                                                     ┃
┃  八字日主：{day_master}（{day_wx}）— {strength_level}                    ┃
┃  八字格局：{geju_name}                                              ┃
┃  紫微命星：{main_star.get('star', '無') if main_star else '無'}      ┃
┃                                                                  ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

【四術交叉驗證】

1️⃣ 八字看「先天能量結構」
   日主{day_master}（{day_wx}），{strength_level}
   格局{geju_name}：{geju.get('geju_info', {}).get('vernacular', '')}
   
2️⃣ 紫微看「性格特質原型」
   命宮{main_star.get('star', '無')}星：{main_star.get('vernacular', '根據完整盤面判斷')}
   
3️⃣ 神煞看「特殊能量印記」
   吉神代表有利場，凶煞提醒風險點

4️⃣ 輔星看「輔助能量配置」
   吉凶平衡影響整體運勢走向

【綜合建議】

✅ 發揮優勢：
• {day_wx}日主的長處：{WX_FIELD.get(day_wx, {}).get('現代', '')}
• {main_star.get('star', '')}星的優勢：{main_star.get('strength', '') if main_star else '根據完整盤面判斷'}
• {geju_name}的適合方向：{geju.get('geju_info', {}).get('suitable', '')}

⚠️ 注意風險：
• {strength_level}需要注意：{'避免過度消耗' if wuxing.get('is_strong') else '需要更多支援'}
• {main_star.get('star', '')}的風險：{main_star.get('weakness', '') if main_star else '根據完整盤面判斷'}

💼 適合方向：
• {geju.get('geju_info', {}).get('modern', '')}
• {main_star.get('career', '') if main_star else '需要完整分析'}

【重要提醒】
命理分析是「決策輔助工具」，不是「命運判決書」。
所有分析都是機率性參考，最終決策權在你手上。

記住：趨吉避凶——趨和避都是動詞，主語是人。
"""
        return content

    def generate_full_report(self, birth: BirthData, lunar_info: Dict,
                            bazi_analysis: Dict, ziwei_analysis: Dict,
                            chart_data: Dict, pillars: Dict,
                            name_data: Optional[Dict] = None) -> str:
        """生成完整報告 v2.0"""
        
        report_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        report = REPORT_HEADER
        report += f"\n生成時間：{report_time}\n"
        report += f"版本：v{self.version} | 框架：{FRAMEWORK_INFO_V2['version']}\n"
        report += DISCLAIMER
        
        # 基本資料
        report += self.generate_basic_info(birth, lunar_info)
        
        # 八字分析（v2.0 增強）
        report += self.generate_bazi_section(bazi_analysis, pillars)
        
        # 紫微分析（v2.0 增強）
        report += self.generate_ziwei_section(ziwei_analysis, chart_data)
        
        # 姓名分析（如果有）
        if name_data:
            report += self.generate_name_section(name_data)
        
        # 綜合建議（v2.0 增強）
        report += self.generate_summary(bazi_analysis, ziwei_analysis)
        
        # 頁尾
        report += """
╔══════════════════════════════════════════════════════════════════╗
║                                                                  ║
║  北斗命數分析報告 v2.0 | 場論詮釋版                                ║
║  建立者：北斗 × 織明 | 框架版本 2.0                                ║
║                                                                  ║
║  新增：五行強弱 + 格局判斷 + 四化詳解 + 神煞 + 輔星               ║
║  古法是根，場論是枝，用戶是花                                      ║
║                                                                  ║
╚══════════════════════════════════════════════════════════════════╝
"""
        return report


# =============================================================================
# PDF 生成器（使用 reportlab）
# =============================================================================

def generate_pdf_report(report_text: str, output_path: str, name: str = "命理") -> bool:
    """
    生成 PDF 報告
    
    需要安裝：pip install reportlab
    """
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.pdfgen import canvas
        from reportlab.pdfbase import pdfmetrics
        from reportlab.pdfbase.ttfonts import TTFont
        from reportlab.lib.units import cm
        
        # 嘗試註冊中文字體
        font_paths = [
            "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc",
            "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
            "/System/Library/Fonts/PingFang.ttc",
            "C:\\Windows\\Fonts\\msyh.ttc",
        ]
        
        font_registered = False
        for font_path in font_paths:
            if os.path.exists(font_path):
                try:
                    pdfmetrics.registerFont(TTFont('Chinese', font_path))
                    font_registered = True
                    break
                except:
                    continue
        
        # 建立 PDF
        c = canvas.Canvas(output_path, pagesize=A4)
        width, height = A4
        
        # 設定字體
        font_name = 'Chinese' if font_registered else 'Helvetica'
        
        # 寫入內容
        y = height - 2 * cm
        lines = report_text.split('\n')
        
        for line in lines:
            if y < 2 * cm:
                c.showPage()
                y = height - 2 * cm
            
            # 處理特殊字符
            line = line.replace('━', '-').replace('┃', '|')
            line = line.replace('┏', '+').replace('┓', '+')
            line = line.replace('┗', '+').replace('┛', '+')
            line = line.replace('┣', '+').replace('┫', '+')
            line = line.replace('╔', '+').replace('╗', '+')
            line = line.replace('╚', '+').replace('╝', '+')
            line = line.replace('╠', '+').replace('╣', '+')
            
            c.setFont(font_name, 10)
            c.drawString(2 * cm, y, line[:80])  # 限制每行長度
            y -= 0.5 * cm
        
        c.save()
        return True
        
    except ImportError:
        print("需要安裝 reportlab：pip install reportlab")
        return False
    except Exception as e:
        print(f"PDF 生成失敗：{e}")
        return False


# =============================================================================
# 便捷函數
# =============================================================================

def create_full_report(birth: BirthData, lunar_info: Dict,
                      pillars: Dict, chart_data: Dict,
                      name_data: Optional[Dict] = None) -> str:
    """
    便捷函數：建立完整報告
    
    Args:
        birth: 出生資料
        lunar_info: 農曆資訊
        pillars: 四柱 {"year": "甲子", "month": "丙寅", ...}
        chart_data: 紫微盤資料
        name_data: 姓名分析資料（可選）
    """
    day_master = pillars["day"][0]
    year_gan = pillars["year"][0]
    
    # 八字完整分析
    bazi_analysis = full_bazi_analysis(day_master, pillars, year_gan)
    
    # 紫微完整分析
    ziwei_analysis = full_ziwei_analysis(chart_data)
    
    # 生成報告
    generator = FullReportGeneratorV2()
    return generator.generate_full_report(
        birth=birth,
        lunar_info=lunar_info,
        bazi_analysis=bazi_analysis,
        ziwei_analysis=ziwei_analysis,
        chart_data=chart_data,
        pillars=pillars,
        name_data=name_data,
    )


if __name__ == "__main__":
    print("報告生成器 v2.0 載入成功")
    print(f"支援模組：{len(FRAMEWORK_INFO_V2['completed_modules'])}個")
