"""
命盤比對引擎 chart_matching.py v1.0
==================================
XTF任務：消-D1 | 執行星：理樞（分析）
確定度：★★★☆☆（經驗統計為主）

核心本質：比對 = 雙人命盤 × 關係規則

📚 比對類型：
1. 合婚比對：夫妻宮位、日主配對
2. 親子比對：子女宮位、命格互動
3. 合作比對：官祿宮位、互補關係

⚠️ XTF8 認識論聲明：
- 天干地支關係：★★★★★（確定）
- 配對規則計算：★★★★☆（有公式）
- 吉凶傾向判斷：★★★☆☆（經驗統計）
- 關係預測：★★☆☆☆（僅供參考）
"""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

# 天干地支
GAN = ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"]
ZHI = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]

# 天干五行
GAN_WX = {"甲": "木", "乙": "木", "丙": "火", "丁": "火", "戊": "土",
          "己": "土", "庚": "金", "辛": "金", "壬": "水", "癸": "水"}

# 天干五合
GAN_HE = {"甲": "己", "己": "甲", "乙": "庚", "庚": "乙", "丙": "辛", "辛": "丙",
          "丁": "壬", "壬": "丁", "戊": "癸", "癸": "戊"}

# 天干相沖
GAN_CHONG = {"甲": "庚", "庚": "甲", "乙": "辛", "辛": "乙", "丙": "壬", "壬": "丙",
             "丁": "癸", "癸": "丁"}

# 地支六合
ZHI_LIUHE = {"子": "丑", "丑": "子", "寅": "亥", "亥": "寅", "卯": "戌", "戌": "卯",
             "辰": "酉", "酉": "辰", "巳": "申", "申": "巳", "午": "未", "未": "午"}

# 地支六沖
ZHI_LIUCHONG = {"子": "午", "午": "子", "丑": "未", "未": "丑", "寅": "申", "申": "寅",
                "卯": "酉", "酉": "卯", "辰": "戌", "戌": "辰", "巳": "亥", "亥": "巳"}

# 地支三合
ZHI_SANHE = {
    "申": ("子", "辰", "水"), "子": ("申", "辰", "水"), "辰": ("申", "子", "水"),
    "寅": ("午", "戌", "火"), "午": ("寅", "戌", "火"), "戌": ("寅", "午", "火"),
    "巳": ("酉", "丑", "金"), "酉": ("巳", "丑", "金"), "丑": ("巳", "酉", "金"),
    "亥": ("卯", "未", "木"), "卯": ("亥", "未", "木"), "未": ("亥", "卯", "木"),
}

# 地支相刑
ZHI_XING = {
    "寅": "巳", "巳": "申", "申": "寅",  # 無恩之刑
    "丑": "戌", "戌": "未", "未": "丑",  # 恃勢之刑
    "子": "卯", "卯": "子",  # 無禮之刑
}

# 五行生剋
WX_SHENG = {"木": "火", "火": "土", "土": "金", "金": "水", "水": "木"}
WX_KE = {"木": "土", "土": "水", "水": "火", "火": "金", "金": "木"}


class MatchType(Enum):
    """比對類型"""
    MARRIAGE = "合婚"
    PARENT_CHILD = "親子"
    COOPERATION = "合作"
    FRIENDSHIP = "友誼"


@dataclass
class PersonChart:
    """個人命盤資料"""
    name: str
    gender: str
    day_master: str  # 日主天干
    year_zhi: str    # 年支
    month_zhi: str   # 月支
    day_zhi: str     # 日支
    hour_zhi: str    # 時支
    # 紫微資料（可選）
    ming_stars: List[str] = None
    fuqi_stars: List[str] = None  # 夫妻宮星曜


@dataclass
class MatchFactor:
    """比對因素"""
    name: str           # 因素名稱
    score: int          # 得分（-10 到 +10）
    description: str    # 描述
    certainty: str      # 確定度


@dataclass
class MatchResult:
    """比對結果"""
    match_type: MatchType
    total_score: int
    max_score: int
    percentage: int
    grade: str  # A/B/C/D/E
    factors: List[MatchFactor]
    summary: str
    advice: List[str]


