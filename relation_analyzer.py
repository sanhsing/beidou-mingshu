#!/usr/bin/env python3
"""
relation_analyzer.py - 十神×六親關係分析引擎
北斗命數 v3.1 商業版

PYLIB: L2-relation-analyzer
Version: v1.0.0
Created: 2026-02-17

功能：
1. 十神關係場分析（以日主為中心）
2. 六親對應解析
3. 關係互動建議
4. 雙盤匹配分析

場論模型：
  人 = 先天能量場 × 後天選擇場 × 關係交互場

@織明 × @理樞
"""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass

# ============================================================
# L0: 十神×六親對照表
# ============================================================

# 十神定義
SHISHEN_MAP = {
    "比肩": {
        "code": "bijian",
        "liuqin": ["朋友", "競爭者", "同行", "兄弟姐妹"],
        "field": "同場競爭場",
        "nature": "同類",
        "traits": ["平等", "競爭", "合作", "觀點衝突"],
        "strength": ["團隊協作", "資源共享", "相互激勵"],
        "risk": ["標準壓制", "利益衝突", "主導權爭奪"],
        "advice": "採用共創模式，避免標準壓制"
    },
    "劫財": {
        "code": "jiecai",
        "liuqin": ["朋友", "競爭者", "同行"],
        "field": "爭奪消耗場",
        "nature": "同類",
        "traits": ["強勢", "爭奪", "消耗", "行動力強"],
        "strength": ["執行力", "果斷", "突破阻礙"],
        "risk": ["過度競爭", "消耗資源", "人際衝突"],
        "advice": "控制競爭慾，轉為合作動能"
    },
    "食神": {
        "code": "shishen",
        "liuqin": ["子女", "學生", "晚輩", "輸出對象"],
        "field": "溫和輸出場",
        "nature": "我生",
        "traits": ["創造", "表達", "享受", "溫和"],
        "strength": ["創造力", "表達能力", "藝術天分"],
        "risk": ["過度享樂", "缺乏進取", "懶散"],
        "advice": "保持輸出節奏，享受但不放縱"
    },
    "傷官": {
        "code": "shangguan",
        "liuqin": ["子女", "學生", "晚輩", "表達能力"],
        "field": "衝擊輸出場",
        "nature": "我生",
        "traits": ["批判", "顛覆", "創新", "銳利"],
        "strength": ["創造力強", "表達銳利", "打破框架"],
        "risk": ["言語過直", "破壞關係", "樹敵"],
        "advice": "鋒利不必尖銳，輸出要留餘地"
    },
    "正財": {
        "code": "zhengcai",
        "liuqin": ["妻子（男命）", "資源", "穩定收入", "客戶"],
        "field": "穩定掌控場",
        "nature": "我剋",
        "traits": ["務實", "穩定", "累積", "保守"],
        "strength": ["理財能力", "穩定收入", "務實態度"],
        "risk": ["過於保守", "缺乏冒險", "視野受限"],
        "advice": "穩中求進，給對方成長空間"
    },
    "偏財": {
        "code": "piancai",
        "liuqin": ["父親", "情人", "意外之財", "投資"],
        "field": "流動資源場",
        "nature": "我剋",
        "traits": ["靈活", "投機", "交際", "慷慨"],
        "strength": ["人緣好", "財運流動", "交際能力"],
        "risk": ["財來財去", "不穩定", "過度消費"],
        "advice": "把握機會但控制風險"
    },
    "正官": {
        "code": "zhengguan",
        "liuqin": ["丈夫（女命）", "上司", "制度", "正統權威"],
        "field": "規則約束場",
        "nature": "剋我",
        "traits": ["規矩", "責任", "約束", "正統"],
        "strength": ["自律", "責任感", "受人尊重"],
        "risk": ["過於拘謹", "壓力大", "缺乏彈性"],
        "advice": "借勢而行，不硬碰硬"
    },
    "七殺": {
        "code": "qisha",
        "liuqin": ["小人", "競爭對手", "壓力來源", "挑戰者"],
        "field": "壓力挑戰場",
        "nature": "剋我",
        "traits": ["壓力", "挑戰", "攻擊", "突破"],
        "strength": ["抗壓能力", "突破困境", "危機處理"],
        "risk": ["壓力過大", "人際衝突", "身心俱疲"],
        "advice": "化敵為友，壓力轉為動力"
    },
    "正印": {
        "code": "zhengyin",
        "liuqin": ["母親", "長輩", "貴人", "保護者"],
        "field": "滋養保護場",
        "nature": "生我",
        "traits": ["保護", "滋養", "學習", "傳承"],
        "strength": ["有貴人", "學習能力", "受保護"],
        "risk": ["過度依賴", "缺乏獨立", "停滯"],
        "advice": "接受滋養但保持獨立"
    },
    "偏印": {
        "code": "pianyin",
        "liuqin": ["繼母", "偏門貴人", "特殊技能"],
        "field": "偏門滋養場",
        "nature": "生我",
        "traits": ["孤獨", "特立", "偏門", "冷門"],
        "strength": ["獨特思維", "特殊技能", "另闢蹊徑"],
        "risk": ["孤僻", "不合群", "鑽牛角尖"],
        "advice": "發揮獨特性，但保持連結"
    }
}

