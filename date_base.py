#!/usr/bin/env python3
"""
date_base.py - 擇日擇時共用基礎模組
版本：v1.0.0

═══════════════════════════════════════════════════════════════════════
10 維度擇日體系：
  D1  黃道吉日     黃道/黑道十二神
  D2  十二建除     建除滿平定執破危成收開閉
  D3  二十八宿     東青龍/北玄武/西白虎/南朱雀
  D4  神煞         吉神/凶神
  D5  沖煞         生肖沖/方位煞
  D6  用事宜忌     依用事類型判斷
  D7  個人八字     與日課配合
  D8  時辰選擇     吉時/凶時
  D9  易經卦象     日期→卦象→吉凶
  D10 農民曆避忌   歲破/月破/四離四絕/楊公忌
═══════════════════════════════════════════════════════════════════════

PYLIB 依賴：無（獨立模組）
XTF8 層級：L0-L4
@織明 × @理樞
"""

from typing import Dict, List, Tuple, Optional, Set
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, date, timedelta
import math

# 嘗試導入農曆模組
try:
    from lunar_calendar_v2 import solar_to_lunar, LunarDate
    HAS_LUNAR = True
except ImportError:
    HAS_LUNAR = False
    LunarDate = None

# ════════════════════════════════════════════════════════════════════
# L0: 常量定義
# ════════════════════════════════════════════════════════════════════

# 天干
TIANGAN = ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"]
TIANGAN_WX = {"甲": "木", "乙": "木", "丙": "火", "丁": "火", "戊": "土",
              "己": "土", "庚": "金", "辛": "金", "壬": "水", "癸": "水"}

# 地支
DIZHI = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]
DIZHI_WX = {"子": "水", "丑": "土", "寅": "木", "卯": "木", "辰": "土", "巳": "火",
            "午": "火", "未": "土", "申": "金", "酉": "金", "戌": "土", "亥": "水"}

# 生肖
SHENGXIAO = ["鼠", "牛", "虎", "兔", "龍", "蛇", "馬", "羊", "猴", "雞", "狗", "豬"]

# 地支沖
DIZHI_CHONG = {
    "子": "午", "午": "子", "丑": "未", "未": "丑",
    "寅": "申", "申": "寅", "卯": "酉", "酉": "卯",
    "辰": "戌", "戌": "辰", "巳": "亥", "亥": "巳"
}

# 地支三合
DIZHI_SANHE = {
    "申子辰": "水", "寅午戌": "火", "巳酉丑": "金", "亥卯未": "木"
}

# 地支六合
DIZHI_LIUHE = {
    "子": "丑", "丑": "子", "寅": "亥", "亥": "寅",
    "卯": "戌", "戌": "卯", "辰": "酉", "酉": "辰",
    "巳": "申", "申": "巳", "午": "未", "未": "午"
}

# ════════════════════════════════════════════════════════════════════
# D1: 黃道吉日（黃道十二神）
# ════════════════════════════════════════════════════════════════════

# 黃道/黑道十二神
HUANGDAO_SHEN = {
    "青龍": {"type": "黃道", "score": 100, "desc": "百事吉利"},
    "明堂": {"type": "黃道", "score": 95, "desc": "貴人相助"},
    "金匱": {"type": "黃道", "score": 90, "desc": "財運亨通"},
    "天德": {"type": "黃道", "score": 95, "desc": "逢凶化吉"},
    "玉堂": {"type": "黃道", "score": 90, "desc": "榮華富貴"},
    "司命": {"type": "黃道", "score": 85, "desc": "壽祿雙全"},
    
    "天刑": {"type": "黑道", "score": 40, "desc": "官非口舌"},
    "朱雀": {"type": "黑道", "score": 45, "desc": "口舌是非"},
    "白虎": {"type": "黑道", "score": 35, "desc": "血光之災"},
    "天牢": {"type": "黑道", "score": 40, "desc": "牢獄之災"},
    "玄武": {"type": "黑道", "score": 45, "desc": "盜賊小人"},
    "勾陳": {"type": "黑道", "score": 50, "desc": "纏繞不清"},
}

# 黃道十二神輪值順序（依月建起）
HUANGDAO_ORDER = ["青龍", "明堂", "天刑", "朱雀", "金匱", "天德",
                  "白虎", "玉堂", "天牢", "玄武", "司命", "勾陳"]

def calc_huangdao(month_zhi: str, day_zhi: str) -> Tuple[str, int, str]:
    """
    計算黃道十二神
    
    月建起青龍，順數至日支
    """
    month_idx = DIZHI.index(month_zhi)
    day_idx = DIZHI.index(day_zhi)
    
    # 計算相差
    diff = (day_idx - month_idx) % 12
    
    shen = HUANGDAO_ORDER[diff]
    info = HUANGDAO_SHEN[shen]
    
    return shen, info["score"], info["desc"]


# ════════════════════════════════════════════════════════════════════
# D2: 十二建除
# ════════════════════════════════════════════════════════════════════

