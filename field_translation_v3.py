"""
場論翻譯系統 field_translation_v3.py v3.0
=========================================
XTF任務：融-F | 執行星：光蘊（統籌）
整合日期：2026-02-08

整合所有白話翻譯模組：
- v1：十神、八卦、紫微主星、格局、數理
- v2：四化、神煞、輔星
- v3：易經64卦、易經384爻（新增）

📚 場論核心概念：
古典術語 → 場態描述 → 現代語言 → 實用建議
"""

from typing import Dict, List, Optional, Any

# ============================================================
# 導入各模組
# ============================================================

try:
    from sihua_translation import (
        SIHUA_BASE, YEAR_GAN_SIHUA, STAR_SIHUA_DETAIL,
        get_sihua_by_year_gan, get_sihua_detail, translate_sihua, generate_sihua_report
    )
    SIHUA_AVAILABLE = True
except ImportError:
    SIHUA_AVAILABLE = False

try:
    from shensha_translation import (
        JISHEN, XIONGSHA, find_shensha, generate_shensha_report
    )
    SHENSHA_AVAILABLE = True
except ImportError:
    SHENSHA_AVAILABLE = False

try:
    from fuzhu_star_translation import (
        LIUJI_STARS, LIUSHA_STARS, OTHER_STARS, ALL_FUZHU_STARS,
        get_fuzhu_star_info, translate_fuzhu_stars, generate_fuzhu_report, analyze_fuzhu_balance
    )
    FUZHU_AVAILABLE = True
except ImportError:
    FUZHU_AVAILABLE = False

try:
    from yijing_gua_translation import (
        GUA_64, get_gua_info, get_gua_by_name, translate_gua, generate_gua_report
    )
    YIJING_GUA_AVAILABLE = True
except ImportError:
    YIJING_GUA_AVAILABLE = False

try:
    from yijing_yao_translation import (
        YAO_384, YAO_POSITION_GUIDE, get_yao_info, get_yao_position_guide,
        translate_yao, generate_yao_report, get_all_yao_for_gua
    )
    YIJING_YAO_AVAILABLE = True
except ImportError:
    YIJING_YAO_AVAILABLE = False

# ============================================================
# v1 原有內容（十神、八卦、紫微主星等）
# ============================================================

SHISHEN_TRANSLATION = {
    "比肩": {"classic": "比肩者，同我也", "vernacular": "跟你一樣的人", "field": "同頻競爭場",
             "modern": "同事、同行、競爭者", "strength": "有同伴、有競爭力、獨立", "weakness": "競爭壓力、分資源"},
    "劫財": {"classic": "劫財者，奪我財也", "vernacular": "會搶你東西的人", "field": "干涉競爭場",
             "modern": "競爭對手、合夥人", "strength": "有衝勁、敢爭取", "weakness": "破財、被搶"},
    "食神": {"classic": "食神者，我生之秀氣", "vernacular": "穩定的才華輸出", "field": "穩定輸出場",
             "modern": "創作、服務、教學", "strength": "有才華、有福氣", "weakness": "可能太安逸"},
    "傷官": {"classic": "傷官者，才華外露", "vernacular": "爆發的才華，會衝撞框架", "field": "衝擊輸出場",
             "modern": "創意、批評、創新", "strength": "才華洋溢、敢說敢做", "weakness": "得罪人、太衝"},
    "偏財": {"classic": "偏財者，眾人之財", "vernacular": "機會財、投資財", "field": "機動掌控場",
             "modern": "投資、業務、創業", "strength": "財路寬、機會多", "weakness": "不穩定、風險大"},
    "正財": {"classic": "正財者，我之所得", "vernacular": "穩穩賺的錢", "field": "穩定掌控場",
             "modern": "薪水、穩定收入", "strength": "收入穩定", "weakness": "格局可能不大"},
    "七殺": {"classic": "七殺者，克我之凶神", "vernacular": "壓力和挑戰", "field": "衝擊約束場",
             "modern": "危機、競爭、壓力", "strength": "有魄力、敢拼", "weakness": "壓力大"},
    "正官": {"classic": "正官者，約束我也", "vernacular": "規矩和管理", "field": "穩定約束場",
             "modern": "工作、法規、上司", "strength": "有紀律、受信任", "weakness": "太保守"},
    "偏印": {"classic": "偏印者，母之偏愛", "vernacular": "偏門的學問和想法", "field": "非正式滋養場",
             "modern": "偏門技能、靈感", "strength": "有創意、有慧根", "weakness": "孤僻、想太多"},
    "正印": {"classic": "正印者，生我之母", "vernacular": "滋養和保護", "field": "正式滋養場",
             "modern": "學歷、證照、靠山", "strength": "有學問、有保護", "weakness": "依賴、不獨立"}
}

