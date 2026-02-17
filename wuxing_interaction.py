#!/usr/bin/env python3
"""
wuxing_interaction.py - 五行互動模型
北斗命數 v3.1 商業版

PYLIB: L2-wuxing-interaction
Version: v1.0.0
Created: 2026-02-17

功能：
1. 五行相生相剋分析
2. 反生反剋模型
3. 五行流動圖生成
4. 五行適配度計算

場論公式：
  金強需水潤。結構需流動。批判需出口。

@理樞 × @織明
"""

from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass

# ============================================================
# L0: 五行基礎定義
# ============================================================

WUXING = ["木", "火", "土", "金", "水"]

# 相生關係：A 生 B
SHENG = {
    "木": "火",  # 木生火
    "火": "土",  # 火生土
    "土": "金",  # 土生金
    "金": "水",  # 金生水
    "水": "木",  # 水生木
}

# 相剋關係：A 剋 B
KE = {
    "木": "土",  # 木剋土
    "土": "水",  # 土剋水
    "水": "火",  # 水剋火
    "火": "金",  # 火剋金
    "金": "木",  # 金剋木
}

# 被生關係：誰生我
SHENG_WO = {v: k for k, v in SHENG.items()}

# 被剋關係：誰剋我
KE_WO = {v: k for k, v in KE.items()}

# 五行場論詮釋
WUXING_FIELD = {
    "木": {
        "name": "木",
        "field": "生長擴張場",
        "traits": ["生長", "擴張", "創新", "彈性"],
        "modern": ["創業", "學習", "成長", "發展"],
        "strength": "適應力強、持續成長",
        "risk": "過度擴張、根基不穩",
    },
    "火": {
        "name": "火",
        "field": "輻射表現場",
        "traits": ["熱情", "表現", "輻射", "照亮"],
        "modern": ["展示", "銷售", "演說", "領導"],
        "strength": "感染力強、引領方向",
        "risk": "燃燒殆盡、過度消耗",
    },
    "土": {
        "name": "土",
        "field": "承載穩定場",
        "traits": ["穩定", "承載", "包容", "厚重"],
        "modern": ["管理", "協調", "穩定", "累積"],
        "strength": "根基穩固、值得信賴",
        "risk": "僵化保守、缺乏變通",
    },
    "金": {
        "name": "金",
        "field": "收斂規則場",
        "traits": ["果斷", "收斂", "規則", "判準"],
        "modern": ["決策", "制度", "效率", "標準"],
        "strength": "執行力強、標準清晰",
        "risk": "過於嚴苛、缺乏彈性",
    },
    "水": {
        "name": "水",
        "field": "流動智慧場",
        "traits": ["流動", "智慧", "變通", "滲透"],
        "modern": ["思考", "學習", "溝通", "適應"],
        "strength": "智慧通達、適應力強",
        "risk": "飄忽不定、缺乏堅持",
    },
}

# ============================================================
# L1: 資料結構
# ============================================================

@dataclass
class WuxingRelation:
    """五行關係"""
    source: str       # 來源五行
    target: str       # 目標五行
    relation: str     # 關係類型（生/剋/同/被生/被剋）
    direction: str    # 方向（我生/生我/我剋/剋我/同類）
    field_desc: str   # 場論描述
    advice: str       # 建議

@dataclass
class WuxingFlow:
    """五行流動分析"""
    day_wx: str               # 日主五行
    yongshen: str             # 用神
    xishen: str               # 喜神
    jishen: str               # 忌神
    flow_path: List[str]      # 最佳流動路徑
    blockage: List[str]       # 阻塞來源
    advice: List[str]         # 調整建議

# ============================================================
# L2: 核心函數
# ============================================================

