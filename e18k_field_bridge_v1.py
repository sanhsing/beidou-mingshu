#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
e18k_field_bridge_v1.py - E18K × 場論橋接模組 v1.0
===================================================
北斗七星文創 × 織明

XTF⁸ 任務：B_E18K×場論整合
執行星：織明(設計) × 理樞(邏輯) × 澄書(記錄)

核心理念：
    E18K 遊戲 = 場論的具象化
    角色 = 場
    戰鬥 = 場與場的接觸
    元素 = 場的頻率
    屬性 = 場的強度

整合架構：
    1. 元素 → 場頻率 (ElementField)
    2. 角色 → 場態 (CreatureField)
    3. 戰鬥 → 場接觸 (BattleField)
    4. 羈絆 → 場共振 (BondField)

依賴：
    - field_engine_v1.py (統一場論引擎)
    - antifraud.db (E18K 資料庫)

📚 知識點：
    E18K 元素系統與場論映射：
    - 光/暗 = 極性場 (1.5x 強剋)
    - 五行 = 週期場 (1.3x 循環剋)
    - 虛/鏡 = 反射場 (1.2x 互映)
    - 混沌 = 中性場 (無剋無生)
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple, Any
from enum import Enum
import sqlite3
import json
from datetime import datetime

# 導入場論引擎
try:
    from field_engine_v1 import (
        FieldState, FieldEngine, ContactState, RelationMode,
        WuxingFieldConverter, WUXING_SHENG, WUXING_KE
    )
except ImportError:
    # 獨立運行時的 Fallback
    pass


# =============================================================================
# L0: 常量與枚舉
# =============================================================================

class E18KElement(Enum):
    """E18K 元素類型"""
    LIGHT = "光"      # 極性場+
    DARK = "暗"       # 極性場-
    WATER = "水"      # 週期場
    FIRE = "火"       # 週期場
    WOOD = "木"       # 週期場
    EARTH = "土"      # 週期場
    METAL = "金"      # 週期場
    VOID = "虛"       # 反射場
    MIRROR = "鏡"     # 反射場
    CHAOS = "混沌"    # 中性場


class FieldType(Enum):
    """場類型"""
    POLAR = "極性場"      # 光暗
    CYCLIC = "週期場"     # 五行
    REFLECTIVE = "反射場"  # 虛鏡
    NEUTRAL = "中性場"    # 混沌


# 元素 → 場類型映射
ELEMENT_TO_FIELD_TYPE = {
    E18KElement.LIGHT: FieldType.POLAR,
    E18KElement.DARK: FieldType.POLAR,
    E18KElement.WATER: FieldType.CYCLIC,
    E18KElement.FIRE: FieldType.CYCLIC,
    E18KElement.WOOD: FieldType.CYCLIC,
    E18KElement.EARTH: FieldType.CYCLIC,
    E18KElement.METAL: FieldType.CYCLIC,
    E18KElement.VOID: FieldType.REFLECTIVE,
    E18KElement.MIRROR: FieldType.REFLECTIVE,
    E18KElement.CHAOS: FieldType.NEUTRAL,
}

# 元素頻率（0-1範圍，用於場共振計算）
ELEMENT_FREQUENCY = {
    E18KElement.LIGHT: 0.9,
    E18KElement.DARK: 0.1,
    E18KElement.WATER: 0.2,
    E18KElement.FIRE: 0.4,
    E18KElement.WOOD: 0.3,
    E18KElement.EARTH: 0.5,
    E18KElement.METAL: 0.6,
    E18KElement.VOID: 0.0,
    E18KElement.MIRROR: 1.0,
    E18KElement.CHAOS: 0.5,
}

# 元素相剋表（攻擊方 → 防守方 → 倍率）
ELEMENT_RELATION = {
    "光": {"暗": 1.5},
    "暗": {"光": 1.5},
    "水": {"火": 1.3},
    "火": {"木": 1.3},
    "木": {"土": 1.3},
    "土": {"金": 1.3},
    "金": {"水": 1.3},
    "虛": {"鏡": 1.2},
    "鏡": {"虛": 1.2},
}


