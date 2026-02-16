"""
紫微流年計算器 ziwei_liunian.py v1.0
====================================
XTF任務：消-B1 | 執行星：理樞（分析）
確定度：★★★★☆（計算公式確定，四化判斷有變數）

核心本質：流年 = 太歲入宮 × 四化飛星

📚 紫微流年計算法則：
1. 流年太歲：當年地支對應十二宮位置
2. 流年四化：當年天干對應四化星
3. 流年宮位：各宮受到太歲影響
4. 流年星曜：流年四化飛入各宮

⚠️ XTF8 認識論聲明：
- 太歲位置計算：★★★★★（確定）
- 流年四化定位：★★★★☆（公式確定）
- 吉凶傾向判斷：★★★☆☆（經驗統計）
"""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime

# 天干
GAN = ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"]

# 地支
ZHI = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]

# 十二宮名稱
GONG_NAMES = ["命宮", "兄弟", "夫妻", "子女", "財帛", "疾厄",
              "遷移", "僕役", "官祿", "田宅", "福德", "父母"]

# 流年四化表（年干→化祿/化權/化科/化忌）
LIUNIAN_SIHUA = {
    "甲": {"祿": "廉貞", "權": "破軍", "科": "武曲", "忌": "太陽"},
    "乙": {"祿": "天機", "權": "天梁", "科": "紫微", "忌": "太陰"},
    "丙": {"祿": "天同", "權": "天機", "科": "文昌", "忌": "廉貞"},
    "丁": {"祿": "太陰", "權": "天同", "科": "天機", "忌": "巨門"},
    "戊": {"祿": "貪狼", "權": "太陰", "科": "右弼", "忌": "天機"},
    "己": {"祿": "武曲", "權": "貪狼", "科": "天梁", "忌": "文曲"},
    "庚": {"祿": "太陽", "權": "武曲", "科": "太陰", "忌": "天同"},
    "辛": {"祿": "巨門", "權": "太陽", "科": "文曲", "忌": "文昌"},
    "壬": {"祿": "天梁", "權": "紫微", "科": "左輔", "忌": "武曲"},
    "癸": {"祿": "破軍", "權": "巨門", "科": "太陰", "忌": "貪狼"},
}

# 四化意義
SIHUA_MEANING = {
    "祿": {"type": "吉", "meaning": "收穫、機會、增益", "advice": "把握機會，積極行動"},
    "權": {"type": "吉", "meaning": "權力、掌控、主導", "advice": "發揮領導力，積極爭取"},
    "科": {"type": "吉", "meaning": "名聲、貴人、考試", "advice": "注重形象，把握學習"},
    "忌": {"type": "凶", "meaning": "阻礙、執著、糾結", "advice": "謹慎行事，避免執念"},
}

# 宮位主題
GONG_THEMES = {
    "命宮": "自我、整體運勢",
    "兄弟": "兄弟姐妹、平輩關係",
    "夫妻": "感情、婚姻、合作",
    "子女": "子女、創作、桃花",
    "財帛": "財運、收入",
    "疾厄": "健康、身體",
    "遷移": "外出、變動、貴人",
    "僕役": "朋友、下屬、人際",
    "官祿": "事業、工作",
    "田宅": "家庭、不動產",
    "福德": "精神、興趣、享受",
    "父母": "長輩、文書、學業",
}


def get_year_ganzhi(year: int) -> Tuple[str, str]:
    """取得年干支"""
    gan_idx = (year - 4) % 10
    zhi_idx = (year - 4) % 12
    return GAN[gan_idx], ZHI[zhi_idx]


def get_taisui_gong(year_zhi: str, ming_gong_zhi: str) -> str:
    """
    計算流年太歲所在宮位
    太歲即流年地支，對應到命盤上的宮位
    """
    # 找到太歲地支在十二宮的位置
    # 簡化：直接用地支索引對應宮位
    zhi_idx = ZHI.index(year_zhi)
    ming_idx = ZHI.index(ming_gong_zhi) if ming_gong_zhi in ZHI else 0
    
    # 計算相對位置
    relative_pos = (zhi_idx - ming_idx) % 12
    return GONG_NAMES[relative_pos]


