"""
八字進階分析模組 bazi_advanced.py v1.0 20260207
================================================
北斗命數框架擴充：五行強弱、格局判斷、神煞系統

📚 知識點：
- 五行強弱 = 八字分析的根本（身強身弱）
- 格局 = 八字的結構特徵（十種常見格局）
- 神煞 = 古典輔助判斷系統（白話化）

建立者：北斗 × 織明
XTF任務：E1+E2+B2
"""

from typing import Dict, List, Optional, Tuple
from wuxing_core import (
    GAN, ZHI, GAN_WX, GAN_YY, ZHI_WX, ZHI_CANG,
    WX_SHENG, WX_KE, WX_ORDER
)


# =============================================================================
# E1: 五行強弱分析系統
# =============================================================================

# 地支藏干力量權重（本氣60%、中氣30%、餘氣10%）
CANG_WEIGHT = {"本": 0.6, "中": 0.3, "餘": 0.1}

# 五行力量基準值
WX_BASE_POWER = {
    "木": {"旺月": ["寅", "卯"], "相月": ["亥", "子"], "休月": ["巳", "午"], "囚月": ["辰", "戌", "丑", "未"], "死月": ["申", "酉"]},
    "火": {"旺月": ["巳", "午"], "相月": ["寅", "卯"], "休月": ["辰", "戌", "丑", "未"], "囚月": ["申", "酉"], "死月": ["亥", "子"]},
    "土": {"旺月": ["辰", "戌", "丑", "未"], "相月": ["巳", "午"], "休月": ["申", "酉"], "囚月": ["亥", "子"], "死月": ["寅", "卯"]},
    "金": {"旺月": ["申", "酉"], "相月": ["辰", "戌", "丑", "未"], "休月": ["亥", "子"], "囚月": ["寅", "卯"], "死月": ["巳", "午"]},
    "水": {"旺月": ["亥", "子"], "相月": ["申", "酉"], "休月": ["寅", "卯"], "囚月": ["巳", "午"], "死月": ["辰", "戌", "丑", "未"]},
}

# 月令力量係數
MONTH_POWER = {"旺": 2.0, "相": 1.5, "休": 1.0, "囚": 0.7, "死": 0.5}


def get_month_power_state(wx: str, month_zhi: str) -> str:
    """取得五行在該月的旺衰狀態"""
    for state, months in WX_BASE_POWER.get(wx, {}).items():
        if month_zhi in months:
            return state.replace("月", "")
    return "休"


def calculate_wuxing_power(pillars: Dict[str, str], month_zhi: str) -> Dict[str, Dict]:
    """
    計算五行力量分布
    
    Args:
        pillars: {"year": "甲子", "month": "乙丑", "day": "丙寅", "hour": "丁卯"}
        month_zhi: 月支
    
    Returns:
        五行力量統計
    """
    # 初始化
    wx_power = {wx: {"count": 0, "power": 0.0, "sources": []} for wx in WX_ORDER}
    
    # 遍歷四柱
    for pillar_name, pillar in pillars.items():
        if len(pillar) < 2:
            continue
        gan, zhi = pillar[0], pillar[1]
        
        # 天干
        gan_wx = GAN_WX.get(gan, "")
        if gan_wx:
            power_state = get_month_power_state(gan_wx, month_zhi)
            power = MONTH_POWER.get(power_state, 1.0)
            wx_power[gan_wx]["count"] += 1
            wx_power[gan_wx]["power"] += power
            wx_power[gan_wx]["sources"].append(f"{pillar_name}干{gan}({power_state})")
        
        # 地支藏干
        for cang_gan, cang_type in ZHI_CANG.get(zhi, []):
            cang_wx = GAN_WX.get(cang_gan, "")
            if cang_wx:
                weight = CANG_WEIGHT.get(cang_type, 0.1)
                power_state = get_month_power_state(cang_wx, month_zhi)
                power = MONTH_POWER.get(power_state, 1.0) * weight
                wx_power[cang_wx]["count"] += weight
                wx_power[cang_wx]["power"] += power
                wx_power[cang_wx]["sources"].append(f"{pillar_name}支{zhi}藏{cang_gan}({cang_type})")
    
    return wx_power


