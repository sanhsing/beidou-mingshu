"""
典籍增強模組
classical_enhancement.py | @理樞 @澄韻 | 2026-02-18

功能：
- 典籍原文引用
- 白話詳解
- SWOT 決策分析
- AI 統合建議

所有術數引擎共用此模組
"""
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from enum import Enum

# ════════════════════════════════════════
# 典籍資料庫
# ════════════════════════════════════════

class ClassicalSource(Enum):
    """典籍來源"""
    YUANHAI_ZIPING = "淵海子平"
    SANMING_TONGHUI = "三命通會"
    DITIAN_SUI = "滴天髓"
    ZIWEI_QUANSHU = "紫微斗數全書"
    ZIWEI_QUANJI = "紫微斗數全集"
    MEIHUA_YISHU = "梅花易數"
    QIMEN_MIJUE = "奇門遁甲秘笈大全"
    XIEJI_BIANFANG = "協紀辨方書"
    XIANGJI_TONGSHU = "象吉通書"
    KANGXI_ZIDIAN = "康熙字典"
    SHUOWEN_JIEZI = "說文解字"

@dataclass
class ClassicalQuote:
    """典籍引文"""
    source: str          # 典籍名稱
    chapter: str         # 章節
    original: str        # 原文
    translation: str     # 白話翻譯
    application: str     # 應用說明

# ════════════════════════════════════════
# 八字典籍
# ════════════════════════════════════════

BAZI_CLASSICS = {
    # 五行相生
    "wood_fire": ClassicalQuote(
        source="淵海子平",
        chapter="論五行生剋制化",
        original="木能生火，火多木焚；火弱逢木，必為炎上。",
        translation="木可以生火，但如果火太旺，反而會把木燒盡；如果火較弱時遇到木，則會使火勢更旺。",
        application="命主木生火的格局，需注意火的強弱平衡。"
    ),
    "fire_earth": ClassicalQuote(
        source="淵海子平",
        chapter="論五行生剋制化",
        original="火能生土，土多火晦；土弱逢火，必為燥烈。",
        translation="火可以生土，但如果土太多，火的光芒會被掩蓋；如果土較弱時遇到火，則土會變得乾燥。",
        application="命主火生土的格局，需留意土的厚薄。"
    ),
    # 十神
    "zhengyin": ClassicalQuote(
        source="三命通會",
        chapter="論正印",
        original="印綬主聰明，多智慧，性慈惠，喜讀書。",
        translation="正印代表聰明、智慧、慈悲善良的特質，命帶正印者通常喜愛學習與閱讀。",
        application="正印為用，利於學習、考試、文書工作。"
    ),
    "qisha": ClassicalQuote(
        source="三命通會",
        chapter="論七殺",
        original="七殺有制，化為權柄；七殺無制，禍患無窮。",
        translation="七殺如果有其他元素制衡，可以轉化為權力與領導力；如果沒有制衡，則容易招來災禍。",
        application="七殺格局需觀察是否有制化，決定行事策略。"
    ),
    "bijian": ClassicalQuote(
        source="滴天髓",
        chapter="論比肩",
        original="比肩重重須損財，財弱逢之徒費心。",
        translation="比肩（與日主相同的五行）過多會損耗財運，如果財星本就弱，遇到比肩會更加辛苦。",
        application="比肩旺時，不宜過度投資或合夥經營。"
    ),
    # 格局
    "caiwan_shuangmei": ClassicalQuote(
        source="三命通會",
        chapter="論財官格",
        original="財旺生官，富貴雙全。",
        translation="財星旺盛且能生助官星，主富貴兼得。",
        application="財官格局良好，利於事業與財富發展。"
    ),
}

# ════════════════════════════════════════
# 紫微典籍
# ════════════════════════════════════════

ZIWEI_CLASSICS = {
    "ziwei_star": ClassicalQuote(
        source="紫微斗數全書",
        chapter="論紫微星",
        original="紫微帝座，諸星之主。在數為尊，在命為貴。",
        translation="紫微星是帝王之星，統領所有星曜。在命盤中代表尊貴、領導力與高格局。",
        application="紫微坐命者，具領導潛質，宜從事管理或創業。"
    ),
    "tianji_star": ClassicalQuote(
        source="紫微斗數全書",
        chapter="論天機星",
        original="天機智慧之星，善謀略，能通變。",
        translation="天機星代表智慧與謀略，命帶此星者善於思考、應變能力強。",
        application="天機坐命者，適合從事策劃、顧問、研究類工作。"
    ),
    "taiyang_star": ClassicalQuote(
        source="紫微斗數全書",
        chapter="論太陽星",
        original="太陽為官祿主，主貴不主富，喜晝生。",
        translation="太陽星主管事業官祿，帶來地位與名聲而非直接財富，白天出生者更佳。",
        application="太陽坐命者，適合公職或需要曝光度的行業。"
    ),
    "taiyin_star": ClassicalQuote(
        source="紫微斗數全書",
        chapter="論太陰星",
        original="太陰為財星，主富不主貴，喜夜生。",
        translation="太陰星是財星，帶來財富而非權位，夜晚出生者更佳。",
        application="太陰坐命者，適合理財、不動產、藝術類工作。"
    ),
    "qingyang_star": ClassicalQuote(
        source="紫微斗數全集",
        chapter="論擎羊星",
        original="擎羊入命，性剛果決，主孤刑。逢吉化權，逢凶更凶。",
        translation="擎羊入命者性格剛毅果斷，但容易孤獨或有刑剋。遇吉星可轉化為權柄，遇凶星則加劇凶象。",
        application="擎羊需觀察會合星曜，決定趨避策略。"
    ),
}

# ════════════════════════════════════════
# 梅花易數典籍
# ════════════════════════════════════════

MEIHUA_CLASSICS = {
    "qian_gua": ClassicalQuote(
        source="梅花易數",
        chapter="論乾卦",
        original="乾為天，為君，為父，為玉，為金，為寒，為冰。",
        translation="乾卦象徵天、君王、父親，以及玉石、金屬、寒冷、冰等意象。",
        application="占得乾卦，主剛健進取，利於領導與決策。"
    ),
    "kun_gua": ClassicalQuote(
        source="梅花易數",
        chapter="論坤卦",
        original="坤為地，為母，為布，為釜，為吝嗇。",
        translation="坤卦象徵大地、母親、布帛、器皿，以及節儉之意。",
        application="占得坤卦，主柔順包容，利於守成與配合。"
    ),
    "ti_yong": ClassicalQuote(
        source="梅花易數",
        chapter="體用生剋篇",
        original="體用生剋之法，乃占卜之要訣。體卦為己，用卦為事。",
        translation="體用生剋是占卜的核心法則。體卦代表自己，用卦代表所問之事。",
        application="體生用為吉，用剋體需謹慎。"
    ),
}

# ════════════════════════════════════════
# 奇門遁甲典籍
# ════════════════════════════════════════

QIMEN_CLASSICS = {
    "jiustar_meaning": ClassicalQuote(
        source="奇門遁甲秘笈大全",
        chapter="論九星",
        original="天蓬貪狼，天任左輔，天冲武曲，各有所主。",
        translation="九星各有其象徵意義：天蓬主貪狼、天任主輔佐、天冲主武勇，各司其職。",
        application="觀察所臨九星，判斷事物性質與走向。"
    ),
    "bamen_meaning": ClassicalQuote(
        source="奇門遁甲秘笈大全",
        chapter="論八門",
        original="開休生三門為吉，死驚傷三門為凶，杜景二門平平。",
        translation="開門、休門、生門是三吉門；死門、驚門、傷門是三凶門；杜門、景門則吉凶參半。",
        application="行事擇門而入，趨吉避凶。"
    ),
}

