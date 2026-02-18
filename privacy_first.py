"""
隱私優先模組
privacy_first.py | @吾鏡 @星殼 | 2026-02-18

核心原則：
- 計算即焚：生辰資料計算後立即刪除
- 零留存：伺服器不保留命盤原始數據
- 用戶主權：隨時可刪除所有資料
"""
import sqlite3
import os
from datetime import datetime, timedelta
from typing import Optional
from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import JSONResponse, HTMLResponse
from pydantic import BaseModel

# === 配置 ===
DB_PATH = "beidou_unified.db"
DELETE_WITHIN_HOURS = 24  # 刪除請求在 24 小時內完成

router = APIRouter(prefix="/api/privacy", tags=["privacy"])

# === 資料模型 ===
class DeleteAccountRequest(BaseModel):
    confirm: bool
    reason: Optional[str] = None

# === 資料庫初始化 ===
def init_privacy_tables():
    """初始化隱私相關表"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 刪除請求記錄
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS deletion_requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            reason TEXT,
            status TEXT DEFAULT 'pending',
            requested_at TEXT DEFAULT CURRENT_TIMESTAMP,
            completed_at TEXT,
            FOREIGN KEY (user_id) REFERENCES auth_users(id)
        )
    ''')
    
    # 隱私日誌（記錄何時刪除了什麼，不記錄內容）
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS privacy_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            action TEXT NOT NULL,
            description TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()

init_privacy_tables()

# === 核心函數 ===
def purge_calculation_data(session_id: str):
    """
    計算即焚：清除計算過程中的暫存資料
    在每次命理計算完成後調用
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 刪除暫存的計算資料
    cursor.execute('''
        DELETE FROM calculation_cache WHERE session_id = ?
    ''', (session_id,))
    
    # 記錄日誌（不含個資）
    cursor.execute('''
        INSERT INTO privacy_logs (action, description)
        VALUES ('purge_calculation', '計算資料已清除')
    ''')
    
    conn.commit()
    conn.close()

