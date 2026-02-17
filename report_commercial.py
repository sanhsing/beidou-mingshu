#!/usr/bin/env python3
"""
report_commercial.py - 北斗命數商業版報告生成器
Version: v3.1.0
Created: 2026-02-17

整合 GPT 建議的商業版報告格式：
- L1 入門版（數位報告）
- L2 進階版（關係匹配版）
- L3 顧問版（高端場論版）
- L4 長期顧問版

場論公式：
  人 = 先天能量場 × 後天選擇場 × 關係交互場

@織明 × @理樞 × @星殼
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime

# 引入模組
try:
    from relation_analyzer import (
        analyze_all_relations, generate_relation_advice,
        match_two_charts, SHISHEN_MAP
    )
    RELATION_LOADED = True
except ImportError:
    RELATION_LOADED = False

try:
    from wuxing_interaction import (
        generate_flow_analysis, generate_wuxing_diagram,
        generate_interaction_matrix, calculate_compatibility,
        WUXING_FIELD
    )
    WUXING_LOADED = True
except ImportError:
    WUXING_LOADED = False

# ============================================================
# L0: 配置與常量
# ============================================================

REPORT_LEVELS = {
    "L1": {
        "name": "入門版",
        "price_range": "NT$ 2,800 – 3,800",
        "features": ["五行分布", "十神解析", "基礎關係建議", "PDF 15-20頁"],
    },
    "L2": {
        "name": "進階版",
        "price_range": "NT$ 8,800 – 12,800",
        "features": ["五行互動圖", "六親場分析", "十二宮位解析", "關係適配模型", "60分鐘線上講解"],
    },
    "L3": {
        "name": "顧問版",
        "price_range": "NT$ 28,000 – 60,000",
        "features": ["全套場論解析", "個人決策模型", "五行動態流動圖", "伴侶/合夥雙盤匹配", "3個月追蹤調整"],
    },
    "L4": {
        "name": "長期顧問",
        "price_range": "NT$ 120,000+/年",
        "features": ["每月場調整", "重大決策諮詢", "動態流年修正", "專屬顧問服務"],
    },
}

# 十二宮位場論詮釋
GONG_FIELD = {
    "命宮": {"field": "自我主場", "traits": ["自我定位", "人格核心"], "advice": "給自己容錯率"},
    "兄弟": {"field": "同輩場", "traits": ["兄弟姐妹", "同事關係"], "advice": "平等互動，避免比較"},
    "夫妻": {"field": "伴侶場", "traits": ["婚姻關係", "合作夥伴"], "advice": "關係中避免指導姿態"},
    "子女": {"field": "輸出場", "traits": ["子女關係", "創作表達"], "advice": "給予空間，不過度期待"},
    "財帛": {"field": "資源場", "traits": ["財務狀況", "價值觀"], "advice": "穩中求進，理性理財"},
    "疾厄": {"field": "健康場", "traits": ["身體狀況", "壓力承受"], "advice": "注意身心平衡"},
    "遷移": {"field": "外出場", "traits": ["出外運勢", "環境適應"], "advice": "主動拓展，不困原地"},
    "交友": {"field": "人際場", "traits": ["朋友圈層", "社交網絡"], "advice": "與思想型人群相合"},
    "事業": {"field": "事業場", "traits": ["職業發展", "社會定位"], "advice": "適合顧問、系統建構"},
    "田宅": {"field": "根基場", "traits": ["不動產", "家庭根基"], "advice": "穩定根基，不急擴張"},
    "福德": {"field": "內心場", "traits": ["精神狀態", "內在滿足"], "advice": "保持內在流動"},
    "父母": {"field": "長輩場", "traits": ["父母關係", "權威對待"], "advice": "接受但保持獨立"},
}

# ============================================================
# L1: 資料結構
# ============================================================

@dataclass
class CommercialReport:
    """商業版報告"""
    level: str
    name: str
    birth_info: Dict
    sections: List[Dict]
    generated_at: str
    word_count: int

# ============================================================
# L2: 報告區塊生成
# ============================================================

class CommercialReportGenerator:
    """商業版報告生成器"""
    
    def __init__(self, level: str = "L1"):
        self.level = level
        self.level_info = REPORT_LEVELS.get(level, REPORT_LEVELS["L1"])
    
    # ========== 標題區 ==========
    
    def generate_header(self, name: str = "") -> str:
        """生成報告標題"""
        return f"""