def analyze_day_master_strength(pillars: Dict[str, str], day_gan: str) -> Dict:
    """
    分析日主強弱
    
    返回：
    - strength: 強/中/弱
    - score: 得分（0-100）
    - analysis: 分析說明
    """
    month_zhi = pillars.get("month", "")[1] if len(pillars.get("month", "")) > 1 else "子"
    day_wx = GAN_WX.get(day_gan, "木")
    
    # 計算五行力量
    wx_power = calculate_wuxing_power(pillars, month_zhi)
    
    # 計算日主得分
    # 日主得分 = 同類（比劫+印星）力量 vs 異類（官殺+財星+食傷）力量
    
    # 同類：自己+生我者
    same_wx = [day_wx]
    for wx in WX_ORDER:
        if WX_SHENG.get(wx) == day_wx:  # 生我者
            same_wx.append(wx)
    
    # 異類：剋我者+我生者+我剋者
    diff_wx = []
    for wx in WX_ORDER:
        if wx not in same_wx:
            diff_wx.append(wx)
    
    same_power = sum(wx_power[wx]["power"] for wx in same_wx)
    diff_power = sum(wx_power[wx]["power"] for wx in diff_wx)
    total_power = same_power + diff_power
    
    if total_power == 0:
        ratio = 0.5
    else:
        ratio = same_power / total_power
    
    # 判定強弱
    if ratio >= 0.55:
        strength = "身強"
        strength_desc = "日主力量充足，有自我主張"
    elif ratio <= 0.45:
        strength = "身弱"
        strength_desc = "日主力量不足，需要支援"
    else:
        strength = "中和"
        strength_desc = "日主力量適中，較為平衡"
    
    # 月令分析
    month_state = get_month_power_state(day_wx, month_zhi)
    month_desc = {
        "旺": "得令，月令扶助日主",
        "相": "相氣，月令間接支援",
        "休": "休氣，月令中立",
        "囚": "囚氣，月令不利",
        "死": "死氣，月令剋制日主"
    }.get(month_state, "")
    
    return {
        "day_master": day_gan,
        "day_wx": day_wx,
        "strength": strength,
        "strength_score": round(ratio * 100),
        "strength_desc": strength_desc,
        "month_state": month_state,
        "month_desc": month_desc,
        "same_power": round(same_power, 2),
        "diff_power": round(diff_power, 2),
        "wx_power": wx_power,
        "field_analysis": f"日主{day_gan}屬{day_wx}，{strength}格局。{month_desc}。能量比{int(ratio*100)}:{int((1-ratio)*100)}。"
    }


# =============================================================================
# E2: 格局判斷系統
# =============================================================================

