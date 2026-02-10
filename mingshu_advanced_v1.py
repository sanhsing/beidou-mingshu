#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
mingshu_advanced_v1.py - 北斗命數進階術數 v1.0
================================================
北斗七星文創 × 織明

XTF⁸ 任務鏈：D1-D4 進階術數
執行星：織明(統籌) × 理樞(算法) × 澄韻(翻譯) × 流祇(場論) × 澄書(文檔)

模組整合 (PYLIB First):
    D1: 紫微斗數進階 - 四化飛星 + 飛星盤 + 宮位四化
        整合: ziwei_advanced, sihua_translation, fuzhu_star_translation
    D2: 奇門遁甲 - 時盤排盤 + 格局判斷
        整合: qimen_engine_v1
    D3: 六壬神課 - 十二神將 + 四課三傳
        新開發
    D4: 風水羅盤 - 二十四山 + 三元九運
        新開發

📚 知識點：
    「進階術數 = 場論多視角的深度探測」
    「四化 = 能量轉化的四種模式」
    「奇門 = 時空場的戰略視角」
    「六壬 = 事態發展的動態模擬」
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple, Any
from enum import Enum
from datetime import datetime, date
import json

# =============================================================================
# 基礎常量
# =============================================================================

TIANGAN = ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"]
DIZHI = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]
WUXING = ["木", "火", "土", "金", "水"]

TIANGAN_WUXING = {
    "甲": "木", "乙": "木", "丙": "火", "丁": "火", "戊": "土",
    "己": "土", "庚": "金", "辛": "金", "壬": "水", "癸": "水"
}

DIZHI_WUXING = {
    "子": "水", "丑": "土", "寅": "木", "卯": "木", "辰": "土", "巳": "火",
    "午": "火", "未": "土", "申": "金", "酉": "金", "戌": "土", "亥": "水"
}


# =============================================================================
# D1: 紫微斗數進階 - 四化飛星
# =============================================================================

class SihuaType(Enum):
    """四化類型"""
    HUALU = ("化祿", "祿", "財富、機會、增益")
    HUAQUAN = ("化權", "權", "權力、掌控、主導")
    HUAKE = ("化科", "科", "名聲、考試、文書")
    HUAJI = ("化忌", "忌", "阻礙、執著、業力")


# 十天干四化星對照表 (甲乙丙丁戊己庚辛壬癸)
SIHUA_TABLE = {
    "甲": {"化祿": "廉貞", "化權": "破軍", "化科": "武曲", "化忌": "太陽"},
    "乙": {"化祿": "天機", "化權": "天梁", "化科": "紫微", "化忌": "太陰"},
    "丙": {"化祿": "天同", "化權": "天機", "化科": "文昌", "化忌": "廉貞"},
    "丁": {"化祿": "太陰", "化權": "天同", "化科": "天機", "化忌": "巨門"},
    "戊": {"化祿": "貪狼", "化權": "太陰", "化科": "右弼", "化忌": "天機"},
    "己": {"化祿": "武曲", "化權": "貪狼", "化科": "天梁", "化忌": "文曲"},
    "庚": {"化祿": "太陽", "化權": "武曲", "化科": "太陰", "化忌": "天同"},
    "辛": {"化祿": "巨門", "化權": "太陽", "化科": "文曲", "化忌": "文昌"},
    "壬": {"化祿": "天梁", "化權": "紫微", "化科": "左輔", "化忌": "武曲"},
    "癸": {"化祿": "破軍", "化權": "巨門", "化科": "太陰", "化忌": "貪狼"},
}

# 十二宮位
ZIWEI_GONGS = [
    "命宮", "兄弟宮", "夫妻宮", "子女宮", "財帛宮", "疾厄宮",
    "遷移宮", "交友宮", "官祿宮", "田宅宮", "福德宮", "父母宮"
]

# 主星列表
ZIWEI_MAIN_STARS = [
    "紫微", "天機", "太陽", "武曲", "天同", "廉貞",
    "天府", "太陰", "貪狼", "巨門", "天相", "天梁", "七殺", "破軍"
]


@dataclass
class SihuaInfo:
    """四化資訊"""
    sihua_type: str       # 化祿/化權/化科/化忌
    star: str             # 被化的星
    source_gan: str       # 來源天干
    target_gong: str      # 落入宮位
    meaning: str          # 解讀
    
    def to_dict(self) -> Dict:
        return {
            "type": self.sihua_type,
            "star": self.star,
            "source": self.source_gan,
            "gong": self.target_gong,
            "meaning": self.meaning
        }


@dataclass
class FeixingResult:
    """飛星結果"""
    source_gong: str          # 起飛宮位
    source_gan: str           # 宮位天干
    sihua_list: List[SihuaInfo]  # 四化列表
    field_analysis: str       # 場論分析
    
    def to_dict(self) -> Dict:
        return {
            "source_gong": self.source_gong,
            "source_gan": self.source_gan,
            "sihua": [s.to_dict() for s in self.sihua_list],
            "field_analysis": self.field_analysis
        }


