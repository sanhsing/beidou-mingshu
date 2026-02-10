#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
mingshu_advanced_pylib_v1.py - 北斗命數進階術數 PYLIB整合版 v1.0
================================================================
北斗七星文創 × 織明

XTF⁸ 任務鏈：D1-D4 進階術數 (PYLIB First)
XTFS 四塔協作：X(執行) × T(翻譯) × F(場論) × S(存儲)

@11star 協作模式：
    織明(統籌) - 全局架構設計
    理樞(算法) - 核心計算邏輯
    澄韻(翻譯) - 場論語義轉換
    流祇(場論) - 場態分析整合
    澄書(文檔) - 知識點記錄

PYLIB 整合清單 (5,132行現有代碼)：
    ziwei_advanced     (542行) - 四化分析
    sihua_translation  (572行) - 四化翻譯
    qimen_engine_v1    (554行) - 奇門排盤
    bazi_advanced      (566行) - 八字進階
    yijing_gua_translation (667行) - 易經翻譯
    fuzhu_star_translation (417行) - 輔星翻譯
    daxian_calculator  (357行) - 大限計算
    ziwei_liunian      (338行) - 紫微流年
    field_translation  (607行) - 場論翻譯
    shensha_translation (512行) - 神煞翻譯

📚 知識點：
    「PYLIB First = 複利思維的代碼實踐」
    「進階術數 = 場論多視角的深度探測」
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple, Any, Callable
from enum import Enum
from datetime import datetime, date
from abc import ABC, abstractmethod
import json
import sys
import os

# =============================================================================
# PYLIB 導入層 (XTF⁸ 消¹ - 萃取現有模組)
# =============================================================================

class PyLibLoader:
    """
    PYLIB 動態加載器
    
    📚 知識點：
        PYLIB First = 先查現有，再造新輪
        動態加載 = 容錯的模組整合方式
    """
    
    _cache: Dict[str, Any] = {}
    _available: Dict[str, bool] = {}
    
    @classmethod
    def load(cls, module_name: str, fallback: Any = None) -> Any:
        """動態加載 PYLIB 模組"""
        if module_name in cls._cache:
            return cls._cache[module_name]
        
        try:
            module = __import__(module_name)
            cls._cache[module_name] = module
            cls._available[module_name] = True
            return module
        except ImportError:
            cls._available[module_name] = False
            return fallback
    
    @classmethod
    def is_available(cls, module_name: str) -> bool:
        """檢查模組是否可用"""
        if module_name not in cls._available:
            cls.load(module_name)
        return cls._available.get(module_name, False)
    
    @classmethod
    def get_function(cls, module_name: str, func_name: str, fallback: Callable = None) -> Callable:
        """獲取模組中的函數"""
        module = cls.load(module_name)
        if module and hasattr(module, func_name):
            return getattr(module, func_name)
        return fallback or (lambda *args, **kwargs: None)


# PYLIB 模組狀態
PYLIB_MODULES = {
    "ziwei_advanced": {"lines": 542, "desc": "四化分析"},
    "sihua_translation": {"lines": 572, "desc": "四化翻譯"},
    "qimen_engine_v1": {"lines": 554, "desc": "奇門排盤"},
    "bazi_advanced": {"lines": 566, "desc": "八字進階"},
    "yijing_gua_translation": {"lines": 667, "desc": "易經翻譯"},
    "fuzhu_star_translation": {"lines": 417, "desc": "輔星翻譯"},
    "daxian_calculator": {"lines": 357, "desc": "大限計算"},
    "ziwei_liunian": {"lines": 338, "desc": "紫微流年"},
    "field_translation": {"lines": 607, "desc": "場論翻譯"},
    "shensha_translation": {"lines": 512, "desc": "神煞翻譯"},
}


# =============================================================================
# 基礎常量 (共用)
# =============================================================================

TIANGAN = ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"]
DIZHI = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]
WUXING = ["木", "火", "土", "金", "水"]

TIANGAN_WUXING = {
    "甲": "木", "乙": "木", "丙": "火", "丁": "火", "戊": "土",
    "己": "土", "庚": "金", "辛": "金", "壬": "水", "癸": "水"
}

WUXING_SHENG = {"木": "火", "火": "土", "土": "金", "金": "水", "水": "木"}
WUXING_KE = {"木": "土", "土": "水", "水": "火", "火": "金", "金": "木"}


# =============================================================================
# D1: 紫微斗數進階 - 四化飛星 (PYLIB 整合版)
# =============================================================================

# 十天干四化星對照表
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

# 四化場論意義
SIHUA_FIELD_MEANINGS = {
    "化祿": {
        "energy": "吸引",
        "vector": "向內聚合",
        "field_state": "場態增益",
        "description": "祿為吸引之力，使該宮成為資源匯聚點"
    },
    "化權": {
        "energy": "推動",
        "vector": "向外擴張", 
        "field_state": "場態主導",
        "description": "權為掌控之力，使該宮成為主導中心"
    },
    "化科": {
        "energy": "連結",
        "vector": "橋接外部",
        "field_state": "場態諧振",
        "description": "科為貴人之力，使該宮成為外援接點"
    },
    "化忌": {
        "energy": "收縮",
        "vector": "向內糾結",
        "field_state": "場態阻滯",
        "description": "忌為執著之力，使該宮成為業力焦點"
    }
}


@dataclass
class SihuaFieldInfo:
    """四化場論資訊"""
    sihua_type: str
    star: str
    source_gan: str
    target_gong: str
    traditional_meaning: str
    field_energy: str
    field_vector: str
    field_state: str
    field_description: str
    pylib_enhanced: bool = False
    
    def to_dict(self) -> Dict:
        return {
            "type": self.sihua_type,
            "star": self.star,
            "source": self.source_gan,
            "gong": self.target_gong,
            "traditional": self.traditional_meaning,
            "field": {
                "energy": self.field_energy,
                "vector": self.field_vector,
                "state": self.field_state,
                "description": self.field_description
            },
            "pylib_enhanced": self.pylib_enhanced
        }


