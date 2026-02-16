#!/usr/bin/env python3
"""
北斗命數 文公尺濾網 v1.0
========================
魯班尺（陽宅）+ 丁蘭尺（陰宅）

用途：
1. 門窗尺寸吉凶（裝修濾網）
2. 姓名總筆畫吉凶（命名輔助）
3. 神位牌位尺寸（祭祀用品）

北斗七星文創 × 織明 | 2026-02-15
"""

from dataclasses import dataclass
from typing import List, Dict, Tuple

# ============================================================
# 魯班尺（門公尺）- 陽宅用
# ============================================================
# 一魯班尺 = 42.9cm，分為8格
# 每格約 5.36cm

LUBAN_GATES = [
    {
        "name": "財",
        "jixiong": "吉",
        "meaning": "財德、進益、大吉",
        "sub": [
            ("財德", "大吉", "招財進寶"),
            ("寶庫", "大吉", "錢財聚集"),
            ("六合", "吉", "六親和睦"),
            ("迎福", "吉", "迎接福氣"),
        ]
    },
    {
        "name": "病",
        "jixiong": "凶",
        "meaning": "災病、退財、凶",
        "sub": [
            ("退財", "凶", "財運衰退"),
            ("公事", "凶", "官司是非"),
            ("牢執", "大凶", "牢獄之災"),
            ("孤寡", "大凶", "孤獨寡居"),
        ]
    },
    {
        "name": "離",
        "jixiong": "凶",
        "meaning": "六親離散、凶",
        "sub": [
            ("長庫", "凶", "長期困頓"),
            ("劫財", "凶", "錢財被劫"),
            ("官鬼", "大凶", "官災鬼祟"),
            ("失脫", "凶", "失去財物"),
        ]
    },
    {
        "name": "義",
        "jixiong": "吉",
        "meaning": "義氣、正義、吉",
        "sub": [
            ("添丁", "大吉", "添丁進口"),
            ("益利", "大吉", "利益增加"),
            ("貴子", "大吉", "得貴子"),
            ("大吉", "大吉", "諸事大吉"),
        ]
    },
    {
        "name": "官",
        "jixiong": "吉",
        "meaning": "官運、升遷、吉",
        "sub": [
            ("順科", "大吉", "科考順利"),
            ("橫財", "吉", "意外之財"),
            ("進益", "吉", "利益增進"),
            ("富貴", "大吉", "榮華富貴"),
        ]
    },
    {
        "name": "劫",
        "jixiong": "凶",
        "meaning": "劫財、凶險、凶",
        "sub": [
            ("死別", "大凶", "生離死別"),
            ("退口", "大凶", "人丁損傷"),
            ("離鄉", "凶", "背井離鄉"),
            ("財失", "凶", "財物損失"),
        ]
    },
    {
        "name": "害",
        "jixiong": "凶",
        "meaning": "災害、口舌、凶",
        "sub": [
            ("災至", "大凶", "災禍降臨"),
            ("死絕", "大凶", "絕後之憂"),
            ("病臨", "凶", "疾病纏身"),
            ("口舌", "凶", "口舌是非"),
        ]
    },
    {
        "name": "本",
        "jixiong": "吉",
        "meaning": "本位、守成、吉",
        "sub": [
            ("財至", "大吉", "財運亨通"),
            ("登科", "大吉", "金榜題名"),
            ("進寶", "大吉", "招財進寶"),
            ("興旺", "大吉", "興旺發達"),
        ]
    },
]

# 一魯班尺 = 42.9cm
LUBAN_UNIT = 42.9
LUBAN_GATE_SIZE = LUBAN_UNIT / 8  # 每格約 5.36cm


# ============================================================
# 丁蘭尺 - 陰宅/神位用
# ============================================================
# 一丁蘭尺 = 38.8cm，分為10格

DINGLAN_GATES = [
    {"name": "丁", "jixiong": "吉", "meaning": "添丁進財"},
    {"name": "害", "jixiong": "凶", "meaning": "災害口舌"},
    {"name": "旺", "jixiong": "吉", "meaning": "興旺發達"},
    {"name": "苦", "jixiong": "凶", "meaning": "辛苦勞碌"},
    {"name": "義", "jixiong": "吉", "meaning": "講究義氣"},
    {"name": "官", "jixiong": "吉", "meaning": "官運亨通"},
    {"name": "死", "jixiong": "凶", "meaning": "死亡災禍"},
    {"name": "興", "jixiong": "吉", "meaning": "興旺繁榮"},
    {"name": "失", "jixiong": "凶", "meaning": "損失破敗"},
    {"name": "財", "jixiong": "吉", "meaning": "財運亨通"},
]

DINGLAN_UNIT = 38.8
DINGLAN_GATE_SIZE = DINGLAN_UNIT / 10  # 每格約 3.88cm


@dataclass
class RulerResult:
    """尺寸吉凶結果"""
    cm: float
    ruler_type: str  # "魯班" / "丁蘭"
    gate_name: str
    jixiong: str
    meaning: str
    sub_gate: str = ""
    sub_meaning: str = ""
    advice: str = ""


