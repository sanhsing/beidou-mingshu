"""
定價頁模組 (升級版)
M4.1-M4.6 | @璃語 | 2026-02-17
"""
from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter(tags=["pricing"])

PRICING_HTML = '''<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>定價方案 - 北斗命數</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        .gradient-bg { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); }
        .card-hover:hover { transform: translateY(-8px); box-shadow: 0 20px 40px rgba(0,0,0,0.1); }
    </style>
</head>
<body class="bg-gray-50">
    <nav class="gradient-bg text-white p-4 shadow-lg">
        <div class="max-w-6xl mx-auto flex justify-between items-center">
            <a href="/" class="text-2xl font-bold">🌟 北斗命數</a>
            <div class="space-x-4">
                <a href="/login" class="hover:text-purple-200">登入</a>
                <a href="/register" class="bg-white text-purple-700 px-4 py-2 rounded-lg">註冊</a>
            </div>
        </div>
    </nav>

    <main class="max-w-6xl mx-auto px-6 py-16">
        <div class="text-center mb-16">
            <h1 class="text-4xl font-bold text-gray-800 mb-4">選擇適合您的方案</h1>
            <p class="text-gray-600 text-lg">透明定價，無隱藏費用</p>
        </div>

        <!-- 訂閱方案 -->
        <div class="grid md:grid-cols-4 gap-6 mb-16">
            <!-- Tier 1 -->
            <div class="card-hover bg-white rounded-2xl p-6 shadow-lg border-2 border-gray-100 transition-all duration-300">
                <div class="text-center mb-6">
                    <span class="text-4xl">🌟</span>
                    <h3 class="text-xl font-bold text-gray-800 mt-2">基礎命盤</h3>
                    <div class="text-3xl font-bold text-purple-600 mt-2">NT$299</div>
                    <p class="text-gray-500 text-sm">單次購買</p>
                </div>
                <ul class="space-y-3 mb-6 text-sm">
                    <li class="flex items-center"><span class="text-green-500 mr-2">✓</span>八字四柱排盤</li>
                    <li class="flex items-center"><span class="text-green-500 mr-2">✓</span>五行分析</li>
                    <li class="flex items-center"><span class="text-green-500 mr-2">✓</span>日主性格解讀</li>
                    <li class="flex items-center"><span class="text-green-500 mr-2">✓</span>十神分析</li>
                    <li class="flex items-center"><span class="text-green-500 mr-2">✓</span>PDF 報告 (12頁)</li>
                    <li class="flex items-center text-gray-400"><span class="mr-2">✗</span>紫微斗數</li>
                    <li class="flex items-center text-gray-400"><span class="mr-2">✗</span>大運流年</li>
                </ul>
                <a href="/register" class="block w-full text-center bg-gray-100 text-gray-800 py-3 rounded-xl font-bold hover:bg-gray-200">選擇</a>
            </div>

            <!-- Tier 2 (推薦) -->
            <div class="card-hover bg-white rounded-2xl p-6 shadow-xl border-2 border-purple-500 transition-all duration-300 relative">
                <div class="absolute -top-3 left-1/2 -translate-x-1/2 gradient-bg text-white px-4 py-1 rounded-full text-sm font-bold">最受歡迎</div>
                <div class="text-center mb-6">
                    <span class="text-4xl">⭐</span>
                    <h3 class="text-xl font-bold text-gray-800 mt-2">完整命理</h3>
                    <div class="text-3xl font-bold text-purple-600 mt-2">NT$599</div>
                    <p class="text-gray-500 text-sm">單次購買</p>
                </div>
                <ul class="space-y-3 mb-6 text-sm">
                    <li class="flex items-center"><span class="text-green-500 mr-2">✓</span>包含基礎命盤全部</li>
                    <li class="flex items-center"><span class="text-green-500 mr-2">✓</span>紫微斗數排盤</li>
                    <li class="flex items-center"><span class="text-green-500 mr-2">✓</span>十年大運分析</li>
                    <li class="flex items-center"><span class="text-green-500 mr-2">✓</span>今年流年詳解</li>
                    <li class="flex items-center"><span class="text-green-500 mr-2">✓</span>事業/感情建議</li>
                    <li class="flex items-center"><span class="text-green-500 mr-2">✓</span>PDF 報告 (30頁)</li>
                    <li class="flex items-center"><span class="text-green-500 mr-2">✓</span>3次合婚配對</li>
                </ul>
                <a href="/register" class="block w-full text-center gradient-bg text-white py-3 rounded-xl font-bold hover:opacity-90">選擇</a>
            </div>

            <!-- Tier 3 -->
            <div class="card-hover bg-white rounded-2xl p-6 shadow-lg border-2 border-gray-100 transition-all duration-300">
                <div class="text-center mb-6">
                    <span class="text-4xl">💎</span>
                    <h3 class="text-xl font-bold text-gray-800 mt-2">尊榮會員</h3>
                    <div class="text-3xl font-bold text-purple-600 mt-2">NT$1,999</div>
                    <p class="text-gray-500 text-sm">年費會員</p>
                </div>
                <ul class="space-y-3 mb-6 text-sm">
                    <li class="flex items-center"><span class="text-green-500 mr-2">✓</span>包含完整命理全部</li>
                    <li class="flex items-center"><span class="text-green-500 mr-2">✓</span>每月運勢更新</li>
                    <li class="flex items-center"><span class="text-green-500 mr-2">✓</span>每年流年報告</li>
                    <li class="flex items-center"><span class="text-green-500 mr-2">✓</span>3次擇日服務</li>
                    <li class="flex items-center"><span class="text-green-500 mr-2">✓</span>1次命名分析</li>
                    <li class="flex items-center"><span class="text-green-500 mr-2">✓</span>無限合婚配對</li>
                    <li class="flex items-center"><span class="text-green-500 mr-2">✓</span>專屬客服</li>
                </ul>
                <a href="/register" class="block w-full text-center bg-purple-100 text-purple-700 py-3 rounded-xl font-bold hover:bg-purple-200">選擇</a>
            </div>

            <!-- Tier 4 -->
            <div class="card-hover bg-white rounded-2xl p-6 shadow-lg border-2 border-gray-100 transition-all duration-300">
                <div class="text-center mb-6">
                    <span class="text-4xl">👑</span>
                    <h3 class="text-xl font-bold text-gray-800 mt-2">家族方案</h3>
                    <div class="text-3xl font-bold text-purple-600 mt-2">NT$4,999</div>
                    <p class="text-gray-500 text-sm">年費 / 5人</p>
                </div>
                <ul class="space-y-3 mb-6 text-sm">
                    <li class="flex items-center"><span class="text-green-500 mr-2">✓</span>尊榮會員 × 5人</li>
                    <li class="flex items-center"><span class="text-green-500 mr-2">✓</span>家族關係分析</li>
                    <li class="flex items-center"><span class="text-green-500 mr-2">✓</span>家族運勢總覽</li>
                    <li class="flex items-center"><span class="text-green-500 mr-2">✓</span>12次擇日服務</li>
                    <li class="flex items-center"><span class="text-green-500 mr-2">✓</span>5次命名分析</li>
                    <li class="flex items-center"><span class="text-green-500 mr-2">✓</span>優先客服</li>
                    <li class="flex items-center"><span class="text-green-500 mr-2">✓</span>專屬顧問</li>
                </ul>
                <a href="/register" class="block w-full text-center bg-gray-100 text-gray-800 py-3 rounded-xl font-bold hover:bg-gray-200">選擇</a>
            </div>
        </div>

        <!-- 點數包 -->
        <div class="mb-16">
            <h2 class="text-2xl font-bold text-gray-800 text-center mb-8">💰 點數儲值</h2>
            <div class="grid md:grid-cols-4 gap-4">
                <div class="bg-white rounded-xl p-4 shadow text-center hover:shadow-lg transition">
                    <div class="text-2xl font-bold text-purple-600">100 點</div>
                    <div class="text-gray-600">NT$99</div>
                    <div class="text-xs text-gray-400 mt-1">$0.99/點</div>
                </div>
                <div class="bg-white rounded-xl p-4 shadow text-center hover:shadow-lg transition">
                    <div class="text-2xl font-bold text-purple-600">300 點</div>
                    <div class="text-gray-600">NT$249</div>
                    <div class="text-xs text-green-500 mt-1">省 16%</div>
                </div>
                <div class="bg-white rounded-xl p-4 shadow text-center hover:shadow-lg transition border-2 border-purple-300">
                    <div class="text-2xl font-bold text-purple-600">500 點</div>
                    <div class="text-gray-600">NT$399</div>
                    <div class="text-xs text-green-500 mt-1">省 20%</div>
                </div>
                <div class="bg-white rounded-xl p-4 shadow text-center hover:shadow-lg transition">
                    <div class="text-2xl font-bold text-purple-600">1000 點</div>
                    <div class="text-gray-600">NT$699</div>
                    <div class="text-xs text-green-500 mt-1">省 30%</div>
                </div>
            </div>
        </div>

        <!-- 單項服務 -->
        <div class="mb-16">
            <h2 class="text-2xl font-bold text-gray-800 text-center mb-8">📋 單項服務價目</h2>
            <div class="bg-white rounded-2xl shadow-lg overflow-hidden">
                <table class="w-full">
                    <thead class="bg-purple-50">
                        <tr>
                            <th class="px-6 py-4 text-left text-gray-700">服務項目</th>
                            <th class="px-6 py-4 text-center text-gray-700">點數</th>
                            <th class="px-6 py-4 text-center text-gray-700">約 NT$</th>
                            <th class="px-6 py-4 text-left text-gray-700">說明</th>
                        </tr>
                    </thead>
                    <tbody class="divide-y">
                        <tr class="hover:bg-gray-50">
                            <td class="px-6 py-4">八字基礎分析</td>
                            <td class="px-6 py-4 text-center font-bold text-purple-600">50</td>
                            <td class="px-6 py-4 text-center">$50</td>
                            <td class="px-6 py-4 text-gray-500">四柱+五行+日主</td>
                        </tr>
                        <tr class="hover:bg-gray-50">
                            <td class="px-6 py-4">紫微排盤</td>
                            <td class="px-6 py-4 text-center font-bold text-purple-600">80</td>
                            <td class="px-6 py-4 text-center">$80</td>
                            <td class="px-6 py-4 text-gray-500">12宮+主星配置</td>
                        </tr>
                        <tr class="hover:bg-gray-50">
                            <td class="px-6 py-4">流年運勢</td>
                            <td class="px-6 py-4 text-center font-bold text-purple-600">60</td>
                            <td class="px-6 py-4 text-center">$60</td>
                            <td class="px-6 py-4 text-gray-500">當年運勢詳解</td>
                        </tr>
                        <tr class="hover:bg-gray-50">
                            <td class="px-6 py-4">合婚配對</td>
                            <td class="px-6 py-4 text-center font-bold text-purple-600">100</td>
                            <td class="px-6 py-4 text-center">$100</td>
                            <td class="px-6 py-4 text-gray-500">雙方八字合盤</td>
                        </tr>
                        <tr class="hover:bg-gray-50">
                            <td class="px-6 py-4">嫁娶擇日</td>
                            <td class="px-6 py-4 text-center font-bold text-purple-600">150</td>
                            <td class="px-6 py-4 text-center">$150</td>
                            <td class="px-6 py-4 text-gray-500">含30天候選日期</td>
                        </tr>
                        <tr class="hover:bg-gray-50">
                            <td class="px-6 py-4">寶寶命名</td>
                            <td class="px-6 py-4 text-center font-bold text-purple-600">200</td>
                            <td class="px-6 py-4 text-center">$200</td>
                            <td class="px-6 py-4 text-gray-500">10個推薦名字</td>
                        </tr>
                        <tr class="hover:bg-gray-50 bg-purple-50">
                            <td class="px-6 py-4 font-bold">完整命理報告</td>
                            <td class="px-6 py-4 text-center font-bold text-purple-600">300</td>
                            <td class="px-6 py-4 text-center">$300</td>
                            <td class="px-6 py-4 text-gray-500">PDF 30頁完整報告</td>
                        </tr>
                    </tbody>
                </table>
            </div>
        </div>

        <!-- FAQ -->
        <div>
            <h2 class="text-2xl font-bold text-gray-800 text-center mb-8">❓ 定價常見問題</h2>
            <div class="space-y-4 max-w-3xl mx-auto">
                <details class="bg-white rounded-xl p-4 shadow">
                    <summary class="font-bold cursor-pointer">點數會過期嗎？</summary>
                    <p class="text-gray-600 mt-2">購買的點數永久有效，不會過期。</p>
                </details>
                <details class="bg-white rounded-xl p-4 shadow">
                    <summary class="font-bold cursor-pointer">訂閱可以退款嗎？</summary>
                    <p class="text-gray-600 mt-2">訂閱可隨時取消，取消後當期仍有效至到期日，不提供退款。</p>
                </details>
                <details class="bg-white rounded-xl p-4 shadow">
                    <summary class="font-bold cursor-pointer">支援哪些付款方式？</summary>
                    <p class="text-gray-600 mt-2">支援信用卡、ATM轉帳、超商代碼繳費。</p>
                </details>
            </div>
        </div>
    </main>

    <footer class="bg-gray-800 text-gray-400 text-center p-6 mt-12">
        <p>© 2026 北斗命數. All rights reserved.</p>
    </footer>
</body>
</html>'''

@router.get("/pricing", response_class=HTMLResponse)
async def pricing_page():
    """定價頁"""
    return PRICING_HTML
