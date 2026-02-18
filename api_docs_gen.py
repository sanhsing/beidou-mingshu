"""API 文檔自動生成 | @理樞"""

API_DOCS = {
    "info": {
        "title": "北斗命數 API",
        "version": "1.0.0",
        "description": "八字命理分析服務 API"
    },
    "endpoints": [
        {"path": "/api/health", "method": "GET", "desc": "健康檢查"},
        {"path": "/api/auth/register", "method": "POST", "desc": "用戶註冊"},
        {"path": "/api/auth/login", "method": "POST", "desc": "用戶登入"},
        {"path": "/api/bazi/analyze", "method": "POST", "desc": "八字分析"},
        {"path": "/api/bazi/free", "method": "POST", "desc": "免費試算"},
        {"path": "/api/user/profile", "method": "GET/PUT", "desc": "個人資料"},
        {"path": "/api/user/credits", "method": "GET", "desc": "點數查詢"},
        {"path": "/api/user/orders", "method": "GET", "desc": "訂單列表"},
        {"path": "/api/payment/notify", "method": "POST", "desc": "支付回調"},
        {"path": "/api/coupon/verify", "method": "POST", "desc": "優惠券驗證"},
        {"path": "/api/invoice/list", "method": "GET", "desc": "發票列表"},
        {"path": "/api/admin/stats/*", "method": "GET", "desc": "管理統計"},
    ]
}

def generate_markdown():
    """生成 Markdown 文檔"""
    md = f"# {API_DOCS['info']['title']}\n\n"
    md += f"> {API_DOCS['info']['description']}\n\n"
    md += f"版本: {API_DOCS['info']['version']}\n\n"
    md += "## 端點列表\n\n"
    md += "| 路徑 | 方法 | 說明 |\n|------|------|------|\n"
    for ep in API_DOCS['endpoints']:
        md += f"| `{ep['path']}` | {ep['method']} | {ep['desc']} |\n"
    return md

if __name__ == "__main__":
    print(generate_markdown())
