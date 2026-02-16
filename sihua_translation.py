"""
紫微四化詳解 sihua_translation.py v1.0
======================================
XTF任務：消-B1 | 執行星：理樞（分析）

核心本質：四化 = 祿權科忌 × 14主星 = 56組合
四化是紫微斗數的動態變化系統，代表流年運勢的吉凶變化

📚 四化基本含義：
- 祿：財祿、享受、進帳、好事來
- 權：權力、掌控、競爭、主導
- 科：聲名、貴人、考試、文書
- 忌：阻礙、糾纏、執著、問題
"""

from typing import Dict, List, Optional

# ============================================================
# 四化基本定義
# ============================================================

SIHUA_BASE = {
    "化祿": {
        "symbol": "祿",
        "vernacular": "好事來、有進帳",
        "field": "資源流入場",
        "modern": "加薪、業績好、貴人、收入增加",
        "positive": "財運好、人緣佳、機會多",
        "negative": "可能過度享樂、貪圖安逸",
        "advice": "把握機會，但不要揮霍",
    },
    "化權": {
        "symbol": "權",
        "vernacular": "有話語權、能掌控",
        "field": "主導掌控場",
        "modern": "升職、主導權、領導力、決策權",
        "positive": "有魄力、能服人、競爭力強",
        "negative": "可能太強勢、獨斷、樹敵",
        "advice": "適度使用權力，注意人際",
    },
    "化科": {
        "symbol": "科",
        "vernacular": "有名氣、貴人助",
        "field": "聲名傳播場",
        "modern": "考試順利、名聲好、貴人出現",
        "positive": "有人幫、名聲好、順利解決",
        "negative": "可能虛名、過度依賴他人",
        "advice": "珍惜貴人，但要有實力",
    },
    "化忌": {
        "symbol": "忌",
        "vernacular": "卡住、有麻煩",
        "field": "阻滯糾纏場",
        "modern": "阻礙、問題、執著、糾纏",
        "positive": "執著可以是專注、深耕",
        "negative": "卡住、損失、是非、健康問題",
        "advice": "放下執著，繞道而行",
    },
}

# ============================================================
# 十四主星四化（依年干）
# ============================================================

# 年干四化表
YEAR_GAN_SIHUA = {
    "甲": {"祿": "廉貞", "權": "破軍", "科": "武曲", "忌": "太陽"},
    "乙": {"祿": "天機", "權": "天梁", "科": "紫微", "忌": "太陰"},
    "丙": {"祿": "天同", "權": "天機", "科": "文昌", "忌": "廉貞"},
    "丁": {"祿": "太陰", "權": "天同", "科": "天機", "忌": "巨門"},
    "戊": {"祿": "貪狼", "權": "太陰", "科": "右弼", "忌": "天機"},
    "己": {"祿": "武曲", "權": "貪狼", "科": "天梁", "忌": "文曲"},
    "庚": {"祿": "太陽", "權": "武曲", "科": "太陰", "忌": "天同"},
    "辛": {"祿": "巨門", "權": "太陽", "科": "文曲", "忌": "文昌"},
    "壬": {"祿": "天梁", "權": "紫微", "科": "左輔", "忌": "武曲"},
    "癸": {"祿": "破軍", "權": "巨門", "科": "太陰", "忌": "貪狼"},
}

# ============================================================
# 14主星各化詳解
# ============================================================

