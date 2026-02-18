#!/usr/bin/env python3
"""
payment_service.py - 北斗命數支付服務
版本：v1.0.0

═══════════════════════════════════════════════════════════════════════
支援金流：
  • 綠界 ECPay
  • 藍新 NewebPay

PYLIB First：基於 cardeal_crm/ecpay_service.py (161行) 改寫
═══════════════════════════════════════════════════════════════════════

XTF Task Chain
@11星協作：@織明(統籌) @流祇(連結) @星殼(架構)
"""

import hashlib
import urllib.parse
import base64
import json
import hmac
from typing import Dict, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad

# ════════════════════════════════════════════════════════════════════
# L0: 配置
# ════════════════════════════════════════════════════════════════════

class PaymentProvider(Enum):
    ECPAY = "ecpay"
    NEWEBPAY = "newebpay"

@dataclass
class PaymentConfig:
    """支付配置"""
    provider: PaymentProvider
    merchant_id: str
    hash_key: str
    hash_iv: str
    is_sandbox: bool = True
    
    @property
    def api_url(self) -> str:
        if self.provider == PaymentProvider.ECPAY:
            return "https://payment-stage.ecpay.com.tw" if self.is_sandbox else "https://payment.ecpay.com.tw"
        else:  # NEWEBPAY
            return "https://ccore.newebpay.com" if self.is_sandbox else "https://core.newebpay.com"

# 預設配置（生產環境應從環境變數讀取）
ECPAY_CONFIG = PaymentConfig(
    provider=PaymentProvider.ECPAY,
    merchant_id="3002607",  # 測試商店
    hash_key="pwFHCqoQZGmho4w6",
    hash_iv="EkRm7iFT261dpevs",
    is_sandbox=True
)

NEWEBPAY_CONFIG = PaymentConfig(
    provider=PaymentProvider.NEWEBPAY,
    merchant_id="MS12345678",  # 測試商店
    hash_key="12345678901234567890123456789012",
    hash_iv="1234567890123456",
    is_sandbox=True
)

# 報告方案
REPORT_PLANS = {
    "L1": {"name": "入門版報告", "price": 2800, "credits": 50},
    "L2": {"name": "進階版報告", "price": 8800, "credits": 150},
    "L3": {"name": "顧問版報告", "price": 28000, "credits": 500},
    "L4_monthly": {"name": "長期顧問（月）", "price": 10000, "credits": 200, "days": 30},
    "L4_yearly": {"name": "長期顧問（年）", "price": 100000, "credits": 2500, "days": 365},
}

# 點數方案
CREDIT_PLANS = {
    "credit_100": {"name": "100 點數", "price": 100, "credits": 100},
    "credit_500": {"name": "500 點數", "price": 450, "credits": 500},
    "credit_1000": {"name": "1000 點數", "price": 800, "credits": 1000},
}

# ════════════════════════════════════════════════════════════════════
# L1: 綠界 ECPay
# ════════════════════════════════════════════════════════════════════

