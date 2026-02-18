#!/usr/bin/env python3
"""
naming_master.py - 北斗命數取名決策系統
版本：v4.1.0

═══════════════════════════════════════════════════════════════════════
逆向工程案例：楊三興 1973/12/30 17:00 52歲
最終決策：
  • 楊涵煜（法定身份證）— 涵養光輝，深沉內斂
  • 楊淳煜（備用/筆名）— 淳厚光輝，溫潤質樸
  • 北斗（公司/對外身份/筆名）
═══════════════════════════════════════════════════════════════════════

15維度 DOE 體系：
  L1（1.5）：D2用神 D3補缺 D4避忌 — 核心命理
  L2（1.2）：D1五格 D6字義 — 重要考量
  L3（1.0）：D5格行 D7讀音 D9三才 D12諧音 — 標準
  L4（0.8）：D10書寫 D11獨特 — 實用參考
  L5（0.5）：D8生肖 D13易卦 D14靈數 D15五音 — 參考

關鍵決策：
  • D8 生肖權重 1.2→0.5：「牛忌日」為文化象徵，非動物本性
  • 煜（2-2-4）優於 熙（2-2-1）：尾音去聲，頓挫有力

核心原則：
  1. 系統分析 → 多項推薦 → 用戶自選
  2. 用神 > 補缺 > 平衡（不是缺什麼補什麼）
  3. 缺的是忌神 → 不補！缺了是福
  4. DOE 多目標優化 → Pareto 最優解集
  5. 名字 = 場的延伸（後天場調和先天場）

PYLIB 依賴：無（獨立模組）
XTF8 層級：L0-L4
@織明 × @理樞
"""

from typing import Dict, List, Tuple, Optional, Set
from dataclasses import dataclass, field
from enum import Enum
import json

# ════════════════════════════════════════════════════════════════════
# L0: 常量定義
# ════════════════════════════════════════════════════════════════════

# 五行關係
SHENG = {"木": "火", "火": "土", "土": "金", "金": "水", "水": "木"}      # 我生
KE = {"木": "土", "土": "水", "水": "火", "火": "金", "金": "木"}         # 我剋
SHENG_ME = {"木": "水", "火": "木", "土": "火", "金": "土", "水": "金"}   # 生我
KE_ME = {"木": "金", "火": "水", "土": "木", "金": "火", "水": "土"}      # 剋我

# 天干五行
GAN_WX = {
    "甲": "木", "乙": "木", "丙": "火", "丁": "火", "戊": "土",
    "己": "土", "庚": "金", "辛": "金", "壬": "水", "癸": "水"
}

# 地支五行
ZHI_WX = {
    "子": "水", "丑": "土", "寅": "木", "卯": "木", "辰": "土", "巳": "火",
    "午": "火", "未": "土", "申": "金", "酉": "金", "戌": "土", "亥": "水"
}

# 地支藏干
ZHI_CANG = {
    "子": ["癸"], "丑": ["己", "癸", "辛"], "寅": ["甲", "丙", "戊"],
    "卯": ["乙"], "辰": ["戊", "乙", "癸"], "巳": ["丙", "庚", "戊"],
    "午": ["丁", "己"], "未": ["己", "丁", "乙"], "申": ["庚", "壬", "戊"],
    "酉": ["辛"], "戌": ["戊", "辛", "丁"], "亥": ["壬", "甲"]
}

# 吉數
JI_SHU = {1,3,5,6,7,8,11,13,15,16,17,18,21,23,24,25,29,31,32,33,35,37,39,
          41,45,47,48,52,57,61,63,65,67,68,81}

# 數理含義
SHU_MEANING = {
    15: "福壽共照", 16: "厚重吉祥", 21: "首領運", 24: "掘藏得金",
    29: "智謀優秀", 32: "寶馬金鞍", 37: "權威顯達", 41: "德高望重"
}

# 數理尾數五行
def shuli_wuxing(n: int) -> str:
    """數理尾數 → 五行"""
    tail = n % 10
    if tail in [1, 2]: return "木"
    elif tail in [3, 4]: return "火"
    elif tail in [5, 6]: return "土"
    elif tail in [7, 8]: return "金"
    else: return "水"

# 生肖配合（牛）
SHENGXIAO_NIU = {
    "喜": ["氵", "水", "艹", "禾", "田", "宀", "冖", "广", "車"],
    "忌": ["日", "山", "心", "忄", "馬", "羊", "王", "玉"],
}

# 字的生肖評分
def calc_shengxiao_score(char: str, char_info: "CharInfo") -> int:
    """計算字的生肖配合分數（牛）"""
    # 水部首：牛喜水
    if char_info.wuxing == "水":
        return 100
    
    # 檢查是否含日
    if "日" in char or char in ["煜", "暉", "晟", "晨", "晴", "景", "照", "曉"]:
        return 50
    
    # 火部但無日
    if char_info.wuxing == "火":
        if char in ["熙", "煒"]:  # 無日字的火字
            return 80
        return 60
    
    # 木部
    if char_info.wuxing == "木":
        return 85
    
    return 75