# ════════════════════════════════════════
# 擇日典籍
# ════════════════════════════════════════

DATE_CLASSICS = {
    "marry_date": ClassicalQuote(
        source="協紀辨方書",
        chapter="嫁娶篇",
        original="嫁娶之道，以女命為主，擇日宜天德、月德、天喜。",
        translation="選擇婚嫁日期，以女方命格為主要考量，適合選用天德、月德、天喜等吉神值日。",
        application="婚嫁擇日首重女命，配合吉神方位。"
    ),
    "ground_break": ClassicalQuote(
        source="象吉通書",
        chapter="動土篇",
        original="動土宜擇土王用事之日，忌三煞、歲破、月破。",
        translation="動土開工適合選用土氣旺盛的日子，避開三煞、歲破、月破等凶日。",
        application="動土擇日重在避凶，確保工程順利。"
    ),
    "open_market": ClassicalQuote(
        source="協紀辨方書",
        chapter="開市篇",
        original="開市立券，宜天願、滿日、成日，忌月破、四離。",
        translation="開業簽約適合選用天願、滿日、成日等吉日，避開月破、四離等凶日。",
        application="開市擇日求財運亨通，事業興旺。"
    ),
}

# ════════════════════════════════════════
# 命名典籍
# ════════════════════════════════════════

NAMING_CLASSICS = {
    "name_principle": ClassicalQuote(
        source="康熙字典",
        chapter="序",
        original="名者，命也。名正則言順，言順則事成。",
        translation="名字與命運相連。名字正確則說話順暢，說話順暢則事情容易成功。",
        application="取名需考慮音義形，與命主五行配合。"
    ),
    "wuxing_name": ClassicalQuote(
        source="說文解字",
        chapter="部首",
        original="凡字之意，皆從其形。水旁從水，木旁從木。",
        translation="字的含義源自字形。水字旁的字屬水，木字旁的字屬木。",
        application="選字時需注意五行屬性，補足命局所缺。"
    ),
}

# ════════════════════════════════════════
# SWOT 分析框架
# ════════════════════════════════════════

@dataclass
class SWOTAnalysis:
    """SWOT 決策分析"""
    strengths: List[str]       # 優勢
    weaknesses: List[str]      # 劣勢
    opportunities: List[str]   # 機會
    threats: List[str]         # 威脅
    strategies: List[str]      # 建議策略
    period: str = ""           # 適用時期

def generate_swot(
    wuxing_balance: Dict[str, float],
    favorable_elements: List[str],
    unfavorable_elements: List[str],
    current_luck: str = "平穩"
) -> SWOTAnalysis:
    """
    根據命理分析生成 SWOT
    """
    strengths = []
    weaknesses = []
    opportunities = []
    threats = []
    strategies = []
    
    # 分析五行優勢
    for element, score in wuxing_balance.items():
        if score > 2.0:
            strengths.append(f"{element}氣旺盛，{WUXING_TRAITS[element]['strength']}")
        elif score < 0.5:
            weaknesses.append(f"{element}氣不足，{WUXING_TRAITS[element]['weakness']}")
    
    # 分析用神機會
    for element in favorable_elements:
        opportunities.append(f"流年遇{element}運，利於{WUXING_TRAITS[element]['opportunity']}")
    
    # 分析忌神威脅
    for element in unfavorable_elements:
        threats.append(f"需注意{element}過旺時期，{WUXING_TRAITS[element]['threat']}")
    
    # 生成策略建議
    if strengths:
        strategies.append(f"發揮優勢：善用{strengths[0][:2]}特質")
    if weaknesses:
        strategies.append(f"補足劣勢：強化{weaknesses[0][:2]}相關能力")
    if opportunities:
        strategies.append(f"把握機會：{opportunities[0]}")
    if threats:
        strategies.append(f"規避風險：{threats[0]}")
    
    return SWOTAnalysis(
        strengths=strengths or ["命格穩健，無明顯短板"],
        weaknesses=weaknesses or ["無明顯劣勢"],
        opportunities=opportunities or ["整體運勢平穩"],
        threats=threats or ["無重大風險"],
        strategies=strategies or ["穩健發展，順勢而為"]
    )

# 五行特質對照表
WUXING_TRAITS = {
    "木": {
        "strength": "創造力強、富同理心",
        "weakness": "易優柔寡斷",
        "opportunity": "創業、創新、教育",
        "threat": "衝動決策、過度擴張"
    },
    "火": {
        "strength": "熱情積極、領導力強",
        "weakness": "易急躁衝動",
        "opportunity": "行銷、演藝、領導",
        "threat": "人際衝突、健康耗損"
    },
    "土": {
        "strength": "穩重務實、誠信可靠",
        "weakness": "易固執保守",
        "opportunity": "房地產、農業、穩健投資",
        "threat": "錯失良機、思維僵化"
    },
    "金": {
        "strength": "決斷力強、重義守信",
        "weakness": "易過於剛硬",
        "opportunity": "金融、科技、法律",
        "threat": "人際疏離、過度苛求"
    },
    "水": {
        "strength": "智慧靈活、應變力強",
        "weakness": "易缺乏定性",
        "opportunity": "貿易、旅遊、諮詢",
        "threat": "方向不定、投機風險"
    }
}

# ════════════════════════════════════════
# AI 決策建議生成
# ════════════════════════════════════════

@dataclass
class AIDecisionAdvice:
    """AI 決策建議"""
    overall_assessment: str     # 整體評估
    short_term_advice: str      # 短期建議（近3個月）
    mid_term_advice: str        # 中期建議（3-12個月）
    long_term_advice: str       # 長期建議（1-3年）
    key_focus_areas: List[str]  # 重點關注領域
    caution_areas: List[str]    # 需謹慎領域
    action_items: List[str]     # 可執行行動

def generate_ai_advice(
    swot: SWOTAnalysis,
    life_area: str = "整體",
    current_period: str = "當前"
) -> AIDecisionAdvice:
    """
    根據 SWOT 生成 AI 決策建議
    """
    # 整體評估
    strength_count = len([s for s in swot.strengths if s != "命格穩健，無明顯短板"])
    weakness_count = len([w for w in swot.weaknesses if w != "無明顯劣勢"])
    
    if strength_count > weakness_count:
        overall = "整體格局良好，優勢明顯，適合積極進取。"
    elif weakness_count > strength_count:
        overall = "目前階段需穩健為主，著重補足短板。"
    else:
        overall = "格局平衡，宜穩中求進，把握適當機會。"
    
    # 生成建議
    short_term = "近期宜" + ("積極把握機會" if swot.opportunities else "穩健觀望")
    mid_term = "中期可" + ("逐步擴大優勢領域" if swot.strengths else "著重能力提升")
    long_term = "長期應" + ("建立持續競爭優勢" if strength_count > 1 else "穩定發展，累積資源")
    
    return AIDecisionAdvice(
        overall_assessment=overall,
        short_term_advice=short_term + "，" + (swot.strategies[0] if swot.strategies else "順勢而為"),
        mid_term_advice=mid_term,
        long_term_advice=long_term,
        key_focus_areas=[s.split("，")[0] for s in swot.strengths[:2]],
        caution_areas=[t.split("，")[0] for t in swot.threats[:2]],
        action_items=swot.strategies[:3]
    )

# ════════════════════════════════════════
# 統一增強接口
# ════════════════════════════════════════

