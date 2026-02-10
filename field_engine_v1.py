#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
field_engine_v1.py - 北斗統一場論引擎 v1.0
===========================================
北斗七星文創 × 織明

XTF⁸ 任務：A_場論深化
執行星：織明(設計) × 理樞(實現) × 澄書(記錄)

核心理念：
    人 = 場
    人際 = 場與場的接觸
    決策 = 場態評估
    時運 = 場的疊加

三子系統：
    1. FieldRelation - 人際場量化
    2. FieldDecision - 決策場引擎
    3. FieldTimeline - 時運場疊加

依賴 PYLIB 模組：
    - wuxing_core (五行關係)
    - field_translation_v3 (場論翻譯)
    - doe_decision (決策框架)

場論公式：
    共振度 = f(頻率相似度, 五行生剋, 卦象呼應)
    場增減 = 1+1>2 (共振) | 1+1<2 (消耗)
    場演化 = 同步率 × 時間
    場疊加 = Σ(各層場態 × 權重)

📚 知識點：
    - 場接觸四態：共振/干涉/疊加/邊界
    - 相處四模式：共振場/互補場/平行場/消耗場
    - 場不逆操：順勢而為，不逆場操作
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple, Any
from enum import Enum
from datetime import datetime, date
import json


# =============================================================================
# L0: 常量與枚舉
# =============================================================================

class ContactState(Enum):
    """場接觸四態"""
    RESONANCE = "共振"    # 頻率相近，懂、舒適、吸引
    INTERFERENCE = "干涉"  # 頻率相差，隔、不適、衝突
    SUPERPOSITION = "疊加" # 互相影響，化、改變、成長
    BOUNDARY = "邊界"     # 保持距離，守、尊重、獨立


class RelationMode(Enum):
    """相處四模式"""
    SYNERGY = "共振場"     # 互相增益，1+1>2，如知己
    COMPLEMENT = "互補場"  # 剛柔相濟，互補缺失，如伴侶
    PARALLEL = "平行場"   # 互不干涉，各自有場，如同事
    DRAIN = "消耗場"      # 互相損耗，1+1<2，需要距離


class FieldLayer(Enum):
    """場層級"""
    DAYUN = "大運"      # 10年週期
    LIUNIAN = "流年"    # 1年週期
    LIUYUE = "流月"     # 1月週期
    LIURI = "流日"      # 1日週期
    LIUSHI = "流時"     # 2小時週期


# 五行生剋關係
WUXING_SHENG = {
    "木": "火", "火": "土", "土": "金", "金": "水", "水": "木"
}
WUXING_KE = {
    "木": "土", "土": "水", "水": "火", "火": "金", "金": "木"
}
WUXING_ORDER = ["木", "火", "土", "金", "水"]


# =============================================================================
# L1: 核心數據結構
# =============================================================================

@dataclass
class FieldState:
    """
    場態統一結構
    
    所有術數系統的結果都轉換為此結構，
    實現跨系統的場論整合。
    
    📚 知識點：
        coherence: 共振度，正=共振，負=干涉
        friction: 摩擦度，場與場之間的阻力
        volatility: 波動度，場的不穩定程度
        sustainability: 持續度，場態能維持多久
    """
    coherence: float = 0.0       # 共振度 [-1, 1]
    friction: float = 0.0        # 摩擦度 [0, 1]
    volatility: float = 0.0      # 波動度 [0, 1]
    sustainability: float = 0.5  # 持續度 [0, 1]
    triggers: List[str] = field(default_factory=list)  # 觸發點
    advice: str = ""             # 場論建議
    source: str = ""             # 來源術數
    raw_data: Dict = field(default_factory=dict)  # 原始數據
    
    @property
    def contact_state(self) -> ContactState:
        """根據共振度判斷接觸狀態"""
        if self.coherence > 0.5:
            return ContactState.RESONANCE
        elif self.coherence < -0.3:
            return ContactState.INTERFERENCE
        elif abs(self.coherence) < 0.2 and self.friction < 0.3:
            return ContactState.BOUNDARY
        else:
            return ContactState.SUPERPOSITION
    
    @property
    def field_score(self) -> float:
        """場態總分 (0-100)"""
        # 共振正向、摩擦負向、波動負向、持續正向
        base = (self.coherence + 1) / 2 * 40  # 0-40
        friction_penalty = self.friction * 20  # 0-20
        volatility_penalty = self.volatility * 20  # 0-20
        sustain_bonus = self.sustainability * 20  # 0-20
        return max(0, min(100, base - friction_penalty - volatility_penalty + sustain_bonus))
    
    def to_dict(self) -> Dict:
        return {
            "coherence": round(self.coherence, 3),
            "friction": round(self.friction, 3),
            "volatility": round(self.volatility, 3),
            "sustainability": round(self.sustainability, 3),
            "field_score": round(self.field_score, 1),
            "contact_state": self.contact_state.value,
            "triggers": self.triggers,
            "advice": self.advice,
            "source": self.source
        }