# 十二建除
JIANCHU = {
    "建": {"score": 70, "yi": ["祭祀", "祈福"], "ji": ["嫁娶", "動土"], "desc": "萬事可為，惟忌動土嫁娶"},
    "除": {"score": 85, "yi": ["祭祀", "解除", "求醫"], "ji": ["嫁娶", "遠行"], "desc": "除舊布新"},
    "滿": {"score": 80, "yi": ["祭祀", "祈福", "嫁娶"], "ji": ["動土", "造葬"], "desc": "圓滿之日"},
    "平": {"score": 75, "yi": ["祭祀", "修造"], "ji": ["嫁娶", "移徙"], "desc": "平常之日"},
    "定": {"score": 85, "yi": ["祭祀", "嫁娶", "造屋"], "ji": ["訴訟", "出行"], "desc": "安定之日"},
    "執": {"score": 65, "yi": ["祭祀", "捕捉"], "ji": ["嫁娶", "開市"], "desc": "執持之日"},
    "破": {"score": 30, "yi": ["破屋", "壞垣"], "ji": ["嫁娶", "開市", "動土"], "desc": "破敗之日"},
    "危": {"score": 60, "yi": ["祭祀", "安床"], "ji": ["登高", "行船"], "desc": "危險之日"},
    "成": {"score": 90, "yi": ["嫁娶", "開市", "動土", "造屋"], "ji": ["訴訟"], "desc": "成就之日"},
    "收": {"score": 80, "yi": ["祭祀", "收穫", "納財"], "ji": ["嫁娶", "開市"], "desc": "收成之日"},
    "開": {"score": 95, "yi": ["嫁娶", "開市", "動土", "造屋"], "ji": ["安葬"], "desc": "開通之日"},
    "閉": {"score": 40, "yi": ["祭祀", "閉戶"], "ji": ["嫁娶", "開市", "動土"], "desc": "閉塞之日"},
}

JIANCHU_ORDER = ["建", "除", "滿", "平", "定", "執", "破", "危", "成", "收", "開", "閉"]

def calc_jianchu(month_zhi: str, day_zhi: str) -> Tuple[str, int, List[str], List[str]]:
    """
    計算十二建除
    
    月建日為建，順推
    """
    month_idx = DIZHI.index(month_zhi)
    day_idx = DIZHI.index(day_zhi)
    
    diff = (day_idx - month_idx) % 12
    
    jc = JIANCHU_ORDER[diff]
    info = JIANCHU[jc]
    
    return jc, info["score"], info["yi"], info["ji"]


# ════════════════════════════════════════════════════════════════════
# D3: 二十八宿
# ════════════════════════════════════════════════════════════════════

# 二十八宿
ERSHIBA_XIU = {
    # 東方青龍七宿
    "角": {"fang": "東", "shen": "青龍", "score": 90, "yi": ["嫁娶", "開市"], "ji": []},
    "亢": {"fang": "東", "shen": "青龍", "score": 50, "yi": [], "ji": ["嫁娶", "動土"]},
    "氐": {"fang": "東", "shen": "青龍", "score": 85, "yi": ["嫁娶", "造屋"], "ji": []},
    "房": {"fang": "東", "shen": "青龍", "score": 95, "yi": ["嫁娶", "動土", "開市"], "ji": []},
    "心": {"fang": "東", "shen": "青龍", "score": 40, "yi": ["祭祀"], "ji": ["嫁娶", "動土"]},
    "尾": {"fang": "東", "shen": "青龍", "score": 85, "yi": ["嫁娶", "造屋"], "ji": []},
    "箕": {"fang": "東", "shen": "青龍", "score": 70, "yi": ["開市"], "ji": ["嫁娶"]},
    
    # 北方玄武七宿
    "斗": {"fang": "北", "shen": "玄武", "score": 85, "yi": ["開市", "動土"], "ji": []},
    "牛": {"fang": "北", "shen": "玄武", "score": 50, "yi": ["祭祀"], "ji": ["嫁娶", "動土"]},
    "女": {"fang": "北", "shen": "玄武", "score": 40, "yi": [], "ji": ["嫁娶", "開市"]},
    "虛": {"fang": "北", "shen": "玄武", "score": 60, "yi": ["祭祀"], "ji": ["嫁娶"]},
    "危": {"fang": "北", "shen": "玄武", "score": 70, "yi": ["祭祀"], "ji": ["動土"]},
    "室": {"fang": "北", "shen": "玄武", "score": 90, "yi": ["嫁娶", "動土", "開市"], "ji": []},
    "壁": {"fang": "北", "shen": "玄武", "score": 95, "yi": ["嫁娶", "動土", "開市"], "ji": []},
    
    # 西方白虎七宿
    "奎": {"fang": "西", "shen": "白虎", "score": 85, "yi": ["嫁娶", "造屋"], "ji": []},
    "婁": {"fang": "西", "shen": "白虎", "score": 90, "yi": ["嫁娶", "動土"], "ji": []},
    "胃": {"fang": "西", "shen": "白虎", "score": 75, "yi": ["開市"], "ji": ["嫁娶"]},
    "昴": {"fang": "西", "shen": "白虎", "score": 50, "yi": ["祭祀"], "ji": ["嫁娶", "動土"]},
    "畢": {"fang": "西", "shen": "白虎", "score": 85, "yi": ["嫁娶", "造屋"], "ji": []},
    "觜": {"fang": "西", "shen": "白虎", "score": 60, "yi": ["祭祀"], "ji": ["動土"]},
    "參": {"fang": "西", "shen": "白虎", "score": 80, "yi": ["開市"], "ji": ["嫁娶"]},
    
    # 南方朱雀七宿
    "井": {"fang": "南", "shen": "朱雀", "score": 85, "yi": ["嫁娶", "動土"], "ji": []},
    "鬼": {"fang": "南", "shen": "朱雀", "score": 40, "yi": ["祭祀"], "ji": ["嫁娶", "動土", "開市"]},
    "柳": {"fang": "南", "shen": "朱雀", "score": 45, "yi": [], "ji": ["嫁娶", "動土"]},
    "星": {"fang": "南", "shen": "朱雀", "score": 90, "yi": ["嫁娶", "動土"], "ji": []},
    "張": {"fang": "南", "shen": "朱雀", "score": 95, "yi": ["嫁娶", "動土", "開市"], "ji": []},
    "翼": {"fang": "南", "shen": "朱雀", "score": 50, "yi": ["祭祀"], "ji": ["嫁娶"]},
    "軫": {"fang": "南", "shen": "朱雀", "score": 85, "yi": ["嫁娶", "造屋"], "ji": []},
}

