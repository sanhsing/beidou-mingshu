"""
易經解卦系統 yijing_jiegua_v1.py v1.0
=====================================
XTF任務：融-F | 執行星：光蘊
逆向工程自：北斗案例
日期：2026-02-08

功能：
1. 整合起卦引擎
2. 整合卦/爻資料
3. 綜合解卦輸出
4. 場論詮釋
"""

from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
from yijing_qigua_engine import (
    SiZhu, GuaResult, qigua_all, qigua_dizhi, qigua_tiangan, qigua_ganzhi,
    BAGUA_SYMBOL, BAGUA_YAO, GUA_64_NAME
)
from yijing_gua_translation import GUA_64, get_gua_info
from yijing_yao_translation import YAO_384, get_yao_info, YAO_POSITION_GUIDE

# ============================================================
# 補充關鍵卦資料（案例中用到的）
# ============================================================

GUA_EXTRA = {
    20: {  # 觀
        "name": "觀", "symbol": "☴☷", "full_name": "風地觀",
        "keyword": "觀察", 
        "guaci": "觀，盥而不薦，有孚顒若",
        "vernacular": "洗手還沒獻祭，誠心莊重仰望",
        "field": "場在「觀察/被觀察」狀態，影響力擴散",
        "daxiang": "風行地上，觀；先王以省方觀民設教",
        "action": "觀察、示範、影響他人",
        "warning": "觀=看，也=被看"
    },
    27: {  # 頤
        "name": "頤", "symbol": "☶☳", "full_name": "山雷頤",
        "keyword": "頤養",
        "guaci": "頤，貞吉，觀頤，自求口實",
        "vernacular": "正固吉利，觀察如何頤養，自己求取養分",
        "field": "場需要「滋養」——你吃什麼，就會變成什麼",
        "daxiang": "山下有雷，頤；君子以慎言語，節飲食",
        "action": "滋養身心、注意飲食、謹慎言語",
        "warning": "養正則吉——養對東西才有用"
    },
    37: {  # 家人
        "name": "家人", "symbol": "☴☲", "full_name": "風火家人",
        "keyword": "家庭",
        "guaci": "家人，利女貞",
        "vernacular": "女性守正有利",
        "field": "場在「家庭」範圍，內部和諧",
        "daxiang": "風自火出，家人；君子以言有物而行有恆",
        "action": "顧家、言行一致、建立規矩",
        "warning": "家齊而後國治——從小處做起"
    },
    50: {  # 鼎
        "name": "鼎", "symbol": "☲☴", "full_name": "火風鼎",
        "keyword": "革新",
        "guaci": "鼎，元吉，亨",
        "vernacular": "大吉，亨通",
        "field": "場在「轉化」狀態——舊→新，原料→成品",
        "daxiang": "木上有火，鼎；君子以正位凝命",
        "action": "轉化、升級、革新、承擔使命",
        "warning": "鼎=器具，承載責任"
    },
    53: {  # 漸
        "name": "漸", "symbol": "☴☶", "full_name": "風山漸",
        "keyword": "漸進",
        "guaci": "漸，女歸吉，利貞",
        "vernacular": "像女子出嫁一樣，按程序一步步來，正固有利",
        "field": "場在「漸進」狀態，不能跳躍，只能累積",
        "daxiang": "山上有木，漸；君子以居賢德善俗",
        "action": "慢慢來、不急躁、按程序走",
        "warning": "漸=慢，但方向對就好"
    },
    64: {  # 未濟
        "name": "未濟", "symbol": "☲☵", "full_name": "火水未濟",
        "keyword": "未成",
        "guaci": "未濟，亨，小狐汔濟，濡其尾，無攸利",
        "vernacular": "亨通，小狐狸快渡河時尾巴濕了，沒有利",
        "field": "場「未完成」，還差最後一步，要謹慎收尾",
        "daxiang": "火在水上，未濟；君子以慎辨物居方",
        "action": "小心、謹慎、最後關頭不鬆懈",
        "warning": "未濟=未完成，但未完成就是希望"
    }
}

# 補充關鍵爻資料
YAO_EXTRA = {
    # 漸卦九三
    (53, 3): {
        "yao": "九三", 
        "text": "鴻漸于陸，夫征不復，婦孕不育，凶，利禦寇",
        "vernacular": "鴻雁進到陸地，丈夫出征不回來，妻子懷孕生不出來，凶，適合防守",
        "field": "場進入「衝突區」，進攻不利，防守有利",
        "action": "守，不攻；內，不外"
    },
    # 鼎卦九三
    (50, 3): {
        "yao": "九三",
        "text": "鼎耳革，其行塞，雉膏不食，方雨虧悔，終吉",
        "vernacular": "鼎的耳朵變了，行動受阻，野雞肉吃不到，快下雨時減少悔恨，最終吉利",
        "field": "場在轉化過程中遇到阻塞，暫時無法輸出，等時機到就會好",
        "action": "等待時機，暫時受阻是正常的"
    },
    # 復卦上六
    (24, 6): {
        "yao": "上六",
        "text": "迷復，凶，有災眚，用行師，終有大敗",
        "vernacular": "迷失在回復的路上，凶，有災難，出兵會大敗",
        "field": "場如果「迷失方向」，就會陷入長期困境",
        "action": "不要迷失，要清楚知道自己在「復」什麼"
    }
}