GEJU_DEFINITIONS = {
    "正官格": {
        "condition": "月支藏正官透出",
        "vernacular": "規矩人的命",
        "field": "穩定約束場主導",
        "trait": "守規矩、有責任心、適合體制內發展",
        "career": "公務員、管理者、法律相關",
        "strength": "穩定、可靠、受信任",
        "weakness": "可能太保守、缺乏創新突破",
    },
    "七殺格": {
        "condition": "月支藏七殺透出",
        "vernacular": "挑戰者的命",
        "field": "衝擊約束場主導",
        "trait": "有魄力、抗壓強、適合競爭環境",
        "career": "軍警、企業家、外科醫師",
        "strength": "果斷、有魄力、能承壓",
        "weakness": "可能太衝、樹敵多",
    },
    "正印格": {
        "condition": "月支藏正印透出",
        "vernacular": "有靠山的命",
        "field": "穩定支援場主導",
        "trait": "有學識、有貴人、適合學術發展",
        "career": "教師、學者、研究員",
        "strength": "有學識、有人脈、穩定成長",
        "weakness": "可能太依賴、不接地氣",
    },
    "偏印格": {
        "condition": "月支藏偏印透出",
        "vernacular": "另類才華的命",
        "field": "獨特支援場主導",
        "trait": "有獨特才能、思維非主流",
        "career": "藝術家、命理師、另類醫療",
        "strength": "獨特、有創意、不受框架限制",
        "weakness": "可能太怪、不被主流認可",
    },
    "食神格": {
        "condition": "月支藏食神透出",
        "vernacular": "有福氣的命",
        "field": "穩定輸出場主導",
        "trait": "有才華、重享受、人緣好",
        "career": "廚師、藝術創作、服務業",
        "strength": "有才華、有福氣、人緣好",
        "weakness": "可能太安逸、缺乏進取心",
    },
    "傷官格": {
        "condition": "月支藏傷官透出",
        "vernacular": "叛逆才子的命",
        "field": "衝擊輸出場主導",
        "trait": "才華洋溢、敢於創新、不守成規",
        "career": "律師、評論家、創意工作者",
        "strength": "有才華、有創意、敢突破",
        "weakness": "可能太衝、得罪人",
    },
    "正財格": {
        "condition": "月支藏正財透出",
        "vernacular": "穩定理財的命",
        "field": "穩定掌控場主導",
        "trait": "務實、會理財、財運穩定",
        "career": "會計、金融、資產管理",
        "strength": "財運穩定、務實可靠",
        "weakness": "可能太計較、格局不大",
    },
    "偏財格": {
        "condition": "月支藏偏財透出",
        "vernacular": "機會財的命",
        "field": "機動掌控場主導",
        "trait": "人脈廣、機會多、財路寬",
        "career": "業務、投資、企業主",
        "strength": "機會多、人脈廣、財路寬",
        "weakness": "可能不穩定、投機風險",
    },
    "建祿格": {
        "condition": "月支為日主祿位",
        "vernacular": "自力更生的命",
        "field": "同頻共振場主導",
        "trait": "獨立、自信、靠自己打拼",
        "career": "自由業、創業者",
        "strength": "獨立自主、不靠他人",
        "weakness": "可能太孤傲、缺乏助力",
    },
    "羊刃格": {
        "condition": "月支為日主刃位",
        "vernacular": "刀鋒上走的命",
        "field": "極端共振場主導",
        "trait": "極端、有魄力、成敗分明",
        "career": "軍警、武術、極限運動",
        "strength": "有魄力、敢冒險",
        "weakness": "可能太衝動、有危險",
    },
}

# 日主祿位對照
DAYMASTER_LU = {"甲": "寅", "乙": "卯", "丙": "巳", "丁": "午", "戊": "巳",
                "己": "午", "庚": "申", "辛": "酉", "壬": "亥", "癸": "子"}

# 日主刃位對照
DAYMASTER_REN = {"甲": "卯", "乙": "寅", "丙": "午", "丁": "巳", "戊": "午",
                 "己": "巳", "庚": "酉", "辛": "申", "壬": "子", "癸": "亥"}


def determine_geju(pillars: Dict[str, str], day_gan: str) -> Dict:
    """
    判定八字格局
    
    格局判定優先順序：
    1. 月支藏干透出天干 → 對應格局
    2. 建祿格、羊刃格檢查
    3. 無明顯格局 → 根據強弱判定
    """
    month_pillar = pillars.get("month", "")
    if len(month_pillar) < 2:
        return {"geju": "未知", "analysis": "月柱資料不完整"}
    
    month_gan, month_zhi = month_pillar[0], month_pillar[1]
    day_wx = GAN_WX.get(day_gan, "木")
    day_yy = GAN_YY.get(day_gan, "陽")
    
    # 取得月支藏干
    month_cang = ZHI_CANG.get(month_zhi, [])
    
    # 檢查透出（月支藏干出現在年干、月干、時干）
    visible_gans = [pillars.get("year", "")[0] if pillars.get("year") else "",
                    month_gan,
                    pillars.get("hour", "")[0] if pillars.get("hour") else ""]
    
    # 判定十神格局
    from wuxing_core import ten_god
    
    detected_geju = None
    for cang_gan, cang_type in month_cang:
        if cang_gan in visible_gans:
            god = ten_god(day_gan, cang_gan)
            if god in ["正官", "七殺", "正印", "偏印", "食神", "傷官", "正財", "偏財"]:
                detected_geju = f"{god}格"
                break
    
    # 檢查建祿格
    if not detected_geju and month_zhi == DAYMASTER_LU.get(day_gan):
        detected_geju = "建祿格"
    
    # 檢查羊刃格
    if not detected_geju and month_zhi == DAYMASTER_REN.get(day_gan):
        detected_geju = "羊刃格"
    
    # 取得格局詳情
    if detected_geju and detected_geju in GEJU_DEFINITIONS:
        geju_info = GEJU_DEFINITIONS[detected_geju]
        return {
            "geju": detected_geju,
            "vernacular": geju_info["vernacular"],
            "field": geju_info["field"],
            "trait": geju_info["trait"],
            "career": geju_info["career"],
            "strength": geju_info["strength"],
            "weakness": geju_info["weakness"],
            "condition": geju_info["condition"],
        }
    
    # 無明顯格局
    return {
        "geju": "雜氣格",
        "vernacular": "混合型的命",
        "field": "多重場疊加",
        "trait": "特徵混合，需要看整體配置",
        "career": "根據其他因素判斷",
        "strength": "適應性強",
        "weakness": "特徵不明顯",
        "condition": "無明顯透出",
    }


