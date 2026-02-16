#!/usr/bin/env python3
"""
北斗命數 增強版命名引擎 v1.0
============================
真正配合八字喜用神的命名系統

特色：
1. 根據出生年月日時計算八字
2. 分析日主強弱
3. 確定喜用神
4. 篩選人格五行配合喜用神的名字

北斗七星文創 × 織明 | 2026-02-15
"""

from dataclasses import dataclass
from typing import List, Dict, Optional, Tuple
from lunar_calendar_v2 import get_bazi
from wuxing_core import GAN_WX, ZHI_WX, GAN

# 五行相生相剋
WX_SHENG = {"木": "火", "火": "土", "土": "金", "金": "水", "水": "木"}
WX_KE = {"木": "土", "土": "水", "水": "火", "火": "金", "金": "木"}
WX_SHENG_REV = {"火": "木", "土": "火", "金": "土", "水": "金", "木": "水"}  # 生我

# 筆畫五行
def stroke_to_wx(stroke: int) -> str:
    """筆畫轉五行（尾數法）"""
    last = stroke % 10
    if last in [1, 2]:
        return "木"
    elif last in [3, 4]:
        return "火"
    elif last in [5, 6]:
        return "土"
    elif last in [7, 8]:
        return "金"
    else:  # 9, 0
        return "水"

# 常用字庫（按五行分類）
CHARS_BY_WX = {
    "木": ["文", "華", "林", "森", "榮", "樹", "松", "柏", "楓", "棋", "藝", "芳", "蘭", "菊", "草", "青", "春", "東"],
    "火": ["明", "光", "輝", "燁", "炎", "照", "曉", "陽", "日", "星", "旭", "昌", "南", "夏", "紅", "丹", "彤", "靈"],
    "土": ["德", "坤", "培", "增", "城", "安", "宇", "宏", "堅", "穩", "中", "正", "和", "仁", "誠", "信", "義", "禮"],
    "金": ["鑫", "銘", "鋒", "銳", "錦", "鈺", "鐘", "金", "銀", "劍", "剛", "毅", "堅", "利", "正", "西", "秋", "白"],
    "水": ["海", "洋", "波", "濤", "江", "河", "湖", "澤", "泉", "清", "潔", "涵", "淳", "潤", "泓", "北", "冬", "雨"],
}

# 康熙筆畫
KANGXI = {
    "王": 4, "李": 7, "張": 11, "劉": 15, "陳": 16, "楊": 13, "黃": 12, "林": 8,
    "文": 4, "明": 8, "華": 14, "國": 11, "建": 9, "志": 7, "偉": 11, "強": 12,
    "海": 11, "波": 9, "龍": 16, "飛": 9, "天": 4, "星": 9, "光": 6, "輝": 15,
    "德": 15, "仁": 4, "義": 13, "智": 12, "信": 9, "忠": 8, "孝": 7, "勇": 9,
    "美": 9, "麗": 19, "芳": 10, "秀": 7, "英": 11, "蘭": 23, "梅": 11, "菊": 14,
    "玉": 5, "珍": 10, "珠": 11, "雅": 12, "靜": 16, "淑": 12, "婷": 12, "娟": 10,
    "敏": 11, "慧": 15, "穎": 16, "聰": 17, "睿": 14, "哲": 10, "思": 9, "博": 12,
    "林": 8, "森": 12, "松": 8, "柏": 9, "楓": 13, "榮": 14, "樹": 16, "東": 8,
    "春": 9, "夏": 10, "秋": 9, "冬": 5, "青": 8, "紅": 9, "藍": 20, "白": 5,
    "金": 8, "銀": 14, "鑫": 24, "銘": 14, "鋒": 15, "銳": 15, "錦": 16, "鐘": 17,
    "海": 11, "洋": 10, "江": 7, "河": 9, "湖": 13, "泉": 9, "清": 12, "涵": 12,
    "坤": 8, "培": 11, "城": 10, "安": 6, "宇": 6, "宏": 7, "堅": 11, "穩": 19,
    "三": 3, "興": 15, "小": 3, "大": 3, "中": 4, "正": 5, "永": 5, "長": 8,
    "嘉": 14, "佳": 8, "俊": 9, "傑": 12, "豪": 14, "傲": 13,
}