STAR_SIHUA_DETAIL = {
    "紫微": {
        "化祿": {
            "meaning": "帝王有祿",
            "vernacular": "領導力變現，地位帶來財富",
            "field": "尊貴資源場",
            "modern": "靠地位賺錢、高層人脈、權力財",
            "advice": "善用影響力，但別貪圖名利",
        },
        "化權": {
            "meaning": "帝王執權",
            "vernacular": "權力極大化，說一不二",
            "field": "絕對掌控場",
            "modern": "最高決策者、一把手、老闘",
            "advice": "權力大責任大，要有胸襟",
        },
        "化科": {
            "meaning": "帝王名揚",
            "vernacular": "聲望隆重，受人尊敬",
            "field": "尊貴聲名場",
            "modern": "德高望重、業界權威、受人敬仰",
            "advice": "名望是責任，要以德服人",
        },
        "化忌": {
            "meaning": "帝王孤高",
            "vernacular": "高處不勝寒，孤獨感",
            "field": "孤高阻滯場",
            "modern": "位高權重但孤獨、決策壓力大",
            "advice": "放下身段，多聽意見",
        },
    },
    "天機": {
        "化祿": {
            "meaning": "智慧生財",
            "vernacular": "腦袋賺錢，點子變現",
            "field": "智慧資源場",
            "modern": "顧問費、策劃費、知識付費",
            "advice": "把知識產品化，創造價值",
        },
        "化權": {
            "meaning": "謀略掌權",
            "vernacular": "軍師當權，策略主導",
            "field": "策略掌控場",
            "modern": "決策顧問、戰略規劃、幕後主導",
            "advice": "從幕後走到台前，敢於決策",
        },
        "化科": {
            "meaning": "智謀得名",
            "vernacular": "聰明名聲在外",
            "field": "智慧聲名場",
            "modern": "智囊、專家、有識之士",
            "advice": "讓聰明被看見，建立專業形象",
        },
        "化忌": {
            "meaning": "想太多卡住",
            "vernacular": "思慮過度，猶豫不決",
            "field": "思緒糾結場",
            "modern": "分析癱瘓、想太多不行動",
            "advice": "想好就做，別讓腦袋綁架行動",
        },
    },
    "太陽": {
        "化祿": {
            "meaning": "光明生財",
            "vernacular": "曝光帶來收益，公開有利",
            "field": "光明資源場",
            "modern": "公開演講、媒體收入、知名度變現",
            "advice": "主動曝光，讓更多人認識你",
        },
        "化權": {
            "meaning": "光芒四射",
            "vernacular": "強勢照耀，主導場面",
            "field": "強勢發光場",
            "modern": "舞台中心、意見領袖、影響力大",
            "advice": "用影響力做好事，別太耀眼刺眼",
        },
        "化科": {
            "meaning": "光明磊落",
            "vernacular": "好名聲，正面形象",
            "field": "正面聲名場",
            "modern": "好口碑、正能量代表、受人信任",
            "advice": "保持正面形象，言行一致",
        },
        "化忌": {
            "meaning": "光芒受阻",
            "vernacular": "曝光反傷，是非纏身",
            "field": "曝光受阻場",
            "modern": "公關危機、負面新聞、形象受損",
            "advice": "低調行事，避免爭議話題",
        },
    },
    "武曲": {
        "化祿": {
            "meaning": "財星化祿",
            "vernacular": "財上加財，正財運旺",
            "field": "財富流入場",
            "modern": "業績好、收入增、財務順利",
            "advice": "財運好，可以積極投資理財",
        },
        "化權": {
            "meaning": "財權在握",
            "vernacular": "財務主導權，經濟話語權",
            "field": "財務掌控場",
            "modern": "財務長、投資決策權、經濟主導",
            "advice": "掌握資金流向，做好財務規劃",
        },
        "化科": {
            "meaning": "財名兼得",
            "vernacular": "理財有名，財務專家",
            "field": "財務聲名場",
            "modern": "理財顧問、金融專家、投資達人",
            "advice": "建立財務專業形象",
        },
        "化忌": {
            "meaning": "財務受阻",
            "vernacular": "錢的問題，資金卡住",
            "field": "財務阻滯場",
            "modern": "資金緊張、投資損失、財務糾紛",
            "advice": "保守理財，避免大筆支出",
        },
    },
    "天同": {
        "化祿": {
            "meaning": "福星添祿",
            "vernacular": "享福還有錢，輕鬆賺錢",
            "field": "舒適資源場",
            "modern": "被動收入、輕鬆獲利、福利好",
            "advice": "享受生活的同時創造收入",
        },
        "化權": {
            "meaning": "福中帶權",
            "vernacular": "輕鬆主導，以柔克剛",
            "field": "柔性掌控場",
            "modern": "服務業管理、柔性領導、親和力主管",
            "advice": "用溫和的方式影響別人",
        },
        "化科": {
            "meaning": "福氣名聲",
            "vernacular": "好人緣，福星高照的形象",
            "field": "親和聲名場",
            "modern": "人緣好、受歡迎、好相處",
            "advice": "保持親和力，廣結善緣",
        },
        "化忌": {
            "meaning": "福星受阻",
            "vernacular": "享受受限，不得安寧",
            "field": "舒適受阻場",
            "modern": "休息不夠、身心疲憊、生活品質下降",
            "advice": "注意休息，別透支身體",
        },
    },
    "廉貞": {
        "化祿": {
            "meaning": "官祿臨門",
            "vernacular": "政商界有利，公關帶財",
            "field": "人脈資源場",
            "modern": "關係變現、社交收益、政商資源",
            "advice": "經營人脈，把關係轉化為資源",
        },
        "化權": {
            "meaning": "官場當道",
            "vernacular": "政治能力強，掌控局面",
            "field": "政治掌控場",
            "modern": "政治手腕、權力運作、影響力",
            "advice": "善用政治智慧，但別玩過頭",
        },
        "化科": {
            "meaning": "官場名望",
            "vernacular": "政商界有名，公關能力強",
            "field": "公關聲名場",
            "modern": "公關專家、社交名人、人脈王",
            "advice": "善用社交能力，建立好名聲",
        },
        "化忌": {
            "meaning": "官非纏身",
            "vernacular": "人際是非，感情糾纏",
            "field": "人際糾纏場",
            "modern": "是非口舌、感情問題、官司",
            "advice": "謹言慎行，避免複雜關係",
        },
    },
    "天府": {
        "化祿": {
            "meaning": "財庫進財",
            "vernacular": "庫房有進帳，存款增加",
            "field": "儲蓄資源場",
            "modern": "存款增加、資產增值、財務穩定",
            "advice": "穩健理財，持續累積",
        },
        "化權": {
            "meaning": "庫房當家",
            "vernacular": "財務主導，管理資產",
            "field": "資產掌控場",
            "modern": "財務管理、資產配置、理財主導",
            "advice": "做好資產管理，保守配置",
        },
        "化科": {
            "meaning": "財庫有名",
            "vernacular": "財務名聲，理財專家",
            "field": "財務聲名場",
            "modern": "理財專家、財務顧問、穩健投資人",
            "advice": "建立穩健理財的形象",
        },
        "化忌": {
            "meaning": "財庫受損",
            "vernacular": "庫房有漏，存款減少",
            "field": "財庫損耗場",
            "modern": "存款減少、資產縮水、財務壓力",
            "advice": "減少支出，保護資產",
        },
    },
    "太陰": {
        "化祿": {
            "meaning": "富星化祿",
            "vernacular": "被動財富，不動產收益",
            "field": "被動資源場",
            "modern": "租金收入、不動產增值、被動收入",
            "advice": "發展被動收入來源",
        },
        "化權": {
            "meaning": "內斂主導",
            "vernacular": "幕後操控，低調掌權",
            "field": "幕後掌控場",
            "modern": "幕後黑手、低調實權、隱性權力",
            "advice": "低調但有實權，別太張揚",
        },
        "化科": {
            "meaning": "內在聲名",
            "vernacular": "低調有名，內行人知道",
            "field": "內斂聲名場",
            "modern": "圈內名人、低調專家、內行認可",
            "advice": "在專業圈內建立名聲",
        },
        "化忌": {
            "meaning": "陰暗面出",
            "vernacular": "情緒問題，內在困擾",
            "field": "內在糾結場",
            "modern": "情緒低落、內心不安、睡眠問題",
            "advice": "關注心理健康，找人傾訴",
        },
    },
    "貪狼": {
        "化祿": {
            "meaning": "慾望生財",
            "vernacular": "慾望變現，多元收入",
            "field": "慾望資源場",
            "modern": "斜槓收入、多元發展、娛樂收益",
            "advice": "把興趣變成收入來源",
        },
        "化權": {
            "meaning": "慾望主導",
            "vernacular": "強烈主導慾，什麼都想要",
            "field": "慾望掌控場",
            "modern": "野心家、多方經營、全面掌控",
            "advice": "專注核心，別貪多嚼不爛",
        },
        "化科": {
            "meaning": "才藝得名",
            "vernacular": "才華被看見，多才多藝",
            "field": "才藝聲名場",
            "modern": "斜槓達人、多才多藝、興趣專家",
            "advice": "展現多元才華，建立個人品牌",
        },
        "化忌": {
            "meaning": "慾望受阻",
            "vernacular": "想要的得不到，慾望糾纏",
            "field": "慾望糾纏場",
            "modern": "求不得、貪心受阻、慾望失控",
            "advice": "控制慾望，知足常樂",
        },
    },
    "巨門": {
        "化祿": {
            "meaning": "口才生財",
            "vernacular": "靠嘴巴賺錢，講話有收益",
            "field": "言語資源場",
            "modern": "演講收入、銷售業績、談判收益",
            "advice": "善用口才，把話術變現",
        },
        "化權": {
            "meaning": "口舌主導",
            "vernacular": "說話有份量，一言九鼎",
            "field": "言語掌控場",
            "modern": "權威發言、輿論主導、話語權",
            "advice": "謹慎發言，權力越大責任越大",
        },
        "化科": {
            "meaning": "口碑名聲",
            "vernacular": "說話有名，口碑好",
            "field": "言語聲名場",
            "modern": "名嘴、評論家、意見領袖",
            "advice": "建立公信力，言而有信",
        },
        "化忌": {
            "meaning": "口舌是非",
            "vernacular": "話多惹禍，口舌糾纏",
            "field": "言語糾纏場",
            "modern": "口舌是非、言語衝突、誤會",
            "advice": "少說多做，禍從口出",
        },
    },
    "天相": {
        "化祿": {
            "meaning": "印星化祿",
            "vernacular": "有人幫忙還有好處",
            "field": "輔助資源場",
            "modern": "貴人帶財、扶持有利、合作收益",
            "advice": "珍惜貴人，互惠互利",
        },
        "化權": {
            "meaning": "輔佐當權",
            "vernacular": "二把手有權，輔助主導",
            "field": "輔助掌控場",
            "modern": "副手、秘書長、幕僚長",
            "advice": "做好輔助工作，有機會上位",
        },
        "化科": {
            "meaning": "輔佐有名",
            "vernacular": "好助手名聲，配合度高",
            "field": "輔助聲名場",
            "modern": "最佳配角、金牌助理、可靠夥伴",
            "advice": "做好配角，貴人自然來",
        },
        "化忌": {
            "meaning": "輔助受阻",
            "vernacular": "幫忙出問題，好心沒好報",
            "field": "輔助受阻場",
            "modern": "幫忙反被怪、配合出問題",
            "advice": "幫忙要適度，別攬過多責任",
        },
    },
    "天梁": {
        "化祿": {
            "meaning": "蔭星化祿",
            "vernacular": "保護有好處，解決問題有收益",
            "field": "庇護資源場",
            "modern": "解決問題收費、保護他人有利",
            "advice": "把解決問題的能力變現",
        },
        "化權": {
            "meaning": "蔭庇當權",
            "vernacular": "庇護者有權，能做主",
            "field": "庇護掌控場",
            "modern": "監察、仲裁、調解主導",
            "advice": "用權力保護弱者，維護正義",
        },
        "化科": {
            "meaning": "清高有名",
            "vernacular": "正直名聲，公正形象",
            "field": "正直聲名場",
            "modern": "公正代表、道德楷模、清流",
            "advice": "保持正直，以德服人",
        },
        "化忌": {
            "meaning": "蔭庇受阻",
            "vernacular": "管太多被嫌，好心沒好報",
            "field": "庇護受阻場",
            "modern": "管太多、被誤解、費力不討好",
            "advice": "適度關心，別太愛管閒事",
        },
    },
    "七殺": {
        "化祿": {
            "meaning": "將星化祿",
            "vernacular": "衝勁帶來財富，開創有利",
            "field": "衝勁資源場",
            "modern": "開拓市場、競爭獲利、突破收益",
            "advice": "用衝勁開創新局面",
        },
        "化權": {
            "meaning": "將星當權",
            "vernacular": "強勢主導，雷厲風行",
            "field": "強勢掌控場",
            "modern": "鐵腕領導、強勢決策、說一不二",
            "advice": "強勢但要有底線，別太霸道",
        },
        "化科": {
            "meaning": "將星有名",
            "vernacular": "有魄力的名聲，強者形象",
            "field": "強者聲名場",
            "modern": "強者代表、業界強人、敢做敢當",
            "advice": "建立強者形象，但別太張揚",
        },
        "化忌": {
            "meaning": "將星受阻",
            "vernacular": "衝勁受阻，有志難伸",
            "field": "衝勁受阻場",
            "modern": "被打壓、有力無處使、受限制",
            "advice": "蓄積能量，等待時機",
        },
    },
    "破軍": {
        "化祿": {
            "meaning": "破舊立新有財",
            "vernacular": "打破重來有好處，變革獲利",
            "field": "變革資源場",
            "modern": "改革收益、創新獲利、破壞式創新",
            "advice": "大膽創新，打破舊局面",
        },
        "化權": {
            "meaning": "破壞主導",
            "vernacular": "破壞重建的主導權",
            "field": "變革掌控場",
            "modern": "改革領導者、創新主導、打破者",
            "advice": "主導變革，但要有建設",
        },
        "化科": {
            "meaning": "創新有名",
            "vernacular": "創新者的名聲，改革派",
            "field": "創新聲名場",
            "modern": "創新代表、改革先鋒、顛覆者",
            "advice": "建立創新者形象，引領變革",
        },
        "化忌": {
            "meaning": "破壞受阻",
            "vernacular": "改革受阻，變動帶來問題",
            "field": "變革受阻場",
            "modern": "改革失敗、變動混亂、破壞過度",
            "advice": "變動要謹慎，別破壞過頭",
        },
    },
}


