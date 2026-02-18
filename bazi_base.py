#!/usr/bin/env python3
"""
bazi_base.py - 八字分析共用基礎模組
版本：v1.0.0

═══════════════════════════════════════════════════════════════════════
XTF8 八層結構：
  L0: 常量（天干地支五行、十神、神煞）
  L1: 基礎計算（干支轉換、五行計算、十神計算）
  L2: 資料結構（BaziPillar, BaziChart, ShenXi）
  L3: 核心類（BaziAnalyzer, HeHunAnalyzer）
  L4: 便捷函數

消-拓-融：
  消：從 naming_master.py 提取八字邏輯
  拓：擴展完整八字分析（四柱排盤、用神喜忌、合婚）
  融：整合到取名、擇日系統
═══════════════════════════════════════════════════════════════════════

@11星協作：@織明 代碼 | @理樞 分析 | @澄書 記錄 | @星殼 架構

PYLIB 依賴：無（獨立模組）
XTF8 層級：L0-L4
"""

from typing import Dict, List, Tuple, Optional, Set
from dataclasses import dataclass, field
from enum import Enum

# ════════════════════════════════════════════════════════════════════
# L0: 常量定義
# ════════════════════════════════════════════════════════════════════

# 天干
TIANGAN = ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"]
TIANGAN_IDX = {g: i for i, g in enumerate(TIANGAN)}

# 天干五行
TIANGAN_WX = {
    "甲": "木", "乙": "木", "丙": "火", "丁": "火", "戊": "土",
    "己": "土", "庚": "金", "辛": "金", "壬": "水", "癸": "水"
}

# 天干陰陽
TIANGAN_YY = {
    "甲": "陽", "乙": "陰", "丙": "陽", "丁": "陰", "戊": "陽",
    "己": "陰", "庚": "陽", "辛": "陰", "壬": "陽", "癸": "陰"
}

# 地支
DIZHI = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]
DIZHI_IDX = {z: i for i, z in enumerate(DIZHI)}

# 地支五行
DIZHI_WX = {
    "子": "水", "丑": "土", "寅": "木", "卯": "木", "辰": "土", "巳": "火",
    "午": "火", "未": "土", "申": "金", "酉": "金", "戌": "土", "亥": "水"
}

# 地支陰陽
DIZHI_YY = {
    "子": "陽", "丑": "陰", "寅": "陽", "卯": "陰", "辰": "陽", "巳": "陰",
    "午": "陽", "未": "陰", "申": "陽", "酉": "陰", "戌": "陽", "亥": "陰"
}

# 地支藏干
DIZHI_CANGGAN = {
    "子": ["癸"], "丑": ["己", "癸", "辛"], "寅": ["甲", "丙", "戊"],
    "卯": ["乙"], "辰": ["戊", "乙", "癸"], "巳": ["丙", "戊", "庚"],
    "午": ["丁", "己"], "未": ["己", "丁", "乙"], "申": ["庚", "壬", "戊"],
    "酉": ["辛"], "戌": ["戊", "辛", "丁"], "亥": ["壬", "甲"],
}

# 生肖
SHENGXIAO = ["鼠", "牛", "虎", "兔", "龍", "蛇", "馬", "羊", "猴", "雞", "狗", "豬"]

# 五行相生
WUXING_SHENG = {"木": "火", "火": "土", "土": "金", "金": "水", "水": "木"}

# 五行相剋
WUXING_KE = {"木": "土", "土": "水", "水": "火", "火": "金", "金": "木"}

# 五行被生
WUXING_BEI_SHENG = {v: k for k, v in WUXING_SHENG.items()}

# 五行被剋
WUXING_BEI_KE = {v: k for k, v in WUXING_KE.items()}

# 地支六沖
DIZHI_CHONG = {
    "子": "午", "午": "子", "丑": "未", "未": "丑",
    "寅": "申", "申": "寅", "卯": "酉", "酉": "卯",
    "辰": "戌", "戌": "辰", "巳": "亥", "亥": "巳"
}

# 地支六合
DIZHI_LIUHE = {
    "子": "丑", "丑": "子", "寅": "亥", "亥": "寅",
    "卯": "戌", "戌": "卯", "辰": "酉", "酉": "辰",
    "巳": "申", "申": "巳", "午": "未", "未": "午"
}