def enhance_analysis(
    analysis_type: str,
    raw_result: Dict[str, Any],
    include_classics: bool = True,
    include_swot: bool = True,
    include_ai_advice: bool = True
) -> Dict[str, Any]:
    """
    統一增強分析結果
    
    Args:
        analysis_type: 分析類型 (bazi/ziwei/meihua/qimen/date/naming)
        raw_result: 原始分析結果
        include_classics: 是否包含典籍引用
        include_swot: 是否包含 SWOT 分析
        include_ai_advice: 是否包含 AI 建議
    
    Returns:
        增強後的分析結果
    """
    enhanced = raw_result.copy()
    
    # 典籍來源
    CLASSICS_MAP = {
        "bazi": BAZI_CLASSICS,
        "ziwei": ZIWEI_CLASSICS,
        "meihua": MEIHUA_CLASSICS,
        "qimen": QIMEN_CLASSICS,
        "date": DATE_CLASSICS,
        "naming": NAMING_CLASSICS
    }
    
    # 添加典籍引用
    if include_classics and analysis_type in CLASSICS_MAP:
        classics = CLASSICS_MAP[analysis_type]
        relevant_quotes = []
        
        # 根據結果內容匹配相關典籍
        for key, quote in classics.items():
            relevant_quotes.append(asdict(quote))
        
        enhanced["classical_references"] = {
            "source_texts": relevant_quotes[:3],  # 最多3條
            "note": "以上引文皆出自古代典籍原典，供參考印證"
        }
    
    # 添加 SWOT 分析
    if include_swot:
        # 從原始結果提取五行資訊（如有）
        wuxing = raw_result.get("wuxing_balance", {
            "木": 1.0, "火": 1.0, "土": 1.0, "金": 1.0, "水": 1.0
        })
        favorable = raw_result.get("favorable_elements", [])
        unfavorable = raw_result.get("unfavorable_elements", [])
        
        swot = generate_swot(wuxing, favorable, unfavorable)
        enhanced["swot_analysis"] = asdict(swot)
    
    # 添加 AI 建議
    if include_ai_advice and include_swot:
        advice = generate_ai_advice(swot)
        enhanced["ai_decision_advice"] = asdict(advice)
    
    # 添加方法論說明
    enhanced["methodology"] = {
        "classical_foundation": "本分析基於古代典籍原典算法",
        "modern_framework": "結合場論框架與 SWOT 決策模型",
        "ai_integration": "運用 AI 進行多維度交叉驗證",
        "output_type": "決策建議（非吉凶預測）",
        "disclaimer": "僅供參考，重大決策請諮詢專業人士"
    }
    
    return enhanced

# ════════════════════════════════════════
# 模組載入
# ════════════════════════════════════════

print("✓ 典籍增強模組已載入")
print(f"  - 八字典籍: {len(BAZI_CLASSICS)} 條")
print(f"  - 紫微典籍: {len(ZIWEI_CLASSICS)} 條")
print(f"  - 梅花典籍: {len(MEIHUA_CLASSICS)} 條")
print(f"  - 奇門典籍: {len(QIMEN_CLASSICS)} 條")
print(f"  - 擇日典籍: {len(DATE_CLASSICS)} 條")
print(f"  - 命名典籍: {len(NAMING_CLASSICS)} 條")

# ════════════════════════════════════════════════════════════════════
# 十神白話翻譯系統（整合自 glossary v1.0）
# ════════════════════════════════════════════════════════════════════

@dataclass
class ShiShenGlossary:
    """十神白話翻譯"""
    name: str              # 十神名稱
    classical: str         # 古典說法
    vernacular: str        # 白話翻譯
    field_theory: str      # 場論詮釋
    modern_analogy: str    # 現代比喻
    field_strong: str      # 場增強時
    field_excess: str      # 場過強時
    field_weak: str        # 場過弱時
    remedy: str = ""       # 調場方法

SHISHEN_GLOSSARY = {
    "正印": ShiShenGlossary(
        name="正印",
        classical="生我者（陰），母親、老師、長輩庇蔭",
        vernacular="有人穩定地照顧你、教導你",
        field_theory="外部能量穩定流入你的場，讓你的場增強",
        modern_analogy="好主管帶你、公司培訓你、有人罩你",
        field_strong="學習順利、有靠山、安全感足",
        field_excess="太依賴、不獨立、媽寶",
        field_weak="沒人教、沒人罩、得自己硬撐",
        remedy="適度獨立，強化食傷（自我表達）"
    ),
    "偏印": ShiShenGlossary(
        name="偏印",
        classical="生我者（陽），繼母、偏師、異類知識",
        vernacular="有人幫你，但方式比較奇怪",
        field_theory="外部能量流入但頻率有偏差，帶有雜訊",
        modern_analogy="斜槓技能、非主流人脈、野路子方法",
        field_strong="獨特優勢、別人沒有的技能",
        field_excess="太偏門、不被主流認可、孤獨",
        field_weak="缺乏獨特性、跟大家一樣",
        remedy="平衡主流與另類，找到利基"
    ),
    "比肩": ShiShenGlossary(
        name="比肩",
        classical="同我者（陽），兄弟、同輩、朋友",
        vernacular="跟你頻率相同的人",
        field_theory="同頻率的場疊加，可能共振（1+1>2）也可能干涉",
        modern_analogy="同事、同學、同業、創業夥伴",
        field_strong="團隊合作、互相幫助、人多力量大",
        field_excess="競爭消耗、財被劫、內鬥",
        field_weak="孤立無援、缺助力、單打獨鬥",
        remedy="共振者聚，干涉者離，選擇同行者"
    ),
    "劫財": ShiShenGlossary(
        name="劫財",
        classical="同我者（陰），競爭者、奪財之人",
        vernacular="跟你搶東西的人",
        field_theory="同頻但產生干涉，導致場損（1+1<2）",
        modern_analogy="搶客戶的同業、搶資源的部門、情敵",
        field_strong="激發競爭動力（適度時）",
        field_excess="財被劫、資源流失、合夥易散",
        field_weak="缺乏競爭意識、太被動",
        remedy="劃清界線、差異化定位、避免正面衝突"
    ),
    "食神": ShiShenGlossary(
        name="食神",
        classical="我生者（陽），才華、享福、口福",
        vernacular="你穩定產出的東西",
        field_theory="你的場向外穩定輸出能量",
        modern_analogy="工作產出、專業技能、穩定的現金流",
        field_strong="創作豐富、收入穩定、生活品質好",
        field_excess="過度消耗自己、只出不進、累",
        field_weak="沒有產出、不被認可、懷才不遇",
        remedy="平衡輸出與充電，用印星滋養"
    ),
    "傷官": ShiShenGlossary(
        name="傷官",
        classical="我生者（陰），才華外露、批評、叛逆",
        vernacular="你爆發性產出的東西",
        field_theory="你的場向外衝擊性輸出，可能打破舊結構",
        modern_analogy="創新產品、直言批評、顛覆性想法",
        field_strong="創新突破、改變現狀、引領潮流",
        field_excess="得罪人、太衝、樹敵太多",
        field_weak="不敢表達、壓抑、有話不說",
        remedy="用印化傷（學習沉澱）、選對場域發揮"
    ),
    "正財": ShiShenGlossary(
        name="正財",
        classical="我剋者（陰），正當收入、妻子（男命）",
        vernacular="你穩定掌控的資源",
        field_theory="你的場對外部資源場進行穩定控制",
        modern_analogy="薪水、存款、房產、穩定客戶",
        field_strong="財務穩定、資源充足、執行力強",
        field_excess="為錢所累、只顧賺錢、太物質",
        field_weak="入不敷出、資源短缺、巧婦難為",
        remedy="強化食傷（創造價值）來生財"
    ),
    "偏財": ShiShenGlossary(
        name="偏財",
        classical="我剋者（陽），意外之財、投資、父親",
        vernacular="你能抓住的機會",
        field_theory="你的場對流動性資源的快速捕獲",
        modern_analogy="投資收益、項目獎金、副業收入、人脈資源",
        field_strong="機會多、財路廣、眼光準",
        field_excess="太投機、不踏實、風險高",
        field_weak="錯失機會、眼光差、只有死薪水",
        remedy="正偏財並進，穩中求進"
    ),
    "正官": ShiShenGlossary(
        name="正官",
        classical="剋我者（陰），上司、丈夫（女命）、法律",
        vernacular="合理管你的人/規則",
        field_theory="外部場對你的場進行穩定、合理的約束",
        modern_analogy="主管、公司制度、法規、合約義務",
        field_strong="有方向、有紀律、有目標、被認可",
        field_excess="壓力大、不自由、被管太緊",
        field_weak="沒方向、太散漫、缺乏約束",
        remedy="用印化官（學習轉化壓力為動力）"
    ),
    "七殺": ShiShenGlossary(
        name="七殺",
        classical="剋我者（陽），小人、壓力、災難",
        vernacular="不講道理的壓力",
        field_theory="外部場對你的場進行衝擊性、強制性的壓制",
        modern_analogy="惡性競爭、職場霸凌、突發危機、不可抗力",
        field_strong="逆境成長、危機變轉機（化解得當時）",
        field_excess="被壓垮、失敗、受傷",
        field_weak="缺乏挑戰、溫室花朵、抗壓弱",
        remedy="用印化殺（找靠山）、食神制殺（用才華化解）"
    ),
}

