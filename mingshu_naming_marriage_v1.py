#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
mingshu_naming_marriage_v1.py - 北斗命數姓名+命名+嫁娶 v1.0
============================================================
北斗七星文創 × 織明

XTF⁸ 任務鏈：M10+M11+M12
執行星：織明(設計) × 理樞(計算) × 澄韻(文案) × 流祇(連結)

模組整合：
    M10: NameEngine         - 姓名學 (三才五格+新生兒命名+改名)
    M11: CompanyNameEngine  - 公司行號命名 (行業五行+筆畫吉凶)
    M12: MarriageZeriEngine - 嫁娶擇時 (合婚分析+吉日篩選)

📚 知識點：
    「姓名 = 後天場的文字錨點」
    「命名 = 為場選擇最佳符號」
    「嫁娶 = 兩場合一的最佳時機」
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple, Any
from enum import Enum
from datetime import datetime, date, timedelta
import json

# 導入本地模組
try:
    from mingshu_engine_v1 import (
        MingshuEngine, BirthInfo, BaziChart, Gender, CalendarType,
        TIANGAN, DIZHI, WUXING, TIANGAN_WUXING, DIZHI_WUXING
    )
    from mingshu_liunian_hepan_v1 import HepanEngine
except ImportError:
    TIANGAN = ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"]
    DIZHI = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]
    WUXING = ["木", "火", "土", "金", "水"]
    TIANGAN_WUXING = {
        "甲": "木", "乙": "木", "丙": "火", "丁": "火", "戊": "土",
        "己": "土", "庚": "金", "辛": "金", "壬": "水", "癸": "水"
    }


# =============================================================================
# 康熙字典筆畫庫 (常用字)
# =============================================================================

KANGXI_STROKES = {
    # 常用姓氏
    "王": 4, "李": 7, "張": 11, "劉": 15, "陳": 16, "楊": 13, "黃": 12, "趙": 14,
    "吳": 7, "周": 8, "徐": 10, "孫": 10, "朱": 6, "馬": 10, "胡": 11, "郭": 15,
    "林": 8, "何": 7, "高": 10, "羅": 20, "鄭": 19, "梁": 11, "謝": 17, "宋": 7,
    "唐": 10, "許": 11, "韓": 17, "馮": 12, "鄧": 19, "曹": 11, "彭": 12, "曾": 12,
    "蕭": 18, "田": 5, "董": 15, "袁": 10, "潘": 16, "蔡": 17, "蔣": 17, "余": 7,
    "杜": 7, "葉": 15, "程": 12, "魏": 18, "蘇": 22, "呂": 7, "丁": 2, "任": 6,
    "沈": 8, "姚": 9, "盧": 16, "姜": 9, "崔": 11, "鍾": 17, "譚": 19, "陸": 16,
    "汪": 8, "范": 11, "金": 8, "石": 5, "廖": 14, "賈": 13, "夏": 10, "韋": 9,
    "傅": 12, "方": 4, "白": 5, "鄒": 17, "孟": 8, "熊": 14, "秦": 10, "邱": 12,
    "江": 7, "尹": 4, "薛": 19, "閻": 16, "段": 9, "雷": 13, "侯": 9, "龍": 16,
    "史": 5, "陶": 16, "黎": 15, "賀": 12, "顧": 21, "毛": 4, "郝": 14, "龔": 22,
    "邵": 12, "萬": 15, "錢": 16, "嚴": 20, "覃": 12, "武": 8, "戴": 18, "莫": 13,
    "孔": 4, "向": 6, "湯": 13, "康": 11, "易": 8, "常": 11, "喬": 12, "賴": 16,
    "文": 4, "施": 9, "洪": 10, "季": 8,
    
    # 常用名字用字
    "一": 1, "二": 2, "三": 3, "四": 4, "五": 5, "六": 6, "七": 7, "八": 8, "九": 9, "十": 10,
    "子": 3, "文": 4, "明": 8, "華": 14, "國": 11, "建": 9, "志": 7, "偉": 11, "強": 12, "軍": 9,
    "平": 5, "東": 8, "海": 11, "波": 9, "成": 7, "龍": 16, "雲": 12, "飛": 9, "天": 4, "星": 9,
    "光": 6, "輝": 15, "德": 15, "仁": 4, "義": 13, "禮": 18, "智": 12, "信": 9, "忠": 8, "孝": 7,
    "勇": 9, "剛": 10, "毅": 15, "堅": 11, "健": 11, "康": 11, "寧": 14, "安": 6, "福": 14, "祥": 11,
    "慶": 15, "榮": 14, "昌": 8, "盛": 12, "興": 15, "旺": 8, "達": 16, "通": 14, "順": 12, "利": 7,
    "美": 9, "麗": 19, "芳": 10, "秀": 7, "英": 11, "蘭": 23, "梅": 11, "菊": 14, "蓮": 17, "荷": 13,
    "玉": 5, "珍": 10, "珠": 11, "寶": 20, "貴": 12, "雅": 12, "靜": 16, "淑": 12, "婷": 12, "娟": 10,
    "敏": 11, "慧": 15, "穎": 16, "聰": 17, "睿": 14, "哲": 10, "思": 9, "雨": 8, "雪": 11, "霜": 17,
    "風": 9, "雷": 13, "電": 13, "霞": 17, "虹": 9, "露": 20, "曉": 16, "晨": 11, "旭": 6, "陽": 17,
    "月": 4, "日": 4, "春": 9, "夏": 10, "秋": 9, "冬": 5, "青": 8, "紅": 9, "黃": 12, "藍": 20,
    "白": 5, "黑": 12, "金": 8, "銀": 14, "鐵": 21, "銅": 14, "玲": 10, "瓏": 21, "琳": 13, "琪": 13,
    "琴": 13, "棋": 12, "書": 10, "畫": 12, "詩": 13, "詞": 12, "歌": 14, "舞": 14, "藝": 21, "術": 11,
    "學": 16, "博": 12, "士": 3, "碩": 14, "研": 11, "究": 7, "科": 9, "技": 8, "工": 3, "程": 12,
    "永": 5, "恆": 10, "久": 3, "長": 8, "遠": 17, "近": 11, "大": 3, "小": 3, "中": 4, "正": 5,
    "新": 13, "舊": 18, "古": 5, "今": 4, "來": 8, "去": 5, "上": 3, "下": 3, "左": 5, "右": 5,
    "前": 9, "後": 9, "內": 4, "外": 5, "高": 10, "低": 7, "深": 12, "淺": 12, "寬": 15, "窄": 10,
    "家": 10, "園": 13, "庭": 10, "院": 15, "堂": 11, "樓": 15, "閣": 14, "亭": 9, "台": 14, "榭": 14,
    "山": 3, "水": 4, "河": 9, "湖": 13, "江": 7, "海": 11, "洋": 10, "川": 3, "溪": 14, "泉": 9,
    "林": 8, "森": 12, "木": 4, "樹": 16, "花": 10, "草": 12, "竹": 6, "松": 8, "柏": 9, "楓": 13,
    "鳥": 11, "魚": 11, "蟲": 18, "獸": 19, "龍": 16, "鳳": 14, "虎": 8, "豹": 10, "獅": 13, "象": 12,
    "馬": 10, "牛": 4, "羊": 6, "豬": 16, "狗": 9, "雞": 18, "鴨": 16, "鵝": 18, "兔": 8, "鼠": 13,
    "心": 4, "愛": 13, "情": 12, "感": 13, "恩": 10, "惠": 12, "慈": 14, "善": 12, "好": 6, "樂": 15,
    "喜": 12, "怒": 9, "哀": 9, "懼": 22, "憂": 15, "愁": 13, "悲": 12, "歡": 22, "笑": 10, "哭": 10,
    "嘉": 14, "佳": 8, "俊": 9, "傑": 12, "豪": 14, "傲": 13, "驕": 22, "謙": 17, "虛": 12, "實": 14,
}

