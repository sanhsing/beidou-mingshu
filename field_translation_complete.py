#!/usr/bin/env python3
"""
北斗命數 完整場論翻譯系統 v1.0
==============================
六親 + 十神 + 十二宮 + 五行生剋
每項都有：白話、場論、關係處理建議

北斗七星文創 × 織明 | 2026-02-15
"""

# ============================================================
# 【一、十神完整翻譯】
# ============================================================
SHISHEN_COMPLETE = {
    "比肩": {
        "relation": "同我者（陰陽同）",
        "liuqin": "兄弟姐妹（同性）",
        "vernacular": "合作的夥伴",
        "field": "同頻共振場",
        "modern": "同事、朋友、合夥人",
        "strength": "有幫手、能合作、人脈廣",
        "weakness": "可能分資源、意見不合",
        "advice": {
            "good": "善用合作關係，一起做大事業",
            "bad": "明確分工和利益分配，避免糾紛",
            "enhance": "多參與團隊活動，建立互信",
        }
    },
    "劫財": {
        "relation": "同我者（陰陽異）",
        "liuqin": "兄弟姐妹（異性）",
        "vernacular": "競爭的對手",
        "field": "同頻干涉場",
        "modern": "競爭者、搶資源的人",
        "strength": "有競爭意識、激發潛能",
        "weakness": "可能被搶、消耗資源",
        "advice": {
            "good": "良性競爭促進成長",
            "bad": "保護核心資源，設立防線",
            "enhance": "化敵為友，競合共贏",
        }
    },
    "食神": {
        "relation": "我生者（陰陽同）",
        "liuqin": "子女（同性）、晚輩",
        "vernacular": "穩定的才華",
        "field": "穩定輸出場",
        "modern": "創作、口才、技藝",
        "strength": "有才華、受喜愛、有福氣",
        "weakness": "可能懶散、太享受",
        "advice": {
            "good": "發揮才華，穩定輸出作品",
            "bad": "避免過度享樂，保持進取心",
            "enhance": "培養一技之長，建立被動收入",
        }
    },
    "傷官": {
        "relation": "我生者（陰陽異）",
        "liuqin": "子女（異性）、晚輩",
        "vernacular": "爆發的才華",
        "field": "衝擊輸出場",
        "modern": "創新、叛逆、表演",
        "strength": "有創意、敢表現、能突破",
        "weakness": "可能得罪人、太尖銳",
        "advice": {
            "good": "把叛逆轉為創新，驚豔市場",
            "bad": "學會圓滑，不要硬碰硬",
            "enhance": "找對舞台，讓才華被看見",
        }
    },
    "偏財": {
        "relation": "我剋者（陰陽同）",
        "liuqin": "父親、情人",
        "vernacular": "機會財",
        "field": "機動掌控場",
        "modern": "投資、副業、意外收入",
        "strength": "賺錢機會多、人緣好",
        "weakness": "可能投機、財來財去",
        "advice": {
            "good": "把握機會，快進快出",
            "bad": "設停損點，不貪心",
            "enhance": "多元佈局，分散風險",
        }
    },
    "正財": {
        "relation": "我剋者（陰陽異）",
        "liuqin": "妻子（男命）、父親",
        "vernacular": "穩定的收入",
        "field": "穩定掌控場",
        "modern": "薪水、正職、固定收入",
        "strength": "收入穩定、務實可靠",
        "weakness": "可能太保守、賺辛苦錢",
        "advice": {
            "good": "穩紮穩打，累積財富",
            "bad": "適當冒險，避免錯失機會",
            "enhance": "提升專業，增加議價能力",
        }
    },
    "七殺": {
        "relation": "剋我者（陰陽同）",
        "liuqin": "子女（男命同性）",
        "vernacular": "壓力和挑戰",
        "field": "衝擊約束場",
        "modern": "壓力、競爭、敵人",
        "strength": "有魄力、敢拼搏、能成大事",
        "weakness": "可能太衝動、樹敵多",
        "advice": {
            "good": "化壓力為動力，逆境成長",
            "bad": "學會借力使力，不硬扛",
            "enhance": "找到對手的弱點，四兩撥千斤",
        }
    },
    "正官": {
        "relation": "剋我者（陰陽異）",
        "liuqin": "丈夫（女命）、上司",
        "vernacular": "合理的管束",
        "field": "穩定約束場",
        "modern": "上司、法規、制度",
        "strength": "有規矩、受尊重、正當權力",
        "weakness": "可能太拘謹、怕出錯",
        "advice": {
            "good": "遵守規則，建立信譽",
            "bad": "不要太死板，適時變通",
            "enhance": "爭取正式授權，名正言順",
        }
    },
    "偏印": {
        "relation": "生我者（陰陽同）",
        "liuqin": "偏母、繼母",
        "vernacular": "偏門的支援",
        "field": "獨特支援場",
        "modern": "偏門學問、特殊技能、另類思維",
        "strength": "有獨門絕活、思維獨特",
        "weakness": "可能太另類、難被理解",
        "advice": {
            "good": "發展獨門專長，差異化競爭",
            "bad": "適時接地氣，不要太孤僻",
            "enhance": "找到欣賞你的伯樂",
        }
    },
    "正印": {
        "relation": "生我者（陰陽異）",
        "liuqin": "母親、長輩",
        "vernacular": "有人教有人罩",
        "field": "穩定支援場",
        "modern": "導師、貴人、學歷、資源",
        "strength": "有學識、有靠山、穩定成長",
        "weakness": "可能太依賴、不接地氣",
        "advice": {
            "good": "善用貴人資源，加速成長",
            "bad": "培養獨立能力，不要太依賴",
            "enhance": "多學習、多請教，建立知識體系",
        }
    },
}

