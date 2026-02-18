"""
FAQ 頁面模組
M12.1-M12.6 | @澄書 | 2026-02-17
"""
from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter(tags=["help"])

FAQ_DATA = {
    "帳號相關": [
        {"q": "如何註冊帳號？", "a": "點擊首頁「免費註冊」按鈕，填寫 Email 和密碼即可完成註冊。註冊後會獲得 50 點贈送點數。"},
        {"q": "忘記密碼怎麼辦？", "a": "點擊登入頁面的「忘記密碼」，輸入您的 Email，我們會發送重置連結到您的信箱。"},
        {"q": "可以更改 Email 嗎？", "a": "登入後在「帳戶設定」頁面可以更改綁定的 Email。"},
        {"q": "如何刪除帳號？", "a": "請聯繫客服申請刪除帳號，我們會在 30 天內處理。"},
    ],
    "支付相關": [
        {"q": "支援哪些付款方式？", "a": "我們支援信用卡（VISA/MasterCard/JCB）、ATM 轉帳、超商代碼繳費。"},
        {"q": "點數會過期嗎？", "a": "不會，購買的點數永久有效。"},
        {"q": "可以退款嗎？", "a": "由於點數為即時入帳的虛擬商品，購買後恕不退款。訂閱會員可隨時取消，取消後當期仍有效。"},
        {"q": "發票如何取得？", "a": "付款成功後，電子發票會自動寄到您的 Email。"},
    ],
    "報告相關": [
        {"q": "報告多久可以拿到？", "a": "支付完成後，報告會在 3 分鐘內自動生成，您可以在「我的報告」頁面下載 PDF。"},
        {"q": "報告可以重新下載嗎？", "a": "可以，您購買的報告會永久保存在帳戶中，隨時可以重新下載。"},
        {"q": "報告看不懂怎麼辦？", "a": "報告中有詳細的名詞解釋。如仍有疑問，可以聯繫客服或考慮升級到有客服支援的會員方案。"},
        {"q": "可以幫家人算嗎？", "a": "可以，您可以輸入任何人的出生資料進行分析。家族方案更適合多人使用。"},
    ],
    "命理相關": [
        {"q": "不知道出生時辰怎麼辦？", "a": "您可以選擇「時辰不詳」，系統會以日柱為主進行分析。準確度會略有下降但仍具參考價值。"},
        {"q": "命理分析準確嗎？", "a": "命理學是傳統文化的一部分，我們的分析基於嚴謹的命理原理。結果僅供參考，重大決策請諮詢專業人士。"},
        {"q": "八字和紫微有什麼不同？", "a": "八字側重於先天命格和五行平衡，紫微斗數則透過星曜排列解讀人生各宮位的運勢，兩者互補使用效果更佳。"},
        {"q": "可以改命嗎？", "a": "命理顯示的是傾向和可能，透過了解自身優劣勢，積極調整心態和行動，可以更好地把握機會、趨吉避凶。"},
    ],
    "安全相關": [
        {"q": "如何辨別命理詐騙？", "a": "正規服務不會以「煞星」「災劫」等話術恐嚇您付費，也不會持續要求加碼。若遇可疑情況，請撥打 165 反詐騙專線。"},
        {"q": "你們會要求額外消災費用嗎？", "a": "絕對不會。北斗命數是純粹的命理分析工具，不提供任何「消災」「化解」「做法事」等服務。"},
        {"q": "我的個資安全嗎？", "a": "我們採用銀行級加密技術保護您的資料，不會出售或分享您的個人資訊。詳見隱私權政策。"},
        {"q": "報告結果讓我很擔心怎麼辦？", "a": "命理分析僅供參考，不應造成心理負擔。如有困擾，建議諮詢專業心理師。生命線：1925、安心專線：1980。"},
    ],
}

FAQ_HTML = '''<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>常見問題 - 北斗命數</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>.gradient-bg {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); }}</style>
</head>
<body class="bg-gray-50">
    <nav class="gradient-bg text-white p-4 shadow-lg">
        <div class="max-w-4xl mx-auto flex justify-between items-center">
            <a href="/" class="text-2xl font-bold">🌟 北斗命數</a>
            <a href="/" class="hover:text-purple-200">← 返回首頁</a>
        </div>
    </nav>

    <main class="max-w-4xl mx-auto px-6 py-12">
        <h1 class="text-4xl font-bold text-gray-800 text-center mb-4">❓ 常見問題</h1>
        <p class="text-gray-600 text-center mb-12">找不到答案？歡迎聯繫客服 service@beidou-mingshu.com</p>

        {faq_sections}
        
        <!-- 聯繫客服 -->
        <div class="bg-purple-50 rounded-2xl p-8 text-center mt-12">
            <h2 class="text-2xl font-bold text-purple-900 mb-4">還有其他問題？</h2>
            <p class="text-gray-600 mb-6">我們的客服團隊隨時為您服務</p>
            <div class="flex justify-center gap-4 flex-wrap">
                <a href="mailto:service@beidou-mingshu.com" class="gradient-bg text-white px-6 py-3 rounded-lg font-bold hover:opacity-90">
                    📧 發送郵件
                </a>
            </div>
        </div>
    </main>

    <footer class="bg-gray-800 text-gray-400 text-center p-6 mt-12">
        <p>© 2026 北斗命數. All rights reserved.</p>
    </footer>
</body>
</html>'''

def generate_faq_html():
    """生成 FAQ HTML"""
    sections = []
    for category, questions in FAQ_DATA.items():
        section = f'''
        <div class="mb-10">
            <h2 class="text-2xl font-bold text-gray-800 mb-6">{category}</h2>
            <div class="space-y-3">
        '''
        for item in questions:
            section += f'''
                <details class="bg-white rounded-xl p-4 shadow hover:shadow-md transition cursor-pointer">
                    <summary class="font-bold text-gray-800">{item['q']}</summary>
                    <p class="text-gray-600 mt-3 pl-4 border-l-2 border-purple-300">{item['a']}</p>
                </details>
            '''
        section += '</div></div>'
        sections.append(section)
    
    return FAQ_HTML.format(faq_sections=''.join(sections))

@router.get("/help", response_class=HTMLResponse)
async def help_page():
    """FAQ 幫助頁面"""
    return generate_faq_html()

@router.get("/faq", response_class=HTMLResponse)
async def faq_redirect():
    """FAQ 重定向"""
    return generate_faq_html()
