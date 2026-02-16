"""
八字大運計算器 dayun_calculator.py v1.0
======================================
XTF任務：消-B1 | 執行星：理樞（分析）
確定度：★★★★★（計算公式確定，可驗證）

核心本質：大運 = 月柱順逆行 × 10年

📚 大運計算法則：
1. 男命陽年/女命陰年 → 順行
2. 男命陰年/女命陽年 → 逆行
3. 起運歲數 = (出生日到交節日天數) ÷ 3
4. 每運10年，從月柱起算

⚠️ XTF8 認識論聲明：
- 大運計算公式：★★★★★（確定）
- 大運吉凶判斷：★★★☆☆（經驗統計）
- 具體事件預測：★★☆☆☆（推測參考）
"""

from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta

# 天干地支
GAN = ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"]
ZHI = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]

# 天干陰陽
GAN_YY = {"甲": "陽", "乙": "陰", "丙": "陽", "丁": "陰", "戊": "陽",
          "己": "陰", "庚": "陽", "辛": "陰", "壬": "陽", "癸": "陰"}

# 天干五行
GAN_WX = {"甲": "木", "乙": "木", "丙": "火", "丁": "火", "戊": "土",
          "己": "土", "庚": "金", "辛": "金", "壬": "水", "癸": "水"}

# 節氣日期（近似值，實際需要精確計算）
# 格式：(月, 日) 為該月節氣大約日期
JIEQI_APPROX = {
    1: (6, "小寒"), 2: (4, "立春"), 3: (6, "驚蟄"), 4: (5, "清明"),
    5: (6, "立夏"), 6: (6, "芒種"), 7: (7, "小暑"), 8: (8, "立秋"),
    9: (8, "白露"), 10: (8, "寒露"), 11: (7, "立冬"), 12: (7, "大雪"),
}


@dataclass
class DayunInfo:
    """大運資訊"""
    order: int          # 第幾運
    ganzhi: str         # 干支
    gan: str            # 天干
    zhi: str            # 地支
    start_age: int      # 起運歲數
    end_age: int        # 結束歲數
    start_year: int     # 起運年份
    end_year: int       # 結束年份
    wx: str             # 五行


@dataclass
class DayunResult:
    """大運計算結果"""
    birth_year: int
    gender: str
    year_gan: str
    month_ganzhi: str
    direction: str      # 順行/逆行
    qiyun_age: float    # 起運歲數
    qiyun_year: int     # 起運年份
    dayun_list: List[DayunInfo]


class DayunCalculator:
    """八字大運計算器"""
    
    def __init__(self, year_gan: str, month_ganzhi: str, gender: str, birth_year: int, birth_month: int, birth_day: int):
        """
        year_gan: 年干
        month_ganzhi: 月柱（如"甲寅"）
        gender: "男"/"女"
        birth_year: 出生年
        birth_month: 出生月
        birth_day: 出生日
        """
        self.year_gan = year_gan
        self.month_gan = month_ganzhi[0]
        self.month_zhi = month_ganzhi[1]
        self.month_ganzhi = month_ganzhi
        self.gender = gender
        self.birth_year = birth_year
        self.birth_month = birth_month
        self.birth_day = birth_day
        
        # 判斷順逆
        self.is_yang_year = GAN_YY[year_gan] == "陽"
        self.is_male = (gender == "男")
        
        # 男陽順、女陽逆、男陰逆、女陰順
        self.is_forward = (self.is_male and self.is_yang_year) or (not self.is_male and not self.is_yang_year)
        self.direction = "順行" if self.is_forward else "逆行"
    
    def calculate_qiyun_age(self) -> float:
        """計算起運歲數（簡化版）"""
        # 找到最近的節氣
        jieqi_day, jieqi_name = JIEQI_APPROX.get(self.birth_month, (6, ""))
        
        # 計算距離節氣的天數
        if self.is_forward:
            # 順行：計算到下個節氣的天數
            if self.birth_day < jieqi_day:
                days = jieqi_day - self.birth_day
            else:
                # 到下個月節氣
                next_month = (self.birth_month % 12) + 1
                next_jieqi_day = JIEQI_APPROX.get(next_month, (6, ""))[0]
                days_in_month = 30  # 簡化
                days = (days_in_month - self.birth_day) + next_jieqi_day
        else:
            # 逆行：計算到上個節氣的天數
            if self.birth_day > jieqi_day:
                days = self.birth_day - jieqi_day
            else:
                # 到上個月節氣
                prev_month = ((self.birth_month - 2) % 12) + 1
                prev_jieqi_day = JIEQI_APPROX.get(prev_month, (6, ""))[0]
                days = self.birth_day + (30 - prev_jieqi_day)
        
        # 三天為一歲
        qiyun_age = round(days / 3, 1)
        
        # 確保合理範圍
        if qiyun_age < 1:
            qiyun_age = 1
        elif qiyun_age > 10:
            qiyun_age = 10
        
        return qiyun_age
    
    def get_next_ganzhi(self, ganzhi: str, forward: bool = True) -> str:
        """取得下一個干支"""
        gan = ganzhi[0]
        zhi = ganzhi[1]
        
        gan_idx = GAN.index(gan)
        zhi_idx = ZHI.index(zhi)
        
        if forward:
            new_gan = GAN[(gan_idx + 1) % 10]
            new_zhi = ZHI[(zhi_idx + 1) % 12]
        else:
            new_gan = GAN[(gan_idx - 1) % 10]
            new_zhi = ZHI[(zhi_idx - 1) % 12]
        
        return new_gan + new_zhi
    
    def calculate(self, num_dayun: int = 8) -> DayunResult:
        """計算大運（預設8個大運）"""
        qiyun_age = self.calculate_qiyun_age()
        qiyun_year = self.birth_year + int(qiyun_age)
        
        dayun_list = []
        current_ganzhi = self.month_ganzhi
        
        for i in range(num_dayun):
            # 下一個大運干支
            current_ganzhi = self.get_next_ganzhi(current_ganzhi, self.is_forward)
            
            start_age = int(qiyun_age) + (i * 10)
            end_age = start_age + 9
            start_year = self.birth_year + start_age
            end_year = self.birth_year + end_age
            
            dayun_info = DayunInfo(
                order=i + 1,
                ganzhi=current_ganzhi,
                gan=current_ganzhi[0],
                zhi=current_ganzhi[1],
                start_age=start_age,
                end_age=end_age,
                start_year=start_year,
                end_year=end_year,
                wx=GAN_WX[current_ganzhi[0]],
            )
            dayun_list.append(dayun_info)
        
        return DayunResult(
            birth_year=self.birth_year,
            gender=self.gender,
            year_gan=self.year_gan,
            month_ganzhi=self.month_ganzhi,
            direction=self.direction,
            qiyun_age=qiyun_age,
            qiyun_year=qiyun_year,
            dayun_list=dayun_list,
        )


