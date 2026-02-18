"""
監控追蹤模組
M11.1-M11.5 | @理樞 | 2026-02-17
PYLIB: logger
"""
import os
import time
from datetime import datetime
from functools import wraps
from typing import Callable, Any
from loguru import logger

# === Sentry 初始化 ===
def init_sentry():
    """初始化 Sentry 錯誤監控"""
    sentry_dsn = os.getenv('SENTRY_DSN')
    if not sentry_dsn:
        logger.warning("SENTRY_DSN 未設定，錯誤監控已禁用")
        return False
    
    try:
        import sentry_sdk
        sentry_sdk.init(
            dsn=sentry_dsn,
            traces_sample_rate=0.1,
            environment=os.getenv('APP_ENV', 'development')
        )
        logger.info("✓ Sentry 錯誤監控已啟用")
        return True
    except ImportError:
        logger.warning("sentry-sdk 未安裝")
        return False
    except Exception as e:
        logger.error(f"Sentry 初始化失敗: {e}")
        return False

# === GA4 追蹤代碼 ===
GA4_SCRIPT = '''
<!-- Google Analytics 4 -->
<script async src="https://www.googletagmanager.com/gtag/js?id={ga_id}"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){{dataLayer.push(arguments);}}
  gtag('js', new Date());
  gtag('config', '{ga_id}');
</script>
'''

def get_ga4_script() -> str:
    """獲取 GA4 追蹤代碼"""
    ga_id = os.getenv('GA4_ID', '')
    if not ga_id:
        return '<!-- GA4 未配置 -->'
    return GA4_SCRIPT.format(ga_id=ga_id)

# === 事件追蹤 ===
EVENT_TRACKING_JS = '''
// 北斗命數 - 事件追蹤
const BeidouTrack = {
    // 頁面瀏覽
    pageView: function(page) {
        if (typeof gtag !== 'undefined') {
            gtag('event', 'page_view', { page_path: page });
        }
        console.log('[Track] Page:', page);
    },
    
    // 按鈕點擊
    buttonClick: function(name, category) {
        if (typeof gtag !== 'undefined') {
            gtag('event', 'click', { 
                event_category: category || 'button',
                event_label: name 
            });
        }
        console.log('[Track] Click:', name);
    },
    
    // 表單提交
    formSubmit: function(formName) {
        if (typeof gtag !== 'undefined') {
            gtag('event', 'form_submit', { form_name: formName });
        }
        console.log('[Track] Form:', formName);
    },
    
    // 購買
    purchase: function(item, value) {
        if (typeof gtag !== 'undefined') {
            gtag('event', 'purchase', { 
                items: [{ name: item }],
                value: value,
                currency: 'TWD'
            });
        }
        console.log('[Track] Purchase:', item, value);
    },
    
    // 註冊
    signUp: function(method) {
        if (typeof gtag !== 'undefined') {
            gtag('event', 'sign_up', { method: method || 'email' });
        }
        console.log('[Track] SignUp:', method);
    },
    
    // 報告生成
    reportGenerated: function(reportType) {
        if (typeof gtag !== 'undefined') {
            gtag('event', 'report_generated', { report_type: reportType });
        }
        console.log('[Track] Report:', reportType);
    }
};
'''

# === 性能監控裝飾器 ===
def track_performance(name: str = None):
    """追蹤函數執行時間"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def async_wrapper(*args, **kwargs) -> Any:
            start = time.time()
            try:
                result = await func(*args, **kwargs)
                duration = time.time() - start
                logger.debug(f"[Perf] {name or func.__name__}: {duration:.3f}s")
                return result
            except Exception as e:
                duration = time.time() - start
                logger.error(f"[Perf] {name or func.__name__} FAILED: {duration:.3f}s - {e}")
                raise
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs) -> Any:
            start = time.time()
            try:
                result = func(*args, **kwargs)
                duration = time.time() - start
                logger.debug(f"[Perf] {name or func.__name__}: {duration:.3f}s")
                return result
            except Exception as e:
                duration = time.time() - start
                logger.error(f"[Perf] {name or func.__name__} FAILED: {duration:.3f}s - {e}")
                raise
        
        import asyncio
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        return sync_wrapper
    
    return decorator

# === 簡單指標收集 ===
class Metrics:
    """簡單指標收集器"""
    
    def __init__(self):
        self.counters = {}
        self.start_time = datetime.now()
    
    def incr(self, name: str, value: int = 1):
        """增加計數器"""
        self.counters[name] = self.counters.get(name, 0) + value
    
    def get(self, name: str) -> int:
        """獲取計數器值"""
        return self.counters.get(name, 0)
    
    def get_all(self) -> dict:
        """獲取所有指標"""
        uptime = (datetime.now() - self.start_time).total_seconds()
        return {
            'uptime_seconds': int(uptime),
            'counters': self.counters.copy()
        }

# 全局指標實例
metrics = Metrics()

# === 日誌配置 ===
def setup_logging():
    """設置日誌配置"""
    log_level = os.getenv('LOG_LEVEL', 'INFO')
    log_file = os.getenv('LOG_FILE', 'logs/beidou.log')
    
    # 確保目錄存在
    os.makedirs(os.path.dirname(log_file), exist_ok=True)
    
    logger.add(
        log_file,
        rotation="10 MB",
        retention="7 days",
        level=log_level,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {name} | {message}"
    )
    
    logger.info("✓ 日誌系統已初始化")

# 初始化
if __name__ != "__main__":
    setup_logging()

if __name__ == "__main__":
    setup_logging()
    print("✓ 監控追蹤模組已載入")
    print(f"GA4 腳本長度: {len(get_ga4_script())}")
    print(f"事件追蹤 JS 長度: {len(EVENT_TRACKING_JS)}")
    
    # 測試性能追蹤
    @track_performance("test_func")
    def test():
        time.sleep(0.1)
        return "done"
    
    print(f"測試結果: {test()}")
