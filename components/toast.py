"""Toast 通知組件 | @星殼"""
TOAST_HTML = '''
<style>
.toast { position: fixed; bottom: 20px; right: 20px; padding: 12px 24px; border-radius: 8px; color: white; z-index: 9999; transform: translateX(120%); transition: transform 0.3s; }
.toast.show { transform: translateX(0); }
.toast.success { background: #10b981; }
.toast.error { background: #ef4444; }
.toast.info { background: #3b82f6; }
</style>
<div id="toast" class="toast"></div>
<script>
function showToast(msg, type='info', duration=3000) {
    const t = document.getElementById('toast');
    t.textContent = msg;
    t.className = 'toast ' + type + ' show';
    setTimeout(() => t.classList.remove('show'), duration);
}
</script>
'''
def get_toast(): return TOAST_HTML
