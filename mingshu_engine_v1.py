#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
mingshu_engine_v1.py - 北斗統一命數引擎 v1.0
=============================================
北斗七星文創 × 織明

XTF⁸ 任務：M1_統一命數引擎
執行星：織明(設計) × 理樞(整合) × 澄書(記錄)

核心理念：
    命數 = 場的時間切片
    八字 = 先天場態
    紫微 = 宮位場網
    易經 = 當下場態
    場論 = 統一語言

整合 PYLIB 模組：
    - bazi_engine / bazi_advanced (八字)
    - ziwei_engine_v1 / ziwei_advanced / ziwei_liunian (紫微)
    - yijing_qigua_engine_v2 / yijing_jiegua_v2 (易經)
    - meihua_engine (梅花)
    - qimen_engine_v1 (奇門)
    - field_engine_v1 (場論)
    - wuxing_core / wuxing_analyzer (五行)

📚 知識點：
    「命數非裁決律」：術數之間不互相裁決
    「場態合成」：多術數 → 場論維度同構收斂
    「事實/推理/不知」：嚴守認知邊界
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple, Any, Union
from enum import Enum
from datetime import datetime, date
from abc import ABC, abstractmethod
import json


# =============================================================================
# L0: 常量與枚舉
# =============================================================================

class Gender(Enum):
    MALE = "M"
    FEMALE = "F"


class CalendarType(Enum):
    LUNAR = "lunar"      # 農曆
    SOLAR = "solar"      # 陽曆


class ChartType(Enum):
    BAZI = "八字"
    ZIWEI = "紫微"
    YIJING = "易經"
    MEIHUA = "梅花"
    QIMEN = "奇門"


# 天干地支
TIANGAN = ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"]
DIZHI = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]

# 五行
WUXING = ["木", "火", "土", "金", "水"]
TIANGAN_WUXING = {
    "甲": "木", "乙": "木", "丙": "火", "丁": "火", "戊": "土",
    "己": "土", "庚": "金", "辛": "金", "壬": "水", "癸": "水"
}
DIZHI_WUXING = {
    "子": "水", "丑": "土", "寅": "木", "卯": "木", "辰": "土", "巳": "火",
    "午": "火", "未": "土", "申": "金", "酉": "金", "戌": "土", "亥": "水"
}

# 十神
SHISHEN = ["比肩", "劫財", "食神", "傷官", "偏財", "正財", "七殺", "正官", "偏印", "正印"]


# =============================================================================
# L1: 核心數據結構
# =============================================================================

