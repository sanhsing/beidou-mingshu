"""
用戶設定頁
settings_page.py | @璃語 | 2026-02-17
PYLIB: user_settings_api, dashboard_v2
"""
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

router = APIRouter(tags=["settings"])

SETTINGS_HTML = '''<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>帳號設定 - 北斗命數</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>.gradient-bg { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); }</style>
</head>
<body class="bg-gray-50 min-h-screen">
    <nav class="gradient-bg text-white p-4 shadow-lg">
        <div class="max-w-4xl mx-auto flex justify-between items-center">
            <a href="/" class="text-2xl font-bold">🌟 北斗命數</a>
            <a href="/dashboard" class="hover:text-purple-200">← 返回儀表板</a>
        </div>
    </nav>

    <main class="max-w-2xl mx-auto px-6 py-8">
        <h1 class="text-3xl font-bold text-gray-800 text-center mb-8">⚙️ 帳號設定</h1>

        <!-- 個人資料 -->
        <div class="bg-white rounded-2xl shadow-xl p-6 mb-6">
            <h2 class="text-xl font-bold text-gray-800 mb-4">👤 個人資料</h2>
            <form id="profileForm" class="space-y-4">
                <div class="grid md:grid-cols-2 gap-4">
                    <div>
                        <label class="block text-gray-700 mb-1">暱稱</label>
                        <input type="text" name="nickname" id="nickname"
                               class="w-full border rounded-lg px-4 py-2 focus:ring-2 focus:ring-purple-300">
                    </div>
                    <div>
                        <label class="block text-gray-700 mb-1">Email</label>
                        <input type="email" name="email" id="email"
                               class="w-full border rounded-lg px-4 py-2 focus:ring-2 focus:ring-purple-300">
                    </div>
                </div>
                <div>
                    <label class="block text-gray-700 mb-1">手機</label>
                    <input type="tel" name="phone" id="phone"
                           class="w-full border rounded-lg px-4 py-2 focus:ring-2 focus:ring-purple-300">
                </div>
                <div class="grid grid-cols-4 gap-2">
                    <div>
                        <label class="block text-gray-700 mb-1">出生年</label>
                        <input type="number" name="birth_year" id="birth_year" min="1900" max="2026"
                               class="w-full border rounded-lg px-3 py-2">
                    </div>
                    <div>
                        <label class="block text-gray-700 mb-1">月</label>
                        <input type="number" name="birth_month" id="birth_month" min="1" max="12"
                               class="w-full border rounded-lg px-3 py-2">
                    </div>
                    <div>
                        <label class="block text-gray-700 mb-1">日</label>
                        <input type="number" name="birth_day" id="birth_day" min="1" max="31"
                               class="w-full border rounded-lg px-3 py-2">
                    </div>
                    <div>
                        <label class="block text-gray-700 mb-1">時</label>
                        <input type="number" name="birth_hour" id="birth_hour" min="0" max="23"
                               class="w-full border rounded-lg px-3 py-2">
                    </div>
                </div>
                <button type="submit" class="w-full gradient-bg text-white py-3 rounded-xl font-bold hover:opacity-90">
                    儲存變更
                </button>
            </form>
        </div>

        <!-- 修改密碼 -->
        <div class="bg-white rounded-2xl shadow-xl p-6 mb-6">
            <h2 class="text-xl font-bold text-gray-800 mb-4">🔐 修改密碼</h2>
            <form id="passwordForm" class="space-y-4">
                <div>
                    <label class="block text-gray-700 mb-1">目前密碼</label>
                    <input type="password" name="old_password" required
                           class="w-full border rounded-lg px-4 py-2 focus:ring-2 focus:ring-purple-300">
                </div>
                <div>
                    <label class="block text-gray-700 mb-1">新密碼</label>
                    <input type="password" name="new_password" required minlength="8"
                           class="w-full border rounded-lg px-4 py-2 focus:ring-2 focus:ring-purple-300">
                </div>
                <div>
                    <label class="block text-gray-700 mb-1">確認新密碼</label>
                    <input type="password" name="confirm_password" required
                           class="w-full border rounded-lg px-4 py-2 focus:ring-2 focus:ring-purple-300">
                </div>
                <button type="submit" class="w-full border-2 border-purple-600 text-purple-600 py-3 rounded-xl font-bold hover:bg-purple-50">
                    更新密碼
                </button>
            </form>
        </div>

        <!-- 通知偏好 -->
        <div class="bg-white rounded-2xl shadow-xl p-6 mb-6">
            <h2 class="text-xl font-bold text-gray-800 mb-4">🔔 通知偏好</h2>
            <form id="notifyForm" class="space-y-4">
                <label class="flex items-center justify-between py-2">
                    <span class="text-gray-700">行銷資訊郵件</span>
                    <input type="checkbox" name="email_marketing" class="w-5 h-5 text-purple-600">
                </label>
                <label class="flex items-center justify-between py-2">
                    <span class="text-gray-700">報告完成通知</span>
                    <input type="checkbox" name="email_report" checked class="w-5 h-5 text-purple-600">
                </label>
                <label class="flex items-center justify-between py-2">
                    <span class="text-gray-700">會員到期提醒</span>
                    <input type="checkbox" name="email_reminder" checked class="w-5 h-5 text-purple-600">
                </label>
                <button type="submit" class="w-full gradient-bg text-white py-3 rounded-xl font-bold hover:opacity-90">
                    儲存偏好
                </button>
            </form>
        </div>

        <!-- 危險區域 -->
        <div class="bg-red-50 rounded-2xl p-6">
            <h2 class="text-xl font-bold text-red-800 mb-4">⚠️ 危險區域</h2>
            <p class="text-red-600 mb-4">刪除帳號後，所有資料將無法復原。</p>
            <button onclick="confirmDelete()" class="border-2 border-red-500 text-red-500 px-6 py-2 rounded-lg font-bold hover:bg-red-50">
                刪除帳號
            </button>
        </div>
    </main>

    <script>
        // 載入個人資料
        fetch('/api/user/profile')
            .then(r => r.json())
            .then(data => {
                if (data.success) {
                    const p = data.profile;
                    document.getElementById('nickname').value = p.nickname || '';
                    document.getElementById('email').value = p.email || '';
                    document.getElementById('phone').value = p.phone || '';
                    document.getElementById('birth_year').value = p.birth_year || '';
                    document.getElementById('birth_month').value = p.birth_month || '';
                    document.getElementById('birth_day').value = p.birth_day || '';
                    document.getElementById('birth_hour').value = p.birth_hour || '';
                }
            });

        // 儲存個人資料
        document.getElementById('profileForm').onsubmit = async (e) => {
            e.preventDefault();
            const formData = new FormData(e.target);
            const data = Object.fromEntries(formData);
            
            const res = await fetch('/api/user/profile', {
                method: 'PUT',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(data)
            });
            
            const result = await res.json();
            alert(result.message || '已儲存');
        };

        // 修改密碼
        document.getElementById('passwordForm').onsubmit = async (e) => {
            e.preventDefault();
            const formData = new FormData(e.target);
            const data = Object.fromEntries(formData);
            
            const res = await fetch('/api/user/password', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(data)
            });
            
            const result = await res.json();
            alert(result.message || result.detail || '已更新');
        };

        // 通知偏好
        document.getElementById('notifyForm').onsubmit = async (e) => {
            e.preventDefault();
            const data = {
                email_marketing: e.target.email_marketing.checked,
                email_report: e.target.email_report.checked,
                email_reminder: e.target.email_reminder.checked,
                push_enabled: false
            };
            
            const res = await fetch('/api/user/notifications', {
                method: 'PUT',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(data)
            });
            
            const result = await res.json();
            alert(result.message || '已儲存');
        };

        // 刪除帳號
        function confirmDelete() {
            if (confirm('確定要刪除帳號嗎？此操作無法復原！')) {
                const password = prompt('請輸入密碼確認：');
                if (password) {
                    fetch('/api/user/account', {
                        method: 'DELETE',
                        headers: {'Content-Type': 'application/x-www-form-urlencoded'},
                        body: 'password=' + encodeURIComponent(password)
                    }).then(r => r.json()).then(result => {
                        alert(result.message || result.detail);
                        if (result.success) window.location = '/';
                    });
                }
            }
        }
    </script>
</body>
</html>'''

@router.get("/settings", response_class=HTMLResponse)
async def settings_page():
    """用戶設定頁面"""
    return SETTINGS_HTML
