#!/usr/bin/env python3
"""
admin.py - 北斗命數管理後台
版本：v1.0.0

═══════════════════════════════════════════════════════════════════════
功能：
  • 用戶管理（查看/停用/調整點數）
  • 訂單管理（查看/退款）
  • 統計報表
  • 系統配置
═══════════════════════════════════════════════════════════════════════

XTF Task Chain: D3
@11星協作：@織明(統籌)
"""

import os
from datetime import datetime, timedelta
from typing import Optional

from fastapi import FastAPI, HTTPException, Depends, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.security import HTTPBasic, HTTPBasicCredentials
import secrets

from config import settings
from db_unified import UnifiedDB

# ════════════════════════════════════════════════════════════════════
# 應用配置
# ════════════════════════════════════════════════════════════════════

app = FastAPI(title="北斗命數管理後台", version="1.0.0")
security = HTTPBasic()
db = UnifiedDB()

# 管理員憑證
ADMIN_USERNAME = os.environ.get("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "beidou_admin_2026")

# ════════════════════════════════════════════════════════════════════
# 認證
# ════════════════════════════════════════════════════════════════════

def verify_admin(credentials: HTTPBasicCredentials = Depends(security)):
    """驗證管理員"""
    correct_username = secrets.compare_digest(credentials.username, ADMIN_USERNAME)
    correct_password = secrets.compare_digest(credentials.password, ADMIN_PASSWORD)
    if not (correct_username and correct_password):
        raise HTTPException(
            status_code=401,
            detail="認證失敗",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username

# ════════════════════════════════════════════════════════════════════
# 樣式
# ════════════════════════════════════════════════════════════════════

ADMIN_STYLES = """
:root {
    --primary: #1a365d;
    --secondary: #2c5282;
    --success: #38a169;
    --warning: #dd6b20;
    --danger: #e53e3e;
    --bg: #f7fafc;
    --card: #ffffff;
}
* { box-sizing: border-box; margin: 0; padding: 0; }
body { font-family: -apple-system, sans-serif; background: var(--bg); }
.navbar { background: var(--primary); color: white; padding: 16px 24px; display: flex; justify-content: space-between; align-items: center; }
.navbar h1 { font-size: 1.4rem; }
.navbar a { color: white; text-decoration: none; margin-left: 20px; opacity: 0.8; }
.navbar a:hover { opacity: 1; }
.container { max-width: 1200px; margin: 0 auto; padding: 24px; }
.card { background: var(--card); border-radius: 12px; padding: 24px; box-shadow: 0 2px 8px rgba(0,0,0,0.06); margin-bottom: 20px; }
.card h2 { color: var(--primary); margin-bottom: 16px; font-size: 1.2rem; }
.stats-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 16px; }
.stat-card { background: var(--card); border-radius: 8px; padding: 20px; text-align: center; box-shadow: 0 2px 4px rgba(0,0,0,0.04); }
.stat-value { font-size: 2rem; font-weight: bold; color: var(--primary); }
.stat-label { color: #718096; margin-top: 4px; }
.table { width: 100%; border-collapse: collapse; }
.table th, .table td { padding: 12px; text-align: left; border-bottom: 1px solid #e2e8f0; }
.table th { background: #f7fafc; font-weight: 600; color: #4a5568; }
.table tr:hover { background: #f7fafc; }
.btn { display: inline-block; padding: 8px 16px; border: none; border-radius: 6px; cursor: pointer; font-size: 0.9rem; text-decoration: none; }
.btn-primary { background: var(--primary); color: white; }
.btn-success { background: var(--success); color: white; }
.btn-warning { background: var(--warning); color: white; }
.btn-danger { background: var(--danger); color: white; }
.btn-sm { padding: 4px 10px; font-size: 0.8rem; }
.badge { display: inline-block; padding: 4px 8px; border-radius: 4px; font-size: 0.75rem; }
.badge-success { background: #c6f6d5; color: #22543d; }
.badge-warning { background: #feebc8; color: #744210; }
.badge-danger { background: #fed7d7; color: #822727; }
.form-group { margin-bottom: 16px; }
.form-group label { display: block; margin-bottom: 6px; font-weight: 500; }
.form-control { width: 100%; padding: 10px; border: 1px solid #e2e8f0; border-radius: 6px; }
.alert { padding: 12px 16px; border-radius: 6px; margin-bottom: 16px; }
.alert-success { background: #c6f6d5; color: #22543d; }
.alert-danger { background: #fed7d7; color: #822727; }
"""

# ════════════════════════════════════════════════════════════════════
# 頁面渲染
# ════════════════════════════════════════════════════════════════════

def render_admin_page(title: str, content: str, active: str = ""):
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>{title} | 管理後台</title>
        <style>{ADMIN_STYLES}</style>
    </head>
    <body>
        <nav class="navbar">
            <h1>🛠️ 北斗命數管理後台</h1>
            <div>
                <a href="/admin/" style="{'opacity:1;font-weight:bold' if active=='home' else ''}">首頁</a>
                <a href="/admin/users" style="{'opacity:1;font-weight:bold' if active=='users' else ''}">用戶</a>
                <a href="/admin/orders" style="{'opacity:1;font-weight:bold' if active=='orders' else ''}">訂單</a>
                <a href="/admin/reports" style="{'opacity:1;font-weight:bold' if active=='reports' else ''}">報告</a>
                <a href="/" target="_blank">前台</a>
            </div>
        </nav>
        <div class="container">
            {content}
        </div>
    </body>
    </html>
    """

# ════════════════════════════════════════════════════════════════════
# 路由
# ════════════════════════════════════════════════════════════════════

@app.get("/admin/", response_class=HTMLResponse)
async def admin_home(admin: str = Depends(verify_admin)):
    """管理首頁"""
    stats = db.get_stats()
    
    # 計算今日數據
    today = datetime.now().strftime("%Y-%m-%d")
    
    content = f"""
    <h2 style="margin-bottom:24px;">📊 系統概覽</h2>
    
    <div class="stats-grid">
        <div class="stat-card">
            <div class="stat-value">{stats.get('users', 0)}</div>
            <div class="stat-label">總用戶數</div>
        </div>
        <div class="stat-card">
            <div class="stat-value">{stats.get('active_users_7d', 0)}</div>
            <div class="stat-label">7日活躍</div>
        </div>
        <div class="stat-card">
            <div class="stat-value">{stats.get('reports', 0)}</div>
            <div class="stat-label">報告生成</div>
        </div>
        <div class="stat-card">
            <div class="stat-value">NT${stats.get('total_revenue', 0):,}</div>
            <div class="stat-label">總收入</div>
        </div>
    </div>
    
    <div class="card" style="margin-top:24px;">
        <h2>📈 命理分析統計</h2>
        <div class="stats-grid" style="margin-top:16px;">
            <div class="stat-card">
                <div class="stat-value" style="font-size:1.5rem;">{stats.get('bazi', 0)}</div>
                <div class="stat-label">八字分析</div>
            </div>
            <div class="stat-card">
                <div class="stat-value" style="font-size:1.5rem;">{stats.get('ziwei', 0)}</div>
                <div class="stat-label">紫微排盤</div>
            </div>
            <div class="stat-card">
                <div class="stat-value" style="font-size:1.5rem;">{stats.get('meihua', 0)}</div>
                <div class="stat-label">梅花起卦</div>
            </div>
            <div class="stat-card">
                <div class="stat-value" style="font-size:1.5rem;">{stats.get('dates', 0)}</div>
                <div class="stat-label">擇日查詢</div>
            </div>
            <div class="stat-card">
                <div class="stat-value" style="font-size:1.5rem;">{stats.get('matches', 0)}</div>
                <div class="stat-label">合婚分析</div>
            </div>
        </div>
    </div>
    
    <div class="card">
        <h2>⚙️ 系統資訊</h2>
        <table class="table">
            <tr><td>版本</td><td>{settings.app.APP_VERSION}</td></tr>
            <tr><td>環境</td><td>{settings.app.ENV}</td></tr>
            <tr><td>數據庫</td><td>{settings.db.DB_PATH}</td></tr>
            <tr><td>時間</td><td>{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</td></tr>
        </table>
    </div>
    """
    
    return render_admin_page("首頁", content, "home")


@app.get("/admin/users", response_class=HTMLResponse)
async def admin_users(admin: str = Depends(verify_admin)):
    """用戶管理"""
    users = db.query("auth_users", order_by="created_at DESC", limit=50)
    
    rows = ""
    for u in users:
        status = '<span class="badge badge-success">啟用</span>' if u.get('is_active') else '<span class="badge badge-danger">停用</span>'
        rows += f"""
        <tr>
            <td>{u.get('id')}</td>
            <td>{u.get('username')}</td>
            <td>{u.get('email', '-')}</td>
            <td>{u.get('credits', 0)}</td>
            <td>{u.get('tier', 'free')}</td>
            <td>{status}</td>
            <td>{u.get('last_login_at', '-')[:10] if u.get('last_login_at') else '-'}</td>
            <td>
                <a href="/admin/user/{u.get('id')}" class="btn btn-primary btn-sm">詳情</a>
            </td>
        </tr>
        """
    
    content = f"""
    <div class="card">
        <h2>👤 用戶管理</h2>
        <table class="table">
            <thead>
                <tr>
                    <th>ID</th>
                    <th>用戶名</th>
                    <th>郵箱</th>
                    <th>點數</th>
                    <th>等級</th>
                    <th>狀態</th>
                    <th>最後登入</th>
                    <th>操作</th>
                </tr>
            </thead>
            <tbody>
                {rows if rows else '<tr><td colspan="8" style="text-align:center;color:#718096;">暫無用戶</td></tr>'}
            </tbody>
        </table>
    </div>
    """
    
    return render_admin_page("用戶管理", content, "users")


@app.get("/admin/user/{user_id}", response_class=HTMLResponse)
async def admin_user_detail(user_id: int, admin: str = Depends(verify_admin)):
    """用戶詳情"""
    user = db.get_by_id("auth_users", user_id)
    if not user:
        raise HTTPException(404, "用戶不存在")
    
    # 獲取用戶記錄
    profiles = db.query("user_profiles", {"user_id": user_id})
    credit_logs = db.query("credit_logs", {"user_id": user_id}, order_by="created_at DESC", limit=10)
    
    credit_rows = ""
    for log in credit_logs:
        amount = log.get('change_amount', 0)
        color = 'color:#38a169' if amount > 0 else 'color:#e53e3e'
        credit_rows += f"""
        <tr>
            <td>{log.get('created_at', '')[:16]}</td>
            <td>{log.get('change_type')}</td>
            <td style="{color}">{'+' if amount > 0 else ''}{amount}</td>
            <td>{log.get('balance_after')}</td>
            <td>{log.get('description', '-')}</td>
        </tr>
        """
    
    content = f"""
    <div class="card">
        <h2>用戶詳情：{user.get('username')}</h2>
        <table class="table">
            <tr><td style="width:150px;">ID</td><td>{user.get('id')}</td></tr>
            <tr><td>UUID</td><td>{user.get('uuid')}</td></tr>
            <tr><td>郵箱</td><td>{user.get('email', '-')}</td></tr>
            <tr><td>點數</td><td><strong>{user.get('credits', 0)}</strong></td></tr>
            <tr><td>等級</td><td>{user.get('tier', 'free')}</td></tr>
            <tr><td>登入次數</td><td>{user.get('login_count', 0)}</td></tr>
            <tr><td>註冊時間</td><td>{user.get('created_at')}</td></tr>
            <tr><td>最後登入</td><td>{user.get('last_login_at', '-')}</td></tr>
        </table>
    </div>
    
    <div class="card">
        <h2>調整點數</h2>
        <form action="/admin/user/{user_id}/credits" method="POST" style="display:flex;gap:12px;align-items:end;">
            <div class="form-group" style="margin:0;">
                <label>數量</label>
                <input type="number" name="amount" class="form-control" style="width:120px;" placeholder="例：100">
            </div>
            <div class="form-group" style="margin:0;flex:1;">
                <label>原因</label>
                <input type="text" name="reason" class="form-control" placeholder="例：系統補償">
            </div>
            <button type="submit" class="btn btn-success">確認調整</button>
        </form>
    </div>
    
    <div class="card">
        <h2>點數記錄</h2>
        <table class="table">
            <thead>
                <tr><th>時間</th><th>類型</th><th>變動</th><th>餘額</th><th>說明</th></tr>
            </thead>
            <tbody>
                {credit_rows if credit_rows else '<tr><td colspan="5" style="text-align:center;color:#718096;">無記錄</td></tr>'}
            </tbody>
        </table>
    </div>
    
    <a href="/admin/users" class="btn btn-primary">← 返回用戶列表</a>
    """
    
    return render_admin_page(f"用戶：{user.get('username')}", content, "users")


@app.post("/admin/user/{user_id}/credits")
async def admin_adjust_credits(
    user_id: int, 
    amount: int = Form(...), 
    reason: str = Form(""),
    admin: str = Depends(verify_admin)
):
    """調整用戶點數"""
    change_type = "admin_add" if amount > 0 else "admin_deduct"
    success, new_balance = db.update_credits(user_id, amount, change_type, reason or f"管理員調整")
    
    if success:
        return RedirectResponse(f"/admin/user/{user_id}?msg=success", status_code=303)
    else:
        return RedirectResponse(f"/admin/user/{user_id}?msg=failed", status_code=303)


@app.get("/admin/orders", response_class=HTMLResponse)
async def admin_orders(admin: str = Depends(verify_admin)):
    """訂單管理"""
    orders = db.query("purchase_records", order_by="created_at DESC", limit=50)
    
    rows = ""
    for o in orders:
        status_map = {
            'pending': '<span class="badge badge-warning">待付款</span>',
            'paid': '<span class="badge badge-success">已付款</span>',
            'failed': '<span class="badge badge-danger">失敗</span>',
            'refunded': '<span class="badge badge-warning">已退款</span>',
        }
        status = status_map.get(o.get('status'), o.get('status'))
        rows += f"""
        <tr>
            <td>{o.get('order_no')}</td>
            <td>{o.get('user_id')}</td>
            <td>{o.get('plan_name', o.get('plan_code'))}</td>
            <td>NT${o.get('amount', 0):,}</td>
            <td>{status}</td>
            <td>{o.get('created_at', '')[:16]}</td>
            <td>{o.get('paid_at', '-')[:16] if o.get('paid_at') else '-'}</td>
        </tr>
        """
    
    content = f"""
    <div class="card">
        <h2>💰 訂單管理</h2>
        <table class="table">
            <thead>
                <tr>
                    <th>訂單號</th>
                    <th>用戶ID</th>
                    <th>方案</th>
                    <th>金額</th>
                    <th>狀態</th>
                    <th>建立時間</th>
                    <th>付款時間</th>
                </tr>
            </thead>
            <tbody>
                {rows if rows else '<tr><td colspan="7" style="text-align:center;color:#718096;">暫無訂單</td></tr>'}
            </tbody>
        </table>
    </div>
    """
    
    return render_admin_page("訂單管理", content, "orders")


@app.get("/admin/reports", response_class=HTMLResponse)
async def admin_reports(admin: str = Depends(verify_admin)):
    """報告管理"""
    reports = db.query("report_records", order_by="created_at DESC", limit=50)
    
    rows = ""
    for r in reports:
        rows += f"""
        <tr>
            <td>{r.get('id')}</td>
            <td>{r.get('user_id')}</td>
            <td>{r.get('report_type')}</td>
            <td>{r.get('report_level', '-')}</td>
            <td>{r.get('credits_used', 0)}</td>
            <td>{r.get('created_at', '')[:16]}</td>
        </tr>
        """
    
    content = f"""
    <div class="card">
        <h2>📄 報告記錄</h2>
        <table class="table">
            <thead>
                <tr>
                    <th>ID</th>
                    <th>用戶ID</th>
                    <th>類型</th>
                    <th>等級</th>
                    <th>點數</th>
                    <th>生成時間</th>
                </tr>
            </thead>
            <tbody>
                {rows if rows else '<tr><td colspan="6" style="text-align:center;color:#718096;">暫無報告</td></tr>'}
            </tbody>
        </table>
    </div>
    """
    
    return render_admin_page("報告管理", content, "reports")


# ════════════════════════════════════════════════════════════════════
# 啟動
# ════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    import uvicorn
    print("🛠️ 管理後台啟動中...")
    print("   http://localhost:8001/admin/")
    print(f"   用戶名: {ADMIN_USERNAME}")
    uvicorn.run(app, host="0.0.0.0", port=8001)