class ZiweiAdvancedEngine:
    """
    紫微斗數進階引擎
    
    D1: 四化飛星 + 宮位四化 + 自化分析
    
    📚 知識點：
        四化 = 能量轉化的四種模式
        飛星 = 宮位間的能量傳遞
        自化 = 宮位內的能量循環
    """
    
    VERSION = "1.0.0"
    
    def __init__(self):
        pass
    
    def get_sihua_by_gan(self, tiangan: str) -> Dict[str, str]:
        """
        根據天干獲取四化星
        
        📚 知識點：
            每個天干對應固定的四化星組合
            這是紫微斗數的核心機制之一
        """
        return SIHUA_TABLE.get(tiangan, {})
    
    def analyze_natal_sihua(self, year_gan: str, star_positions: Dict[str, str] = None) -> List[SihuaInfo]:
        """
        分析本命四化
        
        Args:
            year_gan: 出生年天干
            star_positions: 星曜所在宮位 {星名: 宮位}
        """
        sihua_stars = self.get_sihua_by_gan(year_gan)
        results = []
        
        meanings = {
            "化祿": "此星得祿，帶來財富與機會，所在宮位為收穫領域",
            "化權": "此星得權，掌握主導權，所在宮位為掌控重心",
            "化科": "此星得科，帶來名聲與貴人，所在宮位為揚名之處",
            "化忌": "此星化忌，帶來阻礙與執著，所在宮位需特別留意"
        }
        
        for sihua_type, star in sihua_stars.items():
            gong = star_positions.get(star, "未知") if star_positions else "待定"
            results.append(SihuaInfo(
                sihua_type=sihua_type,
                star=star,
                source_gan=year_gan,
                target_gong=gong,
                meaning=f"{star}{sihua_type}：{meanings.get(sihua_type, '')}"
            ))
        
        return results
    
    def analyze_feixing(
        self,
        source_gong: str,
        gong_gan: str,
        star_positions: Dict[str, str] = None
    ) -> FeixingResult:
        """
        分析飛星（宮干四化）
        
        📚 知識點：
            飛星 = 從某宮飛出的四化
            宮干 = 宮位的天干
            四化落宮 = 能量傳遞的目的地
        """
        sihua_stars = self.get_sihua_by_gan(gong_gan)
        sihua_list = []
        
        for sihua_type, star in sihua_stars.items():
            gong = star_positions.get(star, "未知") if star_positions else "待定"
            meaning = self._get_feixing_meaning(source_gong, sihua_type, gong)
            sihua_list.append(SihuaInfo(
                sihua_type=sihua_type,
                star=star,
                source_gan=gong_gan,
                target_gong=gong,
                meaning=meaning
            ))
        
        field_analysis = self._analyze_feixing_field(source_gong, sihua_list)
        
        return FeixingResult(
            source_gong=source_gong,
            source_gan=gong_gan,
            sihua_list=sihua_list,
            field_analysis=field_analysis
        )
    
    def _get_feixing_meaning(self, source: str, sihua_type: str, target: str) -> str:
        """獲取飛星解讀"""
        if source == target:
            return f"自化{sihua_type}：{source}的能量在宮內循環"
        
        relation_meanings = {
            ("命宮", "財帛宮"): "命飛財：個人能量轉化為財富",
            ("命宮", "官祿宮"): "命飛官：個人能量轉化為事業",
            ("官祿宮", "命宮"): "官飛命：事業能量反饋自身",
            ("財帛宮", "命宮"): "財飛命：財富能量滋養自身",
        }
        
        key = (source, target)
        if key in relation_meanings:
            return f"{relation_meanings[key]}（{sihua_type}）"
        
        return f"{source}飛{target}：{sihua_type}能量從{source}傳遞到{target}"
    
    def _analyze_feixing_field(self, source: str, sihua_list: List[SihuaInfo]) -> str:
        """場論分析飛星"""
        targets = [s.target_gong for s in sihua_list]
        
        # 檢查自化
        self_hua = [s for s in sihua_list if s.target_gong == source]
        if self_hua:
            return f"場論視角：{source}有自化現象，能量在本宮循環，{self_hua[0].sihua_type}特質強化"
        
        # 檢查集中
        from collections import Counter
        target_count = Counter(targets)
        most_common = target_count.most_common(1)
        if most_common and most_common[0][1] >= 2:
            return f"場論視角：能量集中於{most_common[0][0]}，該領域為{source}的重點投射區"
        
        return f"場論視角：{source}的能量分散投射，影響多個生活領域"
    
    def analyze_zihua(self, gong: str, gong_gan: str, stars_in_gong: List[str]) -> Dict:
        """
        分析自化
        
        📚 知識點：
            自化 = 宮干四化的星正好在本宮
            自化祿 = 自己賺自己花，不積財
            自化忌 = 內耗、自我阻礙
        """
        sihua_stars = self.get_sihua_by_gan(gong_gan)
        zihua_found = []
        
        for sihua_type, star in sihua_stars.items():
            if star in stars_in_gong:
                zihua_found.append({
                    "type": sihua_type,
                    "star": star,
                    "meaning": self._get_zihua_meaning(sihua_type)
                })
        
        return {
            "gong": gong,
            "gong_gan": gong_gan,
            "zihua": zihua_found,
            "has_zihua": len(zihua_found) > 0
        }
    
    def _get_zihua_meaning(self, sihua_type: str) -> str:
        """自化解讀"""
        meanings = {
            "化祿": "自化祿：財來財去，賺錢能力強但不易積蓄，享受當下",
            "化權": "自化權：獨立自主，不喜受人管束，自我意識強",
            "化科": "自化科：低調謙虛，不愛出風頭，內斂型才華",
            "化忌": "自化忌：內心糾結，自我要求高，容易鑽牛角尖"
        }
        return meanings.get(sihua_type, "")


# =============================================================================
# D2: 奇門遁甲
# =============================================================================

# 九宮
JIUGONG = ["坎一宮", "坤二宮", "震三宮", "巽四宮", "中五宮", "乾六宮", "兌七宮", "艮八宮", "離九宮"]

# 八門
BAMEN = ["休門", "生門", "傷門", "杜門", "景門", "死門", "驚門", "開門"]

# 九星
JIUXING = ["天蓬", "天芮", "天衝", "天輔", "天禽", "天心", "天柱", "天任", "天英"]

# 八神
BASHEN = ["值符", "騰蛇", "太陰", "六合", "白虎", "玄武", "九地", "九天"]

