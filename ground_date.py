#!/usr/bin/env python3
"""
ground_date.py - 開工動土擇日擇時模組
版本：v2.0.0

═══════════════════════════════════════════════════════════════════════
v2.0 更新：整合業主八字配合
  • 業主完整八字分析
  • 日課與業主用神配合
  • 坐向五行配合
═══════════════════════════════════════════════════════════════════════

開工動土專用維度（基於 date_base.py 10維度）：
  D6  動土宜忌     土王用事/天火地火
  D7  業主八字     用神配合/日課配合
  
動土專用神煞：
  吉神：天德/月德/福德/驛馬/天馬
  凶神：土府/土瘟/土忌/天火/地火/土王用事
═══════════════════════════════════════════════════════════════════════

PYLIB 依賴：date_base.py, bazi_base.py
XTF8 層級：L0-L4
@11星協作：@織明(統籌) @理樞(分析) @澄書(記錄) @流祇(連結)
"""

from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, field
from datetime import date, timedelta
from date_base import (
    DateSelector, DateCandidate, DateScore, DATE_WEIGHTS,
    TIANGAN, DIZHI, SHENGXIAO, DIZHI_CHONG, DIZHI_LIUHE, DIZHI_SANHE,
    TIANGAN_WX, DIZHI_WX, FANGWEI,
    calc_huangdao, calc_jianchu, calc_xiu, calc_shensha, calc_chongsha,
    calc_jishi, calc_yijing, check_avoid, get_ganzhi_from_date,
    JIANCHU, ERSHIBA_XIU, XIU_ORDER,
    get_full_rike, FullRike, calc_shichen_ganzhi
)
from bazi_base import (
    BaziChart, BaziAnalyzer, analyze_bazi, analyze_hehun, calc_rike_score,
    RikePeihe, HeHunResult, get_shengxiao, check_dizhi_relation
)

# ════════════════════════════════════════════════════════════════════
# L0: 開工動土專用常量
# ════════════════════════════════════════════════════════════════════

# 動土吉神
GROUND_JI_SHEN = {
    "天德": {"score": 20, "desc": "逢凶化吉"},
    "月德": {"score": 18, "desc": "諸事吉利"},
    "福德": {"score": 15, "desc": "福氣臨門"},
    "驛馬": {"score": 12, "desc": "動工順利"},
    "天馬": {"score": 12, "desc": "進展迅速"},
    "天恩": {"score": 10, "desc": "得天之恩"},
    "月恩": {"score": 8, "desc": "得月之恩"},
    "四相": {"score": 10, "desc": "四方吉利"},
    "時德": {"score": 8, "desc": "時來運轉"},
    "三合": {"score": 12, "desc": "三合吉慶"},
    "六合": {"score": 10, "desc": "六合和順"},
    "天倉": {"score": 10, "desc": "財源廣進"},
    "母倉": {"score": 8, "desc": "倉儲豐盈"},
}

# 動土凶神
GROUND_XIONG_SHEN = {
    "土府": {"score": -30, "desc": "動土大忌"},
    "土瘟": {"score": -25, "desc": "土中瘟疫"},
    "土忌": {"score": -20, "desc": "土氣不利"},
    "天火": {"score": -25, "desc": "火災之象"},
    "地火": {"score": -25, "desc": "地下火患"},
    "土王用事": {"score": -35, "desc": "土旺不宜動"},
    "大煞": {"score": -20, "desc": "大凶之象"},
    "小煞": {"score": -15, "desc": "小凶之象"},
    "月破": {"score": -35, "desc": "月破大凶"},
    "歲破": {"score": -35, "desc": "歲破大凶"},
    "劫煞": {"score": -20, "desc": "劫難之象"},
    "災煞": {"score": -20, "desc": "災禍之象"},
    "五墓": {"score": -18, "desc": "五墓之日"},
    "九坎": {"score": -15, "desc": "坎坷之象"},
    "九焦": {"score": -15, "desc": "焦慮之象"},
}

# 土王用事（四季末18天）
# 春季：立夏前18天（約4/17-5/4）
# 夏季：立秋前18天（約7/20-8/6）
# 秋季：立冬前18天（約10/20-11/6）
# 冬季：立春前18天（約1/17-2/3）
TUWANG_YONGSHI = {
    # 簡化：用農曆月份近似
    "春": [(4, 17), (5, 4)],   # 約農曆三月末
    "夏": [(7, 20), (8, 6)],   # 約農曆六月末
    "秋": [(10, 20), (11, 6)], # 約農曆九月末
    "冬": [(1, 17), (2, 3)],   # 約農曆十二月末
}

