"""
五行核心模組 wuxing_core.py v2.0 20260207
=========================================
北斗術數引擎共用基礎：天干地支、五行、十神、生剋關係
v2.0 新增：場論詮釋、白話翻譯

📚 知識點：
- 天干地支是中國曆法的基礎編碼系統（60甲子循環）
- 五行生剋是所有術數系統的底層邏輯
- 十神系統是八字分析的核心框架
- 場論統一詮釋：所有術數概念可用「場」的語言描述
"""

from typing import Dict, Optional, Tuple, List

# ===== 天干 =====
GAN = ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"]
GAN_WX = {"甲": "木", "乙": "木", "丙": "火", "丁": "火", "戊": "土",
           "己": "土", "庚": "金", "辛": "金", "壬": "水", "癸": "水"}
GAN_YY = {"甲": "陽", "乙": "陰", "丙": "陽", "丁": "陰", "戊": "陽",
           "己": "陰", "庚": "陽", "辛": "陰", "壬": "陽", "癸": "陰"}

# ===== 地支 =====
ZHI = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]
ZHI_WX = {"子": "水", "丑": "土", "寅": "木", "卯": "木", "辰": "土",
           "巳": "火", "午": "火", "未": "土", "申": "金", "酉": "金",
           "戌": "土", "亥": "水"}
ZHI_YY = {"子": "陽", "丑": "陰", "寅": "陽", "卯": "陰", "辰": "陽",
           "巳": "陰", "午": "陽", "未": "陰", "申": "陽", "酉": "陰",
           "戌": "陽", "亥": "陰"}

# 地支序數（梅花用，1起始）
ZHI_NUM = {z: i + 1 for i, z in enumerate(ZHI)}

# 生肖
ZODIAC = ["鼠", "牛", "虎", "兔", "龍", "蛇", "馬", "羊", "猴", "雞", "狗", "豬"]

# ===== 五行生剋 =====
WX_ORDER = ["木", "火", "土", "金", "水"]

# 五行生剋關係
WX_SHENG = {"木": "火", "火": "土", "土": "金", "金": "水", "水": "木"}
WX_KE = {"木": "土", "土": "水", "水": "火", "火": "金", "金": "木"}

# ===== v2.0 新增：五行場論詮釋 =====
WX_FIELD = {
    "木": {"場態": "成長擴張場", "特徵": "向上、創新、生機", "現代": "創意、成長、學習"},
    "火": {"場態": "外放發散場", "特徵": "熱情、表達、擴張", "現代": "表現、曝光、影響"},
    "土": {"場態": "穩定承載場", "特徵": "包容、穩定、務實", "現代": "執行、落地、累積"},
    "金": {"場態": "收斂規則場", "特徵": "果斷、收斂、規則", "現代": "決策、制度、效率"},
    "水": {"場態": "流動變通場", "特徵": "智慧、流動、變化", "現代": "策略、靈活、適應"},
}

# 五行關係場論
WX_RELATION_FIELD = {
    "相生": {
        "木生火": ("創意點燃熱情", "能量順流，B場增強"),
        "火生土": ("熱情沉澱成果", "表現轉化為累積"),
        "土生金": ("累積產生價值", "執行產出成果"),
        "金生水": ("規則產生流動", "制度催生靈活"),
        "水生木": ("智慧滋養創意", "策略支援成長"),
    },
    "反生": {
        "水多木漂": ("資源過多反害", "支援太多失去自主"),
        "木多火塞": ("創意太多動不了", "想法過載無法執行"),
        "火多土焦": ("表現過度傷根基", "曝光過頭反受害"),
        "土多金埋": ("執行太重限創新", "務實過度失靈活"),
        "金多水濁": ("制度太僵失活力", "規則過多阻流動"),
    },
    "相剋": {
        "木剋土": ("創新打破穩定", "變革衝擊既有"),
        "土剋水": ("執行限制策略", "穩定約束變化"),
        "水剋火": ("策略壓制衝動", "冷靜控制熱情"),
        "火剋金": ("熱情打破規則", "創意挑戰制度"),
        "金剋木": ("規則限制創新", "制度約束成長"),
    },
    "反剋": {
        "木堅金缺": ("創意太強制度崩", "變革過猛規則失效"),
        "金多火熄": ("制度太僵創新死", "規則壓制熱情"),
        "火多水乾": ("熱情過度理智失", "衝動壓過策略"),
        "水多土崩": ("變化太大組織垮", "流動過快根基失"),
        "土多木折": ("穩定過重創新壓", "既得利益阻變革"),
    },
}