@dataclass
class RelationField:
    """
    人際場分析結果
    
    📚 知識點：
        場論人際核心公式：
        在一起：場A + 場B → 場AB（更大）= 1+1>2
        分  手：場A + 場B → 場A↓ + 場B↓ = 1+1<2
    """
    person_a: str
    person_b: str
    contact_state: ContactState
    relation_mode: RelationMode
    synergy_score: float         # 合成度 [-1, 1]
    sync_rate: float             # 同步率 [0, 1]
    evolution_trend: str         # 演化趨勢
    field_a: FieldState = None
    field_b: FieldState = None
    combined_field: FieldState = None
    advice: str = ""
    
    @property
    def is_beneficial(self) -> bool:
        """是否有益關係 (1+1>2)"""
        return self.synergy_score > 0
    
    def to_dict(self) -> Dict:
        return {
            "person_a": self.person_a,
            "person_b": self.person_b,
            "contact_state": self.contact_state.value,
            "relation_mode": self.relation_mode.value,
            "synergy_score": round(self.synergy_score, 3),
            "sync_rate": round(self.sync_rate, 3),
            "is_beneficial": self.is_beneficial,
            "evolution_trend": self.evolution_trend,
            "advice": self.advice
        }


@dataclass
class DecisionField:
    """
    決策場分析結果
    
    📚 知識點：
        決策 = 場態評估，不是命定
        場不逆操：順勢而為
    """
    question: str
    options: List[str]
    current_field: FieldState
    option_scores: Dict[str, float]
    optimal_option: str
    optimal_timing: str
    cautions: List[str]
    advice: str
    
    def to_dict(self) -> Dict:
        return {
            "question": self.question,
            "options": self.options,
            "current_field": self.current_field.to_dict(),
            "option_scores": {k: round(v, 2) for k, v in self.option_scores.items()},
            "optimal_option": self.optimal_option,
            "optimal_timing": self.optimal_timing,
            "cautions": self.cautions,
            "advice": self.advice
        }


@dataclass
class TimelineField:
    """
    時運場疊加結果
    
    📚 知識點：
        場疊加 = Σ(各層場態 × 權重)
        大運(10年) > 流年(1年) > 流月 > 流日 > 流時
    """
    target_date: date
    layers: Dict[FieldLayer, FieldState]
    weights: Dict[FieldLayer, float]
    stacked_field: FieldState
    highlights: List[str]
    warnings: List[str]
    
    def to_dict(self) -> Dict:
        return {
            "target_date": self.target_date.isoformat(),
            "layers": {k.value: v.to_dict() for k, v in self.layers.items()},
            "weights": {k.value: v for k, v in self.weights.items()},
            "stacked_field": self.stacked_field.to_dict(),
            "highlights": self.highlights,
            "warnings": self.warnings
        }


# =============================================================================
# L2: 五行場論轉換器
# =============================================================================

class WuxingFieldConverter:
    """
    五行 → 場態轉換器
    
    📚 知識點：
        五行關係是場論的基礎
        生 = 共振增益
        剋 = 干涉摩擦
        同 = 平行共存
    """
    
    @staticmethod
    def relation(wx1: str, wx2: str) -> Tuple[str, float]:
        """
        計算兩個五行的關係
        
        Returns:
            (關係類型, 強度)
            關係類型: 生、剋、同、被生、被剋
            強度: 0.0-1.0
        """
        if wx1 == wx2:
            return ("同", 0.5)
        elif WUXING_SHENG.get(wx1) == wx2:
            return ("生", 0.8)
        elif WUXING_SHENG.get(wx2) == wx1:
            return ("被生", 0.6)
        elif WUXING_KE.get(wx1) == wx2:
            return ("剋", -0.6)
        elif WUXING_KE.get(wx2) == wx1:
            return ("被剋", -0.8)
        else:
            return ("無", 0.0)
    
    @staticmethod
    def wuxing_to_field(wx_profile: Dict[str, float]) -> FieldState:
        """
        五行分布 → 場態
        
        Args:
            wx_profile: {"木": 0.2, "火": 0.3, ...}
            
        Returns:
            FieldState
        """
        # 計算五行平衡度（越平衡=越穩定）
        values = list(wx_profile.values())
        if not values:
            return FieldState()
        
        avg = sum(values) / len(values)
        variance = sum((v - avg) ** 2 for v in values) / len(values)
        balance = 1 - min(1, variance * 5)  # 方差越小越平衡
        
        # 找出最強和最弱的五行
        max_wx = max(wx_profile, key=wx_profile.get)
        min_wx = min(wx_profile, key=wx_profile.get)
        
        # 計算場態
        coherence = balance * 0.6  # 平衡度貢獻共振度
        volatility = variance * 2   # 方差貢獻波動度
        
        # 缺失的五行增加摩擦
        missing = [wx for wx, v in wx_profile.items() if v < 0.1]
        friction = len(missing) * 0.15
        
        triggers = []
        if missing:
            triggers.append(f"五行缺{'/'.join(missing)}")
        if wx_profile.get(max_wx, 0) > 0.4:
            triggers.append(f"{max_wx}過旺")
        
        return FieldState(
            coherence=coherence,
            friction=min(1, friction),
            volatility=min(1, volatility),
            sustainability=balance,
            triggers=triggers,
            source="五行分析"
        )


