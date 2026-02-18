#!/usr/bin/env python3
"""
bazi_naming_selector.py - 八字配合命名選擇器
北斗命數 v3.1.3

逆向工程邏輯：
1. 輸入生辰 → 計算八字 → 得出用神/喜神/忌神
2. 根據用神 → 篩選適合的漢字五行
3. 根據姓氏筆畫 → 計算最佳名字筆畫組合（五格全吉）
4. 組合漢字 → 生成候選名字 → 排序輸出

PYLIB 依賴：
- wuxing_analyzer.py（五行分析）
- main.py（康熙筆畫查詢）
- name_engine.py（五格計算）

XTF8 層級：L0-L4
@織明 × @理樞
"""

from typing import Dict, List, Tuple, Optional, Set
from dataclasses import dataclass, field
from enum import Enum
import sqlite3
import os

# ============================================================
# L0: 常量定義
# ============================================================

# 五行
class WuXing(Enum):
    MU = "木"
    HUO = "火"
    TU = "土"
    JIN = "金"
    SHUI = "水"

# 五行生剋
WUXING_SHENG = {"木": "火", "火": "土", "土": "金", "金": "水", "水": "木"}
WUXING_KE = {"木": "土", "土": "水", "水": "火", "火": "金", "金": "木"}
WUXING_SHENG_ME = {"木": "水", "火": "木", "土": "火", "金": "土", "水": "金"}

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

# 數理吉凶（1-81）
SHULI_JIXIONG = {
    # 吉數
    1: "吉", 3: "吉", 5: "吉", 6: "吉", 7: "吉", 8: "吉",
    11: "吉", 13: "吉", 15: "吉", 16: "吉", 17: "吉", 18: "吉",
    21: "吉", 23: "吉", 24: "吉", 25: "吉", 29: "吉",
    31: "吉", 32: "吉", 33: "吉", 35: "吉", 37: "吉", 39: "吉",
    41: "吉", 45: "吉", 47: "吉", 48: "吉",
    52: "吉", 57: "吉", 61: "吉", 63: "吉", 65: "吉", 67: "吉", 68: "吉",
    81: "吉",
    # 半吉
    10: "半吉", 22: "半吉", 27: "半吉", 30: "半吉", 38: "半吉",
    49: "半吉", 51: "半吉", 55: "半吉", 58: "半吉",
    71: "半吉", 73: "半吉", 75: "半吉", 78: "半吉",
}

def get_shuli_jixiong(n: int) -> str:
    """取得數理吉凶"""
    if n > 81:
        n = n % 80 or 80
    return SHULI_JIXIONG.get(n, "凶")

# 筆畫對應五行（尾數）
def stroke_to_wuxing(stroke: int) -> str:
    """筆畫尾數對應五行"""
    last = stroke % 10
    if last in [1, 2]:
        return "木"
    elif last in [3, 4]:
        return "火"
    elif last in [5, 6]:
        return "土"
    elif last in [7, 8]:
        return "金"
    else:  # 9, 0
        return "水"

# ============================================================
# L1: 水/木部首常用字庫
# ============================================================

# 水部首字（按筆畫分類）
WATER_CHARS = {
    5: ["永", "汀", "汁", "氾"],
    6: ["汝", "江", "池", "汐", "汕"],
    7: ["沂", "沐", "汲", "沁", "沅", "沃"],
    8: ["沛", "泓", "泊", "法", "沫", "沅", "沐", "泗", "沿"],
    9: ["泉", "泰", "洋", "洛", "洪", "洲", "津", "洞", "洵"],
    10: ["浩", "浚", "海", "浦", "涂", "浪", "浮", "浸"],
    11: ["涵", "淳", "淇", "淮", "深", "淼", "清", "淑", "淞"],
    12: ["淵", "渝", "游", "湘", "湛", "渲", "湖", "渡", "渠"],
    13: ["源", "溪", "溥", "湧", "溢", "溫", "溶", "滄"],
    14: ["滔", "漢", "滄", "漣", "漪", "滿", "漸"],
    15: ["潤", "潔", "澄", "潛", "潮", "澈", "澎"],
    16: ["澤", "澎", "澳", "澗", "澱", "霖"],
    17: ["濤", "濟", "濱", "濬", "濠"],
    18: ["瀚", "濱", "瀏", "瀛"],
}