# 天火日（依月份）
TIANHUO_RI = {
    1: "子", 2: "丑", 3: "寅", 4: "卯", 5: "辰", 6: "巳",
    7: "午", 8: "未", 9: "申", 10: "酉", 11: "戌", 12: "亥"
}

# 地火日（依月份）
DIHUO_RI = {
    1: "酉", 2: "戌", 3: "亥", 4: "子", 5: "丑", 6: "寅",
    7: "卯", 8: "辰", 9: "巳", 10: "午", 11: "未", 12: "申"
}

# 八方位與五行
FANGWEI_WX = {
    "東": "木", "東南": "木", "南": "火", "西南": "土",
    "西": "金", "西北": "金", "北": "水", "東北": "土"
}

# 坐向與煞方
ZUOXIANG_SHA = {
    "坐北朝南": {"sha": "北", "sha_zhi": ["子"]},
    "坐南朝北": {"sha": "南", "sha_zhi": ["午"]},
    "坐東朝西": {"sha": "東", "sha_zhi": ["卯"]},
    "坐西朝東": {"sha": "西", "sha_zhi": ["酉"]},
    "坐東北朝西南": {"sha": "東北", "sha_zhi": ["丑", "寅"]},
    "坐西南朝東北": {"sha": "西南", "sha_zhi": ["未", "申"]},
    "坐東南朝西北": {"sha": "東南", "sha_zhi": ["辰", "巳"]},
    "坐西北朝東南": {"sha": "西北", "sha_zhi": ["戌", "亥"]},
}

# 動土吉宿
GROUND_JI_XIU = ["房", "壁", "奎", "婁", "畢", "井", "星", "張", "軫", "斗", "室", "角", "氐", "尾"]

# 動土凶宿
GROUND_XIONG_XIU = ["心", "亢", "牛", "女", "虛", "昴", "鬼", "柳", "翼", "觜", "參", "危"]


# ════════════════════════════════════════════════════════════════════
# L1: 開工動土專用計算函數
# ════════════════════════════════════════════════════════════════════

def check_tianhuo(month: int, day_zhi: str) -> bool:
    """檢查是否為天火日"""
    return TIANHUO_RI.get(month) == day_zhi

def check_dihuo(month: int, day_zhi: str) -> bool:
    """檢查是否為地火日"""
    return DIHUO_RI.get(month) == day_zhi

def check_tuwang(d: date) -> bool:
    """
    檢查是否為土王用事期間
    
    簡化判斷：四季末各18天
    """
    month, day = d.month, d.day
    
    for season, (start, end) in TUWANG_YONGSHI.items():
        start_m, start_d = start
        end_m, end_d = end
        
        if start_m == end_m:
            if month == start_m and start_d <= day <= end_d:
                return True
        else:
            if (month == start_m and day >= start_d) or \
               (month == end_m and day <= end_d):
                return True
    
    return False

def calc_ground_shensha(month: int, day_gan: str, day_zhi: str,
                         owner_zhi: str, zuoxiang: str = None) -> Tuple[List[str], List[str], int]:
    """
    計算開工動土專用神煞
    
    返回：(吉神列表, 凶神列表, 分數調整)
    """
    ji_list = []
    xiong_list = []
    score_adj = 0
    
    # 天火日
    if check_tianhuo(month, day_zhi):
        xiong_list.append("天火")
        score_adj += GROUND_XIONG_SHEN["天火"]["score"]
    
    # 地火日
    if check_dihuo(month, day_zhi):
        xiong_list.append("地火")
        score_adj += GROUND_XIONG_SHEN["地火"]["score"]
    
    # 六合（與屋主）
    if DIZHI_LIUHE.get(day_zhi) == owner_zhi:
        ji_list.append("屋主六合")
        score_adj += 15
    
    # 三合（與屋主）
    for sanhe in DIZHI_SANHE:
        if day_zhi in sanhe and owner_zhi in sanhe:
            ji_list.append("屋主三合")
            score_adj += 10
            break
    
    # 沖屋主
    if DIZHI_CHONG.get(day_zhi) == owner_zhi:
        xiong_list.append("沖屋主")
        score_adj -= 30
    
    # 坐向煞方
    if zuoxiang and zuoxiang in ZUOXIANG_SHA:
        sha_info = ZUOXIANG_SHA[zuoxiang]
        if day_zhi in sha_info["sha_zhi"]:
            xiong_list.append(f"煞{sha_info['sha']}")
            score_adj -= 20
    
    return ji_list, xiong_list, score_adj

