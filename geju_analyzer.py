"""
八字格局判斷器 geju_analyzer.py v1.0
====================================
XTF任務：消-E1 | 執行星：理樞（分析）

核心本質：格局 = 月令透干 + 日主強弱 + 配合情況

📚 格局判斷法則：
1. 月令定格：看月令藏干透出天干為何
2. 日主強弱：身強身弱影響格局喜忌
3. 成格條件：有無破格因素
"""

from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from wuxing_analyzer import WuxingAnalyzer, GAN_WX, ZHI_CANG, ZHI_WX

# 十神計算
def calc_shishen(day_master: str, target: str) -> str:
    """計算十神"""
    GAN_YY = {"甲": "陽", "乙": "陰", "丙": "陽", "丁": "陰", "戊": "陽",
              "己": "陰", "庚": "陽", "辛": "陰", "壬": "陽", "癸": "陰"}
    
    WX_ORDER = ["木", "火", "土", "金", "水"]
    dm_wx = GAN_WX[day_master]
    tg_wx = GAN_WX[target]
    dm_yy = GAN_YY[day_master]
    tg_yy = GAN_YY[target]
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


# 格局定義
GEJU_INFO = {
    "正官格": {
        "shishen": "正官",
        "condition": "月令正官透出",
        "vernacular": "走正規路線",
        "field": "穩定約束場",
        "suitable": "體制內發展",
        "modern": "公務員、大企業主管、專業經理人",
        "strong_advice": "身強官輕，可以承擔更多責任，適合往管理層發展",
        "weak_advice": "身弱官重，壓力大，需要貴人扶持，宜穩中求進",
    },
    "七殺格": {
        "shishen": "七殺",
        "condition": "月令七殺透出",
        "vernacular": "壓力轉動力",
        "field": "衝擊挑戰場",
        "suitable": "創業競爭",
        "modern": "創業者、軍人、運動員、業務高手",
        "strong_advice": "身強殺有力，敢拼敢衝，適合開創性工作",
        "weak_advice": "身弱殺重，壓力極大，需要印星化殺，找好導師",
    },
    "正印格": {
        "shishen": "正印",
        "condition": "月令正印透出",
        "vernacular": "有人教有靠山",
        "field": "穩定支援場",
        "suitable": "學術幕僚",
        "modern": "學者、顧問、幕僚、老師",
        "strong_advice": "身強印多，學識豐富但要注意實踐，別光說不練",
        "weak_advice": "身弱有印，有貴人相助，適合靠知識吃飯",
    },
    "偏印格": {
        "shishen": "偏印",
        "condition": "月令偏印透出",
        "vernacular": "走非主流路線",
        "field": "獨特輸入場",
        "suitable": "技術偏門",
        "modern": "技術專家、另類療法、小眾領域、研發",
        "strong_advice": "身強偏印，獨特才能可以發揮，但要找到市場",
        "weak_advice": "身弱偏印，可能思慮過多，需要行動力",
    },
    "正財格": {
        "shishen": "正財",
        "condition": "月令正財透出",
        "vernacular": "穩穩賺錢",
        "field": "穩定掌控場",
        "suitable": "財務經營",
        "modern": "會計、財務、中小企業主、投資理財",
        "strong_advice": "身強財旺，能承擔財務責任，適合經商",
        "weak_advice": "身弱財多，錢難守住，需要學習理財，找人合作",
    },
    "偏財格": {
        "shishen": "偏財",
        "condition": "月令偏財透出",
        "vernacular": "抓機會投資",
        "field": "機動掌控場",
        "suitable": "投資業務",
        "modern": "投資人、業務、仲介、創業家",
        "strong_advice": "身強偏財，財路寬廣，適合投資創業",
        "weak_advice": "身弱偏財，機會多但難把握，需要團隊支援",
    },
    "食神格": {
        "shishen": "食神",
        "condition": "月令食神透出",
        "vernacular": "才華穩定輸出",
        "field": "穩定輸出場",
        "suitable": "創作服務",
        "modern": "廚師、作家、設計師、藝術家",
        "strong_advice": "身強食神，才華洋溢，適合創作和表現",
        "weak_advice": "身弱食神，輸出消耗大，需要休息充電",
    },
    "傷官格": {
        "shishen": "傷官",
        "condition": "月令傷官透出",
        "vernacular": "才華衝擊框架",
        "field": "衝擊輸出場",
        "suitable": "創新批評",
        "modern": "創新者、評論家、創業者、改革派",
        "strong_advice": "身強傷官，才華爆發力強，適合創新但要注意人際",
        "weak_advice": "身弱傷官，消耗過大，需要收斂鋒芒",
    },
    "建祿格": {
        "shishen": "比肩",
        "condition": "月令為日主祿地",
        "vernacular": "自力更生型",
        "field": "自主獨立場",
        "suitable": "獨立發展",
        "modern": "自由業、獨立工作者、專業人士",
        "strong_advice": "建祿身強，獨立性強，適合自己闖",
        "weak_advice": "建祿身弱，雖有根基但需要外力支援",
    },
    "月刃格": {
        "shishen": "劫財",
        "condition": "月令為日主刃地",
        "vernacular": "競爭搶奪型",
        "field": "競爭干涉場",
        "suitable": "競爭領域",
        "modern": "業務、競技、金融交易",
        "strong_advice": "月刃身強，競爭力強但要注意合作",
        "weak_advice": "月刃身弱，有競爭壓力，需要學會借力",
    },
}

