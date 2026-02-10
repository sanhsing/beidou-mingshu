#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
mingshu_api_enhanced_v1.py - 北斗命數增強API層 v1.0
===================================================
北斗七星文創 × 織明 × 澄韻 × 流祇 × 理樞

自動將所有 API 輸出增強為：
- raw: 原始數據
- 白話: 一般人能懂
- 場論: 現代科學語言
- 建議: 可操作行動

XTF⁸ + XTFS + @11star 協作
T層(翻譯) + F層(場論) + X層(執行) 整合

📚 知識點：
    「API 增強 = 數據 + 智慧」
    「每個輸出都是一次教育機會」
"""

from typing import Dict, List, Optional, Any, Union
from datetime import datetime
from functools import wraps
import json

# 導入翻譯資料庫
try:
    from mingshu_translation_db_v1 import TranslationDB, TranslationEntry
    TRANSLATION_AVAILABLE = True
except ImportError:
    TRANSLATION_AVAILABLE = False


# =============================================================================
# 輸出增強器
# =============================================================================

class OutputEnhancer:
    """
    輸出增強器
    
    自動為 API 輸出添加白話、場論、建議
    """
    
    VERSION = "1.0.0"
    
    def __init__(self):
        self.enabled = TRANSLATION_AVAILABLE
    
    def enhance(self, data: Dict, context: str = "") -> Dict:
        """
        增強輸出
        
        Args:
            data: 原始數據
            context: 上下文（如 "八字", "紫微", "奇門"）
        
        Returns:
            增強後的數據，包含 raw, 白話, 場論, 建議
        """
        if not self.enabled:
            return {"raw": data, "note": "翻譯模組未載入"}
        
        enhanced = {
            "raw": data,
            "interpretations": [],
            "summary": "",
            "advice": []
        }
        
        # 根據上下文選擇增強方法
        if context == "八字":
            enhanced = self._enhance_bazi(data)
        elif context == "紫微":
            enhanced = self._enhance_ziwei(data)
        elif context == "四化":
            enhanced = self._enhance_sihua(data)
        elif context == "奇門":
            enhanced = self._enhance_qimen(data)
        elif context == "六壬":
            enhanced = self._enhance_liuren(data)
        elif context == "風水":
            enhanced = self._enhance_fengshui(data)
        else:
            # 通用增強
            enhanced = self._enhance_generic(data)
        
        return enhanced
    
    def _enhance_bazi(self, data: Dict) -> Dict:
        """增強八字輸出"""
        result = {
            "raw": data,
            "四柱解讀": [],
            "十神解讀": [],
            "綜合建議": []
        }
        
        # 解讀天干
        for pillar in ["年", "月", "日", "時"]:
            gan_key = f"{pillar}干"
            zhi_key = f"{pillar}支"
            
            if gan_key in data:
                gan = data[gan_key]
                entry = TranslationDB.get(gan, "天干")
                if entry:
                    result["四柱解讀"].append({
                        "柱": pillar,
                        "天干": gan,
                        "一句話": entry.one_line,
                        "白話": entry.white_speak,
                        "場論": entry.field_theory
                    })
            
            if zhi_key in data:
                zhi = data[zhi_key]
                entry = TranslationDB.get(zhi, "地支")
                if entry:
                    result["四柱解讀"].append({
                        "柱": pillar,
                        "地支": zhi,
                        "一句話": entry.one_line,
                        "白話": entry.white_speak,
                        "場論": entry.field_theory
                    })
        
        # 解讀十神
        if "十神" in data:
            for shishen, info in data["十神"].items():
                entry = TranslationDB.get(shishen, "十神")
                if entry:
                    result["十神解讀"].append({
                        "十神": shishen,
                        "位置": info if isinstance(info, str) else "",
                        "一句話": entry.one_line,
                        "白話": entry.white_speak,
                        "場論": entry.field_theory,
                        "建議": entry.advice
                    })
        
        # 綜合建議
        result["綜合建議"] = self._generate_bazi_advice(data)
        
        return result
    
    def _enhance_ziwei(self, data: Dict) -> Dict:
        """增強紫微輸出"""
        result = {
            "raw": data,
            "命宮主星解讀": {},
            "各宮解讀": [],
            "四化解讀": [],
            "綜合建議": []
        }
        
        # 解讀命宮主星
        if "命宮主星" in data:
            star = data["命宮主星"]
            entry = TranslationDB.get(star, "紫微主星")
            if entry:
                result["命宮主星解讀"] = {
                    "星曜": star,
                    "一句話": entry.one_line,
                    "白話": entry.white_speak,
                    "場論": entry.field_theory,
                    "建議": entry.advice
                }
        
        # 解讀各宮
        if "十二宮" in data:
            for gong, info in data["十二宮"].items():
                gong_entry = TranslationDB.get(gong, "十二宮")
                gong_interp = {
                    "宮位": gong,
                    "一句話": gong_entry.one_line if gong_entry else "",
                    "管轄": gong_entry.white_speak if gong_entry else "",
                    "星曜": []
                }
                
                # 解讀宮內星曜
                if isinstance(info, dict) and "主星" in info:
                    for star in info["主星"]:
                        star_entry = TranslationDB.get(star, "紫微主星")
                        if star_entry:
                            gong_interp["星曜"].append({
                                "星": star,
                                "一句話": star_entry.one_line,
                                "場論": star_entry.field_theory
                            })
                
                result["各宮解讀"].append(gong_interp)
        
        # 解讀四化
        if "四化" in data:
            for sihua_type, star in data["四化"].items():
                sihua_entry = TranslationDB.get(sihua_type, "四化")
                star_entry = TranslationDB.get(star, "紫微主星")
                
                # 找出星曜所在宮位
                gong = self._find_star_gong(data, star)
                gong_entry = TranslationDB.get(gong, "十二宮") if gong else None
                
                result["四化解讀"].append({
                    "四化": sihua_type,
                    "星曜": star,
                    "宮位": gong or "未知",
                    "四化意義": {
                        "一句話": sihua_entry.one_line if sihua_entry else "",
                        "白話": sihua_entry.white_speak if sihua_entry else "",
                        "場論": sihua_entry.field_theory if sihua_entry else "",
                        "建議": sihua_entry.advice if sihua_entry else ""
                    },
                    "影響領域": gong_entry.white_speak if gong_entry else "",
                    "綜合解讀": self._format_sihua_interpretation(
                        sihua_type, star, gong, sihua_entry, star_entry, gong_entry
                    )
                })
        
        return result
    
    def _enhance_sihua(self, data: Dict) -> Dict:
        """增強四化輸出"""
        result = {
            "raw": data,
            "四化詳解": []
        }
        
        sihua_list = data.get("四化", [])
        if isinstance(sihua_list, dict):
            sihua_list = [{"type": k, "star": v} for k, v in sihua_list.items()]
        
        for item in sihua_list:
            sihua_type = item.get("type") or item.get("四化")
            star = item.get("star") or item.get("星曜")
            gong = item.get("gong") or item.get("宮位")
            
            sihua_entry = TranslationDB.get(sihua_type, "四化")
            star_entry = TranslationDB.get(star, "紫微主星")
            gong_entry = TranslationDB.get(gong, "十二宮") if gong else None
            
            interp = {
                "四化": sihua_type,
                "星曜": star,
                "宮位": gong,
                "完整解讀": self._format_sihua_full(
                    sihua_type, star, gong, sihua_entry, star_entry, gong_entry
                )
            }
            
            result["四化詳解"].append(interp)
        
        return result
    
    def _enhance_qimen(self, data: Dict) -> Dict:
        """增強奇門輸出"""
        result = {
            "raw": data,
            "格局說明": "",
            "值使門解讀": {},
            "九宮解讀": [],
            "行動建議": []
        }
        
        # 格局說明
        dun_type = "陽遁" if data.get("yang_dun") else "陰遁"
        ju = data.get("ju_number", "?")
        result["格局說明"] = f"{dun_type}{ju}局"
        
        # 值使門
        if "duty_men" in data:
            men = data["duty_men"]
            entry = TranslationDB.get(men, "八門")
            if entry:
                result["值使門解讀"] = {
                    "門": men,
                    "吉凶": "吉" if men in ["開門", "休門", "生門"] else "凶" if men in ["傷門", "死門", "驚門"] else "中",
                    "一句話": entry.one_line,
                    "白話": entry.white_speak,
                    "場論": entry.field_theory,
                    "建議": entry.advice
                }
        
        # 九宮解讀
        if "gongs" in data:
            for gong_data in data["gongs"]:
                gong_num = gong_data.get("position", gong_data.get("宮"))
                men = gong_data.get("men", gong_data.get("門"))
                xing = gong_data.get("star", gong_data.get("星"))
                
                men_entry = TranslationDB.get(men, "八門") if men else None
                xing_entry = TranslationDB.get(xing, "九星") if xing else None
                
                result["九宮解讀"].append({
                    "宮位": gong_num,
                    "八門": {
                        "名稱": men,
                        "一句話": men_entry.one_line if men_entry else "",
                        "場論": men_entry.field_theory if men_entry else ""
                    } if men else None,
                    "九星": {
                        "名稱": xing,
                        "一句話": xing_entry.one_line if xing_entry else "",
                        "場論": xing_entry.field_theory if xing_entry else ""
                    } if xing else None
                })
        
        # 行動建議
        result["行動建議"] = self._generate_qimen_advice(data)
        
        return result
    
    def _enhance_liuren(self, data: Dict) -> Dict:
        """增強六壬輸出"""
        result = {
            "raw": data,
            "四課解讀": [],
            "三傳解讀": [],
            "綜合判斷": ""
        }
        
        # 四課解讀
        if "sike" in data:
            for i, ke in enumerate(data["sike"], 1):
                shenjiang = ke.get("shenjiang_name", ke.get("神將"))
                entry = TranslationDB.get(shenjiang, "十二神將") if shenjiang else None
                
                result["四課解讀"].append({
                    "課數": f"第{i}課",
                    "神將": shenjiang,
                    "吉凶": entry.keywords[0] if entry and entry.keywords else "",
                    "一句話": entry.one_line if entry else "",
                    "白話": entry.white_speak if entry else "",
                    "場論": entry.field_theory if entry else ""
                })
        
        # 三傳解讀
        if "sanchuan" in data:
            chuan_names = ["初傳", "中傳", "末傳"]
            for i, chuan in enumerate(data["sanchuan"]):
                shenjiang = chuan.get("shenjiang_name", chuan.get("神將"))
                entry = TranslationDB.get(shenjiang, "十二神將") if shenjiang else None
                
                result["三傳解讀"].append({
                    "傳": chuan_names[i] if i < 3 else f"第{i+1}傳",
                    "神將": shenjiang,
                    "一句話": entry.one_line if entry else "",
                    "意義": entry.white_speak if entry else ""
                })
        
        # 綜合判斷
        result["綜合判斷"] = self._generate_liuren_judgment(data)
        
        return result
    
    def _enhance_fengshui(self, data: Dict) -> Dict:
        """增強風水輸出"""
        result = {
            "raw": data,
            "坐向解讀": {},
            "當運解讀": {},
            "綜合建議": []
        }
        
        # 坐向解讀
        if "sitting" in data:
            shan = data["sitting"]
            # 這裡可以添加二十四山的翻譯
            result["坐向解讀"] = {
                "坐山": shan,
                "說明": f"房屋坐{shan}山"
            }
        
        if "facing" in data:
            result["坐向解讀"]["朝向"] = data["facing"]
        
        # 當運解讀
        yun = data.get("current_yun", 9)
        yun_entry = TranslationDB.get(yun, "三元九運") if isinstance(yun, int) else None
        if yun_entry:
            result["當運解讀"] = {
                "運數": yun,
                "一句話": yun_entry.one_line,
                "白話": yun_entry.white_speak,
                "場論": yun_entry.field_theory,
                "建議": yun_entry.advice
            }
        
        return result
    
    def _enhance_generic(self, data: Dict) -> Dict:
        """通用增強"""
        result = {
            "raw": data,
            "interpretations": []
        }
        
        # 遍歷數據，嘗試翻譯每個術語
        def traverse_and_translate(obj, prefix=""):
            if isinstance(obj, dict):
                for k, v in obj.items():
                    entry = TranslationDB.get(str(k))
                    if entry:
                        result["interpretations"].append({
                            "term": k,
                            "path": prefix + k,
                            "一句話": entry.one_line,
                            "白話": entry.white_speak,
                            "場論": entry.field_theory
                        })
                    traverse_and_translate(v, prefix + k + ".")
            elif isinstance(obj, list):
                for i, item in enumerate(obj):
                    traverse_and_translate(item, prefix + f"[{i}].")
            elif isinstance(obj, str):
                entry = TranslationDB.get(obj)
                if entry:
                    result["interpretations"].append({
                        "term": obj,
                        "path": prefix.rstrip("."),
                        "一句話": entry.one_line,
                        "白話": entry.white_speak,
                        "場論": entry.field_theory
                    })
        
        traverse_and_translate(data)
        return result
    
    # ===== 輔助方法 =====
    
    def _find_star_gong(self, data: Dict, star: str) -> Optional[str]:
        """找出星曜所在宮位"""
        if "星曜宮位" in data:
            return data["星曜宮位"].get(star)
        if "十二宮" in data:
            for gong, info in data["十二宮"].items():
                if isinstance(info, dict) and star in info.get("主星", []):
                    return gong
        return None
    
    def _format_sihua_interpretation(self, sihua_type, star, gong, 
                                     sihua_entry, star_entry, gong_entry) -> str:
        """格式化四化解讀"""
        lines = [f"【{star}{sihua_type}入{gong or '?'}】"]
        
        if sihua_entry:
            lines.append(f"✦ {sihua_entry.one_line}")
            lines.append(f"✦ 白話：{sihua_entry.white_speak}")
        
        if gong_entry:
            lines.append(f"✦ 影響：{gong_entry.white_speak}")
        
        if sihua_entry:
            lines.append(f"✦ 場論：{sihua_entry.field_theory}")
            lines.append(f"✦ 建議：{sihua_entry.advice}")
        
        return "\n".join(lines)
    
    def _format_sihua_full(self, sihua_type, star, gong,
                          sihua_entry, star_entry, gong_entry) -> Dict:
        """完整四化解讀"""
        return {
            "標題": f"{star}{sihua_type}入{gong or '?'}",
            "一句話": sihua_entry.one_line if sihua_entry else "",
            "白話": sihua_entry.white_speak if sihua_entry else "",
            "影響領域": gong_entry.white_speak if gong_entry else "",
            "場論": sihua_entry.field_theory if sihua_entry else "",
            "建議": sihua_entry.advice if sihua_entry else "",
            "星曜特質": star_entry.one_line if star_entry else ""
        }
    
    def _generate_bazi_advice(self, data: Dict) -> List[str]:
        """生成八字綜合建議"""
        advice = []
        
        # 根據日主生成建議
        day_gan = data.get("日干")
        if day_gan:
            entry = TranslationDB.get(day_gan, "天干")
            if entry:
                advice.append(f"日主{day_gan}：{entry.advice}")
        
        return advice
    
    def _generate_qimen_advice(self, data: Dict) -> List[str]:
        """生成奇門行動建議"""
        advice = []
        
        duty_men = data.get("duty_men")
        if duty_men:
            entry = TranslationDB.get(duty_men, "八門")
            if entry:
                advice.append(f"今日值使{duty_men}：{entry.advice}")
        
        return advice
    
    def _generate_liuren_judgment(self, data: Dict) -> str:
        """生成六壬綜合判斷"""
        judgments = []
        
        # 分析四課吉凶
        if "sike" in data:
            jis = 0
            xiongs = 0
            for ke in data["sike"]:
                shenjiang = ke.get("shenjiang_name", ke.get("神將"))
                if shenjiang in ["貴人", "青龍", "六合", "太常", "太陰"]:
                    jis += 1
                elif shenjiang in ["白虎", "玄武", "騰蛇", "勾陳", "天空"]:
                    xiongs += 1
            
            if jis > xiongs:
                judgments.append("四課吉神多於凶神，整體形勢有利")
            elif xiongs > jis:
                judgments.append("四課凶神多於吉神，需要謹慎行事")
            else:
                judgments.append("四課吉凶參半，需要審時度勢")
        
        return "。".join(judgments) if judgments else "請結合具體情況判斷"


# =============================================================================
# API 裝飾器
# =============================================================================

def enhance_output(context: str = ""):
    """
    API 輸出增強裝飾器
    
    使用方式:
        @enhance_output("八字")
        def api_bazi():
            return raw_data
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            enhancer = OutputEnhancer()
            return enhancer.enhance(result, context)
        return wrapper
    return decorator


