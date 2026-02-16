#!/usr/bin/env python3
"""
北斗命數 問事占卜系統 v1.0
==========================
輸入問題 + 年月日時 → 起卦 → 解卦 → 建議

北斗七星文創 × 織明 | 2026-02-15
"""

from dataclasses import dataclass
from typing import Dict
from datetime import date
from meihua_engine import full_meihua
from almanac_filter import get_day_almanac
from wuxing_core import ZHI, ZHI_NUM

# 體用關係→吉凶
TIYONG_VERDICT = {
    "我剋": ("大吉", "體剋用，我方主動，能掌控局面"),
    "生我": ("吉", "用生體，外力相助，順利發展"),
    "比和": ("平", "體用比和，雙方勢均力敵"),
    "剋我": ("凶", "用剋體，外力壓制，宜退守"),
    "我生": ("小凶", "體生用，消耗精力，付出多"),
}

# 分類建議
CATEGORY_ADVICE = {
    "career": {
        "大吉": "事業發展有利，可主動出擊",
        "吉": "工作順利，有貴人相助",
        "平": "維持現狀為宜",
        "凶": "職場有壓力，宜低調",
        "小凶": "工作辛苦，付出多回報少",
    },
    "relationship": {
        "大吉": "感情主動有利，適合追求",
        "吉": "感情和諧，對方有好感",
        "平": "感情平淡，維持現狀",
        "凶": "感情有阻礙，需溝通",
        "小凶": "付出較多，對方未必領情",
    },
    "wealth": {
        "大吉": "財運旺盛，投資有利",
        "吉": "有財運，把握機會",
        "平": "收支平衡，不宜冒險",
        "凶": "財運不佳，宜保守",
        "小凶": "投入大於產出，暫緩",
    },
    "health": {
        "大吉": "身體健康，精力充沛",
        "吉": "健康無大礙",
        "平": "健康一般，宜調養",
        "凶": "注意健康，建議檢查",
        "小凶": "消耗過大，注意休息",
    },
    "general": {
        "大吉": "形勢有利，積極行動",
        "吉": "順利發展，穩步前進",
        "平": "維持現狀，不宜冒進",
        "凶": "形勢不利，宜退守",
        "小凶": "需要付出，回報有限",
    },
}


def hour_to_zhi(hour: int) -> str:
    """小時轉地支"""
    zhi_idx = (hour + 1) // 2 % 12
    return ZHI[zhi_idx]


def divine(question: str, year: int, month: int, day: int, hour: int,
           category: str = "general") -> Dict:
    """
    問事占卜
    
    參數:
        question: 問題
        year, month, day, hour: 問事時間
        category: career/relationship/wealth/health/general
    
    返回: 占卜結果字典
    """
    # 1. 計算參數
    year_zhi_num = (year - 4) % 12 + 1
    hour_zhi = hour_to_zhi(hour)
    hour_zhi_num = ZHI_NUM.get(hour_zhi, 1)
    
    # 2. 起卦
    meihua = full_meihua(year_zhi_num, month, day, hour_zhi_num, question)
    
    # 3. 取出結果
    ben_gua = meihua["ben_gua"]
    bian_gua = meihua["bian_gua"]
    hu_gua = meihua["hu_gua"]
    tiyong = meihua["ti_yong"]
    
    # 4. 判斷吉凶
    relation = tiyong.relation
    verdict_info = TIYONG_VERDICT.get(relation, ("平", "形勢平穩"))
    verdict = verdict_info[0]
    
    # 5. 分類建議
    advice = CATEGORY_ADVICE.get(category, CATEGORY_ADVICE["general"]).get(verdict, "觀望")
    
    # 6. 農民曆
    almanac = get_day_almanac(date(year, month, day))
    
    return {
        "question": question,
        "time": f"{year}年{month}月{day}日 {hour_zhi}時({hour}點)",
        "category": category,
        "gua": {
            "main": ben_gua.name,
            "bian": bian_gua.name,
            "hu": hu_gua.name,
            "dong_yao": ben_gua.dong_yao,
        },
        "tiyong": {
            "ti": f"{tiyong.ti_name}({tiyong.ti_wx})",
            "yong": f"{tiyong.yong_name}({tiyong.yong_wx})",
            "relation": relation,
            "meaning": tiyong.verdict,
        },
        "result": {
            "verdict": verdict,
            "advice": advice,
        },
        "detail": {
            "hu": tiyong.hu_analysis,
            "bian": tiyong.bian_analysis,
        },
        "almanac": f"{almanac.ganzhi} {almanac.jianchu}({almanac.jianchu_jixiong})",
    }


# ============================================================
# 測試
# ============================================================
if __name__ == "__main__":
    print("=" * 70)
    print("         北斗命數 問事占卜系統")
    print("=" * 70)
    
    questions = [
        ("今年事業運勢如何？", 2026, 2, 15, 10, "career"),
        ("這筆投資能賺錢嗎？", 2026, 3, 8, 14, "wealth"),
        ("我和他/她適合嗎？", 2026, 2, 14, 20, "relationship"),
        ("近期身體狀況？", 2026, 2, 15, 8, "health"),
    ]
    
    for q, y, m, d, h, cat in questions:
        print(f"\n【問事: {q}】")
        r = divine(q, y, m, d, h, cat)
        print(f"  時間: {r['time']}")
        print(f"  ┌────────────────────────────────────────────────────────┐")
        print(f"  │ 本卦: {r['gua']['main']:<40}   │")
        print(f"  │ 變卦: {r['gua']['bian']:<40}   │")
        print(f"  │ 互卦: {r['gua']['hu']:<40}   │")
        print(f"  │ 動爻: 第{r['gua']['dong_yao']}爻                                         │")
        print(f"  ├────────────────────────────────────────────────────────┤")
        print(f"  │ 體: {r['tiyong']['ti']:<10} 用: {r['tiyong']['yong']:<10}               │")
        print(f"  │ {r['tiyong']['meaning']:<48} │")
        print(f"  ├────────────────────────────────────────────────────────┤")
        print(f"  │ ★ 判斷: {r['result']['verdict']:<42}   │")
        print(f"  │ ★ 建議: {r['result']['advice']:<40} │")
        print(f"  └────────────────────────────────────────────────────────┘")
    
    print("\n" + "=" * 70)
    print("✅ 問事占卜系統完成！")
    print("=" * 70)