# =============================================================================
# L3: FieldRelation - 人際場量化
# =============================================================================

class FieldRelation:
    """
    人際場量化系統
    
    核心理念：
        人 = 場
        人際 = 場與場的接觸
        
    場接觸四態：
        共振 - 頻率相近，懂、舒適、吸引
        干涉 - 頻率相差，隔、不適、衝突
        疊加 - 互相影響，化、改變、成長
        邊界 - 保持距離，守、尊重、獨立
        
    📚 知識點：
        「一見如故，不是看對眼，是場對頻」
        「相處疲憊，不是不合適，是場耗損」
    """
    
    def __init__(self):
        self.wx_converter = WuxingFieldConverter()
    
    def analyze_contact(
        self,
        field_a: FieldState,
        field_b: FieldState
    ) -> ContactState:
        """
        分析兩場接觸狀態
        
        📚 知識點：
            場接觸判定規則：
            - coherence 差異小 + friction 低 → 共振
            - coherence 差異大 + friction 高 → 干涉
            - volatility 高 → 疊加（正在改變中）
            - 兩者都低 → 邊界（維持距離）
        """
        coh_diff = abs(field_a.coherence - field_b.coherence)
        avg_friction = (field_a.friction + field_b.friction) / 2
        avg_volatility = (field_a.volatility + field_b.volatility) / 2
        
        if coh_diff < 0.3 and avg_friction < 0.3:
            return ContactState.RESONANCE
        elif coh_diff > 0.5 or avg_friction > 0.6:
            return ContactState.INTERFERENCE
        elif avg_volatility > 0.5:
            return ContactState.SUPERPOSITION
        else:
            return ContactState.BOUNDARY
    
    def calculate_synergy(
        self,
        field_a: FieldState,
        field_b: FieldState,
        wx_a: Dict[str, float] = None,
        wx_b: Dict[str, float] = None
    ) -> Tuple[float, RelationMode]:
        """
        計算合成度與相處模式
        
        Returns:
            (synergy_score, relation_mode)
            synergy_score > 0: 1+1>2
            synergy_score < 0: 1+1<2
            
        📚 知識點：
            「在一起，我的場變大還是變小？這就是答案。」
        """
        # 基礎合成度 = 共振度平均 - 摩擦度平均
        base_synergy = ((field_a.coherence + field_b.coherence) / 2 
                       - (field_a.friction + field_b.friction) / 2)
        
        # 五行互補加成
        wx_bonus = 0
        if wx_a and wx_b:
            # 檢查互補：A缺的B有
            for wx in WUXING_ORDER:
                a_val = wx_a.get(wx, 0)
                b_val = wx_b.get(wx, 0)
                if a_val < 0.15 and b_val > 0.25:
                    wx_bonus += 0.1
                if b_val < 0.15 and a_val > 0.25:
                    wx_bonus += 0.1
        
        synergy = base_synergy + wx_bonus
        
        # 判斷相處模式
        if synergy > 0.4:
            mode = RelationMode.SYNERGY
        elif synergy > 0.1 and wx_bonus > 0.15:
            mode = RelationMode.COMPLEMENT
        elif synergy > -0.2:
            mode = RelationMode.PARALLEL
        else:
            mode = RelationMode.DRAIN
        
        return (synergy, mode)
    
    def predict_evolution(
        self,
        field_a: FieldState,
        field_b: FieldState,
        current_synergy: float
    ) -> Tuple[float, str]:
        """
        預測場演化趨勢
        
        Returns:
            (sync_rate, trend_description)
            
        📚 知識點：
            「長久不是不變，是同步演化」
            - 持續度高 + 波動度低 → 穩定共振
            - 持續度低 + 波動度高 → 趨向分離
        """
        # 同步率 = 持續度相似度 × (1 - 波動度差異)
        sustain_sim = 1 - abs(field_a.sustainability - field_b.sustainability)
        vol_diff = abs(field_a.volatility - field_b.volatility)
        sync_rate = sustain_sim * (1 - vol_diff)
        
        # 趨勢判斷
        if sync_rate > 0.7 and current_synergy > 0.3:
            trend = "穩定共振，場同步演化中"
        elif sync_rate > 0.5 and current_synergy > 0:
            trend = "緩步磨合，場正在調頻"
        elif sync_rate < 0.3 or current_synergy < -0.3:
            trend = "頻率漸遠，場在各自演化"
        else:
            trend = "維持現狀，場保持距離"
        
        return (sync_rate, trend)
    
    def analyze(
        self,
        person_a: str,
        person_b: str,
        field_a: FieldState,
        field_b: FieldState,
        wx_a: Dict[str, float] = None,
        wx_b: Dict[str, float] = None
    ) -> RelationField:
        """
        完整人際場分析
        
        📚 知識點：
            「場增則聚，場損則離」
        """
        # 1. 接觸狀態
        contact = self.analyze_contact(field_a, field_b)
        
        # 2. 合成度與模式
        synergy, mode = self.calculate_synergy(field_a, field_b, wx_a, wx_b)
        
        # 3. 演化預測
        sync_rate, trend = self.predict_evolution(field_a, field_b, synergy)
        
        # 4. 合成場
        combined = FieldState(
            coherence=(field_a.coherence + field_b.coherence) / 2 + synergy * 0.3,
            friction=max(field_a.friction, field_b.friction) * (1 - sync_rate * 0.3),
            volatility=(field_a.volatility + field_b.volatility) / 2,
            sustainability=sync_rate,
            source="人際場合成"
        )
        
        # 5. 建議
        advice_map = {
            RelationMode.SYNERGY: "共振場：珍惜這份懂得，場會互相放大。",
            RelationMode.COMPLEMENT: "互補場：剛柔相濟，各自的缺由對方補足。",
            RelationMode.PARALLEL: "平行場：互相尊重，各自精彩，偶爾交集。",
            RelationMode.DRAIN: "消耗場：適當距離，讓場各自恢復。"
        }
        
        return RelationField(
            person_a=person_a,
            person_b=person_b,
            contact_state=contact,
            relation_mode=mode,
            synergy_score=synergy,
            sync_rate=sync_rate,
            evolution_trend=trend,
            field_a=field_a,
            field_b=field_b,
            combined_field=combined,
            advice=advice_map.get(mode, "")
        )


