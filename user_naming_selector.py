#!/usr/bin/env python3
"""
user_naming_selector.py - 用戶自選取名系統
北斗命數 v3.1.6

═══════════════════════════════════════════════════════════════════════
逆向工程案例：楊三興 → 楊淳熙
═══════════════════════════════════════════════════════════════════════

【輸入條件】
┌─────────────┬─────────────────────────────────────────────────────┐
│  生辰八字   │  1973/12/30 17:00 → 癸丑年 癸丑月 庚子日 乙酉時     │
│  姓氏       │  楊（13畫）                                         │
│  年齡       │  52歲                                               │
└─────────────┴─────────────────────────────────────────────────────┘

【系統分析】
┌─────────────┬─────────────────────────────────────────────────────┐
│  日主       │  庚金（身強 59分）                                   │
│  五行統計   │  木1 火0 土1 金2.5 水3.5                             │
│  缺失       │  火 ← 缺！                                          │
│  用神       │  水（洩金）                                         │
│  喜神       │  火（剋金）、木（耗金）                             │
│  忌神       │  土、金                                             │
│  補神       │  火（缺失+喜神）                                    │
│  人生階段   │  晚年 → 重總格                                      │
└─────────────┴─────────────────────────────────────────────────────┘

【推薦組合】
┌─────────────┬─────────────────────────────────────────────────────┐
│  水+水      │  雙補用神（楊沛霖、楊泓澤）                         │
│  水+火      │  用神+補缺（楊淳熙、楊涵煜）← 最佳！                │
│  水+木      │  用神+財星（楊泓林）                                │
└─────────────┴─────────────────────────────────────────────────────┘

【用戶選擇】
┌─────────────┬─────────────────────────────────────────────────────┐
│  最終選擇   │  楊淳熙（木+水+火）                                  │
│  五格       │  人24吉 地24吉 總37吉（權威顯達）                   │
│  配合       │  用神水✓ 補缺火✓ 通關木✓                           │
└─────────────┴─────────────────────────────────────────────────────┘

核心原則：系統分析 → 多項推薦 → 用戶自選

PYLIB 依賴：wuxing_analyzer.py
XTF8 層級：L0-L4
@織明 × @理樞
"""

from typing import Dict, List, Tuple, Optional, Set
from dataclasses import dataclass, field
from enum import Enum
import json

# ============================================================
# L0: 常量（從 PYLIB 引用）
# ============================================================

# 五行生剋
WUXING_SHENG = {"木": "火", "火": "土", "土": "金", "金": "水", "水": "木"}
WUXING_KE = {"木": "土", "土": "水", "水": "火", "火": "金", "金": "木"}
WUXING_SHENG_ME = {"木": "水", "火": "木", "土": "火", "金": "土", "水": "金"}
WUXING_KE_ME = {"木": "金", "火": "水", "土": "木", "金": "火", "水": "土"}

# 天干五行
GAN_WUXING = {
    "甲": "木", "乙": "木", "丙": "火", "丁": "火", "戊": "土",
    "己": "土", "庚": "金", "辛": "金", "壬": "水", "癸": "水"
}

# 地支五行
ZHI_WUXING = {
    "子": "水", "丑": "土", "寅": "木", "卯": "木", "辰": "土",
    "巳": "火", "午": "火", "未": "土", "申": "金", "酉": "金",
    "戌": "土", "亥": "水"
}

# 地支藏干
ZHI_CANGGAN = {
    "子": ["癸"], "丑": ["己", "癸", "辛"], "寅": ["甲", "丙", "戊"],
    "卯": ["乙"], "辰": ["戊", "乙", "癸"], "巳": ["丙", "庚", "戊"],
    "午": ["丁", "己"], "未": ["己", "丁", "乙"], "申": ["庚", "壬", "戊"],
    "酉": ["辛"], "戌": ["戊", "辛", "丁"], "亥": ["壬", "甲"]
}

# 數理吉凶（吉數集合）
SHULI_JI = {1, 3, 5, 6, 7, 8, 11, 13, 15, 16, 17, 18, 21, 23, 24, 25, 29, 
            31, 32, 33, 35, 37, 39, 41, 45, 47, 48, 52, 57, 61, 63, 65, 67, 68, 81}

