"""
姓名學引擎 name_engine.py v1.0 20260206
========================================
三才五格姓名學：筆畫計算、五格配置、三才五行、81數理吉凶

📚 知識點：
- 三才五格由熊崎健翁（日本）系統化
- 筆畫以康熙字典繁體為準
- 五格：天格(先天)、人格(主運核心)、地格(基礎)、外格(人際)、總格(後運)
- 三才=天格人格地格的五行配置，連續相生為最佳
- 81數理吉凶表是數字命理學的核心查詢表
"""

from dataclasses import dataclass
from wuxing_core import WX_ORDER, wx_relation


# ===== 81數理吉凶表（完整版） =====
# 格式：數字 → (吉凶, 卦名, 簡述)
SULI_81 = {
    1:  ("大吉", "太極之數", "萬物開泰，最大吉祥運"),
    2:  ("大凶", "一身孤節", "混沌未定，分離破敗"),
    3:  ("大吉", "進取如意", "智勇得志，博得名利"),
    4:  ("大凶", "破敗凶變", "日被雲遮，身遭殘害"),
    5:  ("大吉", "種竹成林", "福祿長壽，陰陽和合"),
    6:  ("大吉", "安穩餘慶", "天德地祥，吉人天相"),
    7:  ("吉",   "精悍剛毅", "精力充沛，推進萬象"),
    8:  ("吉",   "意志堅剛", "鐵石之功，蓄養實力"),
    9:  ("凶",   "破舟入海", "大成大敗，窮迫逆境"),
    10: ("凶",   "零暗萬業", "萬事終結，前途黯淡"),
    11: ("大吉", "旱苗逢雨", "萬物更新，天賦吉運"),
    12: ("凶",   "掘井無泉", "意志薄弱，有志難伸"),
    13: ("大吉", "春日牡丹", "才藝多能，天賦吉運"),
    14: ("大凶", "破兆",     "浮沉不定，有智謀但多挫折，家族緣薄"),
    15: ("大吉", "福壽",     "福壽圓滿，富貴榮譽"),
    16: ("大吉", "厚重",     "貴人得助，興家成業，有德望，能服眾"),
    17: ("半吉", "剛強",     "權威剛強，突破萬難，有領導力但需謙和"),
    18: ("大吉", "鐵鏡重磨", "有志竟成，內外吉祥，能成大業"),
    19: ("凶",   "多難",     "智慧優秀但運途多險，克服困難後可成功"),
    20: ("凶",   "屋下藏金", "非業破運，百事不如意"),
    21: ("大吉", "明月中天", "光風霽月，萬物確立"),
    22: ("凶",   "秋草逢霜", "百事不如意，志望半途而廢"),
    23: ("大吉", "壯麗",     "旭日東升，偉大昌隆"),
    24: ("大吉", "掘藏得金", "家門餘慶，錦上添花"),
    25: ("吉",   "資性英敏", "天資聰慧，宜守不宜進"),
    26: ("凶中吉", "變怪",   "英雄豪傑，波瀾壯闊，變化萬端"),
    27: ("凶",   "欲望難滿", "自我心強，多受誹謗"),
    28: ("大凶", "闊水浮萍", "豪傑氣概但遭難運"),
    29: ("吉",   "智謀",     "天賦幸運，可成大事"),
    30: ("半吉半凶", "非運",   "沉浮不定，吉凶難分"),
    31: ("大吉", "春日花開", "智勇得志，統御萬物"),
    32: ("大吉", "寶馬金鞍", "僥倖多望，貴人得助，財帛豐裕，繁榮至上"),
    33: ("大吉", "升天",     "旭日昇天，功名顯達"),
    34: ("大凶", "破家",     "破家之兆，損財難免"),
    35: ("吉",   "高樓望月", "溫和平靜，優雅發展"),
    36: ("凶",   "波瀾",     "風浪不息，俠義薄運"),
    37: ("吉",   "猛虎出林", "權威顯達，吉人天相"),
    38: ("半吉", "磨鐵成針", "有志竟成，技藝成名"),
    39: ("吉",   "富貴榮華", "光明磊落，權利顯達"),
    40: ("半凶", "退安",     "智謀膽力，嘗盡波瀾"),
    41: ("大吉", "有德",     "純陽獨秀，德望兼備"),
    42: ("凶",   "寒蟬在柳", "博達多能，十藝九不成"),
    43: ("凶",   "散財",     "雨夜之花，外祥內苦"),
    44: ("凶",   "煩悶",     "暗藏殺機，破壞難免"),
    45: ("大吉", "順風",     "新生泰和，順風揚帆"),
    46: ("凶",   "浪裏淘金", "載寶沉舟，須防暗礁"),
    47: ("大吉", "點石成金", "開花結子，權威進展"),
    48: ("吉",   "古松立鶴", "智謀兼備，德望高大"),
    49: ("凶",   "轉變",     "吉凶難分，凶多吉少"),
    50: ("半吉半凶", "小舟入海", "成敗各半，先盛後衰"),
    51: ("半吉半凶", "沉浮",   "盛衰交加，先成後敗"),
    52: ("大吉", "達眼",     "卓識達眼，先見之明"),
    53: ("凶",   "曲卷難星", "外祥內患，盛衰參半"),
    54: ("大凶", "石上栽花", "多難短命"),
    55: ("半吉半凶", "善惡",   "善善惡惡，大成大敗"),
    56: ("凶",   "浪裏行舟", "歷盡艱難，四周障礙"),
    57: ("吉",   "日照春松", "寒雪青松，最宜持守"),
    58: ("半吉", "晚行遇月", "先苦後甘，寬宏大量"),
    59: ("凶",   "寒蟬悲風", "須防外患"),
    60: ("凶",   "無謀",     "暗淡無光，動搖不安"),
    61: ("吉",   "牡丹芙蓉", "名利雙收，繁華富貴"),
    62: ("凶",   "衰敗",     "內外不和，萬事逐漸衰退"),
    63: ("吉",   "舟歸平海", "富貴尊榮，身心安泰"),
    64: ("凶",   "非命",     "骨肉分離，孤獨悲慘"),
    65: ("大吉", "巨流歸海", "富貴長壽，家運隆昌"),
    66: ("凶",   "岩頭步馬", "身心不安，進退維谷"),
    67: ("大吉", "通達",     "利路亨通，萬事皆吉"),
    68: ("大吉", "順風吹帆", "興家立業，一統天下"),
    69: ("凶",   "非業",     "坐立不安，動搖不定"),
    70: ("凶",   "殘敗",     "家勢衰退，孤獨寂寞"),
    71: ("半吉", "石上金花", "吉凶各半，宜靜守"),
    72: ("凶",   "勞苦",     "先甘後苦，萬難艱辛"),
    73: ("半吉", "天地明月", "志高力微，宜腳踏實地"),
    74: ("凶",   "殘菊逢霜", "無勇無謀，退縮自保"),
    75: ("半吉", "退守",     "守則可安，進則難成"),
    76: ("凶",   "離散",     "骨肉離散，獨身悲愁"),
    77: ("半吉半凶", "半吉",   "先吉後凶，須引以為戒"),
    78: ("半吉", "晚苦",     "晚年冷淡，有才無命"),
    79: ("凶",   "雲頭望月", "挫折困難，事業不成"),
    80: ("半吉", "遁吉",     "辛苦嘗盡，可獲成功"),
    81: ("大吉", "萬物回春", "等同1數，最極之數還歸太極"),
}