# 木部首字（按筆畫分類）
WOOD_CHARS = {
    4: ["木", "朴"],
    5: ["本", "末", "札", "未", "禾"],
    6: ["朵", "朴", "机", "朽", "朱"],
    7: ["杉", "材", "村", "杏", "李", "杜", "束"],
    8: ["林", "松", "杰", "杭", "東", "枝", "杯", "析"],
    9: ["柏", "柳", "柯", "柱", "柔", "桂", "柄", "柚"],
    10: ["桐", "桓", "桑", "格", "栩", "栢", "桃", "株"],
    11: ["梧", "梓", "梅", "梁", "棋", "梢", "梨"],
    12: ["森", "棠", "棟", "椒", "植", "棉", "棕"],
    13: ["楠", "楷", "楓", "楚", "榆", "楊", "業"],
    14: ["榕", "榮", "槐", "榛", "槍", "榜"],
    15: ["樟", "樂", "樸", "樺", "樑", "樓"],
    16: ["橋", "樹", "橙", "橘"],
}

# ============================================================
# L2: 資料結構
# ============================================================

@dataclass
class BaziInfo:
    """八字資訊"""
    year_pillar: str
    month_pillar: str
    day_pillar: str
    hour_pillar: str
    day_master: str  # 日主天干
    day_element: str  # 日主五行
    is_strong: bool  # 身強身弱
    strength_score: int  # 強弱分數

@dataclass
class YongShenConfig:
    """用神配置"""
    yongshen: str  # 用神五行
    xishen: str    # 喜神五行
    jishen: str    # 忌神五行
    qiushen: str   # 仇神五行
    xianshen: str  # 閒神五行

@dataclass
class WuGeResult:
    """五格計算結果"""
    tian: int  # 天格
    ren: int   # 人格
    di: int    # 地格
    wai: int   # 外格
    zong: int  # 總格
    
    tian_ji: str = ""
    ren_ji: str = ""
    di_ji: str = ""
    wai_ji: str = ""
    zong_ji: str = ""
    
    all_ji: bool = False  # 是否全吉
    score: int = 0        # 綜合評分

@dataclass
class LifeStageAnalysis:
    """人生階段分析"""
    # 四柱對應
    childhood: str = ""    # 童年 1-16（年柱）
    youth: str = ""        # 青年 17-32（月柱）
    middle_age: str = ""   # 中年 33-48（日柱）
    elder: str = ""        # 晚年 49+（時柱）
    
    # 五格對應
    di_ge_stage: str = ""   # 地格 → 早年基礎
    ren_ge_stage: str = ""  # 人格 → 中年主運
    zong_ge_stage: str = "" # 總格 → 晚年歸宿
    
    # 綜合建議
    weak_stage: str = ""    # 最弱階段
    focus_wuge: str = ""    # 重點補強五格
    suggestion: str = ""    # 取名建議

@dataclass
class NameCandidate:
    """候選名字"""
    surname: str           # 姓
    given_name: str        # 名
    full_name: str         # 全名
    chars_wuxing: List[str]  # 各字五行
    wuge: WuGeResult       # 五格結果
    bazi_match_score: int  # 八字配合分數
    total_score: int       # 總分
    analysis: str          # 分析說明
    life_stage: Optional[LifeStageAnalysis] = None  # 人生階段分析

# ============================================================
# L3: 核心計算邏輯
# ============================================================

