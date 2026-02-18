"""
認證頁面模組
auth_pages.py | @星殼 | 2026-02-17

頁面：
- /login - 登入
- /register - 註冊
- /forgot-password - 忘記密碼
- /reset-password - 重設密碼
- /change-password - 變更密碼（需登入）
"""
from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter(tags=["auth-pages"])

# === 共用樣式 ===
BASE_STYLE = '''
<script src="https://cdn.tailwindcss.com"></script>
<style>
    .gradient-bg { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); }
    .card { background: white; border-radius: 1rem; box-shadow: 0 10px 40px rgba(0,0,0,0.1); }
</style>
'''

# === 登入頁面 ===
LOGIN_PAGE = '''<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>登入 - 北斗命數</title>
    ''' + BASE_STYLE + '''
</head>
<body class="gradient-bg min-h-screen flex items-center justify-center p-4">
    <div class="card p-8 w-full max-w-md">
        <div class="text-center mb-8">
            <h1 class="text-3xl font-bold text-gray-800">🌟 北斗命數</h1>
            <p class="text-gray-600 mt-2">登入您的帳號</p>
        </div>
        
        <form id="login-form" class="space-y-4">
            <div>
                <label class="block text-gray-700 mb-2">帳號</label>
                <input type="text" id="username" required
                       class="w-full px-4 py-3 border rounded-xl focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                       placeholder="請輸入帳號">
            </div>
            <div>
                <label class="block text-gray-700 mb-2">密碼</label>
                <input type="password" id="password" required
                       class="w-full px-4 py-3 border rounded-xl focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                       placeholder="請輸入密碼">
            </div>
            
            <div class="flex justify-between items-center text-sm">
                <label class="flex items-center">
                    <input type="checkbox" id="remember" class="mr-2">
                    <span class="text-gray-600">記住我</span>
                </label>
                <a href="/forgot-password" class="text-purple-600 hover:underline">忘記密碼？</a>
            </div>
            
            <button type="submit" 
                    class="w-full gradient-bg text-white py-3 rounded-xl font-bold hover:opacity-90 transition">
                登入
            </button>
        </form>
        
        <div class="mt-6 text-center text-gray-600">
            還沒有帳號？ <a href="/register" class="text-purple-600 font-bold hover:underline">立即註冊</a>
        </div>
        
        <div id="message" class="mt-4 p-3 rounded-xl text-center hidden"></div>
    </div>
    
    <script>
        document.getElementById('login-form').addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const username = document.getElementById('username').value;
            const password = document.getElementById('password').value;
            const msgEl = document.getElementById('message');
            
            try {
                const res = await fetch('/api/auth/login', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({ username, password })
                });
                
                const data = await res.json();
                
                if (data.success || data.access_token) {
                    // 儲存 Token
                    localStorage.setItem('token', data.access_token || data.token);
                    localStorage.setItem('user', JSON.stringify(data.user || {username}));
                    
                    msgEl.className = 'mt-4 p-3 rounded-xl text-center bg-green-100 text-green-700';
                    msgEl.textContent = '登入成功！正在跳轉...';
                    msgEl.classList.remove('hidden');
                    
                    setTimeout(() => window.location.href = '/dashboard', 1000);
                } else {
                    msgEl.className = 'mt-4 p-3 rounded-xl text-center bg-red-100 text-red-700';
                    msgEl.textContent = data.detail || data.message || '登入失敗';
                    msgEl.classList.remove('hidden');
                }
            } catch (e) {
                msgEl.className = 'mt-4 p-3 rounded-xl text-center bg-red-100 text-red-700';
                msgEl.textContent = '連線失敗，請稍後再試';
                msgEl.classList.remove('hidden');
            }
        });
    </script>
</body>
</html>'''


