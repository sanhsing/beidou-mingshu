"""
八字流年分析器 liunian_analyzer.py v1.0
======================================
XTF任務：消-B2 | 執行星：理樞（分析）
確定度：★★★☆☆（吉凶判斷是經驗統計）

核心本質：流年 = 當年干支 × 命局配合

📚 流年分析法則：
1. 流年干支與日主的關係（十神）
2. 流年干支與命局的刑沖合害
3. 流年與大運的配合
4. 流年天干透出、地支入墓

⚠️ XTF8 認識論聲明：
- 流年干支計算：★★★★★（確定）
- 流年十神關係：★★★★☆（可推導）
- 流年吉凶傾向：★★★☆☆（經驗統計）
- 具體事件預測：★☆☆☆☆（高度不確定）
"""

from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from datetime import datetime

# 天干地支
GAN = ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"]
ZHI = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]

# 天干五行
GAN_WX = {"甲": "木", "乙": "木", "丙": "火", "丁": "火", "戊": "土",
          "己": "土", "庚": "金", "辛": "金", "壬": "水", "癸": "水"}

# 天干陰陽
GAN_YY = {"甲": "陽", "乙": "陰", "丙": "陽", "丁": "陰", "戊": "陽",
          "己": "陰", "庚": "陽", "辛": "陰", "壬": "陽", "癸": "陰"}

# 地支五行
ZHI_WX = {"子": "水", "丑": "土", "寅": "木", "卯": "木", "辰": "土",
          "巳": "火", "午": "火", "未": "土", "申": "金", "酉": "金",
          "戌": "土", "亥": "水"}

# 五行生剋
WX_SHENG = {"木": "火", "火": "土", "土": "金", "金": "水", "水": "木"}
WX_KE = {"木": "土", "土": "水", "水": "火", "火": "金", "金": "木"}

# 六合
LIUHE = {
    "子": "丑", "丑": "子", "寅": "亥", "亥": "寅",
    "卯": "戌", "戌": "卯", "辰": "酉", "酉": "辰",
    "巳": "申", "申": "巳", "午": "未", "未": "午",
}

# 六沖
LIUCHONG = {
    "子": "午", "午": "子", "丑": "未", "未": "丑",
    "寅": "申", "申": "寅", "卯": "酉", "酉": "卯",
    "辰": "戌", "戌": "辰", "巳": "亥", "亥": "巳",
}

# 三合局
SANHE = {
    "申子辰": "水", "寅午戌": "火", "巳酉丑": "金", "亥卯未": "木",
}

# 三刑
SANXING = {
    "寅": ["巳", "申"], "巳": ["寅", "申"], "申": ["寅", "巳"],  # 無恩之刑
    "丑": ["戌", "未"], "戌": ["丑", "未"], "未": ["丑", "戌"],  # 恃勢之刑
    "子": ["卯"], "卯": ["子"],  # 無禮之刑
    "辰": ["辰"], "午": ["午"], "酉": ["酉"], "亥": ["亥"],  # 自刑
}


def calc_shishen(day_master: str, target_gan: str) -> str:
    """計算十神"""
    WX_ORDER = ["木", "火", "土", "金", "水"]
    
    dm_wx = GAN_WX[day_master]
    tg_wx = GAN_WX[target_gan]
    dm_yy = GAN_YY[day_master]
    tg_yy = GAN_YY[target_gan]
    same_yy = (dm_yy == tg_yy)
    
    ia = WX_ORDER.index(dm_wx)
    ib = WX_ORDER.index(tg_wx)
    
    if ia == ib:
        rel = "比和"
    elif (ia + 1) % 5 == ib:
        rel = "我生"
    elif (ia - 1) % 5 == ib:
        rel = "生我"
    elif (ia + 2) % 5 == ib:
        rel = "我剋"
    else:
        rel = "剋我"
    
    mapping = {
        ("比和", True): "比肩", ("比和", False): "劫財",
        ("生我", True): "偏印", ("生我", False): "正印",
        ("我生", True): "食神", ("我生", False): "傷官",
        ("我剋", True): "偏財", ("我剋", False): "正財",
        ("剋我", True): "七殺", ("剋我", False): "正官",
    }
    return mapping[(rel, same_yy)]


