"""
五行強弱分析器 wuxing_analyzer.py v1.0
======================================
XTF任務：消-E2 | 執行星：理樞（分析）

核心本質：強弱 = 得令 + 得地 + 得生 + 得助

📚 五行強弱判斷法則：
1. 得令（月令）：日主生於當令月份 +40分
2. 得地（地支藏干）：地支中有日主同五行 +10分/個
3. 得生（印星）：有生我的五行 +10分/個
4. 得助（比劫）：有同我的五行 +10分/個
5. 洩耗剋（減分）：食傷/財/官殺 各-5分/個

總分 > 50 為身強，< 50 為身弱
"""

from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum

# 月令五行對照（節氣為準）
MONTH_WUXING = {
    1: "土",   # 丑月（小寒-立春）
    2: "木",   # 寅月（立春-驚蟄）
    3: "木",   # 卯月（驚蟄-清明）
    4: "土",   # 辰月（清明-立夏）
    5: "火",   # 巳月（立夏-芒種）
    6: "火",   # 午月（芒種-小暑）
    7: "土",   # 未月（小暑-立秋）
    8: "金",   # 申月（立秋-白露）
    9: "金",   # 酉月（白露-寒露）
    10: "土",  # 戌月（寒露-立冬）
    11: "水",  # 亥月（立冬-大雪）
    12: "水",  # 子月（大雪-小寒）
}

# 月令旺相判斷（日主五行 vs 月令五行）
MONTH_STRENGTH = {
    # (日主五行, 月令五行): 得分
    # 當令（旺）
    ("木", "木"): 40, ("火", "火"): 40, ("土", "土"): 40, ("金", "金"): 40, ("水", "水"): 40,
    # 相（生我）
    ("木", "水"): 30, ("火", "木"): 30, ("土", "火"): 30, ("金", "土"): 30, ("水", "金"): 30,
    # 休（我生）
    ("木", "火"): 10, ("火", "土"): 10, ("土", "金"): 10, ("金", "水"): 10, ("水", "木"): 10,
    # 囚（剋我）
    ("木", "金"): 5, ("火", "水"): 5, ("土", "木"): 5, ("金", "火"): 5, ("水", "土"): 5,
    # 死（我剋）
    ("木", "土"): 0, ("火", "金"): 0, ("土", "水"): 0, ("金", "木"): 0, ("水", "火"): 0,
}

# 五行生剋
WX_SHENG = {"木": "火", "火": "土", "土": "金", "金": "水", "水": "木"}
WX_KE = {"木": "土", "土": "水", "水": "火", "火": "金", "金": "木"}
WX_SHENG_ME = {"木": "水", "火": "木", "土": "火", "金": "土", "水": "金"}  # 生我者
WX_KE_ME = {"木": "金", "火": "水", "土": "木", "金": "火", "水": "土"}  # 剋我者

# 天干五行
GAN_WX = {"甲": "木", "乙": "木", "丙": "火", "丁": "火", "戊": "土",
          "己": "土", "庚": "金", "辛": "金", "壬": "水", "癸": "水"}

# 地支五行
ZHI_WX = {"子": "水", "丑": "土", "寅": "木", "卯": "木", "辰": "土",
          "巳": "火", "午": "火", "未": "土", "申": "金", "酉": "金",
          "戌": "土", "亥": "水"}

# 地支藏干
ZHI_CANG = {
    "子": ["癸"],
    "丑": ["己", "癸", "辛"],
    "寅": ["甲", "丙", "戊"],
    "卯": ["乙"],
    "辰": ["戊", "乙", "癸"],
    "巳": ["丙", "庚", "戊"],
    "午": ["丁", "己"],
    "未": ["己", "丁", "乙"],
    "申": ["庚", "壬", "戊"],
    "酉": ["辛"],
    "戌": ["戊", "辛", "丁"],
    "亥": ["壬", "甲"],
}


@dataclass
class WuxingScore:
    """五行得分詳情"""
    total: int
    month_score: int  # 得令
    root_score: int   # 得地（通根）
    sheng_score: int  # 得生（印星）
    help_score: int   # 得助（比劫）
    drain_score: int  # 洩耗（食傷財官）
    is_strong: bool
    strength_level: str  # 極強/強/中和/弱/極弱
    analysis: str


