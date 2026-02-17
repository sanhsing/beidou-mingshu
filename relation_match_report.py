#!/usr/bin/env python3
"""
relation_match_report.py - 雙場互動結構分析報告
北斗命數 v3.1 商業版

GPT 戰略定位：這是高價產品核心

封面標題：《雙場互動結構分析報告》
副標：不是合不合。是能量怎麼流。

@織明 × @流祇
"""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime

# 引入模組
try:
    from wuxing_interaction import (
        get_relation, calculate_compatibility, WUXING_FIELD,
        SHENG, KE, SHENG_WO
    )
    from relation_analyzer import get_shishen, SHISHEN_MAP
    MODULES_LOADED = True
except ImportError:
    MODULES_LOADED = False
    # 備用定義
    SHENG = {"木": "火", "火": "土", "土": "金", "金": "水", "水": "木"}
    KE = {"木": "土", "土": "水", "水": "火", "火": "金", "金": "木"}
    SHENG_WO = {v: k for k, v in SHENG.items()}

# ============================================================
# L0: 關係動態模式定義
# ============================================================

RELATION_PATTERNS = {
    "mutual_sheng": {
        "name": "互補型",
        "desc": "雙方能量互相滋養，形成正向循環",
        "emoji": "🔄",
        "traits": ["相互支持", "能量流動順暢", "長期穩定"],
        "advice": "珍惜這種結構，保持雙向流動",
    },
    "one_way_sheng": {
        "name": "單向付出型",
        "desc": "一方持續生另一方，能量單向流動",
        "emoji": "➡️",
        "traits": ["付出不均", "依賴關係", "需要平衡"],
        "advice": "付出方注意保存能量，接受方學會回饋",
    },
    "mutual_ke": {
        "name": "消耗型",
        "desc": "雙方能量互相消耗，容易產生衝突",
        "emoji": "⚔️",
        "traits": ["競爭關係", "壓力來源", "需要調和"],
        "advice": "找到第三方元素作為緩衝，減少直接碰撞",
    },
    "one_way_ke": {
        "name": "壓力型",
        "desc": "一方持續剋另一方，形成壓力關係",
        "emoji": "⬇️",
        "traits": ["權力不均", "壓力來源", "需要轉化"],
        "advice": "被剋方學會借勢轉化，剋方適度收斂",
    },
    "resonance": {
        "name": "共振型",
        "desc": "雙方同類五行，能量同頻共振",
        "emoji": "🎵",
        "traits": ["理解容易", "競爭可能", "需要分工"],
        "advice": "避免主導權爭奪，找到各自領域",
    },
    "neutral": {
        "name": "中性型",
        "desc": "無直接生剋關係，需要中介連結",
        "emoji": "⚖️",
        "traits": ["互動較少", "需要橋樑", "可塑性高"],
        "advice": "找到共同興趣或中介元素，建立連結",
    },
}

# ============================================================
# L1: 資料結構
# ============================================================

@dataclass
class PersonProfile:
    """個人能量檔案"""
    name: str
    day_master: str           # 日主天干
    day_element: str          # 日主五行
    strength_level: str       # 身強身弱
    wuxing_count: Dict[str, int]
    yongshen: str            # 用神
    jishen: str              # 忌神

@dataclass
class RelationFlow:
    """關係流動分析"""
    a_to_b: str              # A 對 B 的關係
    b_to_a: str              # B 對 A 的關係
    a_shishen_to_b: str      # A 視 B 為什麼十神
    b_shishen_to_a: str      # B 視 A 為什麼十神
    pattern: str             # 關係模式
    compatibility: int       # 相容度 (0-100)

# ============================================================
# L2: 分析函數
# ============================================================

