#!/usr/bin/env python3
"""
event_date.py - 多用途擇日模組
版本：v1.0.0

═══════════════════════════════════════════════════════════════════════
支援用途：
  • 開市：開業/開張/開幕
  • 搬家：入宅/移徙/遷居
  • 安床：安床/安香/安神
  • 祭祀：祭祀/祈福/還願
  • 出行：出行/旅遊/遠行
═══════════════════════════════════════════════════════════════════════

PYLIB 依賴：date_base.py, bazi_base.py
XTF8 層級：L0-L4
@11星協作：@織明(統籌) @理樞(分析) @澄書(記錄) @流祇(連結)
"""

from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, field
from datetime import date, timedelta
from enum import Enum
from date_base import (
    DateSelector, DateCandidate, DateScore, DATE_WEIGHTS,
    TIANGAN, DIZHI, SHENGXIAO, DIZHI_CHONG, DIZHI_LIUHE, DIZHI_SANHE,
    calc_huangdao, calc_jianchu, calc_xiu, calc_shensha, calc_chongsha,
    calc_jishi, calc_yijing, check_avoid, get_ganzhi_from_date,
    get_full_rike, FullRike, JIANCHU, ERSHIBA_XIU, XIU_ORDER
)
from bazi_base import (
    BaziChart, analyze_bazi, calc_rike_score, RikePeihe
)

# ════════════════════════════════════════════════════════════════════
# L0: 用途類型定義
# ════════════════════════════════════════════════════════════════════

class EventType(Enum):
    """用途類型"""
    KAISHI = "開市"      # 開業/開張
    BANJIA = "搬家"      # 入宅/移徙
    ANCHUANG = "安床"    # 安床/安香
    JISI = "祭祀"        # 祭祀/祈福
    CHUXING = "出行"     # 出行/旅遊

# 各用途的建除宜忌
EVENT_JIANCHU = {
    EventType.KAISHI: {
        "yi": ["開", "成", "滿"],
        "ji": ["破", "閉", "執"],
        "best": ["開", "成"],
    },
    EventType.BANJIA: {
        "yi": ["開", "成", "定", "滿"],
        "ji": ["破", "閉", "建"],
        "best": ["成", "開"],
    },
    EventType.ANCHUANG: {
        "yi": ["成", "定", "開", "滿"],
        "ji": ["破", "閉", "危"],
        "best": ["成", "定"],
    },
    EventType.JISI: {
        "yi": ["開", "成", "定", "滿", "建", "除", "平", "收"],
        "ji": ["破", "閉"],
        "best": ["開", "成"],
    },
    EventType.CHUXING: {
        "yi": ["開", "成", "定", "滿", "除"],
        "ji": ["破", "閉", "危", "執"],
        "best": ["開", "成"],
    },
}

# 各用途的二十八宿宜忌
EVENT_XIU = {
    EventType.KAISHI: {
        "yi": ["房", "壁", "奎", "婁", "畢", "井", "星", "張", "斗", "室"],
        "ji": ["心", "亢", "牛", "女", "虛", "鬼", "柳", "翼"],
    },
    EventType.BANJIA: {
        "yi": ["房", "壁", "奎", "婁", "畢", "井", "星", "張", "軫", "氐", "尾", "室"],
        "ji": ["心", "亢", "牛", "女", "虛", "鬼", "柳", "翼", "危"],
    },
    EventType.ANCHUANG: {
        "yi": ["房", "壁", "奎", "婁", "畢", "井", "星", "張", "室", "斗"],
        "ji": ["心", "亢", "牛", "女", "虛", "鬼", "柳", "翼"],
    },
    EventType.JISI: {
        "yi": ["房", "壁", "奎", "婁", "畢", "井", "星", "張", "軫", "氐", "尾", "室", "斗", "角"],
        "ji": ["心", "亢", "牛", "女", "虛", "鬼"],
    },
    EventType.CHUXING: {
        "yi": ["房", "壁", "奎", "婁", "畢", "井", "星", "張", "氐", "室", "斗"],
        "ji": ["心", "亢", "牛", "女", "虛", "鬼", "柳", "翼", "危"],
    },
}