# ============================================================
# 【二、十二宮完整翻譯】
# ============================================================
GONG_COMPLETE = {
    "命宮": {
        "liuqin": "自己",
        "vernacular": "你這個人本身",
        "field": "核心自我場",
        "theme": "性格、才華、人生態度",
        "strength": "了解自己，發揮本性",
        "weakness": "盲點太多，自我設限",
        "advice": {
            "good": "認識自己，發揮優勢",
            "bad": "正視缺點，持續改進",
            "enhance": "做自己，但要適應環境",
        }
    },
    "兄弟": {
        "liuqin": "兄弟姐妹、朋友",
        "vernacular": "你的手足和戰友",
        "field": "平輩互動場",
        "theme": "合作、競爭、人際",
        "strength": "人脈廣、有幫手",
        "weakness": "可能分資源、意見不合",
        "advice": {
            "good": "建立互信，一起打拼",
            "bad": "明確界線，避免糾紛",
            "enhance": "化競爭為合作，共同成長",
        }
    },
    "夫妻": {
        "liuqin": "配偶、合作夥伴",
        "vernacular": "你的另一半",
        "field": "親密互動場",
        "theme": "感情、婚姻、合作",
        "strength": "有人陪伴、互相扶持",
        "weakness": "可能磨合、期望落差",
        "advice": {
            "good": "珍惜緣分，用心經營",
            "bad": "理解差異，包容對方",
            "enhance": "共同成長，一起變好",
        }
    },
    "子女": {
        "liuqin": "子女、晚輩、桃花",
        "vernacular": "你的下一代",
        "field": "傳承輸出場",
        "theme": "生育、教育、創作",
        "strength": "有傳承、有作品",
        "weakness": "可能操心、付出多",
        "advice": {
            "good": "用心培育，傳承智慧",
            "bad": "適度放手，讓他獨立",
            "enhance": "把才華轉為作品，留下legacy",
        }
    },
    "財帛": {
        "liuqin": "財運、收入",
        "vernacular": "你的錢袋子",
        "field": "資源掌控場",
        "theme": "賺錢、理財、物質",
        "strength": "財源穩定、物質充裕",
        "weakness": "可能守財、太物質",
        "advice": {
            "good": "開源節流，穩健理財",
            "bad": "不要太貪，見好就收",
            "enhance": "提升價值，錢自然來",
        }
    },
    "疾厄": {
        "liuqin": "健康、災厄",
        "vernacular": "你的身體狀況",
        "field": "身體能量場",
        "theme": "健康、意外、壓力",
        "strength": "身體健康、抗壓力強",
        "weakness": "可能過勞、忽視健康",
        "advice": {
            "good": "定期體檢，預防勝於治療",
            "bad": "有症狀及早處理，不要拖",
            "enhance": "作息正常，運動養生",
        }
    },
    "遷移": {
        "liuqin": "外出、貴人",
        "vernacular": "你出門在外的運氣",
        "field": "外部機遇場",
        "theme": "旅行、外地、貴人",
        "strength": "貴人多、外出順利",
        "weakness": "可能奔波、水土不服",
        "advice": {
            "good": "多出門，機會在外面",
            "bad": "注意安全，小心意外",
            "enhance": "拓展視野，連結外部資源",
        }
    },
    "交友": {
        "liuqin": "下屬、朋友、同事",
        "vernacular": "你身邊的人",
        "field": "人際網絡場",
        "theme": "人脈、下屬、社交",
        "strength": "人緣好、有團隊",
        "weakness": "可能交友不慎、被拖累",
        "advice": {
            "good": "廣結善緣，建立人脈",
            "bad": "識人要明，遠離損友",
            "enhance": "以誠待人，吸引同頻的人",
        }
    },
    "官祿": {
        "liuqin": "事業、地位",
        "vernacular": "你的工作和成就",
        "field": "社會定位場",
        "theme": "事業、職位、名聲",
        "strength": "有成就、受肯定",
        "weakness": "可能壓力大、責任重",
        "advice": {
            "good": "專注本業，做出成績",
            "bad": "不要貪功，穩紮穩打",
            "enhance": "建立專業品牌，讓人記住你",
        }
    },
    "田宅": {
        "liuqin": "家庭、房產",
        "vernacular": "你的家和房子",
        "field": "根基穩定場",
        "theme": "房產、家庭、祖業",
        "strength": "有根基、家庭和睦",
        "weakness": "可能負擔重、家務多",
        "advice": {
            "good": "經營家庭，置產安居",
            "bad": "不要過度投資房產",
            "enhance": "打造溫暖的家，是最好的投資",
        }
    },
    "福德": {
        "liuqin": "福氣、精神生活",
        "vernacular": "你的內心世界",
        "field": "內在滿足場",
        "theme": "精神、興趣、福報",
        "strength": "知足常樂、內心富足",
        "weakness": "可能空虛、想太多",
        "advice": {
            "good": "培養興趣，滋養心靈",
            "bad": "不要胡思亂想，活在當下",
            "enhance": "做善事，累積福報",
        }
    },
    "父母": {
        "liuqin": "父母、長輩、文書",
        "vernacular": "你的長輩和靠山",
        "field": "支援傳承場",
        "theme": "父母、長輩、學業",
        "strength": "有靠山、有傳承",
        "weakness": "可能依賴、期望壓力",
        "advice": {
            "good": "孝順父母，傳承智慧",
            "bad": "獨立自主，不過度依賴",
            "enhance": "學習長輩經驗，站在巨人肩膀",
        }
    },
}