def analyze_relation_flow(a: PersonProfile, b: PersonProfile) -> RelationFlow:
    """分析雙方關係流動"""
    
    a_wx = a.day_element
    b_wx = b.day_element
    
    # 計算雙向關係
    if a_wx == b_wx:
        a_to_b = "同類"
        b_to_a = "同類"
        pattern = "resonance"
        compat = 70
    elif SHENG.get(a_wx) == b_wx:
        a_to_b = "我生"
        b_to_a = "生我"
        if SHENG.get(b_wx) == a_wx:
            pattern = "mutual_sheng"
            compat = 90
        else:
            pattern = "one_way_sheng"
            compat = 75
    elif SHENG.get(b_wx) == a_wx:
        a_to_b = "生我"
        b_to_a = "我生"
        pattern = "one_way_sheng"
        compat = 75
    elif KE.get(a_wx) == b_wx:
        a_to_b = "我剋"
        b_to_a = "剋我"
        if KE.get(b_wx) == a_wx:
            pattern = "mutual_ke"
            compat = 40
        else:
            pattern = "one_way_ke"
            compat = 50
    elif KE.get(b_wx) == a_wx:
        a_to_b = "剋我"
        b_to_a = "我剋"
        pattern = "one_way_ke"
        compat = 50
    else:
        a_to_b = "間接"
        b_to_a = "間接"
        pattern = "neutral"
        compat = 60
    
    # 計算十神關係
    a_shishen = get_shishen(a.day_master, b.day_master) if MODULES_LOADED else "待計算"
    b_shishen = get_shishen(b.day_master, a.day_master) if MODULES_LOADED else "待計算"
    
    return RelationFlow(
        a_to_b=a_to_b,
        b_to_a=b_to_a,
        a_shishen_to_b=a_shishen,
        b_shishen_to_a=b_shishen,
        pattern=pattern,
        compatibility=compat,
    )

def generate_flow_diagram_ascii(a: PersonProfile, b: PersonProfile, flow: RelationFlow) -> str:
    """生成雙向流動 ASCII 圖"""
    
    pattern_info = RELATION_PATTERNS.get(flow.pattern, RELATION_PATTERNS["neutral"])
    
    # 根據關係類型選擇箭頭
    if flow.a_to_b == "我生":
        a_arrow = "───▶"
        b_arrow = "◀───"
    elif flow.a_to_b == "生我":
        a_arrow = "◀───"
        b_arrow = "───▶"
    elif flow.a_to_b == "我剋":
        a_arrow = "═══▶"
        b_arrow = "◀═══"
    elif flow.a_to_b == "剋我":
        a_arrow = "◀═══"
        b_arrow = "═══▶"
    else:
        a_arrow = "────"
        b_arrow = "────"
    
    diagram = f"""
    ╔═══════════════════════════════════════════════════════════════╗
    ║                    雙向能量流動圖                              ║
    ╚═══════════════════════════════════════════════════════════════╝
    
         ┌─────────────┐                      ┌─────────────┐
         │  {a.name:^9}  │                      │  {b.name:^9}  │
         │             │                      │             │
         │  {a.day_master}{a.day_element}（日主）│                      │  {b.day_master}{b.day_element}（日主）│
         │  {a.strength_level:^9}│                      │  {b.strength_level:^9}│
         └─────────────┘                      └─────────────┘
                │                                    │
                │         A → B: {flow.a_to_b:^6}            │
                │{a_arrow}─────────────────────{a_arrow}│
                │                                    │
                │         B → A: {flow.b_to_a:^6}            │
                │{b_arrow}─────────────────────{b_arrow}│
                │                                    │
    
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    關係模式：{pattern_info['emoji']} {pattern_info['name']}
    相容度：{flow.compatibility}%
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
    return diagram

# ============================================================
# L3: 報告生成
# ============================================================

class RelationMatchReportGenerator:
    """雙場互動結構分析報告生成器"""
    
    def __init__(self):
        self.generated_at = datetime.now().strftime("%Y-%m-%d %H:%M")
    
    def generate_cover(self, a: PersonProfile, b: PersonProfile) -> str:
        """生成封面"""
        return f"""