def get_year_ganzhi(year: int) -> str:
    """取得年干支"""
    # 甲子年起算
    gan_idx = (year - 4) % 10
    zhi_idx = (year - 4) % 12
    return GAN[gan_idx] + ZHI[zhi_idx]


@dataclass
class LiunianAnalysis:
    """流年分析結果"""
    year: int
    ganzhi: str
    gan: str
    zhi: str
    gan_shishen: str      # 流年天干十神
    zhi_wx: str           # 流年地支五行
    interactions: List[str]  # 與命局的互動
    tendency: str         # 吉凶傾向
    advice: str           # 建議
    certainty: str        # 確定度


class LiunianAnalyzer:
    """流年分析器"""
    
    def __init__(self, day_master: str, pillars: Dict[str, str], is_strong: bool = True):
        """
        day_master: 日主天干
        pillars: 四柱 {"year": "甲子", "month": "丙寅", "day": "庚午", "hour": "壬申"}
        is_strong: 是否身強
        """
        self.day_master = day_master
        self.day_wx = GAN_WX[day_master]
        self.pillars = pillars
        self.is_strong = is_strong
        
        # 取得所有地支
        self.all_zhi = [p[1] for p in pillars.values()]
    
    def analyze_year(self, year: int) -> LiunianAnalysis:
        """分析特定流年"""
        ganzhi = get_year_ganzhi(year)
        gan = ganzhi[0]
        zhi = ganzhi[1]
        
        # 天干十神
        gan_shishen = calc_shishen(self.day_master, gan)
        
        # 地支五行
        zhi_wx = ZHI_WX[zhi]
        
        # 檢查與命局的互動
        interactions = []
        
        # 檢查六合
        for orig_zhi in self.all_zhi:
            if LIUHE.get(zhi) == orig_zhi:
                interactions.append(f"{zhi}與{orig_zhi}六合（和諧）")
        
        # 檢查六沖
        for orig_zhi in self.all_zhi:
            if LIUCHONG.get(zhi) == orig_zhi:
                interactions.append(f"{zhi}與{orig_zhi}相沖（變動）")
        
        # 檢查三刑
        xing_targets = SANXING.get(zhi, [])
        for orig_zhi in self.all_zhi:
            if orig_zhi in xing_targets:
                interactions.append(f"{zhi}與{orig_zhi}相刑（壓力）")
        
        # 判斷吉凶傾向
        tendency, advice, certainty = self._judge_tendency(gan_shishen, zhi_wx, interactions)
        
        return LiunianAnalysis(
            year=year,
            ganzhi=ganzhi,
            gan=gan,
            zhi=zhi,
            gan_shishen=gan_shishen,
            zhi_wx=zhi_wx,
            interactions=interactions,
            tendency=tendency,
            advice=advice,
            certainty=certainty,
        )
    
    def _judge_tendency(self, gan_shishen: str, zhi_wx: str, interactions: List[str]) -> Tuple[str, str, str]:
        """判斷吉凶傾向"""
        
        # 身強喜洩耗、身弱喜生扶
        shishen_tendency = {
            "比肩": ("平" if self.is_strong else "吉", "競爭合作"),
            "劫財": ("凶" if self.is_strong else "吉", "注意財務"),
            "食神": ("吉" if self.is_strong else "平", "才華發揮"),
            "傷官": ("吉" if self.is_strong else "凶", "創新但注意人際"),
            "偏財": ("吉" if self.is_strong else "凶", "投資機會"),
            "正財": ("吉" if self.is_strong else "凶", "穩定收入"),
            "七殺": ("凶" if not self.is_strong else "吉", "壓力挑戰"),
            "正官": ("平" if self.is_strong else "凶", "責任壓力"),
            "偏印": ("凶" if self.is_strong else "吉", "學習思考"),
            "正印": ("平" if self.is_strong else "吉", "貴人相助"),
        }
        
        base_tendency, base_advice = shishen_tendency.get(gan_shishen, ("平", ""))
        
        # 根據互動調整
        has_chong = any("相沖" in i for i in interactions)
        has_he = any("六合" in i for i in interactions)
        has_xing = any("相刑" in i for i in interactions)
        
        if has_chong:
            if base_tendency == "吉":
                tendency = "平"
            else:
                tendency = base_tendency
            advice = base_advice + "，變動較大"
        elif has_xing:
            if base_tendency == "吉":
                tendency = "平"
            else:
                tendency = "凶"
            advice = base_advice + "，有壓力挑戰"
        elif has_he:
            if base_tendency == "凶":
                tendency = "平"
            else:
                tendency = "吉"
            advice = base_advice + "，有貴人和諧"
        else:
            tendency = base_tendency
            advice = base_advice
        
        certainty = "★★★☆☆"  # 吉凶判斷是經驗統計
        
        return tendency, advice, certainty
    
    def analyze_years(self, start_year: int, num_years: int = 10) -> List[LiunianAnalysis]:
        """分析多年流年"""
        return [self.analyze_year(start_year + i) for i in range(num_years)]