# ============================================================
# 【三、五行關係完整翻譯】
# ============================================================
WUXING_RELATION_COMPLETE = {
    "相生": {
        "木生火": {
            "vernacular": "創意點燃熱情",
            "field": "能量順流，火場增強",
            "advice": {
                "good": "順勢而為，把想法變成行動",
                "bad": "火太旺會燒盡木，適可而止",
                "enhance": "持續輸出創意，保持熱情",
            }
        },
        "火生土": {
            "vernacular": "熱情沉澱成果",
            "field": "表現轉化為累積",
            "advice": {
                "good": "把展現的成績沉澱下來",
                "bad": "不要只有熱度沒有成果",
                "enhance": "每次表現都要留下資產",
            }
        },
        "土生金": {
            "vernacular": "累積產生價值",
            "field": "執行產出成果",
            "advice": {
                "good": "穩紮穩打，自然產生回報",
                "bad": "太慢會錯失機會",
                "enhance": "持續累積，等待收割",
            }
        },
        "金生水": {
            "vernacular": "規則產生流動",
            "field": "制度催生靈活",
            "advice": {
                "good": "在規則中找到靈活空間",
                "bad": "太死板會失去彈性",
                "enhance": "建立SOP，但保留調整空間",
            }
        },
        "水生木": {
            "vernacular": "智慧滋養創意",
            "field": "策略支援成長",
            "advice": {
                "good": "用知識澆灌想法，讓它長大",
                "bad": "空想不行動會萎縮",
                "enhance": "持續學習，培養創新能力",
            }
        },
    },
    "相剋": {
        "木剋土": {
            "vernacular": "創新打破穩定",
            "field": "變革衝擊既有",
            "advice": {
                "good": "適度打破框架，推動改革",
                "bad": "太激進會失去根基",
                "enhance": "漸進式創新，不要一步到位",
            }
        },
        "土剋水": {
            "vernacular": "執行限制策略",
            "field": "穩定約束變化",
            "advice": {
                "good": "用紀律控制衝動",
                "bad": "太僵化會失去靈活",
                "enhance": "建立框架，但留有餘地",
            }
        },
        "水剋火": {
            "vernacular": "策略壓制衝動",
            "field": "冷靜控制熱情",
            "advice": {
                "good": "理性分析，避免衝動決策",
                "bad": "太冷會失去行動力",
                "enhance": "冷靜規劃，但要果斷執行",
            }
        },
        "火剋金": {
            "vernacular": "熱情打破規則",
            "field": "創意挑戰制度",
            "advice": {
                "good": "用熱情融化僵化的制度",
                "bad": "太衝會破壞秩序",
                "enhance": "在規則內展現創意",
            }
        },
        "金剋木": {
            "vernacular": "規則限制創新",
            "field": "制度約束成長",
            "advice": {
                "good": "用紀律修剪雜枝，專注核心",
                "bad": "太嚴會壓制創意",
                "enhance": "有原則地創新，不要天馬行空",
            }
        },
    },
    "反生": {
        "水多木漂": {
            "vernacular": "資源過多反害",
            "field": "支援太多失去自主",
            "advice": {
                "good": "感恩資源，但要獨立",
                "bad": "不要被資源養廢了",
                "enhance": "善用資源，但保持獨立性",
            }
        },
        "木多火塞": {
            "vernacular": "創意太多動不了",
            "field": "想法過載無法執行",
            "advice": {
                "good": "精選最好的想法執行",
                "bad": "想太多做太少會焦慮",
                "enhance": "先做一個MVP，再迭代",
            }
        },
        "火多土焦": {
            "vernacular": "表現過度傷根基",
            "field": "曝光過頭反受害",
            "advice": {
                "good": "適度曝光，保持神秘感",
                "bad": "過度行銷會透支信任",
                "enhance": "低調累積，高調出擊",
            }
        },
        "土多金埋": {
            "vernacular": "執行太重限創新",
            "field": "務實過度失靈活",
            "advice": {
                "good": "在穩定中尋找突破口",
                "bad": "太保守會錯失機會",
                "enhance": "穩中求變，漸進創新",
            }
        },
        "金多水濁": {
            "vernacular": "制度太僵失活力",
            "field": "規則過多阻流動",
            "advice": {
                "good": "簡化規則，保持靈活",
                "bad": "官僚主義會扼殺創新",
                "enhance": "定期清理無效規則",
            }
        },
    },
    "反剋": {
        "木堅金缺": {
            "vernacular": "創意太強制度崩",
            "field": "變革過猛規則失效",
            "advice": {
                "good": "創新要有底線",
                "bad": "太叛逆會失去秩序",
                "enhance": "在框架內最大化創新",
            }
        },
        "金多火熄": {
            "vernacular": "制度太僵創新死",
            "field": "規則壓制熱情",
            "advice": {
                "good": "適度鬆綁，激發活力",
                "bad": "太多規則會窒息組織",
                "enhance": "保留創新空間",
            }
        },
        "火多水乾": {
            "vernacular": "熱情過度理智失",
            "field": "衝動壓過策略",
            "advice": {
                "good": "熱情要有理智引導",
                "bad": "太衝動會後悔",
                "enhance": "激情加上紀律",
            }
        },
        "水多土崩": {
            "vernacular": "變化太大組織垮",
            "field": "流動過快根基失",
            "advice": {
                "good": "變化要有節奏",
                "bad": "太多變化會失去穩定",
                "enhance": "漸進式變革",
            }
        },
        "土多木折": {
            "vernacular": "穩定過重創新壓",
            "field": "既得利益阻變革",
            "advice": {
                "good": "在穩定中培育創新",
                "bad": "太守舊會被時代淘汰",
                "enhance": "保持開放心態",
            }
        },
    },
}

