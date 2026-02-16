"""
易經64卦場論翻譯 yijing_gua_translation.py v1.0
==============================================
XTF任務：拓-T2 | 執行星：織明（全局）
整合日期：2026-02-08

📚 場論核心：卦 = 場的狀態描述
"""

from typing import Dict, List, Optional, Any

# ============================================================
# 64卦翻譯資料
# ============================================================

GUA_64 = {
    1: {
        "name": "乾", "symbol": "☰☰", "full_name": "乾為天",
        "keyword": "剛健", "vernacular": "開創→亨通→有利→堅守",
        "field": "場能量處於「全開」狀態",
        "modern": "像「滿血狀態」，但要知道什麼時候該收",
        "daxiang": "天行健，君子以自強不息",
        "action": "持續努力，不要等待，主動創造",
        "warning": "亢龍有悔——太滿會翻車"
    },
    2: {
        "name": "坤", "symbol": "☷☷", "full_name": "坤為地",
        "keyword": "柔順", "vernacular": "開創亨通，但要像母馬一樣順勢而行",
        "field": "場能量處於「承載」狀態",
        "modern": "像「後勤支援」，不搶風頭但不可或缺",
        "daxiang": "地勢坤，君子以厚德載物",
        "action": "配合、支持、承接、滋養",
        "warning": "不是被動，是「有意識的配合」"
    },
    3: {
        "name": "屯", "symbol": "☵☳", "full_name": "水雷屯",
        "keyword": "初生", "vernacular": "開始很好，但不要急著出去，先建立根基",
        "field": "場處於「萌芽」狀態，能量要先聚集再釋放",
        "modern": "像「創業初期」，先活下來再說",
        "daxiang": "雲雷屯，君子以經綸",
        "action": "打基礎、找人才、不急著擴張",
        "warning": "草創維艱，但堅持就會突破"
    },
    4: {
        "name": "蒙", "symbol": "☶☵", "full_name": "山水蒙",
        "keyword": "啟蒙", "vernacular": "會亨通，但要學生主動來問",
        "field": "場處於「未開發」狀態，需要引導",
        "modern": "像「學習期」，承認不懂，主動請教",
        "daxiang": "山下出泉，蒙；君子以果行育德",
        "action": "學習、請教、接受啟蒙、不恥下問",
        "warning": "再三瀆，瀆則不告"
    },
    5: {
        "name": "需", "symbol": "☵☰", "full_name": "水天需",
        "keyword": "等待", "vernacular": "有信心，會亨通，但要等待時機",
        "field": "場能量在蓄積，時機未到不要動",
        "modern": "像「等綠燈」，準備好了但還不能走",
        "daxiang": "雲上於天，需；君子以飲食宴樂",
        "action": "等待、準備、養精蓄銳、不急躁",
        "warning": "等待不是被動，是「主動的等待」"
    },
    6: {
        "name": "訟", "symbol": "☰☵", "full_name": "天水訟",
        "keyword": "爭訟", "vernacular": "有理也要小心，和解最好",
        "field": "場與場對抗，消耗能量",
        "modern": "像「打官司」，贏了也傷元氣",
        "daxiang": "天與水違行，訟；君子以作事謀始",
        "action": "和解、妥協、找中間人",
        "warning": "訟則終凶——爭到最後沒贏家"
    },
    7: {
        "name": "師", "symbol": "☷☵", "full_name": "地水師",
        "keyword": "軍隊", "vernacular": "正當的戰爭，有德行的將領帶領才會吉",
        "field": "場需要「領導核心」來統整能量",
        "modern": "像「帶團隊」，要有紀律有方向",
        "daxiang": "地中有水，師；君子以容民畜眾",
        "action": "統籌、組織、紀律、明確目標",
        "warning": "師出無名則凶"
    },
    8: {
        "name": "比", "symbol": "☵☷", "full_name": "水地比",
        "keyword": "親近", "vernacular": "吉利，但要選對人親近",
        "field": "場與場靠近，形成聯盟",
        "modern": "像「找同盟」，選對人一起走",
        "daxiang": "地上有水，比；先王以建萬國，親諸侯",
        "action": "結盟、親近、選擇合作對象",
        "warning": "比之匪人——選錯人會出事"
    },
    9: {
        "name": "小畜", "symbol": "☴☰", "full_name": "風天小畜",
        "keyword": "小蓄", "vernacular": "亨通，但蓄積還不夠",
        "field": "場能量在小規模蓄積",
        "modern": "像「存款不夠」，先繼續存",
        "daxiang": "風行天上，小畜；君子以懿文德",
        "action": "小規模累積、不要急著用",
        "warning": "小畜就是「還沒到火候」"
    },
    10: {
        "name": "履", "symbol": "☰☱", "full_name": "天澤履",
        "keyword": "踐行", "vernacular": "踩到老虎尾巴也不被咬，會亨通",
        "field": "場在危險邊緣，但知道分寸就安全",
        "modern": "像「走鋼索」，危險但有技巧就沒事",
        "daxiang": "上天下澤，履；君子以辨上下，定民志",
        "action": "小心謹慎、知道分寸、不逾矩",
        "warning": "危險中有機會，但要有分寸感"
    },
    11: {
        "name": "泰", "symbol": "☷☰", "full_name": "地天泰",
        "keyword": "通泰", "vernacular": "付出少收穫大，大吉大利",
        "field": "場上下交流，能量循環暢通",
        "modern": "像「經濟繁榮期」，一切都順",
        "daxiang": "天地交，泰；后以財成天地之道",
        "action": "把握好時機，趁勢發展",
        "warning": "泰極否來——好到頂就要轉了"
    },
    12: {
        "name": "否", "symbol": "☰☷", "full_name": "天地否",
        "keyword": "閉塞", "vernacular": "閉塞不通，付出多收穫少",
        "field": "場上下隔絕，能量無法流通",
        "modern": "像「經濟蕭條期」，做什麼都不順",
        "daxiang": "天地不交，否；君子以儉德辟難",
        "action": "收斂、節省、等待轉機",
        "warning": "否極泰來——撐過去就好了"
    },
    13: {
        "name": "同人", "symbol": "☰☲", "full_name": "天火同人",
        "keyword": "同心", "vernacular": "在廣闘處與人同心，可以成大事",
        "field": "場與場共振，形成更大的場",
        "modern": "像「找到志同道合的人」",
        "daxiang": "天與火，同人；君子以類族辨物",
        "action": "找同伴、建團隊、求同存異",
        "warning": "同人于宗，吝——只跟小圈子混會受限"
    },
    14: {
        "name": "大有", "symbol": "☲☰", "full_name": "火天大有",
        "keyword": "大有", "vernacular": "大吉大利，擁有很多",
        "field": "場能量充沛，資源豐富",
        "modern": "像「人生高峰期」，什麼都有",
        "daxiang": "火在天上，大有；君子以遏惡揚善",
        "action": "分享、回饋、不吝嗇",
        "warning": "有多少就有多大責任"
    },
    15: {
        "name": "謙", "symbol": "☷☶", "full_name": "地山謙",
        "keyword": "謙虛", "vernacular": "謙虛會亨通，君子會有好結果",
        "field": "場能量內斂，不外顯但有實力",
        "modern": "像「低調有料」，不張揚但有底氣",
        "daxiang": "地中有山，謙；君子以裒多益寡",
        "action": "謙虛、低調、不炫耀",
        "warning": "64卦中唯一六爻皆吉的卦"
    },
    16: {
        "name": "豫", "symbol": "☳☷", "full_name": "雷地豫",
        "keyword": "喜樂", "vernacular": "適合建立基業、帶領團隊",
        "field": "場能量釋放，眾人響應",
        "modern": "像「振奮人心的時刻」，士氣高昂",
        "daxiang": "雷出地奮，豫；先王以作樂崇德",
        "action": "把握時機、鼓舞士氣、啟動計畫",
        "warning": "不要只顧歡樂忘了正事"
    },
    17: {
        "name": "隨", "symbol": "☱☳", "full_name": "澤雷隨",
        "keyword": "跟隨", "vernacular": "隨順大勢會亨通",
        "field": "場跟隨大趨勢，不逆流",
        "modern": "像「順勢而為」，不硬撐",
        "daxiang": "澤中有雷，隨；君子以嚮晦入宴息",
        "action": "跟隨、配合、順勢、休息",
        "warning": "隨有獲——跟對人才有收穫"
    },
    18: {
        "name": "蠱", "symbol": "☶☴", "full_name": "山風蠱",
        "keyword": "整治", "vernacular": "有問題要處理，處理前後各三天觀察",
        "field": "場有「積弊」需要清理",
        "modern": "像「整頓爛攤子」，先搞清狀況再動手",
        "daxiang": "山下有風，蠱；君子以振民育德",
        "action": "整治、改革、清理、重建",
        "warning": "蠱=問題，但處理好反而是機會"
    },
    19: {
        "name": "臨", "symbol": "☷☱", "full_name": "地澤臨",
        "keyword": "臨近", "vernacular": "大吉，但好景不會太長",
        "field": "場在擴張期，但有時效性",
        "modern": "像「機會來了」，但有期限",
        "daxiang": "澤上有地，臨；君子以教思無窮",
        "action": "把握時機、趁勢而上、不要拖",
        "warning": "有期限，過了就變了"
    },
    20: {
        "name": "觀", "symbol": "☴☷", "full_name": "風地觀",
        "keyword": "觀察", "vernacular": "洗手還沒獻祭，莊重虔誠地觀看",
        "field": "場處於「觀察」狀態，收集訊息",
        "modern": "像「調研階段」，看清楚再說",
        "daxiang": "風行地上，觀；先王以省方觀民設教",
        "action": "觀察、調研、了解情況、不急著動",
        "warning": "先看清楚，再決定怎麼做"
    },
    21: {
        "name": "噬嗑", "symbol": "☲☳", "full_name": "火雷噬嗑",
        "keyword": "咬合", "vernacular": "亨通，適合處理糾紛、執行法律",
        "field": "場有「障礙」需要咬破",
        "modern": "像「解決卡點」，該處理就處理",
        "daxiang": "雷電噬嗑；先王以明罰敕法",
        "action": "處理問題、執行紀律、排除障礙",
        "warning": "有障礙就要咬破，不能繞過"
    },
    22: {
        "name": "賁", "symbol": "☶☲", "full_name": "山火賁",
        "keyword": "文飾", "vernacular": "亨通，適合小事出行",
        "field": "場在「裝飾」狀態，外表美化",
        "modern": "像「包裝」，內容不變但呈現更好",
        "daxiang": "山下有火，賁；君子以明庶政",
        "action": "美化、修飾、形式感、但不要過度",
        "warning": "賁如濡如——適度裝飾，不要虛假"
    },
    23: {
        "name": "剝", "symbol": "☶☷", "full_name": "山地剝",
        "keyword": "剝落", "vernacular": "不適合行動，一層層被剝落",
        "field": "場在「衰退」狀態，能量流失",
        "modern": "像「下坡路」，先止損",
        "daxiang": "山附於地，剝；上以厚下安宅",
        "action": "收縮、保守、厚待下層、止損",
        "warning": "剝到底就是復——撐過去就翻轉"
    },
    24: {
        "name": "復", "symbol": "☷☳", "full_name": "地雷復",
        "keyword": "回復", "vernacular": "亨通，來去順利，朋友來沒問題",
        "field": "場在「復甦」狀態，能量重新聚集",
        "modern": "像「觸底反彈」，最壞已過",
        "daxiang": "雷在地中，復；先王以至日閉關",
        "action": "休養生息、等待時機、慢慢恢復",
        "warning": "復=回來，好的會回來"
    },
    25: {
        "name": "无妄", "symbol": "☰☳", "full_name": "天雷无妄",
        "keyword": "無妄", "vernacular": "誠實正直會亨通，不正當會有災",
        "field": "場在「真實」狀態，不能有虛假",
        "modern": "像「實話實說」，不要有僥倖心理",
        "daxiang": "天下雷行，物與无妄",
        "action": "誠實、本分、不妄想、不投機",
        "warning": "无妄之災——沒做壞事也可能遇災，接受它"
    },
    26: {
        "name": "大畜", "symbol": "☶☰", "full_name": "山天大畜",
        "keyword": "大蓄", "vernacular": "正固有利，出去吃飯比在家好，可以做大事",
        "field": "場蓄積足夠，可以釋放能量",
        "modern": "像「存夠了可以花」，實力足夠了",
        "daxiang": "天在山中，大畜；君子以多識前言往行",
        "action": "可以行動、做大事、發揮實力",
        "warning": "畜到位才能用，不要提早花"
    },
    27: {
        "name": "頤", "symbol": "☶☳", "full_name": "山雷頤",
        "keyword": "頤養", "vernacular": "正固吉利，看怎麼養自己",
        "field": "場需要「滋養」，輸入能量",
        "modern": "像「養生」，吃什麼很重要",
        "daxiang": "山下有雷，頤；君子以慎言語，節飲食",
        "action": "滋養身心、注意飲食、謹慎言語",
        "warning": "養正則吉——養對東西才有用"
    },
    28: {
        "name": "大過", "symbol": "☱☴", "full_name": "澤風大過",
        "keyword": "大過", "vernacular": "主樑彎了，但勇往直前反而亨通",
        "field": "場處於「超負荷」狀態，需要突破",
        "modern": "像「非常時期」，要用非常手段",
        "daxiang": "澤滅木，大過；君子以獨立不懼",
        "action": "勇敢、果斷、不按常規、獨立承擔",
        "warning": "大過時期要有大過勇氣"
    },
    29: {
        "name": "坎", "symbol": "☵☵", "full_name": "坎為水",
        "keyword": "險陷", "vernacular": "重複的險境，有信心，心裡亨通，行動有功",
        "field": "場處於「險境」，但熟悉險境就能通過",
        "modern": "像「困難重重」，但堅持就能過",
        "daxiang": "水洊至，習坎；君子以常德行，習教事",
        "action": "面對、習慣、堅持、不逃避",
        "warning": "坎=習險，熟悉了就不怕"
    },
    30: {
        "name": "離", "symbol": "☲☲", "full_name": "離為火",
        "keyword": "附麗", "vernacular": "正固有利亨通，養柔順的母牛吉利",
        "field": "場處於「明亮」狀態，但要有附著點",
        "modern": "像「光芒萬丈」，但要有根基",
        "daxiang": "明兩作，離；大人以繼明照于四方",
        "action": "展現、照亮、但要有根、不要飄",
        "warning": "火需要柴——光明需要依附"
    },
    31: {
        "name": "咸", "symbol": "☱☶", "full_name": "澤山咸",
        "keyword": "感應", "vernacular": "亨通，正固有利，娶妻吉利",
        "field": "場與場產生「感應」，自然相吸",
        "modern": "像「來電了」，彼此有感覺",
        "daxiang": "山上有澤，咸；君子以虛受人",
        "action": "敞開心胸、感受他人、建立連結",
        "warning": "咸=感，真誠感應，不是技巧"
    },
    32: {
        "name": "恆", "symbol": "☳☴", "full_name": "雷風恆",
        "keyword": "恆久", "vernacular": "亨通無災，正固有利，適合行動",
        "field": "場處於「恆定」狀態，能量穩定輸出",
        "modern": "像「長期主義」，持續做下去",
        "daxiang": "雷風恆；君子以立不易方",
        "action": "堅持、恆久、不隨意改變方向",
        "warning": "恆久之道——不是不變，是核心不變"
    },
    33: {
        "name": "遯", "symbol": "☰☶", "full_name": "天山遯",
        "keyword": "退避", "vernacular": "亨通，小事正固有利",
        "field": "場需要「退避」，保存能量",
        "modern": "像「戰略撤退」，退是為了更好的進",
        "daxiang": "天下有山，遯；君子以遠小人",
        "action": "退讓、遠離、保存實力、不硬撐",
        "warning": "遯=退，但是主動的退"
    },
    34: {
        "name": "大壯", "symbol": "☳☰", "full_name": "雷天大壯",
        "keyword": "壯盛", "vernacular": "正固有利",
        "field": "場能量「極盛」，但要有節制",
        "modern": "像「力量很大」，但要用對地方",
        "daxiang": "雷在天上，大壯；君子以非禮弗履",
        "action": "用力但不過度、守禮、不恃強凌弱",
        "warning": "壯不能過——力量大也要有分寸"
    },
    35: {
        "name": "晉", "symbol": "☲☷", "full_name": "火地晉",
        "keyword": "晉升", "vernacular": "諸侯受賞馬匹眾多，一天接見三次",
        "field": "場在「上升」狀態，能量向上提升",
        "modern": "像「升官發財」，事業上升期",
        "daxiang": "明出地上，晉；君子以自昭明德",
        "action": "進取、表現自己、抓住機會",
        "warning": "晉=進，但要光明正大地進"
    },
    36: {
        "name": "明夷", "symbol": "☷☲", "full_name": "地火明夷",
        "keyword": "光明損", "vernacular": "在艱難中堅持正道有利",
        "field": "場在「隱蔽」狀態，收斂光芒",
        "modern": "像「韜光養晦」，暫時不顯露",
        "daxiang": "明入地中，明夷；君子以蒞眾用晦而明",
        "action": "隱藏、收斂、裝傻、等待時機",
        "warning": "明夷=光明受傷，但不是消失"
    },
    37: {
        "name": "家人", "symbol": "☴☲", "full_name": "風火家人",
        "keyword": "家庭", "vernacular": "女性守正有利",
        "field": "場在「家庭」範圍，內部和諧",
        "modern": "像「齊家」，先把家管好",
        "daxiang": "風自火出，家人；君子以言有物而行有恆",
        "action": "顧家、言行一致、建立規矩",
        "warning": "家齊而後國治——從小處做起"
    },
    38: {
        "name": "睽", "symbol": "☲☱", "full_name": "火澤睽",
        "keyword": "乖離", "vernacular": "小事可以，大事不行",
        "field": "場與場「分離」，方向不同",
        "modern": "像「意見分歧」，但可以求同存異",
        "daxiang": "上火下澤，睽；君子以同而異",
        "action": "承認差異、求小同、不強求一致",
        "warning": "睽=分離，但分離中有合"
    },
    39: {
        "name": "蹇", "symbol": "☵☶", "full_name": "水山蹇",
        "keyword": "艱難", "vernacular": "往平坦處好，往險峻處不好，見貴人吉",
        "field": "場有「障礙」，需要繞道或求助",
        "modern": "像「遇到瓶頸」，找人幫忙",
        "daxiang": "山上有水，蹇；君子以反身修德",
        "action": "反省、修德、求助、換路",
        "warning": "蹇=跛腳，走慢點但還是能走"
    },
    40: {
        "name": "解", "symbol": "☳☵", "full_name": "雷水解",
        "keyword": "解除", "vernacular": "往平坦處好，沒事就回去，有事就趁早",
        "field": "場「解除」束縛，能量釋放",
        "modern": "像「壓力釋放」，問題解決了",
        "daxiang": "雷雨作，解；君子以赦過宥罪",
        "action": "放下、原諒、解決問題、不翻舊帳",
        "warning": "解=解開，趁機處理積累的問題"
    },
    41: {
        "name": "損", "symbol": "☶☱", "full_name": "山澤損",
        "keyword": "減損", "vernacular": "有誠信，大吉，無災，可以正固",
        "field": "場「減損」下層，增益上層",
        "modern": "像「節省投資」，減少消費，增加儲蓄",
        "daxiang": "山下有澤，損；君子以懲忿窒欲",
        "action": "節制、減少、克制慾望",
        "warning": "損下益上——不是虧損，是調整"
    },
    42: {
        "name": "益", "symbol": "☴☳", "full_name": "風雷益",
        "keyword": "增益", "vernacular": "適合行動，可以做大事",
        "field": "場「增益」，能量流入",
        "modern": "像「好運來了」，做什麼都順",
        "daxiang": "風雷益；君子以見善則遷，有過則改",
        "action": "把握機會、做大事、改正缺點",
        "warning": "益=增加，好時機要用"
    },
    43: {
        "name": "夬", "symbol": "☱☰", "full_name": "澤天夬",
        "keyword": "決斷", "vernacular": "在朝廷公布，誠信號召有危險",
        "field": "場到了「決斷」時刻，必須選擇",
        "modern": "像「臨門一腳」，該決定了",
        "daxiang": "澤上於天，夬；君子以施祿及下",
        "action": "決斷、公開、不拖延",
        "warning": "夬=決，決斷要果斷但不魯莽"
    },
    44: {
        "name": "姤", "symbol": "☰☴", "full_name": "天風姤",
        "keyword": "相遇", "vernacular": "女子強勢，不宜娶這樣的女子",
        "field": "場發生「不期而遇」，意外接觸",
        "modern": "像「偶遇」，但要看清楚是什麼",
        "daxiang": "天下有風，姤；后以施命誥四方",
        "action": "觀察、不急著投入、看清楚",
        "warning": "姤=遇，但不是每個遇都是緣"
    },
    45: {
        "name": "萃", "symbol": "☱☷", "full_name": "澤地萃",
        "keyword": "聚集", "vernacular": "亨通，君王到宗廟，見貴人有利",
        "field": "場「聚集」能量，形成群體",
        "modern": "像「聚會」，人聚在一起",
        "daxiang": "澤上於地，萃；君子以除戎器，戒不虞",
        "action": "聚集、團結、建立組織",
        "warning": "萃=聚，聚集後要有防備"
    },
    46: {
        "name": "升", "symbol": "☷☴", "full_name": "地風升",
        "keyword": "上升", "vernacular": "大吉，見貴人好，不用擔心，往南好",
        "field": "場能量「上升」，穩步提升",
        "modern": "像「穩步上升」，一步一步往上",
        "daxiang": "地中生木，升；君子以順德積小以高大",
        "action": "累積、進步、一步一步來",
        "warning": "升=升，但是慢慢升，不是暴漲"
    },
    47: {
        "name": "困", "symbol": "☱☵", "full_name": "澤水困",
        "keyword": "困頓", "vernacular": "亨通，大人正固吉，無災，說話沒人信",
        "field": "場能量「耗盡」，需要撐住",
        "modern": "像「山窮水盡」，但堅持就能過",
        "daxiang": "澤無水，困；君子以致命遂志",
        "action": "堅持、忍耐、不放棄、少說多做",
        "warning": "困=窮，但窮則變，變則通"
    },
    48: {
        "name": "井", "symbol": "☵☴", "full_name": "水風井",
        "keyword": "井養", "vernacular": "城市會變但井不會變",
        "field": "場是「資源」，穩定供給",
        "modern": "像「公共設施」，人人可用",
        "daxiang": "木上有水，井；君子以勞民勸相",
        "action": "提供價值、服務他人、穩定輸出",
        "warning": "井=供給，但要保持清潔"
    },
    49: {
        "name": "革", "symbol": "☱☲", "full_name": "澤火革",
        "keyword": "變革", "vernacular": "到了時候才會相信，大吉利正",
        "field": "場發生「變革」，舊的被新的取代",
        "modern": "像「改革」，但要時機成熟",
        "daxiang": "澤中有火，革；君子以治曆明時",
        "action": "變革、創新、除舊布新",
        "warning": "革=變，但要在對的時候變"
    },
    50: {
        "name": "鼎", "symbol": "☲☴", "full_name": "火風鼎",
        "keyword": "鼎新", "vernacular": "大吉，亨通",
        "field": "場在「轉化」，把原料變成成品",
        "modern": "像「升級換代」，舊的變新的",
        "daxiang": "木上有火，鼎；君子以正位凝命",
        "action": "轉化、升級、革新、承擔使命",
        "warning": "鼎=器具，承載責任"
    },
    51: {
        "name": "震", "symbol": "☳☳", "full_name": "震為雷",
        "keyword": "震動", "vernacular": "亨通，雷來了會害怕，但之後笑著說話",
        "field": "場受到「震動」，警醒後振作",
        "modern": "像「被嚇到但沒事」，虛驚一場",
        "daxiang": "洊雷震；君子以恐懼修省",
        "action": "警醒、反省、振作、不要怕",
        "warning": "震=動，震後要修省"
    },
    52: {
        "name": "艮", "symbol": "☶☶", "full_name": "艮為山",
        "keyword": "止靜", "vernacular": "止於背後，不顧自己",
        "field": "場處於「靜止」狀態，暫停行動",
        "modern": "像「停下來」，該停就停",
        "daxiang": "兼山艮；君子以思不出其位",
        "action": "停止、安靜、不妄動、守住本分",
        "warning": "艮=止，知止而後有定"
    },
    53: {
        "name": "漸", "symbol": "☴☶", "full_name": "風山漸",
        "keyword": "漸進", "vernacular": "女子出嫁吉利，正固有利",
        "field": "場在「漸進」狀態，慢慢發展",
        "modern": "像「循序漸進」，一步一步來",
        "daxiang": "山上有木，漸；君子以居賢德善俗",
        "action": "慢慢來、不急躁、按程序走",
        "warning": "漸=慢，但方向對就好"
    },
    54: {
        "name": "歸妹", "symbol": "☳☱", "full_name": "雷澤歸妹",
        "keyword": "歸嫁", "vernacular": "行動不吉，沒什麼好處",
        "field": "場「錯位」，時機或對象不對",
        "modern": "像「不是時候」，先等等",
        "daxiang": "澤上有雷，歸妹；君子以永終知敝",
        "action": "等待、不急、看清楚再說",
        "warning": "歸妹=出嫁，但條件不成熟"
    },
    55: {
        "name": "豐", "symbol": "☳☲", "full_name": "雷火豐",
        "keyword": "豐盛", "vernacular": "亨通，君王到達，不用擔心，適合正午",
        "field": "場在「極盛」狀態，光芒萬丈",
        "modern": "像「人生巔峰」，但日中則昃",
        "daxiang": "雷電皆至，豐；君子以折獄致刑",
        "action": "把握高峰、發揮影響力",
        "warning": "豐=大，但大到極點就會轉"
    },
    56: {
        "name": "旅", "symbol": "☲☶", "full_name": "火山旅",
        "keyword": "旅行", "vernacular": "小亨通，旅途正固吉利",
        "field": "場在「移動」狀態，沒有固定根基",
        "modern": "像「在路上」，不是長久之計",
        "daxiang": "山上有火，旅；君子以明慎用刑",
        "action": "謹慎、低調、不長久停留",
        "warning": "旅=客，客人要有客人的樣子"
    },
    57: {
        "name": "巽", "symbol": "☴☴", "full_name": "巽為風",
        "keyword": "順入", "vernacular": "小亨通，適合行動，適合見貴人",
        "field": "場在「滲透」狀態，無孔不入",
        "modern": "像「潛移默化」，慢慢影響",
        "daxiang": "隨風巽；君子以申命行事",
        "action": "柔順、滲透、反覆強調、耐心",
        "warning": "巽=入，柔軟地進入"
    },
    58: {
        "name": "兌", "symbol": "☱☱", "full_name": "兌為澤",
        "keyword": "喜悅", "vernacular": "亨通，正固有利",
        "field": "場在「喜悅」狀態，能量互相滋養",
        "modern": "像「開心交流」，彼此受益",
        "daxiang": "麗澤兌；君子以朋友講習",
        "action": "交流、分享、一起學習",
        "warning": "兌=說，說話要讓人開心"
    },
    59: {
        "name": "渙", "symbol": "☴☵", "full_name": "風水渙",
        "keyword": "渙散", "vernacular": "亨通，君王到宗廟，可做大事",
        "field": "場在「擴散」狀態，能量向外傳播",
        "modern": "像「散播」，打破隔閡",
        "daxiang": "風行水上，渙；先王以享于帝立廟",
        "action": "擴散、傳播、打破僵局",
        "warning": "渙=散，但散是為了重聚"
    },
    60: {
        "name": "節", "symbol": "☵☱", "full_name": "水澤節",
        "keyword": "節制", "vernacular": "亨通，但太苦的節制不能長久",
        "field": "場需要「節制」，但不能過度",
        "modern": "像「適度節制」，不要太極端",
        "daxiang": "澤上有水，節；君子以制數度，議德行",
        "action": "節制、但不過分、保持平衡",
        "warning": "節=節制，適度才能持久"
    },
    61: {
        "name": "中孚", "symbol": "☴☱", "full_name": "風澤中孚",
        "keyword": "誠信", "vernacular": "連小豬和魚都感應到誠信，可做大事",
        "field": "場在「誠信」狀態，內外一致",
        "modern": "像「真誠待人」，言行一致",
        "daxiang": "澤上有風，中孚；君子以議獄緩死",
        "action": "誠信、真誠、言行一致",
        "warning": "中孚=內心誠信，不是表面功夫"
    },
    62: {
        "name": "小過", "symbol": "☳☶", "full_name": "雷山小過",
        "keyword": "小過", "vernacular": "亨通，正固有利，適合小事，不適合大事",
        "field": "場「小幅度」偏離，但在可接受範圍",
        "modern": "像「小錯可以」，但不要大錯",
        "daxiang": "山上有雷，小過；君子以行過乎恭",
        "action": "小事可以，大事不要、謙恭過度",
        "warning": "小過=小幅度超過，不要大過"
    },
    63: {
        "name": "既濟", "symbol": "☵☲", "full_name": "水火既濟",
        "keyword": "完成", "vernacular": "小亨通，正固有利，開始好結尾亂",
        "field": "場已「完成」，但完成後要維護",
        "modern": "像「功成」，但要守成",
        "daxiang": "水在火上，既濟；君子以思患而預防之",
        "action": "維護、守成、預防問題",
        "warning": "既濟=已完成，但完成後更難"
    },
    64: {
        "name": "未濟", "symbol": "☲☵", "full_name": "火水未濟",
        "keyword": "未成", "vernacular": "亨通，小狐狸快過河時尾巴濕了",
        "field": "場「未完成」，還差最後一步",
        "modern": "像「功虧一簣」，最後要小心",
        "daxiang": "火在水上，未濟；君子以慎辨物居方",
        "action": "小心、謹慎、最後關頭不鬆懈",
        "warning": "未濟=未完成，但未完成就是希望"
    }
}

