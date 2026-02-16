"""
梅花易數引擎 meihua_engine.py v1.0 20260206
============================================
邵雍法標準梅花易數：起卦、互卦、變卦、體用分析

📚 知識點：
- 先天八卦數：乾1兌2離3震4巽5坎6艮7坤8
- 上卦=(年支+月+日) % 8，下卦=(年支+月+日+時支) % 8
- 動爻=(年支+月+日+時支) % 6
- 體用：動爻所在卦=用，不動卦=體
- 互卦：2,3,4爻為下互，3,4,5爻為上互
"""

from dataclasses import dataclass
from wuxing_core import ZHI_NUM, WX_ORDER, wx_relation

# ===== 先天八卦 =====
GUA_NAME = {
    1: "乾(天)", 2: "兌(澤)", 3: "離(火)", 4: "震(雷)",
    5: "巽(風)", 6: "坎(水)", 7: "艮(山)", 8: "坤(地)",
}
GUA_SHORT = {1: "乾", 2: "兌", 3: "離", 4: "震", 5: "巽", 6: "坎", 7: "艮", 8: "坤"}

# 先天八卦五行
GUA_WX = {
    "乾": "金", "兌": "金", "離": "火", "震": "木",
    "巽": "木", "坎": "水", "艮": "土", "坤": "土",
}

# 八卦爻象（從下到上）: 1=陽, 0=陰
GUA_YAO = {
    1: [1, 1, 1],  # 乾
    2: [1, 1, 0],  # 兌
    3: [1, 0, 1],  # 離
    4: [1, 0, 0],  # 震
    5: [0, 1, 1],  # 巽
    6: [0, 1, 0],  # 坎
    7: [0, 0, 1],  # 艮
    8: [0, 0, 0],  # 坤
}

# 反查：爻象→卦數
YAO_TO_GUA = {tuple(v): k for k, v in GUA_YAO.items()}

# 64卦名（上卦, 下卦）→ 卦名
HEX_NAMES = {
    (1,1): "乾為天(1)", (1,2): "天澤履(10)", (1,3): "天火同人(13)", (1,4): "天雷無妄(25)",
    (1,5): "天風姤(44)", (1,6): "天水訟(6)", (1,7): "天山遯(33)", (1,8): "天地否(12)",
    (2,1): "澤天夬(43)", (2,2): "兌為澤(58)", (2,3): "澤火革(49)", (2,4): "澤雷隨(17)",
    (2,5): "澤風大過(28)", (2,6): "澤水困(47)", (2,7): "澤山咸(31)", (2,8): "澤地萃(45)",
    (3,1): "火天大有(14)", (3,2): "火澤睽(38)", (3,3): "離為火(30)", (3,4): "火雷噬嗑(21)",
    (3,5): "火風鼎(50)", (3,6): "火水未濟(64)", (3,7): "火山旅(56)", (3,8): "火地晉(35)",
    (4,1): "雷天大壯(34)", (4,2): "雷澤歸妹(54)", (4,3): "雷火豐(55)", (4,4): "震為雷(51)",
    (4,5): "雷風恆(32)", (4,6): "雷水解(40)", (4,7): "雷山小過(62)", (4,8): "雷地豫(16)",
    (5,1): "風天小畜(9)", (5,2): "風澤中孚(61)", (5,3): "風火家人(37)", (5,4): "風雷益(42)",
    (5,5): "巽為風(57)", (5,6): "風水渙(59)", (5,7): "風山漸(53)", (5,8): "風地觀(20)",
    (6,1): "水天需(5)", (6,2): "水澤節(60)", (6,3): "水火既濟(63)", (6,4): "水雷屯(3)",
    (6,5): "水風井(48)", (6,6): "坎為水(29)", (6,7): "水山蹇(39)", (6,8): "水地比(8)",
    (7,1): "山天大畜(26)", (7,2): "山澤損(41)", (7,3): "山火賁(22)", (7,4): "山雷頤(27)",
    (7,5): "山風蠱(18)", (7,6): "山水蒙(4)", (7,7): "艮為山(52)", (7,8): "山地剝(23)",
    (8,1): "地天泰(11)", (8,2): "地澤臨(19)", (8,3): "地火明夷(36)", (8,4): "地雷復(24)",
    (8,5): "地風升(46)", (8,6): "地水師(7)", (8,7): "地山謙(15)", (8,8): "坤為地(2)",
}