class ChartMatcher:
    """命盤比對器"""
    
    def __init__(self, person1: PersonChart, person2: PersonChart):
        self.p1 = person1
        self.p2 = person2
    
    def _check_gan_relation(self, gan1: str, gan2: str) -> Tuple[str, int]:
        """檢查天干關係"""
        if GAN_HE.get(gan1) == gan2:
            return "天干五合", 8
        if GAN_CHONG.get(gan1) == gan2:
            return "天干相沖", -5
        
        wx1, wx2 = GAN_WX.get(gan1, ""), GAN_WX.get(gan2, "")
        if wx1 == wx2:
            return "天干同五行", 3
        if WX_SHENG.get(wx1) == wx2 or WX_SHENG.get(wx2) == wx1:
            return "天干相生", 5
        if WX_KE.get(wx1) == wx2 or WX_KE.get(wx2) == wx1:
            return "天干相剋", -3
        
        return "天干無特殊關係", 0
    
    def _check_zhi_relation(self, zhi1: str, zhi2: str) -> Tuple[str, int]:
        """檢查地支關係"""
        if ZHI_LIUHE.get(zhi1) == zhi2:
            return "地支六合", 8
        if ZHI_LIUCHONG.get(zhi1) == zhi2:
            return "地支六沖", -6
        if ZHI_XING.get(zhi1) == zhi2:
            return "地支相刑", -4
        
        # 三合
        sanhe = ZHI_SANHE.get(zhi1)
        if sanhe and zhi2 in sanhe[:2]:
            return "地支三合", 6
        
        return "地支無特殊關係", 0
    
    def match_marriage(self) -> MatchResult:
        """合婚比對"""
        factors = []
        
        # 1. 日主五合
        rel, score = self._check_gan_relation(self.p1.day_master, self.p2.day_master)
        factors.append(MatchFactor(
            name="日主關係",
            score=score,
            description=f"{self.p1.day_master}與{self.p2.day_master} — {rel}",
            certainty="★★★★☆",
        ))
        
        # 2. 年支關係
        rel, score = self._check_zhi_relation(self.p1.year_zhi, self.p2.year_zhi)
        factors.append(MatchFactor(
            name="年支關係",
            score=score,
            description=f"{self.p1.year_zhi}與{self.p2.year_zhi} — {rel}",
            certainty="★★★★☆",
        ))
        
        # 3. 日支關係（夫妻宮）
        rel, score = self._check_zhi_relation(self.p1.day_zhi, self.p2.day_zhi)
        # 日支是夫妻宮，權重加倍
        score = int(score * 1.5)
        factors.append(MatchFactor(
            name="日支關係（夫妻宮）",
            score=score,
            description=f"{self.p1.day_zhi}與{self.p2.day_zhi} — {rel}",
            certainty="★★★★★",
        ))
        
        # 4. 月支關係
        rel, score = self._check_zhi_relation(self.p1.month_zhi, self.p2.month_zhi)
        factors.append(MatchFactor(
            name="月支關係",
            score=score,
            description=f"{self.p1.month_zhi}與{self.p2.month_zhi} — {rel}",
            certainty="★★★★☆",
        ))
        
        # 5. 性別互補（傳統觀點）
        if self.p1.gender != self.p2.gender:
            # 陰陽配對
            dm1_yy = "陽" if GAN.index(self.p1.day_master) % 2 == 0 else "陰"
            dm2_yy = "陽" if GAN.index(self.p2.day_master) % 2 == 0 else "陰"
            if dm1_yy != dm2_yy:
                factors.append(MatchFactor(
                    name="日主陰陽互補",
                    score=4,
                    description=f"{self.p1.day_master}({dm1_yy})與{self.p2.day_master}({dm2_yy}) — 陰陽調和",
                    certainty="★★★☆☆",
                ))
        
        return self._calculate_result(MatchType.MARRIAGE, factors)
    
    def match_parent_child(self) -> MatchResult:
        """親子比對"""
        factors = []
        
        # 1. 日主生剋關係
        wx1, wx2 = GAN_WX.get(self.p1.day_master, ""), GAN_WX.get(self.p2.day_master, "")
        if WX_SHENG.get(wx1) == wx2:
            factors.append(MatchFactor(
                name="父母生子女",
                score=7,
                description=f"{wx1}生{wx2} — 自然支持關係",
                certainty="★★★★☆",
            ))
        elif WX_SHENG.get(wx2) == wx1:
            factors.append(MatchFactor(
                name="子女生父母",
                score=5,
                description=f"{wx2}生{wx1} — 子女孝順",
                certainty="★★★★☆",
            ))
        elif WX_KE.get(wx1) == wx2:
            factors.append(MatchFactor(
                name="父母剋子女",
                score=-4,
                description=f"{wx1}剋{wx2} — 管教較嚴",
                certainty="★★★☆☆",
            ))
        elif WX_KE.get(wx2) == wx1:
            factors.append(MatchFactor(
                name="子女剋父母",
                score=-3,
                description=f"{wx2}剋{wx1} — 可能有衝突",
                certainty="★★★☆☆",
            ))
        else:
            factors.append(MatchFactor(
                name="五行關係",
                score=2,
                description=f"{wx1}與{wx2} — 普通關係",
                certainty="★★★☆☆",
            ))
        
        # 2. 年支關係
        rel, score = self._check_zhi_relation(self.p1.year_zhi, self.p2.year_zhi)
        factors.append(MatchFactor(
            name="年支關係",
            score=score,
            description=f"{self.p1.year_zhi}與{self.p2.year_zhi} — {rel}",
            certainty="★★★★☆",
        ))
        
        # 3. 時支與年支關係（子女宮與對方年）
        rel, score = self._check_zhi_relation(self.p1.hour_zhi, self.p2.year_zhi)
        factors.append(MatchFactor(
            name="時支與年支",
            score=score,
            description=f"子女宮{self.p1.hour_zhi}與{self.p2.year_zhi} — {rel}",
            certainty="★★★☆☆",
        ))
        
        return self._calculate_result(MatchType.PARENT_CHILD, factors)
    
    def match_cooperation(self) -> MatchResult:
        """合作比對"""
        factors = []
        
        # 1. 日主互補
        wx1, wx2 = GAN_WX.get(self.p1.day_master, ""), GAN_WX.get(self.p2.day_master, "")
        if WX_SHENG.get(wx1) == wx2 or WX_SHENG.get(wx2) == wx1:
            factors.append(MatchFactor(
                name="五行互補",
                score=6,
                description=f"{wx1}與{wx2}相生 — 能量流動順暢",
                certainty="★★★★☆",
            ))
        elif wx1 == wx2:
            factors.append(MatchFactor(
                name="五行同類",
                score=4,
                description=f"同為{wx1} — 理念相近",
                certainty="★★★★☆",
            ))
        
        # 2. 天干五合
        rel, score = self._check_gan_relation(self.p1.day_master, self.p2.day_master)
        if "五合" in rel:
            factors.append(MatchFactor(
                name="日主五合",
                score=score,
                description=f"{self.p1.day_master}與{self.p2.day_master}五合 — 合作默契好",
                certainty="★★★★☆",
            ))
        
        # 3. 年支關係
        rel, score = self._check_zhi_relation(self.p1.year_zhi, self.p2.year_zhi)
        factors.append(MatchFactor(
            name="年支關係",
            score=score,
            description=f"{self.p1.year_zhi}與{self.p2.year_zhi} — {rel}",
            certainty="★★★★☆",
        ))
        
        return self._calculate_result(MatchType.COOPERATION, factors)
    
    def _calculate_result(self, match_type: MatchType, factors: List[MatchFactor]) -> MatchResult:
        """計算結果"""
        total_score = sum(f.score for f in factors)
        max_score = len(factors) * 10
        
        # 正規化分數（0-100）
        normalized = int(((total_score + max_score) / (2 * max_score)) * 100)
        normalized = max(0, min(100, normalized))
        
        # 評級
        if normalized >= 80:
            grade = "A"
        elif normalized >= 65:
            grade = "B"
        elif normalized >= 50:
            grade = "C"
        elif normalized >= 35:
            grade = "D"
        else:
            grade = "E"
        
        # 總結
        if grade in ["A", "B"]:
            summary = f"{match_type.value}契合度高，有良好基礎"
        elif grade == "C":
            summary = f"{match_type.value}契合度中等，需要磨合"
        else:
            summary = f"{match_type.value}契合度較低，需要努力經營"
        
        # 建議
        advice = []
        for f in factors:
            if f.score >= 5:
                advice.append(f"✅ {f.name}良好：{f.description}")
            elif f.score <= -3:
                advice.append(f"⚠️ {f.name}需注意：{f.description}")
        
        return MatchResult(
            match_type=match_type,
            total_score=total_score,
            max_score=max_score,
            percentage=normalized,
            grade=grade,
            factors=factors,
            summary=summary,
            advice=advice,
        )