# 筆畫吉凶表
STROKE_FORTUNE = {
    1: ("大吉", "太極之數，萬物開泰"),
    2: ("凶", "混沌未開，進退保守"),
    3: ("大吉", "三才俱全，萬事亨通"),
    5: ("大吉", "福祿長壽，富貴榮華"),
    6: ("大吉", "六合之數，天德地祥"),
    7: ("吉", "獨立權威，剛毅果斷"),
    8: ("吉", "堅剛意志，進取富貴"),
    11: ("大吉", "草木逢春，萬事順利"),
    13: ("大吉", "智謀超群，博學多才"),
    15: ("大吉", "福壽雙全，圓滿之數"),
    16: ("大吉", "厚德載物，安富尊榮"),
    21: ("大吉", "光風霽月，獨立權威"),
    23: ("大吉", "旭日東升，功名顯達"),
    24: ("大吉", "財源廣進，白手成家"),
    25: ("吉", "資性英敏，剛毅果斷"),
    29: ("吉", "財力歸集，名聞天下"),
    31: ("大吉", "智勇雙全，可享清福"),
    32: ("大吉", "寶馬金鞍，僥倖多望"),
    33: ("大吉", "旭日昇天，鸞鳳相會"),
    35: ("吉", "溫和平靜，智達通暢"),
    37: ("吉", "權威顯達，吉祥發達"),
    39: ("吉", "富貴榮華，財帛豐盈"),
    41: ("大吉", "德望高大，事事如意"),
    45: ("吉", "順風揚帆，新生泰運"),
    47: ("吉", "花開之象，萬事如意"),
    48: ("吉", "德智兼備，顯祖揚名"),
    # 凶數
    4: ("凶", "四象之數，破敗衰亡"),
    9: ("凶", "破舟入海，吉凶難分"),
    10: ("凶", "萬事終局，回顧茫然"),
    12: ("凶", "薄弱無力，謀事難成"),
    14: ("凶", "破兆離散，家庭緣薄"),
    19: ("凶", "智高路險，多難短命"),
    20: ("凶", "非業破運，厄難迭來"),
    22: ("凶", "中年多難，離祖別親"),
    26: ("凶", "變怪奇異，英雄色厄"),
    27: ("半吉", "欲望無止，自我矛盾"),
    28: ("凶", "家親緣薄，離群索居"),
    30: ("半吉", "吉凶參半，投機取巧"),
    34: ("凶", "破家之兆，見識短淺"),
    36: ("凶", "波瀾萬丈，俠義之氣"),
    40: ("半吉", "智謀奪取，浮沉不定"),
    42: ("半吉", "寒蟬在柳，十藝九窮"),
    43: ("凶", "散財破產，見識短淺"),
    44: ("凶", "煩悶困苦，難遂心願"),
    46: ("凶", "波瀾起伏，困苦艱難"),
    49: ("半吉", "吉凶難分，轉禍為福"),
    50: ("半吉", "吉凶互見，一成一敗"),
}


# =============================================================================
# M10: 姓名學引擎
# =============================================================================

@dataclass
class WugeResult:
    """五格結果"""
    tiange: int           # 天格
    renge: int            # 人格
    dige: int             # 地格
    waige: int            # 外格
    zongge: int           # 總格
    tiange_wx: str        # 天格五行
    renge_wx: str         # 人格五行
    dige_wx: str          # 地格五行
    sancai: str           # 三才配置
    sancai_fortune: str   # 三才吉凶
    
    def to_dict(self) -> Dict:
        return {
            "tiange": {"value": self.tiange, "wuxing": self.tiange_wx},
            "renge": {"value": self.renge, "wuxing": self.renge_wx},
            "dige": {"value": self.dige, "wuxing": self.dige_wx},
            "waige": {"value": self.waige},
            "zongge": {"value": self.zongge},
            "sancai": self.sancai,
            "sancai_fortune": self.sancai_fortune
        }


