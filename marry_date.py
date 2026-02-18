#!/usr/bin/env python3
"""
marry_date.py - 嫁娶擇日擇時模組
版本：v2.0.0

═══════════════════════════════════════════════════════════════════════
v2.0 更新：加入雙方八字配合分析

嫁娶專用維度（基於 date_base.py 10維度）：
  D6  嫁娶宜忌     紅煞日/月忌日/重日復日
  D7  新人八字     男女命配合/用神配合/合婚分析
  
嫁娶專用神煞：
  吉神：天喜/天德/月德/紅鸞/天嗣
  凶神：紅煞/月厭/厭對/歸忌/往亡
═══════════════════════════════════════════════════════════════════════

PYLIB 依賴：date_base.py, bazi_base.py
XTF8 層級：L0-L4
@織明 × @理樞
"""

from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, field
from datetime import date, timedelta
from date_base import (
    DateSelector, DateCandidate, DateScore, DATE_WEIGHTS,
    TIANGAN, DIZHI, SHENGXIAO, DIZHI_CHONG, DIZHI_LIUHE, DIZHI_SANHE,
    calc_huangdao, calc_jianchu, calc_xiu, calc_shensha, calc_chongsha,
    calc_jishi, calc_yijing, check_avoid, get_ganzhi_from_date,
    JIANCHU, ERSHIBA_XIU,
    get_full_rike, FullRike, calc_shichen_ganzhi
)
from bazi_base import (
    BaziChart, BaziAnalyzer, RikePeihe, HeHunResult, HeHunAnalyzer,
    analyze_bazi, analyze_hehun, calc_rike_score,
    DIZHI_CHONG as BAZI_CHONG, DIZHI_LIUHE as BAZI_LIUHE,
    check_dizhi_relation, SHENGXIAO as BAZI_SHENGXIAO
)

# ════════════════════════════════════════════════════════════════════
# L0: 嫁娶專用常量
# ════════════════════════════════════════════════════════════════════

# 嫁娶吉神
MARRY_JI_SHEN = {
    "天喜": {"score": 20, "desc": "喜事臨門"},
    "紅鸞": {"score": 25, "desc": "姻緣天定"},
    "天嗣": {"score": 15, "desc": "利於子嗣"},
    "天德": {"score": 18, "desc": "逢凶化吉"},
    "月德": {"score": 15, "desc": "諸事吉利"},
    "三合": {"score": 12, "desc": "三合吉慶"},
    "六合": {"score": 12, "desc": "六合和順"},
    "天德合": {"score": 12, "desc": "得貴人助"},
    "月德合": {"score": 10, "desc": "得貴人助"},
    "母倉": {"score": 8, "desc": "母儀天下"},
    "益後": {"score": 10, "desc": "利於後代"},
}

# 嫁娶凶神
MARRY_XIONG_SHEN = {
    "紅煞": {"score": -30, "desc": "嫁娶大忌"},
    "月厭": {"score": -25, "desc": "月厭日"},
    "厭對": {"score": -20, "desc": "厭對日"},
    "歸忌": {"score": -25, "desc": "歸忌日"},
    "往亡": {"score": -20, "desc": "往亡日"},
    "月刑": {"score": -15, "desc": "月刑日"},
    "月破": {"score": -35, "desc": "月破大凶"},
    "重日": {"score": -15, "desc": "重婚之象"},
    "復日": {"score": -15, "desc": "重婚之象"},
    "四離": {"score": -20, "desc": "離散之象"},
    "四絕": {"score": -20, "desc": "斷絕之象"},
    "孤辰": {"score": -18, "desc": "孤獨之象"},
    "寡宿": {"score": -18, "desc": "寡居之象"},
    "披麻": {"score": -25, "desc": "喪事之象"},
    "殃煞": {"score": -20, "desc": "災殃之象"},
}

# 嫁娶忌日（農曆日期）
MARRY_JI_RI = {
    # 紅煞日（正月午日、二月未日...）
    "紅煞": {
        1: "午", 2: "未", 3: "申", 4: "酉", 5: "戌", 6: "亥",
        7: "子", 8: "丑", 9: "寅", 10: "卯", 11: "辰", 12: "巳"
    },
    # 月厭日（正月戌日、二月酉日...）
    "月厭": {
        1: "戌", 2: "酉", 3: "申", 4: "未", 5: "午", 6: "巳",
        7: "辰", 8: "卯", 9: "寅", 10: "丑", 11: "子", 12: "亥"
    },
}