# 三才配置
def calc_sancai_score(tian_wx: str, ren_wx: str, di_wx: str) -> Tuple[int, str]:
    """計算三才配置分數"""
    score = 70
    desc_parts = []
    
    # 天 → 人
    if SHENG.get(tian_wx) == ren_wx:
        score += 15
        desc_parts.append(f"天生人({tian_wx}→{ren_wx})吉")
    elif tian_wx == ren_wx:
        score += 5
        desc_parts.append(f"天人同({tian_wx})")
    elif KE.get(tian_wx) == ren_wx:
        score -= 10
        desc_parts.append(f"天剋人凶")
    elif KE.get(ren_wx) == tian_wx:
        score -= 5
        desc_parts.append(f"人剋天小凶")
    
    # 人 → 地
    if SHENG.get(ren_wx) == di_wx:
        score += 15
        desc_parts.append(f"人生地({ren_wx}→{di_wx})吉")
    elif ren_wx == di_wx:
        score += 5
        desc_parts.append(f"人地同({ren_wx})")
    elif KE.get(ren_wx) == di_wx:
        score -= 10
        desc_parts.append(f"人剋地凶")
    elif KE.get(di_wx) == ren_wx:
        score -= 5
        desc_parts.append(f"地剋人小凶")
    
    # 天地關係
    if SHENG.get(tian_wx) == di_wx or SHENG.get(di_wx) == tian_wx:
        score += 5
        desc_parts.append("天地相生")
    elif tian_wx == di_wx:
        score += 3
    
    return min(100, max(40, score)), "，".join(desc_parts)

# D10: 書寫平衡
def calc_writing_score(s1: int, s2: int, s3: int, struct1: str, struct2: str) -> int:
    """計算書寫平衡分數"""
    score = 80
    
    # 筆畫差異
    max_diff = max(abs(s1-s2), abs(s2-s3), abs(s1-s3))
    if max_diff <= 3:
        score += 5
    elif max_diff >= 8:
        score -= 10
    
    # 趨勢
    if s1 <= s2 <= s3 or s1 >= s2 >= s3:
        score += 5
    elif s2 < s1 and s2 < s3:
        score -= 5
    
    # 結構搭配
    if struct1 == "左右" and struct2 == "左右":
        score += 5
    elif (struct1 == "左右" and struct2 == "上下") or \
         (struct1 == "上下" and struct2 == "左右"):
        score += 3
    
    return min(100, max(60, score))

# D11: 獨特性
CHAR_RARITY = {
    "明": 30, "華": 30, "偉": 30, "強": 30, "文": 35,
    "海": 40, "浩": 40, "林": 45, "森": 50,
    "清": 70, "深": 75, "涵": 80, "淳": 85,
    "熙": 88, "煜": 90, "淇": 92, "燁": 93, "煒": 94,
    "澤": 85, "霖": 88, "沛": 86,
}

def calc_unique_score(c1: str, c2: str) -> int:
    """計算獨特性分數"""
    s1 = CHAR_RARITY.get(c1, 80)
    s2 = CHAR_RARITY.get(c2, 80)
    return (s1 + s2) // 2

# D12: 諧音禁忌
def calc_xieyin_score(pinyin: str) -> int:
    """計算諧音分數"""
    bad_patterns = ["yangwei", "si", "gui", "sang", "ku"]
    pinyin_lower = pinyin.lower().replace(" ", "")
    
    for pattern in bad_patterns:
        if pattern in pinyin_lower:
            return 50
    return 100

# D13: 易經卦象
def calc_yijing_score(xing: int, ming: int) -> int:
    """計算易經卦象分數"""
    # 簡化：基於筆畫總數
    total = xing + ming
    # 吉數
    if total in [15, 16, 24, 32, 37, 41, 45]:
        return 90
    elif total % 8 == 0:
        return 85
    return 80

# D14: 數字能量
def calc_numerology_score(total: int) -> int:
    """計算數字能量分數"""
    # 生命靈數
    n = total
    while n >= 10:
        n = sum(int(d) for d in str(n))
    
    # 靈數評分
    scores = {1: 90, 2: 85, 3: 88, 4: 85, 5: 82, 6: 88, 7: 90, 8: 92, 9: 95}
    return scores.get(n, 80)

# D15: 五音歸元
def calc_wuyin_score(p1: str, p2: str, p3: str) -> int:
    """計算五音分數"""
    def get_wuyin_wx(pinyin: str) -> str:
        first = pinyin[0].lower() if pinyin else "g"
        if first in ['g', 'k', 'h']: return "土"
        elif first in ['z', 'c', 's']: return "金"
        elif first in ['j', 'q', 'x']: return "木"
        elif first in ['d', 't', 'n', 'l']: return "火"
        else: return "水"
    
    wx1 = get_wuyin_wx(p1)
    wx2 = get_wuyin_wx(p2)
    wx3 = get_wuyin_wx(p3)
    
    score = 75
    # 相生加分
    if SHENG.get(wx1) == wx2:
        score += 5
    if SHENG.get(wx2) == wx3:
        score += 5
    # 相剋減分
    if KE.get(wx1) == wx2 or KE.get(wx2) == wx1:
        score -= 5
    if KE.get(wx2) == wx3 or KE.get(wx3) == wx2:
        score -= 5
    
    return min(100, max(60, score))

# 字的結構類型
CHAR_STRUCTURE = {
    "淳": "左右", "涵": "左右", "清": "左右", "沛": "左右", "深": "左右",
    "浩": "左右", "海": "左右", "泓": "左右", "源": "左右", "溪": "左右",
    "澤": "左右", "霖": "上下", "潤": "左右", "淇": "左右",
    "熙": "上下", "煜": "左右", "煒": "左右", "暉": "左右", "照": "上下",
    "晟": "上下", "晨": "上下", "燁": "左右", "曉": "左右",
}

# ════════════════════════════════════════════════════════════════════
# L1: 字庫（含讀音）
# ════════════════════════════════════════════════════════════════════