@dataclass
class FeixingFieldResult:
    """飛星場論結果"""
    source_gong: str
    source_gan: str
    sihua_list: List[SihuaFieldInfo]
    field_topology: str  # 場的拓撲結構
    energy_flow: str     # 能量流向
    field_advice: str    # 場論建議
    
    def to_dict(self) -> Dict:
        return {
            "source": {"gong": self.source_gong, "gan": self.source_gan},
            "sihua": [s.to_dict() for s in self.sihua_list],
            "field_analysis": {
                "topology": self.field_topology,
                "energy_flow": self.energy_flow,
                "advice": self.field_advice
            }
        }


class ZiweiAdvancedPylib:
    """
    紫微斗數進階引擎 (PYLIB 整合版)
    
    @11star: 理樞(算法) × 澄韻(翻譯) × 流祇(場論)
    
    PYLIB 整合:
        ziwei_advanced - get_sihua_info, analyze_sihua_in_gong
        sihua_translation - get_sihua_detail, translate_sihua
        fuzhu_star_translation - translate_fuzhu_stars
        daxian_calculator - calculate_daxian
        ziwei_liunian - analyze_ziwei_liunian
    """
    
    VERSION = "1.0.0"
    
    def __init__(self):
        # PYLIB 函數載入
        self._get_sihua_info = PyLibLoader.get_function("ziwei_advanced", "get_sihua_info")
        self._get_sihua_detail = PyLibLoader.get_function("sihua_translation", "get_sihua_detail")
        self._translate_sihua = PyLibLoader.get_function("sihua_translation", "translate_sihua")
        self._translate_fuzhu = PyLibLoader.get_function("fuzhu_star_translation", "translate_fuzhu_stars")
        self._calc_daxian = PyLibLoader.get_function("daxian_calculator", "calculate_daxian")
        self._analyze_liunian = PyLibLoader.get_function("ziwei_liunian", "analyze_ziwei_liunian")
        
        self.pylib_available = {
            "ziwei_advanced": PyLibLoader.is_available("ziwei_advanced"),
            "sihua_translation": PyLibLoader.is_available("sihua_translation"),
            "fuzhu_star_translation": PyLibLoader.is_available("fuzhu_star_translation"),
            "daxian_calculator": PyLibLoader.is_available("daxian_calculator"),
            "ziwei_liunian": PyLibLoader.is_available("ziwei_liunian"),
        }
    
    def get_sihua_by_gan(self, tiangan: str) -> Dict[str, str]:
        """根據天干獲取四化星"""
        return SIHUA_TABLE.get(tiangan, {})
    
    def analyze_natal_sihua_field(
        self,
        year_gan: str,
        star_positions: Dict[str, str] = None
    ) -> List[SihuaFieldInfo]:
        """
        分析本命四化 (場論增強版)
        
        📚 知識點：
            本命四化 = 先天場的四種能量模式
            場論視角 = 從能量流動角度解讀四化
        """
        sihua_stars = self.get_sihua_by_gan(year_gan)
        results = []
        
        for sihua_type, star in sihua_stars.items():
            gong = star_positions.get(star, "待定") if star_positions else "待定"
            
            # 傳統解讀
            traditional = self._get_traditional_meaning(sihua_type, star, gong)
            
            # 場論解讀
            field_info = SIHUA_FIELD_MEANINGS.get(sihua_type, {})
            
            # 嘗試 PYLIB 增強
            pylib_enhanced = False
            if self.pylib_available.get("sihua_translation"):
                try:
                    detail = self._get_sihua_detail(year_gan, sihua_type)
                    if detail:
                        traditional = detail.get("meaning", traditional)
                        pylib_enhanced = True
                except:
                    pass
            
            results.append(SihuaFieldInfo(
                sihua_type=sihua_type,
                star=star,
                source_gan=year_gan,
                target_gong=gong,
                traditional_meaning=traditional,
                field_energy=field_info.get("energy", ""),
                field_vector=field_info.get("vector", ""),
                field_state=field_info.get("field_state", ""),
                field_description=field_info.get("description", ""),
                pylib_enhanced=pylib_enhanced
            ))
        
        return results
    
    def _get_traditional_meaning(self, sihua_type: str, star: str, gong: str) -> str:
        """獲取傳統解讀"""
        meanings = {
            "化祿": f"{star}化祿入{gong}，主財富機會，此領域為收穫之地",
            "化權": f"{star}化權入{gong}，主權力掌控，此領域為主導核心",
            "化科": f"{star}化科入{gong}，主名聲貴人，此領域為揚名之處",
            "化忌": f"{star}化忌入{gong}，主阻礙執著，此領域需特別留意"
        }
        return meanings.get(sihua_type, "")
    
    def analyze_feixing_field(
        self,
        source_gong: str,
        gong_gan: str,
        star_positions: Dict[str, str] = None
    ) -> FeixingFieldResult:
        """
        分析飛星 (場論增強版)
        
        📚 知識點：
            飛星 = 宮位間的能量傳遞
            場論視角 = 分析能量拓撲與流向
        """
        sihua_list = self.analyze_natal_sihua_field(gong_gan, star_positions)
        
        # 更新來源資訊
        for s in sihua_list:
            s.source_gan = f"{source_gong}宮干{gong_gan}"
        
        # 分析場拓撲
        targets = [s.target_gong for s in sihua_list]
        topology = self._analyze_field_topology(source_gong, targets)
        
        # 分析能量流向
        energy_flow = self._analyze_energy_flow(sihua_list)
        
        # 場論建議
        field_advice = self._generate_field_advice(source_gong, sihua_list)
        
        return FeixingFieldResult(
            source_gong=source_gong,
            source_gan=gong_gan,
            sihua_list=sihua_list,
            field_topology=topology,
            energy_flow=energy_flow,
            field_advice=field_advice
        )
    
    def _analyze_field_topology(self, source: str, targets: List[str]) -> str:
        """分析場的拓撲結構"""
        from collections import Counter
        target_count = Counter(targets)
        
        if len(set(targets)) == 1:
            return f"集中型：四化全部集中於{targets[0]}，形成強烈聚焦"
        
        most_common = target_count.most_common(1)
        if most_common and most_common[0][1] >= 2:
            return f"偏重型：能量偏重於{most_common[0][0]}，次要分散其他宮位"
        
        return "分散型：能量均勻分散於多個宮位，影響面廣但力度分散"
    
    def _analyze_energy_flow(self, sihua_list: List[SihuaFieldInfo]) -> str:
        """分析能量流向"""
        lu_gong = next((s.target_gong for s in sihua_list if s.sihua_type == "化祿"), None)
        ji_gong = next((s.target_gong for s in sihua_list if s.sihua_type == "化忌"), None)
        
        if lu_gong and ji_gong:
            if lu_gong == ji_gong:
                return f"祿忌同宮{lu_gong}：得失並存，此領域既有機會也有挑戰"
            return f"祿在{lu_gong}忌在{ji_gong}：能量從{lu_gong}區域流向{ji_gong}區域消耗"
        
        return "能量流向需結合完整命盤分析"
    
    def _generate_field_advice(self, source: str, sihua_list: List[SihuaFieldInfo]) -> str:
        """生成場論建議"""
        lu_field = next((s for s in sihua_list if s.sihua_type == "化祿"), None)
        ji_field = next((s for s in sihua_list if s.sihua_type == "化忌"), None)
        
        advice_parts = []
        
        if lu_field:
            advice_parts.append(f"把握{lu_field.target_gong}的吸引能量，此為{source}的資源來源")
        
        if ji_field:
            advice_parts.append(f"留意{ji_field.target_gong}的阻滯能量，避免過度執著")
        
        return "；".join(advice_parts) if advice_parts else "場態平衡，維持現狀即可"
    
    def analyze_zihua(self, gong: str, gong_gan: str, stars_in_gong: List[str]) -> Dict:
        """
        分析自化
        
        📚 知識點：
            自化 = 宮內能量循環
            場論視角 = 能量在邊界內的自我消耗或強化
        """
        sihua_stars = self.get_sihua_by_gan(gong_gan)
        zihua_found = []
        
        for sihua_type, star in sihua_stars.items():
            if star in stars_in_gong:
                field_info = SIHUA_FIELD_MEANINGS.get(sihua_type, {})
                zihua_found.append({
                    "type": sihua_type,
                    "star": star,
                    "traditional": self._get_zihua_traditional(sihua_type),
                    "field_meaning": f"能量在{gong}內{field_info.get('vector', '循環')}，形成{field_info.get('field_state', '自循環')}"
                })
        
        return {
            "gong": gong,
            "gong_gan": gong_gan,
            "zihua": zihua_found,
            "has_zihua": len(zihua_found) > 0,
            "field_summary": self._summarize_zihua_field(gong, zihua_found) if zihua_found else "無自化"
        }
    
    def _get_zihua_traditional(self, sihua_type: str) -> str:
        """自化傳統解讀"""
        meanings = {
            "化祿": "自化祿：財來財去，能賺能花，不易積蓄",
            "化權": "自化權：獨立自主，不受拘束，我行我素",
            "化科": "自化科：低調內斂，不愛張揚，默默耕耘",
            "化忌": "自化忌：內心糾結，自我要求，容易鑽牛角尖"
        }
        return meanings.get(sihua_type, "")
    
    def _summarize_zihua_field(self, gong: str, zihua_list: List[Dict]) -> str:
        """自化場論總結"""
        types = [z["type"] for z in zihua_list]
        
        if "化忌" in types:
            return f"{gong}自化忌：能量內耗，需調整心態以釋放阻滯"
        if "化祿" in types:
            return f"{gong}自化祿：能量流動，享受過程重於累積結果"
        if "化權" in types:
            return f"{gong}自化權：能量自主，獨立運作不依賴外力"
        if "化科" in types:
            return f"{gong}自化科：能量內斂，默默提升無需外顯"
        
        return f"{gong}多重自化，能量複雜循環"


