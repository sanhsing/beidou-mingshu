"""
易經解卦系統 yijing_jiegua_v2.py v2.0
=====================================
引用 yijing_config.py 資料
引用 yijing_qigua_engine_v2.py 計算
"""

from typing import Dict, Optional
from yijing_qigua_engine_v2 import (
    QiGuaResult, qigua_dizhi, qigua_tiangan, qigua_ganzhi,
    GUA_TO_NUM, BAGUA_SYMBOL, GUA_64_REVERSE, gua_to_6bit,
    get_cuo_gua, get_zong_gua, GUA_64_MAP, GUA_64_NAME
)
from yijing_config import GUA_DATA, YAO_DATA, YAO_POSITION, FIELD_THEORY

# ============================================================
# 資料取得
# ============================================================

def get_gua(gua_num: int) -> Dict:
    """取得卦資料"""
    if gua_num in GUA_DATA:
        return GUA_DATA[gua_num]
    return {
        "name": GUA_64_NAME.get(gua_num, "?"),
        "keyword": "（資料待補）",
        "baihua": "（資料待補）",
        "field": "（資料待補）"
    }

def get_yao(gua_num: int, yao_pos: int) -> Dict:
    """取得爻資料"""
    key = (gua_num, yao_pos)
    if key in YAO_DATA:
        return YAO_DATA[key]
    
    # 無特定爻資料，返回通則
    pos_info = YAO_POSITION.get(yao_pos, {})
    return {
        "yao": f"第{yao_pos}爻",
        "yaoci": "（資料待補）",
        "baihua": "（資料待補）",
        "field": f"爻位{pos_info.get('name', '')}：{pos_info.get('tendency', '')}",
        "action": pos_info.get('meaning', '（待補）')
    }

# ============================================================
# 完整解卦
# ============================================================

def jiegua(r: QiGuaResult) -> str:
    """完整解卦輸出"""
    
    # 取得資料
    ben = get_gua(r.ben_gua_num)
    bian = get_gua(r.bian_gua_num)
    yao = get_yao(r.ben_gua_num, r.dong_yao)
    pos = YAO_POSITION.get(r.dong_yao, {})
    
    # 符號
    u_sym = BAGUA_SYMBOL[GUA_TO_NUM[r.upper]]
    l_sym = BAGUA_SYMBOL[GUA_TO_NUM[r.lower]]
    bu_sym = BAGUA_SYMBOL[GUA_TO_NUM[r.bian_upper]]
    bl_sym = BAGUA_SYMBOL[GUA_TO_NUM[r.bian_lower]]
    
    return f"""
{'='*60}
【{r.method}】
{'='*60}

## 計算
年={r.calc['y']} 月={r.calc['m']} 日={r.calc['d']} 時={r.calc['h']}
上卦：{r.calc['upper_sum']} % 8 → {r.upper} {u_sym}
下卦：{r.calc['total_sum']} % 8 → {r.lower} {l_sym}
動爻：{r.calc['total_sum']} % 6 → {r.dong_yao}爻
6-bit：{r.ben_bit6:06b} XOR {(1<<(r.dong_yao-1)):06b} = {r.bian_bit6:06b}

## 本卦：{ben.get('name', '?')}（{r.ben_gua_num}）{u_sym}{l_sym}

| 項目 | 內容 |
|------|------|
| 全名 | {ben.get('full_name', '?')} |
| 卦辭 | {ben.get('guaci', '?')} |
| 白話 | {ben.get('baihua', '?')} |
| 場論 | {ben.get('field', '?')} |
| 大象 | {ben.get('daxiang', '?')} |
| 關鍵詞 | {ben.get('keyword', '?')} |
| 行動 | {ben.get('action', '?')} |
| 警示 | {ben.get('warning', '?')} |

## 動爻：{yao.get('yao', '?')}

| 項目 | 內容 |
|------|------|
| 爻辭 | {yao.get('yaoci', '?')} |
| 白話 | {yao.get('baihua', '?')} |
| 場論 | {yao.get('field', '?')} |
| 行動 | {yao.get('action', '?')} |
| 爻位 | {pos.get('name', '')}爻 — {pos.get('meaning', '')}，{pos.get('tendency', '')} |

## 變卦：{bian.get('name', '?')}（{r.bian_gua_num}）{bu_sym}{bl_sym}

| 項目 | 內容 |
|------|------|
| 全名 | {bian.get('full_name', '?')} |
| 白話 | {bian.get('baihua', '?')} |
| 場論 | {bian.get('field', '?')} |
| 關鍵詞 | {bian.get('keyword', '?')} |
| 行動 | {bian.get('action', '?')} |

## 一句話

> **{ben.get('name')}（{ben.get('keyword', '?')}）→ {yao.get('yao')}（{yao.get('action', '')[:15]}）→ {bian.get('name')}（{bian.get('keyword', '?')}）**
"""