def get_relation(wx1: str, wx2: str) -> WuxingRelation:
    """計算兩個五行的關係"""
    if wx1 == wx2:
        return WuxingRelation(
            source=wx1, target=wx2,
            relation="同類",
            direction="同場",
            field_desc=f"同為{WUXING_FIELD[wx1]['field']}，能量同頻",
            advice="合作共創，但注意主導權分配"
        )
    
    # 我生對方
    if SHENG.get(wx1) == wx2:
        return WuxingRelation(
            source=wx1, target=wx2,
            relation="相生",
            direction="我生",
            field_desc=f"{wx1}生{wx2}，你會輸出能量給對方",
            advice="輸出帶來流動，但注意不要過度付出"
        )
    
    # 對方生我
    if SHENG.get(wx2) == wx1:
        return WuxingRelation(
            source=wx1, target=wx2,
            relation="被生",
            direction="生我",
            field_desc=f"{wx2}生{wx1}，對方會滋養你",
            advice="接受滋養但保持獨立，避免過度依賴"
        )
    
    # 我剋對方
    if KE.get(wx1) == wx2:
        return WuxingRelation(
            source=wx1, target=wx2,
            relation="相剋",
            direction="我剋",
            field_desc=f"{wx1}剋{wx2}，你會控制或消耗對方",
            advice="掌控但不壓制，給對方空間"
        )
    
    # 對方剋我
    if KE.get(wx2) == wx1:
        return WuxingRelation(
            source=wx1, target=wx2,
            relation="被剋",
            direction="剋我",
            field_desc=f"{wx2}剋{wx1}，對方會給你壓力",
            advice="學會借勢轉化，壓力可成動力"
        )
    
    return WuxingRelation(
        source=wx1, target=wx2,
        relation="無直接關係",
        direction="間接",
        field_desc="需透過其他五行中介",
        advice="尋找共同連結點"
    )

def analyze_reverse_sheng_ke(wx: str, wx_count: Dict[str, int]) -> List[str]:
    """
    分析反生反剋
    
    場論解釋：
    - 當某元素過強時，生反成壓
    - 當某元素過弱時，剋反成助
    """
    insights = []
    
    # 誰生我
    sheng_wo = SHENG_WO.get(wx)
    if sheng_wo and wx_count.get(sheng_wo, 0) > 2:
        insights.append(f"⚠️ {sheng_wo}過多生{wx} → 反成壓力（生反成壓）")
        insights.append(f"   建議：減少對{sheng_wo}的依賴，增加流動")
    
    # 誰剋我
    ke_wo = KE_WO.get(wx)
    if ke_wo and wx_count.get(ke_wo, 0) == 1:
        insights.append(f"💡 適度{ke_wo}剋{wx} → 反成推力（剋反成助）")
        insights.append(f"   說明：適度壓力促進突破")
    
    # 我生誰
    wo_sheng = SHENG.get(wx)
    if wo_sheng and wx_count.get(wo_sheng, 0) > 2:
        insights.append(f"⚠️ {wx}過度生{wo_sheng} → 消耗過大")
        insights.append(f"   建議：控制輸出節奏，保存能量")
    
    return insights

def generate_flow_analysis(day_wx: str, wx_count: Dict[str, int], is_strong: bool) -> WuxingFlow:
    """
    生成五行流動分析
    
    身強：需要洩耗（我生、我剋）
    身弱：需要生扶（生我、同類）
    """
    wo_sheng = SHENG.get(day_wx)      # 我生
    sheng_wo = SHENG_WO.get(day_wx)   # 生我
    wo_ke = KE.get(day_wx)            # 我剋
    ke_wo = KE_WO.get(day_wx)         # 剋我
    
    if is_strong:
        # 身強用洩耗
        yongshen = wo_sheng           # 用神：我生
        xishen = SHENG.get(wo_sheng)  # 喜神：食傷生財
        jishen = sheng_wo             # 忌神：生我
        flow_path = [day_wx, wo_sheng, SHENG.get(wo_sheng, "")]
        blockage = [sheng_wo, f"過多{sheng_wo}會阻塞流動"]
    else:
        # 身弱用生扶
        yongshen = sheng_wo           # 用神：生我
        xishen = day_wx               # 喜神：同類
        jishen = wo_sheng             # 忌神：我生（洩氣）
        flow_path = [sheng_wo, day_wx]
        blockage = [wo_sheng, f"過多{wo_sheng}會過度消耗"]
    
    # 生成建議
    advice = []
    wx_info = WUXING_FIELD.get(day_wx, {})
    yong_info = WUXING_FIELD.get(yongshen, {})
    
    if is_strong:
        advice.append(f"{day_wx}強需{yongshen}潤，{wx_info.get('field', '')}需要流動出口")
        advice.append(f"多輸出（{yong_info.get('modern', ['輸出'])[0]}）能帶來平衡")
        advice.append(f"避免{sheng_wo}過多（過度保護反成壓力）")
    else:
        advice.append(f"{day_wx}弱需{yongshen}生，需要外部支持")
        advice.append(f"多連結（{yong_info.get('modern', ['連結'])[0]}）能獲得能量")
        advice.append(f"避免{wo_sheng}過多（過度輸出會消耗自己）")
    
    # 加入反生反剋洞見
    reverse_insights = analyze_reverse_sheng_ke(day_wx, wx_count)
    if reverse_insights:
        advice.extend(reverse_insights)
    
    return WuxingFlow(
        day_wx=day_wx,
        yongshen=yongshen,
        xishen=xishen,
        jishen=jishen,
        flow_path=[x for x in flow_path if x],
        blockage=blockage,
        advice=advice
    )

