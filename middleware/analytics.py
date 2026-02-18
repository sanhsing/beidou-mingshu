"""
GA4 自動注入中間件
analytics.py | @星殼 | 2026-02-17

功能：
- 自動在 HTML 響應中注入 GA4 追蹤代碼
- 支援環境變數配置
"""
import os
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

# GA4 追蹤代碼
GA4_SCRIPT = '''
<!-- Google Analytics 4 -->
<script async src="https://www.googletagmanager.com/gtag/js?id={ga_id}"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){{dataLayer.push(arguments);}}
  gtag('js', new Date());
  gtag('config', '{ga_id}');
  
  // 自定義事件追蹤
  window.trackEvent = function(action, category, label, value) {{
    gtag('event', action, {{
      'event_category': category,
      'event_label': label,
      'value': value
    }});
  }};
</script>
'''

class GA4Middleware(BaseHTTPMiddleware):
    """GA4 自動注入中間件"""
    
    async def dispatch(self, request, call_next):
        response = await call_next(request)
        
        # 只處理 HTML 響應
        content_type = response.headers.get('content-type', '')
        if 'text/html' not in content_type:
            return response
        
        # 檢查 GA4_ID
        ga_id = os.getenv('GA4_ID', '')
        if not ga_id:
            return response
        
        # 讀取響應內容
        body = b''
        async for chunk in response.body_iterator:
            body += chunk
        
        # 注入 GA4 代碼到 </head> 之前
        html = body.decode('utf-8')
        ga_script = GA4_SCRIPT.format(ga_id=ga_id)
        
        if '</head>' in html:
            html = html.replace('</head>', ga_script + '\n</head>')
        
        # 返回修改後的響應
        return Response(
            content=html,
            status_code=response.status_code,
            headers=dict(response.headers),
            media_type='text/html'
        )


def get_ga4_script() -> str:
    """獲取 GA4 追蹤代碼（手動使用）"""
    ga_id = os.getenv('GA4_ID', '')
    if not ga_id:
        return '<!-- GA4 未配置 -->'
    return GA4_SCRIPT.format(ga_id=ga_id)