# ============================================================
# 【四、六親完整翻譯】
# ============================================================
LIUQIN_COMPLETE = {
    "父": {
        "shishen": ["偏財", "正財"],
        "gong": "父母宮",
        "vernacular": "生命的來源",
        "field": "權威支撐場",
        "theme": "供養、權威、資源",
        "advice": {
            "good": "感恩父親的付出，傳承他的智慧",
            "bad": "不要過度依賴，學會獨立承擔",
            "enhance": "和父親建立平等的成人關係",
        }
    },
    "母": {
        "shishen": ["正印", "偏印"],
        "gong": "父母宮",
        "vernacular": "無條件的愛",
        "field": "滋養支援場",
        "theme": "養育、教育、情感",
        "advice": {
            "good": "感恩母親的養育，常回家看看",
            "bad": "不要讓媽媽太操心",
            "enhance": "把母親的愛傳遞給下一代",
        }
    },
    "兄弟姐妹": {
        "shishen": ["比肩", "劫財"],
        "gong": "兄弟宮",
        "vernacular": "一起長大的戰友",
        "field": "平輩競合場",
        "theme": "合作、競爭、支援",
        "advice": {
            "good": "化競爭為合作，一起做大事",
            "bad": "明確界線，避免財務糾紛",
            "enhance": "互相扶持，共同成長",
        }
    },
    "配偶": {
        "shishen": ["正財", "正官"],
        "gong": "夫妻宮",
        "vernacular": "人生的伴侶",
        "field": "親密互補場",
        "theme": "感情、婚姻、合作",
        "advice": {
            "good": "珍惜對方，用心經營感情",
            "bad": "理解差異，包容對方的缺點",
            "enhance": "共同成長，一起變得更好",
        }
    },
    "子女": {
        "shishen": ["食神", "傷官", "七殺", "正官"],
        "gong": "子女宮",
        "vernacular": "生命的延續",
        "field": "傳承輸出場",
        "theme": "生育、教育、傳承",
        "advice": {
            "good": "用心培育，傳承智慧和價值觀",
            "bad": "適度放手，讓孩子獨立",
            "enhance": "做孩子的榜樣，而不是管家",
        }
    },
}