@dataclass
class BaziAnalysis:
    """八字分析結果"""
    bazi_str: str
    day_master: str
    day_master_wx: str
    wx_count: Dict[str, int]
    strength: str  # 身強/身弱
    need_wx: List[str]  # 喜用神五行
    avoid_wx: List[str]  # 忌神五行


@dataclass
class NameSuggestion:
    """命名建議"""
    name: str
    surname: str
    given_name: str
    tiange: int
    renge: int
    dige: int
    zongge: int
    sancai: str
    renge_wx: str
    score: float
    reason: str
    bazi_match: str  # 與八字配合說明


def analyze_bazi_for_naming(year: int, month: int, day: int, hour: int) -> BaziAnalysis:
    """分析八字，確定喜用神"""
    bazi = get_bazi(year, month, day, hour)
    
    # 日主
    day_gan = bazi['day'][0]
    day_wx = GAN_WX[day_gan]
    
    # 統計五行（天干+地支簡化）
    wx_count = {"木": 0, "火": 0, "土": 0, "金": 0, "水": 0}
    for pillar in [bazi['year'], bazi['month'], bazi['day'], bazi['hour']]:
        gan = pillar[0]
        wx_count[GAN_WX[gan]] += 1
    
    # 判斷強弱
    help_wx = WX_SHENG_REV[day_wx]  # 生我者
    strength_score = wx_count[day_wx] + wx_count[help_wx]
    
    if strength_score >= 3:
        strength = "身強"
        # 身強宜洩（我生）、剋（剋我）、耗（我剋）
        need_wx = [WX_SHENG[day_wx], WX_KE[day_wx]]  # 洩、耗
        avoid_wx = [day_wx, help_wx]  # 忌同類、生我
    else:
        strength = "身弱"
        # 身弱宜生（生我）、助（同類）
        need_wx = [help_wx, day_wx]
        avoid_wx = [WX_SHENG[day_wx], WX_KE[day_wx]]
    
    return BaziAnalysis(
        bazi_str=bazi['bazi_str'],
        day_master=day_gan,
        day_master_wx=day_wx,
        wx_count=wx_count,
        strength=strength,
        need_wx=need_wx,
        avoid_wx=avoid_wx
    )


