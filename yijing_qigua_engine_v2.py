"""
易經起卦引擎 yijing_qigua_engine_v2.py v2.0
==========================================
XTF任務：拓-T | 執行星：織明
優化：二進制位運算
日期：2026-02-08

核心洞見：
- 易經 = 6-bit 狀態機
- 卦 = 6-bit 整數 (0-63)
- 動爻 = 翻轉對應 bit
- 變卦 = XOR 運算

修正：八卦二進制對應（從下到上，初爻→三爻）
"""

from typing import Dict, Tuple
from dataclasses import dataclass

# ============================================================
# 核心常量
# ============================================================

# 天干地支序數
TIANGAN = '甲乙丙丁戊己庚辛壬癸'
TIANGAN_NUM = {g: i+1 for i, g in enumerate(TIANGAN)}

DIZHI = '子丑寅卯辰巳午未申酉戌亥'
DIZHI_NUM = {z: i+1 for i, z in enumerate(DIZHI)}

# 八卦先天數 → 名稱/符號
NUM_TO_GUA = {1: '乾', 2: '兌', 3: '離', 4: '震', 5: '巽', 6: '坎', 7: '艮', 8: '坤'}
GUA_TO_NUM = {v: k for k, v in NUM_TO_GUA.items()}
BAGUA_SYMBOL = {1: '☰', 2: '☱', 3: '☲', 4: '☳', 5: '☴', 6: '☵', 7: '☶', 8: '☷'}

# 八卦二進制（bit2=上爻, bit1=中爻, bit0=初爻）
# 陽=1, 陰=0
BAGUA_BIN = {
    '乾': 0b111,  # ☰ 陽陽陽
    '兌': 0b011,  # ☱ 陰陽陽（上陰）
    '離': 0b101,  # ☲ 陽陰陽（中陰）
    '震': 0b001,  # ☳ 陰陰陽（初陽）
    '巽': 0b110,  # ☴ 陽陽陰（初陰）
    '坎': 0b010,  # ☵ 陰陽陰（中陽）
    '艮': 0b100,  # ☶ 陽陰陰（上陽）
    '坤': 0b000,  # ☷ 陰陰陰
}

# 二進制 → 八卦名
BIN_TO_GUA = {v: k for k, v in BAGUA_BIN.items()}

# 六十四卦：(上卦名, 下卦名) → 卦序
GUA_64_MAP = {
    ('乾','乾'):1,  ('乾','坤'):12, ('乾','震'):25, ('乾','艮'):33,
    ('乾','坎'):6,  ('乾','離'):13, ('乾','巽'):44, ('乾','兌'):10,
    ('坤','乾'):11, ('坤','坤'):2,  ('坤','震'):24, ('坤','艮'):15,
    ('坤','坎'):7,  ('坤','離'):36, ('坤','巽'):46, ('坤','兌'):19,
    ('震','乾'):34, ('震','坤'):16, ('震','震'):51, ('震','艮'):62,
    ('震','坎'):3,  ('震','離'):55, ('震','巽'):32, ('震','兌'):54,
    ('艮','乾'):26, ('艮','坤'):23, ('艮','震'):27, ('艮','艮'):52,
    ('艮','坎'):4,  ('艮','離'):22, ('艮','巽'):18, ('艮','兌'):41,
    ('坎','乾'):5,  ('坎','坤'):8,  ('坎','震'):40, ('坎','艮'):39,
    ('坎','坎'):29, ('坎','離'):64, ('坎','巽'):48, ('坎','兌'):60,
    ('離','乾'):14, ('離','坤'):35, ('離','震'):21, ('離','艮'):56,
    ('離','坎'):63, ('離','離'):30, ('離','巽'):50, ('離','兌'):38,
    ('巽','乾'):9,  ('巽','坤'):20, ('巽','震'):42, ('巽','艮'):53,
    ('巽','坎'):59, ('巽','離'):37, ('巽','巽'):57, ('巽','兌'):61,
    ('兌','乾'):43, ('兌','坤'):45, ('兌','震'):17, ('兌','艮'):31,
    ('兌','坎'):47, ('兌','離'):49, ('兌','巽'):28, ('兌','兌'):58,
}

# 卦序 → (上卦, 下卦)
GUA_64_REVERSE = {v: k for k, v in GUA_64_MAP.items()}