@dataclass
class NameAnalysis:
    """姓名分析結果"""
    surname: str
    given_name: str
    full_name: str
    strokes: List[int]
    total_strokes: int
    wuge: WugeResult
    fortune_summary: str
    wuxing_analysis: str
    bazi_match: Optional[str] = None
    score: float = 0.0
    suggestions: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict:
        return {
            "full_name": self.full_name,
            "surname": self.surname,
            "given_name": self.given_name,
            "strokes": self.strokes,
            "total_strokes": self.total_strokes,
            "wuge": self.wuge.to_dict(),
            "fortune_summary": self.fortune_summary,
            "wuxing_analysis": self.wuxing_analysis,
            "bazi_match": self.bazi_match,
            "score": round(self.score, 1),
            "suggestions": self.suggestions
        }


@dataclass
class NameSuggestion:
    """命名建議"""
    name: str
    strokes: List[int]
    score: float
    wuge: WugeResult
    reason: str
    
    def to_dict(self) -> Dict:
        return {
            "name": self.name,
            "strokes": self.strokes,
            "score": round(self.score, 1),
            "wuge": self.wuge.to_dict(),
            "reason": self.reason
        }


class NameEngine:
    """
    姓名學引擎
    
    M10: 三才五格 + 新生兒命名 + 改名分析
    
    📚 知識點：
        姓名 = 後天場的文字錨點
        三才 = 天人地 = 父母/自己/子女
        五格 = 天格/人格/地格/外格/總格
    """
    
    VERSION = "1.0.0"
    
    def __init__(self):
        self.strokes_db = KANGXI_STROKES.copy()
        try:
            self.engine = MingshuEngine()
        except:
            self.engine = None
    
    def get_strokes(self, char: str) -> int:
        """獲取康熙字典筆畫"""
        if char in self.strokes_db:
            return self.strokes_db[char]
        # 未知字假設為10畫
        return 10
    
    def num_to_wuxing(self, n: int) -> str:
        """數字尾數轉五行"""
        d = n % 10
        if d in [1, 2]:
            return "木"
        elif d in [3, 4]:
            return "火"
        elif d in [5, 6]:
            return "土"
        elif d in [7, 8]:
            return "金"
        else:
            return "水"
    
    def calc_wuge(self, surname: str, given_name: str) -> WugeResult:
        """
        計算五格
        
        📚 知識點：
            單姓雙名: 天=姓+1, 人=姓+名1, 地=名1+名2, 外=總-人+1, 總=全部
        """
        # 獲取筆畫
        s_strokes = [self.get_strokes(c) for c in surname]
        g_strokes = [self.get_strokes(c) for c in given_name]
        
        s_total = sum(s_strokes)
        g_total = sum(g_strokes)
        total = s_total + g_total
        
        # 五格計算
        if len(surname) == 1:
            # 單姓
            tiange = s_total + 1
            if len(given_name) >= 1:
                renge = s_total + g_strokes[0]
            else:
                renge = s_total + 1
            if len(given_name) >= 2:
                dige = g_strokes[0] + g_strokes[1]
            elif len(given_name) == 1:
                dige = g_strokes[0] + 1
            else:
                dige = 2
        else:
            # 複姓
            tiange = s_strokes[0] + s_strokes[1]
            if len(given_name) >= 1:
                renge = s_strokes[-1] + g_strokes[0]
            else:
                renge = s_strokes[-1] + 1
            if len(given_name) >= 2:
                dige = g_strokes[0] + g_strokes[1]
            elif len(given_name) == 1:
                dige = g_strokes[0] + 1
            else:
                dige = 2
        
        zongge = total
        waige = zongge - renge + 1
        if waige <= 0:
            waige = 1
        
        # 五行
        tiange_wx = self.num_to_wuxing(tiange)
        renge_wx = self.num_to_wuxing(renge)
        dige_wx = self.num_to_wuxing(dige)
        
        # 三才
        sancai = f"{tiange_wx}{renge_wx}{dige_wx}"
        sancai_fortune = self._judge_sancai(tiange_wx, renge_wx, dige_wx)
        
        return WugeResult(
            tiange=tiange,
            renge=renge,
            dige=dige,
            waige=waige,
            zongge=zongge,
            tiange_wx=tiange_wx,
            renge_wx=renge_wx,
            dige_wx=dige_wx,
            sancai=sancai,
            sancai_fortune=sancai_fortune
        )
    
    def _judge_sancai(self, tian: str, ren: str, di: str) -> str:
        """判斷三才吉凶"""
        WUXING_SHENG = {"木": "火", "火": "土", "土": "金", "金": "水", "水": "木"}
        WUXING_KE = {"木": "土", "土": "水", "水": "火", "火": "金", "金": "木"}
        
        score = 0
        reasons = []
        
        # 天生人
        if WUXING_SHENG.get(tian) == ren:
            score += 30
            reasons.append("天生人")
        elif tian == ren:
            score += 20
            reasons.append("天人同")
        elif WUXING_KE.get(tian) == ren:
            score -= 20
            reasons.append("天剋人")
        
        # 人生地
        if WUXING_SHENG.get(ren) == di:
            score += 30
            reasons.append("人生地")
        elif ren == di:
            score += 20
            reasons.append("人地同")
        elif WUXING_KE.get(ren) == di:
            score -= 20
            reasons.append("人剋地")
        
        if score >= 50:
            return f"大吉 ({'+'.join(reasons)})"
        elif score >= 30:
            return f"吉 ({'+'.join(reasons)})"
        elif score >= 0:
            return f"平 ({'+'.join(reasons) if reasons else '無特殊'})"
        else:
            return f"凶 ({'+'.join(reasons)})"
    
    def analyze(self, surname: str, given_name: str, birth_info: 'BirthInfo' = None) -> NameAnalysis:
        """
        分析姓名
        
        📚 知識點：
            姓名分析 = 五格 + 三才 + 與八字配合
        """
        full_name = surname + given_name
        strokes = [self.get_strokes(c) for c in full_name]
        total_strokes = sum(strokes)
        
        # 計算五格
        wuge = self.calc_wuge(surname, given_name)
        
        # 吉凶總結
        fortunes = []
        for ge_name, ge_val in [("人格", wuge.renge), ("地格", wuge.dige), ("總格", wuge.zongge)]:
            fortune_info = STROKE_FORTUNE.get(ge_val, ("平", "一般"))
            fortunes.append(f"{ge_name}{ge_val}({fortune_info[0]})")
        
        fortune_summary = " | ".join(fortunes)
        
        # 五行分析
        wuxing_analysis = f"三才{wuge.sancai}: {wuge.sancai_fortune}"
        
        # 八字配合分析
        bazi_match = None
        WUXING_SHENG_LOCAL = {"木": "火", "火": "土", "土": "金", "金": "水", "水": "木"}
        if birth_info and self.engine:
            bazi = self.engine.get_bazi(birth_info)
            day_master = bazi.day_master
            day_master_wx = TIANGAN_WUXING.get(day_master, "")
            
            # 人格五行與日主關係
            if wuge.renge_wx == day_master_wx:
                bazi_match = f"人格{wuge.renge_wx}與日主{day_master}({day_master_wx})同類，助身"
            elif WUXING_SHENG_LOCAL.get(wuge.renge_wx) == day_master_wx:
                bazi_match = f"人格{wuge.renge_wx}生日主{day_master_wx}，有利"
        
        # 評分
        score = self._calc_score(wuge)
        
        # 建議
        suggestions = []
        if "凶" in fortune_summary:
            suggestions.append("部分格數偏凶，可考慮調整")
        if "大吉" in wuge.sancai_fortune:
            suggestions.append("三才配置優良")
        
        return NameAnalysis(
            surname=surname,
            given_name=given_name,
            full_name=full_name,
            strokes=strokes,
            total_strokes=total_strokes,
            wuge=wuge,
            fortune_summary=fortune_summary,
            wuxing_analysis=wuxing_analysis,
            bazi_match=bazi_match,
            score=score,
            suggestions=suggestions
        )
    
    def _calc_score(self, wuge: WugeResult) -> float:
        """計算姓名得分"""
        score = 60.0
        
        # 三才評分
        if "大吉" in wuge.sancai_fortune:
            score += 20
        elif "吉" in wuge.sancai_fortune:
            score += 10
        elif "凶" in wuge.sancai_fortune:
            score -= 15
        
        # 五格評分
        for ge_val in [wuge.renge, wuge.dige, wuge.zongge]:
            fortune = STROKE_FORTUNE.get(ge_val, ("平", ""))[0]
            if fortune == "大吉":
                score += 5
            elif fortune == "吉":
                score += 2
            elif fortune == "凶":
                score -= 5
        
        return max(0, min(100, score))
    
    def suggest_names(
        self,
        surname: str,
        birth_info: 'BirthInfo' = None,
        gender: str = "M",
        count: int = 10
    ) -> List[NameSuggestion]:
        """
        新生兒命名建議
        
        📚 知識點：
            命名 = 為場選擇最佳符號
            優先順序：三才吉 > 五格吉 > 八字補 > 字義美
        """
        suggestions = []
        s_strokes = sum(self.get_strokes(c) for c in surname)
        
        # 獲取八字喜用神
        need_wx = None
        if birth_info and self.engine:
            bazi = self.engine.get_bazi(birth_info)
            analysis = self.engine.analyze_bazi(bazi)
            if analysis.get("weak_wuxing"):
                need_wx = analysis["weak_wuxing"][0]
        
        # 生成候選名字組合
        # 簡化：根據筆畫吉凶選擇
        good_strokes = [n for n, (f, _) in STROKE_FORTUNE.items() if f in ["大吉", "吉"]]
        
        # 選擇字
        male_chars = ["文", "明", "志", "偉", "強", "軍", "海", "龍", "傑", "豪", "博", "哲", "睿", "德", "仁"]
        female_chars = ["美", "麗", "芳", "秀", "英", "玉", "珍", "雅", "靜", "婷", "慧", "敏", "穎", "嘉", "佳"]
        
        chars = male_chars if gender == "M" else female_chars
        
        # 嘗試組合
        tried = set()
        for c1 in chars:
            for c2 in chars:
                if c1 == c2:
                    continue
                name = c1 + c2
                if name in tried:
                    continue
                tried.add(name)
                
                # 分析
                analysis = self.analyze(surname, name, birth_info)
                
                # 篩選
                if analysis.score < 65:
                    continue
                
                reason_parts = []
                if "大吉" in analysis.wuge.sancai_fortune:
                    reason_parts.append("三才大吉")
                if need_wx and analysis.wuge.renge_wx == need_wx:
                    reason_parts.append(f"人格補{need_wx}")
                
                suggestions.append(NameSuggestion(
                    name=surname + name,
                    strokes=analysis.strokes,
                    score=analysis.score,
                    wuge=analysis.wuge,
                    reason=" | ".join(reason_parts) if reason_parts else "配置良好"
                ))
        
        # 排序取前 N
        suggestions.sort(key=lambda x: -x.score)
        return suggestions[:count]
    
    def compare_names(
        self,
        surname: str,
        old_name: str,
        new_name: str,
        birth_info: 'BirthInfo' = None
    ) -> Dict:
        """
        改名前後比對
        
        📚 知識點：
            改名 = 場的符號調整
            比較：五格變化 + 三才變化 + 分數變化
        """
        old_analysis = self.analyze(surname, old_name, birth_info)
        new_analysis = self.analyze(surname, new_name, birth_info)
        
        return {
            "old": old_analysis.to_dict(),
            "new": new_analysis.to_dict(),
            "score_change": round(new_analysis.score - old_analysis.score, 1),
            "sancai_change": f"{old_analysis.wuge.sancai} → {new_analysis.wuge.sancai}",
            "recommendation": "建議改名" if new_analysis.score > old_analysis.score + 10 else "改名效果有限"
        }


