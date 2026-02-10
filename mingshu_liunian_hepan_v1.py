#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
mingshu_liunian_hepan_v1.py - 北斗命數流年運勢+人際合盤 v1.0
=============================================================
北斗七星文創 × 織明

XTF⁸ 任務鏈：M5+M6
執行星：織明(設計) × 理樞(整合) × 澄書(記錄) × 流祇(連結)

模組整合：
    M5: LiunianEngine   - 流年運勢 (大運/流年/流月/流日/流時)
    M6: HepanEngine     - 人際合盤 (命盤對比 + 場論相處)

依賴：
    - mingshu_engine_v1.py (統一命數引擎)
    - field_engine_v1.py (場論引擎)
    - PYLIB: ziwei_liunian, wuxing_core

📚 知識點：
    「時運場疊加」：大運×流年×流月×流日×流時 → 綜合場態
    「場接觸四態」：共振/干涉/疊加/邊界
    「相處四模式」：共振場/互補場/平行場/消耗場
    「場增離公式」：1+1>2=聚，1+1<2=離
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple, Any
from enum import Enum
from datetime import datetime, date, timedelta
import json

# 導入本地模組
try:
    from mingshu_engine_v1 import (
        MingshuEngine, MingshuResult, BirthInfo, BaziChart, Pillar,
        FieldState, Gender, CalendarType, TIANGAN, DIZHI, WUXING,
        TIANGAN_WUXING, DIZHI_WUXING
    )
except ImportError:
    # Fallback 常量
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
# 共用常量與枚舉
# =============================================================================

class TimeLayer(Enum):
    """時運層級"""
    DAYUN = "大運"      # 10年
    LIUNIAN = "流年"    # 1年
    LIUYUE = "流月"     # 1月
    LIURI = "流日"      # 1日
    LIUSHI = "流時"     # 2小時


class ContactState(Enum):
    """場接觸狀態"""
    RESONANCE = "共振"      # 頻率相近
    INTERFERENCE = "干涉"   # 頻率相差
    SUPERPOSITION = "疊加"  # 互相影響
    BOUNDARY = "邊界"       # 保持距離


class RelationMode(Enum):
    """相處模式"""
    RESONANCE_FIELD = "共振場"    # 1+1>2
    COMPLEMENTARY = "互補場"      # 剛柔相濟
    PARALLEL = "平行場"           # 互不干涉
    CONSUMING = "消耗場"          # 1+1<2


# 時運層權重
LAYER_WEIGHTS = {
    TimeLayer.DAYUN: 0.35,
    TimeLayer.LIUNIAN: 0.30,
    TimeLayer.LIUYUE: 0.20,
    TimeLayer.LIURI: 0.10,
    TimeLayer.LIUSHI: 0.05
}

# 五行生剋
WUXING_SHENG = {"木": "火", "火": "土", "土": "金", "金": "水", "水": "木"}
WUXING_KE = {"木": "土", "土": "水", "水": "火", "火": "金", "金": "木"}
WUXING_SHENG_BY = {"火": "木", "土": "火", "金": "土", "水": "金", "木": "水"}
WUXING_KE_BY = {"土": "木", "水": "土", "火": "水", "金": "火", "木": "金"}

# 日主關係（十神簡化）
def get_relation(day_master_wx: str, target_wx: str) -> str:
    """獲取日主與目標五行的關係"""
    if day_master_wx == target_wx:
        return "比劫"
    if WUXING_SHENG.get(day_master_wx) == target_wx:
        return "食傷"
    if WUXING_KE.get(day_master_wx) == target_wx:
        return "財星"
    if WUXING_KE.get(target_wx) == day_master_wx:
        return "官殺"
    if WUXING_SHENG.get(target_wx) == day_master_wx:
        return "印星"
    return "中性"


# =============================================================================
# M5: 流年運勢引擎
# =============================================================================

@dataclass
class TimeLayerField:
    """時運層場態"""
    layer: TimeLayer
    ganzhi: str
    gan: str
    zhi: str
    gan_wuxing: str
    zhi_wuxing: str
    relation_to_day: str      # 與日主關係
    field_state: 'FieldState'
    advice: str = ""
    
    def to_dict(self) -> Dict:
        return {
            "layer": self.layer.value,
            "ganzhi": self.ganzhi,
            "gan": self.gan,
            "zhi": self.zhi,
            "gan_wuxing": self.gan_wuxing,
            "zhi_wuxing": self.zhi_wuxing,
            "relation_to_day": self.relation_to_day,
            "field_state": self.field_state.to_dict() if self.field_state else None,
            "advice": self.advice
        }