# 地支三合
DIZHI_SANHE = {"申子辰": "水", "寅午戌": "火", "巳酉丑": "金", "亥卯未": "木"}

# 地支三會
DIZHI_SANHUI = {"寅卯辰": "木", "巳午未": "火", "申酉戌": "金", "亥子丑": "水"}

# 地支相刑
DIZHI_XING = {
    "寅": "巳", "巳": "申", "申": "寅",
    "丑": "戌", "戌": "未", "未": "丑",
    "子": "卯", "卯": "子",
    "辰": "辰", "午": "午", "酉": "酉", "亥": "亥",
}

# 地支相害
DIZHI_HAI = {
    "子": "未", "未": "子", "丑": "午", "午": "丑",
    "寅": "巳", "巳": "寅", "卯": "辰", "辰": "卯",
    "申": "亥", "亥": "申", "酉": "戌", "戌": "酉"
}

# 天干五合
TIANGAN_WUHE = {
    "甲": ("己", "土"), "己": ("甲", "土"),
    "乙": ("庚", "金"), "庚": ("乙", "金"),
    "丙": ("辛", "水"), "辛": ("丙", "水"),
    "丁": ("壬", "木"), "壬": ("丁", "木"),
    "戊": ("癸", "火"), "癸": ("戊", "火"),
}


# ════════════════════════════════════════════════════════════════════
# L0: 四神系統
# ════════════════════════════════════════════════════════════════════

class ShenType(Enum):
    """四神類型"""
    YONGSHEN = "用神"
    XISHEN = "喜神"
    JISHEN = "忌神"
    CHOUSHEN = "仇神"
    XIANSHEN = "閒神"


# ════════════════════════════════════════════════════════════════════
# L1: 基礎計算函數
# ════════════════════════════════════════════════════════════════════

def get_wuxing(gan_or_zhi: str) -> str:
    """獲取天干或地支的五行"""
    if gan_or_zhi in TIANGAN_WX:
        return TIANGAN_WX[gan_or_zhi]
    elif gan_or_zhi in DIZHI_WX:
        return DIZHI_WX[gan_or_zhi]
    return ""

def get_yinyang(gan_or_zhi: str) -> str:
    """獲取天干或地支的陰陽"""
    if gan_or_zhi in TIANGAN_YY:
        return TIANGAN_YY[gan_or_zhi]
    elif gan_or_zhi in DIZHI_YY:
        return DIZHI_YY[gan_or_zhi]
    return ""

def get_shengxiao(year_zhi: str) -> str:
    """獲取生肖"""
    if year_zhi in DIZHI_IDX:
        return SHENGXIAO[DIZHI_IDX[year_zhi]]
    return ""

def calc_shishen(day_gan: str, target_gan: str) -> str:
    """計算十神"""
    day_wx = TIANGAN_WX[day_gan]
    day_yy = TIANGAN_YY[day_gan]
    target_wx = TIANGAN_WX[target_gan]
    target_yy = TIANGAN_YY[target_gan]
    
    same_yy = (day_yy == target_yy)
    
    if day_wx == target_wx:
        return "比肩" if same_yy else "劫財"
    if WUXING_SHENG[day_wx] == target_wx:
        return "食神" if same_yy else "傷官"
    if WUXING_KE[day_wx] == target_wx:
        return "偏財" if same_yy else "正財"
    if WUXING_KE[target_wx] == day_wx:
        return "七殺" if same_yy else "正官"
    if WUXING_SHENG[target_wx] == day_wx:
        return "偏印" if same_yy else "正印"
    return ""

def check_dizhi_relation(zhi1: str, zhi2: str) -> List[str]:
    """檢查兩地支關係"""
    relations = []
    
    if DIZHI_CHONG.get(zhi1) == zhi2:
        relations.append("六沖")
    if DIZHI_LIUHE.get(zhi1) == zhi2:
        relations.append("六合")
    
    for sanhe_zhi, sanhe_wx in DIZHI_SANHE.items():
        if zhi1 in sanhe_zhi and zhi2 in sanhe_zhi:
            relations.append(f"三合{sanhe_wx}")
            break
    
    for sanhui_zhi, sanhui_wx in DIZHI_SANHUI.items():
        if zhi1 in sanhui_zhi and zhi2 in sanhui_zhi:
            relations.append(f"三會{sanhui_wx}")
            break
    
    if DIZHI_XING.get(zhi1) == zhi2:
        relations.append("相刑")
    if DIZHI_HAI.get(zhi1) == zhi2:
        relations.append("相害")
    
    wx1, wx2 = DIZHI_WX[zhi1], DIZHI_WX[zhi2]
    if WUXING_SHENG[wx1] == wx2:
        relations.append("相生")
    elif WUXING_KE[wx1] == wx2:
        relations.append("相剋")
    
    return relations


