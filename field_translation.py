"""
場論翻譯模組 field_translation.py v2.0 20260207
================================================
北斗命數「去神秘化」核心：場論白話翻譯系統

📚 知識點：
- 場論 = 用現代「場」的概念統一詮釋所有術數
- 白話翻譯 = 把古典術語翻成現代人能懂的語言
- 現代比喻 = 用職場/生活情境類比古典概念
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum


# =============================================================================
# 十神白話翻譯
# =============================================================================

SHISHEN_TRANSLATION = {
    "正官": {
        "relation": "剋我者（陰陽異）",
        "vernacular": "合理的管束",
        "field": "穩定約束場",
        "modern": "主管、制度、規則",
        "strength": "有方向、有紀律、受人尊重",
        "weakness": "可能太保守、缺乏創新",
    },
    "七殺": {
        "relation": "剋我者（陰陽同）",
        "vernacular": "壓力和挑戰",
        "field": "衝擊約束場",
        "modern": "危機、競爭、壓迫",
        "strength": "抗壓、有魄力、敢拼",
        "weakness": "太衝、樹敵多、身體負擔",
    },
    "正印": {
        "relation": "生我者（陰陽異）",
        "vernacular": "有人教有人罩",
        "field": "穩定支援場",
        "modern": "導師、貴人、資源",
        "strength": "有學識、有靠山、穩定成長",
        "weakness": "可能太依賴、不接地氣",
    },
    "偏印": {
        "relation": "生我者（陰陽同）",
        "vernacular": "偏門的支援",
        "field": "獨特支援場",
        "modern": "另類、偏技、非正統",
        "strength": "有獨特才能、不受框架限制",
        "weakness": "可能太怪、不被主流認可",
    },
    "正財": {
        "relation": "我剋者（陰陽異）",
        "vernacular": "穩定的收入",
        "field": "穩定掌控場",
        "modern": "薪水、存款、固定資產",
        "strength": "財運穩定、務實可靠",
        "weakness": "可能太計較、格局不大",
    },
    "偏財": {
        "relation": "我剋者（陰陽同）",
        "vernacular": "機會財",
        "field": "機動掌控場",
        "modern": "投資、獎金、意外收入",
        "strength": "機會多、人脈廣、財路寬",
        "weakness": "可能不穩定、投機風險",
    },
    "食神": {
        "relation": "我生者（陰陽同）",
        "vernacular": "穩定的才華",
        "field": "穩定輸出場",
        "modern": "創作、服務、穩定表達",
        "strength": "有才華、有福氣、人緣好",
        "weakness": "可能太安逸、缺乏進取心",
    },
    "傷官": {
        "relation": "我生者（陰陽異）",
        "vernacular": "爆發的才華",
        "field": "衝擊輸出場",
        "modern": "創意、批評、顛覆",
        "strength": "有才華、有創意、敢突破",
        "weakness": "可能太衝、得罪人",
    },
    "比肩": {
        "relation": "同我者（陰陽同）",
        "vernacular": "合作的夥伴",
        "field": "同頻共振場",
        "modern": "同事、朋友、合作",
        "strength": "有幫手、能合作",
        "weakness": "可能分資源、意見不合",
    },
    "劫財": {
        "relation": "同我者（陰陽異）",
        "vernacular": "競爭的對手",
        "field": "同頻干涉場",
        "modern": "競爭、消耗、搶奪",
        "strength": "有競爭意識、激發潛能",
        "weakness": "可能被搶、消耗資源",
    },
}


# =============================================================================
# 八卦白話翻譯
# =============================================================================

BAGUA_TRANSLATION = {
    "乾": {
        "symbol": "☰",
        "binary": "111",
        "classic": "天、父、剛健",
        "vernacular": "全力衝刺",
        "field": "純陽上升場",
        "modern": "CEO模式、領導者",
        "strength": "動力強、有魄力、敢決斷",
        "weakness": "太剛易折、不聽意見、過度擴張",
        "scenario": "創業衝刺期、年底業績衝刺、考試前全力備考",
    },
    "坤": {
        "symbol": "☷",
        "binary": "000",
        "classic": "地、母、柔順",
        "vernacular": "配合承載",
        "field": "純陰承載場",
        "modern": "後勤模式、支援者",
        "strength": "穩定、包容、持久、可靠",
        "weakness": "太被動、缺乏主見、被人踩",
        "scenario": "公司行政後勤、學習階段、蓄勢待發",
    },
    "震": {
        "symbol": "☳",
        "binary": "001",
        "classic": "雷、長子、動",
        "vernacular": "突然啟動",
        "field": "震動啟發場",
        "modern": "創業啟動、破局",
        "strength": "有衝勁、敢行動、能破局",
        "weakness": "虎頭蛇尾、後勁不足、太衝動",
        "scenario": "新項目啟動、跳槽換工作、突然的靈感",
    },
    "巽": {
        "symbol": "☴",
        "binary": "110",
        "classic": "風、長女、入",
        "vernacular": "慢慢滲透",
        "field": "滲透流通場",
        "modern": "軟實力、影響力",
        "strength": "不引起抵抗、持久、深入人心",
        "weakness": "太慢、沒存在感、被忽視",
        "scenario": "品牌長期經營、慢慢說服老闘、文化影響",
    },
    "坎": {
        "symbol": "☵",
        "binary": "010",
        "classic": "水、中男、險",
        "vernacular": "穿越困難",
        "field": "流動陷落場",
        "modern": "危機模式、挑戰",
        "strength": "能在困境中找到出路、鍛鍊韌性",
        "weakness": "真的陷進去出不來、一錯再錯",
        "scenario": "公司資金困難、職涯瓶頸期、人生低潮期",
    },
    "離": {
        "symbol": "☲",
        "binary": "101",
        "classic": "火、中女、麗",
        "vernacular": "光明展現",
        "field": "附著光明場",
        "modern": "曝光模式、展示",
        "strength": "能見度高、有魅力、能吸引人",
        "weakness": "太依賴外部、內在空虛、曇花一現",
        "scenario": "產品發布會、自媒體經營、個人品牌塑造",
    },
    "艮": {
        "symbol": "☶",
        "binary": "100",
        "classic": "山、少男、止",
        "vernacular": "適時停止",
        "field": "停止界限場",
        "modern": "止損模式、守成",
        "strength": "知止、有邊界感、能穩住",
        "weakness": "太保守、錯失機會、不敢動",
        "scenario": "投資止損、設定工作邊界、拒絕不合理要求",
    },
    "兌": {
        "symbol": "☱",
        "binary": "011",
        "classic": "澤、少女、悅",
        "vernacular": "喜悅交流",
        "field": "喜悅開口場",
        "modern": "社交模式、溝通",
        "strength": "會說話、有親和力、能成交",
        "weakness": "話太多、口舌是非、表面功夫",
        "scenario": "業務開發、社群經營、團隊溝通",
    },
}


# =============================================================================
# 紫微14主星白話翻譯
# =============================================================================

ZIWEI_STAR_TRANSLATION = {
    "紫微": {
        "wuxing": "土",
        "classic": "帝王、尊貴",
        "vernacular": "天生老大命",
        "field": "中央統籌場",
        "modern": "CEO、老闆",
        "strength": "格局大、有威嚴、能服眾",
        "weakness": "太驕傲、不接地氣、孤獨",
        "career": "管理層、企業主、政治人物",
    },
    "天機": {
        "wuxing": "木",
        "classic": "智慧、謀略",
        "vernacular": "聰明愛動腦",
        "field": "思維運算場",
        "modern": "軍師、策略師",
        "strength": "聰明、有策略、適應力強",
        "weakness": "想太多、猶豫不決、缺乏執行力",
        "career": "顧問、分析師、企劃、研發",
    },
    "太陽": {
        "wuxing": "火",
        "classic": "光明、博愛",
        "vernacular": "熱情愛幫人",
        "field": "外放發光場",
        "modern": "公眾人物、老師",
        "strength": "有魅力、有人緣、正能量",
        "weakness": "太操心、管太多、容易透支",
        "career": "教育、媒體、公關、政治",
    },
    "武曲": {
        "wuxing": "金",
        "classic": "財星、剛毅",
        "vernacular": "務實重效率",
        "field": "執行落地場",
        "modern": "財務長、軍人",
        "strength": "有執行力、務實、有財運",
        "weakness": "太冷硬、不通人情、孤獨",
        "career": "金融、軍警、運動、技術",
    },
    "天同": {
        "wuxing": "水",
        "classic": "福星、享樂",
        "vernacular": "隨和愛享受",
        "field": "舒適安逸場",
        "modern": "生活家、躺平族",
        "strength": "好相處、懂生活、有福氣",
        "weakness": "太安逸、缺乏進取心、容易被動",
        "career": "服務業、餐飲、休閒、藝術",
    },
    "廉貞": {
        "wuxing": "火",
        "classic": "桃花、公關",
        "vernacular": "有魅力會交際",
        "field": "人際磁吸場",
        "modern": "公關、業務",
        "strength": "有魅力、會交際、人脈廣",
        "weakness": "感情複雜、易惹是非、不夠專一",
        "career": "公關、業務、演藝、社交媒體",
    },
    "天府": {
        "wuxing": "土",
        "classic": "財庫、保守",
        "vernacular": "穩重會存錢",
        "field": "儲存守成場",
        "modern": "財務主管、守財奴",
        "strength": "穩重、會理財、有安全感",
        "weakness": "太保守、缺乏創新、小氣",
        "career": "金融、會計、不動產、倉儲",
    },
    "太陰": {
        "wuxing": "水",
        "classic": "富星、細膩",
        "vernacular": "細心重隱私",
        "field": "內斂收藏場",
        "modern": "幕僚、研究員",
        "strength": "細心、有品味、善於觀察",
        "weakness": "太內向、缺乏自信、情緒化",
        "career": "研究、設計、藝術、不動產",
    },
    "貪狼": {
        "wuxing": "木",
        "classic": "桃花、慾望",
        "vernacular": "多才慾望強",
        "field": "慾望驅動場",
        "modern": "斜槓青年、業務高手",
        "strength": "多才、有魅力、適應力強",
        "weakness": "貪多嚼不爛、不專精、感情複雜",
        "career": "業務、娛樂、創意、多元發展",
    },
    "巨門": {
        "wuxing": "水",
        "classic": "暗星、口舌",
        "vernacular": "口才好愛質疑",
        "field": "言語穿透場",
        "modern": "律師、主持人",
        "strength": "口才好、有洞察力、善於質疑",
        "weakness": "嘴巴太利、招是非、疑心重",
        "career": "法律、媒體、教育、諮詢",
    },
    "天相": {
        "wuxing": "水",
        "classic": "印星、輔佐",
        "vernacular": "配合有原則",
        "field": "輔助協調場",
        "modern": "秘書、副手",
        "strength": "可靠、有原則、配合度高",
        "weakness": "太依附、缺乏主見、不夠有魄力",
        "career": "秘書、行政、人資、幕僚",
    },
    "天梁": {
        "wuxing": "土",
        "classic": "蔭星、清高",
        "vernacular": "正直愛管事",
        "field": "庇護監督場",
        "modern": "監察官、長輩",
        "strength": "正直、能解決問題、有公信力",
        "weakness": "太愛管、太清高、不近人情",
        "career": "法律、監察、社工、醫療",
    },
    "七殺": {
        "wuxing": "金",
        "classic": "將星、衝勁",
        "vernacular": "有魄力敢衝",
        "field": "衝擊突破場",
        "modern": "創業家、將軍",
        "strength": "有魄力、敢衝、執行力強",
        "weakness": "太衝動、樹敵多、孤獨",
        "career": "軍警、運動、創業、開拓性工作",
    },
    "破軍": {
        "wuxing": "水",
        "classic": "耗星、破壞",
        "vernacular": "敢破壞求變",
        "field": "破壞重建場",
        "modern": "改革者、創業家",
        "strength": "敢創新、有開創力、不怕改變",
        "weakness": "破壞性強、不穩定、難以持久",
        "career": "創業、研發、改革、變動性工作",
    },
}


# =============================================================================
# 八字格局白話翻譯
# =============================================================================

GEJU_TRANSLATION = {
    "正官格": {
        "condition": "月令正官透出",
        "vernacular": "走正規路線",
        "field": "穩定約束場",
        "suitable": "體制內發展",
        "modern": "公務員、大企業主管",
        "advice": "找個好公司或考個公職，按部就班往上爬",
    },
    "七殺格": {
        "condition": "月令七殺透出",
        "vernacular": "壓力轉動力",
        "field": "衝擊挑戰場",
        "suitable": "創業競爭",
        "modern": "創業者、軍人、運動員",
        "advice": "你是壓力型選手，找個好導師幫你化解壓力",
    },
    "正印格": {
        "condition": "月令正印透出",
        "vernacular": "有人教有靠山",
        "field": "穩定支援場",
        "suitable": "學術幕僚",
        "modern": "學者、顧問、幕僚",
        "advice": "適合靠知識吃飯，找個好平台讓你發揮",
    },
    "偏印格": {
        "condition": "月令偏印透出",
        "vernacular": "走非主流路線",
        "field": "獨特輸入場",
        "suitable": "技術偏門",
        "modern": "技術專家、另類療法、小眾領域",
        "advice": "找到你的小眾市場，深耕下去",
    },
    "正財格": {
        "condition": "月令正財透出",
        "vernacular": "穩穩賺錢",
        "field": "穩定掌控場",
        "suitable": "財務經營",
        "modern": "會計、財務、中小企業主",
        "advice": "天生會理財，用錢去創造更大的價值",
    },
    "偏財格": {
        "condition": "月令偏財透出",
        "vernacular": "抓機會投資",
        "field": "機動掌控場",
        "suitable": "投資業務",
        "modern": "投資人、業務、仲介",
        "advice": "有抓機會的天賦，但賺到要守住一部分",
    },
    "食神格": {
        "condition": "月令食神透出",
        "vernacular": "才華穩定輸出",
        "field": "穩定輸出場",
        "suitable": "創作服務",
        "modern": "廚師、作家、設計師",
        "advice": "有才華又懂生活，把才華轉化成收入",
    },
    "傷官格": {
        "condition": "月令傷官透出",
        "vernacular": "才華衝擊框架",
        "field": "衝擊輸出場",
        "suitable": "創新批評",
        "modern": "創新者、評論家、創業者",
        "advice": "很聰明，但要學會包裝，不要太直接得罪人",
    },
}


# =============================================================================
# 81數理精選
# =============================================================================

SHULI_81 = {
    # 大吉
    1: {"name": "太極之數", "type": "大吉", "meaning": "萬物開始，有創造力"},
    3: {"name": "進取之數", "type": "大吉", "meaning": "積極向上，有發展"},
    5: {"name": "福壽之數", "type": "大吉", "meaning": "福氣好，平順"},
    6: {"name": "安穩之數", "type": "大吉", "meaning": "天時地利，安定"},
    7: {"name": "剛毅之數", "type": "大吉", "meaning": "意志堅定，有魄力"},
    8: {"name": "堅實之數", "type": "大吉", "meaning": "努力有成，意志力強"},
    11: {"name": "旺盛之數", "type": "大吉", "meaning": "草木逢春，萬事如意"},
    13: {"name": "智略之數", "type": "大吉", "meaning": "足智多謀，有才華"},
    15: {"name": "福壽之數", "type": "大吉", "meaning": "福壽圓滿，慈祥"},
    16: {"name": "厚德之數", "type": "大吉", "meaning": "德望高，受人尊敬"},
    21: {"name": "首領之數", "type": "大吉", "meaning": "領導力強，有威望"},
    23: {"name": "壯麗之數", "type": "大吉", "meaning": "旭日東昇，興旺發達"},
    24: {"name": "豐財之數", "type": "大吉", "meaning": "財運好，白手起家"},
    29: {"name": "智謀之數", "type": "大吉", "meaning": "智慧超群，財官雙美"},
    31: {"name": "智勇之數", "type": "大吉", "meaning": "智勇雙全，有領導力"},
    32: {"name": "僥倖之數", "type": "大吉", "meaning": "貴人多，機遇好"},
    33: {"name": "升天之數", "type": "大吉", "meaning": "家門昌隆，才德兼備"},
    35: {"name": "保守之數", "type": "大吉", "meaning": "溫和平靜，穩中有進"},
    37: {"name": "權威之數", "type": "大吉", "meaning": "獨立權威，有聲望"},
    41: {"name": "純陽之數", "type": "大吉", "meaning": "德高望重，功成名就"},
    45: {"name": "順風之數", "type": "大吉", "meaning": "順風順水，新生泰和"},
    47: {"name": "開花之數", "type": "大吉", "meaning": "開花結果，事業有成"},
    48: {"name": "智謀之數", "type": "大吉", "meaning": "顧問師表，德智兼備"},
    # 凶
    2: {"name": "分離之數", "type": "凶", "meaning": "分離、動盪"},
    4: {"name": "凶變之數", "type": "凶", "meaning": "破敗、不順"},
    9: {"name": "窮盡之數", "type": "凶", "meaning": "盛極而衰"},
    10: {"name": "歸零之數", "type": "凶", "meaning": "萬事歸空"},
    12: {"name": "薄弱之數", "type": "凶", "meaning": "意志薄弱"},
    14: {"name": "破兆之數", "type": "凶", "meaning": "破敗、孤獨"},
    19: {"name": "多難之數", "type": "凶", "meaning": "多災多難"},
    20: {"name": "虛無之數", "type": "凶", "meaning": "虛無、不實"},
    22: {"name": "秋草之數", "type": "凶", "meaning": "秋草逢霜"},
    26: {"name": "波瀾之數", "type": "凶", "meaning": "起伏不定"},
    28: {"name": "孤獨之數", "type": "凶", "meaning": "孤獨、離群"},
    34: {"name": "破家之數", "type": "凶", "meaning": "破敗之象"},
    36: {"name": "風波之數", "type": "凶", "meaning": "風波不斷"},
    40: {"name": "浮沉之數", "type": "凶", "meaning": "浮沉不定"},
    44: {"name": "煩悶之數", "type": "凶", "meaning": "煩悶不安"},
    46: {"name": "浪裡之數", "type": "凶", "meaning": "載寶沉舟"},
}


# =============================================================================
# 查詢函數
# =============================================================================

def get_shishen_translation(shishen: str) -> Dict:
    """查詢十神白話翻譯"""
    return SHISHEN_TRANSLATION.get(shishen, {})


def get_bagua_translation(gua: str) -> Dict:
    """查詢八卦白話翻譯"""
    # 支援符號或名稱查詢
    for name, data in BAGUA_TRANSLATION.items():
        if gua == name or gua == data["symbol"]:
            return {"name": name, **data}
    return {}


def get_ziwei_star_translation(star: str) -> Dict:
    """查詢紫微主星白話翻譯"""
    return ZIWEI_STAR_TRANSLATION.get(star, {})


def get_geju_translation(geju: str) -> Dict:
    """查詢格局白話翻譯"""
    for name, data in GEJU_TRANSLATION.items():
        if geju in name or name in geju:
            return {"name": name, **data}
    return {}


def get_shuli_translation(num: int) -> Dict:
    """查詢81數理白話翻譯"""
    actual = num if num <= 81 else num - 80
    if actual in SHULI_81:
        return SHULI_81[actual]
    return {"name": "中吉/平", "type": "中", "meaning": "吉凶參半，需視整體配置"}


def stroke_to_wuxing(stroke: int) -> str:
    """筆畫轉五行"""
    mapping = {1: "木", 2: "木", 3: "火", 4: "火", 5: "土",
               6: "土", 7: "金", 8: "金", 9: "水", 0: "水"}
    return mapping[stroke % 10]


def translate_ziwei_stars(stars: List[str]) -> List[Dict]:
    """批量翻譯紫微星曜"""
    return [{"star": s, **get_ziwei_star_translation(s)} for s in stars if get_ziwei_star_translation(s)]


def translate_bazi_shishen(shishen_list: List[str]) -> List[Dict]:
    """批量翻譯八字十神"""
    return [{"shishen": s, **get_shishen_translation(s)} for s in shishen_list if get_shishen_translation(s)]


# =============================================================================
# 場論分析報告生成
# =============================================================================

def generate_field_analysis(engine: str, data: Dict) -> Dict:
    """生成場論分析報告"""
    analysis = {
        "engine": engine,
        "field_summary": "",
        "core_field": "",
        "strengths": [],
        "weaknesses": [],
        "suggestions": [],
    }
    
    if engine == "紫微斗數" and "ming_stars" in data:
        stars = data["ming_stars"]
        if stars:
            main_star = stars[0]
            star_info = get_ziwei_star_translation(main_star)
            if star_info:
                analysis["core_field"] = star_info.get("field", "")
                analysis["field_summary"] = f"命宮主星{main_star}，{star_info.get('vernacular', '')}"
                analysis["strengths"].append(star_info.get("strength", ""))
                analysis["weaknesses"].append(star_info.get("weakness", ""))
                analysis["suggestions"].append(f"適合職業：{star_info.get('career', '')}")
    
    elif engine == "八字" and "day_master" in data:
        dm = data["day_master"]
        analysis["core_field"] = f"{dm}日主場"
        analysis["field_summary"] = f"日主{dm}，代表你的核心能量"
    
    elif engine == "姓名學" and "wuge" in data:
        ren = data["wuge"].get("ren", 0)
        shuli = get_shuli_translation(ren)
        analysis["core_field"] = "人格場（最重要）"
        analysis["field_summary"] = f"人格{ren}，{shuli['name']}（{shuli['type']}）"
        analysis["strengths"].append(shuli["meaning"])
    
    return analysis


# =============================================================================
# 框架版本資訊
# =============================================================================

FRAMEWORK_INFO = {
    "version": "2.0",
    "framework_version": "1.8",
    "completed_modules": [
        "十神（10項）",
        "五行關係（8種）",
        "六親（5類）",
        "十二宮（12宮）",
        "姓名學（81數理）",
        "梅花八卦（8卦）",
        "八字格局（10格）",
        "紫微14主星（14星）",
    ],
    "philosophy": "術數是個人化決策框架生成器，與天氣預報同構",
    "disclaimer": "趨吉避凶——趨和避都是動詞，主語是人",
}


if __name__ == "__main__":
    print("=== 場論翻譯模組 v2.0 測試 ===\n")
    
    print("【十神翻譯】")
    print(get_shishen_translation("正官"))
    
    print("\n【八卦翻譯】")
    print(get_bagua_translation("乾"))
    
    print("\n【紫微星翻譯】")
    print(get_ziwei_star_translation("紫微"))
    
    print("\n【格局翻譯】")
    print(get_geju_translation("正官格"))
    
    print("\n【81數理翻譯】")
    print(get_shuli_translation(16))