@dataclass
class CharInfo:
    """漢字資訊"""
    char: str
    stroke: int
    wuxing: str
    pinyin: str
    tone: int  # 1-4聲
    meaning: str

# 水字庫
CHAR_SHUI = [
    CharInfo("淳", 11, "水", "chún", 2, "淳厚純正"),
    CharInfo("涵", 11, "水", "hán", 2, "涵養包容"),
    CharInfo("淇", 11, "水", "qí", 2, "清澈淇水"),
    CharInfo("清", 11, "水", "qīng", 1, "清澈高潔"),
    CharInfo("深", 11, "水", "shēn", 1, "深遠深邃"),
    CharInfo("浩", 10, "水", "hào", 4, "浩瀚廣大"),
    CharInfo("海", 10, "水", "hǎi", 3, "海納百川"),
    CharInfo("泓", 8, "水", "hóng", 2, "水深而廣"),
    CharInfo("沛", 8, "水", "pèi", 4, "充沛豐盛"),
    CharInfo("源", 13, "水", "yuán", 2, "源頭根本"),
    CharInfo("溪", 13, "水", "xī", 1, "清流溪水"),
    CharInfo("澤", 16, "水", "zé", 2, "恩澤潤澤"),
    CharInfo("霖", 16, "水", "lín", 2, "甘霖福澤"),
    CharInfo("潤", 15, "水", "rùn", 4, "潤澤滋養"),
]

# 火字庫
CHAR_HUO = [
    CharInfo("熙", 13, "火", "xī", 1, "光明興盛"),
    CharInfo("煜", 13, "火", "yù", 4, "光輝照耀"),
    CharInfo("煒", 13, "火", "wěi", 3, "光彩煒煒"),
    CharInfo("暉", 13, "火", "huī", 1, "陽光光輝"),
    CharInfo("照", 13, "火", "zhào", 4, "照耀光明"),
    CharInfo("晟", 11, "火", "shèng", 4, "光明旺盛"),
    CharInfo("晨", 11, "火", "chén", 2, "早晨希望"),
    CharInfo("晴", 12, "火", "qíng", 2, "晴朗明媚"),
    CharInfo("景", 12, "火", "jǐng", 3, "光景美景"),
    CharInfo("燁", 16, "火", "yè", 4, "光華燦爛"),
    CharInfo("曉", 16, "火", "xiǎo", 3, "破曉黎明"),
]

# 木字庫
CHAR_MU = [
    CharInfo("林", 8, "木", "lín", 2, "茂林成蔭"),
    CharInfo("森", 12, "木", "sēn", 1, "森林茂盛"),
    CharInfo("楠", 13, "木", "nán", 2, "楠木珍貴"),
    CharInfo("楓", 13, "木", "fēng", 1, "楓葉秋紅"),
    CharInfo("梓", 11, "木", "zǐ", 3, "梓木良材"),
    CharInfo("棟", 12, "木", "dòng", 4, "棟樑之才"),
    CharInfo("桐", 10, "木", "tóng", 2, "梧桐高潔"),
    CharInfo("柏", 9, "木", "bǎi", 3, "松柏長青"),
]

# 字庫索引
CHAR_DB = {}
for c in CHAR_SHUI + CHAR_HUO + CHAR_MU:
    key = (c.stroke, c.wuxing)
    if key not in CHAR_DB:
        CHAR_DB[key] = []
    CHAR_DB[key].append(c)

def get_chars(stroke: int, wuxing: str) -> List[CharInfo]:
    """獲取指定筆畫和五行的漢字"""
    return CHAR_DB.get((stroke, wuxing), [])

# 姓氏資料
SURNAME_DB = {
    "楊": {"stroke": 13, "wuxing": "木", "pinyin": "yáng", "tone": 2},
    "陳": {"stroke": 16, "wuxing": "土", "pinyin": "chén", "tone": 2},
    "林": {"stroke": 8, "wuxing": "木", "pinyin": "lín", "tone": 2},
    "李": {"stroke": 7, "wuxing": "木", "pinyin": "lǐ", "tone": 3},
    "王": {"stroke": 4, "wuxing": "土", "pinyin": "wáng", "tone": 2},
    "張": {"stroke": 11, "wuxing": "火", "pinyin": "zhāng", "tone": 1},
}

# ════════════════════════════════════════════════════════════════════
# L2: 資料結構
# ════════════════════════════════════════════════════════════════════

class ShenType(Enum):
    """四神類型"""
    YONGSHEN = "用神"
    XISHEN = "喜神"
    JISHEN = "忌神"
    XIANSHEN = "閒神"

@dataclass
class BaziAnalysis:
    """八字分析結果"""
    day_master: str = ""
    day_wx: str = ""
    is_strong: bool = False
    strength_score: int = 0
    
    wx_count: Dict[str, float] = field(default_factory=dict)
    missing: List[str] = field(default_factory=list)
    
    yongshen: str = ""
    xishen: List[str] = field(default_factory=list)
    jishen: List[str] = field(default_factory=list)
    xianshen: List[str] = field(default_factory=list)
    bushen: List[str] = field(default_factory=list)  # 缺失需補

@dataclass
class LifeStage:
    """人生階段"""
    age: int
    name: str
    priority: str
    di_weight: float
    ren_weight: float
    zong_weight: float

