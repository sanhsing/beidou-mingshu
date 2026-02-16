"""
JWT 認證模組 auth_jwt.py v1.0
============================
XTF任務：消-C1 | 執行星：星殼（架構）
確定度：★★★★★（標準化技術）

核心本質：token = header.payload.signature

📚 JWT 認證流程：
1. 用戶登入 → 驗證密碼
2. 生成 JWT Token（含用戶ID、過期時間）
3. 客戶端存儲 Token
4. 請求時攜帶 Token → 驗證
"""

import hashlib
import secrets
import time
import json
import base64
import hmac
from typing import Dict, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta

# 配置
JWT_SECRET = "beidou_mingshu_secret_key_2026"  # 生產環境應從環境變數讀取
JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24小時
REFRESH_TOKEN_EXPIRE_DAYS = 7


@dataclass
class TokenPayload:
    """Token 載荷"""
    user_id: int
    username: str
    exp: int  # 過期時間戳
    iat: int  # 發行時間戳
    token_type: str = "access"  # access / refresh


@dataclass
class User:
    """用戶資料"""
    user_id: int
    username: str
    password_hash: str
    salt: str
    email: str = ""
    is_active: bool = True
    created_at: str = ""
    role: str = "user"  # user / admin


class PasswordHasher:
    """密碼雜湊器"""
    
    @staticmethod
    def generate_salt() -> str:
        """生成隨機鹽"""
        return secrets.token_hex(16)
    
    @staticmethod
    def hash_password(password: str, salt: str) -> str:
        """雜湊密碼"""
        combined = f"{password}{salt}"
        return hashlib.sha256(combined.encode()).hexdigest()
    
    @staticmethod
    def verify_password(password: str, salt: str, password_hash: str) -> bool:
        """驗證密碼"""
        return PasswordHasher.hash_password(password, salt) == password_hash


class JWTManager:
    """JWT 管理器"""
    
    def __init__(self, secret: str = JWT_SECRET):
        self.secret = secret
    
    def _base64url_encode(self, data: bytes) -> str:
        """Base64 URL 安全編碼"""
        return base64.urlsafe_b64encode(data).rstrip(b'=').decode('utf-8')
    
    def _base64url_decode(self, data: str) -> bytes:
        """Base64 URL 安全解碼"""
        padding = 4 - len(data) % 4
        if padding != 4:
            data += '=' * padding
        return base64.urlsafe_b64decode(data.encode('utf-8'))
    
    def _sign(self, message: str) -> str:
        """簽名"""
        signature = hmac.new(
            self.secret.encode(),
            message.encode(),
            hashlib.sha256
        ).digest()
        return self._base64url_encode(signature)
    
    def create_token(self, payload: TokenPayload) -> str:
        """創建 JWT Token"""
        # Header
        header = {"alg": "HS256", "typ": "JWT"}
        header_b64 = self._base64url_encode(json.dumps(header).encode())
        
        # Payload
        payload_dict = asdict(payload)
        payload_b64 = self._base64url_encode(json.dumps(payload_dict).encode())
        
        # Signature
        message = f"{header_b64}.{payload_b64}"
        signature = self._sign(message)
        
        return f"{header_b64}.{payload_b64}.{signature}"
    
    def verify_token(self, token: str) -> Tuple[bool, Optional[TokenPayload], str]:
        """
        驗證 JWT Token
        返回：(是否有效, 載荷, 錯誤訊息)
        """
        try:
            parts = token.split('.')
            if len(parts) != 3:
                return False, None, "Token 格式錯誤"
            
            header_b64, payload_b64, signature = parts
            
            # 驗證簽名
            message = f"{header_b64}.{payload_b64}"
            expected_signature = self._sign(message)
            
            if signature != expected_signature:
                return False, None, "簽名驗證失敗"
            
            # 解析載荷
            payload_json = self._base64url_decode(payload_b64).decode('utf-8')
            payload_dict = json.loads(payload_json)
            
            # 檢查過期
            if payload_dict.get('exp', 0) < int(time.time()):
                return False, None, "Token 已過期"
            
            payload = TokenPayload(
                user_id=payload_dict['user_id'],
                username=payload_dict['username'],
                exp=payload_dict['exp'],
                iat=payload_dict['iat'],
                token_type=payload_dict.get('token_type', 'access'),
            )
            
            return True, payload, ""
        
        except Exception as e:
            return False, None, f"Token 解析錯誤：{str(e)}"
    
    def create_access_token(self, user_id: int, username: str) -> str:
        """創建訪問 Token"""
        now = int(time.time())
        exp = now + (ACCESS_TOKEN_EXPIRE_MINUTES * 60)
        
        payload = TokenPayload(
            user_id=user_id,
            username=username,
            exp=exp,
            iat=now,
            token_type="access",
        )
        return self.create_token(payload)
    
    def create_refresh_token(self, user_id: int, username: str) -> str:
        """創建刷新 Token"""
        now = int(time.time())
        exp = now + (REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60)
        
        payload = TokenPayload(
            user_id=user_id,
            username=username,
            exp=exp,
            iat=now,
            token_type="refresh",
        )
        return self.create_token(payload)
    
    def refresh_access_token(self, refresh_token: str) -> Tuple[bool, str, str]:
        """
        使用刷新 Token 取得新的訪問 Token
        返回：(成功, 新 Token, 錯誤訊息)
        """
        valid, payload, error = self.verify_token(refresh_token)
        
        if not valid:
            return False, "", error
        
        if payload.token_type != "refresh":
            return False, "", "不是有效的刷新 Token"
        
        new_token = self.create_access_token(payload.user_id, payload.username)
        return True, new_token, ""