@dataclass
class LiunianResult:
    """流年運勢結果"""
    birth_info: 'BirthInfo'
    target_date: date
    bazi: 'BaziChart'
    day_master: str
    day_master_wuxing: str
    layers: List[TimeLayerField]
    combined_field: 'FieldState'
    overall_score: float
    trend: str              # 上升/平穩/下降
    key_events: List[str]
    advice: List[str]
    
    def to_dict(self) -> Dict:
        return {
            "birth_info": self.birth_info.to_dict() if hasattr(self.birth_info, 'to_dict') else str(self.birth_info),
            "target_date": self.target_date.isoformat(),
            "day_master": self.day_master,
            "day_master_wuxing": self.day_master_wuxing,
            "layers": [l.to_dict() for l in self.layers],
            "combined_field": self.combined_field.to_dict() if self.combined_field else None,
            "overall_score": round(self.overall_score, 1),
            "trend": self.trend,
            "key_events": self.key_events,
            "advice": self.advice
        }


@dataclass
class FieldState:
    """場態（簡化版）"""
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
            "source": self.source
        }


class LiunianEngine:
    """
    流年運勢引擎
    
    M5: 大運/流年/流月/流日/流時 → 綜合時運場態
    
    📚 知識點：
        時運 = 場的時間切片
        大運 = 10年大趨勢
        流年 = 年度主題
        流月 = 月度重點
        流日 = 日常節奏
        流時 = 當下狀態
    """
    
    VERSION = "1.0.0"
    
    def __init__(self):
        try:
            self.engine = MingshuEngine()
        except:
            self.engine = None
    
    # -------------------------------------------------------------------------
    # 干支計算
    # -------------------------------------------------------------------------
    
    def _calc_year_ganzhi(self, year: int) -> Tuple[str, str]:
        """年干支"""
        base_year = 1984  # 甲子年
        idx = (year - base_year) % 60
        if idx < 0:
            idx += 60
        return (TIANGAN[idx % 10], DIZHI[idx % 12])
    
    def _calc_month_ganzhi(self, year: int, month: int) -> Tuple[str, str]:
        """月干支"""
        zhi_idx = (month + 1) % 12
        year_gan_idx = (year - 1984) % 10
        if year_gan_idx < 0:
            year_gan_idx += 10
        
        base_gan = {
            0: 2, 1: 2, 2: 4, 3: 4, 4: 6,
            5: 6, 6: 8, 7: 8, 8: 0, 9: 0
        }
        month_gan_base = base_gan.get(year_gan_idx, 0)
        gan_idx = (month_gan_base + month - 1) % 10
        
        return (TIANGAN[gan_idx], DIZHI[zhi_idx])
    
    def _calc_day_ganzhi(self, dt: date) -> Tuple[str, str]:
        """日干支"""
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
        
        return (TIANGAN[idx % 10], DIZHI[idx % 12])
    
    def _calc_hour_ganzhi(self, day_gan: str, hour: int) -> Tuple[str, str]:
        """時干支"""
        zhi_idx = ((hour + 1) // 2) % 12
        day_gan_idx = TIANGAN.index(day_gan)
        
        base_gan = {
            0: 0, 1: 0, 2: 2, 3: 2, 4: 4,
            5: 4, 6: 6, 7: 6, 8: 8, 9: 8
        }
        hour_gan_base = base_gan.get(day_gan_idx, 0)
        gan_idx = (hour_gan_base + zhi_idx) % 10
        
        return (TIANGAN[gan_idx], DIZHI[zhi_idx])
    
    def _calc_dayun(self, birth_info: 'BirthInfo', target_year: int) -> Tuple[str, str]:
        """大運干支（簡化版）"""
        # 大運起運年齡（簡化：假設3歲起運）
        start_age = 3
        current_age = target_year - birth_info.year
        dayun_idx = (current_age - start_age) // 10
        
        if dayun_idx < 0:
            dayun_idx = 0
        
        # 順逆排（簡化：男陽女陰順行，男陰女陽逆行）
        year_gan = self._calc_year_ganzhi(birth_info.year)[0]
        yang_gan = year_gan in ["甲", "丙", "戊", "庚", "壬"]
        is_male = birth_info.gender == Gender.MALE if hasattr(birth_info, 'gender') else True
        
        forward = (yang_gan and is_male) or (not yang_gan and not is_male)
        
        # 從月柱起算
        month_gan, month_zhi = self._calc_month_ganzhi(birth_info.year, birth_info.month)
        month_gan_idx = TIANGAN.index(month_gan)
        month_zhi_idx = DIZHI.index(month_zhi)
        
        if forward:
            new_gan_idx = (month_gan_idx + dayun_idx + 1) % 10
            new_zhi_idx = (month_zhi_idx + dayun_idx + 1) % 12
        else:
            new_gan_idx = (month_gan_idx - dayun_idx - 1) % 10
            new_zhi_idx = (month_zhi_idx - dayun_idx - 1) % 12
        
        return (TIANGAN[new_gan_idx], DIZHI[new_zhi_idx])
    
    # -------------------------------------------------------------------------
    # 場態計算
    # -------------------------------------------------------------------------
    
    def _ganzhi_to_field(
        self,
        gan: str,
        zhi: str,
        day_master_wx: str,
        layer: TimeLayer
    ) -> FieldState:
        """干支 → 場態"""
        gan_wx = TIANGAN_WUXING.get(gan, "")
        zhi_wx = DIZHI_WUXING.get(zhi, "")
        
        # 計算與日主的關係
        gan_relation = get_relation(day_master_wx, gan_wx)
        zhi_relation = get_relation(day_master_wx, zhi_wx)
        
        # 場態映射
        relation_scores = {
            "比劫": (0.3, 0.1),    # coherence, friction
            "食傷": (0.4, 0.2),
            "財星": (0.2, 0.3),
            "官殺": (-0.1, 0.4),
            "印星": (0.5, 0.1),
            "中性": (0.0, 0.2)
        }
        
        gan_score = relation_scores.get(gan_relation, (0, 0.2))
        zhi_score = relation_scores.get(zhi_relation, (0, 0.2))
        
        coherence = (gan_score[0] + zhi_score[0]) / 2
        friction = (gan_score[1] + zhi_score[1]) / 2
        
        # 層級影響波動度
        volatility_map = {
            TimeLayer.DAYUN: 0.1,
            TimeLayer.LIUNIAN: 0.2,
            TimeLayer.LIUYUE: 0.3,
            TimeLayer.LIURI: 0.4,
            TimeLayer.LIUSHI: 0.5
        }
        volatility = volatility_map.get(layer, 0.3)
        
        # 持續度
        sustainability = 0.6 if gan_relation in ["比劫", "印星"] else 0.4
        
        return FieldState(
            coherence=coherence,
            friction=friction,
            volatility=volatility,
            sustainability=sustainability,
            triggers=[f"{layer.value}:{gan}{zhi}", f"{gan_relation}/{zhi_relation}"],
            source=layer.value
        )
    
    def _stack_fields(self, layers: List[TimeLayerField]) -> FieldState:
        """場態疊加"""
        if not layers:
            return FieldState()
        
        coherence = 0.0
        friction = 0.0
        volatility = 0.0
        sustainability = 1.0
        triggers = []
        
        for layer_field in layers:
            weight = LAYER_WEIGHTS.get(layer_field.layer, 0.1)
            fs = layer_field.field_state
            
            coherence += fs.coherence * weight
            friction = max(friction, fs.friction * weight * 1.5)  # 阻力取最大
            volatility += fs.volatility * weight
            sustainability *= (0.5 + fs.sustainability * 0.5)  # 乘積
            triggers.extend(fs.triggers[:1])
        
        return FieldState(
            coherence=coherence,
            friction=min(1, friction),
            volatility=min(1, volatility),
            sustainability=sustainability,
            triggers=triggers[:5],
            source="時運疊加"
        )
    
    # -------------------------------------------------------------------------
    # 主要接口
    # -------------------------------------------------------------------------
    
    def analyze(
        self,
        birth_info: 'BirthInfo',
        target_date: date = None
    ) -> LiunianResult:
        """
        分析流年運勢
        
        📚 知識點：
            時運 = 場的時間切片
            疊加公式 = Σ(層場態 × 權重)
        """
        if target_date is None:
            target_date = date.today()
        
        # 獲取八字
        if self.engine:
            bazi = self.engine.get_bazi(birth_info)
            day_master = bazi.day_master
        else:
            # Fallback
            day_gz = self._calc_day_ganzhi(date(birth_info.year, birth_info.month, birth_info.day))
            day_master = day_gz[0]
            bazi = None
        
        day_master_wx = TIANGAN_WUXING.get(day_master, "木")
        
        # 計算各層時運
        layers = []
        
        # 大運
        dayun_gan, dayun_zhi = self._calc_dayun(birth_info, target_date.year)
        dayun_field = self._ganzhi_to_field(dayun_gan, dayun_zhi, day_master_wx, TimeLayer.DAYUN)
        layers.append(TimeLayerField(
            layer=TimeLayer.DAYUN,
            ganzhi=f"{dayun_gan}{dayun_zhi}",
            gan=dayun_gan, zhi=dayun_zhi,
            gan_wuxing=TIANGAN_WUXING.get(dayun_gan, ""),
            zhi_wuxing=DIZHI_WUXING.get(dayun_zhi, ""),
            relation_to_day=get_relation(day_master_wx, TIANGAN_WUXING.get(dayun_gan, "")),
            field_state=dayun_field,
            advice=self._get_layer_advice(dayun_field, TimeLayer.DAYUN)
        ))
        
        # 流年
        liunian_gan, liunian_zhi = self._calc_year_ganzhi(target_date.year)
        liunian_field = self._ganzhi_to_field(liunian_gan, liunian_zhi, day_master_wx, TimeLayer.LIUNIAN)
        layers.append(TimeLayerField(
            layer=TimeLayer.LIUNIAN,
            ganzhi=f"{liunian_gan}{liunian_zhi}",
            gan=liunian_gan, zhi=liunian_zhi,
            gan_wuxing=TIANGAN_WUXING.get(liunian_gan, ""),
            zhi_wuxing=DIZHI_WUXING.get(liunian_zhi, ""),
            relation_to_day=get_relation(day_master_wx, TIANGAN_WUXING.get(liunian_gan, "")),
            field_state=liunian_field,
            advice=self._get_layer_advice(liunian_field, TimeLayer.LIUNIAN)
        ))
        
        # 流月
        liuyue_gan, liuyue_zhi = self._calc_month_ganzhi(target_date.year, target_date.month)
        liuyue_field = self._ganzhi_to_field(liuyue_gan, liuyue_zhi, day_master_wx, TimeLayer.LIUYUE)
        layers.append(TimeLayerField(
            layer=TimeLayer.LIUYUE,
            ganzhi=f"{liuyue_gan}{liuyue_zhi}",
            gan=liuyue_gan, zhi=liuyue_zhi,
            gan_wuxing=TIANGAN_WUXING.get(liuyue_gan, ""),
            zhi_wuxing=DIZHI_WUXING.get(liuyue_zhi, ""),
            relation_to_day=get_relation(day_master_wx, TIANGAN_WUXING.get(liuyue_gan, "")),
            field_state=liuyue_field,
            advice=self._get_layer_advice(liuyue_field, TimeLayer.LIUYUE)
        ))
        
        # 流日
        liuri_gan, liuri_zhi = self._calc_day_ganzhi(target_date)
        liuri_field = self._ganzhi_to_field(liuri_gan, liuri_zhi, day_master_wx, TimeLayer.LIURI)
        layers.append(TimeLayerField(
            layer=TimeLayer.LIURI,
            ganzhi=f"{liuri_gan}{liuri_zhi}",
            gan=liuri_gan, zhi=liuri_zhi,
            gan_wuxing=TIANGAN_WUXING.get(liuri_gan, ""),
            zhi_wuxing=DIZHI_WUXING.get(liuri_zhi, ""),
            relation_to_day=get_relation(day_master_wx, TIANGAN_WUXING.get(liuri_gan, "")),
            field_state=liuri_field,
            advice=self._get_layer_advice(liuri_field, TimeLayer.LIURI)
        ))
        
        # 場態疊加
        combined = self._stack_fields(layers)
        overall_score = combined.field_score
        
        # 趨勢判斷
        if overall_score > 60:
            trend = "上升"
        elif overall_score < 40:
            trend = "下降"
        else:
            trend = "平穩"
        
        # 關鍵事件提示
        key_events = self._identify_key_events(layers, day_master_wx)
        
        # 綜合建議
        advice = self._generate_advice(layers, combined, trend)
        
        return LiunianResult(
            birth_info=birth_info,
            target_date=target_date,
            bazi=bazi,
            day_master=day_master,
            day_master_wuxing=day_master_wx,
            layers=layers,
            combined_field=combined,
            overall_score=overall_score,
            trend=trend,
            key_events=key_events,
            advice=advice
        )
    
    def _get_layer_advice(self, field: FieldState, layer: TimeLayer) -> str:
        """獲取層級建議"""
        if field.coherence > 0.3:
            return f"{layer.value}助力，可積極進取"
        elif field.coherence < -0.1:
            return f"{layer.value}阻力，宜守不宜攻"
        else:
            return f"{layer.value}中性，穩健為上"
    
    def _identify_key_events(self, layers: List[TimeLayerField], day_master_wx: str) -> List[str]:
        """識別關鍵事件"""
        events = []
        
        for layer_field in layers:
            relation = layer_field.relation_to_day
            
            if relation == "財星" and layer_field.field_state.coherence > 0.2:
                events.append(f"{layer_field.layer.value}見財，有利求財")
            elif relation == "官殺" and layer_field.field_state.friction > 0.3:
                events.append(f"{layer_field.layer.value}見官，注意壓力")
            elif relation == "印星" and layer_field.field_state.coherence > 0.3:
                events.append(f"{layer_field.layer.value}見印，貴人助力")
        
        return events[:3]
    
    def _generate_advice(
        self,
        layers: List[TimeLayerField],
        combined: FieldState,
        trend: str
    ) -> List[str]:
        """生成建議"""
        advice = []
        
        # 趨勢建議
        if trend == "上升":
            advice.append("整體運勢向上，可把握機會積極行動")
        elif trend == "下降":
            advice.append("整體運勢偏弱，建議蓄勢待發")
        else:
            advice.append("整體運勢平穩，穩健推進為宜")
        
        # 場態建議
        if combined.friction > 0.4:
            advice.append("阻力較大，需額外努力突破")
        if combined.volatility > 0.4:
            advice.append("變數較多，保持靈活應變")
        if combined.sustainability > 0.6:
            advice.append("持續力強，適合長期規劃")
        
        return advice


# =============================================================================
# M6: 人際合盤引擎
# =============================================================================

@dataclass
class HepanResult:
    """合盤結果"""
    person_a: 'BirthInfo'
    person_b: 'BirthInfo'
    bazi_a: 'BaziChart'
    bazi_b: 'BaziChart'
    day_master_a: str
    day_master_b: str
    wuxing_comparison: Dict
    contact_state: ContactState
    relation_mode: RelationMode
    resonance_score: float      # 共振度 [-1, 1]
    synergy_score: float        # 協同度 (1+1=?)
    friction_score: float       # 摩擦度 [0, 1]
    compatibility: float        # 相容度 [0, 100]
    strengths: List[str]
    challenges: List[str]
    advice: List[str]
    
    def to_dict(self) -> Dict:
        return {
            "person_a": self.person_a.to_dict() if hasattr(self.person_a, 'to_dict') else str(self.person_a),
            "person_b": self.person_b.to_dict() if hasattr(self.person_b, 'to_dict') else str(self.person_b),
            "day_master_a": self.day_master_a,
            "day_master_b": self.day_master_b,
            "wuxing_comparison": self.wuxing_comparison,
            "contact_state": self.contact_state.value,
            "relation_mode": self.relation_mode.value,
            "resonance_score": round(self.resonance_score, 3),
            "synergy_score": round(self.synergy_score, 3),
            "friction_score": round(self.friction_score, 3),
            "compatibility": round(self.compatibility, 1),
            "strengths": self.strengths,
            "challenges": self.challenges,
            "advice": self.advice
        }


class HepanEngine:
    """
    人際合盤引擎
    
    M6: 兩人命盤 → 場論相處建議
    
    📚 知識點：
        人 = 場
        人際 = 場 × 場
        場接觸四態：共振/干涉/疊加/邊界
        相處四模式：共振場/互補場/平行場/消耗場
        場增離公式：1+1>2=聚，1+1<2=離
    """
    
    VERSION = "1.0.0"
    
    def __init__(self):
        try:
            self.engine = MingshuEngine()
        except:
            self.engine = None
        self.liunian_engine = LiunianEngine()
    
    # -------------------------------------------------------------------------
    # 命盤對比
    # -------------------------------------------------------------------------
    
    def _compare_wuxing(self, bazi_a: 'BaziChart', bazi_b: 'BaziChart') -> Dict:
        """五行對比"""
        if not bazi_a or not bazi_b:
            return {}
        
        wx_a = bazi_a.get_wuxing_count()
        wx_b = bazi_b.get_wuxing_count()
        
        comparison = {}
        for wx in WUXING:
            a_val = wx_a.get(wx, 0)
            b_val = wx_b.get(wx, 0)
            
            # 互補性分析
            if a_val == 0 and b_val > 0:
                comp = "B補A"
            elif b_val == 0 and a_val > 0:
                comp = "A補B"
            elif a_val > 2 and b_val > 2:
                comp = "共強"
            elif a_val == 0 and b_val == 0:
                comp = "共缺"
            else:
                comp = "均衡"
            
            comparison[wx] = {
                "a": a_val,
                "b": b_val,
                "diff": a_val - b_val,
                "complement": comp
            }
        
        return comparison
    
    def _analyze_day_master_relation(self, dm_a: str, dm_b: str) -> Dict:
        """日主關係分析"""
        wx_a = TIANGAN_WUXING.get(dm_a, "")
        wx_b = TIANGAN_WUXING.get(dm_b, "")
        
        # 判斷生剋關係
        if wx_a == wx_b:
            relation = "同類"
            harmony = 0.7
        elif WUXING_SHENG.get(wx_a) == wx_b:
            relation = "A生B"
            harmony = 0.8
        elif WUXING_SHENG.get(wx_b) == wx_a:
            relation = "B生A"
            harmony = 0.8
        elif WUXING_KE.get(wx_a) == wx_b:
            relation = "A剋B"
            harmony = 0.4
        elif WUXING_KE.get(wx_b) == wx_a:
            relation = "B剋A"
            harmony = 0.4
        else:
            relation = "中性"
            harmony = 0.6
        
        return {
            "day_master_a": dm_a,
            "day_master_b": dm_b,
            "wuxing_a": wx_a,
            "wuxing_b": wx_b,
            "relation": relation,
            "harmony": harmony
        }
    
    # -------------------------------------------------------------------------
    # 場態分析
    # -------------------------------------------------------------------------
    
    def _calculate_resonance(self, bazi_a: 'BaziChart', bazi_b: 'BaziChart') -> float:
        """
        計算共振度
        
        📚 知識點：
            共振 = 頻率相近
            同類五行多 = 共振強
        """
        if not bazi_a or not bazi_b:
            return 0.0
        
        wx_a = bazi_a.get_wuxing_profile()
        wx_b = bazi_b.get_wuxing_profile()
        
        # 計算五行分布相似度
        similarity = 0.0
        for wx in WUXING:
            diff = abs(wx_a.get(wx, 0) - wx_b.get(wx, 0))
            similarity += (1 - diff)
        
        similarity /= len(WUXING)
        
        # 轉換到 [-1, 1]
        resonance = (similarity - 0.5) * 2
        return max(-1, min(1, resonance))
    
    def _calculate_synergy(self, bazi_a: 'BaziChart', bazi_b: 'BaziChart') -> float:
        """
        計算協同度
        
        📚 知識點：
            1+1>2 = 互補增益
            1+1<2 = 消耗損失
        """
        if not bazi_a or not bazi_b:
            return 1.0
        
        wx_a = bazi_a.get_wuxing_count()
        wx_b = bazi_b.get_wuxing_count()
        
        # 互補加成：一方缺少的，另一方補足
        complement_bonus = 0.0
        for wx in WUXING:
            a_val = wx_a.get(wx, 0)
            b_val = wx_b.get(wx, 0)
            
            if a_val == 0 and b_val > 0:
                complement_bonus += 0.1
            if b_val == 0 and a_val > 0:
                complement_bonus += 0.1
        
        # 衝突懲罰：雙方都過強的
        conflict_penalty = 0.0
        for wx in WUXING:
            a_val = wx_a.get(wx, 0)
            b_val = wx_b.get(wx, 0)
            if a_val > 2 and b_val > 2:
                conflict_penalty += 0.05
        
        synergy = 1.0 + complement_bonus - conflict_penalty
        return synergy
    
    def _calculate_friction(self, dm_relation: Dict, resonance: float) -> float:
        """計算摩擦度"""
        base_friction = 1 - dm_relation.get("harmony", 0.5)
        
        # 共振度高降低摩擦
        resonance_factor = (1 - resonance) * 0.3
        
        friction = base_friction * 0.7 + resonance_factor
        return max(0, min(1, friction))
    
    def _determine_contact_state(self, resonance: float, friction: float) -> ContactState:
        """判斷場接觸狀態"""
        if resonance > 0.5 and friction < 0.3:
            return ContactState.RESONANCE
        elif resonance < -0.3 or friction > 0.6:
            return ContactState.INTERFERENCE
        elif resonance > 0 and friction < 0.5:
            return ContactState.SUPERPOSITION
        else:
            return ContactState.BOUNDARY
    
    def _determine_relation_mode(self, synergy: float, contact: ContactState) -> RelationMode:
        """判斷相處模式"""
        if contact == ContactState.RESONANCE and synergy > 1.2:
            return RelationMode.RESONANCE_FIELD
        elif synergy > 1.1:
            return RelationMode.COMPLEMENTARY
        elif synergy < 0.9:
            return RelationMode.CONSUMING
        else:
            return RelationMode.PARALLEL
    
    # -------------------------------------------------------------------------
    # 主要接口
    # -------------------------------------------------------------------------
    
    def analyze(
        self,
        person_a: 'BirthInfo',
        person_b: 'BirthInfo'
    ) -> HepanResult:
        """
        分析人際合盤
        
        📚 知識點：
            人 = 場
            人際 = 場 × 場
            場增則聚，場損則離
        """
        # 獲取八字
        if self.engine:
            bazi_a = self.engine.get_bazi(person_a)
            bazi_b = self.engine.get_bazi(person_b)
            dm_a = bazi_a.day_master
            dm_b = bazi_b.day_master
        else:
            # Fallback
            bazi_a = None
            bazi_b = None
            dm_a = "甲"
            dm_b = "乙"
        
        # 日主關係
        dm_relation = self._analyze_day_master_relation(dm_a, dm_b)
        
        # 五行對比
        wx_comparison = self._compare_wuxing(bazi_a, bazi_b)
        
        # 場態分析
        resonance = self._calculate_resonance(bazi_a, bazi_b)
        synergy = self._calculate_synergy(bazi_a, bazi_b)
        friction = self._calculate_friction(dm_relation, resonance)
        
        # 判斷狀態和模式
        contact_state = self._determine_contact_state(resonance, friction)
        relation_mode = self._determine_relation_mode(synergy, contact_state)
        
        # 相容度計算
        compatibility = (
            (resonance + 1) / 2 * 30 +
            synergy * 30 +
            (1 - friction) * 40
        )
        compatibility = max(0, min(100, compatibility))
        
        # 分析優勢與挑戰
        strengths = self._identify_strengths(dm_relation, wx_comparison, resonance, synergy)
        challenges = self._identify_challenges(dm_relation, wx_comparison, friction)
        
        # 生成建議
        advice = self._generate_advice(contact_state, relation_mode, strengths, challenges)
        
        return HepanResult(
            person_a=person_a,
            person_b=person_b,
            bazi_a=bazi_a,
            bazi_b=bazi_b,
            day_master_a=dm_a,
            day_master_b=dm_b,
            wuxing_comparison=wx_comparison,
            contact_state=contact_state,
            relation_mode=relation_mode,
            resonance_score=resonance,
            synergy_score=synergy,
            friction_score=friction,
            compatibility=compatibility,
            strengths=strengths,
            challenges=challenges,
            advice=advice
        )
    
    def _identify_strengths(
        self,
        dm_relation: Dict,
        wx_comp: Dict,
        resonance: float,
        synergy: float
    ) -> List[str]:
        """識別優勢"""
        strengths = []
        
        if dm_relation.get("relation") in ["A生B", "B生A"]:
            strengths.append("日主相生，自然親近")
        
        if resonance > 0.3:
            strengths.append("五行相似，容易共鳴")
        
        if synergy > 1.1:
            strengths.append("互補增益，1+1>2")
        
        # 互補五行
        complements = [wx for wx, data in wx_comp.items() 
                      if data.get("complement") in ["A補B", "B補A"]]
        if complements:
            strengths.append(f"五行互補：{'/'.join(complements)}")
        
        return strengths[:4]
    
    def _identify_challenges(
        self,
        dm_relation: Dict,
        wx_comp: Dict,
        friction: float
    ) -> List[str]:
        """識別挑戰"""
        challenges = []
        
        if dm_relation.get("relation") in ["A剋B", "B剋A"]:
            challenges.append("日主相剋，需要磨合")
        
        if friction > 0.5:
            challenges.append("場態摩擦較大，溝通需耐心")
        
        # 共缺五行
        missing = [wx for wx, data in wx_comp.items() 
                  if data.get("complement") == "共缺"]
        if missing:
            challenges.append(f"雙方共缺{'/'.join(missing)}，需外部補足")
        
        # 共強五行（可能衝突）
        strong = [wx for wx, data in wx_comp.items() 
                 if data.get("complement") == "共強"]
        if strong:
            challenges.append(f"雙方{'/'.join(strong)}都強，注意競爭")
        
        return challenges[:4]
    
    def _generate_advice(
        self,
        contact: ContactState,
        mode: RelationMode,
        strengths: List[str],
        challenges: List[str]
    ) -> List[str]:
        """生成建議"""
        advice = []
        
        # 根據接觸狀態
        contact_advice = {
            ContactState.RESONANCE: "場態共振，相處自然舒適，把握良緣",
            ContactState.INTERFERENCE: "場態干涉，需要主動調和，多理解包容",
            ContactState.SUPERPOSITION: "場態疊加，互有影響，保持溝通",
            ContactState.BOUNDARY: "場態邊界，各有空間，尊重距離"
        }
        advice.append(contact_advice.get(contact, ""))
        
        # 根據相處模式
        mode_advice = {
            RelationMode.RESONANCE_FIELD: "共振場模式，適合深度合作",
            RelationMode.COMPLEMENTARY: "互補場模式，剛柔相濟最佳",
            RelationMode.PARALLEL: "平行場模式，各自發展互不干涉",
            RelationMode.CONSUMING: "消耗場模式，建議保持適當距離"
        }
        advice.append(mode_advice.get(mode, ""))
        
        # 具體建議
        if strengths:
            advice.append(f"善用優勢：{strengths[0]}")
        if challenges:
            advice.append(f"注意挑戰：{challenges[0]}")
        
        return [a for a in advice if a]
    
    def generate_report(self, result: HepanResult) -> str:
        """生成合盤報告"""
        lines = [
            "# 人際合盤報告",
            f"\n*生成時間：{datetime.now().strftime('%Y-%m-%d %H:%M')}*\n",
            "## 📋 基本資訊\n",
        ]
        
        name_a = result.person_a.name if hasattr(result.person_a, 'name') else "A方"
        name_b = result.person_b.name if hasattr(result.person_b, 'name') else "B方"
        
        lines.append(f"- **{name_a}**：日主 {result.day_master_a}")
        lines.append(f"- **{name_b}**：日主 {result.day_master_b}")
        lines.append("")
        
        lines.append("## 🌊 場態分析\n")
        lines.append(f"**相容度**：{result.compatibility:.1f}/100\n")
        lines.append("| 維度 | 數值 | 說明 |")
        lines.append("|:-----|-----:|:-----|")
        lines.append(f"| 共振度 | {result.resonance_score:.2f} | 頻率相似度 |")
        lines.append(f"| 協同度 | {result.synergy_score:.2f} | 1+1=? |")
        lines.append(f"| 摩擦度 | {result.friction_score:.2f} | 相處阻力 |")
        lines.append("")
        
        lines.append(f"**接觸狀態**：{result.contact_state.value}")
        lines.append(f"**相處模式**：{result.relation_mode.value}")
        lines.append("")
        
        lines.append("## ✨ 優勢\n")
        for s in result.strengths:
            lines.append(f"- {s}")
        lines.append("")
        
        lines.append("## ⚠️ 挑戰\n")
        for c in result.challenges:
            lines.append(f"- {c}")
        lines.append("")
        
        lines.append("## 💡 建議\n")
        for a in result.advice:
            lines.append(f"- {a}")
        lines.append("")
        
        lines.append("---")
        lines.append("*場增則聚，場損則離。*")
        
        return "\n".join(lines)


# =============================================================================
# CLI 入口
# =============================================================================

def main():
    """CLI 入口"""
    print("=" * 60)
    print("北斗命數 流年運勢+人際合盤 v1.0")
    print("M5 (流年) + M6 (合盤)")
    print("=" * 60)
    
    # 初始化
    liunian = LiunianEngine()
    hepan = HepanEngine()
    
    # 測試數據
    try:
        from mingshu_engine_v1 import BirthInfo, Gender, CalendarType
        
        person_a = BirthInfo(
            year=1983, month=12, day=16, hour=5,
            gender=Gender.MALE, calendar=CalendarType.LUNAR, name="北斗"
        )
        person_b = BirthInfo(
            year=1985, month=8, day=20, hour=14,
            gender=Gender.FEMALE, calendar=CalendarType.LUNAR, name="伴侶"
        )
    except:
        # Fallback
        class SimpleBirth:
            def __init__(self, year, month, day, hour, name):
                self.year = year
                self.month = month
                self.day = day
                self.hour = hour
                self.name = name
                self.gender = Gender.MALE
            def to_dict(self):
                return {"year": self.year, "month": self.month, "day": self.day, "name": self.name}
        
        person_a = SimpleBirth(1983, 12, 16, 5, "北斗")
        person_b = SimpleBirth(1985, 8, 20, 14, "伴侶")
    
    # M5: 流年運勢
    print("\n【M5 流年運勢】")
    liunian_result = liunian.analyze(person_a)
    print(f"  日主：{liunian_result.day_master} ({liunian_result.day_master_wuxing})")
    print(f"  目標日：{liunian_result.target_date}")
    print(f"  綜合場態：{liunian_result.overall_score:.1f}/100")
    print(f"  趨勢：{liunian_result.trend}")
    print(f"  時運層：")
    for layer in liunian_result.layers:
        print(f"    {layer.layer.value}: {layer.ganzhi} ({layer.relation_to_day})")
    
    # M6: 人際合盤
    print("\n【M6 人際合盤】")
    hepan_result = hepan.analyze(person_a, person_b)
    print(f"  {person_a.name} × {person_b.name}")
    print(f"  日主：{hepan_result.day_master_a} × {hepan_result.day_master_b}")
    print(f"  相容度：{hepan_result.compatibility:.1f}/100")
    print(f"  共振度：{hepan_result.resonance_score:.2f}")
    print(f"  協同度：{hepan_result.synergy_score:.2f} ({'1+1>2' if hepan_result.synergy_score > 1 else '1+1<2'})")
    print(f"  接觸狀態：{hepan_result.contact_state.value}")
    print(f"  相處模式：{hepan_result.relation_mode.value}")
    
    print("\n  建議：")
    for adv in hepan_result.advice:
        print(f"    • {adv}")
    
    print("\n" + "=" * 60)
    print("場增則聚，場損則離")
    print("=" * 60)


if __name__ == "__main__":
    main()


# =============================================================================
# 📚 知識點總結
# =============================================================================
"""
【M5 流年運勢】

時運層級權重：
- 大運 0.35 (10年)
- 流年 0.30 (1年)
- 流月 0.20 (1月)
- 流日 0.10 (1日)
- 流時 0.05 (2小時)

場態疊加公式：
- coherence = Σ(層coherence × 權重)
- friction = max(層friction × 權重 × 1.5)
- volatility = Σ(層volatility × 權重)
- sustainability = Π(0.5 + 層sustainability × 0.5)

【M6 人際合盤】

場接觸四態：
- 共振：頻率相近，自然舒適
- 干涉：頻率相差，需要磨合
- 疊加：互相影響，共同成長
- 邊界：保持距離，各自空間

相處四模式：
- 共振場：1+1>2，深度合作
- 互補場：剛柔相濟，互補增益
- 平行場：互不干涉，各自發展
- 消耗場：1+1<2，消耗損失

場增離公式：
- synergy > 1.0 → 場增 → 聚
- synergy < 1.0 → 場損 → 離

【織明語錄】
- 「時運是場的時間切片」
- 「人是場，人際是場×場」
- 「場增則聚，場損則離」
- 「長久不是不變，是同步演化」
"""