@dataclass
class DOEScore:
    """DOE 15維度評分"""
    # 命理層
    wuge: int = 0           # D1: 五格數理
    yongshen: int = 0       # D2: 用神配合
    bushen: int = 0         # D3: 補缺配合
    avoid_ji: int = 0       # D4: 避忌配合
    wuge_wx: int = 0        # D5: 五格五行
    # 語言層
    meaning: int = 0        # D6: 字義
    sound: int = 0          # D7: 讀音
    # 傳統層
    shengxiao: int = 0      # D8: 生肖配合
    sancai: int = 0         # D9: 三才配置
    # 實用層
    writing: int = 0        # D10: 書寫平衡
    unique: int = 0         # D11: 獨特性
    xieyin: int = 0         # D12: 諧音禁忌
    # 玄學層
    yijing: int = 0         # D13: 易經卦象
    numerology: int = 0     # D14: 數字能量
    wuyin: int = 0          # D15: 五音歸元
    # 總分
    raw_total: int = 0      # 原始總分
    weighted_total: float = 0.0  # 加權總分

# 15維度權重
DOE_WEIGHTS = {
    "wuge": 1.2,        # D1
    "yongshen": 1.5,    # D2 核心
    "bushen": 1.5,      # D3 核心
    "avoid_ji": 1.5,    # D4 核心
    "wuge_wx": 1.0,     # D5
    "meaning": 1.2,     # D6
    "sound": 1.0,       # D7
    "shengxiao": 0.5,   # D8 降權：生肖喜忌多為文化象徵，非動物本性
    "sancai": 1.0,      # D9
    "writing": 0.8,     # D10
    "unique": 0.8,      # D11
    "xieyin": 1.0,      # D12
    "yijing": 0.5,      # D13
    "numerology": 0.5,  # D14
    "wuyin": 0.5,       # D15
}

@dataclass
class NameCandidate:
    """候選名字"""
    full_name: str
    chars: List[str]
    strokes: List[int]
    wuxing: List[str]
    pinyin: str
    tones: List[int]
    
    # 五格
    ren_ge: int = 0
    di_ge: int = 0
    zong_ge: int = 0
    wai_ge: int = 0
    wuge_desc: str = ""
    
    # 配合
    match_yongshen: bool = False
    match_bushen: bool = False
    match_desc: str = ""
    
    # 字義
    meaning: str = ""
    imagery: str = ""  # 意象
    
    # DOE 評分
    doe: DOEScore = field(default_factory=DOEScore)
    
    # 推薦理由
    recommendation: str = ""

# ════════════════════════════════════════════════════════════════════
# L3: 核心系統
# ════════════════════════════════════════════════════════════════════