# 各用途專用吉神
EVENT_JI_SHEN = {
    EventType.KAISHI: {
        "天財": 20, "月財": 15, "天倉": 12, "福德": 10,
        "天德": 15, "月德": 12, "驛馬": 10,
    },
    EventType.BANJIA: {
        "天德": 18, "月德": 15, "福德": 12, "天恩": 10,
        "母倉": 8, "安香": 15, "天喜": 10,
    },
    EventType.ANCHUANG: {
        "天德": 18, "月德": 15, "福德": 12, "安床": 20,
        "六合": 10, "母倉": 8,
    },
    EventType.JISI: {
        "天德": 20, "月德": 18, "天恩": 15, "福德": 12,
        "月恩": 10, "四相": 8, "時德": 8,
    },
    EventType.CHUXING: {
        "驛馬": 20, "天馬": 18, "天德": 15, "月德": 12,
        "福德": 10, "天恩": 8,
    },
}

# 各用途專用凶神
EVENT_XIONG_SHEN = {
    EventType.KAISHI: {
        "月破": -30, "歲破": -35, "大耗": -20, "劫煞": -18,
        "災煞": -15, "天火": -15,
    },
    EventType.BANJIA: {
        "月破": -30, "歲破": -35, "天火": -25, "地火": -25,
        "歸忌": -20, "往亡": -18,
    },
    EventType.ANCHUANG: {
        "月破": -30, "歲破": -35, "天火": -20, "地火": -20,
        "白虎": -15,
    },
    EventType.JISI: {
        "月破": -25, "歲破": -30, "天狗": -15, "白虎": -12,
    },
    EventType.CHUXING: {
        "月破": -30, "歲破": -35, "往亡": -25, "歸忌": -20,
        "災煞": -18, "劫煞": -15, "天火": -15,
    },
}


# ════════════════════════════════════════════════════════════════════
# L1: 用途專用計算
# ════════════════════════════════════════════════════════════════════

def calc_event_jianchu_score(event_type: EventType, jianchu: str) -> int:
    """計算用途專用建除分數"""
    config = EVENT_JIANCHU.get(event_type, {})
    
    if jianchu in config.get("best", []):
        return 95
    elif jianchu in config.get("yi", []):
        return 85
    elif jianchu in config.get("ji", []):
        return 35
    else:
        return 70

def calc_event_xiu_score(event_type: EventType, xiu: str) -> int:
    """計算用途專用二十八宿分數"""
    config = EVENT_XIU.get(event_type, {})
    
    if xiu in config.get("yi", []):
        return 90
    elif xiu in config.get("ji", []):
        return 40
    else:
        return 70


# ════════════════════════════════════════════════════════════════════
# L2: 資料結構
# ════════════════════════════════════════════════════════════════════

@dataclass
class EventCandidate(DateCandidate):
    """用途候選日期"""
    event_type: EventType = EventType.KAISHI
    event_ji_shen: List[str] = field(default_factory=list)
    event_xiong_shen: List[str] = field(default_factory=list)
    chong_owner: bool = False
    full_rike: Optional[FullRike] = None


# ════════════════════════════════════════════════════════════════════
# L3: 多用途擇日核心類
# ════════════════════════════════════════════════════════════════════