# =============================================================================
# D2: 奇門遁甲 (PYLIB 整合版)
# =============================================================================

# 九宮
JIUGONG_INFO = {
    1: {"name": "坎一宮", "direction": "北", "element": "水", "bagua": "坎"},
    2: {"name": "坤二宮", "direction": "西南", "element": "土", "bagua": "坤"},
    3: {"name": "震三宮", "direction": "東", "element": "木", "bagua": "震"},
    4: {"name": "巽四宮", "direction": "東南", "element": "木", "bagua": "巽"},
    5: {"name": "中五宮", "direction": "中", "element": "土", "bagua": "中"},
    6: {"name": "乾六宮", "direction": "西北", "element": "金", "bagua": "乾"},
    7: {"name": "兌七宮", "direction": "西", "element": "金", "bagua": "兌"},
    8: {"name": "艮八宮", "direction": "東北", "element": "土", "bagua": "艮"},
    9: {"name": "離九宮", "direction": "南", "element": "火", "bagua": "離"},
}

# 八門場論意義
BAMEN_FIELD = {
    "開門": {"energy": "啟動", "vector": "向外", "state": "場態激活", "advice": "宜開創、出行、求財"},
    "休門": {"energy": "休養", "vector": "向內", "state": "場態休眠", "advice": "宜休息、養生、訪友"},
    "生門": {"energy": "生發", "vector": "向上", "state": "場態成長", "advice": "宜置產、求醫、啟程"},
    "傷門": {"energy": "衝擊", "vector": "向前", "state": "場態碰撞", "advice": "宜競爭、訴訟、維權"},
    "杜門": {"energy": "封閉", "vector": "向內收", "state": "場態隔離", "advice": "宜隱藏、保密、避禍"},
    "景門": {"energy": "照明", "vector": "向外展", "state": "場態顯化", "advice": "宜文書、考試、宣傳"},
    "死門": {"energy": "終結", "vector": "向下", "state": "場態消亡", "advice": "宜結束、了斷、安葬"},
    "驚門": {"energy": "震盪", "vector": "不定", "state": "場態動盪", "advice": "宜警示、談判、口舌"},
}

# 九星場論意義
JIUXING_FIELD = {
    "天蓬": {"nature": "盜賊", "element": "水", "field_role": "暗流"},
    "天芮": {"nature": "疾病", "element": "土", "field_role": "阻滯"},
    "天衝": {"nature": "武勇", "element": "木", "field_role": "衝擊"},
    "天輔": {"nature": "文昌", "element": "木", "field_role": "輔助"},
    "天禽": {"nature": "中正", "element": "土", "field_role": "核心"},
    "天心": {"nature": "醫藥", "element": "金", "field_role": "調和"},
    "天柱": {"nature": "訟獄", "element": "金", "field_role": "阻隔"},
    "天任": {"nature": "善良", "element": "土", "field_role": "承載"},
    "天英": {"nature": "血光", "element": "火", "field_role": "照耀"},
}