def measure_luban(cm: float) -> RulerResult:
    """
    用魯班尺測量尺寸
    
    cm: 尺寸（公分）
    返回: 吉凶結果
    """
    # 取餘數確定落在哪一格
    remainder = cm % LUBAN_UNIT
    gate_idx = int(remainder // LUBAN_GATE_SIZE) % 8
    sub_idx = int((remainder % LUBAN_GATE_SIZE) / (LUBAN_GATE_SIZE / 4)) % 4
    
    gate = LUBAN_GATES[gate_idx]
    sub = gate["sub"][sub_idx]
    
    # 建議
    if gate["jixiong"] == "吉":
        advice = f"此尺寸落在「{gate['name']}」門，{sub[2]}，屬吉。"
    else:
        advice = f"此尺寸落在「{gate['name']}」門，{sub[2]}，建議調整。"
    
    return RulerResult(
        cm=cm,
        ruler_type="魯班尺",
        gate_name=gate["name"],
        jixiong=gate["jixiong"],
        meaning=gate["meaning"],
        sub_gate=sub[0],
        sub_meaning=sub[2],
        advice=advice
    )


def measure_dinglan(cm: float) -> RulerResult:
    """
    用丁蘭尺測量尺寸
    
    cm: 尺寸（公分）
    返回: 吉凶結果
    """
    remainder = cm % DINGLAN_UNIT
    gate_idx = int(remainder // DINGLAN_GATE_SIZE) % 10
    
    gate = DINGLAN_GATES[gate_idx]
    
    if gate["jixiong"] == "吉":
        advice = f"此尺寸落在「{gate['name']}」字，{gate['meaning']}，適合神位牌位。"
    else:
        advice = f"此尺寸落在「{gate['name']}」字，{gate['meaning']}，建議調整尺寸。"
    
    return RulerResult(
        cm=cm,
        ruler_type="丁蘭尺",
        gate_name=gate["name"],
        jixiong=gate["jixiong"],
        meaning=gate["meaning"],
        advice=advice
    )


def find_good_size(target_cm: float, ruler: str = "魯班", tolerance: float = 5.0) -> List[RulerResult]:
    """
    在目標尺寸附近找吉祥尺寸
    
    target_cm: 目標尺寸
    ruler: "魯班" 或 "丁蘭"
    tolerance: 允許偏差（正負）
    
    返回: 吉祥尺寸列表
    """
    results = []
    
    measure_func = measure_luban if ruler == "魯班" else measure_dinglan
    
    # 以0.1cm為單位搜索
    current = target_cm - tolerance
    while current <= target_cm + tolerance:
        result = measure_func(current)
        if result.jixiong == "吉":
            results.append(result)
        current += 0.1
    
    # 去重（保留首次出現的吉門）
    seen = set()
    unique_results = []
    for r in results:
        key = r.gate_name
        if key not in seen:
            seen.add(key)
            unique_results.append(r)
    
    return unique_results


def stroke_to_luban(strokes: int) -> RulerResult:
    """
    姓名筆畫對應魯班尺吉凶
    
    用於命名參考：總筆畫落在哪個門
    """
    # 筆畫轉換為「單位」：每筆畫視為一個單位
    # 這是民間的一種用法，將筆畫循環對應八門
    gate_idx = (strokes - 1) % 8
    
    gate = LUBAN_GATES[gate_idx]
    
    return RulerResult(
        cm=float(strokes),
        ruler_type="魯班尺（筆畫）",
        gate_name=gate["name"],
        jixiong=gate["jixiong"],
        meaning=gate["meaning"],
        advice=f"總筆畫{strokes}畫落在「{gate['name']}」門，{gate['meaning']}"
    )


# ============================================================
# 測試
# ============================================================
if __name__ == "__main__":
    print("=" * 60)
    print("         北斗命數 文公尺濾網 測試")
    print("=" * 60)
    
    # 1. 門寬測量
    print("\n【1. 門寬測量（魯班尺）】")
    for cm in [88, 90, 100, 106, 118]:
        result = measure_luban(cm)
        print(f"  {cm}cm → {result.gate_name}({result.jixiong}) {result.sub_gate}")
        print(f"         {result.sub_meaning}")
    
    # 2. 神位測量
    print("\n【2. 神位測量（丁蘭尺）】")
    for cm in [21, 25, 30, 35]:
        result = measure_dinglan(cm)
        print(f"  {cm}cm → {result.gate_name}({result.jixiong}) {result.meaning}")
    
    # 3. 尋找吉祥尺寸
    print("\n【3. 尋找吉祥門寬（目標90cm±5cm）】")
    good_sizes = find_good_size(90, "魯班", 5)
    for r in good_sizes[:4]:
        print(f"  {r.cm:.1f}cm → {r.gate_name}({r.jixiong}) {r.sub_gate}")
    
    # 4. 姓名筆畫
    print("\n【4. 姓名筆畫對應（魯班尺）】")
    for strokes in [24, 31, 32, 33]:
        result = stroke_to_luban(strokes)
        print(f"  {strokes}畫 → {result.gate_name}({result.jixiong}) {result.meaning}")
    
    print("\n" + "=" * 60)
    print("✅ 文公尺濾網測試完成！")
    print("=" * 60)
