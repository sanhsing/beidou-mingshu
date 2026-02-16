#!/usr/bin/env python3
"""
北斗命數 農民曆濾網 v1.0
========================
每日宜忌 + 沖煞 + 十二建除 + 二十八宿

用於擇日系統的濾網：
- 嫁娶擇日：避開"忌嫁娶"
- 開業擇日：選"宜開市"
- 搬家擇日：選"宜入宅"

北斗七星文創 × 織明 | 2026-02-15
"""

from dataclasses import dataclass
from typing import List, Dict, Tuple
from datetime import date, timedelta

# ============================================================
# 十二建除（建除十二神）
# ============================================================
JIANCHU = ["建", "除", "滿", "平", "定", "執", "破", "危", "成", "收", "開", "閉"]

JIANCHU_MEANING = {
    "建": {"吉凶": "吉", "宜": ["出行", "上任", "會友"], "忌": ["動土", "開倉"]},
    "除": {"吉凶": "吉", "宜": ["祭祀", "解除", "醫病", "掃舍"], "忌": ["嫁娶", "遠行"]},
    "滿": {"吉凶": "吉", "宜": ["祈福", "結婚", "開市", "入宅"], "忌": ["動土", "服藥"]},
    "平": {"吉凶": "平", "宜": ["修路", "塗泥"], "忌": ["祈福", "求嗣", "嫁娶", "開市"]},
    "定": {"吉凶": "吉", "宜": ["祭祀", "嫁娶", "入宅", "修造"], "忌": ["訴訟", "出行"]},
    "執": {"吉凶": "平", "宜": ["祭祀", "捕捉", "收斂"], "忌": ["開市", "交易", "嫁娶"]},
    "破": {"吉凶": "凶", "宜": ["破土", "拆卸", "求醫"], "忌": ["嫁娶", "開市", "祈福"]},
    "危": {"吉凶": "凶", "宜": ["祭祀", "祈福"], "忌": ["登高", "出行", "嫁娶", "造屋"]},
    "成": {"吉凶": "吉", "宜": ["開市", "入學", "嫁娶", "開業"], "忌": ["訴訟"]},
    "收": {"吉凶": "吉", "宜": ["收斂", "嫁娶", "立券", "交易"], "忌": ["開市", "動土"]},
    "開": {"吉凶": "吉", "宜": ["開市", "開業", "嫁娶", "入宅", "出行"], "忌": ["下葬", "動土"]},
    "閉": {"吉凶": "凶", "宜": ["修倉", "築堤", "埋葬"], "忌": ["開市", "出行", "嫁娶", "開業"]},
}

# ============================================================
# 二十八宿
# ============================================================
ERSHIBA_XIU = [
    "角", "亢", "氐", "房", "心", "尾", "箕",  # 東方青龍
    "斗", "牛", "女", "虛", "危", "室", "壁",  # 北方玄武
    "奎", "婁", "胃", "昴", "畢", "觜", "參",  # 西方白虎
    "井", "鬼", "柳", "星", "張", "翼", "軫",  # 南方朱雀
]

XIU_JIXIONG = {
    "角": ("吉", "文昌吉星，利文事"),
    "亢": ("凶", "不宜嫁娶、開張"),
    "氐": ("吉", "利婚姻、交易"),
    "房": ("吉", "大吉，百事皆宜"),
    "心": ("凶", "不宜動土、建造"),
    "尾": ("吉", "利嫁娶、開市"),
    "箕": ("凶", "不宜遠行、交易"),
    "斗": ("吉", "利祈福、修造"),
    "牛": ("凶", "不宜嫁娶、出行"),
    "女": ("凶", "不宜嫁娶"),
    "虛": ("凶", "大凶，百事不宜"),
    "危": ("凶", "不宜建造、嫁娶"),
    "室": ("吉", "大吉，百事皆宜"),
    "壁": ("吉", "利文昌、開業"),
    "奎": ("吉", "利文事、嫁娶"),
    "婁": ("吉", "利牧養、嫁娶"),
    "胃": ("吉", "利嫁娶、開業"),
    "昴": ("凶", "不宜動土、嫁娶"),
    "畢": ("吉", "利祈福、嫁娶"),
    "觜": ("凶", "不宜建造、開張"),
    "參": ("凶", "不宜嫁娶、遠行"),
    "井": ("吉", "利開渠、建造"),
    "鬼": ("凶", "大凶，百事不宜"),
    "柳": ("凶", "不宜嫁娶、開市"),
    "星": ("吉", "利建造、開業"),
    "張": ("吉", "大吉，百事皆宜"),
    "翼": ("凶", "不宜嫁娶、出行"),
    "軫": ("吉", "利嫁娶、交易"),
}

