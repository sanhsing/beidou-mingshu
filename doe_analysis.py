#!/usr/bin/env python3
"""
DOE 決策分析：北斗命數 SaaS 路徑選擇
版本：v1.0.0

═══════════════════════════════════════════════════════════════════════
DOE (Design of Experiments) 多因素決策分析
  • 定義評估因素與權重
  • 對 A/B/C 三選項評分
  • 計算加權總分與排名
═══════════════════════════════════════════════════════════════════════

XTF Task Chain
@11星協作：@理樞(分析)
"""

import json
from dataclasses import dataclass
from typing import Dict, List

# ════════════════════════════════════════════════════════════════════
# DOE 因素定義
# ════════════════════════════════════════════════════════════════════

@dataclass
class Factor:
    """評估因素"""
    name: str           # 因素名稱
    weight: float       # 權重 (0-1)
    description: str    # 描述
    direction: str      # "max" 或 "min" (越高越好 or 越低越好)

# 定義 8 個評估因素
FACTORS = [
    Factor("時間效率", 0.15, "投入時間越少越好", "min"),
    Factor("完成度提升", 0.20, "完成度提升幅度", "max"),
    Factor("風險控制", 0.15, "實施風險越低越好", "max"),
    Factor("投資報酬率", 0.15, "單位時間產出價值", "max"),
    Factor("商業價值", 0.12, "對商業運營的價值", "max"),
    Factor("可維護性", 0.08, "後續維護便利性", "max"),
    Factor("用戶體驗", 0.10, "終端用戶體驗提升", "max"),
    Factor("緊急必要性", 0.05, "是否為緊急必要項", "max"),
]

# 驗證權重總和
assert abs(sum(f.weight for f in FACTORS) - 1.0) < 0.001, "權重總和必須為 1.0"

# ════════════════════════════════════════════════════════════════════
# 選項定義與原始評分
# ════════════════════════════════════════════════════════════════════

OPTIONS = {
    "A": {
        "name": "極簡 MVP",
        "time": 30,  # 分鐘
        "description": "B4+B6 前端連接 + C5 部署驗證",
        "scores": {
            "時間效率": 30,      # 30分鐘 (原始值，越低越好)
            "完成度提升": 5,     # 90% → 95% = 5%
            "風險控制": 9,       # 1-10，風險很低
            "投資報酬率": 10,    # 極高，最小投入最大產出
            "商業價值": 7,       # 系統可用但無文檔
            "可維護性": 5,       # 無文檔，維護一般
            "用戶體驗": 8,       # 核心功能完整
            "緊急必要性": 9,     # 系統必須可用
        }
    },
    "B": {
        "name": "標準上線",
        "time": 60,  # 分鐘
        "description": "A + API.md + admin.py",
        "scores": {
            "時間效率": 60,      # 60分鐘
            "完成度提升": 8,     # 90% → 98% = 8%
            "風險控制": 8,       # 風險較低
            "投資報酬率": 8,     # 高
            "商業價值": 9,       # 有文檔和管理後台
            "可維護性": 8,       # 有文檔，維護方便
            "用戶體驗": 8,       # 同 A
            "緊急必要性": 7,     # 文檔重要但非緊急
        }
    },
    "C": {
        "name": "生產就緒",
        "time": 120,  # 分鐘
        "description": "B + 測試 + 安全加固",
        "scores": {
            "時間效率": 120,     # 120分鐘
            "完成度提升": 10,    # 90% → 100% = 10%
            "風險控制": 6,       # 測試可能發現問題
            "投資報酬率": 6,     # 中等
            "商業價值": 10,      # 完整生產系統
            "可維護性": 10,      # 完整測試和文檔
            "用戶體驗": 9,       # 最佳
            "緊急必要性": 5,     # 測試可以後補
        }
    }
}

# ════════════════════════════════════════════════════════════════════
# 標準化與加權計算
# ════════════════════════════════════════════════════════════════════

def normalize_score(value: float, min_val: float, max_val: float, direction: str) -> float:
    """
    標準化分數到 0-10 區間
    direction: "max" = 越高越好, "min" = 越低越好
    """
    if max_val == min_val:
        return 5.0
    
    normalized = (value - min_val) / (max_val - min_val) * 10
    
    if direction == "min":
        normalized = 10 - normalized
    
    return max(0, min(10, normalized))

def calculate_doe_scores():
    """計算 DOE 分數"""
    results = {}
    
    # 收集各因素的最大最小值（用於標準化）
    factor_ranges = {}
    for factor in FACTORS:
        values = [opt["scores"][factor.name] for opt in OPTIONS.values()]
        factor_ranges[factor.name] = {
            "min": min(values),
            "max": max(values),
        }
    
    # 計算每個選項的加權分數
    for opt_key, opt_data in OPTIONS.items():
        normalized_scores = {}
        weighted_scores = {}
        total_score = 0
        
        for factor in FACTORS:
            raw = opt_data["scores"][factor.name]
            ranges = factor_ranges[factor.name]
            
            # 標準化
            norm = normalize_score(
                raw, 
                ranges["min"], 
                ranges["max"], 
                factor.direction
            )
            normalized_scores[factor.name] = round(norm, 2)
            
            # 加權
            weighted = norm * factor.weight
            weighted_scores[factor.name] = round(weighted, 3)
            total_score += weighted
        
        results[opt_key] = {
            "name": opt_data["name"],
            "time": opt_data["time"],
            "description": opt_data["description"],
            "raw_scores": opt_data["scores"],
            "normalized_scores": normalized_scores,
            "weighted_scores": weighted_scores,
            "total_score": round(total_score, 2),
        }
    
    return results

