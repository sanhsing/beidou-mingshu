"""統一頁腳組件 | @璃語"""
FOOTER_HTML = '''
<footer class="bg-gray-800 text-gray-400 py-12 px-6">
    <div class="max-w-6xl mx-auto grid md:grid-cols-4 gap-8">
        <div><h3 class="text-white font-bold mb-4">🌟 北斗命數</h3><p class="text-sm">結合傳統命理與現代科技</p></div>
        <div><h4 class="text-white font-bold mb-4">服務</h4><ul class="space-y-2 text-sm"><li><a href="/free" class="hover:text-white">免費試算</a></li><li><a href="/pricing" class="hover:text-white">方案價格</a></li></ul></div>
        <div><h4 class="text-white font-bold mb-4">關於</h4><ul class="space-y-2 text-sm"><li><a href="/about" class="hover:text-white">關於我們</a></li><li><a href="/help" class="hover:text-white">常見問題</a></li></ul></div>
        <div><h4 class="text-white font-bold mb-4">法律</h4><ul class="space-y-2 text-sm"><li><a href="/legal/privacy" class="hover:text-white">隱私政策</a></li><li><a href="/legal/terms" class="hover:text-white">服務條款</a></li><li><a href="/legal/cookie" class="hover:text-white">Cookie政策</a></li><li><a href="/legal/children" class="hover:text-white">兒童保護</a></li></ul></div>
    </div>
    <div class="max-w-6xl mx-auto mt-8 pt-8 border-t border-gray-700 text-center text-sm">© 2026 北斗命數 v1.0.0</div>
</footer>'''
def get_footer(): return FOOTER_HTML