XIU_ORDER = ["角", "亢", "氐", "房", "心", "尾", "箕",
             "斗", "牛", "女", "虛", "危", "室", "壁",
             "奎", "婁", "胃", "昴", "畢", "觜", "參",
             "井", "鬼", "柳", "星", "張", "翼", "軫"]

def calc_xiu(day_idx: int) -> Tuple[str, int, str]:
    """
    計算二十八宿
    
    依日序循環
    """
    xiu = XIU_ORDER[day_idx % 28]
    info = ERSHIBA_XIU[xiu]
    
    return xiu, info["score"], f"{info['fang']}方{info['shen']}"


# ════════════════════════════════════════════════════════════════════
# D4: 神煞
# ════════════════════════════════════════════════════════════════════

# 吉神
JI_SHEN = {
    "天德": {"score": 20, "desc": "逢凶化吉"},
    "月德": {"score": 18, "desc": "諸事吉利"},
    "天德合": {"score": 15, "desc": "得貴人助"},
    "月德合": {"score": 12, "desc": "得貴人助"},
    "天赦": {"score": 25, "desc": "萬事大吉"},
    "天願": {"score": 15, "desc": "心想事成"},
    "月恩": {"score": 12, "desc": "受月恩庇"},
    "四相": {"score": 10, "desc": "四方吉利"},
    "時德": {"score": 10, "desc": "時來運轉"},
    "民日": {"score": 8, "desc": "利於民事"},
    "三合": {"score": 15, "desc": "三合吉慶"},
    "六合": {"score": 12, "desc": "六合和順"},
    "五合": {"score": 10, "desc": "五行相合"},
    "天喜": {"score": 15, "desc": "喜事臨門"},
    "天醫": {"score": 12, "desc": "利於求醫"},
    "母倉": {"score": 10, "desc": "利於納財"},
    "福生": {"score": 8, "desc": "福氣降臨"},
    "聖心": {"score": 8, "desc": "心靈相通"},
}

# 凶神
XIONG_SHEN = {
    "月破": {"score": -30, "desc": "大凶", "avoid": ["嫁娶", "動土", "開市"]},
    "歲破": {"score": -35, "desc": "大凶", "avoid": ["嫁娶", "動土", "開市"]},
    "月煞": {"score": -20, "desc": "凶", "avoid": ["嫁娶", "出行"]},
    "月刑": {"score": -15, "desc": "凶", "avoid": ["嫁娶", "動土"]},
    "月厭": {"score": -15, "desc": "凶", "avoid": ["嫁娶"]},
    "大耗": {"score": -18, "desc": "凶", "avoid": ["開市", "納財"]},
    "災煞": {"score": -20, "desc": "凶", "avoid": ["出行", "動土"]},
    "天火": {"score": -15, "desc": "凶", "avoid": ["動土", "造屋"]},
    "地火": {"score": -15, "desc": "凶", "avoid": ["動土", "造屋"]},
    "四廢": {"score": -20, "desc": "凶", "avoid": ["嫁娶", "動土", "開市"]},
    "五墓": {"score": -18, "desc": "凶", "avoid": ["嫁娶", "動土"]},
    "復日": {"score": -12, "desc": "凶", "avoid": ["嫁娶"]},
    "重日": {"score": -10, "desc": "小凶", "avoid": ["嫁娶"]},
    "朱雀": {"score": -12, "desc": "凶", "avoid": ["開市"]},
    "白虎": {"score": -15, "desc": "凶", "avoid": ["嫁娶", "動土"]},
    "天狗": {"score": -12, "desc": "凶", "avoid": ["祭祀"]},
    "勾陳": {"score": -10, "desc": "小凶", "avoid": ["訴訟"]},
}

