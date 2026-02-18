"""
客服支援模組
contact_support.py | @澄書 @流祇 | 2026-02-18
PYLIB: email_service, db_unified

功能：
- 聯繫表單
- 工單系統
- Email 通知
"""
import sqlite3
import secrets
from datetime import datetime
from typing import Optional, List
from enum import Enum
from fastapi import APIRouter, Request, HTTPException, Form
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel, EmailStr

# === 配置 ===
DB_PATH = "beidou_unified.db"
SUPPORT_EMAIL = "support@beidou-mingshu.com"

router = APIRouter(tags=["support"])

# === 資料模型 ===
class TicketCategory(str, Enum):
    GENERAL = "general"          # 一般詢問
    TECHNICAL = "technical"      # 技術問題
    PAYMENT = "payment"          # 付款問題
    REPORT = "report"            # 報告問題
    ACCOUNT = "account"          # 帳戶問題
    REFUND = "refund"            # 退款申請
    SUGGESTION = "suggestion"    # 建議回饋
    OTHER = "other"              # 其他

class TicketStatus(str, Enum):
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    WAITING = "waiting"
    RESOLVED = "resolved"
    CLOSED = "closed"

class ContactFormRequest(BaseModel):
    name: str
    email: EmailStr
    category: TicketCategory = TicketCategory.GENERAL
    subject: str
    message: str

# === 資料庫初始化 ===
def init_support_tables():
    """初始化客服表"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS support_tickets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ticket_no TEXT UNIQUE NOT NULL,
            user_id INTEGER,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            category TEXT DEFAULT 'general',
            subject TEXT NOT NULL,
            message TEXT NOT NULL,
            status TEXT DEFAULT 'open',
            priority INTEGER DEFAULT 2,
            assigned_to TEXT,
            resolved_at TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES auth_users(id)
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS ticket_replies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ticket_id INTEGER NOT NULL,
            is_staff INTEGER DEFAULT 0,
            reply_by TEXT,
            message TEXT NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (ticket_id) REFERENCES support_tickets(id)
        )
    ''')
    
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_ticket_email ON support_tickets(email)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_ticket_status ON support_tickets(status)')
    
    conn.commit()
    conn.close()

# 初始化
init_support_tables()

# === 工具函數 ===
def generate_ticket_no() -> str:
    """生成工單編號"""
    timestamp = datetime.now().strftime("%Y%m%d")
    random_str = secrets.token_hex(3).upper()
    return f"TK{timestamp}{random_str}"

def send_ticket_notification(ticket_no: str, email: str, subject: str):
    """發送工單通知"""
    try:
        from email_service import EmailService
        
        service = EmailService()
        
        html = f'''
        <div style="max-width:600px;margin:0 auto;font-family:sans-serif;">
            <div style="background:linear-gradient(135deg,#667eea 0%,#764ba2 100%);padding:30px;text-align:center;">
                <h1 style="color:white;margin:0;">🌟 北斗命數</h1>
            </div>
            <div style="padding:30px;background:#f9fafb;">
                <h2 style="color:#1f2937;">已收到您的訊息</h2>
                <p style="color:#4b5563;">感謝您聯繫北斗命數客服，我們已收到您的訊息。</p>
                <div style="background:#fff;border:1px solid #e5e7eb;padding:20px;border-radius:8px;margin:20px 0;">
                    <p style="margin:0;color:#6b7280;font-size:14px;">工單編號</p>
                    <p style="margin:5px 0 15px;font-size:18px;font-weight:bold;color:#667eea;">{ticket_no}</p>
                    <p style="margin:0;color:#6b7280;font-size:14px;">主旨</p>
                    <p style="margin:5px 0;color:#1f2937;">{subject}</p>
                </div>
                <p style="color:#4b5563;">我們通常會在 1-2 個工作天內回覆您。</p>
                <p style="color:#6b7280;font-size:14px;">如有緊急問題，請直接來信至 {SUPPORT_EMAIL}</p>
            </div>
            <div style="padding:20px;text-align:center;color:#9ca3af;font-size:12px;">
                © 2026 北斗命數 | 此為系統自動發送，請勿回覆
            </div>
        </div>
        '''
        
        service._send(email, f'【北斗命數】已收到您的訊息 - {ticket_no}', html)
        
        # 同時通知客服
        staff_html = f'''
        <div style="font-family:sans-serif;padding:20px;">
            <h2>新工單通知</h2>
            <p><strong>工單編號：</strong>{ticket_no}</p>
            <p><strong>客戶信箱：</strong>{email}</p>
            <p><strong>主旨：</strong>{subject}</p>
            <p>請登入後台處理。</p>
        </div>
        '''
        service._send(SUPPORT_EMAIL, f'[新工單] {ticket_no} - {subject}', staff_html)
        
    except Exception as e:
        print(f"[Support] 通知發送失敗: {e}")

# === API 端點 ===
@router.post("/api/support/submit")
async def submit_ticket(req: ContactFormRequest, request: Request):
    """提交客服工單"""
    ticket_no = generate_ticket_no()
    
    # 嘗試獲取用戶 ID
    user_id = None
    try:
        from auth_jwt import get_user_id
        user_id = get_user_id(request)
    except:
        pass
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO support_tickets 
        (ticket_no, user_id, name, email, category, subject, message)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (ticket_no, user_id, req.name, req.email, req.category, req.subject, req.message))
    
    conn.commit()
    conn.close()
    
    # 發送通知
    send_ticket_notification(ticket_no, req.email, req.subject)
    
    return {
        "success": True,
        "ticket_no": ticket_no,
        "message": "感謝您的訊息，我們會盡快回覆"
    }

@router.get("/api/support/tickets")
async def my_tickets(request: Request, email: str = None):
    """查詢我的工單"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # 嘗試用登入用戶查詢
    user_id = None
    try:
        from auth_jwt import get_user_id
        user_id = get_user_id(request)
    except:
        pass
    
    if user_id:
        cursor.execute('''
            SELECT * FROM support_tickets 
            WHERE user_id = ? 
            ORDER BY created_at DESC
        ''', (user_id,))
    elif email:
        cursor.execute('''
            SELECT * FROM support_tickets 
            WHERE email = ? 
            ORDER BY created_at DESC
        ''', (email,))
    else:
        return {"tickets": []}
    
    tickets = [dict(row) for row in cursor.fetchall()]
    conn.close()
    
    return {"tickets": tickets}

