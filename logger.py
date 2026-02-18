#!/usr/bin/env python3
"""
logger.py - 北斗命數結構化日誌系統
版本：v1.0.0

═══════════════════════════════════════════════════════════════════════
功能：
  • 結構化日誌輸出
  • 文件輪轉
  • 錯誤追蹤
  • 請求日誌
═══════════════════════════════════════════════════════════════════════

XTF Task Chain: D8
@11星協作：@星殼(架構)
"""

import os
import sys
import json
import logging
import traceback
from datetime import datetime
from typing import Any, Dict, Optional
from logging.handlers import RotatingFileHandler
from pathlib import Path

# ════════════════════════════════════════════════════════════════════
# 配置
# ════════════════════════════════════════════════════════════════════

LOG_DIR = os.environ.get("LOG_PATH", "./logs")
LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO")
LOG_MAX_SIZE = 10 * 1024 * 1024  # 10MB
LOG_BACKUP_COUNT = 5

# 確保日誌目錄存在
Path(LOG_DIR).mkdir(parents=True, exist_ok=True)

# ════════════════════════════════════════════════════════════════════
# 結構化日誌格式器
# ════════════════════════════════════════════════════════════════════

class StructuredFormatter(logging.Formatter):
    """結構化 JSON 日誌格式器"""
    
    def format(self, record: logging.LogRecord) -> str:
        log_data = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        
        # 添加額外字段
        if hasattr(record, 'extra_data'):
            log_data["data"] = record.extra_data
        
        # 添加異常信息
        if record.exc_info:
            log_data["exception"] = {
                "type": record.exc_info[0].__name__ if record.exc_info[0] else None,
                "message": str(record.exc_info[1]) if record.exc_info[1] else None,
                "traceback": traceback.format_exception(*record.exc_info) if record.exc_info[0] else None,
            }
        
        return json.dumps(log_data, ensure_ascii=False)


class ConsoleFormatter(logging.Formatter):
    """控制台彩色格式器"""
    
    COLORS = {
        'DEBUG': '\033[36m',     # Cyan
        'INFO': '\033[32m',      # Green
        'WARNING': '\033[33m',   # Yellow
        'ERROR': '\033[31m',     # Red
        'CRITICAL': '\033[35m',  # Magenta
    }
    RESET = '\033[0m'
    
    def format(self, record: logging.LogRecord) -> str:
        color = self.COLORS.get(record.levelname, self.RESET)
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # 基本格式
        msg = f"{timestamp} | {color}{record.levelname:8}{self.RESET} | {record.name} | {record.getMessage()}"
        
        # 添加額外數據
        if hasattr(record, 'extra_data') and record.extra_data:
            data_str = json.dumps(record.extra_data, ensure_ascii=False)
            if len(data_str) > 200:
                data_str = data_str[:200] + "..."
            msg += f" | {data_str}"
        
        return msg

# ════════════════════════════════════════════════════════════════════
# Logger 類
# ════════════════════════════════════════════════════════════════════