# ════════════════════════════════════════════════════════════════════
# L2: 資料結構
# ════════════════════════════════════════════════════════════════════

@dataclass
class BaziPillar:
    """單柱"""
    name: str
    gan: str
    zhi: str
    gan_wx: str = ""
    zhi_wx: str = ""
    canggan: List[str] = field(default_factory=list)
    shishen: str = ""
    
    def __post_init__(self):
        if self.gan:
            self.gan_wx = TIANGAN_WX.get(self.gan, "")
        if self.zhi:
            self.zhi_wx = DIZHI_WX.get(self.zhi, "")
            self.canggan = DIZHI_CANGGAN.get(self.zhi, [])

@dataclass 
class BaziChart:
    """八字命盤"""
    year: BaziPillar = None
    month: BaziPillar = None
    day: BaziPillar = None
    hour: BaziPillar = None
    
    day_master: str = ""
    day_master_wx: str = ""
    day_master_yy: str = ""
    
    wx_count: Dict[str, float] = field(default_factory=dict)
    wx_missing: List[str] = field(default_factory=list)
    
    is_strong: bool = False
    strength_score: int = 50
    strength_desc: str = ""
    
    yongshen: str = ""
    xishen: List[str] = field(default_factory=list)
    jishen: List[str] = field(default_factory=list)
    choushen: List[str] = field(default_factory=list)
    xianshen: List[str] = field(default_factory=list)
    bushen: List[str] = field(default_factory=list)
    
    shengxiao: str = ""
    
    def get_pillars(self) -> List[BaziPillar]:
        return [self.year, self.month, self.day, self.hour]
    
    def get_ganzhi_str(self) -> str:
        pillars = self.get_pillars()
        return " ".join([f"{p.gan}{p.zhi}" for p in pillars if p])

@dataclass
class RikePeihe:
    """日課配合評分"""
    rike_gan: str = ""
    rike_zhi: str = ""
    rike_wx: str = ""
    score: int = 75
    relations: List[str] = field(default_factory=list)
    desc: str = ""
    sheng_yongshen: bool = False
    ke_jishen: bool = False
    chong_mingzhu: bool = False
    he_mingzhu: bool = False


# ════════════════════════════════════════════════════════════════════
# L3: 核心類 - 八字分析器
# ════════════════════════════════════════════════════════════════════