# 節氣局數對照
JIEQI_JU = {
    "冬至": [1, 7, 4], "小寒": [2, 8, 5], "大寒": [3, 9, 6],
    "立春": [8, 5, 2], "雨水": [9, 6, 3], "驚蟄": [1, 7, 4],
    "春分": [3, 9, 6], "清明": [4, 1, 7], "穀雨": [5, 2, 8],
    "立夏": [4, 1, 7], "小滿": [5, 2, 8], "芒種": [6, 3, 9],
    "夏至": [9, 3, 6], "小暑": [8, 2, 5], "大暑": [7, 1, 4],
    "立秋": [2, 5, 8], "處暑": [1, 4, 7], "白露": [9, 3, 6],
    "秋分": [7, 1, 4], "寒露": [6, 9, 3], "霜降": [5, 8, 2],
    "立冬": [6, 9, 3], "小雪": [5, 8, 2], "大雪": [4, 7, 1],
}


@dataclass
class QimenGong:
    """奇門宮位"""
    position: int          # 宮位 (1-9)
    name: str              # 宮名
    tiangan: str           # 天干
    men: str               # 門
    xing: str              # 星
    shen: str              # 神
    dizhi: str             # 地支（地盤）
    
    def to_dict(self) -> Dict:
        return {
            "position": self.position,
            "name": self.name,
            "tiangan": self.tiangan,
            "men": self.men,
            "xing": self.xing,
            "shen": self.shen,
            "dizhi": self.dizhi
        }


@dataclass
class QimenPan:
    """奇門盤"""
    pan_type: str          # 盤類型 (時盤/日盤/月盤/年盤)
    ju_number: int         # 局數 (1-9)
    is_yang_dun: bool      # 陽遁/陰遁
    gongs: List[QimenGong] # 九宮
    duty_gan: str          # 值符落宮天干
    duty_men: str          # 值使落宮門
    timestamp: datetime    # 起盤時間
    geju: List[str]        # 格局
    
    def to_dict(self) -> Dict:
        return {
            "type": self.pan_type,
            "ju": self.ju_number,
            "yang_dun": self.is_yang_dun,
            "gongs": [g.to_dict() for g in self.gongs],
            "duty_gan": self.duty_gan,
            "duty_men": self.duty_men,
            "timestamp": self.timestamp.isoformat(),
            "geju": self.geju
        }