# =============================================================================
# 增強版 API 類
# =============================================================================

class MingshuEnhancedAPI:
    """
    北斗命數增強版 API
    
    所有輸出都自動附帶：白話 + 場論 + 建議
    """
    
    VERSION = "1.0.0"
    
    def __init__(self):
        self.enhancer = OutputEnhancer()
    
    def analyze_bazi(self, year: int, month: int, day: int, hour: int, 
                     gender: str = "male") -> Dict:
        """八字分析（增強版）"""
        # 模擬原始數據（實際應調用 mingshu_engine）
        raw = {
            "年干": "癸", "年支": "丑",
            "月干": "甲", "月支": "寅",
            "日干": "丙", "日支": "午",
            "時干": "庚", "時支": "申",
            "十神": {
                "比肩": "丙火",
                "食神": "戊土",
                "偏財": "庚金"
            }
        }
        return self.enhancer.enhance(raw, "八字")
    
    def analyze_ziwei(self, year: int, month: int, day: int, hour: int,
                      gender: str = "male") -> Dict:
        """紫微分析（增強版）"""
        raw = {
            "命宮主星": "紫微",
            "四化": {
                "化祿": "破軍",
                "化權": "巨門",
                "化科": "太陰",
                "化忌": "貪狼"
            },
            "十二宮": {
                "命宮": {"主星": ["紫微", "天府"]},
                "財帛宮": {"主星": ["太陰"]},
                "官祿宮": {"主星": ["巨門"]}
            }
        }
        return self.enhancer.enhance(raw, "紫微")
    
    def analyze_sihua(self, year_gan: str, star_positions: Dict = None) -> Dict:
        """四化分析（增強版）"""
        # 癸年四化
        raw = {
            "四化": [
                {"type": "化祿", "star": "破軍", "gong": "命宮"},
                {"type": "化權", "star": "巨門", "gong": "官祿宮"},
                {"type": "化科", "star": "太陰", "gong": "財帛宮"},
                {"type": "化忌", "star": "貪狼", "gong": "夫妻宮"}
            ]
        }
        return self.enhancer.enhance(raw, "四化")
    
    def analyze_qimen(self, dt: datetime = None) -> Dict:
        """奇門分析（增強版）"""
        raw = {
            "yang_dun": True,
            "ju_number": 2,
            "duty_men": "開門",
            "gongs": [
                {"position": 1, "men": "休門", "star": "天蓬"},
                {"position": 2, "men": "生門", "star": "天芮"},
                {"position": 3, "men": "傷門", "star": "天衝"},
            ]
        }
        return self.enhancer.enhance(raw, "奇門")
    
    def analyze_liuren(self, day_gan: str, day_zhi: str, 
                       hour_zhi: str, is_day: bool = True) -> Dict:
        """六壬分析（增強版）"""
        raw = {
            "sike": [
                {"shenjiang_name": "貴人"},
                {"shenjiang_name": "騰蛇"},
                {"shenjiang_name": "青龍"},
                {"shenjiang_name": "太常"}
            ],
            "sanchuan": [
                {"shenjiang_name": "貴人"},
                {"shenjiang_name": "六合"},
                {"shenjiang_name": "青龍"}
            ]
        }
        return self.enhancer.enhance(raw, "六壬")
    
    def analyze_fengshui(self, degree: float, year: int = None) -> Dict:
        """風水分析（增強版）"""
        raw = {
            "sitting": "子",
            "facing": "午",
            "current_yun": 9
        }
        return self.enhancer.enhance(raw, "風水")