class BaziNamingSelector:
    """
    八字配合命名選擇器
    
    使用方式：
    selector = BaziNamingSelector()
    
    # 設定八字
    selector.set_bazi(
        day_master="庚",      # 日主
        is_strong=True,       # 身強
        month_zhi="丑"        # 月支（用於判斷月令）
    )
    
    # 或直接設定用神
    selector.set_yongshen(yongshen="水", xishen="木", jishen="土")
    
    # 生成名字
    names = selector.generate_names(
        surname="楊",
        count=10
    )
    """
    
    def __init__(self, db_path: str = None):
        self.bazi: Optional[BaziInfo] = None
        self.yongshen_config: Optional[YongShenConfig] = None
        self.db_path = db_path or "./kangxi_20k.db"
        
        # 載入字庫
        self.water_chars = WATER_CHARS
        self.wood_chars = WOOD_CHARS
        
    def set_bazi_from_pillars(
        self,
        year_pillar: str,
        month_pillar: str,
        day_pillar: str,
        hour_pillar: str
    ):
        """從四柱設定八字"""
        day_master = day_pillar[0]
        day_element = GAN_WUXING.get(day_master, "")
        
        # 計算身強身弱（簡化版）
        is_strong, score = self._calc_strength(
            day_master, day_element,
            [year_pillar, month_pillar, day_pillar, hour_pillar]
        )
        
        self.bazi = BaziInfo(
            year_pillar=year_pillar,
            month_pillar=month_pillar,
            day_pillar=day_pillar,
            hour_pillar=hour_pillar,
            day_master=day_master,
            day_element=day_element,
            is_strong=is_strong,
            strength_score=score
        )
        
        # 自動計算用神
        self._calc_yongshen()
        
    def set_yongshen(
        self,
        yongshen: str,
        xishen: str,
        jishen: str,
        qiushen: str = "",
        xianshen: str = ""
    ):
        """直接設定用神配置"""
        self.yongshen_config = YongShenConfig(
            yongshen=yongshen,
            xishen=xishen,
            jishen=jishen,
            qiushen=qiushen,
            xianshen=xianshen
        )
    
    def _calc_strength(
        self,
        day_master: str,
        day_element: str,
        pillars: List[str]
    ) -> Tuple[bool, int]:
        """計算身強身弱"""
        score = 0
        
        # 1. 月令得分
        month_zhi = pillars[1][1] if len(pillars) > 1 else ""
        month_wx = ZHI_WUXING.get(month_zhi, "")
        
        if month_wx == day_element:
            score += 40  # 當令
        elif WUXING_SHENG_ME.get(day_element) == month_wx:
            score += 30  # 相（生我）
        elif WUXING_SHENG.get(day_element) == month_wx:
            score += 10  # 休（我生）
        
        # 2. 通根得分
        for pillar in pillars:
            if len(pillar) < 2:
                continue
            zhi = pillar[1]
            cang_gans = ZHI_CANGGAN.get(zhi, [])
            for gan in cang_gans:
                gan_wx = GAN_WUXING.get(gan, "")
                if gan_wx == day_element:
                    score += 10  # 通根
        
        # 3. 印比得分
        for pillar in pillars:
            if not pillar:
                continue
            gan = pillar[0]
            gan_wx = GAN_WUXING.get(gan, "")
            
            if gan_wx == day_element:
                score += 10  # 比劫
            elif gan_wx == WUXING_SHENG_ME.get(day_element):
                score += 10  # 印星
        
        # 4. 洩耗扣分
        for pillar in pillars:
            if not pillar:
                continue
            gan = pillar[0]
            gan_wx = GAN_WUXING.get(gan, "")
            
            if gan_wx == WUXING_SHENG.get(day_element):
                score -= 5  # 食傷
            elif gan_wx == WUXING_KE.get(day_element):
                score -= 5  # 財
        
        is_strong = score >= 50
        return is_strong, score
    
    def _calc_yongshen(self):
        """根據八字計算用神"""
        if not self.bazi:
            return
        
        day_wx = self.bazi.day_element
        is_strong = self.bazi.is_strong
        
        if is_strong:
            # 身強：用神為洩（食傷）或剋（財官）
            yongshen = WUXING_SHENG.get(day_wx, "")  # 我生 = 食傷
            xishen = WUXING_KE.get(day_wx, "")       # 我剋 = 財
            jishen = WUXING_SHENG_ME.get(day_wx, "") # 生我 = 印
            qiushen = WUXING_KE.get(yongshen, "") if yongshen else ""  # 剋用神
        else:
            # 身弱：用神為生（印）或助（比劫）
            yongshen = WUXING_SHENG_ME.get(day_wx, "")  # 生我 = 印
            xishen = day_wx                              # 同我 = 比劫
            jishen = WUXING_KE.get(day_wx, "")          # 我剋 = 財（耗）
            qiushen = WUXING_SHENG.get(day_wx, "")      # 我生 = 食傷（洩）
        
        # 閒神 = 剩下的
        all_wx = {"木", "火", "土", "金", "水"}
        used = {yongshen, xishen, jishen, qiushen}
        xianshen = (all_wx - used).pop() if len(all_wx - used) > 0 else ""
        
        self.yongshen_config = YongShenConfig(
            yongshen=yongshen,
            xishen=xishen,
            jishen=jishen,
            qiushen=qiushen,
            xianshen=xianshen
        )
    
    def calc_wuge(self, surname_strokes: int, name1_strokes: int, name2_strokes: int = 0) -> WuGeResult:
        """計算五格"""
        if name2_strokes == 0:
            # 單名
            tian = surname_strokes + 1
            ren = surname_strokes + name1_strokes
            di = name1_strokes + 1
            wai = 2
            zong = surname_strokes + name1_strokes
        else:
            # 雙名
            tian = surname_strokes + 1
            ren = surname_strokes + name1_strokes
            di = name1_strokes + name2_strokes
            zong = surname_strokes + name1_strokes + name2_strokes
            wai = zong - ren + 1
        
        tian_ji = get_shuli_jixiong(tian)
        ren_ji = get_shuli_jixiong(ren)
        di_ji = get_shuli_jixiong(di)
        wai_ji = get_shuli_jixiong(wai)
        zong_ji = get_shuli_jixiong(zong)
        
        # 評分
        score = 0
        ji_count = 0
        for ji in [tian_ji, ren_ji, di_ji, wai_ji, zong_ji]:
            if ji == "吉":
                score += 20
                ji_count += 1
            elif ji == "半吉":
                score += 10
        
        all_ji = (ren_ji == "吉" and di_ji == "吉" and zong_ji == "吉")
        
        return WuGeResult(
            tian=tian, ren=ren, di=di, wai=wai, zong=zong,
            tian_ji=tian_ji, ren_ji=ren_ji, di_ji=di_ji,
            wai_ji=wai_ji, zong_ji=zong_ji,
            all_ji=all_ji, score=score
        )
    
    def find_best_stroke_combos(
        self,
        surname_strokes: int,
        max_strokes: int = 20
    ) -> List[Tuple[int, int, WuGeResult]]:
        """找出最佳筆畫組合"""
        results = []
        
        for s1 in range(1, max_strokes + 1):
            for s2 in range(1, max_strokes + 1):
                wuge = self.calc_wuge(surname_strokes, s1, s2)
                if wuge.all_ji:  # 人格、地格、總格都吉
                    results.append((s1, s2, wuge))
        
        # 按分數排序
        results.sort(key=lambda x: (-x[2].score, x[0] + x[1]))
        
        return results[:30]  # 返回前30個
    
    def get_chars_by_stroke_and_wuxing(
        self,
        stroke: int,
        wuxing: str
    ) -> List[str]:
        """根據筆畫和五行獲取漢字"""
        chars = []
        
        if wuxing == "水":
            chars.extend(self.water_chars.get(stroke, []))
        elif wuxing == "木":
            chars.extend(self.wood_chars.get(stroke, []))
        
        # 如果有康熙字典資料庫，可以擴展查詢
        if os.path.exists(self.db_path):
            try:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                # 根據部首判斷五行
                cursor.execute("""
                    SELECT char FROM kangxi 
                    WHERE stroke = ? 
                    LIMIT 50
                """, (stroke,))
                rows = cursor.fetchall()
                for row in rows:
                    char = row[0]
                    if self._char_wuxing(char) == wuxing:
                        if char not in chars:
                            chars.append(char)
                conn.close()
            except:
                pass
        
        return chars
    
    def _char_wuxing(self, char: str) -> str:
        """判斷漢字五行（簡化版：根據部首）"""
        water_radicals = "氵水冫雨"
        wood_radicals = "木艹竹禾"
        fire_radicals = "火灬日"
        earth_radicals = "土石山"
        metal_radicals = "金釒钅"
        
        for c in char:
            if c in water_radicals:
                return "水"
            elif c in wood_radicals:
                return "木"
            elif c in fire_radicals:
                return "火"
            elif c in earth_radicals:
                return "土"
            elif c in metal_radicals:
                return "金"
        
        return ""
    
    def calc_bazi_match_score(
        self,
        chars_wuxing: List[str]
    ) -> Tuple[int, str]:
        """計算八字配合分數"""
        if not self.yongshen_config:
            return 50, "未設定用神"
        
        score = 50  # 基準分
        analysis = []
        
        for wx in chars_wuxing:
            if wx == self.yongshen_config.yongshen:
                score += 25
                analysis.append(f"{wx}(用神+25)")
            elif wx == self.yongshen_config.xishen:
                score += 15
                analysis.append(f"{wx}(喜神+15)")
            elif wx == self.yongshen_config.jishen:
                score -= 20
                analysis.append(f"{wx}(忌神-20)")
            elif wx == self.yongshen_config.qiushen:
                score -= 10
                analysis.append(f"{wx}(仇神-10)")
        
        return min(100, max(0, score)), " ".join(analysis)
    
    def analyze_life_stages(self, wuge: WuGeResult) -> LifeStageAnalysis:
        """
        分析人生階段與五格配合
        
        四柱對應：
        - 年柱 → 童年 1-16
        - 月柱 → 青年 17-32
        - 日柱 → 中年 33-48
        - 時柱 → 晚年 49+
        
        五格對應：
        - 地格 → 早年基礎 1-25
        - 人格 → 中年主運 25-48（最重要）
        - 總格 → 晚年歸宿 49+
        """
        analysis = LifeStageAnalysis()
        
        # 分析四柱（如果有八字資訊）
        if self.bazi:
            # 年柱解讀
            year_gan = self.bazi.year_pillar[0] if self.bazi.year_pillar else ""
            year_wx = GAN_WUXING.get(year_gan, "")
            if year_wx == self.yongshen_config.yongshen if self.yongshen_config else "":
                analysis.childhood = "童年順利，有用神助力"
            elif year_wx == self.yongshen_config.jishen if self.yongshen_config else "":
                analysis.childhood = "童年波折，需後天補強"
            else:
                analysis.childhood = "童年平穩"
            
            # 月柱解讀
            month_gan = self.bazi.month_pillar[0] if self.bazi.month_pillar else ""
            month_shishen = self._get_shishen(self.bazi.day_master, month_gan)
            if month_shishen in ["傷官", "七殺"]:
                analysis.youth = "青年創造力強但波折多，需地格吉來補強"
            elif month_shishen in ["正印", "偏印"]:
                analysis.youth = "青年有長輩助力，學業順利"
            elif month_shishen in ["正財", "偏財"]:
                analysis.youth = "青年財運佳，但需穩健"
            else:
                analysis.youth = "青年平穩發展"
            
            # 日柱解讀
            analysis.middle_age = f"中年核心：{self.bazi.day_master}金身強" if self.bazi.is_strong else f"中年核心：{self.bazi.day_master}金身弱"
            
            # 時柱解讀
            hour_gan = self.bazi.hour_pillar[0] if self.bazi.hour_pillar else ""
            hour_shishen = self._get_shishen(self.bazi.day_master, hour_gan)
            if hour_shishen in ["正財", "偏財"]:
                analysis.elder = "晚年財運穩定，有收成"
            elif hour_shishen in ["食神", "傷官"]:
                analysis.elder = "晚年子女有成就"
            elif hour_shishen in ["正官", "七殺"]:
                analysis.elder = "晚年有地位但壓力也有"
            else:
                analysis.elder = "晚年平穩"
        
        # 分析五格對應人生階段
        # 地格 → 早年基礎
        if wuge.di_ji == "吉":
            analysis.di_ge_stage = f"地格{wuge.di}吉：早年基礎穩固"
        elif wuge.di_ji == "半吉":
            analysis.di_ge_stage = f"地格{wuge.di}半吉：早年有小波折"
        else:
            analysis.di_ge_stage = f"地格{wuge.di}凶：早年基礎不穩，需注意"
        
        # 人格 → 中年主運（最重要）
        if wuge.ren_ji == "吉":
            analysis.ren_ge_stage = f"人格{wuge.ren}吉：中年主運旺盛，事業有成"
        elif wuge.ren_ji == "半吉":
            analysis.ren_ge_stage = f"人格{wuge.ren}半吉：中年需努力，有機會"
        else:
            analysis.ren_ge_stage = f"人格{wuge.ren}凶：中年運勢需謹慎"
        
        # 總格 → 晚年歸宿
        if wuge.zong_ji == "吉":
            analysis.zong_ge_stage = f"總格{wuge.zong}吉：晚年有歸宿，福壽雙全"
        elif wuge.zong_ji == "半吉":
            analysis.zong_ge_stage = f"總格{wuge.zong}半吉：晚年平穩"
        else:
            analysis.zong_ge_stage = f"總格{wuge.zong}凶：晚年需提早規劃"
        
        # 找出最弱階段，給出建議
        weak_stages = []
        if wuge.di_ji == "凶":
            weak_stages.append("早年")
        if wuge.ren_ji == "凶":
            weak_stages.append("中年")
        if wuge.zong_ji == "凶":
            weak_stages.append("晚年")
        
        if weak_stages:
            analysis.weak_stage = "、".join(weak_stages)
            if "早年" in weak_stages:
                analysis.focus_wuge = "地格"
            elif "中年" in weak_stages:
                analysis.focus_wuge = "人格"
            else:
                analysis.focus_wuge = "總格"
            analysis.suggestion = f"建議優化{analysis.focus_wuge}數理，補強{analysis.weak_stage}運勢"
        else:
            analysis.weak_stage = "無"
            analysis.focus_wuge = "人格"
            analysis.suggestion = "五格配置良好，各階段運勢平衡"
        
        return analysis
    
    def _get_shishen(self, day_master: str, gan: str) -> str:
        """計算十神"""
        if not day_master or not gan:
            return ""
        
        day_wx = GAN_WUXING.get(day_master, "")
        gan_wx = GAN_WUXING.get(gan, "")
        
        if not day_wx or not gan_wx:
            return ""
        
        # 判斷陰陽
        yang_gan = "甲丙戊庚壬"
        day_yang = day_master in yang_gan
        gan_yang = gan in yang_gan
        same_polarity = day_yang == gan_yang
        
        # 判斷十神
        if gan_wx == day_wx:
            return "比肩" if same_polarity else "劫財"
        elif gan_wx == WUXING_SHENG.get(day_wx):
            return "食神" if same_polarity else "傷官"
        elif gan_wx == WUXING_KE.get(day_wx):
            return "偏財" if same_polarity else "正財"
        elif gan_wx == WUXING_SHENG_ME.get(day_wx):
            return "偏印" if same_polarity else "正印"
        else:  # 剋我
            return "七殺" if same_polarity else "正官"
    
    def generate_names(
        self,
        surname: str,
        surname_strokes: int = None,
        count: int = 10,
        prefer_wuxing: List[str] = None
    ) -> List[NameCandidate]:
        """
        生成名字
        
        參數：
        - surname: 姓氏
        - surname_strokes: 姓氏筆畫（可自動查詢）
        - count: 生成數量
        - prefer_wuxing: 偏好五行（預設根據用神）
        """
        if not self.yongshen_config:
            raise ValueError("請先設定八字或用神")
        
        # 取得姓氏筆畫
        if surname_strokes is None:
            surname_strokes = self._get_kangxi_stroke(surname) or len(surname) * 10
        
        # 確定偏好五行
        if prefer_wuxing is None:
            prefer_wuxing = [
                self.yongshen_config.yongshen,
                self.yongshen_config.xishen
            ]
        
        # 找最佳筆畫組合
        stroke_combos = self.find_best_stroke_combos(surname_strokes)
        
        candidates = []
        
        for s1, s2, wuge in stroke_combos:
            # 為每個筆畫組合找漢字
            for wx1 in prefer_wuxing:
                chars1 = self.get_chars_by_stroke_and_wuxing(s1, wx1)
                for wx2 in prefer_wuxing:
                    chars2 = self.get_chars_by_stroke_and_wuxing(s2, wx2)
                    
                    for c1 in chars1[:5]:  # 限制每個組合最多5個字
                        for c2 in chars2[:5]:
                            given_name = c1 + c2
                            full_name = surname + given_name
                            
                            # 計算八字配合分數
                            chars_wuxing = [
                                self._char_wuxing(surname) or stroke_to_wuxing(surname_strokes),
                                wx1,
                                wx2
                            ]
                            bazi_score, bazi_analysis = self.calc_bazi_match_score(chars_wuxing)
                            
                            # 總分 = 五格分 + 八字配合分
                            total_score = wuge.score + bazi_score
                            
                            candidate = NameCandidate(
                                surname=surname,
                                given_name=given_name,
                                full_name=full_name,
                                chars_wuxing=chars_wuxing,
                                wuge=wuge,
                                bazi_match_score=bazi_score,
                                total_score=total_score,
                                analysis=f"五格{wuge.score}分 + 八字{bazi_score}分 = {total_score}分 | {bazi_analysis}"
                            )
                            candidates.append(candidate)
        
        # 去重並排序
        seen = set()
        unique_candidates = []
        for c in candidates:
            if c.full_name not in seen:
                seen.add(c.full_name)
                unique_candidates.append(c)
        
        unique_candidates.sort(key=lambda x: -x.total_score)
        
        return unique_candidates[:count]
    
    def _get_kangxi_stroke(self, char: str) -> Optional[int]:
        """查詢康熙字典筆畫"""
        if not os.path.exists(self.db_path):
            return None
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT stroke FROM kangxi WHERE char = ?", (char,))
            row = cursor.fetchone()
            conn.close()
            return row[0] if row else None
        except:
            return None
    
    def generate_report(self, candidates: List[NameCandidate]) -> str:
        """生成報告"""
        if not candidates:
            return "無候選名字"
        
        report = []
        report.append("=" * 70)
        report.append("八字配合命名選擇報告")
        report.append("=" * 70)
        
        if self.yongshen_config:
            report.append(f"\n【用神配置】")
            report.append(f"  用神：{self.yongshen_config.yongshen}")
            report.append(f"  喜神：{self.yongshen_config.xishen}")
            report.append(f"  忌神：{self.yongshen_config.jishen}")
        
        report.append(f"\n【候選名字】（共 {len(candidates)} 個）\n")
        
        for i, c in enumerate(candidates, 1):
            wuge = c.wuge
            report.append(f"  {i:2}. {c.full_name}")
            report.append(f"      五行：{'→'.join(c.chars_wuxing)}")
            report.append(f"      五格：人{wuge.ren}({wuge.ren_ji}) 地{wuge.di}({wuge.di_ji}) 總{wuge.zong}({wuge.zong_ji})")
            report.append(f"      評分：{c.analysis}")
            report.append("")
        
        report.append("=" * 70)
        
        return "\n".join(report)


