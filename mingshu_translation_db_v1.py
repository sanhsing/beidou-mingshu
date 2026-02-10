#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
mingshu_translation_db_v1.py - 北斗命數翻譯資料庫 v1.0
=====================================================
北斗七星文創 × 織明 × 澄韻 × 流祇

PYLIB First: 一次建立，處處引用
所有術語的統一翻譯來源

包含：
- 白話解釋 (一般人能懂的語言)
- 場論視角 (現代物理學思維)
- 實用建議 (可操作的行動指引)

XTF⁸ + XTFS + @11star 協作
T層(翻譯) + F層(場論) 核心模組

📚 知識點：
    「翻譯 = 跨越認知鴻溝的橋樑」
    「PYLIB First = 複利思維的代碼實踐」
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from enum import Enum

# =============================================================================
# 翻譯條目結構
# =============================================================================

@dataclass
class TranslationEntry:
    """翻譯條目"""
    term: str           # 術語
    category: str       # 類別
    one_line: str       # 一句話說明
    white_speak: str    # 白話解釋
    field_theory: str   # 場論視角
    advice: str         # 實用建議
    keywords: List[str] # 關鍵詞
    
    def to_dict(self) -> Dict:
        return asdict(self)
    
    def format_output(self) -> str:
        """格式化輸出"""
        return f"""【{self.term}】{self.one_line}
✦ 白話：{self.white_speak}
✦ 場論：{self.field_theory}
✦ 建議：{self.advice}"""


# =============================================================================
# 八字翻譯資料庫
# =============================================================================

# ---------- 天干 ----------
TIANGAN_DB = {
    "甲": TranslationEntry(
        term="甲", category="天干",
        one_line="參天大樹，開創之首",
        white_speak="像一棵大樹，有向上生長的力量。代表開創、領導、正直、有理想。",
        field_theory="陽木場：向上生發的能量，具有開創性和領導性，場態呈垂直向上擴展",
        advice="適合開創新局、帶領團隊，但要注意不要過於固執",
        keywords=["開創", "領導", "正直", "向上"]
    ),
    "乙": TranslationEntry(
        term="乙", category="天干",
        one_line="藤蔓花草，柔韌適應",
        white_speak="像藤蔓或花草，看似柔弱但很有韌性。代表柔順、適應力強、有藝術氣質。",
        field_theory="陰木場：柔性延展的能量，具有適應性和包容性，場態呈水平蔓延",
        advice="善用柔性力量，借力使力，在變化中找到機會",
        keywords=["柔韌", "適應", "藝術", "變通"]
    ),
    "丙": TranslationEntry(
        term="丙", category="天干",
        one_line="太陽之火，光明熱情",
        white_speak="像太陽一樣，光明磊落、熱情大方。代表積極、樂觀、有感染力。",
        field_theory="陽火場：輻射散發的能量，具有照耀性和溫暖性，場態呈全方位擴散",
        advice="發揮你的熱情和感染力，但要注意不要過度消耗自己",
        keywords=["光明", "熱情", "樂觀", "感染力"]
    ),
    "丁": TranslationEntry(
        term="丁", category="天干",
        one_line="燭火星光，溫暖細膩",
        white_speak="像蠟燭或星光，溫暖但不刺眼。代表細膩、專注、有內涵。",
        field_theory="陰火場：聚焦凝聚的能量，具有專注性和穿透性，場態呈定向照射",
        advice="發揮細膩觀察力，專注深耕某個領域",
        keywords=["溫暖", "細膩", "專注", "內斂"]
    ),
    "戊": TranslationEntry(
        term="戊", category="天干",
        one_line="高山大地，穩重可靠",
        white_speak="像高山或大地，穩重踏實、可以依靠。代表誠信、包容、有承載力。",
        field_theory="陽土場：承載穩定的能量，具有包容性和可靠性，場態呈向下扎根",
        advice="發揮穩定可靠的特質，成為別人的依靠",
        keywords=["穩重", "可靠", "包容", "承載"]
    ),
    "己": TranslationEntry(
        term="己", category="天干",
        one_line="田園沃土，滋養萬物",
        white_speak="像田園的土壤，能滋養萬物生長。代表務實、謹慎、善於培養。",
        field_theory="陰土場：滋養孕育的能量，具有培育性和轉化性，場態呈內化吸收",
        advice="善於培養和支持他人，在幕後發揮影響力",
        keywords=["滋養", "務實", "謹慎", "培育"]
    ),
    "庚": TranslationEntry(
        term="庚", category="天干",
        one_line="刀劍斧鉞，剛毅果斷",
        white_speak="像刀劍一樣，鋒利果斷、有執行力。代表剛強、決斷、有魄力。",
        field_theory="陽金場：剛性切割的能量，具有決斷性和執行性，場態呈銳利穿透",
        advice="發揮決斷力和執行力，但要注意不要傷人傷己",
        keywords=["剛毅", "果斷", "執行力", "魄力"]
    ),
    "辛": TranslationEntry(
        term="辛", category="天干",
        one_line="珠寶首飾，精緻敏感",
        white_speak="像珠寶首飾，精緻美麗但也敏感。代表細膩、有品味、追求完美。",
        field_theory="陰金場：精煉收斂的能量，具有敏感性和審美性，場態呈內向凝聚",
        advice="發揮審美能力和細膩特質，但不要過於敏感",
        keywords=["精緻", "敏感", "品味", "完美"]
    ),
    "壬": TranslationEntry(
        term="壬", category="天干",
        one_line="江河大海，智慧奔放",
        white_speak="像江河大海，有容乃大、智慧深沉。代表聰明、變通、有遠見。",
        field_theory="陽水場：流動奔放的能量，具有智慧性和包容性，場態呈大範圍流動",
        advice="發揮智慧和包容力，像水一樣找到出路",
        keywords=["智慧", "包容", "變通", "遠見"]
    ),
    "癸": TranslationEntry(
        term="癸", category="天干",
        one_line="雨露泉水，滋潤細膩",
        white_speak="像雨露或泉水，默默滋潤萬物。代表敏感、直覺強、善於洞察。",
        field_theory="陰水場：滲透滋潤的能量，具有敏感性和洞察性，場態呈微觀滲透",
        advice="相信直覺，善用洞察力，在細節中發現機會",
        keywords=["滋潤", "敏感", "直覺", "洞察"]
    ),
}