class QimenEngine:
    """
    奇門遁甲引擎
    
    D2: 時盤排盤 + 格局判斷 + 場論解讀
    
    📚 知識點：
        奇門 = 時空場的戰略視角
        三奇 = 乙丙丁 (日月星)
        六儀 = 戊己庚辛壬癸
        八門 = 行動方向指引
    """
    
    VERSION = "1.0.0"
    
    def __init__(self):
        pass
    
    def get_jieqi(self, dt: date) -> str:
        """獲取節氣（簡化版）"""
        # 簡化：根據月日粗略判斷
        month = dt.month
        day = dt.day
        
        jieqi_dates = {
            (1, 6): "小寒", (1, 20): "大寒",
            (2, 4): "立春", (2, 19): "雨水",
            (3, 6): "驚蟄", (3, 21): "春分",
            (4, 5): "清明", (4, 20): "穀雨",
            (5, 6): "立夏", (5, 21): "小滿",
            (6, 6): "芒種", (6, 21): "夏至",
            (7, 7): "小暑", (7, 23): "大暑",
            (8, 8): "立秋", (8, 23): "處暑",
            (9, 8): "白露", (9, 23): "秋分",
            (10, 8): "寒露", (10, 24): "霜降",
            (11, 8): "立冬", (11, 22): "小雪",
            (12, 7): "大雪", (12, 22): "冬至",
        }
        
        # 找最近的節氣
        current_jieqi = "冬至"
        for (m, d), jq in jieqi_dates.items():
            if month > m or (month == m and day >= d):
                current_jieqi = jq
        
        return current_jieqi
    
    def is_yang_dun(self, jieqi: str) -> bool:
        """判斷陽遁/陰遁"""
        yang_jieqi = ["冬至", "小寒", "大寒", "立春", "雨水", "驚蟄",
                      "春分", "清明", "穀雨", "立夏", "小滿", "芒種"]
        return jieqi in yang_jieqi
    
    def get_ju_number(self, jieqi: str, yuan: int = 0) -> int:
        """
        獲取局數
        
        Args:
            jieqi: 節氣
            yuan: 元 (0=上元, 1=中元, 2=下元)
        """
        ju_list = JIEQI_JU.get(jieqi, [1, 7, 4])
        return ju_list[yuan % 3]
    
    def hour_to_dizhi(self, hour: int) -> str:
        """時辰轉地支"""
        dizhi_hours = [
            (23, 1, "子"), (1, 3, "丑"), (3, 5, "寅"), (5, 7, "卯"),
            (7, 9, "辰"), (9, 11, "巳"), (11, 13, "午"), (13, 15, "未"),
            (15, 17, "申"), (17, 19, "酉"), (19, 21, "戌"), (21, 23, "亥")
        ]
        
        for start, end, zhi in dizhi_hours:
            if start <= hour < end or (start == 23 and (hour >= 23 or hour < 1)):
                return zhi
        return "子"
    
    def create_pan(self, dt: datetime = None, pan_type: str = "時盤") -> QimenPan:
        """
        創建奇門盤
        
        📚 知識點：
            排盤步驟：
            1. 定局數 (節氣+元)
            2. 定值符值使 (時干)
            3. 排天盤 (三奇六儀)
            4. 排門盤 (八門)
            5. 排星盤 (九星)
            6. 排神盤 (八神)
        """
        if dt is None:
            dt = datetime.now()
        
        jieqi = self.get_jieqi(dt.date())
        yang_dun = self.is_yang_dun(jieqi)
        
        # 簡化：根據時辰計算元
        hour_zhi = self.hour_to_dizhi(dt.hour)
        yuan = DIZHI.index(hour_zhi) % 3
        
        ju = self.get_ju_number(jieqi, yuan)
        
        # 構建九宮（簡化版）
        gongs = []
        
        # 地盤地支對應
        dipan_zhi = ["子", "坤", "卯", "巽", "中", "乾", "酉", "艮", "午"]
        
        # 簡化排盤
        for i in range(9):
            pos = i + 1
            name = JIUGONG[i]
            
            # 天干（簡化：按順序）
            gan_idx = (ju - 1 + i) % 10
            tiangan = TIANGAN[gan_idx]
            
            # 門
            men_idx = (ju - 1 + i) % 8
            men = BAMEN[men_idx]
            
            # 星
            xing_idx = i
            xing = JIUXING[xing_idx]
            
            # 神
            shen_idx = i % 8
            shen = BASHEN[shen_idx]
            
            gongs.append(QimenGong(
                position=pos,
                name=name,
                tiangan=tiangan,
                men=men,
                xing=xing,
                shen=shen,
                dizhi=dipan_zhi[i]
            ))
        
        # 值符值使
        duty_gan = TIANGAN[(ju - 1) % 10]
        duty_men = BAMEN[(ju - 1) % 8]
        
        # 格局分析
        geju = self._analyze_geju(gongs, yang_dun)
        
        return QimenPan(
            pan_type=pan_type,
            ju_number=ju,
            is_yang_dun=yang_dun,
            gongs=gongs,
            duty_gan=duty_gan,
            duty_men=duty_men,
            timestamp=dt,
            geju=geju
        )
    
    def _analyze_geju(self, gongs: List[QimenGong], yang_dun: bool) -> List[str]:
        """
        分析格局
        
        📚 知識點：
            吉格：青龍返首、飛鳥跌穴、九遁等
            凶格：伏吟、反吟、刑格等
        """
        geju = []
        
        # 檢查三奇 (乙丙丁)
        sanqi_gongs = []
        for g in gongs:
            if g.tiangan in ["乙", "丙", "丁"]:
                sanqi_gongs.append((g.tiangan, g.position))
        
        if sanqi_gongs:
            geju.append(f"三奇落宮：{', '.join([f'{t}在{p}宮' for t, p in sanqi_gongs])}")
        
        # 檢查吉門
        ji_men = ["生門", "開門", "休門"]
        for g in gongs:
            if g.men in ji_men:
                geju.append(f"吉門{g.men}在{g.position}宮")
                break
        
        # 檢查值符
        for g in gongs:
            if g.shen == "值符":
                geju.append(f"值符在{g.position}宮（{g.name}）")
                break
        
        if not geju:
            geju.append("盤局中性，需結合具體問題分析")
        
        return geju
    
    def get_field_interpretation(self, pan: QimenPan) -> Dict:
        """
        場論解讀奇門盤
        
        📚 知識點：
            奇門 = 時空場的戰略層
            九宮 = 場的九個方位區域
            八門 = 場的八種行動向量
        """
        interpretation = {
            "overall": "",
            "action_advice": "",
            "favorable_direction": "",
            "timing": ""
        }
        
        # 整體判斷
        dun_type = "陽遁" if pan.is_yang_dun else "陰遁"
        interpretation["overall"] = f"{dun_type}{pan.ju_number}局：{'進取擴張' if pan.is_yang_dun else '收斂守成'}之勢"
        
        # 行動建議（根據值使門）
        men_advice = {
            "開門": "宜開創、求財、出行",
            "生門": "宜生意、置產、求醫",
            "休門": "宜休養、訪友、養生",
            "傷門": "宜競爭、訴訟、維權",
            "杜門": "宜隱藏、保密、避禍",
            "景門": "宜文書、考試、宣傳",
            "死門": "宜安葬、結束、了斷",
            "驚門": "宜口舌、談判、警示"
        }
        interpretation["action_advice"] = men_advice.get(pan.duty_men, "中性，視情況而定")
        
        # 有利方位
        for g in pan.gongs:
            if g.men in ["生門", "開門"]:
                direction_map = {
                    1: "北", 2: "西南", 3: "東", 4: "東南",
                    5: "中", 6: "西北", 7: "西", 8: "東北", 9: "南"
                }
                interpretation["favorable_direction"] = f"{direction_map.get(g.position, '')}方（{g.men}所在）"
                break
        
        # 時機
        interpretation["timing"] = f"值符{pan.duty_gan}，值使{pan.duty_men}：{self._get_timing_advice(pan.duty_men)}"
        
        return interpretation
    
    def _get_timing_advice(self, men: str) -> str:
        """時機建議"""
        advice = {
            "開門": "此時宜動不宜靜，把握機會",
            "生門": "生機勃發，適合啟動新計劃",
            "休門": "休養生息，不宜強求",
            "傷門": "小心衝突，宜守不宜攻",
            "杜門": "閉門修煉，不宜對外",
            "景門": "適合學習、表達、創作",
            "死門": "宜結束舊事，不宜開新",
            "驚門": "謹慎行事，防止意外"
        }
        return advice.get(men, "中性時機")


# =============================================================================
# D3: 六壬神課
# =============================================================================

# 十二神將
SHIER_SHENJIANG = {
    "子": ("貴人", "天乙貴人，主貴氣、化解"),
    "丑": ("騰蛇", "主怪異、變化、憂慮"),
    "寅": ("朱雀", "主口舌、文書、訊息"),
    "卯": ("六合", "主和合、交易、媒介"),
    "辰": ("勾陳", "主訴訟、田土、糾纏"),
    "巳": ("青龍", "主喜慶、財帛、吉祥"),
    "午": ("太常", "主衣祿、宴會、穩定"),
    "未": ("白虎", "主凶煞、疾病、喪亡"),
    "申": ("太陰", "主陰私、賄賂、暗事"),
    "酉": ("天后", "主婦女、陰私、暗昧"),
    "戌": ("玄武", "主盜賊、欺騙、逃亡"),
    "亥": ("天空", "主欺詐、空亡、虛假")
}

