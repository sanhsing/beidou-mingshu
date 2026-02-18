"""
反詐騙模組
anti_fraud.py | @星殼 | 2026-02-18

功能：
- 禁用詞過濾（AI 輸出審核）
- 價格上限驗證
- 反詐提示生成
"""
import re
from typing import Tuple, List

# === 禁用詞列表 ===
FORBIDDEN_PHRASES = [
    # 恐嚇話術
    "家破人亡", "必死", "死劫", "血光之災", "橫禍",
    "煞星纏身", "命帶煞", "大凶", "絕命", "夭折",
    "冤親債主", "業障深重", "前世孽緣",
    
    # 斂財話術
    "消災", "化解", "做法事", "點燈", "安太歲",
    "靈符", "加持", "功德金", "供養", "還債",
    "急需處理", "越快越好", "再不處理",
]

# === 價格上限 ===
PRICE_LIMITS = {
    "single_report": 500,      # 單份報告上限 NT$500
    "subscription_monthly": 999,  # 月訂閱上限
    "subscription_yearly": 4990,  # 年訂閱上限
}

# === 反詐提示 ===
ANTI_FRAUD_NOTICE = """
⚠️ 反詐騙提示

正規命理服務不會：
• 以恐嚇話術（如「煞星」「災劫」）要求您付費
• 持續要求您加碼付款
• 要求轉帳至個人帳戶

若遇可疑情況，請撥打 165 反詐騙專線。
"""

def filter_forbidden_content(text: str) -> Tuple[str, List[str]]:
    """
    過濾禁用詞
    
    Returns:
        (filtered_text, found_phrases)
    """
    found = []
    filtered = text
    
    for phrase in FORBIDDEN_PHRASES:
        if phrase in text:
            found.append(phrase)
            # 替換為安全用語
            filtered = filtered.replace(phrase, "【此處已過濾】")
    
    return filtered, found


def check_price_limit(price: float, price_type: str = "single_report") -> Tuple[bool, str]:
    """
    檢查價格是否超過上限
    
    Returns:
        (is_valid, message)
    """
    limit = PRICE_LIMITS.get(price_type, 500)
    
    if price > limit:
        return False, f"價格 {price} 超過上限 {limit}"
    
    return True, "OK"


def get_anti_fraud_footer() -> str:
    """獲取反詐提示（用於報告底部）"""
    return """
---
📞 反詐騙提示：若有人以本報告內容要求您支付額外費用，請撥打 165 反詐騙專線。
本服務為娛樂參考性質，不提供任何「消災」「化解」服務。
"""


def validate_ai_output(text: str) -> Tuple[str, bool, List[str]]:
    """
    驗證 AI 輸出內容
    
    Returns:
        (safe_text, has_issues, issues)
    """
    safe_text, found_phrases = filter_forbidden_content(text)
    
    has_issues = len(found_phrases) > 0
    
    return safe_text, has_issues, found_phrases


# === 測試 ===
if __name__ == "__main__":
    test_text = "您命帶煞星，需要消災化解，否則家破人亡"
    
    safe, has_issues, issues = validate_ai_output(test_text)
    
    print(f"原文：{test_text}")
    print(f"過濾後：{safe}")
    print(f"問題詞：{issues}")
    print(f"有問題：{has_issues}")


print("✓ 反詐騙模組已載入")
