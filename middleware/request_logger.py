"""請求日誌中間件 | @理樞"""
import time
async def log_request(request, call_next):
    start = time.time()
    response = await call_next(request)
    print(f"[API] {request.method} {request.url.path} → {response.status_code} ({round((time.time()-start)*1000,2)}ms)")
    return response