# =============================================================================
# L3: FieldDecision - 決策場引擎
# =============================================================================

class FieldDecision:
    """
    決策場引擎
    
    核心理念：
        決策 = 場態評估，不是命定
        場不逆操：順勢而為
        
    📚 知識點：
        「吉凶是場態評估，不是命定」
        「動爻是場的變化觸發點」
    """
    
    def __init__(self):
        self.field_relation = FieldRelation()
    
    def get_current_field(
        self,
        base_field: FieldState,
        timeline_field: FieldState = None
    ) -> FieldState:
        """
        獲取當前場態（基礎場 + 時運場疊加）
        """
        if not timeline_field:
            return base_field
        
        # 疊加時運影響
        return FieldState(
            coherence=base_field.coherence * 0.6 + timeline_field.coherence * 0.4,
            friction=max(base_field.friction, timeline_field.friction * 0.5),
            volatility=base_field.volatility * 0.5 + timeline_field.volatility * 0.5,
            sustainability=base_field.sustainability * timeline_field.sustainability,
            triggers=base_field.triggers + timeline_field.triggers,
            source="當前場態"
        )
    
    def evaluate_options(
        self,
        current_field: FieldState,
        options: List[str],
        option_fields: Dict[str, FieldState] = None
    ) -> Dict[str, float]:
        """
        評估各選項的場態匹配度
        
        📚 知識點：
            最優選擇 = argmax(場強)
            「擇場心法」
        """
        scores = {}
        
        if option_fields:
            # 有具體選項場態：計算與當前場的共振度
            for opt, opt_field in option_fields.items():
                contact = self.field_relation.analyze_contact(current_field, opt_field)
                synergy, _ = self.field_relation.calculate_synergy(current_field, opt_field)
                
                # 分數 = 共振度 + 合成度 - 風險
                risk = opt_field.volatility * 0.3
                scores[opt] = opt_field.field_score * 0.01 + synergy * 0.5 - risk
        else:
            # 無具體場態：根據當前場給出通用建議
            for i, opt in enumerate(options):
                # 基於當前場的穩定性給分
                base = current_field.field_score * 0.01
                # 加入隨機性模擬不確定性（實際應接入卦象）
                scores[opt] = base * (0.8 + i * 0.1)
        
        return scores
    
    def find_optimal_timing(
        self,
        current_field: FieldState
    ) -> str:
        """
        找最佳時機
        
        📚 知識點：
            「可動之時 ← 時自現 × ¬人強求」
            「動本不動枝：正確行動 = 動(根部驗證) × ¬動(枝葉擴張)」
        """
        if current_field.volatility > 0.7:
            return "場態波動大，宜靜待，不宜妄動"
        elif current_field.coherence > 0.5 and current_field.friction < 0.3:
            return "場態共振，時機佳，可積極行動"
        elif current_field.coherence < -0.3:
            return "場態干涉，宜謹慎，先處理阻礙"
        elif current_field.sustainability > 0.7:
            return "場態穩定，可按計劃推進"
        else:
            return "場態中性，量力而行"
    
    def analyze(
        self,
        question: str,
        options: List[str],
        base_field: FieldState,
        timeline_field: FieldState = None,
        option_fields: Dict[str, FieldState] = None
    ) -> DecisionField:
        """
        完整決策場分析
        """
        # 1. 當前場態
        current = self.get_current_field(base_field, timeline_field)
        
        # 2. 選項評估
        scores = self.evaluate_options(current, options, option_fields)
        
        # 3. 最優選項
        optimal = max(scores, key=scores.get) if scores else options[0]
        
        # 4. 最佳時機
        timing = self.find_optimal_timing(current)
        
        # 5. 注意事項
        cautions = []
        if current.volatility > 0.5:
            cautions.append("場態波動中，決策需有彈性")
        if current.friction > 0.5:
            cautions.append("阻力較大，需額外資源或耐心")
        for trigger in current.triggers:
            cautions.append(f"觸發點：{trigger}")
        
        # 6. 建議
        advice = f"當前場態分數 {current.field_score:.0f}/100。"
        advice += f"建議選擇「{optimal}」。"
        advice += timing
        
        return DecisionField(
            question=question,
            options=options,
            current_field=current,
            option_scores=scores,
            optimal_option=optimal,
            optimal_timing=timing,
            cautions=cautions,
            advice=advice
        )