class BaziAnalyzer:
    """八字分析器"""
    
    def __init__(self, year_gz: str, month_gz: str, day_gz: str, hour_gz: str):
        self.chart = BaziChart()
        
        self.chart.year = self._parse_pillar("年柱", year_gz)
        self.chart.month = self._parse_pillar("月柱", month_gz)
        self.chart.day = self._parse_pillar("日柱", day_gz)
        self.chart.hour = self._parse_pillar("時柱", hour_gz)
        
        self.chart.day_master = self.chart.day.gan
        self.chart.day_master_wx = TIANGAN_WX[self.chart.day_master]
        self.chart.day_master_yy = TIANGAN_YY[self.chart.day_master]
        self.chart.shengxiao = get_shengxiao(self.chart.year.zhi)
        
        self._calc_shishen()
        self._analyze()
    
    def _parse_pillar(self, name: str, gz: str) -> BaziPillar:
        if len(gz) >= 2:
            return BaziPillar(name=name, gan=gz[0], zhi=gz[1])
        return BaziPillar(name=name, gan="", zhi="")
    
    def _calc_shishen(self):
        day_gan = self.chart.day_master
        for pillar in [self.chart.year, self.chart.month, self.chart.hour]:
            if pillar and pillar.gan:
                pillar.shishen = calc_shishen(day_gan, pillar.gan)
    
    def _analyze(self):
        self._calc_wuxing_count()
        self._calc_strength()
        self._calc_yongshen()
        self._calc_bushen()
    
    def _calc_wuxing_count(self):
        wx_count = {"木": 0, "火": 0, "土": 0, "金": 0, "水": 0}
        gan_weight = {"年": 0.8, "月": 1.0, "日": 1.2, "時": 0.8}
        zhi_weight = {"年": 0.8, "月": 1.2, "日": 1.0, "時": 0.8}
        
        pillars = [
            (self.chart.year, "年"), (self.chart.month, "月"),
            (self.chart.day, "日"), (self.chart.hour, "時"),
        ]
        
        for pillar, pos in pillars:
            if not pillar:
                continue
            if pillar.gan_wx:
                wx_count[pillar.gan_wx] += gan_weight[pos]
            if pillar.zhi_wx:
                wx_count[pillar.zhi_wx] += zhi_weight[pos] * 0.6
            for i, cg in enumerate(pillar.canggan):
                cg_wx = TIANGAN_WX[cg]
                cg_weight = [0.3, 0.2, 0.1][min(i, 2)]
                wx_count[cg_wx] += zhi_weight[pos] * cg_weight
        
        self.chart.wx_count = wx_count
        self.chart.wx_missing = [wx for wx, count in wx_count.items() if count < 0.5]
    
    def _calc_strength(self):
        day_wx = self.chart.day_master_wx
        wx_count = self.chart.wx_count
        month_zhi = self.chart.month.zhi
        month_wx = DIZHI_WX[month_zhi]
        
        deling = 0
        if month_wx == day_wx:
            deling = 20
        elif WUXING_SHENG[month_wx] == day_wx:
            deling = 15
        elif WUXING_KE[month_wx] == day_wx:
            deling = -15
        
        same_wx = wx_count.get(day_wx, 0)
        sheng_wx = wx_count.get(WUXING_BEI_SHENG.get(day_wx, ""), 0)
        dezhu = (same_wx + sheng_wx) * 8
        
        ke_wx = wx_count.get(WUXING_BEI_KE.get(day_wx, ""), 0)
        xie_wx = wx_count.get(WUXING_SHENG.get(day_wx, ""), 0)
        shouke = (ke_wx + xie_wx * 0.7) * 6
        
        strength = 50 + deling + dezhu - shouke
        strength = max(10, min(90, int(strength)))
        
        self.chart.strength_score = strength
        self.chart.is_strong = strength >= 50
        
        if strength >= 70:
            self.chart.strength_desc = "身強"
        elif strength >= 55:
            self.chart.strength_desc = "偏強"
        elif strength >= 45:
            self.chart.strength_desc = "中和"
        elif strength >= 30:
            self.chart.strength_desc = "偏弱"
        else:
            self.chart.strength_desc = "身弱"
    
    def _calc_yongshen(self):
        day_wx = self.chart.day_master_wx
        is_strong = self.chart.is_strong
        
        if is_strong:
            self.chart.yongshen = WUXING_KE.get(day_wx) or WUXING_SHENG.get(day_wx)
            if self.chart.yongshen:
                self.chart.xishen = [WUXING_BEI_SHENG.get(self.chart.yongshen, "")]
            self.chart.jishen = [WUXING_BEI_SHENG.get(day_wx, ""), day_wx]
        else:
            self.chart.yongshen = WUXING_BEI_SHENG.get(day_wx) or day_wx
            if self.chart.yongshen:
                self.chart.xishen = [WUXING_BEI_SHENG.get(self.chart.yongshen, "")]
            self.chart.jishen = [WUXING_BEI_KE.get(day_wx, ""), WUXING_SHENG.get(day_wx, "")]
        
        self.chart.xishen = [x for x in self.chart.xishen if x]
        self.chart.jishen = [x for x in self.chart.jishen if x]
        self.chart.choushen = [WUXING_BEI_SHENG.get(j, "") for j in self.chart.jishen]
        self.chart.choushen = [x for x in self.chart.choushen if x and x not in self.chart.jishen]
        
        all_wx = {"木", "火", "土", "金", "水"}
        used = {self.chart.yongshen} | set(self.chart.xishen) | set(self.chart.jishen) | set(self.chart.choushen)
        self.chart.xianshen = list(all_wx - used)
    
    def _calc_bushen(self):
        bushen = []
        for wx in self.chart.wx_missing:
            if wx == self.chart.yongshen or wx in self.chart.xishen:
                bushen.append(wx)
        self.chart.bushen = bushen
    
    def should_bu(self, wx: str) -> Tuple[bool, str]:
        """判斷某五行是否應該補"""
        if wx == self.chart.yongshen:
            return True, "必補！用神"
        elif wx in self.chart.xishen:
            return True, "要補！喜神"
        elif wx in self.chart.jishen:
            return False, "不補！忌神，缺了是福"
        elif wx in self.chart.choushen:
            return False, "不補！仇神"
        else:
            return True, "可補，閒神"
    
    def calc_rike_peihe(self, rike_gan: str, rike_zhi: str) -> RikePeihe:
        """計算日課與命主配合"""
        result = RikePeihe(
            rike_gan=rike_gan, rike_zhi=rike_zhi,
            rike_wx=TIANGAN_WX.get(rike_gan, "")
        )
        
        score = 75
        relations = []
        rike_wx = result.rike_wx
        day_zhi = self.chart.day.zhi
        year_zhi = self.chart.year.zhi
        
        # 日課五行與用神關係
        if rike_wx == self.chart.yongshen:
            score += 20
            relations.append("日課為用神")
            result.sheng_yongshen = True
        elif WUXING_SHENG.get(rike_wx) == self.chart.yongshen:
            score += 15
            relations.append("日課生用神")
            result.sheng_yongshen = True
        elif rike_wx in self.chart.xishen:
            score += 10
            relations.append("日課為喜神")
        
        # 日課五行與忌神關係
        if rike_wx in self.chart.jishen:
            score -= 25
            relations.append("日課為忌神")
        elif WUXING_KE.get(rike_wx) in self.chart.jishen:
            score += 10
            relations.append("日課剋忌神")
            result.ke_jishen = True
        
        # 日課地支與命主地支關係
        day_relations = check_dizhi_relation(rike_zhi, day_zhi)
        if "六沖" in day_relations:
            score -= 30
            relations.append("沖日支")
            result.chong_mingzhu = True
        elif "六合" in day_relations:
            score += 15
            relations.append("合日支")
            result.he_mingzhu = True
        
        year_relations = check_dizhi_relation(rike_zhi, year_zhi)
        if "六沖" in year_relations:
            score -= 20
            relations.append("沖年支")
        elif "六合" in year_relations:
            score += 10
            relations.append("合年支")
        
        for rel in day_relations + year_relations:
            if "三合" in rel:
                score += 8
                relations.append(rel)
                break
        
        result.score = max(20, min(100, score))
        result.relations = relations
        result.desc = "、".join(relations) if relations else "平"
        
        return result
    
    def print_chart(self):
        """輸出命盤"""
        c = self.chart
        print("═" * 60)
        print("        八字命盤")
        print("═" * 60)
        print(f"""
  四柱：{c.get_ganzhi_str()}
  生肖：{c.shengxiao}
  日主：{c.day_master}（{c.day_master_wx}{c.day_master_yy}）
  
  五行：木{c.wx_count.get('木', 0):.1f} 火{c.wx_count.get('火', 0):.1f} 土{c.wx_count.get('土', 0):.1f} 金{c.wx_count.get('金', 0):.1f} 水{c.wx_count.get('水', 0):.1f}
  缺失：{c.wx_missing if c.wx_missing else '無'}
  
  身強弱：{c.strength_desc}（{c.strength_score}分）
  
  用神：{c.yongshen} ← 最需要
  喜神：{c.xishen}
  忌神：{c.jishen} ← 要避開
  
  需補：{c.bushen if c.bushen else '無特別需補'}
        """)
        print("═" * 60)


