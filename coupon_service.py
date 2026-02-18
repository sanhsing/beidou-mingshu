"""
優惠券服務
coupon_service.py | @星殼 | 2026-02-17
PYLIB: db_unified
"""
from fastapi import APIRouter, Request, HTTPException, Depends
from pydantic import BaseModel
from datetime import datetime, timedelta
from typing import Optional, List
import sqlite3
import secrets
import string

router = APIRouter(prefix="/api/coupon", tags=["coupon"])

DB_PATH = 'beidou_unified.db'

# === Pydantic Models ===
class CouponCreate(BaseModel):
    code: Optional[str] = None  # 不填則自動生成
    name: str
    discount_type: str  # 'percent' 或 'fixed'
    discount_value: float  # 百分比 (0-100) 或固定金額
    min_amount: float = 0  # 最低消費
    max_discount: Optional[float] = None  # 最高折抵 (百分比折扣用)
    usage_limit: int = 0  # 0 = 無限
    per_user_limit: int = 1  # 每人限用
    valid_from: Optional[str] = None
    valid_until: Optional[str] = None
    applicable_products: Optional[str] = None  # 適用商品 (逗號分隔)

class CouponVerify(BaseModel):
    code: str
    amount: float
    product_id: Optional[str] = None

# === 初始化表 ===
def init_coupon_tables():
    """初始化優惠券表"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS coupons (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            code TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            discount_type TEXT NOT NULL,
            discount_value REAL NOT NULL,
            min_amount REAL DEFAULT 0,
            max_discount REAL,
            usage_limit INTEGER DEFAULT 0,
            usage_count INTEGER DEFAULT 0,
            per_user_limit INTEGER DEFAULT 1,
            valid_from TEXT,
            valid_until TEXT,
            applicable_products TEXT,
            status TEXT DEFAULT 'active',
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS coupon_usage (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            coupon_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            order_no TEXT,
            discount_amount REAL,
            used_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (coupon_id) REFERENCES coupons(id)
        )
    ''')
    
    conn.commit()
    conn.close()

init_coupon_tables()

# === 輔助函數 ===
def generate_coupon_code(length: int = 8) -> str:
    """生成優惠券碼"""
    chars = string.ascii_uppercase + string.digits
    return ''.join(secrets.choice(chars) for _ in range(length))

def get_user_id(request: Request) -> int:
    """獲取用戶ID"""
    return 1  # TODO: JWT

# === API 端點 ===

@router.post("/create")
async def create_coupon(data: CouponCreate, request: Request):
    """
    P4.2: 建立優惠券 (管理員)
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        code = data.code or generate_coupon_code()
        
        # 檢查是否重複
        cursor.execute('SELECT id FROM coupons WHERE code = ?', (code,))
        if cursor.fetchone():
            raise HTTPException(status_code=400, detail="優惠券碼已存在")
        
        cursor.execute('''
            INSERT INTO coupons (
                code, name, discount_type, discount_value,
                min_amount, max_discount, usage_limit, per_user_limit,
                valid_from, valid_until, applicable_products
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            code, data.name, data.discount_type, data.discount_value,
            data.min_amount, data.max_discount, data.usage_limit, data.per_user_limit,
            data.valid_from, data.valid_until, data.applicable_products
        ))
        
        coupon_id = cursor.lastrowid
        conn.commit()
        
        return {
            "success": True,
            "coupon": {
                "id": coupon_id,
                "code": code,
                "name": data.name
            }
        }
        
    finally:
        conn.close()


@router.post("/verify")
async def verify_coupon(data: CouponVerify, request: Request):
    """
    P4.3: 驗證優惠券
    """
    user_id = get_user_id(request)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # 查詢優惠券
        cursor.execute('''
            SELECT id, name, discount_type, discount_value, min_amount, max_discount,
                   usage_limit, usage_count, per_user_limit, valid_from, valid_until,
                   applicable_products, status
            FROM coupons WHERE code = ?
        ''', (data.code.upper(),))
        
        row = cursor.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="優惠券不存在")
        
        coupon = {
            'id': row[0], 'name': row[1], 'discount_type': row[2],
            'discount_value': row[3], 'min_amount': row[4], 'max_discount': row[5],
            'usage_limit': row[6], 'usage_count': row[7], 'per_user_limit': row[8],
            'valid_from': row[9], 'valid_until': row[10],
            'applicable_products': row[11], 'status': row[12]
        }
        
        # 檢查狀態
        if coupon['status'] != 'active':
            raise HTTPException(status_code=400, detail="優惠券已停用")
        
        # 檢查有效期
        now = datetime.now().isoformat()
        if coupon['valid_from'] and now < coupon['valid_from']:
            raise HTTPException(status_code=400, detail="優惠券尚未生效")
        if coupon['valid_until'] and now > coupon['valid_until']:
            raise HTTPException(status_code=400, detail="優惠券已過期")
        
        # 檢查使用次數
        if coupon['usage_limit'] > 0 and coupon['usage_count'] >= coupon['usage_limit']:
            raise HTTPException(status_code=400, detail="優惠券已達使用上限")
        
        # 檢查用戶使用次數
        cursor.execute('''
            SELECT COUNT(*) FROM coupon_usage 
            WHERE coupon_id = ? AND user_id = ?
        ''', (coupon['id'], user_id))
        user_usage = cursor.fetchone()[0]
        
        if user_usage >= coupon['per_user_limit']:
            raise HTTPException(status_code=400, detail="您已達到此優惠券使用上限")
        
        # 檢查最低消費
        if data.amount < coupon['min_amount']:
            raise HTTPException(
                status_code=400, 
                detail=f"未達最低消費 NT${coupon['min_amount']}"
            )
        
        # 檢查適用商品
        if coupon['applicable_products'] and data.product_id:
            products = coupon['applicable_products'].split(',')
            if data.product_id not in products:
                raise HTTPException(status_code=400, detail="此優惠券不適用於此商品")
        
        # 計算折扣
        if coupon['discount_type'] == 'percent':
            discount = data.amount * coupon['discount_value'] / 100
            if coupon['max_discount']:
                discount = min(discount, coupon['max_discount'])
        else:  # fixed
            discount = min(coupon['discount_value'], data.amount)
        
        discount = round(discount, 0)
        
        return {
            "success": True,
            "valid": True,
            "coupon_id": coupon['id'],
            "coupon_name": coupon['name'],
            "original_amount": data.amount,
            "discount": discount,
            "final_amount": data.amount - discount
        }
        
    finally:
        conn.close()


@router.post("/use")
async def use_coupon(
    coupon_id: int,
    order_no: str,
    discount_amount: float,
    request: Request
):
    """
    使用優惠券 (結帳後調用)
    """
    user_id = get_user_id(request)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # 記錄使用
        cursor.execute('''
            INSERT INTO coupon_usage (coupon_id, user_id, order_no, discount_amount)
            VALUES (?, ?, ?, ?)
        ''', (coupon_id, user_id, order_no, discount_amount))
        
        # 更新使用次數
        cursor.execute('''
            UPDATE coupons SET usage_count = usage_count + 1 WHERE id = ?
        ''', (coupon_id,))
        
        conn.commit()
        
        return {"success": True}
        
    finally:
        conn.close()


@router.get("/list")
async def list_coupons(request: Request):
    """
    查詢可用優惠券
    """
    user_id = get_user_id(request)
    now = datetime.now().isoformat()
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            SELECT c.id, c.code, c.name, c.discount_type, c.discount_value,
                   c.min_amount, c.max_discount, c.valid_until,
                   (SELECT COUNT(*) FROM coupon_usage WHERE coupon_id = c.id AND user_id = ?) as user_usage,
                   c.per_user_limit
            FROM coupons c
            WHERE c.status = 'active'
              AND (c.valid_from IS NULL OR c.valid_from <= ?)
              AND (c.valid_until IS NULL OR c.valid_until >= ?)
              AND (c.usage_limit = 0 OR c.usage_count < c.usage_limit)
        ''', (user_id, now, now))
        
        coupons = []
        for row in cursor.fetchall():
            if row[8] < row[9]:  # user_usage < per_user_limit
                coupons.append({
                    'id': row[0],
                    'code': row[1],
                    'name': row[2],
                    'discount_type': row[3],
                    'discount_value': row[4],
                    'min_amount': row[5],
                    'max_discount': row[6],
                    'valid_until': row[7]
                })
        
        return {"success": True, "coupons": coupons}
        
    finally:
        conn.close()