def calc_shensha(year_gan: str, month_zhi: str, day_gan: str, day_zhi: str) -> Tuple[List[str], List[str], int]:
    """
    計算神煞（簡化版）
    
    返回：(吉神列表, 凶神列表, 總分調整)
    """
    ji_list = []
    xiong_list = []
    score_adj = 0
    
    # 天德：月支對應
    tiande_map = {"寅": "丙", "卯": "甲", "辰": "壬", "巳": "庚",
                  "午": "甲", "未": "壬", "申": "庚", "酉": "丙",
                  "戌": "甲", "亥": "壬", "子": "庚", "丑": "丙"}
    if tiande_map.get(month_zhi) == day_gan:
        ji_list.append("天德")
        score_adj += JI_SHEN["天德"]["score"]
    
    # 月德：月支對應
    yuede_map = {"寅午戌": "丙", "申子辰": "壬", "亥卯未": "甲", "巳酉丑": "庚"}
    for zhi_group, gan in yuede_map.items():
        if month_zhi in zhi_group and day_gan == gan:
            ji_list.append("月德")
            score_adj += JI_SHEN["月德"]["score"]
            break
    
    # 三合
    for sanhe, _ in DIZHI_SANHE.items():
        if day_zhi in sanhe and month_zhi in sanhe:
            ji_list.append("三合")
            score_adj += JI_SHEN["三合"]["score"]
            break
    
    # 六合
    if DIZHI_LIUHE.get(day_zhi) == month_zhi:
        ji_list.append("六合")
        score_adj += JI_SHEN["六合"]["score"]
    
    # 月破
    if DIZHI_CHONG.get(month_zhi) == day_zhi:
        xiong_list.append("月破")
        score_adj += XIONG_SHEN["月破"]["score"]
    
    return ji_list, xiong_list, score_adj


# ════════════════════════════════════════════════════════════════════
# D5: 沖煞
# ════════════════════════════════════════════════════════════════════

# 方位
FANGWEI = {
    "子": "北", "午": "南", "卯": "東", "酉": "西",
    "丑": "東北", "寅": "東北", "辰": "東南", "巳": "東南",
    "未": "西南", "申": "西南", "戌": "西北", "亥": "西北"
}

def calc_chongsha(day_zhi: str, person_zhi: str = None) -> Tuple[str, str, int, bool]:
    """
    計算沖煞
    
    返回：(沖生肖, 煞方位, 分數, 是否沖命主)
    """
    chong_zhi = DIZHI_CHONG[day_zhi]
    chong_sx = SHENGXIAO[DIZHI.index(chong_zhi)]
    sha_fang = FANGWEI[chong_zhi]
    
    # 是否沖命主
    chong_person = person_zhi == chong_zhi if person_zhi else False
    
    score = 80 if not chong_person else 30
    
    return chong_sx, sha_fang, score, chong_person


# ════════════════════════════════════════════════════════════════════
# D8: 時辰選擇
# ════════════════════════════════════════════════════════════════════

# 時辰
SHICHEN = {
    "子": {"start": 23, "end": 1, "name": "子時", "desc": "夜半"},
    "丑": {"start": 1, "end": 3, "name": "丑時", "desc": "雞鳴"},
    "寅": {"start": 3, "end": 5, "name": "寅時", "desc": "平旦"},
    "卯": {"start": 5, "end": 7, "name": "卯時", "desc": "日出"},
    "辰": {"start": 7, "end": 9, "name": "辰時", "desc": "食時"},
    "巳": {"start": 9, "end": 11, "name": "巳時", "desc": "隅中"},
    "午": {"start": 11, "end": 13, "name": "午時", "desc": "日中"},
    "未": {"start": 13, "end": 15, "name": "未時", "desc": "日昳"},
    "申": {"start": 15, "end": 17, "name": "申時", "desc": "晡時"},
    "酉": {"start": 17, "end": 19, "name": "酉時", "desc": "日入"},
    "戌": {"start": 19, "end": 21, "name": "戌時", "desc": "黃昏"},
    "亥": {"start": 21, "end": 23, "name": "亥時", "desc": "人定"},
}

# 日上起時（五鼠遁）
RIQISHI = {
    "甲己": "甲", "乙庚": "丙", "丙辛": "戊", "丁壬": "庚", "戊癸": "壬"
}

def calc_shichen_ganzhi(day_gan: str, hour_zhi: str) -> str:
    """計算時辰干支"""
    # 五鼠遁
    for key, start_gan in RIQISHI.items():
        if day_gan in key:
            start_idx = TIANGAN.index(start_gan)
            hour_idx = DIZHI.index(hour_zhi)
            gan = TIANGAN[(start_idx + hour_idx) % 10]
            return f"{gan}{hour_zhi}"
    return hour_zhi

def calc_jishi(day_zhi: str, month_zhi: str) -> List[Tuple[str, int, str]]:
    """
    計算吉時
    
    返回：[(時辰, 分數, 說明), ...]
    """
    results = []
    
    for zhi in DIZHI:
        score = 75  # 基準分
        notes = []
        
        # 與日支關係
        if DIZHI_LIUHE.get(zhi) == day_zhi:
            score += 15
            notes.append("六合")
        
        for sanhe in DIZHI_SANHE:
            if zhi in sanhe and day_zhi in sanhe:
                score += 10
                notes.append("三合")
                break
        
        if DIZHI_CHONG.get(zhi) == day_zhi:
            score -= 25
            notes.append("沖日")
        
        # 與月支關係
        if DIZHI_CHONG.get(zhi) == month_zhi:
            score -= 15
            notes.append("沖月")
        
        desc = "、".join(notes) if notes else "平"
        results.append((zhi, min(100, max(30, score)), desc))
    
    return results