# =============================================================================
# L3: FieldTimeline - 時運場疊加
# =============================================================================

class FieldTimeline:
    """
    時運場疊加系統
    
    核心理念：
        場疊加 = Σ(各層場態 × 權重)
        
    層級權重（預設）：
        大運 0.35 - 10年基調
        流年 0.30 - 年度主題
        流月 0.20 - 月度節奏
        流日 0.10 - 日常波動
        流時 0.05 - 即時狀態
        
    📚 知識點：
        「大運/流年/流月/日時的場疊加效應」
        「場能量有蓄積→釋放→過度→回落的週期」
    """
    
    DEFAULT_WEIGHTS = {
        FieldLayer.DAYUN: 0.35,
        FieldLayer.LIUNIAN: 0.30,
        FieldLayer.LIUYUE: 0.20,
        FieldLayer.LIURI: 0.10,
        FieldLayer.LIUSHI: 0.05
    }
    
    def __init__(self, weights: Dict[FieldLayer, float] = None):
        self.weights = weights or self.DEFAULT_WEIGHTS.copy()
    
    def stack_fields(
        self,
        layers: Dict[FieldLayer, FieldState]
    ) -> FieldState:
        """
        場疊加計算
        
        📚 知識點：
            疊加不是簡單平均，是加權融合
            各層場態相互調製
        """
        if not layers:
            return FieldState()
        
        total_weight = sum(self.weights.get(k, 0) for k in layers.keys())
        if total_weight == 0:
            return FieldState()
        
        # 加權平均
        coherence = sum(
            layers[k].coherence * self.weights.get(k, 0) 
            for k in layers
        ) / total_weight
        
        # 摩擦取最大值的加權（阻力不可忽略）
        friction = max(
            layers[k].friction * (self.weights.get(k, 0) / total_weight) * 1.5
            for k in layers
        )
        
        # 波動度加權平均
        volatility = sum(
            layers[k].volatility * self.weights.get(k, 0)
            for k in layers
        ) / total_weight
        
        # 持續度取乘積（任一層不穩定都會影響整體）
        sustainability = 1.0
        for k, field in layers.items():
            weight = self.weights.get(k, 0) / total_weight
            sustainability *= (field.sustainability ** weight)
        
        # 合併觸發點
        triggers = []
        for k, field in layers.items():
            for t in field.triggers:
                triggers.append(f"[{k.value}] {t}")
        
        return FieldState(
            coherence=coherence,
            friction=min(1, friction),
            volatility=volatility,
            sustainability=sustainability,
            triggers=triggers[:5],  # 最多5個觸發點
            source="時運場疊加"
        )
    
    def analyze(
        self,
        target_date: date,
        layers: Dict[FieldLayer, FieldState]
    ) -> TimelineField:
        """
        完整時運場分析
        """
        # 疊加計算
        stacked = self.stack_fields(layers)
        
        # 提取亮點
        highlights = []
        for layer, field in layers.items():
            if field.coherence > 0.5:
                highlights.append(f"{layer.value}場態佳，共振度高")
            if field.sustainability > 0.7:
                highlights.append(f"{layer.value}穩定持久")
        
        # 提取警告
        warnings = []
        for layer, field in layers.items():
            if field.friction > 0.5:
                warnings.append(f"{layer.value}阻力大")
            if field.volatility > 0.6:
                warnings.append(f"{layer.value}波動劇烈")
            for t in field.triggers:
                if "剋" in t or "沖" in t:
                    warnings.append(f"{layer.value}: {t}")
        
        return TimelineField(
            target_date=target_date,
            layers=layers,
            weights=self.weights,
            stacked_field=stacked,
            highlights=highlights[:3],
            warnings=warnings[:3]
        )