@dataclass
class LiunianSihuaInfo:
    """流年四化資訊"""
    hua_type: str      # 祿/權/科/忌
    star: str          # 星曜
    meaning: str       # 意義
    advice: str        # 建議
    is_ji: bool        # 是否吉


@dataclass
class LiunianGongInfo:
    """流年宮位資訊"""
    gong_name: str     # 宮位名稱
    theme: str         # 主題
    sihua_in: List[str]  # 飛入的四化
    tendency: str      # 吉凶傾向
    advice: str        # 建議


@dataclass
class ZiweiLiunianResult:
    """紫微流年分析結果"""
    year: int
    year_gan: str
    year_zhi: str
    taisui_gong: str
    sihua: Dict[str, LiunianSihuaInfo]
    gong_analysis: List[LiunianGongInfo]
    overall: str
    key_points: List[str]


class ZiweiLiunianCalculator:
    """紫微流年計算器"""
    
    def __init__(self, ming_gong_zhi: str, gongs: List[Dict] = None):
        """
        ming_gong_zhi: 命宮地支
        gongs: 十二宮資料（含星曜）
        """
        self.ming_gong_zhi = ming_gong_zhi
        self.gongs = gongs or []
        
        # 建立星曜→宮位映射
        self.star_to_gong = {}
        if gongs:
            for i, gong in enumerate(gongs):
                for star in gong.get("main_stars", []) + gong.get("aux_stars", []):
                    self.star_to_gong[star] = GONG_NAMES[i]
    
    def analyze_year(self, year: int) -> ZiweiLiunianResult:
        """分析特定流年"""
        year_gan, year_zhi = get_year_ganzhi(year)
        
        # 太歲宮位
        taisui_gong = get_taisui_gong(year_zhi, self.ming_gong_zhi)
        
        # 流年四化
        sihua_config = LIUNIAN_SIHUA.get(year_gan, {})
        sihua = {}
        for hua_type, star in sihua_config.items():
            meaning_info = SIHUA_MEANING.get(hua_type, {})
            sihua[hua_type] = LiunianSihuaInfo(
                hua_type=hua_type,
                star=star,
                meaning=meaning_info.get("meaning", ""),
                advice=meaning_info.get("advice", ""),
                is_ji=(meaning_info.get("type") == "吉"),
            )
        
        # 分析各宮位受到的影響
        gong_sihua_map = {name: [] for name in GONG_NAMES}
        
        for hua_type, star in sihua_config.items():
            target_gong = self.star_to_gong.get(star, "")
            if target_gong:
                gong_sihua_map[target_gong].append(hua_type)
        
        # 太歲所在宮位特別標記
        gong_analysis = []
        for gong_name in GONG_NAMES:
            sihua_in = gong_sihua_map.get(gong_name, [])
            theme = GONG_THEMES.get(gong_name, "")
            
            # 判斷吉凶
            ji_count = sum(1 for s in sihua_in if s in ["祿", "權", "科"])
            xiong_count = sum(1 for s in sihua_in if s == "忌")
            
            if gong_name == taisui_gong:
                tendency = "重點關注（太歲所在）"
                advice = f"今年{theme}是主要課題"
            elif ji_count > xiong_count:
                tendency = "有利"
                advice = f"{theme}方面有正面能量"
            elif xiong_count > ji_count:
                tendency = "需注意"
                advice = f"{theme}方面宜謹慎"
            else:
                tendency = "平穩"
                advice = f"{theme}方面維持現狀"
            
            gong_analysis.append(LiunianGongInfo(
                gong_name=gong_name,
                theme=theme,
                sihua_in=sihua_in,
                tendency=tendency,
                advice=advice,
            ))
        
        # 整體判斷
        total_ji = sum(len([s for s in g.sihua_in if s in ["祿", "權", "科"]]) for g in gong_analysis)
        total_xiong = sum(len([s for s in g.sihua_in if s == "忌"]) for g in gong_analysis)
        
        if total_ji > total_xiong:
            overall = "整體有利"
        elif total_xiong > total_ji:
            overall = "整體需謹慎"
        else:
            overall = "整體平穩"
        
        # 關鍵提示
        key_points = []
        key_points.append(f"流年太歲在{taisui_gong}，{GONG_THEMES.get(taisui_gong, '')}是今年重點")
        
        for hua_type, info in sihua.items():
            target_gong = self.star_to_gong.get(info.star, "未知宮位")
            if hua_type == "祿":
                key_points.append(f"化祿飛{target_gong}：{GONG_THEMES.get(target_gong, '')}有收穫機會")
            elif hua_type == "忌":
                key_points.append(f"化忌飛{target_gong}：{GONG_THEMES.get(target_gong, '')}宜謹慎")
        
        return ZiweiLiunianResult(
            year=year,
            year_gan=year_gan,
            year_zhi=year_zhi,
            taisui_gong=taisui_gong,
            sihua=sihua,
            gong_analysis=gong_analysis,
            overall=overall,
            key_points=key_points,
        )