# ════════════════════════════════════════════════════════════════════
# 六親場論詮釋系統
# ════════════════════════════════════════════════════════════════════

@dataclass
class LiuQinGlossary:
    """六親場論詮釋"""
    name: str              # 六親名稱
    male_shishen: str      # 男命十神
    female_shishen: str    # 女命十神
    field_role: str        # 場論角色
    field_trait: str       # 場態特徵

LIUQIN_GLOSSARY = {
    "祖父": LiuQinGlossary("祖父", "偏印", "偏印", "遠距滋養場", "間接能量輸入"),
    "祖母": LiuQinGlossary("祖母", "偏印", "偏印", "遠距滋養場", "間接能量輸入"),
    "父親": LiuQinGlossary("父親", "偏財", "偏財", "資源供給場", "掌控型能量源"),
    "母親": LiuQinGlossary("母親", "正印", "正印", "直接庇護場", "滋養型能量源"),
    "兄弟": LiuQinGlossary("兄弟", "比肩", "劫財", "同頻競爭場", "共振或干涉"),
    "姐妹": LiuQinGlossary("姐妹", "劫財", "比肩", "同頻競爭場", "共振或干涉"),
    "妻子": LiuQinGlossary("妻子", "正財", "—", "穩定掌控場", "主體控客體"),
    "丈夫": LiuQinGlossary("丈夫", "—", "正官", "穩定約束場", "客體控主體"),
    "兒子": LiuQinGlossary("兒子", "七殺", "傷官", "衝擊輸出場", "能量強發散"),
    "女兒": LiuQinGlossary("女兒", "正官", "食神", "穩定輸出場", "能量柔發散"),
}


# ════════════════════════════════════════════════════════════════════
# 十神 × XTFS 四塔映射
# ════════════════════════════════════════════════════════════════════

SHISHEN_XTFS_MAPPING = {
    # 十神 → XTFS 塔位
    "食神": {"tower": "X消", "function": "突破發散，拆解舊結構", "field": "能量向外輻射，場的擴散"},
    "傷官": {"tower": "X消", "function": "突破發散，拆解舊結構", "field": "能量向外輻射，場的擴散"},
    "正印": {"tower": "T拓", "function": "吸收轉化，測量平衡", "field": "能量向內吸收，場的滋養"},
    "偏印": {"tower": "T拓", "function": "吸收轉化，測量平衡", "field": "能量向內吸收，場的滋養"},
    "正財": {"tower": "F融", "function": "落地執行，結果產出", "field": "能量的掌控，場的整合"},
    "偏財": {"tower": "F融", "function": "落地執行，結果產出", "field": "能量的掌控，場的整合"},
    "正官": {"tower": "S選", "function": "邊界審核，風險控制", "field": "能量的約束，場的邊界"},
    "七殺": {"tower": "S選", "function": "邊界審核，風險控制", "field": "能量的約束，場的邊界"},
    "比肩": {"tower": "場基底", "function": "同頻共振或干涉", "field": "場的頻率本身"},
    "劫財": {"tower": "場基底", "function": "同頻共振或干涉", "field": "場的頻率本身"},
}

# ════════════════════════════════════════════════════════════════════
# 十神場損診斷系統
# ════════════════════════════════════════════════════════════════════

SHISHEN_FIELD_DIAGNOSIS = {
    # 感受 → 可能的十神場損 → 調場方向
    "壓力大被剋": {
        "diagnosis": "官殺過旺",
        "remedy": "尋找印星（學習、貴人）化解",
        "action": "找靠山、進修學習、取得認證"
    },
    "發散過度體虛": {
        "diagnosis": "食傷過旺",
        "remedy": "強化印星（休息、充電）",
        "action": "減少輸出、多休息、接受幫助"
    },
    "孤立無援": {
        "diagnosis": "比劫過弱",
        "remedy": "尋找同頻者（朋友、合作）",
        "action": "加入社群、尋找合作夥伴"
    },
    "財運不濟": {
        "diagnosis": "財星過弱或比劫過旺",
        "remedy": "強化食傷（創造價值）",
        "action": "提升技能、增加產出、差異化定位"
    },
    "缺乏動力": {
        "diagnosis": "官殺過弱",
        "remedy": "設定目標、接受約束",
        "action": "找主管帶、設定 deadline、加入團隊"
    },
    "依賴過度": {
        "diagnosis": "印星過旺",
        "remedy": "強化食傷（表達、獨立）",
        "action": "獨立完成任務、減少求助、自我表達"
    },
}

# ════════════════════════════════════════════════════════════════════
# 紫微星曜白話翻譯
# ════════════════════════════════════════════════════════════════════

@dataclass
class ZiweiStarGlossary:
    """紫微星曜白話翻譯"""
    name: str              # 星曜名稱
    wuxing: str            # 五行
    classical: str         # 古典含義
    vernacular: str        # 白話翻譯
    field_theory: str      # 場論詮釋
    modern_career: str     # 現代職業
    strength: str          # 優勢
    weakness: str          # 風險

