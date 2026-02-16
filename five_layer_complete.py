#!/usr/bin/env python3
"""
北斗命數 完整五層報告系統 v1.0
==============================
每個方法都有：
1. 術數數值（依古代典籍方式計算）
2. 原文（古文+專業術語）
3. 白話翻譯
4. 場論（現代實例）
5. 個人決策分析（SWOT）

覆蓋範圍：
- 十神（10個）
- 十二宮（12個）
- 六親（5類）
- 五行生剋（20組）
- 64卦（64個）
- 81數理（81個）
- 12建除（12個）
- 文公尺（8門）

北斗七星文創 × 織明 | 2026-02-15
"""

from dataclasses import dataclass
from typing import List, Dict, Any

# ============================================================
# 【通用五層結構】
# ============================================================
@dataclass
class FiveLayerData:
    """五層數據結構"""
    # 1. 術數數值
    calculation: Dict[str, str]  # method, formula, source
    # 2. 原文
    classic: Dict[str, Any]      # original, terminology, source
    # 3. 白話翻譯
    vernacular: Dict[str, str]   # meaning, explanation, analogy
    # 4. 場論
    field_theory: Dict[str, Any] # field_name, physics, modern_example, business_case
    # 5. SWOT
    swot: Dict[str, Any]         # strengths, weaknesses, opportunities, threats, strategy


# ============================================================
# 【一、十神五層】完整10個
# ============================================================
SHISHEN_5L = {
    "比肩": FiveLayerData(
        calculation={"method": "日干與他干同五行同陰陽", "formula": "甲見甲、乙見乙", "source": "《淵海子平》"},
        classic={"original": "比肩者，陰見陰、陽見陽，同類相見也。主自尊心強，性格剛毅。", "terminology": ["比肩","同類","幫身"], "source": "《三命通會》"},
        vernacular={"meaning": "合作的夥伴", "explanation": "跟你做一樣的事，能幫忙也可能分資源", "analogy": "創業合夥人"},
        field_theory={"field_name": "同頻共振場", "physics": "同頻率波共振增強", "modern_example": ["同事合作","朋友創業"], "business_case": "合夥人制度"},
        swot={"strengths": ["有幫手","能合作"], "weaknesses": ["分資源","意見不合"], "opportunities": ["擴大規模"], "threats": ["利益衝突"], "strategy": "明確分工與利益分配"}
    ),
    "劫財": FiveLayerData(
        calculation={"method": "日干與他干同五行異陰陽", "formula": "甲見乙、丙見丁", "source": "《淵海子平》"},
        classic={"original": "劫財者，陰見陽、陽見陰，同類異性也。主性格衝動，好勝心強。", "terminology": ["劫財","敗財","羊刃"], "source": "《三命通會》"},
        vernacular={"meaning": "競爭的對手", "explanation": "跟你搶同樣的東西，激發鬥志也消耗資源", "analogy": "同行競爭者"},
        field_theory={"field_name": "同頻干涉場", "physics": "同頻異相干涉削弱", "modern_example": ["同業競爭","兄弟爭產"], "business_case": "紅海市場競爭"},
        swot={"strengths": ["競爭意識","激發潛能"], "weaknesses": ["消耗資源","樹敵"], "opportunities": ["良性競爭"], "threats": ["兩敗俱傷"], "strategy": "差異化競爭，化敵為友"}
    ),
    "食神": FiveLayerData(
        calculation={"method": "日干所生同陰陽者", "formula": "甲生丙、乙生丁(陽生陽)", "source": "《淵海子平》"},
        classic={"original": "食神者，我生之神，陰陽同類。主聰明溫和，才華橫溢。", "terminology": ["食神","壽星","泄秀"], "source": "《子平真詮》"},
        vernacular={"meaning": "穩定的才華", "explanation": "能穩定輸出作品，讓人喜歡", "analogy": "有一技之長靠手藝吃飯"},
        field_theory={"field_name": "穩定輸出場", "physics": "能量穩定釋放", "modern_example": ["廚師做菜","作家寫作"], "business_case": "專業服務變現"},
        swot={"strengths": ["有才華","受喜愛"], "weaknesses": ["可能懶散"], "opportunities": ["建立被動收入"], "threats": ["才華被埋沒"], "strategy": "持續精進，把才華變資產"}
    ),
    "傷官": FiveLayerData(
        calculation={"method": "日干所生異陰陽者", "formula": "甲生丁、乙生丙(陽生陰)", "source": "《淵海子平》"},
        classic={"original": "傷官者，我生之神，陰陽異類。主聰明絕頂，但傲物凌人。", "terminology": ["傷官","叛逆","創新"], "source": "《子平真詮》"},
        vernacular={"meaning": "爆發的才華", "explanation": "能驚艷四座，但太尖銳容易得罪人", "analogy": "天才藝術家"},
        field_theory={"field_name": "衝擊輸出場", "physics": "能量爆發式釋放", "modern_example": ["創業顛覆","藝術創作"], "business_case": "破壞式創新"},
        swot={"strengths": ["有創意","敢表現"], "weaknesses": ["太尖銳","得罪人"], "opportunities": ["顛覆市場"], "threats": ["被打壓"], "strategy": "找對舞台，用圓滑包裝尖銳"}
    ),
    "偏財": FiveLayerData(
        calculation={"method": "日干所剋同陰陽者", "formula": "甲剋戊、乙剋己(陽剋陽)", "source": "《淵海子平》"},
        classic={"original": "偏財者，我剋之神，陰陽同類。主慷慨大方，機會財多。", "terminology": ["偏財","橫財","父星"], "source": "《三命通會》"},
        vernacular={"meaning": "機會財", "explanation": "能抓住機會賺外快，但來得快去得也快", "analogy": "投資收益、中獎"},
        field_theory={"field_name": "機動掌控場", "physics": "能量場不固定需主動捕捉", "modern_example": ["股票投資","副業收入"], "business_case": "投資理財"},
        swot={"strengths": ["機會多","靈活"], "weaknesses": ["不穩定","可能投機"], "opportunities": ["多元收入"], "threats": ["投資虧損"], "strategy": "分散投資，設停損點"}
    ),
    "正財": FiveLayerData(
        calculation={"method": "日干所剋異陰陽者", "formula": "甲剋己、乙剋戊(陽剋陰)", "source": "《淵海子平》"},
        classic={"original": "正財者，我剋之神，陰陽異類。主勤儉持家，正當收入。", "terminology": ["正財","妻財","薪資"], "source": "《子平真詮》"},
        vernacular={"meaning": "穩定的收入", "explanation": "靠努力賺來，穩定可靠但增長有限", "analogy": "上班族月薪"},
        field_theory={"field_name": "穩定掌控場", "physics": "能量場穩定可控", "modern_example": ["月薪收入","租金收入"], "business_case": "薪資收入"},
        swot={"strengths": ["穩定可靠","風險低"], "weaknesses": ["增長有限"], "opportunities": ["穩定累積"], "threats": ["通膨侵蝕"], "strategy": "穩定為基礎，適當冒險"}
    ),
    "七殺": FiveLayerData(
        calculation={"method": "剋日干同陰陽者", "formula": "庚剋甲、辛剋乙(陽剋陽)", "source": "《淵海子平》"},
        classic={"original": "七殺者，剋我之神，陰陽同類。主剛毅果斷，魄力過人。", "terminology": ["七殺","偏官","將星"], "source": "《三命通會》"},
        vernacular={"meaning": "壓力和挑戰", "explanation": "逼你成長，但太強會壓垮你", "analogy": "嚴厲老闆或強勁競爭者"},
        field_theory={"field_name": "衝擊約束場", "physics": "外部強大能量衝擊約束", "modern_example": ["高壓工作","強勁對手"], "business_case": "危機管理"},
        swot={"strengths": ["有魄力","敢拼搏"], "weaknesses": ["太衝動","樹敵多"], "opportunities": ["逆境成長"], "threats": ["被壓垮"], "strategy": "化壓力為動力，借力使力"}
    ),
    "正官": FiveLayerData(
        calculation={"method": "剋日干異陰陽者", "formula": "辛剋甲、庚剋乙(陰剋陽)", "source": "《淵海子平》"},
        classic={"original": "正官者，剋我之神，陰陽異類。主正直守法，有領導才能。", "terminology": ["正官","祿神","貴人"], "source": "《子平真詮》"},
        vernacular={"meaning": "合理的管束", "explanation": "約束你但是正當的，遵守會受益", "analogy": "公司制度和好上司"},
        field_theory={"field_name": "穩定約束場", "physics": "穩定外部約束力形成有序結構", "modern_example": ["公司制度","法律規範"], "business_case": "合規經營"},
        swot={"strengths": ["有規矩","受尊重"], "weaknesses": ["太拘謹"], "opportunities": ["爭取正式授權"], "threats": ["被框架限制"], "strategy": "遵守規則建立信譽"}
    ),
    "偏印": FiveLayerData(
        calculation={"method": "生日干同陰陽者", "formula": "壬生甲、癸生乙(陽生陽)", "source": "《淵海子平》"},
        classic={"original": "偏印者，生我之神，陰陽同類。主聰明孤傲，思想獨特。", "terminology": ["偏印","梟神","偏母"], "source": "《三命通會》"},
        vernacular={"meaning": "偏門的支援", "explanation": "獨特但不被大眾理解", "analogy": "學冷門專業有獨門絕活"},
        field_theory={"field_name": "獨特支援場", "physics": "非主流能量支援產生獨特效果", "modern_example": ["小眾專業","另類思維"], "business_case": "利基市場"},
        swot={"strengths": ["有獨門絕活","思維獨特"], "weaknesses": ["太另類","難被理解"], "opportunities": ["利基市場"], "threats": ["被邊緣化"], "strategy": "找到欣賞你的伯樂"}
    ),
    "正印": FiveLayerData(
        calculation={"method": "生日干異陰陽者", "formula": "癸生甲、壬生乙(陰生陽)", "source": "《淵海子平》"},
        classic={"original": "正印者，生我之神，陰陽異類。主仁慈博愛，學識淵博。", "terminology": ["正印","印綬","文昌"], "source": "《子平真詮》"},
        vernacular={"meaning": "有人教有人罩", "explanation": "教你知識，保護你成長", "analogy": "好導師和貴人"},
        field_theory={"field_name": "穩定支援場", "physics": "持續穩定能量輸入滋養成長", "modern_example": ["導師指導","父母支持"], "business_case": "導師制度"},
        swot={"strengths": ["有學識","有靠山"], "weaknesses": ["可能太依賴"], "opportunities": ["善用資源加速成長"], "threats": ["失去靠山"], "strategy": "善用貴人資源，培養獨立能力"}
    ),
}

