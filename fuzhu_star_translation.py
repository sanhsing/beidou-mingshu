"""
紫微輔星白話翻譯 fuzhu_star_translation.py v1.0
==============================================
XTF任務：消-B3 | 執行星：璃語（介面）+ 理樞（分析）

核心本質：輔星 = 吉星6 + 煞星6 + 雜曜
輔星是紫微斗數中輔助14主星的星曜

📚 輔星分類：
- 六吉星：左輔、右弼、天魁、天鉞、文昌、文曲
- 六煞星：擎羊、陀羅、火星、鈴星、地空、地劫
- 四化輔星：祿存、天馬、化祿、化權、化科、化忌
- 雜曜：天刑、天姚、紅鸞、天喜等
"""

from typing import Dict, List, Optional

# ============================================================
# 六吉星
# ============================================================

LIUJI_STARS = {
    "左輔": {
        "wuxing": "土",
        "category": "吉星",
        "pair": "右弼",
        "classic": "左輔主助力、貴人",
        "vernacular": "有人幫忙、助力多",
        "field": "左方輔助場",
        "modern": "有貴人、有助手、人脈廣",
        "strength": "有人幫忙、做事有助力、團隊運好",
        "weakness": "可能依賴他人",
        "in_ming": "命宮有左輔，一生多貴人相助",
        "in_career": "事業有貴人、有好同事",
        "in_wealth": "財運有助力、合作生財",
        "advice": "珍惜貴人，也要提升自己能力",
    },
    "右弼": {
        "wuxing": "水",
        "category": "吉星",
        "pair": "左輔",
        "classic": "右弼主助力、貴人",
        "vernacular": "有人幫忙、助力多",
        "field": "右方輔助場",
        "modern": "有貴人、有助手、人脈廣",
        "strength": "有人幫忙、做事有助力、團隊運好",
        "weakness": "可能依賴他人",
        "in_ming": "命宮有右弼，一生多貴人相助",
        "in_career": "事業有貴人、有好同事",
        "in_wealth": "財運有助力、合作生財",
        "advice": "珍惜貴人，也要提升自己能力",
    },
    "天魁": {
        "wuxing": "火",
        "category": "吉星",
        "pair": "天鉞",
        "classic": "天魁主陽貴人、男性貴人",
        "vernacular": "有男性貴人相助",
        "field": "陽性貴人場",
        "modern": "男性貴人、長官、父輩相助",
        "strength": "有權威人士相助、長官緣好",
        "weakness": "可能太依賴長官",
        "in_ming": "命宮有天魁，有男性貴人、長官提拔",
        "in_career": "事業有長官支持、升遷有望",
        "in_wealth": "財運有權威人士相助",
        "advice": "尊重長輩，贏得賞識",
    },
    "天鉞": {
        "wuxing": "火",
        "category": "吉星",
        "pair": "天魁",
        "classic": "天鉞主陰貴人、女性貴人",
        "vernacular": "有女性貴人相助",
        "field": "陰性貴人場",
        "modern": "女性貴人、母輩、暗中相助",
        "strength": "有女性相助、暗中有貴人",
        "weakness": "可能不知道誰在幫你",
        "in_ming": "命宮有天鉞，有女性貴人、暗中有人相助",
        "in_career": "事業有女性支持、暗中有貴人",
        "in_wealth": "財運有暗中相助",
        "advice": "善待身邊女性，貴人可能在身邊",
    },
    "文昌": {
        "wuxing": "金",
        "category": "吉星",
        "pair": "文曲",
        "classic": "文昌主文才、考試、學業",
        "vernacular": "頭腦好、讀書行、考運佳",
        "field": "正統文才場",
        "modern": "學習能力強、考試順利、文書工作好",
        "strength": "聰明、學習力強、表達能力好",
        "weakness": "可能太書生氣",
        "in_ming": "命宮有文昌，聰明好學、考運佳",
        "in_career": "事業適合文職、教育、研究",
        "in_wealth": "靠知識技能賺錢",
        "advice": "把學習能力轉化為競爭優勢",
    },
    "文曲": {
        "wuxing": "水",
        "category": "吉星",
        "pair": "文昌",
        "classic": "文曲主藝術、才華、桃花",
        "vernacular": "有藝術天分、有魅力",
        "field": "藝術才華場",
        "modern": "藝術才華、創意、異性緣好",
        "strength": "有藝術天分、創意好、有魅力",
        "weakness": "可能太感性、桃花複雜",
        "in_ming": "命宮有文曲，有藝術天分、異性緣佳",
        "in_career": "事業適合藝術、創意、娛樂",
        "in_wealth": "靠才華創意賺錢",
        "advice": "發揮藝術天分，但感情要有分寸",
    },
}