# 數理含義
SHULI_MEANING = {
    15: "福壽共照",
    16: "厚重吉祥",
    21: "首領運",
    24: "掘藏得金",
    29: "智謀優秀",
    32: "寶馬金鞍",
    37: "權威顯達",
    41: "德高望重",
}

def is_ji(n: int) -> bool:
    """判斷數理是否吉"""
    if n > 81:
        n = n % 80 or 80
    return n in SHULI_JI

# ============================================================
# L1: 字庫（精選常用字）
# ============================================================

# 水部首字（用神）
CHAR_SHUI = {
    8:  ["沛", "泓", "泊", "沐", "法"],
    9:  ["泉", "洋", "洛", "津", "泰"],
    10: ["浩", "海", "浚", "洵", "浦"],
    11: ["淳", "涵", "淇", "清", "深", "淑"],  # 淳11畫
    12: ["淵", "渝", "湘", "湛", "渲"],
    13: ["源", "溪", "湧", "溫", "溢"],
    15: ["潤", "潔", "澄", "潮", "潛"],
    16: ["澤", "霖", "澎", "澗"],
}

# 火部首字（補缺）
CHAR_HUO = {
    9:  ["炳", "昱", "映", "昶", "炫"],
    10: ["晉", "晏", "烜", "烽"],
    11: ["晟", "晨", "焜", "烯"],
    12: ["晴", "景", "焯", "焱"],
    13: ["煜", "煒", "熙", "暉", "照"],  # 熙13畫
    15: ["熠", "熹", "暾", "輝"],
    16: ["燁", "曉", "燃", "燈"],
}

# 木部首字（財星）
CHAR_MU = {
    8:  ["林", "松", "杰", "東", "枝"],
    9:  ["柏", "柳", "柯", "桂", "柔"],
    10: ["桐", "桓", "格", "栩", "桑"],
    11: ["梧", "梓", "梅", "梁", "棋"],
    12: ["森", "棠", "棟", "植", "棉"],
    13: ["楠", "楷", "楓", "楚", "榆"],
}

# 字義詞典
CHAR_MEANING = {
    # 水
    "淳": "淳厚純正", "涵": "包涵涵養", "清": "清澈高潔", "深": "深遠深邃",
    "源": "源頭根本", "溪": "清流溪水", "澤": "恩澤潤澤", "霖": "甘霖福澤",
    "浩": "浩瀚廣大", "海": "海納百川", "泓": "水深而廣", "沛": "充沛豐盛",
    # 火
    "熙": "光明興盛", "煜": "光輝照耀", "晟": "光明旺盛", "暉": "陽光光輝",
    "晨": "早晨希望", "景": "光景美景", "照": "照耀光明", "燁": "光華燦爛",
    # 木
    "林": "茂林成蔭", "森": "森林茂盛", "楠": "楠木珍貴", "楓": "楓葉秋紅",
    "梓": "梓木良材", "棟": "棟樑之才", "桐": "梧桐高潔", "柏": "松柏長青",
}

# 常用姓氏筆畫
SURNAME_STROKES = {
    "楊": 13, "陳": 16, "林": 8, "李": 7, "王": 4, "張": 11,
    "劉": 15, "黃": 12, "吳": 7, "周": 8, "徐": 10, "孫": 10,
    "趙": 14, "朱": 6, "何": 7, "郭": 15, "羅": 20, "梁": 11,
    "蔡": 17, "鄭": 19, "許": 11, "謝": 17, "蕭": 18, "曾": 12,
}

# 姓氏五行
SURNAME_WUXING = {
    "楊": "木", "林": "木", "柏": "木", "松": "木", "森": "木",
    "江": "水", "池": "水", "沈": "水", "洪": "水",
    "陳": "土", "黃": "土",
}

# ============================================================
# L2: 資料結構
# ============================================================

@dataclass
class UserInput:
    """用戶輸入"""
    surname: str
    surname_strokes: int
    surname_wuxing: str
    year_pillar: str
    month_pillar: str
    day_pillar: str
    hour_pillar: str
    age: int