def calc_ground_xiu_score(xiu: str) -> int:
    """計算動土二十八宿分數"""
    if xiu in GROUND_JI_XIU:
        return 90
    elif xiu in GROUND_XIONG_XIU:
        return 40
    else:
        return 70


# ════════════════════════════════════════════════════════════════════
# L2: 資料結構
# ════════════════════════════════════════════════════════════════════

@dataclass
class GroundCandidate(DateCandidate):
    """開工動土候選日期"""
    ground_ji_shen: List[str] = field(default_factory=list)
    ground_xiong_shen: List[str] = field(default_factory=list)
    is_tuwang: bool = False
    is_tianhuo: bool = False
    is_dihuo: bool = False
    chong_owner: bool = False
    sha_zuoxiang: bool = False
    
    # v2.0: 完整日課
    full_rike: Optional[FullRike] = None


# ════════════════════════════════════════════════════════════════════
# L3: 開工動土擇日核心類
# ════════════════════════════════════════════════════════════════════

class GroundDateSelector(DateSelector):
    """
    開工動土擇日選擇器
    
    v2.0: 支持完整八字配合
    """
    
    def __init__(self, owner_zhi: str, owner_sx: str = None,
                 zuoxiang: str = None,
                 owner_bazi: Tuple[str, str, str, str] = None):
        """
        初始化
        
        Args:
            owner_zhi: 屋主年支
            owner_sx: 屋主生肖（可選）
            zuoxiang: 房屋坐向（如「坐北朝南」）
            owner_bazi: 屋主完整八字（年柱, 月柱, 日柱, 時柱）
        """
        super().__init__(use_type="動土")
        self.owner_zhi = owner_zhi
        self.owner_sx = owner_sx or SHENGXIAO[DIZHI.index(owner_zhi)]
        self.zuoxiang = zuoxiang
        
        # v2.0: 完整八字
        self.owner_bazi = owner_bazi
        self.owner_chart: Optional[BaziChart] = None
        
        if owner_bazi:
            self.owner_chart = analyze_bazi(*owner_bazi)
        
        self.candidates: List[GroundCandidate] = []
    
    def analyze_date(self, d: date, year_gz: str, month_gz: str,
                     day_gz: str, lunar_month: int, lunar_day: int,
                     person_zhi: str = None) -> GroundCandidate:
        """
        分析開工動土日期
        """
        year_zhi = year_gz[1] if len(year_gz) >= 2 else "子"
        month_zhi = month_gz[1] if len(month_gz) >= 2 else "寅"
        day_gan = day_gz[0] if day_gz else "甲"
        day_zhi = day_gz[1] if len(day_gz) >= 2 else "子"
        
        cand = GroundCandidate(
            date=d,
            ganzhi=day_gz,
            lunar=f"{lunar_month}月{lunar_day}日"
        )
        
        # 檢查土王用事
        if check_tuwang(d):
            cand.is_tuwang = True
        
        # D1: 黃道吉日
        shen, score1, desc1 = calc_huangdao(month_zhi, day_zhi)
        cand.huangdao_shen = shen
        cand.score.huangdao = score1
        
        # D2: 十二建除（動土專用判斷）
        jc, score2, yi, ji = calc_jianchu(month_zhi, day_zhi)
        cand.jianchu = jc
        # 動土專用：開成定日最吉，破閉建日凶
        if jc in ["開", "成"]:
            cand.score.jianchu = 95
        elif jc in ["定"]:
            cand.score.jianchu = 90
        elif jc in ["滿", "平"]:
            cand.score.jianchu = 80
        elif jc in ["破", "閉"]:
            cand.score.jianchu = 25
        elif jc == "建":
            cand.score.jianchu = 40  # 動土忌建日
        else:
            cand.score.jianchu = score2
        
        cand.yi = yi
        cand.ji = ji
        
        # D3: 二十八宿（動土專用）
        day_idx = d.toordinal()
        xiu = XIU_ORDER[day_idx % 28]
        cand.xiu = xiu
        cand.score.xiu = calc_ground_xiu_score(xiu)
        
        # D4: 神煞（通用 + 動土專用）
        ji_shen, xiong_shen, score4 = calc_shensha(year_gz[0], month_zhi, day_gan, day_zhi)
        ground_ji, ground_xiong, ground_score = calc_ground_shensha(
            lunar_month, day_gan, day_zhi, self.owner_zhi, self.zuoxiang)
        
        cand.ji_shen = ji_shen + ground_ji
        cand.xiong_shen = xiong_shen + ground_xiong
        cand.ground_ji_shen = ground_ji
        cand.ground_xiong_shen = ground_xiong
        cand.score.shensha = 75 + score4 + ground_score
        
        # 天火/地火標記
        if check_tianhuo(lunar_month, day_zhi):
            cand.is_tianhuo = True
        if check_dihuo(lunar_month, day_zhi):
            cand.is_dihuo = True
        
        # D5: 沖煞（檢查是否沖屋主）
        chong_sx, sha_fang, score5, _ = calc_chongsha(day_zhi)
        cand.chong_sx = chong_sx
        cand.sha_fang = sha_fang
        
        # 沖屋主
        if DIZHI_CHONG.get(day_zhi) == self.owner_zhi:
            cand.chong_owner = True
            score5 = 25
        
        # 煞坐向
        if self.zuoxiang and self.zuoxiang in ZUOXIANG_SHA:
            sha_info = ZUOXIANG_SHA[self.zuoxiang]
            if day_zhi in sha_info["sha_zhi"]:
                cand.sha_zuoxiang = True
                score5 -= 15
        
        cand.score.chongsha = max(30, score5)
        
        # D6: 動土宜忌
        cand.score.yongshi = self._calc_yongshi(cand, lunar_month)
        
        # D7: 屋主八字配合
        cand.score.bazi = self._calc_bazi_ground(cand)
        
        # D8: 時辰
        jishi = calc_jishi(day_zhi, month_zhi)
        # 過濾掉沖屋主的時辰
        filtered_jishi = []
        for z, s, desc in jishi:
            if DIZHI_CHONG.get(z) == self.owner_zhi:
                continue
            filtered_jishi.append((z, s))
        
        cand.jishi = [(z, s) for z, s in filtered_jishi if s >= 75][:6]
        cand.score.shichen = max([s for z, s in filtered_jishi]) if filtered_jishi else 60
        
        # D9: 易經
        gua_name, gua_xiang, score9, gua_desc = calc_yijing(d.year, d.month, d.day)
        cand.gua_name = gua_name
        cand.score.yijing = score9
        
        # D10: 農民曆避忌
        avoids = check_avoid(lunar_month, lunar_day, year_zhi, month_zhi, day_zhi)
        cand.avoids = [desc for _, desc, _ in avoids]
        avoid_score = sum([s for _, _, s in avoids])
        
        # 土王用事額外扣分
        if cand.is_tuwang:
            cand.avoids.append("土王用事")
            avoid_score -= 35
        
        cand.score.avoid = 100 + avoid_score
        
        # v2.0: 完整日課
        cand.full_rike = get_full_rike(d)
        
        # 計算總分
        self._calc_total(cand)
        
        return cand
    
    def _calc_yongshi(self, cand: GroundCandidate, lunar_month: int = None) -> int:
        """計算動土用事分數"""
        score = 75
        
        # 建除宜忌
        if "動土" in cand.yi or "造屋" in cand.yi:
            score += 20
        if "動土" in cand.ji:
            score -= 25
        
        # 二十八宿宜忌
        xiu_info = ERSHIBA_XIU.get(cand.xiu, {})
        if "動土" in xiu_info.get("yi", []) or "造屋" in xiu_info.get("yi", []):
            score += 15
        if "動土" in xiu_info.get("ji", []):
            score -= 20
        
        # 土王用事
        if cand.is_tuwang:
            score -= 30
        
        # 天火地火
        if cand.is_tianhuo or cand.is_dihuo:
            score -= 20
        
        return max(20, min(100, score))
    
    def _calc_bazi_ground(self, cand: GroundCandidate) -> int:
        """
        計算業主八字配合分數
        
        v2.0: 使用完整八字分析
        """
        score = 75
        
        # 基礎：沖屋主
        if cand.chong_owner:
            score -= 35
        
        # 基礎：煞坐向
        if cand.sha_zuoxiang:
            score -= 20
        
        # 基礎：吉神加分
        if "屋主六合" in cand.ground_ji_shen:
            score += 15
        if "屋主三合" in cand.ground_ji_shen:
            score += 10
        
        # v2.0: 完整八字配合
        if self.owner_chart and len(cand.ganzhi) >= 2:
            rike_gan = cand.ganzhi[0]
            rike_zhi = cand.ganzhi[1]
            rike_result = calc_rike_score(self.owner_chart, rike_gan, rike_zhi)
            
            # 用神配合（日課生用神）
            if rike_result.sheng_yongshen:
                score += 15
                cand.ground_ji_shen.append("生用神")
            
            # 剋忌神（好事）
            if rike_result.ke_jishen:
                score += 10
                cand.ground_ji_shen.append("剋忌神")
            
            # 沖命主（壞事）
            if rike_result.chong_mingzhu:
                score -= 20
                cand.ground_xiong_shen.append("沖命主")
            
            # 合命主（好事）
            if rike_result.he_mingzhu:
                score += 10
                cand.ground_ji_shen.append("合命主")
            
            # 從 relations 提取更多信息
            for rel in rike_result.relations:
                if "忌神" in rel and "剋" not in rel:
                    score -= 15
                    if rel not in cand.ground_xiong_shen:
                        cand.ground_xiong_shen.append(rel)
        
        return max(20, min(100, score))
    
    def select_dates(self, start_date: date, end_date: date,
                     top_n: int = 10) -> List[GroundCandidate]:
        """
        選擇開工動土吉日
        
        Args:
            start_date: 開始日期
            end_date: 結束日期
            top_n: 返回前 N 個最佳日期
        
        Returns:
            排序後的候選日期列表
        """
        self.candidates = []
        
        current = start_date
        while current <= end_date:
            # 獲取干支
            year_gz, month_gz, day_gz = get_ganzhi_from_date(current)
            
            # 簡化農曆
            lunar_month = current.month
            lunar_day = current.day
            
            cand = self.analyze_date(
                current, year_gz, month_gz, day_gz,
                lunar_month, lunar_day
            )
            
            self.candidates.append(cand)
            current += timedelta(days=1)
        
        # 排序
        self.candidates.sort(key=lambda x: -x.score.weighted_total)
        
        # 過濾掉大凶日
        filtered = [c for c in self.candidates 
                    if c.score.weighted_total >= 750 
                    and not c.chong_owner
                    and not c.is_tuwang]
        
        return filtered[:top_n]
    
    def print_result(self, candidates: List[GroundCandidate] = None):
        """輸出結果"""
        if candidates is None:
            candidates = self.candidates[:10]
        
        print("═" * 75)
        print(f"        開工動土擇日結果")
        print(f"        屋主：{self.owner_sx}（{self.owner_zhi}）")
        if self.zuoxiang:
            print(f"        坐向：{self.zuoxiang}")
        print("═" * 75)
        
        for i, cand in enumerate(candidates, 1):
            s = cand.score
            
            warnings = []
            if cand.is_tuwang:
                warnings.append("⚠土王用事")
            if cand.is_tianhuo:
                warnings.append("⚠天火")
            if cand.is_dihuo:
                warnings.append("⚠地火")
            if cand.chong_owner:
                warnings.append("⚠沖屋主")
            if cand.sha_zuoxiang:
                warnings.append("⚠煞坐向")
            
            warn_str = " ".join(warnings) if warnings else ""
            
            # 完整日課
            rike_str = ""
            jishi_str = ""
            if cand.full_rike:
                rike = cand.full_rike
                rike_str = f"\n    ┌─────────────────────────────────────────┐\n" \
                           f"    │  完整日課：{rike.full_rike:<28} │\n" \
                           f"    │  最佳時辰：{rike.hour_gz}（{rike.hour_score}分）{' '*17}│\n" \
                           f"    └─────────────────────────────────────────┘"
                jishi_str = ', '.join([f'{gz}' for _, gz, sc in rike.jishi_list[:4] if sc >= 75])
            else:
                jishi_str = ', '.join([f'{z}時' for z, _ in cand.jishi[:4]]) if cand.jishi else '無'
            
            print(f"""
  【#{i}】{cand.date} {cand.ganzhi}（農曆{cand.lunar}）{warn_str}
  {rike_str}
    黃道：{cand.huangdao_shen}（{s.huangdao}分）
    建除：{cand.jianchu}（{s.jianchu}分）
    二十八宿：{cand.xiu}（{s.xiu}分）
    沖煞：沖{cand.chong_sx}，煞{cand.sha_fang}（{s.chongsha}分）
    卦象：{cand.gua_name}（{s.yijing}分）
    
    動土吉神：{', '.join(cand.ground_ji_shen) if cand.ground_ji_shen else '無'}
    動土凶神：{', '.join(cand.ground_xiong_shen) if cand.ground_xiong_shen else '無'}
    農曆避忌：{', '.join(cand.avoids) if cand.avoids else '無'}
    
    吉時選項：{jishi_str}
    
    加權總分：{s.weighted_total:.1f}
            """)