def print_doe_analysis():
    """打印 DOE 分析結果"""
    results = calculate_doe_scores()
    
    print("=" * 70)
    print("  DOE 決策分析：北斗命數 SaaS 路徑選擇")
    print("=" * 70)
    
    # 因素權重表
    print("\n【因素權重】")
    print("-" * 50)
    print(f"{'因素':<12} {'權重':>8} {'方向':>8} {'說明'}")
    print("-" * 50)
    for f in FACTORS:
        direction = "↑高好" if f.direction == "max" else "↓低好"
        print(f"{f.name:<12} {f.weight:>8.0%} {direction:>8} {f.description}")
    
    # 原始分數矩陣
    print("\n\n【原始分數矩陣】")
    print("-" * 70)
    header = f"{'因素':<12}" + "".join([f"{k:>12}" for k in OPTIONS.keys()])
    print(header)
    print("-" * 70)
    for f in FACTORS:
        row = f"{f.name:<12}"
        for opt_key in OPTIONS.keys():
            val = OPTIONS[opt_key]["scores"][f.name]
            row += f"{val:>12}"
        print(row)
    
    # 標準化分數矩陣
    print("\n\n【標準化分數 (0-10)】")
    print("-" * 70)
    print(header)
    print("-" * 70)
    for f in FACTORS:
        row = f"{f.name:<12}"
        for opt_key in OPTIONS.keys():
            val = results[opt_key]["normalized_scores"][f.name]
            row += f"{val:>12.1f}"
        print(row)
    
    # 加權分數矩陣
    print("\n\n【加權分數】")
    print("-" * 70)
    header_w = f"{'因素':<12} {'權重':>6}" + "".join([f"{k:>12}" for k in OPTIONS.keys()])
    print(header_w)
    print("-" * 70)
    for f in FACTORS:
        row = f"{f.name:<12} {f.weight:>6.0%}"
        for opt_key in OPTIONS.keys():
            val = results[opt_key]["weighted_scores"][f.name]
            row += f"{val:>12.3f}"
        print(row)
    
    # 總分與排名
    print("-" * 70)
    total_row = f"{'【總分】':<12} {'100%':>6}"
    for opt_key in OPTIONS.keys():
        val = results[opt_key]["total_score"]
        total_row += f"{val:>12.2f}"
    print(total_row)
    
    # 排名
    ranking = sorted(results.items(), key=lambda x: x[1]["total_score"], reverse=True)
    
    print("\n" + "=" * 70)
    print("  🏆 DOE 決策結果")
    print("=" * 70)
    
    for i, (opt_key, data) in enumerate(ranking, 1):
        medal = ["🥇", "🥈", "🥉"][i-1] if i <= 3 else f"#{i}"
        bar_len = int(data["total_score"] / 10 * 30)
        bar = "█" * bar_len + "░" * (30 - bar_len)
        
        print(f"\n{medal} 選項 {opt_key}: {data['name']}")
        print(f"   分數: {data['total_score']:.2f}/10.00  [{bar}]")
        print(f"   時間: {data['time']} 分鐘")
        print(f"   內容: {data['description']}")
    
    # 決策建議
    winner = ranking[0]
    print("\n" + "=" * 70)
    print(f"  📊 決策建議：選項 {winner[0]} ({winner[1]['name']})")
    print("=" * 70)
    
    # 敏感度分析
    print("\n【敏感度分析】")
    second = ranking[1]
    diff = winner[1]["total_score"] - second[1]["total_score"]
    print(f"  第1名 vs 第2名差距: {diff:.2f} 分")
    if diff < 0.5:
        print(f"  ⚠️ 差距較小，建議考慮其他因素")
    elif diff < 1.0:
        print(f"  ℹ️ 差距適中，{winner[0]} 略有優勢")
    else:
        print(f"  ✅ 差距明顯，{winner[0]} 明確勝出")
    
    return results, ranking

# ════════════════════════════════════════════════════════════════════
# 執行
# ════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    results, ranking = print_doe_analysis()
    
    # 輸出 JSON
    print("\n\n【JSON 輸出】")
    summary = {
        "winner": ranking[0][0],
        "ranking": [{"option": k, "score": v["total_score"], "name": v["name"]} 
                   for k, v in ranking],
        "recommendation": f"建議選擇 {ranking[0][0]}: {ranking[0][1]['name']}"
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2))