# ============================================================
# 工具函數
# ============================================================

def get_gua_info(gua_num: int) -> Optional[Dict]:
    """獲取卦的完整信息"""
    return GUA_64.get(gua_num)

def get_gua_by_name(name: str) -> Optional[Dict]:
    """通過卦名獲取卦信息"""
    for num, gua in GUA_64.items():
        if gua["name"] == name:
            return {"num": num, **gua}
    return None

def translate_gua(gua_num: int) -> str:
    """生成卦的白話翻譯文本"""
    gua = get_gua_info(gua_num)
    if not gua:
        return f"未找到第{gua_num}卦"
    
    return f"""
【{gua['full_name']}】{gua['symbol']}

📖 關鍵詞：{gua['keyword']}

🗣 白話：{gua['vernacular']}

⚡ 場論：{gua['field']}

💡 現代比喻：{gua['modern']}

📜 大象：{gua['daxiang']}

🎯 行動建議：{gua['action']}

⚠️ 注意：{gua['warning']}
"""

def generate_gua_report(gua_num: int) -> Dict:
    """生成卦的報告格式"""
    gua = get_gua_info(gua_num)
    if not gua:
        return {"error": f"未找到第{gua_num}卦"}
    
    return {
        "num": gua_num,
        "name": gua["name"],
        "symbol": gua["symbol"],
        "full_name": gua["full_name"],
        "keyword": gua["keyword"],
        "vernacular": gua["vernacular"],
        "field": gua["field"],
        "modern": gua["modern"],
        "daxiang": gua["daxiang"],
        "action": gua["action"],
        "warning": gua["warning"]
    }

# ============================================================
# 測試
# ============================================================

if __name__ == "__main__":
    print("易經64卦場論翻譯模組 v1.0")
    print("=" * 50)
    print(f"總卦數：{len(GUA_64)}")
    print()
    # 測試乾卦
    print(translate_gua(1))
    # 測試未濟卦
    print(translate_gua(64))