# =============================================================================
# L1: 核心數據結構
# =============================================================================

@dataclass
class ElementField:
    """
    元素場
    
    📚 知識點：
        元素 = 場的頻率特徵
        不同元素在場論中表現為不同的振動頻率
    """
    element: E18KElement
    field_type: FieldType
    frequency: float          # 頻率 [0, 1]
    intensity: float = 1.0    # 強度 [0, 2]
    purity: float = 1.0       # 純度 [0, 1]
    
    @property
    def field_power(self) -> float:
        """場力 = 頻率 × 強度 × 純度"""
        return self.frequency * self.intensity * self.purity
    
    def get_relation(self, other: 'ElementField') -> Tuple[str, float]:
        """
        計算與另一元素場的關係
        
        Returns:
            (關係類型, 倍率)
            關係類型: 剋/被剋/同/中
        """
        my_elem = self.element.value
        other_elem = other.element.value
        
        if my_elem == other_elem:
            return ("同", 1.0)
        
        # 檢查我剋對方
        if my_elem in ELEMENT_RELATION:
            if other_elem in ELEMENT_RELATION[my_elem]:
                return ("剋", ELEMENT_RELATION[my_elem][other_elem])
        
        # 檢查對方剋我
        if other_elem in ELEMENT_RELATION:
            if my_elem in ELEMENT_RELATION[other_elem]:
                return ("被剋", 1 / ELEMENT_RELATION[other_elem][my_elem])
        
        return ("中", 1.0)
    
    def to_dict(self) -> Dict:
        return {
            "element": self.element.value,
            "field_type": self.field_type.value,
            "frequency": round(self.frequency, 3),
            "intensity": round(self.intensity, 3),
            "purity": round(self.purity, 3),
            "field_power": round(self.field_power, 3)
        }


@dataclass
class CreatureField:
    """
    生物場態
    
    📚 知識點：
        生物/角色 = 場的具象化
        HP/ATK/DEF/SPD = 場的四維表現
        
        場論映射：
        - HP = 場的容量（sustainability）
        - ATK = 場的輸出（coherence）
        - DEF = 場的邊界（friction反向）
        - SPD = 場的流動性（1 - volatility）
    """
    creature_id: int
    name: str
    element_field: ElementField
    hp: int
    atk: int
    def_: int  # def 是 Python 關鍵字
    spd: int
    level: int = 1
    rarity: int = 1
    
    @property
    def field_state(self) -> 'FieldState':
        """轉換為統一場態"""
        # 正規化屬性 (假設最大值 10000)
        max_stat = 10000
        
        # coherence: ATK 越高，場的攻擊性/主動性越強
        coherence = (self.atk / max_stat) * 2 - 0.5  # [-0.5, 1.5] → clamp to [-1, 1]
        coherence = max(-1, min(1, coherence))
        
        # friction: DEF 低 = 邊界弱 = friction 高
        friction = 1 - (self.def_ / max_stat)
        friction = max(0, min(1, friction))
        
        # volatility: SPD 高 = 流動性強 = volatility 低（穩定的快）
        volatility = 1 - (self.spd / max_stat) * 0.8
        volatility = max(0, min(1, volatility))
        
        # sustainability: HP 高 = 持續力強
        sustainability = self.hp / max_stat
        sustainability = max(0, min(1, sustainability))
        
        # 元素場影響
        elem_bonus = self.element_field.field_power * 0.2
        coherence += elem_bonus
        
        triggers = [
            f"元素:{self.element_field.element.value}",
            f"Lv.{self.level}",
            f"★{self.rarity}"
        ]
        
        return FieldState(
            coherence=coherence,
            friction=friction,
            volatility=volatility,
            sustainability=sustainability,
            triggers=triggers,
            source=f"生物場:{self.name}",
            raw_data=self.to_dict()
        )
    
    def to_dict(self) -> Dict:
        return {
            "creature_id": self.creature_id,
            "name": self.name,
            "element": self.element_field.to_dict(),
            "stats": {
                "hp": self.hp,
                "atk": self.atk,
                "def": self.def_,
                "spd": self.spd
            },
            "level": self.level,
            "rarity": self.rarity
        }