# ============================================================
# 資料取得函數
# ============================================================

def get_gua_full(gua_num: int) -> Dict:
    """取得完整卦資料"""
    # 優先從 GUA_64 取
    if gua_num in GUA_64:
        return GUA_64[gua_num]
    # 其次從補充資料取
    if gua_num in GUA_EXTRA:
        return GUA_EXTRA[gua_num]
    # 都沒有就返回基本資訊
    return {
        "name": GUA_64_NAME.get(gua_num, "?"),
        "keyword": "（資料待補）",
        "vernacular": "（資料待補）",
        "field": "（資料待補）"
    }

def get_yao_full(gua_num: int, yao_pos: int) -> Dict:
    """取得完整爻資料"""
    # 優先從 YAO_384 取
    key = (gua_num, yao_pos)
    if key in YAO_384:
        return YAO_384[key]
    # 其次從補充資料取
    if key in YAO_EXTRA:
        return YAO_EXTRA[key]
    # 都沒有就返回基本資訊
    return {
        "yao": f"第{yao_pos}爻",
        "text": "（資料待補）",
        "vernacular": "（資料待補）",
        "field": "（資料待補）",
        "action": "（資料待補）"
    }

def get_yao_name_from_gua(gua_num: int, yao_pos: int) -> str:
    """根據卦和爻位取得爻名（如九三、六二）"""
    gua_info = get_gua_full(gua_num)
    
    # 從符號推斷爻的陰陽
    # 這裡簡化處理，實際需要完整的卦爻結構
    pos_names = {1: '初', 2: '二', 3: '三', 4: '四', 5: '五', 6: '上'}
    
    yao_info = get_yao_full(gua_num, yao_pos)
    if 'yao' in yao_info:
        return yao_info['yao']
    
    return f"第{yao_pos}爻"

# ============================================================
# 解卦輸出
# ============================================================

@dataclass
class JieGuaResult:
    """解卦結果"""
    method: str
    # 計算
    calc_detail: Dict
    # 本卦
    ben_gua_num: int
    ben_gua_name: str
    ben_gua_info: Dict
    # 動爻
    dong_yao: int
    dong_yao_name: str
    dong_yao_info: Dict
    # 變卦
    bian_gua_num: int
    bian_gua_name: str
    bian_gua_info: Dict

def jiegua_single(qigua_result: GuaResult) -> JieGuaResult:
    """單一方法解卦"""
    ben_info = get_gua_full(qigua_result.ben_gua_num)
    bian_info = get_gua_full(qigua_result.bian_gua_num)
    dong_info = get_yao_full(qigua_result.ben_gua_num, qigua_result.dong_yao)
    dong_name = dong_info.get('yao', f"第{qigua_result.dong_yao}爻")
    
    return JieGuaResult(
        method=qigua_result.method,
        calc_detail=qigua_result.calc_detail,
        ben_gua_num=qigua_result.ben_gua_num,
        ben_gua_name=qigua_result.ben_gua_name,
        ben_gua_info=ben_info,
        dong_yao=qigua_result.dong_yao,
        dong_yao_name=dong_name,
        dong_yao_info=dong_info,
        bian_gua_num=qigua_result.bian_gua_num,
        bian_gua_name=qigua_result.bian_gua_name,
        bian_gua_info=bian_info
    )