# =============================================================================
# B2: 神煞白話翻譯系統
# =============================================================================

SHENSHA_TRANSLATION = {
    # 吉神
    "天乙貴人": {
        "type": "吉",
        "vernacular": "遇難有人救",
        "field": "貴人護持場",
        "effect": "遇困難時容易有人幫忙，化險為夷",
        "modern": "人脈資源、貴人運",
    },
    "文昌貴人": {
        "type": "吉",
        "vernacular": "讀書考試運好",
        "field": "文智增益場",
        "effect": "學習能力強，考試運佳",
        "modern": "學業、證照、文書工作",
    },
    "驛馬": {
        "type": "中",
        "vernacular": "動起來就有運",
        "field": "流動激發場",
        "effect": "適合出差、旅行、變動型工作",
        "modern": "出差、搬遷、跳槽機會",
    },
    "桃花": {
        "type": "中",
        "vernacular": "異性緣好",
        "field": "人際吸引場",
        "effect": "容易吸引異性，人緣佳",
        "modern": "感情機會、人際魅力",
    },
    "華蓋": {
        "type": "中",
        "vernacular": "孤獨的才華",
        "field": "獨立思維場",
        "effect": "有藝術或宗教傾向，喜歡獨處思考",
        "modern": "藝術天份、哲學興趣",
    },
    "將星": {
        "type": "吉",
        "vernacular": "天生領導命",
        "field": "領導核心場",
        "effect": "有領導能力，適合帶領團隊",
        "modern": "管理職、領導角色",
    },
    "天德貴人": {
        "type": "吉",
        "vernacular": "有道德護佑",
        "field": "德行護持場",
        "effect": "行正道則有福報，逢凶化吉",
        "modern": "品德加分、無形保護",
    },
    "月德貴人": {
        "type": "吉",
        "vernacular": "每月都有小確幸",
        "field": "恆定福氣場",
        "effect": "日常生活中常有小幸運",
        "modern": "生活順遂、小確幸多",
    },
    "金輿": {
        "type": "吉",
        "vernacular": "出門有好車坐",
        "field": "交通順遂場",
        "effect": "出行順利，有代步工具運",
        "modern": "車運、出行順利",
    },
    "祿神": {
        "type": "吉",
        "vernacular": "餓不死的命",
        "field": "基本保障場",
        "effect": "基本生活有保障，不會太差",
        "modern": "基本收入、溫飽無虞",
    },
    
    # 凶煞
    "羊刃": {
        "type": "凶",
        "vernacular": "刀口上討生活",
        "field": "極端銳利場",
        "effect": "容易有血光、意外，需要小心",
        "modern": "意外風險、衝動行事",
    },
    "劫煞": {
        "type": "凶",
        "vernacular": "小心被搶被騙",
        "field": "劫奪風險場",
        "effect": "容易有財物損失或被欺騙",
        "modern": "詐騙風險、財物損失",
    },
    "災煞": {
        "type": "凶",
        "vernacular": "意外災害多",
        "field": "災難吸引場",
        "effect": "容易遇到意外或災害",
        "modern": "保險、安全意識",
    },
    "亡神": {
        "type": "凶",
        "vernacular": "精神耗損大",
        "field": "精力虛耗場",
        "effect": "容易精神疲勞、思慮過多",
        "modern": "精神壓力、過度思考",
    },
    "孤辰寡宿": {
        "type": "凶",
        "vernacular": "感情路較孤單",
        "field": "情感隔離場",
        "effect": "感情上可能較晚婚或獨處",
        "modern": "單身傾向、晚婚機會",
    },
    "白虎": {
        "type": "凶",
        "vernacular": "小心血光之災",
        "field": "傷害風險場",
        "effect": "容易有血光、手術、意外傷害",
        "modern": "安全防護、健康檢查",
    },
    "喪門弔客": {
        "type": "凶",
        "vernacular": "容易遇到喪事",
        "field": "哀傷感應場",
        "effect": "可能有親友離世或參加喪禮",
        "modern": "情緒管理、哀傷輔導",
    },
    "官符": {
        "type": "凶",
        "vernacular": "小心官司糾紛",
        "field": "法律風險場",
        "effect": "容易有官司、訴訟、罰單",
        "modern": "法律風險、合約注意",
    },
    "破碎": {
        "type": "凶",
        "vernacular": "東西容易壞",
        "field": "損壞傾向場",
        "effect": "物品容易損壞、計劃容易中斷",
        "modern": "設備維護、計劃備案",
    },
    "天哭天虛": {
        "type": "凶",
        "vernacular": "容易傷心流淚",
        "field": "悲傷共振場",
        "effect": "情緒較敏感，容易傷感",
        "modern": "情緒敏感、需要陪伴",
    },
}