# ---------- 地支 ----------
DIZHI_DB = {
    "子": TranslationEntry(
        term="子", category="地支",
        one_line="夜半子時，萬物孕育",
        white_speak="代表深夜，萬物在黑暗中孕育。有智慧、善謀略、喜歡思考。",
        field_theory="水場極點：能量在最深處醞釀，具有潛藏性和智慧性",
        advice="善用夜晚和安靜的時間思考規劃",
        keywords=["智慧", "孕育", "潛藏", "謀略"]
    ),
    "丑": TranslationEntry(
        term="丑", category="地支",
        one_line="凌晨丑時，蓄勢待發",
        white_speak="代表凌晨，黎明前的蓄積。穩重務實、有耐心、善於積累。",
        field_theory="土場濕寒：能量在積累轉化，具有儲存性和轉化性",
        advice="耐心積累，厚積薄發",
        keywords=["穩重", "積累", "耐心", "務實"]
    ),
    "寅": TranslationEntry(
        term="寅", category="地支",
        one_line="黎明寅時，萬物甦醒",
        white_speak="代表黎明，萬物開始甦醒。有開創精神、行動力強、充滿希望。",
        field_theory="木場生發：能量開始向上噴發，具有開創性和生命力",
        advice="把握早晨的能量，適合開始新計劃",
        keywords=["開創", "行動", "希望", "生機"]
    ),
    "卯": TranslationEntry(
        term="卯", category="地支",
        one_line="日出卯時，生機蓬勃",
        white_speak="代表日出，生機蓬勃。溫和有禮、人緣好、有藝術氣質。",
        field_theory="木場旺盛：能量蓬勃外展，具有親和性和生長性",
        advice="發揮親和力，適合社交和創作",
        keywords=["生機", "溫和", "人緣", "藝術"]
    ),
    "辰": TranslationEntry(
        term="辰", category="地支",
        one_line="上午辰時，龍騰萬里",
        white_speak="代表上午，精力充沛。有理想抱負、變化多端、有神秘感。",
        field_theory="土場濕潤：能量充沛但需轉化，具有變化性和包容性",
        advice="把握上午的高效時段，但要注意落實",
        keywords=["理想", "變化", "神秘", "包容"]
    ),
    "巳": TranslationEntry(
        term="巳", category="地支",
        one_line="近午巳時，熱力上升",
        white_speak="代表接近中午，熱力上升。聰明機智、有魅力、善於表達。",
        field_theory="火場升騰：能量快速上升，具有活躍性和表達性",
        advice="發揮口才和魅力，適合展現自己",
        keywords=["聰明", "魅力", "表達", "機智"]
    ),
    "午": TranslationEntry(
        term="午", category="地支",
        one_line="正午時分，陽氣最旺",
        white_speak="代表正午，陽氣最盛。熱情開朗、愛出風頭、精力旺盛。",
        field_theory="火場極盛：能量達到頂峰，具有輻射性和領導性",
        advice="發揮熱情和領導力，但要注意保存精力",
        keywords=["熱情", "開朗", "精力", "領導"]
    ),
    "未": TranslationEntry(
        term="未", category="地支",
        one_line="午後未時，溫和收斂",
        white_speak="代表午後，開始收斂。溫和體貼、有愛心、善於照顧人。",
        field_theory="土場乾燥：能量開始內收，具有滋養性和包容性",
        advice="發揮關懷他人的特質，適合服務性工作",
        keywords=["溫和", "體貼", "愛心", "包容"]
    ),
    "申": TranslationEntry(
        term="申", category="地支",
        one_line="下午申時，金氣漸升",
        white_speak="代表下午，開始轉涼。聰明靈活、有創意、善於應變。",
        field_theory="金場初生：能量轉向收斂，具有靈活性和創造性",
        advice="發揮靈活變通的能力，善於解決問題",
        keywords=["聰明", "靈活", "創意", "應變"]
    ),
    "酉": TranslationEntry(
        term="酉", category="地支",
        one_line="傍晚酉時，金氣正旺",
        white_speak="代表傍晚，準備休息。精緻講究、有品味、注重外表。",
        field_theory="金場旺盛：能量精煉收斂，具有審美性和精緻性",
        advice="發揮審美能力，適合精細工作",
        keywords=["精緻", "品味", "講究", "審美"]
    ),
    "戌": TranslationEntry(
        term="戌", category="地支",
        one_line="入夜戌時，忠誠守護",
        white_speak="代表入夜，萬物歸宿。忠誠可靠、有責任感、重視承諾。",
        field_theory="土場乾燥：能量守護收藏，具有忠誠性和保護性",
        advice="發揮忠誠可靠的特質，適合守成",
        keywords=["忠誠", "可靠", "責任", "守護"]
    ),
    "亥": TranslationEntry(
        term="亥", category="地支",
        one_line="深夜亥時，萬物休養",
        white_speak="代表深夜，萬物休養。有包容心、想像力豐富、善於體諒。",
        field_theory="水場初生：能量開始潛藏，具有包容性和想像力",
        advice="善用休息時間，讓身心恢復",
        keywords=["包容", "想像", "休養", "體諒"]
    ),
}