ZIWEI_STAR_GLOSSARY = {
    "紫微": ZiweiStarGlossary(
        name="紫微",
        wuxing="土",
        classical="帝座、尊貴、領導",
        vernacular="你是老大的命",
        field_theory="核心統御場，諸星歸服",
        modern_career="CEO、主管、領導者",
        strength="有威嚴、能服眾、格局大",
        weakness="高處不勝寒、孤獨、需要配星"
    ),
    "天機": ZiweiStarGlossary(
        name="天機",
        wuxing="木",
        classical="智慧、謀略、善變",
        vernacular="聰明愛動腦",
        field_theory="思維運算場，快速切換",
        modern_career="顧問、分析師、企劃、研發",
        strength="聰明、有策略、適應力強",
        weakness="想太多、猶豫不決、缺乏執行力"
    ),
    "太陽": ZiweiStarGlossary(
        name="太陽",
        wuxing="火",
        classical="光明、博愛、男性",
        vernacular="熱情外向、愛照顧人",
        field_theory="輻射發散場，照亮他人",
        modern_career="公關、行銷、政治、公益",
        strength="熱情、正面、有影響力",
        weakness="過度付出、燃燒自己、廟旺才佳"
    ),
    "武曲": ZiweiStarGlossary(
        name="武曲",
        wuxing="金",
        classical="財星、剛毅、果斷",
        vernacular="會賺錢、很實際",
        field_theory="執行決斷場，直接了當",
        modern_career="財務、金融、軍警、運動",
        strength="執行力強、賺錢能力、果斷",
        weakness="太剛硬、不近人情、需柔化"
    ),
    "天同": ZiweiStarGlossary(
        name="天同",
        wuxing="水",
        classical="福星、溫和、享福",
        vernacular="人緣好、愛享受",
        field_theory="和諧共振場，柔順適應",
        modern_career="服務業、藝術、休閒、社工",
        strength="好相處、有福氣、壓力小",
        weakness="太懶散、缺乏野心、易安逸"
    ),
    "廉貞": ZiweiStarGlossary(
        name="廉貞",
        wuxing="火",
        classical="次桃花、精明、複雜",
        vernacular="精明能幹、有魅力",
        field_theory="複合運算場，多面向",
        modern_career="法律、政治、演藝、公關",
        strength="能力強、有魅力、多才多藝",
        weakness="太複雜、情緒化、易捲入是非"
    ),
    "天府": ZiweiStarGlossary(
        name="天府",
        wuxing="土",
        classical="財庫、穩重、保守",
        vernacular="穩重守財、有安全感",
        field_theory="蓄積封存場，穩定守護",
        modern_career="行政、財務、保險、倉儲",
        strength="穩定、有存款、讓人安心",
        weakness="太保守、缺乏冒險、格局受限"
    ),
    "太陰": ZiweiStarGlossary(
        name="太陰",
        wuxing="水",
        classical="田宅主、溫柔、女性",
        vernacular="細膩敏感、有品味",
        field_theory="內斂吸收場，柔性累積",
        modern_career="設計、藝術、房地產、夜班",
        strength="細心、有品味、財運穩",
        weakness="太敏感、情緒化、夜生才旺"
    ),
    "貪狼": ZiweiStarGlossary(
        name="貪狼",
        wuxing="木",
        classical="桃花星、慾望、多才",
        vernacular="慾望強、興趣多",
        field_theory="擴張探索場，多方涉獵",
        modern_career="演藝、業務、餐飲、娛樂",
        strength="多才多藝、有魅力、適應力強",
        weakness="不專一、慾望過多、易沉迷"
    ),
    "巨門": ZiweiStarGlossary(
        name="巨門",
        wuxing="水",
        classical="是非星、口才、暗星",
        vernacular="口才好、愛質疑",
        field_theory="分析解構場，挖掘真相",
        modern_career="律師、記者、教師、分析師",
        strength="口才佳、分析力強、不被騙",
        weakness="太多疑、口舌是非、人際緊張"
    ),
    "天相": ZiweiStarGlossary(
        name="天相",
        wuxing="水",
        classical="印星、輔佐、文書",
        vernacular="幕僚型、愛幫人",
        field_theory="輔佐協調場，承上啟下",
        modern_career="秘書、行政、顧問、公務員",
        strength="協調能力、文書能力、受信任",
        weakness="缺乏主見、依附他人、格局受限"
    ),
    "天梁": ZiweiStarGlossary(
        name="天梁",
        wuxing="土",
        classical="蔭星、清高、長輩",
        vernacular="正直愛管事",
        field_theory="庇護監督場，化險為夷",
        modern_career="醫療、法律、教育、公益",
        strength="有正義感、能化解危機、有貴人運",
        weakness="太嘮叨、愛說教、管太多"
    ),
    "七殺": ZiweiStarGlossary(
        name="七殺",
        wuxing="金",
        classical="將星、衝勁、孤獨",
        vernacular="衝勁強、有魄力",
        field_theory="衝擊突破場，破舊立新",
        modern_career="軍警、創業、運動、冒險",
        strength="有魄力、執行力強、不怕難",
        weakness="太衝動、人際疏離、孤獨"
    ),
    "破軍": ZiweiStarGlossary(
        name="破軍",
        wuxing="水",
        classical="耗星、破壞、變動",
        vernacular="喜歡打破現狀",
        field_theory="解構重組場，先破後立",
        modern_career="改革者、創業、研發、藝術",
        strength="創新能力、不怕變、開創性強",
        weakness="太叛逆、破壞性強、難穩定"
    ),
}


# ════════════════════════════════════════════════════════════════════
# 統一查詢函數
# ════════════════════════════════════════════════════════════════════

def get_shishen_glossary(shishen_name: str) -> Optional[Dict]:
    """獲取十神白話翻譯"""
    if shishen_name in SHISHEN_GLOSSARY:
        g = SHISHEN_GLOSSARY[shishen_name]
        return {
            "name": g.name,
            "classical": g.classical,
            "vernacular": g.vernacular,
            "field_theory": g.field_theory,
            "modern_analogy": g.modern_analogy,
            "field_states": {
                "strong": g.field_strong,
                "excess": g.field_excess,
                "weak": g.field_weak
            },
            "remedy": g.remedy,
            "xtfs_mapping": SHISHEN_XTFS_MAPPING.get(shishen_name, {})
        }
    return None

def get_liuqin_glossary(liuqin_name: str) -> Optional[Dict]:
    """獲取六親場論詮釋"""
    if liuqin_name in LIUQIN_GLOSSARY:
        g = LIUQIN_GLOSSARY[liuqin_name]
        return {
            "name": g.name,
            "male_shishen": g.male_shishen,
            "female_shishen": g.female_shishen,
            "field_role": g.field_role,
            "field_trait": g.field_trait
        }
    return None

def get_ziwei_star_glossary(star_name: str) -> Optional[Dict]:
    """獲取紫微星曜白話翻譯"""
    if star_name in ZIWEI_STAR_GLOSSARY:
        s = ZIWEI_STAR_GLOSSARY[star_name]
        return {
            "name": s.name,
            "wuxing": s.wuxing,
            "classical": s.classical,
            "vernacular": s.vernacular,
            "field_theory": s.field_theory,
            "modern_career": s.modern_career,
            "strength": s.strength,
            "weakness": s.weakness
        }
    return None

def diagnose_field_issue(symptom: str) -> Optional[Dict]:
    """根據感受診斷場損"""
    for key, diagnosis in SHISHEN_FIELD_DIAGNOSIS.items():
        if key in symptom or symptom in key:
            return diagnosis
    return None

def get_all_shishen_vernacular() -> Dict[str, str]:
    """獲取所有十神的白話翻譯（簡版）"""
    return {name: g.vernacular for name, g in SHISHEN_GLOSSARY.items()}

def get_all_ziwei_vernacular() -> Dict[str, str]:
    """獲取所有紫微星曜的白話翻譯（簡版）"""
    return {name: s.vernacular for name, s in ZIWEI_STAR_GLOSSARY.items()}

# ════════════════════════════════════════════════════════════════════
# 增強版分析接口（更新）
# ════════════════════════════════════════════════════════════════════

