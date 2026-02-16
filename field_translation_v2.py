"""
場論翻譯系統 field_translation_v2.py v2.0
=========================================
XTF任務：拓-T2 | 執行星：流祇（連結）

整合所有白話翻譯模組：
- 十神、八卦、紫微主星、格局、數理（v1）
- 四化、神煞、輔星（v2新增）

📚 場論核心概念：
古典術語 → 場態描述 → 現代語言 → 實用建議
"""

from typing import Dict, List, Optional, Any

# ============================================================
# 導入各模組
# ============================================================

from sihua_translation import (
    SIHUA_BASE, YEAR_GAN_SIHUA, STAR_SIHUA_DETAIL,
    get_sihua_by_year_gan, get_sihua_detail, translate_sihua, generate_sihua_report
)
from shensha_translation import (
    JISHEN, XIONGSHA, find_shensha, generate_shensha_report
)
from fuzhu_star_translation import (
    LIUJI_STARS, LIUSHA_STARS, OTHER_STARS, ALL_FUZHU_STARS,
    get_fuzhu_star_info, translate_fuzhu_stars, generate_fuzhu_report, analyze_fuzhu_balance
)

# ============================================================
# v1 原有內容（保持不變）
# ============================================================

# 十神白話翻譯
SHISHEN_TRANSLATION = {
    "比肩": {
        "classic": "比肩者，同我也",
        "vernacular": "跟你一樣的人",
        "field": "同頻競爭場",
        "modern": "同事、同行、競爭者",
        "strength": "有同伴、有競爭力、獨立",
        "weakness": "競爭壓力、分資源",
        "advice": "合作比競爭更有利",
    },
    "劫財": {
        "classic": "劫財者，奪我財也",
        "vernacular": "會搶你東西的人",
        "field": "干涉競爭場",
        "modern": "競爭對手、合夥人（要小心）",
        "strength": "有衝勁、敢爭取",
        "weakness": "破財、被搶、合作糾紛",
        "advice": "謹慎選擇合作夥伴",
    },
    "食神": {
        "classic": "食神者，我生之秀氣",
        "vernacular": "穩定的才華輸出",
        "field": "穩定輸出場",
        "modern": "創作、服務、教學、表演",
        "strength": "有才華、有福氣、好脾氣",
        "weakness": "可能太安逸",
        "advice": "把才華變成收入來源",
    },
    "傷官": {
        "classic": "傷官者，才華外露",
        "vernacular": "爆發的才華，會衝撞框架",
        "field": "衝擊輸出場",
        "modern": "創意、批評、創新、挑戰權威",
        "strength": "才華洋溢、敢說敢做",
        "weakness": "得罪人、太衝、惹是非",
        "advice": "收斂鋒芒，把批評變建設",
    },
    "偏財": {
        "classic": "偏財者，眾人之財",
        "vernacular": "機會財、投資財",
        "field": "機動掌控場",
        "modern": "投資、業務、仲介、創業",
        "strength": "財路寬、機會多、人脈廣",
        "weakness": "不穩定、風險大",
        "advice": "抓住機會但要控制風險",
    },
    "正財": {
        "classic": "正財者，我之所得",
        "vernacular": "穩穩賺的錢",
        "field": "穩定掌控場",
        "modern": "薪水、穩定收入、正當收益",
        "strength": "收入穩定、理財保守",
        "weakness": "格局可能不大",
        "advice": "穩健理財，適度投資",
    },
    "七殺": {
        "classic": "七殺者，克我之凶神",
        "vernacular": "壓力和挑戰",
        "field": "衝擊約束場",
        "modern": "危機、競爭、壓力、挑戰",
        "strength": "有魄力、敢拼、抗壓性強",
        "weakness": "壓力大、易有衝突",
        "advice": "把壓力轉化為動力",
    },
    "正官": {
        "classic": "正官者，克我之正神",
        "vernacular": "合理的管束",
        "field": "穩定約束場",
        "modern": "主管、制度、規範、責任",
        "strength": "有地位、守規矩、有責任感",
        "weakness": "束縛、壓力",
        "advice": "在體制內發展",
    },
    "偏印": {
        "classic": "偏印者，生我之偏神",
        "vernacular": "非主流的知識來源",
        "field": "獨特輸入場",
        "modern": "技術、偏門、另類療法、小眾領域",
        "strength": "獨特才能、專業技術",
        "weakness": "可能太偏門、孤獨",
        "advice": "把獨特變成專業",
    },
    "正印": {
        "classic": "正印者，生我之正神",
        "vernacular": "有人教你、有靠山",
        "field": "穩定支援場",
        "modern": "導師、貴人、學習、保護",
        "strength": "有人幫、學習力強、有靠山",
        "weakness": "可能依賴他人",
        "advice": "珍惜貴人，也要獨立",
    },
}