GUA_64_NAME = {
    1: '乾', 2: '坤', 3: '屯', 4: '蒙', 5: '需', 6: '訟', 7: '師', 8: '比',
    9: '小畜', 10: '履', 11: '泰', 12: '否', 13: '同人', 14: '大有', 15: '謙', 16: '豫',
    17: '隨', 18: '蠱', 19: '臨', 20: '觀', 21: '噬嗑', 22: '賁', 23: '剝', 24: '復',
    25: '无妄', 26: '大畜', 27: '頤', 28: '大過', 29: '坎', 30: '離', 31: '咸', 32: '恆',
    33: '遯', 34: '大壯', 35: '晉', 36: '明夷', 37: '家人', 38: '睽', 39: '蹇', 40: '解',
    41: '損', 42: '益', 43: '夬', 44: '姤', 45: '萃', 46: '升', 47: '困', 48: '井',
    49: '革', 50: '鼎', 51: '震', 52: '艮', 53: '漸', 54: '歸妹', 55: '豐', 56: '旅',
    57: '巽', 58: '兌', 59: '渙', 60: '節', 61: '中孚', 62: '小過', 63: '既濟', 64: '未濟'
}

# ============================================================
# 核心函數
# ============================================================

def num_to_bagua_name(n: int) -> str:
    """餘數 → 八卦名"""
    r = n % 8
    num = 8 if r == 0 else r
    return NUM_TO_GUA[num]

def num_to_yao(n: int) -> int:
    """餘數 → 動爻位置 (1-6)"""
    r = n % 6
    return 6 if r == 0 else r

def gua_to_6bit(upper: str, lower: str) -> int:
    """上下卦 → 6-bit 整數"""
    upper_bin = BAGUA_BIN[upper]
    lower_bin = BAGUA_BIN[lower]
    return (upper_bin << 3) | lower_bin

def bit6_to_gua(bit6: int) -> Tuple[str, str]:
    """6-bit → 上下卦名"""
    upper_bin = (bit6 >> 3) & 0b111
    lower_bin = bit6 & 0b111
    return BIN_TO_GUA.get(upper_bin, '?'), BIN_TO_GUA.get(lower_bin, '?')

def flip_yao(bit6: int, yao_pos: int) -> int:
    """翻轉動爻 (XOR)
    
    yao_pos: 1=初爻(bit0), 2=二爻(bit1), ..., 6=上爻(bit5)
    """
    mask = 1 << (yao_pos - 1)
    return bit6 ^ mask

def get_bian_gua(upper: str, lower: str, dong_yao: int) -> Tuple[str, str]:
    """計算變卦"""
    bit6 = gua_to_6bit(upper, lower)
    bian_bit6 = flip_yao(bit6, dong_yao)
    return bit6_to_gua(bian_bit6)

def get_cuo_gua(upper: str, lower: str) -> Tuple[str, str]:
    """錯卦（六爻全反）"""
    bit6 = gua_to_6bit(upper, lower)
    return bit6_to_gua(bit6 ^ 0b111111)

def get_zong_gua(upper: str, lower: str) -> Tuple[str, str]:
    """綜卦（上下顛倒）"""
    return lower, upper

# ============================================================
# 起卦
# ============================================================

@dataclass
class QiGuaResult:
    method: str
    upper: str
    lower: str
    dong_yao: int
    ben_gua_num: int
    ben_gua_name: str
    ben_bit6: int
    bian_upper: str
    bian_lower: str
    bian_gua_num: int
    bian_gua_name: str
    bian_bit6: int
    calc: Dict

def qigua(y: int, m: int, d: int, h: int, method: str) -> QiGuaResult:
    """通用起卦"""
    upper_sum = y + m + d
    total_sum = y + m + d + h
    
    upper = num_to_bagua_name(upper_sum)
    lower = num_to_bagua_name(total_sum)
    dong_yao = num_to_yao(total_sum)
    
    ben_gua_num = GUA_64_MAP.get((upper, lower), 0)
    ben_gua_name = GUA_64_NAME.get(ben_gua_num, '?')
    ben_bit6 = gua_to_6bit(upper, lower)
    
    bian_upper, bian_lower = get_bian_gua(upper, lower, dong_yao)
    bian_gua_num = GUA_64_MAP.get((bian_upper, bian_lower), 0)
    bian_gua_name = GUA_64_NAME.get(bian_gua_num, '?')
    bian_bit6 = gua_to_6bit(bian_upper, bian_lower)
    
    return QiGuaResult(
        method=method,
        upper=upper, lower=lower, dong_yao=dong_yao,
        ben_gua_num=ben_gua_num, ben_gua_name=ben_gua_name, ben_bit6=ben_bit6,
        bian_upper=bian_upper, bian_lower=bian_lower,
        bian_gua_num=bian_gua_num, bian_gua_name=bian_gua_name, bian_bit6=bian_bit6,
        calc={'y': y, 'm': m, 'd': d, 'h': h, 'upper_sum': upper_sum, 'total_sum': total_sum}
    )

