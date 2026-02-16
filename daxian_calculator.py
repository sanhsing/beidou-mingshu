"""
紫微大限計算器 daxian_calculator.py v1.0
=======================================
XTF任務：消-B3 | 執行星：理樞（分析）
確定度：★★★★★（計算公式確定）

核心本質：大限 = 命宮起10年順逆行

📚 大限計算法則：
1. 陽男陰女順行，陰男陽女逆行
2. 從命宮開始，每宮10年
3. 第一大限歲數由局數決定

局數與起限歲數：
- 水二局：2歲起限
- 木三局：3歲起限
- 金四局：4歲起限
- 土五局：5歲起限
- 火六局：6歲起限

⚠️ XTF8 認識論聲明：
- 大限計算公式：★★★★★（確定）
- 大限吉凶傾向：★★★☆☆（經驗統計）
- 具體事件預測：★★☆☆☆（參考性質）
"""

from typing import Dict, List, Optional
from dataclasses import dataclass

# 十二宮名稱（順序）
GONG_NAMES = ["命宮", "父母", "福德", "田宅", "官祿", "僕役", 
              "遷移", "疾厄", "財帛", "子女", "夫妻", "兄弟"]

# 十二地支
ZHI = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]

# 局數與起限歲數
JU_START_AGE = {
    "水二局": 2,
    "木三局": 3,
    "金四局": 4,
    "土五局": 5,
    "火六局": 6,
}

# 年干陰陽
GAN_YY = {"甲": "陽", "乙": "陰", "丙": "陽", "丁": "陰", "戊": "陽",
          "己": "陰", "庚": "陽", "辛": "陰", "壬": "陽", "癸": "陰"}


@dataclass
class DaxianInfo:
    """大限資訊"""
    order: int           # 第幾大限
    gong_name: str       # 宮位名稱
    gong_zhi: str        # 宮位地支
    start_age: int       # 起始歲數
    end_age: int         # 結束歲數
    start_year: int      # 起始年份
    end_year: int        # 結束年份
    main_stars: List[str]  # 該宮主星


@dataclass
class DaxianResult:
    """大限計算結果"""
    birth_year: int
    gender: str
    ju_shu: str
    ming_gong_idx: int
    direction: str
    start_age: int
    daxian_list: List[DaxianInfo]


class DaxianCalculator:
    """紫微大限計算器"""
    
    def __init__(
        self,
        year_gan: str,
        gender: str,
        ju_shu: str,
        ming_gong_idx: int,
        birth_year: int,
        gongs: List[Dict] = None,
    ):
        """
        year_gan: 年干
        gender: "男"/"女"
        ju_shu: 局數（如"金四局"）
        ming_gong_idx: 命宮索引（0-11）
        birth_year: 出生年
        gongs: 十二宮資料（可選，用於取主星）
        """
        self.year_gan = year_gan
        self.gender = gender
        self.ju_shu = ju_shu
        self.ming_gong_idx = ming_gong_idx
        self.birth_year = birth_year
        self.gongs = gongs or []
        
        # 判斷順逆
        is_yang = GAN_YY.get(year_gan) == "陽"
        is_male = (gender == "男")
        
        # 陽男陰女順行，陰男陽女逆行
        self.is_forward = (is_yang and is_male) or (not is_yang and not is_male)
        self.direction = "順行" if self.is_forward else "逆行"
        
        # 起限歲數
        self.start_age = JU_START_AGE.get(ju_shu, 4)
    
    def calculate(self, num_daxian: int = 8) -> DaxianResult:
        """計算大限"""
        daxian_list = []
        
        for i in range(num_daxian):
            # 計算宮位索引
            if self.is_forward:
                gong_idx = (self.ming_gong_idx + i) % 12
            else:
                gong_idx = (self.ming_gong_idx - i) % 12
            
            # 計算歲數
            start_age = self.start_age + (i * 10)
            end_age = start_age + 9
            start_year = self.birth_year + start_age
            end_year = self.birth_year + end_age
            
            # 取得宮位資料
            gong_name = GONG_NAMES[gong_idx]
            gong_zhi = ZHI[gong_idx]  # 簡化，實際需要根據命盤
            
            # 取得主星（如果有）
            main_stars = []
            if self.gongs and len(self.gongs) > gong_idx:
                main_stars = self.gongs[gong_idx].get("main_stars", [])
            
            daxian_info = DaxianInfo(
                order=i + 1,
                gong_name=gong_name,
                gong_zhi=gong_zhi,
                start_age=start_age,
                end_age=end_age,
                start_year=start_year,
                end_year=end_year,
                main_stars=main_stars,
            )
            daxian_list.append(daxian_info)
        
        return DaxianResult(
            birth_year=self.birth_year,
            gender=self.gender,
            ju_shu=self.ju_shu,
            ming_gong_idx=self.ming_gong_idx,
            direction=self.direction,
            start_age=self.start_age,
            daxian_list=daxian_list,
        )


def calculate_daxian(
    year_gan: str,
    gender: str,
    ju_shu: str,
    ming_gong_idx: int,
    birth_year: int,
    gongs: List[Dict] = None,
    num_daxian: int = 8,
) -> Dict:
    """便捷函數：計算大限"""
    calculator = DaxianCalculator(
        year_gan, gender, ju_shu, ming_gong_idx, birth_year, gongs
    )
    result = calculator.calculate(num_daxian)
    
    return {
        "birth_year": result.birth_year,
        "gender": result.gender,
        "ju_shu": result.ju_shu,
        "direction": result.direction,
        "start_age": result.start_age,
        "daxian_list": [
            {
                "order": d.order,
                "gong_name": d.gong_name,
                "gong_zhi": d.gong_zhi,
                "start_age": d.start_age,
                "end_age": d.end_age,
                "start_year": d.start_year,
                "end_year": d.end_year,
                "main_stars": d.main_stars,
            }
            for d in result.daxian_list
        ],
    }