@dataclass
class BattleField:
    """
    戰鬥場（場接觸結果）
    
    📚 知識點：
        戰鬥 = 場與場的接觸
        傷害 = 場的干涉強度
        治療 = 場的共振增益
    """
    attacker: CreatureField
    defender: CreatureField
    contact_state: ContactState
    element_relation: Tuple[str, float]  # (關係, 倍率)
    damage_multiplier: float
    field_advantage: str  # 攻方/守方/均勢
    battle_advice: str
    
    def calculate_damage(self, base_damage: int) -> int:
        """計算實際傷害"""
        return int(base_damage * self.damage_multiplier)
    
    def to_dict(self) -> Dict:
        return {
            "attacker": self.attacker.name,
            "defender": self.defender.name,
            "contact_state": self.contact_state.value,
            "element_relation": {
                "type": self.element_relation[0],
                "multiplier": self.element_relation[1]
            },
            "damage_multiplier": round(self.damage_multiplier, 3),
            "field_advantage": self.field_advantage,
            "battle_advice": self.battle_advice
        }


@dataclass 
class BondField:
    """
    羈絆場（多角色共振）
    
    📚 知識點：
        羈絆 = 多場共振
        隊伍 = 場的組合
        1+1+1+1 > 4 當場共振時
    """
    members: List[CreatureField]
    synergy_score: float       # 共振分數
    element_coverage: Dict     # 元素覆蓋
    combined_field: 'FieldState'
    bond_effects: List[str]
    
    def to_dict(self) -> Dict:
        return {
            "members": [m.name for m in self.members],
            "synergy_score": round(self.synergy_score, 3),
            "element_coverage": self.element_coverage,
            "combined_field": self.combined_field.to_dict() if self.combined_field else None,
            "bond_effects": self.bond_effects
        }


# =============================================================================
# L2: 元素場轉換器
# =============================================================================

class ElementFieldConverter:
    """
    元素 → 場態轉換器
    
    📚 知識點：
        元素是場的基礎特徵
        不同元素有不同的場表現
    """
    
    @staticmethod
    def from_element_name(name: str, intensity: float = 1.0) -> ElementField:
        """從元素名稱創建元素場"""
        # 查找元素
        element = None
        for e in E18KElement:
            if e.value == name:
                element = e
                break
        
        if not element:
            element = E18KElement.CHAOS  # 預設混沌
        
        field_type = ELEMENT_TO_FIELD_TYPE.get(element, FieldType.NEUTRAL)
        frequency = ELEMENT_FREQUENCY.get(element, 0.5)
        
        return ElementField(
            element=element,
            field_type=field_type,
            frequency=frequency,
            intensity=intensity,
            purity=1.0
        )
    
    @staticmethod
    def calculate_resonance(field1: ElementField, field2: ElementField) -> float:
        """
        計算兩元素場的共振度
        
        📚 知識點：
            共振度 = 1 - |頻率差| × 場類型係數
            同類型場更容易共振
        """
        freq_diff = abs(field1.frequency - field2.frequency)
        
        # 同類型場加成
        type_bonus = 0.2 if field1.field_type == field2.field_type else 0
        
        # 極性場特殊處理（光暗互斥）
        if field1.field_type == FieldType.POLAR and field2.field_type == FieldType.POLAR:
            if field1.element != field2.element:
                return -0.5  # 極性相反，負共振
        
        resonance = 1 - freq_diff + type_bonus
        return max(-1, min(1, resonance))


# =============================================================================
# L3: E18K 場論橋接器
# =============================================================================