@dataclass
class BaziAnalysis:
    """八字分析結果"""
    # 基本資訊
    day_master: str = ""
    day_element: str = ""
    is_strong: bool = False
    strength_score: int = 0
    
    # 五行統計
    wuxing_count: Dict[str, float] = field(default_factory=dict)
    missing: List[str] = field(default_factory=list)  # 缺失五行
    
    # 用神配置
    yongshen: str = ""   # 用神
    xishen: List[str] = field(default_factory=list)  # 喜神
    jishen: List[str] = field(default_factory=list)  # 忌神
    bushen: List[str] = field(default_factory=list)  # 補神（缺失需補）

@dataclass
class LifeStage:
    """人生階段配置"""
    age: int
    stage_name: str      # 童年/青年/中年/晚年
    priority_wuge: str   # 重點五格
    di_weight: float     # 地格權重
    ren_weight: float    # 人格權重
    zong_weight: float   # 總格權重

@dataclass  
class NameOption:
    """候選名字（供用戶選擇）"""
    # 基本資訊
    full_name: str
    char1: str
    char2: str
    stroke1: int
    stroke2: int
    
    # 五行
    wuxing: List[str]      # [姓五行, 名1五行, 名2五行]
    wuxing_desc: str       # 五行描述
    wuxing_flow: str       # 五行流動
    
    # 五格
    ren_ge: int
    di_ge: int
    zong_ge: int
    wai_ge: int
    wuge_desc: str
    
    # 配合分析
    match_yongshen: bool = False  # 配合用神
    match_bushen: bool = False    # 配合補神
    match_desc: str = ""          # 配合描述
    
    # 字義
    meaning: str = ""
    
    # 評分
    wuge_score: int = 0
    bazi_score: int = 0
    total_score: int = 0
    
    # 推薦理由
    recommendation: str = ""

# ============================================================
# L3: 核心系統
# ============================================================

