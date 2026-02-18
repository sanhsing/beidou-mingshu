#!/usr/bin/env python3
"""
security.py - 北斗命數安全中間件
版本：v1.0.0

═══════════════════════════════════════════════════════════════════════
功能：
  • Rate Limiting（限流）
  • IP 黑名單
  • 安全 Headers
  • SQL 注入防護
═══════════════════════════════════════════════════════════════════════

XTF Task Chain: D7
@11星協作：@星殼(架構)
"""

import time
import re
from typing import Dict, List, Optional, Callable
from collections import defaultdict
from datetime import datetime, timedelta
from functools import wraps

from fastapi import Request, HTTPException, Response
from fastapi.responses import JSONResponse

# ════════════════════════════════════════════════════════════════════
# Rate Limiter
# ════════════════════════════════════════════════════════════════════

class RateLimiter:
    """請求限流器"""
    
    def __init__(self):
        self.requests: Dict[str, List[float]] = defaultdict(list)
        self.blocked_ips: Dict[str, float] = {}
    
    def is_blocked(self, ip: str) -> bool:
        """檢查 IP 是否被封鎖"""
        if ip in self.blocked_ips:
            if time.time() < self.blocked_ips[ip]:
                return True
            else:
                del self.blocked_ips[ip]
        return False
    
    def block_ip(self, ip: str, duration: int = 3600):
        """封鎖 IP"""
        self.blocked_ips[ip] = time.time() + duration
    
    def check_rate(self, ip: str, limit: int = 100, window: int = 60) -> bool:
        """
        檢查請求頻率
        
        Args:
            ip: 客戶端 IP
            limit: 時間窗口內允許的最大請求數
            window: 時間窗口（秒）
        
        Returns:
            True 如果允許，False 如果超限
        """
        now = time.time()
        window_start = now - window
        
        # 清理過期記錄
        self.requests[ip] = [
            t for t in self.requests[ip] 
            if t > window_start
        ]
        
        # 檢查是否超限
        if len(self.requests[ip]) >= limit:
            return False
        
        # 記錄請求
        self.requests[ip].append(now)
        return True
    
    def get_remaining(self, ip: str, limit: int = 100, window: int = 60) -> int:
        """獲取剩餘請求數"""
        now = time.time()
        window_start = now - window
        count = len([t for t in self.requests[ip] if t > window_start])
        return max(0, limit - count)

# 全局限流器
rate_limiter = RateLimiter()

# ════════════════════════════════════════════════════════════════════
# 安全 Headers
# ════════════════════════════════════════════════════════════════════

SECURITY_HEADERS = {
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
    "X-XSS-Protection": "1; mode=block",
    "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
    "Content-Security-Policy": "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'",
    "Referrer-Policy": "strict-origin-when-cross-origin",
    "Permissions-Policy": "geolocation=(), microphone=(), camera=()",
}

def add_security_headers(response: Response) -> Response:
    """添加安全 Headers"""
    for key, value in SECURITY_HEADERS.items():
        response.headers[key] = value
    return response

# ════════════════════════════════════════════════════════════════════
# SQL 注入防護
# ════════════════════════════════════════════════════════════════════

SQL_INJECTION_PATTERNS = [
    r"(\b(union|select|insert|update|delete|drop|truncate|alter)\b)",
    r"(--|#|/\*|\*/)",
    r"(\b(or|and)\b\s+\d+\s*=\s*\d+)",
    r"('\s*;\s*--)",
    r"(xp_|sp_)",
]

def check_sql_injection(value: str) -> bool:
    """
    檢查 SQL 注入
    
    Returns:
        True 如果檢測到可疑內容
    """
    if not value:
        return False
    
    value_lower = value.lower()
    for pattern in SQL_INJECTION_PATTERNS:
        if re.search(pattern, value_lower, re.IGNORECASE):
            return True
    return False

def sanitize_input(value: str) -> str:
    """清理輸入"""
    if not value:
        return value
    
    # 移除可疑字符
    value = re.sub(r'[<>"\']', '', value)
    # 限制長度
    return value[:1000]