# ════════════════════════════════════════════════════════════════════
# D9: 易經卦象
# ════════════════════════════════════════════════════════════════════

# 八卦
BAGUA = {
    1: ("乾", "☰", "天", 95), 2: ("兌", "☱", "澤", 85),
    3: ("離", "☲", "火", 80), 4: ("震", "☳", "雷", 75),
    5: ("巽", "☴", "風", 80), 6: ("坎", "☵", "水", 65),
    7: ("艮", "☶", "山", 70), 0: ("坤", "☷", "地", 90),
}

# 64卦簡易吉凶
GUA_JIXI = {
    "乾乾": ("乾為天", 95, "元亨利貞"),
    "坤坤": ("坤為地", 90, "厚德載物"),
    "乾坤": ("天地否", 40, "閉塞不通"),
    "坤乾": ("地天泰", 95, "天地交泰"),
    "離坎": ("火水未濟", 50, "將濟未濟"),
    "坎離": ("水火既濟", 90, "萬事亨通"),
}

def calc_yijing(year: int, month: int, day: int) -> Tuple[str, str, int, str]:
    """
    計算易經卦象
    
    返回：(卦名, 卦象, 分數, 說明)
    """
    # 上卦：年+月 除8
    shang = (year + month) % 8
    if shang == 0: shang = 8
    
    # 下卦：月+日 除8
    xia = (month + day) % 8
    if xia == 0: xia = 8
    
    # 動爻：年+月+日 除6
    dong = (year + month + day) % 6
    if dong == 0: dong = 6
    
    shang_info = BAGUA[shang % 8]
    xia_info = BAGUA[xia % 8]
    
    # 查卦辭
    key = shang_info[0] + xia_info[0]
    if key in GUA_JIXI:
        gua_name, score, desc = GUA_JIXI[key]
    else:
        # 一般計算
        score = (shang_info[3] + xia_info[3]) // 2
        gua_name = f"{shang_info[2]}{xia_info[2]}"
        desc = "卦象平常"
    
    gua_xiang = f"{shang_info[1]}{xia_info[1]}"
    
    return gua_name, gua_xiang, score, desc


# ════════════════════════════════════════════════════════════════════
# D10: 農民曆避忌
# ════════════════════════════════════════════════════════════════════

# 楊公十三忌（農曆日期）
YANGGONG_JI = [
    (1, 13), (2, 11), (3, 9), (4, 7), (5, 5), (6, 3),
    (7, 1), (7, 29), (8, 27), (9, 25), (10, 23), (11, 21), (12, 19)
]

# 月忌日
YUE_JI = [5, 14, 23]  # 初五、十四、廿三

# 四離日：立春夏秋冬前一日
# 四絕日：春分夏至秋分冬至前一日
# （需要節氣計算，此處簡化）

class AvoidType(Enum):
    """避忌類型"""
    SUI_PO = "歲破"
    YUE_PO = "月破"
    SI_LI = "四離"
    SI_JUE = "四絕"
    YANG_GONG = "楊公忌"
    YUE_JI = "月忌日"
    CHONG_SHA = "沖煞"

def check_avoid(lunar_month: int, lunar_day: int, year_zhi: str, 
                month_zhi: str, day_zhi: str) -> List[Tuple[AvoidType, str, int]]:
    """
    檢查農民曆避忌
    
    返回：[(避忌類型, 說明, 扣分), ...]
    """
    avoids = []
    
    # 楊公十三忌
    if (lunar_month, lunar_day) in YANGGONG_JI:
        avoids.append((AvoidType.YANG_GONG, f"楊公忌日（{lunar_month}月{lunar_day}日）", -30))
    
    # 月忌日
    if lunar_day in YUE_JI:
        avoids.append((AvoidType.YUE_JI, f"月忌日（初{lunar_day}）", -15))
    
    # 歲破（日支沖年支）
    if DIZHI_CHONG.get(day_zhi) == year_zhi:
        avoids.append((AvoidType.SUI_PO, f"歲破日（沖太歲{year_zhi}）", -35))
    
    # 月破（日支沖月支）
    if DIZHI_CHONG.get(day_zhi) == month_zhi:
        avoids.append((AvoidType.YUE_PO, f"月破日（沖月建{month_zhi}）", -30))
    
    return avoids


# ════════════════════════════════════════════════════════════════════
# L2: 資料結構
# ════════════════════════════════════════════════════════════════════

@dataclass
class DateScore:
    """日期評分"""
    # D1-D10 分數
    huangdao: int = 0       # D1
    jianchu: int = 0        # D2
    xiu: int = 0            # D3
    shensha: int = 0        # D4
    chongsha: int = 0       # D5
    yongshi: int = 0        # D6 用事宜忌
    bazi: int = 0           # D7 八字配合
    shichen: int = 0        # D8 時辰
    yijing: int = 0         # D9 易經
    avoid: int = 0          # D10 農民曆避忌
    
    raw_total: int = 0
    weighted_total: float = 0.0

