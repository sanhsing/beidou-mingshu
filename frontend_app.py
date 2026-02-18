#!/usr/bin/env python3
"""
frontend_app.py - 北斗命數統一前端應用
版本：v1.0.0

═══════════════════════════════════════════════════════════════════════
整合所有前端頁面：
  • 首頁（登入/註冊）
  • 命理報告
  • 命名/婚嫁/擇日
  • 用戶中心
  • 管理後台
═══════════════════════════════════════════════════════════════════════

PYLIB First：整合 frontend/ 目錄 2300 行 HTML
XTF Task Chain
@11星協作：@織明(統籌) @璃語(介面)
"""

from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
import os

# ════════════════════════════════════════════════════════════════════
# App 配置
# ════════════════════════════════════════════════════════════════════

app = FastAPI(title="北斗命數", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# 靜態文件
FRONTEND_DIR = os.path.join(os.path.dirname(__file__), "frontend")
if os.path.exists(FRONTEND_DIR):
    app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")

# ════════════════════════════════════════════════════════════════════
# 共用組件
# ════════════════════════════════════════════════════════════════════

COMMON_STYLES = """
:root {
    --primary: #1E3A5F;
    --secondary: #4A90A4;
    --accent: #E8B85B;
    --success: #4CAF50;
    --warning: #F59E0B;
    --danger: #EF4444;
    --bg: #F8FAFC;
    --card: #FFFFFF;
    --text: #1A202C;
    --muted: #64748B;
    --border: #E2E8F0;
}

* { box-sizing: border-box; margin: 0; padding: 0; }

body {
    font-family: -apple-system, BlinkMacSystemFont, 'PingFang TC', 'Microsoft JhengHei', sans-serif;
    background: var(--bg);
    color: var(--text);
    line-height: 1.6;
}

.container { max-width: 1200px; margin: 0 auto; padding: 20px; }

/* 導航欄 */
.navbar {
    background: var(--primary);
    color: white;
    padding: 0 20px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    height: 60px;
    position: sticky;
    top: 0;
    z-index: 100;
}

.navbar-brand {
    font-size: 1.4rem;
    font-weight: bold;
    color: white;
    text-decoration: none;
    display: flex;
    align-items: center;
    gap: 8px;
}

.navbar-nav {
    display: flex;
    gap: 8px;
    list-style: none;
}

.navbar-nav a {
    color: rgba(255,255,255,0.85);
    text-decoration: none;
    padding: 8px 16px;
    border-radius: 6px;
    transition: all 0.2s;
}

.navbar-nav a:hover, .navbar-nav a.active {
    background: rgba(255,255,255,0.15);
    color: white;
}

.navbar-user {
    display: flex;
    align-items: center;
    gap: 12px;
}

.navbar-credits {
    background: var(--accent);
    padding: 4px 12px;
    border-radius: 20px;
    font-size: 0.85rem;
}

.navbar-avatar {
    width: 36px;
    height: 36px;
    border-radius: 50%;
    background: var(--secondary);
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
}

/* 卡片 */
.card {
    background: var(--card);
    border-radius: 12px;
    padding: 24px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.06);
    margin-bottom: 20px;
}

.card-header {
    font-size: 1.2rem;
    font-weight: 600;
    color: var(--primary);
    margin-bottom: 16px;
    display: flex;
    align-items: center;
    gap: 8px;
}

/* 按鈕 */
.btn {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    gap: 8px;
    padding: 12px 24px;
    border: none;
    border-radius: 8px;
    font-size: 1rem;
    font-weight: 500;
    cursor: pointer;
    transition: all 0.2s;
}

.btn-primary {
    background: var(--primary);
    color: white;
}

.btn-primary:hover { background: #2d5a87; }

.btn-accent {
    background: var(--accent);
    color: white;
}

.btn-outline {
    background: transparent;
    border: 2px solid var(--border);
    color: var(--text);
}

.btn-outline:hover {
    border-color: var(--primary);
    color: var(--primary);
}

/* 表單 */
.form-group { margin-bottom: 16px; }

.form-group label {
    display: block;
    margin-bottom: 6px;
    font-weight: 500;
    color: var(--muted);
}

.form-control {
    width: 100%;
    padding: 12px 16px;
    border: 2px solid var(--border);
    border-radius: 8px;
    font-size: 1rem;
    transition: all 0.2s;
}

.form-control:focus {
    outline: none;
    border-color: var(--secondary);
}

.form-row {
    display: flex;
    gap: 12px;
}

.form-row .form-group { flex: 1; }

/* 功能卡片 */
.feature-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
    gap: 20px;
}

.feature-card {
    background: var(--card);
    border-radius: 12px;
    padding: 24px;
    text-align: center;
    box-shadow: 0 2px 8px rgba(0,0,0,0.06);
    cursor: pointer;
    transition: all 0.2s;
    border: 2px solid transparent;
}

.feature-card:hover {
    transform: translateY(-4px);
    box-shadow: 0 8px 24px rgba(0,0,0,0.12);
    border-color: var(--secondary);
}

.feature-icon {
    font-size: 3rem;
    margin-bottom: 12px;
}

.feature-title {
    font-size: 1.2rem;
    font-weight: 600;
    margin-bottom: 8px;
}

.feature-desc {
    color: var(--muted);
    font-size: 0.9rem;
}

/* 表格 */
.table {
    width: 100%;
    border-collapse: collapse;
}

.table th, .table td {
    padding: 12px;
    text-align: left;
    border-bottom: 1px solid var(--border);
}

.table th {
    background: var(--bg);
    font-weight: 600;
    color: var(--muted);
}

/* 標籤 */
.badge {
    display: inline-block;
    padding: 4px 10px;
    border-radius: 20px;
    font-size: 0.8rem;
    font-weight: 500;
}

.badge-success { background: #DEF7EC; color: #03543F; }
.badge-warning { background: #FEF3C7; color: #92400E; }
.badge-danger { background: #FEE2E2; color: #991B1B; }

/* Modal */
.modal-overlay {
    display: none;
    position: fixed;
    top: 0; left: 0; right: 0; bottom: 0;
    background: rgba(0,0,0,0.5);
    z-index: 1000;
    align-items: center;
    justify-content: center;
}

.modal-overlay.active { display: flex; }

.modal {
    background: white;
    border-radius: 16px;
    padding: 32px;
    max-width: 480px;
    width: 90%;
    max-height: 90vh;
    overflow-y: auto;
}

.modal-header {
    font-size: 1.4rem;
    font-weight: 600;
    margin-bottom: 20px;
}

/* 響應式 */
@media (max-width: 768px) {
    .navbar-nav { display: none; }
    .form-row { flex-direction: column; }
    .feature-grid { grid-template-columns: 1fr; }
}
"""

COMMON_JS = """
// ═══════════════════════════════════════════════════════════════
// 北斗命數前端 API 配置
// XTF Task Chain: B1
// @11星協作：@璃語(介面)
// ═══════════════════════════════════════════════════════════════

// API 配置
const API_BASE = window.location.origin;

// 狀態管理
const state = {
    user: null,
    token: localStorage.getItem('beidou_token'),
    loading: false,
};

// API 請求
async function api(path, options = {}) {
    const headers = { 'Content-Type': 'application/json' };
    if (state.token) {
        headers['Authorization'] = `Bearer ${state.token}`;
    }
    
    const res = await fetch(API_BASE + path, {
        ...options,
        headers: { ...headers, ...options.headers },
        body: options.body ? JSON.stringify(options.body) : undefined,
    });
    
    if (res.status === 401) {
        logout();
        return null;
    }
    
    return res.json();
}

// 登入
async function login(username, password) {
    state.loading = true;
    try {
        const data = await api('/api/auth/login', {
            method: 'POST',
            body: { username, password },
        });
        
        if (data && data.access_token) {
            state.token = data.access_token;
            state.user = data.user;
            localStorage.setItem('beidou_token', data.access_token);
            return true;
        }
        return false;
    } finally {
        state.loading = false;
    }
}

// 登出
function logout() {
    state.token = null;
    state.user = null;
    localStorage.removeItem('beidou_token');
    window.location.href = '/login';
}

// 檢查登入
async function checkAuth() {
    if (!state.token) return false;
    
    const user = await api('/api/auth/me');
    if (user && user.id) {
        state.user = user;
        return true;
    }
    return false;
}

// 更新導航欄
function updateNavbar() {
    const userArea = document.getElementById('navbar-user');
    if (!userArea) return;
    
    if (state.user) {
        userArea.innerHTML = `
            <span class="navbar-credits">💎 ${state.user.credits}</span>
            <div class="navbar-avatar" onclick="toggleUserMenu()">
                ${state.user.username.charAt(0).toUpperCase()}
            </div>
        `;
    } else {
        userArea.innerHTML = `
            <a href="/login" class="btn btn-outline" style="color:white;border-color:rgba(255,255,255,0.3)">登入</a>
        `;
    }
}

// 格式化日期
function formatDate(dateStr) {
    const d = new Date(dateStr);
    return d.toLocaleDateString('zh-TW');
}

// 顯示提示
function showToast(message, type = 'info') {
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.textContent = message;
    toast.style.cssText = `
        position: fixed; bottom: 20px; right: 20px;
        padding: 12px 24px; border-radius: 8px;
        background: ${type === 'error' ? '#EF4444' : type === 'success' ? '#10B981' : '#3B82F6'};
        color: white; z-index: 2000;
    `;
    document.body.appendChild(toast);
    setTimeout(() => toast.remove(), 3000);
}

// 頁面載入
document.addEventListener('DOMContentLoaded', async () => {
    await checkAuth();
    updateNavbar();
});
"""

# ════════════════════════════════════════════════════════════════════
# 頁面組件
# ════════════════════════════════════════════════════════════════════

def render_navbar(active: str = ""):
    """渲染導航欄"""
    return f"""
    <nav class="navbar">
        <a href="/" class="navbar-brand">
            <span>⭐</span> 北斗命數
        </a>
        <ul class="navbar-nav">
            <li><a href="/" class="{'active' if active == 'home' else ''}">首頁</a></li>
            <li><a href="/bazi" class="{'active' if active == 'bazi' else ''}">八字分析</a></li>
            <li><a href="/ziwei" class="{'active' if active == 'ziwei' else ''}">紫微斗數</a></li>
            <li><a href="/date" class="{'active' if active == 'date' else ''}">擇日</a></li>
            <li><a href="/naming" class="{'active' if active == 'naming' else ''}">命名</a></li>
            <li><a href="/reports" class="{'active' if active == 'reports' else ''}">我的報告</a></li>
        </ul>
        <div class="navbar-user" id="navbar-user">
            <a href="/login" class="btn btn-outline" style="color:white;border-color:rgba(255,255,255,0.3)">登入</a>
        </div>
    </nav>
    """

def render_page(title: str, content: str, active: str = "", need_auth: bool = False):
    """渲染完整頁面"""
    return f"""
    <!DOCTYPE html>
    <html lang="zh-TW">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{title} | 北斗命數</title>
        <style>{COMMON_STYLES}</style>
    </head>
    <body>
        {render_navbar(active)}
        <main class="container">
            {content}
        </main>
        <script>{COMMON_JS}</script>
        {'<script>if(!state.token) window.location.href="/login";</script>' if need_auth else ''}
    </body>
    </html>
    """

# ════════════════════════════════════════════════════════════════════
# 頁面路由
# ════════════════════════════════════════════════════════════════════

@app.get("/", response_class=HTMLResponse)
async def home():
    """首頁"""
    content = """
    <div style="text-align:center; padding:40px 0;">
        <h1 style="font-size:2.5rem; color:var(--primary); margin-bottom:16px;">
            ⭐ 北斗命數
        </h1>
        <p style="font-size:1.2rem; color:var(--muted); margin-bottom:40px;">
            個人化決策框架生成系統
        </p>
    </div>
    
    <div class="feature-grid">
        <div class="feature-card" onclick="location.href='/bazi'">
            <div class="feature-icon">🔮</div>
            <div class="feature-title">八字分析</div>
            <div class="feature-desc">四柱八字、大運流年、用神喜忌</div>
        </div>
        
        <div class="feature-card" onclick="location.href='/ziwei'">
            <div class="feature-icon">⭐</div>
            <div class="feature-title">紫微斗數</div>
            <div class="feature-desc">命盤排盤、十二宮位、星曜分析</div>
        </div>
        
        <div class="feature-card" onclick="location.href='/meihua'">
            <div class="feature-icon">🌸</div>
            <div class="feature-title">梅花易數</div>
            <div class="feature-desc">先天起卦、體用分析、占卜問事</div>
        </div>
        
        <div class="feature-card" onclick="location.href='/date'">
            <div class="feature-icon">📅</div>
            <div class="feature-title">擇日</div>
            <div class="feature-desc">嫁娶、動土、開市、搬家吉日</div>
        </div>
        
        <div class="feature-card" onclick="location.href='/naming'">
            <div class="feature-icon">📝</div>
            <div class="feature-title">命名</div>
            <div class="feature-desc">嬰兒取名、成人改名、公司命名</div>
        </div>
        
        <div class="feature-card" onclick="location.href='/match'">
            <div class="feature-icon">💑</div>
            <div class="feature-title">合婚配對</div>
            <div class="feature-desc">八字合婚、親子配對、合作分析</div>
        </div>
    </div>
    
    <div class="card" style="margin-top:40px; text-align:center;">
        <h3 style="margin-bottom:16px;">🎁 新用戶優惠</h3>
        <p style="color:var(--muted); margin-bottom:20px;">
            註冊即贈送 100 點數，可免費體驗入門版報告
        </p>
        <a href="/register" class="btn btn-accent">立即註冊</a>
    </div>
    """
    return render_page("首頁", content, "home")


@app.get("/login", response_class=HTMLResponse)
async def login_page():
    """登入頁"""
    content = """
    <div style="max-width:400px; margin:60px auto;">
        <div class="card">
            <h2 style="text-align:center; margin-bottom:24px;">登入</h2>
            
            <form onsubmit="handleLogin(event)">
                <div class="form-group">
                    <label>用戶名</label>
                    <input type="text" id="username" class="form-control" required>
                </div>
                
                <div class="form-group">
                    <label>密碼</label>
                    <input type="password" id="password" class="form-control" required>
                </div>
                
                <button type="submit" class="btn btn-primary" style="width:100%;">
                    登入
                </button>
            </form>
            
            <p style="text-align:center; margin-top:20px; color:var(--muted);">
                還沒有帳號？<a href="/register" style="color:var(--secondary);">立即註冊</a>
            </p>
        </div>
    </div>
    
    <script>
    async function handleLogin(e) {
        e.preventDefault();
        const username = document.getElementById('username').value;
        const password = document.getElementById('password').value;
        
        const success = await login(username, password);
        if (success) {
            showToast('登入成功！', 'success');
            setTimeout(() => window.location.href = '/', 1000);
        } else {
            showToast('用戶名或密碼錯誤', 'error');
        }
    }
    </script>
    """
    return render_page("登入", content)


@app.get("/register", response_class=HTMLResponse)
async def register_page():
    """註冊頁"""
    content = """
    <div style="max-width:400px; margin:60px auto;">
        <div class="card">
            <h2 style="text-align:center; margin-bottom:24px;">註冊</h2>
            
            <form onsubmit="handleRegister(event)">
                <div class="form-group">
                    <label>用戶名</label>
                    <input type="text" id="username" class="form-control" required minlength="3">
                </div>
                
                <div class="form-group">
                    <label>電子郵件</label>
                    <input type="email" id="email" class="form-control">
                </div>
                
                <div class="form-group">
                    <label>密碼</label>
                    <input type="password" id="password" class="form-control" required minlength="6">
                </div>
                
                <div class="form-group">
                    <label>確認密碼</label>
                    <input type="password" id="password2" class="form-control" required>
                </div>
                
                <button type="submit" class="btn btn-primary" style="width:100%;">
                    註冊
                </button>
            </form>
            
            <p style="text-align:center; margin-top:20px; color:var(--muted);">
                已有帳號？<a href="/login" style="color:var(--secondary);">登入</a>
            </p>
        </div>
    </div>
    
    <script>
    async function handleRegister(e) {
        e.preventDefault();
        const username = document.getElementById('username').value;
        const email = document.getElementById('email').value;
        const password = document.getElementById('password').value;
        const password2 = document.getElementById('password2').value;
        
        if (password !== password2) {
            showToast('兩次密碼不一致', 'error');
            return;
        }
        
        const data = await api('/api/auth/register', {
            method: 'POST',
            body: { username, email, password },
        });
        
        if (data && data.success) {
            showToast('註冊成功！請登入', 'success');
            setTimeout(() => window.location.href = '/login', 1500);
        } else {
            showToast(data?.message || '註冊失敗', 'error');
        }
    }
    </script>
    """
    return render_page("註冊", content)


@app.get("/bazi", response_class=HTMLResponse)
async def bazi_page():
    """八字分析頁"""
    content = """
    <h1 style="margin-bottom:24px;">🔮 八字分析</h1>
    
    <div class="card">
        <div class="card-header">輸入出生資料</div>
        
        <form onsubmit="analyzeBazi(event)">
            <div class="form-row">
                <div class="form-group">
                    <label>年</label>
                    <input type="number" id="year" class="form-control" value="1990" min="1900" max="2100" required>
                </div>
                <div class="form-group">
                    <label>月</label>
                    <input type="number" id="month" class="form-control" value="6" min="1" max="12" required>
                </div>
                <div class="form-group">
                    <label>日</label>
                    <input type="number" id="day" class="form-control" value="15" min="1" max="31" required>
                </div>
                <div class="form-group">
                    <label>時</label>
                    <input type="number" id="hour" class="form-control" value="12" min="0" max="23" required>
                </div>
            </div>
            
            <div class="form-row">
                <div class="form-group">
                    <label>性別</label>
                    <select id="gender" class="form-control">
                        <option value="男">男</option>
                        <option value="女">女</option>
                    </select>
                </div>
                <div class="form-group">
                    <label>曆法</label>
                    <select id="calendar" class="form-control">
                        <option value="solar">國曆</option>
                        <option value="lunar">農曆</option>
                    </select>
                </div>
            </div>
            
            <button type="submit" class="btn btn-primary">開始分析</button>
        </form>
    </div>
    
    <div id="result" style="display:none;">
        <div class="card">
            <div class="card-header">📊 分析結果</div>
            <div id="result-content"></div>
        </div>
    </div>
    
    <script>
    async function analyzeBazi(e) {
        e.preventDefault();
        
        const data = {
            year: parseInt(document.getElementById('year').value),
            month: parseInt(document.getElementById('month').value),
            day: parseInt(document.getElementById('day').value),
            hour: parseInt(document.getElementById('hour').value),
            gender: document.getElementById('gender').value,
            calendar: document.getElementById('calendar').value,
        };
        
        showToast('分析中...', 'info');
        
        const result = await api('/api/bazi/analyze', {
            method: 'POST',
            body: data,
        });
        
        if (result && result.四柱) {
            document.getElementById('result').style.display = 'block';
            document.getElementById('result-content').innerHTML = `
                <div style="display:grid; grid-template-columns:repeat(4,1fr); gap:12px; text-align:center; margin-bottom:20px;">
                    <div class="card" style="padding:16px;">
                        <div style="color:var(--muted);">年柱</div>
                        <div style="font-size:1.5rem; font-weight:bold;">${result.四柱.年柱}</div>
                    </div>
                    <div class="card" style="padding:16px;">
                        <div style="color:var(--muted);">月柱</div>
                        <div style="font-size:1.5rem; font-weight:bold;">${result.四柱.月柱}</div>
                    </div>
                    <div class="card" style="padding:16px;">
                        <div style="color:var(--muted);">日柱</div>
                        <div style="font-size:1.5rem; font-weight:bold;">${result.四柱.日柱}</div>
                    </div>
                    <div class="card" style="padding:16px;">
                        <div style="color:var(--muted);">時柱</div>
                        <div style="font-size:1.5rem; font-weight:bold;">${result.四柱.時柱}</div>
                    </div>
                </div>
                <p><strong>日主：</strong>${result.日主?.天干 || '-'} (${result.日主?.五行 || '-'})</p>
                <p><strong>用神：</strong>${result.用神喜忌?.用神 || '-'}</p>
                <p><strong>喜神：</strong>${result.用神喜忌?.喜神 || '-'}</p>
            `;
            showToast('分析完成！', 'success');
        } else {
            showToast('分析失敗，請重試', 'error');
        }
    }
    </script>
    """
    return render_page("八字分析", content, "bazi")


@app.get("/reports", response_class=HTMLResponse)
async def reports_page():
    """我的報告頁"""
    content = """
    <h1 style="margin-bottom:24px;">📄 我的報告</h1>
    
    <div class="card">
        <table class="table">
            <thead>
                <tr>
                    <th>報告類型</th>
                    <th>等級</th>
                    <th>生成時間</th>
                    <th>操作</th>
                </tr>
            </thead>
            <tbody id="reports-list">
                <tr>
                    <td colspan="4" style="text-align:center; color:var(--muted);">
                        載入中...
                    </td>
                </tr>
            </tbody>
        </table>
    </div>
    
    <script>
    document.addEventListener('DOMContentLoaded', async () => {
        if (!state.token) {
            window.location.href = '/login';
            return;
        }
        
        const reports = await api('/api/records/report');
        const list = document.getElementById('reports-list');
        
        if (reports && reports.records && reports.records.length > 0) {
            list.innerHTML = reports.records.map(r => `
                <tr>
                    <td>${r.report_type || '-'}</td>
                    <td><span class="badge badge-success">${r.report_level || 'L1'}</span></td>
                    <td>${formatDate(r.created_at)}</td>
                    <td>
                        ${r.file_path ? `<a href="${r.file_path}" class="btn btn-outline" style="padding:6px 12px;" download>下載</a>` : '-'}
                    </td>
                </tr>
            `).join('');
        } else {
            list.innerHTML = `
                <tr>
                    <td colspan="4" style="text-align:center; color:var(--muted); padding:40px;">
                        暫無報告，<a href="/bazi" style="color:var(--secondary);">開始分析</a>生成您的第一份報告
                    </td>
                </tr>
            `;
        }
    });
    </script>
    """
    return render_page("我的報告", content, "reports", need_auth=True)


@app.get("/user", response_class=HTMLResponse)
async def user_page():
    """用戶中心頁"""
    content = """
    <h1 style="margin-bottom:24px;">👤 用戶中心</h1>
    
    <div class="card">
        <div class="card-header">基本資訊</div>
        <div id="user-info">載入中...</div>
    </div>
    
    <div class="card">
        <div class="card-header">💎 點數</div>
        <div style="display:flex; align-items:center; gap:20px;">
            <span style="font-size:2rem; font-weight:bold;" id="user-credits">-</span>
            <a href="/pricing" class="btn btn-accent">購買點數</a>
        </div>
    </div>
    
    <div class="card">
        <div class="card-header">出生資料</div>
        <div id="user-profiles">載入中...</div>
        <button class="btn btn-outline" onclick="showAddProfile()" style="margin-top:16px;">
            + 添加資料
        </button>
    </div>
    
    <script>
    document.addEventListener('DOMContentLoaded', async () => {
        // 用戶資訊
        const user = await api('/api/auth/me');
        if (user) {
            document.getElementById('user-info').innerHTML = `
                <p><strong>用戶名：</strong>${user.username}</p>
                <p><strong>郵箱：</strong>${user.email || '-'}</p>
                <p><strong>會員等級：</strong>${user.tier}</p>
                <p><strong>註冊時間：</strong>${formatDate(user.created_at)}</p>
            `;
            document.getElementById('user-credits').textContent = user.credits;
        }
        
        // 出生資料
        const profiles = await api('/api/profiles');
        const list = document.getElementById('user-profiles');
        if (profiles && profiles.profiles && profiles.profiles.length > 0) {
            list.innerHTML = profiles.profiles.map(p => `
                <div style="padding:12px; border:1px solid var(--border); border-radius:8px; margin-bottom:8px;">
                    <strong>${p.name}</strong> (${p.gender})
                    <br>
                    <span style="color:var(--muted);">
                        ${p.birth_year}/${p.birth_month}/${p.birth_day} ${p.birth_hour}時
                    </span>
                </div>
            `).join('');
        } else {
            list.innerHTML = '<p style="color:var(--muted);">尚未添加出生資料</p>';
        }
    });
    </script>
    """
    return render_page("用戶中心", content, need_auth=True)


@app.get("/pricing", response_class=HTMLResponse)
async def pricing_page():
    """定價頁"""
    content = """
    <h1 style="text-align:center; margin-bottom:40px;">💰 點數方案</h1>
    
    <div class="feature-grid">
        <div class="card" style="text-align:center;">
            <h3>100 點數</h3>
            <div style="font-size:2rem; font-weight:bold; color:var(--primary); margin:16px 0;">
                NT$ 100
            </div>
            <p style="color:var(--muted); margin-bottom:20px;">適合體驗</p>
            <button class="btn btn-primary" onclick="purchase('credit_100')">購買</button>
        </div>
        
        <div class="card" style="text-align:center; border:2px solid var(--accent);">
            <span class="badge badge-warning" style="margin-bottom:12px;">熱門</span>
            <h3>500 點數</h3>
            <div style="font-size:2rem; font-weight:bold; color:var(--primary); margin:16px 0;">
                NT$ 450
            </div>
            <p style="color:var(--muted); margin-bottom:20px;">省 10%</p>
            <button class="btn btn-accent" onclick="purchase('credit_500')">購買</button>
        </div>
        
        <div class="card" style="text-align:center;">
            <h3>1000 點數</h3>
            <div style="font-size:2rem; font-weight:bold; color:var(--primary); margin:16px 0;">
                NT$ 800
            </div>
            <p style="color:var(--muted); margin-bottom:20px;">省 20%</p>
            <button class="btn btn-primary" onclick="purchase('credit_1000')">購買</button>
        </div>
    </div>
    
    <h2 style="text-align:center; margin:60px 0 40px;">📄 報告方案</h2>
    
    <div class="feature-grid">
        <div class="card">
            <h3>L1 入門版</h3>
            <div style="font-size:1.8rem; font-weight:bold; color:var(--primary); margin:16px 0;">
                50 點
            </div>
            <ul style="color:var(--muted); padding-left:20px; margin-bottom:20px;">
                <li>八字基礎分析</li>
                <li>五行分布圖</li>
                <li>PDF 報告</li>
            </ul>
        </div>
        
        <div class="card">
            <h3>L2 進階版</h3>
            <div style="font-size:1.8rem; font-weight:bold; color:var(--primary); margin:16px 0;">
                150 點
            </div>
            <ul style="color:var(--muted); padding-left:20px; margin-bottom:20px;">
                <li>完整八字+紫微</li>
                <li>大運流年分析</li>
                <li>PDF 報告 15-20頁</li>
            </ul>
        </div>
        
        <div class="card">
            <h3>L3 顧問版</h3>
            <div style="font-size:1.8rem; font-weight:bold; color:var(--primary); margin:16px 0;">
                500 點
            </div>
            <ul style="color:var(--muted); padding-left:20px; margin-bottom:20px;">
                <li>全套命理分析</li>
                <li>個人決策模型</li>
                <li>60分鐘線上講解</li>
            </ul>
        </div>
    </div>
    
    <script>
    async function purchase(planCode) {
        if (!state.token) {
            showToast('請先登入', 'warning');
            setTimeout(() => window.location.href = '/login', 1500);
            return;
        }
        
        showToast('建立訂單中...', 'info');
        
        // 調用支付 API
        const result = await api('/api/payment/create', {
            method: 'POST',
            body: { 
                plan_code: planCode,
                provider: 'ecpay'
            },
        });
        
        if (result && result.success && result.payment_url) {
            showToast('跳轉支付頁面...', 'success');
            // 跳轉到支付頁面
            window.location.href = result.payment_url;
        } else if (result && result.form_html) {
            // 綠界表單提交方式
            document.body.insertAdjacentHTML('beforeend', result.form_html);
            document.getElementById('ecpay-form')?.submit();
        } else {
            showToast(result?.message || '建立訂單失敗', 'error');
        }
    }
    </script>
    """
    return render_page("定價", content)


# ════════════════════════════════════════════════════════════════════
# 靜態頁面代理
# ════════════════════════════════════════════════════════════════════

@app.get("/landing", response_class=HTMLResponse)
async def landing():
    """行銷落地頁"""
    path = os.path.join(FRONTEND_DIR, "landing.html")
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    raise HTTPException(404)

@app.get("/naming", response_class=HTMLResponse)
async def naming():
    """命名頁"""
    path = os.path.join(FRONTEND_DIR, "naming.html")
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    raise HTTPException(404)

@app.get("/feedback", response_class=HTMLResponse)
async def feedback():
    """回饋頁"""
    path = os.path.join(FRONTEND_DIR, "feedback.html")
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    raise HTTPException(404)


# ════════════════════════════════════════════════════════════════════
# 啟動
# ════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    import uvicorn
    print("🌟 北斗命數前端啟動中...")
    print("   http://localhost:8080")
    uvicorn.run(app, host="0.0.0.0", port=8080)