# ============================================================
# 【工具函數】
# ============================================================

def get_shishen_complete(shishen: str) -> dict:
    """獲取十神完整翻譯"""
    return SHISHEN_COMPLETE.get(shishen, {})

def get_gong_complete(gong: str) -> dict:
    """獲取十二宮完整翻譯"""
    return GONG_COMPLETE.get(gong, {})

def get_wuxing_relation(relation_type: str, relation: str) -> dict:
    """獲取五行關係翻譯
    
    relation_type: 相生/相剋/反生/反剋
    relation: 如 木生火, 水剋火, 水多木漂 等
    """
    return WUXING_RELATION_COMPLETE.get(relation_type, {}).get(relation, {})

def get_liuqin_complete(liuqin: str) -> dict:
    """獲取六親完整翻譯"""
    return LIUQIN_COMPLETE.get(liuqin, {})

def analyze_relationship(my_wx: str, other_wx: str) -> dict:
    """分析兩人五行關係及建議
    
    返回：關係類型、白話、場論、建議
    """
    WX = ["木", "火", "土", "金", "水"]
    WX_SHENG = {"木": "火", "火": "土", "土": "金", "金": "水", "水": "木"}
    WX_KE = {"木": "土", "土": "水", "水": "火", "火": "金", "金": "木"}
    
    result = {
        "my_wx": my_wx,
        "other_wx": other_wx,
        "relation_type": "",
        "relation_name": "",
        "vernacular": "",
        "field": "",
        "advice": {},
    }
    
    # 判斷關係
    if WX_SHENG[my_wx] == other_wx:
        # 我生他
        relation = f"{my_wx}生{other_wx}"
        result["relation_type"] = "我生他"
        result["relation_name"] = relation
        data = get_wuxing_relation("相生", relation)
    elif WX_SHENG[other_wx] == my_wx:
        # 他生我
        relation = f"{other_wx}生{my_wx}"
        result["relation_type"] = "他生我"
        result["relation_name"] = relation
        data = get_wuxing_relation("相生", relation)
    elif WX_KE[my_wx] == other_wx:
        # 我剋他
        relation = f"{my_wx}剋{other_wx}"
        result["relation_type"] = "我剋他"
        result["relation_name"] = relation
        data = get_wuxing_relation("相剋", relation)
    elif WX_KE[other_wx] == my_wx:
        # 他剋我
        relation = f"{other_wx}剋{my_wx}"
        result["relation_type"] = "他剋我"
        result["relation_name"] = relation
        data = get_wuxing_relation("相剋", relation)
    else:
        # 同五行或無直接關係
        result["relation_type"] = "同類或無直接關係"
        result["relation_name"] = f"{my_wx}與{other_wx}"
        data = {
            "vernacular": "同頻或平行",
            "field": "共振或無干涉",
            "advice": {
                "good": "互相理解，和平共處",
                "bad": "可能缺乏互補",
                "enhance": "找到互補的第三方",
            }
        }
    
    result["vernacular"] = data.get("vernacular", "")
    result["field"] = data.get("field", "")
    result["advice"] = data.get("advice", {})
    
    return result