# 八卦白話翻譯
BAGUA_TRANSLATION = {
    "乾": {
        "symbol": "☰",
        "wuxing": "金",
        "classic": "乾為天，剛健中正",
        "vernacular": "全力衝刺、領導模式",
        "field": "純陽上升場",
        "modern": "CEO模式、主導、決策",
        "strength": "有魄力、能領導、有決斷",
        "weakness": "可能太強勢、獨斷",
        "scenario": "需要主導、決策、領導的場合",
    },
    "坤": {
        "symbol": "☷",
        "wuxing": "土",
        "classic": "坤為地，厚德載物",
        "vernacular": "配合承載、支援模式",
        "field": "純陰承載場",
        "modern": "後勤支援、配合、包容",
        "strength": "包容力強、能承載、穩定",
        "weakness": "可能太被動",
        "scenario": "需要支援、配合、包容的場合",
    },
    "震": {
        "symbol": "☳",
        "wuxing": "木",
        "classic": "震為雷，動而有聲",
        "vernacular": "突然啟動、破局模式",
        "field": "震動啟發場",
        "modern": "創業破局、突然行動、新開始",
        "strength": "有衝勁、能破局",
        "weakness": "可能太衝動",
        "scenario": "需要破局、啟動、改變的場合",
    },
    "巽": {
        "symbol": "☴",
        "wuxing": "木",
        "classic": "巽為風，入而無阻",
        "vernacular": "柔軟滲透、傳播模式",
        "field": "滲透傳播場",
        "modern": "行銷傳播、柔性影響、漸進",
        "strength": "柔軟、能滲透、傳播力強",
        "weakness": "可能太軟弱",
        "scenario": "需要滲透、傳播、影響的場合",
    },
    "坎": {
        "symbol": "☵",
        "wuxing": "水",
        "classic": "坎為水，習險不已",
        "vernacular": "穿越困難、危機模式",
        "field": "流動陷落場",
        "modern": "危機處理、穿越困難、適應",
        "strength": "適應力強、能穿越困難",
        "weakness": "可能陷入困境",
        "scenario": "需要穿越困難、處理危機的場合",
    },
    "離": {
        "symbol": "☲",
        "wuxing": "火",
        "classic": "離為火，明而附麗",
        "vernacular": "展現光芒、表現模式",
        "field": "發光依附場",
        "modern": "展現才華、表演、曝光",
        "strength": "有光芒、能展現",
        "weakness": "可能太張揚",
        "scenario": "需要展現、表演、曝光的場合",
    },
    "艮": {
        "symbol": "☶",
        "wuxing": "土",
        "classic": "艮為山，止而不動",
        "vernacular": "停下來、穩定模式",
        "field": "靜止阻擋場",
        "modern": "止損、等待、穩定",
        "strength": "穩定、能止損",
        "weakness": "可能太固執",
        "scenario": "需要停止、等待、穩定的場合",
    },
    "兌": {
        "symbol": "☱",
        "wuxing": "金",
        "classic": "兌為澤，說而和悅",
        "vernacular": "交流愉悅、社交模式",
        "field": "交流喜悅場",
        "modern": "社交、談判、娛樂",
        "strength": "會說話、人緣好",
        "weakness": "可能太輕浮",
        "scenario": "需要社交、談判、娛樂的場合",
    },
}