class NamingMaster:
    """
    北斗命數取名決策系統
    
    核心原則：
    1. 系統分析 → 多項推薦 → 用戶自選
    2. 用神 > 補缺 > 平衡
    3. DOE 多目標優化
    4. 名字 = 場的延伸
    
    使用流程：
        master = NamingMaster()
        master.set_input("楊", "癸丑", "癸丑", "庚子", "乙酉", 52)
        master.analyze()
        candidates = master.recommend()
        # 用戶從 candidates 自選
    """
    
    def __init__(self):
        self.surname = ""
        self.surname_info = {}
        self.pillars = []
        self.age = 0
        self.bazi: Optional[BaziAnalysis] = None
        self.stage: Optional[LifeStage] = None
        self.candidates: List[NameCandidate] = []
    
    # ────────────────────────────────────────────────────────────────
    # 步驟1：輸入
    # ────────────────────────────────────────────────────────────────
    
    def set_input(self, surname: str, year: str, month: str, 
                  day: str, hour: str, age: int) -> "NamingMaster":
        """設定輸入"""
        self.surname = surname
        self.surname_info = SURNAME_DB.get(surname, {
            "stroke": len(surname) * 10, "wuxing": "木", 
            "pinyin": surname, "tone": 2
        })
        self.pillars = [year, month, day, hour]
        self.age = age
        return self
    
    # ────────────────────────────────────────────────────────────────
    # 步驟2：分析
    # ────────────────────────────────────────────────────────────────
    
    def analyze(self) -> "NamingMaster":
        """執行完整分析"""
        self._analyze_bazi()
        self._analyze_stage()
        return self
    
    def _analyze_bazi(self):
        """分析八字"""
        self.bazi = BaziAnalysis()
        
        # 日主
        day = self.pillars[2]
        self.bazi.day_master = day[0] if day else ""
        self.bazi.day_wx = GAN_WX.get(self.bazi.day_master, "")
        
        # 五行統計
        count = {"木": 0, "火": 0, "土": 0, "金": 0, "水": 0}
        for p in self.pillars:
            if p:
                wx = GAN_WX.get(p[0], "")
                if wx: count[wx] += 1
                if len(p) >= 2:
                    for c in ZHI_CANG.get(p[1], []):
                        cwx = GAN_WX.get(c, "")
                        if cwx: count[cwx] += 0.5
        
        self.bazi.wx_count = count
        self.bazi.missing = [wx for wx, c in count.items() if c == 0]
        
        # 身強弱
        score = 0
        day_wx = self.bazi.day_wx
        month = self.pillars[1]
        
        if month and len(month) >= 2:
            mwx = ZHI_WX.get(month[1], "")
            if mwx == day_wx: score += 40
            elif SHENG_ME.get(day_wx) == mwx: score += 30
        
        for p in self.pillars:
            if p and len(p) >= 2:
                for c in ZHI_CANG.get(p[1], []):
                    if GAN_WX.get(c) == day_wx: score += 8
            if p:
                gwx = GAN_WX.get(p[0], "")
                if gwx == day_wx or gwx == SHENG_ME.get(day_wx): score += 3
        
        self.bazi.is_strong = score >= 50
        self.bazi.strength_score = score
        
        # 四神配置
        self._calc_four_shen()
    
    def _calc_four_shen(self):
        """計算四神（用神/喜神/忌神/閒神）"""
        day_wx = self.bazi.day_wx
        is_strong = self.bazi.is_strong
        
        if is_strong:
            # 身強：洩剋耗
            self.bazi.yongshen = SHENG.get(day_wx, "")       # 食傷（洩）
            self.bazi.xishen = [
                KE.get(day_wx, ""),                          # 財（耗）
                KE_ME.get(day_wx, "")                        # 官殺（剋）
            ]
            self.bazi.jishen = [
                SHENG_ME.get(day_wx, ""),                    # 印（生）
                day_wx                                        # 比劫（助）
            ]
        else:
            # 身弱：生助
            self.bazi.yongshen = SHENG_ME.get(day_wx, "")    # 印（生）
            self.bazi.xishen = [day_wx]                       # 比劫（助）
            self.bazi.jishen = [
                SHENG.get(day_wx, ""),                        # 食傷（洩）
                KE.get(day_wx, ""),                           # 財（耗）
                KE_ME.get(day_wx, "")                         # 官殺（剋）
            ]
        
        # 閒神：既非喜用也非忌神
        all_wx = {"木", "火", "土", "金", "水"}
        used = {self.bazi.yongshen} | set(self.bazi.xishen) | set(self.bazi.jishen)
        self.bazi.xianshen = list(all_wx - used)
        
        # 補神：缺失中屬於喜用的
        good = [self.bazi.yongshen] + self.bazi.xishen
        self.bazi.bushen = [wx for wx in self.bazi.missing if wx in good]
        
        # 清理
        self.bazi.xishen = [x for x in self.bazi.xishen if x]
        self.bazi.jishen = [x for x in self.bazi.jishen if x]
    
    def get_shen_type(self, wx: str) -> ShenType:
        """判斷五行屬於哪種神"""
        if wx == self.bazi.yongshen:
            return ShenType.YONGSHEN
        elif wx in self.bazi.xishen:
            return ShenType.XISHEN
        elif wx in self.bazi.jishen:
            return ShenType.JISHEN
        else:
            return ShenType.XIANSHEN
    
    def should_supplement(self, wx: str) -> Tuple[bool, str]:
        """判斷缺的五行是否要補"""
        shen_type = self.get_shen_type(wx)
        
        if shen_type == ShenType.YONGSHEN:
            return True, "必補！用神"
        elif shen_type == ShenType.XISHEN:
            return True, "要補！喜神"
        elif shen_type == ShenType.JISHEN:
            return False, "不補！忌神，缺了是福"
        else:
            return False, "可不補，閒神"
    
    def _analyze_stage(self):
        """分析人生階段"""
        age = self.age
        if age <= 16:
            self.stage = LifeStage(age, "童年", "地格", 2.0, 1.0, 0.5)
        elif age <= 32:
            self.stage = LifeStage(age, "青年", "地格+人格", 1.5, 1.5, 0.8)
        elif age <= 48:
            self.stage = LifeStage(age, "中年", "人格", 0.8, 2.0, 1.0)
        else:
            self.stage = LifeStage(age, "晚年", "總格", 0.5, 1.0, 2.0)
    
    # ────────────────────────────────────────────────────────────────
    # 步驟3：生成候選（DOE 多目標優化）
    # ────────────────────────────────────────────────────────────────
    
    def recommend(self, count: int = 20) -> List[NameCandidate]:
        """生成候選名字（Pareto 最優解集）"""
        self.candidates = []
        
        # 五行組合策略
        combos = self._get_wuxing_combos()
        
        # 筆畫組合
        strokes = self._get_best_strokes()
        
        # 生成候選
        for wx1, wx2, combo_type in combos:
            for s1, s2 in strokes:
                chars1 = get_chars(s1, wx1)
                chars2 = get_chars(s2, wx2)
                
                for c1 in chars1[:5]:
                    for c2 in chars2[:5]:
                        cand = self._create_candidate(c1, c2, combo_type)
                        if cand:
                            self.candidates.append(cand)
        
        # 去重並按 DOE 總分排序
        seen = set()
        unique = []
        for c in self.candidates:
            if c.full_name not in seen:
                seen.add(c.full_name)
                unique.append(c)
        
        unique.sort(key=lambda x: -x.doe.weighted_total)
        self.candidates = unique[:count]
        
        return self.candidates
    
    def _get_wuxing_combos(self) -> List[Tuple[str, str, str]]:
        """獲取五行組合策略"""
        combos = []
        yong = self.bazi.yongshen
        bu = self.bazi.bushen
        xi = self.bazi.xishen
        
        # 策略1：用神+補缺（最佳）
        for b in bu:
            combos.append((yong, b, "用神+補缺"))
            combos.append((b, yong, "補缺+用神"))
        
        # 策略2：用神+用神
        combos.append((yong, yong, "雙用神"))
        
        # 策略3：用神+喜神
        for x in xi:
            if x != yong and x not in bu:
                combos.append((yong, x, "用神+喜神"))
        
        return combos
    
    def _get_best_strokes(self) -> List[Tuple[int, int]]:
        """獲取最佳筆畫組合"""
        results = []
        xing = self.surname_info.get("stroke", 13)
        
        for s1 in range(8, 17):
            for s2 in range(8, 17):
                ren = xing + s1
                di = s1 + s2
                zong = xing + s1 + s2
                
                if ren in JI_SHU and di in JI_SHU and zong in JI_SHU:
                    # 加權評分
                    score = (
                        20 * self.stage.ren_weight +
                        20 * self.stage.di_weight +
                        20 * self.stage.zong_weight
                    )
                    results.append((s1, s2, score))
        
        results.sort(key=lambda x: (-x[2], x[0] + x[1]))
        return [(r[0], r[1]) for r in results[:25]]
    
    def _create_candidate(self, c1: CharInfo, c2: CharInfo, 
                          combo_type: str) -> Optional[NameCandidate]:
        """創建候選名字（含 DOE 評分）"""
        xing = self.surname_info.get("stroke", 13)
        xing_tone = self.surname_info.get("tone", 2)
        xing_pinyin = self.surname_info.get("pinyin", self.surname)
        xing_wx = self.surname_info.get("wuxing", "木")
        
        s1, s2 = c1.stroke, c2.stroke
        
        # 五格
        ren = xing + s1
        di = s1 + s2
        zong = xing + s1 + s2
        wai = zong - ren + 1
        
        if not (ren in JI_SHU and di in JI_SHU and zong in JI_SHU):
            return None
        
        # DOE 評分
        doe = DOEScore()
        
        # D1: 五格數理
        doe.wuge = 95 if (ren in JI_SHU and di in JI_SHU and zong in JI_SHU) else 60
        if wai not in JI_SHU:
            doe.wuge -= 5
        
        # D2: 用神配合
        match_yong = c1.wuxing == self.bazi.yongshen or c2.wuxing == self.bazi.yongshen
        doe.yongshen = 100 if match_yong else 70
        
        # D3: 補缺配合
        match_bu = c1.wuxing in self.bazi.bushen or c2.wuxing in self.bazi.bushen
        doe.bushen = 100 if match_bu else 70
        
        # D4: 避忌配合
        has_ji = c1.wuxing in self.bazi.jishen or c2.wuxing in self.bazi.jishen
        doe.avoid_ji = 60 if has_ji else 100
        
        # D5: 五格五行
        wuge_wx = [shuli_wuxing(ren), shuli_wuxing(di), shuli_wuxing(zong)]
        ji_in_wuge = any(wx in self.bazi.jishen for wx in wuge_wx)
        doe.wuge_wx = 80 if ji_in_wuge else 90
        
        # D6: 字義（主觀，給基準分）
        doe.meaning = 90 + hash(c1.char + c2.char) % 5
        
        # D7: 讀音
        doe.sound = self._calc_sound_score(xing_tone, c1.tone, c2.tone)
        
        # D8: 生肖配合（牛）
        shengxiao1 = calc_shengxiao_score(c1.char, c1)
        shengxiao2 = calc_shengxiao_score(c2.char, c2)
        doe.shengxiao = (shengxiao1 + shengxiao2) // 2
        
        # D9: 三才配置
        tian = xing + 1  # 天格（單姓）
        tian_wx = shuli_wuxing(tian)
        ren_wx = shuli_wuxing(ren)
        di_wx = shuli_wuxing(di)
        doe.sancai, _ = calc_sancai_score(tian_wx, ren_wx, di_wx)
        
        # D10: 書寫平衡
        struct1 = CHAR_STRUCTURE.get(c1.char, "左右")
        struct2 = CHAR_STRUCTURE.get(c2.char, "左右")
        doe.writing = calc_writing_score(xing, s1, s2, struct1, struct2)
        
        # D11: 獨特性
        doe.unique = calc_unique_score(c1.char, c2.char)
        
        # D12: 諧音禁忌
        pinyin_full = f"{xing_pinyin} {c1.pinyin} {c2.pinyin}"
        doe.xieyin = calc_xieyin_score(pinyin_full)
        
        # D13: 易經卦象
        doe.yijing = calc_yijing_score(xing, s1 + s2)
        
        # D14: 數字能量
        doe.numerology = calc_numerology_score(xing + s1 + s2)
        
        # D15: 五音歸元
        doe.wuyin = calc_wuyin_score(xing_pinyin, c1.pinyin, c2.pinyin)
        
        # 原始總分（15維度）
        doe.raw_total = (doe.wuge + doe.yongshen + doe.bushen + doe.avoid_ji + 
                         doe.wuge_wx + doe.meaning + doe.sound + doe.shengxiao + 
                         doe.sancai + doe.writing + doe.unique + doe.xieyin +
                         doe.yijing + doe.numerology + doe.wuyin)
        
        # 加權總分
        doe.weighted_total = (
            doe.wuge * DOE_WEIGHTS["wuge"] +
            doe.yongshen * DOE_WEIGHTS["yongshen"] +
            doe.bushen * DOE_WEIGHTS["bushen"] +
            doe.avoid_ji * DOE_WEIGHTS["avoid_ji"] +
            doe.wuge_wx * DOE_WEIGHTS["wuge_wx"] +
            doe.meaning * DOE_WEIGHTS["meaning"] +
            doe.sound * DOE_WEIGHTS["sound"] +
            doe.shengxiao * DOE_WEIGHTS["shengxiao"] +
            doe.sancai * DOE_WEIGHTS["sancai"] +
            doe.writing * DOE_WEIGHTS["writing"] +
            doe.unique * DOE_WEIGHTS["unique"] +
            doe.xieyin * DOE_WEIGHTS["xieyin"] +
            doe.yijing * DOE_WEIGHTS["yijing"] +
            doe.numerology * DOE_WEIGHTS["numerology"] +
            doe.wuyin * DOE_WEIGHTS["wuyin"]
        )
        
        # 五格描述
        ren_m = SHU_MEANING.get(ren, "")
        zong_m = SHU_MEANING.get(zong, "")
        wuge_desc = f"人{ren}吉{f'({ren_m})' if ren_m else ''} 地{di}吉 總{zong}吉{f'({zong_m})' if zong_m else ''}"
        
        # 配合描述
        match_parts = []
        if c1.wuxing == self.bazi.yongshen:
            match_parts.append(f"{c1.wuxing}(用神)")
        elif c1.wuxing in self.bazi.bushen:
            match_parts.append(f"{c1.wuxing}(補缺)")
        
        if c2.wuxing == self.bazi.yongshen:
            match_parts.append(f"{c2.wuxing}(用神)")
        elif c2.wuxing in self.bazi.bushen:
            match_parts.append(f"{c2.wuxing}(補缺)")
        
        # 意象
        imagery = self._get_imagery(c1, c2)
        
        # 拼音
        pinyin = f"{xing_pinyin.capitalize()} {c1.pinyin.capitalize()} {c2.pinyin.capitalize()}"
        
        return NameCandidate(
            full_name=f"{self.surname}{c1.char}{c2.char}",
            chars=[self.surname, c1.char, c2.char],
            strokes=[xing, s1, s2],
            wuxing=[xing_wx, c1.wuxing, c2.wuxing],
            pinyin=pinyin,
            tones=[xing_tone, c1.tone, c2.tone],
            ren_ge=ren, di_ge=di, zong_ge=zong, wai_ge=wai,
            wuge_desc=wuge_desc,
            match_yongshen=match_yong,
            match_bushen=match_bu,
            match_desc=" + ".join(match_parts),
            meaning=f"{c1.meaning} + {c2.meaning}",
            imagery=imagery,
            doe=doe,
            recommendation=combo_type
        )
    
    def _calc_sound_score(self, t1: int, t2: int, t3: int) -> int:
        """計算讀音分數"""
        score = 85
        
        # 聲調變化
        tones = [t1, t2, t3]
        
        # 最佳：有去聲收尾（頓挫）
        if t3 == 4:
            score += 5
        
        # 避免三連同調
        if t1 == t2 == t3:
            score -= 10
        
        # 抑揚頓挫加分
        if len(set(tones)) == 3:
            score += 5
        
        return min(100, max(70, score))
    
    def _get_imagery(self, c1: CharInfo, c2: CharInfo) -> str:
        """獲取意象描述"""
        if c1.wuxing == "水" and c2.wuxing == "火":
            if "淳" in c1.char:
                return "清泉映朝陽，純淨而明亮"
            elif "涵" in c1.char:
                return "深潭藏烈火，內斂而閃耀"
            elif "清" in c1.char:
                return "清流映晨曦，高潔而光明"
            else:
                return "水火既濟，陰陽調和"
        elif c1.wuxing == "水" and c2.wuxing == "水":
            return "雙水流動，智慧通達"
        elif c1.wuxing == "水" and c2.wuxing == "木":
            return "水木相生，生機盎然"
        else:
            return "五行調和"
    
    # ────────────────────────────────────────────────────────────────
    # 輸出報告
    # ────────────────────────────────────────────────────────────────
    
    def print_analysis(self):
        """輸出分析報告"""
        print("═" * 65)
        print("【系統分析報告】")
        print("═" * 65)
        
        b = self.bazi
        s = self.stage
        
        print(f"""
┌{'─'*63}┐
│  姓氏：{self.surname}（{self.surname_info.get('stroke')}畫，{self.surname_info.get('wuxing')}）
│  四柱：{' '.join(self.pillars)}
│  年齡：{self.age}歲（{s.name}）
└{'─'*63}┘

【八字分析】
  日主：{b.day_master}（{b.day_wx}）
  身強：{'是' if b.is_strong else '否'}（{b.strength_score}分）

【五行統計】""")
        
        for wx in ["木", "火", "土", "金", "水"]:
            c = b.wx_count.get(wx, 0)
            bar = "█" * int(c) + "░" * (5 - int(c))
            mark = " ← 缺！" if c == 0 else ""
            print(f"  {wx}：{bar} ({c}){mark}")
        
        print(f"""
【四神配置】
  用神：{b.yongshen} ← 最需要
  喜神：{b.xishen}
  忌神：{b.jishen} ← 要避開
  閒神：{b.xianshen}
  補神：{b.bushen if b.bushen else '無'} {'← 缺失要補！' if b.bushen else ''}

【缺五行判斷】""")
        
        for wx in b.missing:
            should, reason = self.should_supplement(wx)
            print(f"  缺{wx}：{reason}")
        
        print(f"""
【人生階段】
  階段：{s.name}（{s.age}歲）
  重點：{s.priority}
""")
    
    def print_candidates(self, top_n: int = 10):
        """輸出候選名字（DOE 排名）"""
        print("═" * 65)
        print("【候選名字】Pareto 最優解集")
        print("═" * 65)
        
        print(f"\n共 {len(self.candidates)} 個候選，按 DOE 總分排序：\n")
        
        for i, c in enumerate(self.candidates[:top_n], 1):
            star = "🏆" if c.match_yongshen and c.match_bushen else "  "
            print(f"{star}【{i:2}】{c.full_name}  （{c.doe.total}分）")
            print(f"      拼音：{c.pinyin}  聲調：{'-'.join(map(str, c.tones))}")
            print(f"      五行：{'+'.join(c.wuxing)}")
            print(f"      五格：{c.wuge_desc}")
            print(f"      字義：{c.meaning}")
            print(f"      意象：{c.imagery}")
            print(f"      配合：{c.match_desc}")
            print(f"      策略：{c.recommendation}")
            print()
        
        print("─" * 65)
        print("🏆 = 用神+補缺 最佳組合")
        print("─" * 65)
    
    def get_doe_comparison(self, names: List[str]) -> str:
        """獲取指定名字的 DOE 對比（15維度 + 加權）"""
        lines = []
        lines.append("═" * 100)
        lines.append("【DOE 對比分析（15維度 + 加權）】")
        lines.append("═" * 100)
        
        target = [c for c in self.candidates if c.full_name in names]
        
        if not target:
            return "未找到指定名字"
        
        # 簡化顯示：分兩行
        lines.append("\n  【命理層 + 語言層】")
        lines.append("  ┌──────────┬──────┬──────┬──────┬──────┬──────┬──────┬──────┐")
        lines.append("  │  名字    │ D1   │ D2   │ D3   │ D4   │ D5   │ D6   │ D7   │")
        lines.append("  │          │ 五格 │ 用神 │ 補缺 │ 避忌 │ 格行 │ 字義 │ 讀音 │")
        lines.append("  ├──────────┼──────┼──────┼──────┼──────┼──────┼──────┼──────┤")
        
        for c in sorted(target, key=lambda x: -x.doe.weighted_total):
            d = c.doe
            lines.append(f"  │  {c.full_name}  │  {d.wuge} │ {d.yongshen} │ {d.bushen} │ {d.avoid_ji} │  {d.wuge_wx} │  {d.meaning} │  {d.sound} │")
        
        lines.append("  └──────────┴──────┴──────┴──────┴──────┴──────┴──────┴──────┘")
        
        lines.append("\n  【傳統層 + 實用層 + 玄學層】")
        lines.append("  ┌──────────┬──────┬──────┬──────┬──────┬──────┬──────┬──────┬──────┬──────────┐")
        lines.append("  │  名字    │ D8   │ D9   │ D10  │ D11  │ D12  │ D13  │ D14  │ D15  │ 加權總分 │")
        lines.append("  │          │ 生肖 │ 三才 │ 書寫 │ 獨特 │ 諧音 │ 易卦 │ 靈數 │ 五音 │          │")
        lines.append("  ├──────────┼──────┼──────┼──────┼──────┼──────┼──────┼──────┼──────┼──────────┤")
        
        for c in sorted(target, key=lambda x: -x.doe.weighted_total):
            d = c.doe
            lines.append(f"  │  {c.full_name}  │  {d.shengxiao} │  {d.sancai} │  {d.writing} │  {d.unique} │ {d.xieyin} │  {d.yijing} │  {d.numerology} │  {d.wuyin} │  {d.weighted_total:6.1f}  │")
        
        lines.append("  └──────────┴──────┴──────┴──────┴──────┴──────┴──────┴──────┴──────┴──────────┘")
        
        lines.append("\n  權重：D2-D4=1.5 | D1,D6,D8=1.2 | D5,D7,D9,D12=1.0 | D10,D11=0.8 | D13-D15=0.5")
        
        return "\n".join(lines)


