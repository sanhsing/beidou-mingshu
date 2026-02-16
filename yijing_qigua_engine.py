"""
易經起卦引擎 yijing_qigua_engine.py v1.0
========================================
XTF任務：拓-T | 執行星：織明
逆向工程自：北斗案例
日期：2026-02-08

功能：
1. 三種起卦方法（地支/天干/干支合）
2. 動爻計算
3. 變卦推導
4. 綜合解卦
"""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass

# ============================================================
# 基礎常量
# ============================================================

# 天干序數（甲1...癸10）
TIANGAN = ['甲', '乙', '丙', '丁', '戊', '己', '庚', '辛', '壬', '癸']
TIANGAN_NUM = {g: i+1 for i, g in enumerate(TIANGAN)}

# 地支序數（子1...亥12）
DIZHI = ['子', '丑', '寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥']
DIZHI_NUM = {z: i+1 for i, z in enumerate(DIZHI)}

# 八卦序數（先天八卦序）
BAGUA_NUM = {1: '乾', 2: '兌', 3: '離', 4: '震', 5: '巽', 6: '坎', 7: '艮', 8: '坤', 0: '坤'}
NUM_BAGUA = {'乾': 1, '兌': 2, '離': 3, '震': 4, '巽': 5, '坎': 6, '艮': 7, '坤': 8}

# 八卦符號
BAGUA_SYMBOL = {
    '乾': '☰', '兌': '☱', '離': '☲', '震': '☳',
    '巽': '☴', '坎': '☵', '艮': '☶', '坤': '☷'
}

# 八卦爻結構（從下到上：0=陰，1=陽）
BAGUA_YAO = {
    '乾': [1, 1, 1], '兌': [1, 1, 0], '離': [1, 0, 1], '震': [0, 0, 1],
    '巽': [1, 1, 0], '坎': [0, 1, 0], '艮': [0, 0, 1], '坤': [0, 0, 0]
}

# 修正：八卦爻結構（從下到上）
BAGUA_YAO = {
    '乾': [1, 1, 1],  # ━━━ ━━━ ━━━
    '兌': [0, 1, 1],  # ━━━ ━━━ ━ ━
    '離': [1, 0, 1],  # ━━━ ━ ━ ━━━
    '震': [1, 0, 0],  # ━ ━ ━ ━ ━━━
    '巽': [0, 1, 1],  # ━━━ ━━━ ━ ━  (注意：巽是陽陽陰從下到上)
    '坎': [0, 1, 0],  # ━ ━ ━━━ ━ ━
    '艮': [1, 0, 0],  # ━ ━ ━ ━ ━━━  (注意：艮是陽陰陰從下到上)
    '坤': [0, 0, 0]   # ━ ━ ━ ━ ━ ━
}

# 再次修正：八卦爻結構（從下到上，初爻→二爻→三爻）
BAGUA_YAO = {
    '乾': [1, 1, 1],  # 三爻全陽
    '坤': [0, 0, 0],  # 三爻全陰
    '震': [1, 0, 0],  # 初陽、二陰、三陰
    '艮': [0, 0, 1],  # 初陰、二陰、三陽
    '坎': [0, 1, 0],  # 初陰、二陽、三陰
    '離': [1, 0, 1],  # 初陽、二陰、三陽
    '巽': [0, 1, 1],  # 初陰、二陽、三陽
    '兌': [1, 1, 0],  # 初陽、二陽、三陰
}

# 64卦對照表（上卦, 下卦）-> 卦序
GUA_64_MAP = {
    ('乾', '乾'): 1,  ('坤', '乾'): 11, ('震', '乾'): 34, ('艮', '乾'): 26,
    ('坎', '乾'): 5,  ('離', '乾'): 14, ('巽', '乾'): 9,  ('兌', '乾'): 43,
    ('乾', '坤'): 12, ('坤', '坤'): 2,  ('震', '坤'): 16, ('艮', '坤'): 23,
    ('坎', '坤'): 8,  ('離', '坤'): 35, ('巽', '坤'): 20, ('兌', '坤'): 45,
    ('乾', '震'): 25, ('坤', '震'): 24, ('震', '震'): 51, ('艮', '震'): 27,
    ('坎', '震'): 3,  ('離', '震'): 21, ('巽', '震'): 42, ('兌', '震'): 17,
    ('乾', '艮'): 33, ('坤', '艮'): 15, ('震', '艮'): 62, ('艮', '艮'): 52,
    ('坎', '艮'): 39, ('離', '艮'): 56, ('巽', '艮'): 53, ('兌', '艮'): 31,
    ('乾', '坎'): 6,  ('坤', '坎'): 7,  ('震', '坎'): 40, ('艮', '坎'): 4,
    ('坎', '坎'): 29, ('離', '坎'): 64, ('巽', '坎'): 59, ('兌', '坎'): 47,
    ('乾', '離'): 13, ('坤', '離'): 36, ('震', '離'): 55, ('艮', '離'): 22,
    ('坎', '離'): 63, ('離', '離'): 30, ('巽', '離'): 37, ('兌', '離'): 49,
    ('乾', '巽'): 44, ('坤', '巽'): 46, ('震', '巽'): 32, ('艮', '巽'): 18,
    ('坎', '巽'): 48, ('離', '巽'): 50, ('巽', '巽'): 57, ('兌', '巽'): 28,
    ('乾', '兌'): 10, ('坤', '兌'): 19, ('震', '兌'): 54, ('艮', '兌'): 41,
    ('坎', '兌'): 60, ('離', '兌'): 38, ('巽', '兌'): 61, ('兌', '兌'): 58,
}