# 四課
SIKE_DESC = {
    "一課": "日上神，代表自己、主動方",
    "二課": "日下神，代表自己的行動結果",
    "三課": "辰上神，代表對方、被動方",
    "四課": "辰下神，代表對方的狀態"
}


@dataclass
class LiurenKe:
    """六壬課"""
    position: str         # 一課/二課/三課/四課
    tiangan: str          # 天干
    dizhi: str            # 地支
    shenjiang: str        # 神將
    meaning: str          # 含義
    
    def to_dict(self) -> Dict:
        return {
            "position": self.position,
            "tiangan": self.tiangan,
            "dizhi": self.dizhi,
            "shenjiang": self.shenjiang,
            "meaning": self.meaning
        }


@dataclass
class SanchuanInfo:
    """三傳資訊"""
    chuchu: LiurenKe      # 初傳
    zhongchuan: LiurenKe  # 中傳
    mochuan: LiurenKe     # 末傳
    pattern: str          # 三傳格局
    
    def to_dict(self) -> Dict:
        return {
            "chuchu": self.chuchu.to_dict(),
            "zhongchuan": self.zhongchuan.to_dict(),
            "mochuan": self.mochuan.to_dict(),
            "pattern": self.pattern
        }


@dataclass
class LiurenPan:
    """六壬盤"""
    day_gan: str          # 日干
    day_zhi: str          # 日支
    hour_zhi: str         # 時支
    sike: List[LiurenKe]  # 四課
    sanchuan: SanchuanInfo  # 三傳
    guiren_zhi: str       # 貴人起位
    field_analysis: str   # 場論分析
    timestamp: datetime
    
    def to_dict(self) -> Dict:
        return {
            "day_gan": self.day_gan,
            "day_zhi": self.day_zhi,
            "hour_zhi": self.hour_zhi,
            "sike": [k.to_dict() for k in self.sike],
            "sanchuan": self.sanchuan.to_dict(),
            "guiren_zhi": self.guiren_zhi,
            "field_analysis": self.field_analysis,
            "timestamp": self.timestamp.isoformat()
        }