@dataclass
class QimenFieldGong:
    """奇門宮位 (場論版)"""
    position: int
    name: str
    direction: str
    element: str
    tiangan: str
    men: str
    xing: str
    shen: str
    men_field: Dict
    xing_field: Dict
    
    def to_dict(self) -> Dict:
        return {
            "position": self.position,
            "name": self.name,
            "direction": self.direction,
            "element": self.element,
            "tiangan": self.tiangan,
            "men": self.men,
            "xing": self.xing,
            "shen": self.shen,
            "field": {
                "men": self.men_field,
                "xing": self.xing_field
            }
        }


@dataclass
class QimenFieldPan:
    """奇門盤 (場論版)"""
    pan_type: str
    ju_number: int
    is_yang_dun: bool
    gongs: List[QimenFieldGong]
    duty_gan: str
    duty_men: str
    timestamp: datetime
    geju: List[str]
    field_summary: Dict
    
    def to_dict(self) -> Dict:
        return {
            "type": self.pan_type,
            "ju": self.ju_number,
            "yang_dun": self.is_yang_dun,
            "gongs": [g.to_dict() for g in self.gongs],
            "duty": {"gan": self.duty_gan, "men": self.duty_men},
            "timestamp": self.timestamp.isoformat(),
            "geju": self.geju,
            "field_summary": self.field_summary
        }