# 特殊格局
SPECIAL_GEJU = {
    "從財格": {
        "condition": "身極弱，財星極旺，無印比生扶",
        "vernacular": "完全依附財運",
        "advice": "跟著錢走，適合在大公司或富人身邊發展",
    },
    "從官格": {
        "condition": "身極弱，官殺極旺，無印比生扶",
        "vernacular": "完全順從體制",
        "advice": "聽從安排，適合在大組織中服務",
    },
    "從兒格": {
        "condition": "身極弱，食傷極旺，無印比生扶",
        "vernacular": "完全輸出才華",
        "advice": "靠才華吃飯，適合藝術創作領域",
    },
    "專旺格": {
        "condition": "身極強，比劫成群，無財官食傷",
        "vernacular": "一往無前型",
        "advice": "需要洩秀，適合創業或領導",
    },
}

# 祿刃位置
GAN_LU = {"甲": "寅", "乙": "卯", "丙": "巳", "丁": "午", "戊": "巳",
          "己": "午", "庚": "申", "辛": "酉", "壬": "亥", "癸": "子"}
GAN_REN = {"甲": "卯", "乙": "寅", "丙": "午", "丁": "巳", "戊": "午",
           "己": "巳", "庚": "酉", "辛": "申", "壬": "子", "癸": "亥"}


@dataclass
class GejuResult:
    """格局分析結果"""
    geju_name: str
    geju_info: Dict
    is_strong: bool
    strength_level: str
    month_shishen: str
    advice: str
    detailed_analysis: str