# ════════════════════════════════════════════════════════════════════
# L3: 雙人合婚分析
# ════════════════════════════════════════════════════════════════════

@dataclass
class HeHunResult:
    """合婚結果"""
    score: int = 75
    grade: str = "中"
    nianming_he: int = 0
    rizhu_he: int = 0
    yongshen_he: int = 0
    shengxiao_he: int = 0
    details: List[str] = field(default_factory=list)

class HeHunAnalyzer:
    """合婚分析器"""
    
    def __init__(self, man_chart: BaziChart, woman_chart: BaziChart):
        self.man = man_chart
        self.woman = woman_chart
    
    def analyze(self) -> HeHunResult:
        result = HeHunResult()
        score = 60
        details = []
        
        # 1. 年命合
        man_year_zhi = self.man.year.zhi
        woman_year_zhi = self.woman.year.zhi
        year_relations = check_dizhi_relation(man_year_zhi, woman_year_zhi)
        
        if "六合" in year_relations:
            score += 15
            result.nianming_he = 90
            details.append(f"年命六合（{man_year_zhi}合{woman_year_zhi}）大吉")
        elif any("三合" in r for r in year_relations):
            score += 10
            result.nianming_he = 85
            details.append("年命三合 吉")
        elif "六沖" in year_relations:
            score -= 15
            result.nianming_he = 40
            details.append(f"年命六沖（{man_year_zhi}沖{woman_year_zhi}）不利")
        else:
            result.nianming_he = 70
            details.append("年命平和")
        
        # 2. 日柱合
        man_day = self.man.day
        woman_day = self.woman.day
        
        if TIANGAN_WUHE.get(man_day.gan, (None,))[0] == woman_day.gan:
            score += 15
            result.rizhu_he = 95
            details.append(f"日干相合（{man_day.gan}合{woman_day.gan}）大吉")
        
        day_relations = check_dizhi_relation(man_day.zhi, woman_day.zhi)
        if "六合" in day_relations:
            score += 12
            result.rizhu_he = max(result.rizhu_he, 90)
            details.append("日支六合 吉")
        elif "六沖" in day_relations:
            score -= 12
            result.rizhu_he = min(result.rizhu_he or 100, 45)
            details.append("日支六沖 不利")
        
        if result.rizhu_he == 0:
            result.rizhu_he = 70
        
        # 3. 用神配合
        man_yong = self.man.yongshen
        woman_yong = self.woman.yongshen
        
        if man_yong in [woman_yong] + self.woman.xishen:
            score += 10
            result.yongshen_he = 90
            details.append("男命用神利女命")
        if woman_yong in [man_yong] + self.man.xishen:
            score += 10
            result.yongshen_he = max(result.yongshen_he, 90)
            details.append("女命用神利男命")
        
        if man_yong in self.woman.jishen:
            score -= 8
            result.yongshen_he = min(result.yongshen_he or 100, 50)
            details.append("男命用神為女命忌神")
        if woman_yong in self.man.jishen:
            score -= 8
            result.yongshen_he = min(result.yongshen_he or 100, 50)
            details.append("女命用神為男命忌神")
        
        if result.yongshen_he == 0:
            result.yongshen_he = 70
        
        result.shengxiao_he = result.nianming_he
        result.score = max(30, min(100, score))
        
        if result.score >= 85:
            result.grade = "上上"
        elif result.score >= 75:
            result.grade = "上"
        elif result.score >= 65:
            result.grade = "中上"
        elif result.score >= 55:
            result.grade = "中"
        elif result.score >= 45:
            result.grade = "中下"
        else:
            result.grade = "下"
        
        result.details = details
        return result