def generate_wuxing_diagram(day_wx: str, is_strong: bool) -> str:
    """
    生成五行流動圖（ASCII）
    """
    wo_sheng = SHENG.get(day_wx, "?")
    sheng_wo = SHENG_WO.get(day_wx, "?")
    wo_ke = KE.get(day_wx, "?")
    ke_wo = KE_WO.get(day_wx, "?")
    
    if is_strong:
        # 身強：強調洩耗路徑
        diagram = f"""
        {ke_wo}（剋我：壓力場）
           ↓
{sheng_wo}（印星：保護場）→ 【{day_wx}】（日主核心）→ {wo_sheng}（輸出場）→ {KE.get(wo_sheng, "?")}（財場）
           ↑__________________________|
                 最佳流動路徑 →→→
"""
    else:
        # 身弱：強調生扶路徑
        diagram = f"""
        {ke_wo}（剋我：壓力場）
           ↓
{sheng_wo}（印星：保護場）→ 【{day_wx}】（日主核心）
     ↑                    
     最佳補充路徑 ←←←
"""
    
    return diagram

def calculate_compatibility(wx1: str, wx2: str) -> Dict:
    """
    計算五行相容度
    """
    rel = get_relation(wx1, wx2)
    
    # 相容度評分
    scores = {
        "同類": 70,
        "相生": 90,  # 我生對方
        "被生": 85,  # 對方生我
        "相剋": 40,  # 我剋對方
        "被剋": 30,  # 對方剋我
    }
    
    score = scores.get(rel.relation, 50)
    
    # 評級
    if score >= 85:
        level = "高相容"
        emoji = "🟢"
    elif score >= 60:
        level = "中相容"
        emoji = "🟡"
    else:
        level = "低相容"
        emoji = "🔴"
    
    return {
        "wx1": wx1,
        "wx2": wx2,
        "relation": rel.relation,
        "direction": rel.direction,
        "score": score,
        "level": level,
        "emoji": emoji,
        "advice": rel.advice,
        "field_desc": rel.field_desc,
    }

# ============================================================
# L3: 互動矩陣
# ============================================================

def generate_interaction_matrix(day_wx: str) -> List[Dict]:
    """
    生成五行互動矩陣
    """
    matrix = []
    for wx in WUXING:
        compat = calculate_compatibility(day_wx, wx)
        matrix.append(compat)
    
    return sorted(matrix, key=lambda x: -x["score"])

# ============================================================
# 測試
# ============================================================

if __name__ == "__main__":
    print("=== 五行互動測試 ===\n")
    
    # 測試：金日主
    day_wx = "金"
    wx_count = {"木": 1, "火": 0, "土": 2, "金": 2, "水": 3}
    is_strong = True
    
    print(f"日主五行：{day_wx}")
    print(f"五行分布：{wx_count}")
    print(f"身強身弱：{'偏強' if is_strong else '偏弱'}\n")
    
    # 流動分析
    flow = generate_flow_analysis(day_wx, wx_count, is_strong)
    print(f"用神：{flow.yongshen}")
    print(f"喜神：{flow.xishen}")
    print(f"忌神：{flow.jishen}")
    print(f"最佳路徑：{'→'.join(flow.flow_path)}")
    print("\n建議：")
    for a in flow.advice:
        print(f"  {a}")
    
    # 流動圖
    print("\n=== 五行流動圖 ===")
    print(generate_wuxing_diagram(day_wx, is_strong))
    
    # 互動矩陣
    print("=== 五行相容度 ===")
    matrix = generate_interaction_matrix(day_wx)
    for m in matrix:
        print(f"{m['emoji']} {day_wx}→{m['wx2']}：{m['relation']} ({m['score']}分) - {m['level']}")