# ════════════════════════════════════════════════════════════════════
# 中間件
# ════════════════════════════════════════════════════════════════════

async def security_middleware(request: Request, call_next):
    """安全中間件"""
    client_ip = request.client.host if request.client else "unknown"
    
    # 1. 檢查 IP 黑名單
    if rate_limiter.is_blocked(client_ip):
        return JSONResponse(
            status_code=429,
            content={"error": "IP 已被暫時封鎖", "retry_after": 3600}
        )
    
    # 2. 檢查請求頻率
    path = request.url.path
    
    # 認證端點更嚴格
    if "/auth/" in path:
        limit, window = 10, 60  # 每分鐘 10 次
    else:
        limit, window = 100, 60  # 每分鐘 100 次
    
    if not rate_limiter.check_rate(client_ip, limit, window):
        return JSONResponse(
            status_code=429,
            content={
                "error": "請求過於頻繁，請稍後再試",
                "retry_after": 60
            }
        )
    
    # 3. 執行請求
    response = await call_next(request)
    
    # 4. 添加安全 Headers
    response = add_security_headers(response)
    
    # 5. 添加 Rate Limit Headers
    remaining = rate_limiter.get_remaining(client_ip, limit, window)
    response.headers["X-RateLimit-Limit"] = str(limit)
    response.headers["X-RateLimit-Remaining"] = str(remaining)
    response.headers["X-RateLimit-Reset"] = str(int(time.time()) + window)
    
    return response

# ════════════════════════════════════════════════════════════════════
# 裝飾器
# ════════════════════════════════════════════════════════════════════

def rate_limit(limit: int = 10, window: int = 60):
    """限流裝飾器"""
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(request: Request, *args, **kwargs):
            client_ip = request.client.host if request.client else "unknown"
            
            if not rate_limiter.check_rate(client_ip, limit, window):
                raise HTTPException(
                    status_code=429,
                    detail=f"請求過於頻繁，請 {window} 秒後再試"
                )
            
            return await func(request, *args, **kwargs)
        return wrapper
    return decorator

# ════════════════════════════════════════════════════════════════════
# 工具函數
# ════════════════════════════════════════════════════════════════════

def validate_password(password: str) -> tuple[bool, str]:
    """
    驗證密碼強度
    
    Returns:
        (is_valid, message)
    """
    if len(password) < 6:
        return False, "密碼長度至少 6 個字符"
    if len(password) > 128:
        return False, "密碼長度不能超過 128 個字符"
    return True, "密碼強度合格"

def mask_sensitive_data(data: dict, fields: List[str] = None) -> dict:
    """遮蔽敏感數據"""
    if fields is None:
        fields = ["password", "token", "secret", "api_key", "hash_key", "hash_iv"]
    
    masked = data.copy()
    for key in masked:
        if any(f in key.lower() for f in fields):
            masked[key] = "***"
    return masked

# ════════════════════════════════════════════════════════════════════
# 測試
# ════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("═" * 60)
    print("  安全模組測試")
    print("═" * 60)
    
    # 測試 Rate Limiter
    print("\n【Rate Limiter 測試】")
    for i in range(12):
        allowed = rate_limiter.check_rate("test_ip", limit=10, window=60)
        print(f"  請求 {i+1}: {'✅ 允許' if allowed else '❌ 拒絕'}")
    
    # 測試 SQL 注入檢測
    print("\n【SQL 注入檢測】")
    test_inputs = [
        "正常輸入",
        "' OR 1=1 --",
        "SELECT * FROM users",
        "user'; DROP TABLE users;--",
    ]
    for inp in test_inputs:
        detected = check_sql_injection(inp)
        print(f"  {inp[:30]:30} → {'🚨 檢測到' if detected else '✅ 安全'}")
    
    # 測試密碼驗證
    print("\n【密碼驗證測試】")
    passwords = ["123", "password123", "a" * 200]
    for pwd in passwords:
        valid, msg = validate_password(pwd)
        print(f"  {pwd[:20]:20} → {'✅' if valid else '❌'} {msg}")
    
    print("\n" + "═" * 60)
    print("✅ 安全模組測試完成")
    print("═" * 60)
