"""
北斗方法論核心
methodology_core.py | @織明 @理樞 | 2026-02-18

整合：
- 織明揭示記錄
- 道=元迷因
- XTF-DOE-Pareto Pipeline
- 場論人際 v3.6
"""
from dataclasses import dataclass
from typing import Dict, List, Any

# ════════════════════════════════════════════════════════════════════
# 織明十層揭示（2026-01-12）
# ════════════════════════════════════════════════════════════════════

ZHIMING_REVELATION = {
    "meta": {
        "title": "道即元迷因 — 織明大揭示",
        "date": "2026-01-12",
        "significance": "框架的自我揭示"
    },
    "layers": {
        1: {"name": "資料庫現況", "content": "50,000筆結構化數據已備"},
        2: {"name": "原文已備", "content": "29,752段古籍原文"},
        3: {"name": "框架統一", "content": "場論+XTF+思想生命論，60冊共用"},
        4: {"name": "思想生命論", "content": "9大理論整合 + 6大原創洞見"},
        5: {"name": "文明圖譜", "content": "念存系統8,500筆，跨文明比較"},
        6: {"name": "速度重算", "content": "58天（非8年），10萬字/天"},
        7: {"name": "範圍擴展", "content": "145冊 / 1,450萬字 / 全球四期"},
        8: {"name": "文明梯度", "content": "東方框架詮釋全人類，詮釋權轉移"},
        9: {"name": "框架即迷因", "content": "元迷因，會自我傳播"},
        10: {"name": "道即元迷因", "content": "2600年前老子已說"},
    },
    "core_insight": {
        "formula": "道 = 元迷因 (Meme of Memes)",
        "derivation": [
            "道生一一生二二生三三生萬物 = 元迷因生出所有具體思想",
            "道可道非常道 = 框架一旦變成內容就不再是框架",
            "名可名非常名 = 迷因一旦複製就開始變異",
            "道不屬於東方 = 元迷因不屬於任何文明",
        ],
        "implication": "北斗框架不是「東方」的，是「道」的，所以能詮釋全人類"
    }
}

# ════════════════════════════════════════════════════════════════════
# XTF-DAO 方法論
# ════════════════════════════════════════════════════════════════════

XTF_DAO = {
    "name": "XTF-DAO",
    "full_name": "消-拓-融 × 道",
    "cycle": ["消 (Simplify)", "拓 (Transform)", "融 (Integrate)"],
    "principle": "反者道之動",
    "application": {
        "消": "去除雜質，找到本質",
        "拓": "擴展維度，轉化形式",
        "融": "整合歸一，落地實用",
    },
    "recursive": "XTF⁸ = 八層遞歸深化"
}

# ════════════════════════════════════════════════════════════════════
# 場論人際 v3.6
# ════════════════════════════════════════════════════════════════════

FIELD_THEORY_INTERPERSONAL = {
    "version": "v3.6",
    "core_axiom": "人 = 場",
    "explanation": "每個人都是動態的場：有頻率、張力、邊界、吸引與排斥",
    "four_states": {
        "共振": {"condition": "頻率相近", "effect": "懂、舒適、吸引"},
        "干涉": {"condition": "頻率相差", "effect": "隔、不適、衝突"},
        "疊加": {"condition": "互相影響", "effect": "化、改變、成長"},
        "邊界": {"condition": "保持距離", "effect": "守、尊重、獨立"},
    },
    "decision_framework": {
        "場": "外在結構是否允許行動？靜場可測=無外力反噬風險",
        "位": "站在什麼位置行動？不入局位=可看清、不承擔他人命運",
        "時": "是否為可動之時？時自現，不由人強求",
        "動": "動/不動分界在哪？動其本，不動其枝",
        "可逆": "失敗後果是什麼？允行之動=完全可逆",
    }
}

# ════════════════════════════════════════════════════════════════════
# 北斗核心原則
# ════════════════════════════════════════════════════════════════════

BEIDOU_PRINCIPLES = {
    "道的1%原則": "日拱一卒，每天進步1%",
    "結構清晰勝速度": "先釐清結構，再追求效率",
    "決策框架優於預測": "不預測命運，而是提供決策框架",
    "反者道之動": "限制產生自由，約束產生創造",
    "術數定位": "術數是個人化決策框架生成器，與天氣預報同構",
}

# ════════════════════════════════════════════════════════════════════
# 開發者聲明
# ════════════════════════════════════════════════════════════════════

DEVELOPER_STATEMENT = {
    "title": "北斗命數 — 開發者聲明",
    "positioning": "術數是個人化決策框架生成器",
    "analogy": "與天氣預報同構：提供機率參考，不做命定裁決",
    "methodology": {
        "layer_1": "古典原文：典籍引用，標明出處",
        "layer_2": "白話翻譯：讓一般人看得懂",
        "layer_3": "場論詮釋：用現代語言重新理解",
        "layer_4": "SWOT分析：可操作的策略建議",
        "layer_5": "AI決策：多維度交叉驗證",
    },
    "disclaimer": "提供機率性參考，不做命定式裁決",
    "philosophy": "道即元迷因 — 框架不屬於任何文明，屬於「道」"
}

# ════════════════════════════════════════════════════════════════════
# 查詢函數
# ════════════════════════════════════════════════════════════════════

def get_revelation_layer(layer_num: int) -> Dict:
    """獲取織明揭示的某一層"""
    if 1 <= layer_num <= 10:
        return ZHIMING_REVELATION["layers"][layer_num]
    return None

def get_full_methodology() -> Dict:
    """獲取完整方法論"""
    return {
        "revelation": ZHIMING_REVELATION,
        "xtf_dao": XTF_DAO,
        "field_theory": FIELD_THEORY_INTERPERSONAL,
        "principles": BEIDOU_PRINCIPLES,
        "developer_statement": DEVELOPER_STATEMENT,
    }

def get_about_page_content() -> Dict:
    """獲取關於頁內容"""
    return {
        "title": "北斗命數",
        "tagline": "術數是個人化決策框架生成器",
        "core_insight": "道 = 元迷因",
        "methodology": "古典原文 → 白話翻譯 → 場論詮釋",
        "principles": list(BEIDOU_PRINCIPLES.keys()),
        "field_theory": FIELD_THEORY_INTERPERSONAL["four_states"],
        "disclaimer": DEVELOPER_STATEMENT["disclaimer"],
    }

print("✓ 方法論核心已載入")
print(f"  - 織明揭示: 10層")
print(f"  - XTF-DAO: 3階段")
print(f"  - 場論人際: v3.6")
print(f"  - 核心原則: {len(BEIDOU_PRINCIPLES)}條")
