"""
八字神煞白話翻譯 shensha_translation.py v1.0
============================================
XTF任務：消-B2 | 執行星：璃語（介面）+ 理樞（分析）

核心本質：神煞 = 吉神 + 凶煞，各有現代詮釋
神煞是古人對特定干支組合的經驗總結

📚 神煞分類：
- 吉神：天乙貴人、文昌、驛馬、天德、月德等
- 凶煞：羊刃、亡神、劫煞、華蓋、孤辰寡宿等
- 中性：桃花、將星、天醫等（看配合）

⚠️ 認識論聲明：
神煞只是經驗統計，非決定性因素
現代應用重在理解其象徵意義
"""

from typing import Dict, List, Optional, Tuple

# ============================================================
# 天干地支基礎
# ============================================================

GAN = ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"]
ZHI = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]

# ============================================================
# 吉神定義與白話
# ============================================================

JISHEN = {
    "天乙貴人": {
        "category": "吉神",
        "rank": 1,  # 重要程度
        "classic": "天乙貴人，命中最吉之神",
        "vernacular": "有貴人相助，遇難呈祥",
        "field": "貴人資源場",
        "modern": "總有人幫忙、關鍵時刻有人拉一把",
        "positive": "人脈好、有靠山、化險為夷",
        "negative": "依賴性可能較強",
        "advice": "珍惜貴人，但也要有自己的能力",
        "lookup": {  # 日干查地支
            "甲": ["丑", "未"], "乙": ["子", "申"], "丙": ["亥", "酉"],
            "丁": ["亥", "酉"], "戊": ["丑", "未"], "己": ["子", "申"],
            "庚": ["丑", "未"], "辛": ["寅", "午"], "壬": ["卯", "巳"],
            "癸": ["卯", "巳"],
        },
    },
    "文昌": {
        "category": "吉神",
        "rank": 2,
        "classic": "文昌貴人，主聰明好學",
        "vernacular": "頭腦好、學習力強、考運佳",
        "field": "智慧學習場",
        "modern": "學霸潛質、考試順利、學習能力強",
        "positive": "讀書好、表達能力強、文書工作順利",
        "negative": "可能太書生氣",
        "advice": "把學習能力轉化為實際能力",
        "lookup": {
            "甲": ["巳"], "乙": ["午"], "丙": ["申"], "丁": ["酉"],
            "戊": ["申"], "己": ["酉"], "庚": ["亥"], "辛": ["子"],
            "壬": ["寅"], "癸": ["卯"],
        },
    },
    "驛馬": {
        "category": "吉神",
        "rank": 3,
        "classic": "驛馬主奔波、遷動、出國",
        "vernacular": "愛動、常出差、有機會出國",
        "field": "流動遷移場",
        "modern": "出差多、換工作、搬家、出國機會",
        "positive": "見多識廣、機會多、不會悶",
        "negative": "可能太奔波、難以安定",
        "advice": "動中求穩，把奔波變成資源",
        "lookup": {  # 年支或日支三合局查
            "申子辰": "寅", "寅午戌": "申", "巳酉丑": "亥", "亥卯未": "巳",
        },
    },
    "天德": {
        "category": "吉神",
        "rank": 4,
        "classic": "天德貴人，能化凶為吉",
        "vernacular": "老天保佑，有驚無險",
        "field": "天佑護持場",
        "modern": "運氣好、災難總能化解、有福氣",
        "positive": "逢凶化吉、有福報、善有善報",
        "negative": "可能太依賴運氣",
        "advice": "福氣要靠德行維持",
        "lookup": {  # 月支查天干
            "寅": "丙", "卯": "丁", "辰": "壬", "巳": "辛",
            "午": "甲", "未": "癸", "申": "壬", "酉": "辛",
            "戌": "丙", "亥": "甲", "子": "癸", "丑": "庚",
        },
    },
    "月德": {
        "category": "吉神",
        "rank": 5,
        "classic": "月德貴人，主福厚德重",
        "vernacular": "有福德、人緣好、得人疼",
        "field": "福德人緣場",
        "modern": "人緣好、受人喜歡、有福氣",
        "positive": "好人緣、有人幫、積善成德",
        "negative": "可能太好說話",
        "advice": "用好人緣創造價值",
        "lookup": {  # 月支查天干
            "寅午戌": "丙", "申子辰": "壬", "亥卯未": "甲", "巳酉丑": "庚",
        },
    },
    "將星": {
        "category": "吉神",
        "rank": 6,
        "classic": "將星主權柄、領導",
        "vernacular": "有領導氣質、能服眾",
        "field": "領導權威場",
        "modern": "有領導力、能帶團隊、有威嚴",
        "positive": "天生領袖、說話有份量",
        "negative": "可能太強勢",
        "advice": "用領導力創造價值，但要傾聽",
        "lookup": {  # 年支或日支查
            "申子辰": "子", "寅午戌": "午", "巳酉丑": "酉", "亥卯未": "卯",
        },
    },
    "天醫": {
        "category": "吉神",
        "rank": 7,
        "classic": "天醫主醫藥、救人",
        "vernacular": "適合醫療相關、有治癒能力",
        "field": "療癒救助場",
        "modern": "醫療工作、諮詢、療癒、助人",
        "positive": "有治癒力、適合助人工作",
        "negative": "可能太操心別人",
        "advice": "把療癒能力專業化",
        "lookup": {  # 月支查
            "寅": "丑", "卯": "寅", "辰": "卯", "巳": "辰",
            "午": "巳", "未": "午", "申": "未", "酉": "申",
            "戌": "酉", "亥": "戌", "子": "亥", "丑": "子",
        },
    },
    "金輿": {
        "category": "吉神",
        "rank": 8,
        "classic": "金輿主車馬、出行",
        "vernacular": "出行順利、有好車坐",
        "field": "交通出行場",
        "modern": "交通順利、有人接送、出行安全",
        "positive": "出行順、交通緣好",
        "negative": "無明顯負面",
        "advice": "善用交通便利擴大活動範圍",
        "lookup": {
            "甲": ["辰"], "乙": ["巳"], "丙": ["未"], "丁": ["申"],
            "戊": ["未"], "己": ["申"], "庚": ["戌"], "辛": ["亥"],
            "壬": ["丑"], "癸": ["寅"],
        },
    },
}