# ============================================================
# 六煞星
# ============================================================

LIUSHA_STARS = {
    "擎羊": {
        "wuxing": "金",
        "category": "煞星",
        "pair": "陀羅",
        "classic": "擎羊主剛烈、是非、血光",
        "vernacular": "個性衝、容易有是非",
        "field": "正面衝擊場",
        "modern": "個性剛烈、衝動、容易起衝突",
        "strength": "有魄力、敢拼敢衝、執行力強",
        "weakness": "易衝動、惹是非、有血光風險",
        "in_ming": "命宮有擎羊，個性剛烈、易有是非",
        "in_career": "事業有衝勁但易起衝突",
        "in_wealth": "財來財去、進出大",
        "advice": "收斂鋒芒，把衝勁用在正途",
    },
    "陀羅": {
        "wuxing": "金",
        "category": "煞星",
        "pair": "擎羊",
        "classic": "陀羅主拖延、糾纏、暗損",
        "vernacular": "事情拖拉、暗中有阻礙",
        "field": "暗中拖延場",
        "modern": "做事拖延、暗中有小人、糾纏不清",
        "strength": "謹慎、考慮周全",
        "weakness": "拖延、糾纏、暗中受損",
        "in_ming": "命宮有陀羅，做事易拖延、暗中有阻礙",
        "in_career": "事業進展緩慢、有暗中阻礙",
        "in_wealth": "財運有暗損、被人算計",
        "advice": "提高效率，防範暗中小人",
    },
    "火星": {
        "wuxing": "火",
        "category": "煞星",
        "pair": "鈴星",
        "classic": "火星主急躁、爆發、災禍",
        "vernacular": "性子急、容易爆發",
        "field": "急躁爆發場",
        "modern": "性格急躁、做事快但草率",
        "strength": "行動力強、反應快",
        "weakness": "太急躁、易出錯、情緒失控",
        "in_ming": "命宮有火星，性格急躁、易衝動",
        "in_career": "事業求快但易出錯",
        "in_wealth": "財來得快去得也快",
        "advice": "培養耐心，欲速則不達",
    },
    "鈴星": {
        "wuxing": "火",
        "category": "煞星",
        "pair": "火星",
        "classic": "鈴星主暴躁、孤獨、災禍",
        "vernacular": "脾氣暴、內心孤獨",
        "field": "暴躁孤獨場",
        "modern": "脾氣不好、內心孤獨、難以親近",
        "strength": "獨立、不依賴",
        "weakness": "孤獨、暴躁、難相處",
        "in_ming": "命宮有鈴星，脾氣暴躁、內心孤獨",
        "in_career": "事業獨立但人際關係差",
        "in_wealth": "財運起伏大",
        "advice": "控制情緒，學會與人相處",
    },
    "地空": {
        "wuxing": "火",
        "category": "煞星",
        "pair": "地劫",
        "classic": "地空主虛空、落空、玄學",
        "vernacular": "想法多但難落實，有玄學天分",
        "field": "虛空創意場",
        "modern": "想法多但不實際、有哲學/玄學傾向",
        "strength": "想像力豐富、有哲學思維",
        "weakness": "太虛、不實際、錢財易空",
        "in_ming": "命宮有地空，想法多但難落實",
        "in_career": "事業宜創意、玄學、宗教",
        "in_wealth": "財運虛空、難以積累",
        "advice": "把想法落實，腳踏實地",
    },
    "地劫": {
        "wuxing": "火",
        "category": "煞星",
        "pair": "地空",
        "classic": "地劫主破財、損失、玄學",
        "vernacular": "容易有損失，有玄學天分",
        "field": "劫財損失場",
        "modern": "容易破財、有損失、有玄學傾向",
        "strength": "看得開、不執著於物質",
        "weakness": "破財、損失、難以積累",
        "in_ming": "命宮有地劫，財運易有損失",
        "in_career": "事業宜創意、玄學、宗教",
        "in_wealth": "財運有劫、容易破財",
        "advice": "謹慎理財，接受無常",
    },
}