@dataclass
class Hexagram:
    """一卦的完整結構"""
    upper: int         # 上卦數 1-8
    lower: int         # 下卦數 1-8
    dong_yao: int      # 動爻位置 1-6
    
    @property
    def name(self) -> str:
        return HEX_NAMES.get((self.upper, self.lower), f"{GUA_SHORT[self.upper]}上{GUA_SHORT[self.lower]}下")
    
    @property
    def upper_name(self) -> str: return GUA_SHORT[self.upper]
    @property
    def lower_name(self) -> str: return GUA_SHORT[self.lower]
    @property
    def upper_wx(self) -> str: return GUA_WX[self.upper_name]
    @property
    def lower_wx(self) -> str: return GUA_WX[self.lower_name]
    
    @property
    def six_yao(self) -> list:
        """六爻（從下到上）"""
        return GUA_YAO[self.lower] + GUA_YAO[self.upper]
    
    @property
    def bian_gua(self) -> 'Hexagram':
        """變卦：動爻變後的卦"""
        yao = list(self.six_yao)
        idx = self.dong_yao - 1
        yao[idx] = 1 - yao[idx]
        new_lower = YAO_TO_GUA[tuple(yao[0:3])]
        new_upper = YAO_TO_GUA[tuple(yao[3:6])]
        return Hexagram(new_upper, new_lower, 0)
    
    @property
    def hu_gua(self) -> 'Hexagram':
        """互卦：2,3,4爻為下互，3,4,5爻為上互"""
        yao = self.six_yao
        hu_lower = YAO_TO_GUA[tuple(yao[1:4])]
        hu_upper = YAO_TO_GUA[tuple(yao[2:5])]
        return Hexagram(hu_upper, hu_lower, 0)
    
    @property
    def ti_gua(self) -> int:
        """體卦：動爻不在的那個卦"""
        if self.dong_yao <= 3:
            return self.upper  # 動在下=下為用，上為體
        else:
            return self.lower  # 動在上=上為用，下為體
    
    @property
    def yong_gua(self) -> int:
        """用卦：動爻所在的卦"""
        if self.dong_yao <= 3:
            return self.lower
        else:
            return self.upper
    
    @property
    def ti_wx(self) -> str: return GUA_WX[GUA_SHORT[self.ti_gua]]
    @property
    def yong_wx(self) -> str: return GUA_WX[GUA_SHORT[self.yong_gua]]
    
    def ti_yong_relation(self) -> str:
        """體用五行生剋關係"""
        return wx_relation(self.ti_wx, self.yong_wx)


def num_mod(n: int, mod: int) -> int:
    """取餘，0替換為mod值（梅花特殊規則）"""
    r = n % mod
    return mod if r == 0 else r


def qigua_birthday(year_zhi_num: int, lunar_month: int, 
                   lunar_day: int, hour_zhi_num: int) -> Hexagram:
    """
    出生年月日時起卦（本命卦）
    
    Parameters:
        year_zhi_num: 年支序數（子1丑2...亥12）
        lunar_month: 農曆月（1-12）
        lunar_day: 農曆日（1-30）
        hour_zhi_num: 時支序數（子1丑2...亥12）
    
    📚 邵雍法：
    上卦 = (年支+月+日) % 8
    下卦 = (年支+月+日+時支) % 8  
    動爻 = (年支+月+日+時支) % 6
    """
    sum_upper = year_zhi_num + lunar_month + lunar_day
    sum_total = sum_upper + hour_zhi_num
    
    upper = num_mod(sum_upper, 8)
    lower = num_mod(sum_total, 8)
    dong = num_mod(sum_total, 6)
    
    return Hexagram(upper, lower, dong)


def qigua_flow_year(benming_total: int, liu_gan_num: int, 
                    liu_zhi_num: int, year_zhi_num: int,
                    liu_year_zhi_num: int) -> Hexagram:
    """
    本命+流年配數起卦
    
    Parameters:
        benming_total: 本命卦的全數（年支+月+日+時支）
        liu_gan_num: 流年天干序（甲1乙2...癸10→實用3=丙）
        liu_zhi_num: 流年地支序（子1...午7）
        year_zhi_num: 本命年支序
        liu_year_zhi_num: 流年地支序
    """
    sum_u = year_zhi_num + liu_year_zhi_num
    sum_l = benming_total + liu_gan_num + liu_zhi_num
    dong = num_mod(sum_l, 6)
    
    upper = num_mod(sum_u, 8)
    lower = num_mod(sum_l, 8)
    
    return Hexagram(upper, lower, dong)


def qigua_pure_year(year_zhi_num: int, month: int = 1,
                    day: int = 1, hour_zhi_num: int = 3) -> Hexagram:
    """
    純流年卦（如立春時刻起卦）
    
    Parameters:
        year_zhi_num: 流年地支序
        month: 農曆月（預設正月）
        day: 農曆日（預設初一）
        hour_zhi_num: 時支序（預設寅3=立春）
    """
    return qigua_birthday(year_zhi_num, month, day, hour_zhi_num)


@dataclass
class TiYongAnalysis:
    """體用分析結果"""
    hexagram: Hexagram
    ti_name: str
    yong_name: str
    ti_wx: str
    yong_wx: str
    relation: str
    verdict: str
    hu_analysis: str
    bian_analysis: str