# ════════════════════════════════════════════════════════════════════
# L4: 便捷函數
# ════════════════════════════════════════════════════════════════════

def select_ground_date(owner_year: int,
                        start_date: date, end_date: date,
                        zuoxiang: str = None,
                        owner_bazi: Tuple[str, str, str, str] = None,
                        top_n: int = 10) -> List[GroundCandidate]:
    """
    便捷函數：選擇開工動土吉日
    
    Args:
        owner_year: 屋主出生年（如1980）
        start_date: 開始日期
        end_date: 結束日期
        zuoxiang: 房屋坐向（可選）
        owner_bazi: 屋主完整八字（年柱, 月柱, 日柱, 時柱）
        top_n: 返回前 N 個
    
    Returns:
        候選日期列表
    """
    # 計算年支
    owner_zhi = DIZHI[(owner_year - 4) % 12]
    
    selector = GroundDateSelector(
        owner_zhi, 
        zuoxiang=zuoxiang,
        owner_bazi=owner_bazi
    )
    return selector.select_dates(start_date, end_date, top_n)


def select_ground_date_v2(owner_bazi: Tuple[str, str, str, str],
                           start_date: date, end_date: date,
                           zuoxiang: str = None,
                           top_n: int = 10) -> List[GroundCandidate]:
    """
    便捷函數：使用完整八字選擇開工動土吉日
    
    Args:
        owner_bazi: 屋主完整八字（年柱, 月柱, 日柱, 時柱）
        start_date: 開始日期
        end_date: 結束日期
        zuoxiang: 房屋坐向（可選）
        top_n: 返回前 N 個
    
    Returns:
        候選日期列表
    """
    owner_zhi = owner_bazi[0][1] if len(owner_bazi[0]) >= 2 else "子"
    
    selector = GroundDateSelector(
        owner_zhi, 
        zuoxiang=zuoxiang,
        owner_bazi=owner_bazi
    )
    return selector.select_dates(start_date, end_date, top_n)


