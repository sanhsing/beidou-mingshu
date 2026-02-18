"""
免費八字試算模組 (簡化版)
M3.1-M3.2 | @星殼 | 2026-02-17
PYLIB: bazi_base, wuxing_core
"""
from datetime import datetime
from typing import Dict, Any

# 天干地支
TIANGAN = ['甲', '乙', '丙', '丁', '戊', '己', '庚', '辛', '壬', '癸']
DIZHI = ['子', '丑', '寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥']
WUXING_GAN = {'甲': '木', '乙': '木', '丙': '火', '丁': '火', '戊': '土', 
              '己': '土', '庚': '金', '辛': '金', '壬': '水', '癸': '水'}
WUXING_ZHI = {'子': '水', '丑': '土', '寅': '木', '卯': '木', '辰': '土', '巳': '火',
              '午': '火', '未': '土', '申': '金', '酉': '金', '戌': '土', '亥': '水'}

# 日主特質簡述
RIZHU_TRAITS = {
    '甲': {'element': '木', 'trait': '領導力強，正直有原則', 'emoji': '🌲'},
    '乙': {'element': '木', 'trait': '柔韌有彈性，善於適應', 'emoji': '🌿'},
    '丙': {'element': '火', 'trait': '熱情開朗，光明磊落', 'emoji': '☀️'},
    '丁': {'element': '火', 'trait': '細膩溫暖，有洞察力', 'emoji': '🕯️'},
    '戊': {'element': '土', 'trait': '穩重踏實，值得信賴', 'emoji': '⛰️'},
    '己': {'element': '土', 'trait': '包容務實，細心周到', 'emoji': '🏔️'},
    '庚': {'element': '金', 'trait': '果斷剛毅，有魄力', 'emoji': '⚔️'},
    '辛': {'element': '金', 'trait': '精緻敏銳，追求完美', 'emoji': '💎'},
    '壬': {'element': '水', 'trait': '智慧深邃，善於謀略', 'emoji': '🌊'},
    '癸': {'element': '水', 'trait': '靈活聰慧，直覺敏銳', 'emoji': '💧'},
}

def calc_year_ganzhi(year: int) -> tuple:
    """計算年干支"""
    gan_idx = (year - 4) % 10
    zhi_idx = (year - 4) % 12
    return TIANGAN[gan_idx], DIZHI[zhi_idx]

def calc_month_ganzhi(year: int, month: int) -> tuple:
    """計算月干支 (簡化版，不考慮節氣)"""
    year_gan, _ = calc_year_ganzhi(year)
    gan_start = (TIANGAN.index(year_gan) % 5) * 2 + 2
    gan_idx = (gan_start + month - 1) % 10
    zhi_idx = (month + 1) % 12
    return TIANGAN[gan_idx], DIZHI[zhi_idx]

def calc_day_ganzhi(year: int, month: int, day: int) -> tuple:
    """計算日干支"""
    from datetime import date
    base = date(1900, 1, 31)  # 甲辰日
    target = date(year, month, day)
    diff = (target - base).days
    gan_idx = diff % 10
    zhi_idx = diff % 12
    return TIANGAN[gan_idx], DIZHI[zhi_idx]

def calc_hour_ganzhi(day_gan: str, hour: int) -> tuple:
    """計算時干支"""
    zhi_idx = (hour + 1) // 2 % 12
    gan_start = (TIANGAN.index(day_gan) % 5) * 2
    gan_idx = (gan_start + zhi_idx) % 10
    return TIANGAN[gan_idx], DIZHI[zhi_idx]

def calc_wuxing_stats(bazi: Dict) -> Dict[str, int]:
    """計算五行統計"""
    stats = {'木': 0, '火': 0, '土': 0, '金': 0, '水': 0}
    for pillar in ['year', 'month', 'day', 'hour']:
        gan = bazi[pillar]['gan']
        zhi = bazi[pillar]['zhi']
        stats[WUXING_GAN[gan]] += 1
        stats[WUXING_ZHI[zhi]] += 1
    return stats

def free_bazi_analyze(year: int, month: int, day: int, hour: int) -> Dict[str, Any]:
    """
    免費八字分析 (簡化版)
    返回基礎八字和日主特質，引導付費升級
    """
    # 計算四柱
    year_gan, year_zhi = calc_year_ganzhi(year)
    month_gan, month_zhi = calc_month_ganzhi(year, month)
    day_gan, day_zhi = calc_day_ganzhi(year, month, day)
    hour_gan, hour_zhi = calc_hour_ganzhi(day_gan, hour)
    
    bazi = {
        'year': {'gan': year_gan, 'zhi': year_zhi, 'ganzhi': year_gan + year_zhi},
        'month': {'gan': month_gan, 'zhi': month_zhi, 'ganzhi': month_gan + month_zhi},
        'day': {'gan': day_gan, 'zhi': day_zhi, 'ganzhi': day_gan + day_zhi},
        'hour': {'gan': hour_gan, 'zhi': hour_zhi, 'ganzhi': hour_gan + hour_zhi},
    }
    
    # 五行統計
    wuxing = calc_wuxing_stats(bazi)
    
    # 日主特質
    rizhu = RIZHU_TRAITS[day_gan]
    
    # 找出最強和最弱的五行
    sorted_wx = sorted(wuxing.items(), key=lambda x: x[1], reverse=True)
    strongest = sorted_wx[0]
    weakest = sorted_wx[-1]
    
    return {
        'bazi': bazi,
        'bazi_str': f"{bazi['year']['ganzhi']} {bazi['month']['ganzhi']} {bazi['day']['ganzhi']} {bazi['hour']['ganzhi']}",
        'day_master': day_gan,
        'day_master_element': rizhu['element'],
        'day_master_emoji': rizhu['emoji'],
        'day_master_trait': rizhu['trait'],
        'wuxing': wuxing,
        'wuxing_strongest': {'element': strongest[0], 'count': strongest[1]},
        'wuxing_weakest': {'element': weakest[0], 'count': weakest[1]},
        'teaser': {
            'has_more': True,
            'locked_features': [
                '十神分析',
                '格局判定',
                '大運走勢',
                '流年運勢',
                '事業方向',
                '感情婚姻',
            ]
        }
    }

if __name__ == "__main__":
    # 測試
    result = free_bazi_analyze(1990, 5, 15, 14)
    print(f"八字: {result['bazi_str']}")
    print(f"日主: {result['day_master']} {result['day_master_emoji']}")
    print(f"特質: {result['day_master_trait']}")
    print(f"五行: {result['wuxing']}")