# === 註冊頁面 ===
REGISTER_PAGE = '''<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>註冊 - 北斗命數</title>
    ''' + BASE_STYLE + '''
</head>
<body class="gradient-bg min-h-screen flex items-center justify-center p-4">
    <div class="card p-8 w-full max-w-md">
        <div class="text-center mb-8">
            <h1 class="text-3xl font-bold text-gray-800">🌟 北斗命數</h1>
            <p class="text-gray-600 mt-2">建立您的帳號</p>
        </div>
        
        <form id="register-form" class="space-y-4">
            <div>
                <label class="block text-gray-700 mb-2">帳號</label>
                <input type="text" id="username" required minlength="3"
                       class="w-full px-4 py-3 border rounded-xl focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                       placeholder="至少 3 個字符">
            </div>
            <div>
                <label class="block text-gray-700 mb-2">Email</label>
                <input type="email" id="email" required
                       class="w-full px-4 py-3 border rounded-xl focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                       placeholder="用於密碼重設">
            </div>
            <div>
                <label class="block text-gray-700 mb-2">密碼</label>
                <input type="password" id="password" required minlength="6"
                       class="w-full px-4 py-3 border rounded-xl focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                       placeholder="至少 6 個字符">
            </div>
            <div>
                <label class="block text-gray-700 mb-2">確認密碼</label>
                <input type="password" id="confirm" required
                       class="w-full px-4 py-3 border rounded-xl focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                       placeholder="再次輸入密碼">
            </div>
            
            <label class="flex items-start text-sm">
                <input type="checkbox" id="agree" required class="mt-1 mr-2">
                <span class="text-gray-600">
                    我同意 <a href="/legal/terms" class="text-purple-600 hover:underline">服務條款</a> 
                    和 <a href="/legal/privacy" class="text-purple-600 hover:underline">隱私政策</a>
                </span>
            </label>
            
            <button type="submit" 
                    class="w-full gradient-bg text-white py-3 rounded-xl font-bold hover:opacity-90 transition">
                註冊
            </button>
        </form>
        
        <div class="mt-6 text-center text-gray-600">
            已有帳號？ <a href="/login" class="text-purple-600 font-bold hover:underline">立即登入</a>
        </div>
        
        <div id="message" class="mt-4 p-3 rounded-xl text-center hidden"></div>
    </div>
    
    <script>
        document.getElementById('register-form').addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const username = document.getElementById('username').value;
            const email = document.getElementById('email').value;
            const password = document.getElementById('password').value;
            const confirm = document.getElementById('confirm').value;
            const msgEl = document.getElementById('message');
            
            if (password !== confirm) {
                msgEl.className = 'mt-4 p-3 rounded-xl text-center bg-red-100 text-red-700';
                msgEl.textContent = '兩次輸入的密碼不一致';
                msgEl.classList.remove('hidden');
                return;
            }
            
            try {
                const res = await fetch('/api/auth/register', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({ username, email, password })
                });
                
                const data = await res.json();
                
                if (data.success) {
                    msgEl.className = 'mt-4 p-3 rounded-xl text-center bg-green-100 text-green-700';
                    msgEl.textContent = '註冊成功！正在跳轉至登入頁...';
                    msgEl.classList.remove('hidden');
                    
                    setTimeout(() => window.location.href = '/login', 1500);
                } else {
                    msgEl.className = 'mt-4 p-3 rounded-xl text-center bg-red-100 text-red-700';
                    msgEl.textContent = data.detail || data.message || '註冊失敗';
                    msgEl.classList.remove('hidden');
                }
            } catch (e) {
                msgEl.className = 'mt-4 p-3 rounded-xl text-center bg-red-100 text-red-700';
                msgEl.textContent = '連線失敗，請稍後再試';
                msgEl.classList.remove('hidden');
            }
        });
    </script>
</body>
</html>'''


# === 忘記密碼頁面 ===
FORGOT_PASSWORD_PAGE = '''<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>忘記密碼 - 北斗命數</title>
    ''' + BASE_STYLE + '''
</head>
<body class="gradient-bg min-h-screen flex items-center justify-center p-4">
    <div class="card p-8 w-full max-w-md">
        <div class="text-center mb-8">
            <h1 class="text-3xl font-bold text-gray-800">🔑 忘記密碼</h1>
            <p class="text-gray-600 mt-2">輸入您的 Email，我們將發送密碼重設連結</p>
        </div>
        
        <form id="forgot-form" class="space-y-4">
            <div>
                <label class="block text-gray-700 mb-2">Email</label>
                <input type="email" id="email" required
                       class="w-full px-4 py-3 border rounded-xl focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                       placeholder="請輸入註冊時的 Email">
            </div>
            
            <button type="submit" 
                    class="w-full gradient-bg text-white py-3 rounded-xl font-bold hover:opacity-90 transition">
                發送重設連結
            </button>
        </form>
        
        <div class="mt-6 text-center">
            <a href="/login" class="text-purple-600 hover:underline">← 返回登入</a>
        </div>
        
        <div id="message" class="mt-4 p-3 rounded-xl text-center hidden"></div>
        
        <div id="success" class="hidden text-center py-4">
            <div class="text-5xl mb-4">📧</div>
            <h2 class="text-xl font-bold text-gray-800 mb-2">郵件已發送</h2>
            <p class="text-gray-600">請檢查您的信箱，點擊連結重設密碼。</p>
            <p class="text-gray-500 text-sm mt-2">（連結 24 小時內有效）</p>
        </div>
    </div>
    
    <script>
        document.getElementById('forgot-form').addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const email = document.getElementById('email').value;
            const msgEl = document.getElementById('message');
            const formEl = document.getElementById('forgot-form');
            const successEl = document.getElementById('success');
            
            try {
                const res = await fetch('/api/auth/forgot-password', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({ email })
                });
                
                const data = await res.json();
                
                if (data.success) {
                    formEl.classList.add('hidden');
                    successEl.classList.remove('hidden');
                } else {
                    msgEl.className = 'mt-4 p-3 rounded-xl text-center bg-red-100 text-red-700';
                    msgEl.textContent = data.detail || '發送失敗';
                    msgEl.classList.remove('hidden');
                }
            } catch (e) {
                msgEl.className = 'mt-4 p-3 rounded-xl text-center bg-red-100 text-red-700';
                msgEl.textContent = '連線失敗，請稍後再試';
                msgEl.classList.remove('hidden');
            }
        });
    </script>
</body>
</html>'''