# 地支藏干
ZHI_CANG = {
    "子": [("癸", "本")],
    "丑": [("己", "本"), ("癸", "中"), ("辛", "餘")],
    "寅": [("甲", "本"), ("丙", "中"), ("戊", "餘")],
    "卯": [("乙", "本")],
    "辰": [("戊", "本"), ("乙", "中"), ("癸", "餘")],
    "巳": [("丙", "本"), ("庚", "中"), ("戊", "餘")],
    "午": [("丁", "本"), ("己", "中")],
    "未": [("己", "本"), ("丁", "中"), ("乙", "餘")],
    "申": [("庚", "本"), ("壬", "中"), ("戊", "餘")],
    "酉": [("辛", "本")],
    "戌": [("戊", "本"), ("辛", "中"), ("丁", "餘")],
    "亥": [("壬", "本"), ("甲", "中")],
}

# 地支六合
ZHI_LIUHE = {
    ("子", "丑"): "土", ("寅", "亥"): "木", ("卯", "戌"): "火",
    ("辰", "酉"): "金", ("巳", "申"): "水", ("午", "未"): "火",
}

# 地支六沖
ZHI_LIUCHONG = [("子", "午"), ("丑", "未"), ("寅", "申"),
                ("卯", "酉"), ("辰", "戌"), ("巳", "亥")]


def wx_relation(a: str, b: str) -> str:
    """五行a對b的關係"""
    ia = WX_ORDER.index(a)
    ib = WX_ORDER.index(b)
    if ia == ib:
        return "比和"
    elif (ia + 1) % 5 == ib:
        return "我生"  # a生b
    elif (ia - 1) % 5 == ib:
        return "生我"  # b生a
    elif (ia + 2) % 5 == ib:
        return "我剋"  # a剋b
    else:
        return "剋我"  # b剋a


def wx_relation_field(a: str, b: str) -> Dict:
    """v2.0：五行關係的場論詮釋"""
    rel = wx_relation(a, b)
    result = {"wuxing_a": a, "wuxing_b": b, "relation": rel}
    
    if rel == "比和":
        result["field_effect"] = "同頻場"
        result["vernacular"] = "同類型能量，可共振可干涉"
        result["modern"] = "合作或競爭，取決於是否對齊"
    elif rel == "我生":
        key = f"{a}生{b}"
        if key in WX_RELATION_FIELD["相生"]:
            v, f = WX_RELATION_FIELD["相生"][key]
            result["field_effect"] = "順生場"
            result["vernacular"] = v
            result["modern"] = f
    elif rel == "生我":
        key = f"{b}生{a}"
        if key in WX_RELATION_FIELD["相生"]:
            v, f = WX_RELATION_FIELD["相生"][key]
            result["field_effect"] = "被生場"
            result["vernacular"] = f"被{v}"
            result["modern"] = "獲得支援和資源"
    elif rel == "我剋":
        key = f"{a}剋{b}"
        if key in WX_RELATION_FIELD["相剋"]:
            v, f = WX_RELATION_FIELD["相剋"][key]
            result["field_effect"] = "剋制場"
            result["vernacular"] = v
            result["modern"] = f
    elif rel == "剋我":
        key = f"{b}剋{a}"
        if key in WX_RELATION_FIELD["相剋"]:
            v, f = WX_RELATION_FIELD["相剋"][key]
            result["field_effect"] = "被剋場"
            result["vernacular"] = f"被{v}"
            result["modern"] = "受到約束或壓力"
    
    return result


def wx_sheng(a: str) -> str:
    """a所生的五行"""
    return WX_ORDER[(WX_ORDER.index(a) + 1) % 5]


def wx_ke(a: str) -> str:
    """a所剋的五行"""
    return WX_ORDER[(WX_ORDER.index(a) + 2) % 5]