class UserNamingSelector:
    """
    用戶自選取名系統
    
    ═══════════════════════════════════════════════════════════════════
    核心原則：系統分析 → 多項推薦 → 用戶自選
    ═══════════════════════════════════════════════════════════════════
    
    使用流程：
        selector = UserNamingSelector()
        selector.input(surname="楊", ..., age=52)
        selector.analyze()
        options = selector.recommend()
        # 用戶從 options 中自選
    """
    
    def __init__(self):
        self.user: Optional[UserInput] = None
        self.bazi: Optional[BaziAnalysis] = None
        self.stage: Optional[LifeStage] = None
        self.options: List[NameOption] = []
    
    # ══════════════════════════════════════════════════════════
    # 步驟1：輸入用戶資料
    # ══════════════════════════════════════════════════════════
    
    def input(
        self,
        surname: str,
        year_pillar: str,
        month_pillar: str,
        day_pillar: str,
        hour_pillar: str,
        age: int
    ) -> "UserNamingSelector":
        """輸入用戶資料"""
        strokes = SURNAME_STROKES.get(surname, 10)
        wuxing = SURNAME_WUXING.get(surname, "木")
        
        self.user = UserInput(
            surname=surname,
            surname_strokes=strokes,
            surname_wuxing=wuxing,
            year_pillar=year_pillar,
            month_pillar=month_pillar,
            day_pillar=day_pillar,
            hour_pillar=hour_pillar,
            age=age
        )
        return self
    
    # ══════════════════════════════════════════════════════════
    # 步驟2：系統分析
    # ══════════════════════════════════════════════════════════
    
    def analyze(self) -> "UserNamingSelector":
        """執行完整分析"""
        self._analyze_bazi()
        self._analyze_stage()
        return self
    
    def _analyze_bazi(self):
        """分析八字"""
        self.bazi = BaziAnalysis()
        u = self.user
        
        # 日主
        self.bazi.day_master = u.day_pillar[0] if u.day_pillar else ""
        self.bazi.day_element = GAN_WUXING.get(self.bazi.day_master, "")
        
        # 五行統計
        count = {"木": 0, "火": 0, "土": 0, "金": 0, "水": 0}
        
        for pillar in [u.year_pillar, u.month_pillar, u.day_pillar, u.hour_pillar]:
            if pillar:
                # 天干
                gan = pillar[0]
                wx = GAN_WUXING.get(gan, "")
                if wx:
                    count[wx] += 1
                
                # 地支藏干
                if len(pillar) >= 2:
                    zhi = pillar[1]
                    for cang in ZHI_CANGGAN.get(zhi, []):
                        cwx = GAN_WUXING.get(cang, "")
                        if cwx:
                            count[cwx] += 0.5
        
        self.bazi.wuxing_count = count
        self.bazi.missing = [wx for wx, c in count.items() if c == 0]
        
        # 身強身弱
        score = 0
        day_wx = self.bazi.day_element
        
        # 月令
        if u.month_pillar and len(u.month_pillar) >= 2:
            month_zhi = u.month_pillar[1]
            month_wx = ZHI_WUXING.get(month_zhi, "")
            if month_wx == day_wx:
                score += 40
            elif WUXING_SHENG_ME.get(day_wx) == month_wx:
                score += 30
        
        # 通根 + 印比
        for pillar in [u.year_pillar, u.month_pillar, u.day_pillar, u.hour_pillar]:
            if pillar and len(pillar) >= 2:
                zhi = pillar[1]
                for cang in ZHI_CANGGAN.get(zhi, []):
                    if GAN_WUXING.get(cang) == day_wx:
                        score += 8
            if pillar:
                gan_wx = GAN_WUXING.get(pillar[0], "")
                if gan_wx == day_wx or gan_wx == WUXING_SHENG_ME.get(day_wx):
                    score += 3
        
        self.bazi.is_strong = score >= 50
        self.bazi.strength_score = score
        
        # 用神配置
        if self.bazi.is_strong:
            # 身強：用神為洩（食傷）
            self.bazi.yongshen = WUXING_SHENG.get(day_wx, "")  # 金→水
            self.bazi.xishen = [
                WUXING_KE.get(day_wx, ""),      # 金→木（財）
                WUXING_KE_ME.get(day_wx, "")    # 火→金（官）
            ]
            self.bazi.jishen = [
                WUXING_SHENG_ME.get(day_wx, ""),  # 土→金（印）
                day_wx                            # 金（比劫）
            ]
        else:
            # 身弱：用神為生（印）
            self.bazi.yongshen = WUXING_SHENG_ME.get(day_wx, "")
            self.bazi.xishen = [day_wx]
            self.bazi.jishen = [WUXING_KE.get(day_wx, ""), WUXING_SHENG.get(day_wx, "")]
        
        # 補神：缺失的五行中，屬於喜用的
        all_good = [self.bazi.yongshen] + self.bazi.xishen
        self.bazi.bushen = [wx for wx in self.bazi.missing if wx in all_good]
        
        # 清理空值
        self.bazi.xishen = [x for x in self.bazi.xishen if x]
        self.bazi.jishen = [x for x in self.bazi.jishen if x]
    
    def _analyze_stage(self):
        """分析人生階段"""
        age = self.user.age
        
        if age <= 16:
            self.stage = LifeStage(age, "童年", "地格", 2.0, 1.0, 0.5)
        elif age <= 32:
            self.stage = LifeStage(age, "青年", "地格+人格", 1.5, 1.5, 0.8)
        elif age <= 48:
            self.stage = LifeStage(age, "中年", "人格", 0.8, 2.0, 1.0)
        else:
            self.stage = LifeStage(age, "晚年", "總格", 0.5, 1.0, 2.0)
    
    # ══════════════════════════════════════════════════════════
    # 步驟3：生成候選（多項推薦）
    # ══════════════════════════════════════════════════════════
    
    def recommend(self, count: int = 20) -> List[NameOption]:
        """生成候選名字供用戶選擇"""
        self.options = []
        
        # 1. 獲取五行組合策略
        combos = self._get_wuxing_combos()
        
        # 2. 獲取最佳筆畫組合
        strokes = self._get_best_strokes()
        
        # 3. 生成候選（確保各種組合都有機會）
        for wx1, wx2 in combos:  # 先遍歷五行組合
            for s1, s2 in strokes:
                chars1 = self._get_chars(s1, wx1)
                chars2 = self._get_chars(s2, wx2)
                
                for c1 in chars1[:5]:  # 增加字數
                    for c2 in chars2[:5]:
                        opt = self._create_option(c1, c2, s1, s2, wx1, wx2)
                        if opt:
                            self.options.append(opt)
        
        # 4. 去重並排序
        seen = set()
        unique = []
        for opt in self.options:
            if opt.full_name not in seen:
                seen.add(opt.full_name)
                unique.append(opt)
        
        unique.sort(key=lambda x: -x.total_score)
        self.options = unique[:count]
        
        return self.options
    
    def _get_wuxing_combos(self) -> List[Tuple[str, str]]:
        """
        獲取五行組合策略
        
        策略優先級：
        1. 用神 + 補缺（水+火）← 最佳
        2. 用神 + 用神（水+水）
        3. 用神 + 喜神（水+木）
        """
        combos = []
        yong = self.bazi.yongshen
        bu = self.bazi.bushen
        xi = self.bazi.xishen
        
        # 策略1：用神 + 補缺（最佳組合）
        for b in bu:
            combos.append((yong, b))
            combos.append((b, yong))
        
        # 策略2：用神 + 用神
        combos.append((yong, yong))
        
        # 策略3：用神 + 喜神
        for x in xi:
            if x != yong and x not in bu:
                combos.append((yong, x))
                combos.append((x, yong))
        
        # 策略4：補缺 + 喜神
        for b in bu:
            for x in xi:
                if b != x:
                    combos.append((b, x))
        
        return combos
    
    def _get_best_strokes(self) -> List[Tuple[int, int]]:
        """獲取最佳筆畫組合"""
        results = []
        xing = self.user.surname_strokes
        
        for s1 in range(8, 18):  # 擴大範圍 8-17
            for s2 in range(8, 18):
                ren = xing + s1
                di = s1 + s2
                zong = xing + s1 + s2
                
                # 三格必須吉
                if is_ji(ren) and is_ji(di) and is_ji(zong):
                    # 加權評分
                    score = (
                        (20 if is_ji(ren) else 0) * self.stage.ren_weight +
                        (20 if is_ji(di) else 0) * self.stage.di_weight +
                        (20 if is_ji(zong) else 0) * self.stage.zong_weight
                    )
                    results.append((s1, s2, score))
        
        results.sort(key=lambda x: (-x[2], x[0] + x[1]))
        return [(r[0], r[1]) for r in results[:30]]  # 取更多組合
    
    def _get_chars(self, stroke: int, wuxing: str) -> List[str]:
        """獲取指定筆畫和五行的漢字"""
        if wuxing == "水":
            return CHAR_SHUI.get(stroke, [])
        elif wuxing == "火":
            return CHAR_HUO.get(stroke, [])
        elif wuxing == "木":
            return CHAR_MU.get(stroke, [])
        return []
    
    def _create_option(
        self, c1: str, c2: str, s1: int, s2: int, wx1: str, wx2: str
    ) -> Optional[NameOption]:
        """創建候選名字"""
        xing = self.user.surname_strokes
        surname = self.user.surname
        surname_wx = self.user.surname_wuxing
        
        # 五格計算
        ren = xing + s1
        di = s1 + s2
        zong = xing + s1 + s2
        wai = zong - ren + 1
        
        # 三格必須吉
        if not (is_ji(ren) and is_ji(di) and is_ji(zong)):
            return None
        
        # 五格分數（加權）
        wuge_score = int(
            20 * self.stage.ren_weight +
            20 * self.stage.di_weight +
            20 * self.stage.zong_weight +
            (10 if is_ji(wai) else 0)
        )
        
        # 八字配合分數
        bazi_score = 50
        match_yongshen = False
        match_bushen = False
        match_parts = []
        
        for wx in [wx1, wx2]:
            if wx == self.bazi.yongshen:
                bazi_score += 25
                match_yongshen = True
                match_parts.append(f"{wx}(用神)")
            elif wx in self.bazi.bushen:
                bazi_score += 20
                match_bushen = True
                match_parts.append(f"{wx}(補缺)")
            elif wx in self.bazi.xishen:
                bazi_score += 15
                match_parts.append(f"{wx}(喜神)")
            elif wx in self.bazi.jishen:
                bazi_score -= 20
        
        bazi_score = min(100, max(0, bazi_score))
        
        # 五行描述
        wuxing = [surname_wx, wx1, wx2]
        wuxing_desc = f"{surname_wx}+{wx1}+{wx2}"
        
        # 五行流動
        flows = []
        if WUXING_SHENG.get(surname_wx) == wx1:
            flows.append(f"{surname_wx}生{wx1}")
        if WUXING_SHENG.get(wx1) == wx2:
            flows.append(f"{wx1}生{wx2}")
        if surname_wx == "木" and wx1 == "水" and wx2 == "火":
            flows.append("木通關水火")
        wuxing_flow = "、".join(flows) if flows else "五行調和"
        
        # 五格描述
        ren_m = SHULI_MEANING.get(ren, "")
        zong_m = SHULI_MEANING.get(zong, "")
        wuge_desc = f"人{ren}吉{f'({ren_m})' if ren_m else ''} 地{di}吉 總{zong}吉{f'({zong_m})' if zong_m else ''}"
        
        # 字義
        m1 = CHAR_MEANING.get(c1, c1)
        m2 = CHAR_MEANING.get(c2, c2)
        meaning = f"{m1} + {m2}"
        
        # 推薦理由
        reasons = []
        if match_yongshen and match_bushen:
            reasons.append("用神+補缺 最佳組合")
        elif match_yongshen:
            reasons.append(f"配合用神{self.bazi.yongshen}")
        elif match_bushen:
            reasons.append(f"補足缺{self.bazi.bushen[0] if self.bazi.bushen else ''}")
        if zong_m:
            reasons.append(f"總格{zong}{zong_m}")
        
        return NameOption(
            full_name=f"{surname}{c1}{c2}",
            char1=c1,
            char2=c2,
            stroke1=s1,
            stroke2=s2,
            wuxing=wuxing,
            wuxing_desc=wuxing_desc,
            wuxing_flow=wuxing_flow,
            ren_ge=ren,
            di_ge=di,
            zong_ge=zong,
            wai_ge=wai,
            wuge_desc=wuge_desc,
            match_yongshen=match_yongshen,
            match_bushen=match_bushen,
            match_desc=" + ".join(match_parts),
            meaning=meaning,
            wuge_score=wuge_score,
            bazi_score=bazi_score,
            total_score=wuge_score + bazi_score,
            recommendation="、".join(reasons) if reasons else "五格全吉"
        )
    
    # ══════════════════════════════════════════════════════════
    # 輸出報告
    # ══════════════════════════════════════════════════════════
    
    def get_analysis_report(self) -> str:
        """獲取分析報告"""
        lines = []
        lines.append("═" * 60)
        lines.append("【系統分析報告】")
        lines.append("═" * 60)
        
        u = self.user
        b = self.bazi
        s = self.stage
        
        lines.append(f"\n┌{'─'*58}┐")
        lines.append(f"│  姓氏：{u.surname}（{u.surname_strokes}畫，{u.surname_wuxing}）{' '*30}│")
        lines.append(f"│  四柱：{u.year_pillar}年 {u.month_pillar}月 {u.day_pillar}日 {u.hour_pillar}時{' '*20}│")
        lines.append(f"│  年齡：{u.age}歲（{s.stage_name}）{' '*36}│")
        lines.append(f"└{'─'*58}┘")
        
        lines.append(f"\n【八字分析】")
        lines.append(f"  日主：{b.day_master}（{b.day_element}）")
        lines.append(f"  身強：{'是' if b.is_strong else '否'}（{b.strength_score}分）")
        
        lines.append(f"\n【五行統計】")
        for wx in ["木", "火", "土", "金", "水"]:
            c = b.wuxing_count.get(wx, 0)
            bar = "█" * int(c) + "░" * (5 - int(c))
            mark = " ← 缺！" if c == 0 else ""
            lines.append(f"  {wx}：{bar} ({c}){mark}")
        
        lines.append(f"\n【用神配置】")
        lines.append(f"  用神：{b.yongshen} ← 最需要")
        lines.append(f"  喜神：{b.xishen}")
        lines.append(f"  忌神：{b.jishen} ← 要避開")
        if b.bushen:
            lines.append(f"  補神：{b.bushen} ← 缺失要補！")
        
        lines.append(f"\n【人生階段】")
        lines.append(f"  階段：{s.stage_name}（{s.age}歲）")
        lines.append(f"  重點：{s.priority_wuge}")
        
        return "\n".join(lines)
    
    def get_options_report(self) -> str:
        """獲取候選名字報告（供用戶選擇）"""
        lines = []
        lines.append("\n" + "═" * 60)
        lines.append("【候選名字】請自選")
        lines.append("═" * 60)
        
        lines.append(f"\n共 {len(self.options)} 個候選，按評分排序：\n")
        
        for i, opt in enumerate(self.options, 1):
            star = "🏆" if opt.match_yongshen and opt.match_bushen else "  "
            lines.append(f"{star}【{i:2}】{opt.full_name}  （{opt.total_score}分）")
            lines.append(f"      五行：{opt.wuxing_desc} → {opt.wuxing_flow}")
            lines.append(f"      五格：{opt.wuge_desc}")
            lines.append(f"      字義：{opt.meaning}")
            lines.append(f"      配合：{opt.match_desc}")
            lines.append(f"      推薦：{opt.recommendation}")
            lines.append("")
        
        lines.append("─" * 60)
        lines.append("請根據以下考量自行選擇：")
        lines.append("  1. 字義寓意 - 是否喜歡")
        lines.append("  2. 讀音順口 - 是否好聽")
        lines.append("  3. 書寫美觀 - 是否好寫")
        lines.append("  4. 個人感覺 - 直覺偏好")
        lines.append("─" * 60)
        lines.append("\n🏆 = 用神+補缺 最佳組合")
        
        return "\n".join(lines)