# =============================================================================
# L4: FieldEngine - 統一場論引擎
# =============================================================================

class FieldEngine:
    """
    北斗統一場論引擎
    
    整合三子系統：
        - FieldRelation: 人際場量化
        - FieldDecision: 決策場引擎
        - FieldTimeline: 時運場疊加
        
    📚 知識點：
        人 = 場
        人際 = 場與場的接觸
        決策 = 場態評估
        時運 = 場的疊加
        
        「道 = 元迷因 = XTF∞」
        「場增則聚，場損則離」
    """
    
    VERSION = "1.0.0"
    AUTHOR = "北斗七星文創 × 織明"
    
    def __init__(self):
        self.relation = FieldRelation()
        self.decision = FieldDecision()
        self.timeline = FieldTimeline()
        self.wx_converter = WuxingFieldConverter()
    
    # -------------------------------------------------------------------------
    # 術數 → 場態轉換器
    # -------------------------------------------------------------------------
    
    def bazi_to_field(
        self,
        bazi_chart: Dict,
        focus: str = "日主"
    ) -> FieldState:
        """
        八字 → 場態
        
        Args:
            bazi_chart: 八字命盤數據
            focus: 關注點（日主/五行/十神）
            
        📚 知識點：
            八字的場論解讀：
            - 日主 = 場的核心
            - 五行分布 = 場的結構
            - 十神配置 = 場的功能
        """
        # 提取五行分布
        wx_profile = bazi_chart.get("wuxing_profile", {
            "木": 0.2, "火": 0.2, "土": 0.2, "金": 0.2, "水": 0.2
        })
        
        field = self.wx_converter.wuxing_to_field(wx_profile)
        
        # 根據格局調整
        pattern = bazi_chart.get("pattern", "")
        if "旺" in pattern:
            field.coherence += 0.2
        if "弱" in pattern:
            field.friction += 0.2
        
        # 加入日主資訊
        day_master = bazi_chart.get("day_master", "")
        if day_master:
            field.triggers.append(f"日主{day_master}")
        
        field.source = "八字"
        field.raw_data = bazi_chart
        
        return field
    
    def yijing_to_field(
        self,
        gua_result: Dict
    ) -> FieldState:
        """
        易經 → 場態
        
        📚 知識點：
            「卦 = 場的狀態」
            「爻 = 場的時間切片」
            「變卦 = 場的轉移」
            「動爻 = 場的變化觸發點」
        """
        ben_gua = gua_result.get("ben_gua", "")
        bian_gua = gua_result.get("bian_gua", "")
        dong_yao = gua_result.get("dong_yao", [])
        
        # 動爻數量影響波動度
        volatility = len(dong_yao) * 0.15
        
        # 本卦判斷基礎場態（簡化版）
        coherence = 0.3  # 預設中性
        if ben_gua in ["乾", "泰", "既濟"]:
            coherence = 0.6
        elif ben_gua in ["坤", "否", "未濟"]:
            coherence = -0.2
        
        # 變卦表示趨勢
        sustainability = 0.5
        if bian_gua and bian_gua != ben_gua:
            sustainability = 0.3  # 有變化，持續度降低
        
        triggers = []
        if dong_yao:
            triggers.append(f"動爻：{'/'.join(map(str, dong_yao))}")
        if bian_gua and bian_gua != ben_gua:
            triggers.append(f"變{bian_gua}")
        
        return FieldState(
            coherence=coherence,
            friction=0.2,
            volatility=min(1, volatility),
            sustainability=sustainability,
            triggers=triggers,
            source="易經",
            raw_data=gua_result
        )
    
    def ziwei_to_field(
        self,
        ziwei_chart: Dict,
        palace: str = "命宮"
    ) -> FieldState:
        """
        紫微 → 場態
        
        📚 知識點：
            紫微的場論解讀：
            - 命宮 = 場的本質
            - 身宮 = 場的表現
            - 十二宮 = 場的不同面向
        """
        palace_data = ziwei_chart.get("palaces", {}).get(palace, {})
        
        main_stars = palace_data.get("main_stars", [])
        sihua = palace_data.get("sihua", [])
        
        # 主星判斷基礎場態
        coherence = 0.3
        if "紫微" in main_stars or "天府" in main_stars:
            coherence = 0.5
        if "貪狼" in main_stars or "廉貞" in main_stars:
            coherence = 0.2
        
        # 四化影響
        friction = 0.2
        volatility = 0.2
        triggers = []
        
        for sh in sihua:
            if "祿" in sh:
                coherence += 0.15
            if "權" in sh:
                volatility += 0.1
            if "科" in sh:
                friction -= 0.1
            if "忌" in sh:
                friction += 0.2
                triggers.append(f"化忌：{sh}")
        
        return FieldState(
            coherence=min(1, max(-1, coherence)),
            friction=min(1, max(0, friction)),
            volatility=min(1, volatility),
            sustainability=0.6,
            triggers=triggers,
            source=f"紫微-{palace}",
            raw_data=palace_data
        )
    
    def merge_fields(
        self,
        fields: List[FieldState],
        weights: List[float] = None
    ) -> FieldState:
        """
        多場合併
        
        📚 知識點：
            多術數疊加：場態合成 = Σ術數 → 場論維度同構收斂
            「術數非裁決律：術數關係 = ¬互相裁決」
        """
        if not fields:
            return FieldState()
        
        if weights is None:
            weights = [1.0] * len(fields)
        
        total_weight = sum(weights)
        if total_weight == 0:
            return FieldState()
        
        # 加權合併
        coherence = sum(f.coherence * w for f, w in zip(fields, weights)) / total_weight
        friction = sum(f.friction * w for f, w in zip(fields, weights)) / total_weight
        volatility = sum(f.volatility * w for f, w in zip(fields, weights)) / total_weight
        sustainability = sum(f.sustainability * w for f, w in zip(fields, weights)) / total_weight
        
        # 合併觸發點
        triggers = []
        for f in fields:
            triggers.extend(f.triggers)
        
        return FieldState(
            coherence=coherence,
            friction=friction,
            volatility=volatility,
            sustainability=sustainability,
            triggers=triggers[:5],
            source="多場合併",
            raw_data={"sources": [f.source for f in fields]}
        )
    
    # -------------------------------------------------------------------------
    # 統一分析入口
    # -------------------------------------------------------------------------
    
    def analyze_relation(
        self,
        person_a: str,
        person_b: str,
        data_a: Dict,
        data_b: Dict,
        source_type: str = "bazi"
    ) -> RelationField:
        """
        人際場分析入口
        """
        # 轉換為場態
        if source_type == "bazi":
            field_a = self.bazi_to_field(data_a)
            field_b = self.bazi_to_field(data_b)
            wx_a = data_a.get("wuxing_profile")
            wx_b = data_b.get("wuxing_profile")
        else:
            field_a = FieldState(**data_a) if isinstance(data_a, dict) else data_a
            field_b = FieldState(**data_b) if isinstance(data_b, dict) else data_b
            wx_a = wx_b = None
        
        return self.relation.analyze(
            person_a, person_b,
            field_a, field_b,
            wx_a, wx_b
        )
    
    def analyze_decision(
        self,
        question: str,
        options: List[str],
        base_data: Dict,
        timeline_data: Dict = None,
        source_type: str = "bazi"
    ) -> DecisionField:
        """
        決策場分析入口
        """
        if source_type == "bazi":
            base_field = self.bazi_to_field(base_data)
        elif source_type == "yijing":
            base_field = self.yijing_to_field(base_data)
        else:
            base_field = FieldState(**base_data) if isinstance(base_data, dict) else base_data
        
        timeline_field = None
        if timeline_data:
            timeline_field = FieldState(**timeline_data) if isinstance(timeline_data, dict) else timeline_data
        
        return self.decision.analyze(
            question, options,
            base_field, timeline_field
        )
    
    def analyze_timeline(
        self,
        target_date: date,
        layer_data: Dict[str, Dict]
    ) -> TimelineField:
        """
        時運場分析入口
        """
        layers = {}
        for layer_name, data in layer_data.items():
            layer = FieldLayer(layer_name)
            if isinstance(data, FieldState):
                layers[layer] = data
            else:
                # 假設是易經數據
                layers[layer] = self.yijing_to_field(data)
        
        return self.timeline.analyze(target_date, layers)
    
    def full_analysis(
        self,
        person: str,
        bazi_data: Dict,
        yijing_data: Dict = None,
        ziwei_data: Dict = None,
        target_date: date = None
    ) -> Dict:
        """
        完整場論分析
        
        整合八字、易經、紫微，輸出統一場態報告
        """
        result = {
            "person": person,
            "timestamp": datetime.now().isoformat(),
            "fields": {},
            "merged_field": None,
            "advice": []
        }
        
        fields = []
        weights = []
        
        # 八字場
        if bazi_data:
            bazi_field = self.bazi_to_field(bazi_data)
            result["fields"]["八字"] = bazi_field.to_dict()
            fields.append(bazi_field)
            weights.append(0.4)
        
        # 易經場
        if yijing_data:
            yijing_field = self.yijing_to_field(yijing_data)
            result["fields"]["易經"] = yijing_field.to_dict()
            fields.append(yijing_field)
            weights.append(0.35)
        
        # 紫微場
        if ziwei_data:
            ziwei_field = self.ziwei_to_field(ziwei_data)
            result["fields"]["紫微"] = ziwei_field.to_dict()
            fields.append(ziwei_field)
            weights.append(0.25)
        
        # 合併場
        if fields:
            merged = self.merge_fields(fields, weights)
            result["merged_field"] = merged.to_dict()
            
            # 生成建議
            if merged.field_score > 70:
                result["advice"].append("場態良好，順勢而為，積極行動")
            elif merged.field_score > 50:
                result["advice"].append("場態中性，穩健推進，量力而行")
            else:
                result["advice"].append("場態低迷，蓄勢待發，修煉自場")
            
            for trigger in merged.triggers:
                result["advice"].append(f"關注：{trigger}")
        
        return result