class ECPayService:
    """綠界金流服務"""
    
    def __init__(self, config: PaymentConfig = ECPAY_CONFIG):
        self.config = config
    
    def _check_mac_value(self, params: dict) -> str:
        """計算 ECPay CheckMacValue"""
        # 排除 CheckMacValue 本身
        filtered = {k: v for k, v in params.items() if k != 'CheckMacValue'}
        
        # 按照字母排序
        sorted_params = sorted(filtered.items(), key=lambda x: x[0])
        
        # 組合字串
        param_str = '&'.join([f'{k}={v}' for k, v in sorted_params])
        
        # 加上 HashKey 和 HashIV
        raw = f"HashKey={self.config.hash_key}&{param_str}&HashIV={self.config.hash_iv}"
        
        # URL encode
        encoded = urllib.parse.quote_plus(raw).lower()
        
        # SHA256
        return hashlib.sha256(encoded.encode('utf-8')).hexdigest().upper()
    
    def create_order(self, user_id: int, plan_code: str, 
                     return_url: str, notify_url: str) -> dict:
        """建立付款訂單"""
        # 取得方案
        plan = REPORT_PLANS.get(plan_code) or CREDIT_PLANS.get(plan_code)
        if not plan:
            return {'success': False, 'error': '無效的方案'}
        
        # 產生訂單編號
        merchant_trade_no = f"BD{datetime.now().strftime('%Y%m%d%H%M%S')}{user_id:06d}"
        trade_date = datetime.now().strftime('%Y/%m/%d %H:%M:%S')
        
        # 組合參數
        params = {
            'MerchantID': self.config.merchant_id,
            'MerchantTradeNo': merchant_trade_no,
            'MerchantTradeDate': trade_date,
            'PaymentType': 'aio',
            'TotalAmount': plan['price'],
            'TradeDesc': urllib.parse.quote('北斗命數系統'),
            'ItemName': plan['name'],
            'ReturnURL': notify_url,
            'OrderResultURL': return_url,
            'ChoosePayment': 'ALL',
            'EncryptType': 1,
        }
        
        params['CheckMacValue'] = self._check_mac_value(params)
        
        return {
            'success': True,
            'provider': 'ecpay',
            'action_url': f'{self.config.api_url}/Cashier/AioCheckOut/V5',
            'params': params,
            'merchant_trade_no': merchant_trade_no,
            'plan': plan
        }
    
    def verify_notify(self, post_data: dict) -> Tuple[bool, str, dict]:
        """驗證回調通知
        
        Returns:
            (是否有效, 訂單編號, 詳細資訊)
        """
        # 驗證 CheckMacValue
        received_mac = post_data.get('CheckMacValue', '')
        calculated_mac = self._check_mac_value(post_data)
        
        if received_mac != calculated_mac:
            return False, '', {'error': 'CheckMacValue 驗證失敗'}
        
        merchant_trade_no = post_data.get('MerchantTradeNo', '')
        rtn_code = post_data.get('RtnCode', '')
        trade_no = post_data.get('TradeNo', '')
        
        is_paid = rtn_code == '1'
        
        return is_paid, merchant_trade_no, {
            'trade_no': trade_no,
            'rtn_code': rtn_code,
            'rtn_msg': post_data.get('RtnMsg', ''),
            'payment_type': post_data.get('PaymentType', ''),
            'trade_amt': post_data.get('TradeAmt', ''),
        }


# ════════════════════════════════════════════════════════════════════
# L2: 藍新 NewebPay
# ════════════════════════════════════════════════════════════════════

