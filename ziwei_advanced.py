"""
紫微擴充模組 ziwei_advanced.py v1.0 20260207
=============================================
北斗命數框架擴充：四化詳解、輔星白話翻譯

📚 知識點：
- 四化 = 紫微斗數的動態能量（祿權科忌）
- 輔星 = 14主星以外的重要星曜
- 場論統一詮釋

建立者：北斗 × 織明
XTF任務：B1+B3
"""

from typing import Dict, List, Optional


# =============================================================================
# B1: 四化詳解系統（30%→100%）
# =============================================================================

SIHUA_TRANSLATION = {
    "化祿": {
        "symbol": "祿",
        "vernacular": "好事來了",
        "field": "增益擴張場",
        "effect": "該星曜特質被放大，帶來好處",
        "modern": "機會增加、資源流入、好運加持",
        "strength": "能量增強、好事吸引",
        "weakness": "可能過度膨脹、樂極生悲",
        "advice": "把握機會但不要貪多",
    },
    "化權": {
        "symbol": "權",
        "vernacular": "有話語權",
        "field": "掌控主導場",
        "effect": "該星曜特質變得強勢、有主導權",
        "modern": "決策權、影響力、控制欲",
        "strength": "有權威、能主導、說話有份量",
        "weakness": "可能太強勢、招惹衝突",
        "advice": "善用權力但避免霸道",
    },
    "化科": {
        "symbol": "科",
        "vernacular": "有名聲",
        "field": "聲譽展現場",
        "effect": "該星曜特質帶來聲譽、學識提升",
        "modern": "名聲、學歷、專業認可",
        "strength": "有名氣、受尊重、文質彬彬",
        "weakness": "可能太愛面子、名實不符",
        "advice": "珍惜名聲但要有實力",
    },
    "化忌": {
        "symbol": "忌",
        "vernacular": "這邊卡住了",
        "field": "收縮阻礙場",
        "effect": "該星曜特質被壓制、帶來阻礙",
        "modern": "困難、挫折、執念、功課",
        "strength": "被迫成長、磨練耐心",
        "weakness": "容易不順、執著太深",
        "advice": "化忌是功課，接受學習而非對抗",
    },
}