def match_charts(
    person1: Dict,
    person2: Dict,
    match_type: str = "marriage",
) -> Dict:
    """便捷函數：比對兩人命盤"""
    p1 = PersonChart(
        name=person1.get("name", "甲方"),
        gender=person1.get("gender", "男"),
        day_master=person1.get("day_master", ""),
        year_zhi=person1.get("year_zhi", ""),
        month_zhi=person1.get("month_zhi", ""),
        day_zhi=person1.get("day_zhi", ""),
        hour_zhi=person1.get("hour_zhi", ""),
    )
    
    p2 = PersonChart(
        name=person2.get("name", "乙方"),
        gender=person2.get("gender", "女"),
        day_master=person2.get("day_master", ""),
        year_zhi=person2.get("year_zhi", ""),
        month_zhi=person2.get("month_zhi", ""),
        day_zhi=person2.get("day_zhi", ""),
        hour_zhi=person2.get("hour_zhi", ""),
    )
    
    matcher = ChartMatcher(p1, p2)
    
    if match_type == "marriage":
        result = matcher.match_marriage()
    elif match_type == "parent_child":
        result = matcher.match_parent_child()
    elif match_type == "cooperation":
        result = matcher.match_cooperation()
    else:
        result = matcher.match_marriage()
    
    return {
        "match_type": result.match_type.value,
        "person1": person1.get("name", "甲方"),
        "person2": person2.get("name", "乙方"),
        "percentage": result.percentage,
        "grade": result.grade,
        "summary": result.summary,
        "factors": [
            {
                "name": f.name,
                "score": f.score,
                "description": f.description,
                "certainty": f.certainty,
            }
            for f in result.factors
        ],
        "advice": result.advice,
    }