# =============================================================================
# M11: 公司行號命名引擎
# =============================================================================

class IndustryType(Enum):
    """行業類型"""
    TECH = ("科技", "金")
    FOOD = ("餐飲", "火")
    RETAIL = ("零售", "木")
    FINANCE = ("金融", "金")
    EDUCATION = ("教育", "水")
    HEALTH = ("醫療", "水")
    CONSTRUCTION = ("建築", "土")
    MEDIA = ("傳媒", "火")
    CULTURE = ("文創", "木")
    SERVICE = ("服務", "土")


@dataclass
class CompanyNameAnalysis:
    """公司名分析結果"""
    company_name: str
    strokes: List[int]
    total_strokes: int
    fortune: Tuple[str, str]
    wuxing: str
    industry_match: str
    score: float
    suggestions: List[str]
    
    def to_dict(self) -> Dict:
        return {
            "company_name": self.company_name,
            "strokes": self.strokes,
            "total_strokes": self.total_strokes,
            "fortune": {"level": self.fortune[0], "meaning": self.fortune[1]},
            "wuxing": self.wuxing,
            "industry_match": self.industry_match,
            "score": round(self.score, 1),
            "suggestions": self.suggestions
        }


class CompanyNameEngine:
    """
    公司行號命名引擎
    
    M11: 公司名五格 + 行業五行配對
    
    📚 知識點：
        公司名 = 企業場的符號
        行業五行 = 領域能量特性
    """
    
    VERSION = "1.0.0"
    
    def __init__(self):
        self.strokes_db = KANGXI_STROKES.copy()
    
    def get_strokes(self, char: str) -> int:
        """獲取筆畫"""
        if char in self.strokes_db:
            return self.strokes_db[char]
        return 10
    
    def analyze(
        self,
        company_name: str,
        industry: IndustryType = None
    ) -> CompanyNameAnalysis:
        """
        分析公司名
        
        📚 知識點：
            公司名筆畫 = 企業運勢指標
            與行業五行配合 = 事半功倍
        """
        strokes = [self.get_strokes(c) for c in company_name]
        total = sum(strokes)
        
        # 筆畫吉凶
        fortune = STROKE_FORTUNE.get(total, ("平", "一般數理"))
        
        # 總筆畫五行
        d = total % 10
        if d in [1, 2]:
            wuxing = "木"
        elif d in [3, 4]:
            wuxing = "火"
        elif d in [5, 6]:
            wuxing = "土"
        elif d in [7, 8]:
            wuxing = "金"
        else:
            wuxing = "水"
        
        # 行業配對
        industry_match = ""
        if industry:
            industry_wx = industry.value[1]
            WUXING_SHENG = {"木": "火", "火": "土", "土": "金", "金": "水", "水": "木"}
            
            if wuxing == industry_wx:
                industry_match = f"名稱五行{wuxing}與{industry.value[0]}行業{industry_wx}同類，大吉"
            elif WUXING_SHENG.get(wuxing) == industry_wx:
                industry_match = f"名稱五行{wuxing}生{industry.value[0]}行業{industry_wx}，有利"
            elif WUXING_SHENG.get(industry_wx) == wuxing:
                industry_match = f"{industry.value[0]}行業{industry_wx}生名稱五行{wuxing}，穩定"
            else:
                industry_match = f"名稱五行{wuxing}與行業{industry_wx}關係一般"
        
        # 評分
        score = 60.0
        if fortune[0] == "大吉":
            score += 25
        elif fortune[0] == "吉":
            score += 15
        elif fortune[0] == "凶":
            score -= 20
        
        if "大吉" in industry_match or "有利" in industry_match:
            score += 10
        
        # 建議
        suggestions = []
        if fortune[0] in ["凶", "半吉"]:
            suggestions.append(f"總筆畫{total}為{fortune[0]}，建議調整")
        if industry and "一般" in industry_match:
            suggestions.append("可考慮調整名稱五行與行業配合")
        if not suggestions:
            suggestions.append("名稱配置良好")
        
        return CompanyNameAnalysis(
            company_name=company_name,
            strokes=strokes,
            total_strokes=total,
            fortune=fortune,
            wuxing=wuxing,
            industry_match=industry_match,
            score=score,
            suggestions=suggestions
        )
    
    def suggest_names(
        self,
        base_name: str,
        industry: IndustryType,
        count: int = 5
    ) -> List[Dict]:
        """生成公司名建議"""
        suggestions = []
        
        # 常用公司名後綴
        suffixes = ["科技", "數位", "創意", "國際", "企業", "實業", "顧問", "工作室"]
        
        for suffix in suffixes:
            full_name = base_name + suffix
            analysis = self.analyze(full_name, industry)
            
            if analysis.score >= 70:
                suggestions.append({
                    "name": full_name,
                    "score": analysis.score,
                    "fortune": analysis.fortune[0],
                    "industry_match": "✓" if "大吉" in analysis.industry_match or "有利" in analysis.industry_match else "○"
                })
        
        suggestions.sort(key=lambda x: -x["score"])
        return suggestions[:count]


