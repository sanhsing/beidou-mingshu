#!/usr/bin/env python3
"""
config.py - 北斗命數統一配置管理
版本：v1.0.2
"""
import os
from pathlib import Path
from dataclasses import dataclass, field
from typing import List

# ════════════════════════════════════════════════════════════════════
# L0: 環境變數載入
# ════════════════════════════════════════════════════════════════════

def load_env():
    """載入 .env 文件"""
    env_path = Path(__file__).parent / ".env"
    if env_path.exists():
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, _, value = line.partition("=")
                    key = key.strip()
                    value = value.strip().strip('"').strip("'")
                    if key and key not in os.environ:
                        os.environ[key] = value

load_env()

def get_env(key: str, default: str = "") -> str:
    return os.environ.get(key, default)

def get_env_bool(key: str, default: bool = False) -> bool:
    val = os.environ.get(key, "").lower()
    return val in ("true", "1", "yes", "on") if val else default

def get_env_int(key: str, default: int = 0) -> int:
    try:
        return int(os.environ.get(key, default))
    except (ValueError, TypeError):
        return default

# ════════════════════════════════════════════════════════════════════
# L1: 配置類
# ════════════════════════════════════════════════════════════════════

@dataclass
class AppConfig:
    APP_NAME: str = "北斗命數"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    ENV: str = "production"
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    TIMEZONE: str = "Asia/Taipei"

@dataclass
class DatabaseConfig:
    DB_PATH: str = "./beidou_unified.db"
    DB_POOL_SIZE: int = 5

@dataclass
class AuthConfig:
    JWT_SECRET: str = "change_this_in_production"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440
    PASSWORD_MIN_LENGTH: int = 6
    NEW_USER_CREDITS: int = 100

@dataclass
class PaymentConfig:
    ECPAY_MERCHANT_ID: str = "3002607"
    ECPAY_HASH_KEY: str = "pwFHCqoQZGmho4w6"
    ECPAY_HASH_IV: str = "EkRm7iFT261dpevs"
    ECPAY_SANDBOX: bool = True

@dataclass
class EmailConfig:
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    SMTP_FROM: str = "noreply@beidou-mingshu.com"

@dataclass
class CORSConfig:
    ALLOW_ORIGINS: List[str] = field(default_factory=lambda: ["*"])
    ALLOW_METHODS: List[str] = field(default_factory=lambda: ["*"])
    ALLOW_HEADERS: List[str] = field(default_factory=lambda: ["*"])
    ALLOW_CREDENTIALS: bool = True

# ════════════════════════════════════════════════════════════════════
# L2: 統一配置類
# ════════════════════════════════════════════════════════════════════

class Settings:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        self._load_config()
        self._initialized = True
    
    def _load_config(self):
        self.app = AppConfig(
            APP_NAME=get_env("APP_NAME", "北斗命數"),
            DEBUG=get_env_bool("DEBUG", False),
            PORT=get_env_int("PORT", 8000),
        )
        
        self.db = DatabaseConfig(
            DB_PATH=get_env("DB_PATH", "./beidou_unified.db"),
        )
        
        self.auth = AuthConfig(
            JWT_SECRET=get_env("SECRET_KEY", get_env("JWT_SECRET", "change_this")),
        )
        
        self.payment = PaymentConfig(
            ECPAY_MERCHANT_ID=get_env("ECPAY_MERCHANT_ID", "3002607"),
            ECPAY_HASH_KEY=get_env("ECPAY_HASH_KEY", "pwFHCqoQZGmho4w6"),
            ECPAY_HASH_IV=get_env("ECPAY_HASH_IV", "EkRm7iFT261dpevs"),
            ECPAY_SANDBOX=get_env_bool("ECPAY_SANDBOX", True),
        )
        
        self.email = EmailConfig(
            SMTP_HOST=get_env("SMTP_HOST", "smtp.gmail.com"),
            SMTP_PORT=get_env_int("SMTP_PORT", 587),
        )
        
        self.cors = CORSConfig()
        
        # 兼容屬性
        self.SECRET_KEY = get_env("SECRET_KEY", self.auth.JWT_SECRET)
        self.DATABASE_URL = get_env("DATABASE_URL", f"sqlite:///{self.db.DB_PATH}")

# ════════════════════════════════════════════════════════════════════
# L3: 業務常量
# ════════════════════════════════════════════════════════════════════

REPORT_PLANS = {
    'basic': {'name': '基礎報告', 'credits': 50, 'pages': 12},
    'standard': {'name': '標準報告', 'credits': 100, 'pages': 24},
    'premium': {'name': '完整報告', 'credits': 200, 'pages': 48},
}

CREDIT_PLANS = {
    'credits_100': {'credits': 100, 'price': 99, 'bonus': 0},
    'credits_300': {'credits': 300, 'price': 249, 'bonus': 20},
    'credits_500': {'credits': 500, 'price': 399, 'bonus': 50},
    'credits_1000': {'credits': 1000, 'price': 699, 'bonus': 150},
}

MEMBERSHIP_TIERS = {
    'free': {'name': '免費會員', 'discount': 0},
    'basic': {'name': '基礎會員', 'discount': 0.1},
    'premium': {'name': '尊榮會員', 'discount': 0.2},
    'vip': {'name': 'VIP會員', 'discount': 0.3},
}

# ════════════════════════════════════════════════════════════════════
# L4: 導出
# ════════════════════════════════════════════════════════════════════

settings = Settings()

def get_settings() -> Settings:
    return settings