# =============================================================================
# CLI 測試
# =============================================================================

def main():
    print("=" * 70)
    print("北斗命數增強API v1.0")
    print("每個輸出都包含：白話 + 場論 + 建議")
    print("@11star: 織明 × 澄韻 × 流祇 × 理樞")
    print("=" * 70)
    
    api = MingshuEnhancedAPI()
    
    # 測試四化
    print("\n【四化分析測試】癸年四化")
    print("-" * 70)
    result = api.analyze_sihua("癸")
    
    for sihua in result.get("四化詳解", []):
        full = sihua.get("完整解讀", {})
        print(f"\n【{full.get('標題', '')}】")
        print(f"✦ {full.get('一句話', '')}")
        print(f"✦ 白話：{full.get('白話', '')}")
        print(f"✦ 影響：{full.get('影響領域', '')}")
        print(f"✦ 場論：{full.get('場論', '')}")
        print(f"✦ 建議：{full.get('建議', '')}")
    
    # 測試奇門
    print("\n" + "=" * 70)
    print("【奇門分析測試】")
    print("-" * 70)
    result = api.analyze_qimen()
    
    print(f"格局：{result.get('格局說明', '')}")
    
    duty = result.get("值使門解讀", {})
    if duty:
        print(f"\n【值使門：{duty.get('門', '')}】（{duty.get('吉凶', '')}）")
        print(f"✦ {duty.get('一句話', '')}")
        print(f"✦ 白話：{duty.get('白話', '')}")
        print(f"✦ 場論：{duty.get('場論', '')}")
        print(f"✦ {duty.get('建議', '')}")
    
    # 測試六壬
    print("\n" + "=" * 70)
    print("【六壬分析測試】")
    print("-" * 70)
    result = api.analyze_liuren("癸", "丑", "卯")
    
    print("【四課解讀】")
    for ke in result.get("四課解讀", []):
        print(f"  {ke.get('課數', '')}: {ke.get('神將', '')} - {ke.get('一句話', '')}")
    
    print(f"\n【綜合判斷】{result.get('綜合判斷', '')}")
    
    # 統計
    print("\n" + "=" * 70)
    with open(__file__, 'r') as f:
        lines = len(f.read().split('\n'))
    print(f"模組行數: {lines} 行")
    print("翻譯模組: {'可用' if TRANSLATION_AVAILABLE else '未載入'}")
    print("=" * 70)


if __name__ == "__main__":
    main()