def analyze_ziwei_liunian(
    year: int,
    ming_gong_zhi: str,
    gongs: List[Dict] = None,
) -> Dict:
    """便捷函數：分析紫微流年"""
    calculator = ZiweiLiunianCalculator(ming_gong_zhi, gongs)
    result = calculator.analyze_year(year)
    
    return {
        "year": result.year,
        "year_gan": result.year_gan,
        "year_zhi": result.year_zhi,
        "taisui_gong": result.taisui_gong,
        "sihua": {
            k: {
                "star": v.star,
                "meaning": v.meaning,
                "advice": v.advice,
            }
            for k, v in result.sihua.items()
        },
        "gong_analysis": [
            {
                "gong_name": g.gong_name,
                "theme": g.theme,
                "sihua_in": g.sihua_in,
                "tendency": g.tendency,
                "advice": g.advice,
            }
            for g in result.gong_analysis
        ],
        "overall": result.overall,
        "key_points": result.key_points,
    }


def generate_ziwei_liunian_report(result: Dict) -> str:
    """生成紫微流年報告"""
    report = f"""
【{result['year']}年紫微流年分析】

流年干支：{result['year_gan']}{result['year_zhi']}
太歲宮位：{result['taisui_gong']}
整體運勢：{result['overall']}

【流年四化】
"""
    
    for hua_type, info in result['sihua'].items():
        emoji = "🟢" if hua_type != "忌" else "🔴"
        report += f"  {emoji} 化{hua_type}：{info['star']} — {info['meaning']}\n"
    
    report += "\n【關鍵提示】\n"
    for point in result['key_points']:
        report += f"  • {point}\n"
    
    report += "\n【宮位影響速覽】\n"
    for gong in result['gong_analysis']:
        if gong['sihua_in']:
            sihua_str = "、".join([f"化{s}" for s in gong['sihua_in']])
            report += f"  {gong['gong_name']}：{sihua_str}（{gong['tendency']}）\n"
    
    report += """
【XTF8 確定度標註】
★★★★★ 太歲位置、四化計算（可驗證）
★★★☆☆ 吉凶傾向判斷（經驗統計）
★★☆☆☆ 具體事件預測（僅供參考）

提醒：紫微流年是「能量背景參考」，不是「命運劇本」。
"""
    
    return report


if __name__ == "__main__":
    # 測試
    # 假設命宮在午宮
    result = analyze_ziwei_liunian(
        year=2026,
        ming_gong_zhi="午",
        gongs=[
            {"main_stars": ["天相"]},  # 命宮
            {"main_stars": ["天梁"]},  # 兄弟
            {"main_stars": ["七殺"]},  # 夫妻
            {"main_stars": []},        # 子女
            {"main_stars": ["廉貞", "天府"]},  # 財帛
            {"main_stars": []},        # 疾厄
            {"main_stars": ["破軍"]},  # 遷移
            {"main_stars": []},        # 僕役
            {"main_stars": ["紫微", "貪狼"]},  # 官祿
            {"main_stars": ["天機", "太陰"]},  # 田宅
            {"main_stars": ["天同", "巨門"]},  # 福德
            {"main_stars": ["太陽", "武曲"]},  # 父母
        ]
    )
    
    print(generate_ziwei_liunian_report(result))