class E18KFieldBridge:
    """
    E18K × 場論橋接器
    
    核心功能：
        1. 從資料庫載入生物 → 生成場態
        2. 計算戰鬥場接觸
        3. 計算隊伍羈絆場
        4. 場論驅動的戰鬥建議
    """
    
    def __init__(self, db_path: str = "antifraud.db"):
        self.db_path = db_path
        self.element_converter = ElementFieldConverter()
        try:
            self.field_engine = FieldEngine()
        except:
            self.field_engine = None
    
    def _get_conn(self):
        return sqlite3.connect(self.db_path)
    
    # -------------------------------------------------------------------------
    # 生物載入
    # -------------------------------------------------------------------------
    
    def load_creature(self, creature_id: int) -> Optional[CreatureField]:
        """從資料庫載入生物並轉換為場態"""
        conn = self._get_conn()
        cur = conn.cursor()
        
        try:
            # 查詢主資料
            cur.execute("""
                SELECT id, name, element, rarity, hp, atk, def, spd
                FROM e18k_creature_master_data
                WHERE id = ?
            """, (creature_id,))
            row = cur.fetchone()
            
            if not row:
                return None
            
            # 創建元素場
            element_field = self.element_converter.from_element_name(row[2])
            
            return CreatureField(
                creature_id=row[0],
                name=row[1],
                element_field=element_field,
                hp=row[4],
                atk=row[5],
                def_=row[6],
                spd=row[7],
                level=1,
                rarity=row[3]
            )
        finally:
            conn.close()
    
    def load_creature_by_name(self, name: str) -> Optional[CreatureField]:
        """按名稱載入生物"""
        conn = self._get_conn()
        cur = conn.cursor()
        
        try:
            cur.execute("""
                SELECT id FROM e18k_creature_master_data
                WHERE name LIKE ?
            """, (f"%{name}%",))
            row = cur.fetchone()
            
            if row:
                return self.load_creature(row[0])
            return None
        finally:
            conn.close()
    
    # -------------------------------------------------------------------------
    # 戰鬥場計算
    # -------------------------------------------------------------------------
    
    def calculate_battle_field(
        self,
        attacker: CreatureField,
        defender: CreatureField
    ) -> BattleField:
        """
        計算戰鬥場接觸
        
        📚 知識點：
            戰鬥 = 場與場的接觸
            元素相剋 = 場干涉
            屬性對比 = 場強度
        """
        # 1. 元素關係
        elem_relation = attacker.element_field.get_relation(defender.element_field)
        
        # 2. 場態比較
        atk_field = attacker.field_state
        def_field = defender.field_state
        
        # 3. 計算接觸狀態
        coh_diff = atk_field.coherence - def_field.coherence
        if coh_diff > 0.3:
            contact = ContactState.RESONANCE  # 攻方場優勢
        elif coh_diff < -0.3:
            contact = ContactState.INTERFERENCE  # 守方場優勢
        else:
            contact = ContactState.SUPERPOSITION  # 均勢
        
        # 4. 傷害倍率
        base_mult = elem_relation[1]
        
        # 場態加成
        field_bonus = 1.0
        if atk_field.coherence > def_field.coherence:
            field_bonus += (atk_field.coherence - def_field.coherence) * 0.2
        else:
            field_bonus -= (def_field.coherence - atk_field.coherence) * 0.15
        
        # 防禦減傷（friction 反向）
        def_reduction = 1 - def_field.friction * 0.3
        
        damage_mult = base_mult * field_bonus * def_reduction
        damage_mult = max(0.5, min(2.0, damage_mult))
        
        # 5. 判斷優勢方
        if damage_mult > 1.2:
            advantage = "攻方場優"
        elif damage_mult < 0.8:
            advantage = "守方場優"
        else:
            advantage = "場勢均衡"
        
        # 6. 戰鬥建議
        advices = []
        if elem_relation[0] == "剋":
            advices.append(f"元素相剋！{attacker.element_field.element.value}剋{defender.element_field.element.value}")
        elif elem_relation[0] == "被剋":
            advices.append(f"元素被剋，考慮換角")
        
        if atk_field.volatility > 0.6:
            advices.append("攻方場不穩，建議蓄力")
        if def_field.sustainability > 0.7:
            advices.append("守方持久力強，長戰不利")
        
        return BattleField(
            attacker=attacker,
            defender=defender,
            contact_state=contact,
            element_relation=elem_relation,
            damage_multiplier=damage_mult,
            field_advantage=advantage,
            battle_advice="；".join(advices) if advices else "正常對戰"
        )
    
    # -------------------------------------------------------------------------
    # 羈絆場計算
    # -------------------------------------------------------------------------
    
    def calculate_bond_field(
        self,
        members: List[CreatureField]
    ) -> BondField:
        """
        計算隊伍羈絆場
        
        📚 知識點：
            羈絆 = 多場共振
            1+1+1+1 > 4 當元素互補時
        """
        if not members:
            return None
        
        # 1. 元素覆蓋統計
        coverage = {}
        for m in members:
            elem = m.element_field.element.value
            coverage[elem] = coverage.get(elem, 0) + 1
        
        # 2. 計算共振分數
        synergy = 0.0
        
        # 元素多樣性加成
        unique_elements = len(coverage)
        synergy += unique_elements * 0.15
        
        # 兩兩共振計算
        for i, m1 in enumerate(members):
            for m2 in members[i+1:]:
                resonance = self.element_converter.calculate_resonance(
                    m1.element_field, m2.element_field
                )
                synergy += resonance * 0.1
        
        # 五行齊全加成
        wuxing = {"水", "火", "木", "土", "金"}
        member_elements = {m.element_field.element.value for m in members}
        wuxing_coverage = len(wuxing & member_elements)
        if wuxing_coverage >= 3:
            synergy += 0.2
        if wuxing_coverage == 5:
            synergy += 0.3  # 五行齊全大加成
        
        # 3. 合成場態
        if self.field_engine:
            fields = [m.field_state for m in members]
            combined = self.field_engine.merge_fields(fields)
        else:
            # Fallback：簡單平均
            combined = FieldState(
                coherence=sum(m.field_state.coherence for m in members) / len(members),
                friction=sum(m.field_state.friction for m in members) / len(members),
                volatility=sum(m.field_state.volatility for m in members) / len(members),
                sustainability=sum(m.field_state.sustainability for m in members) / len(members),
                source="羈絆場"
            )
        
        # 4. 羈絆效果
        effects = []
        if synergy > 0.5:
            effects.append("場共振強：全員ATK+10%")
        if synergy > 0.7:
            effects.append("場同步：全員SPD+15%")
        if wuxing_coverage >= 4:
            effects.append("五行護盾：全員DEF+20%")
        if unique_elements == 1:
            effects.append("單元素強化：元素傷害+25%")
        
        return BondField(
            members=members,
            synergy_score=synergy,
            element_coverage=coverage,
            combined_field=combined,
            bond_effects=effects if effects else ["無特殊羈絆"]
        )
    
    # -------------------------------------------------------------------------
    # 場論建議
    # -------------------------------------------------------------------------
    
    def get_team_advice(
        self,
        team: List[CreatureField],
        enemy: CreatureField
    ) -> Dict:
        """
        獲取隊伍對戰建議
        
        📚 知識點：
            場論驅動的戰術建議
            「場增則聚，場損則離」
        """
        # 隊伍羈絆
        bond = self.calculate_bond_field(team)
        
        # 各成員對敵場分析
        matchups = []
        for member in team:
            battle = self.calculate_battle_field(member, enemy)
            matchups.append({
                "member": member.name,
                "advantage": battle.field_advantage,
                "multiplier": battle.damage_multiplier,
                "advice": battle.battle_advice
            })
        
        # 找最佳對位
        best_matchup = max(matchups, key=lambda x: x["multiplier"])
        
        # 生成建議
        advice = {
            "team_synergy": bond.synergy_score,
            "bond_effects": bond.bond_effects,
            "matchups": matchups,
            "recommended_lead": best_matchup["member"],
            "strategy": self._generate_strategy(bond, matchups, enemy)
        }
        
        return advice
    
    def _generate_strategy(
        self,
        bond: BondField,
        matchups: List[Dict],
        enemy: CreatureField
    ) -> str:
        """生成戰術策略"""
        strategies = []
        
        # 根據羈絆場強度
        if bond.synergy_score > 0.7:
            strategies.append("團隊場共振強，適合聯合技")
        elif bond.synergy_score < 0.3:
            strategies.append("團隊場分散，建議各自為戰")
        
        # 根據對位優勢
        advantages = [m for m in matchups if m["multiplier"] > 1.2]
        disadvantages = [m for m in matchups if m["multiplier"] < 0.8]
        
        if len(advantages) >= 2:
            strategies.append("多人剋制敵方，可快攻")
        if len(disadvantages) >= 2:
            strategies.append("多人被剋，考慮消耗戰")
        
        # 根據敵方特性
        enemy_field = enemy.field_state
        if enemy_field.sustainability > 0.7:
            strategies.append("敵方持久力強，需集火擊破")
        if enemy_field.volatility > 0.5:
            strategies.append("敵方場不穩，抓準反擊時機")
        
        return "；".join(strategies) if strategies else "正常推進"