# ---------- 十神 ----------
SHISHEN_DB = {
    "比肩": TranslationEntry(
        term="比肩", category="十神",
        one_line="像你的同學或兄弟",
        white_speak="代表和你平等的人，如朋友、同事、兄弟姐妹。你們能量相近，既是夥伴也是競爭者。",
        field_theory="同頻共振場：能量頻率相近，形成平行互動。像兩個同頻的波，會共振也會干涉",
        advice="與人合作時保持獨立，競爭時保持風度。這類關係既是助力也需界限",
        keywords=["朋友", "競爭", "獨立", "平等"]
    ),
    "劫財": TranslationEntry(
        term="劫財", category="十神",
        one_line="會搶你資源的人",
        white_speak="代表會分走你資源的人或事，如競爭者、破財的情況。需要學會保護自己的資源。",
        field_theory="能量爭奪場：同質能量爭奪有限資源，形成消耗性互動。像兩個磁鐵同極相斥",
        advice="學會保護自己的資源，不要輕易借錢或合夥。有劫財的人適合獨立作業",
        keywords=["競爭", "破財", "爭奪", "保護"]
    ),
    "食神": TranslationEntry(
        term="食神", category="十神",
        one_line="你的才華和口福",
        white_speak="代表你天生的才華、創造力、以及享受生活的能力。也代表口福、美食、和悠閒。",
        field_theory="創造輸出場：能量自然向外流動，形成創作和表達。像泉水自然湧出",
        advice="培養你的才華和興趣，享受生活但不要過度懶散。適合創作、美食、藝術相關",
        keywords=["才華", "創作", "口福", "享受"]
    ),
    "傷官": TranslationEntry(
        term="傷官", category="十神",
        one_line="你的叛逆和創新",
        white_speak="代表反叛傳統、追求創新的力量。聰明有才華，但容易得罪人。有強烈的表達慾望。",
        field_theory="突破創新場：能量爆發式輸出，打破既有框架。像火山爆發，破壞與創造並存",
        advice="引導創新能量到正面方向，學會委婉表達。適合創業、藝術、自由職業",
        keywords=["叛逆", "創新", "口才", "聰明"]
    ),
    "偏財": TranslationEntry(
        term="偏財", category="十神",
        one_line="意外之財和人脈",
        white_speak="代表意外的收入、投機的財運、廣泛的人脈。來得快去得也快，需要把握時機。",
        field_theory="機會捕獲場：能量呈現脈衝式進入，需要敏銳捕捉。像閃電，瞬間出現",
        advice="把握機會但不要貪心，偏財來得快去得快。適合業務、投資、社交相關",
        keywords=["意外財", "人脈", "投機", "機會"]
    ),
    "正財": TranslationEntry(
        term="正財", category="十神",
        one_line="穩定的收入和妻子",
        white_speak="代表正當穩定的收入、踏實的理財方式。也代表妻子（對男性而言）和穩定的感情。",
        field_theory="資源積累場：能量緩慢但持續流入，形成穩定積累。像細水長流",
        advice="腳踏實地經營財務，不要急於求成。正財旺的人適合穩定工作、長期投資",
        keywords=["穩定", "收入", "踏實", "理財"]
    ),
    "七殺": TranslationEntry(
        term="七殺", category="十神",
        one_line="壓力也是動力",
        white_speak="代表外來的壓力、挑戰、和權威。雖然帶來壓力，但也能激發你的潛能，讓你成長。",
        field_theory="壓力挑戰場：外部能量形成衝擊，激發內在潛能。像壓力鍋，壓力越大能量越強",
        advice="把壓力轉化為動力，挑戰是成長的機會。適合競爭性強、需要魄力的工作",
        keywords=["壓力", "挑戰", "權威", "成長"]
    ),
    "正官": TranslationEntry(
        term="正官", category="十神",
        one_line="你的事業和規範",
        white_speak="代表正當的工作、社會地位、以及約束你的規範。也代表丈夫（對女性而言）。",
        field_theory="秩序結構場：能量形成規範和框架，帶來穩定但也限制自由。像河道引導水流",
        advice="在規範中發展，利用體制的力量。適合公職、大企業、需要認證的專業",
        keywords=["事業", "規範", "地位", "穩定"]
    ),
    "偏印": TranslationEntry(
        term="偏印", category="十神",
        one_line="偏門的智慧和靈感",
        white_speak="代表非主流的學問、靈感、和意外的貴人。思想獨特，但有時想太多、不切實際。",
        field_theory="靈感接收場：能量以非線性方式進入，帶來突發靈感。像電波接收，時有時無",
        advice="相信直覺但要落實行動，偏門學問可能帶來獨特價值。適合研究、玄學、創意",
        keywords=["靈感", "偏門", "直覺", "獨特"]
    ),
    "正印": TranslationEntry(
        term="正印", category="十神",
        one_line="你的貴人和庇護",
        white_speak="代表母親、貴人、保護你的力量、以及學歷文憑。有正印的人通常有人照顧、有靠山。",
        field_theory="保護庇佑場：能量形成保護層，提供滋養和支持。像大樹遮蔭，給予庇護",
        advice="善用貴人資源，但不要過度依賴。有正印的人適合學術、教育、需要證照的工作",
        keywords=["貴人", "庇護", "學歷", "母親"]
    ),
}

# ---------- 常見神煞 ----------
SHENSHA_DB = {
    "天乙貴人": TranslationEntry(
        term="天乙貴人", category="神煞",
        one_line="最大的貴人星",
        white_speak="命中最強的貴人星，代表一生中會遇到很多貴人相助，逢凶化吉。",
        field_theory="貴人護佑場：形成正向連結的能量網，在關鍵時刻會有援助出現",
        advice="珍惜生命中的貴人，也要成為別人的貴人。多結善緣",
        keywords=["貴人", "化吉", "幫助", "善緣"]
    ),
    "文昌": TranslationEntry(
        term="文昌", category="神煞",
        one_line="考試和學習的幸運星",
        white_speak="代表學業、考試、文書方面的好運。有文昌的人通常讀書考試比較順利。",
        field_theory="智慧增益場：提升學習和記憶的效率，在考試時更容易發揮",
        advice="善用學習優勢，考試前多複習。適合學術、寫作、文職工作",
        keywords=["考試", "學業", "文書", "聰明"]
    ),
    "驛馬": TranslationEntry(
        term="驛馬", category="神煞",
        one_line="奔波和遠行的星",
        white_speak="代表移動、出差、搬遷、遠行。有驛馬的人生活較不安定，但適合外出發展。",
        field_theory="動態位移場：能量傾向外向移動，不適合待在原地",
        advice="適合外派、業務、旅遊相關工作。安定下來反而不順",
        keywords=["移動", "出差", "遠行", "變動"]
    ),
    "桃花": TranslationEntry(
        term="桃花", category="神煞",
        one_line="異性緣和魅力的星",
        white_speak="代表異性緣、魅力、人緣。有桃花的人容易受歡迎，但也要注意感情糾紛。",
        field_theory="人際吸引場：形成對他人的吸引力，尤其是異性",
        advice="善用人緣優勢，但要注意感情界限。適合服務、公關、演藝",
        keywords=["異性緣", "魅力", "人緣", "感情"]
    ),
    "華蓋": TranslationEntry(
        term="華蓋", category="神煞",
        one_line="孤高和藝術的星",
        white_speak="代表孤獨、清高、有藝術或宗教傾向。有華蓋的人內心世界豐富，但較難被理解。",
        field_theory="獨立精神場：能量傾向內在探索，與世俗保持距離",
        advice="接受自己的獨特性，適合藝術、哲學、修行相關",
        keywords=["孤獨", "藝術", "清高", "宗教"]
    ),
    "羊刃": TranslationEntry(
        term="羊刃", category="神煞",
        one_line="剛強和危險的星",
        white_speak="代表性格剛強、有魄力，但也容易衝動、有血光之災。需要特別注意安全。",
        field_theory="剛性衝擊場：能量呈現尖銳衝擊，有破壞性但也有開創性",
        advice="控制脾氣，注意安全。適合需要魄力的工作如軍警、外科",
        keywords=["剛強", "衝動", "魄力", "危險"]
    ),
}


# =============================================================================
# 紫微翻譯資料庫
# =============================================================================