def num_to_wx(n: int) -> str:
    """
    數字→五行（三才五格用）
    
    📚 規則：尾數1,2=木  3,4=火  5,6=土  7,8=金  9,0=水
    """
    last = n % 10
    if last in [1, 2]: return "木"
    if last in [3, 4]: return "火"
    if last in [5, 6]: return "土"
    if last in [7, 8]: return "金"
    return "水"


@dataclass
class WuGeResult:
    """五格計算結果"""
    # 基本資料
    xing: str              # 姓
    ming: list[str]        # 名（可1-2字）
    kangxi_strokes: dict   # 康熙筆畫
    
    # 五格數值
    tian: int   # 天格
    ren: int    # 人格
    di: int     # 地格
    wai: int    # 外格
    zong: int   # 總格
    
    @property
    def tian_wx(self): return num_to_wx(self.tian)
    @property
    def ren_wx(self): return num_to_wx(self.ren)
    @property
    def di_wx(self): return num_to_wx(self.di)
    @property
    def wai_wx(self): return num_to_wx(self.wai)
    @property
    def zong_wx(self): return num_to_wx(self.zong)
    
    @property
    def sancai(self) -> tuple:
        """三才配置（天→人→地）"""
        return (self.tian_wx, self.ren_wx, self.di_wx)
    
    @property
    def sancai_str(self) -> str:
        return f"{self.tian_wx}→{self.ren_wx}→{self.di_wx}"
    
    def sancai_relations(self) -> list[str]:
        """三才生剋關係"""
        return [
            f"天→人: {self.tian_wx}→{self.ren_wx} = {wx_relation(self.tian_wx, self.ren_wx)}",
            f"人→地: {self.ren_wx}→{self.di_wx} = {wx_relation(self.ren_wx, self.di_wx)}",
        ]
    
    def is_sancai_liansheng(self) -> bool:
        """三才是否連續相生"""
        r1 = wx_relation(self.tian_wx, self.ren_wx)
        r2 = wx_relation(self.ren_wx, self.di_wx)
        # 天生人 + 人生地 = 連續相生
        return r1 in ("我生", "生我") and r2 in ("我生", "生我")
    
    def suli_info(self, ge_name: str, num: int) -> dict:
        """查81數理吉凶"""
        key = num if num <= 81 else ((num - 1) % 80 + 1)
        info = SULI_81.get(key, ("未知", "—", "—"))
        return {
            "格": ge_name,
            "數": num,
            "五行": num_to_wx(num),
            "吉凶": info[0],
            "名": info[1],
            "述": info[2],
        }
    
    def all_suli(self) -> list[dict]:
        """全部五格的數理吉凶"""
        return [
            self.suli_info("天格", self.tian),
            self.suli_info("人格", self.ren),
            self.suli_info("地格", self.di),
            self.suli_info("外格", self.wai),
            self.suli_info("總格", self.zong),
        ]
    
    def summary(self) -> str:
        lines = [
            f"姓名：{''.join([self.xing] + self.ming)}",
            f"康熙筆畫：{self.kangxi_strokes}",
            f"",
            f"  天格={self.tian}({self.tian_wx})  人格={self.ren}({self.ren_wx})",
            f"  地格={self.di}({self.di_wx})  外格={self.wai}({self.wai_wx})",
            f"  總格={self.zong}({self.zong_wx})",
            f"  三才：{self.sancai_str}",
        ]
        for r in self.sancai_relations():
            lines.append(f"    {r}")
        if self.is_sancai_liansheng():
            lines.append(f"    ★ 三才連續相生=極佳配置")
        
        lines.append(f"")
        for s in self.all_suli():
            lines.append(f"  {s['格']}{s['數']}({s['五行']})：{s['吉凶']}「{s['名']}」{s['述']}")
        
        return "\n".join(lines)