# 十神計算（日主為基準）
SHISHEN_CALC = {
    # (日主, 他干) -> 十神
    ("甲", "甲"): "比肩", ("甲", "乙"): "劫財", ("甲", "丙"): "食神", ("甲", "丁"): "傷官",
    ("甲", "戊"): "偏財", ("甲", "己"): "正財", ("甲", "庚"): "七殺", ("甲", "辛"): "正官",
    ("甲", "壬"): "偏印", ("甲", "癸"): "正印",
    
    ("乙", "乙"): "比肩", ("乙", "甲"): "劫財", ("乙", "丁"): "食神", ("乙", "丙"): "傷官",
    ("乙", "己"): "偏財", ("乙", "戊"): "正財", ("乙", "辛"): "七殺", ("乙", "庚"): "正官",
    ("乙", "癸"): "偏印", ("乙", "壬"): "正印",
    
    ("丙", "丙"): "比肩", ("丙", "丁"): "劫財", ("丙", "戊"): "食神", ("丙", "己"): "傷官",
    ("丙", "庚"): "偏財", ("丙", "辛"): "正財", ("丙", "壬"): "七殺", ("丙", "癸"): "正官",
    ("丙", "甲"): "偏印", ("丙", "乙"): "正印",
    
    ("丁", "丁"): "比肩", ("丁", "丙"): "劫財", ("丁", "己"): "食神", ("丁", "戊"): "傷官",
    ("丁", "辛"): "偏財", ("丁", "庚"): "正財", ("丁", "癸"): "七殺", ("丁", "壬"): "正官",
    ("丁", "乙"): "偏印", ("丁", "甲"): "正印",
    
    ("戊", "戊"): "比肩", ("戊", "己"): "劫財", ("戊", "庚"): "食神", ("戊", "辛"): "傷官",
    ("戊", "壬"): "偏財", ("戊", "癸"): "正財", ("戊", "甲"): "七殺", ("戊", "乙"): "正官",
    ("戊", "丙"): "偏印", ("戊", "丁"): "正印",
    
    ("己", "己"): "比肩", ("己", "戊"): "劫財", ("己", "辛"): "食神", ("己", "庚"): "傷官",
    ("己", "癸"): "偏財", ("己", "壬"): "正財", ("己", "乙"): "七殺", ("己", "甲"): "正官",
    ("己", "丁"): "偏印", ("己", "丙"): "正印",
    
    ("庚", "庚"): "比肩", ("庚", "辛"): "劫財", ("庚", "壬"): "食神", ("庚", "癸"): "傷官",
    ("庚", "甲"): "偏財", ("庚", "乙"): "正財", ("庚", "丙"): "七殺", ("庚", "丁"): "正官",
    ("庚", "戊"): "偏印", ("庚", "己"): "正印",
    
    ("辛", "辛"): "比肩", ("辛", "庚"): "劫財", ("辛", "癸"): "食神", ("辛", "壬"): "傷官",
    ("辛", "乙"): "偏財", ("辛", "甲"): "正財", ("辛", "丁"): "七殺", ("辛", "丙"): "正官",
    ("辛", "己"): "偏印", ("辛", "戊"): "正印",
    
    ("壬", "壬"): "比肩", ("壬", "癸"): "劫財", ("壬", "甲"): "食神", ("壬", "乙"): "傷官",
    ("壬", "丙"): "偏財", ("壬", "丁"): "正財", ("壬", "戊"): "七殺", ("壬", "己"): "正官",
    ("壬", "庚"): "偏印", ("壬", "辛"): "正印",
    
    ("癸", "癸"): "比肩", ("癸", "壬"): "劫財", ("癸", "乙"): "食神", ("癸", "甲"): "傷官",
    ("癸", "丁"): "偏財", ("癸", "丙"): "正財", ("癸", "己"): "七殺", ("癸", "戊"): "正官",
    ("癸", "辛"): "偏印", ("癸", "庚"): "正印",
}