# 女命行嫁大利月（依女命生肖）
NVMING_DALI_YUE = {
    "鼠": [6, 12], "牛": [5, 11], "虎": [2, 8], "兔": [1, 7],
    "龍": [4, 10], "蛇": [3, 9], "馬": [6, 12], "羊": [5, 11],
    "猴": [2, 8], "雞": [1, 7], "狗": [4, 10], "豬": [3, 9]
}

# 女命行嫁小利月
NVMING_XIAOLI_YUE = {
    "鼠": [1, 7], "牛": [4, 10], "虎": [3, 9], "兔": [6, 12],
    "龍": [5, 11], "蛇": [2, 8], "馬": [1, 7], "羊": [4, 10],
    "猴": [3, 9], "雞": [6, 12], "狗": [5, 11], "豬": [2, 8]
}

# 翁姑月（避開）
WENGGU_YUE = {
    "鼠": [3, 9], "牛": [2, 8], "虎": [1, 7], "兔": [6, 12],
    "龍": [3, 9], "蛇": [2, 8], "馬": [3, 9], "羊": [2, 8],
    "猴": [1, 7], "雞": [6, 12], "狗": [3, 9], "豬": [2, 8]
}

# 嫁娶吉宿
MARRY_JI_XIU = ["房", "壁", "奎", "婁", "畢", "井", "星", "張", "軫", "角", "氐", "尾", "室", "斗"]

# 嫁娶凶宿
MARRY_XIONG_XIU = ["心", "亢", "牛", "女", "虛", "昴", "鬼", "柳", "翼", "觜", "參"]


# ════════════════════════════════════════════════════════════════════
# L1: 嫁娶專用計算函數
# ════════════════════════════════════════════════════════════════════

def check_hongsha(lunar_month: int, day_zhi: str) -> bool:
    """檢查是否為紅煞日"""
    return MARRY_JI_RI["紅煞"].get(lunar_month) == day_zhi

def check_yueyan(lunar_month: int, day_zhi: str) -> bool:
    """檢查是否為月厭日"""
    return MARRY_JI_RI["月厭"].get(lunar_month) == day_zhi

def check_chongri(day_gan: str) -> bool:
    """檢查是否為重日（甲甲、乙乙...）"""
    # 簡化：干支相同為重日
    return False  # 需要更精確的計算

def get_nvming_month(nvming_sx: str) -> Tuple[List[int], List[int], List[int]]:
    """
    獲取女命行嫁月
    
    返回：(大利月, 小利月, 翁姑月)
    """
    dali = NVMING_DALI_YUE.get(nvming_sx, [])
    xiaoli = NVMING_XIAOLI_YUE.get(nvming_sx, [])
    wenggu = WENGGU_YUE.get(nvming_sx, [])
    
    return dali, xiaoli, wenggu

def calc_marry_shensha(lunar_month: int, day_gan: str, day_zhi: str,
                        man_zhi: str, woman_zhi: str) -> Tuple[List[str], List[str], int]:
    """
    計算嫁娶專用神煞
    
    返回：(吉神列表, 凶神列表, 分數調整)
    """
    ji_list = []
    xiong_list = []
    score_adj = 0
    
    # 紅煞日
    if check_hongsha(lunar_month, day_zhi):
        xiong_list.append("紅煞")
        score_adj += MARRY_XIONG_SHEN["紅煞"]["score"]
    
    # 月厭日
    if check_yueyan(lunar_month, day_zhi):
        xiong_list.append("月厭")
        score_adj += MARRY_XIONG_SHEN["月厭"]["score"]
    
    # 六合（與男命）
    if DIZHI_LIUHE.get(day_zhi) == man_zhi:
        ji_list.append("男命六合")
        score_adj += 15
    
    # 六合（與女命）
    if DIZHI_LIUHE.get(day_zhi) == woman_zhi:
        ji_list.append("女命六合")
        score_adj += 15
    
    # 沖男命
    if DIZHI_CHONG.get(day_zhi) == man_zhi:
        xiong_list.append("沖男命")
        score_adj -= 25
    
    # 沖女命
    if DIZHI_CHONG.get(day_zhi) == woman_zhi:
        xiong_list.append("沖女命")
        score_adj -= 25
    
    return ji_list, xiong_list, score_adj