@dataclass
class BirthInfo:
    """
    出生資訊（統一輸入格式）
    
    📚 知識點：
        命數的起點是出生時間
        時間 = 場的錨點
    """
    year: int
    month: int
    day: int
    hour: int
    minute: int = 0
    gender: Gender = Gender.MALE
    calendar: CalendarType = CalendarType.LUNAR
    timezone: str = "Asia/Taipei"
    name: str = ""
    
    def to_dict(self) -> Dict:
        return {
            "year": self.year,
            "month": self.month,
            "day": self.day,
            "hour": self.hour,
            "minute": self.minute,
            "gender": self.gender.value,
            "calendar": self.calendar.value,
            "timezone": self.timezone,
            "name": self.name
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'BirthInfo':
        return cls(
            year=data["year"],
            month=data["month"],
            day=data["day"],
            hour=data["hour"],
            minute=data.get("minute", 0),
            gender=Gender(data.get("gender", "M")),
            calendar=CalendarType(data.get("calendar", "lunar")),
            timezone=data.get("timezone", "Asia/Taipei"),
            name=data.get("name", "")
        )


@dataclass
class Pillar:
    """四柱之一柱"""
    gan: str    # 天干
    zhi: str    # 地支
    
    @property
    def ganzhi(self) -> str:
        return f"{self.gan}{self.zhi}"
    
    @property
    def gan_wuxing(self) -> str:
        return TIANGAN_WUXING.get(self.gan, "")
    
    @property
    def zhi_wuxing(self) -> str:
        return DIZHI_WUXING.get(self.zhi, "")
    
    def to_dict(self) -> Dict:
        return {
            "gan": self.gan,
            "zhi": self.zhi,
            "ganzhi": self.ganzhi,
            "gan_wuxing": self.gan_wuxing,
            "zhi_wuxing": self.zhi_wuxing
        }


@dataclass
class BaziChart:
    """
    八字命盤
    
    📚 知識點：
        四柱 = 年月日時
        日主 = 命主核心
        十神 = 六親關係
    """
    year_pillar: Pillar
    month_pillar: Pillar
    day_pillar: Pillar
    hour_pillar: Pillar
    
    @property
    def day_master(self) -> str:
        """日主（日干）"""
        return self.day_pillar.gan
    
    @property
    def pillars(self) -> List[Pillar]:
        return [self.year_pillar, self.month_pillar, 
                self.day_pillar, self.hour_pillar]
    
    @property
    def bazi_string(self) -> str:
        """八字字符串"""
        return " ".join(p.ganzhi for p in self.pillars)
    
    def get_wuxing_count(self) -> Dict[str, int]:
        """五行統計"""
        count = {wx: 0 for wx in WUXING}
        for p in self.pillars:
            if p.gan_wuxing:
                count[p.gan_wuxing] += 1
            if p.zhi_wuxing:
                count[p.zhi_wuxing] += 1
        return count
    
    def get_wuxing_profile(self) -> Dict[str, float]:
        """五行分布（正規化）"""
        count = self.get_wuxing_count()
        total = sum(count.values())
        if total == 0:
            return {wx: 0.2 for wx in WUXING}
        return {wx: cnt / total for wx, cnt in count.items()}
    
    def to_dict(self) -> Dict:
        return {
            "year": self.year_pillar.to_dict(),
            "month": self.month_pillar.to_dict(),
            "day": self.day_pillar.to_dict(),
            "hour": self.hour_pillar.to_dict(),
            "day_master": self.day_master,
            "bazi_string": self.bazi_string,
            "wuxing_count": self.get_wuxing_count(),
            "wuxing_profile": self.get_wuxing_profile()
        }


@dataclass
class ZiweiPalace:
    """紫微宮位"""
    name: str           # 宮名
    position: int       # 位置 (1-12)
    main_stars: List[str] = field(default_factory=list)  # 主星
    aux_stars: List[str] = field(default_factory=list)   # 輔星
    sihua: List[str] = field(default_factory=list)       # 四化
    
    def to_dict(self) -> Dict:
        return {
            "name": self.name,
            "position": self.position,
            "main_stars": self.main_stars,
            "aux_stars": self.aux_stars,
            "sihua": self.sihua
        }


@dataclass
class ZiweiChart:
    """
    紫微命盤
    
    📚 知識點：
        十二宮 = 人生十二面向
        主星 = 宮位主導力量
        四化 = 年干動態影響
    """
    ming_gong: int      # 命宮位置
    shen_gong: int      # 身宮位置
    palaces: List[ZiweiPalace] = field(default_factory=list)
    
    PALACE_NAMES = [
        "命宮", "兄弟", "夫妻", "子女", "財帛", "疾厄",
        "遷移", "交友", "官祿", "田宅", "福德", "父母"
    ]
    
    def get_palace(self, name: str) -> Optional[ZiweiPalace]:
        """按名稱獲取宮位"""
        for p in self.palaces:
            if p.name == name:
                return p
        return None
    
    def to_dict(self) -> Dict:
        return {
            "ming_gong": self.ming_gong,
            "shen_gong": self.shen_gong,
            "palaces": [p.to_dict() for p in self.palaces]
        }


@dataclass
class GuaResult:
    """
    卦象結果
    
    📚 知識點：
        卦 = 6-bit 狀態機
        動爻 = 變化觸發點
        變卦 = 趨勢指向
    """
    ben_gua: str        # 本卦名
    ben_gua_num: int    # 本卦數 (1-64)
    bian_gua: str       # 變卦名
    bian_gua_num: int   # 變卦數
    dong_yao: List[int] # 動爻列表 (1-6)
    method: str         # 起卦方法
    
    @property
    def has_bian(self) -> bool:
        """是否有變卦"""
        return len(self.dong_yao) > 0
    
    def to_dict(self) -> Dict:
        return {
            "ben_gua": self.ben_gua,
            "ben_gua_num": self.ben_gua_num,
            "bian_gua": self.bian_gua,
            "bian_gua_num": self.bian_gua_num,
            "dong_yao": self.dong_yao,
            "method": self.method,
            "has_bian": self.has_bian
        }


@dataclass
class FieldState:
    """場態（從 field_engine_v1 簡化引入）"""
    coherence: float = 0.0
    friction: float = 0.0
    volatility: float = 0.0
    sustainability: float = 0.5
    triggers: List[str] = field(default_factory=list)
    advice: str = ""
    source: str = ""
    
    @property
    def field_score(self) -> float:
        base = (self.coherence + 1) / 2 * 40
        friction_penalty = self.friction * 20
        volatility_penalty = self.volatility * 20
        sustain_bonus = self.sustainability * 20
        return max(0, min(100, base - friction_penalty - volatility_penalty + sustain_bonus))
    
    def to_dict(self) -> Dict:
        return {
            "coherence": round(self.coherence, 3),
            "friction": round(self.friction, 3),
            "volatility": round(self.volatility, 3),
            "sustainability": round(self.sustainability, 3),
            "field_score": round(self.field_score, 1),
            "triggers": self.triggers,
            "advice": self.advice,
            "source": self.source
        }


@dataclass
class MingshuResult:
    """
    命數綜合結果
    
    📚 知識點：
        多術數整合 = 場論維度同構收斂
        不互相裁決 = 術數非裁決律
    """
    birth_info: BirthInfo
    bazi: Optional[BaziChart] = None
    ziwei: Optional[ZiweiChart] = None
    yijing: Optional[GuaResult] = None
    field_state: Optional[FieldState] = None
    analysis: Dict = field(default_factory=dict)
    advice: List[str] = field(default_factory=list)
    generated_at: str = ""
    
    def __post_init__(self):
        if not self.generated_at:
            self.generated_at = datetime.now().isoformat()
    
    def to_dict(self) -> Dict:
        return {
            "birth_info": self.birth_info.to_dict(),
            "bazi": self.bazi.to_dict() if self.bazi else None,
            "ziwei": self.ziwei.to_dict() if self.ziwei else None,
            "yijing": self.yijing.to_dict() if self.yijing else None,
            "field_state": self.field_state.to_dict() if self.field_state else None,
            "analysis": self.analysis,
            "advice": self.advice,
            "generated_at": self.generated_at
        }


# =============================================================================
# L2: 排盤計算器
# =============================================================================

class BaziCalculator:
    """
    八字排盤計算器
    
    📚 知識點：
        年柱 = 立春分界
        月柱 = 節氣分界
        日柱 = 干支紀日
        時柱 = 時辰換算
    """
    
    # 六十甲子表
    JIAZI_TABLE = [
        f"{TIANGAN[i % 10]}{DIZHI[i % 12]}" 
        for i in range(60)
    ]
    
    def __init__(self):
        pass
    
    def calculate(self, birth: BirthInfo) -> BaziChart:
        """計算八字命盤"""
        # 簡化計算（實際需要精確的節氣計算）
        year_gz = self._calc_year_pillar(birth.year)
        month_gz = self._calc_month_pillar(birth.year, birth.month)
        day_gz = self._calc_day_pillar(birth.year, birth.month, birth.day)
        hour_gz = self._calc_hour_pillar(day_gz[0], birth.hour)
        
        return BaziChart(
            year_pillar=Pillar(year_gz[0], year_gz[1]),
            month_pillar=Pillar(month_gz[0], month_gz[1]),
            day_pillar=Pillar(day_gz[0], day_gz[1]),
            hour_pillar=Pillar(hour_gz[0], hour_gz[1])
        )
    
    def _calc_year_pillar(self, year: int) -> Tuple[str, str]:
        """年柱計算（簡化版，以立春為界）"""
        # 1984年為甲子年
        base_year = 1984
        idx = (year - base_year) % 60
        if idx < 0:
            idx += 60
        gan_idx = idx % 10
        zhi_idx = idx % 12
        return (TIANGAN[gan_idx], DIZHI[zhi_idx])
    
    def _calc_month_pillar(self, year: int, month: int) -> Tuple[str, str]:
        """月柱計算（簡化版）"""
        # 月支固定：正月=寅，二月=卯...
        zhi_idx = (month + 1) % 12  # 正月對應寅(2)
        
        # 月干由年干推算（五虎遁）
        year_gan = self._calc_year_pillar(year)[0]
        year_gan_idx = TIANGAN.index(year_gan)
        
        # 五虎遁規則
        base_gan = {
            0: 2, 1: 2,   # 甲己年起丙寅
            2: 4, 3: 4,   # 乙庚年起戊寅
            4: 6, 5: 6,   # 丙辛年起庚寅
            6: 8, 7: 8,   # 丁壬年起壬寅
            8: 0, 9: 0    # 戊癸年起甲寅
        }
        month_gan_base = base_gan.get(year_gan_idx, 0)
        gan_idx = (month_gan_base + month - 1) % 10
        
        return (TIANGAN[gan_idx], DIZHI[zhi_idx])
    
    def _calc_day_pillar(self, year: int, month: int, day: int) -> Tuple[str, str]:
        """日柱計算（簡化版，使用公式）"""
        # 使用儒略日計算
        if month <= 2:
            year -= 1
            month += 12
        
        a = year // 100
        b = 2 - a + a // 4
        jd = int(365.25 * (year + 4716)) + int(30.6001 * (month + 1)) + day + b - 1524
        
        # 干支紀日（1984年1月1日為甲子日）
        base_jd = 2445336  # 1984-01-01
        diff = jd - base_jd
        idx = diff % 60
        if idx < 0:
            idx += 60
        
        return (TIANGAN[idx % 10], DIZHI[idx % 12])
    
    def _calc_hour_pillar(self, day_gan: str, hour: int) -> Tuple[str, str]:
        """時柱計算"""
        # 時支：子時(23-1)=0, 丑時(1-3)=1, ...
        zhi_idx = ((hour + 1) // 2) % 12
        
        # 時干由日干推算（五鼠遁）
        day_gan_idx = TIANGAN.index(day_gan)
        base_gan = {
            0: 0, 1: 0,   # 甲己日起甲子
            2: 2, 3: 2,   # 乙庚日起丙子
            4: 4, 5: 4,   # 丙辛日起戊子
            6: 6, 7: 6,   # 丁壬日起庚子
            8: 8, 9: 8    # 戊癸日起壬子
        }
        hour_gan_base = base_gan.get(day_gan_idx, 0)
        gan_idx = (hour_gan_base + zhi_idx) % 10
        
        return (TIANGAN[gan_idx], DIZHI[zhi_idx])


class ZiweiCalculator:
    """
    紫微排盤計算器
    
    📚 知識點：
        命宮 = 出生月時定位
        身宮 = 與命宮相對
        安星 = 依五行局排布
    """
    
    MAIN_STARS = [
        "紫微", "天機", "太陽", "武曲", "天同", "廉貞",
        "天府", "太陰", "貪狼", "巨門", "天相", "天梁", "七殺", "破軍"
    ]
    
    def __init__(self):
        pass
    
    def calculate(self, birth: BirthInfo) -> ZiweiChart:
        """計算紫微命盤"""
        # 命宮位置（簡化計算）
        ming_gong = self._calc_ming_gong(birth.month, birth.hour)
        shen_gong = self._calc_shen_gong(birth.month, birth.hour)
        
        # 初始化十二宮
        palaces = []
        for i in range(12):
            pos = (ming_gong + i - 1) % 12 + 1
            palace = ZiweiPalace(
                name=ZiweiChart.PALACE_NAMES[i],
                position=pos
            )
            palaces.append(palace)
        
        # 安主星（簡化版）
        self._place_main_stars(palaces, birth)
        
        # 安四化
        self._place_sihua(palaces, birth)
        
        return ZiweiChart(
            ming_gong=ming_gong,
            shen_gong=shen_gong,
            palaces=palaces
        )
    
    def _calc_ming_gong(self, month: int, hour: int) -> int:
        """命宮計算"""
        # 命宮 = 寅宮起正月，逆數至生月，再由生月順數至生時
        zhi_idx = ((hour + 1) // 2) % 12  # 時辰
        ming = (14 - month + zhi_idx) % 12
        return ming + 1 if ming >= 0 else ming + 13
    
    def _calc_shen_gong(self, month: int, hour: int) -> int:
        """身宮計算"""
        zhi_idx = ((hour + 1) // 2) % 12
        shen = (month + zhi_idx + 2) % 12
        return shen + 1 if shen >= 0 else shen + 13
    
    def _place_main_stars(self, palaces: List[ZiweiPalace], birth: BirthInfo):
        """安主星（簡化版）"""
        # 根據出生日決定紫微星位置（簡化）
        ziwei_pos = (birth.day % 12)
        
        # 紫微星系
        ziwei_series = ["紫微", "天機", "太陽", "武曲", "天同", "廉貞"]
        for i, star in enumerate(ziwei_series):
            pos = (ziwei_pos + i * 2) % 12
            for p in palaces:
                if p.position == pos + 1:
                    p.main_stars.append(star)
                    break
        
        # 天府星系
        tianfu_pos = (12 - ziwei_pos) % 12
        tianfu_series = ["天府", "太陰", "貪狼", "巨門", "天相", "天梁", "七殺", "破軍"]
        for i, star in enumerate(tianfu_series):
            pos = (tianfu_pos + i) % 12
            for p in palaces:
                if p.position == pos + 1:
                    p.main_stars.append(star)
                    break
    
    def _place_sihua(self, palaces: List[ZiweiPalace], birth: BirthInfo):
        """安四化（簡化版）"""
        # 根據年干決定四化
        year_gan_idx = (birth.year - 4) % 10
        
        # 四化表（簡化）
        sihua_table = {
            0: [("廉貞", "祿"), ("破軍", "權"), ("武曲", "科"), ("太陽", "忌")],  # 甲
            1: [("天機", "祿"), ("天梁", "權"), ("紫微", "科"), ("太陰", "忌")],  # 乙
            2: [("天同", "祿"), ("天機", "權"), ("文昌", "科"), ("廉貞", "忌")],  # 丙
            3: [("太陰", "祿"), ("天同", "權"), ("天機", "科"), ("巨門", "忌")],  # 丁
            4: [("貪狼", "祿"), ("太陰", "權"), ("右弼", "科"), ("天機", "忌")],  # 戊
            5: [("武曲", "祿"), ("貪狼", "權"), ("天梁", "科"), ("文曲", "忌")],  # 己
            6: [("太陽", "祿"), ("武曲", "權"), ("太陰", "科"), ("天同", "忌")],  # 庚
            7: [("巨門", "祿"), ("太陽", "權"), ("文曲", "科"), ("文昌", "忌")],  # 辛
            8: [("天梁", "祿"), ("紫微", "權"), ("左輔", "科"), ("武曲", "忌")],  # 壬
            9: [("破軍", "祿"), ("巨門", "權"), ("太陰", "科"), ("貪狼", "忌")],  # 癸
        }
        
        sihua_list = sihua_table.get(year_gan_idx, [])
        for star, hua in sihua_list:
            for p in palaces:
                if star in p.main_stars:
                    p.sihua.append(f"{star}化{hua}")
                    break


class YijingCalculator:
    """
    易經起卦計算器
    
    📚 知識點：
        卦 = 6-bit 狀態機
        64卦 = 2^6
        動爻 = flip bit
        變卦 = XOR
    """
    
    BAGUA_NAMES = ["乾", "兌", "離", "震", "巽", "坎", "艮", "坤"]
    
    # 64卦名（上卦×8 + 下卦）
    GUA_NAMES = [
        "乾", "姤", "同人", "遯", "無妄", "訟", "天", "否",
        "履", "兌", "革", "損", "隨", "困", "咸", "萃",
        "大有", "大過", "離", "旅", "噬嗑", "未濟", "賁", "晉",
        "大壯", "恆", "豐", "小過", "震", "解", "豫", "歸妹",
        "小畜", "巽", "家人", "漸", "益", "渙", "中孚", "觀",
        "需", "井", "既濟", "蹇", "屯", "坎", "節", "比",
        "大畜", "蠱", "頤", "剝", "復", "蒙", "艮", "謙",
        "泰", "升", "明夷", "臨", "損", "師", "臨", "坤"
    ]
    
    def __init__(self):
        pass
    
    def qigua_birthday(self, birth: BirthInfo) -> GuaResult:
        """生日起卦"""
        # 上卦 = (年+月+日) % 8
        # 下卦 = (年+月+日+時) % 8
        # 動爻 = (年+月+日+時) % 6 + 1
        
        total1 = birth.year + birth.month + birth.day
        total2 = total1 + birth.hour
        
        shang = total1 % 8
        xia = total2 % 8
        dong = (total2 % 6) + 1
        
        ben_num = shang * 8 + xia
        ben_name = self._get_gua_name(shang, xia)
        
        # 變卦
        bian_shang, bian_xia = self._flip_yao(shang, xia, dong)
        bian_num = bian_shang * 8 + bian_xia
        bian_name = self._get_gua_name(bian_shang, bian_xia)
        
        return GuaResult(
            ben_gua=ben_name,
            ben_gua_num=ben_num,
            bian_gua=bian_name,
            bian_gua_num=bian_num,
            dong_yao=[dong],
            method="生日起卦"
        )
    
    def qigua_time(self, dt: datetime = None) -> GuaResult:
        """時間起卦"""
        if dt is None:
            dt = datetime.now()
        
        # 年月日時數字
        year_num = dt.year
        month_num = dt.month
        day_num = dt.day
        hour_num = dt.hour
        
        total1 = year_num + month_num + day_num
        total2 = total1 + hour_num
        
        shang = total1 % 8
        xia = total2 % 8
        dong = (total2 % 6) + 1
        
        ben_name = self._get_gua_name(shang, xia)
        bian_shang, bian_xia = self._flip_yao(shang, xia, dong)
        bian_name = self._get_gua_name(bian_shang, bian_xia)
        
        return GuaResult(
            ben_gua=ben_name,
            ben_gua_num=shang * 8 + xia,
            bian_gua=bian_name,
            bian_gua_num=bian_shang * 8 + bian_xia,
            dong_yao=[dong],
            method="時間起卦"
        )
    
    def _get_gua_name(self, shang: int, xia: int) -> str:
        """獲取卦名"""
        idx = shang * 8 + xia
        if 0 <= idx < len(self.GUA_NAMES):
            return self.GUA_NAMES[idx]
        return f"卦{idx}"
    
    def _flip_yao(self, shang: int, xia: int, dong: int) -> Tuple[int, int]:
        """翻轉動爻得變卦"""
        # 動爻1-3在下卦，4-6在上卦
        if dong <= 3:
            # 翻轉下卦的第 dong 爻
            bit = 1 << (dong - 1)
            xia = xia ^ bit
        else:
            # 翻轉上卦的第 (dong-3) 爻
            bit = 1 << (dong - 4)
            shang = shang ^ bit
        return (shang % 8, xia % 8)


# =============================================================================
# L3: 分析引擎
# =============================================================================

class BaziAnalyzer:
    """八字分析器"""
    
    def analyze(self, chart: BaziChart) -> Dict:
        """分析八字"""
        result = {
            "day_master": chart.day_master,
            "day_master_wuxing": TIANGAN_WUXING.get(chart.day_master, ""),
            "wuxing_count": chart.get_wuxing_count(),
            "wuxing_profile": chart.get_wuxing_profile(),
            "pattern": self._determine_pattern(chart),
            "strength": self._analyze_strength(chart),
            "yongshen": self._find_yongshen(chart)
        }
        return result
    
    def _determine_pattern(self, chart: BaziChart) -> str:
        """判斷格局（簡化版）"""
        month_zhi = chart.month_pillar.zhi
        # 簡化：根據月令判斷
        patterns = {
            "寅": "印格", "卯": "印格",
            "巳": "食傷格", "午": "食傷格",
            "申": "財格", "酉": "財格",
            "亥": "官殺格", "子": "官殺格"
        }
        return patterns.get(month_zhi, "普通格")
    
    def _analyze_strength(self, chart: BaziChart) -> str:
        """分析日主強弱"""
        day_wx = TIANGAN_WUXING.get(chart.day_master, "")
        profile = chart.get_wuxing_profile()
        
        # 日主五行佔比
        day_wx_ratio = profile.get(day_wx, 0)
        
        # 生扶五行
        sheng_map = {"木": "水", "火": "木", "土": "火", "金": "土", "水": "金"}
        sheng_wx = sheng_map.get(day_wx, "")
        sheng_ratio = profile.get(sheng_wx, 0)
        
        total_support = day_wx_ratio + sheng_ratio
        
        if total_support > 0.5:
            return "身強"
        elif total_support < 0.3:
            return "身弱"
        else:
            return "中和"
    
    def _find_yongshen(self, chart: BaziChart) -> str:
        """找用神（簡化版）"""
        strength = self._analyze_strength(chart)
        day_wx = TIANGAN_WUXING.get(chart.day_master, "")
        
        # 身強喜洩耗，身弱喜生扶
        ke_map = {"木": "金", "火": "水", "土": "木", "金": "火", "水": "土"}
        sheng_map = {"木": "水", "火": "木", "土": "火", "金": "土", "水": "金"}
        
        if strength == "身強":
            return ke_map.get(day_wx, "")
        else:
            return sheng_map.get(day_wx, "")


class FieldConverter:
    """場態轉換器"""
    
    def bazi_to_field(self, chart: BaziChart, analysis: Dict) -> FieldState:
        """八字 → 場態"""
        profile = chart.get_wuxing_profile()
        
        # 計算平衡度
        values = list(profile.values())
        avg = sum(values) / len(values)
        variance = sum((v - avg) ** 2 for v in values) / len(values)
        balance = 1 - min(1, variance * 5)
        
        # 場態映射
        coherence = balance * 0.6
        volatility = variance * 2
        
        # 缺失五行增加摩擦
        missing = [wx for wx, v in profile.items() if v < 0.1]
        friction = len(missing) * 0.15
        
        # 身強/身弱影響
        strength = analysis.get("strength", "中和")
        if strength == "身強":
            coherence += 0.2
        elif strength == "身弱":
            friction += 0.1
        
        triggers = []
        if missing:
            triggers.append(f"五行缺{'/'.join(missing)}")
        triggers.append(f"日主{chart.day_master}")
        triggers.append(f"{strength}")
        
        return FieldState(
            coherence=max(-1, min(1, coherence)),
            friction=min(1, friction),
            volatility=min(1, volatility),
            sustainability=balance,
            triggers=triggers,
            source="八字"
        )
    
    def yijing_to_field(self, gua: GuaResult) -> FieldState:
        """易經 → 場態"""
        # 動爻數量影響波動度
        volatility = len(gua.dong_yao) * 0.15
        
        # 卦象判斷（簡化）
        auspicious = ["乾", "泰", "既濟", "大有", "同人"]
        inauspicious = ["坤", "否", "未濟", "剝", "困"]
        
        if gua.ben_gua in auspicious:
            coherence = 0.6
        elif gua.ben_gua in inauspicious:
            coherence = -0.2
        else:
            coherence = 0.3
        
        sustainability = 0.5
        if gua.has_bian:
            sustainability = 0.3
        
        triggers = [f"本卦:{gua.ben_gua}"]
        if gua.dong_yao:
            triggers.append(f"動爻:{gua.dong_yao}")
        if gua.has_bian:
            triggers.append(f"變卦:{gua.bian_gua}")
        
        return FieldState(
            coherence=coherence,
            friction=0.2,
            volatility=min(1, volatility),
            sustainability=sustainability,
            triggers=triggers,
            source="易經"
        )
    
    def merge_fields(self, fields: List[FieldState], weights: List[float] = None) -> FieldState:
        """多場合併"""
        if not fields:
            return FieldState()
        
        if weights is None:
            weights = [1.0] * len(fields)
        
        total_weight = sum(weights)
        if total_weight == 0:
            return FieldState()
        
        coherence = sum(f.coherence * w for f, w in zip(fields, weights)) / total_weight
        friction = sum(f.friction * w for f, w in zip(fields, weights)) / total_weight
        volatility = sum(f.volatility * w for f, w in zip(fields, weights)) / total_weight
        sustainability = sum(f.sustainability * w for f, w in zip(fields, weights)) / total_weight
        
        triggers = []
        for f in fields:
            triggers.extend(f.triggers[:2])
        
        return FieldState(
            coherence=coherence,
            friction=friction,
            volatility=volatility,
            sustainability=sustainability,
            triggers=triggers[:5],
            source="多術數合成"
        )


# =============================================================================
# L4: 統一命數引擎
# =============================================================================

class MingshuEngine:
    """
    北斗統一命數引擎
    
    核心功能：
        1. 統一輸入 (BirthInfo)
        2. 多術數排盤 (八字/紫微/易經)
        3. 場論轉換 (FieldState)
        4. 綜合分析 (MingshuResult)
    
    📚 知識點：
        「命數非裁決律」：術數之間不互相裁決
        「場態合成」：多術數 → 場論維度同構收斂
    """
    
    VERSION = "1.0.0"
    AUTHOR = "北斗七星文創 × 織明"
    
    def __init__(self):
        self.bazi_calc = BaziCalculator()
        self.ziwei_calc = ZiweiCalculator()
        self.yijing_calc = YijingCalculator()
        self.bazi_analyzer = BaziAnalyzer()
        self.field_converter = FieldConverter()
    
    # -------------------------------------------------------------------------
    # 排盤層
    # -------------------------------------------------------------------------
    
    def get_bazi(self, birth: BirthInfo) -> BaziChart:
        """獲取八字命盤"""
        return self.bazi_calc.calculate(birth)
    
    def get_ziwei(self, birth: BirthInfo) -> ZiweiChart:
        """獲取紫微命盤"""
        return self.ziwei_calc.calculate(birth)
    
    def get_yijing(self, birth: BirthInfo) -> GuaResult:
        """獲取易經本命卦"""
        return self.yijing_calc.qigua_birthday(birth)
    
    def get_yijing_now(self) -> GuaResult:
        """獲取當下卦"""
        return self.yijing_calc.qigua_time()
    
    # -------------------------------------------------------------------------
    # 分析層
    # -------------------------------------------------------------------------
    
    def analyze_bazi(self, chart: BaziChart) -> Dict:
        """分析八字"""
        return self.bazi_analyzer.analyze(chart)
    
    def analyze_combined(
        self,
        bazi: BaziChart = None,
        ziwei: ZiweiChart = None,
        yijing: GuaResult = None
    ) -> Dict:
        """
        綜合分析
        
        📚 知識點：
            多術數整合原則：
            1. 不互相裁決
            2. 各取所長
            3. 場論統一
        """
        analysis = {}
        
        if bazi:
            analysis["bazi"] = self.analyze_bazi(bazi)
        
        if ziwei:
            ming_palace = ziwei.get_palace("命宮")
            if ming_palace:
                analysis["ziwei"] = {
                    "ming_gong_stars": ming_palace.main_stars,
                    "ming_gong_sihua": ming_palace.sihua
                }
        
        if yijing:
            analysis["yijing"] = {
                "ben_gua": yijing.ben_gua,
                "bian_gua": yijing.bian_gua if yijing.has_bian else None,
                "dong_yao": yijing.dong_yao
            }
        
        return analysis
    
    # -------------------------------------------------------------------------
    # 場論層
    # -------------------------------------------------------------------------
    
    def to_field_state(
        self,
        bazi: BaziChart = None,
        yijing: GuaResult = None,
        bazi_analysis: Dict = None
    ) -> FieldState:
        """轉換為統一場態"""
        fields = []
        weights = []
        
        if bazi and bazi_analysis:
            bazi_field = self.field_converter.bazi_to_field(bazi, bazi_analysis)
            fields.append(bazi_field)
            weights.append(0.6)
        
        if yijing:
            yijing_field = self.field_converter.yijing_to_field(yijing)
            fields.append(yijing_field)
            weights.append(0.4)
        
        if fields:
            return self.field_converter.merge_fields(fields, weights)
        return FieldState()
    
    # -------------------------------------------------------------------------
    # 報告層
    # -------------------------------------------------------------------------
    
    def generate_basic(self, birth: BirthInfo) -> MingshuResult:
        """生成基礎命盤"""
        bazi = self.get_bazi(birth)
        bazi_analysis = self.analyze_bazi(bazi)
        
        return MingshuResult(
            birth_info=birth,
            bazi=bazi,
            analysis={"bazi": bazi_analysis},
            advice=[f"日主{bazi.day_master}，{bazi_analysis['strength']}"]
        )
    
    def generate_full(self, birth: BirthInfo) -> MingshuResult:
        """
        生成完整命盤
        
        📚 知識點：
            完整分析 = 八字 + 紫微 + 易經 → 場論整合
        """
        # 1. 排盤
        bazi = self.get_bazi(birth)
        ziwei = self.get_ziwei(birth)
        yijing = self.get_yijing(birth)
        
        # 2. 分析
        bazi_analysis = self.analyze_bazi(bazi)
        combined = self.analyze_combined(bazi, ziwei, yijing)
        
        # 3. 場論
        field_state = self.to_field_state(bazi, yijing, bazi_analysis)
        
        # 4. 建議
        advice = self._generate_advice(bazi_analysis, field_state)
        
        return MingshuResult(
            birth_info=birth,
            bazi=bazi,
            ziwei=ziwei,
            yijing=yijing,
            field_state=field_state,
            analysis=combined,
            advice=advice
        )
    
    def _generate_advice(self, bazi_analysis: Dict, field: FieldState) -> List[str]:
        """生成建議"""
        advice = []
        
        # 八字建議
        strength = bazi_analysis.get("strength", "")
        yongshen = bazi_analysis.get("yongshen", "")
        if strength and yongshen:
            advice.append(f"{strength}，用神{yongshen}")
        
        # 場論建議
        if field.field_score > 70:
            advice.append("場態良好，順勢而為")
        elif field.field_score > 50:
            advice.append("場態中性，穩健推進")
        else:
            advice.append("場態待調，修煉自場")
        
        # 觸發點提醒
        for trigger in field.triggers[:2]:
            if "缺" in trigger:
                advice.append(f"注意：{trigger}")
        
        return advice


# =============================================================================
# L4: CLI 入口
# =============================================================================

def main():
    """CLI 入口"""
    print("=" * 60)
    print("北斗統一命數引擎 v1.0")
    print("=" * 60)
    
    engine = MingshuEngine()
    
    # 示例：北斗命盤
    birth = BirthInfo(
        year=1983,
        month=12,
        day=16,
        hour=5,
        gender=Gender.MALE,
        calendar=CalendarType.LUNAR,
        name="北斗"
    )
    
    print(f"\n【輸入】{birth.name}")
    print(f"  農曆 {birth.year}年{birth.month}月{birth.day}日 {birth.hour}時")
    
    # 生成完整命盤
    result = engine.generate_full(birth)
    
    print(f"\n【八字】{result.bazi.bazi_string}")
    print(f"  日主：{result.bazi.day_master}")
    print(f"  五行：{result.bazi.get_wuxing_count()}")
    
    if result.ziwei:
        ming_palace = result.ziwei.get_palace("命宮")
        if ming_palace:
            print(f"\n【紫微命宮】")
            print(f"  主星：{ming_palace.main_stars}")
            print(f"  四化：{ming_palace.sihua}")
    
    if result.yijing:
        print(f"\n【易經本命卦】")
        print(f"  本卦：{result.yijing.ben_gua}")
        print(f"  變卦：{result.yijing.bian_gua}")
        print(f"  動爻：{result.yijing.dong_yao}")
    
    if result.field_state:
        print(f"\n【場態分析】")
        print(f"  場態分：{result.field_state.field_score:.1f}/100")
        print(f"  觸發點：{result.field_state.triggers}")
    
    print(f"\n【建議】")
    for adv in result.advice:
        print(f"  • {adv}")
    
    print("\n" + "=" * 60)
    print("命數非裁決律：術數之間不互相裁決")
    print("=" * 60)


if __name__ == "__main__":
    main()


# =============================================================================
# 📚 知識點總結
# =============================================================================
"""
【統一命數引擎架構】

輸入層 → 排盤層 → 分析層 → 場論層 → 報告層

1. BirthInfo (統一輸入)
   - 年月日時 + 性別 + 曆法 + 時區

2. 排盤層
   - BaziChart (四柱八字)
   - ZiweiChart (紫微十二宮)
   - GuaResult (易經卦象)

3. 分析層
   - 八字：格局/用神/五行強弱
   - 紫微：四化/飛星
   - 易經：本卦/變卦/動爻

4. 場論層
   - FieldState (統一場態)
   - 多術數 → 場論維度同構收斂

5. 報告層
   - 基礎命盤 (bazi only)
   - 完整命盤 (bazi + ziwei + yijing + field)

【核心原則】

1. 命數非裁決律
   - 術數之間不互相裁決
   - 各有側重，互相補充

2. 場態合成
   - 八字 60% + 易經 40% → 合成場態
   - 權重可調整

3. 事實/推理/不知
   - 事實說事實（排盤結果）
   - 推理說推理（分析判斷）
   - 不知說不知（超出範圍）

【織明語錄】
   - 「命數是場的時間切片」
   - 「八字是先天場態，易經是當下場態」
   - 「場論是統一語言」
"""