# ---------- 十四主星 ----------
ZIWEI_STAR_DB = {
    "紫微": TranslationEntry(
        term="紫微", category="紫微主星",
        one_line="帝王之星，天生領袖",
        white_speak="命盤的皇帝，代表尊貴、領導力、自尊心。有紫微的人有天生的領袖氣質，但也比較高傲。",
        field_theory="核心主導場：如恆星統御行星，形成向心凝聚的能量結構，自然成為中心",
        advice="發揮領導特質，但要放下身段、傾聽他人。適合管理、決策、高位工作",
        keywords=["領導", "尊貴", "高傲", "決策"]
    ),
    "天機": TranslationEntry(
        term="天機", category="紫微主星",
        one_line="智慧之星，善於謀略",
        white_speak="命盤的軍師，代表智慧、策劃、變化。有天機的人聰明善變，但容易想太多、優柔寡斷。",
        field_theory="策略轉換場：如風之流動，能量靈活變換方向，善於找到最佳路徑",
        advice="相信自己的分析能力，但要果斷行動。適合企劃、顧問、策略相關",
        keywords=["智慧", "謀略", "善變", "分析"]
    ),
    "太陽": TranslationEntry(
        term="太陽", category="紫微主星",
        one_line="光明之星，樂於付出",
        white_speak="命盤的太陽，代表光明、付出、男性長輩。有太陽的人熱情大方，但容易過度消耗自己。",
        field_theory="能量輻射場：如太陽普照萬物，能量主動向外散發，不求回報",
        advice="付出要有界限，照顧好自己才能照顧別人。適合公益、教育、服務",
        keywords=["光明", "付出", "熱情", "消耗"]
    ),
    "武曲": TranslationEntry(
        term="武曲", category="紫微主星",
        one_line="財星，做事果斷",
        white_speak="命盤的財神，代表財富、決斷、剛毅。有武曲的人理財能力強、做事果斷，但可能感情較淡薄。",
        field_theory="財富凝聚場：如金屬收縮，能量向內聚斂，具有強大的資源吸納能力",
        advice="發揮理財專長，但要注意人際關係。適合金融、會計、管理",
        keywords=["財富", "果斷", "剛毅", "理財"]
    ),
    "天同": TranslationEntry(
        term="天同", category="紫微主星",
        one_line="福星，知足常樂",
        white_speak="命盤的福星，代表福氣、享受、溫和。有天同的人心態好、人緣佳，但可能缺乏進取心。",
        field_theory="和諧福澤場：如水之包容，能量柔和流動，自然形成舒適環境",
        advice="保持樂觀心態，但要有目標和行動。適合服務、社工、休閒相關",
        keywords=["福氣", "享受", "溫和", "知足"]
    ),
    "廉貞": TranslationEntry(
        term="廉貞", category="紫微主星",
        one_line="囚星，愛恨分明",
        white_speak="命盤的糾纏星，代表感情、是非、堅持。有廉貞的人感情豐富、有原則，但容易陷入糾紛。",
        field_theory="情感糾纏場：如火之燃燒，能量執著凝聚，難以放下",
        advice="學會放下，不要鑽牛角尖。適合需要堅持的工作如律師、記者",
        keywords=["感情", "是非", "堅持", "糾纏"]
    ),
    "天府": TranslationEntry(
        term="天府", category="紫微主星",
        one_line="財庫之星，穩重可靠",
        white_speak="命盤的財庫，代表穩重、包容、財庫。有天府的人穩健可靠、善於守成，但可能過於保守。",
        field_theory="資源庫藏場：如大地承載，能量穩定儲存，形成可靠的資源池",
        advice="發揮穩健特質，但要適時創新。適合財務、倉儲、管理",
        keywords=["穩重", "財庫", "包容", "保守"]
    ),
    "太陰": TranslationEntry(
        term="太陰", category="紫微主星",
        one_line="財星，溫柔細膩",
        white_speak="命盤的月亮，代表女性、感情、財富。有太陰的人溫柔細膩、有藝術氣質，但可能多愁善感。",
        field_theory="情感滋養場：如月之反射，能量柔性吸納，形成內在的豐富世界",
        advice="發揮細膩和藝術特質，但不要過度情緒化。適合藝術、設計、服務",
        keywords=["溫柔", "感情", "財富", "藝術"]
    ),
    "貪狼": TranslationEntry(
        term="貪狼", category="紫微主星",
        one_line="桃花星，多才多藝",
        white_speak="命盤的桃花星，代表慾望、才藝、魅力。有貪狼的人多才多藝、充滿魅力，但可能貪心不足。",
        field_theory="慾望探索場：如藤蔓攀附，能量多向延伸，不斷追求新鮮事物",
        advice="專注發展一兩項才能，不要見異思遷。適合演藝、業務、創意",
        keywords=["桃花", "才藝", "慾望", "魅力"]
    ),
    "巨門": TranslationEntry(
        term="巨門", category="紫微主星",
        one_line="口舌星，善於分析",
        white_speak="命盤的分析師，代表口才、是非、分析。有巨門的人分析能力強、口才好，但容易多疑、招是非。",
        field_theory="分析解構場：如黑洞吸納，能量質疑穿透，善於發現問題",
        advice="用分析能力解決問題而非製造問題。適合法律、研究、諮詢",
        keywords=["口才", "分析", "是非", "多疑"]
    ),
    "天相": TranslationEntry(
        term="天相", category="紫微主星",
        one_line="印星，善於協調",
        white_speak="命盤的協調者，代表貴人、輔佐、協調。有天相的人人緣好、善於協調，但可能缺乏主見。",
        field_theory="協調服務場：如橋樑溝通，能量輔助連結，促進各方合作",
        advice="發揮協調能力，但要有自己的立場。適合秘書、人資、公關",
        keywords=["協調", "貴人", "輔佐", "人緣"]
    ),
    "天梁": TranslationEntry(
        term="天梁", category="紫微主星",
        one_line="蔭星，正義清高",
        white_speak="命盤的守護者，代表庇護、正義、清高。有天梁的人正義感強、有長輩緣，但可能過於清高。",
        field_theory="保護監察場：如大樹遮蔭，能量庇護覆蓋，守護正義",
        advice="發揮正義感，但不要過於說教。適合公職、醫療、社工",
        keywords=["庇護", "正義", "清高", "監察"]
    ),
    "七殺": TranslationEntry(
        term="七殺", category="紫微主星",
        one_line="將星，有魄力",
        white_speak="命盤的將軍，代表權力、魄力、衝勁。有七殺的人有領導力、敢作敢當，但可能衝動、樹敵。",
        field_theory="征服開拓場：如利劍出鞘，能量衝擊突破，適合開疆拓土",
        advice="把魄力用在正確的地方，控制衝動。適合創業、軍警、業務",
        keywords=["魄力", "權力", "衝勁", "開拓"]
    ),
    "破軍": TranslationEntry(
        term="破軍", category="紫微主星",
        one_line="耗星，喜歡挑戰",
        white_speak="命盤的先鋒，代表變動、破壞、開創。有破軍的人愛冒險、不安於現狀，但可能難以守成。",
        field_theory="革新變動場：如浪潮衝擊，能量破舊立新，適合打破僵局",
        advice="把破壞力轉為創造力，學會適可而止。適合創新、改革、冒險",
        keywords=["變動", "破壞", "開創", "冒險"]
    ),
}