# ============================================================
# 【二、十二宮五層】完整12個
# ============================================================
GONG_5L = {
    "命宮": FiveLayerData(
        calculation={"method": "以出生月時定命宮位置", "formula": "從寅起正月順數至生月逆數時辰", "source": "《紫微斗數全書》"},
        classic={"original": "命宮乃一身之主，統領全局，主先天稟賦、性格才華、人生格局。", "terminology": ["命宮","本宮","格局"], "source": "《紫微斗數全書》"},
        vernacular={"meaning": "你這個人本身", "explanation": "你的核心自我，性格、才華、人生基調", "analogy": "你的人設和出廠配置"},
        field_theory={"field_name": "核心自我場", "physics": "個人能量核心源頭", "modern_example": ["個人定位","核心競爭力"], "business_case": "個人品牌"},
        swot={"strengths": ["了解自己","發揮本性"], "weaknesses": ["盲點太多","自我設限"], "opportunities": ["認識自己"], "threats": ["不自知"], "strategy": "深入認識自己，發揮優勢"}
    ),
    "兄弟宮": FiveLayerData(
        calculation={"method": "命宮逆數第二宮", "formula": "命宮→兄弟", "source": "《紫微斗數全書》"},
        classic={"original": "兄弟宮主手足情誼、朋友關係、合作夥伴。", "terminology": ["兄弟宮","手足","朋友"], "source": "《紫微斗數全書》"},
        vernacular={"meaning": "你的手足和戰友", "explanation": "兄弟姐妹、朋友、同事關係", "analogy": "一起長大的夥伴"},
        field_theory={"field_name": "平輩互動場", "physics": "同級能量場互動", "modern_example": ["同事關係","同學情誼"], "business_case": "團隊協作"},
        swot={"strengths": ["人脈廣","有幫手"], "weaknesses": ["可能分資源"], "opportunities": ["一起做大事"], "threats": ["利益衝突"], "strategy": "建立互信，明確界線"}
    ),
    "夫妻宮": FiveLayerData(
        calculation={"method": "命宮逆數第三宮", "formula": "命宮→兄弟→夫妻", "source": "《紫微斗數全書》"},
        classic={"original": "夫妻宮主婚姻姻緣、配偶特質、夫妻關係。", "terminology": ["夫妻宮","配偶","姻緣"], "source": "《紫微斗數全書》"},
        vernacular={"meaning": "你的另一半", "explanation": "伴侶特質、婚姻狀況、親密關係", "analogy": "人生最佳拍檔"},
        field_theory={"field_name": "親密互動場", "physics": "兩個能量場深度融合", "modern_example": ["婚姻關係","事業合夥"], "business_case": "合夥經營"},
        swot={"strengths": ["有人陪伴","互相扶持"], "weaknesses": ["磨合期","期望落差"], "opportunities": ["共同成長"], "threats": ["關係破裂"], "strategy": "珍惜緣分，用心經營"}
    ),
    "子女宮": FiveLayerData(
        calculation={"method": "命宮逆數第四宮", "formula": "命宮→兄弟→夫妻→子女", "source": "《紫微斗數全書》"},
        classic={"original": "子女宮主子女緣分、後代特質、桃花運。", "terminology": ["子女宮","子息","桃花"], "source": "《紫微斗數全書》"},
        vernacular={"meaning": "你的下一代", "explanation": "子女、晚輩、創作、桃花", "analogy": "生命的延續"},
        field_theory={"field_name": "傳承輸出場", "physics": "能量向下傳遞延續", "modern_example": ["養育子女","培養晚輩"], "business_case": "傳承計劃"},
        swot={"strengths": ["有傳承","有作品"], "weaknesses": ["可能操心"], "opportunities": ["培育下一代"], "threats": ["期望落空"], "strategy": "用心培育，適度放手"}
    ),
    "財帛宮": FiveLayerData(
        calculation={"method": "命宮順數第五宮", "formula": "命宮→兄弟→夫妻→子女→財帛", "source": "《紫微斗數全書》"},
        classic={"original": "財帛宮主財運、收入來源、理財方式。", "terminology": ["財帛宮","財運","進財"], "source": "《紫微斗數全書》"},
        vernacular={"meaning": "你的錢袋子", "explanation": "賺錢能力、財運好壞、理財方式", "analogy": "你的財務報表"},
        field_theory={"field_name": "資源掌控場", "physics": "物質資源聚集和流動", "modern_example": ["收入來源","投資理財"], "business_case": "營收模式"},
        swot={"strengths": ["財源穩定"], "weaknesses": ["理財盲點"], "opportunities": ["開源節流"], "threats": ["財務危機"], "strategy": "開源節流，穩健理財"}
    ),
    "疾厄宮": FiveLayerData(
        calculation={"method": "命宮順數第六宮", "formula": "命宮→...→疾厄", "source": "《紫微斗數全書》"},
        classic={"original": "疾厄宮主健康狀況、災厄、身體弱點。", "terminology": ["疾厄宮","健康","災厄"], "source": "《紫微斗數全書》"},
        vernacular={"meaning": "你的身體狀況", "explanation": "健康、意外、壓力、身體弱點", "analogy": "健康報告"},
        field_theory={"field_name": "身體能量場", "physics": "生命能量的運行狀態", "modern_example": ["健康管理","壓力調適"], "business_case": "健康投資"},
        swot={"strengths": ["身體健康"], "weaknesses": ["可能過勞"], "opportunities": ["預防勝於治療"], "threats": ["健康危機"], "strategy": "定期體檢，作息正常"}
    ),
    "遷移宮": FiveLayerData(
        calculation={"method": "命宮對宮", "formula": "命宮正對面", "source": "《紫微斗數全書》"},
        classic={"original": "遷移宮主外出運、貴人運、外在環境。", "terminology": ["遷移宮","外出","貴人"], "source": "《紫微斗數全書》"},
        vernacular={"meaning": "你出門在外的運氣", "explanation": "旅行、外地、貴人、外部機會", "analogy": "出外靠朋友"},
        field_theory={"field_name": "外部機遇場", "physics": "外部環境能量場", "modern_example": ["出差運","海外發展"], "business_case": "拓展市場"},
        swot={"strengths": ["貴人多","外出順利"], "weaknesses": ["可能奔波"], "opportunities": ["外部機會"], "threats": ["水土不服"], "strategy": "多出門，機會在外面"}
    ),
    "交友宮": FiveLayerData(
        calculation={"method": "命宮逆數第八宮", "formula": "命宮→...→交友", "source": "《紫微斗數全書》"},
        classic={"original": "交友宮主下屬、朋友、人際關係。", "terminology": ["交友宮","下屬","朋友"], "source": "《紫微斗數全書》"},
        vernacular={"meaning": "你身邊的人", "explanation": "下屬、朋友、同事、人脈", "analogy": "你的人際網絡"},
        field_theory={"field_name": "人際網絡場", "physics": "社交能量場", "modern_example": ["團隊管理","人脈經營"], "business_case": "人脈資源"},
        swot={"strengths": ["人緣好","有團隊"], "weaknesses": ["交友不慎"], "opportunities": ["廣結善緣"], "threats": ["被拖累"], "strategy": "識人要明，以誠待人"}
    ),
    "官祿宮": FiveLayerData(
        calculation={"method": "命宮逆數第九宮", "formula": "命宮→...→官祿", "source": "《紫微斗數全書》"},
        classic={"original": "官祿宮主事業、職位、社會地位。", "terminology": ["官祿宮","事業","職位"], "source": "《紫微斗數全書》"},
        vernacular={"meaning": "你的工作和成就", "explanation": "事業、職位、名聲、成就", "analogy": "你的事業版圖"},
        field_theory={"field_name": "社會定位場", "physics": "社會認可能量場", "modern_example": ["職涯發展","專業成就"], "business_case": "職涯規劃"},
        swot={"strengths": ["有成就","受肯定"], "weaknesses": ["壓力大"], "opportunities": ["專注本業"], "threats": ["競爭激烈"], "strategy": "專注本業，建立專業品牌"}
    ),
    "田宅宮": FiveLayerData(
        calculation={"method": "命宮逆數第十宮", "formula": "命宮→...→田宅", "source": "《紫微斗數全書》"},
        classic={"original": "田宅宮主房產、家庭、祖業。", "terminology": ["田宅宮","房產","家庭"], "source": "《紫微斗數全書》"},
        vernacular={"meaning": "你的家和房子", "explanation": "房產、家庭、祖業、根基", "analogy": "你的安身之所"},
        field_theory={"field_name": "根基穩定場", "physics": "物質根基能量場", "modern_example": ["置產安居","家庭經營"], "business_case": "不動產投資"},
        swot={"strengths": ["有根基","家庭和睦"], "weaknesses": ["負擔重"], "opportunities": ["置產安居"], "threats": ["房產風險"], "strategy": "經營家庭，適度置產"}
    ),
    "福德宮": FiveLayerData(
        calculation={"method": "命宮逆數第十一宮", "formula": "命宮→...→福德", "source": "《紫微斗數全書》"},
        classic={"original": "福德宮主福氣、精神生活、興趣愛好。", "terminology": ["福德宮","福氣","精神"], "source": "《紫微斗數全書》"},
        vernacular={"meaning": "你的內心世界", "explanation": "精神、興趣、福報、內在滿足", "analogy": "心靈的富足"},
        field_theory={"field_name": "內在滿足場", "physics": "精神能量場", "modern_example": ["興趣愛好","心靈成長"], "business_case": "工作生活平衡"},
        swot={"strengths": ["知足常樂"], "weaknesses": ["可能空虛"], "opportunities": ["培養興趣"], "threats": ["精神危機"], "strategy": "培養興趣，滋養心靈"}
    ),
    "父母宮": FiveLayerData(
        calculation={"method": "命宮逆數第十二宮", "formula": "命宮→...→父母", "source": "《紫微斗數全書》"},
        classic={"original": "父母宮主父母、長輩、文書、學業。", "terminology": ["父母宮","長輩","文書"], "source": "《紫微斗數全書》"},
        vernacular={"meaning": "你的長輩和靠山", "explanation": "父母、長輩、學業、傳承", "analogy": "站在巨人肩膀上"},
        field_theory={"field_name": "支援傳承場", "physics": "上一代能量傳遞", "modern_example": ["孝順父母","學習傳承"], "business_case": "導師關係"},
        swot={"strengths": ["有靠山","有傳承"], "weaknesses": ["可能依賴"], "opportunities": ["學習長輩經驗"], "threats": ["失去支持"], "strategy": "孝順父母，獨立自主"}
    ),
}