# ============================================================
# 測試
# ============================================================
if __name__ == "__main__":
    print("=" * 60)
    print("     北斗命數 完整場論翻譯系統 測試")
    print("=" * 60)
    
    # 十神
    print("\n【十神測試】")
    for ss in ["比肩", "七殺", "正印"]:
        data = get_shishen_complete(ss)
        print(f"  {ss}: {data['vernacular']} | {data['field']}")
        print(f"       建議: {data['advice']['enhance']}")
    
    # 十二宮
    print("\n【十二宮測試】")
    for gong in ["命宮", "夫妻", "財帛"]:
        data = get_gong_complete(gong)
        print(f"  {gong}: {data['vernacular']} | {data['field']}")
        print(f"       建議: {data['advice']['enhance']}")
    
    # 五行關係
    print("\n【五行關係測試】")
    result = analyze_relationship("水", "木")
    print(f"  水 → 木: {result['relation_type']}")
    print(f"       白話: {result['vernacular']}")
    print(f"       場論: {result['field']}")
    print(f"       建議: {result['advice']['enhance']}")
    
    # 六親
    print("\n【六親測試】")
    for lq in ["父", "配偶", "子女"]:
        data = get_liuqin_complete(lq)
        print(f"  {lq}: {data['vernacular']} | {data['field']}")
        print(f"       建議: {data['advice']['enhance']}")
    
    print("\n" + "=" * 60)
    print("✅ 完整場論翻譯系統測試完成！")
    print("=" * 60)