# ============================================================
# 凶煞定義與白話
# ============================================================

XIONGSHA = {
    "羊刃": {
        "category": "凶煞",
        "rank": 1,
        "classic": "羊刃主剛強、暴躁、血光",
        "vernacular": "個性強、脾氣大、要注意安全",
        "field": "剛烈衝突場",
        "modern": "性格剛烈、容易衝動、要注意身體",
        "positive": "有魄力、敢拼敢衝",
        "negative": "衝動、易怒、有血光之災風險",
        "advice": "收斂鋒芒，把剛強用在正途",
        "lookup": {  # 日干查
            "甲": "卯", "乙": "寅", "丙": "午", "丁": "巳",
            "戊": "午", "己": "巳", "庚": "酉", "辛": "申",
            "壬": "子", "癸": "亥",
        },
    },
    "劫煞": {
        "category": "凶煞",
        "rank": 2,
        "classic": "劫煞主損失、被劫",
        "vernacular": "注意財物損失、小人侵害",
        "field": "損失劫奪場",
        "modern": "防盜、防詐騙、注意財務安全",
        "positive": "有警覺心可以避險",
        "negative": "可能有財物損失、遇小人",
        "advice": "謹慎理財，防人之心不可無",
        "lookup": {  # 年支或日支查
            "申子辰": "巳", "寅午戌": "亥", "巳酉丑": "寅", "亥卯未": "申",
        },
    },
    "亡神": {
        "category": "凶煞",
        "rank": 3,
        "classic": "亡神主虛耗、損失",
        "vernacular": "容易虛耗、不實際",
        "field": "虛耗消散場",
        "modern": "精力消耗、做白工、效率低",
        "positive": "警示作用，提醒要務實",
        "negative": "可能白忙一場",
        "advice": "做事要務實，避免虛耗",
        "lookup": {
            "申子辰": "亥", "寅午戌": "巳", "巳酉丑": "申", "亥卯未": "寅",
        },
    },
    "華蓋": {
        "category": "中性",
        "rank": 4,
        "classic": "華蓋主孤獨、藝術、宗教",
        "vernacular": "有藝術天分，但可能孤獨",
        "field": "藝術孤高場",
        "modern": "藝術家、宗教、獨立工作、不合群",
        "positive": "有藝術天分、獨立思考",
        "negative": "可能孤僻、不合群",
        "advice": "把孤獨轉化為創作力",
        "lookup": {
            "申子辰": "辰", "寅午戌": "戌", "巳酉丑": "丑", "亥卯未": "未",
        },
    },
    "孤辰": {
        "category": "凶煞",
        "rank": 5,
        "classic": "孤辰主孤獨、離群",
        "vernacular": "個性獨立，可能較孤獨",
        "field": "孤獨離群場",
        "modern": "獨立性強、不喜群體、獨來獨往",
        "positive": "獨立自主、不依賴",
        "negative": "可能太孤僻、難以合作",
        "advice": "保持獨立但也要學會合作",
        "lookup": {
            "亥子丑": "寅", "寅卯辰": "巳", "巳午未": "申", "申酉戌": "亥",
        },
    },
    "寡宿": {
        "category": "凶煞",
        "rank": 6,
        "classic": "寡宿主孤寡、感情不順",
        "vernacular": "感情路可能較坎坷",
        "field": "感情孤寂場",
        "modern": "感情較遲、獨立、不喜被束縛",
        "positive": "獨立自主、不依賴伴侶",
        "negative": "可能感情不順",
        "advice": "經營感情要用心，別太獨立",
        "lookup": {
            "亥子丑": "戌", "寅卯辰": "丑", "巳午未": "辰", "申酉戌": "未",
        },
    },
    "桃花": {
        "category": "中性",
        "rank": 7,
        "classic": "桃花主感情、人緣",
        "vernacular": "有魅力、人緣好、異性緣佳",
        "field": "魅力人緣場",
        "modern": "有魅力、異性緣好、社交能力強",
        "positive": "人緣好、有魅力、容易受歡迎",
        "negative": "可能感情複雜、爛桃花",
        "advice": "善用魅力但要有界限",
        "lookup": {
            "申子辰": "酉", "寅午戌": "卯", "巳酉丑": "午", "亥卯未": "子",
        },
    },
    "空亡": {
        "category": "凶煞",
        "rank": 8,
        "classic": "空亡主虛空、落空",
        "vernacular": "有些事可能落空、不實際",
        "field": "虛空落空場",
        "modern": "計畫可能落空、要有備案",
        "positive": "可以放下執著",
        "negative": "可能白忙一場",
        "advice": "做事要有備案，接受無常",
        # 空亡計算較複雜，需要甲子旬
    },
    "血刃": {
        "category": "凶煞",
        "rank": 9,
        "classic": "血刃主血光、受傷",
        "vernacular": "注意身體安全、避免受傷",
        "field": "血光傷害場",
        "modern": "注意交通安全、避免危險活動",
        "positive": "警示作用",
        "negative": "可能有血光之災",
        "advice": "注意安全，避免危險",
        "lookup": {  # 月支查
            "寅": "丑", "卯": "寅", "辰": "卯", "巳": "辰",
            "午": "巳", "未": "午", "申": "未", "酉": "申",
            "戌": "酉", "亥": "戌", "子": "亥", "丑": "子",
        },
    },
}