@router.get("/api/support/ticket/{ticket_no}")
async def get_ticket(ticket_no: str):
    """查詢單一工單"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM support_tickets WHERE ticket_no = ?', (ticket_no,))
    ticket = cursor.fetchone()
    
    if not ticket:
        conn.close()
        raise HTTPException(status_code=404, detail="工單不存在")
    
    # 獲取回覆
    cursor.execute('''
        SELECT * FROM ticket_replies 
        WHERE ticket_id = ? 
        ORDER BY created_at ASC
    ''', (ticket['id'],))
    replies = [dict(row) for row in cursor.fetchall()]
    
    conn.close()
    
    return {
        "ticket": dict(ticket),
        "replies": replies
    }

# === 聯繫頁面 ===
@router.get("/contact", response_class=HTMLResponse)
async def contact_page():
    """聯繫我們頁面"""
    categories = [
        ("general", "一般詢問"),
        ("technical", "技術問題"),
        ("payment", "付款問題"),
        ("report", "報告問題"),
        ("account", "帳戶問題"),
        ("refund", "退款申請"),
        ("suggestion", "建議回饋"),
        ("other", "其他"),
    ]
    
    options_html = "\n".join([
        f'<option value="{cat}">{label}</option>' 
        for cat, label in categories
    ])
    
    return f'''<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>聯繫我們 - 北斗命數</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        .gradient-bg {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); }}
    </style>
</head>
<body class="bg-gray-50 min-h-screen">
    <nav class="gradient-bg text-white p-4 shadow-lg">
        <div class="max-w-4xl mx-auto flex justify-between items-center">
            <a href="/" class="text-2xl font-bold">🌟 北斗命數</a>
            <a href="/" class="hover:text-purple-200">← 返回首頁</a>
        </div>
    </nav>
    
    <main class="max-w-2xl mx-auto p-6 my-8">
        <div class="bg-white rounded-xl shadow-lg p-8">
            <h1 class="text-2xl font-bold text-gray-800 mb-2">聯繫我們</h1>
            <p class="text-gray-600 mb-6">有任何問題或建議？我們很樂意聽取您的意見。</p>
            
            <form id="contactForm" class="space-y-4">
                <div class="grid md:grid-cols-2 gap-4">
                    <div>
                        <label class="block text-sm font-medium text-gray-700 mb-1">姓名 *</label>
                        <input type="text" id="name" required
                               class="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent">
                    </div>
                    <div>
                        <label class="block text-sm font-medium text-gray-700 mb-1">Email *</label>
                        <input type="email" id="email" required
                               class="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent">
                    </div>
                </div>
                
                <div>
                    <label class="block text-sm font-medium text-gray-700 mb-1">問題類型</label>
                    <select id="category" 
                            class="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent">
                        {options_html}
                    </select>
                </div>
                
                <div>
                    <label class="block text-sm font-medium text-gray-700 mb-1">主旨 *</label>
                    <input type="text" id="subject" required
                           class="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent">
                </div>
                
                <div>
                    <label class="block text-sm font-medium text-gray-700 mb-1">訊息內容 *</label>
                    <textarea id="message" rows="5" required
                              class="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                              placeholder="請詳細描述您的問題或建議..."></textarea>
                </div>
                
                <button type="submit" 
                        class="w-full bg-purple-600 text-white py-3 rounded-lg hover:bg-purple-700 transition font-medium">
                    送出訊息
                </button>
            </form>
            
            <div id="successMessage" class="hidden mt-6 p-4 bg-green-50 border border-green-200 rounded-lg">
                <div class="flex items-center">
                    <span class="text-2xl mr-3">✅</span>
                    <div>
                        <p class="font-medium text-green-800">訊息已送出</p>
                        <p class="text-green-600 text-sm">工單編號：<span id="ticketNo" class="font-mono"></span></p>
                        <p class="text-green-600 text-sm">我們會盡快回覆您的 Email</p>
                    </div>
                </div>
            </div>
        </div>
        
        <!-- 常見問題連結 -->
        <div class="mt-6 text-center">
            <p class="text-gray-600">
                在送出前，您也可以先查看 
                <a href="/faq" class="text-purple-600 hover:underline">常見問題</a>
            </p>
        </div>
        
        <!-- 其他聯繫方式 -->
        <div class="mt-8 bg-white rounded-xl shadow p-6">
            <h2 class="font-bold text-gray-800 mb-4">其他聯繫方式</h2>
            <div class="grid md:grid-cols-2 gap-4 text-sm">
                <div class="flex items-center text-gray-600">
                    <span class="mr-2">📧</span>
                    <span>{SUPPORT_EMAIL}</span>
                </div>
                <div class="flex items-center text-gray-600">
                    <span class="mr-2">⏰</span>
                    <span>回覆時間：1-2 個工作天</span>
                </div>
            </div>
        </div>
    </main>
    
    <script>
        document.getElementById('contactForm').addEventListener('submit', async (e) => {{
            e.preventDefault();
            
            const data = {{
                name: document.getElementById('name').value,
                email: document.getElementById('email').value,
                category: document.getElementById('category').value,
                subject: document.getElementById('subject').value,
                message: document.getElementById('message').value
            }};
            
            try {{
                const res = await fetch('/api/support/submit', {{
                    method: 'POST',
                    headers: {{'Content-Type': 'application/json'}},
                    body: JSON.stringify(data)
                }});
                
                const result = await res.json();
                
                if (result.success) {{
                    document.getElementById('contactForm').classList.add('hidden');
                    document.getElementById('successMessage').classList.remove('hidden');
                    document.getElementById('ticketNo').textContent = result.ticket_no;
                }} else {{
                    alert('送出失敗，請稍後再試');
                }}
            }} catch (err) {{
                alert('送出失敗，請稍後再試');
            }}
        }});
    </script>
</body>
</html>'''

# === 工單查詢頁面 ===
@router.get("/support/track", response_class=HTMLResponse)
async def track_ticket_page():
    """工單查詢頁面"""
    return '''<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>工單查詢 - 北斗命數</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        .gradient-bg { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); }
    </style>
</head>
<body class="bg-gray-50 min-h-screen">
    <nav class="gradient-bg text-white p-4 shadow-lg">
        <div class="max-w-4xl mx-auto flex justify-between items-center">
            <a href="/" class="text-2xl font-bold">🌟 北斗命數</a>
            <a href="/contact" class="hover:text-purple-200">聯繫客服</a>
        </div>
    </nav>
    
    <main class="max-w-xl mx-auto p-6 my-8">
        <div class="bg-white rounded-xl shadow-lg p-8">
            <h1 class="text-2xl font-bold text-gray-800 mb-6">工單查詢</h1>
            
            <div class="space-y-4">
                <div>
                    <label class="block text-sm font-medium text-gray-700 mb-1">工單編號</label>
                    <input type="text" id="ticketNo" placeholder="例如：TK20260218ABC123"
                           class="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-purple-500">
                </div>
                <button onclick="trackTicket()" 
                        class="w-full bg-purple-600 text-white py-2 rounded-lg hover:bg-purple-700">
                    查詢
                </button>
            </div>
            
            <div id="result" class="mt-6 hidden">
                <div id="ticketInfo" class="border rounded-lg p-4"></div>
            </div>
        </div>
    </main>
    
    <script>
        async function trackTicket() {
            const ticketNo = document.getElementById('ticketNo').value.trim();
            if (!ticketNo) return alert('請輸入工單編號');
            
            try {
                const res = await fetch(`/api/support/ticket/${ticketNo}`);
                if (!res.ok) {
                    alert('找不到此工單');
                    return;
                }
                
                const data = await res.json();
                const ticket = data.ticket;
                
                const statusMap = {
                    'open': '待處理',
                    'in_progress': '處理中',
                    'waiting': '等待回覆',
                    'resolved': '已解決',
                    'closed': '已關閉'
                };
                
                const statusColor = {
                    'open': 'bg-yellow-100 text-yellow-800',
                    'in_progress': 'bg-blue-100 text-blue-800',
                    'waiting': 'bg-orange-100 text-orange-800',
                    'resolved': 'bg-green-100 text-green-800',
                    'closed': 'bg-gray-100 text-gray-800'
                };
                
                document.getElementById('ticketInfo').innerHTML = `
                    <div class="space-y-3">
                        <div class="flex justify-between items-center">
                            <span class="font-mono text-purple-600">${ticket.ticket_no}</span>
                            <span class="px-2 py-1 rounded text-sm ${statusColor[ticket.status]}">${statusMap[ticket.status]}</span>
                        </div>
                        <div>
                            <p class="text-sm text-gray-500">主旨</p>
                            <p class="font-medium">${ticket.subject}</p>
                        </div>
                        <div>
                            <p class="text-sm text-gray-500">提交時間</p>
                            <p>${new Date(ticket.created_at).toLocaleString('zh-TW')}</p>
                        </div>
                        ${data.replies.length > 0 ? `
                            <div class="border-t pt-3 mt-3">
                                <p class="text-sm text-gray-500 mb-2">回覆記錄</p>
                                ${data.replies.map(r => `
                                    <div class="bg-gray-50 p-3 rounded mb-2">
                                        <p class="text-sm text-gray-500">${r.is_staff ? '客服回覆' : '您的回覆'} - ${new Date(r.created_at).toLocaleString('zh-TW')}</p>
                                        <p class="mt-1">${r.message}</p>
                                    </div>
                                `).join('')}
                            </div>
                        ` : ''}
                    </div>
                `;
                
                document.getElementById('result').classList.remove('hidden');
            } catch (err) {
                alert('查詢失敗，請稍後再試');
            }
        }
    </script>
</body>
</html>'''

print("✓ 客服支援模組已載入")