class BeidouLogger:
    """北斗命數 Logger"""
    
    _instance = None
    _loggers: Dict[str, logging.Logger] = {}
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        self._setup_root_logger()
        self._initialized = True
    
    def _setup_root_logger(self):
        """設置根日誌器"""
        root_logger = logging.getLogger("beidou")
        root_logger.setLevel(getattr(logging, LOG_LEVEL.upper(), logging.INFO))
        
        # 清除現有 handlers
        root_logger.handlers.clear()
        
        # 控制台 Handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(ConsoleFormatter())
        root_logger.addHandler(console_handler)
        
        # 文件 Handler（JSON 格式）
        file_handler = RotatingFileHandler(
            os.path.join(LOG_DIR, "beidou.log"),
            maxBytes=LOG_MAX_SIZE,
            backupCount=LOG_BACKUP_COUNT,
            encoding='utf-8',
        )
        file_handler.setFormatter(StructuredFormatter())
        root_logger.addHandler(file_handler)
        
        # 錯誤文件 Handler
        error_handler = RotatingFileHandler(
            os.path.join(LOG_DIR, "error.log"),
            maxBytes=LOG_MAX_SIZE,
            backupCount=LOG_BACKUP_COUNT,
            encoding='utf-8',
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(StructuredFormatter())
        root_logger.addHandler(error_handler)
        
        self._loggers["beidou"] = root_logger
    
    def get_logger(self, name: str = "beidou") -> logging.Logger:
        """獲取日誌器"""
        if name not in self._loggers:
            logger = logging.getLogger(name)
            if not name.startswith("beidou"):
                logger.parent = self._loggers.get("beidou")
            self._loggers[name] = logger
        return self._loggers[name]
    
    def log_with_data(
        self, 
        level: str, 
        message: str, 
        data: Optional[Dict[str, Any]] = None,
        logger_name: str = "beidou"
    ):
        """帶數據的日誌"""
        logger = self.get_logger(logger_name)
        record = logger.makeRecord(
            logger_name, 
            getattr(logging, level.upper()), 
            "", 0, 
            message, 
            (), 
            None
        )
        if data:
            record.extra_data = data
        logger.handle(record)

# ════════════════════════════════════════════════════════════════════
# 便捷函數
# ════════════════════════════════════════════════════════════════════

_logger_instance = BeidouLogger()

def get_logger(name: str = "beidou") -> logging.Logger:
    """獲取日誌器"""
    return _logger_instance.get_logger(name)

def log_info(message: str, data: Dict = None):
    """INFO 日誌"""
    _logger_instance.log_with_data("INFO", message, data)

def log_warning(message: str, data: Dict = None):
    """WARNING 日誌"""
    _logger_instance.log_with_data("WARNING", message, data)

def log_error(message: str, data: Dict = None, exc_info: bool = False):
    """ERROR 日誌"""
    logger = get_logger()
    if exc_info:
        logger.error(message, exc_info=True)
    else:
        _logger_instance.log_with_data("ERROR", message, data)

def log_debug(message: str, data: Dict = None):
    """DEBUG 日誌"""
    _logger_instance.log_with_data("DEBUG", message, data)

# ════════════════════════════════════════════════════════════════════
# 請求日誌中間件
# ════════════════════════════════════════════════════════════════════

import time
from fastapi import Request

async def request_logging_middleware(request: Request, call_next):
    """請求日誌中間件"""
    start_time = time.time()
    
    # 請求信息
    request_data = {
        "method": request.method,
        "path": str(request.url.path),
        "query": str(request.query_params),
        "client_ip": request.client.host if request.client else "unknown",
    }
    
    # 執行請求
    try:
        response = await call_next(request)
        process_time = (time.time() - start_time) * 1000
        
        # 響應信息
        log_data = {
            **request_data,
            "status_code": response.status_code,
            "process_time_ms": round(process_time, 2),
        }
        
        # 根據狀態碼選擇日誌級別
        if response.status_code >= 500:
            log_error(f"Request completed with error", log_data)
        elif response.status_code >= 400:
            log_warning(f"Request completed with client error", log_data)
        else:
            log_info(f"Request completed", log_data)
        
        return response
        
    except Exception as e:
        process_time = (time.time() - start_time) * 1000
        log_data = {
            **request_data,
            "error": str(e),
            "process_time_ms": round(process_time, 2),
        }
        log_error(f"Request failed: {e}", log_data, exc_info=True)
        raise

# ════════════════════════════════════════════════════════════════════
# 測試
# ════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("═" * 60)
    print("  日誌系統測試")
    print("═" * 60)
    
    logger = get_logger()
    
    print("\n【基本日誌測試】")
    log_info("這是一條 INFO 日誌")
    log_warning("這是一條 WARNING 日誌")
    log_error("這是一條 ERROR 日誌")
    log_debug("這是一條 DEBUG 日誌")
    
    print("\n【帶數據日誌測試】")
    log_info("用戶登入", {"user_id": 1, "username": "test"})
    log_warning("點數不足", {"user_id": 1, "credits": 0, "required": 50})
    
    print("\n【異常日誌測試】")
    try:
        raise ValueError("測試異常")
    except Exception as e:
        log_error(f"捕獲異常: {e}", exc_info=True)
    
    print("\n【日誌文件】")
    for f in Path(LOG_DIR).glob("*.log"):
        print(f"  {f.name}: {f.stat().st_size} bytes")
    
    print("\n" + "═" * 60)
    print("✅ 日誌系統測試完成")
    print("═" * 60)