# ============================================================
# 神煞查詢函數
# ============================================================

def find_shensha(day_gan: str, pillars: Dict[str, str]) -> List[Dict]:
    """查詢八字中的神煞"""
    result = []
    
    # 取得所有地支
    all_zhi = [p[1] for p in pillars.values()]
    year_zhi = pillars["year"][1]
    month_zhi = pillars["month"][1]
    day_zhi = pillars["day"][1]
    
    # 判斷年支所屬三合局
    san_he_groups = {
        "申": "申子辰", "子": "申子辰", "辰": "申子辰",
        "寅": "寅午戌", "午": "寅午戌", "戌": "寅午戌",
        "巳": "巳酉丑", "酉": "巳酉丑", "丑": "巳酉丑",
        "亥": "亥卯未", "卯": "亥卯未", "未": "亥卯未",
    }
    san_he = san_he_groups.get(year_zhi, "")
    
    # 查吉神
    for name, info in JISHEN.items():
        lookup = info.get("lookup", {})
        
        # 天乙、文昌、金輿：日干查地支
        if name in ["天乙貴人", "文昌", "金輿"]:
            targets = lookup.get(day_gan, [])
            if isinstance(targets, str):
                targets = [targets]
            for zhi in all_zhi:
                if zhi in targets:
                    result.append({
                        "name": name,
                        "category": info["category"],
                        "found_in": zhi,
                        "vernacular": info["vernacular"],
                        "field": info["field"],
                        "modern": info["modern"],
                        "positive": info["positive"],
                        "negative": info["negative"],
                        "advice": info["advice"],
                    })
                    break
        
        # 驛馬、將星、天醫等：三合局查
        elif name in ["驛馬", "將星"]:
            target = lookup.get(san_he, "")
            if target and target in all_zhi:
                result.append({
                    "name": name,
                    "category": info["category"],
                    "found_in": target,
                    "vernacular": info["vernacular"],
                    "field": info["field"],
                    "modern": info["modern"],
                    "positive": info["positive"],
                    "negative": info["negative"],
                    "advice": info["advice"],
                })
        
        # 天德、月德：月支查天干
        elif name in ["天德"]:
            target = lookup.get(month_zhi, "")
            all_gan = [p[0] for p in pillars.values()]
            if target and target in all_gan:
                result.append({
                    "name": name,
                    "category": info["category"],
                    "found_in": target,
                    "vernacular": info["vernacular"],
                    "field": info["field"],
                    "modern": info["modern"],
                    "positive": info["positive"],
                    "negative": info["negative"],
                    "advice": info["advice"],
                })
        
        # 天醫：月支查地支
        elif name == "天醫":
            target = lookup.get(month_zhi, "")
            if target and target in all_zhi:
                result.append({
                    "name": name,
                    "category": info["category"],
                    "found_in": target,
                    "vernacular": info["vernacular"],
                    "field": info["field"],
                    "modern": info["modern"],
                    "positive": info["positive"],
                    "negative": info["negative"],
                    "advice": info["advice"],
                })
    
    # 查凶煞
    for name, info in XIONGSHA.items():
        lookup = info.get("lookup", {})
        
        # 羊刃：日干查地支
        if name == "羊刃":
            target = lookup.get(day_gan, "")
            if target and target in all_zhi:
                result.append({
                    "name": name,
                    "category": info["category"],
                    "found_in": target,
                    "vernacular": info["vernacular"],
                    "field": info["field"],
                    "modern": info["modern"],
                    "positive": info["positive"],
                    "negative": info["negative"],
                    "advice": info["advice"],
                })
        
        # 劫煞、亡神、華蓋、桃花：三合局查
        elif name in ["劫煞", "亡神", "華蓋", "桃花"]:
            target = lookup.get(san_he, "")
            if target and target in all_zhi:
                result.append({
                    "name": name,
                    "category": info["category"],
                    "found_in": target,
                    "vernacular": info["vernacular"],
                    "field": info["field"],
                    "modern": info["modern"],
                    "positive": info["positive"],
                    "negative": info["negative"],
                    "advice": info["advice"],
                })
        
        # 孤辰、寡宿：年支三方查
        elif name in ["孤辰", "寡宿"]:
            fang_groups = {
                "亥": "亥子丑", "子": "亥子丑", "丑": "亥子丑",
                "寅": "寅卯辰", "卯": "寅卯辰", "辰": "寅卯辰",
                "巳": "巳午未", "午": "巳午未", "未": "巳午未",
                "申": "申酉戌", "酉": "申酉戌", "戌": "申酉戌",
            }
            fang = fang_groups.get(year_zhi, "")
            target = lookup.get(fang, "")
            if target and target in all_zhi:
                result.append({
                    "name": name,
                    "category": info["category"],
                    "found_in": target,
                    "vernacular": info["vernacular"],
                    "field": info["field"],
                    "modern": info["modern"],
                    "positive": info["positive"],
                    "negative": info["negative"],
                    "advice": info["advice"],
                })
    
    return result