# 紫微14主星白話翻譯
ZIWEI_STAR_TRANSLATION = {
    "紫微": {
        "wuxing": "土",
        "classic": "帝座之星，尊貴無比",
        "vernacular": "天生老大命，愛面子",
        "field": "中央統籌場",
        "modern": "CEO、領導者、決策者",
        "strength": "有氣勢、能領導、有尊嚴",
        "weakness": "愛面子、可能孤高",
        "career": "高層管理、領導職位",
    },
    "天機": {
        "wuxing": "木",
        "classic": "謀略之星，善於變通",
        "vernacular": "聰明愛動腦，點子多",
        "field": "思維運算場",
        "modern": "軍師、顧問、策劃",
        "strength": "聰明、靈活、有謀略",
        "weakness": "想太多、優柔寡斷",
        "career": "策劃、顧問、研發",
    },
    "太陽": {
        "wuxing": "火",
        "classic": "光明之星，普照萬物",
        "vernacular": "熱情愛幫人，愛發光",
        "field": "外放發光場",
        "modern": "老師、公關、媒體人",
        "strength": "熱情、樂於助人、有影響力",
        "weakness": "太操心、消耗大",
        "career": "教育、公關、媒體",
    },
    "武曲": {
        "wuxing": "金",
        "classic": "財星之首，剛毅果斷",
        "vernacular": "務實重效率，財務腦",
        "field": "執行落地場",
        "modern": "CFO、財務、執行者",
        "strength": "務實、有效率、財務觀念好",
        "weakness": "太硬、不通人情",
        "career": "財務、金融、執行管理",
    },
    "天同": {
        "wuxing": "水",
        "classic": "福星之首，享福悠閒",
        "vernacular": "好好先生，愛享受",
        "field": "舒適享受場",
        "modern": "服務業、享受生活",
        "strength": "好相處、有福氣、人緣好",
        "weakness": "太軟、缺乏魄力",
        "career": "服務業、休閒娛樂",
    },
    "廉貞": {
        "wuxing": "火",
        "classic": "次桃花星，政治手腕",
        "vernacular": "會做人，有手腕",
        "field": "人際政治場",
        "modern": "政治家、公關、社交高手",
        "strength": "會做人、政治智慧高",
        "weakness": "可能太複雜",
        "career": "公關、政治、社交型工作",
    },
    "天府": {
        "wuxing": "土",
        "classic": "財庫之星，穩定保守",
        "vernacular": "穩穩守財，保守型",
        "field": "儲蓄穩定場",
        "modern": "財務保守、資產管理",
        "strength": "穩定、守財、保守",
        "weakness": "太保守、格局不大",
        "career": "財務、資產管理、穩定型工作",
    },
    "太陰": {
        "wuxing": "水",
        "classic": "富星之首，田宅之主",
        "vernacular": "低調有錢，重隱私",
        "field": "內斂積累場",
        "modern": "不動產、投資、低調富人",
        "strength": "低調、有內涵、擅積累",
        "weakness": "太低調、情緒化",
        "career": "不動產、投資、幕後工作",
    },
    "貪狼": {
        "wuxing": "木",
        "classic": "桃花之首，多才多藝",
        "vernacular": "什麼都想要，多才多藝",
        "field": "慾望擴張場",
        "modern": "斜槓、多元發展、娛樂",
        "strength": "多才多藝、有魅力、慾望強",
        "weakness": "貪多、不專注",
        "career": "娛樂、斜槓、多元發展",
    },
    "巨門": {
        "wuxing": "水",
        "classic": "是非之星，口才之星",
        "vernacular": "能說會道，但可能惹是非",
        "field": "言語表達場",
        "modern": "律師、辯論、銷售",
        "strength": "口才好、分析力強",
        "weakness": "是非多、太挑剔",
        "career": "法律、銷售、分析師",
    },
    "天相": {
        "wuxing": "水",
        "classic": "印星之首，輔佐之才",
        "vernacular": "好助手，配合度高",
        "field": "輔助配合場",
        "modern": "秘書、助理、幕僚",
        "strength": "配合度高、有原則",
        "weakness": "太依附他人",
        "career": "秘書、助理、輔助型工作",
    },
    "天梁": {
        "wuxing": "土",
        "classic": "蔭星之首，化解災厄",
        "vernacular": "老大哥，愛幫人解決問題",
        "field": "庇護解厄場",
        "modern": "老師、法官、調解人",
        "strength": "能庇護他人、解決問題",
        "weakness": "管太多、愛操心",
        "career": "教育、法律、調解",
    },
    "七殺": {
        "wuxing": "金",
        "classic": "將星之首，剛強威猛",
        "vernacular": "衝衝衝，有魄力",
        "field": "衝擊開創場",
        "modern": "創業者、軍人、開拓者",
        "strength": "有魄力、敢衝、有執行力",
        "weakness": "太衝、樹敵多",
        "career": "創業、軍警、開拓性工作",
    },
    "破軍": {
        "wuxing": "水",
        "classic": "破耗之星，先破後立",
        "vernacular": "打破重來，破壞式創新",
        "field": "破壞重建場",
        "modern": "改革者、創新者、破壞式創新",
        "strength": "敢破敢立、有創新精神",
        "weakness": "破壞過度、不穩定",
        "career": "創新、改革、創業",
    },
}

