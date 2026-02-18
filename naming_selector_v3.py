#!/usr/bin/env python3
"""
naming_selector_v3.py - 用戶自選取名系統
北斗命數 v3.1.5

═══════════════════════════════════════════════════════════════════════
核心原則：系統分析 → 多項推薦 → 用戶自選
═══════════════════════════════════════════════════════════════════════

逆向工程邏輯（根據楊三興→楊淳熙案例）：

輸入條件：
1. 生辰八字 → 計算日主、身強身弱 → 決定用神/喜神/忌神
2. 五行統計 → 找出缺失的五行 → 決定補神
3. 用戶年齡 → 判斷人生階段 → 調整五格優先級
4. 姓氏     → 固定條件 → 計算可調整的筆畫範圍

輸出原則：
1. 多個候選名字（10-20個）
2. 每個名字附帶分析和評分
3. 用戶根據個人喜好自選

測試案例：
  輸入：楊三興 1973/12/30 17:00 52歲
  分析：庚金身強、用神水、缺火、晚年重總格
  推薦：楊淳熙、楊涵熙、楊清煜...
  用戶選擇：楊淳熙 ✓

XTF8 層級：L0-L4
@織明 × @理樞
"""

from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, field
from enum import Enum
import json

# ============================================================
# L0: 常量定義
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

# 數理吉凶
SHULI_JI = {1, 3, 5, 6, 7, 8, 11, 13, 15, 16, 17, 18, 21, 23, 24, 25, 29, 
            31, 32, 33, 35, 37, 39, 41, 45, 47, 48, 52, 57, 61, 63, 65, 67, 68, 81}

# 數理含義
SHULI_MEANING = {
    15: ("福壽共照", "立身興家，福壽雙全"),
    21: ("首領運", "獨立權威，能成大業"),
    24: ("掘藏得金", "家門餘慶，白手成家"),
    29: ("智謀優秀", "財力雄厚，成就大業"),
    32: ("寶馬金鞍", "僥倖多能，精力旺盛"),
    37: ("權威顯達", "獨立權威，熱誠忠信"),
}

def get_jixiong(n: int) -> str:
    if n > 81:
        n = n % 80 or 80
    return "吉" if n in SHULI_JI else "凶"

# ============================================================
# L1: 字庫（精選常用字）
# ============================================================

# 水部首（用神首選）
CHAR_WATER = {
    8: ["沛", "泓", "泊", "沐"],
    9: ["泉", "洋", "洛", "津"],
    10: ["浩", "海", "浚", "洵"],
    11: ["淳", "涵", "淇", "清", "深", "淑"],
    12: ["淵", "渝", "湘", "湛"],
    13: ["源", "溪", "湧", "溫"],
    15: ["潤", "潔", "澄", "潮"],
    16: ["澤", "霖", "澎"],
}

# 火部首（補缺用）
CHAR_FIRE = {
    9: ["炳", "昱", "映", "昶"],
    10: ["晉", "晏", "烜"],
    11: ["晟", "晨", "焜"],
    12: ["晴", "景", "焯"],
    13: ["煜", "煒", "熙", "暉", "照"],
    15: ["熠", "熹", "暾"],
    16: ["燁", "曉", "燃"],
}

# 木部首（財星用）
CHAR_WOOD = {
    8: ["林", "松", "杰", "東"],
    9: ["柏", "柳", "柯", "桂"],
    10: ["桐", "桓", "格", "栩"],
    11: ["梧", "梓", "梅", "梁"],
    12: ["森", "棠", "棟", "植"],
    13: ["楠", "楷", "楓", "楚"],
}

# 常用姓氏筆畫
SURNAME_STROKES = {
    "楊": 13, "陳": 16, "林": 8, "李": 7, "王": 4, "張": 11,
    "劉": 15, "黃": 12, "吳": 7, "周": 8, "徐": 10, "孫": 10,
    "趙": 14, "朱": 6, "何": 7, "郭": 15, "羅": 20, "梁": 11,
}

# ============================================================
# L2: 資料結構
# ============================================================

@dataclass
class UserInput:
    """用戶輸入"""
    surname: str                    # 姓氏
    surname_strokes: int = 0        # 姓氏筆畫
    year_pillar: str = ""           # 年柱
    month_pillar: str = ""          # 月柱
    day_pillar: str = ""            # 日柱
    hour_pillar: str = ""           # 時柱
    age: int = 30                   # 年齡