# ============================================================
# L1: 資料結構
# ============================================================

@dataclass
class RelationAnalysis:
    """關係分析結果"""
    shishen: str          # 十神
    liuqin: List[str]     # 六親對應
    field: str            # 場論詮釋
    nature: str           # 本質（同類/我生/我剋/剋我/生我）
    traits: List[str]     # 特徵
    strength: List[str]   # 優勢
    risk: List[str]       # 風險
    advice: str           # 調整建議

@dataclass
class RelationMatch:
    """雙盤匹配結果"""
    my_daymaster: str
    other_daymaster: str
    i_to_other: str       # 我對對方的十神
    other_to_me: str      # 對方對我的十神
    compatibility: str    # 相容度
    interaction: str      # 互動模式
    advice: str           # 建議

# ============================================================
# L2: 核心函數
# ============================================================

def get_shishen(day_master: str, other_gan: str) -> str:
    """計算十神"""
    return SHISHEN_CALC.get((day_master, other_gan), "未知")

def get_shishen_info(shishen: str) -> Dict:
    """取得十神詳細資訊"""
    return SHISHEN_MAP.get(shishen, {})

def analyze_relation(day_master: str, other_gan: str) -> RelationAnalysis:
    """分析關係"""
    shishen = get_shishen(day_master, other_gan)
    info = get_shishen_info(shishen)
    
    if not info:
        return RelationAnalysis(
            shishen=shishen,
            liuqin=["未知"],
            field="未知場",
            nature="未知",
            traits=[],
            strength=[],
            risk=[],
            advice="無法分析"
        )
    
    return RelationAnalysis(
        shishen=shishen,
        liuqin=info.get("liuqin", []),
        field=info.get("field", ""),
        nature=info.get("nature", ""),
        traits=info.get("traits", []),
        strength=info.get("strength", []),
        risk=info.get("risk", []),
        advice=info.get("advice", "")
    )

def analyze_all_relations(day_master: str, pillars: Dict) -> List[Dict]:
    """分析四柱所有關係"""
    results = []
    
    pillar_names = {"year": "年柱", "month": "月柱", "day": "日柱", "hour": "時柱"}
    
    for pillar_key, pillar_val in pillars.items():
        if not pillar_val or len(pillar_val) < 1:
            continue
        
        gan = pillar_val[0]
        if gan == day_master and pillar_key == "day":
            continue  # 跳過日干本身
        
        rel = analyze_relation(day_master, gan)
        results.append({
            "pillar": pillar_names.get(pillar_key, pillar_key),
            "gan": gan,
            "shishen": rel.shishen,
            "field": rel.field,
            "nature": rel.nature,
            "liuqin": rel.liuqin,
            "advice": rel.advice,
        })
    
    return results