def generate_match_report(result: Dict) -> str:
    """生成比對報告"""
    emoji_grade = {"A": "🌟🌟🌟🌟🌟", "B": "🌟🌟🌟🌟", "C": "🌟🌟🌟", "D": "🌟🌟", "E": "🌟"}
    
    report = f"""
╔══════════════════════════════════════════════════════════════════╗
║  命盤比對分析 | {result['match_type']}                                    ║
╚══════════════════════════════════════════════════════════════════╝

【比對雙方】
甲方：{result['person1']}
乙方：{result['person2']}

【契合度評分】
分數：{result['percentage']}分
等級：{result['grade']} {emoji_grade.get(result['grade'], '')}
評語：{result['summary']}

【分析因素】
"""
    
    for f in result['factors']:
        emoji = "🟢" if f['score'] > 0 else ("🔴" if f['score'] < 0 else "⚪")
        report += f"  {emoji} {f['name']}：{f['description']}（{f['certainty']}）\n"
    
    report += "\n【建議】\n"
    for advice in result['advice']:
        report += f"  {advice}\n"
    
    report += """
【XTF8 確定度標註】
★★★★★ 天干地支關係（確定）
★★★★☆ 配對規則計算（有公式）
★★★☆☆ 吉凶傾向判斷（經驗統計）
★★☆☆☆ 關係預測（僅供參考）

重要提醒：命盤比對是「參考工具」，不是「關係判決」。
好的關係需要雙方用心經營，與命盤無直接因果關係。
"""
    
    return report


if __name__ == "__main__":
    # 測試：合婚比對
    person1 = {
        "name": "北斗",
        "gender": "男",
        "day_master": "庚",
        "year_zhi": "丑",
        "month_zhi": "子",
        "day_zhi": "子",
        "hour_zhi": "酉",
    }
    
    person2 = {
        "name": "測試",
        "gender": "女",
        "day_master": "乙",
        "year_zhi": "未",
        "month_zhi": "午",
        "day_zhi": "卯",
        "hour_zhi": "巳",
    }
    
    result = match_charts(person1, person2, "marriage")
    print(generate_match_report(result))