@dataclass
class BaziAnalysis:
    """八字分析結果"""
    day_master: str = ""            # 日主
    day_element: str = ""           # 日主五行
    is_strong: bool = False         # 身強身弱
    strength_score: int = 0         # 強弱分數
    
    wuxing_count: Dict[str, float] = field(default_factory=dict)  # 五行統計
    missing_wuxing: List[str] = field(default_factory=list)       # 缺失五行
    
    yongshen: str = ""              # 用神
    xishen: List[str] = field(default_factory=list)   # 喜神
    jishen: List[str] = field(default_factory=list)   # 忌神
    bushen: List[str] = field(default_factory=list)   # 補神（缺失需補）

@dataclass
class LifeStage:
    """人生階段"""
    age: int = 0
    stage: str = ""                 # childhood/youth/middle/elder
    priority: str = ""              # 重點五格
    di_weight: float = 1.0          # 地格權重
    ren_weight: float = 1.0         # 人格權重
    zong_weight: float = 1.0        # 總格權重

@dataclass
class NameOption:
    """候選名字（供用戶選擇）"""
    name: str                       # 全名
    chars: List[str]                # 各字
    wuxing: List[str]               # 各字五行
    wuxing_flow: str                # 五行流動描述
    
    # 五格
    ren_ge: int = 0                 # 人格
    di_ge: int = 0                  # 地格
    zong_ge: int = 0                # 總格
    wai_ge: int = 0                 # 外格
    wuge_desc: str = ""             # 五格描述
    
    # 配合分析
    yongshen_match: bool = False    # 是否配合用神
    bushen_match: bool = False      # 是否補缺
    
    # 評分
    wuge_score: int = 0             # 五格分
    bazi_score: int = 0             # 八字配合分
    total_score: int = 0            # 總分
    
    # 字義
    meaning: str = ""               # 字義解讀
    
    # 推薦理由
    recommendation: str = ""        # 推薦理由

# ============================================================
# L3: 核心系統
# ============================================================