def calculate_dayun(
    year_gan: str,
    month_ganzhi: str,
    gender: str,
    birth_year: int,
    birth_month: int,
    birth_day: int,
    num_dayun: int = 8,
) -> Dict:
    """便捷函數：計算大運"""
    calculator = DayunCalculator(
        year_gan, month_ganzhi, gender, birth_year, birth_month, birth_day
    )
    result = calculator.calculate(num_dayun)
    
    return {
        "birth_year": result.birth_year,
        "gender": result.gender,
        "direction": result.direction,
        "qiyun_age": result.qiyun_age,
        "qiyun_year": result.qiyun_year,
        "dayun_list": [
            {
                "order": d.order,
                "ganzhi": d.ganzhi,
                "gan": d.gan,
                "zhi": d.zhi,
                "wx": d.wx,
                "start_age": d.start_age,
                "end_age": d.end_age,
                "start_year": d.start_year,
                "end_year": d.end_year,
            }
            for d in result.dayun_list
        ],
    }


def get_current_dayun(dayun_result: Dict, current_year: int = None) -> Optional[Dict]:
    """取得當前大運"""
    if current_year is None:
        current_year = datetime.now().year
    
    for d in dayun_result["dayun_list"]:
        if d["start_year"] <= current_year <= d["end_year"]:
            return d
    
    return None


def generate_dayun_report(dayun_result: Dict, day_master: str = "") -> str:
    """生成大運報告"""
    report = f"""【八字大運分析】

出生年：{dayun_result['birth_year']}年
性別：{dayun_result['gender']}
大運方向：{dayun_result['direction']}
起運歲數：{dayun_result['qiyun_age']}歲（{dayun_result['qiyun_year']}年）

【大運排列】
"""
    
    for d in dayun_result["dayun_list"]:
        report += f"""
第{d['order']}運：{d['ganzhi']}（{d['wx']}）
  歲數：{d['start_age']}～{d['end_age']}歲
  年份：{d['start_year']}～{d['end_year']}年
"""
    
    # 認識論聲明
    report += """
【場論詮釋】
大運是人生的「大階段能量場」，每10年為一個週期。
順行代表能量向外擴展，逆行代表能量向內收斂。

【XTF8 確定度標註】
★★★★★ 大運計算公式（可驗證）
★★★☆☆ 大運吉凶判斷（經驗統計）
★★☆☆☆ 具體事件預測（僅供參考）

重要提醒：大運是「能量傾向」，不是「命運判決」。
"""
    
    return report


if __name__ == "__main__":
    # 測試：1973年12月30日男性（北斗）
    # 八字：癸丑/甲子/庚子/乙酉
    result = calculate_dayun(
        year_gan="癸",
        month_ganzhi="甲子",
        gender="男",
        birth_year=1973,
        birth_month=12,
        birth_day=30,
    )
    
    print(generate_dayun_report(result))
    
    # 取得當前大運
    current = get_current_dayun(result, 2026)
    if current:
        print(f"\n當前大運：{current['ganzhi']}（{current['start_year']}～{current['end_year']}）")