# 格局白話翻譯
GEJU_TRANSLATION = {
    "正官格": {"vernacular": "走正規路線", "field": "穩定約束場", "suitable": "體制內發展"},
    "七殺格": {"vernacular": "壓力轉動力", "field": "衝擊挑戰場", "suitable": "創業競爭"},
    "正印格": {"vernacular": "有人教有靠山", "field": "穩定支援場", "suitable": "學術幕僚"},
    "偏印格": {"vernacular": "走非主流路線", "field": "獨特輸入場", "suitable": "技術偏門"},
    "正財格": {"vernacular": "穩穩賺錢", "field": "穩定掌控場", "suitable": "財務經營"},
    "偏財格": {"vernacular": "抓機會投資", "field": "機動掌控場", "suitable": "投資業務"},
    "食神格": {"vernacular": "才華穩定輸出", "field": "穩定輸出場", "suitable": "創作服務"},
    "傷官格": {"vernacular": "才華衝擊框架", "field": "衝擊輸出場", "suitable": "創新批評"},
    "建祿格": {"vernacular": "自力更生型", "field": "自主獨立場", "suitable": "獨立發展"},
    "月刃格": {"vernacular": "競爭搶奪型", "field": "競爭干涉場", "suitable": "競爭領域"},
}

# 81數理精選
SHULI_81 = {
    1: {"name": "太極之數", "type": "大吉", "meaning": "萬物開泰，最吉之數"},
    3: {"name": "進取之數", "type": "大吉", "meaning": "進取如意，增進繁榮"},
    5: {"name": "福壽之數", "type": "大吉", "meaning": "福壽圓滿，富貴榮華"},
    6: {"name": "安穩之數", "type": "大吉", "meaning": "安穩餘慶，吉人天相"},
    7: {"name": "精悍之數", "type": "吉", "meaning": "剛毅果斷，精悍有為"},
    8: {"name": "堅剛之數", "type": "吉", "meaning": "意志堅定，勤勉發展"},
    11: {"name": "旱苗逢雨", "type": "大吉", "meaning": "挽回家運，順利發展"},
    13: {"name": "智略超群", "type": "大吉", "meaning": "智謀優秀，才能出眾"},
    15: {"name": "福壽雙全", "type": "大吉", "meaning": "福壽圓滿，富貴榮譽"},
    16: {"name": "貴人得助", "type": "大吉", "meaning": "貴人相助，興家立業"},
    21: {"name": "首領之數", "type": "大吉", "meaning": "光風霽月，萬物更新"},
    23: {"name": "旭日東升", "type": "大吉", "meaning": "旭日東升，發育茂盛"},
    24: {"name": "掘藏得金", "type": "大吉", "meaning": "家門餘慶，錦上添花"},
    31: {"name": "智勇得志", "type": "大吉", "meaning": "智勇得志，可享清福"},
    32: {"name": "僥倖之數", "type": "大吉", "meaning": "僥倖多望，貴人得助"},
    33: {"name": "升天之數", "type": "大吉", "meaning": "家門隆昌，才德開展"},
    35: {"name": "保守之數", "type": "吉", "meaning": "溫和平靜，保守生平"},
    37: {"name": "權威之數", "type": "吉", "meaning": "權威顯達，吉人天相"},
    39: {"name": "富貴榮華", "type": "吉", "meaning": "富貴榮華，財帛豐盈"},
    41: {"name": "德高望重", "type": "大吉", "meaning": "德高望重，事事如意"},
    45: {"name": "順風之數", "type": "大吉", "meaning": "順風揚帆，新生泰和"},
    47: {"name": "花開之數", "type": "吉", "meaning": "花開之象，萬事如意"},
    48: {"name": "青松之數", "type": "吉", "meaning": "青松立鶴，德智兼備"},
    # 凶數
    2: {"name": "分離之數", "type": "凶", "meaning": "混沌未定，分離破敗"},
    4: {"name": "凶變之數", "type": "凶", "meaning": "凶變不測，災難重重"},
    9: {"name": "破舟之數", "type": "凶", "meaning": "興盡凋落，窮迫逆境"},
    10: {"name": "零暗之數", "type": "凶", "meaning": "萬事終局，回顧茫然"},
    12: {"name": "薄弱之數", "type": "凶", "meaning": "薄弱無力，孤立無援"},
    14: {"name": "破兆之數", "type": "凶", "meaning": "家庭緣薄，孤獨遭難"},
    19: {"name": "多難之數", "type": "凶", "meaning": "風雲蔽日，遮障重重"},
    20: {"name": "虛無之數", "type": "凶", "meaning": "非業破運，災難重重"},
    22: {"name": "秋草之數", "type": "凶", "meaning": "秋草逢霜，困難重重"},
    26: {"name": "變怪之數", "type": "半凶", "meaning": "變怪奇異，英雄豪傑"},
    27: {"name": "增長之數", "type": "半凶", "meaning": "欲望無止，自我犧牲"},
    28: {"name": "闘爭之數", "type": "凶", "meaning": "魚臨旱地，難逃厄運"},
    34: {"name": "破家之數", "type": "凶", "meaning": "破家亡身，短命非業"},
    36: {"name": "風波之數", "type": "半凶", "meaning": "風浪不息，俠義薄運"},
    40: {"name": "退安之數", "type": "半凶", "meaning": "智謀膽力，冒險投機"},
    42: {"name": "寒蟬之數", "type": "凶", "meaning": "博識多能，精力耗散"},
    43: {"name": "散財之數", "type": "凶", "meaning": "雨夜之花，薄弱散漫"},
    44: {"name": "煩悶之數", "type": "凶", "meaning": "破家亡身，暗藏慘淡"},
    46: {"name": "浪裡行舟", "type": "凶", "meaning": "載寶沉舟，浪裡淘沙"},
    49: {"name": "轉變之數", "type": "半凶", "meaning": "吉凶難分，不知所措"},
    50: {"name": "小舟之數", "type": "半凶", "meaning": "吉凶參半，禍福相依"},
}