class LiurenEngine:
    """
    六壬神課引擎
    
    D3: 四課三傳 + 十二神將 + 場論整合
    
    📚 知識點：
        六壬 = 事態發展的動態模擬
        四課 = 人我雙方的狀態
        三傳 = 事件發展的三個階段
    """
    
    VERSION = "1.0.0"
    
    # 天乙貴人起法
    GUIREN_TABLE = {
        "甲": ("丑", "未"), "戊": ("丑", "未"), "庚": ("丑", "未"),
        "乙": ("子", "申"), "己": ("子", "申"),
        "丙": ("亥", "酉"), "丁": ("亥", "酉"),
        "壬": ("卯", "巳"), "癸": ("卯", "巳"),
        "辛": ("午", "寅")
    }
    
    def __init__(self):
        pass
    
    def get_guiren_zhi(self, day_gan: str, is_day: bool = True) -> str:
        """
        獲取貴人起位
        
        📚 知識點：
            晝占用晝貴，夜占用夜貴
            貴人所臨之位為六壬盤的起點
        """
        pair = self.GUIREN_TABLE.get(day_gan, ("丑", "未"))
        return pair[0] if is_day else pair[1]
    
    def get_shenjiang(self, dizhi: str) -> Tuple[str, str]:
        """獲取神將"""
        return SHIER_SHENJIANG.get(dizhi, ("未知", ""))
    
    def _get_shang_shen(self, base_zhi: str, target_zhi: str) -> str:
        """
        獲取上神（加臨）
        
        📚 知識點：
            以月將加時，順數至日支上神
        """
        # 簡化：直接用相對位置
        base_idx = DIZHI.index(base_zhi)
        target_idx = DIZHI.index(target_zhi)
        diff = (target_idx - base_idx) % 12
        return DIZHI[(base_idx + diff) % 12]
    
    def create_pan(
        self,
        day_gan: str,
        day_zhi: str,
        hour_zhi: str,
        is_day: bool = True
    ) -> LiurenPan:
        """
        創建六壬盤
        
        📚 知識點：
            排盤步驟：
            1. 定貴人起位
            2. 排天盤（月將加時）
            3. 排四課（日上/日下/辰上/辰下）
            4. 取三傳（初傳/中傳/末傳）
        """
        # 貴人起位
        guiren_zhi = self.get_guiren_zhi(day_gan, is_day)
        
        # 排四課（簡化版）
        sike = []
        
        # 一課：日上神
        ke1_zhi = self._get_shang_shen(hour_zhi, day_zhi)
        shenjiang1 = self.get_shenjiang(ke1_zhi)
        sike.append(LiurenKe(
            position="一課",
            tiangan=day_gan,
            dizhi=ke1_zhi,
            shenjiang=shenjiang1[0],
            meaning=f"日上神{ke1_zhi}：{SIKE_DESC['一課']}"
        ))
        
        # 二課：一課上神
        ke2_zhi = self._get_shang_shen(hour_zhi, ke1_zhi)
        shenjiang2 = self.get_shenjiang(ke2_zhi)
        sike.append(LiurenKe(
            position="二課",
            tiangan=TIANGAN[(TIANGAN.index(day_gan) + 6) % 10],  # 簡化
            dizhi=ke2_zhi,
            shenjiang=shenjiang2[0],
            meaning=f"日下神{ke2_zhi}：{SIKE_DESC['二課']}"
        ))
        
        # 三課：辰上神
        ke3_zhi = self._get_shang_shen(hour_zhi, day_zhi)
        shenjiang3 = self.get_shenjiang(ke3_zhi)
        sike.append(LiurenKe(
            position="三課",
            tiangan=TIANGAN[(DIZHI.index(day_zhi)) % 10],
            dizhi=ke3_zhi,
            shenjiang=shenjiang3[0],
            meaning=f"辰上神{ke3_zhi}：{SIKE_DESC['三課']}"
        ))
        
        # 四課：三課上神
        ke4_zhi = self._get_shang_shen(hour_zhi, ke3_zhi)
        shenjiang4 = self.get_shenjiang(ke4_zhi)
        sike.append(LiurenKe(
            position="四課",
            tiangan=TIANGAN[(DIZHI.index(day_zhi) + 6) % 10],
            dizhi=ke4_zhi,
            shenjiang=shenjiang4[0],
            meaning=f"辰下神{ke4_zhi}：{SIKE_DESC['四課']}"
        ))
        
        # 三傳（簡化：取一二三課）
        sanchuan = SanchuanInfo(
            chuchu=sike[0],
            zhongchuan=sike[1],
            mochuan=sike[2],
            pattern=self._determine_pattern(sike)
        )
        
        # 場論分析
        field_analysis = self._field_analysis(sike, sanchuan)
        
        return LiurenPan(
            day_gan=day_gan,
            day_zhi=day_zhi,
            hour_zhi=hour_zhi,
            sike=sike,
            sanchuan=sanchuan,
            guiren_zhi=guiren_zhi,
            field_analysis=field_analysis,
            timestamp=datetime.now()
        )
    
    def _determine_pattern(self, sike: List[LiurenKe]) -> str:
        """判斷三傳格局"""
        # 簡化判斷
        zhis = [k.dizhi for k in sike]
        
        # 檢查伏吟（四課同支）
        if len(set(zhis)) == 1:
            return "伏吟課：事緩難動，宜靜待"
        
        # 檢查反吟（沖）
        chong_pairs = [("子", "午"), ("丑", "未"), ("寅", "申"), 
                       ("卯", "酉"), ("辰", "戌"), ("巳", "亥")]
        for z1, z2 in [(zhis[0], zhis[2]), (zhis[1], zhis[3])]:
            if (z1, z2) in chong_pairs or (z2, z1) in chong_pairs:
                return "反吟課：反覆無常，事多變動"
        
        return "正常課式"
    
    def _field_analysis(self, sike: List[LiurenKe], sanchuan: SanchuanInfo) -> str:
        """場論分析"""
        # 分析神將分佈
        good_shen = ["貴人", "青龍", "太常", "六合"]
        bad_shen = ["白虎", "玄武", "騰蛇", "勾陳"]
        
        shen_list = [k.shenjiang for k in sike]
        good_count = sum(1 for s in shen_list if s in good_shen)
        bad_count = sum(1 for s in shen_list if s in bad_shen)
        
        if good_count > bad_count:
            return f"場態偏吉：吉神{good_count}個 > 凶神{bad_count}個，事態向好發展"
        elif bad_count > good_count:
            return f"場態偏凶：凶神{bad_count}個 > 吉神{good_count}個，需謹慎行事"
        else:
            return "場態中性：吉凶參半，視具體問題而定"


# =============================================================================
# D4: 風水羅盤 (基礎版)
# =============================================================================

# 二十四山
ERSHISI_SHAN = [
    ("壬", "北", "水", 337.5, 352.5),
    ("子", "北", "水", 352.5, 7.5),
    ("癸", "北", "水", 7.5, 22.5),
    ("丑", "東北", "土", 22.5, 37.5),
    ("艮", "東北", "土", 37.5, 52.5),
    ("寅", "東北", "木", 52.5, 67.5),
    ("甲", "東", "木", 67.5, 82.5),
    ("卯", "東", "木", 82.5, 97.5),
    ("乙", "東", "木", 97.5, 112.5),
    ("辰", "東南", "土", 112.5, 127.5),
    ("巽", "東南", "木", 127.5, 142.5),
    ("巳", "東南", "火", 142.5, 157.5),
    ("丙", "南", "火", 157.5, 172.5),
    ("午", "南", "火", 172.5, 187.5),
    ("丁", "南", "火", 187.5, 202.5),
    ("未", "西南", "土", 202.5, 217.5),
    ("坤", "西南", "土", 217.5, 232.5),
    ("申", "西南", "金", 232.5, 247.5),
    ("庚", "西", "金", 247.5, 262.5),
    ("酉", "西", "金", 262.5, 277.5),
    ("辛", "西", "金", 277.5, 292.5),
    ("戌", "西北", "土", 292.5, 307.5),
    ("乾", "西北", "金", 307.5, 322.5),
    ("亥", "西北", "水", 322.5, 337.5),
]

# 三元九運
SANYUAN_JIUYUN = {
    # 下元
    7: {"years": (1984, 2003), "name": "七運", "xing": "兌", "element": "金"},
    8: {"years": (2004, 2023), "name": "八運", "xing": "艮", "element": "土"},
    9: {"years": (2024, 2043), "name": "九運", "xing": "離", "element": "火"},
    # 上元
    1: {"years": (2044, 2063), "name": "一運", "xing": "坎", "element": "水"},
    2: {"years": (2064, 2083), "name": "二運", "xing": "坤", "element": "土"},
    3: {"years": (2084, 2103), "name": "三運", "xing": "震", "element": "木"},
}