def get_sihua_by_year_gan(year_gan: str) -> Dict[str, str]:
    """根據年干取得四化星"""
    return YEAR_GAN_SIHUA.get(year_gan, {})


def get_sihua_detail(star: str, hua: str) -> Dict:
    """取得特定星曜四化的詳細資訊"""
    star_sihua = STAR_SIHUA_DETAIL.get(star, {})
    hua_detail = star_sihua.get(hua, {})
    
    if hua_detail:
        return {
            "star": star,
            "hua": hua,
            **hua_detail,
        }
    
    # 如果沒有詳細資料，返回基本資料
    base = SIHUA_BASE.get(hua, {})
    return {
        "star": star,
        "hua": hua,
        "meaning": f"{star}{hua}",
        "vernacular": base.get("vernacular", ""),
        "field": base.get("field", ""),
        "modern": base.get("modern", ""),
        "advice": base.get("advice", ""),
    }


def translate_sihua(year_gan: str) -> List[Dict]:
    """翻譯年干四化"""
    sihua = get_sihua_by_year_gan(year_gan)
    result = []
    
    for hua_type, star in sihua.items():
        hua_name = f"化{hua_type}"
        detail = get_sihua_detail(star, hua_name)
        result.append(detail)
    
    return result


def generate_sihua_report(year_gan: str) -> str:
    """生成四化報告"""
    sihua_list = translate_sihua(year_gan)
    
    report = f"""【{year_gan}年四化解析】

"""
    for item in sihua_list:
        report += f"""★ {item['star']}{item['hua']}
  • 白話：{item.get('vernacular', '')}
  • 場論：{item.get('field', '')}
  • 現代：{item.get('modern', '')}
  • 建議：{item.get('advice', '')}

"""
    
    return report


if __name__ == "__main__":
    # 測試
    print(generate_sihua_report("癸"))
