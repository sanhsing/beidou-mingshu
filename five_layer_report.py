#!/usr/bin/env python3
"""
北斗命數 五層報告系統 v1.0
==========================
每個方法都有完整五層結構：

1. 術數數值（依古代典籍方式計算）
2. 原文（古文+專業術語）
3. 白話翻譯
4. 場論（現代實例）
5. 個人決策分析（SWOT）

北斗七星文創 × 織明 | 2026-02-15
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any

# ============================================================
# 【一、十神五層翻譯】
# ============================================================
SHISHEN_FIVE_LAYER = {
    "比肩": {
        # 1. 術數數值
        "calculation": {
            "method": "日干與他干同五行同陰陽",
            "formula": "甲見甲、乙見乙、丙見丙...",
            "source": "《淵海子平》：比者，同類相幫也",
        },
        # 2. 原文（古文+專業術語）
        "classic": {
            "original": "比肩者，陰見陰、陽見陽，同類相見也。主自尊心強，性格剛毅，不屈不撓。",
            "terminology": ["比肩", "同類", "日主", "幫身"],
            "source": "《三命通會》《子平真詮》",
        },
        # 3. 白話翻譯
        "vernacular": {
            "meaning": "合作的夥伴",
            "explanation": "比肩就像你的同事、朋友，跟你做一樣的事，能幫你分擔工作，但也可能分走資源。",
            "analogy": "就像創業合夥人，能一起打拼，但要談清楚股份分配。",
        },
        # 4. 場論（現代實例）
        "field_theory": {
            "field_name": "同頻共振場",
            "physics": "兩個同頻率的波相遇，會產生共振增強效應",
            "modern_example": [
                "同事合作完成專案",
                "朋友一起創業",
                "團隊協作",
            ],
            "business_case": "合夥人制度、策略聯盟",
        },
        # 5. SWOT分析
        "swot": {
            "strengths": ["有幫手", "能合作", "人脈廣", "分擔壓力"],
            "weaknesses": ["可能分資源", "意見不合", "各有主見"],
            "opportunities": ["擴大規模", "分工協作", "互補專長"],
            "threats": ["競爭關係", "利益衝突", "分裂風險"],
            "strategy": "明確分工與利益分配，建立共同目標，化競爭為合作",
        },
    },
    "劫財": {
        "calculation": {
            "method": "日干與他干同五行異陰陽",
            "formula": "甲見乙、丙見丁...",
            "source": "《淵海子平》：劫者，奪財之神也",
        },
        "classic": {
            "original": "劫財者，陰見陽、陽見陰，同類異性也。主性格衝動，好勝心強，爭奪資源。",
            "terminology": ["劫財", "敗財", "羊刃", "爭財"],
            "source": "《三命通會》",
        },
        "vernacular": {
            "meaning": "競爭的對手",
            "explanation": "劫財像你的競爭者，跟你搶同樣的東西，激發你的鬥志，但也消耗你的資源。",
            "analogy": "就像同行競爭對手，讓你不敢懈怠，但也可能惡性競爭。",
        },
        "field_theory": {
            "field_name": "同頻干涉場",
            "physics": "同頻率但相位相反的波相遇，會產生干涉削弱效應",
            "modern_example": [
                "同業競爭",
                "兄弟爭產",
                "同事搶功勞",
            ],
            "business_case": "紅海市場競爭、價格戰",
        },
        "swot": {
            "strengths": ["有競爭意識", "激發潛能", "保持警覺"],
            "weaknesses": ["消耗資源", "可能被搶", "樹敵"],
            "opportunities": ["良性競爭促進成長", "差異化突圍"],
            "threats": ["惡性競爭", "兩敗俱傷", "資源流失"],
            "strategy": "保護核心資源，差異化競爭，必要時化敵為友",
        },
    },
    "食神": {
        "calculation": {
            "method": "日干所生同陰陽者",
            "formula": "甲生丙、乙生丁...(陽生陽、陰生陰)",
            "source": "《淵海子平》：食者，生我者之長生也",
        },
        "classic": {
            "original": "食神者，我生之神，陰陽同類。主聰明溫和，才華橫溢，有口福壽元。",
            "terminology": ["食神", "壽星", "泄秀", "才華"],
            "source": "《子平真詮》：食神制殺，英華外泄",
        },
        "vernacular": {
            "meaning": "穩定的才華",
            "explanation": "食神像你的天賦才能，能穩定輸出作品，讓人喜歡，但太享受會變懶。",
            "analogy": "就像有一技之長的人，靠手藝吃飯，過得安穩但可能不思進取。",
        },
        "field_theory": {
            "field_name": "穩定輸出場",
            "physics": "能量穩定釋放，產生持續穩定的輸出",
            "modern_example": [
                "廚師做菜",
                "作家寫作",
                "穩定的被動收入",
            ],
            "business_case": "專業服務、技術變現、內容創作",
        },
        "swot": {
            "strengths": ["有才華", "受喜愛", "有福氣", "穩定輸出"],
            "weaknesses": ["可能懶散", "太享受", "不求進取"],
            "opportunities": ["發揮才華", "建立被動收入", "打造個人品牌"],
            "threats": ["才華被埋沒", "過度消耗", "競爭者模仿"],
            "strategy": "持續精進技能，建立護城河，把才華變成資產",
        },
    },
    "傷官": {
        "calculation": {
            "method": "日干所生異陰陽者",
            "formula": "甲生丁、乙生丙...(陽生陰、陰生陽)",
            "source": "《淵海子平》：傷者，傷害官星也",
        },
        "classic": {
            "original": "傷官者，我生之神，陰陽異類。主聰明絕頂，才高八斗，但傲物凌人。",
            "terminology": ["傷官", "挑戰權威", "叛逆", "創新"],
            "source": "《子平真詮》：傷官見官，為禍百端",
        },
        "vernacular": {
            "meaning": "爆發的才華",
            "explanation": "傷官像你的創意靈感，能驚艷四座，但太尖銳容易得罪人。",
            "analogy": "就像天才藝術家，作品驚豔但性格難搞，需要找對伯樂。",
        },
        "field_theory": {
            "field_name": "衝擊輸出場",
            "physics": "能量爆發式釋放，產生強大衝擊波",
            "modern_example": [
                "創業顛覆行業",
                "藝術家創作驚人作品",
                "打破常規的創新",
            ],
            "business_case": "破壞式創新、產品顛覆、藝術創作",
        },
        "swot": {
            "strengths": ["有創意", "敢表現", "能突破", "驚豔"],
            "weaknesses": ["太尖銳", "得罪人", "不穩定"],
            "opportunities": ["顛覆市場", "建立獨特地位", "吸引關注"],
            "threats": ["被打壓", "太另類被排斥", "曇花一現"],
            "strategy": "找對舞台，用圓滑包裝尖銳，把叛逆變成創新",
        },
    },
    "偏財": {
        "calculation": {
            "method": "日干所剋同陰陽者",
            "formula": "甲剋戊、乙剋己...(陽剋陽、陰剋陰)",
            "source": "《淵海子平》：偏財者，眾人之財也",
        },
        "classic": {
            "original": "偏財者，我剋之神，陰陽同類。主慷慨大方，善於交際，機會財多。",
            "terminology": ["偏財", "橫財", "機會財", "父星"],
            "source": "《三命通會》：偏財主外，為眾人之財",
        },
        "vernacular": {
            "meaning": "機會財",
            "explanation": "偏財像意外的收入，能抓住機會賺外快，但來得快去得也快。",
            "analogy": "就像投資收益、中獎、副業收入，要把握機會但別貪心。",
        },
        "field_theory": {
            "field_name": "機動掌控場",
            "physics": "能量場不固定，需要主動捕捉和掌控",
            "modern_example": [
                "股票投資",
                "副業收入",
                "意外獎金",
            ],
            "business_case": "投資理財、多元收入、機會型創業",
        },
        "swot": {
            "strengths": ["機會多", "人緣好", "靈活", "敢冒險"],
            "weaknesses": ["不穩定", "可能投機", "財來財去"],
            "opportunities": ["多元收入", "投資增值", "把握風口"],
            "threats": ["投資虧損", "過度冒險", "錢財散失"],
            "strategy": "分散投資，設停損點，把意外財轉為穩定資產",
        },
    },
    "正財": {
        "calculation": {
            "method": "日干所剋異陰陽者",
            "formula": "甲剋己、乙剋戊...(陽剋陰、陰剋陽)",
            "source": "《淵海子平》：正財者，己身之財也",
        },
        "classic": {
            "original": "正財者，我剋之神，陰陽異類。主勤儉持家，穩健理財，正當收入。",
            "terminology": ["正財", "妻財", "薪資", "固定收入"],
            "source": "《子平真詮》：正財主內，為己身之財",
        },
        "vernacular": {
            "meaning": "穩定的收入",
            "explanation": "正財像你的薪水，靠努力賺來，穩定可靠但增長有限。",
            "analogy": "就像上班族的月薪，每月固定進帳，踏實但別指望暴富。",
        },
        "field_theory": {
            "field_name": "穩定掌控場",
            "physics": "能量場穩定可控，持續產生穩定輸出",
            "modern_example": [
                "月薪收入",
                "租金收入",
                "穩定的客戶",
            ],
            "business_case": "薪資收入、穩定合約、長期客戶",
        },
        "swot": {
            "strengths": ["穩定可靠", "風險低", "可預測"],
            "weaknesses": ["增長有限", "賺辛苦錢", "太保守"],
            "opportunities": ["穩定累積", "建立信用", "長期複利"],
            "threats": ["通膨侵蝕", "錯失機會", "收入天花板"],
            "strategy": "穩定為基礎，適當冒險，持續提升價值",
        },
    },
    "七殺": {
        "calculation": {
            "method": "剋日干同陰陽者",
            "formula": "庚剋甲、辛剋乙...(陽剋陽、陰剋陰)",
            "source": "《淵海子平》：七殺者，剋我無情也",
        },
        "classic": {
            "original": "七殺者，剋我之神，陰陽同類。主剛毅果斷，魄力過人，但性急易怒。",
            "terminology": ["七殺", "偏官", "將星", "權威"],
            "source": "《三命通會》：七殺如不可馴之虎",
        },
        "vernacular": {
            "meaning": "壓力和挑戰",
            "explanation": "七殺像你的對手和壓力，逼你成長，但太強會壓垮你。",
            "analogy": "就像嚴厲的老闆或強勁的競爭者，讓你不敢懈怠。",
        },
        "field_theory": {
            "field_name": "衝擊約束場",
            "physics": "外部強大能量對自身產生衝擊和約束",
            "modern_example": [
                "高壓工作環境",
                "強勁對手競爭",
                "逆境中成長",
            ],
            "business_case": "危機管理、逆境領導、壓力測試",
        },
        "swot": {
            "strengths": ["有魄力", "敢拼搏", "抗壓強", "能成大事"],
            "weaknesses": ["太衝動", "樹敵多", "壓力大"],
            "opportunities": ["逆境成長", "危機變轉機", "展現實力"],
            "threats": ["被壓垮", "健康受損", "四面樹敵"],
            "strategy": "化壓力為動力，學會借力使力，找到支援系統",
        },
    },
    "正官": {
        "calculation": {
            "method": "剋日干異陰陽者",
            "formula": "辛剋甲、庚剋乙...(陰剋陽、陽剋陰)",
            "source": "《淵海子平》：正官者，剋我有情也",
        },
        "classic": {
            "original": "正官者，剋我之神，陰陽異類。主正直守法，有領導才能，重名譽地位。",
            "terminology": ["正官", "祿神", "官星", "貴人"],
            "source": "《子平真詮》：正官乃貴氣之神",
        },
        "vernacular": {
            "meaning": "合理的管束",
            "explanation": "正官像合理的規則和上司，約束你但是正當的，遵守會受益。",
            "analogy": "就像公司制度和好上司，有規矩但講道理。",
        },
        "field_theory": {
            "field_name": "穩定約束場",
            "physics": "穩定的外部約束力，形成有序的結構",
            "modern_example": [
                "公司制度",
                "法律規範",
                "行業標準",
            ],
            "business_case": "制度建設、合規經營、標準化管理",
        },
        "swot": {
            "strengths": ["有規矩", "受尊重", "正當權力", "有信譽"],
            "weaknesses": ["太拘謹", "怕出錯", "缺乏彈性"],
            "opportunities": ["爭取正式授權", "建立信譽", "獲得認可"],
            "threats": ["被框架限制", "錯失創新機會", "官僚化"],
            "strategy": "遵守規則建立信譽，在框架內尋找空間",
        },
    },
    "偏印": {
        "calculation": {
            "method": "生日干同陰陽者",
            "formula": "壬生甲、癸生乙...(陽生陽、陰生陰)",
            "source": "《淵海子平》：偏印者，梟神也",
        },
        "classic": {
            "original": "偏印者，生我之神，陰陽同類。主聰明孤傲，思想獨特，但好高騖遠。",
            "terminology": ["偏印", "梟神", "偏母", "獨門絕學"],
            "source": "《三命通會》：梟印奪食，不利子息",
        },
        "vernacular": {
            "meaning": "偏門的支援",
            "explanation": "偏印像非主流的知識和支援，獨特但不被大眾理解。",
            "analogy": "就像學冷門專業，有獨門絕活但市場小。",
        },
        "field_theory": {
            "field_name": "獨特支援場",
            "physics": "非主流的能量支援，產生獨特的效果",
            "modern_example": [
                "小眾專業",
                "另類思維",
                "獨門技術",
            ],
            "business_case": "利基市場、獨門技術、差異化競爭",
        },
        "swot": {
            "strengths": ["有獨門絕活", "思維獨特", "差異化"],
            "weaknesses": ["太另類", "難被理解", "市場小"],
            "opportunities": ["利基市場", "獨佔優勢", "高溢價"],
            "threats": ["被邊緣化", "無人欣賞", "孤芳自賞"],
            "strategy": "找到欣賞你的伯樂，適時接地氣，獨特但不孤僻",
        },
    },
    "正印": {
        "calculation": {
            "method": "生日干異陰陽者",
            "formula": "癸生甲、壬生乙...(陰生陽、陽生陰)",
            "source": "《淵海子平》：正印者，生我有情也",
        },
        "classic": {
            "original": "正印者，生我之神，陰陽異類。主仁慈博愛，學識淵博，有貴人相助。",
            "terminology": ["正印", "印綬", "文昌", "學堂"],
            "source": "《子平真詮》：印綬主文，為貴人之星",
        },
        "vernacular": {
            "meaning": "有人教有人罩",
            "explanation": "正印像你的老師和靠山，教你知識，保護你成長。",
            "analogy": "就像好導師和貴人，給你資源和庇護。",
        },
        "field_theory": {
            "field_name": "穩定支援場",
            "physics": "持續穩定的能量輸入，滋養成長",
            "modern_example": [
                "導師指導",
                "父母支持",
                "貴人相助",
            ],
            "business_case": "導師制度、貴人網絡、資源支援",
        },
        "swot": {
            "strengths": ["有學識", "有靠山", "穩定成長", "受庇護"],
            "weaknesses": ["可能太依賴", "不接地氣", "溫室花朵"],
            "opportunities": ["善用資源", "加速成長", "站在巨人肩上"],
            "threats": ["失去靠山", "無法獨立", "依賴症"],
            "strategy": "善用貴人資源，同時培養獨立能力",
        },
    },
}

# ============================================================
# 【二、十二宮五層翻譯】
# ============================================================
GONG_FIVE_LAYER = {
    "命宮": {
        "calculation": {
            "method": "以出生月時定命宮位置",
            "formula": "從寅起正月，順數至生月，逆數時辰",
            "source": "《紫微斗數全書》：命宮定一生榮枯",
        },
        "classic": {
            "original": "命宮乃一身之主，統領全局，主先天稟賦、性格才華、人生格局。",
            "terminology": ["命宮", "本宮", "格局", "命主"],
            "source": "《紫微斗數全書》《斗數秘儀》",
        },
        "vernacular": {
            "meaning": "你這個人本身",
            "explanation": "命宮代表你的核心自我，你的性格、才華、人生基調。",
            "analogy": "就像你的人設和出廠配置，決定你的底色。",
        },
        "field_theory": {
            "field_name": "核心自我場",
            "physics": "個人能量的核心源頭，影響所有其他場域",
            "modern_example": [
                "個人定位",
                "核心競爭力",
                "人格特質",
            ],
            "business_case": "個人品牌、核心價值、自我定位",
        },
        "swot": {
            "strengths": ["了解自己", "發揮本性", "核心優勢"],
            "weaknesses": ["盲點太多", "自我設限", "固執"],
            "opportunities": ["認識自己", "發揮優勢", "做自己"],
            "threats": ["不自知", "被定型", "錯失潛能"],
            "strategy": "深入認識自己，發揮優勢，接納弱點，持續成長",
        },
    },
    "夫妻宮": {
        "calculation": {
            "method": "命宮逆數第三宮",
            "formula": "命宮→兄弟→夫妻",
            "source": "《紫微斗數全書》：夫妻宮主婚姻配偶",
        },
        "classic": {
            "original": "夫妻宮主婚姻姻緣、配偶特質、夫妻關係、合作夥伴。",
            "terminology": ["夫妻宮", "配偶", "姻緣", "合作"],
            "source": "《紫微斗數全書》",
        },
        "vernacular": {
            "meaning": "你的另一半",
            "explanation": "夫妻宮代表你的伴侶特質、婚姻狀況、親密關係。",
            "analogy": "就像你的最佳拍檔，一起面對人生。",
        },
        "field_theory": {
            "field_name": "親密互動場",
            "physics": "兩個能量場的深度融合與互動",
            "modern_example": [
                "婚姻關係",
                "事業合夥",
                "深度合作",
            ],
            "business_case": "合夥經營、策略聯盟、長期合作",
        },
        "swot": {
            "strengths": ["有人陪伴", "互相扶持", "共同成長"],
            "weaknesses": ["磨合期", "期望落差", "失去自我"],
            "opportunities": ["珍惜緣分", "共同進步", "互補優勢"],
            "threats": ["關係破裂", "背叛", "各走各路"],
            "strategy": "珍惜緣分，用心經營，理解差異，共同成長",
        },
    },
    "財帛宮": {
        "calculation": {
            "method": "命宮順數第五宮",
            "formula": "命宮→兄弟→夫妻→子女→財帛",
            "source": "《紫微斗數全書》：財帛宮主財富收入",
        },
        "classic": {
            "original": "財帛宮主財運、收入來源、理財方式、物質生活。",
            "terminology": ["財帛宮", "財運", "進財", "破財"],
            "source": "《紫微斗數全書》",
        },
        "vernacular": {
            "meaning": "你的錢袋子",
            "explanation": "財帛宮代表你的賺錢能力、財運好壞、理財方式。",
            "analogy": "就像你的財務報表，收入多少、怎麼花。",
        },
        "field_theory": {
            "field_name": "資源掌控場",
            "physics": "物質資源的聚集和流動",
            "modern_example": [
                "收入來源",
                "投資理財",
                "財務規劃",
            ],
            "business_case": "營收模式、現金流、資產配置",
        },
        "swot": {
            "strengths": ["財源穩定", "理財能力", "物質充裕"],
            "weaknesses": ["守財不善", "太物質", "理財盲點"],
            "opportunities": ["開源節流", "投資增值", "建立被動收入"],
            "threats": ["財務危機", "破產", "錢財散失"],
            "strategy": "開源節流，穩健理財，建立多元收入",
        },
    },
    # ... 其他宮位類似結構
}


# ============================================================
# 【三、報告生成器】
# ============================================================

@dataclass
class FiveLayerReport:
    """五層報告結構"""
    name: str
    calculation: Dict
    classic: Dict
    vernacular: Dict
    field_theory: Dict
    swot: Dict


def generate_shishen_report(shishen: str) -> FiveLayerReport:
    """生成十神五層報告"""
    data = SHISHEN_FIVE_LAYER.get(shishen, {})
    return FiveLayerReport(
        name=shishen,
        calculation=data.get("calculation", {}),
        classic=data.get("classic", {}),
        vernacular=data.get("vernacular", {}),
        field_theory=data.get("field_theory", {}),
        swot=data.get("swot", {})
    )


def print_five_layer_report(report: FiveLayerReport):
    """打印五層報告"""
    print(f"\n{'═' * 70}")
    print(f"【{report.name}】五層分析報告")
    print(f"{'═' * 70}")
    
    # 1. 術數數值
    calc = report.calculation
    print(f"\n┌─ 1. 術數計算（古籍方式）────────────────────────────────┐")
    print(f"│ 方法: {calc.get('method', 'N/A'):<50} │")
    print(f"│ 公式: {calc.get('formula', 'N/A'):<50} │")
    print(f"│ 出處: {calc.get('source', 'N/A'):<50} │")
    print(f"└───────────────────────────────────────────────────────────┘")
    
    # 2. 原文
    classic = report.classic
    print(f"\n┌─ 2. 原文（古文+專業術語）──────────────────────────────────┐")
    orig = classic.get('original', 'N/A')
    # 分行顯示長文字
    for i in range(0, len(orig), 45):
        print(f"│ {orig[i:i+45]:<55} │")
    print(f"│ 術語: {', '.join(classic.get('terminology', [])):<48} │")
    print(f"│ 出處: {classic.get('source', 'N/A'):<50} │")
    print(f"└───────────────────────────────────────────────────────────┘")
    
    # 3. 白話翻譯
    vern = report.vernacular
    print(f"\n┌─ 3. 白話翻譯 ─────────────────────────────────────────────┐")
    print(f"│ 一句話: {vern.get('meaning', 'N/A'):<48} │")
    exp = vern.get('explanation', 'N/A')
    for i in range(0, len(exp), 45):
        print(f"│ {exp[i:i+45]:<55} │")
    print(f"│ 比喻: {vern.get('analogy', 'N/A'):<50} │")
    print(f"└───────────────────────────────────────────────────────────┘")
    
    # 4. 場論
    field = report.field_theory
    print(f"\n┌─ 4. 場論（現代實例）─────────────────────────────────────────┐")
    print(f"│ 場域: {field.get('field_name', 'N/A'):<50} │")
    print(f"│ 物理: {field.get('physics', 'N/A'):<50} │")
    print(f"│ 實例: {', '.join(field.get('modern_example', [])):<46} │")
    print(f"│ 商業: {field.get('business_case', 'N/A'):<50} │")
    print(f"└───────────────────────────────────────────────────────────┘")
    
    # 5. SWOT
    swot = report.swot
    print(f"\n┌─ 5. SWOT 決策分析 ───────────────────────────────────────────┐")
    print(f"│ S優勢: {', '.join(swot.get('strengths', [])):<48} │")
    print(f"│ W劣勢: {', '.join(swot.get('weaknesses', [])):<48} │")
    print(f"│ O機會: {', '.join(swot.get('opportunities', [])):<48} │")
    print(f"│ T威脅: {', '.join(swot.get('threats', [])):<48} │")
    print(f"├─ 策略建議 ─────────────────────────────────────────────────┤")
    strategy = swot.get('strategy', 'N/A')
    for i in range(0, len(strategy), 50):
        print(f"│ {strategy[i:i+50]:<55} │")
    print(f"└───────────────────────────────────────────────────────────┘")


# ============================================================
# 測試
# ============================================================
if __name__ == "__main__":
    print("=" * 70)
    print("         北斗命數 五層報告系統 測試")
    print("=" * 70)
    
    # 測試十神報告
    for shishen in ["比肩", "七殺", "正印"]:
        report = generate_shishen_report(shishen)
        print_five_layer_report(report)
    
    print("\n" + "=" * 70)
    print("✅ 五層報告系統測試完成！")
    print("=" * 70)