# =============================================================================
# M12: 嫁娶擇時引擎
# =============================================================================

@dataclass
class MarriageMatch:
    """合婚結果"""
    person_a: 'BirthInfo'
    person_b: 'BirthInfo'
    day_master_match: str
    wuxing_match: str
    compatibility: float
    strengths: List[str]
    challenges: List[str]
    advice: List[str]
    
    def to_dict(self) -> Dict:
        return {
            "day_master_match": self.day_master_match,
            "wuxing_match": self.wuxing_match,
            "compatibility": round(self.compatibility, 1),
            "strengths": self.strengths,
            "challenges": self.challenges,
            "advice": self.advice
        }


@dataclass
class MarriageDate:
    """嫁娶吉日"""
    date: date
    ganzhi: str
    quality: str
    score: float
    reasons: List[str]
    warnings: List[str]
    
    def to_dict(self) -> Dict:
        return {
            "date": self.date.isoformat(),
            "ganzhi": self.ganzhi,
            "quality": self.quality,
            "score": round(self.score, 1),
            "reasons": self.reasons,
            "warnings": self.warnings
        }


class MarriageZeriEngine:
    """
    嫁娶擇時引擎
    
    M12: 合婚分析 + 嫁娶吉日篩選
    
    📚 知識點：
        嫁娶 = 兩場合一的最佳時機
        合婚 = 場態共振評估
        擇日 = 選擇場態最佳節點
    """
    
    VERSION = "1.0.0"
    
    # 嫁娶忌日
    MARRIAGE_TABOOS = [
        "丙子", "丁丑", "戊寅", "辛卯", "庚辰", "癸巳",
        "甲午", "乙未", "戊申", "丁酉", "戊戌", "己亥"
    ]
    
    # 嫁娶吉日干支
    MARRIAGE_AUSPICIOUS = [
        "甲子", "乙丑", "丙寅", "丁卯", "己巳", "庚午",
        "辛未", "壬申", "癸酉", "甲戌", "乙亥"
    ]
    
    def __init__(self):
        try:
            self.engine = MingshuEngine()
            self.hepan = HepanEngine()
        except:
            self.engine = None
            self.hepan = None
    
    def _calc_day_ganzhi(self, dt: date) -> str:
        """計算日干支"""
        year, month, day = dt.year, dt.month, dt.day
        if month <= 2:
            year -= 1
            month += 12
        
        a = year // 100
        b = 2 - a + a // 4
        jd = int(365.25 * (year + 4716)) + int(30.6001 * (month + 1)) + day + b - 1524
        
        base_jd = 2445336
        diff = jd - base_jd
        idx = diff % 60
        if idx < 0:
            idx += 60
        
        return TIANGAN[idx % 10] + DIZHI[idx % 12]
    
    def analyze_match(
        self,
        person_a: 'BirthInfo',
        person_b: 'BirthInfo'
    ) -> MarriageMatch:
        """
        合婚分析
        
        📚 知識點：
            合婚 = 兩人場態的共振評估
            日主配對 = 核心能量匹配
        """
        # 獲取八字
        if self.engine:
            bazi_a = self.engine.get_bazi(person_a)
            bazi_b = self.engine.get_bazi(person_b)
            dm_a = bazi_a.day_master
            dm_b = bazi_b.day_master
        else:
            dm_a = "甲"
            dm_b = "乙"
        
        dm_a_wx = TIANGAN_WUXING.get(dm_a, "木")
        dm_b_wx = TIANGAN_WUXING.get(dm_b, "木")
        
        # 日主配對
        WUXING_SHENG = {"木": "火", "火": "土", "土": "金", "金": "水", "水": "木"}
        
        if dm_a_wx == dm_b_wx:
            day_master_match = f"日主同類 ({dm_a}{dm_a_wx} × {dm_b}{dm_b_wx})，相知相惜"
            dm_score = 75
        elif WUXING_SHENG.get(dm_a_wx) == dm_b_wx:
            day_master_match = f"男生女 ({dm_a}{dm_a_wx}生{dm_b}{dm_b_wx})，照顧有加"
            dm_score = 85
        elif WUXING_SHENG.get(dm_b_wx) == dm_a_wx:
            day_master_match = f"女生男 ({dm_b}{dm_b_wx}生{dm_a}{dm_a_wx})，支持包容"
            dm_score = 80
        else:
            day_master_match = f"五行相異 ({dm_a}{dm_a_wx} × {dm_b}{dm_b_wx})，需要磨合"
            dm_score = 60
        
        # 使用合盤引擎
        if self.hepan:
            hepan_result = self.hepan.analyze(person_a, person_b)
            compatibility = (dm_score + hepan_result.compatibility) / 2
            strengths = hepan_result.strengths
            challenges = hepan_result.challenges
        else:
            compatibility = dm_score
            strengths = ["日主配對良好"] if dm_score >= 75 else []
            challenges = ["需要更多磨合"] if dm_score < 70 else []
        
        # 建議
        advice = []
        if compatibility >= 80:
            advice.append("緣分深厚，可考慮擇吉日成婚")
        elif compatibility >= 65:
            advice.append("配對尚可，建議加強溝通")
        else:
            advice.append("配對有挑戰，建議深入了解")
        
        return MarriageMatch(
            person_a=person_a,
            person_b=person_b,
            day_master_match=day_master_match,
            wuxing_match=f"{dm_a_wx} × {dm_b_wx}",
            compatibility=compatibility,
            strengths=strengths,
            challenges=challenges,
            advice=advice
        )
    
    def find_auspicious_dates(
        self,
        person_a: 'BirthInfo',
        person_b: 'BirthInfo',
        start_date: date = None,
        days: int = 90
    ) -> List[MarriageDate]:
        """
        尋找嫁娶吉日
        
        📚 知識點：
            嫁娶擇日 = 避開忌日 + 選擇吉日 + 與雙方八字配合
        """
        if start_date is None:
            start_date = date.today()
        
        # 獲取日主
        if self.engine:
            bazi_a = self.engine.get_bazi(person_a)
            bazi_b = self.engine.get_bazi(person_b)
            dm_a_wx = TIANGAN_WUXING.get(bazi_a.day_master, "木")
            dm_b_wx = TIANGAN_WUXING.get(bazi_b.day_master, "木")
        else:
            dm_a_wx = "木"
            dm_b_wx = "火"
        
        results = []
        current = start_date
        end_date = start_date + timedelta(days=days)
        
        while current <= end_date:
            ganzhi = self._calc_day_ganzhi(current)
            gan = ganzhi[0]
            zhi = ganzhi[1]
            
            score = 60.0
            reasons = []
            warnings = []
            
            # 檢查忌日
            if ganzhi in self.MARRIAGE_TABOOS:
                score -= 30
                warnings.append(f"{ganzhi}為嫁娶忌日")
            
            # 檢查吉日
            if ganzhi in self.MARRIAGE_AUSPICIOUS:
                score += 20
                reasons.append(f"{ganzhi}為嫁娶吉日")
            
            # 與日主配合
            gan_wx = TIANGAN_WUXING.get(gan, "")
            if gan_wx == dm_a_wx or gan_wx == dm_b_wx:
                score += 10
                reasons.append(f"日干{gan}({gan_wx})與命主相合")
            
            # 避開沖日（簡化）
            # 子午沖、卯酉沖、寅申沖、巳亥沖、辰戌沖、丑未沖
            
            # 月份考量（農曆雙月為佳）
            if current.month in [2, 4, 6, 8, 10, 12]:
                score += 5
                reasons.append("雙月吉利")
            
            # 週末加分
            if current.weekday() in [5, 6]:
                score += 5
                reasons.append("週末便於宴客")
            
            # 判斷品質
            if score >= 80:
                quality = "大吉"
            elif score >= 65:
                quality = "吉"
            elif score >= 50:
                quality = "平"
            else:
                quality = "忌"
            
            if quality in ["大吉", "吉"]:
                results.append(MarriageDate(
                    date=current,
                    ganzhi=ganzhi,
                    quality=quality,
                    score=score,
                    reasons=reasons if reasons else ["日期平穩"],
                    warnings=warnings
                ))
            
            current += timedelta(days=1)
        
        # 排序
        results.sort(key=lambda x: -x.score)
        return results[:20]