# 框架資訊
FRAMEWORK_INFO = {
    "framework_version": "1.8 → 2.0",
    "philosophy": "古法是根，場論是枝，用戶是花",
    "epistemology": "術數是決策框架生成器，非命定裁決",
    "completed_modules": [
        "十神（100%）", "五行關係（100%）", "六親（100%）",
        "十二宮（100%）", "姓名學（100%）", "梅花八卦（100%）",
        "八字格局（100%）", "紫微14主星（100%）",
        "紫微四化（100%）", "神煞（100%）", "輔星（100%）",  # v2新增
    ],
    "pending_modules": [
        "紫微大限流年（30%）", "八字大運流年（20%）",
    ],
}


# ============================================================
# 便捷查詢函數
# ============================================================

def get_shishen_translation(name: str) -> Optional[Dict]:
    return SHISHEN_TRANSLATION.get(name)

def get_bagua_translation(name: str) -> Optional[Dict]:
    return BAGUA_TRANSLATION.get(name)

def get_ziwei_star_translation(name: str) -> Optional[Dict]:
    return ZIWEI_STAR_TRANSLATION.get(name)

def get_geju_translation(name: str) -> Optional[Dict]:
    return GEJU_TRANSLATION.get(name)

def get_shuli_translation(num: int) -> Dict:
    if num > 81:
        num = num % 80 if num % 80 != 0 else 80
    return SHULI_81.get(num, {"name": "普通", "type": "平", "meaning": "普通之數"})

