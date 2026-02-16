#!/usr/bin/env python3
"""
奇門遁甲引擎 qimen_engine.py v1.0
==================================
XTF任務: T8 | 執行星: 織明(框架)+理樞(實現)

📚 知識點：
- 奇門遁甲相傳源於黃帝戰蚩尤
- 三式之首（奇門、太乙、六壬）
- 本引擎採用「時家奇門」（最常用）
- 陽遁順排、陰遁逆排

📐 核心結構：
- 九宮：坎一、坤二、震三、巽四、中五、乾六、兌七、艮八、離九
- 八門：休、生、傷、杜、景、死、驚、開
- 九星：天蓬、天芮、天沖、天輔、天禽、天心、天柱、天任、天英
- 八神：值符、騰蛇、太陰、六合、白虎、玄武、九地、九天
- 三奇：乙、丙、丁
- 六儀：戊、己、庚、辛、壬、癸
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime, timedelta
import math

# ===== 基礎常數 =====
TIANGAN = ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"]
DIZHI = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]

# 九宮（洛書順序）
JIUGONG = {
    1: {"name": "坎", "direction": "北", "element": "水", "position": (1, 0)},
    2: {"name": "坤", "direction": "西南", "element": "土", "position": (0, 2)},
    3: {"name": "震", "direction": "東", "element": "木", "position": (1, 2)},
    4: {"name": "巽", "direction": "東南", "element": "木", "position": (2, 2)},
    5: {"name": "中", "direction": "中", "element": "土", "position": (1, 1)},
    6: {"name": "乾", "direction": "西北", "element": "金", "position": (2, 0)},
    7: {"name": "兌", "direction": "西", "element": "金", "position": (1, 0)},
    8: {"name": "艮", "direction": "東北", "element": "土", "position": (0, 0)},
    9: {"name": "離", "direction": "南", "element": "火", "position": (0, 1)},
}

# 九宮飛盤順序（順飛）
GONG_ORDER = [1, 8, 3, 4, 9, 2, 7, 6]  # 中宮5不飛

# 八門
BAMEN = ["休", "生", "傷", "杜", "景", "死", "驚", "開"]
BAMEN_DETAIL = {
    "休": {"element": "水", "nature": "吉", "meaning": "休養生息、謀事可成"},
    "生": {"element": "土", "nature": "大吉", "meaning": "萬物生發、大利求財"},
    "傷": {"element": "木", "nature": "凶", "meaning": "傷害損失、不利謀事"},
    "杜": {"element": "木", "nature": "平", "meaning": "閉塞不通、宜守不宜進"},
    "景": {"element": "火", "nature": "平", "meaning": "光明顯達、利文書事"},
    "死": {"element": "土", "nature": "大凶", "meaning": "萬物消亡、諸事不宜"},
    "驚": {"element": "金", "nature": "凶", "meaning": "驚恐憂慮、口舌是非"},
    "開": {"element": "金", "nature": "大吉", "meaning": "開創萬事、諸事皆宜"},
}

# 九星
JIUXING = ["天蓬", "天芮", "天沖", "天輔", "天禽", "天心", "天柱", "天任", "天英"]
JIUXING_DETAIL = {
    "天蓬": {"element": "水", "nature": "凶", "meaning": "盜賊之星、主陰謀"},
    "天芮": {"element": "土", "nature": "凶", "meaning": "病符之星、主疾病"},
    "天沖": {"element": "木", "nature": "吉", "meaning": "武曲之星、主果敢"},
    "天輔": {"element": "木", "nature": "吉", "meaning": "文曲之星、主文書"},
    "天禽": {"element": "土", "nature": "平", "meaning": "中央之星、主調和"},
    "天心": {"element": "金", "nature": "大吉", "meaning": "天醫之星、主醫藥"},
    "天柱": {"element": "金", "nature": "凶", "meaning": "訟獄之星、主口舌"},
    "天任": {"element": "土", "nature": "吉", "meaning": "福德之星、主忠厚"},
    "天英": {"element": "火", "nature": "平", "meaning": "文明之星、主血光"},
}

# 八神
BASHEN = ["值符", "騰蛇", "太陰", "六合", "白虎", "玄武", "九地", "九天"]
BASHEN_DETAIL = {
    "值符": {"nature": "大吉", "meaning": "萬事之首、諸事皆利"},
    "騰蛇": {"nature": "凶", "meaning": "虛驚怪異、主虛詐"},
    "太陰": {"nature": "吉", "meaning": "陰私暗昧、宜陰謀事"},
    "六合": {"nature": "吉", "meaning": "和合之神、主婚姻交易"},
    "白虎": {"nature": "凶", "meaning": "凶煞之神、主兵戈血光"},
    "玄武": {"nature": "凶", "meaning": "盜賊之神、主失物"},
    "九地": {"nature": "吉", "meaning": "坤順之神、宜守不宜攻"},
    "九天": {"nature": "吉", "meaning": "威權之神、利出行遠征"},
}

# 三奇六儀
SANQI = ["乙", "丙", "丁"]  # 三奇
LIUYI = ["戊", "己", "庚", "辛", "壬", "癸"]  # 六儀

# 陽遁九局起宮（時干落宮）
# 局數 → 戊落宮位
YANG_JU = {
    1: 1, 2: 2, 3: 3, 4: 4, 5: 5, 6: 6, 7: 7, 8: 8, 9: 9
}

# 陰遁九局起宮
YIN_JU = {
    1: 9, 2: 8, 3: 7, 4: 6, 5: 5, 6: 4, 7: 3, 8: 2, 9: 1
}

# 二十四節氣（用於定局）
JIEQI_24 = [
    "冬至", "小寒", "大寒", "立春", "雨水", "驚蟄",
    "春分", "清明", "穀雨", "立夏", "小滿", "芒種",
    "夏至", "小暑", "大暑", "立秋", "處暑", "白露",
    "秋分", "寒露", "霜降", "立冬", "小雪", "大雪"
]

# 節氣對應局數（上中下三元）
# 冬至後陽遁，夏至後陰遁
JIEQI_JU = {
    # 陽遁（冬至→夏至前）
    "冬至": {"上": 1, "中": 7, "下": 4},
    "小寒": {"上": 2, "中": 8, "下": 5},
    "大寒": {"上": 3, "中": 9, "下": 6},
    "立春": {"上": 8, "中": 5, "下": 2},
    "雨水": {"上": 9, "中": 6, "下": 3},
    "驚蟄": {"上": 1, "中": 7, "下": 4},
    "春分": {"上": 3, "中": 9, "下": 6},
    "清明": {"上": 4, "中": 1, "下": 7},
    "穀雨": {"上": 5, "中": 2, "下": 8},
    "立夏": {"上": 4, "中": 1, "下": 7},
    "小滿": {"上": 5, "中": 2, "下": 8},
    "芒種": {"上": 6, "中": 3, "下": 9},
    # 陰遁（夏至→冬至前）
    "夏至": {"上": 9, "中": 3, "下": 6},
    "小暑": {"上": 8, "中": 2, "下": 5},
    "大暑": {"上": 7, "中": 1, "下": 4},
    "立秋": {"上": 2, "中": 5, "下": 8},
    "處暑": {"上": 1, "中": 4, "下": 7},
    "白露": {"上": 9, "中": 3, "下": 6},
    "秋分": {"上": 7, "中": 1, "下": 4},
    "寒露": {"上": 6, "中": 9, "下": 3},
    "霜降": {"上": 5, "中": 8, "下": 2},
    "立冬": {"上": 6, "中": 9, "下": 3},
    "小雪": {"上": 5, "中": 8, "下": 2},
    "大雪": {"上": 4, "中": 7, "下": 1},
}


# ===== 節氣計算（簡化版） =====
def get_jieqi_for_date(year: int, month: int, day: int) -> Tuple[str, str]:
    """
    根據日期估算所在節氣和元（上中下）
    
    📚 簡化版：實際應用需精確節氣時刻表
    
    Returns:
        (節氣名, 上/中/下元)
    """
    # 簡化的節氣日期表（每月兩個節氣，約在5-7日和20-22日）
    jieqi_dates = [
        (1, 6, "小寒"), (1, 20, "大寒"),
        (2, 4, "立春"), (2, 19, "雨水"),
        (3, 6, "驚蟄"), (3, 21, "春分"),
        (4, 5, "清明"), (4, 20, "穀雨"),
        (5, 6, "立夏"), (5, 21, "小滿"),
        (6, 6, "芒種"), (6, 21, "夏至"),
        (7, 7, "小暑"), (7, 23, "大暑"),
        (8, 7, "立秋"), (8, 23, "處暑"),
        (9, 8, "白露"), (9, 23, "秋分"),
        (10, 8, "寒露"), (10, 24, "霜降"),
        (11, 7, "立冬"), (11, 22, "小雪"),
        (12, 7, "大雪"), (12, 22, "冬至"),
    ]
    
    # 找當前節氣
    current_jieqi = "冬至"  # 預設
    for jq_month, jq_day, jq_name in jieqi_dates:
        if month > jq_month or (month == jq_month and day >= jq_day):
            current_jieqi = jq_name
    
    # 計算元（每個節氣分三元，約5天一元）
    # 簡化：根據日期粗略判斷
    day_of_month = day
    if day_of_month <= 10:
        yuan = "上"
    elif day_of_month <= 20:
        yuan = "中"
    else:
        yuan = "下"
    
    return current_jieqi, yuan


def is_yang_dun(jieqi: str) -> bool:
    """判斷陽遁還是陰遁"""
    yang_jieqi = ["冬至", "小寒", "大寒", "立春", "雨水", "驚蟄",
                  "春分", "清明", "穀雨", "立夏", "小滿", "芒種"]
    return jieqi in yang_jieqi


def get_ju_number(jieqi: str, yuan: str) -> int:
    """獲取局數"""
    if jieqi in JIEQI_JU:
        return JIEQI_JU[jieqi].get(yuan, 1)
    return 1


# ===== 時辰計算 =====
def hour_to_dizhi(hour: int) -> Tuple[int, str]:
    """小時轉時辰地支"""
    # 子時23-1, 丑時1-3, ...
    zhi_idx = ((hour + 1) // 2) % 12
    return zhi_idx, DIZHI[zhi_idx]


def get_time_gan(day_gan: str, hour_zhi_idx: int) -> str:
    """根據日干和時辰求時干（五鼠遁時）"""
    day_idx = TIANGAN.index(day_gan)
    # 甲己日起甲子，乙庚日起丙子，丙辛日起戊子，丁壬日起庚子，戊癸日起壬子
    base_map = {0: 0, 5: 0, 1: 2, 6: 2, 2: 4, 7: 4, 3: 6, 8: 6, 4: 8, 9: 8}
    base = base_map.get(day_idx, 0)
    time_gan_idx = (base + hour_zhi_idx) % 10
    return TIANGAN[time_gan_idx]


# ===== 排盤核心 =====
@dataclass
class QiMenGong:
    """單一宮位"""
    gong_num: int           # 宮數 1-9
    gong_name: str          # 宮名
    direction: str          # 方位
    element: str            # 五行
    
    dipan_gan: str = ""     # 地盤干
    tianpan_gan: str = ""   # 天盤干
    men: str = ""           # 八門
    xing: str = ""          # 九星
    shen: str = ""          # 八神
    
    def summary(self) -> str:
        return f"{self.gong_name}({self.direction}): 天{self.tianpan_gan} 地{self.dipan_gan} {self.men}門 {self.xing} {self.shen}"


@dataclass
class QiMenPan:
    """奇門遁甲盤"""
    # 時間資訊
    year: int
    month: int
    day: int
    hour: int
    
    # 節氣與局
    jieqi: str
    yuan: str
    ju_num: int
    is_yang: bool
    
    # 時空干支
    time_gan: str
    time_zhi: str
    
    # 值符值使
    zhifu_xing: str = ""    # 值符（九星）
    zhifu_gong: int = 0     # 值符落宮
    zhishi_men: str = ""    # 值使（八門）
    zhishi_gong: int = 0    # 值使落宮
    
    # 九宮
    gongs: Dict[int, QiMenGong] = field(default_factory=dict)
    
    def summary(self) -> str:
        lines = [
            "=" * 50,
            "奇門遁甲時盤",
            "=" * 50,
            f"時間: {self.year}年{self.month}月{self.day}日 {self.hour}時",
            f"節氣: {self.jieqi} {self.yuan}元",
            f"局數: {'陽遁' if self.is_yang else '陰遁'}第{self.ju_num}局",
            f"時干支: {self.time_gan}{self.time_zhi}",
            f"值符: {self.zhifu_xing}（落{self.gongs.get(self.zhifu_gong, QiMenGong(0,'','','')).gong_name}宮）",
            f"值使: {self.zhishi_men}門（落{self.gongs.get(self.zhishi_gong, QiMenGong(0,'','','')).gong_name}宮）",
            "",
            "【九宮布局】",
        ]
        
        # 按方位顯示
        for gong_num in [4, 9, 2, 3, 5, 7, 8, 1, 6]:  # 九宮格順序
            if gong_num in self.gongs:
                g = self.gongs[gong_num]
                lines.append(f"  {g.summary()}")
        
        return "\n".join(lines)


def create_qimen_pan(year: int, month: int, day: int, hour: int, 
                     day_gan: str = "甲") -> QiMenPan:
    """
    建立奇門遁甲時盤
    
    Parameters:
        year, month, day, hour: 時間
        day_gan: 日干（需要外部提供或計算）
    
    Returns:
        QiMenPan 奇門盤
    """
    # 1. 獲取節氣和元
    jieqi, yuan = get_jieqi_for_date(year, month, day)
    
    # 2. 判斷陰陽遁
    is_yang = is_yang_dun(jieqi)
    
    # 3. 獲取局數
    ju_num = get_ju_number(jieqi, yuan)
    
    # 4. 計算時辰
    hour_zhi_idx, hour_zhi = hour_to_dizhi(hour)
    time_gan = get_time_gan(day_gan, hour_zhi_idx)
    
    # 5. 初始化九宮
    gongs = {}
    for num, info in JIUGONG.items():
        gongs[num] = QiMenGong(
            gong_num=num,
            gong_name=info["name"],
            direction=info["direction"],
            element=info["element"]
        )
    
    # 6. 布地盤（按局數起戊）
    # 三奇六儀順序：戊己庚辛壬癸丁丙乙
    sanqi_liuyi = ["戊", "己", "庚", "辛", "壬", "癸", "丁", "丙", "乙"]
    
    if is_yang:
        start_gong = YANG_JU[ju_num]
        # 陽遁順布
        gong_order = [start_gong]
        current = start_gong
        for _ in range(8):
            current = current % 9 + 1
            if current == 5:
                current = 6  # 跳過中宮
            gong_order.append(current)
    else:
        start_gong = YIN_JU[ju_num]
        # 陰遁逆布
        gong_order = [start_gong]
        current = start_gong
        for _ in range(8):
            current = (current - 2) % 9 + 1
            if current == 5:
                current = 4  # 跳過中宮
            gong_order.append(current)
    
    # 布地盤
    for i, gan in enumerate(sanqi_liuyi):
        if i < len(gong_order):
            gong_num = gong_order[i]
            if gong_num in gongs:
                gongs[gong_num].dipan_gan = gan
    
    # 7. 找值符（時干所在地盤位置的九星）
    time_gan_gong = 0
    for gong_num, gong in gongs.items():
        if gong.dipan_gan == time_gan:
            time_gan_gong = gong_num
            break
    
    # 值符是時干地盤所臨之星
    star_order = ["天蓬", "天芮", "天沖", "天輔", "天禽", "天心", "天柱", "天任", "天英"]
    zhifu_xing = star_order[time_gan_gong - 1] if 1 <= time_gan_gong <= 9 else "天禽"
    
    # 值符隨時干轉（值符落宮 = 時干所臨地盤宮）
    zhifu_gong = time_gan_gong if time_gan_gong else 5
    
    # 8. 布天盤（時干入中宮，帶動旋轉）
    # 簡化版：時干落宮即為天盤起點
    tianpan_start = zhifu_gong
    for i, gan in enumerate(sanqi_liuyi):
        if is_yang:
            target_gong = (tianpan_start + i - 1) % 9 + 1
        else:
            target_gong = (tianpan_start - i - 1) % 9 + 1
        if target_gong == 0:
            target_gong = 9
        if target_gong in gongs:
            gongs[target_gong].tianpan_gan = gan
    
    # 9. 布八門
    # 值使是時干地盤所臨之門，隨時干轉
    men_order = ["休", "死", "傷", "杜", "", "開", "驚", "生", "景"]  # 按宮位
    zhishi_men = men_order[time_gan_gong - 1] if 1 <= time_gan_gong <= 9 and men_order[time_gan_gong-1] else "休"
    zhishi_gong = zhifu_gong
    
    # 布門（從值使落宮起）
    active_men = [m for m in BAMEN]
    for i, men in enumerate(active_men):
        if is_yang:
            target_gong = (zhishi_gong + i - 1) % 9 + 1
        else:
            target_gong = (zhishi_gong - i - 1) % 9 + 1
        if target_gong == 0:
            target_gong = 9
        if target_gong == 5:
            continue  # 中宮不布門
        if target_gong in gongs:
            gongs[target_gong].men = men
    
    # 10. 布九星
    for i, xing in enumerate(star_order):
        gong_num = i + 1
        if gong_num in gongs:
            gongs[gong_num].xing = xing
    
    # 11. 布八神（從值符落宮起順布）
    for i, shen in enumerate(BASHEN):
        target_gong = (zhifu_gong + i - 1) % 9 + 1
        if target_gong == 0:
            target_gong = 9
        if target_gong in gongs:
            gongs[target_gong].shen = shen
    
    return QiMenPan(
        year=year, month=month, day=day, hour=hour,
        jieqi=jieqi, yuan=yuan, ju_num=ju_num, is_yang=is_yang,
        time_gan=time_gan, time_zhi=hour_zhi,
        zhifu_xing=zhifu_xing, zhifu_gong=zhifu_gong,
        zhishi_men=zhishi_men, zhishi_gong=zhishi_gong,
        gongs=gongs
    )


# ===== 格局判定 =====
def analyze_geju(pan: QiMenPan) -> List[str]:
    """
    分析格局
    
    📚 常見格局：
    - 天遁：天盤丙+地盤丁+生門
    - 地遁：天盤乙+地盤己+開門
    - 人遁：天盤丁+地盤太陰+休門
    - 青龍返首：天盤甲子戊落1宮
    - 等等...
    """
    findings = []
    
    # 檢查各宮格局
    for gong_num, gong in pan.gongs.items():
        tian = gong.tianpan_gan
        di = gong.dipan_gan
        men = gong.men
        xing = gong.xing
        shen = gong.shen
        
        # 天遁
        if tian == "丙" and di == "丁" and men == "生":
            findings.append(f"【天遁】{gong.gong_name}宮：丙奇得生門，諸事大吉")
        
        # 地遁
        if tian == "乙" and di == "己" and men == "開":
            findings.append(f"【地遁】{gong.gong_name}宮：乙奇得開門，謀事可成")
        
        # 人遁
        if tian == "丁" and shen == "太陰" and men == "休":
            findings.append(f"【人遁】{gong.gong_name}宮：丁奇得太陰休門，陰私事利")
        
        # 門迫（門剋宮）
        if men and gong.element:
            men_element = BAMEN_DETAIL.get(men, {}).get("element", "")
            # 簡化的五行相剋判斷
            ke_map = {"金": "木", "木": "土", "土": "水", "水": "火", "火": "金"}
            if ke_map.get(men_element) == gong.element:
                findings.append(f"【門迫】{gong.gong_name}宮：{men}門剋宮，不利行動")
        
        # 奇入墓
        if tian == "乙" and gong_num == 2:  # 乙入坤
            findings.append(f"【乙奇入墓】{gong.gong_name}宮：不利出行")
        if tian == "丙" and gong_num == 6:  # 丙入乾
            findings.append(f"【丙奇入墓】{gong.gong_name}宮：光明被遮")
        if tian == "丁" and gong_num == 8:  # 丁入艮
            findings.append(f"【丁奇入墓】{gong.gong_name}宮：文書不利")
    
    # 值符值使判斷
    zhifu_gong = pan.gongs.get(pan.zhifu_gong)
    if zhifu_gong:
        if zhifu_gong.men in ["開", "休", "生"]:
            findings.append(f"【值符吉門】值符落{zhifu_gong.men}門，時機可行")
        elif zhifu_gong.men in ["死", "驚", "傷"]:
            findings.append(f"【值符凶門】值符落{zhifu_gong.men}門，宜緩不宜急")
    
    if not findings:
        findings.append("【平常格局】無特殊吉凶，依事論斷")
    
    return findings


# ===== 場論翻譯 =====
def field_translation(pan: QiMenPan) -> List[str]:
    """
    場論翻譯（描述性，不裁決）
    
    📐 將奇門結構翻譯為場論語言
    """
    findings = ["【場論視角】"]
    
    # 整體時空場
    if pan.is_yang:
        findings.append(f"時空場：陽遁{pan.ju_num}局，能量外放、適合主動出擊")
    else:
        findings.append(f"時空場：陰遁{pan.ju_num}局，能量收斂、適合守成謀劃")
    
    # 值符場（核心能量）
    zhifu_info = JIUXING_DETAIL.get(pan.zhifu_xing, {})
    findings.append(f"核心能量場（值符）：{pan.zhifu_xing}")
    findings.append(f"  特質：{zhifu_info.get('meaning', '無')}")
    
    # 值使場（執行通道）
    zhishi_info = BAMEN_DETAIL.get(pan.zhishi_men, {})
    findings.append(f"執行通道（值使）：{pan.zhishi_men}門")
    findings.append(f"  特質：{zhishi_info.get('meaning', '無')}")
    
    return findings


# ===== 主程式 =====
if __name__ == "__main__":
    print("=" * 60)
    print("奇門遁甲引擎 v1.0 測試")
    print("XTF任務: T8 | 執行星: 織明+理樞")
    print("=" * 60)
    
    # 測試：當前時間
    from datetime import datetime
    now = datetime(2026, 2, 6, 14, 0)  # 測試時間
    
    pan = create_qimen_pan(
        year=now.year,
        month=now.month,
        day=now.day,
        hour=now.hour,
        day_gan="丙"  # 需要實際計算，這裡假設
    )
    
    print(pan.summary())
    print()
    
    # 格局分析
    geju = analyze_geju(pan)
    print("【格局分析】")
    for g in geju:
        print(f"  {g}")
    print()
    
    # 場論翻譯
    field = field_translation(pan)
    for f in field:
        print(f)