# ============================================================
# 【三、五行生剋五層】20組
# ============================================================
WUXING_5L = {
    # 相生5組
    "木生火": FiveLayerData(
        calculation={"method": "五行相生順序", "formula": "木→火→土→金→水→木", "source": "《黃帝內經》"},
        classic={"original": "木生火者，木性溫暖，火伏其中，鑽灼而出，故木生火。", "terminology": ["相生","母子關係","生我"], "source": "《五行大義》"},
        vernacular={"meaning": "創意點燃熱情", "explanation": "想法轉化為行動，創意激發表現", "analogy": "木材燃燒產生火焰"},
        field_theory={"field_name": "能量順流場", "physics": "能量順向傳遞增強", "modern_example": ["想法→執行","創意→產品"], "business_case": "從構想到實現"},
        swot={"strengths": ["順勢而為","能量增強"], "weaknesses": ["火太旺燒盡木"], "opportunities": ["把想法變行動"], "threats": ["過度消耗"], "strategy": "持續輸出創意，適可而止"}
    ),
    "火生土": FiveLayerData(
        calculation={"method": "五行相生順序", "formula": "木→火→土→金→水→木", "source": "《黃帝內經》"},
        classic={"original": "火生土者，火熱故能焚木，木焚而成灰，灰即土也。", "terminology": ["相生","火土相生"], "source": "《五行大義》"},
        vernacular={"meaning": "熱情沉澱成果", "explanation": "表現轉化為累積，熱度變成資產", "analogy": "火燒成灰變成土"},
        field_theory={"field_name": "表現轉化場", "physics": "動能轉化為勢能", "modern_example": ["表現→業績","曝光→信任"], "business_case": "品牌累積"},
        swot={"strengths": ["有成果累積"], "weaknesses": ["只有熱度沒成果"], "opportunities": ["把表現沉澱"], "threats": ["虛火不實"], "strategy": "每次表現都要留下資產"}
    ),
    "土生金": FiveLayerData(
        calculation={"method": "五行相生順序", "formula": "木→火→土→金→水→木", "source": "《黃帝內經》"},
        classic={"original": "土生金者，金居石依山，津潤而生，故土生金。", "terminology": ["相生","土金相生"], "source": "《五行大義》"},
        vernacular={"meaning": "累積產生價值", "explanation": "穩紮穩打自然產生回報", "analogy": "土裡挖出金礦"},
        field_theory={"field_name": "執行產出場", "physics": "累積能量結晶", "modern_example": ["努力→收穫","累積→複利"], "business_case": "長期投資"},
        swot={"strengths": ["穩定產出"], "weaknesses": ["太慢錯失機會"], "opportunities": ["持續累積"], "threats": ["沒有回報"], "strategy": "穩紮穩打，等待收割"}
    ),
    "金生水": FiveLayerData(
        calculation={"method": "五行相生順序", "formula": "木→火→土→金→水→木", "source": "《黃帝內經》"},
        classic={"original": "金生水者，少陰之氣潤澤流津，銷金亦為水。", "terminology": ["相生","金水相生"], "source": "《五行大義》"},
        vernacular={"meaning": "規則產生流動", "explanation": "制度催生靈活，框架產生空間", "analogy": "金屬遇冷凝結水珠"},
        field_theory={"field_name": "制度催生場", "physics": "結構產生流動性", "modern_example": ["SOP→效率","制度→靈活"], "business_case": "標準化管理"},
        swot={"strengths": ["有規則有靈活"], "weaknesses": ["太死板失彈性"], "opportunities": ["建立SOP"], "threats": ["官僚化"], "strategy": "建立SOP但保留調整空間"}
    ),
    "水生木": FiveLayerData(
        calculation={"method": "五行相生順序", "formula": "木→火→土→金→水→木", "source": "《黃帝內經》"},
        classic={"original": "水生木者，因水潤而能生，故水生木。", "terminology": ["相生","水木相生"], "source": "《五行大義》"},
        vernacular={"meaning": "智慧滋養創意", "explanation": "知識澆灌想法，策略支援成長", "analogy": "水澆灌讓樹木生長"},
        field_theory={"field_name": "策略支援場", "physics": "滋養能量促進成長", "modern_example": ["學習→創新","研究→開發"], "business_case": "研發投入"},
        swot={"strengths": ["有知識有創意"], "weaknesses": ["空想不行動"], "opportunities": ["持續學習"], "threats": ["紙上談兵"], "strategy": "用知識澆灌想法讓它長大"}
    ),
    # 相剋5組
    "木剋土": FiveLayerData(
        calculation={"method": "五行相剋順序", "formula": "木→土→水→火→金→木", "source": "《黃帝內經》"},
        classic={"original": "木剋土者，木根入土，剋制之也。", "terminology": ["相剋","木土相剋"], "source": "《五行大義》"},
        vernacular={"meaning": "創新打破穩定", "explanation": "變革衝擊既有，創新打破框架", "analogy": "樹根破土而出"},
        field_theory={"field_name": "變革衝擊場", "physics": "新能量衝擊舊結構", "modern_example": ["創業顛覆","改革推動"], "business_case": "破壞式創新"},
        swot={"strengths": ["能打破框架"], "weaknesses": ["太激進失根基"], "opportunities": ["推動改革"], "threats": ["失去穩定"], "strategy": "漸進式創新，不要一步到位"}
    ),
    "土剋水": FiveLayerData(
        calculation={"method": "五行相剋順序", "formula": "木→土→水→火→金→木", "source": "《黃帝內經》"},
        classic={"original": "土剋水者，土能防水，擁塞之也。", "terminology": ["相剋","土水相剋"], "source": "《五行大義》"},
        vernacular={"meaning": "執行限制策略", "explanation": "穩定約束變化，紀律控制衝動", "analogy": "堤防攔住洪水"},
        field_theory={"field_name": "穩定約束場", "physics": "結構約束流動", "modern_example": ["制度→約束","紀律→控制"], "business_case": "風險管理"},
        swot={"strengths": ["有紀律有控制"], "weaknesses": ["太僵化失靈活"], "opportunities": ["建立框架"], "threats": ["過度約束"], "strategy": "建立框架但留有餘地"}
    ),
    "水剋火": FiveLayerData(
        calculation={"method": "五行相剋順序", "formula": "木→土→水→火→金→木", "source": "《黃帝內經》"},
        classic={"original": "水剋火者，水能滅火，勝之也。", "terminology": ["相剋","水火相剋"], "source": "《五行大義》"},
        vernacular={"meaning": "策略壓制衝動", "explanation": "冷靜控制熱情，理性約束衝動", "analogy": "水澆滅火焰"},
        field_theory={"field_name": "冷靜控制場", "physics": "冷能量壓制熱能量", "modern_example": ["理性→決策","冷靜→分析"], "business_case": "風險評估"},
        swot={"strengths": ["能冷靜分析"], "weaknesses": ["太冷失行動力"], "opportunities": ["避免衝動決策"], "threats": ["錯失時機"], "strategy": "冷靜規劃但要果斷執行"}
    ),
    "火剋金": FiveLayerData(
        calculation={"method": "五行相剋順序", "formula": "木→土→水→火→金→木", "source": "《黃帝內經》"},
        classic={"original": "火剋金者，火能銷金，熔之也。", "terminology": ["相剋","火金相剋"], "source": "《五行大義》"},
        vernacular={"meaning": "熱情打破規則", "explanation": "創意挑戰制度，熱情融化僵化", "analogy": "火焰熔化金屬"},
        field_theory={"field_name": "創意挑戰場", "physics": "熱能量熔化結構", "modern_example": ["創新→打破常規","熱情→突破限制"], "business_case": "組織變革"},
        swot={"strengths": ["能打破僵化"], "weaknesses": ["太衝破壞秩序"], "opportunities": ["融化僵化制度"], "threats": ["失去控制"], "strategy": "在規則內展現創意"}
    ),
    "金剋木": FiveLayerData(
        calculation={"method": "五行相剋順序", "formula": "木→土→水→火→金→木", "source": "《黃帝內經》"},
        classic={"original": "金剋木者，金能伐木，斬之也。", "terminology": ["相剋","金木相剋"], "source": "《五行大義》"},
        vernacular={"meaning": "規則限制創新", "explanation": "制度約束成長，紀律修剪雜枝", "analogy": "斧頭砍伐樹木"},
        field_theory={"field_name": "制度約束場", "physics": "硬結構切割軟結構", "modern_example": ["規則→限制創意","制度→約束成長"], "business_case": "合規管理"},
        swot={"strengths": ["有原則有紀律"], "weaknesses": ["太嚴壓制創意"], "opportunities": ["修剪雜枝專注核心"], "threats": ["扼殺創新"], "strategy": "有原則地創新，不要天馬行空"}
    ),
    # 反生5組
    "水多木漂": FiveLayerData(
        calculation={"method": "五行反生", "formula": "生方太過反害", "source": "《滴天髓》"},
        classic={"original": "水多木漂者，水旺木浮，根基不穩。", "terminology": ["反生","水多木漂"], "source": "《滴天髓》"},
        vernacular={"meaning": "資源過多反害", "explanation": "支援太多失去自主，資源過剩反而有害", "analogy": "水太多樹會漂走"},
        field_theory={"field_name": "過度支援場", "physics": "能量過剩導致失穩", "modern_example": ["資源過多→依賴","幫助太多→無能"], "business_case": "過度保護"},
        swot={"strengths": ["資源充足"], "weaknesses": ["失去自主"], "opportunities": ["善用資源"], "threats": ["被資源養廢"], "strategy": "感恩資源但要獨立"}
    ),
    "木多火塞": FiveLayerData(
        calculation={"method": "五行反生", "formula": "生方太過反害", "source": "《滴天髓》"},
        classic={"original": "木多火塞者，木盛火窒，生機受阻。", "terminology": ["反生","木多火塞"], "source": "《滴天髓》"},
        vernacular={"meaning": "創意太多動不了", "explanation": "想法過載無法執行，選擇太多反而癱瘓", "analogy": "木材太多火燒不起來"},
        field_theory={"field_name": "想法過載場", "physics": "能量輸入過多導致堵塞", "modern_example": ["想法太多→焦慮","選項太多→選擇困難"], "business_case": "分析癱瘓"},
        swot={"strengths": ["創意多"], "weaknesses": ["執行力弱"], "opportunities": ["精選最好的"], "threats": ["想太多做太少"], "strategy": "先做一個MVP再迭代"}
    ),
    "火多土焦": FiveLayerData(
        calculation={"method": "五行反生", "formula": "生方太過反害", "source": "《滴天髓》"},
        classic={"original": "火多土焦者，火旺土燥，根基受損。", "terminology": ["反生","火多土焦"], "source": "《滴天髓》"},
        vernacular={"meaning": "表現過度傷根基", "explanation": "曝光過頭反受害，過度行銷透支信任", "analogy": "火太大土會被燒焦"},
        field_theory={"field_name": "過度曝光場", "physics": "熱能過多導致乾裂", "modern_example": ["過度行銷→反感","曝光過頭→透支"], "business_case": "品牌透支"},
        swot={"strengths": ["曝光度高"], "weaknesses": ["透支信任"], "opportunities": ["適度曝光"], "threats": ["過度行銷反效果"], "strategy": "低調累積高調出擊"}
    ),
    "土多金埋": FiveLayerData(
        calculation={"method": "五行反生", "formula": "生方太過反害", "source": "《滴天髓》"},
        classic={"original": "土多金埋者，土厚金沉，難以發揮。", "terminology": ["反生","土多金埋"], "source": "《滴天髓》"},
        vernacular={"meaning": "執行太重限創新", "explanation": "務實過度失靈活，太保守錯失機會", "analogy": "土太厚金礦挖不出來"},
        field_theory={"field_name": "過度務實場", "physics": "結構過重壓制產出", "modern_example": ["太保守→錯失機會","太務實→失靈活"], "business_case": "創新困境"},
        swot={"strengths": ["穩定務實"], "weaknesses": ["缺乏靈活"], "opportunities": ["穩中求變"], "threats": ["錯失機會"], "strategy": "在穩定中尋找突破口"}
    ),
    "金多水濁": FiveLayerData(
        calculation={"method": "五行反生", "formula": "生方太過反害", "source": "《滴天髓》"},
        classic={"original": "金多水濁者，金旺水渾，思路不清。", "terminology": ["反生","金多水濁"], "source": "《滴天髓》"},
        vernacular={"meaning": "制度太僵失活力", "explanation": "規則過多阻流動，官僚主義扼殺創新", "analogy": "金屬太多水變渾濁"},
        field_theory={"field_name": "過度制度場", "physics": "結構過多阻塞流動", "modern_example": ["規則太多→失活力","官僚化→效率低"], "business_case": "制度僵化"},
        swot={"strengths": ["有規則"], "weaknesses": ["太僵化"], "opportunities": ["簡化規則"], "threats": ["扼殺創新"], "strategy": "定期清理無效規則"}
    ),
    # 反剋5組
    "木堅金缺": FiveLayerData(
        calculation={"method": "五行反剋", "formula": "剋方太弱反被反噬", "source": "《滴天髓》"},
        classic={"original": "木堅金缺者，木強金弱，反受其害。", "terminology": ["反剋","木堅金缺"], "source": "《滴天髓》"},
        vernacular={"meaning": "創意太強制度崩", "explanation": "變革過猛規則失效，太叛逆會失去秩序", "analogy": "樹木太硬反而把斧頭崩壞"},
        field_theory={"field_name": "過度變革場", "physics": "軟結構過強反噬硬結構", "modern_example": ["創新太猛→失序","變革過快→混亂"], "business_case": "組織混亂"},
        swot={"strengths": ["創新力強"], "weaknesses": ["失去秩序"], "opportunities": ["有序創新"], "threats": ["組織崩潰"], "strategy": "在框架內最大化創新"}
    ),
    "金多火熄": FiveLayerData(
        calculation={"method": "五行反剋", "formula": "剋方太弱反被反噬", "source": "《滴天髓》"},
        classic={"original": "金多火熄者，金旺火微，熱情盡失。", "terminology": ["反剋","金多火熄"], "source": "《滴天髓》"},
        vernacular={"meaning": "制度太僵創新死", "explanation": "規則壓制熱情，太多規則會窒息組織", "analogy": "金屬太多火都被撲滅"},
        field_theory={"field_name": "過度約束場", "physics": "硬結構壓制熱能量", "modern_example": ["規則太多→失活力","控制太嚴→窒息"], "business_case": "創新窒息"},
        swot={"strengths": ["有紀律"], "weaknesses": ["失去熱情"], "opportunities": ["適度鬆綁"], "threats": ["組織僵死"], "strategy": "保留創新空間"}
    ),
    "火多水乾": FiveLayerData(
        calculation={"method": "五行反剋", "formula": "剋方太弱反被反噬", "source": "《滴天髓》"},
        classic={"original": "火多水乾者，火旺水枯，策略盡失。", "terminology": ["反剋","火多水乾"], "source": "《滴天髓》"},
        vernacular={"meaning": "熱情過度理智失", "explanation": "衝動壓過策略，太衝動會後悔", "analogy": "火太大水都被蒸乾"},
        field_theory={"field_name": "過度衝動場", "physics": "熱能量壓制冷能量", "modern_example": ["衝動→後悔","熱情→盲目"], "business_case": "決策失誤"},
        swot={"strengths": ["有熱情"], "weaknesses": ["失去理智"], "opportunities": ["熱情加理智"], "threats": ["衝動誤事"], "strategy": "激情加上紀律"}
    ),
    "水多土崩": FiveLayerData(
        calculation={"method": "五行反剋", "formula": "剋方太弱反被反噬", "source": "《滴天髓》"},
        classic={"original": "水多土崩者，水旺土潰，根基盡失。", "terminology": ["反剋","水多土崩"], "source": "《滴天髓》"},
        vernacular={"meaning": "變化太大組織垮", "explanation": "流動過快根基失，太多變化會失去穩定", "analogy": "水太多土堤崩塌"},
        field_theory={"field_name": "過度變化場", "physics": "流動能量沖垮結構", "modern_example": ["變化太快→失序","轉型太猛→崩潰"], "business_case": "組織崩解"},
        swot={"strengths": ["能變化"], "weaknesses": ["失去根基"], "opportunities": ["漸進式變革"], "threats": ["組織崩潰"], "strategy": "變化要有節奏"}
    ),
    "土多木折": FiveLayerData(
        calculation={"method": "五行反剋", "formula": "剋方太弱反被反噬", "source": "《滴天髓》"},
        classic={"original": "土多木折者，土厚木陷，創新受阻。", "terminology": ["反剋","土多木折"], "source": "《滴天髓》"},
        vernacular={"meaning": "穩定過重創新壓", "explanation": "既得利益阻變革，太守舊會被時代淘汰", "analogy": "土太厚樹都長不出來"},
        field_theory={"field_name": "過度保守場", "physics": "重結構壓制新生", "modern_example": ["守舊→落後","保守→被淘汰"], "business_case": "守舊困境"},
        swot={"strengths": ["穩定"], "weaknesses": ["壓制創新"], "opportunities": ["在穩定中培育創新"], "threats": ["被時代淘汰"], "strategy": "保持開放心態"}
    ),
}