def calculate_wuge(xing: str, ming: list[str], kangxi: dict) -> WuGeResult:
    """
    計算五格
    
    Parameters:
        xing: 姓氏（單字）
        ming: 名字列表（1-2字）
        kangxi: 康熙筆畫字典 {字: 筆畫數}
    
    📚 五格公式（單姓雙名）：
    天格 = 姓筆畫 + 1（先天，不論吉凶）
    人格 = 姓 + 名1（核心主運，最重要）
    地格 = 名1 + 名2（前運/基礎）
    外格 = 總格 - 人格 + 1（人際環境）
    總格 = 姓 + 名1 + 名2（後運/一生總結）
    
    📚 特殊情況：
    - 單姓單名：天格=姓+1, 人格=姓+名, 地格=名+1, 外格=2, 總格=姓+名
    - 複姓雙名：天格=姓1+姓2, 人格=姓2+名1, 地格=名1+名2, 外格=姓1+名2, 總格=全部
    """
    s = kangxi[xing]
    
    if len(ming) == 2:
        m1 = kangxi[ming[0]]
        m2 = kangxi[ming[1]]
        tian = s + 1
        ren = s + m1
        di = m1 + m2
        zong = s + m1 + m2
        wai = zong - ren + 1
    elif len(ming) == 1:
        m1 = kangxi[ming[0]]
        tian = s + 1
        ren = s + m1
        di = m1 + 1
        zong = s + m1
        wai = 2
    else:
        raise ValueError("名字需1-2字")
    
    return WuGeResult(
        xing=xing, ming=ming,
        kangxi_strokes=kangxi,
        tian=tian, ren=ren, di=di, wai=wai, zong=zong,
    )