# 10維度權重
DATE_WEIGHTS = {
    "huangdao": 1.2,   # D1
    "jianchu": 1.5,    # D2 核心
    "xiu": 1.0,        # D3
    "shensha": 1.2,    # D4
    "chongsha": 1.5,   # D5 核心
    "yongshi": 1.5,    # D6 核心
    "bazi": 1.2,       # D7
    "shichen": 1.0,    # D8
    "yijing": 0.5,     # D9 參考
    "avoid": 1.5,      # D10 核心（負分）
}

@dataclass
class DateCandidate:
    """候選日期"""
    date: date
    ganzhi: str           # 日干支
    lunar: str            # 農曆
    
    huangdao_shen: str = ""
    jianchu: str = ""
    xiu: str = ""
    ji_shen: List[str] = field(default_factory=list)
    xiong_shen: List[str] = field(default_factory=list)
    chong_sx: str = ""
    sha_fang: str = ""
    gua_name: str = ""
    avoids: List[str] = field(default_factory=list)
    
    yi: List[str] = field(default_factory=list)
    ji: List[str] = field(default_factory=list)
    
    score: DateScore = field(default_factory=DateScore)
    
    jishi: List[Tuple[str, int]] = field(default_factory=list)  # 吉時


# ════════════════════════════════════════════════════════════════════
# L3: 核心類
# ════════════════════════════════════════════════════════════════════

class DateSelector:
    """
    擇日擇時選擇器（基類）
    
    子類：MarryDateSelector, GroundDateSelector
    """
    
    def __init__(self, use_type: str = "通用"):
        self.use_type = use_type
        self.candidates: List[DateCandidate] = []
    
    def analyze_date(self, d: date, year_gz: str, month_gz: str, 
                     day_gz: str, lunar_month: int, lunar_day: int,
                     person_zhi: str = None) -> DateCandidate:
        """
        分析單一日期
        """
        year_zhi = year_gz[1] if len(year_gz) >= 2 else "子"
        month_zhi = month_gz[1] if len(month_gz) >= 2 else "寅"
        day_gan = day_gz[0] if day_gz else "甲"
        day_zhi = day_gz[1] if len(day_gz) >= 2 else "子"
        
        cand = DateCandidate(
            date=d,
            ganzhi=day_gz,
            lunar=f"{lunar_month}月{lunar_day}日"
        )
        
        # D1: 黃道吉日
        shen, score1, desc1 = calc_huangdao(month_zhi, day_zhi)
        cand.huangdao_shen = shen
        cand.score.huangdao = score1
        
        # D2: 十二建除
        jc, score2, yi, ji = calc_jianchu(month_zhi, day_zhi)
        cand.jianchu = jc
        cand.score.jianchu = score2
        cand.yi = yi
        cand.ji = ji
        
        # D3: 二十八宿
        day_idx = d.toordinal()  # 簡化
        xiu, score3, xiu_desc = calc_xiu(day_idx)
        cand.xiu = xiu
        cand.score.xiu = score3
        
        # D4: 神煞
        ji_shen, xiong_shen, score4 = calc_shensha(year_gz[0], month_zhi, day_gan, day_zhi)
        cand.ji_shen = ji_shen
        cand.xiong_shen = xiong_shen
        cand.score.shensha = 75 + score4  # 基準分 + 調整
        
        # D5: 沖煞
        chong_sx, sha_fang, score5, chong_person = calc_chongsha(day_zhi, person_zhi)
        cand.chong_sx = chong_sx
        cand.sha_fang = sha_fang
        cand.score.chongsha = score5
        
        # D6: 用事宜忌（由子類實現）
        cand.score.yongshi = self._calc_yongshi(cand)
        
        # D7: 八字配合（由子類實現）
        cand.score.bazi = self._calc_bazi(cand, person_zhi)
        
        # D8: 時辰
        jishi = calc_jishi(day_zhi, month_zhi)
        cand.jishi = [(z, s) for z, s, _ in jishi if s >= 80]
        cand.score.shichen = max([s for _, s, _ in jishi]) if jishi else 75
        
        # D9: 易經
        gua_name, gua_xiang, score9, gua_desc = calc_yijing(d.year, d.month, d.day)
        cand.gua_name = gua_name
        cand.score.yijing = score9
        
        # D10: 農民曆避忌
        avoids = check_avoid(lunar_month, lunar_day, year_zhi, month_zhi, day_zhi)
        cand.avoids = [desc for _, desc, _ in avoids]
        avoid_score = sum([s for _, _, s in avoids])
        cand.score.avoid = 100 + avoid_score  # 基準100，有避忌則扣分
        
        # 計算總分
        self._calc_total(cand)
        
        return cand
    
    def _calc_yongshi(self, cand: DateCandidate) -> int:
        """計算用事宜忌分數（子類覆寫）"""
        return 75
    
    def _calc_bazi(self, cand: DateCandidate, person_zhi: str) -> int:
        """計算八字配合分數（子類覆寫）"""
        return 75
    
    def _calc_total(self, cand: DateCandidate):
        """計算總分"""
        s = cand.score
        
        s.raw_total = (s.huangdao + s.jianchu + s.xiu + s.shensha + 
                       s.chongsha + s.yongshi + s.bazi + s.shichen + 
                       s.yijing + s.avoid)
        
        s.weighted_total = (
            s.huangdao * DATE_WEIGHTS["huangdao"] +
            s.jianchu * DATE_WEIGHTS["jianchu"] +
            s.xiu * DATE_WEIGHTS["xiu"] +
            s.shensha * DATE_WEIGHTS["shensha"] +
            s.chongsha * DATE_WEIGHTS["chongsha"] +
            s.yongshi * DATE_WEIGHTS["yongshi"] +
            s.bazi * DATE_WEIGHTS["bazi"] +
            s.shichen * DATE_WEIGHTS["shichen"] +
            s.yijing * DATE_WEIGHTS["yijing"] +
            s.avoid * DATE_WEIGHTS["avoid"]
        )
    
    def print_candidate(self, cand: DateCandidate):
        """輸出候選日期"""
        s = cand.score
        print(f"""
  【{cand.date}】{cand.ganzhi}（農曆{cand.lunar}）
  
    黃道：{cand.huangdao_shen}（{s.huangdao}分）
    建除：{cand.jianchu}（{s.jianchu}分）
    二十八宿：{cand.xiu}（{s.xiu}分）
    吉神：{', '.join(cand.ji_shen) if cand.ji_shen else '無'}
    凶神：{', '.join(cand.xiong_shen) if cand.xiong_shen else '無'}
    沖煞：沖{cand.chong_sx}，煞{cand.sha_fang}
    卦象：{cand.gua_name}（{s.yijing}分）
    避忌：{', '.join(cand.avoids) if cand.avoids else '無'}
    
    宜：{', '.join(cand.yi)}
    忌：{', '.join(cand.ji)}
    
    吉時：{', '.join([f'{z}時' for z, _ in cand.jishi[:4]])}
    
    加權總分：{s.weighted_total:.1f}
        """)


