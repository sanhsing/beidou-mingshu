"""
大運流年整合模組 fortune_timeline.py v1.0
========================================
XTF任務：拓-T1 | 執行星：流祇（連結）

整合功能：
- 八字大運 (dayun_calculator)
- 八字流年 (liunian_analyzer)
- 紫微大限 (daxian_calculator)
- 紫微流年 (待實現)

📚 時間軸整合概念：
大運/大限 = 10年能量週期
流年 = 1年能量背景
月運 = 1月能量細節
日運 = 1日能量參考
"""

from typing import Dict, List, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass

# 導入各模組
from dayun_calculator import calculate_dayun, get_current_dayun, generate_dayun_report
from liunian_analyzer import analyze_liunian, analyze_liunian_range, generate_liunian_report
from daxian_calculator import calculate_daxian, get_current_daxian, generate_daxian_report, get_daxian_meaning


@dataclass
class FortuneTimeline:
    """運勢時間軸"""
    birth_year: int
    gender: str
    # 八字
    bazi_dayun: List[Dict]
    bazi_liunian: List[Dict]
    current_bazi_dayun: Dict
    current_bazi_liunian: Dict
    # 紫微
    ziwei_daxian: List[Dict]
    current_ziwei_daxian: Dict
    # 綜合
    current_year: int
    overall_tendency: str
    overall_advice: str


class FortuneTimelineBuilder:
    """運勢時間軸建構器"""
    
    def __init__(
        self,
        # 基本資料
        birth_year: int,
        birth_month: int,
        birth_day: int,
        gender: str,
        # 八字資料
        year_gan: str,
        month_ganzhi: str,
        day_master: str,
        pillars: Dict[str, str],
        is_strong: bool = True,
        # 紫微資料
        ju_shu: str = "",
        ming_gong_idx: int = 0,
        gongs: List[Dict] = None,
    ):
        self.birth_year = birth_year
        self.birth_month = birth_month
        self.birth_day = birth_day
        self.gender = gender
        
        # 八字
        self.year_gan = year_gan
        self.month_ganzhi = month_ganzhi
        self.day_master = day_master
        self.pillars = pillars
        self.is_strong = is_strong
        
        # 紫微
        self.ju_shu = ju_shu
        self.ming_gong_idx = ming_gong_idx
        self.gongs = gongs or []
        
        self.current_year = datetime.now().year
    
    def build(self, num_fortune: int = 8, num_liunian: int = 10) -> FortuneTimeline:
        """建構完整時間軸"""
        
        # 八字大運
        bazi_dayun_result = calculate_dayun(
            self.year_gan, self.month_ganzhi, self.gender,
            self.birth_year, self.birth_month, self.birth_day, num_fortune
        )
        bazi_dayun = bazi_dayun_result["dayun_list"]
        current_bazi_dayun = get_current_dayun(bazi_dayun_result, self.current_year) or {}
        
        # 八字流年
        bazi_liunian = analyze_liunian_range(
            self.day_master, self.pillars, self.current_year, num_liunian, self.is_strong
        )
        current_bazi_liunian = analyze_liunian(
            self.day_master, self.pillars, self.current_year, self.is_strong
        )
        
        # 紫微大限
        ziwei_daxian = []
        current_ziwei_daxian = {}
        if self.ju_shu:
            daxian_result = calculate_daxian(
                self.year_gan, self.gender, self.ju_shu,
                self.ming_gong_idx, self.birth_year, self.gongs, num_fortune
            )
            ziwei_daxian = daxian_result["daxian_list"]
            current_ziwei_daxian = get_current_daxian(daxian_result, self.current_year) or {}
        
        # 綜合判斷
        overall_tendency, overall_advice = self._analyze_overall(
            current_bazi_dayun, current_bazi_liunian, current_ziwei_daxian
        )
        
        return FortuneTimeline(
            birth_year=self.birth_year,
            gender=self.gender,
            bazi_dayun=bazi_dayun,
            bazi_liunian=bazi_liunian,
            current_bazi_dayun=current_bazi_dayun,
            current_bazi_liunian=current_bazi_liunian,
            ziwei_daxian=ziwei_daxian,
            current_ziwei_daxian=current_ziwei_daxian,
            current_year=self.current_year,
            overall_tendency=overall_tendency,
            overall_advice=overall_advice,
        )
    
    def _analyze_overall(
        self,
        dayun: Dict,
        liunian: Dict,
        daxian: Dict,
    ) -> Tuple[str, str]:
        """綜合分析當前運勢"""
        
        # 收集傾向
        tendencies = []
        
        if liunian.get("tendency"):
            tendencies.append(liunian["tendency"])
        
        # 簡單加權判斷
        ji_count = tendencies.count("吉")
        xiong_count = tendencies.count("凶")
        ping_count = tendencies.count("平")
        
        if ji_count > xiong_count:
            overall = "整體有利"
        elif xiong_count > ji_count:
            overall = "整體需謹慎"
        else:
            overall = "整體平穩"
        
        # 建議
        advices = []
        if liunian.get("advice"):
            advices.append(liunian["advice"])
        if daxian.get("gong_name"):
            meaning = get_daxian_meaning(daxian["gong_name"])
            advices.append(meaning.get("advice", ""))
        
        overall_advice = "；".join(filter(None, advices))
        
        return overall, overall_advice