# 64卦名稱
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
# 資料結構
# ============================================================

@dataclass
class SiZhu:
    """四柱"""
    year_gan: str
    year_zhi: str
    month_gan: str
    month_zhi: str
    day_gan: str
    day_zhi: str
    hour_gan: str
    hour_zhi: str
    
    def get_gan_nums(self) -> Tuple[int, int, int, int]:
        """取天干序數"""
        return (
            TIANGAN_NUM[self.year_gan],
            TIANGAN_NUM[self.month_gan],
            TIANGAN_NUM[self.day_gan],
            TIANGAN_NUM[self.hour_gan]
        )
    
    def get_zhi_nums(self) -> Tuple[int, int, int, int]:
        """取地支序數"""
        return (
            DIZHI_NUM[self.year_zhi],
            DIZHI_NUM[self.month_zhi],
            DIZHI_NUM[self.day_zhi],
            DIZHI_NUM[self.hour_zhi]
        )

@dataclass
class GuaResult:
    """起卦結果"""
    method: str           # 起卦方法
    upper_gua: str        # 上卦
    lower_gua: str        # 下卦
    dong_yao: int         # 動爻位置（1-6）
    ben_gua_num: int      # 本卦序號
    ben_gua_name: str     # 本卦名
    bian_gua_num: int     # 變卦序號
    bian_gua_name: str    # 變卦名
    calc_detail: Dict     # 計算細節

# ============================================================
# 起卦計算
# ============================================================

def num_to_gua(num: int) -> str:
    """數字轉八卦（餘數對應）"""
    r = num % 8
    return BAGUA_NUM[r if r != 0 else 8]

def num_to_yao(num: int) -> int:
    """數字轉動爻位置（1-6）"""
    r = num % 6
    return r if r != 0 else 6

def get_bian_gua(upper: str, lower: str, dong_yao: int) -> Tuple[str, str]:
    """計算變卦
    
    dong_yao: 1-6，1是初爻（最下），6是上爻（最上）
    1-3爻在下卦，4-6爻在上卦
    """
    # 組合六爻（下卦3爻 + 上卦3爻）
    yao_list = BAGUA_YAO[lower].copy() + BAGUA_YAO[upper].copy()
    
    # 動爻變化（陽↔陰）
    idx = dong_yao - 1
    yao_list[idx] = 1 - yao_list[idx]
    
    # 重新拆分上下卦
    new_lower_yao = yao_list[:3]
    new_upper_yao = yao_list[3:]
    
    # 爻列表轉八卦
    def yao_to_gua(yao: List[int]) -> str:
        for name, pattern in BAGUA_YAO.items():
            if pattern == yao:
                return name
        return '?'
    
    return yao_to_gua(new_upper_yao), yao_to_gua(new_lower_yao)

def qigua_dizhi(sizhu: SiZhu) -> GuaResult:
    """地支法起卦"""
    y, m, d, h = sizhu.get_zhi_nums()
    
    upper_sum = y + m + d
    total_sum = y + m + d + h
    
    upper = num_to_gua(upper_sum)
    lower = num_to_gua(total_sum)
    dong = num_to_yao(total_sum)
    
    ben_gua_num = GUA_64_MAP.get((upper, lower), 0)
    ben_gua_name = GUA_64_NAME.get(ben_gua_num, '?')
    
    bian_upper, bian_lower = get_bian_gua(upper, lower, dong)
    bian_gua_num = GUA_64_MAP.get((bian_upper, bian_lower), 0)
    bian_gua_name = GUA_64_NAME.get(bian_gua_num, '?')
    
    return GuaResult(
        method='地支法',
        upper_gua=upper,
        lower_gua=lower,
        dong_yao=dong,
        ben_gua_num=ben_gua_num,
        ben_gua_name=ben_gua_name,
        bian_gua_num=bian_gua_num,
        bian_gua_name=bian_gua_name,
        calc_detail={
            'nums': {'year': y, 'month': m, 'day': d, 'hour': h},
            'upper_sum': upper_sum,
            'total_sum': total_sum
        }
    )

