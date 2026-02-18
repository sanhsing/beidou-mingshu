#!/usr/bin/env python3
"""
test_api.py - 北斗命數 API 單元測試
版本：v1.0.0

═══════════════════════════════════════════════════════════════════════
XTF Task Chain: D5
@11星協作：@理樞(測試)
═══════════════════════════════════════════════════════════════════════
"""

import pytest
import sys
import os

# 添加父目錄到路徑
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi.testclient import TestClient

# ════════════════════════════════════════════════════════════════════
# 測試配置
# ════════════════════════════════════════════════════════════════════

@pytest.fixture
def client():
    """創建測試客戶端"""
    from app import app
    return TestClient(app)

@pytest.fixture
def auth_headers(client):
    """獲取認證 headers"""
    # 註冊測試用戶
    client.post("/api/auth/register", json={
        "username": "testuser",
        "password": "test123456",
        "email": "test@example.com"
    })
    
    # 登入獲取 token
    response = client.post("/api/auth/login", json={
        "username": "testuser",
        "password": "test123456"
    })
    
    if response.status_code == 200:
        token = response.json().get("access_token")
        return {"Authorization": f"Bearer {token}"}
    return {}

# ════════════════════════════════════════════════════════════════════
# 系統測試
# ════════════════════════════════════════════════════════════════════

class TestSystem:
    """系統端點測試"""
    
    def test_health_check(self, client):
        """健康檢查"""
        response = client.get("/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
    
    def test_status(self, client):
        """系統狀態"""
        response = client.get("/api/status")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert "version" in data
    
    def test_config_plans(self, client):
        """定價方案"""
        response = client.get("/api/config/plans")
        assert response.status_code == 200
        data = response.json()
        assert "report_plans" in data
        assert "credit_plans" in data

# ════════════════════════════════════════════════════════════════════
# 認證測試
# ════════════════════════════════════════════════════════════════════

class TestAuth:
    """認證端點測試"""
    
    def test_register(self, client):
        """用戶註冊"""
        response = client.post("/api/auth/register", json={
            "username": "newuser",
            "password": "password123",
            "email": "new@example.com"
        })
        # 可能成功或用戶已存在
        assert response.status_code in [200, 400]
    
    def test_login_success(self, client):
        """登入成功"""
        # 先註冊
        client.post("/api/auth/register", json={
            "username": "logintest",
            "password": "test123456",
            "email": "login@example.com"
        })
        
        # 登入
        response = client.post("/api/auth/login", json={
            "username": "logintest",
            "password": "test123456"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
    
    def test_login_fail(self, client):
        """登入失敗"""
        response = client.post("/api/auth/login", json={
            "username": "nonexistent",
            "password": "wrongpassword"
        })
        assert response.status_code == 401
    
    def test_me_unauthorized(self, client):
        """未授權訪問"""
        response = client.get("/api/auth/me")
        assert response.status_code in [401, 403]
    
    def test_me_authorized(self, client, auth_headers):
        """授權訪問"""
        response = client.get("/api/auth/me", headers=auth_headers)
        if auth_headers:
            assert response.status_code == 200

# ════════════════════════════════════════════════════════════════════
# 命理 API 測試
# ════════════════════════════════════════════════════════════════════

class TestMingshu:
    """命理端點測試"""
    
    def test_bazi_analyze(self, client):
        """八字分析"""
        response = client.post("/api/bazi/analyze", json={
            "year": 1990,
            "month": 6,
            "day": 15,
            "hour": 12,
            "gender": "男",
            "calendar": "solar"
        })
        assert response.status_code == 200
        data = response.json()
        assert "四柱" in data
        assert "日主" in data
    
    def test_ziwei_chart(self, client):
        """紫微排盤"""
        response = client.post("/api/ziwei/chart", json={
            "year": 1990,
            "month": 6,
            "day": 15,
            "hour": 12,
            "gender": "男",
            "calendar": "solar"
        })
        assert response.status_code == 200
    
    def test_meihua_divine(self, client):
        """梅花起卦"""
        response = client.post("/api/meihua/divine", json={
            "method": "time",
            "question": "測試問題"
        })
        assert response.status_code == 200
    
    def test_date_select(self, client):
        """擇日選擇"""
        response = client.post("/api/date/select", json={
            "date_type": "marry",
            "year": 2026,
            "month": 3
        })
        assert response.status_code == 200

# ════════════════════════════════════════════════════════════════════
# 支付 API 測試
# ════════════════════════════════════════════════════════════════════

class TestPayment:
    """支付端點測試"""
    
    def test_payment_plans(self, client):
        """支付方案"""
        response = client.get("/api/payment/plans")
        assert response.status_code == 200

# ════════════════════════════════════════════════════════════════════
# 運行測試
# ════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
