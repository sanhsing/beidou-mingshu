#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
mingshu_translation_ext_v1.py - 北斗命數翻譯擴展庫 v1.0
=====================================================
北斗七星文創 × 織明 × 澄韻 × 流祇 × 理樞

XTF⁸ Task Chain: 批次1-4翻譯詞條補充
- 批次1: 紫微輔星(11) + 長生十二宮(12) + 五行(5) = 28條
- 批次2: 奇門八神(8)
- 批次3: 二十四山向(24)
- 批次4: 六十甲子納音(60)
總計: 120條

XTFS 分工:
  X(執行): 數據結構定義
  T(翻譯): 術語→白話
  F(場論): 場態解讀
  S(存儲): PYLIB 統一存儲

@11star: 織明(統籌) × 澄韻(翻譯) × 流祇(場論) × 理樞(整合)

PYLIB First: 一次建立，處處引用

📚 知識點：
    「擴展庫 = 核心庫的補充」
    「120條 = 完整專業解讀的基礎」
"""

from dataclasses import dataclass, asdict
from typing import Dict, List, Optional

@dataclass
class TranslationEntry:
    """翻譯條目"""
    term: str
    category: str
    one_line: str
    white_speak: str
    field_theory: str
    advice: str
    keywords: List[str]
    
    def to_dict(self) -> Dict:
        return asdict(self)
    
    def format_output(self) -> str:
        return f"""【{self.term}】{self.one_line}