# ============================================================
# L4: 便捷函數
# ============================================================

def generate_names_for_bazi(
    surname: str,
    surname_strokes: int,
    day_master: str,
    is_strong: bool,
    count: int = 10
) -> List[NameCandidate]:
    """
    根據八字生成名字（便捷函數）
    
    範例：
    names = generate_names_for_bazi(
        surname="楊",
        surname_strokes=13,
        day_master="庚",
        is_strong=True,
        count=10
    )
    """
    selector = BaziNamingSelector()
    
    day_element = GAN_WUXING.get(day_master, "")
    
    # 設定簡化的八字
    selector.bazi = BaziInfo(
        year_pillar="", month_pillar="", day_pillar=day_master,
        hour_pillar="", day_master=day_master, day_element=day_element,
        is_strong=is_strong, strength_score=60 if is_strong else 40
    )
    selector._calc_yongshen()
    
    return selector.generate_names(surname, surname_strokes, count)


def generate_names_for_yongshen(
    surname: str,
    surname_strokes: int,
    yongshen: str,
    xishen: str,
    jishen: str,
    count: int = 10
) -> List[NameCandidate]:
    """
    根據用神生成名字（便捷函數）
    
    範例：
    names = generate_names_for_yongshen(
        surname="楊",
        surname_strokes=13,
        yongshen="水",
        xishen="木",
        jishen="土",
        count=10
    )
    """
    selector = BaziNamingSelector()
    selector.set_yongshen(yongshen, xishen, jishen)
    return selector.generate_names(surname, surname_strokes, count)