def calc_marry_xiu_score(xiu: str) -> int:
    """計算嫁娶二十八宿分數"""
    if xiu in MARRY_JI_XIU:
        return 90
    elif xiu in MARRY_XIONG_XIU:
        return 40
    else:
        return 70


# ════════════════════════════════════════════════════════════════════
# L2: 資料結構
# ════════════════════════════════════════════════════════════════════

@dataclass
class MarryCandidate(DateCandidate):
    """嫁娶候選日期"""
    marry_ji_shen: List[str] = field(default_factory=list)
    marry_xiong_shen: List[str] = field(default_factory=list)
    is_dali_yue: bool = False
    is_xiaoli_yue: bool = False
    is_wenggu_yue: bool = False
    chong_man: bool = False
    chong_woman: bool = False
    
    # v2.0 新增：八字配合
    man_rike_match: Optional[RikePeihe] = None   # 日課與男命配合
    woman_rike_match: Optional[RikePeihe] = None # 日課與女命配合
    bazi_match_score: int = 0                     # 八字配合總分
    
    # v2.1: 完整日課
    full_rike: Optional[FullRike] = None


# ════════════════════════════════════════════════════════════════════
# L3: 嫁娶擇日核心類
# ════════════════════════════════════════════════════════════════════

class MarryDateSelector(DateSelector):
    """
    嫁娶擇日選擇器
    
    v2.0：支持完整八字配合分析
    """
    
    def __init__(self, man_zhi: str, woman_zhi: str, 
                 man_sx: str = None, woman_sx: str = None,
                 man_bazi: BaziChart = None, woman_bazi: BaziChart = None):
        """
        初始化
        
        Args:
            man_zhi: 男方年支
            woman_zhi: 女方年支
            man_sx: 男方生肖（可選，可從年支推算）
            woman_sx: 女方生肖（可選）
            man_bazi: 男方完整八字（可選，v2.0新增）
            woman_bazi: 女方完整八字（可選，v2.0新增）
        """
        super().__init__(use_type="嫁娶")
        self.man_zhi = man_zhi
        self.woman_zhi = woman_zhi
        self.man_sx = man_sx or SHENGXIAO[DIZHI.index(man_zhi)]
        self.woman_sx = woman_sx or SHENGXIAO[DIZHI.index(woman_zhi)]
        
        # v2.0：完整八字
        self.man_bazi = man_bazi
        self.woman_bazi = woman_bazi
        self.use_full_bazi = man_bazi is not None and woman_bazi is not None
        
        # 獲取女命行嫁月
        self.dali_yue, self.xiaoli_yue, self.wenggu_yue = get_nvming_month(self.woman_sx)
        
        # 合婚分析
        self.hehun_result: Optional[HeHunResult] = None
        if self.use_full_bazi:
            self.hehun_result = analyze_hehun(man_bazi, woman_bazi)
        
        self.candidates: List[MarryCandidate] = []
    
    def analyze_date(self, d: date, year_gz: str, month_gz: str,
                     day_gz: str, lunar_month: int, lunar_day: int,
                     person_zhi: str = None) -> MarryCandidate:
        """
        分析嫁娶日期
        """
        year_zhi = year_gz[1] if len(year_gz) >= 2 else "子"
        month_zhi = month_gz[1] if len(month_gz) >= 2 else "寅"
        day_gan = day_gz[0] if day_gz else "甲"
        day_zhi = day_gz[1] if len(day_gz) >= 2 else "子"
        
        cand = MarryCandidate(
            date=d,
            ganzhi=day_gz,
            lunar=f"{lunar_month}月{lunar_day}日"
        )
        
        # D1: 黃道吉日
        shen, score1, desc1 = calc_huangdao(month_zhi, day_zhi)
        cand.huangdao_shen = shen
        cand.score.huangdao = score1
        
        # D2: 十二建除（嫁娶專用判斷）
        jc, score2, yi, ji = calc_jianchu(month_zhi, day_zhi)
        cand.jianchu = jc
        # 嫁娶專用：開成日最吉，破閉日最凶
        if jc in ["開", "成"]:
            cand.score.jianchu = 95
        elif jc in ["定", "滿"]:
            cand.score.jianchu = 85
        elif jc in ["破", "閉"]:
            cand.score.jianchu = 30
        else:
            cand.score.jianchu = score2
        
        cand.yi = yi
        cand.ji = ji
        
        # D3: 二十八宿（嫁娶專用）
        day_idx = d.toordinal()
        from date_base import XIU_ORDER
        xiu = XIU_ORDER[day_idx % 28]
        cand.xiu = xiu
        cand.score.xiu = calc_marry_xiu_score(xiu)
        
        # D4: 神煞（通用 + 嫁娶專用）
        ji_shen, xiong_shen, score4 = calc_shensha(year_gz[0], month_zhi, day_gan, day_zhi)
        marry_ji, marry_xiong, marry_score = calc_marry_shensha(
            lunar_month, day_gan, day_zhi, self.man_zhi, self.woman_zhi)
        
        cand.ji_shen = ji_shen + marry_ji
        cand.xiong_shen = xiong_shen + marry_xiong
        cand.marry_ji_shen = marry_ji
        cand.marry_xiong_shen = marry_xiong
        cand.score.shensha = 75 + score4 + marry_score
        
        # D5: 沖煞（檢查是否沖新人）
        chong_sx, sha_fang, score5, _ = calc_chongsha(day_zhi)
        cand.chong_sx = chong_sx
        cand.sha_fang = sha_fang
        
        # 沖男命
        if DIZHI_CHONG.get(day_zhi) == self.man_zhi:
            cand.chong_man = True
            score5 = 30
        # 沖女命
        if DIZHI_CHONG.get(day_zhi) == self.woman_zhi:
            cand.chong_woman = True
            score5 = 25
        
        cand.score.chongsha = score5
        
        # D6: 嫁娶宜忌
        cand.score.yongshi = self._calc_yongshi(cand, lunar_month)
        
        # D7: 新人八字配合
        cand.score.bazi = self._calc_bazi_marry(cand, lunar_month)
        
        # 標記行嫁月
        if lunar_month in self.dali_yue:
            cand.is_dali_yue = True
        elif lunar_month in self.xiaoli_yue:
            cand.is_xiaoli_yue = True
        if lunar_month in self.wenggu_yue:
            cand.is_wenggu_yue = True
        
        # D8: 時辰
        jishi = calc_jishi(day_zhi, month_zhi)
        # 過濾掉沖新人的時辰
        filtered_jishi = []
        for z, s, desc in jishi:
            if DIZHI_CHONG.get(z) == self.man_zhi:
                continue
            if DIZHI_CHONG.get(z) == self.woman_zhi:
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
        cand.score.avoid = 100 + avoid_score
        
        # v2.1: 完整日課
        cand.full_rike = get_full_rike(d)
        
        # 計算總分
        self._calc_total(cand)
        
        return cand
    
    def _calc_yongshi(self, cand: MarryCandidate, lunar_month: int = None) -> int:
        """計算嫁娶用事分數"""
        score = 75
        
        # 建除宜忌
        if "嫁娶" in cand.yi:
            score += 20
        if "嫁娶" in cand.ji:
            score -= 25
        
        # 二十八宿宜忌
        xiu_info = ERSHIBA_XIU.get(cand.xiu, {})
        if "嫁娶" in xiu_info.get("yi", []):
            score += 15
        if "嫁娶" in xiu_info.get("ji", []):
            score -= 20
        
        return max(30, min(100, score))
    
    def _calc_bazi_marry(self, cand: MarryCandidate, lunar_month: int, day_gz: str = None) -> int:
        """計算新人八字配合分數"""
        score = 75
        
        # 大利月
        if lunar_month in self.dali_yue:
            score += 20
        # 小利月
        elif lunar_month in self.xiaoli_yue:
            score += 10
        # 翁姑月
        if lunar_month in self.wenggu_yue:
            score -= 15
        
        # 沖男命
        if cand.chong_man:
            score -= 30
        
        # 沖女命
        if cand.chong_woman:
            score -= 30
        
        # v2.0：完整八字配合
        if self.use_full_bazi and day_gz:
            # 日課與男命配合
            man_match = analyze_rike_match(self.man_bazi, day_gz)
            cand.man_rike_match = man_match
            
            # 日課與女命配合
            woman_match = analyze_rike_match(self.woman_bazi, day_gz)
            cand.woman_rike_match = woman_match
            
            # 計算八字配合分數
            bazi_score = (man_match.score + woman_match.score) // 2
            cand.bazi_match_score = bazi_score
            
            # 調整分數
            if bazi_score >= 85:
                score += 15
            elif bazi_score >= 70:
                score += 5
            elif bazi_score < 50:
                score -= 15
        
        return max(30, min(100, score))
    
    def select_dates(self, start_date: date, end_date: date,
                     top_n: int = 10) -> List[MarryCandidate]:
        """
        選擇嫁娶吉日
        
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
            # 獲取干支（簡化版，實際需要萬年曆）
            year_gz, month_gz, day_gz = get_ganzhi_from_date(current)
            
            # 簡化：假設農曆月日與公曆相近（實際需要轉換）
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
                    if c.score.weighted_total >= 800 
                    and not c.chong_man 
                    and not c.chong_woman]
        
        return filtered[:top_n]
    
    def print_result(self, candidates: List[MarryCandidate] = None):
        """輸出結果"""
        if candidates is None:
            candidates = self.candidates[:10]
        
        print("═" * 75)
        print(f"        嫁娶擇日結果")
        print(f"        男方：{self.man_sx}（{self.man_zhi}）")
        print(f"        女方：{self.woman_sx}（{self.woman_zhi}）")
        print(f"        女命大利月：{self.dali_yue}")
        print(f"        女命小利月：{self.xiaoli_yue}")
        print("═" * 75)
        
        for i, cand in enumerate(candidates, 1):
            s = cand.score
            yue_mark = "★大利" if cand.is_dali_yue else "○小利" if cand.is_xiaoli_yue else ""
            if cand.is_wenggu_yue:
                yue_mark += "⚠翁姑"
            
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
  【#{i}】{cand.date} {cand.ganzhi}（農曆{cand.lunar}）{yue_mark}
  {rike_str}
    黃道：{cand.huangdao_shen}（{s.huangdao}分）
    建除：{cand.jianchu}（{s.jianchu}分）
    二十八宿：{cand.xiu}（{s.xiu}分）
    沖煞：沖{cand.chong_sx}，煞{cand.sha_fang}（{s.chongsha}分）
    卦象：{cand.gua_name}（{s.yijing}分）
    
    嫁娶吉神：{', '.join(cand.marry_ji_shen) if cand.marry_ji_shen else '無'}
    嫁娶凶神：{', '.join(cand.marry_xiong_shen) if cand.marry_xiong_shen else '無'}
    農曆避忌：{', '.join(cand.avoids) if cand.avoids else '無'}
    
    吉時選項：{jishi_str}
    
    加權總分：{s.weighted_total:.1f}
            """)