# ---------- 四化 ----------
SIHUA_DB = {
    "化祿": TranslationEntry(
        term="化祿", category="四化",
        one_line="這是你的幸運領域",
        white_speak="這顆星被「加持」了！在它所在的領域會帶來好運、機會和收穫。像是開了綠燈，事情比較順利，資源會自然流向你。",
        field_theory="吸引力場：形成能量入口，自然吸引資源、機會、好運進入此領域。能量向內聚合，越積越多",
        advice="把握這個領域的機會，這是你的「收穫區」。主動出擊會有好結果",
        keywords=["機會", "財富", "順利", "增益"]
    ),
    "化權": TranslationEntry(
        term="化權", category="四化",
        one_line="這是你有話語權的領域",
        white_speak="這顆星拿到「權杖」了！在它代表的領域你會想要主導、想要做主。有企圖心和競爭性，想要證明自己。",
        field_theory="推動力場：形成能量輸出，主動向外擴張影響力。能量向外推進，具有支配性",
        advice="在這個領域可以主動出擊、爭取主導權，但注意不要過於強勢",
        keywords=["權力", "掌控", "主導", "競爭"]
    ),
    "化科": TranslationEntry(
        term="化科", category="四化",
        one_line="這是你容易被肯定的領域",
        white_speak="這顆星有了「光環」！在它代表的領域容易被看見、得到肯定、有貴人幫忙。名聲和學業運都好。",
        field_theory="諧振連結場：與外界產生良性共振，吸引認同和助力。能量形成正面連結，帶來貴人",
        advice="這個領域適合展現自己，會有貴人相助。把握曝光機會",
        keywords=["名聲", "考試", "貴人", "被看見"]
    ),
    "化忌": TranslationEntry(
        term="化忌", category="四化",
        one_line="這是你的功課所在",
        white_speak="這顆星遇到「關卡」了！在它代表的領域你會特別在意、容易卡住、放不下。這是人生需要學習的課題，不是壞事。",
        field_theory="阻滯糾結場：能量在此處循環打結，形成執念。需要學會放下，才能讓能量流通",
        advice="這個領域是你的功課，不要過度執著，學會放下反而會解套",
        keywords=["阻礙", "執著", "糾結", "課題"]
    ),
}

# ---------- 十二宮 ----------
GONG_DB = {
    "命宮": TranslationEntry(
        term="命宮", category="十二宮",
        one_line="你的人設和性格",
        white_speak="代表「你是誰」，是你的性格、外表、氣質的總和。別人第一眼看到你的印象，以及你這一生的基調。",
        field_theory="場的核心：所有能量的出發點和歸宿，定義了你這個「場」的基本屬性",
        advice="認識自己是第一步，接受自己的特質，發揮優勢、修正缺點",
        keywords=["性格", "外貌", "氣質", "人生"]
    ),
    "兄弟宮": TranslationEntry(
        term="兄弟宮", category="十二宮",
        one_line="你的戰友和夥伴",
        white_speak="代表兄弟姐妹、朋友、同事、合作夥伴的關係。也看你和平輩之間的互動模式。",
        field_theory="平行場：與同頻率者的互動模式，能量相近的人如何共處",
        advice="選擇好的夥伴，互相扶持。合作時要有界限",
        keywords=["兄弟", "朋友", "同事", "合作"]
    ),
    "夫妻宮": TranslationEntry(
        term="夫妻宮", category="十二宮",
        one_line="你的另一半",
        white_speak="代表配偶、戀人、以及婚姻狀態。看你理想的對象類型、婚姻品質、感情模式。",
        field_theory="互補場：與最親密者的能量交換，如何在親密關係中互動",
        advice="了解自己需要什麼樣的伴侶，經營關係需要雙方努力",
        keywords=["配偶", "戀人", "婚姻", "感情"]
    ),
    "子女宮": TranslationEntry(
        term="子女宮", category="十二宮",
        one_line="你的作品和創造",
        white_speak="代表子女緣分、和孩子的關係，也代表你的創造力、投資運、以及「你生出來的東西」。",
        field_theory="延續場：向下一代傳遞的能量，以及你創造出來的成果",
        advice="培養創造力，對子女要有耐心。投資要謹慎",
        keywords=["子女", "創造", "投資", "延續"]
    ),
    "財帛宮": TranslationEntry(
        term="財帛宮", category="十二宮",
        one_line="你的錢包",
        white_speak="代表你的賺錢能力、理財方式、對金錢的態度。看你錢從哪裡來、怎麼花、能不能存得住。",
        field_theory="物質場：與金錢資源的吸納和流動方式，能量如何轉化為物質",
        advice="了解自己的財運模式，培養正確的金錢觀",
        keywords=["收入", "理財", "金錢", "消費"]
    ),
    "疾厄宮": TranslationEntry(
        term="疾厄宮", category="十二宮",
        one_line="你的身體",
        white_speak="代表健康狀況、身體弱點、以及可能的疾病傾向。提醒你要注意哪些方面的健康。",
        field_theory="身體場：肉體與能量的平衡狀態，哪裡容易出現失衡",
        advice="預防勝於治療，注意身體警訊，養成好習慣",
        keywords=["健康", "疾病", "身體", "意外"]
    ),
    "遷移宮": TranslationEntry(
        term="遷移宮", category="十二宮",
        one_line="外面的世界",
        white_speak="代表出外運、旅行運、以及在外面的發展。看你適不適合離開家鄉發展、出門順不順利。",
        field_theory="擴展場：向外拓展的能量與機會，離開舒適圈的發展潛力",
        advice="評估外出發展的利弊，把握外在機會",
        keywords=["出外", "旅行", "發展", "貴人"]
    ),
    "交友宮": TranslationEntry(
        term="交友宮", category="十二宮",
        one_line="你的朋友圈",
        white_speak="代表朋友關係、社交能力、以及下屬緣分。看你交的是什麼樣的朋友、社交品質如何。",
        field_theory="社交場：與他人建立連結的模式，人際網絡的特質",
        advice="交友要有選擇，經營人脈但不要勉強",
        keywords=["朋友", "社交", "下屬", "人脈"]
    ),
    "官祿宮": TranslationEntry(
        term="官祿宮", category="十二宮",
        one_line="你的事業",
        white_speak="代表工作運、事業發展、以及社會地位。看你適合什麼職業、事業能做多大。",
        field_theory="成就場：在社會上建立影響力的能量，如何被社會認可",
        advice="選擇適合自己的職業方向，腳踏實地發展",
        keywords=["事業", "工作", "地位", "成就"]
    ),
    "田宅宮": TranslationEntry(
        term="田宅宮", category="十二宮",
        one_line="你的家",
        white_speak="代表不動產運、家庭環境、以及居住狀況。看你買房運如何、家裡環境怎麼樣。",
        field_theory="根基場：安身立命的穩定能量，生活的基礎和根據地",
        advice="穩定是發展的基礎，經營好自己的家",
        keywords=["房產", "家庭", "居住", "根基"]
    ),
    "福德宮": TranslationEntry(
        term="福德宮", category="十二宮",
        one_line="你的內心世界",
        white_speak="代表精神狀態、興趣嗜好、以及內心的滿足感。看你快不快樂、有什麼興趣、精神層面的追求。",
        field_theory="精神場：內在滿足與幸福感的來源，心靈的能量狀態",
        advice="培養興趣愛好，照顧好內心世界",
        keywords=["精神", "興趣", "福報", "快樂"]
    ),
    "父母宮": TranslationEntry(
        term="父母宮", category="十二宮",
        one_line="你的靠山",
        white_speak="代表與父母的關係、長輩緣分、以及來自上方的助力。也看文書運、學歷運。",
        field_theory="傳承場：接收上一代能量的管道，從長輩得到的資源和影響",
        advice="感恩父母，經營長輩關係，善用他們的智慧",
        keywords=["父母", "長輩", "靠山", "文書"]
    ),
}