╔══════════════════════════════════════════════════════════════════╗
║                                                                  ║
║                    北 斗 命 數 報 告                              ║
║                                                                  ║
║            個人能量場 × 關係結構 × 決策調整模型                    ║
║                                                                  ║
╚══════════════════════════════════════════════════════════════════╝

{f'  報告對象：{name}' if name else ''}
  報告版本：{self.level_info["name"]}
  生成時間：{datetime.now().strftime("%Y-%m-%d %H:%M")}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  📜 認識論聲明

  命盤不是結果。命盤是結構。
  結構決定阻力，人決定方向。
  
  本報告為：
  • 能量結構解析工具
  • 決策場參考模型
  • 自我認知深化輔助

  非宿命論推斷。人始終高於命盤。

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

    # ========== 核心摘要 ==========
    
    def generate_core_summary(self, bazi: Dict, ziwei: Dict) -> str:
        """生成核心結構摘要"""
        day_master = bazi.get("day_master", "")
        day_element = bazi.get("day_element", "")
        strength = bazi.get("strength", {})
        geju = bazi.get("geju", {})
        
        strength_level = strength.get("strength_level", "中和")
        geju_name = geju.get("geju_name", "")
        
        ming_stars = ziwei.get("ming_stars", [])
        ming_stars_str = "、".join(ming_stars[:2]) if ming_stars else "待定"
        
        return f"""
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃  一、核心結構摘要                                                 ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

  • 日主核心：{day_master}{day_element}（日元）
  • 能量傾向：{strength_level}
  • 結構特性：{geju_name}
  • 命宮主星：{ming_stars_str}

  ┌─────────────────────────────────────────────────────────┐
  │  主題命題                                               │
  │                                                         │
  │  規則型人格 × 創造型輸出 × 結構型決策                    │
  └─────────────────────────────────────────────────────────┘

  場論總公式：
  
    人 = 先天能量場 × 後天選擇場 × 關係交互場

"""

    # ========== 八字能量結構 ==========
    
    def generate_bazi_section(self, bazi: Dict) -> str:
        """生成八字能量結構（先天場）"""
        day_master = bazi.get("day_master", "")
        day_element = bazi.get("day_element", "")
        strength = bazi.get("strength", {})
        geju = bazi.get("geju", {})
        wuxing_count = bazi.get("wuxing_count", {})
        
        # 五行場論
        wx_info = WUXING_FIELD.get(day_element, {}) if WUXING_LOADED else {}
        
        # 用神分析
        yongshen = strength.get("yongshen", {})
        yong = yongshen.get("用神", "")
        xi = yongshen.get("喜神", "")
        ji = yongshen.get("忌神", "")
        
        # 格局
        geju_name = geju.get("geju_name", "")
        geju_info = geju.get("geju_info", {})
        
        # 五行分布視覺化
        wx_bars = ""
        max_count = max(wuxing_count.values()) if wuxing_count else 1
        for wx in ["木", "火", "土", "金", "水"]:
            count = wuxing_count.get(wx, 0)
            bar = "█" * count + "░" * (max_count - count)
            wx_bars += f"    {wx}：{bar} ({count})\n"
        
        content = f"""
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃  二、八字能量結構（先天場）                                       ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

  【1】日主定位：{day_master}{day_element}

  {day_master}{day_element}象徵：
  • {wx_info.get('traits', ['結構', '規則', '判準', '框架'])[0]}
  • {wx_info.get('traits', ['結構', '規則', '判準', '框架'])[1]}
  • {wx_info.get('traits', ['結構', '規則', '判準', '框架'])[2]}
  • {wx_info.get('traits', ['結構', '規則', '判準', '框架'])[3]}

  場論詮釋：{wx_info.get('field', '收斂規則場')}
  
  此類人格具備：
  • {wx_info.get('modern', ['分析能力', '標準感', '內在秩序需求'])[0]}
  • 標準感
  • 內在秩序需求

  【2】格局特性：{geju_name}

  {geju_name}象徵：
  • 創造
  • 批判
  • 重構
  • 打破既有秩序

  這意味著：
  你不是守成型人格，而是改造型人格。

  適合：
  • 顧問型工作
  • 內容創作
  • 系統建構
  • 策略思維

  【3】五行分布

{wx_bars}

  【4】用神與平衡策略

  • 用神：{yong}（流動、學習、溝通）
  • 喜神：{xi}（成長、創新）
  • 忌神：{ji}（僵化、過度保守）

  場論詮釋：
  
    {day_element}強需要{yong}潤。
    結構需要流動。
    批判需要出口。

  建議平衡方式：
  • 多輸出思考（寫作、演說）
  • 持續學習新知
  • 避免陷入僵化框架

"""
        return content

    # ========== 十神×六親關係 ==========
    
    def generate_relation_section(self, day_master: str, pillars: Dict) -> str:
        """生成十神×六親關係場"""
        if not RELATION_LOADED:
            return "\n【十神×六親分析】\n（關係分析模組未載入）\n"
        
        relations = analyze_all_relations(day_master, pillars)
        advice = generate_relation_advice(day_master, pillars)
        
        content = f"""
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃  三、十神 × 六親結構（關係場）                                    ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

  以{day_master}為中心，十神代表關係投射。

"""
        # 十神分類說明
        shishen_groups = {
            "比肩/劫財": {
                "element": "同類",
                "liuqin": ["朋友", "競爭者", "同行"],
                "traits": ["易產生觀點衝突", "重平等", "不喜被壓"],
                "advice": "避免標準壓制，採用共創模式"
            },
            "食神/傷官": {
                "element": "我生",
                "liuqin": ["子女", "學生", "輸出對象", "表達能力"],
                "traits": ["創造力強", "表達銳利"],
                "risk": ["言語過直", "容易破壞他人場"],
                "advice": "鋒利不必尖銳，輸出要留餘地"
            },
            "正財/偏財": {
                "element": "我剋",
                "liuqin": ["伴侶", "資源", "金錢", "客戶"],
                "traits": ["與成長型人格相合", "與學習型伴侶相順"],
                "advice": "關係中要給空間，不以標準壓對方"
            },
            "正官/七殺": {
                "element": "剋我",
                "liuqin": ["上司", "制度", "外在權威"],
                "traits": ["遇強勢權威易產生衝突", "對體制敏感"],
                "advice": "學會借勢，不硬碰"
            },
            "正印/偏印": {
                "element": "生我",
                "liuqin": ["長輩", "母系能量", "保護場"],
                "traits": ["過度依賴安全結構會讓你停滯"],
                "advice": "保持流動，不困於舊框架"
            },
        }
        
        idx = 1
        for group_name, info in shishen_groups.items():
            content += f"""
  【{idx}】{group_name}（{info['element']}）

  代表：
  • {'、'.join(info['liuqin'])}

  特性：
  • {'、'.join(info['traits'])}

  調整建議：
  • {info['advice']}

"""
            idx += 1
        
        return content

    # ========== 五行互動 ==========
    
    def generate_wuxing_section(self, day_element: str, wuxing_count: Dict, is_strong: bool) -> str:
        """生成五行互動與反生反剋"""
        if not WUXING_LOADED:
            return "\n【五行互動分析】\n（五行互動模組未載入）\n"
        
        flow = generate_flow_analysis(day_element, wuxing_count, is_strong)
        diagram = generate_wuxing_diagram(day_element, is_strong)
        
        content = f"""
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃  四、五行互動與反生反剋                                           ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

  【五行流動結構圖】
{diagram}

  【相生】

  {day_element}生{flow.yongshen}（{flow.yongshen}為用神）
  → 輸出能帶來流動
  → 創作能提升能量場

  【相剋】

  {flow.blockage[0] if flow.blockage else '火'}過多
  → 強勢環境易消耗你

  【反生反剋】（場論解釋）

  當某元素過強時：
  • 生反成壓
  • 剋反成助

  例如：
  過多土生金 → 金過強 → 流動受阻
  適度火克金 → 反而促成突破

  ┌─────────────────────────────────────────────────────────┐
  │  這就是：阻力有時是推力。                               │
  └─────────────────────────────────────────────────────────┘

  【平衡建議】

"""
        for i, adv in enumerate(flow.advice[:4], 1):
            content += f"  {i}. {adv}\n"
        
        return content

    # ========== 十二宮位場 ==========
    
    def generate_gong_section(self, ziwei: Dict) -> str:
        """生成十二宮位場"""
        content = f"""
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃  五、十二宮位場（關係層級）                                       ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

  （以結構場詮釋，不逐星細論）

"""
        key_gongs = ["命宮", "夫妻", "事業", "交友"]
        for gong in key_gongs:
            info = GONG_FIELD.get(gong, {})
            content += f"""
  【{gong}】（{info.get('field', '')}）

  • {'、'.join(info.get('traits', []))}
  
  建議：{info.get('advice', '')}

"""
        return content

    # ========== 關係調整建議 ==========
    
    def generate_adjustment_section(self) -> str:
        """生成關係調整建議"""
        return """
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃  六、關係調整建議（實用版）                                       ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

  【1】輸出前多 0.5 秒停頓

  這會減少傷官衝擊。

  【2】問句多於結論

  把「我認為」改為「你怎麼看？」

  【3】給伴侶成長空間

  不要把她拉進你的節奏。

  【4】遇強勢權威

  不對抗，改為：結構重組。

"""

    # ========== 總結 ==========
    
    def generate_summary(self, day_element: str, yongshen: str) -> str:
        """生成總結"""
        return f"""
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃  七、總結定位                                                     ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

  你不是衝動型人格。
  你是——

  ┌─────────────────────────────────────────────────────────┐
  │                                                         │
  │        結 構 型 創 造 者                                 │
  │                                                         │
  │        框架建立者 × 系統整合者 × 決策顧問型人格          │
  │                                                         │
  └─────────────────────────────────────────────────────────┘

  當你：
  • 讓{yongshen}流動
  • 讓木成長
  • 不被土困住

  你的場會穩定擴張。

  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  真正的價值在於：

    幫助他人看見結構。

  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

"""

    # ========== 結尾聲明 ==========
    
    def generate_footer(self) -> str:
        """生成結尾聲明"""
        return f"""
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃  報告定位聲明                                                     ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

  這不是算命。
  這是：

    結構解析 × 關係模型 × 決策優化

  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  商業版本特點：
  ✓ 去除技術錯誤訊息
  ✓ 統一場論語言
  ✓ 降低術語密度
  ✓ 強化可讀性
  ✓ 保留北斗模型特色

  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  📘 北斗七星文創
  🔗 報告版本：{self.level_info["name"]}
  📅 生成時間：{datetime.now().strftime("%Y-%m-%d")}

  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

"""

    # ========== 完整報告生成 ==========
    
    def generate_full_report(self, 
                            name: str,
                            bazi: Dict, 
                            ziwei: Dict,
                            pillars: Dict) -> str:
        """生成完整商業版報告"""
        
        day_master = bazi.get("day_master", "")
        day_element = bazi.get("day_element", "")
        wuxing_count = bazi.get("wuxing_count", {})
        strength = bazi.get("strength", {})
        is_strong = strength.get("strength_level", "") in ["極強", "偏強", "中和偏強"]
        yongshen = strength.get("yongshen", {}).get("用神", "水")
        
        report = ""
        
        # 標題
        report += self.generate_header(name)
        
        # 核心摘要
        report += self.generate_core_summary(bazi, ziwei)
        
        # 八字能量結構
        report += self.generate_bazi_section(bazi)
        
        # L2+ 才有的內容
        if self.level in ["L2", "L3", "L4"]:
            # 十神×六親
            report += self.generate_relation_section(day_master, pillars)
            
            # 五行互動
            report += self.generate_wuxing_section(day_element, wuxing_count, is_strong)
        
        # L3+ 才有的內容
        if self.level in ["L3", "L4"]:
            # 十二宮位
            report += self.generate_gong_section(ziwei)
        
        # 關係調整建議
        report += self.generate_adjustment_section()
        
        # 總結
        report += self.generate_summary(day_element, yongshen)
        
        # 結尾
        report += self.generate_footer()
        
        return report


# ============================================================
# 測試
# ============================================================

if __name__ == "__main__":
    print("=== 商業版報告生成測試 ===\n")
    
    # 測試資料
    bazi = {
        "day_master": "庚",
        "day_element": "金",
        "pillars": {"year": "癸丑", "month": "癸丑", "day": "庚子", "hour": "乙酉"},
        "wuxing_count": {"木": 1, "火": 0, "土": 2, "金": 2, "水": 3},
        "strength": {
            "strength_level": "偏強",
            "yongshen": {"用神": "水", "喜神": "木", "忌神": "土"}
        },
        "geju": {"geju_name": "傷官格", "geju_info": {}},
    }
    
    ziwei = {
        "ming_stars": ["天機", "天梁"],
        "ju_shu": 5,
    }
    
    pillars = bazi["pillars"]
    
    # 生成 L2 報告
    generator = CommercialReportGenerator(level="L2")
    report = generator.generate_full_report(
        name="楊三興",
        bazi=bazi,
        ziwei=ziwei,
        pillars=pillars
    )
    
    print(report[:3000])
    print(f"\n... 報告總長度：{len(report)} 字")