def cross_with_bazi(wuge: WuGeResult, day_master_wx: str, 
                    missing_wx: list[str]) -> list[str]:
    """
    姓名五行與八字交叉分析
    
    Parameters:
        wuge: 五格結果
        day_master_wx: 日主五行（如 "金"）
        missing_wx: 八字缺少的五行列表
    
    Returns: 分析結論列表
    """
    findings = []
    
    # 人格（核心）對日主的關係
    ren_rel = wx_relation(wuge.ren_wx, day_master_wx)
    if ren_rel == "生我":
        findings.append(f"人格{wuge.ren}({wuge.ren_wx})生日主({day_master_wx})=有利，姓名核心能量助命")
    elif ren_rel == "剋我":
        findings.append(f"人格{wuge.ren}({wuge.ren_wx})剋日主({day_master_wx})=有壓力")
    elif ren_rel == "比和":
        findings.append(f"人格{wuge.ren}({wuge.ren_wx})與日主({day_master_wx})比和=自我增強")
    
    # 五格五行是否補缺
    all_wx = {wuge.tian_wx, wuge.ren_wx, wuge.di_wx, wuge.wai_wx, wuge.zong_wx}
    for m in missing_wx:
        if m in all_wx:
            findings.append(f"姓名五行含{m}，補八字所缺")
        else:
            findings.append(f"姓名五行未補缺{m}")
    
    return findings


# ===== 常用康熙字典筆畫表（可擴充） =====
# 這是預設的小型字典，實際使用需要完整的康熙筆畫資料庫
KANGXI_COMMON = {
    "楊": 13, "三": 3, "興": 15,  # 北斗實測修正：興=15畫
    "王": 4, "李": 7, "張": 11, "劉": 15, "陳": 16,
    "林": 8, "黃": 12, "吳": 7, "趙": 14, "周": 8,
    "國": 11, "志": 7, "明": 8, "華": 14, "文": 4,
    "家": 10, "建": 9, "德": 15, "天": 4, "大": 3,
    "宏": 7, "偉": 11, "子": 3, "永": 5, "美": 9,
}


if __name__ == "__main__":
    print("=" * 60)
    print("楊三興 — 三才五格姓名學分析")
    print("=" * 60)
    
    kangxi = {"楊": 13, "三": 3, "興": 15}
    result = calculate_wuge("楊", ["三", "興"], kangxi)
    print(f"\n{result.summary()}")
    
    # 與八字交叉
    print(f"\n{'=' * 60}")
    print("姓名 × 八字 交叉分析")
    print("=" * 60)
    findings = cross_with_bazi(result, "金", ["火"])
    for f in findings:
        print(f"  · {f}")