# ============================================================
# 其他重要輔星
# ============================================================

OTHER_STARS = {
    "祿存": {
        "wuxing": "土",
        "category": "財星",
        "classic": "祿存主正財、俸祿、穩定收入",
        "vernacular": "有穩定收入、財運穩",
        "field": "穩定財源場",
        "modern": "薪水穩定、有正財、理財保守",
        "strength": "財運穩定、有固定收入",
        "weakness": "可能太保守、格局不大",
        "in_ming": "命宮有祿存，財運穩定、有正財",
        "in_career": "事業收入穩定、適合體制內",
        "in_wealth": "財運好、有存款",
        "advice": "穩健理財，適度投資",
    },
    "天馬": {
        "wuxing": "火",
        "category": "動星",
        "classic": "天馬主遷動、出差、變化",
        "vernacular": "愛動、常變動、有出國運",
        "field": "流動變化場",
        "modern": "出差多、換工作、搬家、出國",
        "strength": "機會多、見識廣、不會悶",
        "weakness": "太動盪、難以安定",
        "in_ming": "命宮有天馬，一生多變動、愛奔波",
        "in_career": "事業需要出差、變動性工作",
        "in_wealth": "財運流動性大",
        "advice": "動中求穩，把變動變成機會",
    },
    "天刑": {
        "wuxing": "火",
        "category": "中性",
        "classic": "天刑主法律、紀律、孤獨",
        "vernacular": "重紀律、適合法律相關",
        "field": "法律紀律場",
        "modern": "適合法律、軍警、紀律性工作",
        "strength": "有原則、重紀律、公正",
        "weakness": "可能太嚴肅、孤獨",
        "in_ming": "命宮有天刑，重紀律、適合法律軍警",
        "in_career": "事業適合法律、軍警、監察",
        "in_wealth": "財運中等",
        "advice": "堅持原則，但也要有彈性",
    },
    "天姚": {
        "wuxing": "水",
        "category": "桃花",
        "classic": "天姚主桃花、人緣、異性緣",
        "vernacular": "有魅力、異性緣好",
        "field": "魅力桃花場",
        "modern": "有魅力、異性緣佳、社交能力強",
        "strength": "人緣好、有魅力、擅長社交",
        "weakness": "可能感情複雜、爛桃花",
        "in_ming": "命宮有天姚，有魅力、異性緣佳",
        "in_career": "事業適合公關、服務、娛樂",
        "in_wealth": "財運可藉人脈賺錢",
        "advice": "善用魅力但要有界限",
    },
    "紅鸞": {
        "wuxing": "水",
        "category": "桃花",
        "classic": "紅鸞主婚姻、喜事、桃花",
        "vernacular": "有婚姻運、喜事臨門",
        "field": "婚姻喜慶場",
        "modern": "婚姻運好、有喜事、感情順利",
        "strength": "感情順利、有婚姻緣",
        "weakness": "可能太早結婚",
        "in_ming": "命宮有紅鸞，感情順利、有婚姻運",
        "in_career": "事業適合婚慶、服務",
        "in_wealth": "財運因婚姻而變化",
        "advice": "把握姻緣，經營感情",
    },
    "天喜": {
        "wuxing": "水",
        "category": "桃花",
        "classic": "天喜主喜事、生育、桃花",
        "vernacular": "有喜事、生育運好",
        "field": "喜事生育場",
        "modern": "有喜事、生育順利、心情愉快",
        "strength": "有喜事、心情好、生育運好",
        "weakness": "無明顯負面",
        "in_ming": "命宮有天喜，有喜事、生育運好",
        "in_career": "事業適合服務、母嬰相關",
        "in_wealth": "財運因喜事而增加",
        "advice": "保持喜悅心情，迎接好事",
    },
    "天哭": {
        "wuxing": "金",
        "category": "煞星",
        "classic": "天哭主悲傷、哭泣、喪事",
        "vernacular": "容易傷心、有悲傷事",
        "field": "悲傷情緒場",
        "modern": "情緒低落、容易傷心、有喪事",
        "strength": "感受力強、有同理心",
        "weakness": "容易悲傷、情緒化",
        "in_ming": "命宮有天哭，情緒容易低落",
        "in_career": "事業適合需要同理心的工作",
        "in_wealth": "財運可能因情緒影響",
        "advice": "調節情緒，把同理心轉化為能力",
    },
    "華蓋": {
        "wuxing": "木",
        "category": "中性",
        "classic": "華蓋主孤獨、藝術、宗教",
        "vernacular": "有藝術天分、獨立、可能孤獨",
        "field": "藝術孤獨場",
        "modern": "藝術天分、獨立思考、不合群",
        "strength": "有藝術天分、思想獨特",
        "weakness": "孤獨、不合群",
        "in_ming": "命宮有華蓋，有藝術天分、獨立",
        "in_career": "事業適合藝術、宗教、研究",
        "in_wealth": "財運靠專業技能",
        "advice": "把孤獨轉化為創作力",
    },
}

