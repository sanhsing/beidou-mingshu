"""
關於我們頁
about_page.py | @澄韻 @璃語 | 2026-02-18
"""
from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter()

@router.get("/about", response_class=HTMLResponse)
async def about_page():
    return '''<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>關於我們 - 北斗命數</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://unpkg.com/aos@2.3.1/dist/aos.css" rel="stylesheet">
    <style>
        .gradient-bg { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); }
        .text-gradient { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
    </style>
</head>
<body class="bg-gray-50">
    <!-- 導航 -->
    <nav class="gradient-bg text-white p-4 shadow-lg">
        <div class="max-w-6xl mx-auto flex justify-between items-center">
            <a href="/" class="text-2xl font-bold">🌟 北斗命數</a>
            <div class="flex gap-6">
                <a href="/" class="hover:text-purple-200">首頁</a>
                <a href="/pricing" class="hover:text-purple-200">定價</a>
                <a href="/contact" class="hover:text-purple-200">聯繫</a>
            </div>
        </div>
    </nav>

    <!-- Hero -->
    <section class="gradient-bg text-white py-20 text-center">
        <div class="max-w-4xl mx-auto px-6">
            <h1 class="text-4xl md:text-5xl font-bold mb-6">關於北斗命數</h1>
            <p class="text-xl text-purple-100">古典智慧 × 現代決策 × AI 分析</p>
            <p class="text-2xl font-medium mt-4">這不是算命，是決策分析系統</p>
        </div>
    </section>

    <!-- 開發者聲明 -->
    <section class="py-16 px-6" data-aos="fade-up">
        <div class="max-w-4xl mx-auto">
            <div class="bg-white rounded-2xl shadow-xl p-8 border-l-4 border-purple-500">
                <h2 class="text-2xl font-bold text-gray-800 mb-6">📜 開發者聲明</h2>
                <div class="space-y-4 text-gray-600 leading-relaxed">
                    <p>
                        北斗命數是一套「<strong class="text-purple-600">基於古典智慧的個人決策分析系統</strong>」，
                        而非傳統意義上的命理預測或算命服務。
                    </p>
                    <p>
                        所有計算方法皆源自古代典籍原典 ——《淵海子平》《三命通會》《紫微斗數全書》《梅花易數》等，
                        每項分析皆附<strong>原文引用</strong>與<strong>白話詳解</strong>，讓您「知其然，更知其所以然」。
                    </p>
                    <p>
                        我們在傳統術數基礎上，導入現代決策科學方法：<strong>場論框架</strong>、<strong>SWOT 模型</strong>、<strong>AI 深度分析</strong>，
                        三者融合，產出可執行的個人決策建議。
                    </p>
                    <div class="bg-purple-50 rounded-lg p-4 mt-6">
                        <p class="text-purple-800 font-medium text-center">
                            「您的命運，由您決定。我們只是提供另一個視角。」
                        </p>
                    </div>
                </div>
            </div>
        </div>
    </section>

    <!-- 三大特色 -->
    <section class="py-16 px-6 bg-white" data-aos="fade-up">
        <div class="max-w-5xl mx-auto">
            <h2 class="text-3xl font-bold text-center mb-12 text-gradient">核心特色</h2>
            <div class="grid md:grid-cols-3 gap-8">
                <!-- 古典根基 -->
                <div class="bg-gray-50 rounded-2xl p-8 border-t-4 border-purple-500">
                    <div class="text-4xl mb-4">📜</div>
                    <h3 class="text-xl font-bold text-gray-800 mb-3">古典根基</h3>
                    <p class="text-gray-600 mb-4">100% 源自古代典籍原典</p>
                    <ul class="text-sm text-gray-500 space-y-2">
                        <li>✓ 《淵海子平》《三命通會》</li>
                        <li>✓ 《紫微斗數全書》</li>
                        <li>✓ 《梅花易數》《奇門遁甲》</li>
                        <li>✓ 《協紀辨方書》《象吉通書》</li>
                    </ul>
                    <p class="text-purple-600 font-medium mt-4 text-sm">
                        每項分析附原文與白話詳解
                    </p>
                </div>
                
                <!-- 現代方法 -->
                <div class="bg-gray-50 rounded-2xl p-8 border-t-4 border-blue-500">
                    <div class="text-4xl mb-4">🧠</div>
                    <h3 class="text-xl font-bold text-gray-800 mb-3">現代方法</h3>
                    <p class="text-gray-600 mb-4">導入決策科學框架</p>
                    <ul class="text-sm text-gray-500 space-y-2">
                        <li>✓ <strong>場論框架</strong>：時空動態分析</li>
                        <li>✓ <strong>SWOT 模型</strong>：優劣勢評估</li>
                        <li>✓ <strong>AI 分析</strong>：多維度交叉驗證</li>
                        <li>✓ <strong>情境模擬</strong>：決策推演</li>
                    </ul>
                    <p class="text-blue-600 font-medium mt-4 text-sm">
                        古典智慧 × 現代決策 × AI 統合
                    </p>
                </div>
                
                <!-- 隱私優先 -->
                <div class="bg-gray-50 rounded-2xl p-8 border-t-4 border-green-500">
                    <div class="text-4xl mb-4">🔒</div>
                    <h3 class="text-xl font-bold text-gray-800 mb-3">隱私優先</h3>
                    <p class="text-gray-600 mb-4">您的資料，絕對安全</p>
                    <ul class="text-sm text-gray-500 space-y-2">
                        <li>✓ <strong>計算即焚</strong>：資料即時刪除</li>
                        <li>✓ <strong>零廣告</strong>：純淨無干擾</li>
                        <li>✓ <strong>絕不外流</strong>：不分享第三方</li>
                        <li>✓ <strong>隨時刪除</strong>：您有完全主權</li>
                    </ul>
                    <p class="text-green-600 font-medium mt-4 text-sm">
                        我們不需要您的數據，只需要您的信任
                    </p>
                </div>
            </div>
        </div>
    </section>

    <!-- 與傳統差異 -->
    <section class="py-16 px-6" data-aos="fade-up">
        <div class="max-w-4xl mx-auto">
            <h2 class="text-3xl font-bold text-center mb-12 text-gradient">與傳統命理的差異</h2>
            <div class="bg-white rounded-2xl shadow-xl overflow-hidden">
                <table class="w-full">
                    <thead class="bg-purple-600 text-white">
                        <tr>
                            <th class="py-4 px-6 text-left">維度</th>
                            <th class="py-4 px-6 text-center">傳統命理</th>
                            <th class="py-4 px-6 text-center">北斗命數</th>
                        </tr>
                    </thead>
                    <tbody class="divide-y">
                        <tr>
                            <td class="py-4 px-6 font-medium">算法來源</td>
                            <td class="py-4 px-6 text-center text-gray-500">口傳心授，難以驗證</td>
                            <td class="py-4 px-6 text-center text-purple-600 font-medium">典籍原文，可查可考 ✓</td>
                        </tr>
                        <tr class="bg-gray-50">
                            <td class="py-4 px-6 font-medium">解釋方式</td>
                            <td class="py-4 px-6 text-center text-gray-500">專業術語，門檻高</td>
                            <td class="py-4 px-6 text-center text-purple-600 font-medium">白話詳解，人人可懂 ✓</td>
                        </tr>
                        <tr>
                            <td class="py-4 px-6 font-medium">分析框架</td>
                            <td class="py-4 px-6 text-center text-gray-500">單一術數</td>
                            <td class="py-4 px-6 text-center text-purple-600 font-medium">6 大術數 + SWOT + AI ✓</td>
                        </tr>
                        <tr class="bg-gray-50">
                            <td class="py-4 px-6 font-medium">輸出結果</td>
                            <td class="py-4 px-6 text-center text-gray-500">吉凶斷言</td>
                            <td class="py-4 px-6 text-center text-purple-600 font-medium">決策建議 ✓</td>
                        </tr>
                        <tr>
                            <td class="py-4 px-6 font-medium">資料處理</td>
                            <td class="py-4 px-6 text-center text-gray-500">永久保存</td>
                            <td class="py-4 px-6 text-center text-purple-600 font-medium">計算即焚，零留存 ✓</td>
                        </tr>
                        <tr class="bg-gray-50">
                            <td class="py-4 px-6 font-medium">商業模式</td>
                            <td class="py-4 px-6 text-center text-gray-500">廣告、消災加購</td>
                            <td class="py-4 px-6 text-center text-purple-600 font-medium">純功能付費，無廣告 ✓</td>
                        </tr>
                    </tbody>
                </table>
            </div>
        </div>
    </section>

    <!-- 六大術數 -->
    <section class="py-16 px-6 bg-white" data-aos="fade-up">
        <div class="max-w-5xl mx-auto">
            <h2 class="text-3xl font-bold text-center mb-12 text-gradient">六大術數系統</h2>
            <div class="grid md:grid-cols-3 gap-6">
                <div class="bg-gray-50 rounded-xl p-6 text-center">
                    <div class="text-3xl mb-2">🎯</div>
                    <h3 class="font-bold">八字分析</h3>
                    <p class="text-sm text-gray-500 mt-2">《淵海子平》《三命通會》</p>
                </div>
                <div class="bg-gray-50 rounded-xl p-6 text-center">
                    <div class="text-3xl mb-2">⭐</div>
                    <h3 class="font-bold">紫微斗數</h3>
                    <p class="text-sm text-gray-500 mt-2">《紫微斗數全書》</p>
                </div>
                <div class="bg-gray-50 rounded-xl p-6 text-center">
                    <div class="text-3xl mb-2">🌸</div>
                    <h3 class="font-bold">梅花易數</h3>
                    <p class="text-sm text-gray-500 mt-2">《梅花易數》</p>
                </div>
                <div class="bg-gray-50 rounded-xl p-6 text-center">
                    <div class="text-3xl mb-2">🚪</div>
                    <h3 class="font-bold">奇門遁甲</h3>
                    <p class="text-sm text-gray-500 mt-2">《奇門遁甲秘笈大全》</p>
                </div>
                <div class="bg-gray-50 rounded-xl p-6 text-center">
                    <div class="text-3xl mb-2">📅</div>
                    <h3 class="font-bold">擇日系統</h3>
                    <p class="text-sm text-gray-500 mt-2">《協紀辨方書》《象吉通書》</p>
                </div>
                <div class="bg-gray-50 rounded-xl p-6 text-center">
                    <div class="text-3xl mb-2">✏️</div>
                    <h3 class="font-bold">命名系統</h3>
                    <p class="text-sm text-gray-500 mt-2">《康熙字典》《說文解字》</p>
                </div>
            </div>
        </div>
    </section>

    <!-- 開發者資訊 -->
    <section class="py-16 px-6" data-aos="fade-up">
        <div class="max-w-4xl mx-auto">
            <h2 class="text-3xl font-bold text-center mb-12 text-gradient">開發者資訊</h2>
            <div class="bg-white rounded-2xl shadow-xl p-8">
                <div class="grid md:grid-cols-2 gap-8">
                    <div>
                        <h3 class="font-bold text-lg mb-4 text-gray-800">🏢 公司資訊</h3>
                        <ul class="space-y-2 text-gray-600">
                            <li><strong>名稱：</strong>北斗七星數位文創工作室</li>
                            <li><strong>創辦人：</strong>北斗</li>
                            <li><strong>成立：</strong>2026 年</li>
                            <li><strong>地點：</strong>台灣</li>
                        </ul>
                    </div>
                    <div>
                        <h3 class="font-bold text-lg mb-4 text-gray-800">💻 技術架構</h3>
                        <ul class="space-y-2 text-gray-600">
                            <li><strong>後端：</strong>Python + FastAPI</li>
                            <li><strong>AI：</strong>Anthropic Claude</li>
                            <li><strong>算法：</strong>100% 古典典籍</li>
                            <li><strong>安全：</strong>計算即焚、零留存</li>
                        </ul>
                    </div>
                </div>
            </div>
        </div>
    </section>

    <!-- CTA -->
    <section class="py-16 px-6 gradient-bg text-white text-center">
        <div class="max-w-2xl mx-auto">
            <h2 class="text-3xl font-bold mb-4">準備好探索了嗎？</h2>
            <p class="text-purple-100 mb-8">開始您的決策分析之旅</p>
            <a href="/free-trial" class="inline-block bg-white text-purple-600 px-8 py-4 rounded-full font-bold hover:shadow-lg transition">
                免費試算 →
            </a>
        </div>
    </section>

    <!-- Footer -->
    <footer class="bg-gray-900 text-white py-12">
        <div class="max-w-6xl mx-auto px-6">
            <div class="grid md:grid-cols-4 gap-8">
                <div>
                    <h4 class="font-bold text-lg mb-4">🌟 北斗命數</h4>
                    <p class="text-gray-400 text-sm">古典智慧 × 現代決策 × AI 分析</p>
                </div>
                <div>
                    <h4 class="font-bold mb-4">服務</h4>
                    <ul class="space-y-2 text-gray-400 text-sm">
                        <li><a href="/free-trial" class="hover:text-white">免費試算</a></li>
                        <li><a href="/pricing" class="hover:text-white">定價方案</a></li>
                        <li><a href="/faq" class="hover:text-white">常見問題</a></li>
                    </ul>
                </div>
                <div>
                    <h4 class="font-bold mb-4">關於</h4>
                    <ul class="space-y-2 text-gray-400 text-sm">
                        <li><a href="/about" class="hover:text-white">關於我們</a></li>
                        <li><a href="/contact" class="hover:text-white">聯繫客服</a></li>
                        <li><a href="/api/privacy/statement" class="hover:text-white">隱私承諾</a></li>
                    </ul>
                </div>
                <div>
                    <h4 class="font-bold mb-4">法律</h4>
                    <ul class="space-y-2 text-gray-400 text-sm">
                        <li><a href="/legal/terms" class="hover:text-white">服務條款</a></li>
                        <li><a href="/legal/privacy" class="hover:text-white">隱私政策</a></li>
                        <li><a href="/legal/disclaimer" class="hover:text-white">免責聲明</a></li>
                    </ul>
                </div>
            </div>
            <div class="border-t border-gray-800 mt-8 pt-8 text-center text-gray-500 text-sm">
                <p>© 2026 北斗七星數位文創工作室. All rights reserved.</p>
                <p class="mt-2">我們不需要您的數據，只需要您的信任</p>
            </div>
        </div>
    </footer>

    <script src="https://unpkg.com/aos@2.3.1/dist/aos.js"></script>
    <script>AOS.init({duration: 800, once: true});</script>
</body>
</html>'''

print("✓ 關於頁路由已載入")