╔══════════════════════════════════════════════════════════════════╗
║                                                                  ║
║              《 雙 場 互 動 結 構 分 析 報 告 》                  ║
║                                                                  ║
║                   不是合不合。是能量怎麼流。                      ║
║                                                                  ║
╚══════════════════════════════════════════════════════════════════╝

  ┌─────────────────────────────────────────────────────────────┐
  │                                                             │
  │    A 方：{a.name}                                            │
  │    B 方：{b.name}                                            │
  │                                                             │
  │    報告類型：關係結構分析                                    │
  │    生成時間：{self.generated_at}                              │
  │                                                             │
  └─────────────────────────────────────────────────────────────┘

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  📜 閱讀須知

  本報告分析的是「能量結構」，不是「緣分好壞」。
  
  關係的品質取決於：
  • 雙方如何理解彼此的結構
  • 如何調整互動模式
  • 如何平衡能量流動
  
  結構可以理解，關係可以優化。
  
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

    def generate_part1_profiles(self, a: PersonProfile, b: PersonProfile) -> str:
        """第一部分：雙方主場"""
        
        def format_wuxing_bar(wuxing_count: Dict[str, int]) -> str:
            total = sum(wuxing_count.values()) or 1
            bars = ""
            for wx in ["木", "火", "土", "金", "水"]:
                count = wuxing_count.get(wx, 0)
                pct = int((count / total) * 10)
                bar = "█" * pct + "░" * (10 - pct)
                bars += f"    {wx}：{bar} ({count})\n"
            return bars
        
        return f"""
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃  第一部分：雙方主場                                               ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

  【A 方】{a.name}
  
  日主：{a.day_master}{a.day_element}
  能量傾向：{a.strength_level}
  用神：{a.yongshen}｜忌神：{a.jishen}
  
  五行分布：
{format_wuxing_bar(a.wuxing_count)}

  ────────────────────────────────────────────────────────────────

  【B 方】{b.name}
  
  日主：{b.day_master}{b.day_element}
  能量傾向：{b.strength_level}
  用神：{b.yongshen}｜忌神：{b.jishen}
  
  五行分布：
{format_wuxing_bar(b.wuxing_count)}

"""

    def generate_part2_flow(self, a: PersonProfile, b: PersonProfile, flow: RelationFlow) -> str:
        """第二部分：雙向流動"""
        
        diagram = generate_flow_diagram_ascii(a, b, flow)
        
        return f"""
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃  第二部分：雙向流動                                               ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

{diagram}

  【流動解讀】

  {a.name} → {b.name}：{flow.a_to_b}
  • {a.name} 視 {b.name} 為「{flow.a_shishen_to_b}」
  • 這意味著：{self._get_shishen_meaning(flow.a_shishen_to_b, a.name, b.name)}

  {b.name} → {a.name}：{flow.b_to_a}
  • {b.name} 視 {a.name} 為「{flow.b_shishen_to_a}」
  • 這意味著：{self._get_shishen_meaning(flow.b_shishen_to_a, b.name, a.name)}

"""

    def _get_shishen_meaning(self, shishen: str, viewer: str, target: str) -> str:
        """獲取十神關係的白話解釋"""
        meanings = {
            "比肩": f"{viewer} 視 {target} 為平等的夥伴或競爭者",
            "劫財": f"{viewer} 視 {target} 為競爭對象，容易有資源爭奪",
            "食神": f"{viewer} 會自然地照顧或滋養 {target}",
            "傷官": f"{viewer} 會對 {target} 有批判或改造的傾向",
            "正財": f"{viewer} 視 {target} 為穩定的資源或伴侶",
            "偏財": f"{viewer} 視 {target} 為流動的資源或機會",
            "正官": f"{viewer} 視 {target} 為權威或約束來源",
            "七殺": f"{viewer} 視 {target} 為壓力或挑戰來源",
            "正印": f"{viewer} 視 {target} 為保護者或滋養來源",
            "偏印": f"{viewer} 視 {target} 為特殊的支持或冷門貴人",
        }
        return meanings.get(shishen, f"{viewer} 與 {target} 有特殊的能量互動")

    def generate_part3_pattern(self, flow: RelationFlow) -> str:
        """第三部分：關係動態模式"""
        
        pattern_info = RELATION_PATTERNS.get(flow.pattern, RELATION_PATTERNS["neutral"])
        
        # 相容度視覺化
        compat_bar = "█" * (flow.compatibility // 10) + "░" * (10 - flow.compatibility // 10)
        
        if flow.compatibility >= 80:
            compat_level = "高相容"
            compat_emoji = "🟢"
        elif flow.compatibility >= 60:
            compat_level = "中相容"
            compat_emoji = "🟡"
        else:
            compat_level = "低相容"
            compat_emoji = "🔴"
        
        return f"""
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃  第三部分：關係動態模式                                           ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

  ┌─────────────────────────────────────────────────────────────┐
  │                                                             │
  │    關係模式：{pattern_info['emoji']} {pattern_info['name']}                              │
  │                                                             │
  │    {pattern_info['desc']}                                    │
  │                                                             │
  └─────────────────────────────────────────────────────────────┘

  【模式特徵】
  
  • {pattern_info['traits'][0]}
  • {pattern_info['traits'][1]}
  • {pattern_info['traits'][2]}

  【相容度】
  
  {compat_emoji} {compat_level}：{compat_bar} {flow.compatibility}%

  【場論解讀】
  
  這不是「好不好」的問題。
  這是「能量怎麼流」的問題。
  
  任何模式都可以運作良好，
  關鍵在於：雙方是否理解這個結構，並願意調整。

"""

    def generate_part4_advice(self, a: PersonProfile, b: PersonProfile, flow: RelationFlow) -> str:
        """第四部分：調整建議"""
        
        pattern_info = RELATION_PATTERNS.get(flow.pattern, RELATION_PATTERNS["neutral"])
        
        # 根據模式生成具體建議
        if flow.pattern == "one_way_sheng":
            if flow.a_to_b == "我生":
                giver, receiver = a.name, b.name
            else:
                giver, receiver = b.name, a.name
            specific_advice = f"""
  【能量平衡】
  
  {giver} 是能量付出方：
  • 注意保存自己的能量
  • 不要過度犧牲
  • 建立自己的獨立空間
  
  {receiver} 是能量接收方：
  • 學會主動回饋
  • 表達感謝和認可
  • 不要理所當然
"""
        elif flow.pattern == "one_way_ke":
            if flow.a_to_b == "我剋":
                presser, pressed = a.name, b.name
            else:
                presser, pressed = b.name, a.name
            specific_advice = f"""
  【壓力轉化】
  
  {presser} 是壓力來源方：
  • 適度收斂強勢
  • 給對方空間
  • 換位思考
  
  {pressed} 是壓力承受方：
  • 學會借勢轉化
  • 壓力可以成為推力
  • 找到自己的優勢領域
"""
        elif flow.pattern == "mutual_ke":
            specific_advice = """
  【衝突緩和】
  
  雙方都有壓力輸出傾向：
  • 找到第三方元素作為緩衝
  • 建立共同目標
  • 避免正面硬碰
  • 分工明確，各自領域
"""
        elif flow.pattern == "resonance":
            specific_advice = """
  【同類協作】
  
  雙方能量同頻：
  • 容易理解彼此
  • 但也容易競爭
  • 需要明確分工
  • 找到各自的主導領域
"""
        else:
            specific_advice = """
  【通用建議】
  
  • 理解彼此的能量結構
  • 接受差異，不要改造對方
  • 找到互補的切入點
  • 保持溝通開放
"""
        
        return f"""
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃  第四部分：調整建議                                               ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

  【核心原則】
  
  不講好壞，講平衡。
  不講對錯，講調整。

{specific_advice}

  【通用調整策略】
  
  1. 理解對方的能量結構
     → 不是改變對方，是理解對方
  
  2. 識別自己的流動方向
     → 知道自己在付出還是接收
  
  3. 找到平衡點
     → 不是 50/50，是雙方都舒服
  
  4. 建立共同的第三空間
     → 共同目標、共同興趣、共同規則

  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  
  {pattern_info['advice']}
  
  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

"""

    def generate_footer(self) -> str:
        """生成結尾"""
        return f"""
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃  報告結語                                                         ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

  關係不是宿命。
  關係是兩個能量場的互動結構。
  
  結構可以理解。
  理解了，就可以調整。
  調整了，關係就會流動。

  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  📘 北斗七星文創
  🔗 雙場互動結構分析報告
  📅 {self.generated_at}

  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

"""

    def generate_full_report(self, a: PersonProfile, b: PersonProfile) -> str:
        """生成完整報告"""
        
        flow = analyze_relation_flow(a, b)
        
        report = ""
        report += self.generate_cover(a, b)
        report += self.generate_part1_profiles(a, b)
        report += self.generate_part2_flow(a, b, flow)
        report += self.generate_part3_pattern(flow)
        report += self.generate_part4_advice(a, b, flow)
        report += self.generate_footer()
        
        return report


# ============================================================
# 測試
# ============================================================

if __name__ == "__main__":
    print("=== 雙場互動結構分析報告測試 ===\n")
    
    # 測試數據
    a = PersonProfile(
        name="北斗",
        day_master="庚",
        day_element="金",
        strength_level="偏強",
        wuxing_count={"木": 1, "火": 0, "土": 2, "金": 2, "水": 3},
        yongshen="水",
        jishen="土",
    )
    
    b = PersonProfile(
        name="伴侶",
        day_master="乙",
        day_element="木",
        strength_level="中和",
        wuxing_count={"木": 2, "火": 2, "土": 1, "金": 1, "水": 2},
        yongshen="水",
        jishen="金",
    )
    
    generator = RelationMatchReportGenerator()
    report = generator.generate_full_report(a, b)
    
    print(report[:3000])
    print("\n... (中略) ...\n")
    print(report[-1500:])
    print(f"\n報告總長度：{len(report)} 字")