def jiegua_full(y_gan: str, y_zhi: str, m_gan: str, m_zhi: str,
                d_gan: str, d_zhi: str, h_gan: str, h_zhi: str) -> str:
    """完整三法解卦"""
    
    r1 = qigua_dizhi(y_zhi, m_zhi, d_zhi, h_zhi)
    r2 = qigua_tiangan(y_gan, m_gan, d_gan, h_gan)
    r3 = qigua_ganzhi(y_gan, y_zhi, m_gan, m_zhi, d_gan, d_zhi, h_gan, h_zhi)
    
    output = f"""
{'#'*60}
# 易經本命卦解讀
# 八字：{y_gan}{y_zhi} {m_gan}{m_zhi} {d_gan}{d_zhi} {h_gan}{h_zhi}
{'#'*60}
"""
    
    output += jiegua(r1)
    output += jiegua(r2)
    output += jiegua(r3)
    
    # 三法綜合
    b1 = get_gua(r1.ben_gua_num)
    b2 = get_gua(r2.ben_gua_num)
    b3 = get_gua(r3.ben_gua_num)
    v1 = get_gua(r1.bian_gua_num)
    v2 = get_gua(r2.bian_gua_num)
    v3 = get_gua(r3.bian_gua_num)
    y1 = get_yao(r1.ben_gua_num, r1.dong_yao)
    y2 = get_yao(r2.ben_gua_num, r2.dong_yao)
    y3 = get_yao(r3.ben_gua_num, r3.dong_yao)
    
    output += f"""
{'='*60}
【三法綜合】
{'='*60}

| 方法 | 本卦 | 動爻 | 變卦 | 核心 |
|------|------|------|------|------|
| 地支法 | {b1.get('name')} | {y1.get('yao')} | {v1.get('name')} | {b1.get('keyword')}→{v1.get('keyword')} |
| 天干法 | {b2.get('name')} | {y2.get('yao')} | {v2.get('name')} | {b2.get('keyword')}→{v2.get('keyword')} |
| 干支合法 | {b3.get('name')} | {y3.get('yao')} | {v3.get('name')} | {b3.get('keyword')}→{v3.get('keyword')} |

## 場論統一訊息

> 以「{b1.get('keyword')}」的方式（{b1.get('name')}），
> 做「{b2.get('keyword')}」的工作（{b2.get('name')}），
> 走「{b3.get('keyword')}」的路（{b3.get('name')}），
> 最終成為「{v1.get('keyword')}」（{v1.get('name')}）、
> 保持「{v2.get('keyword')}」（{v2.get('name')}）、
> 行「{v3.get('keyword')}」之道（{v3.get('name')}）。

## 場論核心

> {FIELD_THEORY['core']}
"""
    
    return output

# ============================================================
# 測試
# ============================================================

if __name__ == "__main__":
    # 北斗八字
    print(jiegua_full('癸', '丑', '乙', '丑', '庚', '子', '乙', '酉'))