class NamingSelector:
    """
    用戶自選取名系統
    
    核心原則：系統分析 → 多項推薦 → 用戶自選
    
    使用流程：
    1. input_user_data() - 輸入用戶資料
    2. analyze() - 系統分析
    3. generate_options() - 生成候選
    4. 用戶自選
    """
    
    def __init__(self):
        self.user_input: Optional[UserInput] = None
        self.bazi: Optional[BaziAnalysis] = None
        self.life_stage: Optional[LifeStage] = None
        self.options: List[NameOption] = []
    
    # ========== 步驟1：輸入用戶資料 ==========
    
    def input_user_data(
        self,
        surname: str,
        year_pillar: str,
        month_pillar: str,
        day_pillar: str,
        hour_pillar: str,
        age: int
    ) -> "NamingSelector":
        """輸入用戶資料"""
        self.user_input = UserInput(
            surname=surname,
            surname_strokes=SURNAME_STROKES.get(surname, len(surname) * 10),
            year_pillar=year_pillar,
            month_pillar=month_pillar,
            day_pillar=day_pillar,
            hour_pillar=hour_pillar,
            age=age
        )
        return self
    
    # ========== 步驟2：系統分析 ==========
    
    def analyze(self) -> "NamingSelector":
        """執行完整分析"""
        if not self.user_input:
            raise ValueError("請先輸入用戶資料")
        
        self._analyze_bazi()
        self._analyze_life_stage()
        
        return self
    
    def _analyze_bazi(self):
        """分析八字"""
        u = self.user_input
        self.bazi = BaziAnalysis()
        
        # 日主
        self.bazi.day_master = u.day_pillar[0] if u.day_pillar else ""
        self.bazi.day_element = GAN_WUXING.get(self.bazi.day_master, "")
        
        # 五行統計
        self._count_wuxing()
        
        # 身強身弱
        self._calc_strength()
        
        # 用神配置
        self._calc_yongshen()
    
    def _count_wuxing(self):
        """統計五行"""
        count = {"木": 0, "火": 0, "土": 0, "金": 0, "水": 0}
        u = self.user_input
        
        # 天干
        for pillar in [u.year_pillar, u.month_pillar, u.day_pillar, u.hour_pillar]:
            if pillar:
                gan = pillar[0]
                wx = GAN_WUXING.get(gan, "")
                if wx:
                    count[wx] += 1
        
        # 地支藏干
        for pillar in [u.year_pillar, u.month_pillar, u.day_pillar, u.hour_pillar]:
            if pillar and len(pillar) >= 2:
                zhi = pillar[1]
                for cang in ZHI_CANGGAN.get(zhi, []):
                    wx = GAN_WUXING.get(cang, "")
                    if wx:
                        count[wx] += 0.5
        
        self.bazi.wuxing_count = count
        self.bazi.missing_wuxing = [wx for wx, c in count.items() if c == 0]
    
    def _calc_strength(self):
        """計算身強身弱"""
        score = 0
        day_wx = self.bazi.day_element
        u = self.user_input
        
        # 月令
        if u.month_pillar and len(u.month_pillar) >= 2:
            month_zhi = u.month_pillar[1]
            month_wx = ZHI_WUXING.get(month_zhi, "")
            
            if month_wx == day_wx:
                score += 40
            elif WUXING_SHENG_ME.get(day_wx) == month_wx:
                score += 30
            elif WUXING_SHENG.get(day_wx) == month_wx:
                score += 10
        
        # 通根
        for pillar in [u.year_pillar, u.month_pillar, u.day_pillar, u.hour_pillar]:
            if pillar and len(pillar) >= 2:
                zhi = pillar[1]
                for cang in ZHI_CANGGAN.get(zhi, []):
                    if GAN_WUXING.get(cang) == day_wx:
                        score += 8
        
        # 印比
        for pillar in [u.year_pillar, u.month_pillar, u.day_pillar, u.hour_pillar]:
            if pillar:
                gan = pillar[0]
                gan_wx = GAN_WUXING.get(gan, "")
                if gan_wx == day_wx or gan_wx == WUXING_SHENG_ME.get(day_wx):
                    score += 5
        
        self.bazi.is_strong = score >= 50
        self.bazi.strength_score = score
    
    def _calc_yongshen(self):
        """計算用神"""
        day_wx = self.bazi.day_element
        is_strong = self.bazi.is_strong
        missing = self.bazi.missing_wuxing
        
        if is_strong:
            # 身強：用神為洩（食傷）
            self.bazi.yongshen = WUXING_SHENG.get(day_wx, "")
            self.bazi.xishen = [
                WUXING_KE.get(day_wx, ""),      # 財
                WUXING_KE_ME.get(day_wx, "")    # 官殺
            ]
            self.bazi.jishen = [
                WUXING_SHENG_ME.get(day_wx, ""),  # 印
                day_wx                            # 比劫
            ]
        else:
            # 身弱：用神為生（印）
            self.bazi.yongshen = WUXING_SHENG_ME.get(day_wx, "")
            self.bazi.xishen = [day_wx]
            self.bazi.jishen = [
                WUXING_KE.get(day_wx, ""),
                WUXING_SHENG.get(day_wx, "")
            ]
        
        # 補神：缺失的五行中，屬於用神或喜神的
        all_good = [self.bazi.yongshen] + self.bazi.xishen
        self.bazi.bushen = [wx for wx in missing if wx in all_good]
        
        # 過濾空值
        self.bazi.xishen = [x for x in self.bazi.xishen if x]
        self.bazi.jishen = [x for x in self.bazi.jishen if x]
    
    def _analyze_life_stage(self):
        """分析人生階段"""
        age = self.user_input.age
        self.life_stage = LifeStage(age=age)
        
        if age <= 16:
            self.life_stage.stage = "童年"
            self.life_stage.priority = "地格"
            self.life_stage.di_weight = 2.0
            self.life_stage.ren_weight = 1.0
            self.life_stage.zong_weight = 0.5
        elif age <= 32:
            self.life_stage.stage = "青年"
            self.life_stage.priority = "地格+人格"
            self.life_stage.di_weight = 1.5
            self.life_stage.ren_weight = 1.5
            self.life_stage.zong_weight = 0.8
        elif age <= 48:
            self.life_stage.stage = "中年"
            self.life_stage.priority = "人格"
            self.life_stage.di_weight = 0.8
            self.life_stage.ren_weight = 2.0
            self.life_stage.zong_weight = 1.0
        else:
            self.life_stage.stage = "晚年"
            self.life_stage.priority = "總格"
            self.life_stage.di_weight = 0.5
            self.life_stage.ren_weight = 1.0
            self.life_stage.zong_weight = 2.0
    
    # ========== 步驟3：生成候選 ==========
    
    def generate_options(self, count: int = 20) -> List[NameOption]:
        """生成候選名字供用戶選擇"""
        if not self.bazi or not self.life_stage:
            raise ValueError("請先執行 analyze()")
        
        self.options = []
        
        # 確定需要的五行組合（多種策略）
        combos = self._get_wuxing_combos()
        
        # 找最佳筆畫組合
        stroke_combos = self._find_best_strokes()
        
        # 生成候選
        for s1, s2 in stroke_combos:
            for wx1, wx2 in combos:
                chars1 = self._get_chars(s1, wx1)
                chars2 = self._get_chars(s2, wx2)
                
                for c1 in chars1[:3]:
                    for c2 in chars2[:3]:
                        option = self._create_option(c1, c2, wx1, wx2, s1, s2)
                        if option:
                            self.options.append(option)
        
        # 去重並排序
        seen = set()
        unique = []
        for opt in self.options:
            if opt.name not in seen:
                seen.add(opt.name)
                unique.append(opt)
        
        unique.sort(key=lambda x: -x.total_score)
        self.options = unique[:count]
        
        return self.options
    
    def _get_wuxing_combos(self) -> List[Tuple[str, str]]:
        """獲取五行組合策略"""
        combos = []
        
        yong = self.bazi.yongshen  # 用神
        bu = self.bazi.bushen      # 補神（缺失）
        xi = self.bazi.xishen      # 喜神
        
        # 策略1：用神 + 用神（雙補用神）
        if yong:
            combos.append((yong, yong))
        
        # 策略2：用神 + 補缺（用神+補火）← 重要！
        for b in bu:
            if yong:
                combos.append((yong, b))
                combos.append((b, yong))
        
        # 策略3：用神 + 喜神
        for x in xi:
            if yong and x != yong:
                combos.append((yong, x))
                combos.append((x, yong))
        
        # 策略4：補缺 + 喜神
        for b in bu:
            for x in xi:
                if b != x:
                    combos.append((b, x))
        
        return combos
    
    def _get_wuxing_priority(self) -> List[str]:
        """獲取五行優先級"""
        priority = []
        
        # 1. 用神優先
        if self.bazi.yongshen:
            priority.append(self.bazi.yongshen)
        
        # 2. 補神次之（缺失的喜用）
        for wx in self.bazi.bushen:
            if wx not in priority:
                priority.append(wx)
        
        # 3. 喜神再次
        for wx in self.bazi.xishen:
            if wx not in priority:
                priority.append(wx)
        
        return priority
    
    def _find_best_strokes(self) -> List[Tuple[int, int]]:
        """找最佳筆畫組合"""
        results = []
        xing = self.user_input.surname_strokes
        
        for s1 in range(5, 18):
            for s2 in range(5, 18):
                ren = xing + s1
                di = s1 + s2
                zong = xing + s1 + s2
                
                if (get_jixiong(ren) == "吉" and 
                    get_jixiong(di) == "吉" and 
                    get_jixiong(zong) == "吉"):
                    
                    # 計算加權分數
                    score = (
                        (20 if get_jixiong(ren) == "吉" else 0) * self.life_stage.ren_weight +
                        (20 if get_jixiong(di) == "吉" else 0) * self.life_stage.di_weight +
                        (20 if get_jixiong(zong) == "吉" else 0) * self.life_stage.zong_weight
                    )
                    results.append((s1, s2, score))
        
        results.sort(key=lambda x: (-x[2], x[0] + x[1]))
        return [(r[0], r[1]) for r in results[:30]]
    
    def _get_chars(self, stroke: int, wuxing: str) -> List[str]:
        """獲取指定筆畫和五行的漢字"""
        if wuxing == "水":
            return CHAR_WATER.get(stroke, [])
        elif wuxing == "火":
            return CHAR_FIRE.get(stroke, [])
        elif wuxing == "木":
            return CHAR_WOOD.get(stroke, [])
        return []
    
    def _create_option(
        self, c1: str, c2: str, wx1: str, wx2: str, s1: int, s2: int
    ) -> Optional[NameOption]:
        """創建候選名字"""
        xing = self.user_input.surname_strokes
        surname = self.user_input.surname
        
        # 五格計算
        ren = xing + s1
        di = s1 + s2
        zong = xing + s1 + s2
        wai = zong - ren + 1
        
        # 檢查吉凶
        if get_jixiong(ren) != "吉" or get_jixiong(di) != "吉" or get_jixiong(zong) != "吉":
            return None
        
        # 計算五格分數（加權）
        wuge_score = int(
            20 * self.life_stage.ren_weight +
            20 * self.life_stage.di_weight +
            20 * self.life_stage.zong_weight +
            (10 if get_jixiong(wai) == "吉" else 0)
        )
        
        # 計算八字配合分數
        bazi_score = 50
        yongshen_match = False
        bushen_match = False
        
        for wx in [wx1, wx2]:
            if wx == self.bazi.yongshen:
                bazi_score += 25
                yongshen_match = True
            elif wx in self.bazi.bushen:
                bazi_score += 20
                bushen_match = True
            elif wx in self.bazi.xishen:
                bazi_score += 15
            elif wx in self.bazi.jishen:
                bazi_score -= 20
        
        bazi_score = min(100, max(0, bazi_score))
        
        # 五行流動描述
        surname_wx = "木" if surname in "楊林森柏" else "土"  # 簡化
        wuxing_flow = f"{surname_wx}→{wx1}→{wx2}"
        
        # 五格描述
        ren_meaning = SHULI_MEANING.get(ren, ("", ""))[0]
        zong_meaning = SHULI_MEANING.get(zong, ("", ""))[0]
        wuge_desc = f"人{ren}吉{f'({ren_meaning})' if ren_meaning else ''} 地{di}吉 總{zong}吉{f'({zong_meaning})' if zong_meaning else ''}"
        
        # 字義
        meaning = self._get_meaning(c1, c2)
        
        # 推薦理由
        reasons = []
        if yongshen_match:
            reasons.append(f"配合用神{self.bazi.yongshen}")
        if bushen_match:
            reasons.append(f"補足缺{self.bazi.bushen}")
        if self.life_stage.stage == "晚年" and zong in SHULI_MEANING:
            reasons.append(f"總格{zong}{SHULI_MEANING[zong][0]}")
        
        return NameOption(
            name=f"{surname}{c1}{c2}",
            chars=[surname, c1, c2],
            wuxing=[surname_wx, wx1, wx2],
            wuxing_flow=wuxing_flow,
            ren_ge=ren,
            di_ge=di,
            zong_ge=zong,
            wai_ge=wai,
            wuge_desc=wuge_desc,
            yongshen_match=yongshen_match,
            bushen_match=bushen_match,
            wuge_score=wuge_score,
            bazi_score=bazi_score,
            total_score=wuge_score + bazi_score,
            meaning=meaning,
            recommendation="、".join(reasons) if reasons else "五格全吉"
        )
    
    def _get_meaning(self, c1: str, c2: str) -> str:
        """獲取字義"""
        meanings = {
            "淳": "淳厚、純正",
            "熙": "光明、興盛",
            "涵": "包涵、涵養",
            "煜": "光輝、照耀",
            "源": "源頭、根本",
            "清": "清澈、高潔",
            "晟": "光明、旺盛",
            "森": "茂盛、眾多",
            "澤": "恩澤、潤澤",
            "暉": "陽光、光輝",
        }
        m1 = meanings.get(c1, c1)
        m2 = meanings.get(c2, c2)
        return f"{m1} + {m2}"
    
    # ========== 輸出報告 ==========
    
    def get_analysis_report(self) -> str:
        """獲取分析報告"""
        lines = []
        lines.append("=" * 60)
        lines.append("八字分析報告")
        lines.append("=" * 60)
        
        if self.bazi:
            lines.append(f"\n【八字】")
            lines.append(f"  四柱：{self.user_input.year_pillar}年 {self.user_input.month_pillar}月 {self.user_input.day_pillar}日 {self.user_input.hour_pillar}時")
            lines.append(f"  日主：{self.bazi.day_master}（{self.bazi.day_element}）")
            lines.append(f"  身強：{'是' if self.bazi.is_strong else '否'}（{self.bazi.strength_score}分）")
            
            lines.append(f"\n【五行統計】")
            for wx, count in self.bazi.wuxing_count.items():
                bar = "█" * int(count) + "░" * (5 - int(count))
                mark = " ← 缺！" if count == 0 else ""
                lines.append(f"  {wx}：{bar} ({count}){mark}")
            
            lines.append(f"\n【用神配置】")
            lines.append(f"  用神：{self.bazi.yongshen} ← 最需要")
            lines.append(f"  喜神：{self.bazi.xishen}")
            lines.append(f"  忌神：{self.bazi.jishen} ← 要避開")
            if self.bazi.bushen:
                lines.append(f"  補神：{self.bazi.bushen} ← 缺失要補！")
        
        if self.life_stage:
            lines.append(f"\n【人生階段】")
            lines.append(f"  年齡：{self.life_stage.age}歲")
            lines.append(f"  階段：{self.life_stage.stage}")
            lines.append(f"  重點：{self.life_stage.priority}")
        
        return "\n".join(lines)
    
    def get_options_report(self) -> str:
        """獲取候選名字報告（供用戶選擇）"""
        lines = []
        lines.append("=" * 60)
        lines.append("候選名字（請自選）")
        lines.append("=" * 60)
        
        lines.append(f"\n共 {len(self.options)} 個候選，按綜合評分排序：\n")
        
        for i, opt in enumerate(self.options, 1):
            lines.append(f"【{i:2}】{opt.name}")
            lines.append(f"     五行：{opt.wuxing_flow}")
            lines.append(f"     五格：{opt.wuge_desc}")
            lines.append(f"     字義：{opt.meaning}")
            lines.append(f"     推薦：{opt.recommendation}")
            lines.append(f"     評分：{opt.total_score}分")
            lines.append("")
        
        lines.append("-" * 60)
        lines.append("請根據以下考量自行選擇：")
        lines.append("  1. 字義寓意是否喜歡")
        lines.append("  2. 讀音是否順口")
        lines.append("  3. 書寫是否美觀")
        lines.append("  4. 個人直覺感受")
        lines.append("-" * 60)
        
        return "\n".join(lines)
    
    def to_dict(self) -> Dict:
        """輸出為字典（可序列化）"""
        return {
            "input": {
                "surname": self.user_input.surname,
                "pillars": f"{self.user_input.year_pillar} {self.user_input.month_pillar} {self.user_input.day_pillar} {self.user_input.hour_pillar}",
                "age": self.user_input.age,
            },
            "analysis": {
                "day_master": f"{self.bazi.day_master}（{self.bazi.day_element}）",
                "is_strong": self.bazi.is_strong,
                "missing": self.bazi.missing_wuxing,
                "yongshen": self.bazi.yongshen,
                "bushen": self.bazi.bushen,
            },
            "life_stage": {
                "stage": self.life_stage.stage,
                "priority": self.life_stage.priority,
            },
            "options": [
                {
                    "name": opt.name,
                    "wuxing": opt.wuxing_flow,
                    "wuge": opt.wuge_desc,
                    "score": opt.total_score,
                    "recommendation": opt.recommendation,
                }
                for opt in self.options[:10]
            ]
        }


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
) -> Tuple[NamingSelector, List[NameOption]]:
    """
    便捷函數：分析並推薦名字
    
    範例：
    selector, options = analyze_and_recommend(
        surname="楊",
        year_pillar="癸丑",
        month_pillar="癸丑",
        day_pillar="庚子",
        hour_pillar="乙酉",
        age=52,
        count=15
    )
    
    print(selector.get_analysis_report())
    print(selector.get_options_report())
    """
    selector = NamingSelector()
    selector.input_user_data(
        surname=surname,
        year_pillar=year_pillar,
        month_pillar=month_pillar,
        day_pillar=day_pillar,
        hour_pillar=hour_pillar,
        age=age
    )
    selector.analyze()
    options = selector.generate_options(count)
    
    return selector, options