# =============================================================================
# L4: CLI 入口
# =============================================================================

def main():
    """CLI 入口"""
    print("=" * 60)
    print("北斗統一場論引擎 v1.0")
    print("=" * 60)
    
    engine = FieldEngine()
    
    # 示例：北斗的八字場態
    beidou_bazi = {
        "day_master": "庚金",
        "pattern": "傷官生財格",
        "wuxing_profile": {
            "木": 0.15,  # 甲乙
            "火": 0.05,  # 缺火
            "土": 0.20,  # 丑
            "金": 0.30,  # 庚辛酉
            "水": 0.30   # 癸子×2
        }
    }
    
    bazi_field = engine.bazi_to_field(beidou_bazi)
    
    print("\n【北斗八字場態】")
    print(json.dumps(bazi_field.to_dict(), ensure_ascii=False, indent=2))
    
    # 示例：決策分析
    print("\n【決策場分析】")
    decision = engine.analyze_decision(
        question="今日是否適合重要會議？",
        options=["進行", "延後", "線上"],
        base_data=beidou_bazi,
        source_type="bazi"
    )
    print(json.dumps(decision.to_dict(), ensure_ascii=False, indent=2))
    
    print("\n" + "=" * 60)
    print("場論核心：場增則聚，場損則離")
    print("=" * 60)