# ============================================================
# 沖煞
# ============================================================
CHONG = {
    "子": "午", "丑": "未", "寅": "申", "卯": "酉",
    "辰": "戌", "巳": "亥", "午": "子", "未": "丑",
    "申": "寅", "酉": "卯", "戌": "辰", "亥": "巳",
}

SHENGXIAO = {
    "子": "鼠", "丑": "牛", "寅": "虎", "卯": "兔",
    "辰": "龍", "巳": "蛇", "午": "馬", "未": "羊",
    "申": "猴", "酉": "雞", "戌": "狗", "亥": "豬",
}

SHA_DIRECTION = {
    "子": "南", "丑": "東", "寅": "北", "卯": "西",
    "辰": "南", "巳": "東", "午": "北", "未": "西",
    "申": "南", "酉": "東", "戌": "北", "亥": "西",
}

# ============================================================
# 每日宜忌（簡化版，實際需要完整黃曆數據）
# ============================================================
ACTIVITIES = [
    "祭祀", "祈福", "求嗣", "開光", "出行", "解除", "動土", "安床",
    "開市", "交易", "立券", "掛匾", "入宅", "移徙", "安香", "開業",
    "嫁娶", "納采", "問名", "訂盟", "納婿", "冠笄", "安葬", "破土",
    "啟鑽", "除服", "成服", "修造", "豎柱", "上梁", "納財", "開倉",
    "造車", "開池", "裁衣", "經絡", "牧養", "理髮", "整手足甲",
]


@dataclass
class DayAlmanac:
    """每日農民曆"""
    date: date
    ganzhi: str
    jianchu: str
    jianchu_jixiong: str
    xiu: str
    xiu_jixiong: str
    chong: str
    sha: str
    yi: List[str]
    ji: List[str]
    overall: str  # 大吉/吉/平/凶/大凶


def calc_day_ganzhi(dt: date) -> str:
    """計算日干支"""
    year, month, day = dt.year, dt.month, dt.day
    if month <= 2:
        year -= 1
        month += 12
    
    a = year // 100
    b = 2 - a + a // 4
    jd = int(365.25 * (year + 4716)) + int(30.6001 * (month + 1)) + day + b - 1524
    
    base_jd = 2445336
    diff = jd - base_jd
    idx = diff % 60
    if idx < 0:
        idx += 60
    
    TIANGAN = ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"]
    DIZHI = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]
    
    return TIANGAN[idx % 10] + DIZHI[idx % 12]