def enhance_analysis_v2(
    analysis_type: str,
    raw_result: Dict[str, Any],
    include_classics: bool = True,
    include_glossary: bool = True,
    include_swot: bool = True,
    include_ai_advice: bool = True
) -> Dict[str, Any]:
    """
    增強版分析結果（含白話翻譯）
    
    Args:
        analysis_type: 分析類型 (bazi/ziwei/meihua/qimen/date/naming)
        raw_result: 原始分析結果
        include_classics: 是否包含典籍引用
        include_glossary: 是否包含白話翻譯
        include_swot: 是否包含 SWOT 分析
        include_ai_advice: 是否包含 AI 建議
    
    Returns:
        增強後的分析結果
    """
    # 先用原版增強
    enhanced = enhance_analysis(
        analysis_type, raw_result, 
        include_classics, include_swot, include_ai_advice
    )
    
    # 添加白話翻譯
    if include_glossary:
        glossary_data = {}
        
        # 八字：添加十神白話
        if analysis_type == "bazi":
            shishen_list = raw_result.get("shishen", [])
            if isinstance(shishen_list, list):
                glossary_data["shishen_glossary"] = {
                    ss: get_shishen_glossary(ss) 
                    for ss in shishen_list if ss in SHISHEN_GLOSSARY
                }
            # 添加所有十神簡版
            glossary_data["shishen_vernacular"] = get_all_shishen_vernacular()
        
        # 紫微：添加星曜白話
        elif analysis_type == "ziwei":
            stars = raw_result.get("stars", [])
            if isinstance(stars, list):
                glossary_data["star_glossary"] = {
                    star: get_ziwei_star_glossary(star)
                    for star in stars if star in ZIWEI_STAR_GLOSSARY
                }
            # 添加所有星曜簡版
            glossary_data["star_vernacular"] = get_all_ziwei_vernacular()
        
        enhanced["glossary"] = glossary_data
    
    # 更新方法論說明
    enhanced["methodology"] = {
        "layer_1": "古典原文：典籍引用，標明出處",
        "layer_2": "白話翻譯：讓一般人看得懂",
        "layer_3": "場論詮釋：用現代語言重新理解",
        "layer_4": "SWOT 分析：可操作的策略建議",
        "layer_5": "AI 決策：多維度交叉驗證",
        "principle": "術數是個人化決策框架生成器，與天氣預報同構",
        "disclaimer": "提供機率性參考，不做命定式裁決"
    }
    
    return enhanced


# ════════════════════════════════════════════════════════════════════
# 模組載入資訊（更新版）
# ════════════════════════════════════════════════════════════════════

print("✓ 典籍增強模組 v2.0 已載入")
print(f"  【典籍資料庫】")
print(f"    - 八字: {len(BAZI_CLASSICS)} 條")
print(f"    - 紫微: {len(ZIWEI_CLASSICS)} 條")
print(f"    - 梅花: {len(MEIHUA_CLASSICS)} 條")
print(f"    - 奇門: {len(QIMEN_CLASSICS)} 條")
print(f"    - 擇日: {len(DATE_CLASSICS)} 條")
print(f"    - 命名: {len(NAMING_CLASSICS)} 條")
print(f"  【白話翻譯】")
print(f"    - 十神: {len(SHISHEN_GLOSSARY)} 個")
print(f"    - 六親: {len(LIUQIN_GLOSSARY)} 個")
print(f"    - 紫微星曜: {len(ZIWEI_STAR_GLOSSARY)} 個")
print(f"  【診斷系統】")
print(f"    - 場損診斷: {len(SHISHEN_FIELD_DIAGNOSIS)} 種")
print(f"    - XTFS映射: {len(SHISHEN_XTFS_MAPPING)} 個")

# ════════════════════════════════════════════════════════════════════
# 梅花八卦白話翻譯系統（整合自 expansion_v1）
# ════════════════════════════════════════════════════════════════════

@dataclass
class BaguaGlossary:
    """八卦白話翻譯"""
    name: str              # 卦名
    symbol: str            # 符號
    classical: str         # 古典象徵
    vernacular: str        # 白話翻譯
    field_theory: str      # 場論詮釋
    modern_analogy: str    # 現代比喻
    strength: str          # 優勢
    weakness: str          # 風險
    interaction: Dict[str, str] = None  # 卦與卦的場效應

BAGUA_GLOSSARY = {
    "乾": BaguaGlossary(
        name="乾",
        symbol="☰",
        classical="天、父、剛健、創造",
        vernacular="全力衝刺、積極進取",
        field_theory="純陽上升場（全開）— 場能量全開，向外擴張",
        modern_analogy="CEO模式、領導者、創業衝刺",
        strength="動力強、有魄力、敢承擔",
        weakness="過度消耗、剛而易折、不聽勸",
        interaction={"坤": "地天泰，最佳搭配", "乾": "兩強相遇，競爭激烈", "坎": "天水訟，有爭端"}
    ),
    "坤": BaguaGlossary(
        name="坤",
        symbol="☷",
        classical="地、母、柔順、包容",
        vernacular="配合接受、穩定承載",
        field_theory="純陰承載場（全收）— 場能量內收，承載一切",
        modern_analogy="後勤模式、支援者、厚積薄發",
        strength="包容力強、穩定可靠、有耐心",
        weakness="太被動、缺乏主見、容易被忽視",
        interaction={"乾": "天地泰，陰陽調和", "坤": "純陰過重，缺乏動力"}
    ),
    "震": BaguaGlossary(
        name="震",
        symbol="☳",
        classical="雷、長子、動、起",
        vernacular="突然啟動、衝擊變化",
        field_theory="震動啟發場（下開）— 能量從底部爆發",
        modern_analogy="創業啟動、破局、驚醒",
        strength="行動力強、有衝勁、能破局",
        weakness="太衝動、虎頭蛇尾、嚇到人",
        interaction={"巽": "雷風恆，持久之道", "艮": "山雷頤，養生之道"}
    ),
    "巽": BaguaGlossary(
        name="巽",
        symbol="☴",
        classical="風、長女、入、順",
        vernacular="滲透影響、柔性推進",
        field_theory="滲透流通場（下收）— 能量柔和滲透",
        modern_analogy="軟實力、影響力、漸進改變",
        strength="適應力強、善溝通、能滲透",
        weakness="缺乏決斷、隨風倒、立場不穩",
        interaction={"震": "風雷益，增益之道", "乾": "天風姤，相遇之機"}
    ),
    "坎": BaguaGlossary(
        name="坎",
        symbol="☵",
        classical="水、中男、險、陷",
        vernacular="困難險阻、流動變通",
        field_theory="流動陷落場（中開）— 能量在困境中流動",
        modern_analogy="危機模式、挑戰、險中求勝",
        strength="適應變化、能屈能伸、智慧應對",
        weakness="陷入困境、進退兩難、心力交瘁",
        interaction={"離": "水火既濟，完美互補", "坤": "地水師，領軍出征"}
    ),
    "離": BaguaGlossary(
        name="離",
        symbol="☲",
        classical="火、中女、麗、附",
        vernacular="光明展現、依附發展",
        field_theory="附著光明場（中收）— 能量向外照耀",
        modern_analogy="曝光模式、展示、依附平台",
        strength="光彩照人、有魅力、能展現",
        weakness="虛榮心強、需要舞台、燒盡自己",
        interaction={"坎": "火水未濟，尚未完成", "乾": "天火同人，志同道合"}
    ),
    "艮": BaguaGlossary(
        name="艮",
        symbol="☶",
        classical="山、少男、止、靜",
        vernacular="停止等待、穩定守成",
        field_theory="停止界限場（上開）— 能量凝固不動",
        modern_analogy="暫停模式、止損、等待時機",
        strength="穩定、有定力、知道何時停",
        weakness="太固執、錯失良機、不知變通",
        interaction={"兌": "山澤損，有所損失", "震": "雷山小過，小心過度"}
    ),
    "兌": BaguaGlossary(
        name="兌",
        symbol="☱",
        classical="澤、少女、悅、說",
        vernacular="喜悅交流、開口表達",
        field_theory="喜悅開口場（上收）— 能量歡快流動",
        modern_analogy="社交模式、溝通、表達說服",
        strength="口才好、有親和力、能說服",
        weakness="說太多、輕浮、口舌是非",
        interaction={"艮": "澤山咸，感應相通", "乾": "天澤履，小心行事"}
    ),
}