def get_shensha_info(shensha_name: str) -> Optional[Dict]:
    """取得神煞詳細資訊"""
    return SHENSHA_TRANSLATION.get(shensha_name)


def generate_shensha_analysis(shensha_list: List[str]) -> Dict:
    """
    生成神煞綜合分析
    
    Args:
        shensha_list: 命局中的神煞列表
    
    Returns:
        神煞分析結果
    """
    ji_shensha = []
    xiong_shensha = []
    zhong_shensha = []
    
    for name in shensha_list:
        info = SHENSHA_TRANSLATION.get(name)
        if info:
            item = {"name": name, **info}
            if info["type"] == "吉":
                ji_shensha.append(item)
            elif info["type"] == "凶":
                xiong_shensha.append(item)
            else:
                zhong_shensha.append(item)
    
    # 生成總評
    total = len(shensha_list)
    ji_count = len(ji_shensha)
    xiong_count = len(xiong_shensha)
    
    if ji_count > xiong_count * 2:
        summary = "神煞配置偏吉，有較多無形助力"
    elif xiong_count > ji_count * 2:
        summary = "神煞配置偏凶，需要多加留意風險"
    else:
        summary = "神煞配置中和，吉凶參半"
    
    return {
        "total": total,
        "ji_count": ji_count,
        "xiong_count": xiong_count,
        "ji_shensha": ji_shensha,
        "xiong_shensha": xiong_shensha,
        "zhong_shensha": zhong_shensha,
        "summary": summary,
    }


# =============================================================================
# 測試
# =============================================================================

if __name__ == "__main__":
    # 測試五行強弱
    test_pillars = {"year": "甲子", "month": "乙丑", "day": "丙寅", "hour": "丁卯"}
    result = analyze_day_master_strength(test_pillars, "丙")
    print("五行強弱測試:", result["strength"], result["strength_score"])
    
    # 測試格局判定
    geju = determine_geju(test_pillars, "丙")
    print("格局判定:", geju["geju"], geju["vernacular"])
    
    # 測試神煞
    shensha_analysis = generate_shensha_analysis(["天乙貴人", "文昌貴人", "羊刃"])
    print("神煞分析:", shensha_analysis["summary"])