def analyze_liunian(
    day_master: str,
    pillars: Dict[str, str],
    year: int,
    is_strong: bool = True,
) -> Dict:
    """便捷函數：分析流年"""
    analyzer = LiunianAnalyzer(day_master, pillars, is_strong)
    result = analyzer.analyze_year(year)
    
    return {
        "year": result.year,
        "ganzhi": result.ganzhi,
        "gan": result.gan,
        "zhi": result.zhi,
        "gan_shishen": result.gan_shishen,
        "zhi_wx": result.zhi_wx,
        "interactions": result.interactions,
        "tendency": result.tendency,
        "advice": result.advice,
        "certainty": result.certainty,
    }


def analyze_liunian_range(
    day_master: str,
    pillars: Dict[str, str],
    start_year: int,
    num_years: int = 10,
    is_strong: bool = True,
) -> List[Dict]:
    """便捷函數：分析多年流年"""
    analyzer = LiunianAnalyzer(day_master, pillars, is_strong)
    results = analyzer.analyze_years(start_year, num_years)
    
    return [
        {
            "year": r.year,
            "ganzhi": r.ganzhi,
            "gan_shishen": r.gan_shishen,
            "tendency": r.tendency,
            "advice": r.advice,
            "interactions": r.interactions,
        }
        for r in results
    ]


def generate_liunian_report(day_master: str, pillars: Dict[str, str], year: int, is_strong: bool = True) -> str:
    """生成流年報告"""
    result = analyze_liunian(day_master, pillars, year, is_strong)
    
    interactions_str = "、".join(result["interactions"]) if result["interactions"] else "無特殊互動"
    
    tendency_emoji = {"吉": "🟢", "平": "🟡", "凶": "🔴"}.get(result["tendency"], "⚪")
    
    report = f"""【{year}年流年分析】

流年干支：{result['ganzhi']}
流年天干十神：{result['gan_shishen']}
流年地支五行：{result['zhi_wx']}

與命局互動：{interactions_str}

整體傾向：{tendency_emoji} {result['tendency']}
建議：{result['advice']}

【XTF8 確定度標註】
{result['certainty']}（吉凶傾向是經驗統計，非決定性預測）

【場論詮釋】
流年是「年度能量背景」，影響該年的主要課題和機會。
{result['ganzhi']}年對你而言是「{result['gan_shishen']}」年，
代表這年的主題是：{result['advice']}

重要提醒：流年分析是「傾向性參考」，具體事件取決於個人行動。
"""
    
    return report


if __name__ == "__main__":
    # 測試：1973年12月30日男性（北斗）
    # 八字：癸丑/甲子/庚子/乙酉
    pillars = {
        "year": "癸丑",
        "month": "甲子",
        "day": "庚子",
        "hour": "乙酉",
    }
    
    # 分析2026年
    print(generate_liunian_report("庚", pillars, 2026, is_strong=False))
    
    # 分析未來5年
    print("\n【未來5年流年速覽】")
    for result in analyze_liunian_range("庚", pillars, 2026, 5, is_strong=False):
        emoji = {"吉": "🟢", "平": "🟡", "凶": "🔴"}.get(result["tendency"], "⚪")
        print(f"{result['year']}年 {result['ganzhi']}：{result['gan_shishen']} {emoji} {result['tendency']}")