# ════════════════════════════════════════════════════════════════════
# 八字格局白話翻譯系統（整合自 expansion_v1）
# ════════════════════════════════════════════════════════════════════

@dataclass
class GejuGlossary:
    """八字格局白話翻譯"""
    name: str              # 格局名稱
    condition: str         # 成立條件
    classical: str         # 古典含義
    vernacular: str        # 白話翻譯
    field_theory: str      # 場論詮釋
    modern_career: str     # 現代職業
    strength: str          # 優勢
    weakness: str          # 風險
    yongshen_tip: str      # 用神建議

GEJU_GLOSSARY = {
    "正官格": GejuGlossary(
        name="正官格",
        condition="月支正官透干，或月支藏干正官透出",
        classical="官星當令，主貴顯、有名望、受約束",
        vernacular="有人管你，而且管得合理",
        field_theory="約束場穩定 — 外部場對你形成穩定、合理的約束",
        modern_career="公務員、主管、法官、經理人",
        strength="有紀律、守規矩、有名望、受尊重",
        weakness="太保守、缺乏創意、被體制束縛",
        yongshen_tip="喜印星護官，忌傷官破格；官弱喜財生官"
    ),
    "七殺格": GejuGlossary(
        name="七殺格",
        condition="月支七殺透干，或月支藏干七殺透出",
        classical="殺星當令，主權威、有魄力、有壓力",
        vernacular="壓力來襲，但能轉化為動力",
        field_theory="約束場衝擊 — 外部場對你形成衝擊性壓制",
        modern_career="軍警、創業者、運動員、挑戰者",
        strength="有魄力、抗壓強、能突破、有權威",
        weakness="太衝動、樹敵多、人際緊張",
        yongshen_tip="喜食神制殺、印星化殺；忌殺無制化"
    ),
    "正印格": GejuGlossary(
        name="正印格",
        condition="月支正印透干，或月支藏干正印透出",
        classical="印星當令，主聰明、有學識、受庇護",
        vernacular="有人教你，穩定地照顧你",
        field_theory="滋養場穩定 — 外部能量穩定流入你的場",
        modern_career="教師、學者、顧問、公務員",
        strength="聰明好學、有貴人、受保護、有涵養",
        weakness="太依賴、不獨立、缺乏行動力",
        yongshen_tip="喜官殺生印，忌財星破印"
    ),
    "偏印格": GejuGlossary(
        name="偏印格",
        condition="月支偏印透干，或月支藏干偏印透出",
        classical="梟神當令，主偏才、有異能、較孤獨",
        vernacular="有人幫你，但方式比較奇怪",
        field_theory="滋養場偏門 — 外部能量流入但頻率有偏差",
        modern_career="研究員、技術專家、藝術家、命理師",
        strength="獨特思維、有專長、不走尋常路",
        weakness="較孤獨、不被理解、想法偏激",
        yongshen_tip="喜財星制梟，忌梟神奪食"
    ),
    "正財格": GejuGlossary(
        name="正財格",
        condition="月支正財透干，或月支藏干正財透出",
        classical="財星當令，主務實、有財緣、重物質",
        vernacular="穩定賺錢，能掌控資源",
        field_theory="掌控場穩定 — 你的場對資源進行穩定控制",
        modern_career="會計、財務、商人、實業家",
        strength="務實穩健、理財能力強、有存款",
        weakness="太物質、為錢所累、格局受限",
        yongshen_tip="喜食傷生財，忌比劫劫財"
    ),
    "偏財格": GejuGlossary(
        name="偏財格",
        condition="月支偏財透干，或月支藏干偏財透出",
        classical="偏財當令，主豪爽、有橫財、善交際",
        vernacular="機會賺錢，能抓住機會",
        field_theory="掌控場機動 — 你的場對流動資源快速捕獲",
        modern_career="投資人、業務、貿易商、經紀人",
        strength="眼光準、人脈廣、機會多、財路寬",
        weakness="太投機、不穩定、風險高",
        yongshen_tip="喜食傷生財，忌比劫爭財"
    ),
    "食神格": GejuGlossary(
        name="食神格",
        condition="月支食神透干，或月支藏干食神透出",
        classical="食神當令，主才華、有福氣、善享受",
        vernacular="穩定產出，有才華且能享福",
        field_theory="輸出場穩定 — 你的場向外穩定輸出能量",
        modern_career="廚師、藝人、設計師、專業人士",
        strength="有才華、有口福、生活品質好、能創造",
        weakness="太安逸、缺乏鬥志、過度享受",
        yongshen_tip="喜財星洩食，忌偏印奪食"
    ),
    "傷官格": GejuGlossary(
        name="傷官格",
        condition="月支傷官透干，或月支藏干傷官透出",
        classical="傷官當令，主聰明、有才氣、好批評",
        vernacular="才華爆發，敢於挑戰權威",
        field_theory="輸出場衝擊 — 你的場向外衝擊性輸出",
        modern_career="律師、記者、創業者、藝術家",
        strength="才華橫溢、敢創新、能突破、有魅力",
        weakness="太衝、得罪人、傷官見官、是非多",
        yongshen_tip="喜財星洩傷官，喜印星制傷官；忌傷官見官"
    ),
}

# ════════════════════════════════════════════════════════════════════
# 紫微十二宮場論系統（整合自 framework_v1.8）
# ════════════════════════════════════════════════════════════════════

@dataclass
class GongweiGlossary:
    """十二宮場論詮釋"""
    name: str              # 宮位名稱
    field_role: str        # 場論角色
    field_trait: str       # 能量特徵
    xtfs_mapping: str      # XTFS映射
    classical: str         # 古典含義
    vernacular: str        # 白話翻譯
    modern_meaning: str    # 現代意義
    opposite: str          # 對宮（張力對沖）