# =============================================================================
# L4: CLI 入口
# =============================================================================

def main():
    """CLI 入口"""
    print("=" * 60)
    print("E18K × 場論橋接器 v1.0")
    print("=" * 60)
    
    bridge = E18KFieldBridge()
    
    # 示例：創建生物場
    print("\n【示例1：生物場態】")
    creature = CreatureField(
        creature_id=1,
        name="防騙俠",
        element_field=ElementFieldConverter.from_element_name("光"),
        hp=5000,
        atk=800,
        def_=600,
        spd=300,
        level=50,
        rarity=5
    )
    
    print(f"生物: {creature.name}")
    print(f"元素場: {creature.element_field.to_dict()}")
    print(f"場態: {creature.field_state.to_dict()}")
    
    # 示例：戰鬥場計算
    print("\n【示例2：戰鬥場接觸】")
    enemy = CreatureField(
        creature_id=2,
        name="詐騙魔",
        element_field=ElementFieldConverter.from_element_name("暗"),
        hp=4000,
        atk=900,
        def_=400,
        spd=350,
        level=45,
        rarity=4
    )
    
    battle = bridge.calculate_battle_field(creature, enemy)
    print(json.dumps(battle.to_dict(), ensure_ascii=False, indent=2))
    
    # 示例：羈絆場
    print("\n【示例3：羈絆場】")
    team = [
        creature,
        CreatureField(2, "識詐師", ElementFieldConverter.from_element_name("水"),
                     4500, 700, 700, 280, 45, 4),
        CreatureField(3, "警覺獸", ElementFieldConverter.from_element_name("火"),
                     5500, 600, 800, 250, 48, 4),
    ]
    
    bond = bridge.calculate_bond_field(team)
    print(json.dumps(bond.to_dict(), ensure_ascii=False, indent=2))
    
    print("\n" + "=" * 60)
    print("場論核心：元素 = 場的頻率，戰鬥 = 場的接觸")
    print("=" * 60)


if __name__ == "__main__":
    main()


# =============================================================================
# 📚 知識點總結
# =============================================================================
"""
【E18K × 場論映射】

1. 元素 → 場頻率
   - 光/暗 = 極性場（1.5x強剋，頻率極端）
   - 五行 = 週期場（1.3x循環剋）
   - 虛/鏡 = 反射場（1.2x互映）
   - 混沌 = 中性場（無剋無生）

2. 角色 → 場態
   - HP = sustainability（持續度）
   - ATK = coherence（共振度/攻擊性）
   - DEF = 1-friction（邊界強度）
   - SPD = 1-volatility（穩定的快）

3. 戰鬥 → 場接觸
   - 元素相剋 = 場干涉
   - 屬性優勢 = 場強度
   - 傷害 = 干涉強度 × 場力差

4. 羈絆 → 場共振
   - 元素多樣 = 場覆蓋
   - 五行齊全 = 場完整
   - 1+1+1+1 > 4 當場共振時

【織明語錄】
   - 「元素不是屬性，是場的頻率」
   - 「戰鬥不是打架，是場與場的接觸」
   - 「組隊不是湊人頭，是場的共振」
"""