def analyze_tiyong(hex_: Hexagram) -> TiYongAnalysis:
    """
    體用生剋分析
    
    📚 體用原則：
    - 體剋用=有財、可掌控
    - 用剋體=外部壓力施加於己
    - 用生體=外力助我
    - 體生用=洩氣、付出
    - 比和=勢均力敵、自我增強
    """
    rel = hex_.ti_yong_relation()
    
    verdict_map = {
        "我剋": "體剋用=有財、可掌控局面",
        "剋我": "用剋體=外部壓力施加於己",
        "生我": "用生體=外力助我、有資源",
        "我生": "體生用=洩氣、付出消耗",
        "比和": "體用比和=勢均力敵、自我增強",
    }
    
    # 互卦分析
    hu = hex_.hu_gua
    hu_upper_wx = GUA_WX[GUA_SHORT[hu.upper]]
    hu_lower_wx = GUA_WX[GUA_SHORT[hu.lower]]
    hu_rel_ti = wx_relation(hu_upper_wx, hex_.ti_wx)
    hu_parts = []
    if hu_upper_wx == hex_.ti_wx or wx_relation(hu_upper_wx, hex_.ti_wx) == "生我":
        hu_parts.append(f"上互{GUA_SHORT[hu.upper]}({hu_upper_wx})助體")
    if hu_lower_wx == hex_.ti_wx or wx_relation(hu_lower_wx, hex_.ti_wx) == "生我":
        hu_parts.append(f"下互{GUA_SHORT[hu.lower]}({hu_lower_wx})助體")
    hu_text = "；".join(hu_parts) if hu_parts else f"互卦{hu.name}"
    
    # 變卦分析
    bian = hex_.bian_gua
    bian_yong_wx = GUA_WX[GUA_SHORT[bian.upper if hex_.dong_yao > 3 else bian.lower]]
    bian_rel = wx_relation(bian_yong_wx, hex_.ti_wx)
    bian_text = f"變卦{bian.name}，變後用卦{bian_yong_wx}對體{bian_rel}"
    
    return TiYongAnalysis(
        hexagram=hex_,
        ti_name=GUA_SHORT[hex_.ti_gua],
        yong_name=GUA_SHORT[hex_.yong_gua],
        ti_wx=hex_.ti_wx,
        yong_wx=hex_.yong_wx,
        relation=rel,
        verdict=verdict_map.get(rel, rel),
        hu_analysis=hu_text,
        bian_analysis=bian_text,
    )


def full_meihua(year_zhi_num: int, lunar_month: int,
                lunar_day: int, hour_zhi_num: int,
                label: str = "梅花卦") -> dict:
    """
    完整梅花易數分析
    
    Returns: 包含本卦、變卦、互卦、體用分析的字典
    """
    hex_ = qigua_birthday(year_zhi_num, lunar_month, lunar_day, hour_zhi_num)
    analysis = analyze_tiyong(hex_)
    
    return {
        "label": label,
        "ben_gua": hex_,
        "bian_gua": hex_.bian_gua,
        "hu_gua": hex_.hu_gua,
        "ti_yong": analysis,
        "params": {
            "year_zhi": year_zhi_num,
            "month": lunar_month,
            "day": lunar_day,
            "hour_zhi": hour_zhi_num,
            "sum_upper": year_zhi_num + lunar_month + lunar_day,
            "sum_total": year_zhi_num + lunar_month + lunar_day + hour_zhi_num,
        },
    }


if __name__ == "__main__":
    # ===== 驗證：楊三興本命卦 =====
    # 丑年(2) 農曆12月 初七 酉時(10)
    print("=" * 60)
    print("楊三興 梅花易數")
    print("=" * 60)
    
    result = full_meihua(2, 12, 7, 10, "本命卦")
    hex_ = result["ben_gua"]
    p = result["params"]
    
    print(f"\n取數：年支(丑)={p['year_zhi']}, 月={p['month']}, "
          f"日={p['day']}, 時支(酉)={p['hour_zhi']}")
    print(f"  上卦數={p['sum_upper']} % 8 = {num_mod(p['sum_upper'], 8)} → {GUA_NAME[hex_.upper]}")
    print(f"  下卦數={p['sum_total']} % 8 = {num_mod(p['sum_total'], 8)} → {GUA_NAME[hex_.lower]}")
    print(f"  動爻 ={p['sum_total']} % 6 = {hex_.dong_yao}")
    
    print(f"\n本卦：{hex_.name}")
    print(f"變卦：{hex_.bian_gua.name}")
    print(f"互卦：{hex_.hu_gua.name}")
    
    ty = result["ti_yong"]
    print(f"\n體用分析：")
    print(f"  體卦：{ty.ti_name}({ty.ti_wx})")
    print(f"  用卦：{ty.yong_name}({ty.yong_wx})")
    print(f"  關係：{ty.relation} → {ty.verdict}")
    print(f"  {ty.hu_analysis}")
    print(f"  {ty.bian_analysis}")
    
    # 本命+流年（2026丙午）
    print(f"\n{'=' * 60}")
    print("本命+2026丙午流年")
    print("=" * 60)
    hex2 = qigua_flow_year(31, 3, 7, 2, 7)  # 本命total=31, 丙=3, 午=7
    print(f"本卦：{hex2.name}")
    print(f"變卦：{hex2.bian_gua.name}")
    print(f"互卦：{hex2.hu_gua.name}")
    ty2 = analyze_tiyong(hex2)
    print(f"體={ty2.ti_name}({ty2.ti_wx}) 用={ty2.yong_name}({ty2.yong_wx}) → {ty2.verdict}")