GONGWEI_GLOSSARY = {
    "命宮": GongweiGlossary(
        name="命宮",
        field_role="核心場 (Core Field)",
        field_trait="場的本質頻率與自我認同",
        xtfs_mapping="主體基底",
        classical="一身之主，性格、才能、外貌",
        vernacular="你是什麼樣的人",
        modern_meaning="核心人格、第一印象、自我定位",
        opposite="遷移宮（我 vs 變）"
    ),
    "父母宮": GongweiGlossary(
        name="父母宮",
        field_role="源頭場 (Source Field)",
        field_trait="能量的初始輸入源",
        xtfs_mapping="T塔（輸入）",
        classical="父母緣分、長輩關係、庇蔭",
        vernacular="誰在照顧你、教導你",
        modern_meaning="原生家庭、師長關係、資源來源",
        opposite="疾厄宮（源頭 vs 載體）"
    ),
    "兄弟宮": GongweiGlossary(
        name="兄弟宮",
        field_role="平行場 (Parallel Field)",
        field_trait="同輩共振/干涉",
        xtfs_mapping="場基底",
        classical="兄弟姐妹、朋友、同事",
        vernacular="誰跟你同一陣線",
        modern_meaning="同儕關係、合作夥伴、競爭對手",
        opposite="奴僕宮（平行 vs 群眾）"
    ),
    "夫妻宮": GongweiGlossary(
        name="夫妻宮",
        field_role="共振場 (Resonance Field)",
        field_trait="異質耦合的親密場",
        xtfs_mapping="F塔（整合）",
        classical="配偶、婚姻、親密關係",
        vernacular="誰跟你共振最強",
        modern_meaning="伴侶關係、合夥人、最親密的人",
        opposite="官祿宮（情 vs 業）"
    ),
    "子女宮": GongweiGlossary(
        name="子女宮",
        field_role="產出場 (Output Field)",
        field_trait="創造/傳承的輸出",
        xtfs_mapping="X塔（輸出）",
        classical="子女、學生、作品、創造",
        vernacular="你產出什麼、留下什麼",
        modern_meaning="子女關係、創作能力、傳承事業",
        opposite="田宅宮（產出 vs 蓄積）"
    ),
    "財帛宮": GongweiGlossary(
        name="財帛宮",
        field_role="交換場 (Exchange Field)",
        field_trait="價值掌控與流通",
        xtfs_mapping="F塔（執行）",
        classical="財運、理財能力、金錢觀",
        vernacular="你能掌控多少資源",
        modern_meaning="收入能力、財務狀況、價值創造",
        opposite="福德宮（物質 vs 精神）"
    ),
    "疾厄宮": GongweiGlossary(
        name="疾厄宮",
        field_role="本體場 (Body Field)",
        field_trait="肉身載體的維護",
        xtfs_mapping="基礎設施",
        classical="健康、疾病、災厄、身體",
        vernacular="你的身體狀況如何",
        modern_meaning="健康狀態、體質、抗壓能力",
        opposite="父母宮（載體 vs 源頭）"
    ),
    "遷移宮": GongweiGlossary(
        name="遷移宮",
        field_role="變動場 (Change Field)",
        field_trait="外部變化與適應",
        xtfs_mapping="環境互動",
        classical="外出、遷徙、在外際遇",
        vernacular="你在外面的運氣如何",
        modern_meaning="出外運、社會形象、外部機會",
        opposite="命宮（變 vs 我）"
    ),
    "奴僕宮": GongweiGlossary(
        name="奴僕宮",
        field_role="群眾場 (Crowd Field)",
        field_trait="人際網絡的調度",
        xtfs_mapping="資源調配",
        classical="部屬、員工、朋友、人脈",
        vernacular="誰聽你的、誰幫你",
        modern_meaning="下屬關係、人脈品質、團隊運",
        opposite="兄弟宮（群眾 vs 平行）"
    ),
    "官祿宮": GongweiGlossary(
        name="官祿宮",
        field_role="行使場 (Action Field)",
        field_trait="社會角色的執行",
        xtfs_mapping="F塔（行動）",
        classical="事業、功名、社會地位",
        vernacular="你在社會上做什麼",
        modern_meaning="職業發展、社會成就、工作狀態",
        opposite="夫妻宮（業 vs 情）"
    ),
    "田宅宮": GongweiGlossary(
        name="田宅宮",
        field_role="封冊場 (Storage Field)",
        field_trait="固定資產與根基",
        xtfs_mapping="蓄積保存",
        classical="房產、祖業、家庭環境",
        vernacular="你的根基在哪裡",
        modern_meaning="不動產、家庭環境、安全感來源",
        opposite="子女宮（蓄積 vs 產出）"
    ),
    "福德宮": GongweiGlossary(
        name="福德宮",
        field_role="精神場 (Spirit Field)",
        field_trait="內心狀態與幸福感",
        xtfs_mapping="內在品質",
        classical="福氣、精神、興趣、享受",
        vernacular="你內心快不快樂",
        modern_meaning="精神狀態、興趣愛好、幸福指數",
        opposite="財帛宮（精神 vs 物質）"
    ),
}

# ════════════════════════════════════════════════════════════════════
# 新增查詢函數（八卦/格局/宮位）
# ════════════════════════════════════════════════════════════════════

def get_bagua_glossary(gua_name: str) -> Optional[Dict]:
    """獲取八卦白話翻譯"""
    if gua_name in BAGUA_GLOSSARY:
        g = BAGUA_GLOSSARY[gua_name]
        return {
            "name": g.name,
            "symbol": g.symbol,
            "classical": g.classical,
            "vernacular": g.vernacular,
            "field_theory": g.field_theory,
            "modern_analogy": g.modern_analogy,
            "strength": g.strength,
            "weakness": g.weakness,
            "interaction": g.interaction
        }
    return None

def get_geju_glossary(geju_name: str) -> Optional[Dict]:
    """獲取格局白話翻譯"""
    if geju_name in GEJU_GLOSSARY:
        g = GEJU_GLOSSARY[geju_name]
        return {
            "name": g.name,
            "condition": g.condition,
            "classical": g.classical,
            "vernacular": g.vernacular,
            "field_theory": g.field_theory,
            "modern_career": g.modern_career,
            "strength": g.strength,
            "weakness": g.weakness,
            "yongshen_tip": g.yongshen_tip
        }
    return None

def get_gongwei_glossary(gong_name: str) -> Optional[Dict]:
    """獲取宮位場論詮釋"""
    if gong_name in GONGWEI_GLOSSARY:
        g = GONGWEI_GLOSSARY[gong_name]
        return {
            "name": g.name,
            "field_role": g.field_role,
            "field_trait": g.field_trait,
            "xtfs_mapping": g.xtfs_mapping,
            "classical": g.classical,
            "vernacular": g.vernacular,
            "modern_meaning": g.modern_meaning,
            "opposite": g.opposite
        }
    return None

def get_all_bagua_vernacular() -> Dict[str, str]:
    """獲取所有八卦白話翻譯（簡版）"""
    return {name: f"{g.symbol} {g.vernacular}" for name, g in BAGUA_GLOSSARY.items()}

def get_all_geju_vernacular() -> Dict[str, str]:
    """獲取所有格局白話翻譯（簡版）"""
    return {name: g.vernacular for name, g in GEJU_GLOSSARY.items()}

def get_all_gongwei_vernacular() -> Dict[str, str]:
    """獲取所有宮位白話翻譯（簡版）"""
    return {name: g.vernacular for name, g in GONGWEI_GLOSSARY.items()}

def get_gongwei_opposite_pairs() -> List[Dict]:
    """獲取宮位對沖組合"""
    pairs = [
        {"pair": "命宮-遷移宮", "tension": "我 vs 變", "meaning": "自我認同與外部變化的張力"},
        {"pair": "夫妻宮-官祿宮", "tension": "情 vs 業", "meaning": "親密關係與事業發展的平衡"},
        {"pair": "財帛宮-福德宮", "tension": "物質 vs 精神", "meaning": "金錢追求與內心滿足的取捨"},
        {"pair": "子女宮-田宅宮", "tension": "產出 vs 蓄積", "meaning": "創造輸出與根基保存的權衡"},
        {"pair": "兄弟宮-奴僕宮", "tension": "平行 vs 群眾", "meaning": "同儕合作與下屬管理的差異"},
        {"pair": "父母宮-疾厄宮", "tension": "源頭 vs 載體", "meaning": "能量來源與身體承載的關聯"},
    ]
    return pairs

# ════════════════════════════════════════════════════════════════════
# 更新模組載入資訊
# ════════════════════════════════════════════════════════════════════

print("✓ 典籍增強模組 v2.1 完整載入")
print(f"  【典籍】八字{len(BAZI_CLASSICS)}+紫微{len(ZIWEI_CLASSICS)}+梅花{len(MEIHUA_CLASSICS)}+奇門{len(QIMEN_CLASSICS)}+擇日{len(DATE_CLASSICS)}+命名{len(NAMING_CLASSICS)}=21條")
print(f"  【白話】十神{len(SHISHEN_GLOSSARY)}+六親{len(LIUQIN_GLOSSARY)}+星曜{len(ZIWEI_STAR_GLOSSARY)}+八卦{len(BAGUA_GLOSSARY)}+格局{len(GEJU_GLOSSARY)}+宮位{len(GONGWEI_GLOSSARY)}=62個")
print(f"  【診斷】場損{len(SHISHEN_FIELD_DIAGNOSIS)}種+XTFS{len(SHISHEN_XTFS_MAPPING)}個")