# ════════════════════════════════════════════════════════════════════
# L4: 便捷函數
# ════════════════════════════════════════════════════════════════════

def analyze_and_recommend(
    surname: str,
    year: str, month: str, day: str, hour: str,
    age: int,
    count: int = 20
) -> Tuple[NamingMaster, List[NameCandidate]]:
    """
    一站式分析並推薦
    
    範例：
        master, candidates = analyze_and_recommend(
            surname="楊",
            year="癸丑", month="癸丑", day="庚子", hour="乙酉",
            age=52
        )
        master.print_analysis()
        master.print_candidates(10)
    """
    master = NamingMaster()
    master.set_input(surname, year, month, day, hour, age)
    master.analyze()
    candidates = master.recommend(count)
    return master, candidates


# ════════════════════════════════════════════════════════════════════
# 測試
# ════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("═" * 70)
    print("        北斗命數取名決策系統 - 測試")
    print("        案例：楊三興 1973/12/30 17:00 52歲")
    print("═" * 70)
    
    # 執行
    master, candidates = analyze_and_recommend(
        surname="楊",
        year="癸丑", month="癸丑", day="庚子", hour="乙酉",
        age=52,
        count=20
    )
    
    # 輸出分析
    master.print_analysis()
    
    # 輸出候選
    master.print_candidates(10)
    
    # DOE 對比
    print(master.get_doe_comparison(["楊淳熙", "楊涵煜", "楊清熙"]))
    
    # 最終決策
    print("""
╔═════════════════════════════════════════════════════════════════════╗
║                                                                     ║
║  最終決策：                                                         ║
║                                                                     ║
║    楊淳熙 — 日常・公務（溫潤面）                                    ║
║    楊涵煜 — 創業・筆名（內斂面）                                    ║
║                                                                     ║
║  同一場，兩種表達                                                   ║
║                                                                     ║
╚═════════════════════════════════════════════════════════════════════╝
    """)
    
    print("═" * 70)
    print("核心原則：系統分析 → 多項推薦 → 用戶自選")
    print("═" * 70)