class GejuAnalyzer:
    """八字格局分析器"""
    
    def __init__(self, day_master: str, pillars: Dict[str, str]):
        self.day_master = day_master
        self.pillars = pillars
        self.month_gan = pillars["month"][0]
        self.month_zhi = pillars["month"][1]
        
        # 取得所有天干
        self.all_gan = [p[0] for p in pillars.values()]
        
        # 計算身強弱
        analyzer = WuxingAnalyzer(day_master, pillars)
        self.strength_result = analyzer.analyze()
        self.is_strong = self.strength_result.is_strong
        self.strength_level = self.strength_result.strength_level
    
    def analyze(self) -> GejuResult:
        """分析格局"""
        
        # 1. 找月令藏干
        month_cang = ZHI_CANG.get(self.month_zhi, [])
        
        # 2. 看月干是什麼十神
        month_gan_shishen = calc_shishen(self.day_master, self.month_gan)
        
        # 3. 看月支藏干有沒有透出天干
        transparent_shishen = []
        for cang in month_cang:
            for gan in self.all_gan:
                if gan == cang:
                    ss = calc_shishen(self.day_master, gan)
                    transparent_shishen.append(ss)
        
        # 4. 判斷格局
        # 優先看透干
        geju_name = None
        
        # 先檢查建祿格和月刃格
        if self.month_zhi == GAN_LU.get(self.day_master):
            geju_name = "建祿格"
        elif self.month_zhi == GAN_REN.get(self.day_master):
            geju_name = "月刃格"
        
        # 再看透干格局
        if not geju_name:
            for ss in transparent_shishen:
                for name, info in GEJU_INFO.items():
                    if info["shishen"] == ss and name not in ["建祿格", "月刃格"]:
                        geju_name = name
                        break
                if geju_name:
                    break
        
        # 如果都沒有，用月干十神定格
        if not geju_name:
            for name, info in GEJU_INFO.items():
                if info["shishen"] == month_gan_shishen:
                    geju_name = name
                    break
        
        # 如果還是沒有，給個預設
        if not geju_name:
            geju_name = "雜氣格"
        
        # 取得格局資訊
        geju_info = GEJU_INFO.get(geju_name, {
            "vernacular": "混合型",
            "field": "複合場",
            "suitable": "多元發展",
            "modern": "需要綜合判斷",
            "strong_advice": "根據具體情況發展",
            "weak_advice": "根據具體情況發展",
        })
        
        # 生成建議
        if self.is_strong:
            advice = geju_info.get("strong_advice", "")
        else:
            advice = geju_info.get("weak_advice", "")
        
        # 詳細分析
        detailed = self._generate_detailed_analysis(geju_name, geju_info, month_gan_shishen)
        
        return GejuResult(
            geju_name=geju_name,
            geju_info=geju_info,
            is_strong=self.is_strong,
            strength_level=self.strength_level,
            month_shishen=month_gan_shishen,
            advice=advice,
            detailed_analysis=detailed,
        )
    
    def _generate_detailed_analysis(self, geju_name: str, geju_info: Dict, month_ss: str) -> str:
        """生成詳細分析"""
        
        return f"""【八字格局分析】

格局：{geju_name}
月干十神：{month_ss}
身強弱：{self.strength_level}（{"身強" if self.is_strong else "身弱"}）

【格局解讀】
• 白話：{geju_info.get('vernacular', '')}
• 場論：{geju_info.get('field', '')}
• 適合：{geju_info.get('suitable', '')}
• 現代：{geju_info.get('modern', '')}

【針對你的建議】
{self.strength_level}的{geju_name}：
{geju_info.get('strong_advice' if self.is_strong else 'weak_advice', '')}

【場論詮釋】
格局是八字能量的主要表現形式。
{geju_name}代表你的能量場傾向於「{geju_info.get('field', '')}」模式。
配合{self.strength_level}的日主，你的人生主題是：{geju_info.get('vernacular', '')}。

【職業建議】
適合方向：{geju_info.get('modern', '')}
"""


def analyze_geju(day_master: str, pillars: Dict[str, str]) -> Dict:
    """便捷函數：分析格局"""
    analyzer = GejuAnalyzer(day_master, pillars)
    result = analyzer.analyze()
    
    return {
        "geju_name": result.geju_name,
        "geju_info": result.geju_info,
        "is_strong": result.is_strong,
        "strength_level": result.strength_level,
        "month_shishen": result.month_shishen,
        "advice": result.advice,
        "detailed_analysis": result.detailed_analysis,
    }


if __name__ == "__main__":
    # 測試：1973年12月30日酉時生（北斗）
    pillars = {
        "year": "癸丑",
        "month": "甲子",
        "day": "庚子",
        "hour": "乙酉",
    }
    
    result = analyze_geju("庚", pillars)
    print(result["detailed_analysis"])