# =============================================================================
# 奇門翻譯資料庫
# =============================================================================

BAMEN_DB = {
    "開門": TranslationEntry(
        term="開門", category="八門",
        one_line="綠燈門，適合開始",
        white_speak="這是最好的門之一！代表「開」始、「開」創、「開」拓。適合啟動新計劃、出門辦事、追求目標。",
        field_theory="啟動場：能量從靜態轉為動態，突破阻礙開始流動。適合一切開始性質的事務",
        advice="✓適合：創業、出行、求職、談判、開張\n✗不宜：隱藏、等待、守成",
        keywords=["開始", "開創", "出行", "談判"]
    ),
    "休門": TranslationEntry(
        term="休門", category="八門",
        one_line="休息站，適合養精蓄銳",
        white_speak="這是休息的門，代表休養、安靜、恢復。適合見貴人、訪友、養生、低調行事。",
        field_theory="修復場：能量進入休眠恢復狀態，適合養精蓄銳、蓄積力量",
        advice="✓適合：休息、訪友、養生、見領導、求貴人\n✗不宜：激烈競爭、開創冒險",
        keywords=["休息", "養生", "貴人", "恢復"]
    ),
    "生門": TranslationEntry(
        term="生門", category="八門",
        one_line="發財門，適合投資",
        white_speak="這是財門！代表「生」財、「生」發、「生」長。適合投資、做生意、置產、求醫。",
        field_theory="生長場：能量蓬勃向上，資源自然增長。適合一切增長性質的事務",
        advice="✓適合：投資、置產、求財、營商、求醫\n✗不宜：結束、放棄、破壞",
        keywords=["財運", "投資", "生意", "增長"]
    ),
    "傷門": TranslationEntry(
        term="傷門", category="八門",
        one_line="戰鬥門，適合競爭",
        white_speak="這是競爭的門，代表傷害、戰鬥、競爭。適合打官司、討債、維權，但要注意受傷。",
        field_theory="衝突場：能量尖銳外放，具有攻擊性。適合需要攻擊性的事務",
        advice="✓適合：競爭、追債、打官司、維權、手術\n✗不宜：合作、和談、結婚、訪友",
        keywords=["競爭", "戰鬥", "官司", "維權"]
    ),
    "杜門": TranslationEntry(
        term="杜門", category="八門",
        one_line="隱身門，適合低調",
        white_speak="這是隱藏的門，代表堵塞、隱蔽、保密。適合低調行事、躲避是非、暗中準備。",
        field_theory="封閉場：能量向內收縮，與外界隔絕。適合需要隱蔽的事務",
        advice="✓適合：躲避、隱藏、保密、偵查、防守\n✗不宜：出頭、張揚、公開、求財",
        keywords=["隱藏", "低調", "保密", "防守"]
    ),
    "景門": TranslationEntry(
        term="景門", category="八門",
        one_line="舞台門，適合展現",
        white_speak="這是表演的門，代表風景、展示、光明。適合考試、面試、宣傳、表演。",
        field_theory="展示場：能量外顯明亮，適合被看見。適合需要曝光的事務",
        advice="✓適合：考試、面試、宣傳、發表、表演\n✗不宜：隱藏、私密行動、陰謀",
        keywords=["展示", "考試", "宣傳", "表演"]
    ),
    "死門": TranslationEntry(
        term="死門", category="八門",
        one_line="終點門，適合結束",
        white_speak="這是結束的門，代表死亡、終結、了斷。只適合結束舊事，不宜開新局。",
        field_theory="終結場：能量走向消亡，事物進入尾聲。適合了結性質的事務",
        advice="✓適合：弔喪、安葬、結束關係、了斷舊事\n✗不宜：開創、求財、結婚、出行",
        keywords=["結束", "終結", "了斷", "告別"]
    ),
    "驚門": TranslationEntry(
        term="驚門", category="八門",
        one_line="警報門，有意外",
        white_speak="這是驚嚇的門，代表驚恐、意外、警告。容易有意外事件，但也適合震懾對方。",
        field_theory="震盪場：能量不穩定波動，引發驚訝和警覺。需要保持警惕",
        advice="✓適合：警告、談判施壓、審訊、討債\n✗不宜：求和、安靜、開心事",
        keywords=["驚嚇", "意外", "警告", "施壓"]
    ),
}

