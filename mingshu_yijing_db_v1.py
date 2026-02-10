#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
mingshu_yijing_db_v1.py - 易經64卦完整翻譯資料庫 v1.0
====================================================
北斗七星文創 × 織明 × 澄韻 × 流祇

64卦完整解讀：
- 卦名 + 卦象
- 卦辭白話
- 場論視角
- 實用建議

PYLIB First: 一次建立，處處引用

📚 知識點：
    「易經 = 變化的智慧」
    「64卦 = 64種場態」
    「場論 = 易經的現代語言」
"""

from dataclasses import dataclass, asdict
from typing import Dict, List

@dataclass
class GuaEntry:
    """卦的翻譯條目"""
    number: int          # 卦序
    name: str            # 卦名
    symbol: str          # 卦象 (上卦/下卦)
    gua_ci: str          # 卦辭原文
    one_line: str        # 一句話
    white_speak: str     # 白話解釋
    field_theory: str    # 場論視角
    advice: str          # 實用建議
    keywords: List[str]  # 關鍵詞
    
    def to_dict(self) -> Dict:
        return asdict(self)
    
    def format_output(self) -> str:
        return f"""【{self.name}卦】{self.symbol}
✦ 卦辭：{self.gua_ci}
✦ 一句話：{self.one_line}
✦ 白話：{self.white_speak}
✦ 場論：{self.field_theory}
✦ 建議：{self.advice}"""


# =============================================================================
# 64卦完整資料庫
# =============================================================================

YIJING_64_GUA = {
    # ===== 上經 30卦 =====
    
    1: GuaEntry(
        number=1, name="乾", symbol="☰☰ 乾上乾下",
        gua_ci="元亨利貞",
        one_line="天行健，君子自強不息",
        white_speak="六爻皆陽，代表天、剛健、積極進取。形勢大好，可以大展宏圖，但要注意物極必反，登高跌重。",
        field_theory="純陽場：能量達到極盛狀態，具有最大的創造性和擴張性。如同正午的太陽，光芒萬丈但也需警惕盛極而衰",
        advice="積極進取，大膽行動。但保持謙遜，懂得適可而止。事業可大展，切忌驕傲自滿",
        keywords=["剛健", "進取", "創造", "領導"]
    ),
    
    2: GuaEntry(
        number=2, name="坤", symbol="☷☷ 坤上坤下",
        gua_ci="元亨，利牝馬之貞",
        one_line="地勢坤，君子厚德載物",
        white_speak="六爻皆陰，代表地、柔順、包容。適合配合他人、承載責任，不宜獨斷獨行，順勢而為最好。",
        field_theory="純陰場：能量呈現承載和包容狀態，如大地承載萬物。適合支持、配合，而非主導",
        advice="順勢而為，厚積薄發。配合大勢，不要急於出頭。耐心等待時機成熟",
        keywords=["柔順", "包容", "承載", "配合"]
    ),
    
    3: GuaEntry(
        number=3, name="屯", symbol="☵☳ 坎上震下",
        gua_ci="元亨利貞，勿用有攸往，利建侯",
        one_line="萬事起頭難",
        white_speak="雷在水下，種子破土而出的艱難。開始做事會遇到阻力，但充滿希望。需要耐心和堅持，不要急躁。",
        field_theory="初生場：能量正在萌發但受到阻礙，如種子頂土而出。困難是暫時的，堅持就會突破",
        advice="開始階段遇到困難是正常的，堅持下去。尋找貴人幫助，不要獨自硬撐",
        keywords=["困難", "開始", "堅持", "希望"]
    ),
    
    4: GuaEntry(
        number=4, name="蒙", symbol="☶☵ 艮上坎下",
        gua_ci="亨，匪我求童蒙，童蒙求我",
        one_line="啟蒙教育，虛心學習",
        white_speak="山下有水，代表蒙昧需要啟發。像小孩需要教育，要虛心求教，找到好老師，循序漸進。",
        field_theory="待啟場：能量處於未開發狀態，需要外力引導才能成長。如同礦石需要提煉",
        advice="虛心學習，不懂就問。找到好的導師或顧問，按部就班，不要好高騖遠",
        keywords=["學習", "啟蒙", "虛心", "指導"]
    ),
    
    5: GuaEntry(
        number=5, name="需", symbol="☵☰ 坎上乾下",
        gua_ci="有孚，光亨，貞吉，利涉大川",
        one_line="等待時機，耐心以待",
        white_speak="雲在天上，雨還沒下。時機未到，需要耐心等待。不是不行動，而是等待最佳時機再行動。",
        field_theory="蓄勢場：能量正在積累，尚未到達釋放時機。如同雲層積聚，終將化為甘霖",
        advice="耐心等待，但不是消極等待。做好準備，時機到了就果斷行動",
        keywords=["等待", "時機", "耐心", "準備"]
    ),
    
    6: GuaEntry(
        number=6, name="訟", symbol="☰☵ 乾上坎下",
        gua_ci="有孚窒惕，中吉，終凶",
        one_line="爭訟之事，適可而止",
        white_speak="天與水相違，代表爭執、訴訟。有理也要適可而止，贏了官司可能輸了關係。能和解就和解。",
        field_theory="對抗場：能量相互衝突，形成對峙。長期對抗消耗巨大，需要找到平衡點",
        advice="能避免爭訟就避免。真要爭，也要適可而止，見好就收。尋求調解比硬碰硬好",
        keywords=["爭訟", "衝突", "和解", "適可而止"]
    ),
    
    7: GuaEntry(
        number=7, name="師", symbol="☷☵ 坤上坎下",
        gua_ci="貞，丈人吉，無咎",
        one_line="統帥軍隊，紀律嚴明",
        white_speak="地中有水，代表軍隊、組織。需要有經驗的領導，紀律嚴明，師出有名。團隊合作才能成功。",
        field_theory="組織場：能量需要有序組織才能發揮最大效力。如同軍隊需要統帥指揮",
        advice="做事要有組織、有紀律。找有經驗的人帶領，不要一盤散沙",
        keywords=["組織", "紀律", "領導", "團隊"]
    ),
    
    8: GuaEntry(
        number=8, name="比", symbol="☵☷ 坎上坤下",
        gua_ci="吉，原筮元永貞，無咎",
        one_line="親近團結，互相幫助",
        white_speak="水在地上，親密無間。代表團結、合作、親近。找到志同道合的人，互相扶持，共同發展。",
        field_theory="親和場：能量相互吸引，形成緊密連結。合作比競爭更有效率",
        advice="尋找合作夥伴，建立同盟。但要選對人，不是誰都能合作",
        keywords=["團結", "合作", "親近", "同盟"]
    ),
    
    9: GuaEntry(
        number=9, name="小畜", symbol="☴☰ 巽上乾下",
        gua_ci="亨，密雲不雨，自我西郊",
        one_line="小有積蓄，暫時等待",
        white_speak="風在天上，雲聚但雨未下。有一些積累但還不夠，需要繼續積蓄力量。小事可成，大事要等。",
        field_theory="積累場：能量正在小規模聚集，尚未達到突破臨界點。量變正在進行，質變尚需時日",
        advice="繼續積累，不要急於求成。小事可以做，大事要等條件成熟",
        keywords=["積蓄", "等待", "小成", "耐心"]
    ),
    
    10: GuaEntry(
        number=10, name="履", symbol="☰☱ 乾上兌下",
        gua_ci="履虎尾，不咥人，亨",
        one_line="小心行事，如履薄冰",
        white_speak="踩在老虎尾巴上，要非常小心。代表身處危險但可以化解。謹慎行事，按規矩辦事，就不會有事。",
        field_theory="謹慎場：能量處於危險邊緣，需要高度警覺和規範行為。如走鋼索，專注則安",
        advice="謹慎小心，遵守規則。不要冒險，不要越界。按部就班最安全",
        keywords=["謹慎", "規矩", "小心", "守禮"]
    ),
    
    11: GuaEntry(
        number=11, name="泰", symbol="☷☰ 坤上乾下",
        gua_ci="小往大來，吉亨",
        one_line="天地交泰，萬事亨通",
        white_speak="地在上天在下，天地相交，陰陽調和。這是最好的卦之一！萬事順利，貴人多助，好運當頭。",
        field_theory="和諧場：陰陽能量完美交融，形成最佳的流通狀態。如同春天萬物生長",
        advice="把握好運，積極行動。但好運不會永遠，要居安思危",
        keywords=["亨通", "順利", "和諧", "交流"]
    ),
    
    12: GuaEntry(
        number=12, name="否", symbol="☰☷ 乾上坤下",
        gua_ci="否之匪人，不利君子貞",
        one_line="天地不交，閉塞不通",
        white_speak="天在上地在下，各走各的，不相交流。代表閉塞、阻礙、不順。小人得勢，君子宜隱。",
        field_theory="阻塞場：陰陽能量分離不交，形成停滯狀態。如同冬天萬物收藏",
        advice="低調忍耐，靜待時機。不要強出頭，保存實力。否極泰來",
        keywords=["閉塞", "阻礙", "忍耐", "等待"]
    ),
    
    13: GuaEntry(
        number=13, name="同人", symbol="☰☲ 乾上離下",
        gua_ci="同人于野，亨，利涉大川",
        one_line="志同道合，團結合作",
        white_speak="天與火同升，代表志同道合的人聚在一起。找到理念相同的夥伴，一起奮鬥，可以成大事。",
        field_theory="共振場：相同頻率的能量相互增強，形成合力。志同道合則事半功倍",
        advice="尋找志同道合的人，組建團隊。但要胸懷寬廣，不要小圈子",
        keywords=["同心", "合作", "團結", "志同道合"]
    ),
    
    14: GuaEntry(
        number=14, name="大有", symbol="☲☰ 離上乾下",
        gua_ci="元亨",
        one_line="大有所獲，豐收滿盈",
        white_speak="火在天上，光明普照。代表大豐收、大成功。財運亨通，事業有成。但要懂得分享，不要獨佔。",
        field_theory="豐盛場：能量充沛且分布廣泛，如陽光普照大地。收穫的時候到了",
        advice="享受成果，但要懂得感恩和分享。富貴不忘本，才能長久",
        keywords=["豐收", "富有", "成功", "分享"]
    ),
    
    15: GuaEntry(
        number=15, name="謙", symbol="☷☶ 坤上艮下",
        gua_ci="亨，君子有終",
        one_line="謙虛謹慎，有始有終",
        white_speak="山在地下，高山卻居於低處。代表謙虛、低調。越有能力越要謙虛，這樣才能走得長遠。",
        field_theory="謙退場：能量主動收斂，不外顯鋒芒。如同滿杯的水，不溢不漏",
        advice="保持謙虛，不要驕傲。越成功越要低調，才能持久",
        keywords=["謙虛", "低調", "持久", "有終"]
    ),
    
    16: GuaEntry(
        number=16, name="豫", symbol="☳☷ 震上坤下",
        gua_ci="利建侯行師",
        one_line="歡樂愉快，順勢而為",
        white_speak="雷從地出，萬物歡欣。代表喜悅、順利、眾人擁護。順勢而為，事半功倍。但不要樂極生悲。",
        field_theory="順勢場：能量順應自然規律流動，阻力最小。如春雷驚蟄，萬物響應",
        advice="順勢而為，把握時機。但不要得意忘形，樂極生悲",
        keywords=["歡樂", "順勢", "眾望", "時機"]
    ),
    
    17: GuaEntry(
        number=17, name="隨", symbol="☱☳ 兌上震下",
        gua_ci="元亨利貞，無咎",
        one_line="隨機應變，順應潮流",
        white_speak="澤中有雷，跟隨形勢。代表適應變化、隨機應變。不是盲目跟從，而是明智地順應潮流。",
        field_theory="適應場：能量根據外部環境調整方向，保持靈活。如水之就下，隨方就圓",
        advice="順應潮流，靈活應變。但要有主見，不是盲目跟風",
        keywords=["隨順", "應變", "靈活", "適應"]
    ),
    
    18: GuaEntry(
        number=18, name="蠱", symbol="☶☴ 艮上巽下",
        gua_ci="元亨，利涉大川",
        one_line="撥亂反正，改革弊端",
        white_speak="山下有風，器皿中生蟲。代表腐敗、弊端需要整頓。發現問題要及時改正，不要拖延。",
        field_theory="整頓場：能量需要重新梳理和淨化，清除積弊。如同打掃房間，除舊布新",
        advice="發現問題立即改正。改革要果斷，但也要循序漸進",
        keywords=["整頓", "改革", "糾正", "除弊"]
    ),
    
    19: GuaEntry(
        number=19, name="臨", symbol="☷☱ 坤上兌下",
        gua_ci="元亨利貞，至于八月有凶",
        one_line="居高臨下，親臨指導",
        white_speak="地上有澤，以上臨下。代表領導、監督、關懷。上位者要親近下屬，但好景不長，要提前準備。",
        field_theory="臨近場：能量從高處向低處流動，形成指導和影響。如春天來臨，萬物甦醒",
        advice="把握當前的好時機，但要居安思危。好運會過去，要提前準備",
        keywords=["臨近", "領導", "關懷", "把握"]
    ),
    
    20: GuaEntry(
        number=20, name="觀", symbol="☴☷ 巽上坤下",
        gua_ci="盥而不薦，有孚顒若",
        one_line="觀察學習，以身作則",
        white_speak="風行地上，無處不到。代表觀察、學習、示範。先觀察清楚再行動，上位者要以身作則。",
        field_theory="觀察場：能量在廣泛流動中收集信息，形成全面認知。如風之周遊，無所不至",
        advice="先觀察，後行動。上位者以身作則，下位者虛心學習",
        keywords=["觀察", "學習", "示範", "認知"]
    ),
    
    21: GuaEntry(
        number=21, name="噬嗑", symbol="☲☳ 離上震下",
        gua_ci="亨，利用獄",
        one_line="咬合障礙，果斷解決",
        white_speak="雷電交加，口中有物。代表障礙需要咬斷、問題需要解決。對待壞人壞事要果斷處理。",
        field_theory="突破場：能量遇到阻礙時需要強力突破。如牙齒咬斷食物，清除障礙",
        advice="遇到障礙果斷處理，不要姑息。但要依法依規，不能濫用權力",
        keywords=["突破", "果斷", "處理", "法治"]
    ),
    
    22: GuaEntry(
        number=22, name="賁", symbol="☶☲ 艮上離下",
        gua_ci="亨，小利有攸往",
        one_line="文飾裝扮，適度即可",
        white_speak="山下有火，光照山間。代表裝飾、美化、文采。適度的包裝是必要的，但不能只有外表沒有內涵。",
        field_theory="修飾場：能量在表面形成美觀的呈現。外在與內在要平衡，過度修飾反而失真",
        advice="適度包裝自己，但內在修養更重要。不要金玉其外，敗絮其中",
        keywords=["文飾", "美化", "適度", "內外兼修"]
    ),
    
    23: GuaEntry(
        number=23, name="剝", symbol="☶☷ 艮上坤下",
        gua_ci="不利有攸往",
        one_line="剝落衰敗，靜待時機",
        white_speak="山附於地，陽氣剝盡。代表衰敗、剝落、小人得勢。不宜行動，靜觀其變，等待轉機。",
        field_theory="衰退場：能量逐漸消散，處於低谷期。如秋葉凋零，需要等待春天",
        advice="低調隱忍，不要強求。保存實力，等待時機。否極泰來",
        keywords=["剝落", "衰敗", "隱忍", "等待"]
    ),
    
    24: GuaEntry(
        number=24, name="復", symbol="☷☳ 坤上震下",
        gua_ci="亨，出入無疾，朋來無咎",
        one_line="一陽來復，否極泰來",
        white_speak="雷在地下，陽氣初生。代表復甦、轉機、新的開始。最壞的時候已經過去，好運正在回來。",
        field_theory="復甦場：能量從最低點開始回升，新的周期啟動。如冬至一陽生，萬物將復甦",
        advice="把握轉機，重新開始。過去的已經過去，專注於未來",
        keywords=["復甦", "轉機", "新生", "希望"]
    ),
    
    25: GuaEntry(
        number=25, name="無妄", symbol="☰☳ 乾上震下",
        gua_ci="元亨利貞，其匪正有眚，不利有攸往",
        one_line="真誠無妄，順其自然",
        white_speak="天下有雷，萬物自然生長。代表真誠、不妄求、順其自然。做事要正當，不要投機取巧。",
        field_theory="自然場：能量按照本然規律運行，不加人為干擾。真誠則吉，妄求則凶",
        advice="做事要正當，不要投機。順其自然，不要強求不屬於自己的東西",
        keywords=["真誠", "自然", "正當", "不妄"]
    ),
    
    26: GuaEntry(
        number=26, name="大畜", symbol="☶☰ 艮上乾下",
        gua_ci="利貞，不家食吉，利涉大川",
        one_line="大有積蓄，厚積薄發",
        white_speak="山中有天，能量被止住積蓄。代表大積累、大蓄養。積蓄實力，等待時機，然後大展宏圖。",
        field_theory="蓄養場：能量被暫時限制但在不斷積累，達到臨界點將爆發。如水庫蓄水，待時而發",
        advice="繼續積累實力，時機成熟再行動。厚積薄發，一鳴驚人",
        keywords=["積蓄", "蓄養", "厚積", "大成"]
    ),
    
    27: GuaEntry(
        number=27, name="頤", symbol="☶☳ 艮上震下",
        gua_ci="貞吉，觀頤，自求口實",
        one_line="養生養德，謹慎言行",
        white_speak="山下有雷，口中含物。代表頤養、養生、飲食。注意養生，謹慎言語，自食其力。",
        field_theory="滋養場：能量通過適當的攝取和節制來維持平衡。養身養心，缺一不可",
        advice="注意健康和養生。管好嘴巴，少說多做。自食其力最踏實",
        keywords=["養生", "言行", "節制", "自立"]
    ),
    
    28: GuaEntry(
        number=28, name="大過", symbol="☱☴ 兌上巽下",
        gua_ci="棟橈，利有攸往，亨",
        one_line="負擔過重，需要改變",
        white_speak="澤滅木，房梁彎曲。代表負擔過重、壓力太大。需要及時調整，減輕負擔，否則會崩潰。",
        field_theory="過載場：能量超出承載極限，結構面臨崩潰風險。需要減壓或加固",
        advice="減輕負擔，及時調整。不要硬撐，學會放下或求助",
        keywords=["過重", "調整", "減壓", "改變"]
    ),
    
    29: GuaEntry(
        number=29, name="坎", symbol="☵☵ 坎上坎下",
        gua_ci="習坎，有孚，維心亨，行有尚",
        one_line="重重險阻，堅持信念",
        white_speak="水流不息，一坎又一坎。代表危險、困難重重。像水一樣，堅持流動，終能穿越所有障礙。",
        field_theory="險阻場：能量遭遇連續阻礙，需要持續突破。如水之穿石，在於恆久",
        advice="困難重重但不要放棄。保持信念，像水一樣堅持流動，終會突破",
        keywords=["險阻", "堅持", "信念", "突破"]
    ),
    
    30: GuaEntry(
        number=30, name="離", symbol="☲☲ 離上離下",
        gua_ci="利貞，亨，畜牝牛吉",
        one_line="光明附麗，依附正道",
        white_speak="兩火相繼，光明普照。代表光明、文明、依附。保持光明正大，依附正道，才能持久。",
        field_theory="光明場：能量以光和熱的形式輻射，需要持續的燃料供給。依附正確的對象才能持久發光",
        advice="保持光明正大。找到正確的依附對象，如事業、理想、正道",
        keywords=["光明", "依附", "文明", "正道"]
    ),
    
    # ===== 下經 34卦 =====
    
    31: GuaEntry(
        number=31, name="咸", symbol="☱☶ 兌上艮下",
        gua_ci="亨，利貞，取女吉",
        one_line="感應交流，真誠相待",
        white_speak="山上有澤，相互感應。代表感情、感應、交流。男女感情要真誠，人際交往要用心。",
        field_theory="感應場：不同性質的能量相互吸引、交流。真誠的心意能引起共鳴",
        advice="真誠待人，用心交流。感情要誠懇，不要虛情假意",
        keywords=["感應", "交流", "真誠", "感情"]
    ),
    
    32: GuaEntry(
        number=32, name="恆", symbol="☳☴ 震上巽下",
        gua_ci="亨，無咎，利貞，利有攸往",
        one_line="持之以恆，始終如一",
        white_speak="雷風相隨，恆久不變。代表堅持、恆久、持續。做事要有恆心，不能三分鐘熱度。",
        field_theory="恆常場：能量保持穩定的運行模式，持續輸出。如四季更替，恆常不變",
        advice="持之以恆，不要半途而廢。但恆常不是固執，該變的時候要變",
        keywords=["恆久", "堅持", "持續", "穩定"]
    ),
    
    33: GuaEntry(
        number=33, name="遯", symbol="☰☶ 乾上艮下",
        gua_ci="亨，小利貞",
        one_line="適時退隱，明哲保身",
        white_speak="天下有山，隱退之象。代表退讓、隱遁、避開。時機不對時要懂得退讓，保全自己。",
        field_theory="退隱場：能量主動收縮，避開不利環境。如同動物冬眠，保存實力",
        advice="該退則退，不要硬撐。暫時隱退不是失敗，是為了更好的前進",
        keywords=["退讓", "隱遁", "保全", "智慧"]
    ),
    
    34: GuaEntry(
        number=34, name="大壯", symbol="☳☰ 震上乾下",
        gua_ci="利貞",
        one_line="實力強大，但要守正",
        white_speak="雷在天上，聲勢浩大。代表實力強盛、氣勢壯大。但越強大越要守正道，不能仗勢欺人。",
        field_theory="壯盛場：能量達到強盛狀態，具有強大的影響力。但需要正確引導，否則會傷人傷己",
        advice="實力強大要守正道。不要仗勢欺人，越強越要謙虛",
        keywords=["強大", "守正", "謙虛", "節制"]
    ),
    
    35: GuaEntry(
        number=35, name="晉", symbol="☲☷ 離上坤下",
        gua_ci="康侯用錫馬蕃庶，晝日三接",
        one_line="日出地上，步步高升",
        white_speak="太陽升到地面上，光明普照。代表晉升、進步、發展。前途光明，事業順利，步步高升。",
        field_theory="上升場：能量穩步向上提升，如日出東方。機會正在到來",
        advice="把握上升機會，但要腳踏實地。不要急功近利，穩步前進",
        keywords=["晉升", "進步", "光明", "發展"]
    ),
    
    36: GuaEntry(
        number=36, name="明夷", symbol="☷☲ 坤上離下",
        gua_ci="利艱貞",
        one_line="光明受傷，韜光養晦",
        white_speak="太陽沒入地下，光明被掩蓋。代表才華被壓制、處境艱難。要韜光養晦，保護自己。",
        field_theory="隱晦場：能量被外部力量壓制，需要隱藏光芒。如同太陽落山，暫時黑暗",
        advice="韜光養晦，不要鋒芒畢露。保護自己，等待黎明",
        keywords=["韜晦", "隱忍", "保護", "等待"]
    ),
    
    37: GuaEntry(
        number=37, name="家人", symbol="☴☲ 巽上離下",
        gua_ci="利女貞",
        one_line="齊家之道，各盡本分",
        white_speak="風自火出，家庭溫暖。代表家庭、家族、團體。每個人各盡本分，家庭才會和諧。",
        field_theory="家庭場：能量在封閉系統內有序流動，各成員各司其職。如家庭分工，和諧運轉",
        advice="經營好家庭，各盡本分。家和萬事興",
        keywords=["家庭", "本分", "和諧", "齊家"]
    ),
    
    38: GuaEntry(
        number=38, name="睽", symbol="☲☱ 離上兌下",
        gua_ci="小事吉",
        one_line="意見分歧，求同存異",
        white_speak="火向上水向下，方向相反。代表分歧、對立、不同意見。大事難成，但小事可以做。",
        field_theory="分歧場：能量方向相反，難以統一。需要找到共同點，或各自發展",
        advice="承認分歧，求同存異。大事難成，先做小事。不同意見也有價值",
        keywords=["分歧", "對立", "求同存異", "小事"]
    ),
    
    39: GuaEntry(
        number=39, name="蹇", symbol="☵☶ 坎上艮下",
        gua_ci="利西南，不利東北，利見大人，貞吉",
        one_line="行路艱難，尋找幫助",
        white_speak="山前有水，難以前行。代表困難、阻礙、行路艱難。需要尋找貴人幫助，不能獨自硬闖。",
        field_theory="阻礙場：能量前進受到重大阻礙，需要繞道或借助外力。如山水阻路，需另尋他途",
        advice="遇到困難尋求幫助，不要獨自硬闖。繞道也是一種智慧",
        keywords=["困難", "阻礙", "求助", "繞道"]
    ),
    
    40: GuaEntry(
        number=40, name="解", symbol="☳☵ 震上坎下",
        gua_ci="利西南，無所往，其來復吉",
        one_line="困難解除，把握時機",
        white_speak="雷雨大作，萬物舒暢。代表解除、釋放、困難過去。危機已經解除，要把握時機行動。",
        field_theory="釋放場：積壓的能量得到釋放，阻礙被清除。如春雷化雨，萬物復甦",
        advice="困難已過，把握時機。但不要報復，要寬大為懷",
        keywords=["解除", "釋放", "時機", "寬恕"]
    ),
    
    41: GuaEntry(
        number=41, name="損", symbol="☶☱ 艮上兌下",
        gua_ci="有孚，元吉，無咎，可貞，利有攸往",
        one_line="減損得益，適度節制",
        white_speak="山下有澤，山減澤增。代表減損、節制、犧牲小我。有時候減少反而是增加，要懂得取捨。",
        field_theory="減損場：能量從一處轉移到另一處，總量守恆。損下益上，短期損失換取長期收益",
        advice="適度減損，懂得取捨。有捨才有得，不要貪多",
        keywords=["減損", "節制", "取捨", "犧牲"]
    ),
    
    42: GuaEntry(
        number=42, name="益", symbol="☴☳ 巽上震下",
        gua_ci="利有攸往，利涉大川",
        one_line="增益受益，把握機會",
        white_speak="風雷相助，萬物受益。代表增加、受益、貴人相助。好機會來了，要積極把握。",
        field_theory="增益場：能量從外部流入，形成增長態勢。如春風化雨，萬物生長",
        advice="把握增益的機會，積極行動。也要幫助他人，形成良性循環",
        keywords=["增益", "機會", "貴人", "互惠"]
    ),
    
    43: GuaEntry(
        number=43, name="夬", symbol="☱☰ 兌上乾下",
        gua_ci="揚于王庭，孚號有厲",
        one_line="決斷果敢，去除壞人",
        white_speak="澤上於天，將要決堤。代表決斷、決裂、去除。對壞人壞事要果斷處理，但要公開公正。",
        field_theory="決斷場：能量積累到臨界點，即將突破。如洪水決堤，不可阻擋",
        advice="果斷決定，不要拖泥帶水。但要公開公正，不能私自行動",
        keywords=["決斷", "果敢", "公正", "去除"]
    ),
    
    44: GuaEntry(
        number=44, name="姤", symbol="☰☴ 乾上巽下",
        gua_ci="女壯，勿用取女",
        one_line="不期而遇，小心應對",
        white_speak="天下有風，無處不入。代表相遇、邂逅、小人乘隙。突然的相遇要小心，可能是機會也可能是陷阱。",
        field_theory="邂逅場：能量意外相遇，可能產生新的組合。如風之遇物，或推動或阻礙",
        advice="不期而遇要小心判斷。可能是機會，也可能是陷阱。保持警覺",
        keywords=["相遇", "警覺", "判斷", "機會"]
    ),
    
    45: GuaEntry(
        number=45, name="萃", symbol="☱☷ 兌上坤下",
        gua_ci="亨，王假有廟，利見大人，亨，利貞",
        one_line="聚集匯合，團結力量",
        white_speak="澤在地上，水流匯聚。代表聚集、集合、團結。將力量聚集起來，可以成大事。",
        field_theory="聚集場：能量從各處匯聚到中心，形成強大合力。如百川歸海，聚沙成塔",
        advice="聚集力量，團結合作。但要有好的領導，否則一盤散沙",
        keywords=["聚集", "團結", "合力", "領導"]
    ),
    
    46: GuaEntry(
        number=46, name="升", symbol="☷☴ 坤上巽下",
        gua_ci="元亨，用見大人，勿恤，南征吉",
        one_line="逐步上升，穩健發展",
        white_speak="木在地下，逐漸生長。代表上升、晉升、穩步發展。像樹木一樣，慢慢但穩定地向上生長。",
        field_theory="上升場：能量穩定向上提升，如樹木生長。不是跳躍式，而是循序漸進",
        advice="穩步向上，不要急躁。腳踏實地，一步一個腳印",
        keywords=["上升", "穩健", "發展", "積累"]
    ),
    
    47: GuaEntry(
        number=47, name="困", symbol="☱☵ 兌上坎下",
        gua_ci="亨，貞大人吉，無咎，有言不信",
        one_line="處境困難，堅守信念",
        white_speak="澤中無水，處境艱難。代表困窮、困難、資源匱乏。處境雖難，但要堅守信念，不要喪失鬥志。",
        field_theory="困乏場：能量被消耗殆盡，處於極度匱乏狀態。如池塘乾涸，需要等待補給",
        advice="困難時堅守信念，不要喪志。說話沒人信，就用行動證明",
        keywords=["困難", "堅守", "信念", "行動"]
    ),
    
    48: GuaEntry(
        number=48, name="井", symbol="☵☴ 坎上巽下",
        gua_ci="改邑不改井，無喪無得",
        one_line="井水養人，利益大眾",
        white_speak="木入水中，汲水而上。代表滋養、供給、資源。像水井一樣，源源不斷地供給大眾。",
        field_theory="供給場：能量從源頭持續輸出，滋養眾生。如井水不竭，取之不盡",
        advice="成為對大家有用的人。但要保持水源清潔，不斷自我提升",
        keywords=["滋養", "供給", "利眾", "提升"]
    ),
    
    49: GuaEntry(
        number=49, name="革", symbol="☱☲ 兌上離下",
        gua_ci="己日乃孚，元亨利貞，悔亡",
        one_line="變革創新，除舊布新",
        white_speak="澤中有火，水火相剋。代表變革、革新、改變。舊的不去新的不來，該變就要變。",
        field_theory="變革場：能量結構發生根本性重組，舊秩序被打破。如鳳凰涅槃，浴火重生",
        advice="該變就變，不要墨守成規。但變革要選對時機，循序漸進",
        keywords=["變革", "創新", "改變", "時機"]
    ),
    
    50: GuaEntry(
        number=50, name="鼎", symbol="☲☴ 離上巽下",
        gua_ci="元吉，亨",
        one_line="鼎新革故，培養人才",
        white_speak="木上有火，鼎中烹飪。代表更新、培養、重用人才。像鼎一樣，把原材料變成美食。",
        field_theory="轉化場：能量通過特定容器和過程進行質的轉變。如烹飪將生變熟，點石成金",
        advice="培養人才，轉化資源。把普通變成不普通",
        keywords=["轉化", "培養", "人才", "更新"]
    ),
    
    51: GuaEntry(
        number=51, name="震", symbol="☳☳ 震上震下",
        gua_ci="亨，震來虩虩，笑言啞啞",
        one_line="雷聲震動，警醒振作",
        white_speak="雷聲重疊，震動四方。代表震動、驚嚇、警醒。突然的震動讓人驚嚇，但也是警醒，要振作起來。",
        field_theory="震動場：能量以強烈震盪的方式釋放，引起廣泛影響。如雷聲驚醒萬物",
        advice="突然的變故是警醒。驚嚇過後要振作，化危機為轉機",
        keywords=["震動", "警醒", "振作", "轉機"]
    ),
    
    52: GuaEntry(
        number=52, name="艮", symbol="☶☶ 艮上艮下",
        gua_ci="艮其背，不獲其身，行其庭，不見其人，無咎",
        one_line="適時而止，知止不殆",
        white_speak="兩山重疊，止而不進。代表停止、靜止、適可而止。該停就停，不要貪多，知道什麼時候該止。",
        field_theory="靜止場：能量停止流動，進入穩定狀態。如山之靜止，不動如山",
        advice="該停就停，不要貪多。適可而止，知止不殆",
        keywords=["停止", "靜止", "適可而止", "穩定"]
    ),
    
    53: GuaEntry(
        number=53, name="漸", symbol="☴☶ 巽上艮下",
        gua_ci="女歸吉，利貞",
        one_line="循序漸進，穩步發展",
        white_speak="山上有木，慢慢生長。代表漸進、緩慢、按部就班。不要急躁，一步一步來，終會成功。",
        field_theory="漸進場：能量以緩慢但穩定的速度累積和提升。如樹木年輪，歲歲增長",
        advice="循序漸進，不要急躁。按部就班，穩紮穩打",
        keywords=["漸進", "穩健", "按部就班", "耐心"]
    ),
    
    54: GuaEntry(
        number=54, name="歸妹", symbol="☳☱ 震上兌下",
        gua_ci="征凶，無攸利",
        one_line="倉促行事，後果不佳",
        white_speak="雷動澤隨，少女出嫁。代表倉促、不當、後果不佳。事情太急躁，準備不充分，結果不會好。",
        field_theory="失序場：能量運行不符合正常規律，造成紊亂。如事情顛倒，本末倒置",
        advice="不要急躁倉促。準備充分再行動，否則後果不佳",
        keywords=["倉促", "不當", "準備", "謹慎"]
    ),
    
    55: GuaEntry(
        number=55, name="豐", symbol="☳☲ 震上離下",
        gua_ci="亨，王假之，勿憂，宜日中",
        one_line="盛大豐收，居安思危",
        white_speak="雷電交加，光明盛大。代表豐盛、盛大、頂峰。事業達到頂峰，但要居安思危，盛極必衰。",
        field_theory="極盛場：能量達到最大值，處於頂峰狀態。如正午太陽，燦爛但將西斜",
        advice="享受豐盛成果，但要居安思危。盛極必衰，提前準備",
        keywords=["豐盛", "頂峰", "居安思危", "準備"]
    ),
    
    56: GuaEntry(
        number=56, name="旅", symbol="☲☶ 離上艮下",
        gua_ci="小亨，旅貞吉",
        one_line="旅途在外，謹慎處世",
        white_speak="火在山上，無所依附。代表旅行、漂泊、暫居。身在異鄉，要特別謹慎，低調處世。",
        field_theory="漂泊場：能量處於不穩定的過渡狀態，缺乏根基。如火之在山，隨時可能熄滅",
        advice="身在異鄉要謹慎。低調處世，不要惹是生非",
        keywords=["旅行", "謹慎", "低調", "暫居"]
    ),
    
    57: GuaEntry(
        number=57, name="巽", symbol="☴☴ 巽上巽下",
        gua_ci="小亨，利有攸往，利見大人",
        one_line="順風而入，柔順滲透",
        white_speak="風隨風行，無孔不入。代表順從、滲透、柔順。像風一樣，柔和但無處不到，以柔克剛。",
        field_theory="滲透場：能量以柔和方式無孔不入，達到廣泛影響。如風之入隙，不著痕跡",
        advice="以柔克剛，不要硬碰硬。像風一樣，柔和但堅持",
        keywords=["順從", "滲透", "柔順", "以柔克剛"]
    ),
    
    58: GuaEntry(
        number=58, name="兌", symbol="☱☱ 兌上兌下",
        gua_ci="亨，利貞",
        one_line="喜悅和樂，但要守正",
        white_speak="兩澤相連，喜悅交流。代表喜悅、愉快、交流。人逢喜事精神爽，但要守正道，不要放縱。",
        field_theory="喜悅場：能量呈現愉快的振動狀態，帶來正面情緒。如人逢喜事，喜氣洋洋",
        advice="享受喜悅，與人分享。但要守正，不要樂極生悲",
        keywords=["喜悅", "交流", "分享", "守正"]
    ),
    
    59: GuaEntry(
        number=59, name="渙", symbol="☴☵ 巽上坎下",
        gua_ci="亨，王假有廟，利涉大川，利貞",
        one_line="分散渙散，需要聚合",
        white_speak="風行水上，波濤渙散。代表渙散、分散、離心。團隊分散，人心不齊，需要重新聚合。",
        field_theory="離散場：能量從中心向外擴散，逐漸失去凝聚力。如冰之消融，需要重新凝聚",
        advice="凝聚人心，團結力量。用共同目標和信念把人聚合起來",
        keywords=["渙散", "聚合", "凝聚", "團結"]
    ),
    
    60: GuaEntry(
        number=60, name="節", symbol="☵☱ 坎上兌下",
        gua_ci="亨，苦節不可貞",
        one_line="節制有度，適可而止",
        white_speak="澤上有水，需要節制。代表節制、節約、限度。任何事情都要有度，過度節制也不好。",
        field_theory="節制場：能量被有意識地限制在一定範圍內，保持平衡。如水庫蓄水，有放有收",
        advice="節制有度，不要過度。過度放縱不好，過度節制也不好",
        keywords=["節制", "適度", "平衡", "限制"]
    ),
    
    61: GuaEntry(
        number=61, name="中孚", symbol="☴☱ 巽上兌下",
        gua_ci="豚魚吉，利涉大川，利貞",
        one_line="誠信中正，感化他人",
        white_speak="澤上有風，風吹水面。代表誠信、信任、感化。以誠信待人，即使是頑固的人也能被感化。",
        field_theory="誠信場：能量以真誠的方式傳遞，引起共鳴和信任。如風吹水面，自然起波",
        advice="以誠待人，建立信任。誠信是最大的資本",
        keywords=["誠信", "信任", "感化", "中正"]
    ),
    
    62: GuaEntry(
        number=62, name="小過", symbol="☳☶ 震上艮下",
        gua_ci="亨，利貞，可小事，不可大事",
        one_line="稍有過度，宜做小事",
        white_speak="山上有雷，小有越過。代表稍微過度、小事可為。大事不宜，小事可以。飛鳥留聲，不可高飛。",
        field_theory="微過場：能量略微超出正常範圍，但未造成大的偏差。可以做小事，大事則力不從心",
        advice="做小事，不要貪大。量力而行，不要越界太多",
        keywords=["小事", "適度", "量力", "謹慎"]
    ),
    
    63: GuaEntry(
        number=63, name="既濟", symbol="☵☲ 坎上離下",
        gua_ci="亨小，利貞，初吉終亂",
        one_line="事情完成，但要謹慎",
        white_speak="水在火上，烹飪完成。代表完成、成功、但要謹慎後續。事情成功了，但後面還有挑戰。",
        field_theory="完成場：能量達到平衡狀態，目標已經實現。但平衡是暫時的，需要持續維護",
        advice="事情完成要謹慎維護。初吉終亂，成功後更要小心",
        keywords=["完成", "成功", "謹慎", "維護"]
    ),
    
    64: GuaEntry(
        number=64, name="未濟", symbol="☲☵ 離上坎下",
        gua_ci="亨，小狐汔濟，濡其尾，無攸利",
        one_line="尚未完成，繼續努力",
        white_speak="火在水上，尚未完成。代表未完成、還在進行、需要努力。小狐狸過河，尾巴濕了，還沒到岸。",
        field_theory="未完成場：能量正在運行但尚未達到目標，處於過渡狀態。如事情進行中，需要持續努力",
        advice="繼續努力，不要放棄。還沒成功，最後一步更要謹慎",
        keywords=["未完成", "努力", "堅持", "謹慎"]
    ),
}


# =============================================================================
# 查詢接口
# =============================================================================

class YijingDB:
    """易經64卦資料庫"""
    
    VERSION = "1.0.0"
    
    @classmethod
    def get_by_number(cls, number: int) -> GuaEntry:
        """按卦序查詢"""
        return YIJING_64_GUA.get(number)
    
    @classmethod
    def get_by_name(cls, name: str) -> GuaEntry:
        """按卦名查詢"""
        for gua in YIJING_64_GUA.values():
            if gua.name == name:
                return gua
        return None
    
    @classmethod
    def get(cls, key) -> GuaEntry:
        """統一查詢接口"""
        if isinstance(key, int):
            return cls.get_by_number(key)
        return cls.get_by_name(key)
    
    @classmethod
    def format(cls, key) -> str:
        """格式化輸出"""
        gua = cls.get(key)
        if gua:
            return gua.format_output()
        return f"【未找到卦：{key}】"
    
    @classmethod
    def all_gua_names(cls) -> List[str]:
        """所有卦名"""
        return [g.name for g in YIJING_64_GUA.values()]
    
    @classmethod
    def stats(cls) -> Dict:
        """統計"""
        return {
            "total": len(YIJING_64_GUA),
            "upper_jing": 30,
            "lower_jing": 34
        }


# =============================================================================
# CLI 測試
# =============================================================================

def main():
    print("=" * 70)
    print("易經64卦完整翻譯資料庫 v1.0")
    print("白話 + 場論 + 實用建議")
    print("@11star: 織明 × 澄韻 × 流祇")
    print("=" * 70)
    
    stats = YijingDB.stats()
    print(f"\n【統計】")
    print(f"  總卦數: {stats['total']}")
    print(f"  上經: {stats['upper_jing']} 卦")
    print(f"  下經: {stats['lower_jing']} 卦")
    
    # 測試輸出
    print("\n" + "=" * 70)
    print("【部分卦象展示】")
    print("=" * 70)
    
    test_gua = [1, 2, 11, 12, 29, 30, 63, 64]
    for num in test_gua:
        gua = YijingDB.get(num)
        print(f"\n{gua.format_output()}")
    
    # 行數統計
    print("\n" + "=" * 70)
    with open(__file__, 'r') as f:
        lines = len(f.read().split('\n'))
    print(f"模組行數: {lines} 行")
    print(f"64卦全部完成 ✓")
    print("=" * 70)


if __name__ == "__main__":
    main()