class NewebPayService:
    """藍新金流服務"""
    
    def __init__(self, config: PaymentConfig = NEWEBPAY_CONFIG):
        self.config = config
    
    def _aes_encrypt(self, data: str) -> str:
        """AES 加密"""
        key = self.config.hash_key.encode('utf-8')
        iv = self.config.hash_iv.encode('utf-8')
        
        cipher = AES.new(key, AES.MODE_CBC, iv)
        padded = pad(data.encode('utf-8'), AES.block_size)
        encrypted = cipher.encrypt(padded)
        
        return encrypted.hex()
    
    def _aes_decrypt(self, encrypted_hex: str) -> str:
        """AES 解密"""
        key = self.config.hash_key.encode('utf-8')
        iv = self.config.hash_iv.encode('utf-8')
        
        cipher = AES.new(key, AES.MODE_CBC, iv)
        decrypted = cipher.decrypt(bytes.fromhex(encrypted_hex))
        
        return unpad(decrypted, AES.block_size).decode('utf-8')
    
    def _sha256_hash(self, data: str) -> str:
        """SHA256 雜湊"""
        raw = f"HashKey={self.config.hash_key}&{data}&HashIV={self.config.hash_iv}"
        return hashlib.sha256(raw.encode('utf-8')).hexdigest().upper()
    
    def create_order(self, user_id: int, plan_code: str,
                     return_url: str, notify_url: str) -> dict:
        """建立付款訂單"""
        plan = REPORT_PLANS.get(plan_code) or CREDIT_PLANS.get(plan_code)
        if not plan:
            return {'success': False, 'error': '無效的方案'}
        
        # 產生訂單編號
        merchant_order_no = f"BD{datetime.now().strftime('%Y%m%d%H%M%S')}{user_id:06d}"
        
        # 交易資料
        trade_info = {
            'MerchantID': self.config.merchant_id,
            'MerchantOrderNo': merchant_order_no,
            'Amt': plan['price'],
            'ItemDesc': plan['name'],
            'Email': '',  # 可選
            'ReturnURL': notify_url,
            'NotifyURL': notify_url,
            'CustomerURL': return_url,
            'TimeStamp': str(int(datetime.now().timestamp())),
            'Version': '2.0',
        }
        
        # 轉換為 query string
        trade_info_str = urllib.parse.urlencode(trade_info)
        
        # AES 加密
        trade_info_encrypted = self._aes_encrypt(trade_info_str)
        
        # SHA256 雜湊
        trade_sha = self._sha256_hash(trade_info_encrypted)
        
        return {
            'success': True,
            'provider': 'newebpay',
            'action_url': f'{self.config.api_url}/MPG/mpg_gateway',
            'params': {
                'MerchantID': self.config.merchant_id,
                'TradeInfo': trade_info_encrypted,
                'TradeSha': trade_sha,
                'Version': '2.0',
            },
            'merchant_order_no': merchant_order_no,
            'plan': plan
        }
    
    def verify_notify(self, post_data: dict) -> Tuple[bool, str, dict]:
        """驗證回調通知"""
        trade_info_encrypted = post_data.get('TradeInfo', '')
        trade_sha = post_data.get('TradeSha', '')
        
        # 驗證 SHA256
        calculated_sha = self._sha256_hash(trade_info_encrypted)
        if trade_sha != calculated_sha:
            return False, '', {'error': 'TradeSha 驗證失敗'}
        
        # 解密
        try:
            trade_info_str = self._aes_decrypt(trade_info_encrypted)
            trade_info = dict(urllib.parse.parse_qsl(trade_info_str))
        except Exception as e:
            return False, '', {'error': f'解密失敗: {e}'}
        
        merchant_order_no = trade_info.get('MerchantOrderNo', '')
        status = trade_info.get('Status', '')
        
        is_paid = status == 'SUCCESS'
        
        return is_paid, merchant_order_no, {
            'status': status,
            'message': trade_info.get('Message', ''),
            'trade_no': trade_info.get('TradeNo', ''),
            'amt': trade_info.get('Amt', ''),
            'payment_type': trade_info.get('PaymentType', ''),
        }


# ════════════════════════════════════════════════════════════════════
# L3: 統一支付介面
# ════════════════════════════════════════════════════════════════════

class PaymentService:
    """統一支付服務"""
    
    def __init__(self, provider: PaymentProvider = PaymentProvider.ECPAY):
        if provider == PaymentProvider.ECPAY:
            self.service = ECPayService()
        else:
            self.service = NewebPayService()
        
        self.provider = provider
    
    def create_order(self, user_id: int, plan_code: str,
                     return_url: str, notify_url: str) -> dict:
        """建立付款訂單"""
        return self.service.create_order(user_id, plan_code, return_url, notify_url)
    
    def verify_notify(self, post_data: dict) -> Tuple[bool, str, dict]:
        """驗證回調通知"""
        return self.service.verify_notify(post_data)
    
    @staticmethod
    def get_plans() -> dict:
        """取得所有方案"""
        return {
            'reports': REPORT_PLANS,
            'credits': CREDIT_PLANS,
        }


# ════════════════════════════════════════════════════════════════════
# L4: FastAPI 端點
# ════════════════════════════════════════════════════════════════════

from fastapi import FastAPI, HTTPException, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from pydantic import BaseModel

app = FastAPI(title="北斗命數支付 API", version="1.0.0")

class CreateOrderRequest(BaseModel):
    user_id: int
    plan_code: str
    provider: str = "ecpay"  # ecpay / newebpay

@app.get("/api/payment/plans")
async def get_plans():
    """取得方案列表"""
    return PaymentService.get_plans()

