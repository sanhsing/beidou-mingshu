"""
電子發票服務
invoice_service.py | @星殼 | 2026-02-17
PYLIB: payment_service, db_unified
"""
from fastapi import APIRouter, Request, HTTPException
from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List
import sqlite3
import hashlib
import os

router = APIRouter(prefix="/api/invoice", tags=["invoice"])

DB_PATH = 'beidou_unified.db'

# === 配置 ===
EINVOICE_MERCHANT_ID = os.getenv('EINVOICE_MERCHANT_ID', '')
EINVOICE_HASH_KEY = os.getenv('EINVOICE_HASH_KEY', '')
EINVOICE_HASH_IV = os.getenv('EINVOICE_HASH_IV', '')
EINVOICE_SANDBOX = os.getenv('EINVOICE_SANDBOX', 'true').lower() == 'true'

# === Pydantic Models ===
class InvoiceRequest(BaseModel):
    order_no: str
    carrier_type: str = 'none'  # none, phone, natural, company
    carrier_num: Optional[str] = None  # 載具號碼
    company_id: Optional[str] = None  # 統編
    buyer_name: Optional[str] = None  # 買受人 (公司名)
    donate: bool = False  # 捐贈
    donate_code: Optional[str] = None  # 捐贈碼

# === 初始化表 ===
def init_invoice_tables():
    """初始化發票表"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS invoices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_no TEXT NOT NULL,
            user_id INTEGER NOT NULL,
            invoice_no TEXT,
            random_code TEXT,
            invoice_date TEXT,
            amount INTEGER NOT NULL,
            tax_amount INTEGER DEFAULT 0,
            carrier_type TEXT DEFAULT 'none',
            carrier_num TEXT,
            company_id TEXT,
            buyer_name TEXT,
            donate INTEGER DEFAULT 0,
            donate_code TEXT,
            status TEXT DEFAULT 'pending',
            einvoice_response TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()

init_invoice_tables()

# === 輔助函數 ===
def get_user_id(request: Request) -> int:
    """獲取用戶ID"""
    return 1  # TODO: JWT

def generate_invoice_no() -> tuple:
    """生成發票號碼 (模擬)"""
    import random
    # 實際應從財政部 API 取得字軌
    prefix = 'AB'  # 字軌
    number = f'{random.randint(10000000, 99999999)}'
    random_code = f'{random.randint(1000, 9999)}'
    return f'{prefix}{number}', random_code

# === EInvoice 服務類 ===
class EInvoiceService:
    """電子發票服務 (整合財政部電子發票平台)"""
    
    def __init__(self):
        self.merchant_id = EINVOICE_MERCHANT_ID
        self.sandbox = EINVOICE_SANDBOX
    
    def issue_invoice(self, data: dict) -> dict:
        """
        P4.6: 開立電子發票
        """
        if not self.merchant_id:
            # 未設定，使用模擬
            invoice_no, random_code = generate_invoice_no()
            return {
                'success': True,
                'invoice_no': invoice_no,
                'random_code': random_code,
                'simulated': True
            }
        
        # TODO: 實際 API 整合
        # 這裡應該調用財政部或綠界電子發票 API
        
        invoice_no, random_code = generate_invoice_no()
        return {
            'success': True,
            'invoice_no': invoice_no,
            'random_code': random_code,
            'simulated': True
        }
    
    def void_invoice(self, invoice_no: str, reason: str) -> dict:
        """作廢發票"""
        # TODO: 實際 API 整合
        return {
            'success': True,
            'message': f'發票 {invoice_no} 已作廢'
        }
    
    def query_invoice(self, invoice_no: str) -> dict:
        """查詢發票"""
        # TODO: 實際 API 整合
        return {
            'success': True,
            'invoice_no': invoice_no,
            'status': 'issued'
        }

einvoice_service = EInvoiceService()

# === API 端點 ===

@router.post("/issue")
async def issue_invoice(data: InvoiceRequest, request: Request):
    """
    開立電子發票
    """
    user_id = get_user_id(request)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # 查詢訂單
        cursor.execute('''
            SELECT amount, status FROM orders WHERE order_no = ? AND user_id = ?
        ''', (data.order_no, user_id))
        
        order = cursor.fetchone()
        if not order:
            raise HTTPException(status_code=404, detail="訂單不存在")
        
        if order[1] != 'paid':
            raise HTTPException(status_code=400, detail="訂單尚未支付")
        
        # 檢查是否已開立
        cursor.execute('''
            SELECT invoice_no FROM invoices WHERE order_no = ? AND status != 'voided'
        ''', (data.order_no,))
        
        existing = cursor.fetchone()
        if existing:
            raise HTTPException(status_code=400, detail=f"已開立發票: {existing[0]}")
        
        amount = order[0]
        tax_amount = int(amount * 0.05)  # 5% 營業稅
        
        # 調用電子發票服務
        result = einvoice_service.issue_invoice({
            'amount': amount,
            'tax_amount': tax_amount,
            'carrier_type': data.carrier_type,
            'carrier_num': data.carrier_num,
            'company_id': data.company_id,
            'buyer_name': data.buyer_name,
            'donate': data.donate,
            'donate_code': data.donate_code
        })
        
        if not result.get('success'):
            raise HTTPException(status_code=500, detail="發票開立失敗")
        
        # 保存發票記錄
        cursor.execute('''
            INSERT INTO invoices (
                order_no, user_id, invoice_no, random_code, invoice_date,
                amount, tax_amount, carrier_type, carrier_num,
                company_id, buyer_name, donate, donate_code, status
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'issued')
        ''', (
            data.order_no, user_id, result['invoice_no'], result['random_code'],
            datetime.now().strftime('%Y-%m-%d'),
            amount, tax_amount, data.carrier_type, data.carrier_num,
            data.company_id, data.buyer_name, int(data.donate), data.donate_code
        ))
        
        conn.commit()
        
        return {
            "success": True,
            "invoice_no": result['invoice_no'],
            "random_code": result['random_code'],
            "amount": amount,
            "tax_amount": tax_amount
        }
        
    finally:
        conn.close()


@router.get("/list")
async def list_invoices(request: Request):
    """
    P4.7: 查詢發票列表
    """
    user_id = get_user_id(request)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            SELECT invoice_no, random_code, invoice_date, amount, 
                   carrier_type, company_id, status, order_no
            FROM invoices 
            WHERE user_id = ?
            ORDER BY created_at DESC
            LIMIT 50
        ''', (user_id,))
        
        invoices = []
        for row in cursor.fetchall():
            invoices.append({
                'invoice_no': row[0],
                'random_code': row[1],
                'invoice_date': row[2],
                'amount': row[3],
                'carrier_type': row[4],
                'company_id': row[5],
                'status': row[6],
                'order_no': row[7]
            })
        
        return {"success": True, "invoices": invoices}
        
    finally:
        conn.close()


@router.get("/{invoice_no}")
async def get_invoice(invoice_no: str, request: Request):
    """
    查詢發票詳情
    """
    user_id = get_user_id(request)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            SELECT * FROM invoices WHERE invoice_no = ? AND user_id = ?
        ''', (invoice_no, user_id))
        
        row = cursor.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="發票不存在")
        
        columns = [desc[0] for desc in cursor.description]
        invoice = dict(zip(columns, row))
        
        return {"success": True, "invoice": invoice}
        
    finally:
        conn.close()


@router.post("/{invoice_no}/void")
async def void_invoice(invoice_no: str, reason: str, request: Request):
    """
    作廢發票 (管理員)
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # 調用作廢 API
        result = einvoice_service.void_invoice(invoice_no, reason)
        
        if result.get('success'):
            cursor.execute('''
                UPDATE invoices SET status = 'voided', updated_at = ?
                WHERE invoice_no = ?
            ''', (datetime.now().isoformat(), invoice_no))
            conn.commit()
        
        return result
        
    finally:
        conn.close()