def qigua_dizhi(y_zhi: str, m_zhi: str, d_zhi: str, h_zhi: str) -> QiGuaResult:
    return qigua(DIZHI_NUM[y_zhi], DIZHI_NUM[m_zhi], DIZHI_NUM[d_zhi], DIZHI_NUM[h_zhi], '地支法')

def qigua_tiangan(y_gan: str, m_gan: str, d_gan: str, h_gan: str) -> QiGuaResult:
    return qigua(TIANGAN_NUM[y_gan], TIANGAN_NUM[m_gan], TIANGAN_NUM[d_gan], TIANGAN_NUM[h_gan], '天干法')

def qigua_ganzhi(y_gan: str, y_zhi: str, m_gan: str, m_zhi: str,
                 d_gan: str, d_zhi: str, h_gan: str, h_zhi: str) -> QiGuaResult:
    y = TIANGAN_NUM[y_gan] + DIZHI_NUM[y_zhi]
    m = TIANGAN_NUM[m_gan] + DIZHI_NUM[m_zhi]
    d = TIANGAN_NUM[d_gan] + DIZHI_NUM[d_zhi]
    h = TIANGAN_NUM[h_gan] + DIZHI_NUM[h_zhi]
    return qigua(y, m, d, h, '干支合法')

# ============================================================
# 輸出
# ============================================================

def format_result(r: QiGuaResult) -> str:
    u_sym = BAGUA_SYMBOL[GUA_TO_NUM[r.upper]]
    l_sym = BAGUA_SYMBOL[GUA_TO_NUM[r.lower]]
    bu_sym = BAGUA_SYMBOL[GUA_TO_NUM[r.bian_upper]]
    bl_sym = BAGUA_SYMBOL[GUA_TO_NUM[r.bian_lower]]
    
    return f"""
【{r.method}】
計算：年={r.calc['y']} 月={r.calc['m']} 日={r.calc['d']} 時={r.calc['h']}
  上卦：{r.calc['upper_sum']} % 8 → {r.upper} {u_sym}
  下卦：{r.calc['total_sum']} % 8 → {r.lower} {l_sym}
  動爻：{r.calc['total_sum']} % 6 → {r.dong_yao}爻

本卦：{r.ben_gua_name}（{r.ben_gua_num}）{u_sym}{l_sym}  [{r.ben_bit6:06b}]
動爻：{r.dong_yao}爻 → XOR {(1 << (r.dong_yao-1)):06b}
變卦：{r.bian_gua_name}（{r.bian_gua_num}）{bu_sym}{bl_sym}  [{r.bian_bit6:06b}]
"""

# ============================================================
# 測試
# ============================================================

if __name__ == "__main__":
    print("=" * 60)
    print("【北斗八字起卦 v2】二進制版")
    print("八字：癸丑 乙丑 庚子 乙酉")
    print("=" * 60)
    
    # 三法測試
    r1 = qigua_dizhi('丑', '丑', '子', '酉')
    r2 = qigua_tiangan('癸', '乙', '庚', '乙')
    r3 = qigua_ganzhi('癸', '丑', '乙', '丑', '庚', '子', '乙', '酉')
    
    print(format_result(r1))
    print(format_result(r2))
    print(format_result(r3))
    
    print("=" * 60)
    print("【位運算示範】")
    print("=" * 60)
    
    # 漸卦錯卦綜卦
    upper, lower = GUA_64_REVERSE[53]
    bit6 = gua_to_6bit(upper, lower)
    print(f"\n漸卦(53) = {upper}{lower} = {bit6:06b}")
    
    cuo_u, cuo_l = get_cuo_gua(upper, lower)
    cuo_num = GUA_64_MAP.get((cuo_u, cuo_l), 0)
    print(f"錯卦（XOR 111111）：{cuo_u}{cuo_l} = {GUA_64_NAME.get(cuo_num)}（{cuo_num}）")
    
    zong_u, zong_l = get_zong_gua(upper, lower)
    zong_num = GUA_64_MAP.get((zong_u, zong_l), 0)
    print(f"綜卦（上下對調）：{zong_u}{zong_l} = {GUA_64_NAME.get(zong_num)}（{zong_num}）")