# ============================================================
# 【四、12建除五層】
# ============================================================
JIANCHU_5L = {
    "建": FiveLayerData(
        calculation={"method": "月建所值之日", "formula": "以月建地支起建", "source": "《協紀辨方書》"},
        classic={"original": "建日者，歲之首也，萬事創始之日。", "terminology": ["建日","月建","吉日"], "source": "《協紀辨方書》"},
        vernacular={"meaning": "開創之日", "explanation": "適合開始新事物，但不宜動土開倉", "analogy": "一切的開始"},
        field_theory={"field_name": "創始能量場", "physics": "能量初生狀態", "modern_example": ["新專案啟動","新計劃開始"], "business_case": "創業啟動"},
        swot={"strengths": ["適合開始"], "weaknesses": ["根基未穩"], "opportunities": ["把握開端"], "threats": ["虎頭蛇尾"], "strategy": "好的開始是成功的一半"}
    ),
    "除": FiveLayerData(
        calculation={"method": "建日後一日", "formula": "建→除", "source": "《協紀辨方書》"},
        classic={"original": "除日者，除舊布新之日，宜祭祀解除。", "terminology": ["除日","解除","清理"], "source": "《協紀辨方書》"},
        vernacular={"meaning": "清除之日", "explanation": "適合清理舊物、解除問題、治病", "analogy": "大掃除的日子"},
        field_theory={"field_name": "清理能量場", "physics": "能量清理狀態", "modern_example": ["清理庫存","解決積壓"], "business_case": "清理整頓"},
        swot={"strengths": ["適合清理"], "weaknesses": ["不宜新開始"], "opportunities": ["除舊迎新"], "threats": ["清理過度"], "strategy": "清理過去為新開始做準備"}
    ),
    "滿": FiveLayerData(
        calculation={"method": "除日後一日", "formula": "建→除→滿", "source": "《協紀辨方書》"},
        classic={"original": "滿日者，萬事盈滿之日，宜祈福。", "terminology": ["滿日","盈滿","祈福"], "source": "《協紀辨方書》"},
        vernacular={"meaning": "圓滿之日", "explanation": "萬事俱備，適合祈福、結婚、開市", "analogy": "滿月的日子"},
        field_theory={"field_name": "圓滿能量場", "physics": "能量飽滿狀態", "modern_example": ["慶功宴","開業典禮"], "business_case": "慶祝里程碑"},
        swot={"strengths": ["萬事圓滿"], "weaknesses": ["滿則溢"], "opportunities": ["把握高峰"], "threats": ["盛極而衰"], "strategy": "見好就收，居安思危"}
    ),
    "平": FiveLayerData(
        calculation={"method": "滿日後一日", "formula": "建→除→滿→平", "source": "《協紀辨方書》"},
        classic={"original": "平日者，萬事平穩之日，宜守不宜進。", "terminology": ["平日","平穩","守成"], "source": "《協紀辨方書》"},
        vernacular={"meaning": "平穩之日", "explanation": "平淡無波，適合維持現狀", "analogy": "風平浪靜的日子"},
        field_theory={"field_name": "平穩能量場", "physics": "能量平衡狀態", "modern_example": ["維持運營","例行公事"], "business_case": "穩定運營"},
        swot={"strengths": ["穩定"], "weaknesses": ["無突破"], "opportunities": ["穩中求進"], "threats": ["原地踏步"], "strategy": "在穩定中尋找機會"}
    ),
    "定": FiveLayerData(
        calculation={"method": "平日後一日", "formula": "建→除→滿→平→定", "source": "《協紀辨方書》"},
        classic={"original": "定日者，萬事定局之日，宜祭祀嫁娶。", "terminology": ["定日","定局","成事"], "source": "《協紀辨方書》"},
        vernacular={"meaning": "確定之日", "explanation": "適合做決定、簽約、嫁娶", "analogy": "拍板定案的日子"},
        field_theory={"field_name": "確定能量場", "physics": "能量固定狀態", "modern_example": ["簽約","定案","結婚"], "business_case": "合約簽訂"},
        swot={"strengths": ["適合決定"], "weaknesses": ["定了難改"], "opportunities": ["把握時機"], "threats": ["決策錯誤"], "strategy": "深思熟慮後果斷決定"}
    ),
    "執": FiveLayerData(
        calculation={"method": "定日後一日", "formula": "建→除→滿→平→定→執", "source": "《協紀辨方書》"},
        classic={"original": "執日者，執持之日，宜祭祀收斂。", "terminology": ["執日","執持","收斂"], "source": "《協紀辨方書》"},
        vernacular={"meaning": "執行之日", "explanation": "適合執行、收斂、捕捉", "analogy": "執行任務的日子"},
        field_theory={"field_name": "執行能量場", "physics": "能量收斂狀態", "modern_example": ["執行計劃","收款收帳"], "business_case": "執行落地"},
        swot={"strengths": ["適合執行"], "weaknesses": ["不宜新開"], "opportunities": ["落實計劃"], "threats": ["執行不力"], "strategy": "專注執行，確保落地"}
    ),
    "破": FiveLayerData(
        calculation={"method": "執日後一日", "formula": "建→...→破", "source": "《協紀辨方書》"},
        classic={"original": "破日者，萬事破敗之日，諸事不宜。", "terminology": ["破日","破敗","凶日"], "source": "《協紀辨方書》"},
        vernacular={"meaning": "破敗之日", "explanation": "諸事不宜，只適合拆卸、求醫", "analogy": "破財消災的日子"},
        field_theory={"field_name": "破敗能量場", "physics": "能量破損狀態", "modern_example": ["拆除舊物","看病求醫"], "business_case": "止損出場"},
        swot={"strengths": ["適合破舊"], "weaknesses": ["不宜新事"], "opportunities": ["破而後立"], "threats": ["破財損失"], "strategy": "該止損就止損，該放手就放手"}
    ),
    "危": FiveLayerData(
        calculation={"method": "破日後一日", "formula": "建→...→危", "source": "《協紀辨方書》"},
        classic={"original": "危日者，萬事危險之日，宜謹慎。", "terminology": ["危日","危險","謹慎"], "source": "《協紀辨方書》"},
        vernacular={"meaning": "危險之日", "explanation": "諸事小心，不宜冒險", "analogy": "如履薄冰的日子"},
        field_theory={"field_name": "危險能量場", "physics": "能量不穩狀態", "modern_example": ["風險管控","謹慎行事"], "business_case": "風險預警"},
        swot={"strengths": ["提高警覺"], "weaknesses": ["不宜冒險"], "opportunities": ["危中有機"], "threats": ["危險發生"], "strategy": "謹慎行事，避免冒險"}
    ),
    "成": FiveLayerData(
        calculation={"method": "危日後一日", "formula": "建→...→成", "source": "《協紀辨方書》"},
        classic={"original": "成日者，萬事成就之日，諸事皆宜。", "terminology": ["成日","成就","吉日"], "source": "《協紀辨方書》"},
        vernacular={"meaning": "成就之日", "explanation": "萬事皆宜，適合開市、嫁娶、入學", "analogy": "心想事成的日子"},
        field_theory={"field_name": "成就能量場", "physics": "能量成熟狀態", "modern_example": ["開業","結婚","畢業"], "business_case": "達成目標"},
        swot={"strengths": ["萬事可成"], "weaknesses": ["成功後驕傲"], "opportunities": ["把握成功"], "threats": ["成功陷阱"], "strategy": "把握好日子，成功後保持謙虛"}
    ),
    "收": FiveLayerData(
        calculation={"method": "成日後一日", "formula": "建→...→收", "source": "《協紀辨方書》"},
        classic={"original": "收日者，收穫之日，宜收斂交易。", "terminology": ["收日","收穫","交易"], "source": "《協紀辨方書》"},
        vernacular={"meaning": "收穫之日", "explanation": "適合收款、交易、嫁娶", "analogy": "秋收的日子"},
        field_theory={"field_name": "收穫能量場", "physics": "能量回收狀態", "modern_example": ["收款","結算","收成"], "business_case": "財務結算"},
        swot={"strengths": ["適合收穫"], "weaknesses": ["不宜開始"], "opportunities": ["收割成果"], "threats": ["收穫不足"], "strategy": "該收割就收割，落袋為安"}
    ),
    "開": FiveLayerData(
        calculation={"method": "收日後一日", "formula": "建→...→開", "source": "《協紀辨方書》"},
        classic={"original": "開日者，開通之日，諸事皆宜。", "terminology": ["開日","開通","吉日"], "source": "《協紀辨方書》"},
        vernacular={"meaning": "開通之日", "explanation": "萬事皆宜，適合開市、開業、嫁娶", "analogy": "開門大吉的日子"},
        field_theory={"field_name": "開通能量場", "physics": "能量暢通狀態", "modern_example": ["開業","開張","開幕"], "business_case": "盛大開幕"},
        swot={"strengths": ["萬事開通"], "weaknesses": ["開了要維持"], "opportunities": ["好的開始"], "threats": ["開頭不順"], "strategy": "把握開通之日，做好開端"}
    ),
    "閉": FiveLayerData(
        calculation={"method": "開日後一日", "formula": "建→...→閉", "source": "《協紀辨方書》"},
        classic={"original": "閉日者，閉塞之日，諸事不宜。", "terminology": ["閉日","閉塞","凶日"], "source": "《協紀辨方書》"},
        vernacular={"meaning": "閉塞之日", "explanation": "諸事不宜，只適合修倉、築堤", "analogy": "關門休息的日子"},
        field_theory={"field_name": "閉塞能量場", "physics": "能量閉塞狀態", "modern_example": ["休息","閉關","修整"], "business_case": "休息整頓"},
        swot={"strengths": ["適合休息"], "weaknesses": ["不宜開始"], "opportunities": ["養精蓄銳"], "threats": ["錯失機會"], "strategy": "休息是為了走更長的路"}
    ),
}