def build_fortune_timeline(
    birth_year: int,
    birth_month: int,
    birth_day: int,
    gender: str,
    year_gan: str,
    month_ganzhi: str,
    day_master: str,
    pillars: Dict[str, str],
    is_strong: bool = True,
    ju_shu: str = "",
    ming_gong_idx: int = 0,
    gongs: List[Dict] = None,
) -> Dict:
    """便捷函數：建構運勢時間軸"""
    builder = FortuneTimelineBuilder(
        birth_year, birth_month, birth_day, gender,
        year_gan, month_ganzhi, day_master, pillars, is_strong,
        ju_shu, ming_gong_idx, gongs
    )
    timeline = builder.build()
    
    return {
        "birth_year": timeline.birth_year,
        "gender": timeline.gender,
        "current_year": timeline.current_year,
        "overall_tendency": timeline.overall_tendency,
        "overall_advice": timeline.overall_advice,
        "bazi_dayun": timeline.bazi_dayun,
        "bazi_liunian": timeline.bazi_liunian,
        "current_bazi_dayun": timeline.current_bazi_dayun,
        "current_bazi_liunian": timeline.current_bazi_liunian,
        "ziwei_daxian": timeline.ziwei_daxian,
        "current_ziwei_daxian": timeline.current_ziwei_daxian,
    }


def generate_fortune_report(timeline: Dict) -> str:
    """生成運勢報告"""
    current_year = timeline["current_year"]
    
    report = f"""
╔══════════════════════════════════════════════════════════════════╗
║              {current_year}年 運勢時間軸分析                            ║
╚══════════════════════════════════════════════════════════════════╝

【整體運勢】
傾向：{timeline['overall_tendency']}
建議：{timeline['overall_advice']}

"""
    
    # 當前八字大運
    if timeline['current_bazi_dayun']:
        d = timeline['current_bazi_dayun']
        report += f"""【當前八字大運】
  大運：{d.get('ganzhi', '')}（{d.get('wx', '')}）
  期間：{d.get('start_age', '')}～{d.get('end_age', '')}歲（{d.get('start_year', '')}～{d.get('end_year', '')}年）

"""
    
    # 當前流年
    if timeline['current_bazi_liunian']:
        l = timeline['current_bazi_liunian']
        tendency_emoji = {"吉": "🟢", "平": "🟡", "凶": "🔴"}.get(l.get('tendency', ''), "⚪")
        report += f"""【{current_year}年流年分析】
  流年干支：{l.get('ganzhi', '')}
  十神：{l.get('gan_shishen', '')}
  傾向：{tendency_emoji} {l.get('tendency', '')}
  建議：{l.get('advice', '')}

"""
    
    # 當前紫微大限
    if timeline['current_ziwei_daxian']:
        dx = timeline['current_ziwei_daxian']
        meaning = get_daxian_meaning(dx.get('gong_name', ''))
        report += f"""【當前紫微大限】
  大限：{dx.get('gong_name', '')}宮
  期間：{dx.get('start_age', '')}～{dx.get('end_age', '')}歲（{dx.get('start_year', '')}～{dx.get('end_year', '')}年）
  主題：{meaning.get('vernacular', '')}
  建議：{meaning.get('advice', '')}

"""
    
    # 未來流年速覽
    report += "【未來5年流年速覽】\n"
    for l in timeline['bazi_liunian'][:5]:
        emoji = {"吉": "🟢", "平": "🟡", "凶": "🔴"}.get(l.get('tendency', ''), "⚪")
        report += f"  {l['year']}年 {l['ganzhi']}：{l['gan_shishen']} {emoji}\n"
    
    report += """
【XTF8 確定度標註】
★★★★★ 干支計算（確定）
★★★☆☆ 吉凶傾向（經驗統計）
★★☆☆☆ 具體事件（參考）

重要提醒：運勢分析是「能量傾向參考」，不是「命運劇本」。
最終結果取決於個人行動和選擇。
"""
    
    return report


if __name__ == "__main__":
    # 測試：1973年12月30日男性（北斗）
    pillars = {
        "year": "癸丑",
        "month": "甲子",
        "day": "庚子",
        "hour": "乙酉",
    }
    
    timeline = build_fortune_timeline(
        birth_year=1973,
        birth_month=12,
        birth_day=30,
        gender="男",
        year_gan="癸",
        month_ganzhi="甲子",
        day_master="庚",
        pillars=pillars,
        is_strong=False,
        ju_shu="金四局",
        ming_gong_idx=6,
    )
    
    print(generate_fortune_report(timeline))
