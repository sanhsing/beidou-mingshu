"""統一錯誤格式 | @理樞"""
from fastapi.responses import JSONResponse
from datetime import datetime
def error_response(code, message, status=400, details=None):
    return JSONResponse(status_code=status, content={"success": False, "error": {"code": code, "message": message, "timestamp": datetime.now().isoformat()}})
ERROR_CODES = {"AUTH_REQUIRED": ("請先登入", 401), "NOT_FOUND": ("資源不存在", 404), "RATE_LIMIT": ("請求過於頻繁", 429)}