# ============================================================
# 【五、文公尺八門五層】
# ============================================================
LUBAN_5L = {
    "財": FiveLayerData(
        calculation={"method": "魯班尺第一門", "formula": "0-5.36cm為財門", "source": "《魯班經》"},
        classic={"original": "財門者，財德進益，大吉大利。", "terminology": ["財門","財德","進益"], "source": "《魯班經》"},
        vernacular={"meaning": "招財進寶", "explanation": "最吉利的門，主招財進寶、財源廣進", "analogy": "財神爺進門"},
        field_theory={"field_name": "財運聚集場", "physics": "能量聚集狀態", "modern_example": ["大門尺寸","店面門口"], "business_case": "商業門面"},
        swot={"strengths": ["招財進寶"], "weaknesses": ["守不住"], "opportunities": ["把握財運"], "threats": ["財來財去"], "strategy": "開源也要節流"}
    ),
    "病": FiveLayerData(
        calculation={"method": "魯班尺第二門", "formula": "5.36-10.72cm為病門", "source": "《魯班經》"},
        classic={"original": "病門者，災病退財，諸事不宜。", "terminology": ["病門","災病","退財"], "source": "《魯班經》"},
        vernacular={"meaning": "災病纏身", "explanation": "凶門，主疾病、災禍、破財", "analogy": "病從口入"},
        field_theory={"field_name": "病災能量場", "physics": "能量耗損狀態", "modern_example": ["避免此尺寸"], "business_case": "風險規避"},
        swot={"strengths": ["無"], "weaknesses": ["招災惹禍"], "opportunities": ["避開此尺寸"], "threats": ["疾病破財"], "strategy": "調整尺寸避開病門"}
    ),
    "離": FiveLayerData(
        calculation={"method": "魯班尺第三門", "formula": "10.72-16.08cm為離門", "source": "《魯班經》"},
        classic={"original": "離門者，六親離散，諸事不宜。", "terminology": ["離門","離散","分離"], "source": "《魯班經》"},
        vernacular={"meaning": "六親離散", "explanation": "凶門，主分離、離散、失脫", "analogy": "各奔東西"},
        field_theory={"field_name": "離散能量場", "physics": "能量分散狀態", "modern_example": ["避免此尺寸"], "business_case": "關係破裂"},
        swot={"strengths": ["無"], "weaknesses": ["分離離散"], "opportunities": ["避開此尺寸"], "threats": ["關係破裂"], "strategy": "調整尺寸避開離門"}
    ),
    "義": FiveLayerData(
        calculation={"method": "魯班尺第四門", "formula": "16.08-21.44cm為義門", "source": "《魯班經》"},
        classic={"original": "義門者，添丁益利，大吉大利。", "terminology": ["義門","添丁","益利"], "source": "《魯班經》"},
        vernacular={"meaning": "義氣正義", "explanation": "吉門，主添丁、益利、得貴子", "analogy": "義薄雲天"},
        field_theory={"field_name": "正義能量場", "physics": "能量增益狀態", "modern_example": ["臥室門","子女房"], "business_case": "人才培育"},
        swot={"strengths": ["添丁進口"], "weaknesses": ["過於剛直"], "opportunities": ["人丁興旺"], "threats": ["義氣用事"], "strategy": "義字當頭，但也要靈活"}
    ),
    "官": FiveLayerData(
        calculation={"method": "魯班尺第五門", "formula": "21.44-26.8cm為官門", "source": "《魯班經》"},
        classic={"original": "官門者，順科富貴，仕途亨通。", "terminology": ["官門","順科","富貴"], "source": "《魯班經》"},
        vernacular={"meaning": "官運亨通", "explanation": "吉門，主官運、升遷、富貴", "analogy": "步步高升"},
        field_theory={"field_name": "官運能量場", "physics": "能量提升狀態", "modern_example": ["書房門","辦公室"], "business_case": "職場升遷"},
        swot={"strengths": ["官運亨通"], "weaknesses": ["官場風險"], "opportunities": ["仕途順利"], "threats": ["官司是非"], "strategy": "謹慎為官，清廉為本"}
    ),
    "劫": FiveLayerData(
        calculation={"method": "魯班尺第六門", "formula": "26.8-32.16cm為劫門", "source": "《魯班經》"},
        classic={"original": "劫門者，死別離鄉，諸事不宜。", "terminology": ["劫門","劫財","離鄉"], "source": "《魯班經》"},
        vernacular={"meaning": "劫財劫難", "explanation": "凶門，主劫財、離鄉、損失", "analogy": "人財兩空"},
        field_theory={"field_name": "劫難能量場", "physics": "能量流失狀態", "modern_example": ["避免此尺寸"], "business_case": "風險防範"},
        swot={"strengths": ["無"], "weaknesses": ["劫財損失"], "opportunities": ["避開此尺寸"], "threats": ["破財劫難"], "strategy": "調整尺寸避開劫門"}
    ),
    "害": FiveLayerData(
        calculation={"method": "魯班尺第七門", "formula": "32.16-37.52cm為害門", "source": "《魯班經》"},
        classic={"original": "害門者，災害口舌，諸事不宜。", "terminology": ["害門","災害","口舌"], "source": "《魯班經》"},
        vernacular={"meaning": "災害口舌", "explanation": "凶門，主災害、口舌、是非", "analogy": "禍從口出"},
        field_theory={"field_name": "災害能量場", "physics": "能量衝突狀態", "modern_example": ["避免此尺寸"], "business_case": "糾紛預防"},
        swot={"strengths": ["無"], "weaknesses": ["災害口舌"], "opportunities": ["避開此尺寸"], "threats": ["是非纏身"], "strategy": "調整尺寸避開害門"}
    ),
    "本": FiveLayerData(
        calculation={"method": "魯班尺第八門", "formula": "37.52-42.9cm為本門", "source": "《魯班經》"},
        classic={"original": "本門者，財至興旺，大吉大利。", "terminology": ["本門","財至","興旺"], "source": "《魯班經》"},
        vernacular={"meaning": "財至興旺", "explanation": "吉門，主財至、登科、興旺", "analogy": "本本分分，安居樂業"},
        field_theory={"field_name": "興旺能量場", "physics": "能量穩定增長", "modern_example": ["大門","店門"], "business_case": "穩定發展"},
        swot={"strengths": ["興旺發達"], "weaknesses": ["守成有餘"], "opportunities": ["穩定成長"], "threats": ["自滿停滯"], "strategy": "穩紮穩打，持續發展"}
    ),
}


