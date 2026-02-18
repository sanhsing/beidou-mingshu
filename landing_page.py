"""
落地頁模組
M2.1-M2.8 | @璃語 | 2026-02-17
"""
from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter(tags=["landing"])

LANDING_HTML = '''<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="description" content="北斗命數 - 專業八字紫微命理分析，AI驅動的智慧命理服務">
    <title>北斗命數 - 您的智慧命理顧問</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://unpkg.com/aos@2.3.1/dist/aos.css" rel="stylesheet">
    <style>
        .gradient-bg { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); }
        .gradient-text { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
        .feature-card:hover { transform: translateY(-5px); }
        .pulse-btn { animation: pulse 2s infinite; }
        @keyframes pulse { 0%, 100% { box-shadow: 0 0 0 0 rgba(102, 126, 234, 0.4); } 50% { box-shadow: 0 0 0 15px rgba(102, 126, 234, 0); } }
    </style>
</head>
<body class="bg-white">
    <!-- 娛樂聲明橫幅 -->
    <div class="bg-purple-100 text-purple-800 text-center py-2 text-sm">
        ⚠️ 本服務為娛樂參考性質，分析結果僅供自我探索之用。
        <a href="/legal/disclaimer" class="underline ml-2">了解更多</a>
    </div>
    
    <!-- 導航 -->
    <nav class="fixed w-full bg-white/95 backdrop-blur-sm shadow-sm z-50">
        <div class="max-w-6xl mx-auto px-6 py-4 flex justify-between items-center">
            <a href="/" class="text-2xl font-bold gradient-text">🌟 北斗命數</a>
            <div class="hidden md:flex space-x-6">
                <a href="#features" class="text-gray-600 hover:text-purple-600">功能</a>
                <a href="#pricing" class="text-gray-600 hover:text-purple-600">定價</a>
                <a href="#faq" class="text-gray-600 hover:text-purple-600">常見問題</a>
            </div>
            <div class="flex space-x-3">
                <a href="/login" class="text-purple-600 hover:text-purple-800 px-4 py-2">登入</a>
                <a href="/register" class="gradient-bg text-white px-5 py-2 rounded-lg hover:opacity-90">免費註冊</a>
            </div>
        </div>
    </nav>

    <!-- Hero -->
    <section class="gradient-bg min-h-screen flex items-center pt-20">
        <div class="max-w-6xl mx-auto px-6 py-20 grid md:grid-cols-2 gap-12 items-center">
            <div class="text-white" data-aos="fade-right">
                <h1 class="text-5xl md:text-6xl font-bold leading-tight mb-6">
                    解讀命運密碼<br>
                    <span class="text-yellow-300">掌握人生方向</span>
                </h1>
                <p class="text-xl text-purple-100 mb-8">
                    結合傳統命理智慧與現代AI技術<br>
                    為您提供專業、精準的八字紫微分析
                </p>
                <div class="flex flex-col sm:flex-row gap-4">
                    <a href="/free" class="pulse-btn bg-white text-purple-700 px-8 py-4 rounded-xl text-lg font-bold hover:bg-purple-50 text-center">
                        🔮 免費試算
                    </a>
                    <a href="/register" class="border-2 border-white text-white px-8 py-4 rounded-xl text-lg font-bold hover:bg-white/10 text-center">
                        註冊領 50 點 →
                    </a>
                </div>
                <p class="text-purple-200 mt-6 text-sm">✓ 無需信用卡 ✓ 3分鐘完成分析 ✓ 專業報告下載</p>
            </div>
            <div class="hidden md:block" data-aos="fade-left">
                <div class="bg-white/10 backdrop-blur-lg rounded-3xl p-8 text-white">
                    <div class="text-center mb-6">
                        <span class="text-6xl">🎴</span>
                        <h3 class="text-2xl font-bold mt-4">八字命盤示例</h3>
                    </div>
                    <div class="grid grid-cols-4 gap-3 text-center">
                        <div class="bg-white/20 rounded-lg p-3">
                            <div class="text-xs text-purple-200">年柱</div>
                            <div class="text-2xl font-bold">甲子</div>
                        </div>
                        <div class="bg-white/20 rounded-lg p-3">
                            <div class="text-xs text-purple-200">月柱</div>
                            <div class="text-2xl font-bold">丙寅</div>
                        </div>
                        <div class="bg-white/20 rounded-lg p-3">
                            <div class="text-xs text-purple-200">日柱</div>
                            <div class="text-2xl font-bold">戊辰</div>
                        </div>
                        <div class="bg-white/20 rounded-lg p-3">
                            <div class="text-xs text-purple-200">時柱</div>
                            <div class="text-2xl font-bold">壬午</div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </section>

    <!-- 功能介紹 -->
    <section id="features" class="py-24 bg-gray-50">
        <div class="max-w-6xl mx-auto px-6">
            <div class="text-center mb-16" data-aos="fade-up">
                <h2 class="text-4xl font-bold text-gray-800 mb-4">專業命理服務</h2>
                <p class="text-gray-600 text-lg">結合傳統智慧與現代技術，提供全方位的命理分析</p>
            </div>
            
            <div class="grid md:grid-cols-3 gap-8">
                <div class="feature-card bg-white rounded-2xl p-8 shadow-lg transition-all duration-300" data-aos="fade-up" data-aos-delay="100">
                    <div class="text-5xl mb-4">🎯</div>
                    <h3 class="text-xl font-bold text-gray-800 mb-3">八字精算</h3>
                    <p class="text-gray-600">精準計算您的八字四柱，分析五行強弱、十神配置，揭示性格特質與人生方向。</p>
                </div>
                
                <div class="feature-card bg-white rounded-2xl p-8 shadow-lg transition-all duration-300" data-aos="fade-up" data-aos-delay="200">
                    <div class="text-5xl mb-4">⭐</div>
                    <h3 class="text-xl font-bold text-gray-800 mb-3">紫微斗數</h3>
                    <p class="text-gray-600">完整排列紫微命盤，解讀十二宮位、主星配置，洞察事業、感情、財運走向。</p>
                </div>
                
                <div class="feature-card bg-white rounded-2xl p-8 shadow-lg transition-all duration-300" data-aos="fade-up" data-aos-delay="300">
                    <div class="text-5xl mb-4">📅</div>
                    <h3 class="text-xl font-bold text-gray-800 mb-3">擇日服務</h3>
                    <p class="text-gray-600">嫁娶、開市、動土、搬家，提供個人化的黃道吉日推薦，趨吉避凶。</p>
                </div>
                
                <div class="feature-card bg-white rounded-2xl p-8 shadow-lg transition-all duration-300" data-aos="fade-up" data-aos-delay="400">
                    <div class="text-5xl mb-4">✏️</div>
                    <h3 class="text-xl font-bold text-gray-800 mb-3">命名建議</h3>
                    <p class="text-gray-600">根據八字五行，結合姓名學原理，為您或寶寶推薦吉祥好名。</p>
                </div>
                
                <div class="feature-card bg-white rounded-2xl p-8 shadow-lg transition-all duration-300" data-aos="fade-up" data-aos-delay="500">
                    <div class="text-5xl mb-4">💑</div>
                    <h3 class="text-xl font-bold text-gray-800 mb-3">合婚配對</h3>
                    <p class="text-gray-600">雙方八字合盤分析，評估婚姻契合度，提供相處建議。</p>
                </div>
                
                <div class="feature-card bg-white rounded-2xl p-8 shadow-lg transition-all duration-300" data-aos="fade-up" data-aos-delay="600">
                    <div class="text-5xl mb-4">📊</div>
                    <h3 class="text-xl font-bold text-gray-800 mb-3">運勢分析</h3>
                    <p class="text-gray-600">大運、流年詳細解讀，掌握人生各階段的機遇與挑戰。</p>
                </div>
            </div>
        </div>
    </section>

    <!-- 為什麼選擇北斗命數 -->
    <section id="why-us" class="py-24 bg-gradient-to-b from-white to-purple-50">
        <div class="max-w-6xl mx-auto px-6">
            <div class="text-center mb-16" data-aos="fade-up">
                <h2 class="text-4xl font-bold text-gray-800 mb-4">為什麼選擇北斗命數？</h2>
                <p class="text-xl text-purple-600 font-medium">這不是算命，是決策分析系統</p>
            </div>
            
            <div class="grid md:grid-cols-3 gap-8 mb-16">
                <!-- 古典根基 -->
                <div class="bg-white rounded-2xl p-8 shadow-lg border-t-4 border-purple-500" data-aos="fade-up" data-aos-delay="100">
                    <div class="text-4xl mb-4">📜</div>
                    <h3 class="text-xl font-bold text-gray-800 mb-3">古典根基</h3>
                    <p class="text-gray-600 mb-4">所有計算皆源自古代典籍原典算法</p>
                    <ul class="text-sm text-gray-500 space-y-1">
                        <li>• 《淵海子平》《三命通會》</li>
                        <li>• 《紫微斗數全書》</li>
                        <li>• 《梅花易數》《奇門遁甲》</li>
                    </ul>
                    <p class="text-purple-600 font-medium mt-4 text-sm">每項分析附原文引用與白話詳解</p>
                </div>
                
                <!-- 現代方法 -->
                <div class="bg-white rounded-2xl p-8 shadow-lg border-t-4 border-blue-500" data-aos="fade-up" data-aos-delay="200">
                    <div class="text-4xl mb-4">🧠</div>
                    <h3 class="text-xl font-bold text-gray-800 mb-3">現代方法</h3>
                    <p class="text-gray-600 mb-4">導入現代決策科學框架</p>
                    <ul class="text-sm text-gray-500 space-y-1">
                        <li>• <strong>場論框架</strong>：時空動態分析</li>
                        <li>• <strong>SWOT 模型</strong>：優劣勢評估</li>
                        <li>• <strong>AI 分析</strong>：多維度驗證</li>
                    </ul>
                    <p class="text-blue-600 font-medium mt-4 text-sm">古典智慧 × 現代決策 × AI 統合</p>
                </div>
                
                <!-- 隱私優先 -->
                <div class="bg-white rounded-2xl p-8 shadow-lg border-t-4 border-green-500" data-aos="fade-up" data-aos-delay="300">
                    <div class="text-4xl mb-4">🔒</div>
                    <h3 class="text-xl font-bold text-gray-800 mb-3">隱私優先</h3>
                    <p class="text-gray-600 mb-4">您的資料，絕對安全</p>
                    <ul class="text-sm text-gray-500 space-y-1">
                        <li>• <strong>計算即焚</strong>：資料即時刪除</li>
                        <li>• <strong>零廣告</strong>：純淨體驗</li>
                        <li>• <strong>絕不外流</strong>：不分享第三方</li>
                    </ul>
                    <p class="text-green-600 font-medium mt-4 text-sm">我們不需要您的數據，只需要您的信任</p>
                </div>
            </div>
            
            <!-- 對比表 -->
            <div class="bg-white rounded-2xl shadow-lg p-8 max-w-4xl mx-auto" data-aos="fade-up">
                <h3 class="text-xl font-bold text-center text-gray-800 mb-6">與傳統命理的差異</h3>
                <div class="overflow-x-auto">
                    <table class="w-full text-sm">
                        <thead>
                            <tr class="border-b-2 border-purple-200">
                                <th class="text-left py-3 px-4">維度</th>
                                <th class="text-center py-3 px-4 text-gray-500">傳統命理</th>
                                <th class="text-center py-3 px-4 text-purple-600">北斗命數</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr class="border-b">
                                <td class="py-3 px-4 font-medium">算法來源</td>
                                <td class="text-center py-3 px-4 text-gray-500">口傳心授</td>
                                <td class="text-center py-3 px-4 text-purple-600">典籍原文可查 ✓</td>
                            </tr>
                            <tr class="border-b">
                                <td class="py-3 px-4 font-medium">解釋方式</td>
                                <td class="text-center py-3 px-4 text-gray-500">專業術語</td>
                                <td class="text-center py-3 px-4 text-purple-600">白話詳解 ✓</td>
                            </tr>
                            <tr class="border-b">
                                <td class="py-3 px-4 font-medium">分析框架</td>
                                <td class="text-center py-3 px-4 text-gray-500">單一術數</td>
                                <td class="text-center py-3 px-4 text-purple-600">多術數 + SWOT + AI ✓</td>
                            </tr>
                            <tr class="border-b">
                                <td class="py-3 px-4 font-medium">輸出結果</td>
                                <td class="text-center py-3 px-4 text-gray-500">吉凶斷言</td>
                                <td class="text-center py-3 px-4 text-purple-600">決策建議 ✓</td>
                            </tr>
                            <tr>
                                <td class="py-3 px-4 font-medium">資料安全</td>
                                <td class="text-center py-3 px-4 text-gray-500">長期保存</td>
                                <td class="text-center py-3 px-4 text-purple-600">計算即焚 ✓</td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            </div>
            
            <!-- 金句 -->
            <div class="text-center mt-12" data-aos="fade-up">
                <p class="text-2xl font-medium text-gray-700">「知其然，更知其所以然」</p>
                <p class="text-gray-500 mt-2">您的命運，由您決定。我們只是提供另一個視角。</p>
            </div>
        </div>
    </section>

    <!-- 定價 -->
    <section id="pricing" class="py-24">
        <div class="max-w-6xl mx-auto px-6">
            <div class="text-center mb-16" data-aos="fade-up">
                <h2 class="text-4xl font-bold text-gray-800 mb-4">透明定價</h2>
                <p class="text-gray-600 text-lg">選擇適合您的方案，開始探索命運密碼</p>
            </div>
            
            <div class="grid md:grid-cols-3 gap-8">
                <div class="bg-white rounded-2xl p-8 shadow-lg border-2 border-gray-100" data-aos="fade-up">
                    <h3 class="text-xl font-bold text-gray-800 mb-2">基礎命盤</h3>
                    <div class="text-4xl font-bold gradient-text mb-4">NT$299</div>
                    <p class="text-gray-500 mb-6">單次購買</p>
                    <ul class="space-y-3 mb-8">
                        <li class="flex items-center text-gray-600"><span class="text-green-500 mr-2">✓</span>八字四柱排盤</li>
                        <li class="flex items-center text-gray-600"><span class="text-green-500 mr-2">✓</span>五行分析</li>
                        <li class="flex items-center text-gray-600"><span class="text-green-500 mr-2">✓</span>性格特質解讀</li>
                        <li class="flex items-center text-gray-600"><span class="text-green-500 mr-2">✓</span>PDF 報告下載</li>
                    </ul>
                    <a href="/register" class="block w-full text-center gradient-bg text-white py-3 rounded-xl font-bold hover:opacity-90">選擇方案</a>
                </div>
                
                <div class="bg-white rounded-2xl p-8 shadow-xl border-2 border-purple-500 relative" data-aos="fade-up" data-aos-delay="100">
                    <div class="absolute -top-4 left-1/2 -translate-x-1/2 gradient-bg text-white px-4 py-1 rounded-full text-sm font-bold">推薦</div>
                    <h3 class="text-xl font-bold text-gray-800 mb-2">完整命理</h3>
                    <div class="text-4xl font-bold gradient-text mb-4">NT$599</div>
                    <p class="text-gray-500 mb-6">單次購買</p>
                    <ul class="space-y-3 mb-8">
                        <li class="flex items-center text-gray-600"><span class="text-green-500 mr-2">✓</span>包含基礎命盤全部</li>
                        <li class="flex items-center text-gray-600"><span class="text-green-500 mr-2">✓</span>紫微斗數排盤</li>
                        <li class="flex items-center text-gray-600"><span class="text-green-500 mr-2">✓</span>十年大運分析</li>
                        <li class="flex items-center text-gray-600"><span class="text-green-500 mr-2">✓</span>今年流年詳解</li>
                        <li class="flex items-center text-gray-600"><span class="text-green-500 mr-2">✓</span>事業/感情建議</li>
                    </ul>
                    <a href="/register" class="block w-full text-center gradient-bg text-white py-3 rounded-xl font-bold hover:opacity-90">選擇方案</a>
                </div>
                
                <div class="bg-white rounded-2xl p-8 shadow-lg border-2 border-gray-100" data-aos="fade-up" data-aos-delay="200">
                    <h3 class="text-xl font-bold text-gray-800 mb-2">尊榮會員</h3>
                    <div class="text-4xl font-bold gradient-text mb-4">NT$1,999</div>
                    <p class="text-gray-500 mb-6">年費會員</p>
                    <ul class="space-y-3 mb-8">
                        <li class="flex items-center text-gray-600"><span class="text-green-500 mr-2">✓</span>包含完整命理全部</li>
                        <li class="flex items-center text-gray-600"><span class="text-green-500 mr-2">✓</span>每月運勢更新</li>
                        <li class="flex items-center text-gray-600"><span class="text-green-500 mr-2">✓</span>3次擇日服務</li>
                        <li class="flex items-center text-gray-600"><span class="text-green-500 mr-2">✓</span>1次命名分析</li>
                        <li class="flex items-center text-gray-600"><span class="text-green-500 mr-2">✓</span>專屬客服</li>
                    </ul>
                    <a href="/register" class="block w-full text-center gradient-bg text-white py-3 rounded-xl font-bold hover:opacity-90">選擇方案</a>
                </div>
            </div>
        </div>
    </section>

    <!-- 用戶見證 -->
    <section class="py-24 bg-gray-50">
        <div class="max-w-6xl mx-auto px-6">
            <div class="text-center mb-16" data-aos="fade-up">
                <h2 class="text-4xl font-bold text-gray-800 mb-4">用戶好評</h2>
            </div>
            
            <div class="grid md:grid-cols-3 gap-8">
                <div class="bg-white rounded-2xl p-8 shadow-lg" data-aos="fade-up">
                    <div class="flex items-center mb-4">
                        <span class="text-yellow-400 text-2xl">★★★★★</span>
                    </div>
                    <p class="text-gray-600 mb-4">「報告分析得很細緻，特別是大運走勢的部分，讓我對未來有更清晰的規劃方向。」</p>
                    <div class="text-gray-800 font-bold">— 林小姐，台北</div>
                </div>
                
                <div class="bg-white rounded-2xl p-8 shadow-lg" data-aos="fade-up" data-aos-delay="100">
                    <div class="flex items-center mb-4">
                        <span class="text-yellow-400 text-2xl">★★★★★</span>
                    </div>
                    <p class="text-gray-600 mb-4">「擇日服務很實用，訂婚選的日子家人都很滿意，謝謝北斗命數！」</p>
                    <div class="text-gray-800 font-bold">— 陳先生，高雄</div>
                </div>
                
                <div class="bg-white rounded-2xl p-8 shadow-lg" data-aos="fade-up" data-aos-delay="200">
                    <div class="flex items-center mb-4">
                        <span class="text-yellow-400 text-2xl">★★★★★</span>
                    </div>
                    <p class="text-gray-600 mb-4">「幫寶寶取名用的，推薦的名字不但好聽，五行也補得很好，很專業！」</p>
                    <div class="text-gray-800 font-bold">— 王太太，台中</div>
                </div>
            </div>
        </div>
    </section>

    <!-- FAQ -->
    <section id="faq" class="py-24">
        <div class="max-w-3xl mx-auto px-6">
            <div class="text-center mb-16" data-aos="fade-up">
                <h2 class="text-4xl font-bold text-gray-800 mb-4">常見問題</h2>
            </div>
            
            <div class="space-y-4">
                <details class="bg-white rounded-xl p-6 shadow-lg cursor-pointer" data-aos="fade-up">
                    <summary class="font-bold text-gray-800 text-lg">報告多久可以收到？</summary>
                    <p class="text-gray-600 mt-4">付款完成後，報告會在 3 分鐘內自動生成，您可以直接在網站下載 PDF。</p>
                </details>
                
                <details class="bg-white rounded-xl p-6 shadow-lg cursor-pointer" data-aos="fade-up" data-aos-delay="100">
                    <summary class="font-bold text-gray-800 text-lg">不知道出生時辰怎麼辦？</summary>
                    <p class="text-gray-600 mt-4">您可以選擇「時辰不詳」選項，系統會以日柱為主進行分析，準確度會略有下降但仍具參考價值。</p>
                </details>
                
                <details class="bg-white rounded-xl p-6 shadow-lg cursor-pointer" data-aos="fade-up" data-aos-delay="200">
                    <summary class="font-bold text-gray-800 text-lg">可以退款嗎？</summary>
                    <p class="text-gray-600 mt-4">由於報告為即時生成的數位商品，一經購買恕不退款。建議先使用免費試算了解服務內容。</p>
                </details>
                
                <details class="bg-white rounded-xl p-6 shadow-lg cursor-pointer" data-aos="fade-up" data-aos-delay="300">
                    <summary class="font-bold text-gray-800 text-lg">命理分析準確嗎？</summary>
                    <p class="text-gray-600 mt-4">我們採用傳統命理學原理進行計算，結果僅供參考。重大人生決策建議諮詢專業人士。</p>
                </details>
            </div>
        </div>
    </section>

    <!-- CTA -->
    <section class="gradient-bg py-20">
        <div class="max-w-4xl mx-auto px-6 text-center text-white" data-aos="fade-up">
            <h2 class="text-4xl font-bold mb-6">準備好探索您的命運了嗎？</h2>
            <p class="text-xl text-purple-100 mb-8">立即註冊，免費獲得 50 點，開始您的命理之旅</p>
            <a href="/free" class="inline-block bg-white text-purple-700 px-12 py-4 rounded-xl text-xl font-bold hover:bg-purple-50 shadow-lg">
                🔮 免費試算
            </a>
        </div>
    </section>

    <!-- Footer -->
    <footer class="bg-gray-900 text-gray-400 py-12">
        <div class="max-w-6xl mx-auto px-6">
            <div class="grid md:grid-cols-4 gap-8 mb-8">
                <div>
                    <h4 class="text-white font-bold text-lg mb-4">🌟 北斗命數</h4>
                    <p class="text-sm">專業命理分析服務<br>結合傳統智慧與現代科技</p>
                </div>
                <div>
                    <h4 class="text-white font-bold mb-4">服務</h4>
                    <ul class="space-y-2 text-sm">
                        <li><a href="/free" class="hover:text-white">免費試算</a></li>
                        <li><a href="/pricing" class="hover:text-white">定價方案</a></li>
                        <li><a href="/bazi" class="hover:text-white">八字分析</a></li>
                    </ul>
                </div>
                <div>
                    <h4 class="text-white font-bold mb-4">支援</h4>
                    <ul class="space-y-2 text-sm">
                        <li><a href="#faq" class="hover:text-white">常見問題</a></li>
                        <li><a href="mailto:service@beidou-mingshu.com" class="hover:text-white">聯繫我們</a></li>
                    </ul>
                </div>
                <div>
                    <h4 class="text-white font-bold mb-4">法律</h4>
                    <ul class="space-y-2 text-sm">
                        <li><a href="/legal/privacy" class="hover:text-white">隱私政策</a></li>
                        <li><a href="/legal/terms" class="hover:text-white">服務條款</a></li>
                        <li><a href="/legal/disclaimer" class="hover:text-white">免責聲明</a></li>
                    </ul>
                </div>
            </div>
            <div class="border-t border-gray-800 pt-8 text-center text-sm">
                <p>© 2026 北斗命數. All rights reserved.</p>
            </div>
        </div>
    </footer>

    <script src="https://unpkg.com/aos@2.3.1/dist/aos.js"></script>
    <script>AOS.init({ duration: 800, once: true });</script>
</body>
</html>'''

@router.get("/", response_class=HTMLResponse)
async def landing_page():
    """落地頁首頁"""
    return LANDING_HTML