# ════════════════════════════════════════════════════════════════════
# 測試
# ════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("═" * 75)
    print("        開工動土擇日模組 v2.0 - 測試")
    print("═" * 75)
    
    # 測試案例：屋主1985年（牛），坐北朝南
    owner_year = 1985
    owner_zhi = DIZHI[(owner_year - 4) % 12]  # 丑
    zuoxiang = "坐北朝南"
    
    # v2.0: 完整八字（乙丑年 丁亥月 庚子日 乙酉時）
    owner_bazi = ("乙丑", "丁亥", "庚子", "乙酉")
    
    print(f"\n  屋主：{owner_year}年生（{SHENGXIAO[DIZHI.index(owner_zhi)]}，{owner_zhi}）")
    print(f"  八字：{' '.join(owner_bazi)}")
    print(f"  坐向：{zuoxiang}")
    
    # 選擇日期範圍
    start = date(2025, 3, 1)
    end = date(2025, 3, 31)
    
    print(f"\n  查詢範圍：{start} 至 {end}")
    
    # v2.0: 使用完整八字
    selector = GroundDateSelector(
        owner_zhi, 
        zuoxiang=zuoxiang,
        owner_bazi=owner_bazi
    )
    
    # 顯示八字分析
    if selector.owner_chart:
        chart = selector.owner_chart
        print(f"\n  【業主八字分析】")
        print(f"    日主：{chart.day_master}（{chart.day_master_wx}）")
        print(f"    用神：{chart.yongshen}")
        print(f"    喜神：{chart.xishen}")
        print(f"    忌神：{chart.jishen}")
    
    results = selector.select_dates(start, end, top_n=5)
    
    # 輸出
    selector.print_result(results)
    
    print("\n" + "═" * 75)