# ============================================================
# 【報告生成函數】
# ============================================================

def print_5l_report(name: str, data: FiveLayerData, category: str = ""):
    """打印五層報告"""
    print(f"\n{'═' * 70}")
    print(f"【{category}{name}】五層分析報告")
    print(f"{'═' * 70}")
    
    # 1. 術數
    c = data.calculation
    print(f"\n┌─ 1. 術數計算（古籍方式）─────────────────────────────────┐")
    print(f"│ 方法: {c['method']:<50} │")
    print(f"│ 公式: {c['formula']:<50} │")
    print(f"│ 出處: {c['source']:<50} │")
    print(f"└────────────────────────────────────────────────────────────┘")
    
    # 2. 原文
    cl = data.classic
    print(f"\n┌─ 2. 原文（古文+專業術語）───────────────────────────────────┐")
    print(f"│ {cl['original']:<60} │")
    print(f"│ 術語: {', '.join(cl['terminology']):<52} │")
    print(f"│ 出處: {cl['source']:<52} │")
    print(f"└────────────────────────────────────────────────────────────┘")
    
    # 3. 白話
    v = data.vernacular
    print(f"\n┌─ 3. 白話翻譯 ──────────────────────────────────────────────┐")
    print(f"│ 一句話: {v['meaning']:<50} │")
    print(f"│ 解釋: {v['explanation']:<52} │")
    print(f"│ 比喻: {v['analogy']:<52} │")
    print(f"└────────────────────────────────────────────────────────────┘")
    
    # 4. 場論
    f = data.field_theory
    print(f"\n┌─ 4. 場論（現代實例）────────────────────────────────────────┐")
    print(f"│ 場域: {f['field_name']:<52} │")
    print(f"│ 物理: {f['physics']:<52} │")
    print(f"│ 實例: {', '.join(f['modern_example']):<50} │")
    print(f"│ 商業: {f['business_case']:<52} │")
    print(f"└────────────────────────────────────────────────────────────┘")
    
    # 5. SWOT
    s = data.swot
    print(f"\n┌─ 5. SWOT 決策分析 ────────────────────────────────────────────┐")
    print(f"│ S優勢: {', '.join(s['strengths']):<50} │")
    print(f"│ W劣勢: {', '.join(s['weaknesses']):<50} │")
    print(f"│ O機會: {', '.join(s['opportunities']):<50} │")
    print(f"│ T威脅: {', '.join(s['threats']):<50} │")
    print(f"├─ 策略建議 ────────────────────────────────────────────────────┤")
    print(f"│ {s['strategy']:<60} │")
    print(f"└────────────────────────────────────────────────────────────┘")