# =============================================================================
# API 整合
# =============================================================================

class NamingMarriageAPI:
    """
    姓名+命名+嫁娶 API
    
    整合 M10+M11+M12
    """
    
    VERSION = "1.0.0"
    
    def __init__(self):
        self.name_engine = NameEngine()
        self.company_engine = CompanyNameEngine()
        self.marriage_engine = MarriageZeriEngine()
    
    def analyze_name(self, surname: str, given_name: str, birth_info: Dict = None) -> Dict:
        """分析姓名"""
        bi = None
        if birth_info:
            try:
                bi = BirthInfo(
                    year=birth_info.get("year", 1990),
                    month=birth_info.get("month", 1),
                    day=birth_info.get("day", 1),
                    hour=birth_info.get("hour", 12),
                    gender=Gender(birth_info.get("gender", "M")),
                    calendar=CalendarType(birth_info.get("calendar", "lunar"))
                )
            except:
                pass
        
        result = self.name_engine.analyze(surname, given_name, bi)
        return {"success": True, "data": result.to_dict()}
    
    def suggest_baby_names(
        self,
        surname: str,
        birth_info: Dict,
        gender: str = "M",
        count: int = 10
    ) -> Dict:
        """新生兒命名建議"""
        try:
            bi = BirthInfo(
                year=birth_info.get("year"),
                month=birth_info.get("month"),
                day=birth_info.get("day"),
                hour=birth_info.get("hour", 12),
                gender=Gender(gender),
                calendar=CalendarType(birth_info.get("calendar", "lunar"))
            )
        except:
            bi = None
        
        suggestions = self.name_engine.suggest_names(surname, bi, gender, count)
        return {"success": True, "data": [s.to_dict() for s in suggestions]}
    
    def compare_rename(
        self,
        surname: str,
        old_name: str,
        new_name: str,
        birth_info: Dict = None
    ) -> Dict:
        """改名比對"""
        bi = None
        if birth_info:
            try:
                bi = BirthInfo(
                    year=birth_info.get("year"),
                    month=birth_info.get("month"),
                    day=birth_info.get("day"),
                    hour=birth_info.get("hour", 12),
                    gender=Gender(birth_info.get("gender", "M")),
                    calendar=CalendarType(birth_info.get("calendar", "lunar"))
                )
            except:
                pass
        
        result = self.name_engine.compare_names(surname, old_name, new_name, bi)
        return {"success": True, "data": result}
    
    def analyze_company_name(
        self,
        company_name: str,
        industry: str = None
    ) -> Dict:
        """分析公司名"""
        ind = None
        if industry:
            try:
                ind = IndustryType[industry.upper()]
            except:
                pass
        
        result = self.company_engine.analyze(company_name, ind)
        return {"success": True, "data": result.to_dict()}
    
    def suggest_company_names(
        self,
        base_name: str,
        industry: str,
        count: int = 5
    ) -> Dict:
        """公司名建議"""
        try:
            ind = IndustryType[industry.upper()]
        except:
            ind = IndustryType.TECH
        
        suggestions = self.company_engine.suggest_names(base_name, ind, count)
        return {"success": True, "data": suggestions}
    
    def analyze_marriage_match(
        self,
        person_a: Dict,
        person_b: Dict
    ) -> Dict:
        """合婚分析"""
        try:
            bi_a = BirthInfo(
                year=person_a.get("year"),
                month=person_a.get("month"),
                day=person_a.get("day"),
                hour=person_a.get("hour", 12),
                gender=Gender(person_a.get("gender", "M")),
                calendar=CalendarType(person_a.get("calendar", "lunar")),
                name=person_a.get("name", "")
            )
            bi_b = BirthInfo(
                year=person_b.get("year"),
                month=person_b.get("month"),
                day=person_b.get("day"),
                hour=person_b.get("hour", 12),
                gender=Gender(person_b.get("gender", "F")),
                calendar=CalendarType(person_b.get("calendar", "lunar")),
                name=person_b.get("name", "")
            )
        except Exception as e:
            return {"success": False, "error": str(e)}
        
        result = self.marriage_engine.analyze_match(bi_a, bi_b)
        return {"success": True, "data": result.to_dict()}
    
    def find_marriage_dates(
        self,
        person_a: Dict,
        person_b: Dict,
        start_date: str = None,
        days: int = 90
    ) -> Dict:
        """尋找嫁娶吉日"""
        try:
            bi_a = BirthInfo(
                year=person_a.get("year"),
                month=person_a.get("month"),
                day=person_a.get("day"),
                hour=person_a.get("hour", 12),
                gender=Gender(person_a.get("gender", "M")),
                calendar=CalendarType(person_a.get("calendar", "lunar"))
            )
            bi_b = BirthInfo(
                year=person_b.get("year"),
                month=person_b.get("month"),
                day=person_b.get("day"),
                hour=person_b.get("hour", 12),
                gender=Gender(person_b.get("gender", "F")),
                calendar=CalendarType(person_b.get("calendar", "lunar"))
            )
        except Exception as e:
            return {"success": False, "error": str(e)}
        
        start = date.fromisoformat(start_date) if start_date else None
        results = self.marriage_engine.find_auspicious_dates(bi_a, bi_b, start, days)
        return {"success": True, "data": [r.to_dict() for r in results]}