# ════════════════════════════════════════════════════════════════════
# L4: 便捷函數
# ════════════════════════════════════════════════════════════════════

def get_ganzhi_from_date(d: date) -> Tuple[str, str, str]:
    """
    從日期計算干支
    
    返回：(年干支, 月干支, 日干支)
    """
    # 優先使用農曆模組
    if HAS_LUNAR:
        try:
            lunar = solar_to_lunar(d.year, d.month, d.day)
            year_gz = f"{lunar.year_gan}{lunar.year_zhi}"
            month_gz = f"{lunar.month_gan}{lunar.month_zhi}"
            day_gz = f"{lunar.day_gan}{lunar.day_zhi}"
            return year_gz, month_gz, day_gz
        except:
            pass
    
    # 備用：簡化計算
    # 日干支（以1900年1月31日為甲辰日起算）
    base_date = date(1900, 1, 31)
    diff = (d - base_date).days
    day_gan = TIANGAN[diff % 10]
    day_zhi = DIZHI[diff % 12]
    
    # 年干支（以1984年為甲子年）
    year_diff = d.year - 1984
    year_gan = TIANGAN[year_diff % 10]
    year_zhi = DIZHI[year_diff % 12]
    
    # 月干支（簡化）
    month_idx = (d.month + 1) % 12
    month_zhi = DIZHI[month_idx]
    month_gan = TIANGAN[(TIANGAN.index(year_gan) * 2 + month_idx) % 10]
    
    return f"{year_gan}{year_zhi}", f"{month_gan}{month_zhi}", f"{day_gan}{day_zhi}"


def get_lunar_info(d: date) -> Optional[dict]:
    """
    獲取完整農曆資訊
    
    Returns:
        dict: {year, month, day, is_leap, year_gz, month_gz, day_gz, shengxiao}
    """
    if not HAS_LUNAR:
        return None
    
    try:
        lunar = solar_to_lunar(d.year, d.month, d.day)
        return {
            "year": lunar.year,
            "month": lunar.month,
            "day": lunar.day,
            "is_leap": lunar.is_leap,
            "year_gz": f"{lunar.year_gan}{lunar.year_zhi}",
            "month_gz": f"{lunar.month_gan}{lunar.month_zhi}",
            "day_gz": f"{lunar.day_gan}{lunar.day_zhi}",
            "shengxiao": lunar.shengxiao,
        }
    except:
        return None


# ════════════════════════════════════════════════════════════════════
# L4+: 完整日課四柱
# ════════════════════════════════════════════════════════════════════

# 五鼠遁：日上起時
RIQISHI = {
    "甲己": "甲", "乙庚": "丙", "丙辛": "戊", "丁壬": "庚", "戊癸": "壬"
}