def get_current_daxian(daxian_result: Dict, current_year: int = None) -> Optional[Dict]:
    """取得當前大限"""
    if current_year is None:
        from datetime import datetime
        current_year = datetime.now().year
    
    for d in daxian_result["daxian_list"]:
        if d["start_year"] <= current_year <= d["end_year"]:
            return d
    
    return None


def generate_daxian_report(daxian_result: Dict) -> str:
    """生成大限報告"""
    report = f"""【紫微大限分析】

出生年：{daxian_result['birth_year']}年
性別：{daxian_result['gender']}
局數：{daxian_result['ju_shu']}
大限方向：{daxian_result['direction']}
起限歲數：{daxian_result['start_age']}歲

【大限排列】
"""
    
    for d in daxian_result["daxian_list"]:
        stars_str = "、".join(d["main_stars"]) if d["main_stars"] else "無主星"
        report += f"""
第{d['order']}大限：{d['gong_name']}（{d['gong_zhi']}）
  歲數：{d['start_age']}～{d['end_age']}歲
  年份：{d['start_year']}～{d['end_year']}年
  主星：{stars_str}
"""
    
    report += """
【場論詮釋】
大限是紫微斗數的「人生大階段」，每10年換一個能量場。
行經不同宮位，代表該階段的人生主題和能量特質。

【XTF8 確定度標註】
★★★★★ 大限計算公式（可驗證）
★★★☆☆ 大限吉凶傾向（經驗統計）
★★☆☆☆ 具體事件預測（僅供參考）

重要提醒：大限是「能量背景」，不是「命運劇本」。
"""
    
    return report


# 大限宮位白話詮釋
DAXIAN_GONG_MEANING = {
    "命宮": {
        "theme": "自我發展",
        "vernacular": "這10年關於「我是誰」",
        "focus": "個人成長、自我定位、人生方向",
        "advice": "專注自我提升，建立核心競爭力",
    },
    "父母": {
        "theme": "長輩關係",
        "vernacular": "這10年關於「長輩緣分」",
        "focus": "與長輩的關係、學習傳承、庇護",
        "advice": "孝順父母，學習長輩智慧",
    },
    "福德": {
        "theme": "心靈品質",
        "vernacular": "這10年關於「內心世界」",
        "focus": "精神生活、興趣愛好、心靈成長",
        "advice": "培養興趣，注重精神層面",
    },
    "田宅": {
        "theme": "家庭不動產",
        "vernacular": "這10年關於「房子和家」",
        "focus": "購屋、搬遷、家庭環境、不動產",
        "advice": "關注居住環境，可考慮置產",
    },
    "官祿": {
        "theme": "事業工作",
        "vernacular": "這10年關於「事業發展」",
        "focus": "職業、事業、工作成就、社會地位",
        "advice": "全力拼事業，把握升遷機會",
    },
    "僕役": {
        "theme": "人際朋友",
        "vernacular": "這10年關於「人脈交友」",
        "focus": "朋友、下屬、人際關係、社交",
        "advice": "經營人脈，善待朋友和部屬",
    },
    "遷移": {
        "theme": "外出變動",
        "vernacular": "這10年關於「往外發展」",
        "focus": "出外、旅行、搬遷、外地發展",
        "advice": "適合向外發展，把握外地機會",
    },
    "疾厄": {
        "theme": "健康身體",
        "vernacular": "這10年關於「健康管理」",
        "focus": "身體健康、疾病、意外、保險",
        "advice": "注重健康，定期檢查，買好保險",
    },
    "財帛": {
        "theme": "財富收入",
        "vernacular": "這10年關於「賺錢理財」",
        "focus": "收入、財富、投資、消費",
        "advice": "積極理財，開源節流並重",
    },
    "子女": {
        "theme": "子女緣分",
        "vernacular": "這10年關於「子女教育」",
        "focus": "生育、子女、教育、傳承",
        "advice": "關注子女教育，培養下一代",
    },
    "夫妻": {
        "theme": "感情婚姻",
        "vernacular": "這10年關於「感情婚姻」",
        "focus": "戀愛、婚姻、伴侶關係",
        "advice": "經營感情，溝通很重要",
    },
    "兄弟": {
        "theme": "平輩關係",
        "vernacular": "這10年關於「平輩合作」",
        "focus": "兄弟姐妹、同事、合作夥伴",
        "advice": "與平輩合作，互助互利",
    },
}


def get_daxian_meaning(gong_name: str) -> Dict:
    """取得大限宮位詮釋"""
    return DAXIAN_GONG_MEANING.get(gong_name, {
        "theme": "綜合",
        "vernacular": "這10年綜合發展",
        "focus": "多方面發展",
        "advice": "平衡各方面",
    })


if __name__ == "__main__":
    # 測試：1973年12月30日男性
    result = calculate_daxian(
        year_gan="癸",
        gender="男",
        ju_shu="金四局",
        ming_gong_idx=6,  # 假設命宮在午宮
        birth_year=1973,
    )
    
    print(generate_daxian_report(result))
    
    # 取得當前大限
    current = get_current_daxian(result, 2026)
    if current:
        meaning = get_daxian_meaning(current["gong_name"])
        print(f"\n當前大限：{current['gong_name']}（{current['start_year']}～{current['end_year']}）")
        print(f"主題：{meaning['vernacular']}")
        print(f"建議：{meaning['advice']}")