class EventDateSelector(DateSelector):
    """
    多用途擇日選擇器
    
    支援：開市/搬家/安床/祭祀/出行
    """
    
    def __init__(self, event_type: EventType, owner_zhi: str = None,
                 owner_bazi: Tuple[str, str, str, str] = None):
        """
        初始化
        
        Args:
            event_type: 用途類型
            owner_zhi: 事主年支（可選）
            owner_bazi: 事主完整八字（可選）
        """
        super().__init__(use_type=event_type.value)
        self.event_type = event_type
        self.owner_zhi = owner_zhi
        self.owner_sx = SHENGXIAO[DIZHI.index(owner_zhi)] if owner_zhi else None
        
        # 八字
        self.owner_bazi = owner_bazi
        self.owner_chart: Optional[BaziChart] = None
        if owner_bazi:
            self.owner_chart = analyze_bazi(*owner_bazi)
        
        self.candidates: List[EventCandidate] = []
    
    def analyze_date(self, d: date, year_gz: str, month_gz: str,
                     day_gz: str, lunar_month: int, lunar_day: int,
                     person_zhi: str = None) -> EventCandidate:
        """分析日期"""
        year_zhi = year_gz[1] if len(year_gz) >= 2 else "子"
        month_zhi = month_gz[1] if len(month_gz) >= 2 else "寅"
        day_gan = day_gz[0] if day_gz else "甲"
        day_zhi = day_gz[1] if len(day_gz) >= 2 else "子"
        
        cand = EventCandidate(
            date=d,
            ganzhi=day_gz,
            lunar=f"{lunar_month}月{lunar_day}日",
            event_type=self.event_type
        )
        
        # D1: 黃道吉日
        shen, score1, desc1 = calc_huangdao(month_zhi, day_zhi)
        cand.huangdao_shen = shen
        cand.score.huangdao = score1
        
        # D2: 十二建除（用途專用）
        jc, _, yi, ji = calc_jianchu(month_zhi, day_zhi)
        cand.jianchu = jc
        cand.score.jianchu = calc_event_jianchu_score(self.event_type, jc)
        cand.yi = yi
        cand.ji = ji
        
        # D3: 二十八宿（用途專用）
        day_idx = d.toordinal()
        xiu = XIU_ORDER[day_idx % 28]
        cand.xiu = xiu
        cand.score.xiu = calc_event_xiu_score(self.event_type, xiu)
        
        # D4: 神煞
        ji_shen, xiong_shen, score4 = calc_shensha(year_gz[0], month_zhi, day_gan, day_zhi)
        cand.ji_shen = ji_shen
        cand.xiong_shen = xiong_shen
        cand.score.shensha = 75 + score4
        
        # D5: 沖煞
        chong_sx, sha_fang, score5, _ = calc_chongsha(day_zhi)
        cand.chong_sx = chong_sx
        cand.sha_fang = sha_fang
        
        # 沖事主
        if self.owner_zhi and DIZHI_CHONG.get(day_zhi) == self.owner_zhi:
            cand.chong_owner = True
            score5 = 30
        
        cand.score.chongsha = score5
        
        # D6: 用事宜忌
        cand.score.yongshi = self._calc_yongshi(cand)
        
        # D7: 八字配合
        cand.score.bazi = self._calc_bazi(cand)
        
        # D8: 時辰
        jishi = calc_jishi(day_zhi, month_zhi)
        filtered = [(z, s) for z, s, _ in jishi 
                    if not (self.owner_zhi and DIZHI_CHONG.get(z) == self.owner_zhi)]
        cand.jishi = [(z, s) for z, s in filtered if s >= 75][:6]
        cand.score.shichen = max([s for z, s in filtered]) if filtered else 60
        
        # D9: 易經
        gua_name, gua_xiang, score9, gua_desc = calc_yijing(d.year, d.month, d.day)
        cand.gua_name = gua_name
        cand.score.yijing = score9
        
        # D10: 農民曆避忌
        avoids = check_avoid(lunar_month, lunar_day, year_zhi, month_zhi, day_zhi)
        cand.avoids = [desc for _, desc, _ in avoids]
        cand.score.avoid = 100 + sum([s for _, _, s in avoids])
        
        # 完整日課
        cand.full_rike = get_full_rike(d)
        
        # 總分
        self._calc_total(cand)
        
        return cand
    
    def _calc_yongshi(self, cand: EventCandidate) -> int:
        """計算用事宜忌分數"""
        score = 75
        event_name = self.event_type.value
        
        # 建除宜忌
        if event_name in cand.yi or any(k in cand.yi for k in [event_name, "開市", "入宅", "祭祀", "出行"]):
            score += 15
        if event_name in cand.ji:
            score -= 20
        
        return max(30, min(100, score))
    
    def _calc_bazi(self, cand: EventCandidate) -> int:
        """計算八字配合分數"""
        score = 75
        
        if cand.chong_owner:
            score -= 30
        
        if self.owner_chart and len(cand.ganzhi) >= 2:
            rike = calc_rike_score(self.owner_chart, cand.ganzhi[0], cand.ganzhi[1])
            if rike.sheng_yongshen:
                score += 15
                cand.event_ji_shen.append("生用神")
            if rike.ke_jishen:
                score += 10
                cand.event_ji_shen.append("剋忌神")
            if rike.chong_mingzhu:
                score -= 20
                cand.event_xiong_shen.append("沖命主")
        
        return max(30, min(100, score))
    
    def select_dates(self, start_date: date, end_date: date,
                     top_n: int = 10) -> List[EventCandidate]:
        """選擇吉日"""
        self.candidates = []
        
        current = start_date
        while current <= end_date:
            year_gz, month_gz, day_gz = get_ganzhi_from_date(current)
            lunar_month = current.month
            lunar_day = current.day
            
            cand = self.analyze_date(
                current, year_gz, month_gz, day_gz,
                lunar_month, lunar_day
            )
            self.candidates.append(cand)
            current += timedelta(days=1)
        
        self.candidates.sort(key=lambda x: -x.score.weighted_total)
        
        filtered = [c for c in self.candidates 
                    if c.score.weighted_total >= 800 and not c.chong_owner]
        
        return filtered[:top_n]
    
    def print_result(self, candidates: List[EventCandidate] = None):
        """輸出結果"""
        if candidates is None:
            candidates = self.candidates[:10]
        
        print("═" * 75)
        print(f"        {self.event_type.value}擇日結果")
        if self.owner_sx:
            print(f"        事主：{self.owner_sx}（{self.owner_zhi}）")
        print("═" * 75)
        
        for i, cand in enumerate(candidates, 1):
            s = cand.score
            
            rike_str = ""
            jishi_str = ""
            if cand.full_rike:
                rike = cand.full_rike
                rike_str = f"\n    ┌─────────────────────────────────────────┐\n" \
                           f"    │  完整日課：{rike.full_rike:<28} │\n" \
                           f"    │  最佳時辰：{rike.hour_gz}（{rike.hour_score}分）{' '*17}│\n" \
                           f"    └─────────────────────────────────────────┘"
                jishi_str = ', '.join([f'{gz}' for _, gz, sc in rike.jishi_list[:4] if sc >= 75])
            
            print(f"""
  【#{i}】{cand.date} {cand.ganzhi}（農曆{cand.lunar}）
  {rike_str}
    黃道：{cand.huangdao_shen}（{s.huangdao}分）
    建除：{cand.jianchu}（{s.jianchu}分）
    二十八宿：{cand.xiu}（{s.xiu}分）
    沖煞：沖{cand.chong_sx}，煞{cand.sha_fang}（{s.chongsha}分）
    
    {self.event_type.value}吉神：{', '.join(cand.event_ji_shen) if cand.event_ji_shen else '無'}
    {self.event_type.value}凶神：{', '.join(cand.event_xiong_shen) if cand.event_xiong_shen else '無'}
    
    吉時選項：{jishi_str}
    加權總分：{s.weighted_total:.1f}
            """)