# =============================================================================
# CLI 入口
# =============================================================================

def main():
    """CLI 入口"""
    print("=" * 60)
    print("北斗命數 姓名+命名+嫁娶 v1.0")
    print("M10 (姓名) + M11 (公司) + M12 (嫁娶)")
    print("=" * 60)
    
    name_engine = NameEngine()
    company_engine = CompanyNameEngine()
    marriage_engine = MarriageZeriEngine()
    
    # M10 測試: 姓名分析
    print("\n【M10 姓名分析】")
    analysis = name_engine.analyze("楊", "三興")
    print(f"  姓名: {analysis.full_name}")
    print(f"  筆畫: {analysis.strokes} = {analysis.total_strokes}")
    print(f"  三才: {analysis.wuge.sancai} ({analysis.wuge.sancai_fortune})")
    print(f"  五格: 天{analysis.wuge.tiange} 人{analysis.wuge.renge} 地{analysis.wuge.dige} 外{analysis.wuge.waige} 總{analysis.wuge.zongge}")
    print(f"  得分: {analysis.score:.1f}/100")
    
    # M10 測試: 新生兒命名
    print("\n【M10 新生兒命名】")
    try:
        birth = BirthInfo(
            year=2026, month=1, day=15, hour=10,
            gender=Gender.MALE, calendar=CalendarType.LUNAR
        )
        suggestions = name_engine.suggest_names("楊", birth, "M", 5)
        print(f"  姓氏「楊」的男寶命名建議:")
        for i, s in enumerate(suggestions[:3]):
            print(f"    {i+1}. {s.name} (得分:{s.score:.0f}) - {s.reason}")
    except:
        print("  (需要 mingshu_engine_v1 支援)")
    
    # M11 測試: 公司名分析
    print("\n【M11 公司名分析】")
    company = company_engine.analyze("北斗七星文創數位", IndustryType.CULTURE)
    print(f"  公司: {company.company_name}")
    print(f"  筆畫: {company.total_strokes}")
    print(f"  五行: {company.wuxing}")
    print(f"  吉凶: {company.fortune[0]} - {company.fortune[1]}")
    print(f"  行業配對: {company.industry_match}")
    print(f"  得分: {company.score:.1f}/100")
    
    # M12 測試: 合婚分析
    print("\n【M12 合婚分析】")
    try:
        person_a = BirthInfo(1983, 12, 16, 5, Gender.MALE, CalendarType.LUNAR, "北斗")
        person_b = BirthInfo(1985, 8, 20, 14, Gender.FEMALE, CalendarType.LUNAR, "伴侶")
        
        match = marriage_engine.analyze_match(person_a, person_b)
        print(f"  {person_a.name} × {person_b.name}")
        print(f"  日主配對: {match.day_master_match}")
        print(f"  相容度: {match.compatibility:.1f}/100")
        print(f"  建議: {match.advice[0] if match.advice else '-'}")
        
        # M12 測試: 嫁娶吉日
        print("\n【M12 嫁娶吉日】")
        dates = marriage_engine.find_auspicious_dates(person_a, person_b, days=30)
        print(f"  未來30天嫁娶吉日 (前5個):")
        for i, d in enumerate(dates[:5]):
            print(f"    {i+1}. {d.date} {d.ganzhi} ({d.quality}) - {d.reasons[0] if d.reasons else '-'}")
    except:
        print("  (需要 mingshu_engine_v1 支援)")
    
    print("\n" + "=" * 60)
    print("姓名=後天場符號 | 命名=為場選符 | 嫁娶=兩場合一")
    print("=" * 60)


