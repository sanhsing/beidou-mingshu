"""響應式導航欄 | @璃語"""
NAVBAR_HTML = '''
<nav class="gradient-bg text-white p-4 shadow-lg sticky top-0 z-50">
    <div class="max-w-6xl mx-auto flex justify-between items-center">
        <a href="/" class="text-2xl font-bold">🌟 北斗命數</a>
        <div class="hidden md:flex space-x-4 items-center">
            <a href="/free" class="hover:text-purple-200">免費試算</a>
            <a href="/pricing" class="hover:text-purple-200">方案</a>
            <a href="/help" class="hover:text-purple-200">幫助</a>
            <a href="/login" class="bg-white text-purple-600 px-4 py-2 rounded-lg font-medium">登入</a>
        </div>
        <button class="md:hidden" onclick="toggleMobileMenu()">☰</button>
    </div>
    <div id="mobileMenu" class="hidden md:hidden mt-4 space-y-2">
        <a href="/free" class="block py-2 hover:text-purple-200">免費試算</a>
        <a href="/pricing" class="block py-2 hover:text-purple-200">方案</a>
        <a href="/help" class="block py-2 hover:text-purple-200">幫助</a>
        <a href="/login" class="block py-2 bg-white text-purple-600 rounded-lg text-center">登入</a>
    </div>
</nav>
<script>function toggleMobileMenu(){document.getElementById('mobileMenu').classList.toggle('hidden');}</script>
'''
def get_navbar(): return NAVBAR_HTML