def format_jiegua(result: JieGuaResult) -> str:
    """格式化解卦輸出"""
    ben = result.ben_gua_info
    dong = result.dong_yao_info
    bian = result.bian_gua_info
    
    output = f"""
{'='*60}
【{result.method}】
{'='*60}

## 計算過程
  年={result.calc_detail['nums']['year']} 月={result.calc_detail['nums']['month']} 日={result.calc_detail['nums']['day']} 時={result.calc_detail['nums']['hour']}
  上卦：{result.calc_detail['upper_sum']} % 8 → {result.ben_gua_info.get('symbol', '')[0] if result.ben_gua_info.get('symbol') else '?'}
  下卦：{result.calc_detail['total_sum']} % 8 → {result.ben_gua_info.get('symbol', '')[1] if len(result.ben_gua_info.get('symbol', '')) > 1 else '?'}
  動爻：{result.calc_detail['total_sum']} % 6 → {result.dong_yao}爻

## 本卦：{result.ben_gua_name}（{result.ben_gua_num}）{ben.get('symbol', '')}

| 項目 | 內容 |
|------|------|
| 關鍵詞 | {ben.get('keyword', '?')} |
| 卦辭 | {ben.get('guaci', ben.get('vernacular', '?'))} |
| 白話 | {ben.get('vernacular', '?')} |
| 場論 | {ben.get('field', '?')} |
| 大象 | {ben.get('daxiang', '?')} |

## 動爻：{result.dong_yao_name}

| 項目 | 內容 |
|------|------|
| 爻辭 | {dong.get('text', '?')} |
| 白話 | {dong.get('vernacular', '?')} |
| 場論 | {dong.get('field', '?')} |
| 行動 | {dong.get('action', '?')} |

## 變卦：{result.bian_gua_name}（{result.bian_gua_num}）{bian.get('symbol', '')}

| 項目 | 內容 |
|------|------|
| 關鍵詞 | {bian.get('keyword', '?')} |
| 白話 | {bian.get('vernacular', '?')} |
| 場論 | {bian.get('field', '?')} |

## 一句話

> **{result.ben_gua_name}（{ben.get('keyword', '?')}）→ {result.dong_yao_name}（{dong.get('action', '?')[:10]}...）→ {result.bian_gua_name}（{bian.get('keyword', '?')}）**
"""
    return output

# ============================================================
# 完整解卦（三法）
# ============================================================

def jiegua_full(sizhu: SiZhu) -> str:
    """完整三法解卦"""
    results = qigua_all(sizhu)
    
    output = f"""
{'#'*60}
# 易經本命卦解讀
# 八字：{sizhu.year_gan}{sizhu.year_zhi} {sizhu.month_gan}{sizhu.month_zhi} {sizhu.day_gan}{sizhu.day_zhi} {sizhu.hour_gan}{sizhu.hour_zhi}
{'#'*60}
"""
    
    for method, qigua_result in results.items():
        jiegua = jiegua_single(qigua_result)
        output += format_jiegua(jiegua)
    
    # 三法綜合
    dizhi = jiegua_single(results['dizhi'])
    tiangan = jiegua_single(results['tiangan'])
    ganzhi = jiegua_single(results['ganzhi'])
    
    output += f"""
{'='*60}
【三法綜合解讀】
{'='*60}

| 方法 | 本卦 | 動爻 | 變卦 | 核心訊息 |
|------|------|------|------|----------|
| 地支法 | {dizhi.ben_gua_name} | {dizhi.dong_yao_name} | {dizhi.bian_gua_name} | {dizhi.ben_gua_info.get('keyword', '?')}→{dizhi.bian_gua_info.get('keyword', '?')} |
| 天干法 | {tiangan.ben_gua_name} | {tiangan.dong_yao_name} | {tiangan.bian_gua_name} | {tiangan.ben_gua_info.get('keyword', '?')}→{tiangan.bian_gua_info.get('keyword', '?')} |
| 干支合法 | {ganzhi.ben_gua_name} | {ganzhi.dong_yao_name} | {ganzhi.bian_gua_name} | {ganzhi.ben_gua_info.get('keyword', '?')}→{ganzhi.bian_gua_info.get('keyword', '?')} |

## 場論統一訊息

> 以「{dizhi.ben_gua_info.get('keyword', '?')}」的方式（{dizhi.ben_gua_name}），
> 做「{tiangan.ben_gua_info.get('keyword', '?')}」的工作（{tiangan.ben_gua_name}），
> 走「{ganzhi.ben_gua_info.get('keyword', '?')}」的路（{ganzhi.ben_gua_name}），
> 最終成為「{dizhi.bian_gua_info.get('keyword', '?')}」（{dizhi.bian_gua_name}）、
> 保持「{tiangan.bian_gua_info.get('keyword', '?')}」（{tiangan.bian_gua_name}）、
> 行「{ganzhi.bian_gua_info.get('keyword', '?')}」之道（{ganzhi.bian_gua_name}）。
"""
    
    return output

# ============================================================
# API 介面
# ============================================================

def jiegua_from_bazi(year_gan: str, year_zhi: str,
                     month_gan: str, month_zhi: str,
                     day_gan: str, day_zhi: str,
                     hour_gan: str, hour_zhi: str) -> str:
    """從八字解卦（API介面）"""
    sizhu = SiZhu(
        year_gan=year_gan, year_zhi=year_zhi,
        month_gan=month_gan, month_zhi=month_zhi,
        day_gan=day_gan, day_zhi=day_zhi,
        hour_gan=hour_gan, hour_zhi=hour_zhi
    )
    return jiegua_full(sizhu)

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
    
    print(jiegua_full(beidou))