def get_day_almanac(dt: date) -> DayAlmanac:
    """獲取某日農民曆"""
    ganzhi = calc_day_ganzhi(dt)
    zhi = ganzhi[1]
    
    # 計算建除（簡化：基於日支循環）
    zhi_idx = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"].index(zhi)
    # 實際需要考慮月建，這裡簡化
    jianchu_idx = (zhi_idx + dt.month) % 12
    jianchu = JIANCHU[jianchu_idx]
    jianchu_info = JIANCHU_MEANING[jianchu]
    
    # 計算二十八宿（簡化：基於日期循環）
    days_since_epoch = (dt - date(2000, 1, 1)).days
    xiu_idx = days_since_epoch % 28
    xiu = ERSHIBA_XIU[xiu_idx]
    xiu_info = XIU_JIXIONG[xiu]
    
    # 沖煞
    chong_zhi = CHONG[zhi]
    chong = f"沖{SHENGXIAO[chong_zhi]}({chong_zhi})"
    sha = f"煞{SHA_DIRECTION[zhi]}"
    
    # 宜忌
    yi = jianchu_info["宜"].copy()
    ji = jianchu_info["忌"].copy()
    
    # 根據二十八宿調整
    if xiu_info[0] == "凶":
        if "嫁娶" in yi:
            yi.remove("嫁娶")
        if "嫁娶" not in ji:
            ji.append("嫁娶")
    
    # 綜合評價
    jianchu_score = {"吉": 2, "平": 1, "凶": 0}[jianchu_info["吉凶"]]
    xiu_score = {"吉": 2, "凶": 0}[xiu_info[0]]
    total = jianchu_score + xiu_score
    
    if total >= 4:
        overall = "大吉"
    elif total >= 3:
        overall = "吉"
    elif total >= 2:
        overall = "平"
    elif total >= 1:
        overall = "凶"
    else:
        overall = "大凶"
    
    return DayAlmanac(
        date=dt,
        ganzhi=ganzhi,
        jianchu=jianchu,
        jianchu_jixiong=jianchu_info["吉凶"],
        xiu=xiu,
        xiu_jixiong=xiu_info[0],
        chong=chong,
        sha=sha,
        yi=yi,
        ji=ji,
        overall=overall
    )


def filter_dates_by_activity(
    start_date: date,
    days: int,
    activity: str,
    require_yi: bool = True
) -> List[DayAlmanac]:
    """
    按活動篩選日期
    
    activity: 要做的事（如 "嫁娶", "開市"）
    require_yi: True=必須在宜中, False=只要不在忌中
    """
    results = []
    current = start_date
    
    for _ in range(days):
        almanac = get_day_almanac(current)
        
        if require_yi:
            if activity in almanac.yi:
                results.append(almanac)
        else:
            if activity not in almanac.ji:
                results.append(almanac)
        
        current += timedelta(days=1)
    
    return results


# ============================================================
# 測試
# ============================================================
if __name__ == "__main__":
    print("=" * 60)
    print("         北斗命數 農民曆濾網 測試")
    print("=" * 60)
    
    # 查詢某日
    print("\n【單日查詢】2026-03-16")
    almanac = get_day_almanac(date(2026, 3, 16))
    print(f"  日期: {almanac.date}")
    print(f"  干支: {almanac.ganzhi}")
    print(f"  建除: {almanac.jianchu} ({almanac.jianchu_jixiong})")
    print(f"  二十八宿: {almanac.xiu} ({almanac.xiu_jixiong})")
    print(f"  {almanac.chong} {almanac.sha}")
    print(f"  宜: {', '.join(almanac.yi)}")
    print(f"  忌: {', '.join(almanac.ji)}")
    print(f"  綜合: {almanac.overall}")
    
    # 篩選嫁娶吉日
    print("\n【篩選嫁娶吉日】2026年3月")
    good_dates = filter_dates_by_activity(
        start_date=date(2026, 3, 1),
        days=31,
        activity="嫁娶",
        require_yi=True
    )
    print(f"  找到 {len(good_dates)} 個宜嫁娶日:")
    for d in good_dates[:5]:
        print(f"    {d.date} ({d.ganzhi}) {d.jianchu} {d.overall}")
    
    # 篩選開市吉日
    print("\n【篩選開市吉日】2026年3月")
    good_dates = filter_dates_by_activity(
        start_date=date(2026, 3, 1),
        days=31,
        activity="開市",
        require_yi=True
    )
    print(f"  找到 {len(good_dates)} 個宜開市日:")
    for d in good_dates[:5]:
        print(f"    {d.date} ({d.ganzhi}) {d.jianchu} {d.overall}")
    
    print("\n" + "=" * 60)
    print("✅ 農民曆濾網測試完成！")
    print("=" * 60)