JIUXING_DB = {
    "天蓬": TranslationEntry(
        term="天蓬", category="九星",
        one_line="盜星，智謀多變",
        white_speak="代表智謀、變化、狡詐。有天蓬的方位適合用計謀，但要小心被騙。",
        field_theory="智謀場：能量多變不定，善於出奇制勝",
        advice="可以用智取勝，但要防小人",
        keywords=["智謀", "變化", "狡詐", "奇謀"]
    ),
    "天芮": TranslationEntry(
        term="天芮", category="九星",
        one_line="病星，注意健康",
        white_speak="代表疾病、困頓、阻礙。這個方位要注意健康問題，做事容易遇阻。",
        field_theory="病滯場：能量受阻不暢，容易出現停滯",
        advice="注意身體健康，做事要有耐心",
        keywords=["疾病", "困頓", "阻礙", "停滯"]
    ),
    "天衝": TranslationEntry(
        term="天衝", category="九星",
        one_line="勇星，衝鋒陷陣",
        white_speak="代表勇猛、衝動、行動力。這個方位適合快速行動，但要小心衝動。",
        field_theory="衝擊場：能量快速爆發，具有突破性",
        advice="把握時機快速行動，但不要魯莽",
        keywords=["勇猛", "衝動", "行動", "突破"]
    ),
    "天輔": TranslationEntry(
        term="天輔", category="九星",
        one_line="文星，利文書考試",
        white_speak="代表文章、學業、文書。這個方位適合讀書、考試、處理文件。",
        field_theory="文昌場：能量傾向思考和學習，利於文事",
        advice="適合靜下心來學習和處理文書",
        keywords=["文書", "學業", "考試", "智慧"]
    ),
    "天禽": TranslationEntry(
        term="天禽", category="九星",
        one_line="中星，統御全局",
        white_speak="代表中央、統御、平衡。這是中宮之星，有統籌全局的能力。",
        field_theory="中樞場：能量居中調和，統御四方",
        advice="把握全局，協調各方",
        keywords=["中央", "統御", "平衡", "全局"]
    ),
    "天心": TranslationEntry(
        term="天心", category="九星",
        one_line="醫星，利求醫治病",
        white_speak="代表醫藥、治療、修復。這個方位適合求醫、養生、修復關係。",
        field_theory="療癒場：能量具有修復性，利於治療",
        advice="適合處理需要修復的事務",
        keywords=["醫藥", "治療", "修復", "養生"]
    ),
    "天柱": TranslationEntry(
        term="天柱", category="九星",
        one_line="隱星，適合隱藏",
        white_speak="代表隱遁、躲藏、防守。這個方位適合低調行事、躲避是非。",
        field_theory="隱蔽場：能量傾向內收，適合躲藏",
        advice="適合低調行事，暗中準備",
        keywords=["隱遁", "躲藏", "防守", "低調"]
    ),
    "天任": TranslationEntry(
        term="天任", category="九星",
        one_line="財星，利求財置產",
        white_speak="代表財富、置產、穩重。這個方位適合投資、買房、求財。",
        field_theory="厚重場：能量穩定積累，利於守財",
        advice="適合長期投資和置產",
        keywords=["財富", "置產", "穩重", "積累"]
    ),
    "天英": TranslationEntry(
        term="天英", category="九星",
        one_line="火星，利文明光彩",
        white_speak="代表光明、文明、才華。這個方位適合展示才華、提升名氣。",
        field_theory="光明場：能量外放明亮，適合展現",
        advice="適合展示自己，爭取曝光",
        keywords=["光明", "文明", "才華", "名氣"]
    ),
}


# =============================================================================
# 六壬翻譯資料庫
# =============================================================================

SHENJIANG_DB = {
    "貴人": TranslationEntry(
        term="貴人", category="十二神將",
        one_line="救星來了",
        white_speak="最大的吉神！代表有貴人出現，能化解危機、帶來轉機。遇到困難會有人幫忙。",
        field_theory="化解場：具有轉化負面能量的特性，能將凶化吉",
        advice="相信會有貴人相助，也要成為別人的貴人",
        keywords=["貴人", "化解", "轉機", "幫助"]
    ),
    "騰蛇": TranslationEntry(
        term="騰蛇", category="十二神將",
        one_line="怪事發生",
        white_speak="代表怪異、虛驚、夢境。事情可能不是表面看起來那樣，有蹊蹺或虛驚一場。",
        field_theory="迷惑場：能量扭曲變形，難以把握真相",
        advice="保持冷靜，不要被表象迷惑，查明真相",
        keywords=["怪異", "虛驚", "夢境", "蹊蹺"]
    ),
    "朱雀": TranslationEntry(
        term="朱雀", category="十二神將",
        one_line="有消息來",
        white_speak="代表口舌、訊息、文書。會有消息傳來，可能是好消息也可能是是非。",
        field_theory="傳訊場：能量通過言語文字傳遞，注意口舌",
        advice="注意言語，管好嘴巴。等待消息時會有音訊",
        keywords=["消息", "口舌", "文書", "傳訊"]
    ),
    "六合": TranslationEntry(
        term="六合", category="十二神將",
        one_line="有人牽線",
        white_speak="代表和合、媒介、交易。會有人從中牽線，促成合作、交易或婚事。",
        field_theory="媒合場：能量促進雙方連結，利於合作",
        advice="把握合作機會，有人願意幫忙牽線",
        keywords=["和合", "媒介", "交易", "婚姻"]
    ),
    "勾陳": TranslationEntry(
        term="勾陳", category="十二神將",
        one_line="糾纏不清",
        white_speak="代表糾纏、訴訟、拖延。事情可能會拖很久、糾纏不清，或有官司訴訟。",
        field_theory="糾纏場：能量互相拉扯，難以脫身",
        advice="有耐心處理，不要急躁。必要時尋求法律幫助",
        keywords=["糾纏", "訴訟", "拖延", "田土"]
    ),
    "青龍": TranslationEntry(
        term="青龍", category="十二神將",
        one_line="喜事臨門",
        white_speak="大吉神！代表喜慶、財運、吉祥。會有好事發生，財運亨通，喜上眉梢。",
        field_theory="祥瑞場：能量積極正向，帶來好運和喜悅",
        advice="把握好運時機，積極行動會有好結果",
        keywords=["喜慶", "財運", "吉祥", "好運"]
    ),
    "太常": TranslationEntry(
        term="太常", category="十二神將",
        one_line="衣食無憂",
        white_speak="代表衣祿、安穩、官職。生活會安穩順遂，衣食無憂，可能有升遷機會。",
        field_theory="穩定場：能量平穩持續，適合守成",
        advice="安心發展，保持現狀會有好結果",
        keywords=["衣祿", "安穩", "官職", "順遂"]
    ),
    "白虎": TranslationEntry(
        term="白虎", category="十二神將",
        one_line="危險信號",
        white_speak="凶神！代表凶煞、疾病、血光。要特別小心安全，注意健康，防範意外。",
        field_theory="凶煞場：能量具有破壞性，需要防範",
        advice="提高警覺，注意安全，做好防護",
        keywords=["凶煞", "疾病", "血光", "意外"]
    ),
    "太陰": TranslationEntry(
        term="太陰", category="十二神將",
        one_line="暗中有人幫",
        white_speak="代表陰私、暗助、女性。會有人在暗中幫忙，或事情在私下解決。",
        field_theory="隱助場：能量在暗處運作，有暗中助力",
        advice="不要聲張，私下解決問題可能更好",
        keywords=["暗助", "陰私", "女性", "私下"]
    ),
    "天后": TranslationEntry(
        term="天后", category="十二神將",
        one_line="與女性有關",
        white_speak="代表女性、感情、陰柔。事情與女性有關，或需要用柔性方式處理。",
        field_theory="陰柔場：能量偏向女性特質，與感情相關",
        advice="留意女性的影響，用柔和方式解決問題",
        keywords=["女性", "感情", "陰柔", "柔和"]
    ),
    "玄武": TranslationEntry(
        term="玄武", category="十二神將",
        one_line="小心被騙",
        white_speak="凶神！代表盜賊、欺騙、失物。要小心被騙被偷，不要輕信他人。",
        field_theory="欺騙場：能量不正當，需防範被騙被盜",
        advice="提高警惕，保管好財物，不要輕信陌生人",
        keywords=["盜賊", "欺騙", "失物", "防騙"]
    ),
    "天空": TranslationEntry(
        term="天空", category="十二神將",
        one_line="可能落空",
        white_speak="代表虛空、落空、欺詐。事情可能落空，承諾可能不實，期望可能失望。",
        field_theory="虛空場：能量無法落實，容易落空",
        advice="不要期望太高，做好落空的準備",
        keywords=["虛空", "落空", "欺詐", "虛假"]
    ),
}