def match_two_charts(my_daymaster: str, other_daymaster: str) -> RelationMatch:
    """雙盤匹配分析"""
    i_to_other = get_shishen(my_daymaster, other_daymaster)
    other_to_me = get_shishen(other_daymaster, my_daymaster)
    
    # 相容度評估
    compatibility_rules = {
        ("食神", "正印"): ("高", "滋養關係"),
        ("傷官", "正印"): ("中", "創造與保護"),
        ("正財", "比肩"): ("中", "付出與平等"),
        ("正官", "傷官"): ("低", "約束與反叛"),
        ("七殺", "比肩"): ("低", "壓力與競爭"),
        ("比肩", "比肩"): ("中", "平等競爭"),
        ("正印", "食神"): ("高", "保護與創造"),
    }
    
    # 簡化匹配
    compat, interaction = compatibility_rules.get(
        (i_to_other, other_to_me), 
        ("中", "一般互動")
    )
    
    # 生成建議
    i_info = get_shishen_info(i_to_other)
    o_info = get_shishen_info(other_to_me)
    
    advice = f"你對對方是「{i_to_other}」場（{i_info.get('nature', '')}），"
    advice += f"對方對你是「{other_to_me}」場（{o_info.get('nature', '')}）。"
    
    if i_info.get("nature") == "我生":
        advice += "你會付出較多，注意平衡。"
    elif i_info.get("nature") == "剋我":
        advice += "對方可能帶來壓力，學會借勢。"
    elif i_info.get("nature") == "生我":
        advice += "對方會支持你，珍惜但保持獨立。"
    
    return RelationMatch(
        my_daymaster=my_daymaster,
        other_daymaster=other_daymaster,
        i_to_other=i_to_other,
        other_to_me=other_to_me,
        compatibility=compat,
        interaction=interaction,
        advice=advice
    )

# ============================================================
# L3: 關係建議生成
# ============================================================

def generate_relation_advice(day_master: str, pillars: Dict, gender: str = "M") -> Dict:
    """生成完整關係建議"""
    relations = analyze_all_relations(day_master, pillars)
    
    # 統計十神分布
    shishen_count = {}
    for rel in relations:
        ss = rel["shishen"]
        shishen_count[ss] = shishen_count.get(ss, 0) + 1
    
    # 找出主要十神
    main_shishen = max(shishen_count.items(), key=lambda x: x[1])[0] if shishen_count else None
    
    # 生成建議
    advice_sections = {
        "relations": relations,
        "main_shishen": main_shishen,
        "shishen_count": shishen_count,
        "summary": "",
        "adjustment": [],
    }
    
    # 根據主要十神生成總結
    if main_shishen:
        info = get_shishen_info(main_shishen)
        advice_sections["summary"] = f"你的關係場以「{main_shishen}」為主，"
        advice_sections["summary"] += f"傾向於{info.get('field', '')}。"
        advice_sections["summary"] += f"優勢在於{'、'.join(info.get('strength', [])[:2])}，"
        advice_sections["summary"] += f"需注意{'、'.join(info.get('risk', [])[:2])}。"
    
    # 具體調整建議
    advice_sections["adjustment"] = [
        "輸出前多 0.5 秒停頓，減少衝擊",
        "問句多於結論，把「我認為」改為「你怎麼看？」",
        "給對方成長空間，不用自己的節奏要求他人",
        "遇強勢權威，不對抗，改為結構重組",
    ]
    
    return advice_sections

# ============================================================
# 測試
# ============================================================

if __name__ == "__main__":
    print("=== 關係分析測試 ===\n")
    
    # 測試：庚金日主
    day_master = "庚"
    pillars = {
        "year": "癸丑",
        "month": "癸丑",
        "day": "庚子",
        "hour": "乙酉"
    }
    
    print(f"日主：{day_master}\n")
    
    # 分析所有關係
    relations = analyze_all_relations(day_master, pillars)
    for rel in relations:
        print(f"{rel['pillar']} {rel['gan']}：{rel['shishen']}（{rel['field']}）")
        print(f"  六親：{', '.join(rel['liuqin'][:2])}")
        print(f"  建議：{rel['advice']}\n")
    
    # 雙盤匹配
    print("=== 雙盤匹配測試 ===")
    match = match_two_charts("庚", "乙")
    print(f"我({match.my_daymaster}) → 對方({match.other_daymaster}): {match.i_to_other}")
    print(f"對方 → 我: {match.other_to_me}")
    print(f"相容度: {match.compatibility}")
    print(f"建議: {match.advice}")