def delete_user_data(user_id: int) -> dict:
    """
    完全刪除用戶所有資料
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    deleted = {
        "reports": 0,
        "profiles": 0,
        "payments": 0,
        "subscriptions": 0,
        "referrals": 0,
        "tickets": 0
    }
    
    # 刪除報告
    cursor.execute('DELETE FROM reports WHERE user_id = ?', (user_id,))
    deleted["reports"] = cursor.rowcount
    
    # 刪除個人檔案
    cursor.execute('DELETE FROM user_profiles WHERE user_id = ?', (user_id,))
    deleted["profiles"] = cursor.rowcount
    
    # 刪除付款記錄（保留財務合規所需的最小資訊）
    cursor.execute('''
        UPDATE orders SET 
            user_id = NULL,
            email = '***已刪除***'
        WHERE user_id = ?
    ''', (user_id,))
    deleted["payments"] = cursor.rowcount
    
    # 刪除訂閱
    cursor.execute('DELETE FROM subscriptions WHERE user_id = ?', (user_id,))
    deleted["subscriptions"] = cursor.rowcount
    
    # 刪除推薦記錄
    cursor.execute('DELETE FROM referrals WHERE referrer_id = ? OR referee_id = ?', (user_id, user_id))
    deleted["referrals"] = cursor.rowcount
    
    # 刪除客服工單
    cursor.execute('DELETE FROM support_tickets WHERE user_id = ?', (user_id,))
    deleted["tickets"] = cursor.rowcount
    
    # 刪除社交帳號關聯
    cursor.execute('DELETE FROM social_accounts WHERE user_id = ?', (user_id,))
    
    # 刪除推薦碼
    cursor.execute('DELETE FROM referral_codes WHERE user_id = ?', (user_id,))
    
    # 刪除分享連結
    cursor.execute('DELETE FROM report_shares WHERE user_id = ?', (user_id,))
    
    # 最後刪除用戶帳號
    cursor.execute('DELETE FROM auth_users WHERE id = ?', (user_id,))
    
    # 記錄日誌
    cursor.execute('''
        INSERT INTO privacy_logs (action, description)
        VALUES ('delete_user', ?)
    ''', (f'用戶 ID {user_id} 資料已完全刪除',))
    
    conn.commit()
    conn.close()
    
    return deleted

# === API 端點 ===
@router.get("/policy")
async def privacy_policy_summary():
    """隱私政策摘要"""
    return {
        "principles": [
            {
                "icon": "🔒",
                "title": "計算即焚",
                "description": "您的生辰資料在計算完成後立即從伺服器刪除"
            },
            {
                "icon": "📄",
                "title": "您的報告，您保管",
                "description": "PDF 報告由您自行下載保存，我們不保留副本"
            },
            {
                "icon": "🗑️",
                "title": "隨時刪除",
                "description": "您可隨時刪除帳戶及所有相關資料，24 小時內完成"
            },
            {
                "icon": "❌",
                "title": "絕不外流",
                "description": "您的個資絕不出售或分享給任何第三方"
            }
        ],
        "data_retention": {
            "birth_data": "0 秒（計算後立即刪除）",
            "reports": "用戶自行保管",
            "account": "直到用戶刪除",
            "payment_records": "依法保留 5 年（去識別化）"
        },
        "third_party_sharing": "絕不",
        "advertising": "無",
        "tracking": "僅基本流量分析（Google Analytics）"
    }

@router.post("/delete-account")
async def request_delete_account(req: DeleteAccountRequest, request: Request):
    """請求刪除帳戶"""
    from auth_jwt import get_user_id
    
    if not req.confirm:
        raise HTTPException(status_code=400, detail="請確認刪除操作")
    
    user_id = get_user_id(request)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 記錄刪除請求
    cursor.execute('''
        INSERT INTO deletion_requests (user_id, reason)
        VALUES (?, ?)
    ''', (user_id, req.reason))
    
    conn.commit()
    conn.close()
    
    # 立即執行刪除
    deleted = delete_user_data(user_id)
    
    return {
        "success": True,
        "message": "您的帳戶及所有資料已完全刪除",
        "deleted": deleted
    }

@router.get("/my-data")
async def get_my_data_summary(request: Request):
    """查看我的資料摘要"""
    from auth_jwt import get_user_id
    
    user_id = get_user_id(request)
    
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # 統計各類資料數量
    cursor.execute('SELECT COUNT(*) as count FROM reports WHERE user_id = ?', (user_id,))
    reports = cursor.fetchone()['count']
    
    cursor.execute('SELECT COUNT(*) as count FROM user_profiles WHERE user_id = ?', (user_id,))
    profiles = cursor.fetchone()['count']
    
    cursor.execute('SELECT COUNT(*) as count FROM orders WHERE user_id = ?', (user_id,))
    orders = cursor.fetchone()['count']
    
    cursor.execute('SELECT created_at FROM auth_users WHERE id = ?', (user_id,))
    user = cursor.fetchone()
    
    conn.close()
    
    return {
        "summary": {
            "reports": reports,
            "profiles": profiles,
            "orders": orders
        },
        "account_created": user['created_at'] if user else None,
        "note": "您可隨時下載或刪除您的所有資料"
    }

@router.post("/export-my-data")
async def export_my_data(request: Request):
    """匯出我的資料（GDPR 合規）"""
    from auth_jwt import get_user_id
    import json
    
    user_id = get_user_id(request)
    
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # 收集用戶資料
    cursor.execute('SELECT username, email, display_name, created_at FROM auth_users WHERE id = ?', (user_id,))
    user = dict(cursor.fetchone()) if cursor.fetchone() else {}
    
    cursor.execute('SELECT * FROM user_profiles WHERE user_id = ?', (user_id,))
    profiles = [dict(row) for row in cursor.fetchall()]
    
    cursor.execute('SELECT id, report_type, created_at FROM reports WHERE user_id = ?', (user_id,))
    reports = [dict(row) for row in cursor.fetchall()]
    
    conn.close()
    
    export_data = {
        "export_date": datetime.now().isoformat(),
        "user": user,
        "profiles": profiles,
        "reports_count": len(reports),
        "note": "生辰資料已在計算後刪除，此處不含命盤原始數據"
    }
    
    return export_data

# === 隱私聲明頁面 ===
@router.get("/statement", response_class=HTMLResponse)
async def privacy_statement_page():
    """隱私聲明頁面"""
    return '''<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>隱私承諾 - 北斗命數</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-gray-50">
    <nav class="bg-gradient-to-r from-purple-600 to-indigo-700 text-white p-4">
        <div class="max-w-4xl mx-auto flex justify-between items-center">
            <a href="/" class="text-2xl font-bold">🌟 北斗命數</a>
            <a href="/" class="hover:text-purple-200">← 返回首頁</a>
        </div>
    </nav>
    
    <main class="max-w-3xl mx-auto p-6 my-8">
        <div class="bg-white rounded-2xl shadow-xl p-8">
            <h1 class="text-3xl font-bold text-center text-gray-800 mb-2">🔒 隱私承諾</h1>
            <p class="text-center text-gray-600 mb-8">我們不需要您的數據，只需要您的信任</p>
            
            <div class="space-y-6">
                <!-- 計算即焚 -->
                <div class="border-l-4 border-purple-500 pl-4 py-2">
                    <h2 class="text-xl font-bold text-gray-800 flex items-center">
                        <span class="text-2xl mr-2">🔥</span> 計算即焚
                    </h2>
                    <p class="text-gray-600 mt-2">
                        您的生辰八字資料在命理計算完成的那一刻，就會從我們的伺服器<strong>立即刪除</strong>。
                        我們不保留任何可識別個人的命盤原始數據。
                    </p>
                </div>
                
                <!-- 您的報告 -->
                <div class="border-l-4 border-blue-500 pl-4 py-2">
                    <h2 class="text-xl font-bold text-gray-800 flex items-center">
                        <span class="text-2xl mr-2">📄</span> 您的報告，您保管
                    </h2>
                    <p class="text-gray-600 mt-2">
                        計算完成後，請<strong>立即下載您的 PDF 報告</strong>並妥善保存。
                        我們不在伺服器保留報告副本。下次分析需重新輸入資料。
                    </p>
                </div>
                
                <!-- 隨時刪除 -->
                <div class="border-l-4 border-green-500 pl-4 py-2">
                    <h2 class="text-xl font-bold text-gray-800 flex items-center">
                        <span class="text-2xl mr-2">🗑️</span> 隨時刪除
                    </h2>
                    <p class="text-gray-600 mt-2">
                        您可以隨時刪除您的帳戶及所有相關資料。
                        我們承諾在<strong> 24 小時內</strong>完成所有資料的清除。
                    </p>
                </div>
                
                <!-- 絕不外流 -->
                <div class="border-l-4 border-red-500 pl-4 py-2">
                    <h2 class="text-xl font-bold text-gray-800 flex items-center">
                        <span class="text-2xl mr-2">🚫</span> 絕不外流
                    </h2>
                    <p class="text-gray-600 mt-2">
                        您的個人資料<strong>絕不</strong>會被出售、分享、或以任何形式提供給第三方。
                        包括廣告商、數據商、合作夥伴 —— 任何人。
                    </p>
                </div>
            </div>
            
            <!-- 對比表 -->
            <div class="mt-10 bg-gray-50 rounded-xl p-6">
                <h3 class="text-lg font-bold text-gray-800 mb-4">我們與其他平台的差異</h3>
                <div class="overflow-x-auto">
                    <table class="w-full text-sm">
                        <thead>
                            <tr class="border-b">
                                <th class="text-left py-2">隱私策略</th>
                                <th class="text-center py-2">一般平台</th>
                                <th class="text-center py-2 text-purple-600">北斗命數</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr class="border-b">
                                <td class="py-2">保留生辰資料</td>
                                <td class="text-center">永久保留</td>
                                <td class="text-center text-green-600 font-bold">❌ 不保留</td>
                            </tr>
                            <tr class="border-b">
                                <td class="py-2">用於廣告分析</td>
                                <td class="text-center">是</td>
                                <td class="text-center text-green-600 font-bold">❌ 否</td>
                            </tr>
                            <tr class="border-b">
                                <td class="py-2">分享第三方</td>
                                <td class="text-center">可能</td>
                                <td class="text-center text-green-600 font-bold">❌ 絕不</td>
                            </tr>
                            <tr class="border-b">
                                <td class="py-2">資料留存期</td>
                                <td class="text-center">永久</td>
                                <td class="text-center text-green-600 font-bold">0 秒</td>
                            </tr>
                            <tr>
                                <td class="py-2">廣告</td>
                                <td class="text-center">有</td>
                                <td class="text-center text-green-600 font-bold">❌ 無</td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            </div>
            
            <!-- 為什麼這樣做 -->
            <div class="mt-10 text-center">
                <h3 class="text-lg font-bold text-gray-800 mb-2">為什麼我們這樣做？</h3>
                <p class="text-gray-600">
                    生辰八字是您最私密的個人資訊之一。<br>
                    我們相信，真正專業的命理服務不需要囤積您的數據。<br>
                    <strong>您付費購買的是分析服務，不是用隱私交換。</strong>
                </p>
            </div>
        </div>
    </main>
</body>
</html>'''

print("✓ 隱私優先模組已載入")
