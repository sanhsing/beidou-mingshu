"""API 限流中間件 | @星殼"""
from collections import defaultdict
import time
request_counts = defaultdict(list)
async def rate_limit_middleware(request, call_next):
    key = f"{request.client.host if request.client else 'unknown'}:{request.url.path}"
    now = time.time()
    request_counts[key] = [t for t in request_counts[key] if now - t < 60]
    if len(request_counts[key]) >= 100:
        from fastapi import HTTPException
        raise HTTPException(429, "請求過於頻繁")
    request_counts[key].append(now)
    return await call_next(request)