if __name__ == "__main__":
    main()


# =============================================================================
# 📚 知識點總結
# =============================================================================
"""
【M10 姓名學】

三才五格：
- 天格 = 姓+1 (單姓) / 姓1+姓2 (複姓)
- 人格 = 姓+名1
- 地格 = 名1+名2
- 外格 = 總-人+1
- 總格 = 全部

數字五行：
- 1,2 = 木
- 3,4 = 火
- 5,6 = 土
- 7,8 = 金
- 9,0 = 水

命名原則：
- 三才相生為吉
- 五格吉數為佳
- 與八字喜用配合

【M11 公司命名】

行業五行：
- 科技/金融 = 金
- 餐飲/傳媒 = 火
- 零售/文創 = 木
- 建築/服務 = 土
- 教育/醫療 = 水

命名原則：
- 總筆畫取吉數
- 五行與行業配合
- 字義正面響亮

【M12 嫁娶擇時】

合婚要點：
- 日主五行配對
- 場態共振評估
- 強弱互補分析

擇日原則：
- 避開嫁娶忌日
- 選擇吉日吉時
- 與雙方八字配合

【織明語錄】
- 「姓名是後天場的文字錨點」
- 「命名是為場選擇最佳符號」
- 「嫁娶是兩場合一的最佳時機」
"""