✦ 白話：{self.white_speak}
✦ 場論：{self.field_theory}
✦ 建議：{self.advice}"""


# =============================================================================
# 批次1: 紫微輔星 (11條)
# =============================================================================

ZIWEI_FUZHU_DB = {
    "左輔": TranslationEntry(
        term="左輔", category="紫微輔星",
        one_line="左邊的貴人，實質幫助",
        white_speak="代表從左邊來的助力，是實實在在的幫忙。有左輔的人人緣好，做事有人相助，不會孤軍奮戰。",
        field_theory="左輔場：能量從左側匯入，形成實質性的支援。如同左臂右膀，提供具體的協助",
        advice="善用貴人資源，但也要成為別人的貴人。互助才能長久",
        keywords=["貴人", "助力", "人緣", "實質幫助"]
    ),
    "右弼": TranslationEntry(
        term="右弼", category="紫微輔星",
        one_line="右邊的貴人，暗中相助",
        white_speak="代表從右邊來的助力，常常是暗中幫忙。有右弼的人會在不知不覺中得到幫助，貴人運好。",
        field_theory="右弼場：能量從右側匯入，形成隱性的支援。如同幕後推手，默默給予助力",
        advice="珍惜暗中幫助你的人，有時候貴人不在明處",
        keywords=["暗助", "貴人", "機會", "幕後"]
    ),
    "文昌": TranslationEntry(
        term="文昌", category="紫微輔星",
        one_line="正統文星，考試運好",
        white_speak="代表正統學問、考試、文書。有文昌的人讀書考試比較順利，適合走學術或文職路線。",
        field_theory="文昌場：能量傾向理性和邏輯思維，形成學習增益。如同明燈照亮知識的道路",
        advice="善用學習優勢，考試前好好準備會有好成績",
        keywords=["考試", "學業", "文書", "正統"]
    ),
    "文曲": TranslationEntry(
        term="文曲", category="紫微輔星",
        one_line="才藝文星，藝術天分",
        white_speak="代表才藝、藝術、口才。有文曲的人多才多藝，有藝術氣質，口才也好，但可能比較感性。",
        field_theory="文曲場：能量傾向感性和創意表達，形成藝術共振。如同樂器發出美妙的聲音",
        advice="發揮藝術天分，但做決定時也要理性思考",
        keywords=["才藝", "藝術", "口才", "感性"]
    ),
    "祿存": TranslationEntry(
        term="祿存", category="紫微輔星",
        one_line="財庫之星，穩定財源",
        white_speak="代表穩定的財富、俸祿、儲蓄。有祿存的人財運穩定，適合存錢，但可能比較保守小氣。",
        field_theory="祿存場：能量形成穩定的財富積累，如同金庫守護財富。能量向內收斂，利於儲蓄",
        advice="善用理財能力，但不要過於吝嗇，該花的要花",
        keywords=["財庫", "穩定", "儲蓄", "俸祿"]
    ),
    "擎羊": TranslationEntry(
        term="擎羊", category="紫微輔星",
        one_line="刑煞之星，衝動是非",
        white_speak="代表衝動、是非、刑傷。有擎羊的人性格剛烈，容易衝動，要注意血光之災和人際衝突。",
        field_theory="擎羊場：能量呈尖銳衝擊狀態，如同羊角般具有攻擊性。易與他人產生摩擦",
        advice="控制脾氣，三思而後行。注意交通安全和人際關係",
        keywords=["衝動", "是非", "刑傷", "剛烈"]
    ),
    "陀羅": TranslationEntry(
        term="陀羅", category="紫微輔星",
        one_line="糾纏之星，拖延反覆",
        white_speak="代表糾纏、拖延、反覆。有陀羅的人做事容易拖延，事情反反覆覆，放不下過去。",
        field_theory="陀羅場：能量呈螺旋糾纏狀態，如同漩渦般纏繞不清。事情容易反覆",
        advice="學會放下，不要糾結過去。做事要果斷，不要拖延",
        keywords=["糾纏", "拖延", "反覆", "放不下"]
    ),
    "火星": TranslationEntry(
        term="火星", category="紫微輔星",
        one_line="爆發之星，急躁衝動",
        white_speak="代表爆發、急躁、突發。有火星的人性格急躁，做事衝動，但也有爆發力和行動力。",
        field_theory="火星場：能量呈爆發式釋放，如同火焰突然竄起。具有強大但不穩定的動能",
        advice="把急躁轉為行動力，但要注意不要衝動誤事",
        keywords=["爆發", "急躁", "衝動", "行動力"]
    ),
    "鈴星": TranslationEntry(
        term="鈴星", category="紫微輔星",
        one_line="暗火之星，悶燒內傷",
        white_speak="代表悶燒、內傷、暗中的火氣。有鈴星的人外表可能平靜，但內心壓力大，容易悶出病來。",
        field_theory="鈴星場：能量在內部悶燒，如同暗火慢慢燃燒。表面平靜內心波動",
        advice="學會釋放壓力，不要什麼都悶在心裡。適度表達情緒",
        keywords=["悶燒", "內傷", "壓力", "暗火"]
    ),
    "地空": TranslationEntry(
        term="地空", category="紫微輔星",
        one_line="空亡之星，想法超脫",
        white_speak="代表空虛、超脫、不切實際。有地空的人想法天馬行空，不拘泥於現實，但可能不夠踏實。",
        field_theory="地空場：能量形成虛空狀態，如同黑洞般吸納物質。思想超脫但可能落空",
        advice="把創意落實為行動，空想不如實做",
        keywords=["空亡", "超脫", "創意", "不實際"]
    ),
    "地劫": TranslationEntry(
        term="地劫", category="紫微輔星",
        one_line="劫數之星，破財變動",
        white_speak="代表劫數、破財、變動。有地劫的人容易遇到突然的變故，財來財去，人生起伏較大。",
        field_theory="地劫場：能量形成劫奪狀態，如同強盜搶劫。財富和穩定容易被突然打破",
        advice="做好風險準備，不要把雞蛋放在同一個籃子",
        keywords=["劫數", "破財", "變動", "起伏"]
    ),
}


# =============================================================================
# 批次1: 長生十二宮 (12條)
# =============================================================================

CHANGSHENG_DB = {
    "長生": TranslationEntry(
        term="長生", category="長生十二宮",
        one_line="生命開始，充滿活力",
        white_speak="代表生命的開始，像嬰兒剛出生。充滿活力和希望，事情正在萌芽，有無限可能。",
        field_theory="初生場：能量剛開始湧現，充滿生機和潛力。如同春天萬物萌發",
        advice="把握新的開始，培養新事物需要耐心",
        keywords=["開始", "活力", "希望", "萌芽"]
    ),
    "沐浴": TranslationEntry(
        term="沐浴", category="長生十二宮",
        one_line="洗滌成長，桃花旺盛",
        white_speak="代表洗滌、成長、也代表桃花。像小孩洗澡，脫去舊衣。這個階段異性緣好，但也容易惹是非。",
        field_theory="洗滌場：能量在淨化和轉變中，不穩定但有魅力。如同脫胎換骨的過程",
        advice="注意感情分寸，桃花雖好也要守住底線",
        keywords=["桃花", "成長", "洗滌", "魅力"]
    ),
    "冠帶": TranslationEntry(
        term="冠帶", category="長生十二宮",
        one_line="成年禮成，開始獨立",
        white_speak="代表成年、獨立、開始承擔責任。像古人行冠禮，正式成為大人。可以開始獨當一面了。",
        field_theory="成熟場：能量開始穩定成形，具備獨立運作的能力。如同花蕾即將綻放",
        advice="承擔責任，開始獨立做事。但經驗還不足，要虛心學習",
        keywords=["成年", "獨立", "責任", "成熟"]
    ),
    "臨官": TranslationEntry(
        term="臨官", category="長生十二宮",
        one_line="步入社會，事業起步",
        white_speak="代表出仕、工作、事業起步。像古人當官上任，正式進入社會。事業開始有起色。",
        field_theory="上升場：能量穩步向上提升，開始建立社會影響力。如同日出東方",
        advice="把握事業機會，這是發展的好時機",
        keywords=["事業", "工作", "上升", "機會"]
    ),
    "帝旺": TranslationEntry(
        term="帝旺", category="長生十二宮",
        one_line="登峰造極，最強盛期",
        white_speak="代表最旺盛、最強大、人生巔峰。像皇帝一樣威風，但物極必反，盛極則衰。",
        field_theory="極盛場：能量達到頂峰，具有最大的影響力。如同正午太陽，但也預示下坡",
        advice="享受成功但要居安思危。巔峰之後是下坡，提前準備",
        keywords=["巔峰", "強盛", "成功", "居安思危"]
    ),
    "衰": TranslationEntry(
        term="衰", category="長生十二宮",
        one_line="由盛轉衰，精力下降",
        white_speak="代表開始衰退、精力下降、走下坡。像人過了壯年，體力開始不如從前。需要調整步伐。",
        field_theory="衰退場：能量開始下降，需要調整節奏。如同秋天落葉，自然規律",
        advice="調整步伐，不要硬撐。保養身體，準備轉型",
        keywords=["衰退", "下降", "調整", "保養"]
    ),
    "病": TranslationEntry(
        term="病", category="長生十二宮",
        one_line="身體欠安，需要休養",
        white_speak="代表生病、虛弱、需要休息。像人生了病，需要調養。這個階段要注意健康，少做大事。",
        field_theory="虛弱場：能量處於低迷狀態，需要補充和恢復。如同電池沒電需要充電",
        advice="注意身體健康，該休息就休息。不要強求",
        keywords=["疾病", "虛弱", "休養", "健康"]
    ),
    "死": TranslationEntry(
        term="死", category="長生十二宮",
        one_line="能量停滯，舊事終結",
        white_speak="代表停止、終結、舊事結束。不是真的死亡，而是某個階段的結束。結束才有新的開始。",
        field_theory="終止場：能量停止流動，舊的循環結束。如同冬天萬物收藏，等待新生",
        advice="接受結束，不要強求延續。結束是為了更好的開始",
        keywords=["終結", "停止", "結束", "轉化"]
    ),
    "墓": TranslationEntry(
        term="墓", category="長生十二宮",
        one_line="收藏入庫，保存實力",
        white_speak="代表收藏、入庫、保存。像把東西收進倉庫，暫時不用但保存著。適合積累和收藏。",
        field_theory="收藏場：能量被收納儲存，處於潛伏狀態。如同種子埋入土中等待發芽",
        advice="適合存錢、收藏、積累資源。時機未到，先保存實力",
        keywords=["收藏", "入庫", "保存", "積累"]
    ),
    "絕": TranslationEntry(
        term="絕", category="長生十二宮",
        one_line="能量斷絕，最低谷期",
        white_speak="代表斷絕、最低點、什麼都沒有。像能量完全耗盡，但絕處逢生，最低點之後就是回升。",
        field_theory="空無場：能量降到最低點，幾乎為零。如同黎明前最黑暗的時刻",
        advice="最低谷就是轉折點。堅持住，否極泰來",
        keywords=["斷絕", "低谷", "轉折", "希望"]
    ),
    "胎": TranslationEntry(
        term="胎", category="長生十二宮",
        one_line="孕育萌芽，新生命起",
        white_speak="代表懷孕、孕育、新事物萌芽。像胎兒在母體中孕育，新的生命正在形成。",
        field_theory="孕育場：新的能量正在醞釀形成，尚未顯現但已存在。如同懷孕初期",
        advice="培養新計劃，但不要急於公開。讓它安靜成長",
        keywords=["孕育", "萌芽", "新生", "醞釀"]
    ),
    "養": TranslationEntry(
        term="養", category="長生十二宮",
        one_line="滋養成長，等待時機",
        white_speak="代表滋養、培養、等待出生。像胎兒即將出生，正在做最後的準備。再等一下就好了。",
        field_theory="滋養場：能量在被動補充中，即將完成準備。如同破曉前的等待",
        advice="耐心等待，時機快到了。做好最後的準備",
        keywords=["滋養", "培養", "等待", "準備"]
    ),
}


# =============================================================================
# 批次1: 五行詳解 (5條)
# =============================================================================

WUXING_DB = {
    "金": TranslationEntry(
        term="金", category="五行",
        one_line="肅殺收斂，果斷剛毅",
        white_speak="金代表收斂、肅殺、果斷。像金屬一樣堅硬有型，具有決斷力和執行力，但也可能過於剛硬。",
        field_theory="金場：能量收斂凝聚，形成堅硬的結構。具有切割和決斷的特性，秋天屬金主收穫",
        advice="發揮果斷特質，但要學會柔和。過剛則折",
        keywords=["收斂", "果斷", "剛毅", "決斷"]
    ),
    "木": TranslationEntry(
        term="木", category="五行",
        one_line="生發向上，仁慈包容",
        white_speak="木代表生長、向上、仁慈。像樹木一樣向上生長，具有生命力和包容心，但也可能過於理想化。",
        field_theory="木場：能量向上生發擴展，形成生長的動力。具有創造和包容的特性，春天屬木主生發",
        advice="發揮創造力和包容心，但要腳踏實地",
        keywords=["生發", "向上", "仁慈", "創造"]
    ),
    "水": TranslationEntry(
        term="水", category="五行",
        one_line="流動變通，智慧靈活",
        white_speak="水代表流動、變通、智慧。像水一樣隨方就圓，具有靈活性和適應力，但也可能過於善變。",
        field_theory="水場：能量向下流動滲透，形成柔和的力量。具有智慧和變通的特性，冬天屬水主收藏",
        advice="發揮靈活變通的能力，但要有原則和底線",
        keywords=["流動", "智慧", "變通", "靈活"]
    ),
    "火": TranslationEntry(
        term="火", category="五行",
        one_line="炎上光明，熱情禮義",
        white_speak="火代表炎上、光明、熱情。像火焰一樣向上燃燒，具有熱情和感染力，但也可能過於急躁。",
        field_theory="火場：能量向上升騰擴散，形成光明和溫暖。具有熱情和表達的特性，夏天屬火主成長",
        advice="發揮熱情和感染力，但要注意保存精力",
        keywords=["光明", "熱情", "向上", "表達"]
    ),
    "土": TranslationEntry(
        term="土", category="五行",
        one_line="承載包容，穩重誠信",
        white_speak="土代表承載、包容、穩重。像大地一樣承載萬物，具有穩定性和可靠性，但也可能過於保守。",
        field_theory="土場：能量居中承載轉化，形成穩定的基礎。具有包容和轉化的特性，四季之交屬土主轉換",
        advice="發揮穩定可靠的特質，但也要適時變通",
        keywords=["承載", "穩重", "包容", "誠信"]
    ),
}


# =============================================================================
# 批次2: 奇門八神 (8條)
# =============================================================================

QIMEN_BASHEN_DB = {
    "值符": TranslationEntry(
        term="值符", category="奇門八神",
        one_line="天乙貴人，最大吉神",
        white_speak="值符是奇門中最大的吉神，代表貴人、領導、權威。得值符相助，事情順利，有貴人扶持。",
        field_theory="貴人場：能量呈現最高級別的吉利狀態，如同得到天神庇佑。一切障礙可化解",
        advice="把握貴人機會，有值符的方位和時間最吉",
        keywords=["貴人", "吉利", "權威", "順利"]
    ),
    "騰蛇": TranslationEntry(
        term="騰蛇", category="奇門八神",
        one_line="虛驚怪異，夢境幻象",
        white_speak="騰蛇代表怪異、虛驚、夢境。事情可能不是表面看起來那樣，有蹊蹺或虛驚一場。",
        field_theory="幻象場：能量呈現扭曲和迷惑狀態，真假難辨。如同鏡花水月",
        advice="保持清醒，不要被表象迷惑。查明真相再行動",
        keywords=["怪異", "虛驚", "夢境", "幻象"]
    ),
    "太陰": TranslationEntry(
        term="太陰", category="奇門八神",
        one_line="暗中幫助，陰私之事",
        white_speak="太陰代表暗中、陰私、女性。有人在暗中幫忙，或事情在私下進行。也代表女性的力量。",
        field_theory="隱秘場：能量在暗處運作，不顯山露水。如同月光照耀，柔和而隱秘",
        advice="善用私下溝通，有些事不需要公開。女性貴人可能幫上忙",
        keywords=["暗助", "陰私", "女性", "隱秘"]
    ),
    "六合": TranslationEntry(
        term="六合", category="奇門八神",
        one_line="和合媒介，促成合作",
        white_speak="六合代表和合、媒介、婚姻。適合談合作、做媒、促成交易。人際關係和諧。",
        field_theory="和合場：能量促進雙方連結，形成合作的橋樑。如同紅娘牽線",
        advice="適合談合作、相親、簽約。有六合的日子適合社交",
        keywords=["和合", "合作", "媒介", "婚姻"]
    ),
    "白虎": TranslationEntry(
        term="白虎", category="奇門八神",
        one_line="凶煞血光，剛猛危險",
        white_speak="白虎代表凶煞、血光、疾病。要注意安全，防範意外。但也代表威嚴和武力。",
        field_theory="凶煞場：能量具有強大的破壞性和攻擊性。如同猛虎下山，威力巨大但危險",
        advice="注意安全，避免衝突。需要威懾力時可以借用",
        keywords=["凶煞", "血光", "危險", "威嚴"]
    ),
    "玄武": TranslationEntry(
        term="玄武", category="奇門八神",
        one_line="盜賊欺詐，小心被騙",
        white_speak="玄武代表盜賊、欺詐、暗昧。要小心被騙被偷，不要輕信他人。也代表隱秘的智慧。",
        field_theory="欺詐場：能量呈現不正當的流動，真假難辨。如同暗夜行動的盜賊",
        advice="提高警覺，保管好財物。做事要透明，不要走旁門左道",
        keywords=["盜賊", "欺詐", "暗昧", "防範"]
    ),
    "九地": TranslationEntry(
        term="九地", category="奇門八神",
        one_line="藏形隱匿，守靜待時",
        white_speak="九地代表隱藏、潛伏、守靜。適合低調行事，不宜張揚。養精蓄銳，等待時機。",
        field_theory="潛藏場：能量向下收縮，處於隱蔽狀態。如同潛龍在淵，蓄勢待發",
        advice="低調潛伏，不要出頭。暗中準備，等待時機",
        keywords=["隱藏", "潛伏", "守靜", "蓄勢"]
    ),
    "九天": TranslationEntry(
        term="九天", category="奇門八神",
        one_line="高揚遠舉，積極進取",
        white_speak="九天代表高揚、進取、遠行。適合出擊、行動、追求高遠目標。放手去做，展翅高飛。",
        field_theory="飛揚場：能量向上升騰，具有強大的上升力。如同鷹擊長空，志在千里",
        advice="積極進取，大膽行動。適合出遠門、爭取大目標",
        keywords=["高揚", "進取", "遠行", "行動"]
    ),
}


# =============================================================================
# 批次3: 二十四山向 (24條)
# =============================================================================

ERSHISI_SHAN_DB = {
    "子": TranslationEntry(
        term="子山", category="二十四山",
        one_line="正北方位，坎水之位",
        white_speak="子山位於正北，屬水，代表智慧、事業、中男。坐子向午的房子，適合講究門面的行業。",
        field_theory="坎水場：能量深沉內斂，具有智慧和藏納的特性。利於思考和積累",
        advice="適合從事需要智慧和耐心的工作",
        keywords=["正北", "智慧", "水", "事業"]
    ),
    "癸": TranslationEntry(
        term="癸山", category="二十四山",
        one_line="北偏東位，天乙貴人",
        white_speak="癸山位於北偏東，屬水，帶天乙貴人氣。坐癸向丁的房子，有貴人運，利於仕途。",
        field_theory="癸水場：能量陰柔滋潤，具有貴人和智慧的特性。利於文昌和考試",
        advice="適合讀書、考試、求貴人",
        keywords=["北偏東", "貴人", "文昌", "水"]
    ),
    "丑": TranslationEntry(
        term="丑山", category="二十四山",
        one_line="東北偏北，艮土之位",
        white_speak="丑山位於東北偏北，屬土，穩重踏實。坐丑向未的房子，適合守成和積累財富。",
        field_theory="丑土場：能量濕寒凝聚，具有儲藏和積累的特性。利於守財",
        advice="適合穩健經營，不宜冒進",
        keywords=["東北偏北", "穩重", "土", "守成"]
    ),
    "艮": TranslationEntry(
        term="艮山", category="二十四山",
        one_line="正東北位，少男之位",
        white_speak="艮山位於正東北，屬土，代表少男、止息、山。坐艮向坤的房子，利於男孩和穩定。",
        field_theory="艮土場：能量靜止穩定，具有止息和轉化的特性。八運(2004-2023)當旺",
        advice="適合需要穩定和專注的事業",
        keywords=["正東北", "少男", "止息", "穩定"]
    ),
    "寅": TranslationEntry(
        term="寅山", category="二十四山",
        one_line="東北偏東，生門之位",
        white_speak="寅山位於東北偏東，屬木，帶生門氣。坐寅向申的房子，適合新創事業和求財。",
        field_theory="寅木場：能量生發向上，具有開創和生長的特性。利於創業",
        advice="適合開創新事業，把握生機",
        keywords=["東北偏東", "生門", "木", "創業"]
    ),
    "甲": TranslationEntry(
        term="甲山", category="二十四山",
        one_line="東偏北位，青龍之首",
        white_speak="甲山位於東偏北，屬木，為青龍之首。坐甲向庚的房子，利於開創和領導。",
        field_theory="甲木場：能量剛健向上，具有開創和領導的特性。利於事業開拓",
        advice="適合開創型事業和領導崗位",
        keywords=["東偏北", "青龍", "木", "開創"]
    ),
    "卯": TranslationEntry(
        term="卯山", category="二十四山",
        one_line="正東方位，震木之位",
        white_speak="卯山位於正東，屬木，代表長男、動能、雷。坐卯向酉的房子，利於行動和發展。",
        field_theory="震木場：能量蓬勃活躍，具有動能和擴展的特性。利於積極進取",
        advice="適合需要行動力的事業",
        keywords=["正東", "震", "木", "行動"]
    ),
    "乙": TranslationEntry(
        term="乙山", category="二十四山",
        one_line="東偏南位，青龍之尾",
        white_speak="乙山位於東偏南，屬木，為青龍之尾。坐乙向辛的房子，利於延續和發展。",
        field_theory="乙木場：能量柔和延展，具有延續和適應的特性。利於守成發展",
        advice="適合延續既有事業，穩中求進",
        keywords=["東偏南", "延續", "木", "發展"]
    ),
    "辰": TranslationEntry(
        term="辰山", category="二十四山",
        one_line="東南偏東，天罡之位",
        white_speak="辰山位於東南偏東，屬土，為天罡位。坐辰向戌的房子，具有庫藏和積累的功能。",
        field_theory="辰土場：能量濕潤儲藏，具有庫藏和轉化的特性。利於積累財富",
        advice="適合需要積累和儲存的行業",
        keywords=["東南偏東", "天罡", "土", "庫藏"]
    ),
    "巽": TranslationEntry(
        term="巽山", category="二十四山",
        one_line="正東南位，長女之位",
        white_speak="巽山位於正東南，屬木，代表長女、進入、風。坐巽向乾的房子，利於人際和商業。",
        field_theory="巽木場：能量柔和滲透，具有進入和交流的特性。利於社交商業",
        advice="適合需要人際交流的事業",
        keywords=["正東南", "長女", "風", "交流"]
    ),
    "巳": TranslationEntry(
        term="巳山", category="二十四山",
        one_line="東南偏南，天財之位",
        white_speak="巳山位於東南偏南，屬火，帶天財氣。坐巳向亥的房子，利於求財和文昌。",
        field_theory="巳火場：能量升騰明亮，具有財祿和文昌的特性。利於求財考試",
        advice="適合求財和提升學業",
        keywords=["東南偏南", "天財", "火", "財祿"]
    ),
    "丙": TranslationEntry(
        term="丙山", category="二十四山",
        one_line="南偏東位，天乙文昌",
        white_speak="丙山位於南偏東，屬火，帶文昌氣。坐丙向壬的房子，利於考試和名聲。",
        field_theory="丙火場：能量光明輝煌，具有文昌和名氣的特性。九運(2024-2043)當旺",
        advice="適合需要名聲和展示的事業",
        keywords=["南偏東", "文昌", "火", "名聲"]
    ),
    "午": TranslationEntry(
        term="午山", category="二十四山",
        one_line="正南方位，離火之位",
        white_speak="午山位於正南，屬火，代表中女、光明、離。坐午向子的房子，九運大旺。",
        field_theory="離火場：能量光明炎上，具有文明和表達的特性。九運(2024-2043)最旺方位",
        advice="九運期間，南方大利。適合文化和科技行業",
        keywords=["正南", "光明", "火", "九運"]
    ),
    "丁": TranslationEntry(
        term="丁山", category="二十四山",
        one_line="南偏西位，天官之位",
        white_speak="丁山位於南偏西，屬火，帶官祿氣。坐丁向癸的房子，利於仕途和官運。",
        field_theory="丁火場：能量溫和凝聚，具有官祿和智慧的特性。利於仕途",
        advice="適合從政或在體制內發展",
        keywords=["南偏西", "官祿", "火", "仕途"]
    ),
    "未": TranslationEntry(
        term="未山", category="二十四山",
        one_line="西南偏南，坤土之位",
        white_speak="未山位於西南偏南，屬土，帶母德氣。坐未向丑的房子，利於女性和服務業。",
        field_theory="未土場：能量溫和滋養，具有母德和包容的特性。利於女性事業",
        advice="適合女性領導和服務行業",
        keywords=["西南偏南", "母德", "土", "服務"]
    ),
    "坤": TranslationEntry(
        term="坤山", category="二十四山",
        one_line="正西南位，老母之位",
        white_speak="坤山位於正西南，屬土，代表老母、順承、地。坐坤向艮的房子，利於穩定和配合。",
        field_theory="坤土場：能量柔順承載，具有包容和配合的特性。利於配合發展",
        advice="適合配合他人，順勢而為",
        keywords=["正西南", "老母", "土", "配合"]
    ),
    "申": TranslationEntry(
        term="申山", category="二十四山",
        one_line="西南偏西，白虎之首",
        white_speak="申山位於西南偏西，屬金，為白虎之首。坐申向寅的房子，具有肅殺和革新的能量。",
        field_theory="申金場：能量肅殺收斂，具有變革和執行的特性。利於改革創新",
        advice="適合需要魄力和變革的事業",
        keywords=["西南偏西", "白虎", "金", "變革"]
    ),
    "庚": TranslationEntry(
        term="庚山", category="二十四山",
        one_line="西偏南位，白虎之位",
        white_speak="庚山位於西偏南，屬金，為白虎位。坐庚向甲的房子，帶刑克氣，需要化解。",
        field_theory="庚金場：能量剛烈肅殺，具有刑克和決斷的特性。需要適當化解",
        advice="注意化解煞氣，適合軍警法律行業",
        keywords=["西偏南", "刑克", "金", "決斷"]
    ),
    "酉": TranslationEntry(
        term="酉山", category="二十四山",
        one_line="正西方位，兌金之位",
        white_speak="酉山位於正西，屬金，代表少女、口舌、澤。坐酉向卯的房子，七運(1984-2003)曾旺。",
        field_theory="兌金場：能量精緻表達，具有口才和愉悅的特性。利於表達和演藝",
        advice="適合需要口才和表達的事業",
        keywords=["正西", "少女", "金", "口舌"]
    ),
    "辛": TranslationEntry(
        term="辛山", category="二十四山",
        one_line="西偏北位，白虎之尾",
        white_speak="辛山位於西偏北，屬金，為白虎之尾。坐辛向乙的房子，利於收成和精緻行業。",
        field_theory="辛金場：能量精煉收斂，具有收成和精緻的特性。利於收獲",
        advice="適合收成階段和精緻行業",
        keywords=["西偏北", "收斂", "金", "精緻"]
    ),
    "戌": TranslationEntry(
        term="戌山", category="二十四山",
        one_line="西北偏西，天門之位",
        white_speak="戌山位於西北偏西，屬土，為天門位。坐戌向辰的房子，利於祈福和宗教。",
        field_theory="戌土場：能量乾燥收藏，具有天門和庫藏的特性。利於靈性發展",
        advice="適合宗教、哲學、靈性相關事業",
        keywords=["西北偏西", "天門", "土", "靈性"]
    ),
    "乾": TranslationEntry(
        term="乾山", category="二十四山",
        one_line="正西北位，老父之位",
        white_speak="乾山位於正西北，屬金，代表老父、剛健、天。坐乾向巽的房子，利於領導和決策。",
        field_theory="乾金場：能量剛健有力，具有領導和決策的特性。利於統帥全局",
        advice="適合領導崗位和決策工作",
        keywords=["正西北", "老父", "金", "領導"]
    ),
    "亥": TranslationEntry(
        term="亥山", category="二十四山",
        one_line="西北偏北，玄機之位",
        white_speak="亥山位於西北偏北，屬水，帶玄機氣。坐亥向巳的房子，利於謀略和玄學。",
        field_theory="亥水場：能量深沉玄妙，具有智慧和玄機的特性。利於謀略策劃",
        advice="適合需要謀略和策劃的工作",
        keywords=["西北偏北", "玄機", "水", "謀略"]
    ),
    "壬": TranslationEntry(
        term="壬山", category="二十四山",
        one_line="北偏西位，玄武之位",
        white_speak="壬山位於北偏西，屬水，為玄武位。坐壬向丙的房子，利於智慧和思考。",
        field_theory="壬水場：能量流動智慧，具有思考和變通的特性。利於智力工作",
        advice="適合需要智慧和思考的事業",
        keywords=["北偏西", "玄武", "水", "智慧"]
    ),
}


# =============================================================================
# 批次4: 六十甲子納音 (60條)
# =============================================================================

JIAZI_NAYIN_DB = {
    "甲子": TranslationEntry(
        term="甲子", category="六十甲子",
        one_line="海中金，深藏不露",
        white_speak="甲子納音為海中金，金藏在海底，深藏不露。代表內斂有才華，但不輕易表現。",
        field_theory="海中金場：能量深藏於無形之中，具有潛力但尚未顯現。如珍珠在蚌，待時而出",
        advice="培養實力，不急於表現。時機到了自然發光",
        keywords=["海中金", "深藏", "內斂", "潛力"]
    ),
    "乙丑": TranslationEntry(
        term="乙丑", category="六十甲子",
        one_line="海中金，蓄勢待發",
        white_speak="乙丑納音為海中金，與甲子同屬。金在海中慢慢成形，需要時間和機會才能出頭。",
        field_theory="海中金場：能量在隱蔽處積累，等待突破的機會。厚積薄發",
        advice="耐心等待，持續積累。機會來了要把握",
        keywords=["海中金", "蓄勢", "等待", "機會"]
    ),
    "丙寅": TranslationEntry(
        term="丙寅", category="六十甲子",
        one_line="爐中火，熱情奔放",
        white_speak="丙寅納音為爐中火，火在爐中燃燒，熱情且有控制。代表有熱情但不失理智。",
        field_theory="爐中火場：能量在容器中燃燒，具有熱情但有節制。如同鍊鐵之火",
        advice="發揮熱情，但要有節制。不要燒過頭",
        keywords=["爐中火", "熱情", "節制", "燃燒"]
    ),
    "丁卯": TranslationEntry(
        term="丁卯", category="六十甲子",
        one_line="爐中火，溫暖持久",
        white_speak="丁卯納音為爐中火，與丙寅同屬。火力溫和持久，不會猛烈但能持續發熱。",
        field_theory="爐中火場：能量溫和持續輸出，具有恆久的熱力。如同家中爐火",
        advice="持續付出，不求速成。溫暖的堅持最有力量",
        keywords=["爐中火", "溫暖", "持久", "穩定"]
    ),
    "戊辰": TranslationEntry(
        term="戊辰", category="六十甲子",
        one_line="大林木，成材大器",
        white_speak="戊辰納音為大林木，森林中的大樹，已經成材。代表有實力有根基，可以獨當一面。",
        field_theory="大林木場：能量蓬勃壯大，已經形成規模。如同森林中的參天大樹",
        advice="發揮你的實力，可以承擔大任",
        keywords=["大林木", "成材", "實力", "大器"]
    ),
    "己巳": TranslationEntry(
        term="己巳", category="六十甲子",
        one_line="大林木，根深葉茂",
        white_speak="己巳納音為大林木，與戊辰同屬。根深葉茂，穩定成長。代表基礎穩固，持續發展。",
        field_theory="大林木場：能量根基穩固，持續向上生長。如同百年老樹",
        advice="穩紮穩打，根基要打好。不求快但求穩",
        keywords=["大林木", "根深", "穩固", "成長"]
    ),
    "庚午": TranslationEntry(
        term="庚午", category="六十甲子",
        one_line="路旁土，任人踐踏",
        white_speak="庚午納音為路旁土，路邊的土被人踩踏。代表默默付出，不求回報。要學會保護自己。",
        field_theory="路旁土場：能量被外界消耗和利用，承受壓力。如同道路承載行人",
        advice="付出要有限度，也要學會保護自己",
        keywords=["路旁土", "付出", "承受", "保護"]
    ),
    "辛未": TranslationEntry(
        term="辛未", category="六十甲子",
        one_line="路旁土，滋養萬物",
        white_speak="辛未納音為路旁土，與庚午同屬。雖在路旁但能滋養兩邊的植物，有服務精神。",
        field_theory="路旁土場：能量在平凡中發揮滋養作用，服務大眾。如同道路兩旁的花草",
        advice="在平凡崗位做不平凡的事，服務精神可貴",
        keywords=["路旁土", "滋養", "服務", "平凡"]
    ),
    "壬申": TranslationEntry(
        term="壬申", category="六十甲子",
        one_line="劍鋒金，鋒利無比",
        white_speak="壬申納音為劍鋒金，劍的鋒刃，極其鋒利。代表能力出眾，但也容易傷人傷己。",
        field_theory="劍鋒金場：能量極度銳利，具有強大的切割力。如同寶劍出鞘",
        advice="收斂鋒芒，能力要用在正途。過於銳利會傷人",
        keywords=["劍鋒金", "鋒利", "能力", "收斂"]
    ),
    "癸酉": TranslationEntry(
        term="癸酉", category="六十甲子",
        one_line="劍鋒金，削鐵如泥",
        white_speak="癸酉納音為劍鋒金，與壬申同屬。是最鋒利的金，什麼都能切開。能力極強但要謹慎使用。",
        field_theory="劍鋒金場：能量達到金的極致狀態，銳不可當。如同神兵利器",
        advice="能力越大責任越大，用在正途才有意義",
        keywords=["劍鋒金", "極致", "能力", "責任"]
    ),
    "甲戌": TranslationEntry(
        term="甲戌", category="六十甲子",
        one_line="山頭火，光照四方",
        white_speak="甲戌納音為山頭火，山頂的火光，照耀四方。代表有名望，容易被看見。",
        field_theory="山頭火場：能量高高在上，光芒外顯。如同烽火台上的火光",
        advice="善用你的影響力，高處不勝寒也要注意",
        keywords=["山頭火", "名望", "高處", "影響力"]
    ),
    "乙亥": TranslationEntry(
        term="乙亥", category="六十甲子",
        one_line="山頭火，照亮黑暗",
        white_speak="乙亥納音為山頭火，與甲戌同屬。在高處照亮黑暗中的人，有指引作用。",
        field_theory="山頭火場：能量從高處散發，為迷途者指引方向。如同燈塔",
        advice="發揮引領作用，幫助他人找到方向",
        keywords=["山頭火", "指引", "照亮", "引領"]
    ),
    "丙子": TranslationEntry(
        term="丙子", category="六十甲子",
        one_line="澗下水，清澈見底",
        white_speak="丙子納音為澗下水，山澗下的清水，清澈純淨。代表心思單純，沒有雜念。",
        field_theory="澗下水場：能量清澈純淨，沒有雜質。如同山泉水",
        advice="保持純淨的心，不要被世俗污染",
        keywords=["澗下水", "清澈", "純淨", "單純"]
    ),
    "丁丑": TranslationEntry(
        term="丁丑", category="六十甲子",
        one_line="澗下水，源源不絕",
        white_speak="丁丑納音為澗下水，與丙子同屬。從山間源源流出，取之不盡。代表資源充沛。",
        field_theory="澗下水場：能量持續從源頭流出，生生不息。如同泉眼",
        advice="找到你的源頭，讓能量持續流動",
        keywords=["澗下水", "源源", "充沛", "持續"]
    ),
    "戊寅": TranslationEntry(
        term="戊寅", category="六十甲子",
        one_line="城頭土，堅固防守",
        white_speak="戊寅納音為城頭土，城牆上的土，用於防禦。代表有防護能力，善於守成。",
        field_theory="城頭土場：能量形成防護結構，抵禦外敵。如同城牆",
        advice="建立自己的防線，保護重要的東西",
        keywords=["城頭土", "防守", "保護", "堅固"]
    ),
    "己卯": TranslationEntry(
        term="己卯", category="六十甲子",
        one_line="城頭土，守護家園",
        white_speak="己卯納音為城頭土，與戊寅同屬。守護城池和家園，有責任感。",
        field_theory="城頭土場：能量用於保護和守衛，具有責任感。如同衛士",
        advice="承擔守護責任，保護家人和團隊",
        keywords=["城頭土", "守護", "責任", "家園"]
    ),
    "庚辰": TranslationEntry(
        term="庚辰", category="六十甲子",
        one_line="白蠟金，純淨無瑕",
        white_speak="庚辰納音為白蠟金，白蠟般純淨的金，沒有雜質。代表品質純正，追求完美。",
        field_theory="白蠟金場：能量純淨無瑕，經過提煉。如同精煉的白金",
        advice="追求品質，但不要過於苛求完美",
        keywords=["白蠟金", "純淨", "完美", "品質"]
    ),
    "辛巳": TranslationEntry(
        term="辛巳", category="六十甲子",
        one_line="白蠟金，精緻貴重",
        white_speak="辛巳納音為白蠟金，與庚辰同屬。精緻且貴重，價值不凡。",
        field_theory="白蠟金場：能量精煉貴重，具有高價值。如同珍貴的白金飾品",
        advice="提升自己的價值，讓自己更加精緻",
        keywords=["白蠟金", "精緻", "貴重", "價值"]
    ),
    "壬午": TranslationEntry(
        term="壬午", category="六十甲子",
        one_line="楊柳木，柔韌有彈性",
        white_speak="壬午納音為楊柳木，楊柳樹木，柔軟但有韌性。代表能屈能伸，適應力強。",
        field_theory="楊柳木場：能量柔韌有彈性，能彎曲但不折斷。如同柳條",
        advice="學會柔軟變通，能屈能伸才能長久",
        keywords=["楊柳木", "柔韌", "彈性", "適應"]
    ),
    "癸未": TranslationEntry(
        term="癸未", category="六十甲子",
        one_line="楊柳木，隨風搖曳",
        white_speak="癸未納音為楊柳木，與壬午同屬。隨風搖曳，順勢而為。代表靈活變通。",
        field_theory="楊柳木場：能量隨外力調整，不硬碰硬。如同風中柳枝",
        advice="順勢而為，不要逆流而上",
        keywords=["楊柳木", "靈活", "順勢", "變通"]
    ),
    "甲申": TranslationEntry(
        term="甲申", category="六十甲子",
        one_line="泉中水，清涼解渴",
        white_speak="甲申納音為泉中水，泉眼中的水，清涼甘甜。代表能解人之渴，幫助他人。",
        field_theory="泉中水場：能量清涼滋潤，能解渴解熱。如同沙漠中的綠洲",
        advice="發揮助人的能力，你能解決別人的問題",
        keywords=["泉中水", "清涼", "解渴", "助人"]
    ),
    "乙酉": TranslationEntry(
        term="乙酉", category="六十甲子",
        one_line="泉中水，源頭活水",
        white_speak="乙酉納音為泉中水，與甲申同屬。是源頭的活水，生生不息。",
        field_theory="泉中水場：能量從源頭湧出，永不枯竭。如同噴泉",
        advice="保持活力，成為他人的能量來源",
        keywords=["泉中水", "源頭", "活水", "活力"]
    ),
    "丙戌": TranslationEntry(
        term="丙戌", category="六十甲子",
        one_line="屋上土，遮風擋雨",
        white_speak="丙戌納音為屋上土，屋頂上的土，用於遮風擋雨。代表保護和庇護。",
        field_theory="屋上土場：能量形成保護層，為下方提供庇護。如同房屋",
        advice="成為他人的保護傘，提供安全感",
        keywords=["屋上土", "保護", "庇護", "安全"]
    ),
    "丁亥": TranslationEntry(
        term="丁亥", category="六十甲子",
        one_line="屋上土，溫暖家園",
        white_speak="丁亥納音為屋上土，與丙戌同屬。為家人提供溫暖的住所。",
        field_theory="屋上土場：能量形成溫暖的保護結構，讓人安心。如同家",
        advice="經營好自己的家，給家人溫暖",
        keywords=["屋上土", "溫暖", "家園", "安心"]
    ),
    "戊子": TranslationEntry(
        term="戊子", category="六十甲子",
        one_line="霹靂火，一鳴驚人",
        white_speak="戊子納音為霹靂火，雷電之火，瞬間爆發。代表突然成功，一鳴驚人。",
        field_theory="霹靂火場：能量瞬間爆發，如同閃電劈下。具有震撼力",
        advice="把握爆發的機會，一擊必中",
        keywords=["霹靂火", "爆發", "驚人", "瞬間"]
    ),
    "己丑": TranslationEntry(
        term="己丑", category="六十甲子",
        one_line="霹靂火，聲勢驚人",
        white_speak="己丑納音為霹靂火，與戊子同屬。雷電交加，聲勢浩大。",
        field_theory="霹靂火場：能量以震撼方式展現，引人注目。如同驚雷",
        advice="適當展示實力，讓人刮目相看",
        keywords=["霹靂火", "聲勢", "震撼", "注目"]
    ),
    "庚寅": TranslationEntry(
        term="庚寅", category="六十甲子",
        one_line="松柏木，四季常青",
        white_speak="庚寅納音為松柏木，松樹柏樹，四季常青。代表堅韌不拔，歷久彌新。",
        field_theory="松柏木場：能量恆久不衰，經得起時間考驗。如同百年松柏",
        advice="堅持到底，時間會證明一切",
        keywords=["松柏木", "常青", "堅韌", "持久"]
    ),
    "辛卯": TranslationEntry(
        term="辛卯", category="六十甲子",
        one_line="松柏木，挺拔堅強",
        white_speak="辛卯納音為松柏木，與庚寅同屬。挺拔堅強，不畏風雪。",
        field_theory="松柏木場：能量堅強不屈，逆境中更顯本色。如同傲雪青松",
        advice="困難時不要放棄，逆境是最好的成長",
        keywords=["松柏木", "堅強", "挺拔", "不屈"]
    ),
    "壬辰": TranslationEntry(
        term="壬辰", category="六十甲子",
        one_line="長流水，源遠流長",
        white_speak="壬辰納音為長流水，長江大河，源遠流長。代表持續發展，生生不息。",
        field_theory="長流水場：能量持續流動，永不停歇。如同大江東去",
        advice="持續努力，讓事業像長河一樣流淌",
        keywords=["長流水", "源遠", "持續", "流長"]
    ),
    "癸巳": TranslationEntry(
        term="癸巳", category="六十甲子",
        one_line="長流水，奔流不息",
        white_speak="癸巳納音為長流水，與壬辰同屬。奔流向前，不回頭。",
        field_theory="長流水場：能量向前流動，勢不可擋。如同奔騰的河流",
        advice="向前看，不要留戀過去",
        keywords=["長流水", "奔流", "向前", "不回頭"]
    ),
    "甲午": TranslationEntry(
        term="甲午", category="六十甲子",
        one_line="砂石金，隱藏價值",
        white_speak="甲午納音為砂石金，砂石中的金子，需要淘洗才能發現。代表有價值但需要被發掘。",
        field_theory="砂石金場：能量隱藏在平凡之中，需要識貨的人發現。如同金礦",
        advice="不要小看自己，找到懂你的人",
        keywords=["砂石金", "隱藏", "價值", "發掘"]
    ),
    "乙未": TranslationEntry(
        term="乙未", category="六十甲子",
        one_line="砂石金，沙裡淘金",
        white_speak="乙未納音為砂石金，與甲午同屬。需要耐心淘洗，才能得到真金。",
        field_theory="砂石金場：能量需要提煉才能顯現價值。如同淘金",
        advice="耐心打磨自己，終會閃光",
        keywords=["砂石金", "淘金", "耐心", "打磨"]
    ),
    "丙申": TranslationEntry(
        term="丙申", category="六十甲子",
        one_line="山下火，溫暖人心",
        white_speak="丙申納音為山下火，山腳下的火光，溫暖旅人。代表給人溫暖和希望。",
        field_theory="山下火場：能量在低處散發溫暖，親近大眾。如同篝火",
        advice="用你的熱情溫暖身邊的人",
        keywords=["山下火", "溫暖", "親近", "希望"]
    ),
    "丁酉": TranslationEntry(
        term="丁酉", category="六十甲子",
        one_line="山下火，照亮前路",
        white_speak="丁酉納音為山下火，與丙申同屬。在山腳照亮夜行人的路。",
        field_theory="山下火場：能量為迷途者提供光明，指引方向。如同路燈",
        advice="成為他人的光，照亮別人的路",
        keywords=["山下火", "照亮", "指引", "光明"]
    ),
    "戊戌": TranslationEntry(
        term="戊戌", category="六十甲子",
        one_line="平地木，遍地開花",
        white_speak="戊戌納音為平地木，平原上的樹木，到處生長。代表發展廣泛，遍地開花。",
        field_theory="平地木場：能量在廣闊空間擴展，形成規模。如同平原森林",
        advice="廣泛發展，不要局限於一處",
        keywords=["平地木", "廣泛", "開花", "發展"]
    ),
    "己亥": TranslationEntry(
        term="己亥", category="六十甲子",
        one_line="平地木，穩健成長",
        white_speak="己亥納音為平地木，與戊戌同屬。在平地穩健生長，不急不躁。",
        field_theory="平地木場：能量穩定擴展，循序漸進。如同農田中的樹苗",
        advice="穩健發展，不求快只求穩",
        keywords=["平地木", "穩健", "成長", "循序"]
    ),
    "庚子": TranslationEntry(
        term="庚子", category="六十甲子",
        one_line="壁上土，裝飾點綴",
        white_speak="庚子納音為壁上土，牆壁上的土，用於裝飾。代表有美化和點綴的作用。",
        field_theory="壁上土場：能量在表面形成裝飾效果，美化環境。如同壁畫",
        advice="發揮美化的作用，讓事物更好看",
        keywords=["壁上土", "裝飾", "美化", "點綴"]
    ),
    "辛丑": TranslationEntry(
        term="辛丑", category="六十甲子",
        one_line="壁上土，錦上添花",
        white_speak="辛丑納音為壁上土，與庚子同屬。在好的基礎上錦上添花。",
        field_theory="壁上土場：能量增強既有的美感，提升品質。如同精美的裝修",
        advice="在好的基礎上做更好，錦上添花",
        keywords=["壁上土", "錦上添花", "提升", "品質"]
    ),
    "壬寅": TranslationEntry(
        term="壬寅", category="六十甲子",
        one_line="金箔金，閃亮奪目",
        white_speak="壬寅納音為金箔金，金箔薄而亮，用於裝飾。代表外表光鮮，吸引眼球。",
        field_theory="金箔金場：能量在表面閃耀，吸引注意。如同金箔裝飾",
        advice="善用外表優勢，但內在也要充實",
        keywords=["金箔金", "閃亮", "外表", "吸引"]
    ),
    "癸卯": TranslationEntry(
        term="癸卯", category="六十甲子",
        one_line="金箔金，光彩照人",
        white_speak="癸卯納音為金箔金，與壬寅同屬。光彩照人，引人注目。",
        field_theory="金箔金場：能量以光彩形式展現，具有吸引力。如同金色光芒",
        advice="展示你的光彩，讓人看到你的價值",
        keywords=["金箔金", "光彩", "照人", "價值"]
    ),
    "甲辰": TranslationEntry(
        term="甲辰", category="六十甲子",
        one_line="覆燈火，照亮室內",
        white_speak="甲辰納音為覆燈火，燈籠裡的火，照亮室內。代表內在的光明，溫馨安定。",
        field_theory="覆燈火場：能量在封閉空間內散發光明，提供溫暖。如同家中燈火",
        advice="經營好內在，讓家庭溫馨",
        keywords=["覆燈火", "照亮", "溫馨", "內在"]
    ),
    "乙巳": TranslationEntry(
        term="乙巳", category="六十甲子",
        one_line="覆燈火，長明不滅",
        white_speak="乙巳納音為覆燈火，與甲辰同屬。燈火長明，不會熄滅。",
        field_theory="覆燈火場：能量持續穩定輸出，如同長明燈。永不熄滅",
        advice="保持內心的光明，永不熄滅",
        keywords=["覆燈火", "長明", "持續", "穩定"]
    ),
    "丙午": TranslationEntry(
        term="丙午", category="六十甲子",
        one_line="天河水，從天而降",
        white_speak="丙午納音為天河水，銀河之水，從天而降。代表恩澤廣布，福從天降。",
        field_theory="天河水場：能量從高處降下，普惠眾生。如同天降甘霖",
        advice="把握天降的機會，也要回饋社會",
        keywords=["天河水", "天降", "恩澤", "福氣"]
    ),
    "丁未": TranslationEntry(
        term="丁未", category="六十甲子",
        one_line="天河水，潤澤萬物",
        white_speak="丁未納音為天河水，與丙午同屬。從天而降，潤澤萬物。",
        field_theory="天河水場：能量廣泛滋潤，不分彼此。如同雨露均霑",
        advice="廣施恩惠，不要偏心",
        keywords=["天河水", "潤澤", "廣布", "公平"]
    ),
    "戊申": TranslationEntry(
        term="戊申", category="六十甲子",
        one_line="大驛土，交通要道",
        white_speak="戊申納音為大驛土，驛站的土地，交通要道。代表四通八達，人來人往。",
        field_theory="大驛土場：能量流通活躍，連接各方。如同交通樞紐",
        advice="發揮連接作用，成為重要的節點",
        keywords=["大驛土", "交通", "連接", "樞紐"]
    ),
    "己酉": TranslationEntry(
        term="己酉", category="六十甲子",
        one_line="大驛土，四通八達",
        white_speak="己酉納音為大驛土，與戊申同屬。四通八達，來往頻繁。",
        field_theory="大驛土場：能量在多個方向流動，活躍度高。如同繁忙的車站",
        advice="擴大人脈，讓資源流通起來",
        keywords=["大驛土", "四通八達", "活躍", "流通"]
    ),
    "庚戌": TranslationEntry(
        term="庚戌", category="六十甲子",
        one_line="釵釧金，精巧細緻",
        white_speak="庚戌納音為釵釧金，首飾的金，精巧細緻。代表精緻優雅，有品味。",
        field_theory="釵釧金場：能量精煉成形，具有審美價值。如同精美的首飾",
        advice="提升品味，追求精緻生活",
        keywords=["釵釧金", "精巧", "細緻", "品味"]
    ),
    "辛亥": TranslationEntry(
        term="辛亥", category="六十甲子",
        one_line="釵釧金，華麗貴氣",
        white_speak="辛亥納音為釵釧金，與庚戌同屬。華麗貴氣，價值不凡。",
        field_theory="釵釧金場：能量以精美形式展現，具有高價值。如同貴族首飾",
        advice="提升自己的格調，讓自己更有價值",
        keywords=["釵釧金", "華麗", "貴氣", "價值"]
    ),
    "壬子": TranslationEntry(
        term="壬子", category="六十甲子",
        one_line="桑柘木，實用價值",
        white_speak="壬子納音為桑柘木，桑樹和柘樹，可養蠶造弓。代表有實用價值，物盡其用。",
        field_theory="桑柘木場：能量具有實用性，能轉化為有用之物。如同可用的材料",
        advice="發揮實用價值，做有用的事",
        keywords=["桑柘木", "實用", "價值", "有用"]
    ),
    "癸丑": TranslationEntry(
        term="癸丑", category="六十甲子",
        one_line="桑柘木，默默奉獻",
        white_speak="癸丑納音為桑柘木，與壬子同屬。默默提供材料，不求回報。",
        field_theory="桑柘木場：能量轉化為他人所用，具有奉獻精神。如同蠶絲",
        advice="默默付出，貢獻自己的力量",
        keywords=["桑柘木", "奉獻", "默默", "貢獻"]
    ),
    "甲寅": TranslationEntry(
        term="甲寅", category="六十甲子",
        one_line="大溪水，奔騰向前",
        white_speak="甲寅納音為大溪水，山間溪流，奔騰向前。代表有衝勁，勇往直前。",
        field_theory="大溪水場：能量快速流動，具有衝勁和活力。如同奔騰的溪水",
        advice="保持衝勁，勇往直前",
        keywords=["大溪水", "奔騰", "衝勁", "向前"]
    ),
    "乙卯": TranslationEntry(
        term="乙卯", category="六十甲子",
        one_line="大溪水，繞山而行",
        white_speak="乙卯納音為大溪水，與甲寅同屬。繞過障礙，靈活前進。",
        field_theory="大溪水場：能量遇阻則繞，靈活變通。如同溪水繞石",
        advice="遇到障礙要靈活，繞道也是前進",
        keywords=["大溪水", "靈活", "繞行", "變通"]
    ),
    "丙辰": TranslationEntry(
        term="丙辰", category="六十甲子",
        one_line="沙中土，隱藏潛力",
        white_speak="丙辰納音為沙中土，沙漠中的土，看似貧瘠實則有潛力。代表潛力待發掘。",
        field_theory="沙中土場：能量隱藏在表面之下，需要開發。如同沙漠下的綠洲",
        advice="相信自己有潛力，等待被發掘",
        keywords=["沙中土", "隱藏", "潛力", "開發"]
    ),
    "丁巳": TranslationEntry(
        term="丁巳", category="六十甲子",
        one_line="沙中土，厚積薄發",
        white_speak="丁巳納音為沙中土，與丙辰同屬。積累到一定程度就會爆發。",
        field_theory="沙中土場：能量在隱蔽處積累，等待時機爆發。如同火山",
        advice="持續積累，時機到了就爆發",
        keywords=["沙中土", "厚積", "薄發", "爆發"]
    ),
    "戊午": TranslationEntry(
        term="戊午", category="六十甲子",
        one_line="天上火，光芒萬丈",
        white_speak="戊午納音為天上火，太陽之火，光芒萬丈。代表光明磊落，影響廣泛。",
        field_theory="天上火場：能量從最高處輻射，普照萬物。如同太陽",
        advice="發揮影響力，但也要注意不要灼傷他人",
        keywords=["天上火", "光芒", "普照", "影響"]
    ),
    "己未": TranslationEntry(
        term="己未", category="六十甲子",
        one_line="天上火，溫暖大地",
        white_speak="己未納音為天上火，與戊午同屬。陽光溫暖大地，給予生機。",
        field_theory="天上火場：能量以溫暖形式惠及萬物，帶來生機。如同春日暖陽",
        advice="用你的熱情溫暖世界",
        keywords=["天上火", "溫暖", "生機", "惠及"]
    ),
    "庚申": TranslationEntry(
        term="庚申", category="六十甲子",
        one_line="石榴木，外剛內柔",
        white_speak="庚申納音為石榴木，石榴樹，外皮硬內果軟。代表外表堅強內心柔軟。",
        field_theory="石榴木場：能量外剛內柔，有保護性的外殼。如同石榴果實",
        advice="保持堅強的外表，但不要隱藏真心",
        keywords=["石榴木", "外剛", "內柔", "保護"]
    ),
    "辛酉": TranslationEntry(
        term="辛酉", category="六十甲子",
        one_line="石榴木，多子多福",
        white_speak="辛酉納音為石榴木，與庚申同屬。石榴多子，代表多子多福，成果豐富。",
        field_theory="石榴木場：能量孕育眾多成果，繁殖力強。如同石榴籽滿滿",
        advice="多培養成果，讓努力開花結果",
        keywords=["石榴木", "多子", "多福", "成果"]
    ),
    "壬戌": TranslationEntry(
        term="壬戌", category="六十甲子",
        one_line="大海水，包容萬象",
        white_speak="壬戌納音為大海水，大海之水，包容萬物。代表胸懷寬廣，包容一切。",
        field_theory="大海水場：能量無限寬廣，包容一切。如同大海納百川",
        advice="培養寬廣胸懷，包容不同的人和事",
        keywords=["大海水", "包容", "寬廣", "胸懷"]
    ),
    "癸亥": TranslationEntry(
        term="癸亥", category="六十甲子",
        one_line="大海水，深不可測",
        white_speak="癸亥納音為大海水，與壬戌同屬。深不可測，蘊含無限。這是六十甲子的最後一個。",
        field_theory="大海水場：能量深邃無限，既是終點也是起點。如同輪迴的大海",
        advice="保持深度，結束是為了新的開始",
        keywords=["大海水", "深邃", "無限", "輪迴"]
    ),
}


# =============================================================================
# 統一查詢接口
# =============================================================================

class TranslationExtDB:
    """翻譯擴展庫統一查詢"""
    
    VERSION = "1.0.0"
    
    DATABASES = {
        "紫微輔星": ZIWEI_FUZHU_DB,
        "長生十二宮": CHANGSHENG_DB,
        "五行": WUXING_DB,
        "奇門八神": QIMEN_BASHEN_DB,
        "二十四山": ERSHISI_SHAN_DB,
        "六十甲子": JIAZI_NAYIN_DB,
    }
    
    @classmethod
    def get(cls, term: str, category: str = None) -> TranslationEntry:
        """查詢翻譯"""
        if category:
            db = cls.DATABASES.get(category, {})
            return db.get(term)
        
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
    def stats(cls) -> dict:
        """統計"""
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
    print("北斗命數翻譯擴展庫 v1.0")
    print("XTF⁸ Task Chain: 批次1-4完成")
    print("@11star: 織明 × 澄韻 × 流祇 × 理樞")
    print("=" * 70)
    
    stats = TranslationExtDB.stats()
    print(f"\n【統計】")
    print(f"  類別數: {stats['categories']}")
    print(f"  總詞條: {stats['total_entries']}")
    
    print(f"\n【各類別詞條數】")
    for cat, count in stats['breakdown'].items():
        print(f"  {cat}: {count}")
    
    # 測試
    print("\n" + "=" * 70)
    print("【示例輸出】")
    print("=" * 70)
    
    tests = [
        ("左輔", "紫微輔星"),
        ("帝旺", "長生十二宮"),
        ("火", "五行"),
        ("值符", "奇門八神"),
        ("午山", "二十四山"),
        ("甲子", "六十甲子"),
    ]
    
    for term, cat in tests:
        print(f"\n{TranslationExtDB.format(term, cat)}")
    
    # 行數
    print("\n" + "=" * 70)
    with open(__file__, 'r') as f:
        lines = len(f.read().split('\n'))
    print(f"模組行數: {lines} 行")
    print(f"翻譯詞條: {stats['total_entries']} 條")
    print("=" * 70)


if __name__ == "__main__":
    main()