@dataclass
class FengshuiDirection:
    """風水方位"""
    shan: str             # 山 (坐山)
    xiang: str            # 向 (朝向)
    shan_wuxing: str      # 坐山五行
    xiang_wuxing: str     # 朝向五行
    shan_direction: str   # 坐山方位
    xiang_direction: str  # 朝向方位
    current_yun: int      # 當運
    assessment: str       # 評估
    
    def to_dict(self) -> Dict:
        return {
            "shan": self.shan,
            "xiang": self.xiang,
            "shan_wuxing": self.shan_wuxing,
            "xiang_wuxing": self.xiang_wuxing,
            "shan_direction": self.shan_direction,
            "xiang_direction": self.xiang_direction,
            "current_yun": self.current_yun,
            "assessment": self.assessment
        }


class FengshuiEngine:
    """
    風水羅盤引擎 (基礎版)
    
    D4: 二十四山 + 三元九運 + 場論對應
    
    📚 知識點：
        風水 = 空間場的能量布局
        坐山朝向 = 場的主軸定位
        三元九運 = 時間場的週期節奏
    """
    
    VERSION = "1.0.0"
    
    def __init__(self):
        pass
    
    def get_current_yun(self, year: int = None) -> int:
        """獲取當前運"""
        if year is None:
            year = datetime.now().year
        
        for yun, info in SANYUAN_JIUYUN.items():
            start, end = info["years"]
            if start <= year <= end:
                return yun
        return 9  # 默認九運
    
    def degree_to_shan(self, degree: float) -> Tuple[str, str, str]:
        """
        角度轉二十四山
        
        Returns: (山名, 方位, 五行)
        """
        degree = degree % 360
        
        for shan, direction, wuxing, start, end in ERSHISI_SHAN:
            if start <= degree < end or (start > end and (degree >= start or degree < end)):
                return shan, direction, wuxing
        
        return "子", "北", "水"
    
    def analyze_direction(
        self,
        shan_degree: float,
        year: int = None
    ) -> FengshuiDirection:
        """
        分析坐向
        
        📚 知識點：
            坐山 = 建築背靠方向
            朝向 = 建築面對方向 (坐山 + 180°)
        """
        if year is None:
            year = datetime.now().year
        
        # 坐山
        shan, shan_dir, shan_wx = self.degree_to_shan(shan_degree)
        
        # 朝向 (對面)
        xiang_degree = (shan_degree + 180) % 360
        xiang, xiang_dir, xiang_wx = self.degree_to_shan(xiang_degree)
        
        # 當運
        current_yun = self.get_current_yun(year)
        yun_info = SANYUAN_JIUYUN.get(current_yun, {})
        
        # 評估
        assessment = self._assess_direction(shan_wx, xiang_wx, current_yun)
        
        return FengshuiDirection(
            shan=shan,
            xiang=xiang,
            shan_wuxing=shan_wx,
            xiang_wuxing=xiang_wx,
            shan_direction=shan_dir,
            xiang_direction=xiang_dir,
            current_yun=current_yun,
            assessment=assessment
        )
    
    def _assess_direction(self, shan_wx: str, xiang_wx: str, yun: int) -> str:
        """評估坐向"""
        yun_info = SANYUAN_JIUYUN.get(yun, {})
        yun_element = yun_info.get("element", "")
        
        WUXING_SHENG = {"木": "火", "火": "土", "土": "金", "金": "水", "水": "木"}
        
        # 與當運五行關係
        if shan_wx == yun_element:
            assessment = f"坐山{shan_wx}與當運{yun}運{yun_element}同類，得運旺氣"
        elif WUXING_SHENG.get(yun_element) == shan_wx:
            assessment = f"當運{yun_element}生坐山{shan_wx}，有利發展"
        elif WUXING_SHENG.get(shan_wx) == yun_element:
            assessment = f"坐山{shan_wx}生當運{yun_element}，耗氣但順勢"
        else:
            assessment = f"坐山{shan_wx}與當運{yun_element}關係一般，需其他因素調和"
        
        return assessment
    
    def get_field_interpretation(self, direction: FengshuiDirection) -> Dict:
        """場論解讀"""
        return {
            "spatial_field": f"空間場定位：坐{direction.shan}朝{direction.xiang}",
            "energy_flow": f"能量流向：從{direction.shan_direction}向{direction.xiang_direction}",
            "temporal_match": f"時間場配合：{direction.current_yun}運 ({SANYUAN_JIUYUN.get(direction.current_yun, {}).get('xing', '')}卦當令)",
            "overall": direction.assessment
        }


# =============================================================================
# 統一 API
# =============================================================================

class MingshuAdvancedAPI:
    """
    進階術數統一 API
    
    整合 D1-D4
    """
    
    VERSION = "1.0.0"
    
    def __init__(self):
        self.ziwei_adv = ZiweiAdvancedEngine()
        self.qimen = QimenEngine()
        self.liuren = LiurenEngine()
        self.fengshui = FengshuiEngine()
    
    # ===== D1: 紫微四化 =====
    
    def get_natal_sihua(self, year_gan: str, star_positions: Dict = None) -> Dict:
        """本命四化"""
        results = self.ziwei_adv.analyze_natal_sihua(year_gan, star_positions)
        return {"success": True, "data": [r.to_dict() for r in results]}
    
    def get_feixing(self, source_gong: str, gong_gan: str, star_positions: Dict = None) -> Dict:
        """飛星分析"""
        result = self.ziwei_adv.analyze_feixing(source_gong, gong_gan, star_positions)
        return {"success": True, "data": result.to_dict()}
    
    def get_zihua(self, gong: str, gong_gan: str, stars_in_gong: List[str]) -> Dict:
        """自化分析"""
        result = self.ziwei_adv.analyze_zihua(gong, gong_gan, stars_in_gong)
        return {"success": True, "data": result}
    
    # ===== D2: 奇門遁甲 =====
    
    def get_qimen_pan(self, dt: datetime = None) -> Dict:
        """奇門排盤"""
        pan = self.qimen.create_pan(dt)
        interpretation = self.qimen.get_field_interpretation(pan)
        return {
            "success": True,
            "data": {
                "pan": pan.to_dict(),
                "interpretation": interpretation
            }
        }
    
    # ===== D3: 六壬神課 =====
    
    def get_liuren_pan(self, day_gan: str, day_zhi: str, hour_zhi: str, is_day: bool = True) -> Dict:
        """六壬起課"""
        pan = self.liuren.create_pan(day_gan, day_zhi, hour_zhi, is_day)
        return {"success": True, "data": pan.to_dict()}
    
    # ===== D4: 風水羅盤 =====
    
    def get_fengshui_direction(self, degree: float, year: int = None) -> Dict:
        """風水方位分析"""
        direction = self.fengshui.analyze_direction(degree, year)
        interpretation = self.fengshui.get_field_interpretation(direction)
        return {
            "success": True,
            "data": {
                "direction": direction.to_dict(),
                "interpretation": interpretation
            }
        }


