"""Loading 動畫組件 | @璃語"""
LOADING_CSS = '''
<style>
@keyframes spin { to { transform: rotate(360deg); } }
@keyframes pulse { 0%, 100% { opacity: 1; } 50% { opacity: 0.5; } }
.loading-spinner { width: 40px; height: 40px; border: 4px solid #e5e7eb; border-top-color: #667eea; border-radius: 50%; animation: spin 1s linear infinite; }
.loading-pulse { animation: pulse 2s ease-in-out infinite; }
.loading-overlay { position: fixed; inset: 0; background: rgba(255,255,255,0.9); display: flex; align-items: center; justify-content: center; z-index: 9999; }
</style>
'''
LOADING_HTML = '<div class="loading-overlay" id="loading"><div class="loading-spinner"></div></div>'
def get_loading(): return LOADING_CSS + LOADING_HTML