def generate_shensha_report(day_gan: str, pillars: Dict[str, str]) -> str:
    """生成神煞報告"""
    shensha_list = find_shensha(day_gan, pillars)
    
    jishen = [s for s in shensha_list if s["category"] == "吉神"]
    xiongsha = [s for s in shensha_list if s["category"] in ["凶煞", "中性"]]
    
    report = """【神煞分析】

"""
    
    if jishen:
        report += "【吉神】\n"
        for s in jishen:
            report += f"""
★ {s['name']}（見於{s['found_in']}）
  • 白話：{s['vernacular']}
  • 場論：{s['field']}
  • 現代：{s['modern']}
  • 優勢：{s['positive']}
  • 建議：{s['advice']}
"""
    else:
        report += "【吉神】無明顯吉神\n"
    
    report += "\n"
    
    if xiongsha:
        report += "【凶煞/中性】\n"
        for s in xiongsha:
            report += f"""
★ {s['name']}（見於{s['found_in']}）— {s['category']}
  • 白話：{s['vernacular']}
  • 場論：{s['field']}
  • 現代：{s['modern']}
  • 注意：{s['negative']}
  • 建議：{s['advice']}
"""
    else:
        report += "【凶煞】無明顯凶煞\n"
    
    report += """
【場論詮釋】
神煞是古人對特定干支組合的經驗總結。
吉神代表有利的能量場，凶煞提醒要注意的風險。
現代應用重在理解其象徵意義，而非迷信吉凶。
"""
    
    return report


if __name__ == "__main__":
    # 測試：1973年12月30日酉時生（北斗）
    pillars = {
        "year": "癸丑",
        "month": "甲子",
        "day": "庚子",
        "hour": "乙酉",
    }
    
    print(generate_shensha_report("庚", pillars))