# ════════════════════════════════════════════════════════════════════
# L4: 便捷函數
# ════════════════════════════════════════════════════════════════════

def analyze_bazi(year_gz: str, month_gz: str, day_gz: str, hour_gz: str) -> BaziChart:
    """便捷函數：分析八字"""
    analyzer = BaziAnalyzer(year_gz, month_gz, day_gz, hour_gz)
    return analyzer.chart

def analyze_hehun(man_bazi: Tuple[str, str, str, str], 
                   woman_bazi: Tuple[str, str, str, str]) -> HeHunResult:
    """便捷函數：合婚分析"""
    man_analyzer = BaziAnalyzer(*man_bazi)
    woman_analyzer = BaziAnalyzer(*woman_bazi)
    hehun = HeHunAnalyzer(man_analyzer.chart, woman_analyzer.chart)
    return hehun.analyze()

def calc_rike_score(bazi: BaziChart, rike_gan: str, rike_zhi: str) -> RikePeihe:
    """便捷函數：計算日課配合"""
    analyzer = BaziAnalyzer(
        f"{bazi.year.gan}{bazi.year.zhi}",
        f"{bazi.month.gan}{bazi.month.zhi}",
        f"{bazi.day.gan}{bazi.day.zhi}",
        f"{bazi.hour.gan}{bazi.hour.zhi}"
    )
    return analyzer.calc_rike_peihe(rike_gan, rike_zhi)