# 各年干四化表（完整版）
YEAR_SIHUA_TABLE = {
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


def get_sihua_info(sihua_name: str) -> Optional[Dict]:
    """取得四化詳細資訊"""
    return SIHUA_TRANSLATION.get(sihua_name)


def get_year_sihua(year_gan: str) -> Dict[str, str]:
    """根據年干取得四化星"""
    return YEAR_SIHUA_TABLE.get(year_gan, {})


def analyze_sihua_in_gong(star: str, sihua: str, gong: str) -> Dict:
    """
    分析某星在某宮的四化影響
    
    Args:
        star: 星名（如「太陽」）
        sihua: 四化類型（如「化祿」）
        gong: 宮位名（如「命宮」）
    
    Returns:
        分析結果
    """
    sihua_info = SIHUA_TRANSLATION.get(sihua, {})
    
    # 宮位場域定義
    GONG_FIELD = {
        "命宮": ("自我本質", "個人特質被增強"),
        "財帛宮": ("財務狀況", "財運相關影響"),
        "事業宮": ("工作發展", "事業相關影響"),
        "遷移宮": ("外在環境", "外出、人際影響"),
        "夫妻宮": ("感情關係", "婚姻感情影響"),
        "子女宮": ("子女緣分", "子女、創作影響"),
        "兄弟宮": ("手足關係", "兄弟、同儕影響"),
        "父母宮": ("長輩關係", "父母、上司影響"),
        "福德宮": ("精神狀態", "內心、享受影響"),
        "田宅宮": ("不動產運", "房產、家庭影響"),
        "奴僕宮": ("下屬關係", "部屬、朋友影響"),
        "疾厄宮": ("健康狀況", "身體、災厄影響"),
    }
    
    gong_info = GONG_FIELD.get(gong, ("未知領域", ""))
    
    # 組合分析
    return {
        "star": star,
        "sihua": sihua,
        "gong": gong,
        "sihua_vernacular": sihua_info.get("vernacular", ""),
        "sihua_field": sihua_info.get("field", ""),
        "gong_domain": gong_info[0],
        "combined_analysis": f"{star}{sihua}落{gong}：{gong_info[0]}方面{sihua_info.get('vernacular', '')}",
        "advice": sihua_info.get("advice", ""),
    }


def generate_sihua_report(year_gan: str, ming_gong_sihua: List[Dict]) -> Dict:
    """
    生成四化分析報告
    
    Args:
        year_gan: 年干
        ming_gong_sihua: 命宮四化列表
    
    Returns:
        四化分析報告
    """
    sihua_stars = get_year_sihua(year_gan)
    
    report_lines = []
    for sihua_type, star in sihua_stars.items():
        sihua_name = f"化{sihua_type}"
        info = SIHUA_TRANSLATION.get(sihua_name, {})
        report_lines.append({
            "star": star,
            "sihua": sihua_name,
            "vernacular": info.get("vernacular", ""),
            "field": info.get("field", ""),
            "effect": info.get("effect", ""),
            "advice": info.get("advice", ""),
        })
    
    # 特殊組合判斷
    special_notes = []
    if sihua_stars.get("忌") == sihua_stars.get("祿"):
        special_notes.append("祿忌同星：福禍相依，好事中藏隱憂")
    
    return {
        "year_gan": year_gan,
        "sihua_stars": sihua_stars,
        "sihua_details": report_lines,
        "special_notes": special_notes,
    }


# =============================================================================
# B3: 輔星白話翻譯系統
# =============================================================================

AUXILIARY_STARS_TRANSLATION = {
    # 六吉星
    "左輔": {
        "type": "吉",
        "wuxing": "土",
        "vernacular": "左邊有人幫",
        "field": "左側支援場",
        "effect": "有貴人相助、做事有人幫忙",
        "modern": "助手、貴人、團隊支援",
        "strength": "人緣好、有助力",
        "weakness": "可能太依賴他人",
    },
    "右弼": {
        "type": "吉",
        "wuxing": "水",
        "vernacular": "右邊有人挺",
        "field": "右側支援場",
        "effect": "有人支持、背後有靠山",
        "modern": "後援、支持者、資源",
        "strength": "有靠山、不孤單",
        "weakness": "可能被過度保護",
    },
    "文昌": {
        "type": "吉",
        "wuxing": "金",
        "vernacular": "讀書腦袋好",
        "field": "文智提升場",
        "effect": "學習能力強、考試運佳",
        "modern": "學業、文書、證照",
        "strength": "聰明、文才好",
        "weakness": "可能太書呆氣",
    },
    "文曲": {
        "type": "吉",
        "wuxing": "水",
        "vernacular": "藝術細胞多",
        "field": "藝文感知場",
        "effect": "有藝術天份、口才好",
        "modern": "藝術、表演、口才",
        "strength": "有才華、感性",
        "weakness": "可能太感性、不務實",
    },
    "天魁": {
        "type": "吉",
        "wuxing": "火",
        "vernacular": "日間貴人",
        "field": "陽貴護持場",
        "effect": "白天做事順利、有明貴人",
        "modern": "日間活動、正式場合有利",
        "strength": "貴人明顯、運勢好",
        "weakness": "晚上運勢相對弱",
    },
    "天鉞": {
        "type": "吉",
        "wuxing": "火",
        "vernacular": "夜間貴人",
        "field": "陰貴護持場",
        "effect": "夜晚做事順利、有暗貴人",
        "modern": "夜間活動、私下場合有利",
        "strength": "暗中有助力",
        "weakness": "白天運勢相對弱",
    },
    
    # 六煞星
    "火星": {
        "type": "煞",
        "wuxing": "火",
        "vernacular": "急性子、衝動",
        "field": "爆發衝擊場",
        "effect": "做事急躁、容易衝動",
        "modern": "急躁、意外、爆發力",
        "strength": "行動快、有爆發力",
        "weakness": "太衝動、容易出錯",
    },
    "鈴星": {
        "type": "煞",
        "wuxing": "火",
        "vernacular": "悶燒型、陰沉",
        "field": "悶燒累積場",
        "effect": "內心壓抑、累積爆發",
        "modern": "壓力累積、情緒爆發",
        "strength": "忍耐力強",
        "weakness": "容易悶出病來",
    },
    "擎羊": {
        "type": "煞",
        "wuxing": "金",
        "vernacular": "刀鋒般銳利",
        "field": "銳利傷害場",
        "effect": "容易有血光、開刀",
        "modern": "意外傷害、手術",
        "strength": "有魄力、敢拼",
        "weakness": "容易受傷",
    },
    "陀羅": {
        "type": "煞",
        "wuxing": "金",
        "vernacular": "拖泥帶水",
        "field": "糾纏延遲場",
        "effect": "做事拖延、糾纏不清",
        "modern": "拖延、糾紛、反覆",
        "strength": "堅持不放棄",
        "weakness": "太執著、不懂放手",
    },
    "地空": {
        "type": "煞",
        "wuxing": "火",
        "vernacular": "腳踩空氣",
        "field": "虛空損耗場",
        "effect": "容易損失、不切實際",
        "modern": "損失、空想、不務實",
        "strength": "想像力豐富",
        "weakness": "不切實際",
    },
    "地劫": {
        "type": "煞",
        "wuxing": "火",
        "vernacular": "被劫走了",
        "field": "劫奪損失場",
        "effect": "容易被搶、財物損失",
        "modern": "被騙、損失、意外支出",
        "strength": "看淡物質",
        "weakness": "守不住財",
    },
    
    # 其他重要輔星
    "天馬": {
        "type": "中",
        "wuxing": "火",
        "vernacular": "動起來才有運",
        "field": "流動驛動場",
        "effect": "適合出差、旅行、變動",
        "modern": "出差、搬遷、變動",
        "strength": "活動力強",
        "weakness": "靜不下來",
    },
    "紅鸞": {
        "type": "吉",
        "wuxing": "水",
        "vernacular": "桃花朵朵開",
        "field": "情感吸引場",
        "effect": "異性緣好、容易有感情",
        "modern": "戀愛運、結婚機會",
        "strength": "人緣好、有魅力",
        "weakness": "可能太花心",
    },
    "天喜": {
        "type": "吉",
        "wuxing": "水",
        "vernacular": "喜事連連",
        "field": "喜慶共振場",
        "effect": "容易有喜事、心情好",
        "modern": "好消息、喜事、懷孕",
        "strength": "樂觀、有福氣",
        "weakness": "可能太樂觀",
    },
    "祿存": {
        "type": "吉",
        "wuxing": "土",
        "vernacular": "錢財有保障",
        "field": "財富累積場",
        "effect": "財運穩定、能存錢",
        "modern": "正財運、存款、保守理財",
        "strength": "財運穩定",
        "weakness": "可能太保守",
    },
    "天刑": {
        "type": "煞",
        "wuxing": "火",
        "vernacular": "容易官司",
        "field": "法律刑罰場",
        "effect": "容易有官司、法律問題",
        "modern": "官司、罰單、合約糾紛",
        "strength": "有正義感",
        "weakness": "容易惹麻煩",
    },
    "天姚": {
        "type": "中",
        "wuxing": "水",
        "vernacular": "風流韻事",
        "field": "曖昧吸引場",
        "effect": "異性緣強、容易有曖昧",
        "modern": "桃花、曖昧、誘惑",
        "strength": "有魅力",
        "weakness": "可能惹桃花劫",
    },
    "孤辰": {
        "type": "煞",
        "wuxing": "火",
        "vernacular": "男怕孤辰",
        "field": "孤獨隔離場",
        "effect": "容易孤獨、感情不順",
        "modern": "單身、獨處、晚婚",
        "strength": "獨立自主",
        "weakness": "感情運差",
    },
    "寡宿": {
        "type": "煞",
        "wuxing": "火",
        "vernacular": "女怕寡宿",
        "field": "寡居隔離場",
        "effect": "容易孤獨、婚姻不順",
        "modern": "單身、守寡、離婚",
        "strength": "獨立自主",
        "weakness": "婚姻運差",
    },
    "天哭": {
        "type": "煞",
        "wuxing": "金",
        "vernacular": "容易流淚",
        "field": "悲傷共振場",
        "effect": "情緒敏感、容易傷心",
        "modern": "情緒化、傷心事",
        "strength": "感性細膩",
        "weakness": "太容易傷心",
    },
    "天虛": {
        "type": "煞",
        "wuxing": "土",
        "vernacular": "空虛寂寞",
        "field": "虛空失落場",
        "effect": "容易感到空虛、失落",
        "modern": "空虛、失落、不滿足",
        "strength": "追求精神",
        "weakness": "容易不滿足",
    },
    "化祿": SIHUA_TRANSLATION["化祿"],
    "化權": SIHUA_TRANSLATION["化權"],
    "化科": SIHUA_TRANSLATION["化科"],
    "化忌": SIHUA_TRANSLATION["化忌"],
}


def get_auxiliary_star_info(star_name: str) -> Optional[Dict]:
    """取得輔星詳細資訊"""
    return AUXILIARY_STARS_TRANSLATION.get(star_name)


def analyze_auxiliary_stars(star_list: List[str]) -> Dict:
    """
    分析輔星組合
    
    Args:
        star_list: 星曜列表
    
    Returns:
        輔星分析結果
    """
    ji_stars = []
    sha_stars = []
    zhong_stars = []
    
    for star in star_list:
        info = AUXILIARY_STARS_TRANSLATION.get(star)
        if info:
            item = {"star": star, **info}
            if info["type"] == "吉":
                ji_stars.append(item)
            elif info["type"] == "煞":
                sha_stars.append(item)
            else:
                zhong_stars.append(item)
    
    # 特殊組合判斷
    special_combos = []
    star_set = set(star_list)
    
    # 輔弼夾
    if "左輔" in star_set and "右弼" in star_set:
        special_combos.append({"name": "輔弼夾", "effect": "左右逢源，貴人滿滿", "type": "大吉"})
    
    # 昌曲夾
    if "文昌" in star_set and "文曲" in star_set:
        special_combos.append({"name": "昌曲夾", "effect": "才華洋溢，文采出眾", "type": "大吉"})
    
    # 魁鉞夾
    if "天魁" in star_set and "天鉞" in star_set:
        special_combos.append({"name": "魁鉞夾", "effect": "貴人加持，日夜有助", "type": "大吉"})
    
    # 火鈴夾
    if "火星" in star_set and "鈴星" in star_set:
        special_combos.append({"name": "火鈴夾", "effect": "爆發力強但衝動危險", "type": "大凶"})
    
    # 羊陀夾
    if "擎羊" in star_set and "陀羅" in star_set:
        special_combos.append({"name": "羊陀夾", "effect": "前有狼後有虎，進退兩難", "type": "大凶"})
    
    # 空劫夾
    if "地空" in star_set and "地劫" in star_set:
        special_combos.append({"name": "空劫夾", "effect": "財來財去，守不住", "type": "大凶"})
    
    # 紅鸞天喜
    if "紅鸞" in star_set and "天喜" in star_set:
        special_combos.append({"name": "紅鸞天喜", "effect": "感情運大好，喜事臨門", "type": "大吉"})
    
    # 生成總評
    ji_count = len(ji_stars)
    sha_count = len(sha_stars)
    
    if ji_count > sha_count * 2:
        summary = "輔星配置偏吉，有較多助力"
    elif sha_count > ji_count * 2:
        summary = "輔星配置偏凶，需要注意化解"
    else:
        summary = "輔星配置中和，吉凶參半"
    
    return {
        "ji_stars": ji_stars,
        "sha_stars": sha_stars,
        "zhong_stars": zhong_stars,
        "special_combos": special_combos,
        "summary": summary,
        "ji_count": ji_count,
        "sha_count": sha_count,
    }


# =============================================================================
# 整合：紫微進階分析
# =============================================================================

def generate_ziwei_advanced_report(
    year_gan: str,
    ming_gong_stars: List[str],
    all_stars: List[str]
) -> Dict:
    """
    生成紫微進階分析報告
    
    Args:
        year_gan: 年干
        ming_gong_stars: 命宮星曜
        all_stars: 所有星曜
    
    Returns:
        進階分析報告
    """
    # 四化分析
    sihua_report = generate_sihua_report(year_gan, [])
    
    # 輔星分析
    auxiliary_analysis = analyze_auxiliary_stars(all_stars)
    
    return {
        "sihua": sihua_report,
        "auxiliary": auxiliary_analysis,
        "summary": f"年干{year_gan}四化，{auxiliary_analysis['summary']}",
    }


# =============================================================================
# 測試
# =============================================================================

if __name__ == "__main__":
    # 測試四化
    sihua_report = generate_sihua_report("甲", [])
    print("甲年四化:", sihua_report["sihua_stars"])
    
    # 測試輔星
    test_stars = ["左輔", "右弼", "文昌", "火星", "天馬"]
    aux_analysis = analyze_auxiliary_stars(test_stars)
    print("輔星分析:", aux_analysis["summary"])
    print("特殊組合:", aux_analysis["special_combos"])