# === 重設密碼頁面 ===
RESET_PASSWORD_PAGE = '''<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>重設密碼 - 北斗命數</title>
    ''' + BASE_STYLE + '''
</head>
<body class="gradient-bg min-h-screen flex items-center justify-center p-4">
    <div class="card p-8 w-full max-w-md">
        <div class="text-center mb-6">
            <h1 class="text-3xl font-bold text-gray-800">🔐 重設密碼</h1>
        </div>
        
        <div id="loading" class="text-center py-8">
            <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-600 mx-auto"></div>
            <p class="mt-4 text-gray-600">驗證連結中...</p>
        </div>
        
        <div id="invalid" class="hidden text-center py-8">
            <div class="text-6xl mb-4">❌</div>
            <h2 class="text-xl font-bold text-red-600 mb-2">連結無效</h2>
            <p id="error-msg" class="text-gray-600 mb-6"></p>
            <a href="/forgot-password" class="text-purple-600 hover:underline">重新申請密碼重設</a>
        </div>
        
        <form id="reset-form" class="hidden space-y-4">
            <div>
                <label class="block text-gray-700 mb-2">新密碼</label>
                <input type="password" id="password" required minlength="6"
                       class="w-full px-4 py-3 border rounded-xl focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                       placeholder="至少 6 個字符">
            </div>
            <div>
                <label class="block text-gray-700 mb-2">確認密碼</label>
                <input type="password" id="confirm" required
                       class="w-full px-4 py-3 border rounded-xl focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                       placeholder="再次輸入新密碼">
            </div>
            <button type="submit" 
                    class="w-full gradient-bg text-white py-3 rounded-xl font-bold hover:opacity-90 transition">
                重設密碼
            </button>
        </form>
        
        <div id="success" class="hidden text-center py-8">
            <div class="text-6xl mb-4">✅</div>
            <h2 class="text-xl font-bold text-green-600 mb-2">密碼重設成功</h2>
            <p class="text-gray-600 mb-6">請使用新密碼登入</p>
            <a href="/login" class="block w-full gradient-bg text-white py-3 rounded-xl font-bold text-center hover:opacity-90">
                前往登入
            </a>
        </div>
    </div>
    
    <script>
        const token = new URLSearchParams(window.location.search).get('token');
        
        async function verifyToken() {
            if (!token) {
                showInvalid('缺少重設連結');
                return;
            }
            
            try {
                const res = await fetch(`/api/auth/reset-password/verify?token=${token}`);
                const data = await res.json();
                
                if (data.valid) {
                    document.getElementById('loading').classList.add('hidden');
                    document.getElementById('reset-form').classList.remove('hidden');
                } else {
                    showInvalid(data.message);
                }
            } catch (e) {
                showInvalid('驗證失敗，請稍後再試');
            }
        }
        
        function showInvalid(msg) {
            document.getElementById('loading').classList.add('hidden');
            document.getElementById('invalid').classList.remove('hidden');
            document.getElementById('error-msg').textContent = msg;
        }
        
        document.getElementById('reset-form').addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const password = document.getElementById('password').value;
            const confirm = document.getElementById('confirm').value;
            
            if (password !== confirm) {
                alert('兩次輸入的密碼不一致');
                return;
            }
            
            try {
                const res = await fetch('/api/auth/reset-password', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({ token, new_password: password })
                });
                
                const data = await res.json();
                
                if (data.success) {
                    document.getElementById('reset-form').classList.add('hidden');
                    document.getElementById('success').classList.remove('hidden');
                } else {
                    alert(data.detail || '重設失敗');
                }
            } catch (e) {
                alert('請求失敗，請稍後再試');
            }
        });
        
        verifyToken();
    </script>
</body>
</html>'''