# ════════════════════════════════════════════════════════════════════
# L4: 便捷函數
# ════════════════════════════════════════════════════════════════════

def select_marry_date(man_year: int, woman_year: int,
                       start_date: date, end_date: date,
                       top_n: int = 10) -> List[MarryCandidate]:
    """
    便捷函數：選擇嫁娶吉日
    
    Args:
        man_year: 男方出生年（如1990）
        woman_year: 女方出生年（如1992）
        start_date: 開始日期
        end_date: 結束日期
        top_n: 返回前 N 個
    
    Returns:
        候選日期列表
    """
    # 計算年支
    man_zhi = DIZHI[(man_year - 4) % 12]
    woman_zhi = DIZHI[(woman_year - 4) % 12]
    
    selector = MarryDateSelector(man_zhi, woman_zhi)
    return selector.select_dates(start_date, end_date, top_n)


# ════════════════════════════════════════════════════════════════════
# 測試
# ════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("═" * 75)
    print("        嫁娶擇日模組 - 測試")
    print("═" * 75)
    
    # 測試案例：男1990年（馬），女1992年（猴）
    man_year = 1990
    woman_year = 1992
    
    man_zhi = DIZHI[(man_year - 4) % 12]  # 午
    woman_zhi = DIZHI[(woman_year - 4) % 12]  # 申
    
    print(f"\n  男方：{man_year}年生（{SHENGXIAO[DIZHI.index(man_zhi)]}，{man_zhi}）")
    print(f"  女方：{woman_year}年生（{SHENGXIAO[DIZHI.index(woman_zhi)]}，{woman_zhi}）")
    
    # 選擇日期範圍
    start = date(2025, 3, 1)
    end = date(2025, 3, 31)
    
    print(f"\n  查詢範圍：{start} 至 {end}")
    
    # 選擇
    selector = MarryDateSelector(man_zhi, woman_zhi)
    results = selector.select_dates(start, end, top_n=5)
    
    # 輸出
    selector.print_result(results)
    
    print("\n" + "═" * 75)