class QimenPylib:
    """
    奇門遁甲引擎 (PYLIB 整合版)
    
    @11star: 理樞(算法) × 流祇(場論)
    
    PYLIB 整合:
        qimen_engine_v1 - create_qimen_pan, analyze_geju
    """
    
    VERSION = "1.0.0"
    
    BAMEN = ["休門", "生門", "傷門", "杜門", "景門", "死門", "驚門", "開門"]
    JIUXING = ["天蓬", "天芮", "天衝", "天輔", "天禽", "天心", "天柱", "天任", "天英"]
    BASHEN = ["值符", "騰蛇", "太陰", "六合", "白虎", "玄武", "九地", "九天"]
    
    def __init__(self):
        self._pylib_create_pan = PyLibLoader.get_function("qimen_engine_v1", "create_qimen_pan")
        self._pylib_analyze_geju = PyLibLoader.get_function("qimen_engine_v1", "analyze_geju")
        self.pylib_available = PyLibLoader.is_available("qimen_engine_v1")
    
    def get_jieqi(self, dt: date) -> str:
        """獲取節氣"""
        month, day = dt.month, dt.day
        jieqi_map = [
            (1, 6, "小寒"), (1, 20, "大寒"), (2, 4, "立春"), (2, 19, "雨水"),
            (3, 6, "驚蟄"), (3, 21, "春分"), (4, 5, "清明"), (4, 20, "穀雨"),
            (5, 6, "立夏"), (5, 21, "小滿"), (6, 6, "芒種"), (6, 21, "夏至"),
            (7, 7, "小暑"), (7, 23, "大暑"), (8, 8, "立秋"), (8, 23, "處暑"),
            (9, 8, "白露"), (9, 23, "秋分"), (10, 8, "寒露"), (10, 24, "霜降"),
            (11, 8, "立冬"), (11, 22, "小雪"), (12, 7, "大雪"), (12, 22, "冬至"),
        ]
        
        current = "冬至"
        for m, d, jq in jieqi_map:
            if month > m or (month == m and day >= d):
                current = jq
        return current
    
    def is_yang_dun(self, jieqi: str) -> bool:
        """判斷陽遁/陰遁"""
        yang = ["冬至", "小寒", "大寒", "立春", "雨水", "驚蟄",
                "春分", "清明", "穀雨", "立夏", "小滿", "芒種"]
        return jieqi in yang
    
    def create_field_pan(self, dt: datetime = None) -> QimenFieldPan:
        """
        創建奇門盤 (場論增強版)
        
        📚 知識點：
            奇門 = 時空場的戰略視角
            三盤四層 = 天地人神四維場態
        """
        if dt is None:
            dt = datetime.now()
        
        jieqi = self.get_jieqi(dt.date())
        yang_dun = self.is_yang_dun(jieqi)
        
        # 計算局數
        hour = dt.hour
        yuan = (DIZHI.index(self._hour_to_zhi(hour))) % 3
        ju = self._get_ju(jieqi, yuan, yang_dun)
        
        # 構建九宮
        gongs = []
        for pos in range(1, 10):
            gong_info = JIUGONG_INFO[pos]
            
            # 排盤（簡化版）
            gan_idx = (ju - 1 + pos - 1) % 10
            tiangan = TIANGAN[gan_idx]
            
            men_idx = (ju - 1 + pos - 1) % 8
            men = self.BAMEN[men_idx]
            
            xing_idx = (pos - 1) % 9
            xing = self.JIUXING[xing_idx]
            
            shen_idx = (pos - 1) % 8
            shen = self.BASHEN[shen_idx]
            
            gongs.append(QimenFieldGong(
                position=pos,
                name=gong_info["name"],
                direction=gong_info["direction"],
                element=gong_info["element"],
                tiangan=tiangan,
                men=men,
                xing=xing,
                shen=shen,
                men_field=BAMEN_FIELD.get(men, {}),
                xing_field=JIUXING_FIELD.get(xing, {})
            ))
        
        # 值符值使
        duty_gan = TIANGAN[(ju - 1) % 10]
        duty_men = self.BAMEN[(ju - 1) % 8]
        
        # 格局分析
        geju = self._analyze_geju(gongs)
        
        # 場論總結
        field_summary = self._summarize_field(gongs, duty_men, yang_dun, ju)
        
        return QimenFieldPan(
            pan_type="時盤",
            ju_number=ju,
            is_yang_dun=yang_dun,
            gongs=gongs,
            duty_gan=duty_gan,
            duty_men=duty_men,
            timestamp=dt,
            geju=geju,
            field_summary=field_summary
        )
    
    def _hour_to_zhi(self, hour: int) -> str:
        """時辰轉地支"""
        idx = ((hour + 1) // 2) % 12
        return DIZHI[idx]
    
    def _get_ju(self, jieqi: str, yuan: int, yang_dun: bool) -> int:
        """獲取局數"""
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
        return JIEQI_JU.get(jieqi, [1, 7, 4])[yuan]
    
    def _analyze_geju(self, gongs: List[QimenFieldGong]) -> List[str]:
        """分析格局"""
        geju = []
        
        # 三奇檢查
        sanqi = []
        for g in gongs:
            if g.tiangan in ["乙", "丙", "丁"]:
                sanqi.append(f"{g.tiangan}在{g.position}宮({g.direction})")
        if sanqi:
            geju.append(f"三奇分佈：{', '.join(sanqi)}")
        
        # 吉門檢查
        ji_men = ["開門", "生門", "休門"]
        for g in gongs:
            if g.men in ji_men:
                geju.append(f"吉門{g.men}在{g.direction}方{g.position}宮")
                break
        
        # 值符位置
        for g in gongs:
            if g.shen == "值符":
                geju.append(f"值符臨{g.position}宮({g.name})")
                break
        
        return geju if geju else ["盤局中性，需結合問事分析"]
    
    def _summarize_field(
        self,
        gongs: List[QimenFieldGong],
        duty_men: str,
        yang_dun: bool,
        ju: int
    ) -> Dict:
        """場論總結"""
        dun_type = "陽遁" if yang_dun else "陰遁"
        dun_meaning = "進取擴張" if yang_dun else "收斂守成"
        
        men_field = BAMEN_FIELD.get(duty_men, {})
        
        # 找有利方位
        favorable = None
        for g in gongs:
            if g.men in ["開門", "生門"]:
                favorable = f"{g.direction}方（{g.men}所在）"
                break
        
        return {
            "overall": f"{dun_type}{ju}局，場態傾向{dun_meaning}",
            "duty_men_field": men_field.get("state", ""),
            "action": men_field.get("advice", "視情況而定"),
            "favorable_direction": favorable or "需結合具體事項判斷",
            "timing": f"值使{duty_men}：{men_field.get('advice', '')}"
        }


# =============================================================================
# D3: 六壬神課 (場論整合版)
# =============================================================================

SHIER_SHENJIANG_FIELD = {
    "子": {"name": "貴人", "nature": "吉", "field_role": "化解、貴助", "element": "水"},
    "丑": {"name": "騰蛇", "nature": "凶", "field_role": "怪異、變化", "element": "土"},
    "寅": {"name": "朱雀", "nature": "中", "field_role": "口舌、文書", "element": "木"},
    "卯": {"name": "六合", "nature": "吉", "field_role": "和合、媒介", "element": "木"},
    "辰": {"name": "勾陳", "nature": "凶", "field_role": "訴訟、糾纏", "element": "土"},
    "巳": {"name": "青龍", "nature": "吉", "field_role": "喜慶、財帛", "element": "火"},
    "午": {"name": "太常", "nature": "吉", "field_role": "衣祿、穩定", "element": "火"},
    "未": {"name": "白虎", "nature": "凶", "field_role": "凶煞、疾病", "element": "土"},
    "申": {"name": "太陰", "nature": "吉", "field_role": "陰私、暗助", "element": "金"},
    "酉": {"name": "天后", "nature": "中", "field_role": "婦女、暗昧", "element": "金"},
    "戌": {"name": "玄武", "nature": "凶", "field_role": "盜賊、欺騙", "element": "土"},
    "亥": {"name": "天空", "nature": "凶", "field_role": "欺詐、空亡", "element": "水"},
}


@dataclass
class LiurenFieldKe:
    """六壬課 (場論版)"""
    position: str
    tiangan: str
    dizhi: str
    shenjiang_name: str
    shenjiang_nature: str
    shenjiang_role: str
    field_meaning: str
    
    def to_dict(self) -> Dict:
        return {
            "position": self.position,
            "tiangan": self.tiangan,
            "dizhi": self.dizhi,
            "shenjiang": {
                "name": self.shenjiang_name,
                "nature": self.shenjiang_nature,
                "role": self.shenjiang_role
            },
            "field_meaning": self.field_meaning
        }


@dataclass 
class LiurenFieldPan:
    """六壬盤 (場論版)"""
    day_gan: str
    day_zhi: str
    hour_zhi: str
    sike: List[LiurenFieldKe]
    sanchuan_pattern: str
    guiren_zhi: str
    field_topology: str
    field_flow: str
    field_advice: str
    timestamp: datetime
    
    def to_dict(self) -> Dict:
        return {
            "day": f"{self.day_gan}{self.day_zhi}",
            "hour": self.hour_zhi,
            "sike": [k.to_dict() for k in self.sike],
            "sanchuan": self.sanchuan_pattern,
            "guiren": self.guiren_zhi,
            "field": {
                "topology": self.field_topology,
                "flow": self.field_flow,
                "advice": self.field_advice
            },
            "timestamp": self.timestamp.isoformat()
        }


class LiurenPylib:
    """
    六壬神課引擎 (場論整合版)
    
    @11star: 理樞(算法) × 流祇(場論) × 澄韻(翻譯)
    """
    
    VERSION = "1.0.0"
    
    GUIREN_TABLE = {
        "甲": ("丑", "未"), "戊": ("丑", "未"), "庚": ("丑", "未"),
        "乙": ("子", "申"), "己": ("子", "申"),
        "丙": ("亥", "酉"), "丁": ("亥", "酉"),
        "壬": ("卯", "巳"), "癸": ("卯", "巳"),
        "辛": ("午", "寅")
    }
    
    def __init__(self):
        pass
    
    def create_field_pan(
        self,
        day_gan: str,
        day_zhi: str,
        hour_zhi: str,
        is_day: bool = True
    ) -> LiurenFieldPan:
        """
        創建六壬盤 (場論版)
        
        📚 知識點：
            六壬 = 事態場的動態模擬
            四課 = 人我雙方的場態
            三傳 = 事件場的時間演化
        """
        # 貴人起位
        guiren_pair = self.GUIREN_TABLE.get(day_gan, ("丑", "未"))
        guiren_zhi = guiren_pair[0] if is_day else guiren_pair[1]
        
        # 排四課
        sike = self._create_sike(day_gan, day_zhi, hour_zhi)
        
        # 三傳格局
        pattern = self._determine_pattern(sike)
        
        # 場論分析
        topology = self._analyze_topology(sike)
        flow = self._analyze_flow(sike)
        advice = self._generate_advice(sike, pattern)
        
        return LiurenFieldPan(
            day_gan=day_gan,
            day_zhi=day_zhi,
            hour_zhi=hour_zhi,
            sike=sike,
            sanchuan_pattern=pattern,
            guiren_zhi=guiren_zhi,
            field_topology=topology,
            field_flow=flow,
            field_advice=advice,
            timestamp=datetime.now()
        )
    
    def _create_sike(self, day_gan: str, day_zhi: str, hour_zhi: str) -> List[LiurenFieldKe]:
        """創建四課"""
        sike = []
        
        # 簡化排盤
        positions = ["一課", "二課", "三課", "四課"]
        meanings = [
            "日上神，代表自己/主動方",
            "日下神，代表行動結果",
            "辰上神，代表對方/被動方",
            "辰下神，代表對方狀態"
        ]
        
        base_idx = DIZHI.index(hour_zhi)
        
        for i, (pos, meaning) in enumerate(zip(positions, meanings)):
            zhi_idx = (DIZHI.index(day_zhi) + i) % 12
            zhi = DIZHI[zhi_idx]
            
            shen_info = SHIER_SHENJIANG_FIELD.get(zhi, {})
            
            sike.append(LiurenFieldKe(
                position=pos,
                tiangan=TIANGAN[(TIANGAN.index(day_gan) + i) % 10],
                dizhi=zhi,
                shenjiang_name=shen_info.get("name", "未知"),
                shenjiang_nature=shen_info.get("nature", "中"),
                shenjiang_role=shen_info.get("field_role", ""),
                field_meaning=f"{meaning}，神將{shen_info.get('name', '')}主{shen_info.get('field_role', '')}"
            ))
        
        return sike
    
    def _determine_pattern(self, sike: List[LiurenFieldKe]) -> str:
        """判斷三傳格局"""
        zhis = [k.dizhi for k in sike]
        
        if len(set(zhis)) == 1:
            return "伏吟課：場態凝滯，事緩難動"
        
        chong = [("子", "午"), ("丑", "未"), ("寅", "申"),
                 ("卯", "酉"), ("辰", "戌"), ("巳", "亥")]
        for z1, z2 in [(zhis[0], zhis[2])]:
            if (z1, z2) in chong or (z2, z1) in chong:
                return "反吟課：場態震盪，事多反覆"
        
        return "正常課式：場態流動，視神將定吉凶"
    
    def _analyze_topology(self, sike: List[LiurenFieldKe]) -> str:
        """分析場拓撲"""
        natures = [k.shenjiang_nature for k in sike]
        ji_count = natures.count("吉")
        xiong_count = natures.count("凶")
        
        if ji_count >= 3:
            return "場態偏吉：吉神主導，事態向好"
        elif xiong_count >= 3:
            return "場態偏凶：凶神主導，謹慎行事"
        return "場態中性：吉凶參半，視情況而定"
    
    def _analyze_flow(self, sike: List[LiurenFieldKe]) -> str:
        """分析場流動"""
        ke1 = sike[0]  # 我方
        ke3 = sike[2]  # 對方
        
        return f"我方{ke1.shenjiang_name}({ke1.shenjiang_role}) ↔ 對方{ke3.shenjiang_name}({ke3.shenjiang_role})"
    
    def _generate_advice(self, sike: List[LiurenFieldKe], pattern: str) -> str:
        """生成建議"""
        if "伏吟" in pattern:
            return "宜靜待，不宜強求，等待時機轉變"
        if "反吟" in pattern:
            return "事多變化，需靈活應對，不可執著"
        
        ke1 = sike[0]
        if ke1.shenjiang_nature == "吉":
            return f"我方得{ke1.shenjiang_name}助，{ke1.shenjiang_role}，宜積極"
        elif ke1.shenjiang_nature == "凶":
            return f"我方臨{ke1.shenjiang_name}，{ke1.shenjiang_role}，宜謹慎"
        return "場態中性，按部就班即可"


# =============================================================================
# D4: 風水羅盤 (場論整合版)
# =============================================================================

ERSHISI_SHAN_FIELD = [
    ("壬", "北", "水", 337.5, 352.5, "玄武位，主智慧"),
    ("子", "北", "水", 352.5, 7.5, "坎卦正位，主險阻"),
    ("癸", "北", "水", 7.5, 22.5, "天乙位，主貴人"),
    ("丑", "東北", "土", 22.5, 37.5, "艮土位，主穩定"),
    ("艮", "東北", "土", 37.5, 52.5, "艮卦正位，主止息"),
    ("寅", "東北", "木", 52.5, 67.5, "生門位，主生發"),
    ("甲", "東", "木", 67.5, 82.5, "青龍頭，主創始"),
    ("卯", "東", "木", 82.5, 97.5, "震卦正位，主動能"),
    ("乙", "東", "木", 97.5, 112.5, "青龍尾，主延續"),
    ("辰", "東南", "土", 112.5, 127.5, "巽土位，主庫藏"),
    ("巽", "東南", "木", 127.5, 142.5, "巽卦正位，主進入"),
    ("巳", "東南", "火", 142.5, 157.5, "天財位，主財祿"),
    ("丙", "南", "火", 157.5, 172.5, "天乙位，主文昌"),
    ("午", "南", "火", 172.5, 187.5, "離卦正位，主光明"),
    ("丁", "南", "火", 187.5, 202.5, "天官位，主官祿"),
    ("未", "西南", "土", 202.5, 217.5, "坤土位，主母德"),
    ("坤", "西南", "土", 217.5, 232.5, "坤卦正位，主順承"),
    ("申", "西南", "金", 232.5, 247.5, "白虎頭，主肅殺"),
    ("庚", "西", "金", 247.5, 262.5, "白虎位，主刑克"),
    ("酉", "西", "金", 262.5, 277.5, "兌卦正位，主口舌"),
    ("辛", "西", "金", 277.5, 292.5, "白虎尾，主收斂"),
    ("戌", "西北", "土", 292.5, 307.5, "乾土位，主天門"),
    ("乾", "西北", "金", 307.5, 322.5, "乾卦正位，主剛健"),
    ("亥", "西北", "水", 322.5, 337.5, "天門位，主玄機"),
]

SANYUAN_JIUYUN_FIELD = {
    7: {"years": (1984, 2003), "xing": "兌", "element": "金", "theme": "口舌是非，金融興旺"},
    8: {"years": (2004, 2023), "xing": "艮", "element": "土", "theme": "地產建築，少男當令"},
    9: {"years": (2024, 2043), "xing": "離", "element": "火", "theme": "文化科技，中女當令"},
    1: {"years": (2044, 2063), "xing": "坎", "element": "水", "theme": "智慧科技，中男當令"},
}


@dataclass
class FengshuiFieldDirection:
    """風水方位 (場論版)"""
    shan: str
    xiang: str
    shan_element: str
    xiang_element: str
    shan_field_meaning: str
    current_yun: int
    yun_element: str
    yun_theme: str
    shan_yun_relation: str
    field_assessment: str
    
    def to_dict(self) -> Dict:
        return {
            "direction": {
                "shan": self.shan,
                "xiang": self.xiang,
                "shan_element": self.shan_element,
                "xiang_element": self.xiang_element,
                "shan_meaning": self.shan_field_meaning
            },
            "yun": {
                "current": self.current_yun,
                "element": self.yun_element,
                "theme": self.yun_theme
            },
            "analysis": {
                "shan_yun_relation": self.shan_yun_relation,
                "assessment": self.field_assessment
            }
        }


class FengshuiPylib:
    """
    風水羅盤引擎 (場論整合版)
    
    @11star: 流祇(場論) × 理樞(算法)
    """
    
    VERSION = "1.0.0"
    
    def __init__(self):
        pass
    
    def get_current_yun(self, year: int = None) -> Tuple[int, Dict]:
        """獲取當運"""
        if year is None:
            year = datetime.now().year
        
        for yun, info in SANYUAN_JIUYUN_FIELD.items():
            if info["years"][0] <= year <= info["years"][1]:
                return yun, info
        return 9, SANYUAN_JIUYUN_FIELD[9]
    
    def degree_to_shan(self, degree: float) -> Tuple[str, str, str, str]:
        """角度轉二十四山"""
        degree = degree % 360
        
        for shan, direction, element, start, end, meaning in ERSHISI_SHAN_FIELD:
            if start <= degree < end or (start > end and (degree >= start or degree < end)):
                return shan, direction, element, meaning
        
        return "子", "北", "水", "坎卦正位"
    
    def analyze_field_direction(self, degree: float, year: int = None) -> FengshuiFieldDirection:
        """
        分析風水方位 (場論版)
        
        📚 知識點：
            風水 = 空間場的能量布局
            坐向 = 場的主軸定位
            三元九運 = 時間場的週期律
        """
        # 坐山
        shan, shan_dir, shan_elem, shan_meaning = self.degree_to_shan(degree)
        
        # 朝向
        xiang_degree = (degree + 180) % 360
        xiang, xiang_dir, xiang_elem, _ = self.degree_to_shan(xiang_degree)
        
        # 當運
        yun, yun_info = self.get_current_yun(year)
        
        # 坐山與運的關係
        relation = self._analyze_shan_yun(shan_elem, yun_info["element"])
        
        # 場論評估
        assessment = self._assess_field(shan, xiang, shan_elem, xiang_elem, yun_info)
        
        return FengshuiFieldDirection(
            shan=shan,
            xiang=xiang,
            shan_element=shan_elem,
            xiang_element=xiang_elem,
            shan_field_meaning=shan_meaning,
            current_yun=yun,
            yun_element=yun_info["element"],
            yun_theme=yun_info["theme"],
            shan_yun_relation=relation,
            field_assessment=assessment
        )
    
    def _analyze_shan_yun(self, shan_elem: str, yun_elem: str) -> str:
        """分析坐山與運的關係"""
        if shan_elem == yun_elem:
            return f"坐山{shan_elem}與當運{yun_elem}同類，得旺氣"
        if WUXING_SHENG.get(yun_elem) == shan_elem:
            return f"當運{yun_elem}生坐山{shan_elem}，得生氣"
        if WUXING_SHENG.get(shan_elem) == yun_elem:
            return f"坐山{shan_elem}生當運{yun_elem}，為洩氣"
        if WUXING_KE.get(yun_elem) == shan_elem:
            return f"當運{yun_elem}剋坐山{shan_elem}，受剋"
        if WUXING_KE.get(shan_elem) == yun_elem:
            return f"坐山{shan_elem}剋當運{yun_elem}，耗力"
        return "關係中性"
    
    def _assess_field(
        self,
        shan: str,
        xiang: str,
        shan_elem: str,
        xiang_elem: str,
        yun_info: Dict
    ) -> str:
        """場論評估"""
        yun_elem = yun_info["element"]
        
        # 坐山得運
        if shan_elem == yun_elem or WUXING_SHENG.get(yun_elem) == shan_elem:
            return f"坐{shan}朝{xiang}：坐山得運，空間場與時間場共振，利於發展"
        
        # 朝向得運
        if xiang_elem == yun_elem or WUXING_SHENG.get(yun_elem) == xiang_elem:
            return f"坐{shan}朝{xiang}：朝向得運，迎接當運能量，適合對外拓展"
        
        # 受剋
        if WUXING_KE.get(yun_elem) == shan_elem:
            return f"坐{shan}朝{xiang}：坐山受運所剋，需化解或調整"
        
        return f"坐{shan}朝{xiang}：場態中性，需結合其他因素綜合判斷"


# =============================================================================
# 統一 API (XTFS 四塔協作)
# =============================================================================

class MingshuAdvancedPylibAPI:
    """
    進階術數統一 API (PYLIB 整合版)
    
    XTFS 四塔協作：
        X(執行): 算法計算
        T(翻譯): 語義轉換
        F(場論): 場態分析
        S(存儲): 結果緩存
    """
    
    VERSION = "1.0.0"
    
    def __init__(self):
        self.ziwei = ZiweiAdvancedPylib()
        self.qimen = QimenPylib()
        self.liuren = LiurenPylib()
        self.fengshui = FengshuiPylib()
        
        # 統計 PYLIB 狀態
        self.pylib_status = self._check_pylib_status()
    
    def _check_pylib_status(self) -> Dict:
        """檢查 PYLIB 狀態"""
        status = {}
        total_available = 0
        total_lines = 0
        
        for mod, info in PYLIB_MODULES.items():
            available = PyLibLoader.is_available(mod)
            status[mod] = {
                "available": available,
                "lines": info["lines"],
                "desc": info["desc"]
            }
            if available:
                total_available += 1
                total_lines += info["lines"]
        
        return {
            "modules": status,
            "summary": {
                "total": len(PYLIB_MODULES),
                "available": total_available,
                "lines_available": total_lines
            }
        }
    
    # ===== D1: 紫微四化 =====
    
    def analyze_sihua(self, year_gan: str, star_positions: Dict = None) -> Dict:
        """分析本命四化"""
        results = self.ziwei.analyze_natal_sihua_field(year_gan, star_positions)
        return {
            "success": True,
            "data": [r.to_dict() for r in results],
            "pylib_enhanced": any(r.pylib_enhanced for r in results)
        }
    
    def analyze_feixing(self, source_gong: str, gong_gan: str, star_positions: Dict = None) -> Dict:
        """分析飛星"""
        result = self.ziwei.analyze_feixing_field(source_gong, gong_gan, star_positions)
        return {"success": True, "data": result.to_dict()}
    
    def analyze_zihua(self, gong: str, gong_gan: str, stars: List[str]) -> Dict:
        """分析自化"""
        result = self.ziwei.analyze_zihua(gong, gong_gan, stars)
        return {"success": True, "data": result}
    
    # ===== D2: 奇門遁甲 =====
    
    def create_qimen(self, dt: datetime = None) -> Dict:
        """創建奇門盤"""
        pan = self.qimen.create_field_pan(dt)
        return {"success": True, "data": pan.to_dict()}
    
    # ===== D3: 六壬神課 =====
    
    def create_liuren(self, day_gan: str, day_zhi: str, hour_zhi: str, is_day: bool = True) -> Dict:
        """創建六壬盤"""
        pan = self.liuren.create_field_pan(day_gan, day_zhi, hour_zhi, is_day)
        return {"success": True, "data": pan.to_dict()}
    
    # ===== D4: 風水羅盤 =====
    
    def analyze_fengshui(self, degree: float, year: int = None) -> Dict:
        """分析風水方位"""
        result = self.fengshui.analyze_field_direction(degree, year)
        return {"success": True, "data": result.to_dict()}
    
    # ===== 系統資訊 =====
    
    def get_pylib_status(self) -> Dict:
        """獲取 PYLIB 狀態"""
        return {"success": True, "data": self.pylib_status}


# =============================================================================
# CLI 入口
# =============================================================================

def main():
    """CLI 入口"""
    print("=" * 70)
    print("北斗命數 進階術數 v1.0 (PYLIB 整合版)")
    print("XTF⁸ + XTFS + @11star 協作")
    print("=" * 70)
    
    api = MingshuAdvancedPylibAPI()
    
    # PYLIB 狀態
    print("\n【PYLIB 模組狀態】")
    status = api.pylib_status
    for mod, info in status["modules"].items():
        icon = "✓" if info["available"] else "○"
        print(f"  {icon} {mod:<25} | {info['lines']:>4}行 | {info['desc']}")
    print(f"  {'─'*50}")
    s = status["summary"]
    print(f"  可用: {s['available']}/{s['total']} 模組 | {s['lines_available']} 行")
    
    # D1: 紫微四化
    print("\n【D1】紫微四化 - 癸年生人 (場論增強)")
    result = api.analyze_sihua("癸")
    for s in result["data"]:
        print(f"  {s['type']}: {s['star']}")
        print(f"    傳統: {s['traditional'][:35]}...")
        print(f"    場論: {s['field']['state']} | {s['field']['vector']}")
    
    # D1: 飛星
    print("\n【D1】飛星分析 - 命宮天干甲")
    result = api.analyze_feixing("命宮", "甲")
    fa = result["data"]["field_analysis"]
    print(f"  拓撲: {fa['topology']}")
    print(f"  能量: {fa['energy_flow']}")
    print(f"  建議: {fa['advice']}")
    
    # D2: 奇門遁甲
    print("\n【D2】奇門遁甲 - 當下時盤 (場論增強)")
    result = api.create_qimen()
    pan = result["data"]
    print(f"  {pan['field_summary']['overall']}")
    print(f"  行動: {pan['field_summary']['action']}")
    print(f"  方位: {pan['field_summary']['favorable_direction']}")
    
    # D3: 六壬神課
    print("\n【D3】六壬神課 - 癸丑日卯時 (場論增強)")
    result = api.create_liuren("癸", "丑", "卯")
    pan = result["data"]
    print(f"  格局: {pan['sanchuan']}")
    print(f"  拓撲: {pan['field']['topology']}")
    print(f"  流向: {pan['field']['flow']}")
    print(f"  建議: {pan['field']['advice']}")
    
    # D4: 風水羅盤
    print("\n【D4】風水羅盤 - 坐北朝南 (場論增強)")
    result = api.analyze_fengshui(0)
    data = result["data"]
    print(f"  坐山: {data['direction']['shan']} ({data['direction']['shan_element']})")
    print(f"  朝向: {data['direction']['xiang']} ({data['direction']['xiang_element']})")
    print(f"  當運: {data['yun']['current']}運 ({data['yun']['theme']})")
    print(f"  關係: {data['analysis']['shan_yun_relation']}")
    print(f"  評估: {data['analysis']['assessment']}")
    
    # 統計
    print("\n" + "=" * 70)
    with open(__file__, 'r') as f:
        lines = len(f.read().split('\n'))
    print(f"本模組: {lines} 行")
    print(f"PYLIB 整合潛力: {sum(m['lines'] for m in PYLIB_MODULES.values())} 行")
    print("=" * 70)


if __name__ == "__main__":
    main()