if __name__ == "__main__":
    main()


# =============================================================================
# 📚 知識點總結
# =============================================================================
"""
【場論核心公式】

1. 人際場公式：
   - 共振度 = f(頻率相似度, 五行生剋, 卦象呼應)
   - 場增減 = 1+1>2 (共振) | 1+1<2 (消耗)
   - 場演化 = 同步率 × 時間

2. 決策場公式：
   - 最優選擇 = argmax(場強)
   - 場不逆操 = 順勢而為
   - 吉凶 = 場態評估，不是命定

3. 時運場公式：
   - 場疊加 = Σ(各層場態 × 權重)
   - 週期 = 蓄積→釋放→過度→回落

【場接觸四態】
   - 共振：頻率相近，懂、舒適、吸引
   - 干涉：頻率相差，隔、不適、衝突
   - 疊加：互相影響，化、改變、成長
   - 邊界：保持距離，守、尊重、獨立

【相處四模式】
   - 共振場：互相增益，1+1>2，如知己
   - 互補場：剛柔相濟，各補缺失，如伴侶
   - 平行場：互不干涉，各自精彩，如同事
   - 消耗場：互相損耗，1+1<2，需距離

【織明語錄】
   - 「一見如故，不是看對眼，是場對頻」
   - 「相處疲憊，不是不合適，是場耗損」
   - 「緣起則聚，緣盡則散」
   - 「長久不是不變，是同步演化」
   - 「場增則聚，場損則離」
"""