# ════════════════════════════════════════════════════════════════════
# L5: 大運流年整合
# ════════════════════════════════════════════════════════════════════

# 嘗試導入大運流年模組
try:
    from dayun_calculator import DayunCalculator, DayunResult
    from liunian_analyzer import LiunianAnalyzer, LiunianAnalysis
    HAS_DAYUN = True
except ImportError:
    HAS_DAYUN = False
    DayunResult = None
    LiunianAnalysis = None

def calc_dayun(year_gz: str, month_gz: str, gender: str,
               birth_year: int, birth_month: int, birth_day: int,
               num_dayun: int = 8):
    """
    計算大運
    
    Args:
        year_gz: 年柱干支
        month_gz: 月柱干支
        gender: 性別（"男"/"女"）
        birth_year/month/day: 出生日期
        num_dayun: 大運數量
    
    Returns:
        DayunResult 或 None
    """
    if not HAS_DAYUN:
        return None
    
    try:
        calc = DayunCalculator(
            year_gan=year_gz[0],
            month_ganzhi=month_gz,
            gender=gender,
            birth_year=birth_year,
            birth_month=birth_month,
            birth_day=birth_day
        )
        return calc.calculate(num_dayun)
    except:
        return None

def calc_liunian(day_master: str, pillars: dict, year: int, is_strong: bool = True):
    """
    計算流年
    
    Args:
        day_master: 日主天干
        pillars: 四柱 {"year": "甲子", "month": "丙寅", "day": "庚午", "hour": "壬申"}
        year: 流年年份
        is_strong: 是否身強
    
    Returns:
        LiunianAnalysis 或 None
    """
    if not HAS_DAYUN:
        return None
    
    try:
        analyzer = LiunianAnalyzer(day_master, pillars, is_strong)
        return analyzer.analyze_year(year)
    except:
        return None


def calc_liunian_simple(bazi_tuple: Tuple[str, str, str, str], year: int):
    """
    簡化流年計算
    
    Args:
        bazi_tuple: (年柱, 月柱, 日柱, 時柱)
        year: 流年年份
    
    Returns:
        LiunianAnalysis 或 None
    """
    if not HAS_DAYUN:
        return None
    
    try:
        pillars = {
            "year": bazi_tuple[0],
            "month": bazi_tuple[1],
            "day": bazi_tuple[2],
            "hour": bazi_tuple[3]
        }
        day_master = bazi_tuple[2][0]  # 日柱天干
        analyzer = LiunianAnalyzer(day_master, pillars, True)
        return analyzer.analyze_year(year)
    except:
        return None


# ════════════════════════════════════════════════════════════════════
# 測試
# ════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("═" * 70)
    print("        八字分析共用模組 - 測試")
    print("═" * 70)
    
    # 測試案例：1973/12/30 17:00（楊三興）
    print("\n【測試1：八字分析】")
    analyzer = BaziAnalyzer("癸丑", "甲子", "庚子", "乙酉")
    analyzer.print_chart()
    
    # 測試日課配合
    print("\n【測試2：日課配合】")
    peihe = analyzer.calc_rike_peihe("壬", "辰")
    print(f"  日課：壬辰")
    print(f"  配合分數：{peihe.score}")
    print(f"  配合關係：{peihe.desc}")
    
    # 測試合婚
    print("\n【測試3：合婚分析】")
    man_bazi = ("庚午", "戊寅", "甲子", "丙寅")
    woman_bazi = ("壬申", "壬寅", "丙午", "庚寅")
    
    result = analyze_hehun(man_bazi, woman_bazi)
    print(f"  合婚等級：{result.grade}（{result.score}分）")
    print(f"  年命合：{result.nianming_he}")
    print(f"  日柱合：{result.rizhu_he}")
    print(f"  詳情：")
    for d in result.details:
        print(f"    - {d}")
    
    print("\n" + "═" * 70)