# ============================================================
# 測試
# ============================================================

if __name__ == "__main__":
    print("=" * 70)
    print("八字配合命名選擇器 測試")
    print("=" * 70)
    
    # 測試案例：楊三興 1973/12/30 17:00
    # 日主：庚金，身強，用神：水，喜神：木，忌神：土
    
    print("\n【測試 1：根據用神生成名字】")
    print("姓氏：楊（13畫）")
    print("用神：水，喜神：木，忌神：土\n")
    
    names = generate_names_for_yongshen(
        surname="楊",
        surname_strokes=13,
        yongshen="水",
        xishen="木",
        jishen="土",
        count=10
    )
    
    print("【候選名字】")
    for i, n in enumerate(names, 1):
        wuge = n.wuge
        print(f"  {i:2}. {n.full_name}")
        print(f"      五行：{'→'.join(n.chars_wuxing)}")
        print(f"      五格：人{wuge.ren}({wuge.ren_ji}) 地{wuge.di}({wuge.di_ji}) 總{wuge.zong}({wuge.zong_ji})")
        print(f"      總分：{n.total_score}")
        print()
    
    print("\n【測試 2：根據日主生成名字】")
    print("日主：庚（金），身強\n")
    
    names2 = generate_names_for_bazi(
        surname="楊",
        surname_strokes=13,
        day_master="庚",
        is_strong=True,
        count=5
    )
    
    for i, n in enumerate(names2, 1):
        print(f"  {i}. {n.full_name} - 總分：{n.total_score}")
    
    print("\n" + "=" * 70)
    print("測試完成！")
    print("=" * 70)
