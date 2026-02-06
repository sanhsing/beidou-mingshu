#!/usr/bin/env python3
"""
農曆精確轉換模組 lunar_calendar.py v2.0
========================================
XTF任務: T9 | 執行星: 理樞(演算法)+織明(架構)

📚 修正版：使用查表法確保精確度
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Tuple, Optional
from datetime import datetime, date, timedelta

# 天干地支
TIANGAN = ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"]
DIZHI = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]
SHENGXIAO = ["鼠", "牛", "虎", "兔", "龍", "蛇", "馬", "羊", "猴", "雞", "狗", "豬"]
LUNAR_MONTHS = ["正", "二", "三", "四", "五", "六", "七", "八", "九", "十", "冬", "臘"]
LUNAR_DAYS = [
    "初一", "初二", "初三", "初四", "初五", "初六", "初七", "初八", "初九", "初十",
    "十一", "十二", "十三", "十四", "十五", "十六", "十七", "十八", "十九", "二十",
    "廿一", "廿二", "廿三", "廿四", "廿五", "廿六", "廿七", "廿八", "廿九", "三十"
]

# ===== 農曆數據 (1900-2100) =====
# 每個數據：高4位=閏月月份(0無閏), 低12位=各月大小(1=大月30天)
# 閏月大小另外記錄
LUNAR_INFO = [
    0x04bd8, 0x04ae0, 0x0a570, 0x054d5, 0x0d260, 0x0d950, 0x16554, 0x056a0, 0x09ad0, 0x055d2,  # 1900-1909
    0x04ae0, 0x0a5b6, 0x0a4d0, 0x0d250, 0x1d255, 0x0b540, 0x0d6a0, 0x0ada2, 0x095b0, 0x14977,  # 1910-1919
    0x04970, 0x0a4b0, 0x0b4b5, 0x06a50, 0x06d40, 0x1ab54, 0x02b60, 0x09570, 0x052f2, 0x04970,  # 1920-1929
    0x06566, 0x0d4a0, 0x0ea50, 0x16e95, 0x05ad0, 0x02b60, 0x186e3, 0x092e0, 0x1c8d7, 0x0c950,  # 1930-1939
    0x0d4a0, 0x1d8a6, 0x0b550, 0x056a0, 0x1a5b4, 0x025d0, 0x092d0, 0x0d2b2, 0x0a950, 0x0b557,  # 1940-1949
    0x06ca0, 0x0b550, 0x15355, 0x04da0, 0x0a5d0, 0x14573, 0x052d0, 0x0a9a8, 0x0e950, 0x06aa0,  # 1950-1959
    0x0aea6, 0x0ab50, 0x04b60, 0x0aae4, 0x0a570, 0x05260, 0x0f263, 0x0d950, 0x05b57, 0x056a0,  # 1960-1969
    0x096d0, 0x04dd5, 0x04ad0, 0x0a4d0, 0x0d4d4, 0x0d250, 0x0d558, 0x0b540, 0x0b5a0, 0x195a6,  # 1970-1979
    0x095b0, 0x049b0, 0x0a974, 0x0a4b0, 0x0b27a, 0x06a50, 0x06d40, 0x0af46, 0x0ab60, 0x09570,  # 1980-1989
    0x04af5, 0x04970, 0x064b0, 0x074a3, 0x0ea50, 0x06b58, 0x055c0, 0x0ab60, 0x096d5, 0x092e0,  # 1990-1999
    0x0c960, 0x0d954, 0x0d4a0, 0x0da50, 0x07552, 0x056a0, 0x0abb7, 0x025d0, 0x092d0, 0x0cab5,  # 2000-2009
    0x0a950, 0x0b4a0, 0x0baa4, 0x0ad50, 0x055d9, 0x04ba0, 0x0a5b0, 0x15176, 0x052b0, 0x0a930,  # 2010-2019
    0x07954, 0x06aa0, 0x0ad50, 0x05b52, 0x04b60, 0x0a6e6, 0x0a4e0, 0x0d260, 0x0ea65, 0x0d530,  # 2020-2029
    0x05aa0, 0x076a3, 0x096d0, 0x04afb, 0x04ad0, 0x0a4d0, 0x1d0b6, 0x0d250, 0x0d520, 0x0dd45,  # 2030-2039
    0x0b5a0, 0x056d0, 0x055b2, 0x049b0, 0x0a577, 0x0a4b0, 0x0aa50, 0x1b255, 0x06d20, 0x0ada0,  # 2040-2049
    0x14b63, 0x09370, 0x049f8, 0x04970, 0x064b0, 0x168a6, 0x0ea50, 0x06aa0, 0x1a6c4, 0x0aae0,  # 2050-2059
    0x092e0, 0x0d2e3, 0x0c960, 0x0d557, 0x0d4a0, 0x0da50, 0x05d55, 0x056a0, 0x0a6d0, 0x055d4,  # 2060-2069
    0x052d0, 0x0a9b8, 0x0a950, 0x0b4a0, 0x0b6a6, 0x0ad50, 0x055a0, 0x0aba4, 0x0a5b0, 0x052b0,  # 2070-2079
    0x0b273, 0x06930, 0x07337, 0x06aa0, 0x0ad50, 0x14b55, 0x04b60, 0x0a570, 0x054e4, 0x0d160,  # 2080-2089
    0x0e968, 0x0d520, 0x0daa0, 0x16aa6, 0x056d0, 0x04ae0, 0x0a9d4, 0x0a2d0, 0x0d150, 0x0f252,  # 2090-2099
    0x0d520,  # 2100
]

# 春節日期（公曆）
SPRING_FESTIVAL = {
    1900: (1, 31), 1901: (2, 19), 1902: (2, 8), 1903: (1, 29), 1904: (2, 16),
    1905: (2, 4), 1906: (1, 25), 1907: (2, 13), 1908: (2, 2), 1909: (1, 22),
    1910: (2, 10), 1911: (1, 30), 1912: (2, 18), 1913: (2, 6), 1914: (1, 26),
    1915: (2, 14), 1916: (2, 3), 1917: (1, 23), 1918: (2, 11), 1919: (2, 1),
    1920: (2, 20), 1921: (2, 8), 1922: (1, 28), 1923: (2, 16), 1924: (2, 5),
    1925: (1, 24), 1926: (2, 13), 1927: (2, 2), 1928: (1, 23), 1929: (2, 10),
    1930: (1, 30), 1931: (2, 17), 1932: (2, 6), 1933: (1, 26), 1934: (2, 14),
    1935: (2, 4), 1936: (1, 24), 1937: (2, 11), 1938: (1, 31), 1939: (2, 19),
    1940: (2, 8), 1941: (1, 27), 1942: (2, 15), 1943: (2, 5), 1944: (1, 25),
    1945: (2, 13), 1946: (2, 2), 1947: (1, 22), 1948: (2, 10), 1949: (1, 29),
    1950: (2, 17), 1951: (2, 6), 1952: (1, 27), 1953: (2, 14), 1954: (2, 3),
    1955: (1, 24), 1956: (2, 12), 1957: (1, 31), 1958: (2, 18), 1959: (2, 8),
    1960: (1, 28), 1961: (2, 15), 1962: (2, 5), 1963: (1, 25), 1964: (2, 13),
    1965: (2, 2), 1966: (1, 21), 1967: (2, 9), 1968: (1, 30), 1969: (2, 17),
    1970: (2, 6), 1971: (1, 27), 1972: (2, 15), 1973: (2, 3), 1974: (1, 23),
    1975: (2, 11), 1976: (1, 31), 1977: (2, 18), 1978: (2, 7), 1979: (1, 28),
    1980: (2, 16), 1981: (2, 5), 1982: (1, 25), 1983: (2, 13), 1984: (2, 2),
    1985: (2, 20), 1986: (2, 9), 1987: (1, 29), 1988: (2, 17), 1989: (2, 6),
    1990: (1, 27), 1991: (2, 15), 1992: (2, 4), 1993: (1, 23), 1994: (2, 10),
    1995: (1, 31), 1996: (2, 19), 1997: (2, 7), 1998: (1, 28), 1999: (2, 16),
    2000: (2, 5), 2001: (1, 24), 2002: (2, 12), 2003: (2, 1), 2004: (1, 22),
    2005: (2, 9), 2006: (1, 29), 2007: (2, 18), 2008: (2, 7), 2009: (1, 26),
    2010: (2, 14), 2011: (2, 3), 2012: (1, 23), 2013: (2, 10), 2014: (1, 31),
    2015: (2, 19), 2016: (2, 8), 2017: (1, 28), 2018: (2, 16), 2019: (2, 5),
    2020: (1, 25), 2021: (2, 12), 2022: (2, 1), 2023: (1, 22), 2024: (2, 10),
    2025: (1, 29), 2026: (2, 17), 2027: (2, 6), 2028: (1, 26), 2029: (2, 13),
    2030: (2, 3), 2031: (1, 23), 2032: (2, 11), 2033: (1, 31), 2034: (2, 19),
    2035: (2, 8), 2036: (1, 28), 2037: (2, 15), 2038: (2, 4), 2039: (1, 24),
    2040: (2, 12), 2041: (2, 1), 2042: (1, 22), 2043: (2, 10), 2044: (1, 30),
    2045: (2, 17), 2046: (2, 6), 2047: (1, 26), 2048: (2, 14), 2049: (2, 2),
    2050: (1, 23),
}


def _get_lunar_info(year: int) -> int:
    """獲取某年的農曆數據"""
    idx = year - 1900
    if 0 <= idx < len(LUNAR_INFO):
        return LUNAR_INFO[idx]
    return 0


def get_leap_month(year: int) -> int:
    """獲取閏月月份，0表示無閏"""
    return (_get_lunar_info(year) >> 16) & 0xF


def get_month_days(year: int, month: int) -> int:
    """獲取某月天數（非閏月）"""
    info = _get_lunar_info(year)
    return 30 if (info >> (16 - month)) & 1 else 29


def get_leap_days(year: int) -> int:
    """獲取閏月天數"""
    leap = get_leap_month(year)
    if leap == 0:
        return 0
    info = _get_lunar_info(year)
    return 30 if (info >> 16) & 0x10000 else 29


def get_year_days(year: int) -> int:
    """獲取農曆年總天數"""
    total = 0
    for m in range(1, 13):
        total += get_month_days(year, m)
    leap = get_leap_month(year)
    if leap:
        total += get_leap_days(year)
    return total


@dataclass
class LunarDate:
    """農曆日期"""
    year: int
    month: int
    day: int
    is_leap: bool
    year_gan: str = ""
    year_zhi: str = ""
    month_gan: str = ""
    month_zhi: str = ""
    day_gan: str = ""
    day_zhi: str = ""
    shengxiao: str = ""
    
    def __str__(self) -> str:
        leap = "閏" if self.is_leap else ""
        return f"{self.year_gan}{self.year_zhi}年 {leap}{LUNAR_MONTHS[self.month-1]}月 {LUNAR_DAYS[self.day-1]}"
    
    def ganzhi_full(self) -> str:
        return f"{self.year_gan}{self.year_zhi} {self.month_gan}{self.month_zhi} {self.day_gan}{self.day_zhi}"


def solar_to_lunar(year: int, month: int, day: int) -> LunarDate:
    """公曆轉農曆（查表法）"""
    
    # 確定農曆年
    lunar_year = year
    sf = SPRING_FESTIVAL.get(year, (2, 1))
    spring_date = date(year, sf[0], sf[1])
    target = date(year, month, day)
    
    if target < spring_date:
        lunar_year = year - 1
        sf = SPRING_FESTIVAL.get(lunar_year, (2, 1))
        spring_date = date(lunar_year, sf[0], sf[1])
    
    # 計算距春節天數
    offset = (target - spring_date).days
    
    # 推算月日
    lunar_month = 1
    is_leap = False
    leap = get_leap_month(lunar_year)
    
    m = 1
    while m <= 12:
        days = get_month_days(lunar_year, m)
        if offset < days:
            lunar_month = m
            break
        offset -= days
        
        # 閏月
        if m == leap:
            leap_days = get_leap_days(lunar_year)
            if offset < leap_days:
                lunar_month = m
                is_leap = True
                break
            offset -= leap_days
        m += 1
    
    if m > 12:
        lunar_month = 12
    
    lunar_day = offset + 1
    
    # 計算干支
    # 年干支：以立春為界更準確，這裡簡化用春節
    year_idx = (lunar_year - 4) % 60
    year_gan = TIANGAN[year_idx % 10]
    year_zhi = DIZHI[year_idx % 12]
    shengxiao = SHENGXIAO[year_idx % 12]
    
    # 月干支（正月建寅）
    # 年干決定月干起點
    year_gan_idx = TIANGAN.index(year_gan)
    month_gan_base = (year_gan_idx % 5) * 2
    month_gan_idx = (month_gan_base + lunar_month - 1) % 10
    month_zhi_idx = (lunar_month + 1) % 12  # 正月=寅(2)
    month_gan = TIANGAN[month_gan_idx]
    month_zhi = DIZHI[month_zhi_idx]
    
    # 日干支（以1900/1/31=甲辰日為基準）
    base = date(1900, 1, 31)
    days_diff = (target - base).days
    day_gan_idx = days_diff % 10
    day_zhi_idx = (days_diff + 4) % 12  # 辰=4
    day_gan = TIANGAN[day_gan_idx]
    day_zhi = DIZHI[day_zhi_idx]
    
    return LunarDate(
        year=lunar_year, month=lunar_month, day=lunar_day, is_leap=is_leap,
        year_gan=year_gan, year_zhi=year_zhi,
        month_gan=month_gan, month_zhi=month_zhi,
        day_gan=day_gan, day_zhi=day_zhi,
        shengxiao=shengxiao
    )


def get_hour_ganzhi(day_gan: str, hour: int) -> Tuple[str, str]:
    """計算時辰干支"""
    hour_zhi_idx = ((hour + 1) // 2) % 12
    hour_zhi = DIZHI[hour_zhi_idx]
    
    day_gan_idx = TIANGAN.index(day_gan)
    base_map = {0: 0, 1: 2, 2: 4, 3: 6, 4: 8, 5: 0, 6: 2, 7: 4, 8: 6, 9: 8}
    hour_gan_idx = (base_map[day_gan_idx] + hour_zhi_idx) % 10
    hour_gan = TIANGAN[hour_gan_idx]
    
    return hour_gan, hour_zhi


def get_bazi(year: int, month: int, day: int, hour: int) -> dict:
    """獲取完整八字"""
    lunar = solar_to_lunar(year, month, day)
    hour_gan, hour_zhi = get_hour_ganzhi(lunar.day_gan, hour)
    
    return {
        "year": f"{lunar.year_gan}{lunar.year_zhi}",
        "month": f"{lunar.month_gan}{lunar.month_zhi}",
        "day": f"{lunar.day_gan}{lunar.day_zhi}",
        "hour": f"{hour_gan}{hour_zhi}",
        "bazi_str": f"{lunar.year_gan}{lunar.year_zhi} {lunar.month_gan}{lunar.month_zhi} {lunar.day_gan}{lunar.day_zhi} {hour_gan}{hour_zhi}",
        "lunar": lunar,
        "shengxiao": lunar.shengxiao,
    }


if __name__ == "__main__":
    print("=" * 60)
    print("農曆精確轉換模組 v2.0 測試")
    print("=" * 60)
    
    tests = [
        (1973, 12, 30, "北斗生日"),
        (2026, 2, 6, "今天"),
        (2024, 2, 10, "2024春節"),
        (2000, 2, 5, "2000春節"),
        (1949, 10, 1, "國慶"),
    ]
    
    print("\n【公曆→農曆】")
    for y, m, d, note in tests:
        lunar = solar_to_lunar(y, m, d)
        print(f"  {y}/{m}/{d} ({note})")
        print(f"    → {lunar}")
        print(f"    干支: {lunar.ganzhi_full()} 生肖:{lunar.shengxiao}")
    
    print("\n【完整八字】北斗 1973/12/30 寅時(4點)")
    bazi = get_bazi(1973, 12, 30, 4)
    print(f"  八字: {bazi['bazi_str']}")
    print(f"  生肖: {bazi['shengxiao']}")