# ════════════════════════════════════════════════════════════════════
# L4: 便捷函數
# ════════════════════════════════════════════════════════════════════

def select_kaishi_date(start: date, end: date, owner_year: int = None, top_n: int = 10):
    """開市擇日"""
    owner_zhi = DIZHI[(owner_year - 4) % 12] if owner_year else None
    selector = EventDateSelector(EventType.KAISHI, owner_zhi)
    return selector.select_dates(start, end, top_n)

def select_banjia_date(start: date, end: date, owner_year: int = None, top_n: int = 10):
    """搬家擇日"""
    owner_zhi = DIZHI[(owner_year - 4) % 12] if owner_year else None
    selector = EventDateSelector(EventType.BANJIA, owner_zhi)
    return selector.select_dates(start, end, top_n)

def select_anchuang_date(start: date, end: date, owner_year: int = None, top_n: int = 10):
    """安床擇日"""
    owner_zhi = DIZHI[(owner_year - 4) % 12] if owner_year else None
    selector = EventDateSelector(EventType.ANCHUANG, owner_zhi)
    return selector.select_dates(start, end, top_n)

def select_jisi_date(start: date, end: date, owner_year: int = None, top_n: int = 10):
    """祭祀擇日"""
    owner_zhi = DIZHI[(owner_year - 4) % 12] if owner_year else None
    selector = EventDateSelector(EventType.JISI, owner_zhi)
    return selector.select_dates(start, end, top_n)

def select_chuxing_date(start: date, end: date, owner_year: int = None, top_n: int = 10):
    """出行擇日"""
    owner_zhi = DIZHI[(owner_year - 4) % 12] if owner_year else None
    selector = EventDateSelector(EventType.CHUXING, owner_zhi)
    return selector.select_dates(start, end, top_n)


# ════════════════════════════════════════════════════════════════════
# 測試
# ════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("═" * 75)
    print("        多用途擇日模組 - 2026年測試")
    print("═" * 75)
    
    start = date(2026, 3, 1)
    end = date(2026, 3, 31)
    owner_year = 1985
    
    # 測試各用途
    for event_type in EventType:
        print(f"\n【{event_type.value}擇日】")
        owner_zhi = DIZHI[(owner_year - 4) % 12]
        selector = EventDateSelector(event_type, owner_zhi)
        results = selector.select_dates(start, end, top_n=2)
        
        for r in results:
            rike = r.full_rike
            print(f"  {r.date} {r.ganzhi} → {rike.full_rike if rike else ''}")
            print(f"    {r.huangdao_shen}/{r.jianchu}/{r.xiu} = {r.score.weighted_total:.0f}分")
    
    print("\n" + "═" * 75)