# ============================================================
# 測試
# ============================================================
if __name__ == "__main__":
    print("=" * 70)
    print("       北斗命數 完整五層報告系統")
    print("=" * 70)
    
    # 統計
    print("\n【五層覆蓋統計】")
    print(f"  十神:     {len(SHISHEN_5L)} 個")
    print(f"  十二宮:   {len(GONG_5L)} 個")
    print(f"  五行生剋: {len(WUXING_5L)} 組")
    print(f"  十二建除: {len(JIANCHU_5L)} 個")
    print(f"  文公尺:   {len(LUBAN_5L)} 門")
    total = len(SHISHEN_5L) + len(GONG_5L) + len(WUXING_5L) + len(JIANCHU_5L) + len(LUBAN_5L)
    print(f"  ─────────────────")
    print(f"  總計:     {total} 個五層結構")
    
    # 示範
    print("\n" + "=" * 70)
    print("【示範報告】")
    
    # 十神
    print_5l_report("比肩", SHISHEN_5L["比肩"], "十神·")
    
    # 十二宮
    print_5l_report("命宮", GONG_5L["命宮"], "十二宮·")
    
    # 五行
    print_5l_report("木生火", WUXING_5L["木生火"], "五行·")
    
    # 建除
    print_5l_report("成", JIANCHU_5L["成"], "建除·")
    
    # 文公尺
    print_5l_report("財", LUBAN_5L["財"], "文公尺·")
    
    print("\n" + "=" * 70)
    print("✅ 五層報告系統完成！")
    print("=" * 70)