def calc_shichen_ganzhi(day_gan: str, hour_zhi: str) -> str:
    """
    計算時柱干支（五鼠遁）
    
    Args:
        day_gan: 日干
        hour_zhi: 時辰地支
    
    Returns:
        時柱干支，如 "甲子"
    """
    for key, start_gan in RIQISHI.items():
        if day_gan in key:
            start_idx = TIANGAN.index(start_gan)
            hour_idx = DIZHI.index(hour_zhi)
            gan = TIANGAN[(start_idx + hour_idx) % 10]
            return f"{gan}{hour_zhi}"
    return hour_zhi

@dataclass
class FullRike:
    """完整日課"""
    date: date
    year_gz: str = ""
    month_gz: str = ""
    day_gz: str = ""
    hour_gz: str = ""
    hour_score: int = 0
    
    # 吉時列表 [(地支, 干支, 分數), ...]
    jishi_list: List[Tuple[str, str, int]] = field(default_factory=list)
    
    @property
    def full_rike(self) -> str:
        """完整四柱字串"""
        return f"{self.year_gz} {self.month_gz} {self.day_gz} {self.hour_gz}"
    
    @property
    def hour_name(self) -> str:
        """時辰名稱"""
        if self.hour_gz and len(self.hour_gz) >= 2:
            zhi = self.hour_gz[1]
            return SHICHEN.get(zhi, {}).get("name", f"{zhi}時")
        return ""

def get_full_rike(d: date, hour_zhi: str = None) -> FullRike:
    """
    獲取完整日課四柱
    
    Args:
        d: 日期
        hour_zhi: 時辰地支（可選，不提供則選擇最佳時辰）
    
    Returns:
        FullRike 完整日課資訊
    """
    year_gz, month_gz, day_gz = get_ganzhi_from_date(d)
    month_zhi = month_gz[1] if len(month_gz) >= 2 else "寅"
    day_gan = day_gz[0] if day_gz else "甲"
    day_zhi = day_gz[1] if len(day_gz) >= 2 else "子"
    
    # 計算所有時辰
    jishi_raw = calc_jishi(day_zhi, month_zhi)
    
    # 轉換為 (地支, 干支, 分數)
    jishi_list = [(z, calc_shichen_ganzhi(day_gan, z), s) 
                  for z, s, _ in jishi_raw if s >= 70]
    
    # 如果指定時辰
    if hour_zhi:
        hour_gz = calc_shichen_ganzhi(day_gan, hour_zhi)
        hour_score = next((s for z, s, _ in jishi_raw if z == hour_zhi), 75)
    else:
        # 找最佳時辰
        best = max(jishi_raw, key=lambda x: x[1])
        hour_zhi = best[0]
        hour_score = best[1]
        hour_gz = calc_shichen_ganzhi(day_gan, hour_zhi)
    
    return FullRike(
        date=d,
        year_gz=year_gz,
        month_gz=month_gz,
        day_gz=day_gz,
        hour_gz=hour_gz,
        hour_score=hour_score,
        jishi_list=jishi_list
    )

def print_full_rike(rike: FullRike, title: str = "完整日課"):
    """輸出完整日課"""
    print(f"\n  【{title}】{rike.date}")
    print(f"    年柱：{rike.year_gz}")
    print(f"    月柱：{rike.month_gz}")
    print(f"    日柱：{rike.day_gz}")
    print(f"    時柱：{rike.hour_gz}（{rike.hour_name}，{rike.hour_score}分）")
    print(f"\n    四柱：{rike.full_rike}")
    
    if rike.jishi_list:
        print(f"\n  【吉時選項】")
        for zhi, gz, score in rike.jishi_list[:6]:
            mark = "★" if gz == rike.hour_gz else " "
            print(f"    {mark} {zhi}時（{gz}）：{score}分")


# ════════════════════════════════════════════════════════════════════
# 測試
# ════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("═" * 70)
    print("        擇日擇時共用基礎模組 - 測試")
    print("═" * 70)
    
    # 測試日期
    test_date = date(2025, 3, 15)
    year_gz, month_gz, day_gz = get_ganzhi_from_date(test_date)
    
    print(f"\n  測試日期：{test_date}")
    print(f"  干支：{year_gz}年 {month_gz}月 {day_gz}日")
    
    # 測試各維度
    print("\n【D1 黃道吉日】")
    shen, score, desc = calc_huangdao(month_gz[1], day_gz[1])
    print(f"  {shen}（{score}分）：{desc}")
    
    print("\n【D2 十二建除】")
    jc, score, yi, ji = calc_jianchu(month_gz[1], day_gz[1])
    print(f"  {jc}（{score}分）")
    print(f"  宜：{yi}")
    print(f"  忌：{ji}")
    
    print("\n【D5 沖煞】")
    chong_sx, sha_fang, score, _ = calc_chongsha(day_gz[1])
    print(f"  沖{chong_sx}，煞{sha_fang}（{score}分）")
    
    print("\n【D8 吉時】")
    jishi = calc_jishi(day_gz[1], month_gz[1])
    for z, s, desc in jishi[:4]:
        print(f"  {z}時：{s}分（{desc}）")
    
    print("\n【D9 易經卦象】")
    gua_name, gua_xiang, score, desc = calc_yijing(test_date.year, test_date.month, test_date.day)
    print(f"  {gua_name} {gua_xiang}（{score}分）：{desc}")
    
    print("\n" + "═" * 70)