BAGUA_TRANSLATION = {
    "乾": {"element": "金", "nature": "天", "family": "父", "body": "頭", "direction": "西北",
           "vernacular": "老大、領導、決策者", "field": "主導場", "modern": "老闆、父親、決策"},
    "坤": {"element": "土", "nature": "地", "family": "母", "body": "腹", "direction": "西南",
           "vernacular": "承載、滋養、包容", "field": "承載場", "modern": "母親、員工、支持"},
    "震": {"element": "木", "nature": "雷", "family": "長男", "body": "足", "direction": "東",
           "vernacular": "啟動、行動、衝勁", "field": "啟動場", "modern": "長子、創業、行動"},
    "巽": {"element": "木", "nature": "風", "family": "長女", "body": "股", "direction": "東南",
           "vernacular": "滲透、傳播、溝通", "field": "滲透場", "modern": "長女、傳播、進入"},
    "坎": {"element": "水", "nature": "水", "family": "中男", "body": "耳", "direction": "北",
           "vernacular": "險阻、智慧、流動", "field": "險阻場", "modern": "危機、智慧、流動"},
    "離": {"element": "火", "nature": "火", "family": "中女", "body": "目", "direction": "南",
           "vernacular": "光明、依附、展現", "field": "展現場", "modern": "展示、文化、美麗"},
    "艮": {"element": "土", "nature": "山", "family": "少男", "body": "手", "direction": "東北",
           "vernacular": "停止、穩固、界限", "field": "止境場", "modern": "停止、穩定、房產"},
    "兌": {"element": "金", "nature": "澤", "family": "少女", "body": "口", "direction": "西",
           "vernacular": "喜悅、交流、說服", "field": "喜悅場", "modern": "說話、交流、喜悅"}
}

ZIWEI_STAR_TRANSLATION = {
    "紫微": {"type": "帝王星", "vernacular": "老闆、領導者", "field": "核心掌控場",
             "strength": "有權威、被尊重、有格局", "weakness": "可能高傲、孤獨"},
    "天機": {"type": "智慧星", "vernacular": "軍師、策劃者", "field": "思考分析場",
             "strength": "聰明、反應快、有謀略", "weakness": "想太多、不夠果斷"},
    "太陽": {"type": "光明星", "vernacular": "給予者、照亮者", "field": "付出展現場",
             "strength": "熱情、大方、有影響力", "weakness": "太累、不懂拒絕"},
    "武曲": {"type": "財星", "vernacular": "執行者、賺錢者", "field": "執行獲取場",
             "strength": "有執行力、會賺錢", "weakness": "太硬、不通人情"},
    "天同": {"type": "福星", "vernacular": "享福者、知足者", "field": "舒適安逸場",
             "strength": "知足、樂觀、人緣好", "weakness": "懶散、缺乏動力"},
    "廉貞": {"type": "囚星", "vernacular": "堅持者、執著者", "field": "堅持執著場",
             "strength": "有原則、不妥協", "weakness": "太固執、容易卡住"},
    "天府": {"type": "財庫星", "vernacular": "守財者、穩重者", "field": "穩定儲蓄場",
             "strength": "穩重、會存錢", "weakness": "保守、不敢冒險"},
    "太陰": {"type": "財星", "vernacular": "積累者、內斂者", "field": "內斂積累場",
             "strength": "細心、會積累", "weakness": "敏感、想太多"},
    "貪狼": {"type": "慾望星", "vernacular": "追求者、多才者", "field": "慾望追求場",
             "strength": "多才多藝、有魅力", "weakness": "貪心、不專一"},
    "巨門": {"type": "口舌星", "vernacular": "分析者、質疑者", "field": "質疑分析場",
             "strength": "分析力強、能言善辯", "weakness": "口舌是非、太尖銳"},
    "天相": {"type": "印星", "vernacular": "輔助者、協調者", "field": "輔助協調場",
             "strength": "會協調、有人緣", "weakness": "沒主見、太依賴"},
    "天梁": {"type": "蔭星", "vernacular": "保護者、長輩", "field": "保護蔭庇場",
             "strength": "有貴人、會照顧人", "weakness": "愛管閒事、囉嗦"},
    "七殺": {"type": "將星", "vernacular": "衝鋒者、開創者", "field": "衝擊開創場",
             "strength": "有魄力、敢衝", "weakness": "太衝、容易受傷"},
    "破軍": {"type": "耗星", "vernacular": "破壞者、改革者", "field": "破壞重建場",
             "strength": "敢破舊、能創新", "weakness": "不穩定、浪費"}
}