def stroke_to_wuxing(stroke: int) -> str:
    """筆畫轉五行"""
    mapping = {1: "木", 2: "木", 3: "火", 4: "火", 5: "土",
               6: "土", 7: "金", 8: "金", 9: "水", 0: "水"}
    return mapping.get(stroke % 10, "土")


def translate_ziwei_stars(star_list: List[str]) -> List[Dict]:
    """批量翻譯紫微主星"""
    result = []
    for star in star_list:
        info = get_ziwei_star_translation(star)
        if info:
            result.append({"star": star, **info})
    return result


def generate_field_analysis(engine: str, data: Dict) -> Dict:
    """生成場論分析"""
    if engine == "紫微斗數":
        ming_stars = data.get("ming_stars", [])
        if ming_stars:
            main_star = ming_stars[0]
            info = get_ziwei_star_translation(main_star)
            return {
                "core_field": f"{main_star}場",
                "field_summary": info.get("field", "") if info else "",
                "vernacular": info.get("vernacular", "") if info else "",
                "career": info.get("career", "") if info else "",
            }
    return {"core_field": "待分析", "field_summary": ""}


# ============================================================
# v2 新增：整合查詢
# ============================================================

def get_all_translations() -> Dict:
    """取得所有翻譯資料"""
    return {
        "shishen": SHISHEN_TRANSLATION,
        "bagua": BAGUA_TRANSLATION,
        "ziwei_stars": ZIWEI_STAR_TRANSLATION,
        "geju": GEJU_TRANSLATION,
        "shuli": SHULI_81,
        "sihua_base": SIHUA_BASE,
        "sihua_detail": STAR_SIHUA_DETAIL,
        "jishen": JISHEN,
        "xiongsha": XIONGSHA,
        "fuzhu_stars": ALL_FUZHU_STARS,
        "framework": FRAMEWORK_INFO,
    }


def generate_comprehensive_report(
    day_gan: str,
    pillars: Dict[str, str],
    year_gan: str,
    ming_stars: List[str],
    fuzhu_stars: List[str],
) -> str:
    """生成綜合場論報告"""
    
    report = """
╔══════════════════════════════════════════════════════════════════╗
║                    場論詮釋綜合報告 v2.0                          ║
╚══════════════════════════════════════════════════════════════════╝

"""
    
    # 1. 四化
    report += generate_sihua_report(year_gan)
    report += "\n"
    
    # 2. 神煞
    report += generate_shensha_report(day_gan, pillars)
    report += "\n"
    
    # 3. 輔星
    report += generate_fuzhu_report("命宮", fuzhu_stars)
    
    return report


if __name__ == "__main__":
    print("場論翻譯系統 v2.0 載入成功")
    print(f"完成模組：{len(FRAMEWORK_INFO['completed_modules'])} 個")
    
    # 測試
    print("\n【十神測試】")
    print(get_shishen_translation("正官"))
    
    print("\n【四化測試】")
    print(get_sihua_detail("紫微", "化權"))