# 合併所有輔星
ALL_FUZHU_STARS = {**LIUJI_STARS, **LIUSHA_STARS, **OTHER_STARS}


def get_fuzhu_star_info(star_name: str) -> Dict:
    """取得輔星詳細資訊"""
    return ALL_FUZHU_STARS.get(star_name, {})


def translate_fuzhu_stars(star_list: List[str]) -> List[Dict]:
    """批量翻譯輔星"""
    result = []
    for star in star_list:
        info = get_fuzhu_star_info(star)
        if info:
            result.append({"star": star, **info})
    return result


def generate_fuzhu_report(gong_name: str, stars: List[str]) -> str:
    """生成某宮位輔星報告"""
    if not stars:
        return f"【{gong_name}輔星】無\n"
    
    report = f"【{gong_name}輔星分析】\n"
    
    ji = [s for s in stars if get_fuzhu_star_info(s).get("category") == "吉星"]
    sha = [s for s in stars if get_fuzhu_star_info(s).get("category") == "煞星"]
    other = [s for s in stars if get_fuzhu_star_info(s).get("category") not in ["吉星", "煞星"]]
    
    if ji:
        report += "\n★ 吉星：\n"
        for star in ji:
            info = get_fuzhu_star_info(star)
            report += f"  • {star}：{info.get('vernacular', '')}\n"
            report += f"    場論：{info.get('field', '')} | 優勢：{info.get('strength', '')}\n"
    
    if sha:
        report += "\n★ 煞星：\n"
        for star in sha:
            info = get_fuzhu_star_info(star)
            report += f"  • {star}：{info.get('vernacular', '')}\n"
            report += f"    場論：{info.get('field', '')} | 注意：{info.get('weakness', '')}\n"
    
    if other:
        report += "\n★ 其他：\n"
        for star in other:
            info = get_fuzhu_star_info(star)
            report += f"  • {star}：{info.get('vernacular', '')}\n"
    
    return report


def analyze_fuzhu_balance(stars: List[str]) -> Dict:
    """分析輔星吉凶平衡"""
    ji_count = sum(1 for s in stars if get_fuzhu_star_info(s).get("category") == "吉星")
    sha_count = sum(1 for s in stars if get_fuzhu_star_info(s).get("category") == "煞星")
    
    if ji_count > sha_count + 1:
        balance = "吉多煞少，整體有利"
    elif sha_count > ji_count + 1:
        balance = "煞多吉少，需要注意"
    else:
        balance = "吉凶相當，需看配合"
    
    return {
        "ji_count": ji_count,
        "sha_count": sha_count,
        "balance": balance,
    }


if __name__ == "__main__":
    # 測試
    test_stars = ["左輔", "文昌", "擎羊", "天馬"]
    
    print("【輔星翻譯測試】")
    for item in translate_fuzhu_stars(test_stars):
        print(f"\n{item['star']}:")
        print(f"  白話：{item.get('vernacular', '')}")
        print(f"  場論：{item.get('field', '')}")
        print(f"  優勢：{item.get('strength', '')}")
        print(f"  注意：{item.get('weakness', '')}")
    
    print("\n" + generate_fuzhu_report("命宮", test_stars))
    print(analyze_fuzhu_balance(test_stars))