# =============================================================================
# CLI 入口
# =============================================================================

def main():
    """CLI 入口"""
    print("=" * 70)
    print("北斗命數 進階術數 v1.0")
    print("D1 紫微四化 | D2 奇門遁甲 | D3 六壬神課 | D4 風水羅盤")
    print("執行星：織明 × 理樞 × 澄韻 × 流祇 × 澄書")
    print("=" * 70)
    
    api = MingshuAdvancedAPI()
    
    # D1: 紫微四化
    print("\n【D1】紫微四化 - 癸年生人")
    result = api.get_natal_sihua("癸")
    for s in result["data"]:
        print(f"  {s['type']}: {s['star']} → {s['meaning'][:30]}...")
    
    # D1: 飛星
    print("\n【D1】飛星分析 - 命宮天干甲")
    result = api.get_feixing("命宮", "甲")
    print(f"  起飛宮: {result['data']['source_gong']}")
    print(f"  場論: {result['data']['field_analysis']}")
    
    # D2: 奇門遁甲
    print("\n【D2】奇門遁甲 - 當下時盤")
    result = api.get_qimen_pan()
    pan = result["data"]["pan"]
    print(f"  {'陽遁' if pan['yang_dun'] else '陰遁'}{pan['ju']}局")
    print(f"  值符: {pan['duty_gan']} | 值使: {pan['duty_men']}")
    print(f"  格局: {', '.join(pan['geju'][:2])}")
    interp = result["data"]["interpretation"]
    print(f"  建議: {interp['action_advice']}")
    
    # D3: 六壬神課
    print("\n【D3】六壬神課 - 癸丑日卯時")
    result = api.get_liuren_pan("癸", "丑", "卯", True)
    pan = result["data"]
    print(f"  日干支: {pan['day_gan']}{pan['day_zhi']}")
    print(f"  貴人起: {pan['guiren_zhi']}")
    print(f"  四課神將: {', '.join([k['shenjiang'] for k in pan['sike']])}")
    print(f"  場論: {pan['field_analysis']}")
    
    # D4: 風水羅盤
    print("\n【D4】風水羅盤 - 坐北朝南 (0度)")
    result = api.get_fengshui_direction(0)
    dir_data = result["data"]["direction"]
    print(f"  坐山: {dir_data['shan']} ({dir_data['shan_direction']}方 {dir_data['shan_wuxing']})")
    print(f"  朝向: {dir_data['xiang']} ({dir_data['xiang_direction']}方 {dir_data['xiang_wuxing']})")
    print(f"  當運: {dir_data['current_yun']}運")
    print(f"  評估: {dir_data['assessment']}")
    
    # 統計
    print("\n" + "=" * 70)
    with open(__file__, 'r') as f:
        lines = len(f.read().split('\n'))
    print(f"模組行數: {lines} 行")
    print("=" * 70)


if __name__ == "__main__":
    main()


# =============================================================================
# 📚 知識點總結
# =============================================================================
"""
【D1 紫微四化】

四化類型：
- 化祿：財富、機會、增益 → 吸引資源
- 化權：權力、掌控、主導 → 主動出擊
- 化科：名聲、考試、文書 → 貴人助力
- 化忌：阻礙、執著、業力 → 需要面對

飛星機制：
- 宮干四化 = 該宮的能量投射
- 自化 = 能量在本宮循環
- 場論視角：四化是場的能量轉換模式

【D2 奇門遁甲】

三盤四層：
- 天盤：九星
- 人盤：八門
- 地盤：九宮
- 神盤：八神

場論視角：
- 奇門 = 時空場的戰略層面
- 三奇 = 場的三種吉利能量（乙丙丁）
- 八門 = 場的八種行動向量

【D3 六壬神課】

四課三傳：
- 一課（日上）：自己
- 二課（日下）：行動
- 三課（辰上）：對方
- 四課（辰下）：對方狀態
- 三傳：事態發展三階段

場論視角：
- 六壬 = 事態場的動態模擬
- 十二神將 = 場的十二種能量態

【D4 風水羅盤】

二十四山：
- 八卦 × 3 = 24 方位
- 每山 15 度

三元九運：
- 上元：1-3 運
- 中元：4-6 運
- 下元：7-9 運
- 每運 20 年

場論視角：
- 風水 = 空間場的能量布局
- 坐向 = 場的主軸定位
- 三元九運 = 時間場的節奏週期

【織明語錄】
- 「進階術數 = 場論多視角的深度探測」
- 「四化 = 能量轉化的四種模式」
- 「奇門 = 時空場的戰略視角」
- 「六壬 = 事態發展的動態模擬」
- 「風水 = 空間場的能量布局」
"""
