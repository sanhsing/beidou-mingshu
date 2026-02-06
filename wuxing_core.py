"""
五行核心模組 wuxing_core.py v1.0 20260206
=========================================
北斗術數引擎共用基礎：天干地支、五行、十神、生剋關係

📚 知識點：
- 天干地支是中國曆法的基礎編碼系統（60甲子循環）
- 五行生剋是所有術數系統的底層邏輯
- 十神系統是八字分析的核心框架
"""

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


def wx_sheng(a: str) -> str:
    """a所生的五行"""
    return WX_ORDER[(WX_ORDER.index(a) + 1) % 5]


def wx_ke(a: str) -> str:
    """a所剋的五行"""
    return WX_ORDER[(WX_ORDER.index(a) + 2) % 5]


# ===== 十神系統 =====
def ten_god(day_master: str, target: str) -> str:
    """
    計算十神
    day_master: 日主天干
    target: 目標天干
    返回: 十神名稱
    
    📚 十神邏輯：
    同我 → 同陰陽=比肩, 異陰陽=劫財
    生我 → 同陰陽=偏印, 異陰陽=正印
    我生 → 同陰陽=食神, 異陰陽=傷官
    我剋 → 同陰陽=偏財, 異陰陽=正財
    剋我 → 同陰陽=七殺, 異陰陽=正官
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
    # 驗證：庚金日主的十神
    print("庚金日主 十神表：")
    for g in GAN:
        print(f"  {g}({GAN_WX[g]}) → {ten_god('庚', g)}")
    
    print(f"\n2026年 = {gz_str(*year_to_gz(2026))}年 {year_to_zodiac(2026)}")