# ===== 十神系統 =====
# v2.0：十神場論詮釋
SHISHEN_FIELD = {
    "比肩": {"relation": "同我者（陰陽同）", "field": "同頻共振場", "vernacular": "合作的夥伴", "modern": "同事、朋友、合作"},
    "劫財": {"relation": "同我者（陰陽異）", "field": "同頻干涉場", "vernacular": "競爭的對手", "modern": "競爭、消耗、搶奪"},
    "食神": {"relation": "我生者（陰陽同）", "field": "穩定輸出場", "vernacular": "穩定的才華", "modern": "創作、服務、產出"},
    "傷官": {"relation": "我生者（陰陽異）", "field": "爆發輸出場", "vernacular": "爆發的才華", "modern": "創意、批評、顛覆"},
    "偏財": {"relation": "我剋者（陰陽同）", "field": "機動掌控場", "vernacular": "機會財", "modern": "投資、獎金、意外收入"},
    "正財": {"relation": "我剋者（陰陽異）", "field": "穩定掌控場", "vernacular": "穩定收入", "modern": "薪水、存款、固定資產"},
    "七殺": {"relation": "剋我者（陰陽同）", "field": "衝擊約束場", "vernacular": "壓力和挑戰", "modern": "危機、競爭、壓迫"},
    "正官": {"relation": "剋我者（陰陽異）", "field": "穩定約束場", "vernacular": "合理的管束", "modern": "主管、制度、規則"},
    "偏印": {"relation": "生我者（陰陽同）", "field": "獨特支援場", "vernacular": "偏門的支援", "modern": "另類、偏技、非正統"},
    "正印": {"relation": "生我者（陰陽異）", "field": "穩定支援場", "vernacular": "有人教有人罩", "modern": "導師、貴人、資源"},
}


def ten_god(day_master: str, target: str) -> str:
    """
    計算十神
    day_master: 日主天干
    target: 目標天干
    返回: 十神名稱
    """
    dm_wx = GAN_WX[day_master]
    tg_wx = GAN_WX[target]
    dm_yy = GAN_YY[day_master]
    tg_yy = GAN_YY[target]
    same_yy = (dm_yy == tg_yy)
    
    rel = wx_relation(dm_wx, tg_wx)
    
    mapping = {
        ("比和", True): "比肩",
        ("比和", False): "劫財",
        ("生我", True): "偏印",
        ("生我", False): "正印",
        ("我生", True): "食神",
        ("我生", False): "傷官",
        ("我剋", True): "偏財",
        ("我剋", False): "正財",
        ("剋我", True): "七殺",
        ("剋我", False): "正官",
    }
    return mapping[(rel, same_yy)]


def ten_god_field(day_master: str, target: str) -> Dict:
    """v2.0：十神的場論詮釋"""
    god_name = ten_god(day_master, target)
    field_info = SHISHEN_FIELD.get(god_name, {})
    return {
        "god": god_name,
        "target": target,
        "target_wuxing": GAN_WX[target],
        **field_info
    }


# ===== 干支轉換工具 =====
def gz_index(gan_idx: int, zhi_idx: int) -> int:
    """天干索引+地支索引 → 60甲子序數(0-59)"""
    return (gan_idx * 6 + zhi_idx * 5) % 60


def gz_from_index(idx: int) -> tuple:
    """60甲子序數 → (天干索引, 地支索引)"""
    return idx % 10, idx % 12


def gz_str(gan_idx: int, zhi_idx: int) -> str:
    """干支索引 → 干支字串"""
    return f"{GAN[gan_idx]}{ZHI[zhi_idx]}"


def year_to_gz(year: int) -> tuple:
    """西曆年 → (天干索引, 地支索引)"""
    g = (year - 4) % 10
    z = (year - 4) % 12
    return g, z


def year_to_zodiac(year: int) -> str:
    """西曆年 → 生肖"""
    return ZODIAC[(year - 4) % 12]


def check_liuhe(z1: str, z2: str) -> str | None:
    """檢查地支六合，返回合化五行或None"""
    pair = tuple(sorted([z1, z2]))
    for (a, b), wx in ZHI_LIUHE.items():
        if pair == tuple(sorted([a, b])):
            return wx
    return None


def check_liuchong(z1: str, z2: str) -> bool:
    """檢查地支六沖"""
    pair = tuple(sorted([z1, z2]))
    return any(pair == tuple(sorted(p)) for p in ZHI_LIUCHONG)


if __name__ == "__main__":
    print("=== 五行核心模組 v2.0 測試 ===\n")
    
    # 五行場論
    print("【五行場論詮釋】")
    for wx, info in WX_FIELD.items():
        print(f"  {wx}：{info['場態']} — {info['現代']}")
    
    print("\n【五行關係場論】")
    print(wx_relation_field("木", "火"))
    print(wx_relation_field("金", "木"))
    
    # 十神場論
    print("\n【庚金日主 十神場論】")
    for g in GAN:
        info = ten_god_field("庚", g)
        print(f"  {g} → {info['god']}：{info.get('vernacular', '')} | {info.get('modern', '')}")