@app.post("/api/payment/create")
async def create_payment(req: CreateOrderRequest, request: Request):
    """建立付款"""
    provider = PaymentProvider.ECPAY if req.provider == "ecpay" else PaymentProvider.NEWEBPAY
    service = PaymentService(provider)
    
    base_url = str(request.base_url).rstrip('/')
    return_url = f"{base_url}/api/payment/return"
    notify_url = f"{base_url}/api/payment/notify"
    
    result = service.create_order(req.user_id, req.plan_code, return_url, notify_url)
    
    if not result.get('success'):
        raise HTTPException(400, result.get('error', '建立訂單失敗'))
    
    return result

@app.post("/api/payment/notify")
async def payment_notify(request: Request):
    """支付回調（綠界/藍新共用）"""
    form_data = await request.form()
    post_data = dict(form_data)
    
    # 判斷金流來源
    if 'CheckMacValue' in post_data:
        service = PaymentService(PaymentProvider.ECPAY)
    else:
        service = PaymentService(PaymentProvider.NEWEBPAY)
    
    is_paid, order_no, info = service.verify_notify(post_data)
    
    if is_paid:
        # TODO: 更新訂單狀態、發放點數
        print(f"✅ 付款成功：{order_no}")
        print(f"   詳細：{info}")
    else:
        print(f"❌ 付款失敗：{order_no}")
        print(f"   詳細：{info}")
    
    # 回應金流平台
    return "1|OK"

@app.get("/api/payment/return")
async def payment_return(request: Request):
    """付款完成返回頁"""
    return HTMLResponse("""
    <html>
    <head><title>付款完成</title></head>
    <body style="text-align:center; padding:50px;">
        <h1>感謝您的購買！</h1>
        <p>付款處理中，請稍候...</p>
        <script>setTimeout(() => window.location.href = '/', 3000);</script>
    </body>
    </html>
    """)

@app.get("/api/payment/status")
async def payment_status():
    """支付模組狀態"""
    return {
        "providers": ["ecpay", "newebpay"],
        "ecpay_sandbox": ECPAY_CONFIG.is_sandbox,
        "newebpay_sandbox": NEWEBPAY_CONFIG.is_sandbox,
        "plans_count": len(REPORT_PLANS) + len(CREDIT_PLANS),
    }


# ════════════════════════════════════════════════════════════════════
# 測試
# ════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("═" * 60)
    print("        北斗命數支付服務 - 測試")
    print("═" * 60)
    
    print("\n【方案列表】")
    plans = PaymentService.get_plans()
    print("  報告方案：")
    for code, plan in plans['reports'].items():
        print(f"    {code}: {plan['name']} NT${plan['price']}")
    print("  點數方案：")
    for code, plan in plans['credits'].items():
        print(f"    {code}: {plan['name']} NT${plan['price']}")
    
    print("\n【綠界 ECPay 測試】")
    ecpay = ECPayService()
    order = ecpay.create_order(
        user_id=1,
        plan_code="L1",
        return_url="https://example.com/return",
        notify_url="https://example.com/notify"
    )
    print(f"  訂單編號：{order['merchant_trade_no']}")
    print(f"  金額：NT${order['plan']['price']}")
    print(f"  CheckMacValue：{order['params']['CheckMacValue'][:20]}...")
    
    print("\n【藍新 NewebPay 測試】")
    try:
        newebpay = NewebPayService()
        order = newebpay.create_order(
            user_id=1,
            plan_code="L2",
            return_url="https://example.com/return",
            notify_url="https://example.com/notify"
        )
        print(f"  訂單編號：{order['merchant_order_no']}")
        print(f"  金額：NT${order['plan']['price']}")
        print(f"  TradeInfo：{order['params']['TradeInfo'][:30]}...")
    except Exception as e:
        print(f"  ⚠️ 需要安裝 pycryptodome：{e}")
    
    print("\n" + "═" * 60)
    print("✅ 支付服務測試完成")
    print("═" * 60)
    print("\n啟動：uvicorn payment_service:app --port 8003")