def qigua_tiangan(sizhu: SiZhu) -> GuaResult:
    """天干法起卦"""
    y, m, d, h = sizhu.get_gan_nums()
    
    upper_sum = y + m + d
    total_sum = y + m + d + h
    
    upper = num_to_gua(upper_sum)
    lower = num_to_gua(total_sum)
    dong = num_to_yao(total_sum)
    
    ben_gua_num = GUA_64_MAP.get((upper, lower), 0)
    ben_gua_name = GUA_64_NAME.get(ben_gua_num, '?')
    
    bian_upper, bian_lower = get_bian_gua(upper, lower, dong)
    bian_gua_num = GUA_64_MAP.get((bian_upper, bian_lower), 0)
    bian_gua_name = GUA_64_NAME.get(bian_gua_num, '?')
    
    return GuaResult(
        method='天干法',
        upper_gua=upper,
        lower_gua=lower,
        dong_yao=dong,
        ben_gua_num=ben_gua_num,
        ben_gua_name=ben_gua_name,
        bian_gua_num=bian_gua_num,
        bian_gua_name=bian_gua_name,
        calc_detail={
            'nums': {'year': y, 'month': m, 'day': d, 'hour': h},
            'upper_sum': upper_sum,
            'total_sum': total_sum
        }
    )

def qigua_ganzhi(sizhu: SiZhu) -> GuaResult:
    """干支合算法起卦"""
    gan = sizhu.get_gan_nums()
    zhi = sizhu.get_zhi_nums()
    
    combined = [g + z for g, z in zip(gan, zhi)]
    y, m, d, h = combined
    
    upper_sum = y + m + d
    total_sum = y + m + d + h
    
    upper = num_to_gua(upper_sum)
    lower = num_to_gua(total_sum)
    dong = num_to_yao(total_sum)
    
    ben_gua_num = GUA_64_MAP.get((upper, lower), 0)
    ben_gua_name = GUA_64_NAME.get(ben_gua_num, '?')
    
    bian_upper, bian_lower = get_bian_gua(upper, lower, dong)
    bian_gua_num = GUA_64_MAP.get((bian_upper, bian_lower), 0)
    bian_gua_name = GUA_64_NAME.get(bian_gua_num, '?')
    
    return GuaResult(
        method='干支合法',
        upper_gua=upper,
        lower_gua=lower,
        dong_yao=dong,
        ben_gua_num=ben_gua_num,
        ben_gua_name=ben_gua_name,
        bian_gua_num=bian_gua_num,
        bian_gua_name=bian_gua_name,
        calc_detail={
            'nums': {'year': y, 'month': m, 'day': d, 'hour': h},
            'upper_sum': upper_sum,
            'total_sum': total_sum
        }
    )

def qigua_all(sizhu: SiZhu) -> Dict[str, GuaResult]:
    """三種方法起卦"""
    return {
        'dizhi': qigua_dizhi(sizhu),
        'tiangan': qigua_tiangan(sizhu),
        'ganzhi': qigua_ganzhi(sizhu)
    }

# ============================================================
# 輸出格式化
# ============================================================

def format_gua_result(result: GuaResult) -> str:
    """格式化起卦結果"""
    upper_sym = BAGUA_SYMBOL[result.upper_gua]
    lower_sym = BAGUA_SYMBOL[result.lower_gua]
    
    return f"""
【{result.method}】

計算：
  年={result.calc_detail['nums']['year']} 月={result.calc_detail['nums']['month']} 日={result.calc_detail['nums']['day']} 時={result.calc_detail['nums']['hour']}
  上卦：{result.calc_detail['upper_sum']} % 8 = {result.calc_detail['upper_sum'] % 8} → {result.upper_gua}
  下卦：{result.calc_detail['total_sum']} % 8 = {result.calc_detail['total_sum'] % 8} → {result.lower_gua}
  動爻：{result.calc_detail['total_sum']} % 6 = {result.calc_detail['total_sum'] % 6} → {result.dong_yao}爻

本卦：{result.ben_gua_name}（{result.ben_gua_num}）{upper_sym}{lower_sym}
動爻：{result.dong_yao}爻
變卦：{result.bian_gua_name}（{result.bian_gua_num}）
"""

def get_yao_name(gua_num: int, yao_pos: int, yao_list: List[int]) -> str:
    """取得爻名（如九三、六二）"""
    # yao_pos: 1-6
    pos_names = ['初', '二', '三', '四', '五', '上']
    pos_name = pos_names[yao_pos - 1] if yao_pos <= 5 else '上'
    
    # 陽爻用九，陰爻用六
    yy = '九' if yao_list[yao_pos - 1] == 1 else '六'
    
    if yao_pos == 1:
        return f"初{yy}"
    elif yao_pos == 6:
        return f"上{yy}"
    else:
        return f"{yy}{pos_name}"

# ============================================================
# 測試
# ============================================================

if __name__ == "__main__":
    # 北斗八字：癸丑 乙丑 庚子 乙酉
    beidou = SiZhu(
        year_gan='癸', year_zhi='丑',
        month_gan='乙', month_zhi='丑',
        day_gan='庚', day_zhi='子',
        hour_gan='乙', hour_zhi='酉'
    )
    
    print("=" * 60)
    print("【北斗八字起卦測試】")
    print("八字：癸丑 乙丑 庚子 乙酉")
    print("=" * 60)
    
    results = qigua_all(beidou)
    
    for method, result in results.items():
        print(format_gua_result(result))
        print("-" * 40)