# ============================================================
# 統一翻譯介面
# ============================================================

def translate_shishen(shishen: str) -> Dict:
    """翻譯十神"""
    return SHISHEN_TRANSLATION.get(shishen, {"error": f"未找到：{shishen}"})

def translate_bagua(gua: str) -> Dict:
    """翻譯八卦"""
    return BAGUA_TRANSLATION.get(gua, {"error": f"未找到：{gua}"})

def translate_ziwei_star(star: str) -> Dict:
    """翻譯紫微主星"""
    return ZIWEI_STAR_TRANSLATION.get(star, {"error": f"未找到：{star}"})

# ============================================================
# 易經統一介面
# ============================================================

def translate_yijing_gua(gua_num: int) -> Dict:
    """翻譯易經卦"""
    if not YIJING_GUA_AVAILABLE:
        return {"error": "易經卦模組未載入"}
    return generate_gua_report(gua_num)

def translate_yijing_yao(gua_num: int, yao_pos: int) -> Dict:
    """翻譯易經爻"""
    if not YIJING_YAO_AVAILABLE:
        return {"error": "易經爻模組未載入"}
    return generate_yao_report(gua_num, yao_pos)

def get_full_gua_with_yao(gua_num: int) -> Dict:
    """獲取完整卦象（含六爻）"""
    result = {"gua": None, "yao": []}
    
    if YIJING_GUA_AVAILABLE:
        result["gua"] = generate_gua_report(gua_num)
    
    if YIJING_YAO_AVAILABLE:
        result["yao"] = get_all_yao_for_gua(gua_num)
    
    return result

# ============================================================
# 模組狀態報告
# ============================================================

def get_translation_status() -> Dict:
    """獲取翻譯模組狀態"""
    return {
        "version": "3.0",
        "date": "2026-02-08",
        "modules": {
            "shishen": {"available": True, "count": len(SHISHEN_TRANSLATION)},
            "bagua": {"available": True, "count": len(BAGUA_TRANSLATION)},
            "ziwei_star": {"available": True, "count": len(ZIWEI_STAR_TRANSLATION)},
            "sihua": {"available": SIHUA_AVAILABLE},
            "shensha": {"available": SHENSHA_AVAILABLE},
            "fuzhu": {"available": FUZHU_AVAILABLE},
            "yijing_gua": {"available": YIJING_GUA_AVAILABLE, "count": 64 if YIJING_GUA_AVAILABLE else 0},
            "yijing_yao": {"available": YIJING_YAO_AVAILABLE, "count": len(YAO_384) if YIJING_YAO_AVAILABLE else 0}
        }
    }

# ============================================================
# 測試
# ============================================================

if __name__ == "__main__":
    print("場論翻譯系統 v3.0")
    print("=" * 50)
    status = get_translation_status()
    print(f"版本：{status['version']}")
    print(f"日期：{status['date']}")
    print("\n模組狀態：")
    for name, info in status['modules'].items():
        available = "✅" if info.get('available') else "❌"
        count = info.get('count', '-')
        print(f"  {name}: {available} ({count})")