# === 變更密碼頁面（需登入）===
CHANGE_PASSWORD_PAGE = '''<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>變更密碼 - 北斗命數</title>
    ''' + BASE_STYLE + '''
</head>
<body class="bg-gray-50 min-h-screen">
    <nav class="gradient-bg text-white p-4">
        <div class="container mx-auto flex justify-between items-center">
            <a href="/" class="text-xl font-bold">🌟 北斗命數</a>
            <a href="/dashboard" class="hover:underline">← 返回儀表板</a>
        </div>
    </nav>
    
    <div class="container mx-auto max-w-md p-4 mt-8">
        <div class="card p-8">
            <h1 class="text-2xl font-bold text-center mb-6">🔒 變更密碼</h1>
            
            <form id="change-form" class="space-y-4">
                <div>
                    <label class="block text-gray-700 mb-2">目前密碼</label>
                    <input type="password" id="old_password" required
                           class="w-full px-4 py-3 border rounded-xl focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                           placeholder="請輸入目前密碼">
                </div>
                <div>
                    <label class="block text-gray-700 mb-2">新密碼</label>
                    <input type="password" id="new_password" required minlength="6"
                           class="w-full px-4 py-3 border rounded-xl focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                           placeholder="至少 6 個字符">
                </div>
                <div>
                    <label class="block text-gray-700 mb-2">確認新密碼</label>
                    <input type="password" id="confirm" required
                           class="w-full px-4 py-3 border rounded-xl focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                           placeholder="再次輸入新密碼">
                </div>
                
                <button type="submit" 
                        class="w-full gradient-bg text-white py-3 rounded-xl font-bold hover:opacity-90 transition">
                    變更密碼
                </button>
            </form>
            
            <div id="message" class="mt-4 p-3 rounded-xl text-center hidden"></div>
        </div>
    </div>
    
    <script>
        // 檢查登入狀態
        const token = localStorage.getItem('token');
        if (!token) {
            window.location.href = '/login';
        }
        
        document.getElementById('change-form').addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const old_password = document.getElementById('old_password').value;
            const new_password = document.getElementById('new_password').value;
            const confirm = document.getElementById('confirm').value;
            const msgEl = document.getElementById('message');
            
            if (new_password !== confirm) {
                msgEl.className = 'mt-4 p-3 rounded-xl text-center bg-red-100 text-red-700';
                msgEl.textContent = '兩次輸入的密碼不一致';
                msgEl.classList.remove('hidden');
                return;
            }
            
            try {
                const res = await fetch('/api/auth/change-password', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': `Bearer ${token}`
                    },
                    body: JSON.stringify({ old_password, new_password })
                });
                
                const data = await res.json();
                
                if (data.success) {
                    msgEl.className = 'mt-4 p-3 rounded-xl text-center bg-green-100 text-green-700';
                    msgEl.textContent = '密碼變更成功！';
                    msgEl.classList.remove('hidden');
                    
                    // 清空表單
                    document.getElementById('change-form').reset();
                } else {
                    msgEl.className = 'mt-4 p-3 rounded-xl text-center bg-red-100 text-red-700';
                    msgEl.textContent = data.detail || '變更失敗';
                    msgEl.classList.remove('hidden');
                }
            } catch (e) {
                msgEl.className = 'mt-4 p-3 rounded-xl text-center bg-red-100 text-red-700';
                msgEl.textContent = '連線失敗，請稍後再試';
                msgEl.classList.remove('hidden');
            }
        });
    </script>
</body>
</html>'''


# === 路由 ===

@router.get("/login", response_class=HTMLResponse)
async def login_page():
    """登入頁面"""
    return LOGIN_PAGE

@router.get("/register", response_class=HTMLResponse)
async def register_page():
    """註冊頁面"""
    return REGISTER_PAGE

@router.get("/forgot-password", response_class=HTMLResponse)
async def forgot_password_page():
    """忘記密碼頁面"""
    return FORGOT_PASSWORD_PAGE

@router.get("/reset-password", response_class=HTMLResponse)
async def reset_password_page():
    """重設密碼頁面"""
    return RESET_PASSWORD_PAGE

@router.get("/change-password", response_class=HTMLResponse)
async def change_password_page():
    """變更密碼頁面"""
    return CHANGE_PASSWORD_PAGE


print("✓ 認證頁面已載入")