# =============================================================================
# 風水翻譯資料庫
# =============================================================================

JIUYUN_DB = {
    9: TranslationEntry(
        term="九運", category="三元九運",
        one_line="火運當令（2024-2043）",
        white_speak="現在是九運，火的能量最旺。文化創意、科技網路、新媒體、眼睛相關行業興盛。中年女性力量崛起。",
        field_theory="火場主導：光明、傳播、文化的能量佔優勢。能夠「被看見」變得非常重要",
        advice="發展與「被看見」有關的事業：內容創作、自媒體、品牌、設計、科技",
        keywords=["文化", "科技", "中女", "傳播"]
    ),
    8: TranslationEntry(
        term="八運", category="三元九運",
        one_line="土運剛過（2004-2023）",
        white_speak="八運剛結束，那是土的能量最旺的時期。房地產大爆發、年輕男性創業潮是那個時期的特徵。",
        field_theory="土場主導（已過）：穩定、積累、建設的能量，房產和建設蓬勃發展",
        advice="房地產的黃金期已過，要轉向新的方向",
        keywords=["地產", "建築", "少男", "積累"]
    ),
}


# =============================================================================
# 易經翻譯資料庫 (簡化版，64卦)
# =============================================================================

YIJING_GUA_DB = {
    "乾": TranslationEntry(
        term="乾卦", category="易經",
        one_line="天行健，君子自強不息",
        white_speak="全陽卦，代表天、剛健、積極進取。形勢大好，但要注意物極必反，不可過於強勢。",
        field_theory="純陽場：能量達到極盛，具有最大的擴張性和創造性，但需警惕過度",
        advice="積極進取但保持謙遜，事業可大展，但要懂得適可而止",
        keywords=["剛健", "進取", "天", "領導"]
    ),
    "坤": TranslationEntry(
        term="坤卦", category="易經",
        one_line="地勢坤，君子厚德載物",
        white_speak="全陰卦，代表地、柔順、包容。適合配合他人、承載責任，不宜獨斷獨行。",
        field_theory="純陰場：能量呈現承載和包容狀態，適合支持而非主導",
        advice="順勢而為，配合大勢，厚積薄發，不要急於出頭",
        keywords=["柔順", "包容", "地", "配合"]
    ),
    "屯": TranslationEntry(
        term="屯卦", category="易經",
        one_line="萬事起頭難",
        white_speak="代表開始的困難，像種子剛發芽，充滿阻力但也充滿希望。需要耐心和毅力。",
        field_theory="初生場：能量正在萌發，面臨阻力但具有生命力，需要時間成長",
        advice="開始做事會遇到困難，但堅持下去會有成果。需要貴人幫助",
        keywords=["困難", "開始", "堅持", "希望"]
    ),
    "蒙": TranslationEntry(
        term="蒙卦", category="易經",
        one_line="啟蒙教育，循序漸進",
        white_speak="代表蒙昧、學習、需要指導。像小孩需要教育，要虛心學習，找到好老師。",
        field_theory="待啟場：能量處於未開發狀態，需要外力引導才能成長",
        advice="虛心學習，找到好的導師或顧問。不懂就問，循序漸進",
        keywords=["學習", "啟蒙", "指導", "謙虛"]
    ),
}


# =============================================================================
# 統一查詢接口
# =============================================================================

class TranslationDB:
    """
    統一翻譯資料庫
    
    PYLIB First: 一次建立，處處引用
    """
    
    VERSION = "1.0.0"
    
    # 所有資料庫
    DATABASES = {
        "天干": TIANGAN_DB,
        "地支": DIZHI_DB,
        "十神": SHISHEN_DB,
        "神煞": SHENSHA_DB,
        "紫微主星": ZIWEI_STAR_DB,
        "四化": SIHUA_DB,
        "十二宮": GONG_DB,
        "八門": BAMEN_DB,
        "九星": JIUXING_DB,
        "十二神將": SHENJIANG_DB,
        "三元九運": JIUYUN_DB,
        "易經": YIJING_GUA_DB,
    }
    
    @classmethod
    def get(cls, term: str, category: str = None) -> Optional[TranslationEntry]:
        """
        查詢翻譯
        
        Args:
            term: 術語
            category: 類別（可選，不指定則全庫搜索）
        
        Returns:
            TranslationEntry 或 None
        """
        if category:
            db = cls.DATABASES.get(category, {})
            return db.get(term)
        
        # 全庫搜索
        for db in cls.DATABASES.values():
            if term in db:
                return db[term]
        
        return None
    
    @classmethod
    def format(cls, term: str, category: str = None) -> str:
        """格式化輸出"""
        entry = cls.get(term, category)
        if entry:
            return entry.format_output()
        return f"【{term}】未找到翻譯"
    
    @classmethod
    def get_dict(cls, term: str, category: str = None) -> Dict:
        """獲取字典格式"""
        entry = cls.get(term, category)
        if entry:
            return entry.to_dict()
        return {"term": term, "error": "未找到翻譯"}
    
    @classmethod
    def stats(cls) -> Dict:
        """統計資料"""
        total = sum(len(db) for db in cls.DATABASES.values())
        return {
            "categories": len(cls.DATABASES),
            "total_entries": total,
            "breakdown": {k: len(v) for k, v in cls.DATABASES.items()}
        }


# =============================================================================
# CLI 測試
# =============================================================================

def main():
    print("=" * 70)
    print("北斗命數翻譯資料庫 v1.0")
    print("PYLIB First: 一次建立，處處引用")
    print("@11star: 織明 × 澄韻 × 流祇")
    print("=" * 70)
    
    # 統計
    stats = TranslationDB.stats()
    print(f"\n【資料庫統計】")
    print(f"  類別數: {stats['categories']}")
    print(f"  總詞條: {stats['total_entries']}")
    print(f"\n【各類別詞條數】")
    for cat, count in stats['breakdown'].items():
        print(f"  {cat}: {count}")
    
    # 測試查詢
    print("\n" + "=" * 70)
    print("【翻譯測試】")
    print("=" * 70)
    
    tests = [
        ("甲", "天干"),
        ("比肩", "十神"),
        ("紫微", "紫微主星"),
        ("化祿", "四化"),
        ("命宮", "十二宮"),
        ("開門", "八門"),
        ("貴人", "十二神將"),
    ]
    
    for term, cat in tests:
        print(f"\n{TranslationDB.format(term, cat)}")
    
    # 統計行數
    print("\n" + "=" * 70)
    with open(__file__, 'r') as f:
        lines = len(f.read().split('\n'))
    print(f"模組行數: {lines} 行")
    print("=" * 70)


if __name__ == "__main__":
    main()