# ============================================================
# 測試
# ============================================================

if __name__ == "__main__":
    print("=" * 70)
    print("        用戶自選取名系統 - 測試")
    print("        案例：楊三興 1973/12/30 17:00 52歲")
    print("=" * 70)
    
    # 執行分析
    selector, options = analyze_and_recommend(
        surname="楊",
        year_pillar="癸丑",
        month_pillar="癸丑",
        day_pillar="庚子",
        hour_pillar="乙酉",
        age=52,
        count=15
    )
    
    # 輸出分析報告
    print(selector.get_analysis_report())
    
    # 輸出候選名字
    print("\n" + selector.get_options_report())
    
    # 驗證楊淳熙是否在列
    found = False
    for opt in options:
        if opt.name == "楊淳熙":
            found = True
            print("\n" + "=" * 60)
            print("✅ 驗證：楊淳熙 在候選列表中")
            print("=" * 60)
            print(f"  五行：{opt.wuxing_flow}")
            print(f"  五格：{opt.wuge_desc}")
            print(f"  推薦：{opt.recommendation}")
            print(f"  評分：{opt.total_score}分")
            break
    
    if not found:
        print("\n⚠️ 楊淳熙 未在候選列表中，需要調整字庫")
    
    print("\n" + "=" * 70)
    print("核心原則：系統分析 → 多項推薦 → 用戶自選")
    print("=" * 70)