def suggest_names_with_bazi(
    surname: str,
    year: int, month: int, day: int, hour: int,
    gender: str = "M",
    count: int = 10
) -> Tuple[BaziAnalysis, List[NameSuggestion]]:
    """
    根據八字喜用神推薦名字
    
    返回: (八字分析, 命名建議列表)
    """
    # 1. 分析八字
    bazi = analyze_bazi_for_naming(year, month, day, hour)
    
    # 2. 獲取姓氏筆畫
    s_strokes = KANGXI.get(surname, 10)
    
    # 3. 選擇喜用神五行的字
    good_chars = []
    for wx in bazi.need_wx:
        good_chars.extend(CHARS_BY_WX.get(wx, []))
    
    # 根據性別篩選
    if gender == "F":
        female_chars = ["美", "麗", "芳", "秀", "英", "蘭", "梅", "菊", "玉", "珍", 
                        "雅", "靜", "淑", "婷", "娟", "敏", "慧", "穎", "涵", "清"]
        good_chars = [c for c in good_chars if c in female_chars or c not in 
                     ["強", "剛", "毅", "勇", "龍", "虎", "豹", "鋒", "銳", "劍"]]
    
    # 4. 生成候選名字
    suggestions = []
    
    for char1 in good_chars[:15]:
        for char2 in good_chars[:15]:
            if char1 == char2:
                continue
            
            given_name = char1 + char2
            
            # 計算筆畫
            m1 = KANGXI.get(char1, 10)
            m2 = KANGXI.get(char2, 10)
            
            # 五格
            tiange = s_strokes + 1
            renge = s_strokes + m1
            dige = m1 + m2
            waige = tiange + dige - renge
            zongge = s_strokes + m1 + m2
            
            # 三才
            t_wx = stroke_to_wx(tiange)
            r_wx = stroke_to_wx(renge)
            d_wx = stroke_to_wx(dige)
            sancai = t_wx + r_wx + d_wx
            
            # 評分
            score = 60.0
            reasons = []
            bazi_match = ""
            
            # 人格五行配合喜用神
            if r_wx in bazi.need_wx:
                score += 20
                reasons.append(f"人格{r_wx}補{bazi.strength}")
                bazi_match = f"人格{r_wx}為喜用神"
            elif r_wx in bazi.avoid_wx:
                score -= 10
                bazi_match = f"人格{r_wx}為忌神"
            
            # 三才相生
            if WX_SHENG.get(t_wx) == r_wx:
                score += 10
                reasons.append("天生人")
            if WX_SHENG.get(r_wx) == d_wx:
                score += 10
                reasons.append("人生地")
            
            # 81數理吉凶（簡化）
            lucky_nums = [1, 3, 5, 6, 7, 8, 11, 13, 15, 16, 21, 23, 24, 25, 29, 31, 32, 33, 35, 37, 39, 41, 45, 47, 48]
            if renge in lucky_nums:
                score += 5
            if dige in lucky_nums:
                score += 5
            if zongge in lucky_nums:
                score += 5
            
            suggestions.append(NameSuggestion(
                name=surname + given_name,
                surname=surname,
                given_name=given_name,
                tiange=tiange,
                renge=renge,
                dige=dige,
                zongge=zongge,
                sancai=sancai,
                renge_wx=r_wx,
                score=score,
                reason=", ".join(reasons) if reasons else "五格平穩",
                bazi_match=bazi_match
            ))
    
    # 排序
    suggestions.sort(key=lambda x: -x.score)
    
    return bazi, suggestions[:count]


# ============ 測試 ============
if __name__ == "__main__":
    print("=" * 70)
    print("         北斗命數 八字配合命名 測試")
    print("=" * 70)
    
    # 案例1: 男孩
    print("\n【案例1: 男孩命名】")
    bazi, suggestions = suggest_names_with_bazi(
        surname="楊",
        year=1993, month=1, day=1, hour=5,
        gender="M",
        count=5
    )
    print(f"  出生: 1993年1月1日 5時")
    print(f"  八字: {bazi.bazi_str}")
    print(f"  日主: {bazi.day_master}({bazi.day_master_wx})")
    print(f"  身強弱: {bazi.strength}")
    print(f"  喜用神: {bazi.need_wx}")
    print(f"  忌神: {bazi.avoid_wx}")
    print(f"\n  命名建議:")
    for i, s in enumerate(suggestions):
        print(f"    {i+1}. {s.name:<8} 三才:{s.sancai} 人格{s.renge_wx} 評分:{s.score:.0f}")
        print(f"       {s.bazi_match} | {s.reason}")
    
    # 案例2: 女孩
    print("\n【案例2: 女孩命名】")
    bazi, suggestions = suggest_names_with_bazi(
        surname="林",
        year=1995, month=6, day=15, hour=9,
        gender="F",
        count=5
    )
    print(f"  出生: 1995年6月15日 9時")
    print(f"  八字: {bazi.bazi_str}")
    print(f"  日主: {bazi.day_master}({bazi.day_master_wx})")
    print(f"  身強弱: {bazi.strength}")
    print(f"  喜用神: {bazi.need_wx}")
    print(f"\n  命名建議:")
    for i, s in enumerate(suggestions):
        print(f"    {i+1}. {s.name:<8} 三才:{s.sancai} 人格{s.renge_wx} 評分:{s.score:.0f}")
        print(f"       {s.bazi_match} | {s.reason}")
    
    print("\n" + "=" * 70)
    print("✅ 八字配合命名測試完成！")
    print("=" * 70)