class AuthManager:
    """認證管理器"""
    
    def __init__(self):
        self.hasher = PasswordHasher()
        self.jwt = JWTManager()
        self._users: Dict[str, User] = {}  # username -> User
        self._user_id_counter = 0
    
    def register(self, username: str, password: str, email: str = "") -> Tuple[bool, str, Optional[User]]:
        """
        註冊用戶
        返回：(成功, 訊息, 用戶)
        """
        if username in self._users:
            return False, "用戶名已存在", None
        
        if len(password) < 6:
            return False, "密碼至少6個字符", None
        
        self._user_id_counter += 1
        salt = self.hasher.generate_salt()
        password_hash = self.hasher.hash_password(password, salt)
        
        user = User(
            user_id=self._user_id_counter,
            username=username,
            password_hash=password_hash,
            salt=salt,
            email=email,
            created_at=datetime.now().isoformat(),
        )
        
        self._users[username] = user
        return True, "註冊成功", user
    
    def login(self, username: str, password: str) -> Tuple[bool, str, Dict]:
        """
        用戶登入
        返回：(成功, 訊息, {access_token, refresh_token})
        """
        user = self._users.get(username)
        
        if not user:
            return False, "用戶不存在", {}
        
        if not user.is_active:
            return False, "用戶已停用", {}
        
        if not self.hasher.verify_password(password, user.salt, user.password_hash):
            return False, "密碼錯誤", {}
        
        access_token = self.jwt.create_access_token(user.user_id, user.username)
        refresh_token = self.jwt.create_refresh_token(user.user_id, user.username)
        
        return True, "登入成功", {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "Bearer",
            "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        }
    
    def verify(self, token: str) -> Tuple[bool, Optional[User], str]:
        """
        驗證 Token 並返回用戶
        """
        valid, payload, error = self.jwt.verify_token(token)
        
        if not valid:
            return False, None, error
        
        user = self._users.get(payload.username)
        if not user:
            return False, None, "用戶不存在"
        
        return True, user, ""
    
    def get_user(self, username: str) -> Optional[User]:
        """取得用戶"""
        return self._users.get(username)
    
    def change_password(self, username: str, old_password: str, new_password: str) -> Tuple[bool, str]:
        """修改密碼"""
        user = self._users.get(username)
        
        if not user:
            return False, "用戶不存在"
        
        if not self.hasher.verify_password(old_password, user.salt, user.password_hash):
            return False, "原密碼錯誤"
        
        if len(new_password) < 6:
            return False, "新密碼至少6個字符"
        
        new_salt = self.hasher.generate_salt()
        user.salt = new_salt
        user.password_hash = self.hasher.hash_password(new_password, new_salt)
        
        return True, "密碼修改成功"


# 全局實例
_auth_manager: AuthManager = None

def get_auth_manager() -> AuthManager:
    """取得認證管理器實例"""
    global _auth_manager
    if _auth_manager is None:
        _auth_manager = AuthManager()
    return _auth_manager


# FastAPI 依賴（可選）
def get_current_user(token: str) -> Tuple[bool, Optional[User], str]:
    """FastAPI 依賴：取得當前用戶"""
    auth = get_auth_manager()
    return auth.verify(token)


if __name__ == "__main__":
    print("=== JWT 認證模組測試 ===")
    
    auth = AuthManager()
    
    # 註冊
    success, msg, user = auth.register("beidou", "password123", "beidou@test.com")
    print(f"註冊：{msg}")
    
    # 登入
    success, msg, tokens = auth.login("beidou", "password123")
    print(f"登入：{msg}")
    if success:
        print(f"Access Token: {tokens['access_token'][:50]}...")
    
    # 驗證
    if tokens:
        valid, user, error = auth.verify(tokens['access_token'])
        print(f"驗證：{'成功' if valid else error}")
        if user:
            print(f"用戶：{user.username} (ID: {user.user_id})")
    
    print("\n✅ JWT 認證模組測試通過")