class WuxingAnalyzer:
    """五行強弱分析器"""
    
    def __init__(self, day_master: str, pillars: Dict[str, str]):
        """
        day_master: 日主天干
        pillars: {"year": "甲子", "month": "丙寅", "day": "庚午", "hour": "壬申"}
        """
        self.day_master = day_master
        self.day_wx = GAN_WX[day_master]
        self.pillars = pillars
        
        # 解析四柱
        self.all_gan = [p[0] for p in pillars.values()]
        self.all_zhi = [p[1] for p in pillars.values()]
        self.month_zhi = pillars["month"][1]
    
    def analyze(self) -> WuxingScore:
        """執行五行強弱分析"""
        
        # 1. 得令（月令）
        month_wx = ZHI_WX[self.month_zhi]
        month_score = MONTH_STRENGTH.get((self.day_wx, month_wx), 10)
        
        # 2. 得地（通根）- 地支藏干中有日主同五行
        root_score = 0
        root_count = 0
        for zhi in self.all_zhi:
            for cang in ZHI_CANG.get(zhi, []):
                if GAN_WX[cang] == self.day_wx:
                    root_score += 10
                    root_count += 1
        
        # 3. 得生（印星）- 生我的五行
        sheng_me_wx = WX_SHENG_ME[self.day_wx]
        sheng_score = 0
        sheng_count = 0
        for gan in self.all_gan:
            if GAN_WX[gan] == sheng_me_wx:
                sheng_score += 10
                sheng_count += 1
        for zhi in self.all_zhi:
            if ZHI_WX[zhi] == sheng_me_wx:
                sheng_score += 5
                sheng_count += 1
        
        # 4. 得助（比劫）- 同我的五行（不含日主自己）
        help_score = 0
        help_count = 0
        for i, gan in enumerate(self.all_gan):
            if GAN_WX[gan] == self.day_wx and gan != self.day_master:
                help_score += 10
                help_count += 1
        for zhi in self.all_zhi:
            if ZHI_WX[zhi] == self.day_wx:
                help_score += 5
                help_count += 1
        
        # 5. 洩耗剋（減分）
        drain_score = 0
        wo_sheng_wx = WX_SHENG[self.day_wx]  # 食傷
        wo_ke_wx = WX_KE[self.day_wx]  # 財
        ke_me_wx = WX_KE_ME[self.day_wx]  # 官殺
        
        for gan in self.all_gan:
            if GAN_WX[gan] == wo_sheng_wx:  # 食傷
                drain_score += 5
            elif GAN_WX[gan] == wo_ke_wx:  # 財
                drain_score += 5
            elif GAN_WX[gan] == ke_me_wx:  # 官殺
                drain_score += 8
        
        for zhi in self.all_zhi:
            if ZHI_WX[zhi] == wo_sheng_wx:
                drain_score += 3
            elif ZHI_WX[zhi] == wo_ke_wx:
                drain_score += 3
            elif ZHI_WX[zhi] == ke_me_wx:
                drain_score += 5
        
        # 計算總分
        total = month_score + root_score + sheng_score + help_score - drain_score
        
        # 判斷強弱
        if total >= 70:
            is_strong = True
            strength_level = "極強"
        elif total >= 55:
            is_strong = True
            strength_level = "偏強"
        elif total >= 45:
            is_strong = False
            strength_level = "中和"
        elif total >= 30:
            is_strong = False
            strength_level = "偏弱"
        else:
            is_strong = False
            strength_level = "極弱"
        
        # 生成分析文字
        analysis = self._generate_analysis(
            month_score, root_score, sheng_score, help_score, drain_score,
            is_strong, strength_level
        )
        
        return WuxingScore(
            total=total,
            month_score=month_score,
            root_score=root_score,
            sheng_score=sheng_score,
            help_score=help_score,
            drain_score=drain_score,
            is_strong=is_strong,
            strength_level=strength_level,
            analysis=analysis,
        )
    
    def _generate_analysis(self, month, root, sheng, help_, drain, is_strong, level) -> str:
        """生成白話分析"""
        
        # 月令分析
        month_zhi_name = self.month_zhi
        month_wx = ZHI_WX[self.month_zhi]
        if month >= 40:
            month_text = f"生於{month_zhi_name}月（{month_wx}旺），當令得時，根基穩固"
        elif month >= 30:
            month_text = f"生於{month_zhi_name}月（{month_wx}相），得月令生扶"
        elif month >= 10:
            month_text = f"生於{month_zhi_name}月（{month_wx}），月令一般"
        else:
            month_text = f"生於{month_zhi_name}月（{month_wx}），月令不利，需要其他補強"
        
        # 通根分析
        if root >= 20:
            root_text = "地支通根多，根基深厚"
        elif root >= 10:
            root_text = "有通根，有基礎支撐"
        else:
            root_text = "通根少，根基較淺"
        
        # 印星分析
        if sheng >= 15:
            sheng_text = "印星多，有貴人相助，學習力強"
        elif sheng >= 10:
            sheng_text = "有印星，有人幫忙"
        else:
            sheng_text = "印星少，需要自己努力"
        
        # 比劫分析
        if help_ >= 15:
            help_text = "比劫多，有夥伴支援但要注意競爭"
        elif help_ >= 10:
            help_text = "有比劫，有同儕幫助"
        else:
            help_text = "比劫少，獨立性強但助力少"
        
        # 洩耗分析
        if drain >= 20:
            drain_text = "食傷財官多，輸出消耗大，容易累"
        elif drain >= 10:
            drain_text = "有洩耗，需要平衡輸出和休息"
        else:
            drain_text = "洩耗少，能量保存較好"
        
        # 綜合建議
        if is_strong:
            advice = "身強喜洩耗，適合創業、管理、表現才華。用神偏向食傷、財、官殺。"
        else:
            advice = "身弱喜生扶，需要貴人、資源、穩定環境。用神偏向印星、比劫。"
        
        return f"""【五行強弱分析】

日主：{self.day_master}（{self.day_wx}）
強弱：{level}（總分 {month + root + sheng + help_ - drain}）

得分明細：
• 月令：{month}分 — {month_text}
• 通根：{root}分 — {root_text}
• 印星：{sheng}分 — {sheng_text}
• 比劫：{help_}分 — {help_text}
• 洩耗：-{drain}分 — {drain_text}

【場論詮釋】
{self.day_wx}日主的能量場目前是「{level}」狀態。
{advice}

【現代建議】
{"你的能量充沛，適合主動出擊、承擔責任、發揮影響力。" if is_strong else "你需要更多支援和資源，適合穩紮穩打、借力使力、蓄積能量。"}
"""
    
    def get_yongshen(self) -> Dict[str, str]:
        """判斷用神（簡化版）"""
        score = self.analyze()
        
        if score.is_strong:
            # 身強喜洩耗
            return {
                "用神": WX_SHENG[self.day_wx],  # 食傷（洩秀）
                "喜神": WX_KE[self.day_wx],     # 財（消耗）
                "忌神": WX_SHENG_ME[self.day_wx],  # 印（再生扶就太旺）
                "仇神": self.day_wx,            # 比劫
                "建議": "適合輸出、創業、表現、花錢投資",
            }
        else:
            # 身弱喜生扶
            return {
                "用神": WX_SHENG_ME[self.day_wx],  # 印（生扶）
                "喜神": self.day_wx,               # 比劫（幫助）
                "忌神": WX_KE[self.day_wx],        # 財（消耗）
                "仇神": WX_KE_ME[self.day_wx],     # 官殺（壓力）
                "建議": "適合學習、找貴人、穩定發展、保守理財",
            }


def analyze_wuxing_strength(day_master: str, pillars: Dict[str, str]) -> Dict:
    """便捷函數：分析五行強弱"""
    analyzer = WuxingAnalyzer(day_master, pillars)
    score = analyzer.analyze()
    yongshen = analyzer.get_yongshen()
    
    return {
        "day_master": day_master,
        "day_wx": GAN_WX[day_master],
        "score": {
            "total": score.total,
            "month": score.month_score,
            "root": score.root_score,
            "sheng": score.sheng_score,
            "help": score.help_score,
            "drain": score.drain_score,
        },
        "is_strong": score.is_strong,
        "strength_level": score.strength_level,
        "yongshen": yongshen,
        "analysis": score.analysis,
    }


if __name__ == "__main__":
    # 測試：1973年12月30日酉時生（北斗）
    # 八字：癸丑/甲子/庚子/乙酉
    pillars = {
        "year": "癸丑",
        "month": "甲子",
        "day": "庚子",
        "hour": "乙酉",
    }
    
    result = analyze_wuxing_strength("庚", pillars)
    print(result["analysis"])
    print("\n【用神分析】")
    for k, v in result["yongshen"].items():
        print(f"  {k}：{v}")
