#!/usr/bin/env python3
"""
紫微斗數引擎 ziwei_engine.py v1.0
==================================
XTF任務: T4 | 執行星: 織明(框架)+理樞(實現)

📚 知識點：
- 紫微斗數為宋代陳希夷（陳摶）所創
- 以農曆生辰定盤，十二宮配十四主星
- 核心概念：命宮、身宮、四化、格局
- 本引擎採用「三合派」規則（最普及）

📐 古今融合：
- 古法安星規則不動
- 場論翻譯（選配）
- 不裁決、不命定，提供決策框架
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Any
from enum import Enum
import sys
sys.path.insert(0, '/home/claude/beidou_mingshu/beidou')

try:
    from wuxing_core import TIANGAN, DIZHI, WX_ORDER
except ImportError:
    # 備用定義
    TIANGAN = ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"]
    DIZHI = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]
    WX_ORDER = ["木", "火", "土", "金", "水"]


# ===== 十二宮名稱 =====
GONG_12 = [
    "命宮", "兄弟", "夫妻", "子女", "財帛", "疾厄",
    "遷移", "交友", "官祿", "田宅", "福德", "父母"
]

# ===== 十四主星 =====
MAIN_STARS_14 = [
    "紫微", "天機", "太陽", "武曲", "天同", "廉貞", "天府",
    "太陰", "貪狼", "巨門", "天相", "天梁", "七殺", "破軍"
]

# ===== 六吉星 =====
LUCKY_STARS_6 = ["左輔", "右弼", "天魁", "天鉞", "文昌", "文曲"]

# ===== 四煞星 =====
EVIL_STARS_4 = ["擎羊", "陀羅", "火星", "鈴星"]

# ===== 四化 =====
SIHUA = ["化祿", "化權", "化科", "化忌"]

# ===== 年干四化表 =====
# 格式：年干 → [化祿星, 化權星, 化科星, 化忌星]
SIHUA_TABLE = {
    "甲": ["廉貞", "破軍", "武曲", "太陽"],
    "乙": ["天機", "天梁", "紫微", "太陰"],
    "丙": ["天同", "天機", "文昌", "廉貞"],
    "丁": ["太陰", "天同", "天機", "巨門"],
    "戊": ["貪狼", "太陰", "右弼", "天機"],
    "己": ["武曲", "貪狼", "天梁", "文曲"],
    "庚": ["太陽", "武曲", "太陰", "天同"],
    "辛": ["巨門", "太陽", "文曲", "文昌"],
    "壬": ["天梁", "紫微", "左輔", "武曲"],
    "癸": ["破軍", "巨門", "太陰", "貪狼"],
}

# ===== 紫微星定位表 =====
# 根據農曆日期定紫微星所在宮位
# 格式：五行局數 → 日數 → 紫微所在地支序號(0-11)
ZIWEI_TABLE = {
    2: {  # 水二局
        1: 1, 2: 2, 3: 2, 4: 3, 5: 3, 6: 4, 7: 4, 8: 5, 9: 5, 10: 6,
        11: 6, 12: 7, 13: 7, 14: 8, 15: 8, 16: 9, 17: 9, 18: 10, 19: 10, 20: 11,
        21: 11, 22: 0, 23: 0, 24: 1, 25: 1, 26: 2, 27: 2, 28: 3, 29: 3, 30: 4,
    },
    3: {  # 木三局
        1: 2, 2: 2, 3: 3, 4: 3, 5: 3, 6: 4, 7: 4, 8: 4, 9: 5, 10: 5,
        11: 5, 12: 6, 13: 6, 14: 6, 15: 7, 16: 7, 17: 7, 18: 8, 19: 8, 20: 8,
        21: 9, 22: 9, 23: 9, 24: 10, 25: 10, 26: 10, 27: 11, 28: 11, 29: 11, 30: 0,
    },
    4: {  # 金四局
        1: 3, 2: 3, 3: 3, 4: 4, 5: 4, 6: 4, 7: 4, 8: 5, 9: 5, 10: 5,
        11: 5, 12: 6, 13: 6, 14: 6, 15: 6, 16: 7, 17: 7, 18: 7, 19: 7, 20: 8,
        21: 8, 22: 8, 23: 8, 24: 9, 25: 9, 26: 9, 27: 9, 28: 10, 29: 10, 30: 10,
    },
    5: {  # 土五局
        1: 4, 2: 4, 3: 4, 4: 4, 5: 5, 6: 5, 7: 5, 8: 5, 9: 5, 10: 6,
        11: 6, 12: 6, 13: 6, 14: 6, 15: 7, 16: 7, 17: 7, 18: 7, 19: 7, 20: 8,
        21: 8, 22: 8, 23: 8, 24: 8, 25: 9, 26: 9, 27: 9, 28: 9, 29: 9, 30: 10,
    },
    6: {  # 火六局
        1: 5, 2: 5, 3: 5, 4: 5, 5: 5, 6: 6, 7: 6, 8: 6, 9: 6, 10: 6,
        11: 6, 12: 7, 13: 7, 14: 7, 15: 7, 16: 7, 17: 7, 18: 8, 19: 8, 20: 8,
        21: 8, 22: 8, 23: 8, 24: 9, 25: 9, 26: 9, 27: 9, 28: 9, 29: 9, 30: 10,
    },
}

# ===== 命宮定位表 =====
# 農曆月份(1-12) + 時辰(0-11) → 命宮地支序號
# 公式：命宮 = (月 + 時辰) 順排，從寅宮起正月
def calc_ming_gong(lunar_month: int, hour_zhi_idx: int) -> int:
    """
    計算命宮位置
    
    📚 口訣：「正月建寅，逆時順月」
    - 正月從寅宮起
    - 順數到該月
    - 再逆數時辰
    
    Parameters:
        lunar_month: 農曆月份 (1-12)
        hour_zhi_idx: 時辰地支序號 (0=子, 1=丑, ..., 11=亥)
    
    Returns:
        命宮地支序號 (0-11)
    """
    # 正月對應寅(2)，順數月份
    month_pos = (2 + lunar_month - 1) % 12
    # 從月位逆數時辰
    ming_pos = (month_pos - hour_zhi_idx) % 12
    return ming_pos


def calc_shen_gong(lunar_month: int, hour_zhi_idx: int) -> int:
    """
    計算身宮位置
    
    📚 口訣：「逆月順時」
    
    Parameters:
        lunar_month: 農曆月份 (1-12)
        hour_zhi_idx: 時辰地支序號 (0=子, 1=丑, ..., 11=亥)
    
    Returns:
        身宮地支序號 (0-11)
    """
    # 正月對應寅(2)，逆數月份
    month_pos = (2 - lunar_month + 1) % 12
    # 從月位順數時辰
    shen_pos = (month_pos + hour_zhi_idx) % 12
    return shen_pos


# ===== 五行局數計算 =====
# 命宮天干地支 → 納音五行 → 局數
NAYIN_WUXING = {
    # 甲子/乙丑 → 海中金
    ("甲", "子"): "金", ("乙", "丑"): "金",
    ("丙", "寅"): "火", ("丁", "卯"): "火",
    ("戊", "辰"): "木", ("己", "巳"): "木",
    ("庚", "午"): "土", ("辛", "未"): "土",
    ("壬", "申"): "金", ("癸", "酉"): "金",
    ("甲", "戌"): "火", ("乙", "亥"): "火",
    ("丙", "子"): "水", ("丁", "丑"): "水",
    ("戊", "寅"): "土", ("己", "卯"): "土",
    ("庚", "辰"): "金", ("辛", "巳"): "金",
    ("壬", "午"): "木", ("癸", "未"): "木",
    ("甲", "申"): "水", ("乙", "酉"): "水",
    ("丙", "戌"): "土", ("丁", "亥"): "土",
    ("戊", "子"): "火", ("己", "丑"): "火",
    ("庚", "寅"): "木", ("辛", "卯"): "木",
    ("壬", "辰"): "水", ("癸", "巳"): "水",
    ("甲", "午"): "金", ("乙", "未"): "金",
    ("丙", "申"): "火", ("丁", "酉"): "火",
    ("戊", "戌"): "木", ("己", "亥"): "木",
    ("庚", "子"): "土", ("辛", "丑"): "土",
    ("壬", "寅"): "金", ("癸", "卯"): "金",
    ("甲", "辰"): "火", ("乙", "巳"): "火",
    ("丙", "午"): "水", ("丁", "未"): "水",
    ("戊", "申"): "土", ("己", "酉"): "土",
    ("庚", "戌"): "金", ("辛", "亥"): "金",
    ("壬", "子"): "木", ("癸", "丑"): "木",
    ("甲", "寅"): "水", ("乙", "卯"): "水",
    ("丙", "辰"): "土", ("丁", "巳"): "土",
    ("戊", "午"): "火", ("己", "未"): "火",
    ("庚", "申"): "木", ("辛", "酉"): "木",
    ("壬", "戌"): "水", ("癸", "亥"): "水",
}

WUXING_JU = {"水": 2, "木": 3, "金": 4, "土": 5, "火": 6}


def calc_ju_shu(year_gan: str, ming_zhi_idx: int) -> int:
    """
    計算五行局數
    
    📚 規則：命宮天干地支的納音五行決定局數
    - 水二局、木三局、金四局、土五局、火六局
    
    Parameters:
        year_gan: 年干（用於計算命宮天干）
        ming_zhi_idx: 命宮地支序號
    
    Returns:
        局數 (2/3/4/5/6)
    """
    # 命宮天干：從年干起子位，順數到命宮地支
    gan_idx = TIANGAN.index(year_gan)
    ming_gan_idx = (gan_idx + ming_zhi_idx) % 10
    ming_gan = TIANGAN[ming_gan_idx]
    ming_zhi = DIZHI[ming_zhi_idx]
    
    # 查納音五行
    nayin_wx = NAYIN_WUXING.get((ming_gan, ming_zhi), "土")
    return WUXING_JU[nayin_wx]


# ===== 安主星 =====
def place_ziwei_stars(ziwei_pos: int) -> Dict[int, List[str]]:
    """
    安紫微星系（紫微、天機、太陽、武曲、天同、廉貞）
    
    📚 口訣：
    紫微逆行：紫微→天機(隔一)→太陽(又隔一)→武曲(又隔一)→天同(隔一)→廉貞(隔二)
    
    Parameters:
        ziwei_pos: 紫微星所在宮位 (0-11)
    
    Returns:
        Dict[宮位序號, 星曜列表]
    """
    stars = {}
    
    # 紫微星系安星（逆行）
    stars[ziwei_pos] = stars.get(ziwei_pos, []) + ["紫微"]
    
    tianji_pos = (ziwei_pos - 1) % 12  # 天機
    stars[tianji_pos] = stars.get(tianji_pos, []) + ["天機"]
    
    # 太陽：隔一位（跳過一宮）
    taiyang_pos = (ziwei_pos - 3) % 12
    stars[taiyang_pos] = stars.get(taiyang_pos, []) + ["太陽"]
    
    # 武曲：又隔一位
    wuqu_pos = (ziwei_pos - 4) % 12
    stars[wuqu_pos] = stars.get(wuqu_pos, []) + ["武曲"]
    
    # 天同：隔一位
    tiantong_pos = (ziwei_pos - 6) % 12
    stars[tiantong_pos] = stars.get(tiantong_pos, []) + ["天同"]
    
    # 廉貞：隔二位
    lianzhen_pos = (ziwei_pos - 8) % 12
    stars[lianzhen_pos] = stars.get(lianzhen_pos, []) + ["廉貞"]
    
    return stars


def place_tianfu_stars(tianfu_pos: int) -> Dict[int, List[str]]:
    """
    安天府星系（天府、太陰、貪狼、巨門、天相、天梁、七殺、破軍）
    
    📚 天府與紫微對宮，然後順行
    
    Parameters:
        tianfu_pos: 天府星所在宮位
    
    Returns:
        Dict[宮位序號, 星曜列表]
    """
    stars = {}
    
    # 天府星系安星（順行）
    stars[tianfu_pos] = stars.get(tianfu_pos, []) + ["天府"]
    
    taiyin_pos = (tianfu_pos + 1) % 12  # 太陰
    stars[taiyin_pos] = stars.get(taiyin_pos, []) + ["太陰"]
    
    tanlang_pos = (tianfu_pos + 2) % 12  # 貪狼
    stars[tanlang_pos] = stars.get(tanlang_pos, []) + ["貪狼"]
    
    jumen_pos = (tianfu_pos + 3) % 12  # 巨門
    stars[jumen_pos] = stars.get(jumen_pos, []) + ["巨門"]
    
    tianxiang_pos = (tianfu_pos + 4) % 12  # 天相
    stars[tianxiang_pos] = stars.get(tianxiang_pos, []) + ["天相"]
    
    tianliang_pos = (tianfu_pos + 5) % 12  # 天梁
    stars[tianliang_pos] = stars.get(tianliang_pos, []) + ["天梁"]
    
    qisha_pos = (tianfu_pos + 6) % 12  # 七殺
    stars[qisha_pos] = stars.get(qisha_pos, []) + ["七殺"]
    
    # 破軍在天府對宮
    pojun_pos = (tianfu_pos + 6) % 12
    # 注意：破軍與七殺不同宮，需重新計算
    pojun_pos = (tianfu_pos + 10) % 12
    stars[pojun_pos] = stars.get(pojun_pos, []) + ["破軍"]
    
    return stars


def calc_tianfu_pos(ziwei_pos: int) -> int:
    """
    計算天府位置
    
    📚 規則：紫微與天府以寅申線為軸對稱
    """
    # 簡化版：天府 = 12 - 紫微 + 4 (以寅為軸)
    # 更精確的對稱計算
    axis_map = {
        0: 4, 1: 3, 2: 2, 3: 1, 4: 0, 5: 11,
        6: 10, 7: 9, 8: 8, 9: 7, 10: 6, 11: 5
    }
    return axis_map.get(ziwei_pos, (4 - ziwei_pos) % 12)


# ===== 安六吉四煞 =====
def place_lucky_stars(year_gan: str, hour_zhi_idx: int) -> Dict[int, List[str]]:
    """
    安六吉星
    
    📚 知識點：
    - 文昌：年干定位
    - 文曲：年干定位  
    - 左輔：月支順行
    - 右弼：月支逆行
    - 天魁：年干定位（陽貴人）
    - 天鉞：年干定位（陰貴人）
    """
    stars = {}
    
    # 文昌位置（年干定）
    wenchang_table = {
        "甲": 6, "乙": 7, "丙": 8, "丁": 9, "戊": 10,
        "己": 10, "庚": 11, "辛": 0, "壬": 1, "癸": 2
    }
    wenchang_pos = wenchang_table.get(year_gan, 0)
    stars[wenchang_pos] = stars.get(wenchang_pos, []) + ["文昌"]
    
    # 文曲位置（年干定，與文昌對沖）
    wenqu_pos = (wenchang_pos + 4) % 12
    stars[wenqu_pos] = stars.get(wenqu_pos, []) + ["文曲"]
    
    # 天魁（陽貴人）
    tiankui_table = {
        "甲": 1, "戊": 1, "庚": 1,  # 丑
        "乙": 0, "己": 0,          # 子
        "丙": 11, "丁": 11,        # 亥
        "辛": 6,                   # 午
        "壬": 3, "癸": 3           # 卯
    }
    tiankui_pos = tiankui_table.get(year_gan, 0)
    stars[tiankui_pos] = stars.get(tiankui_pos, []) + ["天魁"]
    
    # 天鉞（陰貴人）
    tianyue_table = {
        "甲": 7, "戊": 7, "庚": 7,  # 未
        "乙": 8, "己": 8,          # 申
        "丙": 9, "丁": 9,          # 酉
        "辛": 2,                   # 寅
        "壬": 5, "癸": 5           # 巳
    }
    tianyue_pos = tianyue_table.get(year_gan, 0)
    stars[tianyue_pos] = stars.get(tianyue_pos, []) + ["天鉞"]
    
    return stars


def place_evil_stars(year_gan: str, year_zhi_idx: int) -> Dict[int, List[str]]:
    """
    安四煞星
    
    📚 知識點：
    - 擎羊：年干定位（祿前一位）
    - 陀羅：年干定位（祿後一位）
    - 火星：年支定位
    - 鈴星：年支定位
    """
    stars = {}
    
    # 祿位表（年干對應祿位）
    lu_table = {
        "甲": 2, "乙": 3, "丙": 5, "丁": 6, "戊": 5,
        "己": 6, "庚": 8, "辛": 9, "壬": 11, "癸": 0
    }
    lu_pos = lu_table.get(year_gan, 0)
    
    # 擎羊（祿前一位）
    qingyang_pos = (lu_pos + 1) % 12
    stars[qingyang_pos] = stars.get(qingyang_pos, []) + ["擎羊"]
    
    # 陀羅（祿後一位）
    tuoluo_pos = (lu_pos - 1) % 12
    stars[tuoluo_pos] = stars.get(tuoluo_pos, []) + ["陀羅"]
    
    # 火星（年支定，寅午戌年在丑...）
    huoxing_table = {
        2: 1, 6: 1, 10: 1,   # 寅午戌 → 丑
        8: 2, 0: 2, 4: 2,    # 申子辰 → 寅
        5: 3, 9: 3, 1: 3,    # 巳酉丑 → 卯
        11: 9, 3: 9, 7: 9,   # 亥卯未 → 酉
    }
    huoxing_pos = huoxing_table.get(year_zhi_idx, 0)
    stars[huoxing_pos] = stars.get(huoxing_pos, []) + ["火星"]
    
    # 鈴星
    lingxing_table = {
        2: 3, 6: 3, 10: 3,   # 寅午戌 → 卯
        8: 10, 0: 10, 4: 10, # 申子辰 → 戌
        5: 10, 9: 10, 1: 10, # 巳酉丑 → 戌
        11: 10, 3: 10, 7: 10,# 亥卯未 → 戌
    }
    lingxing_pos = lingxing_table.get(year_zhi_idx, 0)
    stars[lingxing_pos] = stars.get(lingxing_pos, []) + ["鈴星"]
    
    return stars


# ===== 資料結構 =====
@dataclass
class ZiWeiGong:
    """單一宮位"""
    index: int              # 0-11
    name: str               # 宮名（命宮、兄弟...）
    zhi: str                # 地支
    gan: str                # 天干
    main_stars: List[str] = field(default_factory=list)   # 主星
    lucky_stars: List[str] = field(default_factory=list)  # 吉星
    evil_stars: List[str] = field(default_factory=list)   # 煞星
    sihua: List[str] = field(default_factory=list)        # 四化
    
    def all_stars(self) -> List[str]:
        return self.main_stars + self.lucky_stars + self.evil_stars


@dataclass
class ZiWeiChart:
    """紫微命盤"""
    # 基本資料
    year_gan: str
    year_zhi: str
    lunar_month: int
    lunar_day: int
    hour_zhi: str
    gender: str  # "男" or "女"
    
    # 計算結果
    ming_gong_idx: int
    shen_gong_idx: int
    ju_shu: int  # 五行局數
    ziwei_pos: int  # 紫微星位置
    tianfu_pos: int  # 天府星位置
    
    # 十二宮
    gongs: List[ZiWeiGong] = field(default_factory=list)
    
    # 四化
    sihua_stars: Dict[str, str] = field(default_factory=dict)  # 星→化
    
    def get_ming_gong(self) -> ZiWeiGong:
        return self.gongs[self.ming_gong_idx]
    
    def get_shen_gong(self) -> ZiWeiGong:
        return self.gongs[self.shen_gong_idx]
    
    def summary(self) -> str:
        lines = [
            "=" * 50,
            "紫微斗數命盤",
            "=" * 50,
            f"生辰：{self.year_gan}{self.year_zhi}年 農曆{self.lunar_month}月{self.lunar_day}日 {self.hour_zhi}時",
            f"性別：{self.gender}",
            f"五行局：{['水二局','木三局','金四局','土五局','火六局'][self.ju_shu-2]}",
            f"命宮：{DIZHI[self.ming_gong_idx]}（{GONG_12[0]}）",
            f"身宮：{DIZHI[self.shen_gong_idx]}",
            "",
            "【十二宮星曜分布】",
        ]
        
        for gong in self.gongs:
            stars_str = ", ".join(gong.all_stars()) if gong.all_stars() else "（無主星）"
            is_ming = "★命宮" if gong.index == self.ming_gong_idx else ""
            is_shen = "☆身宮" if gong.index == self.shen_gong_idx else ""
            marker = is_ming or is_shen
            lines.append(f"  {gong.name}({gong.zhi}): {stars_str} {marker}")
        
        lines.append("")
        lines.append("【四化】")
        for star, hua in self.sihua_stars.items():
            lines.append(f"  {star} → {hua}")
        
        return "\n".join(lines)


def create_ziwei_chart(
    year_gan: str, year_zhi: str,
    lunar_month: int, lunar_day: int,
    hour_zhi: str, gender: str = "男"
) -> ZiWeiChart:
    """
    建立紫微命盤
    
    Parameters:
        year_gan: 年干
        year_zhi: 年支
        lunar_month: 農曆月 (1-12)
        lunar_day: 農曆日 (1-30)
        hour_zhi: 時辰地支
        gender: 性別
    
    Returns:
        ZiWeiChart 命盤物件
    """
    year_zhi_idx = DIZHI.index(year_zhi)
    hour_zhi_idx = DIZHI.index(hour_zhi)
    
    # 1. 計算命宮、身宮
    ming_gong_idx = calc_ming_gong(lunar_month, hour_zhi_idx)
    shen_gong_idx = calc_shen_gong(lunar_month, hour_zhi_idx)
    
    # 2. 計算五行局數
    ju_shu = calc_ju_shu(year_gan, ming_gong_idx)
    
    # 3. 定紫微星位置
    day_key = min(lunar_day, 30)
    ziwei_pos = ZIWEI_TABLE.get(ju_shu, {}).get(day_key, 0)
    
    # 4. 定天府位置
    tianfu_pos = calc_tianfu_pos(ziwei_pos)
    
    # 5. 初始化十二宮
    gongs = []
    for i in range(12):
        # 宮位名稱順排
        gong_name_idx = (i - ming_gong_idx) % 12
        gong = ZiWeiGong(
            index=i,
            name=GONG_12[gong_name_idx],
            zhi=DIZHI[i],
            gan=TIANGAN[(TIANGAN.index(year_gan) + i) % 10]
        )
        gongs.append(gong)
    
    # 6. 安主星
    ziwei_stars = place_ziwei_stars(ziwei_pos)
    tianfu_stars = place_tianfu_stars(tianfu_pos)
    
    for pos, stars in ziwei_stars.items():
        gongs[pos].main_stars.extend(stars)
    for pos, stars in tianfu_stars.items():
        gongs[pos].main_stars.extend(stars)
    
    # 7. 安吉星煞星
    lucky_stars = place_lucky_stars(year_gan, hour_zhi_idx)
    evil_stars = place_evil_stars(year_gan, year_zhi_idx)
    
    for pos, stars in lucky_stars.items():
        gongs[pos].lucky_stars.extend(stars)
    for pos, stars in evil_stars.items():
        gongs[pos].evil_stars.extend(stars)
    
    # 8. 四化
    sihua_list = SIHUA_TABLE.get(year_gan, ["", "", "", ""])
    sihua_stars = {}
    for i, star in enumerate(sihua_list):
        if star:
            sihua_stars[star] = SIHUA[i]
    
    # 標記四化到宮位
    for gong in gongs:
        for star in gong.main_stars:
            if star in sihua_stars:
                gong.sihua.append(f"{star}{sihua_stars[star]}")
    
    return ZiWeiChart(
        year_gan=year_gan,
        year_zhi=year_zhi,
        lunar_month=lunar_month,
        lunar_day=lunar_day,
        hour_zhi=hour_zhi,
        gender=gender,
        ming_gong_idx=ming_gong_idx,
        shen_gong_idx=shen_gong_idx,
        ju_shu=ju_shu,
        ziwei_pos=ziwei_pos,
        tianfu_pos=tianfu_pos,
        gongs=gongs,
        sihua_stars=sihua_stars,
    )


# ===== 場論翻譯（選配） =====
STAR_FIELD_MAP = {
    "紫微": {"field": "帝王場", "energy": "統御、尊貴、自我中心"},
    "天機": {"field": "機變場", "energy": "智慧、變化、不安定"},
    "太陽": {"field": "光明場", "energy": "付出、照耀、消耗"},
    "武曲": {"field": "剛毅場", "energy": "決斷、財務、孤獨"},
    "天同": {"field": "和緩場", "energy": "享樂、懶散、福氣"},
    "廉貞": {"field": "囚禁場", "energy": "執著、桃花、是非"},
    "天府": {"field": "財庫場", "energy": "保守、穩定、守成"},
    "太陰": {"field": "內斂場", "energy": "柔和、藏富、母性"},
    "貪狼": {"field": "慾望場", "energy": "多才、桃花、不滿足"},
    "巨門": {"field": "暗曜場", "energy": "口才、是非、研究"},
    "天相": {"field": "印鑑場", "energy": "輔佐、衣食、被動"},
    "天梁": {"field": "蔭庇場", "energy": "老成、清高、孤獨"},
    "七殺": {"field": "衝鋒場", "energy": "開創、衝動、孤獨"},
    "破軍": {"field": "破壞場", "energy": "變革、耗損、不安"},
}


def field_translation(chart: ZiWeiChart) -> List[str]:
    """
    場論翻譯（描述性，不裁決）
    
    📐 古今融合：
    - 古法星曜結構不變
    - 用場論語言重新描述
    - 不判吉凶，只描述能量特質
    """
    findings = []
    ming_gong = chart.get_ming_gong()
    
    findings.append("【場論視角】")
    findings.append(f"命宮能量場構成：")
    
    for star in ming_gong.main_stars:
        if star in STAR_FIELD_MAP:
            info = STAR_FIELD_MAP[star]
            findings.append(f"  · {star} = {info['field']}：{info['energy']}")
    
    # 四化影響
    if ming_gong.sihua:
        findings.append(f"四化調變：{', '.join(ming_gong.sihua)}")
    
    # 場的整體特質
    if "紫微" in ming_gong.main_stars:
        findings.append("整體場特質：帝王場主導，自我意識強，適合領導角色")
    elif "天機" in ming_gong.main_stars:
        findings.append("整體場特質：機變場主導，思維靈活，適合謀略角色")
    elif "太陽" in ming_gong.main_stars:
        findings.append("整體場特質：光明場主導，願意付出，但需注意能量消耗")
    
    return findings


# ===== 主程式 =====
if __name__ == "__main__":
    print("=" * 60)
    print("紫微斗數引擎 v1.0 測試")
    print("XTF任務: T4 | 執行星: 織明+理樞")
    print("=" * 60)
    
    # 測試：北斗（楊三興）1973年12月30日 寅時
    # 農曆：癸丑年十二月初七
    chart = create_ziwei_chart(
        year_gan="癸",
        year_zhi="丑",
        lunar_month=12,
        lunar_day=7,
        hour_zhi="寅",
        gender="男"
    )
    
    print(chart.summary())
    print()
    
    # 場論翻譯
    field_notes = field_translation(chart)
    for note in field_notes:
        print(note)