# ============================================================
# L4: 便捷函數
# ============================================================

def analyze_and_recommend(
    surname: str,
    year_pillar: str,
    month_pillar: str,
    day_pillar: str,
    hour_pillar: str,
    age: int,
    count: int = 15
) -> Tuple["UserNamingSelector", List[NameOption]]:
    """
    便捷函數：一站式分析並推薦
    
    範例：
        selector, options = analyze_and_recommend(
            surname="楊",
            year_pillar="癸丑",
            month_pillar="癸丑",
            day_pillar="庚子",
            hour_pillar="乙酉",
            age=52
        )
        
        print(selector.get_analysis_report())
        print(selector.get_options_report())
    """
    selector = UserNamingSelector()
    selector.input(
        surname=surname,
        year_pillar=year_pillar,
        month_pillar=month_pillar,
        day_pillar=day_pillar,
        hour_pillar=hour_pillar,
        age=age
    )
    selector.analyze()
    options = selector.recommend(count)
    
    return selector, options


# ============================================================
# 測試：驗證案例 楊三興 → 楊淳熙
# ============================================================

if __name__ == "__main__":
    print("═" * 70)
    print("        用戶自選取名系統 - 案例驗證")
    print("        楊三興 1973/12/30 17:00 52歲 → 楊淳熙")
    print("═" * 70)
    
    # 執行分析
    selector, options = analyze_and_recommend(
        surname="楊",
        year_pillar="癸丑",
        month_pillar="癸丑",
        day_pillar="庚子",
        hour_pillar="乙酉",
        age=52,
        count=20
    )
    
    # 輸出分析報告
    print(selector.get_analysis_report())
    
    # 輸出候選名字
    print(selector.get_options_report())
    
    # 驗證楊淳熙
    print("\n" + "═" * 70)
    print("【驗證：楊淳熙】")
    print("═" * 70)
    
    found = None
    for opt in options:
        if opt.full_name == "楊淳熙":
            found = opt
            break
    
    if found:
        print(f"""
    ✅ 楊淳熙 在候選列表中！
    
    五行：{found.wuxing_desc}（{found.wuxing_flow}）
    五格：{found.wuge_desc}
    字義：{found.meaning}
    配合：{found.match_desc}
    推薦：{found.recommendation}
    評分：{found.total_score}分
    
    配合用神：{'✓' if found.match_yongshen else '✗'}
    配合補缺：{'✓' if found.match_bushen else '✗'}
        """)
    else:
        print("    ⚠️ 楊淳熙 未在列表中")
    
    print("═" * 70)
    print("核心原則：系統分析 → 多項推薦 → 用戶自選")
    print("═" * 70)
